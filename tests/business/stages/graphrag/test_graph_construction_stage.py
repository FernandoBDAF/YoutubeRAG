"""
Tests for Graph Construction Stage.

Run with: python -m tests.business.stages.graphrag.test_graph_construction_stage
"""

from unittest.mock import MagicMock, Mock


def test_get_construction_stats():
    """Test get_construction_stats function (used by pipeline)."""
    from business.stages.graphrag.graph_construction import GraphConstructionStage

    stage = GraphConstructionStage()

    # Mock config
    stage.config = Mock()
    stage.config.read_db_name = "test_db"
    stage.config.read_coll = "test_chunks"

    # Mock chunks collection
    mock_chunks = MagicMock()
    mock_chunks.count_documents.side_effect = [
        150,  # total_resolved
        140,  # constructed_chunks
        2,  # failed_chunks
    ]

    # Mock relations collection
    mock_relations = MagicMock()
    mock_relations.count_documents.return_value = 500  # total_relationships

    # Mock graphrag_collections
    stage.graphrag_collections = {"relations": mock_relations}

    stage.get_collection = lambda name, io, db_name: mock_chunks

    # Execute
    stats = stage.get_construction_stats()

    # Verify
    assert stats["total_resolved_chunks"] == 150
    assert stats["constructed_chunks"] == 140
    assert stats["failed_chunks"] == 2
    assert stats["pending_chunks"] == 8  # 150 - 140 - 2
    assert stats["total_relationships"] == 500

    print("✓ get_construction_stats returns correct statistics")


def run_all_tests():
    """Run all tests."""
    print("=== Testing Graph Construction Stage ===\n")

    test_get_construction_stats()

    print("\n✅ All graph construction stage tests passed!")


if __name__ == "__main__":
    run_all_tests()
