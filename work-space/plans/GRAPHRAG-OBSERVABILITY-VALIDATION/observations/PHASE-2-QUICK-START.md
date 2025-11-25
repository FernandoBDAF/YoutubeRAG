# Phase 2 Quick Start - Pipeline Execution

**Achievement**: 2.1 - Baseline Pipeline Run  
**Status**: 🟢 READY TO EXECUTE

---

## 🚀 Execute This Command

```bash
cd /Users/fernandobarroso/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG

python business/pipelines/graphrag.py \
  --db-name validation_01 \
  --experiment-id baseline-no-observability \
  --stages all
```

---

## 📊 What Happens

1. **Stage 1 (Extraction)**: Extracts entities/relations from 2006 video_chunks
2. **Stage 2 (Resolution)**: Resolves entity duplicates and creates entities collection
3. **Stage 3 (Construction)**: Builds knowledge graph with relations
4. **Stage 4 (Detection)**: Detects communities in the graph

**Result**: New collections in `validation_01`:

- `entities`
- `relations`
- `communities`

---

## ⏱️ Expected Time

**90-150 minutes** (1.5 - 2.5 hours)

---

## 📈 Monitor (Optional)

In a separate terminal:

```bash
watch -n 2 'ps aux | grep graphrag.py && echo "---" && free -h'
```

---

## ✅ Phase 1 Status

- ✅ `video_chunks` collection copied (2006 documents)
- ✅ Environment variables set
- ✅ Disk space verified (14GB available)
- ✅ MongoDB connected
- ✅ **READY FOR PHASE 2**

---

## 📝 After Execution (Phase 3)

1. Record the exit code: `echo $?`
2. Count new collections:
   ```bash
   mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
     --eval "db.entities.countDocuments()"
   ```
3. Calculate runtime
4. Document results

---

## 🎯 You're Set!

Everything is ready. Execute the command above when you're ready to start.

---

**Last Updated**: 2025-11-12 23:15 UTC  
**Status**: ✅ READY TO EXECUTE
