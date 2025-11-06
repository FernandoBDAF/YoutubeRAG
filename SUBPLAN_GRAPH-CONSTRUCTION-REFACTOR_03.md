# SUBPLAN: Batch Success Counter Fixed

**Parent Plan**: PLAN_GRAPH-CONSTRUCTION-REFACTOR.md  
**Achievement**: 0.3  
**Priority**: CRITICAL  
**Status**: ✅ COMPLETE  
**Created**: 2025-11-06

---

## 🎯 Objective

Fix batch success counter to accurately report successful processing counts instead of always showing 0.

**Current Problem**:
- `handle_doc` returns `None` on success
- `process_batch` counts: `sum(1 for r in results if r is not None)`
- This always results in 0 successful_count

**Target State**:
- `handle_doc` returns `True` on success, `False` on failure
- `process_batch` counts `True` values
- Accurate success logging

---

## 📋 What Needs to Be Created

### 1. Modified Methods

**File**: `business/stages/graphrag/graph_construction.py`

- **`handle_doc()`** (line ~101):
  - Change return type from `Optional[Dict[str, Any]]` to `bool`
  - Return `True` on success
  - Return `False` on failure (or use `_mark_construction_failed` which may return None)

- **`process_batch()`** (line ~1126):
  - Change counting logic from `if r is not None` to `if r is True`
  - Or: Use `self.stats["updated"]` count instead

### 2. Tests

**File**: `tests/business/stages/graphrag/test_graph_construction_batch_counter.py` (new)

- Test: handle_doc returns True on success
- Test: handle_doc returns False on failure
- Test: process_batch counts successes accurately
- Test: Batch with 5 successes reports "5/5 successful"

---

## 🔧 Approach

### Step 1: Write Tests First (TDD)

1. Create test file
2. Write tests for return values
3. Run tests (should fail - returns None)

### Step 2: Fix handle_doc

1. Change return type annotation to `bool`
2. Return `True` after successful update
3. Return `False` on exceptions or failures
4. Update `_mark_construction_failed` if needed

### Step 3: Fix process_batch

1. Change counting logic to check for `True`
2. Or use `self.stats["updated"]` if available

### Step 4: Run Tests

1. All new tests passing
2. No regressions in existing tests

---

## ✅ Expected Results

### Success Criteria

- [ ] handle_doc returns True on success
- [ ] handle_doc returns False on failure
- [ ] process_batch counts successes accurately
- [ ] Logging shows correct success count
- [ ] All tests passing
- [ ] No regressions

### Validation

- Run test suite
- Manually verify: batch with 5 successes logs "5/5 successful"

---

## 📝 Notes

- **Alternative Approach**: Could use `self.stats["updated"]` instead of return values
- **Backward Compatibility**: Return value change is internal (not used elsewhere)
- **Logging**: This fix improves observability

---

## 🔗 Related

- **Achievement 0.1**: Relationship Existence Checks (completed)
- **Achievement 0.2**: source_count Inflation (completed)
- **Achievement 0.3**: This achievement

