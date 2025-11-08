"""Unit tests for generate_resume_prompt.py - extract_plan_info and generate_resume_prompt functions."""

import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from LLM.scripts.generation.generate_resume_prompt import (
    extract_plan_info,
    generate_resume_prompt,
)


class TestExtractPlanInfo(unittest.TestCase):
    """Test extract_plan_info function."""

    def test_whats_next_achievement_detection(self):
        """Test 'What's Next' achievement detection."""
        plan_content = """# PLAN: Test Feature

**Status**: Paused

**What's Next**: Achievement 2.3

---

## Other Section
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_TEST_RESUME.md"
        plan_path.write_text(plan_content)
        
        try:
            result = extract_plan_info(plan_path)
            
            self.assertEqual(result["next_achievement"], "2.3")
            self.assertEqual(result["feature_name"], "TEST_RESUME")
            self.assertEqual(result["plan_path"], "PLAN_TEST_RESUME.md")
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_next_achievement_detection(self):
        """Test 'Next' achievement detection."""
        plan_content = """# PLAN: Test Feature

**Status**: Paused

**Next**: Achievement 1.5

---

## Other Section
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_TEST_RESUME.md"
        plan_path.write_text(plan_content)
        
        try:
            result = extract_plan_info(plan_path)
            
            self.assertEqual(result["next_achievement"], "1.5")
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_achievement_title_extraction(self):
        """Test achievement title extraction."""
        plan_content = """# PLAN: Test Feature

**Status**: Paused

**Next**: Achievement 1.2

---

## 🎯 Desirable Achievements

### Priority 0: HIGH

**Achievement 1.2**: Test Infrastructure Setup
- Goal: Create test infrastructure

---

## Other Section
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_TEST_RESUME.md"
        plan_path.write_text(plan_content)
        
        try:
            result = extract_plan_info(plan_path)
            
            self.assertEqual(result["next_achievement"], "1.2")
            self.assertEqual(result["next_title"], "Test Infrastructure Setup")
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_archive_location_extraction(self):
        """Test archive location extraction."""
        plan_content = """# PLAN: Test Feature

**Status**: Paused

**Next**: Achievement 1.1

---

**Archive Location**: `documentation/archive/test-feature/`
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_TEST_RESUME.md"
        plan_path.write_text(plan_content)
        
        try:
            result = extract_plan_info(plan_path)
            
            self.assertEqual(result["archive_location"], "documentation/archive/test-feature/")
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_archive_location_fallback(self):
        """Test archive location fallback to default."""
        plan_content = """# PLAN: Test Feature

**Status**: Paused

**Next**: Achievement 1.1

---

No archive location specified.
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_TEST_RESUME.md"
        plan_path.write_text(plan_content)
        
        try:
            result = extract_plan_info(plan_path)
            
            # Should use default fallback
            self.assertEqual(result["archive_location"], "./feature-archive/")
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_no_achievement_found(self):
        """Test when no achievement information found."""
        plan_content = """# PLAN: Test Feature

**Status**: Paused

---

## Other Section

No achievement information here.
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_TEST_RESUME.md"
        plan_path.write_text(plan_content)
        
        try:
            result = extract_plan_info(plan_path)
            
            # Should return fallback "X.Y" and "[Title]"
            self.assertEqual(result["next_achievement"], "X.Y")
            self.assertEqual(result["next_title"], "[Title]")
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_feature_name_extraction(self):
        """Test feature name extraction from file path."""
        plan_content = """# PLAN: Test Feature

**Status**: Paused
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_MY-FEATURE-RESUME.md"
        plan_path.write_text(plan_content)
        
        try:
            result = extract_plan_info(plan_path)
            
            # Should extract feature name correctly
            self.assertEqual(result["feature_name"], "MY-FEATURE-RESUME")
            self.assertEqual(result["plan_path"], "PLAN_MY-FEATURE-RESUME.md")
        finally:
            if plan_path.exists():
                plan_path.unlink()


class TestGenerateResumePrompt(unittest.TestCase):
    """Test generate_resume_prompt function."""

    def test_generate_prompt_with_valid_info(self):
        """Test prompt generation with valid plan info."""
        plan_content = """# PLAN: Test Feature

**Status**: Paused

**Next**: Achievement 1.2

---

## 🎯 Desirable Achievements

**Achievement 1.2**: Test Infrastructure Setup

---

**Archive Location**: `documentation/archive/test-feature/`
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_TEST_RESUME.md"
        plan_path.write_text(plan_content)
        
        try:
            prompt = generate_resume_prompt(plan_path)
            
            # Should generate valid prompt
            self.assertIsNotNone(prompt)
            self.assertIn("PLAN_TEST_RESUME.md", prompt)
            self.assertIn("Test Feature", prompt)
            self.assertIn("Achievement 1.2", prompt)
            self.assertIn("Test Infrastructure Setup", prompt)
            self.assertIn("PRE-RESUME CHECKLIST", prompt)
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_generate_prompt_with_fallback(self):
        """Test prompt generation when no achievement found (fallback to X.Y)."""
        plan_content = """# PLAN: Test Feature

**Status**: Paused

---

## Other Section

No achievement information.
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_TEST_RESUME.md"
        plan_path.write_text(plan_content)
        
        try:
            prompt = generate_resume_prompt(plan_path)
            
            # Should use fallback "X.Y" and "[Title]"
            self.assertIsNotNone(prompt)
            self.assertIn("Achievement X.Y", prompt)
            self.assertIn("[Title]", prompt)
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_prompt_template_formatting(self):
        """Test that all template placeholders are filled correctly."""
        plan_content = """# PLAN: My Feature

