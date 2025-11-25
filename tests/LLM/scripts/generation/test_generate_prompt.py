"""Unit tests for generate_prompt.py - extract_handoff_section and find_next_achievement_from_plan functions."""

import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from LLM.scripts.generation.workflow_detector import WorkflowDetector
from LLM.scripts.generation.plan_parser import PlanParser
from LLM.scripts.generation.utils import Achievement
from LLM.scripts.generation.generate_prompt import generate_prompt

# Create instances for tests
detector = WorkflowDetector()
parser = PlanParser()
extract_handoff_section = parser.extract_handoff_section
find_next_achievement_from_plan = detector.find_next_achievement_from_plan
find_next_achievement_hybrid = detector.find_next_achievement_hybrid


class TestExtractHandoffSection(unittest.TestCase):
    """Test extract_handoff_section function."""

    def test_normal_extraction(self):
        """Test normal extraction of handoff section."""
        plan_content = """# PLAN: Test Feature

## 📝 Current Status & Handoff (For Pause/Resume)

**Last Updated**: 2025-11-08 00:30 UTC  
**Status**: In Progress

**Completed Achievements**: 5/10 (50%)

**Summary**: 
- ✅ Achievement 0.1 Complete
- ⏳ Next: Achievement 0.2 (Next Task)

**When Resuming**:
1. Follow protocol
2. Read this section

---

## Other Section

Some other content here.
"""
        result = extract_handoff_section(plan_content)
        self.assertIsNotNone(result)
        self.assertIn("Last Updated", result)
        self.assertIn("Next: Achievement 0.2", result)
        self.assertNotIn("Other Section", result)

    def test_missing_section(self):
        """Test handling of missing handoff section."""
        plan_content = """# PLAN: Test Feature

## Other Section

Some content here.
"""
        result = extract_handoff_section(plan_content)
        self.assertIsNone(result)

    def test_empty_section(self):
        """Test handling of empty handoff section."""
        plan_content = """# PLAN: Test Feature

## 📝 Current Status & Handoff

---

## Other Section

Some content here.
"""
        result = extract_handoff_section(plan_content)
        # Empty section should return None
        self.assertIsNone(result)

    def test_section_variations(self):
        """Test different header format variations."""
        # Test without emoji
        plan_content1 = """# PLAN: Test Feature

## Current Status & Handoff

**Next**: Achievement 1.1

---

## Other Section
"""
        result1 = extract_handoff_section(plan_content1)
        self.assertIsNotNone(result1)
        self.assertIn("Next", result1)

        # Test with different spacing
        plan_content2 = """# PLAN: Test Feature

##  📝  Current Status & Handoff  

**Next**: Achievement 1.1

---

## Other Section
"""
        result2 = extract_handoff_section(plan_content2)
        self.assertIsNotNone(result2)

    def test_stops_at_next_section(self):
        """Test that extraction stops at next ## header."""
        plan_content = """# PLAN: Test Feature

## 📝 Current Status & Handoff

**Next**: Achievement 1.1
Some content here.

## Other Section

This should not be included.
"""
        result = extract_handoff_section(plan_content)
        self.assertIsNotNone(result)
        self.assertIn("Next", result)
        self.assertIn("Some content", result)
        self.assertNotIn("This should not be included", result)

    def test_case_insensitive(self):
        """Test that header matching is case-insensitive."""
        plan_content = """# PLAN: Test Feature

## current status & handoff

**Next**: Achievement 1.1

---

## Other Section
"""
        result = extract_handoff_section(plan_content)
        self.assertIsNotNone(result)
        self.assertIn("Next", result)

    def test_multiple_sections_after(self):
        """Test that it stops at first ## header after handoff."""
        plan_content = """# PLAN: Test Feature

## 📝 Current Status & Handoff

**Next**: Achievement 1.1

## First Section

Content 1

## Second Section

Content 2
"""
        result = extract_handoff_section(plan_content)
        self.assertIsNotNone(result)
        self.assertIn("Next", result)
        self.assertNotIn("Content 1", result)
        self.assertNotIn("Content 2", result)


