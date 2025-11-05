# Pipeline Running in Sequential Mode - Issue

**Date**: November 4, 2025  
**Issue**: Pipeline running SEQUENTIALLY instead of concurrent  
**Cause**: --concurrency flag not passed or not working

---

## 🐛 The Problem

**From log** (line 25):

```
Using SEQUENTIAL processing: 1000 chunks
```

**NOT**:

```
Using ADVANCED TPM TRACKING: 1000 chunks with 300 workers
```

---

## 🔍 Why This Happens

**Sequential mode triggers when**:

```python
use_concurrent = self.config.concurrency and self.config.concurrency > 1

if use_concurrent and use_tpm_tracking:
    # TPM mode
elif use_concurrent:
    # Concurrent mode
else:
    # SEQUENTIAL mode ← Currently here!
```

**Causes**:

1. `--concurrency` flag not passed
2. Concurrency is None or 1
3. Config not reading concurrency correctly

---

## ✅ Solution

**You need to pass** `--concurrency 300`:

```bash
python -m app.cli.graphrag \
  --max 13069 \
  --concurrency 300 \  # ← REQUIRED!
  --read-db-name validation_db \
  --write-db-name validation_db \
  --verbose
```

---

## 📊 Performance Impact

### Sequential (current):

- Processing: 1 chunk at a time
- Time per chunk: ~15 seconds
- 1000 chunks: **~4.2 hours** ❌
- 13,069 chunks: **~55 hours** ❌

### Concurrent 300 workers (should be):

- Processing: 300 chunks simultaneously
- Time per chunk: ~0.25 seconds
- 1000 chunks: **~4 minutes** ✅
- 13,069 chunks: **~55 minutes** ✅

**Difference**: 55 hours vs 55 minutes = **60x slower!** ❌

---

## 🚨 Action Required

**STOP the current run** (Ctrl+C) and restart with:

```bash
python -m app.cli.graphrag \
  --max 13069 \
  --concurrency 300 \
  --read-db-name validation_db \
  --write-db-name validation_db \
  --verbose
```

**Why the default didn't work**:

- Environment config uses env vars, not CLI defaults
- CLI `--concurrency` must be explicitly passed
- Can't default in argparse without breaking backwards compatibility

---

**Fix**: Add --concurrency 300 to command  
**Time**: Will drop from 55 hours to 55 minutes ✅
