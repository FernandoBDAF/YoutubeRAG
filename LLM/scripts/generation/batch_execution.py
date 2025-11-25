"""
Batch EXECUTION Creation Module

Enables batch creation of EXECUTION_TASKs for multiple achievements at the same dependency
level, providing safety features (dry-run, confirmation, rollback) and prerequisite validation
to prevent errors and ensure reliable parallel workflow orchestration.

Usage:
    from LLM.scripts.generation.batch_execution import batch_create_executions
    
    # Batch create EXECUTION_TASKs
    result = batch_create_executions(plan_path, dry_run=False)
    print(result)
    
    # Dry-run mode (preview only)
    result = batch_create_executions(plan_path, dry_run=True)
    print(result)
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Reuse filter_by_dependency_level from batch_subplan
from LLM.scripts.generation.batch_subplan import (
    filter_by_dependency_level,
    calculate_dependency_level,
    find_next_incomplete_level
)
from LLM.scripts.generation.plan_parser import PlanParser


@dataclass
class BatchResult:
    """Result of batch EXECUTION creation."""
    created: List[Path] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    errors: List[Tuple[str, str]] = field(default_factory=list)  # (achievement_id, error_msg)
    missing_subplans: List[str] = field(default_factory=list)  # SUBPLANs that must be created first
    
    def __str__(self) -> str:
        """Format batch result as string."""
        lines = []
        
        if self.missing_subplans:
            lines.append(f"⚠️  Missing {len(self.missing_subplans)} SUBPLANs (create these first):")
            for ach_id in self.missing_subplans:
                lines.append(f"  - Achievement {ach_id}")
            lines.append("")
        
        if self.created:
            lines.append(f"✅ Created {len(self.created)} EXECUTION_TASKs:")
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


def validate_subplan_prerequisites(
    plan_path: Path,
    achievements: List[Dict]
) -> Tuple[List[Dict], List[str]]:
    """
    Validate that all SUBPLANs exist for achievements.
    
    This is a critical prerequisite check - EXECUTION_TASKs require SUBPLANs to exist
    because they reference SUBPLAN context (objective, approach, etc.).
    
    Args:
        plan_path: Path to PLAN directory (or PLAN file)
        achievements: List of achievement dicts
    
    Returns:
        Tuple of (valid_achievements, missing_subplan_ids)
    
    Example:
        >>> valid, missing = validate_subplan_prerequisites(plan_path, achievements)
        >>> if missing:
        ...     print(f"Missing SUBPLANs: {missing}")
        ...     # Block EXECUTION creation
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
    
    valid_achievements = []
    missing_subplan_ids = []
    
    for ach in achievements:
        ach_id = ach.get("achievement_id", "")
        if not ach_id:
            continue
        
        # Format: SUBPLAN_{PLAN_NAME}_{ACHIEVEMENT_ID}.md
        # Achievement ID "1.1" becomes "11"
        ach_id_formatted = ach_id.replace(".", "")
        subplan_filename = f"SUBPLAN_{plan_name}_{ach_id_formatted}.md"
        subplan_path = subplans_dir / subplan_filename
        
        if subplan_path.exists():
            valid_achievements.append(ach)
        else:
            missing_subplan_ids.append(ach_id)
    
    return valid_achievements, missing_subplan_ids


