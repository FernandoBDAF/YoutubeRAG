#!/usr/bin/env python3
"""
Quick validation cleanup - remove problematic relationships to test community detection.
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
db_name = os.getenv("DB_NAME", "mongo_hack")

client = MongoClient(mongo_uri)
db = client[db_name]

print("=" * 80)
print("QUICK VALIDATION CLEANUP")
print("=" * 80)

print(f"\nConnected to database: {db_name}")

# Check current state
entities_count = db.entities.count_documents({})
relations_before = db.relations.count_documents({})
mentions_count = db.entity_mentions.count_documents({})
communities_count = db.communities.count_documents({})

print(f"\nCurrent state:")
print(f"  Entities: {entities_count}")
print(f"  Relations: {relations_before}")
print(f"  Entity Mentions: {mentions_count}")
print(f"  Communities: {communities_count}")

# Check relationship type distribution
print(f"\nRelationship types before cleanup:")
pipeline = [
    {"$group": {"_id": "$relationship_type", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
]

for doc in db.relations.aggregate(pipeline):
    rel_type = doc["_id"] or "llm_extracted"
    count = doc["count"]
    pct = (count / relations_before) * 100 if relations_before > 0 else 0
    print(f"  {rel_type}: {count} ({pct:.1f}%)")

# Remove problematic relationships
print(f"\n" + "-" * 80)
print("Removing problematic relationships...")
print("-" * 80)

# Remove cross_chunk and semantic_similarity relationships
result = db.relations.delete_many(
    {"relationship_type": {"$in": ["cross_chunk", "semantic_similarity"]}}
)

print(f"\n✓ Deleted {result.deleted_count} relationships")

# Check new state
relations_after = db.relations.count_documents({})
print(f"\nRelations after cleanup: {relations_after}")
print(
    f"Reduction: {relations_before - relations_after} ({((relations_before - relations_after) / relations_before * 100):.1f}%)"
)

# Show remaining relationship types
print(f"\nRemaining relationship types:")
for doc in db.relations.aggregate(pipeline):
    rel_type = doc["_id"] or "llm_extracted"
    count = doc["count"]
    pct = (count / relations_after) * 100 if relations_after > 0 else 0
    print(f"  {rel_type}: {count} ({pct:.1f}%)")

# Clear communities to allow re-detection
print(f"\n" + "-" * 80)
print("Clearing communities for re-detection...")
print("-" * 80)

db.communities.drop()
db.video_chunks.update_many({}, {"$unset": {"graphrag_communities": 1}})

print(f"\n✓ Communities cleared")

print("\n" + "=" * 80)
print("CLEANUP COMPLETE")
print("=" * 80)

print(f"\nNext steps:")
print(f"  1. Run: python scripts/analyze_graph_structure.py")
print(f"  2. Verify graph density is now reasonable (0.05-0.15)")
print(f"  3. Re-run community detection stage")
print(f"  4. Verify communities are detected")
