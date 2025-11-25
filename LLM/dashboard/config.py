"""Dashboard configuration management.

This module provides configuration management for the dashboard, including
loading/saving settings to YAML files, validation, and default values.

Usage:
    config = DashboardConfig()
    theme_name = config.get("theme", "default")
    config.set("theme", "dark")
    config.save()
"""

from pathlib import Path
from typing import Any, Dict, Optional
import yaml


class DashboardConfig:
    """Dashboard configuration manager.
    
    Manages dashboard configuration with YAML persistence, validation,
    and default values. Configuration is stored in LLM/dashboard/config.yaml.
    
    Attributes:
        config_path: Path to configuration file
        config: Dictionary containing current configuration
        defaults: Default configuration values
    """
    
    # Default configuration values
    DEFAULTS = {
        "theme": "default",
        "refresh_interval": 1,
        "show_stats": True,
        "show_parallel": True,
        "auto_copy_commands": True,
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file. If None, uses default
                        location (LLM/dashboard/config.yaml)
        """
        if config_path is None:
            # Default to LLM/dashboard/config.yaml
            config_path = Path(__file__).parent / "config.yaml"
        
        self.config_path = config_path
        self.defaults = self.DEFAULTS.copy()
        self.config = self.load()
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from YAML file.
        
        If file doesn't exist or is invalid, returns default configuration
        and creates the config file with defaults.
        
        Returns:
            Dictionary containing configuration values
        """
        # If config file doesn't exist, create it with defaults
        if not self.config_path.exists():
            self._create_default_config()
            return self.defaults.copy()
        
        try:
            with open(self.config_path, 'r') as f:
                loaded_config = yaml.safe_load(f) or {}
            
            # Merge with defaults (defaults for missing keys)
            config = self.defaults.copy()
            config.update(loaded_config)
            
            # Validate and type-convert
            config = self._validate_config(config)
            
            return config
            
        except (yaml.YAMLError, IOError, OSError) as e:
            # If YAML is invalid, fall back to defaults and recreate file
            print(f"Warning: Invalid configuration file, using defaults: {e}")
            self._create_default_config()
            return self.defaults.copy()
    
    def save(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Save configuration to YAML file.
        
        Args:
            config: Configuration dictionary to save. If None, saves current config.
            
        Returns:
            True if save successful, False otherwise
        """
        if config is not None:
            self.config = self._validate_config(config)
        
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                yaml.safe_dump(
                    self.config,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                )
            
            return True
            
        except (IOError, OSError) as e:
            print(f"Error: Failed to save configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value and save.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
        self.save()
    
    def toggle(self, key: str) -> bool:
        """Toggle boolean configuration value.
        
        Args:
            key: Configuration key (must be boolean value)
            
        Returns:
            New value after toggle
            
        Raises:
            ValueError: If value is not boolean
        """
        current_value = self.config.get(key)
        
        if not isinstance(current_value, bool):
            raise ValueError(f"Cannot toggle non-boolean value: {key}={current_value}")
        
        new_value = not current_value
        self.set(key, new_value)
        return new_value
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values and save."""
        self.config = self.defaults.copy()
        self.save()
    
    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and type-convert configuration values.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            Validated configuration dictionary
        """
        validated = {}
        
        # Validate theme
        theme = config.get("theme", "default")
        if theme not in ["default", "dark", "light"]:
            theme = "default"
        validated["theme"] = theme
        
        # Validate refresh_interval (positive integer)
        try:
            refresh = int(config.get("refresh_interval", 1))
            validated["refresh_interval"] = max(1, min(refresh, 60))  # Clamp to 1-60 seconds
        except (ValueError, TypeError):
            validated["refresh_interval"] = 1
        
        # Validate boolean flags
        for key in ["show_stats", "show_parallel", "auto_copy_commands"]:
            value = config.get(key, True)
            validated[key] = bool(value)
        
        return validated
    
    def _create_default_config(self) -> None:
        """Create default configuration file with comments."""
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write YAML with comments
        with open(self.config_path, 'w') as f:
            f.write("# Dashboard Configuration\n")
            f.write("# This file controls the appearance and behavior of the LLM Dashboard\n\n")
            
            f.write("# Color theme: default, dark, or light\n")
            f.write(f"theme: {self.defaults['theme']}\n\n")
            
            f.write("# Auto-refresh interval in seconds (1-60)\n")
            f.write(f"refresh_interval: {self.defaults['refresh_interval']}\n\n")
            
            f.write("# Show statistics section in dashboard\n")
            f.write(f"show_stats: {str(self.defaults['show_stats']).lower()}\n\n")
            
            f.write("# Show parallel execution opportunities\n")
            f.write(f"show_parallel: {str(self.defaults['show_parallel']).lower()}\n\n")
            
            f.write("# Automatically copy commands to clipboard\n")
            f.write(f"auto_copy_commands: {str(self.defaults['auto_copy_commands']).lower()}\n")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values.
        
        Returns:
            Dictionary of all configuration values
        """
        return self.config.copy()
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return f"DashboardConfig(path='{self.config_path}', settings={len(self.config)})"

