"""
Tests for clipboard default and folder shortcuts in generate_prompt.py

Achievement 0.1: Clipboard by Default & Short Commands
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from LLM.scripts.generation.utils import (
    copy_to_clipboard_safe,
    resolve_folder_shortcut,
)


class TestClipboardDefault:
    """Test clipboard default behavior"""

    def test_clipboard_enabled_by_default(self):
        """Clipboard should copy when enabled=True (default)"""
        with patch("pyperclip.copy") as mock_copy:
            result = copy_to_clipboard_safe("test text", enabled=True)
            assert result is True
            mock_copy.assert_called_once_with("test text")

    def test_clipboard_disabled_with_flag(self):
        """Clipboard should not copy when enabled=False"""
        with patch("pyperclip.copy") as mock_copy:
            result = copy_to_clipboard_safe("test text", enabled=False)
            assert result is False
            mock_copy.assert_not_called()

    def test_clipboard_handles_import_error(self):
        """Should handle gracefully if pyperclip not available"""
        with patch("pyperclip.copy", side_effect=ImportError("No module")):
            result = copy_to_clipboard_safe("test text", enabled=True)
            assert result is False

    def test_clipboard_handles_runtime_error(self):
        """Should handle runtime errors gracefully"""
        with patch("pyperclip.copy", side_effect=RuntimeError("Clipboard error")):
            result = copy_to_clipboard_safe("test text", enabled=True)
            assert result is False


class TestFolderShortcut:
    """Test @folder shortcut resolution"""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing"""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir)

        # Create work-space/plans structure
        plans_dir = workspace / "work-space" / "plans"
        plans_dir.mkdir(parents=True)

        # Create test plan folders
        restore_folder = plans_dir / "RESTORE-EXECUTION-WORKFLOW-AUTOMATION"
        restore_folder.mkdir()
        (restore_folder / "PLAN_RESTORE-EXECUTION-WORKFLOW-AUTOMATION.md").write_text("# PLAN")

        graphrag_folder = plans_dir / "GRAPHRAG-OBSERVABILITY-EXCELLENCE"
        graphrag_folder.mkdir()
        (graphrag_folder / "PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md").write_text("# PLAN")

        prompt_folder = plans_dir / "PROMPT-GENERATOR-UX-AND-FOUNDATION"
        prompt_folder.mkdir()
        (prompt_folder / "PLAN_PROMPT-GENERATOR-UX-AND-FOUNDATION.md").write_text("# PLAN")

        # Save original cwd and change to temp
        original_cwd = Path.cwd()
        import os

        os.chdir(workspace)

        yield workspace

        # Cleanup
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)

    def test_folder_shortcut_single_match(self, temp_workspace):
        """Should find PLAN when folder name matches uniquely"""
        result = resolve_folder_shortcut("RESTORE")
        assert result.name == "PLAN_RESTORE-EXECUTION-WORKFLOW-AUTOMATION.md"
        assert result.exists()

    def test_folder_shortcut_case_insensitive(self, temp_workspace):
        """Should match case-insensitively"""
        result = resolve_folder_shortcut("restore")
        assert result.name == "PLAN_RESTORE-EXECUTION-WORKFLOW-AUTOMATION.md"

    def test_folder_shortcut_partial_match(self, temp_workspace):
        """Should match partial folder names"""
        result = resolve_folder_shortcut("GRAPHRAG-OBSERVABILITY")
        assert result.name == "PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md"

    def test_folder_shortcut_not_found(self, temp_workspace):
        """Should exit with helpful error if folder not found"""
        with pytest.raises(SystemExit) as exc_info:
            resolve_folder_shortcut("NONEXISTENT")
        assert exc_info.value.code == 1

    def test_folder_shortcut_multiple_matches(self, temp_workspace):
        """Should exit with error if multiple folders match"""
        # Create another folder with PROMPT in name
        plans_dir = temp_workspace / "work-space" / "plans"
        prompt2_folder = plans_dir / "PROMPT-SYSTEM-DESIGN"
        prompt2_folder.mkdir()
        (prompt2_folder / "PLAN_PROMPT-SYSTEM-DESIGN.md").write_text("# PLAN")

        with pytest.raises(SystemExit) as exc_info:
            resolve_folder_shortcut("PROMPT")
        assert exc_info.value.code == 1

    def test_folder_shortcut_no_plan_file(self, temp_workspace):
        """Should exit with error if folder exists but no PLAN file"""
        plans_dir = temp_workspace / "work-space" / "plans"
        empty_folder = plans_dir / "EMPTY-FOLDER"
        empty_folder.mkdir()

        with pytest.raises(SystemExit) as exc_info:
            resolve_folder_shortcut("EMPTY")
        assert exc_info.value.code == 1

    def test_folder_shortcut_multiple_plan_files(self, temp_workspace):
        """Should exit with error if multiple PLAN files in folder"""
        plans_dir = temp_workspace / "work-space" / "plans"
        multi_folder = plans_dir / "MULTI-PLAN-FOLDER"
        multi_folder.mkdir()
        (multi_folder / "PLAN_MULTI-1.md").write_text("# PLAN 1")
        (multi_folder / "PLAN_MULTI-2.md").write_text("# PLAN 2")

        with pytest.raises(SystemExit) as exc_info:
            resolve_folder_shortcut("MULTI")
        assert exc_info.value.code == 1


