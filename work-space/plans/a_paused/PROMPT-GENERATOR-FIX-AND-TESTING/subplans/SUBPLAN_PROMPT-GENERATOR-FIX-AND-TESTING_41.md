# SUBPLAN: Achievement 4.1 - Integration Test Suite

**Mother Plan**: PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md  
**Achievement Addressed**: Achievement 4.1 (Integration Test Suite)  
**Status**: In Progress  
**Created**: 2025-01-28 01:50 UTC  
**Estimated Effort**: 2 hours

---

## 🎯 Objective

Create comprehensive integration test suite for LLM scripts to test end-to-end workflows, script interactions (generation → validation → archiving), and integration with real PLAN files from the project.

---

## 📋 What Needs to Be Created

### Files to Create

1. **Test File**: `tests/LLM/scripts/integration/test_workflows.py`
   - End-to-end tests for common workflows
   - Test script interactions (generation → validation → archiving)
   - Test with real PLAN files from project
   - Test complete methodology workflows

---

## 🎯 Approach

### Step 1: Identify Common Workflows

Review existing scripts to identify common workflows:
- **Workflow 1**: Generate prompt → Validate plan → Archive completed
- **Workflow 2**: Generate pause prompt → Validate execution start → Archive
- **Workflow 3**: Generate resume prompt → Validate mid-plan → Archive
- **Workflow 4**: Generate verify prompt → Validate plan completion → Archive
- **Workflow 5**: Full cycle: Generate → Validate → Archive → Generate next

### Step 2: Create Test Fixtures

Use existing test fixtures and create additional ones:
- Sample PLAN files (from fixtures or real project)
- Sample SUBPLAN files
- Sample EXECUTION_TASK files
- Mock archive directories

### Step 3: Write Integration Tests

**For Workflow 1 (Generate → Validate → Archive)**:
- Test generating prompt for next achievement
- Test validating plan compliance
- Test archiving completed files
- Test complete workflow end-to-end

**For Workflow 2 (Pause → Validate → Archive)**:
- Test generating pause prompt
- Test validating execution start
- Test archiving paused files

**For Workflow 3 (Resume → Validate → Archive)**:
- Test generating resume prompt
- Test validating mid-plan
- Test archiving resumed files

**For Workflow 4 (Verify → Validate → Archive)**:
- Test generating verify prompt
- Test validating plan completion
- Test archiving verified files

**For Workflow 5 (Full Cycle)**:
- Test complete methodology cycle
- Test multiple achievements in sequence
- Test archive structure creation
- Test validation at each step

### Step 4: Test with Real PLAN Files

- Test with actual PLAN files from project root
- Test with various PLAN states (in progress, complete, paused)
- Test with different archive locations
- Test with different feature names

### Step 5: Verify Coverage

- Run tests: `python -m unittest tests.LLM.scripts.integration.test_workflows -v`
- All integration tests should pass
- Tests should cover main workflows

---

## ✅ Expected Results

### Deliverables

1. ✅ Test file created: `tests/LLM/scripts/integration/test_workflows.py`
2. ✅ End-to-end tests for common workflows
3. ✅ Script interaction tests
4. ✅ Tests with real PLAN files
5. ✅ All integration tests pass

### Success Criteria

- [ ] All integration tests pass
- [ ] Tests cover main workflows
- [ ] Tests use real PLAN files where appropriate
- [ ] Tests follow existing test patterns in project

---

## 🧪 Tests

### Test 1: File Exists

```bash
# Verify test file exists
ls -1 tests/LLM/scripts/integration/test_workflows.py
```

### Test 2: Tests Run

```bash
# Run tests
python -m unittest tests.LLM.scripts.integration.test_workflows -v
```

### Test 3: Coverage Check

```bash
# Verify all tests pass
python -m unittest tests.LLM.scripts.integration.test_workflows -v | grep -E "(OK|FAILED)"
```

---

## 📝 Notes

- Follow existing test patterns from other test files
- Use `unittest.TestCase` (project uses unittest, not pytest)
- Create temporary files using `tempfile` module
- Clean up temporary files after tests
- Use existing fixtures from `tests/LLM/scripts/fixtures/`
- Test real PLAN files from project root where safe
- Test script interactions (output of one script as input to another)
- Test error handling in workflows
- Test archive structure creation

---

**Status**: Ready to Execute  
**Next**: Create EXECUTION_TASK and begin implementation
