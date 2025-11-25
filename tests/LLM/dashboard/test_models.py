"""
Tests for dashboard models module.

Tests data models and enums.
"""

import pytest
from pathlib import Path

from LLM.dashboard.models import (
    AchievementState,
    AchievementStatus,
    PlanState,
    PlanStatus,
)


class TestPlanStatus:
    """Tests for PlanStatus enum."""

    def test_plan_status_values(self):
        """Test PlanStatus enum has correct values."""
        assert PlanStatus.ACTIVE.value == "active"
        assert PlanStatus.COMPLETE.value == "complete"
        assert PlanStatus.NEEDS_ATTENTION.value == "needs_attention"


class TestAchievementStatus:
    """Tests for AchievementStatus enum."""

    def test_achievement_status_values(self):
        """Test AchievementStatus enum has correct values."""
        assert AchievementStatus.NOT_STARTED.value == "not_started"
        assert AchievementStatus.IN_PROGRESS.value == "in_progress"
        assert AchievementStatus.COMPLETE.value == "complete"
        assert AchievementStatus.NEEDS_FIX.value == "needs_fix"


class TestAchievementState:
    """Tests for AchievementState dataclass."""

    def test_create_achievement_state(self):
        """Test creating AchievementState."""
        state = AchievementState(
            achievement_id="1.1",
            title="Test Achievement",
            status=AchievementStatus.COMPLETE,
            has_subplan=True,
            has_execution=True,
            has_approved=True,
            has_fix=False,
        )

        assert state.achievement_id == "1.1"
        assert state.title == "Test Achievement"
        assert state.status == AchievementStatus.COMPLETE
        assert state.has_subplan is True
        assert state.has_approved is True

    def test_is_complete(self):
        """Test is_complete() method."""
        state = AchievementState(
            achievement_id="1.1",
            title="Test",
            status=AchievementStatus.COMPLETE,
            has_subplan=True,
            has_execution=True,
            has_approved=True,
            has_fix=False,
        )

        assert state.is_complete() is True

    def test_needs_fix(self):
        """Test needs_fix() method."""
        state = AchievementState(
            achievement_id="1.1",
            title="Test",
            status=AchievementStatus.NEEDS_FIX,
            has_subplan=True,
            has_execution=True,
            has_approved=False,
            has_fix=True,
        )

        assert state.needs_fix() is True


class TestPlanState:
    """Tests for PlanState dataclass."""

    def test_create_plan_state(self):
        """Test creating PlanState."""
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
            status=PlanStatus.ACTIVE,
        )

        assert state.name == "MY-PLAN"
        assert state.last_achievement == "2.3"
        assert state.next_achievements == ["2.4", "2.5"]
        assert state.total_achievements == 10
        assert state.progress_percentage == 50.0

    def test_is_complete(self):
        """Test is_complete() method."""
        state = PlanState(
            name="MY-PLAN",
            plan_file=Path("test.md"),
            last_achievement="3.3",
            next_achievements=[],
            total_achievements=3,
            completed_achievements=3,
            progress_percentage=100.0,
            status=PlanStatus.COMPLETE,
        )

        assert state.is_complete() is True

    def test_needs_attention(self):
        """Test needs_attention() method."""
        state = PlanState(
            name="MY-PLAN",
            plan_file=Path("test.md"),
            last_achievement="1.1",
            next_achievements=["1.2"],
            pending_fixes=["1.2"],
            status=PlanStatus.NEEDS_ATTENTION,
        )

        assert state.needs_attention() is True

    def test_has_pending_work(self):
        """Test has_pending_work() method."""
        state = PlanState(
            name="MY-PLAN",
            plan_file=Path("test.md"),
            last_achievement="1.1",
            next_achievements=["1.2"],
            pending_reviews=["1.2"],
            pending_fixes=[],
        )

        assert state.has_pending_work() is True

    def test_get_completion_ratio(self):
        """Test get_completion_ratio() method."""
        state = PlanState(
            name="MY-PLAN",
            plan_file=Path("test.md"),
            last_achievement="1.1",
            next_achievements=[],
            total_achievements=10,
            completed_achievements=5,
        )

        assert state.get_completion_ratio() == "5/10"
