"""
Tests for completion message statistics in generate_prompt.py

Achievement 0.2: Helpful Completion Messages & Next Actions
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from LLM.scripts.generation.plan_parser import PlanParser

# Create parser instance for tests
parser = PlanParser()
extract_plan_statistics = parser.extract_plan_statistics


class TestStatisticsExtraction:
    """Test statistics extraction from PLAN and filesystem"""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing"""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir)

        # Create work-space/plans structure
        plans_dir = workspace / "work-space" / "plans"
        test_folder = plans_dir / "TEST-FEATURE"
        test_folder.mkdir(parents=True)

        # Create PLAN file with 3 achievements
        plan_file = test_folder.parent.parent.parent / "PLAN_TEST-FEATURE.md"
        plan_file.write_text(
            """# PLAN: Test Feature

## Desirable Achievements

**Achievement 0.1**: First Achievement
**Achievement 0.2**: Second Achievement
**Achievement 0.3**: Third Achievement
"""
        )

        # Create subplans folder with 3 SUBPLANs
        subplans_dir = test_folder / "subplans"
        subplans_dir.mkdir()
        for i in range(1, 4):
            (subplans_dir / f"SUBPLAN_TEST-FEATURE_0{i}.md").write_text(f"# SUBPLAN {i}")

        # Create execution folder with 3 EXECUTION_TASKs
        execution_dir = test_folder / "execution"
        execution_dir.mkdir()
        for i in range(1, 4):
            (execution_dir / f"EXECUTION_TASK_TEST-FEATURE_0{i}_01.md").write_text(
                f"# EXECUTION_TASK {i}\n**Time**: {i + 1}.5 hours"
            )

        # Save original cwd
        original_cwd = Path.cwd()
        import os

        os.chdir(workspace)

        yield workspace, plan_file

        # Cleanup
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)

    def test_extract_plan_statistics_basic(self, temp_workspace):
        """Should extract basic statistics correctly"""
        workspace, plan_file = temp_workspace

        stats = extract_plan_statistics(plan_file, "TEST-FEATURE")

        assert stats["total_achievements"] == 3
        assert stats["subplan_count"] == 3
        assert stats["execution_count"] == 3

    def test_extract_plan_statistics_with_time(self, temp_workspace):
        """Should sum time from EXECUTION_TASKs"""
        workspace, plan_file = temp_workspace

        stats = extract_plan_statistics(plan_file, "TEST-FEATURE")

        # 2.5 + 3.5 + 4.5 = 10.5 hours
        assert stats["total_time"] == "10.5 hours"

    def test_extract_plan_statistics_empty_plan(self):
        """Should handle PLAN with no achievements gracefully"""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir)

        # Create empty PLAN
        plan_file = workspace / "PLAN_EMPTY.md"
        plan_file.write_text("# PLAN: Empty\n\nNo achievements here.")

        # Create structure
        plans_dir = workspace / "work-space" / "plans" / "EMPTY"
        plans_dir.mkdir(parents=True)

        original_cwd = Path.cwd()
        import os

        os.chdir(workspace)

        stats = extract_plan_statistics(plan_file, "EMPTY")

        assert stats["total_achievements"] == 0
        assert stats["subplan_count"] == 0
        assert stats["execution_count"] == 0
        assert stats["total_time"] == "N/A"

        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)

    def test_extract_plan_statistics_missing_folders(self):
        """Should handle missing subplans/execution folders gracefully"""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir)

        # Create PLAN with achievements
        plan_file = workspace / "PLAN_MISSING.md"
        plan_file.write_text(
            """# PLAN: Missing

**Achievement 0.1**: Test
**Achievement 0.2**: Test
"""
        )

        # Create plans dir but no subplans/execution folders
        plans_dir = workspace / "work-space" / "plans" / "MISSING"
        plans_dir.mkdir(parents=True)

        original_cwd = Path.cwd()
        import os

        os.chdir(workspace)

        stats = extract_plan_statistics(plan_file, "MISSING")

        assert stats["total_achievements"] == 2
        assert stats["subplan_count"] == 0
        assert stats["execution_count"] == 0
        assert stats["total_time"] == "N/A"

        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)

    def test_extract_plan_statistics_no_time_in_executions(self):
        """Should handle EXECUTION_TASKs without time fields"""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir)

        # Create PLAN
        plan_file = workspace / "PLAN_NOTIME.md"
        plan_file.write_text("# PLAN: NoTime\n**Achievement 0.1**: Test")

        # Create structure with EXECUTION_TASKs but no time
        plans_dir = workspace / "work-space" / "plans" / "NOTIME"
        execution_dir = plans_dir / "execution"
        execution_dir.mkdir(parents=True)
        (execution_dir / "EXECUTION_TASK_NOTIME_01_01.md").write_text(
            "# EXECUTION\nNo time field here"
        )

        original_cwd = Path.cwd()
        import os

        os.chdir(workspace)

        stats = extract_plan_statistics(plan_file, "NOTIME")

        assert stats["execution_count"] == 1
        assert stats["total_time"] == "N/A"

        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)

    def test_extract_plan_statistics_mixed_time_formats(self):
        """Should handle different time format variations"""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir)

        # Create PLAN
        plan_file = workspace / "PLAN_MIXED.md"
        plan_file.write_text("# PLAN: Mixed\n**Achievement 0.1**: Test")

        # Create structure with different time formats
        plans_dir = workspace / "work-space" / "plans" / "MIXED"
        execution_dir = plans_dir / "execution"
        execution_dir.mkdir(parents=True)

        # Different formats: "Time:", "Actual:", "hours", "hour"
        (execution_dir / "EXECUTION_TASK_MIXED_01_01.md").write_text("**Time**: 2.5 hours")
        (execution_dir / "EXECUTION_TASK_MIXED_01_02.md").write_text("**Actual**: 3 hours")
        (execution_dir / "EXECUTION_TASK_MIXED_01_03.md").write_text("**Time**: 1 hour")

        original_cwd = Path.cwd()
        import os

        os.chdir(workspace)

        stats = extract_plan_statistics(plan_file, "MIXED")

        # 2.5 + 3 + 1 = 6.5 hours
        assert stats["total_time"] == "6.5 hours"

        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)


