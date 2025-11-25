"""
Batch SUBPLAN Creation Module

Enables batch creation of SUBPLANs for multiple achievements at the same dependency
level, providing safety features (dry-run, confirmation, rollback) to prevent errors
and ensure reliable parallel workflow orchestration.

Usage:
    from LLM.scripts.generation.batch_subplan import batch_create_subplans

    # Batch create SUBPLANs
    result = batch_create_subplans(plan_path, dry_run=False)
    print(result)

    # Dry-run mode (preview only)
    result = batch_create_subplans(plan_path, dry_run=True)
    print(result)
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from LLM.scripts.generation.plan_parser import PlanParser


@dataclass
class BatchResult:
    """Result of batch SUBPLAN creation."""

    created: List[Path] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    errors: List[Tuple[str, str]] = field(default_factory=list)  # (achievement_id, error_msg)

    def __str__(self) -> str:
        """Format batch result as string."""
        lines = []

        if self.created:
            lines.append(f"✅ Created {len(self.created)} SUBPLANs:")
            for path in self.created:
                lines.append(f"  - {path.name}")

        if self.skipped:
            lines.append(f"\n⏭️  Skipped {len(self.skipped)} (already exist):")
            for ach_id in self.skipped:
                lines.append(f"  - Achievement {ach_id}")

        if self.errors:
            lines.append(f"\n❌ Errors ({len(self.errors)}):")
            for ach_id, error in self.errors:
                lines.append(f"  - Achievement {ach_id}: {error}")

        return "\n".join(lines)


def calculate_dependency_level(
    achievement_id: str, achievements: List[Dict], memo: Optional[Dict[str, int]] = None
) -> int:
    """
    Calculate dependency level for an achievement recursively with memoization.

    Level 0: No dependencies
    Level 1: Depends only on level 0 achievements
    Level 2: Depends on level 1 achievements
    Etc.

    Args:
        achievement_id: Achievement ID (e.g., "1.1")
        achievements: List of achievement dicts from parallel.json
        memo: Memoization dict for caching results

    Returns:
        Dependency level (0, 1, 2, ...)

    Example:
        >>> achievements = [
        ...     {"achievement_id": "1.1", "dependencies": []},
        ...     {"achievement_id": "1.2", "dependencies": ["1.1"]},
        ...     {"achievement_id": "1.3", "dependencies": ["1.2"]}
        ... ]
        >>> calculate_dependency_level("1.1", achievements)
        0
        >>> calculate_dependency_level("1.2", achievements)
        1
        >>> calculate_dependency_level("1.3", achievements)
        2
    """
    if memo is None:
        memo = {}

    # Return cached result if available
    if achievement_id in memo:
        return memo[achievement_id]

    # Find achievement in list
    ach = None
    for a in achievements:
        if a.get("achievement_id") == achievement_id:
            ach = a
            break

    if not ach:
        # Achievement not found, assume level 0
        memo[achievement_id] = 0
        return 0

    dependencies = ach.get("dependencies", [])

    # No dependencies = level 0
    if not dependencies:
        memo[achievement_id] = 0
        return 0

    # Calculate level = max(dependency levels) + 1
    dep_levels = []
    for dep_id in dependencies:
        dep_level = calculate_dependency_level(dep_id, achievements, memo)
        dep_levels.append(dep_level)

    level = max(dep_levels) + 1
    memo[achievement_id] = level
    return level


def filter_by_dependency_level(achievements: List[Dict], level: int = 0) -> List[Dict]:
    """
    Filter achievements by dependency level.

    Algorithm:
    - Level 0: No dependencies (can run immediately)
    - Level 1: Depends only on level 0 achievements
    - Level 2: Depends on level 1 achievements
    - Etc.

    Args:
        achievements: List of achievement dicts from parallel.json
        level: Dependency level to filter (default: 0)

    Returns:
        List of achievements at specified level

    Example:
        >>> achievements = [
        ...     {"achievement_id": "1.1", "dependencies": []},
        ...     {"achievement_id": "1.2", "dependencies": ["1.1"]},
        ...     {"achievement_id": "1.3", "dependencies": []}
        ... ]
        >>> level_0 = filter_by_dependency_level(achievements, level=0)
        >>> print([a["achievement_id"] for a in level_0])
        ['1.1', '1.3']
    """
    filtered = []
    memo = {}  # Memoization for efficiency

    for ach in achievements:
        ach_id = ach.get("achievement_id")
        if not ach_id:
            continue

        ach_level = calculate_dependency_level(ach_id, achievements, memo)
        if ach_level == level:
            filtered.append(ach)

    return filtered


def detect_missing_subplans(plan_path: Path, achievements: List[Dict]) -> List[Dict]:
    """
    Detect which achievements are missing SUBPLANs.

    Checks for file: subplans/SUBPLAN_{PLAN_NAME}_{ACHIEVEMENT_ID}.md

    Args:
        plan_path: Path to PLAN directory (or PLAN file)
        achievements: List of achievement dicts

    Returns:
        List of achievements without SUBPLANs

    Example:
        >>> missing = detect_missing_subplans(plan_path, achievements)
        >>> print(f"Missing SUBPLANs: {len(missing)}")
    """
    # Get plan directory
    if plan_path.is_file():
        plan_dir = plan_path.parent
    else:
        plan_dir = plan_path

    # Extract plan name from directory or PLAN file
    plan_files = list(plan_dir.glob("PLAN_*.md"))
    if not plan_files:
        # Try to get from parent if we're in a subdirectory
        plan_files = list(plan_dir.parent.glob("PLAN_*.md"))

    if not plan_files:
        raise FileNotFoundError(f"No PLAN_*.md file found in {plan_dir}")

    plan_file = plan_files[0]
    plan_name = plan_file.stem.replace("PLAN_", "")

    # Check for subplans directory
    subplans_dir = plan_dir / "subplans"
    if not subplans_dir.exists():
        # All are missing if directory doesn't exist
        return achievements.copy()

    missing = []
    for ach in achievements:
        ach_id = ach.get("achievement_id", "")
        if not ach_id:
            continue

        # Format: SUBPLAN_{PLAN_NAME}_{ACHIEVEMENT_ID}.md
        # Achievement ID "1.1" becomes "11"
        ach_id_formatted = ach_id.replace(".", "")
        subplan_filename = f"SUBPLAN_{plan_name}_{ach_id_formatted}.md"
        subplan_path = subplans_dir / subplan_filename

        if not subplan_path.exists():
            missing.append(ach)

    return missing


def show_batch_preview(
    achievements: List[Dict], plan_name: str, level: Optional[int] = None
) -> None:
    """
    Show preview of what would be created in batch.

    Args:
        achievements: List of achievements to create SUBPLANs for
        plan_name: Name of the plan
        level: Optional dependency level number

    Example:
        >>> show_batch_preview(achievements, "MY-PLAN", level=6)
        📋 Batch SUBPLAN Creation Preview
        ================================================================================
        Plan: MY-PLAN
        Level: 6 (next incomplete level)
        Achievements to create: 3

        SUBPLANs that will be created:
          1. Achievement 3.1 - SUBPLAN_MY-PLAN_31.md
          2. Achievement 3.2 - SUBPLAN_MY-PLAN_32.md
          3. Achievement 3.3 - SUBPLAN_MY-PLAN_33.md
        ================================================================================
    """
    print("\n" + "=" * 80)
    print("📋 Batch SUBPLAN Creation Preview")
    print("=" * 80)
    print(f"Plan: {plan_name}")
    if level is not None:
        print(f"Level: {level} (next incomplete level)")
    print(f"Achievements to create: {len(achievements)}")
    print()
    print("SUBPLANs that will be created:")

    for i, ach in enumerate(achievements, 1):
        ach_id = ach.get("achievement_id", "?")
        ach_id_formatted = ach_id.replace(".", "")
        subplan_filename = f"SUBPLAN_{plan_name}_{ach_id_formatted}.md"
        print(f"  {i}. Achievement {ach_id} - {subplan_filename}")

    print("=" * 80)


def confirm_batch_creation(achievements: List[Dict]) -> bool:
    """
    Ask user to confirm batch creation.

    Args:
        achievements: List of achievements to create

    Returns:
        True if user confirms, False otherwise

    Example:
        >>> if confirm_batch_creation(achievements):
        ...     # Proceed with creation
    """
    print()
    response = (
        input(f"Proceed with batch creation of {len(achievements)} SUBPLANs? (y/N): ")
        .strip()
        .lower()
    )
    return response in ["y", "yes"]


def create_subplan_file(plan_path: Path, achievement_id: str, plan_data: Dict) -> Path:
    """
    Create a single SUBPLAN file.

    Note: This is a placeholder that generates a prompt for SUBPLAN creation.
    The actual SUBPLAN content should be generated by an LLM using the prompt.

    Args:
        plan_path: Path to PLAN directory (or PLAN file)
        achievement_id: Achievement ID (e.g., "1.1")
        plan_data: Parsed PLAN data

    Returns:
        Path to created SUBPLAN file

    Raises:
        ValueError: If SUBPLAN creation fails
    """
    # Get plan directory
    if plan_path.is_file():
        plan_dir = plan_path.parent
        plan_file = plan_path
    else:
        plan_dir = plan_path
        plan_files = list(plan_dir.glob("PLAN_*.md"))
        if not plan_files:
            raise FileNotFoundError(f"No PLAN_*.md file found in {plan_dir}")
        plan_file = plan_files[0]

    plan_name = plan_file.stem.replace("PLAN_", "")

    # Format achievement ID for filename
    ach_id_formatted = achievement_id.replace(".", "")

    # Create subplans directory if it doesn't exist
    subplans_dir = plan_dir / "subplans"
    subplans_dir.mkdir(parents=True, exist_ok=True)

    # SUBPLAN filename
    subplan_filename = f"SUBPLAN_{plan_name}_{ach_id_formatted}.md"
    subplan_path = subplans_dir / subplan_filename

    # Generate placeholder SUBPLAN (to be filled by LLM)
    placeholder_content = f"""# SUBPLAN: Achievement {achievement_id}

