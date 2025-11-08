# SUBPLAN: Test Coverage for generate_prompt.py

**Mother Plan**: PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md  
**Achievement Addressed**: Achievement 1.2 (Test Coverage for `generate_prompt.py`)  
**Status**: In Progress  
**Created**: 2025-01-27 15:00 UTC  
**Estimated Effort**: 2 hours

---

## 🎯 Objective

Achieve >90% test coverage for `generate_prompt.py` by adding comprehensive unit tests for `find_next_achievement_hybrid()`, integration tests for full prompt generation, and edge case tests (missing files, invalid inputs). This builds on existing tests for `extract_handoff_section()` and `find_next_achievement_from_plan()` to ensure complete coverage and prevent regressions.

**Contribution to PLAN**: This achievement provides comprehensive test coverage for the core prompt generation script, ensuring reliability and preventing future bugs. It uses the test infrastructure created in Achievement 1.1.

---

## 📋 What Needs to Be Created

### Files to Modify

1. **tests/LLM/scripts/generation/test_generate_prompt.py**
   - Add unit tests for `find_next_achievement_hybrid()`
   - Add integration tests for full prompt generation workflow
   - Add edge case tests (missing files, invalid inputs, error handling)
   - Ensure >90% coverage for `generate_prompt.py`

### Functions/Classes to Test

**Unit Tests Needed**:
- `find_next_achievement_hybrid()` - Test hybrid approach (handoff → archive → root)
- `find_next_achievement_from_archive()` - Test archive-based detection
- `find_next_achievement_from_root()` - Test root directory detection
- `parse_plan_file()` - Test PLAN file parsing
- `detect_validation_scripts()` - Test validation script detection
- `generate_prompt()` - Test full prompt generation

**Integration Tests Needed**:
- Full prompt generation workflow (file → achievement → prompt)
- Error handling (missing files, invalid inputs)
- Edge cases (empty files, malformed PLANs)

**Edge Case Tests Needed**:
- Missing PLAN file
- Invalid file paths
- Empty PLAN content
- Malformed achievement formats
- Missing handoff section
- Missing archive location

---

## 📝 Approach

**Strategy**: Build on existing test infrastructure, add missing test coverage systematically, use fixtures from Achievement 1.1.

**Method**:

1. **Review Existing Tests**:
   - Understand what's already tested (extract_handoff_section, find_next_achievement_from_plan)
   - Identify gaps in coverage
   - Plan additional tests needed

2. **Add Unit Tests for find_next_achievement_hybrid()**:
   - Test hybrid approach (handoff section priority)
   - Test fallback to archive detection
   - Test fallback to root detection
   - Test with various PLAN states

3. **Add Integration Tests**:
   - Test full prompt generation workflow
   - Test with real PLAN files (using fixtures)
   - Test error handling paths
   - Test edge cases

4. **Add Edge Case Tests**:
   - Missing files
   - Invalid inputs
   - Empty/malformed content
   - Error handling

5. **Verify Coverage**:
   - Run coverage tool
   - Ensure >90% coverage
   - Identify and cover any gaps

**Key Considerations**:

- **Use Test Infrastructure**: Leverage fixtures from Achievement 1.1
- **Build on Existing**: Extend current test file, don't duplicate
- **Coverage Focus**: Aim for >90% coverage, focus on critical paths
- **Realistic Tests**: Use real PLAN structures from fixtures
- **Error Handling**: Test both success and failure paths

**Risks to Watch For**:

- Over-testing trivial code (focus on critical paths)
- Missing edge cases (comprehensive error handling)
- Not using fixtures (should leverage test infrastructure)

---

## 🧪 Tests Required

### Test File

- `tests/LLM/scripts/generation/test_generate_prompt.py` (extend existing)

### Test Cases to Cover

**Unit Tests for find_next_achievement_hybrid()**:
1. Test hybrid approach with handoff section present
2. Test fallback to archive when handoff missing
3. Test fallback to root when archive missing
4. Test with various PLAN states
5. Test error handling

**Integration Tests**:
1. Test full prompt generation with valid PLAN
2. Test prompt generation with missing file
3. Test prompt generation with invalid input
4. Test with real PLAN files from fixtures

