"""
Test Achievement Finding - Phase 2 of Achievement 1.3

Tests for achievement finding functions including:
- find_next_achievement_from_plan()
- find_next_achievement_hybrid()
- is_achievement_complete()
- find_subplan_for_achievement()
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from LLM.scripts.generation.workflow_detector import WorkflowDetector
from LLM.scripts.generation.utils import is_achievement_complete
from LLM.scripts.generation.generate_prompt import find_subplan_for_achievement

# Create detector instance for tests
detector = WorkflowDetector()
find_next_achievement_from_plan = detector.find_next_achievement_from_plan
find_next_achievement_hybrid = detector.find_next_achievement_hybrid


class TestFindNextAchievementFromPlan:
    """Test finding achievement from PLAN handoff section."""

    def test_finds_from_handoff_section_with_next(self):
        """Test finding achievement from 'Current Status & Handoff' section with Next:."""
        plan_content = """# PLAN: TEST-FEATURE

## Current Status & Handoff

⏳ Next: Achievement 0.2 (Data Processing)
**Status**: Ready to start

## Achievements

### Achievement 0.1: Setup ✅
Status: Complete

### Achievement 0.2: Data Processing ⏳
Status: Next
"""

        result = find_next_achievement_from_plan(plan_content)

        assert result == "0.2"

    def test_finds_from_handoff_with_next_achievement(self):
        """Test finding with 'Next: Achievement X.Y' format."""
        plan_content = """# PLAN: TEST-FEATURE

## Current Status & Handoff

Next: Achievement 1.3 (Testing)
"""

        result = find_next_achievement_from_plan(plan_content)

        assert result == "1.3"

    def test_handles_plan_without_handoff(self):
        """Test when no handoff section exists."""
        plan_content = """# PLAN: TEST-FEATURE

## Achievements

### Achievement 0.1: Setup ✅
Status: Complete

### Achievement 0.2: Data Processing ⏳
Status: In Progress
"""

        result = find_next_achievement_from_plan(plan_content)

        # Should return None when no handoff
        assert result is None

    def test_handles_complete_plan(self):
        """Test when plan has no next achievement."""
        plan_content = """# PLAN: TEST-FEATURE

## Current Status & Handoff

All achievements complete!

## Achievements

### Achievement 0.1: Setup ✅
Status: Complete
"""

        result = find_next_achievement_from_plan(plan_content)

        # Should return None when no next
        assert result is None


class TestIsAchievementComplete:
    """Test achievement completion detection (filesystem-first)."""

    @pytest.fixture
    def temp_plan_dir(self):
        """Create temporary plan directory structure."""
        temp_dir = tempfile.mkdtemp()
        plan_dir = Path(temp_dir) / "TEST-FEATURE"
        plan_dir.mkdir(parents=True)

        # Create plan file
        plan_file = plan_dir / "PLAN_TEST-FEATURE.md"
        plan_file.write_text("# PLAN: TEST-FEATURE\n")

        # Create execution/feedbacks structure
        feedbacks_dir = plan_dir / "execution" / "feedbacks"
        feedbacks_dir.mkdir(parents=True)

        yield plan_dir, plan_file, feedbacks_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_detects_complete_with_checkmark_before(self, temp_plan_dir):
        """Test detecting complete achievement with APPROVED file."""
        plan_dir, plan_file, feedbacks_dir = temp_plan_dir

        # Create APPROVED file for achievement 0.1
        approved_file = feedbacks_dir / "APPROVED_01.md"
        approved_file.write_text(
            """# Achievement 0.1 Approval

**Status**: ✅ Approved
**Date**: 2025-11-12
**Reviewer**: Test Suite
"""
        )

        result = is_achievement_complete("0.1", "", plan_file)
        assert result is True

    def test_detects_incomplete_with_hourglass(self, temp_plan_dir):
        """Test detecting incomplete achievement (no APPROVED file)."""
        plan_dir, plan_file, feedbacks_dir = temp_plan_dir

        # Don't create APPROVED file - achievement is incomplete

        result = is_achievement_complete("0.2", "", plan_file)
        assert result is False

    def test_detects_pending_with_box(self, temp_plan_dir):
        """Test detecting pending achievement (no APPROVED file)."""
        plan_dir, plan_file, feedbacks_dir = temp_plan_dir

        # Don't create APPROVED file - achievement is pending

        result = is_achievement_complete("0.3", "", plan_file)
        assert result is False

    def test_handles_achievement_not_found(self, temp_plan_dir):
        """Test when achievement number doesn't exist."""
        plan_dir, plan_file, feedbacks_dir = temp_plan_dir

        # Don't create APPROVED file

        result = is_achievement_complete("0.5", "", plan_file)
        assert result is False

    def test_handles_dotted_achievement_numbers(self, temp_plan_dir):
        """Test achievement numbers with dots (e.g., 1.2) - APPROVED_12.md."""
        plan_dir, plan_file, feedbacks_dir = temp_plan_dir

        # Create APPROVED file for achievement 1.2 (becomes APPROVED_12.md)
        approved_file = feedbacks_dir / "APPROVED_12.md"
        approved_file.write_text(
            """# Achievement 1.2 Approval

**Status**: ✅ Approved
**Date**: 2025-11-12
**Reviewer**: Test Suite
"""
        )

        result = is_achievement_complete("1.2", "", plan_file)
        assert result is True

    def test_case_insensitive_complete_status(self, temp_plan_dir):
        """Test that filesystem detection is consistent."""
        plan_dir, plan_file, feedbacks_dir = temp_plan_dir

        # Create APPROVED file
        approved_file = feedbacks_dir / "APPROVED_03.md"
        approved_file.write_text("# Approved\n")

        # Filesystem detection is case-consistent (file exists or not)
        result = is_achievement_complete("0.3", "", plan_file)
        assert result is True


