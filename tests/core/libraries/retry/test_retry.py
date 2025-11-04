"""
Tests for Retry Library.

Run with: python -m tests.core.libraries.retry.test_retry
"""

import time
from core.libraries.retry import (
    with_retry,
    ExponentialBackoff,
    FixedDelay,
    retry_llm_call,
)


# Test counter for simulating failures
attempt_count = 0


def test_successful_on_first_try():
    """Test function that succeeds immediately."""
    global attempt_count
    attempt_count = 0

    @with_retry(max_attempts=3)
    def succeeds():
        global attempt_count
        attempt_count += 1
        return "success"

    result = succeeds()
    assert result == "success"
    assert attempt_count == 1  # Should only call once
    print("✓ Successful on first try (no retry needed)")


def test_retry_until_success():
    """Test function that fails then succeeds."""
    global attempt_count
    attempt_count = 0

    @with_retry(max_attempts=3, base_delay=0.1)
    def fails_twice():
        global attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ValueError("Not yet")
        return "success"

    result = fails_twice()
    assert result == "success"
    assert attempt_count == 3  # Should retry twice
    print("✓ Retry until success works")


def test_max_retries_exceeded():
    """Test function that always fails."""
    global attempt_count
    attempt_count = 0

    @with_retry(max_attempts=3, base_delay=0.1)
    def always_fails():
        global attempt_count
        attempt_count += 1
        raise ValueError("Always fails")

    try:
        always_fails()
        assert False, "Should have raised exception"
    except ValueError as e:
        assert str(e) == "Always fails"
        assert attempt_count == 3  # Should try exactly 3 times

    print("✓ Max retries enforced")


def test_exponential_backoff_timing():
    """Test exponential backoff delays."""
    policy = ExponentialBackoff(max_attempts=4, base_delay=0.1, multiplier=2.0)

    delays = [policy.get_delay(i) for i in range(1, 5)]
    assert delays[0] == 0.1  # Attempt 1: 0.1s
    assert delays[1] == 0.2  # Attempt 2: 0.2s
    assert delays[2] == 0.4  # Attempt 3: 0.4s
    assert delays[3] == 0.8  # Attempt 4: 0.8s

    print("✓ Exponential backoff calculates correct delays")


def test_fixed_delay():
    """Test fixed delay policy."""
    policy = FixedDelay(max_attempts=3, delay=0.5)

    delays = [policy.get_delay(i) for i in range(1, 4)]
    assert all(d == 0.5 for d in delays)

    print("✓ Fixed delay works")


def test_retry_on_specific_exceptions():
    """Test retrying only on specific exception types."""
    global attempt_count
    attempt_count = 0

    @with_retry(max_attempts=3, retry_on=(ValueError,), base_delay=0.1)
    def raises_key_error():
        global attempt_count
        attempt_count += 1
        raise KeyError("Not retryable")

    try:
        raises_key_error()
        assert False, "Should have raised KeyError"
    except KeyError:
        assert attempt_count == 1  # Should NOT retry KeyError

    print("✓ Retry only on specified exceptions")


def test_llm_retry_decorator():
    """Test specialized LLM retry decorator."""
    global attempt_count
    attempt_count = 0

    @retry_llm_call(max_attempts=2)
    def simulated_llm_call():
        global attempt_count
        attempt_count += 1
        if attempt_count < 2:
            raise Exception("Rate limit")
        return "LLM response"

    result = simulated_llm_call()
    assert result == "LLM response"
    assert attempt_count == 2

    print("✓ LLM retry decorator works")


def run_all_tests():
    """Run all retry tests."""
    print("Testing Retry Library")
    print("=" * 60)
    print()

    test_successful_on_first_try()
    test_retry_until_success()
    test_max_retries_exceeded()
    test_exponential_backoff_timing()
    test_fixed_delay()
    test_retry_on_specific_exceptions()
    test_llm_retry_decorator()

    print()
    print("=" * 60)
    print("🎉 All retry tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
