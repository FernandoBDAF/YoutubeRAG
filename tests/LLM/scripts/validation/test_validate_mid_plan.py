"""Unit tests for validate_mid_plan.py - Mid-plan compliance validation."""

import unittest
import sys
import tempfile
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from LLM.scripts.validation.validate_mid_plan import (
    extract_statistics,
    count_actual_subplans,
    count_actual_execution_tasks,
    get_archive_location,
    check_subplan_registration,
    validate_mid_plan,
)


class TestExtractStatistics(unittest.TestCase):
    """Test extract_statistics function."""

    def test_extract_subplan_count(self):
        """Test extracting SUBPLAN count."""
        plan_content = """# PLAN: Test Feature

## Subplan Tracking

**Summary Statistics**:

- **SUBPLANs**: 5 created (5 complete, 0 in progress, 0 pending)
- **EXECUTION_TASKs**: 5 created (5 complete, 0 abandoned)
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(plan_content)
            temp_path = Path(f.name)

        try:
            result = extract_statistics(temp_path)
            self.assertEqual(result["subplans_claimed"], 5)
        finally:
            temp_path.unlink()

    def test_extract_execution_task_count(self):
        """Test extracting EXECUTION_TASK count."""
        plan_content = """# PLAN: Test Feature

## Subplan Tracking

**Summary Statistics**:

- **SUBPLANs**: 3 created (3 complete, 0 in progress, 0 pending)
- **EXECUTION_TASKs**: 3 created (3 complete, 0 abandoned)
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(plan_content)
            temp_path = Path(f.name)

        try:
            result = extract_statistics(temp_path)
            self.assertEqual(result["execution_tasks_claimed"], 3)
        finally:
            temp_path.unlink()

    def test_extract_both_counts(self):
        """Test extracting both SUBPLAN and EXECUTION_TASK counts."""
        plan_content = """# PLAN: Test Feature

## Subplan Tracking

**Summary Statistics**:

- **SUBPLANs**: 10 created (10 complete, 0 in progress, 0 pending)
- **EXECUTION_TASKs**: 10 created (10 complete, 0 abandoned)
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(plan_content)
            temp_path = Path(f.name)

        try:
            result = extract_statistics(temp_path)
            self.assertEqual(result["subplans_claimed"], 10)
            self.assertEqual(result["execution_tasks_claimed"], 10)
        finally:
            temp_path.unlink()

    def test_missing_statistics_section(self):
        """Test missing statistics section."""
        plan_content = """# PLAN: Test Feature

