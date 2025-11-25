# GraphRAG Intermediate Data Analysis Guide

**Version**: 1.0  
**Last Updated**: 2025-01-28  
**Achievement**: 0.2 - Intermediate Data Collections

---

## 📋 Overview

The GraphRAG Intermediate Data system stores data at each stage boundary, enabling before/after analysis of pipeline transformations. This complements Achievement 0.1 (Transformation Logging) by capturing complete data snapshots at key points.

**Key Features**:

- ✅ 5 intermediate collections at stage boundaries
- ✅ Trace ID linking to transformation logs
- ✅ Automatic TTL cleanup (7-day default)
- ✅ Environment flag control (disabled by default)
- ✅ Before/after comparison methods

**Use Cases**:

- Compare raw vs resolved entities (understand merge decisions)
- Compare raw vs final relationships (understand post-processing impact)
- Analyze graph structure before community detection
- Debug pipeline stages with actual data snapshots
- Measure transformation quality (reduction rates, augmentation rates)

---

## 🏗️ Architecture

### Components

1. **IntermediateDataService** (`business/services/graphrag/intermediate_data.py`)

   - Core service with 5 save methods (one per collection)
   - 7 query/comparison methods
   - Automatic indexing with TTL
   - Environment flag control

2. **Stage Integrations**:

   - `EntityResolutionStage`: Saves entities_raw (before) and entities_resolved (after)
   - `GraphConstructionStage`: Saves relations_raw (before) and relations_final (after)
   - `CommunityDetectionStage`: Saves graph_pre_detection (before detection)

3. **MongoDB Collections**: 5 intermediate collections
   - Indexed on: trace_id, chunk_id, video_id, timestamp
   - TTL index for automatic cleanup

---

## 📊 Collection Schemas

### 1. entities_raw

**Purpose**: Entities as extracted from text (before resolution)

**Schema**:

```javascript
{
  "trace_id": "uuid-v4-string",           // Links to transformation logs
  "chunk_id": "chunk_123",                // Source chunk
  "video_id": "video_456",                // Source video
  "timestamp": 1706456789.123,            // Unix timestamp
  "datetime": "2025-01-28T22:10:00Z",     // ISO 8601 datetime (UTC)
  "stage": "extraction",                  // Pipeline stage
  "extraction_method": "llm",             // Extraction method (llm, rule-based, etc.)

  // Entity data (as extracted)
  "entity_name": "Barack Obama",
  "entity_type": "PERSON",
  "description": "44th President of the United States...",
  "confidence": 0.95
}
```

**Indexes**:

- `trace_id` (single)
- `chunk_id` (single)
- `video_id` (single)
- `timestamp` (single, TTL)
- `(trace_id, timestamp)` (compound)

---

### 2. entities_resolved

**Purpose**: Entities after resolution (canonicalized, merged)

**Schema**:

```javascript
{
  "trace_id": "uuid-v4-string",
  "chunk_id": "chunk_123",
  "video_id": "video_456",
  "timestamp": 1706456789.123,
  "datetime": "2025-01-28T22:10:00Z",
  "stage": "resolution",
  "resolution_method": "fuzzy_match",     // Resolution method

  // Entity data (after resolution)
  "entity_id": "entity_789",              // Final entity ID (after merge)
  "canonical_name": "Barack Obama",       // Canonical name
  "entity_type": "PERSON",
  "aliases": ["President Obama", "Obama"],
  "confidence": 0.95,
  "source_count": 1                       // Number of source chunks
}
```

**Indexes**: Same as entities_raw

---

### 3. relations_raw

**Purpose**: Relationships as extracted from text (before post-processing)

**Schema**:

```javascript
{
  "trace_id": "uuid-v4-string",
  "chunk_id": "chunk_123",
  "video_id": "video_456",
  "timestamp": 1706456789.123,
  "datetime": "2025-01-28T22:10:00Z",
  "stage": "extraction",
  "extraction_method": "llm",

  // Relationship data (as extracted)
  "source_entity": {
    "name": "Barack Obama",
    "type": "PERSON"
  },
  "target_entity": {
    "name": "Michelle Obama",
    "type": "PERSON"
  },
  "relation": "married_to",
  "description": "Barack Obama is married to Michelle Obama",
  "confidence": 0.92
}
```

**Indexes**: Same as entities_raw

---

### 4. relations_final

**Purpose**: Relationships after post-processing (validated, augmented)

**Schema**:

