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

Achievement 3.1: Upgraded to structured error handling with custom exceptions
"""

import sys
from pathlib import Path
from typing import Optional, List

# Achievement 3.1: Import structured error handling
from core.libraries.error_handling import handle_errors
from LLM.scripts.generation.exceptions import (
    PlanNotFoundError,
    InvalidPathError,
    format_error_with_suggestions,
)


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
        PlanNotFoundError: If folder not found, multiple matches, or no PLAN file
        InvalidPathError: If plans directory doesn't exist

    Examples:
        @RESTORE → work-space/plans/RESTORE-EXECUTION-WORKFLOW-AUTOMATION/PLAN_*.md
        @GRAPHRAG → work-space/plans/GRAPHRAG-OBSERVABILITY-EXCELLENCE/PLAN_*.md
    """
    # Achievement 3.1: Validate folder_name is not empty
    if not folder_name or not folder_name.strip():
        raise PlanNotFoundError(
            plan_name="(empty)",
            searched_paths=[Path("work-space/plans")],
            available_plans=[],
        )

    plans_dir = Path("work-space/plans")

    # Achievement 3.1: Use InvalidPathError instead of print + sys.exit
    if not plans_dir.exists():
        raise InvalidPathError(
            path=plans_dir,
            reason="directory does not exist",
            path_type="plans directory",
        )

    # Find folders containing the name (case-insensitive partial match)
    matching_folders = []
    for folder in plans_dir.iterdir():
        if folder.is_dir() and folder_name.upper() in folder.name.upper():
            matching_folders.append(folder)

    # Achievement 3.1: Use PlanNotFoundError with available plans
    if not matching_folders:
        available_plans = [f.name for f in sorted(plans_dir.iterdir()) if f.is_dir()]
        raise PlanNotFoundError(
            plan_name=folder_name,
            searched_paths=[plans_dir],
            available_plans=available_plans,
        )

    # Achievement 3.1: Ambiguous folder match - provide clear context
    if len(matching_folders) > 1:
        from core.libraries.error_handling import ApplicationError

        raise ApplicationError(
            f"Multiple folders match '@{folder_name}'",
            context={
                "folder_name": folder_name,
                "matches": [f.name for f in matching_folders],
                "suggestions": [
                    "Use more specific name (more characters from folder name)",
                    "Use full path instead of @folder shortcut",
                    f"Example: work-space/plans/{matching_folders[0].name}/PLAN_*.md",
                ],
            },
        )

    # Find PLAN file in folder
    folder = matching_folders[0]
    plan_files = list(folder.glob("PLAN_*.md"))

    # Achievement 3.1: No PLAN file found
    if not plan_files:
        raise PlanNotFoundError(
            plan_name=folder.name,
            searched_paths=[folder],
            available_plans=[],
        )

    # Achievement 3.1: Multiple PLAN files (ambiguous)
    if len(plan_files) > 1:
        from core.libraries.error_handling import ApplicationError

        raise ApplicationError(
            f"Multiple PLAN files found in {folder.name}",
            context={
                "folder": folder.name,
                "files": [f.name for f in plan_files],
                "suggestions": [
                    "This folder should only have one PLAN_*.md file",
                    "Remove duplicate PLAN files",
                    "Or use full path to specify which one",
                ],
            },
        )

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
        InvalidPathError: If path not found
        PlanNotFoundError: If @folder or @FILE.md not found
        ApplicationError: If multiple matches found

    Examples:
        @RESTORE → work-space/plans/RESTORE-EXECUTION-WORKFLOW-AUTOMATION/PLAN_*.md
        @PLAN_FEATURE.md → work-space/plans/FEATURE/PLAN_FEATURE.md
        @SUBPLAN_FEATURE_01.md → work-space/plans/FEATURE/subplans/SUBPLAN_FEATURE_01.md
        full/path/to/file.md → full/path/to/file.md
    """
    # Achievement 3.1: Handle regular paths with InvalidPathError
    if not path_str.startswith("@"):
        # Regular path - just verify it exists
        path = Path(path_str)
        if not path.exists():
            raise InvalidPathError(
                path=path,
                reason="file does not exist",
                path_type=file_type,
            )
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

    # Achievement 3.1: File not found - use appropriate exception
    if not matching_files:
        from core.libraries.error_handling import ApplicationError

        raise ApplicationError(
            f"{file_type} file not found: @{shorthand}",
            context={
                "filename": shorthand,
                "file_type": file_type,
                "searched_paths": [str(d) for d in search_dirs],
                "suggestions": [
                    "Check filename spelling",
                    f"Search manually: find work-space/plans -name '{filename}'",
                    "Use full path instead of @ shortcut",
                    "List available files: ls work-space/plans/*/",
                ],
            },
        )

    # Achievement 3.1: Multiple matches - provide clear guidance
    if len(matching_files) > 1:
        from core.libraries.error_handling import ApplicationError

        raise ApplicationError(
            f"Multiple files match '@{shorthand}'",
            context={
                "filename": shorthand,
                "matches": [str(f) for f in matching_files],
                "suggestions": [
                    "Use full path to specify which file:",
                ]
                + [f"  {f}" for f in matching_files],
            },
        )

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