## Other Section
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(plan_content)
            temp_path = Path(f.name)

        try:
            result = extract_statistics(temp_path)
            self.assertEqual(result, {})
        finally:
            temp_path.unlink()

    def test_partial_statistics(self):
        """Test PLAN with only SUBPLAN count."""
        plan_content = """# PLAN: Test Feature

## Subplan Tracking

**Summary Statistics**:

- **SUBPLANs**: 5 created (5 complete, 0 in progress, 0 pending)
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(plan_content)
            temp_path = Path(f.name)

        try:
            result = extract_statistics(temp_path)
            self.assertEqual(result["subplans_claimed"], 5)
            self.assertNotIn("execution_tasks_claimed", result)
        finally:
            temp_path.unlink()


class TestCountActualSubplans(unittest.TestCase):
    """Test count_actual_subplans function."""

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

    def test_count_subplans_in_root(self):
        """Test counting SUBPLANs in root."""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text("# PLAN: Test\n")

        # Create SUBPLAN files
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")

        result = count_actual_subplans(plan_path)
        self.assertEqual(result, 2)

    def test_count_subplans_in_archive(self):
        """Test counting SUBPLANs in archive."""
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

        result = count_actual_subplans(plan_path)
        self.assertEqual(result, 2)

    def test_count_subplans_both_locations(self):
        """Test counting SUBPLANs in both root and archive."""
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLANs in root
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")

        # Get actual archive location (will be fallback)
        archive_path = get_archive_location(plan_path)
        archive_dir = archive_path / "subplans"
        archive_dir.mkdir(parents=True, exist_ok=True)
        (archive_dir / "SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")

        result = count_actual_subplans(plan_path)
        self.assertEqual(result, 2)

    def test_count_no_subplans(self):
        """Test counting with no SUBPLANs."""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text("# PLAN: Test\n")

        result = count_actual_subplans(plan_path)
        self.assertEqual(result, 0)

    def test_count_with_different_feature(self):
        """Test counting with different feature name."""
        plan_path = Path("PLAN_OTHER.md")
        plan_path.write_text("# PLAN: Other\n")

        # Create SUBPLANs for different feature
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")

        result = count_actual_subplans(plan_path)
        self.assertEqual(result, 0)


class TestCountActualExecutionTasks(unittest.TestCase):
    """Test count_actual_execution_tasks function."""

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

    def test_count_execution_tasks_in_root(self):
        """Test counting EXECUTION_TASKs in root."""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text("# PLAN: Test\n")

        # Create EXECUTION_TASK files
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_22_01.md").write_text("# EXECUTION_TASK: Test\n")

        result = count_actual_execution_tasks(plan_path)
        self.assertEqual(result, 2)

    def test_count_execution_tasks_in_archive(self):
        """Test counting EXECUTION_TASKs in archive."""
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

        result = count_actual_execution_tasks(plan_path)
        self.assertEqual(result, 2)

    def test_count_execution_tasks_both_locations(self):
        """Test counting EXECUTION_TASKs in both root and archive."""
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create EXECUTION_TASKs in root
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")

        # Get actual archive location (will be fallback)
        archive_path = get_archive_location(plan_path)
        archive_dir = archive_path / "execution"
        archive_dir.mkdir(parents=True, exist_ok=True)
        (archive_dir / "EXECUTION_TASK_TEST_22_01.md").write_text("# EXECUTION_TASK: Test\n")

        result = count_actual_execution_tasks(plan_path)
        self.assertEqual(result, 2)

    def test_count_no_execution_tasks(self):
        """Test counting with no EXECUTION_TASKs."""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text("# PLAN: Test\n")

        result = count_actual_execution_tasks(plan_path)
        self.assertEqual(result, 0)

    def test_count_multiple_attempts(self):
        """Test counting EXECUTION_TASKs with multiple attempts (01, 02)."""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text("# PLAN: Test\n")

        # Create multiple EXECUTION_TASK files for same achievement
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_11_02.md").write_text("# EXECUTION_TASK: Test\n")

        result = count_actual_execution_tasks(plan_path)
        self.assertEqual(result, 2)


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


class TestCheckSubplanRegistration(unittest.TestCase):
    """Test check_subplan_registration function."""

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

    def test_all_subplans_registered(self):
        """Test all SUBPLANs registered."""
        # Function checks for "SUBPLAN_TEST_11" and "SUBPLAN_TEST_22" in content
        plan_content = """# PLAN: Test Feature

## Subplan Tracking

- **SUBPLAN_TEST_11**: Achievement 1.1 - Status: ✅ Complete
- **SUBPLAN_TEST_22**: Achievement 2.2 - Status: ✅ Complete
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLAN files
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")

        result = check_subplan_registration(plan_path)
        self.assertEqual(result, [])

    def test_some_subplans_unregistered(self):
        """Test some SUBPLANs unregistered."""
        # Function extracts subplan_num (last part after underscore) and checks for "SUBPLAN_{feature}_{subplan_num}"
        # For "SUBPLAN_TEST_11.md", it looks for "SUBPLAN_TEST_11" in content
        plan_content = """# PLAN: Test Feature

## Subplan Tracking

- **SUBPLAN_TEST_11**: Achievement 1.1 - Status: ✅ Complete
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLAN files
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")

        result = check_subplan_registration(plan_path)
        # Function checks if "SUBPLAN_TEST_11" is in content (it is, in "**SUBPLAN_TEST_11**")
        # Function checks if "SUBPLAN_TEST_22" is in content (it is not)
        # So only SUBPLAN_TEST_22 should be unregistered
        # But wait - the function extracts subplan_num as the last part after underscore
        # For "SUBPLAN_TEST_11.md", subplan_num = "11"
        # It looks for "SUBPLAN_TEST_11" which should match "**SUBPLAN_TEST_11**"
        self.assertEqual(len(result), 1)
        self.assertIn("SUBPLAN_TEST_22.md", result)

    def test_subplans_in_archive(self):
        """Test SUBPLANs in archive are checked."""
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`

## Subplan Tracking

- **SUBPLAN_11**: Achievement 1.1 - Status: ✅ Complete
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create archive directory and SUBPLAN
        archive_dir = Path("documentation/archive/test-feature/subplans")
        archive_dir.mkdir(parents=True)
        (archive_dir / "SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")

        result = check_subplan_registration(plan_path)
        self.assertEqual(result, [])

    def test_no_subplans(self):
        """Test with no SUBPLANs."""
        plan_content = """# PLAN: Test Feature

## Subplan Tracking
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        result = check_subplan_registration(plan_path)
        self.assertEqual(result, [])


