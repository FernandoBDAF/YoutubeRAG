"""
tests/LLM/dashboard/test_main_dashboard.py - Unit Tests for Main Dashboard

Achievement: 0.3 - Main Dashboard Implementation
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from rich.console import Console
from rich.table import Table

from LLM.dashboard.main_dashboard import (
    MainDashboard,
    create_plan_table,
    format_next_achievements,
    get_status_emoji,
)
from LLM.dashboard.models import PlanState


class TestMainDashboard:
    """Tests for MainDashboard class."""

    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        dashboard = MainDashboard()

        assert dashboard.console is not None
        assert isinstance(dashboard.console, Console)
        assert dashboard.workspace_root == Path.cwd()
        assert dashboard.discovery is not None
        assert dashboard.state_detector is not None

    def test_init_with_custom_console(self):
        """Test initialization with custom console."""
        mock_console = Mock(spec=Console)
        dashboard = MainDashboard(console=mock_console)

        assert dashboard.console == mock_console
        assert dashboard.workspace_root == Path.cwd()

    def test_init_with_custom_workspace(self):
        """Test initialization with custom workspace root."""
        custom_root = Path("/custom/workspace")
        dashboard = MainDashboard(workspace_root=custom_root)

        assert dashboard.workspace_root == custom_root
        assert dashboard.discovery.plans_root == custom_root / "work-space" / "plans"
        assert dashboard.state_detector is not None

    @patch.object(MainDashboard, "get_user_input")
    @patch.object(MainDashboard, "render_header")
    @patch.object(MainDashboard, "render_plans")
    @patch.object(MainDashboard, "render_prompt")
    @patch.object(MainDashboard, "clear")
    def test_show_loop_quit(
        self, mock_clear, mock_render_prompt, mock_render_plans, mock_render_header, mock_get_input
    ):
        """Test show() loop quits on 'q'."""
        mock_console = Mock(spec=Console)
        mock_get_input.return_value = "q"

        dashboard = MainDashboard(console=mock_console)
        dashboard.show()

        # Verify loop ran once and quit
        mock_clear.assert_called_once()
        mock_render_header.assert_called_once()
        mock_render_plans.assert_called_once()
        mock_render_prompt.assert_called_once()
        mock_get_input.assert_called_once()
        mock_console.print.assert_called_once_with("[yellow]Goodbye![/yellow]")

    @patch.object(MainDashboard, "open_plan_dashboard")
    @patch.object(MainDashboard, "get_user_input")
    @patch.object(MainDashboard, "render_header")
    @patch.object(MainDashboard, "render_plans")
    @patch.object(MainDashboard, "render_prompt")
    @patch.object(MainDashboard, "clear")
    def test_show_loop_select_plan(
        self,
        mock_clear,
        mock_render_prompt,
        mock_render_plans,
        mock_render_header,
        mock_get_input,
        mock_open_plan,
    ):
        """Test show() loop handles plan selection."""
        mock_console = Mock(spec=Console)
        # First input selects plan 1, second input quits
        mock_get_input.side_effect = ["1", "q"]

        dashboard = MainDashboard(console=mock_console)
        dashboard.show()

        # Verify plan was opened with correct index (0-based)
        mock_open_plan.assert_called_once_with(0)
        # Verify loop ran twice (select plan, then quit)
        assert mock_clear.call_count == 2
        assert mock_render_header.call_count == 2

    @patch.object(Console, "print")
    def test_render_header(self, mock_print):
        """Test render_header() displays header panel."""
        dashboard = MainDashboard()
        dashboard.render_header()

        # Verify console.print was called twice (panel + spacing)
        assert mock_print.call_count == 2

    @patch.object(Console, "print")
    def test_render_plans_empty(self, mock_print):
        """Test render_plans() handles empty plans list."""
        dashboard = MainDashboard()
        
        # Mock discovery after instantiation
        dashboard.discovery = Mock()
        dashboard.discovery.get_all_plans.return_value = []
        
        dashboard.render_plans()

        # Verify warning message displayed
        mock_print.assert_called_once_with("[yellow]No plans found in work-space/plans/[/yellow]")

    @patch.object(Console, "print")
    def test_render_plans_with_data(self, mock_print):
        """Test render_plans() displays plans table."""
        dashboard = MainDashboard()
        
        # Mock discovery and state_detector after instantiation
        dashboard.discovery = Mock()
        dashboard.state_detector = Mock()
        
        # Mock discovery to return plan paths
        dashboard.discovery.get_all_plans.return_value = [Path("/plans/PLAN1"), Path("/plans/PLAN2")]

        # Mock state detector to return plan states
        mock_state_1 = Mock(spec=PlanState)
        mock_state_1.name = "PLAN1"
        mock_state_1.last_achievement = "1.1"
        mock_state_1.next_achievements = ["1.2"]
        mock_state_1.pending_fixes = []

        mock_state_2 = Mock(spec=PlanState)
        mock_state_2.name = "PLAN2"
        mock_state_2.last_achievement = None
        mock_state_2.next_achievements = []
        mock_state_2.pending_fixes = []

        dashboard.state_detector.get_plan_state.side_effect = [mock_state_1, mock_state_2]

        dashboard.render_plans()

        # Verify console.print was called (table + spacing)
        assert mock_print.call_count == 2

    @patch.object(Console, "print")
    def test_render_prompt(self, mock_print):
        """Test render_prompt() displays user prompt."""
        dashboard = MainDashboard()
        dashboard.render_prompt()

        # Verify console.print was called
        mock_print.assert_called_once()

    @patch("rich.prompt.Prompt.ask")
    def test_get_user_input_quit(self, mock_ask):
        """Test get_user_input() returns 'q'."""
        mock_ask.return_value = "q"

        dashboard = MainDashboard()
        result = dashboard.get_user_input()

        assert result == "q"

    @patch("rich.prompt.Prompt.ask")
    def test_get_user_input_valid_number(self, mock_ask):
        """Test get_user_input() returns valid number."""
        mock_ask.return_value = "3"

        dashboard = MainDashboard()
        result = dashboard.get_user_input()

        assert result == "3"

    @patch("rich.prompt.Prompt.ask")
    def test_get_user_input_keyboard_interrupt(self, mock_ask):
        """Test get_user_input() returns 'q' on KeyboardInterrupt."""
        mock_ask.side_effect = KeyboardInterrupt()

        dashboard = MainDashboard()
        result = dashboard.get_user_input()

        assert result == "q"

    @patch("builtins.input")
    @patch.object(Console, "print")
    def test_open_plan_dashboard_placeholder(self, mock_print, mock_input):
        """Test open_plan_dashboard() shows placeholder message."""
        dashboard = MainDashboard()
        dashboard.open_plan_dashboard(0)

        # Verify placeholder message displayed (3 prints: blank line, message, prompt)
        assert mock_print.call_count == 3
        # Verify input was called (wait for user)
        mock_input.assert_called_once()


class TestTableRendering:
    """Tests for table rendering functions."""

    def test_create_plan_table_empty(self):
        """Test create_plan_table() with empty list."""
        table = create_plan_table([])

        assert isinstance(table, Table)
        assert table.title == "Active Plans"
        assert len(table.columns) == 5

    def test_create_plan_table_single_plan(self):
        """Test create_plan_table() with single plan."""
        mock_state = Mock(spec=PlanState)
        mock_state.name = "TEST-PLAN"
        mock_state.last_achievement = "1.1"
        mock_state.next_achievements = ["1.2"]
        mock_state.pending_fixes = []

        table = create_plan_table([mock_state])

        assert isinstance(table, Table)
        assert len(table.columns) == 5
        assert len(table.rows) == 1

    def test_create_plan_table_multiple_plans(self):
        """Test create_plan_table() with multiple plans."""
        mock_state_1 = Mock(spec=PlanState)
        mock_state_1.name = "PLAN1"
        mock_state_1.last_achievement = "1.1"
        mock_state_1.next_achievements = ["1.2"]
        mock_state_1.pending_fixes = []

        mock_state_2 = Mock(spec=PlanState)
        mock_state_2.name = "PLAN2"
        mock_state_2.last_achievement = None
        mock_state_2.next_achievements = ["0.1", "0.2"]
        mock_state_2.pending_fixes = []

        table = create_plan_table([mock_state_1, mock_state_2])

        assert isinstance(table, Table)
        assert len(table.columns) == 5
        assert len(table.rows) == 2

    def test_table_columns_correct(self):
        """Test table has correct columns."""
        table = create_plan_table([])

        assert len(table.columns) == 5
        assert table.columns[0].header == "#"
        assert table.columns[1].header == "Plan"
        assert table.columns[2].header == "Last"
        assert table.columns[3].header == "Next"
        assert table.columns[4].header == "Status"

    def test_table_title(self):
        """Test table has correct title."""
        table = create_plan_table([])

        assert table.title == "Active Plans"

    def test_table_formatting(self):
        """Test table has correct formatting."""
        table = create_plan_table([])

        assert table.show_header is True
        assert table.header_style == "bold cyan"

    def test_format_next_achievements_empty(self):
        """Test format_next_achievements() with empty list."""
        result = format_next_achievements([])

        assert result == "None"

    def test_format_next_achievements_single(self):
        """Test format_next_achievements() with single achievement."""
        result = format_next_achievements(["2.1"])

        assert result == "2.1"

    def test_format_next_achievements_two(self):
        """Test format_next_achievements() with two achievements."""
        result = format_next_achievements(["2.1", "2.2"])

        assert result == "2.1, 2.2"

    def test_format_next_achievements_three(self):
        """Test format_next_achievements() with three achievements."""
        result = format_next_achievements(["2.1", "2.2", "2.3"])

        assert result == "2.1, 2.2 (+1 more)"

    def test_format_next_achievements_many(self):
        """Test format_next_achievements() with many achievements."""
        result = format_next_achievements(["2.1", "2.2", "2.3", "2.4", "2.5"])

        assert result == "2.1, 2.2 (+3 more)"


class TestStatusIndicators:
    """Tests for status emoji functions."""

    def test_status_needs_attention_single_fix(self):
        """Test get_status_emoji() for single pending fix."""
        mock_state = Mock(spec=PlanState)
        mock_state.pending_fixes = ["FIX_11"]
        mock_state.last_achievement = "1.1"
        mock_state.next_achievements = ["1.2"]

        result = get_status_emoji(mock_state)

        assert result == "🔴 Needs attention (1 fix)"

    def test_status_needs_attention_multiple_fixes(self):
        """Test get_status_emoji() for multiple pending fixes."""
        mock_state = Mock(spec=PlanState)
        mock_state.pending_fixes = ["FIX_11", "FIX_12"]
        mock_state.last_achievement = "1.2"
        mock_state.next_achievements = ["1.3"]

        result = get_status_emoji(mock_state)

        assert result == "🔴 Needs attention (2 fixes)"

    def test_status_in_progress(self):
        """Test get_status_emoji() for in-progress plan."""
        mock_state = Mock(spec=PlanState)
        mock_state.pending_fixes = []
        mock_state.last_achievement = "1.1"
        mock_state.next_achievements = ["1.2", "1.3"]

        result = get_status_emoji(mock_state)

        assert result == "🟡 In progress"

    def test_status_ready_to_execute(self):
        """Test get_status_emoji() for ready plan."""
        mock_state = Mock(spec=PlanState)
        mock_state.pending_fixes = []
        mock_state.last_achievement = None
        mock_state.next_achievements = ["0.1"]

        result = get_status_emoji(mock_state)

        assert result == "🟢 Ready to execute"

    def test_status_no_next_action(self):
        """Test get_status_emoji() for complete/blocked plan."""
        mock_state = Mock(spec=PlanState)
        mock_state.pending_fixes = []
        mock_state.last_achievement = "3.3"
        mock_state.next_achievements = []

        result = get_status_emoji(mock_state)

        assert result == "⚪ No next action"

    def test_status_priority_fixes_first(self):
        """Test status priority: fixes take precedence."""
        mock_state = Mock(spec=PlanState)
        mock_state.pending_fixes = ["FIX_11"]
        mock_state.last_achievement = "1.1"
        mock_state.next_achievements = ["1.2"]

        result = get_status_emoji(mock_state)

        # Should show "needs attention" not "in progress"
        assert result.startswith("🔴 Needs attention")

