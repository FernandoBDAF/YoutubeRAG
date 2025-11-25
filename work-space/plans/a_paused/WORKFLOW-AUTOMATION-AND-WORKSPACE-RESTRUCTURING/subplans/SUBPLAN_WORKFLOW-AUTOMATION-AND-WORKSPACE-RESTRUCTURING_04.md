# SUBPLAN: Update Discovery Scripts for Nested Structure

**Type**: SUBPLAN  
**Mother Plan**: PLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING.md  
**Plan**: Workflow Automation & Workspace Restructuring  
**Achievement Addressed**: Achievement 0.4 (Update Discovery Scripts for Nested Structure)  
**Achievement**: 0.4  
**Status**: Design Phase  
**Created**: 2025-11-09 03:10 UTC  
**Estimated Effort**: 3-4 hours

**File Location**: `work-space/plans/WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING/subplans/SUBPLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_04.md`

**Size**: 200-600 lines

---

## 🎯 Objective

Refactor ALL discovery functions to use nested workspace structure exclusively. Remove flat structure support (now obsolete after Achievement 0.3 migration). This simplifies code, improves performance, and enables cleaner automation for Priority 1-4 work.

---

## 🎓 Context (Minimal Reading)

**Prerequisites Completed**:
- ✅ Achievement 0.1: Dual structure support enabled
- ✅ Achievement 0.2: Migration script created
- ✅ Achievement 0.3: All 16 PLANs migrated to nested structure

**Current State**:
- All PLAN files in work-space/plans/PLAN_NAME/
- All SUBPLANs in work-space/plans/PLAN_NAME/subplans/
- All EXECUTION_TASKs in work-space/plans/PLAN_NAME/execution/
- Discovery code still checks flat structure as fallback (legacy support)

**What's Wrong**:
- Complex discovery logic (checks multiple locations)
- Dual-structure conditional checks throughout code
- Unnecessary filename pattern parsing
- Performance overhead from pattern searches

**Opportunity**:
- Nested structure = built-in hierarchy
- Direct path access = faster discovery
- Simplified code = fewer bugs
- Remove legacy code = cleaner maintenance

---

## 🔀 Execution Strategy

**Multiple Executions**: Yes, coordinated refactoring

**Why Multiple**:
- Large codebase to refactor systematically
- Different areas with different patterns:
  1. Core discovery functions (generate_prompt.py)
  2. Validation scripts (validate_*.py)
  3. Archive discovery (manual_archive.py)
  4. Sub-generators (generate_subplan_prompt.py, generate_execution_prompt.py)
- Can work on these in parallel (mostly independent)
- Testing each area independently reduces risk

**Execution Phases**:
1. **EXECUTION_01**: Core discovery refactoring (find_subplan_for_achievement, etc.)
2. **EXECUTION_02**: Validation script updates (validate_registration.py, etc.)
3. **EXECUTION_03**: Archive discovery refactoring
4. **Synthesis**: Test all changes together, document learnings

---

## 📋 Detailed Refactoring Plan

### Discovery Functions to Update

**1. `find_subplan_for_achievement()` in generate_prompt.py (Lines 748-805)**

Current:
```python
# Checks: nested structure, flat structure, archive
# Uses: structure detection, filename patterns
# Returns: Path to SUBPLAN
```

Refactored:
```python
# Only check: nested structure in plan folder
# Simpler logic: given plan file, go to plan/subplans/
# Direct path: work-space/plans/PLAN_NAME/subplans/
# Still check: archive for archived SUBPLANs
```

**2. `find_execution_files()` in generate_subplan_prompt.py (Lines 192-240+)**

Current:
- Finds EXECUTION_TASK files
- Checks flat and nested structure
- Uses pattern matching

Refactored:
- Only check nested: plan/execution/
- Direct path access
- No pattern parsing needed (folder = hierarchy)

**3. `find_previous_executions()` in generate_execution_prompt.py**

Current:
- Searches for previous EXECUTION files
- Checks multiple locations

Refactored:
- Only check: plan/execution/
- Direct folder scan
- Simpler logic

**4. `find_next_achievement_hybrid()` in generate_prompt.py**

Current:
- Complex logic with flat/nested detection
- Multiple conditional branches

Refactored:
- Simplified: assume nested structure
- Direct plan folder access
- Fewer conditions

### Validation Scripts to Update

**Files to update**:
- `validate_registration.py` - find_subplans_for_plan, find_execution_tasks_for_plan
- `validate_achievement_completion.py` - find_subplan_path, find_execution_tasks
- `validate_subplan_executions.py` - find_execution_tasks
- `validate_archive_structure.py` - archive discovery functions

