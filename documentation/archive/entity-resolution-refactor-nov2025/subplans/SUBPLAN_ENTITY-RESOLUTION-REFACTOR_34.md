# SUBPLAN: Entity Mention ID Mapping Fix

**Mother Plan**: PLAN_ENTITY-RESOLUTION-REFACTOR.md  
**Achievement Addressed**: Achievement 3.5.1  
**Status**: In Progress  
**Created**: 2025-11-06  
**Estimated Effort**: 1-2 hours

---

## 🎯 Objective

Fix critical bug where entity mentions are saved with wrong entity_id when entities are merged via fuzzy matching. Currently, when `_store_resolved_entities` finds a fuzzy match and reuses an existing entity_id, the original `resolved_entities` list still contains the original entity_id. When `_store_entity_mentions` is called with this list, it creates mentions pointing to non-existent entities (the original entity_id that was never persisted).

**Impact**: 9% of mentions (9,000+ out of 99,353) point to non-existent entities, breaking graph construction and relationships.

---

## 📋 What Needs to Be Created

### Files to Modify

1. **`business/stages/graphrag/entity_resolution.py`**:
   - Modify `_store_resolved_entities()` to return `Dict[str, str]` (id_map: `{original_id → final_id}`)
   - Modify `_store_entity_mentions()` to accept `id_map` parameter and use it
   - Update `handle_doc()` to capture id_map and pass it to `_store_entity_mentions()`

### Functions to Modify

1. **`_store_resolved_entities()`**:

   - Change return type from `List[str]` to `Dict[str, str]`
   - Build id_map as entities are processed
   - Return id_map instead of stored_entity_ids list

2. **`_store_entity_mentions()`**:

   - Add `id_map: Optional[Dict[str, str]] = None` parameter
   - Use `id_map.get(entity.entity_id, entity.entity_id)` to get final_id
   - Use final_id when creating mention documents

3. **`handle_doc()`**:
   - Capture id_map from `_store_resolved_entities()`
   - Pass id_map to `_store_entity_mentions()`

---

## 🔧 Approach

### Step 1: Modify `_store_resolved_entities()` to Build and Return id_map

- Initialize `id_map = {}` at start
- For each entity:
  - Store `original_id = entity.entity_id`
  - After processing (upsert or merge):
    - If merged with existing: `id_map[original_id] = existing_entity_id`
    - If new entity: `id_map[original_id] = original_id` (no change)
  - Return `id_map` instead of `stored_entity_ids`

### Step 2: Modify `_store_entity_mentions()` to Use id_map

- Add `id_map: Optional[Dict[str, str]] = None` parameter
- Default to empty dict if None: `id_map = id_map or {}`
- When creating mention_doc:
  - `final_id = id_map.get(entity.entity_id, entity.entity_id)`
  - Use `final_id` in mention_doc instead of `entity.entity_id`

### Step 3: Update `handle_doc()` to Pass id_map

- Change: `stored_entities = self._store_resolved_entities(...)`
- To: `id_map = self._store_resolved_entities(...)`
- Change: `self._store_entity_mentions(resolved_entities, chunk_id, video_id)`
- To: `self._store_entity_mentions(resolved_entities, chunk_id, video_id, id_map)`

### Step 4: Update Return Value Usage (if needed)

- Check if `stored_entities` (now `id_map`) is used elsewhere
- Update any code that depends on the return value

---

## ✅ Tests Required

### Test File

**File**: `tests/business/stages/graphrag/test_entity_resolution_stage_id_mapping.py`

### Test Cases

1. **Test ID Mapping on Fuzzy Match**:

   - Create entity "Jason Ku" with entity_id_A
   - Create entity "J. Ku" with entity_id_B (fuzzy match)
   - Verify id_map contains `{entity_id_B: entity_id_A}`
   - Verify mentions use entity_id_A (not entity_id_B)

2. **Test ID Mapping on New Entity**:

   - Create new entity (no match)
   - Verify id_map contains `{entity_id: entity_id}` (no change)

3. **Test ID Mapping on Exact Match**:

   - Create entity that matches existing by entity_id
   - Verify id_map contains `{entity_id: entity_id}` (no change)

4. **Test Mentions Use Correct ID**:

   - Create scenario with fuzzy match
   - Verify mention documents use final_id from id_map
   - Verify no mentions point to non-existent entities

5. **Test Backward Compatibility**:
   - Call `_store_entity_mentions` without id_map
   - Verify it still works (uses entity.entity_id directly)

---

## 🎯 Expected Results

### Functional Changes

- `_store_resolved_entities()` returns `Dict[str, str]` mapping original_id → final_id
- `_store_entity_mentions()` uses id_map to get correct entity_id for mentions
- All mentions reference existing entities (0% orphaned mentions)

### Observable Outcomes

- Database validation shows 0 orphaned mentions
- Graph construction can find all entities referenced in mentions
- Relationships are correctly established

### Success Indicators

- ✅ All test cases pass
- ✅ Database integrity check: 0 orphaned mentions
- ✅ Graph construction stage works without errors
- ✅ No regression in existing functionality

---

## 🔗 Dependencies

- None (this is a bug fix, not dependent on other achievements)
- Uses existing fuzzy matching infrastructure (Achievement 0.2)
- Uses existing candidate lookup (Achievement 0.1)

---

## 📝 Execution Task Reference

- **EXECUTION_TASK_ENTITY-RESOLUTION-REFACTOR_34_01.md** - Implementation log

---

## 🔍 Key Implementation Details

### id_map Structure

```python
id_map = {
    "original_entity_id_1": "final_entity_id_1",  # Merged with existing
    "original_entity_id_2": "original_entity_id_2",  # New entity (no change)
    "original_entity_id_3": "existing_entity_id",  # Fuzzy matched
}
```

### Backward Compatibility

- `_store_entity_mentions()` should handle `id_map=None` gracefully
- Default to using `entity.entity_id` if id_map not provided
- This ensures existing code doesn't break

### Edge Cases

- Empty id_map: Should work (all entities use their own entity_id)
- Missing key in id_map: Use entity.entity_id as fallback
- Multiple entities merged to same final_id: All should map correctly

---

**Status**: ✅ Complete  
**Completed**: 2025-11-06

---

## ✅ Implementation Summary

**Code Changes**:

- Modified `_store_resolved_entities()` to return `Dict[str, str]` (id_map)
- Modified `_store_entity_mentions()` to accept and use `id_map` parameter
- Updated `handle_doc()` to capture and pass id_map
- Updated resolution payload to use `len(id_map)`

**Tests**:

- Created `test_entity_resolution_stage_id_mapping.py` with 4 test cases
- All tests passing: id_map on fuzzy match, new entity, mentions use correct ID, backward compatibility

**Next**: Production validation to confirm 0% orphaned mentions
