"""
Tests for Entity Resolution Stage.

Run with: python -m tests.business.stages.graphrag.test_entity_resolution_stage
"""

from unittest.mock import MagicMock, Mock


def test_get_resolution_stats():
    """Test get_resolution_stats function (used by pipeline)."""
    from business.stages.graphrag.entity_resolution import EntityResolutionStage

    stage = EntityResolutionStage()

    # Mock config
    stage.config = Mock()
    stage.config.read_db_name = "test_db"
    stage.config.read_coll = "test_chunks"

    # Mock collections
    mock_chunks = MagicMock()
    mock_chunks.count_documents.side_effect = [
        100,  # total_extracted
        85,  # resolved_chunks
        3,  # failed_chunks
    ]

    mock_entities = MagicMock()
    mock_entities.count_documents.return_value = 250  # total_entities

    mock_mentions = MagicMock()
    mock_mentions.count_documents.return_value = 1000  # total_mentions

    # Mock graphrag_collections
    stage.graphrag_collections = {
        "entities": mock_entities,
        "entity_mentions": mock_mentions,
    }

    def mock_get_collection(name, io, db_name):
        return mock_chunks

    stage.get_collection = mock_get_collection

    # Execute
    stats = stage.get_resolution_stats()

    # Verify
    assert stats["total_extracted_chunks"] == 100
    assert stats["resolved_chunks"] == 85
    assert stats["failed_chunks"] == 3
    assert stats["pending_chunks"] == 12  # 100 - 85 - 3
    assert stats["total_entities"] == 250
    assert stats["total_mentions"] == 1000

    print("✓ get_resolution_stats returns correct statistics")


def run_all_tests():
    """Run all tests."""
    print("=== Testing Entity Resolution Stage ===\n")

    test_get_resolution_stats()

    print("\n✅ All entity resolution stage tests passed!")


if __name__ == "__main__":
    run_all_tests()
