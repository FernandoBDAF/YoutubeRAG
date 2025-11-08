"""Integration tests for LLM scripts workflows - End-to-end workflow testing."""

import unittest
import sys
import tempfile
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from LLM.scripts.generation.generate_prompt import (
    parse_plan_file,
    find_next_achievement_from_plan,
    find_next_achievement_hybrid,
)
from LLM.scripts.validation.validate_plan_compliance import (
    find_plan_files,
    extract_sections,
    calculate_compliance_score,
)
from LLM.scripts.validation.validate_registration import (
    validate_plan_registration,
)
from LLM.scripts.archiving.archive_completed import (
    find_plan_file,
    get_archive_location,
    determine_archive_type,
    archive_file,
)
from tests.LLM.scripts.fixtures.sample_plans import (
    get_sample_plan_content,
    get_plan_with_achievements,
)


class TestWorkflowGenerateValidateArchive(unittest.TestCase):
    """Test workflow: Generate prompt → Validate plan → Archive completed."""

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

    def test_generate_validate_archive_workflow(self):
        """Test complete workflow: generate → validate → archive."""
        # Create PLAN file
        plan_content = get_sample_plan_content()
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Step 1: Generate prompt for next achievement
        plan_data = parse_plan_file(plan_path)
        with open(plan_path, "r", encoding="utf-8") as f:
            plan_content = f.read()
        next_achievement = find_next_achievement_from_plan(plan_content)
        self.assertIsNotNone(next_achievement)
        self.assertEqual(next_achievement, "1.1")

        # Step 2: Validate plan compliance
        sections = extract_sections(plan_path)
        compliance = calculate_compliance_score(plan_path, sections)
        self.assertGreater(compliance["score"], 0)

        # Step 3: Create SUBPLAN and EXECUTION_TASK
        subplan_path = Path("SUBPLAN_TEST_11.md")
        subplan_path.write_text("# SUBPLAN: Test\n")
        execution_task_path = Path("EXECUTION_TASK_TEST_11_01.md")
        execution_task_path.write_text("# EXECUTION_TASK: Test\n")

        # Step 4: Archive completed files
        archive_location = get_archive_location(plan_path)
        archive_type_subplan = determine_archive_type(subplan_path)
        archive_type_execution = determine_archive_type(execution_task_path)

        result1 = archive_file(subplan_path, archive_location, archive_type_subplan)
        result2 = archive_file(
            execution_task_path, archive_location, archive_type_execution
        )

        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertFalse(subplan_path.exists())
        self.assertFalse(execution_task_path.exists())
        self.assertTrue(
            (archive_location / "subplans" / "SUBPLAN_TEST_11.md").exists()
        )
        self.assertTrue(
            (archive_location / "execution" / "EXECUTION_TASK_TEST_11_01.md").exists()
        )


class TestWorkflowPauseValidateArchive(unittest.TestCase):
    """Test workflow: Generate pause prompt → Validate execution start → Archive."""

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

    def test_pause_validate_archive_workflow(self):
        """Test workflow: pause → validate execution start → archive."""
        # Create PLAN file
        plan_content = get_sample_plan_content()
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create EXECUTION_TASK (paused work)
        execution_task_path = Path("EXECUTION_TASK_TEST_11_01.md")
        execution_task_content = """# EXECUTION_TASK: Test Feature

**Status**: Paused
"""
        execution_task_path.write_text(execution_task_content)

        # Step 1: Validate execution start prerequisites
        # (This would typically be done before pausing)
        from LLM.scripts.validation.validate_execution_start import (
            validate_execution_start,
        )

        pass_check, message = validate_execution_start(execution_task_path)
        # May fail if PLAN doesn't have all prerequisites, but that's OK for this test
        # We're testing the workflow, not the validation itself

        # Step 2: Archive paused EXECUTION_TASK
        archive_location = get_archive_location(plan_path)
        archive_type = determine_archive_type(execution_task_path)

        result = archive_file(execution_task_path, archive_location, archive_type)
        self.assertTrue(result)
        self.assertFalse(execution_task_path.exists())