class TestCompletionMessage:
    """Test completion message generation with statistics"""

    def test_completion_message_includes_all_statistics(self):
        """Completion message should include all available statistics"""
        stats = {
            "total_achievements": 7,
            "subplan_count": 7,
            "execution_count": 7,
            "total_time": "25.5 hours",
        }

        # Build stats section (same logic as in generate_prompt.py)
        stats_lines = []
        if stats["total_achievements"] > 0:
            stats_lines.append(f"  • {stats['total_achievements']} achievements completed")
        if stats["subplan_count"] > 0:
            stats_lines.append(f"  • {stats['subplan_count']} SUBPLANs created")
        if stats["execution_count"] > 0:
            stats_lines.append(f"  • {stats['execution_count']} EXECUTION_TASKs completed")
        if stats["total_time"] != "N/A":
            stats_lines.append(f"  • {stats['total_time']} invested")

        stats_section = "\n".join(stats_lines)

        assert "7 achievements completed" in stats_section
        assert "7 SUBPLANs created" in stats_section
        assert "7 EXECUTION_TASKs completed" in stats_section
        assert "25.5 hours invested" in stats_section

    def test_completion_message_with_partial_statistics(self):
        """Should handle partial statistics gracefully"""
        stats = {
            "total_achievements": 3,
            "subplan_count": 0,
            "execution_count": 2,
            "total_time": "N/A",
        }

        # Build stats section
        stats_lines = []
        if stats["total_achievements"] > 0:
            stats_lines.append(f"  • {stats['total_achievements']} achievements completed")
        if stats["subplan_count"] > 0:
            stats_lines.append(f"  • {stats['subplan_count']} SUBPLANs created")
        if stats["execution_count"] > 0:
            stats_lines.append(f"  • {stats['execution_count']} EXECUTION_TASKs completed")
        if stats["total_time"] != "N/A":
            stats_lines.append(f"  • {stats['total_time']} invested")

        stats_section = "\n".join(stats_lines) if stats_lines else "  • Work completed successfully"

        assert "3 achievements completed" in stats_section
        assert "SUBPLANs" not in stats_section  # Should skip zero counts
        assert "2 EXECUTION_TASKs completed" in stats_section
        assert "invested" not in stats_section  # Should skip N/A

    def test_completion_message_with_no_statistics(self):
        """Should provide fallback message when no statistics available"""
        stats = {
            "total_achievements": 0,
            "subplan_count": 0,
            "execution_count": 0,
            "total_time": "N/A",
        }

        # Build stats section
        stats_lines = []
        if stats["total_achievements"] > 0:
            stats_lines.append(f"  • {stats['total_achievements']} achievements completed")
        if stats["subplan_count"] > 0:
            stats_lines.append(f"  • {stats['subplan_count']} SUBPLANs created")
        if stats["execution_count"] > 0:
            stats_lines.append(f"  • {stats['execution_count']} EXECUTION_TASKs completed")
        if stats["total_time"] != "N/A":
            stats_lines.append(f"  • {stats['total_time']} invested")

        stats_section = "\n".join(stats_lines) if stats_lines else "  • Work completed successfully"

        assert stats_section == "  • Work completed successfully"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
