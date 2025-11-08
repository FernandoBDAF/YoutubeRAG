# SUBPLAN: Test Coverage for generate_resume_prompt.py

**Mother Plan**: PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md  
**Achievement Addressed**: Achievement 1.4 (Test Coverage for `generate_resume_prompt.py`)  
**Status**: In Progress  
**Created**: 2025-01-27 17:00 UTC  
**Estimated Effort**: 1 hour

---

## 🎯 Objective

Achieve >90% test coverage for `generate_resume_prompt.py` by creating comprehensive unit tests for prompt generation logic, integration tests with paused PLANs, and edge case tests. This ensures the resume prompt generator is reliable and prevents regressions.

**Contribution to PLAN**: This achievement provides test coverage for the resume prompt generation script, ensuring it correctly extracts plan information and generates appropriate resume prompts. It uses the test infrastructure from Achievement 1.1.

---

## 📋 What Needs to Be Created

### Files to Create

1. **tests/LLM/scripts/generation/test_generate_resume_prompt.py**
   - Unit tests for `extract_plan_info()` function
   - Unit tests for `generate_resume_prompt()` function
   - Integration tests with paused PLAN files
   - Edge case tests (missing files, invalid inputs, various achievement formats)

### Functions/Classes to Test

**Unit Tests Needed**:
- `extract_plan_info()` - Test plan information extraction
  - Test "What's Next" / "Next" achievement detection
  - Test achievement title extraction
  - Test archive location extraction
  - Test feature name extraction
  - Test fallback to "X.Y" when no achievement found

- `generate_resume_prompt()` - Test prompt generation
  - Test prompt template formatting
  - Test with valid plan info
  - Test with missing achievement (fallback to "X.Y")
  - Test with missing title (fallback to "[Title]")

**Integration Tests Needed**:
- Full workflow with paused PLAN files (using fixtures)
- Test with various PLAN states (paused, in progress)
- Test CLI execution (main function)

**Edge Case Tests Needed**:
- Missing PLAN file
- Invalid file path
- Empty PLAN content
- PLAN without achievements
- PLAN without "What's Next" or "Next"
- Various achievement format variations

---

## 📝 Approach

**Strategy**: Create comprehensive test suite using test infrastructure from Achievement 1.1, test all code paths in extract_plan_info and generate_resume_prompt functions.

**Method**:

1. **Review Script Structure**:
   - Understand extract_plan_info() logic (achievement detection, title extraction, archive location)
   - Understand generate_resume_prompt() template formatting
   - Identify all code paths

2. **Create Test File**:
   - Use test infrastructure from Achievement 1.1 (fixtures, utilities)
   - Create test classes for each function
   - Structure: Unit tests → Integration tests → Edge cases

3. **Add Unit Tests**:
   - Test extract_plan_info() with achievement detection
   - Test achievement title extraction
   - Test archive location extraction
   - Test generate_resume_prompt() with various inputs

4. **Add Integration Tests**:
   - Test full workflow with paused PLAN files
   - Test CLI execution
   - Test with real PLAN structures

5. **Add Edge Case Tests**:
   - Missing files
   - Invalid inputs
   - Empty/malformed content
   - Missing achievement information

6. **Verify Coverage**:
   - Run coverage tool
   - Ensure >90% coverage
   - Identify and cover any gaps

**Key Considerations**:

- **Use Test Infrastructure**: Leverage fixtures from Achievement 1.1
- **Achievement Detection**: Test "What's Next" and "Next" patterns
- **Title Extraction**: Test achievement title extraction from PLAN
- **Template Formatting**: Verify prompt template is correctly filled
- **Error Handling**: Test graceful handling of edge cases
- **Realistic Tests**: Use real PLAN structures from fixtures

**Risks to Watch For**:

- Missing title extraction tests
- Not testing archive location extraction
- Missing edge cases (empty files, missing sections)

---

## 🧪 Tests Required

### Test File

- `tests/LLM/scripts/generation/test_generate_resume_prompt.py` (new file)

### Test Cases to Cover

**Unit Tests for extract_plan_info()**:
1. Test "What's Next" achievement detection
2. Test "Next" achievement detection
3. Test achievement title extraction
4. Test archive location extraction
5. Test feature name extraction
6. Test fallback to "X.Y" when no achievement found
7. Test fallback to "[Title]" when no title found

