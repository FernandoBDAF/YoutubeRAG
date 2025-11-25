"""
Test Workflow Detection - Phase 1 of Achievement 1.3

Tests for detect_workflow_state_filesystem() and detect_workflow_state()
covering all 7 workflow states and filesystem-based detection logic.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from LLM.scripts.generation.workflow_detector import WorkflowDetector
from LLM.scripts.generation.generate_prompt import detect_workflow_state

# Create detector instance for tests
detector = WorkflowDetector()
detect_workflow_state_filesystem = detector.detect_workflow_state_filesystem


class TestDetectWorkflowStateFilesystem:
    """Test filesystem-based workflow state detection (7 states)."""

    def setup_method(self):
        """Create temporary directory structure for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.plan_dir = Path(self.temp_dir) / "TEST-FEATURE"
        self.plan_dir.mkdir(parents=True)
        self.subplan_dir = self.plan_dir / "subplans"
        self.subplan_dir.mkdir()
        self.execution_dir = self.plan_dir / "execution"
        self.execution_dir.mkdir()

        # Create PLAN file
        self.plan_path = self.plan_dir / "PLAN_TEST-FEATURE.md"
        self.plan_path.write_text("# PLAN: TEST-FEATURE\n")

    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_state_1_no_subplan(self):
        """Test State 1: no_subplan - SUBPLAN doesn't exist."""
        result = detect_workflow_state_filesystem(self.plan_path, "TEST-FEATURE", "0.1")

        assert result["state"] == "no_subplan"
        assert result["subplan_path"] is None
        assert result["recommendation"] == "create_subplan"
        assert result["execution_count"] == 0
        assert result["completed_count"] == 0

    def test_state_2_subplan_no_execution(self):
        """Test State 2: subplan_no_execution - SUBPLAN exists, no EXECUTION files."""
        # Create SUBPLAN
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text("# SUBPLAN: TEST-FEATURE 0.1\n**Status**: ⏳ In Progress\n")

        result = detect_workflow_state_filesystem(self.plan_path, "TEST-FEATURE", "0.1")

        assert result["state"] == "subplan_no_execution"
        assert result["subplan_path"] == subplan_path
        assert result["recommendation"] == "create_execution"
        assert result["execution_count"] == 0
        assert result["completed_count"] == 0

    def test_state_3_active_execution_continue(self):
        """Test State 3: active_execution - EXECUTION in progress (continue)."""
        # Create SUBPLAN
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text("# SUBPLAN: TEST-FEATURE 0.1\n**Status**: ⏳ In Progress\n")

        # Create incomplete EXECUTION
        exec_path = self.execution_dir / "EXECUTION_TASK_TEST-FEATURE_01_01.md"
        exec_path.write_text("# EXECUTION_TASK\n**Status**: ⏳ In Progress\n")

        result = detect_workflow_state_filesystem(self.plan_path, "TEST-FEATURE", "0.1")

        assert result["state"] == "active_execution"
        assert result["subplan_path"] == subplan_path
        assert result["recommendation"] == "continue_execution"
        assert result["execution_count"] == 1
        assert result["completed_count"] == 0

    def test_state_4_create_next_execution(self):
        """Test State 4: active_execution - Need to create next EXECUTION (multi-execution)."""
        # Create SUBPLAN with multi-execution plan
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_content = """# SUBPLAN: TEST-FEATURE 0.1
**Status**: ⏳ In Progress

## 🔄 Active EXECUTION_TASKs

| Execution | Status | Description |
|-----------|--------|-------------|
| 01_01     | ✅ Complete | First execution |
| 01_02     | ⏳ Pending | Second execution |
"""
        subplan_path.write_text(subplan_content)

        # Create completed EXECUTION
        exec1_path = self.execution_dir / "EXECUTION_TASK_TEST-FEATURE_01_01.md"
        exec1_path.write_text("# EXECUTION_TASK\n**Status**: ✅ Complete\n")

        result = detect_workflow_state_filesystem(self.plan_path, "TEST-FEATURE", "0.1")

        assert result["state"] == "active_execution"
        assert result["subplan_path"] == subplan_path
        assert result["recommendation"] == "create_next_execution"
        assert result["execution_count"] == 2  # From SUBPLAN table
        assert result["completed_count"] == 1

    def test_state_5_subplan_all_executed(self):
        """Test State 5: subplan_all_executed - All EXECUTIONs complete."""
        # Create SUBPLAN
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text("# SUBPLAN: TEST-FEATURE 0.1\n**Status**: ⏳ In Progress\n")

        # Create completed EXECUTION
        exec_path = self.execution_dir / "EXECUTION_TASK_TEST-FEATURE_01_01.md"
        exec_path.write_text("# EXECUTION_TASK\n**Status**: ✅ Complete\n")

        result = detect_workflow_state_filesystem(self.plan_path, "TEST-FEATURE", "0.1")

        assert result["state"] == "subplan_all_executed"
        assert result["subplan_path"] == subplan_path
        assert result["recommendation"] == "synthesize_or_complete"
        assert result["execution_count"] == 1
        assert result["completed_count"] == 1

    def test_state_6_subplan_complete(self):
        """Test State 6: subplan_complete - SUBPLAN marked complete."""
        # Create completed SUBPLAN
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text("# SUBPLAN: TEST-FEATURE 0.1\n**Status**: ✅ Complete\n")

        result = detect_workflow_state_filesystem(self.plan_path, "TEST-FEATURE", "0.1")

        assert result["state"] == "subplan_complete"
        assert result["subplan_path"] == subplan_path
        assert result["recommendation"] == "next_achievement"
        assert result["execution_count"] == 0
        assert result["completed_count"] == 0

    def test_handles_v2_execution_files(self):
        """Test that detection handles _V2 and other filename variations."""
        # Create SUBPLAN
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text("# SUBPLAN: TEST-FEATURE 0.1\n**Status**: ⏳ In Progress\n")

        # Create V2 EXECUTION file
        exec_path = self.execution_dir / "EXECUTION_TASK_TEST-FEATURE_01_01_V2.md"
        exec_path.write_text("# EXECUTION_TASK\n**Status**: ⏳ In Progress\n")

        result = detect_workflow_state_filesystem(self.plan_path, "TEST-FEATURE", "0.1")

        # Should detect the V2 file
        assert result["state"] == "active_execution"
        assert result["execution_count"] == 1

    def test_multi_execution_workflow(self):
        """Test multi-execution workflow with 3 executions."""
        # Create SUBPLAN with 3 executions
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_content = """# SUBPLAN: TEST-FEATURE 0.1
**Status**: ⏳ In Progress

## 🔄 Active EXECUTION_TASKs

| Execution | Status | Description |
|-----------|--------|-------------|
| 01_01     | ✅ Complete | First |
| 01_02     | ✅ Complete | Second |
| 01_03     | ⏳ In Progress | Third |
"""
        subplan_path.write_text(subplan_content)

        # Create 2 completed, 1 in progress
        exec1_path = self.execution_dir / "EXECUTION_TASK_TEST-FEATURE_01_01.md"
        exec1_path.write_text("# EXECUTION_TASK\n**Status**: ✅ Complete\n")

        exec2_path = self.execution_dir / "EXECUTION_TASK_TEST-FEATURE_01_02.md"
        exec2_path.write_text("# EXECUTION_TASK\n**Status**: ✅ Complete\n")

        exec3_path = self.execution_dir / "EXECUTION_TASK_TEST-FEATURE_01_03.md"
        exec3_path.write_text("# EXECUTION_TASK\n**Status**: ⏳ In Progress\n")

        result = detect_workflow_state_filesystem(self.plan_path, "TEST-FEATURE", "0.1")

        assert result["state"] == "active_execution"
        assert result["recommendation"] == "continue_execution"
        assert result["execution_count"] == 3
        assert result["completed_count"] == 2

    def test_no_execution_folder(self):
        """Test when execution folder doesn't exist."""
        # Create SUBPLAN
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text("# SUBPLAN: TEST-FEATURE 0.1\n**Status**: ⏳ In Progress\n")

        # Remove execution folder
        shutil.rmtree(self.execution_dir)

        result = detect_workflow_state_filesystem(self.plan_path, "TEST-FEATURE", "0.1")

        assert result["state"] == "subplan_no_execution"
        assert result["recommendation"] == "create_execution"

    def test_achievement_with_dots(self):
        """Test achievement numbers with dots (e.g., 1.2)."""
        # Create SUBPLAN for achievement 1.2
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_12.md"
        subplan_path.write_text("# SUBPLAN: TEST-FEATURE 1.2\n**Status**: ⏳ In Progress\n")

        result = detect_workflow_state_filesystem(self.plan_path, "TEST-FEATURE", "1.2")

        assert result["state"] == "subplan_no_execution"
        assert result["subplan_path"] == subplan_path


