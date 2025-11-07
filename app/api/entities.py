"""
Entity API Endpoints

Achievement 3.1: Entity Browser

REST API endpoints for browsing and searching entities in the GraphRAG knowledge graph.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from core.libraries.error_handling.decorators import handle_errors
from dependencies.database.mongodb import get_mongo_client
from core.config.paths import DB_NAME
from business.services.graphrag.indexes import get_graphrag_collections

logger = logging.getLogger(__name__)


def search_entities(
    db_name: str,
    query: Optional[str] = None,
    entity_type: Optional[str] = None,
    min_confidence: Optional[float] = None,
    min_source_count: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    Search entities with filters.
    
    Achievement 3.1: Entity Browser
    
    Args:
        db_name: Database name
        query: Search query (searches name, canonical_name, aliases)
        entity_type: Filter by entity type
        min_confidence: Minimum confidence threshold
        min_source_count: Minimum source_count threshold
        limit: Maximum number of results
        offset: Pagination offset
        
    Returns:
        Dictionary with results and pagination info
    """
    client = get_mongo_client()
    db = client[db_name]
    collections = get_graphrag_collections(db)
    entities_collection = collections["entities"]
    
    # Build query filter
    filter_query = {}
    
    if query:
        # Search in name, canonical_name, and aliases
        filter_query["$or"] = [
            {"name": {"$regex": query, "$options": "i"}},
            {"canonical_name": {"$regex": query, "$options": "i"}},
            {"aliases": {"$regex": query, "$options": "i"}},
        ]
    
    if entity_type:
        filter_query["type"] = entity_type
    
    if min_confidence is not None:
        filter_query["confidence"] = {"$gte": min_confidence}
    
    if min_source_count is not None:
        filter_query["source_count"] = {"$gte": min_source_count}
    
    # Get total count
    total = entities_collection.count_documents(filter_query)
    
    # Get paginated results
    cursor = entities_collection.find(filter_query).skip(offset).limit(limit).sort("source_count", -1)
    
    entities = []
    for doc in cursor:
        entity = {
            "entity_id": doc.get("entity_id"),
            "name": doc.get("name"),
            "canonical_name": doc.get("canonical_name"),
            "type": doc.get("type"),
            "description": doc.get("description", ""),
            "confidence": doc.get("confidence", 0.0),
            "source_count": doc.get("source_count", 0),
            "aliases": doc.get("aliases", []),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
        }
        entities.append(entity)
    
    return {
        "entities": entities,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total,
    }


