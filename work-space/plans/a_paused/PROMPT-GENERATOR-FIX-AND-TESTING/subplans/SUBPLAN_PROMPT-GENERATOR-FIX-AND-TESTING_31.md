# SUBPLAN: Achievement 3.1 - Test Coverage for archive_completed.py

**Mother Plan**: PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md  
**Achievement Addressed**: Achievement 3.1 (Test Coverage for archive_completed.py)  
**Status**: In Progress  
**Created**: 2025-01-28 01:30 UTC  
**Estimated Effort**: 2 hours

---

## 🎯 Objective

Create comprehensive test coverage for `LLM/scripts/archiving/archive_completed.py` to ensure the script correctly archives completed SUBPLANs and EXECUTION_TASKs, handles archive location detection, and supports batch operations.

---

## 📋 What Needs to Be Created

### Files to Create

1. **Test File**: `tests/LLM/scripts/archiving/test_archive_completed.py`
   - Unit tests for `find_plan_file()` function
   - Unit tests for `get_archive_location()` function
   - Unit tests for `determine_archive_type()` function
   - Unit tests for `archive_file()` function
   - Integration tests with various file types (SUBPLAN, EXECUTION_TASK)
   - Edge case tests (missing PLAN, invalid paths, archive creation, duplicate files)

---

## 🎯 Approach

### Step 1: Analyze Script Functions

Review `archive_completed.py` to understand:
- `find_plan_file()`: Finds parent PLAN file for SUBPLAN or EXECUTION_TASK
- `get_archive_location()`: Extracts archive location from PLAN file
- `determine_archive_type()`: Determines if file is SUBPLAN or EXECUTION_TASK
- `archive_file()`: Moves file to archive location
- `main()`: CLI entry point with argument parsing

### Step 2: Create Test Fixtures

Create temporary files for testing:
- Sample PLAN files with various archive location formats
- Sample SUBPLAN files
- Sample EXECUTION_TASK files
- Sample archive directories
- Sample files with missing PLAN files

### Step 3: Write Unit Tests

**For `find_plan_file()`**:
- Test finding PLAN for SUBPLAN
- Test finding PLAN for EXECUTION_TASK
- Test with missing PLAN file
- Test with invalid file type
- Test with different feature name formats

**For `get_archive_location()`**:
- Test extracting archive location from PLAN
- Test fallback to inferred location
- Test various archive location formats
- Test with missing archive location section

**For `determine_archive_type()`**:
- Test determining SUBPLAN type
- Test determining EXECUTION_TASK type
- Test with invalid file type

**For `archive_file()`**:
- Test archiving SUBPLAN file
- Test archiving EXECUTION_TASK file
- Test creating archive structure
- Test handling duplicate files
- Test with missing source file

### Step 4: Write Integration Tests

- Test archiving single SUBPLAN
- Test archiving single EXECUTION_TASK
- Test batch archiving (multiple files)
- Test batch mode flag
- Test CLI argument parsing (@ prefix handling)
- Test exit codes (0 for success, 1 for error)

### Step 5: Write Edge Case Tests

- Test missing PLAN file
- Test invalid file paths
- Test archive creation
- Test duplicate files (already exists in archive)
- Test missing source files
- Test invalid file types

### Step 6: Verify Coverage

- Run tests: `python -m unittest tests.LLM.scripts.archiving.test_archive_completed -v`
- Check coverage: Target >90% coverage
- All tests should pass

---

## ✅ Expected Results

### Deliverables

1. ✅ Test file created: `tests/LLM/scripts/archiving/test_archive_completed.py`
2. ✅ Unit tests for all functions
3. ✅ Integration tests with various file types
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
ls -1 tests/LLM/scripts/archiving/test_archive_completed.py
```

### Test 2: Tests Run

```bash
# Run tests
python -m unittest tests.LLM.scripts.archiving.test_archive_completed -v
```

### Test 3: Coverage Check

```bash
# Verify all tests pass
python -m unittest tests.LLM.scripts.archiving.test_archive_completed -v | grep -E "(OK|FAILED)"
```

---

## 📝 Notes

- Follow existing test patterns from `test_validate_references.py`
- Use `unittest.TestCase` (project uses unittest, not pytest)
- Create temporary files using `tempfile` module
- Clean up temporary files after tests
- Mock file system operations if needed
- Test both single file and batch mode
- Test exit codes for CLI
- Test archive structure creation
- Test duplicate file handling

---

**Status**: Ready to Execute  
**Next**: Create EXECUTION_TASK and begin implementation

