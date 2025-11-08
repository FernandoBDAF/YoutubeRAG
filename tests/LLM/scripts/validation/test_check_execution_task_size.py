"""Unit tests for check_execution_task_size.py - EXECUTION_TASK size limit validation."""

import unittest
import sys
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from LLM.scripts.validation.check_execution_task_size import (
    count_lines,
    check_limit,
)


class TestCountLines(unittest.TestCase):
    """Test count_lines function."""

    def test_normal_file(self):
        """Test counting lines in normal file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write("Line 1\nLine 2\nLine 3\n")
            temp_path = Path(f.name)

        try:
            result = count_lines(temp_path)
            self.assertEqual(result, 3)
        finally:
            temp_path.unlink()

    def test_empty_file(self):
        """Test counting lines in empty file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            temp_path = Path(f.name)

        try:
            result = count_lines(temp_path)
            self.assertEqual(result, 0)
        finally:
            temp_path.unlink()

    def test_single_line(self):
        """Test counting single line file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write("Single line")
            temp_path = Path(f.name)

        try:
            result = count_lines(temp_path)
            self.assertEqual(result, 1)
        finally:
            temp_path.unlink()

    def test_multiline_file(self):
        """Test counting lines in multi-line file."""
        lines = "\n".join([f"Line {i}" for i in range(1, 101)])
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(lines)
            temp_path = Path(f.name)

        try:
            result = count_lines(temp_path)
            self.assertEqual(result, 100)
        finally:
            temp_path.unlink()

    def test_file_with_empty_lines(self):
        """Test counting lines including empty lines."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write("Line 1\n\nLine 3\n\n\nLine 6\n")
            temp_path = Path(f.name)

        try:
            result = count_lines(temp_path)
            # File has: Line 1, empty, Line 3, empty, empty, Line 6, empty (last newline)
            self.assertEqual(result, 6)  # 6 lines total
        finally:
            temp_path.unlink()


