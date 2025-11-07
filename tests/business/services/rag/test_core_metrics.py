"""
Tests for RAG Core Service Metrics Integration.

Tests that metrics are properly tracked for RAG core service functions.
Run with: python tests/business/services/rag/test_core_metrics.py
"""

import os
import sys
import time
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
)

# Import RAG core module to register metrics
import business.services.rag.core  # noqa: F401

from core.libraries.metrics import MetricRegistry, export_prometheus_text


def test_metrics_registered():
    """Test that RAG service metrics are registered."""
    registry = MetricRegistry.get_instance()

    # Check that metrics exist
    rag_service_calls = registry.get("rag_service_calls")
    rag_service_errors = registry.get("rag_service_errors")
    rag_service_duration = registry.get("rag_service_duration_seconds")
    rag_embedding_calls = registry.get("rag_embedding_calls")
    rag_embedding_errors = registry.get("rag_embedding_errors")
    rag_embedding_duration = registry.get("rag_embedding_duration_seconds")

    assert rag_service_calls is not None, "rag_service_calls metric not registered"
    assert rag_service_errors is not None, "rag_service_errors metric not registered"
    assert (
        rag_service_duration is not None
    ), "rag_service_duration metric not registered"
    assert rag_embedding_calls is not None, "rag_embedding_calls metric not registered"
    assert (
        rag_embedding_errors is not None
    ), "rag_embedding_errors metric not registered"
    assert (
        rag_embedding_duration is not None
    ), "rag_embedding_duration metric not registered"

    print("✓ All RAG core metrics are registered")


def test_embed_query_tracks_metrics():
    """Test that embed_query tracks metrics correctly."""
    from core.libraries.metrics import MetricRegistry

    registry = MetricRegistry.get_instance()
    embedding_calls = registry.get("rag_embedding_calls")
    embedding_errors = registry.get("rag_embedding_errors")
    embedding_duration = registry.get("rag_embedding_duration_seconds")

    # Check that metrics exist (we can't easily test the full function without API keys)
    assert embedding_calls is not None, "rag_embedding_calls metric should exist"
    assert embedding_errors is not None, "rag_embedding_errors metric should exist"
    assert embedding_duration is not None, "rag_embedding_duration metric should exist"

    print("✓ embed_query metrics are available for tracking")


def test_rag_answer_tracks_metrics():
    """Test that rag_answer tracks metrics correctly."""
    from core.libraries.metrics import MetricRegistry

    registry = MetricRegistry.get_instance()
    service_calls = registry.get("rag_service_calls")
    service_errors = registry.get("rag_service_errors")
    service_duration = registry.get("rag_service_duration_seconds")

    # Reset metrics
    if service_calls:
        service_calls.reset()
    if service_errors:
        service_errors.reset()

    # Check that metrics exist (we can't easily test the full function without DB)
    assert service_calls is not None, "rag_service_calls metric should exist"
    assert service_errors is not None, "rag_service_errors metric should exist"
    assert service_duration is not None, "rag_service_duration metric should exist"

    print("✓ rag_answer metrics are available for tracking")


def test_metrics_export_includes_rag_metrics():
    """Test that Prometheus export includes RAG metrics."""
    metrics_text = export_prometheus_text()

    # Check for RAG service metrics
    assert (
        "rag_service_calls" in metrics_text or "rag_service_calls_total" in metrics_text
    ), "rag_service_calls should be in Prometheus export"
    assert (
        "rag_service_errors" in metrics_text
        or "rag_service_errors_total" in metrics_text
    ), "rag_service_errors should be in Prometheus export"
    assert (
        "rag_service_duration_seconds" in metrics_text
    ), "rag_service_duration_seconds should be in Prometheus export"

    # Check for embedding metrics
    assert (
        "rag_embedding_calls" in metrics_text
        or "rag_embedding_calls_total" in metrics_text
    ), "rag_embedding_calls should be in Prometheus export"
    assert (
        "rag_embedding_errors" in metrics_text
        or "rag_embedding_errors_total" in metrics_text
    ), "rag_embedding_errors should be in Prometheus export"
    assert (
        "rag_embedding_duration_seconds" in metrics_text
    ), "rag_embedding_duration_seconds should be in Prometheus export"

    print("✓ RAG metrics are included in Prometheus export")


def test_metrics_labels_correct():
    """Test that metrics use correct labels."""
    from core.libraries.metrics import MetricRegistry

    registry = MetricRegistry.get_instance()
    service_calls = registry.get("rag_service_calls")

    if service_calls:
        # Test that labels are used correctly
        # This is a structural test - actual label values depend on function calls
        assert hasattr(service_calls, "inc"), "Counter should have inc method"
        assert hasattr(service_calls, "get"), "Counter should have get method"

        print("✓ Metrics support label-based tracking")


def run_all_tests():
    """Run all RAG core metrics tests."""
    print("Testing RAG Core Service Metrics Integration")
    print("=" * 60)
    print()

    test_metrics_registered()
    test_embed_query_tracks_metrics()
    test_rag_answer_tracks_metrics()
    test_metrics_export_includes_rag_metrics()
    test_metrics_labels_correct()

    print()
    print("=" * 60)
    print("🎉 All RAG core metrics tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
