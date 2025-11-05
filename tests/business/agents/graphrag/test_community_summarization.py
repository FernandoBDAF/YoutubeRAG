"""
Tests for Community Summarization Agent.

Run with: python -m tests.business.agents.graphrag.test_community_summarization
"""

from unittest.mock import Mock, MagicMock


def test_extract_title_from_summary():
    """Test title extraction from summary text."""
    from business.agents.graphrag.community_summarization import (
        CommunitySummarizationAgent,
    )

    mock_client = MagicMock()
    agent = CommunitySummarizationAgent(llm_client=mock_client)

    # Test with "Title:" prefix
    summary1 = "Title: Python Ecosystem\n\nThis is a summary..."
    result1 = agent._extract_title(summary1)
    assert result1 == "Python Ecosystem"

    # Test with markdown heading
    summary2 = "# Machine Learning\n\nThis is a summary..."
    result2 = agent._extract_title(summary2)
    assert result2 == "Machine Learning"

    # Test with first line fallback
    summary3 = "Short Title\n\nThis is a longer summary..."
    result3 = agent._extract_title(summary3)
    assert result3 == "Short Title"

    print("✓ _extract_title handles various formats")


def test_select_important_entities():
    """Test selection of important entities for summarization."""
    from business.agents.graphrag.community_summarization import (
        CommunitySummarizationAgent,
    )
    from core.models.graphrag import ResolvedEntity, EntityType

    mock_client = MagicMock()
    agent = CommunitySummarizationAgent(llm_client=mock_client)

    entities = [
        ResolvedEntity(
            entity_id="a" * 32,
            canonical_name="E1",
            name="E1",
            type=EntityType.CONCEPT,
            description="First entity description here",
            confidence=0.9,
            source_count=5,
            resolution_methods=[],
            aliases=[],
        ),
        ResolvedEntity(
            entity_id="b" * 32,
            canonical_name="E2",
            name="E2",
            type=EntityType.CONCEPT,
            description="Second entity description",
            confidence=0.7,
            source_count=2,
            resolution_methods=[],
            aliases=[],
        ),
        ResolvedEntity(
            entity_id="c" * 32,
            canonical_name="E3",
            name="E3",
            type=EntityType.CONCEPT,
            description="Third entity description",
            confidence=0.6,
            source_count=1,
            resolution_methods=[],
            aliases=[],
        ),
    ]

    result = agent._select_important_entities(entities, max_count=2)

    assert len(result) == 2
    assert result[0].confidence >= result[1].confidence  # Sorted by importance

    print("✓ _select_important_entities selects top N by confidence")


def test_select_important_relationships():
    """Test selection of important relationships."""
    from business.agents.graphrag.community_summarization import (
        CommunitySummarizationAgent,
    )
    from core.models.graphrag import ResolvedRelationship

    mock_client = MagicMock()
    agent = CommunitySummarizationAgent(llm_client=mock_client)

    relationships = [
        ResolvedRelationship(
            relationship_id="r1" + "a" * 30,
            subject_id="a" * 32,
            object_id="b" * 32,
            predicate="uses",
            description="High confidence relationship here",
            confidence=0.9,
            source_count=3,
        ),
        ResolvedRelationship(
            relationship_id="r2" + "b" * 30,
            subject_id="b" * 32,
            object_id="c" * 32,
            predicate="related",
            description="Low confidence relationship",
            confidence=0.5,
            source_count=1,
        ),
    ]

    result = agent._select_important_relationships(relationships, max_count=1)

    assert len(result) == 1
    assert result[0].confidence == 0.9  # Highest confidence kept

    print("✓ _select_important_relationships selects top N")


def run_all_tests():
    """Run all tests."""
    print("=== Testing Community Summarization Agent ===\n")

    test_extract_title_from_summary()
    test_select_important_entities()
    test_select_important_relationships()

    print("\n✅ All community summarization agent tests passed!")


if __name__ == "__main__":
    run_all_tests()
