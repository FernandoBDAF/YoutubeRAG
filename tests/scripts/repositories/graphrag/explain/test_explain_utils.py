#!/usr/bin/env python3
"""
Unit tests for explain_utils.py

Tests all utility functions with real database data.
Achievement 1.1: Transformation Explanation Tools - V2
"""

import pytest
import sys
import os
from typing import Optional

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))

from scripts.repositories.graphrag.explain.explain_utils import (
    get_mongodb_connection,
    find_entity_by_name,
    find_entity_by_id,
    find_merge_logs,
    find_relationship_filter_logs,
    find_entity_all_logs,
    find_community,
    find_relationship_creation_logs,
    validate_trace_id,
    get_entity_raw_mentions,
    get_entity_relationships,
    calculate_node_degree,
    group_relationships_by_source,
    format_section_header,
    format_subsection_header,
    format_key_value,
    format_json_output
)


class TestMongoDBConnection:
    """Test MongoDB connection functions."""
    
    def test_get_mongodb_connection(self):
        """Test that we can connect to MongoDB."""
        client, db = get_mongodb_connection()
        assert client is not None
        assert db is not None
        
        # Test that we can query the database
        collections = db.list_collection_names()
        assert isinstance(collections, list)
        
        client.close()
    
    def test_connection_has_required_collections(self):
        """Test that database has required collections."""
        client, db = get_mongodb_connection()
        
        collections = db.list_collection_names()
        
        # Check for key collections
        required_collections = [
            "entities_resolved",
            "transformation_logs",
            "communities"
        ]
        
        for coll in required_collections:
            assert coll in collections, f"Missing collection: {coll}"
        
        client.close()


class TestEntityLookup:
    """Test entity lookup functions."""
    
    @pytest.fixture
    def db(self):
        """Get database connection."""
        client, db = get_mongodb_connection()
        yield db
        client.close()
    
    def test_find_entity_by_name_exists(self, db):
        """Test finding an entity that exists."""
        # Get any entity from database
        sample_entity = db.entities_resolved.find_one()
        
        if sample_entity:
            entity_name = sample_entity.get("name")
            result = find_entity_by_name(db, entity_name)
            
            assert result is not None
            assert result.get("name") == entity_name
    
    def test_find_entity_by_name_not_exists(self, db):
        """Test finding an entity that doesn't exist."""
        result = find_entity_by_name(db, "NonExistentEntity12345XYZ")
        assert result is None
    
    def test_find_entity_by_id_exists(self, db):
        """Test finding an entity by ID that exists."""
        # Get any entity from database
        sample_entity = db.entities_resolved.find_one()
        
        if sample_entity:
            entity_id = sample_entity.get("entity_id")
            result = find_entity_by_id(db, entity_id)
            
            assert result is not None
            assert result.get("entity_id") == entity_id
    
    def test_find_entity_by_id_not_exists(self, db):
        """Test finding an entity by ID that doesn't exist."""
        result = find_entity_by_id(db, "nonexistent_id_12345")
        assert result is None
    
    def test_find_entity_with_trace_id(self, db):
        """Test finding entity with trace_id filter."""
        # Get any entity with trace_id
        sample_entity = db.entities_resolved.find_one({"trace_id": {"$exists": True}})
        
        if sample_entity:
            entity_name = sample_entity.get("name")
            trace_id = sample_entity.get("trace_id")
            
            result = find_entity_by_name(db, entity_name, trace_id)
            
            assert result is not None
            assert result.get("trace_id") == trace_id


class TestTransformationLogs:
    """Test transformation log query functions."""
    
    @pytest.fixture
    def db(self):
        """Get database connection."""
        client, db = get_mongodb_connection()
        yield db
        client.close()
    
    def test_find_merge_logs(self, db):
        """Test finding merge logs for an entity."""
        # Get any entity
        sample_entity = db.entities_resolved.find_one()
        
        if sample_entity:
            entity_id = sample_entity.get("entity_id")
            logs = find_merge_logs(db, entity_id)
            
            assert isinstance(logs, list)
            # Logs may be empty if entity wasn't merged
    
    def test_find_entity_all_logs(self, db):
        """Test finding all logs for an entity."""
        # Get any entity
        sample_entity = db.entities_resolved.find_one()
        
        if sample_entity:
            entity_id = sample_entity.get("entity_id")
            logs = find_entity_all_logs(db, entity_id)
            
            assert isinstance(logs, list)
    
    def test_find_relationship_creation_logs(self, db):
        """Test finding relationship creation logs."""
        # Get any trace_id
        sample_log = db.transformation_logs.find_one({"trace_id": {"$exists": True}})
        
        if sample_log:
            trace_id = sample_log.get("trace_id")
            logs = find_relationship_creation_logs(db, trace_id)
            
            assert isinstance(logs, list)
    
    def test_validate_trace_id_exists(self, db):
        """Test validating a trace_id that exists."""
        # Get any trace_id
        sample_log = db.transformation_logs.find_one({"trace_id": {"$exists": True}})
        
        if sample_log:
            trace_id = sample_log.get("trace_id")
            result = validate_trace_id(db, trace_id)
            
            assert result is True
    
    def test_validate_trace_id_not_exists(self, db):
        """Test validating a trace_id that doesn't exist."""
        result = validate_trace_id(db, "nonexistent_trace_id_12345")
        assert result is False


class TestCommunityLookup:
    """Test community lookup functions."""
    
    @pytest.fixture
    def db(self):
        """Get database connection."""
        client, db = get_mongodb_connection()
        yield db
        client.close()
    
    def test_find_community_exists(self, db):
        """Test finding a community that exists."""
        # Get any community
        sample_community = db.communities.find_one()
        
        if sample_community:
            community_id = sample_community.get("community_id")
            result = find_community(db, community_id)
            
            assert result is not None
            assert result.get("community_id") == community_id
    
    def test_find_community_not_exists(self, db):
        """Test finding a community that doesn't exist."""
        result = find_community(db, "nonexistent_community_12345")
        assert result is None