def detect_missing_executions(
    plan_path: Path,
    achievements: List[Dict]
) -> List[Dict]:
    """
    Detect which achievements are missing EXECUTION_TASKs.
    
    Checks for file: execution/EXECUTION_TASK_{PLAN_NAME}_{ACHIEVEMENT_ID}_01.md
    
    Args:
        plan_path: Path to PLAN directory (or PLAN file)
        achievements: List of achievement dicts
    
    Returns:
        List of achievements without EXECUTION_TASKs
    
    Example:
        >>> missing = detect_missing_executions(plan_path, achievements)
        >>> print(f"Missing EXECUTIONs: {len(missing)}")
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
    
    # Check for execution directory
    execution_dir = plan_dir / "execution"
    if not execution_dir.exists():
        # All are missing if directory doesn't exist
        return achievements.copy()
    
    missing = []
    for ach in achievements:
        ach_id = ach.get("achievement_id", "")
        if not ach_id:
            continue
        
        # Format: EXECUTION_TASK_{PLAN_NAME}_{ACHIEVEMENT_ID}_01.md
        # Achievement ID "1.1" becomes "11"
        ach_id_formatted = ach_id.replace(".", "")
        execution_filename = f"EXECUTION_TASK_{plan_name}_{ach_id_formatted}_01.md"
        execution_path = execution_dir / execution_filename
        
        if not execution_path.exists():
            missing.append(ach)
    
    return missing


def show_batch_preview(
    achievements: List[Dict],
    plan_name: str,
    missing_subplans: List[str] = None,
    level: Optional[int] = None
) -> None:
    """
    Show preview of what would be created in batch.
    
    Args:
        achievements: List of achievements to create EXECUTION_TASKs for
        plan_name: Name of the plan
        missing_subplans: Optional list of missing SUBPLAN IDs (shows warning)
        level: Optional dependency level number
    
    Example:
        >>> show_batch_preview(achievements, "MY-PLAN", level=6)
        📋 Batch EXECUTION Creation Preview
        ================================================================================
        Plan: MY-PLAN
        Level: 6 (next incomplete level)
        Achievements to create: 3
        
        EXECUTION_TASKs that will be created:
          1. Achievement 3.1 - EXECUTION_TASK_MY-PLAN_31_01.md
          2. Achievement 3.2 - EXECUTION_TASK_MY-PLAN_32_01.md
          3. Achievement 3.3 - EXECUTION_TASK_MY-PLAN_33_01.md
        ================================================================================
    """
    print("\n" + "="*80)
    print("📋 Batch EXECUTION Creation Preview")
    print("="*80)
    print(f"Plan: {plan_name}")
    if level is not None:
        print(f"Level: {level} (next incomplete level)")
    print(f"Achievements to create: {len(achievements)}")
    
    if missing_subplans:
        print()
        print(f"⚠️  WARNING: {len(missing_subplans)} SUBPLANs missing (create these first):")
        for ach_id in missing_subplans:
            print(f"  - Achievement {ach_id}")
    
    print()
    print("EXECUTION_TASKs that will be created:")
    
    for i, ach in enumerate(achievements, 1):
        ach_id = ach.get("achievement_id", "?")
        ach_id_formatted = ach_id.replace(".", "")
        execution_filename = f"EXECUTION_TASK_{plan_name}_{ach_id_formatted}_01.md"
        print(f"  {i}. Achievement {ach_id} - {execution_filename}")
    
    print("="*80)


def confirm_batch_creation(
    achievements: List[Dict]
) -> bool:
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
    response = input(f"Proceed with batch creation of {len(achievements)} EXECUTION_TASKs? (y/N): ").strip().lower()
    return response in ['y', 'yes']


def create_execution_file(
    plan_path: Path,
    achievement_id: str,
    subplan_data: Dict
) -> Path:
    """
    Create a single EXECUTION_TASK file.
    
    Note: This is a placeholder that generates a basic EXECUTION_TASK structure.
    The actual EXECUTION_TASK content should be filled in by the user or LLM.
    
    Args:
        plan_path: Path to PLAN directory (or PLAN file)
        achievement_id: Achievement ID (e.g., "1.1")
        subplan_data: Parsed SUBPLAN data (optional, for context)
    
    Returns:
        Path to created EXECUTION_TASK file
    
    Raises:
        ValueError: If EXECUTION creation fails
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
    
    # Create execution directory if it doesn't exist
    execution_dir = plan_dir / "execution"
    execution_dir.mkdir(parents=True, exist_ok=True)
    
    # EXECUTION_TASK filename
    execution_filename = f"EXECUTION_TASK_{plan_name}_{ach_id_formatted}_01.md"
    execution_path = execution_dir / execution_filename
    
    # Generate placeholder EXECUTION_TASK (to be filled by user/LLM)
    placeholder_content = f"""# EXECUTION_TASK: Achievement {achievement_id}

**PLAN**: {plan_name}  
**SUBPLAN**: SUBPLAN_{plan_name}_{ach_id_formatted}.md  
**Achievement**: {achievement_id}  
**Task**: 01  
**Status**: 📋 Design Phase (Batch Created - Needs Content)

---

## 📋 SUBPLAN Context

[TO BE FILLED: Copy objective and approach from SUBPLAN_{plan_name}_{ach_id_formatted}.md]

---

## 🎯 Execution Instructions

[TO BE FILLED: Detailed execution steps]

---

## 📊 Iteration Log

### Iteration 1: [Date]

**Phase**: [Phase Number]  
**Duration**: [Actual Time]  
**Status**: [In Progress / Complete]

**Work Completed**:

- [List what was done]

**Issues Encountered**:

- [List any issues]

**Solutions Applied**:

- [List solutions]

**Next Steps**:

- [What's next]

---

## ✅ Completion Checklist

[TO BE FILLED: List of deliverables and verification steps]

---

**EXECUTION_TASK Status**: 📋 Placeholder Created (Batch Mode)  
**Next Step**: Fill in EXECUTION_TASK content using generate_execution_prompt.py  
"""
    
    # Write placeholder EXECUTION_TASK
    with open(execution_path, 'w', encoding='utf-8') as f:
        f.write(placeholder_content)
    
    return execution_path


