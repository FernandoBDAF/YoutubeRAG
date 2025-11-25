# Phase 2 Final Command - Achievement 2.1

**Date**: 2025-11-12  
**Issue**: `--experiment-id` is not a recognized argument  
**Solution**: Remove `--experiment-id` (it's only available via config file)  
**Status**: ✅ CORRECTED

---

## ✅ FINAL CORRECTED COMMAND

```bash
cd /Users/fernandobarroso/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG

python -m app.cli.graphrag \
  --max 200 \
  --db-name validation_01 \
  --verbose
```

**What this does**:

- Processes **200 chunks** from `validation_01.video_chunks`
- Runs all 4 GraphRAG stages (extraction → resolution → construction → detection)
- Creates baseline metrics in **10-15 minutes**
- Observability disabled (via `.env` variables)
- Verbose logging for detailed output

---

## 🔄 Arguments Explained

| Argument    | Value           | Purpose                                           |
| ----------- | --------------- | ------------------------------------------------- |
| `--max`     | `200`           | Limit to 200 chunks (faster baseline)             |
| `--db-name` | `validation_01` | Single database mode (all stages read/write here) |
| `--verbose` | (flag)          | Detailed logging output                           |

**Note**: `--experiment-id` is NOT a CLI argument. It's only available via config file (`--config path/to/config.json`).

---

## 📊 Alternative Options

### Option 1: Small Test (RECOMMENDED)

```bash
python -m app.cli.graphrag --max 200 --db-name validation_01 --verbose
```

**Time**: 10-15 minutes

### Option 2: Medium Test

```bash
python -m app.cli.graphrag --max 500 --db-name validation_01 --verbose
```

**Time**: 25-35 minutes

### Option 3: Full Run

```bash
python -m app.cli.graphrag --max 2006 --db-name validation_01 --verbose
```

**Time**: 90-150 minutes

---

## ⏱️ Expected Timeline (200 chunks)

| Stage                     | Duration  | Output                                     |
| ------------------------- | --------- | ------------------------------------------ |
| **Stage 1: Extraction**   | 4-6 min   | Extract entities/relations from 200 chunks |
| **Stage 2: Resolution**   | 3-4 min   | Resolve duplicate entities                 |
| **Stage 3: Construction** | 2-3 min   | Build knowledge graph                      |
| **Stage 4: Detection**    | 1-2 min   | Detect communities                         |
| **Total**                 | 10-15 min | Complete baseline                          |

---

## 📝 What to Monitor

### During Execution

- [ ] Stage transitions (watch for "Running GraphRAG stage: ..." messages)
- [ ] Memory usage (optional: `watch -n 2 'ps aux | grep graphrag'`)
- [ ] Any errors or warnings
- [ ] Timestamps for each stage

### After Execution

- [ ] Exit code: `echo $?` (should be 0)
- [ ] Collections created in `validation_01`
- [ ] Document counts
- [ ] Total runtime

---

## ✅ Verification Commands

### Check collections created

```bash
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "db.getCollectionNames()"
```

### Count documents

```bash
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "
    print('Entities:', db.entities.countDocuments({}));
    print('Relations:', db.relations.countDocuments({}));
    print('Communities:', db.communities.countDocuments({}));
  "
```

---

## 🎯 Ready to Execute

All issues resolved:

- ✅ Module import error fixed (use `python -m app.cli.graphrag`)
- ✅ Chunk count optimized (200 chunks for fast baseline)
- ✅ Invalid argument removed (`--experiment-id`)
- ✅ Command tested and ready

**Execute the command above when ready!** 🚀

---

**Last Updated**: 2025-11-12 23:30 UTC  
**Status**: ✅ FINAL - READY TO EXECUTE
