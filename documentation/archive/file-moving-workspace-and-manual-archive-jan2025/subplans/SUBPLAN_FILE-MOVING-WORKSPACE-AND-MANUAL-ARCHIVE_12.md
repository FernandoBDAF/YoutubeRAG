# SUBPLAN: Protocol and Documentation Updates

**Type**: SUBPLAN  
**Mother Plan**: PLAN_FILE-MOVING-WORKSPACE-AND-MANUAL-ARCHIVE.md  
**Plan**: FILE-MOVING-WORKSPACE-AND-MANUAL-ARCHIVE  
**Achievement Addressed**: Achievement 1.2 (Protocol and Documentation Updates)  
**Achievement**: 1.2  
**Status**: In Progress  
**Created**: 2025-01-28 00:55 UTC  
**Estimated Effort**: 1-2 hours

**Metadata Tags**: See `LLM/guides/METADATA-TAGS.md` for virtual organization system

---

## 🎯 Objective

Update all protocols and documentation to integrate the workspace folder and manual archive script. This ensures the methodology documentation reflects the new workspace-based file organization and user-controlled archiving approach. This implements Achievement 1.2 and completes the workspace integration across all methodology documentation.

---

## 📋 What Needs to Be Created

### Files to Modify

- `LLM/protocols/IMPLEMENTATION_START_POINT.md` - Reference workspace folder for file creation
- `LLM/protocols/IMPLEMENTATION_END_POINT.md` - Reference manual archive script, update archiving workflow
- `LLM-METHODOLOGY.md` - Add workspace folder to directory structure, document workspace purpose
- `LLM/index/FILE-INDEX.md` - Update file locations (workspace instead of root), update statistics

---

## 🎯 Approach

### Step 1: Update IMPLEMENTATION_START_POINT.md

**Changes Needed**:

1. Update file location examples to reference workspace:
   - PLAN files: `work-space/plans/PLAN_*.md`
   - SUBPLAN files: `work-space/subplans/SUBPLAN_*.md`
   - EXECUTION*TASK files: `work-space/execution/EXECUTION_TASK*\*.md`
2. Update naming convention section with workspace paths
3. Add workspace guidance section or note
4. Update archive folder creation section (if needed)

**Key Sections to Update**:

- Naming Convention section
- File location examples
- Archive folder creation (if references root)

### Step 2: Update IMPLEMENTATION_END_POINT.md

**Changes Needed**:

1. Reference manual archive script:
   - Add section about manual archiving
   - Update archiving workflow to use `manual_archive.py`
   - Remove or update automatic archiving references
2. Update file location examples to workspace
3. Update archiving commands to reference workspace

**Key Sections to Update**:

- Archiving Process section
- Deferred Archiving section
- File location examples

### Step 3: Update LLM-METHODOLOGY.md

**Changes Needed**:

1. Add workspace folder to directory structure:
   - Add `work-space/` to the directory tree
   - Document subdirectories (plans/, subplans/, execution/)
2. Document workspace purpose:
   - Explain why workspace exists
   - Link to work-space/README.md
3. Reference manual archive script:
   - Mention manual_archive.py
   - Explain user-controlled archiving

**Key Sections to Update**:

- Full Documentation Index (directory structure)
- Add new section about workspace (or integrate into existing structure)

### Step 4: Update FILE-INDEX.md

**Changes Needed**:

1. Update file locations:
   - Change "Root directory" references to "work-space/"
   - Update PLANs location: `work-space/plans/`
   - Update SUBPLANs location: `work-space/subplans/`
   - Update EXECUTION_TASKs location: `work-space/execution/`
2. Update statistics:
   - Note that active files are in workspace
   - Update counts if needed

**Key Sections to Update**:

- Active Plans section
- Active SUBPLANs section
- Active EXECUTION_TASKs section
- Summary Statistics

### Step 5: Verify All Updates

**Check**:

- All protocols reference workspace
- Manual archive script referenced
- Documentation structure updated
- File locations consistent

---

## ✅ Expected Results

### Deliverables

1. **Updated IMPLEMENTATION_START_POINT.md**:

   - File location examples reference workspace
   - Workspace guidance included

2. **Updated IMPLEMENTATION_END_POINT.md**:

   - Manual archive script referenced
   - Archiving workflow updated
   - Workspace file locations

3. **Updated LLM-METHODOLOGY.md**:

   - Workspace folder in directory structure
   - Workspace purpose documented
   - Manual archive script referenced

4. **Updated FILE-INDEX.md**:
   - File locations updated to workspace
   - Statistics updated

### Success Criteria

- [ ] All 4 files updated
- [ ] Workspace references consistent
- [ ] Manual archive script referenced
- [ ] File locations updated correctly
- [ ] Documentation structure reflects workspace

---

## 🧪 Tests

### Test 1: Protocol Updates

```bash
# Check START_POINT references workspace
grep -i "work-space" LLM/protocols/IMPLEMENTATION_START_POINT.md | wc -l

# Check END_POINT references manual archive
grep -i "manual.*archive\|manual_archive" LLM/protocols/IMPLEMENTATION_END_POINT.md | wc -l
```

**Expected**: Protocols reference workspace and manual archive

### Test 2: Methodology Updates

```bash
# Check LLM-METHODOLOGY.md references workspace
grep -i "work-space\|workspace" LLM-METHODOLOGY.md | wc -l
```

**Expected**: Methodology documents workspace

### Test 3: File Index Updates

```bash
# Check FILE-INDEX.md references workspace
grep -i "work-space" LLM/index/FILE-INDEX.md | wc -l
```

**Expected**: File index references workspace

---

## 📝 Notes

- **Consistency**: Ensure all references use same workspace structure
- **Backward Compatibility**: Note that existing root files can remain (migration optional)
- **Clear Guidance**: Make it clear where new files should be created
- **Manual Archive Emphasis**: Highlight that archiving is user-controlled, not automatic

---

**Status**: Ready to Execute  
**Next**: Create EXECUTION_TASK and begin implementation
