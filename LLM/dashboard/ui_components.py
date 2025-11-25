"""
UI Components Module

Provides reusable UI components for dashboard implementations.

**Components**:
- Panel helpers (info, success, warning, error)
- Table helpers (simple table creation)
- Text formatting (status, headers, colors)
- Prompt wrappers (choice, confirm, text input)
- Status indicators (emojis and constants)

Created: 2025-11-13
Achievement: 0.1 - Rich Dashboard Framework Setup
"""

from typing import List, Optional

from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

# =============================================================================
# Status Indicators (Constants)
# =============================================================================

STATUS_APPROVED = "✅"
STATUS_WARNING = "⚠️"
STATUS_ERROR = "🔴"
STATUS_SUCCESS = "🟢"
STATUS_IN_PROGRESS = "🟡"
STATUS_NOT_STARTED = "⚪"

# =============================================================================
# Panel Helpers
# =============================================================================


def create_panel(content, title: str = "", border_style: str = "blue") -> Panel:
    """
    Create Rich panel with consistent styling.

    Args:
        content: Panel content (Text, str, or renderable)
        title: Panel title
        border_style: Border color (blue, green, red, yellow, etc.)

    Returns:
        Rich Panel object

    **Usage**:
        panel = create_panel("Hello", "Greeting", border_style="green")
        console.print(panel)
    """
    return Panel(content, title=title, border_style=border_style)


def create_info_panel(content, title: str = "Info") -> Panel:
    """
    Create info panel (blue border).

    Args:
        content: Panel content
        title: Panel title (default: "Info")

    Returns:
        Rich Panel with blue border
    """
    return Panel(content, title=title, border_style="blue")


def create_success_panel(content, title: str = "Success") -> Panel:
    """
    Create success panel (green border).

    Args:
        content: Panel content
        title: Panel title (default: "Success")

    Returns:
        Rich Panel with green border
    """
    return Panel(content, title=title, border_style="green")


def create_warning_panel(content, title: str = "Warning") -> Panel:
    """
    Create warning panel (yellow border).

    Args:
        content: Panel content
        title: Panel title (default: "Warning")

    Returns:
        Rich Panel with yellow border
    """
    return Panel(content, title=title, border_style="yellow")


def create_error_panel(content, title: str = "Error") -> Panel:
    """
    Create error panel (red border).

    Args:
        content: Panel content
        title: Panel title (default: "Error")

    Returns:
        Rich Panel with red border
    """
    return Panel(content, title=title, border_style="red")


# =============================================================================
# Table Helpers
# =============================================================================


def create_table(
    title: str = "", show_header: bool = True, header_style: str = "bold cyan"
) -> Table:
    """
    Create Rich table with consistent styling.

    Args:
        title: Table title
        show_header: Whether to show header row
        header_style: Style for header (default: "bold cyan")

    Returns:
        Rich Table object (add columns and rows after creation)

    **Usage**:
        table = create_table("Results")
        table.add_column("Name")
        table.add_column("Status")
        table.add_row("Task 1", "✅")
        console.print(table)
    """
    return Table(title=title, show_header=show_header, header_style=header_style)


def create_simple_table(columns: List[str]) -> Table:
    """
    Create simple table with specified columns.

    Args:
        columns: List of column names

    Returns:
        Rich Table with columns added

    **Usage**:
        table = create_simple_table(["Name", "Status", "Time"])
        table.add_row("Task 1", "✅", "2h")
        console.print(table)
    """
    table = create_table()
    for col in columns:
        table.add_column(col)
    return table


# =============================================================================
# Text Formatting
# =============================================================================


def format_status(status: str, label: str) -> Text:
    """
    Format status with emoji and label.

    Args:
        status: Status type (approved, warning, error, success, in_progress, not_started)
        label: Status label text

    Returns:
        Rich Text object with formatted status

    **Usage**:
        text = format_status('approved', 'Achievement 1.1')
        console.print(text)  # Prints: "✅ Achievement 1.1" in green

    **Available Statuses**:
        - approved: ✅ (green)
        - warning: ⚠️ (yellow)
        - error: 🔴 (red)
        - success: 🟢 (green)
        - in_progress: 🟡 (yellow)
        - not_started: ⚪ (dim)
    """
    status_map = {
        "approved": (STATUS_APPROVED, "green"),
        "warning": (STATUS_WARNING, "yellow"),
        "error": (STATUS_ERROR, "red"),
        "success": (STATUS_SUCCESS, "green"),
        "in_progress": (STATUS_IN_PROGRESS, "yellow"),
        "not_started": (STATUS_NOT_STARTED, "dim"),
    }

    emoji, color = status_map.get(status, (STATUS_NOT_STARTED, "dim"))

    text = Text()
    text.append(f"{emoji} {label}", style=color)
    return text


def format_header(text: str) -> Text:
    """
    Format header text (bold cyan).

    Args:
        text: Header text

    Returns:
        Rich Text object styled as header
    """
    return Text(text, style="bold cyan")


def format_error(text: str) -> Text:
    """
    Format error text (red).

    Args:
        text: Error message

    Returns:
        Rich Text object styled as error
    """
    return Text(text, style="red")


def format_success(text: str) -> Text:
    """
    Format success text (green).

    Args:
        text: Success message

    Returns:
        Rich Text object styled as success
    """
    return Text(text, style="green")


# =============================================================================
# Prompt Wrappers
# =============================================================================


def prompt_choice(message: str, choices: List[str], default: Optional[str] = None) -> str:
    """
    Prompt user for choice from list.

    Args:
        message: Prompt message
        choices: List of valid choices
        default: Default choice (optional)

    Returns:
        User's choice

    **Usage**:
        choice = prompt_choice("Select option", ["1", "2", "3"], default="1")
    """
    return Prompt.ask(message, choices=choices, default=default)


def prompt_confirm(message: str, default: bool = False) -> bool:
    """
    Prompt user for yes/no confirmation.

    Args:
        message: Confirmation message
        default: Default value (True/False)

    Returns:
        User's confirmation (True/False)

    **Usage**:
        if prompt_confirm("Continue?", default=True):
            # User confirmed
            pass
    """
    return Confirm.ask(message, default=default)


def prompt_text(message: str, default: str = "") -> str:
    """
    Prompt user for text input.

    Args:
        message: Prompt message
        default: Default value

    Returns:
        User's input

    **Usage**:
        name = prompt_text("Enter plan name", default="MY-PLAN")
    """
    return Prompt.ask(message, default=default)