class TestFindNextAchievementFromPlan(unittest.TestCase):
    """Test find_next_achievement_from_plan function."""

    def test_handoff_section_priority(self):
        """Test that handoff section is prioritized over full file."""
        plan_content = """# PLAN: Test Feature

## Some Section

**Next**: Review plan, create first SUBPLAN (Achievement 0.1 - Old Section)

---

## 📝 Current Status & Handoff (For Pause/Resume)

**Last Updated**: 2025-11-08 00:40 UTC  
**Status**: In Progress

**Summary**: 
- ✅ Achievement 0.1 Complete
- ⏳ Next: Achievement 3.3 (High Priority Issues Fixed)

---

## Other Section

Some content here.
"""
        result = find_next_achievement_from_plan(plan_content)
        # Should return 3.3 from handoff section, not 0.1 from old section
        self.assertEqual(result, "3.3")

    def test_handoff_section_format_variations(self):
        """Test different formats in handoff section."""
        # Test with ⏳ Next: format
        plan_content1 = """# PLAN: Test Feature

## 📝 Current Status & Handoff

⏳ Next: Achievement 1.1

---

## Other Section
"""
        result1 = find_next_achievement_from_plan(plan_content1)
        self.assertEqual(result1, "1.1")

        # Test with **What's Next**: format
        plan_content2 = """# PLAN: Test Feature

## 📝 Current Status & Handoff

**What's Next**: Achievement 2.2

---

## Other Section
"""
        result2 = find_next_achievement_from_plan(plan_content2)
        self.assertEqual(result2, "2.2")

        # Test with Next: format
        plan_content3 = """# PLAN: Test Feature

## 📝 Current Status & Handoff

Next: Achievement 3.3

---

## Other Section
"""
        result3 = find_next_achievement_from_plan(plan_content3)
        self.assertEqual(result3, "3.3")

    def test_fallback_to_full_file(self):
        """Test fallback to full file when handoff section missing."""
        plan_content = """# PLAN: Test Feature

## Some Section

Next: Achievement 1.1 (No handoff section)

---

## Other Section
"""
        result = find_next_achievement_from_plan(plan_content)
        # Should find 1.1 from full file search
        self.assertEqual(result, "1.1")

    def test_pattern_order(self):
        """Test that Pattern 4 (⏳ Next:) is checked before Pattern 1 (**Next**:)."""
        plan_content = """# PLAN: Test Feature

## 📝 Current Status & Handoff

**Next**: Review plan, create first SUBPLAN (Achievement 0.1 - Old format)
⏳ Next: Achievement 3.3 (New format)

---

## Other Section
"""
        result = find_next_achievement_from_plan(plan_content)
        # Pattern 4 (⏳ Next:) should match first, not Pattern 1 (**Next**:)
        self.assertEqual(result, "3.3")

    def test_real_plan_file(self):
        """Test with actual PLAN_API-REVIEW-AND-TESTING.md file."""
        plan_path = (
            Path(__file__).parent.parent.parent.parent.parent / "PLAN_API-REVIEW-AND-TESTING.md"
        )
        if plan_path.exists():
            with open(plan_path, "r", encoding="utf-8") as f:
                plan_content = f.read()

            result = find_next_achievement_from_plan(plan_content)
            # Should return 3.3, not 0.1
            self.assertEqual(
                result, "3.3", "Should return 3.3 from handoff section, not 0.1 from old section"
            )

    def test_no_match(self):
        """Test when no 'Next' mention found."""
        plan_content = """# PLAN: Test Feature

## Some Section

No achievement mentions here.

---

## Other Section
"""
        result = find_next_achievement_from_plan(plan_content)
        self.assertIsNone(result)


class TestRegressionWithOtherPlans(unittest.TestCase):
    """Regression tests with other PLAN files to ensure no breakage."""

    def test_plan_community_detection_refactor(self):
        """Test with PLAN_COMMUNITY-DETECTION-REFACTOR.md."""
        plan_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "PLAN_COMMUNITY-DETECTION-REFACTOR.md"
        )
        if plan_path.exists():
            with open(plan_path, "r", encoding="utf-8") as f:
                plan_content = f.read()

            result = find_next_achievement_from_plan(plan_content)
            # Should return a valid achievement number or None (not crash)
            if result:
                self.assertRegex(result, r"^\d+\.\d+$", "Should return valid achievement format")

    def test_plan_entity_resolution_refactor(self):
        """Test with PLAN_ENTITY-RESOLUTION-REFACTOR.md."""
        plan_path = (
            Path(__file__).parent.parent.parent.parent.parent / "PLAN_ENTITY-RESOLUTION-REFACTOR.md"
        )
        if plan_path.exists():
            with open(plan_path, "r", encoding="utf-8") as f:
                plan_content = f.read()

            result = find_next_achievement_from_plan(plan_content)
            # Should return a valid achievement number or None (not crash)
            if result:
                self.assertRegex(result, r"^\d+\.\d+$", "Should return valid achievement format")

    def test_plan_extraction_quality_enhancement(self):
        """Test with PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md."""
        plan_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md"
        )
        if plan_path.exists():
            with open(plan_path, "r", encoding="utf-8") as f:
                plan_content = f.read()

            result = find_next_achievement_from_plan(plan_content)
            # Should return a valid achievement number or None (not crash)
            if result:
                self.assertRegex(result, r"^\d+\.\d+$", "Should return valid achievement format")


