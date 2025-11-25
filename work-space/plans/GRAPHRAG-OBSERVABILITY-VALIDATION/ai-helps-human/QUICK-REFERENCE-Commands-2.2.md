# Quick Reference: Achievement 2.2 Commands

**Achievement**: 2.2 (Observability Pipeline Run)  
**Created**: 2025-11-13

---

## 🚀 Phase 1: Setup

### Check Observability Stack

```bash
docker ps | grep -E "prometheus|grafana|loki|promtail"
curl -s http://localhost:3000/api/health | jq
curl -s http://localhost:9090/-/healthy
curl -s http://localhost:9091/metrics | head -20
```

### Enable Observability

```bash
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
export GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=7
export GRAPHRAG_QUALITY_METRICS=true

# Verify
echo "GRAPHRAG_TRANSFORMATION_LOGGING=$GRAPHRAG_TRANSFORMATION_LOGGING"
echo "GRAPHRAG_SAVE_INTERMEDIATE_DATA=$GRAPHRAG_SAVE_INTERMEDIATE_DATA"
echo "GRAPHRAG_QUALITY_METRICS=$GRAPHRAG_QUALITY_METRICS"
```

### Clean Database

```bash
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "
    db.video_chunks.updateMany({}, {\$unset: {
      'graphrag_extraction': '',
      'graphrag_resolution': '',
      'graphrag_construction': '',
      'graphrag_communities': ''
    }});
    db.entities.deleteMany({});
    db.relations.deleteMany({});
    db.communities.deleteMany({});
    db.transformation_logs.deleteMany({});
    db.entities_raw.deleteMany({});
    db.entities_resolved.deleteMany({});
    db.relations_raw.deleteMany({});
    db.relations_final.deleteMany({});
    db.graph_pre_detection.deleteMany({});
    db.quality_metrics.deleteMany({});
    db.graphrag_runs.deleteMany({});
    print('Cleanup complete!');
  "
```

---

## 🏃 Phase 2: Execute

### Run Pipeline

```bash
python -m app.cli.graphrag --max 50 --db-name validation_01 --verbose
```

### Monitor

- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- Watch terminal for trace_id, errors, warnings

---

## 🔍 Phase 3: Verify

### Check Collections

```bash
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "
    const observability = [
      'transformation_logs', 'entities_raw', 'entities_resolved',
      'relations_raw', 'relations_final', 'graph_pre_detection',
      'quality_metrics', 'graphrag_runs'
    ];
    observability.forEach(coll => {
      const count = db[coll].countDocuments({});
      print(coll + ':', count + ' docs');
    });
  "
```

### Check Data Quality

```bash
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "
    print('Entities:', db.entities.countDocuments({}));
    print('Relations:', db.relations.countDocuments({}));
    print('Communities:', db.communities.countDocuments({}));
  "
```

### Get Run Metadata

```bash
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "
    const run = db.graphrag_runs.findOne({});
    if (run) {
      print('Trace ID:', run.trace_id);
      print('Runtime:', (new Date(run.end_time) - new Date(run.start_time)) / 1000 + 's');
    }
  "
```

### Calculate Storage

```bash
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "
    const collections = [
      'entities', 'relations', 'communities',
      'transformation_logs', 'entities_raw', 'entities_resolved',
      'relations_raw', 'relations_final', 'graph_pre_detection',
      'quality_metrics', 'graphrag_runs'
    ];
    let totalSize = 0;
    collections.forEach(coll => {
      const stats = db[coll].stats();
      totalSize += stats.size;
    });
    print('Total:', (totalSize / 1024).toFixed(2) + ' KB');
  "
```

---

## 📊 Expected Results

### Baseline (Achievement 2.1)

- Runtime: ~510s
- Entities: 220
- Relations: 71
- Communities: 26
- Storage: ~557 KB

### Acceptable Ranges (Achievement 2.2)

- Runtime: < 612s (< 20% overhead)
- Entities: 220 (0% change)
- Relations: 71 (0% change)
- Communities: 26 (0% change)
- Storage: < 835 KB (< 50% overhead)

---

## 🚨 Troubleshooting

### Restart Observability Stack

```bash
cd /Users/fernandobarroso/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG
docker-compose -f docker-compose.observability.yml down
docker-compose -f docker-compose.observability.yml up -d
```

### Check Logs

```bash
# Pipeline logs
ls -lt logs/pipeline/ | head -5

# Docker logs
docker logs youtuberag-prometheus --tail 50
docker logs youtuberag-grafana --tail 50
```

---

## 📁 File Locations

- **Logs**: `logs/pipeline/graphrag_full_pipeline_*.log`
- **Documentation**: `documentation/`
- **Observations**: `observations/`
- **Screenshots**: `observations/screenshots/` (optional)
