#!/usr/bin/env python3
"""
Comprehensive test suite for prompt generator bug fixes.

Tests all 5 bugs:
- Bug #1: Missing achievement validation
- Bug #2: No completion detection
- Bug #3: Combination bug (missing achievement + completed fallback)
- Bug #4: False positive completion detection
- Bug #5: Pattern matching order

Target: >95% coverage for all new/fixed functions
"""

import unittest
import tempfile
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from LLM.scripts.generation.generate_prompt import (
    get_plan_status,
    is_plan_complete,
)
from LLM.scripts.generation.utils import is_achievement_complete, Achievement
from LLM.scripts.generation.plan_parser import PlanParser
from LLM.scripts.generation.workflow_detector import WorkflowDetector


class TestIsAchievementComplete(unittest.TestCase):
    """Test is_achievement_complete() function - FILESYSTEM-ONLY."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.plan_path = self.temp_path / "PLAN_TEST.md"
        self.plan_path.write_text("# PLAN: Test")
        self.feedbacks_dir = self.temp_path / "execution" / "feedbacks"
        self.feedbacks_dir.mkdir(parents=True)

    def test_achievement_complete_with_emoji_in_handoff(self):
        """Achievement marked complete via APPROVED_11.md file (filesystem-first)."""
        plan_content = """# PLAN: Test

## 📝 Current Status & Handoff

**What's Done**:
- ✅ Achievement 1.1 complete

---
"""
        # Create APPROVED file (filesystem-first)
        (self.feedbacks_dir / "APPROVED_11.md").write_text("# APPROVED")
        self.assertTrue(is_achievement_complete("1.1", plan_content, self.plan_path))

    def test_achievement_complete_format_no_emoji(self):
        """Achievement marked complete via APPROVED_11.md file (filesystem-first)."""
        plan_content = """# PLAN: Test

## 📝 Current Status & Handoff

**What's Done**:
- Achievement 1.1 Complete: Created script

---
"""
        # Create APPROVED file (filesystem-first)
        (self.feedbacks_dir / "APPROVED_11.md").write_text("# APPROVED")
        self.assertTrue(is_achievement_complete("1.1", plan_content, self.plan_path))

    def test_achievement_not_complete(self):
        """Achievement not marked complete (no APPROVED file)."""
        plan_content = """# PLAN: Test

## 📝 Current Status & Handoff

**What's Done**:
- Achievement 1.1 In Progress

---
"""
        # No APPROVED file created, so should return False
        self.assertFalse(is_achievement_complete("1.1", plan_content, self.plan_path))

    def test_achievement_doesnt_exist(self):
        """Achievement doesn't exist in PLAN (no APPROVED file)."""
        plan_content = """# PLAN: Test

## 📝 Current Status & Handoff

**What's Done**:
- Achievement 1.1 Complete

---
"""
        # No APPROVED_21.md file, so should return False
        self.assertFalse(is_achievement_complete("2.1", plan_content, self.plan_path))

    def test_empty_handoff_section(self):
        """Empty handoff section (no APPROVED file)."""
        plan_content = """# PLAN: Test

## Some Section
"""
        # No APPROVED file, so should return False
        self.assertFalse(is_achievement_complete("1.1", plan_content, self.plan_path))


class TestGetPlanStatus(unittest.TestCase):
    """Test get_plan_status() function."""

    def test_planning_status(self):
        """PLAN with 'Planning' status."""
        plan_content = """# PLAN: Test

**Status**: Planning

## 📝 Current Status & Handoff

**Status**: Planning
"""
        self.assertEqual(get_plan_status(plan_content), "planning")

    def test_in_progress_status(self):
        """PLAN with 'In Progress' status."""
        plan_content = """# PLAN: Test

**Status**: In Progress

## 📝 Current Status & Handoff

**Status**: In Progress
"""
        self.assertEqual(get_plan_status(plan_content), "in progress")

    def test_complete_status(self):
        """PLAN with 'Complete' status."""
        plan_content = """# PLAN: Test

**Status**: Complete

## 📝 Current Status & Handoff

**Status**: Complete
"""
        self.assertEqual(get_plan_status(plan_content), "complete")

    def test_no_status_specified(self):
        """PLAN without status specified."""
        plan_content = """# PLAN: Test

## Some Section
"""
        self.assertEqual(get_plan_status(plan_content), "unknown")


