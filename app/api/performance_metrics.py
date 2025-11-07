"""
Performance Metrics API

Achievement 6.3: Performance Dashboard

REST API endpoints for retrieving pipeline performance metrics.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
import os
import sys


# Add project root to Python path for imports
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from core.libraries.error_handling.decorators import handle_errors
from dependencies.database.mongodb import get_mongo_client
from core.config.paths import DB_NAME
from business.services.observability.prometheus_metrics import get_metrics_tracker

logger = logging.getLogger(__name__)


def get_performance_metrics(
    db_name: str,
    pipeline_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get performance metrics for pipeline execution.
    
    Achievement 6.3: Performance Dashboard
    
    Args:
        db_name: Database name
        pipeline_id: Optional pipeline ID to filter by
        
    Returns:
        Dictionary with performance metrics
    """
    client = get_mongo_client()
    db = client[db_name]
    tracking_coll = db.experiment_tracking
    
    # Build query
    query = {"pipeline_type": "graphrag"}
    if pipeline_id:
        query["experiment_id"] = pipeline_id
    
    # Get latest pipeline run
    latest_run = tracking_coll.find_one(query, sort=[("started_at", -1)])
    
    if not latest_run:
        return {
            "error": "No pipeline runs found",
            "stages": {},
        }
    
    # Get stage-level performance from metrics collection
    metrics_collection = db.graphrag_metrics
    stage_metrics = {}
    
    stages = ["graph_extraction", "entity_resolution", "graph_construction", "community_detection"]
    for stage in stages:
        stage_docs = list(
            metrics_collection.find({"stage": stage})
            .sort("timestamp", -1)
            .limit(1)
        )
        
        if stage_docs:
            doc = stage_docs[0]
            stage_metrics[stage] = {
                "timestamp": doc.get("timestamp"),
                "run_id": doc.get("run_id"),
            }
    
    # Calculate duration if available
    duration = None
    if latest_run.get("started_at") and latest_run.get("completed_at"):
        start = latest_run["started_at"]
        end = latest_run["completed_at"]
        if isinstance(start, datetime) and isinstance(end, datetime):
            duration = (end - start).total_seconds()
        elif isinstance(start, str) and isinstance(end, str):
            # Parse ISO strings
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
            duration = (end_dt - start_dt).total_seconds()
    
    # Get chunk counts from tracking
    config = latest_run.get("configuration", {})
    total_chunks = config.get("total_chunks", 0)
    
    # Calculate throughput
    throughput = {}
    if duration and duration > 0 and total_chunks > 0:
        throughput["chunks_per_sec"] = total_chunks / duration
        throughput["chunks_per_min"] = (total_chunks / duration) * 60
    
    return {
        "pipeline_id": latest_run.get("experiment_id"),
        "status": latest_run.get("status"),
        "started_at": latest_run.get("started_at"),
        "completed_at": latest_run.get("completed_at"),
        "duration_seconds": duration,
        "total_chunks": total_chunks,
        "throughput": throughput,
        "stages": stage_metrics,
    }


def get_performance_trends(
    db_name: str,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Get performance trends over time.
    
    Achievement 6.3: Performance Dashboard
    
    Args:
        db_name: Database name
        limit: Maximum number of data points
        
    Returns:
        Dictionary with time series performance data
    """
    client = get_mongo_client()
    db = client[db_name]
    tracking_coll = db.experiment_tracking
    
    # Get pipeline runs over time
    cursor = (
        tracking_coll.find({"pipeline_type": "graphrag"})
        .sort("started_at", -1)
        .limit(limit)
    )
    
    trends = []
    for doc in cursor:
        started_at = doc.get("started_at")
        completed_at = doc.get("completed_at")
        
        duration = None
        if started_at and completed_at:
            if isinstance(started_at, datetime) and isinstance(completed_at, datetime):
                duration = (completed_at - started_at).total_seconds()
            elif isinstance(started_at, str) and isinstance(completed_at, str):
                try:
                    start_dt = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                    duration = (end_dt - start_dt).total_seconds()
                except:
                    pass
        
        config = doc.get("configuration", {})
        total_chunks = config.get("total_chunks", 0)
        
        throughput = None
        if duration and duration > 0 and total_chunks > 0:
            throughput = total_chunks / duration
        
        trends.append({
            "pipeline_id": doc.get("experiment_id"),
            "timestamp": started_at.isoformat() if isinstance(started_at, datetime) else str(started_at),
            "status": doc.get("status"),
            "duration_seconds": duration,
            "total_chunks": total_chunks,
            "throughput_chunks_per_sec": throughput,
        })
    
    # Reverse to get chronological order
    trends.reverse()
    
    return {
        "data_points": len(trends),
        "trends": trends,
    }


class PerformanceMetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for performance metrics API endpoints."""
    
    @handle_errors(log_traceback=True, reraise=False)
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path_parts = parsed.path.strip("/").split("/")
        params = parse_qs(parsed.query)
        db_name = params.get("db_name", [DB_NAME])[0]
        
        try:
            if len(path_parts) >= 3 and path_parts[0] == "api" and path_parts[1] == "performance":
                if path_parts[2] == "metrics":
                    # GET /api/performance/metrics?pipeline_id=xxx
                    pipeline_id = params.get("pipeline_id", [None])[0]
                    
                    metrics = get_performance_metrics(
                        db_name=db_name,
                        pipeline_id=pipeline_id,
                    )
                    
                    response_json = json.dumps(metrics, indent=2, default=str)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(response_json.encode("utf-8"))
                    
                elif path_parts[2] == "trends":
                    # GET /api/performance/trends
                    limit = int(params.get("limit", [50])[0])
                    
                    trends = get_performance_trends(db_name=db_name, limit=limit)
                    
                    response_json = json.dumps(trends, indent=2, default=str)
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
            logger.error(f"Error in performance metrics API: {e}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            error_response = json.dumps({"error": str(e)})
            self.wfile.write(error_response.encode("utf-8"))
    
    def log_message(self, format, *args):
        """Suppress default HTTP logging."""
        pass


if __name__ == "__main__":
    from http.server import HTTPServer
    import sys
    
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = HTTPServer(("0.0.0.0", port), PerformanceMetricsHandler)
    logger.info(f"✅ Performance metrics API server started on http://0.0.0.0:{port}/api/performance")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Performance metrics API server stopped")
        server.shutdown()

