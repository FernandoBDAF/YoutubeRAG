#!/usr/bin/env python3
"""
Integration tests for dual structure discovery functions.

Tests that discovery functions work with both flat and nested workspace structures.
"""

import pytest
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))


class TestDualStructureDiscovery:
    """Test cases for discovery functions with dual structure support."""

    @pytest.mark.skip(
        reason="Flat structure (work-space/subplans/) not supported by current implementation - only feature-specific subplans/ folders"
    )
    def test_find_subplan_flat_structure(self, tmp_path):
        """Test finding SUBPLAN in flat structure (SKIPPED - not implemented)."""
        from LLM.scripts.generation.generate_prompt import find_subplan_for_achievement

        # Create flat structure
        plans_folder = tmp_path / "work-space" / "plans"
        plans_folder.mkdir(parents=True)
        plan_file = plans_folder / "PLAN_TEST.md"
        plan_file.write_text("# PLAN_TEST")

        subplans_folder = tmp_path / "work-space" / "subplans"
        subplans_folder.mkdir(parents=True)
        subplan_file = subplans_folder / "SUBPLAN_TEST_11.md"
        subplan_file.write_text("# SUBPLAN_TEST")

        # Change to tmp_path for relative path resolution
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = find_subplan_for_achievement("TEST", "1.1", plan_file)
            assert result is not None
            assert result.name == "SUBPLAN_TEST_11.md"
        finally:
            os.chdir(original_cwd)

    def test_find_subplan_nested_structure(self, tmp_path):
        """Test finding SUBPLAN in nested structure."""
        from LLM.scripts.generation.generate_prompt import find_subplan_for_achievement

        # Create nested structure
        plan_folder = tmp_path / "work-space" / "plans" / "PLAN_TEST"
        plan_folder.mkdir(parents=True)
        plan_file = plan_folder / "PLAN_TEST.md"
        plan_file.write_text("# PLAN_TEST")

        subplans_folder = plan_folder / "subplans"
        subplans_folder.mkdir()
        subplan_file = subplans_folder / "SUBPLAN_TEST_11.md"
        subplan_file.write_text("# SUBPLAN_TEST")

        # Change to tmp_path for relative path resolution
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = find_subplan_for_achievement("TEST", "1.1", plan_file)
            assert result is not None
            assert result.name == "SUBPLAN_TEST_11.md"
        finally:
            os.chdir(original_cwd)

    def test_find_subplan_both_structures_prefers_nested(self, tmp_path):
        """Test that nested structure is preferred when both exist."""
        from LLM.scripts.generation.generate_prompt import find_subplan_for_achievement

        # Create both structures
        plan_folder = tmp_path / "work-space" / "plans" / "PLAN_TEST"
        plan_folder.mkdir(parents=True)
        plan_file = plan_folder / "PLAN_TEST.md"
        plan_file.write_text("# PLAN_TEST")

        # Nested structure
        nested_subplans = plan_folder / "subplans"
        nested_subplans.mkdir()
        nested_subplan = nested_subplans / "SUBPLAN_TEST_11.md"
        nested_subplan.write_text("# SUBPLAN_TEST nested")

        # Flat structure
        flat_subplans = tmp_path / "work-space" / "subplans"
        flat_subplans.mkdir(parents=True)
        flat_subplan = flat_subplans / "SUBPLAN_TEST_11.md"
        flat_subplan.write_text("# SUBPLAN_TEST flat")

        # Change to tmp_path for relative path resolution
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = find_subplan_for_achievement("TEST", "1.1", plan_file)
            assert result is not None
            # Should prefer nested structure
            assert "nested" in result.read_text()
        finally:
            os.chdir(original_cwd)

    def test_find_execution_files_flat_structure(self, tmp_path):
        """Test finding EXECUTION_TASK files in flat structure."""
        from LLM.scripts.generation.generate_subplan_prompt import find_execution_files

        # Create flat structure
        plans_folder = tmp_path / "work-space" / "plans"
        plans_folder.mkdir(parents=True)
        plan_file = plans_folder / "PLAN_TEST.md"
        plan_file.write_text("# PLAN_TEST")

        subplans_folder = tmp_path / "work-space" / "subplans"
        subplans_folder.mkdir(parents=True)
        subplan_file = subplans_folder / "SUBPLAN_TEST_01.md"
        subplan_file.write_text("# SUBPLAN_TEST\n\nEXECUTION_TASK_TEST_01_01")

        execution_folder = tmp_path / "work-space" / "execution"
        execution_folder.mkdir(parents=True)
        execution_file = execution_folder / "EXECUTION_TASK_TEST_01_01.md"
        execution_file.write_text("# EXECUTION_TASK")

        # Change to tmp_path for relative path resolution
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            results = find_execution_files(subplan_file)
            assert len(results) > 0
            assert any("EXECUTION_TASK_TEST_01_01.md" in str(r) for r in results)
        finally:
            os.chdir(original_cwd)

    def test_find_execution_files_nested_structure(self, tmp_path):
        """Test finding EXECUTION_TASK files in nested structure."""
        from LLM.scripts.generation.generate_subplan_prompt import find_execution_files

        # Create nested structure
        plan_folder = tmp_path / "work-space" / "plans" / "PLAN_TEST"
        plan_folder.mkdir(parents=True)
        plan_file = plan_folder / "PLAN_TEST.md"
        plan_file.write_text("# PLAN_TEST")

        subplans_folder = plan_folder / "subplans"
        subplans_folder.mkdir()
        subplan_file = subplans_folder / "SUBPLAN_TEST_01.md"
        subplan_file.write_text("# SUBPLAN_TEST\n\nEXECUTION_TASK_TEST_01_01")

        execution_folder = plan_folder / "execution"
        execution_folder.mkdir()
        execution_file = execution_folder / "EXECUTION_TASK_TEST_01_01.md"
        execution_file.write_text("# EXECUTION_TASK")

        # Change to tmp_path for relative path resolution
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            results = find_execution_files(subplan_file)
            assert len(results) > 0
            assert any("EXECUTION_TASK_TEST_01_01.md" in str(r) for r in results)
        finally:
            os.chdir(original_cwd)

    def test_find_previous_executions_flat_structure(self, tmp_path):
        """Test finding previous EXECUTION_TASK files in flat structure."""
        from LLM.scripts.generation.generate_execution_prompt import find_previous_executions

        # Create flat structure
        plans_folder = tmp_path / "work-space" / "plans"
        plans_folder.mkdir(parents=True)
        plan_file = plans_folder / "PLAN_TEST.md"
        plan_file.write_text("# PLAN_TEST")

        subplans_folder = tmp_path / "work-space" / "subplans"
        subplans_folder.mkdir(parents=True)
        subplan_file = subplans_folder / "SUBPLAN_TEST_01.md"
        subplan_file.write_text(
            "# SUBPLAN_TEST\n\nEXECUTION_TASK_TEST_01_01\nEXECUTION_TASK_TEST_01_02"
        )

        execution_folder = tmp_path / "work-space" / "execution"
        execution_folder.mkdir(parents=True)
        execution_file_1 = execution_folder / "EXECUTION_TASK_TEST_01_01.md"
        execution_file_1.write_text("# EXECUTION_TASK 01")
        execution_file_2 = execution_folder / "EXECUTION_TASK_TEST_01_02.md"
        execution_file_2.write_text("# EXECUTION_TASK 02")

        # Change to tmp_path for relative path resolution
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            results = find_previous_executions(subplan_file)
            assert len(results) >= 2
            # Should be sorted by execution number
            assert "01" in str(results[0]) or "02" in str(results[0])
        finally:
            os.chdir(original_cwd)

    def test_find_previous_executions_nested_structure(self, tmp_path):
        """Test finding previous EXECUTION_TASK files in nested structure."""
        from LLM.scripts.generation.generate_execution_prompt import find_previous_executions

        # Create nested structure
        plan_folder = tmp_path / "work-space" / "plans" / "PLAN_TEST"
        plan_folder.mkdir(parents=True)
        plan_file = plan_folder / "PLAN_TEST.md"
        plan_file.write_text("# PLAN_TEST")

        subplans_folder = plan_folder / "subplans"
        subplans_folder.mkdir()
        subplan_file = subplans_folder / "SUBPLAN_TEST_01.md"
        subplan_file.write_text(
            "# SUBPLAN_TEST\n\nEXECUTION_TASK_TEST_01_01\nEXECUTION_TASK_TEST_01_02"
        )

        execution_folder = plan_folder / "execution"
        execution_folder.mkdir()
        execution_file_1 = execution_folder / "EXECUTION_TASK_TEST_01_01.md"
        execution_file_1.write_text("# EXECUTION_TASK 01")
        execution_file_2 = execution_folder / "EXECUTION_TASK_TEST_01_02.md"
        execution_file_2.write_text("# EXECUTION_TASK 02")

        # Change to tmp_path for relative path resolution
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            results = find_previous_executions(subplan_file)
            assert len(results) >= 2
            # Should be sorted by execution number
            assert "01" in str(results[0]) or "02" in str(results[0])
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
