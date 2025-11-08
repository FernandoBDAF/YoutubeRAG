# SUBPLAN: Fix Naming Convention Violations

**Type**: SUBPLAN  
**Mother Plan**: PLAN_ROOT-PLANS-COMPLIANCE-AND-ORGANIZATION.md  
**Plan**: ROOT-PLANS-COMPLIANCE-AND-ORGANIZATION  
**Achievement Addressed**: Achievement 1.2 (Fix Naming Convention Violations)  
**Achievement**: 1.2  
**Status**: In Progress  
**Created**: 2025-11-08  
**Estimated Effort**: 1-2 hours

**Metadata Tags**: See `LLM/guides/METADATA-TAGS.md` for virtual organization system

**File Location**: `work-space/subplans/SUBPLAN_ROOT-PLANS-COMPLIANCE-AND-ORGANIZATION_12.md`

---

## 🎯 Objective

Identify and fix any naming convention violations in SUBPLAN, EXECUTION_TASK, and EXECUTION_ANALYSIS files in the root directory. Ensure all files follow the correct naming patterns and update any references in PLANs if files are renamed.

---

## 📋 What Needs to Be Created

### Files to Check

- **SUBPLAN files** (35 files in root): Check naming pattern `SUBPLAN_<FEATURE>_<NUMBER>.md`
- **EXECUTION_TASK files** (36 files in root): Check naming pattern `EXECUTION_TASK_<FEATURE>_<SUBPLAN>_<EXECUTION>.md`
- **EXECUTION_ANALYSIS files** (17 files in root): Check naming pattern `EXECUTION_ANALYSIS_<TOPIC>.md`

### Files to Create

- Naming violation report: Document any violations found and fixes applied

### Files to Modify

- Any files that need renaming (if violations found)
- PLAN files (if references need updating after renaming)

---

## 📝 Approach

**Strategy**: Systematic naming convention check using audit report, then fix violations

**Method**:

1. **Read Audit Report**:

   - Use `EXECUTION_ANALYSIS_ROOT-PLANS-AUDIT.md` for complete file list
   - Extract all SUBPLAN, EXECUTION_TASK, and EXECUTION_ANALYSIS file names

2. **Check Naming Conventions**:

   - **SUBPLAN pattern**: `SUBPLAN_<FEATURE>_<NUMBER>.md`
     - Feature name should match parent PLAN feature (kebab-case)
     - Number should be numeric (01, 02, etc.)
   - **EXECUTION_TASK pattern**: `EXECUTION_TASK_<FEATURE>_<SUBPLAN>_<EXECUTION>.md`
     - Feature name should match parent PLAN feature
     - SUBPLAN should match SUBPLAN number (01, 02, etc.)
     - EXECUTION should be numeric (01, 02, etc.)
   - **EXECUTION_ANALYSIS pattern**: `EXECUTION_ANALYSIS_<TOPIC>.md`
     - Topic should be descriptive (kebab-case)

3. **Identify Violations**:

   - Compare actual filenames against expected patterns
   - Document each violation with:
     - Current filename
     - Expected filename
     - Reason for violation

4. **Fix Violations**:

   - Rename files to correct naming convention
   - Update any references in PLAN files
   - Verify no broken references

5. **Create Report**:
   - Document all violations found
   - Document all fixes applied
   - List any files that couldn't be fixed (with reason)

**Key Considerations**:

- Feature names should match parent PLAN feature name (extracted from PLAN filename)
- Numbers should be zero-padded (01, 02, not 1, 2)
- Kebab-case for feature names and topics
- Check for case sensitivity issues
- Verify no duplicate filenames after renaming

---

## 🧪 Tests Required

**Note**: Documentation and file organization work, no code tests required.

**Verification**:

- Verify all files follow naming convention after fixes
- Verify no broken references in PLAN files
- Verify no duplicate filenames

---

## 📊 Expected Results

**Functional Changes**:

- All files renamed to follow correct naming convention (if violations found)
- All references in PLAN files updated (if files renamed)
- Naming violation report created

**Observable Outcomes**:

- All SUBPLAN files follow `SUBPLAN_<FEATURE>_<NUMBER>.md` pattern
- All EXECUTION*TASK files follow `EXECUTION_TASK*<FEATURE>_<SUBPLAN>_<EXECUTION>.md` pattern
- All EXECUTION*ANALYSIS files follow `EXECUTION_ANALYSIS*<TOPIC>.md` pattern
- Naming violation report documents findings and fixes

**Compliance Improvement**:

- 100% naming convention compliance
- No broken references
- Ready for file organization (Achievement 2.1)

---

## 🔗 Dependencies

**Prerequisites**:

- Achievement 0.1 complete (audit report provides file list)
- Achievement 1.1 complete (PLANs updated, may have references to check)

**Related Work**:

- Uses `EXECUTION_ANALYSIS_ROOT-PLANS-AUDIT.md` for file list
- Achievement 2.1 depends on this (needs correctly named files for organization)

---

## 📝 Execution Task Reference

- `EXECUTION_TASK_ROOT-PLANS-COMPLIANCE-AND-ORGANIZATION_12_01.md` - First execution

---

**Status**: In Progress  
**Next**: Execute naming convention check and fix violations
