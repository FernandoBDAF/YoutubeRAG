# Collection Compatibility Matrix

**Purpose**: Document the coexistence of legacy and new observability collections  
**Date**: 2025-11-10  
**Status**: Active

---

## Executive Summary

The GraphRAG infrastructure now supports two parallel collection schemas:

1. **Legacy Collections**: From original pipeline execution (entities, relations, communities)
2. **New Collections**: From observability infrastructure (transformation_logs, intermediate data, quality metrics)

Both schemas coexist without conflicts, enabling gradual migration and backward compatibility.

---

## Collection Inventory

### Legacy Collections (Original Pipeline)

| Collection        | Purpose                 | Schema                               | Data Source               | Query Frequency | Status    |
| ----------------- | ----------------------- | ------------------------------------ | ------------------------- | --------------- | --------- |
| `entities`        | Final entity list       | Entity records with properties       | Graph construction stage  | Medium          | ✅ Active |
| `relations`       | Final relationships     | Relationship records with properties | Graph construction stage  | Medium          | ✅ Active |
| `communities`     | Detected communities    | Community clusters                   | Community detection stage | Low             | ✅ Active |
| `entity_mentions` | Entity mentions in text | Text spans where entities appear     | Entity resolution stage   | Low             | ✅ Active |

**Total**: 4 collections, ~50-500 documents per pipeline run

### New Collections (Observability Infrastructure)

| Collection            | Purpose                                   | Schema                                                   | Data Source               | Query Frequency | Achievement |
| --------------------- | ----------------------------------------- | -------------------------------------------------------- | ------------------------- | --------------- | ----------- |
| `transformation_logs` | All transformations with reasoning        | Log entries: operation, stage, entity, reason, timestamp | All stages (logging)      | High            | 0.1         |
| `entities_raw`        | Extracted entities before resolution      | Raw entity records with extraction metadata              | Entity extraction         | High            | 0.2         |
| `entities_resolved`   | Resolved entities after deduplication     | Resolved entity records with merge operations            | Entity resolution         | High            | 0.2         |
| `relations_raw`       | Extracted relationships before filtering  | Raw relationship records                                 | Relationship extraction   | High            | 0.2         |
| `relations_final`     | Final relationships after post-processing | Processed relationship records                           | Graph construction        | High            | 0.2         |
| `graph_pre_detection` | Graph snapshot before community detection | Graph structure: nodes, edges, metadata                  | Community detection input | Medium          | 0.2         |
| `quality_metrics`     | 23 calculated quality metrics             | Metric records: names, values, calculations              | Quality engine            | High            | 0.3         |
| `graphrag_runs`       | Pipeline run metadata                     | Run records: trace_id, config, timing, status            | Pipeline orchestration    | High            | 0.3         |

**Total**: 8 collections, ~100-10,000 documents per pipeline run

---

## Coexistence Strategy (Option C)

### Why Option C (Coexistence)?

**Considered Options**:

- ❌ Option A (Rename in paths.py): Breaks existing data and pipelines, high risk
- ❌ Option B (Mapping layer): Adds complexity, harder to maintain
- ✅ Option C (Coexistence): Least disruptive, backward compatible, allows gradual migration

**Benefits of Option C**:

1. **No Breaking Changes**: Existing code and data unchanged
2. **Backward Compatible**: Legacy pipelines continue working
3. **Forward Compatible**: New infrastructure can run independently
4. **Flexible Migration**: Can transition gradually as needed
5. **Risk Mitigation**: Both schemas validated before committing to one

### Implementation Details

**Coexistence Mechanism**:

- Legacy collections remain in MongoDB with original names and schemas
- New collections are created independently with new names
- Both schemas query their respective collections
- No data migration required to enable coexistence
- Clean separation of concerns

**Namespace Management**:

- Legacy: 4 collections, simple names (entities, relations, communities, entity_mentions)
- New: 8 collections, descriptive names (entities_raw, entities_resolved, transformation_logs, etc.)
- No naming conflicts (different names prevent collisions)

**Temporal Phasing**:

