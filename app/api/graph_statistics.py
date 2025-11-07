"""
Graph Statistics API

Achievement 6.2: Graph Statistics Dashboard

REST API endpoints for retrieving graph-level statistics and analytics.
"""

import json
import logging
from typing import Dict, Any, Optional
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from core.libraries.error_handling.decorators import handle_errors
from dependencies.database.mongodb import get_mongo_client
from core.config.paths import DB_NAME
from business.services.graphrag.indexes import get_graphrag_collections
from business.stages.graphrag.graph_construction import GraphConstructionStage
from core.config.graphrag import GraphRAGPipelineConfig

logger = logging.getLogger(__name__)


def get_graph_statistics(db_name: str) -> Dict[str, Any]:
    """
    Get comprehensive graph statistics.

    Achievement 6.2: Graph Statistics Dashboard

    Args:
        db_name: Database name

    Returns:
        Dictionary with graph statistics
    """
    client = get_mongo_client()
    db = client[db_name]
    collections = get_graphrag_collections(db)
    entities_collection = collections["entities"]
    relations_collection = collections["relations"]

    # Basic counts
    total_entities = entities_collection.count_documents({})
    total_relationships = relations_collection.count_documents({})

    # Entity type distribution
    type_pipeline = [
        {"$group": {"_id": "$type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    type_distribution = list(entities_collection.aggregate(type_pipeline))

    # Predicate distribution
    predicate_pipeline = [
        {"$group": {"_id": "$predicate", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    predicate_distribution = list(relations_collection.aggregate(predicate_pipeline))

    # Calculate entity degrees
    entity_degrees = {}

    # Outgoing relationships
    outgoing_pipeline = [{"$group": {"_id": "$subject_id", "count": {"$sum": 1}}}]
    for result in relations_collection.aggregate(outgoing_pipeline):
        entity_degrees[result["_id"]] = entity_degrees.get(result["_id"], 0) + result["count"]

    # Incoming relationships
    incoming_pipeline = [{"$group": {"_id": "$object_id", "count": {"$sum": 1}}}]
    for result in relations_collection.aggregate(incoming_pipeline):
        entity_degrees[result["_id"]] = entity_degrees.get(result["_id"], 0) + result["count"]

    # Degree statistics
    degrees = list(entity_degrees.values())
    avg_degree = sum(degrees) / len(degrees) if degrees else 0
    max_degree = max(degrees) if degrees else 0
    min_degree = min(degrees) if degrees else 0

    # Degree distribution (histogram)
    degree_buckets = {}
    for degree in degrees:
        bucket = (degree // 5) * 5  # Bucket by 5s
        degree_buckets[bucket] = degree_buckets.get(bucket, 0) + 1

    # Graph density
    potential_edges = total_entities * (total_entities - 1) / 2 if total_entities > 1 else 0
    graph_density = total_relationships / potential_edges if potential_edges > 0 else 0

    # Connected components (simplified - count isolated entities)
    isolated_entities = total_entities - len(entity_degrees)

    # Clustering coefficient (simplified - would need full graph analysis)
    # For now, use edge-to-node ratio as proxy
    edge_to_node_ratio = total_relationships / total_entities if total_entities > 0 else 0

    return {
        "total_entities": total_entities,
        "total_relationships": total_relationships,
        "graph_density": graph_density,
        "edge_to_node_ratio": edge_to_node_ratio,
        "isolated_entities": isolated_entities,
        "connected_entities": len(entity_degrees),
        "avg_degree": round(avg_degree, 2),
        "max_degree": max_degree,
        "min_degree": min_degree,
        "type_distribution": [{"type": t["_id"], "count": t["count"]} for t in type_distribution],
        "predicate_distribution": [
            {"predicate": p["_id"], "count": p["count"]}
            for p in predicate_distribution[:20]  # Top 20
        ],
        "degree_distribution": [
            {"degree": k, "count": v} for k, v in sorted(degree_buckets.items())
        ],
    }


def get_graph_statistics_over_time(
    db_name: str,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Get graph statistics over time from metrics collection.

    Achievement 6.2: Graph Statistics Dashboard

    Args:
        db_name: Database name
        limit: Maximum number of data points

    Returns:
        Dictionary with time series data
    """
    client = get_mongo_client()
    db = client[db_name]
    metrics_collection = db.graphrag_metrics

    # Get latest metrics over time
    cursor = metrics_collection.find({}).sort("timestamp", -1).limit(limit)

    time_series = []
    for doc in cursor:
        graph_data = doc.get("graph", {})
        time_series.append(
            {
                "timestamp": doc.get("timestamp"),
                "nodes": graph_data.get("nodes", 0),
                "edges": graph_data.get("edges", 0),
                "density": graph_data.get("density", 0),
                "edge_to_node_ratio": graph_data.get("edge_to_node_ratio", 0),
                "run_id": doc.get("run_id"),
            }
        )

    # Reverse to get chronological order
    time_series.reverse()

    return {
        "data_points": len(time_series),
        "time_series": time_series,
    }


class GraphStatisticsHandler(BaseHTTPRequestHandler):
    """HTTP handler for graph statistics API endpoints."""

    @handle_errors(log_traceback=True, reraise=False)
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path_parts = parsed.path.strip("/").split("/")
        params = parse_qs(parsed.query)
        db_name = params.get("db_name", [DB_NAME])[0]

        try:
            if len(path_parts) >= 3 and path_parts[0] == "api" and path_parts[1] == "graph":
                if path_parts[2] == "statistics":
                    # GET /api/graph/statistics
                    stats = get_graph_statistics(db_name=db_name)

                    response_json = json.dumps(stats, indent=2, default=str)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(response_json.encode("utf-8"))

                elif path_parts[2] == "trends":
                    # GET /api/graph/trends
                    limit = int(params.get("limit", [50])[0])

                    trends = get_graph_statistics_over_time(db_name=db_name, limit=limit)

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
            logger.error(f"Error in graph statistics API: {e}")
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
    server = HTTPServer(("0.0.0.0", port), GraphStatisticsHandler)
    logger.info(f"✅ Graph statistics API server started on http://0.0.0.0:{port}/api/graph")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Graph statistics API server stopped")
        server.shutdown()