def get_entity_details(
    db_name: str,
    entity_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific entity.
    
    Achievement 3.1: Entity Browser
    
    Args:
        db_name: Database name
        entity_id: Entity ID
        
    Returns:
        Entity details including relationships, or None if not found
    """
    client = get_mongo_client()
    db = client[db_name]
    collections = get_graphrag_collections(db)
    entities_collection = collections["entities"]
    relations_collection = collections["relations"]
    
    # Get entity
    entity_doc = entities_collection.find_one({"entity_id": entity_id})
    if not entity_doc:
        return None
    
    # Get relationships where this entity is subject or object
    relationships = []
    
    # As subject
    for rel in relations_collection.find({"subject_id": entity_id}):
        relationships.append({
            "relationship_id": rel.get("relationship_id"),
            "direction": "outgoing",
            "predicate": rel.get("predicate"),
            "object_id": rel.get("object_id"),
            "description": rel.get("description", ""),
            "confidence": rel.get("confidence", 0.0),
            "source_count": rel.get("source_count", 0),
        })
    
    # As object
    for rel in relations_collection.find({"object_id": entity_id}):
        relationships.append({
            "relationship_id": rel.get("relationship_id"),
            "direction": "incoming",
            "predicate": rel.get("predicate"),
            "subject_id": rel.get("subject_id"),
            "description": rel.get("description", ""),
            "confidence": rel.get("confidence", 0.0),
            "source_count": rel.get("source_count", 0),
        })
    
    # Get entity names for related entities
    related_entity_ids = set()
    for rel in relationships:
        if "subject_id" in rel:
            related_entity_ids.add(rel["subject_id"])
        if "object_id" in rel:
            related_entity_ids.add(rel["object_id"])
    
    related_entity_names = {}
    if related_entity_ids:
        for entity_doc in entities_collection.find(
            {"entity_id": {"$in": list(related_entity_ids)}},
            {"entity_id": 1, "name": 1, "canonical_name": 1, "type": 1}
        ):
            related_entity_names[entity_doc["entity_id"]] = {
                "name": entity_doc.get("name"),
                "canonical_name": entity_doc.get("canonical_name"),
                "type": entity_doc.get("type"),
            }
    
    # Add entity names to relationships
    for rel in relationships:
        if "subject_id" in rel:
            rel["subject_name"] = related_entity_names.get(rel["subject_id"], {})
        if "object_id" in rel:
            rel["object_name"] = related_entity_names.get(rel["object_id"], {})
    
    return {
        "entity_id": entity_doc.get("entity_id"),
        "name": entity_doc.get("name"),
        "canonical_name": entity_doc.get("canonical_name"),
        "type": entity_doc.get("type"),
        "description": entity_doc.get("description", ""),
        "confidence": entity_doc.get("confidence", 0.0),
        "source_count": entity_doc.get("source_count", 0),
        "aliases": entity_doc.get("aliases", []),
        "source_chunks": entity_doc.get("source_chunks", []),
        "created_at": entity_doc.get("created_at"),
        "updated_at": entity_doc.get("updated_at"),
        "relationships": relationships,
        "relationship_count": len(relationships),
    }


class EntityAPIHandler(BaseHTTPRequestHandler):
    """HTTP handler for entity API endpoints."""
    
    @handle_errors(log_traceback=True, reraise=False)
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path_parts = parsed.path.strip("/").split("/")
        
        # Parse query parameters
        params = parse_qs(parsed.query)
        db_name = params.get("db_name", [DB_NAME])[0]
        
        try:
            if len(path_parts) >= 2 and path_parts[0] == "api" and path_parts[1] == "entities":
                if len(path_parts) == 2 or path_parts[2] == "search":
                    # Search entities: /api/entities/search
                    query = params.get("q", [None])[0]
                    entity_type = params.get("type", [None])[0]
                    min_confidence = params.get("min_confidence", [None])[0]
                    min_source_count = params.get("min_source_count", [None])[0]
                    limit = int(params.get("limit", [50])[0])
                    offset = int(params.get("offset", [0])[0])
                    
                    if min_confidence:
                        min_confidence = float(min_confidence)
                    if min_source_count:
                        min_source_count = int(min_source_count)
                    
                    results = search_entities(
                        db_name=db_name,
                        query=query,
                        entity_type=entity_type,
                        min_confidence=min_confidence,
                        min_source_count=min_source_count,
                        limit=limit,
                        offset=offset,
                    )
                    
                    response_json = json.dumps(results, indent=2, default=str)
                    
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(response_json.encode("utf-8"))
                    
                elif len(path_parts) == 3:
                    # Get entity details: /api/entities/{entity_id}
                    entity_id = path_parts[2]
                    
                    entity = get_entity_details(db_name=db_name, entity_id=entity_id)
                    
                    if entity is None:
                        self.send_response(404)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        error_response = json.dumps({"error": "Entity not found"})
                        self.wfile.write(error_response.encode("utf-8"))
                    else:
                        response_json = json.dumps(entity, indent=2, default=str)
                        
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
            logger.error(f"Error in entity API: {e}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            error_response = json.dumps({"error": str(e)})
            self.wfile.write(error_response.encode("utf-8"))
    
    def log_message(self, format, *args):
        """Suppress default HTTP logging."""
        pass


def start_entity_api_server(port: int = 8000, host: str = "0.0.0.0") -> None:
    """
    Start HTTP server for entity API.
    
    Achievement 3.1: Entity Browser
    
    Args:
        port: Port to listen on (default: 8000)
        host: Host to bind to (default: 0.0.0.0)
    """
    from http.server import HTTPServer
    
    server = HTTPServer((host, port), EntityAPIHandler)
    logger.info(f"✅ Entity API server started on http://{host}:{port}/api/entities")
    logger.info("📊 Entity search and details available via REST API")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Entity API server stopped")
        server.shutdown()


if __name__ == "__main__":
    import sys
    
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    start_entity_api_server(port=port)

