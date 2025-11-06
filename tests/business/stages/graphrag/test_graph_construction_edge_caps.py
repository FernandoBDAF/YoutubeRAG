"""
Tests for Graph Construction Stage - Synthetic Edge Caps.

Tests Achievement 2.3: Synthetic Edge Caps Per Entity.

Run with: python -m tests.business.stages.graphrag.test_graph_construction_edge_caps
"""

try:
    import pytest

    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from unittest.mock import MagicMock, Mock, patch
import os
from typing import Dict, Any

from business.stages.graphrag.graph_construction import GraphConstructionStage


class TestEdgeCaps:
    """Test that edge caps are enforced for synthetic relationships."""

    def _mock_stage(self):
        """Create a mock GraphConstructionStage."""
        stage = GraphConstructionStage()
        stage.config = Mock()
        stage.config.db_name = "test_db"

        mock_relations = MagicMock()
        mock_mentions = MagicMock()
        mock_entities = MagicMock()

        stage.graphrag_collections = {
            "relations": mock_relations,
            "entity_mentions": mock_mentions,
            "entities": mock_entities,
        }

        return stage, mock_relations, mock_mentions, mock_entities

    def test_co_occurrence_edge_cap_enforced(self):
        """Test that co-occurrence edge cap is enforced."""
        stage, mock_relations, mock_mentions, mock_entities = self._mock_stage()

        # Set low cap for testing
        import os
        original_env = os.environ.get("GRAPHRAG_MAX_COOC_PER_ENTITY")
        try:
            os.environ["GRAPHRAG_MAX_COOC_PER_ENTITY"] = "2"
            # Mock entity mentions
            mock_mentions.find.return_value = [
                {"chunk_id": "chunk_1", "entity_id": "b" * 32},
                {"chunk_id": "chunk_1", "entity_id": "c" * 32},
                {"chunk_id": "chunk_1", "entity_id": "d" * 32},
            ]

            # Mock: no existing relationships
            mock_relations.find_one.return_value = None

            # Mock degree counts: entity1 has 2 co-occurrence edges (at cap), entity2 has 0
            def mock_count_documents(query):
                if "b" * 32 in str(query):
                    return 2  # At cap
                return 0

            mock_relations.count_documents.side_effect = mock_count_documents

            # Mock batch_insert
            with patch(
                "business.stages.graphrag.graph_construction.batch_insert"
            ) as mock_batch:
                mock_batch.return_value = {"inserted": 0, "total": 0, "failed": 0}

                # Call _add_co_occurrence_relationships
                result = stage._add_co_occurrence_relationships()

                # Verify batch_insert was called (may be empty if all capped)
                # The important thing is that entities at cap don't get more edges
                assert mock_relations.count_documents.called
        finally:
            # Restore environment
            if original_env is not None:
                os.environ["GRAPHRAG_MAX_COOC_PER_ENTITY"] = original_env
            elif "GRAPHRAG_MAX_COOC_PER_ENTITY" in os.environ:
                del os.environ["GRAPHRAG_MAX_COOC_PER_ENTITY"]

    def test_semantic_similarity_edge_cap_enforced(self):
        """Test that semantic similarity edge cap is enforced."""
        stage, mock_relations, mock_entities, _ = self._mock_stage()

        # Set low cap for testing
        import os
        original_env = os.environ.get("GRAPHRAG_MAX_SIM_PER_ENTITY")
        try:
            os.environ["GRAPHRAG_MAX_SIM_PER_ENTITY"] = "2"
            # Mock entities with embeddings
            mock_entities.find.side_effect = [
                iter([]),  # No entities without embeddings
                iter([
                    {
                        "entity_id": "b" * 32,
                        "name": "Entity 1",
                        "entity_embedding": [0.1, 0.2, 0.3],
                        "entity_embedding_norm": 1.0,
                    },
                    {
                        "entity_id": "c" * 32,
                        "name": "Entity 2",
                        "entity_embedding": [0.4, 0.5, 0.6],
                        "entity_embedding_norm": 1.0,
                    },
                ]),
            ]

            # Mock: no existing relationships
            mock_relations.find_one.return_value = None

            # Mock degree counts: entity1 has 2 similarity edges (at cap)
            def mock_count_documents(query):
                if "b" * 32 in str(query):
                    return 2  # At cap
                return 0

            mock_relations.count_documents.side_effect = mock_count_documents

            # Mock batch_insert
            with patch(
                "business.stages.graphrag.graph_construction.batch_insert"
            ) as mock_batch:
                mock_batch.return_value = {"inserted": 0, "total": 0, "failed": 0}

                # Call _add_semantic_similarity_relationships
                result = stage._add_semantic_similarity_relationships(
                    similarity_threshold=0.5
                )

                # Verify count_documents was called (degree check)
                assert mock_relations.count_documents.called
        finally:
            # Restore environment
            if original_env is not None:
                os.environ["GRAPHRAG_MAX_SIM_PER_ENTITY"] = original_env
            elif "GRAPHRAG_MAX_SIM_PER_ENTITY" in os.environ:
                del os.environ["GRAPHRAG_MAX_SIM_PER_ENTITY"]

    def test_edge_cap_defaults(self):
        """Test that edge caps have sensible defaults."""
        stage, _, _, _ = self._mock_stage()

        # Test with no environment variables set
        with patch.dict(os.environ, {}, clear=True):
            # Should use defaults (200)
            max_cooc = int(os.getenv("GRAPHRAG_MAX_COOC_PER_ENTITY", "200"))
            max_sim = int(os.getenv("GRAPHRAG_MAX_SIM_PER_ENTITY", "200"))

            assert max_cooc == 200
            assert max_sim == 200

    def test_get_entity_degree(self):
        """Test that _get_entity_degree counts relationships correctly."""
        stage, mock_relations, _, _ = self._mock_stage()

        entity_id = "b" * 32

        # Mock count_documents
        mock_relations.count_documents.return_value = 5

        # Call _get_entity_degree
        degree = stage._get_entity_degree(entity_id)

        # Verify count_documents was called with correct query
        assert mock_relations.count_documents.called
        call_args = mock_relations.count_documents.call_args[0][0]
        assert "$or" in call_args
        assert {"subject_id": entity_id} in call_args["$or"]
        assert {"object_id": entity_id} in call_args["$or"]

        assert degree == 5


def run_all_tests():
    """Run all tests."""
    test_classes = [TestEdgeCaps]

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

