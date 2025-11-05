"""
Tests for configuration library loader.

Run with: python -m tests.core.libraries.configuration.test_loader
"""

import os
from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel

from core.libraries.configuration import load_config, ConfigLoader


@dataclass
class SimpleConfig:
    """Simple dataclass config for testing."""

    name: str = "default"
    value: int = 10
    flag: bool = False


class PydanticConfig(BaseModel):
    """Pydantic config for testing."""

    name: str = "default"
    value: int = 10
    temperature: float = 0.1


def test_load_config_with_args():
    """Test loading config with args priority."""
    config = load_config(
        SimpleConfig,
        args={"name": "from_args", "value": 20},
    )

    assert config.name == "from_args"
    assert config.value == 20
    assert config.flag == False  # Default value
    print("✓ load_config with args priority")


def test_load_config_with_env():
    """Test loading config from environment variables."""
    # Set environment variables
    os.environ["TEST_NAME"] = "from_env"
    os.environ["TEST_VALUE"] = "30"

    config = load_config(
        SimpleConfig,
        env_prefix="TEST_",
    )

    assert config.name == "from_env"
    assert config.value == 30

    # Cleanup
    del os.environ["TEST_NAME"]
    del os.environ["TEST_VALUE"]

    print("✓ load_config with environment variables")


def test_load_config_priority():
    """Test args > env > defaults priority."""
    os.environ["PRIORITY_NAME"] = "from_env"
    os.environ["PRIORITY_VALUE"] = "50"

    config = load_config(
        SimpleConfig,
        args={"value": 100},  # Args override env
        env_prefix="PRIORITY_",
        defaults={"name": "from_defaults"},  # Lower priority
    )

    assert config.name == "from_env"  # From env (no args for name)
    assert config.value == 100  # From args (highest priority)

    # Cleanup
    del os.environ["PRIORITY_NAME"]
    del os.environ["PRIORITY_VALUE"]

    print("✓ load_config priority: args > env > defaults")


def test_load_config_with_defaults():
    """Test loading config with defaults."""
    config = load_config(
        SimpleConfig,
        defaults={"name": "from_defaults", "value": 42},
    )

    assert config.name == "from_defaults"
    assert config.value == 42
    print("✓ load_config with defaults")


def test_load_config_pydantic_model():
    """Test loading Pydantic model config."""
    config = load_config(
        PydanticConfig,
        args={"temperature": 0.5},
        defaults={"name": "pydantic_test"},
    )

    assert isinstance(config, PydanticConfig)
    assert config.name == "pydantic_test"
    assert config.temperature == 0.5
    assert config.value == 10  # Default from model
    print("✓ load_config with Pydantic model")


def test_env_type_conversion():
    """Test environment variable type conversion."""
    os.environ["TYPES_NAME"] = "test"
    os.environ["TYPES_VALUE"] = "123"
    os.environ["TYPES_FLAG"] = "true"

    config = load_config(
        SimpleConfig,
        env_prefix="TYPES_",
    )

    assert config.name == "test"  # String
    assert config.value == 123  # Converted to int
    assert config.flag == True  # Converted to bool

    # Cleanup
    del os.environ["TYPES_NAME"]
    del os.environ["TYPES_VALUE"]
    del os.environ["TYPES_FLAG"]

    print("✓ Environment variable type conversion")


def test_config_loader_class():
    """Test ConfigLoader class method."""
    config = ConfigLoader.load(
        SimpleConfig,
        args={"name": "via_loader"},
        defaults={"value": 99},
    )

    assert config.name == "via_loader"
    assert config.value == 99
    print("✓ ConfigLoader.load() method")


def test_partial_override():
    """Test partial configuration override."""
    config = load_config(
        SimpleConfig,
        args={"name": "partial"},  # Only override name
        defaults={"value": 50, "flag": True},
    )

    assert config.name == "partial"  # From args
    assert config.value == 50  # From defaults
    assert config.flag == True  # From defaults
    print("✓ Partial configuration override")


def run_all_tests():
    """Run all tests."""
    print("=== Testing Configuration Library ===\n")

    test_load_config_with_args()
    test_load_config_with_env()
    test_load_config_priority()
    test_load_config_with_defaults()
    test_load_config_pydantic_model()
    test_env_type_conversion()
    test_config_loader_class()
    test_partial_override()

    print("\n✅ All configuration tests passed!")


if __name__ == "__main__":
    run_all_tests()