**PLAN**: {plan_name}  
**Achievement**: {achievement_id}  
**Status**: 📋 Design Phase (Batch Created - Needs Content)

---

## 🎯 Objective

[TO BE FILLED: Objective from PLAN Achievement {achievement_id}]

---

## 📦 Deliverables

[TO BE FILLED: List of deliverables]

---

## 🔧 Approach

[TO BE FILLED: Approach and phases]

---

## 🔄 Execution Strategy

[TO BE FILLED: Single or multiple executions?]

---

## 🧪 Testing Strategy

[TO BE FILLED: Testing approach]

---

## 📊 Expected Results

[TO BE FILLED: Success criteria]

---

**Status**: 📋 Placeholder Created (Batch Mode)  
**Next Step**: Fill in SUBPLAN content using generate_subplan_prompt.py  
"""

    # Write placeholder SUBPLAN
    with open(subplan_path, "w", encoding="utf-8") as f:
        f.write(placeholder_content)

    return subplan_path


def find_next_incomplete_level(plan_path: Path, achievements: List[Dict]) -> Optional[int]:
    """
    Find the next incomplete dependency level (achievements with missing SUBPLANs).

    This auto-detects which level to batch create, starting from level 0 and moving up.

    Args:
        plan_path: Path to PLAN directory
        achievements: List of achievement dicts

    Returns:
        Next incomplete level number, or None if all complete

    Example:
        >>> level = find_next_incomplete_level(plan_path, achievements)
        >>> if level is not None:
        ...     print(f"Next incomplete level: {level}")
    """
    # Calculate all levels
    memo = {}
    max_level = 0
    for ach in achievements:
        ach_id = ach.get("achievement_id")
        if ach_id:
            level = calculate_dependency_level(ach_id, achievements, memo)
            max_level = max(max_level, level)

    # Check each level from 0 to max_level
    for level in range(max_level + 1):
        level_achievements = filter_by_dependency_level(achievements, level=level)
        if level_achievements:
            missing = detect_missing_subplans(plan_path, level_achievements)
            if missing:
                return level

    return None  # All levels complete


def batch_create_subplans(
    plan_path: Path,
    dry_run: bool = False,
    parallel_json_path: Optional[Path] = None,
    achievements: Optional[List[Dict]] = None,
    skip_confirmation: bool = False,
) -> BatchResult:
    """
    Batch create SUBPLANs for achievements in parallel.json.

    Two modes:
    - Auto mode (achievements=None): Auto-detect next incomplete level
    - Manual mode (achievements provided): Use specific achievements

    Steps:
    1. Load parallel.json
    2. Get achievements (provided or auto-detect)
    3. Detect missing SUBPLANs
    4. Show preview (unless skip_confirmation)
    5. Confirm with user (unless dry-run or skip_confirmation)
    6. Create SUBPLANs

    Args:
        plan_path: Path to PLAN directory or PLAN file
        dry_run: If True, preview without creating files
        parallel_json_path: Optional path to parallel.json (auto-detect if None)
        achievements: Optional list of specific achievements to create SUBPLANs for
        skip_confirmation: If True, skip preview and confirmation

    Returns:
        BatchResult with created SUBPLANs, skipped, and errors

    Example:
        >>> # Auto mode
        >>> result = batch_create_subplans(Path("work-space/plans/MY-PLAN"))
        >>>
        >>> # Manual mode (from handler)
        >>> result = batch_create_subplans(
        ...     Path("work-space/plans/MY-PLAN"),
        ...     achievements=specific_achievements,
        ...     skip_confirmation=True
        ... )
    """
    result = BatchResult()

    # Get plan directory
    if plan_path.is_file():
        plan_dir = plan_path.parent
        plan_file = plan_path
    else:
        plan_dir = plan_path
        plan_files = list(plan_dir.glob("PLAN_*.md"))
        if not plan_files:
            result.errors.append(("N/A", f"No PLAN_*.md file found in {plan_dir}"))
            return result
        plan_file = plan_files[0]

    plan_name = plan_file.stem.replace("PLAN_", "")

    # Load parallel.json
    if parallel_json_path is None:
        parallel_json_path = plan_dir / "parallel.json"

    if not parallel_json_path.exists():
        result.errors.append(("N/A", f"parallel.json not found at {parallel_json_path}"))
        return result

    try:
        with open(parallel_json_path, "r", encoding="utf-8") as f:
            parallel_data = json.load(f)
    except json.JSONDecodeError as e:
        result.errors.append(("N/A", f"Invalid JSON in parallel.json: {e}"))
        return result

    all_achievements = parallel_data.get("achievements", [])
    if not all_achievements:
        result.errors.append(("N/A", "No achievements found in parallel.json"))
        return result

    # Use provided achievements or auto-detect
    if achievements is not None:
        # Manual mode: use provided achievements
        level_achievements = achievements
        # Calculate level from first achievement
        if level_achievements:
            memo = {}
            next_level = calculate_dependency_level(
                level_achievements[0].get("achievement_id"), all_achievements, memo
            )
        else:
            next_level = 0
    else:
        # Auto-detect mode: find next incomplete level
        next_level = find_next_incomplete_level(plan_dir, all_achievements)

        if next_level is None:
            print("✅ All SUBPLANs already exist for all levels")
            return result

        # Filter achievements at next incomplete level
        level_achievements = filter_by_dependency_level(all_achievements, level=next_level)

        if not level_achievements:
            print(f"ℹ️  No achievements at level {next_level}")
            return result

    # Detect missing SUBPLANs
    missing = detect_missing_subplans(plan_dir, level_achievements)

    if not missing:
        print(f"✅ All SUBPLANs already exist for level {next_level} achievements")
        # Add to skipped
        for ach in level_achievements:
            result.skipped.append(ach.get("achievement_id", "?"))
        return result

    # Show preview and confirm (unless skipping)
    if not skip_confirmation:
        # Show preview
        show_batch_preview(missing, plan_name, level=next_level)

        # Dry-run mode: stop here
        if dry_run:
            print("\n🔍 DRY-RUN MODE: No files created")
            return result

        # Confirm with user
        if not confirm_batch_creation(missing):
            print("❌ Batch creation cancelled")
            return result

    # Parse PLAN data
    parser = PlanParser()
    try:
        plan_data = parser.parse_plan_file(plan_file)
    except Exception as e:
        result.errors.append(("N/A", f"Failed to parse PLAN: {e}"))
        return result

    # Create SUBPLANs
    print("\n🔨 Creating SUBPLANs...")
    for ach in missing:
        ach_id = ach.get("achievement_id", "?")
        try:
            subplan_path = create_subplan_file(plan_dir, ach_id, plan_data)
            result.created.append(subplan_path)
            print(f"  ✅ Created: {subplan_path.name}")
        except Exception as e:
            result.errors.append((ach_id, str(e)))
            print(f"  ❌ Failed: {ach_id} - {e}")

    # Add skipped (already exist)
    for ach in level_achievements:
        if ach not in missing:
            result.skipped.append(ach.get("achievement_id", "?"))

    return result
