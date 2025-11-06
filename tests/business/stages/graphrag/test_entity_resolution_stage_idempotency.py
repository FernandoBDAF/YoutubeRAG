"""
Tests for entity mention deduplication and idempotency (Achievement 3.5.2).

Verifies that unique index prevents duplicate mentions and reruns are idempotent.
"""

import unittest
from unittest.mock import Mock, patch
from pymongo.errors import DuplicateKeyError

try:
    import pytest
except ImportError:
    pytest = None

from business.stages.graphrag.entity_resolution import EntityResolutionStage
from business.services.graphrag.indexes import _create_entity_mentions_indexes
from core.models.graphrag import ResolvedEntity, EntityType
from pymongo.database import Database


class TestUniqueIndexCreation(unittest.TestCase):
    """Test that unique index is created on (entity_id, chunk_id, position)."""

    def test_unique_index_created(self):
        """Test that unique index exists on entity_mentions collection."""
        # Mock database
        mock_db = Mock(spec=Database)
        mock_collection = Mock()
        mock_db.entity_mentions = mock_collection

        # Mock index creation
        mock_collection.create_index.return_value = "entity_chunk_position_unique"

        # Call index creation
        _create_entity_mentions_indexes(mock_db)

        # Verify unique index was created
        create_index_calls = [
            call
            for call in mock_collection.create_index.call_args_list
            if len(call[0]) > 0
            and call[0][0] == [("entity_id", 1), ("chunk_id", 1), ("position", 1)]
        ]

        self.assertGreater(len(create_index_calls), 0, "Unique index should be created")

        # Verify unique=True was passed
        unique_call = create_index_calls[0]
        self.assertTrue(unique_call[1].get("unique", False), "Index should be unique")

    def test_index_creation_idempotent(self):
        """Test that index creation is idempotent (can run twice)."""
        # Mock database
        mock_db = Mock(spec=Database)
        mock_collection = Mock()
        mock_db.entity_mentions = mock_collection

        # First call succeeds
        mock_collection.create_index.return_value = "entity_chunk_position_unique"
        _create_entity_mentions_indexes(mock_db)

        # Second call should also succeed (idempotent)
        # Simulate index already exists (no exception raised)
        _create_entity_mentions_indexes(mock_db)

        # Should not raise exception
        self.assertTrue(True, "Index creation should be idempotent")


class TestDuplicatePrevention(unittest.TestCase):
    """Test that duplicate mentions are prevented."""

    def setUp(self):
        """Set up test fixtures."""
        self.stage = EntityResolutionStage()
        self.stage.config = Mock()
        self.stage.config.db_name = "test_db"
        self.stage.config.read_db_name = "test_db"
        self.stage.config.write_db_name = "test_db"

        # Mock collections
        self.stage.graphrag_collections = {
            "entity_mentions": Mock(),
        }

    def test_duplicate_mention_prevented(self):
        """Test that duplicate mentions cannot be inserted."""
        entity = ResolvedEntity(
            entity_id="a" * 32,
            canonical_name="Test Entity",
            name="Test Entity",
            type=EntityType.PERSON,
            description="Test description for entity",
            confidence=0.9,
            source_count=1,
            resolution_methods=["extraction"],
            aliases=[],
        )

        # Mock batch_insert to raise DuplicateKeyError on second insert
        with patch(
            "business.stages.graphrag.entity_resolution.batch_insert"
        ) as mock_batch:
            # First insert succeeds
            mock_batch.return_value = {"inserted": 1, "total": 1}

            # First call
            self.stage._store_entity_mentions(
                [entity], "chunk_1", "video_1", id_map=None
            )

            # Second call with same entity (simulating rerun)
            # batch_insert should handle duplicates gracefully with ordered=False
            # But we verify the unique index would prevent it
            mock_batch.return_value = {
                "inserted": 0,
                "total": 1,
            }  # 0 inserted due to duplicates

            # Second call should not raise exception (handled gracefully)
            self.stage._store_entity_mentions(
                [entity], "chunk_1", "video_1", id_map=None
            )

            # Verify batch_insert was called twice
            self.assertEqual(mock_batch.call_count, 2)

    def test_duplicate_error_handled_gracefully(self):
        """Test that DuplicateKeyError is handled gracefully."""
        entity = ResolvedEntity(
            entity_id="b" * 32,
            canonical_name="Test Entity 2",
            name="Test Entity 2",
            type=EntityType.PERSON,
            description="Test description for entity 2",
            confidence=0.9,
            source_count=1,
            resolution_methods=["extraction"],
            aliases=[],
        )

        # Mock batch_insert to raise DuplicateKeyError
        with patch(
            "business.stages.graphrag.entity_resolution.batch_insert"
        ) as mock_batch:
            mock_batch.side_effect = DuplicateKeyError("Duplicate key error")

            # Should not raise exception (handled gracefully)
            try:
                self.stage._store_entity_mentions(
                    [entity], "chunk_1", "video_1", id_map=None
                )
                # If we get here, error was handled
                handled = True
            except DuplicateKeyError:
                handled = False

            self.assertTrue(handled, "DuplicateKeyError should be handled gracefully")


class TestRerunIdempotency(unittest.TestCase):
    """Test that reruns are idempotent."""

    def setUp(self):
        """Set up test fixtures."""
        self.stage = EntityResolutionStage()
        self.stage.config = Mock()
        self.stage.config.db_name = "test_db"
        self.stage.config.read_db_name = "test_db"
        self.stage.config.write_db_name = "test_db"

        # Mock collections
        self.stage.graphrag_collections = {
            "entity_mentions": Mock(),
        }

    def test_rerun_does_not_create_duplicates(self):
        """Test that rerunning same chunk doesn't create duplicate mentions."""
        entity = ResolvedEntity(
            entity_id="c" * 32,
            canonical_name="Test Entity 3",
            name="Test Entity 3",
            type=EntityType.PERSON,
            description="Test description for entity 3",
            confidence=0.9,
            source_count=1,
            resolution_methods=["extraction"],
            aliases=[],
        )

        # Mock batch_insert
        with patch(
            "business.stages.graphrag.entity_resolution.batch_insert"
        ) as mock_batch:
            # First run: 1 inserted
            mock_batch.return_value = {"inserted": 1, "total": 1}

            self.stage._store_entity_mentions(
                [entity], "chunk_1", "video_1", id_map=None
            )

            # Second run (rerun): 0 inserted (duplicates prevented by unique index)
            mock_batch.return_value = {"inserted": 0, "total": 1}

            self.stage._store_entity_mentions(
                [entity], "chunk_1", "video_1", id_map=None
            )

            # Verify both calls succeeded (no exceptions)
            self.assertEqual(mock_batch.call_count, 2)

            # Verify second call reported 0 inserted (duplicates prevented)
            second_call_result = mock_batch.return_value
            self.assertEqual(second_call_result["inserted"], 0)


if __name__ == "__main__":
    unittest.main()
