# Phase 2 Corrected Commands - Achievement 2.1

**Date**: 2025-11-12  
**Issue**: Module import error when running `python business/pipelines/graphrag.py`  
**Solution**: Use `python -m app.cli.graphrag` instead  
**Status**: ✅ CORRECTED

---

## 🔧 Issue Identified

**Error**:

```
ModuleNotFoundError: No module named 'core'
```

**Root Cause**: Running the pipeline script directly doesn't set up the Python path correctly. The project uses a CLI module approach.

**Correct Approach**: Use `python -m app.cli.graphrag` which properly sets up the module path.

---

## ✅ Corrected Commands

### Option 1: Small Test Run (RECOMMENDED for baseline)

**Process 200 chunks** (~10-15 minutes):

```bash
cd /Users/fernandobarroso/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG

python -m app.cli.graphrag \
  --max 200 \
  --db-name validation_01 \
  --experiment-id baseline-no-observability-200 \
  --verbose
```

**Why 200 chunks?**

- ✅ Fast execution (~10-15 minutes vs 90-150 minutes)
- ✅ Sufficient for baseline metrics
- ✅ Tests all 4 stages
- ✅ Provides comparison data
- ✅ Saves time and resources

---

### Option 2: Medium Test Run

**Process 500 chunks** (~25-35 minutes):

```bash
python -m app.cli.graphrag \
  --max 500 \
  --db-name validation_01 \
  --experiment-id baseline-no-observability-500 \
  --verbose
```

---

### Option 3: Full Run (All 2006 chunks)

**Process all 2006 chunks** (~90-150 minutes):

```bash
python -m app.cli.graphrag \
  --max 2006 \
  --db-name validation_01 \
  --experiment-id baseline-no-observability-full \
  --verbose
```

**Note**: Only use this if you need comprehensive baseline data. For comparison purposes, 200-500 chunks is usually sufficient.

---

## 📊 Comparison: Chunk Counts

| Option     | Chunks | Time       | Use Case                            |
| ---------- | ------ | ---------- | ----------------------------------- |
| **Small**  | 200    | 10-15 min  | ✅ **Recommended** - Quick baseline |
| **Medium** | 500    | 25-35 min  | More data points                    |
| **Full**   | 2006   | 90-150 min | Complete dataset                    |

---

## 🎯 Recommendation: Start with 200 Chunks

**Why?**

1. **Fast Feedback**: Get baseline metrics in 10-15 minutes
2. **Resource Efficient**: Uses less disk space (97% capacity)
3. **Sufficient Data**: 200 chunks provides meaningful metrics
4. **Easy Comparison**: Achievement 2.2 (with observability) can use same 200 chunks
5. **Iterative Approach**: Can always run more if needed

**Baseline Metrics from 200 chunks**:

- Runtime (with observability disabled)
- Memory usage
- Storage requirements
- Success rate
- Entities/relations/communities created

**Then for Achievement 2.2**:

- Run same 200 chunks WITH observability enabled
- Compare metrics directly (apples-to-apples)
- Measure observability overhead

---

## ✅ Updated Phase 2 Command (RECOMMENDED)

```bash
cd /Users/fernandobarroso/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG

# Recommended: 200 chunks for quick baseline
python -m app.cli.graphrag \
  --max 200 \
  --db-name validation_01 \
  --experiment-id baseline-no-observability-200 \
  --verbose
```

**Expected Output**:

- Stage 1 (Extraction): Process 200 chunks
- Stage 2 (Resolution): Resolve entities
- Stage 3 (Construction): Build graph
- Stage 4 (Detection): Detect communities

**Expected Time**: 10-15 minutes

---

## 📝 What `--max 200` Does

From the code analysis:

- Limits pipeline to process **first 200 chunks** from `video_chunks` collection
- All 4 stages run on these 200 chunks
- Creates entities, relations, communities from this subset
- Provides representative baseline metrics

**Without `--max`**: Would process all 2006 chunks (~90-150 minutes)

---

## 🔄 Arguments Explained

| Argument          | Value                           | Purpose                               |
| ----------------- | ------------------------------- | ------------------------------------- |
| `--max`           | `200`                           | Limit to 200 chunks (faster baseline) |
| `--db-name`       | `validation_01`                 | Single database mode (all stages)     |
| `--experiment-id` | `baseline-no-observability-200` | Track this specific run               |
| `--verbose`       | (flag)                          | Detailed logging output               |

**Note**: Observability is disabled via `.env` variables (already set in Phase 1).

---

## ✅ Verification After Execution

```bash
# Count results
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "
    print('Entities:', db.entities.countDocuments({}));
    print('Relations:', db.relations.countDocuments({}));
    print('Communities:', db.communities.countDocuments({}));
  "
```

---

## 🎯 Next Steps

1. **Execute** the recommended command (200 chunks)
2. **Monitor** execution (should take 10-15 minutes)
3. **Record** metrics (runtime, memory, storage)
4. **Verify** collections created
5. **Document** results for Phase 3

---

**Last Updated**: 2025-11-12 23:20 UTC  
**Status**: ✅ CORRECTED - READY TO EXECUTE  
**Recommendation**: Use 200 chunks for fast, efficient baseline
