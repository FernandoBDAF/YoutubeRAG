"""
Metrics HTTP Endpoint for Prometheus Scraping.

Simple HTTP server serving /metrics endpoint in Prometheus text format.
Part of the APP layer - external interface.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

logger = logging.getLogger(__name__)


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for /metrics endpoint."""

    @handle_errors(log_traceback=True, reraise=False)
    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/metrics":
            try:
                from core.libraries.metrics import export_prometheus_text

                metrics_text = export_prometheus_text()

                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(metrics_text.encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(f"Error: {e}".encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress default HTTP logging."""
        pass


@handle_errors(log_traceback=True, reraise=True)
def start_metrics_server(port: int = 9091, host: str = "0.0.0.0"):
    """Start HTTP server for Prometheus metrics scraping.

    Args:
        port: Port to listen on (default: 9091)
        host: Host to bind to (default: 0.0.0.0)

    Example:
        # Run in background thread
        import threading
        thread = threading.Thread(target=start_metrics_server, daemon=True)
        thread.start()

        # Prometheus can now scrape http://localhost:9091/metrics
    """
    server = HTTPServer((host, port), MetricsHandler)
    logger.info(f"Metrics server started on http://{host}:{port}/metrics")
    logger.info("Prometheus can now scrape this endpoint")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Metrics server stopped")
        server.shutdown()


if __name__ == "__main__":
    # Can run standalone for testing
    import sys

    sys.path.insert(
        0, "/Users/fernandobarroso/Local Repo/YoutubeRAG-mongohack/YoutubeRAG"
    )

    logging.basicConfig(level=logging.INFO)
    print("Starting metrics server on http://localhost:9091/metrics")
    print("Press Ctrl+C to stop")
    start_metrics_server()
