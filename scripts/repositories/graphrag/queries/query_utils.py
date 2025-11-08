#!/usr/bin/env python3
"""
Shared utilities for GraphRAG query scripts.

Provides common functions for MongoDB connection, output formatting,
and filtering used across all query scripts.
"""

import json
import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

# Load environment variables
load_dotenv()


def get_mongodb_connection() -> tuple[MongoClient, Database]:
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


def format_table(data: List[Dict[str, Any]], columns: List[tuple[str, str, int]], title: str = "Results") -> str:
    """
    Format data as a table.
    
    Args:
        data: List of dictionaries to format
        columns: List of (field_name, display_name, width) tuples
        title: Table title
        
    Returns:
        Formatted table string
    """
    if not data:
        return f"\n📊 {title} (0 results)\n"
    
    # Calculate total width
    total_width = sum(width for _, _, width in columns) + (len(columns) - 1) * 2
    
    # Build header
    lines = [
        f"\n📊 {title} ({len(data)} results)",
        "=" * total_width,
    ]
    
    # Column headers
    header_parts = []
    for _, display_name, width in columns:
        header_parts.append(f"{display_name:<{width}}")
    lines.append("  ".join(header_parts))
    lines.append("-" * total_width)
    
    # Data rows
    for item in data:
        row_parts = []
        for field_name, _, width in columns:
            value = item.get(field_name, "")
            # Handle different types
            if isinstance(value, float):
                value_str = f"{value:.4f}"
            elif isinstance(value, datetime):
                value_str = value.strftime("%Y-%m-%d %H:%M")
            else:
                value_str = str(value)
            # Truncate if too long
            if len(value_str) > width:
                value_str = value_str[:width-3] + "..."
            row_parts.append(f"{value_str:<{width}}")
        lines.append("  ".join(row_parts))
    
    lines.append("=" * total_width)
    return "\n".join(lines)


def format_json(data: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
    """
    Format data as JSON.
    
    Args:
        data: List of dictionaries to format
        metadata: Optional metadata to include
        
    Returns:
        JSON string
    """
    output = {
        "metadata": metadata or {},
        "count": len(data),
        "results": data
    }
    return json.dumps(output, indent=2, default=str)


def format_csv(data: List[Dict[str, Any]], columns: List[str]) -> str:
    """
    Format data as CSV.
    
    Args:
        data: List of dictionaries to format
        columns: List of column names to include
        
    Returns:
        CSV string
    """
    import csv
    from io import StringIO
    
    output_buffer = StringIO()
    
    if data:
        writer = csv.DictWriter(output_buffer, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        for item in data:
            # Convert all values to strings for CSV
            row = {k: str(v) if v is not None else "" for k, v in item.items() if k in columns}
            writer.writerow(row)
    
    return output_buffer.getvalue()


def output_results(
    data: List[Dict[str, Any]],
    format: str,
    output_file: Optional[str] = None,
    table_columns: Optional[List[tuple[str, str, int]]] = None,
    csv_columns: Optional[List[str]] = None,
    title: str = "Results",
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Output results in specified format.
    
    Args:
        data: List of dictionaries to output
        format: Output format ("table", "json", "csv")
        output_file: Optional file path to write to
        table_columns: Column specification for table format
        csv_columns: Column names for CSV format
        title: Title for table format
        metadata: Metadata for JSON format
    """
    # Format data
    if format == "json":
        output_data = format_json(data, metadata)
    elif format == "csv":
        if not csv_columns:
            # Use all keys from first item
            csv_columns = list(data[0].keys()) if data else []
        output_data = format_csv(data, csv_columns)
    else:  # table
        if not table_columns:
            # Auto-generate columns from first item
            if data:
                table_columns = [(k, k.replace("_", " ").title(), 20) for k in list(data[0].keys())[:5]]
            else:
                table_columns = []
        output_data = format_table(data, table_columns, title)
    
    # Output
    if output_file:
        with open(output_file, "w") as f:
            f.write(output_data)
        print(f"✅ Results saved to {output_file}")
    else:
        print(output_data)


def build_trace_id_filter(trace_id: Optional[str]) -> Dict[str, Any]:
    """
    Build MongoDB filter for trace_id.
    
    Args:
        trace_id: Optional trace ID to filter by
        
    Returns:
        MongoDB filter dict
    """
    if trace_id:
        return {"trace_id": trace_id}
    return {}


def build_date_range_filter(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    date_field: str = "timestamp"
) -> Dict[str, Any]:
    """
    Build MongoDB filter for date range.
    
    Args:
        start_date: Optional start date (ISO format)
        end_date: Optional end date (ISO format)
        date_field: Field name for date filtering
        
    Returns:
        MongoDB filter dict
    """
    filter_dict = {}
    
    if start_date or end_date:
        date_filter = {}
        if start_date:
            date_filter["$gte"] = datetime.fromisoformat(start_date)
        if end_date:
            date_filter["$lte"] = datetime.fromisoformat(end_date)
        filter_dict[date_field] = date_filter
    
    return filter_dict


def add_common_arguments(parser):
    """
    Add common arguments to argument parser.
    
    Args:
        parser: argparse.ArgumentParser instance
    """
    parser.add_argument(
        "--trace-id",
        help="Filter by trace ID (pipeline run)"
    )
    parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)"
    )
    parser.add_argument(
        "--output",
        help="Output file path (optional)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of results (default: 20)"
    )


def print_summary(title: str, stats: Dict[str, Any]) -> None:
    """
    Print a summary box with statistics.
    
    Args:
        title: Summary title
        stats: Dictionary of statistics to display
    """
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print(f"{'=' * 60}\n")


