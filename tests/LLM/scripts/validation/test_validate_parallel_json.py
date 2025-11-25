"""
Tests for parallel.json validation and status detection scripts.

Tests cover:
- Schema validation (required fields, types, formats)
- Circular dependency detection
- Status detection from filesystem
- Error message quality

Created: 2025-11-13
Achievement: 1.3 - Validation Script Created
"""

import json
import pytest
from pathlib import Path
from LLM.scripts.validation.validate_parallel_json import (
    validate_schema,
    check_circular_dependencies,
    validate_dependency_existence,
    validate_parallel_json,
    ValidationResult,
)
from LLM.scripts.validation.get_parallel_status import (
    get_achievement_status_from_filesystem,
    get_parallel_status,
    enrich_parallel_json_with_status,
)


# ============================================================================
# Schema Validation Tests
# ============================================================================


class TestSchemaValidation:
    """Test schema validation logic."""

    def test_valid_level1_json(self):
        """Test valid level 1 parallel.json."""
        data = {
            "plan_name": "TEST-PLAN",
            "parallelization_level": "level_1",
            "achievements": [
                {"achievement_id": "1.1", "dependencies": [], "status": "not_started"}
            ],
        }
        errors = validate_schema(data)
        assert len(errors) == 0

    def test_valid_level2_json(self):
        """Test valid level 2 parallel.json."""
        data = {
            "plan_name": "TEST-PLAN",
            "parallelization_level": "level_2",
            "achievements": [
                {"achievement_id": "3.1", "dependencies": ["2.2"], "status": "not_started"}
            ],
        }
        errors = validate_schema(data)
        assert len(errors) == 0

    def test_valid_level3_json(self):
        """Test valid level 3 parallel.json."""
        data = {
            "plan_name": "TEST-PLAN",
            "parallelization_level": "level_3",
            "achievements": [
                {"achievement_id": "1.1", "dependencies": [], "status": "not_started"},
                {"achievement_id": "2.1", "dependencies": ["1.1"], "status": "not_started"},
            ],
        }
        errors = validate_schema(data)
        assert len(errors) == 0

    def test_missing_plan_name(self):
        """Test missing plan_name field."""
        data = {"parallelization_level": "level_1", "achievements": []}
        errors = validate_schema(data)
        assert any("plan_name" in e for e in errors)

    def test_missing_parallelization_level(self):
        """Test missing parallelization_level field."""
        data = {"plan_name": "TEST-PLAN", "achievements": []}
        errors = validate_schema(data)
        assert any("parallelization_level" in e for e in errors)

    def test_missing_achievements(self):
        """Test missing achievements field."""
        data = {"plan_name": "TEST-PLAN", "parallelization_level": "level_1"}
        errors = validate_schema(data)
        assert any("achievements" in e for e in errors)

    def test_invalid_parallelization_level(self):
        """Test invalid parallelization_level value."""
        data = {"plan_name": "TEST-PLAN", "parallelization_level": "invalid", "achievements": []}
        errors = validate_schema(data)
        assert any("parallelization_level" in e and "invalid" in e for e in errors)

    def test_achievements_not_array(self):
        """Test achievements field not an array."""
        data = {
            "plan_name": "TEST-PLAN",
            "parallelization_level": "level_1",
            "achievements": "not an array",
        }
        errors = validate_schema(data)
        assert any("achievements" in e and "array" in e for e in errors)

    def test_missing_achievement_id(self):
        """Test achievement missing achievement_id."""
        data = {
            "plan_name": "TEST-PLAN",
            "parallelization_level": "level_1",
            "achievements": [{"dependencies": []}],
        }
        errors = validate_schema(data)
        assert any("achievement_id" in e for e in errors)

    def test_invalid_achievement_id_format(self):
        """Test invalid achievement_id format."""
        data = {
            "plan_name": "TEST-PLAN",
            "parallelization_level": "level_1",
            "achievements": [{"achievement_id": "invalid", "dependencies": []}],
        }
        errors = validate_schema(data)
        assert any("achievement_id" in e and "format" in e for e in errors)

    def test_missing_dependencies(self):
        """Test achievement missing dependencies field."""
        data = {
            "plan_name": "TEST-PLAN",
            "parallelization_level": "level_1",
            "achievements": [{"achievement_id": "1.1"}],
        }
        errors = validate_schema(data)
        assert any("dependencies" in e for e in errors)

    def test_dependencies_not_array(self):
        """Test dependencies field not an array."""
        data = {
            "plan_name": "TEST-PLAN",
            "parallelization_level": "level_1",
            "achievements": [{"achievement_id": "1.1", "dependencies": "not an array"}],
        }
        errors = validate_schema(data)
        assert any("dependencies" in e and "array" in e for e in errors)

    def test_invalid_dependency_id_format(self):
        """Test invalid dependency ID format."""
        data = {
            "plan_name": "TEST-PLAN",
            "parallelization_level": "level_1",
            "achievements": [{"achievement_id": "1.1", "dependencies": ["invalid"]}],
        }
        errors = validate_schema(data)
        assert any("dependency" in e.lower() and "format" in e for e in errors)

    def test_invalid_status_value(self):
        """Test invalid status enum value."""
        data = {
            "plan_name": "TEST-PLAN",
            "parallelization_level": "level_1",
            "achievements": [
                {"achievement_id": "1.1", "dependencies": [], "status": "invalid_status"}
            ],
        }
        errors = validate_schema(data)
        assert any("status" in e and "invalid_status" in e for e in errors)


