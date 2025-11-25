# SUBPLAN: Update Scripts for Dual Structure Support

**Type**: SUBPLAN  
**Mother Plan**: PLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING.md  
**Plan**: Workflow Automation & Workspace Restructuring  
**Achievement Addressed**: Achievement 0.1 (Update Scripts for Dual Structure Support)  
**Achievement**: 0.1  
**Status**: In Progress  
**Created**: 2025-11-08 22:00 UTC  
**Estimated Effort**: 2-3 hours

**File Location**: `work-space/subplans/SUBPLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_01.md`

**Size**: 200-600 lines

---

## 🎯 Objective

Enable scripts to detect and work with both flat and nested workspace structures during migration. This implements Achievement 0.1 and provides the foundation for safe migration by allowing scripts to support both structures simultaneously, enabling a gradual transition without breaking existing functionality.

---

## 📋 What Needs to Be Created

### Files to Create

- `LLM/scripts/workflow/structure_detection.py` - Structure detection function
  - Purpose: Detect whether workspace uses flat or nested structure
  - Function: `detect_structure(plan_path: Path) -> str` returns "flat" or "nested"

### Files to Modify

- `LLM/scripts/generation/generate_prompt.py`

  - Modify: `find_subplan_for_achievement()` function
  - Add: Support for both flat and nested structures
  - Check: Both `work-space/subplans/` (flat) and `plan_folder / "subplans"` (nested)

- `LLM/scripts/generation/generate_execution_prompt.py`

  - Modify: `find_previous_executions()` function
  - Add: Support for both flat and nested structures
  - Check: Both `work-space/execution/` (flat) and `plan_folder / "execution"` (nested)

- `LLM/scripts/generation/generate_subplan_prompt.py`
  - Modify: `find_execution_files()` function
  - Add: Support for both flat and nested structures

### Functions/Classes to Add

- `detect_structure(plan_path: Path) -> str` in `structure_detection.py`
  - Logic: Check if `plan_path.parent / "subplans"` exists → "nested", else "flat"
  - Returns: "flat" or "nested"

### Functions to Modify

- `find_subplan_for_achievement(feature_name: str, achievement_num: str) -> Optional[Path]`

  - Add: Structure detection call
  - Add: Check both structures (flat first for backward compatibility, then nested)
  - Return: First found SUBPLAN

- `find_execution_for_subplan(subplan_path: Path) -> Optional[Path]`
  - Add: Structure detection call
  - Add: Check both structures
  - Return: First found EXECUTION_TASK

---

## 🎯 Execution Strategy

**Pattern**: Single EXECUTION (straightforward implementation)

**Rationale**: This is a focused change - add structure detection and update discovery functions. No need for multiple executions or parallel work.

**Execution Plan**:

1. Create structure detection function
2. Update discovery functions to use structure detection
3. Test with both structures
4. Verify backward compatibility

---

## 📝 Approach

### Step 1: Create Structure Detection Function

1. Create `LLM/scripts/workflow/structure_detection.py`
2. Implement `detect_structure(plan_path: Path) -> str`:
   ```python
   def detect_structure(plan_path: Path) -> str:
       """Detect if workspace uses flat or nested structure."""
       plan_folder = plan_path.parent
       subplans_folder = plan_folder / "subplans"
       if subplans_folder.exists() and subplans_folder.is_dir():
           return "nested"
       return "flat"
   ```
3. Add docstring and type hints
4. Handle edge cases (missing parent, etc.)

### Step 2: Update Discovery Functions

1. Import `detect_structure` in `generate_prompt.py`
2. Modify `find_subplan_for_achievement()`:
   - Call `detect_structure(plan_path)` to determine structure
   - If "nested": Check `plan_folder / "subplans" / SUBPLAN_*.md`
   - If "flat": Check `work-space/subplans/SUBPLAN_*.md` (existing logic)
   - Return first found
3. Apply same pattern to `find_execution_for_subplan()` in other scripts
4. Maintain backward compatibility (check flat first if ambiguous)

