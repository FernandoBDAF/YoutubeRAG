"""
Tests for Relationship Resolution Agent.

Run with: python -m tests.business.agents.graphrag.test_relationship_resolution
"""

from unittest.mock import Mock, MagicMock


def test_resolve_relationships_single():
    """Test resolving a single relationship (no LLM needed)."""
    from business.agents.graphrag.relationship_resolution import (
        RelationshipResolutionAgent,
    )

    mock_client = MagicMock()
    agent = RelationshipResolutionAgent(llm_client=mock_client)

    extracted_data = [
        {
            "chunk_id": "chunk-1",
            "relationships": [
                {
                    "source_entity": {"name": "Python"},
                    "target_entity": {"name": "Django"},
                    "relation": "uses",
                    "description": "Python uses Django framework",
                    "confidence": 0.9,
                }
            ],
        }
    ]

    # Mock entity name to ID mapping (must be 32-char MD5 hashes)
    entity_name_to_id = {
        "python": "a" * 32,  # Valid 32-char ID
        "django": "b" * 32,  # Valid 32-char ID
    }

    result = agent.resolve_relationships(extracted_data, entity_name_to_id)

    assert len(result) == 1
    assert result[0].predicate == "uses"
    assert result[0].source_count == 1

    print("✓ resolve_relationships with single relationship")


def test_lookup_entity_id_with_mapping():
    """Test entity ID lookup with provided mapping."""
    from business.agents.graphrag.relationship_resolution import (
        RelationshipResolutionAgent,
    )

    mock_client = MagicMock()
    agent = RelationshipResolutionAgent(llm_client=mock_client)

    entity_name_to_id = {
        "python": "a" * 32,  # Valid 32-char MD5 hash
        "django": "b" * 32,
    }

    result = agent._lookup_entity_id("Python", entity_name_to_id)

    assert result == "a" * 32  # Case insensitive match
    print("✓ _lookup_entity_id with mapping (case insensitive)")


def test_lookup_entity_id_without_mapping():
    """Test entity ID generation when no mapping provided."""
    from business.agents.graphrag.relationship_resolution import (
        RelationshipResolutionAgent,
    )

    mock_client = MagicMock()
    agent = RelationshipResolutionAgent(llm_client=mock_client)

    result = agent._lookup_entity_id("Python", entity_name_to_id=None)

    assert result is not None
    assert isinstance(result, str)
    assert len(result) == 32  # MD5 hash length

    print("✓ _lookup_entity_id generates ID when no mapping")


def test_calculate_overall_confidence():
    """Test confidence calculation for relationships."""
    from business.agents.graphrag.relationship_resolution import (
        RelationshipResolutionAgent,
    )

    mock_client = MagicMock()
    agent = RelationshipResolutionAgent(llm_client=mock_client)

    relationship_group = [
        {"confidence": 0.9},
        {"confidence": 0.8},
        {"confidence": 0.7},
    ]

    result = agent._calculate_overall_confidence(relationship_group)

    expected = (0.9 + 0.8 + 0.7) / 3
    assert abs(result - expected) < 0.01

    print("✓ _calculate_overall_confidence averages correctly")


def test_validate_entity_existence():
    """Test filtering relationships by entity existence."""
    from business.agents.graphrag.relationship_resolution import (
        RelationshipResolutionAgent,
    )
    from core.models.graphrag import ResolvedRelationship

    mock_client = MagicMock()
    agent = RelationshipResolutionAgent(llm_client=mock_client)

    relationships = [
        ResolvedRelationship(
            relationship_id="r" * 32,  # Valid 32-char hash
            subject_id="a" * 32,  # Valid 32-char hash
            object_id="b" * 32,  # Valid 32-char hash
            predicate="uses",
            description="Test relationship description",  # At least 10 chars
            confidence=0.8,
            source_count=1,
        ),
        ResolvedRelationship(
            relationship_id="s" * 32,
            subject_id="a" * 32,
            object_id="c" * 32,  # entity_missing
            predicate="uses",
            description="Test relationship 2 description",
            confidence=0.8,
            source_count=1,
        ),
    ]

    existing_entity_ids = {"a" * 32, "b" * 32}  # "c" * 32 not in set

    result = agent.validate_entity_existence(relationships, existing_entity_ids)

    assert len(result) == 1  # Only first relationship kept
    assert result[0].relationship_id == "r" * 32

    print("✓ validate_entity_existence filters correctly")


def run_all_tests():
    """Run all tests."""
    print("=== Testing Relationship Resolution Agent ===\n")

    test_resolve_relationships_single()
    test_lookup_entity_id_with_mapping()
    test_lookup_entity_id_without_mapping()
    test_calculate_overall_confidence()
    test_validate_entity_existence()

    print("\n✅ All relationship resolution agent tests passed!")


if __name__ == "__main__":
    run_all_tests()
