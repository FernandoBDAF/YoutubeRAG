#!/usr/bin/env python3
"""
Status Detection Script for parallel.json Files

This script derives achievement status from the filesystem (read-only).
Status is never persisted to parallel.json - it's computed at runtime.

Usage:
    python get_parallel_status.py <parallel.json>
    python get_parallel_status.py <parallel.json> --format json

Created: 2025-11-13
Achievement: 1.3 - Validation Script Created
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict


def get_achievement_status_from_filesystem(
    achievement_id: str, plan_name: str, workspace_root: Path
) -> str:
    """
    Derive achievement status from filesystem (read-only).

    Follows filesystem-first philosophy: status is derived, not persisted.

    Status priority order (check in order, return first match):
    1. APPROVED file exists → "complete"
    2. FIX file exists → "failed"
    3. EXECUTION_TASK file exists → "execution_created"
    4. SUBPLAN file exists → "subplan_created"
    5. SKIPPED file exists → "skipped"
    6. None of above → "not_started"

    Args:
        achievement_id: Achievement ID (e.g., "1.1")
        plan_name: PLAN name (e.g., "PARALLEL-EXECUTION-AUTOMATION")
        workspace_root: Path to workspace root

    Returns:
        Status string: "not_started", "subplan_created", "execution_created",
                       "complete", "failed", "skipped"
    """
    # Convert achievement ID to file format (1.1 → 11)
    ach_num = achievement_id.replace(".", "")

    # Build paths
    plan_dir = workspace_root / "work-space" / "plans" / plan_name

    # Check for APPROVED file (terminal state - highest priority)
    approved_path = plan_dir / "execution" / "feedbacks" / f"APPROVED_{ach_num}.md"
    if approved_path.exists():
        return "complete"

    # Check for FIX file
    fix_path = plan_dir / "execution" / "feedbacks" / f"FIX_{ach_num}.md"
    if fix_path.exists():
        return "failed"

    # Check for EXECUTION_TASK file (any _XX.md variant)
    execution_dir = plan_dir / "execution"
    if execution_dir.exists():
        execution_pattern = f"EXECUTION_TASK_{plan_name}_{ach_num}_*.md"
        execution_files = list(execution_dir.glob(execution_pattern))
        if execution_files:
            return "execution_created"

    # Check for SUBPLAN file
    subplan_path = plan_dir / "subplans" / f"SUBPLAN_{plan_name}_{ach_num}.md"
    if subplan_path.exists():
        return "subplan_created"

    # Check for SKIPPED file
    skipped_path = plan_dir / "execution" / f"SKIPPED_{ach_num}.md"
    if skipped_path.exists():
        return "skipped"

    # Default: not started
    return "not_started"


def get_parallel_status(parallel_json_path: Path) -> Dict[str, str]:
    """
    Get status for all achievements in parallel.json.

    Args:
        parallel_json_path: Path to parallel.json file

    Returns:
        Dict mapping achievement_id to status
    """
    # Load parallel.json
    with open(parallel_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    plan_name = data.get("plan_name", "UNKNOWN")

    # Infer workspace root from parallel.json location
    # Assumes parallel.json is in project root, examples/, or work-space/plans/PLAN_NAME/
    parallel_json_str = str(parallel_json_path)

    if "examples" in parallel_json_str:
        # parallel.json is in examples/ directory
        workspace_root = parallel_json_path.parent.parent
    elif "work-space/plans" in parallel_json_str or "work-space\\plans" in parallel_json_str:
        # parallel.json is in work-space/plans/PLAN_NAME/ directory
        # The path is already relative to project root, so workspace_root is current directory
        workspace_root = Path(".")
    else:
        # parallel.json is in project root
        workspace_root = parallel_json_path.parent

    # Get status for each achievement
    status_map = {}
    for ach in data.get("achievements", []):
        if "achievement_id" in ach:
            ach_id = ach["achievement_id"]
            status = get_achievement_status_from_filesystem(ach_id, plan_name, workspace_root)
            status_map[ach_id] = status

    return status_map


def enrich_parallel_json_with_status(parallel_data: Dict, workspace_root: Path) -> Dict:
    """
    Enrich parallel.json data with runtime status (read-only, not persisted).

    This creates a copy of the parallel.json data with status fields added.
    The enriched data is for display only - never write it back to the file.

    Args:
        parallel_data: Loaded parallel.json data
        workspace_root: Path to workspace root

    Returns:
        Enriched data with status fields (for display only, not for writing back)
    """
    plan_name = parallel_data.get("plan_name", "UNKNOWN")

    # Create deep copy to avoid modifying original
    enriched = json.loads(json.dumps(parallel_data))

    # Add status to each achievement
    for ach in enriched.get("achievements", []):
        if "achievement_id" in ach:
            ach_id = ach["achievement_id"]
            status = get_achievement_status_from_filesystem(ach_id, plan_name, workspace_root)
            ach["status"] = status  # Add status for display

    return enriched


def format_status_table(status_map: Dict[str, str]) -> str:
    """
    Format status map as a table.

    Args:
        status_map: Dict mapping achievement_id to status

    Returns:
        Formatted table string
    """
    if not status_map:
        return "No achievements found."

    # Status emoji mapping
    status_emoji = {
        "not_started": "⚪",
        "subplan_created": "📋",
        "execution_created": "📝",
        "in_progress": "🟡",
        "complete": "✅",
        "failed": "❌",
        "skipped": "⏭️",
    }

    lines = []
    lines.append("Achievement Status (from filesystem):")
    lines.append("=" * 50)

    for ach_id, status in sorted(status_map.items()):
        emoji = status_emoji.get(status, "❓")
        lines.append(f"{emoji} {ach_id:6s} → {status}")

    lines.append("=" * 50)

    # Add legend
    lines.append("\nLegend:")
    lines.append("  ⚪ not_started       - No files created yet")
    lines.append("  📋 subplan_created   - SUBPLAN file exists")
    lines.append("  📝 execution_created - EXECUTION_TASK file exists")
    lines.append("  ✅ complete          - APPROVED file exists")
    lines.append("  ❌ failed            - FIX file exists")
    lines.append("  ⏭️  skipped          - SKIPPED file exists")

    return "\n".join(lines)


def main():
    """CLI interface for status detection."""
    parser = argparse.ArgumentParser(
        description="Get parallel.json status from filesystem (read-only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s parallel.json
  %(prog)s examples/parallel_level1_example.json
  %(prog)s parallel.json --format json

Note:
  Status is derived from filesystem (APPROVED, FIX, SUBPLAN files).
  Status is NEVER written to parallel.json - it's computed at runtime.
        """,
    )
    parser.add_argument("parallel_json", type=Path, help="Path to parallel.json file")
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )

    args = parser.parse_args()

    # Check file exists
    if not args.parallel_json.exists():
        print(f"Error: File not found: {args.parallel_json}", file=sys.stderr)
        return 1

    # Get status
    try:
        status_map = get_parallel_status(args.parallel_json)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.parallel_json}: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Output
    if args.format == "json":
        print(json.dumps(status_map, indent=2))
    else:
        print(format_status_table(status_map))

    return 0


if __name__ == "__main__":
    sys.exit(main())
