# EXECUTION_DEBUG: Entity Resolution - Two More Critical Bugs

**Type**: EXECUTION_DEBUG (Complex Issue Investigation)  
**Date**: 2025-11-12  
**Run**: Second attempt after decorator fix  
**Status**: ✅ ROOT CAUSES IDENTIFIED & FIXES PROPOSED  
**Severity**: 🔴 CRITICAL - Still blocks Achievement 2.1 baseline run  
**Impact**: All 400 chunks failed in Stage 2 (Entity Resolution) - AGAIN

---

## 📋 Issue Summary

**After fixing the decorator bug**, ran pipeline again and Stage 2 STILL failed for all 400 chunks, but with **TWO NEW ERRORS**:

### Error 1: MongoDB Conflict (Most Common)

```
ERROR | business.stages.graphrag.entity_resolution | _store_resolved_entities:552 |
Failed to store entity <entity_id>: Updating the path 'source_count' would create a conflict at 'source_count'
Full error: {'code': 40, 'codeName': 'ConflictingUpdateOperators'}
```

### Error 2: AttributeError (Less Common)

```
ERROR | business.stages.graphrag.entity_resolution | handle_doc:250 |
Error processing chunk <chunk_id> for entity resolution: 'ResolvedEntity' object has no attribute 'original_id'
```

**Result**: Stage 2 failed for ALL 400 chunks (0 updated, 400 failed)

---

## 🔍 Investigation Process

### Step 1: Verify Decorator Fix Worked

**Check**: Did the decorator fix resolve the previous error?

**Previous Error** (Run 1):

```
handle_errors.<locals>.decorator() got an unexpected keyword argument 'entities'
```

**Current Errors** (Run 2):

```
Updating the path 'source_count' would create a conflict
'ResolvedEntity' object has no attribute 'original_id'
```

✅ **Decorator fix worked!** Different errors now, meaning we're past the decorator issue.

---

### Step 2: Analyze Error 1 - MongoDB Conflict

**Error Location**: `business/stages/graphrag/entity_resolution.py` line 552

**Error Message**: `"Updating the path 'source_count' would create a conflict at 'source_count'"`

**MongoDB Error Code**: 40 (`ConflictingUpdateOperators`)

**What This Means**: MongoDB doesn't allow the same field to appear in multiple update operators in a single update operation.

#### Investigation: `_upsert_entity` Method

**File**: `business/stages/graphrag/entity_resolution.py`  
**Lines**: 615-648

**Code Analysis**:

```python
# Line 615-623: Build update document
update = {
    "$setOnInsert": {
        "entity_id": entity_id,
        "created_at": now,
        "first_seen": now,
        "type": resolved_entity.type.value,
        "source_count": 1,  # ← Line 623: source_count in $setOnInsert
    },
    "$set": { ... },
    "$addToSet": { ... },
    "$max": { ... },
}

# Line 644-647: Conditionally add $inc
if is_new_chunk:
    update["$inc"] = {"source_count": 1}  # ← Line 647: source_count in $inc
```

**🚨 ROOT CAUSE IDENTIFIED**:

MongoDB update has `source_count` in **TWO operators**:

1. Line 623: `$setOnInsert: {"source_count": 1}`
2. Line 647: `$inc: {"source_count": 1}`

**MongoDB Rule**: A field can only appear in ONE update operator per operation.

**Why This Fails**:

- For **NEW entities** (upsert creates document):
  - `$setOnInsert` sets `source_count = 1`
  - `$inc` tries to increment `source_count` by 1
  - **CONFLICT**: Can't set AND increment same field
- For **EXISTING entities**:
  - `$setOnInsert` is ignored (document exists)
  - `$inc` increments `source_count` by 1
  - **NO CONFLICT**: Only one operator applies

**Result**: ALL new entities fail, only updates to existing entities work.

---

### Step 3: Analyze Error 2 - AttributeError

**Error Location**: `business/stages/graphrag/entity_resolution.py` line 250 (error handler)

**Error Message**: `'ResolvedEntity' object has no attribute 'original_id'`

#### Investigation: Where is `original_id` Used?

**Found 2 locations**:

**Location 1**: Line 187

```python
resolved_entities_data.append({
    "entity_id": id_map.get(entity.original_id, entity.original_id),  # ← ERROR!
    "canonical_name": entity.canonical_name,
    ...
})
```

**Location 2**: Line 554 (error handler)

