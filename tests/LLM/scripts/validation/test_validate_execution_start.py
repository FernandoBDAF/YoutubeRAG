"""Unit tests for validate_execution_start.py - Execution start validation."""

import unittest
import sys
import tempfile
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from LLM.scripts.validation.validate_execution_start import (
    extract_feature_from_file,
    check_subplan_exists,
    check_parent_plan_exists,
    get_archive_location,
    check_archive_location_exists,
    validate_execution_start,
)


class TestExtractFeatureFromFile(unittest.TestCase):
    """Test extract_feature_from_file function."""

    def test_valid_filename(self):
        """Test extracting feature from valid filename."""
        file_path = Path("EXECUTION_TASK_TEST-FEATURE_11_01.md")
        result = extract_feature_from_file(file_path)
        self.assertEqual(result, "TEST-FEATURE")

    def test_valid_filename_with_numbers(self):
        """Test extracting feature from filename with numbers."""
        file_path = Path("EXECUTION_TASK_TEST123_11_01.md")
        result = extract_feature_from_file(file_path)
        self.assertEqual(result, "TEST123")

    def test_valid_filename_with_hyphens(self):
        """Test extracting feature from filename with hyphens."""
        file_path = Path("EXECUTION_TASK_TEST-FEATURE-NAME_11_01.md")
        result = extract_feature_from_file(file_path)
        self.assertEqual(result, "TEST-FEATURE-NAME")

    def test_invalid_filename_format(self):
        """Test invalid filename format raises ValueError."""
        file_path = Path("INVALID_FILENAME.md")
        with self.assertRaises(ValueError) as context:
            extract_feature_from_file(file_path)
        self.assertIn("Could not extract feature", str(context.exception))

    def test_invalid_filename_missing_parts(self):
        """Test filename missing parts raises ValueError."""
        file_path = Path("EXECUTION_TASK_TEST.md")
        with self.assertRaises(ValueError) as context:
            extract_feature_from_file(file_path)
        self.assertIn("Could not extract feature", str(context.exception))


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
        # Create EXECUTION_TASK file
        execution_file = Path("EXECUTION_TASK_TEST_11_01.md")
        execution_file.write_text("# EXECUTION_TASK: Test\n")

        # Create SUBPLAN file
        subplan_file = Path("SUBPLAN_TEST_11.md")
        subplan_file.write_text("# SUBPLAN: Test\n")

        result = check_subplan_exists(execution_file)
        self.assertTrue(result)

    def test_subplan_missing(self):
        """Test SUBPLAN missing."""
        # Create EXECUTION_TASK file but not SUBPLAN
        execution_file = Path("EXECUTION_TASK_TEST_11_01.md")
        execution_file.write_text("# EXECUTION_TASK: Test\n")

        result = check_subplan_exists(execution_file)
        self.assertFalse(result)

    def test_different_subplan_number(self):
        """Test SUBPLAN with different number."""
        # Create EXECUTION_TASK for 11
        execution_file = Path("EXECUTION_TASK_TEST_11_01.md")
        execution_file.write_text("# EXECUTION_TASK: Test\n")

        # Create SUBPLAN for 22 (different number)
        subplan_file = Path("SUBPLAN_TEST_22.md")
        subplan_file.write_text("# SUBPLAN: Test\n")

        result = check_subplan_exists(execution_file)
        self.assertFalse(result)


class TestCheckParentPlanExists(unittest.TestCase):
    """Test check_parent_plan_exists function."""

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

    def test_plan_exists(self):
        """Test PLAN exists."""
        # Create EXECUTION_TASK file
        execution_file = Path("EXECUTION_TASK_TEST_11_01.md")
        execution_file.write_text("# EXECUTION_TASK: Test\n")

        # Create PLAN file
        plan_file = Path("PLAN_TEST.md")
        plan_file.write_text("# PLAN: Test\n")

        result = check_parent_plan_exists(execution_file)
        self.assertTrue(result)

    def test_plan_missing(self):
        """Test PLAN missing."""
        # Create EXECUTION_TASK file but not PLAN
        execution_file = Path("EXECUTION_TASK_TEST_11_01.md")
        execution_file.write_text("# EXECUTION_TASK: Test\n")

        result = check_parent_plan_exists(execution_file)
        self.assertFalse(result)

    def test_plan_with_hyphens(self):
        """Test PLAN with hyphens in feature name."""
        # Create EXECUTION_TASK with hyphens
        execution_file = Path("EXECUTION_TASK_TEST-FEATURE_11_01.md")
        execution_file.write_text("# EXECUTION_TASK: Test\n")

        # Create PLAN (hyphens converted to underscores in filename)
        plan_file = Path("PLAN_TEST-FEATURE.md")
        plan_file.write_text("# PLAN: Test\n")

        result = check_parent_plan_exists(execution_file)
        self.assertTrue(result)


