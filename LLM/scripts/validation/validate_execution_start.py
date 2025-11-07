#!/usr/bin/env python3
"""
Validate Execution Start - Blocking Validation Script

Validates prerequisites before starting EXECUTION_TASK.
Checks: SUBPLAN exists, parent PLAN exists, archive location exists.

Usage:
    python LLM/scripts/validate_execution_start.py @EXECUTION_TASK_FILE.md

Exit Codes:
    0 = Prerequisites met (OK to start execution)
    1 = Prerequisites missing (MUST fix before starting)
"""

import argparse
import re
import sys
from pathlib import Path


def extract_feature_from_file(file_path: Path) -> str:
    """Extract feature name from EXECUTION_TASK filename."""
    # Pattern: EXECUTION_TASK_FEATURE_SUBPLAN_EXECUTION.md
    match = re.match(r"EXECUTION_TASK_([A-Z0-9-]+)_(\d+)_(\d+)\.md", file_path.name)
    if match:
        return match.group(1)
    raise ValueError(f"Could not extract feature from filename: {file_path.name}")


def check_subplan_exists(file_path: Path) -> bool:
    """Check if parent SUBPLAN exists."""
    # Extract feature and subplan number
    match = re.match(r"EXECUTION_TASK_([A-Z0-9-]+)_(\d+)_(\d+)\.md", file_path.name)
    if match:
        feature = match.group(1)
        subplan_num = match.group(2)
        subplan_file = Path(f"SUBPLAN_{feature}_{subplan_num}.md")
        return subplan_file.exists()
    return False


def check_parent_plan_exists(file_path: Path) -> bool:
    """Check if parent PLAN exists."""
    feature = extract_feature_from_file(file_path)
    plan_file = Path(f"PLAN_{feature}.md")
    return plan_file.exists()


def get_archive_location(plan_path: Path) -> Path:
    """Extract archive location from PLAN file."""
    with open(plan_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Look for "Archive Location" section
    match = re.search(r"Archive Location[:\s]+\*\*[:\s]*`?([^`\n]+)`?", content, re.IGNORECASE)
    if match:
        location = match.group(1).strip().strip("\"'")
        return Path(location)

    # Fallback: Try to infer
    feature = plan_path.stem.replace("PLAN_", "").lower().replace("_", "-")
    return Path(f"./{feature}-archive/")


def check_archive_location_exists(plan_path: Path) -> bool:
    """Check if archive location exists."""
    archive_location = get_archive_location(plan_path)
    return archive_location.exists()


def validate_execution_start(file_path: Path) -> tuple[bool, str]:
    """
    Validate prerequisites before starting EXECUTION_TASK.

    Returns:
        (pass, message) - pass=True if valid, False if issues found
    """
    if not file_path.exists():
        return False, f"❌ Error: File not found: {file_path}"

    # Check prerequisites
    errors = []

    # Check SUBPLAN
    if not check_subplan_exists(file_path):
        feature = extract_feature_from_file(file_path)
        match = re.match(r"EXECUTION_TASK_([A-Z0-9-]+)_(\d+)_(\d+)\.md", file_path.name)
        subplan_num = match.group(2) if match else "XX"
        errors.append(f"❌ SUBPLAN missing: SUBPLAN_{feature}_{subplan_num}.md")

    # Check parent PLAN
    feature = extract_feature_from_file(file_path)
    plan_path = Path(f"PLAN_{feature}.md")
    if not check_parent_plan_exists(file_path):
        errors.append(f"❌ Parent PLAN missing: PLAN_{feature}.md")
    elif not check_archive_location_exists(plan_path):
        archive_location = get_archive_location(plan_path)
        errors.append(f"❌ Archive location missing: {archive_location}")

    # Build message
    if errors:
        message = "❌ PREREQUISITES MISSING - BLOCKING EXECUTION START\n\n"
        message += "Issues Found:\n"
        message += "\n".join(errors)
        message += "\n\n📋 Fix Prompt:\n\n"
        message += "To fix these issues:\n"

        if not check_subplan_exists(file_path):
            match = re.match(r"EXECUTION_TASK_([A-Z0-9-]+)_(\d+)_(\d+)\.md", file_path.name)
            if match:
                feature = match.group(1)
                subplan_num = match.group(2)
                message += f"1. Create SUBPLAN: SUBPLAN_{feature}_{subplan_num}.md\n"
                message += "   - See: LLM/templates/SUBPLAN-TEMPLATE.md\n"

        if not check_parent_plan_exists(file_path):
            message += f"2. Create parent PLAN: PLAN_{feature}.md\n"
            message += "   - See: LLM/templates/PLAN-TEMPLATE.md\n"

        plan_path = Path(f"PLAN_{feature}.md")
        if plan_path.exists() and not check_archive_location_exists(plan_path):
            archive_location = get_archive_location(plan_path)
            message += f"3. Create archive location: {archive_location}\n"
            message += "   - Run: mkdir -p {archive_location}/{{subplans,execution}}\n"
            message += "   - See: LLM/protocols/IMPLEMENTATION_START_POINT.md\n"

        message += "\nAfter fixing, run validation again:\n"
        message += f"  python LLM/scripts/validate_execution_start.py @{file_path.name}\n"

        return False, message

    # Valid
    message = "✅ Prerequisites met - OK to start execution\n\n"
    message += "Checks passed:\n"
    message += "✓ SUBPLAN exists\n"
    message += "✓ Parent PLAN exists\n"
    message += "✓ Archive location exists\n"
    message += "\nSafe to start EXECUTION_TASK!"

    return True, message


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate prerequisites before starting EXECUTION_TASK",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python LLM/scripts/validate_execution_start.py @EXECUTION_TASK_FEATURE_01_01.md
  python LLM/scripts/validate_execution_start.py EXECUTION_TASK_FEATURE_01_01.md

Checks:
  - SUBPLAN exists
  - Parent PLAN exists
  - Archive location exists

Exit Codes:
  0 = Prerequisites met (OK to start execution)
  1 = Prerequisites missing (MUST fix before starting)
        """,
    )

    parser.add_argument(
        "execution_task_file", help="EXECUTION_TASK file (e.g., @EXECUTION_TASK_FEATURE_01_01.md)"
    )

    args = parser.parse_args()

    try:
        # Clean file path
        file_path = Path(args.execution_task_file.replace("@", ""))

        # Validate
        pass_check, message = validate_execution_start(file_path)

        # Print message
        print(message)

        # Exit code
        sys.exit(0 if pass_check else 1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
