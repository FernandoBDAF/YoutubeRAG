#!/usr/bin/env python3
"""
Test Suite for PromptBuilder Module

Tests the prompt template management and formatting functionality
extracted in Achievement 2.3.

Test Coverage:
- Template structure and placeholders
- build_achievement_prompt() with various contexts
- format_validation_scripts() with and without scripts
- build_completion_message() formatting
- Edge cases and error handling

Created: 2025-11-12
Achievement: 2.3 - Extract Prompt Generation Module
"""
import sys
import unittest
from pathlib import Path
from typing import Dict, List

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from LLM.scripts.generation.prompt_builder import PromptBuilder


class TestPromptBuilderInit(unittest.TestCase):
    """Test PromptBuilder initialization."""

    def test_init_creates_instance(self):
        """Test that PromptBuilder can be instantiated."""
        builder = PromptBuilder()
        self.assertIsNotNone(builder)

    def test_template_exists(self):
        """Test that ACHIEVEMENT_EXECUTION_TEMPLATE is defined."""
        builder = PromptBuilder()
        self.assertTrue(hasattr(builder, "ACHIEVEMENT_EXECUTION_TEMPLATE"))
        self.assertIsInstance(builder.ACHIEVEMENT_EXECUTION_TEMPLATE, str)
        self.assertGreater(len(builder.ACHIEVEMENT_EXECUTION_TEMPLATE), 100)


class TestAchievementExecutionTemplate(unittest.TestCase):
    """Test the ACHIEVEMENT_EXECUTION_TEMPLATE content and structure."""

    def setUp(self):
        self.builder = PromptBuilder()
        self.template = self.builder.ACHIEVEMENT_EXECUTION_TEMPLATE

    def test_template_has_required_placeholders(self):
        """Test that template contains all required placeholder variables."""
        required_placeholders = [
            "{achievement_num}",
            "{feature}",
            "{achievement_title}",
            "{achievement_goal}",
            "{estimated_hours}",
            "{achievement_lines}",
            "{handoff_lines}",
            "{plan_total_lines}",
            "{context_budget}",
            "{subplan_num}",
            "{archive_location}",
            "{validation_scripts}",
            "{project_context}",
        ]

        for placeholder in required_placeholders:
            with self.subTest(placeholder=placeholder):
                self.assertIn(
                    placeholder,
                    self.template,
                    f"Template missing required placeholder: {placeholder}",
                )

    def test_template_has_context_boundaries_section(self):
        """Test that template includes CONTEXT BOUNDARIES section."""
        self.assertIn("CONTEXT BOUNDARIES", self.template)
        self.assertIn("Read ONLY These", self.template)
        self.assertIn("CONTEXT BUDGET", self.template)

    def test_template_has_required_steps_section(self):
        """Test that template includes REQUIRED STEPS section."""
        self.assertIn("REQUIRED STEPS", self.template)
        self.assertIn("Step 1: Create SUBPLAN", self.template)
        self.assertIn("Step 2: Create EXECUTION_TASK", self.template)

    def test_template_has_validation_section(self):
        """Test that template includes VALIDATION ENFORCEMENT section."""
        self.assertIn("VALIDATION ENFORCEMENT", self.template)

    def test_template_has_do_not_section(self):
        """Test that template includes DO NOT section."""
        self.assertIn("DO NOT:", self.template)
        self.assertIn("Skip SUBPLAN", self.template)
        self.assertIn("Skip EXECUTION_TASK", self.template)

    def test_template_has_remember_section(self):
        """Test that template includes REMEMBER section."""
        self.assertIn("REMEMBER:", self.template)
        self.assertIn("SUBPLAN + EXECUTION_TASK", self.template)


