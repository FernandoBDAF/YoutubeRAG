"""
Graph Data API - Central Router

Routes HTTP requests to appropriate handlers.
All routing logic is centralized here for easy maintenance.

Usage:
    from app.graph_api.router import handle_request
    
    result, status = handle_request("GET", "entities/search", {"q": "algorithm"})
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from .constants import (
    DEFAULT_DB_NAME,
    DEFAULT_LIMIT,
    DEFAULT_OFFSET,
    DEFAULT_MAX_HOPS,
    DEFAULT_MAX_NODES,
    MAX_LIMIT,
    API_VERSION,
    EXPORT_FORMATS,
)
from .handlers import (
    entities,
    communities,
    relationships,
    ego_network,
    export,
    statistics,
    quality_metrics,
    performance_metrics,
    metrics,
    query,
)

logger = logging.getLogger(__name__)


def handle_request(
    method: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    body: Optional[Dict[str, Any]] = None,
) -> tuple:
    """
    Route HTTP requests to handlers.

    Args:
        method: HTTP method (GET, POST)
        path: URL path without /api/ prefix
        params: Query parameters
        body: Request body for POST

    Returns:
        Tuple of (response_dict, status_code)
    """
    params = params or {}
    
    try:
        # Clean path
        path = path.lstrip("/")
        parts = path.split("/")
        
        # Get common parameters
        db_name = params.get("db_name", DEFAULT_DB_NAME)
        limit = min(int(params.get("limit", DEFAULT_LIMIT)), MAX_LIMIT)
        offset = int(params.get("offset", DEFAULT_OFFSET))

        # ========================================
        # Health Check
        # ========================================
        if method == "GET" and path == "health":
            return {
                "status": "healthy",
                "version": API_VERSION,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "service": "graph-data-api",
            }, 200

        # ========================================
        # Entity Endpoints
        # ========================================
        if path.startswith("entities"):
            if method == "GET":
                if len(parts) == 1 or (len(parts) == 2 and parts[1] == "search"):
                    # GET /entities or /entities/search
                    return entities.search(
                        db_name=db_name,
                        query=params.get("q"),
                        entity_type=params.get("type"),
                        min_confidence=_parse_float(params.get("min_confidence")),
                        min_source_count=_parse_int(params.get("min_source_count")),
                        limit=limit,
                        offset=offset,
                    ), 200
                elif len(parts) == 2:
                    # GET /entities/{entity_id}
                    entity_id = parts[1]
                    result = entities.get_details(db_name, entity_id)
                    if result is None:
                        return {"error": "Entity not found", "entity_id": entity_id}, 404
                    return result, 200

        # ========================================
        # Community Endpoints
        # ========================================
        if path.startswith("communities"):
            if method == "GET":
                if len(parts) == 1 or (len(parts) == 2 and parts[1] == "search"):
                    # GET /communities or /communities/search
                    return communities.search(
                        db_name=db_name,
                        level=_parse_int(params.get("level")),
                        min_size=_parse_int(params.get("min_size")),
                        max_size=_parse_int(params.get("max_size")),
                        min_coherence=_parse_float(params.get("min_coherence")),
                        limit=limit,
                        offset=offset,
                        sort_by=params.get("sort_by", "entity_count"),
                    ), 200
                elif len(parts) == 2 and parts[1] == "levels":
                    # GET /communities/levels
                    return communities.get_levels(db_name), 200
                elif len(parts) == 2:
                    # GET /communities/{community_id}
                    community_id = parts[1]
                    result = communities.get_details(db_name, community_id)
                    if result is None:
                        return {"error": "Community not found", "community_id": community_id}, 404
                    return result, 200

        # ========================================
        # Relationship Endpoints
        # ========================================
        if path.startswith("relationships"):
            if method == "GET":
                if len(parts) == 1 or (len(parts) == 2 and parts[1] == "search"):
                    # GET /relationships or /relationships/search
                    return relationships.search(
                        db_name=db_name,
                        predicate=params.get("predicate"),
                        entity_type=params.get("type"),
                        min_confidence=_parse_float(params.get("min_confidence")),
                        subject_id=params.get("subject_id"),
                        object_id=params.get("object_id"),
                        limit=limit,
                        offset=offset,
                    ), 200

        # ========================================
        # Ego Network Endpoints
        # ========================================
        if path.startswith("ego"):
            if method == "GET" and len(parts) >= 3 and parts[1] == "network":
                # GET /ego/network/{entity_id}
                entity_id = parts[2]
                max_hops = int(params.get("max_hops", DEFAULT_MAX_HOPS))
                max_nodes = int(params.get("max_nodes", DEFAULT_MAX_NODES))
                
                result = ego_network.get(db_name, entity_id, max_hops, max_nodes)
                status = 404 if "error" in result else 200
                return result, status

        # ========================================
        # Export Endpoints
        # ========================================
        if path.startswith("export"):
            if method == "GET" and len(parts) >= 2:
                # GET /export/{format}
                format_type = parts[1].lower()
                if format_type not in EXPORT_FORMATS:
                    return {"error": f"Unsupported format: {format_type}", "supported": EXPORT_FORMATS}, 400
                
                # Parse entity_ids if provided
                entity_ids = None
                if params.get("entity_ids"):
                    entity_ids = params["entity_ids"].split(",")
                
                community_id = params.get("community_id")
                
                if format_type == "json":
                    result = export.export_json(db_name, entity_ids, community_id)
                    return result, 200 if "error" not in result else 400
                elif format_type == "csv":
                    csv_data = export.export_csv(db_name, entity_ids, community_id)
                    return {"format": "csv", "data": csv_data}, 200
                elif format_type == "graphml":
                    graphml_data = export.export_graphml(db_name, entity_ids, community_id)
                    return {"format": "graphml", "data": graphml_data}, 200
                elif format_type == "gexf":
                    gexf_data = export.export_gexf(db_name, entity_ids, community_id)
                    return {"format": "gexf", "data": gexf_data}, 200

        # ========================================
        # Statistics Endpoints
        # ========================================
        if path == "statistics" or path == "stats":
            if method == "GET":
                return statistics.get(db_name), 200

        if path == "statistics/time" or path == "stats/time":
            if method == "GET":
                return statistics.get_over_time(db_name, limit), 200

        # ========================================
        # Metrics Endpoints
        # ========================================
        if path == "metrics" or path == "metrics/prometheus":
            if method == "GET":
                metrics_text = metrics.get_prometheus_metrics()
                return {"format": "prometheus", "data": metrics_text}, 200

        if path.startswith("metrics/quality"):
            if method == "GET":
                stage = params.get("stage")
                return quality_metrics.get_stage_metrics(db_name, stage), 200

        if path.startswith("metrics/performance"):
            if method == "GET":
                if "trends" in path:
                    return performance_metrics.get_trends(db_name, limit), 200
                else:
                    pipeline_id = params.get("pipeline_id")
                    return performance_metrics.get(db_name, pipeline_id), 200

        # ========================================
        # Query Endpoints
        # ========================================
        if path.startswith("query"):
            if method == "GET" and path == "query/modes":
                # GET /query/modes - List available query modes
                return query.get_query_modes(), 200
            
            if method == "POST" and (path == "query/execute" or path == "query"):
                # POST /query/execute - Execute natural language query
                if not body:
                    return {"error": "Request body is required"}, 400
                
                query_text = body.get("query")
                if not query_text:
                    return {"error": "Query text is required", "field": "query"}, 400
                
                mode = body.get("mode", "global")
                options = body.get("options", {})
                
                result = query.execute(
                    db_name=db_name,
                    query_text=query_text,
                    mode=mode,
                    options=options,
                )
                
                # Return appropriate status code based on result
                if "error" in result:
                    if "Configuration error" in result.get("error", ""):
                        return result, 500
                    elif "Invalid mode" in result.get("error", ""):
                        return result, 400
                    else:
                        return result, 500
                
                return result, 200

        # ========================================
        # Not Found
        # ========================================
        return {
            "error": "Not found",
            "message": f"Unknown endpoint: {method} /{path}",
            "available_endpoints": _get_available_endpoints(),
        }, 404

    except Exception as e:
        logger.exception(f"Error handling request: {method} /{path}")
        return {"error": "Internal server error", "message": str(e)}, 500


def _parse_int(value: Optional[str]) -> Optional[int]:
    """Parse string to int or return None."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _parse_float(value: Optional[str]) -> Optional[float]:
    """Parse string to float or return None."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _get_available_endpoints() -> list:
    """Get list of available endpoints."""
    return [
        "GET /health",
        "GET /entities/search?q=&type=&limit=&offset=",
        "GET /entities/{entity_id}",
        "GET /communities/search?level=&min_size=&sort_by=",
        "GET /communities/{community_id}",
        "GET /communities/levels",
        "GET /relationships/search?predicate=&subject_id=&object_id=",
        "GET /ego/network/{entity_id}?max_hops=&max_nodes=",
        "GET /export/{format}?entity_ids=&community_id=",
        "GET /statistics",
        "GET /statistics/time",
        "GET /metrics",
        "GET /metrics/quality?stage=",
        "GET /metrics/performance",
        "GET /metrics/performance/trends",
        "POST /query/execute",
        "GET /query/modes",
    ]


__all__ = ["handle_request"]

