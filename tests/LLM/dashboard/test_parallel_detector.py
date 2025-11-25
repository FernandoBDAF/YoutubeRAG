"""
Tests for parallel execution detection in dashboard.

Verifies ParallelDetector functionality, UI rendering, and integration
with batch tools from PARALLEL-EXECUTION-AUTOMATION.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from rich.console import Console

from LLM.dashboard.parallel_detector import ParallelDetector, ParallelGroup
from LLM.dashboard.plan_dashboard import PlanDashboard


class TestParallelDetector:
    """Tests for ParallelDetector class."""

    @pytest.fixture
    def test_plan_with_parallel_json(self, tmp_path):
        """Create test plan with parallel.json."""
        plan_dir = tmp_path / "plans" / "TEST-PLAN"
        plan_dir.mkdir(parents=True)

        # Create PLAN file
        (plan_dir / "PLAN_TEST-PLAN.md").write_text("# Test Plan")

        # Create parallel.json with 3 level-0 achievements
        parallel_data = {
            "plan_name": "TEST-PLAN",
            "achievements": [
                {
                    "id": "3.1",
                    "name": "Achievement 3.1",
                    "dependencies": [],
                    "estimated_hours": "3-4",
                },
                {
                    "id": "3.2",
                    "name": "Achievement 3.2",
                    "dependencies": [],
                    "estimated_hours": "3-4",
                },
                {
                    "id": "3.3",
                    "name": "Achievement 3.3",
                    "dependencies": [],
                    "estimated_hours": "3-4",
                },
            ],
        }
        (plan_dir / "parallel.json").write_text(json.dumps(parallel_data, indent=2))

        return plan_dir

    def test_has_parallel_opportunities_true(self, test_plan_with_parallel_json):
        """Test has_parallel_opportunities returns True when parallel.json exists."""
        detector = ParallelDetector(test_plan_with_parallel_json)
        assert detector.has_parallel_opportunities() is True

    def test_has_parallel_opportunities_false(self, tmp_path):
        """Test has_parallel_opportunities returns False when no parallel.json."""
        plan_dir = tmp_path / "plans" / "NO-PARALLEL"
        plan_dir.mkdir(parents=True)

        detector = ParallelDetector(plan_dir)
        assert detector.has_parallel_opportunities() is False

    def test_detect_parallel_opportunities_groups(self, test_plan_with_parallel_json):
        """Test detect_parallel_opportunities returns correct groups."""
        detector = ParallelDetector(test_plan_with_parallel_json)
        groups = detector.detect_parallel_opportunities()

        assert len(groups) == 1
        assert groups[0].level == 0
        assert len(groups[0].achievements) == 3
        assert groups[0].achievement_ids == ["3.1", "3.2", "3.3"]

    def test_detect_parallel_opportunities_empty_plan(self, tmp_path):
        """Test detect_parallel_opportunities with no parallel.json."""
        plan_dir = tmp_path / "plans" / "EMPTY"
        plan_dir.mkdir(parents=True)

        detector = ParallelDetector(plan_dir)
        groups = detector.detect_parallel_opportunities()

        assert groups == []

    def test_filter_incomplete_achievements(self, test_plan_with_parallel_json):
        """Test _filter_incomplete removes completed achievements."""
        # Create APPROVED file for one achievement
        feedbacks_dir = test_plan_with_parallel_json / "execution" / "feedbacks"
        feedbacks_dir.mkdir(parents=True)
        (feedbacks_dir / "APPROVED_31.md").write_text("# APPROVED 3.1")

        detector = ParallelDetector(test_plan_with_parallel_json)
        groups = detector.detect_parallel_opportunities()

        # Should have 1 group with 2 achievements (3.2 and 3.3, not 3.1)
        assert len(groups) == 1
        assert len(groups[0].achievements) == 2
        assert "3.1" not in groups[0].achievement_ids
        assert "3.2" in groups[0].achievement_ids
        assert "3.3" in groups[0].achievement_ids


class TestParallelGroup:
    """Tests for ParallelGroup dataclass and time calculations."""

    def test_parallel_group_time_savings(self, tmp_path):
        """Test ParallelGroup calculates time savings correctly."""
        plan_dir = tmp_path / "plans" / "TEST"
        plan_dir.mkdir(parents=True)

        # Create parallel.json with 3 achievements
        parallel_data = {
            "plan_name": "TEST",
            "achievements": [
                {"id": "1.1", "dependencies": []},
                {"id": "1.2", "dependencies": []},
                {"id": "1.3", "dependencies": []},
            ],
        }
        (plan_dir / "parallel.json").write_text(json.dumps(parallel_data))

        detector = ParallelDetector(plan_dir)
        groups = detector.detect_parallel_opportunities()

        assert len(groups) == 1
        group = groups[0]

        # 3 achievements: sequential = 10.5h, parallel = 3.5h, savings = 7h (67%)
        assert group.parallel_time == 3.5
        assert group.sequential_time == 10.5
        assert group.time_savings == 7.0
        assert group.savings_percentage == pytest.approx(66.67, rel=0.1)

    def test_get_first_incomplete_group(self, tmp_path):
        """Test get_first_incomplete_group returns lowest level group."""
        plan_dir = tmp_path / "plans" / "TEST"
        plan_dir.mkdir(parents=True)

        # Create parallel.json with multiple levels
        parallel_data = {
            "plan_name": "TEST",
            "achievements": [
                {"id": "1.1", "dependencies": []},  # Level 0
                {"id": "2.1", "dependencies": ["1.1"]},  # Level 1
            ],
        }
        (plan_dir / "parallel.json").write_text(json.dumps(parallel_data))

        detector = ParallelDetector(plan_dir)
        group = detector.get_first_incomplete_group()

        assert group is not None
        assert group.level == 0
        assert "1.1" in group.achievement_ids


class TestParallelUI:
    """Tests for parallel UI rendering in dashboard."""

    @pytest.fixture
    def plan_with_parallel(self, tmp_path, monkeypatch):
        """Create plan with parallel.json for UI testing."""
        plan_dir = tmp_path / "plans" / "UI-TEST"
        plan_dir.mkdir(parents=True)

        (plan_dir / "PLAN_UI-TEST.md").write_text("# UI Test Plan")

        parallel_data = {
            "plan_name": "UI-TEST",
            "achievements": [
                {"id": "1.1", "dependencies": []},
                {"id": "1.2", "dependencies": []},
            ],
        }
        (plan_dir / "parallel.json").write_text(json.dumps(parallel_data))

        # Mock PlanDiscovery to return test plan
        monkeypatch.setattr(
            "LLM.dashboard.plan_dashboard.PlanDiscovery.get_all_plans", lambda self: [plan_dir]
        )

        return plan_dir

    def test_render_parallel_opportunities_shows_section(self, plan_with_parallel, capsys):
        """Test render_parallel_opportunities displays section when parallel.json exists."""
        console = Console()
        dashboard = PlanDashboard(plan_id=1, console=console)

        # Call render method
        dashboard.render_parallel_opportunities()

        # Verify section was rendered (console output would contain parallel text)
        # Note: This is a smoke test - full UI testing would use Rich's capture
        assert dashboard.parallel_detector.has_parallel_opportunities() is True

    def test_render_parallel_opportunities_hidden_without_json(self, tmp_path, monkeypatch):
        """Test render_parallel_opportunities hidden when no parallel.json."""
        plan_dir = tmp_path / "plans" / "NO-PARALLEL"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_NO-PARALLEL.md").write_text("# No Parallel")

        monkeypatch.setattr(
            "LLM.dashboard.plan_dashboard.PlanDiscovery.get_all_plans", lambda self: [plan_dir]
        )

        console = Console()
        dashboard = PlanDashboard(plan_id=1, console=console)

        # Call render method - should return early (no error)
        dashboard.render_parallel_opportunities()

        assert dashboard.parallel_detector.has_parallel_opportunities() is False

    def test_parallel_action_in_menu(self, plan_with_parallel):
        """Test parallel action appears in action menu when enabled."""
        console = Console()
        dashboard = PlanDashboard(plan_id=1, console=console)

        actions = dashboard._get_available_actions()

        # Find parallel action (action 2)
        parallel_action = next((a for a in actions if a.key == "2"), None)
        assert parallel_action is not None
        assert "Parallel" in parallel_action.label
        assert parallel_action.enabled is True

    def test_parallel_action_disabled_without_opportunities(self, tmp_path, monkeypatch):
        """Test parallel action disabled when no opportunities."""
        plan_dir = tmp_path / "plans" / "NO-OPP"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_NO-OPP.md").write_text("# No Opportunities")

        monkeypatch.setattr(
            "LLM.dashboard.plan_dashboard.PlanDiscovery.get_all_plans", lambda self: [plan_dir]
        )

        console = Console()
        dashboard = PlanDashboard(plan_id=1, console=console)

        actions = dashboard._get_available_actions()

        parallel_action = next((a for a in actions if a.key == "2"), None)
        assert parallel_action is not None
        assert parallel_action.enabled is False


class TestParallelAction:
    """Tests for parallel execution action."""

    @pytest.fixture
    def dashboard_with_parallel(self, tmp_path, monkeypatch):
        """Create dashboard with parallel opportunities."""
        plan_dir = tmp_path / "plans" / "ACTION-TEST"
        plan_dir.mkdir(parents=True)

        (plan_dir / "PLAN_ACTION-TEST.md").write_text("# Action Test")

        parallel_data = {
            "plan_name": "ACTION-TEST",
            "achievements": [
                {"id": "1.1", "dependencies": []},
                {"id": "1.2", "dependencies": []},
            ],
        }
        (plan_dir / "parallel.json").write_text(json.dumps(parallel_data))

        monkeypatch.setattr(
            "LLM.dashboard.plan_dashboard.PlanDiscovery.get_all_plans", lambda self: [plan_dir]
        )

        console = Console()
        return PlanDashboard(plan_id=1, console=console)

    def test_action_execute_parallel_no_opportunities(self, tmp_path, monkeypatch):
        """Test _action_execute_parallel shows message when no opportunities."""
        plan_dir = tmp_path / "plans" / "NO-PARALLEL"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_NO-PARALLEL.md").write_text("# No Parallel")

        monkeypatch.setattr(
            "LLM.dashboard.plan_dashboard.PlanDiscovery.get_all_plans", lambda self: [plan_dir]
        )

        console = Console()
        dashboard = PlanDashboard(plan_id=1, console=console)

        # Mock get_user_input to avoid blocking
        dashboard.get_user_input = Mock(return_value="")

        # Call action - should not raise error
        dashboard._action_execute_parallel()

        # Verify get_user_input was called (waiting for key press)
        assert dashboard.get_user_input.called

    def test_show_parallel_execution_instructions(self, dashboard_with_parallel):
        """Test _show_parallel_execution_instructions displays commands."""
        # Create a mock group
        group = ParallelGroup(
            level=0,
            achievements=[{"id": "1.1"}, {"id": "1.2"}],
            achievement_ids=["1.1", "1.2"],
            parallel_time=3.5,
            sequential_time=7.0,
            time_savings=3.5,
            savings_percentage=50.0,
        )

        # Mock get_user_input to avoid blocking
        dashboard_with_parallel.get_user_input = Mock(return_value="")

        # Call method - should not raise error
        dashboard_with_parallel._show_parallel_execution_instructions(group)

        # Verify get_user_input was called
        assert dashboard_with_parallel.get_user_input.called


class TestIntegration:
    """Integration tests with real parallel.json from PARALLEL-EXECUTION-AUTOMATION."""

    def test_detect_real_parallel_json(self):
        """Test detection with real parallel.json from PARALLEL-EXECUTION-AUTOMATION plan."""
        # This test uses the actual PARALLEL-EXECUTION-AUTOMATION plan if it exists
        parallel_plan_path = (
            Path.cwd() / "work-space" / "plans" / "PARALLEL-EXECUTION-AUTOMATION"
        )

        if not parallel_plan_path.exists():
            pytest.skip("PARALLEL-EXECUTION-AUTOMATION plan not found")

        detector = ParallelDetector(parallel_plan_path)

        if not detector.has_parallel_opportunities():
            pytest.skip("No parallel.json in PARALLEL-EXECUTION-AUTOMATION")

        groups = detector.detect_parallel_opportunities()

        # If all achievements are complete, groups will be empty - that's OK
        if len(groups) == 0:
            pytest.skip("All achievements in PARALLEL-EXECUTION-AUTOMATION are complete")

        # Each group should have valid structure
        for group in groups:
            assert group.level >= 0
            assert len(group.achievements) > 0
            assert len(group.achievement_ids) > 0
            assert group.parallel_time > 0
            assert group.sequential_time > 0
            assert group.time_savings >= 0
            assert 0 <= group.savings_percentage <= 100

    def test_dashboard_with_real_plan(self, monkeypatch):
        """Test dashboard integration with real parallel plan."""
        parallel_plan_path = (
            Path.cwd() / "work-space" / "plans" / "PARALLEL-EXECUTION-AUTOMATION"
        )

        if not parallel_plan_path.exists():
            pytest.skip("PARALLEL-EXECUTION-AUTOMATION plan not found")

        # Mock PlanDiscovery
        monkeypatch.setattr(
            "LLM.dashboard.plan_dashboard.PlanDiscovery.get_all_plans",
            lambda self: [parallel_plan_path],
        )

        console = Console()
        dashboard = PlanDashboard(plan_id=1, console=console)

        # Should initialize without error
        assert dashboard.parallel_detector is not None

        # Render should work without error
        dashboard.render_parallel_opportunities()

    def test_filter_by_dependency_level_integration(self):
        """Test integration with batch_subplan's filter_by_dependency_level."""
        from LLM.scripts.generation.batch_subplan import filter_by_dependency_level

        # Create test achievements (using achievement_id field as expected by batch tools)
        achievements = [
            {"achievement_id": "1.1", "dependencies": []},  # Level 0
            {"achievement_id": "1.2", "dependencies": []},  # Level 0
            {"achievement_id": "2.1", "dependencies": ["1.1"]},  # Level 1
        ]

        # Filter to level 0
        level_0 = filter_by_dependency_level(achievements, level=0)

        assert len(level_0) == 2
        assert level_0[0]["achievement_id"] == "1.1"
        assert level_0[1]["achievement_id"] == "1.2"

