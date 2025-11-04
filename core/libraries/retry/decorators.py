"""
Retry Decorators.

Provides decorators for automatic retry with configurable policies.
Part of the CORE libraries - retry library.
"""

import time
import logging
import functools
from typing import Callable, Optional, Tuple, Type

from core.libraries.retry.policies import (
    RetryPolicy,
    ExponentialBackoff,
    DEFAULT_POLICY,
)


logger = logging.getLogger(__name__)


def with_retry(
    max_attempts: int = 3,
    backoff: str = "exponential",
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retry_on: Tuple[Type[Exception], ...] = (Exception,),
    policy: Optional[RetryPolicy] = None,
) -> Callable:
    """Decorator for automatic retry with configurable policy.

    Integrates with logging and metrics libraries.

    Args:
        max_attempts: Maximum retry attempts (default: 3)
        backoff: Backoff strategy - "exponential" or "fixed" (default: "exponential")
        base_delay: Base delay in seconds (default: 1.0)
        max_delay: Maximum delay for exponential backoff (default: 60.0)
        retry_on: Tuple of exception types to retry (default: all exceptions)
        policy: Custom RetryPolicy instance (overrides other params)

    Returns:
        Decorated function with retry logic

    Example:
        @with_retry(max_attempts=3, backoff="exponential")
        def call_external_api():
            # Automatically retries on failure with exponential backoff
            ...

        @with_retry(max_attempts=5, base_delay=2.0, retry_on=(TimeoutError, ConnectionError))
        def flaky_operation():
            # Only retries on specific errors
            ...
    """
    # Determine policy
    if policy is None:
        if backoff == "exponential":
            from core.libraries.retry.policies import ExponentialBackoff

            policy = ExponentialBackoff(
                max_attempts=max_attempts, base_delay=base_delay, max_delay=max_delay
            )
        elif backoff == "fixed":
            from core.libraries.retry.policies import FixedDelay

            policy = FixedDelay(max_attempts=max_attempts, delay=base_delay)
        else:
            policy = ExponentialBackoff(max_attempts=max_attempts)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            last_exception = None

            # Get logger for this function
            func_logger = logging.getLogger(func.__module__)

            while attempt < policy.max_attempts:
                attempt += 1

                try:
                    # Try the operation
                    result = func(*args, **kwargs)

                    # If successful and we retried, log success
                    if attempt > 1:
                        func_logger.info(
                            f"[RETRY] {func.__name__} succeeded on attempt {attempt}"
                        )

                    return result

                except retry_on as e:
                    last_exception = e

                    # Check if should retry
                    if not policy.should_retry(attempt, e):
                        # No more retries
                        func_logger.error(
                            f"[RETRY] {func.__name__} failed after {attempt} attempts",
                            exc_info=True,
                        )
                        raise

                    # Calculate delay
                    delay = policy.get_delay(attempt)

                    # Log retry with context
                    from core.libraries.error_handling.exceptions import (
                        format_exception_message,
                    )

                    error_msg = format_exception_message(e)

                    func_logger.warning(
                        f"[RETRY] {func.__name__} attempt {attempt} failed: {error_msg}. "
                        f"Retrying in {delay:.1f}s... "
                        f"({policy.max_attempts - attempt} attempts remaining)"
                    )

                    # Track retry metric
                    try:
                        from core.libraries.metrics import MetricRegistry

                        registry = MetricRegistry.get_instance()
                        retry_counter = registry.get("retries_attempted")
                        if retry_counter:
                            retry_counter.inc(
                                labels={
                                    "function": func.__name__,
                                    "error_type": type(e).__name__,
                                }
                            )
                    except Exception:
                        pass

                    # Wait before retry
                    time.sleep(delay)

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


def retry_llm_call(max_attempts: int = 3) -> Callable:
    """Specialized retry decorator for LLM calls.

    Uses exponential backoff optimized for LLM rate limits.

    Args:
        max_attempts: Maximum retry attempts (default: 3)

    Returns:
        Decorated function

    Example:
        @retry_llm_call(max_attempts=5)
        def call_openai():
            # Retries with appropriate backoff for rate limits
            ...
    """
    return with_retry(
        max_attempts=max_attempts,
        backoff="exponential",
        base_delay=1.0,
        max_delay=60.0,
        retry_on=(Exception,),  # Retry on all LLM errors
    )
