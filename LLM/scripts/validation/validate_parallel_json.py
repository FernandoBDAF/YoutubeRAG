#!/usr/bin/env python3
"""
Validation Script for parallel.json Files

This script validates parallel.json files for structural integrity and
dependency correctness. It performs schema validation and circular dependency
detection.

Usage:
    python validate_parallel_json.py <parallel.json>
    python validate_parallel_json.py <parallel.json> --verbose

Created: 2025-11-13
Achievement: 1.3 - Validation Script Created
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set


@dataclass
class ValidationResult:
    """Result of parallel.json validation."""

    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    cycles: List[List[str]] = field(default_factory=list)

    def __str__(self) -> str:
        """Format validation result as string."""
        lines = []

        if self.valid:
            lines.append("✅ Validation passed!")
        else:
            lines.append("❌ Validation failed!")

            if self.errors:
                lines.append(f"\nErrors ({len(self.errors)}):")
                for error in self.errors:
                    lines.append(f"  - {error}")

            if self.cycles:
                lines.append(f"\nCircular Dependencies ({len(self.cycles)}):")
                for cycle in self.cycles:
                    cycle_str = " → ".join(cycle)
                    lines.append(f"  - {cycle_str}")

            if self.warnings:
                lines.append(f"\nWarnings ({len(self.warnings)}):")
                for warning in self.warnings:
                    lines.append(f"  - {warning}")

        return "\n".join(lines)


def validate_schema(data: Dict) -> List[str]:
    """
    Validate parallel.json against schema requirements.

    Args:
        data: Loaded parallel.json data

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Check required fields
    required_fields = ["plan_name", "parallelization_level", "achievements"]
    for field_name in required_fields:
        if field_name not in data:
            errors.append(
                f"Missing required field: '{field_name}'. " f"Add this field to your parallel.json."
            )

    # Validate parallelization_level enum
    if "parallelization_level" in data:
        valid_levels = ["level_1", "level_2", "level_3"]
        level = data["parallelization_level"]
        if level not in valid_levels:
            errors.append(
                f"Invalid parallelization_level: '{level}'. "
                f"Must be one of: {', '.join(valid_levels)}. "
                f"Fix: Change to 'level_1', 'level_2', or 'level_3'."
            )

    # Validate achievements array
    if "achievements" in data:
        if not isinstance(data["achievements"], list):
            errors.append(
                "Field 'achievements' must be an array. "
                "Fix: Change achievements to a JSON array: []"
            )
        else:
            # Validate each achievement
            for i, ach in enumerate(data["achievements"]):
                if not isinstance(ach, dict):
                    errors.append(f"Achievement {i}: Must be an object, not {type(ach).__name__}")
                    continue

                # Validate achievement_id
                if "achievement_id" not in ach:
                    errors.append(
                        f"Achievement {i}: Missing required field 'achievement_id'. "
                        f'Add: "achievement_id": "X.Y"'
                    )
                else:
                    ach_id = ach["achievement_id"]
                    if not re.match(r"^\d+\.\d+$", str(ach_id)):
                        errors.append(
                            f"Achievement {i}: Invalid achievement_id format: '{ach_id}'. "
                            f"Must match pattern X.Y (e.g., '1.1', '2.3'). "
                            f"Fix: Change to format like '1.1' or '2.3'."
                        )

                # Validate status enum (if present)
                if "status" in ach:
                    valid_statuses = [
                        "not_started",
                        "subplan_created",
                        "execution_created",
                        "in_progress",
                        "complete",
                        "failed",
                        "skipped",
                    ]
                    status = ach["status"]
                    if status not in valid_statuses:
                        errors.append(
                            f"Achievement {ach.get('achievement_id', i)}: "
                            f"Invalid status: '{status}'. "
                            f"Must be one of: {', '.join(valid_statuses)}"
                        )

                # Validate dependencies
                if "dependencies" not in ach:
                    errors.append(
                        f"Achievement {ach.get('achievement_id', i)}: "
                        f"Missing required field 'dependencies'. "
                        f'Add: "dependencies": [] (or list of dependency IDs)'
                    )
                elif not isinstance(ach["dependencies"], list):
                    errors.append(
                        f"Achievement {ach.get('achievement_id', i)}: "
                        f"Field 'dependencies' must be an array. "
                        f"Fix: Change to JSON array: []"
                    )
                else:
                    # Validate each dependency ID format
                    for dep in ach["dependencies"]:
                        if not re.match(r"^\d+\.\d+$", str(dep)):
                            errors.append(
                                f"Achievement {ach.get('achievement_id', i)}: "
                                f"Invalid dependency ID format: '{dep}'. "
                                f"Must match pattern X.Y (e.g., '1.1', '2.3')."
                            )

    return errors


