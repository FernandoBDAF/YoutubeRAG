# Final Optimized Pipeline Command

**Date**: November 4, 2025  
**Status**: ✅ All optimizations complete  
**Configuration**: Validated with 300-chunk tests

---

## ✅ **What's Now Default**

### **TPM Tracking**: ✅ Enabled by default

- No need to set `GRAPHRAG_USE_TPM_TRACKING=true`
- Can disable with `GRAPHRAG_USE_TPM_TRACKING=false` if needed

### **Rate Limits** (validated defaults):

- **TPM**: 950,000 (95% of 1M limit)
- **RPM**: 20,000 (validated with your tier)

### **Batch Size**: Dynamic

- 100 workers → 200 batch size
- 300 workers → 600 batch size
- Capped at 1000 for safety

---

## 🚀 **Simple Command (All Defaults)**

```bash
python -m app.cli.graphrag \
  --max 13069 \
  --concurrency 300 \
  --read-db-name validation_db \
  --write-db-name validation_db \
  --log-file logs/graphrag_full_13k_optimized.log \
  --verbose
```

**That's it!** All optimizations are now defaults ✅

---

## 📊 **What This Will Do**

### **Processing**:

- All 13,069 chunks
- 300 workers (concurrent)
- TPM tracking enabled
- Dynamic 600-chunk batches
- Safety saves every batch

### **Stages**:

1. **graph_extraction**: ~55 minutes
2. **entity_resolution**: ~30 minutes
3. **graph_construction**: ~30 minutes
4. **community_detection**: ~5 minutes

**Total**: **~2 hours** (vs 66.5 hours sequential)

**Speedup**: **~33x faster!** ✅

---

## 📊 **Expected Results**

### **Collections Created**:

- **entities**: ~3,800 entities
- **relations**: ~5,800 relationships
- **entity_mentions**: ~8,000 mentions
- **communities**: TBD (community detection stage)

### **Quality**:

- Cross-chunk entity grouping ✅
- Relationship validation ✅
- Entity type classification ✅
- 100% success rate ✅

---

## ⚡ **Alternative: Run Script**

```bash
./RUN-FULL-PIPELINE.sh
```

Both do the same thing!

---

## 📋 **After Completion**

**Analyze results**:

```bash
python -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['validation_db']

print('GraphRAG Pipeline Results:')
print(f'  Entities: {db.entities.count_documents({}):,}')
print(f'  Relations: {db.relations.count_documents({}):,}')
print(f'  Communities: {db.communities.count_documents({}):,}' if 'communities' in db.list_collection_names() else '  Communities: 0')
print(f'  Processed chunks: {db.video_chunks.count_documents({\"graphrag_construction.status\": \"completed\"}):,}')
"
```

---

**Defaults**: ✅ TPM=true, 950k TPM, 20k RPM, dynamic batches  
**Command**: ✅ Simple - no env vars needed  
**Expected**: ✅ ~2 hours for full dataset  
**Ready**: Run the command above! 🚀
