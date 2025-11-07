"""
Real-Time Pipeline Progress Monitoring

Achievement 1.3: Real-Time Progress Monitoring

WebSocket endpoint for streaming pipeline progress updates.
"""

import json
import logging
import threading
import time
from typing import Dict, Any, Optional, Set
from queue import Queue, Empty

try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs
except ImportError:
    HTTPServer = None
    BaseHTTPRequestHandler = None

logger = logging.getLogger(__name__)

# Global progress store (in-memory, per pipeline_id)
_progress_store: Dict[str, Dict[str, Any]] = {}
_progress_subscribers: Dict[str, Set[Queue]] = {}  # pipeline_id -> set of queues
_lock = threading.Lock()


class ProgressUpdate:
    """Progress update message."""

    def __init__(
        self,
        pipeline_id: str,
        stage: Optional[str] = None,
        status: Optional[str] = None,
        progress: Optional[float] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
    ):
        self.pipeline_id = pipeline_id
        self.stage = stage
        self.status = status
        self.progress = progress
        self.message = message
        self.error = error
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "pipeline_id": self.pipeline_id,
            "stage": self.stage,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "error": self.error,
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


def update_progress(
    pipeline_id: str,
    stage: Optional[str] = None,
    status: Optional[str] = None,
    progress: Optional[float] = None,
    message: Optional[str] = None,
    error: Optional[str] = None,
) -> None:
    """
    Update pipeline progress and notify subscribers.

    Achievement 1.3: Real-Time Progress Monitoring

    Args:
        pipeline_id: Unique pipeline identifier
        stage: Current stage name
        status: Pipeline status (running, completed, failed)
        progress: Progress percentage (0.0-1.0)
        message: Status message
        error: Error message if any
    """
    with _lock:
        # Update progress store
        if pipeline_id not in _progress_store:
            _progress_store[pipeline_id] = {}

        _progress_store[pipeline_id].update(
            {
                "stage": stage,
                "status": status,
                "progress": progress,
                "message": message,
                "error": error,
                "last_updated": time.time(),
            }
        )

        # Notify subscribers
        if pipeline_id in _progress_subscribers:
            update = ProgressUpdate(
                pipeline_id=pipeline_id,
                stage=stage,
                status=status,
                progress=progress,
                message=message,
                error=error,
            )

            # Send to all subscribers
            dead_queues = set()
            for queue in _progress_subscribers[pipeline_id]:
                try:
                    queue.put_nowait(update)
                except Exception as e:
                    logger.warning(f"Failed to send progress update: {e}")
                    dead_queues.add(queue)

            # Remove dead queues
            _progress_subscribers[pipeline_id] -= dead_queues


def get_progress(pipeline_id: str) -> Optional[Dict[str, Any]]:
    """
    Get current progress for a pipeline.

    Args:
        pipeline_id: Unique pipeline identifier

    Returns:
        Progress dictionary or None if not found
    """
    with _lock:
        return _progress_store.get(pipeline_id, {}).copy()


def subscribe_progress(pipeline_id: str) -> Queue:
    """
    Subscribe to progress updates for a pipeline.

    Args:
        pipeline_id: Unique pipeline identifier

    Returns:
        Queue that will receive ProgressUpdate objects
    """
    queue = Queue(maxsize=100)  # Limit queue size

    with _lock:
        if pipeline_id not in _progress_subscribers:
            _progress_subscribers[pipeline_id] = set()
        _progress_subscribers[pipeline_id].add(queue)

    return queue


def unsubscribe_progress(pipeline_id: str, queue: Queue) -> None:
    """
    Unsubscribe from progress updates.

    Args:
        pipeline_id: Unique pipeline identifier
        queue: Queue to remove
    """
    with _lock:
        if pipeline_id in _progress_subscribers:
            _progress_subscribers[pipeline_id].discard(queue)


class ProgressSSEHandler(BaseHTTPRequestHandler):
    """Server-Sent Events handler for progress streaming."""

    def do_GET(self):
        """Handle GET requests for SSE progress stream."""
        parsed = urlparse(self.path)
        if parsed.path != "/api/pipeline/progress":
            self.send_response(404)
            self.end_headers()
            return

        # Parse query parameters
        params = parse_qs(parsed.query)
        pipeline_id = params.get("pipeline_id", ["default"])[0]

        # Set up SSE headers
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        # Subscribe to progress updates
        queue = subscribe_progress(pipeline_id)

        try:
            # Send initial progress
            current = get_progress(pipeline_id)
            if current:
                self._send_sse("progress", json.dumps(current))

            # Stream updates
            while True:
                try:
                    update = queue.get(timeout=30)  # 30s timeout
                    self._send_sse("progress", update.to_json())
                except Empty:
                    # Send heartbeat
                    self._send_sse("heartbeat", json.dumps({"timestamp": time.time()}))
        except Exception as e:
            logger.error(f"Error in SSE stream: {e}")
        finally:
            unsubscribe_progress(pipeline_id, queue)

    def _send_sse(self, event: str, data: str) -> None:
        """Send Server-Sent Event."""
        try:
            self.wfile.write(f"event: {event}\n".encode())
            self.wfile.write(f"data: {data}\n\n".encode())
            self.wfile.flush()
        except Exception as e:
            logger.error(f"Failed to send SSE: {e}")
            raise

    def log_message(self, format, *args):
        """Suppress default HTTP logging."""
        pass


def start_progress_server(port: int = 8000, host: str = "0.0.0.0") -> None:
    """
    Start HTTP server for progress streaming (SSE).

    Achievement 1.3: Real-Time Progress Monitoring

    Args:
        port: Port to listen on (default: 8000)
        host: Host to bind to (default: 0.0.0.0)

    Example:
        # Run in background thread
        import threading
        from app.api.pipeline_progress import start_progress_server

        thread = threading.Thread(target=start_progress_server, daemon=True)
        thread.start()

        # Clients can connect to: http://localhost:8000/api/pipeline/progress?pipeline_id=default
    """
    if HTTPServer is None:
        logger.error("HTTP server not available")
        return

    server = HTTPServer((host, port), ProgressSSEHandler)
    logger.info(f"✅ Progress server started on http://{host}:{port}/api/pipeline/progress")
    logger.info("📡 Clients can subscribe to progress updates via SSE")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Progress server stopped")
        server.shutdown()


if __name__ == "__main__":
    # Can run standalone for testing
    import sys

    sys.path.insert(0, "/Users/fernandobarroso/Local Repo/YoutubeRAG-mongohack/YoutubeRAG")

    logging.basicConfig(level=logging.INFO)
    print("Starting progress server on http://localhost:8000/api/pipeline/progress")
    print("Press Ctrl+C to stop")
    start_progress_server()



