# SUBPLAN: Achievement 2.1 - Test Coverage for check_plan_size.py

**Mother Plan**: PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md  
**Achievement Addressed**: Achievement 2.1 (Test Coverage for check_plan_size.py)  
**Status**: In Progress  
**Created**: 2025-01-27 23:00 UTC  
**Estimated Effort**: 1 hour

---

## 🎯 Objective

Create comprehensive test coverage for `LLM/scripts/validation/check_plan_size.py` to ensure the script correctly validates PLAN size limits (600 lines / 32 hours) and provides appropriate warnings and errors.

---

## 📋 What Needs to Be Created

### Files to Create

1. **Test File**: `tests/LLM/scripts/validation/test_check_plan_size.py`
   - Unit tests for `count_lines()` function
   - Unit tests for `extract_estimated_effort()` function
   - Unit tests for `check_limits()` function
   - Integration tests with various PLAN sizes
   - Edge case tests (empty files, very large files, missing files)
   - Test fixtures (sample PLAN files with different sizes and effort estimates)

---

## 🎯 Approach

### Step 1: Analyze Script Functions

Review `check_plan_size.py` to understand:
- `count_lines()`: Counts total lines in PLAN file
- `extract_estimated_effort()`: Extracts estimated effort from various patterns
- `check_limits()`: Validates limits and returns warnings/errors
- `main()`: CLI entry point with argument parsing

### Step 2: Create Test Fixtures

Create temporary PLAN files for testing:
- Small PLAN (< 400 lines, < 24 hours)
- Medium PLAN (400-600 lines, 24-32 hours)
- Large PLAN (> 600 lines, > 32 hours)
- PLAN with various effort estimate formats
- Empty PLAN file
- PLAN with no effort estimate

### Step 3: Write Unit Tests

**For `count_lines()`**:
- Test with normal file
- Test with empty file
- Test with single line
- Test with multi-line file

**For `extract_estimated_effort()`**:
- Test "Total Estimated Effort: X hours"
- Test "Estimated Effort: X-Y hours" (range)
- Test "Estimated: X hours"
- Test "Effort: X hours"
- Test multiple achievement efforts (sum)
- Test with no effort estimate (returns 0)
- Test case insensitivity

**For `check_limits()`**:
- Test within limits (no warnings/errors)
- Test line count warning (400-600 lines)
- Test line count error (> 600 lines)
- Test effort warning (24-32 hours)
- Test effort error (> 32 hours)
- Test both warnings
- Test both errors
- Test missing file
- Test empty file

### Step 4: Write Integration Tests

- Test with real PLAN file structure
- Test CLI argument parsing (@ prefix handling)
- Test exit codes (0 for pass, 1 for fail)
- Test error handling (exceptions)

### Step 5: Verify Coverage

- Run tests: `python -m pytest tests/LLM/scripts/validation/test_check_plan_size.py -v`
- Check coverage: `python -m pytest --cov=LLM/scripts/validation/check_plan_size --cov-report=term-missing`
- Target: >90% coverage

---

## ✅ Expected Results

### Deliverables

1. ✅ Test file created: `tests/LLM/scripts/validation/test_check_plan_size.py`
2. ✅ Unit tests for all functions (count_lines, extract_estimated_effort, check_limits)
3. ✅ Integration tests with various PLAN sizes
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
ls -1 tests/LLM/scripts/validation/test_check_plan_size.py
```

### Test 2: Tests Run

```bash
# Run tests
python -m pytest tests/LLM/scripts/validation/test_check_plan_size.py -v
```

### Test 3: Coverage Check

```bash
# Check coverage
python -m pytest --cov=LLM/scripts/validation/check_plan_size --cov-report=term-missing tests/LLM/scripts/validation/test_check_plan_size.py
```

---

## 📝 Notes

- Follow existing test patterns from `test_generate_prompt.py`
- Use `unittest.TestCase` or `pytest` (check project preference)
- Create temporary files using `tempfile` module
- Clean up temporary files after tests
- Mock file operations if needed for edge cases

---

**Status**: Ready to Execute  
**Next**: Create EXECUTION_TASK and begin implementation
