# SUBPLAN: Fix Prompt Generator Multi-Execution Detection

**Type**: SUBPLAN  
**Mother Plan**: PLAN_RESTORE-EXECUTION-WORKFLOW-AUTOMATION.md  
**Achievement**: 1.6  
**Status**: ✅ Complete  
**Created**: 2025-11-09 06:30 UTC  
**Estimated Effort**: 3-4 hours

---

## 🎯 Objective

Replace content-based (regex) detection with filesystem-based detection in the prompt generator. This enables proper detection of multi-execution SUBPLANs and eliminates false positives that occur when SUBPLAN content contains the word "Complete" in sections like "Success Criteria".

**Context**: Achievement 1.5 validation revealed that multi-execution SUBPLANs (increasingly common pattern) are incorrectly detected as "complete" due to overly broad regex patterns in `generate_prompt.py`. The improved nested workspace structure from PLAN 3 Achievement 0.3 now makes filesystem-based detection viable and preferable.

**Why This Matters**:

- Multi-execution workflows now critical (validated in Achievement 1.5)
- Current automation blocks multi-execution workflow prompts
- Filesystem structure is stable and encodes workflow relationships
- Cleaner, more maintainable code than regex patterns

---

## 📋 Deliverables

### Files to Modify

1. **`LLM/scripts/generation/generate_prompt.py`**
   - Add `detect_workflow_state_filesystem()` function
   - Update `detect_workflow_state()` to use new function
   - Keep old regex patterns as commented reference
   - Add docstrings explaining filesystem logic

### Files to Create

1. **`tests/LLM/scripts/generation/test_prompt_generator_filesystem.py`**
   - Unit tests for new detection function
   - Integration tests with real workspace
   - Test multi-execution workflows
   - Test edge cases (missing files, partial completion, etc.)

### Documentation

1. **Updated docstrings** in generate_prompt.py
   - Explain filesystem-based detection approach
   - Document workflow state transitions
   - Add examples for each state

---

## 🎨 Approach

### Phase 1: Understand Current Implementation (30 min)

**Actions**:

1. Read current `detect_workflow_state()` function (lines 857-904)
2. Read `check_subplan_status()` function (lines 795-854)
3. Understand the workflow state detection flow
4. Identify all workflow states returned

**Deliverable**: Clear understanding of current logic and flow

### Phase 2: Design Filesystem Detection (1 hour)

**Design the new function**:

1. Map workflow states to filesystem patterns:

   - `no_subplan` → SUBPLAN file doesn't exist
   - `subplan_no_execution` → SUBPLAN exists, no EXECUTION_TASKs
   - `active_execution` → EXECUTION_TASKs exist with In Progress status
   - `subplan_all_executed` → All EXECUTIONs complete, need synthesis
   - `subplan_complete` → SUBPLAN marked ✅ Complete

2. Design function signature:

   ```python
   def detect_workflow_state_filesystem(
       feature_name: str, achievement_num: str, plan_folder: Path
   ) -> Dict[str, any]
   ```

3. Algorithm:
   - Check SUBPLAN path existence
   - Count EXECUTION_TASK files in execution/ folder
   - Check each EXECUTION_TASK's completion status
   - Return state with metadata (count, completed, active)

**Deliverable**: Function design document with pseudocode

### Phase 3: Implement Filesystem Detection (1.5 hours)

**Implementation steps**:

1. Create `detect_workflow_state_filesystem()` function with:

   - SUBPLAN existence check
   - EXECUTION_TASK folder scanning
   - Individual file status checking
   - Comprehensive error handling

2. Add helper function if needed:

   - `_get_execution_files()` - find all EXECUTION_TASKs for achievement
   - `_check_execution_status()` - check single EXECUTION_TASK status

3. Update `detect_workflow_state()` to:

   - Try filesystem detection first
   - Fall back gracefully on errors
   - Return complete state dict

4. Update `main()` to use new detection

**Deliverables**:

- Working detect_workflow_state_filesystem() function
- Updated detect_workflow_state() function
- All error handling in place

### Phase 4: Write Comprehensive Tests (1 hour)

**Unit Tests**:

1. Test each workflow state:

   - [ ] no_subplan state
   - [ ] subplan_no_execution state
   - [ ] active_execution state (single + multiple)
   - [ ] subplan_all_executed state
   - [ ] subplan_complete state

