#!/usr/bin/env python3
"""
Validate Achievement Completion - Blocking Validation Script

Validates that an achievement is properly completed before marking it complete.
Checks: SUBPLAN exists, EXECUTION_TASK exists (all if multiple), deliverables exist,
synthesis section present (if multiple EXECUTIONs).

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
from typing import List, Optional, Tuple


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


def find_subplan_path(feature: str, achievement_num: str) -> Optional[Path]:
    """Find SUBPLAN file for achievement (nested structure + archive)."""
    subplan_num = achievement_num.replace(".", "")
    subplan_name = f"SUBPLAN_{feature}_{subplan_num}.md"

    # Check nested structure: work-space/plans/PLAN_NAME/subplans/
    plan_folder = Path(f"work-space/plans/{feature}")
    if plan_folder.exists():
        nested_subplan = plan_folder / "subplans" / subplan_name
        if nested_subplan.exists():
            return nested_subplan

    # Check archive location from PLAN
    plan_path = Path(f"work-space/plans/{feature}/PLAN_{feature}.md")
    if not plan_path.exists():
        plan_path = Path(f"PLAN_{feature}.md")

    if plan_path.exists():
        # Extract archive location from PLAN
        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r"\*\*Archive Location\*\*:\s*(.+?)(?:\n|$)", content)
            if match:
                archive_str = match.group(1).strip()
                if archive_str.startswith("`"):
                    archive_str = archive_str.strip("`")
                archive_path = Path(archive_str)
                archive_subplan = archive_path / "subplans" / subplan_name
                if archive_subplan.exists():
                    return archive_subplan

    return None


def check_subplan_exists(feature: str, achievement_num: str) -> bool:
    """Check if SUBPLAN file exists for achievement."""
    return find_subplan_path(feature, achievement_num) is not None


def find_execution_tasks(feature: str, achievement_num: str) -> List[Path]:
    """Find all EXECUTION_TASK files for achievement (nested structure + archive)."""
    subplan_num = achievement_num.replace(".", "")
    execution_pattern = f"EXECUTION_TASK_{feature}_{subplan_num}_*.md"
    execution_files = []

    # Check nested structure: work-space/plans/PLAN_NAME/execution/
    plan_folder = Path(f"work-space/plans/{feature}")
    if plan_folder.exists():
        nested_execution_dir = plan_folder / "execution"
        if nested_execution_dir.exists():
            execution_files.extend(nested_execution_dir.glob(execution_pattern))

    # Check archive (if we can find archive location)
    plan_path = Path(f"work-space/plans/{feature}/PLAN_{feature}.md")
    if not plan_path.exists():
        plan_path = Path(f"PLAN_{feature}.md")

    if plan_path.exists():
        # Extract archive location from PLAN
        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r"\*\*Archive Location\*\*:\s*(.+?)(?:\n|$)", content)
            if match:
                archive_str = match.group(1).strip()
                if archive_str.startswith("`"):
                    archive_str = archive_str.strip("`")
                archive_path = Path(archive_str)
                archive_execution = archive_path / "execution"
                if archive_execution.exists():
                    execution_files.extend(archive_execution.glob(execution_pattern))

    return execution_files


def check_execution_task_exists(feature: str, achievement_num: str) -> bool:
    """Check if EXECUTION_TASK file exists for achievement."""
    return len(find_execution_tasks(feature, achievement_num)) > 0


def check_execution_complete(execution_path: Path) -> bool:
    """Check if EXECUTION_TASK is marked complete."""
    try:
        with open(execution_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Check for completion markers
        if re.search(r"Status.*Complete|✅.*Complete|Complete.*✅", content, re.IGNORECASE):
            return True
        return False
    except Exception:
        return False


def parse_subplan_for_executions(subplan_path: Path) -> dict:
    """Parse SUBPLAN to detect execution count and synthesis section."""
    try:
        with open(subplan_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return {"execution_count": "Single", "synthesis_section": False}

    info = {
        "execution_count": "Single",  # Default
        "synthesis_section": False,
    }

    # Check for Execution Strategy section
    execution_strategy_match = re.search(
        r"## 🔄 Execution Strategy.*?\n(.*?)(?=\n## |$)",
        content,
        re.DOTALL,
    )
    if execution_strategy_match:
        strategy_text = execution_strategy_match.group(1)
        if "Multiple" in strategy_text:
            info["execution_count"] = "Multiple"

    # Check for Execution Results Synthesis section
    if re.search(r"## 📊 Execution Results Synthesis", content):
        info["synthesis_section"] = True

    return info


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

    # Check EXECUTION_TASK(s) - support multiple
    execution_files = find_execution_tasks(feature, achievement_num)
    if len(execution_files) == 0:
        errors.append(
            f"❌ EXECUTION_TASK missing: EXECUTION_TASK_{feature}_{achievement_num.replace('.', '')}_*.md"
        )
    else:
        # Check if SUBPLAN has multiple EXECUTIONs
        subplan_path = find_subplan_path(feature, achievement_num)
        if subplan_path:
            subplan_info = parse_subplan_for_executions(subplan_path)

            # If multiple EXECUTIONs, check all are complete
            if subplan_info["execution_count"] == "Multiple":
                incomplete_executions = []
                for exec_file in execution_files:
                    if not check_execution_complete(exec_file):
                        incomplete_executions.append(exec_file.name)

                if incomplete_executions:
                    errors.append(
                        f"❌ Not all EXECUTIONs complete (SUBPLAN has multiple EXECUTIONs):\n"
                        f"   → Incomplete: {', '.join(incomplete_executions)}\n"
                        f"   → All EXECUTIONs must be complete before marking achievement done"
                    )

                # Check synthesis section present
                if not subplan_info["synthesis_section"]:
                    errors.append(
                        f"❌ Synthesis section missing (SUBPLAN has multiple EXECUTIONs):\n"
                        f"   → SUBPLAN must have 'Execution Results Synthesis' section when multiple EXECUTIONs\n"
                        f"   → Add section to synthesize results from all EXECUTIONs"
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
    execution_count = len(execution_files)
    if execution_count == 1:
        message += f"✓ EXECUTION_TASK exists\n"
    else:
        message += f"✓ All {execution_count} EXECUTION_TASKs exist and complete\n"
        subplan_path = find_subplan_path(feature, achievement_num)
        if subplan_path:
            subplan_info = parse_subplan_for_executions(subplan_path)
            if subplan_info["execution_count"] == "Multiple":
                message += f"✓ Synthesis section present\n"
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
  - EXECUTION_TASK exists for achievement (all if multiple)
  - All EXECUTIONs complete (if SUBPLAN has multiple)
  - Synthesis section present (if multiple EXECUTIONs)
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
