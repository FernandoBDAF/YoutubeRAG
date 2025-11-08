#!/usr/bin/env python3
"""
Query Graph Evolution

Track how graph metrics (density, degree distribution) evolved during construction
as different post-processing methods added relationships.
"""

import argparse
from typing import Optional

from query_utils import (
    get_mongodb_connection,
    build_trace_id_filter,
)


def query_graph_evolution(
    trace_id: str,
    format: str = "table",
    output: Optional[str] = None,
) -> None:
    """
    Track graph evolution during construction.
    
    Args:
        trace_id: Trace ID to analyze
        format: Output format
        output: Output file path
    """
    client, db = get_mongodb_connection()
    
    try:
        query = build_trace_id_filter(trace_id)
        
        # Get relationship creation events in chronological order
        create_events = list(
            db["transformation_logs"]
            .find({
                "trace_id": trace_id,
                "transformation_type": {"$in": ["relationship_create", "relationship_augment"]}
            })
            .sort("timestamp", 1)
        )
        
        if not create_events:
            print(f"No relationship creation events found for trace_id: {trace_id}")
            return
        
        # Count entities (for density calculation)
        entity_count = db["entities_resolved"].count_documents(query)
        
        # Track cumulative counts by method
        cumulative = {"LLM": 0, "co_occurrence": 0, "semantic_similarity": 0, "other": 0}
        total = 0
        
        evolution_points = []
        
        for event in create_events:
            trans_type = event.get("transformation_type")
            details = event.get("details", {})
            
            if trans_type == "relationship_create":
                method = "LLM"
                cumulative["LLM"] += 1
            else:  # relationship_augment
                method = details.get("method", "other")
                if method in cumulative:
                    cumulative[method] += 1
                else:
                    cumulative["other"] += 1
            
            total += 1
            
            # Calculate density (every 50 relationships or at key points)
            if total % 50 == 0 or total == len(create_events):
                density = (total / (entity_count * (entity_count - 1))) if entity_count > 1 else 0
                evolution_points.append({
                    "relationship_count": total,
                    "density": density,
                    "llm_count": cumulative["LLM"],
                    "co_occurrence_count": cumulative["co_occurrence"],
                    "semantic_count": cumulative["semantic_similarity"],
                    "other_count": cumulative["other"],
                })
        
        # Print evolution summary
        print("\n" + "=" * 80)
        print(f"  Graph Evolution for {trace_id}")
        print("=" * 80)
        print(f"\n📊 Evolution Points ({len(evolution_points)} snapshots):\n")
        print(f"{'Rels':<8} {'Density':<10} {'LLM':<8} {'Co-Occur':<10} {'Semantic':<10} {'Other':<8}")
        print("-" * 80)
        
        for point in evolution_points:
            print(f"{point['relationship_count']:<8} "
                  f"{point['density']:<10.4f} "
                  f"{point['llm_count']:<8} "
                  f"{point['co_occurrence_count']:<10} "
                  f"{point['semantic_count']:<10} "
                  f"{point['other_count']:<8}")
        
        print("=" * 80 + "\n")
        
        # If output file specified, write JSON
        if output:
            import json
            output_data = {
                "trace_id": trace_id,
                "entity_count": entity_count,
                "total_relationships": total,
                "evolution_points": evolution_points
            }
            with open(output, "w") as f:
                json.dump(output_data, f, indent=2, default=str)
            print(f"✅ Results saved to {output}")
        
    finally:
        client.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Track graph evolution during construction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Track graph evolution
  python query_graph_evolution.py --trace-id abc123

  # Export to JSON for plotting
  python query_graph_evolution.py --trace-id abc123 --output evolution.json

Use Case:
  "How did graph density evolve? When did co-occurrence add the most relationships?"
        """,
    )
    
    parser.add_argument("--trace-id", required=True, help="Trace ID to analyze")
    parser.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    parser.add_argument("--output", help="Output file path (optional)")
    
    args = parser.parse_args()
    
    query_graph_evolution(
        trace_id=args.trace_id,
        format=args.format,
        output=args.output,
    )


if __name__ == "__main__":
    main()