def check_circular_dependencies(achievements: List[Dict]) -> List[List[str]]:
    """
    Detect circular dependencies using depth-first search.

    Args:
        achievements: List of achievement objects

    Returns:
        List of cycles found (each cycle is a list of achievement IDs)
    """
    # Build adjacency list (graph)
    graph = {}
    for ach in achievements:
        if "achievement_id" in ach and "dependencies" in ach:
            ach_id = ach["achievement_id"]
            deps = ach.get("dependencies", [])
            graph[ach_id] = deps

    # DFS to detect cycles
    cycles = []
    visited = set()
    rec_stack = set()

    def dfs(node: str, path: List[str]):
        """Depth-first search to detect cycles."""
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, path.copy())
            elif neighbor in rec_stack:
                # Found cycle - extract the cycle from path
                try:
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    # Avoid duplicate cycles
                    if cycle not in cycles and list(reversed(cycle)) not in cycles:
                        cycles.append(cycle)
                except ValueError:
                    # neighbor not in path (shouldn't happen, but handle gracefully)
                    pass

        rec_stack.remove(node)

    # Run DFS from each unvisited node
    for node in graph:
        if node not in visited:
            dfs(node, [])

    return cycles


def validate_dependency_existence(achievements: List[Dict]) -> List[str]:
    """
    Validate that all dependency IDs exist in achievements list.

    Args:
        achievements: List of achievement objects

    Returns:
        List of error messages for missing dependencies
    """
    errors = []

    # Collect all achievement IDs
    achievement_ids = {ach["achievement_id"] for ach in achievements if "achievement_id" in ach}

    # Check each dependency
    for ach in achievements:
        if "achievement_id" not in ach or "dependencies" not in ach:
            continue

        ach_id = ach["achievement_id"]
        for dep in ach["dependencies"]:
            if dep not in achievement_ids:
                errors.append(
                    f"Achievement {ach_id}: Dependency '{dep}' not found in achievements list. "
                    f"Fix: Add achievement {dep} or remove this dependency."
                )

    return errors


def validate_parallel_json(file_path: Path) -> ValidationResult:
    """
    Validate parallel.json file.

    Performs:
    - Schema validation (required fields, types, formats)
    - Circular dependency detection
    - Dependency existence validation

    Args:
        file_path: Path to parallel.json file

    Returns:
        ValidationResult with errors, warnings, and detected cycles
    """
    errors = []
    warnings = []
    cycles = []

    # Check file exists
    if not file_path.exists():
        return ValidationResult(
            valid=False, errors=[f"File not found: {file_path}"], warnings=[], cycles=[]
        )

    # Load JSON
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return ValidationResult(
            valid=False,
            errors=[
                f"Invalid JSON: {e.msg} at line {e.lineno}, column {e.colno}. "
                f"Fix: Check JSON syntax (missing comma, bracket, quote, etc.)"
            ],
            warnings=[],
            cycles=[],
        )
    except Exception as e:
        return ValidationResult(
            valid=False, errors=[f"Error reading file: {str(e)}"], warnings=[], cycles=[]
        )

    # Schema validation
    schema_errors = validate_schema(data)
    errors.extend(schema_errors)

    # Only proceed with dependency checks if achievements exist and are valid
    if "achievements" in data and isinstance(data["achievements"], list):
        # Circular dependency detection
        cycles = check_circular_dependencies(data["achievements"])
        if cycles:
            for cycle in cycles:
                cycle_str = " → ".join(cycle)
                errors.append(
                    f"Circular dependency detected: {cycle_str}. "
                    f"Fix: Remove one of the dependencies to break the cycle."
                )

        # Dependency existence validation
        dep_errors = validate_dependency_existence(data["achievements"])
        errors.extend(dep_errors)

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings, cycles=cycles)


def main():
    """CLI interface for validation."""
    parser = argparse.ArgumentParser(
        description="Validate parallel.json file structure and dependencies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s parallel.json
  %(prog)s examples/parallel_level1_example.json
  %(prog)s parallel.json --verbose

Exit codes:
  0 - Validation passed
  1 - Validation failed
        """,
    )
    parser.add_argument("parallel_json", type=Path, help="Path to parallel.json file")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed validation information"
    )

    args = parser.parse_args()

    # Validate
    result = validate_parallel_json(args.parallel_json)

    # Output
    print(result)

    if args.verbose and result.valid:
        print("\nValidation checks passed:")
        print("  ✓ Schema validation (required fields, types, formats)")
        print("  ✓ Circular dependency detection")
        print("  ✓ Dependency existence validation")

    # Exit with appropriate code
    return 0 if result.valid else 1


if __name__ == "__main__":
    sys.exit(main())
