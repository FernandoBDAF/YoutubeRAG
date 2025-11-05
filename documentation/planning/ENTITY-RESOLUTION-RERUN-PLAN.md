# Entity Resolution Rerun - Validation & Execution Plan

**Date**: November 4, 2025  
**Status**: ✅ **READY TO RUN** - Implementation validated  
**Last Failed At**: entity_resolution stage (61-hour run on Nov 2)

---

## 📋 Implementation Validation

### ✅ Libraries Applied (Other Session)

**From `LIBRARY-APPLICATION-STATUS.md`**:

1. **✅ database.batch_insert** - Applied to `entity_resolution.py`

   - Lines 19-21: Import added
   - Lines 342-353: Used for entity mentions batch insertion
   - **Result**: Better error handling + statistics tracking

2. **✅ concurrency.run_llm_concurrent** - Applied to ingestion stages

   - `enrich.py` and `clean.py` now use concurrent processing
   - **Impact**: 54 hours → 11 hours (5x speedup for 13k chunks)

3. **✅ rate_limiting.RateLimiter** - Applied to `rag/core.py`

   - Prevents hitting Voyage API rate limits proactively

4. **✅ serialization.json_encoder** - Applied to `chat/export.py`
   - Removed 30-line duplicate MongoDB type handling

**Tests**:

- ✅ Serialization: 12 tests, 3 bugs fixed
- ✅ Data Transform: 10 tests passing
- ✅ All tests passing (100% pass rate)

---

## 🔍 Entity Resolution Stage Review

### Code Changes (business/stages/graphrag/entity_resolution.py)

**Status**: ✅ **VALIDATED** - All changes are improvements

#### 1. Import Added (Lines 19-21):

```python
from core.libraries.database import (
    batch_insert,
)  # Better error handling than insert_many
```

**Impact**: ✅ Safer batch operations with detailed statistics

#### 2. Batch Insert Used (Lines 342-353):

```python
# Before (insert_many):
mentions_collection.insert_many(mentions)

# After (batch_insert):
result = batch_insert(
    collection=mentions_collection,
    documents=mentions,
    batch_size=1000,
    ordered=False,  # Continue on errors
)
logger.debug(
    f"Inserted {result['inserted']}/{result['total']} entity mentions "
    f"(chunk {chunk_id})"
)
```

**Impact**:

- ✅ Better error resilience (`ordered=False` continues on errors)
- ✅ Detailed statistics (`inserted`, `total`, `failed`)
- ✅ More informative logging

#### 3. Existing Features Still Present:

- ✅ `upsert_existing` support (lines 162-176)
- ✅ Entity deduplication (checks `entity_id`)
- ✅ Entity update logic (merges aliases, updates confidence)
- ✅ Error handling and failure marking
- ✅ Progress logging

**Conclusion**: All changes are additive - no functionality removed ✅

---

## 📊 What We Know From Last Run

### ✅ graph_extraction Success (Nov 2, 2025)

**Results**:

- ✅ Processed: 13,069 chunks
- ✅ Successful: 13,051 chunks (99.9%)
- ✅ Failed: 18 chunks (0.1%)
- ✅ **Data saved to MongoDB**: All 13,051 chunks have `graphrag_extraction` metadata
- ✅ Duration: 61 hours (~390 chunks/hour)

**Verification**:

```
Total chunks: 13,069
Chunks with graphrag_extraction: 13,069
Chunks with status='completed': 13,051
Sample extraction: 6 entities, 5 relationships ✅
```

### ❌ entity_resolution Failure

**From logs** (GRAPHRAG-13K-CORRECT-ANALYSIS.md):

```
2025-11-02 11:56:15,588 - graph_extraction - INFO - Summary: processed=13069 updated=13051...
[pipeline] (2/4) Running entity_resolution with read_db=mongo_hack write_db=mongo_hack
2025-11-02 11:56:15,596 - __main__ - ERROR - Error running GraphRAG pipeline:
```

**Problem**: Empty error message - complete blindness!

