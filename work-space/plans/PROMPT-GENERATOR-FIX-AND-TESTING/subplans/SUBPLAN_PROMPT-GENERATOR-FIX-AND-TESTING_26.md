# SUBPLAN: Achievement 2.6 - Test Coverage for validate_registration.py

**Mother Plan**: PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md  
**Achievement Addressed**: Achievement 2.6 (Test Coverage for validate_registration.py)  
**Status**: In Progress  
**Created**: 2025-01-28 00:20 UTC  
**Estimated Effort**: 1.5 hours

---

## 🎯 Objective

Create comprehensive test coverage for `LLM/scripts/validation/validate_registration.py` to ensure the script correctly validates component registration (SUBPLANs and EXECUTION_TASKs) in PLANs and SUBPLANs, and detects orphaned files.

---

## 📋 What Needs to Be Created

### Files to Create

1. **Test File**: `tests/LLM/scripts/validation/test_validate_registration.py`
   - Unit tests for `find_subplans_for_plan()` function
   - Unit tests for `find_execution_tasks_for_plan()` function
   - Unit tests for `find_execution_tasks_for_subplan()` function
   - Unit tests for `get_archive_location()` function
   - Unit tests for `extract_registered_subplans()` function
   - Unit tests for `extract_registered_execution_tasks_plan()` function
   - Unit tests for `extract_registered_execution_tasks_subplan()` function
   - Unit tests for `validate_plan_registration()` function
   - Unit tests for `validate_subplan_registration()` function
   - Integration tests with various PLAN/SUBPLAN states
   - Edge case tests (missing files, orphaned files, unregistered files)

---

## 🎯 Approach

### Step 1: Analyze Script Functions

Review `validate_registration.py` to understand:
- `find_subplans_for_plan()`: Finds all SUBPLAN files for a PLAN (root + archive)
- `find_execution_tasks_for_plan()`: Finds all EXECUTION_TASK files for a PLAN (root + archive)
- `find_execution_tasks_for_subplan()`: Finds all EXECUTION_TASK files for a SUBPLAN (root + archive)
- `get_archive_location()`: Extracts archive location from PLAN file
- `extract_registered_subplans()`: Extracts registered SUBPLANs from PLAN file
- `extract_registered_execution_tasks_plan()`: Extracts registered EXECUTION_TASKs from PLAN file
- `extract_registered_execution_tasks_subplan()`: Extracts registered EXECUTION_TASKs from SUBPLAN file
- `validate_plan_registration()`: Main validation function for PLANs
- `validate_subplan_registration()`: Main validation function for SUBPLANs
- `main()`: CLI entry point with argument parsing

### Step 2: Create Test Fixtures

Create temporary files for testing:
- Sample PLAN files with various registration states
- Sample SUBPLAN files (root and archived)
- Sample EXECUTION_TASK files (root and archived)
- Sample archive directories

### Step 3: Write Unit Tests

**For `find_subplans_for_plan()`**:
- Test finding SUBPLANs in root
- Test finding SUBPLANs in archive
- Test finding SUBPLANs in both locations
- Test with no SUBPLANs
- Test with different feature names

**For `find_execution_tasks_for_plan()`**:
- Test finding EXECUTION_TASKs in root
- Test finding EXECUTION_TASKs in archive
- Test finding EXECUTION_TASKs in both locations
- Test with no EXECUTION_TASKs
- Test with multiple attempts

**For `find_execution_tasks_for_subplan()`**:
- Test finding EXECUTION_TASKs in root
- Test finding EXECUTION_TASKs in archive
- Test finding EXECUTION_TASKs in both locations
- Test with no EXECUTION_TASKs
- Test with invalid SUBPLAN filename

**For `get_archive_location()`**:
- Test extracting archive location from PLAN
- Test fallback to inferred location
- Test various archive location formats

**For `extract_registered_subplans()`**:
- Test extracting from "Active Components" section
- Test extracting from "Subplan Tracking" section
- Test extracting from both sections (duplicates removed)
- Test with no registered SUBPLANs
- Test with various formats

**For `extract_registered_execution_tasks_plan()`**:
- Test extracting from "Active Components" section
- Test extracting from "Subplan Tracking" section
- Test extracting from both sections (duplicates removed)
- Test with no registered EXECUTION_TASKs

**For `extract_registered_execution_tasks_subplan()`**:
- Test extracting from "Active EXECUTION_TASKs" section
- Test with no registered EXECUTION_TASKs

**For `validate_plan_registration()`**:
- Test all components registered
- Test unregistered SUBPLANs
- Test unregistered EXECUTION_TASKs
- Test orphaned SUBPLAN registrations (warning)
- Test orphaned EXECUTION_TASK registrations (warning)
- Test multiple issues
- Test missing PLAN file

**For `validate_subplan_registration()`**:
- Test all EXECUTION_TASKs registered
- Test unregistered EXECUTION_TASKs
- Test missing SUBPLAN file

### Step 4: Write Integration Tests

- Test with complete valid PLAN (all components registered)
- Test with invalid PLAN (unregistered components)
- Test with complete valid SUBPLAN (all EXECUTION_TASKs registered)
- Test CLI argument parsing (@ prefix handling, PLAN vs SUBPLAN)
- Test exit codes (0 for pass, 1 for fail)
- Test error handling (exceptions, invalid file types)

### Step 5: Write Edge Case Tests

- Test missing PLAN/SUBPLAN file
- Test files in archive vs root
- Test orphaned registrations (registered but file doesn't exist)
- Test unregistered files (file exists but not registered)
- Test invalid file types

### Step 6: Verify Coverage

- Run tests: `python -m unittest tests.LLM.scripts.validation.test_validate_registration -v`
- Check coverage: Target >90% coverage
- All tests should pass

---

## ✅ Expected Results

### Deliverables

1. ✅ Test file created: `tests/LLM/scripts/validation/test_validate_registration.py`
2. ✅ Unit tests for all functions
3. ✅ Integration tests with various PLAN/SUBPLAN states
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
ls -1 tests/LLM/scripts/validation/test_validate_registration.py
```

### Test 2: Tests Run

```bash
# Run tests
python -m unittest tests.LLM.scripts.validation.test_validate_registration -v
```

### Test 3: Coverage Check

```bash
# Verify all tests pass
python -m unittest tests.LLM.scripts.validation.test_validate_registration -v | grep -E "(OK|FAILED)"
```

---

## 📝 Notes

- Follow existing test patterns from `test_validate_mid_plan.py`
- Use `unittest.TestCase` (project uses unittest, not pytest)
- Create temporary files using `tempfile` module
- Clean up temporary files after tests
- Mock file system operations if needed
- Test archive location checking (root and archive)
- Test registration extraction from various section formats

---

**Status**: Ready to Execute  
**Next**: Create EXECUTION_TASK and begin implementation

