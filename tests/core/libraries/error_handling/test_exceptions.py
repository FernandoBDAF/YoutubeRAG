"""
Tests for Error Handling Exception Hierarchy.

Simple tests to verify exception formatting and context preservation.
Run with: python -m core.libraries.error_handling.test_exceptions
"""

from core.libraries.error_handling.exceptions import (
    ApplicationError,
    StageError,
    AgentError,
    PipelineError,
    ConfigurationError,
    DatabaseError,
    LLMError,
    wrap_exception,
)


def test_application_error_basic():
    """Test basic ApplicationError without context."""
    try:
        raise ApplicationError("Something went wrong")
    except ApplicationError as e:
        assert str(e) == "Something went wrong"
        assert e.message == "Something went wrong"
        assert e.context == {}
        assert e.cause is None
        print("✓ Basic ApplicationError works")


def test_application_error_with_context():
    """Test ApplicationError with context."""
    try:
        raise ApplicationError(
            "Processing failed",
            context={"chunk_id": "123", "stage": "extraction", "attempt": 3},
        )
    except ApplicationError as e:
        msg = str(e)
        assert "Processing failed" in msg
        assert "chunk_id=123" in msg
        assert "stage=extraction" in msg
        assert "attempt=3" in msg
        print("✓ ApplicationError with context works")
        print(f"  Message: {msg}")


def test_application_error_with_cause():
    """Test ApplicationError with cause chaining."""
    original = ValueError("Invalid value")
    try:
        raise ApplicationError("Higher level error", cause=original)
    except ApplicationError as e:
        msg = str(e)
        assert "Higher level error" in msg
        assert "ValueError" in msg
        assert "Invalid value" in msg
        assert e.cause is original
        print("✓ ApplicationError with cause works")
        print(f"  Message: {msg}")


def test_application_error_full():
    """Test ApplicationError with both context and cause."""
    original = KeyError("missing_field")
    try:
        raise ApplicationError(
            "Data validation failed",
            context={"entity_id": "abc-123", "field": "name"},
            cause=original,
        )
    except ApplicationError as e:
        msg = str(e)
        assert "Data validation failed" in msg
        assert "entity_id=abc-123" in msg
        assert "field=name" in msg
        assert "KeyError" in msg
        assert "missing_field" in msg
        print("✓ ApplicationError with context + cause works")
        print(f"  Message: {msg}")


def test_specialized_exceptions():
    """Test all specialized exception types."""
    exceptions = [
        (StageError, "Stage failed", {"stage": "extraction"}),
        (AgentError, "Agent failed", {"agent": "GraphExtractionAgent"}),
        (PipelineError, "Pipeline failed", {"pipeline": "graphrag"}),
        (ConfigurationError, "Config invalid", {"db_name": None}),
        (DatabaseError, "DB write failed", {"collection": "entities"}),
        (LLMError, "LLM call failed", {"model": "gpt-4o-mini", "attempts": 3}),
    ]

    for exc_class, message, context in exceptions:
        try:
            raise exc_class(message, context=context)
        except exc_class as e:
            msg = str(e)
            assert message in msg
            for key, value in context.items():
                assert f"{key}={value}" in msg
            print(f"✓ {exc_class.__name__} works")


def test_wrap_exception():
    """Test exception wrapping helper."""
    original = RuntimeError("Original problem")

    try:
        raise wrap_exception(
            "Wrapped error",
            original,
            error_class=StageError,
            stage="entity_resolution",
            chunks_processed=5000,
        )
    except StageError as e:
        msg = str(e)
        assert "Wrapped error" in msg
        assert "stage=entity_resolution" in msg
        assert "chunks_processed=5000" in msg
        assert "RuntimeError" in msg
        assert "Original problem" in msg
        assert e.cause is original
        print("✓ wrap_exception() works")
        print(f"  Message: {msg}")


def test_add_context():
    """Test dynamic context addition."""
    try:
        error = ApplicationError("Base error", context={"initial": "value"})
        error.add_context(added="new_value", another="data")
        raise error
    except ApplicationError as e:
        msg = str(e)
        assert "initial=value" in msg
        assert "added=new_value" in msg
        assert "another=data" in msg
        print("✓ add_context() works")
        print(f"  Message: {msg}")


def test_empty_cause_message():
    """Test handling of exceptions with empty __str__."""

    class SilentException(Exception):
        def __str__(self):
            return ""

    original = SilentException()

    try:
        raise ApplicationError("Handling silent exception", cause=original)
    except ApplicationError as e:
        msg = str(e)
        assert "Handling silent exception" in msg
        assert "SilentException" in msg  # Type still shown
        assert "(no message)" in msg  # Fallback for empty message
        print("✓ Empty cause message handled correctly")
        print(f"  Message: {msg}")


def run_all_tests():
    """Run all exception tests."""
    print("Testing Error Handling Exception Hierarchy")
    print("=" * 60)
    print()

    test_application_error_basic()
    test_application_error_with_context()
    test_application_error_with_cause()
    test_application_error_full()
    print()

    test_specialized_exceptions()
    print()

    test_wrap_exception()
    test_add_context()
    test_empty_cause_message()

    print()
    print("=" * 60)
    print("🎉 All exception tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
