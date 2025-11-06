# SUBPLAN: Basic Test Runner

**Mother Plan**: PLAN_TEST-RUNNER-INFRASTRUCTURE.md  
**Achievement Addressed**: Achievement 1.1 (All Tests Can Be Run with Single Command)  
**Status**: Not Started  
**Created**: 2025-11-06 01:25 UTC  
**Estimated Effort**: 1-2 hours

---

## 🎯 Objective

Create a simple Python script (`scripts/run_tests.py`) that discovers all tests in the `tests/` directory and runs them with a single command. The script should provide clear output showing pass/fail status and exit with appropriate exit codes.

---

## 📋 What Needs to Be Created

### Files to Create

1. **`scripts/run_tests.py`**
   - Main test runner script
   - Discovers all test files in `tests/` directory
   - Runs tests using Python's unittest or pytest (whichever is available)
   - Provides clear pass/fail summary
   - Exit code: 0 if all pass, non-zero if any fail

### Functions/Classes to Add

**In `scripts/run_tests.py`**:
- `discover_test_files()` - Find all test files in tests/ directory
- `run_tests()` - Execute tests and collect results
- `format_output()` - Format test results for display
- `main()` - CLI entry point with argparse

---

## 📝 Approach

**Strategy**: Create a simple, robust test runner that works with Python's standard unittest framework (which is available in all Python installations). Use unittest's discovery mechanism to find and run all tests.

**Method**:
1. **Exploration**: Check existing test structure and framework
2. **Implementation**: Create `scripts/run_tests.py` using unittest discovery
3. **Testing**: Test the script with actual test files
4. **Validation**: Ensure it runs all 47+ test files correctly

**Key Considerations**:
- **Test Discovery**: Use `unittest.discover()` to find all tests
- **Output Format**: Clear summary with pass/fail counts
- **Exit Codes**: 0 for success, 1 for failures (standard Unix convention)
- **Error Handling**: Graceful handling of import errors, missing tests
- **Compatibility**: Works with Python 3.x standard library (no external dependencies)

---

## 🧪 Tests Required (if applicable)

### Test File
- `tests/scripts/test_run_tests.py` (optional - can test script itself)

### Test Cases to Cover (if testing the script)
- Test discovery finds all test files
- Test execution runs discovered tests
- Exit code is correct (0 for pass, non-zero for fail)
- Output format is correct

### Test-First Requirement
- [x] Tests written before implementation (optional for this script - it's a utility)
- [ ] Initial test run shows all failing
- [x] Tests define success criteria

**Note**: This is a utility script, so testing it is optional. The script itself is the test of the test infrastructure.

---

## ✅ Expected Results

### Functional Changes
- New Python script (`scripts/run_tests.py`) will be available
- Can run `python scripts/run_tests.py` to execute all tests
- Script discovers and runs all 47+ test files

### Observable Outcomes
- Running `python scripts/run_tests.py` will:
  - Discover all test files in `tests/` directory
  - Execute all tests
  - Display pass/fail summary
  - Show test count (passed/failed)
  - Exit with code 0 if all pass, non-zero if any fail
- Output will show:
  - Test discovery progress (optional)
  - Test execution progress
  - Summary: "X tests passed, Y tests failed"
  - List of failures (if any)

---

## 🔍 Conflict Analysis with Other Subplans

**Review Existing Subplans**:
- None yet (this is the first subplan)

**Analysis**:
- No conflicts - this is foundational work
- Other subplans (1.2, 1.3) will build on this

**Result**: Safe to proceed

---

## 🔗 Dependencies

### Other Subplans
- None (this is the first subplan)

### External Dependencies
- Python standard library only (unittest module)
- No external packages required

### Prerequisite Knowledge
- Understanding of Python unittest discovery
- Knowledge of test file naming conventions (test_*.py)

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

- `EXECUTION_TASK_TEST-RUNNER-INFRASTRUCTURE_01_01.md`: Initial implementation

**First Execution**: `EXECUTION_TASK_TEST-RUNNER-INFRASTRUCTURE_01_01.md`

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] `scripts/run_tests.py` created and executable
- [ ] Script discovers all test files in `tests/` directory
- [ ] Script runs all tests successfully
- [ ] Clear output with pass/fail summary
- [ ] Exit codes work correctly (0 for pass, non-zero for fail)
- [ ] Tested with actual test files
- [ ] Ready for archive

---

## 📝 Notes

**Common Pitfalls**:
- Ensuring test discovery works with nested directory structure
- Handling import errors gracefully (some tests may fail due to missing dependencies)
- Making script executable and finding correct Python interpreter
- Handling edge cases (no tests found, all tests fail)

**Resources**:
- Python unittest documentation
- Existing test files in `tests/` directory for reference
- `IMPLEMENTATION_START_POINT.md` for methodology

---

**Ready to Execute**: Create EXECUTION_TASK and begin work  
**Reference**: IMPLEMENTATION_START_POINT.md for workflows

