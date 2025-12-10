"""
Clean extraction status from chunks to re-run extraction.

This script removes graphrag_extraction field from video_chunks
to allow re-running extraction stage.

Usage:
    python scripts/clean_extraction_status.py --db validation_db
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import argparse


def clean_extraction_status(db_name="validation_db"):
    """Clean extraction status from specified database."""
    load_dotenv()

    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        print("ERROR: MONGODB_URI not set in environment")
        return 1

    client = MongoClient(mongodb_uri)
    db = client[db_name]
    chunks_collection = db.video_chunks

    print("=" * 80)
    print(f"Cleaning extraction status from {db_name}.video_chunks")
    print("=" * 80)

    # Check current status
    print("\n1. Current status:")
    total_chunks = chunks_collection.count_documents({})
    with_extraction = chunks_collection.count_documents(
        {"graphrag_extraction": {"$exists": True}}
    )

    print(f"   Total chunks: {total_chunks:,}")
    print(f"   With extraction status: {with_extraction:,}")

    if with_extraction == 0:
        print("\n✓ No extraction status found - already clean!")
        return 0

    # Remove extraction status
    print(f"\n2. Removing graphrag_extraction, graphrag_resolution, graphrag_construction, and graphrag_communities from {with_extraction:,} chunks...")
    result = chunks_collection.update_many({}, {"$unset": {"graphrag_extraction": 1, "graphrag_resolution": 1, "graphrag_construction": 1, "graphrag_communities": 1}})


    print(f"   Modified: {result.modified_count:,} chunks")

    # Verify
    print("\n3. Verifying...")
    remaining = chunks_collection.count_documents(
        {"graphrag_extraction": {"$exists": True}, "graphrag_resolution": {"$exists": True}, "graphrag_construction": {"$exists": True}, "graphrag_communities": {"$exists": True}}
    )

    if remaining == 0:
        print(f"   ✅ Success! All extraction status removed")
        print(f"\n   Database: {db_name}")
        print(f"   Ready for: Fresh extraction run")
    else:
        print(f"   ⚠️  Warning: {remaining} chunks still have extraction status")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean extraction status from chunks")
    parser.add_argument(
        "--db", default="validation_db", help="Database name (default: mongo_hack)"
    )
    args = parser.parse_args()

    sys.exit(clean_extraction_status(db_name=args.db))
