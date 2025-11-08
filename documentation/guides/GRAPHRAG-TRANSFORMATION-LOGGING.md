# GraphRAG Transformation Logging Guide

**Version**: 1.0  
**Last Updated**: 2025-01-28  
**Achievement**: 0.1 - Transformation Logging Infrastructure

---

## 📋 Overview

The GraphRAG Transformation Logging system provides structured, queryable logs for every transformation in the pipeline. This enables "why" questions about entity merges, relationship filtering, and community formation.

**Key Features**:
- ✅ Structured logs for all 8 operation types
- ✅ Trace ID linking across pipeline stages
- ✅ MongoDB storage for fast querying
- ✅ Indexed for performance
- ✅ Confidence scores and reasoning

**Use Cases**:
- Debug why entities were merged or skipped
- Understand relationship filtering decisions
- Analyze community formation patterns
- Track transformations across pipeline runs
- Audit pipeline behavior for quality assurance

---

## 🏗️ Architecture

### Components

1. **TransformationLogger Service** (`business/services/graphrag/transformation_logger.py`)
   - Core logging service with 8 operation-specific methods
   - MongoDB integration with automatic indexing
   - Can be disabled for performance (via env var)

2. **Stage Integrations**:
   - `EntityResolutionStage`: Logs MERGE, CREATE, SKIP operations
   - `GraphConstructionStage`: Logs RELATIONSHIP_CREATE, FILTER, AUGMENT operations
   - `CommunityDetectionStage`: Logs COMMUNITY_FORM, ENTITY_CLUSTER operations

3. **Trace ID System** (`business/pipelines/graphrag.py`)
   - Unique UUID generated per pipeline run
   - Propagated to all stage configs
   - Links all transformations in a single run

4. **MongoDB Collection**: `transformation_logs`
   - Indexed on: trace_id, entity_id, stage, operation, timestamp
   - Compound indexes for common queries

---

## 📊 Log Format Specification

### Base Log Entry Structure

All log entries share this base structure:

```javascript
{
  "trace_id": "uuid-v4-string",           // Links transformations across stages
  "stage": "stage_name",                  // entity_resolution, graph_construction, community_detection
  "operation": "OPERATION_TYPE",          // See operation types below
  "timestamp": 1706456789.123,            // Unix timestamp (float)
  "datetime": "2025-01-28T16:06:29.123Z", // ISO 8601 datetime (UTC)
  // ... operation-specific fields
}
```

### Operation Types

#### 1. ENTITY_MERGE

**When**: Two entities are merged during entity resolution

```javascript
{
  "trace_id": "a1b2c3d4-...",
  "stage": "entity_resolution",
  "operation": "ENTITY_MERGE",
  "timestamp": 1706456789.123,
  "datetime": "2025-01-28T16:06:29.123Z",
  "entity_a": {
    "id": "entity_123",
    "name": "Barack Obama"
  },
  "entity_b": {
    "id": "entity_456",
    "name": "President Obama"
  },
  "result_entity": {
    "id": "entity_456",
    "name": "President Obama"
  },
  "reason": "fuzzy_match_above_threshold",
  "similarity": 0.92,
  "confidence": 0.95
}
```

#### 2. ENTITY_CREATE

**When**: A new entity is created (canonicalized) during entity resolution

```javascript
{
  "trace_id": "a1b2c3d4-...",
  "stage": "entity_resolution",
  "operation": "ENTITY_CREATE",
  "timestamp": 1706456789.123,
  "datetime": "2025-01-28T16:06:29.123Z",
  "entity": {
    "id": "entity_789",
    "name": "Michelle Obama"
  },
  "entity_type": "PERSON",
  "sources": 1,
  "confidence": 0.88
}
```

#### 3. ENTITY_SKIP

**When**: An entity is skipped during entity resolution

