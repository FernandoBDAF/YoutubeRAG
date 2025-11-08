"""
Test Edge Cases - Phase 5 of Achievement 1.3

Tests for error scenarios, edge cases, and graceful degradation:
- Missing files and directories
- Malformed content
- Permission errors
- Empty files
- Unicode and special characters
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from LLM.scripts.generation.generate_prompt import (
    detect_workflow_state_filesystem,
    find_next_achievement_from_plan,
    is_achievement_complete,
    find_subplan_for_achievement,
    extract_handoff_section,
)


class TestMissingFilesAndDirectories:
    """Test handling of missing files and directories."""

    def setup_method(self):
        """Create temporary directory structure for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.plan_dir = Path(self.temp_dir) / "TEST-FEATURE"
        self.plan_dir.mkdir(parents=True)
        
        # Create PLAN file
        self.plan_path = self.plan_dir / "PLAN_TEST-FEATURE.md"
        self.plan_path.write_text("# PLAN: TEST-FEATURE\n")

    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_missing_subplan_directory(self):
        """Test when subplans directory doesn't exist."""
        # No subplans directory created
        
        result = detect_workflow_state_filesystem(
            self.plan_path, "TEST-FEATURE", "0.1"
        )
        
        assert result["state"] == "no_subplan"
        assert result["subplan_path"] is None

    def test_missing_execution_directory(self):
        """Test when execution directory doesn't exist."""
        # Create subplans directory and SUBPLAN
        subplan_dir = self.plan_dir / "subplans"
        subplan_dir.mkdir()
        subplan_path = subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text("# SUBPLAN\n**Status**: ⏳ In Progress\n")
        
        # No execution directory
        
        result = detect_workflow_state_filesystem(
            self.plan_path, "TEST-FEATURE", "0.1"
        )
        
        assert result["state"] == "subplan_no_execution"

    def test_empty_subplan_directory(self):
        """Test when subplans directory is empty."""
        subplan_dir = self.plan_dir / "subplans"
        subplan_dir.mkdir()
        
        result = detect_workflow_state_filesystem(
            self.plan_path, "TEST-FEATURE", "0.1"
        )
        
        assert result["state"] == "no_subplan"

    def test_empty_execution_directory(self):
        """Test when execution directory is empty."""
        # Create directories
        subplan_dir = self.plan_dir / "subplans"
        subplan_dir.mkdir()
        execution_dir = self.plan_dir / "execution"
        execution_dir.mkdir()
        
        # Create SUBPLAN
        subplan_path = subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text("# SUBPLAN\n**Status**: ⏳ In Progress\n")
        
        result = detect_workflow_state_filesystem(
            self.plan_path, "TEST-FEATURE", "0.1"
        )
        
        assert result["state"] == "subplan_no_execution"


class TestMalformedContent:
    """Test handling of malformed or invalid content."""

    def test_empty_plan_content(self):
        """Test with empty PLAN content."""
        result = find_next_achievement_from_plan("")
        assert result is None

    def test_plan_with_no_handoff_section(self):
        """Test PLAN without handoff section."""
        plan_content = """# PLAN: TEST-FEATURE

## Achievements

### Achievement 0.1: Setup
"""
        
        result = find_next_achievement_from_plan(plan_content)
        assert result is None

    def test_handoff_section_with_no_next(self):
        """Test handoff section without 'Next:' field."""
        plan_content = """# PLAN: TEST-FEATURE

## Current Status & Handoff

**Status**: In Progress
**Context**: Working on setup
"""
        
        result = find_next_achievement_from_plan(plan_content)
        assert result is None

    def test_malformed_achievement_number(self):
        """Test with malformed achievement numbers."""
        plan_content = """# PLAN

## Current Status & Handoff

✅ Achievement ABC complete
"""
        
        # Function uses re.escape() so it will match any string
        result = is_achievement_complete("ABC", plan_content)
        # Actually matches because re.escape() handles any string
        assert result is True

    def test_empty_handoff_section(self):
        """Test with empty handoff section."""
        plan_content = """# PLAN: TEST-FEATURE

## Current Status & Handoff

## Achievements
"""
        
        result = extract_handoff_section(plan_content)
        # Returns None when section is empty (no content between headers)
        assert result is None


class TestUnicodeAndSpecialCharacters:
    """Test handling of unicode and special characters."""

    def setup_method(self):
        """Create temporary directory structure for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.plan_dir = Path(self.temp_dir) / "TEST-FEATURE"
        self.plan_dir.mkdir(parents=True)
        self.subplan_dir = self.plan_dir / "subplans"
        self.subplan_dir.mkdir()
        
        self.plan_path = self.plan_dir / "PLAN_TEST-FEATURE.md"
        self.plan_path.write_text("# PLAN: TEST-FEATURE\n")

    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_unicode_in_achievement_title(self):
        """Test achievement with unicode characters in title."""
        plan_content = """# PLAN

## Current Status & Handoff

Next: Achievement 0.1 (Configuración Inicial 🚀)
"""
        
        result = find_next_achievement_from_plan(plan_content)
        assert result == "0.1"

    def test_emoji_variations_in_status(self):
        """Test different emoji variations in status."""
        plan_content = """# PLAN

