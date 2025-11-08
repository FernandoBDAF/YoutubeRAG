# SUBPLAN: Template Updates for Workspace

**Type**: SUBPLAN  
**Mother Plan**: PLAN_FILE-MOVING-WORKSPACE-AND-MANUAL-ARCHIVE.md  
**Plan**: FILE-MOVING-WORKSPACE-AND-MANUAL-ARCHIVE  
**Achievement Addressed**: Achievement 1.1 (Template Updates for Workspace)  
**Achievement**: 1.1  
**Status**: In Progress  
**Created**: 2025-01-28 00:40 UTC  
**Estimated Effort**: 1 hour

**Metadata Tags**: See `LLM/guides/METADATA-TAGS.md` for virtual organization system

---

## 🎯 Objective

Update all methodology templates to generate files in the workspace folder (`work-space/`) instead of the root directory. This ensures all new PLANs, SUBPLANs, and EXECUTION_TASKs are created in the organized workspace structure, preventing root directory pollution. This implements Achievement 1.1 and completes the workspace integration for file generation.

---

## 📋 What Needs to Be Created

### Files to Modify

- `LLM/templates/PLAN-TEMPLATE.md` - Update file location to `work-space/plans/`
- `LLM/templates/SUBPLAN-TEMPLATE.md` - Update file location to `work-space/subplans/`
- `LLM/templates/EXECUTION_TASK-TEMPLATE.md` - Update file location to `work-space/execution/`
- `LLM/templates/PROMPTS.md` - Update prompts to reference workspace

---

## 🎯 Approach

### Step 1: Update PLAN-TEMPLATE.md

**Changes Needed**:
1. Update "Archive Location" section to reference workspace
2. Add workspace guidance section
3. Update file location examples to show `work-space/plans/`
4. Add note about workspace folder structure

**Key Sections to Update**:
- Archive Location section
- Context for LLM Execution section
- File location references

### Step 2: Update SUBPLAN-TEMPLATE.md

**Changes Needed**:
1. Update file location references to `work-space/subplans/`
2. Update archive location references
3. Add workspace note

**Key Sections to Update**:
- File location examples
- Archive references

### Step 3: Update EXECUTION_TASK-TEMPLATE.md

**Changes Needed**:
1. Update file location references to `work-space/execution/`
2. Update archive location references
3. Add workspace note

**Key Sections to Update**:
- File location examples
- Archive references

### Step 4: Update PROMPTS.md

**Changes Needed**:
1. Update "Create New PLAN" prompt:
   - Change file path examples to `work-space/plans/PLAN_*.md`
   - Add workspace guidance
2. Update other prompts that reference file locations
3. Add workspace usage examples

**Key Sections to Update**:
- Create New PLAN prompt
- File path examples throughout

### Step 5: Verify All Updates

**Check**:
- All templates reference workspace
- File paths updated correctly
- Archive locations still work
- Examples are clear

---

## ✅ Expected Results

### Deliverables

1. **Updated PLAN-TEMPLATE.md**:
   - File location changed to `work-space/plans/`
   - Workspace guidance added
   - Archive location references updated

2. **Updated SUBPLAN-TEMPLATE.md**:
   - File location changed to `work-space/subplans/`
   - References updated

3. **Updated EXECUTION_TASK-TEMPLATE.md**:
   - File location changed to `work-space/execution/`
   - References updated

4. **Updated PROMPTS.md**:
   - Prompts reference workspace
   - File path examples updated

### Success Criteria

- [ ] All 4 templates updated
- [ ] File locations reference workspace
- [ ] Archive locations still work
- [ ] Examples are clear and consistent
- [ ] Workspace guidance included

---

## 🧪 Tests

### Test 1: Template File Locations

```bash
# Check PLAN template references workspace
grep -i "work-space/plans" LLM/templates/PLAN-TEMPLATE.md

# Check SUBPLAN template references workspace
grep -i "work-space/subplans" LLM/templates/SUBPLAN-TEMPLATE.md

# Check EXECUTION_TASK template references workspace
grep -i "work-space/execution" LLM/templates/EXECUTION_TASK-TEMPLATE.md
```

**Expected**: All templates reference workspace paths

### Test 2: PROMPTS.md Updates

```bash
# Check PROMPTS.md references workspace
grep -i "work-space" LLM/templates/PROMPTS.md | wc -l
```

**Expected**: PROMPTS.md contains workspace references

### Test 3: Archive References

```bash
# Verify archive references still present
grep -i "archive" LLM/templates/PLAN-TEMPLATE.md | head -3
```

**Expected**: Archive references still work

---

## 📝 Notes

- **Consistency**: Ensure all templates use same workspace structure
- **Backward Compatibility**: Existing files in root can remain (migration optional)
- **Clear Examples**: File path examples should be clear and consistent
- **Workspace Guidance**: Add brief explanation of workspace purpose in templates

---

**Status**: Ready to Execute  
**Next**: Create EXECUTION_TASK and begin implementation

