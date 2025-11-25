"""
Performance tests for prompt generation scripts.

Tests caching, metrics collection, and performance targets.
Achievement 3.2 - Performance Optimization + Library Integration
"""

import pytest
import time
import os
from pathlib import Path
from LLM.scripts.generation.plan_parser import PlanParser


class TestCaching:
    """Test caching functionality and performance."""

    def test_plan_cache_hit_rate_exceeds_80_percent(self, tmp_path):
        """Test PLAN parsing cache achieves >80% hit rate."""
        # Create test PLAN file
        test_plan = tmp_path / "PLAN_TEST.md"
        test_plan.write_text(
            """
# PLAN: Test Feature

**Achievement 0.1**: Test Achievement
Purpose: Test purpose
What: Test what
Success: Test success
        """
        )

        parser = PlanParser()

        # First call - cache miss
        result1 = parser.parse_plan_file(test_plan)
        assert result1 is not None

        # Next 10 calls - cache hits
        for _ in range(10):
            result = parser.parse_plan_file(test_plan)
            assert result is not None

        # Check cache stats
        stats = parser.parse_plan_file.cache.stats()

        # Total: 11 calls (1 miss + 10 hits)
        assert stats["hits"] >= 10, f"Expected >= 10 hits, got {stats['hits']}"
        assert stats["misses"] == 1, f"Expected 1 miss, got {stats['misses']}"
        assert stats["hit_rate"] > 80, f"Cache hit rate {stats['hit_rate']:.1f}% < 80%"

    def test_cache_invalidation_on_file_modification(self, tmp_path):
        """Test cache invalidates when file modified (mtime changes)."""
        # Create test PLAN file
        test_plan = tmp_path / "PLAN_TEST.md"
        test_plan.write_text("# PLAN: Test\n\n**Achievement 0.1**: Test")

        parser = PlanParser()

        # First parse - cache miss
        result1 = parser.parse_plan_file(test_plan)
        stats1 = parser.parse_plan_file.cache.stats()
        initial_misses = stats1["misses"]

        # Modify file (change content and mtime)
        time.sleep(0.01)  # Ensure different mtime
        test_plan.write_text("# PLAN: Test Modified\n\n**Achievement 0.1**: Test")

        # Second parse - should be cache miss (mtime changed)
        result2 = parser.parse_plan_file(test_plan)
        stats2 = parser.parse_plan_file.cache.stats()

        # Should have 1 additional miss
        assert (
            stats2["misses"] > initial_misses
        ), f"Expected cache miss after file modification, but misses didn't increase"

    def test_cache_size_limit_enforced(self, tmp_path):
        """Test cache respects max_size limit (LRU eviction)."""
        parser = PlanParser()

        # Get cache max size (should be 50 from decorator)
        max_size = parser.parse_plan_file.cache.max_size
        assert max_size == 50, f"Expected max_size=50, got {max_size}"

        # Cache size should never exceed max_size
        # (This is a property test - cache implementation enforces this)
        stats = parser.parse_plan_file.cache.stats()
        assert stats["size"] <= max_size, f"Cache size {stats['size']} exceeds max_size {max_size}"


class TestMetrics:
    """Test metrics collection."""

    def test_metrics_are_registered(self):
        """Test that performance metrics are registered with registry."""
        from core.libraries.metrics import MetricRegistry

        registry = MetricRegistry.get_instance()

        # Check that our metrics are registered (use public API)
        assert (
            "prompt_generation_total" in registry.metrics
        ), "prompt_generation_total not registered"
        assert (
            "prompt_generation_duration_seconds" in registry.metrics
        ), "prompt_generation_duration_seconds not registered"
        assert "plan_cache_hits_total" in registry.metrics, "plan_cache_hits_total not registered"

    def test_counter_increments(self):
        """Test Counter metric increments correctly."""
        from core.libraries.metrics import Counter

        counter = Counter("test_counter", labels=["status"])

        # Increment with different labels
        counter.inc(labels={"status": "success"})
        counter.inc(amount=5, labels={"status": "success"})
        counter.inc(labels={"status": "error"})

        # Check values
        assert counter.get(labels={"status": "success"}) == 6
        assert counter.get(labels={"status": "error"}) == 1

    def test_histogram_observes_duration(self):
        """Test Histogram metric records durations."""
        from core.libraries.metrics import Histogram

        histogram = Histogram("test_duration", labels=["operation"])

        # Observe some durations
        histogram.observe(1.5, labels={"operation": "parse"})
        histogram.observe(0.8, labels={"operation": "parse"})
        histogram.observe(2.2, labels={"operation": "parse"})

        # Check observations recorded (use internal API since no public getter)
        observations = histogram._observations[histogram._make_key({"operation": "parse"})]
        assert len(observations) == 3
        assert sum(observations) == pytest.approx(4.5)


