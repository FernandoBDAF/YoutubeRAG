"""
LLM/dashboard/main_dashboard.py - Main Dashboard Implementation

This module implements the main dashboard that displays all plans with their
current states, providing users with a single-view overview of the entire
LLM Methodology workspace.

Achievement: 0.3 - Main Dashboard Implementation
Updated: 2025-11-13
Achievement: 0.4 - Library Integration & Production Patterns
"""

from typing import List, Optional
from pathlib import Path
import time

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from core.libraries.logging import get_logger, set_log_context
from LLM.dashboard.base_dashboard import BaseDashboard
from LLM.dashboard.models import PlanState
from LLM.dashboard.plan_discovery import PlanDiscovery
from LLM.dashboard.state_detector import StateDetector
from LLM.dashboard.plan_dashboard import PlanDashboard
from LLM.dashboard.exceptions import (
    ActionExecutionError,
    InvalidUserInputError,
    PlanLoadError,
    StateDetectionError
)
from LLM.scripts.generation.exceptions import format_error_with_suggestions
from LLM.dashboard.metrics import (
    register_dashboard_metrics,
    track_action,
    track_load_time
)

logger = get_logger(__name__)


class MainDashboard(BaseDashboard):
    """
    Main dashboard showing all plans with their current states.

    This dashboard serves as the primary entry point for the CLI, displaying
    all discovered plans in a Rich-formatted table with status indicators.

    **Usage**:
        dashboard = MainDashboard()
        dashboard.show()  # Launch interactive dashboard
    """

    def __init__(
        self, console: Optional[Console] = None, workspace_root: Optional[Path] = None
    ):
        """
        Initialize dashboard with console and workspace root.

        Args:
            console: Optional Rich Console instance
            workspace_root: Optional workspace root path (defaults to current directory)
        """
        super().__init__(console)
        self.workspace_root = workspace_root or Path.cwd()
        
        # PlanDiscovery expects plans_root (work-space/plans/)
        plans_root = self.workspace_root / "work-space" / "plans"
        self.discovery = PlanDiscovery(plans_root=plans_root)
        
        # StateDetector doesn't take any init parameters
        self.state_detector = StateDetector()
        
        # Register metrics
        register_dashboard_metrics()

    def show(self):
        """
        Show main dashboard with interactive loop.

        Displays all plans in a table and provides options to:
        - Select a plan by number (placeholder for Achievement 1.1)
        - Quit with 'q'

        **Interactive Loop**:
        1. Clear screen
        2. Render header
        3. Render plans table
        4. Show prompt
        5. Handle user input
        6. Repeat until 'q'
        """
        start_time = time.time()
        
        set_log_context(
            dashboard='main',
            workspace=str(self.workspace_root)
        )
        
        logger.info("Dashboard opened", extra={'workspace_root': str(self.workspace_root)})
        
        # Track load time (initial render)
        load_duration = time.time() - start_time
        track_load_time('main', load_duration)
        
        try:
            while True:
                self.clear()
                self.render_header()
                self.render_plans()
                self.render_prompt()

                choice = self.get_user_input()
                if choice == "q":
                    self.print("[yellow]Goodbye![/yellow]")
                    logger.info("Dashboard closed by user")
                    track_action('close_dashboard', 'success')
                    break
                elif choice.isdigit():
                    plan_index = int(choice) - 1
                    self.open_plan_dashboard(plan_index)
        except KeyboardInterrupt:
            logger.info("Dashboard interrupted by user (KeyboardInterrupt)")
            self.print("\n[yellow]Goodbye![/yellow]")
            track_action('close_dashboard', 'interrupted')
        except Exception as e:
            logger.error("Dashboard error", exc_info=True)
            track_action('dashboard_error', 'error')
            raise

    def render_header(self):
        """
        Render dashboard header with title and navigation help.

        Displays a panel with:
        - Dashboard title
        - Navigation instructions
        """
        header_text = Text()
        header_text.append("LLM Methodology Dashboard\n", style=f"bold {self.get_color('primary')}")
        header_text.append("Navigate: Select plan by number | ", style="dim")
        header_text.append("'q' to quit", style=self.get_color("warning"))

        panel = Panel(header_text, border_style=self.get_color("info"), title="Main Dashboard")
        self.console.print(panel)
        self.console.print()  # Add spacing

    def render_plans(self):
        """
        Render plan list table.

        Discovers all plans using PlanDiscovery, detects their states using
        StateDetector, and displays them in a Rich table.

        **Table Columns**:
        - #: Plan index (for selection)
        - Plan: Plan name
        - Last: Last completed achievement
        - Next: Next available achievements
        - Status: Status emoji with description
        """
        try:
            plans = self.discovery.get_all_plans()

            if not plans:
                self.print("[yellow]No plans found in work-space/plans/[/yellow]")
                return

            plan_states = []
            for plan in plans:
                try:
                    state = self.state_detector.get_plan_state(plan)
                    plan_states.append(state)
                except StateDetectionError as e:
                    # Log error but continue with other plans
                    self.print(f"[red]Error detecting state for {plan.name}[/red]")
                    # Create minimal state for display
                    from LLM.dashboard.models import PlanStatus
                    minimal_state = PlanState(
                        name=plan.name,
                        plan_file=plan / "PLAN_unknown.md",
                        last_achievement=None,
                        next_achievements=[],
                        pending_reviews=[],
                        pending_fixes=[],
                        total_achievements=0,
                        completed_achievements=0,
                        progress_percentage=0.0,
                        status=PlanStatus.ACTIVE,
                    )
                    plan_states.append(minimal_state)

            table = create_plan_table(plan_states, self.theme)
            self.console.print(table)
            self.console.print()  # Add spacing
            
        except PlanLoadError as e:
            # Display formatted error
            error_output = format_error_with_suggestions(e)
            self.console.print(error_output)
            self.console.print()  # Add spacing

    def render_prompt(self):
        """
        Display user input prompt.

        Shows a styled prompt for user to select a plan or quit.
        """
        prompt_text = Text()
        prompt_text.append("Select plan ", style=self.get_color("primary"))
        prompt_text.append("(number) ", style=self.get_color("warning"))
        prompt_text.append("or ", style="dim")
        prompt_text.append("'q' ", style=self.get_color("warning"))
        prompt_text.append("to quit: ", style=self.get_color("primary"))
        self.console.print(prompt_text, end="")

    def get_user_input(self) -> str:
        """
        Get and validate user input.

        Returns:
            User's input (lowercase, stripped)

        **Valid Inputs**:
        - 'q': Quit dashboard
        - Number: Select plan by index
        """
        try:
            choice = Prompt.ask("", console=self.console, default="").lower().strip()
            return choice
        except (KeyboardInterrupt, EOFError):
            return "q"

    def open_plan_dashboard(self, plan_index: int):
        """
        Open plan-specific dashboard (Achievement 1.1).

        Args:
            plan_index: Index of the plan to open (0-based)

        Raises:
            InvalidUserInputError: If plan_index is out of range

        **Behavior**:
        Launches the plan-specific dashboard showing detailed information
        about the selected plan, including achievements, status, and actions.
        """
        try:
            plans = self.discovery.get_all_plans()
            
            if plan_index < 0 or plan_index >= len(plans):
                raise InvalidUserInputError(
                    f"Invalid plan index: {plan_index + 1}",
                    context={
                        'input': str(plan_index + 1),
                        'available_plans': len(plans),
                        'valid_range': f"1-{len(plans)}" if plans else "No plans available"
                    },
                    suggestions=[
                        f"Choose a number between 1 and {len(plans)}" if plans else "No plans available to select",
                        "Review the plan list",
                        "Press 'q' to quit"
                    ]
                )
            
            # Launch plan-specific dashboard (Achievement 1.1)
            logger.info("Opening plan dashboard", extra={
                'plan_index': plan_index + 1
            })
            
            plan_dashboard = PlanDashboard(plan_id=plan_index + 1, console=self.console)
            plan_dashboard.show()
            
            # Track successful action
            track_action('open_plan', 'success')
            
        except (PlanLoadError, ActionExecutionError, InvalidUserInputError) as e:
            # Display formatted error
            error_output = format_error_with_suggestions(e)
            self.console.print()
            self.console.print(error_output)
            self.console.print("[dim]Press Enter to continue...[/dim]")
            input()
            
            # Track error
            track_action('open_plan', 'error')


