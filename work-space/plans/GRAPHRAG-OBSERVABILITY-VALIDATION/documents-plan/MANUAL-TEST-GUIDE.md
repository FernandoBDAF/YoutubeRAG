# GraphRAG Observability Infrastructure - Manual Test Guide

**Purpose**: Comprehensive step-by-step guide for manually testing the complete GraphRAG observability infrastructure  
**Audience**: Developers, QA Engineers, DevOps, and anyone validating the observability system  
**Last Updated**: 2025-11-15  
**Estimated Time**: 4-6 hours for complete testing

---

## Table of Contents

1. [Overview & Context](#overview--context)
2. [Prerequisites & Setup](#prerequisites--setup)
3. [Understanding the GraphRAG Pipeline](#understanding-the-graphrag-pipeline)
4. [Test Suite Organization](#test-suite-organization)
5. [Phase 1: Infrastructure Testing](#phase-1-infrastructure-testing)
6. [Phase 2: Data Collection Testing](#phase-2-data-collection-testing)
7. [Phase 3: Validation & Query Testing](#phase-3-validation--query-testing)
8. [Phase 4: Performance & Storage Testing](#phase-4-performance--storage-testing)
9. [Phase 5: Tool Enhancement Testing](#phase-5-tool-enhancement-testing)
10. [Phase 6: Production Readiness Testing](#phase-6-production-readiness-testing)
11. [Troubleshooting](#troubleshooting)
12. [Quick Reference](#quick-reference)

---

## Overview & Context

### What is GraphRAG?

GraphRAG is a **Graph-based Retrieval-Augmented Generation** system that transforms unstructured text into a knowledge graph for enhanced information retrieval and generation.

**Pipeline Stages**:
1. **Extraction** - Extract entities and relationships from text
2. **Resolution** - Merge duplicate entities (e.g., "Apple Inc." and "Apple" → single entity)
3. **Graph Construction** - Build the knowledge graph
4. **Community Detection** - Identify entity clusters/communities

**Key Reference**: `documentation/guides/GRAPHRAG-TRANSFORMATION-LOGGING.md`

### What is the Observability Infrastructure?

The observability infrastructure provides **complete visibility** into the GraphRAG pipeline execution through:

- **Transformation Logging** - Track every data transformation (merges, creates, skips)
- **Intermediate Data Storage** - Snapshot data at each pipeline stage
- **Quality Metrics** - 23 metrics tracking pipeline health
- **Performance Monitoring** - Prometheus + Grafana dashboards
- **Log Aggregation** - Loki for centralized logging
- **Query Tools** - Scripts for analyzing pipeline behavior
- **Explanation Tools** - Understand why transformations happened

**Key Reference**: `PLAN_GRAPHRAG-OBSERVABILITY-VALIDATION.md`

### What This Guide Tests

This manual test guide validates **25 achievements** across 7 priority levels:

- **Priority 1-2**: Core infrastructure (transformation logging, metrics, dashboards)
- **Priority 3**: Validation framework and testing
- **Priority 4**: Data analysis tools
- **Priority 5**: Performance and storage assessment
- **Priority 6**: Documentation and knowledge capture
- **Priority 7**: Tool enhancements and production readiness

**Total Achievements Tested**: 25  
**Total Execution Tasks**: 34  
**Total Documentation**: 81+ files

---

## Prerequisites & Setup

### System Requirements

**Software**:
- Python 3.9+
- MongoDB 4.4+
- Docker & Docker Compose (for Prometheus/Grafana/Loki)
- Git

**Hardware**:
- 8 GB RAM minimum (16 GB recommended)
- 10 GB free disk space
- Network access for package installation

### Environment Setup

**Step 1: Navigate to Project Root**

```bash
cd /Users/fernandobarroso/repo/KnowledgeManager/GraphRAG
```

**Step 2: Verify Python Environment**

```bash
python --version  # Should be 3.9+
which python      # Verify correct Python
```

**Step 3: Install Dependencies**

```bash
# If using virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

**Step 4: Configure Environment Variables**

```bash
# Copy template
cp documentation/ENV-OBSERVABILITY-TEMPLATE.md .env

# Edit .env file with your settings
# Key variables to set:
# - MONGODB_URI (default: mongodb://localhost:27017/)
# - MONGODB_DATABASE (default: graphrag)
# - OBSERVABILITY_ENABLED=true
# - All feature flags (see template for details)
```

**Reference**: `documentation/Environment-Variables-Guide.md` (17 KB guide)

**Step 5: Start MongoDB**

```bash
# If using local MongoDB
mongod --dbpath /path/to/data/db

# If using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Verify connection
mongosh mongodb://localhost:27017/ --eval "db.version()"
```

**Step 6: Verify Test Data Exists**

```bash
# Check if you have test input data
ls -la data/input/

# If no test data, you'll need sample text files for processing
# Example: Create a simple test file
echo "Apple Inc. is a technology company. Apple creates innovative products." > data/input/test.txt
```

### Optional: Start Observability Stack

For full testing of Prometheus/Grafana/Loki:

```bash
# Start Docker Compose stack
cd observability/
docker-compose up -d

# Verify services
docker ps
# Should see: prometheus, grafana, loki

# Access UIs:
# - Grafana: http://localhost:3000 (admin/admin)
# - Prometheus: http://localhost:9090
# - Loki: http://localhost:3100
```

**Reference**: `documentation/Dashboard-Setup-Guide-1.3.md`

---

## Understanding the GraphRAG Pipeline

### Pipeline Architecture

```
Input Text
    ↓
┌─────────────────────────────────────────────────────────────┐
│  EXTRACTION STAGE                                           │
│  • Extract entities from text                               │
│  • Extract relationships                                    │
│  • Generate embeddings                                      │
│  Output: Raw entities + relationships                       │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  RESOLUTION STAGE                                           │
│  • Detect duplicate entities                                │
│  • Merge duplicates (e.g., "Apple" + "Apple Inc." → 1)    │
│  • Consolidate relationships                                │
│  Output: Resolved entities (typically 60-80% fewer)        │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  GRAPH CONSTRUCTION STAGE                                   │
│  • Build graph structure                                    │
│  • Create nodes (entities)                                  │
│  • Create edges (relationships)                             │
│  Output: Knowledge graph                                    │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  COMMUNITY DETECTION STAGE                                  │
│  • Identify entity clusters                                 │
│  • Calculate modularity                                     │
│  • Assign community IDs                                     │
│  Output: Graph with communities                             │
└─────────────────────────────────────────────────────────────┘
    ↓
Knowledge Graph (queryable)
```

### Data Flow with Observability

```
Pipeline Stage
    ↓
┌─────────────────────┐
│ Transformation      │ ──→ transformation_logs (MongoDB)
│ Logging             │     • What changed?
│                     │     • Why?
│                     │     • When?
└─────────────────────┘
    ↓
┌─────────────────────┐
│ Intermediate Data   │ ──→ intermediate_data_* (MongoDB)
│ Snapshots           │     • Data before stage
│                     │     • Data after stage
└─────────────────────┘
    ↓
┌─────────────────────┐
│ Quality Metrics     │ ──→ quality_metrics (MongoDB)
│ Calculation         │     • 23 metrics tracked
│                     │     • Per-stage metrics
└─────────────────────┘
    ↓
┌─────────────────────┐
│ Performance         │ ──→ Prometheus + Grafana
│ Monitoring          │     • Runtime metrics
│                     │     • System resources
└─────────────────────┘
```

**References**:
- `documentation/guides/GRAPHRAG-TRANSFORMATION-LOGGING.md` - Transformation logging details
- `documentation/guides/INTERMEDIATE-DATA-ANALYSIS.md` - Intermediate data structure
- `documentation/guides/QUALITY-METRICS.md` - All 23 metrics explained

### Key Collections in MongoDB

After a pipeline run, you'll have these collections:

**Core Data**:
- `entities` - Final resolved entities
- `relationships` - Entity relationships
- `communities` - Community detection results

**Observability Data**:
- `transformation_logs` - Every transformation tracked (merges, creates, skips)
- `intermediate_data_extraction` - Snapshot after extraction
- `intermediate_data_resolution` - Snapshot after resolution
- `intermediate_data_construction` - Snapshot after construction
- `intermediate_data_detection` - Snapshot after detection
- `quality_metrics` - 23 metrics per pipeline run

**Reference**: `documentation/Observability-Collections-Report.md` (19 KB, 541 lines)

---

## Test Suite Organization

### Testing Phases

This guide is organized into 6 testing phases that mirror the achievement priorities:

| Phase | Focus | Achievements | Time |
|-------|-------|--------------|------|
| 1 | Infrastructure | 1.1-2.3 | 45 min |
| 2 | Data Collection | 3.1-3.3 | 30 min |
| 3 | Validation & Query | 4.1-4.3 | 60 min |
| 4 | Performance & Storage | 5.1-5.3 | 90 min |
| 5 | Tool Enhancements | 7.1 | 30 min |
| 6 | Production Readiness | 7.2-7.3 | 45 min |

**Total Time**: 4-6 hours (depending on pipeline run duration)

### Test Results Tracking

Create a test results file:

```bash
mkdir -p test-results/
cat > test-results/manual-test-run-$(date +%Y%m%d).md << 'EOF'
# Manual Test Run - $(date +%Y-%m-%d)

## Test Environment
- Tester: [Your Name]
- Date: $(date)
- MongoDB Version: [version]
- Python Version: [version]
- Branch/Commit: [git info]

## Test Results

### Phase 1: Infrastructure Testing
- [ ] Test 1.1: Transformation Logging
- [ ] Test 1.2: Intermediate Data
- [ ] Test 1.3: Prometheus Metrics
- [ ] Test 1.4: Grafana Dashboards
- [ ] Test 1.5: Loki Logging

[Continue for all phases...]

## Issues Found
[List any issues]

## Notes
[Any observations]
EOF
```

---

## Phase 1: Infrastructure Testing

**Goal**: Verify core observability infrastructure is working  
**Time**: ~45 minutes  
**Reference**: Achievements 1.1-2.3

### Test 1.1: Transformation Logging

**What This Tests**: Verifies that all pipeline transformations are logged to MongoDB

**Context**: The transformation logger tracks every entity merge, create, and skip operation. This is crucial for debugging and understanding pipeline behavior.

**Execution**: `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_11_01.md`

#### Step 1: Verify Logger Configuration

```bash
# Check that transformation logging is enabled
grep "TRANSFORMATION_LOGGING_ENABLED" .env
# Should output: TRANSFORMATION_LOGGING_ENABLED=true

# Verify the logger service exists
ls -la business/services/graphrag/transformation_logger.py
```

#### Step 2: Run a Pipeline with Logging

```bash
# Clear old transformation logs (optional)
mongosh mongodb://localhost:27017/graphrag --eval "db.transformation_logs.deleteMany({})"

# Run the GraphRAG pipeline
python -m business.services.graphrag.pipeline \
  --input data/input/test.txt \
  --output data/output/ \
  --trace-id "manual-test-$(date +%s)"

# Note the trace_id from output for later reference
```

**Expected Output**:
```
Starting GraphRAG pipeline...
Trace ID: manual-test-1234567890
Stage: extraction
  - Extracted 10 entities
  - Extracted 8 relationships
Stage: resolution
  - Resolved 10 raw entities to 4 entities (60% merge rate)
Stage: construction
  - Built graph with 4 nodes, 5 edges
Stage: detection
  - Detected 2 communities
Pipeline complete!
```

#### Step 3: Verify Transformation Logs

```bash
# Count transformation logs
mongosh mongodb://localhost:27017/graphrag --eval "
  db.transformation_logs.countDocuments({})
"

# Should see logs (typically 100-200 per run)

# View a sample merge log
mongosh mongodb://localhost:27017/graphrag --eval "
  db.transformation_logs.findOne({
    transformation_type: 'entity_merge'
  })
"
```

**Expected Result**:
```javascript
{
  _id: ObjectId("..."),
  trace_id: "manual-test-1234567890",
  timestamp: ISODate("2025-11-15T..."),
  stage: "resolution",
  transformation_type: "entity_merge",
  entity_id: "resolved_entity_123",
  details: {
    merged_from: ["raw_entity_456", "raw_entity_789"],
    reason: "high_similarity",
    similarity_score: 0.92
  }
}
```

#### Step 4: Run Validation Script

```bash
# Run transformation logging validation
cd observability/
./validate-transformation-logging.sh

# Should show all checks passing
```

**Expected Output**:
```
✓ MongoDB connection successful
✓ transformation_logs collection exists
✓ Transformation logs found: 150
✓ All transformation types present (merge, create, skip)
✓ All stages logged (extraction, resolution, construction, detection)
✓ Trace IDs are present
✓ Timestamps are valid
All checks passed!
```

**References**:
- Code: `business/services/graphrag/transformation_logger.py`
- Guide: `documentation/guides/GRAPHRAG-TRANSFORMATION-LOGGING.md`
- Execution: `execution/EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_11_01.md`

---

### Test 1.2: Intermediate Data Collection

**What This Tests**: Verifies that data snapshots are captured at each pipeline stage

**Context**: Intermediate data allows you to see exactly what the data looked like before and after each transformation stage.

**Execution**: `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_12_01.md`

#### Step 1: Verify Intermediate Data is Enabled

```bash
# Check environment configuration
grep "INTERMEDIATE_DATA_ENABLED" .env
# Should output: INTERMEDIATE_DATA_ENABLED=true
```

#### Step 2: Check Collections After Pipeline Run

```bash
# List all intermediate data collections
mongosh mongodb://localhost:27017/graphrag --eval "
  db.getCollectionNames().filter(name => name.startsWith('intermediate_data_'))
"
```

**Expected Output**:
```javascript
[
  "intermediate_data_extraction",
  "intermediate_data_resolution",
  "intermediate_data_construction",
  "intermediate_data_detection"
]
```

#### Step 3: Examine Intermediate Data

```bash
# Count documents in each collection
mongosh mongodb://localhost:27017/graphrag --eval "
  const stages = ['extraction', 'resolution', 'construction', 'detection'];
  stages.forEach(stage => {
    const count = db['intermediate_data_' + stage].countDocuments({});
    print(stage + ': ' + count + ' documents');
  });
"
```

**Expected Output**:
```
extraction: 10 documents
resolution: 4 documents
construction: 4 documents
detection: 4 documents
```

#### Step 4: Compare Before/After Resolution

```bash
# See the difference resolution made
python scripts/repositories/graphrag/queries/compare_before_after_resolution.py \
  --trace-id manual-test-1234567890
```

**Expected Output** (with color formatting from Achievement 7.1):
```
=== Raw vs Resolved Entity Comparison ===

Trace ID: manual-test-1234567890

RAW ENTITIES (before resolution): 10 entities
  • Apple Inc. (type: ORGANIZATION)
  • Apple (type: ORGANIZATION)
  • iPhone (type: PRODUCT)
  • Steve Jobs (type: PERSON)
  ...

RESOLVED ENTITIES (after resolution): 4 entities
  • Apple Inc. (type: ORGANIZATION)
    ← Merged from: ["Apple Inc.", "Apple"]
  • iPhone (type: PRODUCT)
  • Steve Jobs (type: PERSON)
  ...

MERGE STATISTICS:
  • Merge rate: 60.0%
  • Original count: 10
  • After resolution: 4
  • Entities merged: 6
```

**References**:
- Code: `business/services/graphrag/intermediate_data.py`
- Guide: `documentation/guides/INTERMEDIATE-DATA-ANALYSIS.md`
- Script: `scripts/repositories/graphrag/queries/compare_before_after_resolution.py`

---

### Test 1.3: Prometheus Metrics Endpoint

**What This Tests**: Verifies that performance metrics are exposed for Prometheus

**Context**: Prometheus scrapes metrics from the `/metrics` endpoint for monitoring pipeline performance.

**Execution**: `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_21_01.md`

#### Step 1: Verify Metrics Service

```bash
# Check if metrics exporter is running
curl http://localhost:8000/metrics

# Or check specific metric
curl http://localhost:8000/metrics | grep graphrag_pipeline
```

**Expected Output** (sample metrics):
```
# HELP graphrag_pipeline_runs_total Total number of pipeline runs
# TYPE graphrag_pipeline_runs_total counter
graphrag_pipeline_runs_total 5.0

# HELP graphrag_pipeline_duration_seconds Pipeline execution duration
# TYPE graphrag_pipeline_duration_seconds histogram
graphrag_pipeline_duration_seconds_bucket{le="10.0"} 0.0
graphrag_pipeline_duration_seconds_bucket{le="30.0"} 3.0
graphrag_pipeline_duration_seconds_bucket{le="60.0"} 5.0
graphrag_pipeline_duration_seconds_count 5.0
graphrag_pipeline_duration_seconds_sum 187.5

# HELP graphrag_entities_extracted Total entities extracted
# TYPE graphrag_entities_extracted gauge
graphrag_entities_extracted{stage="extraction"} 10.0
graphrag_entities_extracted{stage="resolution"} 4.0
```

#### Step 2: Verify Prometheus is Scraping

If you started the observability stack:

```bash
# Check Prometheus targets
open http://localhost:9090/targets

# Run a query in Prometheus
open http://localhost:9090/graph
# Query: rate(graphrag_pipeline_runs_total[5m])
```

#### Step 3: Test PromQL Queries

```bash
# Test some PromQL queries via API
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=graphrag_pipeline_runs_total'

curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=rate(graphrag_pipeline_duration_seconds_sum[5m])'
```

**References**:
- Code: `business/services/graphrag/metrics_exporter.py`
- Guide: `documentation/Environment-Variables-Guide.md`
- Examples: `documentation/PromQL-Examples-Achievement-1.2.md`
- Report: `documentation/Metrics-Endpoint-Validation-Report-1.2.md`

---

### Test 1.4: Grafana Dashboards

**What This Tests**: Verifies that Grafana dashboards visualize pipeline metrics

**Context**: Grafana provides real-time visualization of pipeline performance, quality metrics, and system health.

**Execution**: `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_22_01.md`

#### Step 1: Access Grafana

```bash
# Open Grafana in browser
open http://localhost:3000

# Login credentials (default)
# Username: admin
# Password: admin
```

#### Step 2: Verify Prometheus Data Source

1. Navigate to: Configuration → Data Sources
2. Click on "Prometheus"
3. Verify URL: `http://prometheus:9090`
4. Click "Test" button
5. Should see: "Data source is working"

#### Step 3: Import/Verify Dashboards

```bash
# Check if dashboards are provisioned
ls -la observability/grafana/dashboards/

# Should see:
# - graphrag-pipeline-overview.json
# - graphrag-quality-metrics.json
# - graphrag-performance.json
```

In Grafana UI:
1. Go to: Dashboards → Browse
2. Should see 3 dashboards:
   - GraphRAG Pipeline Overview
   - GraphRAG Quality Metrics
   - GraphRAG Performance

#### Step 4: Test Dashboard Panels

Open "GraphRAG Pipeline Overview" dashboard:

**Expected Panels**:
- Pipeline Runs (counter)
- Average Pipeline Duration (graph)
- Entities Extracted vs Resolved (comparison)
- Stage Durations (bar chart)
- Success Rate (percentage)
- Recent Errors (table)

**Verify Data**:
- All panels should show data (not "No data")
- Time range selector works
- Refresh works
- Panels are interactive (clickable)

#### Step 5: Test Dashboard Queries

Click "Edit" on any panel to see the PromQL query:

Example queries you should see:
```promql
# Pipeline runs over time
rate(graphrag_pipeline_runs_total[5m])

# Average duration
rate(graphrag_pipeline_duration_seconds_sum[5m]) / 
rate(graphrag_pipeline_duration_seconds_count[5m])

# Entity merge rate
(graphrag_entities_extracted{stage="extraction"} - 
 graphrag_entities_extracted{stage="resolution"}) / 
graphrag_entities_extracted{stage="extraction"} * 100
```

**References**:
- Setup: `documentation/Dashboard-Setup-Guide-1.3.md`
- Queries: `documentation/Dashboard-Queries-1.3.md`
- Debug: `documentation/Grafana-Dashboards-Debug-Log-1.3.md`
- Summary: `execution/ACHIEVEMENT-2.2-COMPLETION-SUMMARY.md`

---

### Test 1.5: Loki Log Aggregation

**What This Tests**: Verifies that application logs are aggregated in Loki

**Context**: Loki provides centralized log storage and querying capabilities.

**Execution**: `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_23_01.md`

#### Step 1: Verify Loki is Running

```bash
# Check Loki health
curl http://localhost:3100/ready

# Should return: ready
```

#### Step 2: Query Logs via Loki API

```bash
# Get recent logs
curl -G http://localhost:3100/loki/api/v1/query \
  --data-urlencode 'query={job="graphrag"}' \
  --data-urlencode 'limit=10'
```

#### Step 3: View Logs in Grafana

In Grafana:
1. Go to: Explore
2. Select: Loki data source
3. Query: `{job="graphrag"}`
4. Should see: Application logs

**Example log entries**:
```
[INFO] Starting pipeline execution (trace_id=manual-test-1234567890)
[INFO] Extraction stage: Extracted 10 entities
[INFO] Resolution stage: Merged 6 entities (60% reduction)
[INFO] Pipeline completed successfully
```

#### Step 4: Filter Logs by Level

Test log filtering:
```
{job="graphrag", level="error"}
{job="graphrag", level="warn"}
{job="graphrag", stage="resolution"}
```

**References**:
- Summary: `execution/ACHIEVEMENT-2.3-COMPLETION-SUMMARY.md`
- Configuration: `observability/docker-compose.yml`

---

## Phase 2: Data Collection Testing

**Goal**: Validate that all observability data is collected correctly  
**Time**: ~30 minutes  
**Reference**: Achievements 3.1-3.3

### Test 2.1: Validation Script Framework

**What This Tests**: Verifies the validation script framework works

**Context**: Validation scripts provide automated checks for each achievement.

**Execution**: `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_31_01.md`

#### Step 1: List All Validation Scripts

```bash
ls -la observability/validate-*.sh

# Should see multiple scripts:
# - validate-transformation-logging.sh
# - validate-intermediate-data.sh
# - validate-quality-metrics.sh
# - validate-achievement-51.sh (Achievement 5.1)
# - validate-achievement-52.sh (Achievement 5.2)
# - validate-achievement-53.sh (Achievement 5.3)
# - validate-achievement-71.sh (Achievement 7.1)
# - validate-achievement-72.sh (Achievement 7.2)
# - validate-achievement-73.sh (Achievement 7.3)
```

#### Step 2: Run a Validation Script

```bash
cd observability/

# Make scripts executable
chmod +x validate-*.sh

# Run transformation logging validation
./validate-transformation-logging.sh
```

**Expected Output Format**:
```
════════════════════════════════════════════════════════════
Validating: Transformation Logging
════════════════════════════════════════════════════════════

Testing MongoDB Connection...
✓ MongoDB connection successful

Testing transformation_logs Collection...
✓ Collection exists
✓ Documents found: 150

Testing Transformation Types...
✓ entity_merge logs found: 6
✓ entity_create logs found: 4
✓ entity_skip logs found: 0

Testing Stages Coverage...
✓ extraction logs: 10
✓ resolution logs: 6
✓ construction logs: 4
✓ detection logs: 4

Testing Data Quality...
✓ All logs have trace_id
✓ All logs have timestamp
✓ All logs have stage
✓ All logs have transformation_type

════════════════════════════════════════════════════════════
✅ ALL CHECKS PASSED (15/15)
════════════════════════════════════════════════════════════
```

#### Step 3: Run Multiple Validation Scripts

```bash
# Run all validation scripts
for script in validate-*.sh; do
  echo ""
  echo "Running $script..."
  ./$script || echo "FAILED: $script"
done
```

**References**:
- Framework: `execution/ACHIEVEMENT-3.1-DESIGN-COMPLETE.md`
- Implementation: `execution/EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_31_01.md`

---

### Test 2.2: End-to-End Integration Testing

**What This Tests**: Verifies all observability components work together

**Context**: This tests the complete data flow from pipeline execution to observability storage.

**Execution**: `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_33_01.md`

#### Step 1: Clear All Observability Data

```bash
# Clear all observability collections
mongosh mongodb://localhost:27017/graphrag --eval "
  db.transformation_logs.deleteMany({});
  db.quality_metrics.deleteMany({});
  db.intermediate_data_extraction.deleteMany({});
  db.intermediate_data_resolution.deleteMany({});
  db.intermediate_data_construction.deleteMany({});
  db.intermediate_data_detection.deleteMany({});
  print('All observability data cleared');
"
```

#### Step 2: Run Complete Pipeline

```bash
# Generate unique trace ID
TRACE_ID="e2e-test-$(date +%s)"

# Run pipeline with all observability enabled
python -m business.services.graphrag.pipeline \
  --input data/input/test.txt \
  --output data/output/ \
  --trace-id "$TRACE_ID"

# Save trace ID for later
echo "$TRACE_ID" > test-results/last-trace-id.txt
```

#### Step 3: Verify All Data Was Collected

```bash
TRACE_ID=$(cat test-results/last-trace-id.txt)

# Check transformation logs
mongosh mongodb://localhost:27017/graphrag --eval "
  const count = db.transformation_logs.countDocuments({trace_id: '$TRACE_ID'});
  print('Transformation logs: ' + count);
  if (count === 0) {
    print('ERROR: No transformation logs found!');
    quit(1);
  }
"

# Check intermediate data
mongosh mongodb://localhost:27017/graphrag --eval "
  const stages = ['extraction', 'resolution', 'construction', 'detection'];
  stages.forEach(stage => {
    const count = db['intermediate_data_' + stage].countDocuments({trace_id: '$TRACE_ID'});
    print('Intermediate data (' + stage + '): ' + count);
    if (count === 0) {
      print('ERROR: No data for ' + stage);
    }
  });
"

# Check quality metrics
mongosh mongodb://localhost:27017/graphrag --eval "
  const count = db.quality_metrics.countDocuments({trace_id: '$TRACE_ID'});
  print('Quality metrics: ' + count);
  if (count === 0) {
    print('ERROR: No quality metrics found!');
    quit(1);
  }
"
```

**Expected Output**:
```
Transformation logs: 150
Intermediate data (extraction): 10
Intermediate data (resolution): 4
Intermediate data (construction): 4
Intermediate data (detection): 4
Quality metrics: 23
```

#### Step 4: Run Comprehensive Test Script

```bash
cd observability/
./validate-e2e-integration.sh --trace-id "$TRACE_ID"
```

**References**:
- Test Results: `execution/ACHIEVEMENT-3.3-TEST-RESULTS.md`
- Final Results: `execution/ACHIEVEMENT-3.3-FINAL-TEST-RESULTS.md`
- Summary: `execution/ACHIEVEMENT-3.3-COMPLETION-SUMMARY.md`

---

## Phase 3: Validation & Query Testing

**Goal**: Test all query scripts and analysis tools  
**Time**: ~60 minutes  
**Reference**: Achievements 4.1-4.3

### Test 3.1: Query Scripts

**What This Tests**: Verifies all query scripts for analyzing observability data

**Context**: Query scripts let you analyze pipeline behavior, compare runs, and debug issues.

**Execution**: `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_41_01.md`

#### Step 1: List Available Query Scripts

```bash
ls -la scripts/repositories/graphrag/queries/

# Should see:
# - compare_before_after_resolution.py
# - analyze_entity_merges.py
# - trace_pipeline_flow.py
# - query_quality_metrics.py
# - find_similar_runs.py
# - query_utils.py (utility functions)
```

#### Step 2: Test Compare Before/After Resolution

```bash
TRACE_ID=$(cat test-results/last-trace-id.txt)

python scripts/repositories/graphrag/queries/compare_before_after_resolution.py \
  --trace-id "$TRACE_ID"
```

**Expected Output** (from Achievement 7.1 enhancements):
```
╔═══════════════════════════════════════════════════════════════╗
║  Raw vs Resolved Entity Comparison                            ║
╚═══════════════════════════════════════════════════════════════╝

Trace ID: e2e-test-1234567890
Date: 2025-11-15 10:30:15

RAW ENTITIES (before resolution):
  Count: 10 entities
  Types: ORGANIZATION (4), PERSON (3), PRODUCT (2), LOCATION (1)

RESOLVED ENTITIES (after resolution):
  Count: 4 entities  ✓ (60% reduction)
  Types: ORGANIZATION (2), PERSON (1), PRODUCT (1)

MERGE ANALYSIS:
  Entity: "Apple Inc." (ORGANIZATION)
    ← Merged: "Apple", "Apple Inc."
    Reason: High similarity (0.92)
    Confidence: 95%
  
  Entity: "Steve Jobs" (PERSON)
    ← Merged: "Steve Jobs", "S. Jobs", "Jobs"
    Reason: Name variants
    Confidence: 88%

STATISTICS:
  Merge Rate: 60.0% ✓
  Avg Similarity: 0.89
  Avg Confidence: 91.5%
  Total Merges: 6

══════════════════════════════════════════════════════════════════
```

#### Step 3: Test Entity Merge Analysis

```bash
python scripts/repositories/graphrag/queries/analyze_entity_merges.py \
  --trace-id "$TRACE_ID" \
  --min-similarity 0.8
```

**Expected Output**:
```
Entity Merge Analysis
=====================

High-Confidence Merges (>0.9 similarity):
  1. "Apple Inc." ← ["Apple", "Apple Inc."] (similarity: 0.92)
  2. "Steve Jobs" ← ["Steve Jobs", "S. Jobs"] (similarity: 0.91)

Medium-Confidence Merges (0.8-0.9 similarity):
  3. "Jobs" → "Steve Jobs" (similarity: 0.85)

Total Merges: 3
Average Similarity: 0.89
```

#### Step 4: Test Trace Pipeline Flow

```bash
python scripts/repositories/graphrag/queries/trace_pipeline_flow.py \
  --trace-id "$TRACE_ID"
```

**Expected Output**:
```
Pipeline Flow: e2e-test-1234567890
==================================

Stage 1: EXTRACTION (10.5s)
  Input: 1 text file
  Output: 10 entities, 8 relationships
  Transformations: 10 entity_create
  
Stage 2: RESOLUTION (5.2s)
  Input: 10 raw entities
  Output: 4 resolved entities
  Transformations: 6 entity_merge, 4 entity_keep
  Merge Rate: 60%
  
Stage 3: CONSTRUCTION (2.1s)
  Input: 4 entities, 8 relationships
  Output: Graph with 4 nodes, 5 edges
  Transformations: 4 node_create, 5 edge_create
  
Stage 4: DETECTION (3.8s)
  Input: Graph with 4 nodes
  Output: 2 communities detected
  Modularity: 0.87

Total Duration: 21.6s
```

#### Step 5: Test Query with Pagination and Caching

The query scripts now support pagination and caching (Achievement 7.1):

```bash
# Query with pagination
python scripts/repositories/graphrag/queries/compare_before_after_resolution.py \
  --trace-id "$TRACE_ID" \
  --page-size 5

# Output will paginate results (press Enter to see next page)

# Query with caching (second run should be faster)
time python scripts/repositories/graphrag/queries/compare_before_after_resolution.py \
  --trace-id "$TRACE_ID" \
  --use-cache

# Run again to test cache
time python scripts/repositories/graphrag/queries/compare_before_after_resolution.py \
  --trace-id "$TRACE_ID" \
  --use-cache
# Should be significantly faster (cached)
```

**References**:
- Validation: `documentation/Query-Scripts-Validation-Report.md` (14 KB, 492 lines)
- Examples: `documentation/Query-Scripts-Example-Outputs.md` (19 KB, 649 lines)
- Documentation: `documentation/Query-Scripts-Documentation-Updates.md` (16 KB, 592 lines)
- Bug Log: `documentation/Query-Scripts-Bug-Log.md` (9.8 KB, 358 lines)
- README: `scripts/repositories/graphrag/queries/README.md` (updated in 7.1)
- Execution: `execution/EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_41_01.md`

---

### Test 3.2: Explanation Tools

**What This Tests**: Verifies tools that explain WHY transformations happened

**Context**: Explanation tools help you understand the reasoning behind entity merges and other transformations.

**Execution**: `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_42_01.md`

#### Step 1: List Explanation Scripts

```bash
ls -la scripts/repositories/graphrag/explain/

# Should see:
# - explain_entity_merge.py
# - explain_similarity_calculation.py
# - explain_community_assignment.py
```

#### Step 2: Test Explain Entity Merge

```bash
# Get a merged entity ID from previous query
# Or use this query to find one:
ENTITY_ID=$(mongosh mongodb://localhost:27017/graphrag --quiet --eval "
  db.transformation_logs.findOne(
    {transformation_type: 'entity_merge'},
    {entity_id: 1}
  ).entity_id
")

# Explain why this merge happened
python scripts/repositories/graphrag/explain/explain_entity_merge.py \
  --entity-id "$ENTITY_ID" \
  --trace-id "$TRACE_ID"
```

**Expected Output** (with color formatting from Achievement 7.1):
```
╔═══════════════════════════════════════════════════════════════╗
║  Entity Merge Explanation                                     ║
╚═══════════════════════════════════════════════════════════════╝

Target Entity: "Apple Inc." (ORGANIZATION)
Entity ID: resolved_entity_abc123

MERGE DETAILS:
  Merged From: 2 raw entities
    1. "Apple Inc." (raw_entity_456)
    2. "Apple" (raw_entity_789)

SIMILARITY ANALYSIS:
  Overall Similarity: 0.92 (HIGH)
    ✓ Name Similarity: 0.95
      • Levenshtein distance: 5
      • Normalized score: 0.95
    ✓ Type Match: 1.0 (both ORGANIZATION)
    ✓ Attribute Overlap: 0.85
      • Shared attributes: ["industry", "founded"]
      • Unique attributes: ["stock_symbol"] (raw_entity_456)

DECISION REASONING:
  ✓ Similarity above threshold (0.80)
  ✓ Same entity type
  ✓ High attribute overlap
  ✓ No conflicting information
  
CONFIDENCE: 95%

ACTION TAKEN:
  • Merged entities into single resolved entity
  • Preserved attributes from both sources
  • Updated relationships to point to resolved entity
  • Logged transformation

══════════════════════════════════════════════════════════════════
```

#### Step 3: Test Similarity Calculation Explanation

```bash
python scripts/repositories/graphrag/explain/explain_similarity_calculation.py \
  --entity-1 "raw_entity_456" \
  --entity-2 "raw_entity_789"
```

**Expected Output**:
```
Similarity Calculation Breakdown
=================================

Entity 1: "Apple Inc." (raw_entity_456)
Entity 2: "Apple" (raw_entity_789)

Name Similarity: 0.95
  • Algorithm: Levenshtein + Jaro-Winkler
  • String distance: 5 characters
  • Normalized: 0.95

Type Similarity: 1.0
  • Both: ORGANIZATION
  • Perfect match

Attribute Similarity: 0.85
  • Shared: industry, founded
  • Entity 1 only: stock_symbol
  • Entity 2 only: (none)
  • Jaccard index: 0.85

Overall Similarity: 0.92
  • Weighted average:
    - Name (50%): 0.95 × 0.5 = 0.475
    - Type (30%): 1.0 × 0.3 = 0.300
    - Attributes (20%): 0.85 × 0.2 = 0.170
    - Total: 0.945 → 0.92 (rounded)

Threshold: 0.80
Result: MERGE (similarity above threshold)
```

**References**:
- Validation: `documentation/Explanation-Tools-Validation-Report.md` (7.2 KB, 247 lines)
- Summary: `documentation/Explanation-Tools-Summary.md` (1.8 KB, 71 lines)
- README: `scripts/repositories/graphrag/explain/README.md` (updated in 6.1)
- Execution: `execution/EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_42_01.md`

---

### Test 3.3: Quality Metrics Analysis

**What This Tests**: Verifies quality metrics are calculated and stored correctly

**Context**: Quality metrics provide 23 different measurements of pipeline health and output quality.

**Execution**: `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_43_01.md`

#### Step 1: Query All Quality Metrics

```bash
TRACE_ID=$(cat test-results/last-trace-id.txt)

python scripts/repositories/graphrag/queries/query_quality_metrics.py \
  --trace-id "$TRACE_ID"
```

**Expected Output**:
```
╔═══════════════════════════════════════════════════════════════╗
║  Quality Metrics Report                                       ║
╚═══════════════════════════════════════════════════════════════╝

Trace ID: e2e-test-1234567890
Total Metrics: 23

EXTRACTION STAGE (6 metrics):
  entity_count: 10 ✓ (within healthy range: 1-1000)
  relationship_count: 8 ✓ (within healthy range: 1-500)
  avg_entity_confidence: 0.89 ✓ (within healthy range: 0.7-1.0)
  entity_type_diversity: 0.75 ✓ (within healthy range: 0.5-1.0)
  extraction_coverage: 0.92 ✓ (within healthy range: 0.8-1.0)
  extraction_duration_seconds: 10.5 ✓

RESOLUTION STAGE (7 metrics):
  raw_entity_count: 10
  resolved_entity_count: 4 ✓
  merge_rate: 0.60 ✓ (within healthy range: 0.3-0.8)
  avg_merge_confidence: 0.91 ✓ (within healthy range: 0.7-1.0)
  avg_similarity_score: 0.89 ✓ (within healthy range: 0.7-1.0)
  entity_reduction_ratio: 0.60 ✓
  resolution_duration_seconds: 5.2 ✓

CONSTRUCTION STAGE (5 metrics):
  node_count: 4 ✓
  edge_count: 5 ✓
  avg_node_degree: 2.5 ✓ (within healthy range: 1-10)
  graph_density: 0.42 ✓ (within healthy range: 0.1-0.8)
  construction_duration_seconds: 2.1 ✓

DETECTION STAGE (5 metrics):
  community_count: 2 ✓ (within healthy range: 1-50)
  modularity_score: 0.87 ✓ (within healthy range: 0.3-1.0)
  avg_community_size: 2.0 ✓
  community_balance: 0.85 ✓ (within healthy range: 0.5-1.0)
  detection_duration_seconds: 3.8 ✓

OVERALL HEALTH: ✓ HEALTHY (23/23 metrics in range)

══════════════════════════════════════════════════════════════════
```

#### Step 2: Test Metrics Over Time

```bash
# Compare current run with previous runs
python scripts/repositories/graphrag/queries/compare_metrics_over_time.py \
  --last-n-runs 5
```

**Expected Output**:
```
Metrics Trends (Last 5 Runs)
============================

Merge Rate:
  Run 1: 0.58
  Run 2: 0.62
  Run 3: 0.55
  Run 4: 0.60
  Run 5: 0.60 (current)
  
  Trend: Stable ✓
  Average: 0.59
  Std Dev: 0.03

Modularity Score:
  Run 1: 0.85
  Run 2: 0.88
  Run 3: 0.84
  Run 4: 0.89
  Run 5: 0.87 (current)
  
  Trend: Stable ✓
  Average: 0.87
  Std Dev: 0.02

[Continue for other metrics...]
```

#### Step 3: Validate Metric Accuracy

```bash
# Run the quality metrics validation
cd observability/
./validate-quality-metrics.sh --trace-id "$TRACE_ID"
```

**Expected Output**:
```
✓ All 23 metrics present
✓ All metrics have valid values
✓ All metrics in healthy ranges
✓ Stage-specific metrics correct
✓ Metric calculations verified
All checks passed!
```

**References**:
- Guide: `documentation/guides/QUALITY-METRICS.md` (updated in 6.1)
- Validation: `documentation/Quality-Metrics-Validation-Report.md` (9.1 KB, 328 lines)
- Accuracy: `documentation/Quality-Metrics-Accuracy-Results.md` (12 KB, 386 lines)
- API Tests: `documentation/Quality-Metrics-API-Tests.md` (10 KB, 442 lines)
- Future Guide: `documentation/Quality-Metrics-Future-Validation-Guide.md` (12 KB, 483 lines)
- Execution: `execution/EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_43_01.md`

---

## Phase 4: Performance & Storage Testing

**Goal**: Measure and validate performance impact and storage usage  
**Time**: ~90 minutes  
**Reference**: Achievements 5.1-5.3

### Test 4.1: Performance Impact Measurement

**What This Tests**: Measures the performance overhead of observability features

**Context**: We need to ensure observability adds <5% overhead to pipeline execution.

**Execution**: `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_51_01.md`

#### Step 1: Run Baseline (No Observability)

```bash
# Disable all observability features
cat > .env.baseline << 'EOF'
TRANSFORMATION_LOGGING_ENABLED=false
INTERMEDIATE_DATA_ENABLED=false
QUALITY_METRICS_ENABLED=false
PROMETHEUS_METRICS_ENABLED=false
EOF

# Run pipeline 3 times for average
for i in {1..3}; do
  echo "Baseline run $i..."
  time python -m business.services.graphrag.pipeline \
    --input data/input/test.txt \
    --output data/output/baseline-$i/ \
    2>&1 | tee test-results/baseline-run-$i.log
done

# Calculate average time
grep "real" test-results/baseline-run-*.log | \
  awk '{sum+=$2; count++} END {print "Average: " sum/count "s"}'
```

**Expected Output**:
```
Baseline run 1... 18.5s
Baseline run 2... 18.2s
Baseline run 3... 18.7s
Average: 18.47s
```

#### Step 2: Run with All Observability Enabled

```bash
# Enable all observability features
cat > .env.observability << 'EOF'
TRANSFORMATION_LOGGING_ENABLED=true
INTERMEDIATE_DATA_ENABLED=true
QUALITY_METRICS_ENABLED=true
PROMETHEUS_METRICS_ENABLED=true
EOF

cp .env.observability .env

# Run pipeline 3 times for average
for i in {1..3}; do
  echo "Observability run $i..."
  time python -m business.services.graphrag.pipeline \
    --input data/input/test.txt \
    --output data/output/observability-$i/ \
    --trace-id "perf-test-$i" \
    2>&1 | tee test-results/observability-run-$i.log
done

# Calculate average time
grep "real" test-results/observability-run-*.log | \
  awk '{sum+=$2; count++} END {print "Average: " sum/count "s"}'
```

**Expected Output**:
```
Observability run 1... 19.2s
Observability run 2... 19.4s
Observability run 3... 19.1s
Average: 19.23s
```

#### Step 3: Calculate Overhead

```bash
cat > test-results/performance-comparison.sh << 'EOF'
#!/bin/bash

BASELINE_AVG=18.47
OBSERVABILITY_AVG=19.23

OVERHEAD=$(echo "scale=2; ($OBSERVABILITY_AVG - $BASELINE_AVG) / $BASELINE_AVG * 100" | bc)

echo "Performance Impact Analysis"
echo "==========================="
echo ""
echo "Baseline (no observability): ${BASELINE_AVG}s"
echo "With observability: ${OBSERVABILITY_AVG}s"
echo "Overhead: ${OVERHEAD}%"
echo ""

if (( $(echo "$OVERHEAD < 5" | bc -l) )); then
  echo "✓ PASS: Overhead is less than 5% target"
else
  echo "✗ FAIL: Overhead exceeds 5% target"
fi
EOF

bash test-results/performance-comparison.sh
```

**Expected Output**:
```
Performance Impact Analysis
===========================

Baseline (no observability): 18.47s
With observability: 19.23s
Overhead: 4.11%

✓ PASS: Overhead is less than 5% target
```

#### Step 4: Per-Feature Overhead Analysis

Test each feature individually:

```bash
# Test transformation logging only
echo "TRANSFORMATION_LOGGING_ENABLED=true
INTERMEDIATE_DATA_ENABLED=false
QUALITY_METRICS_ENABLED=false" > .env

time python -m business.services.graphrag.pipeline \
  --input data/input/test.txt \
  --output data/output/test-logging-only/

# Test intermediate data only
echo "TRANSFORMATION_LOGGING_ENABLED=false
INTERMEDIATE_DATA_ENABLED=true
QUALITY_METRICS_ENABLED=false" > .env

time python -m business.services.graphrag.pipeline \
  --input data/input/test.txt \
  --output data/output/test-intermediate-only/

# Test quality metrics only
echo "TRANSFORMATION_LOGGING_ENABLED=false
INTERMEDIATE_DATA_ENABLED=false
QUALITY_METRICS_ENABLED=true" > .env

time python -m business.services.graphrag.pipeline \
  --input data/input/test.txt \
  --output data/output/test-metrics-only/
```

**Expected Results** (from Achievement 5.1):
- Transformation Logging: ~0.6% overhead
- Intermediate Data: ~1.7% overhead
- Quality Metrics: ~2.0% overhead
- **Total**: <5% overhead ✓

#### Step 5: Run Validation Script

```bash
cd observability/
./validate-achievement-51.sh
```

**References**:
- **Analysis**: `documentation/Performance-Impact-Analysis.md` ⭐ (13 KB, 435 lines)
- **Breakdown**: `documentation/Feature-Overhead-Breakdown.md` ⭐ (13 KB, 527 lines)
- **Recommendations**: `documentation/Optimization-Recommendations.md` ⭐ (14 KB, 580 lines)
- Execution: `execution/EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_51_01.md`
- Approval: `execution/feedbacks/APPROVED_51.md`

---

### Test 4.2: Storage Growth Analysis

**What This Tests**: Measures storage consumed by observability data

**Context**: We need to ensure observability data stays under 500 MB and that TTL (Time-To-Live) works.

**Execution**: `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_52_01.md`

#### Step 1: Measure Collection Sizes

```bash
# Create storage analysis script
cat > test-results/measure-storage.sh << 'EOF'
#!/bin/bash

echo "Storage Analysis"
echo "==============="
echo ""

mongosh mongodb://localhost:27017/graphrag --quiet --eval "
  const collections = [
    'transformation_logs',
    'intermediate_data_extraction',
    'intermediate_data_resolution',
    'intermediate_data_construction',
    'intermediate_data_detection',
    'quality_metrics'
  ];
  
  let total = 0;
  
  collections.forEach(coll => {
    const stats = db[coll].stats();
    const sizeMB = (stats.size / 1024 / 1024).toFixed(2);
    total += stats.size;
    print(coll + ': ' + sizeMB + ' MB (' + stats.count + ' docs)');
  });
  
  const totalMB = (total / 1024 / 1024).toFixed(2);
  print('');
  print('Total Observability Storage: ' + totalMB + ' MB');
  print('Target: < 500 MB');
  
  if (total < 500 * 1024 * 1024) {
    print('✓ PASS: Under 500 MB limit');
  } else {
    print('✗ FAIL: Exceeds 500 MB limit');
  }
"
EOF

bash test-results/measure-storage.sh
```

**Expected Output** (from Achievement 5.2):
```
Storage Analysis
===============

transformation_logs: 28.5 MB (597 docs)
intermediate_data_extraction: 125.3 MB (10 docs)
intermediate_data_resolution: 98.7 MB (4 docs)
intermediate_data_construction: 112.4 MB (4 docs)
intermediate_data_detection: 115.2 MB (4 docs)
quality_metrics: 9.8 MB (23 docs)

Total Observability Storage: 489.9 MB
Target: < 500 MB
✓ PASS: Under 500 MB limit
```

#### Step 2: Test TTL (Time-To-Live) Indexes

```bash
# Verify TTL indexes exist
mongosh mongodb://localhost:27017/graphrag --eval "
  const collections = [
    'transformation_logs',
    'intermediate_data_extraction',
    'intermediate_data_resolution',
    'intermediate_data_construction',
    'intermediate_data_detection',
    'quality_metrics'
  ];
  
  print('TTL Index Verification');
  print('======================');
  print('');
  
  collections.forEach(coll => {
    const indexes = db[coll].getIndexes();
    const ttlIndex = indexes.find(idx => idx.expireAfterSeconds !== undefined);
    
    if (ttlIndex) {
      const days = ttlIndex.expireAfterSeconds / 86400;
      print('✓ ' + coll + ': TTL index found (' + days + ' days)');
    } else {
      print('✗ ' + coll + ': NO TTL index');
    }
  });
"
```

**Expected Output**:
```
TTL Index Verification
======================

✓ transformation_logs: TTL index found (30 days)
✓ intermediate_data_extraction: TTL index found (30 days)
✓ intermediate_data_resolution: TTL index found (30 days)
✓ intermediate_data_construction: TTL index found (30 days)
✓ intermediate_data_detection: TTL index found (30 days)
✓ quality_metrics: TTL index found (30 days)
```

#### Step 3: Simulate Long-Term Growth

```bash
# Project monthly growth
cat > test-results/project-growth.sh << 'EOF'
#!/bin/bash

CURRENT_SIZE_MB=489.9
RUNS_PER_DAY=10
DAYS_IN_MONTH=30

# Without TTL
GROWTH_PER_RUN_MB=$CURRENT_SIZE_MB
MONTHLY_WITHOUT_TTL=$(echo "$GROWTH_PER_RUN_MB * $RUNS_PER_DAY * $DAYS_IN_MONTH" | bc)

# With TTL (30 days)
MONTHLY_WITH_TTL=$(echo "$GROWTH_PER_RUN_MB * $RUNS_PER_DAY * 30" | bc)

echo "Storage Growth Projection"
echo "========================"
echo ""
echo "Current size (1 run): ${CURRENT_SIZE_MB} MB"
echo "Runs per day: ${RUNS_PER_DAY}"
echo ""
echo "WITHOUT TTL (infinite retention):"
echo "  Monthly growth: ${MONTHLY_WITHOUT_TTL} MB (~$( echo "$MONTHLY_WITHOUT_TTL / 1024" | bc ) GB)"
echo ""
echo "WITH TTL (30-day retention):"
echo "  Steady state: ${MONTHLY_WITH_TTL} MB (~$( echo "$MONTHLY_WITH_TTL / 1024" | bc ) GB)"
echo "  (Old data automatically deleted after 30 days)"
EOF

bash test-results/project-growth.sh
```

**Expected Output**:
```
Storage Growth Projection
========================

Current size (1 run): 489.9 MB
Runs per day: 10

WITHOUT TTL (infinite retention):
  Monthly growth: 146970 MB (~143 GB)

WITH TTL (30-day retention):
  Steady state: 146970 MB (~143 GB)
  (Old data automatically deleted after 30 days)
```

#### Step 4: Run Validation Script

```bash
cd observability/
./validate-achievement-52.sh
```

**References**:
- **Analysis**: `documentation/Storage-Impact-Analysis.md` ⭐ (9.2 KB, 340 lines)
- Execution: `execution/EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_52_01.md`
- Approval: `execution/feedbacks/APPROVED_52.md`

---

### Test 4.3: Cost-Benefit Assessment

**What This Tests**: Validates the comprehensive cost-benefit analysis of observability

**Context**: Synthesizes performance and storage data to make production recommendations.

**Execution**: `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_53_01.md`

#### Step 1: Review Cost-Benefit Analysis

```bash
# View the comprehensive analysis
cat documentation/Production-Recommendations.md | less

# Or view specific sections
grep -A 20 "## Feature Categorization" documentation/Production-Recommendations.md
```

**Key Findings** (from Achievement 5.3):

**COSTS**:
- Performance: <5% overhead (LOW)
- Storage: ~490 MB per run (MEDIUM)
- Code Complexity: 5,388 lines (MEDIUM)
- Maintenance: ~10 hours/quarter (LOW)

**BENEFITS**:
- Debugging: 10x improvement (VERY HIGH)
- Quality Visibility: 23 metrics (HIGH)
- Learning: 4-5x faster onboarding (HIGH)
- Experimentation: 5-7x faster tuning (VERY HIGH)

**VERDICT**: **STRONGLY RECOMMENDED** for production

#### Step 2: Review Feature Recommendations

```bash
# View recommended feature settings
grep -A 30 "### Always-On Features" documentation/Production-Recommendations.md
```

**Feature Categorization**:

**Always-On** (minimal overhead):
- Transformation Logging (~0.6% overhead)
- Quality Metrics (~2.0% overhead)
- Prometheus Metrics (negligible)

**Configurable** (enable as needed):
- Intermediate Data Storage (~1.7% overhead)
  - Enable in staging/debugging
  - Disable in production (unless needed)

**Dev-Only** (development environments):
- Detailed debug logging
- Verbose query output

#### Step 3: Test Feature Toggle Strategy

```bash
# Test different environment configurations

# Development environment
cat > .env.development << 'EOF'
OBSERVABILITY_PROFILE=development
TRANSFORMATION_LOGGING_ENABLED=true
INTERMEDIATE_DATA_ENABLED=true
QUALITY_METRICS_ENABLED=true
PROMETHEUS_METRICS_ENABLED=true
LOG_LEVEL=DEBUG
EOF

# Staging environment
cat > .env.staging << 'EOF'
OBSERVABILITY_PROFILE=staging
TRANSFORMATION_LOGGING_ENABLED=true
INTERMEDIATE_DATA_ENABLED=true
QUALITY_METRICS_ENABLED=true
PROMETHEUS_METRICS_ENABLED=true
LOG_LEVEL=INFO
EOF

# Production environment
cat > .env.production << 'EOF'
OBSERVABILITY_PROFILE=production
TRANSFORMATION_LOGGING_ENABLED=true
INTERMEDIATE_DATA_ENABLED=false
QUALITY_METRICS_ENABLED=true
PROMETHEUS_METRICS_ENABLED=true
LOG_LEVEL=WARNING
EOF

# Test production config
cp .env.production .env
python -m business.services.graphrag.pipeline \
  --input data/input/test.txt \
  --output data/output/prod-config-test/

# Verify only enabled features are active
mongosh mongodb://localhost:27017/graphrag --eval "
  print('Transformation logs: ' + db.transformation_logs.countDocuments({}));
  print('Intermediate data: ' + db.intermediate_data_extraction.countDocuments({}));
  print('Quality metrics: ' + db.quality_metrics.countDocuments({}));
"
```

**Expected Output** (production config):
```
Transformation logs: 150  ✓ (enabled)
Intermediate data: 0     ✓ (disabled)
Quality metrics: 23      ✓ (enabled)
```

#### Step 4: Run Validation Script

```bash
cd observability/
./validate-achievement-53.sh
```

**References**:
- **Recommendations**: `documentation/Production-Recommendations.md` ⭐ (21 KB, 803 lines)
- **Cost-Benefit Analysis**: `execution/EXECUTION_ANALYSIS_OBSERVABILITY-COST-BENEFIT.md` (685 lines)
- Execution: `execution/EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_53_01.md`
- Approval: `execution/feedbacks/APPROVED_53.md`

---

## Phase 5: Tool Enhancement Testing

**Goal**: Test enhanced query tools and performance optimizations  
**Time**: ~30 minutes  
**Reference**: Achievements 7.1-7.2

### Test 5.1: Tool Enhancements

**What This Tests**: Verifies color formatting, pagination, caching, and progress indicators

**Context**: Achievement 7.1 added 5 major enhancements to query scripts for better usability.

**Execution**: `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_71_01.md`

#### Step 1: Test Color Formatting

```bash
# Run query with color output
python scripts/repositories/graphrag/queries/compare_before_after_resolution.py \
  --trace-id "$TRACE_ID" \
  --color

# Should see:
# - Green for positive values
# - Red for warnings
# - Blue for headers
# - Yellow for metrics
```

#### Step 2: Test Pagination

```bash
# Query with pagination (5 results per page)
python scripts/repositories/graphrag/queries/analyze_entity_merges.py \
  --trace-id "$TRACE_ID" \
  --page-size 5

# Press Enter to see next page
# Type 'q' to quit
```

#### Step 3: Test Query Caching

```bash
# First run (no cache)
echo "First run (building cache)..."
time python scripts/repositories/graphrag/queries/compare_before_after_resolution.py \
  --trace-id "$TRACE_ID" \
  --use-cache

# Second run (cached)
echo "Second run (using cache)..."
time python scripts/repositories/graphrag/queries/compare_before_after_resolution.py \
  --trace-id "$TRACE_ID" \
  --use-cache

# Should be significantly faster
```

**Expected Output**:
```
First run (building cache)...
real    0m2.543s

Second run (using cache)...
real    0m0.187s  ✓ (93% faster)
```

#### Step 4: Test Progress Indicators

```bash
# Run script with progress bars
python scripts/repositories/graphrag/queries/trace_pipeline_flow.py \
  --trace-id "$TRACE_ID" \
  --show-progress

# Should show:
# Loading transformation logs... [████████████████████] 100%
# Processing stages... [████████████████████] 100%
```

#### Step 5: Run Enhancement Tests

```bash
# Run unit tests for enhancements
pytest tests/scripts/repositories/graphrag/queries/test_query_utils_enhancements.py -v

# Should see all tests pass
```

**Expected Output**:
```
test_color_formatting ... PASSED
test_pagination ... PASSED
test_query_cache ... PASSED
test_progress_indicators ... PASSED
test_format_color_value ... PASSED

5 passed in 0.43s
```

**References**:
- **Enhancement Report**: `documentation/Tool-Enhancement-Report.md` ⭐ (13 KB, 449 lines)
- Code: `scripts/repositories/graphrag/queries/query_utils.py`
- README: `scripts/repositories/graphrag/queries/README.md` (270+ lines added)
- Explain README: `scripts/repositories/graphrag/explain/README.md` (130+ lines added)
- Tests: `tests/scripts/repositories/graphrag/queries/test_query_utils_enhancements.py`
- Execution: `execution/EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_71_01.md`
- Approval: `execution/feedbacks/APPROVED_71.md`

---

### Test 5.2: Performance Optimizations

**What This Tests**: Verifies batch logging and MongoDB optimizations

**Context**: Achievement 7.2 reduced database writes by 99% through batch operations.

**Execution**: `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_72_01.md`

#### Step 1: Test Batch Transformation Logging

```bash
# Enable MongoDB profiling to see queries
mongosh mongodb://localhost:27017/graphrag --eval "
  db.setProfilingLevel(2);  // Profile all operations
  db.system.profile.drop(); // Clear old profile data
"

# Run pipeline with batching enabled
python -m business.services.graphrag.pipeline \
  --input data/input/test.txt \
  --output data/output/batch-test/ \
  --trace-id "batch-test-$(date +%s)"

# Check how many insert operations were performed
mongosh mongodb://localhost:27017/graphrag --eval "
  const inserts = db.system.profile.find({
    ns: 'graphrag.transformation_logs',
    op: 'insert'
  }).count();
  
  const insertMany = db.system.profile.find({
    ns: 'graphrag.transformation_logs',
    op: 'insert',
    command: { \$exists: true },
    'command.documents': { \$exists: true }
  }).count();
  
  print('Individual inserts (insert_one): ' + inserts);
  print('Batch inserts (insert_many): ' + insertMany);
  
  if (insertMany > 0) {
    print('✓ Batch logging is working');
  } else {
    print('✗ Batch logging not detected');
  }
"
```

**Expected Output** (from Achievement 7.2):
```
Individual inserts (insert_one): 0
Batch inserts (insert_many): 7  ✓

✓ Batch logging is working
```

**Impact**: 597 individual inserts → 7 batch inserts (99% reduction)

#### Step 2: Verify Batch Quality Metrics

```bash
# Check quality metrics batching
mongosh mongodb://localhost:27017/graphrag --eval "
  const inserts = db.system.profile.find({
    ns: 'graphrag.quality_metrics',
    op: 'insert'
  }).count();
  
  print('Quality metrics inserts: ' + inserts);
  
  if (inserts <= 5) {
    print('✓ Quality metrics batching is working');
  } else {
    print('✗ Too many individual inserts');
  }
"
```

**Expected Output**:
```
Quality metrics inserts: 4
✓ Quality metrics batching is working
```

#### Step 3: Measure Performance Improvement

```bash
# Measure overhead with optimizations
time python -m business.services.graphrag.pipeline \
  --input data/input/test.txt \
  --output data/output/optimized-test/

# Compare to original baseline (from Test 4.1)
# Original observability overhead: ~4.11%
# Optimized observability overhead: ~2.5%
# Improvement: ~40% reduction in overhead
```

#### Step 4: Run Unit Tests

```bash
# Test batch logging functionality
pytest tests/business/services/graphrag/test_transformation_logger.py -v

# Should see:
# - test_buffer_functionality PASSED
# - test_manual_flush PASSED
# - All other tests PASSED
```

#### Step 5: Run Validation Script

```bash
cd observability/
./validate-achievement-72.sh
```

**References**:
- **Optimization Report**: `documentation/Performance-Optimization-Report.md` ⭐ (12 KB, 380 lines)
- Code: `business/services/graphrag/transformation_logger.py` (batch buffering)
- Code: `business/services/graphrag/quality_metrics.py` (batch metrics)
- Tests: `tests/business/services/graphrag/test_transformation_logger.py`
- Validation: `observability/validate-achievement-72.sh`
- Execution: `execution/EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_72_01.md`

**Key Improvements**:
- Database writes: 597 → 7 (99% reduction)
- Transformation logging overhead: 0.6% → 0.3-0.4%
- Quality metrics overhead: 1.3-2.5% → 0.8-1.5%
- Total overhead: <5% → <3.5%

---

## Phase 6: Production Readiness Testing

**Goal**: Validate production deployment readiness  
**Time**: ~45 minutes  
**Reference**: Achievement 7.3

### Test 6.1: Production Readiness Checklist

**What This Tests**: Verifies all 187 pre-deployment checks

**Context**: The production readiness checklist ensures nothing is missed before deployment.

**Execution**: `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_73_01.md`

#### Step 1: Review Checklist

```bash
# Open the checklist
cat documentation/Production-Readiness-Checklist.md | less

# Or check specific sections
grep "## 1" documentation/Production-Readiness-Checklist.md -A 20
```

**10 Checklist Sections** (187 total items):
1. Environment Setup (15 items)
2. Configuration Management (18 items)
3. Infrastructure Deployment (22 items)
4. Database Validation (20 items)
5. Performance Validation (17 items)
6. Monitoring and Alerting (25 items)
7. Testing and Validation (20 items)
8. Documentation Review (15 items)
9. Security and Compliance (20 items)
10. Sign-Off and Approval (15 items)

#### Step 2: Complete Key Sections

**Environment Setup**:
```bash
# Check Python version
python --version  # ≥ 3.9 ✓

# Check MongoDB connection
mongosh mongodb://localhost:27017/ --eval "db.version()"  # ≥ 4.4 ✓

# Check Docker
docker --version  # ✓

# Verify environment variables
grep -E "MONGODB_URI|OBSERVABILITY" .env
```

**Configuration Management**:
```bash
# Validate .env file
python -c "
import os
from dotenv import load_dotenv

load_dotenv()

required = [
    'MONGODB_URI',
    'MONGODB_DATABASE',
    'TRANSFORMATION_LOGGING_ENABLED',
    'QUALITY_METRICS_ENABLED'
]

missing = [var for var in required if not os.getenv(var)]

if missing:
    print('✗ Missing variables:', missing)
else:
    print('✓ All required variables present')
"
```

**Database Validation**:
```bash
# Verify TTL indexes
mongosh mongodb://localhost:27017/graphrag --eval "
  const required = [
    'transformation_logs',
    'quality_metrics',
    'intermediate_data_extraction'
  ];
  
  required.forEach(coll => {
    const indexes = db[coll].getIndexes();
    const hasTTL = indexes.some(idx => idx.expireAfterSeconds !== undefined);
    print(coll + ': ' + (hasTTL ? '✓' : '✗'));
  });
"
```

#### Step 3: Run Automated Validation

```bash
cd observability/
./validate-achievement-73.sh
```

**Expected Output**:
```
════════════════════════════════════════════════════════════
Validating: Production Readiness Package (Achievement 7.3)
════════════════════════════════════════════════════════════

Testing Documentation Files...
✓ Production-Readiness-Checklist.md exists (187 items)
✓ Production-Deployment-Guide.md exists (813 lines)
✓ Operations-Runbook.md exists (1,078 lines)

Testing Checklist Content...
✓ All 10 sections present
✓ Environment setup section complete
✓ Configuration management section complete
[... all 187 items verified ...]

Testing Deployment Guide...
✓ Prerequisites section present
✓ Phased rollout strategy defined
✓ Rollback procedures documented

Testing Operations Runbook...
✓ Daily operations defined
✓ Monitoring procedures present
✓ Troubleshooting guide complete

════════════════════════════════════════════════════════════
✅ ALL CHECKS PASSED (57/57)
════════════════════════════════════════════════════════════
```

**References**:
- **Checklist**: `documentation/Production-Readiness-Checklist.md` ⭐ (13 KB, 418 lines, 187 items)
- **Deployment Guide**: `documentation/Production-Deployment-Guide.md` ⭐ (18 KB, 813 lines)
- **Operations Runbook**: `documentation/Operations-Runbook.md` ⭐ (25 KB, 1,078 lines)
- Validation: `observability/validate-achievement-73.sh`
- Execution: `execution/EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_73_01.md`

---

### Test 6.2: Deployment Procedures

**What This Tests**: Validates the phased deployment strategy

**Context**: The deployment guide provides a phased rollout strategy: Staging → Pilot → Production.

#### Step 1: Review Deployment Strategy

```bash
# View phased rollout plan
grep "### Phase" documentation/Production-Deployment-Guide.md -A 10
```

**Phased Rollout**:
1. **Staging Deployment** - Full testing in staging
2. **Pilot Deployment** - 10-20% of production traffic
3. **Production Rollout**:
   - Phase 1: 25% traffic
   - Phase 2: 50% traffic
   - Phase 3: 75% traffic
   - Phase 4: 100% traffic

#### Step 2: Test Rollback Procedures

```bash
# View rollback procedures
grep "## Rollback Procedures" documentation/Production-Deployment-Guide.md -A 30
```

**Rollback Steps**:
1. Disable observability features via environment variables
2. Restart services
3. Verify system returns to normal
4. Investigate issues
5. Plan fixes

#### Step 3: Test Configuration Switching

```bash
# Test switching between configurations
cp .env.production .env
echo "✓ Production config active"

# Simulate rollback
cp .env.baseline .env
echo "✓ Rolled back to baseline (no observability)"

# Restore production config
cp .env.production .env
echo "✓ Restored production config"
```

**References**:
- Deployment Guide: `documentation/Production-Deployment-Guide.md` (see Phase 1-4 sections)

---

### Test 6.3: Operations Runbook

**What This Tests**: Validates operational procedures are documented

**Context**: The runbook provides day-to-day operational guidance.

#### Step 1: Review Daily Operations

```bash
# View daily operations checklist
grep "## Daily Operations" documentation/Operations-Runbook.md -A 30
```

**Daily Tasks**:
- [ ] Check Grafana dashboards
- [ ] Review alert status
- [ ] Check MongoDB disk space
- [ ] Review recent pipeline runs
- [ ] Check for errors in Loki logs

#### Step 2: Test Health Check Script

```bash
# Create daily health check script
cat > scripts/operations/daily-health-check.sh << 'EOF'
#!/bin/bash

echo "GraphRAG Observability Health Check"
echo "==================================="
echo ""

# Check MongoDB
echo "Checking MongoDB..."
mongosh mongodb://localhost:27017/ --eval "db.version()" --quiet && echo "✓ MongoDB: Healthy" || echo "✗ MongoDB: Down"

# Check Prometheus
echo "Checking Prometheus..."
curl -s http://localhost:9090/-/healthy > /dev/null && echo "✓ Prometheus: Healthy" || echo "✗ Prometheus: Down"

# Check Grafana
echo "Checking Grafana..."
curl -s http://localhost:3000/api/health > /dev/null && echo "✓ Grafana: Healthy" || echo "✗ Grafana: Down"

# Check Loki
echo "Checking Loki..."
curl -s http://localhost:3100/ready > /dev/null && echo "✓ Loki: Healthy" || echo "✗ Loki: Down"

# Check storage
echo ""
echo "Storage Check:"
mongosh mongodb://localhost:27017/graphrag --quiet --eval "
  const collections = ['transformation_logs', 'quality_metrics'];
  let total = 0;
  collections.forEach(coll => {
    const size = db[coll].stats().size;
    total += size;
  });
  const totalMB = (total / 1024 / 1024).toFixed(2);
  print('Observability data: ' + totalMB + ' MB');
  if (total < 500 * 1024 * 1024) {
    print('✓ Storage: Within limits');
  } else {
    print('⚠ Storage: Approaching limits');
  }
"

echo ""
echo "Health check complete!"
EOF

chmod +x scripts/operations/daily-health-check.sh
./scripts/operations/daily-health-check.sh
```

**Expected Output**:
```
GraphRAG Observability Health Check
===================================

Checking MongoDB...
✓ MongoDB: Healthy
Checking Prometheus...
✓ Prometheus: Healthy
Checking Grafana...
✓ Grafana: Healthy
Checking Loki...
✓ Loki: Healthy

Storage Check:
Observability data: 489.9 MB
✓ Storage: Within limits

Health check complete!
```

#### Step 3: Review Troubleshooting Guide

```bash
# View common issues
grep "## Troubleshooting Guide" documentation/Operations-Runbook.md -A 50
```

**Common Issues Covered**:
- High database write latency
- Missing transformation logs
- Grafana dashboard not loading
- MongoDB storage full
- Pipeline performance degradation

**References**:
- Operations Runbook: `documentation/Operations-Runbook.md` (1,078 lines)

---

## Troubleshooting

### Common Issues

#### Issue 1: MongoDB Connection Failures

**Symptoms**:
```
Error: Could not connect to MongoDB
pymongo.errors.ServerSelectionTimeoutError
```

**Solution**:
```bash
# Check if MongoDB is running
ps aux | grep mongod

# Start MongoDB
mongod --dbpath /path/to/data/db

# Verify connection string in .env
grep MONGODB_URI .env
```

---

#### Issue 2: No Transformation Logs

**Symptoms**:
- Pipeline runs but no logs in `transformation_logs` collection
- Query scripts return no results

**Solution**:
```bash
# Check if logging is enabled
grep TRANSFORMATION_LOGGING_ENABLED .env
# Should be: TRANSFORMATION_LOGGING_ENABLED=true

# Verify logger is initialized
python -c "
from business.services.graphrag.transformation_logger import TransformationLogger
logger = TransformationLogger()
print('Logger enabled:', logger.enabled)
"
```

---

#### Issue 3: Grafana Shows "No Data"

**Symptoms**:
- Dashboards load but show "No data"
- Metrics not appearing

**Solution**:
```bash
# 1. Check Prometheus data source in Grafana
curl http://localhost:9090/api/v1/targets

# 2. Verify metrics endpoint
curl http://localhost:8000/metrics | grep graphrag

# 3. Check if metrics exporter is running
ps aux | grep metrics_exporter

# 4. Verify time range in Grafana (should include recent data)
```

---

#### Issue 4: High Storage Usage

**Symptoms**:
- MongoDB disk space filling up
- Collections growing too large

**Solution**:
```bash
# Check TTL indexes
mongosh mongodb://localhost:27017/graphrag --eval "
  db.transformation_logs.getIndexes().forEach(idx => {
    if (idx.expireAfterSeconds) {
      print('TTL: ' + idx.expireAfterSeconds / 86400 + ' days');
    }
  });
"

# If no TTL, create one:
mongosh mongodb://localhost:27017/graphrag --eval "
  db.transformation_logs.createIndex(
    { timestamp: 1 },
    { expireAfterSeconds: 2592000 }  // 30 days
  );
"

# Manually clean old data
mongosh mongodb://localhost:27017/graphrag --eval "
  const cutoff = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
  db.transformation_logs.deleteMany({ timestamp: { \$lt: cutoff } });
"
```

---

#### Issue 5: Performance Degradation

**Symptoms**:
- Pipeline runs slower than expected
- Observability overhead > 5%

**Solution**:
```bash
# 1. Check if batching is enabled (Achievement 7.2)
grep -r "insert_many" business/services/graphrag/

# 2. Disable intermediate data if not needed
echo "INTERMEDIATE_DATA_ENABLED=false" >> .env

# 3. Reduce batch size if memory constrained
# Edit transformation_logger.py:
# batch_size=10  (reduce from default 50)

# 4. Monitor MongoDB performance
mongosh mongodb://localhost:27017/graphrag --eval "
  db.setProfilingLevel(2);
  // Run pipeline
  // Then check:
  db.system.profile.find().sort({ millis: -1 }).limit(10);
"
```

---

### Getting Help

**Documentation**:
- Main Plan: `PLAN_GRAPHRAG-OBSERVABILITY-VALIDATION.md`
- Execution Index: `execution/INDEX.md`
- Documentation Index: `execution/INDEX-DOCUMENTATION.md`
- Best Practices: `documentation/Validation-Best-Practices.md`

**Validation Scripts**:
- All validation scripts: `observability/validate-*.sh`
- Run all: `cd observability && for s in validate-*.sh; do ./$s; done`

**Query Scripts**:
- Query examples: `documentation/Query-Scripts-Example-Outputs.md`
- README: `scripts/repositories/graphrag/queries/README.md`

---

## Quick Reference

### Essential Commands

```bash
# Run pipeline with observability
python -m business.services.graphrag.pipeline \
  --input data/input/test.txt \
  --output data/output/ \
  --trace-id "test-$(date +%s)"

# Query transformation logs
mongosh mongodb://localhost:27017/graphrag --eval "
  db.transformation_logs.find().limit(5).pretty()
"

# Check quality metrics
python scripts/repositories/graphrag/queries/query_quality_metrics.py \
  --trace-id YOUR_TRACE_ID

# Compare before/after resolution
python scripts/repositories/graphrag/queries/compare_before_after_resolution.py \
  --trace-id YOUR_TRACE_ID

# Health check
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3000/api/health # Grafana
curl http://localhost:3100/ready      # Loki

# Storage check
mongosh mongodb://localhost:27017/graphrag --eval "
  db.transformation_logs.stats().size / 1024 / 1024
"
```

### Environment Variables

**Essential Settings**:
```bash
# Core
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=graphrag

# Observability Features
TRANSFORMATION_LOGGING_ENABLED=true
INTERMEDIATE_DATA_ENABLED=true
QUALITY_METRICS_ENABLED=true
PROMETHEUS_METRICS_ENABLED=true

# Performance
BATCH_SIZE=50  # For batching optimizations
```

### Key Files

**Configuration**:
- `.env` - Environment variables
- `observability/docker-compose.yml` - Observability stack

**Code**:
- `business/services/graphrag/transformation_logger.py` - Logging
- `business/services/graphrag/intermediate_data.py` - Data snapshots
- `business/services/graphrag/quality_metrics.py` - Metrics calculation

**Scripts**:
- `scripts/repositories/graphrag/queries/` - Query scripts
- `scripts/repositories/graphrag/explain/` - Explanation tools
- `observability/validate-*.sh` - Validation scripts

**Documentation**:
- `documentation/Production-Readiness-Checklist.md` - 187 pre-deployment checks
- `documentation/Production-Deployment-Guide.md` - Deployment procedures
- `documentation/Operations-Runbook.md` - Day-to-day operations

---

## Summary

This manual test guide covers **comprehensive testing** of the GraphRAG observability infrastructure across:

- ✅ **Infrastructure**: Transformation logging, intermediate data, metrics, dashboards
- ✅ **Validation**: Scripts, integration testing, end-to-end validation
- ✅ **Query Tools**: Analysis scripts, explanation tools, quality metrics
- ✅ **Performance**: Impact measurement, storage analysis, cost-benefit assessment
- ✅ **Enhancements**: Color formatting, pagination, caching, progress indicators, batch optimizations
- ✅ **Production**: Readiness checklist, deployment procedures, operations runbook

**Total Test Coverage**: 25 achievements, 34 execution tasks, 81+ documentation files

**Estimated Testing Time**: 4-6 hours for complete manual testing

**Next Steps**:
1. Complete all test phases
2. Document results in `test-results/`
3. Review production readiness checklist
4. Plan staging deployment
5. Execute phased production rollout

**References**:
- Master Plan: `PLAN_GRAPHRAG-OBSERVABILITY-VALIDATION.md`
- Execution Index: `execution/INDEX.md`
- Documentation Index: `execution/INDEX-DOCUMENTATION.md`
- Best Practices: `documentation/Validation-Best-Practices.md`

---

**Guide Version**: 1.0  
**Last Updated**: 2025-11-15  
**Status**: Complete & Ready for Use

For questions or issues, refer to the troubleshooting section or consult the comprehensive documentation index.