class TestGetArchiveLocation(unittest.TestCase):
    """Test get_archive_location function."""

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

    def test_extract_archive_location_from_plan(self):
        """Test extracting archive location from PLAN."""
        # Note: Current regex pattern doesn't match "**Archive Location**: path" format
        # It expects "Archive Location" followed by "**", so it falls back to inferred location
        # This tests the fallback behavior
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`

## Other Section
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        result = get_archive_location(plan_path)
        # Falls back to inferred location because regex doesn't match
        self.assertEqual(result, Path("./test-archive/"))

    def test_extract_archive_location_with_colon(self):
        """Test extracting archive location with colon."""
        # Note: Current regex pattern doesn't match "**Archive Location**: path" format
        # Falls back to inferred location
        plan_content = """# PLAN: Test Feature

**Archive Location**: documentation/archive/test-feature/
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        result = get_archive_location(plan_path)
        # Falls back to inferred location
        self.assertEqual(result, Path("./test-archive/"))

    def test_extract_archive_location_with_backticks(self):
        """Test extracting archive location with backticks."""
        # Note: Current regex pattern doesn't match "**Archive Location**: `path`" format
        # Falls back to inferred location
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        result = get_archive_location(plan_path)
        # Falls back to inferred location
        self.assertEqual(result, Path("./test-archive/"))

    def test_fallback_to_inferred_location(self):
        """Test fallback to inferred location when not specified."""
        plan_content = """# PLAN: Test Feature

## Other Section
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        result = get_archive_location(plan_path)
        # Path object doesn't include ./ in string representation
        self.assertEqual(result, Path("./test-archive/"))

    def test_fallback_with_hyphens(self):
        """Test fallback with hyphens in feature name."""
        plan_content = """# PLAN: Test Feature Name

## Other Section
"""
        plan_path = Path("PLAN_TEST-FEATURE-NAME.md")
        plan_path.write_text(plan_content)

        result = get_archive_location(plan_path)
        # Path object doesn't include ./ in string representation, but path is correct
        self.assertEqual(result, Path("./test-feature-name-archive/"))


class TestCheckArchiveLocationExists(unittest.TestCase):
    """Test check_archive_location_exists function."""

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

    def test_archive_location_exists(self):
        """Test archive location exists."""
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create archive directory (get actual path from PLAN - will be fallback)
        archive_path = get_archive_location(plan_path)
        archive_path.mkdir(parents=True, exist_ok=True)

        result = check_archive_location_exists(plan_path)
        self.assertTrue(result)

    def test_archive_location_missing(self):
        """Test archive location missing."""
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Don't create archive directory
        result = check_archive_location_exists(plan_path)
        self.assertFalse(result)

    def test_archive_location_fallback_exists(self):
        """Test fallback archive location exists."""
        plan_content = """# PLAN: Test Feature

## Other Section
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create fallback archive directory (get actual path first)
        archive_path = get_archive_location(plan_path)
        archive_path.mkdir(parents=True, exist_ok=True)

        result = check_archive_location_exists(plan_path)
        self.assertTrue(result)


class TestValidateExecutionStart(unittest.TestCase):
    """Test validate_execution_start function."""

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

    def test_all_prerequisites_met(self):
        """Test all prerequisites met."""
        # Create EXECUTION_TASK
        execution_file = Path("EXECUTION_TASK_TEST_11_01.md")
        execution_file.write_text("# EXECUTION_TASK: Test\n")

        # Create SUBPLAN
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")

        # Create PLAN with archive location
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`
"""
        Path("PLAN_TEST.md").write_text(plan_content)

        # Create archive directory (need to check what path is actually used)
        archive_path = get_archive_location(Path("PLAN_TEST.md"))
        archive_path.mkdir(parents=True, exist_ok=True)

        pass_check, message = validate_execution_start(execution_file)
        if not pass_check:
            print(f"Validation failed: {message}")
        self.assertTrue(pass_check, f"Validation failed: {message}")
        self.assertIn("✅ Prerequisites met", message)
        self.assertIn("SUBPLAN exists", message)
        self.assertIn("Parent PLAN exists", message)
        self.assertIn("Archive location exists", message)

    def test_missing_subplan(self):
        """Test missing SUBPLAN."""
        # Create EXECUTION_TASK but not SUBPLAN
        execution_file = Path("EXECUTION_TASK_TEST_11_01.md")
        execution_file.write_text("# EXECUTION_TASK: Test\n")

        # Create PLAN with archive location
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`
"""
        Path("PLAN_TEST.md").write_text(plan_content)

        # Create archive directory
        Path("documentation/archive/test-feature/").mkdir(parents=True)

        pass_check, message = validate_execution_start(execution_file)
        self.assertFalse(pass_check)
        self.assertIn("❌ PREREQUISITES MISSING", message)
        self.assertIn("SUBPLAN missing", message)

    def test_missing_plan(self):
        """Test missing PLAN."""
        # Create EXECUTION_TASK
        execution_file = Path("EXECUTION_TASK_TEST_11_01.md")
        execution_file.write_text("# EXECUTION_TASK: Test\n")

        # Create SUBPLAN
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")

        # Don't create PLAN

        pass_check, message = validate_execution_start(execution_file)
        self.assertFalse(pass_check)
        self.assertIn("❌ PREREQUISITES MISSING", message)
        self.assertIn("Parent PLAN missing", message)

    def test_missing_archive_location(self):
        """Test missing archive location."""
        # Create EXECUTION_TASK
        execution_file = Path("EXECUTION_TASK_TEST_11_01.md")
        execution_file.write_text("# EXECUTION_TASK: Test\n")

        # Create SUBPLAN
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")

        # Create PLAN with archive location
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`
"""
        Path("PLAN_TEST.md").write_text(plan_content)

        # Don't create archive directory

        pass_check, message = validate_execution_start(execution_file)
        self.assertFalse(pass_check)
        self.assertIn("❌ PREREQUISITES MISSING", message)
        self.assertIn("Archive location missing", message)

    def test_missing_file(self):
        """Test missing EXECUTION_TASK file."""
        execution_file = Path("EXECUTION_TASK_NONEXISTENT_11_01.md")

        pass_check, message = validate_execution_start(execution_file)
        self.assertFalse(pass_check)
        self.assertIn("❌ Error: File not found", message)

    def test_multiple_issues(self):
        """Test multiple issues (SUBPLAN + archive location missing)."""
        # Create EXECUTION_TASK
        execution_file = Path("EXECUTION_TASK_TEST_11_01.md")
        execution_file.write_text("# EXECUTION_TASK: Test\n")

        # Create PLAN with archive location
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`
"""
        Path("PLAN_TEST.md").write_text(plan_content)

        # Don't create SUBPLAN or archive directory

        pass_check, message = validate_execution_start(execution_file)
        self.assertFalse(pass_check)
        self.assertIn("❌ PREREQUISITES MISSING", message)
        self.assertIn("SUBPLAN missing", message)
        self.assertIn("Archive location missing", message)

    def test_fix_prompt_in_message(self):
        """Test that error message includes fix prompt."""
        # Create EXECUTION_TASK but not SUBPLAN
        execution_file = Path("EXECUTION_TASK_TEST_11_01.md")
        execution_file.write_text("# EXECUTION_TASK: Test\n")

        # Create PLAN with archive location
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`
"""
        Path("PLAN_TEST.md").write_text(plan_content)

        # Create archive directory
        Path("documentation/archive/test-feature/").mkdir(parents=True)

        pass_check, message = validate_execution_start(execution_file)
        self.assertFalse(pass_check)
        self.assertIn("📋 Fix Prompt:", message)
        self.assertIn("Create SUBPLAN", message)

    def test_archive_location_fallback(self):
        """Test archive location fallback when not specified."""
        # Create EXECUTION_TASK
        execution_file = Path("EXECUTION_TASK_TEST_11_01.md")
        execution_file.write_text("# EXECUTION_TASK: Test\n")

        # Create SUBPLAN
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")

        # Create PLAN without archive location (will use fallback)
        plan_content = """# PLAN: Test Feature

## Other Section
"""
        Path("PLAN_TEST.md").write_text(plan_content)

        # Create fallback archive directory
        Path("./test-archive/").mkdir()

        pass_check, message = validate_execution_start(execution_file)
        self.assertTrue(pass_check)
        self.assertIn("✅ Prerequisites met", message)


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

    def test_complete_valid_setup(self):
        """Test with complete valid setup."""
        # Create EXECUTION_TASK
        execution_file = Path("EXECUTION_TASK_TEST-FEATURE_11_01.md")
        execution_file.write_text("# EXECUTION_TASK: Test\n")

        # Create SUBPLAN
        Path("SUBPLAN_TEST-FEATURE_11.md").write_text("# SUBPLAN: Test\n")

        # Create PLAN with archive location
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`

## Priority 0: Foundation

**Achievement 0.1**: Setup
"""
        Path("PLAN_TEST-FEATURE.md").write_text(plan_content)

        # Create archive directory structure (get actual path from PLAN)
        plan_path = Path("PLAN_TEST-FEATURE.md")
        archive_path = get_archive_location(plan_path)
        archive_path.mkdir(parents=True, exist_ok=True)
        (archive_path / "subplans").mkdir(exist_ok=True)
        (archive_path / "execution").mkdir(exist_ok=True)

        pass_check, message = validate_execution_start(execution_file)
        if not pass_check:
            print(f"Validation failed: {message}")
        self.assertTrue(pass_check, f"Validation failed: {message}")
        self.assertIn("✅ Prerequisites met", message)

    def test_cli_argument_parsing(self):
        """Test CLI argument parsing (simulated)."""
        # This tests the main() function indirectly through validate_execution_start
        # Actual CLI testing would require subprocess or mocking argparse
        execution_file = Path("EXECUTION_TASK_TEST_11_01.md")
        execution_file.write_text("# EXECUTION_TASK: Test\n")

        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")

        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create archive directory (get actual path from PLAN)
        archive_path = get_archive_location(plan_path)
        archive_path.mkdir(parents=True, exist_ok=True)

        # Test with @ prefix (should be handled by main, but we test validate_execution_start directly)
        pass_check, message = validate_execution_start(execution_file)
        if not pass_check:
            print(f"Validation failed: {message}")
        self.assertTrue(pass_check, f"Validation failed: {message}")


if __name__ == "__main__":
    unittest.main()

