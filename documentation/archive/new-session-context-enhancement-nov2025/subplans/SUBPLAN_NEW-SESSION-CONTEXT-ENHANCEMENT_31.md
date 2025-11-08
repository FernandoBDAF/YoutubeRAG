# SUBPLAN: Create Archive Validation Scripts

**Mother Plan**: PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md  
**Achievement Addressed**: Achievement 3.1 (Create Archive Validation Scripts)  
**Status**: In Progress  
**Created**: 2025-11-08 01:58 UTC  
**Estimated Effort**: 1-2 hours

---

## 🎯 Objective

Create validation scripts to verify archive location and archive structure compliance. This includes `validate_archive_location.py` to check archive location matches PLAN specification, and `validate_archive_structure.py` to verify archive structure exists. These scripts will catch archive location mismatches and missing archive structures, preventing procedural errors like those identified in the work review analysis.

**Contribution to PLAN**: This is part of Priority 3 (Validation Scripts) that creates automated validation for archive-related issues. By creating these scripts, we provide automated checks that catch archive location mismatches and missing archive structures before they cause problems.

---

## 📋 What Needs to Be Created

### Files to Create

1. **LLM/scripts/validation/validate_archive_location.py**
   - Check archive location in PLAN matches actual archive location
   - Verify archive structure exists (subplans/, execution/)
   - Check for duplicate files (root vs archive)
   - Report mismatches and issues
   - Provide fix suggestions

2. **LLM/scripts/validation/validate_archive_structure.py**
   - Verify archive directory exists
   - Verify subdirectories exist (subplans/, execution/)
   - Check archive location matches PLAN specification
   - Report missing structure

### Content to Include

**validate_archive_location.py**:
- Function to extract archive location from PLAN
- Function to check actual archive location
- Function to check for duplicate files
- Function to verify archive structure
- Main function to run all checks
- Error reporting with fix suggestions

**validate_archive_structure.py**:
- Function to extract archive location from PLAN
- Function to verify archive directory exists
- Function to verify subdirectories exist
- Main function to run checks
- Error reporting

---

## 📝 Approach

**Strategy**: Create two validation scripts that check archive location and structure compliance.

**Method**:

1. **Read Existing Validation Scripts**: Review `validate_mid_plan.py` for patterns and structure
2. **Create validate_archive_location.py**: Implement archive location validation
3. **Create validate_archive_structure.py**: Implement archive structure validation
4. **Test Scripts**: Test with existing PLANs (e.g., PLAN_FILE-MOVING-OPTIMIZATION.md)
5. **Verify Integration**: Ensure scripts work with existing validation infrastructure

**Key Considerations**:

- **Consistency**: Scripts should follow patterns from existing validation scripts
- **Error Messages**: Should be clear and actionable
- **Fix Suggestions**: Should provide specific commands to fix issues
- **Integration**: Should work with existing validation infrastructure

**Risks to Watch For**:

- Breaking existing validation infrastructure
- Incomplete validation coverage
- Unclear error messages
- Missing edge cases

---

## 🧪 Tests Required (Validation Approach)

**Validation Method** (code work):

**Functionality Check**:
- [ ] validate_archive_location.py works
- [ ] validate_archive_structure.py works
- [ ] Scripts catch archive location mismatches
- [ ] Scripts catch missing archive structures
- [ ] Scripts detect duplicate files

**Integration Validation**:
- [ ] Scripts follow existing validation script patterns
- [ ] Error messages are clear and actionable
- [ ] Fix suggestions are specific and helpful

**Review Against Requirements**:
- [ ] Achievement 3.1 requirements met
- [ ] Success criteria from PLAN met
- [ ] All deliverables present

**Verification Commands**:
```bash
# Verify scripts exist
ls -1 LLM/scripts/validation/validate_archive_location.py
ls -1 LLM/scripts/validation/validate_archive_structure.py

# Test with existing PLAN
python LLM/scripts/validation/validate_archive_location.py PLAN_FILE-MOVING-OPTIMIZATION.md
python LLM/scripts/validation/validate_archive_structure.py PLAN_FILE-MOVING-OPTIMIZATION.md

# Test with PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md
python LLM/scripts/validation/validate_archive_location.py PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md
python LLM/scripts/validation/validate_archive_structure.py PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md
```

---

## ✅ Expected Results

### Functional Changes

- **Validation Scripts Created**: Two new validation scripts for archive compliance
- **Automated Checks**: Archive location and structure automatically validated
- **Error Reporting**: Clear error messages with fix suggestions

