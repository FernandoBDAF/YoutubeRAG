#!/usr/bin/env python3
"""
Error Summary

Query and summarize errors from video_chunks and other collections.
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
def generate_error_summary(
    stage: Optional[str] = None,
    limit: int = 20,
    format: str = "table",
    output: Optional[str] = None,
) -> None:
    """Generate error summary from collections."""
    mongo_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DB_NAME", "mongo_hack")

    if not mongo_uri:
        print("❌ Error: MONGODB_URI not found in environment")
        sys.exit(1)

    client = MongoClient(mongo_uri)
    db = client[db_name]

    errors: Dict[str, Any] = {
        "extraction_errors": [],
        "resolution_errors": [],
        "construction_errors": [],
    }

    # Extraction errors
    extraction_query: Dict[str, Any] = {"graphrag_extraction.status": "failed"}
    if stage == "extraction":
        extraction_errors = list(db["video_chunks"].find(extraction_query).limit(limit))
        for chunk in extraction_errors:
            errors["extraction_errors"].append(
                {
                    "chunk_id": chunk.get("chunk_id"),
                    "video_id": chunk.get("video_id"),
                    "error": chunk.get("graphrag_extraction", {}).get("error", "unknown"),
                }
            )

    # Resolution errors
    resolution_query: Dict[str, Any] = {"graphrag_resolution.status": "failed"}
    if stage == "resolution" or not stage:
        resolution_errors = list(db["video_chunks"].find(resolution_query).limit(limit))
        for chunk in resolution_errors:
            errors["resolution_errors"].append(
                {
                    "chunk_id": chunk.get("chunk_id"),
                    "video_id": chunk.get("video_id"),
                    "error": chunk.get("graphrag_resolution", {}).get("error", "unknown"),
                }
            )

    # Construction errors
    construction_query: Dict[str, Any] = {"graphrag_construction.status": "failed"}
    if stage == "construction" or not stage:
        construction_errors = list(db["video_chunks"].find(construction_query).limit(limit))
        for chunk in construction_errors:
            errors["construction_errors"].append(
                {
                    "chunk_id": chunk.get("chunk_id"),
                    "video_id": chunk.get("video_id"),
                    "error": chunk.get("graphrag_construction", {}).get("error", "unknown"),
                }
            )

    # Format output
    if format == "json":
        output_data = json.dumps(errors, indent=2, default=str)
    else:  # table
        lines = ["\n📊 Error Summary", "=" * 80]

        if errors["extraction_errors"]:
            lines.append(f"\n❌ Extraction Errors ({len(errors['extraction_errors'])}):")
            for err in errors["extraction_errors"][:10]:
                lines.append(f"  Chunk: {err['chunk_id']}, Error: {err['error']}")

        if errors["resolution_errors"]:
            lines.append(f"\n❌ Resolution Errors ({len(errors['resolution_errors'])}):")
            for err in errors["resolution_errors"][:10]:
                lines.append(f"  Chunk: {err['chunk_id']}, Error: {err['error']}")

        if errors["construction_errors"]:
            lines.append(f"\n❌ Construction Errors ({len(errors['construction_errors'])}):")
            for err in errors["construction_errors"][:10]:
                lines.append(f"  Chunk: {err['chunk_id']}, Error: {err['error']}")

        total_errors = sum(len(v) for v in errors.values())
        if total_errors == 0:
            lines.append("\n✅ No errors found")

        lines.append("=" * 80)
        output_data = "\n".join(lines)

    if output:
        with open(output, "w") as f:
            f.write(output_data)
        print(f"✅ Error summary saved to {output}")
    else:
        print(output_data)


def main():
    parser = argparse.ArgumentParser(description="Generate error summary")
    parser.add_argument(
        "--stage", choices=["extraction", "resolution", "construction"], help="Filter by stage"
    )
    parser.add_argument("--limit", type=int, default=20, help="Maximum errors per stage")
    parser.add_argument(
        "--format", choices=["table", "json"], default="table", help="Output format"
    )
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()
    generate_error_summary(
        stage=args.stage,
        limit=args.limit,
        format=args.format,
        output=args.output,
    )


if __name__ == "__main__":
    main()
