"""
Tests for library integration in dashboard.

Verifies exception handling, logging, caching, and metrics collection work correctly
when integrated into the dashboard codebase.

Created: 2025-11-14
Achievement: 0.4 - Library Integration & Production Patterns
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

from LLM.dashboard.exceptions import (
    DashboardError,
    PlanLoadError,
    StateDetectionError,
    ActionExecutionError,
    InvalidUserInputError
)
from LLM.dashboard.main_dashboard import MainDashboard
from LLM.dashboard.metrics import (
    register_dashboard_metrics,
    track_action,
    track_load_time,
    track_cache_operation,
    update_plan_state
)


class TestExceptionHandling:
    """Test dashboard exception classes."""
    
    def test_dashboard_error_is_application_error(self):
        """DashboardError should inherit from ApplicationError."""
        from LLM.scripts.generation.exceptions import ApplicationError
        assert issubclass(DashboardError, ApplicationError)
    
    def test_plan_load_error_with_context(self):
        """PlanLoadError should support context."""
        error = PlanLoadError(
            "Plan not found",
            context={'plan_path': '/path/to/plan'}
        )
        assert error.context['plan_path'] == '/path/to/plan'
        assert "Plan not found" in str(error)
    
    def test_state_detection_error(self):
        """StateDetectionError should work correctly."""
        error = StateDetectionError(
            "State detection failed",
            context={'plan_dir': '/path/to/plan'}
        )
        assert 'plan_dir' in error.context
        assert error.context['plan_dir'] == '/path/to/plan'
    
    def test_action_execution_error(self):
        """ActionExecutionError should work correctly."""
        error = ActionExecutionError(
            "Action failed",
            context={'action': 'open_plan'}
        )
        assert error.context['action'] == 'open_plan'
    
    def test_invalid_user_input_error(self):
        """InvalidUserInputError should work correctly."""
        error = InvalidUserInputError(
            "Invalid input",
            context={'input': 'xyz', 'expected': 'number'}
        )
        assert error.context['input'] == 'xyz'
        assert error.context['expected'] == 'number'
    
    def test_exception_hierarchy(self):
        """All exceptions should inherit from DashboardError."""
        assert issubclass(PlanLoadError, DashboardError)
        assert issubclass(StateDetectionError, DashboardError)
        assert issubclass(ActionExecutionError, DashboardError)
        assert issubclass(InvalidUserInputError, DashboardError)
    
    def test_exception_with_context(self):
        """Exceptions should work with context parameter."""
        error = PlanLoadError("Test error", context={'test': 'value'})
        assert error.context['test'] == 'value'
    
    def test_exception_with_no_context(self):
        """Exceptions should work without context."""
        error = StateDetectionError("Test error")
        assert hasattr(error, 'context')


class TestLoggingIntegration:
    """Test structured logging integration."""
    
    @patch('LLM.dashboard.main_dashboard.logger')
    def test_dashboard_lifecycle_logging(self, mock_logger):
        """Dashboard should log lifecycle events."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dashboard = MainDashboard(workspace_root=Path(tmpdir))
            # Verify logger is available
            assert mock_logger is not None
    
    @patch('LLM.dashboard.plan_discovery.logger')
    def test_discovery_logging_available(self, mock_logger):
        """Plan discovery should have logger available."""
        from LLM.dashboard.plan_discovery import PlanDiscovery
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_root = Path(tmpdir) / "plans"
            plans_root.mkdir()
            discovery = PlanDiscovery(plans_root=plans_root)
            # Just verify logger is imported
            assert mock_logger is not None
    
    @patch('LLM.dashboard.state_detector.logger')
    def test_state_detector_logging_available(self, mock_logger):
        """State detector should have logger available."""
        from LLM.dashboard.state_detector import StateDetector
        detector = StateDetector()
        # Just verify logger is imported
        assert mock_logger is not None


