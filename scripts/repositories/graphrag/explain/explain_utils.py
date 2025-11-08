#!/usr/bin/env python3
"""
Shared utilities for GraphRAG explanation scripts.

Provides common functions for MongoDB connection, transformation log queries,
entity lookup, and output formatting used across all explanation tools.

Achievement 1.1: Transformation Explanation Tools
"""

import json
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

# Load environment variables
load_dotenv()


def get_mongodb_connection() -> Tuple[MongoClient, Database]:
    """
    Get MongoDB client and database connection.
    
    Returns:
        Tuple of (MongoClient, Database)
        
    Raises:
        SystemExit: If MONGODB_URI not found in environment
    """
    mongo_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DB_NAME", "mongo_hack")
    
    if not mongo_uri:
        print("❌ Error: MONGODB_URI not found in environment")
        sys.exit(1)
    
    client = MongoClient(mongo_uri)
    db = client[db_name]
    
    return client, db


def find_entity_by_name(db: Database, entity_name: str, trace_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Find entity by name in entities_resolved collection.
    
    Args:
        db: MongoDB database
        entity_name: Entity name to search for
        trace_id: Optional trace ID to filter by
        
    Returns:
        Entity document or None if not found
    """
    query = {"name": {"$regex": f"^{entity_name}$", "$options": "i"}}
    if trace_id:
        query["trace_id"] = trace_id
    
    return db.entities_resolved.find_one(query)


def find_entity_by_id(db: Database, entity_id: str, trace_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Find entity by ID in entities_resolved collection.
    
    Args:
        db: MongoDB database
        entity_id: Entity ID to search for
        trace_id: Optional trace ID to filter by
        
    Returns:
        Entity document or None if not found
    """
    query = {"entity_id": entity_id}
    if trace_id:
        query["trace_id"] = trace_id
    
    return db.entities_resolved.find_one(query)


def find_merge_logs(db: Database, entity_id: str, trace_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Find entity merge transformation logs.
    
    Args:
        db: MongoDB database
        entity_id: Entity ID to search for
        trace_id: Optional trace ID to filter by
        
    Returns:
        List of merge log documents
    """
    query = {
        "operation": "entity_merge",
        "$or": [
            {"before.entity_id": entity_id},
            {"after.entity_id": entity_id}
        ]
    }
    if trace_id:
        query["trace_id"] = trace_id
    
    return list(db.transformation_logs.find(query).sort("timestamp", 1))


def find_relationship_filter_logs(
    db: Database,
    source_id: str,
    target_id: str,
    trace_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Find relationship filter transformation logs.
    
    Args:
        db: MongoDB database
        source_id: Source entity ID
        target_id: Target entity ID
        trace_id: Optional trace ID to filter by
        
    Returns:
        List of filter log documents
    """
    query = {
        "operation": "relationship_filter",
        "entity_ids": {"$all": [source_id, target_id]}
    }
    if trace_id:
        query["trace_id"] = trace_id
    
    return list(db.transformation_logs.find(query).sort("timestamp", 1))


def find_entity_all_logs(db: Database, entity_id: str, trace_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Find all transformation logs involving an entity.
    
    Args:
        db: MongoDB database
        entity_id: Entity ID to search for
        trace_id: Optional trace ID to filter by
        
    Returns:
        List of log documents sorted by timestamp
    """
    query = {
        "$or": [
            {"entity_id": entity_id},
            {"before.entity_id": entity_id},
            {"after.entity_id": entity_id},
            {"entity_ids": entity_id}
        ]
    }
    if trace_id:
        query["trace_id"] = trace_id
    
    return list(db.transformation_logs.find(query).sort("timestamp", 1))


def find_community(db: Database, community_id: str, trace_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Find community by ID.
    
    Args:
        db: MongoDB database
        community_id: Community ID to search for
        trace_id: Optional trace ID to filter by
        
    Returns:
        Community document or None if not found
    """
    query = {"community_id": community_id}
    if trace_id:
        query["trace_id"] = trace_id
    
    return db.communities.find_one(query)


def find_relationship_creation_logs(db: Database, trace_id: str) -> List[Dict[str, Any]]:
    """
    Find all relationship creation and augmentation logs for a trace.
    
    Args:
        db: MongoDB database
        trace_id: Trace ID to filter by
        
    Returns:
        List of relationship log documents sorted by timestamp
    """
    query = {
        "trace_id": trace_id,
        "operation": {"$in": ["relationship_create", "relationship_augment"]}
    }
    
    return list(db.transformation_logs.find(query).sort("timestamp", 1))


def format_section_header(title: str, width: int = 63) -> str:
    """
    Format a section header.
    
    Args:
        title: Section title
        width: Total width of header
        
    Returns:
        Formatted header string
    """
    return f"\n{'═' * width}\n   {title}\n{'═' * width}\n"


def format_subsection_header(title: str, width: int = 63) -> str:
    """
    Format a subsection header.
    
    Args:
        title: Subsection title
        width: Total width of header
        
    Returns:
        Formatted header string
    """
    return f"\n{title}\n{'-' * width}\n"


def format_key_value(key: str, value: Any, indent: int = 0) -> str:
    """
    Format a key-value pair.
    
    Args:
        key: Key name
        value: Value to display
        indent: Number of spaces to indent
        
    Returns:
        Formatted string
    """
    spaces = " " * indent
    if isinstance(value, list):
        if not value:
            return f"{spaces}{key}: []"
        items = ", ".join(str(v) for v in value[:5])
        if len(value) > 5:
            items += f", ... ({len(value)} total)"
        return f"{spaces}{key}: [{items}]"
    elif isinstance(value, dict):
        return f"{spaces}{key}: {json.dumps(value, default=str)}"
    else:
        return f"{spaces}{key}: {value}"


def format_json_output(data: Dict[str, Any]) -> str:
    """
    Format data as JSON.
    
    Args:
        data: Data to format
        
    Returns:
        JSON string
    """
    return json.dumps(data, indent=2, default=str)


def format_text_output(lines: List[str]) -> str:
    """
    Format lines as plain text.
    
    Args:
        lines: Lines to format
        
    Returns:
        Plain text string
    """
    return "\n".join(lines)


def validate_trace_id(db: Database, trace_id: str) -> bool:
    """
    Validate that a trace ID exists in the database.
    
    Args:
        db: MongoDB database
        trace_id: Trace ID to validate
        
    Returns:
        True if trace ID exists, False otherwise
    """
    # Check if any transformation logs exist for this trace_id
    count = db.transformation_logs.count_documents({"trace_id": trace_id}, limit=1)
    return count > 0


def get_entity_raw_mentions(db: Database, entity_name: str, trace_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get raw entity mentions before resolution.
    
    Args:
        db: MongoDB database
        entity_name: Entity name to search for
        trace_id: Optional trace ID to filter by
        
    Returns:
        List of raw entity documents
    """
    query = {"name": {"$regex": f"^{entity_name}$", "$options": "i"}}
    if trace_id:
        query["trace_id"] = trace_id
    
    return list(db.entities_raw.find(query))


def get_entity_relationships(db: Database, entity_id: str, trace_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get all relationships involving an entity.
    
    Args:
        db: MongoDB database
        entity_id: Entity ID
        trace_id: Optional trace ID to filter by
        
    Returns:
        List of relationship documents
    """
    query = {
        "$or": [
            {"source_id": entity_id},
            {"target_id": entity_id}
        ]
    }
    if trace_id:
        query["trace_id"] = trace_id
    
    return list(db.relations_final.find(query))


def calculate_node_degree(relationships: List[Dict[str, Any]], entity_id: str) -> int:
    """
    Calculate node degree (number of connections).
    
    Args:
        relationships: List of relationship documents
        entity_id: Entity ID
        
    Returns:
        Node degree
    """
    return len(relationships)


def group_relationships_by_source(relationships: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Group relationships by source (llm, co_occurrence, semantic_similarity).
    
    Args:
        relationships: List of relationship documents
        
    Returns:
        Dictionary of source -> count
    """
    sources = {}
    for rel in relationships:
        source = rel.get("source", "llm")
        sources[source] = sources.get(source, 0) + 1
    return sources


def print_error(message: str):
    """Print error message to stderr."""
    print(f"❌ Error: {message}", file=sys.stderr)


def print_warning(message: str):
    """Print warning message to stderr."""
    print(f"⚠️  Warning: {message}", file=sys.stderr)


def print_success(message: str):
    """Print success message."""
    print(f"✅ {message}")


def print_info(message: str):
    """Print info message."""
    print(f"ℹ️  {message}")


