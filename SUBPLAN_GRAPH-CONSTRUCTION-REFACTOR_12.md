# SUBPLAN: Reverse Mapping Collision Handling

**Parent Plan**: PLAN_GRAPH-CONSTRUCTION-REFACTOR.md  
**Achievement**: 1.2  
**Priority**: HIGH  
**Status**: 🔄 IN PROGRESS  
**Created**: 2025-11-06

---

## 🎯 Objective

Fix reverse mapping to handle existing reverse relationships by merging fields instead of skipping or duplicating.

**Current Problem**:
- `_add_bidirectional_relationships` creates reverse without checking if reverse already exists
- If reverse exists with different description/confidence, creates divergent twin edges
- No merge logic for existing reverse relationships

**Target State**:
- Before creating reverse, check if it already exists
- If exists, merge fields (max confidence, union source_chunks, longest description)
- Use atomic upsert pattern (like entity resolution)
- No duplicate reverse relationships

---

## 📋 What Needs to Be Created

### 1. Modified Method

**File**: `business/stages/graphrag/graph_construction.py`

- **`_add_bidirectional_relationships()`** (line ~855):
  - Check if reverse relationship exists by relationship_id
  - If exists, use atomic upsert to merge fields
  - Merge policy: max confidence, union source_chunks, longest description
  - If not exists, create new reverse relationship

### 2. Tests

**File**: `tests/business/stages/graphrag/test_graph_construction_reverse_collision.py` (new)

- Test: Reverse already exists → merge, don't duplicate
- Test: Merge policy: max confidence, union source_chunks, longest description
- Test: Reverse doesn't exist → create new
- Test: No duplicate reverse relationships

---

## 🔧 Approach

### Step 1: Write Tests First (TDD)

1. Create test file
2. Write tests for reverse collision handling
3. Run tests (should fail - creates duplicates)

### Step 2: Fix _add_bidirectional_relationships

1. Check if reverse relationship exists by relationship_id
2. If exists, use `find_one_and_update` with merge policy
3. If not exists, create new reverse relationship
4. Use atomic upsert pattern

### Step 3: Run Tests

1. All new tests passing
2. No regressions in existing tests

---

## ✅ Expected Results

### Success Criteria

- [ ] Reverse already exists → merge, don't duplicate
- [ ] Merge policy: max confidence, union source_chunks, longest description
- [ ] No duplicate reverse relationships
- [ ] All tests passing
- [ ] No regressions

### Validation

- Run test suite
- Manually verify: reverse exists → merged, not duplicated

---

## 📝 Notes

- **Pattern Reuse**: Same atomic upsert pattern as entity resolution
- **Merge Policy**: Conservative - keep best of both (max confidence, longest description)
- **Performance**: Atomic upsert is efficient

---

## 🔗 Related

- **Achievement 1.1**: Density Computation (just completed)
- **Achievement 1.3**: Unique Indexes (next)