class TestFormatValidationScripts(unittest.TestCase):
    """Test the format_validation_scripts() method."""

    def setUp(self):
        self.builder = PromptBuilder()

    def test_format_with_single_script(self):
        """Test formatting with a single validation script."""
        scripts = ["validate_plan.py"]
        result = self.builder.format_validation_scripts(scripts)

        self.assertIn("After Step 4, these scripts will run:", result)
        self.assertIn("✓ validate_plan.py", result)
        self.assertIn("BLOCKS with error", result)

    def test_format_with_multiple_scripts(self):
        """Test formatting with multiple validation scripts."""
        scripts = ["validate_plan.py", "check_files.py", "lint_code.py"]
        result = self.builder.format_validation_scripts(scripts)

        self.assertIn("After Step 4, these scripts will run:", result)
        self.assertIn("✓ validate_plan.py", result)
        self.assertIn("✓ check_files.py", result)
        self.assertIn("✓ lint_code.py", result)
        self.assertIn("BLOCKS with error", result)

    def test_format_with_empty_list(self):
        """Test formatting with no validation scripts."""
        scripts = []
        result = self.builder.format_validation_scripts(scripts)

        self.assertIn("being built", result)
        self.assertNotIn("BLOCKS", result)

    def test_format_returns_string(self):
        """Test that method always returns a string."""
        for scripts in [[], ["script.py"], ["s1.py", "s2.py"]]:
            with self.subTest(scripts=scripts):
                result = self.builder.format_validation_scripts(scripts)
                self.assertIsInstance(result, str)


class TestBuildAchievementPrompt(unittest.TestCase):
    """Test the build_achievement_prompt() method."""

    def setUp(self):
        self.builder = PromptBuilder()
        self.base_context = {
            "feature_name": "TEST_FEATURE",
            "achievement_num": "1.2",
            "achievement_title": "Implement Test Feature",
            "achievement_lines": 45,
            "handoff_lines": 12,
            "plan_total_lines": 500,
            "context_budget": 57,
            "subplan_num": "12",
            "archive_location": "work-space/plans/TEST_FEATURE/",
        }

    def test_build_with_minimal_context(self):
        """Test building prompt with minimal required context."""
        prompt = self.builder.build_achievement_prompt(self.base_context, [])

        # Verify key values are present
        self.assertIn("Achievement 1.2", prompt)
        self.assertIn("TEST_FEATURE", prompt)
        self.assertIn("Implement Test Feature", prompt)
        self.assertIn("45 lines", prompt)
        self.assertIn("57 lines maximum", prompt)

    def test_build_with_full_context(self):
        """Test building prompt with all context fields."""
        full_context = {
            **self.base_context,
            "achievement_goal": "Create comprehensive test suite",
            "estimated_hours": "2-3 hours",
            "project_context": "# PROJECT CONTEXT\nSome context here\n",
        }

        prompt = self.builder.build_achievement_prompt(full_context, [])

        self.assertIn("Create comprehensive test suite", prompt)
        self.assertIn("2-3 hours", prompt)
        self.assertIn("# PROJECT CONTEXT", prompt)

    def test_build_with_validation_scripts(self):
        """Test building prompt with validation scripts."""
        scripts = ["validate_test.py", "check_coverage.py"]
        prompt = self.builder.build_achievement_prompt(self.base_context, scripts)

        self.assertIn("validate_test.py", prompt)
        self.assertIn("check_coverage.py", prompt)
        self.assertIn("BLOCKS with error", prompt)

    def test_build_uses_default_values(self):
        """Test that missing optional fields use default values."""
        prompt = self.builder.build_achievement_prompt(self.base_context, [])

        # Should use default values
        self.assertIn("See PLAN for details", prompt)
        self.assertIn("See PLAN", prompt)

    def test_build_returns_string(self):
        """Test that method returns a string."""
        prompt = self.builder.build_achievement_prompt(self.base_context, [])
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 500)  # Should be substantial prompt

    def test_build_preserves_template_structure(self):
        """Test that built prompt maintains template structure."""
        prompt = self.builder.build_achievement_prompt(self.base_context, [])

        # Check for key sections
        self.assertIn("CONTEXT BOUNDARIES", prompt)
        self.assertIn("REQUIRED STEPS", prompt)
        self.assertIn("VALIDATION ENFORCEMENT", prompt)
        self.assertIn("DO NOT:", prompt)
        self.assertIn("REMEMBER:", prompt)

    def test_build_with_different_achievement_numbers(self):
        """Test building prompts for different achievement numbers."""
        for ach_num in ["1.1", "2.3", "10.5"]:
            with self.subTest(achievement_num=ach_num):
                context = {
                    **self.base_context,
                    "achievement_num": ach_num,
                    "subplan_num": ach_num.replace(".", ""),
                }
                prompt = self.builder.build_achievement_prompt(context, [])

                self.assertIn(f"Achievement {ach_num}", prompt)
                self.assertIn(f"SUBPLAN_TEST_FEATURE_{ach_num.replace('.', '')}", prompt)


