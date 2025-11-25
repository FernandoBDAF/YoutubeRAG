"""
Tests for batch_execution.py

Tests batch EXECUTION creation functionality including:
- Prerequisite validation (SUBPLANs must exist)
- Dependency level filtering (reused from batch_subplan)
- Missing EXECUTION detection
- Batch creation workflow
- Dry-run mode
- Error handling
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from LLM.scripts.generation.batch_execution import (
    BatchResult,
    validate_subplan_prerequisites,
    detect_missing_executions,
    show_batch_preview,
    confirm_batch_creation,
    create_execution_file,
    batch_create_executions
)


class TestBatchResult:
    """Tests for BatchResult dataclass."""
    
    def test_batch_result_empty(self):
        """Test empty batch result."""
        result = BatchResult()
        assert len(result.created) == 0
        assert len(result.skipped) == 0
        assert len(result.errors) == 0
        assert len(result.missing_subplans) == 0
    
    def test_batch_result_str_created(self):
        """Test string representation with created files."""
        result = BatchResult(
            created=[Path("EXECUTION_TASK_X_11_01.md"), Path("EXECUTION_TASK_X_12_01.md")]
        )
        output = str(result)
        assert "✅ Created 2 EXECUTION_TASKs:" in output
        assert "EXECUTION_TASK_X_11_01.md" in output
        assert "EXECUTION_TASK_X_12_01.md" in output
    
    def test_batch_result_str_missing_subplans(self):
        """Test string representation with missing SUBPLANs."""
        result = BatchResult(
            missing_subplans=["1.1", "1.2"]
        )
        output = str(result)
        assert "⚠️  Missing 2 SUBPLANs (create these first):" in output
        assert "Achievement 1.1" in output
        assert "Achievement 1.2" in output
    
    def test_batch_result_str_mixed(self):
        """Test string representation with mixed results."""
        result = BatchResult(
            created=[Path("EXECUTION_TASK_X_11_01.md")],
            skipped=["1.2"],
            errors=[("1.3", "Error")],
            missing_subplans=["1.4"]
        )
        output = str(result)
        assert "⚠️  Missing 1 SUBPLANs" in output
        assert "✅ Created 1 EXECUTION_TASKs:" in output
        assert "⏭️  Skipped 1 (already exist):" in output
        assert "❌ Errors (1):" in output


class TestPrerequisiteValidation:
    """Tests for SUBPLAN prerequisite validation."""
    
    def test_validate_subplan_prerequisites_all_exist(self, tmp_path):
        """Test when all SUBPLANs exist."""
        # Create plan structure with SUBPLANs
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
        
        valid, missing = validate_subplan_prerequisites(plan_dir, achievements)
        
        assert len(valid) == 2
        assert len(missing) == 0
    
    def test_validate_subplan_prerequisites_none_exist(self, tmp_path):
        """Test when no SUBPLANs exist."""
        # Create plan structure without SUBPLANs
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        subplans_dir = plan_dir / "subplans"
        subplans_dir.mkdir()
        
        achievements = [
            {"achievement_id": "1.1"},
            {"achievement_id": "1.2"},
        ]
        
        valid, missing = validate_subplan_prerequisites(plan_dir, achievements)
        
        assert len(valid) == 0
        assert len(missing) == 2
        assert "1.1" in missing
        assert "1.2" in missing
    
    def test_validate_subplan_prerequisites_some_missing(self, tmp_path):
        """Test when some SUBPLANs missing."""
        # Create plan structure with partial SUBPLANs
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
        
        valid, missing = validate_subplan_prerequisites(plan_dir, achievements)
        
        assert len(valid) == 1
        assert valid[0]["achievement_id"] == "1.1"
        assert len(missing) == 1
        assert "1.2" in missing


class TestDetection:
    """Tests for missing EXECUTION detection."""
    
    def test_detect_missing_executions_none_exist(self, tmp_path):
        """Test when no EXECUTIONs exist."""
        # Create plan structure
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        (plan_dir / "execution").mkdir()
        
        achievements = [
            {"achievement_id": "1.1"},
            {"achievement_id": "1.2"},
        ]
        
        missing = detect_missing_executions(plan_dir, achievements)
        assert len(missing) == 2
    
    def test_detect_missing_executions_all_exist(self, tmp_path):
        """Test when all EXECUTIONs exist."""
        # Create plan structure
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        execution_dir = plan_dir / "execution"
        execution_dir.mkdir()
        
        # Create EXECUTION_TASKs
        (execution_dir / "EXECUTION_TASK_MY-PLAN_11_01.md").write_text("# EXECUTION 1.1")
        (execution_dir / "EXECUTION_TASK_MY-PLAN_12_01.md").write_text("# EXECUTION 1.2")
        
        achievements = [
            {"achievement_id": "1.1"},
            {"achievement_id": "1.2"},
        ]
        
        missing = detect_missing_executions(plan_dir, achievements)
        assert len(missing) == 0
    
    def test_detect_missing_executions_some_exist(self, tmp_path):
        """Test when some EXECUTIONs exist."""
        # Create plan structure
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        execution_dir = plan_dir / "execution"
        execution_dir.mkdir()
        
        # Create only one EXECUTION_TASK
        (execution_dir / "EXECUTION_TASK_MY-PLAN_11_01.md").write_text("# EXECUTION 1.1")
        
        achievements = [
            {"achievement_id": "1.1"},
            {"achievement_id": "1.2"},
        ]
        
        missing = detect_missing_executions(plan_dir, achievements)
        assert len(missing) == 1
        assert missing[0]["achievement_id"] == "1.2"
    
    def test_detect_missing_executions_no_execution_dir(self, tmp_path):
        """Test when execution directory doesn't exist."""
        # Create plan structure without execution dir
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        
        achievements = [
            {"achievement_id": "1.1"},
        ]
        
        missing = detect_missing_executions(plan_dir, achievements)
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
        assert "📋 Batch EXECUTION Creation Preview" in captured.out
        assert "Plan: MY-PLAN" in captured.out
        assert "Achievements to create: 2" in captured.out
        assert "Achievement 1.1 - EXECUTION_TASK_MY-PLAN_11_01.md" in captured.out
        assert "Achievement 1.2 - EXECUTION_TASK_MY-PLAN_12_01.md" in captured.out
    
    def test_show_batch_preview_with_warnings(self, capsys):
        """Test batch preview with missing SUBPLANs warning."""
        achievements = [
            {"achievement_id": "1.1"},
        ]
        missing_subplans = ["1.2", "1.3"]
        
        show_batch_preview(achievements, "MY-PLAN", missing_subplans)
        
        captured = capsys.readouterr()
        assert "⚠️  WARNING: 2 SUBPLANs missing" in captured.out
        assert "Achievement 1.2" in captured.out
        assert "Achievement 1.3" in captured.out
    
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


