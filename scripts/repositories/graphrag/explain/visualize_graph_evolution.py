#!/usr/bin/env python3
"""
Graph Evolution Visualizer

Visualizes how the graph structure evolves through the construction stage.
Shows step-by-step addition of relationships and tracks density/degree metrics.

Achievement 1.1: Transformation Explanation Tools

Usage:
    python visualize_graph_evolution.py --trace-id xyz
    python visualize_graph_evolution.py --trace-id xyz --format json
    python visualize_graph_evolution.py --trace-id xyz --output graph_evolution.json
"""

import argparse
import sys
import json
from typing import Optional, Dict, Any, List

from explain_utils import (
    get_mongodb_connection,
    find_relationship_creation_logs,
    format_section_header,
    format_subsection_header,
    format_key_value,
    format_json_output,
    print_error,
    validate_trace_id
)


def visualize_graph_evolution(
    trace_id: str,
    output_format: str = "text",
    output_file: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Visualize graph evolution through construction.
    
    Args:
        trace_id: Trace ID to visualize
        output_format: Output format (text, json)
        output_file: Optional output file path
        
    Returns:
        Evolution data dict (for JSON output) or None
    """
    client, db = get_mongodb_connection()
    
    try:
        # Validate trace_id
        if not validate_trace_id(db, trace_id):
            print_error(f"Trace ID '{trace_id}' not found")
            return None
        
        # Get all relationship creation/augmentation logs
        rel_logs = find_relationship_creation_logs(db, trace_id)
        
        # Count entities
        entity_count = db.entities_resolved.count_documents({"trace_id": trace_id})
        max_edges = entity_count * (entity_count - 1) if entity_count > 1 else 0
        
        # Group by source
        steps = {
            "llm": [],
            "co_occurrence": [],
            "semantic_similarity": [],
            "cross_chunk": []
        }
        
        for log in rel_logs:
            source = log.get("source", "llm")
            if source in steps:
                steps[source].append(log)
        
        # Calculate cumulative metrics
        evolution_steps = []
        cumulative_edges = 0
        
        for step_name, step_logs in [
            ("Step 1: LLM Relationships", steps["llm"]),
            ("Step 2: + Co-occurrence", steps["co_occurrence"]),
            ("Step 3: + Semantic Similarity", steps["semantic_similarity"]),
            ("Step 4: + Cross-chunk", steps["cross_chunk"])
        ]:
            edges_added = len(step_logs)
            cumulative_edges += edges_added
            
            density = cumulative_edges / max_edges if max_edges > 0 else 0
            avg_degree = (2 * cumulative_edges) / entity_count if entity_count > 0 else 0
            
            evolution_steps.append({
                "step": step_name,
                "edges_added": edges_added,
                "cumulative_edges": cumulative_edges,
                "density": density,
                "average_degree": avg_degree
            })
        
        # Build evolution data
        evolution = {
            "trace_id": trace_id,
            "entity_count": entity_count,
            "max_possible_edges": max_edges,
            "steps": evolution_steps,
            "breakdown": {
                "llm": len(steps["llm"]),
                "co_occurrence": len(steps["co_occurrence"]),
                "semantic_similarity": len(steps["semantic_similarity"]),
                "cross_chunk": len(steps["cross_chunk"])
            }
        }
        
        # Output
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(evolution, f, indent=2, default=str)
            print(f"✅ Evolution data saved to {output_file}")
        elif output_format == "json":
            print(format_json_output(evolution))
        else:
            print_text_evolution(evolution)
        
        return evolution
        
    finally:
        client.close()


def print_text_evolution(evolution: Dict[str, Any]):
    """Print evolution in text format."""
    print(format_section_header("GRAPH EVOLUTION VISUALIZATION"))
    
    print(f"Trace ID: {evolution['trace_id']}")
    print(f"Entity Count: {evolution['entity_count']}")
    print(f"Max Possible Edges: {evolution['max_possible_edges']}")
    
    print(format_subsection_header("Evolution Steps"))
    
    for step in evolution["steps"]:
        print(f"\n{step['step']}")
        print(format_key_value("  Edges Added", step['edges_added']))
        print(format_key_value("  Cumulative Edges", step['cumulative_edges']))
        print(format_key_value("  Graph Density", f"{step['density']:.4f}"))
        print(format_key_value("  Average Degree", f"{step['average_degree']:.2f}"))
    
    print(format_subsection_header("Breakdown by Source"))
    for source, count in evolution["breakdown"].items():
        print(f"  • {source}: {count} relationships")


def main():
    parser = argparse.ArgumentParser(
        description="Visualize graph evolution through construction stage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Visualize graph evolution
  python visualize_graph_evolution.py --trace-id xyz
  
  # JSON output
  python visualize_graph_evolution.py --trace-id xyz --format json
  
  # Save to file
  python visualize_graph_evolution.py --trace-id xyz --output graph_evolution.json
"""
    )
    
    parser.add_argument("--trace-id", required=True, help="Trace ID to visualize")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--output", help="Output file path (JSON format)")
    
    args = parser.parse_args()
    
    result = visualize_graph_evolution(
        trace_id=args.trace_id,
        output_format=args.format,
        output_file=args.output
    )
    
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()


