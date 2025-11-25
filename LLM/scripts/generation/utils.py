#!/usr/bin/env python3
"""
Utility Functions for Generate Prompt and Related Modules

This module provides standalone utility functions that don't fit into specific
domain modules (parsing, workflow detection, prompt building, etc.).

**Module Purpose**:
- General-purpose helper functions
- Clipboard operations
- Path resolution utilities
- Common operations used across multiple modules

**Design Philosophy**:
- Standalone functions (not class methods)
- No external dependencies on other generation modules
- Reusable across different tools
- Clear, single-purpose functions

Created: 2025-11-12
Achievement: 2.4 - Extract Parsing & Utilities Module
Achievement 3.1: Updated to use structured error handling from path_resolution
"""
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Achievement 3.1: Import from path_resolution for consistent error handling
from LLM.scripts.generation import path_resolution


@dataclass
class Achievement:
    """Achievement data structure."""

    number: str  # "0.1", "1.1"
    title: str
    goal: str
    effort: str  # "2-3 hours"
    priority: str
    section_lines: int  # Lines in achievement section


def copy_to_clipboard_safe(text: str, enabled: bool = True) -> bool:
    """
    Safely copy text to clipboard with error handling.

    Attempts to copy text to system clipboard using pyperclip.
    Handles clipboard unavailability gracefully without crashing.

    This is Achievement 0.1 feature - makes clipboard the DEFAULT behavior.
    This function is called for ALL output (prompts, errors, conflicts,
    completion messages) to enable seamless copy-paste workflow.

    **Error Handling**:
    - Catches pyperclip exceptions (clipboard unavailable)
    - Falls back gracefully (returns False, caller handles)
    - Never crashes the script

    **Design Philosophy**:
    - Clipboard should "just work" for 95% of users
    - 5% who can't use clipboard get clear message
    - Enabled by default, can be disabled with --no-clipboard

    Args:
        text: Text to copy to clipboard
        enabled: Whether clipboard is enabled (default True)

    Returns:
        bool: True if copied successfully, False otherwise

    Example:
        >>> success = copy_to_clipboard_safe("Hello World")
        >>> if success:
        ...     print("✅ Copied!")
        ✅ Copied!

        >>> copy_to_clipboard_safe("Text", enabled=False)
        False

    Tested: Yes (13 tests in test_clipboard_and_shortcuts.py)
    """
    if not enabled:
        return False

    try:
        import pyperclip

        pyperclip.copy(text)
        return True
    except Exception as e:
        print(f"\n⚠️  Could not copy to clipboard: {e}")
        print("(Output still shown below)")
        return False


def resolve_folder_shortcut(folder_name: str) -> Path:
    """
    Resolve @folder shortcut to actual PLAN path.

    Converts @FOLDER-NAME shortcuts to full PLAN file paths.
    Searches in work-space/plans/ directory for matching PLAN.

    **Search Strategy**:
    1. Try nested structure: work-space/plans/FOLDER-NAME/PLAN_*.md
    2. Try flat structure: work-space/plans/PLAN_FOLDER-NAME.md
    3. Raise error if not found in either location

    **Naming Convention**:
    - @FEATURE → work-space/plans/FEATURE/PLAN_FEATURE.md
    - Case-insensitive matching
    - Handles both nested and flat directory structures

    Args:
        folder_name: Folder name (with or without @ prefix)

    Returns:
        Path: Resolved PLAN file path

    Raises:
        PlanNotFoundError: If PLAN file not found (Achievement 3.1)
        InvalidPathError: If plans directory doesn't exist (Achievement 3.1)

    Example:
        >>> path = resolve_folder_shortcut("@PROMPT-GENERATOR-UX-AND-FOUNDATION")
        >>> print(path.name)
        "PLAN_PROMPT-GENERATOR-UX-AND-FOUNDATION.md"

        >>> path = resolve_folder_shortcut("GRAPHRAG-OBSERVABILITY")
        >>> print(path.exists())
        True

    Tested: Yes (13 tests in test_clipboard_and_shortcuts.py)

    Used by: main() (when args.plan_file starts with @ and has no .md extension)

    Achievement 3.1: Delegate to path_resolution for consistent structured error handling
    """
    # Remove @ prefix if present
    folder_name = folder_name.lstrip("@")

    # Achievement 3.1: Delegate to path_resolution module for consistent error handling
    return path_resolution.resolve_folder_shortcut(folder_name)


