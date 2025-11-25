# Collection Usage Guide

**Achievement**: 4.2 - Legacy Collection Coexistence Verified  
**Date**: 2025-11-13  
**Purpose**: Guide for choosing between legacy and observability collections  
**Audience**: Developers, Data Analysts, Pipeline Users

---

## 📚 Collection Inventory

### Legacy Collections (Original Pipeline)

| Collection    | Purpose                     | Status              | Use When                                    |
| ------------- | --------------------------- | ------------------- | ------------------------------------------- |
| `entities`    | Stores extracted entities   | ✅ Exists (empty)   | Using legacy pipeline without observability |
| `relations`   | Stores entity relationships | ✅ Exists (empty)   | Using legacy pipeline without observability |
| `communities` | Stores detected communities | ✅ Exists (empty)   | Using legacy pipeline without observability |
| `chunks`      | Stores text chunks          | ✅ Exists (25 docs) | Always (shared by both pipelines)           |

### Observability Collections (New Pipeline)

| Collection                   | Purpose                        | Status            | Use When                                            |
| ---------------------------- | ------------------------------ | ----------------- | --------------------------------------------------- |
| `entities_resolved`          | Final resolved entities        | ⏳ Pending        | Using observability pipeline (replaces `entities`)  |
| `relations_final`            | Final filtered relationships   | ⏳ Pending        | Using observability pipeline (replaces `relations`) |
| `transformation_logs`        | Transformation decisions       | ⏳ Pending        | Debugging, understanding pipeline behavior          |
| `entity_mentions`            | Raw extracted entities         | ✅ Exists (empty) | Debugging extraction stage                          |
| `entities_before_resolution` | Entities before resolution     | ⏳ Pending        | Comparing before/after resolution                   |
| `entities_after_resolution`  | Entities after resolution      | ⏳ Pending        | Comparing before/after resolution                   |
| `relations_before_filter`    | Relationships before filtering | ⏳ Pending        | Comparing before/after filtering                    |
| `quality_metrics`            | Quality metrics per stage      | ⏳ Pending        | Monitoring pipeline quality                         |
| `graphrag_runs`              | Pipeline run metadata          | ✅ Exists (empty) | Tracking pipeline executions                        |

---

## 🎯 When to Use Which Collection

### Scenario 1: Production Pipeline (No Debugging Needed)

**Use**: Legacy Collections

**Collections**:

- `entities` - Final entities
- `relations` - Final relationships
- `communities` - Detected communities

**Why**:

- Minimal storage overhead
- Faster pipeline execution
- Simple schema

**How to Enable**:

```bash
# Disable observability features
export GRAPHRAG_TRANSFORMATION_LOGGING=false
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
export GRAPHRAG_QUALITY_METRICS=false
```

---

### Scenario 2: Development/Debugging

**Use**: Observability Collections

**Collections**:

- `entities_resolved` - Final entities (with trace_id)
- `relations_final` - Final relationships (with trace_id)
- `transformation_logs` - Decision logs
- `entity_mentions` - Raw extractions
- `entities_before_resolution` - Pre-resolution state
- `entities_after_resolution` - Post-resolution state
- `relations_before_filter` - Pre-filter relationships
- `quality_metrics` - Quality metrics

**Why**:

- Full visibility into pipeline behavior
- Can trace decisions
- Can debug issues
- Can compare before/after states

**How to Enable**:

```bash
# Enable observability features
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
export GRAPHRAG_QUALITY_METRICS=true
```

---

### Scenario 3: Quality Monitoring

**Use**: Observability Collections (Selective)

**Collections**:

- `entities_resolved` - Final entities
- `relations_final` - Final relationships
- `quality_metrics` - Quality metrics
- `graphrag_runs` - Run metadata

**Why**:

- Track quality over time
- Monitor pipeline health
- Identify degradation

**How to Enable**:

```bash
# Enable quality metrics only
export GRAPHRAG_TRANSFORMATION_LOGGING=false
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
export GRAPHRAG_QUALITY_METRICS=true
```

---

### Scenario 4: Experimentation/A-B Testing

**Use**: Observability Collections (Full)

**Collections**:

- All observability collections
- Use `experiment_id` to distinguish runs

**Why**:

- Compare different pipeline versions
- Track experiments systematically
- Analyze performance differences

**How to Enable**:

```bash
# Enable all observability features
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
export GRAPHRAG_QUALITY_METRICS=true

# Run with experiment ID
python business/pipelines/graphrag.py \
  --experiment-id experiment-v2 \
  --video-id <video-id>
```

---

## 🔄 Collection Naming Conventions

### Legacy Collections

**Pattern**: Simple, descriptive names

- `entities` - Entity collection
- `relations` - Relationship collection
- `communities` - Community collection

**Characteristics**:

- Short names
- No suffixes
- Backward compatible

---

### Observability Collections

**Pattern**: Descriptive names with suffixes

- `entities_resolved` - Final state indicator (`_resolved`)
- `relations_final` - Final state indicator (`_final`)
- `transformation_logs` - Purpose indicator (`_logs`)
- `entities_before_resolution` - State indicator (`_before_resolution`)
- `entities_after_resolution` - State indicator (`_after_resolution`)
- `relations_before_filter` - State indicator (`_before_filter`)
- `quality_metrics` - Purpose indicator (`_metrics`)

**Characteristics**:

- Descriptive suffixes
- Clear purpose
- Easy to distinguish from legacy

---

## 📊 Collection Purpose and Contents

### `entities` (Legacy)

**Purpose**: Store final extracted entities

**Schema**:

