#!/usr/bin/env python3
"""
Test Suite for Generate FIX Prompt Module

Tests the FIX prompt generation system added in Achievement 2.9.

Test Coverage:
- extract_fix_issues() parser with various FIX file formats
- generate_fix_prompt() end-to-end generation
- Real-world validation with actual FIX_21.md
- Edge cases and error handling

Created: 2025-11-13
Achievement: 2.9 - Implement FIX Feedback Detection & Prompt Generation
"""
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from LLM.scripts.generation.generate_fix_prompt import extract_fix_issues, generate_fix_prompt


class TestExtractFixIssues(unittest.TestCase):
    """Test the extract_fix_issues() parser function."""

    def setUp(self):
        """Set up test fixtures with temporary directory."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_extract_metadata(self):
        """Test extracting metadata from FIX file header."""
        fix_content = """# FIX REQUIRED: Achievement 2.1

**Reviewer**: John Doe
**Review Date**: 2025-11-13
**Status**: ⚠️ NEEDS FIXES

---
"""
        fix_file = self.test_dir / "FIX_21.md"
        fix_file.write_text(fix_content)

        result = extract_fix_issues(fix_file)

        self.assertEqual(result["reviewer"], "John Doe")
        self.assertEqual(result["review_date"], "2025-11-13")
        self.assertEqual(result["status"], "⚠️ NEEDS FIXES")

    def test_extract_critical_issues(self):
        """Test extracting critical issues with #### headers."""
        fix_content = """# FIX REQUIRED: Achievement 2.1

**Reviewer**: Test
**Review Date**: 2025-11-13

### Critical Issues (must fix)

#### 1. **PRIMARY OBJECTIVE NOT ACHIEVED** ⚠️ BLOCKER

**Issue**: No valid baseline metrics established

**Evidence**:
- SUBPLAN objective not met
- No successful end-to-end pipeline completion

**Impact**: Cannot proceed to next achievement

**Fix Required**:
1. Execute pipeline end-to-end
2. Verify all stages complete

---

#### 2. **REQUIRED DELIVERABLES MISSING** ⚠️ BLOCKER

**Issue**: 3 of 3 required deliverables not created

**Fix Required**: Create all 3 documents

---
"""
        fix_file = self.test_dir / "FIX_21.md"
        fix_file.write_text(fix_content)

        result = extract_fix_issues(fix_file)

        self.assertEqual(len(result["critical_issues"]), 2)
        self.assertEqual(result["critical_issues"][0]["title"], "PRIMARY OBJECTIVE NOT ACHIEVED")
        self.assertIn("No valid baseline metrics", result["critical_issues"][0]["body"])
        self.assertEqual(result["critical_issues"][1]["title"], "REQUIRED DELIVERABLES MISSING")

    def test_extract_minor_issues(self):
        """Test extracting minor issues from bullet list."""
        fix_content = """# FIX REQUIRED

### Critical Issues
(none)

### Minor Issues

- Improve documentation clarity
- Add more test coverage
- Refactor long functions

---
"""
        fix_file = self.test_dir / "FIX_01.md"
        fix_file.write_text(fix_content)

        result = extract_fix_issues(fix_file)

        self.assertEqual(len(result["minor_issues"]), 3)
        self.assertEqual(result["minor_issues"][0]["text"], "Improve documentation clarity")
        self.assertEqual(result["minor_issues"][1]["text"], "Add more test coverage")

    def test_extract_code_references(self):
        """Test extracting code references (@Python, @TypeScript patterns)."""
        fix_content = """# FIX REQUIRED

### Critical Issues

#### 1. **Fix Bug**

See @Python (779-1075) and @Python (873-1075) for the issues.
Also review @TypeScript (45-120) for similar pattern.

---
"""
        fix_file = self.test_dir / "FIX_01.md"
        fix_file.write_text(fix_content)

        result = extract_fix_issues(fix_file)

        self.assertEqual(len(result["code_references"]), 3)
        self.assertIn("@Python (779-1075)", result["code_references"])
        self.assertIn("@Python (873-1075)", result["code_references"])
        self.assertIn("@TypeScript (45-120)", result["code_references"])

    def test_extract_what_worked_well(self):
        """Test extracting 'What Worked Well' section."""
        fix_content = """# FIX REQUIRED

### Critical Issues
(none)

## What Worked Well

- Excellent debugging work
- Clear documentation
- Good test coverage

---
"""
        fix_file = self.test_dir / "FIX_01.md"
        fix_file.write_text(fix_content)

        result = extract_fix_issues(fix_file)

        self.assertEqual(len(result["what_worked_well"]), 3)
        self.assertEqual(result["what_worked_well"][0], "Excellent debugging work")

    def test_handle_missing_sections_gracefully(self):
        """Test parser handles missing sections without errors."""
        fix_content = """# FIX REQUIRED

**Reviewer**: Test
**Review Date**: 2025-11-13

(Minimal content, missing most sections)
"""
        fix_file = self.test_dir / "FIX_01.md"
        fix_file.write_text(fix_content)

        result = extract_fix_issues(fix_file)

        # Should return empty lists, not raise errors
        self.assertEqual(len(result["critical_issues"]), 0)
        self.assertEqual(len(result["minor_issues"]), 0)
        self.assertEqual(len(result["code_references"]), 0)
        self.assertEqual(len(result["what_worked_well"]), 0)
        self.assertEqual(result["reviewer"], "Test")


