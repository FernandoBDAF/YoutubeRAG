"""
Integration Tests for BaseStage with Observability Libraries.

Tests that BaseStage correctly integrates with error_handling, logging, and metrics.
Run with: python -m tests.core.base.test_stage
"""

import logging
from typing import Any, Dict, Iterable
from core.base.stage import BaseStage
from core.models.config import BaseStageConfig
from core.libraries.metrics import MetricRegistry, export_prometheus_text


class TestStage(BaseStage):
    """Simple test stage for integration testing."""

    name = "test_stage"
    description = "Test stage for integration"
    ConfigCls = BaseStageConfig

    def __init__(self):
        super().__init__()
        self.docs_to_return = []
        self.should_fail = False
        self.fail_on_doc = None

    def setup(self):
        """Setup (no-op for tests)."""
        pass

    def iter_docs(self) -> Iterable[Dict[str, Any]]:
        """Return test documents."""
        return self.docs_to_return

    def handle_doc(self, doc: Dict[str, Any]) -> None:
        """Process document."""
        if self.fail_on_doc and doc.get("id") == self.fail_on_doc:
            raise ValueError(f"Simulated failure on doc {self.fail_on_doc}")

        if self.should_fail:
            raise RuntimeError("Simulated stage failure")

        # Simulate processing
        doc["processed"] = True


def test_stage_successful_execution():
    """Test stage executes successfully and tracks metrics."""
    # Clear metrics
    registry = MetricRegistry.get_instance()
    registry.reset_all()

    # Create and run stage
    stage = TestStage()
    stage.docs_to_return = [{"id": 1}, {"id": 2}, {"id": 3}]

    config = BaseStageConfig()
    exit_code = stage.run(config)

    # Verify success
    assert exit_code == 0, f"Expected exit_code 0, got {exit_code}"
    assert stage.stats["processed"] == 3
    assert stage.stats["failed"] == 0

    # Verify metrics collected
    started = registry.get("stage_started")
    completed = registry.get("stage_completed")

    assert started.get(labels={"stage": "test_stage"}) == 1.0
    assert completed.get(labels={"stage": "test_stage"}) == 1.0

    print("✓ Stage successful execution and metrics tracking")


def test_stage_handles_document_errors():
    """Test stage continues after document errors."""
    registry = MetricRegistry.get_instance()
    registry.reset_all()

    # Create stage that fails on doc 2
    stage = TestStage()
    stage.docs_to_return = [{"id": 1}, {"id": 2}, {"id": 3}]
    stage.fail_on_doc = 2

    config = BaseStageConfig()
    exit_code = stage.run(config)

    # Should still complete (exit_code 0)
    assert exit_code == 0
    assert stage.stats["processed"] == 2  # Only docs 1 and 3 processed successfully
    assert stage.stats["failed"] == 1  # Doc 2 failed

    # Verify metrics
    docs_failed = registry.get("documents_failed")
    assert docs_failed.get(labels={"stage": "test_stage"}) == 1.0

    print("✓ Stage handles document errors correctly")


def test_stage_tracks_duration():
    """Test stage tracks execution duration."""
    registry = MetricRegistry.get_instance()
    registry.reset_all()

    stage = TestStage()
    stage.docs_to_return = [{"id": 1}]

    config = BaseStageConfig()
    stage.run(config)

    # Verify duration histogram has observations
    duration = registry.get("stage_duration_seconds")
    stats = duration.summary(labels={"stage": "test_stage"})

    assert stats["count"] == 1
    assert stats["sum"] > 0  # Should have non-zero duration

    print("✓ Stage tracks execution duration")


def test_stage_fatal_error_tracking():
    """Test stage tracks errors even when continuing."""
    registry = MetricRegistry.get_instance()
    registry.reset_all()

    stage = TestStage()
    stage.fail_on_doc = 1  # Fail on first doc
    stage.docs_to_return = [{"id": 1}]

    config = BaseStageConfig()
    exit_code = stage.run(config)

    # With @handle_errors(reraise=False), still returns 0
    assert exit_code == 0

    # But metrics track the failure
    docs_failed = registry.get("documents_failed")
    assert docs_failed.get(labels={"stage": "test_stage"}) == 1.0

    # And error logged in errors_total (via log_exception)
    errors_total = registry.get("errors_total")
    # Should have at least 1 error tracked
    all_errors = errors_total.get_all()
    assert len(all_errors) > 0

    print("✓ Stage tracks errors in metrics")


def test_stage_operation_logging():
    """Test stage logs operation lifecycle."""
    import io
    import sys

    # Capture logs
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.INFO)

    logger = logging.getLogger("core.libraries.logging.operations")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    stage = TestStage()
    stage.docs_to_return = [{"id": 1}]

    config = BaseStageConfig()
    stage.run(config)

    log_output = log_capture.getvalue()

    # Verify operation logging
    assert "[OPERATION] Starting stage_test_stage" in log_output
    assert "[OPERATION] Completed stage_test_stage" in log_output

    logger.removeHandler(handler)

    print("✓ Stage logs operation lifecycle")


def test_stage_max_docs_limit():
    """Test stage respects max config."""
    registry = MetricRegistry.get_instance()
    registry.reset_all()

    stage = TestStage()
    stage.docs_to_return = [{"id": i} for i in range(10)]

    config = BaseStageConfig(max=5)
    stage.run(config)

    # Should only process 5
    assert stage.stats["processed"] == 5

    docs_processed = registry.get("documents_processed")
    assert docs_processed.get(labels={"stage": "test_stage"}) == 5.0

    print("✓ Stage respects max document limit")


def run_all_tests():
    """Run all BaseStage integration tests."""
    print("Testing BaseStage Integration with Observability Libraries")
    print("=" * 60)
    print()

    # Setup logging to avoid noise
    logging.basicConfig(level=logging.WARNING, format="")

    test_stage_successful_execution()
    test_stage_handles_document_errors()
    test_stage_tracks_duration()
    test_stage_fatal_error_tracking()
    test_stage_operation_logging()
    test_stage_max_docs_limit()

    print()
    print("=" * 60)
    print("🎉 All BaseStage integration tests passed!")
    print("🎉 BaseStage correctly integrates with:")
    print("  - error_handling library (exception handling)")
    print("  - logging library (operation lifecycle)")
    print("  - metrics library (tracking)")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
