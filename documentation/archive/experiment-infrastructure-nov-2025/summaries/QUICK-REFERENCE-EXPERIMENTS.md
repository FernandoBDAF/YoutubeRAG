# GraphRAG Experiments - Quick Reference

**Updated**: November 4, 2025

---

## 🚀 Common Commands

### Run with Config File

```bash
python -m app.cli.graphrag \
  --config configs/graphrag/louvain_resolution_08.json \
  --stage community_detection
```

### Run with CLI Flags

```bash
python -m app.cli.graphrag \
  --stage community_detection \
  --read-db-name mongo_hack \
  --write-db-name graphrag_exp_custom \
  --algorithm louvain \
  --resolution 0.8
```

### Compare Experiments

```bash
python scripts/compare_graphrag_experiments.py DB1 DB2 [DB3 ...]
```

---

## 📋 Available Config Files

| File                         | Resolution | Purpose                       |
| ---------------------------- | ---------- | ----------------------------- |
| `louvain_default.json`       | 1.0        | Baseline (current production) |
| `louvain_resolution_08.json` | 0.8        | Fewer, larger communities     |
| `louvain_resolution_15.json` | 1.5        | More, smaller communities     |

---

## 🎯 Quick Experiment

```bash
# 1. Run experiment (~4 min)
python -m app.cli.graphrag \
  --config configs/graphrag/louvain_resolution_08.json \
  --stage community_detection

# 2. Compare with baseline (~5 sec)
python scripts/compare_graphrag_experiments.py \
  mongo_hack graphrag_exp_louvain_res08

# 3. Analyze and decide!
```

---

## ⚙️ Common Flags

| Flag              | Values                                                                 | Default       | Description           |
| ----------------- | ---------------------------------------------------------------------- | ------------- | --------------------- |
| `--config`        | path/to/file.json                                                      | None          | Load config from file |
| `--stage`         | extraction, entity_resolution, graph_construction, community_detection | full pipeline | Run specific stage    |
| `--read-db-name`  | database name                                                          | **REQUIRED**  | Source database       |
| `--write-db-name` | database name                                                          | **REQUIRED**  | Target database       |
| `--algorithm`     | louvain, hierarchical_leiden                                           | louvain       | Detection algorithm   |
| `--resolution`    | 0.5-2.0                                                                | 1.0           | Louvain resolution    |
| `--concurrency`   | integer                                                                | 300           | Worker count          |
| `--max`           | integer                                                                | unlimited     | Max documents         |

---

## 📊 Current Production Config

```json
{
  "experiment_id": "louvain_resolution_1.0",
  "read_db": "mongo_hack",
  "write_db": "mongo_hack",
  "concurrency": 300,
  "community_detection": {
    "algorithm": "louvain",
    "resolution": 1.0,
    "min_cluster_size": 2,
    "max_cluster_size": 50
  }
}
```

**Results**:

- 873 communities
- Modularity: 0.6347
- Avg size: ~31 entities
- Multi-entity: >99%

---

## ⚠️ Safety Rules

1. ✅ **Always specify both `--read-db-name` and `--write-db-name`**
2. ✅ **Use unique `write-db-name` for each experiment**
3. ✅ **Check experiment_tracking collection to avoid conflicts**
4. ✅ **Archive or drop old experiment databases**

---

## 🧹 Cleanup Commands

### Drop Experiment Database

```bash
# MongoDB shell
mongosh
use graphrag_exp_louvain_res08
db.dropDatabase()
```

### List All Experiment Databases

```bash
mongosh --eval "db.adminCommand('listDatabases').databases.filter(d => d.name.startsWith('graphrag_exp')).forEach(d => print(d.name))"
```

---

## 📚 More Info

- **Full Guide**: `documentation/guides/EXPERIMENT-WORKFLOW.md`
- **Technical Details**: `EXPERIMENT-INFRASTRUCTURE-COMPLETE.md`
- **Session Summary**: `SESSION-SUMMARY-NOV-4-2025-COMPLETE.md`

---

**Quick Ref Version**: 1.0  
**Last Updated**: Nov 4, 2025
