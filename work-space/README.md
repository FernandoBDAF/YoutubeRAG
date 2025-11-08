# Workspace Directory

**Purpose**: Dedicated location for all generated methodology files to prevent root directory pollution  
**Created**: 2025-01-27  
**Status**: Active

---

## 🎯 What This Is

The `work-space/` directory is a dedicated folder for all active methodology files (PLANs, SUBPLANs, EXECUTION_TASKs). Instead of creating these files in the project root, they are organized here to keep the root directory clean and focused on project code.

**Key Benefits**:
- **Clean Root**: Project root stays uncluttered with methodology files
- **Better Organization**: All active work in one dedicated location
- **Easy Discovery**: Know exactly where to find active PLANs, SUBPLANs, EXECUTION_TASKs
- **Separation of Concerns**: Methodology files separate from project code

---

## 📁 Directory Structure

```
work-space/
├── plans/          # PLAN files (PLAN_*.md)
├── subplans/       # SUBPLAN files (SUBPLAN_*.md)
├── execution/      # EXECUTION_TASK files (EXECUTION_TASK_*.md)
└── README.md       # This file
```

### Directory Purposes

**plans/**:
- Contains all PLAN files
- Example: `PLAN_FILE-MOVING-WORKSPACE-AND-MANUAL-ARCHIVE.md`
- One PLAN per feature/initiative

**subplans/**:
- Contains all SUBPLAN files
- Example: `SUBPLAN_FILE-MOVING-WORKSPACE-AND-MANUAL-ARCHIVE_01.md`
- One SUBPLAN per achievement

**execution/**:
- Contains all EXECUTION_TASK files
- Example: `EXECUTION_TASK_FILE-MOVING-WORKSPACE-AND-MANUAL-ARCHIVE_01_01.md`
- One EXECUTION_TASK per execution attempt

---

## 📖 Usage Instructions

### Creating Files in Workspace

**When creating a new PLAN**:
- Create file in `work-space/plans/`
- Example: `work-space/plans/PLAN_NEW-FEATURE.md`

**When creating a new SUBPLAN**:
- Create file in `work-space/subplans/`
- Example: `work-space/subplans/SUBPLAN_NEW-FEATURE_01.md`

**When creating a new EXECUTION_TASK**:
- Create file in `work-space/execution/`
- Example: `work-space/execution/EXECUTION_TASK_NEW-FEATURE_01_01.md`

### Referencing Files

**From templates and protocols**:
- Reference files using workspace paths: `work-space/plans/PLAN_*.md`
- Update file paths in documentation to reflect workspace location

**From command line**:
```bash
# List all PLANs
ls -1 work-space/plans/

# List all SUBPLANs
ls -1 work-space/subplans/

# List all EXECUTION_TASKs
ls -1 work-space/execution/
```

### File Discovery

**Quick discovery**:
- All active PLANs: `work-space/plans/`
- All active SUBPLANs: `work-space/subplans/`
- All active EXECUTION_TASKs: `work-space/execution/`

**Search**:
```bash
# Find PLAN by name
find work-space/plans/ -name "*FEATURE*"

# Find all files for a feature
find work-space/ -name "*FEATURE*"
```

---

## 🔄 Migration Notes

### Current State

**Existing files in root**:
- Many PLANs, SUBPLANs, and EXECUTION_TASKs currently exist in project root
- These files will remain in root until manually migrated (if desired)

### Migration Strategy (Optional)

**If you want to migrate existing files**:

1. **Identify files to migrate**:
   ```bash
   # Find all PLANs in root
   ls -1 PLAN_*.md
   
   # Find all SUBPLANs in root
   ls -1 SUBPLAN_*.md
   
   # Find all EXECUTION_TASKs in root
   ls -1 EXECUTION_TASK_*.md
   ```

2. **Move files**:
   ```bash
   # Move PLANs
   mv PLAN_*.md work-space/plans/
   
   # Move SUBPLANs
   mv SUBPLAN_*.md work-space/subplans/
   
   # Move EXECUTION_TASKs
   mv EXECUTION_TASK_*.md work-space/execution/
   ```

3. **Update references**:
   - Update ACTIVE_PLANS.md with new paths
   - Update any scripts that reference these files
   - Update documentation references

**Note**: Migration is optional. You can keep existing files in root and only use workspace for new files.

### Future Files

**All new files**:
- New PLANs, SUBPLANs, and EXECUTION_TASKs should be created in workspace
- Templates and protocols will be updated to use workspace paths
- This ensures root stays clean going forward

---

## 🔗 Related Documentation

- **Methodology**: `LLM-METHODOLOGY.md` - Overall methodology reference
- **Templates**: `LLM/templates/` - File templates (will reference workspace)
- **Protocols**: `LLM/protocols/` - Entry/exit protocols (will reference workspace)
- **Archive**: `documentation/archive/` - Completed work archives

---

## 📊 Workspace Statistics

**Current Files** (as of creation):
- PLANs: 0 (will populate as new PLANs are created)
- SUBPLANs: 0 (will populate as new SUBPLANs are created)
- EXECUTION_TASKs: 0 (will populate as new EXECUTION_TASKs are created)

**Note**: Statistics will be updated as files are created in workspace.

---

## 🚀 Next Steps

1. **Templates Updated**: Templates will be updated to create files in workspace (Achievement 1.1)
2. **Protocols Updated**: Protocols will be updated to reference workspace (Achievement 1.2)
3. **Manual Archive**: Archive script will work with workspace files (Achievement 0.2)

---

**Version**: 1.0  
**Status**: Active  
**Last Updated**: 2025-01-27