```javascript
{
  "trace_id": "a1b2c3d4-...",
  "stage": "entity_resolution",
  "operation": "ENTITY_SKIP",
  "timestamp": 1706456789.123,
  "datetime": "2025-01-28T16:06:29.123Z",
  "entity": {
    "id": "chunk_123",
    "name": "chunk_123"
  },
  "reason": "no_extraction_data",
  "confidence": 0.0
}
```

#### 4. RELATIONSHIP_CREATE

**When**: A new relationship is created during graph construction

```javascript
{
  "trace_id": "a1b2c3d4-...",
  "stage": "graph_construction",
  "operation": "RELATIONSHIP_CREATE",
  "timestamp": 1706456789.123,
  "datetime": "2025-01-28T16:06:29.123Z",
  "relationship": {
    "source": "entity_123",
    "target": "entity_456",
    "type": "MARRIED_TO"
  },
  "confidence": 0.91,
  "weight": 1.0
}
```

#### 5. RELATIONSHIP_FILTER

**When**: A relationship is filtered out during graph construction

```javascript
{
  "trace_id": "a1b2c3d4-...",
  "stage": "graph_construction",
  "operation": "RELATIONSHIP_FILTER",
  "timestamp": 1706456789.123,
  "datetime": "2025-01-28T16:06:29.123Z",
  "relationship": {
    "source": "chunk_123",
    "target": "chunk_123"
  },
  "reason": "no_extraction_data",
  "confidence": 0.0
}
```

#### 6. RELATIONSHIP_AUGMENT

**When**: A relationship is augmented with additional information

```javascript
{
  "trace_id": "a1b2c3d4-...",
  "stage": "graph_construction",
  "operation": "RELATIONSHIP_AUGMENT",
  "timestamp": 1706456789.123,
  "datetime": "2025-01-28T16:06:29.123Z",
  "relationship": {
    "source": "entity_123",
    "target": "entity_456",
    "type": "WORKS_WITH"
  },
  "augmentation": {
    "weight": 2.5,
    "co_occurrences": 5
  },
  "confidence": 0.89
}
```

#### 7. COMMUNITY_FORM

**When**: A community is formed during community detection

```javascript
{
  "trace_id": "a1b2c3d4-...",
  "stage": "community_detection",
  "operation": "COMMUNITY_FORM",
  "timestamp": 1706456789.123,
  "datetime": "2025-01-28T16:06:29.123Z",
  "community_id": "community_0_1",
  "entities": [
    {"id": "entity_123", "name": "Barack Obama"},
    {"id": "entity_456", "name": "Michelle Obama"},
    {"id": "entity_789", "name": "Joe Biden"}
  ],
  "modularity": 0.82,
  "coherence": 0.82,
  "algorithm": "leiden",
  "resolution_parameter": 1.0
}
```

#### 8. ENTITY_CLUSTER

**When**: An entity is assigned to a community

```javascript
{
  "trace_id": "a1b2c3d4-...",
  "stage": "community_detection",
  "operation": "ENTITY_CLUSTER",
  "timestamp": 1706456789.123,
  "datetime": "2025-01-28T16:06:29.123Z",
  "entity": {
    "id": "entity_123",
    "name": "Barack Obama"
  },
  "community_id": "community_0_1",
  "reason": "algorithm_assignment",
  "neighbors": 12
}
```

---

## 🔍 Query Examples

### Example 1: Find All Transformations for a Pipeline Run

```javascript
db.transformation_logs.find({
  trace_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}).sort({ timestamp: 1 })
```

**Use Case**: Debug a specific pipeline run end-to-end

---

### Example 2: Find All Entity Merges with High Similarity

```javascript
db.transformation_logs.find({
  operation: "ENTITY_MERGE",
  similarity: { $gte: 0.9 }
}).sort({ similarity: -1 })
```

**Use Case**: Audit high-confidence entity merges

---

### Example 3: Find Why a Specific Entity Was Skipped

```javascript
db.transformation_logs.find({
  operation: "ENTITY_SKIP",
  "entity.id": "chunk_123"
})
```

**Use Case**: Debug why an entity wasn't processed

---

### Example 4: Find All Relationships Filtered in a Run

