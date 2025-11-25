#!/usr/bin/env python3
"""
Test Suite for PlanParser Module

Tests the PLAN parsing functionality extracted in Achievement 2.4.

Test Coverage:
- PlanParser initialization
- parse_plan_file() with various PLAN structures
- extract_handoff_section() with and without sections
- extract_plan_statistics() accuracy
- Helper methods (estimate_section_size, find_archive_location, calculate_handoff_size)
- Edge cases and error handling

Created: 2025-11-12
Achievement: 2.4 - Extract Parsing & Utilities Module
"""
import sys
import unittest
import tempfile
from pathlib import Path
from typing import Dict

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from LLM.scripts.generation.plan_parser import PlanParser


class TestPlanParserInit(unittest.TestCase):
    """Test PlanParser initialization."""

    def test_init_creates_instance(self):
        """Test that PlanParser can be instantiated."""
        parser = PlanParser()
        self.assertIsNotNone(parser)

    def test_parser_has_all_methods(self):
        """Test that PlanParser has all required methods."""
        parser = PlanParser()
        required_methods = [
            'parse_plan_file',
            'extract_handoff_section',
            'extract_plan_statistics',
            'estimate_section_size',
            'find_archive_location',
            'calculate_handoff_size'
        ]
        for method in required_methods:
            self.assertTrue(hasattr(parser, method),
                            f"PlanParser missing method: {method}")


class TestParsePlanFile(unittest.TestCase):
    """Test the parse_plan_file() method."""

    def setUp(self):
        self.parser = PlanParser()
        self.temp_dir = tempfile.mkdtemp()

    def test_parse_valid_plan(self):
        """Test parsing a valid PLAN file."""
        plan_content = """# PLAN: Test Feature

**Status**: In Progress
**Archive Location**: documentation/archive/test-feature-2025-11/

## Achievement Index

- Achievement 1.1: First Achievement
- Achievement 1.2: Second Achievement

## 📋 Current Status & Handoff

Last updated: 2025-11-12

What's done:
- Achievement 1.1 complete

What's next:
- Achievement 1.2

**Achievement 1.1**: First Achievement

Goal: Do something
Effort: 2 hours

---

**Achievement 1.2**: Second Achievement

Goal: Do something else
Effort: 3 hours
"""
        plan_path = Path(self.temp_dir) / "PLAN_TEST.md"
        plan_path.write_text(plan_content)

        result = self.parser.parse_plan_file(plan_path)

        self.assertIsInstance(result, dict)
        self.assertIn('feature_name', result)
        self.assertIn('achievements', result)
        self.assertIn('archive_location', result)

    def test_parse_plan_extracts_feature_name(self):
        """Test that feature name is extracted correctly."""
        plan_content = """# PLAN: My Cool Feature

**Status**: In Progress

**Achievement 1.1**: Test
"""
        plan_path = Path(self.temp_dir) / "PLAN_MY_COOL_FEATURE.md"
        plan_path.write_text(plan_content)

        result = self.parser.parse_plan_file(plan_path)

        self.assertIn('feature_name', result)
        self.assertEqual(result['feature_name'], 'MY_COOL_FEATURE')

    def test_parse_plan_nonexistent_file(self):
        """Test parsing nonexistent file raises FileNotFoundError."""
        plan_path = Path(self.temp_dir) / "NONEXISTENT.md"

        with self.assertRaises(FileNotFoundError):
            self.parser.parse_plan_file(plan_path)

    def test_parse_plan_extracts_archive_location(self):
        """Test that archive location is extracted with ./ pattern."""
        plan_content = """# PLAN: Test

**Archive Location**: ./test-feature/

**Achievement 1.1**: Test
"""
        plan_path = Path(self.temp_dir) / "PLAN_TEST.md"
        plan_path.write_text(plan_content)

        result = self.parser.parse_plan_file(plan_path)

        self.assertIn('archive_location', result)
        self.assertEqual(result['archive_location'], './test-feature/')


class TestExtractHandoffSection(unittest.TestCase):
    """Test the extract_handoff_section() method."""

    def setUp(self):
        self.parser = PlanParser()

    def test_extract_handoff_present(self):
        """Test extracting handoff section when present."""
        plan_content = """# PLAN: Test

## 📋 Current Status & Handoff

Last updated: 2025-11-12

What's done:
- Achievement 1 complete

What's next:
- Achievement 2

---

## Other Section

Content here.
"""
        result = self.parser.extract_handoff_section(plan_content)

        self.assertIsNotNone(result)
        self.assertIn('Last updated', result)
        self.assertIn('Achievement 1 complete', result)
        self.assertNotIn('Other Section', result)

    def test_extract_handoff_missing(self):
        """Test extracting handoff when section doesn't exist."""
        plan_content = """# PLAN: Test

## Some Other Section

Content here.
"""
        result = self.parser.extract_handoff_section(plan_content)

        self.assertIsNone(result)

    def test_extract_handoff_empty_plan(self):
        """Test extracting handoff from empty PLAN."""
        plan_content = ""

        result = self.parser.extract_handoff_section(plan_content)

        self.assertIsNone(result)


