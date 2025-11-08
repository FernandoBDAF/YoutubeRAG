#!/usr/bin/env python3
"""
Check PLAN Size Limits - Blocking Validation Script

Enforces PLAN size limits:
- Warning at 700 lines: "Approaching limit, ensure focus maintained"
- Error at 900 lines: "MUST convert to GrammaPlan or split" (exit code 1)
- Warning at 30 hours: "Consider GrammaPlan"
- Error at 40 hours: "MUST convert to GrammaPlan" (exit code 1)

Note: With workflow separation, PLANs provide context for SUBPLAN creation only,
not execution. This enables larger PLANs (900 lines) without context bloat.

Usage:
    python LLM/scripts/check_plan_size.py @PLAN_FILE.md
    python LLM/scripts/check_plan_size.py PLAN_FILE.md

Exit Codes:
    0 = Within limits (OK to proceed)
    1 = Limits exceeded (MUST fix before continuing)
"""

import argparse
import re
import sys
from pathlib import Path


def count_lines(file_path: Path) -> int:
    """Count total lines in PLAN file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return len(f.readlines())


def extract_estimated_effort(content: str) -> int:
    """Extract estimated effort in hours from PLAN content."""
    # Look for "Estimated Effort" or "Total Estimated Effort"
    patterns = [
        r"Total Estimated Effort[:\s]+(\d+)[-\s]*(\d+)?\s*hours?",
        r"Estimated Effort[:\s]+(\d+)[-\s]*(\d+)?\s*hours?",
        r"Estimated[:\s]+(\d+)[-\s]*(\d+)?\s*hours?",
        r"Effort[:\s]+(\d+)[-\s]*(\d+)?\s*hours?",
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            # Take the higher number if range (e.g., "18-22 hours" → 22)
            if match.group(2):
                return int(match.group(2))
            return int(match.group(1))

    # If not found, try to sum individual achievement estimates
    # Look for "Effort: X-Y hours" in achievements
    effort_pattern = r"Effort[:\s]+(\d+)[-\s]*(\d+)?\s*hours?"
    matches = re.findall(effort_pattern, content, re.IGNORECASE)

    if matches:
        total = 0
        for match in matches:
            if match[1]:  # Range
                total += int(match[1])
            else:
                total += int(match[0])
        return total

    return 0  # Not found


def check_limits(file_path: Path) -> tuple[bool, str]:
    """
    Check if PLAN exceeds size limits.

    Returns:
        (pass, message) - pass=True if within limits, False if exceeded
    """
    if not file_path.exists():
        return False, f"❌ Error: File not found: {file_path}"

    # Count lines
    line_count = count_lines(file_path)

    # Read content for effort extraction
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract estimated effort
    estimated_hours = extract_estimated_effort(content)

    # Check limits
    errors = []
    warnings = []

    # Line count checks
    if line_count > 900:
        errors.append(f"❌ Line count: {line_count} (exceeds 900-line limit)\n   → MUST convert to GrammaPlan or split")
    elif line_count > 700:
        warnings.append(f"⚠️  Line count: {line_count} (approaching 900-line limit)\n   → Approaching limit, ensure focus maintained")

    # Effort checks
    if estimated_hours > 40:
        errors.append(f"❌ Estimated effort: {estimated_hours}h (exceeds 40-hour limit)\n   → MUST convert to GrammaPlan")
    elif estimated_hours > 30:
        warnings.append(f"⚠️  Estimated effort: {estimated_hours}h (approaching 40-hour limit)\n   → Consider GrammaPlan")

    # Build message
    if errors:
        message = "❌ PLAN EXCEEDS HARD LIMITS - MUST CONVERT TO GRAMMAPLAN\n\n"
        message += "\n".join(errors)
        if warnings:
            message += "\n\n" + "\n".join(warnings)
        message += "\n\n📖 See: LLM/guides/GRAMMAPLAN-GUIDE.md"
        message += "\n📋 Template: LLM/templates/GRAMMAPLAN-TEMPLATE.md"
        return False, message

    if warnings:
        message = "⚠️  PLAN APPROACHING LIMITS - CONSIDER GRAMMAPLAN\n\n"
        message += "\n".join(warnings)
        message += (
            "\n\n💡 Recommendation: Consider converting to GrammaPlan now to avoid blocking later."
        )
        message += "\n📖 See: LLM/guides/GRAMMAPLAN-GUIDE.md"
        return True, message

    # Within limits
    message = f"✅ PLAN WITHIN LIMITS\n\n"
    message += f"Lines: {line_count} / 900 ✅\n"
    if estimated_hours > 0:
        message += f"Estimated: {estimated_hours}h / 40h ✅\n"
    else:
        message += f"Estimated: Not specified (check manually)\n"
    return True, message


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check PLAN size limits (900 lines / 40 hours)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python LLM/scripts/validation/check_plan_size.py @PLAN_FEATURE.md
  python LLM/scripts/validation/check_plan_size.py PLAN_FEATURE.md

Limits:
  - Lines: 900 maximum (warning at 700)
  - Hours: 40 maximum (warning at 30)

Note: With workflow separation, PLANs can be larger since they provide context
for SUBPLAN creation only, not execution.

Exit Codes:
  0 = Within limits (OK to proceed)
  1 = Limits exceeded (MUST fix before continuing)
        """,
    )

    parser.add_argument("plan_file", help="PLAN file (e.g., @PLAN_FEATURE.md or PLAN_FEATURE.md)")

    args = parser.parse_args()

    try:
        # Clean file path
        plan_path = Path(args.plan_file.replace("@", ""))

        # Check limits
        pass_check, message = check_limits(plan_path)

        # Print message
        print(message)

        # Exit code
        sys.exit(0 if pass_check else 1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