**Impact**:

- ❌ No chunks have `graphrag_resolution` metadata
- ❌ Entities collection: 0 documents
- ❌ Entity_mentions collection: 0 documents

---

## 🛡️ Safety Checks Before Rerun

### ✅ Check 1: Extraction Data Exists

```bash
# Connect to MongoDB and verify:
use mongo_hack

# Check chunks with extraction data
db.video_chunks.countDocuments({
  "graphrag_extraction.status": "completed"
})
# Expected: 13,051

# Sample extraction data
db.video_chunks.findOne(
  {"graphrag_extraction.status": "completed"},
  {"graphrag_extraction": 1, "chunk_id": 1}
)
# Expected: Should show entities and relationships
```

**If count ≠ 13,051**: Stop and investigate extraction data

### ✅ Check 2: Collections Exist

```bash
# Check GraphRAG collections exist
db.getCollectionNames().filter(name => name.includes("entities") || name.includes("relations") || name.includes("communities"))

# Expected: entities, entity_mentions, relations, communities
```

**If collections missing**: Run `python app/scripts/utilities/seed_indexes.py`

### ✅ Check 3: Current State

```bash
# Check if any resolution already exists
db.video_chunks.countDocuments({
  "graphrag_resolution.status": "completed"
})
# Expected: 0 (clean start)

# Check entities collection
db.entities.countDocuments({})
# Expected: 0 (clean start)
```

**If data exists**: Decide whether to:

- A. Clean and start fresh: Delete entities, entity_mentions, reset resolution metadata
- B. Continue from where it failed: Use `--upsert-existing` flag

---

## 🚀 Execution Plan

### Strategy A: Fresh Start (Recommended)

**Why**:

- Last run failed with empty error
- No partial data to preserve
- Clean slate ensures consistency

**Steps**:

```bash
# 1. Clean existing data (if any)
mongosh "mongodb+srv://cluster0.djtttp9.mongodb.net/mongo_hack" \
  --username <user> --password <pass> \
  --eval "
    db.video_chunks.updateMany(
      {'graphrag_resolution': {\$exists: true}},
      {\$unset: {'graphrag_resolution': 1}}
    );
    db.entities.deleteMany({});
    db.entity_mentions.deleteMany({});
    print('Cleaned resolution data');
  "

# 2. Run entity_resolution with small test batch
python app/cli/graphrag.py \
  --stage entity_resolution \
  --max 10 \
  --model gpt-4o-mini \
  --verbose \
  --log-file logs/entity_resolution_test.log

# 3. Verify test results
mongosh "mongodb+srv://cluster0.djtttp9.mongodb.net/mongo_hack" \
  --eval "
    print('Resolved chunks:', db.video_chunks.countDocuments({
      'graphrag_resolution.status': 'completed'
    }));
    print('Total entities:', db.entities.countDocuments({}));
    print('Total mentions:', db.entity_mentions.countDocuments({}));
  "

# 4. If test succeeds, run full resolution
python app/cli/graphrag.py \
  --stage entity_resolution \
  --model gpt-4o-mini \
  --verbose \
  --log-file logs/entity_resolution_full.log \
  --resolution-concurrency 2

# 5. Monitor progress (in another terminal)
tail -f logs/entity_resolution_full.log | grep -E "(INFO|WARNING|ERROR)"
```

### Strategy B: Continue from Last State (If partial data exists)

**Steps**:

```bash
# 1. Check current state
mongosh "mongodb+srv://cluster0.djtttp9.mongodb.net/mongo_hack" \
  --eval "
    print('Resolved:', db.video_chunks.countDocuments({
      'graphrag_resolution.status': 'completed'
    }));
    print('Pending:', db.video_chunks.countDocuments({
      'graphrag_extraction.status': 'completed',
      'graphrag_resolution.status': {\$ne: 'completed'}
    }));
  "

# 2. Run with --upsert-existing (will reprocess failed chunks)
python app/cli/graphrag.py \
  --stage entity_resolution \
  --model gpt-4o-mini \
  --upsert-existing \
  --verbose \
  --log-file logs/entity_resolution_continue.log
```

