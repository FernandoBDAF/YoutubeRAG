#!/usr/bin/env python3
"""
Check GrammaPlan Size Limits - Blocking Validation Script

Enforces GrammaPlan size limits:
- Warning at 1,000 lines: "Consider splitting or simplifying"
- Error at 1,500 lines: "MUST split into multiple GrammaPlans or convert to NORTH_STAR" (exit code 1)

Usage:
    python LLM/scripts/validation/check_grammaplan_size.py @GRAMMAPLAN_FILE.md
    python LLM/scripts/validation/check_grammaplan_size.py GRAMMAPLAN_FILE.md

Exit Codes:
    0 = Within limits (OK to proceed)
    1 = Limits exceeded (MUST fix before continuing)
    2 = Warning (consider action)
"""

import argparse
import sys
from pathlib import Path


def count_lines(file_path: Path) -> int:
    """Count total lines in GrammaPlan file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return len(f.readlines())


def check_limits(file_path: Path) -> tuple[bool, str, int]:
    """
    Check if GrammaPlan exceeds size limits.

    Returns:
        (pass, message, exit_code) - pass=True if within limits, False if exceeded
        exit_code: 0=OK, 1=Error, 2=Warning
    """
    if not file_path.exists():
        return False, f"❌ Error: File not found: {file_path}", 1

    # Count lines
    line_count = count_lines(file_path)

    # Check limits
    errors = []
    warnings = []

    # Line count checks
    if line_count >= 1500:
        errors.append(
            f"❌ Line count: {line_count} (exceeds 1,500-line limit)\n"
            f"   → MUST split into multiple GrammaPlans or convert to NORTH_STAR"
        )
    elif line_count >= 1000:
        warnings.append(
            f"⚠️  Line count: {line_count} (approaching 1,500-line limit)\n"
            f"   → Consider splitting or simplifying"
        )
    elif line_count < 600:
        warnings.append(
            f"ℹ️  Line count: {line_count} (below 600-line minimum)\n"
            f"   → This might be a PLAN instead of a GrammaPlan"
        )

    # Build message
    if errors:
        message = "❌ GRAMMAPLAN EXCEEDS HARD LIMIT - MUST FIX\n\n"
        message += "\n".join(errors)
        if warnings:
            message += "\n\n" + "\n".join(warnings)
        message += "\n\n📖 See: LLM/guides/GRAMMAPLAN-GUIDE.md"
        message += "\n📋 Template: LLM/templates/GRAMMAPLAN-TEMPLATE.md"
        message += "\n⭐ Consider: LLM/guides/NORTH-STAR-GUIDE.md (if strategic vision)"
        return False, message, 1

    if warnings:
        message = "⚠️  GRAMMAPLAN SIZE WARNING\n\n"
        message += "\n".join(warnings)
        if line_count >= 1000:
            message += (
                "\n\n💡 Recommendation: Consider splitting into multiple GrammaPlans or simplifying."
            )
        elif line_count < 600:
            message += (
                "\n\n💡 Recommendation: Verify this should be a GrammaPlan (vs. PLAN)."
            )
        message += "\n📖 See: LLM/guides/GRAMMAPLAN-GUIDE.md"
        return True, message, 2

    # Within limits
    message = f"✅ GRAMMAPLAN WITHIN LIMITS\n\n"
    message += f"Lines: {line_count} / 1,500 ✅\n"
    message += f"Size: {'Typical' if line_count < 1000 else 'Large'} GrammaPlan\n"
    return True, message, 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check GrammaPlan size limits (600-1,500 lines)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python LLM/scripts/validation/check_grammaplan_size.py @GRAMMAPLAN_FEATURE.md
  python LLM/scripts/validation/check_grammaplan_size.py GRAMMAPLAN_FEATURE.md

Limits:
  - Lines: 600-1,500 (warning at 1,000, error at 1,500)
  - Below 600: Might be PLAN instead
  - Above 1,500: Must split or convert to NORTH_STAR

Exit Codes:
  0 = Within limits (OK to proceed)
  1 = Limits exceeded (MUST fix before continuing)
  2 = Warning (consider action)
        """,
    )

    parser.add_argument(
        "grammaplan_file",
        help="GrammaPlan file (e.g., @GRAMMAPLAN_FEATURE.md or GRAMMAPLAN_FEATURE.md)",
    )

    args = parser.parse_args()

    try:
        # Clean file path
        grammaplan_path = Path(args.grammaplan_file.replace("@", ""))

        # Check limits
        pass_check, message, exit_code = check_limits(grammaplan_path)

        # Print message
        print(message)

        # Exit code
        sys.exit(exit_code)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

