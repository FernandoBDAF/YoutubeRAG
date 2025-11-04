"""
Tests for Metrics Library Integration.

Tests integration with logging and error_handling libraries.
Run with: python -m tests.core.libraries.metrics.test_integration
"""

import logging
from core.libraries.logging import log_exception
from core.libraries.metrics import MetricRegistry, export_prometheus_text


def test_log_exception_tracks_metrics():
    """Test that log_exception auto-tracks error metrics."""
    logging.basicConfig(level=logging.ERROR, format="")
    logger = logging.getLogger("test.integration")

    # Clear metrics
    registry = MetricRegistry.get_instance()
    errors = registry.get("errors_total")
    if errors:
        errors.reset()

    # Log some errors
    try:
        raise ValueError("Test error 1")
    except Exception as e:
        log_exception(logger, "Error 1", e, include_traceback=False)

    try:
        raise KeyError("Test error 2")
    except Exception as e:
        log_exception(logger, "Error 2", e, include_traceback=False)

    try:
        raise ValueError("Test error 3")
    except Exception as e:
        log_exception(logger, "Error 3", e, include_traceback=False)

    # Check metrics
    errors = registry.get("errors_total")
    value_error_count = errors.get(
        labels={"error_type": "ValueError", "component": "integration"}
    )
    key_error_count = errors.get(
        labels={"error_type": "KeyError", "component": "integration"}
    )

    assert value_error_count == 2.0, f"Expected 2 ValueErrors, got {value_error_count}"
    assert key_error_count == 1.0, f"Expected 1 KeyError, got {key_error_count}"

    print("✓ log_exception() auto-tracks error metrics")


def test_prometheus_export_includes_errors():
    """Test that Prometheus export includes error metrics."""
    metrics_text = export_prometheus_text()

    assert "errors_total" in metrics_text
    assert 'error_type="ValueError"' in metrics_text
    assert 'error_type="KeyError"' in metrics_text

    print("✓ Prometheus export includes error metrics")


def run_all_tests():
    """Run all integration tests."""
    print("Testing Metrics Library Integration")
    print("=" * 60)
    print()

    test_log_exception_tracks_metrics()
    test_prometheus_export_includes_errors()

    print()
    print("=" * 60)
    print("🎉 All integration tests passed!")
    print("🎉 Libraries work together seamlessly!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