class TestIsPlanCompleteFixed(unittest.TestCase):
    """Test is_plan_complete() function - FILESYSTEM-ONLY (Bug #11)."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.plan_path = self.temp_path / "PLAN_TEST.md"
        self.plan_path.write_text("# PLAN: Test")
        self.feedbacks_dir = self.temp_path / "execution" / "feedbacks"
        self.feedbacks_dir.mkdir(parents=True)

    def test_complete_plan_all_achievements_complete(self):
        """Complete PLAN via APPROVED files (filesystem-first)."""
        achievements = [
            Achievement("1.1", "First", "", "", "", 10),
            Achievement("1.2", "Second", "", "", "", 10),
        ]
        plan_content = """# PLAN: Test

## 📝 Current Status & Handoff

All achievements complete! ✅

---
"""
        # Create APPROVED files for all achievements (filesystem-first)
        (self.feedbacks_dir / "APPROVED_11.md").write_text("# APPROVED")
        (self.feedbacks_dir / "APPROVED_12.md").write_text("# APPROVED")
        self.assertTrue(is_plan_complete(plan_content, achievements, self.plan_path))

    def test_complete_plan_with_percentage(self):
        """Complete PLAN via APPROVED files (filesystem-first)."""
        achievements = [Achievement(f"1.{i}", f"Ach {i}", "", "", "", 10) for i in range(1, 8)]
        plan_content = """# PLAN: Test

## 📝 Current Status & Handoff

Completed: 7/7 achievements complete

