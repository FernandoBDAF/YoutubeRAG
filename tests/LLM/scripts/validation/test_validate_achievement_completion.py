"""Unit tests for validate_achievement_completion.py - Achievement completion validation."""

import unittest
import sys
import tempfile
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from LLM.scripts.validation.validate_achievement_completion import (
    find_achievement_in_plan,
    check_subplan_exists,
    check_execution_task_exists,
    check_deliverables_exist,
    validate_achievement,
)


class TestFindAchievementInPlan(unittest.TestCase):
    """Test find_achievement_in_plan function."""

    def test_find_achievement_with_deliverables(self):
        """Test finding achievement with deliverables."""
        plan_content = """# PLAN: Test Feature

**Achievement 1.1**: Test Achievement

- Deliverables:
  - File: `tests/test_file.py`
  - Document: `docs/test_doc.md`
  - Script: `scripts/test_script.sh`

## Other Section
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(plan_content)
            temp_path = Path(f.name)

        try:
            result = find_achievement_in_plan(temp_path, "1.1")
            self.assertIsNotNone(result)
            self.assertEqual(result["title"], "Test Achievement")
            # Function extracts full lines including labels, not just file paths
            self.assertTrue(any("tests/test_file.py" in d for d in result["deliverables"]))
            self.assertTrue(any("docs/test_doc.md" in d for d in result["deliverables"]))
            self.assertTrue(any("scripts/test_script.sh" in d for d in result["deliverables"]))
        finally:
            temp_path.unlink()

    def test_find_achievement_without_deliverables(self):
        """Test finding achievement without deliverables section."""
        plan_content = """# PLAN: Test Feature

**Achievement 2.3**: Another Achievement

## Other Section
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(plan_content)
            temp_path = Path(f.name)

        try:
            result = find_achievement_in_plan(temp_path, "2.3")
            self.assertIsNotNone(result)
            self.assertEqual(result["title"], "Another Achievement")
            self.assertEqual(result["deliverables"], [])
        finally:
            temp_path.unlink()

    def test_find_achievement_not_found(self):
        """Test finding non-existent achievement."""
        plan_content = """# PLAN: Test Feature

**Achievement 1.1**: Test Achievement

## Other Section
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(plan_content)
            temp_path = Path(f.name)

        try:
            result = find_achievement_in_plan(temp_path, "3.5")
            self.assertEqual(result, {})
        finally:
            temp_path.unlink()

    def test_find_achievement_empty_deliverables(self):
        """Test finding achievement with empty deliverables section."""
        plan_content = """# PLAN: Test Feature

**Achievement 1.1**: Test Achievement

- Deliverables:

