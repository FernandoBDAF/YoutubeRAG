# SUBPLAN: Mention Deduplication & Idempotency Fix

**Mother Plan**: PLAN_ENTITY-RESOLUTION-REFACTOR.md  
**Achievement Addressed**: Achievement 3.5.2  
**Status**: In Progress  
**Created**: 2025-11-06  
**Estimated Effort**: 1 hour

---

## 🎯 Objective

Fix duplicate mentions created on reruns by adding a unique index on (entity_id, chunk_id, position) and handling duplicate errors gracefully. This ensures reruns are idempotent and prevents duplicate data in the database.

**Impact**: Reruns won't create duplicate mentions, database stays clean, idempotent operations.

---

## 📋 What Needs to Be Created

### Files to Modify

1. **`business/services/graphrag/indexes.py`**:

   - Add unique index on (entity_id, chunk_id, position) in `_create_entity_mentions_indexes()`

2. **`business/stages/graphrag/entity_resolution.py`** (optional):
   - Handle duplicate key errors gracefully in `_store_entity_mentions()`
   - Log duplicate attempts but don't fail

### Functions to Modify

1. **`_create_entity_mentions_indexes()`**:
   - Add unique index: `[("entity_id", 1), ("chunk_id", 1), ("position", 1)]`
   - Name: `entity_chunk_position_unique`

---

## 🔧 Approach

### Step 1: Add Unique Index

- In `_create_entity_mentions_indexes()`, add unique index on (entity_id, chunk_id, position)
- Use `unique=True` parameter
- Handle case where index might already exist (idempotent index creation)

### Step 2: Handle Duplicate Errors (Optional but Recommended)

- In `_store_entity_mentions()`, catch `DuplicateKeyError` from pymongo
- Log duplicate attempts but don't fail
- Continue processing other mentions

### Step 3: Test Idempotency

- Create test that reruns same chunk
- Verify no duplicate mentions created
- Verify index prevents duplicates

---

## ✅ Tests Required

### Test File

**File**: `tests/business/stages/graphrag/test_entity_resolution_stage_idempotency.py`

### Test Cases

1. **Test Unique Index Creation**:

   - Verify unique index is created on (entity_id, chunk_id, position)
   - Verify index creation is idempotent (can run twice)

2. **Test Duplicate Prevention**:

   - Insert mention with (entity_id, chunk_id, position)
   - Try to insert same mention again
   - Verify duplicate key error is raised (or handled gracefully)

3. **Test Rerun Idempotency**:
   - Process same chunk twice
   - Verify no duplicate mentions created
   - Verify second run doesn't fail

---

## 🎯 Expected Results

### Functional Changes

- Unique index on (entity_id, chunk_id, position) exists
- Duplicate mentions cannot be inserted
- Reruns are idempotent (no duplicates created)

### Observable Outcomes

- Database validation shows no duplicate mentions
- Rerunning same chunk doesn't create new mentions
- Clean database without duplicate data

### Success Indicators

- ✅ Unique index created successfully
- ✅ Duplicate insert attempts handled gracefully
- ✅ Reruns are idempotent
- ✅ No duplicate mentions in database

---

## 🔗 Dependencies

- None (this is a bug fix, independent of other achievements)
- Uses existing index creation infrastructure

---

## 📝 Execution Task Reference

- **EXECUTION_TASK_ENTITY-RESOLUTION-REFACTOR_35_01.md** - Implementation log

---

## 🔍 Key Implementation Details

### Unique Index Structure

```python
entity_mentions.create_index(
    [("entity_id", 1), ("chunk_id", 1), ("position", 1)],
    name="entity_chunk_position_unique",
    unique=True
)
```

### Error Handling

- Catch `pymongo.errors.DuplicateKeyError`
- Log duplicate attempt but continue
- Don't fail entire batch on duplicate

### Idempotency

- Same (entity_id, chunk_id, position) → only one mention
- Reruns don't create duplicates
- Safe to run multiple times

---

**Status**: ✅ Complete  
**Completed**: 2025-11-06

---

## ✅ Implementation Summary

**Code Changes**:

- Added unique index on (entity_id, chunk_id, position) in `_create_entity_mentions_indexes()`
- Added DuplicateKeyError handling in `_store_entity_mentions()`
- Index creation is idempotent (can run multiple times)

**Tests**:

- Created `test_entity_resolution_stage_idempotency.py` with 5 test cases
- All tests passing: unique index creation, duplicate prevention, rerun idempotency

**Next**: Production validation to confirm no duplicate mentions
