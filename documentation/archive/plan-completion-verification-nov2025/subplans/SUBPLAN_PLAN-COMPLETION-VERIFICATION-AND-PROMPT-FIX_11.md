# SUBPLAN: Create validate_plan_completion.py

**Mother Plan**: PLAN_PLAN-COMPLETION-VERIFICATION-AND-PROMPT-FIX.md  
**Achievement Addressed**: Achievement 1.1 (Create `validate_plan_completion.py`)  
**Status**: In Progress  
**Created**: 2025-11-08  
**Estimated Effort**: 2-3 hours

---

## 🎯 Objective

Create validation script to verify all achievements in a PLAN are complete. This script will check each achievement's completion status (SUBPLAN exists, EXECUTION_TASK exists, deliverables exist), calculate completion percentage, identify pending achievements, and return appropriate exit codes. This is the foundation for automated PLAN completion verification.

**Contribution to PLAN**: This is Priority 1 (Core Completion Verification) that creates the foundation for all other achievements. By creating this script, we enable automated completion detection, which is required for fixing the prompt generator bugs and enabling proper completion workflow.

---

## 📋 What Needs to Be Created

### Files to Create

1. **LLM/scripts/validation/validate_plan_completion.py**
   - Parse PLAN to extract all achievements
   - For each achievement, check:
     - SUBPLAN exists (in root or archive)
     - EXECUTION_TASK exists (in root or archive)
     - Deliverables exist (if specified)
     - Achievement marked complete in PLAN (optional check)
   - Calculate completion percentage (X/Y achievements)
   - Identify pending achievements
   - Return exit code (0 = complete, 1 = incomplete)
   - Provide actionable error messages

### Content to Include

**validate_plan_completion.py**:
- Function to parse PLAN and extract all achievements
- Function to check achievement completion status (SUBPLAN, EXECUTION_TASK, deliverables)
- Function to check archive location and search archived files
- Function to calculate completion percentage
- Function to identify pending achievements
- Main function with CLI interface
- Error reporting with actionable messages
- Exit codes (0 = complete, 1 = incomplete)

---

## 📝 Approach

**Strategy**: Create validation script following patterns from existing validation scripts (`validate_achievement_completion.py`, `validate_mid_plan.py`).

**Method**:

1. **Review Existing Validation Scripts**: Study `validate_achievement_completion.py` and `validate_mid_plan.py` for patterns
2. **Create Core Functions**: Implement achievement parsing, completion checking, archive searching
3. **Implement Completion Logic**: Check SUBPLAN, EXECUTION_TASK, deliverables for each achievement
4. **Add Reporting**: Generate completion percentage, pending achievements list
5. **Test Scripts**: Test with complete PLAN (`PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md`) and incomplete PLAN (`PLAN_METHODOLOGY-V2-ENHANCEMENTS.md`)

**Key Considerations**:

- **Consistency**: Script should follow patterns from existing validation scripts
- **Archive Support**: Must check both root directory and archive location
- **Error Messages**: Should be clear and actionable
- **Exit Codes**: 0 = complete, 1 = incomplete (standard practice)
- **Performance**: Should handle PLANs with many achievements efficiently

**Risks to Watch For**:

- Incomplete archive location parsing
- Missing edge cases (no achievements, all archived, etc.)
- Performance issues with large PLANs
- Incorrect completion detection logic

---

## 🧪 Tests Required (Validation Approach)

**Validation Method** (code work):

**Functionality Check**:
- [ ] Script parses PLAN correctly
- [ ] Script extracts all achievements
- [ ] Script checks SUBPLAN existence (root and archive)
- [ ] Script checks EXECUTION_TASK existence (root and archive)
- [ ] Script checks deliverables existence
- [ ] Script calculates completion percentage correctly
- [ ] Script identifies pending achievements correctly
- [ ] Exit code 0 for complete PLAN
- [ ] Exit code 1 for incomplete PLAN

**Integration Validation**:
- [ ] Script follows existing validation script patterns
- [ ] Error messages are clear and actionable
- [ ] Archive location parsing works correctly

**Review Against Requirements**:
- [ ] Achievement 1.1 requirements met
- [ ] Success criteria from PLAN met
- [ ] All deliverables present

