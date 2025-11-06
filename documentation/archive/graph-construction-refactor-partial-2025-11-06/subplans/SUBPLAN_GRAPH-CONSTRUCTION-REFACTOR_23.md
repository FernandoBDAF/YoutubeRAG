# SUBPLAN: Synthetic Edge Caps Per Entity

**Parent Plan**: PLAN_GRAPH-CONSTRUCTION-REFACTOR.md  
**Achievement**: 2.3  
**Priority**: HIGH  
**Status**: ✅ COMPLETE  
**Created**: 2025-11-06

---

## 🎯 Objective

Add degree caps to prevent high-degree entities from exploding synthetic edges, controlling graph growth.

**Current Problem**:
- No limits on synthetic edges per entity
- High-degree entities can create thousands of synthetic edges
- Graph can become over-connected

**Target State**:
- Environment variables: `GRAPHRAG_MAX_COOC_PER_ENTITY`, `GRAPHRAG_MAX_SIM_PER_ENTITY`
- Skip adding edge if entity degree exceeds cap
- Log skipped edges for monitoring
- Controlled synthetic edge growth

---

## 📋 What Needs to Be Created

### 1. Modified Methods

**File**: `business/stages/graphrag/graph_construction.py`

- **`_add_co_occurrence_relationships()`** (line ~378):
  - Check entity degree before adding edge
  - Skip if degree >= `GRAPHRAG_MAX_COOC_PER_ENTITY`
  - Track skipped edges

- **`_add_semantic_similarity_relationships()`** (line ~504):
  - Check entity degree before adding edge
  - Skip if degree >= `GRAPHRAG_MAX_SIM_PER_ENTITY`
  - Track skipped edges

- **`_add_cross_chunk_relationships()`** (line ~615):
  - Optional: Add cap for cross-chunk edges
  - Or: Use same cap as co-occurrence

### 2. Helper Method

- **`_get_entity_degree()`**:
  - Count relationships where entity is subject or object
  - Cache results for performance

### 3. Tests

**File**: `tests/business/stages/graphrag/test_graph_construction_edge_caps.py` (new)

- Test: Edge cap enforced for co-occurrence
- Test: Edge cap enforced for semantic similarity
- Test: Skipped edges logged
- Test: High-degree entities don't explode

---

## 🔧 Approach

### Step 1: Write Tests First (TDD)

1. Create test file
2. Write tests for edge caps
3. Run tests (should fail - no caps)

### Step 2: Add Helper Method

1. Create `_get_entity_degree()` to count relationships
2. Cache results for performance

### Step 3: Add Caps to Methods

1. Read environment variables
2. Check degree before adding edge
3. Skip if cap exceeded
4. Log skipped edges

### Step 4: Run Tests

1. All new tests passing
2. No regressions in existing tests

---

## ✅ Expected Results

### Success Criteria

- [ ] Edge caps enforced for co-occurrence
- [ ] Edge caps enforced for semantic similarity
- [ ] Skipped edges logged
- [ ] High-degree entities don't explode
- [ ] All tests passing
- [ ] No regressions

### Validation

- Run test suite
- Manually verify: high-degree entity → edges capped

---

## 📝 Notes

- **Performance**: Degree counting can be expensive - cache results
- **Config**: Environment variables with sensible defaults (e.g., 200)
- **Logging**: Track skipped edges for monitoring

---

## 🔗 Related

- **Achievement 2.1**: ANN Index (independent)
- **Achievement 2.2**: Cosine Optimization (just completed)