class TestGenerateFixPrompt(unittest.TestCase):
    """Test the generate_fix_prompt() function."""

    def setUp(self):
        """Set up test fixtures with temporary directory."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.plan_dir = Path(self.temp_dir.name) / "FEATURE"
        self.plan_file = self.plan_dir / "PLAN_FEATURE.md"
        self.feedbacks_dir = self.plan_dir / "execution" / "feedbacks"

        # Create directory structure
        self.plan_dir.mkdir(parents=True)
        self.plan_file.write_text("# PLAN: FEATURE")
        self.feedbacks_dir.mkdir(parents=True)

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_generate_prompt_with_critical_issues(self):
        """Test generating FIX prompt with critical issues."""
        fix_content = """# FIX REQUIRED: Achievement 2.1

**Reviewer**: John Doe
**Review Date**: 2025-11-13
**Status**: ⚠️ NEEDS FIXES

### Critical Issues (must fix)

#### 1. **PRIMARY OBJECTIVE NOT ACHIEVED**

**Issue**: No valid baseline metrics established
**Fix Required**: Execute pipeline end-to-end

---
"""
        fix_file = self.feedbacks_dir / "FIX_21.md"
        fix_file.write_text(fix_content)

        prompt = generate_fix_prompt(self.plan_file, "2.1")

        # Verify prompt contains key sections
        self.assertIn("REVIEWER FEEDBACK: NEEDS FIXES", prompt)
        self.assertIn("Reviewer: John Doe", prompt)
        self.assertIn("CRITICAL ISSUES TO FIX", prompt)
        self.assertIn("PRIMARY OBJECTIVE NOT ACHIEVED", prompt)
        self.assertIn("FIX ACTION PLAN", prompt)
        self.assertIn("FIX_21_RESOLUTION.md", prompt)

    def test_generate_prompt_with_code_references(self):
        """Test FIX prompt includes extracted code references."""
        fix_content = """# FIX REQUIRED

**Reviewer**: Test
**Review Date**: 2025-11-13

### Critical Issues

#### 1. **Fix Bug**

See @Python (779-1075) for the issue.

