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
    is_achievement_complete,
    get_plan_status,
    is_plan_complete,
    find_next_achievement_hybrid,
    find_next_achievement_from_archive,
    find_next_achievement_from_root,
    extract_handoff_section,
    Achievement,
)


class TestIsAchievementComplete(unittest.TestCase):
    """Test is_achievement_complete() function."""

    def test_achievement_complete_with_emoji_in_handoff(self):
        """Achievement marked complete with ✅ emoji in handoff section."""
        plan_content = """# PLAN: Test

## 📝 Current Status & Handoff

**What's Done**:
- ✅ Achievement 1.1 complete

---
"""
        self.assertTrue(is_achievement_complete("1.1", plan_content))

    def test_achievement_complete_format_no_emoji(self):
        """Achievement marked complete in 'Achievement X.Y Complete:' format."""
        plan_content = """# PLAN: Test

## 📝 Current Status & Handoff

**What's Done**:
- Achievement 1.1 Complete: Created script

---
"""
        self.assertTrue(is_achievement_complete("1.1", plan_content))

    def test_achievement_not_complete(self):
        """Achievement not marked complete."""
        plan_content = """# PLAN: Test

## 📝 Current Status & Handoff

**What's Done**:
- Achievement 1.1 In Progress

---
"""
        self.assertFalse(is_achievement_complete("1.1", plan_content))

    def test_achievement_doesnt_exist(self):
        """Achievement doesn't exist in PLAN."""
        plan_content = """# PLAN: Test

## 📝 Current Status & Handoff

**What's Done**:
- Achievement 1.1 Complete

---
"""
        self.assertFalse(is_achievement_complete("2.1", plan_content))

    def test_empty_handoff_section(self):
        """Empty handoff section."""
        plan_content = """# PLAN: Test

## Some Section
"""
        self.assertFalse(is_achievement_complete("1.1", plan_content))


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
    """Test is_plan_complete() function (FIXED for Bug #4)."""

    def test_complete_plan_all_achievements_complete(self):
        """Complete PLAN with 'All achievements complete'."""
        achievements = [
            Achievement("1.1", "First", "", "", "", 10),
            Achievement("1.2", "Second", "", "", "", 10),
        ]
        plan_content = """# PLAN: Test

## 📝 Current Status & Handoff

All achievements complete! ✅

---
"""
        self.assertTrue(is_plan_complete(plan_content, achievements))

    def test_complete_plan_with_percentage(self):
        """Complete PLAN with '7/7 achievements complete'."""
        achievements = [Achievement(f"1.{i}", f"Ach {i}", "", "", "", 10) for i in range(1, 8)]
        plan_content = """# PLAN: Test

## 📝 Current Status & Handoff

Completed: 7/7 achievements complete

---
"""
        self.assertTrue(is_plan_complete(plan_content, achievements))

    def test_incomplete_plan_false_positive(self):
        """Incomplete PLAN (2/4) - should NOT match (Bug #4)."""
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
        # This should NOT detect as complete (only 2/4 complete)
        self.assertFalse(is_plan_complete(plan_content, achievements))

    def test_false_positive_descriptive_text(self):
        """PLAN with 'all achievements are complete' in description (false positive)."""
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
        # Should NOT match "all achievements are complete" in description
        self.assertFalse(is_plan_complete(plan_content, achievements))

    def test_false_positive_script_reference(self):
        """PLAN with 'plan_completion.py' in code (false positive)."""
        achievements = [Achievement("1.1", "First", "", "", "", 10)]
        plan_content = """# PLAN: Test

## 📝 Current Status & Handoff

Run `plan_completion.py` to verify all achievements are complete.

**What's Next**:
- Achievement 1.1

---
"""
        # Should NOT match "plan_completion" script reference
        self.assertFalse(is_plan_complete(plan_content, achievements))

    def test_false_positive_individual_achievement_status(self):
        """PLAN with 'Status**: Achievement 2.1 Complete' (false positive)."""
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
        # Should NOT match individual achievement completion status
        self.assertFalse(is_plan_complete(plan_content, achievements))

    def test_complete_plan_with_all_achievements_marked(self):
        """Complete PLAN with all achievements marked ✅."""
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
        self.assertTrue(is_plan_complete(plan_content, achievements))


class TestFindNextAchievementHybridComprehensive(unittest.TestCase):
    """Test find_next_achievement_hybrid() (ALL BUGS)."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

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
            result = find_next_achievement_hybrid(
                plan_path, "TEST", achievements, "./nonexistent-archive/"
            )
            # Should return 0.1 (first unarchived achievement)
            self.assertIsNotNone(result)
            self.assertEqual(result.number, "0.1")

    def test_bug_2_completion_detection(self):
        """Bug #2: Complete PLAN (should return None)."""
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

        # Should return None (PLAN is complete)
        result = find_next_achievement_hybrid(
            plan_path, "TEST", achievements, "./nonexistent-archive/"
        )
        self.assertIsNone(result)

    def test_bug_3_missing_achievement_and_completed_fallback(self):
        """Bug #3: Missing achievement + completed fallback (should skip completed)."""
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

        # Should warn and fall back, but skip completed 0.1
        with self.assertWarns(UserWarning):
            result = find_next_achievement_hybrid(
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
        result = find_next_achievement_hybrid(
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
        result = find_next_achievement_hybrid(
            plan_path, "TEST", achievements, "./nonexistent-archive/"
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.number, "1.1")

    def test_completed_achievement_in_handoff(self):
        """Completed achievement in handoff (should warn, use fallback)."""
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

        # Should warn and fall back to next incomplete achievement
        with self.assertWarns(UserWarning):
            result = find_next_achievement_hybrid(
                plan_path, "TEST", achievements, "./nonexistent-archive/"
            )
            # Should return 0.1 or 1.2 (first incomplete)
            self.assertIsNotNone(result)
            self.assertIn(result.number, ["0.1", "1.2"])

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
        result = find_next_achievement_hybrid(
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

    def test_find_next_achievement_from_archive_skips_completed(self):
        """Archive fallback skips completed achievements."""
        # Create archived SUBPLAN for 0.1
        subplan_01 = self.archive_subplans / "SUBPLAN_TEST_01.md"
        subplan_01.write_text("# SUBPLAN")

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
        result = find_next_achievement_from_archive(
            "TEST", achievements, str(self.archive_path), plan_content
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.number, "1.2")

    def test_find_next_achievement_from_root_skips_completed(self):
        """Root fallback skips completed achievements."""
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
        result = find_next_achievement_from_root("TEST", achievements, plan_content)
        self.assertIsNotNone(result)
        self.assertEqual(result.number, "1.1")


if __name__ == "__main__":
    unittest.main()

