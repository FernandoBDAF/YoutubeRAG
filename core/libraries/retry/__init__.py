"""
Retry Library - Cross-Cutting Concern.

Provides automatic retry logic with configurable backoff policies.
Part of the CORE libraries - Tier 1 (full implementation).

Usage:
    from core.libraries.retry import with_retry, ExponentialBackoff

    # Simple usage with defaults
    @with_retry(max_attempts=3)
    def call_api():
        # Automatically retries with exponential backoff
        ...

    # Custom policy
    policy = ExponentialBackoff(max_attempts=5, base_delay=2.0)

    @with_retry(policy=policy)
    def important_operation():
        ...

    # Specialized for LLM calls
    from core.libraries.retry import retry_llm_call

    @retry_llm_call(max_attempts=5)
    def call_openai():
        ...
"""

from core.libraries.retry.policies import (
    RetryPolicy,
    ExponentialBackoff,
    FixedDelay,
    NoRetry,
    DEFAULT_POLICY,
)

from core.libraries.retry.decorators import (
    with_retry,
    retry_llm_call,
)


__all__ = [
    # Policies
    "RetryPolicy",
    "ExponentialBackoff",
    "FixedDelay",
    "NoRetry",
    "DEFAULT_POLICY",
    # Decorators
    "with_retry",
    "retry_llm_call",
]
