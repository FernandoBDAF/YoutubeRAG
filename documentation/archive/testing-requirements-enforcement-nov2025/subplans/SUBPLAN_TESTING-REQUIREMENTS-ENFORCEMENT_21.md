# SUBPLAN: Create validate_test_coverage.py Script

**Type**: SUBPLAN  
**Mother Plan**: PLAN_TESTING-REQUIREMENTS-ENFORCEMENT.md  
**Plan**: TESTING-REQUIREMENTS-ENFORCEMENT  
**Achievement Addressed**: Achievement 2.1 (Create `validate_test_coverage.py` Script)  
**Achievement**: 2.1  
**Status**: In Progress  
**Created**: 2025-01-28 03:15 UTC  
**Estimated Effort**: 2-3 hours

**Metadata Tags**: See `LLM/guides/METADATA-TAGS.md` for virtual organization system

**File Location**: `work-space/subplans/SUBPLAN_TESTING-REQUIREMENTS-ENFORCEMENT_21.md`

---

## 🎯 Objective

Create a validation script `validate_test_coverage.py` that enforces test file existence and coverage requirements for implementations. This script will check if test files exist, verify they have tests for new functions/classes, check coverage, and report missing tests with actionable fix prompts. This implements Achievement 2.1 and provides automated enforcement of testing requirements.

---

## 📋 What Needs to Be Created

### Files to Create

- `LLM/scripts/validation/validate_test_coverage.py` - Main validation script
  - Check if test file exists for implementation
  - Verify test file has tests for new functions/classes
  - Check test coverage (if pytest-cov available)
  - Report missing tests with actionable fix prompts
  - Support workspace files (`work-space/` directory)
  - Integration with achievement completion workflow

### Files to Modify

- None (new script creation)

---

## 📝 Approach

**Strategy**: Create a validation script following the pattern of existing validation scripts, with focus on test file detection, coverage checking, and actionable error reporting.

**Method**:

1. **Study Existing Validation Scripts**:
   - Review `validate_plan_completion.py` for structure and patterns
   - Review `validate_achievement_completion.py` for file checking logic
   - Understand exit codes and error reporting patterns

2. **Design Script Structure**:
   - Command-line interface (argparse)
   - Input: Implementation file path or achievement identifier
   - Output: Exit code (0 = pass, 1 = fail) + error messages
   - Support for workspace files (`work-space/` directory)

3. **Implement Test File Detection**:
   - Map implementation file to expected test file location
   - Check if test file exists in `tests/LLM/scripts/<domain>/`
   - Handle workspace files (map from `work-space/` to test location)

4. **Implement Test Coverage Checking**:
   - Check if pytest-cov is available
   - If available, run coverage check
   - Report coverage percentage
   - Warn if coverage <90%

5. **Implement Test Content Verification**:
   - Parse test file to find test classes/functions
   - Check if tests exist for new functions/classes in implementation
   - Report missing tests with actionable prompts

6. **Implement Error Reporting**:
   - Clear error messages
   - Actionable fix prompts
   - Integration with achievement completion workflow

7. **Test Script**:
   - Test with implementation that has tests (should pass)
   - Test with implementation without tests (should fail)
   - Test with partial coverage (should warn)
   - Test with workspace files

**Key Considerations**:

- Follow existing validation script patterns
- Support workspace files (`work-space/` directory)
- Provide actionable error messages
- Handle edge cases (missing files, invalid paths)
- Integration with achievement completion workflow

---

## 🧪 Tests Required

### Test File

- `tests/LLM/scripts/validation/test_validate_test_coverage.py` (to be created in future)

### Test Cases to Cover

1. Implementation with tests (should pass)
2. Implementation without tests (should fail with fix prompt)
3. Partial test coverage (should warn)
4. Test file in correct location
5. Workspace file support
6. Missing implementation file (error handling)
7. Invalid test file path (error handling)

### Test-First Requirement

- [ ] Tests written before implementation (TDD workflow preferred)
- [ ] Initial test run shows all failing
- [ ] Tests define success criteria

**Note**: For this achievement, we're creating the validation script itself. Test coverage for the script can be added in a future achievement.

---

## ✅ Expected Results

### Functional Changes

- Validation script created and functional
- Script checks test file existence
- Script verifies test coverage (if pytest-cov available)
- Script reports missing tests with actionable prompts
- Script supports workspace files

