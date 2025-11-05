"""
Tests for Graph Extraction Agent.

Run with: python -m tests.business.agents.graphrag.test_extraction
"""

from unittest.mock import Mock, MagicMock
from core.models.graphrag import (
    KnowledgeModel,
    EntityModel,
    RelationshipModel,
    EntityType,
)


def test_extract_from_chunk_success():
    """Test successful extraction from chunk."""
    from business.agents.graphrag.extraction import GraphExtractionAgent

    # Mock LLM client
    mock_client = MagicMock()
    agent = GraphExtractionAgent(llm_client=mock_client, model_name="gpt-4o-mini")

    # Mock successful LLM response
    mock_entity1 = EntityModel(
        name="Python",
        type=EntityType.TECHNOLOGY,
        description="Programming language used for data science",
        confidence=0.9,
    )
    mock_entity2 = EntityModel(
        name="Data Science",
        type=EntityType.CONCEPT,
        description="Field of study",
        confidence=0.85,
    )
    mock_relationship = RelationshipModel(
        source_entity=mock_entity1,
        target_entity=mock_entity2,
        relation="used_in",
        description="Python is used in data science",
        confidence=0.8,
    )

    # Note: Validation requires both entities to have confidence >= 0.3
    mock_knowledge = KnowledgeModel(
        entities=[mock_entity1, mock_entity2],  # Both entities must be in list
        relationships=[mock_relationship],
    )

    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.parsed = mock_knowledge
    mock_client.beta.chat.completions.parse.return_value = mock_response

    # Test chunk
    chunk = {
        "chunk_id": "test-123",
        "chunk_text": "Python is a programming language used in data science.",
    }

    # Execute
    result = agent.extract_from_chunk(chunk)

    # Verify
    assert result is not None
    assert len(result.entities) == 2  # Both entities
    assert len(result.relationships) == 1

    print("✓ extract_from_chunk success case")


def test_extract_from_chunk_empty_text():
    """Test extraction with empty chunk text."""
    from business.agents.graphrag.extraction import GraphExtractionAgent

    mock_client = MagicMock()
    agent = GraphExtractionAgent(llm_client=mock_client)

    chunk = {"chunk_id": "test-123", "chunk_text": ""}

    result = agent.extract_from_chunk(chunk)

    assert result is None
    print("✓ extract_from_chunk handles empty text")


def test_validate_and_enhance_filters_low_confidence():
    """Test that validation filters out low-confidence entities."""
    from business.agents.graphrag.extraction import GraphExtractionAgent

    mock_client = MagicMock()
    agent = GraphExtractionAgent(llm_client=mock_client)

    # Create knowledge model with mixed confidence
    high_conf_entity = EntityModel(
        name="Python",
        type=EntityType.TECHNOLOGY,
        description="Programming language",
        confidence=0.8,
    )
    low_conf_entity = EntityModel(
        name="Thing",
        type=EntityType.OTHER,
        description="Some thing",
        confidence=0.2,  # Below 0.3 threshold
    )

    knowledge_model = KnowledgeModel(
        entities=[high_conf_entity, low_conf_entity], relationships=[]
    )

    chunk = {"chunk_id": "test-123"}

    # Execute validation
    result = agent._validate_and_enhance(knowledge_model, chunk)

    # Verify low-confidence entity filtered out
    assert len(result.entities) == 1
    assert result.entities[0].name == "Python"
    assert result.entities[0].confidence == 0.8

    print("✓ _validate_and_enhance filters low confidence entities")


def test_validate_and_enhance_filters_invalid_relationships():
    """Test that validation filters relationships with missing entities."""
    from business.agents.graphrag.extraction import GraphExtractionAgent

    mock_client = MagicMock()
    agent = GraphExtractionAgent(llm_client=mock_client)

    # Create entity
    entity = EntityModel(
        name="Python",
        type=EntityType.TECHNOLOGY,
        description="Programming language",
        confidence=0.8,
    )

    # Create relationship with non-existent target
    relationship = RelationshipModel(
        source_entity=entity,
        target_entity=EntityModel(
            name="Missing",
            type=EntityType.OTHER,
            description="Not in entities",
            confidence=0.2,  # Low confidence, will be filtered
        ),
        relation="uses",
        description="Python uses Missing",
        confidence=0.5,
    )

    knowledge_model = KnowledgeModel(entities=[entity], relationships=[relationship])

    chunk = {"chunk_id": "test-123"}

    # Execute
    result = agent._validate_and_enhance(knowledge_model, chunk)

    # Verify relationship filtered (target entity missing from filtered entities)
    assert len(result.entities) == 1
    assert len(result.relationships) == 0  # Filtered out

    print("✓ _validate_and_enhance filters invalid relationships")


def run_all_tests():
    """Run all tests."""
    print("=== Testing Graph Extraction Agent ===\n")

    test_extract_from_chunk_success()
    test_extract_from_chunk_empty_text()
    test_validate_and_enhance_filters_low_confidence()
    test_validate_and_enhance_filters_invalid_relationships()

    print("\n✅ All extraction agent tests passed!")


if __name__ == "__main__":
    run_all_tests()
