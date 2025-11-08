# SUBPLAN: Critical Path Test Coverage (70%)

**Type**: SUBPLAN  
**Mother Plan**: PLAN_PROMPT-GENERATOR-UX-AND-FOUNDATION.md  
**Plan**: PROMPT-GENERATOR-UX-AND-FOUNDATION  
**Achievement Addressed**: Achievement 1.1 (Critical Path Test Coverage)  
**Achievement**: 1.1  
**Status**: ✅ Complete  
**Created**: 2025-11-10 01:00 UTC  
**Estimated Effort**: 4-5 hours

**File Location**: `work-space/plans/PROMPT-GENERATOR-UX-AND-FOUNDATION/subplans/SUBPLAN_PROMPT-GENERATOR-UX-AND-FOUNDATION_11.md`

**Size**: 200-600 lines

---

## 🎯 Objective

Create comprehensive tests for core functions and recent bug fixes in `generate_prompt.py` to prevent regressions and enable safe refactoring. Focus on critical paths: PLAN parsing, achievement finding, conflict detection, multi-execution handling, trust flags, and completion detection. Target: Increase test coverage from 12.5% to 70%.

---

## 📋 Deliverables

### Test Files

1. **`test_core_parsing.py`** - PLAN parsing and achievement extraction

   - Test `parse_plan_file()`
   - Test achievement section extraction
   - Test current status parsing
   - Edge cases: malformed PLANs, missing sections

2. **`test_achievement_finding.py`** - Next achievement detection

   - Test `find_next_achievement_hybrid()`
   - Test with various PLAN states
   - Test with completed vs incomplete achievements
   - Edge cases: all complete, none complete, gaps

