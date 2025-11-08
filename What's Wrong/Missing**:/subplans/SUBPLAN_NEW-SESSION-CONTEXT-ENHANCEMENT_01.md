# SUBPLAN: Fix Archive Location Issues

**Mother Plan**: PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md  
**Achievement Addressed**: Achievement 0.1 (Fix Archive Location Issues)  
**Status**: In Progress  
**Created**: 2025-11-08 00:45 UTC  
**Estimated Effort**: 15 minutes

---

## 🎯 Objective

Fix archive location mismatch and duplicate files from PLAN_FILE-MOVING-OPTIMIZATION.md work. Files were archived to wrong location (`feature-archive/`) instead of PLAN-specified location (`documentation/archive/file-moving-optimization-nov2025/`). This achievement fixes the immediate issues identified in the work review analysis.

**Contribution to PLAN**: This is the foundation achievement (Priority 0) that fixes procedural errors from previous work. By correcting archive locations, we ensure methodology compliance and set the foundation for context enhancement work.

---

## 📋 What Needs to Be Created

### Files to Move

1. **SUBPLAN_FILE-MOVING-OPTIMIZATION_01.md**
   - Current location: `feature-archive/subplans/`
   - Correct location: `documentation/archive/file-moving-optimization-nov2025/subplans/`

2. **EXECUTION_TASK_FILE-MOVING-OPTIMIZATION_01_01.md**
   - Current location: `feature-archive/execution/`
   - Correct location: `documentation/archive/file-moving-optimization-nov2025/execution/`

### Files to Remove

1. **SUBPLAN_FILE-MOVING-OPTIMIZATION_01.md** (if exists in root)
2. **EXECUTION_TASK_FILE-MOVING-OPTIMIZATION_01_01.md** (if exists in root)

### Directories to Create

