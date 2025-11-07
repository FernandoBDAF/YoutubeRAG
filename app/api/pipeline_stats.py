"""
Pipeline Stats API

Achievement 2.1: Stage Stats API

REST API endpoint for retrieving per-stage statistics from the GraphRAG pipeline.
Aggregates stats from all stages: extraction, entity resolution, graph construction, and community detection.
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
from core.config.graphrag import GraphRAGPipelineConfig
from business.stages.graphrag.extraction import GraphExtractionStage
from business.stages.graphrag.entity_resolution import EntityResolutionStage
from business.stages.graphrag.graph_construction import GraphConstructionStage
from business.stages.graphrag.community_detection import CommunityDetectionStage

logger = logging.getLogger(__name__)


def get_all_stage_stats(
    config: Optional[GraphRAGPipelineConfig] = None,
    db_name: Optional[str] = None,
    read_db_name: Optional[str] = None,
    write_db_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get statistics from all GraphRAG pipeline stages.

    Achievement 2.1: Stage Stats API

    Args:
        config: Optional GraphRAG pipeline config. If None, creates default config.
        db_name: Optional database name (for backward compatibility)
        read_db_name: Optional read database name
        write_db_name: Optional write database name

    Returns:
        Dictionary containing stats for all stages:
        {
            "graph_extraction": {...},
            "entity_resolution": {...},
            "graph_construction": {...},
            "community_detection": {...},
            "aggregate": {...}
        }
    """
    # Create default config if not provided
    if config is None:
        config = GraphRAGPipelineConfig()
        if db_name:
            config.extraction_config.db_name = db_name
        if read_db_name:
            config.extraction_config.read_db_name = read_db_name
        if write_db_name:
            config.extraction_config.write_db_name = write_db_name

    stats = {}

    try:
        # Stage 1: Graph Extraction
        extraction_stage = GraphExtractionStage(config.extraction_config)
        stats["graph_extraction"] = extraction_stage.get_processing_stats()
        stats["graph_extraction"]["stage_name"] = "graph_extraction"
        stats["graph_extraction"]["stage_display_name"] = "Graph Extraction"
    except Exception as e:
        logger.error(f"Error getting extraction stats: {e}")
        stats["graph_extraction"] = {"error": str(e)}

    try:
        # Stage 2: Entity Resolution
        resolution_stage = EntityResolutionStage(config.resolution_config)
        stats["entity_resolution"] = resolution_stage.get_resolution_stats()
        stats["entity_resolution"]["stage_name"] = "entity_resolution"
        stats["entity_resolution"]["stage_display_name"] = "Entity Resolution"
    except Exception as e:
        logger.error(f"Error getting resolution stats: {e}")
        stats["entity_resolution"] = {"error": str(e)}

    try:
        # Stage 3: Graph Construction
        construction_stage = GraphConstructionStage(config.construction_config)
        stats["graph_construction"] = construction_stage.get_construction_stats()
        stats["graph_construction"]["stage_name"] = "graph_construction"
        stats["graph_construction"]["stage_display_name"] = "Graph Construction"
    except Exception as e:
        logger.error(f"Error getting construction stats: {e}")
        stats["graph_construction"] = {"error": str(e)}

    try:
        # Stage 4: Community Detection
        detection_stage = CommunityDetectionStage(config.detection_config)
        stats["community_detection"] = detection_stage.get_detection_stats()
        stats["community_detection"]["stage_name"] = "community_detection"
        stats["community_detection"]["stage_display_name"] = "Community Detection"
    except Exception as e:
        logger.error(f"Error getting detection stats: {e}")
        stats["community_detection"] = {"error": str(e)}

    # Calculate aggregate statistics
    try:
        extraction = stats.get("graph_extraction", {})
        resolution = stats.get("entity_resolution", {})
        construction = stats.get("graph_construction", {})
        detection = stats.get("community_detection", {})

        stats["aggregate"] = {
            "total_chunks": extraction.get("total_chunks", 0),
            "total_entities": resolution.get("total_entities", 0),
            "total_relationships": construction.get("total_relationships", 0),
            "total_communities": detection.get("total_communities", 0),
            "stages_completed": sum(
                1
                for stage_stats in [extraction, resolution, construction, detection]
                if stage_stats.get("completion_rate", 0) >= 0.95
            ),
            "overall_completion_rate": (
                (
                    extraction.get("completion_rate", 0)
                    + resolution.get("completion_rate", 0)
                    + construction.get("completion_rate", 0)
                    + detection.get("completion_rate", 0)
                )
                / 4
                if any(
                    [
                        extraction.get("completion_rate", 0),
                        resolution.get("completion_rate", 0),
                        construction.get("completion_rate", 0),
                        detection.get("completion_rate", 0),
                    ]
                )
                else 0
            ),
        }
    except Exception as e:
        logger.error(f"Error calculating aggregate stats: {e}")
        stats["aggregate"] = {"error": str(e)}

    return stats


class PipelineStatsHandler(BaseHTTPRequestHandler):
    """HTTP handler for /api/pipeline/stats endpoint."""

    @handle_errors(log_traceback=True, reraise=False)
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        if parsed.path != "/api/pipeline/stats":
            self.send_response(404)
            self.end_headers()
            return

        # Parse query parameters
        params = parse_qs(parsed.query)
        db_name = params.get("db_name", [None])[0]
        read_db_name = params.get("read_db_name", [None])[0]
        write_db_name = params.get("write_db_name", [None])[0]

        try:
            stats = get_all_stage_stats(
                db_name=db_name,
                read_db_name=read_db_name,
                write_db_name=write_db_name,
            )

            response_json = json.dumps(stats, indent=2, default=str)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response_json.encode("utf-8"))
        except Exception as e:
            logger.error(f"Error in stats endpoint: {e}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            error_response = json.dumps({"error": str(e)})
            self.wfile.write(error_response.encode("utf-8"))

    def log_message(self, format, *args):
        """Suppress default HTTP logging."""
        pass


def start_stats_server(port: int = 8000, host: str = "0.0.0.0") -> None:
    """
    Start HTTP server for pipeline stats API.

    Achievement 2.1: Stage Stats API

    Args:
        port: Port to listen on (default: 8000)
        host: Host to bind to (default: 0.0.0.0)

    Example:
        # Run in background thread
        import threading
        from app.api.pipeline_stats import start_stats_server

        thread = threading.Thread(target=start_stats_server, daemon=True)
        thread.start()

        # API available at: http://localhost:8000/api/pipeline/stats
    """
    from http.server import HTTPServer

    server = HTTPServer((host, port), PipelineStatsHandler)
    logger.info(f"✅ Pipeline stats server started on http://{host}:{port}/api/pipeline/stats")
    logger.info("📊 Stage statistics available via REST API")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stats server stopped")
        server.shutdown()


if __name__ == "__main__":
    # Can run standalone for testing
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    start_stats_server(port=port)


