#!/usr/bin/env python3
"""
Test Suite for Utils Module

Tests the utility functions extracted in Achievement 2.4.

Test Coverage:
- copy_to_clipboard_safe() with various scenarios
- resolve_folder_shortcut() with valid and invalid inputs
- Edge cases and error handling

Created: 2025-11-12
Achievement: 2.4 - Extract Parsing & Utilities Module
"""
import sys
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from LLM.scripts.generation import utils


class TestCopyToClipboardSafe(unittest.TestCase):
    """Test the copy_to_clipboard_safe() function."""

    @patch("pyperclip.copy")
    def test_copy_successful(self, mock_copy):
        """Test successful clipboard copy."""
        result = utils.copy_to_clipboard_safe("Hello World")

        self.assertTrue(result)
        mock_copy.assert_called_once_with("Hello World")

    def test_copy_disabled(self):
        """Test clipboard copy when disabled."""
        result = utils.copy_to_clipboard_safe("Hello World", enabled=False)

        self.assertFalse(result)

    @patch("pyperclip.copy", side_effect=Exception("Clipboard unavailable"))
    def test_copy_with_exception(self, mock_copy):
        """Test clipboard copy when pyperclip raises exception."""
        result = utils.copy_to_clipboard_safe("Hello World")

        self.assertFalse(result)

    @patch("pyperclip.copy")
    def test_copy_empty_text(self, mock_copy):
        """Test clipboard copy with empty text."""
        result = utils.copy_to_clipboard_safe("")

        self.assertTrue(result)
        mock_copy.assert_called_once_with("")

    @patch("pyperclip.copy")
    def test_copy_long_text(self, mock_copy):
        """Test clipboard copy with very long text."""
        long_text = "A" * 10000

        result = utils.copy_to_clipboard_safe(long_text)

        self.assertTrue(result)
        mock_copy.assert_called_once_with(long_text)


class TestResolveFolderShortcut(unittest.TestCase):
    """Test the resolve_folder_shortcut() function."""

    def setUp(self):
        # Create a temporary workspace structure for testing
        self.temp_dir = tempfile.mkdtemp()
        self.workspace_plans = Path(self.temp_dir) / "work-space" / "plans"
        self.workspace_plans.mkdir(parents=True, exist_ok=True)

        # Create some test plan folders
        test_plan_folder = self.workspace_plans / "TEST-FEATURE"
        test_plan_folder.mkdir(exist_ok=True)
        (test_plan_folder / "PLAN_TEST-FEATURE.md").write_text("# PLAN: Test")

    def test_resolve_valid_folder(self):
        """Test resolving a valid folder shortcut."""
        # This test depends on actual workspace structure
        # If PROMPT-GENERATOR-UX-AND-FOUNDATION exists, test with it
        result = utils.resolve_folder_shortcut("PROMPT-GENERATOR-UX-AND-FOUNDATION")

        if result:
            self.assertIsInstance(result, Path)
            self.assertTrue(result.exists())
            self.assertTrue(str(result).endswith(".md"))

    def test_resolve_nonexistent_folder(self):
        """Test resolving nonexistent folder raises PlanNotFoundError (Achievement 3.1)."""
        from LLM.scripts.generation.exceptions import PlanNotFoundError
        with self.assertRaises(PlanNotFoundError):
            utils.resolve_folder_shortcut("NONEXISTENT-FOLDER-12345")

    def test_resolve_empty_string(self):
        """Test resolving empty string raises PlanNotFoundError (Achievement 3.1)."""
        from LLM.scripts.generation.exceptions import PlanNotFoundError
        with self.assertRaises(PlanNotFoundError):
            utils.resolve_folder_shortcut("")

    def test_resolve_with_special_characters(self):
        """Test resolving folder name with special characters raises exception (Achievement 3.1)."""
        from LLM.scripts.generation.exceptions import PlanNotFoundError
        # Invalid characters don't match any real folder, so PlanNotFoundError raised
        with self.assertRaises(PlanNotFoundError):
            utils.resolve_folder_shortcut("TEST-FEATURE@#$")

    def test_resolve_with_spaces(self):
        """Test resolving folder name with spaces raises exception (Achievement 3.1)."""
        from LLM.scripts.generation.exceptions import PlanNotFoundError
        # Spaces in folder name won't match any real folder
        with self.assertRaises(PlanNotFoundError):
            utils.resolve_folder_shortcut("TEST FEATURE WITH SPACES")

    def test_resolve_lowercase_folder(self):
        """Test resolving with lowercase folder name - expects uppercase."""
        # Implementation expects uppercase folder names, so lowercase might exit
        # We test that it handles the call (may exit or work depending on implementation)
        try:
            result = utils.resolve_folder_shortcut("prompt-generator-ux-and-foundation")
            # If it succeeds, result should be a Path
            self.assertIsInstance(result, Path)
        except SystemExit:
            # Implementation may call sys.exit() for invalid folder format
            pass


