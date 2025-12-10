#!/usr/bin/env python3
"""
Entity Merge Explainer

Explains why two entities were merged (or not merged) during entity resolution.
Shows similarity scores, merge methods, confidence, and evidence from transformation logs.

Achievement 1.1: Transformation Explanation Tools

Usage:
    python explain_entity_merge.py --entity-a "Barack Obama" --entity-b "President Obama"
    python explain_entity_merge.py --entity-id-a abc123 --entity-id-b def456 --trace-id xyz
    python explain_entity_merge.py --entity-a "Apple" --entity-b "Apple Inc" --format json
"""

import argparse
import sys
from typing import Optional, Dict, Any

from explain_utils import (
    get_mongodb_connection,
    find_entity_by_name,
    find_entity_by_id,
    find_merge_logs,
    format_section_header,
    format_key_value,
    format_json_output,
    print_error,
    print_warning,
    validate_trace_id
)


def explain_entity_merge(
    entity_a_name: Optional[str] = None,
    entity_a_id: Optional[str] = None,
    entity_b_name: Optional[str] = None,
    entity_b_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    output_format: str = "text"
) -> Optional[Dict[str, Any]]:
    """
    Explain entity merge decision.
    
    Args:
        entity_a_name: First entity name
        entity_a_id: First entity ID
        entity_b_name: Second entity name
        entity_b_id: Second entity ID
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
        if entity_a_id:
            entity_a = find_entity_by_id(db, entity_a_id, trace_id)
        elif entity_a_name:
            entity_a = find_entity_by_name(db, entity_a_name, trace_id)
        else:
            print_error("Must provide either --entity-a or --entity-id-a")
            return None
        
        if entity_b_id:
            entity_b = find_entity_by_id(db, entity_b_id, trace_id)
        elif entity_b_name:
            entity_b = find_entity_by_name(db, entity_b_name, trace_id)
        else:
            print_error("Must provide either --entity-b or --entity-id-b")
            return None
        
        if not entity_a:
            print_error(f"Entity A not found: {entity_a_name or entity_a_id}")
            return None
        
        if not entity_b:
            print_error(f"Entity B not found: {entity_b_name or entity_b_id}")
            return None
        
        # Find merge logs for both entities
        merge_logs_a = find_merge_logs(db, entity_a["entity_id"], trace_id)
        merge_logs_b = find_merge_logs(db, entity_b["entity_id"], trace_id)
        
        # Find merge log between these two entities
        merge_log = None
        for log in merge_logs_a:
            before = log.get("before", {})
            after = log.get("after", {})
            
            # Check if this log involves both entities
            if (before.get("entity_id") in [entity_a["entity_id"], entity_b["entity_id"]] and
                after.get("entity_id") in [entity_a["entity_id"], entity_b["entity_id"]]):
                merge_log = log
                break
        
        # Build explanation data
        explanation = {
            "trace_id": trace_id or entity_a.get("trace_id", "unknown"),
            "entity_a": {
                "entity_id": entity_a["entity_id"],
                "name": entity_a.get("name", "unknown"),
                "type": entity_a.get("type", "unknown"),
                "confidence": entity_a.get("confidence", 0),
                "chunk_ids": entity_a.get("chunk_ids", [])
            },
            "entity_b": {
                "entity_id": entity_b["entity_id"],
                "name": entity_b.get("name", "unknown"),
                "type": entity_b.get("type", "unknown"),
                "confidence": entity_b.get("confidence", 0),
                "chunk_ids": entity_b.get("chunk_ids", [])
            },
            "merge_decision": "merged" if merge_log else "not_merged",
            "merge_details": None
        }
        
        if merge_log:
            before = merge_log.get("before", {})
            after = merge_log.get("after", {})
            
            explanation["merge_details"] = {
                "method": merge_log.get("method", "unknown"),
                "similarity_score": merge_log.get("similarity", 0),
                "confidence": merge_log.get("confidence", 0),
                "reason": merge_log.get("reason", "No reason provided"),
                "timestamp": merge_log.get("timestamp"),
                "before_name": before.get("name", "unknown"),
                "after_name": after.get("name", "unknown")
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
    print(format_section_header("ENTITY MERGE EXPLANATION"))
    
    print(f"Trace ID: {explanation['trace_id']}")
    print(f"Merge Decision: {'✅ MERGED' if explanation['merge_decision'] == 'merged' else '❌ NOT MERGED'}")
    
    print("\nEntity A:")
    entity_a = explanation["entity_a"]
    print(format_key_value("  Name", entity_a["name"]))
    print(format_key_value("  Type", entity_a["type"]))
    print(format_key_value("  Confidence", f"{entity_a['confidence']:.3f}"))
    print(format_key_value("  Chunks", entity_a["chunk_ids"]))
    
    print("\nEntity B:")
    entity_b = explanation["entity_b"]
    print(format_key_value("  Name", entity_b["name"]))
    print(format_key_value("  Type", entity_b["type"]))
    print(format_key_value("  Confidence", f"{entity_b['confidence']:.3f}"))
    print(format_key_value("  Chunks", entity_b["chunk_ids"]))
    
    if explanation["merge_details"]:
        print("\nMerge Details:")
        details = explanation["merge_details"]
        print(format_key_value("  Method", details["method"]))
        print(format_key_value("  Similarity Score", f"{details['similarity_score']:.3f}"))
        print(format_key_value("  Confidence", f"{details['confidence']:.3f}"))
        print(format_key_value("  Reason", details["reason"]))
        print(format_key_value("  Before Name", details["before_name"]))
        print(format_key_value("  After Name", details["after_name"]))
    else:
        print("\nNo merge occurred between these entities.")
        print("Possible reasons:")
        print("  - Similarity score below threshold")
        print("  - Different entity types")
        print("  - Insufficient evidence for merge")


def main():
    parser = argparse.ArgumentParser(
        description="Explain why two entities were merged (or not merged)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Explain merge by entity names
  python explain_entity_merge.py --entity-a "Barack Obama" --entity-b "President Obama"
  
  # Explain merge by entity IDs
  python explain_entity_merge.py --entity-id-a abc123 --entity-id-b def456
  
  # Filter by trace ID
  python explain_entity_merge.py --entity-a "Apple" --entity-b "Apple Inc" --trace-id xyz
  
  # JSON output
  python explain_entity_merge.py --entity-a "Google" --entity-b "Alphabet" --format json
"""
    )
    
    parser.add_argument("--entity-a", help="First entity name")
    parser.add_argument("--entity-id-a", help="First entity ID")
    parser.add_argument("--entity-b", help="Second entity name")
    parser.add_argument("--entity-id-b", help="Second entity ID")
    parser.add_argument("--trace-id", help="Filter by trace ID")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not (args.entity_a or args.entity_id_a):
        print_error("Must provide either --entity-a or --entity-id-a")
        sys.exit(1)
    
    if not (args.entity_b or args.entity_id_b):
        print_error("Must provide either --entity-b or --entity-id-b")
        sys.exit(1)
    
    result = explain_entity_merge(
        entity_a_name=args.entity_a,
        entity_a_id=args.entity_id_a,
        entity_b_name=args.entity_b,
        entity_b_id=args.entity_id_b,
        trace_id=args.trace_id,
        output_format=args.format
    )
    
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()


