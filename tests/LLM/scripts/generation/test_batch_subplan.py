"""
Tests for batch_subplan.py

Tests batch SUBPLAN creation functionality including:
- Dependency level calculation
- Filtering by dependency level
- Missing SUBPLAN detection
- Batch creation workflow
- Dry-run mode
- Error handling
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from LLM.scripts.generation.batch_subplan import (
    BatchResult,
    calculate_dependency_level,
    filter_by_dependency_level,
    detect_missing_subplans,
    show_batch_preview,
    confirm_batch_creation,
    create_subplan_file,
    batch_create_subplans
)


class TestBatchResult:
    """Tests for BatchResult dataclass."""
    
    def test_batch_result_empty(self):
        """Test empty batch result."""
        result = BatchResult()
        assert len(result.created) == 0
        assert len(result.skipped) == 0
        assert len(result.errors) == 0
    
    def test_batch_result_str_created(self):
        """Test string representation with created files."""
        result = BatchResult(
            created=[Path("SUBPLAN_X_11.md"), Path("SUBPLAN_X_12.md")]
        )
        output = str(result)
        assert "✅ Created 2 SUBPLANs:" in output
        assert "SUBPLAN_X_11.md" in output
        assert "SUBPLAN_X_12.md" in output
    
    def test_batch_result_str_skipped(self):
        """Test string representation with skipped achievements."""
        result = BatchResult(
            skipped=["1.1", "1.2"]
        )
        output = str(result)
        assert "⏭️  Skipped 2 (already exist):" in output
        assert "Achievement 1.1" in output
        assert "Achievement 1.2" in output
    
    def test_batch_result_str_errors(self):
        """Test string representation with errors."""
        result = BatchResult(
            errors=[("1.1", "File not found"), ("1.2", "Invalid format")]
        )
        output = str(result)
        assert "❌ Errors (2):" in output
        assert "Achievement 1.1: File not found" in output
        assert "Achievement 1.2: Invalid format" in output
    
    def test_batch_result_str_mixed(self):
        """Test string representation with mixed results."""
        result = BatchResult(
            created=[Path("SUBPLAN_X_11.md")],
            skipped=["1.2"],
            errors=[("1.3", "Error")]
        )
        output = str(result)
        assert "✅ Created 1 SUBPLANs:" in output
        assert "⏭️  Skipped 1 (already exist):" in output
        assert "❌ Errors (1):" in output


class TestDependencyLevel:
    """Tests for dependency level calculation."""
    
    def test_calculate_dependency_level_0(self):
        """Test level 0 (no dependencies)."""
        achievements = [
            {"achievement_id": "1.1", "dependencies": []},
            {"achievement_id": "1.2", "dependencies": []},
        ]
        assert calculate_dependency_level("1.1", achievements) == 0
        assert calculate_dependency_level("1.2", achievements) == 0
    
    def test_calculate_dependency_level_1(self):
        """Test level 1 (depends on level 0)."""
        achievements = [
            {"achievement_id": "1.1", "dependencies": []},
            {"achievement_id": "1.2", "dependencies": ["1.1"]},
        ]
        assert calculate_dependency_level("1.1", achievements) == 0
        assert calculate_dependency_level("1.2", achievements) == 1
    
    def test_calculate_dependency_level_2(self):
        """Test level 2 (depends on level 1)."""
        achievements = [
            {"achievement_id": "1.1", "dependencies": []},
            {"achievement_id": "1.2", "dependencies": ["1.1"]},
            {"achievement_id": "1.3", "dependencies": ["1.2"]},
        ]
        assert calculate_dependency_level("1.1", achievements) == 0
        assert calculate_dependency_level("1.2", achievements) == 1
        assert calculate_dependency_level("1.3", achievements) == 2
    
    def test_calculate_dependency_level_multiple_deps(self):
        """Test with multiple dependencies."""
        achievements = [
            {"achievement_id": "1.1", "dependencies": []},
            {"achievement_id": "1.2", "dependencies": []},
            {"achievement_id": "1.3", "dependencies": ["1.1", "1.2"]},
        ]
        assert calculate_dependency_level("1.3", achievements) == 1
    
    def test_calculate_dependency_level_complex(self):
        """Test complex dependency chain."""
        achievements = [
            {"achievement_id": "1.1", "dependencies": []},
            {"achievement_id": "1.2", "dependencies": ["1.1"]},
            {"achievement_id": "1.3", "dependencies": []},
            {"achievement_id": "2.1", "dependencies": ["1.2", "1.3"]},
        ]
        assert calculate_dependency_level("1.1", achievements) == 0
        assert calculate_dependency_level("1.2", achievements) == 1
        assert calculate_dependency_level("1.3", achievements) == 0
        assert calculate_dependency_level("2.1", achievements) == 2
    
    def test_calculate_dependency_level_not_found(self):
        """Test with achievement not in list."""
        achievements = [
            {"achievement_id": "1.1", "dependencies": []},
        ]
        # Should return 0 for not found
        assert calculate_dependency_level("1.2", achievements) == 0
    
    def test_calculate_dependency_level_memoization(self):
        """Test that memoization works."""
        achievements = [
            {"achievement_id": "1.1", "dependencies": []},
            {"achievement_id": "1.2", "dependencies": ["1.1"]},
            {"achievement_id": "1.3", "dependencies": ["1.2"]},
        ]
        memo = {}
        calculate_dependency_level("1.3", achievements, memo)
        # Memo should have all three levels cached
        assert "1.1" in memo
        assert "1.2" in memo
        assert "1.3" in memo
        assert memo["1.1"] == 0
        assert memo["1.2"] == 1
        assert memo["1.3"] == 2


class TestFiltering:
    """Tests for dependency level filtering."""
    
    def test_filter_by_dependency_level_0(self):
        """Test filtering level 0."""
        achievements = [
            {"achievement_id": "1.1", "dependencies": []},
            {"achievement_id": "1.2", "dependencies": ["1.1"]},
            {"achievement_id": "1.3", "dependencies": []},
        ]
        level_0 = filter_by_dependency_level(achievements, level=0)
        assert len(level_0) == 2
        assert level_0[0]["achievement_id"] == "1.1"
        assert level_0[1]["achievement_id"] == "1.3"
    
    def test_filter_by_dependency_level_1(self):
        """Test filtering level 1."""
        achievements = [
            {"achievement_id": "1.1", "dependencies": []},
            {"achievement_id": "1.2", "dependencies": ["1.1"]},
            {"achievement_id": "1.3", "dependencies": ["1.1"]},
        ]
        level_1 = filter_by_dependency_level(achievements, level=1)
        assert len(level_1) == 2
        assert level_1[0]["achievement_id"] == "1.2"
        assert level_1[1]["achievement_id"] == "1.3"
    
    def test_filter_by_dependency_level_empty(self):
        """Test filtering with no matches."""
        achievements = [
            {"achievement_id": "1.1", "dependencies": []},
            {"achievement_id": "1.2", "dependencies": ["1.1"]},
        ]
        level_2 = filter_by_dependency_level(achievements, level=2)
        assert len(level_2) == 0
    
    def test_filter_by_dependency_level_empty_list(self):
        """Test filtering empty list."""
        level_0 = filter_by_dependency_level([], level=0)
        assert len(level_0) == 0


class TestDetection:
    """Tests for missing SUBPLAN detection."""
    
    def test_detect_missing_subplans_none_exist(self, tmp_path):
        """Test when no SUBPLANs exist."""
        # Create plan structure
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        (plan_dir / "subplans").mkdir()
        
        achievements = [
            {"achievement_id": "1.1"},
            {"achievement_id": "1.2"},
        ]
        
        missing = detect_missing_subplans(plan_dir, achievements)
        assert len(missing) == 2
    
    def test_detect_missing_subplans_all_exist(self, tmp_path):
        """Test when all SUBPLANs exist."""
        # Create plan structure
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        subplans_dir = plan_dir / "subplans"
        subplans_dir.mkdir()
        
        # Create SUBPLANs
        (subplans_dir / "SUBPLAN_MY-PLAN_11.md").write_text("# SUBPLAN 1.1")
        (subplans_dir / "SUBPLAN_MY-PLAN_12.md").write_text("# SUBPLAN 1.2")
        
        achievements = [
            {"achievement_id": "1.1"},
            {"achievement_id": "1.2"},
        ]
        
        missing = detect_missing_subplans(plan_dir, achievements)
        assert len(missing) == 0
    
    def test_detect_missing_subplans_some_exist(self, tmp_path):
        """Test when some SUBPLANs exist."""
        # Create plan structure
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        subplans_dir = plan_dir / "subplans"
        subplans_dir.mkdir()
        
        # Create only one SUBPLAN
        (subplans_dir / "SUBPLAN_MY-PLAN_11.md").write_text("# SUBPLAN 1.1")
        
        achievements = [
            {"achievement_id": "1.1"},
            {"achievement_id": "1.2"},
        ]
        
        missing = detect_missing_subplans(plan_dir, achievements)
        assert len(missing) == 1
        assert missing[0]["achievement_id"] == "1.2"
    
    def test_detect_missing_subplans_no_subplans_dir(self, tmp_path):
        """Test when subplans directory doesn't exist."""
        # Create plan structure without subplans dir
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        
        achievements = [
            {"achievement_id": "1.1"},
        ]
        
        missing = detect_missing_subplans(plan_dir, achievements)
        assert len(missing) == 1


