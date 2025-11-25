"""
Tests for ui_components module.

Tests UI component creation functions, text formatting, and prompts.
"""
import pytest
from unittest.mock import Mock, patch

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from LLM.dashboard.ui_components import (
    # Status constants
    STATUS_APPROVED, STATUS_WARNING, STATUS_ERROR,
    STATUS_SUCCESS, STATUS_IN_PROGRESS, STATUS_NOT_STARTED,
    # Panel helpers
    create_panel, create_info_panel, create_success_panel,
    create_warning_panel, create_error_panel,
    # Table helpers
    create_table, create_simple_table,
    # Text formatting
    format_status, format_header, format_error, format_success,
    # Prompt wrappers
    prompt_choice, prompt_confirm, prompt_text
)


class TestStatusConstants:
    """Tests for status indicator constants."""
    
    def test_status_constants_defined(self):
        """Test that all status constants are defined."""
        assert STATUS_APPROVED == "✅"
        assert STATUS_WARNING == "⚠️"
        assert STATUS_ERROR == "🔴"
        assert STATUS_SUCCESS == "🟢"
        assert STATUS_IN_PROGRESS == "🟡"
        assert STATUS_NOT_STARTED == "⚪"


class TestPanelHelpers:
    """Tests for panel creation helpers."""
    
    def test_create_panel_basic(self):
        """Test basic panel creation."""
        panel = create_panel("Test content", "Test Title")
        
        assert isinstance(panel, Panel)
    
    def test_create_panel_custom_border(self):
        """Test panel with custom border style."""
        panel = create_panel("Content", "Title", border_style="green")
        
        assert isinstance(panel, Panel)
    
    def test_create_info_panel(self):
        """Test info panel creation (blue border)."""
        panel = create_info_panel("Info message")
        
        assert isinstance(panel, Panel)
    
    def test_create_info_panel_custom_title(self):
        """Test info panel with custom title."""
        panel = create_info_panel("Info message", title="Custom Info")
        
        assert isinstance(panel, Panel)
    
    def test_create_success_panel(self):
        """Test success panel creation (green border)."""
        panel = create_success_panel("Success message")
        
        assert isinstance(panel, Panel)
    
    def test_create_warning_panel(self):
        """Test warning panel creation (yellow border)."""
        panel = create_warning_panel("Warning message")
        
        assert isinstance(panel, Panel)
    
    def test_create_error_panel(self):
        """Test error panel creation (red border)."""
        panel = create_error_panel("Error message")
        
        assert isinstance(panel, Panel)


class TestTableHelpers:
    """Tests for table creation helpers."""
    
    def test_create_table_basic(self):
        """Test basic table creation."""
        table = create_table("Test Table")
        
        assert isinstance(table, Table)
    
    def test_create_table_no_header(self):
        """Test table without header."""
        table = create_table(show_header=False)
        
        assert isinstance(table, Table)
    
    def test_create_simple_table(self):
        """Test simple table with columns."""
        columns = ["Name", "Status", "Time"]
        table = create_simple_table(columns)
        
        assert isinstance(table, Table)
        # Verify columns were added (Rich Table has columns attribute)
        assert len(table.columns) == 3


class TestTextFormatting:
    """Tests for text formatting functions."""
    
    def test_format_status_approved(self):
        """Test approved status formatting."""
        text = format_status('approved', 'Test Label')
        
        assert isinstance(text, Text)
        assert "✅" in str(text)
        assert "Test Label" in str(text)
    
    def test_format_status_warning(self):
        """Test warning status formatting."""
        text = format_status('warning', 'Warning Label')
        
        assert isinstance(text, Text)
        assert "⚠️" in str(text)
    
    def test_format_status_error(self):
        """Test error status formatting."""
        text = format_status('error', 'Error Label')
        
        assert isinstance(text, Text)
        assert "🔴" in str(text)
    
    def test_format_status_success(self):
        """Test success status formatting."""
        text = format_status('success', 'Success Label')
        
        assert isinstance(text, Text)
        assert "🟢" in str(text)
    
    def test_format_status_in_progress(self):
        """Test in_progress status formatting."""
        text = format_status('in_progress', 'In Progress Label')
        
        assert isinstance(text, Text)
        assert "🟡" in str(text)
    
    def test_format_status_not_started(self):
        """Test not_started status formatting."""
        text = format_status('not_started', 'Not Started Label')
        
        assert isinstance(text, Text)
        assert "⚪" in str(text)
    
    def test_format_status_unknown(self):
        """Test unknown status defaults to not_started."""
        text = format_status('unknown_status', 'Unknown Label')
        
        assert isinstance(text, Text)
        assert "⚪" in str(text)
    
    def test_format_header(self):
        """Test header text formatting."""
        text = format_header("Header Text")
        
        assert isinstance(text, Text)
        assert "Header Text" in str(text)
    
    def test_format_error(self):
        """Test error text formatting."""
        text = format_error("Error message")
        
        assert isinstance(text, Text)
        assert "Error message" in str(text)
    
    def test_format_success(self):
        """Test success text formatting."""
        text = format_success("Success message")
        
        assert isinstance(text, Text)
        assert "Success message" in str(text)


class TestPromptWrappers:
    """Tests for prompt wrapper functions."""
    
    @patch('LLM.dashboard.ui_components.Prompt.ask')
    def test_prompt_choice(self, mock_ask):
        """Test prompt_choice() calls Prompt.ask with choices."""
        mock_ask.return_value = "1"
        
        result = prompt_choice("Select option", ["1", "2", "3"])
        
        mock_ask.assert_called_once_with("Select option", choices=["1", "2", "3"], default=None)
        assert result == "1"
    
    @patch('LLM.dashboard.ui_components.Prompt.ask')
    def test_prompt_choice_with_default(self, mock_ask):
        """Test prompt_choice() with default value."""
        mock_ask.return_value = "2"
        
        result = prompt_choice("Select option", ["1", "2", "3"], default="2")
        
        mock_ask.assert_called_once_with("Select option", choices=["1", "2", "3"], default="2")
        assert result == "2"
    
    @patch('LLM.dashboard.ui_components.Confirm.ask')
    def test_prompt_confirm(self, mock_ask):
        """Test prompt_confirm() calls Confirm.ask."""
        mock_ask.return_value = True
        
        result = prompt_confirm("Continue?")
        
        mock_ask.assert_called_once_with("Continue?", default=False)
        assert result is True
    
    @patch('LLM.dashboard.ui_components.Confirm.ask')
    def test_prompt_confirm_with_default(self, mock_ask):
        """Test prompt_confirm() with default value."""
        mock_ask.return_value = False
        
        result = prompt_confirm("Continue?", default=True)
        
        mock_ask.assert_called_once_with("Continue?", default=True)
        assert result is False
    
    @patch('LLM.dashboard.ui_components.Prompt.ask')
    def test_prompt_text(self, mock_ask):
        """Test prompt_text() calls Prompt.ask."""
        mock_ask.return_value = "user input"
        
        result = prompt_text("Enter name")
        
        mock_ask.assert_called_once_with("Enter name", default="")
        assert result == "user input"
    
    @patch('LLM.dashboard.ui_components.Prompt.ask')
    def test_prompt_text_with_default(self, mock_ask):
        """Test prompt_text() with default value."""
        mock_ask.return_value = "MY-PLAN"
        
        result = prompt_text("Enter plan name", default="MY-PLAN")
        
        mock_ask.assert_called_once_with("Enter plan name", default="MY-PLAN")
        assert result == "MY-PLAN"

