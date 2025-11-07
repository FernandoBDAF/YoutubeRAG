"""
Tests for GraphRAG pipeline stage selection and partial runs.

Tests Achievement 0.1: Stage Selection & Partial Runs
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from business.pipelines.graphrag import GraphRAGPipeline
from core.config.graphrag import GraphRAGPipelineConfig


class TestGraphRAGStageSelection(unittest.TestCase):
    """Test stage selection and partial pipeline runs."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = GraphRAGPipelineConfig()
        # Mock database to avoid actual DB connection
        with patch("dependencies.database.mongodb.get_mongo_client") as mock_client:
            mock_db = Mock()
            mock_client.return_value = {"mongo_hack": mock_db}
            self.pipeline = GraphRAGPipeline(self.config)

    def test_parse_stage_selection_by_name(self):
        """Test parsing stage selection by name."""
        # Test short names
        stages = self.pipeline._parse_stage_selection("extraction,resolution")
        self.assertEqual(stages, ["graph_extraction", "entity_resolution"])

        # Test full names
        stages = self.pipeline._parse_stage_selection("graph_extraction,entity_resolution")
        self.assertEqual(stages, ["graph_extraction", "entity_resolution"])

    def test_parse_stage_selection_by_range(self):
        """Test parsing stage selection by range."""
        stages = self.pipeline._parse_stage_selection("1-3")
        self.assertEqual(stages, ["graph_extraction", "entity_resolution", "graph_construction"])

        stages = self.pipeline._parse_stage_selection("2-4")
        self.assertEqual(stages, ["entity_resolution", "graph_construction", "community_detection"])

    def test_parse_stage_selection_by_indices(self):
        """Test parsing stage selection by individual indices."""
        stages = self.pipeline._parse_stage_selection("1,3,4")
        self.assertEqual(stages, ["graph_extraction", "graph_construction", "community_detection"])

    def test_parse_stage_selection_empty(self):
        """Test parsing empty stage selection (should return all stages)."""
        stages = self.pipeline._parse_stage_selection(None)
        self.assertEqual(stages, None)  # None means all stages

        stages = self.pipeline._parse_stage_selection("")
        self.assertEqual(stages, None)

    def test_get_stage_dependencies(self):
        """Test getting stage dependencies."""
        deps = self.pipeline._get_stage_dependencies("graph_extraction")
        self.assertEqual(deps, [])

        deps = self.pipeline._get_stage_dependencies("entity_resolution")
        self.assertEqual(deps, ["graph_extraction"])

        deps = self.pipeline._get_stage_dependencies("graph_construction")
        self.assertEqual(deps, ["graph_extraction", "entity_resolution"])

        deps = self.pipeline._get_stage_dependencies("community_detection")
        self.assertEqual(deps, ["graph_extraction", "entity_resolution", "graph_construction"])

    def test_validate_stage_dependencies_all_met(self):
        """Test dependency validation when all dependencies are met."""
        selected = ["graph_extraction", "entity_resolution"]
        missing = self.pipeline._validate_stage_dependencies(selected)
        self.assertEqual(missing, [])

    def test_validate_stage_dependencies_missing(self):
        """Test dependency validation when dependencies are missing."""
        selected = ["entity_resolution"]  # Missing graph_extraction
        missing = self.pipeline._validate_stage_dependencies(selected)
        self.assertEqual(missing, ["graph_extraction"])

        selected = ["graph_construction"]  # Missing extraction and resolution
        missing = self.pipeline._validate_stage_dependencies(selected)
        self.assertEqual(set(missing), {"graph_extraction", "entity_resolution"})

    def test_resolve_stage_selection_with_dependencies(self):
        """Test resolving stage selection with auto-included dependencies."""
        selected = ["entity_resolution"]
        resolved = self.pipeline._resolve_stage_selection(selected, auto_include_deps=True)
        self.assertIn("graph_extraction", resolved)
        self.assertIn("entity_resolution", resolved)
        # Should maintain order
        self.assertEqual(resolved[0], "graph_extraction")
        self.assertEqual(resolved[1], "entity_resolution")

    def test_resolve_stage_selection_without_dependencies(self):
        """Test resolving stage selection without auto-including dependencies."""
        selected = ["entity_resolution"]
        with self.assertRaises(ValueError) as cm:
            self.pipeline._resolve_stage_selection(selected, auto_include_deps=False)
        self.assertIn("missing dependencies", str(cm.exception).lower())

    def test_filter_stage_specs(self):
        """Test filtering stage specs based on selection."""
        selected = ["graph_extraction", "entity_resolution"]
        filtered = self.pipeline._filter_stage_specs(selected)
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0].stage, "graph_extraction")
        self.assertEqual(filtered[1].stage, "entity_resolution")

    def test_filter_stage_specs_maintains_order(self):
        """Test that filtering maintains stage order."""
        selected = ["community_detection", "graph_extraction"]  # Out of order
        filtered = self.pipeline._filter_stage_specs(selected)
        # Should maintain original pipeline order, not selection order
        self.assertEqual(filtered[0].stage, "graph_extraction")
        self.assertEqual(filtered[1].stage, "community_detection")

    def test_invalid_stage_name(self):
        """Test error handling for invalid stage names."""
        with self.assertRaises(ValueError) as cm:
            self.pipeline._parse_stage_selection("invalid_stage")
        self.assertIn("invalid", str(cm.exception).lower())

    def test_invalid_stage_range(self):
        """Test error handling for invalid stage ranges."""
        with self.assertRaises(ValueError) as cm:
            self.pipeline._parse_stage_selection("5-10")  # Out of range
        self.assertIn("invalid", str(cm.exception).lower())

    def test_run_stages_partial(self):
        """Test running partial pipeline with selected stages."""
        # Mock the runner to avoid actual execution
        with patch.object(self.pipeline.runner, "run", return_value=0):
            # Create a new pipeline instance with mocked runner
            with patch("dependencies.database.mongodb.get_mongo_client") as mock_client:
                mock_db = Mock()
                mock_client.return_value = {"mongo_hack": mock_db}
                pipeline = GraphRAGPipeline(self.config)

                # Mock the filtered runner
                with patch("business.pipelines.graphrag.PipelineRunner") as mock_runner_class:
                    mock_runner = Mock()
                    mock_runner.run.return_value = 0
                    mock_runner_class.return_value = mock_runner

                    result = pipeline.run_stages("extraction,resolution")
                    self.assertEqual(result, 0)
                    # Verify runner was created and run was called
                    mock_runner.run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
