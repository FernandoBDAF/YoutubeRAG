#!/usr/bin/env python3
"""
Monitor GraphRAG graph density in real-time.
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import time

load_dotenv()

mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
db_name = os.getenv("DB_NAME", "mongo_hack")

client = MongoClient(mongo_uri)
db = client[db_name]


def calculate_density():
    """Calculate current graph density."""
    entities_count = db.entities.count_documents({})
    relations_count = db.relations.count_documents({})

    if entities_count < 2:
        return 0.0, entities_count, relations_count

    max_possible = entities_count * (entities_count - 1) / 2
    density = relations_count / max_possible if max_possible > 0 else 0.0

    return density, entities_count, relations_count


def get_relationship_breakdown():
    """Get relationship counts by type."""
    pipeline = [
        {"$group": {"_id": "$relationship_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]

    breakdown = {}
    for doc in db.relations.aggregate(pipeline):
        rel_type = doc["_id"] or "llm_extracted"
        breakdown[rel_type] = doc["count"]

    return breakdown


def monitor_once():
    """Show current density status."""
    density, entities, relations = calculate_density()

    print("=" * 80)
    print("GraphRAG Graph Density Monitor")
    print("=" * 80)
    print(f"\n📊 Current Metrics:")
    print(f"  Entities: {entities}")
    print(f"  Relationships: {relations}")
    print(
        f"  Max Possible: {int(entities * (entities - 1) / 2) if entities >= 2 else 0}"
    )
    print(f"\n🎯 Graph Density: {density:.4f}")

    # Status indicator
    if density < 0.15:
        status = "✅ EXCELLENT - Sparse, well-connected"
    elif density < 0.30:
        status = "✅ GOOD - Healthy density"
    elif density < 0.50:
        status = "⚠️ WARNING - Getting dense"
    elif density < 0.80:
        status = "🔴 ALERT - Very dense, approaching complete"
    else:
        status = "🔴 CRITICAL - Near-complete or complete graph!"

    print(f"  Status: {status}")

    # Show relationship breakdown
    breakdown = get_relationship_breakdown()

    if breakdown:
        print(f"\n📈 Relationship Breakdown:")
        total = sum(breakdown.values())

        for rel_type in [
            "llm_extracted",
            "co_occurrence",
            "semantic_similarity",
            "cross_chunk",
            "bidirectional",
            "predicted",
        ]:
            count = breakdown.get(rel_type, 0)
            if count > 0:
                pct = (count / total * 100) if total > 0 else 0
                print(f"  {rel_type}: {count} ({pct:.1f}%)")

        # Show others
        others = {
            k: v
            for k, v in breakdown.items()
            if k
            not in [
                "llm_extracted",
                "co_occurrence",
                "semantic_similarity",
                "cross_chunk",
                "bidirectional",
                "predicted",
            ]
        }
        if others:
            other_total = sum(others.values())
            print(f"  other types: {other_total} ({other_total/total*100:.1f}%)")

    print("\n" + "=" * 80)


def monitor_continuous(interval=5):
    """Monitor density continuously."""
    print("🔄 Continuous monitoring mode (Ctrl+C to stop)")
    print(f"   Refreshing every {interval} seconds\n")

    try:
        while True:
            monitor_once()
            print(f"\n⏱️  Refreshing in {interval}s...\n")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\n✋ Monitoring stopped by user")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--watch":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        monitor_continuous(interval)
    else:
        monitor_once()
