# SUBPLAN: Stable Community IDs Implementation

**Mother Plan**: PLAN_COMMUNITY-DETECTION-REFACTOR.md  
**Achievement Addressed**: Achievement 0.1 - Stable Community IDs Implemented  
**Status**: ✅ Complete  
**Created**: 2025-11-06 21:30 UTC  
**Estimated Effort**: 2-3 hours

---

## 🎯 Objective

Replace order-dependent, index-based community IDs with hash-based, deterministic IDs. This ensures the same set of entities always gets the same community ID across runs, enabling versioning, caching, diffs, and stable downstream references.

---

## 📋 What Needs to Be Created

### Files to Modify

1. **`business/agents/graphrag/community_detection.py`**:
   - Add `_generate_stable_community_id(level, entity_ids)` method
   - Replace `community_id = f"level_{level}_community_{i}"` with hash-based generation
   - Fix bug: `community_id` undefined in hierarchical_leiden section (line 472)
   - Apply to both Louvain and hierarchical_leiden code paths

### Files to Create

1. **`tests/business/agents/graphrag/test_community_detection_stable_ids.py`**:
   - Test `_generate_stable_community_id()` determinism
   - Test same entity set → same ID
   - Test different entity sets → different IDs
   - Test ID format (level prefix + hash)
   - Test integration with `_organize_communities_by_level()`

---

## 🔧 Approach

### Step 1: Implement Stable ID Generator

- Create `_generate_stable_community_id(level, entity_ids)` method:
  - Sort entity_ids to ensure deterministic order
  - Create signature: `",".join(sorted(entity_ids))`
  - Compute SHA1 hash: `sha1(signature.encode()).hexdigest()[:12]`
  - Format: `f"lvl{level}-{hash}"` (e.g., `lvl1-a3f2b1c4d5e6`)
  - Return deterministic ID

### Step 2: Replace Index-Based IDs in Louvain Path

- In `_organize_communities_by_level()`, Louvain section (line 382):
  - Replace: `community_id = f"level_{level}_community_{i}"`
  - With: `community_id = self._generate_stable_community_id(level, entity_ids)`
  - Remove dependency on enumeration index `i`

### Step 3: Fix Bug in Hierarchical Leiden Path

- In `_organize_communities_by_level()`, hierarchical_leiden section (line 472):
  - Currently: `community_id` is used but never defined (bug!)
  - Fix: Add `community_id = self._generate_stable_community_id(level, entity_ids)`
  - Before line 472 (before `organized[level][community_id]`)

### Step 4: Add Import

- Add `import hashlib` at top of file (if not already present)

### Step 5: Test Determinism

- Write tests to verify:
  - Same graph run twice → same community IDs
  - Different entity sets → different IDs
  - ID format is correct (lvl{level}-{12-char-hash})

---

## 🧪 Tests Required

### Unit Tests

1. **`test_generate_stable_community_id_deterministic`**:

   - Same entity_ids → same ID
   - Different order of same entity_ids → same ID (sorted)
   - Different entity_ids → different ID

2. **`test_generate_stable_community_id_format`**:

   - ID starts with `lvl{level}-`
   - ID has 12-character hash suffix
   - Level is correct in ID

3. **`test_organize_communities_stable_ids_louvain`**:

   - Louvain communities get stable IDs
   - Same graph → same IDs across runs
   - ID format matches expected pattern

4. **`test_organize_communities_stable_ids_hierarchical_leiden`**:

   - Hierarchical Leiden communities get stable IDs
   - Bug fix: community_id is defined (not undefined)
   - Same graph → same IDs across runs

5. **`test_organize_communities_idempotent`**:
   - Run detection twice on same graph
   - All community IDs identical
   - No order-dependent variation

---

## ✅ Expected Results

### Functional Changes

- Community IDs are deterministic (same entities → same ID)
- Community IDs are stable across runs
- ID format: `lvl{level}-{12-char-hash}` (e.g., `lvl1-a3f2b1c4d5e6`)
- Bug fixed: hierarchical_leiden path now defines `community_id`

### Observable Outcomes

- Running detection twice on same graph produces identical community IDs
- Community IDs can be used for versioning, caching, diffs
- Downstream systems can reference communities by stable ID

### Success Indicators

- All tests passing
- No order-dependent ID generation
- ID format consistent and predictable
- Bug in hierarchical_leiden section fixed

---

## 🔗 Dependencies

- None - This is the first achievement in Priority 0
- No external dependencies (hashlib is standard library)

---

## 📝 Execution Task Reference

- **EXECUTION_TASK_COMMUNITY-DETECTION-REFACTOR_01_01.md** - Implementation and testing

---

## 🎯 Notes

- This is a **breaking change** - existing community IDs will change format
- Migration path will be handled in later achievements (run metadata)
- For now, focus on correctness and determinism
- The hash-based approach ensures stability even if detection order changes