---
"""
        # Create APPROVED files for all achievements (filesystem-first)
        for i in range(1, 8):
            (self.feedbacks_dir / f"APPROVED_1{i}.md").write_text("# APPROVED")
        self.assertTrue(is_plan_complete(plan_content, achievements, self.plan_path))

    def test_incomplete_plan_false_positive(self):
        """Incomplete PLAN (2/4) - filesystem shows only 2 APPROVED (Bug #4)."""
        achievements = [
            Achievement("1.1", "First", "", "", "", 10),
            Achievement("2.1", "Second", "", "", "", 10),
            Achievement("3.1", "Third", "", "", "", 10),
            Achievement("3.2", "Fourth", "", "", "", 10),
        ]
        plan_content = """# PLAN: Test

## 📝 Current Status & Handoff

**What's Done**:
- Achievement 1.1 Complete
- Achievement 2.1 Complete

**What's Next**:
- Achievement 3.1

**Status**: Achievement 2.1 Complete

---
"""
        # Create APPROVED files for only 2 achievements (filesystem-first)
        (self.feedbacks_dir / "APPROVED_11.md").write_text("# APPROVED")
        (self.feedbacks_dir / "APPROVED_21.md").write_text("# APPROVED")
        # This should NOT detect as complete (only 2/4 have APPROVED files)
        self.assertFalse(is_plan_complete(plan_content, achievements, self.plan_path))

    def test_false_positive_descriptive_text(self):
        """PLAN with 'all achievements are complete' text (no APPROVED files)."""
        achievements = [
            Achievement("1.1", "First", "", "", "", 10),
            Achievement("2.1", "Second", "", "", "", 10),
        ]
        plan_content = """# PLAN: Test

## 📝 Current Status & Handoff

To verify all achievements are complete, run the validation script.

**What's Next**:
- Achievement 2.1

---
"""
        # No APPROVED files created - should return False (ignores markdown)
        self.assertFalse(is_plan_complete(plan_content, achievements, self.plan_path))

    def test_false_positive_script_reference(self):
        """PLAN with 'plan_completion.py' text (no APPROVED files)."""
        achievements = [Achievement("1.1", "First", "", "", "", 10)]
        plan_content = """# PLAN: Test

## 📝 Current Status & Handoff

Run `plan_completion.py` to verify all achievements are complete.

**What's Next**:
- Achievement 1.1

---
"""
        # No APPROVED files - should return False (ignores markdown)
        self.assertFalse(is_plan_complete(plan_content, achievements, self.plan_path))

    def test_false_positive_individual_achievement_status(self):
        """PLAN with 'Status**: Achievement 2.1 Complete' (no APPROVED files)."""
        achievements = [
            Achievement("1.1", "First", "", "", "", 10),
            Achievement("2.1", "Second", "", "", "", 10),
        ]
        plan_content = """# PLAN: Test

## 📝 Current Status & Handoff

**Status**: Achievement 2.1 Complete

**What's Next**:
- Achievement 3.1

---
"""
        # No APPROVED files - should return False (ignores markdown)
        self.assertFalse(is_plan_complete(plan_content, achievements, self.plan_path))

    def test_complete_plan_with_all_achievements_marked(self):
        """Complete PLAN via APPROVED files (filesystem-first)."""
        achievements = [
            Achievement("1.1", "First", "", "", "", 10),
            Achievement("1.2", "Second", "", "", "", 10),
        ]
        plan_content = """# PLAN: Test

## 📝 Current Status & Handoff

**What's Done**:
- Achievement 1.1 Complete
- Achievement 1.2 Complete

---
"""
        # Create APPROVED files for all achievements (filesystem-first)
        (self.feedbacks_dir / "APPROVED_11.md").write_text("# APPROVED")
        (self.feedbacks_dir / "APPROVED_12.md").write_text("# APPROVED")
        self.assertTrue(is_plan_complete(plan_content, achievements, self.plan_path))


class TestFindNextAchievementHybridComprehensive(unittest.TestCase):
    """Test find_next_achievement_hybrid() - FILESYSTEM-FIRST."""

    def setUp(self):
        """Create temporary directory and initialize detector."""
        self.detector = WorkflowDetector()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        # Create feedbacks directory for filesystem-first completion checks
        self.feedbacks_dir = self.temp_path / "execution" / "feedbacks"
        self.feedbacks_dir.mkdir(parents=True)

    def test_bug_1_missing_achievement_validation(self):
        """Bug #1: Handoff references non-existent achievement (should warn, use fallback)."""
        plan_content = """# PLAN: Test

**Status**: In Progress

## 📝 Current Status & Handoff

**What's Next**:
- ⏳ Achievement 3.4 (doesn't exist)

---

## 🎯 Desirable Achievements

**Achievement 0.1**: First
**Achievement 1.1**: Second
**Achievement 1.2**: Third
"""
        plan_path = self.temp_path / "PLAN_TEST.md"
        plan_path.write_text(plan_content)

        achievements = [
            Achievement("0.1", "First", "", "", "", 10),
            Achievement("1.1", "Second", "", "", "", 10),
            Achievement("1.2", "Third", "", "", "", 10),
        ]

        # Should warn and fall back (0.1 is first unarchived)
        with self.assertWarns(UserWarning):
            result = self.detector.find_next_achievement_hybrid(
                plan_path, "TEST", achievements, "./nonexistent-archive/"
            )
            # Should return 0.1 (first unarchived achievement)
            self.assertIsNotNone(result)
            self.assertEqual(result.number, "0.1")

    def test_bug_2_completion_detection(self):
        """Bug #2: Complete PLAN via APPROVED files (should return None)."""
        plan_content = """# PLAN: Test

**Status**: In Progress

## 📝 Current Status & Handoff

All achievements complete! ✅

---

## 🎯 Desirable Achievements

**Achievement 1.1**: First
**Achievement 1.2**: Second
"""
        plan_path = self.temp_path / "PLAN_TEST.md"
        plan_path.write_text(plan_content)

        achievements = [
            Achievement("1.1", "First", "", "", "", 10),
            Achievement("1.2", "Second", "", "", "", 10),
        ]

        # Create APPROVED files for all achievements (filesystem-first)
        (self.feedbacks_dir / "APPROVED_11.md").write_text("# APPROVED")
        (self.feedbacks_dir / "APPROVED_12.md").write_text("# APPROVED")

        # Should return None (PLAN is complete - all have APPROVED files)
        result = self.detector.find_next_achievement_hybrid(
            plan_path, "TEST", achievements, "./nonexistent-archive/"
        )
        self.assertIsNone(result)

    def test_bug_3_missing_achievement_and_completed_fallback(self):
        """Bug #3: Missing achievement + completed fallback via APPROVED file (should skip completed)."""
        plan_content = """# PLAN: Test

**Status**: In Progress

## 📝 Current Status & Handoff

**What's Done**:
- Achievement 0.1 Complete

**What's Next**:
- ⏳ Achievement 1.6 (doesn't exist)

---

## 🎯 Desirable Achievements

**Achievement 0.1**: First (complete)
**Achievement 1.1**: Second
**Achievement 1.2**: Third
"""
        plan_path = self.temp_path / "PLAN_TEST.md"
        plan_path.write_text(plan_content)

        achievements = [
            Achievement("0.1", "First", "", "", "", 10),
            Achievement("1.1", "Second", "", "", "", 10),
            Achievement("1.2", "Third", "", "", "", 10),
        ]

        # Create APPROVED file for 0.1 (filesystem-first)
        (self.feedbacks_dir / "APPROVED_01.md").write_text("# APPROVED")

        # Should warn and fall back, but skip completed 0.1
        with self.assertWarns(UserWarning):
            result = self.detector.find_next_achievement_hybrid(
                plan_path, "TEST", achievements, "./nonexistent-archive/"
            )
            # Should return 1.1 (first incomplete unarchived achievement, not 0.1)
            self.assertIsNotNone(result)
            self.assertEqual(result.number, "1.1")

    def test_planning_status_returns_first_achievement(self):
        """Planning status (should return first achievement)."""
        plan_content = """# PLAN: Test

**Status**: Planning

## 📝 Current Status & Handoff

Ready to start.

---

## 🎯 Desirable Achievements

**Achievement 0.1**: First
**Achievement 1.1**: Second
"""
        plan_path = self.temp_path / "PLAN_TEST.md"
        plan_path.write_text(plan_content)

        achievements = [
            Achievement("0.1", "First", "", "", "", 10),
            Achievement("1.1", "Second", "", "", "", 10),
        ]

        # Should return first achievement for Planning status
        result = self.detector.find_next_achievement_hybrid(
            plan_path, "TEST", achievements, "./nonexistent-archive/"
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.number, "0.1")

    def test_valid_achievement_in_handoff(self):
        """Valid achievement in handoff (should return it)."""
        plan_content = """# PLAN: Test

**Status**: In Progress

## 📝 Current Status & Handoff

**What's Done**:
- Achievement 0.1 Complete

**What's Next**:
- ⏳ Achievement 1.1

---

## 🎯 Desirable Achievements

**Achievement 0.1**: First
**Achievement 1.1**: Second
"""
        plan_path = self.temp_path / "PLAN_TEST.md"
        plan_path.write_text(plan_content)

        achievements = [
            Achievement("0.1", "First", "", "", "", 10),
            Achievement("1.1", "Second", "", "", "", 10),
        ]

        # Should return 1.1 (from handoff)
        result = self.detector.find_next_achievement_hybrid(
            plan_path, "TEST", achievements, "./nonexistent-archive/"
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.number, "1.1")

    def test_completed_achievement_in_handoff(self):
        """Completed achievement in handoff via APPROVED file (should warn, use fallback)."""
        plan_content = """# PLAN: Test

**Status**: In Progress

## 📝 Current Status & Handoff

**What's Done**:
- Achievement 1.1 Complete

**What's Next**:
- ⏳ Achievement 1.1 (already complete)

---

## 🎯 Desirable Achievements

**Achievement 0.1**: First
**Achievement 1.1**: Second (complete)
**Achievement 1.2**: Third
"""
        plan_path = self.temp_path / "PLAN_TEST.md"
        plan_path.write_text(plan_content)

        achievements = [
            Achievement("0.1", "First", "", "", "", 10),
            Achievement("1.1", "Second", "", "", "", 10),
            Achievement("1.2", "Third", "", "", "", 10),
        ]

        # Create APPROVED file for 1.1 (filesystem-first)
        (self.feedbacks_dir / "APPROVED_11.md").write_text("# APPROVED")

        # Should warn and fall back to next incomplete achievement
        with self.assertWarns(UserWarning):
            result = self.detector.find_next_achievement_hybrid(
                plan_path, "TEST", achievements, "./nonexistent-archive/"
            )
            # Should return 0.1 (first incomplete)
            self.assertIsNotNone(result)
            self.assertEqual(result.number, "0.1")

    def test_bug_6_planning_status_with_completed_work(self):
        """Bug #6: Planning status but work done - should use handoff, not return first."""
        plan_content = """# PLAN: Test

**Status**: Planning

## 📝 Current Status & Handoff

**What's Done**:
- ✅ Achievement 0.1 Complete
- ✅ Achievement 1.1 Complete

**What's Next**:
- ⏳ Achievement 1.2

---

## 🎯 Desirable Achievements

**Achievement 0.1**: First
**Achievement 1.1**: Second
**Achievement 1.2**: Third
"""
        plan_path = self.temp_path / "PLAN_TEST.md"
        plan_path.write_text(plan_content)

        achievements = [
            Achievement("0.1", "First", "", "", "", 10),
            Achievement("1.1", "Second", "", "", "", 10),
            Achievement("1.2", "Third", "", "", "", 10),
        ]

        # Should return 1.2 from handoff (NOT 0.1 even though status is Planning)
        result = self.detector.find_next_achievement_hybrid(
            plan_path, "TEST", achievements, "./nonexistent-archive/"
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.number, "1.2")  # From handoff, not first achievement


class TestFallbackFunctionsFixed(unittest.TestCase):
    """Test fallback functions (FIXED to skip completed achievements)."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # Create archive directory structure
        self.archive_path = self.temp_path / "archive"
        self.archive_subplans = self.archive_path / "subplans"
        self.archive_subplans.mkdir(parents=True)

        # Create plan file with execution/feedbacks/ structure
        self.plan_path = self.temp_path / "PLAN_TEST.md"
        self.plan_path.write_text("# PLAN: Test")
        self.feedbacks_dir = self.temp_path / "execution" / "feedbacks"
        self.feedbacks_dir.mkdir(parents=True)

    def test_find_next_achievement_from_archive_skips_completed(self):
        """Archive fallback skips completed achievements."""
        # Create archived SUBPLAN for 0.1
        subplan_01 = self.archive_subplans / "SUBPLAN_TEST_01.md"
        subplan_01.write_text("# SUBPLAN")

        # Create APPROVED files for 0.1 and 1.1 (filesystem-first completion check)
        (self.feedbacks_dir / "APPROVED_01.md").write_text("# APPROVED")
        (self.feedbacks_dir / "APPROVED_11.md").write_text("# APPROVED")

        plan_content = """# PLAN: Test

## 📝 Current Status & Handoff

**What's Done**:
- Achievement 0.1 Complete
- Achievement 1.1 Complete

---
"""
        achievements = [
            Achievement("0.1", "First", "", "", "", 10),
            Achievement("1.1", "Second", "", "", "", 10),
            Achievement("1.2", "Third", "", "", "", 10),
        ]

        # Should skip 0.1 (archived) and 1.1 (complete), return 1.2
        detector = WorkflowDetector()
        result = detector.find_next_achievement_from_archive(
            "TEST", achievements, str(self.archive_path), plan_content, self.plan_path
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.number, "1.2")

    def test_find_next_achievement_from_root_skips_completed(self):
        """Root fallback skips completed achievements."""
        # Create APPROVED file for 0.1 (filesystem-first completion check)
        (self.feedbacks_dir / "APPROVED_01.md").write_text("# APPROVED")

        plan_content = """# PLAN: Test

## 📝 Current Status & Handoff

**What's Done**:
- Achievement 0.1 Complete

---
"""
        achievements = [
            Achievement("0.1", "First", "", "", "", 10),
            Achievement("1.1", "Second", "", "", "", 10),
        ]

        # Should skip 0.1 (complete), return 1.1
        detector = WorkflowDetector()
        result = detector.find_next_achievement_from_root(
            "TEST", achievements, plan_content, self.plan_path
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.number, "1.1")


if __name__ == "__main__":
    unittest.main()
