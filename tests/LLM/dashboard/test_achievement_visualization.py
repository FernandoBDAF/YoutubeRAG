"""
Tests for achievement visualization features.

Tests achievement list rendering, status formatting, health score calculation,
and stale execution detection.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from rich.console import Console

from LLM.dashboard.plan_dashboard import PlanDashboard, HealthScore
from LLM.dashboard.models import PlanState, PlanStatus


class TestAchievementParsing:
    """Tests for achievement parsing from PLAN file."""
    
    def test_get_all_achievements_basic(self, tmp_path):
        """Test parsing achievements from PLAN file."""
        plan_dir = tmp_path / "work-space" / "plans" / "TEST-PLAN"
        plan_dir.mkdir(parents=True)
        
        plan_content = """# Test Plan

## Achievement Index

- Achievement 0.1: First Achievement
- Achievement 0.2: Second Achievement
- Achievement 1.1: Third Achievement

## Next Section
"""
        (plan_dir / "PLAN_TEST-PLAN.md").write_text(plan_content)
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="TEST-PLAN",
            plan_file=plan_dir / "PLAN_TEST-PLAN.md",
            last_achievement=None,
            next_achievements=[],
            pending_reviews=[],
            pending_fixes=[],
            total_achievements=3,
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
            
            achievements = dashboard._get_all_achievements()
            
            assert len(achievements) == 3
            assert achievements[0]['number'] == '0.1'
            assert achievements[0]['title'] == 'First Achievement'
            assert achievements[1]['number'] == '0.2'
            assert achievements[2]['number'] == '1.1'
    
    def test_get_all_achievements_no_index(self, tmp_path):
        """Test when Achievement Index section missing."""
        plan_dir = tmp_path / "work-space" / "plans" / "NO-INDEX"
        plan_dir.mkdir(parents=True)
        
        plan_content = """# Test Plan

## Some Other Section

