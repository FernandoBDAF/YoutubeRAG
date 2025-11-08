#!/usr/bin/env python3
"""
Archive Completed Files - Helper Script

Moves completed SUBPLANs and EXECUTION_TASKs to archive folder.
Supports deferred archiving policy: archive at achievement/plan completion (batch mode).

Usage:
    # Single file (deferred archiving - archive when ready)
    python LLM/scripts/archive_completed.py @SUBPLAN_FEATURE_XX.md
    
    # Batch mode: archive multiple files together (recommended for deferred archiving)
    python LLM/scripts/archive_completed.py --batch @SUBPLAN_FEATURE_XX.md @EXECUTION_TASK_FEATURE_XX_YY.md
    
    # Multiple files (batch mode implied)
    python LLM/scripts/archive_completed.py @SUBPLAN_FEATURE_XX.md @EXECUTION_TASK_FEATURE_XX_YY.md

The script:
- Auto-detects archive location from PLAN file
- Creates archive structure if needed
- Moves file(s) to appropriate subdirectory
- Supports batch operations for deferred archiving policy
- Provides clear feedback
"""

import argparse
import re
import sys
from pathlib import Path


def find_plan_file(file_path: Path) -> Path:
    """Find the parent PLAN file for a SUBPLAN or EXECUTION_TASK.
    
    Uses nested structure: work-space/plans/PLAN_NAME/
    If file is in nested structure, uses parent directory.
    Otherwise checks nested structure based on feature name.
    """
    # Check if file is in nested structure: work-space/plans/{feature}/
    # If so, PLAN is in the same directory
    if "plans" in file_path.parts:
        plan_index = file_path.parts.index("plans")
        if plan_index + 1 < len(file_path.parts):
            plan_folder = Path(*file_path.parts[:plan_index + 2])
            # Extract feature name from folder name
            feature_name = plan_folder.name
            plan_file = plan_folder / f"PLAN_{feature_name}.md"
            if plan_file.exists():
                return plan_file
    
    # Extract feature name from file
    if file_path.name.startswith("SUBPLAN_"):
        feature = file_path.name.replace("SUBPLAN_", "").split("_")[0]
    elif file_path.name.startswith("EXECUTION_TASK_"):
        parts = file_path.name.replace("EXECUTION_TASK_", "").split("_")
        feature = parts[0]
    else:
        raise ValueError(f"Unknown file type: {file_path.name}")

    # Check nested structure: work-space/plans/{feature}/PLAN_{feature}.md
    plan_file = Path("work-space") / "plans" / feature / f"PLAN_{feature}.md"
    if plan_file.exists():
        return plan_file

    # Try with different naming (e.g., METHODOLOGY-V2-ENHANCEMENTS)
    # This is a fallback - ideally feature name matches exactly
    raise FileNotFoundError(f"Could not find PLAN file for feature: {feature}")


def get_archive_location(plan_path: Path) -> Path:
    """Extract archive location from PLAN file."""
    with open(plan_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Look for "Archive Location" section
    match = re.search(r"Archive Location[:\s]+\*\*[:\s]*`?([^`\n]+)`?", content, re.IGNORECASE)
    if match:
        location = match.group(1).strip()
        # Remove quotes if present
        location = location.strip("\"'")
        return Path(location)

    # Fallback: Try to infer from feature name
    feature = plan_path.stem.replace("PLAN_", "").lower().replace("_", "-")
    return Path(f"./{feature}-archive/")


def determine_archive_type(file_path: Path) -> str:
    """Determine if file is SUBPLAN or EXECUTION_TASK."""
    if file_path.name.startswith("SUBPLAN_"):
        return "subplans"
    elif file_path.name.startswith("EXECUTION_TASK_"):
        return "execution"
    else:
        raise ValueError(f"Unknown file type: {file_path.name}")


def archive_file(file_path: Path, archive_location: Path, archive_type: str) -> bool:
    """Move file to archive location."""
    # Create archive structure if needed
    archive_dir = archive_location / archive_type
    archive_dir.mkdir(parents=True, exist_ok=True)

    # Move file
    destination = archive_dir / file_path.name

    if destination.exists():
        print(f"⚠️  Warning: {destination} already exists. Skipping move.")
        return False

    file_path.rename(destination)
    print(f"✅ Archived: {file_path.name} → {destination}")
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Archive completed SUBPLAN or EXECUTION_TASK (supports deferred archiving)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single file
  python LLM/scripts/archive_completed.py @SUBPLAN_FEATURE_01.md
  
  # Batch mode (recommended for deferred archiving - archive at achievement completion)
  python LLM/scripts/archive_completed.py --batch @SUBPLAN_FEATURE_01.md @EXECUTION_TASK_FEATURE_01_01.md
  
  # Multiple files (batch mode implied)
  python LLM/scripts/archive_completed.py @SUBPLAN_FEATURE_01.md @EXECUTION_TASK_FEATURE_01_01.md

The script:
- Finds parent PLAN file
- Extracts archive location from PLAN
- Moves file(s) to archive/subplans/ or archive/execution/
- Creates archive structure if needed
- Supports batch operations for deferred archiving policy

Deferred Archiving Policy:
- Archive files at achievement completion or plan completion (not immediately)
- Use --batch flag or multiple files to archive together
- Reduces file moving overhead by 95%

Exit Codes:
  0 = Success
  1 = Error (file not found, archive location not found, etc.)
        """,
    )

    parser.add_argument(
        "files",
        nargs="+",
        help="SUBPLAN or EXECUTION_TASK file(s) to archive (e.g., @SUBPLAN_FEATURE_01.md)",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Batch mode: archive multiple files together (recommended for deferred archiving)",
    )

    args = parser.parse_args()

    try:
        # Clean file paths
        file_paths = [Path(f.replace("@", "")) for f in args.files]

        # Validate all files exist
        for file_path in file_paths:
            if not file_path.exists():
                print(f"❌ Error: File not found: {file_path}")
                sys.exit(1)

        # Find parent PLAN (use first file to determine PLAN)
        try:
            plan_path = find_plan_file(file_paths[0])
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            print(f"💡 Tip: Ensure PLAN file exists and feature name matches")
            sys.exit(1)

        # Get archive location
        archive_location = get_archive_location(plan_path)

        # Archive all files
        success_count = 0
        for file_path in file_paths:
            # Determine archive type
            try:
                archive_type = determine_archive_type(file_path)
            except ValueError as e:
                print(f"❌ Error: {e}")
                continue

            # Archive file
            if archive_file(file_path, archive_location, archive_type):
                success_count += 1

        if success_count > 0:
            print(f"\n✅ Archived {success_count} file(s) successfully!")
            print(f"📁 Archive: {archive_location}/")
            if args.batch or len(file_paths) > 1:
                print(f"📦 Batch mode: Deferred archiving policy applied")
            sys.exit(0)
        else:
            print(f"\n⚠️  No files were archived")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