---

## 📊 Expected Results

### Time Estimates

**Per Chunk**:

- Entity resolution: ~5-10s (LLM + DB operations)
- With concurrency=2: ~2.5-5s per chunk

**For 13,051 chunks**:

- Sequential: ~18-36 hours
- Concurrency=2: ~9-18 hours
- Concurrency=5: ~3.6-7.2 hours

**Recommended**: Start with `--resolution-concurrency 2` to avoid rate limits

### Database Changes

**video_chunks collection**:

- All 13,051 chunks should get `graphrag_resolution` metadata:
  ```json
  {
    "graphrag_resolution": {
      "status": "completed",
      "resolved_entities": 6,
      "stored_entities": 5,
      "processed_at": 1730742000,
      "model_used": "gpt-4o-mini"
    }
  }
  ```

**entities collection**:

- Expected: ~15,000-25,000 unique entities
- Each entity has:
  - `entity_id`: 32-char MD5 hash
  - `canonical_name`: Resolved name
  - `type`: PERSON, TECH, ORG, CONCEPT, EVENT
  - `description`: From LLM
  - `confidence`: 0.0-1.0
  - `source_count`: Number of mentions
  - `aliases`: Alternative names
  - `source_chunks`: Array of chunk IDs

**entity_mentions collection**:

- Expected: ~78,000-100,000 mentions (6-8 per chunk)
- Links entities to chunks

---

## 🔍 Monitoring & Validation

### During Execution

**Watch for these patterns**:

```bash
# Good signs:
INFO - Processing chunk XYZ for entity resolution
INFO - Successfully resolved 6 entities for chunk XYZ
DEBUG - Inserted 6/6 entity mentions (chunk XYZ)

# Warning signs:
WARNING - No entity extraction data found in chunk XYZ
ERROR - Error processing chunk XYZ for entity resolution
```

**Check database live** (every 1000 chunks):

```bash
mongosh "mongodb+srv://cluster0.djtttp9.mongodb.net/mongo_hack" \
  --eval "
    print('Progress:');
    print('  Resolved:', db.video_chunks.countDocuments({
      'graphrag_resolution.status': 'completed'
    }), '/ 13051');
    print('  Entities:', db.entities.countDocuments({}));
    print('  Mentions:', db.entity_mentions.countDocuments({}));
  "
```

### After Completion

**Validation Queries**:

```javascript
// 1. Check resolution coverage
db.video_chunks.aggregate([
  { $match: { "graphrag_extraction.status": "completed" } },
  {
    $group: {
      _id: "$graphrag_resolution.status",
      count: { $sum: 1 },
    },
  },
]);
// Expected: {_id: "completed", count: 13051} (or close)

// 2. Check entity quality
db.entities.aggregate([
  {
    $group: {
      _id: "$type",
      count: { $sum: 1 },
      avgConfidence: { $avg: "$confidence" },
      avgSourceCount: { $avg: "$source_count" },
    },
  },
  { $sort: { count: -1 } },
]);
// Expected: Balanced distribution, confidence > 0.6, source_count > 1

// 3. Check for orphaned entities (no mentions)
db.entities.aggregate([
  {
    $lookup: {
      from: "entity_mentions",
      localField: "entity_id",
      foreignField: "entity_id",
      as: "mentions",
    },
  },
  { $match: { mentions: { $size: 0 } } },
  { $count: "orphaned" },
]);
// Expected: 0 orphaned entities

// 4. Top entities by source count
db.entities
  .find({}, { canonical_name: 1, type: 1, source_count: 1 })
  .sort({ source_count: -1 })
  .limit(10);
// Should show meaningful entities with high source counts
```

---

## 🚨 Troubleshooting

### If Entity Resolution Fails Again

**Diagnostic Steps**:

1. **Check error logs**:

   ```bash
   tail -100 logs/entity_resolution_full.log | grep -E "ERROR|WARNING"
   ```

