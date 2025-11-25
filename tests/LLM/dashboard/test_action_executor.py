"""
Tests for action executor and action features.

Tests action execution, command building, action menu, and documentation access.
"""

import pytest
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from rich.console import Console

from LLM.dashboard.action_executor import ActionExecutor
from LLM.dashboard.plan_dashboard import PlanDashboard, Action
from LLM.dashboard.models import PlanState, AchievementState, PlanStatus, AchievementStatus


class TestActionExecutor:
    """Tests for ActionExecutor class."""
    
    def test_init(self, tmp_path):
        """Test ActionExecutor initialization."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()
        
        console = Console()
        executor = ActionExecutor(plan_dir, console)
        
        assert executor.plan_path == plan_dir
        assert executor.plan_name == "TEST-PLAN"
        assert executor.console == console
    
    @patch('subprocess.run')
    def test_execute_next_command_building(self, mock_run, tmp_path):
        """Test execute_next builds correct command."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        
        console = Console()
        executor = ActionExecutor(plan_dir, console)
        
        # Mock successful execution
        mock_run.return_value = Mock(returncode=0)
        
        with patch('builtins.input'):  # Mock the pause
            executor.execute_next()
        
        # Verify command
        expected_cmd = [
            "python",
            "LLM/scripts/generation/generate_prompt.py",
            "@MY-PLAN",
            "--next",
            "--interactive"
        ]
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == expected_cmd
    
    @patch('subprocess.run')
    def test_create_subplan_command_building(self, mock_run, tmp_path):
        """Test create_subplan builds correct command."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        
        console = Console()
        executor = ActionExecutor(plan_dir, console)
        
        mock_run.return_value = Mock(returncode=0)
        
        with patch('builtins.input'):
            executor.create_subplan("1.2")
        
        expected_cmd = [
            "python",
            "LLM/scripts/generation/generate_subplan_prompt.py",
            "@MY-PLAN",
            "--achievement", "1.2"
        ]
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == expected_cmd
    
    @patch('subprocess.run')
    def test_create_execution_command_building(self, mock_run, tmp_path):
        """Test create_execution builds correct command."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        
        console = Console()
        executor = ActionExecutor(plan_dir, console)
        
        mock_run.return_value = Mock(returncode=0)
        
        with patch('builtins.input'):
            executor.create_execution("2.3")
        
        expected_cmd = [
            "python",
            "LLM/scripts/generation/generate_execution_prompt.py",
            "@MY-PLAN",
            "--achievement", "2.3"
        ]
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == expected_cmd
    
    @patch('subprocess.run')
    def test_run_command_failure_handling(self, mock_run, tmp_path):
        """Test command failure handling."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        
        console = Console()
        executor = ActionExecutor(plan_dir, console)
        
        # Mock failed execution
        mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd')
        
        with patch('builtins.input'):
            # Should not raise, should handle gracefully
            executor.execute_next()
        
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_run_command_not_found(self, mock_run, tmp_path):
        """Test command not found handling."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        
        console = Console()
        executor = ActionExecutor(plan_dir, console)
        
        # Mock command not found
        mock_run.side_effect = FileNotFoundError()
        
        with patch('builtins.input'):
            # Should not raise, should handle gracefully
            executor.execute_next()
        
        mock_run.assert_called_once()