# =============================================================================
# Table Rendering Functions
# =============================================================================


def create_plan_table(plan_states: List[PlanState], theme=None) -> Table:
    """
    Create Rich table for plan list.

    Args:
        plan_states: List of PlanState objects
        theme: Optional Theme object for colors

    Returns:
        Rich Table with plan information

    **Table Structure**:
    - Column 1: # (index for selection)
    - Column 2: Plan (plan name)
    - Column 3: Last (last completed achievement)
    - Column 4: Next (next available achievements)
    - Column 5: Status (emoji + description)

    **Usage**:
        plan_states = [state1, state2, state3]
        table = create_plan_table(plan_states, theme)
        console.print(table)
    """
    # Import Theme here to avoid circular imports
    from LLM.dashboard.theme import Theme
    if theme is None:
        theme = Theme("default")
    
    table = Table(title="Active Plans", show_header=True, header_style=f"bold {theme.get_color('primary')}")

    table.add_column("#", style=theme.get_color("primary"), width=3)
    table.add_column("Plan", style="bold", width=40)
    table.add_column("Last", style=theme.get_color("success"), width=15)
    table.add_column("Next", style=theme.get_color("warning"), width=20)
    table.add_column("Status", style=theme.get_color("primary"), width=15)

    for i, plan in enumerate(plan_states, 1):
        status_emoji = get_status_emoji(plan)
        next_str = format_next_achievements(plan.next_achievements)

        table.add_row(
            str(i),
            plan.name,
            plan.last_achievement or "None",
            next_str,
            status_emoji,
        )

    return table


