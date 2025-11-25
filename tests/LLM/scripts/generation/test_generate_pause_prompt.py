"""Unit tests for generate_pause_prompt.py - extract_plan_info and generate_pause_prompt functions."""

import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from LLM.scripts.generation.generate_pause_prompt import (
    extract_plan_info,
    generate_pause_prompt,
)


class TestExtractPlanInfo(unittest.TestCase):
    """Test extract_plan_info function."""

    def test_priority_1_next_achievement(self):
        """Test Priority 1: 'Next Achievement' detection."""
        plan_content = """# PLAN: Test Feature

**Status**: In Progress

**Next Achievement**: 2.3

---

## Other Section
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_TEST_PAUSE.md"
        plan_path.write_text(plan_content)
        
        try:
            result = extract_plan_info(plan_path)
            
            self.assertEqual(result["next_achievement"], "2.3")
            self.assertEqual(result["feature_name"], "TEST_PAUSE")
            self.assertEqual(result["plan_path"], "PLAN_TEST_PAUSE.md")
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_priority_2_whats_next(self):
        """Test Priority 2: 'What's Next' section detection."""
        plan_content = """# PLAN: Test Feature

**Status**: In Progress

**What's Next**: Achievement 1.5

---

## Other Section
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_TEST_PAUSE.md"
        plan_path.write_text(plan_content)
        
        try:
            result = extract_plan_info(plan_path)
            
            self.assertEqual(result["next_achievement"], "1.5")
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_priority_3_paused_at(self):
        """Test Priority 3: 'Paused At' detection."""
        plan_content = """# PLAN: Test Feature

**Status**: Paused

**Paused At**: Achievement 3.1

---

## Other Section
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_TEST_PAUSE.md"
        plan_path.write_text(plan_content)
        
        try:
            result = extract_plan_info(plan_path)
            
            self.assertEqual(result["next_achievement"], "3.1")
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_fallback_completed_achievement(self):
        """Test fallback to last completed achievement."""
        plan_content = """# PLAN: Test Feature

**Status**: In Progress

**Summary**:
- ✅ Achievement 0.1 complete
- ✅ Achievement 0.2 complete
- ✅ Achievement 1.1 complete

---

## Other Section
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_TEST_PAUSE.md"
        plan_path.write_text(plan_content)
        
        try:
            result = extract_plan_info(plan_path)
            
            # Should return last completed achievement (1.1)
            self.assertEqual(result["next_achievement"], "1.1")
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_priority_order(self):
        """Test that Priority 1 takes precedence over Priority 2."""
        plan_content = """# PLAN: Test Feature

**Next Achievement**: 2.1
**What's Next**: Achievement 1.5

---

## Other Section
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_TEST_PAUSE.md"
        plan_path.write_text(plan_content)
        
        try:
            result = extract_plan_info(plan_path)
            
            # Priority 1 should win (2.1, not 1.5)
            self.assertEqual(result["next_achievement"], "2.1")
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_no_achievement_found(self):
        """Test when no achievement information found."""
        plan_content = """# PLAN: Test Feature

**Status**: Planning

---

## Other Section

No achievement information here.
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_TEST_PAUSE.md"
        plan_path.write_text(plan_content)
        
        try:
            result = extract_plan_info(plan_path)
            
            # Should return fallback "X.Y"
            self.assertEqual(result["next_achievement"], "X.Y")
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_feature_name_extraction(self):
        """Test feature name extraction from file path."""
        plan_content = """# PLAN: Test Feature

**Status**: In Progress
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_MY-FEATURE.md"
        plan_path.write_text(plan_content)
        
        try:
            result = extract_plan_info(plan_path)
            
            # Should extract feature name correctly
            self.assertEqual(result["feature_name"], "MY-FEATURE")
            self.assertEqual(result["plan_path"], "PLAN_MY-FEATURE.md")
        finally:
            if plan_path.exists():
                plan_path.unlink()


class TestGeneratePausePrompt(unittest.TestCase):
    """Test generate_pause_prompt function."""

    def test_generate_prompt_with_valid_info(self):
        """Test prompt generation with valid plan info."""
        plan_content = """# PLAN: Test Feature

**Status**: In Progress

**Next Achievement**: 1.2

---

## Other Section
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_TEST_PAUSE.md"
        plan_path.write_text(plan_content)
        
        try:
            prompt = generate_pause_prompt(plan_path)
            
            # Should generate valid prompt
            self.assertIsNotNone(prompt)
            self.assertIn("PLAN_TEST_PAUSE.md", prompt)
            self.assertIn("TEST_PAUSE", prompt)  # Feature name from filename, not title
            self.assertIn("Achievement 1.2", prompt)
            self.assertIn("PRE-PAUSE CHECKLIST", prompt)
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_generate_prompt_with_fallback(self):
        """Test prompt generation when no achievement found (fallback to X.Y)."""
        plan_content = """# PLAN: Test Feature

**Status**: Planning

---

## Other Section

