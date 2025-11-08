"""Unit tests for validate_plan_compliance.py - PLAN compliance validation."""

import unittest
import sys
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from LLM.scripts.validation.validate_plan_compliance import (
    find_plan_files,
    extract_sections,
    check_naming_compliance,
    calculate_compliance_score,
    generate_report,
)


class TestFindPlanFiles(unittest.TestCase):
    """Test find_plan_files function."""

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

    def test_find_plan_files(self):
        """Test finding PLAN files in root."""
        Path("PLAN_TEST.md").write_text("# PLAN: Test\n")
        Path("PLAN_OTHER.md").write_text("# PLAN: Other\n")

        result = find_plan_files(Path("."))
        self.assertEqual(len(result), 2)
        self.assertTrue(any(f.name == "PLAN_TEST.md" for f in result))
        self.assertTrue(any(f.name == "PLAN_OTHER.md" for f in result))

    def test_find_grammaplan_files(self):
        """Test finding GRAMMAPLAN files."""
        Path("GRAMMAPLAN_TEST.md").write_text("# GRAMMAPLAN: Test\n")
        Path("GRAMMAPLAN_OTHER.md").write_text("# GRAMMAPLAN: Other\n")

        result = find_plan_files(Path("."))
        self.assertEqual(len(result), 2)
        self.assertTrue(any(f.name == "GRAMMAPLAN_TEST.md" for f in result))
        self.assertTrue(any(f.name == "GRAMMAPLAN_OTHER.md" for f in result))

    def test_find_both_types(self):
        """Test finding both PLAN and GRAMMAPLAN files."""
        Path("PLAN_TEST.md").write_text("# PLAN: Test\n")
        Path("GRAMMAPLAN_TEST.md").write_text("# GRAMMAPLAN: Test\n")

        result = find_plan_files(Path("."))
        self.assertEqual(len(result), 2)

    def test_find_no_files(self):
        """Test finding with no files."""
        result = find_plan_files(Path("."))
        self.assertEqual(len(result), 0)

    def test_find_sorted(self):
        """Test that results are sorted."""
        Path("PLAN_B.md").write_text("# PLAN: B\n")
        Path("PLAN_A.md").write_text("# PLAN: A\n")
        Path("PLAN_C.md").write_text("# PLAN: C\n")

        result = find_plan_files(Path("."))
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].name, "PLAN_A.md")
        self.assertEqual(result[1].name, "PLAN_B.md")
        self.assertEqual(result[2].name, "PLAN_C.md")


class TestExtractSections(unittest.TestCase):
    """Test extract_sections function."""

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

    def test_extract_sections(self):
        """Test extracting sections from file."""
        content = """# PLAN: Test

## Context for LLM Execution
Some content

## Goal
Some goal

## Problem Statement
Some problem
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(content)

        result = extract_sections(plan_path)
        self.assertEqual(len(result), 3)
        self.assertIn("Context for LLM Execution", result)
        self.assertIn("Goal", result)
        self.assertIn("Problem Statement", result)

    def test_extract_sections_with_emojis(self):
        """Test extracting sections with emojis."""
        content = """# PLAN: Test

## 📋 Context for LLM Execution
Some content

## 🎯 Goal
Some goal
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(content)

        result = extract_sections(plan_path)
        self.assertEqual(len(result), 2)
        # Emojis should be removed
        self.assertIn("Context for LLM Execution", result)
        self.assertIn("Goal", result)

    def test_extract_sections_missing_file(self):
        """Test extracting sections from missing file."""
        plan_path = Path("PLAN_NONEXISTENT.md")

        result = extract_sections(plan_path)
        self.assertEqual(result, [])

    def test_extract_sections_empty_file(self):
        """Test extracting sections from empty file."""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text("")

        result = extract_sections(plan_path)
        self.assertEqual(result, [])

    def test_extract_sections_no_sections(self):
        """Test extracting sections from file with no sections."""
        content = """# PLAN: Test

Some content without sections.
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(content)

        result = extract_sections(plan_path)
        self.assertEqual(result, [])

    def test_extract_sections_extra_markers(self):
        """Test extracting sections with extra markers."""
        content = """# PLAN: Test

## 🔄 Subplan Tracking
Some content

