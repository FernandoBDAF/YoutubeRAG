"""
Clean GraphRAG fields from validation_db to re-run full pipeline.

This script:
1. Removes all GraphRAG status fields from video_chunks
2. Drops entities collection
3. Drops relations collection
4. Leaves chunks ready for fresh GraphRAG processing

Usage:
    python scripts/clean_graphrag_fields.py --db validation_db
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import argparse


def clean_graphrag_fields(db_name="validation_db"):
    """Clean all GraphRAG processing from specified database."""
    load_dotenv()

    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        print("ERROR: MONGODB_URI not set in environment")
        return 1

    client = MongoClient(mongodb_uri)
    db = client[db_name]

    print("=" * 80)
    print(f"Cleaning GraphRAG data from {db_name}")
    print("=" * 80)

    # 1. Check current status
    print("\n1. Current status:")
    chunks_coll = db.video_chunks
    total_chunks = chunks_coll.count_documents({"chunk_text": {"$exists": True}})
    with_extraction = chunks_coll.count_documents(
        {"graphrag_extraction": {"$exists": True}}
    )
    with_resolution = chunks_coll.count_documents(
        {"graphrag_resolution": {"$exists": True}}
    )
    with_construction = chunks_coll.count_documents(
        {"graphrag_construction": {"$exists": True}}
    )

    print(f"   video_chunks: {total_chunks:,} chunks")
    print(f"     - With extraction: {with_extraction:,}")
    print(f"     - With resolution: {with_resolution:,}")
    print(f"     - With construction: {with_construction:,}")

    # Check collections
    collections = db.list_collection_names()
    entities_exist = "entities" in collections
    relations_exist = "relations" in collections

    if entities_exist:
        entity_count = db.entities.count_documents({})
        print(f"   entities collection: {entity_count:,} documents")
    else:
        print(f"   entities collection: Does not exist")

    if relations_exist:
        relation_count = db.relations.count_documents({})
        print(f"   relations collection: {relation_count:,} documents")
    else:
        print(f"   relations collection: Does not exist")

    # 2. Remove GraphRAG fields from chunks
    print("\n2. Cleaning video_chunks...")
    result = chunks_coll.update_many(
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
    print(f"   Modified: {result.modified_count:,} chunks")

    # 3. Drop entities collection
    if entities_exist:
        print("\n3. Dropping entities collection...")
        db.entities.drop()
        print(f"   ✓ Dropped entities collection")
    else:
        print("\n3. entities collection doesn't exist (skipping)")

    # 4. Drop relations collection
    if relations_exist:
        print("\n4. Dropping relations collection...")
        db.relations.drop()
        print(f"   ✓ Dropped relations collection")
    else:
        print("\n4. relations collection doesn't exist (skipping)")

    # 5. Verify clean
    print("\n5. Verifying...")
    remaining_extraction = chunks_coll.count_documents(
        {"graphrag_extraction": {"$exists": True}}
    )
    remaining_resolution = chunks_coll.count_documents(
        {"graphrag_resolution": {"$exists": True}}
    )
    remaining_construction = chunks_coll.count_documents(
        {"graphrag_construction": {"$exists": True}}
    )

    collections_after = db.list_collection_names()
    entities_after = "entities" in collections_after
    relations_after = "relations" in collections_after

    print(
        f"   video_chunks GraphRAG fields: {remaining_extraction + remaining_resolution + remaining_construction}"
    )
    print(f"   entities collection exists: {entities_after}")
    print(f"   relations collection exists: {relations_after}")

    if (
        remaining_extraction == 0
        and remaining_resolution == 0
        and remaining_construction == 0
    ):
        if not entities_after and not relations_after:
            print("\n✅ Success! All GraphRAG data removed - ready for fresh run")
        else:
            print("\n⚠️  Warning: Collections still exist")
            return 1
    else:
        print(
            f"\n⚠️  Warning: {remaining_extraction + remaining_resolution + remaining_construction} chunks still have GraphRAG fields"
        )
        return 1

    # Summary
    print("\n" + "=" * 80)
    print("Clean Complete - Ready for Full Pipeline")
    print("=" * 80)
    print(f"\n{db_name} ready with {total_chunks:,} clean chunks")
    print("\nNext: Run full GraphRAG pipeline with TPM")
    print("-" * 80)
    print("\nGRAPHRAG_USE_TPM_TRACKING=true \\")
    print("GRAPHRAG_TARGET_TPM=950000 \\")
    print("GRAPHRAG_TARGET_RPM=10000 \\")
    print("python -m app.cli.graphrag \\")
    print(f"  --max {total_chunks} \\")
    print("  --concurrency 100 \\")
    print(f"  --read-db-name {db_name} \\")
    print(f"  --write-db-name {db_name} \\")
    print("  --log-file logs/graphrag_full_tpm.log \\")
    print("  --verbose")
    print()
    print("This will run all 4 stages:")
    print("  1. graph_extraction")
    print("  2. entity_resolution")
    print("  3. graph_construction")
    print("  4. community_detection")
    print()

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean GraphRAG data from database")
    parser.add_argument(
        "--db", default="validation_db", help="Database name (default: validation_db)"
    )
    args = parser.parse_args()

    sys.exit(clean_graphrag_fields(db_name=args.db))
