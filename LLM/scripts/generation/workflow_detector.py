#!/usr/bin/env python3
"""
Workflow Detector Module - Filesystem-First State Detection"""
from __future__ import annotations  # Enable deferred type hint evaluation

"""

This module provides workflow state detection, conflict checking, and achievement
finding functionality for the prompt generation system.

**Filesystem-First State Tracking Philosophy**:
- PLAN's responsibility: Define Achievement Index (list of all achievements)
- Filesystem's responsibility: Track completion via APPROVED_XX.md files
- Conflicts detected between Achievement Index and filesystem only
- NO markdown parsing for state tracking (only for structure/handoff)

**Module Responsibilities**:
1. Detect workflow state (no_subplan, subplan_no_execution, active_execution, etc.)
2. Detect conflicts between Achievement Index and filesystem
3. Find next achievement using hybrid approach (handoff → status → archive → root)

**State Detection Strategy**:
- Check filesystem for SUBPLANs and EXECUTION_TASKs
- Check execution/feedbacks/ for APPROVED_XX.md files
- Use Achievement Index from PLAN as structure definition
- Ignore markdown patterns for state (filesystem is source of truth)

Created: 2025-11-12
Achievement: 2.2 - Extract Workflow Detection Module
"""

from pathlib import Path
from typing import Optional, Dict, List, TYPE_CHECKING
import re
import warnings

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from LLM.scripts.generation.utils import Achievement

# Note: Dependencies from generate_prompt are imported locally within methods
# to avoid circular import issues. These remain in generate_prompt.py as they're
# used by multiple modules:
# - Achievement (dataclass)
# - is_achievement_complete()
# - extract_handoff_section()
# - is_plan_complete()
# - get_plan_status()
# - parse_plan_file()
# - find_subplan_for_achievement()


