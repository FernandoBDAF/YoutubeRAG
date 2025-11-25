"""
Tests for InteractiveMenu class in interactive_menu.py

Tests the InteractiveMenu class that provides two-stage interactive experience:
- Pre-execution menu: Choose workflow
- Post-generation menu: Handle output
- Feedback generation helper

Created: 2025-11-11
Achievement: 2.1 in PLAN_PROMPT-GENERATOR-UX-AND-FOUNDATION.md
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from io import StringIO

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from LLM.scripts.generation.interactive_menu import InteractiveMenu


class TestInteractiveMenu:
    """Test suite for InteractiveMenu class."""

    def test_class_instantiation(self):
        """Test that InteractiveMenu can be instantiated."""
        menu = InteractiveMenu()
        assert menu is not None
        assert isinstance(menu, InteractiveMenu)

    def test_show_pre_execution_menu_option_1(self, capsys):
        """Test pre-execution menu option 1: Next achievement (default)."""
        original_argv = sys.argv.copy()
        try:
            sys.argv = ["generate_prompt.py", "@TEST"]
            with patch("builtins.input", return_value="1"):
                menu = InteractiveMenu()
                menu.show_pre_execution_menu()

            # Verify sys.argv was modified
            assert "--next" in sys.argv
            assert "--interactive" in sys.argv
        finally:
            sys.argv = original_argv

    def test_show_pre_execution_menu_option_2(self, capsys):
        """Test pre-execution menu option 2: Specific achievement."""
        original_argv = sys.argv.copy()
        try:
            sys.argv = ["generate_prompt.py", "@TEST"]
            with patch("builtins.input", side_effect=["2", "1.1"]):
                menu = InteractiveMenu()
                menu.show_pre_execution_menu()

            # Verify sys.argv was modified with achievement
            assert "--achievement" in sys.argv
            assert "1.1" in sys.argv
        finally:
            sys.argv = original_argv

    def test_show_pre_execution_menu_option_3(self, capsys):
        """Test pre-execution menu option 3: View achievements."""
        with patch("sys.argv", ["generate_prompt.py", "@TEST"]):
            with patch("builtins.input", return_value="3"):
                menu = InteractiveMenu()
                with pytest.raises(SystemExit):
                    menu.show_pre_execution_menu()

        captured = capsys.readouterr()
        assert "Available achievements" in captured.out

    def test_show_pre_execution_menu_option_5(self, capsys):
        """Test pre-execution menu option 5: Exit."""
        with patch("sys.argv", ["generate_prompt.py", "@TEST"]):
            with patch("builtins.input", return_value="5"):
                menu = InteractiveMenu()
                with pytest.raises(SystemExit):
                    menu.show_pre_execution_menu()

    def test_show_post_generation_menu_single_command(self, capsys):
        """Test post-generation menu with single command detected."""
        prompt = "**Recommended Command**:\n  python test.py"
        with patch("builtins.input", return_value="1"):
            with patch(
                "LLM.scripts.generation.utils.copy_to_clipboard_safe",
                return_value=True,
            ):
                menu = InteractiveMenu()
                menu.show_post_generation_menu(prompt, "create_subplan")

        captured = capsys.readouterr()
        assert "Copy command to clipboard" in captured.out
        assert "Command copied to clipboard" in captured.out

    def test_show_post_generation_menu_multiple_commands(self, capsys):
        """Test post-generation menu with multiple commands detected."""
        prompt = "**Recommended Command**:\n  python test1.py\n\nOr use test2 directly:\n  python test2.py"
        with patch("builtins.input", return_value="1"):
            with patch(
                "LLM.scripts.generation.utils.copy_to_clipboard_safe",
                return_value=True,
            ):
                menu = InteractiveMenu()
                menu.show_post_generation_menu(prompt, "create_execution")

        captured = capsys.readouterr()
        assert "Copy first command" in captured.out
        assert "Copy second command" in captured.out

    def test_show_post_generation_menu_no_commands(self, capsys):
        """Test post-generation menu with no commands detected."""
        prompt = "This is a simple prompt without commands."
        with patch("builtins.input", return_value="1"):
            with patch(
                "LLM.scripts.generation.utils.copy_to_clipboard_safe",
                return_value=True,
            ):
                menu = InteractiveMenu()
                menu.show_post_generation_menu(prompt, "next_achievement")

        captured = capsys.readouterr()
        assert "Copy to clipboard" in captured.out
        assert "Copied to clipboard" in captured.out

    def test_show_post_generation_menu_with_feedback_option(self, capsys):
        """Test post-generation menu includes feedback option when plan_path and achievement_num provided."""
        prompt = "Test prompt"
        plan_path = Path("work-space/plans/TEST/PLAN_TEST.md")
        achievement_num = "1.1"

        with patch("builtins.input", return_value="5"):  # Select feedback option
            menu = InteractiveMenu()
            with patch("LLM.scripts.generation.interactive_menu.subprocess.run") as mock_subprocess:
                mock_subprocess.return_value = MagicMock(returncode=0, stdout="Feedback prompt")
                try:
                    menu.show_post_generation_menu(
                        prompt, "create_subplan", None, plan_path, achievement_num
                    )
                except SystemExit:
                    pass  # Expected when feedback is generated

        captured = capsys.readouterr()
        assert "Generate feedback" in captured.out

    def test_show_post_generation_menu_view_prompt(self, capsys):
        """Test post-generation menu option: View full prompt."""
        prompt = "**Recommended Command**:\n  python test.py\n\nFull prompt text here."
        with patch("builtins.input", side_effect=["3", "c"]):  # View, then copy command
            with patch(
                "LLM.scripts.generation.utils.copy_to_clipboard_safe",
                return_value=True,
            ):
                menu = InteractiveMenu()
                menu.show_post_generation_menu(prompt, "create_subplan")

        captured = capsys.readouterr()
        assert "Full prompt text here" in captured.out

    def test_show_post_generation_menu_save_to_file(self, capsys):
        """Test post-generation menu option: Save to file."""
        prompt = "Test prompt content"
        with patch(
            "builtins.input", side_effect=["3", "test_output.txt"]
        ):  # Option 3 for no-command menu
            with patch("builtins.open", create=True) as mock_open:
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file
                menu = InteractiveMenu()
                menu.show_post_generation_menu(prompt, "create_subplan")

        captured = capsys.readouterr()
        assert "Saved to test_output.txt" in captured.out

    def test_show_post_generation_menu_execute_command(self, capsys):
        """Test post-generation menu option: Execute recommended command."""
        prompt = "**Recommended Command**:\n  python test.py"
        command = "python test.py"
        with patch("builtins.input", return_value="5"):  # Option 5 for single-command menu
            with patch("LLM.scripts.generation.interactive_menu.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                menu = InteractiveMenu()
                menu.show_post_generation_menu(prompt, "create_subplan", command, None, None)

        captured = capsys.readouterr()
        assert "Executing" in captured.out
        assert "completed successfully" in captured.out

    def test_show_post_generation_menu_get_help(self, capsys):
        """Test post-generation menu option: Get help."""
        prompt = "**Recommended Command**:\n  python test.py"
        with patch(
            "builtins.input", return_value="5"
        ):  # Option 5 is "Get help" when no command param
            menu = InteractiveMenu()
            menu.show_post_generation_menu(prompt, "create_subplan", None)

        captured = capsys.readouterr()
        assert "💡 Help" in captured.out or "Help" in captured.out
        assert "Workflow State" in captured.out

    def test_show_post_generation_menu_invalid_choice_retry(self, capsys):
        """Test post-generation menu retries on invalid choice."""
        prompt = "Test prompt"
        with patch("builtins.input", side_effect=["99", "1"]):  # Invalid, then valid
            with patch(
                "LLM.scripts.generation.utils.copy_to_clipboard_safe",
                return_value=True,
            ):
                menu = InteractiveMenu()
                menu.show_post_generation_menu(prompt, "create_subplan")

        captured = capsys.readouterr()
        assert "Invalid choice" in captured.out

    def test_generate_feedback_interactive_success(self, capsys):
        """Test generate_feedback_interactive successfully calls subprocess."""
        plan_path = Path("work-space/plans/TEST/PLAN_TEST.md")
        achievement_num = "1.1"

        with patch("LLM.scripts.generation.interactive_menu.subprocess.run") as mock_subprocess:
            mock_subprocess.return_value = MagicMock(
                returncode=0, stdout="Feedback prompt generated", stderr=""
            )
            menu = InteractiveMenu()
            menu.generate_feedback_interactive(plan_path, achievement_num)

        captured = capsys.readouterr()
        assert "Generating feedback prompt" in captured.out
        assert "Feedback prompt generated and copied to clipboard" in captured.out

    def test_generate_feedback_interactive_failure(self, capsys):
        """Test generate_feedback_interactive handles subprocess failure."""
        plan_path = Path("work-space/plans/TEST/PLAN_TEST.md")
        achievement_num = "1.1"

        with patch("LLM.scripts.generation.interactive_menu.subprocess.run") as mock_subprocess:
            mock_subprocess.return_value = MagicMock(
                returncode=1, stdout="", stderr="Error: Script failed"
            )
            menu = InteractiveMenu()
            menu.generate_feedback_interactive(plan_path, achievement_num)

        captured = capsys.readouterr()
        assert "Error generating feedback prompt" in captured.out

    def test_generate_feedback_interactive_exception(self, capsys):
        """Test generate_feedback_interactive handles exceptions."""
        plan_path = Path("work-space/plans/TEST/PLAN_TEST.md")
        achievement_num = "1.1"

        with patch(
            "LLM.scripts.generation.interactive_menu.subprocess.run",
            side_effect=Exception("Test exception"),
        ):
            menu = InteractiveMenu()
            menu.generate_feedback_interactive(plan_path, achievement_num)

        captured = capsys.readouterr()
        assert "Error" in captured.out
