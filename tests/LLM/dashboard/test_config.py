"""
Tests for Dashboard Configuration system (Achievement 3.1).

Tests cover:
- Configuration loading
- Configuration saving
- Validation
- Default values
- File operations
"""

import pytest
from pathlib import Path
import yaml
import tempfile
import os

from LLM.dashboard.config import DashboardConfig


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config_path = Path(f.name)
        yield config_path
    
    # Cleanup
    if config_path.exists():
        config_path.unlink()


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for config files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestConfigLoading:
    """Test configuration loading functionality."""
    
    def test_load_from_nonexistent_file_creates_defaults(self, temp_config_file):
        """Test loading from nonexistent file creates default config."""
        temp_config_file.unlink()  # Ensure it doesn't exist
        config = DashboardConfig(temp_config_file)
        
        assert config.config is not None
        assert config.get("theme") == "default"
        assert config.get("refresh_interval") == 1
        assert config.get("show_stats") is True
    
    def test_load_from_valid_file(self, temp_config_file):
        """Test loading from valid YAML file."""
        # Write valid config
        with open(temp_config_file, 'w') as f:
            yaml.safe_dump({"theme": "dark", "refresh_interval": 5}, f)
        
        config = DashboardConfig(temp_config_file)
        assert config.get("theme") == "dark"
        assert config.get("refresh_interval") == 5
    
    def test_load_with_invalid_yaml(self, temp_config_file):
        """Test loading with invalid YAML falls back to defaults."""
        # Write invalid YAML
        with open(temp_config_file, 'w') as f:
            f.write("invalid: yaml: syntax: error:")
        
        config = DashboardConfig(temp_config_file)
        # Should fall back to defaults
        assert config.get("theme") == "default"
    
    def test_load_merges_with_defaults(self, temp_config_file):
        """Test that loaded config merges with defaults for missing keys."""
        # Write partial config
        with open(temp_config_file, 'w') as f:
            yaml.safe_dump({"theme": "dark"}, f)
        
        config = DashboardConfig(temp_config_file)
        # Should have custom value
        assert config.get("theme") == "dark"
        # Should have default values for missing keys
        assert config.get("refresh_interval") == 1
        assert config.get("show_stats") is True
    
    def test_load_with_empty_file(self, temp_config_file):
        """Test loading from empty file uses defaults."""
        # Write empty file
        temp_config_file.write_text("")
        
        config = DashboardConfig(temp_config_file)
        assert config.get("theme") == "default"


class TestConfigSaving:
    """Test configuration saving functionality."""
    
    def test_save_to_file(self, temp_config_file):
        """Test saving configuration to file."""
        temp_config_file.unlink()  # Start fresh
        
        config = DashboardConfig(temp_config_file)
        config.set("theme", "dark")
        
        # Verify file was created
        assert temp_config_file.exists()
        
        # Verify content
        with open(temp_config_file, 'r') as f:
            saved_config = yaml.safe_load(f)
        assert saved_config["theme"] == "dark"
    
    def test_save_creates_directory(self, temp_config_dir):
        """Test that save creates parent directory if needed."""
        config_path = temp_config_dir / "subdir" / "config.yaml"
        
        config = DashboardConfig(config_path)
        config.save()
        
        assert config_path.exists()
        assert config_path.parent.exists()
    
    def test_save_preserves_values(self, temp_config_file):
        """Test that save preserves all config values."""
        temp_config_file.unlink()
        
        config = DashboardConfig(temp_config_file)
        config.set("theme", "dark")
        config.set("refresh_interval", 10)
        
        # Load in new instance
        config2 = DashboardConfig(temp_config_file)
        assert config2.get("theme") == "dark"
        assert config2.get("refresh_interval") == 10
    
    def test_save_with_custom_config(self, temp_config_file):
        """Test saving with custom config dict."""
        config = DashboardConfig(temp_config_file)
        custom_config = {"theme": "light", "refresh_interval": 5}
        result = config.save(custom_config)
        
        assert result is True
        assert config.get("theme") == "light"