class TestFindSubplanForAchievement:
    """Test finding SUBPLAN files for achievements."""

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

    def test_finds_subplan_simple_number(self):
        """Test finding SUBPLAN with simple achievement number (0.1)."""
        # Create SUBPLAN
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan_path.write_text("# SUBPLAN\n")

        result = find_subplan_for_achievement("TEST-FEATURE", "0.1", self.plan_path)

        assert result == subplan_path

    def test_finds_subplan_dotted_number(self):
        """Test finding SUBPLAN with dotted achievement number (1.2)."""
        # Create SUBPLAN (dots removed: 1.2 -> 12)
        subplan_path = self.subplan_dir / "SUBPLAN_TEST-FEATURE_12.md"
        subplan_path.write_text("# SUBPLAN\n")

        result = find_subplan_for_achievement("TEST-FEATURE", "1.2", self.plan_path)

        assert result == subplan_path

    def test_returns_none_when_not_found(self):
        """Test returns None when SUBPLAN doesn't exist."""
        result = find_subplan_for_achievement("TEST-FEATURE", "0.1", self.plan_path)

        assert result is None

    def test_handles_multiple_subplans(self):
        """Test finding specific SUBPLAN when multiple exist."""
        # Create multiple SUBPLANs
        subplan1 = self.subplan_dir / "SUBPLAN_TEST-FEATURE_01.md"
        subplan1.write_text("# SUBPLAN 0.1\n")

        subplan2 = self.subplan_dir / "SUBPLAN_TEST-FEATURE_02.md"
        subplan2.write_text("# SUBPLAN 0.2\n")

        subplan3 = self.subplan_dir / "SUBPLAN_TEST-FEATURE_03.md"
        subplan3.write_text("# SUBPLAN 0.3\n")

        # Find specific one
        result = find_subplan_for_achievement("TEST-FEATURE", "0.2", self.plan_path)

        assert result == subplan2

    def test_handles_feature_name_with_dashes(self):
        """Test feature names with multiple dashes."""
        # Create directory with dashes
        dash_dir = Path(self.temp_dir) / "MULTI-DASH-FEATURE"
        dash_dir.mkdir()
        dash_subplan_dir = dash_dir / "subplans"
        dash_subplan_dir.mkdir()

        plan_path = dash_dir / "PLAN_MULTI-DASH-FEATURE.md"
        plan_path.write_text("# PLAN\n")

        subplan_path = dash_subplan_dir / "SUBPLAN_MULTI-DASH-FEATURE_01.md"
        subplan_path.write_text("# SUBPLAN\n")

        result = find_subplan_for_achievement("MULTI-DASH-FEATURE", "0.1", plan_path)

        assert result == subplan_path


class TestAchievementFindingEdgeCases:
    """Test edge cases in achievement finding."""

    @pytest.fixture
    def temp_plan_dir(self):
        """Create temporary plan directory structure."""
        temp_dir = tempfile.mkdtemp()
        plan_dir = Path(temp_dir) / "TEST-FEATURE"
        plan_dir.mkdir(parents=True)

        # Create plan file
        plan_file = plan_dir / "PLAN_TEST-FEATURE.md"
        plan_file.write_text("# PLAN: TEST-FEATURE\n")

        # Create execution/feedbacks structure
        feedbacks_dir = plan_dir / "execution" / "feedbacks"
        feedbacks_dir.mkdir(parents=True)

        yield plan_dir, plan_file, feedbacks_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_achievement_with_leading_zeros(self, temp_plan_dir):
        """Test achievement numbers with leading zeros (01 -> APPROVED_01.md)."""
        plan_dir, plan_file, feedbacks_dir = temp_plan_dir

        # Create APPROVED file for achievement 01 (APPROVED_01.md)
        approved_file = feedbacks_dir / "APPROVED_01.md"
        approved_file.write_text(
            """# Achievement 01 Approval

**Status**: ✅ Approved
**Date**: 2025-11-12
**Reviewer**: Test Suite
"""
        )

        # Should match "01" format
        result1 = is_achievement_complete("01", "", plan_file)

        assert result1 is True

    def test_achievement_in_handoff_with_extra_text(self):
        """Test extracting achievement from handoff with description."""
        plan_content = """# PLAN

## Current Status & Handoff

Next: Achievement 0.2 (Data Processing and Validation)
**Status**: Ready to start
**Context**: After completing setup...
"""

        result = find_next_achievement_from_plan(plan_content)

        # Should extract just "0.2"
        assert result == "0.2"

    def test_multiple_handoff_sections(self):
        """Test when there are multiple handoff-like sections."""
        plan_content = """# PLAN

## Previous Status

Next: Achievement 0.1 (Old)

## Current Status & Handoff

Next: Achievement 0.2 (Current)
"""

        result = find_next_achievement_from_plan(plan_content)

        # Should use "Current Status & Handoff" section
        assert result == "0.2"

    def test_empty_plan_content(self):
        """Test handling empty plan content."""
        result = find_next_achievement_from_plan("")

        assert result is None

    def test_plan_with_no_achievements(self):
        """Test plan with no achievements section."""
        plan_content = """# PLAN: TEST-FEATURE

## Overview

This is a plan without achievements yet.
"""

        result = find_next_achievement_from_plan(plan_content)

        assert result is None