```javascript
db.transformation_logs.find({
  trace_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  operation: "RELATIONSHIP_FILTER"
})
```

**Use Case**: Understand why relationships were excluded

---

### Example 5: Find All Communities Formed in a Run

```javascript
db.transformation_logs.find({
  trace_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  operation: "COMMUNITY_FORM"
})
```

**Use Case**: Analyze community detection results

---

### Example 6: Find Entity Transformation History

```javascript
db.transformation_logs.find({
  $or: [
    { "entity.id": "entity_123" },
    { "entity_a.id": "entity_123" },
    { "entity_b.id": "entity_123" },
    { "result_entity.id": "entity_123" }
  ]
}).sort({ timestamp: 1 })
```

**Use Case**: Track all transformations involving a specific entity

---

### Example 7: Count Operations by Stage

```javascript
db.transformation_logs.aggregate([
  {
    $match: {
      trace_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    }
  },
  {
    $group: {
      _id: { stage: "$stage", operation: "$operation" },
      count: { $sum: 1 }
    }
  },
  {
    $sort: { "_id.stage": 1, "_id.operation": 1 }
  }
])
```

**Use Case**: Pipeline transformation statistics

---

### Example 8: Find Low-Confidence Transformations

```javascript
db.transformation_logs.find({
  trace_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  confidence: { $lt: 0.7, $gt: 0 }
}).sort({ confidence: 1 })
```

**Use Case**: Identify uncertain transformations for review

---

## 💻 Usage Guide

### Enable/Disable Logging

Logging is controlled via environment variable:

```bash
# Enable logging (default)
export GRAPHRAG_TRANSFORMATION_LOGGING=true

# Disable logging (for performance)
export GRAPHRAG_TRANSFORMATION_LOGGING=false
```

### Accessing Logs in Code

```python
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client.youtuberag

# Query logs
logs = db.transformation_logs.find({
    "trace_id": "your-trace-id-here"
}).sort("timestamp", 1)

for log in logs:
    print(f"{log['stage']}: {log['operation']} - {log.get('reason', 'N/A')}")
```

### Finding Trace IDs

Trace IDs are logged at pipeline start:

```bash
# Check pipeline logs
grep "Trace ID generated" logs/pipeline/*.log

# Example output:
# 2025-01-28 16:06:29 - INFO - 🔍 Trace ID generated: a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

Or query from run metadata:

```javascript
db.graphrag_runs.find({}, { trace_id: 1, created_at: 1 }).sort({ created_at: -1 }).limit(10)
```

---

## 🎯 Best Practices

### 1. Use Trace IDs for Debugging

Always start with a trace ID to isolate a specific pipeline run:

```javascript
// Good: Scoped to specific run
db.transformation_logs.find({ trace_id: "..." })

// Bad: Unscoped query (slow, mixed runs)
db.transformation_logs.find({ operation: "ENTITY_MERGE" })
```

### 2. Index Your Queries

The collection is indexed on common fields. Use them:

```javascript
// Good: Uses index
db.transformation_logs.find({ trace_id: "...", stage: "entity_resolution" })

// Bad: Full collection scan
db.transformation_logs.find({ "entity.name": "Barack Obama" })
```

### 3. Aggregate for Statistics

Use aggregation pipelines for counts and summaries:

```javascript
// Count operations per stage
db.transformation_logs.aggregate([
  { $match: { trace_id: "..." } },
  { $group: { _id: "$stage", count: { $sum: 1 } } }
])
```

### 4. Filter by Confidence

Focus on high/low confidence transformations:

```javascript
// High confidence merges
db.transformation_logs.find({
  operation: "ENTITY_MERGE",
  confidence: { $gte: 0.9 }
})

