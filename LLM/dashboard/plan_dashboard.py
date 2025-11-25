"""
Plan-specific dashboard for LLM Methodology.

Shows detailed information for a single plan including status,
quick stats, and available actions.
"""

from pathlib import Path
from typing import Union, Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
import time
import os
import atexit

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.table import Table

from LLM.dashboard.base_dashboard import BaseDashboard
from LLM.dashboard.plan_discovery import PlanDiscovery
from LLM.dashboard.state_detector import StateDetector
from LLM.dashboard.action_executor import ActionExecutor
from LLM.dashboard.workflow_executor import WorkflowExecutor
from LLM.dashboard.parallel_detector import ParallelDetector, ParallelGroup
from core.libraries.logging import get_logger

logger = get_logger(__name__)


@dataclass
class HealthScore:
    """Plan health score data."""

    score: float  # 0-100
    status: str  # "Excellent", "Good", "Fair", "Needs Attention"
    emoji: str  # "🟢", "🟡", "🟠", "🔴"
    breakdown: Dict[str, float]  # Component scores


@dataclass
class Action:
    """Dashboard action definition."""

    key: str  # Key to press (e.g., '1', '2')
    emoji: str  # Emoji indicator
    label: str  # Action label
    enabled: bool = True  # Whether action is available


class PlanDashboard(BaseDashboard):
    """
    Plan-specific dashboard showing detailed information for a single plan.

    Shows:
    - Plan header (name, description)
    - Status section (progress, last achievement, priority, remaining time)
    - Quick stats (SUBPLANs, EXECUTIONs, reviews, tests)
    - Navigation (back to main dashboard)

    Example:
        >>> from rich.console import Console
        >>> console = Console()
        >>> dashboard = PlanDashboard(plan_id=1, console=console)
        >>> dashboard.show()
    """

    def __init__(self, plan_id: Union[int, str], console: Console):
        """
        Initialize plan dashboard.

        Args:
            plan_id: Plan number (e.g., 1) or plan name (e.g., "@LLM-DASHBOARD-CLI")
            console: Rich Console instance

        Raises:
            ValueError: If plan not found or invalid plan_id
        """
        super().__init__(console)
        self.plan_path = self._resolve_plan(plan_id)
        self.discovery = PlanDiscovery()
        self.state_detector = StateDetector()
        self.state = self.state_detector.get_plan_state(self.plan_path)
        self.plan_name = self.plan_path.name
        self.parallel_detector = ParallelDetector(self.plan_path)
        self.workflow_executor = WorkflowExecutor(self.plan_path, self.console)
        
        # Achievement 2.3: Real-time state updates
        self.last_refresh_time = datetime.now()
        
        # Multi-instance detection (Achievement 2.3)
        if self.detect_multi_instance():
            from rich.prompt import Confirm
            self.console.print()
            self.console.print("[yellow]⚠️  Another dashboard instance is already running[/yellow]")
            if not Confirm.ask("Continue anyway?", default=False):
                raise RuntimeError("User cancelled - another instance running")
        
        self.create_lock_file()
        atexit.register(self.cleanup_lock_file)

        logger.info(
            "Plan dashboard initialized",
            extra={"plan_name": self.plan_name, "plan_path": str(self.plan_path)},
        )

    def show(self):
        """
        Show plan dashboard in interactive loop.

        Loop:
        1. Clear screen
        2. Render all sections
        3. Get user input
        4. Handle action or exit
        """
        logger.info("Plan dashboard opened", extra={"plan_name": self.plan_name})

        while True:
            self.clear()
            self.render_header()
            self.render_status()
            self.render_health_score()
            self.render_stats()
            self.render_achievements()
            self.render_parallel_opportunities()
            self.render_actions()
            self.render_refresh_footer()  # Achievement 2.3: Refresh indicators

            choice = self.get_user_input("\nEnter action: ")
            if choice.lower() in ["b", "back", "6"]:
                logger.info("Returning to main dashboard", extra={"plan_name": self.plan_name})
                break
            else:
                self.handle_action(choice)

        logger.info("Plan dashboard closed", extra={"plan_name": self.plan_name})

    def get_user_input(self, prompt_text: str = "") -> str:
        """
        Get and validate user input.

        Args:
            prompt_text: Prompt text to show user

        Returns:
            User's input (lowercase, stripped)

        Handles:
        - KeyboardInterrupt: Returns 'b' (go back)
        - EOFError: Returns 'b' (go back)
        - 'r': Manual refresh (Achievement 2.3)
        """
        try:
            if prompt_text:
                choice = Prompt.ask(prompt_text, console=self.console, default="").lower().strip()
            else:
                choice = Prompt.ask("", console=self.console, default="").lower().strip()
            
            # Achievement 2.3: Handle manual refresh
            if choice == 'r':
                self.handle_state_refresh()
                return ""  # Return empty to re-prompt
            
            return choice
        except (KeyboardInterrupt, EOFError):
            return "b"  # Return to main dashboard on interrupt

    def _resolve_plan(self, plan_id: Union[int, str]) -> Path:
        """
        Resolve plan ID to plan directory path.

        Args:
            plan_id: Either:
                - Integer (1, 2, 3) - plan number from main dashboard
                - String with @ ("@LLM-DASHBOARD-CLI") - plan name
                - String without @ ("LLM-DASHBOARD-CLI") - plan name

        Returns:
            Path to plan directory

        Raises:
            ValueError: If plan not found

        Example:
            >>> self._resolve_plan(1)
            Path('work-space/plans/LLM-DASHBOARD-CLI')
            >>> self._resolve_plan("@LLM-DASHBOARD-CLI")
            Path('work-space/plans/LLM-DASHBOARD-CLI')
        """
        discovery = PlanDiscovery()
        plans = discovery.get_all_plans()

        logger.debug(
            "Resolving plan", extra={"plan_id": str(plan_id), "available_plans": len(plans)}
        )

        # Handle integer (plan number from list)
        if isinstance(plan_id, int):
            if 1 <= plan_id <= len(plans):
                plan_path = plans[plan_id - 1]
                logger.debug(
                    "Plan resolved by number",
                    extra={"plan_id": plan_id, "plan_path": str(plan_path)},
                )
                return plan_path
            raise ValueError(f"Plan number {plan_id} out of range (1-{len(plans)})")

        # Handle string (plan name)
        plan_name = plan_id.lstrip("@").strip()

        # Find matching plan directory
        for plan_path in plans:
            if plan_path.name == plan_name:
                logger.debug(
                    "Plan resolved by name",
                    extra={"plan_name": plan_name, "plan_path": str(plan_path)},
                )
                return plan_path

        raise ValueError(f"Plan not found: {plan_name}")

    def render_header(self):
        """
        Render plan dashboard header.

        Shows:
        - Plan name (bold primary color)
        - "Plan Dashboard" subtitle
        """
        header = Text()
        header.append(f"📋 {self.plan_name}\n", style=f"bold {self.get_color('primary')}")
        header.append("Plan Dashboard", style="dim")

        panel = Panel(header, border_style=self.get_color("primary"), padding=(1, 2))
        self.console.print(panel)
        self.console.print()

    def render_status(self):
        """
        Render plan status section.

        Shows:
        - Progress (X/Y achievements, percentage)
        - Last completed achievement (with APPROVED file reference)
        - Current priority level
        - Estimated remaining hours

        Format:
            📊 Plan Status
            ├─ Progress: 11/18 achievements (61%)
            ├─ Last Complete: 3.1 (✅ APPROVED_31.md)
            ├─ Priority: Unknown (MVP placeholder)
            └─ Estimated Remaining: 9-12 hours
        """
        content = Text()
        content.append("📊 Plan Status\n", style=f"bold {self.get_color('primary')}")

        # Progress
        if self.state.total_achievements > 0:
            progress_pct = self.state.completed_achievements / self.state.total_achievements * 100
            content.append(
                f"├─ Progress: {self.state.completed_achievements}/{self.state.total_achievements} achievements ({progress_pct:.0f}%)\n"
            )
        else:
            content.append("├─ Progress: 0/0 achievements (new plan)\n")

        # Last complete achievement
        if self.state.last_achievement:
            ach_num = self.state.last_achievement.replace(".", "")
            content.append(
                f"├─ Last Complete: {self.state.last_achievement} (✅ APPROVED_{ach_num}.md)\n"
            )
        else:
            content.append("├─ Last Complete: None (new plan)\n")

        # Current priority
        priority_desc = self._get_current_priority()
        content.append(f"├─ Priority: {priority_desc}\n")

        # Estimated remaining time
        remaining_hours = self._estimate_remaining_hours()
        content.append(f"└─ Estimated Remaining: {remaining_hours}\n")

        panel = Panel(content, border_style=self.get_color("primary"), padding=(1, 2))
        self.console.print(panel)

    def _get_current_priority(self) -> str:
        """
        Get current priority level.

        For MVP: Return "Unknown" placeholder
        Future: Parse from PLAN file or derive from last achievement

        Returns:
            Priority description string
        """
        # TODO: Implement priority detection in future iteration
        return "Unknown (will implement in future iteration)"

    def _estimate_remaining_hours(self) -> str:
        """
        Estimate remaining hours based on pending achievements.

        Logic:
        - Count pending achievements (total - completed)
        - Assume 3-4 hours per achievement (average)
        - Return range (e.g., "9-12 hours")

        Returns:
            Formatted time estimate string
        """
        pending = self.state.total_achievements - self.state.completed_achievements

        if pending == 0:
            return "0 hours (complete!)"
        elif pending == 1:
            return "3-4 hours"
        else:
            min_hours = pending * 3
            max_hours = pending * 4
            return f"{min_hours}-{max_hours} hours"

    def render_stats(self):
        """
        Render quick stats section.

        Shows:
        - SUBPLANs: Created vs waiting
        - EXECUTIONs: Complete vs active
        - Reviews: Approved vs pending fixes
        - Tests: Passing/total (placeholder for MVP)

        Format:
            ⚡ Quick Stats
            ├─ SUBPLANs: 11 created, 0 waiting
            ├─ EXECUTIONs: 11 complete, 0 active
            ├─ Reviews: 11 approved, 0 fixes pending
            └─ Tests: 0/0 (not yet integrated)
        """
        stats = self._calculate_stats()

        content = Text()
        content.append("⚡ Quick Stats\n", style=f"bold {self.get_color('info')}")

        # SUBPLANs
        content.append(
            f"├─ SUBPLANs: {stats['subplans_created']} created, {stats['subplans_waiting']} waiting\n"
        )

        # EXECUTIONs
        content.append(
            f"├─ EXECUTIONs: {stats['executions_complete']} complete, {stats['executions_active']} active\n"
        )

        # Reviews
        content.append(
            f"├─ Reviews: {stats['reviews_approved']} approved, {stats['reviews_pending']} fixes pending\n"
        )

        # Tests (placeholder for MVP)
        if stats["tests_total"] > 0:
            test_pct = stats["tests_passing"] / stats["tests_total"] * 100
            content.append(
                f"└─ Tests: {stats['tests_passing']}/{stats['tests_total']} passing ({test_pct:.1f}%)\n"
            )
        else:
            content.append("└─ Tests: 0/0 (not yet integrated)\n")

        panel = Panel(content, border_style=self.get_color("info"), padding=(1, 2))
        self.console.print(panel)

    def _calculate_stats(self) -> Dict[str, int]:
        """
        Calculate statistics from filesystem state.

        Returns:
            Dictionary with:
            - subplans_created: Count of SUBPLAN_*.md files
            - subplans_waiting: Count of achievements without SUBPLANs
            - executions_complete: Count of APPROVED files
            - executions_active: Count of EXECUTION_TASK files without APPROVED
            - reviews_approved: Count of APPROVED_*.md files
            - reviews_pending: Count of FIX_*.md files
            - tests_passing: 0 (placeholder for future)
            - tests_total: 0 (placeholder for future)
        """
        stats = {
            "subplans_created": 0,
            "subplans_waiting": 0,
            "executions_complete": 0,
            "executions_active": 0,
            "reviews_approved": 0,
            "reviews_pending": 0,
            "tests_passing": 0,
            "tests_total": 0,
        }

        # Count SUBPLANs
        subplans_dir = self.plan_path / "subplans"
        if subplans_dir.exists():
            stats["subplans_created"] = len(list(subplans_dir.glob("SUBPLAN_*.md")))

        # Count achievements waiting for SUBPLANs
        stats["subplans_waiting"] = max(
            0, self.state.total_achievements - stats["subplans_created"]
        )

        # Count reviews (APPROVED and FIX files)
        feedbacks_dir = self.plan_path / "execution" / "feedbacks"
        if feedbacks_dir.exists():
            stats["reviews_approved"] = len(list(feedbacks_dir.glob("APPROVED_*.md")))
            stats["reviews_pending"] = len(list(feedbacks_dir.glob("FIX_*.md")))

        # Count EXECUTIONs
        execution_dir = self.plan_path / "execution"
        if execution_dir.exists():
            execution_files = list(execution_dir.glob("EXECUTION_TASK_*_01.md"))
            stats["executions_active"] = len(execution_files)
            stats["executions_complete"] = stats["reviews_approved"]

        # Tests (placeholder - will implement in future achievement)
        stats["tests_passing"] = 0
        stats["tests_total"] = 0

        logger.debug("Stats calculated", extra={"plan_name": self.plan_name, "stats": stats})

        return stats

    def _get_all_achievements(self) -> List[Dict[str, str]]:
        """
        Parse all achievements from PLAN file.

        Parses the "Achievement Index" section and extracts:
        - Achievement number (e.g., "1.1")
        - Achievement title (e.g., "Plan-Specific Dashboard")

        Returns:
            List of achievement dicts with 'number' and 'title' keys
        """
        achievements = []

        plan_file = self.state.plan_file
        if not plan_file or not plan_file.exists():
            return []

        try:
            content = plan_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            logger.error(
                "Failed to read PLAN file for achievements",
                exc_info=True,
                extra={"plan_file": str(plan_file)},
            )
            return []

        # Parse Achievement Index section
        # Look for "## Achievement Index" or "## 📋 Achievement Index"
        index_pattern = re.compile(r"^##\s+(?:📋\s+)?Achievement Index", re.MULTILINE)
        match = index_pattern.search(content)

        if not match:
            logger.warning(
                "No Achievement Index found in PLAN", extra={"plan_file": str(plan_file)}
            )
            return []

        # Extract section after Achievement Index
        index_start = match.end()
        # Find next ## heading or end of file
        next_heading = re.search(r"^##\s+", content[index_start:], re.MULTILINE)
        index_end = index_start + next_heading.start() if next_heading else len(content)
        index_section = content[index_start:index_end]

        # Parse achievements: "- Achievement X.Y: Title"
        ach_pattern = re.compile(r"-\s+Achievement\s+(\d+\.\d+):\s+(.+?)(?:\n|$)")

        for match in ach_pattern.finditer(index_section):
            number = match.group(1)
            title = match.group(2).strip()

            achievements.append({"number": number, "title": title})

        logger.debug(
            "Achievements parsed",
            extra={"plan_name": self.plan_name, "achievement_count": len(achievements)},
        )

        return achievements

    def render_achievements(self):
        """
        Render achievement list with states.

        Shows:
        - Achievement number (e.g., "1.1", "2.3")
        - Achievement title
        - Current status (with emoji)
        - Next action (what to do)
        """
        achievements = self._get_all_achievements()

        if not achievements:
            self.console.print(f"[{self.get_color('warning')}]No achievements found in plan[/{self.get_color('warning')}]")
            return

        table = Table(
            title="📋 Achievements", show_header=True, header_style=f"bold {self.get_color('primary')}", border_style=self.get_color("primary")
        )

        table.add_column("Number", style="bold", width=12)
        table.add_column("Title", width=40)
        table.add_column("Status", width=20)
        table.add_column("Action", width=15)

        for ach in achievements:
            status_str = self._format_status(ach)
            action_str = self._format_action(ach)

            table.add_row(ach["number"], ach["title"], status_str, action_str)

        self.console.print(table)
        self.console.print()

    def _format_status(self, achievement: Dict) -> str:
        """
        Format achievement status with emoji.

        Status Priority (check in order):
        1. APPROVED (highest priority - completed)
        2. FIX pending (needs attention)
        3. In progress (has EXECUTION, no APPROVED)
        4. SUBPLAN ready (has SUBPLAN, no EXECUTION)
        5. Not started (default)

        Args:
            achievement: Achievement dict with 'number' and 'title'

        Returns:
            Formatted status string with emoji
        """
        ach_num = achievement["number"].replace(".", "")

        # Check for APPROVED (complete)
        approved_file = self.plan_path / "execution" / "feedbacks" / f"APPROVED_{ach_num}.md"
        if approved_file.exists():
            return "[green]✅ APPROVED[/green]"

        # Check for FIX (needs attention)
        fix_file = self.plan_path / "execution" / "feedbacks" / f"FIX_{ach_num}.md"
        if fix_file.exists():
            return "[red]⚠️ FIX pending[/red]"

        # Check for EXECUTION (in progress)
        execution_pattern = f"EXECUTION_TASK_*_{ach_num}_*.md"
        execution_dir = self.plan_path / "execution"
        if execution_dir.exists() and list(execution_dir.glob(execution_pattern)):
            return "[yellow]🔄 In progress[/yellow]"

        # Check for SUBPLAN (ready to execute)
        subplan_pattern = f"SUBPLAN_*_{ach_num}.md"
        subplans_dir = self.plan_path / "subplans"
        if subplans_dir.exists() and list(subplans_dir.glob(subplan_pattern)):
            return "[cyan]📝 SUBPLAN ready[/cyan]"

        # Not started
        return "[dim]⏸️ Not started[/dim]"

    def _format_action(self, achievement: Dict) -> str:
        """
        Format next action for achievement.

        Args:
            achievement: Achievement dict

        Returns:
            Formatted action string
        """
        ach_num = achievement["number"].replace(".", "")

        # Complete
        approved_file = self.plan_path / "execution" / "feedbacks" / f"APPROVED_{ach_num}.md"
        if approved_file.exists():
            return "[dim]Complete[/dim]"

        # Fix
        fix_file = self.plan_path / "execution" / "feedbacks" / f"FIX_{ach_num}.md"
        if fix_file.exists():
            return "[red]Fix issues[/red]"

        # Continue execution
        execution_pattern = f"EXECUTION_TASK_*_{ach_num}_*.md"
        execution_dir = self.plan_path / "execution"
        if execution_dir.exists() and list(execution_dir.glob(execution_pattern)):
            return "[yellow]Continue[/yellow]"

        # Execute (SUBPLAN ready)
        subplan_pattern = f"SUBPLAN_*_{ach_num}.md"
        subplans_dir = self.plan_path / "subplans"
        if subplans_dir.exists() and list(subplans_dir.glob(subplan_pattern)):
            return "[cyan]Execute[/cyan]"

        # Design (need SUBPLAN)
        return "Design"

    def calculate_health_score(self) -> HealthScore:
        """
        Calculate overall plan health score (0-100).

        Components (total 100 points):
        - 30 points: Achievement completion rate
        - 20 points: No pending fixes
        - 20 points: No stale executions (>7 days old)
        - 15 points: Test pass rate (placeholder)
        - 15 points: Documentation complete (placeholder)

        Returns:
            HealthScore with score, status, emoji, and breakdown
        """
        breakdown = {}
        score = 0.0

        # 30 points: Achievement completion rate
        if self.state.total_achievements > 0:
            completion_rate = self.state.completed_achievements / self.state.total_achievements
            completion_points = 30 * completion_rate
            score += completion_points
            breakdown["completion"] = completion_points
        else:
            breakdown["completion"] = 0.0

        # 20 points: No pending fixes
        stats = self._calculate_stats()
        if stats["reviews_pending"] == 0:
            score += 20
            breakdown["no_fixes"] = 20.0
        else:
            breakdown["no_fixes"] = 0.0

        # 20 points: No stale executions (>7 days old)
        stale_count = self._count_stale_executions()
        if stale_count == 0:
            score += 20
            breakdown["no_stale"] = 20.0
        else:
            breakdown["no_stale"] = 0.0

        # 15 points: Test pass rate (placeholder for MVP)
        test_pass_rate = 0  # TODO: Integrate with pytest
        if stats["tests_total"] > 0:
            test_points = 15 * (test_pass_rate / 100)
            score += test_points
            breakdown["tests"] = test_points
        else:
            breakdown["tests"] = 0.0

        # 15 points: Documentation complete (placeholder for MVP)
        # TODO: Check for README, guides, etc.
        breakdown["docs"] = 0.0

        return HealthScore(
            score=score,
            status=self._get_health_status(score),
            emoji=self._get_health_emoji(score),
            breakdown=breakdown,
        )

    def _get_health_status(self, score: float) -> str:
        """Get health status from score."""
        if score >= 95:
            return "Excellent"
        elif score >= 80:
            return "Good"
        elif score >= 60:
            return "Fair"
        else:
            return "Needs Attention"

    def _get_health_emoji(self, score: float) -> str:
        """Get health emoji from score."""
        if score >= 95:
            return "🟢"
        elif score >= 80:
            return "🟡"
        elif score >= 60:
            return "🟠"
        else:
            return "🔴"

    def _count_stale_executions(self) -> int:
        """
        Count EXECUTION files older than 7 days without APPROVED.

        Returns:
            Count of stale executions
        """
        stale_count = 0
        execution_dir = self.plan_path / "execution"

        if not execution_dir.exists():
            return 0

        seven_days_ago = datetime.now() - timedelta(days=7)

        for exec_file in execution_dir.glob("EXECUTION_TASK_*_01.md"):
            # Extract achievement number from filename
            # Format: EXECUTION_TASK_{PLAN}_{ACH_NUM}_01.md
            parts = exec_file.stem.split("_")
            if len(parts) >= 4:
                ach_num = parts[-2]  # Second to last part

                # Check if APPROVED exists
                approved_file = (
                    self.plan_path / "execution" / "feedbacks" / f"APPROVED_{ach_num}.md"
                )

                if not approved_file.exists():
                    # Check file age
                    try:
                        mtime = datetime.fromtimestamp(exec_file.stat().st_mtime)
                        if mtime < seven_days_ago:
                            stale_count += 1
                    except OSError:
                        pass  # Skip if can't read mtime

        return stale_count

    def render_health_score(self):
        """
        Render plan health score.

        Shows:
        - Overall score (0-100)
        - Status (Excellent, Good, Fair, Needs Attention)
        - Emoji indicator
        - Breakdown of score components
        """
        health = self.calculate_health_score()

        content = Text()
        content.append(
            f"{health.emoji} Score: {health.score:.0f}/100 - {health.status}\n\n", style="bold"
        )
        content.append("Breakdown:\n")

        # Completion
        if "completion" in health.breakdown:
            completion_pct = (
                (self.state.completed_achievements / self.state.total_achievements * 100)
                if self.state.total_achievements > 0
                else 0
            )
            content.append(
                f"  ✅ Completion: {health.breakdown['completion']:.0f}/30 ({self.state.completed_achievements}/{self.state.total_achievements} achievements, {completion_pct:.0f}%)\n"
            )

        # No fixes
        if health.breakdown.get("no_fixes", 0) > 0:
            content.append(f"  ✅ No pending fixes: {health.breakdown['no_fixes']:.0f}/20\n")
        else:
            stats = self._calculate_stats()
            content.append(f"  ⚠️ Has pending fixes: 0/20 ({stats['reviews_pending']} fixes)\n")

        # No stale
        if health.breakdown.get("no_stale", 0) > 0:
            content.append(f"  ✅ No stale executions: {health.breakdown['no_stale']:.0f}/20\n")
        else:
            stale_count = self._count_stale_executions()
            content.append(f"  ⚠️ Has stale executions: 0/20 ({stale_count} >7 days)\n")

        # Tests (placeholder)
        content.append(f"  ⏸️ Tests: {health.breakdown.get('tests', 0):.0f}/15 (not integrated)\n")

        # Docs (placeholder)
        content.append(f"  ⏸️ Docs: {health.breakdown.get('docs', 0):.0f}/15 (not integrated)\n")

        border_style = self.get_color("success") if health.score >= 80 else self.get_color("warning") if health.score >= 60 else self.get_color("error")
        panel = Panel(content, title="🏥 Plan Health", border_style=border_style, padding=(1, 2))
        self.console.print(panel)
        self.console.print()

    def render_parallel_opportunities(self):
        """
        Render parallel execution opportunities section.

        Only shown if parallel.json exists. Shows:
        - Parallel groups by dependency level
        - Achievements in each group
        - Time savings (parallel vs sequential)
        """
        if not self.parallel_detector.has_parallel_opportunities():
            return  # Don't show section if no parallel.json

        logger.debug("Rendering parallel opportunities", extra={"plan_name": self.plan_name})

        try:
            groups = self.parallel_detector.detect_parallel_opportunities()

            if not groups:
                return  # All complete, don't show empty section

            content = Text()
            content.append("🔀 Parallel Execution Opportunities\n\n", style=f"bold {self.get_color('primary')}")

            for group in groups:
                # Group header
                content.append(
                    f"Level {group.level} Group ({len(group.achievements)} achievements):\n",
                    style=self.get_color("primary"),
                )

                # List achievements
                for i, achievement_id in enumerate(group.achievement_ids):
                    if i < len(group.achievement_ids) - 1:
                        content.append(f"  ├─ {achievement_id}\n")
                    else:
                        content.append(f"  └─ {achievement_id}\n")

                # Time savings
                content.append(
                    f"  └─ Time: {group.parallel_time:.1f}h parallel vs {group.sequential_time:.1f}h sequential\n"
                )
                content.append(
                    f"     Savings: {group.time_savings:.1f}h ({group.savings_percentage:.0f}%)\n",
                    style=self.get_color("success"),
                )
                content.append("\n")

            panel = Panel(content, border_style=self.get_color("primary"), padding=(1, 2))
            self.console.print(panel)
            self.console.print()

        except Exception as e:
            logger.error(
                "Failed to render parallel opportunities",
                exc_info=True,
                extra={"plan_name": self.plan_name},
            )
            # Silently skip section on error - don't break dashboard

    def render_actions(self):
        """
        Render action menu.

        Shows:
        - Available actions with key bindings
        - Emoji indicators for each action
        - Enabled/disabled state
        """
        actions = self._get_available_actions()

        content = Text()
        content.append("🎯 Available Actions\n\n", style=f"bold {self.get_color('success')}")

        for action in actions:
            if action.enabled:
                content.append(f"{action.key}. {action.emoji} {action.label}\n")
            else:
                content.append(f"{action.key}. {action.emoji} {action.label} ", style="dim")
                content.append("[dim](disabled)[/dim]\n")

        panel = Panel(content, border_style=self.get_color("success"), padding=(1, 2))
        self.console.print(panel)

    def _get_available_actions(self) -> List[Action]:
        """
        Get list of available actions based on plan state.

        Returns:
            List of Action objects
        """
        # Execute Next only enabled if next achievements exist
        has_next = len(self.state.next_achievements) > 0

        # Parallel execution only enabled if parallel.json exists and has opportunities
        has_parallel = False
        try:
            if self.parallel_detector.has_parallel_opportunities():
                groups = self.parallel_detector.detect_parallel_opportunities()
                has_parallel = len(groups) > 0
        except Exception:
            has_parallel = False

        actions = [
            Action("1", "▶️", "Execute Next Achievement", enabled=has_next),
            Action("2", "🔀", "Execute Parallel Group", enabled=has_parallel),
            Action("3", "📝", "Create SUBPLAN", enabled=True),
            Action("4", "🔄", "Create EXECUTION", enabled=True),
            Action("5", "📚", "View Documentation", enabled=True),
            Action("6", "🔙", "Back to Plans", enabled=True),
        ]
        return actions

    def handle_action(self, choice: str):
        """
        Handle user action choice.

        Args:
            choice: User's input (action key)
        """
        if choice == "1":
            self._action_execute_next()
        elif choice == "2":
            self._action_execute_parallel()
        elif choice == "3":
            self._action_create_subplan()
        elif choice == "4":
            self._action_create_execution()
        elif choice == "5":
            self._action_view_documentation()
        elif choice.lower() == "s":
            self.show_settings()
        elif choice == "6" or choice.lower() in ["b", "back"]:
            return  # Exit handled in show() loop
        else:
            self.console.print("[red]Invalid choice. Please select 1-6 or 's'.[/red]")
            self.console.print("Press any key to continue...")
            self.get_user_input("")

    def _action_execute_next(self):
        """Execute next achievement action (Achievement 2.2)."""
        if not self.state.next_achievements:
            self.console.print("[yellow]No achievements ready to execute[/yellow]")
            self.console.print("Press any key to continue...")
            self.get_user_input("")
            return

        # Use WorkflowExecutor for interactive workflow with progress tracking
        result = self.workflow_executor.execute_workflow("next")
        
        # Achievement 2.3: Auto-refresh after action
        if result.success:
            self.auto_refresh_after_action()
        
        # Result display handled by workflow_executor, just pause for user
        self.console.print("[dim]Press any key to continue...[/dim]")
        self.get_user_input("")

    def _action_execute_parallel(self):
        """Execute parallel group action."""
        if not self.parallel_detector.has_parallel_opportunities():
            self.console.print("[yellow]No parallel.json found[/yellow]")
            self.console.print("Press any key to continue...")
            self.get_user_input("")
            return

        try:
            groups = self.parallel_detector.detect_parallel_opportunities()

            if not groups:
                self.console.print("[yellow]No parallel opportunities available (all complete)[/yellow]")
                self.console.print("Press any key to continue...")
                self.get_user_input("")
                return

            # Show available groups
            self.console.print()
            self.console.print("[bold cyan]Available Parallel Groups:[/bold cyan]")
            for i, group in enumerate(groups):
                self.console.print(
                    f"{i + 1}. Level {group.level}: {len(group.achievements)} achievements "
                    f"({group.time_savings:.1f}h savings)"
                )

            # Get user choice
            self.console.print()
            choice = Prompt.ask(
                "Select group to execute (or 'b' to cancel)",
                console=self.console,
                default="1",
            )

            if choice.lower() in ["b", "back", "cancel"]:
                return

            try:
                group_index = int(choice) - 1
                if group_index < 0 or group_index >= len(groups):
                    self.console.print("[red]Invalid group number[/red]")
                    self.console.print("Press any key to continue...")
                    self.get_user_input("")
                    return

                selected_group = groups[group_index]
                self._show_parallel_execution_instructions(selected_group)

            except ValueError:
                self.console.print("[red]Invalid input. Please enter a number.[/red]")
                self.console.print("Press any key to continue...")
                self.get_user_input("")
                return

        except Exception as e:
            logger.error(
                "Error in parallel execution action",
                exc_info=True,
                extra={"plan_name": self.plan_name},
            )
            self.console.print(f"[red]Error: {str(e)}[/red]")
            self.console.print("Press any key to continue...")
            self.get_user_input("")

    def _show_parallel_execution_instructions(self, group: ParallelGroup):
        """
        Show instructions for executing a parallel group.

        Args:
            group: ParallelGroup to execute
        """
        self.console.print()
        primary = self.get_color("primary")
        warning = self.get_color("warning")
        self.console.print(Panel(
            f"[bold {primary}]Parallel Execution Instructions[/bold {primary}]\n\n"
            f"Level {group.level} Group: {len(group.achievements)} achievements\n"
            f"Achievements: {', '.join(group.achievement_ids)}\n\n"
            f"[{warning}]Time Savings:[/{warning}] {group.time_savings:.1f}h ({group.savings_percentage:.0f}%)\n"
            f"  • Sequential: {group.sequential_time:.1f}h\n"
            f"  • Parallel: {group.parallel_time:.1f}h",
            border_style=primary,
            padding=(1, 2),
        ))

        self.console.print()
        self.console.print("[bold green]Step 1: Create SUBPLANs for parallel group[/bold green]")
        self.console.print()
        self.console.print("Run this command:")
        self.console.print()
        self.console.print(
            f"[cyan]python LLM/scripts/generation/batch_subplan.py "
            f"--plan-path {self.plan_path} --level {group.level}[/cyan]"
        )

        self.console.print()
        self.console.print("[bold green]Step 2: Create EXECUTIONs for parallel group[/bold green]")
        self.console.print()
        self.console.print("Run this command:")
        self.console.print()
        self.console.print(
            f"[cyan]python LLM/scripts/generation/batch_execution.py "
            f"--plan-path {self.plan_path} --level {group.level}[/cyan]"
        )

        self.console.print()
        self.console.print("[bold green]Step 3: Execute in parallel[/bold green]")
        self.console.print()
        self.console.print("Open multiple terminals and run:")
        for ach_id in group.achievement_ids:
            ach_num = ach_id.replace(".", "")
            self.console.print(
                f"[cyan]python LLM/scripts/generation/generate_prompt.py continue "
                f"@EXECUTION_TASK_{self.plan_name}_{ach_num}_01.md[/cyan]"
            )

        self.console.print()
        self.console.print("[dim]Press any key to continue...[/dim]")
        self.get_user_input("")

    def _action_create_subplan(self):
        """Create SUBPLAN action (Achievement 2.2)."""
        self.console.print()
        ach_num = Prompt.ask("Enter achievement number (e.g., 1.2)", console=self.console)

        if not ach_num or ach_num.lower() in ["b", "back", "cancel"]:
            return

        # Use WorkflowExecutor for interactive workflow with progress tracking
        result = self.workflow_executor.execute_workflow("subplan", achievement_id=ach_num)
        
        # Achievement 2.3: Auto-refresh after action
        if result.success:
            self.auto_refresh_after_action()
        
        # Result display handled by workflow_executor, just pause for user
        self.console.print("[dim]Press any key to continue...[/dim]")
        self.get_user_input("")

    def _action_create_execution(self):
        """Create EXECUTION action (Achievement 2.2)."""
        self.console.print()
        ach_num = Prompt.ask("Enter achievement number (e.g., 1.2)", console=self.console)

        if not ach_num or ach_num.lower() in ["b", "back", "cancel"]:
            return

        # Convert achievement number to SUBPLAN ID (e.g., "1.2" -> "12")
        subplan_id = ach_num.replace(".", "")
        
        # Use WorkflowExecutor for interactive workflow with progress tracking
        result = self.workflow_executor.execute_workflow("execution", subplan_id=subplan_id)
        
        # Achievement 2.3: Auto-refresh after action
        if result.success:
            self.auto_refresh_after_action()
        
        # Result display handled by workflow_executor, just pause for user
        self.console.print("[dim]Press any key to continue...[/dim]")
        self.get_user_input("")

    def _action_view_documentation(self):
        """View documentation action."""
        self._show_documentation_menu()

    def _show_documentation_menu(self):
        """
        Show documentation menu with available docs.

        Displays:
        - List of available documentation files
        - Quick access to guides and references
        """
        docs = [
            ("1", "SUBPLAN Workflow Guide", "LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md"),
            ("2", "EXECUTION Task Template", "LLM/templates/EXECUTION_TASK-TEMPLATE.md"),
            ("3", "SUBPLAN Template", "LLM/templates/SUBPLAN-TEMPLATE.md"),
            ("4", "Prompts Reference", "LLM/templates/PROMPTS.md"),
            ("5", "Dashboard README", "LLM/dashboard/README.md"),
            ("6", "Main README", "README.md"),
        ]

        self.clear()

        content = Text()
        content.append("📚 Documentation\n\n", style=f"bold {self.get_color('primary')}")

        for num, title, path in docs:
            # Check if file exists
            doc_file = Path(path)
            if doc_file.exists():
                content.append(f"{num}. {title}\n")
            else:
                content.append(f"{num}. {title} ", style="dim")
                content.append("[dim](not found)[/dim]\n")

        content.append("\nb. Back to dashboard\n", style="dim")

        panel = Panel(content, title="Available Documentation", border_style=self.get_color("primary"), padding=(1, 2))
        self.console.print(panel)

        choice = Prompt.ask(
            "\nSelect document (1-6) or 'b' for back", console=self.console, default="b"
        )

        if choice.lower() == "b":
            return

        if choice.isdigit() and 1 <= int(choice) <= 6:
            doc_path = docs[int(choice) - 1][2]
            self._open_document(doc_path)

    def _open_document(self, doc_path: str):
        """
        Open document in pager or print preview.

        Args:
            doc_path: Path to documentation file
        """
        doc_file = Path(doc_path)

        if not doc_file.exists():
            self.console.print(f"\n[red]Document not found: {doc_path}[/red]")
            self.console.print("Press any key to continue...")
            self.get_user_input("")
            return

        # Try to open in less (pager)
        try:
            import subprocess

            result = subprocess.run(["less", str(doc_file)], check=False)

            logger.info("Document viewed", extra={"doc_path": doc_path})

        except FileNotFoundError:
            # Fallback: print first 50 lines
            try:
                with doc_file.open("r") as f:
                    lines = f.readlines()[:50]
                    self.console.print("".join(lines))

                    # Count total lines
                    f.seek(0)
                    total_lines = sum(1 for _ in f)

                    self.console.print(f"\n[cyan]Showing first 50 of {total_lines} lines[/cyan]")
                    self.console.print(f"[cyan]Full doc: {doc_path}[/cyan]")

                    logger.info(
                        "Document preview shown",
                        extra={"doc_path": doc_path, "lines_shown": 50, "total_lines": total_lines},
                    )

            except OSError as e:
                self.console.print(f"\n[red]Failed to read document: {e}[/red]")

                logger.error("Failed to read document", exc_info=True, extra={"doc_path": doc_path})

            self.console.print("\nPress any key to continue...")
            self.get_user_input("")
    
    # ========================================================================
    # Achievement 2.3: Real-Time State Updates
    # ========================================================================
    
    def handle_state_refresh(self):
        """
        Handle manual state refresh with cache invalidation.
        
        Achievement 2.3: Manual refresh mechanism
        
        Clears all caches and reloads state from filesystem.
        Shows refresh indicator to user.
        """
        self.console.print()
        self.console.print("[cyan]🔄 Refreshing state...[/cyan]")
        
        # Clear caches (if they exist)
        if hasattr(self.state_detector.get_plan_state, 'cache'):
            self.state_detector.get_plan_state.cache.clear()
        if hasattr(self.discovery.get_all_plans, 'cache'):
            self.discovery.get_all_plans.cache.clear()
        
        # Reload state from filesystem
        self.state = self.state_detector.get_plan_state(self.plan_path)
        self.last_refresh_time = datetime.now()
        
        # Show success indicator
        self.console.print("[green]✓ State refreshed from filesystem[/green]")
        
        logger.info(
            "State manually refreshed",
            extra={"plan_name": self.plan_name, "cache_cleared": True}
        )
        
        time.sleep(0.5)  # Brief pause to show message
    
    def auto_refresh_after_action(self):
        """
        Auto-refresh state after any action execution.
        
        Achievement 2.3: Auto-refresh mechanism
        
        Called after workflow actions that may change filesystem state.
        Adds brief delay for filesystem to settle.
        """
        logger.info("Auto-refreshing after action", extra={"plan_name": self.plan_name})
        
        # Give filesystem time to settle
        time.sleep(0.5)
        
        # Clear caches
        if hasattr(self.state_detector.get_plan_state, 'cache'):
            self.state_detector.get_plan_state.cache.clear()
        if hasattr(self.discovery.get_all_plans, 'cache'):
            self.discovery.get_all_plans.cache.clear()
        
        # Reload state
        self.state = self.state_detector.get_plan_state(self.plan_path)
        self.last_refresh_time = datetime.now()
    
    def detect_multi_instance(self) -> bool:
        """
        Detect if another dashboard instance is running.
        
        Achievement 2.3: Multi-instance detection
        
        Returns:
            True if another instance detected, False otherwise
        """
        lock_file = Path("LLM/dashboard/.dashboard.lock")
        
        if not lock_file.exists():
            return False
        
        try:
            # Read PID from lock file
            with open(lock_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process still alive (Unix)
            try:
                os.kill(pid, 0)  # Signal 0 checks existence without killing
                # Process exists
                logger.warning(
                    "Another dashboard instance detected",
                    extra={"pid": pid}
                )
                return True
            except (ProcessLookupError, PermissionError):
                # Process doesn't exist, stale lock file
                logger.info(
                    "Removing stale lock file",
                    extra={"pid": pid}
                )
                lock_file.unlink()
                return False
                
        except (ValueError, OSError) as e:
            # Corrupted lock file, remove it
            logger.warning(
                "Corrupted lock file, removing",
                extra={"error": str(e)}
            )
            lock_file.unlink()
            return False
    
    def create_lock_file(self):
        """
        Create lock file for this dashboard instance.
        
        Achievement 2.3: Multi-instance detection
        """
        lock_file = Path("LLM/dashboard/.dashboard.lock")
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock_file.write_text(str(os.getpid()))
        
        logger.info(
            "Lock file created",
            extra={"pid": os.getpid(), "lock_file": str(lock_file)}
        )
    
    def cleanup_lock_file(self):
        """
        Remove lock file on dashboard exit.
        
        Achievement 2.3: Multi-instance detection
        
        Registered as atexit handler to ensure cleanup.
        """
        lock_file = Path("LLM/dashboard/.dashboard.lock")
        
        if lock_file.exists():
            try:
                # Only remove if it's our PID
                with open(lock_file, 'r') as f:
                    pid = int(f.read().strip())
                
                if pid == os.getpid():
                    lock_file.unlink()
                    logger.info("Lock file cleaned up", extra={"pid": pid})
            except (ValueError, OSError):
                pass  # Ignore cleanup errors
    
    def show_settings(self):
        """
        Show settings menu.
        
        Achievement 3.1: Settings menu
        
        Allows users to:
        - Change theme (default, dark, light)
        - Toggle display options
        - Preview themes before applying
        """
        while True:
            self.clear()
            
            # Load current settings
            settings = self.config.get_all()
            
            # Build menu
            content = Text()
            content.append("⚙️  Dashboard Settings\n\n", style=f"bold {self.get_color('primary')}")
            
            content.append(f"1. Theme: {settings['theme']}\n")
            content.append(f"2. Refresh Interval: {settings['refresh_interval']}s\n")
            content.append(f"3. Show Stats: {settings['show_stats']}\n")
            content.append(f"4. Show Parallel: {settings['show_parallel']}\n")
            content.append(f"5. Auto-Copy Commands: {settings['auto_copy_commands']}\n")
            content.append("\n")
            content.append("6. Back to dashboard\n", style="dim")
            
            panel = Panel(content, border_style=self.get_color("primary"), padding=(1, 2))
            self.console.print(panel)
            
            # Get user choice
            choice = Prompt.ask(
                "\nSelect setting to change (1-6)",
                console=self.console,
                default="6"
            )
            
            if choice == "1":
                self._change_theme()
            elif choice == "2":
                self._change_refresh_interval()
            elif choice == "3":
                self.config.toggle("show_stats")
                self.console.print(f"[{self.get_color('success')}]Toggled show_stats[/{self.get_color('success')}]")
                self.console.print("Press any key to continue...")
                self.get_user_input("")
            elif choice == "4":
                self.config.toggle("show_parallel")
                self.console.print(f"[{self.get_color('success')}]Toggled show_parallel[/{self.get_color('success')}]")
                self.console.print("Press any key to continue...")
                self.get_user_input("")
            elif choice == "5":
                self.config.toggle("auto_copy_commands")
                self.console.print(f"[{self.get_color('success')}]Toggled auto_copy_commands[/{self.get_color('success')}]")
                self.console.print("Press any key to continue...")
                self.get_user_input("")
            elif choice == "6" or choice.lower() in ["b", "back"]:
                break
            else:
                self.console.print(f"[{self.get_color('error')}]Invalid choice[/{self.get_color('error')}]")
                self.console.print("Press any key to continue...")
                self.get_user_input("")
    
    def _change_theme(self):
        """
        Show theme selection menu with preview.
        
        Achievement 3.1: Theme switching
        """
        available_themes = Theme.list_available_themes()
        current_theme = self.config.get("theme", "default")
        
        while True:
            self.clear()
            
            # Show menu
            content = Text()
            content.append("🎨 Select Theme\n\n", style=f"bold {self.get_color('primary')}")
            
            for i, theme_name in enumerate(available_themes, 1):
                if theme_name == current_theme:
                    content.append(f"{i}. {theme_name} (current)\n", style="bold")
                else:
                    content.append(f"{i}. {theme_name}\n")
            
            content.append(f"{len(available_themes) + 1}. Preview theme\n", style="dim")
            content.append(f"{len(available_themes) + 2}. Back\n", style="dim")
            
            panel = Panel(content, border_style=self.get_color("primary"), padding=(1, 2))
            self.console.print(panel)
            
            choice = Prompt.ask(
                f"\nSelect theme (1-{len(available_themes) + 2})",
                console=self.console,
                default=str(len(available_themes) + 2)
            )
            
            try:
                choice_int = int(choice)
                
                if 1 <= choice_int <= len(available_themes):
                    # Apply theme
                    selected_theme = available_themes[choice_int - 1]
                    self.config.set("theme", selected_theme)
                    
                    # Reload theme
                    self.theme = Theme(selected_theme)
                    
                    self.console.print(f"[{self.get_color('success')}]Theme changed to {selected_theme}[/{self.get_color('success')}]")
                    self.console.print("Press any key to continue...")
                    self.get_user_input("")
                    break
                elif choice_int == len(available_themes) + 1:
                    # Preview theme
                    self._preview_themes()
                elif choice_int == len(available_themes) + 2 or choice.lower() in ["b", "back"]:
                    break
                else:
                    self.console.print(f"[{self.get_color('error')}]Invalid choice[/{self.get_color('error')}]")
                    self.console.print("Press any key to continue...")
                    self.get_user_input("")
            except ValueError:
                if choice.lower() in ["b", "back"]:
                    break
                self.console.print(f"[{self.get_color('error')}]Invalid choice[/{self.get_color('error')}]")
                self.console.print("Press any key to continue...")
                self.get_user_input("")
    
    def _preview_themes(self):
        """
        Show theme previews.
        
        Achievement 3.1: Theme preview
        """
        self.clear()
        
        available_themes = Theme.list_available_themes()
        
        for theme_name in available_themes:
            theme = Theme(theme_name)
            preview_panel = theme.preview()
            self.console.print(preview_panel)
            self.console.print()
        
        self.console.print("[dim]Press any key to continue...[/dim]")
        self.get_user_input("")
    
    def _change_refresh_interval(self):
        """
        Change refresh interval setting.
        
        Achievement 3.1: Refresh interval configuration
        """
        self.clear()
        
        current = self.config.get("refresh_interval", 1)
        
        self.console.print(f"Current refresh interval: {current}s\n")
        interval_str = Prompt.ask(
            "Enter new interval in seconds (1-60)",
            console=self.console,
            default=str(current)
        )
        
        try:
            interval = int(interval_str)
            if 1 <= interval <= 60:
                self.config.set("refresh_interval", interval)
                self.console.print(f"[{self.get_color('success')}]Refresh interval set to {interval}s[/{self.get_color('success')}]")
            else:
                self.console.print(f"[{self.get_color('error')}]Value must be between 1 and 60[/{self.get_color('error')}]")
        except ValueError:
            self.console.print(f"[{self.get_color('error')}]Invalid number[/{self.get_color('error')}]")
        
        self.console.print("Press any key to continue...")
        self.get_user_input("")
    
    def render_refresh_footer(self):
        """
        Render footer with refresh indicators.
        
        Achievement 2.3: Refresh indicators
        
        Shows:
        - Last updated timestamp
        - Manual refresh hint ('r' key)
        - Staleness warning if >5 minutes since refresh
        """
        self.console.print()
        
        # Calculate time since last refresh
        now = datetime.now()
        time_diff = now - self.last_refresh_time
        minutes_old = time_diff.total_seconds() / 60
        
        # Build footer text
        footer = Text()
        
        # Last updated timestamp
        timestamp = self.last_refresh_time.strftime('%H:%M:%S')
        footer.append(f"Last updated: {timestamp}", style=self.get_color("dim"))
        
        # Staleness warning if >5 minutes
        if minutes_old > 5:
            footer.append(" | ", style="dim")
            footer.append(f"⚠️  Stale data ({int(minutes_old)}m old)", style=self.get_color("warning"))
        
        # Manual refresh hint
        footer.append(" | ", style="dim")
        footer.append("Press ", style="dim")
        footer.append("'r'", style=f"bold {self.get_color('primary')}")
        footer.append(" to refresh", style="dim")
        
        self.console.print(footer)
