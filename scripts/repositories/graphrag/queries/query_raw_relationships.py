#!/usr/bin/env python3
"""
Query Raw Relationships (Before Post-Processing)

Query relationships as extracted, before post-processing adds co-occurrence,
semantic similarity, and other augmentations.
Uses the relations_raw collection from Achievement 0.2.
"""

import argparse
from typing import Optional

from query_utils import (
    get_mongodb_connection,
    output_results,
    build_trace_id_filter,
    add_common_arguments,
    print_summary
)


def query_raw_relationships(
    trace_id: Optional[str] = None,
    relationship_type: Optional[str] = None,
    source_entity: Optional[str] = None,
    target_entity: Optional[str] = None,
    limit: int = 20,
    format: str = "table",
    output: Optional[str] = None,
) -> None:
    """
    Query raw relationships before post-processing.
    
    Args:
        trace_id: Filter by trace ID
        relationship_type: Filter by relationship type
        source_entity: Filter by source entity name
        target_entity: Filter by target entity name
        limit: Maximum number of results
        format: Output format
        output: Output file path
    """
    client, db = get_mongodb_connection()
    
    try:
        # Build query
        query = build_trace_id_filter(trace_id)
        
        if relationship_type:
            query["predicate"] = relationship_type
        if source_entity:
            query["source_name"] = {"$regex": source_entity, "$options": "i"}
        if target_entity:
            query["target_name"] = {"$regex": target_entity, "$options": "i"}
        
        # Query relations_raw collection
        relationships = list(
            db["relations_raw"]
            .find(query)
            .sort("confidence", -1)
            .limit(limit)
        )
        
        if not relationships:
            print("No raw relationships found matching criteria")
            return
        
        # Print summary
        total_count = db["relations_raw"].count_documents(query)
        
        # Get predicate distribution
        pred_pipeline = [
            {"$match": query},
            {"$group": {"_id": "$predicate", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        pred_dist = list(db["relations_raw"].aggregate(pred_pipeline))
        
        print_summary("Raw Relationships Query", {
            "Total Matching": total_count,
            "Showing": len(relationships),
            "Trace ID": trace_id or "All",
            "Top Predicates": ", ".join([f"{p['_id']}: {p['count']}" for p in pred_dist[:3]])
        })
        
        # Format output
        table_columns = [
            ("source_name", "Source", 25),
            ("predicate", "Predicate", 20),
            ("target_name", "Target", 25),
            ("confidence", "Confidence", 10),
        ]
        
        csv_columns = [
            "source_entity_id", "source_name", "predicate",
            "target_entity_id", "target_name", "confidence",
            "chunk_id", "extraction_method"
        ]
        
        metadata = {
            "query": "raw_relationships",
            "trace_id": trace_id,
            "relationship_type": relationship_type,
            "total_count": total_count
        }
        
        output_results(
            relationships,
            format,
            output,
            table_columns=table_columns,
            csv_columns=csv_columns,
            title="Raw Relationships (Before Post-Processing)",
            metadata=metadata
        )
        
    finally:
        client.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Query raw relationships before post-processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query raw relationships from a pipeline run
  python query_raw_relationships.py --trace-id abc123

  # Query specific relationship type
  python query_raw_relationships.py --trace-id abc123 --relationship-type "works_for"

  # Query relationships involving a specific entity
  python query_raw_relationships.py --trace-id abc123 --source-entity "Einstein"

  # Export to JSON
  python query_raw_relationships.py --trace-id abc123 --format json --output raw_rels.json

Use Case:
  "What relationships were extracted before post-processing added augmentations?"
        """,
    )
    
    add_common_arguments(parser)
    parser.add_argument("--relationship-type", help="Filter by relationship type/predicate")
    parser.add_argument("--source-entity", help="Filter by source entity name (partial match)")
    parser.add_argument("--target-entity", help="Filter by target entity name (partial match)")
    
    args = parser.parse_args()
    
    query_raw_relationships(
        trace_id=args.trace_id,
        relationship_type=args.relationship_type,
        source_entity=args.source_entity,
        target_entity=args.target_entity,
        limit=args.limit,
        format=args.format,
        output=args.output,
    )


if __name__ == "__main__":
    main()