class TestValidateMidPlan(unittest.TestCase):
    """Test validate_mid_plan function."""

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

    def test_all_checks_pass(self):
        """Test all checks pass."""
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`

## Subplan Tracking

**Summary Statistics**:

- **SUBPLANs**: 2 created (2 complete, 0 in progress, 0 pending)
- **EXECUTION_TASKs**: 2 created (2 complete, 0 abandoned)

- **SUBPLAN_11**: Achievement 1.1 - Status: ✅ Complete
- **SUBPLAN_22**: Achievement 2.2 - Status: ✅ Complete
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLAN files
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")

        # Create EXECUTION_TASK files
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_22_01.md").write_text("# EXECUTION_TASK: Test\n")

        # Create archive directory
        archive_path = get_archive_location(plan_path)
        archive_path.mkdir(parents=True, exist_ok=True)

        pass_check, message = validate_mid_plan(plan_path)
        self.assertTrue(pass_check)
        self.assertIn("✅ PLAN compliance validated", message)
        self.assertIn("Statistics accurate", message)
        self.assertIn("Archive location exists", message)

    def test_subplan_count_mismatch(self):
        """Test SUBPLAN count mismatch."""
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`

## Subplan Tracking

**Summary Statistics**:

- **SUBPLANs**: 5 created (5 complete, 0 in progress, 0 pending)
- **EXECUTION_TASKs**: 2 created (2 complete, 0 abandoned)
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create only 2 SUBPLAN files (not 5)
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")

        # Create EXECUTION_TASK files
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_22_01.md").write_text("# EXECUTION_TASK: Test\n")

        # Create archive directory
        archive_path = get_archive_location(plan_path)
        archive_path.mkdir(parents=True, exist_ok=True)

        pass_check, message = validate_mid_plan(plan_path)
        self.assertFalse(pass_check)
        self.assertIn("❌ PLAN COMPLIANCE ISSUES FOUND", message)
        self.assertIn("SUBPLAN count mismatch", message)

    def test_execution_task_count_mismatch(self):
        """Test EXECUTION_TASK count mismatch."""
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`

## Subplan Tracking

**Summary Statistics**:

- **SUBPLANs**: 2 created (2 complete, 0 in progress, 0 pending)
- **EXECUTION_TASKs**: 5 created (5 complete, 0 abandoned)
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLAN files
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")

        # Create only 2 EXECUTION_TASK files (not 5)
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_22_01.md").write_text("# EXECUTION_TASK: Test\n")

        # Create archive directory
        archive_path = get_archive_location(plan_path)
        archive_path.mkdir(parents=True, exist_ok=True)

        pass_check, message = validate_mid_plan(plan_path)
        self.assertFalse(pass_check)
        self.assertIn("❌ PLAN COMPLIANCE ISSUES FOUND", message)
        self.assertIn("EXECUTION_TASK count mismatch", message)

    def test_unregistered_subplans_warning(self):
        """Test unregistered SUBPLANs (warning, not blocking)."""
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`

## Subplan Tracking

**Summary Statistics**:

- **SUBPLANs**: 2 created (2 complete, 0 in progress, 0 pending)
- **EXECUTION_TASKs**: 2 created (2 complete, 0 abandoned)

- **SUBPLAN_11**: Achievement 1.1 - Status: ✅ Complete
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLAN files (one unregistered)
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")

        # Create EXECUTION_TASK files
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_22_01.md").write_text("# EXECUTION_TASK: Test\n")

        # Create archive directory
        archive_path = get_archive_location(plan_path)
        archive_path.mkdir(parents=True, exist_ok=True)

        pass_check, message = validate_mid_plan(plan_path)
        # Warnings are non-blocking, so should still pass
        self.assertTrue(pass_check)
        self.assertIn("✅ PLAN compliance validated", message)
        self.assertIn("Unregistered SUBPLANs", message)

    def test_missing_archive_location(self):
        """Test missing archive location."""
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`

## Subplan Tracking

**Summary Statistics**:

- **SUBPLANs**: 2 created (2 complete, 0 in progress, 0 pending)
- **EXECUTION_TASKs**: 2 created (2 complete, 0 abandoned)
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLAN files
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")

        # Create EXECUTION_TASK files
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_22_01.md").write_text("# EXECUTION_TASK: Test\n")

        # Don't create archive directory

        pass_check, message = validate_mid_plan(plan_path)
        self.assertFalse(pass_check)
        self.assertIn("❌ PLAN COMPLIANCE ISSUES FOUND", message)
        self.assertIn("Archive location missing", message)

    def test_missing_plan_file(self):
        """Test missing PLAN file."""
        plan_path = Path("PLAN_NONEXISTENT.md")

        pass_check, message = validate_mid_plan(plan_path)
        self.assertFalse(pass_check)
        self.assertIn("❌ Error: PLAN file not found", message)

    def test_multiple_issues(self):
        """Test multiple issues (count mismatch + missing archive)."""
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`

