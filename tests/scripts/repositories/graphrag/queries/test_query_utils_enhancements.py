#!/usr/bin/env python3
"""
Unit tests for query_utils enhancements.

Tests the new features added in Achievement 7.1:
- Color formatting functions
- Pagination support
- Query caching mechanism
- Progress indicators
"""

import pytest
import sys
import os
from typing import Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../../")))

# Only import the functions we can test without DB connection
from scripts.repositories.graphrag.queries.query_utils import (
    paginate_results,
    format_color_value,
    QueryCache,
    Colors,
)


class TestPagination:
    """Test pagination functionality."""

    def test_paginate_results_basic(self):
        """Test basic pagination."""
        data = [{"id": i, "name": f"item_{i}"} for i in range(100)]
        
        page1, meta1 = paginate_results(data, page=1, page_size=20)
        
        assert len(page1) == 20
        assert meta1["current_page"] == 1
        assert meta1["total_items"] == 100
        assert meta1["total_pages"] == 5
        assert meta1["has_next"] is True
        assert meta1["has_previous"] is False

    def test_paginate_results_middle_page(self):
        """Test pagination in middle of dataset."""
        data = [{"id": i} for i in range(100)]
        
        page3, meta3 = paginate_results(data, page=3, page_size=20)
        
        assert len(page3) == 20
        assert meta3["current_page"] == 3
        assert meta3["has_next"] is True
        assert meta3["has_previous"] is True

    def test_paginate_results_last_page(self):
        """Test pagination on last page."""
        data = [{"id": i} for i in range(100)]
        
        page5, meta5 = paginate_results(data, page=5, page_size=20)
        
        assert len(page5) == 20
        assert meta5["current_page"] == 5
        assert meta5["has_next"] is False
        assert meta5["has_previous"] is True

    def test_paginate_results_partial_last_page(self):
        """Test pagination with partial last page."""
        data = [{"id": i} for i in range(45)]
        
        page3, meta3 = paginate_results(data, page=3, page_size=20)
        
        assert len(page3) == 5  # Only 5 items on last page
        assert meta3["total_pages"] == 3
        assert meta3["has_next"] is False

    def test_paginate_results_invalid_page(self):
        """Test pagination with invalid page number."""
        data = [{"id": i} for i in range(100)]
        
        # Page 0 should become page 1
        page_invalid, meta_invalid = paginate_results(data, page=0, page_size=20)
        assert meta_invalid["current_page"] == 1
        
        # Page > total_pages should become last page
        page_over, meta_over = paginate_results(data, page=100, page_size=20)
        assert meta_over["current_page"] == 5

    def test_paginate_results_empty_data(self):
        """Test pagination with empty dataset."""
        data = []
        
        page, meta = paginate_results(data, page=1, page_size=20)
        
        assert len(page) == 0
        assert meta["total_items"] == 0
        assert meta["total_pages"] == 0

    def test_paginate_results_single_page(self):
        """Test pagination with data fitting single page."""
        data = [{"id": i} for i in range(10)]
        
        page, meta = paginate_results(data, page=1, page_size=20)
        
        assert len(page) == 10
        assert meta["total_pages"] == 1
        assert meta["has_next"] is False


class TestColorFormatting:
    """Test color formatting functionality."""

    def test_format_color_value_none(self):
        """Test formatting None values."""
        result = format_color_value(None, "text")
        assert "-" in result  # Should contain dash

    def test_format_color_value_success(self):
        """Test formatting with success color."""
        result = format_color_value(100, "success")
        assert "100" in result
        assert Colors.GREEN in result

    def test_format_color_value_warning(self):
        """Test formatting with warning color."""
        result = format_color_value("warning", "warning")
        assert "warning" in result
        assert Colors.YELLOW in result

    def test_format_color_value_error(self):
        """Test formatting with error color."""
        result = format_color_value("error", "error")
        assert "error" in result
        assert Colors.RED in result

    def test_format_color_value_info(self):
        """Test formatting with info color."""
        result = format_color_value("info", "info")
        assert "info" in result
        assert Colors.BLUE in result

    def test_format_color_value_text(self):
        """Test formatting with text (no color)."""
        result = format_color_value("plain text", "text")
        assert "plain text" in result

    def test_format_color_value_numeric(self):
        """Test formatting numeric values."""
        result = format_color_value(42.5, "success")
        assert "42.5" in result


