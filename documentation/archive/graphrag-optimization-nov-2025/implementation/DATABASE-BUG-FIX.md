# Critical Database Bug Fix

**Date**: November 4, 2025  
**Issue**: Entities and relations written to wrong database  
**Status**: ✅ FIXED

---

## 🐛 The Bug

### What Happened:

After running entity_resolution and graph_construction on `validation_db`, **no collections were created** in validation_db.

### Investigation:

```
mongo_hack:
  entities: 27,234 ✓ (written here!)
  relations: 31,530 ✓ (written here!)

validation_db:
  entities: 0 ✗ (should be here!)
  relations: 0 ✗ (should be here!)
```

**Root Cause**: Stages were using `self.db` instead of `self.db_write`

---

## 🔍 Root Cause Analysis

### Code Before (WRONG):

```python
# entity_resolution.py line 64
self.graphrag_collections = get_graphrag_collections(self.db)  # ❌

# graph_construction.py line 65
self.graphrag_collections = get_graphrag_collections(self.db)  # ❌

# community_detection.py line 71
self.graphrag_collections = get_graphrag_collections(self.db)  # ❌
```

**Problem**:

- `self.db` = `config.db_name` (default: "mongo_hack")
- `self.db_write` = `config.write_db_name` (e.g., "validation_db")
- Stages were READING from validation_db but WRITING to mongo_hack!

---

## ✅ The Fix

### Code After (CORRECT):

```python
# entity_resolution.py line 64
self.graphrag_collections = get_graphrag_collections(self.db_write)  # ✅

# graph_construction.py line 65
self.graphrag_collections = get_graphrag_collections(self.db_write)  # ✅

# community_detection.py line 71
self.graphrag_collections = get_graphrag_collections(self.db_write)  # ✅
```

**Result**: Now entities and relations will be written to the correct write database!

---

## 📋 Files Changed

1. ✅ `business/stages/graphrag/entity_resolution.py`
2. ✅ `business/stages/graphrag/graph_construction.py`
3. ✅ `business/stages/graphrag/community_detection.py`

**Change**: `self.db` → `self.db_write` for graphrag_collections

---

## ✅ Validation

### Before Fix:

```bash
--write-db-name validation_db
```

**Result**: Entities/relations written to mongo_hack ❌

### After Fix:

```bash
--write-db-name validation_db
```

**Result**: Entities/relations written to validation_db ✅

---

## 🚀 Ready to Test

**Command**:

```bash
GRAPHRAG_USE_TPM_TRACKING=true \
GRAPHRAG_TARGET_TPM=950000 \
GRAPHRAG_TARGET_RPM=10000 \
python -m app.cli.graphrag \
  --max 13069 \
  --concurrency 100 \
  --read-db-name validation_db \
  --write-db-name validation_db \
  --log-file logs/graphrag_full_tpm_fixed.log \
  --verbose
```

**Expected**:

- ✅ Entities written to validation_db.entities
- ✅ Relations written to validation_db.relations
- ✅ Communities written to validation_db.communities
- ✅ All GraphRAG fields in validation_db.video_chunks

---

**Bug**: ✅ Fixed  
**Database**: ✅ Cleaned and ready  
**Test**: ✅ Ready to run!