3. **`test_conflict_detection.py`** - PLAN/filesystem conflict detection (Bug #2 fix)

   - Test `detect_plan_filesystem_conflict()`
   - Test conflict scenarios (PLAN outdated, filesystem wrong)
   - Test no-conflict scenarios
   - Test trust flags (`--trust-plan`, `--trust-filesystem`)

4. **`test_multi_execution.py`** - Multi-execution handling (Bugs #6-7 fixes)

   - Test Bug #6 fix (multi-execution count from SUBPLAN table)
   - Test Bug #7 fix (create next execution from filesystem)
   - Test with 1, 3, 6 executions
   - Edge cases: incomplete executions, missing table

5. **`test_completion_detection.py`** - PLAN completion detection
   - Test when PLAN is complete
   - Test when more work remains
   - Test completion message generation
   - Test statistics extraction

### Coverage Report

- Coverage report showing 70%+ coverage
- Identify remaining untested code
- Plan for Achievement 1.3 (90% coverage)

---

## 🎨 Approach

**Strategy**: Test critical paths first (functions most likely to break), then recent bug fixes (prevent regressions), using real PLAN files as test data.

**Testing Philosophy**:

1. **Real data** - Use actual PLAN files from workspace
2. **Edge cases** - Test error conditions
3. **Regression prevention** - Test all bug fixes
4. **Integration** - Test workflows, not just functions

**Method**:

1. Identify critical functions (7 functions)
2. Create test file for each domain
3. Write 12+ test functions
4. Use real PLAN files as fixtures
5. Test happy paths + edge cases
6. Run coverage report
7. Verify 70%+ coverage

---

## 🔄 Execution Strategy

**Execution Count**: Single

**Rationale**: This is a cohesive testing effort that can be completed in one systematic pass. All tests are related (core functions + bug fixes) and can be implemented together efficiently.

**Execution Plan**:

**EXECUTION_TASK_11_01**: Critical Path Test Coverage Implementation

- Phase 1: Setup & Planning (30 min)
- Phase 2: Core Function Tests (90 min)
- Phase 3: Bug Fix Tests (90 min)
- Phase 4: Integration & Coverage (60 min)
- Estimated: 4-5 hours

**Dependencies**: None (builds on existing test infrastructure)

---

## 🧪 Detailed Test Plan

### Test Suite 1: Core Parsing (`test_core_parsing.py`)

**Functions to Test**:

- `parse_plan_file()` - Extract PLAN content
- `extract_achievement_section()` - Get achievement details
- `extract_current_status()` - Get current status

**Test Cases** (4 tests):

1. `test_parse_plan_file_valid()` - Parse valid PLAN
2. `test_parse_plan_file_missing()` - Handle missing file
3. `test_extract_achievement_section_found()` - Extract existing achievement
4. `test_extract_achievement_section_not_found()` - Handle missing achievement

**Fixtures**: Use real PLAN files from workspace

---

### Test Suite 2: Achievement Finding (`test_achievement_finding.py`)

**Functions to Test**:

- `find_next_achievement_hybrid()` - Find next incomplete achievement
- Achievement status detection logic

**Test Cases** (3 tests):

1. `test_find_next_achievement_first_incomplete()` - Find first incomplete
2. `test_find_next_achievement_all_complete()` - Handle all complete
3. `test_find_next_achievement_with_gaps()` - Handle gaps in numbering

**Fixtures**: Create mock PLANs with various completion states

---

### Test Suite 3: Conflict Detection (`test_conflict_detection.py`)

**Functions to Test**:

- `detect_plan_filesystem_conflict()` - Detect PLAN/filesystem drift
- Trust flag handling

**Test Cases** (5 tests):

1. `test_conflict_detection_plan_outdated()` - PLAN says next, filesystem says complete
2. `test_conflict_detection_filesystem_wrong()` - Filesystem incomplete, PLAN says complete
3. `test_conflict_detection_no_conflict()` - States match
4. `test_trust_plan_flag()` - --trust-plan bypasses conflict
5. `test_trust_filesystem_flag()` - --trust-filesystem bypasses conflict

**Fixtures**: Create test PLANs with known conflicts

---

### Test Suite 4: Multi-Execution (`test_multi_execution.py`)

**Functions to Test**:

- Bug #6 fix: Multi-execution count from SUBPLAN table
- Bug #7 fix: Create next execution from filesystem

**Test Cases** (6 tests):

1. `test_bug6_fix_count_from_subplan_table()` - Read planned count from table
2. `test_bug6_fix_table_parsing_accuracy()` - Parse table correctly (not Dependencies column)
3. `test_bug6_fix_suggest_correct_next()` - Suggest correct next execution
4. `test_bug7_fix_filesystem_scan()` - Scan filesystem for completed
5. `test_bug7_fix_highest_calculation()` - Find highest completed number
6. `test_bug7_fix_next_is_highest_plus_one()` - Calculate next as highest + 1

**Fixtures**: Create test SUBPLANs with Active EXECUTION_TASKs tables

---

### Test Suite 5: Completion Detection (`test_completion_detection.py`)

**Functions to Test**:

- PLAN completion detection
- `extract_plan_statistics()` - Statistics extraction (Achievement 0.2)
- Completion message generation

**Test Cases** (3 tests):

1. `test_plan_completion_detection()` - Detect when all achievements complete
2. `test_plan_incomplete_detection()` - Detect when work remains
3. `test_statistics_extraction()` - Extract correct statistics (already has 9 tests, add edge cases)

**Fixtures**: Use real completed PLANs

---

## ✅ Success Criteria

**Coverage**:

- ✅ Test coverage increases from 12.5% to 70%+
- ✅ All 7 critical functions tested
- ✅ All recent bug fixes tested (Bugs #6-11)
- ✅ 12+ new test functions added

**Quality**:

- ✅ All tests passing (100%)
- ✅ Tests use real PLAN files
- ✅ Edge cases covered
- ✅ Integration tests included

**Regression Prevention**:

- ✅ Bug #6 fix tested (can't regress)
- ✅ Bug #7 fix tested (can't regress)
- ✅ Bug #8 fix tested (emoji-agnostic)
- ✅ Bug #9 fix tested (shared module)
- ✅ Bug #10-11 fixes tested (path handling)

**Documentation**:

- ✅ Test files well-documented
- ✅ Coverage report generated
- ✅ Gaps identified for Achievement 1.3

---

## 🚨 Risks & Mitigations

### Risk 1: Tests Break Existing Functionality

**Mitigation**:

- Run existing tests first (baseline)
- Ensure all existing tests still pass
- Only add new tests, don't modify existing

### Risk 2: Hard to Test Complex Functions

**Mitigation**:

- Use real PLAN files as fixtures
- Mock filesystem operations
- Test one aspect at a time
- Integration tests for full workflows

### Risk 3: Coverage Target Too Ambitious

**Mitigation**:

- Focus on critical paths first
- 70% is realistic (not 90%)
- Achievement 1.3 will reach 90%
- Incremental progress

---

## 📚 Context & References

**Related Work**:

- Achievement 0.1-0.3: Created 49 tests (template to follow)
- `EXECUTION_ANALYSIS_GENERATE-PROMPT-COMPLETE-AUDIT.md` (test plan, 47+ tests needed)
- `work-space/analyses/implementation_automation/INDEX.md` (all bug documentation)

**Bug Documentation**:

- Bug #2: `EXECUTION_ANALYSIS_PROMPT-GENERATOR-CONFLICT-DETECTION.md`
- Bugs #3-4: `EXECUTION_ANALYSIS_EXECUTION-STATUS-DETECTION-BUGS.md`
- Bugs #6-7: `EXECUTION_ANALYSIS_SEVEN-BUGS-FINAL-SYNTHESIS.md`
- Bug #8: `EXECUTION_ANALYSIS_SUBPLAN-EXTRACTION-BUG-8.md`
- Bugs #9-11: Individual analyses in `implementation_automation/`

**Code Locations**:

- `LLM/scripts/generation/generate_prompt.py` (1,920 lines, 24 functions)
- `tests/LLM/scripts/generation/` (existing test files)
- `tests/LLM/scripts/conftest.py` (shared fixtures)

**Templates**:

- `LLM/templates/SUBPLAN-TEMPLATE.md`
- `LLM/templates/EXECUTION_TASK-TEMPLATE.md`

---

## 🎯 Expected Results

**After Completion**:

1. **Test Coverage Report**:

   ```
   generate_prompt.py
   ├── Tested: 70%+ (17 of 24 functions)
   ├── Untested: 30% (7 functions)
   └── Critical paths: 100% covered
   ```

2. **Regression Prevention**:

   - Bug #6 fix: ✅ Tested (can't regress)
   - Bug #7 fix: ✅ Tested (can't regress)
   - Bug #8 fix: ✅ Tested (emoji-agnostic works)
   - Bug #9 fix: ✅ Tested (shared module works)
   - Bug #10-11 fixes: ✅ Tested (path handling correct)

3. **Safe Refactoring**:

   - Can modify code confidently
   - Tests catch regressions
   - Ready for Achievement 2.1 (module extraction)

4. **Quality Metrics**:
   - 12+ new tests
   - 100% passing
   - Real PLAN files used
   - Edge cases covered

---

**Status**: ✅ Design Complete, Ready for Execution  
**Next Step**: Create EXECUTION_TASK_PROMPT-GENERATOR-UX-AND-FOUNDATION_11_01.md  
**Estimated Time**: 4-5 hours  
**Confidence**: High (clear test plan, existing test infrastructure)
