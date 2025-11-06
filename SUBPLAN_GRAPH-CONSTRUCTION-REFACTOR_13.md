# SUBPLAN: Unique Indexes for Idempotency

**Parent Plan**: PLAN_GRAPH-CONSTRUCTION-REFACTOR.md  
**Achievement**: 1.3  
**Priority**: HIGH  
**Status**: ✅ COMPLETE  
**Created**: 2025-11-06

---

## 🎯 Objective

Verify and add unique indexes to ensure idempotent operations and prevent duplicate relationships on reruns.

**Current State**:
- `relationship_id` already has unique index (verified)
- No composite unique index on (subject_id, object_id, predicate)

**Target State**:
- Verify unique index on `relationship_id` exists
- Consider composite unique index on `(subject_id, object_id, predicate)` with partial filter for `relationship_type: "extracted"` only
- Handle duplicate key errors gracefully in all relationship insertion paths

---

## 📋 What Needs to Be Created

### 1. Index Verification/Addition

**File**: `business/services/graphrag/indexes.py`

- **`_create_relations_indexes()`** (line ~91):
  - Verify unique index on `relationship_id` exists (already exists)
  - Optionally add composite unique index on `(subject_id, object_id, predicate)` with partial filter for `relationship_type: "extracted"`
  - Document rationale for index choice

### 2. Error Handling

**File**: `business/stages/graphrag/graph_construction.py`

- Handle `DuplicateKeyError` gracefully in:
  - `_store_resolved_relationships()` (batch insert)
  - `_add_co_occurrence_relationships()` (batch insert)
  - `_add_semantic_similarity_relationships()` (batch insert)
  - `_add_cross_chunk_relationships()` (batch insert)
  - `_add_bidirectional_relationships()` (batch insert)

### 3. Tests

**File**: `tests/business/stages/graphrag/test_graph_construction_idempotency.py` (new)

- Test: Unique index on relationship_id exists
- Test: Reruns don't create duplicates
- Test: DuplicateKeyError handled gracefully
- Test: Idempotent operations

---

## 🔧 Approach

### Step 1: Verify Existing Index

1. Check `business/services/graphrag/indexes.py`
2. Confirm unique index on `relationship_id` exists
3. Document it's already there

### Step 2: Add Error Handling

1. Import `DuplicateKeyError` from `pymongo.errors`
2. Wrap batch inserts in try-except
3. Log duplicate key errors as expected (idempotency)
4. Don't treat as failures

### Step 3: Write Tests

1. Create test file
2. Write tests for idempotency
3. Run tests

### Step 4: Optional Composite Index

1. Consider if needed (may not be necessary with relationship_id unique)
2. If added, use partial filter for extracted relationships only

---

## ✅ Expected Results

### Success Criteria

- [ ] Unique index on relationship_id verified
- [ ] DuplicateKeyError handled gracefully
- [ ] Reruns don't create duplicates
- [ ] All tests passing
- [ ] No regressions

### Validation

- Run test suite
- Manually verify: rerun same chunk → no duplicates

---

## 📝 Notes

- **Index Choice**: `relationship_id` unique index is sufficient because:
  - relationship_id is deterministic (includes subject, object, predicate)
  - Multiple predicates per pair have different relationship_ids
  - Composite index may not be necessary

- **Error Handling**: Duplicate key errors are expected on reruns (idempotency)

---

## 🔗 Related

- **Achievement 1.1**: Density Computation (completed)
- **Achievement 1.2**: Reverse Mapping Collision (completed)
- **Achievement 3.5.2** (Entity Resolution): Similar unique index pattern

