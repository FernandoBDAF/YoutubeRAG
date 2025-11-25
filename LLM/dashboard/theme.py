"""Dashboard theme system for color customization.

This module provides a simple theme system that allows users to customize
dashboard colors. It includes three built-in themes: default, dark, and light.

Usage:
    theme = Theme("dark")
    primary_color = theme.get_color("primary")
    preview_panel = theme.preview()
"""

from typing import Dict
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class Theme:
    """Dashboard color theme.
    
    Provides color mappings for dashboard UI elements with support for
    three built-in themes: default, dark, and light.
    
    Attributes:
        name: Theme name (default, dark, or light)
        colors: Dictionary mapping color roles to Rich color codes
    """
    
    def __init__(self, name: str = "default"):
        """Initialize theme with specified name.
        
        Args:
            name: Theme name. Must be one of: default, dark, light.
                  Falls back to "default" if invalid name provided.
        """
        self.name = name if name in ["default", "dark", "light"] else "default"
        self.colors = self._load_colors()
    
    def _load_colors(self) -> Dict[str, str]:
        """Load theme colors based on theme name.
        
        Returns:
            Dictionary mapping semantic color names to Rich color codes.
            Keys: primary, success, warning, error, info, text, dim
        """
        themes = {
            "default": {
                "primary": "cyan",
                "success": "green",
                "warning": "yellow",
                "error": "red",
                "info": "blue",
                "text": "white",
                "dim": "dim cyan",
            },
            "dark": {
                "primary": "bright_cyan",
                "success": "bright_green",
                "warning": "bright_yellow",
                "error": "bright_red",
                "info": "bright_blue",
                "text": "bright_white",
                "dim": "cyan",
            },
            "light": {
                "primary": "blue",
                "success": "green",
                "warning": "yellow",
                "error": "red",
                "info": "cyan",
                "text": "black",
                "dim": "blue",
            }
        }
        return themes.get(self.name, themes["default"])
    
    def get_color(self, color_name: str, fallback: str = "white") -> str:
        """Get Rich color code for semantic color name.
        
        Args:
            color_name: Semantic color name (primary, success, warning, error, info, text, dim)
            fallback: Fallback color if color_name not found
            
        Returns:
            Rich color code string (e.g., "cyan", "bright_green")
        """
        return self.colors.get(color_name, fallback)
    
    def preview(self) -> Panel:
        """Generate a preview panel showing all theme colors.
        
        Returns:
            Rich Panel with color samples and labels
        """
        table = Table(show_header=True, header_style="bold", box=None)
        table.add_column("Color Role", style="white")
        table.add_column("Sample", justify="center")
        table.add_column("Code", style="dim")
        
        # Add row for each color
        for role, color in self.colors.items():
            # Create sample text with the color
            sample = Text("●●●", style=color)
            table.add_row(role.capitalize(), sample, f"[{color}]")
        
        panel = Panel(
            table,
            title=f"[bold {self.colors['primary']}]Theme: {self.name.capitalize()}[/]",
            border_style=self.colors["primary"],
            padding=(1, 2),
        )
        
        return panel
    
    def get_all_colors(self) -> Dict[str, str]:
        """Get all colors in the theme.
        
        Returns:
            Dictionary of all color mappings
        """
        return self.colors.copy()
    
    @staticmethod
    def list_available_themes() -> list[str]:
        """List all available theme names.
        
        Returns:
            List of available theme names
        """
        return ["default", "dark", "light"]
    
    def __repr__(self) -> str:
        """String representation of theme."""
        return f"Theme(name='{self.name}', colors={len(self.colors)})"