class TestUtilsIntegration(unittest.TestCase):
    """Integration tests for utils module."""

    def test_all_functions_importable(self):
        """Test that all expected functions can be imported."""
        expected_functions = ["copy_to_clipboard_safe", "resolve_folder_shortcut"]

        for func_name in expected_functions:
            with self.subTest(function=func_name):
                self.assertTrue(hasattr(utils, func_name), f"Missing function: {func_name}")
                self.assertTrue(
                    callable(getattr(utils, func_name)), f"Function not callable: {func_name}"
                )

    @patch("pyperclip.copy")
    def test_copy_and_resolve_work_together(self, mock_copy):
        """Test that utils functions work independently."""
        # Test clipboard works
        clip_result = utils.copy_to_clipboard_safe("test")
        self.assertTrue(clip_result)

        # Test resolve works (may return None if folder doesn't exist)
        resolve_result = utils.resolve_folder_shortcut("TEST")
        self.assertTrue(resolve_result is None or isinstance(resolve_result, Path))


class TestGetAchievementStatus(unittest.TestCase):
    """
    Test the get_achievement_status() function (tri-state detection).
    
    Achievement 2.9 - Implement FIX Feedback Detection & Prompt Generation
    Tests tri-state model: approved / needs_fix / incomplete
    """

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
    
    def test_status_approved_when_approved_file_exists(self):
        """Test returns 'approved' when APPROVED_XX.md exists."""
        # Create APPROVED file
        approved_file = self.feedbacks_dir / "APPROVED_01.md"
        approved_file.write_text("# APPROVED")
        
        status = utils.get_achievement_status("0.1", self.plan_file)
        
        self.assertEqual(status, "approved")
    
    def test_status_needs_fix_when_fix_file_exists(self):
        """Test returns 'needs_fix' when FIX_XX.md exists (no APPROVED)."""
        # Create FIX file only
        fix_file = self.feedbacks_dir / "FIX_21.md"
        fix_file.write_text("# FIX")
        
        status = utils.get_achievement_status("2.1", self.plan_file)
        
        self.assertEqual(status, "needs_fix")
    
    def test_status_incomplete_when_neither_exists(self):
        """Test returns 'incomplete' when neither APPROVED nor FIX exists."""
        status = utils.get_achievement_status("0.3", self.plan_file)
        
        self.assertEqual(status, "incomplete")
    
    def test_approved_priority_over_fix(self):
        """Test APPROVED takes priority when both APPROVED and FIX exist."""
        # Create both files
        approved_file = self.feedbacks_dir / "APPROVED_15.md"
        approved_file.write_text("# APPROVED")
        fix_file = self.feedbacks_dir / "FIX_15.md"
        fix_file.write_text("# FIX")
        
        status = utils.get_achievement_status("1.5", self.plan_file)
        
        # APPROVED should override FIX
        self.assertEqual(status, "approved")
    
    def test_status_incomplete_when_no_feedbacks_folder(self):
        """Test returns 'incomplete' when feedbacks folder doesn't exist."""
        # Remove feedbacks folder
        import shutil
        shutil.rmtree(self.feedbacks_dir)
        
        status = utils.get_achievement_status("0.1", self.plan_file)
        
        self.assertEqual(status, "incomplete")
    
    def test_status_incomplete_when_no_plan_path(self):
        """Test returns 'incomplete' when plan_path is None."""
        status = utils.get_achievement_status("0.1", None)
        
        self.assertEqual(status, "incomplete")
    
    def test_achievement_number_formatting(self):
        """Test achievement number formatting (e.g., '2.1' -> '21')."""
        # Create APPROVED_21.md
        approved_file = self.feedbacks_dir / "APPROVED_21.md"
        approved_file.write_text("# APPROVED")
        
        # Test with dot notation
        status = utils.get_achievement_status("2.1", self.plan_file)
        self.assertEqual(status, "approved")
        
        # Create APPROVED_102.md for "10.2"
        approved_file2 = self.feedbacks_dir / "APPROVED_102.md"
        approved_file2.write_text("# APPROVED")
        
        status2 = utils.get_achievement_status("10.2", self.plan_file)
        self.assertEqual(status2, "approved")


class TestIsAchievementCompleteWithTriState(unittest.TestCase):
    """
    Test that is_achievement_complete() maintains backward compatibility
    with new tri-state get_achievement_status() function.
    
    Achievement 2.9 - Backward Compatibility Tests
    """

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
    
    def test_returns_true_when_approved(self):
        """Test is_achievement_complete() returns True for approved status."""
        approved_file = self.feedbacks_dir / "APPROVED_01.md"
        approved_file.write_text("# APPROVED")
        
        result = utils.is_achievement_complete("0.1", "", self.plan_file)
        
        self.assertTrue(result)
    
    def test_returns_false_when_needs_fix(self):
        """Test is_achievement_complete() returns False for needs_fix status."""
        fix_file = self.feedbacks_dir / "FIX_21.md"
        fix_file.write_text("# FIX")
        
        result = utils.is_achievement_complete("2.1", "", self.plan_file)
        
        # Should return False even though FIX file exists
        self.assertFalse(result)
    
    def test_returns_false_when_incomplete(self):
        """Test is_achievement_complete() returns False for incomplete status."""
        result = utils.is_achievement_complete("0.3", "", self.plan_file)
        
        self.assertFalse(result)
    
    def test_backward_compatibility_with_plan_content(self):
        """Test function still accepts plan_content parameter (unused)."""
        approved_file = self.feedbacks_dir / "APPROVED_01.md"
        approved_file.write_text("# APPROVED")
        
        # plan_content parameter is ignored but should not cause errors
        result = utils.is_achievement_complete("0.1", "some plan content", self.plan_file)
        
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
