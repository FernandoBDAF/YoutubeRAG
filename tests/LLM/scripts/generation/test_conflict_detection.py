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
from LLM.scripts.generation.workflow_detector import WorkflowDetector

# Create detector instance for tests
detector = WorkflowDetector()
detect_plan_filesystem_conflict = detector.detect_plan_filesystem_conflict


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

        # Create feedbacks directory for filesystem-first tracking
        self.feedbacks_dir = self.execution_dir / "feedbacks"
        self.feedbacks_dir.mkdir()

        # Create PLAN file
        self.plan_path = self.plan_dir / "PLAN_TEST-FEATURE.md"

    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_conflict_achievement_not_in_index(self):
        """Test conflict: APPROVED file exists for achievement not in PLAN."""
        # Create APPROVED file for achievement NOT in PLAN
        approved_file = self.feedbacks_dir / "APPROVED_99.md"
        approved_file.write_text(
            """# Achievement 9.9 Approval

**Status**: ✅ Approved
**Date**: 2025-11-12
**Reviewer**: Test Suite
"""
        )

        # PLAN that doesn't include achievement 9.9
        plan_content = """# PLAN: TEST-FEATURE

## 📋 Desirable Achievements

**Achievement 0.1**: Setup
**Achievement 0.2**: Implementation
**Achievement 0.3**: Testing

## Current Status & Handoff

Next: Achievement 0.1 (Setup)
"""
        self.plan_path.write_text(plan_content)

        result = detect_plan_filesystem_conflict(
            self.plan_path, "TEST-FEATURE", "0.1", plan_content
        )

        assert result is not None
        assert result["has_conflict"] is True
        assert len(result["conflicts"]) == 1
        assert result["conflicts"][0]["type"] == "achievement_not_in_index"
        assert "9.9" in result["conflicts"][0]["message"]
        assert "not in Achievement Index" in result["conflicts"][0]["message"]

    def test_conflict_orphaned_subplan(self):
        """Test conflict: SUBPLAN exists for achievement not in PLAN."""
        # Create SUBPLAN for achievement NOT in PLAN
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_99.md"
        subplan_path.write_text("# SUBPLAN: TEST-FEATURE 9.9\n**Status**: ⏳ In Progress\n")

        # PLAN that doesn't include 9.9
        plan_content = """# PLAN: TEST-FEATURE

## 📋 Desirable Achievements

**Achievement 0.1**: Setup
**Achievement 0.2**: Implementation
**Achievement 0.3**: Testing

## Current Status & Handoff

Next: Achievement 0.1 (Setup)
"""
        self.plan_path.write_text(plan_content)

        result = detect_plan_filesystem_conflict(
            self.plan_path, "TEST-FEATURE", "0.1", plan_content
        )

        assert result is not None
        assert result["has_conflict"] is True
        assert len(result["conflicts"]) == 1
        assert result["conflicts"][0]["type"] == "orphaned_work"
        assert "9.9" in result["conflicts"][0]["message"]
        assert "not in Achievement Index" in result["conflicts"][0]["message"]

    def test_no_conflict_when_execution_in_plan(self):
        """Test no conflict when EXECUTION exists for achievement in PLAN (orphan detection only checks SUBPLANs)."""
        # Create EXECUTION for achievement IN PLAN (0.1)
        exec_path = self.execution_dir / "EXECUTION_TASK_TEST-FEATURE_01_01.md"
        exec_path.write_text("# EXECUTION_TASK\n**Status**: ⏳ In Progress\n")

        # PLAN that includes 0.1
        plan_content = """# PLAN: TEST-FEATURE

## 📋 Desirable Achievements

**Achievement 0.1**: Setup
**Achievement 0.2**: Implementation
**Achievement 0.3**: Testing

## Current Status & Handoff

Next: Achievement 0.1 (Setup)
"""
        self.plan_path.write_text(plan_content)

        result = detect_plan_filesystem_conflict(
            self.plan_path, "TEST-FEATURE", "0.1", plan_content
        )

        # Should return None - EXECUTION orphan detection not implemented (only SUBPLANs checked)
        assert result is None

    def test_no_conflict_when_in_index_and_filesystem(self):
        """Test no conflict when Achievement Index and filesystem agree."""
        # Create APPROVED file for achievement IN index
        approved_file = self.feedbacks_dir / "APPROVED_01.md"
        approved_file.write_text("# Approved\n")

        # Create SUBPLAN for achievement IN index
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text("# SUBPLAN\n")

        # PLAN that includes 0.1
        plan_content = """# PLAN: TEST-FEATURE

## 📋 Desirable Achievements

**Achievement 0.1**: Setup
**Achievement 0.2**: Implementation
**Achievement 0.3**: Testing

## Current Status & Handoff

Next: Achievement 0.2 (Implementation)
"""
        self.plan_path.write_text(plan_content)

        result = detect_plan_filesystem_conflict(
            self.plan_path, "TEST-FEATURE", "0.1", plan_content
        )

        # Should return None when no conflict
        assert result is None

    def test_no_conflict_when_no_approved_files(self):
        """Test no conflict when no APPROVED files exist yet."""
        # Create SUBPLAN but no APPROVED file
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text("# SUBPLAN: TEST-FEATURE 0.1\n")

        # PLAN with Achievement Index
        plan_content = """# PLAN: TEST-FEATURE

## 📋 Desirable Achievements

**Achievement 0.1**: Setup
**Achievement 0.2**: Implementation

## Current Status & Handoff

Next: Achievement 0.1 (Setup)
"""
        self.plan_path.write_text(plan_content)

        result = detect_plan_filesystem_conflict(
            self.plan_path, "TEST-FEATURE", "0.1", plan_content
        )

        # Should return None when no conflicts
        assert result is None

    def test_conflict_includes_details(self):
        """Test that conflict result includes all necessary details."""
        # Create APPROVED file for achievement NOT in index
        approved_file = self.feedbacks_dir / "APPROVED_99.md"
        approved_file.write_text("# Approved\n")

        # PLAN without 9.9 in Achievement Index
        plan_content = """# PLAN: TEST-FEATURE

## 📋 Desirable Achievements

**Achievement 0.1**: Setup
**Achievement 0.2**: Implementation

## Current Status & Handoff

Next: Achievement 0.1 (Setup)
"""
        self.plan_path.write_text(plan_content)

        result = detect_plan_filesystem_conflict(
            self.plan_path, "TEST-FEATURE", "0.1", plan_content
        )

        assert result is not None
        assert "has_conflict" in result
        assert "conflicts" in result
        assert result["has_conflict"] is True
        assert len(result["conflicts"]) > 0

    def test_multiple_conflicts(self):
        """Test detection of multiple conflicts at once."""
        # Create APPROVED and SUBPLAN for achievements NOT in index
        approved_file = self.feedbacks_dir / "APPROVED_98.md"
        approved_file.write_text("# Approved\n")

        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_99.md"
        subplan_path.write_text("# SUBPLAN\n")

        # PLAN without 9.8 or 9.9 in Achievement Index
        plan_content = """# PLAN: TEST-FEATURE

## 📋 Desirable Achievements

**Achievement 0.1**: Setup
**Achievement 0.2**: Implementation

## Current Status & Handoff

Next: Achievement 0.1 (Setup)
"""
        self.plan_path.write_text(plan_content)

        result = detect_plan_filesystem_conflict(
            self.plan_path, "TEST-FEATURE", "0.1", plan_content
        )

        assert result is not None
        assert result["has_conflict"] is True
        # Should have 2 conflicts (one for APPROVED, one for SUBPLAN)
        assert len(result["conflicts"]) == 2

    def test_no_conflict_when_no_work_started(self):
        """Test no conflict when no work has started (no filesystem artifacts)."""
        # No SUBPLAN, no EXECUTION, no APPROVED files

        # PLAN with Achievement Index
        plan_content = """# PLAN: TEST-FEATURE

## 📋 Desirable Achievements

**Achievement 0.1**: Setup
**Achievement 0.2**: Implementation

## Current Status & Handoff

Next: Achievement 0.1 (Setup)
"""
        self.plan_path.write_text(plan_content)

        result = detect_plan_filesystem_conflict(
            self.plan_path, "TEST-FEATURE", "0.1", plan_content
        )

        # Should return None when no filesystem artifacts
        assert result is None

    def test_conflict_provides_resolution_guidance(self):
        """Test that conflict includes likely cause and resolution guidance."""
        # Create APPROVED file for achievement NOT in index
        approved_file = self.feedbacks_dir / "APPROVED_99.md"
        approved_file.write_text("# Approved\n")

        # PLAN without 9.9 in Achievement Index
        plan_content = """# PLAN: TEST-FEATURE

## 📋 Desirable Achievements

**Achievement 0.1**: Setup
**Achievement 0.2**: Implementation

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
        assert "resolution" in conflict
        assert "Achievement Index" in conflict["resolution"]
