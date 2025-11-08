# SUBPLAN: Test Coverage for generate_verify_prompt.py

**Mother Plan**: PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md  
**Achievement Addressed**: Achievement 1.5 (Test Coverage for `generate_verify_prompt.py`)  
**Status**: In Progress  
**Created**: 2025-01-27 18:00 UTC  
**Estimated Effort**: 1 hour

---

## 🎯 Objective

Achieve >90% test coverage for `generate_verify_prompt.py` by creating comprehensive unit tests for prompt generation logic, integration tests with validation script execution, and edge case tests. This ensures the verify prompt generator is reliable and prevents regressions.

**Contribution to PLAN**: This achievement provides test coverage for the verify prompt generation script, ensuring it correctly runs validation and generates appropriate fix prompts. It uses the test infrastructure from Achievement 1.1.

---

## 📋 What Needs to Be Created

### Files to Create

1. **tests/LLM/scripts/generation/test_generate_verify_prompt.py**
   - Unit tests for `run_validation()` function (mocked subprocess)
   - Unit tests for `generate_verify_prompt()` function
   - Integration tests with validation script execution
   - Edge case tests (missing files, validation errors, subprocess failures)

### Functions/Classes to Test

**Unit Tests Needed**:
- `run_validation()` - Test subprocess execution
  - Test successful validation (returncode 0)
  - Test failed validation (returncode != 0)
  - Test subprocess exception handling
  - Test output capture

- `generate_verify_prompt()` - Test prompt generation
  - Test with valid PLAN (no fixes needed)
  - Test with invalid PLAN (fixes needed)
  - Test fix instruction extraction from validation output
  - Test template formatting

**Integration Tests Needed**:
- Full workflow with actual validation script execution
- Test with real PLAN files
- Test CLI execution (main function)

**Edge Case Tests Needed**:
- Missing PLAN file
- Invalid file path
- Validation script not found
- Subprocess execution failure
- Validation output without "Fix Prompt:" section

---

## 📝 Approach

**Strategy**: Create comprehensive test suite using test infrastructure from Achievement 1.1, mock subprocess calls for unit tests, and use real validation script for integration tests.

**Method**:

1. **Review Script Structure**:
   - Understand run_validation() subprocess execution
   - Understand generate_verify_prompt() logic (valid vs invalid)
   - Understand fix instruction extraction
   - Identify all code paths

2. **Create Test File**:
   - Use test infrastructure from Achievement 1.1 (fixtures, utilities)
   - Create test classes for each function
   - Structure: Unit tests → Integration tests → Edge cases

3. **Add Unit Tests**:
   - Mock subprocess.run() for run_validation() tests
   - Test generate_verify_prompt() with various validation outputs
   - Test fix instruction extraction logic

4. **Add Integration Tests**:
   - Test full workflow with actual validation script
   - Test CLI execution
   - Test with real PLAN files

5. **Add Edge Case Tests**:
   - Missing files
   - Invalid inputs
   - Subprocess failures
   - Validation errors

6. **Verify Coverage**:
   - Run coverage tool
   - Ensure >90% coverage
   - Identify and cover any gaps

**Key Considerations**:

- **Use Test Infrastructure**: Leverage fixtures from Achievement 1.1
- **Mock Subprocess**: Use unittest.mock for subprocess.run() in unit tests
- **Real Validation**: Use actual validation script for integration tests
- **Error Handling**: Test graceful handling of subprocess failures
- **Fix Instruction Extraction**: Test parsing of validation output

**Risks to Watch For**:

- Not properly mocking subprocess calls
- Missing edge cases (subprocess failures, validation errors)
- Not testing fix instruction extraction logic

---

## 🧪 Tests Required

### Test File

- `tests/LLM/scripts/generation/test_generate_verify_prompt.py` (new file)

### Test Cases to Cover

**Unit Tests for run_validation()**:
1. Test successful validation (returncode 0)
2. Test failed validation (returncode != 0)
3. Test subprocess exception handling
4. Test output capture (stdout)

**Unit Tests for generate_verify_prompt()**:
1. Test with valid PLAN (no fixes needed)
2. Test with invalid PLAN (fixes needed)
3. Test fix instruction extraction from validation output
4. Test fallback when "Fix Prompt:" not in output
5. Test template formatting (all placeholders filled)

**Integration Tests**:
1. Test full workflow with actual validation script
2. Test CLI execution (main function)
3. Test with real PLAN files

**Edge Case Tests**:
1. Missing PLAN file
2. Invalid file path
3. Validation script not found
4. Subprocess execution failure
5. Validation output without "Fix Prompt:" section