class TestEdgeCases(unittest.TestCase):
    """Edge case tests for achievement detection."""

    def test_multiple_achievements_in_handoff(self):
        """Test handling of multiple 'Next' mentions in handoff section."""
        plan_content = """# PLAN: Test Feature

## 📝 Current Status & Handoff

**Last Updated**: 2025-11-08 00:50 UTC  
**Status**: In Progress

**Summary**: 
- ✅ Achievement 0.1 Complete
- ⏳ Next: Achievement 3.3 (High Priority Issues Fixed) or Achievement 3.4 (Documentation Updated)

**Old Next**: Achievement 0.1 (should be ignored)

---

## Other Section
"""
        result = find_next_achievement_from_plan(plan_content)
        # Should return 3.3 (first match in handoff section, Pattern 4 priority)
        self.assertEqual(result, "3.3")

    def test_achievement_with_parentheses(self):
        """Test handling of 'Achievement X.Y (Description)' format."""
        plan_content = """# PLAN: Test Feature

## 📝 Current Status & Handoff

⏳ Next: Achievement 2.1 (Test Infrastructure Setup)

---

## Other Section
"""
        result = find_next_achievement_from_plan(plan_content)
        self.assertEqual(result, "2.1")

    def test_achievement_with_dash(self):
        """Test handling of 'Achievement X.Y - Description' format."""
        plan_content = """# PLAN: Test Feature

## 📝 Current Status & Handoff

⏳ Next: Achievement 1.2 - Curl Test Scripts Created

---

## Other Section
"""
        result = find_next_achievement_from_plan(plan_content)
        self.assertEqual(result, "1.2")


class TestFindNextAchievementHybrid(unittest.TestCase):
    """Test find_next_achievement_hybrid function."""

    def test_hybrid_with_handoff_section(self):
        """Test hybrid approach when handoff section is present."""
        plan_content = """# PLAN: Test Feature

## 📝 Current Status & Handoff

⏳ Next: Achievement 1.2

---

## Other Section
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_TEST.md"
        # Create temporary PLAN file
        plan_path.write_text(plan_content)

        try:
            achievements = [
                Achievement(
                    number="1.1", title="First", goal="", effort="", priority="", section_lines=10
                ),
                Achievement(
                    number="1.2", title="Second", goal="", effort="", priority="", section_lines=10
                ),
            ]

            result = find_next_achievement_hybrid(
                plan_path, "TEST", achievements, "./test-archive/"
            )

            # Should return 1.2 from handoff section
            self.assertIsNotNone(result)
            self.assertEqual(result.number, "1.2")
        finally:
            # Cleanup
            if plan_path.exists():
                plan_path.unlink()

    def test_hybrid_fallback_to_archive(self):
        """Test fallback to archive when handoff section missing."""
        plan_content = """# PLAN: Test Feature

## Some Section

No handoff section here.

---
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_TEST.md"
        plan_path.write_text(plan_content)

        try:
            achievements = [
                Achievement(
                    number="1.1", title="First", goal="", effort="", priority="", section_lines=10
                ),
            ]

            # Archive directory doesn't exist, should fallback to root
            result = find_next_achievement_hybrid(
                plan_path, "TEST", achievements, "./nonexistent-archive/"
            )

            # Should handle gracefully (may return None or fallback)
            # Just verify it doesn't crash
            self.assertTrue(result is None or isinstance(result, Achievement))
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_hybrid_with_invalid_file(self):
        """Test hybrid approach with invalid/missing file."""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_NONEXISTENT.md"

        achievements = [
            Achievement(
                number="1.1", title="First", goal="", effort="", priority="", section_lines=10
            ),
        ]

        # Should handle missing file gracefully
        result = find_next_achievement_hybrid(
            plan_path, "NONEXISTENT", achievements, "./test-archive/"
        )

        # Should not crash, may return None or fallback
        self.assertTrue(result is None or isinstance(result, Achievement))


