#!/usr/bin/env python3
"""
Diagnose GraphRAG Community Detection Issues

This script analyzes the GraphRAG data to identify why communities
all have single entities and no relationships.
"""

import os
import sys
from collections import defaultdict, Counter
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
sys.path.insert(0, project_root)

from dependencies.database.mongodb import get_mongo_client
from core.config.paths import DB_NAME

load_dotenv()


def analyze_graphrag_data():
    """Analyze GraphRAG collections to diagnose community issues."""
    client = get_mongo_client()
    db = client[DB_NAME]

    print("=" * 80)
    print("GraphRAG Community Detection Analysis")
    print("=" * 80)
    print()

    # 1. Count collections
    print("1. COLLECTION COUNTS")
    print("-" * 80)
    entities_count = db.entities.count_documents({})
    relations_count = db.relations.count_documents({})
    communities_count = db.communities.count_documents({})
    chunks_count = db.video_chunks.count_documents({})

    print(f"  Entities:     {entities_count:,}")
    print(f"  Relationships: {relations_count:,}")
    print(f"  Communities:  {communities_count:,}")
    print(f"  Chunks:       {chunks_count:,}")
    print()

    # 2. Check community sizes
    print("2. COMMUNITY SIZE DISTRIBUTION")
    print("-" * 80)
    community_sizes = Counter()
    communities_with_relationships = 0
    communities_without_relationships = 0

    for comm in db.communities.find():
        entity_count = comm.get("entity_count", 0)
        relationship_count = comm.get("relationship_count", 0)
        community_sizes[entity_count] += 1

        if relationship_count > 0:
            communities_with_relationships += 1
        else:
            communities_without_relationships += 1

    print(f"  Communities by entity count:")
    for size, count in sorted(community_sizes.items()):
        print(f"    {size} entity(ies): {count} communities")

    print(f"\n  Communities with relationships: {communities_with_relationships}")
    print(f"  Communities without relationships: {communities_without_relationships}")
    print()

    # 3. Check relationship data
    print("3. RELATIONSHIP ANALYSIS")
    print("-" * 80)

    if relations_count == 0:
        print("  ⚠️  NO RELATIONSHIPS FOUND!")
        print("  This is likely the root cause - the graph is disconnected.")
        print()
    else:
        # Sample relationships
        print(f"  Sample relationships (showing first 3):")
        for i, rel in enumerate(db.relations.find().limit(3)):
            print(
                f"    {i+1}. {rel.get('subject_id', 'N/A')[:8]}... -> "
                f"{rel.get('object_id', 'N/A')[:8]}... "
                f"(predicate: {rel.get('predicate', 'N/A')})"
            )
        print()

        # Check entity coverage
        entity_ids_in_rels = set()
        for rel in db.relations.find():
            entity_ids_in_rels.add(rel.get("subject_id"))
            entity_ids_in_rels.add(rel.get("object_id"))

        isolated_entity_ids = set()
        for entity in db.entities.find():
            entity_id = entity.get("entity_id")
            if entity_id not in entity_ids_in_rels:
                isolated_entity_ids.add(entity_id)

        print(f"  Entities in relationships: {len(entity_ids_in_rels):,}")
        print(f"  Isolated entities (no relationships): {len(isolated_entity_ids):,}")
        print(f"  Coverage: {len(entity_ids_in_rels) / entities_count * 100:.1f}%")
        print()

    # 4. Check extraction data in chunks
    print("4. GRAPH EXTRACTION ANALYSIS")
    print("-" * 80)

    chunks_with_extraction = db.video_chunks.count_documents(
        {"graphrag_extraction.status": "completed"}
    )
    chunks_with_entities = db.video_chunks.count_documents(
        {"graphrag_extraction.data.entities": {"$exists": True, "$ne": []}}
    )
    chunks_with_relationships = db.video_chunks.count_documents(
        {"graphrag_extraction.data.relationships": {"$exists": True, "$ne": []}}
    )

    print(f"  Chunks with completed extraction: {chunks_with_extraction:,}")
    print(f"  Chunks with entities extracted: {chunks_with_entities:,}")
    print(f"  Chunks with relationships extracted: {chunks_with_relationships:,}")
    print()

    # Get average extraction counts
    entity_counts = []
    relationship_counts = []

    for chunk in db.video_chunks.find(
        {
            "graphrag_extraction.status": "completed",
            "graphrag_extraction.data": {"$exists": True},
        }
    ).limit(
        100
    ):  # Sample 100 chunks
        data = chunk.get("graphrag_extraction", {}).get("data", {})
        entity_counts.append(len(data.get("entities", [])))
        relationship_counts.append(len(data.get("relationships", [])))

    if entity_counts:
        avg_entities = sum(entity_counts) / len(entity_counts)
        avg_relationships = sum(relationship_counts) / len(relationship_counts)
        print(f"  Average entities per chunk: {avg_entities:.1f}")
        print(f"  Average relationships per chunk: {avg_relationships:.1f}")
        print()

    # 5. Check graph construction status
    print("5. GRAPH CONSTRUCTION STATUS")
    print("-" * 80)

    chunks_with_construction = db.video_chunks.count_documents(
        {"graphrag_construction.status": "completed"}
    )

    print(f"  Chunks with completed construction: {chunks_with_construction:,}")
    print()

    # 6. Check entity resolution status
    print("6. ENTITY RESOLUTION STATUS")
    print("-" * 80)

    chunks_with_resolution = db.video_chunks.count_documents(
        {"graphrag_resolution.status": "completed"}
    )

    print(f"  Chunks with completed resolution: {chunks_with_resolution:,}")
    print()

    # 7. Summary and recommendations
    print("=" * 80)
    print("DIAGNOSIS & RECOMMENDATIONS")
    print("=" * 80)
    print()

    issues = []

    if relations_count == 0:
        issues.append(
            "❌ CRITICAL: No relationships found in database. "
            "This means graph_construction is not working properly."
        )
    elif relations_count < entities_count * 0.1:
        issues.append(
            f"⚠️  WARNING: Very few relationships ({relations_count}) compared to "
            f"entities ({entities_count}). "
            f"Expected at least {int(entities_count * 0.1)} relationships."
        )

    if chunks_with_relationships == 0:
        issues.append(
            "❌ CRITICAL: No chunks have relationships extracted. "
            "graph_extraction stage is not extracting relationships properly."
        )

    if communities_without_relationships == communities_count:
        issues.append(
            "❌ CRITICAL: All communities have 0 relationships. "
            "This confirms the graph is disconnected."
        )

    if community_sizes.get(1, 0) == communities_count:
        issues.append(
            f"❌ CRITICAL: All {communities_count} communities have only 1 entity. "
            "Community detection should filter these out (min_cluster_size=2)."
        )

    if issues:
        print("ISSUES FOUND:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print()
    else:
        print("✅ No major issues detected. Graph structure looks healthy.")
        print()

    print("RECOMMENDED ACTIONS:")
    print()
    if relations_count == 0 or chunks_with_relationships == 0:
        print(
            "  1. Check graph_extraction stage - ensure relationships are being extracted"
        )
        print("  2. Review extraction logs for warnings about missing relationships")
        print("  3. Check if LLM is properly extracting relationships from chunks")
        print()
    if community_sizes.get(1, 0) == communities_count:
        print(
            "  4. Apply Fix 1 from GRAPHRAG-COMMUNITY-ANALYSIS.md - filter single-entity communities"
        )
        print("  5. Re-run community detection after fixing relationship issues")
        print()
    if relations_count > 0 and isolated_entity_ids:
        print(
            f"  6. Consider linking {len(isolated_entity_ids)} isolated entities to existing graph"
        )
        print()


if __name__ == "__main__":
    try:
        analyze_graphrag_data()
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
