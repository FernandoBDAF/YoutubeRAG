#!/usr/bin/env python3
"""
Entity Journey Tracer

Traces the complete transformation journey of an entity through all pipeline stages.
Shows extraction, resolution, graph construction, and community detection details.

Achievement 1.1: Transformation Explanation Tools

Usage:
    python trace_entity_journey.py --entity "Barack Obama"
    python trace_entity_journey.py --entity-id abc123 --trace-id xyz
    python trace_entity_journey.py --entity "Apple Inc" --format json
"""

import argparse
import sys
from typing import Optional, Dict, Any, List

from explain_utils import (
    get_mongodb_connection,
    find_entity_by_name,
    find_entity_by_id,
    find_entity_all_logs,
    get_entity_raw_mentions,
    get_entity_relationships,
    find_community,
    format_section_header,
    format_subsection_header,
    format_key_value,
    format_json_output,
    print_error,
    validate_trace_id,
    calculate_node_degree,
    group_relationships_by_source
)


def trace_entity_journey(
    entity_name: Optional[str] = None,
    entity_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    output_format: str = "text"
) -> Optional[Dict[str, Any]]:
    """
    Trace complete entity journey through pipeline.
    
    Args:
        entity_name: Entity name
        entity_id: Entity ID
        trace_id: Optional trace ID to filter by
        output_format: Output format (text, json)
        
    Returns:
        Journey data dict (for JSON output) or None
    """
    client, db = get_mongodb_connection()
    
    try:
        # Validate trace_id if provided
        if trace_id and not validate_trace_id(db, trace_id):
            print_error(f"Trace ID '{trace_id}' not found")
            return None
        
        # Find entity
        if entity_id:
            entity = find_entity_by_id(db, entity_id, trace_id)
        elif entity_name:
            entity = find_entity_by_name(db, entity_name, trace_id)
        else:
            print_error("Must provide either --entity or --entity-id")
            return None
        
        if not entity:
            print_error(f"Entity not found: {entity_name or entity_id}")
            return None
        
        # Stage 1: Extraction
        raw_mentions = get_entity_raw_mentions(db, entity.get("name", ""), trace_id)
        
        # Stage 2: Resolution
        merge_logs = find_entity_all_logs(db, entity["entity_id"], trace_id)
        merge_count = sum(1 for log in merge_logs if log.get("operation") == "entity_merge")
        
        # Stage 3: Graph Construction
        relationships = get_entity_relationships(db, entity["entity_id"], trace_id)
        node_degree = calculate_node_degree(relationships, entity["entity_id"])
        rel_sources = group_relationships_by_source(relationships)
        
        # Stage 4: Community Detection
        community = None
        for comm in db.communities.find({"entity_ids": entity["entity_id"], "trace_id": trace_id} if trace_id else {"entity_ids": entity["entity_id"]}):
            community = comm
            break
        
        # Build journey
        journey = {
            "trace_id": trace_id or entity.get("trace_id", "unknown"),
            "entity": {
                "entity_id": entity["entity_id"],
                "name": entity.get("name", "unknown"),
                "type": entity.get("type", "unknown"),
                "confidence": entity.get("confidence", 0)
            },
            "stage_1_extraction": {
                "raw_mentions": len(raw_mentions),
                "chunks": [m.get("chunk_id") for m in raw_mentions],
                "confidences": [m.get("confidence", 0) for m in raw_mentions]
            },
            "stage_2_resolution": {
                "merge_count": merge_count,
                "final_entity_id": entity["entity_id"],
                "confidence_preserved": entity.get("confidence", 0)
            },
            "stage_3_construction": {
                "relationship_count": len(relationships),
                "node_degree": node_degree,
                "relationship_sources": rel_sources
            },
            "stage_4_detection": {
                "community_id": community.get("community_id") if community else None,
                "community_size": len(community.get("entity_ids", [])) if community else 0,
                "role": "hub" if node_degree > 5 else "peripheral"
            }
        }
        
        # Output
        if output_format == "json":
            print(format_json_output(journey))
        else:
            print_text_journey(journey)
        
        return journey
        
    finally:
        client.close()


def print_text_journey(journey: Dict[str, Any]):
    """Print journey in text format."""
    print(format_section_header(f"ENTITY JOURNEY: {journey['entity']['name']}"))
    
    print(f"Trace ID: {journey['trace_id']}")
    print(f"Entity ID: {journey['entity']['entity_id']}")
    print(f"Type: {journey['entity']['type']}")
    print(f"Final Confidence: {journey['entity']['confidence']:.3f}")
    
    # Stage 1
    print(format_subsection_header("Stage 1: EXTRACTION"))
    extraction = journey["stage_1_extraction"]
    print(f"✅ Extracted from {extraction['raw_mentions']} chunks")
    if extraction["chunks"]:
        print(f"Chunks: {', '.join(extraction['chunks'][:5])}")
        if len(extraction["chunks"]) > 5:
            print(f"  ... and {len(extraction['chunks']) - 5} more")
    if extraction["confidences"]:
        avg_conf = sum(extraction["confidences"]) / len(extraction["confidences"])
        print(f"Average Confidence: {avg_conf:.3f}")
    
    # Stage 2
    print(format_subsection_header("Stage 2: RESOLUTION"))
    resolution = journey["stage_2_resolution"]
    if resolution["merge_count"] > 0:
        print(f"✅ Merged {resolution['merge_count']} mentions → 1 entity")
    else:
        print("✅ No merges (unique entity)")
    print(f"Final Entity ID: {resolution['final_entity_id']}")
    print(f"Confidence Preserved: {resolution['confidence_preserved']:.3f}")
    
    # Stage 3
    print(format_subsection_header("Stage 3: GRAPH CONSTRUCTION"))
    construction = journey["stage_3_construction"]
    print(f"✅ Connected to {construction['relationship_count']} entities")
    print(f"Node Degree: {construction['node_degree']}")
    if construction["relationship_sources"]:
        print("Relationship Sources:")
        for source, count in construction["relationship_sources"].items():
            print(f"  • {source}: {count}")
    
    # Stage 4
    print(format_subsection_header("Stage 4: COMMUNITY DETECTION"))
    detection = journey["stage_4_detection"]
    if detection["community_id"]:
        print(f"✅ Assigned to community {detection['community_id']}")
        print(f"Community Size: {detection['community_size']} entities")
        print(f"Role: {detection['role']}")
    else:
        print("❌ Not assigned to any community")


def main():
    parser = argparse.ArgumentParser(
        description="Trace complete entity journey through pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Trace by entity name
  python trace_entity_journey.py --entity "Barack Obama"
  
  # Trace by entity ID
  python trace_entity_journey.py --entity-id abc123
  
  # Filter by trace ID
  python trace_entity_journey.py --entity "Apple Inc" --trace-id xyz
  
  # JSON output
  python trace_entity_journey.py --entity "Google" --format json
"""
    )
    
    parser.add_argument("--entity", help="Entity name")
    parser.add_argument("--entity-id", help="Entity ID")
    parser.add_argument("--trace-id", help="Filter by trace ID")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    result = trace_entity_journey(
        entity_name=args.entity,
        entity_id=args.entity_id,
        trace_id=args.trace_id,
        output_format=args.format
    )
    
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()


