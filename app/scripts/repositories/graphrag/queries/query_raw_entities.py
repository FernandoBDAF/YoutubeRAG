#!/usr/bin/env python3
"""
Query Raw Entities (Before Resolution)

Query entities as extracted from chunks, before entity resolution merges them.
Uses the entities_raw collection from IntermediateDataService (Achievement 0.2).
"""

import argparse
import sys
from typing import Optional

from query_utils import (
    get_mongodb_connection,
    output_results,
    build_trace_id_filter,
    add_common_arguments,
    print_summary
)


def query_raw_entities(
    trace_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    chunk_id: Optional[str] = None,
    min_confidence: float = 0.0,
    limit: int = 20,
    format: str = "table",
    output: Optional[str] = None,
) -> None:
    """
    Query raw entities before resolution.
    
    Args:
        trace_id: Filter by trace ID
        entity_type: Filter by entity type
        chunk_id: Filter by chunk ID
        min_confidence: Minimum confidence score
        limit: Maximum number of results
        format: Output format
        output: Output file path
    """
    client, db = get_mongodb_connection()
    
    try:
        # Build query
        query = build_trace_id_filter(trace_id)
        
        if entity_type:
            query["entity_type"] = entity_type
        if chunk_id:
            query["chunk_id"] = chunk_id
        if min_confidence > 0:
            query["confidence"] = {"$gte": min_confidence}
        
        # Query entities_raw collection
        entities = list(
            db["entities_raw"]
            .find(query)
            .sort("confidence", -1)
            .limit(limit)
        )
        
        if not entities:
            print("No raw entities found matching criteria")
            return
        
        # Print summary
        total_count = db["entities_raw"].count_documents(query)
        unique_types = db["entities_raw"].distinct("entity_type", query)
        
        print_summary("Raw Entities Query", {
            "Total Matching": total_count,
            "Showing": len(entities),
            "Unique Types": len(unique_types),
            "Trace ID": trace_id or "All",
        })
        
        # Format output
        table_columns = [
            ("entity_id", "Entity ID", 36),
            ("name", "Name", 30),
            ("entity_type", "Type", 15),
            ("confidence", "Confidence", 10),
            ("chunk_id", "Chunk ID", 36),
        ]
        
        csv_columns = [
            "entity_id", "name", "entity_type", "confidence",
            "chunk_id", "source_text", "extraction_method"
        ]
        
        metadata = {
            "query": "raw_entities",
            "trace_id": trace_id,
            "entity_type": entity_type,
            "total_count": total_count
        }
        
        output_results(
            entities,
            format,
            output,
            table_columns=table_columns,
            csv_columns=csv_columns,
            title="Raw Entities (Before Resolution)",
            metadata=metadata
        )
        
    finally:
        client.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Query raw entities before resolution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query raw entities from a specific pipeline run
  python query_raw_entities.py --trace-id abc123

  # Query PERSON entities with high confidence
  python query_raw_entities.py --trace-id abc123 --entity-type PERSON --min-confidence 0.8

  # Query entities from a specific chunk
  python query_raw_entities.py --trace-id abc123 --chunk-id chunk_001

  # Export to JSON
  python query_raw_entities.py --trace-id abc123 --format json --output raw_entities.json

Use Case:
  "What entities were extracted from chunk X before resolution merged them?"
        """,
    )
    
    add_common_arguments(parser)
    parser.add_argument("--entity-type", help="Filter by entity type (e.g., PERSON, ORGANIZATION)")
    parser.add_argument("--chunk-id", help="Filter by chunk ID")
    parser.add_argument("--min-confidence", type=float, default=0.0, help="Minimum confidence score")
    
    args = parser.parse_args()
    
    query_raw_entities(
        trace_id=args.trace_id,
        entity_type=args.entity_type,
        chunk_id=args.chunk_id,
        min_confidence=args.min_confidence,
        limit=args.limit,
        format=args.format,
        output=args.output,
    )


if __name__ == "__main__":
    main()