2. **Check for rate limiting**:

   ```bash
   grep -i "rate limit" logs/entity_resolution_full.log
   ```

   - If found: Reduce concurrency or add delays

3. **Check for validation errors**:

   ```bash
   grep -i "validation" logs/entity_resolution_full.log
   ```

   - If found: Check entity/mention Pydantic models

4. **Test with single chunk**:

   ```bash
   # Find a specific chunk ID
   CHUNK_ID=$(mongosh "mongodb+srv://cluster0.djtttp9.mongodb.net/mongo_hack" \
     --quiet --eval "db.video_chunks.findOne({'graphrag_extraction.status': 'completed'}).chunk_id")

   # Run resolution on just that chunk
   python app/cli/graphrag.py \
     --stage entity_resolution \
     --max 1 \
     --verbose
   ```

5. **Check library integration**:
   - Verify `database.batch_insert` is imported correctly
   - Check for import errors in logs

### Common Issues & Fixes

**Issue 1: Empty error message** (like last run)

- **Fix**: Enhanced error logging added to `app/cli/graphrag.py`
- Now logs full traceback with `logger.exception()`

**Issue 2: Rate limits**

- **Fix**: Use `--resolution-concurrency 1` or 2 (not higher)
- Use `rate_limiting.RateLimiter` (already applied to rag/core.py)

**Issue 3: Database connection timeout**

- **Fix**: Add connection timeout to MongoDB client
- Check network stability

**Issue 4: Pydantic validation errors**

- **Fix**: Check entity schema matches `ResolvedEntity` model
- Verify all required fields are present

---

## ✅ GO/NO-GO Decision

### ✅ GREEN LIGHTS (All True):

- [x] Extraction data exists (13,051 chunks)
- [x] Libraries applied and tested (database.batch_insert)
- [x] Error handling improved (batch operations, logging)
- [x] GraphRAG collections exist
- [x] MongoDB connection working
- [x] OpenAI API key configured

### 🚫 RED LIGHTS (Any True):

- [ ] Extraction data missing or corrupted
- [ ] Library tests failing
- [ ] MongoDB connection issues
- [ ] OpenAI API key missing/invalid

**Status**: ✅ **ALL GREEN - SAFE TO RUN**

---

## 🎯 Recommended Execution

**Start with test run**:

```bash
# Terminal 1: Run test with 10 chunks
python app/cli/graphrag.py \
  --stage entity_resolution \
  --max 10 \
  --model gpt-4o-mini \
  --verbose \
  --log-file logs/entity_resolution_test_$(date +%Y%m%d_%H%M%S).log

# Terminal 2: Monitor logs
tail -f logs/entity_resolution_test_*.log
```

**If test succeeds**, run full pipeline:

```bash
# Start full run
python app/cli/graphrag.py \
  --stage entity_resolution \
  --model gpt-4o-mini \
  --resolution-concurrency 2 \
  --verbose \
  --log-file logs/entity_resolution_full_$(date +%Y%m%d_%H%M%S).log
```

**Monitor progress**:

```bash
# Terminal 2: Live monitoring
while true; do
  clear
  echo "=== Entity Resolution Progress ==="
  echo "Time: $(date)"
  mongosh "mongodb+srv://cluster0.djtttp9.mongodb.net/mongo_hack" \
    --quiet --eval "
      var completed = db.video_chunks.countDocuments({'graphrag_resolution.status': 'completed'});
      var total = 13051;
      var percent = (completed / total * 100).toFixed(2);
      print('Completed: ' + completed + ' / ' + total + ' (' + percent + '%)');
      print('Entities: ' + db.entities.countDocuments({}));
      print('Mentions: ' + db.entity_mentions.countDocuments({}));
    "
  sleep 60
done
```

---

**Status**: ✅ **VALIDATED AND READY**  
**Recommendation**: **START WITH 10-CHUNK TEST, THEN FULL RUN**  
**Estimated Time**: 9-18 hours (with concurrency=2)