class TestPreviewAndConfirmation:
    """Tests for preview and confirmation functions."""
    
    def test_show_batch_preview(self, capsys):
        """Test batch preview display."""
        achievements = [
            {"achievement_id": "1.1"},
            {"achievement_id": "1.2"},
        ]
        
        show_batch_preview(achievements, "MY-PLAN")
        
        captured = capsys.readouterr()
        assert "📋 Batch SUBPLAN Creation Preview" in captured.out
        assert "Plan: MY-PLAN" in captured.out
        assert "Achievements to create: 2" in captured.out
        assert "Achievement 1.1 - SUBPLAN_MY-PLAN_11.md" in captured.out
        assert "Achievement 1.2 - SUBPLAN_MY-PLAN_12.md" in captured.out
    
    @patch('builtins.input', return_value='y')
    def test_confirm_batch_creation_yes(self, mock_input):
        """Test confirmation with yes."""
        achievements = [{"achievement_id": "1.1"}]
        result = confirm_batch_creation(achievements)
        assert result is True
    
    @patch('builtins.input', return_value='n')
    def test_confirm_batch_creation_no(self, mock_input):
        """Test confirmation with no."""
        achievements = [{"achievement_id": "1.1"}]
        result = confirm_batch_creation(achievements)
        assert result is False
    
    @patch('builtins.input', return_value='')
    def test_confirm_batch_creation_empty(self, mock_input):
        """Test confirmation with empty (default no)."""
        achievements = [{"achievement_id": "1.1"}]
        result = confirm_batch_creation(achievements)
        assert result is False