class TestExecutionCreation:
    """Tests for EXECUTION file creation."""
    
    def test_create_execution_file(self, tmp_path):
        """Test creating a single EXECUTION file."""
        # Create plan structure
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        
        # Create EXECUTION
        execution_path = create_execution_file(plan_dir, "1.1", {})
        
        assert execution_path.exists()
        assert execution_path.name == "EXECUTION_TASK_MY-PLAN_11_01.md"
        
        content = execution_path.read_text()
        assert "# EXECUTION_TASK: Achievement 1.1" in content
        assert "**PLAN**: MY-PLAN" in content
        assert "**SUBPLAN**: SUBPLAN_MY-PLAN_11.md" in content


class TestBatchCreation:
    """Tests for batch EXECUTION creation."""
    
    def test_batch_create_executions_no_parallel_json(self, tmp_path):
        """Test batch creation with no parallel.json."""
        # Create plan structure without parallel.json
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        
        result = batch_create_executions(plan_dir, dry_run=False)
        
        assert len(result.created) == 0
        assert len(result.errors) == 1
        assert "parallel.json not found" in result.errors[0][1]
    
    def test_batch_create_executions_missing_subplans(self, tmp_path, capsys):
        """Test batch creation with missing SUBPLANs (blocks creation)."""
        # Create plan structure without SUBPLANs
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        (plan_dir / "subplans").mkdir()
        
        # Create parallel.json
        parallel_data = {
            "parallelization_level": "level_1",
            "achievements": [
                {"achievement_id": "1.1", "dependencies": []},
                {"achievement_id": "1.2", "dependencies": []},
            ]
        }
        (plan_dir / "parallel.json").write_text(json.dumps(parallel_data))
        
        result = batch_create_executions(plan_dir, dry_run=False)
        
        # Should block creation due to missing SUBPLANs
        assert len(result.created) == 0
        assert len(result.missing_subplans) == 2
        assert "1.1" in result.missing_subplans
        assert "1.2" in result.missing_subplans
        
        captured = capsys.readouterr()
        assert "Missing 2 SUBPLANs" in captured.out
    
    def test_batch_create_executions_dry_run(self, tmp_path, capsys):
        """Test batch creation in dry-run mode."""
        # Create plan structure with SUBPLANs
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        subplans_dir = plan_dir / "subplans"
        subplans_dir.mkdir()
        (subplans_dir / "SUBPLAN_MY-PLAN_11.md").write_text("# SUBPLAN 1.1")
        (subplans_dir / "SUBPLAN_MY-PLAN_12.md").write_text("# SUBPLAN 1.2")
        
        # Create parallel.json
        parallel_data = {
            "parallelization_level": "level_1",
            "achievements": [
                {"achievement_id": "1.1", "dependencies": []},
                {"achievement_id": "1.2", "dependencies": []},
            ]
        }
        (plan_dir / "parallel.json").write_text(json.dumps(parallel_data))
        
        result = batch_create_executions(plan_dir, dry_run=True)
        
        # Dry-run should not create files
        assert len(result.created) == 0
        assert not (plan_dir / "execution" / "EXECUTION_TASK_MY-PLAN_11_01.md").exists()
        
        captured = capsys.readouterr()
        assert "DRY-RUN MODE" in captured.out
    
    @patch('builtins.input', return_value='n')
    def test_batch_create_executions_cancelled(self, mock_input, tmp_path):
        """Test batch creation cancelled by user."""
        # Create plan structure with SUBPLANs
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        subplans_dir = plan_dir / "subplans"
        subplans_dir.mkdir()
        (subplans_dir / "SUBPLAN_MY-PLAN_11.md").write_text("# SUBPLAN 1.1")
        
        # Create parallel.json
        parallel_data = {
            "parallelization_level": "level_1",
            "achievements": [
                {"achievement_id": "1.1", "dependencies": []},
            ]
        }
        (plan_dir / "parallel.json").write_text(json.dumps(parallel_data))
        
        result = batch_create_executions(plan_dir, dry_run=False)
        
        # Should not create files if cancelled
        assert len(result.created) == 0
    
    @patch('builtins.input', return_value='y')
    def test_batch_create_executions_success(self, mock_input, tmp_path):
        """Test successful batch creation."""
        # Create plan structure with SUBPLANs
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        subplans_dir = plan_dir / "subplans"
        subplans_dir.mkdir()
        (subplans_dir / "SUBPLAN_MY-PLAN_11.md").write_text("# SUBPLAN 1.1")
        (subplans_dir / "SUBPLAN_MY-PLAN_12.md").write_text("# SUBPLAN 1.2")
        
        # Create parallel.json
        parallel_data = {
            "parallelization_level": "level_1",
            "achievements": [
                {"achievement_id": "1.1", "dependencies": []},
                {"achievement_id": "1.2", "dependencies": []},
            ]
        }
        (plan_dir / "parallel.json").write_text(json.dumps(parallel_data))
        
        result = batch_create_executions(plan_dir, dry_run=False)
        
        # Should create 2 EXECUTION_TASKs
        assert len(result.created) == 2
        assert (plan_dir / "execution" / "EXECUTION_TASK_MY-PLAN_11_01.md").exists()
        assert (plan_dir / "execution" / "EXECUTION_TASK_MY-PLAN_12_01.md").exists()
    
    @patch('builtins.input', return_value='y')
    def test_batch_create_executions_skip_existing(self, mock_input, tmp_path):
        """Test skipping existing EXECUTION_TASKs."""
        # Create plan structure with SUBPLANs
        plan_dir = tmp_path / "MY-PLAN"
        plan_dir.mkdir()
        (plan_dir / "PLAN_MY-PLAN.md").write_text("# PLAN")
        subplans_dir = plan_dir / "subplans"
        subplans_dir.mkdir()
        (subplans_dir / "SUBPLAN_MY-PLAN_11.md").write_text("# SUBPLAN 1.1")
        (subplans_dir / "SUBPLAN_MY-PLAN_12.md").write_text("# SUBPLAN 1.2")
        
        execution_dir = plan_dir / "execution"
        execution_dir.mkdir()
        
        # Create one existing EXECUTION_TASK
        (execution_dir / "EXECUTION_TASK_MY-PLAN_11_01.md").write_text("# Existing")
        
        # Create parallel.json
        parallel_data = {
            "parallelization_level": "level_1",
            "achievements": [
                {"achievement_id": "1.1", "dependencies": []},
                {"achievement_id": "1.2", "dependencies": []},
            ]
        }
        (plan_dir / "parallel.json").write_text(json.dumps(parallel_data))
        
        result = batch_create_executions(plan_dir, dry_run=False)
        
        # Should create 1 EXECUTION_TASK and skip 1
        assert len(result.created) == 1
        assert len(result.skipped) == 1
        assert result.skipped[0] == "1.1"


