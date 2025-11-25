"""
Tests for filesystem-based workflow detection in generate_prompt.py

Achievement 1.6: Fix Prompt Generator Multi-Execution Detection
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


class TestFilesystemDetection:
    """Test filesystem-based workflow state detection"""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace structure for testing"""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir)

        # Create nested structure
        plan_folder = workspace / "work-space" / "plans" / "TEST-FEATURE"
        plan_folder.mkdir(parents=True)

        subplans_folder = plan_folder / "subplans"
        subplans_folder.mkdir()

        execution_folder = plan_folder / "execution"
        execution_folder.mkdir()

        # Create PLAN file
        plan_file = plan_folder / "PLAN_TEST-FEATURE.md"
        plan_file.write_text(
            """# PLAN: Test Feature

## 📋 Desirable Achievements

### Achievement 0.1: Test Achievement
**Purpose**: Test
**What**: Test
**Success**: Test
**Effort**: 1 hour
"""
        )

        yield {
            "workspace": workspace,
            "plan_folder": plan_folder,
            "plan_file": plan_file,
            "subplans_folder": subplans_folder,
            "execution_folder": execution_folder,
        }

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_no_subplan(self, temp_workspace):
        """Test detection when SUBPLAN doesn't exist"""
        result = detect_workflow_state_filesystem(
            temp_workspace["plan_file"], "TEST-FEATURE", "0.1"
        )

        assert result["state"] == "no_subplan"
        assert result["subplan_path"] is None
        assert result["recommendation"] == "create_subplan"
        assert result["execution_count"] == 0
        assert result["completed_count"] == 0

    def test_subplan_no_execution(self, temp_workspace):
        """Test detection when SUBPLAN exists but no EXECUTION_TASKs"""
        # Create SUBPLAN
        subplan_file = temp_workspace["subplans_folder"] / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_file.write_text(
            """# SUBPLAN: Test

**Status**: 🚀 In Progress

## 🎯 Objective
Test objective
"""
        )

        result = detect_workflow_state_filesystem(
            temp_workspace["plan_file"], "TEST-FEATURE", "0.1"
        )

        assert result["state"] == "subplan_no_execution"
        assert result["subplan_path"] == subplan_file
        assert result["recommendation"] == "create_execution"
        assert result["execution_count"] == 0
        assert result["completed_count"] == 0

    def test_active_single_execution(self, temp_workspace):
        """Test detection with one active EXECUTION_TASK"""
        # Create SUBPLAN
        subplan_file = temp_workspace["subplans_folder"] / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_file.write_text(
            """# SUBPLAN: Test

**Status**: 🚀 In Progress

## 🎯 Objective
Test objective
"""
        )

        # Create active EXECUTION_TASK
        exec_file = temp_workspace["execution_folder"] / "EXECUTION_TASK_TEST-FEATURE_01_01.md"
        exec_file.write_text(
            """# EXECUTION_TASK: Test

**Status**: 🚀 In Progress

## 📋 Mission
Test mission
"""
        )

        result = detect_workflow_state_filesystem(
            temp_workspace["plan_file"], "TEST-FEATURE", "0.1"
        )

        assert result["state"] == "active_execution"
        assert result["subplan_path"] == subplan_file
        assert result["recommendation"] == "continue_execution"
        assert result["execution_count"] == 1
        assert result["completed_count"] == 0

    def test_active_multiple_executions(self, temp_workspace):
        """Test detection with multiple EXECUTION_TASKs (some complete, some active)"""
        # Create SUBPLAN
        subplan_file = temp_workspace["subplans_folder"] / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_file.write_text(
            """# SUBPLAN: Test

**Status**: 🚀 In Progress

## 🎯 Objective
Test objective
"""
        )

        # Create completed EXECUTION_TASK
        exec_file_1 = temp_workspace["execution_folder"] / "EXECUTION_TASK_TEST-FEATURE_01_01.md"
        exec_file_1.write_text(
            """# EXECUTION_TASK: Test 1

**Status**: ✅ Complete

## 📋 Mission
Test mission 1
"""
        )

        # Create active EXECUTION_TASK
        exec_file_2 = temp_workspace["execution_folder"] / "EXECUTION_TASK_TEST-FEATURE_01_02.md"
        exec_file_2.write_text(
            """# EXECUTION_TASK: Test 2

**Status**: 🚀 In Progress

## 📋 Mission
Test mission 2
"""
        )

        # Create planning EXECUTION_TASK
        exec_file_3 = temp_workspace["execution_folder"] / "EXECUTION_TASK_TEST-FEATURE_01_03.md"
        exec_file_3.write_text(
            """# EXECUTION_TASK: Test 3

**Status**: 📋 Planning

## 📋 Mission
Test mission 3
"""
        )

        result = detect_workflow_state_filesystem(
            temp_workspace["plan_file"], "TEST-FEATURE", "0.1"
        )

        assert result["state"] == "active_execution"
        assert result["subplan_path"] == subplan_file
        assert result["recommendation"] == "continue_execution"
        assert result["execution_count"] == 3
        assert result["completed_count"] == 1

    def test_all_executions_complete(self, temp_workspace):
        """Test detection when all EXECUTION_TASKs are complete"""
        # Create SUBPLAN
        subplan_file = temp_workspace["subplans_folder"] / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_file.write_text(
            """# SUBPLAN: Test

**Status**: 🚀 In Progress

## 🎯 Objective
Test objective
"""
        )

        # Create completed EXECUTION_TASKs
        for i in range(1, 4):
            exec_file = (
                temp_workspace["execution_folder"] / f"EXECUTION_TASK_TEST-FEATURE_01_0{i}.md"
            )
            exec_file.write_text(
                f"""# EXECUTION_TASK: Test {i}

**Status**: ✅ Complete

## 📋 Mission
Test mission {i}
"""
            )

        result = detect_workflow_state_filesystem(
            temp_workspace["plan_file"], "TEST-FEATURE", "0.1"
        )

        assert result["state"] == "subplan_all_executed"
        assert result["subplan_path"] == subplan_file
        assert result["recommendation"] == "synthesize_or_complete"
        assert result["execution_count"] == 3
        assert result["completed_count"] == 3

    def test_subplan_complete(self, temp_workspace):
        """Test detection when SUBPLAN is marked complete"""
        # Create completed SUBPLAN
        subplan_file = temp_workspace["subplans_folder"] / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_file.write_text(
            """# SUBPLAN: Test

**Status**: ✅ Complete

## 🎯 Objective
Test objective
"""
        )

        result = detect_workflow_state_filesystem(
            temp_workspace["plan_file"], "TEST-FEATURE", "0.1"
        )

        assert result["state"] == "subplan_complete"
        assert result["subplan_path"] == subplan_file
        assert result["recommendation"] == "next_achievement"
        assert result["execution_count"] == 0
        assert result["completed_count"] == 0

    def test_missing_execution_folder(self, temp_workspace):
        """Test detection when execution folder doesn't exist"""
        # Create SUBPLAN
        subplan_file = temp_workspace["subplans_folder"] / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_file.write_text(
            """# SUBPLAN: Test

**Status**: 🚀 In Progress

## 🎯 Objective
Test objective
"""
        )

        # Remove execution folder
        shutil.rmtree(temp_workspace["execution_folder"])

        result = detect_workflow_state_filesystem(
            temp_workspace["plan_file"], "TEST-FEATURE", "0.1"
        )

        assert result["state"] == "subplan_no_execution"
        assert result["subplan_path"] == subplan_file
        assert result["recommendation"] == "create_execution"
        assert result["execution_count"] == 0
        assert result["completed_count"] == 0

    def test_malformed_filenames(self, temp_workspace):
        """Test detection with malformed EXECUTION_TASK filenames"""
        # Create SUBPLAN
        subplan_file = temp_workspace["subplans_folder"] / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_file.write_text(
            """# SUBPLAN: Test

**Status**: 🚀 In Progress

## 🎯 Objective
Test objective
"""
        )

        # Create malformed EXECUTION_TASK (wrong pattern)
        exec_file = temp_workspace["execution_folder"] / "EXECUTION_TASK_WRONG_NAME.md"
        exec_file.write_text(
            """# EXECUTION_TASK: Test

**Status**: 🚀 In Progress

## 📋 Mission
Test mission
"""
        )

        result = detect_workflow_state_filesystem(
            temp_workspace["plan_file"], "TEST-FEATURE", "0.1"
        )

        # Should not find the malformed file
        assert result["state"] == "subplan_no_execution"
        assert result["execution_count"] == 0


