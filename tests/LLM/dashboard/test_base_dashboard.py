"""
Tests for base_dashboard module.

Tests the BaseDashboard abstract class and its methods.
"""

import pytest
from unittest.mock import Mock, MagicMock

from rich.console import Console
from rich.panel import Panel

from LLM.dashboard.base_dashboard import BaseDashboard


class ConcreteDashboard(BaseDashboard):
    """Concrete implementation of BaseDashboard for testing."""

    def show(self):
        """Implementation of abstract show() method."""
        self.print("Dashboard shown")


class TestBaseDashboard:
    """Tests for BaseDashboard class."""

    def test_init_with_console(self):
        """Test initialization with provided Console."""
        mock_console = Mock(spec=Console)
        dashboard = ConcreteDashboard(console=mock_console)

        assert dashboard.console is mock_console

    def test_init_without_console(self):
        """Test initialization creates Console if not provided."""
        dashboard = ConcreteDashboard()

        assert dashboard.console is not None
        assert isinstance(dashboard.console, Console)

    def test_show_must_be_implemented(self):
        """Test that BaseDashboard.show() raises NotImplementedError."""

        # Can't instantiate BaseDashboard directly (it's abstract)
        # Test via incomplete subclass instead
        class IncompleteDashboard(BaseDashboard):
            pass

        mock_console = Mock(spec=Console)

        with pytest.raises(TypeError) as exc_info:
            dashboard = IncompleteDashboard(console=mock_console)

        assert "Can't instantiate abstract class" in str(exc_info.value)

    def test_clear(self):
        """Test clear() calls console.clear()."""
        mock_console = Mock(spec=Console)
        dashboard = ConcreteDashboard(console=mock_console)

        dashboard.clear()

        mock_console.clear.assert_called_once()

    def test_render_panel_basic(self):
        """Test render_panel() creates Panel with basic args."""
        mock_console = Mock(spec=Console)
        dashboard = ConcreteDashboard(console=mock_console)

        panel = dashboard.render_panel("Test content", "Test Title")

        assert isinstance(panel, Panel)
        # Panel content and title are set internally

    def test_render_panel_custom_border(self):
        """Test render_panel() with custom border style."""
        mock_console = Mock(spec=Console)
        dashboard = ConcreteDashboard(console=mock_console)

        panel = dashboard.render_panel("Test content", "Test Title", border_style="green")

        assert isinstance(panel, Panel)

    def test_render_panel_with_kwargs(self):
        """Test render_panel() passes kwargs to Panel."""
        mock_console = Mock(spec=Console)
        dashboard = ConcreteDashboard(console=mock_console)

        panel = dashboard.render_panel("Test content", expand=True, padding=(1, 2))

        assert isinstance(panel, Panel)

    def test_print(self):
        """Test print() delegates to console.print()."""
        mock_console = Mock(spec=Console)
        dashboard = ConcreteDashboard(console=mock_console)

        dashboard.print("Test message")

        mock_console.print.assert_called_once_with("Test message")

    def test_print_with_args(self):
        """Test print() with multiple arguments."""
        mock_console = Mock(spec=Console)
        dashboard = ConcreteDashboard(console=mock_console)

        dashboard.print("Message", 123, style="cyan")

        mock_console.print.assert_called_once_with("Message", 123, style="cyan")

    def test_concrete_dashboard_show(self):
        """Test concrete dashboard show() implementation."""
        mock_console = Mock(spec=Console)
        dashboard = ConcreteDashboard(console=mock_console)

        dashboard.show()

        mock_console.print.assert_called_once_with("Dashboard shown")
