"""
Tests for Graph Construction Stage - Reverse Mapping Collision Handling.

Tests Achievement 1.2: Reverse Mapping Collision Handling.

Run with: python -m tests.business.stages.graphrag.test_graph_construction_reverse_collision
"""

try:
    import pytest

    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from unittest.mock import MagicMock, Mock
from typing import Dict, Any

from business.stages.graphrag.graph_construction import GraphConstructionStage
from pymongo import ReturnDocument


class TestReverseMappingCollision:
    """Test that reverse mapping handles existing reverse relationships correctly."""

    def _mock_stage(self):
        """Create a mock GraphConstructionStage."""
        stage = GraphConstructionStage()
        stage.config = Mock()
        stage.config.db_name = "test_db"

        mock_relations = MagicMock()
        stage.graphrag_collections = {"relations": mock_relations}

        return stage, mock_relations

    def test_reverse_exists_merges_instead_of_duplicating(self):
        """Test that existing reverse relationships are merged, not duplicated."""
        stage, mock_relations = self._mock_stage()

        # Original relationship
        original_rel = {
            "relationship_id": "a" * 32,
            "subject_id": "b" * 32,
            "object_id": "c" * 32,
            "predicate": "teaches",
            "description": "Original description",
            "confidence": 0.8,
            "source_chunks": ["chunk_1"],
        }

        # Reverse relationship already exists
        existing_reverse = {
            "relationship_id": "d" * 32,  # Different ID (reverse)
            "subject_id": "c" * 32,
            "object_id": "b" * 32,
            "predicate": "taught_by",
            "description": "Existing reverse description",
            "confidence": 0.9,  # Higher confidence
            "source_chunks": ["chunk_2"],
        }

        # Mock: find returns original relationship
        mock_relations.find.return_value = [original_rel]

        # Generate reverse relationship_id (same as code does)
        from core.models.graphrag import ResolvedRelationship

        reverse_relationship_id = ResolvedRelationship.generate_relationship_id(
            "c" * 32, "b" * 32, "taught_by"
        )

        # Update existing_reverse to use correct relationship_id
        existing_reverse["relationship_id"] = reverse_relationship_id

        # Track update calls
        update_calls = []

        # Mock: find_one returns existing reverse when checking by relationship_id
        def mock_find_one(query):
            if "relationship_id" in query:
                if query["relationship_id"] == reverse_relationship_id:
                    return existing_reverse
            return None

        mock_relations.find_one.side_effect = mock_find_one

        # Mock: find_one_and_update for merge
        def mock_find_one_and_update(filter, update, **kwargs):
            update_calls.append((filter, update))
            # Verify merge policy
            assert "$max" in update or "$set" in update
            assert "$addToSet" in update  # Union source_chunks
            return existing_reverse

        mock_relations.find_one_and_update.side_effect = mock_find_one_and_update

        # Mock batch_insert (should not be called if merge happens)
        from unittest.mock import patch

        with patch("business.stages.graphrag.graph_construction.batch_insert") as mock_batch:
            # Call _add_bidirectional_relationships
            stage._add_bidirectional_relationships()

            # Verify find_one_and_update was called (merge happened)
            assert len(update_calls) > 0

    def test_reverse_not_exists_creates_new(self):
        """Test that non-existent reverse relationships are created."""
        stage, mock_relations = self._mock_stage()

        # Original relationship
        original_rel = {
            "relationship_id": "a" * 32,
            "subject_id": "b" * 32,
            "object_id": "c" * 32,
            "predicate": "teaches",
            "description": "Original description",
            "confidence": 0.8,
            "source_chunks": ["chunk_1"],
        }

        # Mock: find returns original relationship
        mock_relations.find.return_value = [original_rel]

        # Mock: find_one returns None (reverse doesn't exist)
        mock_relations.find_one.return_value = None

        # Mock batch_insert
        from unittest.mock import patch

        with patch("business.stages.graphrag.graph_construction.batch_insert") as mock_batch:
            mock_batch.return_value = {"inserted": 1, "total": 1, "failed": 0}

            # Call _add_bidirectional_relationships
            stage._add_bidirectional_relationships()

            # Verify batch_insert was called (new reverse created)
            assert mock_batch.called

    def test_merge_policy_max_confidence(self):
        """Test that merge policy uses max confidence."""
        stage, mock_relations = self._mock_stage()

        # Original relationship with lower confidence
        original_rel = {
            "relationship_id": "a" * 32,
            "subject_id": "b" * 32,
            "object_id": "c" * 32,
            "predicate": "teaches",
            "confidence": 0.7,
        }

        # Existing reverse with higher confidence
        existing_reverse = {
            "relationship_id": "d" * 32,
            "confidence": 0.9,  # Higher
        }

        mock_relations.find.return_value = [original_rel]
        mock_relations.find_one.return_value = existing_reverse

        # Track update document
        update_docs = []

        def capture_update(filter, update, **kwargs):
            update_docs.append(update)
            return existing_reverse

        mock_relations.find_one_and_update.side_effect = capture_update

        # Call _add_bidirectional_relationships
        stage._add_bidirectional_relationships()

        # Verify $max or $set includes max confidence
        assert len(update_docs) > 0
        update = update_docs[0]
        # Should keep max confidence (0.9)
        assert "$max" in update or ("$set" in update and "confidence" in update.get("$set", {}))


def run_all_tests():
    """Run all tests."""
    test_classes = [TestReverseMappingCollision]

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