### Step 3: Testing

1. Create unit tests for `detect_structure()`:
   - Test with nested structure (subplans folder exists)
   - Test with flat structure (no subplans folder)
   - Test edge cases (missing parent, etc.)
2. Create integration tests:
   - Test `find_subplan_for_achievement()` with flat structure
   - Test `find_subplan_for_achievement()` with nested structure
   - Test both structures present (should prefer nested)
3. Run all tests to verify

---

## ✅ Deliverables

1. **Structure Detection Function**:

   - File: `LLM/scripts/workflow/structure_detection.py`
   - Function: `detect_structure(plan_path: Path) -> str`
   - Tests: Unit tests in `tests/LLM/scripts/workflow/test_structure_detection.py`

2. **Updated Discovery Functions**:

   - `find_subplan_for_achievement()` in `generate_prompt.py` (dual support)
   - `find_previous_executions()` in `generate_execution_prompt.py` (dual support)
   - `find_execution_files()` in `generate_subplan_prompt.py` (dual support)

3. **Tests**:
   - Unit tests for structure detection (>90% coverage)
   - Integration tests for discovery with both structures
   - Test file: `tests/LLM/scripts/workflow/test_structure_detection.py`
   - Integration test file: `tests/LLM/scripts/generation/test_dual_structure_discovery.py`

---

## 🧪 Tests

### Unit Tests (structure_detection.py)

**Test Cases**:

1. `test_detect_structure_nested()` - Returns "nested" when subplans folder exists
2. `test_detect_structure_flat()` - Returns "flat" when subplans folder doesn't exist
3. `test_detect_structure_missing_parent()` - Handles missing parent gracefully
4. `test_detect_structure_subplans_is_file()` - Handles subplans as file (not dir)

**Coverage Requirement**: >90%

### Integration Tests (discovery functions)

**Test Cases**:

1. `test_find_subplan_flat_structure()` - Finds SUBPLAN in flat structure
2. `test_find_subplan_nested_structure()` - Finds SUBPLAN in nested structure
3. `test_find_subplan_both_structures()` - Prefers nested when both exist
4. `test_find_execution_flat_structure()` - Finds EXECUTION in flat structure
5. `test_find_execution_nested_structure()` - Finds EXECUTION in nested structure

**Coverage Requirement**: >90%

---

## 📊 Expected Results

**Success Criteria**:

- ✅ Structure detection function works correctly
- ✅ Discovery functions support both structures
- ✅ Backward compatibility maintained (flat structure still works)
- ✅ All tests pass (>90% coverage)
- ✅ Scripts can work with both structures during migration

**Validation**:

- Run: `pytest tests/LLM/scripts/workflow/test_structure_detection.py -v`
- Run: `pytest tests/LLM/scripts/generation/test_dual_structure_discovery.py -v`
- Verify: `python -c "from LLM.scripts.workflow.structure_detection import detect_structure; print('OK')"`

---

## 🔄 Active EXECUTION_TASKs

- [ ] **EXECUTION_TASK_01_01**: Status: In Progress

---

## 📝 Execution Log

- **EXECUTION_TASK_01_01**: Created 2025-11-08, Status: In Progress

---

## 📚 References

- `PLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING.md` - Mother PLAN
- `LLM/templates/SUBPLAN-TEMPLATE.md` - SUBPLAN template
- `EXECUTION_ANALYSIS_WORKSPACE-STRUCTURE-RESTRUCTURING.md` - Restructuring context
- `LLM/scripts/generation/generate_prompt.py` - Script to modify

---

## ✅ Success Criteria

**This SUBPLAN is Complete When**:

- [ ] Structure detection function created and tested
- [ ] All discovery functions updated for dual support
- [ ] All tests passing (>90% coverage)
- [ ] Backward compatibility verified
- [ ] Scripts work with both structures
- [ ] EXECUTION_TASK complete with learnings

---

**Status**: In Progress  
**Next**: Execute EXECUTION_TASK_01_01 - implement structure detection and update discovery functions
