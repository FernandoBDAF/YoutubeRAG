# SUBPLAN: Test Infrastructure Setup

**Mother Plan**: PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md  
**Achievement Addressed**: Achievement 1.1 (Test Infrastructure Setup)  
**Status**: In Progress  
**Created**: 2025-01-27 14:00 UTC  
**Estimated Effort**: 1 hour

---

## 🎯 Objective

Create comprehensive test infrastructure for all LLM methodology scripts by establishing test directory structure, creating reusable test fixtures (sample PLAN files, mock archives), and developing test utilities (helper functions for script testing). This provides the foundation for test coverage across all 13 scripts (generation, validation, archiving) and enables efficient test development in subsequent achievements.

**Contribution to PLAN**: This is the foundation achievement for Priority 1 (Test Coverage). Without proper test infrastructure, writing tests for individual scripts will be inefficient and inconsistent. This achievement enables all subsequent test coverage work.

---

## 📋 What Needs to Be Created

### Files to Create

1. **Test Directory Structure**:
   - `tests/LLM/scripts/__init__.py` - Package initialization (may already exist)
   - `tests/LLM/scripts/validation/__init__.py` - Validation scripts test package
   - `tests/LLM/scripts/archiving/__init__.py` - Archiving scripts test package
   - `tests/LLM/scripts/generation/__init__.py` - Generation scripts test package (may already exist)

2. **Test Configuration**:
   - `tests/LLM/scripts/conftest.py` - Pytest configuration and shared fixtures

3. **Test Fixtures**:
   - `tests/LLM/scripts/fixtures/__init__.py` - Fixtures package
   - `tests/LLM/scripts/fixtures/sample_plans.py` - Sample PLAN file fixtures
   - `tests/LLM/scripts/fixtures/mock_archives.py` - Mock archive structure fixtures

4. **Test Utilities**:
   - `tests/LLM/scripts/utils/__init__.py` - Utilities package
   - `tests/LLM/scripts/utils/script_test_helpers.py` - Helper functions for script testing

### Files to Modify

- None (infrastructure only)

### Functions/Classes to Add

**In `conftest.py`**:
- `sample_plan_file()` - Fixture providing sample PLAN content
- `sample_plan_path()` - Fixture providing temporary PLAN file path
- `mock_archive_structure()` - Fixture providing mock archive directory structure
- `temp_archive_dir()` - Fixture providing temporary archive directory

**In `fixtures/sample_plans.py`**:
- `get_sample_plan_content()` - Function returning sample PLAN content
- `get_minimal_plan_content()` - Function returning minimal valid PLAN
- `get_plan_with_achievements()` - Function returning PLAN with multiple achievements
- `get_plan_with_handoff()` - Function returning PLAN with handoff section

**In `fixtures/mock_archives.py`**:
- `create_mock_archive()` - Function creating mock archive structure
- `get_archive_structure()` - Function returning archive directory structure

**In `utils/script_test_helpers.py`**:
- `run_script()` - Helper to run scripts and capture output
- `assert_script_success()` - Helper to assert script execution success
- `assert_script_failure()` - Helper to assert script execution failure
- `get_script_output()` - Helper to capture script stdout/stderr
- `create_temp_plan_file()` - Helper to create temporary PLAN file
- `create_temp_archive()` - Helper to create temporary archive structure

---

## 📝 Approach

**Strategy**: Create reusable, well-organized test infrastructure that follows pytest best practices and enables efficient test development for all script types.

**Method**:

1. **Create Directory Structure**:
   - Create test package directories (validation, archiving, generation)
   - Add `__init__.py` files for proper Python package structure
   - Ensure structure matches script organization

2. **Create Pytest Configuration**:
   - Set up `conftest.py` with shared fixtures
   - Configure fixtures for common test scenarios (PLAN files, archives)
   - Use pytest fixtures for dependency injection

3. **Create Test Fixtures**:
   - Sample PLAN files with various configurations (minimal, with achievements, with handoff)
   - Mock archive structures (subplans, execution directories)
   - Temporary file/directory fixtures for isolation

4. **Create Test Utilities**:
   - Helper functions for common test operations (running scripts, assertions)
   - Utilities for creating temporary test files
   - Utilities for validating script output

**Key Considerations**:

- **Reusability**: Fixtures and utilities must be reusable across all script tests
- **Isolation**: Each test should be independent (use temporary files/directories)
- **Realism**: Sample PLAN files should reflect real PLAN structure
- **Completeness**: Cover common scenarios (valid files, invalid files, missing files)
- **Pytest Best Practices**: Use fixtures, parametrization, and proper assertions

**Risks to Watch For**:

- Over-engineering fixtures (keep them simple and focused)
- Not covering edge cases in fixtures (missing files, invalid formats)
- Creating fixtures that are too specific (should be general-purpose)

---

## 🧪 Tests Required

### Validation Approach (Infrastructure Work)

**Completeness Check**:
- [ ] All directory structure created
- [ ] All `__init__.py` files present
- [ ] `conftest.py` has required fixtures
- [ ] Fixture files have required functions
- [ ] Utility file has required helpers

**Structure Validation**:
- [ ] Directory structure matches script organization
- [ ] Fixtures follow pytest conventions
- [ ] Utilities follow Python best practices

