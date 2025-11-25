"""
Custom exceptions for prompt generation scripts.

Domain-specific exceptions that extend core.libraries.error_handling.ApplicationError
with tailored error messages, context, and actionable suggestions for prompt generation
workflows.

Usage:
    from LLM.scripts.generation.exceptions import PlanNotFoundError

    raise PlanNotFoundError(
        plan_name="FEATURE-NAME",
        searched_paths=[Path("work-space/plans/FEATURE-NAME")],
        available_plans=["PLAN-A", "PLAN-B"]
    )
"""

from pathlib import Path
from typing import List, Optional
from core.libraries.error_handling import ApplicationError


class PlanNotFoundError(ApplicationError):
    """Raised when a PLAN file cannot be found.

    Provides actionable suggestions for finding the correct PLAN file.
    """

    def __init__(
        self,
        plan_name: str,
        searched_paths: Optional[List[Path]] = None,
        available_plans: Optional[List[str]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize PlanNotFoundError with helpful context.

        Args:
            plan_name: Name of the PLAN that wasn't found
            searched_paths: List of paths that were searched
            available_plans: List of available PLAN names
            cause: Original exception if any
        """
        context = {
            "plan_name": plan_name,
            "searched_paths": [str(p) for p in (searched_paths or [])],
        }

        message = f"PLAN file not found: {plan_name}"

        suggestions = [
            f"Check if file exists: ls work-space/plans/{plan_name}/",
            f"Use @folder shortcut: @{plan_name}",
            "See available plans: ls work-space/plans/",
        ]

        if available_plans:
            context["available_plans"] = available_plans
            suggestions.append("\nAvailable plans:")
            for plan in available_plans:
                suggestions.append(f"  - @{plan}")

        context["suggestions"] = suggestions

        super().__init__(message, context=context, cause=cause)


class AchievementNotFoundError(ApplicationError):
    """Raised when an achievement cannot be found in a PLAN.

    Provides suggestions for finding valid achievements.
    """

    def __init__(
        self,
        achievement_num: str,
        plan_name: str,
        available_achievements: Optional[List[str]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize AchievementNotFoundError with helpful context.

        Args:
            achievement_num: Achievement number that wasn't found (e.g., "2.1")
            plan_name: Name of the PLAN that was searched
            available_achievements: List of available achievement numbers
            cause: Original exception if any
        """
        context = {
            "achievement_num": achievement_num,
            "plan_name": plan_name,
        }

        message = f"Achievement {achievement_num} not found in PLAN {plan_name}"

        suggestions = [
            f"Check achievement exists: grep 'Achievement {achievement_num}' work-space/plans/{plan_name}/PLAN_*.md",
            f"Use correct format: X.Y (e.g., 2.1, 3.5)",
            "List achievements: grep '^\\*\\*Achievement' PLAN_FILE.md",
        ]

        if available_achievements:
            context["available_achievements"] = available_achievements
            suggestions.append("\nAvailable achievements in this PLAN:")
            for ach in available_achievements[:10]:  # Limit to first 10
                suggestions.append(f"  - {ach}")
            if len(available_achievements) > 10:
                suggestions.append(f"  ... and {len(available_achievements) - 10} more")

        context["suggestions"] = suggestions

        super().__init__(message, context=context, cause=cause)


class SubplanNotFoundError(ApplicationError):
    """Raised when a SUBPLAN file cannot be found.

    Provides suggestions for finding or creating SUBPLANs.
    """

    def __init__(
        self,
        achievement_num: str,
        plan_name: str,
        expected_path: Optional[Path] = None,
        available_subplans: Optional[List[str]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize SubplanNotFoundError with helpful context.

        Args:
            achievement_num: Achievement number for the SUBPLAN
            plan_name: Name of the parent PLAN
            expected_path: Expected path where SUBPLAN should be
            available_subplans: List of available SUBPLAN files
            cause: Original exception if any
        """
        context = {
            "achievement_num": achievement_num,
            "plan_name": plan_name,
        }

        if expected_path:
            context["expected_path"] = str(expected_path)
            message = f"SUBPLAN not found for Achievement {achievement_num}: {expected_path}"
        else:
            message = f"SUBPLAN not found for Achievement {achievement_num}"

        suggestions = [
            f"Create SUBPLAN: python -m LLM.scripts.generation.generate_subplan_prompt @{plan_name} --achievement {achievement_num}",
            f"Check existing SUBPLANs: ls work-space/plans/{plan_name}/subplans/",
            "Use correct naming: SUBPLAN_PLANNAME_XX.md (e.g., SUBPLAN_FEATURE_21.md)",
        ]

        if available_subplans:
            context["available_subplans"] = available_subplans
            suggestions.append("\nAvailable SUBPLANs:")
            for subplan in available_subplans[:5]:  # Limit to first 5
                suggestions.append(f"  - {subplan}")
            if len(available_subplans) > 5:
                suggestions.append(f"  ... and {len(available_subplans) - 5} more")

        context["suggestions"] = suggestions

        super().__init__(message, context=context, cause=cause)


class InvalidAchievementFormatError(ApplicationError):
    """Raised when an achievement number has invalid format.

    Provides examples of correct formats.
    """

    def __init__(
        self,
        achievement_input: str,
        expected_format: str = "X.Y",
        cause: Optional[Exception] = None,
    ):
        """Initialize InvalidAchievementFormatError with helpful context.

        Args:
            achievement_input: The invalid achievement input
            expected_format: Expected format description
            cause: Original exception if any
        """
        context = {
            "achievement_input": achievement_input,
            "expected_format": expected_format,
        }

        message = f"Invalid achievement format: '{achievement_input}'"

        suggestions = [
            f"Use correct format: {expected_format}",
            "Valid examples: 1.1, 2.5, 3.10",
            "Must be: number.number (e.g., 2.1, not 2 or 2.1.3)",
        ]

        context["suggestions"] = suggestions

        super().__init__(message, context=context, cause=cause)


class ExecutionTaskNotFoundError(ApplicationError):
    """Raised when an EXECUTION_TASK file cannot be found.

    Provides suggestions for finding or creating EXECUTION_TASKs.
    """

    def __init__(
        self,
        achievement_num: str,
        execution_num: str,
        plan_name: str,
        expected_path: Optional[Path] = None,
        available_tasks: Optional[List[str]] = None,
        cause: Optional[Exception] = None,
    ):
        """Initialize ExecutionTaskNotFoundError with helpful context.

        Args:
            achievement_num: Achievement number
            execution_num: Execution number (e.g., "01")
            plan_name: Name of the parent PLAN
            expected_path: Expected path where EXECUTION_TASK should be
            available_tasks: List of available EXECUTION_TASK files
            cause: Original exception if any
        """
        context = {
            "achievement_num": achievement_num,
            "execution_num": execution_num,
            "plan_name": plan_name,
        }

        if expected_path:
            context["expected_path"] = str(expected_path)
            message = f"EXECUTION_TASK not found: {expected_path}"
        else:
            message = f"EXECUTION_TASK not found for Achievement {achievement_num}, Execution {execution_num}"

        suggestions = [
            f"Check if SUBPLAN exists first: ls work-space/plans/{plan_name}/subplans/",
            f"List EXECUTION_TASKs: ls work-space/plans/{plan_name}/execution/EXECUTION_TASK_*",
            "Use correct naming: EXECUTION_TASK_PLANNAME_XX_YY.md",
        ]

        if available_tasks:
            context["available_tasks"] = available_tasks
            suggestions.append("\nAvailable EXECUTION_TASKs:")
            for task in available_tasks[:5]:
                suggestions.append(f"  - {task}")
            if len(available_tasks) > 5:
                suggestions.append(f"  ... and {len(available_tasks) - 5} more")

        context["suggestions"] = suggestions

        super().__init__(message, context=context, cause=cause)


class InvalidPathError(ApplicationError):
    """Raised when a path is invalid or inaccessible.

    Provides suggestions for fixing path issues.
    """

    def __init__(
        self, path: Path, reason: str, path_type: str = "file", cause: Optional[Exception] = None
    ):
        """Initialize InvalidPathError with helpful context.

        Args:
            path: The invalid path
            reason: Why the path is invalid
            path_type: Type of path (file, directory, etc.)
            cause: Original exception if any
        """
        context = {
            "path": str(path),
            "reason": reason,
            "path_type": path_type,
        }

        message = f"Invalid {path_type} path: {path} ({reason})"

        suggestions = [
            (
                f"Check if {path_type} exists: ls {path.parent}/"
                if path.parent
                else f"Check if {path_type} exists"
            ),
            "Use absolute path or relative from workspace root",
            "Check permissions: ls -la",
        ]

        context["suggestions"] = suggestions

        super().__init__(message, context=context, cause=cause)


def format_error_with_suggestions(error: ApplicationError, use_colors: bool = True) -> str:
    """Format an ApplicationError with nice formatting for terminal output.

    Achievement 3.1: Added color coding for better readability.

    Args:
        error: The ApplicationError to format
        use_colors: Whether to use ANSI color codes (default: True)

    Returns:
        Formatted string with error message and suggestions
    """
    # ANSI color codes (Achievement 3.1: Color-coded output)
    if use_colors:
        RED = "\033[91m"
        YELLOW = "\033[93m"
        GREEN = "\033[92m"
        BLUE = "\033[94m"
        BOLD = "\033[1m"
        RESET = "\033[0m"
    else:
        RED = YELLOW = GREEN = BLUE = BOLD = RESET = ""

    lines = [
        f"{RED}{BOLD}❌ ERROR:{RESET} {RED}{error.message}{RESET}",
        "",
    ]

    # Add context details
    if error.context:
        # Filter out suggestions from context display
        display_context = {k: v for k, v in error.context.items() if k != "suggestions"}
        if display_context:
            lines.append(f"{BLUE}Details:{RESET}")
            for key, value in display_context.items():
                if key not in ["suggestions"]:
                    lines.append(f"  {key}: {value}")
            lines.append("")

    # Add suggestions
    if "suggestions" in error.context:
        lines.append(f"{YELLOW}{BOLD}HOW TO FIX:{RESET}")
        suggestions = error.context["suggestions"]
        for i, suggestion in enumerate(suggestions, 1):
            if suggestion.startswith("\n"):
                lines.append(f"{YELLOW}{suggestion[1:]}{RESET}")  # Remove leading newline
            elif suggestion.startswith("  -"):
                lines.append(f"{YELLOW}{suggestion}{RESET}")  # Already indented
            else:
                lines.append(f"{YELLOW}{i}. {suggestion}{RESET}")
        lines.append("")

    return "\n".join(lines)