```json
{
  "_id": "ObjectId",
  "name": "string",
  "type": "string",
  "description": "string",
  "metadata": "object"
}
```

**Query Example**:

```bash
mongosh mongo_hack --eval "db.entities.find({ type: 'PERSON' }).limit(10)"
```

---

### `entities_resolved` (Observability)

**Purpose**: Store final resolved entities with observability metadata

**Schema**:

```json
{
  "_id": "ObjectId",
  "name": "string",
  "type": "string",
  "description": "string",
  "metadata": "object",
  "trace_id": "string",
  "experiment_id": "string",
  "resolution_metadata": {
    "merged_from": ["entity_id_1", "entity_id_2"],
    "confidence": 0.95
  }
}
```

**Query Example**:

```bash
mongosh mongo_hack --eval "db.entities_resolved.find({ trace_id: 'abc123' }).limit(10)"
```

---

### `transformation_logs` (Observability)

**Purpose**: Store transformation decisions for debugging

**Schema**:

```json
{
  "_id": "ObjectId",
  "trace_id": "string",
  "stage": "string",
  "operation": "string",
  "decision": "string",
  "reason": "string",
  "timestamp": "ISODate",
  "metadata": "object"
}
```

**Query Example**:

```bash
mongosh mongo_hack --eval "db.transformation_logs.find({ stage: 'resolution' }).limit(10)"
```

---

### `quality_metrics` (Observability)

**Purpose**: Store quality metrics per stage

**Schema**:

```json
{
  "_id": "ObjectId",
  "trace_id": "string",
  "stage": "string",
  "metric_name": "string",
  "value": "number",
  "timestamp": "ISODate"
}
```

**Query Example**:

```bash
mongosh mongo_hack --eval "db.quality_metrics.find({ stage: 'extraction' }).limit(10)"
```

---

## 🔀 Field Mapping (Legacy → Observability)

### Entities

| Legacy Field  | Observability Field   | Notes                           |
| ------------- | --------------------- | ------------------------------- |
| `_id`         | `_id`                 | Same                            |
| `name`        | `name`                | Same                            |
| `type`        | `type`                | Same                            |
| `description` | `description`         | Same                            |
| `metadata`    | `metadata`            | Same                            |
| N/A           | `trace_id`            | **NEW**: Observability tracking |
| N/A           | `experiment_id`       | **NEW**: Experiment tracking    |
| N/A           | `resolution_metadata` | **NEW**: Resolution details     |

### Relations

| Legacy Field | Observability Field | Notes                           |
| ------------ | ------------------- | ------------------------------- |
| `_id`        | `_id`               | Same                            |
| `source`     | `source`            | Same                            |
| `target`     | `target`            | Same                            |
| `type`       | `type`              | Same                            |
| `weight`     | `weight`            | Same                            |
| N/A          | `trace_id`          | **NEW**: Observability tracking |
| N/A          | `experiment_id`     | **NEW**: Experiment tracking    |
| N/A          | `filter_metadata`   | **NEW**: Filtering details      |

---

## 📝 Query Examples

### Query Legacy Collections

```bash
# Count entities
mongosh mongo_hack --eval "db.entities.countDocuments()"

# Find entities by type
mongosh mongo_hack --eval "db.entities.find({ type: 'PERSON' })"

# Find relationships
mongosh mongo_hack --eval "db.relations.find({ source: 'entity_123' })"
```

### Query Observability Collections

```bash
# Count resolved entities
mongosh mongo_hack --eval "db.entities_resolved.countDocuments()"

# Find entities by trace_id
mongosh mongo_hack --eval "db.entities_resolved.find({ trace_id: 'abc123' })"

# Find transformation logs for a trace
mongosh mongo_hack --eval "db.transformation_logs.find({ trace_id: 'abc123' })"

# Find quality metrics for extraction stage
mongosh mongo_hack --eval "db.quality_metrics.find({ stage: 'extraction' })"
```

---

## ✅ Best Practices

### 1. Choose Collections Based on Use Case

- **Production**: Use legacy collections (minimal overhead)
- **Development**: Use observability collections (full visibility)
- **Monitoring**: Use selective observability (quality metrics only)

### 2. Use trace_id for Debugging

- Always query by `trace_id` when debugging
- Enables tracing decisions across stages
- Links all observability data for a run

### 3. Clean Up Old Data

- Set TTL indexes on observability collections
- Keep legacy collections lean
- Archive old experiments

### 4. Monitor Storage Growth

- Observability collections can grow quickly
- Monitor database size regularly
- Adjust retention policies as needed

### 5. Document Collection Usage

- Document which collections your queries use
- Update queries when switching collections
- Test queries against both collection types

---

## 🚀 Migration Path

### If Currently Using Legacy Collections

1. **Enable Observability**: Set environment variables
2. **Run Pipeline**: New collections will be created
3. **Test Queries**: Verify new collections work
4. **Update Code**: Switch queries to new collections
5. **Monitor**: Watch for issues
6. **Deprecate Legacy**: Once confident, stop using legacy collections

### If Starting Fresh

1. **Use Observability Collections**: Enable from the start
2. **Skip Legacy**: No need to create legacy collections
3. **Benefit**: Full observability from day one

---

## 📚 Summary

**Key Takeaways**:

- Legacy collections are simple, minimal overhead
- Observability collections provide full visibility
- Collections coexist peacefully (different names)
- Choose based on use case (production vs. development)
- Use `trace_id` for debugging
- Monitor storage growth

**Recommendation**: Use observability collections in development, consider legacy for production if overhead is a concern.

---

**Guide Status**: ✅ COMPLETE  
**Last Updated**: 2025-11-13  
**Next Review**: After observability pipeline run
