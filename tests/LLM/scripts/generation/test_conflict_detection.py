"""
Test Conflict Detection - Phase 3 of Achievement 1.3

Tests for detect_plan_filesystem_conflict() covering all 3 conflict types:
1. plan_outdated_complete: Filesystem shows complete, PLAN says next
2. plan_outdated_synthesis: All EXECUTIONs complete, PLAN not updated
3. plan_premature_complete: PLAN says complete, work still active
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from LLM.scripts.generation.generate_prompt import detect_plan_filesystem_conflict


class TestDetectPlanFilesystemConflict:
    """Test conflict detection between PLAN and filesystem."""

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

    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_conflict_type_1_plan_outdated_complete(self):
        """Test Conflict Type 1: SUBPLAN complete but PLAN says next."""
        # Create completed SUBPLAN
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text(
            "# SUBPLAN: TEST-FEATURE 0.1\n**Status**: ✅ Complete\n"
        )
        
        # PLAN says achievement is next (not complete)
        plan_content = """# PLAN: TEST-FEATURE

## Current Status & Handoff

Next: Achievement 0.1 (Setup)

## Achievements

### Achievement 0.1: Setup ⏳
Status: In Progress
"""
        self.plan_path.write_text(plan_content)
        
        result = detect_plan_filesystem_conflict(
            self.plan_path, "TEST-FEATURE", "0.1", plan_content
        )
        
        assert result is not None
        assert result["has_conflict"] is True
        assert result["achievement_num"] == "0.1"
        assert len(result["conflicts"]) == 1
        assert result["conflicts"][0]["type"] == "plan_outdated_complete"
        assert "marked COMPLETE in filesystem" in result["conflicts"][0]["message"]

    def test_conflict_type_2_plan_outdated_synthesis(self):
        """Test Conflict Type 2: All EXECUTIONs complete but PLAN not updated."""
        # Create SUBPLAN (not marked complete)
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text(
            "# SUBPLAN: TEST-FEATURE 0.1\n**Status**: ⏳ In Progress\n"
        )
        
        # Create completed EXECUTION
        exec_path = self.execution_dir / "EXECUTION_TASK_TEST-FEATURE_01_01.md"
        exec_path.write_text(
            "# EXECUTION_TASK\n**Status**: ✅ Complete\n"
        )
        
        # PLAN says achievement is next (not complete)
        plan_content = """# PLAN: TEST-FEATURE

## Current Status & Handoff

Next: Achievement 0.1 (Setup)

## Achievements

### Achievement 0.1: Setup ⏳
Status: In Progress
"""
        self.plan_path.write_text(plan_content)
        
        result = detect_plan_filesystem_conflict(
            self.plan_path, "TEST-FEATURE", "0.1", plan_content
        )
        
        assert result is not None
        assert result["has_conflict"] is True
        assert len(result["conflicts"]) == 1
        assert result["conflicts"][0]["type"] == "plan_outdated_synthesis"
        assert "all executions complete" in result["conflicts"][0]["message"]

    def test_conflict_type_3_plan_premature_complete(self):
        """Test Conflict Type 3: PLAN says complete but work still active."""
        # Create SUBPLAN (in progress)
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text(
            "# SUBPLAN: TEST-FEATURE 0.1\n**Status**: ⏳ In Progress\n"
        )
        
        # Create in-progress EXECUTION
        exec_path = self.execution_dir / "EXECUTION_TASK_TEST-FEATURE_01_01.md"
        exec_path.write_text(
            "# EXECUTION_TASK\n**Status**: ⏳ In Progress\n"
        )
        
        # PLAN says achievement is complete
        plan_content = """# PLAN: TEST-FEATURE

## Current Status & Handoff

✅ Achievement 0.1 complete

## Achievements

### Achievement 0.1: Setup ✅
Status: Complete
"""
        self.plan_path.write_text(plan_content)
        
        result = detect_plan_filesystem_conflict(
            self.plan_path, "TEST-FEATURE", "0.1", plan_content
        )
        
        assert result is not None
        assert result["has_conflict"] is True
        assert len(result["conflicts"]) == 1
        assert result["conflicts"][0]["type"] == "plan_premature_complete"
        assert "marked COMPLETE in PLAN but work is still active" in result["conflicts"][0]["message"]

    def test_no_conflict_when_synchronized(self):
        """Test no conflict when PLAN and filesystem are synchronized."""
        # Create in-progress SUBPLAN
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text(
            "# SUBPLAN: TEST-FEATURE 0.1\n**Status**: ⏳ In Progress\n"
        )
        
        # Create in-progress EXECUTION
        exec_path = self.execution_dir / "EXECUTION_TASK_TEST-FEATURE_01_01.md"
        exec_path.write_text(
            "# EXECUTION_TASK\n**Status**: ⏳ In Progress\n"
        )
        
        # PLAN says achievement is next (matches filesystem)
        plan_content = """# PLAN: TEST-FEATURE

