"""Unit tests for validate_registration.py - Component registration validation."""

import unittest
import sys
import tempfile
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from LLM.scripts.validation.validate_registration import (
    find_subplans_for_plan,
    find_execution_tasks_for_plan,
    find_execution_tasks_for_subplan,
    get_archive_location,
    extract_registered_subplans,
    extract_registered_execution_tasks_plan,
    extract_registered_execution_tasks_subplan,
    validate_plan_registration,
    validate_subplan_registration,
)


class TestFindSubplansForPlan(unittest.TestCase):
    """Test find_subplans_for_plan function."""

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

    def test_find_subplans_in_root(self):
        """Test finding SUBPLANs in root."""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text("# PLAN: Test\n")

        # Create SUBPLAN files
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")

        result = find_subplans_for_plan(plan_path)
        self.assertEqual(len(result), 2)
        self.assertTrue(any(f.name == "SUBPLAN_TEST_11.md" for f in result))
        self.assertTrue(any(f.name == "SUBPLAN_TEST_22.md" for f in result))

    def test_find_subplans_in_archive(self):
        """Test finding SUBPLANs in archive."""
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Get actual archive location (will be fallback)
        archive_path = get_archive_location(plan_path)
        archive_dir = archive_path / "subplans"
        archive_dir.mkdir(parents=True, exist_ok=True)
        (archive_dir / "SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        (archive_dir / "SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")

        result = find_subplans_for_plan(plan_path)
        self.assertEqual(len(result), 2)

    def test_find_subplans_both_locations(self):
        """Test finding SUBPLANs in both root and archive."""
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLAN in root
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")

        # Get actual archive location (will be fallback)
        archive_path = get_archive_location(plan_path)
        archive_dir = archive_path / "subplans"
        archive_dir.mkdir(parents=True, exist_ok=True)
        (archive_dir / "SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")

        result = find_subplans_for_plan(plan_path)
        self.assertEqual(len(result), 2)

    def test_find_no_subplans(self):
        """Test finding with no SUBPLANs."""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text("# PLAN: Test\n")

        result = find_subplans_for_plan(plan_path)
        self.assertEqual(len(result), 0)

    def test_find_with_different_feature(self):
        """Test finding with different feature name."""
        plan_path = Path("PLAN_OTHER.md")
        plan_path.write_text("# PLAN: Other\n")

        # Create SUBPLANs for different feature
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")

        result = find_subplans_for_plan(plan_path)
        self.assertEqual(len(result), 0)


class TestFindExecutionTasksForPlan(unittest.TestCase):
    """Test find_execution_tasks_for_plan function."""

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

    def test_find_execution_tasks_in_root(self):
        """Test finding EXECUTION_TASKs in root."""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text("# PLAN: Test\n")

        # Create EXECUTION_TASK files
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_22_01.md").write_text("# EXECUTION_TASK: Test\n")

        result = find_execution_tasks_for_plan(plan_path)
        self.assertEqual(len(result), 2)

    def test_find_execution_tasks_in_archive(self):
        """Test finding EXECUTION_TASKs in archive."""
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Get actual archive location (will be fallback)
        archive_path = get_archive_location(plan_path)
        archive_dir = archive_path / "execution"
        archive_dir.mkdir(parents=True, exist_ok=True)
        (archive_dir / "EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        (archive_dir / "EXECUTION_TASK_TEST_22_01.md").write_text("# EXECUTION_TASK: Test\n")

        result = find_execution_tasks_for_plan(plan_path)
        self.assertEqual(len(result), 2)

    def test_find_execution_tasks_both_locations(self):
        """Test finding EXECUTION_TASKs in both root and archive."""
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create EXECUTION_TASK in root
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")

        # Get actual archive location (will be fallback)
        archive_path = get_archive_location(plan_path)
        archive_dir = archive_path / "execution"
        archive_dir.mkdir(parents=True, exist_ok=True)
        (archive_dir / "EXECUTION_TASK_TEST_22_01.md").write_text("# EXECUTION_TASK: Test\n")

        result = find_execution_tasks_for_plan(plan_path)
        self.assertEqual(len(result), 2)

    def test_find_no_execution_tasks(self):
        """Test finding with no EXECUTION_TASKs."""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text("# PLAN: Test\n")

        result = find_execution_tasks_for_plan(plan_path)
        self.assertEqual(len(result), 0)

    def test_find_multiple_attempts(self):
        """Test finding EXECUTION_TASKs with multiple attempts."""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text("# PLAN: Test\n")

        # Create multiple EXECUTION_TASK files for same achievement
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_11_02.md").write_text("# EXECUTION_TASK: Test\n")

        result = find_execution_tasks_for_plan(plan_path)
        self.assertEqual(len(result), 2)


class TestFindExecutionTasksForSubplan(unittest.TestCase):
    """Test find_execution_tasks_for_subplan function."""

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

    def test_find_execution_tasks_in_root(self):
        """Test finding EXECUTION_TASKs in root."""
        subplan_path = Path("SUBPLAN_TEST_11.md")
        subplan_path.write_text("# SUBPLAN: Test\n")

        # Create EXECUTION_TASK files
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_11_02.md").write_text("# EXECUTION_TASK: Test\n")

        result = find_execution_tasks_for_subplan(subplan_path)
        self.assertEqual(len(result), 2)

    def test_find_execution_tasks_in_archive(self):
        """Test finding EXECUTION_TASKs in archive."""
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        subplan_path = Path("SUBPLAN_TEST_11.md")
        subplan_path.write_text("# SUBPLAN: Test\n")

        # Get actual archive location (will be fallback)
        archive_path = get_archive_location(plan_path)
        archive_dir = archive_path / "execution"
        archive_dir.mkdir(parents=True, exist_ok=True)
        (archive_dir / "EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        (archive_dir / "EXECUTION_TASK_TEST_11_02.md").write_text("# EXECUTION_TASK: Test\n")

        result = find_execution_tasks_for_subplan(subplan_path)
        self.assertEqual(len(result), 2)

    def test_find_execution_tasks_both_locations(self):
        """Test finding EXECUTION_TASKs in both root and archive."""
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        subplan_path = Path("SUBPLAN_TEST_11.md")
        subplan_path.write_text("# SUBPLAN: Test\n")

        # Create EXECUTION_TASK in root
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")

        # Get actual archive location (will be fallback)
        archive_path = get_archive_location(plan_path)
        archive_dir = archive_path / "execution"
        archive_dir.mkdir(parents=True, exist_ok=True)
        (archive_dir / "EXECUTION_TASK_TEST_11_02.md").write_text("# EXECUTION_TASK: Test\n")

        result = find_execution_tasks_for_subplan(subplan_path)
        self.assertEqual(len(result), 2)

    def test_find_no_execution_tasks(self):
        """Test finding with no EXECUTION_TASKs."""
        subplan_path = Path("SUBPLAN_TEST_11.md")
        subplan_path.write_text("# SUBPLAN: Test\n")

        result = find_execution_tasks_for_subplan(subplan_path)
        self.assertEqual(len(result), 0)

    def test_invalid_subplan_filename(self):
        """Test with invalid SUBPLAN filename."""
        subplan_path = Path("INVALID_SUBPLAN.md")
        subplan_path.write_text("# SUBPLAN: Test\n")

        result = find_execution_tasks_for_subplan(subplan_path)
        self.assertEqual(len(result), 0)


class TestGetArchiveLocation(unittest.TestCase):
    """Test get_archive_location function."""

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

    def test_fallback_to_inferred_location(self):
        """Test fallback to inferred location when not specified."""
        plan_content = """# PLAN: Test Feature

## Other Section
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        result = get_archive_location(plan_path)
        # Falls back to inferred location
        self.assertEqual(result, Path("./test-archive/"))

    def test_fallback_with_hyphens(self):
        """Test fallback with hyphens in feature name."""
        plan_content = """# PLAN: Test Feature Name

## Other Section
"""
        plan_path = Path("PLAN_TEST-FEATURE-NAME.md")
        plan_path.write_text(plan_content)

        result = get_archive_location(plan_path)
        # Falls back to inferred location (converts underscores to hyphens)
        self.assertEqual(result, Path("./test-feature-name-archive/"))


class TestExtractRegisteredSubplans(unittest.TestCase):
    """Test extract_registered_subplans function."""

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

    def test_extract_from_active_components(self):
        """Test extracting from Active Components section."""
        plan_content = """# PLAN: Test Feature

## 🔄 Active Components

- **SUBPLAN_TEST_11**: Achievement 1.1
- **SUBPLAN_TEST_22**: Achievement 2.2

## 🔄 Subplan Tracking
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        result = extract_registered_subplans(plan_path)
        self.assertEqual(len(result), 2)
        self.assertIn("SUBPLAN_TEST_11.md", result)
        self.assertIn("SUBPLAN_TEST_22.md", result)

    def test_extract_from_subplan_tracking(self):
        """Test extracting from Subplan Tracking section."""
        plan_content = """# PLAN: Test Feature

## 🔄 Subplan Tracking

- **SUBPLAN_TEST_11**: Achievement 1.1 - Status: ✅ Complete
- **SUBPLAN_TEST_22**: Achievement 2.2 - Status: ✅ Complete

## Other Section
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        result = extract_registered_subplans(plan_path)
        self.assertEqual(len(result), 2)
        self.assertIn("SUBPLAN_TEST_11.md", result)
        self.assertIn("SUBPLAN_TEST_22.md", result)

    def test_extract_from_both_sections(self):
        """Test extracting from both sections (duplicates removed)."""
        plan_content = """# PLAN: Test Feature

## 🔄 Active Components

- **SUBPLAN_TEST_11**: Achievement 1.1

## 🔄 Subplan Tracking

- **SUBPLAN_TEST_11**: Achievement 1.1 - Status: ✅ Complete
- **SUBPLAN_TEST_22**: Achievement 2.2 - Status: ✅ Complete

## Other Section
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        result = extract_registered_subplans(plan_path)
        # Duplicates should be removed
        self.assertEqual(len(result), 2)
        self.assertIn("SUBPLAN_TEST_11.md", result)
        self.assertIn("SUBPLAN_TEST_22.md", result)

    def test_extract_no_registered(self):
        """Test extracting with no registered SUBPLANs."""
        plan_content = """# PLAN: Test Feature

## Other Section
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        result = extract_registered_subplans(plan_path)
        self.assertEqual(result, [])


class TestExtractRegisteredExecutionTasksPlan(unittest.TestCase):
    """Test extract_registered_execution_tasks_plan function."""

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

    def test_extract_from_active_components(self):
        """Test extracting from Active Components section."""
        plan_content = """# PLAN: Test Feature

## 🔄 Active Components

- **EXECUTION_TASK_TEST_11_01**: Iteration 1
- **EXECUTION_TASK_TEST_22_01**: Iteration 1

## 🔄 Subplan Tracking
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        result = extract_registered_execution_tasks_plan(plan_path)
        self.assertEqual(len(result), 2)
        self.assertIn("EXECUTION_TASK_TEST_11_01.md", result)
        self.assertIn("EXECUTION_TASK_TEST_22_01.md", result)

    def test_extract_from_subplan_tracking(self):
        """Test extracting from Subplan Tracking section."""
        plan_content = """# PLAN: Test Feature

## 🔄 Subplan Tracking

- **SUBPLAN_11**: Achievement 1.1
  └─ EXECUTION_TASK_TEST_11_01: Iteration 1 - Status: ✅ Complete
- **SUBPLAN_22**: Achievement 2.2
  └─ EXECUTION_TASK_TEST_22_01: Iteration 1 - Status: ✅ Complete

## Other Section
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        result = extract_registered_execution_tasks_plan(plan_path)
        self.assertEqual(len(result), 2)
        self.assertIn("EXECUTION_TASK_TEST_11_01.md", result)
        self.assertIn("EXECUTION_TASK_TEST_22_01.md", result)

    def test_extract_from_both_sections(self):
        """Test extracting from both sections (duplicates removed)."""
        plan_content = """# PLAN: Test Feature

## 🔄 Active Components

- **EXECUTION_TASK_TEST_11_01**: Iteration 1

## 🔄 Subplan Tracking

- **SUBPLAN_11**: Achievement 1.1
  └─ EXECUTION_TASK_TEST_11_01: Iteration 1 - Status: ✅ Complete
- **SUBPLAN_22**: Achievement 2.2
  └─ EXECUTION_TASK_TEST_22_01: Iteration 1 - Status: ✅ Complete

## Other Section
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        result = extract_registered_execution_tasks_plan(plan_path)
        # Duplicates should be removed
        self.assertEqual(len(result), 2)
        self.assertIn("EXECUTION_TASK_TEST_11_01.md", result)
        self.assertIn("EXECUTION_TASK_TEST_22_01.md", result)

    def test_extract_no_registered(self):
        """Test extracting with no registered EXECUTION_TASKs."""
        plan_content = """# PLAN: Test Feature

## Other Section
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        result = extract_registered_execution_tasks_plan(plan_path)
        self.assertEqual(result, [])


class TestExtractRegisteredExecutionTasksSubplan(unittest.TestCase):
    """Test extract_registered_execution_tasks_subplan function."""

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

    def test_extract_from_active_section(self):
        """Test extracting from Active EXECUTION_TASKs section."""
        subplan_content = """# SUBPLAN: Test Feature

## 🔄 Active EXECUTION_TASKs

- **EXECUTION_TASK_TEST_11_01**: Iteration 1 - Status: ✅ Complete
- **EXECUTION_TASK_TEST_11_02**: Iteration 2 - Status: ✅ Complete

## Other Section
"""
        subplan_path = Path("SUBPLAN_TEST_11.md")
        subplan_path.write_text(subplan_content)

        result = extract_registered_execution_tasks_subplan(subplan_path)
        self.assertEqual(len(result), 2)
        self.assertIn("EXECUTION_TASK_TEST_11_01.md", result)
        self.assertIn("EXECUTION_TASK_TEST_11_02.md", result)

    def test_extract_no_registered(self):
        """Test extracting with no registered EXECUTION_TASKs."""
        subplan_content = """# SUBPLAN: Test Feature

## Other Section
"""
        subplan_path = Path("SUBPLAN_TEST_11.md")
        subplan_path.write_text(subplan_content)

        result = extract_registered_execution_tasks_subplan(subplan_path)
        self.assertEqual(result, [])


class TestValidatePlanRegistration(unittest.TestCase):
    """Test validate_plan_registration function."""

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

    def test_all_components_registered(self):
        """Test all components registered."""
        # Function looks for SUBPLAN_TEST_11 and EXECUTION_TASK_TEST_11_01 patterns in content
        plan_content = """# PLAN: Test Feature

## 🔄 Subplan Tracking

- **SUBPLAN_TEST_11**: Achievement 1.1 - Status: ✅ Complete
  └─ EXECUTION_TASK_TEST_11_01: Iteration 1 - Status: ✅ Complete
- **SUBPLAN_TEST_22**: Achievement 2.2 - Status: ✅ Complete
  └─ EXECUTION_TASK_TEST_22_01: Iteration 1 - Status: ✅ Complete

## Other Section
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLAN files
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")

        # Create EXECUTION_TASK files
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_22_01.md").write_text("# EXECUTION_TASK: Test\n")

        pass_check, message = validate_plan_registration(plan_path)
        if not pass_check:
            print(f"Validation failed: {message}")
        self.assertTrue(pass_check, f"Validation failed: {message}")
        self.assertIn("✅ Component registration validated", message)
        self.assertIn("All SUBPLANs registered", message)
        self.assertIn("All EXECUTION_TASKs registered", message)

    def test_unregistered_subplans(self):
        """Test unregistered SUBPLANs."""
        plan_content = """# PLAN: Test Feature

## 🔄 Subplan Tracking

- **SUBPLAN_TEST_11**: Achievement 1.1 - Status: ✅ Complete
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLAN files (one unregistered)
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")

        # Create EXECUTION_TASK files
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")

        pass_check, message = validate_plan_registration(plan_path)
        self.assertFalse(pass_check)
        self.assertIn("❌ REGISTRATION ISSUES FOUND", message)
        self.assertIn("Unregistered SUBPLANs", message)

    def test_unregistered_execution_tasks(self):
        """Test unregistered EXECUTION_TASKs."""
        plan_content = """# PLAN: Test Feature

## 🔄 Subplan Tracking

- **SUBPLAN_TEST_11**: Achievement 1.1 - Status: ✅ Complete
  └─ EXECUTION_TASK_TEST_11_01: Iteration 1 - Status: ✅ Complete
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLAN files
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")

        # Create EXECUTION_TASK files (one unregistered)
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_11_02.md").write_text("# EXECUTION_TASK: Test\n")

        pass_check, message = validate_plan_registration(plan_path)
        self.assertFalse(pass_check)
        self.assertIn("❌ REGISTRATION ISSUES FOUND", message)
        self.assertIn("Unregistered EXECUTION_TASKs", message)

    def test_orphaned_subplan_registrations(self):
        """Test orphaned SUBPLAN registrations (warning, not blocking)."""
        plan_content = """# PLAN: Test Feature

## 🔄 Subplan Tracking

- **SUBPLAN_TEST_11**: Achievement 1.1 - Status: ✅ Complete
- **SUBPLAN_TEST_22**: Achievement 2.2 - Status: ✅ Complete

## Other Section
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create only one SUBPLAN file (other is orphaned)
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")

        # Don't create EXECUTION_TASK files (test orphaned SUBPLAN only)

        pass_check, message = validate_plan_registration(plan_path)
        # Orphaned registrations are warnings, not blocking
        if not pass_check:
            print(f"Validation failed: {message}")
        self.assertTrue(pass_check, f"Validation failed: {message}")
        self.assertIn("✅ Component registration validated", message)
        self.assertIn("Orphaned SUBPLAN registrations", message)

    def test_orphaned_execution_task_registrations(self):
        """Test orphaned EXECUTION_TASK registrations (warning, not blocking)."""
        plan_content = """# PLAN: Test Feature

## 🔄 Subplan Tracking

- **SUBPLAN_TEST_11**: Achievement 1.1 - Status: ✅ Complete
  └─ EXECUTION_TASK_TEST_11_01: Iteration 1 - Status: ✅ Complete
  └─ EXECUTION_TASK_TEST_11_02: Iteration 2 - Status: ✅ Complete

## Other Section
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLAN files
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")

        # Create only one EXECUTION_TASK file (other is orphaned)
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")

        pass_check, message = validate_plan_registration(plan_path)
        # Orphaned registrations are warnings, not blocking
        if not pass_check:
            print(f"Validation failed: {message}")
        self.assertTrue(pass_check, f"Validation failed: {message}")
        self.assertIn("✅ Component registration validated", message)
        self.assertIn("Orphaned EXECUTION_TASK registrations", message)

    def test_multiple_issues(self):
        """Test multiple issues (unregistered + orphaned)."""
        plan_content = """# PLAN: Test Feature

## 🔄 Subplan Tracking

- **SUBPLAN_TEST_11**: Achievement 1.1 - Status: ✅ Complete
  └─ EXECUTION_TASK_TEST_11_01: Iteration 1 - Status: ✅ Complete
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLAN files (one unregistered)
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")

        # Create EXECUTION_TASK files (one unregistered)
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_11_02.md").write_text("# EXECUTION_TASK: Test\n")

        pass_check, message = validate_plan_registration(plan_path)
        self.assertFalse(pass_check)
        self.assertIn("❌ REGISTRATION ISSUES FOUND", message)
        self.assertIn("Unregistered SUBPLANs", message)
        self.assertIn("Unregistered EXECUTION_TASKs", message)

    def test_missing_plan_file(self):
        """Test missing PLAN file."""
        plan_path = Path("PLAN_NONEXISTENT.md")

        pass_check, message = validate_plan_registration(plan_path)
        self.assertFalse(pass_check)
        self.assertIn("❌ Error: PLAN file not found", message)

    def test_fix_prompt_in_message(self):
        """Test that error message includes fix prompt."""
        plan_content = """# PLAN: Test Feature

## 🔄 Subplan Tracking

- **SUBPLAN_TEST_11**: Achievement 1.1 - Status: ✅ Complete
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLAN files (one unregistered)
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")

        pass_check, message = validate_plan_registration(plan_path)
        self.assertFalse(pass_check)
        self.assertIn("📋 Fix Prompt:", message)
        self.assertIn("Register unregistered SUBPLANs", message)


class TestValidateSubplanRegistration(unittest.TestCase):
    """Test validate_subplan_registration function."""

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

    def test_all_execution_tasks_registered(self):
        """Test all EXECUTION_TASKs registered."""
        subplan_content = """# SUBPLAN: Test Feature

## 🔄 Active EXECUTION_TASKs

- **EXECUTION_TASK_TEST_11_01**: Iteration 1 - Status: ✅ Complete
- **EXECUTION_TASK_TEST_11_02**: Iteration 2 - Status: ✅ Complete

## Other Section
"""
        subplan_path = Path("SUBPLAN_TEST_11.md")
        subplan_path.write_text(subplan_content)

        # Create EXECUTION_TASK files
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_11_02.md").write_text("# EXECUTION_TASK: Test\n")

        pass_check, message = validate_subplan_registration(subplan_path)
        self.assertTrue(pass_check)
        self.assertIn("✅ Component registration validated", message)
        self.assertIn("All EXECUTION_TASKs registered", message)

    def test_unregistered_execution_tasks(self):
        """Test unregistered EXECUTION_TASKs."""
        subplan_content = """# SUBPLAN: Test Feature

## 🔄 Active EXECUTION_TASKs

- **EXECUTION_TASK_TEST_11_01**: Iteration 1 - Status: ✅ Complete

## Other Section
"""
        subplan_path = Path("SUBPLAN_TEST_11.md")
        subplan_path.write_text(subplan_content)

        # Create EXECUTION_TASK files (one unregistered)
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_11_02.md").write_text("# EXECUTION_TASK: Test\n")

        pass_check, message = validate_subplan_registration(subplan_path)
        self.assertFalse(pass_check)
        self.assertIn("❌ REGISTRATION ISSUES FOUND", message)
        self.assertIn("Unregistered EXECUTION_TASKs", message)

    def test_missing_subplan_file(self):
        """Test missing SUBPLAN file."""
        subplan_path = Path("SUBPLAN_NONEXISTENT_11.md")

        pass_check, message = validate_subplan_registration(subplan_path)
        self.assertFalse(pass_check)
        self.assertIn("❌ Error: SUBPLAN file not found", message)

    def test_fix_prompt_in_message(self):
        """Test that error message includes fix prompt."""
        subplan_content = """# SUBPLAN: Test Feature

## 🔄 Active EXECUTION_TASKs

- **EXECUTION_TASK_TEST_11_01**: Iteration 1 - Status: ✅ Complete

## Other Section
"""
        subplan_path = Path("SUBPLAN_TEST_11.md")
        subplan_path.write_text(subplan_content)

        # Create EXECUTION_TASK files (one unregistered)
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_11_02.md").write_text("# EXECUTION_TASK: Test\n")

        pass_check, message = validate_subplan_registration(subplan_path)
        self.assertFalse(pass_check)
        self.assertIn("📋 Fix Prompt:", message)
        self.assertIn("Register unregistered EXECUTION_TASKs", message)


class TestIntegration(unittest.TestCase):
    """Integration tests with real PLAN/SUBPLAN structures."""

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

    def test_complete_valid_plan(self):
        """Test with complete valid PLAN."""
        plan_content = """# PLAN: Test Feature

## 🔄 Subplan Tracking

- **SUBPLAN_TEST_11**: Achievement 1.1 - Status: ✅ Complete
  └─ EXECUTION_TASK_TEST_11_01: Iteration 1 - Status: ✅ Complete
- **SUBPLAN_TEST_22**: Achievement 2.2 - Status: ✅ Complete
  └─ EXECUTION_TASK_TEST_22_01: Iteration 1 - Status: ✅ Complete

## Other Section
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLAN files
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")

        # Create EXECUTION_TASK files
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_22_01.md").write_text("# EXECUTION_TASK: Test\n")

        pass_check, message = validate_plan_registration(plan_path)
        if not pass_check:
            print(f"Validation failed: {message}")
        self.assertTrue(pass_check, f"Validation failed: {message}")
        self.assertIn("✅ Component registration validated", message)

    def test_complete_valid_subplan(self):
        """Test with complete valid SUBPLAN."""
        subplan_content = """# SUBPLAN: Test Feature

## 🔄 Active EXECUTION_TASKs

- **EXECUTION_TASK_TEST_11_01**: Iteration 1 - Status: ✅ Complete
- **EXECUTION_TASK_TEST_11_02**: Iteration 2 - Status: ✅ Complete

## Other Section
"""
        subplan_path = Path("SUBPLAN_TEST_11.md")
        subplan_path.write_text(subplan_content)

        # Create EXECUTION_TASK files
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_11_02.md").write_text("# EXECUTION_TASK: Test\n")

        pass_check, message = validate_subplan_registration(subplan_path)
        self.assertTrue(pass_check, f"Validation failed: {message}")
        self.assertIn("✅ Component registration validated", message)

    def test_cli_argument_parsing(self):
        """Test CLI argument parsing (simulated)."""
        # This tests the main() function indirectly through validate functions
        # Actual CLI testing would require subprocess or mocking argparse
        plan_content = """# PLAN: Test Feature

## 🔄 Subplan Tracking

- **SUBPLAN_TEST_11**: Achievement 1.1 - Status: ✅ Complete
  └─ EXECUTION_TASK_TEST_11_01: Iteration 1 - Status: ✅ Complete

## Other Section
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")

        # Test with @ prefix (should be handled by main, but we test validate directly)
        pass_check, message = validate_plan_registration(plan_path)
        if not pass_check:
            print(f"Validation failed: {message}")
        self.assertTrue(pass_check, f"Validation failed: {message}")


if __name__ == "__main__":
    unittest.main()

