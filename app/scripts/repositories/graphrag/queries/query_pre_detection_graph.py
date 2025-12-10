#!/usr/bin/env python3
"""
Query Pre-Detection Graph

Analyze graph structure before community detection to understand
the input state for community algorithms.
"""

import argparse
from typing import Optional

from query_utils import (
    get_mongodb_connection,
    build_trace_id_filter,
)


def query_pre_detection_graph(
    trace_id: str,
    format: str = "table",
    output: Optional[str] = None,
) -> None:
    """
    Analyze graph before community detection.
    
    Args:
        trace_id: Trace ID to analyze
        format: Output format
        output: Output file path
    """
    client, db = get_mongodb_connection()
    
    try:
        query = build_trace_id_filter(trace_id)
        
        # Get graph snapshot
        graph_data = db["graph_pre_detection"].find_one(query)
        
        if not graph_data:
            print(f"No pre-detection graph found for trace_id: {trace_id}")
            return
        
        # Extract metrics
        node_count = graph_data.get("node_count", 0)
        edge_count = graph_data.get("edge_count", 0)
        density = graph_data.get("density", 0.0)
        avg_degree = graph_data.get("average_degree", 0.0)
        degree_dist = graph_data.get("degree_distribution", {})
        
        # Print detailed summary
        print("\n" + "=" * 80)
        print(f"  Pre-Detection Graph Analysis for {trace_id}")
        print("=" * 80)
        print(f"\n📊 Graph Structure:")
        print(f"  Nodes (Entities):    {node_count}")
        print(f"  Edges (Relationships): {edge_count}")
        print(f"  Density:             {density:.4f}")
        print(f"  Average Degree:      {avg_degree:.2f}")
        
        if degree_dist:
            print(f"\n📈 Degree Distribution:")
            # Show top degree nodes
            sorted_degrees = sorted(degree_dist.items(), key=lambda x: x[1], reverse=True)[:10]
            for entity_id, degree in sorted_degrees:
                print(f"  {entity_id[:40]:<40}: {degree} connections")
        
        # Connectivity analysis
        max_degree = max(degree_dist.values()) if degree_dist else 0
        min_degree = min(degree_dist.values()) if degree_dist else 0
        
        print(f"\n📊 Connectivity Stats:")
        print(f"  Max Degree:  {max_degree}")
        print(f"  Min Degree:  {min_degree}")
        print(f"  Isolated Nodes: {sum(1 for d in degree_dist.values() if d == 0)}")
        
        print("=" * 80 + "\n")
        
        # If output file specified, write JSON
        if output:
            import json
            output_data = {
                "trace_id": trace_id,
                "node_count": node_count,
                "edge_count": edge_count,
                "density": density,
                "average_degree": avg_degree,
                "max_degree": max_degree,
                "min_degree": min_degree,
                "degree_distribution": degree_dist
            }
            with open(output, "w") as f:
                json.dump(output_data, f, indent=2, default=str)
            print(f"✅ Results saved to {output}")
        
    finally:
        client.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze graph before community detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze pre-detection graph
  python query_pre_detection_graph.py --trace-id abc123

  # Export to JSON
  python query_pre_detection_graph.py --trace-id abc123 --output pre_graph.json

Use Case:
  "What did the graph look like before community detection? What's the connectivity?"
        """,
    )
    
    parser.add_argument("--trace-id", required=True, help="Trace ID to analyze")
    parser.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    parser.add_argument("--output", help="Output file path (optional)")
    
    args = parser.parse_args()
    
    query_pre_detection_graph(
        trace_id=args.trace_id,
        format=args.format,
        output=args.output,
    )


if __name__ == "__main__":
    main()


