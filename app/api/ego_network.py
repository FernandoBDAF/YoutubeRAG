"""
Ego Network API

Achievement 7.1: Ego Network Visualization

REST API endpoints for retrieving N-hop ego networks around entities.
"""

import json
import logging
from typing import Dict, Any, Optional, Set, List
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

logger = logging.getLogger(__name__)


def get_ego_network(
    db_name: str,
    entity_id: str,
    max_hops: int = 2,
    max_nodes: int = 100,
) -> Dict[str, Any]:
    """
    Get N-hop ego network around an entity.

    Achievement 7.1: Ego Network Visualization

    Args:
        db_name: Database name
        entity_id: Central entity ID
        max_hops: Maximum number of hops (1-hop = direct neighbors, 2-hop = neighbors of neighbors, etc.)
        max_nodes: Maximum number of nodes to return

    Returns:
        Dictionary with nodes and links for the ego network
    """
    client = get_mongo_client()
    db = client[db_name]
    collections = get_graphrag_collections(db)
    entities_collection = collections["entities"]
    relations_collection = collections["relations"]

    # Get central entity
    center_entity = entities_collection.find_one({"entity_id": entity_id})
    if not center_entity:
        return {
            "error": "Entity not found",
            "entity_id": entity_id,
        }

    # BFS to collect nodes at each hop level
    visited: Set[str] = {entity_id}
    nodes_by_hop: Dict[int, Set[str]] = {0: {entity_id}}
    all_relationships: List[Dict[str, Any]] = []

    # Get relationships for each hop level
    for hop in range(max_hops):
        current_level_nodes = nodes_by_hop.get(hop, set())
        if not current_level_nodes:
            break

        # Find all relationships where subject or object is in current level
        relationships = list(
            relations_collection.find(
                {
                    "$or": [
                        {"subject_id": {"$in": list(current_level_nodes)}},
                        {"object_id": {"$in": list(current_level_nodes)}},
                    ]
                }
            )
        )

        next_level_nodes: Set[str] = set()

        for rel in relationships:
            # Add relationship
            all_relationships.append(
                {
                    "subject_id": rel.get("subject_id"),
                    "object_id": rel.get("object_id"),
                    "predicate": rel.get("predicate"),
                    "confidence": rel.get("confidence", 0.0),
                    "hop": hop + 1,  # Relationship connects to next hop
                }
            )

            # Add connected nodes to next level
            subj_id = rel.get("subject_id")
            obj_id = rel.get("object_id")

            if subj_id not in visited:
                next_level_nodes.add(subj_id)
                visited.add(subj_id)

            if obj_id not in visited:
                next_level_nodes.add(obj_id)
                visited.add(obj_id)

        # Limit nodes if we exceed max_nodes
        if len(visited) > max_nodes:
            # Keep only first max_nodes nodes
            visited_list = list(visited)
            visited = set(visited_list[:max_nodes])
            next_level_nodes = next_level_nodes.intersection(visited)
            break

        if next_level_nodes:
            nodes_by_hop[hop + 1] = next_level_nodes

    # Get all entity details
    entity_ids = list(visited)
    entity_docs = list(
        entities_collection.find(
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
        )
    )

    # Build nodes list with hop information
    nodes = []
    for doc in entity_docs:
        entity_id_doc = doc.get("entity_id")
        hop_level = 0
        for hop, node_set in nodes_by_hop.items():
            if entity_id_doc in node_set:
                hop_level = hop
                break

        nodes.append(
            {
                "entity_id": entity_id_doc,
                "name": doc.get("name") or doc.get("canonical_name") or entity_id_doc,
                "canonical_name": doc.get("canonical_name"),
                "type": doc.get("type", "OTHER"),
                "description": doc.get("description", ""),
                "confidence": doc.get("confidence", 0.0),
                "source_count": doc.get("source_count", 0),
                "hop_level": hop_level,
                "is_center": entity_id_doc == entity_id,
            }
        )

    # Filter relationships to only include nodes we have
    valid_node_ids = set(entity_ids)
    links = []
    for rel in all_relationships:
        if rel["subject_id"] in valid_node_ids and rel["object_id"] in valid_node_ids:
            links.append(
                {
                    "source": rel["subject_id"],
                    "target": rel["object_id"],
                    "predicate": rel["predicate"],
                    "confidence": rel.get("confidence", 0.0),
                    "hop": rel.get("hop", 1),
                }
            )

    return {
        "center_entity": {
            "entity_id": entity_id,
            "name": center_entity.get("name") or center_entity.get("canonical_name") or entity_id,
            "type": center_entity.get("type", "OTHER"),
        },
        "nodes": nodes,
        "links": links,
        "max_hops": max_hops,
        "total_nodes": len(nodes),
        "total_links": len(links),
    }


class EgoNetworkHandler(BaseHTTPRequestHandler):
    """HTTP handler for ego network API endpoints."""

    @handle_errors(log_traceback=True, reraise=False)
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path_parts = parsed.path.strip("/").split("/")
        params = parse_qs(parsed.query)
        db_name = params.get("db_name", [DB_NAME])[0]

        try:
            if len(path_parts) >= 4 and path_parts[0] == "api" and path_parts[1] == "ego":
                if path_parts[2] == "network":
                    # GET /api/ego/network/{entity_id}?max_hops=2&max_nodes=100
                    entity_id = path_parts[3]
                    max_hops = int(params.get("max_hops", [2])[0])
                    max_nodes = int(params.get("max_nodes", [100])[0])

                    network = get_ego_network(
                        db_name=db_name,
                        entity_id=entity_id,
                        max_hops=max_hops,
                        max_nodes=max_nodes,
                    )

                    response_json = json.dumps(network, indent=2, default=str)
                    status_code = 200 if "error" not in network else 404
                    self.send_response(status_code)
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
            logger.error(f"Error in ego network API: {e}")
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
    server = HTTPServer(("0.0.0.0", port), EgoNetworkHandler)
    logger.info(f"✅ Ego network API server started on http://0.0.0.0:{port}/api/ego")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Ego network API server stopped")
        server.shutdown()
