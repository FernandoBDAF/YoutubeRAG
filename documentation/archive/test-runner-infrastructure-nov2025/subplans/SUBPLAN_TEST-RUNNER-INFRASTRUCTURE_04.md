# SUBPLAN: Categorized Test Running

**Related PLAN**: PLAN_TEST-RUNNER-INFRASTRUCTURE.md  
**Achievement**: 2.1 (Categorized Test Running)  
**Status**: ✅ COMPLETE  
**Created**: 2025-11-06 18:45 UTC  
**Completed**: 2025-11-06 18:50 UTC

---

## 🎯 Objective

Add support for running tests by category/type (e.g., unit tests, integration tests, fast tests) to the test runner, allowing developers to run specific test categories for faster feedback or targeted validation.

---

## 📋 Context

**Current State**:

- Test runner supports running all tests or specific modules
- No way to run tests by category (unit vs integration)
- No way to run only fast tests for quick feedback

**What We Need**:

- Ability to categorize tests (unit, integration, etc.)
- Support for running tests by category
- Fast test subset for quick feedback

**Constraints**:

- Project uses unittest (not pytest), so no pytest markers
- Need to use directory structure or naming conventions
- Should work with existing test organization

---

## 🎯 Success Criteria

**This Subplan is Complete When**:

- [x] Test runner supports `--category` argument
- [x] Can run unit tests separately from integration tests
- [x] Can run fast tests subset
- [x] Categories are clearly defined and documented
- [x] Works with existing test structure
- [x] All tests passing (category filtering works correctly)
- [x] Code commented with learnings
- [x] `EXECUTION_TASK_TEST-RUNNER-INFRASTRUCTURE_04_01.md` complete
- [x] Ready for archive

---

## 📋 Approach

### Strategy

1. **Analyze Test Structure**:

   - Examine existing test organization
   - Identify natural categories (unit vs integration)
   - Determine if naming conventions exist

2. **Define Categories**:

   - Unit tests (fast, isolated)
   - Integration tests (slower, require setup)
   - Fast tests (subset for quick feedback)

3. **Implementation Options**:

   - **Option A**: Use directory structure (e.g., `tests/unit/`, `tests/integration/`)
   - **Option B**: Use naming conventions (e.g., `test_unit_*.py`, `test_integration_*.py`)
   - **Option C**: Use both - directory structure preferred, naming as fallback

4. **Enhance Test Runner**:
   - Add `--category` argument to `run_tests.py`
   - Filter tests based on category
   - Support categories: `unit`, `integration`, `fast`, `all`

### Deliverables

1. Enhanced `scripts/run_tests.py` with category support
2. Updated documentation explaining categories
3. Category definitions and conventions

---

## 🔄 Implementation Steps

### Step 1: Analyze Test Organization

- [ ] Explore test directory structure
- [ ] Identify test patterns and conventions
- [ ] Determine categorization strategy

### Step 2: Define Categories

- [ ] Define unit test criteria
- [ ] Define integration test criteria
- [ ] Define fast test subset
- [ ] Document category definitions

### Step 3: Implement Category Support

- [ ] Add category detection logic
- [ ] Add `--category` argument to CLI
- [ ] Filter tests based on category
- [ ] Test with various categories

### Step 4: Documentation

- [ ] Update test running documentation
- [ ] Document category definitions
- [ ] Provide usage examples

---

## 📚 References

- `PLAN_TEST-RUNNER-INFRASTRUCTURE.md` - Parent plan
- `scripts/run_tests.py` - Current test runner
- `documentation/guides/RUNNING-TESTS.md` - Test running guide
- `IMPLEMENTATION_START_POINT.md` - Methodology reference

---

**Status**: Ready for Execution  
**Next**: Create EXECUTION_TASK and begin implementation
