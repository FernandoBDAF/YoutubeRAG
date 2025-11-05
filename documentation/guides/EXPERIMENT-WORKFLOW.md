# GraphRAG Experiment Workflow Guide

**Date**: November 4, 2025  
**Status**: Active - Ready for use

---

## 🎯 Purpose

This guide explains how to run GraphRAG experiments with different configurations for comparative analysis.

---

## 🚀 Quick Start

### Running an Experiment with Config File

```bash
python -m app.cli.graphrag \
  --config configs/graphrag/louvain_resolution_08.json \
  --stage community_detection
```

### Running with CLI Flags (No Config File)

```bash
python -m app.cli.graphrag \
  --stage community_detection \
  --read-db-name mongo_hack \
  --write-db-name graphrag_exp_custom \
  --algorithm louvain \
  --resolution 1.2 \
  --concurrency 300
```

### Mixing Config File + CLI Overrides

```bash
# Use config file as base, override specific values
python -m app.cli.graphrag \
  --config configs/graphrag/louvain_default.json \
  --write-db-name graphrag_exp_test \
  --resolution 1.3
```

**Priority**: CLI flags > Config file > Environment variables

---

## 📋 Configuration File Format

### Example: `configs/graphrag/my_experiment.json`

```json
{
  "experiment_id": "my_unique_experiment",
  "read_db": "mongo_hack",
  "write_db": "graphrag_my_experiment",
  "concurrency": 300,
  "community_detection": {
    "algorithm": "louvain",
    "resolution": 1.0,
    "min_cluster_size": 2,
    "max_cluster_size": 50
  }
}
```

### Required Fields

- ✅ `experiment_id`: Unique identifier for tracking
- ✅ `read_db`: Source database (where chunks are)
- ✅ `write_db`: Target database (where results go)

### Optional Fields

- `concurrency`: Worker count (default: 300)
- `community_detection.algorithm`: "louvain" or "hierarchical_leiden" (default: "louvain")
- `community_detection.resolution`: 0.5-2.0 (default: 1.0)
- `community_detection.min_cluster_size`: Filter small communities (default: 2)
- `community_detection.max_cluster_size`: Soft cap (default: 50)

---

## 🧪 Running Experiments

### Scenario 1: Test Different Resolutions

**Goal**: Find optimal resolution parameter for community detection

```bash
# Experiment 1: Lower resolution (fewer, larger communities)
python -m app.cli.graphrag \
  --config configs/graphrag/louvain_resolution_08.json \
  --stage community_detection

# Experiment 2: Default resolution (baseline)
python -m app.cli.graphrag \
  --config configs/graphrag/louvain_default.json \
  --stage community_detection

# Experiment 3: Higher resolution (more, smaller communities)
python -m app.cli.graphrag \
  --config configs/graphrag/louvain_resolution_15.json \
  --stage community_detection

# Compare results
python scripts/compare_graphrag_experiments.py \
  graphrag_exp_louvain_res08 \
  mongo_hack \
  graphrag_exp_louvain_res15
```

**Expected Results**:

- Resolution 0.8: ~600 communities, avg size ~45
- Resolution 1.0: ~873 communities, avg size ~31 (baseline)
- Resolution 1.5: ~1200 communities, avg size ~23

### Scenario 2: Test Different Algorithms

**Goal**: Compare Louvain vs hierarchical_leiden

```bash
# Experiment 1: Louvain (proven)
python -m app.cli.graphrag \
  --stage community_detection \
  --read-db-name mongo_hack \
  --write-db-name graphrag_exp_louvain \
  --algorithm louvain

# Experiment 2: Hierarchical Leiden (test if improved)
python -m app.cli.graphrag \
  --stage community_detection \
  --read-db-name mongo_hack \
  --write-db-name graphrag_exp_leiden \
  --algorithm hierarchical_leiden

# Compare
python scripts/compare_graphrag_experiments.py \
  graphrag_exp_louvain graphrag_exp_leiden
```

