# SUBPLAN: Achievement 0.3 - Test Bug Fix

**Parent Plan**: `PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md`  
**Achievement**: 0.3  
**Status**: ⏳ In Progress  
**Created**: 2025-11-08 00:50 UTC

---

## 📋 Objective

Create comprehensive test cases from the analysis document (`EXECUTION_ANALYSIS_PROMPT-GENERATOR-0.1-BUG.md`) to validate the bug fix implemented in Achievements 0.1 and 0.2. Ensure the fix works correctly with `PLAN_API-REVIEW-AND-TESTING.md` (should return 3.3), test with other PLAN files to verify no regressions, and cover edge cases (missing section, various formats).

---

## 🎯 Deliverables

1. **Enhanced Test Suite** (`tests/LLM/scripts/generation/test_generate_prompt.py`):
   - Additional test cases from analysis document
   - Regression tests with other PLAN files
   - Edge case tests (archive fallback, root fallback)
   - All tests passing

2. **Test Results Documentation**:
   - Verification that `PLAN_API-REVIEW-AND-TESTING.md` returns 3.3
   - Verification that other PLANs still work correctly
   - Confirmation of edge case handling

---

## 🔍 Approach

### Step 1: Review Analysis Document Test Cases

From `EXECUTION_ANALYSIS_PROMPT-GENERATOR-0.1-BUG.md`, identify test cases:

1. **Current Issue Test**:
   - Input: `PLAN_API-REVIEW-AND-TESTING.md`
   - Expected: Achievement 3.3
   - Status: Already covered in `test_real_plan_file`

2. **Status Section Format Variations**:
   - `⏳ Next: Achievement X.Y`
   - `**What's Next**: Achievement X.Y`
   - `Next: Achievement X.Y`
   - Status: Already covered in `test_handoff_section_format_variations`

3. **Missing Status Section**:
   - PLAN without "Current Status & Handoff"
   - Should fall back to full file search
   - Status: Already covered in `test_fallback_to_full_file`

4. **Archive Fallback** (NEW):
   - PLAN with archived SUBPLANs
   - Should detect next unarchived achievement
   - Status: **NOT COVERED** - Need to add

5. **Root Fallback** (NEW):
   - PLAN without archive
   - Should detect next missing SUBPLAN in root
   - Status: **NOT COVERED** - Need to add

6. **Regression Tests with Other PLANs** (NEW):
   - Test with `PLAN_METHODOLOGY-V2-ENHANCEMENTS.md`
   - Test with `PLAN_FILE-MOVING-OPTIMIZATION.md`
   - Test with `PLAN_GRAPH-CONSTRUCTION-REFACTOR.md`
   - Verify they still work correctly
   - Status: **NOT COVERED** - Need to add

### Step 2: Add Missing Test Cases

Add the following test classes/methods to `test_generate_prompt.py`:

1. **TestRegressionWithOtherPlans**:
   - `test_plan_methodology_v2_enhancements()`: Verify it works with another PLAN
   - `test_plan_file_moving_optimization()`: Verify it works with another PLAN
   - `test_plan_graph_construction_refactor()`: Verify it works with another PLAN

2. **TestArchiveFallback** (if `find_next_achievement_from_archive` exists):
   - `test_archive_fallback_when_handoff_missing()`: Test archive detection
   - `test_archive_fallback_priority()`: Verify archive is checked after handoff

3. **TestRootFallback** (if `find_next_achievement_from_root` exists):
   - `test_root_fallback_when_handoff_missing()`: Test root directory detection
   - `test_root_fallback_priority()`: Verify root is checked after handoff

4. **TestEdgeCases**:
   - `test_multiple_achievements_in_handoff()`: Handle multiple "Next" mentions
   - `test_achievement_with_parentheses()`: Handle "Achievement 3.3 (Description)"
   - `test_achievement_with_dash()`: Handle "Achievement 3.3 - Description"

### Step 3: Verify Bug Fix

Run the test with `PLAN_API-REVIEW-AND-TESTING.md`:
- Should return "3.3" (not "0.1")
- This validates the fix from Achievements 0.1 and 0.2

### Step 4: Run All Tests

Execute the full test suite:
```bash
python -m unittest discover -s tests/LLM/scripts/generation -p "test_*.py"
```

All tests should pass.

---

## 🧪 Tests Required

### Existing Tests (Already Implemented)

1. `TestExtractHandoffSection` (7 tests):
   - `test_normal_extraction`
   - `test_missing_section`
   - `test_empty_section`
   - `test_section_variations`
   - `test_stops_at_next_section`
   - `test_case_insensitive`
   - `test_multiple_sections_after`

2. `TestFindNextAchievementFromPlan` (6 tests):
   - `test_handoff_section_priority`
   - `test_handoff_section_format_variations`
   - `test_fallback_to_full_file`
   - `test_pattern_order`
   - `test_real_plan_file` (tests PLAN_API-REVIEW-AND-TESTING.md)
   - `test_no_match`

### New Tests to Add

1. **Regression Tests** (3 tests):
   - `test_plan_methodology_v2_enhancements`: Test with another PLAN file
   - `test_plan_file_moving_optimization`: Test with another PLAN file
   - `test_plan_graph_construction_refactor`: Test with another PLAN file

2. **Edge Case Tests** (3 tests):
   - `test_multiple_achievements_in_handoff`: Handle multiple "Next" mentions
   - `test_achievement_with_parentheses`: Handle "Achievement 3.3 (Description)"
   - `test_achievement_with_dash`: Handle "Achievement 3.3 - Description"

**Note**: Archive and root fallback tests are deferred if those functions don't exist in `generate_prompt.py`. We'll check the implementation first.

---

## 📊 Expected Results

### Success Criteria

1. ✅ All existing tests pass (13 tests)
2. ✅ New regression tests pass (3 tests)
3. ✅ New edge case tests pass (3 tests)
4. ✅ Total: 19 tests passing
5. ✅ `PLAN_API-REVIEW-AND-TESTING.md` returns "3.3" (bug fixed)
6. ✅ Other PLAN files work correctly (no regressions)

### Test Coverage

- **Handoff Section Extraction**: 7 tests
- **Achievement Detection**: 12 tests (6 existing + 6 new)
- **Total**: 19 tests

### Files Modified

- `tests/LLM/scripts/generation/test_generate_prompt.py`: Add 6 new test methods

---

## 🔄 Dependencies

- **Achievement 0.1**: Extract Handoff Section Function (✅ Complete)
- **Achievement 0.2**: Update Achievement Detection Logic (✅ Complete)
- **Analysis Document**: `EXECUTION_ANALYSIS_PROMPT-GENERATOR-0.1-BUG.md` (✅ Exists)

---

## 📝 Notes

- The bug fix is already implemented in Achievements 0.1 and 0.2
- This achievement focuses on **testing** the fix, not implementing it
- We'll add regression tests to ensure other PLANs still work
- Edge cases will be added based on the analysis document
- Archive/root fallback tests will be added only if those functions exist

---

## ✅ Completion Checklist

- [ ] Review analysis document test cases
- [ ] Add regression tests for other PLAN files (3 tests)
- [ ] Add edge case tests (3 tests)
- [ ] Run all tests and verify they pass
- [ ] Verify `PLAN_API-REVIEW-AND-TESTING.md` returns "3.3"
- [ ] Verify other PLAN files work correctly
- [ ] Document test results

---

**Estimated Effort**: 30 minutes  
**Priority**: HIGH (validates bug fix)


