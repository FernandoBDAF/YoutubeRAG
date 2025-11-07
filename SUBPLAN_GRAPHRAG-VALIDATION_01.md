# SUBPLAN: Test Environment Preparation

**Mother Plan**: PLAN_GRAPHRAG-VALIDATION.md  
**Achievement Addressed**: Achievement 0.1 - Test Environment Prepared  
**Status**: In Progress  
**Created**: November 7, 2025  
**Estimated Effort**: 1-2 hours

---

## 🎯 Objective

Prepare and verify the testing environment for GraphRAG pipeline validation. This includes verifying database connectivity, identifying suitable test datasets, checking observability stack configuration, and capturing baseline metrics before running any pipeline stages.

**Contribution to Mother Plan**: Establishes foundation for all validation testing, ensuring we have working environment and baseline for comparison.

---

## 📝 What Needs to Be Created

### Files to Create

1. `EXECUTION_TASK_GRAPHRAG-VALIDATION_01_01.md` - Execution tracking
2. `VALIDATION_ENVIRONMENT-SETUP.md` - Environment verification results
3. Baseline metrics snapshot (embedded in validation doc or separate)

### Modifications

- None (validation only)

---

## 🛠️ Approach

### Step 1: Verify Database Connection (15 minutes)

**Actions**:
1. Check MongoDB connection string in environment
2. Test connection with simple query
3. List available databases
4. Verify GraphRAG collections exist
5. Check collection counts

**Validation**:
```python
from dependencies.database.mongodb import get_mongo_client
from core.config.paths import DB_NAME

client = get_mongo_client()
db = client[DB_NAME]

# Verify collections
collections = db.list_collection_names()
graphrag_collections = ['video_chunks', 'entities', 'relations', 'communities', 'graphrag_runs', 'entity_mentions']

for coll in graphrag_collections:
    if coll in collections:
        count = db[coll].count_documents({})
        print(f'✓ {coll}: {count} documents')
    else:
        print(f'✗ {coll}: NOT FOUND')
```

### Step 2: Identify Test Dataset (30 minutes)

**Actions**:
1. Query video_chunks collection
2. Find chunks suitable for testing:
   - Need 10-20 chunks minimum for quick test
   - Prefer chunks with existing extraction data
   - Identify video_ids for targeted testing
3. Document test dataset specification

**Criteria for Test Data**:
- Small: 10-20 chunks for quick validation
- Medium: 100-200 chunks for comprehensive testing
- Diverse: Multiple videos, different content types
- Clean: Valid text, no corrupted data

**Query**:
```python
# Find suitable test data
chunks_with_extraction = db.video_chunks.count_documents({
    'graphrag_extraction.status': 'completed'
})

# Get sample video IDs
sample_vids = db.video_chunks.aggregate([
    {'$match': {'graphrag_extraction.status': 'completed'}},
    {'$group': {'_id': '$video_id', 'count': {'$sum': 1}}},
    {'$sort': {'count': -1}},
    {'$limit': 3}
])

for vid in sample_vids:
    print(f"Video: {vid['_id']}, Chunks: {vid['count']}")
```

### Step 3: Verify Observability Stack Configuration (20 minutes)

**Actions**:
1. Check `docker-compose.observability.yml` exists
2. Verify Prometheus configuration
3. Verify Grafana configuration
4. Check metrics endpoint (`/metrics`) works
5. Document configuration status

**Verification**:
```bash
# Check observability files
ls -la docker-compose.observability.yml
ls -la observability/prometheus/
ls -la observability/grafana/

# Test metrics endpoint (if running)
curl -s http://localhost:8000/metrics | head -20
```

### Step 4: Capture Baseline Metrics (20 minutes)

**Actions**:
1. Query current state of GraphRAG collections
2. Capture document counts
3. Note any existing graphrag_runs
4. Document baseline for comparison

**Metrics to Capture**:
```python
baseline = {
    'video_chunks': {
        'total': db.video_chunks.count_documents({}),
        'with_extraction': db.video_chunks.count_documents({'graphrag_extraction.status': 'completed'}),
        'with_resolution': db.video_chunks.count_documents({'graphrag_resolution.status': 'completed'}),
    },
    'entities': db.entities.count_documents({}),
    'entity_mentions': db.entity_mentions.count_documents({}),
    'relations': db.relations.count_documents({}),
    'communities': db.communities.count_documents({}),
    'graphrag_runs': db.graphrag_runs.count_documents({}),
}

import json
print(json.dumps(baseline, indent=2))
```

---

## 🧪 Tests Required

**Not Applicable** - This is validation/setup work, not code implementation.

**Validation Criteria**:
- Database connection works
- Test dataset identified and documented
- Observability stack configuration verified
- Baseline metrics captured

---

## 📊 Expected Results

### Functional Changes

- No code changes (validation only)
- Environment verified as ready
- Test data identified

### Observable Outcomes

- Database connection confirmed
- Collection counts documented
- Test dataset specification created
- Baseline metrics snapshot captured
- Environment status: READY / ISSUES FOUND

### Success Indicators

- ✅ Can connect to MongoDB
- ✅ GraphRAG collections exist
- ✅ Suitable test data available (at least 20 chunks)
- ✅ Observability stack files present
- ✅ Baseline documented

---

## 🔗 Dependencies

**Prerequisites**:
- MongoDB instance running and accessible
- Environment variables configured (.env file)
- Video chunks with extraction data exist

**No Dependencies on Other Subplans**: This is the first validation step

---

## 📋 Execution Task Reference

- EXECUTION_TASK_GRAPHRAG-VALIDATION_01_01.md (to be created)

---

**Status**: Ready to execute

