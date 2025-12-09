"""
Copy raw_videos from mongo_hack to 2025-12 database.

This script copies all raw_videos to a new database for processing.

Usage:
    python scripts/generate_db_with_raw_videos.py [--max N]
"""

import os
import sys
from pathlib import Path

# Add project root to Python path for module resolution
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from pymongo import MongoClient
from dotenv import load_dotenv
import argparse


def copy_raw_videos(max_videos=None):
    """Copy raw_videos from mongo_hack to 2025-12 database."""
    load_dotenv()
    
    # Connect to MongoDB
    mongodb_uri = os.getenv('MONGODB_URI')
    if not mongodb_uri:
        print("ERROR: MONGODB_URI not set in environment")
        return 1
    
    client = MongoClient(mongodb_uri)
    
    # Source and destination databases
    source_db = client['mongo_hack']
    dest_db = client['2025-12']
    
    print("=" * 80)
    print("Copying raw_videos from mongo_hack to 2025-12")
    print("=" * 80)
    
    # Get source and destination collections
    source_collection = source_db.raw_videos
    dest_collection = dest_db.raw_videos
    
    # Clear destination
    print("\n1. Clearing 2025-12.raw_videos...")
    result = dest_collection.delete_many({})
    print(f"   Deleted {result.deleted_count} existing documents")
    
    # Count source documents
    print("\n2. Finding raw_videos in mongo_hack...")
    total_videos = source_collection.count_documents({})
    print(f"   Found {total_videos:,} raw videos")
    
    # Limit if specified
    if max_videos:
        limit = min(int(max_videos), total_videos)
        print(f"   Limiting to {limit:,} videos (--max {max_videos})")
    else:
        limit = total_videos
    
    # Copy documents in batches
    print(f"\n3. Copying {limit:,} raw videos...")
    cursor = source_collection.find({}).limit(limit) if limit < total_videos else source_collection.find({})
    
    batch = []
    batch_size = 1000
    copied_count = 0
    
    for i, doc in enumerate(cursor, 1):
        batch.append(doc)
        
        # Insert in batches
        if len(batch) >= batch_size:
            dest_collection.insert_many(batch)
            copied_count += len(batch)
            print(f"   Copied {copied_count:,}/{limit:,} videos...")
            batch = []
    
    # Insert remaining
    if batch:
        dest_collection.insert_many(batch)
        copied_count += len(batch)
    
    print(f"\n✅ Copy complete: {copied_count:,} raw videos copied to 2025-12")
    
    # Verify
    print("\n4. Verifying...")
    dest_count = dest_collection.count_documents({})
    print(f"   2025-12.raw_videos: {dest_count:,} documents")
    
    # Show sample fields
    sample = dest_collection.find_one()
    if sample:
        print(f"\n   Sample document fields: {list(sample.keys())}")
    
    print("\n" + "=" * 80)
    print("Database 2025-12 ready with raw_videos collection")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy raw_videos to 2025-12 database")
    parser.add_argument("--max", type=int, help="Maximum videos to copy")
    args = parser.parse_args()
    
    sys.exit(copy_raw_videos(max_videos=args.max))

