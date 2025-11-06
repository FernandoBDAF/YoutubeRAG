"""
Tests for Graph Construction Stage - source_count Accuracy.

Tests Achievement 0.2: source_count Inflation Fixed.

Run with: python -m tests.business.stages.graphrag.test_graph_construction_source_count
"""

try:
    import pytest

    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from unittest.mock import MagicMock, Mock, patch
from typing import Dict, Any

from business.stages.graphrag.graph_construction import GraphConstructionStage
from core.models.graphrag import ResolvedRelationship, EntityType


class TestSourceCountAccuracy:
    """Test that source_count is accurate and doesn't inflate on reruns."""

    def _mock_stage(self):
        """Create a mock GraphConstructionStage."""
        stage = GraphConstructionStage()
        stage.config = Mock()
        stage.config.db_name = "test_db"

        mock_relations = MagicMock()
        stage.graphrag_collections = {"relations": mock_relations}

        return stage, mock_relations

    def test_new_relationship_source_count(self):
        """Test that new relationships start with source_count = 1."""
        stage, mock_relations = self._mock_stage()

        # Create a new relationship with valid 32-char IDs
        relationship = ResolvedRelationship(
            relationship_id="a" * 32,
            subject_id="b" * 32,
            object_id="c" * 32,
            predicate="teaches",
            description="Test relationship",
            confidence=0.9,
            source_count=1,
        )

        # Mock: relationship doesn't exist
        mock_relations.find_one.return_value = None

        # Call _insert_new_relationship
        stage._insert_new_relationship(relationship, "chunk_1", "video_1")

        # Verify insert_one was called
        assert mock_relations.insert_one.called

        # Get the document that was inserted
        call_args = mock_relations.insert_one.call_args
        inserted_doc = call_args[0][0]

        # Verify source_count = 1
        assert inserted_doc["source_count"] == 1
        assert inserted_doc["source_chunks"] == ["chunk_1"]

    def test_source_count_increments_on_new_chunk(self):
        """Test that source_count increments when a new chunk is added."""
        stage, mock_relations = self._mock_stage()

        # Existing relationship with one chunk
        existing_rel = {
            "relationship_id": "a" * 32,
            "subject_id": "b" * 32,
            "object_id": "c" * 32,
            "predicate": "teaches",
            "source_count": 1,
            "source_chunks": ["chunk_1"],
        }

        # New relationship from different chunk
        new_relationship = ResolvedRelationship(
            relationship_id="a" * 32,
            subject_id="b" * 32,
            object_id="c" * 32,
            predicate="teaches",
            description="Updated description",
            confidence=0.9,
            source_count=1,
        )

        # Mock: relationship exists
        mock_relations.find_one.return_value = existing_rel

        # Track update calls
        update_calls = []

        def capture_update_one(filter, update):
            update_calls.append((filter, update))

        mock_relations.update_one.side_effect = capture_update_one

        # Call _update_existing_relationship
        stage._update_existing_relationship(
            existing_rel, new_relationship, "chunk_2", "video_1"
        )

        # Verify update was called
        assert len(update_calls) > 0

        # Get the update document
        _, update_doc = update_calls[0]

        # Verify $inc is present (new chunk)
        assert "$inc" in update_doc
        assert update_doc["$inc"]["source_count"] == 1

        # Verify $addToSet is present
        assert "$addToSet" in update_doc
        assert "source_chunks" in update_doc["$addToSet"]

    def test_source_count_unchanged_on_rerun(self):
        """Test that source_count does not increment on rerun of same chunk."""
        stage, mock_relations = self._mock_stage()

        # Existing relationship with chunk_1
        existing_rel = {
            "relationship_id": "a" * 32,
            "subject_id": "b" * 32,
            "object_id": "c" * 32,
            "predicate": "teaches",
            "source_count": 1,
            "source_chunks": ["chunk_1"],
        }

        # Same relationship from same chunk (rerun)
        same_relationship = ResolvedRelationship(
            relationship_id="a" * 32,
            subject_id="b" * 32,
            object_id="c" * 32,
            predicate="teaches",
            description="Same description",
            confidence=0.9,
            source_count=1,
        )

        # Mock: relationship exists
        mock_relations.find_one.return_value = existing_rel

        # Track update calls
        update_calls = []

        def capture_update_one(filter, update):
            update_calls.append((filter, update))

        mock_relations.update_one.side_effect = capture_update_one

        # Call _update_existing_relationship with same chunk_id
        stage._update_existing_relationship(
            existing_rel, same_relationship, "chunk_1", "video_1"
        )

        # Verify update was called
        assert len(update_calls) > 0

        # Get the update document
        _, update_doc = update_calls[0]

        # Verify $inc is NOT present (same chunk, no increment)
        assert "$inc" not in update_doc or "source_count" not in update_doc.get(
            "$inc", {}
        )

        # Verify $addToSet is still present (idempotent)
        assert "$addToSet" in update_doc
        assert "source_chunks" in update_doc["$addToSet"]

    def test_source_count_matches_source_chunks_length(self):
        """Test that source_count matches the length of source_chunks."""
        stage, mock_relations = self._mock_stage()

        # Existing relationship with multiple chunks
        existing_rel = {
            "relationship_id": "a" * 32,
            "subject_id": "b" * 32,
            "object_id": "c" * 32,
            "predicate": "teaches",
            "source_count": 2,
            "source_chunks": ["chunk_1", "chunk_2"],
        }

        # New relationship from new chunk
        new_relationship = ResolvedRelationship(
            relationship_id="a" * 32,
            subject_id="b" * 32,
            object_id="c" * 32,
            predicate="teaches",
            description="New description",
            confidence=0.9,
            source_count=1,
        )

        # Mock: relationship exists
        mock_relations.find_one.return_value = existing_rel

        # Track update calls
        update_calls = []

        def capture_update_one(filter, update):
            update_calls.append((filter, update))

        mock_relations.update_one.side_effect = capture_update_one

        # Call _update_existing_relationship with new chunk
        stage._update_existing_relationship(
            existing_rel, new_relationship, "chunk_3", "video_1"
        )

        # Verify update was called
        assert len(update_calls) > 0

        # Get the update document
        _, update_doc = update_calls[0]

        # Verify $inc increments source_count (from 2 to 3)
        assert "$inc" in update_doc
        assert update_doc["$inc"]["source_count"] == 1

        # After update, source_count should be 3, matching 3 chunks
        # (This is verified by the increment happening)


def run_all_tests():
    """Run all tests."""
    test_classes = [TestSourceCountAccuracy]

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
                    raise

    print("\n✅ All tests passed!")


if __name__ == "__main__":
    run_all_tests()