## ✅ Current Status & Handoff
Some status
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(content)

        result = extract_sections(plan_path)
        self.assertEqual(len(result), 2)
        # Extra markers should be removed
        self.assertIn("Subplan Tracking", result)
        self.assertIn("Current Status & Handoff", result)


class TestCheckNamingCompliance(unittest.TestCase):
    """Test check_naming_compliance function."""

    def test_valid_plan_name(self):
        """Test valid PLAN name."""
        plan_path = Path("PLAN_TEST.md")
        pass_check, message = check_naming_compliance(plan_path)
        self.assertTrue(pass_check)
        self.assertIn("Valid PLAN name", message)

    def test_valid_plan_name_with_hyphens(self):
        """Test valid PLAN name with hyphens."""
        plan_path = Path("PLAN_TEST-FEATURE.md")
        pass_check, message = check_naming_compliance(plan_path)
        self.assertTrue(pass_check)
        self.assertIn("Valid PLAN name", message)

    def test_valid_plan_name_with_numbers(self):
        """Test valid PLAN name with numbers."""
        plan_path = Path("PLAN_TEST123.md")
        pass_check, message = check_naming_compliance(plan_path)
        self.assertTrue(pass_check)
        self.assertIn("Valid PLAN name", message)

    def test_valid_grammaplan_name(self):
        """Test valid GRAMMAPLAN name."""
        plan_path = Path("GRAMMAPLAN_TEST.md")
        pass_check, message = check_naming_compliance(plan_path)
        self.assertTrue(pass_check)
        self.assertIn("Valid GRAMMAPLAN name", message)

    def test_invalid_name_format(self):
        """Test invalid name format."""
        plan_path = Path("INVALID_NAME.md")
        pass_check, message = check_naming_compliance(plan_path)
        self.assertFalse(pass_check)
        self.assertIn("Invalid name format", message)

    def test_invalid_name_lowercase(self):
        """Test invalid name with lowercase."""
        plan_path = Path("plan_test.md")
        pass_check, message = check_naming_compliance(plan_path)
        self.assertFalse(pass_check)
        self.assertIn("Invalid name format", message)

    def test_invalid_name_wrong_extension(self):
        """Test invalid name with wrong extension."""
        plan_path = Path("PLAN_TEST.txt")
        pass_check, message = check_naming_compliance(plan_path)
        self.assertFalse(pass_check)
        self.assertIn("Invalid name format", message)

    def test_invalid_name_special_characters(self):
        """Test invalid name with special characters."""
        plan_path = Path("PLAN_TEST@FEATURE.md")
        pass_check, message = check_naming_compliance(plan_path)
        self.assertFalse(pass_check)
        self.assertIn("Invalid name format", message)


