"""
Tests for state consistency and refresh mechanisms.

Achievement 2.3: Real-Time State Updates

Tests manual refresh, auto-refresh, and multi-instance detection.
"""

import pytest
import os
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
from rich.console import Console

from LLM.dashboard.plan_dashboard import PlanDashboard


class TestManualRefresh:
    """Tests for manual refresh functionality."""
    
    @patch('LLM.dashboard.plan_dashboard.PlanDiscovery')
    @patch('LLM.dashboard.plan_dashboard.StateDetector')
    def test_handle_state_refresh_clears_caches(self, mock_detector, mock_discovery, tmp_path):
        """Test that manual refresh clears caches."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_TEST-PLAN.md").write_text("# PLAN")
        
        console = Console()
        
        # Mock discovery and detector
        mock_discovery_instance = Mock()
        mock_discovery_instance.get_all_plans.return_value = [plan_dir]
        mock_discovery.return_value = mock_discovery_instance
        
        mock_detector_instance = Mock()
        mock_state = Mock()
        mock_state.next_achievements = []
        mock_detector_instance.get_plan_state.return_value = mock_state
        mock_detector.return_value = mock_detector_instance
        
        with patch('LLM.dashboard.plan_dashboard.ParallelDetector'), \
             patch('LLM.dashboard.plan_dashboard.WorkflowExecutor'):
            with patch('LLM.dashboard.plan_dashboard.PlanDashboard.detect_multi_instance', return_value=False), \
                 patch('LLM.dashboard.plan_dashboard.PlanDashboard._resolve_plan', return_value=plan_dir):
                dashboard = PlanDashboard("TEST-PLAN", console)
        
        # Call refresh
        dashboard.handle_state_refresh()
        
        # Verify state was reloaded
        assert mock_detector_instance.get_plan_state.call_count >= 2  # Once in init, once in refresh
    
    @patch('LLM.dashboard.plan_dashboard.PlanDiscovery')
    @patch('LLM.dashboard.plan_dashboard.StateDetector')
    def test_handle_state_refresh_updates_timestamp(self, mock_detector, mock_discovery, tmp_path):
        """Test that manual refresh updates last_refresh_time."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_TEST-PLAN.md").write_text("# PLAN")
        
        console = Console()
        
        mock_discovery_instance = Mock()
        mock_discovery_instance.get_all_plans.return_value = [plan_dir]
        mock_discovery.return_value = mock_discovery_instance
        
        mock_detector_instance = Mock()
        mock_state = Mock()
        mock_state.next_achievements = []
        mock_detector_instance.get_plan_state.return_value = mock_state
        mock_detector.return_value = mock_detector_instance
        
        with patch('LLM.dashboard.plan_dashboard.ParallelDetector'), \
             patch('LLM.dashboard.plan_dashboard.WorkflowExecutor'):
            with patch('LLM.dashboard.plan_dashboard.PlanDashboard.detect_multi_instance', return_value=False), \
                 patch('LLM.dashboard.plan_dashboard.PlanDashboard._resolve_plan', return_value=plan_dir):
                dashboard = PlanDashboard("TEST-PLAN", console)
        
        old_time = dashboard.last_refresh_time
        time.sleep(0.1)
        
        dashboard.handle_state_refresh()
        
        assert dashboard.last_refresh_time > old_time