No achievement information.
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_TEST_PAUSE.md"
        plan_path.write_text(plan_content)
        
        try:
            prompt = generate_pause_prompt(plan_path)
            
            # Should use fallback "X.Y"
            self.assertIsNotNone(prompt)
            self.assertIn("Achievement X.Y", prompt)
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_prompt_template_formatting(self):
        """Test that all template placeholders are filled correctly."""
        plan_content = """# PLAN: My Feature

**Next Achievement**: 2.5

---
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_MY_FEATURE.md"
        plan_path.write_text(plan_content)
        
        try:
            prompt = generate_pause_prompt(plan_path)
            
            # Verify all placeholders filled
            self.assertIn("PLAN_MY_FEATURE.md", prompt)
            self.assertIn("MY_FEATURE", prompt)  # Feature name from filename
            self.assertIn("Achievement 2.5", prompt)
            self.assertNotIn("{plan_path}", prompt)  # Should be replaced
            self.assertNotIn("{feature_name}", prompt)  # Should be replaced
            self.assertNotIn("{achievement}", prompt)  # Should be replaced
        finally:
            if plan_path.exists():
                plan_path.unlink()


class TestIntegration(unittest.TestCase):
    """Integration tests for generate_pause_prompt.py."""

    def test_full_workflow_with_sample_plan(self):
        """Test full workflow with sample PLAN file."""
        plan_content = """# PLAN: Integration Test

**Status**: In Progress  
**Created**: 2025-01-27 12:00 UTC

---

## 📝 Current Status & Handoff

**Last Updated**: 2025-01-27 12:00 UTC  
**Status**: In Progress

**Next Achievement**: 1.3

---

## 🎯 Desirable Achievements

### Priority 0: HIGH

**Achievement 1.3**: Test Coverage
- Goal: Add tests

---

**Archive Location**: `documentation/archive/integration-test/`
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_INTEGRATION_PAUSE.md"
        plan_path.write_text(plan_content)
        
        try:
            prompt = generate_pause_prompt(plan_path)
            
            # Should generate complete prompt
            self.assertIsNotNone(prompt)
            self.assertIn("PLAN_INTEGRATION_PAUSE.md", prompt)
            self.assertIn("Integration Test", prompt)
            self.assertIn("Achievement 1.3", prompt)
            self.assertIn("PRE-PAUSE CHECKLIST", prompt)
            self.assertIn("VALIDATION ENFORCEMENT", prompt)
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_with_missing_file(self):
        """Test with missing PLAN file."""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_NONEXISTENT_PAUSE.md"
        
        # Should raise FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            generate_pause_prompt(plan_path)


class TestEdgeCases(unittest.TestCase):
    """Edge case tests for generate_pause_prompt.py."""

    def test_empty_plan_file(self):
        """Test with empty PLAN file."""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_EMPTY_PAUSE.md"
        plan_path.write_text("")
        
        try:
            prompt = generate_pause_prompt(plan_path)
            
            # Should handle empty file gracefully
            self.assertIsNotNone(prompt)
            self.assertIn("Achievement X.Y", prompt)  # Fallback
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_plan_without_achievements(self):
        """Test PLAN file without any achievement information."""
        plan_content = """# PLAN: No Achievements

**Status**: Planning

---

## Other Section

No achievement mentions anywhere.
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_NO_ACHIEVEMENTS_PAUSE.md"
        plan_path.write_text(plan_content)
        
        try:
            prompt = generate_pause_prompt(plan_path)
            
            # Should use fallback "X.Y"
            self.assertIsNotNone(prompt)
            self.assertIn("Achievement X.Y", prompt)
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_achievement_format_variations(self):
        """Test various achievement format variations."""
        # Test with parentheses
        plan_content1 = """# PLAN: Test

**Next Achievement**: 2.1 (Test Task)
"""
        plan_path1 = Path(__file__).parent.parent.parent.parent.parent / "PLAN_VARIATION1.md"
        plan_path1.write_text(plan_content1)
        
        try:
            result1 = extract_plan_info(plan_path1)
            self.assertEqual(result1["next_achievement"], "2.1")
        finally:
            if plan_path1.exists():
                plan_path1.unlink()

        # Test with dash
        plan_content2 = """# PLAN: Test

**What's Next**: Achievement 3.2 - Another Task
"""
        plan_path2 = Path(__file__).parent.parent.parent.parent.parent / "PLAN_VARIATION2.md"
        plan_path2.write_text(plan_content2)
        
        try:
            result2 = extract_plan_info(plan_path2)
            self.assertEqual(result2["next_achievement"], "3.2")
        finally:
            if plan_path2.exists():
                plan_path2.unlink()

    def test_case_insensitive_matching(self):
        """Test that matching is case-insensitive."""
        plan_content = """# PLAN: Test

**next achievement**: 1.4
**WHAT'S NEXT**: Achievement 2.5
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_CASE_TEST.md"
        plan_path.write_text(plan_content)
        
        try:
            result = extract_plan_info(plan_path)
            
            # Should match case-insensitively (Priority 1 wins)
            self.assertEqual(result["next_achievement"], "1.4")
        finally:
            if plan_path.exists():
                plan_path.unlink()


if __name__ == "__main__":
    unittest.main()


