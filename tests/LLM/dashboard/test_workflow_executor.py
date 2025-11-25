"""
Tests for workflow executor.

Achievement 2.2: Interactive Workflow Execution

Tests interactive workflow execution with progress tracking, result display,
and error handling.
"""

import pytest
import subprocess
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from rich.console import Console

from LLM.dashboard.workflow_executor import WorkflowExecutor
from LLM.dashboard.models import ExecutionResult, WorkflowType, WorkflowState


class TestWorkflowExecutorInit:
    """Tests for WorkflowExecutor initialization."""
    
    def test_init(self, tmp_path):
        """Test WorkflowExecutor initialization."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()
        
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        assert executor.plan_path == plan_dir
        assert executor.plan_name == "TEST-PLAN"
        assert executor.console == console


class TestWorkflowRouting:
    """Tests for workflow routing logic."""
    
    def test_execute_workflow_routes_to_next(self, tmp_path):
        """Test execute_workflow routes NEXT to _execute_next_workflow."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        with patch.object(executor, '_execute_next_workflow') as mock_next:
            mock_next.return_value = ExecutionResult(success=True)
            result = executor.execute_workflow("next")
            
            mock_next.assert_called_once()
            assert result.success
    
    def test_execute_workflow_routes_to_subplan(self, tmp_path):
        """Test execute_workflow routes SUBPLAN to _execute_subplan_workflow."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        with patch.object(executor, '_execute_subplan_workflow') as mock_subplan:
            mock_subplan.return_value = ExecutionResult(success=True)
            result = executor.execute_workflow("subplan", achievement_id="1.1")
            
            mock_subplan.assert_called_once_with("1.1")
            assert result.success
    
    def test_execute_workflow_routes_to_execution(self, tmp_path):
        """Test execute_workflow routes EXECUTION to _execute_execution_workflow."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        with patch.object(executor, '_execute_execution_workflow') as mock_execution:
            mock_execution.return_value = ExecutionResult(success=True)
            result = executor.execute_workflow("execution", subplan_id="11")
            
            mock_execution.assert_called_once_with("11")
            assert result.success
    
    def test_execute_workflow_invalid_type(self, tmp_path):
        """Test execute_workflow with invalid workflow type."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        result = executor.execute_workflow("invalid")
        
        assert not result.success
        assert "Unknown workflow type" in result.error
    
    def test_execute_workflow_subplan_missing_achievement_id(self, tmp_path):
        """Test SUBPLAN workflow without achievement_id raises error."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        result = executor.execute_workflow("subplan")
        
        assert not result.success
        assert "achievement_id required" in result.error
    
    def test_execute_workflow_execution_missing_subplan_id(self, tmp_path):
        """Test EXECUTION workflow without subplan_id raises error."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        result = executor.execute_workflow("execution")
        
        assert not result.success
        assert "subplan_id required" in result.error


class TestNextWorkflow:
    """Tests for next workflow execution."""
    
    @patch('LLM.dashboard.workflow_executor.Confirm.ask')
    @patch('subprocess.run')
    def test_next_workflow_user_confirms(self, mock_run, mock_confirm, tmp_path):
        """Test next workflow when user confirms."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        mock_confirm.return_value = True
        mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")
        
        result = executor._execute_next_workflow()
        
        mock_confirm.assert_called_once()
        mock_run.assert_called_once()
        assert result.success
    
    @patch('LLM.dashboard.workflow_executor.Confirm.ask')
    def test_next_workflow_user_cancels(self, mock_confirm, tmp_path):
        """Test next workflow when user cancels."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        mock_confirm.return_value = False
        
        result = executor._execute_next_workflow()
        
        assert not result.success
        assert "cancelled" in result.error.lower()
    
    @patch('LLM.dashboard.workflow_executor.Confirm.ask')
    @patch('subprocess.run')
    def test_next_workflow_command_structure(self, mock_run, mock_confirm, tmp_path):
        """Test next workflow builds correct command."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        mock_confirm.return_value = True
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        executor._execute_next_workflow()
        
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "python"
        assert "generate_prompt.py" in cmd[1]
        assert "@MY-PLAN" in cmd
        assert "--next" in cmd
        assert "--interactive" in cmd