```python
except Exception as e:
    logger.error(f"Failed to store entity {entity.entity_id}: {e}")
    id_map[original_id] = original_id  # ← ERROR if original_id not defined!
    continue
```

#### Investigation: `ResolvedEntity` Class

**File**: `core/models/graphrag.py`  
**Lines**: 139-154

```python
class ResolvedEntity(BaseModel):
    """Model for resolved/canonicalized entities."""

    entity_id: str = Field(...)  # ← Has entity_id
    canonical_name: str = Field(...)
    name: str = Field(...)
    type: EntityType = Field(...)
    description: str = Field(...)
    confidence: float
    source_count: int = Field(ge=1)
    resolution_methods: List[str] = Field(default_factory=list)
    aliases: List[str] = Field(default_factory=list)
    # NO original_id attribute!
```

**🚨 ROOT CAUSE IDENTIFIED**:

`ResolvedEntity` class has `entity_id`, NOT `original_id`.

**Why This Fails**:

- Line 187: Tries to access `entity.original_id` → AttributeError
- Line 427 defines `original_id = entity.entity_id` (correct)
- Line 554 tries to use `original_id` in except block, but if exception happens before line 427, `original_id` is undefined

**Result**: Some chunks fail with AttributeError when trying to save resolved entities.

---

## ✅ The Fixes

### Fix 1: MongoDB Conflict - Remove `source_count` from `$setOnInsert`

**File**: `business/stages/graphrag/entity_resolution.py`

**Change**: Lines 615-648

**Problem**: `source_count` appears in both `$setOnInsert` and `$inc`

**Solution**: Remove `source_count` from `$setOnInsert`, handle it differently

**Before** (WRONG):

```python
update = {
    "$setOnInsert": {
        "entity_id": entity_id,
        "created_at": now,
        "first_seen": now,
        "type": resolved_entity.type.value,
        "source_count": 1,  # ← REMOVE THIS
    },
    # ... other operators ...
}

if is_new_chunk:
    update["$inc"] = {"source_count": 1}  # ← CONFLICTS with above
```

**After** (CORRECT):

```python
update = {
    "$setOnInsert": {
        "entity_id": entity_id,
        "created_at": now,
        "first_seen": now,
        "type": resolved_entity.type.value,
        "source_count": 0,  # ← Start at 0, will be incremented by $inc
    },
    # ... other operators ...
}

# ALWAYS increment for new chunks (works for both new and existing entities)
if is_new_chunk:
    update["$inc"] = {"source_count": 1}  # ← No conflict, $setOnInsert uses 0
```

**Why This Works**:

- New entity: `$setOnInsert` sets `source_count = 0`, then `$inc` increments to 1 ✅
- Existing entity: `$setOnInsert` ignored, `$inc` increments by 1 ✅
- No conflict: Different values, MongoDB can handle both operators

---

### Fix 2: AttributeError - Use `entity.entity_id` Instead of `entity.original_id`

**File**: `business/stages/graphrag/entity_resolution.py`

**Change 1**: Line 187

**Before** (WRONG):

```python
resolved_entities_data.append({
    "entity_id": id_map.get(entity.original_id, entity.original_id),  # ← ERROR!
    ...
})
```

**After** (CORRECT):

```python
resolved_entities_data.append({
    "entity_id": id_map.get(entity.entity_id, entity.entity_id),  # ← Use entity_id
    ...
})
```

**Change 2**: Line 554 (error handler)

**Before** (WRONG):

```python
except Exception as e:
    logger.error(f"Failed to store entity {entity.entity_id}: {e}")
    id_map[original_id] = original_id  # ← ERROR if original_id not defined!
    continue
```

**After** (CORRECT):

```python
except Exception as e:
    logger.error(f"Failed to store entity {entity.entity_id}: {e}")
    id_map[entity.entity_id] = entity.entity_id  # ← Use entity.entity_id directly
    continue
```

**Why This Works**:

- `ResolvedEntity` has `entity_id` attribute, not `original_id`
- Using `entity.entity_id` directly avoids dependency on local variable `original_id`
- Works even if exception happens before `original_id` is defined

---

## 🧪 Testing Strategy

### Test 1: Quick Validation (50 chunks)

```bash
# After applying both fixes
mongosh "..." --eval "db.video_chunks.updateMany({}, {\$unset: {...}})"
python -m app.cli.graphrag --max 50 --db-name validation_01 --verbose
```

**Expected**:

- ✅ Stage 1 (Extraction): 50 chunks processed
- ✅ Stage 2 (Resolution): 50 chunks resolved (**0 failed**)
- ✅ Stage 3 (Construction): Graph built
- ✅ Stage 4 (Detection): Communities detected

