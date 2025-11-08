#!/usr/bin/env python3
"""
Migration Validation Script

Validates that migration from flat to nested workspace structure completed successfully.

Checks:
- Folder structure is correct
- All files in right locations
- Cross-references are valid
- No files left in old locations
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple


class MigrationValidator:
    """Validates completed migrations"""

    def __init__(self, workspace_root="work-space"):
        self.workspace_root = Path(workspace_root)
        self.plans_dir = self.workspace_root / "plans"
        self.old_subplans_dir = self.workspace_root / "subplans"
        self.old_execution_dir = self.workspace_root / "execution"
        self.issues = []
        self.warnings = []
        self.info = []

    def validate_all_plans(self) -> Dict:
        """Validate all PLANs in new structure"""
        report = {
            "timestamp": Path.cwd().glob,
            "total_plans": 0,
            "valid_plans": 0,
            "issues": [],
            "warnings": [],
            "details": [],
        }

        if not self.plans_dir.exists():
            report["issues"].append("Plans directory does not exist")
            return report

        # Find all PLAN folders
        plan_folders = [d for d in self.plans_dir.iterdir() if d.is_dir()]
        report["total_plans"] = len(plan_folders)

        print(f"\n{'='*70}")
        print("MIGRATION VALIDATION")
        print(f"{'='*70}")
        print(f"Found {len(plan_folders)} PLAN folders\n")

        for plan_folder in sorted(plan_folders):
            print(f"Validating: {plan_folder.name}")
            is_valid, details = self.validate_plan(plan_folder)

            if is_valid:
                report["valid_plans"] += 1
                print(f"  ✅ Valid")
            else:
                print(f"  ❌ Issues found")

            report["details"].append(
                {"plan": plan_folder.name, "valid": is_valid, "details": details}
            )

        # Check for files in old locations
        print(f"\nChecking old locations for remaining files...")
        old_files = self._check_old_locations()
        if old_files:
            report["warnings"].append(f"Found {len(old_files)} files in old flat structure")
            for file in old_files:
                print(f"  ⚠️  {file}")

        report["issues"] = self.issues
        report["warnings"] = report["warnings"] + self.warnings

        return report

    def validate_plan(self, plan_folder: Path) -> Tuple[bool, Dict]:
        """Validate single PLAN folder"""
        details = {"folder": str(plan_folder), "checks": {}, "issues": []}

        is_valid = True

        # Check 1: Folder structure
        subplans_dir = plan_folder / "subplans"
        execution_dir = plan_folder / "execution"

        details["checks"]["structure"] = {
            "subplans_exists": subplans_dir.exists(),
            "execution_exists": execution_dir.exists(),
        }

        if not details["checks"]["structure"]["subplans_exists"]:
            details["issues"].append(f"Missing subplans/ folder")
            is_valid = False

        if not details["checks"]["structure"]["execution_exists"]:
            details["issues"].append(f"Missing execution/ folder")
            is_valid = False

        # Check 2: PLAN file exists
        plan_files = list(plan_folder.glob("PLAN_*.md"))
        details["checks"]["plan_file"] = len(plan_files) > 0

        if not details["checks"]["plan_file"]:
            details["issues"].append("No PLAN file found in root")
            is_valid = False
        elif len(plan_files) > 1:
            details["issues"].append(
                f"Multiple PLAN files found (expected 1, found {len(plan_files)})"
            )
            is_valid = False

        # Check 3: File counts
        subplan_count = len(list(subplans_dir.glob("*.md"))) if subplans_dir.exists() else 0
        execution_count = len(list(execution_dir.glob("*.md"))) if execution_dir.exists() else 0

        details["checks"]["file_counts"] = {
            "subplans": subplan_count,
            "executions": execution_count,
            "total": len(plan_files) + subplan_count + execution_count,
        }

        # Check 4: File naming conventions
        if subplans_dir.exists():
            for file in subplans_dir.glob("*.md"):
                if not file.name.startswith("SUBPLAN_"):
                    details["issues"].append(f"Invalid SUBPLAN name: {file.name}")
                    is_valid = False

        if execution_dir.exists():
            for file in execution_dir.glob("*.md"):
                if not file.name.startswith("EXECUTION_TASK_"):
                    details["issues"].append(f"Invalid EXECUTION_TASK name: {file.name}")
                    is_valid = False

        # Check 5: Cross-references (basic check)
        broken_refs = self._check_cross_references(plan_folder)
        if broken_refs:
            details["issues"].extend(broken_refs)
            is_valid = False

        return is_valid, details

    def _check_cross_references(self, plan_folder: Path) -> List[str]:
        """Check for broken cross-references in plan"""
        issues = []

        try:
            # Get all markdown files
            all_files = list(plan_folder.glob("**/*.md"))

            # Simple check: look for suspicious references
            for file in all_files:
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Check for references to old flat structure
                    if "work-space/subplans/" in content:
                        if not ("work-space/plans" in str(file)):
                            issues.append(
                                f"Possible broken reference in {file.relative_to(self.workspace_root)}"
                            )

                    if "work-space/execution/" in content:
                        if not ("work-space/plans" in str(file)):
                            issues.append(
                                f"Possible broken reference in {file.relative_to(self.workspace_root)}"
                            )

                except Exception as e:
                    issues.append(f"Error reading {file.name}: {str(e)}")

        except Exception as e:
            issues.append(f"Reference check error: {str(e)}")

        return issues

    def _check_old_locations(self) -> List[str]:
        """Check if files remain in old flat structure locations"""
        remaining = []

        # Check subplans directory
        if self.old_subplans_dir.exists():
            subplan_files = list(self.old_subplans_dir.glob("SUBPLAN_*.md"))
            remaining.extend([f"Old: {f.relative_to(self.workspace_root)}" for f in subplan_files])

        # Check execution directory
        if self.old_execution_dir.exists():
            exec_files = list(self.old_execution_dir.glob("EXECUTION_TASK_*.md"))
            remaining.extend([f"Old: {f.relative_to(self.workspace_root)}" for f in exec_files])

        return remaining

    def generate_report(self) -> str:
        """Generate validation report"""
        report = self.validate_all_plans()

        output = []
        output.append("\n" + "=" * 70)
        output.append("MIGRATION VALIDATION REPORT")
        output.append("=" * 70)
        output.append(f"Total PLANs Found:  {report['total_plans']}")
        output.append(f"Valid PLANs:        {report['valid_plans']}")
        output.append(f"Issues Found:       {len(report['issues'])}")
        output.append(f"Warnings:           {len(report['warnings'])}")
        output.append("=" * 70)

        # Detailed results
        output.append("\nDETAILED RESULTS:")
        for detail in report["details"]:
            status = "✅ VALID" if detail["valid"] else "❌ INVALID"
            output.append(f"\n{detail['plan']}: {status}")

            if detail["details"]["checks"]:
                output.append("  Checks:")
                for check, result in detail["details"]["checks"].items():
                    if isinstance(result, dict):
                        for k, v in result.items():
                            output.append(f"    • {k}: {v}")
                    else:
                        output.append(f"    • {check}: {result}")

            if detail["details"]["issues"]:
                output.append("  Issues:")
                for issue in detail["details"]["issues"]:
                    output.append(f"    ⚠️  {issue}")

        # Issues summary
        if report["issues"]:
            output.append("\n" + "-" * 70)
            output.append("ALL ISSUES:")
            for issue in report["issues"]:
                output.append(f"  • {issue}")

        if report["warnings"]:
            output.append("\n" + "-" * 70)
            output.append("ALL WARNINGS:")
            for warning in report["warnings"]:
                output.append(f"  • {warning}")

        output.append("\n" + "=" * 70)

        if report["valid_plans"] == report["total_plans"] and not report["issues"]:
            output.append("✅ MIGRATION VALIDATION PASSED")
        else:
            output.append("❌ MIGRATION VALIDATION FAILED")

        output.append("=" * 70 + "\n")

        return "\n".join(output)


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate workspace migration to nested structure")
    parser.add_argument(
        "--workspace", default="work-space", help="Path to workspace root (default: work-space)"
    )

    args = parser.parse_args()

    validator = MigrationValidator(args.workspace)
    report = validator.generate_report()
    print(report)

    # Return non-zero if validation failed
    validation_result = validator.validate_all_plans()
    if (
        validation_result["issues"]
        or len(validation_result["valid_plans"]) != validation_result["total_plans"]
    ):
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
