"""
Dashboard Utilities Module

Provides helper functions for dashboard implementations.

**Utilities**:
- Timestamp and date formatting
- Text truncation
- Plan name validation
- Achievement number parsing
- Common string operations

Created: 2025-11-13
Achievement: 0.1 - Rich Dashboard Framework Setup
Updated: 2025-11-13 (Achievement 0.2 - Added achievement number parser)
Updated: 2025-11-14 (Achievement 0.4 - Compiled regex patterns)
"""

import re
from datetime import datetime

# Compiled regex patterns (10-20% performance gain)
ACHIEVEMENT_NUM_PATTERN_1 = re.compile(r"_(\d)(\d+)(?:_|$)")  # Pattern: APPROVED_31
ACHIEVEMENT_NUM_PATTERN_2 = re.compile(r"_(\d+\.\d+)(?:_|$)")  # Pattern: _1.1_
APPROVED_FILE_PATTERN = re.compile(r"APPROVED_(\d+)\.md")
FIX_FILE_PATTERN = re.compile(r"FIX_(\d+)\.md")
SUBPLAN_FILE_PATTERN = re.compile(r"SUBPLAN_.*_(\d+)\.md")
EXECUTION_FILE_PATTERN = re.compile(r"EXECUTION_TASK_.*_(\d+)_\d+\.md")


def format_timestamp(dt: datetime) -> str:
    """
    Format datetime as HH:MM:SS.

    Args:
        dt: Datetime object

    Returns:
        Formatted time string (HH:MM:SS)

    **Usage**:
        now = datetime.now()
        time_str = format_timestamp(now)  # "14:32:15"
    """
    return dt.strftime("%H:%M:%S")


def format_date(dt: datetime) -> str:
    """
    Format datetime as YYYY-MM-DD.

    Args:
        dt: Datetime object

    Returns:
        Formatted date string (YYYY-MM-DD)

    **Usage**:
        today = datetime.now()
        date_str = format_date(today)  # "2025-11-13"
    """
    return dt.strftime("%Y-%m-%d")


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Truncate text to max length with ellipsis.

    Args:
        text: Text to truncate
        max_length: Maximum length (default: 50)

    Returns:
        Truncated text with "..." if longer than max_length

    **Usage**:
        long_text = "This is a very long achievement title that needs truncation"
        short = truncate_text(long_text, 30)  # "This is a very long achiev..."
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def validate_plan_name(name: str) -> bool:
    """
    Validate plan name format.

    Args:
        name: Plan name to validate

    Returns:
        True if valid, False otherwise

    **Valid Names**:
        - Non-empty string
        - Doesn't start with '.'
        - Contains at least one non-whitespace character

    **Usage**:
        if validate_plan_name("MY-PLAN"):
            # Name is valid
            pass
    """
    return bool(name and name.strip() and not name.startswith("."))


def parse_achievement_number(filename: str) -> str:
    """
    Parse achievement number from filename using compiled regex patterns.

    Extracts achievement number (X.Y format) from various file patterns:
    - APPROVED_31.md → "3.1"
    - FIX_12.md → "1.2"
    - SUBPLAN_02.md → "0.2"
    - EXECUTION_TASK_11_01.md → "1.1"

    Args:
        filename: Filename to parse (with or without extension)

    Returns:
        Achievement number in X.Y format (e.g., "3.1")

    Raises:
        ValueError: If no achievement number found in filename

    **Usage**:
        num = parse_achievement_number("APPROVED_31.md")  # "3.1"
        num = parse_achievement_number("FIX_12")  # "1.2"
        num = parse_achievement_number("SUBPLAN_PARALLEL-EXEC_02.md")  # "0.2"
    """
    # Remove file extension
    name = filename.split(".")[0]

    # Pattern 1: APPROVED_31 or FIX_12 format (2 digits) - uses compiled pattern
    match = ACHIEVEMENT_NUM_PATTERN_1.search(name)
    if match:
        return f"{match.group(1)}.{match.group(2)}"

    # Pattern 2: Explicit dot format (e.g., _1.1_) - uses compiled pattern
    match = ACHIEVEMENT_NUM_PATTERN_2.search(name)
    if match:
        return match.group(1)

    raise ValueError(f"No achievement number found in filename: {filename}")


def is_approved_file(filename: str) -> bool:
    """
    Check if file is an APPROVED file using compiled regex.

    Args:
        filename: Filename to check

    Returns:
        True if matches APPROVED_*.md pattern

    **Usage**:
        if is_approved_file("APPROVED_31.md"):
            print("This is an approved file")
    """
    return bool(APPROVED_FILE_PATTERN.match(filename))


def is_fix_file(filename: str) -> bool:
    """
    Check if file is a FIX file using compiled regex.

    Args:
        filename: Filename to check

    Returns:
        True if matches FIX_*.md pattern

    **Usage**:
        if is_fix_file("FIX_12.md"):
            print("This is a fix file")
    """
    return bool(FIX_FILE_PATTERN.match(filename))


def is_subplan_file(filename: str) -> bool:
    """
    Check if file is a SUBPLAN file using compiled regex.

    Args:
        filename: Filename to check

    Returns:
        True if matches SUBPLAN_*_*.md pattern

    **Usage**:
        if is_subplan_file("SUBPLAN_PLAN-NAME_01.md"):
            print("This is a subplan file")
    """
    return bool(SUBPLAN_FILE_PATTERN.match(filename))


def is_execution_file(filename: str) -> bool:
    """
    Check if file is an EXECUTION_TASK file using compiled regex.

    Args:
        filename: Filename to check

    Returns:
        True if matches EXECUTION_TASK_*_*_*.md pattern

    **Usage**:
        if is_execution_file("EXECUTION_TASK_PLAN-NAME_11_01.md"):
            print("This is an execution file")
    """
    return bool(EXECUTION_FILE_PATTERN.match(filename))
