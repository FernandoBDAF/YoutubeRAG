#!/usr/bin/env python3
"""
Compare Before/After Resolution

Compare raw entities vs. resolved entities to measure resolution effectiveness.
Uses entities_raw and entities_resolved collections from Achievement 0.2.
"""

import argparse
from typing import Optional

from query_utils import (
    get_mongodb_connection,
    build_trace_id_filter,
    print_summary
)


def compare_before_after_resolution(
    trace_id: str,
    format: str = "table",
    output: Optional[str] = None,
) -> None:
    """
    Compare raw vs. resolved entities.
    
    Args:
        trace_id: Trace ID to analyze
        format: Output format
        output: Output file path
    """
    client, db = get_mongodb_connection()
    
    try:
        query = build_trace_id_filter(trace_id)
        
        # Count raw entities
        raw_count = db["entities_raw"].count_documents(query)
        
        # Count resolved entities
        resolved_count = db["entities_resolved"].count_documents(query)
        
        if raw_count == 0:
            print(f"No raw entities found for trace_id: {trace_id}")
            return
        
        # Calculate merge rate
        merge_rate = ((raw_count - resolved_count) / raw_count * 100) if raw_count > 0 else 0
        
        # Get type distribution for raw
        raw_type_pipeline = [
            {"$match": query},
            {"$group": {"_id": "$entity_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        raw_types = {t["_id"]: t["count"] for t in db["entities_raw"].aggregate(raw_type_pipeline)}
        
        # Get type distribution for resolved
        resolved_type_pipeline = [
            {"$match": query},
            {"$group": {"_id": "$type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        resolved_types = {t["_id"]: t["count"] for t in db["entities_resolved"].aggregate(resolved_type_pipeline)}
        
        # Get confidence stats for raw
        raw_conf_pipeline = [
            {"$match": query},
            {"$group": {
                "_id": None,
                "avg": {"$avg": "$confidence"},
                "min": {"$min": "$confidence"},
                "max": {"$max": "$confidence"}
            }}
        ]
        raw_conf = list(db["entities_raw"].aggregate(raw_conf_pipeline))
        
        # Print detailed summary
        print("\n" + "=" * 80)
        print(f"  Resolution Comparison for {trace_id}")
        print("=" * 80)
        print(f"\n📊 Entity Counts:")
        print(f"  Raw Entities (before):     {raw_count}")
        print(f"  Resolved Entities (after): {resolved_count}")
        print(f"  Entities Merged:           {raw_count - resolved_count}")
        print(f"  Merge Rate:                {merge_rate:.1f}%")
        
        print(f"\n📈 Type Distribution Changes:")
        all_types = set(raw_types.keys()) | set(resolved_types.keys())
        for entity_type in sorted(all_types):
            raw_c = raw_types.get(entity_type, 0)
            res_c = resolved_types.get(entity_type, 0)
            change = res_c - raw_c
            change_str = f"{change:+d}" if change != 0 else "0"
            print(f"  {entity_type:20s}: {raw_c:4d} → {res_c:4d} ({change_str})")
        
        if raw_conf:
            print(f"\n📊 Confidence Stats (Raw):")
            print(f"  Average: {raw_conf[0]['avg']:.4f}")
            print(f"  Min:     {raw_conf[0]['min']:.4f}")
            print(f"  Max:     {raw_conf[0]['max']:.4f}")
        
        print("=" * 80 + "\n")
        
        # If output file specified, write JSON
        if output:
            import json
            output_data = {
                "trace_id": trace_id,
                "raw_count": raw_count,
                "resolved_count": resolved_count,
                "entities_merged": raw_count - resolved_count,
                "merge_rate_percent": merge_rate,
                "type_distribution": {
                    "raw": raw_types,
                    "resolved": resolved_types
                },
                "confidence_stats": raw_conf[0] if raw_conf else {}
            }
            with open(output, "w") as f:
                json.dump(output_data, f, indent=2, default=str)
            print(f"✅ Results saved to {output}")
        
    finally:
        client.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Compare raw vs. resolved entities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare entities before/after resolution
  python compare_before_after_resolution.py --trace-id abc123

  # Export comparison to JSON
  python compare_before_after_resolution.py --trace-id abc123 --output comparison.json

Use Case:
  "How effective is entity resolution? What's the merge rate? How did type distribution change?"
        """,
    )
    
    parser.add_argument("--trace-id", required=True, help="Trace ID to analyze")
    parser.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    parser.add_argument("--output", help="Output file path (optional)")
    
    args = parser.parse_args()
    
    compare_before_after_resolution(
        trace_id=args.trace_id,
        format=args.format,
        output=args.output,
    )


if __name__ == "__main__":
    main()