### Coverage Requirement

- **Target**: >90% coverage for `generate_verify_prompt.py`
- **Focus**: Critical functions (run_validation, generate_verify_prompt, main)
- **Verification**: Run coverage tool and verify threshold met

---

## ✅ Expected Results

### Functional Changes

- **Test Coverage**: >90% coverage for `generate_verify_prompt.py`
- **Test Suite**: Comprehensive tests for all functions
- **Error Handling**: Edge cases and error paths tested
- **Integration**: Full workflow tested end-to-end

### Observable Outcomes

- **Coverage Report**: Shows >90% coverage
- **All Tests Pass**: New tests pass
- **Test File**: Created with comprehensive test classes
- **Documentation**: Tests serve as usage examples

### Success Indicators

- ✅ Unit tests for run_validation() added (with mocked subprocess)
- ✅ Unit tests for generate_verify_prompt() added
- ✅ Integration tests added
- ✅ Edge case tests added
- ✅ >90% coverage achieved
- ✅ All tests pass
- ✅ Test file created and validated

---

## 🔍 Conflict Analysis with Other Subplans

**Review Existing Subplans**:
- SUBPLAN_01-03: Achievements 0.1-0.3 - ✅ Complete
- SUBPLAN_11: Achievement 1.1 - ✅ Complete (test infrastructure)
- SUBPLAN_12-14: Achievements 1.2-1.4 - ✅ Complete (test coverage for other scripts)

**Check for**:
- **Overlap**: No overlap - this is for different script
- **Conflicts**: No conflicts - uses same test infrastructure
- **Dependencies**: Depends on Achievement 1.1 (test infrastructure)
- **Integration**: Uses fixtures and utilities from Achievement 1.1

**Analysis**:
- No conflicts detected
- Builds on test infrastructure from Achievement 1.1
- Similar structure to Achievements 1.2-1.4 (can follow same pattern)
- Safe to proceed

**Result**: Safe to proceed

---

## 🔗 Dependencies

### Other Subplans
- Achievement 1.1 (Test Infrastructure Setup) - ✅ Complete (provides fixtures and utilities)

### External Dependencies
- pytest (for test framework)
- coverage.py (for coverage measurement)
- unittest.mock (for mocking subprocess)
- Test fixtures from Achievement 1.1
- validate_mid_plan.py script (for integration tests)

### Prerequisite Knowledge
- Understanding of `generate_verify_prompt.py` functions
- Understanding of pytest testing patterns
- Understanding of unittest.mock for subprocess mocking
- Understanding of test fixtures from Achievement 1.1

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

_None yet - will be created when execution starts_

**First Execution**: `EXECUTION_TASK_PROMPT-GENERATOR-FIX-AND-TESTING_15_01.md`

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] Unit tests for run_validation() added (with mocked subprocess)
- [ ] Unit tests for generate_verify_prompt() added
- [ ] Integration tests added
- [ ] Edge case tests added
- [ ] >90% coverage achieved (verified with coverage tool)
- [ ] All tests pass
- [ ] Test file created and validated
- [ ] EXECUTION_TASK complete
- [ ] Ready for archive

---

## 📝 Notes

**Common Pitfalls**:
- Not properly mocking subprocess calls (use unittest.mock)
- Missing edge cases (subprocess failures, validation errors)
- Not testing fix instruction extraction logic

**Resources**:
- PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md (Achievement 1.5 section)
- Source code: `LLM/scripts/generation/generate_verify_prompt.py`
- Test infrastructure: `tests/LLM/scripts/conftest.py`, fixtures, utilities
- Similar pattern: `tests/LLM/scripts/generation/test_generate_resume_prompt.py`

---

## 📖 What to Read (Focus Rules)

**When working on this SUBPLAN**, follow these focus rules to minimize context:

**✅ READ ONLY**:
- This SUBPLAN file (complete file)
- Parent PLAN Achievement 1.5 section (13 lines)
- Active EXECUTION_TASKs (if any exist)
- Parent PLAN "Current Status & Handoff" section (27 lines)
- Source code: `LLM/scripts/generation/generate_verify_prompt.py`

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

- [ ] **EXECUTION_TASK_PROMPT-GENERATOR-FIX-AND-TESTING_15_01**: Status: In Progress

**Registration Workflow**:

1. When creating EXECUTION_TASK: Add to this list immediately
2. When archiving: Remove from this list

**Why**: Immediate parent awareness ensures SUBPLAN knows about its active EXECUTION_TASKs.

---

**Ready to Execute**: Create EXECUTION_TASK and begin work  
**Reference**: IMPLEMENTATION_START_POINT.md for workflows


