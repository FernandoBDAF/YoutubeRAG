"""
Dashboard-specific exceptions.

All dashboard exceptions inherit from ApplicationError for consistency
with the broader LLM methodology system.
"""

from LLM.scripts.generation.exceptions import ApplicationError


class DashboardError(ApplicationError):
    """
    Base exception for all dashboard errors.

    Provides structured error handling with context and suggestions
    for all dashboard-related operations.
    """

    pass


class PlanLoadError(DashboardError):
    """
    Raised when a plan cannot be loaded.

    Context fields:
    - plan_path: Path to the plan that failed to load
    - plan_dir: Plan directory path
    - reason: Specific reason for failure

    Suggestions:
    - Verify plan directory exists
    - Check for PLAN_*.md file in directory
    - Ensure proper file permissions
    - Verify workspace structure
    """

    pass


class StateDetectionError(DashboardError):
    """
    Raised when state detection fails.

    Context fields:
    - plan_dir: Plan directory being analyzed
    - detector: State detector that failed
    - reason: Specific reason for failure

    Suggestions:
    - Verify plan structure is valid
    - Check for required state files
    - Ensure file permissions are correct
    - Review plan directory contents
    """

    pass


class ActionExecutionError(DashboardError):
    """
    Raised when a dashboard action fails to execute.

    Context fields:
    - action: Action that was attempted
    - plan: Plan being operated on (if applicable)
    - reason: Specific reason for failure

    Suggestions:
    - Verify action is valid for current state
    - Check dependencies are met
    - Review error details above
    - Try alternative action
    """

    pass


class InvalidUserInputError(DashboardError):
    """
    Raised when user provides invalid input.

    Context fields:
    - input: User's input
    - expected: Expected input format
    - available_options: List of valid options

    Suggestions:
    - Review available options
    - Check input format
    - Try again with valid input
    """

    pass