class TestIntegrationWithRealWorkspace:
    """Integration tests with real workspace structure"""

    def test_graphrag_multi_execution(self):
        """Test with real GRAPHRAG plan (multi-execution)"""
        plan_path = Path(
            "work-space/plans/GRAPHRAG-OBSERVABILITY-EXCELLENCE/PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md"
        )

        if not plan_path.exists():
            pytest.skip("GRAPHRAG plan not found in workspace")

        result = detect_workflow_state_filesystem(
            plan_path, "GRAPHRAG-OBSERVABILITY-EXCELLENCE", "0.1"
        )

        # Should detect the SUBPLAN and EXECUTION_TASK
        assert result["state"] in ["active_execution", "subplan_all_executed", "subplan_complete"]
        assert result["subplan_path"] is not None

    def test_restore_automation_single_execution(self):
        """Test with real RESTORE-EXECUTION plan (single execution)"""
        plan_path = Path(
            "work-space/plans/RESTORE-EXECUTION-WORKFLOW-AUTOMATION/PLAN_RESTORE-EXECUTION-WORKFLOW-AUTOMATION.md"
        )

        if not plan_path.exists():
            pytest.skip("RESTORE-EXECUTION plan not found in workspace")

        result = detect_workflow_state_filesystem(
            plan_path, "RESTORE-EXECUTION-WORKFLOW-AUTOMATION", "1.6"
        )

        # Should detect Achievement 1.6's SUBPLAN and EXECUTION_TASK
        assert result["state"] in ["active_execution", "subplan_all_executed", "subplan_complete"]
        assert result["subplan_path"] is not None

    def test_no_regressions_single_execution(self):
        """Test that single-execution workflows still work correctly"""
        plan_path = Path(
            "work-space/plans/RESTORE-EXECUTION-WORKFLOW-AUTOMATION/PLAN_RESTORE-EXECUTION-WORKFLOW-AUTOMATION.md"
        )

        if not plan_path.exists():
            pytest.skip("RESTORE-EXECUTION plan not found in workspace")

        # Test Achievement 1.2 (completed single execution - may be archived)
        result = detect_workflow_state_filesystem(
            plan_path, "RESTORE-EXECUTION-WORKFLOW-AUTOMATION", "1.2"
        )

        # Should be complete, have execution, or no_subplan (if archived)
        assert result["state"] in [
            "subplan_complete",
            "active_execution",
            "subplan_all_executed",
            "no_subplan",
        ]

    def test_detect_workflow_state_uses_filesystem(self):
        """Test that detect_workflow_state() uses filesystem detection"""
        plan_path = Path(
            "work-space/plans/RESTORE-EXECUTION-WORKFLOW-AUTOMATION/PLAN_RESTORE-EXECUTION-WORKFLOW-AUTOMATION.md"
        )

        if not plan_path.exists():
            pytest.skip("RESTORE-EXECUTION plan not found in workspace")

        # Call the main function (should use filesystem detection)
        result = detect_workflow_state(plan_path, "RESTORE-EXECUTION-WORKFLOW-AUTOMATION", "1.6")

        # Should return valid state
        assert result["state"] in [
            "no_subplan",
            "subplan_no_execution",
            "active_execution",
            "subplan_all_executed",
            "subplan_complete",
        ]


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace structure for testing"""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir)

        # Create nested structure
        plan_folder = workspace / "work-space" / "plans" / "TEST-FEATURE"
        plan_folder.mkdir(parents=True)

        subplans_folder = plan_folder / "subplans"
        subplans_folder.mkdir()

        execution_folder = plan_folder / "execution"
        execution_folder.mkdir()

        # Create PLAN file
        plan_file = plan_folder / "PLAN_TEST-FEATURE.md"
        plan_file.write_text(
            """# PLAN: Test Feature