**Verification Commands**:
```bash
# Verify script exists
ls -1 LLM/scripts/validation/validate_plan_completion.py

# Test with complete PLAN
python LLM/scripts/validation/validate_plan_completion.py PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md
# Expected: Exit code 0, "✅ PLAN Complete: 7/7 (100%)"

# Test with incomplete PLAN
python LLM/scripts/validation/validate_plan_completion.py PLAN_METHODOLOGY-V2-ENHANCEMENTS.md
# Expected: Exit code 1, "❌ PLAN Incomplete: X/Y (Z%)", pending achievements listed
```

---

## ✅ Expected Results

### Functional Changes

- **Validation Script Created**: `validate_plan_completion.py` file exists
- **Completion Detection**: Script correctly detects complete and incomplete PLANs
- **Reporting**: Script reports completion percentage and pending achievements
- **Exit Codes**: Script returns appropriate exit codes

### Observable Outcomes

- `validate_plan_completion.py` file exists
- Script works with complete PLANs (returns 0, reports 100%)
- Script works with incomplete PLANs (returns 1, reports percentage, lists pending)
- Error messages are clear and actionable

### Success Indicators

- ✅ validate_plan_completion.py file exists
- ✅ Script detects complete PLANs correctly
- ✅ Script detects incomplete PLANs correctly
- ✅ Completion percentage calculated accurately
- ✅ Pending achievements identified correctly
- ✅ All verification commands pass

---

## 🔍 Conflict Analysis with Other Subplans

**Review Existing Subplans**:
- None (this is the first achievement)

**Check for**:
- **Overlap**: No overlap (first achievement)
- **Conflicts**: None
- **Dependencies**: None (can work independently)
- **Integration**: This creates foundation for other achievements

**Analysis**:
- No conflicts detected
- Independent work (creating new script)
- Safe to proceed

**Result**: Safe to proceed

---

## 🔗 Dependencies

### Other Subplans
- None (independent work)

### External Dependencies
- Python standard library (pathlib, re, sys, argparse)
- Existing validation script patterns (for consistency)

### Prerequisite Knowledge
- Understanding of validation script patterns
- Understanding of PLAN structure
- Understanding of archive location format
- Understanding of achievement completion criteria

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

_None yet - will be created when execution starts_

**First Execution**: `EXECUTION_TASK_PLAN-COMPLETION-VERIFICATION-AND-PROMPT-FIX_11_01.md`

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] validate_plan_completion.py file created
- [ ] Script parses PLAN correctly
- [ ] Script checks achievement completion status correctly
- [ ] Script calculates completion percentage correctly
- [ ] Script identifies pending achievements correctly
- [ ] Exit codes work correctly (0 = complete, 1 = incomplete)
- [ ] All verification commands pass
- [ ] EXECUTION_TASK complete
- [ ] Ready for archive

---

## 📝 Notes

**Common Pitfalls**:
- Incomplete archive location parsing
- Missing edge cases (no achievements, all archived)
- Incorrect completion detection logic
- Performance issues with large PLANs

**Resources**:
- PLAN_PLAN-COMPLETION-VERIFICATION-AND-PROMPT-FIX.md (Achievement 1.1 section)
- LLM/scripts/validation/validate_achievement_completion.py (pattern reference)
- LLM/scripts/validation/validate_mid_plan.py (pattern reference)
- PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md (test case: complete PLAN)
- PLAN_METHODOLOGY-V2-ENHANCEMENTS.md (test case: incomplete PLAN)

---

## 📖 What to Read (Focus Rules)

**When working on this SUBPLAN**, follow these focus rules to minimize context:

**✅ READ ONLY**:
- This SUBPLAN file (complete file)
- Parent PLAN Achievement 1.1 section (28 lines)
- Active EXECUTION_TASKs (if any exist)
- Parent PLAN "Current Status & Handoff" section (17 lines)
- LLM/scripts/validation/validate_achievement_completion.py (for pattern reference - minimal reading)
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

- [ ] **EXECUTION_TASK_PLAN-COMPLETION-VERIFICATION-AND-PROMPT-FIX_11_01**: Status: In Progress

**Registration Workflow**:

1. When creating EXECUTION_TASK: Add to this list immediately
2. When archiving: Remove from this list

**Why**: Immediate parent awareness ensures SUBPLAN knows about its active EXECUTION_TASKs.

---

**Ready to Execute**: Create EXECUTION_TASK and begin work  
**Reference**: IMPLEMENTATION_START_POINT.md for workflows