def get_status_emoji(plan: PlanState) -> str:
    """
    Get status emoji for plan (priority order).

    Args:
        plan: PlanState object

    Returns:
        Status string with emoji

    **Status Priority** (checked in order):
    1. 🔴 Needs attention: Has pending fixes
    2. 🟡 In progress: Has both last achievement and next achievements
    3. 🟢 Ready to execute: Has next achievements but no last achievement
    4. ⚪ No next action: No next achievements (complete or blocked)

    **Usage**:
        status = get_status_emoji(plan_state)
        # Returns: "🟢 Ready to execute"
    """
    if plan.pending_fixes:
        count = len(plan.pending_fixes)
        fix_word = "fix" if count == 1 else "fixes"
        return f"🔴 Needs attention ({count} {fix_word})"
    elif plan.next_achievements and plan.last_achievement:
        return "🟡 In progress"
    elif plan.next_achievements:
        return "🟢 Ready to execute"
    else:
        return "⚪ No next action"


def format_next_achievements(next_achievements: List[str]) -> str:
    """
    Format next achievements for display.

    Args:
        next_achievements: List of achievement IDs

    Returns:
        Formatted string

    **Format Examples**:
    - Empty list: "None"
    - 1 achievement: "2.1"
    - 2 achievements: "2.1, 2.2"
    - 3+ achievements: "2.1, 2.2 (+1 more)"
    - 4+ achievements: "2.1, 2.2 (+2 more)"

    **Usage**:
        formatted = format_next_achievements(["2.1", "2.2", "2.3"])
        # Returns: "2.1, 2.2 (+1 more)"
    """
    if not next_achievements:
        return "None"
    elif len(next_achievements) == 1:
        return next_achievements[0]
    elif len(next_achievements) == 2:
        return f"{next_achievements[0]}, {next_achievements[1]}"
    else:
        remaining = len(next_achievements) - 2
        return (
            f"{next_achievements[0]}, {next_achievements[1]} (+{remaining} more)"
        )

