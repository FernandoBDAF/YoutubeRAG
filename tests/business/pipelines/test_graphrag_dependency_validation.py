"""
Tests for GraphRAG pipeline dependency validation.

Tests Achievement 0.3: Stage Dependency Validation
"""
import unittest
from unittest.mock import Mock, patch
import logging
from business.pipelines.graphrag import GraphRAGPipeline
from core.config.graphrag import GraphRAGPipelineConfig


class TestGraphRAGDependencyValidation(unittest.TestCase):
    """Test dependency validation and out-of-order warnings."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = GraphRAGPipelineConfig()
        # Mock database to avoid actual DB connection
        with patch("dependencies.database.mongodb.get_mongo_client") as mock_client:
            mock_db = Mock()
            mock_client.return_value = {"mongo_hack": mock_db}
            self.pipeline = GraphRAGPipeline(self.config)

    def test_warn_out_of_order_single_stage(self):
        """Test that single stage doesn't trigger out-of-order warning."""
        # Should not raise or log anything
        try:
            self.pipeline._warn_out_of_order(["graph_extraction"])
        except Exception as e:
            self.fail(f"_warn_out_of_order raised {e} unexpectedly")

    def test_warn_out_of_order_sequential(self):
        """Test that sequential stages don't trigger warning."""
        # Should not raise or log anything
        try:
            self.pipeline._warn_out_of_order(
                ["graph_extraction", "entity_resolution", "graph_construction"]
            )
        except Exception as e:
            self.fail(f"_warn_out_of_order raised {e} unexpectedly")

    def test_warn_out_of_order_reversed(self):
        """Test that reversed order triggers warning."""
        with self.assertLogs(logger="business.pipelines.graphrag", level=logging.WARNING) as log:
            self.pipeline._warn_out_of_order(
                ["community_detection", "graph_extraction"]
            )
        # Should log warning
        self.assertGreater(len(log.records), 0)
        self.assertIn("out of order", log.records[0].message.lower())

    def test_warn_out_of_order_mixed(self):
        """Test that mixed order triggers warning."""
        with self.assertLogs(logger="business.pipelines.graphrag", level=logging.WARNING) as log:
            self.pipeline._warn_out_of_order(
                ["graph_construction", "graph_extraction", "entity_resolution"]
            )
        # Should log warning
        self.assertGreater(len(log.records), 0)
        self.assertIn("out of order", log.records[0].message.lower())

    def test_resolve_stage_selection_warns_out_of_order(self):
        """Test that resolve_stage_selection warns about out-of-order selection."""
        with self.assertLogs(logger="business.pipelines.graphrag", level=logging.WARNING) as log:
            resolved = self.pipeline._resolve_stage_selection(
                ["community_detection", "graph_extraction"], auto_include_deps=True
            )
        # Should log warning
        self.assertGreater(len(log.records), 0)
        # Should still resolve correctly
        self.assertIn("graph_extraction", resolved)
        self.assertIn("community_detection", resolved)
        # Should maintain correct order
        self.assertEqual(resolved[0], "graph_extraction")

    def test_resolve_stage_selection_logs_auto_include(self):
        """Test that resolve_stage_selection logs auto-included dependencies."""
        with self.assertLogs(logger="business.pipelines.graphrag", level=logging.INFO) as log:
            resolved = self.pipeline._resolve_stage_selection(
                ["entity_resolution"], auto_include_deps=True
            )
        # Should log auto-inclusion
        info_messages = [r.message for r in log.records if r.levelno == logging.INFO]
        auto_include_logged = any("auto-including" in msg.lower() for msg in info_messages)
        self.assertTrue(auto_include_logged, "Should log auto-inclusion of dependencies")
        # Should include dependency
        self.assertIn("graph_extraction", resolved)
        self.assertIn("entity_resolution", resolved)

    def test_resolve_stage_selection_error_on_missing_deps(self):
        """Test that resolve_stage_selection raises error when dependencies missing and auto_include_deps=False."""
        with self.assertRaises(ValueError) as cm:
            self.pipeline._resolve_stage_selection(
                ["entity_resolution"], auto_include_deps=False
            )
        self.assertIn("missing dependencies", str(cm.exception).lower())
        self.assertIn("graph_extraction", str(cm.exception))

    def test_resolve_stage_selection_no_error_with_auto_include(self):
        """Test that resolve_stage_selection doesn't error when auto_include_deps=True."""
        # Should not raise
        resolved = self.pipeline._resolve_stage_selection(
            ["entity_resolution"], auto_include_deps=True
        )
        self.assertIn("graph_extraction", resolved)
        self.assertIn("entity_resolution", resolved)

    def test_resolve_stage_selection_maintains_order(self):
        """Test that resolved stages maintain correct pipeline order."""
        # Select out of order
        resolved = self.pipeline._resolve_stage_selection(
            ["community_detection", "graph_extraction"], auto_include_deps=True
        )
        # Should be in correct order
        self.assertEqual(resolved[0], "graph_extraction")
        self.assertEqual(resolved[-1], "community_detection")

    def test_resolve_stage_selection_all_stages(self):
        """Test resolving all stages (None selection)."""
        resolved = self.pipeline._resolve_stage_selection(None, auto_include_deps=True)
        # Should return all stages in order
        self.assertEqual(len(resolved), 4)
        self.assertEqual(resolved[0], "graph_extraction")
        self.assertEqual(resolved[1], "entity_resolution")
        self.assertEqual(resolved[2], "graph_construction")
        self.assertEqual(resolved[3], "community_detection")


if __name__ == "__main__":
    unittest.main()