Content here
"""
        (plan_dir / "PLAN_NO-INDEX.md").write_text(plan_content)
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="NO-INDEX",
            plan_file=plan_dir / "PLAN_NO-INDEX.md",
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
            
            achievements = dashboard._get_all_achievements()
            
            assert len(achievements) == 0


class TestStatusFormatting:
    """Tests for status formatting."""
    
    @pytest.fixture
    def dashboard_with_plan(self, tmp_path):
        """Create dashboard with test plan."""
        plan_dir = tmp_path / "work-space" / "plans" / "TEST-PLAN"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_TEST-PLAN.md").write_text("# Test")
        
        # Create directories
        (plan_dir / "subplans").mkdir()
        (plan_dir / "execution").mkdir()
        (plan_dir / "execution" / "feedbacks").mkdir()
        
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
            return dashboard, plan_dir
    
    def test_format_status_approved(self, dashboard_with_plan):
        """Test approved achievement status."""
        dashboard, plan_dir = dashboard_with_plan
        
        # Create APPROVED file
        (plan_dir / "execution" / "feedbacks" / "APPROVED_11.md").write_text("# APPROVED")
        
        ach = {'number': '1.1', 'title': 'Test'}
        status = dashboard._format_status(ach)
        
        assert "✅" in status
        assert "APPROVED" in status
    
    def test_format_status_fix_pending(self, dashboard_with_plan):
        """Test fix pending status."""
        dashboard, plan_dir = dashboard_with_plan
        
        # Create FIX file
        (plan_dir / "execution" / "feedbacks" / "FIX_12.md").write_text("# FIX")
        
        ach = {'number': '1.2', 'title': 'Test'}
        status = dashboard._format_status(ach)
        
        assert "⚠️" in status
        assert "FIX" in status
    
    def test_format_status_in_progress(self, dashboard_with_plan):
        """Test in progress status."""
        dashboard, plan_dir = dashboard_with_plan
        
        # Create EXECUTION file
        (plan_dir / "execution" / "EXECUTION_TASK_TEST-PLAN_13_01.md").write_text("# EXECUTION")
        
        ach = {'number': '1.3', 'title': 'Test'}
        status = dashboard._format_status(ach)
        
        assert "🔄" in status
        assert "progress" in status.lower()
    
    def test_format_status_subplan_ready(self, dashboard_with_plan):
        """Test SUBPLAN ready status."""
        dashboard, plan_dir = dashboard_with_plan
        
        # Create SUBPLAN file
        (plan_dir / "subplans" / "SUBPLAN_TEST-PLAN_14.md").write_text("# SUBPLAN")
        
        ach = {'number': '1.4', 'title': 'Test'}
        status = dashboard._format_status(ach)
        
        assert "📝" in status
        assert "SUBPLAN" in status
    
    def test_format_status_not_started(self, dashboard_with_plan):
        """Test not started status."""
        dashboard, plan_dir = dashboard_with_plan
        
        ach = {'number': '2.1', 'title': 'Test'}
        status = dashboard._format_status(ach)
        
        assert "⏸️" in status
        assert "Not started" in status
    
    def test_format_action_complete(self, dashboard_with_plan):
        """Test action for completed achievement."""
        dashboard, plan_dir = dashboard_with_plan
        
        (plan_dir / "execution" / "feedbacks" / "APPROVED_11.md").write_text("# APPROVED")
        
        ach = {'number': '1.1', 'title': 'Test'}
        action = dashboard._format_action(ach)
        
        assert "Complete" in action
    
    def test_format_action_fix(self, dashboard_with_plan):
        """Test action for fix pending."""
        dashboard, plan_dir = dashboard_with_plan
        
        (plan_dir / "execution" / "feedbacks" / "FIX_12.md").write_text("# FIX")
        
        ach = {'number': '1.2', 'title': 'Test'}
        action = dashboard._format_action(ach)
        
        assert "Fix" in action


class TestHealthScore:
    """Tests for plan health score calculation."""
    
    def test_calculate_health_score_perfect(self, tmp_path):
        """Test health score for perfect plan."""
        plan_dir = tmp_path / "work-space" / "plans" / "PERFECT-PLAN"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_PERFECT-PLAN.md").write_text("# Perfect")
        
        # Create structure with no issues
        (plan_dir / "execution" / "feedbacks").mkdir(parents=True)
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="PERFECT-PLAN",
            plan_file=plan_dir / "PLAN_PERFECT-PLAN.md",
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
            
            health = dashboard.calculate_health_score()
            
            # 30 (completion) + 20 (no fixes) + 20 (no stale) = 70
            assert health.score == 70.0
            assert health.breakdown['completion'] == 30.0
            assert health.breakdown['no_fixes'] == 20.0
            assert health.breakdown['no_stale'] == 20.0
    
    def test_calculate_health_score_with_fixes(self, tmp_path):
        """Test health score with pending fixes."""
        plan_dir = tmp_path / "work-space" / "plans" / "HAS-FIXES"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_HAS-FIXES.md").write_text("# Has Fixes")
        
        feedbacks_dir = plan_dir / "execution" / "feedbacks"
        feedbacks_dir.mkdir(parents=True)
        (feedbacks_dir / "FIX_12.md").write_text("# FIX")
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="HAS-FIXES",
            plan_file=plan_dir / "PLAN_HAS-FIXES.md",
            last_achievement="1.1",
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
            
            health = dashboard.calculate_health_score()
            
            # 15 (50% completion) + 0 (has fixes) + 20 (no stale) = 35
            assert health.score == 35.0
            assert health.breakdown['no_fixes'] == 0.0
    
    def test_count_stale_executions_none(self, tmp_path):
        """Test stale execution count when none exist."""
        plan_dir = tmp_path / "work-space" / "plans" / "NO-STALE"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_NO-STALE.md").write_text("# No Stale")
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="NO-STALE",
            plan_file=plan_dir / "PLAN_NO-STALE.md",
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
            
            stale_count = dashboard._count_stale_executions()
            
            assert stale_count == 0
    
    def test_count_stale_executions_with_stale(self, tmp_path):
        """Test stale execution detection."""
        plan_dir = tmp_path / "work-space" / "plans" / "HAS-STALE"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_HAS-STALE.md").write_text("# Has Stale")
        
        execution_dir = plan_dir / "execution"
        execution_dir.mkdir()
        feedbacks_dir = execution_dir / "feedbacks"
        feedbacks_dir.mkdir()
        
        # Create old EXECUTION file (>7 days)
        exec_file = execution_dir / "EXECUTION_TASK_HAS-STALE_11_01.md"
        exec_file.write_text("# Old EXECUTION")
        
        # Set mtime to 10 days ago
        ten_days_ago = datetime.now() - timedelta(days=10)
        import os
        os.utime(exec_file, (ten_days_ago.timestamp(), ten_days_ago.timestamp()))
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="HAS-STALE",
            plan_file=plan_dir / "PLAN_HAS-STALE.md",
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
            
            stale_count = dashboard._count_stale_executions()
            
            assert stale_count == 1
    
    def test_get_health_status_ranges(self, tmp_path):
        """Test health status for different score ranges."""
        plan_dir = tmp_path / "work-space" / "plans" / "TEST"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_TEST.md").write_text("# Test")
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="TEST",
            plan_file=plan_dir / "PLAN_TEST.md",
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
            
            assert dashboard._get_health_status(100) == "Excellent"
            assert dashboard._get_health_status(95) == "Excellent"
            assert dashboard._get_health_status(90) == "Good"
            assert dashboard._get_health_status(80) == "Good"
            assert dashboard._get_health_status(70) == "Fair"
            assert dashboard._get_health_status(60) == "Fair"
            assert dashboard._get_health_status(50) == "Needs Attention"
    
    def test_get_health_emoji_ranges(self, tmp_path):
        """Test health emoji for different score ranges."""
        plan_dir = tmp_path / "work-space" / "plans" / "TEST"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_TEST.md").write_text("# Test")
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="TEST",
            plan_file=plan_dir / "PLAN_TEST.md",
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
            
            assert dashboard._get_health_emoji(100) == "🟢"
            assert dashboard._get_health_emoji(95) == "🟢"
            assert dashboard._get_health_emoji(90) == "🟡"
            assert dashboard._get_health_emoji(80) == "🟡"
            assert dashboard._get_health_emoji(70) == "🟠"
            assert dashboard._get_health_emoji(60) == "🟠"
            assert dashboard._get_health_emoji(50) == "🔴"


class TestRendering:
    """Tests for rendering methods."""
    
    def test_render_achievements(self, tmp_path):
        """Test achievement table rendering."""
        plan_dir = tmp_path / "work-space" / "plans" / "TEST"
        plan_dir.mkdir(parents=True)
        
        plan_content = """# Test

## Achievement Index

- Achievement 1.1: First
- Achievement 1.2: Second
"""
        (plan_dir / "PLAN_TEST.md").write_text(plan_content)
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="TEST",
            plan_file=plan_dir / "PLAN_TEST.md",
            last_achievement=None,
            next_achievements=[],
            pending_reviews=[],
            pending_fixes=[],
            total_achievements=2,
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
            dashboard.render_achievements()
    
    def test_render_health_score(self, tmp_path):
        """Test health score rendering."""
        plan_dir = tmp_path / "work-space" / "plans" / "TEST"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_TEST.md").write_text("# Test")
        
        (plan_dir / "execution" / "feedbacks").mkdir(parents=True)
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="TEST",
            plan_file=plan_dir / "PLAN_TEST.md",
            last_achievement="1.1",
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
            dashboard.render_health_score()

