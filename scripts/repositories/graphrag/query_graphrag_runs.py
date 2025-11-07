#!/usr/bin/env python3
"""
Query GraphRAG Runs

Query pipeline run metadata from the graphrag_runs collection.
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from dotenv import load_dotenv
from pymongo import MongoClient
from core.libraries.error_handling.decorators import handle_errors

load_dotenv()


@handle_errors(log_traceback=True, reraise=True)
def query_runs(
    stage: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    format: str = "table",
    output: Optional[str] = None,
) -> None:
    """Query GraphRAG pipeline runs."""
    mongo_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DB_NAME", "mongo_hack")

    if not mongo_uri:
        print("❌ Error: MONGODB_URI not found in environment")
        sys.exit(1)

    client = MongoClient(mongo_uri)
    db = client[db_name]

    # Build query
    query: Dict[str, Any] = {}
    if stage:
        query["stage"] = stage
    if status:
        query["status"] = status

    # Query runs
    runs = list(db["graphrag_runs"].find(query).limit(limit).sort("started_at", -1))

    if not runs:
        print("No runs found matching criteria")
        return

    # Format output
    if format == "json":
        output_data = json.dumps(runs, indent=2, default=str)
    elif format == "csv":
        import csv
        from io import StringIO

        output_buffer = StringIO()
        if runs:
            writer = csv.DictWriter(
                output_buffer,
                fieldnames=[
                    "run_id",
                    "stage",
                    "status",
                    "started_at",
                    "completed_at",
                    "documents_processed",
                ],
            )
            writer.writeheader()
            for run in runs:
                writer.writerow(
                    {
                        "run_id": run.get("run_id", ""),
                        "stage": run.get("stage", ""),
                        "status": run.get("status", ""),
                        "started_at": run.get("started_at", ""),
                        "completed_at": run.get("completed_at", ""),
                        "documents_processed": run.get("documents_processed", 0),
                    }
                )
        output_data = output_buffer.getvalue()
    else:  # table
        output_lines = [
            f"\n📊 GraphRAG Runs ({len(runs)} results)",
            "=" * 120,
            f"{'Run ID':<40} {'Stage':<25} {'Status':<15} {'Started':<20} {'Documents':<10}",
            "-" * 120,
        ]
        for run in runs:
            run_id = str(run.get("run_id", ""))[:38]
            stage = str(run.get("stage", ""))[:23]
            status = str(run.get("status", ""))[:13]
            started = str(run.get("started_at", ""))[:18]
            docs = run.get("documents_processed", 0)
            output_lines.append(f"{run_id:<40} {stage:<25} {status:<15} {started:<20} {docs:<10}")
        output_lines.append("=" * 120)
        output_data = "\n".join(output_lines)

    if output:
        with open(output, "w") as f:
            f.write(output_data)
        print(f"✅ Results saved to {output}")
    else:
        print(output_data)


def main():
    parser = argparse.ArgumentParser(description="Query GraphRAG pipeline runs")
    parser.add_argument("--stage", help="Filter by stage name")
    parser.add_argument("--status", help="Filter by status (completed, failed, running)")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of results")
    parser.add_argument(
        "--format", choices=["table", "json", "csv"], default="table", help="Output format"
    )
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()
    query_runs(
        stage=args.stage,
        status=args.status,
        limit=args.limit,
        format=args.format,
        output=args.output,
    )


if __name__ == "__main__":
    main()
