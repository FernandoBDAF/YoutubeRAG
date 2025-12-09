"""
Pipeline Execution Management Module

Reference: API_DESIGN_SPECIFICATION.md Section 3.6, 3.7, 7.1, 7.2

Provides:
- Background pipeline execution
- Thread-safe state management
- Progress tracking
- Pipeline cancellation
- MongoDB persistence for state recovery
"""

import argparse
import logging
import os
import threading
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Thread-safe pipeline state storage (in-memory cache)
_active_pipelines: Dict[str, Dict[str, Any]] = {}
_pipeline_lock = threading.Lock()

# Flag to track if recovery has been attempted
_recovery_done = False


# ============================================
# Database Persistence Helpers
# ============================================


def _sync_to_db(pipeline_id: str, state: Dict[str, Any]) -> None:
    """
    Sync pipeline state to database for persistence.
    
    Fails silently to allow graceful degradation when DB is unavailable.
    """
    try:
        from .repository import get_repository
        repo = get_repository()
        if repo is None:
            logger.warning(f"[{pipeline_id}] No repository available for DB sync")
            return
        
        # Make a copy to avoid modifying original state
        db_state = state.copy()
        
        # Convert datetime objects to ISO strings for MongoDB
        if isinstance(db_state.get("started_timestamp"), float):
            # Keep as-is for DB
            pass
        
        if repo.exists(pipeline_id):
            repo.update(pipeline_id, db_state)
            logger.debug(f"[{pipeline_id}] Updated in DB (status: {state.get('status')})")
        else:
            repo.create(db_state)
            logger.debug(f"[{pipeline_id}] Created in DB (status: {state.get('status')})")
            
    except Exception as e:
        logger.warning(f"Failed to sync pipeline {pipeline_id} to DB: {e}")


def _load_from_db(pipeline_id: str) -> Optional[Dict[str, Any]]:
    """Load pipeline state from database."""
    try:
        from .repository import get_repository
        repo = get_repository()
        if repo is None:
            logger.debug(f"[{pipeline_id}] No repository for DB load")
            return None
        result = repo.get(pipeline_id)
        if result:
            logger.debug(f"[{pipeline_id}] Loaded from DB (status: {result.get('status')})")
        else:
            logger.debug(f"[{pipeline_id}] Not found in DB")
        return result
    except Exception as e:
        logger.warning(f"Failed to load pipeline {pipeline_id} from DB: {e}")
        return None


def recover_state_from_db() -> None:
    """
    Recover pipeline state from database on startup.
    
    Any pipelines that were "running" when the server died are marked as "interrupted".
    """
    global _recovery_done
    
    if _recovery_done:
        return
    
    _recovery_done = True
    
    try:
        from .repository import get_repository
        repo = get_repository()
        if repo is None:
            logger.info("Pipeline persistence not available - skipping recovery")
            return
        
        # Find pipelines that were running when server stopped
        active = repo.list_active()
        interrupted_count = 0
        
        for pipeline in active:
            if pipeline.get("status") == "running":
                repo.update_status(
                    pipeline["pipeline_id"],
                    "interrupted",
                    error="Server restarted during execution"
                )
                interrupted_count += 1
                logger.warning(
                    f"Pipeline {pipeline['pipeline_id']} marked as interrupted (was running)"
                )
        
        if interrupted_count > 0:
            logger.info(f"Recovered {interrupted_count} interrupted pipelines from database")
        else:
            logger.info("No running pipelines found during recovery")
            
    except Exception as e:
        logger.warning(f"Failed to recover state from DB: {e}")


# ============================================
# Public API Functions
# ============================================


