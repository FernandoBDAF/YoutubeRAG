"""
Tests for TransformationLogger service.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from pymongo.database import Database
from business.services.graphrag.transformation_logger import (
    TransformationLogger,
    get_transformation_logger,
)


class TestTransformationLogger(unittest.TestCase):
    """Test cases for TransformationLogger."""

    def setUp(self):
        """Set up test fixtures."""
        self.db = Mock(spec=Database)
        self.collection = MagicMock()
        self.db.transformation_logs = self.collection

    def test_init_enabled(self):
        """Test logger initialization with logging enabled."""
        logger = TransformationLogger(self.db, enabled=True)
        self.assertTrue(logger.enabled)
        self.assertEqual(logger.collection, self.collection)
        # Verify indexes were created
        self.assertTrue(self.collection.create_index.called)

    def test_init_disabled(self):
        """Test logger initialization with logging disabled."""
        logger = TransformationLogger(self.db, enabled=False)
        self.assertFalse(logger.enabled)
        self.assertIsNone(logger.collection)

    def test_log_entity_merge(self):
        """Test logging entity merge operation."""
        logger = TransformationLogger(self.db, enabled=True)
        self.collection.insert_one.return_value.inserted_id = "test_id"

        entity_a = {"id": "entity_a_123", "name": "Python"}
        entity_b = {"id": "entity_b_456", "name": "Python Programming"}
        result_entity = {"id": "entity_b_456", "name": "Python"}

        log_id = logger.log_entity_merge(
            entity_a=entity_a,
            entity_b=entity_b,
            result_entity=result_entity,
            reason="fuzzy_match",
            similarity=0.95,
            confidence=0.90,
            method="levenshtein",
            trace_id="trace_123",
        )

        self.assertIsNotNone(log_id)
        self.assertTrue(self.collection.insert_one.called)
        call_args = self.collection.insert_one.call_args[0][0]
        self.assertEqual(call_args["operation"], "MERGE")
        self.assertEqual(call_args["stage"], "entity_resolution")
        self.assertEqual(call_args["trace_id"], "trace_123")
        self.assertEqual(call_args["reason"], "fuzzy_match")
        self.assertEqual(call_args["similarity"], 0.95)
        self.assertEqual(call_args["confidence"], 0.90)

    def test_log_entity_create(self):
        """Test logging entity creation operation."""
        logger = TransformationLogger(self.db, enabled=True)
        self.collection.insert_one.return_value.inserted_id = "test_id"

        entity = {"id": "entity_123", "name": "Python"}

        log_id = logger.log_entity_create(
            entity=entity,
            entity_type="TECHNOLOGY",
            sources=5,
            confidence=0.92,
            trace_id="trace_123",
        )

        self.assertIsNotNone(log_id)
        call_args = self.collection.insert_one.call_args[0][0]
        self.assertEqual(call_args["operation"], "CREATE")
        self.assertEqual(call_args["entity_type"], "TECHNOLOGY")
        self.assertEqual(call_args["sources"], 5)

    def test_log_entity_skip(self):
        """Test logging entity skip operation."""
        logger = TransformationLogger(self.db, enabled=True)
        self.collection.insert_one.return_value.inserted_id = "test_id"

        entity = {"id": "entity_123", "name": "the"}

        log_id = logger.log_entity_skip(
            entity=entity,
            reason="stopword",
            confidence=0.10,
            trace_id="trace_123",
        )

        self.assertIsNotNone(log_id)
        call_args = self.collection.insert_one.call_args[0][0]
        self.assertEqual(call_args["operation"], "SKIP")
        self.assertEqual(call_args["reason"], "stopword")

    def test_log_relationship_create(self):
        """Test logging relationship creation operation."""
        logger = TransformationLogger(self.db, enabled=True)
        self.collection.insert_one.return_value.inserted_id = "test_id"

        relationship = {
            "subject": {"id": "entity_a", "name": "Python"},
            "predicate": "uses",
            "object": {"id": "entity_b", "name": "Django"},
        }

        log_id = logger.log_relationship_create(
            relationship=relationship,
            relationship_type="llm_extracted",
            confidence=0.90,
            trace_id="trace_123",
        )

        self.assertIsNotNone(log_id)
        call_args = self.collection.insert_one.call_args[0][0]
        self.assertEqual(call_args["operation"], "RELATIONSHIP")
        self.assertEqual(call_args["stage"], "graph_construction")
        self.assertEqual(call_args["relationship_type"], "llm_extracted")

    def test_log_relationship_filter(self):
        """Test logging relationship filter operation."""
        logger = TransformationLogger(self.db, enabled=True)
        self.collection.insert_one.return_value.inserted_id = "test_id"

        relationship = {
            "subject": {"id": "entity_a", "name": "Python"},
            "predicate": "uses",
            "object": {"id": "entity_b", "name": "Django"},
        }

        log_id = logger.log_relationship_filter(
            relationship=relationship,
            reason="below_threshold",
            confidence=0.25,
            threshold=0.30,
            trace_id="trace_123",
        )

        self.assertIsNotNone(log_id)
        call_args = self.collection.insert_one.call_args[0][0]
        self.assertEqual(call_args["operation"], "FILTER")
        self.assertEqual(call_args["reason"], "below_threshold")
        self.assertEqual(call_args["threshold"], 0.30)

    def test_log_relationship_augment(self):
        """Test logging relationship augmentation operation."""
        logger = TransformationLogger(self.db, enabled=True)
        self.collection.insert_one.return_value.inserted_id = "test_id"

        relationship = {
            "subject": {"id": "entity_a", "name": "Python"},
            "predicate": "co_occurs_with",
            "object": {"id": "entity_b", "name": "Django"},
        }

        log_id = logger.log_relationship_augment(
            relationship=relationship,
            method="co_occurrence",
            confidence=0.70,
            chunk_id="chunk_123",
            trace_id="trace_123",
        )

        self.assertIsNotNone(log_id)
        call_args = self.collection.insert_one.call_args[0][0]
        self.assertEqual(call_args["operation"], "AUGMENT")
        self.assertEqual(call_args["method"], "co_occurrence")
        self.assertEqual(call_args["chunk_id"], "chunk_123")

    def test_log_community_form(self):
        """Test logging community formation operation."""
        logger = TransformationLogger(self.db, enabled=True)
        self.collection.insert_one.return_value.inserted_id = "test_id"

        entities = [
            {"id": "entity_1", "name": "Python"},
            {"id": "entity_2", "name": "Django"},
        ]

        log_id = logger.log_community_form(
            community_id="community_0",
            entities=entities,
            modularity=0.45,
            coherence=0.78,
            algorithm="leiden",
            resolution_parameter=1.0,
            trace_id="trace_123",
        )

        self.assertIsNotNone(log_id)
        call_args = self.collection.insert_one.call_args[0][0]
        self.assertEqual(call_args["operation"], "COMMUNITY")
        self.assertEqual(call_args["stage"], "community_detection")
        self.assertEqual(call_args["community_id"], "community_0")
        self.assertEqual(call_args["entity_count"], 2)
        self.assertEqual(call_args["modularity"], 0.45)
        self.assertEqual(call_args["algorithm"], "leiden")

    def test_log_entity_cluster(self):
        """Test logging entity cluster assignment operation."""
        logger = TransformationLogger(self.db, enabled=True)
        self.collection.insert_one.return_value.inserted_id = "test_id"

        entity = {"id": "entity_123", "name": "Python"}

        log_id = logger.log_entity_cluster(
            entity=entity,
            community_id="community_0",
            reason="high_edge_weight",
            neighbors=5,
            trace_id="trace_123",
        )

        self.assertIsNotNone(log_id)
        call_args = self.collection.insert_one.call_args[0][0]
        self.assertEqual(call_args["operation"], "CLUSTER")
        self.assertEqual(call_args["community_id"], "community_0")
        self.assertEqual(call_args["reason"], "high_edge_weight")

    def test_logging_disabled(self):
        """Test that logging returns None when disabled."""
        logger = TransformationLogger(self.db, enabled=False)

        entity = {"id": "entity_123", "name": "Python"}

        log_id = logger.log_entity_create(
            entity=entity,
            entity_type="TECHNOLOGY",
            sources=5,
            confidence=0.92,
            trace_id="trace_123",
        )

        self.assertIsNone(log_id)
        self.assertFalse(self.collection.insert_one.called)

    def test_get_transformations_by_trace_id(self):
        """Test querying transformations by trace_id."""
        logger = TransformationLogger(self.db, enabled=True)

        # Mock cursor
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.__iter__.return_value = [
            {"trace_id": "trace_123", "operation": "MERGE"},
            {"trace_id": "trace_123", "operation": "CREATE"},
        ]
        self.collection.find.return_value = mock_cursor

        results = logger.get_transformations_by_trace_id("trace_123")

        self.assertEqual(len(results), 2)
        self.collection.find.assert_called_once_with({"trace_id": "trace_123"})

    def test_get_transformations_by_entity_id(self):
        """Test querying transformations by entity_id."""
        logger = TransformationLogger(self.db, enabled=True)

        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.__iter__.return_value = [
            {"entity.id": "entity_123", "operation": "CREATE"},
        ]
        self.collection.find.return_value = mock_cursor

        results = logger.get_transformations_by_entity_id("entity_123")

        self.assertEqual(len(results), 1)
        # Verify query includes entity_id in multiple fields
        call_args = self.collection.find.call_args[0][0]
        self.assertIn("$or", call_args)

    def test_get_transformations_by_stage(self):
        """Test querying transformations by stage."""
        logger = TransformationLogger(self.db, enabled=True)

        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.__iter__.return_value = [
            {"stage": "entity_resolution", "operation": "MERGE"},
        ]
        self.collection.find.return_value = mock_cursor

        results = logger.get_transformations_by_stage("entity_resolution")

        self.assertEqual(len(results), 1)
        self.collection.find.assert_called_once_with({"stage": "entity_resolution"})

    def test_get_transformation_logger_function(self):
        """Test get_transformation_logger factory function."""
        with patch.dict("os.environ", {"GRAPHRAG_TRANSFORMATION_LOGGING": "true"}):
            logger = get_transformation_logger(self.db, enabled=True)
            self.assertIsInstance(logger, TransformationLogger)
            self.assertTrue(logger.enabled)

    def test_get_transformation_logger_disabled_by_env(self):
        """Test that logger respects environment variable."""
        with patch.dict("os.environ", {"GRAPHRAG_TRANSFORMATION_LOGGING": "false"}):
            logger = get_transformation_logger(self.db, enabled=True)
            self.assertFalse(logger.enabled)


if __name__ == "__main__":
    unittest.main()


