#!/usr/bin/env python3
"""
Validate Achievement Completion - Blocking Validation Script

Validates that an achievement is properly completed before marking it complete.
Checks: SUBPLAN exists, EXECUTION_TASK exists, deliverables exist.

Usage:
    python LLM/scripts/validate_achievement_completion.py @PLAN_FILE.md --achievement 1.1

Exit Codes:
    0 = Achievement properly completed (OK to mark complete)
    1 = Issues found (MUST fix before marking complete)
"""

import argparse
import re
import sys
from pathlib import Path


def find_achievement_in_plan(plan_path: Path, achievement_num: str) -> dict:
    """Find achievement section in PLAN file."""
    with open(plan_path, "r", encoding="utf-8") as f:
        content = f.read()
        lines = content.split("\n")

    # Find achievement section
    achievement_pattern = rf"\*\*Achievement {re.escape(achievement_num)}\*\*:(.+)"
    achievement_info = {}

    for i, line in enumerate(lines):
        if re.match(achievement_pattern, line):
            # Extract achievement details
            achievement_info["line"] = i
            achievement_info["title"] = line.split(":", 1)[1].strip() if ":" in line else ""

            # Look for deliverables in following lines
            deliverables = []
            for j in range(i, min(i + 50, len(lines))):
                if "Deliverables" in lines[j] or "deliverables" in lines[j].lower():
                    # Extract deliverables (look for list items)
                    for k in range(j, min(j + 20, len(lines))):
                        if lines[k].strip().startswith("-") or lines[k].strip().startswith("*"):
                            deliverable = lines[k].strip().lstrip("-*").strip()
                            if deliverable and not deliverable.startswith("["):
                                deliverables.append(deliverable)
                    break

            achievement_info["deliverables"] = deliverables
            break

    return achievement_info


def check_subplan_exists(feature: str, achievement_num: str) -> bool:
    """Check if SUBPLAN file exists for achievement."""
    subplan_num = achievement_num.replace(".", "")
    subplan_file = Path(f"SUBPLAN_{feature}_{subplan_num}.md")
    return subplan_file.exists()


def check_execution_task_exists(feature: str, achievement_num: str) -> bool:
    """Check if EXECUTION_TASK file exists for achievement."""
    subplan_num = achievement_num.replace(".", "")
    # Check for EXECUTION_TASK files (may have multiple attempts)
    execution_pattern = f"EXECUTION_TASK_{feature}_{subplan_num}_*.md"
    execution_files = list(Path(".").glob(execution_pattern))
    return len(execution_files) > 0


def check_deliverables_exist(achievement: dict) -> list:
    """Check if deliverables from achievement exist."""
    missing = []

    for deliverable in achievement.get("deliverables", []):
        # Try to extract file paths from deliverable text
        # Look for patterns like "LLM/scripts/script.py" or "file.md"
        file_patterns = re.findall(r"([A-Za-z0-9_/-]+\.(py|md|txt|sh))", deliverable)

        for pattern, ext in file_patterns:
            file_path = Path(pattern)
            if not file_path.exists():
                missing.append(pattern)

    return missing


def validate_achievement(plan_path: Path, achievement_num: str) -> tuple[bool, str]:
    """
    Validate achievement completion.

    Returns:
        (pass, message) - pass=True if valid, False if issues found
    """
    if not plan_path.exists():
        return False, f"❌ Error: PLAN file not found: {plan_path}"

    # Extract feature name
    feature = plan_path.stem.replace("PLAN_", "")

    # Find achievement
    achievement = find_achievement_in_plan(plan_path, achievement_num)

    if not achievement:
        return False, f"❌ Error: Achievement {achievement_num} not found in PLAN"

    # Check prerequisites
    errors = []
    warnings = []

    # Check SUBPLAN
    if not check_subplan_exists(feature, achievement_num):
        errors.append(
            f"❌ SUBPLAN missing: SUBPLAN_{feature}_{achievement_num.replace('.', '')}.md"
        )

    # Check EXECUTION_TASK
    if not check_execution_task_exists(feature, achievement_num):
        errors.append(
            f"❌ EXECUTION_TASK missing: EXECUTION_TASK_{feature}_{achievement_num.replace('.', '')}_*.md"
        )

    # Check deliverables
    missing_deliverables = check_deliverables_exist(achievement)
    if missing_deliverables:
        for deliverable in missing_deliverables:
            errors.append(f"❌ Deliverable missing: {deliverable}")

    # Build message
    if errors:
        message = "❌ ACHIEVEMENT NOT PROPERLY COMPLETED - BLOCKING MARKING COMPLETE\n\n"
        message += "Issues Found:\n"
        message += "\n".join(errors)
        message += "\n\n📋 Fix Prompt:\n\n"
        message += "To fix these issues:\n"

        if not check_subplan_exists(feature, achievement_num):
            message += (
                f"1. Create SUBPLAN: SUBPLAN_{feature}_{achievement_num.replace('.', '')}.md\n"
            )
        if not check_execution_task_exists(feature, achievement_num):
            message += f"2. Create EXECUTION_TASK: EXECUTION_TASK_{feature}_{achievement_num.replace('.', '')}_01.md\n"
        if missing_deliverables:
            message += "3. Create missing deliverables:\n"
            for deliverable in missing_deliverables:
                message += f"   - {deliverable}\n"

        message += "\nAfter fixing, run validation again:\n"
        message += f"  python LLM/scripts/validate_achievement_completion.py @{plan_path.name} --achievement {achievement_num}\n"

        return False, message

    # Valid
    message = f"✅ Achievement {achievement_num} properly completed\n\n"
    message += "Checks passed:\n"
    message += f"✓ SUBPLAN exists\n"
    message += f"✓ EXECUTION_TASK exists\n"
    if achievement.get("deliverables"):
        message += f"✓ Deliverables exist\n"
    message += "\nSafe to mark achievement complete!"

    return True, message


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate achievement completion before marking complete",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python LLM/scripts/validate_achievement_completion.py @PLAN_FEATURE.md --achievement 1.1
  python LLM/scripts/validate_achievement_completion.py PLAN_FEATURE.md --achievement 2.3

Checks:
  - SUBPLAN exists for achievement
  - EXECUTION_TASK exists for achievement
  - Deliverables from achievement exist

Exit Codes:
  0 = Achievement properly completed (OK to mark complete)
  1 = Issues found (MUST fix before marking complete)
        """,
    )

    parser.add_argument("plan_file", help="PLAN file (e.g., @PLAN_FEATURE.md or PLAN_FEATURE.md)")

    parser.add_argument("--achievement", required=True, help="Achievement number (e.g., 1.1, 2.3)")

    args = parser.parse_args()

    try:
        # Clean file path
        plan_path = Path(args.plan_file.replace("@", ""))

        # Validate
        pass_check, message = validate_achievement(plan_path, args.achievement)

        # Print message
        print(message)

        # Exit code
        sys.exit(0 if pass_check else 1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
