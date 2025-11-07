"""
Pipeline Control API

Achievement 5.1: Pipeline Control API

REST API endpoints for controlling GraphRAG pipeline execution (start, pause, resume, cancel, status).
"""

import json
import logging
import threading
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from core.libraries.error_handling.decorators import handle_errors
from dependencies.database.mongodb import get_mongo_client
from core.config.paths import DB_NAME
from core.config.graphrag import GraphRAGPipelineConfig
from business.pipelines.graphrag import GraphRAGPipeline

logger = logging.getLogger(__name__)

# In-memory pipeline state (for active pipelines)
_active_pipelines: Dict[str, Dict[str, Any]] = {}
_pipeline_lock = threading.Lock()


def get_pipeline_status(pipeline_id: str, db_name: str = DB_NAME) -> Optional[Dict[str, Any]]:
    """
    Get current status of a pipeline.
    
    Achievement 5.1: Pipeline Control API
    
    Args:
        pipeline_id: Pipeline ID
        db_name: Database name
        
    Returns:
        Pipeline status dictionary or None if not found
    """
    with _pipeline_lock:
        if pipeline_id in _active_pipelines:
            return _active_pipelines[pipeline_id].copy()
    
    # Check MongoDB for completed/failed pipelines
    client = get_mongo_client()
    db = client[db_name]
    tracking_coll = db.experiment_tracking
    
    pipeline_doc = tracking_coll.find_one({"experiment_id": pipeline_id})
    if pipeline_doc:
        return {
            "pipeline_id": pipeline_id,
            "status": pipeline_doc.get("status", "unknown"),
            "started_at": pipeline_doc.get("started_at"),
            "completed_at": pipeline_doc.get("completed_at"),
            "configuration": pipeline_doc.get("configuration", {}),
        }
    
    return None


def start_pipeline(
    config_dict: Dict[str, Any],
    pipeline_id: Optional[str] = None,
    db_name: str = DB_NAME,
) -> Dict[str, Any]:
    """
    Start a new pipeline execution.
    
    Achievement 5.1: Pipeline Control API
    
    Args:
        config_dict: Pipeline configuration dictionary
        pipeline_id: Optional pipeline ID (generated if not provided)
        db_name: Database name
        
    Returns:
        Dictionary with pipeline_id and status
    """
    if pipeline_id is None:
        pipeline_id = config_dict.get("experiment_id") or f"pipeline_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    # Check if pipeline already exists
    existing = get_pipeline_status(pipeline_id, db_name)
    if existing and existing.get("status") == "running":
        return {
            "error": "Pipeline already running",
            "pipeline_id": pipeline_id,
            "status": "running",
        }
    
    # Create pipeline config from dictionary
    try:
        # Create stage configs from dict
        from core.config.graphrag import (
            GraphExtractionConfig,
            EntityResolutionConfig,
            GraphConstructionConfig,
            CommunityDetectionConfig,
        )
        from core.config.paths import DB_NAME as DEFAULT_DB
        
        # Extract stage configs
        extraction_dict = config_dict.get("extraction", {})
        resolution_dict = config_dict.get("resolution", {})
        construction_dict = config_dict.get("construction", {})
        detection_dict = config_dict.get("detection", {})
        
        # Create stage configs (simplified - use defaults if not provided)
        extraction_config = GraphExtractionConfig(
            db_name=extraction_dict.get("db_name", db_name),
            read_db_name=extraction_dict.get("read_db_name"),
            write_db_name=extraction_dict.get("write_db_name"),
            model_name=extraction_dict.get("model_name", "gpt-4o-mini"),
        )
        resolution_config = EntityResolutionConfig(
            db_name=resolution_dict.get("db_name", db_name),
            read_db_name=resolution_dict.get("read_db_name"),
            write_db_name=resolution_dict.get("write_db_name"),
        )
        construction_config = GraphConstructionConfig(
            db_name=construction_dict.get("db_name", db_name),
            read_db_name=construction_dict.get("read_db_name"),
            write_db_name=construction_dict.get("write_db_name"),
        )
        detection_config = CommunityDetectionConfig(
            db_name=detection_dict.get("db_name", db_name),
            read_db_name=detection_dict.get("read_db_name"),
            write_db_name=detection_dict.get("write_db_name"),
            algorithm=detection_dict.get("algorithm", "louvain"),
            resolution_parameter=detection_dict.get("resolution", 1.0),
        )
        
        # Create pipeline config
        config = GraphRAGPipelineConfig(
            experiment_id=pipeline_id,
            selected_stages=config_dict.get("selected_stages"),
            resume_from_failure=config_dict.get("resume_from_failure", False),
            extraction_config=extraction_config,
            resolution_config=resolution_config,
            construction_config=construction_config,
            detection_config=detection_config,
            continue_on_error=config_dict.get("continue_on_error", True),
        )
    except Exception as e:
        logger.error(f"Failed to create pipeline config: {e}", exc_info=True)
        return {
            "error": f"Invalid configuration: {str(e)}",
            "pipeline_id": pipeline_id,
        }
    
    # Initialize pipeline state
    with _pipeline_lock:
        _active_pipelines[pipeline_id] = {
            "pipeline_id": pipeline_id,
            "status": "starting",
            "started_at": datetime.utcnow().isoformat(),
            "config": config_dict,
            "thread": None,
            "pipeline": None,
        }
    
    # Start pipeline in background thread
    def run_pipeline():
        try:
            with _pipeline_lock:
                _active_pipelines[pipeline_id]["status"] = "running"
                pipeline = GraphRAGPipeline(config)
                _active_pipelines[pipeline_id]["pipeline"] = pipeline
            
            # Run pipeline
            exit_code = pipeline.run_full_pipeline()
            
            # Update status
            with _pipeline_lock:
                if pipeline_id in _active_pipelines:
                    _active_pipelines[pipeline_id]["status"] = "completed" if exit_code == 0 else "failed"
                    _active_pipelines[pipeline_id]["completed_at"] = datetime.utcnow().isoformat()
                    _active_pipelines[pipeline_id]["exit_code"] = exit_code
                    
                    # Store in MongoDB for history
                    tracking_db = pipeline.client[db_name]
                    tracking_coll = tracking_db.experiment_tracking
                    tracking_coll.update_one(
                        {"experiment_id": pipeline_id},
                        {
                            "$set": {
                                "status": "completed" if exit_code == 0 else "failed",
                                "completed_at": datetime.utcnow(),
                                "exit_code": exit_code,
                            }
                        },
                        upsert=True,
                    )
        except Exception as e:
            logger.error(f"Pipeline {pipeline_id} failed: {e}", exc_info=True)
            with _pipeline_lock:
                if pipeline_id in _active_pipelines:
                    _active_pipelines[pipeline_id]["status"] = "failed"
                    _active_pipelines[pipeline_id]["completed_at"] = datetime.utcnow().isoformat()
                    _active_pipelines[pipeline_id]["error"] = str(e)
    
    thread = threading.Thread(target=run_pipeline, daemon=True)
    thread.start()
    
    with _pipeline_lock:
        _active_pipelines[pipeline_id]["thread"] = thread
    
    return {
        "pipeline_id": pipeline_id,
        "status": "starting",
        "message": "Pipeline started",
    }