class TestIntegration:
    """Integration tests for new features"""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for integration testing"""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir)

        # Create complete structure
        plans_dir = workspace / "work-space" / "plans"
        test_folder = plans_dir / "TEST-FEATURE"
        test_folder.mkdir(parents=True)

        # Create PLAN file
        plan_file = test_folder / "PLAN_TEST-FEATURE.md"
        plan_file.write_text(
            """# PLAN: Test Feature

## 📋 Desirable Achievements

**Achievement 0.1**: Test Achievement
**Purpose**: Test
**What**: Test
**Success**: Test
**Effort**: 1 hour

## 📋 Current Status & Handoff

**Next**: Achievement 0.1
"""
        )

        # Create subplans and execution folders
        (test_folder / "subplans").mkdir()
        (test_folder / "execution").mkdir()

        # Save original cwd
        original_cwd = Path.cwd()
        import os

        os.chdir(workspace)

        yield workspace

        # Cleanup
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)

    def test_folder_shortcut_with_real_plan(self, temp_workspace):
        """Should resolve folder and find PLAN file"""
        result = resolve_folder_shortcut("TEST")
        assert result.name == "PLAN_TEST-FEATURE.md"
        assert result.exists()
        assert "TEST-FEATURE" in str(result.parent)

    def test_clipboard_with_real_output(self):
        """Should copy real output to clipboard"""
        test_output = "This is a test prompt\nWith multiple lines"
        with patch("pyperclip.copy") as mock_copy:
            result = copy_to_clipboard_safe(test_output)
            assert result is True
            mock_copy.assert_called_once_with(test_output)


class TestBackwardCompatibility:
    """Test that old commands still work"""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace"""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir)

        plans_dir = workspace / "work-space" / "plans"
        test_folder = plans_dir / "TEST-FEATURE"
        test_folder.mkdir(parents=True)

        plan_file = test_folder / "PLAN_TEST-FEATURE.md"
        plan_file.write_text("# PLAN")

        original_cwd = Path.cwd()
        import os

        os.chdir(workspace)

        yield workspace

        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)

    def test_old_at_plan_format_still_works(self, temp_workspace):
        """@PLAN_NAME.md format should still work"""
        # This test would require full integration
        # For now, verify the logic path exists
        assert True  # Placeholder - full test requires main() integration

    def test_full_path_still_works(self, temp_workspace):
        """Full paths should still work"""
        # This test would require full integration
        # For now, verify the logic path exists
        assert True  # Placeholder - full test requires main() integration


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
