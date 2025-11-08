#!/usr/bin/env python3
"""
Generate Completion Status Report for PLANs

Creates human-readable status report showing:
- Completion percentage (X/Y achievements)
- Achievement-by-achievement status
- Pending work list
- Ready for END_POINT indicator

Usage:
    python LLM/scripts/generation/generate_completion_status.py @PLAN_FEATURE.md
    python LLM/scripts/generation/generate_completion_status.py @PLAN_FEATURE.md --verbose
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple


def extract_archive_location(plan_path: Path) -> Optional[str]:
    """Extract archive location from PLAN file."""
    with open(plan_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Look for archive location in multiple places
    patterns = [
        r"\*\*Archive Location\*\*[:\s]+[`']?([^`'\n]+)[`']?",
        r"Archive Location[:\s]+[`']?([^`'\n]+)[`']?",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            # Clean up common formatting
            location = location.rstrip("*/`")
            return location
    
    return None


def parse_plan_achievements(plan_path: Path) -> List[Dict[str, str]]:
    """
    Parse PLAN file to extract all achievements.
    
    Returns list of dicts with keys: number, title
    """
    with open(plan_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    achievements = []
    
    # Pattern to match achievement definitions
    pattern = r"\*\*Achievement\s+(\d+\.\d+)\*\*[:\s]+(.+?)(?=\n\n|$)"
    
    for match in re.finditer(pattern, content, re.DOTALL):
        ach_num = match.group(1)
        ach_title = match.group(2).strip()
        
        # Clean title (take first line only)
        ach_title = ach_title.split("\n")[0].strip()
        
        achievements.append({
            "number": ach_num,
            "title": ach_title,
        })
    
    return achievements


def check_achievement_status(
    plan_path: Path, achievement: Dict[str, str], feature_name: str, archive_location: Optional[Path]
) -> bool:
    """
    Check if a single achievement is complete (SUBPLAN and EXECUTION_TASK exist).
    
    Returns True if complete, False otherwise.
    """
    ach_num = achievement["number"]
    subplan_num = ach_num.replace(".", "")
    subplan_name = f"SUBPLAN_{feature_name}_{subplan_num}.md"
    exec_task_name = f"EXECUTION_TASK_{feature_name}_{subplan_num}_01.md"
    
    # Check root directory
    if (Path(subplan_name).exists() or Path(exec_task_name).exists()):
        return True
    
    # Check archive location
    if archive_location and archive_location.exists():
        subplan_archive = archive_location / "subplans" / subplan_name
        exec_archive = archive_location / "execution" / exec_task_name
        
        if subplan_archive.exists() or exec_archive.exists():
            return True
    
    return False


def generate_completion_status(plan_path: Path, verbose: bool = False) -> Tuple[bool, str]:
    """
    Generate completion status report for PLAN.
    
    Args:
        plan_path: Path to PLAN file
        verbose: Include additional details in output
        
    Returns:
        Tuple of (is_complete, status_report)
    """
    # Extract feature name
    feature_name = plan_path.stem.replace("PLAN_", "")
    
    # Extract archive location
    archive_location_str = extract_archive_location(plan_path)
    archive_location = Path(archive_location_str) if archive_location_str else None
    
    # Parse achievements
    achievements = parse_plan_achievements(plan_path)
    
    if not achievements:
        return False, "❌ No achievements found in PLAN!"
    
    # Check status for each achievement
    achievement_status = []
    completed_count = 0
    
    for ach in achievements:
        is_complete = check_achievement_status(plan_path, ach, feature_name, archive_location)
        achievement_status.append({
            "number": ach["number"],
            "title": ach["title"],
            "complete": is_complete,
        })
        if is_complete:
            completed_count += 1
    
    # Calculate completion percentage
    total_count = len(achievements)
    percentage = int((completed_count / total_count) * 100) if total_count > 0 else 0
    is_complete = completed_count == total_count
    
    # Generate report
    report_lines = []
    
    # Header
    if is_complete:
        report_lines.append(f"✅ PLAN Complete: {feature_name}")
    else:
        report_lines.append(f"⏳ PLAN In Progress: {feature_name}")
    
    report_lines.append("")
    
    # Summary
    report_lines.append(f"Completion: {completed_count}/{total_count} ({percentage}%)")
    report_lines.append("")
    
    # Achievement list
    report_lines.append("Achievements:")
    for ach_status in achievement_status:
        icon = "✅" if ach_status["complete"] else "⏳"
        num = ach_status["number"]
        title = ach_status["title"][:60]  # Truncate long titles
        report_lines.append(f"  {icon} {num}: {title}")
    
    report_lines.append("")
    
    # Pending achievements (if any)
    pending = [a for a in achievement_status if not a["complete"]]
    if pending:
        report_lines.append("Pending:")
        for ach in pending:
            report_lines.append(f"  - {ach['number']}: {ach['title'][:60]}")
        report_lines.append("")
    
    # END_POINT readiness
    if is_complete:
        report_lines.append("Status: Ready for END_POINT ✅")
        report_lines.append("")
        report_lines.append("Next Steps:")
        report_lines.append("  1. Follow @LLM/protocols/IMPLEMENTATION_END_POINT.md")
        report_lines.append("  2. Archive PLAN completely")
        report_lines.append("  3. Update CHANGELOG.md")
    else:
        pending_count = len(pending)
        report_lines.append(f"Status: Not ready for END_POINT ({pending_count} achievement{'s' if pending_count != 1 else ''} pending)")
    
    # Verbose details
    if verbose:
        report_lines.append("")
        report_lines.append("Details:")
        report_lines.append(f"  - PLAN file: {plan_path}")
        report_lines.append(f"  - Archive: {archive_location or 'Not specified'}")
        report_lines.append(f"  - Feature: {feature_name}")
    
    return is_complete, "\n".join(report_lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate completion status report for PLAN"
    )
    parser.add_argument(
        "plan_path",
        type=str,
        help="Path to PLAN file (e.g., @PLAN_FEATURE.md or PLAN_FEATURE.md)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show additional details in report",
    )
    
    args = parser.parse_args()
    
    # Handle @ prefix
    plan_path_str = args.plan_path.lstrip("@")
    plan_path = Path(plan_path_str)
    
    if not plan_path.exists():
        print(f"❌ Error: PLAN file not found: {plan_path}")
        sys.exit(1)
    
    # Generate status report
    is_complete, report = generate_completion_status(plan_path, args.verbose)
    
    # Print report
    print(report)
    
    # Exit with appropriate code
    sys.exit(0 if is_complete else 1)


if __name__ == "__main__":
    main()


