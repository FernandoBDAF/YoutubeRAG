#!/usr/bin/env python3
"""
Compare Before/After Construction

Compare raw relationships vs. final relationships to measure post-processing impact.
Shows which methods (co-occurrence, semantic similarity, etc.) added how many relationships.
"""

import argparse
from typing import Optional

from query_utils import (
    get_mongodb_connection,
    build_trace_id_filter,
)


def compare_before_after_construction(
    trace_id: str,
    format: str = "table",
    output: Optional[str] = None,
) -> None:
    """
    Compare raw vs. final relationships.
    
    Args:
        trace_id: Trace ID to analyze
        format: Output format
        output: Output file path
    """
    client, db = get_mongodb_connection()
    
    try:
        query = build_trace_id_filter(trace_id)
        
        # Count raw relationships
        raw_count = db["relations_raw"].count_documents(query)
        
        # Count final relationships
        final_count = db["relations_final"].count_documents(query)
        
        if raw_count == 0:
            print(f"No raw relationships found for trace_id: {trace_id}")
            return
        
        # Calculate increase
        added_count = final_count - raw_count
        increase_pct = (added_count / raw_count * 100) if raw_count > 0 else 0
        
        # Get method distribution from transformation logs
        method_pipeline = [
            {"$match": {
                "trace_id": trace_id,
                "transformation_type": "relationship_augment"
            }},
            {"$group": {"_id": "$details.method", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        method_dist = {m["_id"]: m["count"] for m in db["transformation_logs"].aggregate(method_pipeline)}
        
        # Print detailed summary
        print("\n" + "=" * 80)
        print(f"  Construction Comparison for {trace_id}")
        print("=" * 80)
        print(f"\n📊 Relationship Counts:")
        print(f"  Raw Relationships (before):  {raw_count}")
        print(f"  Final Relationships (after): {final_count}")
        print(f"  Relationships Added:         {added_count}")
        print(f"  Increase:                    {increase_pct:.1f}%")
        
        if method_dist:
            print(f"\n📈 Post-Processing Methods:")
            for method, count in sorted(method_dist.items(), key=lambda x: x[1], reverse=True):
                pct = (count / added_count * 100) if added_count > 0 else 0
                print(f"  {method:25s}: +{count:4d} ({pct:.1f}%)")
        
        print("=" * 80 + "\n")
        
        # If output file specified, write JSON
        if output:
            import json
            output_data = {
                "trace_id": trace_id,
                "raw_count": raw_count,
                "final_count": final_count,
                "relationships_added": added_count,
                "increase_percent": increase_pct,
                "methods": method_dist
            }
            with open(output, "w") as f:
                json.dump(output_data, f, indent=2, default=str)
            print(f"✅ Results saved to {output}")
        
    finally:
        client.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Compare raw vs. final relationships",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare relationships before/after post-processing
  python compare_before_after_construction.py --trace-id abc123

  # Export comparison to JSON
  python compare_before_after_construction.py --trace-id abc123 --output comparison.json

Use Case:
  "How much did post-processing add? Which methods contributed most?"
        """,
    )
    
    parser.add_argument("--trace-id", required=True, help="Trace ID to analyze")
    parser.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    parser.add_argument("--output", help="Output file path (optional)")
    
    args = parser.parse_args()
    
    compare_before_after_construction(
        trace_id=args.trace_id,
        format=args.format,
        output=args.output,
    )


if __name__ == "__main__":
    main()


