# SUBPLAN: Atomic Upsert Operations

**Mother Plan**: PLAN_ENTITY-RESOLUTION-REFACTOR.md  
**Achievement Addressed**: Achievement 2.1 - Atomic Upsert Operations Implemented  
**Status**: In Progress  
**Created**: 2025-11-06 23:00 UTC  
**Estimated Effort**: 3-4 hours

---

## 🎯 Objective

Replace the separate `_update_existing_entity` and `_insert_new_entity` methods with a single atomic `_upsert_entity` operation using `find_one_and_update(..., upsert=True)`. This eliminates race conditions and ensures atomicity when multiple processes try to update the same entity concurrently.

---

## 📋 What Needs to Be Created

### Files to Modify

1. **`business/stages/graphrag/entity_resolution.py`**:
   - Replace `_update_existing_entity` and `_insert_new_entity` with `_upsert_entity`
   - Use `find_one_and_update(..., upsert=True)` with proper merge policy:
     - `$setOnInsert` for immutable fields (created_at, first_seen, entity_id, type)
     - `$set` for updateable fields (description, updated_at, canonical_name, name)
     - `$inc` for counters (source_count)
     - `$addToSet` for arrays (aliases, aliases_normalized, source_chunks)
     - `$max` for confidence (keep highest)
     - `$push` with `$slice` for provenance (capped array)

---

## 🔧 Approach

### Step 1: Create Atomic Upsert Method

- Implement `_upsert_entity()` using `find_one_and_update(..., upsert=True)`
- Use `ReturnDocument.AFTER` to get updated document
- Implement proper merge policy with all MongoDB operators

### Step 2: Replace Separate Methods

- Update `_store_resolved_entities()` to use `_upsert_entity()` instead of separate methods
- Remove `_update_existing_entity` and `_insert_new_entity` methods

### Step 3: Test Atomicity

- Ensure concurrent updates don't create duplicates
- Verify merge policy works correctly

---

## ✅ Expected Results

- Single atomic operation for insert/update
- No race conditions
- Proper merge policy implemented
- All fields handled correctly

---

**Status**: Ready to Execute  
**Next**: Implement \_upsert_entity() with atomic operations