class TestCheckLimit(unittest.TestCase):
    """Test check_limit function."""

    def test_within_limits_small(self):
        """Test EXECUTION_TASK well within limits (< 150 lines)."""
        content = "# EXECUTION_TASK: Test\n\n" + "\n".join(["Line"] * 100)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            pass_check, message = check_limit(temp_path)
            self.assertTrue(pass_check)
            self.assertIn("✅ EXECUTION_TASK WITHIN LIMITS", message)
            self.assertIn("Lines: 102", message)
        finally:
            temp_path.unlink()

    def test_within_limits_approaching(self):
        """Test EXECUTION_TASK within limits but approaching (120-149 lines)."""
        content = "# EXECUTION_TASK: Test\n\n" + "\n".join(["Line"] * 120)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            pass_check, message = check_limit(temp_path)
            self.assertTrue(pass_check)
            self.assertIn("✅ EXECUTION_TASK WITHIN LIMITS", message)
            self.assertIn("Lines: 122", message)
            self.assertIn("Approaching recommended target", message)
        finally:
            temp_path.unlink()

    def test_warning_at_150(self):
        """Test warning at exactly 150 lines."""
        # Script uses > 150, so 150 is still within limits (no warning)
        content = "\n".join(["Line"] * 150)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            pass_check, message = check_limit(temp_path)
            self.assertTrue(pass_check)  # 150 is within limits (> 150 triggers warning)
            self.assertIn("✅ EXECUTION_TASK WITHIN LIMITS", message)
            self.assertIn("Lines: 150", message)
        finally:
            temp_path.unlink()

    def test_warning_above_150(self):
        """Test warning above 150 lines (150-200)."""
        content = "\n".join(["Line"] * 175)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            pass_check, message = check_limit(temp_path)
            self.assertTrue(pass_check)  # Warning doesn't fail
            self.assertIn("⚠️  EXECUTION_TASK APPROACHING LIMIT", message)
            self.assertIn("Current size: 175 lines", message)
        finally:
            temp_path.unlink()

    def test_warning_at_199(self):
        """Test warning at 199 lines (just below error threshold)."""
        content = "\n".join(["Line"] * 199)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            pass_check, message = check_limit(temp_path)
            self.assertTrue(pass_check)  # Warning doesn't fail
            self.assertIn("⚠️  EXECUTION_TASK APPROACHING LIMIT", message)
            self.assertIn("Current size: 199 lines", message)
        finally:
            temp_path.unlink()

    def test_error_at_200(self):
        """Test error at exactly 200 lines."""
        # Script uses > 200, so 200 is still within limits (warning, not error)
        content = "\n".join(["Line"] * 200)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            pass_check, message = check_limit(temp_path)
            self.assertTrue(pass_check)  # 200 is within limits (> 200 triggers error)
            self.assertIn("⚠️  EXECUTION_TASK APPROACHING LIMIT", message)
            self.assertIn("Current size: 200 lines", message)
            self.assertIn("approaching 200-line limit", message)
        finally:
            temp_path.unlink()

    def test_error_above_200(self):
        """Test error above 200 lines."""
        content = "\n".join(["Line"] * 250)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            pass_check, message = check_limit(temp_path)
            self.assertFalse(pass_check)  # Error fails
            self.assertIn("❌ EXECUTION_TASK EXCEEDS HARD LIMIT", message)
            self.assertIn("Current size: 250 lines", message)
            self.assertIn("exceeds 200-line limit", message)
            self.assertIn("MUST CREATE NEW EXECUTION_TASK", message)
        finally:
            temp_path.unlink()

    def test_boundary_149(self):
        """Test boundary case: 149 lines (just below warning)."""
        content = "\n".join(["Line"] * 149)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            pass_check, message = check_limit(temp_path)
            self.assertTrue(pass_check)
            self.assertIn("✅ EXECUTION_TASK WITHIN LIMITS", message)
            self.assertIn("Lines: 149", message)
        finally:
            temp_path.unlink()

    def test_boundary_151(self):
        """Test boundary case: 151 lines (just above warning)."""
        content = "\n".join(["Line"] * 151)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            pass_check, message = check_limit(temp_path)
            self.assertTrue(pass_check)  # Warning doesn't fail
            self.assertIn("⚠️  EXECUTION_TASK APPROACHING LIMIT", message)
            self.assertIn("Current size: 151 lines", message)
        finally:
            temp_path.unlink()

    def test_boundary_201(self):
        """Test boundary case: 201 lines (just above error)."""
        content = "\n".join(["Line"] * 201)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            pass_check, message = check_limit(temp_path)
            self.assertFalse(pass_check)  # Error fails
            self.assertIn("❌ EXECUTION_TASK EXCEEDS HARD LIMIT", message)
            self.assertIn("Current size: 201 lines", message)
        finally:
            temp_path.unlink()

    def test_missing_file(self):
        """Test handling of missing file."""
        temp_path = Path("/nonexistent/execution_task.md")
        pass_check, message = check_limit(temp_path)
        self.assertFalse(pass_check)
        self.assertIn("❌ Error: File not found", message)

    def test_empty_file(self):
        """Test handling of empty file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            temp_path = Path(f.name)

        try:
            pass_check, message = check_limit(temp_path)
            self.assertTrue(pass_check)  # Empty file is within limits
            self.assertIn("✅ EXECUTION_TASK WITHIN LIMITS", message)
            self.assertIn("Lines: 0", message)
        finally:
            temp_path.unlink()

    def test_very_large_file(self):
        """Test very large file (> 300 lines)."""
        content = "\n".join(["Line"] * 500)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            pass_check, message = check_limit(temp_path)
            self.assertFalse(pass_check)
            self.assertIn("❌ EXECUTION_TASK EXCEEDS HARD LIMIT", message)
            self.assertIn("Current size: 500 lines", message)
            self.assertIn("MUST CREATE NEW EXECUTION_TASK", message)
        finally:
            temp_path.unlink()

    def test_message_contains_actions(self):
        """Test that error message contains required actions."""
        content = "\n".join(["Line"] * 250)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            pass_check, message = check_limit(temp_path)
            self.assertFalse(pass_check)
            self.assertIn("📋 Actions Required:", message)
            self.assertIn("Condense iteration log", message)
            self.assertIn("Prioritize learning summary", message)
            self.assertIn("Create new EXECUTION_TASK", message)
        finally:
            temp_path.unlink()

    def test_warning_contains_recommendations(self):
        """Test that warning message contains recommendations."""
        content = "\n".join(["Line"] * 175)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            pass_check, message = check_limit(temp_path)
            self.assertTrue(pass_check)
            self.assertIn("💡 Recommendations:", message)
            self.assertIn("Condense iteration log", message)
            self.assertIn("Consider creating new EXECUTION_TASK", message)
        finally:
            temp_path.unlink()


class TestIntegration(unittest.TestCase):
    """Integration tests with real EXECUTION_TASK file structure."""

    def test_real_execution_task_structure(self):
        """Test with realistic EXECUTION_TASK file structure."""
        content = """# EXECUTION_TASK: Test Feature

**Mother Plan**: PLAN_TEST.md
**SUBPLAN**: SUBPLAN_TEST_01.md
**Achievement**: 1.1
**Status**: In Progress

## 🎯 Objective

Test objective here.

## 🎯 Approach

1. Step 1
2. Step 2

## 📝 Iteration Log

### Iteration 1: Implementation

**Started**: 2025-01-27
**Status**: Complete

**Actions Taken**:
- Action 1
- Action 2

**Results**:
- Result 1
- Result 2

## 📚 Learning Summary

Key learnings here.

## ✅ Completion Status

**Status**: Complete
"""
        # Add enough lines to be realistic but within limits
        content += "\n".join([f"## Section {i}\nContent here.\n" for i in range(30)])

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            pass_check, message = check_limit(temp_path)
            # Should pass (within limits)
            self.assertTrue(pass_check)
            self.assertIn("✅ EXECUTION_TASK WITHIN LIMITS", message)
        finally:
            temp_path.unlink()


if __name__ == "__main__":
    unittest.main()
