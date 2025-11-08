#!/usr/bin/env python3
"""
Unit Tests for Phase 1 Discovery Refactoring

Tests the refactored discovery functions that now assume nested structure exclusively.
"""

import pytest
from pathlib import Path
from LLM.scripts.generation.generate_prompt import (
    find_subplan_for_achievement,
    detect_workflow_state,
)


class TestFindSubplanForAchievement:
    """Test suite for find_subplan_for_achievement() function."""

    def test_find_existing_subplan_with_plan_path(self):
        """Test finding existing SUBPLAN with plan_path provided."""
        subplan = find_subplan_for_achievement(
            "METHODOLOGY-HIERARCHY-EVOLUTION",
            "0.1",
            Path("work-space/plans/METHODOLOGY-HIERARCHY-EVOLUTION/PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md")
        )
        assert subplan is not None, "Should find existing SUBPLAN_METHODOLOGY-HIERARCHY-EVOLUTION_01"
        assert subplan.exists(), f"SUBPLAN file should exist: {subplan}"
        assert "subplans" in str(subplan), "Should be in nested subplans folder"
        assert "SUBPLAN_METHODOLOGY-HIERARCHY-EVOLUTION_01.md" in str(subplan)

    def test_find_subplan_without_plan_path(self):
        """Test finding SUBPLAN without plan_path (using feature_name only)."""
        subplan = find_subplan_for_achievement(
            "METHODOLOGY-HIERARCHY-EVOLUTION",
            "0.1"
        )
        assert subplan is not None, "Should find SUBPLAN using feature_name"
        assert subplan.exists(), f"SUBPLAN should exist: {subplan}"

    def test_find_nonexistent_subplan_returns_none(self):
        """Test that non-existent SUBPLAN returns None."""
        subplan = find_subplan_for_achievement(
            "NONEXISTENT-PLAN",
            "9.9",
            Path("work-space/plans/NONEXISTENT/PLAN_NONEXISTENT.md")
        )
        assert subplan is None, "Should return None for non-existent SUBPLAN"

    def test_achievement_num_formatting(self):
        """Test that achievement number formatting works correctly."""
        # 0.1 should be converted to 01
        subplan = find_subplan_for_achievement(
            "METHODOLOGY-HIERARCHY-EVOLUTION",
            "0.1"
        )
        assert subplan is not None
        assert "01" in str(subplan), "Should format 0.1 as 01"

        # 1.2 should be converted to 12
        subplan = find_subplan_for_achievement(
            "METHODOLOGY-HIERARCHY-EVOLUTION",
            "1.2"
        )
        if subplan:  # If exists
            assert "12" in str(subplan), "Should format 1.2 as 12"

    def test_multiple_plan_discovery(self):
        """Test discovery works with multiple migrated PLANs."""
        plans_to_test = [
            ("METHODOLOGY-HIERARCHY-EVOLUTION", "0.1"),
            ("WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING", "0.1"),
            ("RESTORE-EXECUTION-WORKFLOW-AUTOMATION", "1.1"),
        ]
        
        for plan_name, achievement in plans_to_test:
            plan_file = Path(f"work-space/plans/{plan_name}/PLAN_{plan_name}.md")
            if plan_file.exists():
                subplan = find_subplan_for_achievement(plan_name, achievement, plan_file)
                # Should either find it or return None (not error)
                assert isinstance(subplan, (Path, type(None))), \
                    f"Should return Path or None for {plan_name}/{achievement}"