class TestSubplanCreation:
    """Tests for SUBPLAN file creation."""
    
    def test_create_subplan_file(self, tmp_path):
        """Test creating a single SUBPLAN file."""
        # Create plan structure
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        
        # Create SUBPLAN
        subplan_path = create_subplan_file(plan_dir, "1.1", {})
        
        assert subplan_path.exists()
        assert subplan_path.name == "SUBPLAN_MY-PLAN_11.md"
        
        content = subplan_path.read_text()
        assert "# SUBPLAN: Achievement 1.1" in content
        assert "**PLAN**: MY-PLAN" in content


class TestBatchCreation:
    """Tests for batch SUBPLAN creation."""
    
    def test_batch_create_subplans_no_parallel_json(self, tmp_path):
        """Test batch creation with no parallel.json."""
        # Create plan structure without parallel.json
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        
        result = batch_create_subplans(plan_dir, dry_run=False)
        
        assert len(result.created) == 0
        assert len(result.errors) == 1
        assert "parallel.json not found" in result.errors[0][1]
    
    def test_batch_create_subplans_invalid_json(self, tmp_path):
        """Test batch creation with invalid JSON."""
        # Create plan structure with invalid JSON
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        (plan_dir / "parallel.json").write_text("invalid json")
        
        result = batch_create_subplans(plan_dir, dry_run=False)
        
        assert len(result.created) == 0
        assert len(result.errors) == 1
        assert "Invalid JSON" in result.errors[0][1]
    
    def test_batch_create_subplans_dry_run(self, tmp_path, capsys):
        """Test batch creation in dry-run mode."""
        # Create plan structure
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        
        # Create parallel.json
        parallel_data = {
            "parallelization_level": "level_1",
            "achievements": [
                {"achievement_id": "1.1", "dependencies": []},
                {"achievement_id": "1.2", "dependencies": []},
            ]
        }
        (plan_dir / "parallel.json").write_text(json.dumps(parallel_data))
        
        result = batch_create_subplans(plan_dir, dry_run=True)
        
        # Dry-run should not create files
        assert len(result.created) == 0
        assert not (plan_dir / "subplans" / "SUBPLAN_MY-PLAN_11.md").exists()
        
        captured = capsys.readouterr()
        assert "DRY-RUN MODE" in captured.out
    
    @patch('builtins.input', return_value='n')
    def test_batch_create_subplans_cancelled(self, mock_input, tmp_path):
        """Test batch creation cancelled by user."""
        # Create plan structure
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        
        # Create parallel.json
        parallel_data = {
            "parallelization_level": "level_1",
            "achievements": [
                {"achievement_id": "1.1", "dependencies": []},
            ]
        }
        (plan_dir / "parallel.json").write_text(json.dumps(parallel_data))
        
        result = batch_create_subplans(plan_dir, dry_run=False)
        
        # Should not create files if cancelled
        assert len(result.created) == 0
    
    @patch('builtins.input', return_value='y')
    def test_batch_create_subplans_success(self, mock_input, tmp_path):
        """Test successful batch creation."""
        # Create plan structure
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        
        # Create parallel.json
        parallel_data = {
            "parallelization_level": "level_1",
            "achievements": [
                {"achievement_id": "1.1", "dependencies": []},
                {"achievement_id": "1.2", "dependencies": []},
            ]
        }
        (plan_dir / "parallel.json").write_text(json.dumps(parallel_data))
        
        result = batch_create_subplans(plan_dir, dry_run=False)
        
        # Should create 2 SUBPLANs
        assert len(result.created) == 2
        assert (plan_dir / "subplans" / "SUBPLAN_MY-PLAN_11.md").exists()
        assert (plan_dir / "subplans" / "SUBPLAN_MY-PLAN_12.md").exists()
    
    @patch('builtins.input', return_value='y')
    def test_batch_create_subplans_skip_existing(self, mock_input, tmp_path):
        """Test skipping existing SUBPLANs."""
        # Create plan structure
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        subplans_dir = plan_dir / "subplans"
        subplans_dir.mkdir()
        
        # Create one existing SUBPLAN
        (subplans_dir / "SUBPLAN_MY-PLAN_11.md").write_text("# Existing")
        
        # Create parallel.json
        parallel_data = {
            "parallelization_level": "level_1",
            "achievements": [
                {"achievement_id": "1.1", "dependencies": []},
                {"achievement_id": "1.2", "dependencies": []},
            ]
        }
        (plan_dir / "parallel.json").write_text(json.dumps(parallel_data))
        
        result = batch_create_subplans(plan_dir, dry_run=False)
        
        # Should create 1 SUBPLAN and skip 1
        assert len(result.created) == 1
        assert len(result.skipped) == 1
        assert result.skipped[0] == "1.1"


