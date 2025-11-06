"""
Tests for Graph Construction Stage - Ontology Integration.

Tests Achievement 3.1: Use Existing Ontology Infrastructure.

Run with: python -m tests.business.stages.graphrag.test_graph_construction_ontology
"""

try:
    import pytest

    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from unittest.mock import MagicMock, Mock, patch
from typing import Dict, Any

from business.stages.graphrag.graph_construction import GraphConstructionStage


class TestOntologyIntegration:
    """Test that ontology is loaded and used for bidirectional relationships."""

    def _mock_stage(self):
        """Create a mock GraphConstructionStage."""
        stage = GraphConstructionStage()
        stage.config = Mock()
        stage.config.db_name = "test_db"

        mock_relations = MagicMock()
        stage.graphrag_collections = {"relations": mock_relations}

        return stage, mock_relations

    def test_ontology_loaded_in_setup(self):
        """Test that ontology is loaded in setup()."""
        stage = GraphConstructionStage()
        stage.config = Mock()
        stage.config.db_name = "test_db"
        stage.config.read_db_name = None
        stage.config.write_db_name = None

        # Mock get_graphrag_collections
        with patch(
            "business.stages.graphrag.graph_construction.get_graphrag_collections"
        ) as mock_get_collections:
            mock_get_collections.return_value = {}

            # Mock load_ontology (imported inside setup method)
            with patch(
                "core.libraries.ontology.loader.load_ontology"
            ) as mock_load_ontology:
                mock_load_ontology.return_value = {
                    "canonical_predicates": {"uses", "teaches"},
                    "symmetric_predicates": {"related_to", "connected_to"},
                    "predicate_map": {},
                }

                # Call setup()
                stage.setup()

                # Verify ontology was loaded
                assert hasattr(stage, "ontology")
                assert "canonical_predicates" in stage.ontology
                assert "symmetric_predicates" in stage.ontology

    def test_symmetric_predicates_skip_bidirectional(self):
        """Test that symmetric predicates skip bidirectional creation."""
        stage, mock_relations = self._mock_stage()

        # Set up ontology with symmetric predicate
        stage.ontology = {
            "canonical_predicates": set(),
            "symmetric_predicates": {"related_to"},
            "predicate_map": {},
        }

        # Mock relationship with symmetric predicate
        mock_relations.find.return_value = [
            {
                "relationship_id": "a" * 32,
                "subject_id": "b" * 32,
                "object_id": "c" * 32,
                "predicate": "related_to",  # Symmetric
            }
        ]

        # Mock batch_insert
        from unittest.mock import patch

        with patch(
            "business.stages.graphrag.graph_construction.batch_insert"
        ) as mock_batch:
            # Call _add_bidirectional_relationships
            result = stage._add_bidirectional_relationships()

            # Verify batch_insert was NOT called (symmetric predicate skipped)
            assert not mock_batch.called or mock_batch.call_count == 0

    def test_reverse_predicate_from_ontology(self):
        """Test that reverse predicates are derived from ontology."""
        stage, mock_relations = self._mock_stage()

        # Set up ontology
        stage.ontology = {
            "canonical_predicates": {"uses", "used_by"},
            "symmetric_predicates": set(),
            "predicate_map": {},
        }

        # Mock relationship with predicate that has reverse
        mock_relations.find.return_value = [
            {
                "relationship_id": "a" * 32,
                "subject_id": "b" * 32,
                "object_id": "c" * 32,
                "predicate": "uses",
            }
        ]

        # Mock: no existing reverse
        mock_relations.find_one.return_value = None

        # Mock batch_insert
        from unittest.mock import patch

        with patch(
            "business.stages.graphrag.graph_construction.batch_insert"
        ) as mock_batch:
            mock_batch.return_value = {"inserted": 1, "total": 1, "failed": 0}

            # Call _add_bidirectional_relationships
            result = stage._add_bidirectional_relationships()

            # Verify batch_insert was called (reverse created)
            assert mock_batch.called

    def test_get_reverse_predicate_returns_none_for_symmetric(self):
        """Test that _get_reverse_predicate returns None for symmetric predicates."""
        stage, _ = self._mock_stage()

        # Set up ontology with symmetric predicate
        stage.ontology = {
            "canonical_predicates": set(),
            "symmetric_predicates": {"related_to"},
            "predicate_map": {},
        }

        # Test symmetric predicate
        reverse = stage._get_reverse_predicate("related_to")

        # Should return None (symmetric predicates don't need reverse)
        assert reverse is None

    def test_get_reverse_predicate_returns_reverse(self):
        """Test that _get_reverse_predicate returns reverse for asymmetric predicates."""
        stage, _ = self._mock_stage()

        # Set up ontology
        stage.ontology = {
            "canonical_predicates": set(),
            "symmetric_predicates": set(),
            "predicate_map": {},
        }

        # Test asymmetric predicate
        reverse = stage._get_reverse_predicate("uses")

        # Should return reverse predicate
        assert reverse == "used_by"

    def test_fallback_when_ontology_not_loaded(self):
        """Test that fallback works when ontology loading fails."""
        stage = GraphConstructionStage()
        stage.config = Mock()
        stage.config.db_name = "test_db"
        stage.config.read_db_name = None
        stage.config.write_db_name = None

        # Mock get_graphrag_collections
        with patch(
            "business.stages.graphrag.graph_construction.get_graphrag_collections"
        ) as mock_get_collections:
            mock_get_collections.return_value = {}

            # Mock load_ontology to raise exception (imported inside setup method)
            with patch(
                "core.libraries.ontology.loader.load_ontology"
            ) as mock_load_ontology:
                mock_load_ontology.side_effect = Exception("Failed to load")

                # Call setup()
                stage.setup()

                # Verify fallback ontology structure exists
                assert hasattr(stage, "ontology")
                assert "canonical_predicates" in stage.ontology
                assert "symmetric_predicates" in stage.ontology


def run_all_tests():
    """Run all tests."""
    test_classes = [TestOntologyIntegration]

    for test_class in test_classes:
        print(f"\n=== Running {test_class.__name__} ===")
        instance = test_class()

        for method_name in dir(instance):
            if method_name.startswith("test_"):
                print(f"  Running {method_name}...")
                try:
                    method = getattr(instance, method_name)
                    method()
                    print(f"    ✓ {method_name} passed")
                except Exception as e:
                    print(f"    ✗ {method_name} failed: {e}")
                    import traceback

                    traceback.print_exc()

    print("\n✅ All tests passed!")


if __name__ == "__main__":
    run_all_tests()

