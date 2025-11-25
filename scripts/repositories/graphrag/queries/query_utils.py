#!/usr/bin/env python3
"""
Shared utilities for GraphRAG query scripts.

Provides common functions for MongoDB connection, output formatting,
and filtering used across all query scripts.

Enhanced with:
- Color-coded output for terminal display
- Pagination support for large result sets
- Caching mechanism for repeated queries
- Progress indicators for long-running operations
"""

import json
import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
from functools import lru_cache
import time

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

# Load environment variables
load_dotenv()

# ANSI Color codes for terminal output
class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    
    @staticmethod
    def disable_if_piped():
        """Disable colors if output is piped"""
        if not sys.stdout.isatty():
            for attr in dir(Colors):
                if not attr.startswith('_') and attr != 'disable_if_piped':
                    setattr(Colors, attr, '')

# Disable colors if output is piped
Colors.disable_if_piped()


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


def paginate_results(
    data: List[Dict[str, Any]],
    page: int = 1,
    page_size: int = 20
) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Paginate results and return pagination metadata.
    
    Args:
        data: List of items to paginate
        page: Page number (1-indexed)
        page_size: Items per page
        
    Returns:
        Tuple of (paginated_data, pagination_metadata)
        
    Learning: Pagination improves UX for large result sets by breaking
    output into manageable chunks. Metadata allows navigation controls.
    """
    total_items = len(data)
    total_pages = (total_items + page_size - 1) // page_size
    
    # Validate page number
    if page < 1:
        page = 1
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    # Calculate slice indices
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    pagination_metadata = {
        "current_page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }
    
    return data[start_idx:end_idx], pagination_metadata


def format_color_value(value: Any, value_type: str = "text") -> str:
    """
    Format a value with color coding based on its type.
    
    Args:
        value: Value to format
        value_type: Type indicator ("success", "warning", "error", "info", "text")
        
    Returns:
        Color-coded string
        
    Learning: Color coding improves readability by providing visual cues:
    - Green for success/positive values
    - Yellow for warnings/caution values
    - Red for errors/negative values
    - Blue for information/neutral values
    """
    if value is None:
        return f"{Colors.WHITE}-{Colors.RESET}"
    
    value_str = str(value)
    
    if value_type == "success":
        return f"{Colors.GREEN}{value_str}{Colors.RESET}"
    elif value_type == "warning":
        return f"{Colors.YELLOW}{value_str}{Colors.RESET}"
    elif value_type == "error":
        return f"{Colors.RED}{value_str}{Colors.RESET}"
    elif value_type == "info":
        return f"{Colors.BLUE}{value_str}{Colors.RESET}"
    else:
        return value_str


def print_progress(current: int, total: int, label: str = "Progress") -> None:
    """
    Print a simple progress indicator.
    
    Args:
        current: Current item count
        total: Total item count
        label: Progress label
        
    Learning: Progress indicators provide user feedback during long operations,
    improving perceived responsiveness and preventing user frustration with
    seemingly unresponsive applications.
    """
    if total == 0:
        return
    
    percentage = (current / total) * 100
    bar_length = 40
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    print(f"\r{label}: |{bar}| {percentage:.1f}% ({current}/{total})", end='')
    
    if current == total:
        print()  # Newline when complete


class QueryCache:
    """
    Simple caching mechanism for MongoDB queries.
    
    Learning: Query caching reduces redundant database calls and improves
    performance for repeated queries. This is especially useful for frequently
    accessed data like entity lookups or aggregation results.
    """
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum number of cached items
            ttl_seconds: Time-to-live for cached items in seconds
        """
        self.cache: Dict[str, tuple[Any, float]] = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if exists and not expired."""
        if key not in self.cache:
            return None
        
        value, timestamp = self.cache[key]
        if time.time() - timestamp > self.ttl_seconds:
            del self.cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set cache value."""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """Clear all cache."""
        self.cache.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "items": len(self.cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds,
        }


# Global query cache instance
query_cache = QueryCache()


