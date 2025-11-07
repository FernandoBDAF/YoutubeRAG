"""
Tests for Pipeline Control API

Achievement 8.1: Comprehensive Test Suite

Tests for app/api/pipeline_control.py endpoints.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import json
import time
from datetime import datetime

from app.api.pipeline_control import (
    get_pipeline_status,
    start_pipeline,
    cancel_pipeline,
    get_pipeline_history,
    PipelineControlHandler,
)


class TestPipelineControlAPI(unittest.TestCase):
    """Test pipeline control API functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.db_name = "test_db"
        self.pipeline_id = "test_pipeline_123"

    @patch("app.api.pipeline_control.get_mongo_client")
    def test_get_pipeline_status_not_found(self, mock_get_client):
        """Test getting status for non-existent pipeline."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_db = MagicMock()
        mock_client.__getitem__ = Mock(return_value=mock_db)
        mock_db.experiment_tracking = MagicMock()
        mock_db.experiment_tracking.find_one.return_value = None

        status = get_pipeline_status(self.pipeline_id, self.db_name)
        self.assertIsNone(status)

    @patch("app.api.pipeline_control.get_mongo_client")
    def test_get_pipeline_history(self, mock_get_client):
        """Test getting pipeline history."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_db = MagicMock()
        mock_client.__getitem__ = Mock(return_value=mock_db)
        mock_coll = MagicMock()
        mock_db.experiment_tracking = mock_coll

        # Mock history documents
        mock_docs = [
            {
                "experiment_id": "pipeline_1",
                "status": "completed",
                "started_at": datetime.utcnow(),
                "completed_at": datetime.utcnow(),
                "exit_code": 0,
            },
            {
                "experiment_id": "pipeline_2",
                "status": "failed",
                "started_at": datetime.utcnow(),
                "completed_at": datetime.utcnow(),
                "exit_code": 1,
            },
        ]
        mock_coll.count_documents.return_value = 2
        mock_coll.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_docs

        history = get_pipeline_history(db_name=self.db_name, limit=10, offset=0)
        self.assertEqual(history["total"], 2)
        self.assertEqual(len(history["pipelines"]), 2)
        self.assertEqual(history["pipelines"][0]["status"], "completed")

    def test_cancel_pipeline_not_found(self):
        """Test canceling non-existent pipeline."""
        result = cancel_pipeline("nonexistent_pipeline")
        self.assertIn("error", result)
        self.assertEqual(result["status"], "Pipeline not found" or "Pipeline not found")

    @patch("app.api.pipeline_control._active_pipelines", {})
    @patch("app.api.pipeline_control._pipeline_lock")
    def test_cancel_pipeline_success(self, mock_lock):
        """Test successfully canceling a pipeline."""
        from app.api.pipeline_control import _active_pipelines, _pipeline_lock

        # Add a running pipeline
        _active_pipelines[self.pipeline_id] = {
            "pipeline_id": self.pipeline_id,
            "status": "running",
            "started_at": datetime.utcnow().isoformat(),
        }

        result = cancel_pipeline(self.pipeline_id)
        self.assertEqual(result["status"], "cancelled")
        self.assertEqual(_active_pipelines[self.pipeline_id]["status"], "cancelled")


class TestPipelineControlHandler(unittest.TestCase):
    """Test PipelineControlHandler HTTP handler."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = PipelineControlHandler(Mock(), ("127.0.0.1", 8000), None)

    def test_do_get_status_missing_pipeline_id(self):
        """Test GET /api/pipeline/status without pipeline_id."""
        self.handler.path = "/api/pipeline/status"
        self.handler.send_response = Mock()
        self.handler.send_header = Mock()
        self.handler.end_headers = Mock()
        self.handler.wfile = Mock()

        self.handler.do_GET()
        self.handler.send_response.assert_called_with(400)

    @patch("app.api.pipeline_control.get_pipeline_status")
    def test_do_get_status_success(self, mock_get_status):
        """Test GET /api/pipeline/status with valid pipeline_id."""
        mock_status = {
            "pipeline_id": "test_123",
            "status": "running",
            "started_at": datetime.utcnow().isoformat(),
        }
        mock_get_status.return_value = mock_status

        self.handler.path = "/api/pipeline/status?pipeline_id=test_123"
        self.handler.send_response = Mock()
        self.handler.send_header = Mock()
        self.handler.end_headers = Mock()
        self.handler.wfile = Mock()

        self.handler.do_GET()
        self.handler.send_response.assert_called_with(200)
        self.handler.wfile.write.assert_called_once()


def run_all_tests():
    """Run all pipeline control API tests."""
    print("Testing Pipeline Control API")
    print("=" * 60)
    print()

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestPipelineControlAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestPipelineControlHandler))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 60)
    if result.wasSuccessful():
        print("✅ All pipeline control API tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
    print("=" * 60)

    return result.wasSuccessful()


if __name__ == "__main__":
    run_all_tests()