**Next**: Achievement 2.5

---

## 🎯 Desirable Achievements

**Achievement 2.5**: Resume Task

---

**Archive Location**: `documentation/archive/my-feature/`
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_MY_FEATURE_RESUME.md"
        plan_path.write_text(plan_content)
        
        try:
            prompt = generate_resume_prompt(plan_path)
            
            # Verify all placeholders filled
            self.assertIn("PLAN_MY_FEATURE_RESUME.md", prompt)
            self.assertIn("My Feature", prompt)
            self.assertIn("Achievement 2.5", prompt)
            self.assertIn("Resume Task", prompt)
            self.assertIn("documentation/archive/my-feature/", prompt)
            self.assertNotIn("{plan_path}", prompt)  # Should be replaced
            self.assertNotIn("{feature_name}", prompt)  # Should be replaced
            self.assertNotIn("{next_achievement}", prompt)  # Should be replaced
            self.assertNotIn("{next_title}", prompt)  # Should be replaced
            self.assertNotIn("{archive_location}", prompt)  # Should be replaced
        finally:
            if plan_path.exists():
                plan_path.unlink()


class TestIntegration(unittest.TestCase):
    """Integration tests for generate_resume_prompt.py."""

    def test_full_workflow_with_paused_plan(self):
        """Test full workflow with paused PLAN file."""
        plan_content = """# PLAN: Integration Test Resume

**Status**: ⏸️ Paused  
**Created**: 2025-01-27 12:00 UTC

---

## 📝 Current Status & Handoff

**Last Updated**: 2025-01-27 12:00 UTC  
**Status**: Paused

**Next**: Achievement 1.3

---

## 🎯 Desirable Achievements

### Priority 0: HIGH

**Achievement 1.3**: Test Coverage
- Goal: Add tests

---

**Archive Location**: `documentation/archive/integration-test-resume/`
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_INTEGRATION_RESUME.md"
        plan_path.write_text(plan_content)
        
        try:
            prompt = generate_resume_prompt(plan_path)
            
            # Should generate complete prompt
            self.assertIsNotNone(prompt)
            self.assertIn("PLAN_INTEGRATION_RESUME.md", prompt)
            self.assertIn("Integration Test Resume", prompt)
            self.assertIn("Achievement 1.3", prompt)
            self.assertIn("PRE-RESUME CHECKLIST", prompt)
            self.assertIn("VALIDATION ENFORCEMENT", prompt)
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_with_missing_file(self):
        """Test with missing PLAN file."""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_NONEXISTENT_RESUME.md"
        
        # Should raise FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            generate_resume_prompt(plan_path)


class TestEdgeCases(unittest.TestCase):
    """Edge case tests for generate_resume_prompt.py."""

    def test_empty_plan_file(self):
        """Test with empty PLAN file."""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_EMPTY_RESUME.md"
        plan_path.write_text("")
        
        try:
            prompt = generate_resume_prompt(plan_path)
            
            # Should handle empty file gracefully
            self.assertIsNotNone(prompt)
            self.assertIn("Achievement X.Y", prompt)  # Fallback
            self.assertIn("[Title]", prompt)  # Fallback
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_plan_without_achievements(self):
        """Test PLAN file without any achievement information."""
        plan_content = """# PLAN: No Achievements

**Status**: Paused

---

## Other Section

No achievement mentions anywhere.
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_NO_ACHIEVEMENTS_RESUME.md"
        plan_path.write_text(plan_content)
        
        try:
            prompt = generate_resume_prompt(plan_path)
            
            # Should use fallback "X.Y" and "[Title]"
            self.assertIsNotNone(prompt)
            self.assertIn("Achievement X.Y", prompt)
            self.assertIn("[Title]", prompt)
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_achievement_format_variations(self):
        """Test various achievement format variations."""
        # Test with parentheses
        plan_content1 = """# PLAN: Test

**Next**: Achievement 2.1 (Test Task)
"""
        plan_path1 = Path(__file__).parent.parent.parent.parent.parent / "PLAN_VARIATION1_RESUME.md"
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
        plan_path2 = Path(__file__).parent.parent.parent.parent.parent / "PLAN_VARIATION2_RESUME.md"
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

**next**: Achievement 1.4
**WHAT'S NEXT**: Achievement 2.5
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_CASE_TEST_RESUME.md"
        plan_path.write_text(plan_content)
        
        try:
            result = extract_plan_info(plan_path)
            
            # Should match case-insensitively (first match wins)
            self.assertEqual(result["next_achievement"], "1.4")
        finally:
            if plan_path.exists():
                plan_path.unlink()

    def test_archive_location_with_quotes(self):
        """Test archive location extraction with quotes."""
        plan_content = """# PLAN: Test

**Next**: Achievement 1.1

---

**Archive Location**: `"documentation/archive/test-feature/"`
"""
        plan_path = Path(__file__).parent.parent.parent.parent.parent / "PLAN_QUOTES_TEST.md"
        plan_path.write_text(plan_content)
        
        try:
            result = extract_plan_info(plan_path)
            
            # Should strip quotes
            self.assertEqual(result["archive_location"], "documentation/archive/test-feature/")
        finally:
            if plan_path.exists():
                plan_path.unlink()


if __name__ == "__main__":
    unittest.main()


