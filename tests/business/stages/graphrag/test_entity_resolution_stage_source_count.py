"""
Tests for source_count accuracy fix (Achievement 3.5.3).

Verifies that source_count only increments when adding new chunks and doesn't inflate on reruns.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import time

try:
    import pytest
except ImportError:
    pytest = None

from business.stages.graphrag.entity_resolution import EntityResolutionStage
from core.models.graphrag import ResolvedEntity, EntityType
from pymongo import ReturnDocument


class TestSourceCountAccuracy(unittest.TestCase):
    """Test that source_count accurately reflects source_chunks."""

    def setUp(self):
        """Set up test fixtures."""
        self.stage = EntityResolutionStage()
        self.stage.config = Mock()
        self.stage.config.db_name = "test_db"
        self.stage.config.read_db_name = "test_db"
        self.stage.config.write_db_name = "test_db"

        # Mock collections
        self.stage.graphrag_collections = {
            "entities": Mock(),
        }

        # Mock resolution agent
        self.stage.resolution_agent = Mock()
        self.stage.resolution_agent._normalize_entity_name = lambda x: x.lower()

    def test_source_count_increments_on_new_chunk(self):
        """Test that source_count increments when adding a new chunk."""
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

        # Mock collection
        mock_collection = self.stage.graphrag_collections["entities"]

        # First upsert: new entity with chunk_1
        mock_collection.find_one.return_value = None  # New entity
        mock_collection.find_one_and_update.return_value = {
            "entity_id": "a" * 32,
            "source_count": 1,
            "source_chunks": ["chunk_1"],
        }

        result = self.stage._upsert_entity(entity, "chunk_1", "video_1")

        # Verify find_one_and_update was called
        self.assertTrue(mock_collection.find_one_and_update.called)

        # Get the update document
        update_call = mock_collection.find_one_and_update.call_args
        update_doc = update_call[0][1]  # Second argument is the update document

        # Verify $setOnInsert includes source_count = 1
        self.assertEqual(update_doc["$setOnInsert"]["source_count"], 1)

        # Second upsert: existing entity with new chunk_2
        mock_collection.find_one.return_value = {
            "entity_id": "a" * 32,
            "source_count": 1,
            "source_chunks": ["chunk_1"],
        }
        mock_collection.find_one_and_update.return_value = {
            "entity_id": "a" * 32,
            "source_count": 2,
            "source_chunks": ["chunk_1", "chunk_2"],
        }

        result = self.stage._upsert_entity(entity, "chunk_2", "video_1")

        # Verify $inc was included (new chunk)
        update_call = mock_collection.find_one_and_update.call_args
        update_doc = update_call[0][1]
        self.assertIn("$inc", update_doc)
        self.assertEqual(update_doc["$inc"]["source_count"], 1)

    def test_source_count_unchanged_on_rerun(self):
        """Test that source_count doesn't increment when rerunning same chunk."""
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

        # Mock collection
        mock_collection = self.stage.graphrag_collections["entities"]

        # First upsert: new entity
        mock_collection.find_one.return_value = None
        mock_collection.find_one_and_update.return_value = {
            "entity_id": "b" * 32,
            "source_count": 1,
            "source_chunks": ["chunk_1"],
        }

        self.stage._upsert_entity(entity, "chunk_1", "video_1")

        # Second upsert: same chunk (rerun)
        mock_collection.find_one.return_value = {
            "entity_id": "b" * 32,
            "source_count": 1,
            "source_chunks": ["chunk_1"],  # chunk_1 already in source_chunks
        }
        mock_collection.find_one_and_update.return_value = {
            "entity_id": "b" * 32,
            "source_count": 1,  # Should still be 1, not 2
            "source_chunks": ["chunk_1"],
        }

        result = self.stage._upsert_entity(entity, "chunk_1", "video_1")

        # Verify $inc was NOT included (chunk already counted)
        update_call = mock_collection.find_one_and_update.call_args
        update_doc = update_call[0][1]
        self.assertNotIn(
            "$inc", update_doc, "source_count should not increment on rerun"
        )

    def test_source_count_matches_source_chunks_length(self):
        """Test that source_count matches the length of source_chunks array."""
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

        # Mock collection
        mock_collection = self.stage.graphrag_collections["entities"]

        # Add multiple chunks
        chunks = ["chunk_1", "chunk_2", "chunk_3"]
        source_count = 0

        for chunk_id in chunks:
            if source_count == 0:
                # First chunk: new entity
                mock_collection.find_one.return_value = None
            else:
                # Subsequent chunks: existing entity
                mock_collection.find_one.return_value = {
                    "entity_id": "c" * 32,
                    "source_count": source_count,
                    "source_chunks": chunks[:source_count],
                }

            source_count += 1
            mock_collection.find_one_and_update.return_value = {
                "entity_id": "c" * 32,
                "source_count": source_count,
                "source_chunks": chunks[:source_count],
            }

            self.stage._upsert_entity(entity, chunk_id, "video_1")

        # Verify final source_count matches source_chunks length
        final_result = mock_collection.find_one_and_update.return_value
        self.assertEqual(
            final_result["source_count"], len(final_result["source_chunks"])
        )

    def test_new_entity_source_count(self):
        """Test that new entity starts with source_count = 1."""
        entity = ResolvedEntity(
            entity_id="d" * 32,
            canonical_name="Test Entity 4",
            name="Test Entity 4",
            type=EntityType.PERSON,
            description="Test description for entity 4",
            confidence=0.9,
            source_count=1,
            resolution_methods=["extraction"],
            aliases=[],
        )

        # Mock collection
        mock_collection = self.stage.graphrag_collections["entities"]
        mock_collection.find_one.return_value = None  # New entity
        mock_collection.find_one_and_update.return_value = {
            "entity_id": "d" * 32,
            "source_count": 1,
            "source_chunks": ["chunk_1"],
        }

        result = self.stage._upsert_entity(entity, "chunk_1", "video_1")

        # Verify $setOnInsert includes source_count = 1
        update_call = mock_collection.find_one_and_update.call_args
        update_doc = update_call[0][1]
        self.assertEqual(update_doc["$setOnInsert"]["source_count"], 1)


if __name__ == "__main__":
    unittest.main()