class TestQueryCache:
    """Test query caching mechanism."""

    def test_cache_basic_set_get(self):
        """Test basic cache set and get."""
        cache = QueryCache()
        cache.set("key1", {"data": "value1"})
        
        result = cache.get("key1")
        assert result == {"data": "value1"}

    def test_cache_miss(self):
        """Test cache miss."""
        cache = QueryCache()
        result = cache.get("nonexistent")
        assert result is None

    def test_cache_max_size(self):
        """Test cache max size eviction."""
        cache = QueryCache(max_size=3)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        cache.set("key4", "value4")  # Should evict oldest
        
        # key1 should be evicted
        assert cache.get("key1") is None
        # Others should exist
        assert cache.get("key2") is not None
        assert cache.get("key3") is not None
        assert cache.get("key4") is not None

    def test_cache_stats(self):
        """Test cache statistics."""
        cache = QueryCache(max_size=10, ttl_seconds=300)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        stats = cache.stats()
        assert stats["items"] == 2
        assert stats["max_size"] == 10
        assert stats["ttl_seconds"] == 300

    def test_cache_clear(self):
        """Test cache clearing."""
        cache = QueryCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        assert len(cache.cache) == 2
        cache.clear()
        assert len(cache.cache) == 0

    def test_cache_overwrite(self):
        """Test cache overwrite."""
        cache = QueryCache()
        cache.set("key", "value1")
        cache.set("key", "value2")
        
        result = cache.get("key")
        assert result == "value2"

    def test_cache_multiple_keys(self):
        """Test cache with multiple keys."""
        cache = QueryCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"


class TestColors:
    """Test color constants."""

    def test_colors_defined(self):
        """Test that all color constants are defined."""
        assert hasattr(Colors, "RESET")
        assert hasattr(Colors, "BOLD")
        assert hasattr(Colors, "RED")
        assert hasattr(Colors, "GREEN")
        assert hasattr(Colors, "YELLOW")
        assert hasattr(Colors, "BLUE")

    def test_colors_are_strings(self):
        """Test that colors are either strings or empty."""
        # After disable_if_piped, colors are either escape codes or empty strings
        assert isinstance(Colors.RESET, str)
        assert isinstance(Colors.RED, str)

    def test_color_reset(self):
        """Test that RESET code exists or is empty (when piped)."""
        # Colors may be disabled when output is piped (e.g., during pytest)
        # This is correct behavior
        assert isinstance(Colors.RESET, str)


class TestIntegration:
    """Integration tests combining multiple features."""

    def test_color_pagination_integration(self):
        """Test using color formatting with paginated results."""
        data = [{"id": i, "count": i * 10} for i in range(50)]
        
        paginated, meta = paginate_results(data, page=1, page_size=10)
        
        # Format first item's count with color
        first_item = paginated[0]
        colored_count = format_color_value(first_item["count"], "success")
        
        assert len(paginated) == 10
        assert "0" in colored_count

    def test_cache_integration(self):
        """Test cache with various data types."""
        cache = QueryCache()
        
        # Cache different types of data
        cache.set("dict", {"key": "value"})
        cache.set("list", [1, 2, 3])
        cache.set("string", "test string")
        cache.set("number", 42)
        
        assert cache.get("dict") == {"key": "value"}
        assert cache.get("list") == [1, 2, 3]
        assert cache.get("string") == "test string"
        assert cache.get("number") == 42

    def test_full_workflow(self):
        """Test complete workflow: cache → paginate → format."""
        # Simulate a workflow
        cache = QueryCache()
        
        # Cache some results
        full_results = [
            {"id": i, "status": "success" if i % 2 == 0 else "error"}
            for i in range(100)
        ]
        cache.set("results", full_results)
        
        # Retrieve from cache
        cached_results = cache.get("results")
        
        # Paginate results
        page1, meta1 = paginate_results(cached_results, page=1, page_size=20)
        
        # Format first item's status with color
        first_status = page1[0]["status"]
        colored_status = format_color_value(
            first_status,
            "success" if first_status == "success" else "error"
        )
        
        assert len(page1) == 20
        assert meta1["total_pages"] == 5
        assert "success" in colored_status or "error" in colored_status


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

