#!/usr/bin/env python3
"""
Structure Detection - Detect workspace structure type (flat vs nested)

This module provides functions to detect whether the workspace uses a flat
or nested structure, enabling scripts to work with both during migration.
"""

from pathlib import Path
from typing import Literal


def detect_structure(plan_path: Path) -> Literal["flat", "nested"]:
    """
    Detect if workspace uses flat or nested structure.

    Structure detection logic:
    - Nested: PLAN file is in a folder that contains a "subplans" subdirectory
    - Flat: PLAN file is in work-space/plans/ with no subplans subdirectory

    Args:
        plan_path: Path to PLAN file (e.g., work-space/plans/PLAN_FEATURE.md
                   or work-space/plans/PLAN_FEATURE/PLAN_FEATURE.md)

    Returns:
        "nested" if nested structure detected, "flat" otherwise

    Examples:
        >>> detect_structure(Path("work-space/plans/PLAN_TEST/PLAN_TEST.md"))
        "nested"  # if subplans/ folder exists

        >>> detect_structure(Path("work-space/plans/PLAN_TEST.md"))
        "flat"  # if no subplans/ folder in parent
    """
    plan_folder = plan_path.parent

    # Check if subplans folder exists in PLAN folder
    subplans_folder = plan_folder / "subplans"
    if subplans_folder.exists() and subplans_folder.is_dir():
        return "nested"

    # Default to flat structure (backward compatibility)
    return "flat"
