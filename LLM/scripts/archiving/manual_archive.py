#!/usr/bin/env python3
"""
Manual Archive Script - User-Controlled Archiving

Archives files from workspace on-demand (only when user runs it).
Supports multiple detection methods and provides dry-run mode for safety.

Usage:
    # Dry-run: See what would be archived
    python LLM/scripts/archiving/manual_archive.py --dry-run --workspace work-space/

    # Archive files with status: archived metadata tag
    python LLM/scripts/archiving/manual_archive.py --workspace work-space/

    # Archive specific files
    python LLM/scripts/archiving/manual_archive.py work-space/plans/PLAN_TEST.md work-space/subplans/SUBPLAN_TEST_01.md

    # Archive files matching pattern
    python LLM/scripts/archiving/manual_archive.py --pattern "EXECUTION_TASK_*_*_01.md" --workspace work-space/

Detection Methods:
1. Metadata Tag: Files with "status: archived" in metadata section
2. Explicit List: Files provided as command-line arguments
3. Pattern Matching: Files matching specified pattern (e.g., completed EXECUTION_TASKs)

The script:
- Scans workspace for files to archive
- Validates files exist and are readable
- Provides dry-run mode to preview what would be archived
- Archives files to appropriate locations (from PLAN or metadata)
- Handles duplicates gracefully
- Provides clear feedback
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# Core library imports
from core.libraries.logging import setup_logging, get_logger, log_operation_start, log_operation_complete
from core.libraries.error_handling import handle_errors, error_context, ConfigurationError
from core.libraries.metrics import Counter, Histogram, MetricRegistry
from core.libraries.validation import validate_value, NotEmpty, Pattern, ValidationError

# Initialize logging
logger = get_logger(__name__)

# Initialize metrics
_archive_operations = Counter('archive_operations_total', labels=['operation', 'status'])
_archive_duration = Histogram('archive_operation_duration_seconds', labels=['operation'])
_archive_files_count = Counter('archive_files_total', labels=['type', 'status'])

# Register metrics
registry = MetricRegistry.get_instance()
registry.register(_archive_operations)
registry.register(_archive_duration)
registry.register(_archive_files_count)


@handle_errors(log_traceback=True)
def find_plan_file(file_path: Path, workspace: Path) -> Optional[Path]:
    """Find the parent PLAN file for a SUBPLAN or EXECUTION_TASK.
    
    Uses nested structure: work-space/plans/PLAN_NAME/
    If file is in nested structure, uses parent directory.
    Otherwise checks nested structure based on feature name.
    
    Args:
        file_path: Path to SUBPLAN or EXECUTION_TASK file
        workspace: Workspace root directory
        
    Returns:
        Path to PLAN file if found, None otherwise
    """
    logger.debug(f"Finding PLAN file for {file_path.name} in workspace {workspace}")
    # If already a PLAN file, return it
    if file_path.name.startswith("PLAN_"):
        return file_path
    
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
        return None

    # Check nested structure: work-space/plans/{feature}/PLAN_{feature}.md
    plan_name = f"PLAN_{feature}.md"
    plan_in_nested = workspace / "plans" / feature / plan_name

    if plan_in_nested.exists():
        logger.debug(f"Found PLAN file: {plan_in_nested}")
        return plan_in_nested

    logger.debug(f"No PLAN file found for {file_path.name}")
    return None


@handle_errors(log_traceback=True)
def get_archive_location(plan_path: Path) -> Optional[Path]:
    """Extract archive location from PLAN file."""
    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Look for "Archive Location" section
        patterns = [
            r"\*\*Archive Location\*\*:\s*`([^`]+)`",
            r"Archive Location[:\s]+`([^`]+)`",
            r"Archive Location[:\s]+\*\*[:\s]*`?([^`\n]+)`?",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                location = match.group(1).strip().strip("\"'")
                return Path(location)

        # Fallback: Try to infer from feature name
        feature = plan_path.stem.replace("PLAN_", "").lower().replace("_", "-")
        return Path(f"documentation/archive/{feature}/")
    except Exception:
        return None


def get_archive_location_from_metadata(file_path: Path) -> Optional[Path]:
    """Extract archive location from file metadata."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Look for archived: metadata tag
        match = re.search(r"\*\*archived\*\*:\s*([^\n]+)", content, re.IGNORECASE)
        if match:
            location = match.group(1).strip().strip("\"'")
            return Path(location)
    except Exception:
        pass
    return None