**Changes**:
- Update all discovery calls to use nested-only functions
- Simplify validation logic (nested structure = known hierarchy)
- Add nested structure checks (verify folders exist)
- Remove flat structure assumptions

### Archive Discovery Updates

**Files**:
- `manual_archive.py` - archive operations
- Archive discovery functions throughout

**Changes**:
- Still need to discover archived files
- But archived files still follow naming patterns
- Can optimize based on nested structure assumptions
- Archive location: documentation/archive/

---

## 🧪 Testing Strategy

**Unit Tests**:
- Test each refactored function with nested structure
- Test with actual migrated PLANs
- Test archive discovery
- Verify no breaking changes

**Integration Tests**:
- Test discovery with real workspace (16 PLANs)
- Test with archive
- Test workflow detection (SUBPLAN/EXECUTION)

**Backward Compatibility**:
- Function signatures: minimal changes (if any, well-documented)
- All call sites updated simultaneously
- No surprise breaking changes

---

## 📊 Expected Simplifications

**Lines of Code**:
- remove flat structure checks: -50 lines
- Simplify condition logic: -30 lines
- Remove pattern parsing: -20 lines
- Total reduction: ~100 lines of code

**Complexity**:
- Before: Multiple conditional branches (flat vs nested)
- After: Direct path logic (nested only)
- Cyclomatic complexity: Lower
- Readability: Much better

**Performance**:
- Before: Search flat directory for matches
- After: Direct folder path access
- Improvement: O(n) search → O(1) lookup

---

## ✅ Success Criteria

Achievement 0.4 Complete When:

☐ All discovery functions refactored for nested-only access
☐ Flat structure support completely removed
☐ All validation scripts updated with new discovery calls
☐ All call sites of discovery functions updated
☐ Archive discovery still works correctly
☐ All unit tests passing (20+ test cases)
☐ All integration tests passing
☐ Real workspace discovery works (tested with 16 PLANs)
☐ Code is simpler and more maintainable
☐ Performance improved (direct path vs pattern search)
☐ No breaking changes to external APIs
☐ Comprehensive documentation of changes

---

## ⚠️ Risk Mitigation

**Risk 1: Breaking Changes to Callers**
- Mitigation: Find all call sites before refactoring
- Update all callers simultaneously
- Test thoroughly

**Risk 2: Archive Discovery Breaks**
- Mitigation: Archive files still follow naming patterns
- Test archive discovery separately
- Fallback to pattern matching if needed

**Risk 3: Regression**
- Mitigation: Keep old tests, add new tests
- Run full test suite
- Test with real workspace

---

## 📁 Files to Modify

**Generation Scripts** (Highest Priority):
- `LLM/scripts/generation/generate_prompt.py` (748-805: main discovery function)
- `LLM/scripts/generation/generate_subplan_prompt.py` (192-240+: execution files)
- `LLM/scripts/generation/generate_execution_prompt.py` (179+: previous executions)

**Validation Scripts**:
- `LLM/scripts/validation/validate_registration.py` (find_subplans_for_plan, etc.)
- `LLM/scripts/validation/validate_achievement_completion.py` (find_subplan_path, etc.)
- `LLM/scripts/validation/validate_subplan_executions.py` (find_execution_tasks)

**Archive Scripts**:
- `LLM/scripts/archiving/manual_archive.py` (find_plan_file)
- `LLM/scripts/archiving/archive_completed.py` (archive discovery)

**Test Files** (to update/create):
- `test_nested_discovery.py` (new unit tests for nested discovery)
- `test_integration_nested.py` (integration tests with real workspace)

---

## 🔗 Dependencies & Next Steps

**Blocks**: 
- Priority 1 (needs clean discovery)
- Priority 2-4 (depends on unified discovery)

**Enables**:
- Achievement 0.5 (archive refactoring)
- Achievement 1.1 (unified discovery)
- Cleaner automation in Priorities 2-4

---

## 🎓 Key Insights

1. **Nested Structure Simplifies Everything**
   - PLAN folder = direct access to components
   - No complex pattern matching needed
   - Folder hierarchy = document hierarchy

2. **Remove Legacy Code**
   - Flat structure is gone (0.3 migrated everything)
   - No need for backward compatibility
   - Opportunity to simplify significantly

3. **Test-Driven Refactoring**
   - Keep old tests passing
   - Add new tests for nested behavior
   - Full regression testing

---

**SUBPLAN Status**: Ready for Execution

Next: Executor creates EXECUTION_TASKs and performs refactoring in phases.

