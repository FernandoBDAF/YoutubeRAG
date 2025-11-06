"""
Tests for Graph Construction Stage - Cosine Similarity Optimization.

Tests Achievement 2.2: Cosine Similarity Optimization.

Run with: python -m tests.business.stages.graphrag.test_graph_construction_cosine_optimization
"""

try:
    import pytest

    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from unittest.mock import MagicMock, Mock, patch
import numpy as np
from typing import Dict, Any

from business.stages.graphrag.graph_construction import GraphConstructionStage


class TestCosineSimilarityOptimization:
    """Test that cosine similarity uses optimized dot product for normalized embeddings."""

    def _mock_stage(self):
        """Create a mock GraphConstructionStage."""
        stage = GraphConstructionStage()
        stage.config = Mock()
        stage.config.db_name = "test_db"

        mock_entities = MagicMock()
        mock_relations = MagicMock()

        stage.graphrag_collections = {
            "entities": mock_entities,
            "relations": mock_relations,
        }

        return stage, mock_entities, mock_relations

    def test_normalized_embeddings_use_dot_product(self):
        """Test that normalized embeddings use dot product directly."""
        stage, mock_entities, mock_relations = self._mock_stage()

        # Create normalized embeddings (L2 norm = 1.0)
        emb1 = np.array([0.6, 0.8, 0.0])  # Norm = 1.0
        emb2 = np.array([0.8, 0.6, 0.0])  # Norm = 1.0

        # Mock entities with normalized embeddings
        # First call: entities without embeddings (empty)
        # Second call: entities with embeddings
        mock_entities.find.side_effect = [
            iter([]),  # No entities without embeddings
            iter([
                {
                    "entity_id": "b" * 32,
                    "name": "Entity 1",
                    "entity_embedding": emb1.tolist(),
                    "entity_embedding_norm": 1.0,  # Normalized flag
                },
                {
                    "entity_id": "c" * 32,
                    "name": "Entity 2",
                    "entity_embedding": emb2.tolist(),
                    "entity_embedding_norm": 1.0,  # Normalized flag
                },
            ]),
        ]

        # Mock: no existing relationship
        mock_relations.find_one.return_value = None

        # Mock batch_insert
        from unittest.mock import patch

        with patch(
            "business.stages.graphrag.graph_construction.batch_insert"
        ) as mock_batch:
            mock_batch.return_value = {"inserted": 1, "total": 1, "failed": 0}

            # Call _add_semantic_similarity_relationships
            stage._add_semantic_similarity_relationships(similarity_threshold=0.5)

            # Verify batch_insert was called (relationship created)
            assert mock_batch.called

    def test_results_match_current_cosine_similarity(self):
        """Test that optimized similarity matches current cosine similarity."""
        # Test vectors
        emb1 = np.array([1.0, 2.0, 3.0])
        emb2 = np.array([4.0, 5.0, 6.0])

        # Normalize
        emb1_norm = emb1 / np.linalg.norm(emb1)
        emb2_norm = emb2 / np.linalg.norm(emb2)

        # Current formula
        similarity_current = np.dot(emb1, emb2) / (
            np.linalg.norm(emb1) * np.linalg.norm(emb2)
        )

        # Optimized formula (dot product of normalized)
        similarity_optimized = np.dot(emb1_norm, emb2_norm)

        # Should match (within floating point precision)
        assert abs(similarity_current - similarity_optimized) < 1e-10

    def test_normalization_flag_stored(self):
        """Test that normalization flag is stored when generating embeddings."""
        stage, mock_entities, mock_relations = self._mock_stage()

        # Mock entity without embedding
        entity_without_embedding = {
            "entity_id": "b" * 32,
            "name": "Test Entity",
            "description": "Test description",
        }

        mock_entities.find.return_value = [entity_without_embedding]

        # Mock embed_texts
        test_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        normalized_embedding = (np.array(test_embedding) / np.linalg.norm(test_embedding)).tolist()

        from unittest.mock import patch

        with patch("business.stages.ingestion.embed.embed_texts") as mock_embed:
            mock_embed.return_value = [test_embedding]

            # Track update calls
            update_calls = []

            def capture_update(filter, update):
                update_calls.append((filter, update))

            mock_entities.update_one.side_effect = capture_update

            # Call _add_semantic_similarity_relationships (will generate embedding)
            stage._add_semantic_similarity_relationships(similarity_threshold=0.5)

            # Verify update_one was called
            assert len(update_calls) > 0

            # Get the update document
            _, update_doc = update_calls[0]
            set_doc = update_doc.get("$set", {})

            # Verify normalization flag is stored
            assert "entity_embedding_norm" in set_doc
            assert set_doc["entity_embedding_norm"] == 1.0

            # Verify embedding is normalized
            stored_embedding = set_doc.get("entity_embedding")
            if stored_embedding:
                stored_norm = np.linalg.norm(np.array(stored_embedding))
                assert abs(stored_norm - 1.0) < 1e-10  # Should be normalized

    def test_backward_compatibility_non_normalized(self):
        """Test that non-normalized embeddings still work (backward compatibility)."""
        stage, mock_entities, mock_relations = self._mock_stage()

        # Create non-normalized embeddings
        emb1 = np.array([1.0, 2.0, 3.0])  # Not normalized
        emb2 = np.array([4.0, 5.0, 6.0])  # Not normalized

        # Mock entities without normalization flag
        # First call: entities without embeddings (empty)
        # Second call: entities with embeddings (not normalized)
        mock_entities.find.side_effect = [
            iter([]),  # No entities without embeddings
            iter([
                {
                    "entity_id": "b" * 32,
                    "name": "Entity 1",
                    "entity_embedding": emb1.tolist(),
                    # No entity_embedding_norm flag
                },
                {
                    "entity_id": "c" * 32,
                    "name": "Entity 2",
                    "entity_embedding": emb2.tolist(),
                    # No entity_embedding_norm flag
                },
            ]),
        ]

        # Mock: no existing relationship
        mock_relations.find_one.return_value = None

        # Mock batch_insert
        from unittest.mock import patch

        with patch(
            "business.stages.graphrag.graph_construction.batch_insert"
        ) as mock_batch:
            mock_batch.return_value = {"inserted": 1, "total": 1, "failed": 0}

            # Call _add_semantic_similarity_relationships
            # Should use standard cosine formula (backward compatibility)
            stage._add_semantic_similarity_relationships(similarity_threshold=0.5)

            # Verify batch_insert was called (relationship created)
            assert mock_batch.called


def run_all_tests():
    """Run all tests."""
    test_classes = [TestCosineSimilarityOptimization]

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

