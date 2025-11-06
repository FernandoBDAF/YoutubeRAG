# SUBPLAN: source_count Accuracy Fix

**Mother Plan**: PLAN_ENTITY-RESOLUTION-REFACTOR.md  
**Achievement Addressed**: Achievement 3.5.3  
**Status**: In Progress  
**Created**: 2025-11-06  
**Estimated Effort**: 1 hour

---

## 🎯 Objective

Fix source_count inflation on reruns by only incrementing source_count when adding a new chunk_id to source_chunks. Currently, `$inc` increments source_count on every upsert, regardless of whether the chunk was already counted, causing source_count to inflate on reruns.

**Impact**: Accurate entity importance metrics, correct trust scoring, reliable source_count that matches actual source_chunks.

---

## 📋 What Needs to Be Created

### Files to Modify

1. **`business/stages/graphrag/entity_resolution.py`**:
   - Modify `_upsert_entity()` to only increment source_count if chunk_id is not already in source_chunks

### Functions to Modify

1. **`_upsert_entity()`**:
   - Check if entity exists and if chunk_id is in source_chunks
   - Only increment source_count if chunk_id is not in source_chunks
   - Use conditional increment logic

---

## 🔧 Approach

### Step 1: Check if Chunk Already Counted

- Before upsert, check if entity exists
- If exists, check if chunk_id is in source_chunks array
- Only increment source_count if chunk_id is not in source_chunks

### Step 2: Conditional Increment

- Use MongoDB's conditional update pattern
- Increment source_count only when adding new chunk_id
- Use `$addToSet` for source_chunks (already doing this)
- Conditionally increment based on whether chunk_id was already present

### Step 3: Alternative Approach (Simpler)

- Read entity first (if exists)
- Check if chunk_id in source_chunks
- Only include `$inc` in update if chunk_id not in source_chunks
- This requires a read-before-write, but ensures accuracy

### Step 4: Best Approach (Atomic)

- Use MongoDB aggregation pipeline in update (if supported)
- Or use two-step: check existence, then conditional update
- Or: Always use `$addToSet` for source_chunks, then set source_count = size of source_chunks array

**Chosen Approach**: Check if entity exists and if chunk_id in source_chunks, then conditionally increment. This is accurate and clear.

---

## ✅ Tests Required

### Test File

**File**: `tests/business/stages/graphrag/test_entity_resolution_stage_source_count.py`

### Test Cases

1. **Test source_count Increments on New Chunk**:

   - Create entity with chunk_1
   - Add chunk_2
   - Verify source_count = 2

2. **Test source_count Unchanged on Rerun**:

   - Create entity with chunk_1 (source_count = 1)
   - Rerun same chunk_1
   - Verify source_count = 1 (not 2)

3. **Test source_count Matches source_chunks Length**:

   - Add multiple chunks
   - Verify source_count == len(source_chunks)

4. **Test New Entity source_count**:
   - Create new entity
   - Verify source_count = 1

---

## 🎯 Expected Results

### Functional Changes

- source_count only increments when adding new chunk_id
- source_count == len(source_chunks) always
- Reruns don't inflate source_count

### Observable Outcomes

- Database validation shows source_count matches source_chunks length
- Rerunning same chunk doesn't increase source_count
- Accurate metrics for trust scoring

### Success Indicators

- ✅ source_count == len(source_chunks) for all entities
- ✅ Reruns don't increase source_count
- ✅ New chunks correctly increment source_count
- ✅ All tests passing

---

## 🔗 Dependencies

- None (this is a bug fix, independent of other achievements)
- Uses existing upsert infrastructure

---

## 📝 Execution Task Reference

- **EXECUTION_TASK_ENTITY-RESOLUTION-REFACTOR_36_01.md** - Implementation log

---

## 🔍 Key Implementation Details

### Conditional Increment Logic

```python
# Check if entity exists
existing_entity = entities_collection.find_one({"entity_id": entity_id})

if existing_entity:
    source_chunks = existing_entity.get("source_chunks", [])
    is_new_chunk = chunk_id not in source_chunks
else:
    is_new_chunk = True  # New entity, always increment

# Only increment if new chunk
if is_new_chunk:
    update["$inc"] = {"source_count": 1}
```

### Alternative: Set source_count from source_chunks

After `$addToSet`, we could set `source_count = len(source_chunks)`, but this requires reading the updated document, which is less efficient.

**Chosen**: Conditional increment (clearer, more efficient).

---

**Status**: ✅ Complete  
**Completed**: 2025-11-06

---

## ✅ Implementation Summary

**Code Changes**:

- Modified `_upsert_entity()` to check if chunk_id already in source_chunks
- Conditional source_count increment (only if new chunk)
- Added source_count = 1 to $setOnInsert for new entities

**Tests**:

- Created `test_entity_resolution_stage_source_count.py` with 4 test cases
- All tests passing: new chunk increments, rerun doesn't increment, source_count matches source_chunks length

**Next**: Production validation to confirm source_count accuracy
