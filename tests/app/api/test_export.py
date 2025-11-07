"""
Tests for Graph Export API

Achievement 8.1: Comprehensive Test Suite

Tests for app/api/export.py endpoints.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch

from app.api.export import (
    export_graph_json,
    export_graph_csv,
    export_graph_graphml,
    export_graph_gexf,
    ExportHandler,
)


class TestExportAPI(unittest.TestCase):
    """Test export API functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.db_name = "test_db"
        self.entity_ids = ["entity_1", "entity_2"]

    @patch("app.api.export.get_mongo_client")
    def test_export_graph_json_community_not_found(self, mock_get_client):
        """Test exporting community graph when community not found."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_db = MagicMock()
        mock_client.__getitem__ = Mock(return_value=mock_db)

        collections = {
            "entities": MagicMock(),
            "relations": MagicMock(),
            "communities": MagicMock(),
        }
        collections["communities"].find_one.return_value = None

        from app.api.export import get_graphrag_collections
        with patch("app.api.export.get_graphrag_collections", return_value=collections):
            result = export_graph_json(self.db_name, community_id="nonexistent")
            self.assertIn("error", result)

    @patch("app.api.export.get_mongo_client")
    def test_export_graph_json_success(self, mock_get_client):
        """Test successfully exporting graph as JSON."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_db = MagicMock()
        mock_client.__getitem__ = Mock(return_value=mock_db)

        # Mock collections
        entities_collection = MagicMock()
        relations_collection = MagicMock()

        entities_collection.find.return_value = [
            {
                "entity_id": "entity_1",
                "name": "Entity 1",
                "type": "PERSON",
            }
        ]

        relations_collection.find.return_value = []

        collections = {
            "entities": entities_collection,
            "relations": relations_collection,
        }

        from app.api.export import get_graphrag_collections
        with patch("app.api.export.get_graphrag_collections", return_value=collections):
            result = export_graph_json(self.db_name, entity_ids=self.entity_ids)
            self.assertNotIn("error", result)
            self.assertIn("nodes", result)
            self.assertIn("links", result)
            self.assertIn("metadata", result)

    def test_export_graph_csv_format(self):
        """Test CSV export format."""
        graph_data = {
            "nodes": [
                {
                    "id": "entity_1",
                    "name": "Entity 1",
                    "type": "PERSON",
                }
            ],
            "links": [
                {
                    "source": "entity_1",
                    "target": "entity_2",
                    "predicate": "knows",
                    "confidence": 0.9,
                }
            ],
        }

        with patch("app.api.export.export_graph_json", return_value=graph_data):
            csv_result = export_graph_csv(self.db_name, entity_ids=self.entity_ids)
            self.assertIn("Nodes:", csv_result)
            self.assertIn("Links:", csv_result)
            self.assertIn("entity_1", csv_result)

    def test_export_graph_graphml_format(self):
        """Test GraphML export format."""
        graph_data = {
            "nodes": [
                {
                    "id": "entity_1",
                    "name": "Entity 1",
                    "type": "PERSON",
                }
            ],
            "links": [
                {
                    "source": "entity_1",
                    "target": "entity_2",
                    "predicate": "knows",
                    "confidence": 0.9,
                }
            ],
        }

        with patch("app.api.export.export_graph_json", return_value=graph_data):
            graphml_result = export_graph_graphml(self.db_name, entity_ids=self.entity_ids)
            self.assertIn("<?xml", graphml_result)
            self.assertIn("<graphml", graphml_result)
            self.assertIn("entity_1", graphml_result)

    def test_export_graph_gexf_format(self):
        """Test GEXF export format."""
        graph_data = {
            "nodes": [
                {
                    "id": "entity_1",
                    "name": "Entity 1",
                    "type": "PERSON",
                }
            ],
            "links": [
                {
                    "source": "entity_1",
                    "target": "entity_2",
                    "predicate": "knows",
                    "confidence": 0.9,
                }
            ],
        }

        with patch("app.api.export.export_graph_json", return_value=graph_data):
            gexf_result = export_graph_gexf(self.db_name, entity_ids=self.entity_ids)
            self.assertIn("<?xml", gexf_result)
            self.assertIn("<gexf", gexf_result)
            self.assertIn("entity_1", gexf_result)


def run_all_tests():
    """Run all export API tests."""
    print("Testing Graph Export API")
    print("=" * 60)
    print()

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestExportAPI))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 60)
    if result.wasSuccessful():
        print("✅ All export API tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
    print("=" * 60)

    return result.wasSuccessful()


if __name__ == "__main__":
    run_all_tests()

