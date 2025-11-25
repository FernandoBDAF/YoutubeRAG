"""
Tests for plan-specific dashboard.

Tests plan resolution, status rendering, stats calculation, and navigation.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from rich.console import Console

from LLM.dashboard.plan_dashboard import PlanDashboard
from LLM.dashboard.models import PlanState, AchievementState, PlanStatus


class TestPlanDashboard:
    """Tests for PlanDashboard class."""
    
    @pytest.fixture
    def test_plan_structure(self, tmp_path):
        """Create test plan structure."""
        plans_root = tmp_path / "work-space" / "plans"
        plans_root.mkdir(parents=True)
        
        plan_dir = plans_root / "TEST-PLAN"
        plan_dir.mkdir()
        
        # Create PLAN file
        (plan_dir / "PLAN_TEST-PLAN.md").write_text("# Test Plan\n\n## Achievement Index\n- Achievement 1.1: Test")
        
        # Create subplans
        subplans_dir = plan_dir / "subplans"
        subplans_dir.mkdir()
        (subplans_dir / "SUBPLAN_TEST-PLAN_11.md").write_text("# SUBPLAN 1.1")
        (subplans_dir / "SUBPLAN_TEST-PLAN_12.md").write_text("# SUBPLAN 1.2")
        
        # Create feedbacks
        feedbacks_dir = plan_dir / "execution" / "feedbacks"
        feedbacks_dir.mkdir(parents=True)
        (feedbacks_dir / "APPROVED_11.md").write_text("# APPROVED 1.1")
        (feedbacks_dir / "FIX_12.md").write_text("# FIX 1.2")
        
        # Create EXECUTION files
        execution_dir = plan_dir / "execution"
        (execution_dir / "EXECUTION_TASK_TEST-PLAN_11_01.md").write_text("# EXECUTION 1.1")
        (execution_dir / "EXECUTION_TASK_TEST-PLAN_12_01.md").write_text("# EXECUTION 1.2")
        
        return plan_dir
    
    def test_init_with_plan_number(self, test_plan_structure, monkeypatch):
        """Test initialization with plan number."""
        # Mock PlanDiscovery.get_all_plans
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [test_plan_structure]
        
        # Mock StateDetector
        mock_state = PlanState(
            name="TEST-PLAN",
            plan_file=test_plan_structure / "PLAN_TEST-PLAN.md",
            last_achievement="1.1",
            next_achievements=[],
            pending_reviews=[],
            pending_fixes=[],
            total_achievements=10,
            completed_achievements=2,
            progress_percentage=20.0,
            status=PlanStatus.ACTIVE
        )
        mock_state_detector = Mock()
        mock_state_detector.get_plan_state.return_value = mock_state
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery', return_value=mock_discovery), \
             patch('LLM.dashboard.plan_dashboard.StateDetector', return_value=mock_state_detector):
            
            console = Console()
            dashboard = PlanDashboard(plan_id=1, console=console)
            
            assert dashboard.plan_path == test_plan_structure
            assert dashboard.plan_name == "TEST-PLAN"
            assert dashboard.state == mock_state
    
    def test_init_with_plan_name_with_at(self, test_plan_structure, monkeypatch):
        """Test initialization with @-prefixed plan name."""
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [test_plan_structure]
        
        mock_state = PlanState(
            name="TEST-PLAN",
            plan_file=test_plan_structure / "PLAN_TEST-PLAN.md",
            last_achievement=None,
            next_achievements=[],
            pending_reviews=[],
            pending_fixes=[],
            total_achievements=10,
            completed_achievements=0,
            progress_percentage=0.0,
            status=PlanStatus.ACTIVE
        )
        mock_state_detector = Mock()
        mock_state_detector.get_plan_state.return_value = mock_state
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery', return_value=mock_discovery), \
             patch('LLM.dashboard.plan_dashboard.StateDetector', return_value=mock_state_detector):
            
            console = Console()
            dashboard = PlanDashboard(plan_id="@TEST-PLAN", console=console)
            
            assert dashboard.plan_path == test_plan_structure
            assert dashboard.plan_name == "TEST-PLAN"
    
    def test_init_with_plan_name_without_at(self, test_plan_structure, monkeypatch):
        """Test initialization with plan name without @."""
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [test_plan_structure]
        
        mock_state = PlanState(
            name="TEST-PLAN",
            plan_file=test_plan_structure / "PLAN_TEST-PLAN.md",
            last_achievement=None,
            next_achievements=[],
            pending_reviews=[],
            pending_fixes=[],
            total_achievements=10,
            completed_achievements=0,
            progress_percentage=0.0,
            status=PlanStatus.ACTIVE
        )
        mock_state_detector = Mock()
        mock_state_detector.get_plan_state.return_value = mock_state
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery', return_value=mock_discovery), \
             patch('LLM.dashboard.plan_dashboard.StateDetector', return_value=mock_state_detector):
            
            console = Console()
            dashboard = PlanDashboard(plan_id="TEST-PLAN", console=console)
            
            assert dashboard.plan_path == test_plan_structure
    
    def test_resolve_plan_invalid_number(self, monkeypatch):
        """Test plan resolution with invalid number."""
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = []
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery', return_value=mock_discovery):
            console = Console()
            
            with pytest.raises(ValueError, match="out of range"):
                PlanDashboard(plan_id=999, console=console)
    
    def test_resolve_plan_not_found(self, monkeypatch):
        """Test plan resolution with non-existent name."""
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = []
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery', return_value=mock_discovery):
            console = Console()
            
            with pytest.raises(ValueError, match="Plan not found"):
                PlanDashboard(plan_id="@NONEXISTENT", console=console)


class TestStatsCalculation:
    """Tests for stats calculation."""
    
    def test_calculate_stats_empty_plan(self, tmp_path):
        """Test stats calculation for empty plan."""
        plan_dir = tmp_path / "work-space" / "plans" / "EMPTY-PLAN"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_EMPTY-PLAN.md").write_text("# Empty Plan\n\n## Achievement Index\n")
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="EMPTY-PLAN",
            plan_file=plan_dir / "PLAN_EMPTY-PLAN.md",
            last_achievement=None,
            next_achievements=[],
            pending_reviews=[],
            pending_fixes=[],
            total_achievements=0,
            completed_achievements=0,
            progress_percentage=0.0,
            status=PlanStatus.ACTIVE
        )
        mock_state_detector = Mock()
        mock_state_detector.get_plan_state.return_value = mock_state
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery', return_value=mock_discovery), \
             patch('LLM.dashboard.plan_dashboard.StateDetector', return_value=mock_state_detector):
            
            console = Console()
            dashboard = PlanDashboard(plan_id=1, console=console)
            
            stats = dashboard._calculate_stats()
            
            assert stats['subplans_created'] == 0
            assert stats['reviews_approved'] == 0
            assert stats['reviews_pending'] == 0
            assert stats['tests_passing'] == 0
            assert stats['tests_total'] == 0
    
    def test_calculate_stats_with_artifacts(self, tmp_path):
        """Test stats calculation with artifacts."""
        plan_dir = tmp_path / "work-space" / "plans" / "TEST-PLAN"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_TEST-PLAN.md").write_text("# Test Plan\n\n## Achievement Index\n")
        
        # Create SUBPLANs
        subplans_dir = plan_dir / "subplans"
        subplans_dir.mkdir()
        (subplans_dir / "SUBPLAN_TEST-PLAN_11.md").write_text("# SUBPLAN 1.1")
        (subplans_dir / "SUBPLAN_TEST-PLAN_12.md").write_text("# SUBPLAN 1.2")
        
        # Create feedbacks
        feedbacks_dir = plan_dir / "execution" / "feedbacks"
        feedbacks_dir.mkdir(parents=True)
        (feedbacks_dir / "APPROVED_11.md").write_text("# APPROVED 1.1")
        (feedbacks_dir / "APPROVED_12.md").write_text("# APPROVED 1.2")
        (feedbacks_dir / "FIX_13.md").write_text("# FIX 1.3")
        
        # Create EXECUTION files
        execution_dir = plan_dir / "execution"
        (execution_dir / "EXECUTION_TASK_TEST-PLAN_11_01.md").write_text("# EXECUTION 1.1")
        (execution_dir / "EXECUTION_TASK_TEST-PLAN_12_01.md").write_text("# EXECUTION 1.2")
        (execution_dir / "EXECUTION_TASK_TEST-PLAN_13_01.md").write_text("# EXECUTION 1.3")
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="TEST-PLAN",
            plan_file=plan_dir / "PLAN_TEST-PLAN.md",
            last_achievement="1.2",
            next_achievements=[],
            pending_reviews=[],
            pending_fixes=[],
            total_achievements=10,
            completed_achievements=2,
            progress_percentage=20.0,
            status=PlanStatus.ACTIVE
        )
        mock_state_detector = Mock()
        mock_state_detector.get_plan_state.return_value = mock_state
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery', return_value=mock_discovery), \
             patch('LLM.dashboard.plan_dashboard.StateDetector', return_value=mock_state_detector):
            
            console = Console()
            dashboard = PlanDashboard(plan_id=1, console=console)
            
            stats = dashboard._calculate_stats()
            
            assert stats['subplans_created'] == 2
            assert stats['reviews_approved'] == 2
            assert stats['reviews_pending'] == 1
            assert stats['executions_active'] == 3


class TestEstimations:
    """Tests for estimation functions."""
    
    def test_estimate_remaining_hours_zero(self, tmp_path):
        """Test remaining hours estimation when complete."""
        plan_dir = tmp_path / "work-space" / "plans" / "COMPLETE-PLAN"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_COMPLETE-PLAN.md").write_text("# Complete Plan")
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="COMPLETE-PLAN",
            plan_file=plan_dir / "PLAN_COMPLETE-PLAN.md",
            last_achievement="3.3",
            next_achievements=[],
            pending_reviews=[],
            pending_fixes=[],
            total_achievements=10,
            completed_achievements=10,
            progress_percentage=100.0,
            status=PlanStatus.ACTIVE
        )
        mock_state_detector = Mock()
        mock_state_detector.get_plan_state.return_value = mock_state
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery', return_value=mock_discovery), \
             patch('LLM.dashboard.plan_dashboard.StateDetector', return_value=mock_state_detector):
            
            console = Console()
            dashboard = PlanDashboard(plan_id=1, console=console)
            
            remaining = dashboard._estimate_remaining_hours()
            
            assert "0" in remaining
            assert "complete" in remaining.lower()
    
    def test_estimate_remaining_hours_single(self, tmp_path):
        """Test remaining hours estimation with single achievement."""
        plan_dir = tmp_path / "work-space" / "plans" / "ALMOST-COMPLETE"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_ALMOST-COMPLETE.md").write_text("# Almost Complete")
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="ALMOST-COMPLETE",
            plan_file=plan_dir / "PLAN_ALMOST-COMPLETE.md",
            last_achievement="2.3",
            next_achievements=[],
            pending_reviews=[],
            pending_fixes=[],
            total_achievements=10,
            completed_achievements=9,
            progress_percentage=90.0,
            status=PlanStatus.ACTIVE
        )
        mock_state_detector = Mock()
        mock_state_detector.get_plan_state.return_value = mock_state
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery', return_value=mock_discovery), \
             patch('LLM.dashboard.plan_dashboard.StateDetector', return_value=mock_state_detector):
            
            console = Console()
            dashboard = PlanDashboard(plan_id=1, console=console)
            
            remaining = dashboard._estimate_remaining_hours()
            
            assert "3-4" in remaining
    
    def test_estimate_remaining_hours_multiple(self, tmp_path):
        """Test remaining hours estimation with multiple achievements."""
        plan_dir = tmp_path / "work-space" / "plans" / "ACTIVE-PLAN"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_ACTIVE-PLAN.md").write_text("# Active Plan")
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="ACTIVE-PLAN",
            plan_file=plan_dir / "PLAN_ACTIVE-PLAN.md",
            last_achievement="1.2",
            next_achievements=[],
            pending_reviews=[],
            pending_fixes=[],
            total_achievements=10,
            completed_achievements=7,
            progress_percentage=70.0,
            status=PlanStatus.ACTIVE
        )
        mock_state_detector = Mock()
        mock_state_detector.get_plan_state.return_value = mock_state
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery', return_value=mock_discovery), \
             patch('LLM.dashboard.plan_dashboard.StateDetector', return_value=mock_state_detector):
            
            console = Console()
            dashboard = PlanDashboard(plan_id=1, console=console)
            
            remaining = dashboard._estimate_remaining_hours()
            
            # 3 pending * 3-4 hours = 9-12 hours
            assert "9" in remaining or "12" in remaining
    
    def test_get_current_priority(self, tmp_path):
        """Test priority description (placeholder for MVP)."""
        plan_dir = tmp_path / "work-space" / "plans" / "TEST-PLAN"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_TEST-PLAN.md").write_text("# Test Plan")
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="TEST-PLAN",
            plan_file=plan_dir / "PLAN_TEST-PLAN.md",
            last_achievement=None,
            next_achievements=[],
            pending_reviews=[],
            pending_fixes=[],
            total_achievements=10,
            completed_achievements=0,
            progress_percentage=0.0,
            status=PlanStatus.ACTIVE
        )
        mock_state_detector = Mock()
        mock_state_detector.get_plan_state.return_value = mock_state
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery', return_value=mock_discovery), \
             patch('LLM.dashboard.plan_dashboard.StateDetector', return_value=mock_state_detector):
            
            console = Console()
            dashboard = PlanDashboard(plan_id=1, console=console)
            
            priority = dashboard._get_current_priority()
            
            # For MVP, returns placeholder
            assert "Unknown" in priority or "will implement" in priority


class TestRendering:
    """Tests for dashboard rendering methods."""
    
    def test_render_header(self, tmp_path):
        """Test header rendering."""
        plan_dir = tmp_path / "work-space" / "plans" / "TEST-PLAN"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_TEST-PLAN.md").write_text("# Test Plan")
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="TEST-PLAN",
            plan_file=plan_dir / "PLAN_TEST-PLAN.md",
            last_achievement=None,
            next_achievements=[],
            pending_reviews=[],
            pending_fixes=[],
            total_achievements=10,
            completed_achievements=0,
            progress_percentage=0.0,
            status=PlanStatus.ACTIVE
        )
        mock_state_detector = Mock()
        mock_state_detector.get_plan_state.return_value = mock_state
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery', return_value=mock_discovery), \
             patch('LLM.dashboard.plan_dashboard.StateDetector', return_value=mock_state_detector):
            
            console = Console()
            dashboard = PlanDashboard(plan_id=1, console=console)
            
            # Should not raise
            dashboard.render_header()
    
    def test_render_status(self, tmp_path):
        """Test status rendering."""
        plan_dir = tmp_path / "work-space" / "plans" / "TEST-PLAN"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_TEST-PLAN.md").write_text("# Test Plan")
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="TEST-PLAN",
            plan_file=plan_dir / "PLAN_TEST-PLAN.md",
            last_achievement="2.1",
            next_achievements=[],
            pending_reviews=[],
            pending_fixes=[],
            total_achievements=10,
            completed_achievements=5,
            progress_percentage=50.0,
            status=PlanStatus.ACTIVE
        )
        mock_state_detector = Mock()
        mock_state_detector.get_plan_state.return_value = mock_state
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery', return_value=mock_discovery), \
             patch('LLM.dashboard.plan_dashboard.StateDetector', return_value=mock_state_detector):
            
            console = Console()
            dashboard = PlanDashboard(plan_id=1, console=console)
            
            # Should not raise
            dashboard.render_status()
    
    def test_render_stats(self, tmp_path):
        """Test stats rendering."""
        plan_dir = tmp_path / "work-space" / "plans" / "TEST-PLAN"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_TEST-PLAN.md").write_text("# Test Plan")
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="TEST-PLAN",
            plan_file=plan_dir / "PLAN_TEST-PLAN.md",
            last_achievement=None,
            next_achievements=[],
            pending_reviews=[],
            pending_fixes=[],
            total_achievements=10,
            completed_achievements=0,
            progress_percentage=0.0,
            status=PlanStatus.ACTIVE
        )
        mock_state_detector = Mock()
        mock_state_detector.get_plan_state.return_value = mock_state
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery', return_value=mock_discovery), \
             patch('LLM.dashboard.plan_dashboard.StateDetector', return_value=mock_state_detector):
            
            console = Console()
            dashboard = PlanDashboard(plan_id=1, console=console)
            
            # Should not raise
            dashboard.render_stats()


class TestNavigation:
    """Tests for dashboard navigation."""
    
    def test_show_exits_on_back(self, tmp_path):
        """Test that show() exits when user presses 'b'."""
        plan_dir = tmp_path / "work-space" / "plans" / "TEST-PLAN"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_TEST-PLAN.md").write_text("# Test Plan")
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="TEST-PLAN",
            plan_file=plan_dir / "PLAN_TEST-PLAN.md",
            last_achievement=None,
            next_achievements=[],
            pending_reviews=[],
            pending_fixes=[],
            total_achievements=10,
            completed_achievements=0,
            progress_percentage=0.0,
            status=PlanStatus.ACTIVE
        )
        mock_state_detector = Mock()
        mock_state_detector.get_plan_state.return_value = mock_state
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery', return_value=mock_discovery), \
             patch('LLM.dashboard.plan_dashboard.StateDetector', return_value=mock_state_detector):
            
            console = Console()
            dashboard = PlanDashboard(plan_id=1, console=console)
            
            # Mock user input to return 'b'
            with patch.object(dashboard, 'get_user_input', return_value='b'):
                dashboard.show()  # Should exit without error
    
    def test_show_exits_on_6(self, tmp_path):
        """Test that show() exits when user presses '6'."""
        plan_dir = tmp_path / "work-space" / "plans" / "TEST-PLAN"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_TEST-PLAN.md").write_text("# Test Plan")
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="TEST-PLAN",
            plan_file=plan_dir / "PLAN_TEST-PLAN.md",
            last_achievement=None,
            next_achievements=[],
            pending_reviews=[],
            pending_fixes=[],
            total_achievements=10,
            completed_achievements=0,
            progress_percentage=0.0,
            status=PlanStatus.ACTIVE
        )
        mock_state_detector = Mock()
        mock_state_detector.get_plan_state.return_value = mock_state
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery', return_value=mock_discovery), \
             patch('LLM.dashboard.plan_dashboard.StateDetector', return_value=mock_state_detector):
            
            console = Console()
            dashboard = PlanDashboard(plan_id=1, console=console)
            
            # Mock user input to return '6'
            with patch.object(dashboard, 'get_user_input', return_value='6'):
                dashboard.show()  # Should exit without error
    
    def test_show_exits_on_back_word(self, tmp_path):
        """Test that show() exits when user types 'back'."""
        plan_dir = tmp_path / "work-space" / "plans" / "TEST-PLAN"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_TEST-PLAN.md").write_text("# Test Plan")
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="TEST-PLAN",
            plan_file=plan_dir / "PLAN_TEST-PLAN.md",
            last_achievement=None,
            next_achievements=[],
            pending_reviews=[],
            pending_fixes=[],
            total_achievements=10,
            completed_achievements=0,
            progress_percentage=0.0,
            status=PlanStatus.ACTIVE
        )
        mock_state_detector = Mock()
        mock_state_detector.get_plan_state.return_value = mock_state
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery', return_value=mock_discovery), \
             patch('LLM.dashboard.plan_dashboard.StateDetector', return_value=mock_state_detector):
            
            console = Console()
            dashboard = PlanDashboard(plan_id=1, console=console)
            
            # Mock user input to return 'back'
            with patch.object(dashboard, 'get_user_input', return_value='back'):
                dashboard.show()  # Should exit without error