def cancel_pipeline(pipeline_id: str) -> Dict[str, Any]:
    """
    Cancel a running pipeline.
    
    Achievement 5.1: Pipeline Control API
    
    Args:
        pipeline_id: Pipeline ID
        
    Returns:
        Status dictionary
    """
    with _pipeline_lock:
        if pipeline_id not in _active_pipelines:
            return {
                "error": "Pipeline not found",
                "pipeline_id": pipeline_id,
            }
        
        pipeline_state = _active_pipelines[pipeline_id]
        if pipeline_state["status"] not in ["starting", "running"]:
            return {
                "error": f"Pipeline is not running (status: {pipeline_state['status']})",
                "pipeline_id": pipeline_id,
                "status": pipeline_state["status"],
            }
        
        # Mark as cancelled (actual cancellation would require thread interruption)
        pipeline_state["status"] = "cancelled"
        pipeline_state["completed_at"] = datetime.utcnow().isoformat()
        
        return {
            "pipeline_id": pipeline_id,
            "status": "cancelled",
            "message": "Pipeline cancellation requested",
        }


def get_pipeline_history(
    db_name: str = DB_NAME,
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    experiment_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get pipeline execution history.
    
    Achievement 5.3: Pipeline History UI
    
    Args:
        db_name: Database name
        limit: Maximum number of results
        offset: Pagination offset
        status: Filter by status
        experiment_id: Filter by experiment_id
        
    Returns:
        Dictionary with history and pagination info
    """
    client = get_mongo_client()
    db = client[db_name]
    tracking_coll = db.experiment_tracking
    
    # Build query
    query = {"pipeline_type": "graphrag"}
    if status:
        query["status"] = status
    if experiment_id:
        query["experiment_id"] = {"$regex": experiment_id, "$options": "i"}
    
    # Get total count
    total = tracking_coll.count_documents(query)
    
    # Get paginated results
    cursor = tracking_coll.find(query).sort("started_at", -1).skip(offset).limit(limit)
    
    pipelines = []
    for doc in cursor:
        pipelines.append({
            "pipeline_id": doc.get("experiment_id", "unknown"),
            "status": doc.get("status", "unknown"),
            "started_at": doc.get("started_at"),
            "completed_at": doc.get("completed_at"),
            "configuration": doc.get("configuration", {}),
            "exit_code": doc.get("exit_code"),
        })
    
    return {
        "pipelines": pipelines,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total,
    }


class PipelineControlHandler(BaseHTTPRequestHandler):
    """HTTP handler for pipeline control API endpoints."""
    
    @handle_errors(log_traceback=True, reraise=False)
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path_parts = parsed.path.strip("/").split("/")
        params = parse_qs(parsed.query)
        db_name = params.get("db_name", [DB_NAME])[0]
        
        try:
            if len(path_parts) >= 3 and path_parts[0] == "api" and path_parts[1] == "pipeline":
                if path_parts[2] == "status":
                    # GET /api/pipeline/status?pipeline_id=xxx
                    pipeline_id = params.get("pipeline_id", [None])[0]
                    if not pipeline_id:
                        self.send_response(400)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        error_response = json.dumps({"error": "pipeline_id parameter required"})
                        self.wfile.write(error_response.encode("utf-8"))
                        return
                    
                    status = get_pipeline_status(pipeline_id, db_name)
                    if status is None:
                        self.send_response(404)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        error_response = json.dumps({"error": "Pipeline not found"})
                        self.wfile.write(error_response.encode("utf-8"))
                    else:
                        response_json = json.dumps(status, indent=2, default=str)
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Access-Control-Allow-Origin", "*")
                        self.end_headers()
                        self.wfile.write(response_json.encode("utf-8"))
                        
                elif path_parts[2] == "history":
                    # GET /api/pipeline/history
                    limit = int(params.get("limit", [50])[0])
                    offset = int(params.get("offset", [0])[0])
                    status = params.get("status", [None])[0]
                    experiment_id = params.get("experiment_id", [None])[0]
                    
                    history = get_pipeline_history(
                        db_name=db_name,
                        limit=limit,
                        offset=offset,
                        status=status,
                        experiment_id=experiment_id,
                    )
                    
                    response_json = json.dumps(history, indent=2, default=str)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(response_json.encode("utf-8"))
                else:
                    self.send_response(404)
                    self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()
                
        except Exception as e:
            logger.error(f"Error in pipeline control API: {e}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            error_response = json.dumps({"error": str(e)})
            self.wfile.write(error_response.encode("utf-8"))
    
    @handle_errors(log_traceback=True, reraise=False)
    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)
        path_parts = parsed.path.strip("/").split("/")
        params = parse_qs(parsed.query)
        db_name = params.get("db_name", [DB_NAME])[0]
        
        try:
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            body_data = json.loads(body) if body else {}
            
            if len(path_parts) >= 3 and path_parts[0] == "api" and path_parts[1] == "pipeline":
                if path_parts[2] == "start":
                    # POST /api/pipeline/start
                    config_dict = body_data.get("config", {})
                    pipeline_id = body_data.get("pipeline_id")
                    
                    result = start_pipeline(
                        config_dict=config_dict,
                        pipeline_id=pipeline_id,
                        db_name=db_name,
                    )
                    
                    response_json = json.dumps(result, indent=2, default=str)
                    status_code = 200 if "error" not in result else 400
                    self.send_response(status_code)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(response_json.encode("utf-8"))
                    
                elif path_parts[2] == "cancel":
                    # POST /api/pipeline/cancel
                    pipeline_id = body_data.get("pipeline_id")
                    if not pipeline_id:
                        self.send_response(400)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        error_response = json.dumps({"error": "pipeline_id required"})
                        self.wfile.write(error_response.encode("utf-8"))
                        return
                    
                    result = cancel_pipeline(pipeline_id)
                    
                    response_json = json.dumps(result, indent=2, default=str)
                    status_code = 200 if "error" not in result else 400
                    self.send_response(status_code)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(response_json.encode("utf-8"))
                    
                elif path_parts[2] == "resume":
                    # POST /api/pipeline/resume (uses start with resume flag)
                    config_dict = body_data.get("config", {})
                    config_dict["resume_from_failure"] = True
                    pipeline_id = body_data.get("pipeline_id")
                    
                    result = start_pipeline(
                        config_dict=config_dict,
                        pipeline_id=pipeline_id,
                        db_name=db_name,
                    )
                    
                    response_json = json.dumps(result, indent=2, default=str)
                    status_code = 200 if "error" not in result else 400
                    self.send_response(status_code)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(response_json.encode("utf-8"))
                else:
                    self.send_response(404)
                    self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()
                
        except json.JSONDecodeError as e:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            error_response = json.dumps({"error": f"Invalid JSON: {str(e)}"})
            self.wfile.write(error_response.encode("utf-8"))
        except Exception as e:
            logger.error(f"Error in pipeline control API: {e}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            error_response = json.dumps({"error": str(e)})
            self.wfile.write(error_response.encode("utf-8"))
    
    def log_message(self, format, *args):
        """Suppress default HTTP logging."""
        pass


def start_pipeline_control_server(port: int = 8000, host: str = "0.0.0.0") -> None:
    """
    Start HTTP server for pipeline control API.
    
    Achievement 5.1: Pipeline Control API
    
    Args:
        port: Port to listen on (default: 8000)
        host: Host to bind to (default: 0.0.0.0)
    """
    server = HTTPServer((host, port), PipelineControlHandler)
    logger.info(f"✅ Pipeline control API server started on http://{host}:{port}/api/pipeline")
    logger.info("🎮 Pipeline control available via REST API")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Pipeline control API server stopped")
        server.shutdown()


if __name__ == "__main__":
    import sys
    
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    start_pipeline_control_server(port=port)

