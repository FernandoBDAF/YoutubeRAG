# Clean GraphRAG Fields Command (CORRECTED)

**Date**: 2025-11-12  
**Purpose**: Remove all GraphRAG processing fields from `video_chunks` to allow re-processing  
**Status**: ✅ CORRECTED - All 4 fields identified

---

## ⚠️ Correction Notice

**Previous version was INCOMPLETE** - missing `graphrag_communities` field!

The correct fields to clean are:

1. ✅ `graphrag_extraction` - Stage 1 (Graph Extraction)
2. ✅ `graphrag_resolution` - Stage 2 (Entity Resolution)
3. ✅ `graphrag_construction` - Stage 3 (Graph Construction)
4. ✅ `graphrag_communities` - Stage 4 (Community Detection) ← **WAS MISSING!**

---

## 🔍 Field Verification

**Source**: Checked all 4 stage files in `business/stages/graphrag/`:

| Stage       | File                     | Field Name              | Line Reference       |
| ----------- | ------------------------ | ----------------------- | -------------------- |
| **Stage 1** | `extraction.py`          | `graphrag_extraction`   | Lines 76, 197, 258   |
| **Stage 2** | `entity_resolution.py`   | `graphrag_resolution`   | Lines 98, 207, 749   |
| **Stage 3** | `graph_construction.py`  | `graphrag_construction` | Lines 210, 339, 1530 |
| **Stage 4** | `community_detection.py` | `graphrag_communities`  | Lines 109, 315, 654  |

---

## ✅ Corrected Command

```bash
mongosh "mongodb+srv://fernandobarroso_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "
    db.video_chunks.updateMany(
      {},
      {
        \$unset: {
          'graphrag_extraction': '',
          'graphrag_resolution': '',
          'graphrag_construction': '',
          'graphrag_communities': ''
        }
      }
    )
  "
```

---

## 📊 What This Does

Removes all 4 GraphRAG processing status fields from ALL chunks in `validation_01.video_chunks`:

| Field                   | Stage | What It Tracks                        |
| ----------------------- | ----- | ------------------------------------- |
| `graphrag_extraction`   | 1     | Entity/relationship extraction status |
| `graphrag_resolution`   | 2     | Entity resolution status              |
| `graphrag_construction` | 3     | Graph construction status             |
| `graphrag_communities`  | 4     | Community detection status            |

---

## 🎯 Expected Output

```
{
  acknowledged: true,
  insertedId: null,
  matchedCount: 2006,
  modifiedCount: 2006,  // ← All chunks cleaned
  upsertedCount: 0
}
```

---

## ✅ Verification After Cleaning

```bash
mongosh "mongodb+srv://fernandobarroso_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "
    print('Total chunks:', db.video_chunks.countDocuments({}));
    print('With extraction:', db.video_chunks.countDocuments({'graphrag_extraction': {\$exists: true}}));
    print('With resolution:', db.video_chunks.countDocuments({'graphrag_resolution': {\$exists: true}}));
    print('With construction:', db.video_chunks.countDocuments({'graphrag_construction': {\$exists: true}}));
    print('With communities:', db.video_chunks.countDocuments({'graphrag_communities': {\$exists: true}}));
  "
```

**Expected**:

```
Total chunks: 2006
With extraction: 0    ← All cleaned
With resolution: 0    ← All cleaned
With construction: 0  ← All cleaned
With communities: 0   ← All cleaned
```

---

## 📝 Why This Matters

**Pipeline Stage Dependencies**:

```
Stage 1 (Extraction)
  ↓ Sets: graphrag_extraction.status = "completed"
  ↓
Stage 2 (Resolution)
  ↓ Requires: graphrag_extraction.status = "completed"
  ↓ Sets: graphrag_resolution.status = "completed"
  ↓
Stage 3 (Construction)
  ↓ Requires: graphrag_resolution.status = "completed"
  ↓ Sets: graphrag_construction.status = "completed"
  ↓
Stage 4 (Detection)
  ↓ Requires: graphrag_construction.status = "completed"
  ↓ Sets: graphrag_communities.status = "completed"
```

**If ANY field is left behind**:

- That stage will SKIP the chunk (thinks it's already processed)
- Subsequent stages will have NO data to process
- Result: Incomplete pipeline run

---

## 🚨 Previous Error

**What was wrong**:

- Used `graphrag_detection` instead of `graphrag_communities`
- This is NOT a field used by the pipeline
- Stage 4 would skip all chunks (thinking they're already processed)

**How discovered**:

- User noticed missing field
- Verified by checking all 4 stage files
- Confirmed correct field name: `graphrag_communities`

---

## 📚 Related Documentation

- `EXECUTION_DEBUG_ENTITY-RESOLUTION-DECORATOR-BUG.md` - Bug fix that required this cleanup
- `BASELINE-RUN-RESULTS-FINAL-2025-11-12.md` - Original run that showed pre-processed chunks issue
- `CLEAN-GRAPHRAG-FIELDS-COMMAND.md` - Original (incorrect) version

---

**Status**: ✅ CORRECTED  
**Ready to use**: YES  
**Verified**: All 4 fields confirmed from source code