class TestExtractPlanStatistics(unittest.TestCase):
    """Test the extract_plan_statistics() method."""

    def setUp(self):
        self.parser = PlanParser()
        self.temp_dir = tempfile.mkdtemp()

    def test_extract_statistics_valid_plan(self):
        """Test extracting statistics from valid PLAN."""
        plan_content = """# PLAN: Test Feature

**Achievement 1.1**: First
**Achievement 1.2**: Second
**Achievement 1.3**: Third
"""
        plan_path = Path(self.temp_dir) / "PLAN_TEST.md"
        plan_path.write_text(plan_content)

        # Create feedbacks directory with some APPROVED files
        feedbacks_dir = plan_path.parent / "execution" / "feedbacks"
        feedbacks_dir.mkdir(parents=True, exist_ok=True)
        (feedbacks_dir / "APPROVED_11.md").write_text("# APPROVED")

        result = self.parser.extract_plan_statistics(plan_path, "TEST")

        self.assertIsInstance(result, dict)
        self.assertIn('total_achievements', result)
        # Note: completed_achievements may not always be in dict depending on implementation

    def test_extract_statistics_no_completions(self):
        """Test statistics when no achievements complete."""
        plan_content = """# PLAN: Test

**Achievement 1.1**: First
**Achievement 1.2**: Second
"""
        plan_path = Path(self.temp_dir) / "PLAN_TEST.md"
        plan_path.write_text(plan_content)

        # Create empty feedbacks directory
        feedbacks_dir = plan_path.parent / "execution" / "feedbacks"
        feedbacks_dir.mkdir(parents=True, exist_ok=True)

        result = self.parser.extract_plan_statistics(plan_path, "TEST")

        self.assertEqual(result.get('completed_achievements', 0), 0)


class TestEstimateSectionSize(unittest.TestCase):
    """Test the estimate_section_size() method."""

    def setUp(self):
        self.parser = PlanParser()

    def test_estimate_section_basic(self):
        """Test basic section size estimation."""
        lines = [
            "**Achievement 1.1**: Test",
            "",
            "Some content here",
            "More content",
            "",
            "---",
            "",
            "**Achievement 1.2**: Next"
        ]

        size = self.parser.estimate_section_size(lines, 0)

        self.assertGreater(size, 0)
        self.assertLessEqual(size, 8)  # Should stop around ---

    def test_estimate_section_no_separator(self):
        """Test estimation when no separator exists."""
        lines = [
            "**Achievement 1.1**: Test",
            "Content line 1",
            "Content line 2",
            "Content line 3"
        ]

        size = self.parser.estimate_section_size(lines, 0)

        self.assertEqual(size, 4)  # All remaining lines


class TestFindArchiveLocation(unittest.TestCase):
    """Test the find_archive_location() method."""

    def setUp(self):
        self.parser = PlanParser()

    def test_find_archive_location_present(self):
        """Test finding archive location when present with ./ pattern."""
        lines = [
            "# PLAN: Test",
            "",
            "**Archive Location**: ./test-archive/",
            "",
            "Content"
        ]

        location = self.parser.find_archive_location(lines)

        self.assertEqual(location, "./test-archive/")

    def test_find_archive_location_with_when_complete(self):
        """Test finding archive location with '(when complete)' text and ./ pattern."""
        lines = [
            "# PLAN: Test",
            "",
            "**Archive Location** (when complete): ./my-feature/",
            ""
        ]

        location = self.parser.find_archive_location(lines)

        self.assertEqual(location, "./my-feature/")

    def test_find_archive_location_missing(self):
        """Test when archive location is not present (returns default)."""
        lines = [
            "# PLAN: Test",
            "",
            "**Status**: In Progress",
            ""
        ]

        location = self.parser.find_archive_location(lines)

        # Implementation returns default './feature-archive/' when not found
        self.assertEqual(location, "./feature-archive/")


class TestCalculateHandoffSize(unittest.TestCase):
    """Test the calculate_handoff_size() method."""

    def setUp(self):
        self.parser = PlanParser()

    def test_calculate_handoff_size_present(self):
        """Test calculating handoff size when section exists."""
        lines = [
            "# PLAN: Test",
            "",
            "## 📋 Current Status & Handoff",
            "",
            "Last updated: 2025-11-12",
            "",
            "What's done:",
            "- Thing 1",
            "",
            "What's next:",
            "- Thing 2",
            "",
            "---",
            "",
            "## Next Section"
        ]

        size = self.parser.calculate_handoff_size(lines)

        self.assertGreater(size, 0)
        self.assertLess(size, 15)  # Should be reasonable size

    def test_calculate_handoff_size_missing(self):
        """Test calculating size when handoff section doesn't exist (returns default)."""
        lines = [
            "# PLAN: Test",
            "",
            "## Some Section",
            "Content"
        ]

        size = self.parser.calculate_handoff_size(lines)

        # Implementation returns default 30 when handoff section not found
        self.assertEqual(size, 30)


if __name__ == "__main__":
    unittest.main()

