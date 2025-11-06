# SUBPLAN: Stable Entity IDs Implementation

**Mother Plan**: PLAN_ENTITY-RESOLUTION-REFACTOR.md  
**Achievement Addressed**: Achievement 0.3 - Stable Entity IDs Implemented  
**Status**: In Progress  
**Created**: 2025-11-06 21:30 UTC  
**Estimated Effort**: 2-3 hours

---

## 🎯 Objective

Replace the current entity ID generation (which uses only canonical_name) with a deterministic ID that's stable across aliases. This fixes the bug where the same entity gets different IDs if its canonical name varies chunk-to-chunk, causing entity fragmentation.

---

## 📋 What Needs to Be Created

### Files to Modify

1. **`core/models/graphrag.py`**:

   - Modify `ResolvedEntity.generate_entity_id()` to use deterministic method
   - Use normalized name + type for stability
   - Option: UUIDv5 with namespace, or stable MD5 hash

2. **`business/agents/graphrag/entity_resolution.py`**:
   - Ensure entity ID generation uses stable method
   - May need helper method for normalization

### Files to Create/Extend

1. **`tests/core/models/test_graphrag_entity_id.py`** (or extend existing):
   - Test stable ID generation
   - Test same entity gets same ID across aliases
   - Test different entities get different IDs

---

## 🔧 Approach

### Step 1: Implement Stable ID Generation

- Change `generate_entity_id()` to use:
  - Normalized canonical name (lowercase, stripped)
  - Entity type
  - Generate: `md5(normalized_name + "|" + type)`
  - This ensures same entity (same normalized name + type) always gets same ID

### Step 2: Update ID Usage

- Ensure all entity creation uses the stable method
- Verify candidate lookup uses entity_id correctly
- Test that merged entities reuse stable IDs

### Step 3: Handle Migration

- Existing entities may have old IDs
- Candidate lookup already handles this (finds by name, not just ID)
- No migration needed for existing data (backward compatible)

---

## 🧪 Tests Required

### Unit Tests

1. **`test_stable_id_same_entity_different_names`**:

   - "Python" and "Python3" (same type) → may get different IDs (different normalized names)
   - "Python" and "python" (same type) → same ID (normalized same)
   - "Python" (PERSON) and "Python" (TECHNOLOGY) → different IDs (different types)

2. **`test_stable_id_across_aliases`**:

   - If we merge "Jason Ku" and "J. Ku", they should use same stable ID
   - This depends on normalization and merge logic

3. **`test_stable_id_deterministic`**:
   - Same normalized name + type → always same ID
   - Multiple calls → same result

---

## ✅ Expected Results

### Functional Changes

- **Before**: Same entity with different canonical names → different IDs
- **After**: Same entity (normalized name + type) → same ID always

### Observable Outcomes

- Entity ID is stable across chunks
- Entity ID is stable across runs
- Merged entities use consistent IDs
- No more ID drift for same entities

### Success Indicators

- ✅ Same normalized name + type → same entity_id
- ✅ Different types → different entity_ids (even if name same)
- ✅ ID generation is deterministic
- ✅ All tests passing

---

## 🔗 Dependencies

### Prerequisites

- Achievement 0.1 (Cross-Chunk Candidate Lookup) - ✅ COMPLETE
- Achievement 0.2 (Similarity Threshold) - ✅ COMPLETE

### Enables

- Better entity stability across resolution runs
- Prevents entity fragmentation
- Supports future ID-based lookups

---

## 📝 Execution Task Reference

- **EXECUTION_TASK_ENTITY-RESOLUTION-REFACTOR_03_01**: Implementation of stable entity IDs

---

**Status**: ✅ COMPLETE  
**Execution**: EXECUTION_TASK_ENTITY-RESOLUTION-REFACTOR_03_01 - Complete

### Implementation Summary

**Completed**:

- ✅ `generate_entity_id()` enhanced to accept optional `entity_type` parameter
- ✅ ID generation uses `md5(normalized_name + "|" + type)` for stability
- ✅ All entity creation calls updated to pass entity type
- ✅ Backward compatible (works without type parameter)

**Key Features**:

- Deterministic: same normalized name + type → same ID always
- Type-aware: different types get different IDs (prevents collisions)
- Prevents ID drift: stable across chunks and runs
- Normalized: lowercase, stripped whitespace

**Next**: Achievement 0.4 will add LLM gating to reduce unnecessary LLM calls
