# SUBPLAN: Achievement 2.7 - Test Coverage for validate_plan_compliance.py

**Mother Plan**: PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md  
**Achievement Addressed**: Achievement 2.7 (Test Coverage for validate_plan_compliance.py)  
**Status**: In Progress  
**Created**: 2025-01-28 00:45 UTC  
**Estimated Effort**: 1.5 hours

---

## 🎯 Objective

Create comprehensive test coverage for `LLM/scripts/validation/validate_plan_compliance.py` to ensure the script correctly validates PLAN document compliance with structured LLM development methodology.

---

## 📋 What Needs to Be Created

### Files to Create

1. **Test File**: `tests/LLM/scripts/validation/test_validate_plan_compliance.py`
   - Unit tests for `find_plan_files()` function
   - Unit tests for `extract_sections()` function
   - Unit tests for `check_naming_compliance()` function
   - Unit tests for `calculate_compliance_score()` function
   - Unit tests for `generate_report()` function
   - Integration tests with compliant/non-compliant PLANs
   - Edge case tests
   - CLI argument parsing tests

---

## 🎯 Approach

### Step 1: Analyze Script Functions

Review `validate_plan_compliance.py` to understand:
- `find_plan_files()`: Finds all PLAN and GRAMMAPLAN files in project
- `extract_sections()`: Extracts markdown ## sections from file
- `check_naming_compliance()`: Checks if file follows naming convention
- `calculate_compliance_score()`: Calculates compliance score based on various criteria
- `generate_report()`: Generates compliance report (human-readable or JSON)
- `main()`: CLI entry point with argument parsing

### Step 2: Create Test Fixtures

Create temporary files for testing:
- Sample PLAN files with various compliance states
- Sample GRAMMAPLAN files
- Sample non-compliant PLAN files
- Sample files with missing sections
- Sample files with all required sections

### Step 3: Write Unit Tests

**For `find_plan_files()`**:
- Test finding PLAN files in root
- Test finding GRAMMAPLAN files
- Test finding both types
- Test with no files
- Test with subdirectories (should not find)

**For `extract_sections()`**:
- Test extracting sections from file
- Test with emojis in section names
- Test with missing file
- Test with empty file
- Test with no sections

**For `check_naming_compliance()`**:
- Test valid PLAN name
- Test valid GRAMMAPLAN name
- Test invalid name format
- Test edge cases (special characters, wrong extension)

**For `calculate_compliance_score()`**:
- Test with all required sections (100 points)
- Test with missing required sections
- Test with v1.4 features (bonus points)
- Test with missing naming compliance
- Test with missing Related Plans section
- Test with missing Subplan Tracking section
- Test various combinations

**For `generate_report()`**:
- Test human-readable report generation
- Test JSON report generation
- Test with multiple PLANs
- Test with empty results
- Test color coding (green/yellow/red)

### Step 4: Write Integration Tests

- Test with complete compliant PLAN
- Test with non-compliant PLAN
- Test with GRAMMAPLAN
- Test CLI with single file
- Test CLI with --all flag
- Test CLI with --json flag
- Test exit codes (0 for compliant, 1 for non-compliant, 2 for errors)

### Step 5: Write Edge Case Tests

- Test missing file
- Test invalid file format
- Test file with no sections
- Test file with only optional sections
- Test file with duplicate sections
- Test very large file

### Step 6: Verify Coverage

- Run tests: `python -m unittest tests.LLM.scripts.validation.test_validate_plan_compliance -v`
- Check coverage: Target >90% coverage
- All tests should pass

---

## ✅ Expected Results

### Deliverables

1. ✅ Test file created: `tests/LLM/scripts/validation/test_validate_plan_compliance.py`
2. ✅ Unit tests for all functions
3. ✅ Integration tests with compliant/non-compliant PLANs
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
ls -1 tests/LLM/scripts/validation/test_validate_plan_compliance.py
```

### Test 2: Tests Run

```bash
# Run tests
python -m unittest tests.LLM.scripts.validation.test_validate_plan_compliance -v
```

### Test 3: Coverage Check

```bash
# Verify all tests pass
python -m unittest tests.LLM.scripts.validation.test_validate_plan_compliance -v | grep -E "(OK|FAILED)"
```

---

## 📝 Notes

- Follow existing test patterns from `test_validate_registration.py`
- Use `unittest.TestCase` (project uses unittest, not pytest)
- Create temporary files using `tempfile` module
- Clean up temporary files after tests
- Mock file system operations if needed
- Test both human-readable and JSON report formats
- Test exit codes for CLI
- Test color coding in reports

---

**Status**: Ready to Execute  
**Next**: Create EXECUTION_TASK and begin implementation

