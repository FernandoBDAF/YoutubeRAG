# SUBPLAN: Update References

**Type**: SUBPLAN  
**Mother Plan**: PLAN_ROOT-PLANS-COMPLIANCE-AND-ORGANIZATION.md  
**Plan**: ROOT-PLANS-COMPLIANCE-AND-ORGANIZATION  
**Achievement Addressed**: Achievement 2.2 (Update References)  
**Achievement**: 2.2  
**Status**: In Progress  
**Created**: 2025-11-08  
**Estimated Effort**: 1-2 hours

**Metadata Tags**: See `LLM/guides/METADATA-TAGS.md` for virtual organization system

**File Location**: `work-space/subplans/SUBPLAN_ROOT-PLANS-COMPLIANCE-AND-ORGANIZATION_22.md`

---

## 🎯 Objective

Update all references to moved files in PLAN documents, ACTIVE_PLANS.md, scripts, and documentation. Ensure all file paths point to work-space/ locations and verify all references work correctly.

---

## 📋 What Needs to Be Created

### Files to Update

- **ACTIVE_PLANS.md**: Update file paths from root to `work-space/plans/`
- **PLAN documents**: Update references to SUBPLAN and EXECUTION_TASK files
- **Scripts**: Update any script references to moved files
- **Documentation**: Update any documentation references

### Files to Create

- Reference update log: Document all references updated

### Files to Check

- Check for broken links in PLAN documents
- Verify script references work
- Verify documentation references work

---

## 📝 Approach

**Strategy**: Systematic reference update using search and replace, then verification

**Method**:

1. **Update ACTIVE_PLANS.md**:
   - Find all references to PLAN files in root
   - Update paths to `work-space/plans/`
   - Verify all PLAN references updated

2. **Update PLAN Documents**:
   - For each PLAN in `work-space/plans/`:
     - Find references to SUBPLAN files (should be `work-space/subplans/`)
     - Find references to EXECUTION_TASK files (should be `work-space/execution/`)
     - Update any root directory references
     - Check for broken links

3. **Update Script References**:
   - Check scripts in `LLM/scripts/` for file path references
   - Update any references to moved files
   - Verify scripts still work

4. **Update Documentation References**:
   - Check documentation files for file path references
   - Update any references to moved files
   - Verify documentation links work

5. **Verify References**:
   - Check for broken links
   - Verify all file paths are correct
   - Test script references
   - Test documentation links

6. **Create Update Log**:
   - Document all references updated
   - List files modified
   - Note any issues found

**Key Considerations**:

- File paths should use `work-space/plans/`, `work-space/subplans/`, `work-space/execution/`
- Relative paths should work from root directory
- Scripts may need path updates if they reference moved files
- Documentation may have @ references that need updating
- Some references may be in markdown links or code blocks

---

## 🧪 Tests Required

**Note**: Reference update work, no code tests required.

**Verification**:
- Verify all file paths updated correctly
- Verify no broken links
- Verify scripts work with new paths
- Verify documentation links work

---

## 📊 Expected Results

**Functional Changes**:
- ACTIVE_PLANS.md updated with new file paths
- PLAN documents updated with correct paths
- Script references updated (if any)
- Documentation references updated (if any)

**Observable Outcomes**:
- All file paths point to work-space/ locations
- No broken links in PLAN documents
- Scripts work with new file locations
- Documentation links work correctly

**Reference Compliance**:
- 100% of references updated
- All file paths correct
- No broken links
- Ready for final verification

---

## 🔗 Dependencies

**Prerequisites**:
- Achievement 2.1 complete (files moved to work-space/)

**Related Work**:
- Uses migration report from Achievement 2.1 for file locations
- Final achievement in Priority 2 (Organization and Migration)

---

## 📝 Execution Task Reference

- `EXECUTION_TASK_ROOT-PLANS-COMPLIANCE-AND-ORGANIZATION_22_01.md` - First execution

---

**Status**: In Progress  
**Next**: Execute reference updates systematically