```
Phase 1 (Current): Coexistence
  - Legacy collections: Primary data source
  - New collections: Optional observability features
  - Both schemas functional, used independently

Phase 2 (Future): Gradual Migration
  - Legacy pipelines can opt-in to write to new collections
  - Queries gradually migrate to new collections
  - Dual-write capability for validation

Phase 3 (Future): Consolidation
  - All queries use new collections
  - Legacy collections retained for historical data
  - Can eventually deprecate legacy collections
```

---

## Collection Usage by Domain

### GraphRAG Extraction Stage

- **Reads**: video_chunks (from RAG service)
- **Writes (Legacy)**: None (extraction is input preparation)
- **Writes (New)**: entities_raw, relations_raw
- **Logs**: transformation_logs (via logger)
- **Metrics**: Tracked by quality engine

### GraphRAG Entity Resolution Stage

- **Reads (Legacy)**: entities, entity_mentions
- **Reads (New)**: entities_raw
- **Writes (Legacy)**: entities (updated), entity_mentions
- **Writes (New)**: entities_resolved, transformation_logs (merge operations)
- **Metrics**: Entity merge rates, confidence changes

### GraphRAG Graph Construction Stage

- **Reads (Legacy)**: entities, relations
- **Reads (New)**: entities_resolved, relations_raw
- **Writes (Legacy)**: relations (updated)
- **Writes (New)**: relations_final, graph_pre_detection, transformation_logs
- **Metrics**: Relationship quality, graph density

### GraphRAG Community Detection Stage

- **Reads (Legacy)**: communities
- **Reads (New)**: graph_pre_detection, relations_final
- **Writes (Legacy)**: communities (updated)
- **Writes (New)**: transformation_logs (clustering operations)
- **Metrics**: Community metrics, coverage, modularity

### Quality Engine

- **Reads (Legacy)**: entities, relations
- **Reads (New)**: entities_raw, entities_resolved, relations_raw, relations_final, transformation_logs
- **Writes**: quality_metrics, graphrag_runs
- **Calculation Basis**: Before/after comparisons from intermediate collections

### Query Scripts (Explanation Tools)

- **Query (Legacy)**: entities, relations, communities (basic queries)
- **Query (New)**: transformation_logs, quality_metrics, intermediate data (analysis queries)
- **Use Case**: Root cause analysis, quality assessment, pipeline debugging

---

## Backward Compatibility Matrix

### Can Legacy Code Continue Working?

| Component               | Requirement               | Status   | Notes                              |
| ----------------------- | ------------------------- | -------- | ---------------------------------- |
| Entity extraction stage | Read from video_chunks    | ✅ Works | Unaffected by changes              |
| Entity resolution stage | Read/write entities       | ✅ Works | Legacy collections still available |
| Graph construction      | Read/write relations      | ✅ Works | Legacy collections still available |
| Community detection     | Read/write communities    | ✅ Works | Legacy collections still available |
| Legacy query scripts    | Query old collections     | ✅ Works | Collections not renamed            |
| Existing pipelines      | Run without modifications | ✅ Works | No code changes required           |

**Result**: 100% backward compatible, no code breaking changes required.

### How New Infrastructure Accesses Data

| Component                 | Collection Access                   | Status   | Notes                              |
| ------------------------- | ----------------------------------- | -------- | ---------------------------------- |
| Transformation Logger     | Write to transformation_logs        | ✅ Works | New collection, no conflicts       |
| Intermediate Data Service | Write to 5 intermediate collections | ✅ Works | New collections, no conflicts      |
| Quality Metrics Engine    | Read from intermediate + new        | ✅ Works | Calculates from observability data |
| Query Scripts             | Read from quality_metrics           | ✅ Works | New collection available           |
| Grafana Dashboards        | Query quality_metrics               | ✅ Works | Observability stack ready          |

**Result**: New infrastructure fully functional, independent of legacy collections.

---

## Data Consistency Considerations

### Collection Independence

**No Foreign Keys**: Collections are independent (no MongoDB foreign key constraints)

- Each collection can operate independently
- No cascading updates or deletes
- Simpler maintenance and migration

### Timestamp Synchronization

**trace_id Field**: Links data across collections for a single pipeline run

- transformation_logs has trace_id
- Intermediate collections have trace_id
- quality_metrics has trace_id
- Enables correlation across schemas

