# SUBPLAN: Cosine Similarity Optimization

**Parent Plan**: PLAN_GRAPH-CONSTRUCTION-REFACTOR.md  
**Achievement**: 2.2  
**Priority**: HIGH  
**Status**: ✅ COMPLETE  
**Created**: 2025-11-06

---

## 🎯 Objective

Optimize cosine similarity computation by normalizing embeddings once at write time and using dot product directly.

**Current Problem**:
- Cosine similarity computed as: `np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))`
- Norms computed on every similarity calculation (expensive)
- No normalization flag stored

**Target State**:
- Normalize embeddings once when stored
- Store `entity_embedding_norm = 1.0` flag
- Use dot product directly: `np.dot(emb1, emb2)` (embeddings already normalized)
- 2-3× faster similarity computation

---

## 📋 What Needs to Be Created

### 1. Modified Methods

**File**: `business/stages/graphrag/graph_construction.py`

- **`_add_semantic_similarity_relationships()`** (line ~504):
  - Normalize embeddings when generating (if not already normalized)
  - Store `entity_embedding_norm = 1.0` flag
  - Use dot product directly: `similarity = np.dot(emb1, emb2)`
  - Check normalization flag before computing similarity

### 2. Tests

**File**: `tests/business/stages/graphrag/test_graph_construction_cosine_optimization.py` (new)

- Test: Normalized embeddings use dot product
- Test: Results match current cosine similarity
- Test: Normalization flag stored correctly
- Test: Non-normalized embeddings still work (backward compatibility)

---

## 🔧 Approach

### Step 1: Write Tests First (TDD)

1. Create test file
2. Write tests for normalization and dot product
3. Run tests (should fail - uses norm computation)

### Step 2: Normalize Embeddings at Write Time

1. When generating embeddings, normalize them
2. Store `entity_embedding_norm = 1.0` flag
3. Update existing embeddings (optional, can be done lazily)

### Step 3: Use Dot Product for Normalized Embeddings

1. Check if embeddings are normalized (flag or check norm)
2. If normalized, use `np.dot(emb1, emb2)`
3. If not normalized, use current formula (backward compatibility)

### Step 4: Run Tests

1. All new tests passing
2. No regressions in existing tests

---

## ✅ Expected Results

### Success Criteria

- [ ] Embeddings normalized at write time
- [ ] Normalization flag stored
- [ ] Dot product used for normalized embeddings
- [ ] Results match current cosine similarity
- [ ] 2-3× faster similarity computation
- [ ] All tests passing
- [ ] No regressions

### Validation

- Run test suite
- Benchmark: Compare performance before/after

---

## 📝 Notes

- **Backward Compatibility**: Non-normalized embeddings still work (fallback to current formula)
- **Lazy Normalization**: Can normalize existing embeddings on first use
- **Performance**: 2-3× speedup from avoiding norm computation

---

## 🔗 Related

- **Achievement 2.1**: ANN Index (will benefit from this optimization)
- **Achievement 2.3**: Synthetic Edge Caps (independent)

