#!/usr/bin/env python3
"""
Query GraphRAG Entities

Query entities from the entities collection with filters and formatting options.
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from dotenv import load_dotenv
from pymongo import MongoClient
from core.libraries.error_handling.decorators import handle_errors

# Load environment variables
load_dotenv()


@handle_errors(log_traceback=True, reraise=True)
def query_entities(
    entity_type: Optional[str] = None,
    limit: int = 20,
    min_mentions: int = 0,
    min_centrality: float = 0.0,
    format: str = "table",
    output: Optional[str] = None,
) -> None:
    """
    Query entities from the entities collection.

    Args:
        entity_type: Filter by entity type (e.g., "PERSON", "ORGANIZATION")
        limit: Maximum number of results
        min_mentions: Minimum mention count
        min_centrality: Minimum centrality score
        format: Output format ("table", "json", "csv")
        output: Optional output file path
    """
    mongo_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DB_NAME", "mongo_hack")

    if not mongo_uri:
        print("❌ Error: MONGODB_URI not found in environment")
        sys.exit(1)

    client = MongoClient(mongo_uri)
    db = client[db_name]

    # Build query
    query: Dict[str, Any] = {}
    if entity_type:
        query["type"] = entity_type
    if min_mentions > 0:
        query["mention_count"] = {"$gte": min_mentions}
    if min_centrality > 0:
        query["centrality_score"] = {"$gte": min_centrality}

    # Query entities
    entities = list(db["entities"].find(query).limit(limit).sort("centrality_score", -1))

    if not entities:
        print("No entities found matching criteria")
        return

    # Format output
    if format == "json":
        output_data = json.dumps(entities, indent=2, default=str)
    elif format == "csv":
        import csv
        from io import StringIO

        output_buffer = StringIO()
        if entities:
            writer = csv.DictWriter(
                output_buffer,
                fieldnames=["entity_id", "name", "type", "mention_count", "centrality_score"],
            )
            writer.writeheader()
            for entity in entities:
                writer.writerow(
                    {
                        "entity_id": entity.get("entity_id", ""),
                        "name": entity.get("name", ""),
                        "type": entity.get("type", ""),
                        "mention_count": entity.get("mention_count", 0),
                        "centrality_score": entity.get("centrality_score", 0.0),
                    }
                )
        output_data = output_buffer.getvalue()
    else:  # table
        # Simple table format
        output_lines = [
            f"\n📊 Entities ({len(entities)} results)",
            "=" * 80,
            f"{'Entity ID':<40} {'Name':<30} {'Type':<15} {'Mentions':<10} {'Centrality':<10}",
            "-" * 80,
        ]
        for entity in entities:
            entity_id = str(entity.get("entity_id", ""))[:38]
            name = str(entity.get("name", ""))[:28]
            etype = str(entity.get("type", ""))[:13]
            mentions = entity.get("mention_count", 0)
            centrality = f"{entity.get('centrality_score', 0.0):.4f}"
            output_lines.append(
                f"{entity_id:<40} {name:<30} {etype:<15} {mentions:<10} {centrality:<10}"
            )
        output_lines.append("=" * 80)
        output_data = "\n".join(output_lines)

    # Output
    if output:
        with open(output, "w") as f:
            f.write(output_data)
        print(f"✅ Results saved to {output}")
    else:
        print(output_data)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Query GraphRAG entities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query top 10 entities
  python query_entities.py --limit 10

  # Query PERSON entities with high centrality
  python query_entities.py --entity-type PERSON --min-centrality 0.5 --limit 20

  # Export to JSON
  python query_entities.py --format json --output entities.json
        """,
    )

    parser.add_argument("--entity-type", help="Filter by entity type (e.g., PERSON, ORGANIZATION)")
    parser.add_argument(
        "--limit", type=int, default=20, help="Maximum number of results (default: 20)"
    )
    parser.add_argument("--min-mentions", type=int, default=0, help="Minimum mention count")
    parser.add_argument(
        "--min-centrality", type=float, default=0.0, help="Minimum centrality score"
    )
    parser.add_argument(
        "--format", choices=["table", "json", "csv"], default="table", help="Output format"
    )
    parser.add_argument("--output", help="Output file path (optional)")

    args = parser.parse_args()

    query_entities(
        entity_type=args.entity_type,
        limit=args.limit,
        min_mentions=args.min_mentions,
        min_centrality=args.min_centrality,
        format=args.format,
        output=args.output,
    )


if __name__ == "__main__":
    main()