# ============================================================================
# Circular Dependency Tests
# ============================================================================


class TestCircularDependencies:
    """Test circular dependency detection."""

    def test_no_dependencies(self):
        """Test achievements with no dependencies."""
        achievements = [
            {"achievement_id": "1.1", "dependencies": []},
            {"achievement_id": "1.2", "dependencies": []},
        ]
        cycles = check_circular_dependencies(achievements)
        assert len(cycles) == 0

    def test_linear_dependencies(self):
        """Test linear dependency chain (no cycle)."""
        achievements = [
            {"achievement_id": "1.1", "dependencies": []},
            {"achievement_id": "1.2", "dependencies": ["1.1"]},
            {"achievement_id": "1.3", "dependencies": ["1.2"]},
        ]
        cycles = check_circular_dependencies(achievements)
        assert len(cycles) == 0

    def test_simple_cycle(self):
        """Test simple cycle: A→B→A."""
        achievements = [
            {"achievement_id": "1.1", "dependencies": ["1.2"]},
            {"achievement_id": "1.2", "dependencies": ["1.1"]},
        ]
        cycles = check_circular_dependencies(achievements)
        assert len(cycles) > 0
        # Check cycle contains both 1.1 and 1.2
        assert any("1.1" in cycle and "1.2" in cycle for cycle in cycles)

    def test_complex_cycle(self):
        """Test complex cycle: A→B→C→A."""
        achievements = [
            {"achievement_id": "1.1", "dependencies": ["1.2"]},
            {"achievement_id": "1.2", "dependencies": ["1.3"]},
            {"achievement_id": "1.3", "dependencies": ["1.1"]},
        ]
        cycles = check_circular_dependencies(achievements)
        assert len(cycles) > 0
        # Check cycle contains all three
        assert any("1.1" in cycle and "1.2" in cycle and "1.3" in cycle for cycle in cycles)

    def test_self_dependency(self):
        """Test self-dependency: A→A."""
        achievements = [{"achievement_id": "1.1", "dependencies": ["1.1"]}]
        cycles = check_circular_dependencies(achievements)
        assert len(cycles) > 0
        assert any("1.1" in cycle for cycle in cycles)

    def test_multiple_independent_chains(self):
        """Test multiple independent dependency chains (no cycles)."""
        achievements = [
            {"achievement_id": "1.1", "dependencies": []},
            {"achievement_id": "1.2", "dependencies": ["1.1"]},
            {"achievement_id": "2.1", "dependencies": []},
            {"achievement_id": "2.2", "dependencies": ["2.1"]},
        ]
        cycles = check_circular_dependencies(achievements)
        assert len(cycles) == 0

    def test_partial_cycle(self):
        """Test graph with both cycle and non-cycle parts."""
        achievements = [
            {"achievement_id": "1.1", "dependencies": []},
            {"achievement_id": "1.2", "dependencies": ["1.1"]},
            {"achievement_id": "2.1", "dependencies": ["2.2"]},
            {"achievement_id": "2.2", "dependencies": ["2.1"]},
        ]
        cycles = check_circular_dependencies(achievements)
        assert len(cycles) > 0
        # Cycle should only contain 2.1 and 2.2
        assert any("2.1" in cycle and "2.2" in cycle for cycle in cycles)


