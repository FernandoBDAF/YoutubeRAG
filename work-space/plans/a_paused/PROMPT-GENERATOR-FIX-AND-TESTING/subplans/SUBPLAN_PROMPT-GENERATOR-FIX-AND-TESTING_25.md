# SUBPLAN: Achievement 2.5 - Test Coverage for validate_mid_plan.py

**Mother Plan**: PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md  
**Achievement Addressed**: Achievement 2.5 (Test Coverage for validate_mid_plan.py)  
**Status**: In Progress  
**Created**: 2025-01-28 00:10 UTC  
**Estimated Effort**: 2 hours

---

## 🎯 Objective

Create comprehensive test coverage for `LLM/scripts/validation/validate_mid_plan.py` to ensure the script correctly validates PLAN compliance at mid-point (statistics accuracy, SUBPLAN registration, archive compliance).

---

## 📋 What Needs to Be Created

### Files to Create

1. **Test File**: `tests/LLM/scripts/validation/test_validate_mid_plan.py`
   - Unit tests for `extract_statistics()` function
   - Unit tests for `count_actual_subplans()` function
   - Unit tests for `count_actual_execution_tasks()` function
   - Unit tests for `get_archive_location()` function
   - Unit tests for `check_subplan_registration()` function
   - Unit tests for `validate_mid_plan()` function
   - Integration tests with various PLAN states
   - Edge case tests (missing files, wrong paths, invalid statistics)

---

## 🎯 Approach

### Step 1: Analyze Script Functions

Review `validate_mid_plan.py` to understand:
- `extract_statistics()`: Extracts statistics from PLAN Subplan Tracking section
- `count_actual_subplans()`: Counts actual SUBPLAN files (root + archive)
- `count_actual_execution_tasks()`: Counts actual EXECUTION_TASK files (root + archive)
- `get_archive_location()`: Extracts archive location from PLAN file
- `check_subplan_registration()`: Checks if all SUBPLANs are registered in PLAN
- `validate_mid_plan()`: Main validation function
- `main()`: CLI entry point with argument parsing

### Step 2: Create Test Fixtures

Create temporary files for testing:
- Sample PLAN files with various statistics
- Sample SUBPLAN files (root and archived)
- Sample EXECUTION_TASK files (root and archived)
- Sample archive directories

### Step 3: Write Unit Tests

**For `extract_statistics()`**:
- Test extracting SUBPLAN count
- Test extracting EXECUTION_TASK count
- Test missing statistics section
- Test various format variations

**For `count_actual_subplans()`**:
- Test counting SUBPLANs in root
- Test counting SUBPLANs in archive
- Test counting both root and archived
- Test with different feature names
- Test with no SUBPLANs

**For `count_actual_execution_tasks()`**:
- Test counting EXECUTION_TASKs in root
- Test counting EXECUTION_TASKs in archive
- Test counting both root and archived
- Test with different feature names
- Test with no EXECUTION_TASKs

**For `get_archive_location()`**:
- Test extracting archive location from PLAN
- Test fallback to inferred location
- Test various archive location formats

**For `check_subplan_registration()`**:
- Test all SUBPLANs registered
- Test some SUBPLANs unregistered
- Test SUBPLANs in root and archive
- Test with no SUBPLANs

**For `validate_mid_plan()`**:
- Test all checks pass
- Test statistics mismatch (SUBPLAN count)
- Test statistics mismatch (EXECUTION_TASK count)
- Test unregistered SUBPLANs (warning)
- Test missing archive location
- Test multiple issues
- Test missing PLAN file

### Step 4: Write Integration Tests

- Test with complete valid PLAN (all files present, statistics accurate)
- Test with invalid PLAN (statistics mismatch, unregistered SUBPLANs)
- Test CLI argument parsing (@ prefix handling)
- Test exit codes (0 for pass, 1 for fail)
- Test error handling (exceptions)
- Test --generate-fix-prompt flag

### Step 5: Write Edge Case Tests

- Test missing PLAN file
- Test PLAN without statistics section
- Test PLAN with wrong statistics format
- Test archive location with special characters
- Test SUBPLANs with different naming patterns

### Step 6: Verify Coverage

- Run tests: `python -m unittest tests.LLM.scripts.validation.test_validate_mid_plan -v`
- Check coverage: Target >90% coverage
- All tests should pass

---

## ✅ Expected Results

### Deliverables

1. ✅ Test file created: `tests/LLM/scripts/validation/test_validate_mid_plan.py`
2. ✅ Unit tests for all functions
3. ✅ Integration tests with various PLAN states
4. ✅ Edge case tests
5. ✅ Test coverage >90%

### Success Criteria

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All edge case tests pass
- [ ] Test coverage >90%
- [ ] Tests follow existing test patterns in project

---

## 🧪 Tests

### Test 1: File Exists

```bash
# Verify test file exists
ls -1 tests/LLM/scripts/validation/test_validate_mid_plan.py
```

### Test 2: Tests Run

```bash
# Run tests
python -m unittest tests.LLM.scripts.validation.test_validate_mid_plan -v
```

### Test 3: Coverage Check

```bash
# Verify all tests pass
python -m unittest tests.LLM.scripts.validation.test_validate_mid_plan -v | grep -E "(OK|FAILED)"
```

---

## 📝 Notes

- Follow existing test patterns from `test_validate_execution_start.py`
- Use `unittest.TestCase` (project uses unittest, not pytest)
- Create temporary files using `tempfile` module
- Clean up temporary files after tests
- Mock file system operations if needed
- Test archive location checking (root and archive)
- Test statistics extraction from various formats

---

**Status**: Ready to Execute  
**Next**: Create EXECUTION_TASK and begin implementation