**Functionality Validation**:
- [ ] Fixtures can be imported and used
- [ ] Utilities can be imported and used
- [ ] Sample PLAN files are valid
- [ ] Mock archives have correct structure

**Verification Commands**:
```bash
# Check directory structure
find tests/LLM/scripts -type d

# Check __init__.py files
find tests/LLM/scripts -name "__init__.py"

# Verify imports work
python -c "from tests.LLM.scripts.conftest import *"
python -c "from tests.LLM.scripts.fixtures.sample_plans import *"
python -c "from tests.LLM.scripts.utils.script_test_helpers import *"
```

---

## ✅ Expected Results

### Functional Changes

- **Test Infrastructure**: Complete test directory structure for all script types
- **Reusable Fixtures**: Sample PLAN files and mock archives available for all tests
- **Test Utilities**: Helper functions for common test operations
- **Pytest Configuration**: Shared fixtures configured in `conftest.py`

### Observable Outcomes

- **Directory Structure**: `tests/LLM/scripts/{validation,archiving,generation}/` exist
- **Fixtures Available**: Can import and use fixtures in test files
- **Utilities Available**: Can import and use helper functions in test files
- **Ready for Tests**: Infrastructure supports writing tests for all 13 scripts

### Success Indicators

- ✅ All test directories created
- ✅ `conftest.py` with shared fixtures
- ✅ Sample PLAN fixtures available
- ✅ Mock archive fixtures available
- ✅ Test utilities available
- ✅ All imports work correctly
- ✅ Infrastructure ready for test development

---

## 🔍 Conflict Analysis with Other Subplans

**Review Existing Subplans**:
- SUBPLAN_01: Achievement 0.1 (Extract Handoff Section Function) - ✅ Complete
- SUBPLAN_02: Achievement 0.2 (Update Achievement Detection Logic) - ✅ Complete
- SUBPLAN_03: Achievement 0.3 (Test Bug Fix) - ✅ Complete

**Check for**:
- **Overlap**: No overlap - this is infrastructure, others are implementation
- **Conflicts**: No conflicts - infrastructure supports all script testing
- **Dependencies**: No dependencies - this is foundation work
- **Integration**: This enables all subsequent test achievements

**Analysis**:
- No conflicts detected
- This is foundation work for Priority 1 achievements
- Safe to proceed

**Result**: Safe to proceed

---

## 🔗 Dependencies

### Other Subplans
- None (this is foundation work)

### External Dependencies
- pytest (for test framework)
- Python pathlib (for file operations)
- tempfile (for temporary files)

### Prerequisite Knowledge
- Understanding of pytest fixtures
- Understanding of LLM script structure
- Understanding of PLAN file format
- Understanding of archive structure

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

_None yet - will be created when execution starts_

**First Execution**: `EXECUTION_TASK_PROMPT-GENERATOR-FIX-AND-TESTING_11_01.md`

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] Test directory structure created (validation, archiving, generation)
- [ ] `conftest.py` with shared fixtures
- [ ] Sample PLAN fixtures created
- [ ] Mock archive fixtures created
- [ ] Test utilities created
- [ ] All imports work correctly
- [ ] Infrastructure ready for test development
- [ ] EXECUTION_TASK complete
- [ ] Ready for archive

---

## 📝 Notes

**Common Pitfalls**:
- Creating fixtures that are too specific (should be general-purpose)
- Not handling temporary file cleanup (use pytest fixtures for cleanup)
- Missing edge cases in fixtures (invalid files, missing files)

**Resources**:
- PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md (Achievement 1.1 section)
- Existing test structure: `tests/LLM/scripts/generation/test_generate_prompt.py`
- Pytest documentation: https://docs.pytest.org/
- LLM script structure: `LLM/scripts/`

---

## 📖 What to Read (Focus Rules)

**When working on this SUBPLAN**, follow these focus rules to minimize context:

**✅ READ ONLY**:
- This SUBPLAN file (complete file)
- Parent PLAN Achievement 1.1 section (9 lines)
- Active EXECUTION_TASKs (if any exist)
- Parent PLAN "Current Status & Handoff" section (27 lines)

**❌ DO NOT READ**:
- Parent PLAN full content
- Other achievements in PLAN
- Other SUBPLANs
- Completed EXECUTION_TASKs (unless needed for context)
- Completed work

**Context Budget**: ~400 lines

**Why**: SUBPLAN defines HOW to achieve one achievement. Reading other achievements or full PLAN adds scope and confusion.

**📖 See**: `LLM/guides/FOCUS-RULES.md` for complete focus rules and examples.

---

## 🔄 Active EXECUTION_TASKs (Updated When Created)

**Current Active Work** (register EXECUTION_TASKs immediately when created):

- [ ] **EXECUTION_TASK_PROMPT-GENERATOR-FIX-AND-TESTING_11_01**: Status: In Progress

**Registration Workflow**:

1. When creating EXECUTION_TASK: Add to this list immediately
2. When archiving: Remove from this list

**Why**: Immediate parent awareness ensures SUBPLAN knows about its active EXECUTION_TASKs.

---

**Ready to Execute**: Create EXECUTION_TASK and begin work  
**Reference**: IMPLEMENTATION_START_POINT.md for workflows