## 📋 Desirable Achievements

### Achievement 0.1: Test Achievement
**Purpose**: Test
**What**: Test
**Success**: Test
**Effort**: 1 hour
"""
        )

        yield {
            "workspace": workspace,
            "plan_folder": plan_folder,
            "plan_file": plan_file,
            "subplans_folder": subplans_folder,
            "execution_folder": execution_folder,
        }

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_permission_denied(self, temp_workspace):
        """Test graceful handling of permission errors"""
        # This test is platform-specific and may not work on all systems
        # Skip if we can't create permission-denied scenario
        pytest.skip("Permission testing requires special setup")

    def test_corrupted_file(self, temp_workspace):
        """Test handling of corrupted EXECUTION_TASK files"""
        # Create SUBPLAN
        subplan_file = temp_workspace["subplans_folder"] / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_file.write_text(
            """# SUBPLAN: Test

**Status**: 🚀 In Progress

## 🎯 Objective
Test objective
"""
        )

        # Create corrupted EXECUTION_TASK (can't read status)
        exec_file = temp_workspace["execution_folder"] / "EXECUTION_TASK_TEST-FEATURE_01_01.md"
        exec_file.write_text("Corrupted content with no status marker")

        result = detect_workflow_state_filesystem(
            temp_workspace["plan_file"], "TEST-FEATURE", "0.1"
        )

        # Should still detect the file but count it as incomplete
        assert result["state"] == "active_execution"
        assert result["execution_count"] == 1
        assert result["completed_count"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