// Low confidence (needs review)
db.transformation_logs.find({
  confidence: { $lt: 0.7, $gt: 0 }
})
```

### 5. Disable in Production (Optional)

For maximum performance, disable logging in production:

```bash
export GRAPHRAG_TRANSFORMATION_LOGGING=false
```

**Note**: Logs are lightweight (~200 bytes each), so performance impact is minimal.

---

## 🔧 Troubleshooting

### No Logs Found

**Check 1**: Is logging enabled?

```bash
echo $GRAPHRAG_TRANSFORMATION_LOGGING
# Should be "true" or empty (defaults to true)
```

**Check 2**: Is the collection created?

```javascript
db.getCollectionNames().includes("transformation_logs")
```

**Check 3**: Check pipeline logs for errors:

```bash
grep "TransformationLogger" logs/pipeline/*.log
```

### Slow Queries

**Check 1**: Are you using indexed fields?

```javascript
// Show indexes
db.transformation_logs.getIndexes()
```

**Check 2**: Add trace_id to your query:

```javascript
// Good: Uses trace_id index
db.transformation_logs.find({ trace_id: "...", operation: "ENTITY_MERGE" })

// Bad: No index
db.transformation_logs.find({ "entity.name": "..." })
```

### Missing Trace IDs

**Check 1**: Verify trace ID generation:

```bash
grep "Trace ID generated" logs/pipeline/*.log
```

**Check 2**: Verify trace ID propagation:

```python
# In your pipeline code
print(f"Config trace_id: {self.config.trace_id}")
```

---

## 📚 Related Documentation

- **TransformationLogger API**: `business/services/graphrag/transformation_logger.py`
- **Stage Integrations**:
  - Entity Resolution: `business/stages/graphrag/entity_resolution.py`
  - Graph Construction: `business/stages/graphrag/graph_construction.py`
  - Community Detection: `business/stages/graphrag/community_detection.py`
- **Trace ID System**: `business/pipelines/graphrag.py`
- **Tests**: `tests/business/pipelines/test_graphrag_trace_id.py`

---

## 📝 Examples in Action

### Example: Debug Entity Merge Decision

**Scenario**: Why were "Barack Obama" and "President Obama" merged?

```javascript
// 1. Find the merge log
db.transformation_logs.findOne({
  operation: "ENTITY_MERGE",
  "entity_a.name": "Barack Obama",
  "entity_b.name": "President Obama"
})

// Result:
{
  "trace_id": "a1b2c3d4-...",
  "operation": "ENTITY_MERGE",
  "entity_a": { "id": "entity_123", "name": "Barack Obama" },
  "entity_b": { "id": "entity_456", "name": "President Obama" },
  "result_entity": { "id": "entity_456", "name": "President Obama" },
  "reason": "fuzzy_match_above_threshold",
  "similarity": 0.92,  // ← High similarity
  "confidence": 0.95   // ← High confidence
}

// Answer: Merged due to 92% similarity (above threshold)
```

### Example: Analyze Community Formation

**Scenario**: What communities were formed and why?

```javascript
// 1. Find all communities in a run
db.transformation_logs.find({
  trace_id: "a1b2c3d4-...",
  operation: "COMMUNITY_FORM"
})

// 2. Analyze a specific community
db.transformation_logs.findOne({
  operation: "COMMUNITY_FORM",
  community_id: "community_0_1"
})

// Result:
{
  "community_id": "community_0_1",
  "entities": [
    { "id": "entity_123", "name": "Barack Obama" },
    { "id": "entity_456", "name": "Michelle Obama" },
    { "id": "entity_789", "name": "Joe Biden" }
  ],
  "modularity": 0.82,  // ← High modularity
  "coherence": 0.82,   // ← High coherence
  "algorithm": "leiden",
  "resolution_parameter": 1.0
}

// Answer: Community formed with 3 entities, high coherence (0.82)
```

---

## 🚀 Next Steps

1. **Run a Pipeline**: Generate some logs
2. **Query Logs**: Try the query examples above
3. **Analyze Results**: Use aggregation for insights
4. **Integrate**: Add custom queries to your workflow

For questions or issues, see the related documentation or check the test files for more examples.

---

**Version**: 1.0  
**Last Updated**: 2025-01-28  
**Maintainer**: GraphRAG Team

