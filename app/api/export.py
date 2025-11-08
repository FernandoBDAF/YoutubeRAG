"""
Graph Export API

Achievement 7.3: Export & Integration Features

REST API endpoints for exporting graphs in various formats (GraphML, GEXF, JSON, CSV).
"""

import json
import logging
import csv
from typing import Dict, Any, Optional
from io import StringIO
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


def export_graph_json(
    db_name: str,
    entity_ids: Optional[list] = None,
    community_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Export graph as JSON.

    Achievement 7.3: Export & Integration Features

    Args:
        db_name: Database name
        entity_ids: Optional list of entity IDs to export (subgraph)
        community_id: Optional community ID to export

    Returns:
        Dictionary with nodes and links
    """
    client = get_mongo_client()
    db = client[db_name]
    collections = get_graphrag_collections(db)
    entities_collection = collections["entities"]
    relations_collection = collections["relations"]

    # Determine which entities to export
    if community_id:
        # Get community entities
        communities_collection = collections["communities"]
        community = communities_collection.find_one({"community_id": community_id})
        if not community:
            return {"error": "Community not found"}
        entity_ids = community.get("entities", [])
    elif not entity_ids:
        # Export all entities
        entity_ids = [doc["entity_id"] for doc in entities_collection.find({}, {"entity_id": 1})]

    # Get entity details
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

    # Get relationships between these entities
    relationships = list(
        relations_collection.find(
            {
                "$and": [
                    {"subject_id": {"$in": entity_ids}},
                    {"object_id": {"$in": entity_ids}},
                ]
            }
        )
    )

    # Build nodes
    nodes = []
    for doc in entity_docs:
        nodes.append(
            {
                "id": doc.get("entity_id"),
                "name": doc.get("name") or doc.get("canonical_name") or doc.get("entity_id"),
                "canonical_name": doc.get("canonical_name"),
                "type": doc.get("type", "OTHER"),
                "description": doc.get("description", ""),
                "confidence": doc.get("confidence", 0.0),
                "source_count": doc.get("source_count", 0),
            }
        )

    # Build links
    links = []
    for rel in relationships:
        links.append(
            {
                "source": rel.get("subject_id"),
                "target": rel.get("object_id"),
                "predicate": rel.get("predicate"),
                "description": rel.get("description", ""),
                "confidence": rel.get("confidence", 0.0),
                "source_count": rel.get("source_count", 0),
            }
        )

    return {
        "nodes": nodes,
        "links": links,
        "metadata": {
            "total_nodes": len(nodes),
            "total_links": len(links),
            "export_type": "community" if community_id else ("subgraph" if entity_ids else "full"),
        },
    }


def export_graph_csv(
    db_name: str,
    entity_ids: Optional[list] = None,
    community_id: Optional[str] = None,
) -> str:
    """
    Export graph as CSV (nodes and links as separate CSV sections).

    Achievement 7.3: Export & Integration Features

    Args:
        db_name: Database name
        entity_ids: Optional list of entity IDs to export
        community_id: Optional community ID to export

    Returns:
        CSV string
    """
    graph_data = export_graph_json(db_name, entity_ids, community_id)

    if "error" in graph_data:
        return f"Error: {graph_data['error']}"

    output = StringIO()

    # Write nodes CSV
    output.write("Nodes:\n")
    writer = csv.writer(output)
    writer.writerow(
        ["id", "name", "canonical_name", "type", "description", "confidence", "source_count"]
    )
    for node in graph_data["nodes"]:
        writer.writerow(
            [
                node.get("id"),
                node.get("name", ""),
                node.get("canonical_name", ""),
                node.get("type", ""),
                node.get("description", ""),
                node.get("confidence", 0),
                node.get("source_count", 0),
            ]
        )

    output.write("\nLinks:\n")
    writer.writerow(["source", "target", "predicate", "description", "confidence", "source_count"])
    for link in graph_data["links"]:
        writer.writerow(
            [
                link.get("source"),
                link.get("target"),
                link.get("predicate", ""),
                link.get("description", ""),
                link.get("confidence", 0),
                link.get("source_count", 0),
            ]
        )

    return output.getvalue()


def export_graph_graphml(
    db_name: str,
    entity_ids: Optional[list] = None,
    community_id: Optional[str] = None,
) -> str:
    """
    Export graph as GraphML format.

    Achievement 7.3: Export & Integration Features

    Args:
        db_name: Database name
        entity_ids: Optional list of entity IDs to export
        community_id: Optional community ID to export

    Returns:
        GraphML XML string
    """
    graph_data = export_graph_json(db_name, entity_ids, community_id)

    if "error" in graph_data:
        return f"Error: {graph_data['error']}"

    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns"',
        '         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        '         xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns',
        '         http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">',
        '  <key id="type" for="node" attr.name="type" attr.type="string"/>',
        '  <key id="name" for="node" attr.name="name" attr.type="string"/>',
        '  <key id="predicate" for="edge" attr.name="predicate" attr.type="string"/>',
        '  <key id="confidence" for="edge" attr.name="confidence" attr.type="double"/>',
        '  <graph id="G" edgedefault="directed">',
    ]

    # Add nodes
    for node in graph_data["nodes"]:
        xml_parts.append(f'    <node id="{node["id"]}">')
        xml_parts.append(f'      <data key="name">{_escape_xml(node.get("name", ""))}</data>')
        xml_parts.append(f'      <data key="type">{_escape_xml(node.get("type", ""))}</data>')
        xml_parts.append("    </node>")

    # Add edges
    for i, link in enumerate(graph_data["links"]):
        xml_parts.append(
            f'    <edge id="e{i}" source="{link["source"]}" target="{link["target"]}">'
        )
        xml_parts.append(
            f'      <data key="predicate">{_escape_xml(link.get("predicate", ""))}</data>'
        )
        xml_parts.append(f'      <data key="confidence">{link.get("confidence", 0)}</data>')
        xml_parts.append("    </edge>")

    xml_parts.append("  </graph>")
    xml_parts.append("</graphml>")

    return "\n".join(xml_parts)


def export_graph_gexf(
    db_name: str,
    entity_ids: Optional[list] = None,
    community_id: Optional[str] = None,
) -> str:
    """
    Export graph as GEXF format.

    Achievement 7.3: Export & Integration Features

    Args:
        db_name: Database name
        entity_ids: Optional list of entity IDs to export
        community_id: Optional community ID to export

    Returns:
        GEXF XML string
    """
    graph_data = export_graph_json(db_name, entity_ids, community_id)

    if "error" in graph_data:
        return f"Error: {graph_data['error']}"

    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">',
        "  <meta>",
        "    <creator>GraphRAG Pipeline Visualization</creator>",
        "    <description>Exported graph</description>",
        "  </meta>",
        '  <graph mode="static" defaultedgetype="directed">',
        '    <attributes class="node">',
        '      <attribute id="type" title="Type" type="string"/>',
        '      <attribute id="name" title="Name" type="string"/>',
        "    </attributes>",
        '    <attributes class="edge">',
        '      <attribute id="predicate" title="Predicate" type="string"/>',
        '      <attribute id="confidence" title="Confidence" type="double"/>',
        "    </attributes>",
        "    <nodes>",
    ]

    # Add nodes
    for node in graph_data["nodes"]:
        xml_parts.append(
            f'      <node id="{node["id"]}" label="{_escape_xml(node.get("name", ""))}">'
        )
        xml_parts.append("        <attvalues>")
        xml_parts.append(
            f'          <attvalue for="type" value="{_escape_xml(node.get("type", ""))}"/>'
        )
        xml_parts.append(
            f'          <attvalue for="name" value="{_escape_xml(node.get("name", ""))}"/>'
        )
        xml_parts.append("        </attvalues>")
        xml_parts.append("      </node>")

    xml_parts.append("    </nodes>")
    xml_parts.append("    <edges>")

    # Add edges
    for i, link in enumerate(graph_data["links"]):
        xml_parts.append(
            f'      <edge id="e{i}" source="{link["source"]}" target="{link["target"]}">'
        )
        xml_parts.append("        <attvalues>")
        xml_parts.append(
            f'          <attvalue for="predicate" value="{_escape_xml(link.get("predicate", ""))}"/>'
        )
        xml_parts.append(
            f'          <attvalue for="confidence" value="{link.get("confidence", 0)}"/>'
        )
        xml_parts.append("        </attvalues>")
        xml_parts.append("      </edge>")

    xml_parts.append("    </edges>")
    xml_parts.append("  </graph>")
    xml_parts.append("</gexf>")

    return "\n".join(xml_parts)


def _escape_xml(text: str) -> str:
    """Escape XML special characters."""
    if not text:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


class ExportHandler(BaseHTTPRequestHandler):
    """HTTP handler for graph export API endpoints."""

    @handle_errors(log_traceback=True, reraise=False)
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path_parts = parsed.path.strip("/").split("/")
        params = parse_qs(parsed.query)
        db_name = params.get("db_name", [DB_NAME])[0]

        try:
            if len(path_parts) >= 3 and path_parts[0] == "api" and path_parts[1] == "export":
                format_type = path_parts[2]  # json, csv, graphml, gexf

                # Get optional filters
                entity_ids = params.get("entity_ids", [None])[0]
                if entity_ids:
                    entity_ids = entity_ids.split(",")

                community_id = params.get("community_id", [None])[0]

                # Export based on format
                if format_type == "json":
                    result = export_graph_json(db_name, entity_ids, community_id)
                    response_json = json.dumps(result, indent=2, default=str)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header(
                        "Content-Disposition", f'attachment; filename="graph_{db_name}.json"'
                    )
                    self.end_headers()
                    self.wfile.write(response_json.encode("utf-8"))

                elif format_type == "csv":
                    result = export_graph_csv(db_name, entity_ids, community_id)
                    self.send_response(200)
                    self.send_header("Content-Type", "text/csv")
                    self.send_header(
                        "Content-Disposition", f'attachment; filename="graph_{db_name}.csv"'
                    )
                    self.end_headers()
                    self.wfile.write(result.encode("utf-8"))

                elif format_type == "graphml":
                    result = export_graph_graphml(db_name, entity_ids, community_id)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/xml")
                    self.send_header(
                        "Content-Disposition", f'attachment; filename="graph_{db_name}.graphml"'
                    )
                    self.end_headers()
                    self.wfile.write(result.encode("utf-8"))

                elif format_type == "gexf":
                    result = export_graph_gexf(db_name, entity_ids, community_id)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/xml")
                    self.send_header(
                        "Content-Disposition", f'attachment; filename="graph_{db_name}.gexf"'
                    )
                    self.end_headers()
                    self.wfile.write(result.encode("utf-8"))
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
            logger.error(f"Error in export API: {e}")
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
    server = HTTPServer(("0.0.0.0", port), ExportHandler)
    logger.info(f"✅ Graph export API server started on http://0.0.0.0:{port}/api/export")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Graph export API server stopped")
        server.shutdown()
