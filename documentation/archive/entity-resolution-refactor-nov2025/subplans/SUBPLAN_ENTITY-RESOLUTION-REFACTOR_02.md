# SUBPLAN: Similarity Threshold Applied (Fuzzy Matching)

**Mother Plan**: PLAN_ENTITY-RESOLUTION-REFACTOR.md  
**Achievement Addressed**: Achievement 0.2 - Similarity Threshold Applied  
**Status**: In Progress  
**Created**: 2025-11-06 21:20 UTC  
**Estimated Effort**: 2-3 hours

---

## 🎯 Objective

Implement fuzzy string matching using RapidFuzz and apply the similarity threshold to enable near-duplicate entity merging. This fixes the critical bug where `similarity_threshold` parameter exists but is never used, allowing entities like "Jason Ku" and "J. Ku" to be merged.

---

## 📋 What Needs to Be Created

### Files to Modify

1. **`business/agents/graphrag/entity_resolution.py`**:

   - Add `_string_score(a, b)` method using RapidFuzz
   - Use WRatio or token_sort_ratio for best results
   - Return score between 0.0 and 1.0

2. **`business/stages/graphrag/entity_resolution.py`**:
   - Enhance `_choose_match()` to use fuzzy matching
   - Apply `similarity_threshold` to filter matches
   - Return best matching candidate above threshold

### Files to Create/Extend

1. **`tests/business/stages/graphrag/test_entity_resolution_stage_candidates.py`**:
   - Add tests for fuzzy matching
   - Test threshold application
   - Test near-duplicate merging

---

## 🔧 Approach

### Step 1: Implement String Similarity Scoring

- Add `_string_score(a, b)` to EntityResolutionAgent
- Use RapidFuzz's `fuzz.WRatio()` for best results
- Handle edge cases: empty strings, very different strings
- Return normalized score (0.0 to 1.0)

### Step 2: Enhance Match Selection

- Update `_choose_match()` to score all candidates
- Find best match above threshold
- Return None if no candidate meets threshold
- Log matches for debugging

### Step 3: Test with Real Examples

- Test: "Jason Ku" vs "J. Ku" → should merge if score >= 0.85
- Test: "Python" vs "Java" → should not merge (score < 0.85)
- Test: "Apple Inc." vs "Apple" → should merge (high similarity)
- Test: Threshold boundary cases (0.84 vs 0.85)

---

## 🧪 Tests Required

### Unit Tests

1. **`test_string_score_similar_names`**:

   - "Jason Ku" vs "J. Ku" → high score (>0.8)
   - "Python" vs "Python3" → high score (>0.8)
   - "Apple Inc." vs "Apple" → high score (>0.8)

2. **`test_string_score_different_names`**:

   - "Python" vs "Java" → low score (<0.5)
   - "John Smith" vs "Jane Doe" → low score (<0.5)

3. **`test_choose_match_with_fuzzy_matching`**:

   - Multiple candidates, best match above threshold → returns best
   - Multiple candidates, none above threshold → returns None
   - Single candidate above threshold → returns candidate
   - Single candidate below threshold → returns None

4. **`test_threshold_boundary`**:
   - Score 0.84 with threshold 0.85 → no match
   - Score 0.85 with threshold 0.85 → match
   - Score 0.86 with threshold 0.85 → match

---

## ✅ Expected Results

### Functional Changes

- **Before**: Only exact normalized matches merged
- **After**: Near-duplicate matches merged if similarity >= threshold

### Observable Outcomes

- "Jason Ku" and "J. Ku" merge into single entity
- "Apple Inc." and "Apple" merge into single entity
- "Python" and "Java" remain separate (low similarity)
- Threshold actively controls merge behavior

### Success Indicators

- ✅ `_string_score()` returns accurate similarity scores
- ✅ `_choose_match()` applies threshold correctly
- ✅ Near-duplicates merge when similarity >= threshold
- ✅ Different entities remain separate when similarity < threshold
- ✅ All tests passing

---

## 🔗 Dependencies

### Prerequisites

- Achievement 0.1 (Cross-Chunk Candidate Lookup) - ✅ COMPLETE
- RapidFuzz dependency added to requirements.txt - ✅ COMPLETE

### Enables

- Achievement 1.2 (Fuzzy Matching Algorithm) - will extend this with multi-strategy scoring
- Achievement 2.1 (Atomic Upsert) - will use fuzzy matching results

---

## 📝 Execution Task Reference

- **EXECUTION_TASK_ENTITY-RESOLUTION-REFACTOR_02_01**: Implementation of fuzzy matching with similarity threshold

---

**Status**: Ready to Execute  
**Next**: Create EXECUTION_TASK and begin implementation
