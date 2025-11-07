#!/usr/bin/env python3
"""
Query GraphRAG Communities

Query communities from the communities collection with filters and formatting options.
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Any, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from dotenv import load_dotenv
from pymongo import MongoClient
from core.libraries.error_handling.decorators import handle_errors

load_dotenv()


@handle_errors(log_traceback=True, reraise=True)
def query_communities(
    limit: int = 20,
    min_coherence: float = 0.0,
    min_entities: int = 0,
    format: str = "table",
    output: Optional[str] = None,
) -> None:
    """Query communities from the communities collection."""
    mongo_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DB_NAME", "mongo_hack")

    if not mongo_uri:
        print("❌ Error: MONGODB_URI not found in environment")
        sys.exit(1)

    client = MongoClient(mongo_uri)
    db = client[db_name]

    # Build query
    query: Dict[str, Any] = {}
    if min_coherence > 0:
        query["coherence_score"] = {"$gte": min_coherence}
    if min_entities > 0:
        query["entities"] = {"$size": {"$gte": min_entities}}

    # Query communities
    communities = list(db["communities"].find(query).limit(limit).sort("coherence_score", -1))

    if not communities:
        print("No communities found matching criteria")
        return

    # Format output
    if format == "json":
        output_data = json.dumps(communities, indent=2, default=str)
    elif format == "csv":
        import csv
        from io import StringIO

        output_buffer = StringIO()
        if communities:
            writer = csv.DictWriter(
                output_buffer,
                fieldnames=["community_id", "entity_count", "coherence_score", "summary"],
            )
            writer.writeheader()
            for comm in communities:
                summary = comm.get("summary", "")[:100] if comm.get("summary") else ""
                writer.writerow(
                    {
                        "community_id": comm.get("community_id", ""),
                        "entity_count": len(comm.get("entities", [])),
                        "coherence_score": comm.get("coherence_score", 0.0),
                        "summary": summary,
                    }
                )
        output_data = output_buffer.getvalue()
    else:  # table
        output_lines = [
            f"\n📊 Communities ({len(communities)} results)",
            "=" * 120,
            f"{'Community ID':<40} {'Entities':<10} {'Coherence':<12} {'Summary':<50}",
            "-" * 120,
        ]
        for comm in communities:
            comm_id = str(comm.get("community_id", ""))[:38]
            entity_count = len(comm.get("entities", []))
            coherence = f"{comm.get('coherence_score', 0.0):.4f}"
            summary = (comm.get("summary", "") or "")[:48]
            output_lines.append(f"{comm_id:<40} {entity_count:<10} {coherence:<12} {summary:<50}")
        output_lines.append("=" * 120)
        output_data = "\n".join(output_lines)

    if output:
        with open(output, "w") as f:
            f.write(output_data)
        print(f"✅ Results saved to {output}")
    else:
        print(output_data)


def main():
    parser = argparse.ArgumentParser(description="Query GraphRAG communities")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of results")
    parser.add_argument("--min-coherence", type=float, default=0.0, help="Minimum coherence score")
    parser.add_argument("--min-entities", type=int, default=0, help="Minimum number of entities")
    parser.add_argument(
        "--format", choices=["table", "json", "csv"], default="table", help="Output format"
    )
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()
    query_communities(
        limit=args.limit,
        min_coherence=args.min_coherence,
        min_entities=args.min_entities,
        format=args.format,
        output=args.output,
    )


if __name__ == "__main__":
    main()
