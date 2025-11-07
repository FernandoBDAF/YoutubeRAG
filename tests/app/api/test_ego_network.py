"""
Tests for Ego Network API

Achievement 8.1: Comprehensive Test Suite

Tests for app/api/ego_network.py endpoints.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch

from app.api.ego_network import get_ego_network, EgoNetworkHandler


class TestEgoNetworkAPI(unittest.TestCase):
    """Test ego network API functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.db_name = "test_db"
        self.entity_id = "entity_123"

    @patch("app.api.ego_network.get_mongo_client")
    def test_get_ego_network_entity_not_found(self, mock_get_client):
        """Test getting ego network for non-existent entity."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_db = MagicMock()
        mock_client.__getitem__ = Mock(return_value=mock_db)
        collections = {
            "entities": MagicMock(),
            "relations": MagicMock(),
        }
        collections["entities"].find_one.return_value = None

        from app.api.ego_network import get_graphrag_collections
        with patch("app.api.ego_network.get_graphrag_collections", return_value=collections):
            result = get_ego_network(self.db_name, self.entity_id, max_hops=1, max_nodes=10)
            self.assertIn("error", result)
            self.assertEqual(result["entity_id"], self.entity_id)

    @patch("app.api.ego_network.get_mongo_client")
    def test_get_ego_network_success(self, mock_get_client):
        """Test successfully getting ego network."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_db = MagicMock()
        mock_client.__getitem__ = Mock(return_value=mock_db)

        # Mock collections
        entities_collection = MagicMock()
        relations_collection = MagicMock()

        # Mock center entity
        entities_collection.find_one.return_value = {
            "entity_id": self.entity_id,
            "name": "Test Entity",
            "type": "PERSON",
        }

        # Mock related entities
        entities_collection.find.return_value = [
            {
                "entity_id": "entity_456",
                "name": "Related Entity",
                "type": "ORGANIZATION",
            }
        ]

        # Mock relationships
        relations_collection.find.return_value = [
            {
                "subject_id": self.entity_id,
                "object_id": "entity_456",
                "predicate": "works_for",
                "confidence": 0.9,
            }
        ]

        collections = {
            "entities": entities_collection,
            "relations": relations_collection,
        }

        from app.api.ego_network import get_graphrag_collections
        with patch("app.api.ego_network.get_graphrag_collections", return_value=collections):
            result = get_ego_network(self.db_name, self.entity_id, max_hops=1, max_nodes=10)
            self.assertNotIn("error", result)
            self.assertEqual(result["center_entity"]["entity_id"], self.entity_id)
            self.assertGreaterEqual(len(result["nodes"]), 1)
            self.assertGreaterEqual(len(result["links"]), 0)


def run_all_tests():
    """Run all ego network API tests."""
    print("Testing Ego Network API")
    print("=" * 60)
    print()

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestEgoNetworkAPI))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 60)
    if result.wasSuccessful():
        print("✅ All ego network API tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
    print("=" * 60)

    return result.wasSuccessful()


if __name__ == "__main__":
    run_all_tests()