---

## 📊 Comparing Experiments

### Using the Comparison Script

```bash
python scripts/compare_graphrag_experiments.py DB1 DB2 [DB3 ...]
```

**Output**:

- Summary table (markdown)
- Detailed statistics per experiment
- Analysis with recommendations

**Metrics Compared**:

- Entity counts
- Relationship counts
- Community counts
- Average community size
- Multi-entity community percentage
- Graph density

### Manual Comparison (MongoDB)

```javascript
// Count communities
db.communities.count();

// Average community size
db.communities.aggregate([
  { $group: { _id: null, avg_size: { $avg: "$entity_count" } } },
]);

// Size distribution
db.communities.aggregate([
  { $group: { _id: "$entity_count", count: { $sum: 1 } } },
  { $sort: { _id: 1 } },
]);
```

---

## ⚠️ Important Notes

### Database Safety

1. **Always specify both `read_db` and `write_db` for experiments**

   - Prevents accidental data mixing
   - Pipeline will error if only one is specified

2. **Use unique `write_db` names**

   - `graphrag_exp_louvain_res08`
   - `graphrag_exp_leiden_test`
   - Avoids overwriting previous experiments

3. **Keep `read_db` pointing to source data**
   - Usually `mongo_hack` (main database)
   - Or `experiment_conservative` (from ETL experiments)

### Experiment Tracking

- Experiments are auto-tracked in `experiment_tracking` collection
- Includes configuration, start time, status
- Use for audit trail and reproducibility

---

## 🎯 Recommended Experiments

### Phase 1: Validate Current Setup (Quick - 30 min each)

Run community detection only (graph already built):

1. **Baseline**: Resolution 1.0 (already done)
2. **Lower**: Resolution 0.8 (fewer communities)
3. **Higher**: Resolution 1.5 (more communities)

```bash
# Takes ~4 min each (only community detection stage)
for res in 0.8 1.5; do
  python -m app.cli.graphrag \
    --stage community_detection \
    --read-db-name mongo_hack \
    --write-db-name graphrag_exp_louvain_res${res/./_} \
    --resolution $res
done
```

### Phase 2: Full Pipeline Experiments (Slow - 4-6 hours each)

Run entire GraphRAG pipeline with different configs:

```bash
# Full run with custom config
python -m app.cli.graphrag \
  --config configs/graphrag/my_experiment.json
```

---

## 📈 Analysis Workflow

1. **Run experiments** (use config files or CLI flags)
2. **Compare results** (use comparison script)
3. **Analyze metrics** (which config performs best?)
4. **Document findings** (update config comments)
5. **Iterate** (test new variations based on findings)

---

## 🔄 Iteration Example

**Iteration 1**: Test resolution range (0.5, 1.0, 1.5, 2.0)  
**Finding**: Resolution 1.0 gives best modularity (0.6347)

**Iteration 2**: Fine-tune around 1.0 (0.9, 1.0, 1.1)  
**Finding**: Resolution 1.0 still optimal

**Iteration 3**: Test min_cluster_size (2, 3, 5)  
**Finding**: min_size=2 preserves important small communities

**Conclusion**: Current defaults are well-tuned!

---

## ✅ Best Practices

1. **Use descriptive experiment_ids**

   - Good: `louvain_res08_minsize3_20241104`
   - Bad: `test1`, `exp2`

2. **Document experiment purpose**

   - Add "comments" field to config file
   - Include hypothesis and expected results

3. **Compare incrementally**

   - Change ONE parameter at a time
   - Makes it clear what caused differences

4. **Archive successful experiments**

   - Keep winning configurations
   - Document why they won

5. **Clean up failed experiments**
   - Drop databases from failed runs
   - Prevents confusion and saves disk space

---

**Guide Status**: ✅ Ready for use  
**Last Updated**: November 4, 2025
