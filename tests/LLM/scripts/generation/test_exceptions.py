"""
Tests for custom prompt generation exceptions.

Tests exception creation, message formatting, context handling, and suggestions.
"""

import pytest
from pathlib import Path
from LLM.scripts.generation.exceptions import (
    PlanNotFoundError,
    AchievementNotFoundError,
    SubplanNotFoundError,
    InvalidAchievementFormatError,
    ExecutionTaskNotFoundError,
    InvalidPathError,
    format_error_with_suggestions,
)


class TestPlanNotFoundError:
    """Tests for PlanNotFoundError."""

    def test_basic_error(self):
        """Test basic PlanNotFoundError creation."""
        error = PlanNotFoundError(
            plan_name="FEATURE-NAME",
            searched_paths=[Path("work-space/plans/FEATURE-NAME")],
        )

        assert "PLAN file not found: FEATURE-NAME" in str(error)
        assert error.context["plan_name"] == "FEATURE-NAME"
        assert len(error.context["searched_paths"]) == 1
        assert "suggestions" in error.context

    def test_with_available_plans(self):
        """Test PlanNotFoundError with available plans list."""
        error = PlanNotFoundError(
            plan_name="NONEXISTENT",
            available_plans=["PLAN-A", "PLAN-B", "PLAN-C"],
        )

        assert "available_plans" in error.context
        assert len(error.context["available_plans"]) == 3
        assert any("@PLAN-A" in s for s in error.context["suggestions"])

    def test_with_cause(self):
        """Test PlanNotFoundError with cause exception."""
        original = FileNotFoundError("No such file")
        error = PlanNotFoundError(
            plan_name="TEST",
            cause=original,
        )

        assert error.cause == original
        assert "FileNotFoundError" in str(error)


class TestAchievementNotFoundError:
    """Tests for AchievementNotFoundError."""

    def test_basic_error(self):
        """Test basic AchievementNotFoundError creation."""
        error = AchievementNotFoundError(
            achievement_num="2.1",
            plan_name="FEATURE",
        )

        assert "Achievement 2.1 not found" in str(error)
        assert error.context["achievement_num"] == "2.1"
        assert error.context["plan_name"] == "FEATURE"
        assert "suggestions" in error.context

    def test_with_available_achievements(self):
        """Test with available achievements list."""
        achievements = ["1.1", "1.2", "2.1", "2.2", "3.1"]
        error = AchievementNotFoundError(
            achievement_num="9.9",
            plan_name="FEATURE",
            available_achievements=achievements,
        )

        assert "available_achievements" in error.context
        assert any("1.1" in s for s in error.context["suggestions"])

    def test_truncates_long_achievement_list(self):
        """Test that long achievement lists are truncated."""
        achievements = [f"{i}.{j}" for i in range(1, 5) for j in range(1, 10)]  # 36 achievements
        error = AchievementNotFoundError(
            achievement_num="99.99",
            plan_name="FEATURE",
            available_achievements=achievements,
        )

        # Should show first 10 and indicate more
        suggestion_text = "\n".join(error.context["suggestions"])
        assert "... and" in suggestion_text


class TestSubplanNotFoundError:
    """Tests for SubplanNotFoundError."""

    def test_basic_error(self):
        """Test basic SubplanNotFoundError creation."""
        error = SubplanNotFoundError(
            achievement_num="2.1",
            plan_name="FEATURE",
        )

        assert "SUBPLAN not found for Achievement 2.1" in str(error)
        assert error.context["achievement_num"] == "2.1"
        assert error.context["plan_name"] == "FEATURE"

    def test_with_expected_path(self):
        """Test with expected path."""
        expected_path = Path("work-space/plans/FEATURE/subplans/SUBPLAN_FEATURE_21.md")
        error = SubplanNotFoundError(
            achievement_num="2.1",
            plan_name="FEATURE",
            expected_path=expected_path,
        )

        assert "expected_path" in error.context
        assert str(expected_path) in str(error)

    def test_with_available_subplans(self):
        """Test with available subplans list."""
        subplans = ["SUBPLAN_FEATURE_11.md", "SUBPLAN_FEATURE_12.md"]
        error = SubplanNotFoundError(
            achievement_num="2.1",
            plan_name="FEATURE",
            available_subplans=subplans,
        )

        assert "available_subplans" in error.context
        assert any("SUBPLAN_FEATURE_11.md" in s for s in error.context["suggestions"])