class WorkflowDetector:
    """
    Detect workflow state using filesystem-first approach.

    This class provides methods for:
    - Detecting current workflow state from filesystem
    - Detecting conflicts between Achievement Index and filesystem
    - Finding next achievement using multiple strategies

    **State Tracking Philosophy**:
    - Filesystem is source of truth for all state
    - APPROVED_XX.md files indicate completion
    - Achievement Index in PLAN defines structure
    - Conflicts occur when filesystem and Index disagree

    **Usage**:
        detector = WorkflowDetector()
        state = detector.detect_workflow_state_filesystem(plan_path, feature, achievement)
        conflict = detector.detect_plan_filesystem_conflict(plan_path, feature, achievement, content)
        next_ach = detector.find_next_achievement_hybrid(plan_path, feature, achievements, archive)
    """

    def __init__(self):
        """Initialize WorkflowDetector (stateless, no setup needed)."""
        pass

    # ==================== CORE DETECTION METHODS (Phase 2) ====================

    def detect_workflow_state_filesystem(
        self, plan_path: Path, feature_name: str, achievement_num: str
    ) -> Dict[str, any]:
        """
        Detect workflow state using filesystem structure (not content parsing).

        This is the ROBUST detection method - checks actual files on disk rather
        than parsing markdown text. Introduced in Achievement 1.6 to eliminate
        parsing fragility and improve reliability.

        Detection Logic:
        1. Check if SUBPLAN file exists
        2. Check if SUBPLAN is marked complete (header check)
        3. Count EXECUTION_TASK files in filesystem
        4. Count completed EXECUTION_TASKs (status check)
        5. Compare completed vs total to determine state

        States Returned:
        - no_subplan: SUBPLAN doesn't exist → create_subplan
        - subplan_complete: SUBPLAN marked complete → next_achievement
        - subplan_no_execution: SUBPLAN exists, no EXECUTION files → create_execution
        - active_execution: Some EXECUTIONs incomplete → continue_execution or create_next_execution
        - subplan_all_executed: All EXECUTIONs complete → synthesize_or_complete

        Bug Fixes Incorporated:
            - Bug #6: Counts from filesystem, not SUBPLAN table (more reliable)
            - Bug #7: Finds highest execution number from filesystem
            - Handles multi-execution workflows correctly
            - Handles _V2 and other filename variations

        Args:
            plan_path: Path to PLAN file in nested structure
            feature_name: Feature name (e.g., "METHODOLOGY-HIERARCHY-EVOLUTION")
            achievement_num: Achievement number (e.g., "0.1")

        Returns:
            Dict with keys:
                - state: str (workflow state name)
                - subplan_path: Optional[Path] (path to SUBPLAN)
                - recommendation: str (suggested next action)
                - execution_count: int (total EXECUTION_TASKs planned/found)
                - completed_count: int (completed EXECUTION_TASKs)

        Example:
            >>> detector = WorkflowDetector()
            >>> state = detector.detect_workflow_state_filesystem(plan_path, "FEATURE", "0.1")
            >>> print(state["state"])
            "subplan_no_execution"
        """
        # Import dependencies locally to avoid circular import
        from LLM.scripts.generation.generate_prompt import find_subplan_for_achievement
        from LLM.scripts.generation.utils import get_achievement_status

        # Check achievement status for FIX detection (Achievement 2.9 - tri-state model)
        status = get_achievement_status(achievement_num, plan_path)

        if status == "needs_fix":
            # Achievement requires fixes before proceeding
            return {
                "state": "needs_fix",
                "subplan_path": None,  # Not relevant for FIX state
                "recommendation": "address_fixes",
                "execution_count": 0,
                "completed_count": 0,
                "fix_file": f"FIX_{achievement_num.replace('.', '')}.md",
                "message": "Reviewer feedback requires fixes before proceeding",
            }

        # Find SUBPLAN file
        subplan_path = find_subplan_for_achievement(feature_name, achievement_num, plan_path)

        if not subplan_path:
            return {
                "state": "no_subplan",
                "subplan_path": None,
                "recommendation": "create_subplan",
                "execution_count": 0,
                "completed_count": 0,
            }

        # Check if SUBPLAN is marked complete in header
        try:
            with open(subplan_path, "r", encoding="utf-8") as f:
                header = f.read(500)  # Read first 500 chars for status

            # Check for explicit completion in header
            if re.search(r"\*\*Status\*\*:\s*✅\s*Complete", header, re.IGNORECASE):
                return {
                    "state": "subplan_complete",
                    "subplan_path": subplan_path,
                    "recommendation": "next_achievement",
                    "execution_count": 0,
                    "completed_count": 0,
                }
        except Exception:
            pass

        # Find EXECUTION_TASK files in filesystem
        plan_folder = plan_path.parent
        execution_folder = plan_folder / "execution"

        if not execution_folder.exists():
            # No execution folder = no executions created yet
            return {
                "state": "subplan_no_execution",
                "subplan_path": subplan_path,
                "recommendation": "create_execution",
                "execution_count": 0,
                "completed_count": 0,
            }

        # Find all EXECUTION_TASK files for this achievement
        subplan_num = achievement_num.replace(".", "")
        execution_pattern = f"EXECUTION_TASK_{feature_name}_{subplan_num}_*.md"

        execution_files = list(execution_folder.glob(execution_pattern))

        if not execution_files:
            # SUBPLAN exists but no EXECUTION_TASKs created
            return {
                "state": "subplan_no_execution",
                "subplan_path": subplan_path,
                "recommendation": "create_execution",
                "execution_count": 0,
                "completed_count": 0,
            }

        # Check completion status of each EXECUTION_TASK
        completed_count = 0
        for exec_file in execution_files:
            try:
                with open(exec_file, "r", encoding="utf-8") as f:
                    content = f.read()
                # Check for completion marker anywhere in file (not just header)
                if re.search(r"\*\*Status\*\*:\s*✅\s*Complete", content, re.IGNORECASE):
                    completed_count += 1
            except Exception:
                continue

        filesystem_count = len(execution_files)

        # Check SUBPLAN for planned execution count (for multi-execution workflows)
        planned_count = None
        try:
            with open(subplan_path, "r", encoding="utf-8") as f:
                subplan_content = f.read()

            # Look for "## 🔄 Active EXECUTION_TASKs" section
            active_section_match = re.search(
                r"##\s*🔄\s*Active EXECUTION_TASKs.*?(?=\n##\s|\Z)",
                subplan_content,
                re.DOTALL | re.IGNORECASE,
            )

            if active_section_match:
                # Count EXECUTION_TASK entries in the section
                active_section = active_section_match.group(0)
                lines = active_section.split("\n")
                execution_rows = []
                for line in lines:
                    # Match lines like "| 01_01     | ..."
                    match = re.match(r"^\|\s*(\d+_\d+)\s*\|", line)
                    if match:
                        execution_rows.append(match.group(1))
                if execution_rows:
                    planned_count = len(execution_rows)
        except Exception:
            pass

        # Use planned count if available, otherwise use filesystem count
        total_count = planned_count if planned_count is not None else filesystem_count

        # Determine state based on completion
        if completed_count < total_count:
            # Some executions still in progress or not yet created
            has_incomplete_file = filesystem_count > completed_count

            return {
                "state": "active_execution",
                "subplan_path": subplan_path,
                "recommendation": (
                    "continue_execution" if has_incomplete_file else "create_next_execution"
                ),
                "execution_count": total_count,
                "completed_count": completed_count,
            }
        elif completed_count == total_count and total_count > 0:
            # All executions complete
            return {
                "state": "subplan_all_executed",
                "subplan_path": subplan_path,
                "recommendation": "synthesize_or_complete",
                "execution_count": total_count,
                "completed_count": completed_count,
            }
        else:
            # Fallback
            return {
                "state": "subplan_no_execution",
                "subplan_path": subplan_path,
                "recommendation": "create_execution",
                "execution_count": 0,
                "completed_count": 0,
            }

    def detect_plan_filesystem_conflict(
        self, plan_path: Path, feature_name: str, achievement_num: str, plan_content: str
    ) -> Optional[Dict[str, any]]:
        """
        Detect conflicts between Achievement Index and filesystem structure.

        **State Tracking Philosophy**:
        - PLAN's ONLY responsibility: Define Achievement Index (list of all achievements)
        - Filesystem's responsibility: Track completion via APPROVED_XX.md files
        - Conflicts ONLY occur when these two sources disagree

        Conflict Types Detected:
        1. achievement_not_in_index: Filesystem has APPROVED file for achievement not in Index
        2. orphaned_work: Filesystem has SUBPLANs/EXECUTIONs for achievement not in Index

        NO LONGER DETECTED (removed):
        - PLAN handoff section staleness (not filesystem's concern)
        - Completion status mismatches (filesystem is source of truth)
        - Work state conflicts (filesystem determines state)

        Detection Strategy:
        1. Parse Achievement Index from PLAN
        2. Check filesystem for APPROVED files
        3. Check filesystem for SUBPLANs/EXECUTIONs
        4. Flag any mismatches between Index and filesystem

        Args:
            plan_path: Path to PLAN file
            feature_name: Feature name
            achievement_num: Achievement number (UNUSED - kept for compatibility)
            plan_content: Full PLAN content

        Returns:
            Dict with conflict details if found, None if no conflict

        Example:
            >>> detector = WorkflowDetector()
            >>> conflict = detector.detect_plan_filesystem_conflict(plan_path, "FEATURE", "0.2", content)
            >>> if conflict:
            ...     print(conflict['conflicts'][0]['message'])
        """
        # Import dependencies locally to avoid circular import
        from LLM.scripts.generation.plan_parser import PlanParser

        # Parse Achievement Index from PLAN
        parser = PlanParser()
        plan_data = parser.parse_plan_file(plan_path)
        index_achievements = {ach.number for ach in plan_data["achievements"]}

        # Check filesystem for APPROVED files
        plan_folder = plan_path.parent
        feedbacks_folder = plan_folder / "execution" / "feedbacks"

        conflicts = []

        if feedbacks_folder.exists():
            # Find all APPROVED_XX.md files
            approved_files = list(feedbacks_folder.glob("APPROVED_*.md"))

            for approved_file in approved_files:
                # Extract achievement number from filename
                filename = approved_file.stem
                ach_num_str = filename.replace("APPROVED_", "")

                # Convert to achievement format (e.g., "21" -> "2.1")
                if len(ach_num_str) >= 2:
                    ach_num = f"{ach_num_str[0]}.{ach_num_str[1:]}"
                else:
                    ach_num = ach_num_str

                # Check if achievement is in Index
                if ach_num not in index_achievements:
                    conflicts.append(
                        {
                            "type": "achievement_not_in_index",
                            "message": f"Achievement {ach_num} has APPROVED file but is not in Achievement Index",
                            "filesystem": f"✅ {approved_file.name}",
                            "plan": "❌ Not in Achievement Index",
                            "likely_cause": "Achievement was completed but not added to Index, or Index was updated but old APPROVED file remains",
                            "resolution": f"Either add Achievement {ach_num} to the Achievement Index section, or remove {approved_file.name} if it's obsolete",
                        }
                    )

        # Check filesystem for orphaned SUBPLANs
        subplans_folder = plan_folder / "subplans"

        if subplans_folder.exists():
            subplan_files = list(subplans_folder.glob(f"SUBPLAN_{feature_name}_*.md"))

            for subplan_file in subplan_files:
                # Extract achievement number from filename
                match = re.search(
                    rf"SUBPLAN_{re.escape(feature_name)}_(\d+)\.md", subplan_file.name
                )
                if match:
                    ach_num_str = match.group(1)
                    if len(ach_num_str) >= 2:
                        ach_num = f"{ach_num_str[0]}.{ach_num_str[1:]}"
                    else:
                        ach_num = ach_num_str

                    if ach_num not in index_achievements:
                        conflicts.append(
                            {
                                "type": "orphaned_work",
                                "message": f"Achievement {ach_num} has SUBPLAN but is not in Achievement Index",
                                "filesystem": f"📄 {subplan_file.name}",
                                "plan": "❌ Not in Achievement Index",
                                "likely_cause": "SUBPLAN was created but achievement was removed from Index",
                                "resolution": f"Either add Achievement {ach_num} to the Achievement Index, or archive {subplan_file.name} if obsolete",
                            }
                        )

        if conflicts:
            return {
                "has_conflict": True,
                "conflicts": conflicts,
            }

        return None

    def find_next_achievement_hybrid(
        self,
        plan_path: Path,
        feature_name: str,
        achievements: List[Achievement],
        archive_location: str,
    ) -> Optional[Achievement]:
        """
        Find next achievement using multiple methods (hybrid approach).

        This is the MAIN achievement finding function - combines multiple detection
        methods with comprehensive validation to find the correct next achievement.

        Detection Methods (Priority Order):
        1. Parse PLAN handoff section (MOST AUTHORITATIVE)
           - Reads explicit "Next: Achievement X.Y" statement
           - Validates achievement exists and is not complete
           - Warns if handoff is stale

        2. Check PLAN status (FALLBACK for plans without clear "Next")
           - If status is "planning", return first achievement
           - Handles plans just starting

        3. Check archive directory (FALLBACK for archived SUBPLANs)
           - Finds first achievement without archived SUBPLAN
           - Skips completed achievements

        4. Check root directory (FALLBACK for flat structure)
           - Finds first achievement without SUBPLAN in root
           - Skips completed achievements

        Validation:
        - Checks if PLAN is complete FIRST (returns None if done)
        - Skips achievements marked complete
        - Warns if handoff mentions non-existent achievement
        - Warns if handoff mentions complete achievement

        Args:
            plan_path: Path to PLAN file
            feature_name: Feature name
            achievements: List of achievements from PLAN
            archive_location: Archive directory path

        Returns:
            Achievement object or None if PLAN is complete

        Example:
            >>> detector = WorkflowDetector()
            >>> next_ach = detector.find_next_achievement_hybrid(plan_path, "FEATURE", achievements, "./archive/")
            >>> print(next_ach.number if next_ach else "Complete")
        """
        # Import dependencies locally to avoid circular import
        from LLM.scripts.generation.utils import is_achievement_complete
        from LLM.scripts.generation.generate_prompt import (
            is_plan_complete,
            get_plan_status,
        )

        # Read PLAN content once
        try:
            with open(plan_path, "r", encoding="utf-8") as f:
                plan_content = f.read()
        except Exception:
            return None

        # STEP 1: Check if PLAN is complete FIRST
        if is_plan_complete(plan_content, achievements, plan_path):
            return None  # Indicates PLAN is complete

        # STEP 2: Parse PLAN "What's Next" (MOST AUTHORITATIVE)
        next_num = self.find_next_achievement_from_plan(plan_content)
        if next_num:
            # Validate achievement exists
            next_ach = next((a for a in achievements if a.number == next_num), None)
            if next_ach:
                # Ensure achievement is not complete
                if not is_achievement_complete(next_ach.number, plan_content, plan_path):
                    return next_ach
                # If complete, warn and continue to fallback
                warnings.warn(
                    f"Achievement {next_num} mentioned in handoff but is marked complete. "
                    f"Falling back to next incomplete achievement.",
                    UserWarning,
                )
            else:
                # Achievement doesn't exist
                warnings.warn(
                    f"Achievement {next_num} mentioned in handoff but not found in PLAN. "
                    f"Available achievements: {[a.number for a in achievements]}. "
                    f"Falling back to archive/root methods.",
                    UserWarning,
                )

        # STEP 3: Check PLAN status (FALLBACK)
        status = get_plan_status(plan_content)
        if status == "planning":
            # Return first achievement if not complete
            if achievements and not is_achievement_complete(
                achievements[0].number, plan_content, plan_path
            ):
                return achievements[0]

        # STEP 4: Check archive directory
        next_ach = self.find_next_achievement_from_archive(
            feature_name, achievements, archive_location, plan_content, plan_path
        )
        if next_ach:
            return next_ach

        # STEP 5: Check root directory
        return self.find_next_achievement_from_root(
            feature_name, achievements, plan_content, plan_path
        )

    # ==================== HELPER METHODS (Phase 3) ====================

    def find_next_achievement_from_plan(self, plan_content: str) -> Optional[str]:
        """
        Find next achievement from PLAN's 'Current Status & Handoff' section.

        This is the PRIMARY method for finding next achievement - reads the
        PLAN's explicit "Next:" statement in the handoff section.

        Search Strategy:
        1. Check handoff section first (authoritative)
        2. Try multiple patterns (⏳ Next:, Next:, etc.)
        3. Fall back to full file if handoff doesn't have clear "Next"

        Args:
            plan_content: Full PLAN file content

        Returns:
            Achievement number (e.g., "1.1") or None

        Example:
            >>> detector = WorkflowDetector()
            >>> next_num = detector.find_next_achievement_from_plan(content)
            >>> print(next_num)
            "1.2"
        """
        # Import dependencies locally to avoid circular import
        from LLM.scripts.generation.plan_parser import PlanParser

        # Reordered patterns: specific formats first, generic/greedy last
        patterns = [
            r"⏳\s*Next[:\s]+Achievement\s+(\d+\.\d+)",  # ⏳ Next: Achievement
            r"(?:Next|What\'s Next)[:\s]+Achievement\s+(\d+\.\d+)",  # Next: Achievement
            r"Next[:\s]+Achievement\s+(\d+\.\d+)",  # Next: Achievement (generic)
            r"⏳\s*Achievement\s+(\d+\.\d+)",  # ⏳ Achievement
            r"(?:Next|What\'s Next)\*\*[:\s]+.*?Achievement\s+(\d+\.\d+)",  # **Next**: ... Achievement
        ]

        # Primary: Try handoff section first
        parser = PlanParser()
        handoff_section = parser.extract_handoff_section(plan_content)
        if handoff_section:
            for pattern in patterns:
                match = re.search(pattern, handoff_section, re.IGNORECASE | re.MULTILINE)
                if match:
                    return match.group(1)

        # Fallback: Search full file
        for pattern in patterns:
            match = re.search(pattern, plan_content, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1)

        return None

    def find_next_achievement_from_archive(
        self,
        feature_name: str,
        achievements: List[Achievement],
        archive_location: str,
        plan_content: str,
        plan_path: Path = None,
    ) -> Optional[Achievement]:
        """
        Find first achievement without archived SUBPLAN (fallback detection method).

        This is a FALLBACK method used when handoff section doesn't have clear
        "Next:" statement. Checks archive directory for SUBPLANs.

        Detection Logic:
        1. Check if archive directory exists
        2. For each achievement (in order):
           - Skip if marked complete (checks APPROVED_XX.md files)
           - Check if SUBPLAN exists in archive
           - Return first achievement without archived SUBPLAN

        Args:
            feature_name: Feature name
            achievements: List of achievements
            archive_location: Archive directory path
            plan_content: PLAN file content
            plan_path: Path to PLAN file

        Returns:
            First incomplete achievement without archived SUBPLAN, or None

        Example:
            >>> detector = WorkflowDetector()
            >>> next_ach = detector.find_next_achievement_from_archive("FEATURE", achievements, "./archive/", content, plan_path)
        """
        # Import dependencies locally to avoid circular import
        from LLM.scripts.generation.utils import is_achievement_complete

        # Convert archive location string to Path
        archive_path = Path(archive_location)

        # Check if archive location exists
        if not archive_path.exists():
            return None

        # Check subplans directory
        archive_subplans = archive_path / "subplans"
        if not archive_subplans.exists():
            return None

        # Find first achievement without archived SUBPLAN
        for ach in achievements:
            # SKIP if marked complete
            if is_achievement_complete(ach.number, plan_content, plan_path):
                continue

            # Check if SUBPLAN exists in archive
            subplan_num = ach.number.replace(".", "")
            subplan_file = archive_subplans / f"SUBPLAN_{feature_name}_{subplan_num}.md"
            if not subplan_file.exists():
                return ach

        return None

    def find_next_achievement_from_root(
        self,
        feature_name: str,
        achievements: List[Achievement],
        plan_content: str,
        plan_path: Path = None,
    ) -> Optional[Achievement]:
        """
        Find first achievement without SUBPLAN in root directory (fallback method).

        This is a FALLBACK method for flat workspace structure (legacy).

        Detection Logic:
        1. For each achievement (in order):
           - Skip if marked complete (checks APPROVED_XX.md files)
           - Check if SUBPLAN exists in root (flat structure)
           - Return first achievement without SUBPLAN

        Args:
            feature_name: Feature name
            achievements: List of achievements
            plan_content: PLAN file content
            plan_path: Path to PLAN file

        Returns:
            First incomplete achievement without SUBPLAN, or None

        Example:
            >>> detector = WorkflowDetector()
            >>> next_ach = detector.find_next_achievement_from_root("FEATURE", achievements, content, plan_path)
        """
        # Import dependencies locally to avoid circular import
        from LLM.scripts.generation.utils import is_achievement_complete

        for ach in achievements:
            # SKIP if marked complete
            if is_achievement_complete(ach.number, plan_content, plan_path):
                continue

            # Check if SUBPLAN exists in root
            subplan_num = ach.number.replace(".", "")
            subplan_file = Path(f"SUBPLAN_{feature_name}_{subplan_num}.md")
            if not subplan_file.exists():
                return ach
        return None