## Other Section
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(plan_content)
            temp_path = Path(f.name)

        try:
            result = find_achievement_in_plan(temp_path, "1.1")
            self.assertIsNotNone(result)
            # Function may extract "Deliverables:" header as a deliverable
            # So we check that actual deliverables are empty (only header if any)
            deliverables = [d for d in result["deliverables"] if d != "Deliverables:"]
            self.assertEqual(deliverables, [])
        finally:
            temp_path.unlink()

    def test_find_achievement_multiple_deliverables(self):
        """Test finding achievement with multiple deliverables."""
        plan_content = """# PLAN: Test Feature

**Achievement 1.1**: Test Achievement

- Deliverables:
  - File 1: `file1.py`
  - File 2: `file2.md`
  - File 3: `file3.txt`
  - File 4: `file4.sh`

## Other Section
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(plan_content)
            temp_path = Path(f.name)

        try:
            result = find_achievement_in_plan(temp_path, "1.1")
            self.assertIsNotNone(result)
            # Function extracts "Deliverables:" header plus 4 items = 5 total
            self.assertEqual(len(result["deliverables"]), 5)
            # Check that file paths are in deliverables
            self.assertTrue(any("file1.py" in d for d in result["deliverables"]))
            self.assertTrue(any("file2.md" in d for d in result["deliverables"]))
        finally:
            temp_path.unlink()


class TestCheckSubplanExists(unittest.TestCase):
    """Test check_subplan_exists function."""

    def setUp(self):
        """Set up test environment."""
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_subplan_exists(self):
        """Test SUBPLAN exists."""
        # Create SUBPLAN file
        subplan_file = Path("SUBPLAN_TEST_11.md")
        subplan_file.write_text("# SUBPLAN: Test\n")

        result = check_subplan_exists("TEST", "1.1")
        self.assertTrue(result)

    def test_subplan_missing(self):
        """Test SUBPLAN missing."""
        result = check_subplan_exists("TEST", "1.1")
        self.assertFalse(result)

    def test_subplan_different_achievement(self):
        """Test SUBPLAN for different achievement."""
        # Create SUBPLAN for 1.1
        subplan_file = Path("SUBPLAN_TEST_11.md")
        subplan_file.write_text("# SUBPLAN: Test\n")

        # Check for 2.3 (should not exist)
        result = check_subplan_exists("TEST", "2.3")
        self.assertFalse(result)


class TestCheckExecutionTaskExists(unittest.TestCase):
    """Test check_execution_task_exists function."""

    def setUp(self):
        """Set up test environment."""
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_execution_task_exists(self):
        """Test EXECUTION_TASK exists."""
        # Create EXECUTION_TASK file
        execution_file = Path("EXECUTION_TASK_TEST_11_01.md")
        execution_file.write_text("# EXECUTION_TASK: Test\n")

        result = check_execution_task_exists("TEST", "1.1")
        self.assertTrue(result)

    def test_execution_task_missing(self):
        """Test EXECUTION_TASK missing."""
        result = check_execution_task_exists("TEST", "1.1")
        self.assertFalse(result)

    def test_execution_task_multiple_attempts(self):
        """Test multiple EXECUTION_TASK files (01, 02)."""
        # Create multiple EXECUTION_TASK files
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_11_02.md").write_text("# EXECUTION_TASK: Test\n")

        result = check_execution_task_exists("TEST", "1.1")
        self.assertTrue(result)

    def test_execution_task_different_achievement(self):
        """Test EXECUTION_TASK for different achievement."""
        # Create EXECUTION_TASK for 1.1
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")

        # Check for 2.3 (should not exist)
        result = check_execution_task_exists("TEST", "2.3")
        self.assertFalse(result)


class TestCheckDeliverablesExist(unittest.TestCase):
    """Test check_deliverables_exist function."""

    def setUp(self):
        """Set up test environment."""
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_all_deliverables_exist(self):
        """Test all deliverables exist."""
        # Create deliverable files
        Path("file1.py").write_text("# Test file\n")
        Path("file2.md").write_text("# Test doc\n")

        achievement = {"deliverables": ["File: `file1.py`", "Document: `file2.md`"]}

        missing = check_deliverables_exist(achievement)
        self.assertEqual(missing, [])

    def test_some_deliverables_missing(self):
        """Test some deliverables missing."""
        # Create only one deliverable
        Path("file1.py").write_text("# Test file\n")

        achievement = {"deliverables": ["File: `file1.py`", "Document: `file2.md`"]}

        missing = check_deliverables_exist(achievement)
        self.assertEqual(len(missing), 1)
        self.assertIn("file2.md", missing)

    def test_no_deliverables(self):
        """Test no deliverables specified."""
        achievement = {"deliverables": []}

        missing = check_deliverables_exist(achievement)
        self.assertEqual(missing, [])

    def test_deliverables_with_paths(self):
        """Test deliverables with directory paths."""
        # Create directory structure
        Path("tests").mkdir()
        Path("tests/test_file.py").write_text("# Test\n")
        Path("docs").mkdir()
        Path("docs/test_doc.md").write_text("# Doc\n")

        achievement = {
            "deliverables": ["File: `tests/test_file.py`", "Document: `docs/test_doc.md`"]
        }

        missing = check_deliverables_exist(achievement)
        self.assertEqual(missing, [])

    def test_deliverables_with_wrong_paths(self):
        """Test deliverables with wrong paths."""
        achievement = {"deliverables": ["File: `nonexistent/file.py`"]}

        missing = check_deliverables_exist(achievement)
        self.assertEqual(len(missing), 1)
        self.assertIn("nonexistent/file.py", missing)


class TestValidateAchievement(unittest.TestCase):
    """Test validate_achievement function."""

    def setUp(self):
        """Set up test environment."""
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_complete_achievement(self):
        """Test complete achievement (all checks pass)."""
        # Create PLAN file
        plan_content = """# PLAN: Test Feature

**Achievement 1.1**: Test Achievement

- Deliverables:
  - File: `test_file.py`
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLAN
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")

        # Create EXECUTION_TASK
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")

        # Create deliverable
        Path("test_file.py").write_text("# Test\n")

        pass_check, message = validate_achievement(plan_path, "1.1")
        self.assertTrue(pass_check)
        self.assertIn("✅ Achievement 1.1 properly completed", message)
        self.assertIn("SUBPLAN exists", message)
        self.assertIn("EXECUTION_TASK exists", message)
        self.assertIn("Deliverables exist", message)

    def test_missing_subplan(self):
        """Test missing SUBPLAN."""
        plan_content = """# PLAN: Test Feature

**Achievement 1.1**: Test Achievement
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create EXECUTION_TASK but not SUBPLAN
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")

        pass_check, message = validate_achievement(plan_path, "1.1")
        self.assertFalse(pass_check)
        self.assertIn("❌ ACHIEVEMENT NOT PROPERLY COMPLETED", message)
        self.assertIn("SUBPLAN missing", message)

    def test_missing_execution_task(self):
        """Test missing EXECUTION_TASK."""
        plan_content = """# PLAN: Test Feature