class TestRelationshipQueries:
    """Test relationship query functions."""
    
    @pytest.fixture
    def db(self):
        """Get database connection."""
        client, db = get_mongodb_connection()
        yield db
        client.close()
    
    def test_get_entity_raw_mentions(self, db):
        """Test getting raw entity mentions."""
        # Get any resolved entity
        sample_entity = db.entities_resolved.find_one()
        
        if sample_entity:
            entity_name = sample_entity.get("name")
            mentions = get_entity_raw_mentions(db, entity_name)
            
            assert isinstance(mentions, list)
    
    def test_get_entity_relationships(self, db):
        """Test getting entity relationships."""
        # Get any entity
        sample_entity = db.entities_resolved.find_one()
        
        if sample_entity:
            entity_id = sample_entity.get("entity_id")
            relationships = get_entity_relationships(db, entity_id)
            
            assert isinstance(relationships, list)
    
    def test_calculate_node_degree(self, db):
        """Test calculating node degree."""
        # Get any entity with relationships
        sample_entity = db.entities_resolved.find_one()
        
        if sample_entity:
            entity_id = sample_entity.get("entity_id")
            relationships = get_entity_relationships(db, entity_id)
            degree = calculate_node_degree(relationships, entity_id)
            
            assert isinstance(degree, int)
            assert degree >= 0
            assert degree == len(relationships)
    
    def test_group_relationships_by_source(self, db):
        """Test grouping relationships by source."""
        # Get some relationships
        relationships = list(db.relations_final.find().limit(10))
        
        if relationships:
            grouped = group_relationships_by_source(relationships)
            
            assert isinstance(grouped, dict)
            # Check that counts are positive
            for source, count in grouped.items():
                assert count > 0


class TestFormattingFunctions:
    """Test output formatting functions."""
    
    def test_format_section_header(self):
        """Test section header formatting."""
        header = format_section_header("TEST HEADER")
        
        assert "TEST HEADER" in header
        assert "═" in header
        assert len(header.split("\n")) >= 3
    
    def test_format_subsection_header(self):
        """Test subsection header formatting."""
        header = format_subsection_header("Test Subsection")
        
        assert "Test Subsection" in header
        assert "-" in header
    
    def test_format_key_value_simple(self):
        """Test key-value formatting with simple value."""
        result = format_key_value("key", "value")
        
        assert "key" in result
        assert "value" in result
        assert ":" in result
    
    def test_format_key_value_list(self):
        """Test key-value formatting with list value."""
        result = format_key_value("key", [1, 2, 3, 4, 5])
        
        assert "key" in result
        assert "[" in result
        assert "]" in result
    
    def test_format_key_value_dict(self):
        """Test key-value formatting with dict value."""
        result = format_key_value("key", {"nested": "value"})
        
        assert "key" in result
        assert "nested" in result
    
    def test_format_key_value_with_indent(self):
        """Test key-value formatting with indentation."""
        result = format_key_value("key", "value", indent=4)
        
        assert result.startswith("    ")
    
    def test_format_json_output(self):
        """Test JSON output formatting."""
        data = {
            "key1": "value1",
            "key2": 123,
            "key3": [1, 2, 3]
        }
        
        result = format_json_output(data)
        
        assert isinstance(result, str)
        # Should be valid JSON
        import json
        parsed = json.loads(result)
        assert parsed == data


class TestRealDataIntegration:
    """Integration tests with real database data."""
    
    @pytest.fixture
    def db(self):
        """Get database connection."""
        client, db = get_mongodb_connection()
        yield db
        client.close()
    
    def test_full_entity_lookup_workflow(self, db):
        """Test complete entity lookup workflow."""
        # Get a real entity
        sample_entity = db.entities_resolved.find_one()
        
        if sample_entity:
            entity_name = sample_entity.get("name")
            entity_id = sample_entity.get("entity_id")
            
            # Test lookup by name
            by_name = find_entity_by_name(db, entity_name)
            assert by_name is not None
            
            # Test lookup by ID
            by_id = find_entity_by_id(db, entity_id)
            assert by_id is not None
            
            # Both should return same entity
            assert by_name.get("entity_id") == by_id.get("entity_id")
    
    def test_full_relationship_workflow(self, db):
        """Test complete relationship workflow."""
        # Get a real entity with relationships
        sample_entity = db.entities_resolved.find_one()
        
        if sample_entity:
            entity_id = sample_entity.get("entity_id")
            
            # Get relationships
            relationships = get_entity_relationships(db, entity_id)
            
            # Calculate degree
            degree = calculate_node_degree(relationships, entity_id)
            
            # Group by source
            if relationships:
                grouped = group_relationships_by_source(relationships)
                
                # Verify totals match
                total = sum(grouped.values())
                assert total == len(relationships)
    
    def test_trace_id_workflow(self, db):
        """Test trace_id filtering workflow."""
        # Get a real trace_id
        sample_log = db.transformation_logs.find_one({"trace_id": {"$exists": True}})
        
        if sample_log:
            trace_id = sample_log.get("trace_id")
            
            # Validate trace_id
            assert validate_trace_id(db, trace_id) is True
            
            # Get entities for this trace
            entities = list(db.entities_resolved.find({"trace_id": trace_id}).limit(5))
            
            if entities:
                # Test entity lookup with trace_id
                entity_name = entities[0].get("name")
                result = find_entity_by_name(db, entity_name, trace_id)
                
                assert result is not None
                assert result.get("trace_id") == trace_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


