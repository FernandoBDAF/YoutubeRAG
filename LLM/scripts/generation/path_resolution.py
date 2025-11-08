"""
Shared path resolution utilities for prompt generation scripts.

This module provides consistent path resolution across all prompt generation scripts:
- generate_prompt.py
- generate_subplan_prompt.py
- generate_execution_prompt.py

Supports:
- @folder shortcuts (e.g., @RESTORE)
- @PLAN_NAME.md shortcuts (e.g., @PLAN_FEATURE.md)
- Full paths (absolute or relative)
- Nested workspace structure (work-space/plans/PLAN_NAME/)

Created: 2025-11-09
Purpose: Fix Bug #9 (feature parity gap) and prevent future inconsistencies
Reference: EXECUTION_ANALYSIS_SUBPLAN-PROMPT-GENERATOR-MISSING-PATH-RESOLUTION-BUG-9.md
"""

import sys
from pathlib import Path
from typing import Optional


def resolve_folder_shortcut(folder_name: str) -> Path:
    """
    Resolve @folder_name to PLAN file in that folder.

    Supports short folder-based references like @RESTORE instead of full path.
    Searches work-space/plans/ for folders matching the name.

    Args:
        folder_name: Folder name without @ (e.g., "RESTORE", "GRAPHRAG")

    Returns:
        Path to PLAN file in matching folder

    Raises:
        SystemExit: If folder not found, multiple matches, or no PLAN file

    Examples:
        @RESTORE → work-space/plans/RESTORE-EXECUTION-WORKFLOW-AUTOMATION/PLAN_*.md
        @GRAPHRAG → work-space/plans/GRAPHRAG-OBSERVABILITY-EXCELLENCE/PLAN_*.md
    """
    plans_dir = Path("work-space/plans")

    if not plans_dir.exists():
        print(f"❌ Plans directory not found: {plans_dir}")
        sys.exit(1)

    # Find folders containing the name (case-insensitive partial match)
    matching_folders = []
    for folder in plans_dir.iterdir():
        if folder.is_dir() and folder_name.upper() in folder.name.upper():
            matching_folders.append(folder)

    if not matching_folders:
        print(f"❌ No folder found matching '@{folder_name}'")
        print(f"\n   Searched in: {plans_dir}")
        print(f"   Available folders:")
        for folder in sorted(plans_dir.iterdir()):
            if folder.is_dir():
                print(f"     - {folder.name}")
        sys.exit(1)

    if len(matching_folders) > 1:
        print(f"⚠️  Multiple folders match '@{folder_name}':")
        for f in matching_folders:
            print(f"   - {f.name}")
        print("\n   Use more specific name or full path")
        sys.exit(1)

    # Find PLAN file in folder
    folder = matching_folders[0]
    plan_files = list(folder.glob("PLAN_*.md"))

    if not plan_files:
        print(f"❌ No PLAN file found in {folder.name}")
        print(f"   Expected: PLAN_*.md")
        sys.exit(1)

    if len(plan_files) > 1:
        print(f"⚠️  Multiple PLAN files in {folder.name}:")
        for f in plan_files:
            print(f"   - {f.name}")
        sys.exit(1)

    return plan_files[0]


def resolve_plan_path(path_str: str, file_type: str = "PLAN") -> Path:
    """
    Resolve path with @ shorthand support.

    Supports multiple formats:
    - @folder (e.g., @RESTORE) → searches for PLAN in folder
    - @PLAN_NAME.md (e.g., @PLAN_FEATURE.md) → searches work-space/plans/ recursively
    - @SUBPLAN_NAME.md → searches work-space/plans/*/subplans/ recursively
    - Full paths (absolute or relative)

    Args:
        path_str: Path string (may start with @)
        file_type: Type of file ("PLAN", "SUBPLAN", "EXECUTION_TASK") for better error messages

    Returns:
        Resolved Path object

    Raises:
        SystemExit: If path not found or ambiguous

    Examples:
        @RESTORE → work-space/plans/RESTORE-EXECUTION-WORKFLOW-AUTOMATION/PLAN_*.md
        @PLAN_FEATURE.md → work-space/plans/FEATURE/PLAN_FEATURE.md
        @SUBPLAN_FEATURE_01.md → work-space/plans/FEATURE/subplans/SUBPLAN_FEATURE_01.md
        full/path/to/file.md → full/path/to/file.md
    """
    if not path_str.startswith("@"):
        # Regular path - just verify it exists
        path = Path(path_str)
        if not path.exists():
            print(f"❌ Error: {file_type} file not found: {path}")
            sys.exit(1)
        return path

    # Remove @ prefix
    shorthand = path_str[1:]

    # Check if @folder format (no .md, no /)
    if "/" not in shorthand and not shorthand.endswith(".md"):
        return resolve_folder_shortcut(shorthand)

    # @FILE_NAME.md format - search recursively
    filename = shorthand

    # Determine search directory based on file type
    if filename.startswith("PLAN_"):
        search_dirs = [Path("work-space/plans")]
    elif filename.startswith("SUBPLAN_"):
        search_dirs = [Path("work-space/plans")]
    elif filename.startswith("EXECUTION_TASK_"):
        search_dirs = [Path("work-space/plans")]
    else:
        # Generic search
        search_dirs = [Path("work-space/plans"), Path("work-space")]

    # Search recursively
    matching_files = []
    for search_dir in search_dirs:
        if search_dir.exists():
            matching_files.extend(list(search_dir.rglob(filename)))

    if not matching_files:
        print(f"❌ {file_type} file not found: @{shorthand}")
        print(f"\n   Searched in: {', '.join(str(d) for d in search_dirs)}")
        print(f"   Use full path or check filename")
        sys.exit(1)

    if len(matching_files) > 1:
        print(f"⚠️  Multiple files match '@{shorthand}':")
        for f in matching_files:
            print(f"   - {f}")
        print("\n   Use full path to disambiguate")
        sys.exit(1)

    return matching_files[0]


def copy_to_clipboard_safe(text: str, enabled: bool = True) -> bool:
    """
    Safely copy text to clipboard with error handling.

    Args:
        text: Text to copy
        enabled: Whether clipboard is enabled (default: True)

    Returns:
        True if successful, False otherwise
    """
    if not enabled:
        return False

    try:
        import pyperclip

        pyperclip.copy(text)
        return True
    except ImportError:
        # pyperclip not installed - silent fail
        return False
    except Exception:
        # Clipboard access failed - silent fail
        return False
