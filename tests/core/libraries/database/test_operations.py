"""
Tests for database library operations with MongoDB mocking.

Run with: python -m tests.core.libraries.database.test_operations
"""

from unittest.mock import MagicMock, Mock
from pymongo.errors import BulkWriteError

from core.libraries.database import batch_insert, batch_update, batch_delete


def test_batch_insert_success():
    """Test successful batch insert."""
    # Mock collection
    mock_collection = MagicMock()
    mock_collection.name = "test_collection"

    # Mock successful insert_many
    mock_result = Mock()
    mock_result.inserted_ids = ["id1", "id2", "id3"]
    mock_collection.insert_many.return_value = mock_result

    # Test data
    documents = [
        {"name": "doc1"},
        {"name": "doc2"},
        {"name": "doc3"},
    ]

    # Execute
    result = batch_insert(mock_collection, documents, batch_size=10)

    # Verify
    assert result["total"] == 3
    assert result["inserted"] == 3
    assert result["failed"] == 0
    assert result["success_rate"] == 100.0
    assert len(result["errors"]) == 0

    print("✓ batch_insert success case")


def test_batch_insert_partial_failure():
    """Test batch insert with partial failures."""
    mock_collection = MagicMock()
    mock_collection.name = "test_collection"

    # Mock BulkWriteError (some docs inserted, some failed)
    bulk_error = BulkWriteError(
        {"nInserted": 2, "writeErrors": [{"index": 2, "errmsg": "duplicate key"}]}
    )
    mock_collection.insert_many.side_effect = bulk_error

    documents = [{"id": 1}, {"id": 2}, {"id": 3}]

    result = batch_insert(mock_collection, documents, batch_size=10, ordered=False)

    assert result["total"] == 3
    assert result["inserted"] == 2
    assert result["failed"] == 1
    assert len(result["errors"]) > 0

    print("✓ batch_insert partial failure handling")


def test_batch_insert_with_batching():
    """Test batch insert splits into multiple batches."""
    mock_collection = MagicMock()
    mock_collection.name = "test_collection"

    # Mock successful inserts - return different counts for each batch
    def mock_insert_many(docs, ordered):
        result = Mock()
        result.inserted_ids = [f"id{i}" for i in range(len(docs))]
        return result

    mock_collection.insert_many.side_effect = mock_insert_many

    # 5 documents with batch_size=2 should make 3 calls (2+2+1)
    documents = [{"id": i} for i in range(5)]

    result = batch_insert(mock_collection, documents, batch_size=2)

    assert result["total"] == 5
    assert result["inserted"] == 5  # 2+2+1
    assert mock_collection.insert_many.call_count == 3  # 3 batches

    print("✓ batch_insert batching logic")


def test_batch_update_success():
    """Test successful batch update."""
    mock_collection = MagicMock()
    mock_collection.name = "test_collection"

    # Mock successful bulk_write
    mock_result = Mock()
    mock_result.matched_count = 3
    mock_result.modified_count = 2
    mock_result.upserted_count = 0
    mock_collection.bulk_write.return_value = mock_result

    updates = [
        {"filter": {"_id": "1"}, "update": {"$set": {"status": "done"}}},
        {"filter": {"_id": "2"}, "update": {"$set": {"status": "done"}}},
        {"filter": {"_id": "3"}, "update": {"$set": {"status": "done"}}},
    ]

    result = batch_update(mock_collection, updates, batch_size=10)

    assert result["total"] == 3
    assert result["matched"] == 3
    assert result["modified"] == 2
    assert result["failed"] == 0

    print("✓ batch_update success case")


