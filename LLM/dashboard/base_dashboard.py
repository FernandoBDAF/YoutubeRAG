"""
Base Dashboard Module

Provides the abstract base class for all dashboard implementations.

**Design Philosophy**:
- Abstract base class enforces consistent interface
- Optional Console parameter for dependency injection (testability)
- Core methods for screen management and rendering
- Subclasses must implement show() method

Created: 2025-11-13
Achievement: 0.1 - Rich Dashboard Framework Setup
"""

from abc import ABC, abstractmethod
from typing import Optional

from rich.console import Console
from rich.panel import Panel

from LLM.dashboard.theme import Theme
from LLM.dashboard.config import DashboardConfig


class BaseDashboard(ABC):
    """
    Abstract base class for all dashboard implementations.

    Provides core functionality for:
    - Console management (Rich Console instance)
    - Screen clearing
    - Panel rendering with consistent styling
    - Common UI patterns

    **Subclasses must implement**:
    - `show()`: Main dashboard display logic

    **Usage**:
        class MyDashboard(BaseDashboard):
            def show(self):
                self.clear()
                panel = self.render_panel("Hello Dashboard", "My Dashboard")
                self.print(panel)

    **Design Decisions**:
    - Optional Console parameter enables dependency injection for testing
    - Wrapper methods (print, clear) provide consistent interface
    - Panel rendering uses Rich library primitives
    """

    def __init__(self, console: Optional[Console] = None):
        """
        Initialize dashboard with Rich Console.

        Args:
            console: Rich Console instance. If None, creates new Console.
                     Optional parameter enables mocking in tests.
        """
        self.console = console or Console()
        self.config = DashboardConfig()
        self.theme = Theme(self.config.get("theme", "default"))

    def get_color(self, color_name: str, fallback: str = "white") -> str:
        """
        Get theme color for semantic color name.
        
        Utility method to retrieve colors from the current theme.
        
        Args:
            color_name: Semantic color name (primary, success, warning, error, info, text, dim)
            fallback: Fallback color if color_name not found
            
        Returns:
            Rich color code string
            
        **Usage**:
            color = self.get_color("primary")  # Returns "cyan" for default theme
            panel = Panel(content, border_style=self.get_color("success"))
        """
        return self.theme.get_color(color_name, fallback)

    @abstractmethod
    def show(self):
        """
        Show dashboard (must be implemented by subclasses).

        This method should contain the main dashboard logic:
        - Clear screen (optional)
        - Render UI components
        - Handle user input
        - Update state

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement show() method")

    def clear(self):
        """
        Clear console screen.

        Uses Rich Console clear() to reset terminal display.
        Useful before rendering dashboard to avoid scroll clutter.

        **Usage**:
            def show(self):
                self.clear()  # Clear before rendering
                # ... render dashboard ...
        """
        self.console.clear()

    def render_panel(self, content, title: str = "", border_style: Optional[str] = None, **kwargs) -> Panel:
        """
        Render Rich panel with consistent styling.

        Creates a Rich Panel with specified content, title, and border style.
        Additional kwargs are passed directly to Panel constructor.

        Args:
            content: Panel content (Text, str, or any Rich renderable)
            title: Panel title (displayed at top)
            border_style: Border color. If None, uses theme's primary color.
            **kwargs: Additional arguments passed to Rich Panel (e.g., expand, padding)

        Returns:
            Rich Panel object ready for printing

        **Usage**:
            panel = self.render_panel("Status: OK", "System Status", border_style="green")
            self.print(panel)

        **Available Border Styles**:
            - None (uses theme primary color - default)
            - green (success)
            - red (error)
            - yellow (warning)
            - cyan (info)
            - magenta (special)
        """
        if border_style is None:
            border_style = self.get_color("primary")
        return Panel(content, title=title, border_style=border_style, **kwargs)

    def print(self, *args, **kwargs):
        """
        Wrapper for console.print().

        Delegates to Rich Console print() method with all arguments.
        Provides consistent interface for printing to console.

        Args:
            *args: Positional arguments passed to Console.print()
            **kwargs: Keyword arguments passed to Console.print()

        **Usage**:
            self.print("[green]Success![/green]")
            self.print(panel)
            self.print("Value:", value, style="cyan")
        """
        self.console.print(*args, **kwargs)
