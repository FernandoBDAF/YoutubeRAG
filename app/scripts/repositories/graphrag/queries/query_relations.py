#!/usr/bin/env python3
"""
Query GraphRAG Relations

Query relationships from the relations collection with filters and formatting options.
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
def query_relations(
    relationship_type: Optional[str] = None,
    limit: int = 20,
    min_confidence: float = 0.0,
    min_edge_weight: float = 0.0,
    format: str = "table",
    output: Optional[str] = None,
) -> None:
    """Query relationships from the relations collection."""
    mongo_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DB_NAME", "mongo_hack")

    if not mongo_uri:
        print("❌ Error: MONGODB_URI not found in environment")
        sys.exit(1)

    client = MongoClient(mongo_uri)
    db = client[db_name]

    # Build query
    query: Dict[str, Any] = {}
    if relationship_type:
        query["relationship_type"] = relationship_type
    if min_confidence > 0:
        query["confidence_score"] = {"$gte": min_confidence}
    if min_edge_weight > 0:
        query["edge_weight"] = {"$gte": min_edge_weight}

    # Query relations
    relations = list(db["relations"].find(query).limit(limit).sort("confidence_score", -1))

    if not relations:
        print("No relations found matching criteria")
        return

    # Format output
    if format == "json":
        output_data = json.dumps(relations, indent=2, default=str)
    elif format == "csv":
        import csv
        from io import StringIO

        output_buffer = StringIO()
        if relations:
            writer = csv.DictWriter(
                output_buffer,
                fieldnames=[
                    "source_entity_id",
                    "target_entity_id",
                    "relationship_type",
                    "confidence_score",
                    "edge_weight",
                ],
            )
            writer.writeheader()
            for rel in relations:
                writer.writerow(
                    {
                        "source_entity_id": rel.get("source_entity_id", ""),
                        "target_entity_id": rel.get("target_entity_id", ""),
                        "relationship_type": rel.get("relationship_type", ""),
                        "confidence_score": rel.get("confidence_score", 0.0),
                        "edge_weight": rel.get("edge_weight", 0.0),
                    }
                )
        output_data = output_buffer.getvalue()
    else:  # table
        output_lines = [
            f"\n📊 Relations ({len(relations)} results)",
            "=" * 100,
            f"{'Source Entity':<40} {'Target Entity':<40} {'Type':<15} {'Confidence':<12} {'Edge Weight':<12}",
            "-" * 100,
        ]
        for rel in relations:
            source = str(rel.get("source_entity_id", ""))[:38]
            target = str(rel.get("target_entity_id", ""))[:38]
            rtype = str(rel.get("relationship_type", ""))[:13]
            confidence = f"{rel.get('confidence_score', 0.0):.4f}"
            edge_weight = f"{rel.get('edge_weight', 0.0):.4f}"
            output_lines.append(
                f"{source:<40} {target:<40} {rtype:<15} {confidence:<12} {edge_weight:<12}"
            )
        output_lines.append("=" * 100)
        output_data = "\n".join(output_lines)

    if output:
        with open(output, "w") as f:
            f.write(output_data)
        print(f"✅ Results saved to {output}")
    else:
        print(output_data)


def main():
    parser = argparse.ArgumentParser(description="Query GraphRAG relations")
    parser.add_argument("--relationship-type", help="Filter by relationship type")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of results")
    parser.add_argument(
        "--min-confidence", type=float, default=0.0, help="Minimum confidence score"
    )
    parser.add_argument("--min-edge-weight", type=float, default=0.0, help="Minimum edge weight")
    parser.add_argument(
        "--format", choices=["table", "json", "csv"], default="table", help="Output format"
    )
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()
    query_relations(
        relationship_type=args.relationship_type,
        limit=args.limit,
        min_confidence=args.min_confidence,
        min_edge_weight=args.min_edge_weight,
        format=args.format,
        output=args.output,
    )


if __name__ == "__main__":
    main()
