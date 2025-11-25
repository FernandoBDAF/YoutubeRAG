# Baseline Pipeline Run Results (FINAL) - Achievement 2.1

**Date**: 2025-11-12  
**Run ID**: f6530127-48e7-4c3d-8039-6d74291b5fef  
**Log File**: `logs/pipeline/graphrag_full_pipeline_20251112_135015.log`  
**Status**: ✅ **COMPLETED** with ⚠️ **CRITICAL BUG IN STAGE 2**

---

## 📊 Executive Summary

**Pipeline Configuration**:

- **Database**: `validation_01` (single database mode)
- **Chunks Processed**: 400 (cleaned from previous runs)
- **Observability**: DISABLED (baseline run)
- **Model**: `gpt-4o-mini`
- **Workers**: 300 concurrent workers
- **TPM Limit**: 950,000
- **RPM Limit**: 20,000

**Overall Results**:

- ✅ Stage 1 (Extraction): **SUCCESS** - 400 chunks processed, entities extracted
- ❌ Stage 2 (Resolution): **FAILED** - All 400 chunks failed with error
- ⚠️ Stage 3 (Construction): **SKIPPED** - No documents to process (Stage 2 failed)
- ⚠️ Stage 4 (Detection): **SKIPPED** - No documents to process (Stage 2 failed)
- ⏱️ Total Runtime: **2 minutes 49 seconds** (169s)
- 🎯 Exit Code: 0 (pipeline completed, but with errors)

---

## ⏱️ Timeline & Performance

### Start & End Times

| Event                | Timestamp           | Notes                              |
| -------------------- | ------------------- | ---------------------------------- |
| **Pipeline Start**   | 2025-11-12 13:50:15 | Trace ID generated                 |
| **Setup Complete**   | 2025-11-12 13:50:17 | Collections & indexes created (2s) |
| **Stage 1 Start**    | 2025-11-12 13:50:17 | Graph Extraction begins            |
| **Stage 1 Complete** | 2025-11-12 13:52:09 | 400 chunks processed (112s)        |
| **Stage 2 Start**    | 2025-11-12 13:52:10 | Entity Resolution begins           |
| **Stage 2 Complete** | 2025-11-12 13:53:04 | All 400 failed with error (54s)    |
| **Stage 3 Complete** | 2025-11-12 13:53:04 | No documents to process (instant)  |
| **Stage 4 Complete** | 2025-11-12 13:53:04 | No documents to process (instant)  |
| **Pipeline End**     | 2025-11-12 13:53:04 | Quality metrics calculated         |

### Stage Performance

| Stage               | Duration | Documents Processed | Status        | Notes                                  |
| ------------------- | -------- | ------------------- | ------------- | -------------------------------------- |
| **Setup**           | 2s       | N/A                 | ✅ Success    | Collections & indexes created          |
| **1. Extraction**   | 112s     | 400 chunks          | ✅ Success    | Entities extracted successfully        |
| **2. Resolution**   | 54s      | 400 chunks          | ❌ **FAILED** | All chunks failed with decorator error |
| **3. Construction** | <1s      | 0 chunks            | ⚠️ Skipped    | No documents (Stage 2 failed)          |
| **4. Detection**    | <1s      | 0 chunks            | ⚠️ Skipped    | No documents (Stage 2 failed)          |
| **Total**           | **169s** | 400 chunks          | ⚠️ Partial    | Only Stage 1 successful                |

---

## 🔍 Detailed Stage Analysis

### Stage 1: Graph Extraction ✅ SUCCESS

**Performance**:

- **Duration**: 111.6 seconds (~1.9 minutes)
- **Chunks Processed**: 400 chunks
- **Entities Extracted**: YES (multiple chunks show successful extraction)
- **Status**: ✅ **COMPLETED SUCCESSFULLY**

**Key Metrics**:

- TPM Usage: 218,500 (23% of 950k limit)
- Concurrent Workers: 300
- Updated: 400
- Failed: 0

**Sample Extractions** (from logs):

```
- Chunk f1423039: 7 entities, 1 relationship
- Chunk e26863d5: 4 entities, 0 relationships
- Chunk 006c9973: 5 entities, 0 relationships
- Chunk a692b56c: 5 entities, 1 relationship
- Chunk 549a8dc1: 11 entities, 1 relationship
- Chunk 0861cf24: 6 entities, 0 relationships
... (many more successful extractions)
```

**Observations**:

```
[graph_extraction] Batch 1 complete: 400 documents in 111.6s
(current TPM: 218,500, updated=400, failed=0)
```

✅ **Stage 1 worked perfectly!** Entities were successfully extracted from chunks.

---

### Stage 2: Entity Resolution ❌ CRITICAL FAILURE

**Performance**:

- **Duration**: 53.5 seconds
- **Chunks Attempted**: 400 chunks
- **Entities Resolved**: 0
- **Status**: ❌ **ALL 400 CHUNKS FAILED**

**Key Metrics**:

- TPM Usage: 1,540,000 (162% of 950k limit - anomaly)
- Updated: 0
- Failed: 400

**Critical Error**:

```
ERROR | business.stages.graphrag.entity_resolution | handle_doc:250 |
Error processing chunk for entity resolution:
handle_errors.<locals>.decorator() got an unexpected keyword argument 'entities'
```

**Observations**:

```
[entity_resolution] Batch 1 complete: 400 documents in 53.5s
(current TPM: 1,540,000, updated=0, failed=400)
```

**Root Cause**:

- There's a **bug in the error handling decorator**
- The decorator is being called with an `entities` keyword argument it doesn't expect
- This caused ALL 400 chunks to fail resolution
- No entities were resolved, so no `graphrag_resolution.status = 'completed'` was set

---

### Stage 3: Graph Construction ⚠️ SKIPPED

**Performance**:

- **Duration**: <1 second
- **Chunks Processed**: 0
- **Status**: ⚠️ **NO DOCUMENTS TO PROCESS**

**Query Used**:

```javascript
{
  'graphrag_resolution.status': 'completed',  // ← None exist!
  '$or': [
    {'graphrag_construction': {'$exists': False}},
    {'graphrag_construction.status': {'$ne': 'completed'}}
  ]
}
```

**Why Skipped**:

- Stage 3 requires `graphrag_resolution.status = 'completed'`
- Since Stage 2 failed for all chunks, no chunks have this status
- Result: 0 documents found to process

---

### Stage 4: Community Detection ⚠️ SKIPPED

**Performance**:

- **Duration**: <1 second
- **Chunks Processed**: 0
- **Status**: ⚠️ **NO DOCUMENTS TO PROCESS**

**Query Used**:

```javascript
{
  'graphrag_construction.status': 'completed',  // ← None exist!
  '$or': [
    {'graphrag_communities': {'$exists': False}},
    {'graphrag_communities.status': {'$ne': 'completed'}}
  ]
}
```

**Why Skipped**:

- Stage 4 requires `graphrag_construction.status = 'completed'`
- Since Stage 3 was skipped, no chunks have this status
- Result: 0 documents found to process

---

## 🎯 Baseline Metrics Summary

### Runtime Metrics

| Metric               | Value             | Notes                                |
| -------------------- | ----------------- | ------------------------------------ |
| **Total Runtime**    | 169 seconds       | 2 minutes 49 seconds                 |
| **Setup Time**       | 2 seconds         | Collections & indexes                |
| **Processing Time**  | 167 seconds       | All 4 stages                         |
| **Chunks Processed** | 400               | All attempted                        |
| **Throughput**       | 2.4 chunks/second | 400 chunks in 167s (processing only) |

### Resource Metrics

| Metric                 | Value       | Notes                             |
| ---------------------- | ----------- | --------------------------------- |
| **TPM Peak Usage**     | 1,540,000   | Stage 2 (162% of limit - anomaly) |
| **Stage 1 TPM**        | 218,500     | 23% of limit (normal)             |
| **RPM Limit**          | 20,000      | Not exceeded                      |
| **Concurrent Workers** | 300         | All stages                        |
| **Model**              | gpt-4o-mini | All LLM calls                     |

### Output Metrics

| Metric                   | Value | Notes                                  |
| ------------------------ | ----- | -------------------------------------- |
| **Entities Extracted**   | YES   | Stage 1 successful (exact count in DB) |
| **Entities Resolved**    | 0     | Stage 2 failed completely              |
| **Relations Created**    | 0     | Stage 3 skipped (no resolved entities) |
| **Communities Detected** | 0     | Stage 4 skipped (no relations)         |
| **Success Rate**         | 25%   | 1 of 4 stages successful               |

---

## 🚨 Critical Issues

### Issue 1: Stage 2 Decorator Error

**Error Message**:

```
handle_errors.<locals>.decorator() got an unexpected keyword argument 'entities'
```

**Impact**: ❌ **PIPELINE BLOCKER**

- All 400 chunks failed in Stage 2
- Stages 3 and 4 were skipped
- No usable baseline data produced

**Root Cause**:

- The `@handle_errors` decorator in entity resolution stage
- Being called with `entities=...` keyword argument
- Decorator doesn't accept this parameter

**Code Location**: `business/stages/graphrag/entity_resolution.py` line ~250

**Fix Required**:

- Remove `entities` keyword argument from decorator call
- OR update decorator to accept `entities` parameter

---

### Issue 2: Anomalous TPM Usage in Stage 2

**Observation**: Stage 2 reported TPM usage of 1,540,000 (162% of 950k limit)

**Possible Causes**:

1. TPM calculation error when all chunks fail
2. Error handling path doesn't properly track TPM
3. Failed chunks still counted toward TPM