class TestBuildCompletionMessage(unittest.TestCase):
    """Test the build_completion_message() method."""

    def setUp(self):
        self.builder = PromptBuilder()

    def test_build_completion_message_basic(self):
        """Test building basic completion message."""
        feature_name = "TEST_FEATURE"
        plan_path = Path("work-space/plans/TEST_FEATURE/PLAN_TEST_FEATURE.md")
        archive_location = "work-space/plans/TEST_FEATURE/"

        message = self.builder.build_completion_message(feature_name, plan_path, archive_location)

        self.assertIn("PLAN COMPLETE", message)
        self.assertIn("TEST_FEATURE", message)
        self.assertIn("END_POINT protocol", message)

    def test_completion_message_has_next_steps(self):
        """Test that completion message includes next steps."""
        message = self.builder.build_completion_message(
            "FEATURE", Path("work-space/plans/FEATURE/PLAN_FEATURE.md"), "work-space/plans/FEATURE/"
        )

        self.assertIn("Next Steps", message)
        self.assertIn("Review the PLAN", message)
        self.assertIn("Archive the PLAN", message)
        self.assertIn("Update ACTIVE_PLANS.md", message)

    def test_completion_message_has_verification_info(self):
        """Test that completion message includes verification command."""
        plan_path = Path("work-space/plans/FEATURE/PLAN_FEATURE.md")
        message = self.builder.build_completion_message(
            "FEATURE", plan_path, "work-space/plans/FEATURE/"
        )

        self.assertIn("verify completion", message)
        self.assertIn("validate_plan_completion.py", message)
        self.assertIn(plan_path.name, message)

    def test_completion_message_has_archive_location(self):
        """Test that completion message includes archive location."""
        archive_location = "work-space/plans/MY_FEATURE/"
        message = self.builder.build_completion_message(
            "MY_FEATURE", Path("work-space/plans/MY_FEATURE/PLAN_MY_FEATURE.md"), archive_location
        )

        self.assertIn("Archive Location", message)
        self.assertIn(archive_location, message)

    def test_completion_message_returns_string(self):
        """Test that method returns a string."""
        message = self.builder.build_completion_message(
            "FEATURE", Path("PLAN_FEATURE.md"), "archive/"
        )

        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 100)


class TestPromptBuilderIntegration(unittest.TestCase):
    """Integration tests for PromptBuilder."""

    def setUp(self):
        self.builder = PromptBuilder()

    def test_full_workflow_prompt_generation(self):
        """Test complete workflow of generating a prompt."""
        # Prepare context
        context = {
            "feature_name": "INTEGRATION_TEST",
            "achievement_num": "3.1",
            "achievement_title": "Test Integration",
            "achievement_goal": "Verify full workflow",
            "estimated_hours": "1 hour",
            "achievement_lines": 30,
            "handoff_lines": 10,
            "plan_total_lines": 300,
            "context_budget": 40,
            "subplan_num": "31",
            "archive_location": "work-space/plans/INTEGRATION_TEST/",
            "project_context": "# Context\nTest context\n",
        }

        # Prepare validation scripts
        validation_scripts = ["validate_integration.py"]

        # Build prompt
        prompt = self.builder.build_achievement_prompt(context, validation_scripts)

        # Verify comprehensive content
        self.assertIn("Achievement 3.1", prompt)
        self.assertIn("INTEGRATION_TEST", prompt)
        self.assertIn("Test Integration", prompt)
        self.assertIn("Verify full workflow", prompt)
        self.assertIn("1 hour", prompt)
        self.assertIn("40 lines maximum", prompt)
        self.assertIn("validate_integration.py", prompt)
        self.assertIn("# Context", prompt)

    def test_multiple_builder_instances_independent(self):
        """Test that multiple PromptBuilder instances work independently."""
        builder1 = PromptBuilder()
        builder2 = PromptBuilder()

        # Both should work
        scripts1 = builder1.format_validation_scripts(["test1.py"])
        scripts2 = builder2.format_validation_scripts(["test2.py"])

        self.assertIn("test1.py", scripts1)
        self.assertIn("test2.py", scripts2)


if __name__ == "__main__":
    unittest.main()
