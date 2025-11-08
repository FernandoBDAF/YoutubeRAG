#!/usr/bin/env python3
"""
Validate SUBPLAN Executions - Blocking Validation Script

Validates that SUBPLANs with multiple EXECUTIONs are properly structured and complete.
Checks: At least 1 EXECUTION exists, all planned EXECUTIONs exist, active EXECUTIONs registered,
SUBPLAN not complete until all EXECUTIONs complete, parallel execution consistency.

Usage:
    python LLM/scripts/validation/validate_subplan_executions.py @SUBPLAN_FILE.md
    python LLM/scripts/validation/validate_subplan_executions.py SUBPLAN_FILE.md

Exit Codes:
    0 = SUBPLAN executions valid (OK)
    1 = Issues found (MUST fix before continuing)
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def extract_feature_and_subplan_num(subplan_path: Path) -> Tuple[Optional[str], Optional[str]]:
    """Extract feature name and subplan number from SUBPLAN filename."""
    match = re.match(r"SUBPLAN_([A-Z0-9-]+)_(\d+)\.md", subplan_path.name)
    if not match:
        return None, None
    return match.group(1), match.group(2)


def find_execution_tasks(feature: str, subplan_num: str, archive_location: Optional[Path] = None, plan_folder: Optional[Path] = None) -> List[Path]:
    """Find all EXECUTION_TASK files for a SUBPLAN (nested structure + archive)."""
    execution_pattern = f"EXECUTION_TASK_{feature}_{subplan_num}_*.md"
    execution_files = []
    
    # Check nested structure: work-space/plans/PLAN_NAME/execution/
    if plan_folder and plan_folder.exists():
        nested_execution_dir = plan_folder / "execution"
        if nested_execution_dir.exists():
            execution_files.extend(nested_execution_dir.glob(execution_pattern))
    else:
        # Try to construct plan folder path
        plan_folder = Path(f"work-space/plans/{feature}")
        if plan_folder.exists():
            nested_execution_dir = plan_folder / "execution"
            if nested_execution_dir.exists():
                execution_files.extend(nested_execution_dir.glob(execution_pattern))
    
    # Check archive/execution/
    if archive_location:
        archive_execution = archive_location / "execution"
        if archive_execution.exists():
            execution_files.extend(archive_execution.glob(execution_pattern))
    
    return execution_files


def get_archive_location(subplan_path: Path) -> Optional[Path]:
    """Extract archive location from parent PLAN."""
    feature, _ = extract_feature_and_subplan_num(subplan_path)
    if not feature:
        return None
    
    plan_path = Path(f"work-space/plans/PLAN_{feature}.md")
    if not plan_path.exists():
        plan_path = Path(f"PLAN_{feature}.md")
    
    if not plan_path.exists():
        return None
    
    # Extract archive location from PLAN
    with open(plan_path, "r", encoding="utf-8") as f:
        content = f.read()
        match = re.search(r"\*\*Archive Location\*\*:\s*(.+?)(?:\n|$)", content)
        if match:
            archive_str = match.group(1).strip()
            if archive_str.startswith("`"):
                archive_str = archive_str.strip("`")
            return Path(archive_str)
    
    return None


def parse_subplan(subplan_path: Path) -> Dict:
    """Parse SUBPLAN file to extract execution information."""
    with open(subplan_path, "r", encoding="utf-8") as f:
        content = f.read()
        lines = content.split("\n")
    
    info = {
        "execution_count": "Single",  # Default
        "parallelization": False,
        "planned_executions": [],
        "active_executions": [],
        "is_complete": False,
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
        if "[PARALLEL]" in strategy_text or "Parallel" in strategy_text:
            info["parallelization"] = True
    
    # Check for Planned Executions table
    planned_executions_match = re.search(
        r"## 🔀 Planned Executions.*?\n\|.*?\n\|.*?\n(.*?)(?=\n## |$)",
        content,
        re.DOTALL,
    )
    if planned_executions_match:
        table_text = planned_executions_match.group(1)
        # Extract EXECUTION names from table
        execution_matches = re.findall(
            r"EXECUTION_TASK_([A-Z0-9-]+)_(\d+)_(\d+)",
            table_text,
        )
        for match in execution_matches:
            info["planned_executions"].append(f"EXECUTION_TASK_{match[0]}_{match[1]}_{match[2]}")
    
    # Check for Active EXECUTION_TASKs table
    active_executions_match = re.search(
        r"## 🔄 Active EXECUTION_TASKs.*?\n\|.*?\n\|.*?\n(.*?)(?=\n## |$)",
        content,
        re.DOTALL,
    )
    if active_executions_match:
        table_text = active_executions_match.group(1)
        # Extract EXECUTION names and status from table
        execution_matches = re.findall(
            r"EXECUTION_TASK_([A-Z0-9-]+)_(\d+)_(\d+).*?\|.*?\|.*?\|.*?\|.*?\|\s*([^\|]+)",
            table_text,
        )
        for match in execution_matches:
            exec_name = f"EXECUTION_TASK_{match[0]}_{match[1]}_{match[2]}"
            status = match[3].strip() if len(match) > 3 else "Unknown"
            info["active_executions"].append({"name": exec_name, "status": status})
    
    # Check if SUBPLAN is marked complete
    if re.search(r"Status.*Complete|✅.*Complete|Complete.*✅", content, re.IGNORECASE):
        info["is_complete"] = True
    
    # Check for Execution Results Synthesis section
    if re.search(r"## 📊 Execution Results Synthesis", content):
        info["synthesis_section"] = True
    
    return info


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


def validate_subplan_executions(subplan_path: Path) -> Tuple[bool, str]:
    """
    Validate SUBPLAN executions.

    Returns:
        (pass, message) - pass=True if valid, False if issues found
    """
    if not subplan_path.exists():
        return False, f"❌ Error: SUBPLAN file not found: {subplan_path}"
    
    feature, subplan_num = extract_feature_and_subplan_num(subplan_path)
    if not feature or not subplan_num:
        return False, f"❌ Error: Invalid SUBPLAN filename format: {subplan_path.name}"
    
    # Parse SUBPLAN
    subplan_info = parse_subplan(subplan_path)
    archive_location = get_archive_location(subplan_path)
    
    # Determine plan folder from SUBPLAN path
    # SUBPLAN is in work-space/plans/PLAN_NAME/subplans/
    plan_folder = subplan_path.parent.parent
    
    # Find all EXECUTION_TASK files
    execution_files = find_execution_tasks(feature, subplan_num, archive_location, plan_folder)
    execution_names = [f.name for f in execution_files]
    
    errors = []
    warnings = []
    
    # Check 1: At least 1 EXECUTION_TASK exists
    if len(execution_files) == 0:
        errors.append(
            f"❌ No EXECUTION_TASK files found for SUBPLAN\n"
            f"   → Expected: EXECUTION_TASK_{feature}_{subplan_num}_*.md\n"
            f"   → Checked: work-space/execution/ and archive/"
        )
    
    # Check 2: All planned EXECUTIONs exist (if "Planned Executions" section present)
    if subplan_info["execution_count"] == "Multiple" and subplan_info["planned_executions"]:
        for planned_exec in subplan_info["planned_executions"]:
            # Extract execution number from planned name
            match = re.search(r"_(\d+)\.md$", planned_exec)
            if match:
                exec_num = match.group(1)
                exec_pattern = f"EXECUTION_TASK_{feature}_{subplan_num}_{exec_num}.md"
                found = any(f.name == exec_pattern for f in execution_files)
                if not found:
                    errors.append(
                        f"❌ Planned EXECUTION not found: {exec_pattern}\n"
                        f"   → Listed in 'Planned Executions' section but file doesn't exist"
                    )
    
    # Check 3: Active EXECUTIONs are registered in SUBPLAN
    if subplan_info["active_executions"]:
        for active_exec in subplan_info["active_executions"]:
            exec_name = active_exec["name"]
            # Extract execution number
            match = re.search(r"_(\d+)\.md$", exec_name)
            if match:
                exec_num = match.group(1)
                exec_pattern = f"EXECUTION_TASK_{feature}_{subplan_num}_{exec_num}.md"
                found = any(f.name == exec_pattern for f in execution_files)
                if not found:
                    errors.append(
                        f"❌ Active EXECUTION registered but file not found: {exec_pattern}\n"
                        f"   → Listed in 'Active EXECUTION_TASKs' table but file doesn't exist"
                    )
    
    # Check 4: SUBPLAN not marked complete until all EXECUTIONs complete
    if subplan_info["is_complete"]:
        incomplete_executions = []
        for exec_file in execution_files:
            if not check_execution_complete(exec_file):
                incomplete_executions.append(exec_file.name)
        
        if incomplete_executions:
            errors.append(
                f"❌ SUBPLAN marked complete but EXECUTIONs not complete:\n"
                f"   → Incomplete: {', '.join(incomplete_executions)}\n"
                f"   → SUBPLAN should not be marked complete until all EXECUTIONs are complete"
            )
    
    # Check 5: Parallel execution consistency (all marked [PARALLEL] complete together)
    if subplan_info["parallelization"] and subplan_info["execution_count"] == "Multiple":
        execution_statuses = []
        for exec_file in execution_files:
            is_complete = check_execution_complete(exec_file)
            execution_statuses.append((exec_file.name, is_complete))
        
        if len(execution_statuses) > 1:
            complete_count = sum(1 for _, is_complete in execution_statuses if is_complete)
            incomplete_count = len(execution_statuses) - complete_count
            
            if complete_count > 0 and incomplete_count > 0:
                warnings.append(
                    f"⚠️  Parallel execution inconsistency detected\n"
                    f"   → Complete: {complete_count}, Incomplete: {incomplete_count}\n"
                    f"   → Parallel EXECUTIONs should complete together (or all remain incomplete)"
                )
    
    # Build message
    if errors:
        message = "❌ SUBPLAN EXECUTION VALIDATION FAILED - BLOCKING\n\n"
        message += "Issues Found:\n"
        message += "\n".join(errors)
        if warnings:
            message += "\n\nWarnings:\n"
            message += "\n".join(warnings)
        message += "\n\n📋 Fix Prompt:\n\n"
        message += "To fix these issues:\n"
        message += "1. Review SUBPLAN structure (Execution Strategy, Planned Executions, Active EXECUTION_TASKs)\n"
        message += "2. Ensure all planned EXECUTIONs exist\n"
        message += "3. Ensure all active EXECUTIONs are registered\n"
        message += "4. Only mark SUBPLAN complete when all EXECUTIONs complete\n"
        message += "5. For parallel EXECUTIONs, ensure consistency\n"
        message += "\nAfter fixing, run validation again:\n"
        message += f"  python LLM/scripts/validation/validate_subplan_executions.py @{subplan_path.name}\n"
        return False, message
    
    if warnings:
        message = "⚠️  SUBPLAN EXECUTION VALIDATION PASSED WITH WARNINGS\n\n"
        message += "Warnings:\n"
        message += "\n".join(warnings)
        message += "\n\n✅ All critical checks passed, but review warnings above."
        return True, message
    
    # Valid
    message = f"✅ SUBPLAN execution validation passed\n\n"
    message += "Checks passed:\n"
    message += f"✓ At least 1 EXECUTION_TASK exists ({len(execution_files)} found)\n"
    if subplan_info["execution_count"] == "Multiple":
        message += f"✓ All planned EXECUTIONs exist\n"
        message += f"✓ Active EXECUTIONs registered\n"
    message += f"✓ Completion status consistent\n"
    if subplan_info["parallelization"]:
        message += f"✓ Parallel execution consistency validated\n"
    message += "\nSUBPLAN execution structure is valid!"
    
    return True, message


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate SUBPLAN executions (multi-execution workflow)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python LLM/scripts/validation/validate_subplan_executions.py @SUBPLAN_FEATURE_01.md
  python LLM/scripts/validation/validate_subplan_executions.py SUBPLAN_FEATURE_01.md

Checks:
  - At least 1 EXECUTION_TASK exists
  - All planned EXECUTIONs exist (if section present)
  - Active EXECUTIONs registered in SUBPLAN
  - SUBPLAN not complete until all EXECUTIONs complete
  - Parallel execution consistency

Exit Codes:
  0 = SUBPLAN executions valid (OK)
  1 = Issues found (MUST fix before continuing)
        """,
    )
    
    parser.add_argument(
        "subplan_file",
        help="SUBPLAN file (e.g., @SUBPLAN_FEATURE_01.md or SUBPLAN_FEATURE_01.md)",
    )
    
    args = parser.parse_args()
    
    try:
        # Clean file path
        subplan_path = Path(args.subplan_file.replace("@", ""))
        
        # Check nested structure first: work-space/plans/PLAN_NAME/subplans/
        if not subplan_path.exists():
            # Try to find in nested structure by searching all plan folders
            for plan_folder in Path("work-space/plans").glob("*/"):
                nested_subplan = plan_folder / "subplans" / subplan_path.name
                if nested_subplan.exists():
                    subplan_path = nested_subplan
                    break
        
        # Validate
        pass_check, message = validate_subplan_executions(subplan_path)
        
        # Print message
        print(message)
        
        # Exit code
        sys.exit(0 if pass_check else 1)
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