class TestDetectWorkflowState:
    """Test wrapper function that tries filesystem first, then fallback."""

    def setup_method(self):
        """Create temporary directory structure for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.plan_dir = Path(self.temp_dir) / "TEST-FEATURE"
        self.plan_dir.mkdir(parents=True)
        self.subplan_dir = self.plan_dir / "subplans"
        self.subplan_dir.mkdir()

        # Create PLAN file
        self.plan_path = self.plan_dir / "PLAN_TEST-FEATURE.md"
        self.plan_path.write_text("# PLAN: TEST-FEATURE\n")

    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_uses_filesystem_detection(self):
        """Test that wrapper uses filesystem detection successfully."""
        # Create SUBPLAN
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text("# SUBPLAN: TEST-FEATURE 0.1\n**Status**: ⏳ In Progress\n")

        result = detect_workflow_state(self.plan_path, "TEST-FEATURE", "0.1")

        # Should get result from filesystem detection
        assert result["state"] == "subplan_no_execution"
        assert result["subplan_path"] == subplan_path
        assert "recommendation" in result

    def test_returns_dict_with_required_keys(self):
        """Test that result always has required keys."""
        result = detect_workflow_state(self.plan_path, "TEST-FEATURE", "0.1")

        # Check required keys
        assert "state" in result
        assert "subplan_path" in result
        assert "recommendation" in result
        assert isinstance(result["state"], str)
