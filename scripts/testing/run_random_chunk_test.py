#!/usr/bin/env python3
"""
Complete random chunk test - select, clean, and prepare for pipeline run.
"""

import os
import random
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
db_name = os.getenv("DB_NAME", "mongo_hack")
client = MongoClient(mongo_uri)
db = client[db_name]

print("=" * 80)
print("RANDOM CHUNK TEST SETUP")
print("=" * 80)

# Configuration
NUM_CHUNKS = 12
SEED = 42

print(f"\nConfiguration:")
print(f"  Chunks to test: {NUM_CHUNKS}")
print(f"  Random seed: {SEED}")

# Step 1: Get dataset info
total_chunks = db.video_chunks.count_documents({})
num_videos = len(db.video_chunks.distinct("video_id"))

print(f"\nDataset:")
print(f"  Total chunks: {total_chunks}")
print(f"  Total videos: {num_videos}")

# Step 2: Select random chunks from DIFFERENT videos
print(f"\n" + "-" * 80)
print("Selecting random chunks...")
print("-" * 80)

random.seed(SEED)

# Get one chunk per video (to maximize diversity)
all_videos = db.video_chunks.distinct("video_id")
selected_video_ids = random.sample(all_videos, min(NUM_CHUNKS, len(all_videos)))

# Get one random chunk from each selected video
selected_chunks = []
for video_id in selected_video_ids:
    chunks_from_video = list(
        db.video_chunks.find(
            {"video_id": video_id}, {"chunk_id": 1, "video_id": 1, "video_title": 1}
        )
    )
    if chunks_from_video:
        selected_chunk = random.choice(chunks_from_video)
        selected_chunks.append(selected_chunk)

print(
    f"\n✓ Selected {len(selected_chunks)} chunks from {len(selected_chunks)} different videos"
)

print(f"\nSelected chunks:")
for i, chunk in enumerate(selected_chunks):
    title = chunk.get("video_title", "Unknown")[:50]
    print(f"  {i+1}. {chunk['video_id']} - {title}...")

chunk_ids = [c["chunk_id"] for c in selected_chunks]

# Step 3: Full GraphRAG cleanup
print(f"\n" + "-" * 80)
print("Performing full GraphRAG cleanup...")
print("-" * 80)

db.entities.drop()
db.relations.drop()
db.communities.drop()
db.entity_mentions.drop()

result = db.video_chunks.update_many(
    {},
    {
        "$unset": {
            "graphrag_extraction": 1,
            "graphrag_resolution": 1,
            "graphrag_construction": 1,
            "graphrag_communities": 1,
        }
    },
)

print(f"✓ Dropped all GraphRAG collections")
print(f"✓ Cleared GraphRAG metadata from {result.modified_count} chunks")

# Step 4: Hide all chunks EXCEPT selected ones
# We do this by temporarily setting a flag
print(f"\n" + "-" * 80)
print("Marking selected chunks for processing...")
print("-" * 80)

# Mark all chunks as not for testing
db.video_chunks.update_many({}, {"$set": {"_test_exclude": True}})

# Mark ONLY selected chunks for testing (remove exclusion flag)
db.video_chunks.update_many(
    {"chunk_id": {"$in": chunk_ids}}, {"$unset": {"_test_exclude": 1}}
)

# Verify
processable_count = db.video_chunks.count_documents(
    {"_test_exclude": {"$exists": False}}
)
print(f"✓ {processable_count} chunks marked for processing")

# Step 5: Instructions
print(f"\n" + "=" * 80)
print("READY TO RUN")
print("=" * 80)

print(f"\n🎯 Next Steps:")
print(
    f"\n1. Run the GraphRAG pipeline (it will only find the {len(chunk_ids)} selected chunks):"
)
print(
    f"\n   python run_graphrag_pipeline.py --max {len(chunk_ids)} --log-file logs/pipeline/graphrag_random_test.log --verbose"
)

print(f"\n2. After completion, check results:")
print(f"\n   grep 'using adaptive window' logs/pipeline/graphrag_random_test.log")
print(f"   grep 'density:' logs/pipeline/graphrag_random_test.log")
print(f"   python scripts/analyze_graph_structure.py")

print(f"\n3. Clean up test markers when done:")
print(
    f"\n   python -c \"from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv(); c = MongoClient(os.getenv('MONGODB_URI')); db = c[os.getenv('DB_NAME', 'mongo_hack')]; db.video_chunks.update_many({{}}, {{'\$unset': {{'_test_exclude': 1}}}}); print('Cleanup complete')\""
)

print(f"\n📊 Expected Results:")
print(f"  - {len(selected_chunks)} different videos")
print(
    f"  - Disconnected components: {max(1, len(selected_chunks)//3)}-{len(selected_chunks)}"
)
print(f"  - Communities: {len(selected_chunks)}-{len(selected_chunks)*3}")
print(f"  - Density: 0.05-0.15 (much lower than single-video tests!)")

print(f"\n" + "=" * 80)
