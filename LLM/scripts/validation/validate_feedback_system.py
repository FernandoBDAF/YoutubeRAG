#!/usr/bin/env python3
"""
Feedback System Validation Script

Validates that a PLAN's feedback system follows conventions:
- APPROVED_XX.md naming format
- Files in execution/feedbacks/ location
- Achievement Index alignment with filesystem
- No orphaned files or missing files

Created: 2025-11-12
Achievement: 2.5 - Codify Feedback System Patterns
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Set


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""

    severity: str  # 'error', 'warning', 'info'
    category: str  # 'naming', 'location', 'alignment', 'orphan', 'missing'
    message: str
    resolution: str
    file: str = ""


@dataclass
class ValidationResult:
    """Results of validation run."""

    passed: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)


class FeedbackSystemValidator:
    """Validates feedback system conventions for a PLAN."""

    def __init__(self, plan_path: Path):
        """
        Initialize validator for a PLAN.

        Args:
            plan_path: Path to PLAN file or PLAN directory
        """
        if plan_path.is_file():
            self.plan_dir = plan_path.parent
            self.plan_file = plan_path
        else:
            self.plan_dir = plan_path
            # Find PLAN file
            plan_files = list(plan_path.glob("PLAN_*.md"))
            if not plan_files:
                raise ValueError(f"No PLAN file found in {plan_path}")
            self.plan_file = plan_files[0]

        self.feedbacks_dir = self.plan_dir / "execution" / "feedbacks"

    def validate(self) -> ValidationResult:
        """
        Run all validation checks.

        Returns:
            ValidationResult with issues and stats
        """
        issues = []

        # Check if feedback structure exists
        if not self.feedbacks_dir.exists():
            issues.append(
                ValidationIssue(
                    severity="error",
                    category="structure",
                    message="Feedback directory does not exist",
                    resolution=f"Create directory: {self.feedbacks_dir}",
                    file=str(self.feedbacks_dir),
                )
            )
            # Can't continue without feedback directory
            return ValidationResult(
                passed=False, issues=issues, stats={"total_issues": len(issues), "errors": 1}
            )

        # Run all validation checks
        issues.extend(self.check_naming_conventions())
        issues.extend(self.check_file_locations())
        issues.extend(self.check_achievement_index_alignment())
        issues.extend(self.check_for_orphans())

        # Calculate stats
        stats = self._calculate_stats(issues)

        # Determine if validation passed (no errors)
        passed = stats.get("errors", 0) == 0

        return ValidationResult(passed=passed, issues=issues, stats=stats)

    def check_naming_conventions(self) -> List[ValidationIssue]:
        """
        Check that all feedback files follow APPROVED_XX.md naming convention.

        Returns:
            List of issues found
        """
        issues = []

        if not self.feedbacks_dir.exists():
            return issues

        # Pattern: APPROVED_XX.md where XX is digits (can be 1-2 digits)
        valid_pattern = re.compile(r"^APPROVED_\d{1,2}\.md$")

        for file in self.feedbacks_dir.iterdir():
            if file.is_file() and file.suffix == ".md":
                if not valid_pattern.match(file.name):
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            category="naming",
                            message=f"Invalid filename format: {file.name}",
                            resolution="Rename to APPROVED_XX.md format (e.g., APPROVED_11.md for Achievement 1.1)",
                            file=str(file),
                        )
                    )

        return issues

    def check_file_locations(self) -> List[ValidationIssue]:
        """
        Check that feedback files are in correct location (execution/feedbacks/).

        Returns:
            List of issues found
        """
        issues = []

        # Check for APPROVED files in wrong locations
        wrong_locations = [
            self.plan_dir,  # Root of plan
            self.plan_dir / "execution",  # execution/ but not feedbacks/
            self.plan_dir / "feedbacks",  # feedbacks/ but not in execution/
        ]

        for location in wrong_locations:
            if location.exists():
                for file in location.iterdir():
                    if file.is_file() and file.name.startswith("APPROVED_"):
                        issues.append(
                            ValidationIssue(
                                severity="error",
                                category="location",
                                message=f"APPROVED file in wrong location: {file}",
                                resolution=f"Move to {self.feedbacks_dir}",
                                file=str(file),
                            )
                        )

        return issues

    def check_achievement_index_alignment(self) -> List[ValidationIssue]:
        """
        Check that Achievement Index matches filesystem completions.

        Returns:
            List of issues found
        """
        issues = []

        # Parse Achievement Index from PLAN
        index_achievements = self._parse_achievement_index()

        # Get completed achievements from filesystem
        completed_achievements = self._get_completed_achievements()

        # Find achievements in Index that aren't complete
        for ach in index_achievements:
            if ach not in completed_achievements:
                issues.append(
                    ValidationIssue(
                        severity="info",
                        category="alignment",
                        message=f"Achievement {ach} in Index but not complete (no APPROVED file)",
                        resolution="This is OK if achievement is still in progress",
                        file="",
                    )
                )

        return issues

    def check_for_orphans(self) -> List[ValidationIssue]:
        """
        Check for orphaned APPROVED files (not in Achievement Index).

        Returns:
            List of issues found
        """
        issues = []

        # Parse Achievement Index from PLAN
        index_achievements = self._parse_achievement_index()

        # Get completed achievements from filesystem
        completed_achievements = self._get_completed_achievements()

        # Find APPROVED files that aren't in Index
        for ach in completed_achievements:
            if ach not in index_achievements:
                file_name = self._achievement_to_filename(ach)
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        category="orphan",
                        message=f"APPROVED file for Achievement {ach} but not in Index",
                        resolution="Add Achievement {ach} to Achievement Index or remove orphaned file",
                        file=str(self.feedbacks_dir / file_name),
                    )
                )

        return issues

    def _parse_achievement_index(self) -> Set[str]:
        """
        Parse Achievement Index from PLAN file.

        Returns:
            Set of achievement numbers (e.g., {"0.1", "0.2", "1.1"})
        """
        achievements = set()

        try:
            content = self.plan_file.read_text()

            # Find Achievement Index section
            index_match = re.search(
                r"## (?:📋 )?Achievement Index.*?(?=\n##|\Z)", content, re.DOTALL
            )

            if not index_match:
                return achievements

            index_section = index_match.group(0)

            # Find all achievement patterns
            # Patterns: "Achievement 1.1", "- Achievement 1.1", "✅ Achievement 1.1"
            patterns = [
                r"Achievement\s+(\d+\.\d+)",
                r"-\s+.*?Achievement\s+(\d+\.\d+)",
                r"✅\s+Achievement\s+(\d+\.\d+)",
            ]

            for pattern in patterns:
                matches = re.findall(pattern, index_section)
                achievements.update(matches)

        except Exception as e:
            print(f"Warning: Could not parse Achievement Index: {e}")

        return achievements

    def _get_completed_achievements(self) -> Set[str]:
        """
        Get completed achievements from filesystem (APPROVED_XX.md files).

        Returns:
            Set of achievement numbers (e.g., {"0.1", "0.2", "1.1"})
        """
        achievements = set()

        if not self.feedbacks_dir.exists():
            return achievements

        pattern = re.compile(r"^APPROVED_(\d{1,2})\.md$")

        for file in self.feedbacks_dir.iterdir():
            if file.is_file():
                match = pattern.match(file.name)
                if match:
                    # Convert filename number to achievement format
                    # APPROVED_11.md -> "1.1", APPROVED_24.md -> "2.4"
                    num_str = match.group(1)
                    if len(num_str) == 1:
                        ach_num = f"0.{num_str}"
                    else:
                        ach_num = f"{num_str[0]}.{num_str[1]}"
                    achievements.add(ach_num)

        return achievements

    def _achievement_to_filename(self, ach_num: str) -> str:
        """
        Convert achievement number to filename.

        Args:
            ach_num: Achievement number (e.g., "1.1")

        Returns:
            Filename (e.g., "APPROVED_11.md")
        """
        # Remove dot: "1.1" -> "11"
        num_part = ach_num.replace(".", "")
        return f"APPROVED_{num_part}.md"

    def _calculate_stats(self, issues: List[ValidationIssue]) -> Dict[str, int]:
        """
        Calculate statistics from issues.

        Args:
            issues: List of validation issues

        Returns:
            Dictionary of stats
        """
        stats = {
            "total_issues": len(issues),
            "errors": sum(1 for i in issues if i.severity == "error"),
            "warnings": sum(1 for i in issues if i.severity == "warning"),
            "info": sum(1 for i in issues if i.severity == "info"),
        }

        # Count by category
        for issue in issues:
            key = f"{issue.category}_issues"
            stats[key] = stats.get(key, 0) + 1

        return stats


def format_validation_report(result: ValidationResult) -> str:
    """
    Format validation result as readable report.

    Args:
        result: ValidationResult to format

    Returns:
        Formatted report string
    """
    lines = []

    # Header
    if result.passed:
        lines.append("✅ VALIDATION PASSED")
    else:
        lines.append("❌ VALIDATION FAILED")

    lines.append("")
    lines.append("=" * 70)

    # Stats
    lines.append("📊 SUMMARY:")
    lines.append(f"   Total Issues: {result.stats.get('total_issues', 0)}")
    lines.append(f"   Errors:       {result.stats.get('errors', 0)}")
    lines.append(f"   Warnings:     {result.stats.get('warnings', 0)}")
    lines.append(f"   Info:         {result.stats.get('info', 0)}")
    lines.append("")

    # Issues by severity
    if result.issues:
        lines.append("=" * 70)
        lines.append("🔍 ISSUES FOUND:")
        lines.append("")

        # Group by severity
        for severity in ["error", "warning", "info"]:
            severity_issues = [i for i in result.issues if i.severity == severity]
            if severity_issues:
                icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}[severity]
                lines.append(f"{icon} {severity.upper()}S ({len(severity_issues)}):")
                lines.append("")

                for issue in severity_issues:
                    lines.append(f"  • {issue.message}")
                    if issue.file:
                        lines.append(f"    File: {issue.file}")
                    lines.append(f"    Resolution: {issue.resolution}")
                    lines.append("")

    else:
        lines.append("✅ No issues found!")

    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate feedback system conventions for a PLAN",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a PLAN directory
  python3 validate_feedback_system.py work-space/plans/FEATURE/

  # Validate a specific PLAN file
  python3 validate_feedback_system.py work-space/plans/FEATURE/PLAN_FEATURE.md

  # Validate all plans
  for plan in work-space/plans/*/; do
    python3 validate_feedback_system.py "$plan"
  done
        """,
    )

    parser.add_argument("plan_path", type=Path, help="Path to PLAN file or PLAN directory")

    parser.add_argument(
        "--quiet", action="store_true", help="Only show summary, not detailed issues"
    )

    args = parser.parse_args()

    # Validate plan path
    if not args.plan_path.exists():
        print(f"❌ Error: Path not found: {args.plan_path}")
        sys.exit(1)

    # Run validation
    try:
        validator = FeedbackSystemValidator(args.plan_path)
        result = validator.validate()

        # Print report
        report = format_validation_report(result)
        print(report)

        # Exit with appropriate code
        sys.exit(0 if result.passed else 1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
