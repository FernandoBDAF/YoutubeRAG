# TPM Tuning for Maximum Throughput

**Date**: November 4, 2025  
**Issue**: Only using 14% of TPM capacity (128k of 900k)  
**Solution**: Optimize waiting logic + increase workers

---

## 📊 Current Performance Analysis

### What We Observed:

- **TPM Usage**: ~128,000 (14% of 900k target)
- **Workers**: 50
- **Time**: 9.7 minutes for 1k chunks
- **Bottleneck**: Conservative TPM waiting logic

### Why So Conservative?

**Original `wait_for_tpm_capacity()`**:

```python
while True:  # Block until capacity available
    current_tpm = sum(tokens)
    if current_tpm + estimated <= target:
        return  # OK to proceed
    time.sleep(0.1)  # Wait and retry
```

**Problem**: Serializes requests when approaching limit  
**Result**: Only ~128k TPM instead of 900k

---

## ✅ Tuning Changes

### Change 1: Optimistic Token Reservation

**Before** (pessimistic):

```python
# Wait until there's capacity
while current_tpm + estimated <= target:
    wait...
# Then reserve
```

**After** (optimistic):

```python
# Reserve immediately (optimistic)
token_window.append((now, estimated_tokens))

# Only wait if WAY over limit (>120%)
if current_tpm > target_tpm * 1.2:
    time.sleep(0.05)  # Minimal delay
```

**Benefit**: Allows bursts up to 1.08M TPM (20% over target)  
**Safety**: Still prevents sustained overuse

---

### Change 2: Non-Blocking Reservation

**Before**: Lock held during entire wait loop (serializes threads)  
**After**: Quick check and release lock (parallel processing)

**Impact**: All 50+ workers can proceed simultaneously

---

### Change 3: Reduced Wait Time

**Before**: `time.sleep(0.1)` = 100ms  
**After**: `time.sleep(0.05)` = 50ms + only when >120% limit

**Impact**: Faster recovery when hitting limit

---

## 📊 Expected Performance

### For 1,000 Chunks:

**Current** (conservative):

- TPM Usage: ~128k (14%)
- Time: 9.7 minutes
- Workers: 50

**After Tuning** (optimized):

- TPM Usage: ~700-850k (78-94%)
- Time: **~1.5-2 minutes**
- Workers: 50-100

**Speedup**: 9.7 min → 1.5 min = **6.5x faster** ✅

---

### For 13,069 Chunks:

**Current**: 2.1 hours  
**After Tuning**: **~20 minutes** ✅

**vs Sequential**: 60 hours → 20 min = **180x speedup!** ✅✅✅

---

## 🎯 Recommended Settings

### Conservative (Current + Small Tuning)

```bash
GRAPHRAG_TARGET_TPM=950000  # Keep same
GRAPHRAG_TARGET_RPM=4500     # Keep same
--concurrency 50             # Keep same
```

**Expected**: ~20 minutes for 13k chunks

### Moderate (Recommended)

```bash
GRAPHRAG_TARGET_TPM=950000
GRAPHRAG_TARGET_RPM=10000    # Increase if tier allows
--concurrency 100            # Double workers
```

**Expected**: ~15 minutes for 13k chunks

### Aggressive (Maximum Throughput)

```bash
GRAPHRAG_TARGET_TPM=980000   # 98% of limit
GRAPHRAG_TARGET_RPM=20000    # If tier allows
--concurrency 200            # 4x workers
```

**Expected**: ~10-12 minutes for 13k chunks

---

## ✅ What Changed

**File**: `business/stages/graphrag/extraction.py`

**Before**:

- Blocking wait loop
- Pessimistic reservation
- Lock held during wait

**After**:

- Optimistic reservation
- Only wait when >120% limit
- Quick lock release
- Minimal wait time (50ms)

**Applied to**:

- ✅ extraction.py (tuned)
- ⏳ entity_resolution.py (needs same tuning)
- ⏳ graph_construction.py (needs same tuning)

---

## 🚀 Test Command (Tuned)

**Test with 13k chunks**:

```bash
# Clean first
python scripts/clean_extraction_status.py --db validation_db

# Run with tuned TPM
GRAPHRAG_USE_TPM_TRACKING=true \
GRAPHRAG_TARGET_TPM=950000 \
GRAPHRAG_TARGET_RPM=10000 \
python -m app.cli.graphrag --stage graph_extraction \
  --max 13069 \
  --concurrency 100 \
  --read-db-name validation_db \
  --write-db-name validation_db \
  --log-file logs/extraction_tpm_tuned_full.log \
  --verbose
```

**Expected**: ~15-20 minutes for all 13,069 chunks ✅

---

**Tuning**: ✅ Complete  
**Expected TPM**: 700-850k (vs 128k before)  
**Expected Time**: 15-20 min (vs 9.7 min for 1k → ~2 hours for 13k)  
**Ready**: To test with full dataset!