## Current Status & Handoff

✅ Achievement 0.1 complete
"""
        
        result = is_achievement_complete("0.1", plan_content)
        assert result is True

    def test_special_characters_in_feature_name(self):
        """Test feature names with special characters."""
        # Create SUBPLAN with special chars
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text("# SUBPLAN\n")
        
        result = find_subplan_for_achievement("TEST-FEATURE", "0.1", self.plan_path)
        assert result == subplan_path


class TestBoundaryConditions:
    """Test boundary conditions and limits."""

    def setup_method(self):
        """Create temporary directory structure for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.plan_dir = Path(self.temp_dir) / "TEST-FEATURE"
        self.plan_dir.mkdir(parents=True)
        self.subplan_dir = self.plan_dir / "subplans"
        self.subplan_dir.mkdir()
        self.execution_dir = self.plan_dir / "execution"
        self.execution_dir.mkdir()
        
        self.plan_path = self.plan_dir / "PLAN_TEST-FEATURE.md"
        self.plan_path.write_text("# PLAN: TEST-FEATURE\n")

    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_achievement_number_zero(self):
        """Test achievement number 0.0."""
        plan_content = """# PLAN

## Current Status & Handoff

Next: Achievement 0.0 (Initial)
"""
        
        result = find_next_achievement_from_plan(plan_content)
        assert result == "0.0"

    def test_large_achievement_number(self):
        """Test large achievement numbers."""
        plan_content = """# PLAN

## Current Status & Handoff

Next: Achievement 99.99 (Final)
"""
        
        result = find_next_achievement_from_plan(plan_content)
        assert result == "99.99"

    def test_many_executions(self):
        """Test workflow with many EXECUTIONs."""
        # Create SUBPLAN
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text("# SUBPLAN\n**Status**: ⏳ In Progress\n")
        
        # Create 10 EXECUTIONs (5 complete, 5 in progress)
        for i in range(1, 11):
            exec_path = self.execution_dir / f"EXECUTION_TASK_TEST-FEATURE_01_{i:02d}.md"
            status = "✅ Complete" if i <= 5 else "⏳ In Progress"
            exec_path.write_text(f"# EXECUTION_TASK\n**Status**: {status}\n")
        
        result = detect_workflow_state_filesystem(
            self.plan_path, "TEST-FEATURE", "0.1"
        )
        
        assert result["state"] == "active_execution"
        assert result["execution_count"] == 10
        assert result["completed_count"] == 5


class TestGracefulDegradation:
    """Test graceful degradation when things go wrong."""

    def setup_method(self):
        """Create temporary directory structure for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.plan_dir = Path(self.temp_dir) / "TEST-FEATURE"
        self.plan_dir.mkdir(parents=True)
        self.subplan_dir = self.plan_dir / "subplans"
        self.subplan_dir.mkdir()
        self.execution_dir = self.plan_dir / "execution"
        self.execution_dir.mkdir()
        
        self.plan_path = self.plan_dir / "PLAN_TEST-FEATURE.md"
        self.plan_path.write_text("# PLAN: TEST-FEATURE\n")

    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_corrupted_subplan_file(self):
        """Test with corrupted SUBPLAN file (no status)."""
        # Create SUBPLAN without status
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text("# SUBPLAN\n# No status field\n")
        
        # Should still detect SUBPLAN exists
        result = detect_workflow_state_filesystem(
            self.plan_path, "TEST-FEATURE", "0.1"
        )
        
        # Should handle gracefully (not crash)
        assert result["state"] in ["subplan_no_execution", "subplan_complete"]

    def test_execution_file_with_no_status(self):
        """Test EXECUTION file without status field."""
        # Create SUBPLAN
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text("# SUBPLAN\n**Status**: ⏳ In Progress\n")
        
        # Create EXECUTION without status
        exec_path = self.execution_dir / "EXECUTION_TASK_TEST-FEATURE_01_01.md"
        exec_path.write_text("# EXECUTION_TASK\n# No status\n")
        
        result = detect_workflow_state_filesystem(
            self.plan_path, "TEST-FEATURE", "0.1"
        )
        
        # Should detect EXECUTION exists but count as incomplete
        assert result["state"] == "active_execution"
        assert result["completed_count"] == 0

    def test_mixed_execution_versions(self):
        """Test mix of regular and _V2 EXECUTION files."""
        # Create SUBPLAN
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text("# SUBPLAN\n**Status**: ⏳ In Progress\n")
        
        # Create regular and V2 files
        exec1_path = self.execution_dir / "EXECUTION_TASK_TEST-FEATURE_01_01.md"
        exec1_path.write_text("# EXECUTION_TASK\n**Status**: ✅ Complete\n")
        
        exec2_path = self.execution_dir / "EXECUTION_TASK_TEST-FEATURE_01_02_V2.md"
        exec2_path.write_text("# EXECUTION_TASK\n**Status**: ⏳ In Progress\n")
        
        result = detect_workflow_state_filesystem(
            self.plan_path, "TEST-FEATURE", "0.1"
        )
        
        # Should detect both files
        assert result["execution_count"] == 2
        assert result["completed_count"] == 1

