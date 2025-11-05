"""
Tests for Graph Extraction Stage.

Run with: python -m tests.business.stages.graphrag.test_extraction_stage
"""

from unittest.mock import MagicMock, Mock


def test_get_processing_stats():
    """Test get_processing_stats function (used by pipeline)."""
    from business.stages.graphrag.extraction import GraphExtractionStage

    # Create stage
    stage = GraphExtractionStage()

    # Mock config
    stage.config = Mock()
    stage.config.read_db_name = "test_db"
    stage.config.read_coll = "test_chunks"

    # Mock collection
    mock_collection = MagicMock()
    mock_collection.count_documents.side_effect = [
        100,  # total_chunks
        80,  # processed_chunks
        5,  # failed_chunks
    ]

    stage.get_collection = lambda name, io, db_name: mock_collection

    # Execute
    stats = stage.get_processing_stats()

    # Verify
    assert stats["total_chunks"] == 100
    assert stats["processed_chunks"] == 80
    assert stats["failed_chunks"] == 5
    assert stats["pending_chunks"] == 15  # 100 - 80 - 5
    assert stats["completion_rate"] == 0.8  # 80/100

    print("✓ get_processing_stats returns correct statistics")


def run_all_tests():
    """Run all tests."""
    print("=== Testing Graph Extraction Stage ===\n")

    test_get_processing_stats()

    print("\n✅ All extraction stage tests passed!")


if __name__ == "__main__":
    run_all_tests()
