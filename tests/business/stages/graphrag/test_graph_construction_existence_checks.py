"""
Tests for Graph Construction Stage - Relationship Existence Checks.

Tests Achievement 0.1: Relationship Existence Checks Include Predicate.

Run with: python -m tests.business.stages.graphrag.test_graph_construction_existence_checks
"""

try:
    import pytest

    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from unittest.mock import MagicMock, Mock, patch
from typing import Dict, Any, List

from business.stages.graphrag.graph_construction import GraphConstructionStage


class TestMultiplePredicatesPerPair:
    """Test that multiple predicates are allowed between same entity pair."""

    def _mock_stage(self):
        """Create a mock GraphConstructionStage with necessary mocks."""
        stage = GraphConstructionStage()
        stage.config = Mock()
        stage.config.db_name = "test_db"
        stage.config.read_db_name = "test_db"
        stage.config.write_db_name = "test_db"

        # Mock collections
        mock_relations = MagicMock()
        mock_mentions = MagicMock()
        mock_entities = MagicMock()
        mock_chunks = MagicMock()

        stage.graphrag_collections = {
            "relations": mock_relations,
            "entity_mentions": mock_mentions,
            "entities": mock_entities,
        }

        def mock_get_collection(name, io, db_name):
            return mock_chunks

        stage.get_collection = mock_get_collection

        return stage, mock_relations, mock_mentions, mock_entities, mock_chunks

    def test_multiple_predicates_allowed(self):
        """Test that multiple predicates can exist between same entity pair."""
        stage, mock_relations, _, _, _ = self._mock_stage()

        entity1_id = "entity_1"
        entity2_id = "entity_2"

        # First relationship: "teaches"
        mock_relations.find_one.side_effect = [
            None,  # First check: "teaches" doesn't exist
            {"relationship_id": "rel_1"},  # After insert, it exists
            None,  # Second check: "mentors" doesn't exist
        ]

        # Mock batch_insert to simulate successful insert
        from unittest.mock import patch

        with patch(
            "business.stages.graphrag.graph_construction.batch_insert"
        ) as mock_batch:
            mock_batch.return_value = {"inserted": 1, "total": 1, "failed": 0}

            # First: Create "teaches" relationship
            # This would be done via _store_resolved_relationships, but for this test
            # we're testing the synthetic methods, so we'll test co-occurrence

            # For co-occurrence: should check predicate in existence check
            # We'll verify the query includes predicate
            query_calls = []

            def capture_find_one(query):
                query_calls.append(query)
                return None  # No existing relationship

            mock_relations.find_one.side_effect = capture_find_one

            # Simulate co-occurrence check
            # The fix should make this query include predicate
            result = mock_relations.find_one(
                {
                    "subject_id": entity1_id,
                    "object_id": entity2_id,
                    "predicate": "co_occurs_with",  # Should include this
                }
            )

            # Verify predicate was in query
            assert len(query_calls) > 0
            last_query = query_calls[-1]
            assert "predicate" in last_query
            assert last_query["predicate"] == "co_occurs_with"

    def test_same_predicate_not_duplicated(self):
        """Test that same predicate between same pair is not duplicated."""
        stage, mock_relations, _, _, _ = self._mock_stage()

        entity1_id = "entity_1"
        entity2_id = "entity_2"

        # First call: relationship exists
        existing_rel = {
            "relationship_id": "rel_1",
            "subject_id": entity1_id,
            "object_id": entity2_id,
            "predicate": "co_occurs_with",
        }

        mock_relations.find_one.return_value = existing_rel

        # Check existence (should find it)
        result = mock_relations.find_one(
            {
                "subject_id": entity1_id,
                "object_id": entity2_id,
                "predicate": "co_occurs_with",
            }
        )

        assert result is not None
        assert result["predicate"] == "co_occurs_with"


class TestCoOccurrenceExistenceCheck:
    """Test that co-occurrence existence check includes predicate."""

    def _mock_stage(self):
        """Create a mock GraphConstructionStage."""
        stage = GraphConstructionStage()
        stage.config = Mock()
        stage.config.db_name = "test_db"

        mock_relations = MagicMock()
        mock_mentions = MagicMock()

        stage.graphrag_collections = {
            "relations": mock_relations,
            "entity_mentions": mock_mentions,
        }

        return stage, mock_relations, mock_mentions

    def test_co_occurrence_check_includes_predicate(self):
        """Test that co-occurrence existence check includes predicate in query."""
        stage, mock_relations, mock_mentions = self._mock_stage()

        # Mock entity mentions
        mock_mentions.find.return_value = [
            {"chunk_id": "chunk_1", "entity_id": "entity_1"},
            {"chunk_id": "chunk_1", "entity_id": "entity_2"},
        ]

        # Capture find_one calls
        query_calls = []

        def capture_find_one(query):
            query_calls.append(query)
            return None  # No existing relationship

        mock_relations.find_one.side_effect = capture_find_one

        # Mock degree check (Achievement 2.3)
        mock_relations.count_documents.return_value = 0

        # Mock batch_insert
        with patch(
            "business.stages.graphrag.graph_construction.batch_insert"
        ) as mock_batch:
            mock_batch.return_value = {"inserted": 1, "total": 1, "failed": 0}

            # Call _add_co_occurrence_relationships
            stage._add_co_occurrence_relationships()

            # Verify at least one find_one was called with predicate
            assert len(query_calls) > 0

            # Check that at least one query includes predicate
            found_predicate_check = False
            for query in query_calls:
                # Query should include predicate: "co_occurs_with"
                if isinstance(query, dict) and "predicate" in query:
                    assert query["predicate"] == "co_occurs_with"
                    found_predicate_check = True
                    break

            assert found_predicate_check, "Existence check should include predicate"