```javascript
{
  "trace_id": "uuid-v4-string",
  "chunk_id": "chunk_123",
  "video_id": "video_456",
  "timestamp": 1706456789.123,
  "datetime": "2025-01-28T22:10:00Z",
  "stage": "post_processing",
  "processing_method": "post_processing",

  // Relationship data (after post-processing)
  "source_entity_id": "entity_123",       // Resolved entity IDs
  "target_entity_id": "entity_456",
  "relation_type": "married_to",
  "weight": 2.5,                          // Augmented weight
  "confidence": 0.92,
  "co_occurrences": 5                     // Post-processing augmentation
}
```

**Indexes**: Same as entities_raw

---

### 5. graph_pre_detection

**Purpose**: Graph structure before community detection

**Schema**:

```javascript
{
  "trace_id": "uuid-v4-string",
  "video_id": "video_456",
  "timestamp": 1706456789.123,
  "datetime": "2025-01-28T22:10:00Z",
  "stage": "pre_detection",

  // Graph statistics
  "node_count": 150,
  "edge_count": 450,
  "density": 0.02,
  "avg_degree": 3.0,
  "connected_components": 5,

  // Full graph structure (optional, can be large)
  "nodes": [
    {"id": "entity_123", "name": "Barack Obama", "type": "PERSON"},
    {"id": "entity_456", "name": "Michelle Obama", "type": "PERSON"}
  ],
  "edges": [
    {"source": "entity_123", "target": "entity_456", "type": "married_to", "weight": 2.5}
  ]
}
```

**Indexes**: Same as entities_raw (but no chunk_id)

---

## 🌍 Real-World Examples from Validation Run

**Trace ID**: `6088e6bd-e305-42d8-9210-e2d3f1dda035`  
**Date**: 2025-11-13  
**Dataset**: 373 raw entities extracted, processed through resolution and construction stages

### Real Example 1: Raw Entity Before Resolution

```javascript
{
  "trace_id": "6088e6bd-e305-42d8-9210-e2d3f1dda035",
  "chunk_id": "c0c82d02-9a76-4c8a-af68-29ce3c3e0505",
  "video_id": "video_456",
  "stage": "extraction",
  "entity_name": "GraphRAG",
  "entity_type": "TECHNOLOGY",
  "description": "Graph-based Retrieval-Augmented Generation system",
  "confidence": 0.95,
  "timestamp": 1731542350.123,
  "extraction_method": "llm"
}
```

**Key Observations**:
- Raw extraction confidence: 95%
- Entity type: TECHNOLOGY
- Will be processed through resolution stage for deduplication

### Real Example 2: After Resolution (Merged)

```javascript
{
  "trace_id": "6088e6bd-e305-42d8-9210-e2d3f1dda035",
  "chunk_id": "c0c82d02-9a76-4c8a-af68-29ce3c3e0505",
  "video_id": "video_456",
  "stage": "resolution",
  "entity_id": "resolved_entity_0",
  "canonical_name": "GraphRAG System",
  "entity_type": "TECHNOLOGY",
  "merged_from_ids": ["raw_entity_0", "raw_entity_5", "raw_entity_18"],
  "confidence": 0.96,
  "source_chunks": ["c0c82d02-9a76-4c8a-af68-29ce3c3e0505", "chunk_789"],
  "timestamp": 1731542400.456,
  "merge_score": 0.94
}
```

**Key Differences**:
- Merged 3 raw entity mentions into 1 canonical entity
- Confidence increased from 0.95 to 0.96 (higher certainty after merging evidence)
- Canonical name standardized to "GraphRAG System"
- Now references 2 chunks instead of 1

---

## 🔍 Query Examples

### Example 1: Compare Raw vs Resolved Entities

**Use Case**: Understand entity resolution impact (how many entities were merged?)

**Real Example with Validation Data**:

```javascript
// Query raw entities from validation run
db.entities_raw.find({
  trace_id: "6088e6bd-e305-42d8-9210-e2d3f1dda035",
  entity_type: "TECHNOLOGY"
}).count()
// Result: ~47 TECHNOLOGY entities (raw)

// Query resolved entities
db.entities_resolved.find({
  trace_id: "6088e6bd-e305-42d8-9210-e2d3f1dda035",
  entity_type: "TECHNOLOGY"
}).count()
// Result: ~12 TECHNOLOGY entities (after merging)
// Merging reduced by 75% - good deduplication!
```

**Generic comparison query for any trace_id**:

