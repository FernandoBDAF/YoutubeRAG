"""
Tests for GraphRAG pipeline resume from failure capability.

Tests Achievement 0.2: Resume from Failure
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from business.pipelines.graphrag import GraphRAGPipeline, STAGE_ORDER
from core.config.graphrag import GraphRAGPipelineConfig


class TestGraphRAGResume(unittest.TestCase):
    """Test resume from failure capability."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = GraphRAGPipelineConfig()
        # Mock database to avoid actual DB connection
        with patch("dependencies.database.mongodb.get_mongo_client") as mock_client:
            mock_collection = Mock()
            mock_db = MagicMock()
            # Configure mock_db to return mock_collection when indexed
            mock_db.__getitem__ = Mock(return_value=mock_collection)
            # Also support direct attribute access
            mock_db.chunks = mock_collection
            mock_client.return_value = {"mongo_hack": mock_db}
            self.pipeline = GraphRAGPipeline(self.config)
            # Patch the client's __getitem__ to return mock_db
            self.pipeline.client = MagicMock()
            self.pipeline.client.__getitem__ = Mock(return_value=mock_db)
            # Store mocks for use in tests
            self.mock_client = mock_client
            self.mock_db = mock_db
            self.mock_collection = mock_collection

    def test_detect_stage_completion_all_complete(self):
        """Test detecting when all stages are complete."""
        # Mock chunks collection with all stages completed
        self.mock_collection.count_documents.side_effect = [
            100,  # Total chunks
            100,  # Extraction completed
            100,  # Resolution completed
            100,  # Construction completed
            100,  # Detection completed
        ]

        completion = self.pipeline._detect_stage_completion()
        self.assertEqual(completion["graph_extraction"], 1.0)
        self.assertEqual(completion["entity_resolution"], 1.0)
        self.assertEqual(completion["graph_construction"], 1.0)
        self.assertEqual(completion["community_detection"], 1.0)

    def test_detect_stage_completion_partial(self):
        """Test detecting when some stages are complete."""
        # Mock chunks collection with only extraction and resolution completed
        self.mock_collection.count_documents.side_effect = [
            100,  # Total chunks
            100,  # Extraction completed
            100,  # Resolution completed
            0,  # Construction not completed
            0,  # Detection not completed
        ]

        completion = self.pipeline._detect_stage_completion()
        self.assertEqual(completion["graph_extraction"], 1.0)
        self.assertEqual(completion["entity_resolution"], 1.0)
        self.assertEqual(completion["graph_construction"], 0.0)
        self.assertEqual(completion["community_detection"], 0.0)

    def test_detect_stage_completion_none_complete(self):
        """Test detecting when no stages are complete."""
        # Mock chunks collection with no stages completed
        self.mock_collection.count_documents.side_effect = [
            100,  # Total chunks
            0,  # Extraction not completed
            0,  # Resolution not completed
            0,  # Construction not completed
            0,  # Detection not completed
        ]

        completion = self.pipeline._detect_stage_completion()
        self.assertEqual(completion["graph_extraction"], 0.0)
        self.assertEqual(completion["entity_resolution"], 0.0)
        self.assertEqual(completion["graph_construction"], 0.0)
        self.assertEqual(completion["community_detection"], 0.0)

    def test_get_last_completed_stage_all_complete(self):
        """Test getting last completed stage when all are complete."""
        completion = {
            "graph_extraction": 1.0,
            "entity_resolution": 1.0,
            "graph_construction": 1.0,
            "community_detection": 1.0,
        }
        last_completed = self.pipeline._get_last_completed_stage(completion)
        self.assertEqual(last_completed, "community_detection")

    def test_get_last_completed_stage_partial(self):
        """Test getting last completed stage when some are complete."""
        completion = {
            "graph_extraction": 1.0,
            "entity_resolution": 1.0,
            "graph_construction": 0.0,
            "community_detection": 0.0,
        }
        last_completed = self.pipeline._get_last_completed_stage(completion)
        self.assertEqual(last_completed, "entity_resolution")

    def test_get_last_completed_stage_none_complete(self):
        """Test getting last completed stage when none are complete."""
        completion = {
            "graph_extraction": 0.0,
            "entity_resolution": 0.0,
            "graph_construction": 0.0,
            "community_detection": 0.0,
        }
        last_completed = self.pipeline._get_last_completed_stage(completion)
        self.assertIsNone(last_completed)

    def test_get_stages_to_run_all_complete(self):
        """Test getting stages to run when all are complete."""
        completion = {
            "graph_extraction": 1.0,
            "entity_resolution": 1.0,
            "graph_construction": 1.0,
            "community_detection": 1.0,
        }
        stages_to_run = self.pipeline._get_stages_to_run(completion)
        self.assertEqual(stages_to_run, [])  # All complete, nothing to run

    def test_get_stages_to_run_partial(self):
        """Test getting stages to run when some are complete."""
        completion = {
            "graph_extraction": 1.0,
            "entity_resolution": 1.0,
            "graph_construction": 0.0,
            "community_detection": 0.0,
        }
        stages_to_run = self.pipeline._get_stages_to_run(completion)
        self.assertEqual(stages_to_run, ["graph_construction", "community_detection"])

    def test_get_stages_to_run_none_complete(self):
        """Test getting stages to run when none are complete."""
        completion = {
            "graph_extraction": 0.0,
            "entity_resolution": 0.0,
            "graph_construction": 0.0,
            "community_detection": 0.0,
        }
        stages_to_run = self.pipeline._get_stages_to_run(completion)
        self.assertEqual(
            stages_to_run,
            [
                "graph_extraction",
                "entity_resolution",
                "graph_construction",
                "community_detection",
            ],
        )

    def test_resume_skips_completed_stages(self):
        """Test that resume skips completed stages."""
        # Mock completion detection
        completion = {
            "graph_extraction": 1.0,
            "entity_resolution": 1.0,
            "graph_construction": 0.0,
            "community_detection": 0.0,
        }

        with patch.object(self.pipeline, "_detect_stage_completion", return_value=completion):
            with patch.object(self.pipeline, "run_stages") as mock_run_stages:
                result = self.pipeline.run_with_resume()
                # Should call run_stages with only incomplete stages
                mock_run_stages.assert_called_once_with("graph_construction,community_detection")

    def test_resume_all_complete(self):
        """Test resume when all stages are complete."""
        completion = {
            "graph_extraction": 1.0,
            "entity_resolution": 1.0,
            "graph_construction": 1.0,
            "community_detection": 1.0,
        }

        with patch.object(self.pipeline, "_detect_stage_completion", return_value=completion):
            result = self.pipeline.run_with_resume()
            # Should return 0 (success) but log that all stages are complete
            self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
