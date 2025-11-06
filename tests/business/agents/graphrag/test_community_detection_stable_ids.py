"""
Tests for Stable Community ID Generation.

Run with: python -m tests.business.agents.graphrag.test_community_detection_stable_ids
"""

import hashlib
from business.agents.graphrag.community_detection import CommunityDetectionAgent
from core.models.graphrag import ResolvedEntity, ResolvedRelationship, EntityType


def test_generate_stable_community_id_deterministic():
    """Test that same entity set produces same ID."""
    agent = CommunityDetectionAgent()

    entity_ids = ["entity1", "entity2", "entity3"]
    level = 1

    # Generate ID twice
    id1 = agent._generate_stable_community_id(level, entity_ids)
    id2 = agent._generate_stable_community_id(level, entity_ids)

    assert id1 == id2, "Same entity set should produce same ID"
    print("✓ Deterministic ID generation")


def test_generate_stable_community_id_order_independent():
    """Test that different order of same entities produces same ID."""
    agent = CommunityDetectionAgent()

    entity_ids1 = ["entity1", "entity2", "entity3"]
    entity_ids2 = ["entity3", "entity1", "entity2"]  # Different order
    level = 1

    id1 = agent._generate_stable_community_id(level, entity_ids1)
    id2 = agent._generate_stable_community_id(level, entity_ids2)

    assert id1 == id2, "Different order of same entities should produce same ID"
    print("✓ Order-independent ID generation")


def test_generate_stable_community_id_different_entities():
    """Test that different entity sets produce different IDs."""
    agent = CommunityDetectionAgent()

    entity_ids1 = ["entity1", "entity2", "entity3"]
    entity_ids2 = ["entity1", "entity2", "entity4"]  # Different entity
    level = 1

    id1 = agent._generate_stable_community_id(level, entity_ids1)
    id2 = agent._generate_stable_community_id(level, entity_ids2)

    assert id1 != id2, "Different entity sets should produce different IDs"
    print("✓ Different entities produce different IDs")


def test_generate_stable_community_id_format():
    """Test that ID format is correct: lvl{level}-{12-char-hash}."""
    agent = CommunityDetectionAgent()

    entity_ids = ["entity1", "entity2", "entity3"]
    level = 1

    community_id = agent._generate_stable_community_id(level, entity_ids)

    # Check format: lvl{level}-{hash}
    assert community_id.startswith(
        f"lvl{level}-"
    ), f"ID should start with 'lvl{level}-', got: {community_id}"

    # Extract hash part
    hash_part = community_id.split("-")[1]
    assert len(hash_part) == 12, f"Hash should be 12 characters, got: {len(hash_part)}"
    assert all(
        c in "0123456789abcdef" for c in hash_part
    ), f"Hash should be hex, got: {hash_part}"

    print(f"✓ ID format correct: {community_id}")


def test_generate_stable_community_id_different_levels():
    """Test that same entities at different levels produce different IDs."""
    agent = CommunityDetectionAgent()

    entity_ids = ["entity1", "entity2", "entity3"]

    id1 = agent._generate_stable_community_id(1, entity_ids)
    id2 = agent._generate_stable_community_id(2, entity_ids)

    assert id1 != id2, "Different levels should produce different IDs"
    assert id1.startswith("lvl1-"), "Level 1 ID should start with 'lvl1-'"
    assert id2.startswith("lvl2-"), "Level 2 ID should start with 'lvl2-'"
    print("✓ Different levels produce different IDs")


def test_organize_communities_stable_ids_louvain():
    """Test that Louvain communities get stable IDs."""
    agent = CommunityDetectionAgent(min_cluster_size=2)

    # Create entities
    entities = [
        ResolvedEntity(
            entity_id="a" * 32,
            canonical_name="Entity A",
            name="Entity A",
            type=EntityType.CONCEPT,
            description="Description A",
            confidence=0.9,
            source_count=1,
            resolution_methods=[],
            aliases=[],
        ),
        ResolvedEntity(
            entity_id="b" * 32,
            canonical_name="Entity B",
            name="Entity B",
            type=EntityType.CONCEPT,
            description="Description B",
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
            predicate="related_to",
            description="A related to B",
            confidence=0.8,
            source_count=1,
        )
    ]

    # Run detection
    result = agent.detect_communities(entities, relationships)
    communities = result["communities"]

    # Check that communities have stable IDs
    assert len(communities) > 0, "Should have at least one community"

    for level, level_communities in communities.items():
        for community_id, community_data in level_communities.items():
            # Check ID format
            assert community_id.startswith(
                f"lvl{level}-"
            ), f"ID should start with 'lvl{level}-', got: {community_id}"
            assert (
                len(community_id.split("-")[1]) == 12
            ), f"Hash should be 12 chars, got: {community_id}"

            # Check that stored community_id matches key
            assert (
                community_data["community_id"] == community_id
            ), "Stored ID should match key"

    print("✓ Louvain communities have stable IDs")


def test_organize_communities_idempotent():
    """Test that running detection twice produces same IDs."""
    agent = CommunityDetectionAgent(min_cluster_size=2)

    entities = [
        ResolvedEntity(
            entity_id="a" * 32,
            canonical_name="Entity A",
            name="Entity A",
            type=EntityType.CONCEPT,
            description="Description A",
            confidence=0.9,
            source_count=1,
            resolution_methods=[],
            aliases=[],
        ),
        ResolvedEntity(
            entity_id="b" * 32,
            canonical_name="Entity B",
            name="Entity B",
            type=EntityType.CONCEPT,
            description="Description B",
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
            predicate="related_to",
            description="A related to B",
            confidence=0.8,
            source_count=1,
        )
    ]

    # Run detection twice
    result1 = agent.detect_communities(entities, relationships)
    result2 = agent.detect_communities(entities, relationships)

    communities1 = result1["communities"]
    communities2 = result2["communities"]

    # Extract all community IDs
    ids1 = set()
    for level_communities in communities1.values():
        ids1.update(level_communities.keys())

    ids2 = set()
    for level_communities in communities2.values():
        ids2.update(level_communities.keys())

    # Should have same IDs
    assert (
        ids1 == ids2
    ), f"Same graph should produce same IDs. Run 1: {ids1}, Run 2: {ids2}"
    print("✓ Detection is idempotent (same graph → same IDs)")


if __name__ == "__main__":
    test_generate_stable_community_id_deterministic()
    test_generate_stable_community_id_order_independent()
    test_generate_stable_community_id_different_entities()
    test_generate_stable_community_id_format()
    test_generate_stable_community_id_different_levels()
    test_organize_communities_stable_ids_louvain()
    test_organize_communities_idempotent()
    print("\n✅ All stable ID tests passed!")
