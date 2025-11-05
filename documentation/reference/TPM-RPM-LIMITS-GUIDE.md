# OpenAI Rate Limits and Configuration Guide

**Date**: November 4, 2025  
**Purpose**: Understand TPM/RPM limits and optimize for maximum throughput

---

## 📊 Current Code Defaults

### In All 3 Stages (extraction, entity_resolution, graph_construction):

```python
target_tpm = int(os.getenv("GRAPHRAG_TARGET_TPM", "950000"))
target_rpm = int(os.getenv("GRAPHRAG_TARGET_RPM", "4500"))
```

**Defaults**:

- TPM: 950,000 (95% of 1M limit)
- RPM: 4,500

**Configuration**: Can override via environment variables ✅

---

## 🎯 Do You Need to Set Them?

### Short Answer: **NO** (defaults are good!)

**Current defaults are already set in code**:

- If you DON'T set env vars → Uses 950k TPM, 4.5k RPM
- If you DO set env vars → Overrides defaults

### When to Override:

**Set GRAPHRAG_USE_TPM_TRACKING=true** (required):

```bash
export GRAPHRAG_USE_TPM_TRACKING=true  # Required to enable TPM mode
```

**Optional overrides**:

```bash
export GRAPHRAG_TARGET_TPM=980000      # If you want 98% of limit
export GRAPHRAG_TARGET_RPM=20000       # If your tier allows higher
```

---

## 📊 OpenAI Rate Limits by Tier

### Tier 1 (Free/Low Usage):

- **TPM**: 200,000
- **RPM**: 500
- **Concurrent**: Very limited

### Tier 2 (Moderate Usage):

- **TPM**: 2,000,000
- **RPM**: 5,000
- **Concurrent**: Good

### Tier 3 (High Usage):

- **TPM**: 10,000,000
- **RPM**: 10,000
- **Concurrent**: Excellent

### Tier 4 (Enterprise):

- **TPM**: 30,000,000+
- **RPM**: 30,000+
- **Concurrent**: Unlimited

**To check your tier**: OpenAI Dashboard → Settings → Limits

---

## ⚠️ Risks of Increasing RPM

### RPM = Requests Per Minute

**Current**: 4,500 RPM default (safe for Tier 1)

### Risks by Tier:

**If Tier 1 (500 RPM limit)**:

- Setting 10,000 RPM → **Will hit rate limit errors**
- OpenAI will return HTTP 429 (Too Many Requests)
- Processing will slow down (retries)

**If Tier 2+ (5,000+ RPM limit)**:

- Setting 10,000 RPM → **Safe if Tier 2+**
- Will use more of your quota
- Faster processing ✅

### How to Test Your Tier:

**Run small test with high RPM**:

```bash
GRAPHRAG_USE_TPM_TRACKING=true \
GRAPHRAG_TARGET_RPM=15000 \
python -m app.cli.graphrag --stage graph_extraction \
  --max 50 --concurrency 100 \
  --read-db-name validation_db --write-db-name validation_db
```

**Watch for**:

- HTTP 429 errors → You're over limit
- No errors → You can increase more

---

## 🚀 Testing 300 Workers

### Recommendations for 300 Worker Test:

**Conservative** (Recommended First):

```bash
# Clean first
python scripts/clean_graphrag_fields.py --db validation_db

# Test with 300 workers
GRAPHRAG_USE_TPM_TRACKING=true \
GRAPHRAG_TARGET_TPM=950000 \
GRAPHRAG_TARGET_RPM=15000 \
python -m app.cli.graphrag \
  --max 500 \
  --concurrency 300 \
  --read-db-name validation_db \
  --write-db-name validation_db \
  --log-file logs/graphrag_300workers_test.log \
  --verbose
```

**Expected**:

- If Tier 2+: Should work great, ~3-4x faster
- If Tier 1: May hit RPM limits

---

**Aggressive** (If conservative works):

```bash
GRAPHRAG_USE_TPM_TRACKING=true \
GRAPHRAG_TARGET_TPM=980000 \
GRAPHRAG_TARGET_RPM=25000 \
python -m app.cli.graphrag \
  --max 500 \
  --concurrency 300 \
  --read-db-name validation_db \
  --write-db-name validation_db \
  --log-file logs/graphrag_300workers_aggressive.log \
  --verbose
```

---

## 📊 Expected Results with 300 Workers

### Theoretical Maximum:

**If TPM is bottleneck** (current):

- 300 workers won't help much (still limited by TPM)
- Need to increase actual TPM utilization first

**If we reach 700-900k TPM**:

- 300 workers could process much faster
- Potential: **500 chunks in 30-45 seconds** (vs 100 in 60s)
- Full dataset: **~1 hour total**

---

## 🎯 Recommended Test Plan

### Test 1: Validate Current Tier Limits

```bash
# Small test with high RPM to check tier
GRAPHRAG_USE_TPM_TRACKING=true \
GRAPHRAG_TARGET_RPM=20000 \
python -m app.cli.graphrag --stage graph_extraction \
  --max 100 --concurrency 100 \
  --read-db-name validation_db --write-db-name validation_db \
  --log-file logs/tier_check.log
```

**Watch for**: HTTP 429 errors (rate limit exceeded)

---

### Test 2: 300 Workers (If Test 1 Passes)

```bash
python scripts/clean_graphrag_fields.py --db validation_db

GRAPHRAG_USE_TPM_TRACKING=true \
GRAPHRAG_TARGET_TPM=950000 \
GRAPHRAG_TARGET_RPM=15000 \
python -m app.cli.graphrag \
  --max 500 \
  --concurrency 300 \
  --read-db-name validation_db \
  --write-db-name validation_db \
  --log-file logs/graphrag_300w_500chunks.log \
  --verbose
```

**Expected**: 500 chunks in ~2-3 minutes (vs ~5 minutes with 100 workers)

---

## ✅ Configuration Summary

### Minimum (Already Works):

```bash
GRAPHRAG_USE_TPM_TRACKING=true  # Only this is required!
python -m app.cli.graphrag ...  # Uses defaults: 950k TPM, 4.5k RPM
```

### Recommended for Testing 300 Workers:

```bash
GRAPHRAG_USE_TPM_TRACKING=true \
GRAPHRAG_TARGET_RPM=15000 \  # Test higher RPM
python -m app.cli.graphrag \
  --max 500 \
  --concurrency 300 \
  ...
```

### Aggressive (If Tier 3+):

```bash
GRAPHRAG_USE_TPM_TRACKING=true \
GRAPHRAG_TARGET_TPM=980000 \
GRAPHRAG_TARGET_RPM=25000 \
python -m app.cli.graphrag \
  --concurrency 300 \
  ...
```

---

**Answer**: You only need `GRAPHRAG_USE_TPM_TRACKING=true`!  
**Defaults**: 950k TPM, 4.5k RPM (already in code)  
**Test**: Ready for 300 worker test! 🚀
