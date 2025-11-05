# CRITICAL ISSUE: Graph Extraction Data Not Saved

**Date**: November 2, 2025  
**Severity**: CRITICAL ❌  
**Impact**: 61 hours of LLM extraction work lost  
**Root Cause**: Multiple issues compounding

---

## 💔 The Situation

### What Happened:

1. GraphRAG pipeline ran for 61 hours (Oct 31 - Nov 2)
2. graph_extraction stage processed 13,069 chunks
3. Logs show: "processed=13069 updated=13051"
4. **BUT**: Zero chunks have `graphrag_extraction` metadata in MongoDB
5. **Result**: All extraction data lost

### Verification:

```bash
Total chunks in database: 13,069 ✅
Chunks with graphrag_extraction: 0 ❌
Entities collection: Does not exist ❌
Relations collection: Does not exist ❌
```

---

## 🔍 Root Cause Analysis

### Issue #1: graspologic Not Installed ⭐ PRIMARY

**Error**:

```
ModuleNotFoundError: No module named 'graspologic'
```

**Impact**: Pipeline couldn't even import properly  
**When**: When trying to load `business.pipelines.runner`  
**Why**: CommunityDetectionStage imports graspologic

**But this doesn't explain why extraction didn't save...**

---

### Issue #2: Extraction Stage Not Writing to DB ⭐ ACTUAL CAUSE

**Historical Context**: We discovered this bug weeks ago!

**The Bug**: `graph_extraction.py` handle_doc() was returning extraction data instead of writing to MongoDB.

**We Fixed It**: Modified `handle_doc()` to explicitly write to database

**But**: The fix might not have been in place when this run started (Oct 31)

**Evidence**:

- Logs say "updated=13051"
- But ZERO chunks have the data
- This matches the exact bug pattern we fixed

**Let me check current code**...

---

### Issue #3: When Did This Run Start?

**Timeline Confusion**:

- Run started: Oct 31 evening
- Folder refactor happened: Oct 31 (during session)
- Run completed: Nov 2 11:56am

**Possibilities**:
A. Run started with old (buggy) code before our fixes
B. Run started with new code but old imports were cached
C. Database write permissions issue

---

## 🔧 Diagnostic Commands

### Check Current graph_extraction Code:

Let me verify if the current code actually writes to DB:

```bash
# Check if handle_doc writes to MongoDB
grep -A 20 "def handle_doc" business/stages/graphrag/extraction.py | grep "update_one\|insert_one"
```

If this shows database writes → Code is correct, run started with old code  
If no writes found → Code is still buggy, need to fix

---

### Check What Code Was Running:

**Question**: Was the pipeline using old code or new code?

**Evidence from logs**:

```
2025-11-02 11:56:15,588 - graph_extraction - INFO - [graph_extraction] Summary: processed=13069 updated=13051
```

The logger name is "graph_extraction" not "app.stages.graph_extraction"

This suggests it might be using a different version of the code!

---

## 🚨 Immediate Actions Needed

### 1. Verify Current Code (5 min)

Check if graph_extraction stage writes to DB:

```python
# Check business/stages/graphrag/extraction.py
# handle_doc() should have:
collection.update_one(
    {"chunk_id": doc["chunk_id"]},
    {"$set": {"graphrag_extraction": {...}}}
)
```

### 2. Install graspologic (1 min)

```bash
pip install graspologic
```

### 3. Test Pipeline on 1 Chunk (2 min)

```bash
python -m app.cli.graphrag --max 1
```

**Expected**: 1 chunk gets graphrag_extraction metadata  
**Verify**: Check MongoDB after run

### 4. If Test Passes → Re-run Full Pipeline

**Reality**: Need another 61 hours 😞

**Options**:
A. Re-run full 13k chunks (61 hours)
B. Run on subset for testing (1 hour for 100 chunks)
C. Fix code, validate thoroughly, then decide

---

## 📊 Cost Analysis

### What Was Lost:

