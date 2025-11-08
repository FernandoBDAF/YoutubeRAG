#!/usr/bin/env python3
"""
Validate PLAN Completion - Blocking Validation Script

Validates that all achievements in a PLAN are complete.
Checks: SUBPLAN exists, EXECUTION_TASK exists, deliverables exist (if specified).

Usage:
    python LLM/scripts/validation/validate_plan_completion.py @PLAN_FILE.md

Exit Codes:
    0 = PLAN complete (all achievements done)
    1 = PLAN incomplete (some achievements pending)
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def extract_archive_location(plan_path: Path) -> Optional[str]:
    """Extract archive location from PLAN file."""
    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Look for "Archive Location" section
        patterns = [
            r"\*\*Archive Location\*\*:\s*`([^`]+)`",
            r"Archive Location[:\s]+`([^`]+)`",
            r"Archive Location[:\s]+([^\n]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Normalize path
                if location.startswith("./"):
                    location = location[2:]
                if location.endswith("/"):
                    location = location[:-1]
                return location
        
        return None
    except Exception as e:
        print(f"❌ Error reading PLAN file: {e}", file=sys.stderr)
        return None


def extract_achievements(plan_path: Path) -> List[str]:
    """Extract all achievement numbers from PLAN file."""
    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find all achievement numbers (e.g., "Achievement 1.1", "Achievement 2.3")
        pattern = r"\*\*Achievement\s+(\d+\.\d+)\*\*"
        matches = re.findall(pattern, content)
        
        # Return unique achievement numbers, sorted
        achievements = sorted(set(matches), key=lambda x: tuple(map(int, x.split('.'))))
        return achievements
    except Exception as e:
        print(f"❌ Error parsing PLAN file: {e}", file=sys.stderr)
        return []


def check_subplan_exists(feature_name: str, achievement_num: str, archive_location: Optional[str]) -> bool:
    """Check if SUBPLAN exists in root or archive."""
    subplan_num = achievement_num.replace(".", "")
    subplan_file = Path(f"SUBPLAN_{feature_name}_{subplan_num}.md")
    
    # Check root directory
    if subplan_file.exists():
        return True
    
    # Check archive directory
    if archive_location:
        archive_path = Path(archive_location)
        archive_subplans = archive_path / "subplans"
        if archive_subplans.exists():
            archived_subplan = archive_subplans / subplan_file.name
            if archived_subplan.exists():
                return True
    
    return False


def check_execution_task_exists(feature_name: str, achievement_num: str, archive_location: Optional[str]) -> bool:
    """Check if EXECUTION_TASK exists in root or archive."""
    subplan_num = achievement_num.replace(".", "")
    execution_pattern = f"EXECUTION_TASK_{feature_name}_{subplan_num}_*.md"
    
    # Check root directory
    execution_files = list(Path(".").glob(execution_pattern))
    if execution_files:
        return True
    
    # Check archive directory
    if archive_location:
        archive_path = Path(archive_location)
        archive_execution = archive_path / "execution"
        if archive_execution.exists():
            archived_execution = list(archive_execution.glob(execution_pattern))
            if archived_execution:
                return True
    
    return False


def check_achievement_completion(
    feature_name: str, achievement_num: str, archive_location: Optional[str]
) -> Tuple[bool, List[str]]:
    """Check if achievement is complete.
    
    Returns:
        (is_complete, issues) - is_complete=True if complete, False if issues found
    """
    issues = []
    
    # Check SUBPLAN
    if not check_subplan_exists(feature_name, achievement_num, archive_location):
        issues.append(f"SUBPLAN missing: SUBPLAN_{feature_name}_{achievement_num.replace('.', '')}.md")
    
    # Check EXECUTION_TASK
    if not check_execution_task_exists(feature_name, achievement_num, archive_location):
        issues.append(f"EXECUTION_TASK missing: EXECUTION_TASK_{feature_name}_{achievement_num.replace('.', '')}_*.md")
    
    return len(issues) == 0, issues


def validate_plan_completion(plan_path: Path) -> Tuple[bool, str]:
    """Validate PLAN completion.
    
    Returns:
        (is_complete, message) - is_complete=True if all achievements complete, False otherwise
    """
    if not plan_path.exists():
        return False, f"❌ PLAN file not found: {plan_path}"
    
    # Extract feature name
    feature_name = plan_path.stem.replace("PLAN_", "")
    
    # Extract achievements
    achievements = extract_achievements(plan_path)
    
    if not achievements:
        return False, "❌ No achievements found in PLAN. Cannot validate completion."
    
    # Extract archive location
    archive_location = extract_archive_location(plan_path)
    
    # Check each achievement
    completed = []
    pending = []
    
    for ach_num in achievements:
        is_complete, issues = check_achievement_completion(feature_name, ach_num, archive_location)
        if is_complete:
            completed.append(ach_num)
        else:
            pending.append((ach_num, issues))
    
    # Calculate completion percentage
    total = len(achievements)
    completed_count = len(completed)
    percentage = (completed_count / total * 100) if total > 0 else 0
    
    # Build report
    if len(pending) == 0:
        message = f"✅ PLAN Complete: {completed_count}/{total} achievements ({percentage:.0f}%)\n\n"
        message += "All achievements are complete. Ready for END_POINT protocol."
        return True, message
    
    # Incomplete PLAN
    message = f"❌ PLAN Incomplete: {completed_count}/{total} achievements ({percentage:.0f}%)\n\n"
    message += "Pending Achievements:\n"
    for ach_num, issues in pending:
        message += f"\n  Achievement {ach_num}:\n"
        for issue in issues:
            message += f"    - {issue}\n"
    
    message += f"\n📋 Fix: Complete pending achievements before marking PLAN complete."
    
    return False, message


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate PLAN completion (all achievements done)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python LLM/scripts/validation/validate_plan_completion.py @PLAN_FEATURE.md
  python LLM/scripts/validation/validate_plan_completion.py PLAN_FEATURE.md

Checks:
  - SUBPLAN exists for each achievement (root or archive)
  - EXECUTION_TASK exists for each achievement (root or archive)
  - Reports completion percentage
  - Identifies pending achievements

Exit Codes:
  0 = PLAN complete (all achievements done)
  1 = PLAN incomplete (some achievements pending)
        """,
    )
    
    parser.add_argument("plan_file", help="PLAN file to validate (e.g., PLAN_FEATURE.md)")
    
    args = parser.parse_args()
    
    plan_path = Path(args.plan_file.replace("@", ""))
    
    is_complete, message = validate_plan_completion(plan_path)
    
    print(message)
    
    sys.exit(0 if is_complete else 1)


if __name__ == "__main__":
    main()


