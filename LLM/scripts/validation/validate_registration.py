#!/usr/bin/env python3
"""
Validate Component Registration - Blocking Validation Script

Validates that all SUBPLANs and EXECUTION_TASKs are properly registered in their parent PLAN/SUBPLAN.
Checks: Registered components match filesystem, no orphaned files, no missing registrations.

Usage:
    python LLM/scripts/validate_registration.py @PLAN_FILE.md
    python LLM/scripts/validate_registration.py @SUBPLAN_FILE.md

Exit Codes:
    0 = All components properly registered (OK)
    1 = Issues found (MUST fix before continuing)
"""

import argparse
import re
import sys
from pathlib import Path


def find_subplans_for_plan(plan_path: Path) -> list:
    """Find all SUBPLAN files for a PLAN (nested structure)."""
    feature = plan_path.stem.replace('PLAN_', '')
    subplan_files = []
    
    # Check nested structure: work-space/plans/PLAN_NAME/subplans/
    plan_folder = plan_path.parent
    nested_subplans_dir = plan_folder / "subplans"
    if nested_subplans_dir.exists():
        subplan_files.extend(nested_subplans_dir.glob("SUBPLAN_*.md"))
    
    # Also check archive for archived SUBPLANs
    archive_location = get_archive_location(plan_path)
    if archive_location.exists():
        archived = list((archive_location / 'subplans').glob(f"SUBPLAN_{feature}_*.md"))
        subplan_files.extend(archived)
    
    return subplan_files


def find_execution_tasks_for_plan(plan_path: Path) -> list:
    """Find all EXECUTION_TASK files for a PLAN (nested structure)."""
    feature = plan_path.stem.replace('PLAN_', '')
    execution_files = []
    
    # Check nested structure: work-space/plans/PLAN_NAME/execution/
    plan_folder = plan_path.parent
    nested_execution_dir = plan_folder / "execution"
    if nested_execution_dir.exists():
        execution_files.extend(nested_execution_dir.glob("EXECUTION_TASK_*.md"))
    
    # Also check archive for archived EXECUTION_TASKs
    archive_location = get_archive_location(plan_path)
    if archive_location.exists():
        archived = list((archive_location / 'execution').glob(f"EXECUTION_TASK_{feature}_*.md"))
        execution_files.extend(archived)
    
    return execution_files


def find_execution_tasks_for_subplan(subplan_path: Path) -> list:
    """Find all EXECUTION_TASK files for a SUBPLAN (nested structure)."""
    # Extract feature and subplan number
    match = re.match(r'SUBPLAN_([A-Z0-9-]+)_(\d+)\.md', subplan_path.name)
    if not match:
        return []
    
    feature = match.group(1)
    subplan_num = match.group(2)
    execution_files = []
    
    # Check nested structure: work-space/plans/PLAN_NAME/execution/
    # SUBPLAN is in work-space/plans/PLAN_NAME/subplans/, so parent's parent is the plan folder
    plan_folder = subplan_path.parent.parent
    nested_execution_dir = plan_folder / "execution"
    if nested_execution_dir.exists():
        execution_files.extend(nested_execution_dir.glob(f"EXECUTION_TASK_{feature}_{subplan_num}_*.md"))
    
    # Also check archive for archived EXECUTION_TASKs
    plan_path = Path(f"work-space/plans/PLAN_{feature}/PLAN_{feature}.md")
    if not plan_path.exists():
        plan_path = Path(f"PLAN_{feature}.md")
    if plan_path.exists():
        archive_location = get_archive_location(plan_path)
        if archive_location.exists():
            archived = list((archive_location / 'execution').glob(f"EXECUTION_TASK_{feature}_{subplan_num}_*.md"))
            execution_files.extend(archived)
    
    return execution_files


