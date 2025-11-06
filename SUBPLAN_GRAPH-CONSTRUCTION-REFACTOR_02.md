# SUBPLAN: source_count Inflation Fixed

**Parent Plan**: PLAN_GRAPH-CONSTRUCTION-REFACTOR.md  
**Achievement**: 0.2  
**Priority**: CRITICAL  
**Status**: ✅ COMPLETE  
**Created**: 2025-11-06

---

## 🎯 Objective

Fix source_count inflation on reruns by only incrementing when chunk_id is new to source_chunks array, matching the fix applied in entity resolution (Achievement 3.5.3).

**Current Problem**:
- `_update_existing_relationship` always `$inc: {source_count: 1}`
- Same chunk replays inflate source_count
- Same bug we just fixed in entity resolution

**Target State**:
- Check if chunk_id already in source_chunks
- Only increment source_count if chunk_id is new
- Set source_count=1 in `$setOnInsert` for new relationships
- source_count == len(source_chunks) always

---

## 📋 What Needs to Be Created

### 1. Modified Method

**File**: `business/stages/graphrag/graph_construction.py`

- **`_update_existing_relationship()`** (line ~308):
  - Check if `chunk_id` is already in `source_chunks`
  - Conditionally add `$inc: {source_count: 1}` only if new chunk
  - Keep `$addToSet: {source_chunks: chunk_id}` (already correct)

- **`_insert_new_relationship()`** (line ~349):
  - Set `source_count: 1` in document (already correct, verify)

### 2. Tests

**File**: `tests/business/stages/graphrag/test_graph_construction_source_count.py` (new)

- Test: New relationship starts with source_count = 1
- Test: source_count increments on new chunk
- Test: source_count unchanged on rerun of same chunk
- Test: source_count matches source_chunks length

---

## 🔧 Approach

### Step 1: Write Tests First (TDD)

1. Create test file
2. Write tests for source_count accuracy
3. Run tests (should fail - always increments)

### Step 2: Fix _update_existing_relationship

1. Get existing relationship's source_chunks
2. Check if chunk_id in source_chunks
3. Conditionally add `$inc: {source_count: 1}` only if new chunk
4. Keep `$addToSet: {source_chunks: chunk_id}`

### Step 3: Verify _insert_new_relationship

1. Ensure source_count = 1 for new relationships
2. Verify source_chunks = [chunk_id]

### Step 4: Run Tests

1. All new tests passing
2. No regressions in existing tests

---

## ✅ Expected Results

### Success Criteria

- [ ] source_count only increments for new chunks
- [ ] source_count unchanged on reruns
- [ ] source_count == len(source_chunks) always
- [ ] New relationships start with source_count = 1
- [ ] All tests passing
- [ ] No regressions

### Validation

- Run test suite
- Manually verify: rerun same chunk → source_count unchanged
- Verify: new chunk → source_count increments

---

## 📝 Notes

- **Pattern Reuse**: Same approach as entity resolution Achievement 3.5.3
- **Backward Compatibility**: Existing relationships will have correct source_count on next update
- **Performance**: Minimal overhead (one array check per update)

---

## 🔗 Related

- **Achievement 3.5.3** (Entity Resolution): Same fix pattern
- **Achievement 0.1**: Relationship Existence Checks (just completed)
- **Achievement 0.3**: Batch Success Counter (next)