## Current Status & Handoff

Next: Achievement 0.1 (Setup)

## Achievements

### Achievement 0.1: Setup ⏳
Status: In Progress
"""
        self.plan_path.write_text(plan_content)
        
        result = detect_plan_filesystem_conflict(
            self.plan_path, "TEST-FEATURE", "0.1", plan_content
        )
        
        # Should return None when no conflict
        assert result is None

    def test_no_conflict_when_both_complete(self):
        """Test no conflict when both PLAN and filesystem show complete."""
        # Create completed SUBPLAN
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text(
            "# SUBPLAN: TEST-FEATURE 0.1\n**Status**: ✅ Complete\n"
        )
        
        # PLAN says achievement is complete
        plan_content = """# PLAN: TEST-FEATURE

## Current Status & Handoff

✅ Achievement 0.1 complete

## Achievements

### Achievement 0.1: Setup ✅
Status: Complete
"""
        self.plan_path.write_text(plan_content)
        
        result = detect_plan_filesystem_conflict(
            self.plan_path, "TEST-FEATURE", "0.1", plan_content
        )
        
        # Should return None when both agree
        assert result is None

    def test_conflict_includes_filesystem_state(self):
        """Test that conflict result includes filesystem state details."""
        # Create completed SUBPLAN
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text(
            "# SUBPLAN: TEST-FEATURE 0.1\n**Status**: ✅ Complete\n"
        )
        
        # PLAN says achievement is next
        plan_content = """# PLAN: TEST-FEATURE

## Current Status & Handoff

Next: Achievement 0.1 (Setup)
"""
        self.plan_path.write_text(plan_content)
        
        result = detect_plan_filesystem_conflict(
            self.plan_path, "TEST-FEATURE", "0.1", plan_content
        )
        
        assert result is not None
        assert "filesystem_state" in result
        assert result["filesystem_state"]["state"] == "subplan_complete"

    def test_conflict_with_multi_execution_workflow(self):
        """Test conflict detection in multi-execution workflow."""
        # Create SUBPLAN with multi-execution plan
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_content = """# SUBPLAN: TEST-FEATURE 0.1
**Status**: ⏳ In Progress

## 🔄 Active EXECUTION_TASKs

| Execution | Status | Description |
|-----------|--------|-------------|
| 01_01     | ✅ Complete | First |
| 01_02     | ✅ Complete | Second |
"""
        subplan_path.write_text(subplan_content)
        
        # Create 2 completed EXECUTIONs
        exec1_path = self.execution_dir / "EXECUTION_TASK_TEST-FEATURE_01_01.md"
        exec1_path.write_text("# EXECUTION_TASK\n**Status**: ✅ Complete\n")
        
        exec2_path = self.execution_dir / "EXECUTION_TASK_TEST-FEATURE_01_02.md"
        exec2_path.write_text("# EXECUTION_TASK\n**Status**: ✅ Complete\n")
        
        # PLAN says achievement is next (not updated)
        plan_content = """# PLAN: TEST-FEATURE

## Current Status & Handoff

Next: Achievement 0.1 (Setup)
"""
        self.plan_path.write_text(plan_content)
        
        result = detect_plan_filesystem_conflict(
            self.plan_path, "TEST-FEATURE", "0.1", plan_content
        )
        
        assert result is not None
        assert result["has_conflict"] is True
        assert result["conflicts"][0]["type"] == "plan_outdated_synthesis"
        # Should show execution count
        assert "2/2" in result["conflicts"][0]["message"]

    def test_no_conflict_when_no_subplan(self):
        """Test no conflict when SUBPLAN doesn't exist yet."""
        # No SUBPLAN created
        
        # PLAN says achievement is next
        plan_content = """# PLAN: TEST-FEATURE

## Current Status & Handoff

Next: Achievement 0.1 (Setup)
"""
        self.plan_path.write_text(plan_content)
        
        result = detect_plan_filesystem_conflict(
            self.plan_path, "TEST-FEATURE", "0.1", plan_content
        )
        
        # Should return None when no SUBPLAN (nothing to conflict with)
        assert result is None

    def test_conflict_provides_resolution_guidance(self):
        """Test that conflict includes likely cause and resolution guidance."""
        # Create completed SUBPLAN
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text(
            "# SUBPLAN: TEST-FEATURE 0.1\n**Status**: ✅ Complete\n"
        )
        
        # PLAN says achievement is next
        plan_content = """# PLAN: TEST-FEATURE

## Current Status & Handoff

Next: Achievement 0.1 (Setup)
"""
        self.plan_path.write_text(plan_content)
        
        result = detect_plan_filesystem_conflict(
            self.plan_path, "TEST-FEATURE", "0.1", plan_content
        )
        
        assert result is not None
        conflict = result["conflicts"][0]
        assert "likely_cause" in conflict
        assert "filesystem" in conflict
        assert "plan" in conflict
        assert "PLAN was not updated" in conflict["likely_cause"]