**Edge Case Tests**:
1. Missing PLAN file
2. Invalid file path
3. Empty PLAN content
4. Malformed achievement format
5. Missing handoff section
6. Missing archive location

### Coverage Requirement

- **Target**: >90% coverage for `generate_prompt.py`
- **Focus**: Critical functions (generate_prompt, find_next_achievement_hybrid, etc.)
- **Verification**: Run coverage tool and verify threshold met

---

## ✅ Expected Results

### Functional Changes

- **Test Coverage**: >90% coverage for `generate_prompt.py`
- **Test Suite**: Comprehensive tests for all critical functions
- **Error Handling**: Edge cases and error paths tested
- **Integration**: Full workflow tested end-to-end

### Observable Outcomes

- **Coverage Report**: Shows >90% coverage
- **All Tests Pass**: New tests pass, existing tests still pass
- **Test File**: Extended with new test classes/methods
- **Documentation**: Tests serve as usage examples

### Success Indicators

- ✅ Unit tests for `find_next_achievement_hybrid()` added
- ✅ Integration tests for full prompt generation added
- ✅ Edge case tests added
- ✅ >90% coverage achieved
- ✅ All tests pass
- ✅ No regressions in existing tests

---

## 🔍 Conflict Analysis with Other Subplans

**Review Existing Subplans**:
- SUBPLAN_01: Achievement 0.1 - ✅ Complete
- SUBPLAN_02: Achievement 0.2 - ✅ Complete
- SUBPLAN_03: Achievement 0.3 - ✅ Complete
- SUBPLAN_11: Achievement 1.1 - ✅ Complete (test infrastructure)

**Check for**:
- **Overlap**: No overlap - this extends existing tests
- **Conflicts**: No conflicts - builds on Achievement 1.1 infrastructure
- **Dependencies**: Depends on Achievement 1.1 (test infrastructure)
- **Integration**: Uses fixtures and utilities from Achievement 1.1

**Analysis**:
- No conflicts detected
- Builds on test infrastructure from Achievement 1.1
- Extends existing test file (no duplication)
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
- Understanding of `generate_prompt.py` functions
- Understanding of pytest testing patterns
- Understanding of test fixtures from Achievement 1.1

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

_None yet - will be created when execution starts_

**First Execution**: `EXECUTION_TASK_PROMPT-GENERATOR-FIX-AND-TESTING_12_01.md`

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] Unit tests for `find_next_achievement_hybrid()` added
- [ ] Integration tests for full prompt generation added
- [ ] Edge case tests added
- [ ] >90% coverage achieved (verified with coverage tool)
- [ ] All tests pass
- [ ] No regressions in existing tests
- [ ] EXECUTION_TASK complete
- [ ] Ready for archive

---

## 📝 Notes

**Common Pitfalls**:
- Not using fixtures from Achievement 1.1 (should leverage infrastructure)
- Missing edge cases (comprehensive error handling needed)
- Not verifying coverage (must run coverage tool)

**Resources**:
- PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md (Achievement 1.2 section)
- Existing tests: `tests/LLM/scripts/generation/test_generate_prompt.py`
- Test infrastructure: `tests/LLM/scripts/conftest.py`, fixtures, utilities
- Source code: `LLM/scripts/generation/generate_prompt.py`

---

## 📖 What to Read (Focus Rules)

**When working on this SUBPLAN**, follow these focus rules to minimize context:

**✅ READ ONLY**:
- This SUBPLAN file (complete file)
- Parent PLAN Achievement 1.2 section (11 lines)
- Active EXECUTION_TASKs (if any exist)
- Parent PLAN "Current Status & Handoff" section (27 lines)
- Existing test file (to understand current tests)

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

- [ ] **EXECUTION_TASK_PROMPT-GENERATOR-FIX-AND-TESTING_12_01**: Status: In Progress

**Registration Workflow**:

1. When creating EXECUTION_TASK: Add to this list immediately
2. When archiving: Remove from this list

**Why**: Immediate parent awareness ensures SUBPLAN knows about its active EXECUTION_TASKs.

---

**Ready to Execute**: Create EXECUTION_TASK and begin work  
**Reference**: IMPLEMENTATION_START_POINT.md for workflows