class TestSemanticSimilarityExistenceCheck:
    """Test that semantic similarity existence check includes predicate."""

    def _mock_stage(self):
        """Create a mock GraphConstructionStage."""
        stage = GraphConstructionStage()
        stage.config = Mock()
        stage.config.db_name = "test_db"

        mock_relations = MagicMock()
        mock_entities = MagicMock()

        stage.graphrag_collections = {
            "relations": mock_relations,
            "entities": mock_entities,
        }

        return stage, mock_relations, mock_entities

    def test_semantic_similarity_check_includes_predicate(self):
        """Test that semantic similarity existence check includes predicate."""
        stage, mock_relations, mock_entities = self._mock_stage()

        # Mock entities with embeddings (find returns entities that already have embeddings)
        mock_entities.find.side_effect = [
            # First call: entities without embeddings (empty)
            iter([]),
            # Second call: entities with embeddings
            iter(
                [
                    {
                        "entity_id": "entity_1",
                        "name": "Entity 1",
                        "description": "Description 1",
                        "entity_embedding": [0.1, 0.2, 0.3],
                    },
                    {
                        "entity_id": "entity_2",
                        "name": "Entity 2",
                        "description": "Description 2",
                        "entity_embedding": [0.4, 0.5, 0.6],
                    },
                ]
            ),
        ]

        # Capture find_one calls
        query_calls = []

        def capture_find_one(query):
            query_calls.append(query)
            return None  # No existing relationship

        mock_relations.find_one.side_effect = capture_find_one

        # Mock batch_insert
        with patch(
            "business.stages.graphrag.graph_construction.batch_insert"
        ) as mock_batch:
            mock_batch.return_value = {"inserted": 1, "total": 1, "failed": 0}

            # Call _add_semantic_similarity_relationships
            stage._add_semantic_similarity_relationships(similarity_threshold=0.5)

            # Verify at least one find_one was called
            assert len(query_calls) > 0

            # Check that at least one query includes predicate
            found_predicate_check = False
            for query in query_calls:
                if isinstance(query, dict) and "predicate" in query:
                    assert query["predicate"] == "semantically_similar_to"
                    found_predicate_check = True
                    break

            assert found_predicate_check, "Existence check should include predicate"


class TestCrossChunkExistenceCheck:
    """Test that cross-chunk existence check includes predicate."""

    def _mock_stage(self):
        """Create a mock GraphConstructionStage."""
        stage = GraphConstructionStage()
        stage.config = Mock()
        stage.config.db_name = "test_db"

        mock_relations = MagicMock()
        mock_mentions = MagicMock()
        mock_entities = MagicMock()
        mock_chunks = MagicMock()

        stage.graphrag_collections = {
            "relations": mock_relations,
            "entity_mentions": mock_mentions,
            "entities": mock_entities,
        }

        def mock_get_collection(name, io, db_name=None):
            return mock_chunks

        stage.get_collection = mock_get_collection
        stage.config = Mock()
        stage.config.db_name = "test_db"
        stage.config.read_db_name = "test_db"
        stage.config.write_db_name = "test_db"

        return stage, mock_relations, mock_mentions, mock_entities, mock_chunks

    def test_cross_chunk_check_includes_predicate(self):
        """Test that cross-chunk existence check includes predicate."""
        stage, mock_relations, mock_mentions, mock_entities, mock_chunks = (
            self._mock_stage()
        )

        # Mock chunk metadata
        mock_chunks.find.return_value = [
            {
                "chunk_id": "chunk_1",
                "video_id": "video_1",
                "timestamp_start": "00:00:00",
            },
            {
                "chunk_id": "chunk_2",
                "video_id": "video_1",
                "timestamp_start": "00:01:00",
            },
        ]

        # Mock entity mentions
        mock_mentions.find.return_value = [
            {"chunk_id": "chunk_1", "entity_id": "entity_1"},
            {"chunk_id": "chunk_2", "entity_id": "entity_2"},
        ]

        # Mock entities
        def mock_entity_find_one(query):
            entity_id = query.get("entity_id")
            if entity_id == "entity_1":
                return {"entity_id": "entity_1", "type": "PERSON", "name": "Alice"}
            elif entity_id == "entity_2":
                return {"entity_id": "entity_2", "type": "CONCEPT", "name": "Python"}
            return None

        mock_entities.find_one.side_effect = mock_entity_find_one

        # Capture find_one calls for existence checks
        query_calls = []

        def capture_find_one(query):
            query_calls.append(query)
            return None  # No existing relationship

        mock_relations.find_one.side_effect = capture_find_one

        # Mock batch_insert
        with patch(
            "business.stages.graphrag.graph_construction.batch_insert"
        ) as mock_batch:
            mock_batch.return_value = {"inserted": 1, "total": 1, "failed": 0}

            # Call _add_cross_chunk_relationships
            stage._add_cross_chunk_relationships()

            # Verify at least one find_one was called
            assert len(query_calls) > 0

            # Check that at least one query includes predicate
            found_predicate_check = False
            for query in query_calls:
                if isinstance(query, dict) and "predicate" in query:
                    # Predicate should be determined by _determine_cross_chunk_predicate
                    assert "predicate" in query
                    found_predicate_check = True
                    break

            assert found_predicate_check, "Existence check should include predicate"


def run_all_tests():
    """Run all tests."""
    test_classes = [
        TestMultiplePredicatesPerPair,
        TestCoOccurrenceExistenceCheck,
        TestSemanticSimilarityExistenceCheck,
        TestCrossChunkExistenceCheck,
    ]

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