## Subplan Tracking

**Summary Statistics**:

- **SUBPLANs**: 5 created (5 complete, 0 in progress, 0 pending)
- **EXECUTION_TASKs**: 5 created (5 complete, 0 abandoned)
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create only 2 SUBPLAN files (not 5)
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")

        # Create only 2 EXECUTION_TASK files (not 5)
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_22_01.md").write_text("# EXECUTION_TASK: Test\n")

        # Don't create archive directory

        pass_check, message = validate_mid_plan(plan_path)
        self.assertFalse(pass_check)
        self.assertIn("❌ PLAN COMPLIANCE ISSUES FOUND", message)
        self.assertIn("SUBPLAN count mismatch", message)
        self.assertIn("EXECUTION_TASK count mismatch", message)
        self.assertIn("Archive location missing", message)

    def test_fix_prompt_in_message(self):
        """Test that error message includes fix prompt."""
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`

## Subplan Tracking

**Summary Statistics**:

- **SUBPLANs**: 5 created (5 complete, 0 in progress, 0 pending)
- **EXECUTION_TASKs**: 2 created (2 complete, 0 abandoned)
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create only 2 SUBPLAN files (not 5)
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")

        # Create EXECUTION_TASK files
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_22_01.md").write_text("# EXECUTION_TASK: Test\n")

        # Create archive directory
        archive_path = get_archive_location(plan_path)
        archive_path.mkdir(parents=True, exist_ok=True)

        pass_check, message = validate_mid_plan(plan_path)
        self.assertFalse(pass_check)
        self.assertIn("📋 Fix Prompt:", message)
        self.assertIn("Update PLAN statistics", message)


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

    def test_complete_valid_plan(self):
        """Test with complete valid PLAN."""
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`

## Subplan Tracking

**Summary Statistics**:

- **SUBPLANs**: 3 created (3 complete, 0 in progress, 0 pending)
- **EXECUTION_TASKs**: 3 created (3 complete, 0 abandoned)

- **SUBPLAN_11**: Achievement 1.1 - Status: ✅ Complete
- **SUBPLAN_22**: Achievement 2.2 - Status: ✅ Complete
- **SUBPLAN_33**: Achievement 3.3 - Status: ✅ Complete
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create SUBPLAN files
        Path("SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        Path("SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")
        Path("SUBPLAN_TEST_33.md").write_text("# SUBPLAN: Test\n")

        # Create EXECUTION_TASK files
        Path("EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_22_01.md").write_text("# EXECUTION_TASK: Test\n")
        Path("EXECUTION_TASK_TEST_33_01.md").write_text("# EXECUTION_TASK: Test\n")

        # Create archive directory
        archive_path = get_archive_location(plan_path)
        archive_path.mkdir(parents=True, exist_ok=True)

        pass_check, message = validate_mid_plan(plan_path)
        self.assertTrue(pass_check, f"Validation failed: {message}")
        self.assertIn("✅ PLAN compliance validated", message)

    def test_plan_with_archived_files(self):
        """Test PLAN with files in archive."""
        plan_content = """# PLAN: Test Feature

**Archive Location**: `documentation/archive/test-feature/`

## Subplan Tracking

**Summary Statistics**:

- **SUBPLANs**: 2 created (2 complete, 0 in progress, 0 pending)
- **EXECUTION_TASKs**: 2 created (2 complete, 0 abandoned)

- **SUBPLAN_11**: Achievement 1.1 - Status: ✅ Complete
- **SUBPLAN_22**: Achievement 2.2 - Status: ✅ Complete
"""
        plan_path = Path("PLAN_TEST.md")
        plan_path.write_text(plan_content)

        # Create archive directory and files
        archive_path = get_archive_location(plan_path)
        (archive_path / "subplans").mkdir(parents=True, exist_ok=True)
        (archive_path / "execution").mkdir(parents=True, exist_ok=True)

        (archive_path / "subplans" / "SUBPLAN_TEST_11.md").write_text("# SUBPLAN: Test\n")
        (archive_path / "subplans" / "SUBPLAN_TEST_22.md").write_text("# SUBPLAN: Test\n")

        (archive_path / "execution" / "EXECUTION_TASK_TEST_11_01.md").write_text("# EXECUTION_TASK: Test\n")
        (archive_path / "execution" / "EXECUTION_TASK_TEST_22_01.md").write_text("# EXECUTION_TASK: Test\n")

        pass_check, message = validate_mid_plan(plan_path)
        self.assertTrue(pass_check, f"Validation failed: {message}")
        self.assertIn("✅ PLAN compliance validated", message)


if __name__ == "__main__":
    unittest.main()

