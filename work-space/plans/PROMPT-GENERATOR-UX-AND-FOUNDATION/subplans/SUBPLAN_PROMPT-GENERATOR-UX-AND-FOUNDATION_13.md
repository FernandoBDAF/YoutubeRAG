# SUBPLAN: Complete Test Coverage (90%)

**Type**: SUBPLAN  
**Mother Plan**: PLAN_PROMPT-GENERATOR-UX-AND-FOUNDATION.md  
**Plan**: PROMPT-GENERATOR-UX-AND-FOUNDATION  
**Achievement Addressed**: Achievement 1.3 (Complete Test Coverage - 90%)  
**Achievement**: 1.3  
**Status**: Design Complete, Ready for Execution  
**Created**: 2025-11-10 07:00 UTC  
**Estimated Effort**: 6-8 hours

**File Location**: `work-space/plans/PROMPT-GENERATOR-UX-AND-FOUNDATION/subplans/SUBPLAN_PROMPT-GENERATOR-UX-AND-FOUNDATION_13.md`

---

## 🎯 Objective

Achieve 90%+ test coverage for `generate_prompt.py` by testing all 20 untested functions, adding integration tests for complete workflows, and edge case tests for error scenarios. This enables safe refactoring for Priority 2 (filesystem state management and class-based architecture).

---

## 📋 Deliverables

### 1. Workflow State Tests (test_workflow_detection.py)

Test all 7 workflow states:

- no_subplan → create_subplan
- subplan_no_execution → create_execution
- active_execution → continue_execution
- create_next_execution → next execution in multi-execution
- subplan_all_executed → synthesize or complete
- subplan_complete → next achievement
- plan_complete → completion message

**Tests**: 10-12 tests

### 2. Achievement Finding Tests (test_achievement_finding.py)

Test achievement detection functions:

- find_next_achievement_hybrid()
- find_next_achievement_from_archive()
- find_next_achievement_from_root()
- is_achievement_complete()
- is_plan_complete()
- get_plan_status()

**Tests**: 12-15 tests

### 3. Conflict Detection Tests (test_conflict_detection.py)

Test conflict detection:

- detect_plan_filesystem_conflict()
- All 3 conflict types (outdated_complete, outdated_synthesis, premature_complete)
- Trust flags (--trust-plan, --trust-filesystem)

**Tests**: 8-10 tests

### 4. Integration Tests (test_integration_workflows.py)

Test complete workflows end-to-end:

- Create SUBPLAN workflow
- Create EXECUTION workflow
- Continue EXECUTION workflow
- Complete achievement workflow

**Tests**: 6-8 tests

### 5. Edge Case Tests (test_edge_cases.py)

Test error scenarios:

- Missing files
- Corrupted files
- Empty files
- Permission errors
- Invalid formats

**Tests**: 8-10 tests

### 6. Coverage Report

Generate coverage report showing >90% coverage:

```bash
pytest --cov=LLM/scripts/generation/generate_prompt --cov-report=term-missing
```

---

## 🎨 Approach

**Strategy**: Systematic testing of all untested functions, organized by functional area (workflow, achievement, conflict, integration, edge cases).

**Method**:

**Phase 1: Workflow State Tests** (2h)

- Create test_workflow_detection.py
- Test detect_workflow_state_filesystem() with all 7 states
- Test detect_workflow_state() wrapper
- Mock filesystem structure for each state

**Phase 2: Achievement Finding Tests** (2h)

- Create test_achievement_finding.py
- Test find_next_achievement_hybrid() with multiple scenarios
- Test helper functions (archive, root, complete checking)
- Use real PLAN fixtures

**Phase 3: Conflict Detection Tests** (1h)

- Create test_conflict_detection.py
- Test all 3 conflict types
- Test trust flags behavior
- Mock PLAN and filesystem states

**Phase 4: Integration Tests** (1.5h)

- Create test_integration_workflows.py
- Test complete workflows end-to-end
- Use temporary test PLANs
- Verify output correctness

**Phase 5: Edge Case Tests** (1h)

- Create test_edge_cases.py
- Test error scenarios
- Verify error messages
- Ensure graceful degradation

