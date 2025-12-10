#!/usr/bin/env python3
"""
Compare Extraction Runs

Compare entity extraction from different pipeline runs to identify quality differences.
Uses the entities_raw collection from IntermediateDataService (Achievement 0.2).
"""

import argparse
from typing import List

from query_utils import (
    get_mongodb_connection,
    output_results,
    print_summary
)


def compare_extraction_runs(
    trace_ids: List[str],
    format: str = "table",
    output: str = None,
) -> None:
    """
    Compare extraction from different runs.
    
    Args:
        trace_ids: List of trace IDs to compare
        format: Output format
        output: Output file path
    """
    client, db = get_mongodb_connection()
    
    try:
        comparison_results = []
        
        for trace_id in trace_ids:
            # Count entities
            total_entities = db["entities_raw"].count_documents({"trace_id": trace_id})
            
            # Get type distribution
            type_pipeline = [
                {"$match": {"trace_id": trace_id}},
                {"$group": {"_id": "$entity_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            type_dist = list(db["entities_raw"].aggregate(type_pipeline))
            
            # Get confidence stats
            conf_pipeline = [
                {"$match": {"trace_id": trace_id}},
                {"$group": {
                    "_id": None,
                    "avg_confidence": {"$avg": "$confidence"},
                    "min_confidence": {"$min": "$confidence"},
                    "max_confidence": {"$max": "$confidence"}
                }}
            ]
            conf_stats = list(db["entities_raw"].aggregate(conf_pipeline))
            
            # Build result
            result = {
                "trace_id": trace_id,
                "total_entities": total_entities,
                "unique_types": len(type_dist),
                "top_type": type_dist[0]["_id"] if type_dist else "N/A",
                "top_type_count": type_dist[0]["count"] if type_dist else 0,
                "avg_confidence": conf_stats[0]["avg_confidence"] if conf_stats else 0.0,
                "min_confidence": conf_stats[0]["min_confidence"] if conf_stats else 0.0,
                "max_confidence": conf_stats[0]["max_confidence"] if conf_stats else 0.0,
            }
            
            comparison_results.append(result)
        
        if not comparison_results:
            print("No extraction data found for specified trace IDs")
            return
        
        # Print summary
        print_summary("Extraction Comparison", {
            "Runs Compared": len(comparison_results),
            "Trace IDs": ", ".join(trace_ids),
        })
        
        # Format output
        table_columns = [
            ("trace_id", "Trace ID", 36),
            ("total_entities", "Total", 8),
            ("unique_types", "Types", 6),
            ("top_type", "Top Type", 15),
            ("top_type_count", "Top Count", 10),
            ("avg_confidence", "Avg Conf", 10),
        ]
        
        csv_columns = [
            "trace_id", "total_entities", "unique_types", "top_type",
            "top_type_count", "avg_confidence", "min_confidence", "max_confidence"
        ]
        
        metadata = {
            "query": "compare_extraction",
            "trace_ids": trace_ids,
            "runs_compared": len(comparison_results)
        }
        
        output_results(
            comparison_results,
            format,
            output,
            table_columns=table_columns,
            csv_columns=csv_columns,
            title="Extraction Run Comparison",
            metadata=metadata
        )
        
    finally:
        client.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Compare extraction from different pipeline runs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare two extraction runs
  python compare_extraction_runs.py --trace-ids abc123 def456

  # Compare multiple runs and export to CSV
  python compare_extraction_runs.py --trace-ids run1 run2 run3 --format csv --output comparison.csv

Use Case:
  "Did the new prompt extract more entities? How does extraction quality compare?"
        """,
    )
    
    parser.add_argument(
        "--trace-ids",
        nargs="+",
        required=True,
        help="Trace IDs to compare (space-separated)"
    )
    parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)"
    )
    parser.add_argument("--output", help="Output file path (optional)")
    
    args = parser.parse_args()
    
    compare_extraction_runs(
        trace_ids=args.trace_ids,
        format=args.format,
        output=args.output,
    )


if __name__ == "__main__":
    main()


