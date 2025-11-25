# SUBPLAN: Create Migration Script

**Type**: SUBPLAN  
**Mother Plan**: PLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING.md  
**Plan**: Workflow Automation & Workspace Restructuring  
**Achievement Addressed**: Achievement 0.2 (Create Migration Script)  
**Achievement**: 0.2  
**Status**: Design Phase  
**Created**: 2025-11-09 02:15 UTC  
**Estimated Effort**: 3-4 hours

**File Location**: `work-space/subplans/SUBPLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_02.md`

**Size**: 200-600 lines

---

## 🎯 Objective

Create automated, safe migration script that transitions workspace from flat structure (plans/, subplans/, execution/) to nested structure (plans/PLAN_NAME/subplans/, plans/PLAN_NAME/execution/). This achievement is critical - it unlocks Achievement 0.3 (migration execution) and enables Phase B of the coordination strategy.

---

## 🎓 Context (Minimal Reading)

**Prerequisite**: Achievement 0.1 COMPLETE - scripts support dual structure

**Dual Structure Support** (from Achievement 0.1):
- Scripts can now detect flat vs nested structure
- Discovery functions work with both
- This provides safety net for migration

**What Migration Must Do**:
1. Inventory active PLANs
2. For each PLAN: create nested folder structure
3. Move PLAN file, SUBPLANs, EXECUTION_TASKs to new locations
4. Update cross-references (relative paths, links)
5. Validate all references intact
6. Provide rollback capability

**Safety First**:
- Dry-run mode (show what WILL happen without doing it)
- Backup creation before any changes
- Verification after migration
- Rollback script if issues found

---

## 🔀 Execution Strategy

**Single Execution**: Yes, straightforward implementation