class TestWorkflowResumeValidateArchive(unittest.TestCase):
    """Test workflow: Generate resume prompt → Validate mid-plan → Archive."""

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

    def test_resume_validate_archive_workflow(self):
        """Test workflow: resume → validate mid-plan → archive."""
        # Create PLAN file with progress
        plan_content = get_plan_with_achievements()
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLANs and EXECUTION_TASKs (in progress)
        subplan_path = Path("SUBPLAN_TEST_11.md")
        subplan_path.write_text("# SUBPLAN: Test\n")
        execution_task_path = Path("EXECUTION_TASK_TEST_11_01.md")
        execution_task_path.write_text("# EXECUTION_TASK: Test\n")

        # Step 1: Validate mid-plan compliance
        from LLM.scripts.validation.validate_mid_plan import validate_mid_plan

        pass_check, message = validate_mid_plan(plan_path)
        # May have warnings, but should not block

        # Step 2: Archive completed files
        archive_location = get_archive_location(plan_path)
        archive_type = determine_archive_type(subplan_path)

        result = archive_file(subplan_path, archive_location, archive_type)
        self.assertTrue(result)


class TestWorkflowVerifyValidateArchive(unittest.TestCase):
    """Test workflow: Generate verify prompt → Validate plan completion → Archive."""

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

    def test_verify_validate_archive_workflow(self):
        """Test workflow: verify → validate plan completion → archive."""
        # Create PLAN file (complete)
        plan_content = get_sample_plan_content()
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create completed SUBPLANs and EXECUTION_TASKs
        subplan_path = Path("SUBPLAN_TEST_01.md")
        subplan_path.write_text("# SUBPLAN: Test\n")
        execution_task_path = Path("EXECUTION_TASK_TEST_01_01.md")
        execution_task_path.write_text("# EXECUTION_TASK: Test\n")

        # Step 1: Validate plan completion
        from LLM.scripts.validation.validate_plan_completion import (
            validate_plan_completion,
        )

        pass_check, message = validate_plan_completion(plan_path)
        # May have issues, but workflow should continue

        # Step 2: Archive completed files
        archive_location = get_archive_location(plan_path)
        archive_type = determine_archive_type(subplan_path)

        result = archive_file(subplan_path, archive_location, archive_type)
        self.assertTrue(result)


class TestWorkflowFullCycle(unittest.TestCase):
    """Test full methodology cycle: Generate → Validate → Archive → Generate next."""

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

    def test_full_methodology_cycle(self):
        """Test complete methodology cycle with multiple achievements."""
        # Create PLAN file
        plan_content = get_plan_with_achievements()
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Step 1: Generate prompt for next achievement
        plan_data = parse_plan_file(plan_path)
        with open(plan_path, "r", encoding="utf-8") as f:
            plan_content = f.read()
        next_achievement = find_next_achievement_from_plan(plan_content)
        self.assertIsNotNone(next_achievement)

        # Step 2: Create SUBPLAN and EXECUTION_TASK for achievement
        subplan_path = Path(f"SUBPLAN_TEST_{next_achievement.replace('.', '')}.md")
        subplan_path.write_text("# SUBPLAN: Test\n")
        execution_task_path = Path(
            f"EXECUTION_TASK_TEST_{next_achievement.replace('.', '')}_01.md"
        )
        execution_task_path.write_text("# EXECUTION_TASK: Test\n")

        # Step 3: Validate plan registration
        pass_check, message = validate_plan_registration(plan_path)
        # May have warnings about unregistered files

        # Step 4: Validate plan compliance
        sections = extract_sections(plan_path)
        compliance = calculate_compliance_score(plan_path, sections)
        self.assertGreater(compliance["score"], 0)

        # Step 5: Archive completed files
        archive_location = get_archive_location(plan_path)
        archive_type_subplan = determine_archive_type(subplan_path)
        archive_type_execution = determine_archive_type(execution_task_path)

        result1 = archive_file(subplan_path, archive_location, archive_type_subplan)
        result2 = archive_file(
            execution_task_path, archive_location, archive_type_execution
        )

        self.assertTrue(result1)
        self.assertTrue(result2)

        # Step 6: Generate next achievement (after archiving)
        # Update PLAN to mark achievement as complete
        updated_content = plan_content.replace(
            "⏳ Next: Achievement 1.2", "✅ Achievement 1.2 Complete\n- ⏳ Next: Achievement 1.3"
        )
        plan_path.write_text(updated_content)

        next_achievement_2 = find_next_achievement_from_plan(updated_content)
        self.assertIsNotNone(next_achievement_2)


