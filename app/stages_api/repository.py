"""
Pipeline Repository - MongoDB persistence layer

Stores pipeline execution state for recovery across server restarts.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Lazy-loaded MongoDB client to avoid import errors if MongoDB not available
_client = None
_repository: Optional["PipelineRepository"] = None


class PipelineRepository:
    """
    MongoDB repository for pipeline execution state.
    
    Collection: pipeline_executions
    """
    
    def __init__(self, connection_string: str, db_name: str = "mongo_hack"):
        from pymongo import MongoClient
        
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.collection = self.db.pipeline_executions
        self._ensure_indexes()
        logger.info(f"PipelineRepository initialized with database: {db_name}")
    
    def _ensure_indexes(self):
        """Create indexes for efficient queries"""
        try:
            self.collection.create_index("pipeline_id", unique=True)
            self.collection.create_index("status")
            self.collection.create_index("started_at")
            logger.debug("Pipeline execution indexes ensured")
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    def create(self, pipeline_state: Dict[str, Any]) -> str:
        """Create new pipeline execution record"""
        pipeline_state["created_at"] = datetime.utcnow()
        pipeline_state["updated_at"] = datetime.utcnow()
        
        try:
            self.collection.insert_one(pipeline_state)
            logger.debug(f"Created pipeline record: {pipeline_state['pipeline_id']}")
            return pipeline_state["pipeline_id"]
        except Exception as e:
            logger.error(f"Failed to create pipeline record: {e}")
            raise
    
    def get(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get pipeline by ID"""
        try:
            result = self.collection.find_one({"pipeline_id": pipeline_id})
            if result:
                result.pop("_id", None)
            return result
        except Exception as e:
            logger.error(f"Failed to get pipeline {pipeline_id}: {e}")
            return None
    
    def update(self, pipeline_id: str, updates: Dict[str, Any]) -> bool:
        """Update pipeline state"""
        updates["updated_at"] = datetime.utcnow()
        
        try:
            result = self.collection.update_one(
                {"pipeline_id": pipeline_id},
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update pipeline {pipeline_id}: {e}")
            return False
    
    def update_status(
        self,
        pipeline_id: str,
        status: str,
        progress: Optional[Dict] = None,
        error: Optional[str] = None,
        error_stage: Optional[str] = None
    ) -> bool:
        """Update pipeline status and optionally progress/error"""
        updates: Dict[str, Any] = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if progress:
            updates["progress"] = progress
        if error:
            updates["error"] = error
        if error_stage:
            updates["error_stage"] = error_stage
        if status in ["completed", "failed", "error", "cancelled", "interrupted"]:
            updates["completed_at"] = datetime.utcnow().isoformat() + "Z"
        
        return self.update(pipeline_id, updates)
    
    def list_active(self) -> List[Dict[str, Any]]:
        """List active pipelines (starting or running)"""
        try:
            cursor = self.collection.find(
                {"status": {"$in": ["starting", "running"]}},
                {"_id": 0}
            ).sort("started_at", -1)
            return list(cursor)
        except Exception as e:
            logger.error(f"Failed to list active pipelines: {e}")
            return []
    
    def list_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent pipeline executions"""
        try:
            cursor = self.collection.find(
                {},
                {"_id": 0}
            ).sort("started_at", -1).limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Failed to list pipeline history: {e}")
            return []
    
    def count_all(self) -> int:
        """Count total pipelines"""
        try:
            return self.collection.count_documents({})
        except Exception as e:
            logger.error(f"Failed to count pipelines: {e}")
            return 0
    
    def exists(self, pipeline_id: str) -> bool:
        """Check if pipeline exists"""
        try:
            return self.collection.count_documents({"pipeline_id": pipeline_id}) > 0
        except Exception as e:
            logger.error(f"Failed to check pipeline existence: {e}")
            return False


def get_repository() -> Optional[PipelineRepository]:
    """
    Get or create repository singleton.
    
    Returns None if MongoDB connection fails (allows graceful degradation).
    """
    global _repository
    
    if _repository is None:
        try:
            connection_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
            # MONGODB_DB takes priority (consistent with execution.py)
            db_name = os.getenv("MONGODB_DB") or os.getenv("DB_NAME") or "mongo_hack"
            _repository = PipelineRepository(connection_string, db_name)
        except Exception as e:
            logger.warning(f"Failed to initialize PipelineRepository: {e}")
            logger.warning("Pipeline persistence will be disabled - state lost on restart")
            return None
    
    return _repository


def is_persistence_enabled() -> bool:
    """Check if persistence is available"""
    return get_repository() is not None

