"""
Tests for Theme system (Achievement 3.1).

Tests cover:
- Theme loading
- Color retrieval
- Theme previews
- Invalid theme handling
"""

import pytest
from rich.panel import Panel

from LLM.dashboard.theme import Theme


class TestThemeLoading:
    """Test theme loading functionality."""
    
    def test_default_theme_loads(self):
        """Test that default theme loads successfully."""
        theme = Theme("default")
        assert theme.name == "default"
        assert theme.colors is not None
        assert len(theme.colors) > 0
    
    def test_dark_theme_loads(self):
        """Test that dark theme loads successfully."""
        theme = Theme("dark")
        assert theme.name == "dark"
        assert theme.colors is not None
        assert len(theme.colors) > 0
    
    def test_light_theme_loads(self):
        """Test that light theme loads successfully."""
        theme = Theme("light")
        assert theme.name == "light"
        assert theme.colors is not None
        assert len(theme.colors) > 0
    
    def test_invalid_theme_fallback(self):
        """Test that invalid theme name falls back to default."""
        theme = Theme("nonexistent")
        assert theme.name == "default"
        assert theme.colors == Theme("default").colors
    
    def test_empty_theme_fallback(self):
        """Test that empty theme name falls back to default."""
        theme = Theme("")
        assert theme.name == "default"
    
    def test_theme_has_all_standard_colors(self):
        """Test that theme has all required color keys."""
        theme = Theme("default")
        required_keys = ["primary", "success", "warning", "error", "info", "text", "dim"]
        for key in required_keys:
            assert key in theme.colors, f"Missing color key: {key}"


class TestColorMapping:
    """Test color retrieval functionality."""
    
    def test_get_color_returns_correct_color(self):
        """Test that get_color returns correct color for valid key."""
        theme = Theme("default")
        color = theme.get_color("primary")
        assert color == "cyan"
    
    def test_get_color_with_fallback(self):
        """Test that get_color returns fallback for invalid key."""
        theme = Theme("default")
        color = theme.get_color("nonexistent", fallback="white")
        assert color == "white"
    
    def test_get_color_default_fallback(self):
        """Test that get_color uses default fallback."""
        theme = Theme("default")
        color = theme.get_color("nonexistent")
        assert color == "white"  # Default fallback
    
    def test_different_themes_different_colors(self):
        """Test that different themes have different colors."""
        default_theme = Theme("default")
        dark_theme = Theme("dark")
        
        # Dark theme should have brighter colors
        assert default_theme.get_color("primary") != dark_theme.get_color("primary")
    
    def test_get_all_colors(self):
        """Test get_all_colors returns copy of colors dict."""
        theme = Theme("default")
        colors = theme.get_all_colors()
        
        assert colors == theme.colors
        assert colors is not theme.colors  # Should be a copy


class TestThemePreview:
    """Test theme preview functionality."""
    
    def test_preview_generates_panel(self):
        """Test that preview generates a Rich Panel."""
        theme = Theme("default")
        preview = theme.preview()
        assert isinstance(preview, Panel)
    
    def test_preview_includes_all_colors(self):
        """Test that preview includes all color roles."""
        theme = Theme("default")
        preview = theme.preview()
        
        # Check that preview content is not empty
        assert preview.renderable is not None
    
    def test_preview_has_title(self):
        """Test that preview has proper title."""
        theme = Theme("default")
        preview = theme.preview()
        assert preview.title is not None


class TestThemeUtilities:
    """Test theme utility functions."""
    
    def test_list_available_themes(self):
        """Test that list_available_themes returns all themes."""
        themes = Theme.list_available_themes()
        assert "default" in themes
        assert "dark" in themes
        assert "light" in themes
        assert len(themes) == 3
    
    def test_theme_repr(self):
        """Test theme string representation."""
        theme = Theme("default")
        repr_str = repr(theme)
        assert "Theme" in repr_str
        assert "default" in repr_str


class TestThemeIntegration:
    """Test theme integration scenarios."""
    
    def test_theme_switching(self):
        """Test that theme can be switched dynamically."""
        theme = Theme("default")
        assert theme.name == "default"
        
        # Create new theme
        theme = Theme("dark")
        assert theme.name == "dark"
    
    def test_theme_color_consistency(self):
        """Test that same theme returns consistent colors."""
        theme1 = Theme("default")
        theme2 = Theme("default")
        
        assert theme1.get_color("primary") == theme2.get_color("primary")
        assert theme1.get_color("success") == theme2.get_color("success")

