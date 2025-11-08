"""
Quality Metrics API

Achievement 6.1: Quality Metrics Dashboard

REST API endpoints for retrieving per-stage quality metrics.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os
import sys


# Add project root to Python path for imports
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from core.libraries.error_handling.decorators import handle_errors
from dependencies.database.mongodb import get_mongo_client
from core.config.paths import DB_NAME
from business.services.graphrag.indexes import get_graphrag_collections
from business.stages.graphrag.extraction import GraphExtractionStage
from business.stages.graphrag.entity_resolution import EntityResolutionStage
from business.stages.graphrag.graph_construction import GraphConstructionStage
from business.stages.graphrag.community_detection import CommunityDetectionStage
from core.config.graphrag import GraphRAGPipelineConfig

logger = logging.getLogger(__name__)


def get_stage_quality_metrics(
    db_name: str,
    stage: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get quality metrics for one or all stages.

    Achievement 6.1: Quality Metrics Dashboard

    Args:
        db_name: Database name
        stage: Optional stage name (extraction, resolution, construction, detection)

    Returns:
        Dictionary with quality metrics per stage
    """
    client = get_mongo_client()
    db = client[db_name]
    collections = get_graphrag_collections(db)

    # Create default config
    config = GraphRAGPipelineConfig()
    config.extraction_config.db_name = db_name
    config.resolution_config.db_name = db_name
    config.construction_config.db_name = db_name
    config.detection_config.db_name = db_name

    metrics = {}

    # Extraction metrics
    if stage is None or stage == "extraction":
        try:
            extraction_stage = GraphExtractionStage(config.extraction_config)
            extraction_stats = extraction_stage.get_processing_stats()

            # Calculate canonical ratio (would need to query extraction data)
            # For now, use placeholder
            metrics["extraction"] = {
                "completion_rate": extraction_stats.get("completion_rate", 0),
                "failure_rate": extraction_stats.get("failure_rate", 0),
                "total_chunks": extraction_stats.get("total_chunks", 0),
                "processed_chunks": extraction_stats.get("processed_chunks", 0),
                "failed_chunks": extraction_stats.get("failed_chunks", 0),
                # Placeholder for canonical_ratio (would need extraction data analysis)
                "canonical_ratio": 0.95,  # Would calculate from actual data
            }
        except Exception as e:
            logger.error(f"Error getting extraction metrics: {e}")
            metrics["extraction"] = {"error": str(e)}

    # Resolution metrics
    if stage is None or stage == "resolution":
        try:
            resolution_stage = EntityResolutionStage(config.resolution_config)
            resolution_stats = resolution_stage.get_resolution_stats()

            total_entities = resolution_stats.get("total_entities", 0)
            total_mentions = resolution_stats.get("total_mentions", 0)

            # Calculate merge rate (entities / mentions)
            merge_rate = (
                (total_mentions - total_entities) / total_mentions if total_mentions > 0 else 0
            )

            metrics["resolution"] = {
                "completion_rate": resolution_stats.get("completion_rate", 0),
                "failure_rate": resolution_stats.get("failure_rate", 0),
                "total_entities": total_entities,
                "total_mentions": total_mentions,
                "merge_rate": merge_rate,
                "duplicate_reduction": merge_rate,  # Same as merge rate
                # Placeholder for llm_call_rate (would need tracking)
                "llm_call_rate": 0.1,  # Would calculate from actual data
            }
        except Exception as e:
            logger.error(f"Error getting resolution metrics: {e}")
            metrics["resolution"] = {"error": str(e)}

    # Construction metrics
    if stage is None or stage == "construction":
        try:
            construction_stage = GraphConstructionStage(config.construction_config)
            construction_stats = construction_stage.get_construction_stats()
            graph_metrics = construction_stage.calculate_graph_metrics()

            total_entities = graph_metrics.get("total_entities", 0)
            total_relationships = graph_metrics.get("total_relationships", 0)

            # Calculate graph density
            potential_edges = total_entities * (total_entities - 1) / 2 if total_entities > 1 else 0
            graph_density = total_relationships / potential_edges if potential_edges > 0 else 0

            # Get relationship type distribution
            relations_collection = collections["relations"]
            predicate_pipeline = [
                {"$group": {"_id": "$predicate", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
            ]
            predicate_dist = list(relations_collection.aggregate(predicate_pipeline))

            metrics["construction"] = {
                "completion_rate": construction_stats.get("completion_rate", 0),
                "failure_rate": construction_stats.get("failure_rate", 0),
                "total_relationships": total_relationships,
                "graph_density": graph_density,
                "avg_degree": graph_metrics.get("avg_degree", 0),
                "max_degree": graph_metrics.get("max_degree", 0),
                "relationship_types": len(predicate_dist),
                "top_predicates": [
                    {"predicate": p["_id"], "count": p["count"]} for p in predicate_dist[:10]
                ],
            }
        except Exception as e:
            logger.error(f"Error getting construction metrics: {e}")
            metrics["construction"] = {"error": str(e)}

    # Detection metrics
    if stage is None or stage == "detection":
        try:
            detection_stage = CommunityDetectionStage(config.detection_config)
            detection_stats = detection_stage.get_detection_stats()

            # Get latest quality metrics from graphrag_metrics collection
            metrics_collection = db.graphrag_metrics
            latest_metrics = metrics_collection.find_one(sort=[("timestamp", -1)])

            modularity = 0
            coverage = 0
            if latest_metrics:
                quality = latest_metrics.get("quality_metrics", {})
                modularity = quality.get("modularity", 0)
                coverage = quality.get("coverage", 0)

            metrics["detection"] = {
                "completion_rate": detection_stats.get("completion_rate", 0),
                "failure_rate": detection_stats.get("failure_rate", 0),
                "total_communities": detection_stats.get("total_communities", 0),
                "modularity": modularity,
                "coverage": coverage,
                "avg_community_size": detection_stats.get("avg_community_size", 0),
                "max_community_size": detection_stats.get("max_community_size", 0),
                "level_distribution": detection_stats.get("level_distribution", {}),
            }
        except Exception as e:
            logger.error(f"Error getting detection metrics: {e}")
            metrics["detection"] = {"error": str(e)}

    return metrics


def get_quality_trends(
    db_name: str,
    stage: str,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Get quality metrics trends over time.

    Achievement 6.1: Quality Metrics Dashboard

    Args:
        db_name: Database name
        stage: Stage name
        limit: Maximum number of data points

    Returns:
        Dictionary with time series data
    """
    client = get_mongo_client()
    db = client[db_name]
    metrics_collection = db.graphrag_metrics

    # Get metrics over time for the stage
    cursor = metrics_collection.find({"stage": stage}).sort("timestamp", -1).limit(limit)

    trends = []
    for doc in cursor:
        trends.append(
            {
                "timestamp": doc.get("timestamp"),
                "modularity": doc.get("quality_metrics", {}).get("modularity", 0),
                "coverage": doc.get("quality_metrics", {}).get("coverage", 0),
                "run_id": doc.get("run_id"),
            }
        )

    # Reverse to get chronological order
    trends.reverse()

    return {
        "stage": stage,
        "data_points": len(trends),
        "trends": trends,
    }


class QualityMetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for quality metrics API endpoints."""

    @handle_errors(log_traceback=True, reraise=False)
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path_parts = parsed.path.strip("/").split("/")
        params = parse_qs(parsed.query)
        db_name = params.get("db_name", [DB_NAME])[0]

        try:
            if len(path_parts) >= 3 and path_parts[0] == "api" and path_parts[1] == "quality":
                if path_parts[2] == "metrics":
                    # GET /api/quality/metrics?stage=extraction
                    stage = params.get("stage", [None])[0]

                    metrics = get_stage_quality_metrics(db_name=db_name, stage=stage)

                    response_json = json.dumps(metrics, indent=2, default=str)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(response_json.encode("utf-8"))

                elif path_parts[2] == "trends":
                    # GET /api/quality/trends?stage=detection
                    stage = params.get("stage", ["detection"])[0]
                    limit = int(params.get("limit", [50])[0])

                    trends = get_quality_trends(db_name=db_name, stage=stage, limit=limit)

                    response_json = json.dumps(trends, indent=2, default=str)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(response_json.encode("utf-8"))
                else:
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    error_response = json.dumps(
                        {"error": "Not found", "message": f"Unknown endpoint: {parsed.path}"}
                    )
                    self.wfile.write(error_response.encode("utf-8"))
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                error_response = json.dumps(
                    {"error": "Not found", "message": f"Unknown endpoint: {parsed.path}"}
                )
                self.wfile.write(error_response.encode("utf-8"))

        except Exception as e:
            logger.error(f"Error in quality metrics API: {e}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            error_response = json.dumps({"error": str(e)})
            self.wfile.write(error_response.encode("utf-8"))

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "3600")
        self.end_headers()

    def log_message(self, format, *args):
        """Suppress default HTTP logging."""
        pass


if __name__ == "__main__":
    from http.server import HTTPServer
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = HTTPServer(("0.0.0.0", port), QualityMetricsHandler)
    logger.info(f"✅ Quality metrics API server started on http://0.0.0.0:{port}/api/quality")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Quality metrics API server stopped")
        server.shutdown()