class TestInvalidAchievementFormatError:
    """Tests for InvalidAchievementFormatError."""

    def test_basic_error(self):
        """Test basic InvalidAchievementFormatError creation."""
        error = InvalidAchievementFormatError(
            achievement_input="2",
        )

        assert "Invalid achievement format: '2'" in str(error)
        assert error.context["achievement_input"] == "2"
        assert error.context["expected_format"] == "X.Y"

    def test_custom_expected_format(self):
        """Test with custom expected format."""
        error = InvalidAchievementFormatError(
            achievement_input="2.1.3",
            expected_format="X.Y (two numbers only)",
        )

        assert error.context["expected_format"] == "X.Y (two numbers only)"
        assert any("X.Y (two numbers only)" in s for s in error.context["suggestions"])

    def test_suggestions_present(self):
        """Test that suggestions are helpful."""
        error = InvalidAchievementFormatError(
            achievement_input="invalid",
        )

        suggestions = error.context["suggestions"]
        assert len(suggestions) >= 3
        assert any("1.1" in s or "2.5" in s for s in suggestions)  # Examples


class TestExecutionTaskNotFoundError:
    """Tests for ExecutionTaskNotFoundError."""

    def test_basic_error(self):
        """Test basic ExecutionTaskNotFoundError creation."""
        error = ExecutionTaskNotFoundError(
            achievement_num="2.1",
            execution_num="01",
            plan_name="FEATURE",
        )

        assert "EXECUTION_TASK not found" in str(error)
        assert error.context["achievement_num"] == "2.1"
        assert error.context["execution_num"] == "01"

    def test_with_expected_path(self):
        """Test with expected path."""
        expected_path = Path("work-space/plans/FEATURE/execution/EXECUTION_TASK_FEATURE_21_01.md")
        error = ExecutionTaskNotFoundError(
            achievement_num="2.1",
            execution_num="01",
            plan_name="FEATURE",
            expected_path=expected_path,
        )

        assert "expected_path" in error.context
        assert str(expected_path) in str(error)


class TestInvalidPathError:
    """Tests for InvalidPathError."""

    def test_basic_error(self):
        """Test basic InvalidPathError creation."""
        path = Path("nonexistent/file.txt")
        error = InvalidPathError(
            path=path,
            reason="file does not exist",
        )

        assert "Invalid file path" in str(error)
        assert "file does not exist" in str(error)
        assert error.context["path_type"] == "file"

    def test_directory_path_type(self):
        """Test with directory path type."""
        path = Path("nonexistent/dir")
        error = InvalidPathError(
            path=path,
            reason="directory not found",
            path_type="directory",
        )

        assert "Invalid directory path" in str(error)
        assert error.context["path_type"] == "directory"


class TestFormatErrorWithSuggestions:
    """Tests for format_error_with_suggestions helper."""

    def test_formats_plan_not_found_error(self):
        """Test formatting PlanNotFoundError."""
        error = PlanNotFoundError(
            plan_name="FEATURE",
            available_plans=["PLAN-A", "PLAN-B"],
        )

        formatted = format_error_with_suggestions(error)

        assert "❌ ERROR:" in formatted
        assert "PLAN file not found: FEATURE" in formatted
        assert "HOW TO FIX:" in formatted
        assert "@PLAN-A" in formatted

    def test_formats_achievement_not_found_error(self):
        """Test formatting AchievementNotFoundError."""
        error = AchievementNotFoundError(
            achievement_num="2.1",
            plan_name="FEATURE",
            available_achievements=["1.1", "1.2"],
        )

        formatted = format_error_with_suggestions(error)

        assert "❌ ERROR:" in formatted
        assert "Achievement 2.1 not found" in formatted
        assert "HOW TO FIX:" in formatted

    def test_includes_context_details(self):
        """Test that context details are included."""
        error = InvalidAchievementFormatError(
            achievement_input="invalid",
        )

        formatted = format_error_with_suggestions(error)

        assert "Details:" in formatted
        assert "achievement_input: invalid" in formatted
        assert "expected_format: X.Y" in formatted

    def test_excludes_suggestions_from_context(self):
        """Test that suggestions aren't duplicated in context."""
        error = PlanNotFoundError(
            plan_name="FEATURE",
        )

        formatted = format_error_with_suggestions(error)

        # Suggestions should appear once under "HOW TO FIX:", not in Details:
        details_section = formatted.split("HOW TO FIX:")[0]
        assert "suggestions" not in details_section.lower()