class TestConfigValidation:
    """Test configuration validation."""
    
    def test_validate_theme_valid(self, temp_config_file):
        """Test validation accepts valid themes."""
        config = DashboardConfig(temp_config_file)
        config.set("theme", "dark")
        assert config.get("theme") == "dark"
    
    def test_validate_theme_invalid_fallback(self, temp_config_file):
        """Test validation falls back for invalid theme."""
        # Write invalid theme
        with open(temp_config_file, 'w') as f:
            yaml.safe_dump({"theme": "invalid_theme"}, f)
        
        config = DashboardConfig(temp_config_file)
        # Should fall back to default
        assert config.get("theme") == "default"
    
    def test_validate_refresh_interval_clamp(self, temp_config_file):
        """Test that refresh_interval is clamped to valid range."""
        # Write out-of-range value
        with open(temp_config_file, 'w') as f:
            yaml.safe_dump({"refresh_interval": 100}, f)  # > 60
        
        config = DashboardConfig(temp_config_file)
        # Should be clamped to max
        assert config.get("refresh_interval") <= 60
    
    def test_validate_refresh_interval_minimum(self, temp_config_file):
        """Test that refresh_interval respects minimum."""
        with open(temp_config_file, 'w') as f:
            yaml.safe_dump({"refresh_interval": -5}, f)
        
        config = DashboardConfig(temp_config_file)
        assert config.get("refresh_interval") >= 1
    
    def test_validate_boolean_flags(self, temp_config_file):
        """Test that boolean flags are validated."""
        with open(temp_config_file, 'w') as f:
            yaml.safe_dump({"show_stats": "yes"}, f)  # String instead of bool
        
        config = DashboardConfig(temp_config_file)
        # Should convert to bool
        assert isinstance(config.get("show_stats"), bool)


class TestConfigAccess:
    """Test configuration access methods."""
    
    def test_get_with_existing_key(self, temp_config_file):
        """Test get() with existing key."""
        config = DashboardConfig(temp_config_file)
        value = config.get("theme")
        assert value is not None
    
    def test_get_with_missing_key_returns_default(self, temp_config_file):
        """Test get() with missing key returns default."""
        config = DashboardConfig(temp_config_file)
        value = config.get("nonexistent_key", "default_value")
        assert value == "default_value"
    
    def test_set_updates_value(self, temp_config_file):
        """Test set() updates value."""
        config = DashboardConfig(temp_config_file)
        config.set("theme", "dark")
        assert config.get("theme") == "dark"
    
    def test_set_saves_automatically(self, temp_config_file):
        """Test that set() saves to file automatically."""
        temp_config_file.unlink()
        
        config = DashboardConfig(temp_config_file)
        config.set("theme", "dark")
        
        # Verify file was updated
        with open(temp_config_file, 'r') as f:
            saved_config = yaml.safe_load(f)
        assert saved_config["theme"] == "dark"
    
    def test_toggle_boolean_value(self, temp_config_file):
        """Test toggle() flips boolean value."""
        config = DashboardConfig(temp_config_file)
        original = config.get("show_stats")
        new_value = config.toggle("show_stats")
        
        assert new_value == (not original)
        assert config.get("show_stats") == new_value
    
    def test_toggle_non_boolean_raises_error(self, temp_config_file):
        """Test toggle() raises error for non-boolean value."""
        config = DashboardConfig(temp_config_file)
        with pytest.raises(ValueError):
            config.toggle("theme")  # String value, not boolean
    
    def test_get_all_returns_copy(self, temp_config_file):
        """Test get_all() returns copy of config."""
        config = DashboardConfig(temp_config_file)
        all_config = config.get_all()
        
        # Modify returned dict
        all_config["theme"] = "modified"
        
        # Original should be unchanged
        assert config.get("theme") != "modified"
    
    def test_reset_to_defaults(self, temp_config_file):
        """Test reset_to_defaults() restores default values."""
        config = DashboardConfig(temp_config_file)
        config.set("theme", "dark")
        config.set("refresh_interval", 10)
        
        config.reset_to_defaults()
        
        assert config.get("theme") == "default"
        assert config.get("refresh_interval") == 1


class TestConfigIntegration:
    """Test configuration integration scenarios."""
    
    def test_config_persistence_across_instances(self, temp_config_file):
        """Test that config persists across multiple instances."""
        # Create first instance and set value
        config1 = DashboardConfig(temp_config_file)
        config1.set("theme", "dark")
        
        # Create second instance and verify
        config2 = DashboardConfig(temp_config_file)
        assert config2.get("theme") == "dark"
    
    def test_config_repr(self, temp_config_file):
        """Test config string representation."""
        config = DashboardConfig(temp_config_file)
        repr_str = repr(config)
        assert "DashboardConfig" in repr_str

