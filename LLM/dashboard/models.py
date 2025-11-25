"""
Dashboard Data Models

Defines data structures for plan and achievement state representation.

**Design Philosophy**:
- Filesystem-first: Status derived from filesystem, not persisted
- Immutable data: Dataclasses with frozen=False for flexibility
- Type-safe: Full type hints throughout
- Rich information: All data needed for dashboard rendering

Created: 2025-11-13
Achievement: 0.2 - Plan Discovery & State Detection
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional


class PlanStatus(Enum):
    """
    Plan-level status enum.

    Status is derived from filesystem state:
    - ACTIVE: Work in progress (some achievements incomplete)
    - COMPLETE: All achievements have APPROVED files
    - NEEDS_ATTENTION: Has pending FIX files requiring attention
    """

    ACTIVE = "active"
    COMPLETE = "complete"
    NEEDS_ATTENTION = "needs_attention"


class AchievementStatus(Enum):
    """
    Achievement-level status enum.

    Status is derived from filesystem state:
    - NOT_STARTED: No SUBPLAN file exists
    - IN_PROGRESS: SUBPLAN or EXECUTION_TASK exists, no APPROVED
    - COMPLETE: APPROVED file exists
    - NEEDS_FIX: FIX file exists
    """

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    NEEDS_FIX = "needs_fix"


@dataclass
class AchievementState:
    """
    State of a single achievement.

    Represents the current state of an achievement based on filesystem queries.
    All boolean flags are derived from file existence checks.

    **Usage**:
        state = AchievementState(
            achievement_id="1.1",
            title="Setup Foundation",
            status=AchievementStatus.COMPLETE,
            has_subplan=True,
            has_execution=True,
            has_approved=True,
            has_fix=False
        )
    """

    achievement_id: str
    title: str
    status: AchievementStatus
    has_subplan: bool
    has_execution: bool
    has_approved: bool
    has_fix: bool

    def is_complete(self) -> bool:
        """Check if achievement is complete (has APPROVED file)."""
        return self.status == AchievementStatus.COMPLETE

    def needs_fix(self) -> bool:
        """Check if achievement needs fixes (has FIX file)."""
        return self.status == AchievementStatus.NEEDS_FIX


@dataclass
class PlanState:
    """
    Complete state of a PLAN.

    Aggregates all plan-level information derived from filesystem queries.
    Used by dashboard to render plan overview and detailed views.

    **Filesystem-First Design**:
    - Status computed from APPROVED/FIX files
    - Progress computed from achievement counts
    - Next achievements computed from sequential order
    - No state persistence (always fresh from filesystem)

    **Usage**:
        state = PlanState(
            name="MY-PLAN",
            plan_file=Path("work-space/plans/MY-PLAN/PLAN_MY-PLAN.md"),
            last_achievement="2.3",
            next_achievements=["2.4", "2.5"],
            pending_reviews=["3.1"],
            pending_fixes=["1.2"],
            total_achievements=10,
            completed_achievements=5,
            progress_percentage=50.0,
            status=PlanStatus.ACTIVE
        )

        if state.is_complete():
            print("Plan complete!")
        elif state.needs_attention():
            print(f"Plan has {len(state.pending_fixes)} pending fixes")
    """

    name: str
    plan_file: Path
    last_achievement: Optional[str]
    next_achievements: List[str]
    pending_reviews: List[str] = field(default_factory=list)
    pending_fixes: List[str] = field(default_factory=list)
    total_achievements: int = 0
    completed_achievements: int = 0
    progress_percentage: float = 0.0
    status: PlanStatus = PlanStatus.ACTIVE

    def is_complete(self) -> bool:
        """Check if plan is complete (all achievements approved)."""
        return self.status == PlanStatus.COMPLETE

    def needs_attention(self) -> bool:
        """Check if plan needs attention (has pending fixes)."""
        return self.status == PlanStatus.NEEDS_ATTENTION or len(self.pending_fixes) > 0

    def has_pending_work(self) -> bool:
        """Check if plan has any pending work (reviews or fixes)."""
        return len(self.pending_reviews) > 0 or len(self.pending_fixes) > 0

    def get_completion_ratio(self) -> str:
        """Get completion ratio as string (e.g., '5/10')."""
        return f"{self.completed_achievements}/{self.total_achievements}"


# ============================================================================
# Achievement 2.2: Interactive Workflow Execution Models
# ============================================================================


class WorkflowType(Enum):
    """
    Types of workflows that can be executed.
    
    Achievement 2.2: Interactive Workflow Execution
    
    - NEXT: Execute next achievement workflow (auto-detect state)
    - SUBPLAN: Create SUBPLAN for specific achievement
    - EXECUTION: Create EXECUTION_TASK for specific SUBPLAN
    """
    
    NEXT = "next"
    SUBPLAN = "subplan"
    EXECUTION = "execution"


class WorkflowState(Enum):
    """
    States of workflow execution.
    
    Achievement 2.2: Interactive Workflow Execution
    
    - PENDING: Workflow queued, not yet started
    - RUNNING: Workflow currently executing
    - SUCCESS: Workflow completed successfully
    - FAILED: Workflow encountered error
    """
    
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class ExecutionResult:
    """
    Result of workflow execution.
    
    Achievement 2.2: Interactive Workflow Execution
    
    Captures the outcome of executing a workflow, including success status,
    deliverables created, test results, and error information if applicable.
    
    **Usage**:
        # Success result
        result = ExecutionResult(
            success=True,
            deliverables=["SUBPLAN_MY-PLAN_11.md"],
            tests_passing=42,
            tests_total=42,
            duration=83.5
        )
        
        # Failure result
        result = ExecutionResult(
            success=False,
            error="SUBPLAN not found: SUBPLAN_MY-PLAN_11.md",
            log_file=Path("logs/workflow_20251114_210000.log")
        )
    """
    
    success: bool
    error: Optional[str] = None
    deliverables: List[str] = field(default_factory=list)
    tests_passing: int = 0
    tests_total: int = 0
    duration: float = 0.0
    log_file: Optional[Path] = None
    
    def has_test_failures(self) -> bool:
        """Check if there are test failures."""
        return self.tests_total > 0 and self.tests_passing < self.tests_total
    
    def format_duration(self) -> str:
        """Format duration as human-readable string (e.g., '2m 34s')."""
        if self.duration < 60:
            return f"{self.duration:.1f}s"
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        return f"{minutes}m {seconds}s"