def has_archived_status(file_path: Path) -> bool:
    """Check if file has status: archived metadata tag."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Look for status: archived in metadata
        patterns = [
            r"\*\*status\*\*:\s*archived",
            r"status:\s*archived",
            r"\*\*Status\*\*:\s*archived",
        ]

        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
    except Exception:
        pass
    return False


def detect_files_by_metadata(workspace: Path) -> List[Path]:
    """Detect files with status: archived metadata tag."""
    files_to_archive = []

    # Scan all subdirectories
    for subdir in ["plans", "subplans", "execution"]:
        subdir_path = workspace / subdir
        if not subdir_path.exists():
            continue

        for file_path in subdir_path.glob("*.md"):
            if has_archived_status(file_path):
                files_to_archive.append(file_path)

    return files_to_archive


def detect_files_by_pattern(workspace: Path, pattern: str) -> List[Path]:
    """Detect files matching pattern."""
    files_to_archive = []

    # Convert glob pattern to regex
    regex_pattern = pattern.replace("*", ".*")

    # Scan all subdirectories
    for subdir in ["plans", "subplans", "execution"]:
        subdir_path = workspace / subdir
        if not subdir_path.exists():
            continue

        for file_path in subdir_path.glob("*.md"):
            if re.match(regex_pattern, file_path.name):
                files_to_archive.append(file_path)

    return files_to_archive


def determine_archive_type(file_path: Path) -> str:
    """Determine archive subdirectory based on file type."""
    if file_path.name.startswith("PLAN_"):
        return "planning"
    elif file_path.name.startswith("SUBPLAN_"):
        return "subplans"
    elif file_path.name.startswith("EXECUTION_TASK_"):
        return "execution"
    else:
        # Default to execution for unknown types
        return "execution"


def validate_file(file_path: Path) -> Tuple[bool, Optional[str]]:
    """Validate file exists and is readable."""
    if not file_path.exists():
        return False, f"File does not exist: {file_path}"

    if not file_path.is_file():
        return False, f"Not a file: {file_path}"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            f.read(1)  # Try to read at least one byte
    except Exception as e:
        return False, f"Cannot read file: {e}"

    return True, None


def archive_file(
    file_path: Path, archive_location: Path, archive_type: str, dry_run: bool = False
) -> Tuple[bool, Optional[str]]:
    """Archive a file to the specified location."""
    # Create archive structure if needed
    archive_dir = archive_location / archive_type
    if not dry_run:
        archive_dir.mkdir(parents=True, exist_ok=True)

    destination = archive_dir / file_path.name

    if destination.exists():
        return False, f"Already exists in archive: {destination}"

    if dry_run:
        return True, f"Would archive: {file_path.name} → {destination}"

    # Move file
    try:
        file_path.rename(destination)
        return True, f"Archived: {file_path.name} → {destination}"
    except Exception as e:
        return False, f"Error archiving: {e}"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manually archive files from workspace (user-controlled, on-demand)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run: See what would be archived
  python LLM/scripts/archiving/manual_archive.py --dry-run --workspace work-space/
  
  # Archive files with status: archived metadata tag
  python LLM/scripts/archiving/manual_archive.py --workspace work-space/
  
  # Archive specific files
  python LLM/scripts/archiving/manual_archive.py work-space/plans/PLAN_TEST.md
  
  # Archive files matching pattern
  python LLM/scripts/archiving/manual_archive.py --pattern "EXECUTION_TASK_*_*_01.md" --workspace work-space/

Detection Methods:
1. Metadata Tag: Files with "status: archived" in metadata
2. Explicit List: Files provided as command-line arguments
3. Pattern Matching: Files matching --pattern

The script:
- Scans workspace for files to archive
- Validates files before archiving
- Provides dry-run mode for safety
- Archives files to appropriate locations
- Handles duplicates gracefully

Exit Codes:
  0 = Success
  1 = Error (validation failed, archive failed, etc.)
        """,
    )

    parser.add_argument(
        "files",
        nargs="*",
        help="Specific files to archive (optional, if not provided, uses detection methods)",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path("work-space"),
        help="Workspace directory (default: work-space/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be archived without actually archiving",
    )
    parser.add_argument(
        "--pattern",
        help="Archive files matching pattern (e.g., 'EXECUTION_TASK_*_*_01.md')",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    # Validate workspace exists
    if not args.workspace.exists():
        print(f"❌ Error: Workspace not found: {args.workspace}")
        sys.exit(1)

    files_to_archive = []

    # Detection methods
    if args.files:
        # Explicit file list
        for file_str in args.files:
            file_path = Path(file_str)
            if not file_path.is_absolute():
                # Try relative to workspace first, then current directory
                workspace_path = args.workspace / file_path
                if workspace_path.exists():
                    file_path = workspace_path
                elif not file_path.exists():
                    print(f"❌ Error: File not found: {file_str}")
                    sys.exit(1)
            files_to_archive.append(file_path)
    elif args.pattern:
        # Pattern matching
        files_to_archive = detect_files_by_pattern(args.workspace, args.pattern)
        if args.verbose:
            print(f"🔍 Pattern '{args.pattern}' matched {len(files_to_archive)} file(s)")
    else:
        # Metadata tag detection (default)
        files_to_archive = detect_files_by_metadata(args.workspace)
        if args.verbose:
            print(
                f"🔍 Metadata detection found {len(files_to_archive)} file(s) with status: archived"
            )

    if not files_to_archive:
        print("ℹ️  No files found to archive")
        if args.dry_run:
            print("💡 Tip: Use --pattern or provide explicit file list")
        sys.exit(0)

    # Validate all files
    valid_files = []
    for file_path in files_to_archive:
        is_valid, error = validate_file(file_path)
        if is_valid:
            valid_files.append(file_path)
        else:
            print(f"⚠️  Skipping invalid file: {error}")

    if not valid_files:
        print("❌ No valid files to archive")
        sys.exit(1)

    # Determine archive locations and archive files
    archived_count = 0
    skipped_count = 0

    for file_path in valid_files:
        # Find archive location
        archive_location = None

        # Try to get from file metadata first
        archive_location = get_archive_location_from_metadata(file_path)

        # If not in metadata, try to find from PLAN
        if not archive_location:
            plan_path = find_plan_file(file_path, args.workspace)
            if plan_path:
                archive_location = get_archive_location(plan_path)

        # Fallback: use default archive structure
        if not archive_location:
            # Extract feature name from file
            if file_path.name.startswith("PLAN_"):
                feature = (
                    file_path.name.replace("PLAN_", "").replace(".md", "").lower().replace("_", "-")
                )
            elif file_path.name.startswith("SUBPLAN_"):
                feature = (
                    file_path.name.replace("SUBPLAN_", "").split("_")[0].lower().replace("_", "-")
                )
            elif file_path.name.startswith("EXECUTION_TASK_"):
                feature = (
                    file_path.name.replace("EXECUTION_TASK_", "")
                    .split("_")[0]
                    .lower()
                    .replace("_", "-")
                )
            else:
                feature = "unknown"
            archive_location = Path(f"documentation/archive/{feature}/")

        if not archive_location:
            print(f"⚠️  Could not determine archive location for: {file_path.name}")
            skipped_count += 1
            continue

        # Determine archive type
        archive_type = determine_archive_type(file_path)

        # Archive file
        success, message = archive_file(file_path, archive_location, archive_type, args.dry_run)

        if success:
            if args.verbose or args.dry_run:
                print(f"✅ {message}")
            archived_count += 1
        else:
            print(f"⚠️  {message}")
            skipped_count += 1

    # Summary
    if args.dry_run:
        print(f"\n📋 Dry-run complete: {archived_count} file(s) would be archived")
        if skipped_count > 0:
            print(f"⚠️  {skipped_count} file(s) would be skipped")
    else:
        print(f"\n✅ Archived {archived_count} file(s) successfully!")
        if skipped_count > 0:
            print(f"⚠️  {skipped_count} file(s) skipped")

    sys.exit(0 if archived_count > 0 else 1)


if __name__ == "__main__":
    main()
