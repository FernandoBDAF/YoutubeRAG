# SUBPLAN: Multi-Strategy Fuzzy Matching

**Mother Plan**: PLAN_ENTITY-RESOLUTION-REFACTOR.md  
**Achievement Addressed**: Achievement 1.2 - Fuzzy Matching Algorithm Implemented  
**Status**: In Progress  
**Created**: 2025-11-06 22:10 UTC  
**Estimated Effort**: 3-4 hours

---

## 🎯 Objective

Implement multi-strategy scoring for fuzzy matching that combines:

- String similarity (RapidFuzz - already implemented)
- Token overlap (Jaccard on stemmed/tokenized words)
- Optional: Embedding cosine similarity (future enhancement)

Combine scores with weighted average and apply threshold to final score for better matching accuracy.

---

## 📋 What Needs to Be Created

### Files to Modify

1. **`business/agents/graphrag/entity_resolution.py`**:

   - Add `_token_score()` for token overlap (Jaccard)
   - Add `_multi_strategy_score()` to combine strategies
   - Update scoring to use multi-strategy approach
   - Make embedding scoring optional (stub for future)

2. **`business/stages/graphrag/entity_resolution.py`**:
   - Update `_choose_match()` to use multi-strategy scoring

---

## 🔧 Approach

### Step 1: Token Overlap Scoring

- Implement `_token_score(a, b)` using Jaccard similarity
- Tokenize both names into word sets
- Calculate Jaccard: intersection / union
- Return score 0.0 to 1.0

### Step 2: Multi-Strategy Combination

- Implement `_multi_strategy_score(a, b)`:
  - String similarity: 0.5 weight (RapidFuzz)
  - Token overlap: 0.3 weight (Jaccard)
  - Embedding: 0.2 weight (optional, stub for now)
  - Combine: `final = 0.5*string + 0.3*token + 0.2*embedding`
  - If embedding unavailable: `final = 0.6*string + 0.4*token` (normalized)

### Step 3: Update Match Selection

- Update `_choose_match()` to use multi-strategy scoring
- Use `_multi_strategy_score()` instead of just `_string_score()`
- Apply threshold to final combined score

---

## 🧪 Tests Required

1. **`test_token_score`**: Test Jaccard similarity on tokenized names
2. **`test_multi_strategy_score`**: Test weighted combination
3. **`test_multi_strategy_matching`**: Test end-to-end matching

---

## ✅ Expected Results

- More accurate fuzzy matching
- Better handling of word order variations
- Configurable weights for different strategies
- Ready for embedding enhancement

---

**Status**: Ready to Execute  
**Next**: Implement token scoring and multi-strategy combination