# ============================================================================
# Dependency Existence Tests
# ============================================================================


class TestDependencyExistence:
    """Test dependency existence validation."""

    def test_all_dependencies_exist(self):
        """Test all dependencies exist in achievements list."""
        achievements = [
            {"achievement_id": "1.1", "dependencies": []},
            {"achievement_id": "1.2", "dependencies": ["1.1"]},
            {"achievement_id": "1.3", "dependencies": ["1.1", "1.2"]},
        ]
        errors = validate_dependency_existence(achievements)
        assert len(errors) == 0

    def test_missing_dependency(self):
        """Test dependency not in achievements list."""
        achievements = [{"achievement_id": "1.1", "dependencies": ["2.1"]}]
        errors = validate_dependency_existence(achievements)
        assert len(errors) > 0
        assert any("2.1" in e and "not found" in e for e in errors)

    def test_multiple_missing_dependencies(self):
        """Test multiple missing dependencies."""
        achievements = [{"achievement_id": "1.1", "dependencies": ["2.1", "2.2", "2.3"]}]
        errors = validate_dependency_existence(achievements)
        assert len(errors) == 3


# ============================================================================
# Integration Tests
# ============================================================================


class TestValidateParallelJson:
    """Test full validation function."""

    def test_valid_file(self, tmp_path):
        """Test validation of valid parallel.json file."""
        # Create valid parallel.json
        parallel_json = tmp_path / "parallel.json"
        data = {
            "plan_name": "TEST-PLAN",
            "parallelization_level": "level_1",
            "achievements": [{"achievement_id": "1.1", "dependencies": []}],
        }
        parallel_json.write_text(json.dumps(data))

        result = validate_parallel_json(parallel_json)
        assert result.valid
        assert len(result.errors) == 0

    def test_file_not_found(self, tmp_path):
        """Test validation of non-existent file."""
        parallel_json = tmp_path / "nonexistent.json"
        result = validate_parallel_json(parallel_json)
        assert not result.valid
        assert any("not found" in e.lower() for e in result.errors)

    def test_malformed_json(self, tmp_path):
        """Test validation of malformed JSON."""
        parallel_json = tmp_path / "parallel.json"
        parallel_json.write_text("{invalid json")

        result = validate_parallel_json(parallel_json)
        assert not result.valid
        assert any("json" in e.lower() for e in result.errors)

    def test_file_with_cycle(self, tmp_path):
        """Test validation detects circular dependency."""
        parallel_json = tmp_path / "parallel.json"
        data = {
            "plan_name": "TEST-PLAN",
            "parallelization_level": "level_1",
            "achievements": [
                {"achievement_id": "1.1", "dependencies": ["1.2"]},
                {"achievement_id": "1.2", "dependencies": ["1.1"]},
            ],
        }
        parallel_json.write_text(json.dumps(data))

        result = validate_parallel_json(parallel_json)
        assert not result.valid
        assert len(result.cycles) > 0
        assert any("circular" in e.lower() for e in result.errors)


# ============================================================================
# Status Detection Tests
# ============================================================================


