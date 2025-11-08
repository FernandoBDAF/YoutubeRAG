#!/usr/bin/env python3
"""
Validate archive location compliance for PLAN documents.

Checks:
- Archive location in PLAN matches actual archive location
- Archive structure exists (subplans/, execution/)
- No duplicate files (root vs archive)
- Reports mismatches and provides fix suggestions
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional, Tuple


def extract_archive_location(plan_path: Path) -> Optional[str]:
    """Extract archive location from PLAN file."""
    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Look for "Archive Location" section
        # Pattern: **Archive Location**: `documentation/archive/FEATURE-NAME/`
        patterns = [
            r"\*\*Archive Location\*\*:\s*`([^`]+)`",
            r"Archive Location[:\s]+`([^`]+)`",
            r"Archive Location[:\s]+([^\n]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Normalize path (remove trailing slash, handle relative paths)
                if location.startswith("./"):
                    location = location[2:]
                if location.endswith("/"):
                    location = location[:-1]
                return location
        
        return None
    except Exception as e:
        print(f"❌ Error reading PLAN file: {e}", file=sys.stderr)
        return None


def check_archive_structure(archive_path: Path) -> Tuple[bool, list]:
    """Check if archive structure exists (subplans/, execution/)."""
    issues = []
    
    if not archive_path.exists():
        issues.append(f"Archive directory does not exist: {archive_path}")
        return False, issues
    
    subplans_dir = archive_path / "subplans"
    execution_dir = archive_path / "execution"
    
    if not subplans_dir.exists():
        issues.append(f"Missing subplans/ directory: {subplans_dir}")
    
    if not execution_dir.exists():
        issues.append(f"Missing execution/ directory: {execution_dir}")
    
    return len(issues) == 0, issues


def check_duplicate_files(plan_path: Path, archive_path: Path) -> Tuple[bool, list]:
    """Check for duplicate files (root vs archive)."""
    issues = []
    
    if not archive_path.exists():
        return True, issues  # Can't check duplicates if archive doesn't exist
    
    feature_name = plan_path.stem.replace("PLAN_", "")
    root_dir = Path(".")
    
    # Check for SUBPLAN files in root that should be archived
    subplans_archive = archive_path / "subplans"
    if subplans_archive.exists():
        for subplan_file in root_dir.glob(f"SUBPLAN_{feature_name}_*.md"):
            archived_subplan = subplans_archive / subplan_file.name
            if archived_subplan.exists():
                issues.append(f"Duplicate SUBPLAN in root and archive: {subplan_file.name}")
    
    # Check for EXECUTION_TASK files in root that should be archived
    execution_archive = archive_path / "execution"
    if execution_archive.exists():
        for exec_file in root_dir.glob(f"EXECUTION_TASK_{feature_name}_*.md"):
            archived_exec = execution_archive / exec_file.name
            if archived_exec.exists():
                issues.append(f"Duplicate EXECUTION_TASK in root and archive: {exec_file.name}")
    
    return len(issues) == 0, issues


def validate_archive_location(plan_path: Path) -> Tuple[bool, str]:
    """Validate archive location compliance."""
    plan_path = Path(plan_path)
    
    if not plan_path.exists():
        return False, f"❌ PLAN file not found: {plan_path}"
    
    # Extract archive location from PLAN
    archive_location = extract_archive_location(plan_path)
    
    if not archive_location:
        return False, "❌ Archive location not found in PLAN. Add 'Archive Location' section to PLAN."
    
    # Convert to Path
    archive_path = Path(archive_location)
    
    # Check archive structure
    structure_ok, structure_issues = check_archive_structure(archive_path)
    
    # Check for duplicate files
    duplicates_ok, duplicate_issues = check_duplicate_files(plan_path, archive_path)
    
    # Build report
    all_ok = structure_ok and duplicates_ok
    issues = structure_issues + duplicate_issues
    
    if all_ok:
        return True, f"✅ Archive location validated: {archive_location}\n  - Structure exists\n  - No duplicates found"
    
    # Build error message with fix suggestions
    error_msg = f"❌ Archive location issues found:\n"
    error_msg += f"  Archive Location: {archive_location}\n\n"
    
    if structure_issues:
        error_msg += "**Structure Issues**:\n"
        for issue in structure_issues:
            error_msg += f"  - {issue}\n"
        error_msg += f"\n**Fix**: Create archive structure:\n"
        error_msg += f"  mkdir -p {archive_location}/{{subplans,execution}}\n\n"
    
    if duplicate_issues:
        error_msg += "**Duplicate Files**:\n"
        for issue in duplicate_issues:
            error_msg += f"  - {issue}\n"
        error_msg += f"\n**Fix**: Remove duplicates from root directory:\n"
        for issue in duplicate_issues:
            filename = issue.split(": ")[1] if ": " in issue else ""
            if filename:
                error_msg += f"  rm {filename}\n"
    
    return False, error_msg


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate archive location compliance for PLAN documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument("plan_file", help="PLAN file to validate (e.g., PLAN_FEATURE.md)")
    
    args = parser.parse_args()
    
    plan_path = Path(args.plan_file.replace("@", ""))
    
    is_valid, message = validate_archive_location(plan_path)
    
    print(message)
    
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()