class TestCalculateComplianceScore(unittest.TestCase):
    """Test calculate_compliance_score function."""

    def test_all_required_sections(self):
        """Test with all required sections."""
        sections = [
            "Context for LLM Execution",
            "Goal",
            "Problem Statement",
            "Success Criteria",
            "Scope Definition",
            "Desirable Achievements",
            "Subplan Tracking",
            "Current Status & Handoff",
            "Related Plans",  # Required for full score
        ]
        plan_path = Path("PLAN_TEST.md")

        result = calculate_compliance_score(plan_path, sections)
        # 40 (template) + 20 (naming) + 10 (related plans) + 10 (subplan tracking) = 80
        self.assertEqual(result["score"], 80)
        self.assertEqual(len(result["issues"]), 0)

    def test_missing_required_sections(self):
        """Test with missing required sections."""
        sections = [
            "Context for LLM Execution",
            "Goal",
            # Missing Problem Statement, Success Criteria, etc.
        ]
        plan_path = Path("PLAN_TEST.md")

        result = calculate_compliance_score(plan_path, sections)
        self.assertLess(result["score"], 100)
        self.assertGreater(len(result["issues"]), 0)

    def test_with_v14_features(self):
        """Test with v1.4 features (bonus points)."""
        sections = [
            "Context for LLM Execution",
            "Goal",
            "Problem Statement",
            "Success Criteria",
            "Scope Definition",
            "Desirable Achievements",
            "Subplan Tracking",
            "Current Status & Handoff",
            "Related Plans",  # Required for full score
            "GrammaPlan Consideration",
            "Summary Statistics",
            "Key Learnings",
            "Pre-Completion Review",
        ]
        plan_path = Path("PLAN_TEST.md")

        result = calculate_compliance_score(plan_path, sections)
        # 40 (template) + 20 (v1.4 bonus) + 20 (naming) + 10 (related plans) + 10 (subplan tracking) = 100
        self.assertEqual(result["score"], 100)  # Capped at 100
        self.assertGreater(result["v14_bonus"], 0)

    def test_missing_naming_compliance(self):
        """Test with missing naming compliance."""
        sections = [
            "Context for LLM Execution",
            "Goal",
            "Problem Statement",
            "Success Criteria",
            "Scope Definition",
            "Desirable Achievements",
            "Subplan Tracking",
            "Current Status & Handoff",
        ]
        plan_path = Path("INVALID_NAME.md")

        result = calculate_compliance_score(plan_path, sections)
        self.assertLess(result["score"], 100)
        self.assertIn("Invalid name format", str(result["issues"]))

    def test_missing_related_plans(self):
        """Test with missing Related Plans section."""
        sections = [
            "Context for LLM Execution",
            "Goal",
            "Problem Statement",
            "Success Criteria",
            "Scope Definition",
            "Desirable Achievements",
            "Subplan Tracking",
            "Current Status & Handoff",
        ]
        plan_path = Path("PLAN_TEST.md")

        result = calculate_compliance_score(plan_path, sections)
        # Should have -10 points for missing Related Plans
        self.assertLess(result["score"], 100)
        self.assertIn("Missing 'Related Plans' section", str(result["issues"]))

    def test_missing_subplan_tracking(self):
        """Test with missing Subplan Tracking section."""
        sections = [
            "Context for LLM Execution",
            "Goal",
            "Problem Statement",
            "Success Criteria",
            "Scope Definition",
            "Desirable Achievements",
            # Missing Subplan Tracking
            "Current Status & Handoff",
        ]
        plan_path = Path("PLAN_TEST.md")

        result = calculate_compliance_score(plan_path, sections)
        self.assertLess(result["score"], 100)
        self.assertIn("Missing 'Subplan Tracking' section", str(result["issues"]))

    def test_score_capped_at_100(self):
        """Test that score is capped at 100."""
        sections = [
            "Context for LLM Execution",
            "Goal",
            "Problem Statement",
            "Success Criteria",
            "Scope Definition",
            "Desirable Achievements",
            "Subplan Tracking",
            "Current Status & Handoff",
            "Related Plans",
            "GrammaPlan Consideration",
            "Summary Statistics",
            "Key Learnings",
            "Pre-Completion Review",
        ]
        plan_path = Path("PLAN_TEST.md")

        result = calculate_compliance_score(plan_path, sections)
        self.assertEqual(result["score"], 100)
        self.assertLessEqual(result["score"], result["max_score"])