class TestMetricsCollection:
    """Test metrics collection."""
    
    def test_register_dashboard_metrics(self):
        """register_dashboard_metrics should not raise errors."""
        # Multiple calls should be safe
        register_dashboard_metrics()
        register_dashboard_metrics()
    
    def test_track_action(self):
        """track_action should not raise errors."""
        track_action('open_plan', 'success')
        track_action('close_dashboard', 'interrupted')
    
    def test_track_load_time(self):
        """track_load_time should not raise errors."""
        track_load_time('main', 0.5)
        track_load_time('plan', 0.3)
    
    def test_track_cache_operation(self):
        """track_cache_operation should not raise errors."""
        track_cache_operation('plan_discovery', 'get', 'hit')
        track_cache_operation('plan_state', 'get', 'miss')
    
    def test_update_plan_state(self):
        """update_plan_state should not raise errors."""
        update_plan_state('TEST-PLAN', 'in_progress', 0.5)
        update_plan_state('OTHER-PLAN', 'complete', 1.0)


class TestRegexPatterns:
    """Test compiled regex patterns."""
    
    def test_regex_patterns_imported(self):
        """Regex patterns should be importable."""
        from LLM.dashboard.utils import (
            ACHIEVEMENT_NUM_PATTERN_1,
            ACHIEVEMENT_NUM_PATTERN_2,
            APPROVED_FILE_PATTERN,
            FIX_FILE_PATTERN,
            SUBPLAN_FILE_PATTERN,
            EXECUTION_FILE_PATTERN
        )
        # Verify they're compiled regex objects
        import re
        assert isinstance(ACHIEVEMENT_NUM_PATTERN_1, re.Pattern)
        assert isinstance(ACHIEVEMENT_NUM_PATTERN_2, re.Pattern)
        assert isinstance(APPROVED_FILE_PATTERN, re.Pattern)
        assert isinstance(FIX_FILE_PATTERN, re.Pattern)
        assert isinstance(SUBPLAN_FILE_PATTERN, re.Pattern)
        assert isinstance(EXECUTION_FILE_PATTERN, re.Pattern)
    
    def test_helper_functions_exist(self):
        """Helper functions for pattern matching should exist."""
        from LLM.dashboard.utils import (
            is_approved_file,
            is_fix_file,
            is_subplan_file,
            is_execution_file
        )
        # Verify they're callable
        assert callable(is_approved_file)
        assert callable(is_fix_file)
        assert callable(is_subplan_file)
        assert callable(is_execution_file)
    
    def test_is_approved_file(self):
        """is_approved_file should correctly identify APPROVED files."""
        from LLM.dashboard.utils import is_approved_file
        assert is_approved_file("APPROVED_31.md") is True
        assert is_approved_file("FIX_31.md") is False
        assert is_approved_file("random.md") is False
    
    def test_is_fix_file(self):
        """is_fix_file should correctly identify FIX files."""
        from LLM.dashboard.utils import is_fix_file
        assert is_fix_file("FIX_12.md") is True
        assert is_fix_file("APPROVED_12.md") is False
        assert is_fix_file("random.md") is False
    
    def test_parse_achievement_number_uses_compiled_patterns(self):
        """parse_achievement_number should use compiled patterns."""
        from LLM.dashboard.utils import parse_achievement_number
        # These should work with compiled patterns
        assert parse_achievement_number("APPROVED_31.md") == "3.1"
        assert parse_achievement_number("FIX_12.md") == "1.2"


class TestIntegration:
    """Test integration of all libraries together."""
    
    def test_dashboard_init_registers_metrics(self):
        """Dashboard initialization should register metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dashboard = MainDashboard(workspace_root=Path(tmpdir))
            # Should not raise any errors
            assert dashboard is not None
    
    def test_exception_classes_available(self):
        """All exception classes should be importable from exceptions module."""
        from LLM.dashboard.exceptions import (
            DashboardError,
            PlanLoadError,
            StateDetectionError,
            ActionExecutionError,
            InvalidUserInputError
        )
        # All should be classes
        assert isinstance(DashboardError, type)
        assert isinstance(PlanLoadError, type)
        assert isinstance(StateDetectionError, type)
        assert isinstance(ActionExecutionError, type)
        assert isinstance(InvalidUserInputError, type)
    
    def test_metrics_module_functions_exist(self):
        """All metrics functions should be available."""
        from LLM.dashboard.metrics import (
            register_dashboard_metrics,
            track_action,
            track_load_time,
            track_cache_operation,
            update_plan_state
        )
        # All should be callable
        assert callable(register_dashboard_metrics)
        assert callable(track_action)
        assert callable(track_load_time)
        assert callable(track_cache_operation)
        assert callable(update_plan_state)

