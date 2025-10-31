from pymongo import MongoClient

from dotenv import load_dotenv
load_dotenv()

import os

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("MONGODB_DB") or "mongo_hack"]

# 1. Drop all GraphRAG collections
db.entities.drop()
db.relations.drop()
db.communities.drop()
db.entity_mentions.drop()

print("✓ Dropped all GraphRAG collections")

# 2. Remove GraphRAG metadata from chunks
result = db.video_chunks.update_many(
    {},
    {
        "$unset": {
            "graphrag_extraction": 1,
            "graphrag_resolution": 1,
            "graphrag_construction": 1,
            "graphrag_communities": 1
        }
    }
)

print(f"✓ Cleaned GraphRAG metadata from {result.modified_count} chunks")

# 3. Verify cleanup
print(f"\nVerification:")
print(f"  Entities: {db.entities.count_documents({})}")
print(f"  Relations: {db.relations.count_documents({})}")
print(f"  Communities: {db.communities.count_documents({})}")
print(f"  Entity mentions: {db.entity_mentions.count_documents({})}")
print(f"  Chunks with graphrag_extraction: {db.video_chunks.count_documents({'graphrag_extraction': {'$exists': True}})}")