class TestGenerateReport(unittest.TestCase):
    """Test generate_report function."""

    def test_human_readable_report(self):
        """Test human-readable report generation."""
        results = [
            {
                "file": "PLAN_TEST.md",
                "data": {
                    "score": 90,
                    "max_score": 100,
                    "issues": [],
                    "successes": ["✓ Has 'Goal' section"],
                    "template_score": 40,
                    "v14_bonus": 20,
                    "sections_found": ["Goal"],
                },
            }
        ]

        report = generate_report(results, output_json=False)
        self.assertIn("PLAN COMPLIANCE VALIDATION REPORT", report)
        self.assertIn("PLAN_TEST.md", report)
        self.assertIn("90/100", report)

    def test_json_report(self):
        """Test JSON report generation."""
        results = [
            {
                "file": "PLAN_TEST.md",
                "data": {
                    "score": 90,
                    "max_score": 100,
                    "issues": [],
                    "successes": ["✓ Has 'Goal' section"],
                    "template_score": 40,
                    "v14_bonus": 20,
                    "sections_found": ["Goal"],
                },
            }
        ]

        report = generate_report(results, output_json=True)
        parsed = json.loads(report)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["file"], "PLAN_TEST.md")
        self.assertEqual(parsed[0]["data"]["score"], 90)

    def test_multiple_plans(self):
        """Test report with multiple PLANs."""
        results = [
            {
                "file": "PLAN_TEST.md",
                "data": {
                    "score": 90,
                    "max_score": 100,
                    "issues": [],
                    "successes": [],
                    "template_score": 40,
                    "v14_bonus": 0,
                    "sections_found": [],
                },
            },
            {
                "file": "PLAN_OTHER.md",
                "data": {
                    "score": 75,
                    "max_score": 100,
                    "issues": ["✗ Missing 'Goal' section"],
                    "successes": [],
                    "template_score": 30,
                    "v14_bonus": 0,
                    "sections_found": [],
                },
            },
        ]

        report = generate_report(results, output_json=False)
        self.assertIn("PLAN_TEST.md", report)
        self.assertIn("PLAN_OTHER.md", report)
        self.assertIn("PLANs Reviewed: 2", report)

    def test_empty_results(self):
        """Test report with empty results."""
        results = []

        report = generate_report(results, output_json=False)
        self.assertIn("PLAN COMPLIANCE VALIDATION REPORT", report)
        self.assertIn("PLANs Reviewed: 0", report)

    def test_color_coding(self):
        """Test color coding in report."""
        results = [
            {
                "file": "PLAN_EXCELLENT.md",
                "data": {
                    "score": 95,
                    "max_score": 100,
                    "issues": [],
                    "successes": [],
                    "template_score": 40,
                    "v14_bonus": 0,
                    "sections_found": [],
                },
            },
            {
                "file": "PLAN_GOOD.md",
                "data": {
                    "score": 80,
                    "max_score": 100,
                    "issues": [],
                    "successes": [],
                    "template_score": 40,
                    "v14_bonus": 0,
                    "sections_found": [],
                },
            },
            {
                "file": "PLAN_POOR.md",
                "data": {
                    "score": 50,
                    "max_score": 100,
                    "issues": ["✗ Missing 'Goal' section"],
                    "successes": [],
                    "template_score": 20,
                    "v14_bonus": 0,
                    "sections_found": [],
                },
            },
        ]

        report = generate_report(results, output_json=False)
        # Check that report contains color codes (ANSI escape sequences)
        self.assertIn("\033[", report)  # ANSI color codes


class TestIntegration(unittest.TestCase):
    """Integration tests with real PLAN structures."""

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

    def test_complete_compliant_plan(self):
        """Test with complete compliant PLAN."""
        content = """# PLAN: Test Feature

## Context for LLM Execution
Some context

## Goal
Some goal

## Problem Statement
Some problem

## Success Criteria
Some criteria

## Scope Definition
Some scope

## Desirable Achievements
Some achievements

## Subplan Tracking
Some tracking

## Current Status & Handoff
Some status

## Related Plans
Some related plans
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(content)

        sections = extract_sections(plan_path)
        result = calculate_compliance_score(plan_path, sections)

        self.assertGreaterEqual(result["score"], 75)
        self.assertEqual(len(result["issues"]), 0)

    def test_non_compliant_plan(self):
        """Test with non-compliant PLAN."""
        content = """# PLAN: Test Feature

## Goal
Some goal
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(content)

        sections = extract_sections(plan_path)
        result = calculate_compliance_score(plan_path, sections)

        self.assertLess(result["score"], 75)
        self.assertGreater(len(result["issues"]), 0)

    def test_grammaplan(self):
        """Test with GRAMMAPLAN."""
        content = """# GRAMMAPLAN: Test Feature

## Context for LLM Execution
Some context

## Goal
Some goal
"""
        plan_path = Path("GRAMMAPLAN_TEST.md")
        plan_path.write_text(content)

        sections = extract_sections(plan_path)
        result = calculate_compliance_score(plan_path, sections)

        # GRAMMAPLAN should pass naming compliance
        pass_check, _ = check_naming_compliance(plan_path)
        self.assertTrue(pass_check)

    def test_cli_single_file(self):
        """Test CLI with single file (simulated)."""
        # This tests the main() function indirectly through component functions
        content = """# PLAN: Test Feature

## Context for LLM Execution
Some context

## Goal
Some goal

## Problem Statement
Some problem

## Success Criteria
Some criteria

## Scope Definition
Some scope

## Desirable Achievements
Some achievements

## Subplan Tracking
Some tracking

## Current Status & Handoff
Some status

## Related Plans
Some related plans
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(content)

        sections = extract_sections(plan_path)
        result = calculate_compliance_score(plan_path, sections)

        self.assertGreaterEqual(result["score"], 75)


if __name__ == "__main__":
    unittest.main()

