"""
Setup validation_db from scratch.

Copies all video_chunks from mongo_hack to validation_db
and removes all GraphRAG processing fields.

Usage:
    python scripts/setup_validation_db.py
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv


def setup_validation_db():
    """Setup validation_db with clean chunks."""
    load_dotenv()

    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        print("ERROR: MONGODB_URI not set in environment")
        return 1

    client = MongoClient(mongodb_uri)

    print("=" * 80)
    print("Setting up validation_db from mongo_hack")
    print("=" * 80)

    # Source and destination
    source_db = client["mongo_hack"]
    dest_db = client["validation_db"]

    source_chunks = source_db.video_chunks
    dest_chunks = dest_db.video_chunks

    # Step 1: Clear destination
    print("\n1. Clearing validation_db.video_chunks...")
    result = dest_chunks.delete_many({})
    print(f"   Deleted: {result.deleted_count:,} chunks")

    # Step 2: Count source chunks
    print("\n2. Counting chunks in mongo_hack...")
    query = {"chunk_text": {"$exists": True, "$ne": ""}}
    total_chunks = source_chunks.count_documents(query)
    print(f"   Found: {total_chunks:,} chunks with text")

    # Step 3: Copy all chunks (removing GraphRAG fields)
    print(f"\n3. Copying all {total_chunks:,} chunks...")
    print("   (Removing GraphRAG processing fields)")

    cursor = source_chunks.find(query)

    batch = []
    batch_size = 1000
    copied_count = 0

    for chunk in cursor:
        # Remove ALL GraphRAG processing fields
        chunk.pop("graphrag_extraction", None)
        chunk.pop("graphrag_resolution", None)
        chunk.pop("graphrag_construction", None)
        chunk.pop("graphrag_communities", None)
        chunk.pop("_test_exclude", None)  # Also remove test exclusion

        batch.append(chunk)

        # Insert in batches
        if len(batch) >= batch_size:
            dest_chunks.insert_many(batch)
            copied_count += len(batch)
            print(f"   Copied: {copied_count:,}/{total_chunks:,} chunks...")
            batch = []

    # Insert remaining
    if batch:
        dest_chunks.insert_many(batch)
        copied_count += len(batch)

    print(f"\n✅ Copy complete: {copied_count:,} chunks copied")

    # Step 4: Verify
    print("\n4. Verifying...")
    validation_count = dest_chunks.count_documents({"chunk_text": {"$exists": True}})
    with_extraction = dest_chunks.count_documents(
        {"graphrag_extraction": {"$exists": True}}
    )
    with_resolution = dest_chunks.count_documents(
        {"graphrag_resolution": {"$exists": True}}
    )
    with_construction = dest_chunks.count_documents(
        {"graphrag_construction": {"$exists": True}}
    )
    with_communities = dest_chunks.count_documents(
        {"graphrag_communities": {"$exists": True}}
    )

    print(f"   validation_db.video_chunks: {validation_count:,} chunks")
    print(f"   With graphrag_extraction: {with_extraction:,}")
    print(f"   With graphrag_resolution: {with_resolution:,}")
    print(f"   With graphrag_construction: {with_construction:,}")
    print(f"   With graphrag_communities: {with_communities:,}")

    if with_extraction == 0 and with_resolution == 0 and with_construction == 0:
        print("\n✅ All GraphRAG fields removed - ready for fresh run!")
    else:
        print("\n⚠️  Warning: Some GraphRAG fields still present")
        return 1

    # Summary
    print("\n" + "=" * 80)
    print("Setup Complete")
    print("=" * 80)
    print(f"\nvalidation_db ready with {validation_count:,} clean chunks")
    print("\nNext step: Run extraction with TPM tracking")
    print("-" * 80)
    print("\nGRAPHRAG_USE_TPM_TRACKING=true \\")
    print("GRAPHRAG_TARGET_TPM=950000 \\")
    print("GRAPHRAG_TARGET_RPM=4500 \\")
    print("python -m app.cli.graphrag --stage graph_extraction \\")
    print(f"  --max {validation_count} \\")
    print("  --concurrency 50 \\")
    print("  --read-db-name validation_db \\")
    print("  --write-db-name validation_db \\")
    print("  --log-file logs/extraction_tpm_full.log \\")
    print("  --verbose")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(setup_validation_db())
