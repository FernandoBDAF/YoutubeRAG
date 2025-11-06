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


def test_handle_doc_skips_empty_chunk():
    """Test that empty chunks are skipped gracefully."""
    from business.stages.graphrag.extraction import GraphExtractionStage

    stage = GraphExtractionStage()
    stage.config = Mock()
    stage.config.write_db_name = "test_db"
    stage.config.write_coll = "test_chunks"
    stage.config.model_name = "gpt-4o-mini"
    stage.config.upsert_existing = False
    stage.stats = {"skipped": 0, "failed": 0, "updated": 0}

    # Mock collection for writing
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = None  # No existing document
    stage.get_collection = lambda name, io, db_name: mock_collection

    # Test chunk with empty text
    doc = {
        "chunk_id": "test-123",
        "video_id": "video-123",
        "chunk_text": "",  # Empty
    }

    # Execute
    result = stage.handle_doc(doc)

    # Verify - should mark as skipped, not failed
    assert result is None
    assert mock_collection.update_one.called
    update_call = mock_collection.update_one.call_args
    assert update_call[0][1]["$set"]["graphrag_extraction"]["status"] == "skipped"
    assert update_call[0][1]["$set"]["graphrag_extraction"]["reason"] == "chunk_empty"
    assert stage.stats["skipped"] == 1

    print("✓ handle_doc skips empty chunks gracefully")


def test_handle_doc_skips_short_chunk():
    """Test that chunks shorter than 20 chars are skipped."""
    from business.stages.graphrag.extraction import GraphExtractionStage

    stage = GraphExtractionStage()
    stage.config = Mock()
    stage.config.write_db_name = "test_db"
    stage.config.write_coll = "test_chunks"
    stage.config.model_name = "gpt-4o-mini"
    stage.config.upsert_existing = False
    stage.stats = {"skipped": 0, "failed": 0, "updated": 0}

    # Mock collection for writing
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = None  # No existing document
    stage.get_collection = lambda name, io, db_name: mock_collection

    # Test chunk with very short text (like the failing chunks)
    doc = {
        "chunk_id": "test-123",
        "video_id": "video-123",
        "chunk_text": ".",  # Just 1 char
    }

    # Execute
    result = stage.handle_doc(doc)

    # Verify - should mark as skipped
    assert result is None
    assert mock_collection.update_one.called
    update_call = mock_collection.update_one.call_args
    assert update_call[0][1]["$set"]["graphrag_extraction"]["status"] == "skipped"
    assert (
        update_call[0][1]["$set"]["graphrag_extraction"]["reason"] == "chunk_noise_only"
    )
    assert stage.stats["skipped"] == 1

    print("✓ handle_doc skips very short chunks gracefully")


def test_handle_doc_skips_noise_only_chunk():
    """Test that chunks with only punctuation are skipped."""
    from business.stages.graphrag.extraction import GraphExtractionStage

    stage = GraphExtractionStage()
    stage.config = Mock()
    stage.config.write_db_name = "test_db"
    stage.config.write_coll = "test_chunks"
    stage.config.model_name = "gpt-4o-mini"
    stage.config.upsert_existing = False
    stage.stats = {"skipped": 0, "failed": 0, "updated": 0}

    # Mock collection for writing
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = None  # No existing document
    stage.get_collection = lambda name, io, db_name: mock_collection

    # Test chunk with only punctuation (like ". That's it, it's a 0" but shorter)
    doc = {
        "chunk_id": "test-123",
        "video_id": "video-123",
        "chunk_text": ". ! ?",  # Only punctuation
    }

    # Execute
    result = stage.handle_doc(doc)

    # Verify - should mark as skipped
    assert result is None
    assert mock_collection.update_one.called
    update_call = mock_collection.update_one.call_args
    assert update_call[0][1]["$set"]["graphrag_extraction"]["status"] == "skipped"
    assert (
        update_call[0][1]["$set"]["graphrag_extraction"]["reason"] == "chunk_noise_only"
    )
    assert stage.stats["skipped"] == 1

    print("✓ handle_doc skips noise-only chunks gracefully")


def test_handle_doc_skips_fragment_chunk():
    """Test that chunks between 20-50 chars (fragments) are skipped when no entities."""
    from business.stages.graphrag.extraction import GraphExtractionStage

    stage = GraphExtractionStage()
    stage.config = Mock()
    stage.config.write_db_name = "test_db"
    stage.config.write_coll = "test_chunks"
    stage.config.model_name = "gpt-4o-mini"
    stage.config.upsert_existing = False
    stage.stats = {"skipped": 0, "failed": 0, "updated": 0}

    # Mock extraction agent to return None (no entities)
    mock_agent = MagicMock()
    mock_agent.extract_from_chunk.return_value = None
    stage.extraction_agent = mock_agent

    # Mock collection for writing
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = None  # No existing document
    stage.get_collection = lambda name, io, db_name: mock_collection

    # Test chunk with fragment text (like the failing chunk: ". That's it, it's a 0" - 21 chars)
    # This will pass pre-filter (< 50 chars but >= 20 and has content), then agent returns None
    doc = {
        "chunk_id": "test-123",
        "video_id": "video-123",
        "chunk_text": ". That's it, it's a 0",  # 21 chars - fragment
    }

    # Execute
    result = stage.handle_doc(doc)

    # Verify - should mark as skipped (because text < 100 chars and agent returned None)
    assert result is None
    assert mock_collection.update_one.called
    update_call = mock_collection.update_one.call_args
    assert update_call[0][1]["$set"]["graphrag_extraction"]["status"] == "skipped"
    assert update_call[0][1]["$set"]["graphrag_extraction"]["reason"] == "no_entities"
    assert stage.stats["skipped"] == 1

    print("✓ handle_doc skips fragment chunks gracefully when no entities")


def run_all_tests():
    """Run all tests."""
    print("=== Testing Graph Extraction Stage ===\n")

    test_get_processing_stats()
    test_handle_doc_skips_empty_chunk()
    test_handle_doc_skips_short_chunk()
    test_handle_doc_skips_noise_only_chunk()
    test_handle_doc_skips_fragment_chunk()

    print("\n✅ All extraction stage tests passed!")


if __name__ == "__main__":
    run_all_tests()