2. Test edge cases:
   - [ ] Missing execution folder
   - [ ] Execution files with unusual names
   - [ ] Permission errors (graceful handling)
   - [ ] Empty execution folder

**Integration Tests**:

1. Test with real workspace PLANs
2. Test GRAPHRAG-OBSERVABILITY-EXCELLENCE (multi-execution)
3. Test RESTORE-EXECUTION-WORKFLOW-AUTOMATION (single execution)
4. Verify correct prompts generated

**Deliverable**: test_prompt_generator_filesystem.py with 15+ test cases

### Phase 5: Integration & Validation (30 min)

**Actions**:

1. Run all tests locally
2. Verify no regressions (single-execution still works)
3. Test with real multi-execution SUBPLAN
4. Verify prompt output is correct
5. Check code quality (docstrings, comments)

**Deliverable**: All tests passing, verified with real data

---

## 🔄 Execution Strategy

**Execution Count**: Single

**Rationale**:

- Clear, sequential work
- No parallelization needed
- Phases build on each other
- Single EXECUTION_TASK sufficient

**EXECUTION_TASK**: `EXECUTION_TASK_RESTORE-EXECUTION-WORKFLOW-AUTOMATION_16_01.md`

---

## 🧪 Tests Required

### Unit Tests (8 tests)

1. **test_filesystem_detection_no_subplan**

   - SUBPLAN doesn't exist
   - Should return `state: no_subplan, recommendation: create_subplan`

2. **test_filesystem_detection_subplan_no_execution**

   - SUBPLAN exists, execution folder empty
   - Should return `state: subplan_no_execution, recommendation: create_execution`

3. **test_filesystem_detection_active_single_execution**

   - SUBPLAN exists, 1 EXECUTION_TASK in progress
   - Should return `state: active_execution, recommendation: continue_execution`

4. **test_filesystem_detection_active_multiple_executions**

   - SUBPLAN exists, 5 EXECUTION_TASKs (3 complete, 2 active)
   - Should return `state: active_execution, recommendation: continue_execution, completed: 3, active: 2`

5. **test_filesystem_detection_all_executed**

   - SUBPLAN exists, all EXECUTION_TASKs complete
   - Should return `state: subplan_all_executed, recommendation: synthesize_results`

6. **test_filesystem_detection_complete**

   - SUBPLAN marked ✅ Complete, all EXECUTION_TASKs complete
   - Should return `state: subplan_complete, recommendation: next_achievement`

7. **test_filesystem_detection_edge_case_missing_execution_folder**

   - Execution folder doesn't exist
   - Should handle gracefully (create list = [])

8. **test_filesystem_detection_edge_case_malformed_filenames**
   - EXECUTION_TASK files with unexpected names
   - Should handle gracefully (skip or filter)

### Integration Tests (5+ tests)

1. **test_integration_graphrag_observability_multi_execution**

   - Real PLAN: PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE
   - Real Achievement: 0.1 (6 planned executions)
   - Verify: Correctly detects active_execution state

2. **test_integration_restore_automation_single_execution**

   - Real PLAN: PLAN_RESTORE-EXECUTION-WORKFLOW-AUTOMATION
   - Real Achievement: 1.1
   - Verify: Correctly detects completion state

3. **test_integration_prompt_generation_with_filesystem_detection**

   - Run full `generate_prompt.py --next` with new detection
   - Verify: Correct prompt generated for multi-execution SUBPLAN

4. **test_integration_no_regressions_single_execution**

   - Verify: Existing single-execution workflows still work
   - Test with 3+ different PLANs

5. **test_integration_filesystem_detection_vs_regex**
   - Compare old regex detection vs new filesystem detection
   - Verify: Filesystem detection more accurate

---

## ✅ Expected Results

### Immediate Outcomes

**Code Changes**:

- New `detect_workflow_state_filesystem()` function (50-80 lines)
- Updated `detect_workflow_state()` function (10-15 lines)
- Helper functions if needed (20-30 lines)
- Total: ~100-120 new lines of code

**Test Coverage**:

- 15+ test cases (unit + integration)
- > 90% coverage of new code
- All tests passing

**Quality Metrics**:

- No regressions in existing functionality
- Multi-execution workflows properly detected
- Prompt output verified with real data

### Long-Term Benefits

✅ Multi-execution SUBPLANs detected correctly  
✅ Automation suggests correct next action  
✅ Scalable approach (works as complexity grows)  
✅ Maintainable code (filesystem rules > regex patterns)  
✅ Foundation for richer automation (metadata, dashboards, etc.)

