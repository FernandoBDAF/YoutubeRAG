# Extraction Concurrent Implementation - Complete

**Date**: November 3, 2025  
**Status**: ✅ Option 1 implemented (10 workers)  
**Ready for**: Option 3 (advanced with 1M TPM)

---

## ✅ Option 1 Implemented

### What Was Added

**File**: `business/stages/graphrag/extraction.py`

**New Methods**:

1. `run()` - Overrides BaseStage.run() to enable concurrent processing
2. `_run_concurrent()` - Handles concurrent extraction
3. `_store_concurrent_results()` - Batch stores results

**Pattern Copied From**: enrich.py stage (proven working)

---

### How It Works

**Configuration**:

```python
# Enable concurrent processing:
python -m app.cli.graphrag --stage graph_extraction \
  --concurrency 10 \  # 10 workers
  --read-db-name mongo_hack \  # Read from production
  --write-db-name validation_db  # Write to validation DB
```

**Execution Flow**:

1. Override run() checks for `config.concurrency > 1`
2. If yes: Uses concurrent processing
3. If no: Falls back to sequential (BaseStage.run())

**Concurrent Processing**:

```python
# Agent factory (thread-safe)
agent_factory = lambda: GraphExtractionAgent(...)

# Run concurrent
results = run_llm_concurrent(
    chunks=docs,
    agent_factory=agent_factory,
    method_name='extract_from_chunk',
    max_workers=10,  # Configurable
    qps=10,  # 600 requests/minute
    retries=1,
    on_error=lambda e, chunk: None
)

# Store all results
_store_concurrent_results(docs, results)
```

---

## 📊 Performance Estimates

### Option 1: Moderate Concurrency (IMPLEMENTED)

| Workers | QPS    | Requests/Min | Time (13k chunks) | Speedup       |
| ------- | ------ | ------------ | ----------------- | ------------- |
| 1 (seq) | -      | ~60          | 60 hours          | 1x (baseline) |
| 5       | 10     | 600          | 12 hours          | 5x            |
| **10**  | **10** | **600**      | **6 hours**       | **10x** ⭐    |
| 15      | 10     | 600          | 4 hours           | 15x           |

**Current Implementation**: 10 workers, 10 QPS

---

### Option 3: Advanced (TO BE IMPLEMENTED)

**OpenAI Limits**:

- **RPM**: Check your tier (500-5,000 requests/min)
- **TPM**: **1,000,000 tokens/minute** (as you stated)

**Calculation**:

```
Assume:
- Average chunk: 500 tokens input + 500 tokens output = 1,000 tokens total
- TPM limit: 1,000,000
- Max chunks/minute: 1,000,000 / 1,000 = 1,000 chunks/min

For 13,031 chunks:
Time = 13,031 / 1,000 = ~13 minutes ✅✅✅
```

**Implementation**:

```python
from core.libraries.rate_limiting import RateLimiter

# Track both requests and tokens
request_limiter = RateLimiter(rpm=4500, name="openai_rpm")  # Conservative
# For TPM, need token counting...

# Option 3 code here...
```

---

## 🎯 Testing Plan

### Step 1: Test Option 1 with Small Dataset

**Command**:

```bash
python -m app.cli.graphrag --stage graph_extraction \
  --max 100 \
  --concurrency 10 \
  --read-db-name mongo_hack \
  --write-db-name validation_db \
  --log-file logs/extraction_concurrent_test.log \
  --verbose
```

**Expected**:

- Duration: ~1 minute (100 chunks / 600 per min)
- Results: 100 chunks extracted
- Errors: None
- Database: Results in validation_db.video_chunks

**Validation**:

```python
# Check results
python -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))

# Check validation_db
validation_db = client['validation_db']
extracted = validation_db.video_chunks.count_documents({
    'graphrag_extraction.status': 'completed'
})
failed = validation_db.video_chunks.count_documents({
    'graphrag_extraction.status': 'failed'
})

print(f'Extracted: {extracted}')
print(f'Failed: {failed}')
print(f'✓ Concurrent processing working' if extracted > 0 else '✗ No results')
"
```

---

### Step 2: Test Option 1 with Full Dataset

**Command**:

```bash
python -m app.cli.graphrag --stage graph_extraction \
  --max 100000 \
  --concurrency 10 \
  --read-db-name mongo_hack \
  --write-db-name validation_db \
  --log-file logs/extraction_concurrent_full.log \
  --verbose
```

**Expected**:

- Duration: ~6 hours (13,031 chunks with 10 workers)
- Speedup: 10x faster than sequential

---

### Step 3: Implement Option 3 (After Option 1 Validates)

**Enhancements**:

- Token tracking per request
- Dynamic rate limiting based on TPM
- Adaptive worker count
- Maximum throughput (1,000 chunks/min)

**Expected**:

- Duration: ~13 minutes for 13k chunks ✅

---

## 📋 Implementation Checklist

### Option 1 (Implemented) ✅

- [x] Import run_llm_concurrent
- [x] Override run() method
- [x] Add \_run_concurrent() method
- [x] Add \_store_concurrent_results() method
- [x] Support read/write DB separation
- [x] Add logging
- [x] Error handling

### Ready to Test

- [ ] Test with --max 100 (validate correctness)
- [ ] Compare results to sequential
- [ ] Test with full dataset
- [ ] Measure actual speedup

### Option 3 (Next)

- [ ] Implement token estimation
- [ ] Add TPM rate limiter
- [ ] Add token tracking per chunk
- [ ] Test with higher concurrency
- [ ] Validate 1M TPM limit handling

---

**Implementation**: ✅ Complete for Option 1  
**Ready**: To test with --max 100 → validation_db  
**Next**: After validation, implement Option 3 for maximum speed
