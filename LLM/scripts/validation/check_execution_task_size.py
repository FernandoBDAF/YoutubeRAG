#!/usr/bin/env python3
"""
Check EXECUTION_TASK Size Limits - Blocking Validation Script

Enforces EXECUTION_TASK size limits:
- Warning at 150 lines: "Approaching limit, condense if possible"
- Error at 200 lines: "MUST create new EXECUTION_TASK" (exit code 1)

Usage:
    python LLM/scripts/check_execution_task_size.py @EXECUTION_TASK_FILE.md
    python LLM/scripts/check_execution_task_size.py EXECUTION_TASK_FILE.md

Exit Codes:
    0 = Within limits (OK to proceed)
    1 = Limits exceeded (MUST fix before continuing)
"""

import argparse
import sys
from pathlib import Path


def count_lines(file_path: Path) -> int:
    """Count total lines in EXECUTION_TASK file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return len(f.readlines())


def check_limit(file_path: Path) -> tuple[bool, str]:
    """
    Check if EXECUTION_TASK exceeds size limits.

    Returns:
        (pass, message) - pass=True if within limits, False if exceeded
    """
    if not file_path.exists():
        return False, f"❌ Error: File not found: {file_path}"

    # Count lines
    line_count = count_lines(file_path)

    # Check limits
    if line_count > 200:
        message = "❌ EXECUTION_TASK EXCEEDS HARD LIMIT - MUST CREATE NEW EXECUTION_TASK\n\n"
        message += f"Current size: {line_count} lines (exceeds 200-line limit)\n\n"
        message += "📋 Actions Required:\n"
        message += "1. Condense iteration log (focus on key decisions only)\n"
        message += "2. Prioritize learning summary (most important insights only)\n"
        message += "3. Remove redundant details\n"
        message += "4. If still >200: Create new EXECUTION_TASK for next phase\n\n"
        message += "📖 See: LLM/templates/EXECUTION_TASK-TEMPLATE.md (Size Limits section)\n"
        message += "📖 See: LLM/guides/CONTEXT-MANAGEMENT.md (EXECUTION_TASK Size Limits)"
        return False, message

    if line_count > 150:
        message = "⚠️  EXECUTION_TASK APPROACHING LIMIT - CONSIDER CONDENSING\n\n"
        message += f"Current size: {line_count} lines (approaching 200-line limit)\n\n"
        message += "💡 Recommendations:\n"
        message += "- Condense iteration log (remove redundant details)\n"
        message += "- Focus learning summary on key insights only\n"
        message += "- Consider creating new EXECUTION_TASK if work continues\n\n"
        message += "📖 See: LLM/templates/EXECUTION_TASK-TEMPLATE.md (Size Limits section)"
        return True, message

    # Within limits
    message = f"✅ EXECUTION_TASK WITHIN LIMITS\n\n"
    message += f"Lines: {line_count} / 200 ✅\n"
    if line_count > 120:
        message += f"💡 Note: Approaching recommended target (120-170 lines ideal)\n"
    return True, message


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check EXECUTION_TASK size limits (200 lines maximum)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python LLM/scripts/check_execution_task_size.py @EXECUTION_TASK_FEATURE_01_01.md
  python LLM/scripts/check_execution_task_size.py EXECUTION_TASK_FEATURE_01_01.md

Limits:
  - Lines: 200 maximum (warning at 150)
  - Target: 120-170 lines (optimal)

Exit Codes:
  0 = Within limits (OK to proceed)
  1 = Limits exceeded (MUST fix before continuing)
        """,
    )

    parser.add_argument(
        "execution_task_file",
        help="EXECUTION_TASK file (e.g., @EXECUTION_TASK_FEATURE_01_01.md or EXECUTION_TASK_FEATURE_01_01.md)",
    )

    args = parser.parse_args()

    try:
        # Clean file path
        file_path = Path(args.execution_task_file.replace("@", ""))

        # Check limits
        pass_check, message = check_limit(file_path)

        # Print message
        print(message)

        # Exit code
        sys.exit(0 if pass_check else 1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
