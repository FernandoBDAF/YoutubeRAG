# SUBPLAN: Relationship Existence Checks Include Predicate

**Parent Plan**: PLAN_GRAPH-CONSTRUCTION-REFACTOR.md  
**Achievement**: 0.1  
**Priority**: CRITICAL  
**Status**: ✅ COMPLETE  
**Created**: 2025-11-06

---

## 🎯 Objective

Fix relationship existence checks in synthetic relationship methods to include `predicate` in the query, allowing multiple predicates between the same entity pair.

**Current Problem**:
- Co-occurrence, semantic similarity, and cross-chunk methods check existence by `{subject_id, object_id}` only
- Missing `predicate` in existence check
- Cannot add multiple predicates between same entity pair (e.g., "teaches" and "mentors")

**Target State**:
- Existence checks include `predicate`: `{subject_id, object_id, predicate}`
- Multiple predicates per pair allowed
- Optionally check both directions for symmetric predicates

---

## 📋 What Needs to Be Created

### 1. Modified Methods

**File**: `business/stages/graphrag/graph_construction.py`

- **`_add_co_occurrence_relationships()`** (line ~419):
  - Change existence check from `{subject_id, object_id}` to `{subject_id, object_id, predicate: "co_occurs_with"}`
  - Keep bidirectional check for symmetric predicates (optional enhancement)

- **`_add_semantic_similarity_relationships()`** (line ~550+):
  - Change existence check to include `predicate: "similar_to"`
  - Find the exact location of existence check

- **`_add_cross_chunk_relationships()`** (line ~700+):
  - Change existence check to include the specific predicate being created
  - May need to check predicate dynamically based on `_determine_cross_chunk_predicate()`

### 2. Tests

**File**: `tests/business/stages/graphrag/test_graph_construction_existence_checks.py` (new)

- Test: Multiple predicates per pair allowed
  - Create "teaches" relationship between A and B
  - Verify "mentors" relationship can also be created between A and B
  - Both should exist in database

- Test: Same predicate not duplicated
  - Create "co_occurs_with" relationship
  - Try to create same "co_occurs_with" again
  - Should be skipped (not duplicated)

- Test: Co-occurrence existence check includes predicate
  - Mock database query to verify predicate is in query

- Test: Semantic similarity existence check includes predicate
  - Mock database query to verify predicate is in query

- Test: Cross-chunk existence check includes predicate
  - Mock database query to verify predicate is in query

---

## 🔧 Approach

### Step 1: Locate All Existence Checks

1. Find `_add_co_occurrence_relationships()` - line ~419
2. Find `_add_semantic_similarity_relationships()` - search for existence check
3. Find `_add_cross_chunk_relationships()` - search for existence check

### Step 2: Write Tests First (TDD)

1. Create test file
2. Write test for multiple predicates per pair
3. Write test for existence check query structure
4. Run tests (should fail - existence checks missing predicate)

### Step 3: Fix Existence Checks

1. **Co-occurrence** (line ~419-426):
   ```python
   # BEFORE:
   existing = relations_collection.find_one({
       "$or": [
           {"subject_id": entity1_id, "object_id": entity2_id},
           {"subject_id": entity2_id, "object_id": entity1_id},
       ]
   })
   
   # AFTER:
   existing = relations_collection.find_one({
       "subject_id": entity1_id,
       "object_id": entity2_id,
       "predicate": "co_occurs_with"
   })
   # Note: co_occurs_with is symmetric, but we check exact match for now
   ```

2. **Semantic Similarity**:
   - Find existence check location
   - Add `predicate: "similar_to"` to query

3. **Cross-Chunk**:
   - Find existence check location
   - Add dynamic predicate from `_determine_cross_chunk_predicate()`

### Step 4: Verify Tests Pass

1. Run all new tests
2. Verify no regressions in existing tests
3. Check that multiple predicates per pair works

---

## ✅ Expected Results

### Success Criteria

- [ ] Co-occurrence existence check includes `predicate: "co_occurs_with"`
- [ ] Semantic similarity existence check includes `predicate: "similar_to"`
- [ ] Cross-chunk existence check includes dynamic predicate
- [ ] Multiple predicates per pair allowed (test passes)
- [ ] Same predicate not duplicated (test passes)
- [ ] All existing tests still pass
- [ ] No regressions in graph construction behavior

### Validation

- Run test suite
- Manually verify database queries include predicate
- Check that graph can have multiple relationship types between same pair

---

## 📝 Notes

- **Symmetric Predicates**: For now, we check exact match (subject, object, predicate). If predicate is symmetric (e.g., "co_occurs_with"), we could optionally check both directions, but that's a future enhancement.

- **Backward Compatibility**: This change is backward compatible - existing relationships will still be found, but now we can add new predicates between same pairs.

- **Performance**: Adding predicate to query may slightly improve index usage if we have a composite index on (subject_id, object_id, predicate).

---

## 🔗 Related

- **Achievement 0.2**: source_count Inflation Fixed (next)
- **Achievement 1.3**: Unique Indexes (may add composite index on (subject_id, object_id, predicate))