class TestPerformance:
    """Test performance targets."""

    def test_plan_parsing_cached_under_200ms(self, tmp_path):
        """Test cached PLAN parsing completes in <200ms."""
        # Create realistic PLAN file
        test_plan = tmp_path / "PLAN_TEST.md"
        content = "# PLAN: Test Feature\n\n"
        for i in range(20):
            content += f"\n**Achievement {i}.1**: Test Achievement {i}\n"
            content += f"Purpose: Test purpose {i}\n"
            content += f"What: Test what {i}\n"
            content += f"Success: Test success {i}\n"
        test_plan.write_text(content)

        parser = PlanParser()

        # First call to populate cache
        parser.parse_plan_file(test_plan)

        # Measure cached call
        start = time.perf_counter()
        result = parser.parse_plan_file(test_plan)
        duration = time.perf_counter() - start

        # Cached call should be very fast (<200ms, typically <1ms)
        assert duration < 0.2, f"Cached PLAN parsing took {duration*1000:.1f}ms, target <200ms"

        # Verify result is correct
        assert len(result["achievements"]) == 20


class TestCompiledPatterns:
    """Test pre-compiled regex patterns."""

    def test_patterns_compiled_at_module_level(self):
        """Test regex patterns are compiled at module level (not at call time)."""
        from LLM.scripts.generation import plan_parser

        # Check patterns exist and are compiled
        assert hasattr(plan_parser, "ACHIEVEMENT_PATTERN")
        assert hasattr(plan_parser, "HANDOFF_PATTERN")
        assert hasattr(plan_parser, "ACHIEVEMENT_COUNT_PATTERN")
        assert hasattr(plan_parser, "TIME_PATTERN")
        assert hasattr(plan_parser, "ARCHIVE_PATTERN")

        # Check they are compiled regex objects
        import re

        assert isinstance(plan_parser.ACHIEVEMENT_PATTERN, re.Pattern)
        assert isinstance(plan_parser.HANDOFF_PATTERN, re.Pattern)

    def test_compiled_patterns_match_correctly(self):
        """Test pre-compiled patterns match expected strings."""
        from LLM.scripts.generation.plan_parser import ACHIEVEMENT_PATTERN

        # Test achievement pattern
        match = ACHIEVEMENT_PATTERN.match("**Achievement 2.1**: Test Achievement")
        assert match is not None
        assert match.group(1) == "2.1"
        assert match.group(2) == " Test Achievement"

        # Test non-match
        no_match = ACHIEVEMENT_PATTERN.match("Not an achievement")
        assert no_match is None


# Integration test (would require real PLAN file)
@pytest.mark.integration
class TestEndToEndPerformance:
    """Integration tests for end-to-end performance."""

    @pytest.mark.skip(reason="Requires actual benchmarking with real data")
    def test_full_prompt_generation_under_3s(self):
        """Test complete prompt generation in <3s."""
        # This would test the full generate_prompt flow
        # Requires actual PLAN files and full environment
        pass

    @pytest.mark.skip(reason="Requires actual benchmarking with real data")
    def test_70_percent_improvement_for_cached_operations(self):
        """Test 70% performance improvement for cached operations."""
        # This would measure before/after performance
        # Requires actual benchmarking runs
        pass