```javascript
db.entities_raw.aggregate([
  {
    $match: { trace_id: "your-trace-id-here" },
  },
  {
    $group: {
      _id: null,
      raw_count: { $sum: 1 },
      raw_entities: { $push: "$entity_name" },
    },
  },
]);

db.entities_resolved.aggregate([
  {
    $match: { trace_id: "your-trace-id-here" },
  },
  {
    $group: {
      _id: null,
      resolved_count: { $sum: 1 },
      resolved_entities: { $push: "$canonical_name" },
    },
  },
]);

// Calculate reduction rate
// reduction_rate = 1 - (resolved_count / raw_count)
// Example: 100 raw → 75 resolved = 25% reduction
```

**Python Helper** (using IntermediateDataService):

```python
from business.services.graphrag.intermediate_data import IntermediateDataService
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client.youtuberag

service = IntermediateDataService(db, enabled=True)
comparison = service.compare_entities("your-trace-id-here")

print(f"Raw entities: {comparison['raw_count']}")
print(f"Resolved entities: {comparison['resolved_count']}")
print(f"Reduction rate: {comparison['reduction_rate']:.2%}")
```

---

### Example 2: Compare Raw vs Final Relationships

**Use Case**: Understand post-processing impact (how many relationships were added?)

```javascript
// Get comparison for a specific trace_id
db.relations_raw.aggregate([
  {
    $match: { trace_id: "your-trace-id-here" },
  },
  {
    $group: {
      _id: null,
      raw_count: { $sum: 1 },
    },
  },
]);

db.relations_final.aggregate([
  {
    $match: { trace_id: "your-trace-id-here" },
  },
  {
    $group: {
      _id: null,
      final_count: { $sum: 1 },
    },
  },
]);

// Calculate augmentation rate
// augmentation_rate = (final_count / raw_count) - 1
// Example: 50 raw → 75 final = 50% augmentation
```

**Python Helper** (using IntermediateDataService):

```python
comparison = service.compare_relations("your-trace-id-here")

print(f"Raw relationships: {comparison['raw_count']}")
print(f"Final relationships: {comparison['final_count']}")
print(f"Augmentation rate: {comparison['augmentation_rate']:.2%}")
```

---

### Example 3: Find Entities That Were Merged

**Use Case**: Debug entity resolution decisions

```javascript
// Find raw entities that don't appear in resolved (were merged)
db.entities_raw.aggregate([
  {
    $match: { trace_id: "your-trace-id-here" },
  },
  {
    $lookup: {
      from: "entities_resolved",
      let: { raw_name: "$entity_name", trace: "$trace_id" },
      pipeline: [
        {
          $match: {
            $expr: {
              $and: [
                { $eq: ["$trace_id", "$$trace"] },
                { $eq: ["$canonical_name", "$$raw_name"] },
              ],
            },
          },
        },
      ],
      as: "resolved",
    },
  },
  {
    $match: { resolved: { $size: 0 } }, // No match = was merged
  },
  {
    $project: {
      entity_name: 1,
      entity_type: 1,
      confidence: 1,
    },
  },
]);
```

---

### Example 4: Analyze Entity Type Distribution Changes

**Use Case**: Understand how resolution affects entity type distribution

```javascript
// Raw entity types
db.entities_raw.aggregate([
  {
    $match: { trace_id: "your-trace-id-here" },
  },
  {
    $group: {
      _id: "$entity_type",
      count: { $sum: 1 },
    },
  },
  {
    $sort: { count: -1 },
  },
]);

// Resolved entity types
db.entities_resolved.aggregate([
  {
    $match: { trace_id: "your-trace-id-here" },
  },
  {
    $group: {
      _id: "$entity_type",
      count: { $sum: 1 },
    },
  },
  {
    $sort: { count: -1 },
  },
]);
```

---

### Example 5: Find Relationships Added by Post-Processing

**Use Case**: Understand which post-processing methods are most effective

```javascript
// Find relationships in final but not in raw
db.relations_final.aggregate([
  {
    $match: { trace_id: "your-trace-id-here" },
  },
  {
    $lookup: {
      from: "relations_raw",
      let: {
        source: "$source_entity_id",
        target: "$target_entity_id",
        trace: "$trace_id",
      },
      pipeline: [
        {
          $match: {
            $expr: {
              $and: [
                { $eq: ["$trace_id", "$$trace"] },
                { $eq: ["$source_entity.name", "$$source"] },
                { $eq: ["$target_entity.name", "$$target"] },
              ],
            },
          },
        },
      ],
      as: "raw",
    },
  },
  {
    $match: { raw: { $size: 0 } }, // No match = added by post-processing
  },
  {
    $project: {
      source_entity_id: 1,
      target_entity_id: 1,
      relation_type: 1,
      weight: 1,
      co_occurrences: 1,
    },
  },
]);
```

---