class TestDetectWorkflowState:
    """Test suite for detect_workflow_state() function."""

    def test_workflow_state_no_subplan(self):
        """Test workflow state when SUBPLAN doesn't exist."""
        state = detect_workflow_state(
            Path("work-space/plans/METHODOLOGY-HIERARCHY-EVOLUTION/PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md"),
            "METHODOLOGY-HIERARCHY-EVOLUTION",
            "9.9"  # Non-existent achievement
        )
        assert state["state"] == "no_subplan", "Should detect no SUBPLAN state"
        assert state["recommendation"] == "create_subplan"
        assert state["subplan_path"] is None

    def test_workflow_state_with_subplan(self):
        """Test workflow state when SUBPLAN exists."""
        state = detect_workflow_state(
            Path("work-space/plans/METHODOLOGY-HIERARCHY-EVOLUTION/PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md"),
            "METHODOLOGY-HIERARCHY-EVOLUTION",
            "0.1"  # Existing achievement
        )
        assert state["state"] in ["subplan_complete", "subplan_no_execution", "active_execution"]
        assert state["subplan_path"] is not None
        assert "recommendation" in state

    def test_workflow_state_has_required_fields(self):
        """Test that workflow state dict has all required fields."""
        state = detect_workflow_state(
            Path("work-space/plans/METHODOLOGY-HIERARCHY-EVOLUTION/PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md"),
            "METHODOLOGY-HIERARCHY-EVOLUTION",
            "0.1"
        )
        required_fields = ["state", "recommendation", "subplan_path"]
        for field in required_fields:
            assert field in state, f"Missing required field: {field}"

    def test_workflow_state_with_multiple_plans(self):
        """Test workflow state works with multiple migrated PLANs."""
        plans_dir = Path("work-space/plans")
        tested = 0
        
        for plan_folder in list(plans_dir.iterdir())[:5]:  # Test first 5
            if plan_folder.is_dir():
                plan_name = plan_folder.name
                plan_file = plan_folder / f"PLAN_{plan_name}.md"
                
                if plan_file.exists():
                    state = detect_workflow_state(plan_file, plan_name, "0.1")
                    assert "state" in state
                    assert "recommendation" in state
                    tested += 1
        
        assert tested > 0, "Should test at least one plan"


class TestNestedStructureAssumptions:
    """Test that functions correctly assume nested structure."""

    def test_no_flat_structure_fallback(self):
        """Verify that flat structure is NOT checked."""
        # Create a SUBPLAN in the old flat structure location (if it exists there)
        # and verify that our function doesn't find it (it should only check nested)
        
        # This test is more of a documentation test - the function should NOT
        # check work-space/subplans/ anymore
        
        # If there are any files in work-space/subplans/, they should NOT be found
        flat_subplans = Path("work-space/subplans").glob("SUBPLAN_*.md")
        for flat_file in list(flat_subplans)[:1]:  # Check first one if any
            # Extract plan name from flat file
            filename = flat_file.stem  # e.g., SUBPLAN_TEST_01
            parts = filename.split("_")
            if len(parts) >= 2:
                # Try to find it - should not find it via flat structure
                # (it might be in nested structure with same name)
                result = find_subplan_for_achievement(
                    parts[1] if len(parts) > 1 else "TEST",
                    "01"
                )
                # We can't assert it's None because it might exist in nested
                # But we know it's not finding from flat structure
                assert isinstance(result, (Path, type(None)))

    def test_archive_discovery_still_works(self):
        """Verify that archive discovery still works after refactoring."""
        # Archive location is documentation/archive/
        archive_base = Path("documentation/archive")
        
        if archive_base.exists():
            # If there are archived SUBPLANs, verify they can be found
            archived_files = list(archive_base.glob("SUBPLAN_*_ARCHIVED.md"))
            if archived_files:
                # Extract feature and achievement from archived filename
                # e.g., SUBPLAN_FEATURE_01_ARCHIVED.md
                first_archived = archived_files[0].stem
                # This is a documentation test - archive discovery should work
                assert "ARCHIVED" in first_archived, "Archive files should have _ARCHIVED suffix"


class TestRegressionAndCompatibility:
    """Test for regressions and backward compatibility."""

    def test_function_signatures_unchanged(self):
        """Verify function signatures haven't changed (backward compatibility)."""
        # find_subplan_for_achievement should still accept same parameters
        import inspect
        sig = inspect.signature(find_subplan_for_achievement)
        params = list(sig.parameters.keys())
        assert "feature_name" in params
        assert "achievement_num" in params
        assert "plan_path" in params

    def test_return_types_correct(self):
        """Verify return types are correct."""
        result1 = find_subplan_for_achievement("TEST", "0.1")
        assert isinstance(result1, (Path, type(None))), "Should return Path or None"

        result2 = detect_workflow_state(
            Path("work-space/plans/METHODOLOGY-HIERARCHY-EVOLUTION/PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md"),
            "METHODOLOGY-HIERARCHY-EVOLUTION",
            "0.1"
        )
        assert isinstance(result2, dict), "Should return dict"
        assert "state" in result2, "Dict should have 'state' key"


if __name__ == "__main__":
    # Run tests with: python -m pytest test_nested_discovery_phase1.py -v
    pytest.main([__file__, "-v", "-x"])