### Observable Outcomes

- Script can be run: `python LLM/scripts/validation/validate_test_coverage.py <file>`
- Script returns appropriate exit codes (0 = pass, 1 = fail)
- Script provides clear error messages
- Script integrates with achievement completion workflow

### Success Indicators

- Script created at `LLM/scripts/validation/validate_test_coverage.py`
- Script checks test file existence correctly
- Script verifies test coverage (if available)
- Script reports missing tests with actionable prompts
- Script supports workspace files
- Script tested with various scenarios
- Script follows existing validation script patterns

---

## 🔍 Conflict Analysis with Other Subplans

**Review Existing Subplans**:

- SUBPLAN_01: Achievement 0.1 (Complete) - No conflicts
- SUBPLAN_11: Achievement 1.1 (Complete) - No conflicts

**Check for**:

- **Overlap**: No overlap (different achievements)
- **Conflicts**: No conflicts (new script creation)
- **Dependencies**: Depends on templates being updated (Achievement 1.1 - complete)
- **Integration**: Results will be used in future achievements (methodology documentation)

**Analysis**:

- No conflicts detected
- Dependencies met (templates updated)
- Safe to proceed independently

**Result**: Safe to proceed

---

## 🔗 Dependencies

### Other Subplans

- SUBPLAN_11 (Achievement 1.1) - Templates updated (complete)

### External Dependencies

- `LLM/scripts/validation/validate_plan_completion.py` - Pattern reference
- `LLM/scripts/validation/validate_achievement_completion.py` - Pattern reference
- pytest-cov (optional, for coverage checking)
- Python 3.x standard library

### Prerequisite Knowledge

- Understanding of validation script patterns
- Knowledge of test file structure
- Understanding of coverage tools (pytest-cov)

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

- [ ] **EXECUTION_TASK_TESTING-REQUIREMENTS-ENFORCEMENT_21_01**: Status: In Progress

**First Execution**: `EXECUTION_TASK_TESTING-REQUIREMENTS-ENFORCEMENT_21_01.md`

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] Script created at `LLM/scripts/validation/validate_test_coverage.py`
- [ ] Script checks test file existence correctly
- [ ] Script verifies test coverage (if pytest-cov available)
- [ ] Script reports missing tests with actionable prompts
- [ ] Script supports workspace files
- [ ] Script tested with various scenarios
- [ ] Script follows existing validation script patterns
- [ ] EXECUTION_TASK complete
- [ ] Ready for archive

---

## 📝 Notes

**Key Context**:

- This is script creation work, following existing validation script patterns
- Focus on test file detection and coverage checking
- Provide actionable error messages
- Support workspace files for consistency

**Common Pitfalls**:

- Don't forget to support workspace files
- Don't make error messages too verbose
- Don't forget to handle edge cases (missing files, invalid paths)
- Don't forget to follow existing validation script patterns

**Resources**:

- `LLM/scripts/validation/validate_plan_completion.py` - Pattern reference
- `LLM/scripts/validation/validate_achievement_completion.py` - Pattern reference
- `tests/LLM/scripts/conftest.py` - Test infrastructure reference

---

## 📖 What to Read (Focus Rules)

**When working on this SUBPLAN**, follow these focus rules to minimize context:

**✅ READ ONLY**:

- This SUBPLAN file (complete file)
- Parent PLAN Achievement 2.1 section (29 lines)
- Active EXECUTION_TASKs (if any exist)
- Existing validation scripts (specific sections only)

**❌ DO NOT READ**:

- Parent PLAN full content
- Other achievements in PLAN
- Other SUBPLANs
- Completed EXECUTION_TASKs
- Full validation script files (only relevant sections)

**Context Budget**: ~400 lines

---

## 🔄 Active EXECUTION_TASKs (Updated When Created)

**Current Active Work** (register EXECUTION_TASKs immediately when created):

- [ ] **EXECUTION_TASK_TESTING-REQUIREMENTS-ENFORCEMENT_21_01**: Status: In Progress

**Registration Workflow**:

1. When creating EXECUTION_TASK: Add to this list immediately
2. When archiving: Remove from this list

---

**Ready to Execute**: Create EXECUTION_TASK and begin work  
**Reference**: IMPLEMENTATION_START_POINT.md for workflows