class TestStatusDetection:
    """Test status detection from filesystem."""

    def test_not_started_status(self, tmp_path):
        """Test not_started status (no files exist)."""
        status = get_achievement_status_from_filesystem("1.1", "TEST-PLAN", tmp_path)
        assert status == "not_started"

    def test_subplan_created_status(self, tmp_path):
        """Test subplan_created status."""
        # Create SUBPLAN file
        plan_dir = tmp_path / "work-space" / "plans" / "TEST-PLAN" / "subplans"
        plan_dir.mkdir(parents=True)
        (plan_dir / "SUBPLAN_TEST-PLAN_11.md").touch()

        status = get_achievement_status_from_filesystem("1.1", "TEST-PLAN", tmp_path)
        assert status == "subplan_created"

    def test_execution_created_status(self, tmp_path):
        """Test execution_created status."""
        # Create EXECUTION_TASK file
        exec_dir = tmp_path / "work-space" / "plans" / "TEST-PLAN" / "execution"
        exec_dir.mkdir(parents=True)
        (exec_dir / "EXECUTION_TASK_TEST-PLAN_11_01.md").touch()

        status = get_achievement_status_from_filesystem("1.1", "TEST-PLAN", tmp_path)
        assert status == "execution_created"

    def test_complete_status(self, tmp_path):
        """Test complete status (APPROVED file exists)."""
        # Create APPROVED file
        feedback_dir = tmp_path / "work-space" / "plans" / "TEST-PLAN" / "execution" / "feedbacks"
        feedback_dir.mkdir(parents=True)
        (feedback_dir / "APPROVED_11.md").touch()

        status = get_achievement_status_from_filesystem("1.1", "TEST-PLAN", tmp_path)
        assert status == "complete"

    def test_failed_status(self, tmp_path):
        """Test failed status (FIX file exists)."""
        # Create FIX file
        feedback_dir = tmp_path / "work-space" / "plans" / "TEST-PLAN" / "execution" / "feedbacks"
        feedback_dir.mkdir(parents=True)
        (feedback_dir / "FIX_11.md").touch()

        status = get_achievement_status_from_filesystem("1.1", "TEST-PLAN", tmp_path)
        assert status == "failed"

    def test_skipped_status(self, tmp_path):
        """Test skipped status."""
        # Create SKIPPED file
        exec_dir = tmp_path / "work-space" / "plans" / "TEST-PLAN" / "execution"
        exec_dir.mkdir(parents=True)
        (exec_dir / "SKIPPED_11.md").touch()

        status = get_achievement_status_from_filesystem("1.1", "TEST-PLAN", tmp_path)
        assert status == "skipped"

    def test_status_priority_complete_over_failed(self, tmp_path):
        """Test that complete status takes priority over failed."""
        # Create both APPROVED and FIX files
        feedback_dir = tmp_path / "work-space" / "plans" / "TEST-PLAN" / "execution" / "feedbacks"
        feedback_dir.mkdir(parents=True)
        (feedback_dir / "APPROVED_11.md").touch()
        (feedback_dir / "FIX_11.md").touch()

        status = get_achievement_status_from_filesystem("1.1", "TEST-PLAN", tmp_path)
        # APPROVED takes priority
        assert status == "complete"

    def test_get_parallel_status(self, tmp_path):
        """Test getting status for all achievements in parallel.json."""
        # Create parallel.json
        parallel_json = tmp_path / "parallel.json"
        data = {
            "plan_name": "TEST-PLAN",
            "parallelization_level": "level_1",
            "achievements": [
                {"achievement_id": "1.1", "dependencies": []},
                {"achievement_id": "1.2", "dependencies": []},
            ],
        }
        parallel_json.write_text(json.dumps(data))

        # Create SUBPLAN for 1.1
        plan_dir = tmp_path / "work-space" / "plans" / "TEST-PLAN" / "subplans"
        plan_dir.mkdir(parents=True)
        (plan_dir / "SUBPLAN_TEST-PLAN_11.md").touch()

        status_map = get_parallel_status(parallel_json)
        assert status_map["1.1"] == "subplan_created"
        assert status_map["1.2"] == "not_started"

    def test_enrich_parallel_json(self, tmp_path):
        """Test enriching parallel.json with status."""
        data = {
            "plan_name": "TEST-PLAN",
            "achievements": [{"achievement_id": "1.1", "dependencies": []}],
        }

        enriched = enrich_parallel_json_with_status(data, tmp_path)
        assert "status" in enriched["achievements"][0]
        assert enriched["achievements"][0]["status"] == "not_started"