def get_archive_location(plan_path: Path) -> Path:
    """Extract archive location from PLAN file."""
    with open(plan_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for "Archive Location" section
    match = re.search(r'Archive Location[:\s]+\*\*[:\s]*`?([^`\n]+)`?', content, re.IGNORECASE)
    if match:
        location = match.group(1).strip().strip('"\'')
        return Path(location)
    
    # Fallback
    feature = plan_path.stem.replace('PLAN_', '').lower().replace('_', '-')
    return Path(f"./{feature}-archive/")


def extract_registered_subplans(plan_path: Path) -> list:
    """Extract registered SUBPLANs from PLAN file."""
    with open(plan_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    registered = []
    
    # Look in "Active Components" section
    active_match = re.search(r'## 🔄 Active Components.*?## 🔄 Subplan Tracking', content, re.DOTALL)
    if active_match:
        active_section = active_match.group(0)
        subplan_matches = re.findall(r'SUBPLAN_([A-Z0-9-]+)_(\d+)', active_section)
        for feature, num in subplan_matches:
            registered.append(f"SUBPLAN_{feature}_{num}.md")
    
    # Look in "Subplan Tracking" section
    tracking_match = re.search(r'## 🔄 Subplan Tracking.*?##', content, re.DOTALL)
    if tracking_match:
        tracking_section = tracking_match.group(0)
        subplan_matches = re.findall(r'SUBPLAN_([A-Z0-9-]+)_(\d+)', tracking_section)
        for feature, num in subplan_matches:
            registered.append(f"SUBPLAN_{feature}_{num}.md")
    
    return list(set(registered))  # Remove duplicates


def extract_registered_execution_tasks_plan(plan_path: Path) -> list:
    """Extract registered EXECUTION_TASKs from PLAN file."""
    with open(plan_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    registered = []
    
    # Look in "Active Components" section
    active_match = re.search(r'## 🔄 Active Components.*?## 🔄 Subplan Tracking', content, re.DOTALL)
    if active_match:
        active_section = active_match.group(0)
        execution_matches = re.findall(r'EXECUTION_TASK_([A-Z0-9-]+)_(\d+)_(\d+)', active_section)
        for feature, subplan_num, exec_num in execution_matches:
            registered.append(f"EXECUTION_TASK_{feature}_{subplan_num}_{exec_num}.md")
    
    # Look in "Subplan Tracking" section
    tracking_match = re.search(r'## 🔄 Subplan Tracking.*?##', content, re.DOTALL)
    if tracking_match:
        tracking_section = tracking_match.group(0)
        execution_matches = re.findall(r'EXECUTION_TASK_([A-Z0-9-]+)_(\d+)_(\d+)', tracking_section)
        for feature, subplan_num, exec_num in execution_matches:
            registered.append(f"EXECUTION_TASK_{feature}_{subplan_num}_{exec_num}.md")
    
    return list(set(registered))  # Remove duplicates


def extract_registered_execution_tasks_subplan(subplan_path: Path) -> list:
    """Extract registered EXECUTION_TASKs from SUBPLAN file."""
    with open(subplan_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    registered = []
    
    # Look in "Active EXECUTION_TASKs" section
    active_match = re.search(r'## 🔄 Active EXECUTION_TASKs.*?##', content, re.DOTALL)
    if active_match:
        active_section = active_match.group(0)
        execution_matches = re.findall(r'EXECUTION_TASK_([A-Z0-9-]+)_(\d+)_(\d+)', active_section)
        for feature, subplan_num, exec_num in execution_matches:
            registered.append(f"EXECUTION_TASK_{feature}_{subplan_num}_{exec_num}.md")
    
    return registered


def validate_plan_registration(plan_path: Path) -> tuple[bool, str]:
    """
    Validate PLAN component registration.
    
    Returns:
        (pass, message) - pass=True if valid, False if issues found
    """
    if not plan_path.exists():
        return False, f"❌ Error: PLAN file not found: {plan_path}"
    
    errors = []
    warnings = []
    
    # Find actual files
    actual_subplans = [f.name for f in find_subplans_for_plan(plan_path)]
    actual_execution_tasks = [f.name for f in find_execution_tasks_for_plan(plan_path)]
    
    # Find registered components
    registered_subplans = extract_registered_subplans(plan_path)
    registered_execution_tasks = extract_registered_execution_tasks_plan(plan_path)
    
    # Check for unregistered SUBPLANs
    unregistered_subplans = [f for f in actual_subplans if f not in registered_subplans]
    if unregistered_subplans:
        errors.append(f"❌ Unregistered SUBPLANs: {', '.join(unregistered_subplans)}")
    
    # Check for unregistered EXECUTION_TASKs
    unregistered_execution_tasks = [f for f in actual_execution_tasks if f not in registered_execution_tasks]
    if unregistered_execution_tasks:
        errors.append(f"❌ Unregistered EXECUTION_TASKs: {', '.join(unregistered_execution_tasks[:5])}")  # Limit to 5
    
    # Check for orphaned registrations (registered but file doesn't exist)
    orphaned_subplans = [f for f in registered_subplans if f not in actual_subplans]
    if orphaned_subplans:
        warnings.append(f"⚠️  Orphaned SUBPLAN registrations: {', '.join(orphaned_subplans)}")
    
    orphaned_execution_tasks = [f for f in registered_execution_tasks if f not in actual_execution_tasks]
    if orphaned_execution_tasks:
        warnings.append(f"⚠️  Orphaned EXECUTION_TASK registrations: {', '.join(orphaned_execution_tasks[:5])}")
    
    # Build message
    if errors:
        message = "❌ REGISTRATION ISSUES FOUND - BLOCKING CONTINUATION\n\n"
        message += "Issues Found:\n"
        message += "\n".join(errors)
        if warnings:
            message += "\n\nWarnings:\n"
            message += "\n".join(warnings)
        
        message += "\n\n📋 Fix Prompt:\n\n"
        message += "To fix these issues:\n"
        
        if unregistered_subplans:
            message += "1. Register unregistered SUBPLANs in PLAN 'Active Components' section:\n"
            for subplan in unregistered_subplans:
                message += f"   - {subplan}\n"
        
        if unregistered_execution_tasks:
            message += "2. Register unregistered EXECUTION_TASKs in PLAN 'Active Components' section:\n"
            for execution in unregistered_execution_tasks[:5]:
                message += f"   - {execution}\n"
        
        message += "\nAfter fixing, run validation again:\n"
        message += f"  python LLM/scripts/validate_registration.py @{plan_path.name}\n"
        
        return False, message
    
    # Valid (warnings are OK)
    message = "✅ Component registration validated\n\n"
    message += "Checks passed:\n"
    message += f"✓ All SUBPLANs registered ({len(actual_subplans)} total)\n"
    message += f"✓ All EXECUTION_TASKs registered ({len(actual_execution_tasks)} total)\n"
    if warnings:
        message += "\nWarnings (non-blocking):\n"
        message += "\n".join(warnings)
        message += "\n\n💡 Consider cleaning up orphaned registrations."
    
    message += "\nSafe to continue!"
    
    return True, message


def validate_subplan_registration(subplan_path: Path) -> tuple[bool, str]:
    """
    Validate SUBPLAN EXECUTION_TASK registration.
    
    Returns:
        (pass, message) - pass=True if valid, False if issues found
    """
    if not subplan_path.exists():
        return False, f"❌ Error: SUBPLAN file not found: {subplan_path}"
    
    errors = []
    
    # Find actual files
    actual_execution_tasks = [f.name for f in find_execution_tasks_for_subplan(subplan_path)]
    
    # Find registered components
    registered_execution_tasks = extract_registered_execution_tasks_subplan(subplan_path)
    
    # Check for unregistered EXECUTION_TASKs
    unregistered = [f for f in actual_execution_tasks if f not in registered_execution_tasks]
    if unregistered:
        errors.append(f"❌ Unregistered EXECUTION_TASKs: {', '.join(unregistered)}")
    
    # Build message
    if errors:
        message = "❌ REGISTRATION ISSUES FOUND - BLOCKING CONTINUATION\n\n"
        message += "Issues Found:\n"
        message += "\n".join(errors)
        
        message += "\n\n📋 Fix Prompt:\n\n"
        message += "To fix these issues:\n"
        message += "1. Register unregistered EXECUTION_TASKs in SUBPLAN 'Active EXECUTION_TASKs' section:\n"
        for execution in unregistered:
            message += f"   - {execution}\n"
        
        message += "\nAfter fixing, run validation again:\n"
        message += f"  python LLM/scripts/validate_registration.py @{subplan_path.name}\n"
        
        return False, message
    
    # Valid
    message = "✅ Component registration validated\n\n"
    message += "Checks passed:\n"
    message += f"✓ All EXECUTION_TASKs registered ({len(actual_execution_tasks)} total)\n"
    message += "\nSafe to continue!"
    
    return True, message


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate component registration in PLAN or SUBPLAN',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python LLM/scripts/validate_registration.py @PLAN_FEATURE.md
  python LLM/scripts/validate_registration.py @SUBPLAN_FEATURE_XX.md

Checks:
  - All SUBPLANs registered in PLAN
  - All EXECUTION_TASKs registered in PLAN/SUBPLAN
  - No orphaned registrations

Exit Codes:
  0 = All components properly registered (OK)
  1 = Issues found (MUST fix before continuing)
        """
    )
    
    parser.add_argument(
        'file',
        help='PLAN or SUBPLAN file (e.g., @PLAN_FEATURE.md or @SUBPLAN_FEATURE_XX.md)'
    )
    
    args = parser.parse_args()
    
    try:
        # Clean file path
        file_path = Path(args.file.replace('@', ''))
        
        # Determine file type and validate
        if file_path.name.startswith('PLAN_'):
            pass_check, message = validate_plan_registration(file_path)
        elif file_path.name.startswith('SUBPLAN_'):
            pass_check, message = validate_subplan_registration(file_path)
        else:
            print(f"❌ Error: File must be PLAN_*.md or SUBPLAN_*.md", file=sys.stderr)
            sys.exit(1)
        
        # Print message
        print(message)
        
        # Exit code
        sys.exit(0 if pass_check else 1)
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

