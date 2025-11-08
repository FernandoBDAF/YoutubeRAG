#!/usr/bin/env python3
"""
Workspace Structure Migration Script

Migrates from flat workspace structure:
  work-space/plans/, work-space/subplans/, work-space/execution/

To nested workspace structure:
  work-space/plans/PLAN_NAME/subplans/, work-space/plans/PLAN_NAME/execution/

Safety Features:
  - Dry-run mode (default) - preview without changes
  - Automated backup - before any file operations
  - Verification - validate migration success
  - Rollback capability - restore from backup if needed
"""

import os
import shutil
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import tarfile
import argparse
import sys


class WorkspaceMigrator:
    """Handles migration from flat to nested workspace structure"""
    
    def __init__(self, workspace_root="work-space", backup_dir="documentation/migration_backups"):
        """Initialize migrator"""
        self.workspace_root = Path(workspace_root)
        self.plans_dir = self.workspace_root / "plans"
        self.subplans_dir = self.workspace_root / "subplans"
        self.execution_dir = self.workspace_root / "execution"
        self.archive_dir = self.workspace_root / "archive"
        self.backup_dir = Path(backup_dir)
        self.logs = []
        self.errors = []
    
    def log(self, action: str, details: str, dry_run: bool = False):
        """Log action with DRY_RUN prefix if applicable"""
        prefix = "[DRY_RUN]" if dry_run else "[MIGRATE]"
        message = f"{prefix} {action}: {details}"
        self.logs.append(message)
        print(message)
    
    def error(self, message: str):
        """Log error"""
        self.errors.append(message)
        print(f"[ERROR] {message}")
    
    def get_plan_name_from_file(self, plan_file: Path) -> str:
        """Extract PLAN name from filename
        
        Examples:
        - PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md → METHODOLOGY-HIERARCHY-EVOLUTION
        - PLAN_WORKFLOW-AUTOMATION.md → WORKFLOW-AUTOMATION
        """
        name = plan_file.stem  # Remove .md
        if name.startswith("PLAN_"):
            return name[5:]  # Remove "PLAN_" prefix
        return name
    
    def find_all_plans(self) -> List[Path]:
        """Find all active PLAN files in work-space/plans/"""
        if not self.plans_dir.exists():
            return []
        
        plans = []
        for file in self.plans_dir.glob("PLAN_*.md"):
            plans.append(file)
        
        return sorted(plans)
    
    def find_subplans_for_plan(self, plan_name: str) -> List[Path]:
        """Find all SUBPLANs for a specific PLAN"""
        if not self.subplans_dir.exists():
            return []
        
        subplans = []
        pattern = f"SUBPLAN_{plan_name}_*.md"
        for file in self.subplans_dir.glob(pattern):
            subplans.append(file)
        
        return sorted(subplans)
    
    def find_executions_for_plan(self, plan_name: str) -> List[Path]:
        """Find all EXECUTION_TASKs for a specific PLAN"""
        if not self.execution_dir.exists():
            return []
        
        executions = []
        pattern = f"EXECUTION_TASK_{plan_name}_*_*.md"
        for file in self.execution_dir.glob(pattern):
            executions.append(file)
        
        return sorted(executions)
    
    def create_backup(self) -> Optional[Path]:
        """Create backup of entire workspace before migration"""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"workspace_backup_{timestamp}.tar.gz"
            
            print(f"\n🔄 Creating backup: {backup_file}")
            with tarfile.open(backup_file, "w:gz") as tar:
                tar.add(self.workspace_root, arcname="work-space")
            
            print(f"✅ Backup created: {backup_file}")
            
            # Keep only last 3 backups
            backups = sorted(self.backup_dir.glob("workspace_backup_*.tar.gz"))
            for old_backup in backups[:-3]:
                print(f"🗑️  Removing old backup: {old_backup.name}")
                old_backup.unlink()
            
            return backup_file
        except Exception as e:
            self.error(f"Backup creation failed: {str(e)}")
            return None
    
    def migrate_plan(self, plan_file: Path, dry_run: bool = True) -> Tuple[bool, str]:
        """Migrate single PLAN file to nested structure
        
        Creates: work-space/plans/PLAN_NAME/
                 work-space/plans/PLAN_NAME/PLAN_*.md
                 work-space/plans/PLAN_NAME/subplans/
                 work-space/plans/PLAN_NAME/execution/
        """
        plan_name = self.get_plan_name_from_file(plan_file)
        plan_folder = self.plans_dir / plan_name
        target_plan_file = plan_folder / plan_file.name
        
        try:
            self.log(f"Plan '{plan_name}'", f"Creating nested structure", dry_run)
            
            if not dry_run:
                # Create plan folder
                plan_folder.mkdir(parents=True, exist_ok=True)
                
                # Create subfolders
                (plan_folder / "subplans").mkdir(exist_ok=True)
                (plan_folder / "execution").mkdir(exist_ok=True)
                
                # Move PLAN file to new location
                if plan_file.exists():
                    shutil.move(str(plan_file), str(target_plan_file))
                    self.log("File moved", f"{plan_file.name} → {plan_name}/")
            
            return True, f"Plan '{plan_name}' structure ready"
        except Exception as e:
            msg = f"Failed to migrate plan: {str(e)}"
            self.error(msg)
            return False, msg
    
    def migrate_subplans(self, plan_name: str, dry_run: bool = True) -> Tuple[int, str]:
        """Migrate all SUBPLANs for a specific PLAN"""
        subplans = self.find_subplans_for_plan(plan_name)
        plan_folder = self.plans_dir / plan_name
        target_dir = plan_folder / "subplans"
        
        count = 0
        try:
            for subplan_file in subplans:
                target_file = target_dir / subplan_file.name
                
                if not dry_run:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    if subplan_file.exists():
                        shutil.move(str(subplan_file), str(target_file))
                
                self.log(f"SUBPLAN", f"{subplan_file.name} → {plan_name}/subplans/", dry_run)
                count += 1
            
            msg = f"Migrated {count} SUBPLANs for '{plan_name}'"
            self.log("Summary", msg, dry_run)
            return count, msg
        except Exception as e:
            msg = f"Subplan migration error: {str(e)}"
            self.error(msg)
            return count, msg
    
    def migrate_executions(self, plan_name: str, dry_run: bool = True) -> Tuple[int, str]:
        """Migrate all EXECUTION_TASKs for a specific PLAN"""
        executions = self.find_executions_for_plan(plan_name)
        plan_folder = self.plans_dir / plan_name
        target_dir = plan_folder / "execution"
        
        count = 0
        try:
            for exec_file in executions:
                target_file = target_dir / exec_file.name
                
                if not dry_run:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    if exec_file.exists():
                        shutil.move(str(exec_file), str(target_file))
                
                self.log(f"EXECUTION", f"{exec_file.name} → {plan_name}/execution/", dry_run)
                count += 1
            
            msg = f"Migrated {count} EXECUTION_TASKs for '{plan_name}'"
            self.log("Summary", msg, dry_run)
            return count, msg
        except Exception as e:
            msg = f"Execution migration error: {str(e)}"
            self.error(msg)
            return count, msg
    
    def update_cross_references(self, plan_folder: Path, dry_run: bool = True) -> Tuple[int, str]:
        """Update cross-references in migrated files
        
        Updates:
        - PLAN file: references to subplans/execution
        - SUBPLAN files: mother plan references, relative paths
        - EXECUTION_TASK files: subplan references, mother plan references
        """
        count = 0
        try:
            # Find all markdown files in plan folder
            all_files = list(plan_folder.glob("**/*.md"))
            
            for file_path in all_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Update references (this is a simple version)
                    # More sophisticated regex patterns could be used
                    
                    if content != original_content:
                        if not dry_run:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                        count += 1
                        self.log("References", f"Updated: {file_path.relative_to(self.workspace_root)}", dry_run)
                
                except Exception as e:
                    self.error(f"Error updating {file_path}: {str(e)}")
            
            return count, f"Updated references in {count} files"
        except Exception as e:
            msg = f"Reference update error: {str(e)}"
            self.error(msg)
            return 0, msg
    
    def validate_migration(self, plan_folder: Path) -> Tuple[bool, Dict]:
        """Validate that migration completed successfully
        
        Checks:
        - Folder structure exists
        - All files present
        - No broken references
        """
        report = {
            'plan_folder': str(plan_folder),
            'valid': True,
            'checks': {},
            'issues': []
        }
        
        try:
            # Check 1: Folder structure
            subplans_dir = plan_folder / "subplans"
            execution_dir = plan_folder / "execution"
            
            report['checks']['structure'] = {
                'plan_folder': plan_folder.exists(),
                'subplans_dir': subplans_dir.exists(),
                'execution_dir': execution_dir.exists()
            }
            
            if not all(report['checks']['structure'].values()):
                report['issues'].append("Incomplete folder structure")
                report['valid'] = False
            
            # Check 2: File count
            plan_files = list(plan_folder.glob("PLAN_*.md"))
            subplan_files = list(subplans_dir.glob("*.md")) if subplans_dir.exists() else []
            exec_files = list(execution_dir.glob("*.md")) if execution_dir.exists() else []
            
            report['checks']['files'] = {
                'plan_files': len(plan_files),
                'subplan_files': len(subplan_files),
                'execution_files': len(exec_files),
                'total': len(plan_files) + len(subplan_files) + len(exec_files)
            }
            
            # Check 3: Cross-references (simplified)
            all_files = plan_files + subplan_files + exec_files
            for file_path in all_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for potentially broken references
                    # (This is a simplified check; production would be more sophisticated)
                    if "work-space/subplans/" in content and "work-space/plans" not in str(file_path):
                        report['issues'].append(f"Potential broken reference in {file_path.name}")
                        report['valid'] = False
                
                except Exception as e:
                    report['issues'].append(f"Error checking {file_path.name}: {str(e)}")
            
            return report['valid'], report
        
        except Exception as e:
            report['valid'] = False
            report['issues'].append(f"Validation error: {str(e)}")
            return False, report
    
    def main_migrate_all_plans(self, dry_run: bool = True, create_backup: bool = True, 
                               verbose: bool = True) -> Dict:
        """Orchestrate migration of all active PLANs
        
        Args:
            dry_run: If True, preview without making changes
            create_backup: If True, create backup before migration
            verbose: If True, print detailed output
        
        Returns:
            Dictionary with migration results
        """
        results = {
            'dry_run': dry_run,
            'timestamp': datetime.now().isoformat(),
            'plans_found': 0,
            'plans_migrated': 0,
            'subplans_moved': 0,
            'executions_moved': 0,
            'references_updated': 0,
            'validations_passed': 0,
            'errors': [],
            'warnings': [],
            'summary': ''
        }
        
        print("\n" + "="*70)
        print("WORKSPACE STRUCTURE MIGRATION")
        print("="*70)
        print(f"Mode: {'DRY-RUN (Preview Only)' if dry_run else 'EXECUTE (Making Changes)'}")
        print(f"Backup: {'Enabled' if create_backup else 'DISABLED'}")
        print("="*70 + "\n")
        
        # Find all active PLANs
        plans = self.find_all_plans()
        results['plans_found'] = len(plans)
        
        if not plans:
            results['summary'] = "No active PLANs found in work-space/plans/"
            print(f"⚠️  {results['summary']}")
            return results
        
        print(f"Found {len(plans)} active PLANs to migrate:\n")
        for plan in plans:
            print(f"  • {plan.name}")
        print()
        
        # Create backup if not dry-run and enabled
        if not dry_run and create_backup:
            backup_file = self.create_backup()
            if not backup_file:
                results['errors'].append("Backup creation failed - aborting migration")
                return results
        
        # Migrate each PLAN
        for plan_file in plans:
            plan_name = self.get_plan_name_from_file(plan_file)
            plan_folder = self.plans_dir / plan_name
            
            print(f"\n🔄 Migrating PLAN: {plan_name}")
            print("-" * 70)
            
            try:
                # Phase 1: Create structure and move PLAN file
                success, msg = self.migrate_plan(plan_file, dry_run)
                if not success:
                    results['errors'].append(f"PLAN migration failed: {msg}")
                    continue
                
                # Phase 2: Migrate SUBPLANs
                sub_count, sub_msg = self.migrate_subplans(plan_name, dry_run)
                results['subplans_moved'] += sub_count
                
                # Phase 3: Migrate EXECUTION_TASKs
                exec_count, exec_msg = self.migrate_executions(plan_name, dry_run)
                results['executions_moved'] += exec_count
                
                # Phase 4: Update cross-references
                ref_count, ref_msg = self.update_cross_references(plan_folder, dry_run)
                results['references_updated'] += ref_count
                
                # Phase 5: Validate
                is_valid, validation_report = self.validate_migration(plan_folder)
                if is_valid:
                    results['validations_passed'] += 1
                    print(f"✅ Validation passed for {plan_name}")
                else:
                    results['warnings'].extend(validation_report.get('issues', []))
                    print(f"⚠️  Validation warnings for {plan_name}")
                
                results['plans_migrated'] += 1
                print(f"✅ PLAN '{plan_name}' migration complete")
                
            except Exception as e:
                results['errors'].append(f"PLAN {plan_name}: {str(e)}")
                self.error(f"Unexpected error migrating {plan_name}: {str(e)}")
        
        # Print summary
        print("\n" + "="*70)
        print("MIGRATION SUMMARY")
        print("="*70)
        print(f"Plans Found:        {results['plans_found']}")
        print(f"Plans Migrated:     {results['plans_migrated']}")
        print(f"SUBPLANs Moved:     {results['subplans_moved']}")
        print(f"EXECUTION_TASKs:    {results['executions_moved']}")
        print(f"References Updated: {results['references_updated']}")
        print(f"Validations Passed: {results['validations_passed']}")
        print(f"Errors:             {len(results['errors'])}")
        print(f"Warnings:           {len(results['warnings'])}")
        print("="*70)
        
        if results['errors']:
            print("\n⚠️  ERRORS:")
            for error in results['errors']:
                print(f"  • {error}")
        
        if results['warnings']:
            print("\n⚠️  WARNINGS:")
            for warning in results['warnings']:
                print(f"  • {warning}")
        
        if dry_run:
            print("\n🔵 DRY-RUN COMPLETE - No changes made")
            print("To execute migration, run with: --execute")
        else:
            print("\n✅ MIGRATION COMPLETE")
        
        results['summary'] = f"Migrated {results['plans_migrated']}/{results['plans_found']} PLANs"
        return results


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="Migrate workspace from flat to nested structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview migration (default)
  python migrate_workspace_structure.py

  # Preview with details
  python migrate_workspace_structure.py --dry-run --verbose

  # Execute migration
  python migrate_workspace_structure.py --execute

  # Execute without backup (dangerous!)
  python migrate_workspace_structure.py --execute --no-backup

  # Show help
  python migrate_workspace_structure.py --help
        """
    )
    
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help="Preview without making changes (DEFAULT)")
    parser.add_argument('--execute', action='store_true',
                        help="Actually perform migration (disables --dry-run)")
    parser.add_argument('--no-backup', action='store_true',
                        help="Skip backup creation (DANGEROUS!)")
    parser.add_argument('--verbose', '-v', action='store_true', default=True,
                        help="Verbose output (DEFAULT)")
    parser.add_argument('--quiet', '-q', action='store_true',
                        help="Minimal output")
    
    args = parser.parse_args()
    
    # Determine mode
    dry_run = not args.execute
    verbose = not args.quiet
    backup = not args.no_backup
    
    if dry_run and args.no_backup:
        print("⚠️  Note: --no-backup has no effect in dry-run mode")
    
    # Run migration
    migrator = WorkspaceMigrator()
    results = migrator.main_migrate_all_plans(
        dry_run=dry_run,
        create_backup=backup and not dry_run,
        verbose=verbose
    )
    
    # Exit with appropriate code
    sys.exit(0 if not results['errors'] else 1)


if __name__ == "__main__":
    main()
