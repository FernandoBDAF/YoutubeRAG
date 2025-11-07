"""
Community API Endpoints

Achievement 4.1: Community Explorer

REST API endpoints for browsing and searching communities in the GraphRAG knowledge graph.
"""

import json
import logging
from typing import Dict, Any, Optional
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os
import sys


# Add project root to Python path for imports
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from core.libraries.error_handling.decorators import handle_errors
from dependencies.database.mongodb import get_mongo_client
from core.config.paths import DB_NAME
from business.services.graphrag.indexes import get_graphrag_collections

logger = logging.getLogger(__name__)


def search_communities(
    db_name: str,
    level: Optional[int] = None,
    min_size: Optional[int] = None,
    max_size: Optional[int] = None,
    min_coherence: Optional[float] = None,
    limit: int = 50,
    offset: int = 0,
    sort_by: str = "entity_count",  # "entity_count", "coherence_score", "level"
) -> Dict[str, Any]:
    """
    Search communities with filters.

    Achievement 4.1: Community Explorer

    Args:
        db_name: Database name
        level: Filter by community level
        min_size: Minimum entity count
        max_size: Maximum entity count
        min_coherence: Minimum coherence score
        limit: Maximum number of results
        offset: Pagination offset
        sort_by: Sort field ("entity_count", "coherence_score", "level")

    Returns:
        Dictionary with results and pagination info
    """
    client = get_mongo_client()
    db = client[db_name]
    collections = get_graphrag_collections(db)
    communities_collection = collections["communities"]

    # Build query filter
    filter_query = {}

    if level is not None:
        filter_query["level"] = level

    if min_size is not None or max_size is not None:
        size_filter = {}
        if min_size is not None:
            size_filter["$gte"] = min_size
        if max_size is not None:
            size_filter["$lte"] = max_size
        filter_query["entity_count"] = size_filter

    if min_coherence is not None:
        filter_query["coherence_score"] = {"$gte": min_coherence}

    # Determine sort order
    sort_order = -1 if sort_by in ["entity_count", "coherence_score"] else 1

    # Get total count
    total = communities_collection.count_documents(filter_query)

    # Get paginated results
    cursor = (
        communities_collection.find(filter_query)
        .skip(offset)
        .limit(limit)
        .sort(sort_by, sort_order)
    )

    communities = []
    for doc in cursor:
        community = {
            "community_id": doc.get("community_id"),
            "level": doc.get("level", 0),
            "title": doc.get("title", ""),
            "summary": doc.get("summary", ""),
            "entities": doc.get("entities", []),
            "entity_count": doc.get("entity_count", len(doc.get("entities", []))),
            "relationship_count": doc.get("relationship_count", 0),
            "coherence_score": doc.get("coherence_score", 0.0),
            "source_chunks": doc.get("source_chunks", []),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
            "run_id": doc.get("run_id"),
            "params_hash": doc.get("params_hash"),
        }
        communities.append(community)

    return {
        "communities": communities,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total,
    }