---

## 📊 Success Criteria

**Functional Success**:

- [ ] Filesystem detection correctly identifies all workflow states
- [ ] Multi-execution SUBPLANs detected as `active_execution`
- [ ] Single-execution SUBPLANs still work correctly
- [ ] Prompt generation works for both single and multi-execution

**Quality Success**:

- [ ] 15+ test cases, all passing
- [ ] > 90% code coverage of new functions
- [ ] No regressions in existing tests
- [ ] Docstrings clear and complete

**Integration Success**:

- [ ] Works with GRAPHRAG-OBSERVABILITY-EXCELLENCE (multi-execution)
- [ ] Works with RESTORE-EXECUTION-WORKFLOW-AUTOMATION (single execution)
- [ ] Works with other real PLANs
- [ ] Prompt output verified by inspection

**Validation Success**:

- [ ] Manual test with `generate_prompt.py --next` on multi-execution SUBPLAN
- [ ] Prompt suggests "continue_execution" instead of "create_subplan"
- [ ] Achievement 1.5 validation scenario now works correctly

---

## 🎓 Designer Notes

### Key Design Decisions

1. **Filesystem Detection Over Regex**:

   - PLAN 3 Achievement 0.3 created stable nested structure
   - Filesystem encodes workflow relationships
   - More robust than content parsing
   - Scalable as complexity grows

2. **Keep Existing Code for Reference**:

   - Comment out old `check_subplan_status()` function
   - Document why regex approach is problematic
   - Preserve knowledge for future reference

3. **Comprehensive Error Handling**:

   - Graceful fallback if filesystem issue
   - Clear error messages
   - No silent failures

4. **Extensive Testing**:
   - Both unit and integration tests
   - Real workspace validation
   - Edge case coverage
   - Regression testing

### Implementation Tips

1. **Start Simple**:

   - Get basic detection working first
   - Add error handling incrementally
   - Test at each step

2. **Use Existing Patterns**:

   - Follow current code style
   - Reuse existing helper functions
   - Match existing naming conventions

3. **Document Thoroughly**:
   - Docstrings for all functions
   - Comments for complex logic
   - Examples in docstrings

---

## 📚 References

**Analysis Document**:

- `EXECUTION_ANALYSIS_PROMPT-GENERATOR-MULTI-EXECUTION-BUG.md` (comprehensive bug analysis with 3 alternatives evaluated)

**Related Code**:

- `LLM/scripts/generation/generate_prompt.py` (main file to modify)
- `LLM/scripts/generation/generate_execution_prompt.py` (has similar issue)
- `LLM/scripts/generation/generate_subplan_prompt.py` (may need updates)

**Real Test Cases**:

- `work-space/plans/GRAPHRAG-OBSERVABILITY-EXCELLENCE/` (multi-execution SUBPLAN with 6 planned executions)
- `work-space/plans/RESTORE-EXECUTION-WORKFLOW-AUTOMATION/` (single-execution SUBPLAN)

**Methodology**:

- LLM-METHODOLOGY.md (section on multi-agent workflow evolution)
- LLM/guides/EXECUTION-ANALYSIS-GUIDE.md (how analysis was done)

---

## 💡 Rationale

**Why This Achievement Now**:

1. Achievement 1.5 revealed the bug in real usage
2. Multi-execution pattern becoming standard
3. Analysis identified clear solution path
4. Filesystem structure from PLAN 3 Achievement 0.3 makes it viable
5. High value fix (enables future automation)

**Why Filesystem Detection**:

1. Nested structure is now standard (no legacy support needed)
2. More accurate than regex (filesystem is source of truth)
3. More maintainable (no regex patterns to maintain)
4. Scales better (works for increasingly complex workflows)
5. Foundation for future enhancements

**Why As Achievement 1.6 in PLAN 2**:

1. Core automation blocker (prevents multi-execution workflows)
2. High-value fix (enables all future multi-execution achievements)
3. Foundation for PLAN 2 goals (automation must work reliably)
4. Relatively short implementation (3-4 hours)
5. Directly addresses bugs discovered in Achievement 1.5 validation

---

**SUBPLAN Status**: Ready for Execution

**Next**: Create EXECUTION_TASK_RESTORE-EXECUTION-WORKFLOW-AUTOMATION_16_01.md and execute the implementation
