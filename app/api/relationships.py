"""
Relationship API Endpoints

Achievement 3.2: Relationship Viewer

REST API endpoints for browsing and searching relationships in the GraphRAG knowledge graph.
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

logger = logging.getLogger(__name__)


def search_relationships(
    db_name: str,
    predicate: Optional[str] = None,
    entity_type: Optional[str] = None,
    min_confidence: Optional[float] = None,
    subject_id: Optional[str] = None,
    object_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    Search relationships with filters.
    
    Achievement 3.2: Relationship Viewer
    
    Args:
        db_name: Database name
        predicate: Filter by predicate type
        entity_type: Filter by entity type (subject or object)
        min_confidence: Minimum confidence threshold
        subject_id: Filter by subject entity ID
        object_id: Filter by object entity ID
        limit: Maximum number of results
        offset: Pagination offset
        
    Returns:
        Dictionary with results and pagination info
    """
    client = get_mongo_client()
    db = client[db_name]
    collections = get_graphrag_collections(db)
    relations_collection = collections["relations"]
    entities_collection = collections["entities"]
    
    # Build query filter
    filter_query = {}
    
    if predicate:
        filter_query["predicate"] = {"$regex": predicate, "$options": "i"}
    
    if min_confidence is not None:
        filter_query["confidence"] = {"$gte": min_confidence}
    
    if subject_id:
        filter_query["subject_id"] = subject_id
    
    if object_id:
        filter_query["object_id"] = object_id
    
    # Get total count
    total = relations_collection.count_documents(filter_query)
    
    # Get paginated results
    cursor = relations_collection.find(filter_query).skip(offset).limit(limit).sort("source_count", -1)
    
    relationships = []
    entity_ids = set()
    
    for doc in cursor:
        entity_ids.add(doc.get("subject_id"))
        entity_ids.add(doc.get("object_id"))
        
        relationships.append({
            "relationship_id": doc.get("relationship_id"),
            "subject_id": doc.get("subject_id"),
            "object_id": doc.get("object_id"),
            "predicate": doc.get("predicate"),
            "description": doc.get("description", ""),
            "confidence": doc.get("confidence", 0.0),
            "source_count": doc.get("source_count", 0),
            "source_chunks": doc.get("source_chunks", []),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
        })
    
    # Get entity names
    entity_names = {}
    if entity_ids:
        for entity_doc in entities_collection.find(
            {"entity_id": {"$in": list(entity_ids)}},
            {"entity_id": 1, "name": 1, "canonical_name": 1, "type": 1}
        ):
            entity_names[entity_doc["entity_id"]] = {
                "name": entity_doc.get("name"),
                "canonical_name": entity_doc.get("canonical_name"),
                "type": entity_doc.get("type"),
            }
    
    # Add entity names to relationships
    for rel in relationships:
        rel["subject_name"] = entity_names.get(rel["subject_id"], {})
        rel["object_name"] = entity_names.get(rel["object_id"], {})
        
        # Filter by entity type if specified
        if entity_type:
            subject_type = rel["subject_name"].get("type")
            object_type = rel["object_name"].get("type")
            if subject_type != entity_type and object_type != entity_type:
                # Remove from results (we'll filter after)
                continue
    
    # Filter by entity type if specified (post-processing)
    if entity_type:
        relationships = [
            rel for rel in relationships
            if rel["subject_name"].get("type") == entity_type or rel["object_name"].get("type") == entity_type
        ]
    
    return {
        "relationships": relationships,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total,
    }


class RelationshipAPIHandler(BaseHTTPRequestHandler):
    """HTTP handler for relationship API endpoints."""
    
    @handle_errors(log_traceback=True, reraise=False)
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path_parts = parsed.path.strip("/").split("/")
        
        # Parse query parameters
        params = parse_qs(parsed.query)
        db_name = params.get("db_name", [DB_NAME])[0]
        
        try:
            if len(path_parts) >= 2 and path_parts[0] == "api" and path_parts[1] == "relationships":
                if len(path_parts) == 2 or path_parts[2] == "search":
                    # Search relationships: /api/relationships/search
                    predicate = params.get("predicate", [None])[0]
                    entity_type = params.get("type", [None])[0]
                    min_confidence = params.get("min_confidence", [None])[0]
                    subject_id = params.get("subject_id", [None])[0]
                    object_id = params.get("object_id", [None])[0]
                    limit = int(params.get("limit", [50])[0])
                    offset = int(params.get("offset", [0])[0])
                    
                    if min_confidence:
                        min_confidence = float(min_confidence)
                    
                    results = search_relationships(
                        db_name=db_name,
                        predicate=predicate,
                        entity_type=entity_type,
                        min_confidence=min_confidence,
                        subject_id=subject_id,
                        object_id=object_id,
                        limit=limit,
                        offset=offset,
                    )
                    
                    response_json = json.dumps(results, indent=2, default=str)
                    
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
            logger.error(f"Error in relationship API: {e}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            error_response = json.dumps({"error": str(e)})
            self.wfile.write(error_response.encode("utf-8"))
    
    def log_message(self, format, *args):
        """Suppress default HTTP logging."""
        pass


def start_relationship_api_server(port: int = 8000, host: str = "0.0.0.0") -> None:
    """
    Start HTTP server for relationship API.
    
    Achievement 3.2: Relationship Viewer
    
    Args:
        port: Port to listen on (default: 8000)
        host: Host to bind to (default: 0.0.0.0)
    """
    from http.server import HTTPServer
    
    server = HTTPServer((host, port), RelationshipAPIHandler)
    logger.info(f"✅ Relationship API server started on http://{host}:{port}/api/relationships")
    logger.info("📊 Relationship search available via REST API")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Relationship API server stopped")
        server.shutdown()


if __name__ == "__main__":
    import sys
    
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    start_relationship_api_server(port=port)

