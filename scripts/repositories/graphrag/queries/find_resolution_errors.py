#!/usr/bin/env python3
"""
Find Resolution Errors

Identify potential false positives (entities that shouldn't have merged)
and false negatives (entities that should have merged but didn't).
"""

import argparse
from typing import Optional

from query_utils import (
    get_mongodb_connection,
    output_results,
    build_trace_id_filter,
    print_summary
)


def find_resolution_errors(
    trace_id: str,
    confidence_threshold: float = 0.9,
    similarity_threshold: float = 0.7,
    limit: int = 20,
    format: str = "table",
    output: Optional[str] = None,
) -> None:
    """
    Find potential resolution errors.
    
    Args:
        trace_id: Trace ID to analyze
        confidence_threshold: High confidence threshold for false positive detection
        similarity_threshold: Low similarity threshold for false positive detection
        limit: Maximum number of results
        format: Output format
        output: Output file path
    """
    client, db = get_mongodb_connection()
    
    try:
        query = build_trace_id_filter(trace_id)
        query["transformation_type"] = "entity_merge"
        
        # Find suspicious merges: high confidence but low similarity
        suspicious_query = {
            **query,
            "details.confidence": {"$gte": confidence_threshold},
            "details.similarity_score": {"$lt": similarity_threshold}
        }
        
        suspicious_merges = list(
            db["transformation_logs"]
            .find(suspicious_query)
            .sort("details.confidence", -1)
            .limit(limit)
        )
        
        # Format results
        formatted_errors = []
        for merge in suspicious_merges:
            details = merge.get("details", {})
            formatted_errors.append({
                "from_name": details.get("from_name", ""),
                "to_name": details.get("to_name", ""),
                "merge_reason": details.get("merge_reason", ""),
                "confidence": details.get("confidence", 0.0),
                "similarity": details.get("similarity_score", 0.0),
                "issue": "High confidence, low similarity",
                "from_entity": details.get("from_entity_id", "")[:36],
                "to_entity": details.get("to_entity_id", "")[:36],
            })
        
        if not formatted_errors:
            print(f"No suspicious merges found for trace_id: {trace_id}")
            print(f"Criteria: confidence >= {confidence_threshold}, similarity < {similarity_threshold}")
            return
        
        # Print summary
        total_merges = db["transformation_logs"].count_documents(query)
        
        print_summary("Potential Resolution Errors", {
            "Total Merges": total_merges,
            "Suspicious Merges": len(formatted_errors),
            "Criteria": f"conf >= {confidence_threshold}, sim < {similarity_threshold}",
            "Trace ID": trace_id,
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
            "merge_reason", "confidence", "similarity", "issue"
        ]
        
        metadata = {
            "query": "find_resolution_errors",
            "trace_id": trace_id,
            "confidence_threshold": confidence_threshold,
            "similarity_threshold": similarity_threshold,
            "total_merges": total_merges,
            "suspicious_count": len(formatted_errors)
        }
        
        output_results(
            formatted_errors,
            format,
            output,
            table_columns=table_columns,
            csv_columns=csv_columns,
            title="Potential Resolution Errors (False Positives)",
            metadata=metadata
        )
        
        print("\n💡 Recommendation: Review these merges manually to confirm if they are false positives.")
        
    finally:
        client.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Find potential resolution errors (false positives/negatives)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Find suspicious merges with default thresholds
  python find_resolution_errors.py --trace-id abc123

  # Use stricter thresholds
  python find_resolution_errors.py --trace-id abc123 --confidence-threshold 0.95 --similarity-threshold 0.6

  # Export to CSV for review
  python find_resolution_errors.py --trace-id abc123 --format csv --output errors.csv

Use Case:
  "What resolution errors should I investigate? Which merges look suspicious?"
        """,
    )
    
    parser.add_argument("--trace-id", required=True, help="Trace ID to analyze")
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.9,
        help="High confidence threshold (default: 0.9)"
    )
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.7,
        help="Low similarity threshold (default: 0.7)"
    )
    parser.add_argument("--limit", type=int, default=20, help="Maximum results (default: 20)")
    parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format"
    )
    parser.add_argument("--output", help="Output file path (optional)")
    
    args = parser.parse_args()
    
    find_resolution_errors(
        trace_id=args.trace_id,
        confidence_threshold=args.confidence_threshold,
        similarity_threshold=args.similarity_threshold,
        limit=args.limit,
        format=args.format,
        output=args.output,
    )


if __name__ == "__main__":
    main()


