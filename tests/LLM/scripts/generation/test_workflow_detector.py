"""
Tests for workflow_detector.py module.

Tests the WorkflowDetector class methods for filesystem-first state detection,
conflict checking, and achievement finding functionality.

Achievement: 2.2 - Extract Workflow Detection Module
Created: 2025-11-12
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from LLM.scripts.generation.workflow_detector import WorkflowDetector
from LLM.scripts.generation.utils import Achievement
from LLM.scripts.generation.plan_parser import PlanParser


class TestWorkflowDetector(unittest.TestCase):
    """Test WorkflowDetector class initialization and basic functionality."""

    def test_init(self):
        """Test WorkflowDetector can be initialized."""
        detector = WorkflowDetector()
        self.assertIsInstance(detector, WorkflowDetector)


class TestDetectWorkflowStateFilesystem(unittest.TestCase):
    """Test detect_workflow_state_filesystem() method."""

    def setUp(self):
        """Create temporary directory structure for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.plan_dir = Path(self.test_dir) / "TEST_PLAN"
        self.plan_dir.mkdir()
        self.plan_path = self.plan_dir / "PLAN_TEST.md"
        self.plan_path.write_text("# Test Plan")
        self.subplans_dir = self.plan_dir / "subplans"
        self.subplans_dir.mkdir()
        self.execution_dir = self.plan_dir / "execution"
        self.execution_dir.mkdir()
        self.detector = WorkflowDetector()

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_no_subplan(self):
        """Test state detection when no SUBPLAN exists."""
        state = self.detector.detect_workflow_state_filesystem(self.plan_path, "TEST", "1.1")
        self.assertEqual(state["state"], "no_subplan")
        self.assertEqual(state["recommendation"], "create_subplan")
        self.assertIsNone(state["subplan_path"])

    def test_subplan_no_execution(self):
        """Test state detection when SUBPLAN exists but no EXECUTION_TASKs."""
        subplan_path = self.subplans_dir / "SUBPLAN_TEST_11.md"
        subplan_path.write_text("**Status**: Pending\n# SUBPLAN")

        state = self.detector.detect_workflow_state_filesystem(self.plan_path, "TEST", "1.1")
        self.assertEqual(state["state"], "subplan_no_execution")
        self.assertEqual(state["recommendation"], "create_execution")
        self.assertEqual(state["subplan_path"], subplan_path)

    def test_active_execution(self):
        """Test state detection when EXECUTIONs are active."""
        subplan_path = self.subplans_dir / "SUBPLAN_TEST_11.md"
        subplan_path.write_text("**Status**: In Progress\n# SUBPLAN")

        exec_path = self.execution_dir / "EXECUTION_TASK_TEST_11_01.md"
        exec_path.write_text("**Status**: 🎯 In Progress\n# Execution")

        state = self.detector.detect_workflow_state_filesystem(self.plan_path, "TEST", "1.1")
        self.assertEqual(state["state"], "active_execution")
        self.assertEqual(state["recommendation"], "continue_execution")
        self.assertEqual(state["execution_count"], 1)
        self.assertEqual(state["completed_count"], 0)

    def test_subplan_all_executed(self):
        """Test state detection when all EXECUTIONs are complete."""
        subplan_path = self.subplans_dir / "SUBPLAN_TEST_11.md"
        subplan_path.write_text("**Status**: In Progress\n# SUBPLAN")

        exec_path = self.execution_dir / "EXECUTION_TASK_TEST_11_01.md"
        exec_path.write_text("**Status**: ✅ Complete\n# Execution")

        state = self.detector.detect_workflow_state_filesystem(self.plan_path, "TEST", "1.1")
        self.assertEqual(state["state"], "subplan_all_executed")
        self.assertEqual(state["recommendation"], "synthesize_or_complete")
        self.assertEqual(state["execution_count"], 1)
        self.assertEqual(state["completed_count"], 1)

    def test_subplan_complete(self):
        """Test state detection when SUBPLAN is marked complete."""
        subplan_path = self.subplans_dir / "SUBPLAN_TEST_11.md"
        subplan_path.write_text("**Status**: ✅ Complete\n# SUBPLAN")

        state = self.detector.detect_workflow_state_filesystem(self.plan_path, "TEST", "1.1")
        self.assertEqual(state["state"], "subplan_complete")
        self.assertEqual(state["recommendation"], "next_achievement")


class TestDetectPlanFilesystemConflict(unittest.TestCase):
    """Test detect_plan_filesystem_conflict() method."""

    def setUp(self):
        """Create temporary directory structure for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.plan_dir = Path(self.test_dir) / "TEST_PLAN"
        self.plan_dir.mkdir()

        # Create a minimal PLAN with Achievement Index
        plan_content = """# PLAN