---
"""
        fix_file = self.feedbacks_dir / "FIX_01.md"
        fix_file.write_text(fix_content)

        prompt = generate_fix_prompt(self.plan_file, "0.1")

        self.assertIn("CODE REFERENCES FROM FEEDBACK", prompt)
        self.assertIn("@Python (779-1075)", prompt)

    def test_generate_prompt_with_minor_issues(self):
        """Test FIX prompt includes minor issues section."""
        fix_content = """# FIX REQUIRED

**Reviewer**: Test
**Review Date**: 2025-11-13

### Critical Issues
(none)

### Minor Issues

- Improve documentation
- Add tests

---
"""
        fix_file = self.feedbacks_dir / "FIX_01.md"
        fix_file.write_text(fix_content)

        prompt = generate_fix_prompt(self.plan_file, "0.1")

        self.assertIn("MINOR ISSUES", prompt)
        self.assertIn("Improve documentation", prompt)
        self.assertIn("Add tests", prompt)

    def test_generate_prompt_with_what_worked_well(self):
        """Test FIX prompt includes positive feedback section."""
        fix_content = """# FIX REQUIRED

**Reviewer**: Test
**Review Date**: 2025-11-13

### Critical Issues
(none)

## What Worked Well

- Excellent debugging work

---
"""
        fix_file = self.feedbacks_dir / "FIX_01.md"
        fix_file.write_text(fix_content)

        prompt = generate_fix_prompt(self.plan_file, "0.1")

        self.assertIn("WHAT WORKED WELL", prompt)
        self.assertIn("Excellent debugging work", prompt)

    def test_error_when_fix_file_missing(self):
        """Test error handling when FIX file doesn't exist."""
        # No FIX file created

        prompt = generate_fix_prompt(self.plan_file, "0.1")

        self.assertIn("Error: FIX file not found", prompt)
        self.assertIn("FIX_01.md", prompt)


class TestRealWorldValidation(unittest.TestCase):
    """
    Test with actual FIX_21.md from GRAPHRAG plan (if available).

    This validates that the parser handles real-world FIX file format.
    """

    def test_parse_real_fix_21_file(self):
        """Test parsing actual FIX_21.md file."""
        fix_file = Path(
            "work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/execution/feedbacks/FIX_21.md"
        )

        if not fix_file.exists():
            self.skipTest("Real FIX_21.md file not found - skipping real-world validation")

        # Parse real FIX file
        result = extract_fix_issues(fix_file)

        # Verify basic structure
        self.assertIsInstance(result, dict)
        self.assertIn("critical_issues", result)
        self.assertIn("minor_issues", result)
        self.assertIn("code_references", result)
        self.assertIn("reviewer", result)
        self.assertIn("review_date", result)

        # Verify real data extracted
        self.assertGreater(len(result["critical_issues"]), 0, "Should extract critical issues")
        self.assertNotEqual(result["reviewer"], "Unknown", "Should extract reviewer name")
        self.assertNotEqual(result["review_date"], "Unknown", "Should extract review date")

    def test_generate_prompt_for_real_fix_21(self):
        """Test generating prompt from actual FIX_21.md."""
        plan_file = Path(
            "work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/PLAN_GRAPHRAG-OBSERVABILITY-VALIDATION.md"
        )

        if not plan_file.exists():
            self.skipTest("Real PLAN file not found - skipping real-world validation")

        fix_file = plan_file.parent / "execution" / "feedbacks" / "FIX_21.md"
        if not fix_file.exists():
            self.skipTest("Real FIX_21.md file not found - skipping real-world validation")

        # Generate prompt
        prompt = generate_fix_prompt(plan_file, "2.1")

        # Verify prompt structure
        self.assertIn("REVIEWER FEEDBACK", prompt)
        self.assertIn("CRITICAL ISSUES TO FIX", prompt)
        self.assertIn("FIX ACTION PLAN", prompt)
        self.assertIn("FIX_21_RESOLUTION.md", prompt)

        # Verify no errors in prompt
        self.assertNotIn("Error:", prompt)


if __name__ == "__main__":
    unittest.main()
