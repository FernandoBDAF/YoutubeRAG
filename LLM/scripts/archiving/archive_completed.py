#!/usr/bin/env python3
"""
Archive Completed Files - Helper Script

Moves completed SUBPLANs and EXECUTION_TASKs to archive folder immediately upon completion.

Usage:
    python LLM/scripts/archive_completed.py @SUBPLAN_FEATURE_XX.md
    python LLM/scripts/archive_completed.py @EXECUTION_TASK_FEATURE_XX_YY.md

The script:
- Auto-detects archive location from PLAN file
- Creates archive structure if needed
- Moves file to appropriate subdirectory
- Provides clear feedback
"""

import argparse
import re
import sys
from pathlib import Path


def find_plan_file(file_path: Path) -> Path:
    """Find the parent PLAN file for a SUBPLAN or EXECUTION_TASK."""
    # Extract feature name from file
    if file_path.name.startswith("SUBPLAN_"):
        feature = file_path.name.replace("SUBPLAN_", "").split("_")[0]
    elif file_path.name.startswith("EXECUTION_TASK_"):
        parts = file_path.name.replace("EXECUTION_TASK_", "").split("_")
        feature = parts[0]
    else:
        raise ValueError(f"Unknown file type: {file_path.name}")

    # Look for PLAN file
    plan_file = Path(f"PLAN_{feature}.md")
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
        description="Archive completed SUBPLAN or EXECUTION_TASK immediately",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python LLM/scripts/archive_completed.py @SUBPLAN_FEATURE_01.md
  python LLM/scripts/archive_completed.py @EXECUTION_TASK_FEATURE_01_01.md

The script:
- Finds parent PLAN file
- Extracts archive location from PLAN
- Moves file to archive/subplans/ or archive/execution/
- Creates archive structure if needed

Exit Codes:
  0 = Success
  1 = Error (file not found, archive location not found, etc.)
        """,
    )

    parser.add_argument(
        "file", help="SUBPLAN or EXECUTION_TASK file to archive (e.g., @SUBPLAN_FEATURE_01.md)"
    )

    args = parser.parse_args()

    try:
        # Clean file path
        file_path = Path(args.file.replace("@", ""))

        if not file_path.exists():
            print(f"❌ Error: File not found: {file_path}")
            sys.exit(1)

        # Find parent PLAN
        try:
            plan_path = find_plan_file(file_path)
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            print(f"💡 Tip: Ensure PLAN file exists and feature name matches")
            sys.exit(1)

        # Get archive location
        archive_location = get_archive_location(plan_path)

        # Determine archive type
        try:
            archive_type = determine_archive_type(file_path)
        except ValueError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

        # Archive file
        success = archive_file(file_path, archive_location, archive_type)

        if success:
            print(f"\n✅ File archived successfully!")
            print(f"📁 Archive: {archive_location}/{archive_type}/")
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