**Unit Tests for generate_resume_prompt()**:
1. Test prompt generation with valid plan info
2. Test prompt generation with missing achievement (fallback to "X.Y")
3. Test prompt generation with missing title (fallback to "[Title]")
4. Test template formatting (all placeholders filled)

**Integration Tests**:
1. Test full workflow with paused PLAN file
2. Test CLI execution (main function)
3. Test with real PLAN files from fixtures

**Edge Case Tests**:
1. Missing PLAN file
2. Invalid file path
3. Empty PLAN content
4. PLAN without achievements
5. PLAN without "What's Next" or "Next"
6. Malformed achievement formats

### Coverage Requirement

- **Target**: >90% coverage for `generate_resume_prompt.py`
- **Focus**: Critical functions (extract_plan_info, generate_resume_prompt, main)
- **Verification**: Run coverage tool and verify threshold met

---

## ✅ Expected Results

### Functional Changes

- **Test Coverage**: >90% coverage for `generate_resume_prompt.py`
- **Test Suite**: Comprehensive tests for all functions
- **Error Handling**: Edge cases and error paths tested
- **Integration**: Full workflow tested end-to-end

### Observable Outcomes

- **Coverage Report**: Shows >90% coverage
- **All Tests Pass**: New tests pass
- **Test File**: Created with comprehensive test classes
- **Documentation**: Tests serve as usage examples

### Success Indicators

- ✅ Unit tests for extract_plan_info() added
- ✅ Unit tests for generate_resume_prompt() added
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
- SUBPLAN_12: Achievement 1.2 - ✅ Complete (test coverage for generate_prompt.py)
- SUBPLAN_13: Achievement 1.3 - ✅ Complete (test coverage for generate_pause_prompt.py)

**Check for**:
- **Overlap**: No overlap - this is for different script
- **Conflicts**: No conflicts - uses same test infrastructure
- **Dependencies**: Depends on Achievement 1.1 (test infrastructure)
- **Integration**: Uses fixtures and utilities from Achievement 1.1

**Analysis**:
- No conflicts detected
- Builds on test infrastructure from Achievement 1.1
- Similar structure to Achievements 1.2 and 1.3 (can follow same pattern)
- Safe to proceed

**Result**: Safe to proceed

---

## 🔗 Dependencies

### Other Subplans
- Achievement 1.1 (Test Infrastructure Setup) - ✅ Complete (provides fixtures and utilities)

### External Dependencies
- pytest (for test framework)
- coverage.py (for coverage measurement)
- Test fixtures from Achievement 1.1

### Prerequisite Knowledge
- Understanding of `generate_resume_prompt.py` functions
- Understanding of pytest testing patterns
- Understanding of test fixtures from Achievement 1.1

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

_None yet - will be created when execution starts_

**First Execution**: `EXECUTION_TASK_PROMPT-GENERATOR-FIX-AND-TESTING_14_01.md`

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] Unit tests for extract_plan_info() added
- [ ] Unit tests for generate_resume_prompt() added
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
- Missing tests for achievement title extraction
- Not testing archive location extraction
- Missing edge cases (empty files, missing sections)

**Resources**:
- PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md (Achievement 1.4 section)
- Source code: `LLM/scripts/generation/generate_resume_prompt.py`
- Test infrastructure: `tests/LLM/scripts/conftest.py`, fixtures, utilities
- Similar pattern: `tests/LLM/scripts/generation/test_generate_pause_prompt.py`

---

## 📖 What to Read (Focus Rules)

**When working on this SUBPLAN**, follow these focus rules to minimize context:

**✅ READ ONLY**:
- This SUBPLAN file (complete file)
- Parent PLAN Achievement 1.4 section (9 lines)
- Active EXECUTION_TASKs (if any exist)
- Parent PLAN "Current Status & Handoff" section (27 lines)
- Source code: `LLM/scripts/generation/generate_resume_prompt.py`

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

- [ ] **EXECUTION_TASK_PROMPT-GENERATOR-FIX-AND-TESTING_14_01**: Status: In Progress

**Registration Workflow**:

1. When creating EXECUTION_TASK: Add to this list immediately
2. When archiving: Remove from this list

**Why**: Immediate parent awareness ensures SUBPLAN knows about its active EXECUTION_TASKs.

---

**Ready to Execute**: Create EXECUTION_TASK and begin work  
**Reference**: IMPLEMENTATION_START_POINT.md for workflows