**Why Single**:
- Well-defined requirements
- Sequential nature (can't parallelize safely)
- Single script that does complete migration
- All functions work together

**Execution Phases**:
1. Write core migration functions
2. Add safety features (dry-run, backup, verify)
3. Add supporting utilities
4. Create comprehensive tests
5. Create migration guide

---

## 📋 Execution Plan

### Phase 1: Core Functions (1-1.5h)

Create `LLM/scripts/migration/migrate_workspace_structure.py`:

**Function 1: `migrate_plan(plan_file, dry_run=True)`**
- Input: PLAN file from `work-space/plans/`
- Create: `work-space/plans/PLAN_NAME/` folder
- Move: PLAN file to `work-space/plans/PLAN_NAME/PLAN_FILENAME.md`
- Create: `subplans/` and `execution/` subfolders
- Return: success flag, error messages

**Function 2: `migrate_subplans(plan_name, dry_run=True)`**
- Input: PLAN name
- Find: All SUBPLANs for this PLAN in `work-space/subplans/`
- Move: To `work-space/plans/PLAN_NAME/subplans/`
- Return: count, success

**Function 3: `migrate_executions(plan_name, dry_run=True)`**
- Input: PLAN name
- Find: All EXECUTION_TASKs for this PLAN in `work-space/execution/`
- Move: To `work-space/plans/PLAN_NAME/execution/`
- Return: count, success

**Function 4: `update_cross_references(plan_folder, dry_run=True)`**
- Input: Migrated PLAN folder
- In PLAN file: Update relative paths to SUBPLANs/EXECUTION_TASKs
- In SUBPLAN files: Update paths
- In EXECUTION_TASK files: Update paths
- Return: updated count

**Function 5: `validate_migration(plan_folder)`**
- Input: Migrated PLAN folder
- Check: All files exist
- Check: All paths resolved
- Check: No broken references
- Return: validation report

### Phase 2: Safety Features (1h)

**Feature 1: Dry-Run Mode**
- All functions accept `dry_run=True` parameter
- When True: print what WILL happen, don't make changes
- Output: clear "DRY RUN" log
- Allows review before actual migration

**Feature 2: Backup Creation**
- Before actual migration: tar entire workspace
- Name: `workspace_backup_TIMESTAMP.tar.gz`
- Location: `documentation/migration_backups/`
- Automatic cleanup (keep last 3 backups)

**Feature 3: Verification**
- After migration: run validation for each PLAN
- Report: count of files, references checked
- Report: any issues found
- Rollback prompt if issues detected

### Phase 3: Main Orchestration (0.5-1h)

**Function: `main_migrate_all_plans(dry_run=True, backup=True)`**
- Discover all active PLANs in `work-space/plans/`
- For each PLAN:
  1. Create nested structure
  2. Migrate SUBPLAN files
  3. Migrate EXECUTION_TASK files
  4. Update cross-references
  5. Validate migration
- Provide summary report

**CLI Interface**:
```
python migrate_workspace_structure.py --dry-run
python migrate_workspace_structure.py --execute
python migrate_workspace_structure.py --execute --no-backup (dangerous!)
python migrate_workspace_structure.py --validate-plan PLAN_NAME
python migrate_workspace_structure.py --rollback BACKUP_FILE
```

---

## 📋 Supporting Deliverables

### Supporting Script 1: Migration Validation Script

**File**: `LLM/scripts/migration/validate_migration.py`

Purpose: Standalone validation that migration was successful

Functions:
- `validate_all_plans()` - check all PLANs in new structure
- `validate_plan(plan_name)` - check single PLAN
- `check_broken_references()` - find any broken links
- `generate_migration_report()` - comprehensive report

### Supporting Script 2: Rollback Script

**File**: `LLM/scripts/migration/rollback_migration.py`

Purpose: Restore workspace from backup if needed

Functions:
- `list_backups()` - show available backups
- `restore_from_backup(backup_file)` - restore specific backup
- `auto_rollback()` - use most recent backup

### Documentation: Migration Guide

**File**: `LLM/guides/MIGRATION-GUIDE.md`

Sections:
- **Before Migration** (what to prepare)
- **Dry-Run Preview** (how to preview without changes)
- **Execute Migration** (actual migration steps)
- **Verification** (how to verify success)
- **Troubleshooting** (common issues)
- **Rollback** (if something goes wrong)
- **Testing After** (verify scripts work in new structure)

---

## 🧪 Testing Strategy

### Unit Tests: `test_migrate_functions.py`

```python
# Test individual functions
test_migrate_plan_structure()          # Create folder structure correctly
test_migrate_plan_file_movement()      # PLAN file moved to right location
test_migrate_subplans_discovery()      # Find and move all SUBPLANs
test_migrate_executions_discovery()    # Find and move all EXECUTION_TASKs
test_update_path_references()          # Paths updated correctly in files
test_validate_migration_success()      # Validation detects successful migration
test_validate_migration_broken()       # Validation detects issues
test_dry_run_mode()                    # Dry-run doesn't change files
test_backup_creation()                 # Backup created before migration
test_rollback_restoration()            # Rollback restores original state
```

### Integration Test: `test_migration_end_to_end.py`

```
1. Setup: Create test workspace with sample PLANs/SUBPLANs/EXECUTION_TASKs
2. Dry-Run: Execute migration in dry-run mode
   - Verify nothing changed
   - Review output
3. Migrate: Execute actual migration
   - Verify all files moved
   - Verify structure correct
4. Validate: Run validation
   - Verify no broken references
   - Verify all files accessible
5. Test Discovery: Run scripts with new structure
   - find_subplan_for_achievement() works
   - find_execution_for_subplan() works
6. Cleanup: Remove test workspace
```

---

## ✅ Success Criteria

**Achievement Complete When**:

1. ✅ `migrate_workspace_structure.py` created with all 5 core functions
2. ✅ All safety features implemented (dry-run, backup, verify)
3. ✅ Supporting scripts created (validate, rollback)
4. ✅ Migration guide written
5. ✅ All unit tests passing (10+ test cases)
6. ✅ Integration test passing (end-to-end)
7. ✅ Scripts can migrate ALL active PLANs successfully
8. ✅ Validation confirms migration success
9. ✅ Rollback functionality verified working

---

## ⚠️ Critical Constraints

**DO NOT**:
- ❌ Actually migrate files in this phase (Achievement 0.3 does that)
- ❌ Remove flat structure support (still needed for parallel work)
- ❌ Assume specific PLAN names (must auto-discover)
- ❌ Skip backup creation
- ❌ Ignore validation errors

**DO**:
- ✅ Make dry-run the default
- ✅ Test thoroughly with sample data
- ✅ Log everything (help with debugging)
- ✅ Document rollback procedure clearly
- ✅ Handle edge cases (empty folders, missing files, etc)

---

## 📊 Deliverables Summary

| Deliverable | Location | Status |
|-----------|----------|--------|
| Main migration script | `LLM/scripts/migration/migrate_workspace_structure.py` | To Create |
| Validation script | `LLM/scripts/migration/validate_migration.py` | To Create |
| Rollback script | `LLM/scripts/migration/rollback_migration.py` | To Create |
| Migration guide | `LLM/guides/MIGRATION-GUIDE.md` | To Create |
| Unit tests | `LLM/scripts/migration/test_migrate_functions.py` | To Create |
| Integration tests | `LLM/scripts/migration/test_migration_end_to_end.py` | To Create |

---

## 🔄 Coordination Notes

**For Executor**:
- Read only this SUBPLAN
- Focus on the execution phases outlined above
- Use success criteria to validate work
- Document any issues found
- Log learnings in EXECUTION_TASK

**For Next Achievement (0.3)**:
- Will actually RUN this script to migrate PLANs
- Needs dry-run output review
- Needs backup verification
- Needs post-migration validation

**Blocker Status**: None - all prerequisites complete (0.1 done)

---

## 📚 Reference Materials

**Workspace Structure** (target):
```
work-space/
├── plans/
│   ├── PLAN_METHODOLOGY-HIERARCHY-EVOLUTION/
│   │   ├── PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md
│   │   ├── subplans/
│   │   │   ├── SUBPLAN_*.md
│   │   │   └── SUBPLAN_*.md
│   │   └── execution/
│   │       ├── EXECUTION_TASK_*.md
│   │       └── EXECUTION_TASK_*.md
│   ├── PLAN_WORKFLOW-AUTOMATION-.../
│   │   ├── PLAN_WORKFLOW-...md
│   │   ├── subplans/
│   │   └── execution/
│   └── ...
├── archive/
│   ├── PLAN_*_ARCHIVED.md
│   ├── SUBPLAN_*_ARCHIVED.md
│   └── EXECUTION_*_ARCHIVED.md
└── migration_backups/
    └── workspace_backup_*.tar.gz
```

**Current Flat Structure** (current):
```
work-space/
├── plans/
│   ├── PLAN_METHODOLOGY-*.md
│   ├── PLAN_WORKFLOW-*.md
│   └── ...
├── subplans/
│   ├── SUBPLAN_*.md
│   └── ...
├── execution/
│   ├── EXECUTION_TASK_*.md
│   └── ...
└── archive/
```

---

**SUBPLAN Status**: Ready for Execution

Next: Executor creates EXECUTION_TASK and implements migration script according to this plan.
