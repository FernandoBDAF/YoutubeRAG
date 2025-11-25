# AI-Assist Guide: Achievement 2.2 - Observability Pipeline Run

**Type**: AI-Assist Guide  
**Achievement**: 2.2 (Observability Pipeline Run Executed)  
**Estimated Time**: 3-4 hours  
**Prerequisites**: Achievement 2.1 complete, observability stack running  
**Created**: 2025-11-13

---

## 🎯 Overview

This guide walks you through executing the GraphRAG pipeline with **all observability features enabled** and measuring the performance overhead compared to the baseline (Achievement 2.1).

**What You'll Do**:

1. Enable observability environment variables
2. Clean database and prepare monitoring
3. Execute pipeline with real-time monitoring
4. Verify observability collections created
5. Compare performance with baseline
6. Create 4 documentation deliverables

**What I'll Analyze**:

- Your terminal output
- MongoDB collection counts
- Performance metrics
- Log files
- Screenshots (optional)

---

## ✅ Prerequisites Checklist

Before starting, verify:

- [ ] Achievement 2.1 complete (baseline established)
- [ ] Observability stack running (Prometheus, Grafana, Loki, Promtail)
- [ ] MongoDB accessible (`validation_01` database)
- [ ] `video_chunks` collection exists in `validation_01`
- [ ] Terminal access to project root
- [ ] Browser access to Grafana (http://localhost:3000) and Prometheus (http://localhost:9090)

---

## 📋 Phase 1: Pre-execution Setup (30-45 min)

### Step 1.1: Verify Observability Stack Running

**Copy and run**:

```bash
# Check Docker containers
docker ps | grep -E "prometheus|grafana|loki|promtail"

# Check Grafana health
curl -s http://localhost:3000/api/health | jq

# Check Prometheus health
curl -s http://localhost:9090/-/healthy

# Check metrics endpoint
curl -s http://localhost:9091/metrics | head -20
```

**Expected Output**:

- 4 containers running (prometheus, grafana, loki, promtail)
- Grafana health: `{"database":"ok"}`
- Prometheus: `Prometheus Server is Healthy.`
- Metrics endpoint: Should show Prometheus format metrics

**Share with me**: Terminal output

---

### Step 1.2: Enable Observability Environment Variables

**Copy and run**:

```bash
# Enable all observability features
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
export GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=7
export GRAPHRAG_QUALITY_METRICS=true

# Verify they're set
echo "GRAPHRAG_TRANSFORMATION_LOGGING=$GRAPHRAG_TRANSFORMATION_LOGGING"
echo "GRAPHRAG_SAVE_INTERMEDIATE_DATA=$GRAPHRAG_SAVE_INTERMEDIATE_DATA"
echo "GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=$GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS"
echo "GRAPHRAG_QUALITY_METRICS=$GRAPHRAG_QUALITY_METRICS"
```

**Expected Output**:

```
GRAPHRAG_TRANSFORMATION_LOGGING=true
GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=7
GRAPHRAG_QUALITY_METRICS=true
```

**Share with me**: Terminal output

---

### Step 1.3: Clean Database

**Copy and run** (replace `***` with your password):

```bash
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "
    // Clean video_chunks processing fields
    db.video_chunks.updateMany({}, {\$unset: {
      'graphrag_extraction': '',
      'graphrag_resolution': '',
      'graphrag_construction': '',
      'graphrag_communities': ''
    }});

    // Clean legacy collections
    db.entities.deleteMany({});
    db.relations.deleteMany({});
    db.communities.deleteMany({});

    // Clean observability collections
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

**Expected Output**:

```
Cleanup complete!
```

**Share with me**: Terminal output

---

### Step 1.4: Verify Database Clean

**Copy and run**:

```bash
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "
    print('video_chunks:', db.video_chunks.countDocuments({}));
    print('entities:', db.entities.countDocuments({}));
    print('relations:', db.relations.countDocuments({}));
    print('communities:', db.communities.countDocuments({}));
    print('transformation_logs:', db.transformation_logs.countDocuments({}));
    print('entities_raw:', db.entities_raw.countDocuments({}));
    print('entities_resolved:', db.entities_resolved.countDocuments({}));
    print('relations_raw:', db.relations_raw.countDocuments({}));
    print('relations_final:', db.relations_final.countDocuments({}));
    print('graph_pre_detection:', db.graph_pre_detection.countDocuments({}));
    print('quality_metrics:', db.quality_metrics.countDocuments({}));
    print('graphrag_runs:', db.graphrag_runs.countDocuments({}));
  "
```

**Expected Output**:

```
video_chunks: 200
entities: 0
relations: 0
communities: 0
transformation_logs: 0
entities_raw: 0
entities_resolved: 0
relations_raw: 0
relations_final: 0
graph_pre_detection: 0
quality_metrics: 0
graphrag_runs: 0
```

**Share with me**: Terminal output

---

### Step 1.5: Prepare Monitoring

**Open in browser**:

1. Grafana: http://localhost:3000
   - Navigate to "GraphRAG Pipeline Dashboard"
   - Keep this tab open for monitoring
2. Prometheus: http://localhost:9090
   - Navigate to "Graph" tab
   - Keep this tab open (optional)

**Prepare terminal**:

- Keep your current terminal for pipeline execution
- (Optional) Open a second terminal for `tail -f logs/pipeline/*.log`

**Note start time**: Record the current time for the observation log

---

## 📋 Phase 2: Pipeline Execution with Monitoring (1-2 hours)

### Step 2.1: Execute Pipeline

**Copy and run**:

```bash
python -m app.cli.graphrag --max 50 --db-name validation_01 --verbose
```

**What to monitor**:

1. **Terminal**: Watch for stage progress, errors, warnings
2. **Grafana**: Refresh dashboard every 30-60 seconds
3. **Note the trace_id**: It will appear early in the logs (format: `45c1256d-5d7d-46a3-900f-3b6b139a289a`)

**What to capture** (optional but helpful):

- Screenshot of Grafana dashboard at start
- Screenshot of Grafana dashboard at middle (Stage 2-3)
- Screenshot of Grafana dashboard at end
- Note any errors or warnings in terminal

**Expected Duration**: ~8-10 minutes (similar to baseline, plus observability overhead)

**⚠️ Important**: Do NOT interrupt the pipeline. Let it complete fully.

---

### Step 2.2: Monitor and Observe

**While pipeline is running**:

1. **Watch terminal output**:

   - Note stage start/end times
   - Note any errors or warnings
   - Note the trace_id (appears early)

2. **Check Grafana dashboard**:

   - Refresh every 30-60 seconds
   - Watch metrics update in real-time
   - Note any anomalies

3. **Record observations**:
   - Start time: `[HH:MM:SS]`
   - Stage 1 (Extraction) start: `[HH:MM:SS]`
   - Stage 2 (Resolution) start: `[HH:MM:SS]`
   - Stage 3 (Construction) start: `[HH:MM:SS]`
   - Stage 4 (Detection) start: `[HH:MM:SS]`
   - End time: `[HH:MM:SS]`
   - Trace ID: `[UUID]`
   - Any errors: `[description]`
   - Any warnings: `[description]`

---

### Step 2.3: Wait for Completion

**Pipeline will complete when you see**:

```
[PIPELINE] Completed: 4/4 stages succeeded, 0 failed
GraphRAG pipeline completed successfully
```

**Exit code should be**: `0` (success)

**Share with me after completion**:

1. Full terminal output (or save to file: `python -m app.cli.graphrag --max 50 --db-name validation_01 --verbose > observability_run.log 2>&1`)
2. Log file from `logs/pipeline/` (most recent `graphrag_full_pipeline_*.log`)
3. Start time, end time, trace_id
4. Any errors or warnings observed
5. Screenshots (if captured)

---

## 📋 Phase 3: Post-execution Analysis (1-1.5 hours)

### Step 3.1: Verify Observability Collections Created

**Copy and run**:

```bash
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "
    const collections = db.getCollectionNames();
    const observability = [
      'transformation_logs',
      'entities_raw',
      'entities_resolved',
      'relations_raw',
      'relations_final',
      'graph_pre_detection',
      'quality_metrics',
      'graphrag_runs'
    ];

    print('\\n=== Observability Collections ===');
    observability.forEach(coll => {
      const exists = collections.includes(coll);
      const count = exists ? db[coll].countDocuments({}) : 0;
      print(coll + ':', exists ? 'EXISTS' : 'MISSING', '(' + count + ' docs)');
    });
  "
```

**Expected Output**:

```
=== Observability Collections ===
transformation_logs: EXISTS (200-500 docs)
entities_raw: EXISTS (~220 docs)
entities_resolved: EXISTS (~220 docs)
relations_raw: EXISTS (~71 docs)
relations_final: EXISTS (~71 docs)
graph_pre_detection: EXISTS (1-5 docs)
quality_metrics: EXISTS (50-200 docs)
graphrag_runs: EXISTS (1 doc)
```

**Share with me**: Terminal output

---

### Step 3.2: Verify Data Quality (Entity/Relation Counts)

**Copy and run**:

```bash
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "
    print('\\n=== Data Quality Check ===');
    print('Entities:', db.entities.countDocuments({}));
    print('Relations:', db.relations.countDocuments({}));
    print('Communities:', db.communities.countDocuments({}));
    print('Processed chunks:', db.video_chunks.countDocuments({'graphrag_extraction.status': 'completed'}));
  "
```

**Expected Output** (should match baseline):

```
=== Data Quality Check ===
Entities: 220
Relations: 71
Communities: 26
Processed chunks: 50
```

**Share with me**: Terminal output

---

### Step 3.3: Extract Trace ID and Run Metadata

**Copy and run**:

```bash
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "
    const run = db.graphrag_runs.findOne({});
    if (run) {
      print('\\n=== Run Metadata ===');
      print('Trace ID:', run.trace_id);
      print('Start Time:', run.start_time);
      print('End Time:', run.end_time);
      const runtime = (new Date(run.end_time) - new Date(run.start_time)) / 1000;
      print('Runtime:', runtime + 's');
      print('Chunks Processed:', run.chunks_processed || 'N/A');
      print('Status:', run.status || 'N/A');
    } else {
      print('ERROR: No run metadata found in graphrag_runs collection');
    }
  "
```

**Expected Output**:

```
=== Run Metadata ===
Trace ID: [UUID]
Start Time: [ISO timestamp]
End Time: [ISO timestamp]
Runtime: [seconds]s
Chunks Processed: 50
Status: completed
```

**Share with me**: Terminal output

---

### Step 3.4: Sample Observability Data

**Copy and run**:

```bash
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "
    print('\\n=== Sample transformation_logs ===');
    printjson(db.transformation_logs.findOne());

    print('\\n=== Sample entities_raw ===');
    printjson(db.entities_raw.findOne());

    print('\\n=== Sample quality_metrics ===');
    printjson(db.quality_metrics.findOne());
  "
```

**Share with me**: Terminal output (first 100 lines is enough)

---

### Step 3.5: Calculate Storage Usage

**Copy and run**:

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
    print('\\n=== Storage Usage ===');
    collections.forEach(coll => {
      const stats = db[coll].stats();
      const sizeKB = (stats.size / 1024).toFixed(2);
      print(coll + ':', sizeKB + ' KB');
      totalSize += stats.size;
    });
    print('\\nTotal:', (totalSize / 1024).toFixed(2) + ' KB');
  "
```

**Expected Output**:

```
=== Storage Usage ===
entities: [X] KB
relations: [X] KB
communities: [X] KB
transformation_logs: [X] KB
entities_raw: [X] KB
entities_resolved: [X] KB
relations_raw: [X] KB
relations_final: [X] KB
graph_pre_detection: [X] KB
quality_metrics: [X] KB
graphrag_runs: [X] KB

Total: [X] KB
```

**Share with me**: Terminal output

---

### Step 3.6: Compare with Baseline

**Baseline metrics** (from Achievement 2.1):

- **Runtime**: ~510 seconds (~8.5 minutes)
- **Entities**: 220
- **Relations**: 71
- **Communities**: 26
- **Storage**: ~557 KB

**Calculate overhead**:

- **Runtime Overhead**: `((observability_runtime - baseline_runtime) / baseline_runtime) * 100`
- **Storage Overhead**: `((observability_storage - baseline_storage) / baseline_storage) * 100`

**Acceptable ranges**:

- Runtime overhead: < 20% (< 612 seconds)
- Storage overhead: < 50% (< 835 KB)

**Share with me**: Your calculated overhead percentages

---

## 📋 Phase 4: Documentation (30-45 min)

### What I'll Create for You

After you share all the data from Phases 1-3, I will create:

1. **`EXECUTION_OBSERVATION_OBSERVABILITY-PIPELINE-RUN_2025-11-13.md`**

   - Real-time observation log
   - Stage timeline
   - Metrics and issues

2. **`Observability-Performance-Report.md`**

   - Detailed performance comparison
   - Runtime overhead analysis
   - Storage overhead analysis
   - Memory usage (if available)

3. **`Observability-Collections-Report.md`**

   - Verification of all 8 collections
   - Document counts
   - Sample data
   - Schema validation

4. **`Observability-Comparison-Summary.md`**
   - Side-by-side comparison with baseline
   - Overhead percentages
   - Recommendations
   - Conclusions

---

## 📊 Quick Reference: Commands Summary

### Pre-execution

```bash
# 1. Check stack
docker ps | grep -E "prometheus|grafana|loki|promtail"

# 2. Enable observability
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
export GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=7
export GRAPHRAG_QUALITY_METRICS=true

# 3. Clean database
mongosh "mongodb+srv://..." --eval "[cleanup script]"
```

### Execution

```bash
# Run pipeline
python -m app.cli.graphrag --max 50 --db-name validation_01 --verbose
```

### Post-execution

```bash
# 1. Verify collections
mongosh "mongodb+srv://..." --eval "[collection check script]"

# 2. Verify data quality
mongosh "mongodb+srv://..." --eval "[data quality script]"

# 3. Extract trace ID
mongosh "mongodb+srv://..." --eval "[trace ID script]"

# 4. Sample data
mongosh "mongodb+srv://..." --eval "[sample data script]"

# 5. Calculate storage
mongosh "mongodb+srv://..." --eval "[storage script]"
```

---

## 🚨 Troubleshooting

### Issue: Observability stack not running

**Solution**:

```bash
cd /Users/fernandobarroso/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG
docker-compose -f docker-compose.observability.yml up -d
```

### Issue: Environment variables not set

**Solution**: Re-export them in the same terminal where you'll run the pipeline

### Issue: Pipeline fails with observability errors

**Solution**: Share the error with me immediately. We may need to disable specific features:

```bash
export GRAPHRAG_TRANSFORMATION_LOGGING=false  # Disable if causing issues
```

### Issue: Collections not created

**Solution**: Check if environment variables were actually set when pipeline ran:

```bash
# In the pipeline logs, search for:
grep "GRAPHRAG_TRANSFORMATION_LOGGING" logs/pipeline/graphrag_full_pipeline_*.log
```

---

## ✅ Success Criteria

Before considering Achievement 2.2 complete:

- [ ] Pipeline completed with exit code 0
- [ ] All 8 observability collections created
- [ ] All collections have > 0 documents
- [ ] Entity/relation/community counts match baseline (220/71/26)
- [ ] Runtime overhead < 20%
- [ ] Storage overhead < 50%
- [ ] Trace ID captured and documented
- [ ] All 4 deliverables created by AI

---

## 📝 What to Share with Me

### After Phase 1 (Setup)

- [ ] Docker containers status
- [ ] Environment variables verification
- [ ] Database cleanup confirmation

### After Phase 2 (Execution)

- [ ] Full terminal output or log file
- [ ] Start time, end time, trace_id
- [ ] Any errors or warnings
- [ ] Screenshots (optional)

### After Phase 3 (Analysis)

- [ ] Observability collections verification
- [ ] Data quality check results
- [ ] Run metadata (trace_id, runtime)
- [ ] Sample data
- [ ] Storage usage
- [ ] Calculated overhead percentages

---

**Ready to Start?** Begin with Phase 1, Step 1.1, and share the results with me after each phase!