**Impact**: Minor (doesn't affect execution, just metrics)

---

## 📝 Collections Status

### Expected Collections in `validation_01`

| Collection        | Expected Status       | Actual Status (Need Verification) |
| ----------------- | --------------------- | --------------------------------- |
| `video_chunks`    | ✅ Exists (2006 docs) | ✅ Exists with extraction data    |
| `entities`        | ⚠️ Created (? docs)   | ❓ Need to verify count           |
| `relations`       | ❌ Created (0 docs)   | ❌ Empty (Stage 3 skipped)        |
| `communities`     | ❌ Created (0 docs)   | ❌ Empty (Stage 4 skipped)        |
| `entity_mentions` | ⚠️ Created (? docs)   | ❓ Need to verify count           |
| `graphrag_runs`   | ✅ Created (1 doc)    | ✅ Run metadata exists            |

**Verification Commands**:

```bash
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "
    print('video_chunks:', db.video_chunks.countDocuments({}));
    print('entities:', db.entities.countDocuments({}));
    print('relations:', db.relations.countDocuments({}));
    print('communities:', db.communities.countDocuments({}));
    print('entity_mentions:', db.entity_mentions.countDocuments({}));
    print('graphrag_runs:', db.graphrag_runs.countDocuments({}));
    print('');
    print('Chunks with extraction completed:', db.video_chunks.countDocuments({'graphrag_extraction.status': 'completed'}));
    print('Chunks with resolution completed:', db.video_chunks.countDocuments({'graphrag_resolution.status': 'completed'}));
  "
```

---

## ✅ Success Criteria Verification

| Criterion                           | Status | Evidence                                          |
| ----------------------------------- | ------ | ------------------------------------------------- |
| Pipeline completes with exit code 0 | ✅     | Log line 8045                                     |
| No unhandled exceptions             | ⚠️     | Handled exceptions in Stage 2 (all chunks failed) |
| MongoDB collections populated       | ⚠️     | Entities extracted but not resolved               |
| Data quality acceptable             | ❌     | Stage 2 bug prevents resolution                   |
| Baseline metrics documented         | ✅     | This document                                     |
| All 4 stages executed               | ⚠️     | Stages 3-4 skipped due to Stage 2 failure         |
| Observability disabled              | ✅     | Confirmed in logs                                 |

**Overall Status**: ❌ **NOT VALID BASELINE** - Stage 2 bug prevents completion

---

## 🔧 Required Actions

### CRITICAL: Fix Stage 2 Bug

**Before Achievement 2.2**, this bug MUST be fixed:

1. **Identify the decorator issue**:

   - File: `business/stages/graphrag/entity_resolution.py`
   - Line: ~250 (error location)
   - Issue: `@handle_errors` decorator called with `entities=...` parameter

2. **Fix Options**:

   - **Option A**: Remove `entities` keyword argument from decorator call
   - **Option B**: Update `@handle_errors` decorator to accept `entities` parameter
   - **Option C**: Use different error handling approach for this call

3. **Test the fix**:

   - Re-run pipeline with `--max 50` to test quickly
   - Verify Stage 2 completes successfully
   - Verify Stages 3-4 run after Stage 2

4. **Re-run baseline**:
   - After fix, re-run with `--max 400`
   - This will be the TRUE baseline for Achievement 2.2 comparison

---

## 📊 What We Learned

### Positive Findings

1. ✅ **Stage 1 Works Perfectly**: 400 chunks processed, entities extracted successfully
2. ✅ **Cleanup Was Successful**: All 400 chunks were processed (not skipped)
3. ✅ **Performance is Good**: 112s for 400 chunks in Stage 1 (2.7 chunks/sec)
4. ✅ **Observability Disabled**: Confirmed working as expected

### Issues Discovered

1. ❌ **Stage 2 Has Critical Bug**: Decorator error prevents all resolution
2. ⚠️ **Pipeline Continues After Failures**: Exit code 0 even with all Stage 2 failures
3. ⚠️ **TPM Metrics Anomaly**: Stage 2 reports 162% TPM usage when failing

---

## 🎯 Next Steps

### Immediate (Before Achievement 2.2)

1. **Fix Stage 2 Bug** ← **CRITICAL BLOCKER**

   - Investigate `business/stages/graphrag/entity_resolution.py` line 250
   - Fix decorator call or decorator implementation
   - Test with small dataset (`--max 50`)

2. **Re-run Baseline**

   - After fix, re-run with `--max 400`
   - Verify all 4 stages complete
   - Document TRUE baseline metrics

3. **Verify Collections**
   - Run verification commands above
   - Check entity counts
   - Verify data quality

### For Achievement 2.2

**CANNOT PROCEED** until Stage 2 bug is fixed and baseline re-run is successful.

---

## 📚 Files Generated

1. **Log File**: `logs/pipeline/graphrag_full_pipeline_20251112_135015.log` (8046 lines)
2. **Baseline Report**: This document
3. **Collections**: Partially populated in `validation_01` database

---

**Prepared By**: AI Analysis of Achievement 2.1 Execution  
**Last Updated**: 2025-11-13 00:10 UTC  
**Status**: ⚠️ **INCOMPLETE** - Stage 2 bug must be fixed before proceeding