## 📋 Achievement Index
- Achievement 1.1: Test Achievement
- Achievement 1.2: Another Achievement
"""
        self.plan_path = self.plan_dir / "PLAN_TEST.md"
        self.plan_path.write_text(plan_content)

        self.feedbacks_dir = self.plan_dir / "execution" / "feedbacks"
        self.feedbacks_dir.mkdir(parents=True)
        self.subplans_dir = self.plan_dir / "subplans"
        self.subplans_dir.mkdir()
        self.detector = WorkflowDetector()

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_no_conflict(self):
        """Test when there are no conflicts."""
        conflict = self.detector.detect_plan_filesystem_conflict(
            self.plan_path, "TEST", "1.1", self.plan_path.read_text()
        )
        self.assertIsNone(conflict)

    def test_approved_file_not_in_index(self):
        """Test conflict when APPROVED file exists for achievement not in Index."""
        # Create APPROVED file for achievement 2.1 (not in index)
        approved_file = self.feedbacks_dir / "APPROVED_21.md"
        approved_file.write_text("# APPROVED")

        conflict = self.detector.detect_plan_filesystem_conflict(
            self.plan_path, "TEST", "1.1", self.plan_path.read_text()
        )
        self.assertIsNotNone(conflict)
        self.assertTrue(conflict["has_conflict"])
        self.assertEqual(len(conflict["conflicts"]), 1)
        self.assertEqual(conflict["conflicts"][0]["type"], "achievement_not_in_index")

    def test_orphaned_subplan(self):
        """Test conflict when SUBPLAN exists for achievement not in Index."""
        # Create SUBPLAN for achievement 2.1 (not in index)
        subplan_file = self.subplans_dir / "SUBPLAN_TEST_21.md"
        subplan_file.write_text("# SUBPLAN")

        conflict = self.detector.detect_plan_filesystem_conflict(
            self.plan_path, "TEST", "1.1", self.plan_path.read_text()
        )
        self.assertIsNotNone(conflict)
        self.assertTrue(conflict["has_conflict"])
        self.assertEqual(len(conflict["conflicts"]), 1)
        self.assertEqual(conflict["conflicts"][0]["type"], "orphaned_work")


class TestFindNextAchievementHybrid(unittest.TestCase):
    """Test find_next_achievement_hybrid() method."""

    def setUp(self):
        """Create temporary directory structure for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.plan_dir = Path(self.test_dir) / "TEST_PLAN"
        self.plan_dir.mkdir()

        # Create achievements
        self.achievements = [
            Achievement(
                number="1.1",
                title="First",
                goal="Test goal",
                effort="2h",
                priority="P1",
                section_lines=10,
            ),
            Achievement(
                number="1.2",
                title="Second",
                goal="Test goal",
                effort="3h",
                priority="P1",
                section_lines=10,
            ),
            Achievement(
                number="2.1",
                title="Third",
                goal="Test goal",
                effort="4h",
                priority="P2",
                section_lines=10,
            ),
        ]

        # Create feedbacks directory for completion tracking
        self.feedbacks_dir = self.plan_dir / "execution" / "feedbacks"
        self.feedbacks_dir.mkdir(parents=True)

        self.detector = WorkflowDetector()

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_returns_none_when_plan_complete(self):
        """Test that None is returned when all achievements are complete."""
        # Mark all achievements complete
        (self.feedbacks_dir / "APPROVED_11.md").write_text("# APPROVED")
        (self.feedbacks_dir / "APPROVED_12.md").write_text("# APPROVED")
        (self.feedbacks_dir / "APPROVED_21.md").write_text("# APPROVED")

        plan_content = """## 📋 Achievement Index
- Achievement 1.1: First
- Achievement 1.2: Second
- Achievement 2.1: Third"""
        plan_path = self.plan_dir / "PLAN_TEST.md"
        plan_path.write_text(plan_content)

        next_ach = self.detector.find_next_achievement_hybrid(
            plan_path, "TEST", self.achievements, str(self.plan_dir / "archive")
        )
        self.assertIsNone(next_ach)

    def test_finds_first_incomplete(self):
        """Test finding first incomplete achievement."""
        # Mark 1.1 complete, leave 1.2 incomplete
        (self.feedbacks_dir / "APPROVED_11.md").write_text("# APPROVED")

        plan_content = """## 📋 Achievement Index
- Achievement 1.1: First
- Achievement 1.2: Second
- Achievement 2.1: Third

## Current Status & Handoff
Next: Achievement 1.2"""
        plan_path = self.plan_dir / "PLAN_TEST.md"
        plan_path.write_text(plan_content)

        next_ach = self.detector.find_next_achievement_hybrid(
            plan_path, "TEST", self.achievements, str(self.plan_dir / "archive")
        )
        self.assertIsNotNone(next_ach)
        self.assertEqual(next_ach.number, "1.2")


class TestFindNextAchievementFromPlan(unittest.TestCase):
    """Test find_next_achievement_from_plan() method."""

    def setUp(self):
        """Initialize detector."""
        self.detector = WorkflowDetector()

    def test_finds_next_from_handoff(self):
        """Test finding achievement from handoff section."""
        plan_content = """
## Current Status & Handoff
Next: Achievement 1.2
"""
        next_num = self.detector.find_next_achievement_from_plan(plan_content)
        self.assertEqual(next_num, "1.2")

    def test_finds_next_with_emoji(self):
        """Test finding achievement with emoji pattern."""
        plan_content = """
## Current Status & Handoff
⏳ Next: Achievement 2.1
"""
        next_num = self.detector.find_next_achievement_from_plan(plan_content)
        self.assertEqual(next_num, "2.1")

    def test_returns_none_when_not_found(self):
        """Test returns None when no next achievement found."""
        plan_content = """
## Current Status & Handoff
All complete!
"""
        next_num = self.detector.find_next_achievement_from_plan(plan_content)
        self.assertIsNone(next_num)


