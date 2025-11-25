"""
Action executor for dashboard operations.

Executes user actions by building and running commands for common
workflow operations.
"""

import subprocess
from pathlib import Path
from typing import List
from rich.console import Console

from core.libraries.logging import get_logger

logger = get_logger(__name__)


class ActionExecutor:
    """
    Execute user actions from dashboard.

    Handles:
    - Command building for common operations
    - Subprocess execution
    - Error handling and reporting

    Example:
        >>> executor = ActionExecutor(plan_path, console)
        >>> executor.execute_next()
    """

    def __init__(self, plan_path: Path, console: Console):
        """
        Initialize action executor.

        Args:
            plan_path: Path to plan directory
            console: Rich Console instance for output
        """
        self.plan_path = plan_path
        self.console = console
        self.plan_name = plan_path.name

        logger.info(
            "Action executor initialized",
            extra={"plan_name": self.plan_name, "plan_path": str(plan_path)},
        )

    def execute_next(self):
        """
        Execute next achievement.

        Builds and runs:
            python LLM/scripts/generation/generate_prompt.py @PLAN --next --interactive
        """
        cmd = [
            "python",
            "LLM/scripts/generation/generate_prompt.py",
            f"@{self.plan_name}",
            "--next",
            "--interactive",
        ]

        logger.info(
            "Executing next achievement",
            extra={"plan_name": self.plan_name, "command": " ".join(cmd)},
        )

        self._run_command(cmd, "Execute Next")

    def create_subplan(self, achievement: str):
        """
        Create SUBPLAN for achievement.

        Args:
            achievement: Achievement number (e.g., "1.2")

        Builds and runs:
            python LLM/scripts/generation/generate_subplan_prompt.py @PLAN --achievement X.Y
        """
        cmd = [
            "python",
            "LLM/scripts/generation/generate_subplan_prompt.py",
            f"@{self.plan_name}",
            "--achievement",
            achievement,
        ]

        logger.info(
            "Creating SUBPLAN",
            extra={
                "plan_name": self.plan_name,
                "achievement": achievement,
                "command": " ".join(cmd),
            },
        )

        self._run_command(cmd, f"Create SUBPLAN for {achievement}")

    def create_execution(self, achievement: str):
        """
        Create EXECUTION for achievement.

        Args:
            achievement: Achievement number (e.g., "1.2")

        Builds and runs:
            python LLM/scripts/generation/generate_execution_prompt.py @PLAN --achievement X.Y
        """
        cmd = [
            "python",
            "LLM/scripts/generation/generate_execution_prompt.py",
            f"@{self.plan_name}",
            "--achievement",
            achievement,
        ]

        logger.info(
            "Creating EXECUTION",
            extra={
                "plan_name": self.plan_name,
                "achievement": achievement,
                "command": " ".join(cmd),
            },
        )

        self._run_command(cmd, f"Create EXECUTION for {achievement}")

    def _run_command(self, cmd: List[str], action_name: str):
        """
        Run command with error handling.

        Args:
            cmd: Command list (e.g., ["python", "script.py", "--flag"])
            action_name: Human-readable action name for logging
        """
        try:
            logger.debug("Running command", extra={"action": action_name, "command": " ".join(cmd)})

            result = subprocess.run(cmd, check=True, capture_output=False)

            self.console.print(f"\n[green]✅ {action_name} completed[/green]")

            logger.info(
                "Command completed successfully",
                extra={"action": action_name, "exit_code": result.returncode},
            )

        except subprocess.CalledProcessError as e:
            self.console.print(f"\n[red]❌ {action_name} failed: {e}[/red]")

            logger.error(
                "Command failed",
                exc_info=True,
                extra={"action": action_name, "exit_code": e.returncode},
            )

        except FileNotFoundError:
            self.console.print(f"\n[red]❌ Command not found[/red]")
            self.console.print("[yellow]Tip: Ensure you're running from project root[/yellow]")

            logger.error(
                "Command not found",
                extra={"action": action_name, "command": cmd[0] if cmd else "unknown"},
            )

        # Pause for user to see result
        self.console.print("\nPress any key to continue...")
        input()
