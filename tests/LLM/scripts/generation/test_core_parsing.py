"""
Tests for core PLAN parsing functions in generate_prompt.py

Tests the fundamental parsing logic that extracts structured data from PLAN files:
- parse_plan_file() - Extract achievements, feature name, archive location
- find_next_achievement_from_plan() - Find next achievement from handoff section
- extract_handoff_section() - Extract Current Status & Handoff section

Created: 2025-11-10
Achievement: 1.1 in PLAN_PROMPT-GENERATOR-UX-AND-FOUNDATION.md
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, mock_open

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from LLM.scripts.generation.workflow_detector import WorkflowDetector
from LLM.scripts.generation.plan_parser import PlanParser

# Create instances for tests
detector = WorkflowDetector()
parser = PlanParser()
parse_plan_file = parser.parse_plan_file
find_next_achievement_from_plan = detector.find_next_achievement_from_plan
extract_handoff_section = parser.extract_handoff_section


class TestParsePlanFile:
    """Test suite for parse_plan_file() function."""

    @pytest.fixture
    def sample_plan_path(self, tmp_path):
        """Create a sample PLAN file for testing."""
        plan_content = """# PLAN: Test Feature

**Achievement 0.1**: First Achievement

Purpose: Test first achievement

**Achievement 0.2**: Second Achievement

Purpose: Test second achievement

**Achievement 1.1**: Third Achievement

Purpose: Test third achievement

## 📋 Current Status & Handoff

**Next**: Achievement 0.2

**Archive Location**: documentation/archive/test-feature-2025-11/
"""
        plan_file = tmp_path / "PLAN_TEST-FEATURE.md"
        plan_file.write_text(plan_content)
        return plan_file

    def test_parse_plan_file_valid(self, sample_plan_path):
        """Test parsing a valid PLAN file."""
        result = parse_plan_file(sample_plan_path)

        assert result["feature_name"] == "TEST-FEATURE"
        assert len(result["achievements"]) == 3
        assert result["achievements"][0].number == "0.1"
        assert result["achievements"][1].number == "0.2"
        assert result["achievements"][2].number == "1.1"
        assert result["archive_location"] is not None  # Archive location extracted

    def test_parse_plan_file_no_achievements(self, tmp_path):
        """Test parsing PLAN with no achievements."""
        plan_content = """# PLAN: Empty Feature

No achievements defined yet.
"""
        plan_file = tmp_path / "PLAN_EMPTY.md"
        plan_file.write_text(plan_content)

        result = parse_plan_file(plan_file)

        assert result["feature_name"] == "EMPTY"
        assert len(result["achievements"]) == 0

    def test_parse_plan_file_extracts_feature_name(self, tmp_path):
        """Test feature name extraction from filename."""
        plan_file = tmp_path / "PLAN_COMPLEX-FEATURE-NAME.md"
        plan_file.write_text("# PLAN: Test\n\n**Achievement 1.1**: Test")

        result = parse_plan_file(plan_file)

        assert result["feature_name"] == "COMPLEX-FEATURE-NAME"

    def test_parse_plan_file_counts_lines(self, sample_plan_path):
        """Test that total line count is accurate."""
        result = parse_plan_file(sample_plan_path)

        assert result["total_plan_lines"] > 0
        assert isinstance(result["total_plan_lines"], int)


class TestExtractHandoffSection:
    """Test suite for extract_handoff_section() function."""

    def test_extract_handoff_section_found(self):
        """Test extracting handoff section when it exists."""
        plan_content = """# PLAN: Test

**Achievement 1.1**: Test

## 📋 Current Status & Handoff

**Next**: Achievement 0.2
**Status**: In Progress

## Other Section

More content
"""
        result = extract_handoff_section(plan_content)

        assert result is not None
        assert "**Next**: Achievement 0.2" in result
        assert "**Status**: In Progress" in result
        assert "## Other Section" not in result  # Should stop at next section

    def test_extract_handoff_section_not_found(self):
        """Test when handoff section doesn't exist."""
        plan_content = """# PLAN: Test

**Achievement 1.1**: Test

No handoff section here.
"""
        result = extract_handoff_section(plan_content)

        assert result is None

    def test_extract_handoff_section_various_formats(self):
        """Test extraction with various section header formats."""
        # Test with different emoji
        plan_content1 = """## 📋 Current Status & Handoff

Content here
"""
        assert extract_handoff_section(plan_content1) is not None

        # Test without emoji
        plan_content2 = """## Current Status & Handoff

Content here
"""
        assert extract_handoff_section(plan_content2) is not None


class TestFindNextAchievementFromPlan:
    """Test suite for find_next_achievement_from_plan() function."""

    def test_find_next_from_handoff_section(self):
        """Test finding next achievement from handoff section."""
        plan_content = """# PLAN: Test

## 📋 Current Status & Handoff

**Next**: Achievement 1.2

## Achievements

**Achievement 1.1**: First
**Achievement 1.2**: Second
"""
        result = find_next_achievement_from_plan(plan_content)

        assert result == "1.2"

    def test_find_next_with_pending_emoji(self):
        """Test finding with ⏳ emoji format."""
        plan_content = """## Current Status & Handoff

⏳ Next: Achievement 2.3
"""
        result = find_next_achievement_from_plan(plan_content)

        assert result == "2.3"

    def test_find_next_fallback_to_full_file(self):
        """Test fallback to full file when not in handoff."""
        plan_content = """# PLAN: Test

**Next**: Achievement 0.1

## Some Section

Content
"""
        result = find_next_achievement_from_plan(plan_content)

        assert result == "0.1"

    def test_find_next_not_found(self):
        """Test when no next achievement is specified."""
        plan_content = """# PLAN: Test

No next achievement mentioned.
"""
        result = find_next_achievement_from_plan(plan_content)

        assert result is None

    def test_find_next_prioritizes_handoff_section(self):
        """Test that handoff section is prioritized over full file."""
        plan_content = """# PLAN: Test

**Next**: Achievement 0.1

## 📋 Current Status & Handoff

**Next**: Achievement 1.1

## Other

**Next**: Achievement 2.1
"""
        result = find_next_achievement_from_plan(plan_content)

        # Should find 1.1 from handoff, not 0.1 from earlier
        assert result == "1.1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
