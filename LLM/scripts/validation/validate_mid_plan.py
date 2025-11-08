#!/usr/bin/env python3
"""
Validate Mid-Plan Compliance - Blocking Validation Script

Validates PLAN compliance at mid-point (or manual trigger).
Checks: Statistics accuracy, SUBPLAN registration, archive compliance.

Usage:
    python LLM/scripts/validate_mid_plan.py @PLAN_FILE.md

Exit Codes:
    0 = PLAN compliant (OK to continue)
    1 = Issues found (MUST fix before continuing)
"""

import argparse
import re
import sys
from pathlib import Path


def extract_statistics(plan_path: Path) -> dict:
    """Extract statistics from PLAN Subplan Tracking section."""
    with open(plan_path, "r", encoding="utf-8") as f:
        content = f.read()

    stats = {}

    # Extract SUBPLAN count
    match = re.search(r"\*\*SUBPLANs\*\*:\s*(\d+)\s+created", content)
    if match:
        stats["subplans_claimed"] = int(match.group(1))

    # Extract EXECUTION_TASK count
    match = re.search(r"\*\*EXECUTION_TASKs\*\*:\s*(\d+)\s+created", content)
    if match:
        stats["execution_tasks_claimed"] = int(match.group(1))

    return stats


def count_actual_subplans(plan_path: Path) -> int:
    """Count actual SUBPLAN files for this PLAN."""
    feature = plan_path.stem.replace("PLAN_", "")
    # Use exact pattern to avoid matching other plans
    subplan_pattern = f"SUBPLAN_{feature}_*.md"
    subplan_files = list(Path(".").glob(subplan_pattern))
    # Also check archive
    archive_location = get_archive_location(plan_path)
    if archive_location.exists():
        archived = list((archive_location / "subplans").glob(f"SUBPLAN_{feature}_*.md"))
        subplan_files.extend(archived)
    # Filter to ensure exact match (handle edge cases)
    exact_matches = [f for f in subplan_files if f.stem.startswith(f"SUBPLAN_{feature}_")]
    return len(exact_matches)


def count_actual_execution_tasks(plan_path: Path) -> int:
    """Count actual EXECUTION_TASK files for this PLAN."""
    feature = plan_path.stem.replace("PLAN_", "")
    execution_pattern = f"EXECUTION_TASK_{feature}_*.md"
    execution_files = list(Path(".").glob(execution_pattern))
    # Also check archive
    archive_location = get_archive_location(plan_path)
    if archive_location.exists():
        archived = list((archive_location / "execution").glob(f"EXECUTION_TASK_{feature}_*.md"))
        execution_files.extend(archived)
    # Filter to ensure exact match (handle edge cases)
    exact_matches = [f for f in execution_files if f.stem.startswith(f"EXECUTION_TASK_{feature}_")]
    return len(exact_matches)


