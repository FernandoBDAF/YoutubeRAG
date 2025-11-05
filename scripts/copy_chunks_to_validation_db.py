"""
Copy chunks from mongo_hack to validation_db for testing.

This script copies all video chunks to a validation database,
removing any GraphRAG processing status to start fresh.

Usage:
    python scripts/copy_chunks_to_validation_db.py [--max N]
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import argparse

def copy_chunks(max_chunks=None):
    """Copy chunks from mongo_hack to validation_db."""
    load_dotenv()
    
    # Connect to MongoDB
    mongodb_uri = os.getenv('MONGODB_URI')
    if not mongodb_uri:
        print("ERROR: MONGODB_URI not set in environment")
        return 1
    
    client = MongoClient(mongodb_uri)
    
    # Source and destination databases
    source_db = client['mongo_hack']
    dest_db = client['validation_db']
    
    print("=" * 80)
    print("Copying chunks from mongo_hack to validation_db")
    print("=" * 80)
    
    # Get source chunks
    source_chunks = source_db.video_chunks
    dest_chunks = dest_db.video_chunks
    
    # Clear destination
    print("\n1. Clearing validation_db.video_chunks...")
    result = dest_chunks.delete_many({})
    print(f"   Deleted {result.deleted_count} existing chunks")
    
    # Find chunks with text
    print("\n2. Finding chunks in mongo_hack...")
    query = {'chunk_text': {'$exists': True, '$ne': ''}}
    total_chunks = source_chunks.count_documents(query)
    print(f"   Found {total_chunks:,} chunks with text")
    
    # Limit if specified
    if max_chunks:
        limit = min(int(max_chunks), total_chunks)
        print(f"   Limiting to {limit:,} chunks (--max {max_chunks})")
    else:
        limit = total_chunks
    
    # Copy chunks in batches
    print(f"\n3. Copying {limit:,} chunks...")
    cursor = source_chunks.find(query).limit(limit)
    
    batch = []
    batch_size = 1000
    copied_count = 0
    
    for i, chunk in enumerate(cursor, 1):
        # Remove GraphRAG processing status
        chunk.pop('graphrag_extraction', None)
        chunk.pop('graphrag_resolution', None)
        chunk.pop('graphrag_construction', None)
        chunk.pop('graphrag_communities', None)
        
        batch.append(chunk)
        
        # Insert in batches
        if len(batch) >= batch_size:
            dest_chunks.insert_many(batch)
            copied_count += len(batch)
            print(f"   Copied {copied_count:,}/{limit:,} chunks...")
            batch = []
    
    # Insert remaining
    if batch:
        dest_chunks.insert_many(batch)
        copied_count += len(batch)
    
    print(f"\n✅ Copy complete: {copied_count:,} chunks copied to validation_db")
    
    # Verify
    print("\n4. Verifying...")
    validation_count = dest_chunks.count_documents({'chunk_text': {'$exists': True}})
    print(f"   validation_db.video_chunks: {validation_count:,} chunks")
    
    # Check for any with extraction status (should be none)
    with_extraction = dest_chunks.count_documents({'graphrag_extraction': {'$exists': True}})
    print(f"   With extraction status: {with_extraction}")
    
    if with_extraction == 0:
        print("\n✅ All chunks ready for fresh extraction!")
    else:
        print(f"\n⚠️  Warning: {with_extraction} chunks still have extraction status")
    
    print("\n" + "=" * 80)
    print("Next step: Run extraction")
    print("=" * 80)
    print("\npython -m app.cli.graphrag --stage graph_extraction \\")
    print(f"  --max {copied_count} \\")
    print("  --concurrency 10 \\")
    print("  --read-db-name validation_db \\")
    print("  --write-db-name validation_db \\")
    print("  --log-file logs/extraction_validation_full.log \\")
    print("  --verbose")
    print()
    
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy chunks to validation_db")
    parser.add_argument("--max", type=int, help="Maximum chunks to copy")
    args = parser.parse_args()
    
    sys.exit(copy_chunks(max_chunks=args.max))

