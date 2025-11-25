"""
Tests for plan_discovery module.

Tests plan discovery logic.
"""

import pytest
from pathlib import Path

from LLM.dashboard.plan_discovery import PlanDiscovery


class TestPlanDiscovery:
    """Tests for PlanDiscovery class."""

    def test_init_default_path(self):
        """Test initialization with default path."""
        discovery = PlanDiscovery()

        assert discovery.plans_root == Path("work-space/plans")

    def test_init_custom_path(self):
        """Test initialization with custom path."""
        custom_path = Path("/custom/plans")
        discovery = PlanDiscovery(plans_root=custom_path)

        assert discovery.plans_root == custom_path

    def test_get_all_plans_with_real_plans(self):
        """Test get_all_plans() with real project plans."""
        discovery = PlanDiscovery()
        plans = discovery.get_all_plans()

        # Should find at least LLM-DASHBOARD-CLI plan
        assert len(plans) > 0
        assert all(p.is_dir() for p in plans)
        assert all(not p.name.startswith(".") for p in plans)

    def test_get_all_plans_nonexistent_root(self):
        """Test get_all_plans() with nonexistent root."""
        discovery = PlanDiscovery(plans_root=Path("/nonexistent/path"))
        plans = discovery.get_all_plans()

        assert plans == []

    def test_get_all_plans_filters_hidden(self, tmp_path):
        """Test that hidden directories are filtered."""
        plans_root = tmp_path / "plans"
        plans_root.mkdir()

        # Create visible and hidden directories
        (plans_root / "VISIBLE-PLAN").mkdir()
        (plans_root / ".hidden-plan").mkdir()

        discovery = PlanDiscovery(plans_root=plans_root)
        plans = discovery.get_all_plans()

        assert len(plans) == 1
        assert plans[0].name == "VISIBLE-PLAN"

    def test_get_all_plans_filters_files(self, tmp_path):
        """Test that files are filtered out."""
        plans_root = tmp_path / "plans"
        plans_root.mkdir()

        # Create directory and file
        (plans_root / "PLAN-DIR").mkdir()
        (plans_root / "plan-file.txt").touch()

        discovery = PlanDiscovery(plans_root=plans_root)
        plans = discovery.get_all_plans()

        assert len(plans) == 1
        assert plans[0].name == "PLAN-DIR"

    def test_get_all_plans_sorted(self, tmp_path):
        """Test that plans are sorted alphabetically."""
        plans_root = tmp_path / "plans"
        plans_root.mkdir()

        # Create plans in non-alphabetical order
        (plans_root / "PLAN-C").mkdir()
        (plans_root / "PLAN-A").mkdir()
        (plans_root / "PLAN-B").mkdir()

        discovery = PlanDiscovery(plans_root=plans_root)
        plans = discovery.get_all_plans()

        assert len(plans) == 3
        assert [p.name for p in plans] == ["PLAN-A", "PLAN-B", "PLAN-C"]

    def test_get_plan_file_exists(self, tmp_path):
        """Test get_plan_file() when PLAN file exists."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        plan_file = plan_dir / "PLAN_MY-PLAN.md"
        plan_file.touch()

        discovery = PlanDiscovery()
        result = discovery.get_plan_file(plan_dir)

        assert result == plan_file

    def test_get_plan_file_not_exists(self, tmp_path):
        """Test get_plan_file() when PLAN file doesn't exist."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()

        discovery = PlanDiscovery()
        result = discovery.get_plan_file(plan_dir)

        assert result is None

    def test_get_plan_file_nonexistent_dir(self):
        """Test get_plan_file() with nonexistent directory."""
        discovery = PlanDiscovery()
        result = discovery.get_plan_file(Path("/nonexistent/dir"))

        assert result is None

    def test_get_plan_file_multiple_files(self, tmp_path):
        """Test get_plan_file() when multiple PLAN files exist."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        plan_file1 = plan_dir / "PLAN_MY-PLAN.md"
        plan_file2 = plan_dir / "PLAN_OLD.md"
        plan_file1.touch()
        plan_file2.touch()

        discovery = PlanDiscovery()
        result = discovery.get_plan_file(plan_dir)

        # Should return one of them (first found)
        assert result in [plan_file1, plan_file2]

    def test_get_plan_name(self, tmp_path):
        """Test get_plan_name() extracts directory name."""
        plan_dir = tmp_path / "MY-AWESOME-PLAN"

        discovery = PlanDiscovery()
        name = discovery.get_plan_name(plan_dir)

        assert name == "MY-AWESOME-PLAN"

    def test_validate_plan_structure_valid(self, tmp_path):
        """Test validate_plan_structure() with valid structure."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").touch()
        (plan_dir / "execution").mkdir()
        (plan_dir / "subplans").mkdir()

        discovery = PlanDiscovery()
        result = discovery.validate_plan_structure(plan_dir)

        assert result is True

    def test_validate_plan_structure_missing_plan_file(self, tmp_path):
        """Test validate_plan_structure() with missing PLAN file."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "execution").mkdir()
        (plan_dir / "subplans").mkdir()

        discovery = PlanDiscovery()
        result = discovery.validate_plan_structure(plan_dir)

        assert result is False

    def test_validate_plan_structure_missing_execution_dir(self, tmp_path):
        """Test validate_plan_structure() with missing execution dir."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").touch()
        (plan_dir / "subplans").mkdir()

        discovery = PlanDiscovery()
        result = discovery.validate_plan_structure(plan_dir)

        assert result is False

    def test_validate_plan_structure_missing_subplans_dir(self, tmp_path):
        """Test validate_plan_structure() with missing subplans dir."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").touch()
        (plan_dir / "execution").mkdir()

        discovery = PlanDiscovery()
        result = discovery.validate_plan_structure(plan_dir)

        assert result is False