def execute_pipeline(
    pipeline: str,
    stages: List[str],
    config: Dict[str, Dict[str, Any]],
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Execute a pipeline in the background.

    Reference: API_DESIGN_SPECIFICATION.md Section 3.6

    Args:
        pipeline: Pipeline type ("ingestion" or "graphrag")
        stages: List of stage names to execute
        config: Stage configurations
        metadata: Optional metadata (experiment_id, description, etc.)

    Returns:
        Pipeline execution info with pipeline_id and tracking URL
    """
    # Ensure recovery has been done
    recover_state_from_db()
    
    # Generate unique pipeline ID
    pipeline_id = f"pipeline_{int(time.time())}_{uuid.uuid4().hex[:8]}"

    # Validate configuration first
    from .validation import validate_pipeline_config

    validation = validate_pipeline_config(pipeline, stages, config)

    if not validation["valid"]:
        return {"error": "Invalid configuration", "details": validation, "pipeline_id": None}

    # Use execution plan from validation (includes dependencies)
    execution_stages = validation["execution_plan"]["stages"]

    # Initialize pipeline state
    state = {
        "pipeline_id": pipeline_id,
        "pipeline": pipeline,
        "status": "starting",
        "started_at": datetime.utcnow().isoformat() + "Z",
        "started_timestamp": time.time(),
        "stages": execution_stages,
        "config": config,
        "metadata": metadata or {},
        "current_stage": None,
        "current_stage_index": 0,
        "completed_stages": [],
        "failed_stages": [],
        "progress": {
            "total_stages": len(execution_stages),
            "completed_stages": 0,
            "percent": 0.0,
        },
        "error": None,
        "error_stage": None,
        "exit_code": None,
    }
    
    with _pipeline_lock:
        _active_pipelines[pipeline_id] = state
    
    # Persist to database
    _sync_to_db(pipeline_id, state)

    # Start execution in background thread
    thread = threading.Thread(
        target=_run_pipeline_background,
        args=(pipeline_id, pipeline, execution_stages, config, metadata),
        daemon=True,
        name=f"Pipeline-{pipeline_id}",
    )
    thread.start()

    return {
        "pipeline_id": pipeline_id,
        "status": "starting",
        "started_at": state["started_at"],
        "stages": execution_stages,
        "tracking_url": f"/api/v1/pipelines/{pipeline_id}/status",
    }


def get_pipeline_status(pipeline_id: str) -> Dict[str, Any]:
    """
    Get current status of a pipeline.

    Reference: API_DESIGN_SPECIFICATION.md Section 3.7

    Returns pipeline state including:
    - Overall status
    - Current stage
    - Progress percentage
    - Timing information
    """
    # Ensure recovery has been done
    recover_state_from_db()
    
    state = None
    
    # First check in-memory cache
    with _pipeline_lock:
        all_ids = list(_active_pipelines.keys())
        logger.debug(f"[{pipeline_id}] Checking memory. Active pipelines: {all_ids}")
        
        if pipeline_id in _active_pipelines:
            state = _active_pipelines[pipeline_id].copy()
            logger.debug(f"[{pipeline_id}] Found in memory (status: {state.get('status')})")
        else:
            logger.debug(f"[{pipeline_id}] NOT in memory cache")
    
    # If not in memory, check database
    if state is None:
        logger.info(f"[{pipeline_id}] Not in memory, checking DB...")
        state = _load_from_db(pipeline_id)
        if state is None:
            logger.warning(f"[{pipeline_id}] Not found in memory or DB - returning 404")
            return {"error": "Pipeline not found", "pipeline_id": pipeline_id}
        else:
            logger.info(f"[{pipeline_id}] Found in DB (status: {state.get('status')})")

    # Calculate elapsed time
    if "started_timestamp" in state:
        if state["status"] in ["completed", "failed", "error", "cancelled", "interrupted"]:
            elapsed = state.get("duration_seconds", 0)
        else:
            elapsed = time.time() - state["started_timestamp"]
        state["elapsed_seconds"] = int(elapsed)

    # Remove internal fields
    state.pop("started_timestamp", None)
    state.pop("completed_timestamp", None)
    state.pop("_id", None)  # MongoDB ObjectId
    state.pop("created_at", None)
    state.pop("updated_at", None)

    return state


def cancel_pipeline(pipeline_id: str) -> Dict[str, Any]:
    """
    Cancel a running pipeline.

    Note: This marks the pipeline as cancelled. The running thread
    should check this status and stop gracefully.
    """
    with _pipeline_lock:
        if pipeline_id not in _active_pipelines:
            # Check database
            state = _load_from_db(pipeline_id)
            if state is None:
                return {"error": "Pipeline not found", "pipeline_id": pipeline_id}
            
            if state["status"] not in ["starting", "running"]:
                return {
                    "error": "Pipeline is not running",
                    "pipeline_id": pipeline_id,
                    "current_status": state["status"],
                }
            
            # Pipeline was in DB but not in memory - unusual state
            return {
                "error": "Pipeline found in history but not actively running",
                "pipeline_id": pipeline_id,
                "current_status": state["status"],
            }

        state = _active_pipelines[pipeline_id]

        if state["status"] not in ["starting", "running"]:
            return {
                "error": "Pipeline is not running",
                "pipeline_id": pipeline_id,
                "current_status": state["status"],
            }

        # Mark as cancelled
        state["status"] = "cancelled"
        state["completed_at"] = datetime.utcnow().isoformat() + "Z"
        state["completed_timestamp"] = time.time()
        state["duration_seconds"] = (
            state["completed_timestamp"] - state["started_timestamp"]
        )

    # Persist to database
    _sync_to_db(pipeline_id, state)

    return {
        "pipeline_id": pipeline_id,
        "status": "cancelled",
        "message": "Pipeline cancellation requested",
    }


def list_active_pipelines() -> Dict[str, Any]:
    """List all active (running/starting) pipelines"""
    # Ensure recovery has been done
    recover_state_from_db()
    
    with _pipeline_lock:
        active = {
            pid: {
                "pipeline_id": state["pipeline_id"],
                "pipeline": state["pipeline"],
                "status": state["status"],
                "started_at": state["started_at"],
                "current_stage": state["current_stage"],
                "progress": state["progress"],
            }
            for pid, state in _active_pipelines.items()
            if state["status"] in ["starting", "running"]
        }

    return {"count": len(active), "pipelines": active}


def get_pipeline_history(limit: int = 10) -> Dict[str, Any]:
    """Get recent pipeline executions"""
    # Ensure recovery has been done
    recover_state_from_db()
    
    # Try to get from database first for complete history
    try:
        from .repository import get_repository
        repo = get_repository()
        if repo is not None:
            db_pipelines = repo.list_history(limit)
            total = repo.count_all()
            
            # Clean up for response - include useful details
            result = []
            for state in db_pipelines:
                result.append({
                    "pipeline_id": state.get("pipeline_id"),
                    "pipeline": state.get("pipeline"),
                    "status": state.get("status"),
                    "started_at": state.get("started_at"),
                    "completed_at": state.get("completed_at"),
                    "stages": state.get("stages", []),
                    "progress": state.get("progress", {}),
                    # Additional useful fields
                    "duration_seconds": state.get("duration_seconds"),
                    "exit_code": state.get("exit_code"),
                    "error": state.get("error"),
                    "error_stage": state.get("error_stage"),
                    "config": state.get("config", {}),
                    "metadata": state.get("metadata", {}),
                })
            
            return {"total": total, "returned": len(result), "pipelines": result}
    except Exception as e:
        logger.warning(f"Failed to get history from DB, falling back to memory: {e}")
    
    # Fallback to in-memory
    with _pipeline_lock:
        all_pipelines = list(_active_pipelines.values())

    # Sort by start time (most recent first)
    all_pipelines.sort(key=lambda x: x.get("started_timestamp", 0), reverse=True)

    # Limit results
    recent = all_pipelines[:limit]

    # Clean up for response - include useful details
    result = []
    for state in recent:
        result.append({
            "pipeline_id": state["pipeline_id"],
            "pipeline": state["pipeline"],
            "status": state["status"],
            "started_at": state["started_at"],
            "completed_at": state.get("completed_at"),
            "stages": state["stages"],
            "progress": state["progress"],
            # Additional useful fields
            "duration_seconds": state.get("duration_seconds"),
            "exit_code": state.get("exit_code"),
            "error": state.get("error"),
            "error_stage": state.get("error_stage"),
            "config": state.get("config", {}),
            "metadata": state.get("metadata", {}),
        })

    return {"total": len(all_pipelines), "returned": len(result), "pipelines": result}


# ============================================
# Background Execution
# ============================================


def _run_pipeline_background(
    pipeline_id: str,
    pipeline: str,
    stages: List[str],
    config: Dict[str, Dict[str, Any]],
    metadata: Optional[Dict[str, Any]],
):
    """
    Run pipeline in background thread.

    Reference: API_DESIGN_SPECIFICATION.md Section 7.2
    """
    try:
        # Update status to running
        _update_pipeline_status(pipeline_id, "running")

        # Create pipeline object
        pipeline_obj = _create_pipeline_object(pipeline, stages, config, metadata)

        if pipeline_obj is None:
            _update_pipeline_error(pipeline_id, "Failed to create pipeline object", None)
            return

        # Execute pipeline - run each SELECTED stage individually
        logger.info(f"[{pipeline_id}] Starting pipeline execution with stages: {stages}")
        
        completed_stages = []
        exit_code = 0
        
        for idx, stage_name in enumerate(stages):
            # Check if cancelled
            with _pipeline_lock:
                if pipeline_id in _active_pipelines:
                    if _active_pipelines[pipeline_id]["status"] == "cancelled":
                        logger.info(f"[{pipeline_id}] Pipeline cancelled, stopping execution")
                        return
            
            # Update current stage
            _update_pipeline_progress(
                pipeline_id,
                current_stage=stage_name,
                current_stage_index=idx,
            )
            
            logger.info(f"[{pipeline_id}] Running stage {idx+1}/{len(stages)}: {stage_name}")
            
            # Run the individual stage
            try:
                stage_exit_code = pipeline_obj.run_stage(stage_name)
                if stage_exit_code != 0:
                    logger.error(f"[{pipeline_id}] Stage {stage_name} failed with exit code {stage_exit_code}")
                    exit_code = stage_exit_code
                    _update_pipeline_error(pipeline_id, f"Stage {stage_name} failed", stage_name)
                    return
                
                completed_stages.append(stage_name)
                _update_pipeline_progress(
                    pipeline_id,
                    completed_stages=completed_stages,
                    percent=((idx + 1) / len(stages)) * 100,
                )
                logger.info(f"[{pipeline_id}] Stage {stage_name} completed successfully")
                
            except Exception as stage_error:
                logger.exception(f"[{pipeline_id}] Stage {stage_name} raised exception")
                _update_pipeline_error(pipeline_id, str(stage_error), stage_name)
                return

        # Update final status
        _update_pipeline_completion(pipeline_id, exit_code, stages)

        logger.info(f"[{pipeline_id}] Pipeline completed with exit code: {exit_code}")

    except Exception as e:
        logger.exception(f"[{pipeline_id}] Pipeline execution failed")
        _update_pipeline_error(pipeline_id, str(e), None)


def _create_pipeline_object(
    pipeline: str,
    stages: List[str],
    config: Dict[str, Dict[str, Any]],
    metadata: Optional[Dict[str, Any]],
):
    """Create pipeline object from configuration"""
    try:
        if pipeline == "graphrag":
            from business.pipelines.graphrag import GraphRAGPipeline
            from core.config.graphrag import GraphRAGPipelineConfig

            # Create args namespace
            args = argparse.Namespace()
            env = dict(os.environ)

            # Apply metadata
            if metadata and "experiment_id" in metadata:
                env["EXPERIMENT_ID"] = metadata["experiment_id"]

            # Apply stage configs to env/args
            _apply_config_to_args_env(config, args, env)

            # Get database name from env (support both DB_NAME and MONGODB_DB)
            db_name = os.getenv("DB_NAME") or os.getenv("MONGODB_DB") or "mongo_hack"
            
            # Create pipeline config
            pipeline_config = GraphRAGPipelineConfig.from_args_env(
                args, env, db_name
            )

            # Set selected stages
            pipeline_config.selected_stages = ",".join(stages)

            return GraphRAGPipeline(pipeline_config)

        elif pipeline == "ingestion":
            from business.pipelines.ingestion import (
                IngestionPipeline,
                IngestionPipelineConfig,
            )
            from business.stages.ingestion.ingest import IngestConfig
            from business.stages.ingestion.clean import CleanConfig
            from business.stages.ingestion.chunk import ChunkConfig
            from business.stages.ingestion.enrich import EnrichConfig
            from business.stages.ingestion.embed import EmbedConfig
            from business.stages.ingestion.redundancy import RedundancyConfig
            from business.stages.ingestion.trust import TrustConfig

            # Get database name from env (support both DB_NAME and MONGODB_DB)
            db_name = os.getenv("DB_NAME") or os.getenv("MONGODB_DB") or "mongo_hack"
            
            # Create args/env for each stage individually to avoid cross-contamination
            def create_stage_config(stage_name: str, config_cls):
                """Create config for a single stage from API config"""
                args = argparse.Namespace()
                env = dict(os.environ)
                
                # Apply only this stage's config
                stage_config_dict = config.get(stage_name, {})
                for key, value in stage_config_dict.items():
                    setattr(args, key, value)
                    # Also set in env with stage prefix
                    env_key = f"{stage_name.upper()}_{key.upper()}"
                    if value is not None:
                        env[env_key] = str(value)
                
                # Create config using the stage's from_args_env
                return config_cls.from_args_env(args, env, db_name)
            
            # Create individual stage configs
            ingest_config = create_stage_config("ingest", IngestConfig)
            clean_config = create_stage_config("clean", CleanConfig)
            chunk_config = create_stage_config("chunk", ChunkConfig)
            enrich_config = create_stage_config("enrich", EnrichConfig)
            embed_config = create_stage_config("embed", EmbedConfig)
            redundancy_config = create_stage_config("redundancy", RedundancyConfig)
            trust_config = create_stage_config("trust", TrustConfig)
            
            # Create pipeline config directly (bypass from_args_env overrides)
            pipeline_config = IngestionPipelineConfig(
                db_name=db_name,
                continue_on_error=True,
                verbose=False,
                dry_run=False,
                ingest_config=ingest_config,
                clean_config=clean_config,
                enrich_config=enrich_config,
                chunk_config=chunk_config,
                embed_config=embed_config,
                redundancy_config=redundancy_config,
                trust_config=trust_config,
            )
            
            logger.info(f"Ingestion pipeline configured with db: {db_name}, selected stages: {stages}")
            logger.info(f"Clean config: max={clean_config.max}, llm={clean_config.llm}, use_llm={clean_config.use_llm}")

            return IngestionPipeline(pipeline_config)

        else:
            logger.error(f"Unknown pipeline type: {pipeline}")
            return None

    except Exception as e:
        logger.exception(f"Failed to create pipeline object: {e}")
        return None


def _apply_config_to_args_env(
    config: Dict[str, Dict[str, Any]],
    args: argparse.Namespace,
    env: Dict[str, str],
):
    """Apply stage configuration to args and environment"""
    for stage_name, stage_config in config.items():
        for key, value in stage_config.items():
            # Set on args namespace
            setattr(args, key, value)

            # Also set in env for stages that read from env
            env_key = f"{stage_name.upper()}_{key.upper()}"
            if value is not None:
                env[env_key] = str(value)


# ============================================
# State Update Helpers (with DB persistence)
# ============================================


def _update_pipeline_status(pipeline_id: str, status: str) -> None:
    """Update pipeline status in memory and database"""
    with _pipeline_lock:
        if pipeline_id in _active_pipelines:
            _active_pipelines[pipeline_id]["status"] = status
            state = _active_pipelines[pipeline_id]
    
    # Persist to database
    _sync_to_db(pipeline_id, {"status": status})


def _update_pipeline_progress(
    pipeline_id: str,
    current_stage: Optional[str] = None,
    current_stage_index: Optional[int] = None,
    completed_stages: Optional[List[str]] = None,
    percent: Optional[float] = None,
) -> None:
    """Update pipeline progress in memory and database"""
    updates: Dict[str, Any] = {}
    
    with _pipeline_lock:
        if pipeline_id not in _active_pipelines:
            return
        
        state = _active_pipelines[pipeline_id]
        
        if current_stage is not None:
            state["current_stage"] = current_stage
            updates["current_stage"] = current_stage
        
        if current_stage_index is not None:
            state["current_stage_index"] = current_stage_index
            updates["current_stage_index"] = current_stage_index
            # Calculate percent based on stage index
            total = state["progress"]["total_stages"]
            if total > 0:
                state["progress"]["percent"] = (current_stage_index / total) * 100
                updates["progress"] = state["progress"]
        
        if completed_stages is not None:
            state["completed_stages"] = completed_stages
            state["progress"]["completed_stages"] = len(completed_stages)
            updates["completed_stages"] = completed_stages
            updates["progress"] = state["progress"]
        
        if percent is not None:
            state["progress"]["percent"] = percent
            updates["progress"] = state["progress"]
    
    # Persist to database
    if updates:
        _sync_to_db(pipeline_id, updates)


def _update_pipeline_completion(pipeline_id: str, exit_code: int, stages: List[str]) -> None:
    """Update pipeline on completion in memory and database"""
    with _pipeline_lock:
        if pipeline_id in _active_pipelines:
            state = _active_pipelines[pipeline_id]
            state["status"] = "completed" if exit_code == 0 else "failed"
            state["exit_code"] = exit_code
            state["completed_at"] = datetime.utcnow().isoformat() + "Z"
            state["completed_timestamp"] = time.time()
            state["duration_seconds"] = (
                state["completed_timestamp"] - state["started_timestamp"]
            )
            state["completed_stages"] = (
                stages if exit_code == 0 else state.get("completed_stages", [])
            )
            state["progress"]["completed_stages"] = (
                len(stages) if exit_code == 0 else state["progress"]["completed_stages"]
            )
            state["progress"]["percent"] = (
                100.0 if exit_code == 0 else state["progress"]["percent"]
            )
            
            # Persist to database
            _sync_to_db(pipeline_id, state)


def _update_pipeline_error(pipeline_id: str, error: str, stage: Optional[str]) -> None:
    """Update pipeline on error in memory and database"""
    with _pipeline_lock:
        if pipeline_id in _active_pipelines:
            state = _active_pipelines[pipeline_id]
            state["status"] = "error"
            state["error"] = error
            state["error_stage"] = stage
            state["completed_at"] = datetime.utcnow().isoformat() + "Z"
            state["completed_timestamp"] = time.time()
            state["duration_seconds"] = (
                state["completed_timestamp"] - state["started_timestamp"]
            )
            
            # Persist to database
            _sync_to_db(pipeline_id, state)


# ============================================
# Module Initialization
# ============================================

# Note: We don't call recover_state_from_db() at module load time
# because it may happen before MongoDB is available.
# Instead, we call it lazily on first API call.
