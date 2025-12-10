#!/usr/bin/env python3
"""
Query Video Chunks

Query video chunks from the video_chunks collection with filters.
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
def query_chunks(
    video_id: Optional[str] = None,
    limit: int = 20,
    min_trust_score: float = 0.0,
    format: str = "table",
    output: Optional[str] = None,
) -> None:
    """Query video chunks."""
    mongo_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DB_NAME", "mongo_hack")

    if not mongo_uri:
        print("❌ Error: MONGODB_URI not found in environment")
        sys.exit(1)

    client = MongoClient(mongo_uri)
    db = client[db_name]

    # Build query
    query: Dict[str, Any] = {}
    if video_id:
        query["video_id"] = video_id
    if min_trust_score > 0:
        query["trust_score"] = {"$gte": min_trust_score}

    # Query chunks
    chunks = list(db["video_chunks"].find(query).limit(limit).sort("trust_score", -1))

    if not chunks:
        print("No chunks found matching criteria")
        return

    # Format output
    if format == "json":
        output_data = json.dumps(chunks, indent=2, default=str)
    elif format == "csv":
        import csv
        from io import StringIO

        output_buffer = StringIO()
        if chunks:
            writer = csv.DictWriter(
                output_buffer,
                fieldnames=["chunk_id", "video_id", "trust_score", "is_redundant", "text_length"],
            )
            writer.writeheader()
            for chunk in chunks:
                text = chunk.get("chunk_text", "") or chunk.get("embedding_text", "")
                writer.writerow(
                    {
                        "chunk_id": chunk.get("chunk_id", ""),
                        "video_id": chunk.get("video_id", ""),
                        "trust_score": chunk.get("trust_score", 0.0),
                        "is_redundant": chunk.get("is_redundant", False),
                        "text_length": len(text),
                    }
                )
        output_data = output_buffer.getvalue()
    else:  # table
        output_lines = [
            f"\n📊 Video Chunks ({len(chunks)} results)",
            "=" * 100,
            f"{'Chunk ID':<40} {'Video ID':<20} {'Trust Score':<12} {'Redundant':<10} {'Text Length':<12}",
            "-" * 100,
        ]
        for chunk in chunks:
            chunk_id = str(chunk.get("chunk_id", ""))[:38]
            video_id = str(chunk.get("video_id", ""))[:18]
            trust = f"{chunk.get('trust_score', 0.0):.4f}"
            redundant = "Yes" if chunk.get("is_redundant", False) else "No"
            text = chunk.get("chunk_text", "") or chunk.get("embedding_text", "")
            text_len = len(text)
            output_lines.append(
                f"{chunk_id:<40} {video_id:<20} {trust:<12} {redundant:<10} {text_len:<12}"
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
    parser = argparse.ArgumentParser(description="Query video chunks")
    parser.add_argument("--video-id", help="Filter by video ID")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of results")
    parser.add_argument("--min-trust-score", type=float, default=0.0, help="Minimum trust score")
    parser.add_argument(
        "--format", choices=["table", "json", "csv"], default="table", help="Output format"
    )
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()
    query_chunks(
        video_id=args.video_id,
        limit=args.limit,
        min_trust_score=args.min_trust_score,
        format=args.format,
        output=args.output,
    )


if __name__ == "__main__":
    main()
