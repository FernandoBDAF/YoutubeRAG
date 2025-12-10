#!/usr/bin/env python3
"""
GraphRAG Statistics Summary

Generate comprehensive statistics for GraphRAG pipeline collections.
"""

import argparse
import json
import os
import sys
from typing import Dict, Any, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from dotenv import load_dotenv
from pymongo import MongoClient
from core.libraries.error_handling.decorators import handle_errors

load_dotenv()


@handle_errors(log_traceback=True, reraise=True)
def generate_stats_summary(format: str = "table", output: Optional[str] = None) -> None:
    """Generate comprehensive GraphRAG statistics."""
    mongo_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DB_NAME", "mongo_hack")

    if not mongo_uri:
        print("❌ Error: MONGODB_URI not found in environment")
        sys.exit(1)

    client = MongoClient(mongo_uri)
    db = client[db_name]

    stats: Dict[str, Any] = {}

    # Video chunks
    total_chunks = db["video_chunks"].count_documents({})
    extracted = db["video_chunks"].count_documents({"graphrag_extraction.status": "completed"})
    resolved = db["video_chunks"].count_documents({"graphrag_resolution.status": "completed"})
    constructed = db["video_chunks"].count_documents({"graphrag_construction.status": "completed"})
    stats["video_chunks"] = {
        "total": total_chunks,
        "extracted": extracted,
        "resolved": resolved,
        "constructed": constructed,
    }

    # Entities
    if "entities" in db.list_collection_names():
        total_entities = db["entities"].count_documents({})
        entity_types = db["entities"].distinct("type")
        stats["entities"] = {
            "total": total_entities,
            "types": len(entity_types),
            "type_breakdown": {
                etype: db["entities"].count_documents({"type": etype}) for etype in entity_types
            },
        }

    # Relations
    if "relations" in db.list_collection_names():
        total_relations = db["relations"].count_documents({})
        rel_types = db["relations"].distinct("relationship_type")
        stats["relations"] = {
            "total": total_relations,
            "types": len(rel_types),
            "type_breakdown": {
                rtype: db["relations"].count_documents({"relationship_type": rtype})
                for rtype in rel_types
            },
        }

    # Communities
    if "communities" in db.list_collection_names():
        total_communities = db["communities"].count_documents({})
        stats["communities"] = {
            "total": total_communities,
            "with_summaries": db["communities"].count_documents(
                {"summary": {"$exists": True, "$ne": ""}}
            ),
        }

    # Entity mentions
    if "entity_mentions" in db.list_collection_names():
        total_mentions = db["entity_mentions"].count_documents({})
        stats["entity_mentions"] = {"total": total_mentions}

    # Format output
    if format == "json":
        output_data = json.dumps(stats, indent=2, default=str)
    else:  # table
        lines = ["\n📊 GraphRAG Statistics Summary", "=" * 80]

        lines.append("\n📁 Video Chunks:")
        lines.append(f"  Total: {stats['video_chunks']['total']:,}")
        lines.append(f"  Extracted: {stats['video_chunks']['extracted']:,}")
        lines.append(f"  Resolved: {stats['video_chunks']['resolved']:,}")
        lines.append(f"  Constructed: {stats['video_chunks']['constructed']:,}")

        if "entities" in stats:
            lines.append("\n👥 Entities:")
            lines.append(f"  Total: {stats['entities']['total']:,}")
            lines.append(f"  Types: {stats['entities']['types']}")
            for etype, count in sorted(
                stats["entities"]["type_breakdown"].items(), key=lambda x: x[1], reverse=True
            )[:5]:
                lines.append(f"    {etype}: {count:,}")

        if "relations" in stats:
            lines.append("\n🔗 Relations:")
            lines.append(f"  Total: {stats['relations']['total']:,}")
            lines.append(f"  Types: {stats['relations']['types']}")
            for rtype, count in sorted(
                stats["relations"]["type_breakdown"].items(), key=lambda x: x[1], reverse=True
            ):
                lines.append(f"    {rtype}: {count:,}")

        if "communities" in stats:
            lines.append("\n🏘️  Communities:")
            lines.append(f"  Total: {stats['communities']['total']:,}")
            lines.append(f"  With Summaries: {stats['communities']['with_summaries']:,}")

        if "entity_mentions" in stats:
            lines.append(f"\n📍 Entity Mentions: {stats['entity_mentions']['total']:,}")

        lines.append("=" * 80)
        output_data = "\n".join(lines)

    if output:
        with open(output, "w") as f:
            f.write(output_data)
        print(f"✅ Statistics saved to {output}")
    else:
        print(output_data)


def main():
    parser = argparse.ArgumentParser(description="Generate GraphRAG statistics summary")
    parser.add_argument(
        "--format", choices=["table", "json"], default="table", help="Output format"
    )
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()
    generate_stats_summary(format=args.format, output=args.output)


if __name__ == "__main__":
    main()