def get_community_details(
    db_name: str,
    community_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific community.

    Achievement 4.1: Community Explorer

    Args:
        db_name: Database name
        community_id: Community ID

    Returns:
        Community details including entities and relationships, or None if not found
    """
    client = get_mongo_client()
    db = client[db_name]
    collections = get_graphrag_collections(db)
    communities_collection = collections["communities"]
    entities_collection = collections["entities"]
    relations_collection = collections["relations"]

    # Get community
    community_doc = communities_collection.find_one({"community_id": community_id})
    if not community_doc:
        return None

    entity_ids = community_doc.get("entities", [])

    # Get entity details
    entity_details = []
    if entity_ids:
        for entity_doc in entities_collection.find(
            {"entity_id": {"$in": entity_ids}},
            {
                "entity_id": 1,
                "name": 1,
                "canonical_name": 1,
                "type": 1,
                "description": 1,
                "confidence": 1,
                "source_count": 1,
            },
        ):
            entity_details.append(
                {
                    "entity_id": entity_doc.get("entity_id"),
                    "name": entity_doc.get("name"),
                    "canonical_name": entity_doc.get("canonical_name"),
                    "type": entity_doc.get("type"),
                    "description": entity_doc.get("description", ""),
                    "confidence": entity_doc.get("confidence", 0.0),
                    "source_count": entity_doc.get("source_count", 0),
                }
            )

    # Get relationships within community (both subject and object are in community)
    relationships = []
    if entity_ids:
        for rel in relations_collection.find(
            {
                "subject_id": {"$in": entity_ids},
                "object_id": {"$in": entity_ids},
            }
        ):
            relationships.append(
                {
                    "relationship_id": rel.get("relationship_id"),
                    "subject_id": rel.get("subject_id"),
                    "object_id": rel.get("object_id"),
                    "predicate": rel.get("predicate"),
                    "description": rel.get("description", ""),
                    "confidence": rel.get("confidence", 0.0),
                    "source_count": rel.get("source_count", 0),
                }
            )

    # Add entity names to relationships
    entity_map = {e["entity_id"]: e for e in entity_details}
    for rel in relationships:
        rel["subject_name"] = entity_map.get(rel["subject_id"], {})
        rel["object_name"] = entity_map.get(rel["object_id"], {})

    return {
        "community_id": community_doc.get("community_id"),
        "level": community_doc.get("level", 0),
        "title": community_doc.get("title", ""),
        "summary": community_doc.get("summary", ""),
        "entity_count": community_doc.get("entity_count", len(entity_ids)),
        "relationship_count": len(relationships),
        "coherence_score": community_doc.get("coherence_score", 0.0),
        "source_chunks": community_doc.get("source_chunks", []),
        "created_at": community_doc.get("created_at"),
        "updated_at": community_doc.get("updated_at"),
        "run_id": community_doc.get("run_id"),
        "params_hash": community_doc.get("params_hash"),
        "entities": entity_details,
        "relationships": relationships,
    }


def get_community_levels(db_name: str) -> Dict[str, Any]:
    """
    Get statistics about community levels.

    Achievement 4.3: Multi-Resolution Community Navigation

    Args:
        db_name: Database name

    Returns:
        Dictionary with level statistics
    """
    client = get_mongo_client()
    db = client[db_name]
    collections = get_graphrag_collections(db)
    communities_collection = collections["communities"]

    # Aggregate by level
    pipeline = [
        {
            "$group": {
                "_id": "$level",
                "count": {"$sum": 1},
                "avg_size": {"$avg": "$entity_count"},
                "avg_coherence": {"$avg": "$coherence_score"},
                "total_entities": {"$sum": "$entity_count"},
            }
        },
        {"$sort": {"_id": 1}},
    ]

    level_stats = list(communities_collection.aggregate(pipeline))

    return {
        "levels": [
            {
                "level": stat["_id"],
                "count": stat["count"],
                "avg_size": round(stat["avg_size"], 2),
                "avg_coherence": round(stat["avg_coherence"], 4),
                "total_entities": stat["total_entities"],
            }
            for stat in level_stats
        ],
    }


class CommunityAPIHandler(BaseHTTPRequestHandler):
    """HTTP handler for community API endpoints."""

    @handle_errors(log_traceback=True, reraise=False)
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path_parts = parsed.path.strip("/").split("/")

        # Parse query parameters
        params = parse_qs(parsed.query)
        db_name = params.get("db_name", [DB_NAME])[0]

        try:
            if len(path_parts) >= 2 and path_parts[0] == "api" and path_parts[1] == "communities":
                if len(path_parts) == 2 or path_parts[2] == "search":
                    # Search communities: /api/communities/search
                    level = params.get("level", [None])[0]
                    min_size = params.get("min_size", [None])[0]
                    max_size = params.get("max_size", [None])[0]
                    min_coherence = params.get("min_coherence", [None])[0]
                    limit = int(params.get("limit", [50])[0])
                    offset = int(params.get("offset", [0])[0])
                    sort_by = params.get("sort_by", ["entity_count"])[0]

                    if level:
                        level = int(level)
                    if min_size:
                        min_size = int(min_size)
                    if max_size:
                        max_size = int(max_size)
                    if min_coherence:
                        min_coherence = float(min_coherence)

                    results = search_communities(
                        db_name=db_name,
                        level=level,
                        min_size=min_size,
                        max_size=max_size,
                        min_coherence=min_coherence,
                        limit=limit,
                        offset=offset,
                        sort_by=sort_by,
                    )

                    response_json = json.dumps(results, indent=2, default=str)

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(response_json.encode("utf-8"))

                elif path_parts[2] == "levels":
                    # Get community levels: /api/communities/levels
                    results = get_community_levels(db_name=db_name)

                    response_json = json.dumps(results, indent=2, default=str)

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(response_json.encode("utf-8"))

                elif len(path_parts) == 3:
                    # Get community details: /api/communities/{community_id}
                    community_id = path_parts[2]

                    community = get_community_details(db_name=db_name, community_id=community_id)

                    if community is None:
                        self.send_response(404)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        error_response = json.dumps({"error": "Community not found"})
                        self.wfile.write(error_response.encode("utf-8"))
                    else:
                        response_json = json.dumps(community, indent=2, default=str)

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
            logger.error(f"Error in community API: {e}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            error_response = json.dumps({"error": str(e)})
            self.wfile.write(error_response.encode("utf-8"))

    def log_message(self, format, *args):
        """Suppress default HTTP logging."""
        pass


def start_community_api_server(port: int = 8000, host: str = "0.0.0.0") -> None:
    """
    Start HTTP server for community API.

    Achievement 4.1: Community Explorer

    Args:
        port: Port to listen on (default: 8000)
        host: Host to bind to (default: 0.0.0.0)
    """
    from http.server import HTTPServer

    server = HTTPServer((host, port), CommunityAPIHandler)
    logger.info(f"✅ Community API server started on http://{host}:{port}/api/communities")
    logger.info("📊 Community search and details available via REST API")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Community API server stopped")
        server.shutdown()


if __name__ == "__main__":
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    start_community_api_server(port=port)
