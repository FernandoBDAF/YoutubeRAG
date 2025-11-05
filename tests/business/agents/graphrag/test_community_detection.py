"""
Tests for Community Detection Agent.

Run with: python -m tests.business.agents.graphrag.test_community_detection
"""

from unittest.mock import Mock
from core.models.graphrag import ResolvedEntity, ResolvedRelationship, EntityType


def test_detect_communities_basic():
    """Test basic community detection with simple graph."""
    from business.agents.graphrag.community_detection import CommunityDetectionAgent

    agent = CommunityDetectionAgent(max_cluster_size=10, min_cluster_size=2)

    # Create simple entities
    entities = [
        ResolvedEntity(
            entity_id="a" * 32,
            canonical_name="Python",
            name="Python",
            type=EntityType.TECHNOLOGY,
            description="Programming language for development",
            confidence=0.9,
            source_count=1,
            resolution_methods=["single"],
            aliases=["Python"],
        ),
        ResolvedEntity(
            entity_id="b" * 32,
            canonical_name="Django",
            name="Django",
            type=EntityType.TECHNOLOGY,
            description="Web framework for Python development",
            confidence=0.85,
            source_count=1,
            resolution_methods=["single"],
            aliases=["Django"],
        ),
    ]

    relationships = [
        ResolvedRelationship(
            relationship_id="r" * 32,
            subject_id="a" * 32,
            object_id="b" * 32,
            predicate="uses",
            description="Python uses Django framework for web",
            confidence=0.8,
            source_count=1,
        )
    ]

    result = agent.detect_communities(entities, relationships)

    assert "communities" in result
    assert "levels" in result
    assert "total_communities" in result

    print("✓ detect_communities with basic graph")


def test_calculate_coherence_score():
    """Test coherence score calculation."""
    from business.agents.graphrag.community_detection import CommunityDetectionAgent

    agent = CommunityDetectionAgent()

    entities = [
        ResolvedEntity(
            entity_id="a" * 32,
            canonical_name="E1",
            name="E1",
            type=EntityType.CONCEPT,
            description="Entity one description",
            confidence=0.9,
            source_count=1,
            resolution_methods=[],
            aliases=[],
        ),
        ResolvedEntity(
            entity_id="b" * 32,
            canonical_name="E2",
            name="E2",
            type=EntityType.CONCEPT,
            description="Entity two description",
            confidence=0.8,
            source_count=1,
            resolution_methods=[],
            aliases=[],
        ),
    ]

    relationships = [
        ResolvedRelationship(
            relationship_id="r" * 32,
            subject_id="a" * 32,
            object_id="b" * 32,
            predicate="related",
            description="Related entities description",
            confidence=0.85,
            source_count=1,
        )
    ]

    score = agent._calculate_coherence_score(entities, relationships)

    assert 0.0 <= score <= 1.0
    assert score > 0  # Should have some coherence

    print("✓ _calculate_coherence_score returns valid score")


def run_all_tests():
    """Run all tests."""
    print("=== Testing Community Detection Agent ===\n")

    test_detect_communities_basic()
    test_calculate_coherence_score()

    print("\n✅ All community detection agent tests passed!")


if __name__ == "__main__":
    run_all_tests()
