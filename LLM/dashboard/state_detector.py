"""
State Detector Module

Detects plan and achievement states from filesystem.

**Design Philosophy**:
- Filesystem-first: All state derived from file existence
- No persistence: Always query filesystem for current state
- Fast queries: Use Path.glob() for efficient file detection
- Graceful errors: Handle missing files/directories

Created: 2025-11-13
Achievement: 0.2 - Plan Discovery & State Detection
Updated: 2025-11-13
Achievement: 0.4 - Library Integration & Production Patterns
"""
import re
from pathlib import Path
from typing import List, Optional

from core.libraries.logging import get_logger
from LLM.dashboard.models import (
    AchievementStatus,
    PlanState,
    PlanStatus,
)
from LLM.dashboard.utils import parse_achievement_number
from LLM.dashboard.exceptions import StateDetectionError

logger = get_logger(__name__)


class StateDetector:
    """
    Detect plan and achievement states from filesystem.
    
    Queries filesystem to determine:
    - Last completed achievement (from APPROVED files)
    - Pending reviews (EXECUTION_TASKs without feedback)
    - Pending fixes (FIX files)
    - Next available achievements (sequential order)
    - Progress percentage (completed / total)
    
    **Filesystem-First Design**:
    All state is computed on-demand from filesystem. No state is cached or
    persisted. This ensures dashboard always shows current reality.
    
    **Usage**:
        detector = StateDetector()
        state = detector.get_plan_state(Path('work-space/plans/MY-PLAN'))
        print(f"Progress: {state.progress_percentage}%")
        print(f"Last: {state.last_achievement}")
        print(f"Next: {state.next_achievements}")
    """
    
    def get_plan_state(self, plan_dir: Path) -> PlanState:
        """
        Get complete plan state from filesystem.
        
        Computes all state by querying filesystem:
        1. Parse achievement index from PLAN file
        2. Find last completed achievement (APPROVED files)
        3. Find pending reviews and fixes
        4. Compute next available achievements
        5. Calculate progress percentage
        6. Determine plan status
        
        Args:
            plan_dir: Path to plan directory
        
        Returns:
            PlanState with all computed information
        
        **Example**:
            detector = StateDetector()
            state = detector.get_plan_state(Path('work-space/plans/MY-PLAN'))
            if state.is_complete():
                print("All achievements complete!")
        """
        logger.debug(f"Detecting state for plan: {plan_dir.name}", extra={'plan_dir': str(plan_dir)})
        
        plan_file = self._get_plan_file(plan_dir)
        if not plan_file:
            logger.warning(f"No PLAN file found for: {plan_dir.name}")
            # Return minimal state if no PLAN file
            return PlanState(
                name=plan_dir.name,
                plan_file=plan_dir / "PLAN_unknown.md",
                last_achievement=None,
                next_achievements=[],
                pending_reviews=[],
                pending_fixes=[],
                total_achievements=0,
                completed_achievements=0,
                progress_percentage=0.0,
                status=PlanStatus.ACTIVE,
            )
        
        # Parse achievement index from PLAN
        all_achievements = self._parse_achievement_index(plan_file)
        
        # Detect states from filesystem
        last_complete = self._get_last_complete(plan_dir)
        pending_reviews = self._get_pending_reviews(plan_dir)
        pending_fixes = self._get_pending_fixes(plan_dir)
        
        # Compute derived values
        completed_count = self._count_approved(plan_dir)
        next_achievements = self._get_next_available(
            all_achievements, last_complete, pending_fixes
        )
        progress = self._calculate_progress(completed_count, len(all_achievements))
        
        # Determine status
        status = self._determine_status(
            completed_count, len(all_achievements), pending_fixes
        )
        
        logger.debug(f"State detected for {plan_dir.name}: {status.value}, progress {progress}%", extra={
            'plan_name': plan_dir.name,
            'status': status.value,
            'progress': progress,
            'completed': completed_count,
            'total': len(all_achievements)
        })
        
        return PlanState(
            name=plan_dir.name,
            plan_file=plan_file,
            last_achievement=last_complete,
            next_achievements=next_achievements,
            pending_reviews=pending_reviews,
            pending_fixes=pending_fixes,
            total_achievements=len(all_achievements),
            completed_achievements=completed_count,
            progress_percentage=progress,
            status=status,
        )
    
    def _get_plan_file(self, plan_dir: Path) -> Optional[Path]:
        """Get PLAN_*.md file from directory."""
        if not plan_dir.exists():
            return None
        plan_files = list(plan_dir.glob("PLAN_*.md"))
        return plan_files[0] if plan_files else None
    
    def _get_last_complete(self, plan_dir: Path) -> Optional[str]:
        """
        Get last completed achievement from APPROVED files.
        
        Finds highest numbered APPROVED_*.md file in execution/feedbacks/.
        
        Args:
            plan_dir: Plan directory
        
        Returns:
            Achievement number (e.g., "3.1") or None if no APPROVED files
        """
        feedbacks_dir = plan_dir / "execution" / "feedbacks"
        if not feedbacks_dir.exists():
            return None
        
        approved_files = sorted(feedbacks_dir.glob("APPROVED_*.md"))
        if not approved_files:
            return None
        
        # Get last (highest numbered) APPROVED file
        last_approved = approved_files[-1]
        
        try:
            return parse_achievement_number(last_approved.name)
        except ValueError:
            return None
    
    def _get_pending_reviews(self, plan_dir: Path) -> List[str]:
        """
        Get achievements with pending reviews.
        
        Finds EXECUTION_TASK files that don't have feedback (no APPROVED or FIX).
        
        Args:
            plan_dir: Plan directory
        
        Returns:
            List of achievement numbers awaiting review
        """
        execution_dir = plan_dir / "execution"
        feedbacks_dir = plan_dir / "execution" / "feedbacks"
        
        if not execution_dir.exists():
            return []
        
        # Get all EXECUTION_TASK files
        exec_files = list(execution_dir.glob("EXECUTION_TASK_*.md"))
        
        pending = []
        for exec_file in exec_files:
            try:
                achievement_num = parse_achievement_number(exec_file.name)
                
                # Check if feedback exists
                if feedbacks_dir.exists():
                    approved = feedbacks_dir / f"APPROVED_{achievement_num.replace('.', '')}.md"
                    fix = feedbacks_dir / f"FIX_{achievement_num.replace('.', '')}.md"
                    
                    if not approved.exists() and not fix.exists():
                        pending.append(achievement_num)
                else:
                    # No feedbacks dir means all executions are pending
                    pending.append(achievement_num)
            except ValueError:
                continue
        
        return sorted(set(pending))
    
    def _get_pending_fixes(self, plan_dir: Path) -> List[str]:
        """
        Get achievements with pending fixes.
        
        Finds FIX_*.md files in execution/feedbacks/.
        
        Args:
            plan_dir: Plan directory
        
        Returns:
            List of achievement numbers with FIX files
        """
        feedbacks_dir = plan_dir / "execution" / "feedbacks"
        if not feedbacks_dir.exists():
            return []
        
        fix_files = feedbacks_dir.glob("FIX_*.md")
        fixes = []
        
        for fix_file in fix_files:
            try:
                achievement_num = parse_achievement_number(fix_file.name)
                fixes.append(achievement_num)
            except ValueError:
                continue
        
        return sorted(set(fixes))
    
    def _get_next_available(
        self, all_achievements: List[str], last_complete: Optional[str], pending_fixes: List[str]
    ) -> List[str]:
        """
        Compute next available achievements.
        
        Logic:
        1. If no achievements complete, return first achievement
        2. If achievements complete, return next in sequential order
        3. Exclude achievements with pending fixes
        4. Return up to 3 next achievements
        
        Args:
            all_achievements: All achievements from index
            last_complete: Last completed achievement
            pending_fixes: Achievements with FIX files
        
        Returns:
            List of next available achievement numbers
        """
        if not all_achievements:
            return []
        
        # If nothing complete, return first achievement
        if last_complete is None:
            first = all_achievements[0]
            return [first] if first not in pending_fixes else []
        
        # Find index of last complete
        try:
            last_idx = all_achievements.index(last_complete)
        except ValueError:
            return []
        
        # Get next achievements (up to 3)
        next_achievements = []
        for i in range(last_idx + 1, min(last_idx + 4, len(all_achievements))):
            achievement = all_achievements[i]
            if achievement not in pending_fixes:
                next_achievements.append(achievement)
        
        return next_achievements
    
    def _calculate_progress(self, completed: int, total: int) -> float:
        """
        Calculate progress percentage.
        
        Args:
            completed: Number of completed achievements
            total: Total number of achievements
        
        Returns:
            Progress percentage (0.0 to 100.0)
        """
        if total == 0:
            return 0.0
        return round((completed / total) * 100, 1)
    
    def _count_approved(self, plan_dir: Path) -> int:
        """Count number of APPROVED files."""
        feedbacks_dir = plan_dir / "execution" / "feedbacks"
        if not feedbacks_dir.exists():
            return 0
        return len(list(feedbacks_dir.glob("APPROVED_*.md")))
    
    def _parse_achievement_index(self, plan_file: Path) -> List[str]:
        """
        Parse Achievement Index from PLAN file.
        
        Finds "## 📋 Achievement Index" section and extracts all achievement
        numbers matching pattern: Achievement X.Y
        
        Args:
            plan_file: Path to PLAN file
        
        Returns:
            List of achievement numbers in order (e.g., ["0.1", "0.2", "1.1"])
            
        Raises:
            StateDetectionError: If PLAN file cannot be read (permissions, encoding)
        """
        if not plan_file.exists():
            return []
        
        try:
            content = plan_file.read_text(encoding='utf-8')
        except UnicodeDecodeError as e:
            raise StateDetectionError(
                f"Failed to decode PLAN file: {str(e)}",
                context={
                    'plan_file': str(plan_file),
                    'error': 'encoding issue'
                },
                suggestions=[
                    "Verify file is UTF-8 encoded",
                    "Check for binary data in file",
                    "Re-save file with proper encoding"
                ]
            ) from e
        except OSError as e:
            raise StateDetectionError(
                f"Failed to read PLAN file: {str(e)}",
                context={
                    'plan_file': str(plan_file),
                    'error': str(e)
                },
                suggestions=[
                    "Verify file is accessible",
                    "Check file permissions",
                    "Ensure disk is available"
                ]
            ) from e
        
        # Find Achievement Index section
        lines = content.split("\n")
        in_index = False
        achievements = []
        
        for line in lines:
            # Start of index section
            if "Achievement Index" in line:
                in_index = True
                continue
            
            # End of index section (next ## heading)
            if in_index and line.startswith("##"):
                break
            
            # Extract achievement numbers
            if in_index:
                # Pattern: "- Achievement 1.1:" or "Achievement 1.1:"
                match = re.search(r"Achievement\s+(\d+\.\d+)", line)
                if match:
                    achievements.append(match.group(1))
        
        return achievements
    
    def _determine_status(
        self, completed: int, total: int, pending_fixes: List[str]
    ) -> PlanStatus:
        """
        Determine plan status.
        
        Logic:
        - NEEDS_ATTENTION: Has pending fixes
        - COMPLETE: All achievements complete
        - ACTIVE: Otherwise
        
        Args:
            completed: Number of completed achievements
            total: Total achievements
            pending_fixes: List of achievements with FIX files
        
        Returns:
            PlanStatus enum value
        """
        if pending_fixes:
            return PlanStatus.NEEDS_ATTENTION
        elif total > 0 and completed == total:
            return PlanStatus.COMPLETE
        else:
            return PlanStatus.ACTIVE



