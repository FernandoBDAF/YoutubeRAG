#!/usr/bin/env python3
"""
Legacy Plan Migration Script

Migrates old plans to use the feedback system:
- Creates execution/feedbacks/ structure
- Detects completed achievements from PLAN markdown
- Generates APPROVED_XX.md files
- Adds Achievement Index if missing
- Validates result

Created: 2025-11-12
Achievement: 2.5 - Codify Feedback System Patterns
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Set


@dataclass
class MigrationResult:
    """Results of migration run."""

    success: bool
    created_files: List[str] = field(default_factory=list)
    created_dirs: List[str] = field(default_factory=list)
    detected_achievements: Set[str] = field(default_factory=set)
    messages: List[str] = field(default_factory=list)


class LegacyPlanMigrator:
    """Migrates legacy plans to feedback system."""

    def __init__(self, plan_path: Path, dry_run: bool = True):
        """
        Initialize migrator for a PLAN.

        Args:
            plan_path: Path to PLAN file or PLAN directory
            dry_run: If True, show what would be done without making changes
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

        self.dry_run = dry_run
        self.feedbacks_dir = self.plan_dir / "execution" / "feedbacks"

    def migrate(self) -> MigrationResult:
        """
        Migrate the plan to feedback system.

        Returns:
            MigrationResult with details of what was done
        """
        result = MigrationResult(success=False)

        try:
            # Step 1: Detect completed achievements
            result.messages.append("🔍 Detecting completed achievements...")
            completed = self.detect_completions_from_markdown()
            result.detected_achievements = completed

            if not completed:
                result.messages.append("ℹ️  No completed achievements detected")
                result.messages.append("   (Looking for ✅ markers or 'Complete' status)")
                result.success = True
                return result

            result.messages.append(
                f"   Found {len(completed)} completed achievements: {sorted(completed)}"
            )

            # Step 2: Create feedback structure
            if not self.feedbacks_dir.exists():
                result.messages.append("")
                result.messages.append("📁 Creating feedback structure...")
                if self.dry_run:
                    result.messages.append(f"   [DRY-RUN] Would create: {self.feedbacks_dir}")
                else:
                    self.feedbacks_dir.mkdir(parents=True, exist_ok=True)
                    result.created_dirs.append(str(self.feedbacks_dir))
                    result.messages.append(f"   ✅ Created: {self.feedbacks_dir}")
            else:
                result.messages.append("")
                result.messages.append("ℹ️  Feedback structure already exists")

            # Step 3: Generate APPROVED files
            result.messages.append("")
            result.messages.append("📝 Generating APPROVED files...")
            for ach in sorted(completed):
                filename = self._achievement_to_filename(ach)
                filepath = self.feedbacks_dir / filename

                if filepath.exists():
                    result.messages.append(f"   ⏭️  Skipping (exists): {filename}")
                else:
                    if self.dry_run:
                        result.messages.append(f"   [DRY-RUN] Would create: {filename}")
                    else:
                        self._create_approved_file(filepath, ach)
                        result.created_files.append(str(filepath))
                        result.messages.append(f"   ✅ Created: {filename}")

            # Step 4: Check Achievement Index
            result.messages.append("")
            result.messages.append("📋 Checking Achievement Index...")
            if self._has_achievement_index():
                result.messages.append("   ✅ Achievement Index already exists")
            else:
                result.messages.append("   ⚠️  Achievement Index not found in PLAN")
                result.messages.append(
                    "      Manual action needed: Add Achievement Index section to PLAN"
                )

            # Success!
            result.success = True

            # Summary
            result.messages.append("")
            result.messages.append("=" * 70)
            result.messages.append("📊 MIGRATION SUMMARY:")
            result.messages.append(f"   Detected achievements: {len(completed)}")
            result.messages.append(f"   Directories created:   {len(result.created_dirs)}")
            result.messages.append(f"   Files created:         {len(result.created_files)}")

            if self.dry_run:
                result.messages.append("")
                result.messages.append("💡 This was a DRY-RUN. Use --apply to make actual changes.")

        except Exception as e:
            result.success = False
            result.messages.append(f"❌ Error: {e}")

        return result

    def detect_completions_from_markdown(self) -> Set[str]:
        """
        Detect completed achievements from PLAN markdown.

        Looks for:
        - ✅ markers before achievement lines
        - "Status: Complete" in achievement sections
        - "COMPLETE" status indicators

        Returns:
            Set of completed achievement numbers (e.g., {"0.1", "1.1"})
        """
        completed = set()

        try:
            content = self.plan_file.read_text()

            # Pattern 1: ✅ Achievement X.X
            pattern1 = r"✅\s+Achievement\s+(\d+\.\d+)"
            matches1 = re.findall(pattern1, content)
            completed.update(matches1)

            # Pattern 2: - ✅ Achievement X.X
            pattern2 = r"-\s+✅\s+Achievement\s+(\d+\.\d+)"
            matches2 = re.findall(pattern2, content)
            completed.update(matches2)

            # Pattern 3: Achievement X.X: ... **Status**: Complete
            pattern3 = r"\*\*Achievement\s+(\d+\.\d+)\*\*:.*?\*\*Status\*\*:\s*(?:✅\s*)?Complete"
            matches3 = re.findall(pattern3, content, re.DOTALL)
            completed.update(matches3)

        except Exception as e:
            print(f"Warning: Could not detect completions: {e}")

        return completed

    def _has_achievement_index(self) -> bool:
        """
        Check if PLAN has an Achievement Index section.

        Returns:
            True if Achievement Index exists
        """
        try:
            content = self.plan_file.read_text()
            return bool(re.search(r"##\s+(?:📋\s+)?Achievement Index", content))
        except:
            return False

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

    def _create_approved_file(self, filepath: Path, ach_num: str):
        """
        Create an APPROVED file with standard content.

        Args:
            filepath: Path to create file at
            ach_num: Achievement number (e.g., "1.1")
        """
        date_str = datetime.now().strftime("%Y-%m-%d")

        content = f"""# APPROVED: Achievement {ach_num}

**Achievement**: {ach_num}  
**Date**: {date_str}  
**Status**: ✅ Approved  

---

## ✅ Approval

This achievement has been marked as complete and approved.

**Migration Note**: This APPROVED file was auto-generated during migration to the feedback system.

---

**Reviewer**: Migration Script  
**Approved**: {date_str}
"""

        filepath.write_text(content)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate legacy plan to feedback system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run (safe, shows what would be done)
  python3 migrate_legacy_completions.py work-space/plans/LEGACY-PLAN/

  # Actually apply migration
  python3 migrate_legacy_completions.py work-space/plans/LEGACY-PLAN/ --apply

  # Migrate specific PLAN file
  python3 migrate_legacy_completions.py work-space/plans/LEGACY-PLAN/PLAN_LEGACY.md --apply
        """,
    )

    parser.add_argument("plan_path", type=Path, help="Path to PLAN file or PLAN directory")

    parser.add_argument(
        "--apply", action="store_true", help="Actually apply changes (default is dry-run)"
    )

    args = parser.parse_args()

    # Validate plan path
    if not args.plan_path.exists():
        print(f"❌ Error: Path not found: {args.plan_path}")
        sys.exit(1)

    # Run migration
    try:
        dry_run = not args.apply
        migrator = LegacyPlanMigrator(args.plan_path, dry_run=dry_run)
        result = migrator.migrate()

        # Print messages
        for message in result.messages:
            print(message)

        # Validate result if applied
        if args.apply and result.success:
            print("")
            print("🔍 Validating result...")
            print("")

            # Import and run validation
            sys.path.insert(0, str(Path(__file__).parent.parent / "validation"))
            from validate_feedback_system import FeedbackSystemValidator, format_validation_report

            validator = FeedbackSystemValidator(args.plan_path)
            validation_result = validator.validate()

            if validation_result.passed:
                print("✅ Migration complete and validated!")
            else:
                print("⚠️  Migration complete but validation found issues:")
                print(format_validation_report(validation_result))

        # Exit with appropriate code
        sys.exit(0 if result.success else 1)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