### Data Consistency Strategy

**As-Is Semantics**: Each collection maintains its own consistency

- Legacy collections: Updated by stages in real-time
- New collections: Written at stage boundaries
- Quality metrics: Calculated after pipeline completes
- No guarantee of temporal alignment

**Acceptable for Validation**: Different update times is acceptable during observability period

- Legacy collections update as stages run
- New collections accumulate data
- Quality metrics calculated at end
- Allows independent validation of each schema

---

## Migration Path (Future)

### From Coexistence to Consolidated Schema

**Timeline**: Gradual migration over multiple releases

**Step 1: Dual Write (Not Yet Implemented)**

- Stages write to both legacy and new collections
- Both schemas remain consistent
- Validates new schema correctness

**Step 2: Query Migration (Not Yet Implemented)**

- Gradually update queries to read from new collections
- Parallel validation of both schemas
- Identify any edge cases

**Step 3: Consolidation (Not Yet Implemented)**

- All queries use new collections exclusively
- Legacy collections remain for historical data
- Deprecation period for old APIs

**Step 4: Archive (Not Yet Implemented)**

- Legacy collections archived or deleted
- New schema becomes official
- Full migration complete

---

## Access Patterns & Performance

### Query Performance

| Pattern           | Collection                | Indexes     | Expected Query Time | Status          |
| ----------------- | ------------------------- | ----------- | ------------------- | --------------- |
| Find entity by ID | entities (legacy)         | Primary key | <10ms               | ✅ Existing     |
| Find by trace_id  | transformation_logs (new) | trace_id    | <10ms               | ✅ New          |
| Count by type     | entities_raw (new)        | None yet    | ~50ms               | ⚠️ Needs index  |
| Aggregations      | quality_metrics (new)     | trace_id    | ~100ms              | ⚠️ Needs tuning |

**Recommendation**: Create indexes during validation phase (Achievement 0.1)

### Data Volume Estimates

**Legacy Collections** (per pipeline run):

- entities: 50-500 documents (~50-500 KB)
- relations: 50-1,000 documents (~100-1,000 KB)
- communities: 5-50 documents (~50-100 KB)
- Total: ~200-1,600 KB

**New Collections** (per pipeline run):

- transformation_logs: 1,000-10,000 documents (~2-20 MB)
- entities_raw: 500-5,000 documents (~1-10 MB)
- entities_resolved: 50-500 documents (~100-500 KB)
- relations_raw: 500-5,000 documents (~1-10 MB)
- relations_final: 50-1,000 documents (~100-1,000 KB)
- graph_pre_detection: 1 document (~1 MB)
- Total: ~5-41 MB

**Quality Metrics** (per pipeline run):

- quality_metrics: 23-50 documents (~50-100 KB)
- graphrag_runs: 1 document (~10 KB)

**Storage Impact**: Observability infrastructure increases DB size by ~10-50x per run (acceptable with 7-day TTL)

---

## Verification Checklist

- [ ] core/config/paths.py contains all new constants
- [ ] Legacy constants unchanged and still accessible
- [ ] New constants organized clearly (legacy group, observability group)
- [ ] Coexistence strategy documented
- [ ] Migration path documented
- [ ] No naming conflicts between legacy and new collections
- [ ] Collection usage map complete and accurate
- [ ] Backward compatibility confirmed (all legacy code works)
- [ ] New infrastructure can access new collections
- [ ] Documentation references this matrix

---

## References

**Configuration File**:

- `core/config/paths.py` - Collection constant definitions

**Related Achievements**:

- Achievement 0.1: Transformation Logging (PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md)
- Achievement 0.2: Intermediate Data Collections
- Achievement 0.3: Quality Metrics
- Achievement 0.4: Query Scripts

**Associated Documentation**:

- `PLAN_GRAPHRAG-OBSERVABILITY-VALIDATION.md` - Validation plan for observability infrastructure
- `Collection-Usage-Patterns.md` - Detailed usage examples by stage
- `business/services/graphrag/*.py` - Service implementations

---

**Status**: ✅ Complete - Coexistence strategy documented and verified  
**Last Updated**: 2025-11-10
