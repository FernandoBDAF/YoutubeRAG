"""
Tests for Metrics Library Collectors.

Run with: python -m tests.core.libraries.metrics.test_collectors
"""

import time
from core.libraries.metrics.collectors import Counter, Gauge, Histogram, Timer


def test_counter():
    """Test Counter metric."""
    counter = Counter("test_counter", labels=["type"])

    # Test increment
    counter.inc(labels={"type": "A"})
    assert counter.get(labels={"type": "A"}) == 1.0

    # Test increment by amount
    counter.inc(amount=5, labels={"type": "A"})
    assert counter.get(labels={"type": "A"}) == 6.0

    # Test multiple labels
    counter.inc(labels={"type": "B"})
    assert counter.get(labels={"type": "B"}) == 1.0
    assert counter.get(labels={"type": "A"}) == 6.0

    # Test reset
    counter.reset(labels={"type": "A"})
    assert counter.get(labels={"type": "A"}) == 0.0

    print("✓ Counter works")


def test_gauge():
    """Test Gauge metric."""
    gauge = Gauge("test_gauge")

    # Test set
    gauge.set(100)
    assert gauge.get() == 100.0

    # Test increment
    gauge.inc(10)
    assert gauge.get() == 110.0

    # Test decrement
    gauge.dec(5)
    assert gauge.get() == 105.0

    print("✓ Gauge works")


def test_histogram():
    """Test Histogram metric."""
    hist = Histogram("test_histogram")

    # Test observations
    hist.observe(10.0)
    hist.observe(20.0)
    hist.observe(30.0)

    # Test summary
    stats = hist.summary()
    assert stats["count"] == 3
    assert stats["sum"] == 60.0
    assert stats["min"] == 10.0
    assert stats["max"] == 30.0
    assert stats["avg"] == 20.0

    # Test percentile
    p50 = hist.percentile(0.5)
    assert p50 == 20.0

    print("✓ Histogram works")


def test_timer():
    """Test Timer context manager."""
    with Timer() as timer:
        time.sleep(0.1)

    elapsed = timer.elapsed()
    assert elapsed >= 0.1
    assert elapsed < 0.2

    print("✓ Timer works")


def test_labels():
    """Test label handling."""
    counter = Counter("test_labels", labels=["stage", "status"])

    counter.inc(labels={"stage": "extraction", "status": "success"})
    counter.inc(labels={"stage": "extraction", "status": "success"})
    counter.inc(labels={"stage": "extraction", "status": "failure"})

    assert counter.get(labels={"stage": "extraction", "status": "success"}) == 2.0
    assert counter.get(labels={"stage": "extraction", "status": "failure"}) == 1.0

    print("✓ Labels work")


def run_all_tests():
    """Run all metrics tests."""
    print("Testing Metrics Library Collectors")
    print("=" * 60)
    print()

    test_counter()
    test_gauge()
    test_histogram()
    test_timer()
    test_labels()

    print()
    print("=" * 60)
    print("🎉 All metrics tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
