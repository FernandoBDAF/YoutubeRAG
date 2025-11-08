#!/usr/bin/env python3
"""
Community Formation Explainer

Explains why entities were clustered into a specific community during community detection.
Shows community members, relationships, coherence factors, and algorithm parameters.

Achievement 1.1: Transformation Explanation Tools

Usage:
    python explain_community_formation.py --community-id comm_123
    python explain_community_formation.py --community-id comm_456 --trace-id xyz
    python explain_community_formation.py --community-id comm_789 --format json
"""

import argparse
import sys
from typing import Optional, Dict, Any

from explain_utils import (
    get_mongodb_connection,
    find_community,
    find_entity_by_id,
    format_section_header,
    format_key_value,
    format_json_output,
    print_error,
    validate_trace_id
)


def explain_community_formation(
    community_id: str,
    trace_id: Optional[str] = None,
    output_format: str = "text"
) -> Optional[Dict[str, Any]]:
    """
    Explain community formation.
    
    Args:
        community_id: Community ID to explain
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
        
        # Find community
        community = find_community(db, community_id, trace_id)
        
        if not community:
            print_error(f"Community not found: {community_id}")
            return None
        
        # Get community members
        entity_ids = community.get("entity_ids", [])
        members = []
        for entity_id in entity_ids[:10]:  # Limit to first 10 for display
            entity = find_entity_by_id(db, entity_id, trace_id)
            if entity:
                members.append({
                    "entity_id": entity_id,
                    "name": entity.get("name", "unknown"),
                    "type": entity.get("type", "unknown")
                })
        
        # Get relationships within community
        relationships_query = {
            "source_id": {"$in": entity_ids},
            "target_id": {"$in": entity_ids}
        }
        if trace_id:
            relationships_query["trace_id"] = trace_id
        
        relationships = list(db.relations_final.find(relationships_query))
        
        # Build explanation
        explanation = {
            "trace_id": trace_id or community.get("trace_id", "unknown"),
            "community_id": community_id,
            "size": len(entity_ids),
            "members_shown": len(members),
            "members": members,
            "relationships_within": len(relationships),
            "coherence_score": community.get("coherence_score", 0),
            "algorithm": community.get("algorithm", "unknown"),
            "parameters": community.get("parameters", {}),
            "modularity": community.get("modularity", 0)
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
    print(format_section_header("COMMUNITY FORMATION EXPLANATION"))
    
    print(f"Trace ID: {explanation['trace_id']}")
    print(f"Community ID: {explanation['community_id']}")
    print(f"Size: {explanation['size']} entities")
    
    print(f"\nAlgorithm: {explanation['algorithm']}")
    print(f"Modularity: {explanation['modularity']:.3f}")
    print(f"Coherence Score: {explanation['coherence_score']:.3f}")
    
    if explanation["parameters"]:
        print("\nAlgorithm Parameters:")
        for key, value in explanation["parameters"].items():
            print(format_key_value(f"  {key}", value))
    
    print(f"\nRelationships Within Community: {explanation['relationships_within']}")
    
    if explanation["members"]:
        print(f"\nCommunity Members (showing {explanation['members_shown']} of {explanation['size']}):")
        for member in explanation["members"]:
            print(f"  • {member['name']} ({member['type']})")
    
    print("\nWhy These Entities Clustered:")
    print("  • High density of relationships within group")
    print("  • Algorithm detected strong connectivity")
    print(f"  • Coherence score: {explanation['coherence_score']:.3f}")


def main():
    parser = argparse.ArgumentParser(
        description="Explain why entities were clustered into a community",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Explain community formation
  python explain_community_formation.py --community-id comm_123
  
  # Filter by trace ID
  python explain_community_formation.py --community-id comm_456 --trace-id xyz
  
  # JSON output
  python explain_community_formation.py --community-id comm_789 --format json
"""
    )
    
    parser.add_argument("--community-id", required=True, help="Community ID to explain")
    parser.add_argument("--trace-id", help="Filter by trace ID")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    result = explain_community_formation(
        community_id=args.community_id,
        trace_id=args.trace_id,
        output_format=args.format
    )
    
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()