def test_batch_update_with_upsert():
    """Test batch update with upsert."""
    mock_collection = MagicMock()
    mock_collection.name = "test_collection"

    mock_result = Mock()
    mock_result.matched_count = 1
    mock_result.modified_count = 1
    mock_result.upserted_count = 2  # 2 new documents
    mock_collection.bulk_write.return_value = mock_result

    updates = [
        {"filter": {"_id": "1"}, "update": {"$set": {"val": "a"}}, "upsert": True},
        {"filter": {"_id": "2"}, "update": {"$set": {"val": "b"}}, "upsert": True},
        {"filter": {"_id": "3"}, "update": {"$set": {"val": "c"}}, "upsert": True},
    ]

    result = batch_update(mock_collection, updates, upsert=True)

    assert result["upserted"] == 2
    assert result["modified"] == 1

    print("✓ batch_update with upsert")


def test_batch_delete_success():
    """Test successful batch delete."""
    mock_collection = MagicMock()
    mock_collection.name = "test_collection"

    mock_result = Mock()
    mock_result.deleted_count = 3
    mock_collection.bulk_write.return_value = mock_result

    filters = [
        {"_id": "1"},
        {"_id": "2"},
        {"_id": "3"},
    ]

    result = batch_delete(mock_collection, filters, batch_size=10)

    assert result["total"] == 3
    assert result["deleted"] == 3
    assert result["failed"] == 0

    print("✓ batch_delete success case")


def test_batch_delete_with_errors():
    """Test batch delete with errors."""
    mock_collection = MagicMock()
    mock_collection.name = "test_collection"

    # First batch succeeds, second fails
    mock_result = Mock()
    mock_result.deleted_count = 2
    mock_collection.bulk_write.side_effect = [
        mock_result,  # First batch succeeds
        Exception("Connection error"),  # Second batch fails
    ]

    filters = [{"_id": str(i)} for i in range(5)]

    result = batch_delete(mock_collection, filters, batch_size=2)

    assert result["total"] == 5
    assert result["deleted"] == 2  # Only first batch
    assert result["failed"] > 0

    print("✓ batch_delete error handling")


def test_batch_operations_empty_list():
    """Test batch operations with empty lists."""
    mock_collection = MagicMock()

    # Empty insert
    result = batch_insert(mock_collection, [], batch_size=10)
    assert result["total"] == 0
    assert result["inserted"] == 0

    # Empty update
    result = batch_update(mock_collection, [], batch_size=10)
    assert result["total"] == 0

    # Empty delete
    result = batch_delete(mock_collection, [], batch_size=10)
    assert result["total"] == 0

    print("✓ batch operations handle empty lists")


def test_batch_insert_ordered_vs_unordered():
    """Test ordered vs unordered insert behavior."""
    mock_collection = MagicMock()
    mock_collection.name = "test_collection"

    mock_result = Mock()
    mock_result.inserted_ids = ["id1", "id2"]
    mock_collection.insert_many.return_value = mock_result

    documents = [{"id": 1}, {"id": 2}]

    # Test ordered=True
    batch_insert(mock_collection, documents, ordered=True)
    call_args = mock_collection.insert_many.call_args
    assert call_args[1]["ordered"] == True

    # Test ordered=False
    batch_insert(mock_collection, documents, ordered=False)
    call_args = mock_collection.insert_many.call_args
    assert call_args[1]["ordered"] == False

    print("✓ batch_insert ordered parameter working")


def run_all_tests():
    """Run all tests."""
    print("=== Testing Database Library ===\n")

    test_batch_insert_success()
    test_batch_insert_partial_failure()
    test_batch_insert_with_batching()
    test_batch_update_success()
    test_batch_update_with_upsert()
    test_batch_delete_success()
    test_batch_delete_with_errors()
    test_batch_operations_empty_list()
    test_batch_insert_ordered_vs_unordered()

    print("\n✅ All database tests passed!")
    print("\n📊 Summary:")
    print("  • batch_insert: Tested with success, partial failure, batching")
    print("  • batch_update: Tested with success, upsert")
    print("  • batch_delete: Tested with success, errors")
    print("  • Edge cases: Empty lists, ordered parameter")


if __name__ == "__main__":
    run_all_tests()
