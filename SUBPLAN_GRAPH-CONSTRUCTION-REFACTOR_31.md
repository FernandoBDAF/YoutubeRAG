# SUBPLAN: Use Existing Ontology Infrastructure

**Parent Plan**: PLAN_GRAPH-CONSTRUCTION-REFACTOR.md  
**Achievement**: 3.1  
**Priority**: MEDIUM  
**Status**: ✅ COMPLETE  
**Created**: 2025-11-06

---

## 🎯 Objective

Remove hard-coded reverse predicate mappings and use existing ontology infrastructure instead.

**Current Problem**:
- Graph construction hard-codes `reverse_predicates` dictionary (lines 986-1005)
- Duplicates extraction's ontology logic
- No single source of truth for predicate metadata

**Target State**:
- Load ontology using existing `load_ontology()` from `core.libraries.ontology`
- Use `symmetric_predicates` for bidirectional relationships
- Build reverse mapping from predicate_map or derive from canonical predicates
- Remove hard-coded `reverse_predicates` dictionary
- Single source of truth for predicate metadata

---

## 📋 What Needs to Be Created

### 1. Modified Methods

**File**: `business/stages/graphrag/graph_construction.py`

- **`setup()`** (line ~40):
  - Load ontology using `load_ontology()`
  - Store in `self.ontology`

- **`_add_bidirectional_relationships()`** (line ~970):
  - Remove hard-coded `reverse_predicates` dictionary
  - Use ontology data to determine reverse predicates
  - Handle symmetric predicates (skip bidirectional creation)
  - Build reverse mapping from predicate_map or derive from patterns

### 2. Helper Method

- **`_get_reverse_predicate(predicate: str) -> Optional[str]`**:
  - Check if predicate is symmetric (skip if so)
  - Look up reverse in predicate_map or derive from patterns
  - Return reverse predicate or None

### 3. Tests

**File**: `tests/business/stages/graphrag/test_graph_construction_ontology.py` (new)

- Test: Bidirectional relationships use ontology data
- Test: Symmetric predicates skip bidirectional creation
- Test: Reverse predicates derived from ontology
- Test: Fallback behavior when ontology not available

---

## 🔧 Approach

### Step 1: Load Ontology in setup()

1. Import `load_ontology` from `core.libraries.ontology`
2. Call `load_ontology()` in `setup()`
3. Store result in `self.ontology`

### Step 2: Create Helper Method

1. Create `_get_reverse_predicate()` method
2. Check `symmetric_predicates` first (return None if symmetric)
3. Build reverse mapping from predicate_map or derive from patterns
4. Return reverse predicate or None

### Step 3: Update _add_bidirectional_relationships

1. Remove hard-coded `reverse_predicates` dictionary
2. Use `_get_reverse_predicate()` for each relationship
3. Skip if predicate is symmetric or no reverse found

### Step 4: Write Tests

1. Create test file
2. Test with mock ontology data
3. Test symmetric predicates
4. Test fallback behavior

### Step 5: Run Tests

1. All new tests passing
2. No regressions in existing tests

---

## ✅ Expected Results

### Success Criteria

- [ ] Ontology loaded in setup()
- [ ] Hard-coded reverse_predicates removed
- [ ] Bidirectional relationships use ontology data
- [ ] Symmetric predicates handled correctly
- [ ] Single source of truth for predicate metadata
- [ ] All tests passing
- [ ] No regressions

### Validation

- Run test suite
- Manually verify: bidirectional relationships still work

---

## 📝 Notes

- **Reverse Mapping**: The ontology may not have explicit reverse mappings. We may need to:
  - Derive from predicate_map (if it contains reverse pairs)
  - Use naming patterns (e.g., "uses" → "used_by")
  - Fall back to hard-coded mapping if ontology doesn't have reverse info

- **Symmetric Predicates**: If a predicate is symmetric, we should skip creating a reverse (it's already bidirectional)

- **Backward Compatibility**: If ontology loading fails, we should have a fallback

---

## 🔗 Related

- **Achievement 3.2**: Edge Attribution (next)
- **Achievement 3.3**: Comprehensive Metrics (next)

