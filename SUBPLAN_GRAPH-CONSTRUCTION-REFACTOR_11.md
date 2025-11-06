# SUBPLAN: Density Computation Formula Corrected

**Parent Plan**: PLAN_GRAPH-CONSTRUCTION-REFACTOR.md  
**Achievement**: 1.1  
**Priority**: HIGH  
**Status**: ✅ COMPLETE  
**Created**: 2025-11-06

---

## 🎯 Objective

Fix density computation to match graph semantics. Current formula uses undirected graph denominator, but graph has directed relationships and multiple predicates per pair.

**Current Problem**:
- Uses undirected graph formula: `max_possible = n*(n-1)/2`
- But graph has directed relationships, multiple predicates per pair
- Density check inconsistent with graph semantics

**Target State**:
- Count unique unordered pairs (subject_id, object_id) actually in DB
- Use actual pair count as numerator, not total relationship count
- Denominator: `n*(n-1)/2` (undirected pairs) - this is correct
- Density = unique_pairs / max_possible_pairs

---

## 📋 What Needs to Be Created

### 1. Modified Method

**File**: `business/stages/graphrag/graph_construction.py`

- **`_calculate_current_graph_density()`** (line ~966):
  - Count unique unordered pairs (subject_id, object_id) in DB
  - Use aggregation to get distinct pairs
  - Keep denominator as `n*(n-1)/2` (correct for undirected pairs)
  - Document formula choice and rationale

### 2. Tests

**File**: `tests/business/stages/graphrag/test_graph_construction_density.py` (new)

- Test: Density with multiple predicates per pair (should count as 1 pair)
- Test: Density with directed relationships (should count unordered pairs)
- Test: Density formula matches graph semantics
- Test: Density calculation handles edge cases (0 entities, 1 entity)

---

## 🔧 Approach

### Step 1: Write Tests First (TDD)

1. Create test file
2. Write tests for density calculation
3. Run tests (should fail - uses total relationships, not unique pairs)

### Step 2: Fix _calculate_current_graph_density

1. Use MongoDB aggregation to count unique unordered pairs
2. Query: `$group` by normalized pair (min(subject_id, object_id), max(subject_id, object_id))
3. Count distinct pairs, not total relationships
4. Keep denominator as `n*(n-1)/2`

### Step 3: Document Formula

1. Add docstring explaining formula choice
2. Explain why we count unique pairs, not total relationships

### Step 4: Run Tests

1. All new tests passing
2. No regressions in existing tests

---

## ✅ Expected Results

### Success Criteria

- [ ] Density counts unique pairs, not total relationships
- [ ] Multiple predicates per pair count as 1 pair
- [ ] Directed relationships handled correctly (unordered pairs)
- [ ] Formula documented with rationale
- [ ] All tests passing
- [ ] No regressions

### Validation

- Run test suite
- Manually verify: 2 relationships between same pair → density counts as 1 pair

---

## 📝 Notes

- **Formula Choice**: We use unique unordered pairs because:
  - Graph can have multiple predicates per pair (e.g., "teaches" and "mentors")
  - We want to measure connectivity, not relationship count
  - Undirected denominator `n*(n-1)/2` is correct for pair-based density

- **Performance**: Aggregation query is efficient with proper indexes

---

## 🔗 Related

- **Achievement 0.1**: Relationship Existence Checks (allows multiple predicates)
- **Achievement 1.2**: Reverse Mapping Collision Handling (next)

