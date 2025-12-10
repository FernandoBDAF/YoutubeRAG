#!/usr/bin/env python3
"""
Compare Detection Algorithms

Compare community detection results from different algorithms
(Leiden, Louvain, Infomap) to identify which works best for your data.
"""

import argparse
from typing import List

from query_utils import (
    get_mongodb_connection,
)


def compare_detection_algorithms(
    trace_ids: List[str],
    format: str = "table",
    output: str = None,
) -> None:
    """
    Compare detection algorithms across runs.
    
    Args:
        trace_ids: List of trace IDs to compare (each using different algorithm)
        format: Output format
        output: Output file path
    """
    client, db = get_mongodb_connection()
    
    try:
        comparison_results = []
        
        for trace_id in trace_ids:
            # Get community formation events
            community_events = list(
                db["transformation_logs"]
                .find({
                    "trace_id": trace_id,
                    "transformation_type": "community_form"
                })
            )
            
            if not community_events:
                print(f"Warning: No community events found for trace_id: {trace_id}")
                continue
            
            # Extract algorithm and metrics from first event
            first_event = community_events[0]
            details = first_event.get("details", {})
            
            algorithm = details.get("algorithm", "unknown")
            modularity = details.get("modularity", 0.0)
            community_count = details.get("community_count", 0)
            
            # Get community size distribution
            sizes = [e.get("details", {}).get("size", 0) for e in community_events]
            avg_size = sum(sizes) / len(sizes) if sizes else 0
            max_size = max(sizes) if sizes else 0
            min_size = min(sizes) if sizes else 0
            
            # Count singletons
            singletons = sum(1 for s in sizes if s == 1)
            singleton_rate = (singletons / len(sizes) * 100) if sizes else 0
            
            result = {
                "trace_id": trace_id,
                "algorithm": algorithm,
                "modularity": modularity,
                "community_count": community_count,
                "avg_size": avg_size,
                "max_size": max_size,
                "min_size": min_size,
                "singletons": singletons,
                "singleton_rate": singleton_rate,
            }
            
            comparison_results.append(result)
        
        if not comparison_results:
            print("No detection results found for specified trace IDs")
            return
        
        # Print comparison table
        print("\n" + "=" * 100)
        print(f"  Community Detection Algorithm Comparison")
        print("=" * 100)
        print(f"\n{'Trace ID':<38} {'Algorithm':<12} {'Modularity':<12} {'Communities':<12} {'Avg Size':<10}")
        print("-" * 100)
        
        for result in comparison_results:
            print(f"{result['trace_id']:<38} "
                  f"{result['algorithm']:<12} "
                  f"{result['modularity']:<12.4f} "
                  f"{result['community_count']:<12} "
                  f"{result['avg_size']:<10.2f}")
        
        print("=" * 100)
        
        # Print recommendation
        if len(comparison_results) > 1:
            best = max(comparison_results, key=lambda x: x['modularity'])
            print(f"\n💡 Recommendation: {best['algorithm']} has highest modularity ({best['modularity']:.4f})")
        
        print()
        
        # If output file specified, write JSON
        if output:
            import json
            output_data = {
                "comparison": comparison_results,
                "best_algorithm": max(comparison_results, key=lambda x: x['modularity'])['algorithm'] if comparison_results else None
            }
            with open(output, "w") as f:
                json.dump(output_data, f, indent=2, default=str)
            print(f"✅ Results saved to {output}")
        
    finally:
        client.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Compare community detection algorithms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare two detection runs
  python compare_detection_algorithms.py --trace-ids leiden_run louvain_run

  # Compare multiple algorithms
  python compare_detection_algorithms.py --trace-ids run1 run2 run3 --output comparison.json

Use Case:
  "Should I use Leiden or Louvain? Which algorithm works best for my data?"
        """,
    )
    
    parser.add_argument(
        "--trace-ids",
        nargs="+",
        required=True,
        help="Trace IDs to compare (space-separated, each using different algorithm)"
    )
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)"
    )
    parser.add_argument("--output", help="Output file path (optional)")
    
    args = parser.parse_args()
    
    compare_detection_algorithms(
        trace_ids=args.trace_ids,
        format=args.format,
        output=args.output,
    )


if __name__ == "__main__":
    main()


