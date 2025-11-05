# Ultra-Simple Command - All Defaults Optimized

**Date**: November 4, 2025  
**Status**: ✅ All optimizations are now defaults  
**No configuration needed!**

---

## ✅ **New Defaults (After Validation)**

### **Validated and Set as Defaults**:

1. ✅ **TPM Tracking**: Enabled by default

   - `GRAPHRAG_USE_TPM_TRACKING=true` (default)
   - Can disable: `GRAPHRAG_USE_TPM_TRACKING=false`

2. ✅ **Concurrency**: 300 workers by default

   - `GRAPHRAG_EXTRACTION_CONCURRENCY=300` (default)
   - `GRAPHRAG_RESOLUTION_CONCURRENCY=300` (default)
   - Can override: `--concurrency <number>`

3. ✅ **Rate Limits**: Validated settings

   - TPM: 950,000 (default)
   - RPM: 20,000 (default)

4. ✅ **Batch Size**: Dynamic

   - 300 workers → 600 batch size
   - Scales automatically

5. ✅ **Log Files**: Auto-named with stage and timestamp
   - Format: `logs/pipeline/graphrag_STAGE_TIMESTAMP.log`
   - Example: `logs/pipeline/graphrag_full_pipeline_20241104_153045.log`

---

## 🚀 **Ultra-Simple Command**

### **For Full Pipeline** (13,069 chunks):

```bash
python -m app.cli.graphrag \
  --max 13069 \
  --read-db-name validation_db \
  --write-db-name validation_db \
  --verbose
```

**That's it!** ✅

No concurrency flag, no log file, no TPM env vars - all optimized defaults!

---

### **What Happens Automatically**:

**Processing**:

- ✅ 300 workers (concurrent)
- ✅ TPM tracking enabled
- ✅ 950k TPM, 20k RPM limits
- ✅ 600-chunk batches
- ✅ Safety saves every batch

**Logging**:

- ✅ Auto-created: `logs/pipeline/graphrag_full_pipeline_20241104_153045.log`
- ✅ Verbose mode enabled
- ✅ All stages logged

**Expected Time**: ~2 hours for 13,069 chunks

---

## 🎯 **For Single Stage** (optional):

### **Extraction only**:

```bash
python -m app.cli.graphrag \
  --stage graph_extraction \
  --max 13069 \
  --read-db-name validation_db \
  --write-db-name validation_db
```

**Auto log**: `logs/pipeline/graphrag_graph_extraction_20241104_153100.log`

---

### **Entity Resolution only**:

```bash
python -m app.cli.graphrag \
  --stage entity_resolution \
  --max 13069 \
  --read-db-name validation_db \
  --write-db-name validation_db
```

**Auto log**: `logs/pipeline/graphrag_entity_resolution_20241104_153200.log`

---

## 📊 **Performance Summary**

| Configuration      | Before         | After (Optimized) | Change            |
| ------------------ | -------------- | ----------------- | ----------------- |
| **TPM Tracking**   | Manual         | **Auto** ✅       | Default enabled   |
| **Workers**        | 1 (manual set) | **300** ✅        | Default 300       |
| **Batch Size**     | 100            | **600** ✅        | Dynamic scaling   |
| **RPM**            | 4,500          | **20,000** ✅     | Validated default |
| **Log File**       | Manual path    | **Auto** ✅       | Stage + timestamp |
| **Command Length** | ~8 lines       | **4 lines** ✅    | Ultra-simple      |

---

## ✅ **Previous vs New Command**

### **Before** (manual configuration):

```bash
GRAPHRAG_USE_TPM_TRACKING=true \
GRAPHRAG_TARGET_TPM=950000 \
GRAPHRAG_TARGET_RPM=20000 \
python -m app.cli.graphrag \
  --max 13069 \
  --concurrency 300 \
  --read-db-name validation_db \
  --write-db-name validation_db \
  --log-file logs/graphrag_full_13k_optimized.log \
  --verbose
```

### **Now** (all defaults):

```bash
python -m app.cli.graphrag \
  --max 13069 \
  --read-db-name validation_db \
  --write-db-name validation_db \
  --verbose
```

**Improvement**: 8 lines → 4 lines, same performance! ✅

---

## 🎯 **Script Alternative**

```bash
./RUN-FULL-PIPELINE.sh
```

Also updated to use minimal command!

---

**Defaults**: ✅ 300 workers, TPM=true, 20k RPM, auto log files  
**Command**: ✅ **Ultra-simple - 4 lines**  
**Performance**: ✅ Same 2-hour runtime  
**Ready**: Run now! 🚀
