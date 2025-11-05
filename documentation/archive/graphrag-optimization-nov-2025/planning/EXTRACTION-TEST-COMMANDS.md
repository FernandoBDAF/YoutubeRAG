# Extraction Concurrent Processing - Test Commands

**Date**: November 3, 2025  
**Status**: ✅ Option 1 implemented, ready to test  
**Goal**: Validate 10x speedup, then move to Option 3

---

## 🧪 Test 1: Small Validation (RECOMMENDED FIRST)

**Purpose**: Validate concurrent processing works correctly

**Command**:

```bash
python -m app.cli.graphrag --stage graph_extraction \
  --max 100 \
  --concurrency 10 \
  --read-db-name mongo_hack \
  --write-db-name validation_db \
  --log-file logs/extraction_concurrent_100.log \
  --verbose
```

**Expected Duration**: ~1 minute (100 chunks @ 600/min)

**What to Check**:

```bash
# 1. Check logs for concurrent processing
grep "CONCURRENT processing\|Launching concurrent\|Completed LLM calls" logs/extraction_concurrent_100.log

# 2. Verify results in validation_db
python -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
validation_db = client['validation_db']

extracted = validation_db.video_chunks.count_documents({'graphrag_extraction.status': 'completed'})
failed = validation_db.video_chunks.count_documents({'graphrag_extraction.status': 'failed'})
total = extracted + failed

print(f'Results in validation_db:')
print(f'  Extracted: {extracted}/{total} ({extracted/total*100 if total else 0:.1f}%)')
print(f'  Failed: {failed}/{total} ({failed/total*100 if total else 0:.1f}%)')
print(f'')
print(f'✅ Success!' if extracted > 90 else '⚠️  Check for issues')
"
```

---

## 🧪 Test 2: Full Dataset with 10 Workers

**Purpose**: Validate full-scale performance improvement

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

**Expected Duration**: ~6 hours (10x faster than 60 hours)

**What to Monitor** (while running):

```bash
# Watch progress
tail -f logs/extraction_concurrent_full.log | grep -E "Completed LLM calls|Stored.*results"

# Check current count
python -c "from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv(); client = MongoClient(os.getenv('MONGODB_URI')); validation_db = client['validation_db']; print(f'Extracted so far: {validation_db.video_chunks.count_documents({\"graphrag_extraction.status\": \"completed\"})}')"
```

---

## 🧪 Test 3: Compare Sequential vs Concurrent

**Purpose**: Measure actual speedup

**Sequential Baseline** (for comparison):

```bash
# Run 100 chunks WITHOUT concurrency
python -m app.cli.graphrag --stage graph_extraction \
  --max 100 \
  --read-db-name mongo_hack \
  --write-db-name test_sequential \
  --log-file logs/extraction_sequential_100.log
# Note: No --concurrency flag = sequential

# Time this and compare to concurrent
```

**Compare**:

```bash
# Sequential time
grep "Summary:" logs/extraction_sequential_100.log

# Concurrent time
grep "Completed LLM calls" logs/extraction_concurrent_100.log

# Calculate speedup
```

---

## 🚀 After Validation: Option 3 Implementation

**If Option 1 works well**, implement advanced version:

### Option 3: Maximum Throughput (1M TPM)

**Enhanced Code** (to be added):

```python
from core.libraries.rate_limiting import RateLimiter

def _run_concurrent_advanced(self, docs):
    """Advanced concurrent with token tracking for 1M TPM."""

    # Create rate limiters
    rpm_limiter = RateLimiter(rpm=4500, name="openai_rpm")  # Requests

    # Token tracking wrapper
    def extract_with_tracking(chunk):
        rpm_limiter.wait()

        # Estimate tokens (rough)
        text_length = len(chunk.get('chunk_text', ''))
        estimated_input_tokens = text_length / 4  # ~4 chars per token
        estimated_output_tokens = 1000  # Average for extraction
        estimated_total = estimated_input_tokens + estimated_output_tokens

        # TODO: Implement TPM limiter based on estimated_total

        result = agent.extract_from_chunk(chunk)
        return result

    # Use higher concurrency
    results = run_concurrent_with_limit(
        func=extract_with_tracking,
        items=docs,
        max_workers=50  # Much higher!
    )

    # ... store results
```

**Expected**: 13,031 chunks in ~13-20 minutes ✅

---

## 📊 Performance Expectations

### Option 1 (Current Implementation)

| Test  | Chunks | Workers | QPS | Expected Time | Speedup |
| ----- | ------ | ------- | --- | ------------- | ------- |
| Small | 100    | 10      | 10  | ~1 min        | -       |
| Full  | 13,031 | 10      | 10  | ~6 hours      | 10x     |

### Option 3 (After Validation)

| Test  | Chunks | Workers | TPM | Expected Time | Speedup |
| ----- | ------ | ------- | --- | ------------- | ------- |
| Small | 100    | 50      | 1M  | ~6 sec        | -       |
| Full  | 13,031 | 50      | 1M  | ~13 min       | 277x ✅ |

---

## ✅ Ready to Test

**Implementation Status**: ✅ Complete for Option 1  
**Command Ready**: Test with --max 100 first  
**Database**: Reads from mongo_hack, writes to validation_db  
**Next**: Run test command above and validate results!