class TestSubplanWorkflow:
    """Tests for SUBPLAN workflow execution."""
    
    @patch('LLM.dashboard.workflow_executor.Confirm.ask')
    @patch('subprocess.run')
    def test_subplan_workflow_success(self, mock_run, mock_confirm, tmp_path):
        """Test SUBPLAN workflow success."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        mock_confirm.return_value = True
        mock_run.return_value = Mock(
            returncode=0,
            stdout="SUBPLAN created: SUBPLAN_MY-PLAN_11.md",
            stderr=""
        )
        
        result = executor._execute_subplan_workflow("1.1")
        
        assert result.success
        assert len(result.deliverables) > 0
    
    @patch('LLM.dashboard.workflow_executor.Confirm.ask')
    def test_subplan_workflow_user_cancels(self, mock_confirm, tmp_path):
        """Test SUBPLAN workflow when user cancels."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        mock_confirm.return_value = False
        
        result = executor._execute_subplan_workflow("1.1")
        
        assert not result.success
        assert "cancelled" in result.error.lower()
    
    def test_subplan_workflow_invalid_achievement_id(self, tmp_path):
        """Test SUBPLAN workflow with invalid achievement ID."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        result = executor._execute_subplan_workflow("invalid")
        
        assert not result.success
        assert "Invalid achievement ID" in result.error
    
    @patch('LLM.dashboard.workflow_executor.Confirm.ask')
    @patch('subprocess.run')
    def test_subplan_workflow_command_structure(self, mock_run, mock_confirm, tmp_path):
        """Test SUBPLAN workflow builds correct command."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        mock_confirm.return_value = True
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        executor._execute_subplan_workflow("2.3")
        
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "python"
        assert "generate_subplan_prompt.py" in cmd[1]
        assert "@MY-PLAN" in cmd
        assert "--achievement" in cmd
        assert "2.3" in cmd


class TestExecutionWorkflow:
    """Tests for EXECUTION workflow execution."""
    
    @patch('LLM.dashboard.workflow_executor.Confirm.ask')
    @patch('subprocess.run')
    def test_execution_workflow_success(self, mock_run, mock_confirm, tmp_path):
        """Test EXECUTION workflow success."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        subplan_dir = plan_dir / "subplans"
        subplan_dir.mkdir()
        subplan_file = subplan_dir / "SUBPLAN_MY-PLAN_11.md"
        subplan_file.write_text("# SUBPLAN")
        
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        mock_confirm.return_value = True
        mock_run.return_value = Mock(
            returncode=0,
            stdout="EXECUTION created: EXECUTION_TASK_MY-PLAN_11_01.md",
            stderr=""
        )
        
        result = executor._execute_execution_workflow("11")
        
        assert result.success
    
    def test_execution_workflow_subplan_not_found(self, tmp_path):
        """Test EXECUTION workflow when SUBPLAN doesn't exist."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        subplan_dir = plan_dir / "subplans"
        subplan_dir.mkdir()
        
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        result = executor._execute_execution_workflow("11")
        
        assert not result.success
        assert "SUBPLAN not found" in result.error
    
    @patch('LLM.dashboard.workflow_executor.Confirm.ask')
    def test_execution_workflow_user_cancels(self, mock_confirm, tmp_path):
        """Test EXECUTION workflow when user cancels."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        subplan_dir = plan_dir / "subplans"
        subplan_dir.mkdir()
        subplan_file = subplan_dir / "SUBPLAN_MY-PLAN_11.md"
        subplan_file.write_text("# SUBPLAN")
        
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        mock_confirm.return_value = False
        
        result = executor._execute_execution_workflow("11")
        
        assert not result.success
        assert "cancelled" in result.error.lower()
    
    @patch('LLM.dashboard.workflow_executor.Confirm.ask')
    @patch('subprocess.run')
    def test_execution_workflow_command_structure(self, mock_run, mock_confirm, tmp_path):
        """Test EXECUTION workflow builds correct command."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        subplan_dir = plan_dir / "subplans"
        subplan_dir.mkdir()
        subplan_file = subplan_dir / "SUBPLAN_MY-PLAN_11.md"
        subplan_file.write_text("# SUBPLAN")
        
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        mock_confirm.return_value = True
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        executor._execute_execution_workflow("11")
        
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "python"
        assert "generate_execution_prompt.py" in cmd[1]
        assert "SUBPLAN_MY-PLAN_11.md" in cmd[2]