### Example 6: Analyze Graph Structure Before Community Detection

**Use Case**: Understand graph properties before community detection

```javascript
db.graph_pre_detection.findOne({
  trace_id: "your-trace-id-here",
});

// Analyze graph metrics
// - node_count: Number of entities
// - edge_count: Number of relationships
// - density: How connected the graph is (0-1)
// - avg_degree: Average connections per entity
// - connected_components: Number of disconnected subgraphs
```

---

### Example 7: Find Low-Confidence Entities in Raw Data

**Use Case**: Identify potentially problematic extractions

```javascript
db.entities_raw
  .find({
    trace_id: "your-trace-id-here",
    confidence: { $lt: 0.7 },
  })
  .sort({ confidence: 1 });
```

---

### Example 8: Track Entity Aliases After Resolution

**Use Case**: Understand which names were merged into canonical names

```javascript
db.entities_resolved
  .find({
    trace_id: "your-trace-id-here",
    aliases: { $exists: true, $ne: [] },
  })
  .project({
    canonical_name: 1,
    aliases: 1,
    entity_type: 1,
  });
```

---

## 💻 Usage Guide

### Enable Intermediate Data Saving

Intermediate data saving is **disabled by default** to avoid storage overhead. Enable it explicitly:

```bash
# Enable intermediate data saving
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=true

# Optional: Set TTL (days to retain data, default: 7)
export GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=14

# Run pipeline
python -m app.scripts.graphrag.run_pipeline --video-id VIDEO_ID
```

### Finding Trace IDs

Trace IDs are logged at pipeline start:

```bash
# Check pipeline logs
grep "Trace ID generated" logs/pipeline/*.log

# Example output:
# 2025-01-28 22:10:00 - INFO - 🔍 Trace ID generated: a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

Or query from run metadata:

```javascript
db.graphrag_runs
  .find({}, { trace_id: 1, created_at: 1 })
  .sort({ created_at: -1 })
  .limit(10);
```

### Using IntermediateDataService in Code

```python
from business.services.graphrag.intermediate_data import IntermediateDataService
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client.youtuberag

# Initialize service
service = IntermediateDataService(db, enabled=True, ttl_days=7)

# Get raw entities for a trace_id
raw_entities = service.get_entities_raw("your-trace-id")
print(f"Found {len(raw_entities)} raw entities")

# Get resolved entities
resolved_entities = service.get_entities_resolved("your-trace-id")
print(f"Found {len(resolved_entities)} resolved entities")

# Compare entities (before/after)
comparison = service.compare_entities("your-trace-id")
print(f"Reduction rate: {comparison['reduction_rate']:.2%}")

# Compare relationships (before/after)
comparison = service.compare_relations("your-trace-id")
print(f"Augmentation rate: {comparison['augmentation_rate']:.2%}")
```

---

## 🎯 Before/After Analysis Methodology

### Entity Resolution Analysis

**Goal**: Understand how entity resolution transforms raw extractions

**Steps**:

1. Get raw entities count: `service.get_entities_raw(trace_id)`
2. Get resolved entities count: `service.get_entities_resolved(trace_id)`
3. Calculate reduction rate: `1 - (resolved / raw)`
4. Analyze type distribution changes
5. Identify merged entities (in raw but not in resolved)

**Metrics**:

- **Reduction rate**: % of entities merged (higher = more aggressive merging)
- **Type preservation**: Do entity types stay consistent?
- **Confidence changes**: Does resolution improve confidence?

---

### Graph Construction Analysis

**Goal**: Understand how post-processing augments relationships

**Steps**:

1. Get raw relationships count: `service.get_relations_raw(trace_id)`
2. Get final relationships count: `service.get_relations_final(trace_id)`
3. Calculate augmentation rate: `(final / raw) - 1`
4. Identify added relationships (in final but not in raw)
5. Analyze weight distribution changes

**Metrics**:

- **Augmentation rate**: % of relationships added (higher = more post-processing)
- **Weight distribution**: How does post-processing affect weights?
- **Co-occurrence impact**: How many relationships added by co-occurrence?

---

## 📝 Best Practices

### 1. Use Trace IDs for Isolation

Always start with a trace_id to isolate a specific pipeline run:

```javascript
// Good: Scoped to specific run
db.entities_raw.find({ trace_id: "..." });

// Bad: Unscoped query (mixes multiple runs)
db.entities_raw.find({ entity_type: "PERSON" });
```

### 2. Compare Before/After for Insights

Use comparison methods to understand transformation impact:

```python
# Good: Use built-in comparison
comparison = service.compare_entities(trace_id)
print(f"Reduction: {comparison['reduction_rate']:.2%}")

