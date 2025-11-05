"""
Tests for Link Prediction Agent.

Run with: python -m tests.business.agents.graphrag.test_link_prediction
"""


def test_predict_missing_links():
    """Test link prediction with simple graph."""
    from business.agents.graphrag.link_prediction import GraphLinkPredictionAgent

    agent = GraphLinkPredictionAgent(confidence_threshold=0.6)

    entities = [
        {"entity_id": "a" * 32, "type": "TECHNOLOGY"},
        {"entity_id": "b" * 32, "type": "TECHNOLOGY"},
    ]

    relationships = []  # No existing relationships

    result = agent.predict_missing_links(entities, relationships)

    assert isinstance(result, list)
    # May or may not predict links depending on structure

    print("✓ predict_missing_links executes without errors")


def test_infer_predicate_from_types():
    """Test predicate inference from entity types."""
    from business.agents.graphrag.link_prediction import GraphLinkPredictionAgent

    agent = GraphLinkPredictionAgent()

    test_cases = [
        ("PERSON", "CONCEPT", "discusses"),
        ("PERSON", "TECHNOLOGY", "uses"),
        ("CONCEPT", "CONCEPT", "related_to"),
        ("TECHNOLOGY", "TECHNOLOGY", "works_with"),
    ]

    for type1, type2, expected_predicate in test_cases:
        result = agent._infer_predicate_from_types(type1, type2)
        assert result == expected_predicate

    print("✓ _infer_predicate_from_types returns correct predicates")


def test_deduplicate_predictions():
    """Test prediction deduplication."""
    from business.agents.graphrag.link_prediction import GraphLinkPredictionAgent

    agent = GraphLinkPredictionAgent()

    predictions = [
        ("a" * 32, "b" * 32, "uses", 0.8),
        ("b" * 32, "a" * 32, "uses", 0.7),  # Duplicate (reverse)
        ("a" * 32, "b" * 32, "uses", 0.9),  # Duplicate (higher confidence)
    ]

    result = agent._deduplicate_predictions(predictions)

    assert len(result) == 1  # Only one unique relationship
    assert result[0][3] == 0.9  # Highest confidence kept

    print("✓ _deduplicate_predictions removes duplicates")


def run_all_tests():
    """Run all tests."""
    print("=== Testing Link Prediction Agent ===\n")

    test_predict_missing_links()
    test_infer_predicate_from_types()
    test_deduplicate_predictions()

    print("\n✅ All link prediction agent tests passed!")


if __name__ == "__main__":
    run_all_tests()