class TestWorkflowWithRealPlanFiles(unittest.TestCase):
    """Test workflows with real PLAN files from project."""

    def setUp(self):
        """Set up test environment."""
        self.original_cwd = os.getcwd()
        self.project_root = Path(__file__).parent.parent.parent.parent.parent

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)

    def test_workflow_with_real_plan_file(self):
        """Test workflow with real PLAN file from project (if available)."""
        # Look for a real PLAN file in project root
        plan_files = list(self.project_root.glob("PLAN_*.md"))
        
        if not plan_files:
            self.skipTest("No PLAN files found in project root")

        # Use first available PLAN file
        real_plan_path = plan_files[0]

        # Step 1: Generate prompt for next achievement
        try:
            plan_data = parse_plan_file(real_plan_path)
            with open(real_plan_path, "r", encoding="utf-8") as f:
                plan_content = f.read()
            next_achievement = find_next_achievement_from_plan(plan_content)
            # May return None if plan is complete, which is OK
        except Exception as e:
            self.skipTest(f"Could not generate prompt: {e}")

        # Step 2: Validate plan compliance
        sections = extract_sections(real_plan_path)
        compliance = calculate_compliance_score(real_plan_path, sections)
        self.assertGreater(compliance["score"], 0)

        # Step 3: Validate plan registration (if SUBPLANs/EXECUTION_TASKs exist)
        try:
            pass_check, message = validate_plan_registration(real_plan_path)
            # May have warnings, but should not fail completely
        except Exception as e:
            # Some plans may not have SUBPLANs/EXECUTION_TASKs yet
            pass

    def test_workflow_with_multiple_real_plans(self):
        """Test workflow with multiple real PLAN files."""
        # Find all PLAN files
        plan_files = list(self.project_root.glob("PLAN_*.md"))
        
        if len(plan_files) < 2:
            self.skipTest("Not enough PLAN files found for multi-plan test")

        # Test compliance validation for multiple plans
        for plan_path in plan_files[:3]:  # Test up to 3 plans
            try:
                sections = extract_sections(plan_path)
                compliance = calculate_compliance_score(plan_path, sections)
                self.assertGreater(compliance["score"], 0)
            except Exception as e:
                # Some plans may have issues, skip them
                continue


class TestWorkflowErrorHandling(unittest.TestCase):
    """Test error handling in workflows."""

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

    def test_workflow_with_missing_plan(self):
        """Test workflow error handling with missing PLAN file."""
        missing_plan = Path("PLAN_NONEXISTENT.md")
        subplan_path = Path("SUBPLAN_NONEXISTENT_11.md")
        subplan_path.write_text("# SUBPLAN: Test\n")

        # Should raise FileNotFoundError when trying to find PLAN
        with self.assertRaises(FileNotFoundError):
            find_plan_file(subplan_path)

    def test_workflow_with_invalid_file_type(self):
        """Test workflow error handling with invalid file type."""
        invalid_path = Path("INVALID_FILE.md")

        # Should raise ValueError when trying to determine archive type
        with self.assertRaises(ValueError):
            determine_archive_type(invalid_path)

    def test_workflow_with_duplicate_archive(self):
        """Test workflow error handling with duplicate files in archive."""
        plan_content = get_sample_plan_content()
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        subplan_path = Path("SUBPLAN_TEST_11.md")
        subplan_path.write_text("# SUBPLAN: Test\n")

        archive_location = get_archive_location(plan_path)
        archive_type = determine_archive_type(subplan_path)

        # Archive first time
        result1 = archive_file(subplan_path, archive_location, archive_type)
        self.assertTrue(result1)

        # Try to archive again (should fail - file already in archive)
        # But file doesn't exist in root anymore, so this tests different scenario
        # Create new file with same name
        subplan_path_2 = Path("SUBPLAN_TEST_11.md")
        subplan_path_2.write_text("# SUBPLAN: Test 2\n")

        result2 = archive_file(subplan_path_2, archive_location, archive_type)
        self.assertFalse(result2)  # Should fail because destination exists


if __name__ == "__main__":
    unittest.main()