def get_achievement_status(ach_num: str, plan_path: Optional[Path]) -> str:
    """
    Get achievement status from filesystem (tri-state model).

    **NEW in Achievement 2.9**: Replaces binary state model with tri-state to handle
    "needs fix" scenario. This closes the feedback loop by detecting FIX_XX.md files
    and enabling fix-specific prompt generation.

    **Tri-State Model**:
    - "approved": APPROVED_XX.md exists (achievement complete, move to next)
    - "needs_fix": FIX_XX.md exists without APPROVED (fixes required, generate FIX prompt)
    - "incomplete": Neither exists (work in progress, generate standard prompt)

    **Priority**: APPROVED always overrides FIX (if both exist, return "approved")

    **State Tracking Philosophy**:
    - PLAN defines Achievement Index (structure)
    - Filesystem tracks state (APPROVED/FIX files)
    - Single source of truth: files, not markdown

    Detection Logic:
    1. Check if execution/feedbacks/ folder exists
    2. Check for APPROVED_XX.md (highest priority)
    3. Check for FIX_XX.md (second priority)
    4. Return "incomplete" if neither exists

    Part of: Feedback System (Achievement 2.5 conventions, 2.9 detection)

    Args:
        ach_num: Achievement number (e.g., "2.1")
        plan_path: Path to PLAN file (None = incomplete)

    Returns:
        str: "approved", "needs_fix", or "incomplete"

    Example:
        >>> plan_path = Path("work-space/plans/FEATURE/PLAN_FEATURE.md")
        >>> get_achievement_status("2.1", plan_path)
        "needs_fix"  # FIX_21.md exists, APPROVED_21.md doesn't

        >>> get_achievement_status("0.1", plan_path)
        "approved"  # APPROVED_01.md exists

        >>> get_achievement_status("0.3", plan_path)
        "incomplete"  # Neither APPROVED_03.md nor FIX_03.md exists

    Achievement: 2.9 - Implement FIX Feedback Detection & Prompt Generation
    """
    if not plan_path:
        return "incomplete"

    plan_folder = plan_path.parent
    feedbacks_folder = plan_folder / "execution" / "feedbacks"

    if not feedbacks_folder.exists():
        return "incomplete"

    # Convert achievement number to filename format (e.g., "2.1" -> "21")
    ach_num_clean = ach_num.replace(".", "")
    approved_file = feedbacks_folder / f"APPROVED_{ach_num_clean}.md"
    fix_file = feedbacks_folder / f"FIX_{ach_num_clean}.md"

    # Priority: APPROVED overrides FIX
    if approved_file.exists():
        return "approved"
    elif fix_file.exists():
        return "needs_fix"
    else:
        return "incomplete"


def is_achievement_complete(ach_num: str, plan_content: str, plan_path: Path = None) -> bool:
    """
    Check if achievement is complete (BACKWARD COMPATIBILITY wrapper).

    **UPDATED in Achievement 2.9**: Now wraps get_achievement_status() for backward
    compatibility. Maintains existing function signature and behavior while using
    new tri-state detection internally.

    This function exists for backward compatibility with existing code that uses
    binary True/False logic. New code should use get_achievement_status() directly
    to access tri-state model (approved/needs_fix/incomplete).

    **State Tracking Philosophy**:
    - PLAN's ONLY responsibility: Define Achievement Index (list of all achievements)
    - Filesystem's responsibility: Track completion via APPROVED_XX.md files
    - NO fallback to PLAN markdown for completion status

    Detection Logic (via get_achievement_status):
    1. Check if execution/feedbacks/ folder exists
    2. Check if APPROVED_XX.md file exists (e.g., APPROVED_21.md for Achievement 2.1)
    3. Return True if status == "approved", False otherwise

    Bug Fixes Incorporated:
        - Filesystem-only: No PLAN markdown parsing for completion
        - Single source of truth: APPROVED_XX.md files
        - Clear separation of concerns: PLAN defines, filesystem tracks
        - Tri-state detection: Handles "needs_fix" scenario (Achievement 2.9)

    Used by: workflow_detector, plan_parser, generate_prompt (legacy code)
    Part of: Feedback System (Achievement 2.5 conventions, 2.9 detection)

    Args:
        ach_num: Achievement number (e.g., "1.1")
        plan_content: Full PLAN file content (UNUSED - kept for backward compatibility)
        plan_path: Path to PLAN file (REQUIRED for filesystem check)

    Returns:
        True if APPROVED_XX.md exists (status == "approved"), False otherwise

    Example:
        >>> plan_path = Path("PLAN_FEATURE.md")
        >>> is_achievement_complete("0.1", "", plan_path)  # plan_content unused
        True  # if execution/feedbacks/APPROVED_01.md exists
        >>> is_achievement_complete("0.3", "", plan_path)
        False  # if APPROVED_03.md doesn't exist (even if FIX_03.md exists)

    Moved from: generate_prompt.py (Achievement 2.6 - Integration)
    Updated: Achievement 2.9 - Now wraps get_achievement_status()
    """
    status = get_achievement_status(ach_num, plan_path)
    return status == "approved"
