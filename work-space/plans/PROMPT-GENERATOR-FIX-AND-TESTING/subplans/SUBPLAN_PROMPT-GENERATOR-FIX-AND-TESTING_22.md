# SUBPLAN: Achievement 2.2 - Test Coverage for check_execution_task_size.py

**Mother Plan**: PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md  
**Achievement Addressed**: Achievement 2.2 (Test Coverage for check_execution_task_size.py)  
**Status**: In Progress  
**Created**: 2025-01-27 23:30 UTC  
**Estimated Effort**: 1 hour

---

## 🎯 Objective

Create comprehensive test coverage for `LLM/scripts/validation/check_execution_task_size.py` to ensure the script correctly validates EXECUTION_TASK size limits (200 lines maximum, warning at 150 lines).

---

## 📋 What Needs to Be Created

### Files to Create

1. **Test File**: `tests/LLM/scripts/validation/test_check_execution_task_size.py`
   - Unit tests for `count_lines()` function
   - Unit tests for `check_limit()` function
   - Integration tests with various EXECUTION_TASK sizes
   - Edge case tests (empty files, very large files, missing files)
   - Test fixtures (sample EXECUTION_TASK files with different sizes)

---

## 🎯 Approach

### Step 1: Analyze Script Functions

Review `check_execution_task_size.py` to understand:
- `count_lines()`: Counts total lines in EXECUTION_TASK file
- `check_limit()`: Validates limits and returns warnings/errors
- `main()`: CLI entry point with argument parsing

### Step 2: Create Test Fixtures

Create temporary EXECUTION_TASK files for testing:
- Small EXECUTION_TASK (< 150 lines)
- Medium EXECUTION_TASK (150-200 lines)
- Large EXECUTION_TASK (> 200 lines)
- Empty EXECUTION_TASK file
- EXECUTION_TASK with various content structures

### Step 3: Write Unit Tests

**For `count_lines()`**:
- Test with normal file
- Test with empty file
- Test with single line
- Test with multi-line file
- Test with file containing empty lines

**For `check_limit()`**:
- Test within limits (< 150 lines)
- Test approaching limit (150-200 lines) - warning
- Test exceeding limit (> 200 lines) - error
- Test missing file
- Test empty file
- Test very large file (> 300 lines)
- Test boundary cases (149, 150, 151, 199, 200, 201 lines)

### Step 4: Write Integration Tests

- Test with real EXECUTION_TASK file structure
- Test CLI argument parsing (@ prefix handling)
- Test exit codes (0 for pass, 1 for fail)
- Test error handling (exceptions)

### Step 5: Verify Coverage

- Run tests: `python -m unittest tests.LLM.scripts.validation.test_check_execution_task_size -v`
- Check coverage: Target >90% coverage
- All tests should pass

---

## ✅ Expected Results

### Deliverables

1. ✅ Test file created: `tests/LLM/scripts/validation/test_check_execution_task_size.py`
2. ✅ Unit tests for all functions (count_lines, check_limit)
3. ✅ Integration tests with various EXECUTION_TASK sizes
4. ✅ Edge case tests (empty files, very large files, missing files)
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
ls -1 tests/LLM/scripts/validation/test_check_execution_task_size.py
```

### Test 2: Tests Run

```bash
# Run tests
python -m unittest tests.LLM.scripts.validation.test_check_execution_task_size -v
```

### Test 3: Coverage Check

```bash
# Verify all tests pass
python -m unittest tests.LLM.scripts.validation.test_check_execution_task_size -v | grep -E "(OK|FAILED)"
```

---

## 📝 Notes

- Follow existing test patterns from `test_check_plan_size.py`
- Use `unittest.TestCase` (project uses unittest, not pytest)
- Create temporary files using `tempfile` module
- Clean up temporary files after tests
- Test boundary cases carefully (149, 150, 151, 199, 200, 201 lines)

---

**Status**: Ready to Execute  
**Next**: Create EXECUTION_TASK and begin implementation

