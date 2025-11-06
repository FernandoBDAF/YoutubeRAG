"""
Tests for entity mention ID mapping fix (Achievement 3.5.1).

Verifies that entity mentions use the correct entity_id when entities
are merged via fuzzy matching.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import time

try:
    import pytest
except ImportError:
    pytest = None

from business.stages.graphrag.entity_resolution import EntityResolutionStage
from core.models.graphrag import ResolvedEntity, EntityType
from core.config.graphrag import EntityResolutionConfig


class TestIDMappingOnFuzzyMatch(unittest.TestCase):
    """Test that id_map correctly maps original_id to final_id on fuzzy match."""

    def setUp(self):
        """Set up test fixtures."""
        self.stage = EntityResolutionStage()
        self.stage.config = Mock()
        self.stage.config.db_name = "test_db"
        self.stage.config.read_db_name = "test_db"
        self.stage.config.write_db_name = "test_db"
        self.stage.config.similarity_threshold = 0.85
        self.stage.config.model_name = "gpt-4o-mini"

        # Mock collections
        self.stage.graphrag_collections = {
            "entities": Mock(),
            "entity_mentions": Mock(),
        }

        # Mock database operations
        self.stage.get_collection = Mock(return_value=Mock())

    def test_id_map_on_fuzzy_match(self):
        """Test that id_map contains correct mapping when fuzzy match occurs."""
        # Create two entities that will fuzzy match
        entity1 = ResolvedEntity(
            entity_id="a" * 32,  # 32-char MD5 hash
            canonical_name="Jason Ku",
            name="Jason Ku",
            type=EntityType.PERSON,
            description="Professor at MIT",
            confidence=0.9,
            source_count=1,
            resolution_methods=["extraction"],
            aliases=[],
        )

        entity2 = ResolvedEntity(
            entity_id="b" * 32,  # 32-char MD5 hash
            canonical_name="J. Ku",
            name="J. Ku",
            type=EntityType.PERSON,
            description="Professor at MIT",
            confidence=0.85,
            source_count=1,
            resolution_methods=["extraction"],
            aliases=[],
        )

        entity_id_1 = "a" * 32
        entity_id_2 = "b" * 32

        # Mock existing entity in DB (entity1)
        self.stage.graphrag_collections["entities"].find_one = Mock(
            side_effect=lambda q: (
                {"entity_id": entity_id_1, "canonical_name": "Jason Ku"}
                if q.get("entity_id") == entity_id_1
                else None
            )
        )

        # Mock candidate lookup to return entity1 for entity2
        self.stage._find_db_candidates = Mock(
            return_value=[
                {
                    "entity_id": entity_id_1,
                    "canonical_name": "Jason Ku",
                    "aliases": [],
                    "type": "PERSON",
                }
            ]
        )

        # Mock _choose_match to return match for entity2
        self.stage._choose_match = Mock(
            side_effect=lambda name, candidates: (
                candidates[0] if name == "J. Ku" else None
            )
        )

        # Mock _upsert_entity
        self.stage._upsert_entity = Mock(return_value={"entity_id": entity_id_1})

        # Call _store_resolved_entities
        id_map = self.stage._store_resolved_entities(
            [entity1, entity2], "chunk_1", "video_1"
        )

        # Verify id_map
        self.assertEqual(id_map[entity_id_1], entity_id_1)  # No change
        self.assertEqual(id_map[entity_id_2], entity_id_1)  # Merged to entity_id_1

    def test_id_map_on_new_entity(self):
        """Test that id_map maps to itself for new entities."""
        new_entity_id = "d" * 32
        entity = ResolvedEntity(
            entity_id=new_entity_id,
            canonical_name="New Entity",
            name="New Entity",
            type=EntityType.CONCEPT,
            description="A new concept entity",
            confidence=0.8,
            source_count=1,
            resolution_methods=["extraction"],
            aliases=[],
        )

        # Mock no existing entity
        self.stage.graphrag_collections["entities"].find_one = Mock(return_value=None)
        self.stage._find_db_candidates = Mock(return_value=[])
        self.stage._choose_match = Mock(return_value=None)
        self.stage._upsert_entity = Mock(return_value={"entity_id": new_entity_id})

        id_map = self.stage._store_resolved_entities([entity], "chunk_1", "video_1")

        # Verify id_map maps to itself
        self.assertEqual(id_map[new_entity_id], new_entity_id)

    def test_mentions_use_correct_id(self):
        """Test that mentions use final_id from id_map."""
        entity1 = ResolvedEntity(
            entity_id="a" * 32,  # 32-char MD5 hash
            canonical_name="Test Entity",
            name="Test Entity",
            type=EntityType.PERSON,
            description="Test description for entity",
            confidence=0.9,
            source_count=1,
            resolution_methods=["extraction"],
            aliases=[],
        )

        # Mock id_map (simulating fuzzy match merge)
        original_id = "a" * 32
        final_id = "b" * 32
        id_map = {original_id: final_id}

        # Mock batch_insert
        mock_collection = Mock()
        self.stage.graphrag_collections["entity_mentions"] = mock_collection

        with patch(
            "business.stages.graphrag.entity_resolution.batch_insert"
        ) as mock_batch:
            mock_batch.return_value = {"inserted": 1, "total": 1}

            # Call _store_entity_mentions
            self.stage._store_entity_mentions([entity1], "chunk_1", "video_1", id_map)

            # Verify batch_insert was called
            self.assertTrue(mock_batch.called)

            # Get the documents passed to batch_insert
            call_args = mock_batch.call_args
            documents = call_args[1]["documents"]

            # Verify mention uses final_id from id_map
            self.assertEqual(len(documents), 1)
            self.assertEqual(documents[0]["entity_id"], final_id)
            self.assertNotEqual(documents[0]["entity_id"], original_id)

    def test_mentions_backward_compatibility(self):
        """Test that mentions work without id_map (backward compatibility)."""
        entity = ResolvedEntity(
            entity_id="c" * 32,  # 32-char MD5 hash
            canonical_name="Test Entity",
            name="Test Entity",
            type=EntityType.PERSON,
            description="Test description for entity",
            confidence=0.9,
            source_count=1,
            resolution_methods=["extraction"],
            aliases=[],
        )

        # Mock batch_insert
        with patch(
            "business.stages.graphrag.entity_resolution.batch_insert"
        ) as mock_batch:
            mock_batch.return_value = {"inserted": 1, "total": 1}

            # Call _store_entity_mentions without id_map
            self.stage._store_entity_mentions(
                [entity], "chunk_1", "video_1", id_map=None
            )

            # Verify batch_insert was called
            self.assertTrue(mock_batch.called)

            # Get the documents
            call_args = mock_batch.call_args
            documents = call_args[1]["documents"]

            # Verify mention uses entity.entity_id (backward compatibility)
            self.assertEqual(documents[0]["entity_id"], "c" * 32)


if __name__ == "__main__":
    unittest.main()
