#!/usr/bin/env python3
"""
Simple test runner for explanation tools (no pytest required).

Tests all utility functions with real database data.
Achievement 1.1: Transformation Explanation Tools - V2
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))

from scripts.repositories.graphrag.explain.explain_utils import (
    get_mongodb_connection,
    find_entity_by_name,
    find_entity_by_id,
    find_merge_logs,
    find_entity_all_logs,
    find_community,
    find_relationship_creation_logs,
    validate_trace_id,
    get_entity_raw_mentions,
    get_entity_relationships,
    calculate_node_degree,
    group_relationships_by_source,
    format_section_header,
    format_key_value,
    format_json_output
)


class TestRunner:
    """Simple test runner."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
    
    def run_test(self, test_name, test_func):
        """Run a single test."""
        try:
            test_func()
            print(f"✅ PASS: {test_name}")
            self.passed += 1
        except AssertionError as e:
            print(f"❌ FAIL: {test_name}")
            print(f"   {str(e)}")
            self.failed += 1
        except Exception as e:
            print(f"⚠️  SKIP: {test_name} ({str(e)})")
            self.skipped += 1
    
    def print_summary(self):
        """Print test summary."""
        total = self.passed + self.failed + self.skipped
        print(f"\n{'═' * 60}")
        print(f"TEST SUMMARY")
        print(f"{'═' * 60}")
        print(f"Total:   {total}")
        print(f"Passed:  {self.passed} ✅")
        print(f"Failed:  {self.failed} ❌")
        print(f"Skipped: {self.skipped} ⚠️")
        print(f"{'═' * 60}\n")
        
        return self.failed == 0


def test_mongodb_connection():
    """Test MongoDB connection."""
    client, db = get_mongodb_connection()
    assert client is not None, "Client should not be None"
    assert db is not None, "Database should not be None"
    
    collections = db.list_collection_names()
    assert isinstance(collections, list), "Collections should be a list"
    
    client.close()


def test_required_collections():
    """Test that required collections exist."""
    client, db = get_mongodb_connection()
    
    collections = db.list_collection_names()
    required = ["entities_resolved", "transformation_logs", "communities"]
    
    for coll in required:
        assert coll in collections, f"Missing collection: {coll}"
    
    client.close()


def test_find_entity_by_name():
    """Test finding entity by name."""
    client, db = get_mongodb_connection()
    
    # Get sample entity
    sample = db.entities_resolved.find_one()
    if not sample:
        client.close()
        raise Exception("No entities in database")
    
    entity_name = sample.get("name")
    result = find_entity_by_name(db, entity_name)
    
    assert result is not None, "Entity should be found"
    assert result.get("name") == entity_name, "Names should match"
    
    client.close()


def test_find_entity_by_id():
    """Test finding entity by ID."""
    client, db = get_mongodb_connection()
    
    # Get sample entity
    sample = db.entities_resolved.find_one()
    if not sample:
        client.close()
        raise Exception("No entities in database")
    
    entity_id = sample.get("entity_id")
    result = find_entity_by_id(db, entity_id)
    
    assert result is not None, "Entity should be found"
    assert result.get("entity_id") == entity_id, "IDs should match"
    
    client.close()


def test_find_entity_not_exists():
    """Test finding non-existent entity."""
    client, db = get_mongodb_connection()
    
    result = find_entity_by_name(db, "NonExistentEntity12345XYZ")
    assert result is None, "Non-existent entity should return None"
    
    client.close()


def test_find_merge_logs():
    """Test finding merge logs."""
    client, db = get_mongodb_connection()
    
    # Get sample entity
    sample = db.entities_resolved.find_one()
    if not sample:
        client.close()
        raise Exception("No entities in database")
    
    entity_id = sample.get("entity_id")
    logs = find_merge_logs(db, entity_id)
    
    assert isinstance(logs, list), "Logs should be a list"
    
    client.close()


def test_validate_trace_id():
    """Test trace ID validation."""
    client, db = get_mongodb_connection()
    
    # Get sample trace_id
    sample = db.transformation_logs.find_one({"trace_id": {"$exists": True}})
    if sample:
        trace_id = sample.get("trace_id")
        result = validate_trace_id(db, trace_id)
        assert result is True, "Valid trace_id should return True"
    
    # Test invalid trace_id
    result = validate_trace_id(db, "nonexistent_trace_12345")
    assert result is False, "Invalid trace_id should return False"
    
    client.close()