def get_archive_location(plan_path: Path) -> Path:
    """Extract archive location from PLAN file."""
    with open(plan_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Look for "Archive Location" section
    match = re.search(r"Archive Location[:\s]+\*\*[:\s]*`?([^`\n]+)`?", content, re.IGNORECASE)
    if match:
        location = match.group(1).strip().strip("\"'")
        return Path(location)

    # Fallback
    feature = plan_path.stem.replace("PLAN_", "").lower().replace("_", "-")
    return Path(f"./{feature}-archive/")


def check_subplan_registration(plan_path: Path) -> list:
    """Check if all SUBPLANs are registered in PLAN."""
    feature = plan_path.stem.replace("PLAN_", "")

    # Find all SUBPLAN files
    subplan_pattern = f"SUBPLAN_{feature}_*.md"
    subplan_files = list(Path(".").glob(subplan_pattern))
    archive_location = get_archive_location(plan_path)
    if archive_location.exists():
        archived = list((archive_location / "subplans").glob(f"SUBPLAN_{feature}_*.md"))
        subplan_files.extend(archived)

    # Read PLAN to find registered SUBPLANs
    with open(plan_path, "r", encoding="utf-8") as f:
        content = f.read()

    registered = []
    for subplan_file in subplan_files:
        subplan_num = subplan_file.stem.split("_")[-1]
        if f"SUBPLAN_{feature}_{subplan_num}" in content:
            registered.append(subplan_file.name)

    # Find unregistered
    unregistered = []
    for subplan_file in subplan_files:
        if subplan_file.name not in registered:
            unregistered.append(subplan_file.name)

    return unregistered


def validate_mid_plan(plan_path: Path) -> tuple[bool, str]:
    """
    Validate PLAN compliance at mid-point.

    Returns:
        (pass, message) - pass=True if valid, False if issues found
    """
    if not plan_path.exists():
        return False, f"❌ Error: PLAN file not found: {plan_path}"

    errors = []
    warnings = []

    # Check statistics accuracy
    stats = extract_statistics(plan_path)
    actual_subplans = count_actual_subplans(plan_path)
    actual_execution_tasks = count_actual_execution_tasks(plan_path)

    if "subplans_claimed" in stats:
        if stats["subplans_claimed"] != actual_subplans:
            errors.append(
                f"❌ SUBPLAN count mismatch: Claimed {stats['subplans_claimed']}, Actual {actual_subplans}"
            )

    if "execution_tasks_claimed" in stats:
        if stats["execution_tasks_claimed"] != actual_execution_tasks:
            errors.append(
                f"❌ EXECUTION_TASK count mismatch: Claimed {stats['execution_tasks_claimed']}, Actual {actual_execution_tasks}"
            )

    # Check SUBPLAN registration
    unregistered = check_subplan_registration(plan_path)
    if unregistered:
        warnings.append(f"⚠️  Unregistered SUBPLANs: {', '.join(unregistered)}")

    # Check archive compliance
    archive_location = get_archive_location(plan_path)
    if not archive_location.exists():
        errors.append(f"❌ Archive location missing: {archive_location}")

    # Build message
    if errors:
        message = "❌ PLAN COMPLIANCE ISSUES FOUND - BLOCKING CONTINUATION\n\n"
        message += "Issues Found:\n"
        message += "\n".join(errors)
        if warnings:
            message += "\n\nWarnings:\n"
            message += "\n".join(warnings)

        message += "\n\n📋 Fix Prompt:\n\n"
        message += "To fix these issues:\n"

        if "subplans_claimed" in stats and stats["subplans_claimed"] != actual_subplans:
            message += f"1. Update PLAN statistics: SUBPLANs: {actual_subplans} (not {stats['subplans_claimed']})\n"
        if (
            "execution_tasks_claimed" in stats
            and stats["execution_tasks_claimed"] != actual_execution_tasks
        ):
            message += f"2. Update PLAN statistics: EXECUTION_TASKs: {actual_execution_tasks} (not {stats['execution_tasks_claimed']})\n"
        if unregistered:
            message += "3. Register SUBPLANs in PLAN 'Subplan Tracking' section:\n"
            for subplan in unregistered:
                message += f"   - {subplan}\n"
        if not archive_location.exists():
            message += f"4. Create archive location: {archive_location}\n"
            message += "   - Run: mkdir -p {archive_location}/{{subplans,execution}}\n"

        message += "\nAfter fixing, run validation again:\n"
        message += f"  python LLM/scripts/validate_mid_plan.py @{plan_path.name}\n"

        return False, message

    # Valid (warnings are OK)
    message = "✅ PLAN compliance validated\n\n"
    message += "Checks passed:\n"
    message += f"✓ Statistics accurate (SUBPLANs: {actual_subplans}, EXECUTION_TASKs: {actual_execution_tasks})\n"
    message += "✓ Archive location exists\n"
    if warnings:
        message += "\nWarnings (non-blocking):\n"
        message += "\n".join(warnings)
        message += "\n\n💡 Consider fixing warnings for better compliance."
    else:
        message += "✓ All SUBPLANs registered\n"

    message += "\nSafe to continue PLAN execution!"

    return True, message


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate PLAN compliance at mid-point",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python LLM/scripts/validate_mid_plan.py @PLAN_FEATURE.md
  python LLM/scripts/validate_mid_plan.py PLAN_FEATURE.md

Checks:
  - Statistics accuracy (claimed vs actual)
  - SUBPLAN registration
  - Archive location exists

Exit Codes:
  0 = PLAN compliant (OK to continue)
  1 = Issues found (MUST fix before continuing)
        """,
    )

    parser.add_argument("plan_file", help="PLAN file (e.g., @PLAN_FEATURE.md or PLAN_FEATURE.md)")

    parser.add_argument(
        "--generate-fix-prompt",
        action="store_true",
        help="Generate fix prompt instead of blocking (for use in generate_verify_prompt.py)",
    )

    args = parser.parse_args()

    try:
        # Clean file path
        plan_path = Path(args.plan_file.replace("@", ""))

        # Validate
        pass_check, message = validate_mid_plan(plan_path)

        # Print message
        print(message)

        # If --generate-fix-prompt, always exit 0 (prompt generation, not blocking)
        if args.generate_fix_prompt:
            sys.exit(0)

        # Exit code
        sys.exit(0 if pass_check else 1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
