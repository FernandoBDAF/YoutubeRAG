"""
Tests for utils module.

Tests helper utility functions.
"""

import pytest
from datetime import datetime

from LLM.dashboard.utils import (
    format_timestamp,
    format_date,
    truncate_text,
    validate_plan_name,
    parse_achievement_number,
)


class TestFormatTimestamp:
    """Tests for format_timestamp function."""

    def test_format_timestamp_basic(self):
        """Test timestamp formatting with known datetime."""
        dt = datetime(2025, 11, 13, 14, 32, 15)
        result = format_timestamp(dt)

        assert result == "14:32:15"

    def test_format_timestamp_midnight(self):
        """Test timestamp formatting at midnight."""
        dt = datetime(2025, 11, 13, 0, 0, 0)
        result = format_timestamp(dt)

        assert result == "00:00:00"

    def test_format_timestamp_late_night(self):
        """Test timestamp formatting late at night."""
        dt = datetime(2025, 11, 13, 23, 59, 59)
        result = format_timestamp(dt)

        assert result == "23:59:59"


class TestFormatDate:
    """Tests for format_date function."""

    def test_format_date_basic(self):
        """Test date formatting with known datetime."""
        dt = datetime(2025, 11, 13, 14, 32, 15)
        result = format_date(dt)

        assert result == "2025-11-13"

    def test_format_date_new_year(self):
        """Test date formatting on new year."""
        dt = datetime(2025, 1, 1, 0, 0, 0)
        result = format_date(dt)

        assert result == "2025-01-01"

    def test_format_date_end_of_year(self):
        """Test date formatting at end of year."""
        dt = datetime(2025, 12, 31, 23, 59, 59)
        result = format_date(dt)

        assert result == "2025-12-31"


class TestTruncateText:
    """Tests for truncate_text function."""

    def test_truncate_text_short(self):
        """Test truncation with text shorter than max_length."""
        text = "Short text"
        result = truncate_text(text, max_length=50)

        assert result == "Short text"

    def test_truncate_text_exact_length(self):
        """Test truncation with text exactly at max_length."""
        text = "A" * 50
        result = truncate_text(text, max_length=50)

        assert result == "A" * 50

    def test_truncate_text_long(self):
        """Test truncation with text longer than max_length."""
        text = "This is a very long achievement title that needs truncation for display"
        result = truncate_text(text, max_length=30)

        assert len(result) == 30
        assert result.endswith("...")
        assert result == "This is a very long achieve..."

    def test_truncate_text_default_length(self):
        """Test truncation with default max_length (50)."""
        text = "A" * 100
        result = truncate_text(text)

        assert len(result) == 50
        assert result.endswith("...")

    def test_truncate_text_custom_length(self):
        """Test truncation with custom max_length."""
        text = "A" * 100
        result = truncate_text(text, max_length=20)

        assert len(result) == 20
        assert result.endswith("...")

    def test_truncate_text_empty(self):
        """Test truncation with empty string."""
        text = ""
        result = truncate_text(text, max_length=50)

        assert result == ""


class TestValidatePlanName:
    """Tests for validate_plan_name function."""

    def test_validate_plan_name_valid(self):
        """Test validation with valid plan name."""
        assert validate_plan_name("MY-PLAN") is True
        assert validate_plan_name("PLAN_NAME") is True
        assert validate_plan_name("Plan123") is True

    def test_validate_plan_name_empty(self):
        """Test validation with empty string."""
        assert validate_plan_name("") is False

    def test_validate_plan_name_dot_prefix(self):
        """Test validation with dot prefix (invalid)."""
        assert validate_plan_name(".hidden") is False
        assert validate_plan_name("..plan") is False

    def test_validate_plan_name_whitespace(self):
        """Test validation with whitespace."""
        assert validate_plan_name("   ") is False

    def test_validate_plan_name_single_char(self):
        """Test validation with single character."""
        assert validate_plan_name("A") is True

    def test_validate_plan_name_with_spaces(self):
        """Test validation with spaces (valid)."""
        assert validate_plan_name("MY PLAN") is True

    def test_validate_plan_name_with_special_chars(self):
        """Test validation with special characters (valid)."""
        assert validate_plan_name("PLAN-2.0_beta") is True


class TestParseAchievementNumber:
    """Tests for parse_achievement_number function."""

    def test_parse_approved_file(self):
        """Test parsing APPROVED_XX.md format."""
        assert parse_achievement_number("APPROVED_31.md") == "3.1"
        assert parse_achievement_number("APPROVED_12.md") == "1.2"
        assert parse_achievement_number("APPROVED_01.md") == "0.1"

    def test_parse_fix_file(self):
        """Test parsing FIX_XX.md format."""
        assert parse_achievement_number("FIX_21.md") == "2.1"
        assert parse_achievement_number("FIX_33.md") == "3.3"

    def test_parse_subplan_file(self):
        """Test parsing SUBPLAN_XX.md format."""
        assert parse_achievement_number("SUBPLAN_02.md") == "0.2"
        assert parse_achievement_number("SUBPLAN_11.md") == "1.1"

    def test_parse_execution_file(self):
        """Test parsing EXECUTION_TASK_XX_01.md format."""
        assert parse_achievement_number("EXECUTION_TASK_11_01.md") == "1.1"
        assert parse_achievement_number("EXECUTION_TASK_23_01.md") == "2.3"

    def test_parse_with_plan_name(self):
        """Test parsing with plan name in filename."""
        assert parse_achievement_number("SUBPLAN_MY-PLAN_12.md") == "1.2"
        assert parse_achievement_number("APPROVED_PARALLEL-EXEC_31.md") == "3.1"

    def test_parse_without_extension(self):
        """Test parsing filename without extension."""
        assert parse_achievement_number("APPROVED_31") == "3.1"
        assert parse_achievement_number("FIX_12") == "1.2"

    def test_parse_invalid_format(self):
        """Test parsing filename with no achievement number."""
        with pytest.raises(ValueError, match="No achievement number found"):
            parse_achievement_number("PLAN_FILE.md")

        with pytest.raises(ValueError, match="No achievement number found"):
            parse_achievement_number("README.md")
