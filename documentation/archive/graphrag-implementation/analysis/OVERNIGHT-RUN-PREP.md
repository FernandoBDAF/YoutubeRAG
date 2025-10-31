# Overnight Run Preparation - GraphRAG 13k Chunks

## Date: October 31, 2025

---

## ✅ Implementation Complete

All critical fixes have been implemented:

1. ✅ **Adaptive Cross-Chunk Window** - Auto-adjusts to video length
2. ✅ **Increased Semantic Similarity Threshold** - 0.92 (stricter)
3. ✅ **Edge Weights** - Prioritizes high-quality relationships
4. ✅ **Density Safeguards** - Stops if density > 0.3

---

## 🧪 Validation Test First (12 Chunks)

### Step 1: Ensure `.env` is Configured

**CHECK YOUR `.env` FILE** - Make sure:

```bash
# LEAVE THIS COMMENTED OUT for adaptive window (RECOMMENDED):
# GRAPHRAG_CROSS_CHUNK_WINDOW=5

# OR remove the line entirely - adaptive is the new default!
```

**If the line exists and is NOT commented, the adaptive window won't work!**

### Step 2: Clean Data

```bash
python scripts/full_cleanup.py
```

### Step 3: Run 12-Chunk Validation

```bash
python run_graphrag_pipeline.py --max 12 --log-file logs/pipeline/graphrag_adaptive.log --verbose
```

### Step 4: Check Results

**Watch for this in the logs**:

```
Video ZA-tUyM_y7s: 12 chunks, using adaptive window=2  ← Should say window=2!
✓ Added ~30-60 cross-chunk relationships (density: 0.20-0.30)  ← Much better!
```

**Expected Results**:

- Cross-chunk: ~30-60 (not 412!)
- Final density: 0.20-0.30 (not 0.83!)
- Communities: 3-8 (not 0!)

---

## 🌙 Overnight Run (13k Chunks)

### ONLY Run If 12-Chunk Validation Passes!

**Success Criteria for Validation**:

- ✅ Adaptive window=2 logged
- ✅ Cross-chunk < 100 relationships
- ✅ Density < 0.30
- ✅ Communities detected > 0

### If Validation Passes:

```bash
# Full 13k chunk run
python run_graphrag_pipeline.py --log-file logs/pipeline/graphrag_full.log --verbose
```

**Expected Runtime**: 2-4 hours for 13k chunks

**Monitor** (optional, in separate terminal):

```bash
tail -f logs/pipeline/graphrag_full.log | grep -E "density:|communities|Progress:"
```

---

## 📊 Expected Results for 13k Chunks

### Assuming ~100 Videos

| Metric          | Estimated      | Notes                        |
| --------------- | -------------- | ---------------------------- |
| Entities        | 3,000-5,000    | Depends on content diversity |
| Relationships   | 50,000-100,000 | With all post-processing     |
| Graph Density   | 0.15-0.25      | Healthy range                |
| Communities     | 50-200         | Meaningful clusters          |
| Processing Time | 2-4 hours      | Mostly LLM calls             |
| Database Size   | 100-500 MB     | Reasonable                   |

### Per-Video Adaptive Windows

**Example** (assuming mixed video lengths):

- 20 short videos (~10 chunks): window=1
- 50 medium videos (~30 chunks): window=3
- 30 long videos (~100 chunks): window=5

**Relationships**:

- LLM extracted: ~15,000
- Co-occurrence: ~20,000
- Cross-chunk: ~30,000 (adaptive windows prevent over-connection)
- Semantic similarity: ~5,000
- Bidirectional: ~15,000
- Predicted: ~5,000
- **Total**: ~90,000

---

## 🚨 What to Watch For

### Good Signs ✅

- Logs show different windows for different videos
- Density increases gradually (0.05 → 0.10 → 0.15 → 0.20)
- No early termination warnings
- Communities detected for most/all chunks

### Warning Signs ⚠️

- Density warnings before all post-processing steps complete
- Cross-chunk adding >500 relationships per video
- Any density > 0.5 at any point

### Stop and Debug If 🔴

- Density exceeds 0.8 during post-processing
- Cross-chunk adds >50,000 relationships total
- Pipeline runs for >6 hours
- Database exceeds 1GB

---

## 🔧 Troubleshooting

### If 12-Chunk Validation Still Fails:

**Density still too high?**

```bash
# Check if GRAPHRAG_CROSS_CHUNK_WINDOW is set in .env
grep GRAPHRAG_CROSS_CHUNK_WINDOW .env

# If it shows uncommented line, comment it out or remove it
```

**Still no communities?**

```bash
# Check final density in logs
grep "density:" logs/pipeline/graphrag_adaptive.log | tail -5

# If density < 0.30 but no communities, check max_cluster_size
# Should be 50 (not 10)
```

### If Overnight Run Takes Too Long:

**Speed up by disabling link prediction**:

```bash
export GRAPHRAG_ENABLE_LINK_PREDICTION=false
```

---

## 📝 Configuration Summary

### Recommended `.env` for Overnight Run:

```bash
# GraphRAG Configuration

# Semantic Similarity
GRAPHRAG_SIMILARITY_THRESHOLD=0.92

# Cross-Chunk: LEAVE UNSET for adaptive window
# GRAPHRAG_CROSS_CHUNK_WINDOW=  ← Comment this out or remove!

# Density Safeguards
GRAPHRAG_MAX_DENSITY=0.3

# Link Prediction (optional - can disable for speed)
GRAPHRAG_ENABLE_LINK_PREDICTION=true
GRAPHRAG_LINK_PREDICTION_THRESHOLD=0.65
GRAPHRAG_MAX_PREDICTIONS_PER_ENTITY=5
```

---

## ✅ Pre-Flight Checklist

Before running overnight:

- [ ] Adaptive window implemented (code changes done)
- [ ] `GRAPHRAG_CROSS_CHUNK_WINDOW` commented out or removed from `.env`
- [ ] 12-chunk validation test passes
- [ ] Communities detected in validation
- [ ] Density < 0.30 in validation
- [ ] MongoDB Atlas connection stable
- [ ] Sufficient disk space (check MongoDB Atlas quota)
- [ ] Log file path configured

---

## 🌅 Morning Analysis

When you wake up, run:

```bash
# Check if pipeline completed
tail -100 logs/pipeline/graphrag_full.log

# Analyze results
python scripts/analyze_graph_structure.py

# Sample data quality
python scripts/sample_graph_data.py

# Test community detection
python scripts/test_community_detection.py
```

**Success Indicators**:

- Pipeline completed message in logs
- Graph density 0.15-0.25
- 50-200 communities detected
- No errors or warnings

---

## 📞 Quick Reference

**Files Modified**:

- `app/stages/graph_construction.py` - Adaptive window logic

**Documentation Created**:

- `documentation/GRAPHRAG-ADAPTIVE-WINDOW-IMPLEMENTATION.md` - This file
- `documentation/GRAPHRAG-CONFIG-REFERENCE.md` - Updated

**Testing Scripts**:

- `scripts/full_cleanup.py` - Clean all GraphRAG data
- `scripts/analyze_graph_structure.py` - Analyze graph metrics
- `scripts/sample_graph_data.py` - Sample entities/relationships
- `scripts/test_community_detection.py` - Test clustering

---

## Summary

1. **Validate with 12 chunks** first (adaptive window=2)
2. **If successful**, run 13k chunks overnight (adaptive windows 1-5)
3. **Check results** in the morning

**The system is ready - good luck with the overnight run!** 🚀