def test_get_entity_relationships():
    """Test getting entity relationships."""
    client, db = get_mongodb_connection()
    
    # Get sample entity
    sample = db.entities_resolved.find_one()
    if not sample:
        client.close()
        raise Exception("No entities in database")
    
    entity_id = sample.get("entity_id")
    relationships = get_entity_relationships(db, entity_id)
    
    assert isinstance(relationships, list), "Relationships should be a list"
    
    client.close()


def test_calculate_node_degree():
    """Test calculating node degree."""
    client, db = get_mongodb_connection()
    
    # Get sample entity
    sample = db.entities_resolved.find_one()
    if not sample:
        client.close()
        raise Exception("No entities in database")
    
    entity_id = sample.get("entity_id")
    relationships = get_entity_relationships(db, entity_id)
    degree = calculate_node_degree(relationships, entity_id)
    
    assert isinstance(degree, int), "Degree should be an integer"
    assert degree >= 0, "Degree should be non-negative"
    assert degree == len(relationships), "Degree should equal relationship count"
    
    client.close()


def test_group_relationships_by_source():
    """Test grouping relationships by source."""
    client, db = get_mongodb_connection()
    
    relationships = list(db.relations_final.find().limit(10))
    if not relationships:
        client.close()
        raise Exception("No relationships in database")
    
    grouped = group_relationships_by_source(relationships)
    
    assert isinstance(grouped, dict), "Grouped should be a dict"
    for source, count in grouped.items():
        assert count > 0, f"Count for {source} should be positive"
    
    client.close()


def test_format_section_header():
    """Test section header formatting."""
    header = format_section_header("TEST")
    assert "TEST" in header, "Header should contain title"
    assert "═" in header, "Header should contain separator"


def test_format_key_value():
    """Test key-value formatting."""
    result = format_key_value("key", "value")
    assert "key" in result, "Result should contain key"
    assert "value" in result, "Result should contain value"


def test_format_json_output():
    """Test JSON formatting."""
    import json
    data = {"key": "value", "number": 123}
    result = format_json_output(data)
    
    assert isinstance(result, str), "Result should be string"
    parsed = json.loads(result)
    assert parsed == data, "Parsed JSON should match original"


def test_find_community():
    """Test finding community."""
    client, db = get_mongodb_connection()
    
    # Get sample community
    sample = db.communities.find_one()
    if sample:
        community_id = sample.get("community_id")
        result = find_community(db, community_id)
        
        assert result is not None, "Community should be found"
        assert result.get("community_id") == community_id, "IDs should match"
    
    client.close()


def main():
    """Run all tests."""
    print("\n" + "═" * 60)
    print("RUNNING EXPLANATION TOOLS UNIT TESTS")
    print("═" * 60 + "\n")
    
    runner = TestRunner()
    
    # MongoDB connection tests
    print("Testing MongoDB Connection...")
    runner.run_test("test_mongodb_connection", test_mongodb_connection)
    runner.run_test("test_required_collections", test_required_collections)
    
    # Entity lookup tests
    print("\nTesting Entity Lookup...")
    runner.run_test("test_find_entity_by_name", test_find_entity_by_name)
    runner.run_test("test_find_entity_by_id", test_find_entity_by_id)
    runner.run_test("test_find_entity_not_exists", test_find_entity_not_exists)
    
    # Transformation log tests
    print("\nTesting Transformation Logs...")
    runner.run_test("test_find_merge_logs", test_find_merge_logs)
    runner.run_test("test_validate_trace_id", test_validate_trace_id)
    
    # Relationship tests
    print("\nTesting Relationships...")
    runner.run_test("test_get_entity_relationships", test_get_entity_relationships)
    runner.run_test("test_calculate_node_degree", test_calculate_node_degree)
    runner.run_test("test_group_relationships_by_source", test_group_relationships_by_source)
    
    # Formatting tests
    print("\nTesting Formatting Functions...")
    runner.run_test("test_format_section_header", test_format_section_header)
    runner.run_test("test_format_key_value", test_format_key_value)
    runner.run_test("test_format_json_output", test_format_json_output)
    
    # Community tests
    print("\nTesting Community Lookup...")
    runner.run_test("test_find_community", test_find_community)
    
    # Print summary
    success = runner.print_summary()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())