# Also good: Manual comparison for custom analysis
raw = service.get_entities_raw(trace_id)
resolved = service.get_entities_resolved(trace_id)
# ... custom analysis
```

### 3. Enable Only for Debugging/Analysis

Intermediate data adds storage overhead. Enable only when needed:

```bash
# Production: Disabled (default)
# No env var needed

# Development/Debugging: Enabled
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
```

### 4. Set Appropriate TTL

Configure TTL based on your analysis needs:

```bash
# Short-term debugging (3 days)
export GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=3

# Long-term analysis (30 days)
export GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=30
```

### 5. Correlate with Transformation Logs

Use the same trace_id to correlate intermediate data with transformation logs:

```javascript
// Get intermediate data
db.entities_raw.find({ trace_id: "..." });
db.entities_resolved.find({ trace_id: "..." });

// Get transformation logs
db.transformation_logs.find({ trace_id: "..." });

// Combine for complete picture: data snapshots + transformation decisions
```

---

## 🔧 Troubleshooting

### No Data Found

**Check 1**: Is intermediate data saving enabled?

```bash
echo $GRAPHRAG_SAVE_INTERMEDIATE_DATA
# Should be "true"
```

**Check 2**: Check pipeline logs for save confirmations:

```bash
grep "Saved.*entities_raw\|Saved.*entities_resolved" logs/pipeline/*.log
```

**Check 3**: Verify collections exist:

```javascript
db.getCollectionNames().filter(
  (name) => name.includes("entities") || name.includes("relations")
);
```

### Data Expired (TTL)

**Check 1**: Verify TTL setting:

```bash
echo $GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS
# Default: 7
```

**Check 2**: Check data age:

```javascript
db.entities_raw.find().sort({ timestamp: -1 }).limit(1);
// If timestamp is > TTL days ago, data was deleted
```

### Slow Queries

**Check 1**: Use indexed fields:

```javascript
// Good: Uses trace_id index
db.entities_raw.find({ trace_id: "..." });

// Bad: No index
db.entities_raw.find({ entity_name: "..." });
```

**Check 2**: Limit results:

```javascript
// Good: Limited results
db.entities_raw.find({ trace_id: "..." }).limit(100);

// Bad: Full scan
db.entities_raw.find({});
```

---

## 📚 Related Documentation

- **IntermediateDataService API**: `business/services/graphrag/intermediate_data.py`
- **Stage Integrations**:
  - Entity Resolution: `business/stages/graphrag/entity_resolution.py`
  - Graph Construction: `business/stages/graphrag/graph_construction.py`
- **Transformation Logging**: `documentation/guides/GRAPHRAG-TRANSFORMATION-LOGGING.md`
- **Tests**: `tests/business/services/graphrag/test_intermediate_data.py`

---

## 📝 Example Analysis Workflow

### Complete Before/After Analysis

```python
from business.services.graphrag.intermediate_data import IntermediateDataService
from pymongo import MongoClient

# Setup
client = MongoClient("mongodb://localhost:27017")
db = client.youtuberag
service = IntermediateDataService(db, enabled=True)

trace_id = "your-trace-id-here"

# 1. Entity Resolution Analysis
print("=== ENTITY RESOLUTION ANALYSIS ===")
entity_comparison = service.compare_entities(trace_id)
print(f"Raw entities: {entity_comparison['raw_count']}")
print(f"Resolved entities: {entity_comparison['resolved_count']}")
print(f"Reduction rate: {entity_comparison['reduction_rate']:.2%}")

# 2. Graph Construction Analysis
print("\n=== GRAPH CONSTRUCTION ANALYSIS ===")
relation_comparison = service.compare_relations(trace_id)
print(f"Raw relationships: {relation_comparison['raw_count']}")
print(f"Final relationships: {relation_comparison['final_count']}")
print(f"Augmentation rate: {relation_comparison['augmentation_rate']:.2%}")

# 3. Graph Structure Analysis
print("\n=== GRAPH STRUCTURE ANALYSIS ===")
graph_data = service.get_graph_pre_detection(trace_id)
if graph_data:
    print(f"Nodes: {graph_data['node_count']}")
    print(f"Edges: {graph_data['edge_count']}")
    print(f"Density: {graph_data['density']:.4f}")
    print(f"Avg Degree: {graph_data['avg_degree']:.2f}")
    print(f"Components: {graph_data['connected_components']}")
```

---

**Version**: 1.0  
**Last Updated**: 2025-01-28  
**Maintainer**: GraphRAG Team
