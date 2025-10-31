#!/usr/bin/env python3
"""
Sample graph data to understand quality and relationship distribution.
"""

from pymongo import MongoClient
import json
import os
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
db_name = os.getenv("DB_NAME", "mongo_hack")

client = MongoClient(mongo_uri)
db = client[db_name]

print(f"Connected to database: {db_name}")
print(f"Checking collections...")
entities_count = db.entities.count_documents({})
relations_count = db.relations.count_documents({})
mentions_count = db.entity_mentions.count_documents({})
print(f"  Entities: {entities_count}")
print(f"  Relations: {relations_count}")
print(f"  Entity Mentions: {mentions_count}")
print()

print("=" * 80)
print("ENTITY SAMPLES (5 entities)")
print("=" * 80)

for i, entity in enumerate(db.entities.find().limit(5)):
    print(f'\n{i+1}. {entity["name"]} ({entity["type"]})')
    print(f'   Description: {entity["description"][:100]}...')
    print(f'   Confidence: {entity.get("confidence", 0):.3f}')
    print(f'   Source Count: {entity.get("source_count", 0)}')
    if "entity_embedding_dim" in entity:
        print(f'   Has Embedding: Yes ({entity["entity_embedding_dim"]} dims)')

print("\n" + "=" * 80)
print("RELATIONSHIP SAMPLES BY TYPE")
print("=" * 80)

# Sample different relationship types
types_to_sample = [
    "related_to",
    "mentioned_together",
    "semantically_similar_to",
    "co_occurs_with",
    "uses",
    "discusses",
]

for rel_type in types_to_sample:
    rel = db.relations.find_one({"predicate": rel_type})
    if rel:
        # Get entity names
        subj = db.entities.find_one({"entity_id": rel["subject_id"]})
        obj = db.entities.find_one({"entity_id": rel["object_id"]})

        print(f"\n[{rel_type}]")
        if subj and obj:
            print(f'  {subj["name"]} → {obj["name"]}')
        print(f'  Description: {rel["description"][:80]}...')
        print(f'  Confidence: {rel.get("confidence", 0):.3f}')
        print(f'  Type: {rel.get("relationship_type", "llm_extracted")}')
        print(f'  Source Count: {rel.get("source_count", 0)}')

print("\n" + "=" * 80)
print("RELATIONSHIP TYPE DISTRIBUTION")
print("=" * 80)

pipeline = [
    {"$group": {"_id": "$relationship_type", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
]

for doc in db.relations.aggregate(pipeline):
    rel_type = doc["_id"] or "llm_extracted"
    count = doc["count"]
    pct = (count / 3591) * 100
    print(f"  {rel_type}: {count} ({pct:.1f}%)")

print("\n" + "=" * 80)
print("HIGH-CONFIDENCE LLM RELATIONSHIPS (top 10)")
print("=" * 80)

llm_rels = list(
    db.relations.find(
        {"relationship_type": {"$exists": False}},
        {
            "subject_id": 1,
            "object_id": 1,
            "predicate": 1,
            "confidence": 1,
            "description": 1,
        },
    )
    .sort("confidence", -1)
    .limit(10)
)

for i, rel in enumerate(llm_rels):
    subj = db.entities.find_one({"entity_id": rel["subject_id"]})
    obj = db.entities.find_one({"entity_id": rel["object_id"]})

    if subj and obj:
        print(f'\n{i+1}. [{rel["predicate"]}] {subj["name"]} → {obj["name"]}')
        print(f'   Confidence: {rel.get("confidence", 0):.3f}')
        print(f'   {rel["description"][:100]}...')

print("\n" + "=" * 80)
print("CROSS-CHUNK SAMPLES (first 5)")
print("=" * 80)

cross_chunk = list(db.relations.find({"relationship_type": "cross_chunk"}).limit(5))

for i, rel in enumerate(cross_chunk):
    subj = db.entities.find_one({"entity_id": rel["subject_id"]})
    obj = db.entities.find_one({"entity_id": rel["object_id"]})

    if subj and obj:
        print(
            f'\n{i+1}. [{rel["predicate"]}] {subj["name"]} ({subj["type"]}) → {obj["name"]} ({obj["type"]})'
        )
        print(f'   Confidence: {rel.get("confidence", 0):.3f}')
        print(f'   Description: {rel["description"]}')