class TestFindNextAchievementFromArchive(unittest.TestCase):
    """Test find_next_achievement_from_archive() method."""

    def setUp(self):
        """Create temporary directory structure."""
        self.test_dir = tempfile.mkdtemp()
        self.plan_dir = Path(self.test_dir) / "TEST_PLAN"
        self.plan_dir.mkdir()
        self.archive_dir = self.plan_dir / "archive" / "subplans"
        self.archive_dir.mkdir(parents=True)
        self.feedbacks_dir = self.plan_dir / "execution" / "feedbacks"
        self.feedbacks_dir.mkdir(parents=True)

        self.plan_path = self.plan_dir / "PLAN_TEST.md"
        plan_content = """## 📋 Achievement Index
- Achievement 1.1: First
- Achievement 1.2: Second"""
        self.plan_path.write_text(plan_content)

        self.achievements = [
            Achievement(
                number="1.1",
                title="First",
                goal="Test goal",
                effort="2h",
                priority="P1",
                section_lines=10,
            ),
            Achievement(
                number="1.2",
                title="Second",
                goal="Test goal",
                effort="3h",
                priority="P1",
                section_lines=10,
            ),
        ]
        self.detector = WorkflowDetector()

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_finds_achievement_without_archived_subplan(self):
        """Test finding first achievement without archived SUBPLAN."""
        # Archive 1.1's SUBPLAN
        (self.archive_dir / "SUBPLAN_TEST_11.md").write_text("# Archived")

        next_ach = self.detector.find_next_achievement_from_archive(
            "TEST",
            self.achievements,
            str(self.archive_dir.parent),
            self.plan_path.read_text(),
            self.plan_path,
        )
        self.assertIsNotNone(next_ach)
        self.assertEqual(next_ach.number, "1.2")

    def test_skips_completed_achievements(self):
        """Test that completed achievements are skipped."""
        # Mark 1.1 complete
        (self.feedbacks_dir / "APPROVED_11.md").write_text("# APPROVED")

        next_ach = self.detector.find_next_achievement_from_archive(
            "TEST",
            self.achievements,
            str(self.archive_dir.parent),
            self.plan_path.read_text(),
            self.plan_path,
        )
        self.assertIsNotNone(next_ach)
        self.assertEqual(next_ach.number, "1.2")


class TestFindNextAchievementFromRoot(unittest.TestCase):
    """Test find_next_achievement_from_root() method."""

    def setUp(self):
        """Initialize test data."""
        self.test_dir = tempfile.mkdtemp()
        self.plan_dir = Path(self.test_dir) / "TEST_PLAN"
        self.plan_dir.mkdir()
        self.feedbacks_dir = self.plan_dir / "execution" / "feedbacks"
        self.feedbacks_dir.mkdir(parents=True)

        self.plan_path = self.plan_dir / "PLAN_TEST.md"
        plan_content = """## 📋 Achievement Index
- Achievement 1.1: First
- Achievement 1.2: Second"""
        self.plan_path.write_text(plan_content)

        self.achievements = [
            Achievement(
                number="1.1",
                title="First",
                goal="Test goal",
                effort="2h",
                priority="P1",
                section_lines=10,
            ),
            Achievement(
                number="1.2",
                title="Second",
                goal="Test goal",
                effort="3h",
                priority="P1",
                section_lines=10,
            ),
        ]
        self.detector = WorkflowDetector()

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_finds_achievement_without_subplan_in_root(self):
        """Test finding first achievement without SUBPLAN in root."""
        # Create SUBPLAN for 1.1 in root (legacy flat structure)
        (Path.cwd() / "SUBPLAN_TEST_11.md").write_text("# SUBPLAN")

        try:
            next_ach = self.detector.find_next_achievement_from_root(
                "TEST", self.achievements, self.plan_path.read_text(), self.plan_path
            )
            self.assertIsNotNone(next_ach)
            self.assertEqual(next_ach.number, "1.2")
        finally:
            # Clean up
            (Path.cwd() / "SUBPLAN_TEST_11.md").unlink(missing_ok=True)

    def test_skips_completed_achievements(self):
        """Test that completed achievements are skipped."""
        # Mark 1.1 complete
        (self.feedbacks_dir / "APPROVED_11.md").write_text("# APPROVED")

        next_ach = self.detector.find_next_achievement_from_root(
            "TEST", self.achievements, self.plan_path.read_text(), self.plan_path
        )
        self.assertIsNotNone(next_ach)
        self.assertEqual(next_ach.number, "1.2")


if __name__ == "__main__":
    unittest.main()
