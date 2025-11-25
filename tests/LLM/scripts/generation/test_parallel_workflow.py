"""
Tests for parallel_workflow module.

Tests parallel workflow support including:
- Parallel discovery prompt generation
- parallel.json detection and validation
- Parallel execution menu
- Dependency graph visualization

Created: 2025-11-13
Achievement: 2.1 - generate_prompt.py Enhanced with Parallel Support
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from LLM.scripts.generation.parallel_workflow import (
    generate_parallel_upgrade_prompt,
    detect_parallel_json,
    validate_and_load_parallel_json,
    detect_and_validate_parallel_json,
    show_parallel_menu,
    handle_parallel_menu_selection,
    show_dependency_graph,
)


# Parallel Upgrade Tests
# ============================================================================


class TestParallelUpgrade:
    """Test parallel discovery prompt generation."""

    def test_parallel_upgrade_generates_prompt(self, tmp_path):
        """Test --parallel-upgrade flag generates prompt."""
        # Create mock plan directory
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()
        plan_file = plan_dir / "PLAN_TEST-PLAN.md"
        plan_file.write_text("""# PLAN: TEST-PLAN

## Achievement Index

**Achievement 1.1**: Test Achievement (2-3h)
**Achievement 1.2**: Another Test (3-4h)
""")

        # Generate prompt
        prompt = generate_parallel_upgrade_prompt(plan_dir)

        # Assert prompt contains expected sections
        assert "Analyze @PLAN_TEST-PLAN.md" in prompt
        assert "INDEPENDENCE CRITERIA" in prompt
        assert "OUTPUT FORMAT" in prompt
        assert "parallelization_level" in prompt

    def test_parallel_upgrade_missing_plan(self, tmp_path):
        """Test error when no PLAN file found."""
        plan_dir = tmp_path / "EMPTY-PLAN"
        plan_dir.mkdir()

        with pytest.raises(FileNotFoundError, match="No PLAN_\\*.md file found"):
            generate_parallel_upgrade_prompt(plan_dir)


# Detection Tests
# ============================================================================


class TestDetection:
    """Test parallel.json detection."""

    def test_detect_parallel_json_exists(self, tmp_path):
        """Test detection when parallel.json exists."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()
        parallel_json = plan_dir / "parallel.json"
        parallel_json.write_text('{"plan_name": "TEST"}')

        result = detect_parallel_json(plan_dir)

        assert result is not None
        assert result == parallel_json
        assert result.exists()

    def test_detect_parallel_json_missing(self, tmp_path):
        """Test detection when parallel.json doesn't exist."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()

        result = detect_parallel_json(plan_dir)

        assert result is None


# Validation Tests
# ============================================================================


class TestValidation:
    """Test parallel.json validation."""

    def test_validate_valid_parallel_json(self, tmp_path):
        """Test validation with valid file."""
        parallel_json = tmp_path / "parallel.json"
        data = {
            "plan_name": "TEST-PLAN",
            "parallelization_level": "level_1",
            "achievements": [
                {"achievement_id": "1.1", "dependencies": [], "status": "not_started"}
            ],
        }
        parallel_json.write_text(json.dumps(data))

        result = validate_and_load_parallel_json(parallel_json)

        assert result is not None
        assert result["plan_name"] == "TEST-PLAN"
        assert result["parallelization_level"] == "level_1"
        assert len(result["achievements"]) == 1

    def test_validate_invalid_json_shows_errors(self, tmp_path, capsys):
        """Test validation with invalid JSON shows errors."""
        parallel_json = tmp_path / "parallel.json"
        data = {
            "plan_name": "TEST-PLAN",
            "parallelization_level": "invalid_level",  # Invalid
            "achievements": [],
        }
        parallel_json.write_text(json.dumps(data))

        result = validate_and_load_parallel_json(parallel_json)

        assert result is None
        captured = capsys.readouterr()
        assert "❌ Invalid parallel.json" in captured.out
        assert "parallelization_level" in captured.out
        assert "💡 Fix:" in captured.out

    def test_validate_malformed_json(self, tmp_path, capsys):
        """Test validation with malformed JSON."""
        parallel_json = tmp_path / "parallel.json"
        parallel_json.write_text("{invalid json")

        result = validate_and_load_parallel_json(parallel_json)

        assert result is None
        captured = capsys.readouterr()
        assert "❌ Invalid parallel.json" in captured.out

    def test_detect_and_validate_combined(self, tmp_path):
        """Test combined detection and validation."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()
        parallel_json = plan_dir / "parallel.json"
        data = {
            "plan_name": "TEST-PLAN",
            "parallelization_level": "level_2",
            "achievements": [
                {"achievement_id": "1.1", "dependencies": [], "status": "not_started"},
                {"achievement_id": "1.2", "dependencies": ["1.1"], "status": "not_started"},
            ],
        }
        parallel_json.write_text(json.dumps(data))

        json_path, json_data = detect_and_validate_parallel_json(plan_dir)

        assert json_path is not None
        assert json_data is not None
        assert json_data["plan_name"] == "TEST-PLAN"
        assert len(json_data["achievements"]) == 2

    def test_detect_and_validate_missing_file(self, tmp_path):
        """Test combined detection when file doesn't exist."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()

        json_path, json_data = detect_and_validate_parallel_json(plan_dir)

        assert json_path is None
        assert json_data is None


# Menu Tests
# ============================================================================


class TestMenu:
    """Test parallel execution menu."""

    def test_show_parallel_menu_displays_options(self, capsys, monkeypatch):
        """Test menu displays all options."""
        data = {
            "parallelization_level": "level_1",
            "achievements": [{"achievement_id": "1.1"}],
        }

        # Mock input to return '5' (back)
        monkeypatch.setattr("builtins.input", lambda _: "5")

        choice = show_parallel_menu(data, "TEST-PLAN")

        captured = capsys.readouterr()
        assert "🔀 Parallel Execution Menu" in captured.out
        assert "1. Batch Create SUBPLANs" in captured.out
        assert "2. Batch Create EXECUTIONs" in captured.out
        assert "3. Run Parallel Executions" in captured.out
        assert "4. View Dependency Graph" in captured.out
        assert "5. Back to Main Menu" in captured.out
        assert choice == "5"

    def test_handle_menu_selection_option_1(self, capsys, tmp_path):
        """Test menu option 1 (Batch SUBPLANs)."""
        data = {"achievements": []}
        plan_path = tmp_path / "TEST-PLAN"
        plan_path.mkdir()
        handle_parallel_menu_selection("1", data, "TEST-PLAN", plan_path)

        captured = capsys.readouterr()
        assert "Batch SUBPLAN Creation" in captured.out

    def test_handle_menu_selection_option_2(self, capsys, tmp_path):
        """Test menu option 2 (Batch EXECUTIONs)."""
        data = {"achievements": []}
        plan_path = tmp_path / "TEST-PLAN"
        plan_path.mkdir()
        handle_parallel_menu_selection("2", data, "TEST-PLAN", plan_path)

        captured = capsys.readouterr()
        assert "Batch EXECUTION Creation" in captured.out

    def test_handle_menu_selection_option_3(self, capsys, tmp_path):
        """Test menu option 3 (Run Parallel)."""
        data = {"achievements": []}
        plan_path = tmp_path / "TEST-PLAN"
        plan_path.mkdir()
        handle_parallel_menu_selection("3", data, "TEST-PLAN", plan_path)

        captured = capsys.readouterr()
        assert "Parallel execution coordination" in captured.out

    def test_handle_menu_selection_option_4(self, capsys, tmp_path):
        """Test menu option 4 (View Dependency Graph)."""
        data = {
            "achievements": [
                {"achievement_id": "1.1", "dependencies": []},
                {"achievement_id": "1.2", "dependencies": ["1.1"]},
            ]
        }
        plan_path = tmp_path / "TEST-PLAN"
        plan_path.mkdir()
        handle_parallel_menu_selection("4", data, "TEST-PLAN", plan_path)

        captured = capsys.readouterr()
        assert "📊 Dependency Graph:" in captured.out
        assert "1.1 → no dependencies" in captured.out
        assert "1.2 → depends on: 1.1" in captured.out

    def test_handle_menu_selection_option_5(self, tmp_path):
        """Test menu option 5 (Back) returns without output."""
        data = {"achievements": []}
        plan_path = tmp_path / "TEST-PLAN"
        plan_path.mkdir()
        # Should return without error
        handle_parallel_menu_selection("5", data, "TEST-PLAN", plan_path)

    def test_handle_menu_selection_invalid(self, capsys, tmp_path):
        """Test invalid menu option."""
        data = {"achievements": []}
        plan_path = tmp_path / "TEST-PLAN"
        plan_path.mkdir()
        handle_parallel_menu_selection("99", data, "TEST-PLAN", plan_path)

        captured = capsys.readouterr()
        assert "❌ Invalid option" in captured.out


# Dependency Graph Tests
# ============================================================================


class TestDependencyGraph:
    """Test dependency graph visualization."""

    def test_show_dependency_graph_no_dependencies(self, capsys):
        """Test graph with no dependencies."""
        data = {
            "achievements": [
                {"achievement_id": "1.1", "dependencies": []},
                {"achievement_id": "1.2", "dependencies": []},
            ]
        }

        show_dependency_graph(data)

        captured = capsys.readouterr()
        assert "📊 Dependency Graph:" in captured.out
        assert "1.1 → no dependencies" in captured.out
        assert "1.2 → no dependencies" in captured.out

    def test_show_dependency_graph_with_dependencies(self, capsys):
        """Test graph with dependencies."""
        data = {
            "achievements": [
                {"achievement_id": "1.1", "dependencies": []},
                {"achievement_id": "1.2", "dependencies": ["1.1"]},
                {"achievement_id": "1.3", "dependencies": ["1.1", "1.2"]},
            ]
        }

        show_dependency_graph(data)

        captured = capsys.readouterr()
        assert "1.1 → no dependencies" in captured.out
        assert "1.2 → depends on: 1.1" in captured.out
        assert "1.3 → depends on: 1.1, 1.2" in captured.out

    def test_show_dependency_graph_empty(self, capsys):
        """Test graph with no achievements."""
        data = {"achievements": []}

        show_dependency_graph(data)

        captured = capsys.readouterr()
        assert "📊 Dependency Graph:" in captured.out


# Integration Tests
# ============================================================================


class TestIntegration:
    """Test full workflow integration."""

    def test_full_workflow_with_parallel_json(self, tmp_path):
        """Test end-to-end workflow with parallel.json."""
        # Create plan directory
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()

        # Create PLAN file
        plan_file = plan_dir / "PLAN_TEST-PLAN.md"
        plan_file.write_text("""# PLAN: TEST-PLAN

## Achievement Index

**Achievement 1.1**: Test Achievement (2-3h)
""")

        # Create parallel.json
        parallel_json = plan_dir / "parallel.json"
        data = {
            "plan_name": "TEST-PLAN",
            "parallelization_level": "level_1",
            "achievements": [
                {"achievement_id": "1.1", "dependencies": [], "status": "not_started"}
            ],
        }
        parallel_json.write_text(json.dumps(data))

        # Test detection
        json_path, json_data = detect_and_validate_parallel_json(plan_dir)
        assert json_path is not None
        assert json_data is not None

        # Test prompt generation
        prompt = generate_parallel_upgrade_prompt(plan_dir)
        assert "PLAN_TEST-PLAN" in prompt

    def test_backward_compatibility_without_parallel_json(self, tmp_path):
        """Test workflow works without parallel.json."""
        plan_dir = tmp_path / "TEST-PLAN"
        plan_dir.mkdir()

        # No parallel.json created
        json_path, json_data = detect_and_validate_parallel_json(plan_dir)

        # Should return None, not error
        assert json_path is None
        assert json_data is None


