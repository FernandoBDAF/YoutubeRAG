#!/usr/bin/env python3
"""
Relationship Filter Explainer

Explains why a relationship between two entities was kept or dropped during graph construction.
Shows all extraction attempts, filtering decisions, confidence scores, and thresholds.

Achievement 1.1: Transformation Explanation Tools

Usage:
    python explain_relationship_filter.py --source "Apple" --target "iPhone"
    python explain_relationship_filter.py --source-id abc123 --target-id def456 --trace-id xyz
    python explain_relationship_filter.py --source "Google" --target "Android" --format json
"""

import argparse
import sys
from typing import Optional, Dict, Any, List

from explain_utils import (
    get_mongodb_connection,
    find_entity_by_name,
    find_entity_by_id,
    find_relationship_filter_logs,
    format_section_header,
    format_key_value,
    format_json_output,
    print_error,
    validate_trace_id
)


def explain_relationship_filter(
    source_name: Optional[str] = None,
    source_id: Optional[str] = None,
    target_name: Optional[str] = None,
    target_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    output_format: str = "text"
) -> Optional[Dict[str, Any]]:
    """
    Explain relationship filtering decisions.
    
    Args:
        source_name: Source entity name
        source_id: Source entity ID
        target_name: Target entity name
        target_id: Target entity ID
        trace_id: Optional trace ID to filter by
        output_format: Output format (text, json)
        
    Returns:
        Explanation data dict (for JSON output) or None
    """
    client, db = get_mongodb_connection()
    
    try:
        # Validate trace_id if provided
        if trace_id and not validate_trace_id(db, trace_id):
            print_error(f"Trace ID '{trace_id}' not found")
            return None
        
        # Find entities
        if source_id:
            source_entity = find_entity_by_id(db, source_id, trace_id)
        elif source_name:
            source_entity = find_entity_by_name(db, source_name, trace_id)
        else:
            print_error("Must provide either --source or --source-id")
            return None
        
        if target_id:
            target_entity = find_entity_by_id(db, target_id, trace_id)
        elif target_name:
            target_entity = find_entity_by_name(db, target_name, trace_id)
        else:
            print_error("Must provide either --target or --target-id")
            return None
        
        if not source_entity:
            print_error(f"Source entity not found: {source_name or source_id}")
            return None
        
        if not target_entity:
            print_error(f"Target entity not found: {target_name or target_id}")
            return None
        
        # Find filter logs
        filter_logs = find_relationship_filter_logs(
            db,
            source_entity["entity_id"],
            target_entity["entity_id"],
            trace_id
        )
        
        # Check if relationship exists in final graph
        final_relationship = db.relations_final.find_one({
            "source_id": source_entity["entity_id"],
            "target_id": target_entity["entity_id"],
            "trace_id": trace_id
        }) if trace_id else db.relations_final.find_one({
            "source_id": source_entity["entity_id"],
            "target_id": target_entity["entity_id"]
        })
        
        # Build explanation
        explanation = {
            "trace_id": trace_id or source_entity.get("trace_id", "unknown"),
            "source_entity": {
                "entity_id": source_entity["entity_id"],
                "name": source_entity.get("name", "unknown"),
                "type": source_entity.get("type", "unknown")
            },
            "target_entity": {
                "entity_id": target_entity["entity_id"],
                "name": target_entity.get("name", "unknown"),
                "type": target_entity.get("type", "unknown")
            },
            "final_status": "kept" if final_relationship else "dropped",
            "extraction_attempts": len(filter_logs),
            "filter_decisions": [],
            "final_relationship": None
        }
        
        # Process filter logs
        for log in filter_logs:
            decision = {
                "operation": log.get("operation"),
                "reason": log.get("reason", "No reason provided"),
                "confidence": log.get("confidence", 0),
                "predicate": log.get("predicate", "unknown"),
                "timestamp": log.get("timestamp")
            }
            explanation["filter_decisions"].append(decision)
        
        if final_relationship:
            explanation["final_relationship"] = {
                "predicate": final_relationship.get("predicate", "unknown"),
                "confidence": final_relationship.get("confidence", 0),
                "source": final_relationship.get("source", "unknown")
            }
        
        # Output
        if output_format == "json":
            print(format_json_output(explanation))
        else:
            print_text_explanation(explanation)
        
        return explanation
        
    finally:
        client.close()


def print_text_explanation(explanation: Dict[str, Any]):
    """Print explanation in text format."""
    print(format_section_header("RELATIONSHIP FILTER EXPLANATION"))
    
    print(f"Trace ID: {explanation['trace_id']}")
    print(f"Final Status: {'✅ KEPT' if explanation['final_status'] == 'kept' else '❌ DROPPED'}")
    
    print(f"\nSource Entity: {explanation['source_entity']['name']} ({explanation['source_entity']['type']})")
    print(f"Target Entity: {explanation['target_entity']['name']} ({explanation['target_entity']['type']})")
    
    print(f"\nExtraction Attempts: {explanation['extraction_attempts']}")
    
    if explanation["filter_decisions"]:
        print("\nFilter Decisions:")
        for i, decision in enumerate(explanation["filter_decisions"], 1):
            print(f"\n  Decision {i}:")
            print(format_key_value("    Predicate", decision["predicate"], 4))
            print(format_key_value("    Confidence", f"{decision['confidence']:.3f}", 4))
            print(format_key_value("    Reason", decision["reason"], 4))
    
    if explanation["final_relationship"]:
        print("\nFinal Relationship:")
        rel = explanation["final_relationship"]
        print(format_key_value("  Predicate", rel["predicate"]))
        print(format_key_value("  Confidence", f"{rel['confidence']:.3f}"))
        print(format_key_value("  Source", rel["source"]))
    else:
        print("\nNo relationship exists in final graph.")


def main():
    parser = argparse.ArgumentParser(
        description="Explain why a relationship was kept or dropped",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Explain by entity names
  python explain_relationship_filter.py --source "Apple" --target "iPhone"
  
  # Explain by entity IDs
  python explain_relationship_filter.py --source-id abc123 --target-id def456
  
  # Filter by trace ID
  python explain_relationship_filter.py --source "Google" --target "Android" --trace-id xyz
  
  # JSON output
  python explain_relationship_filter.py --source "Tesla" --target "Elon Musk" --format json
"""
    )
    
    parser.add_argument("--source", help="Source entity name")
    parser.add_argument("--source-id", help="Source entity ID")
    parser.add_argument("--target", help="Target entity name")
    parser.add_argument("--target-id", help="Target entity ID")
    parser.add_argument("--trace-id", help="Filter by trace ID")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    result = explain_relationship_filter(
        source_name=args.source,
        source_id=args.source_id,
        target_name=args.target,
        target_id=args.target_id,
        trace_id=args.trace_id,
        output_format=args.format
    )
    
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()


