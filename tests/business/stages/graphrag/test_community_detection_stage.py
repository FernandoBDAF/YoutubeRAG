"""
Tests for Community Detection Stage.

Run with: python -m tests.business.stages.graphrag.test_community_detection_stage
"""

from unittest.mock import MagicMock, Mock


def test_get_detection_stats():
    """Test get_detection_stats function (used by pipeline)."""
    from business.stages.graphrag.community_detection import CommunityDetectionStage

    stage = CommunityDetectionStage()

    # Mock config
    stage.config = Mock()
    stage.config.read_db_name = "test_db"
    stage.config.read_coll = "test_chunks"

    # Mock chunks collection
    mock_chunks = MagicMock()
    mock_chunks.count_documents.side_effect = [
        200,  # total_constructed
        180,  # detected_chunks
        5,  # failed_chunks
    ]

    # Mock communities collection
    mock_communities = MagicMock()
    mock_communities.count_documents.return_value = 15  # total_communities

    # Mock aggregation for level distribution
    mock_communities.aggregate.return_value = [
        {"_id": 1, "count": 10},
        {"_id": 2, "count": 5},
    ]

    # Mock graphrag_collections
    stage.graphrag_collections = {"communities": mock_communities}

    stage.get_collection = lambda name, io, db_name: mock_chunks

    # Execute
    stats = stage.get_detection_stats()

    # Verify
    assert stats["total_constructed_chunks"] == 200
    assert stats["detected_chunks"] == 180
    assert stats["failed_chunks"] == 5
    assert stats["pending_chunks"] == 15  # 200 - 180 - 5
    assert stats["total_communities"] == 15
    assert stats["level_distribution"] == {"1": 10, "2": 5}

    print("✓ get_detection_stats returns correct statistics")


def run_all_tests():
    """Run all tests."""
    print("=== Testing Community Detection Stage ===\n")

    test_get_detection_stats()

    print("\n✅ All community detection stage tests passed!")


if __name__ == "__main__":
    run_all_tests()
