"""
Tests for Entity Resolution Agent.

Run with: python -m tests.business.agents.graphrag.test_entity_resolution
"""

from unittest.mock import Mock, MagicMock


def test_resolve_entities_single_entity():
    """Test resolving a single entity (no LLM needed)."""
    from business.agents.graphrag.entity_resolution import EntityResolutionAgent

    mock_client = MagicMock()
    agent = EntityResolutionAgent(llm_client=mock_client)

    extracted_data = [
        {
            "chunk_id": "chunk-1",
            "entities": [
                {
                    "name": "Python",
                    "type": "TECHNOLOGY",
                    "description": "Programming language",
                    "confidence": 0.9,
                }
            ],
        }
    ]

    result = agent.resolve_entities(extracted_data)

    assert len(result) == 1
    assert result[0].name == "Python"
    assert result[0].source_count == 1

    print("✓ resolve_entities with single entity")


def test_determine_canonical_name_highest_count():
    """Test canonical name selection based on count."""
    from business.agents.graphrag.entity_resolution import EntityResolutionAgent

    mock_client = MagicMock()
    agent = EntityResolutionAgent(llm_client=mock_client)

    entity_group = [
        {"name": "Python", "confidence": 0.8},
        {"name": "Python", "confidence": 0.9},
        {"name": "python", "confidence": 0.7},
    ]

    result = agent._determine_canonical_name(entity_group)

    assert result == "Python"  # Most common (2 times)
    print("✓ _determine_canonical_name selects highest count")


def test_determine_entity_type_most_common():
    """Test entity type determination."""
    from business.agents.graphrag.entity_resolution import EntityResolutionAgent

    mock_client = MagicMock()
    agent = EntityResolutionAgent(llm_client=mock_client)

    entity_group = [
        {"type": "TECHNOLOGY"},
        {"type": "TECHNOLOGY"},
        {"type": "CONCEPT"},
    ]

    result = agent._determine_entity_type(entity_group)

    assert result.value == "TECHNOLOGY"  # Most common
    print("✓ _determine_entity_type selects most common")


def test_calculate_overall_confidence():
    """Test confidence calculation."""
    from business.agents.graphrag.entity_resolution import EntityResolutionAgent

    mock_client = MagicMock()
    agent = EntityResolutionAgent(llm_client=mock_client)

    entity_group = [
        {"confidence": 0.8},
        {"confidence": 0.9},
        {"confidence": 0.7},
    ]

    result = agent._calculate_overall_confidence(entity_group)

    expected = (0.8 + 0.9 + 0.7) / 3
    assert abs(result - expected) < 0.01
    print("✓ _calculate_overall_confidence averages correctly")


def test_normalize_entity_name_improvements():
    """Test improved normalization logic."""
    from business.agents.graphrag.entity_resolution import EntityResolutionAgent

    mock_client = MagicMock()
    agent = EntityResolutionAgent(llm_client=mock_client)

    test_cases = [
        ("Python Programming", "python programming"),
        (
            "Technologies",
            "technologies",
        ),  # TODO: Should become "technology" with better stemming
        ("Dr. Smith", "smith"),
        ("OpenAI Inc.", "openai"),
        ("The Company", "company"),
    ]

    for original, expected in test_cases:
        result = agent._normalize_entity_name(original)
        assert (
            result == expected
        ), f"Failed: '{original}' → '{result}' (expected: '{expected}')"

    print("✓ _normalize_entity_name handles various patterns")


def run_all_tests():
    """Run all tests."""
    print("=== Testing Entity Resolution Agent ===\n")

    test_resolve_entities_single_entity()
    test_determine_canonical_name_highest_count()
    test_determine_entity_type_most_common()
    test_calculate_overall_confidence()
    test_normalize_entity_name_improvements()

    print("\n✅ All entity resolution agent tests passed!")


if __name__ == "__main__":
    run_all_tests()