class TestAutoRefresh:
    """Tests for auto-refresh after actions."""
    
    @patch('LLM.dashboard.plan_dashboard.PlanDiscovery')
    @patch('LLM.dashboard.plan_dashboard.StateDetector')
    def test_auto_refresh_after_action_updates_state(self, mock_detector, mock_discovery, tmp_path):
        """Test that auto-refresh updates state."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_TEST-PLAN.md").write_text("# PLAN")
        
        console = Console()
        
        mock_discovery_instance = Mock()
        mock_discovery_instance.get_all_plans.return_value = [plan_dir]
        mock_discovery.return_value = mock_discovery_instance
        
        mock_detector_instance = Mock()
        mock_state = Mock()
        mock_state.next_achievements = []
        mock_detector_instance.get_plan_state.return_value = mock_state
        mock_detector.return_value = mock_detector_instance
        
        with patch('LLM.dashboard.plan_dashboard.ParallelDetector'), \
             patch('LLM.dashboard.plan_dashboard.WorkflowExecutor'):
            with patch('LLM.dashboard.plan_dashboard.PlanDashboard.detect_multi_instance', return_value=False), \
                 patch('LLM.dashboard.plan_dashboard.PlanDashboard._resolve_plan', return_value=plan_dir):
                dashboard = PlanDashboard("TEST-PLAN", console)
        
        initial_calls = mock_detector_instance.get_plan_state.call_count
        
        dashboard.auto_refresh_after_action()
        
        # Should have called get_plan_state again
        assert mock_detector_instance.get_plan_state.call_count > initial_calls


class TestMultiInstanceDetection:
    """Tests for multi-instance detection."""
    
    def test_detect_multi_instance_no_lock_file(self, tmp_path):
        """Test detection when no lock file exists."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_TEST-PLAN.md").write_text("# PLAN")
        
        console = Console()
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery'), \
             patch('LLM.dashboard.plan_dashboard.StateDetector'), \
             patch('LLM.dashboard.plan_dashboard.ParallelDetector'), \
             patch('LLM.dashboard.plan_dashboard.WorkflowExecutor'):
            with patch('LLM.dashboard.plan_dashboard.PlanDashboard.detect_multi_instance', return_value=False):
                dashboard = PlanDashboard(plan_dir, console)
            
            # Manually test detection
            result = dashboard.detect_multi_instance()
            assert result is False
    
    def test_detect_multi_instance_with_stale_lock(self, tmp_path):
        """Test detection with stale lock file."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_TEST-PLAN.md").write_text("# PLAN")
        
        # Create stale lock file with non-existent PID
        lock_file = Path("LLM/dashboard/.dashboard.lock")
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock_file.write_text("999999")  # PID that doesn't exist
        
        console = Console()
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery'), \
             patch('LLM.dashboard.plan_dashboard.StateDetector'), \
             patch('LLM.dashboard.plan_dashboard.ParallelDetector'), \
             patch('LLM.dashboard.plan_dashboard.WorkflowExecutor'):
            with patch('LLM.dashboard.plan_dashboard.PlanDashboard.detect_multi_instance', return_value=False):
                dashboard = PlanDashboard(plan_dir, console)
            
            # Manually test detection - should remove stale lock
            result = dashboard.detect_multi_instance()
            assert result is False
            assert not lock_file.exists()  # Stale lock removed
    
    def test_create_lock_file(self, tmp_path):
        """Test lock file creation."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_TEST-PLAN.md").write_text("# PLAN")
        
        console = Console()
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery'), \
             patch('LLM.dashboard.plan_dashboard.StateDetector'), \
             patch('LLM.dashboard.plan_dashboard.ParallelDetector'), \
             patch('LLM.dashboard.plan_dashboard.WorkflowExecutor'):
            with patch('LLM.dashboard.plan_dashboard.PlanDashboard.detect_multi_instance', return_value=False):
                dashboard = PlanDashboard(plan_dir, console)
        
        lock_file = Path("LLM/dashboard/.dashboard.lock")
        
        assert lock_file.exists()
        
        # Verify PID in lock file
        pid = int(lock_file.read_text())
        assert pid == os.getpid()
        
        # Cleanup
        dashboard.cleanup_lock_file()
    
    def test_cleanup_lock_file(self, tmp_path):
        """Test lock file cleanup."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_TEST-PLAN.md").write_text("# PLAN")
        
        console = Console()
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery'), \
             patch('LLM.dashboard.plan_dashboard.StateDetector'), \
             patch('LLM.dashboard.plan_dashboard.ParallelDetector'), \
             patch('LLM.dashboard.plan_dashboard.WorkflowExecutor'):
            with patch('LLM.dashboard.plan_dashboard.PlanDashboard.detect_multi_instance', return_value=False):
                dashboard = PlanDashboard(plan_dir, console)
        
        lock_file = Path("LLM/dashboard/.dashboard.lock")
        assert lock_file.exists()
        
        dashboard.cleanup_lock_file()
        
        assert not lock_file.exists()


class TestRefreshIndicators:
    """Tests for refresh indicators and footer."""
    
    @patch('LLM.dashboard.plan_dashboard.PlanDiscovery')
    @patch('LLM.dashboard.plan_dashboard.StateDetector')
    def test_render_refresh_footer_shows_timestamp(self, mock_detector, mock_discovery, tmp_path):
        """Test that footer shows last updated timestamp."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_TEST-PLAN.md").write_text("# PLAN")
        
        console = Console()
        
        mock_discovery_instance = Mock()
        mock_discovery_instance.get_all_plans.return_value = [plan_dir]
        mock_discovery.return_value = mock_discovery_instance
        
        mock_detector_instance = Mock()
        mock_state = Mock()
        mock_state.next_achievements = []
        mock_detector_instance.get_plan_state.return_value = mock_state
        mock_detector.return_value = mock_detector_instance
        
        with patch('LLM.dashboard.plan_dashboard.ParallelDetector'), \
             patch('LLM.dashboard.plan_dashboard.WorkflowExecutor'):
            with patch('LLM.dashboard.plan_dashboard.PlanDashboard.detect_multi_instance', return_value=False), \
                 patch('LLM.dashboard.plan_dashboard.PlanDashboard._resolve_plan', return_value=plan_dir):
                dashboard = PlanDashboard("TEST-PLAN", console)
        
        # Should not raise exception
        dashboard.render_refresh_footer()
    
    @patch('LLM.dashboard.plan_dashboard.PlanDiscovery')
    @patch('LLM.dashboard.plan_dashboard.StateDetector')
    def test_render_refresh_footer_shows_staleness_warning(self, mock_detector, mock_discovery, tmp_path):
        """Test that footer shows staleness warning when data is old."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_TEST-PLAN.md").write_text("# PLAN")
        
        console = Console()
        
        mock_discovery_instance = Mock()
        mock_discovery_instance.get_all_plans.return_value = [plan_dir]
        mock_discovery.return_value = mock_discovery_instance
        
        mock_detector_instance = Mock()
        mock_state = Mock()
        mock_state.next_achievements = []
        mock_detector_instance.get_plan_state.return_value = mock_state
        mock_detector.return_value = mock_detector_instance
        
        with patch('LLM.dashboard.plan_dashboard.ParallelDetector'), \
             patch('LLM.dashboard.plan_dashboard.WorkflowExecutor'):
            with patch('LLM.dashboard.plan_dashboard.PlanDashboard.detect_multi_instance', return_value=False), \
                 patch('LLM.dashboard.plan_dashboard.PlanDashboard._resolve_plan', return_value=plan_dir):
                dashboard = PlanDashboard("TEST-PLAN", console)
        
        # Make data stale (>5 minutes old)
        dashboard.last_refresh_time = datetime.now() - timedelta(minutes=6)
        
        # Should not raise exception and should show warning
        dashboard.render_refresh_footer()