### Observable Outcomes

- `validate_archive_location.py` file exists
- `validate_archive_structure.py` file exists
- Scripts catch archive location mismatches
- Scripts catch missing archive structures
- Scripts provide actionable fix suggestions

### Success Indicators

- ✅ validate_archive_location.py file exists
- ✅ validate_archive_structure.py file exists
- ✅ Scripts catch archive location mismatches
- ✅ Scripts catch missing archive structures
- ✅ All verification commands pass

---

## 🔍 Conflict Analysis with Other Subplans

**Review Existing Subplans**:
- SUBPLAN_01: Achievement 0.1 (Fix Archive Location Issues) - Complete
- SUBPLAN_11: Achievement 1.1 (Enhance PLAN_FILE-MOVING-OPTIMIZATION.md Context) - Complete
- SUBPLAN_12: Achievement 1.2 (Create PROJECT-CONTEXT.md) - Complete
- SUBPLAN_21: Achievement 2.1 (Update Prompt Generator with Project Context) - Complete
- SUBPLAN_22: Achievement 2.2 (Update PLAN Template with Project Context Section) - Complete
- SUBPLAN_23: Achievement 2.3 (Update Achievement Sections with Archive Instructions) - Complete

**Check for**:
- **Overlap**: No overlap (different achievements)
- **Conflicts**: None
- **Dependencies**: None (can work independently)
- **Integration**: This creates validation scripts that complement existing validation infrastructure

**Analysis**:
- No conflicts detected
- Independent work (creating new scripts)
- Safe to proceed

**Result**: Safe to proceed

---

## 🔗 Dependencies

### Other Subplans
- None (independent work)

### External Dependencies
- Python standard library (pathlib, re, sys)
- Existing validation script patterns (for consistency)

### Prerequisite Knowledge
- Understanding of validation script patterns
- Understanding of archive location format
- Understanding of archive structure requirements

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

_None yet - will be created when execution starts_

**First Execution**: `EXECUTION_TASK_NEW-SESSION-CONTEXT-ENHANCEMENT_31_01.md`

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] validate_archive_location.py file created
- [ ] validate_archive_structure.py file created
- [ ] Scripts catch archive location mismatches
- [ ] Scripts catch missing archive structures
- [ ] All verification commands pass
- [ ] EXECUTION_TASK complete
- [ ] Ready for archive

---

## 📝 Notes

**Common Pitfalls**:
- Incomplete validation coverage
- Unclear error messages
- Missing edge cases
- Breaking existing validation infrastructure

**Resources**:
- PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md (Achievement 3.1 section)
- EXECUTION_ANALYSIS_NEW-SESSION-WORK-REVIEW.md (archive location issues analysis)
- LLM/scripts/validation/validate_mid_plan.py (pattern reference)

---

## 📖 What to Read (Focus Rules)

**When working on this SUBPLAN**, follow these focus rules to minimize context:

**✅ READ ONLY**:
- This SUBPLAN file (complete file)
- Parent PLAN Achievement 3.1 section (24 lines)
- Active EXECUTION_TASKs (if any exist)
- Parent PLAN "Current Status & Handoff" section (18 lines)
- LLM/scripts/validation/validate_mid_plan.py (for pattern reference - minimal reading)

**❌ DO NOT READ**:
- Parent PLAN full content
- Other achievements in PLAN
- Other SUBPLANs
- Completed EXECUTION_TASKs (unless needed for context)
- Full validation directory (only pattern reference)

**Context Budget**: ~400 lines

**Why**: SUBPLAN defines HOW to achieve one achievement. Reading other achievements or full PLAN adds scope and confusion.

**📖 See**: `LLM/guides/FOCUS-RULES.md` for complete focus rules and examples.

---

## 🔄 Active EXECUTION_TASKs (Updated When Created)

**Current Active Work** (register EXECUTION_TASKs immediately when created):

- [ ] **EXECUTION_TASK_NEW-SESSION-CONTEXT-ENHANCEMENT_31_01**: Status: In Progress

**Registration Workflow**:

1. When creating EXECUTION_TASK: Add to this list immediately
2. When archiving: Remove from this list

**Why**: Immediate parent awareness ensures SUBPLAN knows about its active EXECUTION_TASKs.

---

**Ready to Execute**: Create EXECUTION_TASK and begin work  
**Reference**: IMPLEMENTATION_START_POINT.md for workflows