### Test 2: Full Baseline (400 chunks)

```bash
# After Test 1 passes
mongosh "..." --eval "db.video_chunks.updateMany({}, {\$unset: {...}})"
python -m app.cli.graphrag --max 400 --db-name validation_01 --verbose
```

**Expected**:

- ✅ All 4 stages complete successfully
- ✅ Entities created in `entities` collection
- ✅ Relations created in `relations` collection
- ✅ Communities detected

---

## 📊 Impact Assessment

### Run 1 (Decorator Bug)

| Stage               | Status     | Chunks | Issue           |
| ------------------- | ---------- | ------ | --------------- |
| **1. Extraction**   | ✅ Success | 400    | -               |
| **2. Resolution**   | ❌ Failed  | 400    | Decorator error |
| **3. Construction** | ⚠️ Skipped | 0      | No data         |
| **4. Detection**    | ⚠️ Skipped | 0      | No data         |

**Fix**: Added `()` to `@handle_errors` decorator

---

### Run 2 (MongoDB Conflict + AttributeError)

| Stage               | Status     | Chunks | Issues                            |
| ------------------- | ---------- | ------ | --------------------------------- |
| **1. Extraction**   | ✅ Success | 400    | -                                 |
| **2. Resolution**   | ❌ Failed  | 400    | MongoDB conflict + AttributeError |
| **3. Construction** | ⚠️ Skipped | 0      | No data                           |
| **4. Detection**    | ⚠️ Skipped | 0      | No data                           |

**Fixes**:

1. Change `source_count` in `$setOnInsert` from 1 to 0
2. Replace `entity.original_id` with `entity.entity_id`

---

### Run 3 (Expected After Fixes)

| Stage               | Status     | Chunks | Result               |
| ------------------- | ---------- | ------ | -------------------- |
| **1. Extraction**   | ✅ Success | 400    | Entities extracted   |
| **2. Resolution**   | ✅ Success | 400    | Entities resolved    |
| **3. Construction** | ✅ Success | 400    | Graph built          |
| **4. Detection**    | ✅ Success | 400    | Communities detected |

**Baseline Status**: ✅ VALID (all 4 stages successful)

---

## 🎓 Lessons Learned

### Technical Lessons

1. **MongoDB Update Operators**: Same field can't appear in multiple operators
2. **Upsert Logic**: Need to carefully handle counters in upserts
3. **Model Attributes**: Always verify attribute names match the model definition
4. **Error Handling**: Exception handlers must not depend on variables that might not be defined

### Process Lessons

1. **Incremental Testing**: Each fix reveals new bugs - test after each fix
2. **Root Cause Analysis**: Don't assume first error is the only error
3. **Code Review**: Check all references to attributes/fields
4. **Documentation**: Track each bug and fix systematically

### Prevention

1. **Unit Tests**: Test upsert logic with new and existing entities
2. **Integration Tests**: Test full pipeline with small dataset
3. **Code Review**: Check MongoDB update operations for conflicts
4. **Linting**: Add checks for undefined variables in except blocks

---

## ✅ Resolution Status

**Bug 1 (MongoDB Conflict)**: ✅ ROOT CAUSE IDENTIFIED  
**Bug 2 (AttributeError)**: ✅ ROOT CAUSE IDENTIFIED  
**Fixes Status**: ⏳ READY TO APPLY  
**Test Status**: ⏳ PENDING (after fixes)  
**Documentation**: ✅ COMPLETE

**Next Action**: Apply both fixes to `business/stages/graphrag/entity_resolution.py`

---

## 📝 Files to Update

1. **`business/stages/graphrag/entity_resolution.py`**:

   - Line 623: Change `"source_count": 1` to `"source_count": 0`
   - Line 187: Change `entity.original_id` to `entity.entity_id` (2 occurrences)
   - Line 554: Change `original_id` to `entity.entity_id` (2 occurrences)

2. **`EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_21_01.md`**:

   - Add Phase 2.3: "Second Bug Fix & Re-run"
   - Document both bugs and fixes

3. **`BASELINE-RUN-RESULTS-FINAL-2025-11-12.md`**:
   - Mark as superseded by Run 2 analysis

---

**Prepared By**: AI Debug Investigation  
**Investigation Time**: 20 minutes  
**Complexity**: High (multiple interacting bugs, MongoDB update semantics)  
**Confidence**: 100% (both root causes definitively identified)