1. **documentation/archive/file-moving-optimization-nov2025/subplans/**
2. **documentation/archive/file-moving-optimization-nov2025/execution/**

### Verification

- Verify archive structure exists
- Verify files in correct location
- Verify no duplicates in root
- Verify archive location matches PLAN specification

---

## 📝 Approach

**Strategy**: Systematic file system operations to correct archive location and remove duplicates.

**Method**:

1. **Create Archive Structure**:
   - Create `documentation/archive/file-moving-optimization-nov2025/` directory
   - Create `subplans/` and `execution/` subdirectories

2. **Move Files to Correct Location**:
   - Move SUBPLAN from `feature-archive/subplans/` to correct location
   - Move EXECUTION_TASK from `feature-archive/execution/` to correct location

3. **Remove Duplicates**:
   - Check root directory for duplicate files
   - Remove duplicates if they exist

4. **Verify**:
   - Verify archive structure exists
   - Verify files in correct location
   - Verify no duplicates
   - Verify matches PLAN specification

**Key Considerations**:

- **Safety**: Verify files exist before moving
- **Backup**: Files are already in archive (feature-archive), so safe to move
- **Verification**: Must verify all steps completed correctly
- **PLAN Update**: May need to update PLAN_FILE-MOVING-OPTIMIZATION.md if archive location section needs correction

**Risks to Watch For**:

- Files don't exist in expected location
- Archive structure creation fails
- Duplicate files in unexpected locations
- PLAN archive location specification incorrect

---

## 🧪 Tests Required (Validation Approach)

**Validation Method** (file system operations):

**Completeness Check**:
- [ ] Archive structure created correctly
- [ ] Files moved to correct location
- [ ] Duplicates removed from root
- [ ] Archive location matches PLAN specification

**Structure Validation**:
- [ ] `documentation/archive/file-moving-optimization-nov2025/subplans/` exists
- [ ] `documentation/archive/file-moving-optimization-nov2025/execution/` exists
- [ ] Files in correct subdirectories

**Verification Commands**:
```bash
# Verify archive structure
ls -d documentation/archive/file-moving-optimization-nov2025/{subplans,execution}

# Verify files in correct location
ls documentation/archive/file-moving-optimization-nov2025/subplans/SUBPLAN_FILE-MOVING-OPTIMIZATION_01.md
ls documentation/archive/file-moving-optimization-nov2025/execution/EXECUTION_TASK_FILE-MOVING-OPTIMIZATION_01_01.md

# Verify no duplicates in root
ls SUBPLAN_FILE-MOVING-OPTIMIZATION_01.md 2>/dev/null && echo "ERROR: Duplicate exists" || echo "OK: No duplicate"
ls EXECUTION_TASK_FILE-MOVING-OPTIMIZATION_01_01.md 2>/dev/null && echo "ERROR: Duplicate exists" || echo "OK: No duplicate"

# Verify archive location matches PLAN
grep "Archive Location" PLAN_FILE-MOVING-OPTIMIZATION.md
```

---

## ✅ Expected Results

### Functional Changes

- **Archive Structure**: Correct archive directory structure created
- **File Location**: Files moved from wrong location to correct location
- **Root Directory**: Clean (no duplicate files)
- **PLAN Compliance**: Archive location matches PLAN specification

### Observable Outcomes

- Archive structure exists: `documentation/archive/file-moving-optimization-nov2025/{subplans,execution}`
- Files in correct location: SUBPLAN and EXECUTION_TASK in correct archive subdirectories
- No duplicates: Root directory clean (no SUBPLAN/EXECUTION_TASK files)
- PLAN verified: Archive location matches PLAN specification

### Success Indicators

- ✅ Archive structure created correctly
- ✅ Files moved to correct location
- ✅ No duplicates in root directory
- ✅ Archive location matches PLAN specification
- ✅ Verification commands pass

---

## 🔍 Conflict Analysis with Other Subplans

**Review Existing Subplans**:
- None yet (this is the first SUBPLAN for this PLAN)

**Check for**:
- **Overlap**: No other subplans exist
- **Conflicts**: None
- **Dependencies**: None
- **Integration**: This is foundation work - fixes issues before context enhancement

**Analysis**:
- No conflicts detected
- This is the first achievement (Priority 0), so no dependencies
- Safe to proceed

**Result**: Safe to proceed

---

## 🔗 Dependencies

### Other Subplans
- None (this is the first SUBPLAN)

### External Dependencies
- None (file system operations only)

### Prerequisite Knowledge
- Understanding of archive structure
- Understanding of PLAN archive location specification
- File system operations (mkdir, mv, rm, ls)

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

_None yet - will be created when execution starts_

**First Execution**: `EXECUTION_TASK_NEW-SESSION-CONTEXT-ENHANCEMENT_01_01.md`

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] Archive structure created correctly
- [ ] Files moved to correct location
- [ ] Duplicates removed from root
- [ ] Archive location verified (matches PLAN)
- [ ] Verification commands pass
- [ ] EXECUTION_TASK complete
- [ ] Ready for archive

---

## 📝 Notes

**Common Pitfalls**:
- Forgetting to create archive structure before moving files
- Not verifying files exist before moving
- Missing duplicate files in root
- Not verifying archive location matches PLAN

**Resources**:
- PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md (Achievement 0.1 section)
- EXECUTION_ANALYSIS_NEW-SESSION-WORK-REVIEW.md (issue details)
- PLAN_FILE-MOVING-OPTIMIZATION.md (archive location specification)

---

## 📖 What to Read (Focus Rules)

**When working on this SUBPLAN**, follow these focus rules to minimize context:

**✅ READ ONLY**:
- This SUBPLAN file (complete file)
- Parent PLAN Achievement 0.1 section (21 lines)
- Active EXECUTION_TASKs (if any exist)
- Parent PLAN "Current Status & Handoff" section (17 lines)

**❌ DO NOT READ**:
- Parent PLAN full content
- Other achievements in PLAN
- Other SUBPLANs
- Completed EXECUTION_TASKs (unless needed for context)
- Completed work

**Context Budget**: ~400 lines

**Why**: SUBPLAN defines HOW to achieve one achievement. Reading other achievements or full PLAN adds scope and confusion.

**📖 See**: `LLM/guides/FOCUS-RULES.md` for complete focus rules and examples.

---

## 🔄 Active EXECUTION_TASKs (Updated When Created)

**Current Active Work** (register EXECUTION_TASKs immediately when created):

- [ ] **EXECUTION_TASK_NEW-SESSION-CONTEXT-ENHANCEMENT_01_01**: Status: In Progress

**Registration Workflow**:

1. When creating EXECUTION_TASK: Add to this list immediately
2. When archiving: Remove from this list

**Why**: Immediate parent awareness ensures SUBPLAN knows about its active EXECUTION_TASKs.

---

**Ready to Execute**: Create EXECUTION_TASK and begin work  
**Reference**: IMPLEMENTATION_START_POINT.md for workflows