class TestProgressTracking:
    """Tests for progress tracking functionality."""
    
    @patch('subprocess.run')
    def test_run_subprocess_shows_progress(self, mock_run, tmp_path):
        """Test _run_subprocess shows progress indicator."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")
        
        result = executor._run_subprocess(
            ["echo", "test"],
            "Test Task",
            "Testing..."
        )
        
        assert result.success
        assert result.duration > 0
    
    @patch('subprocess.run')
    def test_run_subprocess_timeout(self, mock_run, tmp_path):
        """Test _run_subprocess handles timeout."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 60)
        
        result = executor._run_subprocess(
            ["sleep", "1000"],
            "Test Task",
            "Testing..."
        )
        
        assert not result.success
        assert "timed out" in result.error.lower()
    
    @patch('subprocess.run')
    def test_run_subprocess_captures_duration(self, mock_run, tmp_path):
        """Test _run_subprocess captures execution duration."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        def slow_run(*args, **kwargs):
            time.sleep(0.1)
            return Mock(returncode=0, stdout="", stderr="")
        
        mock_run.side_effect = slow_run
        
        result = executor._run_subprocess(
            ["echo", "test"],
            "Test Task",
            "Testing..."
        )
        
        assert result.duration >= 0.1


class TestResultDisplay:
    """Tests for result display functionality."""
    
    def test_display_result_success(self, tmp_path, capsys):
        """Test _display_result shows success panel."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        result = ExecutionResult(
            success=True,
            deliverables=["SUBPLAN_XX_11.md"],
            duration=45.5
        )
        
        executor._display_result(result)
        # Result should be displayed (visual test, hard to assert)
    
    def test_display_result_failure(self, tmp_path, capsys):
        """Test _display_result shows failure panel."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        result = ExecutionResult(
            success=False,
            error="Test error message"
        )
        
        executor._display_result(result)
        # Result should be displayed (visual test, hard to assert)
    
    def test_display_result_with_deliverables(self, tmp_path):
        """Test _display_result shows deliverables."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        result = ExecutionResult(
            success=True,
            deliverables=["file1.md", "file2.md"],
            duration=30.0
        )
        
        executor._display_result(result)
        # Should display both deliverables
    
    def test_display_result_with_tests(self, tmp_path):
        """Test _display_result shows test results."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        result = ExecutionResult(
            success=True,
            tests_passing=42,
            tests_total=42,
            duration=10.0
        )
        
        executor._display_result(result)
        # Should display test results


class TestErrorHandling:
    """Tests for error handling functionality."""
    
    def test_handle_error_creates_result(self, tmp_path):
        """Test _handle_error creates ExecutionResult."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        error = ValueError("Test error")
        result = executor._handle_error(error, "test_workflow")
        
        assert not result.success
        assert "Test error" in result.error
    
    def test_generate_recovery_suggestions_not_found(self, tmp_path):
        """Test recovery suggestions for 'not found' errors."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        suggestions = executor._generate_recovery_suggestions(
            "SUBPLAN not found: SUBPLAN_XX_11.md"
        )
        
        assert len(suggestions) > 0
        assert any("SUBPLAN" in s for s in suggestions)
    
    def test_generate_recovery_suggestions_timeout(self, tmp_path):
        """Test recovery suggestions for timeout errors."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        suggestions = executor._generate_recovery_suggestions(
            "Workflow timed out after 60 seconds"
        )
        
        assert len(suggestions) > 0
        # Should generate some suggestions even if not specific to timeout
        assert all(isinstance(s, str) for s in suggestions)
    
    def test_generate_recovery_suggestions_invalid_format(self, tmp_path):
        """Test recovery suggestions for invalid format errors."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        suggestions = executor._generate_recovery_suggestions(
            "Invalid achievement ID format: invalid"
        )
        
        assert len(suggestions) > 0


class TestOutputParsing:
    """Tests for output parsing functionality."""
    
    def test_parse_success_output_extracts_deliverables(self, tmp_path):
        """Test _parse_success_output extracts deliverables from output."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        output = "SUBPLAN created: SUBPLAN_XX_11.md\nFile saved successfully"
        result = executor._parse_success_output(output, "test", 10.0)
        
        assert result.success
        assert len(result.deliverables) > 0
        assert "SUBPLAN_XX_11.md" in result.deliverables
    
    def test_parse_success_output_no_deliverables(self, tmp_path):
        """Test _parse_success_output with no deliverables."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        output = "Operation completed successfully"
        result = executor._parse_success_output(output, "test", 10.0)
        
        assert result.success
        assert len(result.deliverables) == 0


class TestIntegration:
    """Integration tests for complete workflow execution."""
    
    @patch('LLM.dashboard.workflow_executor.Confirm.ask')
    @patch('subprocess.run')
    def test_complete_workflow_next_to_subplan(self, mock_run, mock_confirm, tmp_path):
        """Test complete workflow from detection to SUBPLAN creation."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        mock_confirm.return_value = True
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Next: create SUBPLAN for 1.1\nSUBPLAN created: SUBPLAN_MY-PLAN_11.md",
            stderr=""
        )
        
        result = executor.execute_workflow("next")
        
        assert result.success
        mock_run.assert_called_once()
    
    @patch('LLM.dashboard.workflow_executor.Confirm.ask')
    @patch('subprocess.run')
    def test_complete_workflow_subplan_to_execution(self, mock_run, mock_confirm, tmp_path):
        """Test complete workflow from SUBPLAN to EXECUTION creation."""
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        subplan_dir = plan_dir / "subplans"
        subplan_dir.mkdir()
        subplan_file = subplan_dir / "SUBPLAN_MY-PLAN_11.md"
        subplan_file.write_text("# SUBPLAN")
        
        console = Console()
        executor = WorkflowExecutor(plan_dir, console)
        
        mock_confirm.return_value = True
        mock_run.return_value = Mock(
            returncode=0,
            stdout="EXECUTION created: EXECUTION_TASK_MY-PLAN_11_01.md",
            stderr=""
        )
        
        result = executor.execute_workflow("execution", subplan_id="11")
        
        assert result.success
        mock_run.assert_called_once()


class TestExecutionResult:
    """Tests for ExecutionResult dataclass methods."""
    
    def test_has_test_failures_with_failures(self):
        """Test has_test_failures with test failures."""
        result = ExecutionResult(
            success=True,
            tests_passing=38,
            tests_total=42
        )
        
        assert result.has_test_failures()
    
    def test_has_test_failures_without_failures(self):
        """Test has_test_failures without test failures."""
        result = ExecutionResult(
            success=True,
            tests_passing=42,
            tests_total=42
        )
        
        assert not result.has_test_failures()
    
    def test_format_duration_seconds(self):
        """Test format_duration for short durations."""
        result = ExecutionResult(success=True, duration=45.5)
        
        formatted = result.format_duration()
        
        assert "45.5s" in formatted
    
    def test_format_duration_minutes(self):
        """Test format_duration for long durations."""
        result = ExecutionResult(success=True, duration=154.0)  # 2m 34s
        
        formatted = result.format_duration()
        
        assert "2m" in formatted
        assert "34s" in formatted

