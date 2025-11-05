# 300 Workers Test Analysis

**Date**: November 4, 2025  
**Test**: 200 chunks with 300 workers  
**Issue**: Batch size capping at 100

---

## 📊 Test Results (300 Workers)

### From extraction_tpm_extraction.log:

**Configuration**:

- Workers: 300 ✅
- RPM: 20,000 ✅
- TPM: 950,000 ✅

**Performance**:

- Batch 1: 100 chunks in 38.0s (line 111)
- Batch 2: 100 chunks in 39.7s (line 316)
- **Total**: 200 chunks in 87.4s = **1.5 minutes**
- **Per chunk**: 0.44s average
- **TPM**: ~128k (still conservative)

---

## 🐛 The Problem

### Why Only 100 at a Time?

**Current code** (line ~597 in extraction.py):

```python
batch_size = 100  # Write every 100 chunks
```

**Result**:

- Batch 1: Process 100 chunks with 300 workers (only uses 100 workers)
- Batch 2: Process 100 chunks with 300 workers (only uses 100 workers)
- **300 workers never fully utilized!**

---

## ✅ The Solution

### Option 1: Increase Batch Size (RECOMMENDED)

**Change**:

```python
batch_size = min(500, total)  # Process up to 500 at once
```

**Benefit**:

- With 300 workers, process 300 chunks simultaneously
- Batch safety still maintained (save every 500)
- Much faster

**Expected**: 200 chunks in **~30-40 seconds** (vs 87s now)

---

### Option 2: Dynamic Batch Size Based on Workers

**Change**:

```python
# Scale batch size with workers
batch_size = min(int(self.config.concurrency) * 3, 1000)
# 100 workers → 300 batch size
# 300 workers → 900 batch size
```

**Benefit**:

- Automatically scales
- Maximizes worker utilization
- Still has safety limit (1000 max)

---

## 📊 Expected Performance with Fix

### Current (300 workers, batch_size=100):

- 200 chunks = 87.4s
- 13,069 chunks = **1.9 hours**

### After Fix (300 workers, batch_size=500):

- 200 chunks = ~30s ✅
- 13,069 chunks = **~32 minutes** ✅

**Speedup**: 1.9h → 32min = **3.5x faster!** ✅

---

## 🎯 Recommended Changes

### For All 3 Stages:

**extraction.py**:

```python
# Line 597
batch_size = min(int(self.config.concurrency) * 2, 1000)
```

**entity_resolution.py**:

```python
# Line ~615
batch_size = min(int(self.config.concurrency) * 2, 1000)
```

**graph_construction.py**:

```python
# Line ~1410
batch_size = min(int(self.config.concurrency) * 2, 1000)
```

**Logic**:

- 10 workers → 20 batch size (safe for small tests)
- 50 workers → 100 batch size
- 100 workers → 200 batch size
- 300 workers → 600 batch size ✅
- Capped at 1000 for safety

---

## ⚠️ Safety Considerations

### Why Keep Batch Saves?

**Risk with large batches**:

- If crash after 5,000 chunks processed but not saved → lose all work
- With batch saves, worst case lose 1 batch

**Recommendation**:

- Batch size of 500-1000 is safe ✅
- Still provides safety checkpoints
- Balances performance vs data safety

---

**Issue**: Batch size hardcoded to 100  
**Solution**: Scale with workers (workers × 2)  
**Expected**: 3.5x faster with fix!
