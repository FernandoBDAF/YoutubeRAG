#!/usr/bin/env python3
"""
Test GraphRAG pipeline with random chunks from different videos.
This provides a more realistic test than consecutive chunks from one video.
"""

import os
import sys
import random
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
db_name = os.getenv("DB_NAME", "mongo_hack")

client = MongoClient(mongo_uri)
db = client[db_name]


def get_random_chunks(collection_name="video_chunks", num_chunks=12, seed=42):
    """
    Select random chunks from the dataset, ensuring diversity across videos.

    Args:
        collection_name: Name of chunks collection
        num_chunks: Number of random chunks to select
        seed: Random seed for reproducibility

    Returns:
        List of chunk IDs
    """
    print("=" * 80)
    print("RANDOM CHUNK SELECTION FOR TESTING")
    print("=" * 80)

    # Get total chunks and video distribution
    total_chunks = db[collection_name].count_documents({})
    print(f"\nDataset overview:")
    print(f"  Total chunks: {total_chunks}")

    # Get video distribution
    pipeline = [
        {"$group": {"_id": "$video_id", "chunk_count": {"$sum": 1}}},
        {"$sort": {"chunk_count": -1}},
        {"$limit": 10},
    ]

    video_distribution = list(db[collection_name].aggregate(pipeline))
    num_videos = db[collection_name].distinct("video_id")

    print(f"  Total videos: {len(num_videos)}")
    print(f"\nTop 10 videos by chunk count:")
    for i, video in enumerate(video_distribution[:10]):
        print(f"    {i+1}. {video['_id']}: {video['chunk_count']} chunks")

    # Strategy: Sample random chunks, but try to get diversity across videos
    print(f"\n" + "-" * 80)
    print(f"Selecting {num_chunks} random chunks (seed={seed})...")
    print("-" * 80)

    random.seed(seed)

    # Get all chunks
    all_chunks = list(
        db[collection_name].find({}, {"chunk_id": 1, "video_id": 1, "video_title": 1})
    )

    if len(all_chunks) < num_chunks:
        print(
            f"⚠️ WARNING: Only {len(all_chunks)} chunks available, requested {num_chunks}"
        )
        num_chunks = len(all_chunks)

    # Random sample
    selected_chunks = random.sample(all_chunks, num_chunks)

    # Analyze selection
    video_counts = {}
    for chunk in selected_chunks:
        video_id = chunk.get("video_id", "unknown")
        video_counts[video_id] = video_counts.get(video_id, 0) + 1

    print(f"\n✓ Selected {len(selected_chunks)} chunks")
    print(f"  Unique videos: {len(video_counts)}")
    print(f"\nVideo distribution in selection:")
    for video_id, count in sorted(
        video_counts.items(), key=lambda x: x[1], reverse=True
    ):
        # Get video title
        chunk_sample = next(
            (c for c in selected_chunks if c.get("video_id") == video_id), None
        )
        title = (
            chunk_sample.get("video_title", "Unknown") if chunk_sample else "Unknown"
        )
        title_short = title[:50] + "..." if len(title) > 50 else title
        print(f"  {video_id}: {count} chunks - {title_short}")

    chunk_ids = [c["chunk_id"] for c in selected_chunks]

    print(f"\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print(f"\n1. Mark these chunks for processing:")
    print(f"   - Clear existing GraphRAG metadata from these chunks")
    print(f"   - This ensures they'll be processed in the next run")

    print(f"\n2. Run GraphRAG pipeline targeting these chunks")

    print(f"\n3. Expected results with {len(video_counts)} videos:")
    if len(video_counts) == 1:
        print(
            f"   ⚠️ All chunks from same video - will still have transitive connection"
        )
        print(f"   Expected communities: 1-3")
    elif len(video_counts) <= 3:
        print(f"   ⚠️ Only {len(video_counts)} videos - limited diversity")
        print(f"   Expected communities: {len(video_counts)}-{len(video_counts)*3}")
    else:
        print(f"   ✅ Good diversity across {len(video_counts)} videos!")
        print(f"   Expected communities: {len(video_counts)}-{len(video_counts)*5}")
        print(
            f"   Expected disconnected components: {max(1, len(video_counts)//3)}-{len(video_counts)}"
        )

    return chunk_ids, selected_chunks


def clear_graphrag_metadata(chunk_ids):
    """Clear GraphRAG metadata from selected chunks to force reprocessing."""
    print(f"\n" + "-" * 80)
    print("Clearing GraphRAG metadata from selected chunks...")
    print("-" * 80)

    result = db.video_chunks.update_many(
        {"chunk_id": {"$in": chunk_ids}},
        {
            "$unset": {
                "graphrag_extraction": 1,
                "graphrag_resolution": 1,
                "graphrag_construction": 1,
                "graphrag_communities": 1,
            }
        },
    )

    print(f"✓ Cleared metadata from {result.modified_count} chunks")


def print_run_command(num_chunks):
    """Print the command to run the pipeline."""
    print(f"\n" + "=" * 80)
    print("RUN COMMAND")
    print("=" * 80)
    print(f"\nRun this command to process the selected chunks:\n")
    print(
        f"  python run_graphrag_pipeline.py --max {num_chunks} --log-file logs/pipeline/graphrag_random_test.log --verbose"
    )
    print(f"\nThen analyze results:")
    print(f"  grep 'using adaptive window' logs/pipeline/graphrag_random_test.log")
    print(f"  grep 'density:' logs/pipeline/graphrag_random_test.log")
    print(f"  python scripts/analyze_graph_structure.py")
    print(f"  python scripts/test_community_detection.py")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Select random chunks for GraphRAG testing"
    )
    parser.add_argument(
        "--num-chunks", type=int, default=12, help="Number of chunks to select"
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--collection", default="video_chunks", help="Chunks collection name"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear GraphRAG metadata from selected chunks",
    )
    parser.add_argument(
        "--full-cleanup",
        action="store_true",
        help="Also clear all GraphRAG collections",
    )

    args = parser.parse_args()

    # Select random chunks
    chunk_ids, selected_chunks = get_random_chunks(
        collection_name=args.collection, num_chunks=args.num_chunks, seed=args.seed
    )

    if args.full_cleanup:
        print(f"\n" + "=" * 80)
        print("FULL CLEANUP")
        print("=" * 80)

        # Drop GraphRAG collections
        db.entities.drop()
        db.relations.drop()
        db.communities.drop()
        db.entity_mentions.drop()

        print("✓ Dropped all GraphRAG collections")

        # Clear all chunk metadata
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

        print(f"✓ Cleared GraphRAG metadata from {result.modified_count} chunks")

    elif args.clear:
        # Import the marking function from run_random_chunk_test
        from run_random_chunk_test import mark_chunks_for_testing

        mark_chunks_for_testing(chunk_ids)

    # Print run command
    print_run_command(args.num_chunks)

    print(f"\n" + "=" * 80)
    print(f"✅ READY TO TEST")
    print("=" * 80)
