#!/usr/bin/env python3
"""
Check NORTH_STAR Size Limits - Blocking Validation Script

Enforces NORTH_STAR size limits:
- Minimum: 800 lines (informational)
- Warning at 1,500 lines: "Consider splitting into multiple north stars"
- Error at 2,000 lines: "Must split" (exit code 1)

Usage:
    python LLM/scripts/validation/check_north_star_size.py @NORTH_STAR_FILE.md
    python LLM/scripts/validation/check_north_star_size.py NORTH_STAR_FILE.md

Exit Codes:
    0 = Within limits (OK to proceed)
    1 = Limits exceeded (MUST fix before continuing)
    2 = Warning (consider action)
"""

import argparse
import sys
from pathlib import Path


def count_lines(file_path: Path) -> int:
    """Count total lines in NORTH_STAR file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return len(f.readlines())


def check_limits(file_path: Path) -> tuple[bool, str, int]:
    """
    Check if NORTH_STAR exceeds size limits.

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

    # Minimum check (informational)
    if line_count < 800:
        warnings.append(
            f"ℹ️  Line count: {line_count} (below 800-line minimum)\n"
            f"   → NORTH_STAR documents should be comprehensive (800-2,000 lines)"
        )

    # Line count checks
    if line_count >= 2000:
        errors.append(
            f"❌ Line count: {line_count} (exceeds 2,000-line limit)\n"
            f"   → MUST split into multiple NORTH_STAR documents"
        )
    elif line_count >= 1500:
        warnings.append(
            f"⚠️  Line count: {line_count} (approaching 2,000-line limit)\n"
            f"   → Consider splitting into multiple north stars"
        )

    # Build message
    if errors:
        message = "❌ NORTH_STAR EXCEEDS HARD LIMIT - MUST FIX\n\n"
        message += "\n".join(errors)
        if warnings:
            message += "\n\n" + "\n".join(warnings)
        message += "\n\n📖 See: LLM/guides/NORTH-STAR-GUIDE.md"
        message += "\n📋 Template: LLM/templates/NORTH_STAR-TEMPLATE.md"
        message += "\n💡 Recommendation: Split into multiple NORTH_STAR documents by domain or concern"
        return False, message, 1

    if warnings:
        message = "⚠️  NORTH_STAR SIZE WARNING\n\n"
        message += "\n".join(warnings)
        if line_count >= 1500:
            message += (
                "\n\n💡 Recommendation: Consider splitting into multiple NORTH_STAR documents."
            )
        elif line_count < 800:
            message += (
                "\n\n💡 Recommendation: Ensure NORTH_STAR is comprehensive enough (800-2,000 lines)."
            )
        message += "\n📖 See: LLM/guides/NORTH-STAR-GUIDE.md"
        return True, message, 2

    # Within limits
    message = f"✅ NORTH_STAR WITHIN LIMITS\n\n"
    message += f"Lines: {line_count} / 2,000 ✅\n"
    message += f"Size: {'Typical' if line_count < 1500 else 'Large'} NORTH_STAR\n"
    return True, message, 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check NORTH_STAR size limits (800-2,000 lines)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python LLM/scripts/validation/check_north_star_size.py @NORTH_STAR_FEATURE.md
  python LLM/scripts/validation/check_north_star_size.py NORTH_STAR_FEATURE.md

Limits:
  - Lines: 800-2,000 (warning at 1,500, error at 2,000)
  - Below 800: Informational (should be comprehensive)
  - Above 2,000: Must split into multiple NORTH_STAR documents

Exit Codes:
  0 = Within limits (OK to proceed)
  1 = Limits exceeded (MUST fix before continuing)
  2 = Warning (consider action)
        """,
    )

    parser.add_argument(
        "north_star_file",
        help="NORTH_STAR file (e.g., @NORTH_STAR_FEATURE.md or NORTH_STAR_FEATURE.md)",
    )

    args = parser.parse_args()

    try:
        # Clean file path
        north_star_path = Path(args.north_star_file.replace("@", ""))

        # Check limits
        pass_check, message, exit_code = check_limits(north_star_path)

        # Print message
        print(message)

        # Exit code
        sys.exit(exit_code)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

