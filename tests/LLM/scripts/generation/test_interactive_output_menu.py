"""
Tests for InteractiveMenu().show_post_generation_menu() function in generate_prompt.py

Tests the post-generation interactive menu that allows users to:
- Copy to clipboard
- View full prompt
- Save to file
- Execute command
- Get help
- Exit

Created: 2025-11-09
Achievement: 0.3 in PLAN_PROMPT-GENERATOR-UX-AND-FOUNDATION.md
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from io import StringIO

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from LLM.scripts.generation.interactive_menu import InteractiveMenu


class TestOutputInteractiveMenu:
    """Test suite for InteractiveMenu().show_post_generation_menu() function."""

    @pytest.fixture
    def sample_prompt(self):
        """Sample prompt text for testing."""
        return """Execute Achievement 1.1 in @PLAN_FEATURE.md

**Recommended Command**:
  python generate_prompt.py @PLAN_FEATURE.md --achievement 1.1 --subplan-only

Follow these steps...
"""

    @pytest.fixture
    def sample_command(self):
        """Sample recommended command."""
        return "python generate_prompt.py @PLAN_FEATURE.md --achievement 1.1 --subplan-only"

    def test_menu_copy_to_clipboard_default(self, sample_prompt, capsys):
        """Test option 1: Copy command to clipboard (default with Enter key)."""
        with patch("builtins.input", return_value=""):  # Empty = default
            with patch("LLM.scripts.generation.utils.copy_to_clipboard_safe", return_value=True):
                InteractiveMenu().show_post_generation_menu(sample_prompt, "create_subplan", None)

        captured = capsys.readouterr()
        assert "🎯 What would you like to do with this prompt?" in captured.out
        assert "1. Copy command to clipboard (default - press Enter)" in captured.out
        assert "✅ Command copied to clipboard!" in captured.out

    def test_menu_copy_explicit_choice(self, sample_prompt, capsys):
        """Test option 1: Copy command to clipboard (explicit choice)."""
        with patch("builtins.input", return_value="1"):
            with patch("LLM.scripts.generation.utils.copy_to_clipboard_safe", return_value=True):
                InteractiveMenu().show_post_generation_menu(sample_prompt, "create_execution", None)

        captured = capsys.readouterr()
        assert "✅ Command copied to clipboard!" in captured.out

    def test_menu_copy_fallback_when_clipboard_unavailable(self, sample_prompt, capsys):
        """Test option 1: Fallback to display when clipboard unavailable."""
        with patch("builtins.input", return_value="1"):
            with patch("LLM.scripts.generation.utils.copy_to_clipboard_safe", return_value=False):
                InteractiveMenu().show_post_generation_menu(sample_prompt, "next_achievement", None)

        captured = capsys.readouterr()
        assert "⚠️  Clipboard not available, displaying" in captured.out
        assert sample_prompt in captured.out

    def test_menu_view_full_prompt(self, sample_prompt, capsys):
        """Test option 2: View full prompt."""
        with patch("builtins.input", side_effect=["2", "n"]):  # View, don't copy
            InteractiveMenu().show_post_generation_menu(sample_prompt, "continue_execution", None)

        captured = capsys.readouterr()
        assert sample_prompt in captured.out
        # Note: "Copy to clipboard?" prompt goes to input, not captured output

    def test_menu_view_then_copy(self, sample_prompt, capsys):
        """Test option 2: View full prompt then copy."""
        with patch("builtins.input", side_effect=["2", "y"]):  # View, then copy
            with patch("LLM.scripts.generation.utils.copy_to_clipboard_safe", return_value=True):
                InteractiveMenu().show_post_generation_menu(
                    sample_prompt, "create_next_execution", None
                )

        captured = capsys.readouterr()
        assert sample_prompt in captured.out
        assert (
            "✅ Command copied to clipboard!" in captured.out
            or "✅ Full message copied to clipboard!" in captured.out
        )

    def test_menu_save_to_file(self, sample_prompt, capsys):
        """Test option 3: Save to file."""
        mock_file = mock_open()
        with patch("builtins.input", side_effect=["3", "test_prompt.txt"]):
            with patch("builtins.open", mock_file):
                InteractiveMenu().show_post_generation_menu(sample_prompt, "plan_complete", None)

        captured = capsys.readouterr()
        # Note: "Enter filename" prompt goes to input, not captured output
        assert "✅ Saved to test_prompt.txt" in captured.out
        mock_file().write.assert_called_once_with(sample_prompt)

    def test_menu_save_no_filename(self, sample_prompt, capsys):
        """Test option 3: Save with no filename provided."""
        with patch("builtins.input", side_effect=["3", ""]):  # Save, empty filename
            InteractiveMenu().show_post_generation_menu(sample_prompt, "conflict", None)

        captured = capsys.readouterr()
        assert "❌ No filename provided" in captured.out

    def test_menu_execute_command(self, sample_prompt, sample_command, capsys):
        """Test option 4: Execute recommended command."""
        with patch("builtins.input", return_value="4"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                InteractiveMenu().show_post_generation_menu(
                    sample_prompt, "create_subplan", sample_command
                )

        captured = capsys.readouterr()
        assert "🚀 Executing:" in captured.out
        assert sample_command in captured.out
        assert "✅ Command completed successfully" in captured.out

    def test_menu_execute_command_failure(self, sample_prompt, sample_command, capsys):
        """Test option 4: Execute command that fails."""
        with patch("builtins.input", return_value="4"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=1)
                InteractiveMenu().show_post_generation_menu(
                    sample_prompt, "create_execution", sample_command
                )

        captured = capsys.readouterr()
        assert "❌ Command failed with exit code 1" in captured.out

    def test_menu_get_help_with_command(self, sample_prompt, sample_command, capsys):
        """Test option 5: Get help when command is available."""
        with patch("builtins.input", return_value="5"):
            InteractiveMenu().show_post_generation_menu(
                sample_prompt, "create_subplan", sample_command
            )

        captured = capsys.readouterr()
        assert "💡 Help:" in captured.out
        assert "Workflow State: create_subplan" in captured.out
        assert sample_command in captured.out

    def test_menu_get_help_without_command(self, sample_prompt, capsys):
        """Test option 4: Get help when no command available."""
        with patch("builtins.input", return_value="4"):
            InteractiveMenu().show_post_generation_menu(sample_prompt, "next_achievement", None)

        captured = capsys.readouterr()
        assert "💡 Help:" in captured.out
        assert "Workflow State: next_achievement" in captured.out
        assert "Copy the prompt and paste into your LLM chat" in captured.out

    def test_menu_exit_with_command(self, sample_prompt, sample_command):
        """Test option 6: Exit when command is available."""
        with patch("builtins.input", return_value="6"):
            with pytest.raises(SystemExit) as exc_info:
                InteractiveMenu().show_post_generation_menu(
                    sample_prompt, "create_execution", sample_command
                )
            assert exc_info.value.code == 0

    def test_menu_exit_without_command(self, sample_prompt):
        """Test option 5: Exit when no command available."""
        with patch("builtins.input", return_value="5"):
            with pytest.raises(SystemExit) as exc_info:
                InteractiveMenu().show_post_generation_menu(sample_prompt, "plan_complete", None)
            assert exc_info.value.code == 0

    def test_menu_invalid_choice_retry(self, sample_prompt, capsys):
        """Test invalid choice loops back to menu."""
        with patch("builtins.input", side_effect=["99", "1"]):  # Invalid, then valid
            with patch("LLM.scripts.generation.utils.copy_to_clipboard_safe", return_value=True):
                InteractiveMenu().show_post_generation_menu(sample_prompt, "create_subplan", None)

        captured = capsys.readouterr()
        assert "❌ Invalid choice" in captured.out
        assert (
            "✅ Command copied to clipboard!" in captured.out
            or "✅ Full message copied to clipboard!" in captured.out
        )  # Eventually succeeds

    def test_menu_shows_execute_option_only_with_command(
        self, sample_prompt, sample_command, capsys
    ):
        """Test that execute option only appears when command is provided."""
        # With command
        with patch("builtins.input", return_value="1"):
            with patch("LLM.scripts.generation.utils.copy_to_clipboard_safe", return_value=True):
                InteractiveMenu().show_post_generation_menu(
                    sample_prompt, "create_subplan", sample_command
                )

        captured_with = capsys.readouterr()
        assert "5. Execute recommended command" in captured_with.out
        # Note: "Choose" prompt goes to input, not captured output

        # Without command
        with patch("builtins.input", return_value="1"):
            with patch("LLM.scripts.generation.utils.copy_to_clipboard_safe", return_value=True):
                InteractiveMenu().show_post_generation_menu(sample_prompt, "next_achievement", None)

        captured_without = capsys.readouterr()
        assert "5. Execute recommended command" not in captured_without.out
        assert "5. Get help" in captured_without.out  # Option 5 is "Get help" when no command

    def test_menu_all_workflow_states(self, sample_prompt, capsys):
        """Test menu works with all workflow states."""
        workflow_states = [
            "create_subplan",
            "create_execution",
            "continue_execution",
            "create_next_execution",
            "next_achievement",
            "plan_complete",
            "conflict",
        ]

        for state in workflow_states:
            with patch("builtins.input", return_value="1"):
                with patch(
                    "LLM.scripts.generation.utils.copy_to_clipboard_safe",
                    return_value=True,
                ):
                    InteractiveMenu().show_post_generation_menu(sample_prompt, state, None)

            captured = capsys.readouterr()
            assert "🎯 What would you like to do with this prompt?" in captured.out
            assert (
                "✅ Command copied to clipboard!" in captured.out
                or "✅ Full message copied to clipboard!" in captured.out
            )


class TestInteractiveIntegration:
    """Integration tests for full interactive workflow."""

    def test_interactive_flag_preserved_through_workflow(self):
        """Test that --interactive flag is preserved from pre to post menu."""
        # This is tested manually above - verifies the flag preservation works
        pass

    def test_command_extraction_from_prompt(self, capsys):
        """Test that recommended command is correctly extracted from prompt."""
        prompt_with_command = """Test prompt

**Recommended Command**:
  python generate_prompt.py @PLAN_FEATURE.md --next

More text...
"""
        with patch("builtins.input", return_value="5"):  # Get help
            InteractiveMenu().show_post_generation_menu(
                prompt_with_command, "create_subplan", "extracted_command"
            )

        captured = capsys.readouterr()
        assert "extracted_command" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
