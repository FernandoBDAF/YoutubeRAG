"""
Exception Logging Helpers.

Provides helpers for logging exceptions with guaranteed visibility.
Part of the CORE libraries - logging library.
"""

import logging
from typing import Any, Optional


def log_exception(
    logger: logging.Logger,
    message: str,
    exception: Exception,
    include_traceback: bool = True,
    context: Optional[dict] = None,
) -> None:
    """Log exception with guaranteed type and message visibility.

    Ensures exception type is ALWAYS shown, preventing empty error messages.
    This is the core logging pattern that prevents the "empty error" problem.

    Args:
        logger: Logger instance to use
        message: Descriptive message about what failed
        exception: The exception that occurred
        include_traceback: Include full traceback (default: True)
        context: Optional dict of contextual information

    Example:
        try:
            risky_operation()
        except Exception as e:
            log_exception(logger, "Operation failed", e)

        # Logs:
        # "ERROR - Operation failed: ValueError: Invalid data
        # [Full traceback]"

        # With context:
        log_exception(logger, "Stage failed", e, context={'stage': 'extraction', 'chunk_id': '123'})
        # "ERROR - Stage failed: StageError: ... [Context: stage=extraction, chunk_id=123]"
    """
    # CRITICAL: Always capture exception type (prevents empty messages!)
    error_type = type(exception).__name__
    error_msg = str(exception) or "(no message)"

    # Build full message
    full_msg = f"{message}: {error_type}: {error_msg}"

    # Add context if provided
    if context:
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
        full_msg += f" [Context: {context_str}]"

    # Log with or without traceback
    if include_traceback:
        logger.error(full_msg, exc_info=True)
    else:
        logger.error(full_msg)


def format_exception_for_log(exception: Exception) -> str:
    """Format exception as 'ExceptionType: message' for logging.

    Handles empty exception messages gracefully.

    Args:
        exception: Exception to format

    Returns:
        Formatted string like "ValueError: Invalid data" or "KeyError: (no message)"
    """
    error_type = type(exception).__name__
    error_msg = str(exception) or "(no message)"
    return f"{error_type}: {error_msg}"