class TestActionMenu:
    """Tests for action menu rendering."""
    
    def test_get_available_actions_with_next(self, tmp_path):
        """Test available actions when next achievement exists."""
        plan_dir = tmp_path / "work-space" / "plans" / "TEST"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_TEST.md").write_text("# Test")
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_ach = AchievementState(
            achievement_id="1.2",
            title="Test",
            status=AchievementStatus.NOT_STARTED,
            has_subplan=False,
            has_execution=False,
            has_approved=False,
            has_fix=False
        )
        
        mock_state = PlanState(
            name="TEST",
            plan_file=plan_dir / "PLAN_TEST.md",
            last_achievement="1.1",
            next_achievements=[mock_ach],
            pending_reviews=[],
            pending_fixes=[],
            total_achievements=10,
            completed_achievements=1,
            progress_percentage=10.0,
            status=PlanStatus.ACTIVE
        )
        mock_state_detector = Mock()
        mock_state_detector.get_plan_state.return_value = mock_state
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery', return_value=mock_discovery), \
             patch('LLM.dashboard.plan_dashboard.StateDetector', return_value=mock_state_detector):
            
            console = Console()
            dashboard = PlanDashboard(plan_id=1, console=console)
            
            actions = dashboard._get_available_actions()
            
            assert len(actions) == 6  # Now 6 actions (added parallel)
            assert actions[0].key == '1'
            assert actions[0].enabled == True  # Execute Next enabled
    
    def test_get_available_actions_without_next(self, tmp_path):
        """Test available actions when no next achievement."""
        plan_dir = tmp_path / "work-space" / "plans" / "TEST"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_TEST.md").write_text("# Test")
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_state = PlanState(
            name="TEST",
            plan_file=plan_dir / "PLAN_TEST.md",
            last_achievement="3.3",
            next_achievements=[],  # No next
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
            
            actions = dashboard._get_available_actions()
            
            assert len(actions) == 6  # Now 6 actions (added parallel)
            assert actions[0].key == '1'
            assert actions[0].enabled == False  # Execute Next disabled
    
    def test_render_actions(self, tmp_path):
        """Test action menu rendering."""
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
            
            # Should not raise
            dashboard.render_actions()


class TestActionHandler:
    """Tests for action handling."""
    
    @pytest.fixture
    def dashboard_mock(self, tmp_path):
        """Create dashboard with mocked state."""
        plan_dir = tmp_path / "work-space" / "plans" / "TEST"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_TEST.md").write_text("# Test")
        
        mock_discovery = Mock()
        mock_discovery.get_all_plans.return_value = [plan_dir]
        
        mock_ach = AchievementState(
            achievement_id="1.2",
            title="Test",
            status=AchievementStatus.NOT_STARTED,
            has_subplan=False,
            has_execution=False,
            has_approved=False,
            has_fix=False
        )
        
        mock_state = PlanState(
            name="TEST",
            plan_file=plan_dir / "PLAN_TEST.md",
            last_achievement="1.1",
            next_achievements=[mock_ach],
            pending_reviews=[],
            pending_fixes=[],
            total_achievements=10,
            completed_achievements=1,
            progress_percentage=10.0,
            status=PlanStatus.ACTIVE
        )
        mock_state_detector = Mock()
        mock_state_detector.get_plan_state.return_value = mock_state
        
        with patch('LLM.dashboard.plan_dashboard.PlanDiscovery', return_value=mock_discovery), \
             patch('LLM.dashboard.plan_dashboard.StateDetector', return_value=mock_state_detector):
            
            console = Console()
            dashboard = PlanDashboard(plan_id=1, console=console)
            return dashboard
    
    def test_handle_action_execute_next(self, dashboard_mock):
        """Test execute next action handling."""
        with patch.object(dashboard_mock, '_action_execute_next') as mock_action:
            dashboard_mock.handle_action('1')
            mock_action.assert_called_once()
    
    def test_handle_action_create_subplan(self, dashboard_mock):
        """Test create SUBPLAN action handling."""
        with patch.object(dashboard_mock, '_action_create_subplan') as mock_action:
            dashboard_mock.handle_action('3')  # Changed from '2' to '3'
            mock_action.assert_called_once()
    
    def test_handle_action_create_execution(self, dashboard_mock):
        """Test create EXECUTION action handling."""
        with patch.object(dashboard_mock, '_action_create_execution') as mock_action:
            dashboard_mock.handle_action('4')  # Changed from '3' to '4'
            mock_action.assert_called_once()
    
    def test_handle_action_view_docs(self, dashboard_mock):
        """Test view documentation action handling."""
        with patch.object(dashboard_mock, '_action_view_documentation') as mock_action:
            dashboard_mock.handle_action('5')  # Changed from '4' to '5'
            mock_action.assert_called_once()
    
    def test_handle_action_invalid(self, dashboard_mock):
        """Test invalid action handling."""
        with patch.object(dashboard_mock, 'get_user_input', return_value=''):
            # Should not raise
            dashboard_mock.handle_action('99')


class TestDocumentationMenu:
    """Tests for documentation menu."""
    
    def test_show_documentation_menu_display(self, tmp_path):
        """Test documentation menu displays."""
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
             patch('LLM.dashboard.plan_dashboard.StateDetector', return_value=mock_state_detector), \
             patch('rich.prompt.Prompt.ask', return_value='b'):
            
            console = Console()
            dashboard = PlanDashboard(plan_id=1, console=console)
            
            # Should not raise
            dashboard._show_documentation_menu()
    
    def test_open_document_not_found(self, tmp_path):
        """Test opening non-existent document."""
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
            
            with patch.object(dashboard, 'get_user_input', return_value=''):
                # Should not raise
                dashboard._open_document("/nonexistent/file.md")
    
    def test_open_document_exists(self, tmp_path):
        """Test opening existing document."""
        plan_dir = tmp_path / "work-space" / "plans" / "TEST"
        plan_dir.mkdir(parents=True)
        (plan_dir / "PLAN_TEST.md").write_text("# Test")
        
        # Create test document
        doc_file = tmp_path / "test_doc.md"
        doc_file.write_text("# Test Documentation\n\nContent here")
        
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
            
            with patch('subprocess.run', side_effect=FileNotFoundError()), \
                 patch.object(dashboard, 'get_user_input', return_value=''):
                # Should fall back to print preview
                dashboard._open_document(str(doc_file))


class TestActionDataclass:
    """Tests for Action dataclass."""
    
    def test_action_creation(self):
        """Test Action dataclass creation."""
        action = Action('1', '▶️', 'Execute Next')
        
        assert action.key == '1'
        assert action.emoji == '▶️'
        assert action.label == 'Execute Next'
        assert action.enabled == True
    
    def test_action_disabled(self):
        """Test Action with disabled state."""
        action = Action('1', '▶️', 'Execute Next', enabled=False)
        
        assert action.enabled == False