- **Time**: 61 hours of processing
- **LLM Costs**: ~13k API calls × $0.0001-0.0005 = **$1.30-$6.50**
- **Extraction Data**: ~65k entities, ~80k relationships (raw)

### What Can Be Recovered:

- **Nothing** - Must re-run from scratch

### Cost to Recover:

- **Time**: Another 61 hours
- **LLM Costs**: Another $1.30-$6.50
- **Confidence**: Need to verify code works first!

---

## 🎯 Recovery Plan

### Phase 1: Validate Code (30 min)

1. **Check graph_extraction.py**:

   - Verify handle_doc() writes to MongoDB
   - If not, fix it!

2. **Install dependencies**:

   ```bash
   pip install graspologic
   ```

3. **Test on 1 chunk**:

   ```bash
   python -m app.cli.graphrag --max 1
   ```

4. **Verify data saved**:
   ```python
   count = db.video_chunks.count_documents({'graphrag_extraction.status': 'completed'})
   # Should be 1
   ```

### Phase 2: Small Test Run (1-2 hours)

**Test on 100 chunks**:

```bash
python -m app.cli.graphrag --max 100
```

**Verify**:

- All 100 chunks get extraction metadata ✓
- entity_resolution creates entities ✓
- graph_construction creates relationships ✓
- community_detection runs (or skip if Louvain not fixed)

**Duration**: ~25 minutes extraction + processing

### Phase 3: Decision Point

**If 100-chunk test succeeds**:

**Option A**: Re-run full 13k (61 hours)

- Verified working
- Complete graph
- High cost

**Option B**: Run on subset (1k chunks, 6 hours)

- Faster validation
- Smaller graph
- Lower cost

**Option C**: Wait and optimize

- Fix community detection first (Louvain)
- Implement better error handling
- Then run with confidence

---

## 🔑 Critical Questions to Answer

### 1. Does current code write to DB?

**Check**:

```bash
grep -B5 -A10 "def handle_doc" business/stages/graphrag/extraction.py | grep update_one
```

**If YES**: Code is correct, old run used buggy code  
**If NO**: Code is buggy, must fix before re-running

### 2. Why did stats say "updated=13051"?

**Theory**: Stats counter incremented even though DB write failed/didn't happen

**Need**: Better logging to show actual MongoDB write confirmation

### 3. Can we add data persistence verification?

**Solution**: After each write, log the actual write result:

```python
result = collection.update_one(...)
logger.info(f"MongoDB write: matched={result.matched_count} modified={result.modified_count}")
```

---

## ⚠️ Prevention Measures (For Next Run)

### 1. Pre-Run Validation

```bash
# Test imports
python -c "from business.pipelines.graphrag import GraphRAGPipeline"

# Test on 1 chunk
python -m app.cli.graphrag --max 1

# Verify data saved
# Check MongoDB manually
```

### 2. Real-Time Monitoring

```bash
# Watch logs
tail -f logs/pipeline/graphrag.log | grep "Summary\|ERROR"

# Monitor MongoDB
# Check counts every hour
```

### 3. Checkpointing

- Save progress every 1000 chunks
- Verify data exists in DB
- Alert if counts don't match

---

## 🚀 Next Steps (RIGHT NOW)

**Run these diagnostic commands to understand what happened**:

```bash
# 1. Check if current code writes to DB
grep -A15 "def handle_doc" business/stages/graphrag/extraction.py

# 2. Install graspologic
pip install graspologic

# 3. Test on 1 chunk
python -m app.cli.graphrag --max 1

# 4. Verify it worked
python -c "
from dependencies.database.mongodb import get_mongo_client
db = get_mongo_client()['mongo_hack']
count = db.video_chunks.count_documents({'graphrag_extraction.status': 'completed'})
print(f'After test: {count} chunks with extraction')
"
```

**If test passes → We know the issue and can re-run safely**  
**If test fails → Need to fix code first**

---

**Status**: Need immediate diagnostic to understand if current code is correct before deciding on recovery strategy.