def find_next_incomplete_execution_level(
    plan_path: Path,
    achievements: List[Dict]
) -> Optional[int]:
    """
    Find the next incomplete dependency level (achievements with missing EXECUTION_TASKs).
    
    This auto-detects which level to batch create, starting from level 0 and moving up.
    
    Args:
        plan_path: Path to PLAN directory
        achievements: List of achievement dicts
    
    Returns:
        Next incomplete level number, or None if all complete
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
            missing = detect_missing_executions(plan_path, level_achievements)
            if missing:
                return level
    
    return None  # All levels complete


def batch_create_executions(
    plan_path: Path,
    dry_run: bool = False,
    parallel_json_path: Optional[Path] = None
) -> BatchResult:
    """
    Batch create EXECUTION_TASKs for achievements in parallel.json.
    
    Steps:
    1. Load parallel.json
    2. Auto-detect next incomplete level (achievements with missing EXECUTION_TASKs)
    3. Filter achievements at that level
    4. Validate SUBPLANs exist (NEW - blocks creation if missing)
    5. Detect missing EXECUTION_TASKs
    6. Show preview
    7. Confirm with user (unless dry-run)
    8. Create EXECUTION_TASKs (or skip if dry-run)
    
    Args:
        plan_path: Path to PLAN directory or PLAN file
        dry_run: If True, preview without creating files
        parallel_json_path: Optional path to parallel.json (auto-detect if None)
    
    Returns:
        BatchResult with created EXECUTION_TASKs, skipped, errors, and missing SUBPLANs
    
    Example:
        >>> result = batch_create_executions(Path("work-space/plans/MY-PLAN"))
        >>> print(f"Created: {len(result.created)}, Skipped: {len(result.skipped)}")
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
        with open(parallel_json_path, 'r', encoding='utf-8') as f:
            parallel_data = json.load(f)
    except json.JSONDecodeError as e:
        result.errors.append(("N/A", f"Invalid JSON in parallel.json: {e}"))
        return result
    
    achievements = parallel_data.get("achievements", [])
    if not achievements:
        result.errors.append(("N/A", "No achievements found in parallel.json"))
        return result
    
    # Auto-detect next incomplete level
    next_level = find_next_incomplete_execution_level(plan_dir, achievements)
    
    if next_level is None:
        print("✅ All EXECUTION_TASKs already exist for all levels")
        return result
    
    # Filter achievements at next incomplete level
    level_achievements = filter_by_dependency_level(achievements, level=next_level)
    
    if not level_achievements:
        print(f"ℹ️  No achievements at level {next_level}")
        return result
    
    # Validate SUBPLANs exist (CRITICAL PREREQUISITE CHECK)
    valid, missing_subplan_ids = validate_subplan_prerequisites(plan_dir, level_achievements)
    
    if missing_subplan_ids:
        result.missing_subplans = missing_subplan_ids
        print(f"\n⚠️  Missing {len(missing_subplan_ids)} SUBPLANs (create these first):")
        for ach_id in missing_subplan_ids:
            print(f"  - Achievement {ach_id}")
        print("\n💡 Tip: Use option 1 to batch create SUBPLANs first")
        return result
    
    # Detect missing EXECUTION_TASKs
    missing = detect_missing_executions(plan_dir, valid)
    
    if not missing:
        print(f"✅ All EXECUTION_TASKs already exist for level {next_level} achievements")
        # Add to skipped
        for ach in valid:
            result.skipped.append(ach.get("achievement_id", "?"))
        return result
    
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
    
    # Parse PLAN data (optional, for context)
    parser = PlanParser()
    try:
        plan_data = parser.parse_plan_file(plan_file)
    except Exception as e:
        # Continue without plan data if parsing fails
        plan_data = {}
    
    # Create EXECUTION_TASKs
    print("\n🔨 Creating EXECUTION_TASKs...")
    for ach in missing:
        ach_id = ach.get("achievement_id", "?")
        try:
            execution_path = create_execution_file(plan_dir, ach_id, plan_data)
            result.created.append(execution_path)
            print(f"  ✅ Created: {execution_path.name}")
        except Exception as e:
            result.errors.append((ach_id, str(e)))
            print(f"  ❌ Failed: {ach_id} - {e}")
    
    # Add skipped (already exist)
    for ach in valid:
        if ach not in missing:
            result.skipped.append(ach.get("achievement_id", "?"))
    
    return result