**Phase 6: Coverage Verification** (0.5h)

- Run coverage report
- Identify any remaining gaps
- Add tests for gaps
- Verify >90% coverage

---

## 🧪 Testing Strategy

### Test Organization

```
tests/LLM/scripts/generation/
├── test_clipboard_and_shortcuts.py (13 tests) ✅ Existing
├── test_completion_message.py (9 tests) ✅ Existing
├── test_interactive_output_menu.py (18 tests) ✅ Existing
├── test_core_parsing.py (12 tests) ✅ Existing
├── test_workflow_detection.py (12 tests) ← NEW
├── test_achievement_finding.py (15 tests) ← NEW
├── test_conflict_detection.py (10 tests) ← NEW
├── test_integration_workflows.py (8 tests) ← NEW
└── test_edge_cases.py (10 tests) ← NEW
```

**Total**: 52 existing + 55 new = 107 tests

### Test Fixtures

Reuse existing fixtures from conftest.py:

- temp_plan_file
- temp_subplan_file
- temp_execution_file
- mock_clipboard

Add new fixtures:

- mock_filesystem_state (for workflow tests)
- sample_plan_content (for parsing tests)
- conflict_scenarios (for conflict tests)

### Coverage Target

Current: ~25% (52 tests, 7 of 27 functions)
Target: >90% (107 tests, 25+ of 27 functions)

Functions to Test (20 untested):

- find_next_achievement_from_archive()
- find_next_achievement_from_root()
- is_achievement_complete()
- get_plan_status()
- is_plan_complete()
- find_next_achievement_hybrid()
- detect_validation_scripts()
- estimate_section_size()
- find_archive_location()
- calculate_handoff_size()
- inject_project_context()
- fill_template()
- find_subplan_for_achievement()
- check_subplan_status()
- detect_workflow_state_filesystem()
- detect_plan_filesystem_conflict()
- detect_workflow_state()
- generate_prompt()
- prompt_interactive_menu()
- main() (integration tests)

---

## 🔄 Execution Strategy

**Single EXECUTION_TASK**: All testing work in one EXECUTION (systematic, sequential)

**Rationale**:

- Tests are interdependent (integration builds on unit)
- Coverage is measured holistically
- Single iteration log is clearer
- All work completes together

**Execution Plan**:

1. Create EXECUTION_TASK_PROMPT-GENERATOR-UX-AND-FOUNDATION_13_01.md
2. Implement Phase 1: Workflow tests (2h)
3. Implement Phase 2: Achievement tests (2h)
4. Implement Phase 3: Conflict tests (1h)
5. Implement Phase 4: Integration tests (1.5h)
6. Implement Phase 5: Edge case tests (1h)
7. Verify coverage >90% (0.5h)
8. Complete EXECUTION_TASK

**Timeline**: 6-8 hours (single session or split across 2 sessions)

---

## ✅ Success Criteria

**Must Have**:

- [ ] 55+ new tests added
- [ ] All 20 untested functions have tests
- [ ] Coverage report shows >90%
- [ ] All tests passing (100%)
- [ ] Integration tests cover complete workflows

**Should Have**:

- [ ] Edge case tests for all error scenarios
- [ ] Performance tests (response time <3s)
- [ ] Fixtures reusable for future tests
- [ ] Test documentation clear

**Nice to Have**:

- [ ] Property-based tests (hypothesis)
- [ ] Mutation testing (verify test quality)
- [ ] Benchmark tests (track performance)

---

## 📊 Expected Results

**Test Coverage**:

- Before: 25% (52 tests, 7 functions)
- After: 90%+ (107 tests, 25+ functions)
- Improvement: 65 percentage points

**Test Files**:

- Before: 4 test files
- After: 9 test files
- New: 5 test files

**Confidence**:

- Before: Can't refactor safely (untested code)
- After: Can refactor confidently (comprehensive tests)
- Impact: Enables Priority 2 work (filesystem state, class refactor)

**Quality**:

- All code paths tested
- Edge cases covered
- Integration verified
- Production-ready

---

**Status**: ✅ Design Complete, Ready for Execution  
**Next**: Create EXECUTION_TASK and begin systematic testing
