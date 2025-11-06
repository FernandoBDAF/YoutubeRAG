# SUBPLAN: Cross-Chunk Candidate Lookup Implementation

**Mother Plan**: PLAN_ENTITY-RESOLUTION-REFACTOR.md  
**Achievement Addressed**: Achievement 0.1 - Cross-Chunk Candidate Lookup Implemented  
**Status**: In Progress  
**Created**: 2025-11-06 20:45 UTC  
**Estimated Effort**: 3-4 hours

---

## 🎯 Objective

Implement cross-chunk candidate lookup in `EntityResolutionStage` to find existing entities in the database before creating new ones. This fixes the critical bug where entities are duplicated across chunks because each chunk is processed independently.

---

## 📋 What Needs to Be Created

### Files to Modify

1. **`business/stages/graphrag/entity_resolution.py`**:
   - Add `_find_db_candidates(name, type, aliases)` method
   - Add `_choose_match(name, candidates)` method (basic version, will be enhanced in Achievement 0.2)
   - Modify `handle_doc()` to lookup candidates before creating entities
   - Integrate with existing `_store_resolved_entities()` flow

### Files to Create

1. **`tests/business/stages/graphrag/test_entity_resolution_stage_candidates.py`**:
   - Test `_find_db_candidates()` with various scenarios
   - Test `_choose_match()` with different candidate sets
   - Test integration with `handle_doc()` flow
   - Test cross-chunk entity reuse

### Dependencies

1. **`requirements.txt`**:
   - Add `rapidfuzz>=3.0.0` for string similarity (needed for Achievement 0.2, but will be used here)

---

## 🔧 Approach

### Step 1: Add Blocking Keys to Agent

- Add `_blocking_keys(name)` method to `EntityResolutionAgent`
- Generate blocking keys: normalized name, alnum-only, acronym
- This will be used in candidate search

### Step 2: Implement Candidate Lookup in Stage

- Implement `_find_db_candidates(name, type, aliases)`:
  - Use blocking keys to query entities collection
  - Query on `canonical_name_normalized` and `aliases_normalized` (will need to add these fields)
  - Return list of candidate entities
  - Handle empty results gracefully

### Step 3: Implement Basic Match Selection

- Implement `_choose_match(name, candidates)`:
  - For now, use exact normalized match (will be enhanced with fuzzy matching in Achievement 0.2)
  - Return best matching candidate or None
  - This will be extended in next achievement

### Step 4: Integrate into Resolution Flow

- Modify `handle_doc()` to:
  - For each entity being resolved, lookup candidates first
  - If match found, reuse existing entity_id
  - If no match, proceed with normal resolution
  - Update entity document with new source information

### Step 5: Handle Normalized Fields

- When storing entities, also store normalized fields:
  - `canonical_name_normalized`: Normalized canonical name
  - `aliases_normalized`: Array of normalized aliases
- This enables efficient candidate lookup

---

## 🧪 Tests Required

### Unit Tests

1. **`test_blocking_keys_generation`**:

   - Test blocking keys for "MIT" → ["mit", "mit", "m"]
   - Test blocking keys for "Prof. John Smith" → normalized, alnum-only, acronym
   - Test blocking keys for "Apple Inc." → normalized (without Inc)

2. **`test_find_db_candidates_with_matches`**:

   - Setup: Insert entity with normalized fields
   - Test: Find candidate using exact normalized name
   - Test: Find candidate using normalized alias
   - Test: Find candidate using blocking key

3. **`test_find_db_candidates_no_matches`**:

   - Test: Query with non-existent entity → empty list
   - Test: Query with different type → empty list (if type filtering)

4. **`test_choose_match_exact_match`**:

   - Test: Exact normalized match → returns candidate
   - Test: No exact match → returns None (fuzzy matching in next achievement)

5. **`test_cross_chunk_entity_reuse`**:
   - Setup: Process chunk 1 with entity "Python"
   - Setup: Process chunk 2 with same entity "Python"
   - Test: Second chunk reuses entity_id from first chunk
   - Test: source_count incremented
   - Test: source_chunks includes both chunks

### Integration Tests

1. **`test_end_to_end_cross_chunk_resolution`**:
   - Create two chunks with overlapping entities
   - Process both chunks through resolution stage
   - Verify: Only one entity created per unique entity
   - Verify: Entity has both chunks as sources

---

## ✅ Expected Results

### Functional Changes

- **Before**: Each chunk creates its own entities independently
- **After**: Entities are looked up across chunks and reused when found

### Observable Outcomes

- Entity count reduced significantly (50-80% reduction)
- Same entity in multiple chunks → single entity with multiple sources
- `source_count` field accurately reflects number of chunks
- `source_chunks` array includes all chunk IDs

### Success Indicators

- ✅ `_find_db_candidates()` finds existing entities
- ✅ `_choose_match()` selects correct candidate
- ✅ Cross-chunk entities reuse same entity_id
- ✅ All tests passing
- ✅ No regression in existing functionality

---

## 🔗 Dependencies

### Prerequisites

- None (this is the first achievement in Priority 0)

### Enables

- Achievement 0.2 (Similarity Threshold) - will enhance `_choose_match()`
- Achievement 0.3 (Stable Entity IDs) - will use candidate lookup
- Achievement 1.1 (Blocking Strategy) - extends blocking keys
- Achievement 2.2 (Normalized Fields) - adds indexes for performance

---

## 📝 Execution Task Reference

- **EXECUTION_TASK_ENTITY-RESOLUTION-REFACTOR_01_01**: Implementation of cross-chunk candidate lookup

---

## 🎯 Next Steps After Completion

1. Update PLAN_ENTITY-RESOLUTION-REFACTOR.md Subplan Tracking
2. Proceed to Achievement 0.2 (Similarity Threshold Applied)
3. Enhance `_choose_match()` with fuzzy matching

---

**Status**: ✅ COMPLETE  
**Execution**: EXECUTION_TASK_ENTITY-RESOLUTION-REFACTOR_01_01 - Complete

### Implementation Summary

**Completed**:

- ✅ `_blocking_keys()` method added to EntityResolutionAgent
- ✅ `_find_db_candidates()` method added to EntityResolutionStage
- ✅ `_choose_match()` method added to EntityResolutionStage (exact match for now)
- ✅ Candidate lookup integrated into `_store_resolved_entities()` flow
- ✅ Normalized fields (`canonical_name_normalized`, `aliases_normalized`) added to entity documents
- ✅ Test suite created: `tests/business/stages/graphrag/test_entity_resolution_stage_candidates.py`
- ✅ RapidFuzz dependency added to requirements.txt

**Key Features**:

- Blocking keys: normalized name, alnum-only, acronym
- Efficient MongoDB queries using normalized fields
- Backward compatible (works with existing entities)
- Cross-chunk entity reuse implemented

**Next**: Achievement 0.2 will enhance `_choose_match()` with fuzzy matching using similarity threshold
