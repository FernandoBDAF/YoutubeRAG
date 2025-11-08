#!/usr/bin/env python3
"""
Query Resolution Decisions

Query entity merge decisions from transformation logs to understand why entities merged.
Uses the transformation_logs collection from Achievement 0.1 (Transformation Logging).
"""

import argparse
from typing import Optional

from query_utils import (
    get_mongodb_connection,
    output_results,
    build_trace_id_filter,
    add_common_arguments,
    print_summary
)


def query_resolution_decisions(
    trace_id: Optional[str] = None,
    merge_reason: Optional[str] = None,
    min_confidence: float = 0.0,
    limit: int = 20,
    format: str = "table",
    output: Optional[str] = None,
) -> None:
    """
    Query entity merge decisions from transformation logs.
    
    Args:
        trace_id: Filter by trace ID
        merge_reason: Filter by merge reason (fuzzy, embedding, context)
        min_confidence: Minimum confidence score
        limit: Maximum number of results
        format: Output format
        output: Output file path
    """
    client, db = get_mongodb_connection()
    
    try:
        # Build query for entity_merge transformations
        query = build_trace_id_filter(trace_id)
        query["transformation_type"] = "entity_merge"
        
        if merge_reason:
            query["details.merge_reason"] = merge_reason
        if min_confidence > 0:
            query["details.confidence"] = {"$gte": min_confidence}
        
        # Query transformation_logs collection
        merges = list(
            db["transformation_logs"]
            .find(query)
            .sort("details.confidence", -1)
            .limit(limit)
        )
        
        if not merges:
            print("No merge decisions found matching criteria")
            return
        
        # Print summary
        total_count = db["transformation_logs"].count_documents(query)
        
        # Count by merge reason
        reason_pipeline = [
            {"$match": query},
            {"$group": {"_id": "$details.merge_reason", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        reason_dist = list(db["transformation_logs"].aggregate(reason_pipeline))
        
        print_summary("Resolution Decisions Query", {
            "Total Merges": total_count,
            "Showing": len(merges),
            "Trace ID": trace_id or "All",
            "Merge Reasons": ", ".join([f"{r['_id']}: {r['count']}" for r in reason_dist[:3]])
        })
        
        # Format merge data for output
        formatted_merges = []
        for merge in merges:
            details = merge.get("details", {})
            formatted_merges.append({
                "from_entity": details.get("from_entity_id", "")[:36],
                "from_name": details.get("from_name", ""),
                "to_entity": details.get("to_entity_id", "")[:36],
                "to_name": details.get("to_name", ""),
                "merge_reason": details.get("merge_reason", ""),
                "confidence": details.get("confidence", 0.0),
                "similarity": details.get("similarity_score", 0.0),
                "timestamp": merge.get("timestamp", ""),
            })
        
        # Format output
        table_columns = [
            ("from_name", "From Name", 25),
            ("to_name", "To Name", 25),
            ("merge_reason", "Reason", 12),
            ("confidence", "Confidence", 10),
            ("similarity", "Similarity", 10),
        ]
        
        csv_columns = [
            "from_entity", "from_name", "to_entity", "to_name",
            "merge_reason", "confidence", "similarity", "timestamp"
        ]
        
        metadata = {
            "query": "resolution_decisions",
            "trace_id": trace_id,
            "merge_reason": merge_reason,
            "total_count": total_count
        }
        
        output_results(
            formatted_merges,
            format,
            output,
            table_columns=table_columns,
            csv_columns=csv_columns,
            title="Entity Merge Decisions",
            metadata=metadata
        )
        
    finally:
        client.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Query entity merge decisions from transformation logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query all merge decisions from a pipeline run
  python query_resolution_decisions.py --trace-id abc123

  # Query only fuzzy matches
  python query_resolution_decisions.py --trace-id abc123 --merge-reason fuzzy

  # Query high-confidence merges
  python query_resolution_decisions.py --trace-id abc123 --min-confidence 0.9

  # Export to JSON
  python query_resolution_decisions.py --trace-id abc123 --format json --output merges.json

Use Case:
  "Why did entity A merge with entity B? What was the confidence and similarity?"
        """,
    )
    
    add_common_arguments(parser)
    parser.add_argument(
        "--merge-reason",
        choices=["fuzzy", "embedding", "context"],
        help="Filter by merge reason"
    )
    parser.add_argument("--min-confidence", type=float, default=0.0, help="Minimum confidence score")
    
    args = parser.parse_args()
    
    query_resolution_decisions(
        trace_id=args.trace_id,
        merge_reason=args.merge_reason,
        min_confidence=args.min_confidence,
        limit=args.limit,
        format=args.format,
        output=args.output,
    )


if __name__ == "__main__":
    main()