class TestGeneratePromptIntegration(unittest.TestCase):
    """Integration tests for generate_prompt function."""

    def test_generate_prompt_with_valid_plan(self):
        """Test full prompt generation with valid PLAN file."""
        plan_content = """# PLAN: Test Feature

**Status**: In Progress  
**Created**: 2025-01-27 12:00 UTC  
**Goal**: Test feature  
**Priority**: High

---

## 📝 Current Status & Handoff (For Pause/Resume)

**Last Updated**: 2025-01-27 12:00 UTC  
**Status**: In Progress

⏳ Next: Achievement 1.1 (First Task)

---

## 🎯 Desirable Achievements

### Priority 0: HIGH

**Achievement 1.1**: First Task
- Goal: Complete first task
- Effort: 1 hour

---

**Archive Location**: `documentation/archive/test-feature/`
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_TEST_INTEGRATION.md"
        plan_path.write_text(plan_content)

        try:
            prompt = generate_prompt(plan_path)

            # Should generate valid prompt
            self.assertIsNotNone(prompt)
            self.assertIn("Achievement 1.1", prompt)
            self.assertIn("TEST_INTEGRATION", prompt)  # Feature name from filename
            self.assertNotIn("❌ Error", prompt)  # Should not be error message
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_generate_prompt_with_specific_achievement(self):
        """Test prompt generation with specific achievement number."""
        plan_content = """# PLAN: Test Feature

**Status**: In Progress

---

## 🎯 Desirable Achievements

### Priority 0: HIGH

**Achievement 1.1**: First Task
- Goal: Complete first task

**Achievement 1.2**: Second Task
- Goal: Complete second task

---

**Archive Location**: `documentation/archive/test-feature/`
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_TEST_SPECIFIC.md"
        plan_path.write_text(plan_content)

        try:
            prompt = generate_prompt(plan_path, achievement_num="1.2")

            # Should generate prompt for specific achievement
            self.assertIsNotNone(prompt)
            self.assertIn("Achievement 1.2", prompt)
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_generate_prompt_with_missing_file(self):
        """Test prompt generation with missing PLAN file."""
        plan_path = (
            Path(__file__).parent.parent.parent.parent.parent / "PLAN_NONEXISTENT_INTEGRATION.md"
        )

        # Should handle missing file gracefully
        with self.assertRaises((FileNotFoundError, Exception)):
            generate_prompt(plan_path)

    def test_generate_prompt_with_no_achievements(self):
        """Test prompt generation with PLAN that has no achievements."""
        plan_content = """# PLAN: Test Feature

**Status**: Planning

---

## Other Section

No achievements defined.

---

**Archive Location**: `documentation/archive/test-feature/`
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_NO_ACHIEVEMENTS.md"
        plan_path.write_text(plan_content)

        try:
            prompt = generate_prompt(plan_path)

            # Should return error message when no achievements found
            self.assertIn("❌", prompt)
        finally:
            if plan_path.exists():
                plan_path.unlink()


class TestEdgeCasesIntegration(unittest.TestCase):
    """Edge case tests for generate_prompt integration."""

    def test_empty_plan_file(self):
        """Test with empty PLAN file."""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_EMPTY.md"
        plan_path.write_text("")

        try:
            prompt = generate_prompt(plan_path)

            # Should handle empty file gracefully
            self.assertIsNotNone(prompt)
            # May return error or handle gracefully
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_malformed_plan_file(self):
        """Test with malformed PLAN file."""
        plan_content = """# PLAN: Test Feature

Invalid content without proper structure.

No achievements section.
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_MALFORMED.md"
        plan_path.write_text(plan_content)

        try:
            prompt = generate_prompt(plan_path)

            # Should handle malformed file gracefully
            self.assertIsNotNone(prompt)
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_plan_without_archive_location(self):
        """Test PLAN file without archive location."""
        plan_content = """# PLAN: Test Feature

**Status**: In Progress

---

## 🎯 Desirable Achievements

### Priority 0: HIGH

**Achievement 1.1**: First Task
- Goal: Complete first task

---

No archive location specified.
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_NO_ARCHIVE.md"
        plan_path.write_text(plan_content)

        try:
            prompt = generate_prompt(plan_path)

            # Should handle missing archive location gracefully
            self.assertIsNotNone(prompt)
        finally:
            if plan_path.exists():
                plan_path.unlink()


if __name__ == "__main__":
    unittest.main()
