# SUBPLAN: Intermediate Data Collections

**Type**: SUBPLAN  
**Mother Plan**: PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md  
**Plan**: GRAPHRAG-OBSERVABILITY-EXCELLENCE  
**Achievement Addressed**: Achievement 0.2 (Intermediate Data Collections Created)  
**Achievement**: 0.2  
**Status**: Design Complete, Ready for Execution  
**Created**: 2025-01-28 10:45 UTC  
**Estimated Effort**: 5-7 hours

**File Location**: `work-space/plans/GRAPHRAG-OBSERVABILITY-EXCELLENCE/subplans/SUBPLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE_02.md`

**Size**: 200-600 lines

**Note**: This SUBPLAN builds on Achievement 0.1 (Transformation Logging). Uses trace_id for linking transformations to intermediate data states.

---

## 🎯 Objective

Create MongoDB collections for intermediate data at each stage boundary, enabling before/after analysis of transformations. This complements Achievement 0.1 by capturing data state at each stage, allowing queries like "what were the raw entities before resolution?" or "how did post-processing change relationships?"

---

## 📋 Deliverables

### Collections to Create

1. `entities_raw` - Entities as extracted (before resolution)
2. `entities_resolved` - Entities after resolution (before graph)
3. `relations_raw` - Relationships as extracted (before post-processing)
4. `relations_final` - Relationships after post-processing (before detection)
5. `graph_pre_detection` - Graph structure before community detection

### Schema Design

- **Core Fields**: trace_id, entity_id/relationship_id, timestamp, stage_metadata
- **Quality Fields**: confidence, source_count, extraction_method
- **Linking**: trace_id enables correlation with transformation logs

### Stage Updates

- **Entity Resolution**: Save to entities_raw (pre-merge), entities_resolved (post-merge)
- **Graph Construction**: Save to relations_raw (pre-processing), relations_final (post-processing)
- **Community Detection**: Save graph_pre_detection (before detection)

### Indexing Strategy

- Single field indexes: trace_id, entity_id, timestamp
- Compound indexes: (trace_id, stage), (entity_id, timestamp)
- TTL indexes for automatic cleanup

### Configuration

- Environment flag: `GRAPHRAG_SAVE_INTERMEDIATE_DATA=true`
- Retention policy: Auto-delete after N days (configurable)

### Documentation

- Schema documentation for each collection
- Query examples for common analyses
- Best practices for before/after comparisons

---

## 🎨 Approach

**Strategy**: Create schema definitions, implement collection saving at stage boundaries, add indexing, enable via environment flag, document for analysts.

**Method**:

1. **Phase 1: Schema Design** - Define MongoDB schemas for each collection (2 tasks)
2. **Phase 2: Stage Integration** - Update stages to save intermediate data (3 tasks)
3. **Phase 3: Indexing & Configuration** - Add indexes and environment control (1 task)
4. **Phase 4: Documentation** - Create usage guides and examples (1 task)

**Key Design Decisions**:

- All intermediate collections include trace_id for transformation correlation
- Collections are optional (disabled by default for production)
- Schema matches existing GraphRAG models for consistency
- TTL indexes for automatic experiment cleanup

---

## 🔄 Execution Strategy

**Execution Count**: Multiple (4 sequential phases)

**Rationale**:

- Phases build on each other (schema → integration → indexing → docs)
- Sequential execution ensures proper testing between phases
- Each phase can be verified independently

**Execution Plan**:

1. **EXECUTION_TASK_02_01**: Schema Definition & Collections Setup

   - Define schemas for all 5 collections
   - Create collection in MongoDB with initial indexes
   - Dependencies: None
   - Estimated: 2 hours

2. **EXECUTION_TASK_02_02**: Entity Resolution Stage Integration

   - Update entity_resolution.py to save intermediate data
   - Save to entities_raw and entities_resolved
   - Add trace_id linking
   - Dependencies: 02_01
   - Estimated: 1.5 hours

3. **EXECUTION_TASK_02_03**: Graph Construction Stage Integration

   - Update graph_construction.py to save intermediate data
   - Save to relations_raw and relations_final
   - Add trace_id linking
   - Dependencies: 02_01
   - Estimated: 1.5 hours

4. **EXECUTION_TASK_02_04**: Documentation & Query Examples
   - Create schema documentation
   - Create query examples for analysts
   - Best practices guide
   - Dependencies: 02_02, 02_03
   - Estimated: 1 hour

**Parallelization**: No - sequential execution required due to dependencies

---

## 🧪 Tests

### Unit Tests

- Schema validation (verify fields and types)
- Data persistence (verify saves to MongoDB)
- Index creation and verification
- Environment variable control

### Integration Tests

- Entity resolution stage: Verify raw/resolved data saved
- Graph construction stage: Verify raw/final data saved
- Before/after queries: Verify data retrievable and comparable
- Trace ID linking: Verify correlation with transformation logs

### Manual Tests

- Run full pipeline with intermediate data enabled
- Query data at each stage boundary
- Verify data completeness and consistency

---

## 📊 Expected Results

**After Completion**:

- 5 new MongoDB collections with proper schemas
- Entity resolution: saves both raw and resolved entities (trace_id linked)
- Graph construction: saves both raw and post-processed relationships (trace_id linked)
- Community detection: saves pre-detection graph state
- Environment flag control: Can enable/disable intermediate data saving
- Query examples: Analysts can run "before/after" comparisons
- Zero overhead when disabled (flag check early in pipeline)

**Quality Metrics**:

- All collections have proper indexes (no full collection scans)
- TTL indexes working (data auto-deletes after retention period)
- Trace_id linking 100% complete (all data traceable to pipeline run)

---

## 🎓 Learning Outcomes

**After Completion, You Will Understand**:

- MongoDB schema design for intermediate data
- Trade-offs between storage and queryability
- Before/after analysis patterns
- How to add non-invasive data collection to existing stages

---

## ✅ Completion Criteria

- [x] Schema defined for all 5 collections
- [x] Collections created with proper indexes
- [x] Entity resolution stage updated
- [x] Graph construction stage updated
- [x] Environment flag control implemented
- [x] Documentation and examples created
- [x] All EXECUTION_TASKs complete (<200 lines each)
- [x] All tests passing
- [x] No performance regression when disabled

---

## 🔄 Active EXECUTION_TASKs

| Execution | Status      | File                                                      | Dependencies |
| --------- | ----------- | --------------------------------------------------------- | ------------ |
| 02_01     | ✅ Complete | EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-EXCELLENCE_02_01.md | None         |
| 02_02     | ✅ Complete | EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-EXCELLENCE_02_02.md | 02_01        |
| 02_03     | ✅ Complete | EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-EXCELLENCE_02_03.md | 02_01        |
| 02_04     | ✅ Complete | EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-EXCELLENCE_02_04.md | 02_02, 02_03 |

---

**Status**: ✅ Complete

**Achievement 0.2**: Intermediate Data Collections Created - ALL TASKS COMPLETE