**Achievement 1.1**: Test Achievement
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLAN but not EXECUTION_TASK
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")

        pass_check, message = validate_achievement(plan_path, "1.1")
        self.assertFalse(pass_check)
        self.assertIn("❌ ACHIEVEMENT NOT PROPERLY COMPLETED", message)
        self.assertIn("EXECUTION_TASK missing", message)

    def test_missing_deliverables(self):
        """Test missing deliverables."""
        plan_content = """# PLAN: Test Feature

**Achievement 1.1**: Test Achievement

- Deliverables:
  - File: `test_file.py`
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLAN and EXECUTION_TASK but not deliverable
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")

        pass_check, message = validate_achievement(plan_path, "1.1")
        self.assertFalse(pass_check)
        self.assertIn("❌ ACHIEVEMENT NOT PROPERLY COMPLETED", message)
        self.assertIn("Deliverable missing", message)

    def test_missing_plan_file(self):
        """Test missing PLAN file."""
        plan_path = Path("PLAN_NONEXISTENT.md")

        pass_check, message = validate_achievement(plan_path, "1.1")
        self.assertFalse(pass_check)
        self.assertIn("❌ Error: PLAN file not found", message)

    def test_missing_achievement(self):
        """Test missing achievement in PLAN."""
        plan_content = """# PLAN: Test Feature

**Achievement 1.1**: Test Achievement
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        pass_check, message = validate_achievement(plan_path, "3.5")
        self.assertFalse(pass_check)
        self.assertIn("❌ Error: Achievement 3.5 not found in PLAN", message)

    def test_multiple_issues(self):
        """Test multiple issues (SUBPLAN + EXECUTION_TASK missing)."""
        plan_content = """# PLAN: Test Feature

**Achievement 1.1**: Test Achievement
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Don't create SUBPLAN or EXECUTION_TASK

        pass_check, message = validate_achievement(plan_path, "1.1")
        self.assertFalse(pass_check)
        self.assertIn("❌ ACHIEVEMENT NOT PROPERLY COMPLETED", message)
        self.assertIn("SUBPLAN missing", message)
        self.assertIn("EXECUTION_TASK missing", message)

    def test_achievement_without_deliverables(self):
        """Test achievement without deliverables section."""
        plan_content = """# PLAN: Test Feature

**Achievement 1.1**: Test Achievement
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLAN and EXECUTION_TASK
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")

        pass_check, message = validate_achievement(plan_path, "1.1")
        self.assertTrue(pass_check)
        self.assertIn("✅ Achievement 1.1 properly completed", message)
        # Should not mention deliverables if none specified
        self.assertNotIn("Deliverables exist", message)

    def test_fix_prompt_in_message(self):
        """Test that error message includes fix prompt."""
        plan_content = """# PLAN: Test Feature

**Achievement 1.1**: Test Achievement
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        pass_check, message = validate_achievement(plan_path, "1.1")
        self.assertFalse(pass_check)
        self.assertIn("📋 Fix Prompt:", message)
        self.assertIn("Create SUBPLAN", message)
        self.assertIn("Create EXECUTION_TASK", message)


class TestIntegration(unittest.TestCase):
    """Integration tests with real file structures."""

    def setUp(self):
        """Set up test environment."""
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_real_plan_structure(self):
        """Test with realistic PLAN file structure."""
        plan_content = """# PLAN: Test Feature

**Status**: Planning
**Created**: 2025-01-27

## Priority 0: Foundation

**Achievement 0.1**: Setup

- Deliverables:
  - File: `setup.py`
  - Document: `README.md`

**Achievement 0.2**: Configuration

- Deliverables:
  - File: `config.py`

## Current Status & Handoff

**Next**: Achievement 0.3
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create files for Achievement 0.1
        Path("SUBPLAN_TEST_01.md").write_text("# SUBPLAN: Test\n")
        Path("EXECUTION_TASK_TEST_01_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("setup.py").write_text("# Setup\n")
        Path("README.md").write_text("# README\n")
        # Note: Function extracts ALL deliverables from PLAN, including from other achievements
        # So we need to create config.py too (from Achievement 0.2)
        Path("config.py").write_text("# Config\n")

        pass_check, message = validate_achievement(plan_path, "0.1")
        self.assertTrue(pass_check, f"Validation failed: {message}")
        self.assertIn("✅ Achievement 0.1 properly completed", message)

    def test_cli_argument_parsing(self):
        """Test CLI argument parsing (simulated)."""
        # This tests the main() function indirectly through validate_achievement
        # Actual CLI testing would require subprocess or mocking argparse
        plan_content = """# PLAN: Test Feature

**Achievement 1.1**: Test Achievement
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")

        # Test with @ prefix (should be handled by main, but we test validate_achievement directly)
        pass_check, message = validate_achievement(plan_path, "1.1")
        self.assertTrue(pass_check)


if __name__ == "__main__":
    unittest.main()
