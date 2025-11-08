#!/usr/bin/env python3
"""
Unit tests for structure detection module.

Tests the detect_structure() function for both flat and nested workspace structures.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from LLM.scripts.workflow.structure_detection import detect_structure


class TestDetectStructure:
    """Test cases for detect_structure() function."""

    def test_detect_structure_nested(self, tmp_path):
        """Test that nested structure is detected when subplans folder exists."""
        # Create nested structure
        plan_folder = tmp_path / "PLAN_TEST"
        plan_folder.mkdir()
        plan_file = plan_folder / "PLAN_TEST.md"
        plan_file.write_text("# PLAN_TEST")

        subplans_folder = plan_folder / "subplans"
        subplans_folder.mkdir()

        result = detect_structure(plan_file)
        assert result == "nested"

    def test_detect_structure_flat(self, tmp_path):
        """Test that flat structure is detected when subplans folder doesn't exist."""
        # Create flat structure
        plan_folder = tmp_path / "plans"
        plan_folder.mkdir()
        plan_file = plan_folder / "PLAN_TEST.md"
        plan_file.write_text("# PLAN_TEST")

        # No subplans folder

        result = detect_structure(plan_file)
        assert result == "flat"

    def test_detect_structure_subplans_is_file(self, tmp_path):
        """Test that subplans as file (not directory) returns flat."""
        plan_folder = tmp_path / "PLAN_TEST"
        plan_folder.mkdir()
        plan_file = plan_folder / "PLAN_TEST.md"
        plan_file.write_text("# PLAN_TEST")

        # Create subplans as file (not directory)
        subplans_file = plan_folder / "subplans"
        subplans_file.write_text("not a directory")

        result = detect_structure(plan_file)
        assert result == "flat"  # Should return flat if subplans is not a directory

    def test_detect_structure_missing_parent(self, tmp_path):
        """Test that missing parent directory returns flat (backward compatibility)."""
        # Create a path that doesn't exist
        plan_file = tmp_path / "nonexistent" / "PLAN_TEST.md"

        result = detect_structure(plan_file)
        assert result == "flat"  # Default to flat for backward compatibility

    def test_detect_structure_nested_with_execution_folder(self, tmp_path):
        """Test nested structure detection when execution folder also exists."""
        plan_folder = tmp_path / "PLAN_TEST"
        plan_folder.mkdir()
        plan_file = plan_folder / "PLAN_TEST.md"
        plan_file.write_text("# PLAN_TEST")

        subplans_folder = plan_folder / "subplans"
        subplans_folder.mkdir()

        execution_folder = plan_folder / "execution"
        execution_folder.mkdir()

        result = detect_structure(plan_file)
        assert result == "nested"  # Should still detect nested based on subplans/


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
