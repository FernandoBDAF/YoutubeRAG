"""
Stages API HTTP Server

Simple HTTP server for testing the Stages API.
For production, integrate with existing API infrastructure.

Usage:
    python -m app.stages_api.server --port 8080
"""

# IMPORTANT: Load .env BEFORE any other imports that might use environment variables
import os

try:
    from dotenv import load_dotenv
    # Try multiple paths to find .env
    possible_paths = [
        os.path.join(os.path.dirname(__file__), '..', '..', '.env'),  # relative to this file
        os.path.join(os.getcwd(), '.env'),  # current working directory
        '.env',  # direct
    ]
    for env_path in possible_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path, override=True)
            print(f"✓ Loaded environment from: {os.path.abspath(env_path)}")
            break
    else:
        print("⚠ No .env file found")
except ImportError:
    print("⚠ python-dotenv not installed, using shell environment")

# Now import everything else
import argparse
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

from .api import handle_request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StagesAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Stages API"""

    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path.replace("/api/v1/", "").replace("/api/", "")

        result, status = handle_request("GET", path)
        self._send_json(result, status)

    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        path = parsed.path.replace("/api/v1/", "").replace("/api/", "")

        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = None
        if content_length > 0:
            body_bytes = self.rfile.read(content_length)
            try:
                body = json.loads(body_bytes.decode("utf-8"))
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON body"}, 400)
                return

        result, status = handle_request("POST", path, body)
        self._send_json(result, status)

    def do_HEAD(self):
        """Handle HEAD requests (same as GET but no body)"""
        parsed = urlparse(self.path)
        path = parsed.path.replace("/api/v1/", "").replace("/api/", "")

        result, status = handle_request("GET", path)
        self._send_headers(status, len(json.dumps(result, indent=2).encode()))

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self._add_cors_headers()
        self.end_headers()

    def _send_headers(self, status=200, content_length=0):
        """Send response headers only (for HEAD requests)"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(content_length))
        self._add_cors_headers()
        self.end_headers()

    def _send_json(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self._add_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def _add_cors_headers(self):
        """Add CORS headers for browser access"""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, format, *args):
        """Custom logging"""
        logger.info(f"{self.address_string()} - {format % args}")


def run_server(host: str = "0.0.0.0", port: int = 8080):
    """Run the HTTP server"""
    server = HTTPServer((host, port), StagesAPIHandler)
    logger.info(f"Stages API server running on http://{host}:{port}")
    logger.info("Endpoints:")
    logger.info("  GET  /api/v1/stages")
    logger.info("  GET  /api/v1/stages/{pipeline}")
    logger.info("  GET  /api/v1/stages/{stage_name}/config")
    logger.info("  GET  /api/v1/stages/{stage_name}/defaults")
    logger.info("  POST /api/v1/stages/{stage_name}/validate")
    logger.info("  POST /api/v1/pipelines/validate")
    logger.info("  POST /api/v1/pipelines/execute")
    logger.info("  GET  /api/v1/pipelines/{pipeline_id}/status")
    logger.info("  POST /api/v1/pipelines/{pipeline_id}/cancel")
    logger.info("  GET  /api/v1/pipelines/active")
    logger.info("  GET  /api/v1/pipelines/history")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stages API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    args = parser.parse_args()

    run_server(args.host, args.port)

