# SUBPLAN: Transformation Logging Infrastructure

**Type**: SUBPLAN  
**Mother Plan**: PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md  
**Plan**: GRAPHRAG-OBSERVABILITY-EXCELLENCE  
**Achievement Addressed**: Achievement 0.1 (Transformation Logging Infrastructure Created)  
**Achievement**: 0.1  
**Status**: ✅ Complete  
**Created**: 2025-01-28 02:30 UTC  
**Estimated Effort**: 6-8 hours

**Metadata Tags**: See `LLM/guides/METADATA-TAGS.md` for virtual organization system

**File Location**: `work-space/subplans/SUBPLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE_01.md`

**Size**: 200-600 lines (increased to support multi-execution planning)

**Note**: This SUBPLAN operates independently - Designer creates design, plans execution(s), then Executor(s) execute. See `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` for complete workflow.

---

## 🎯 Objective

Build structured logging infrastructure that captures every transformation in the GraphRAG pipeline with reasons, enabling "why" questions. This implements Achievement 0.1 and provides the foundation for all observability features by making every transformation visible and explainable.

**Key Goal**: Enable answering questions like "Why did entity X merge with entity Y?" or "Why was relationship Z filtered?" by reading structured logs.

---

## 📋 What Needs to Be Created

### Files to Modify

1. **`business/stages/graphrag/entity_resolution.py`**:

   - Add transformation logging for entity operations (MERGE, CREATE, SKIP)
   - Log merge decisions with reasons, similarity scores, confidence
   - Log entity creation with type, sources, confidence
   - Log entity skips with reasons (stopwords, low confidence, etc.)

2. **`business/stages/graphrag/graph_construction.py`**:

   - Add transformation logging for relationship operations (RELATIONSHIP, FILTER, AUGMENT)
   - Log relationship creation from LLM extraction
   - Log relationship filtering decisions (below threshold, etc.)
   - Log relationship augmentation from post-processing methods (co-occurrence, semantic, cross-chunk, bidirectional)

3. **`business/stages/graphrag/community_detection.py`**:

   - Add transformation logging for community operations (COMMUNITY, CLUSTER)
   - Log community formation with modularity, coherence, entity count
   - Log entity assignments to communities with reasons
   - Log algorithm decisions (Leiden vs. Louvain, resolution parameter)

4. **`business/pipelines/graphrag.py`**:
   - Add trace_id generation at pipeline start
   - Pass trace_id to all stages
   - Store trace_id in pipeline metadata

### Files to Create

1. **`business/services/graphrag/transformation_logger.py`** (new):

   - Centralized transformation logging service
   - Structured JSON log format
   - Human-readable log format
   - Queryable log storage (MongoDB collection or structured logs)
   - Trace ID management

2. **`documentation/guides/GRAPHRAG-TRANSFORMATION-LOGGING.md`**:
   - Log format documentation
   - Log query examples
   - Usage guide for transformation logs

### Functions/Classes to Add

1. **`TransformationLogger` class** (in `transformation_logger.py`):

   - `log_transformation(operation, stage, data, trace_id)` - Main logging method
   - `log_entity_merge(entity_a, entity_b, reason, similarity, confidence, trace_id)`
   - `log_entity_create(entity, entity_type, sources, confidence, trace_id)`
   - `log_entity_skip(entity, reason, confidence, trace_id)`
   - `log_relationship_create(relationship, relationship_type, confidence, trace_id)`
   - `log_relationship_filter(relationship, reason, confidence, threshold, trace_id)`
   - `log_relationship_augment(relationship, method, confidence, trace_id)`
   - `log_community_form(community_id, entities, modularity, coherence, trace_id)`
   - `log_entity_cluster(entity_id, community_id, reason, neighbors, trace_id)`
   - `get_transformations_by_trace_id(trace_id)` - Query method
   - `get_transformations_by_entity_id(entity_id, trace_id)` - Query method

2. **Helper functions in stages**:
   - `_log_entity_operation()` in entity_resolution.py
   - `_log_relationship_operation()` in graph_construction.py
   - `_log_community_operation()` in community_detection.py

### Tests Required

1. **`tests/business/stages/graphrag/test_entity_resolution_logging.py`**:

   - Test MERGE logging with various reasons
   - Test CREATE logging
   - Test SKIP logging
   - Test trace_id linking

2. **`tests/business/stages/graphrag/test_graph_construction_logging.py`**:

   - Test RELATIONSHIP logging
   - Test FILTER logging
   - Test AUGMENT logging for each method
   - Test trace_id linking

3. **`tests/business/stages/graphrag/test_community_detection_logging.py`**:

   - Test COMMUNITY logging
   - Test CLUSTER logging
   - Test algorithm decision logging
   - Test trace_id linking

4. **`tests/business/services/graphrag/test_transformation_logger.py`**:
   - Test TransformationLogger class
   - Test log format (JSON and human-readable)
   - Test query methods
   - Test trace_id management

---

## 📝 Approach

**Strategy**: Create centralized transformation logging service, then integrate into each stage incrementally. Use structured JSON logs for queryability while maintaining human-readable format for debugging.

**Method**:

1. **Phase 1: Create Transformation Logger Service**:

   - Design log schema (operation, stage, entity_id, reason, confidence, trace_id, timestamp)
   - Implement TransformationLogger class with all log methods
   - Create MongoDB collection for structured logs (optional, can use file logs initially)
   - Implement query methods for trace_id and entity_id

2. **Phase 2: Integrate Trace ID System**:

   - Generate trace_id at pipeline start in `graphrag.py`
   - Pass trace_id to all stages via config or stage context
   - Store trace_id in pipeline metadata

3. **Phase 3: Add Entity Resolution Logging**:

   - Identify all transformation points in entity resolution:
     - Entity merge decisions (in `_store_resolved_entities()`)
     - Entity creation (in `_store_resolved_entities()`)
     - Entity skip decisions (if any)
   - Add logging calls at each transformation point
   - Extract merge reasons, similarity scores, confidence values
   - Test with real data

4. **Phase 4: Add Graph Construction Logging**:

   - Identify all transformation points in graph construction:
     - Relationship creation from LLM extraction
     - Relationship filtering (below threshold, etc.)
     - Relationship augmentation (co-occurrence, semantic, cross-chunk, bidirectional)
   - Add logging calls at each transformation point
   - Extract augmentation methods, filtering reasons, confidence values
   - Test with real data

5. **Phase 5: Add Community Detection Logging**:

   - Identify all transformation points in community detection:
     - Community formation (in `_detect_communities()`)
     - Entity assignments to communities
     - Algorithm decisions (Leiden vs. Louvain, resolution parameter)
   - Add logging calls at each transformation point
   - Extract modularity, coherence, algorithm parameters
   - Test with real data

6. **Phase 6: Documentation and Examples**:
   - Document log format specifications
   - Create log query examples
   - Create usage guide

**Key Considerations**:

- **Performance**: Logging must not slow pipeline significantly (<10% overhead)

  - Use async logging where possible
  - Batch log writes
  - Make logging optional via environment flag

- **Log Storage**:

  - Option 1: MongoDB collection `transformation_logs` (queryable, persistent)
  - Option 2: Structured JSON log files (simpler, but less queryable)
  - Recommendation: Start with MongoDB collection for queryability

- **Log Format**:

  - JSON for machine parsing and querying
  - Human-readable format for debugging (can be generated from JSON)
  - Include all queryable fields: entity_id, operation, reason, confidence, stage, trace_id, timestamp

- **Trace ID Linking**:

  - Generate unique trace_id per pipeline run
  - Link all transformations across stages with same trace_id
  - Enable querying all transformations for a specific run or entity

- **Code Changes**:
  - Minimize changes to existing logic
  - Add logging calls at transformation points
  - Don't modify core transformation logic
  - Make logging optional (can disable for production if needed)

**Risks to Watch For**:

- **Performance Impact**: Logging overhead may slow pipeline

  - Mitigation: Measure baseline, add logging incrementally, optimize if >10% overhead

- **Code Complexity**: Adding logging may make code harder to read

  - Mitigation: Use helper methods, keep logging calls concise

- **Log Volume**: Large datasets may generate many logs
  - Mitigation: Use efficient storage, implement retention policy, make logging optional

---

## 🔄 Execution Strategy

**Execution Count**: Multiple (Sequential)

**Rationale**:

- Multiple independent components (logger service, trace ID, 3 stages)
- Sequential execution allows learning from each stage
- Each stage builds on previous work (logger service first, then integrations)
- Can test each stage independently before moving to next

**Execution Type**: Sequential

**Execution Plan**:

1. **EXECUTION_TASK_01_01**: Create Transformation Logger Service

   - Create `transformation_logger.py` with TransformationLogger class
   - Implement all log methods
   - Create MongoDB collection schema
   - Write unit tests
   - **Dependencies**: None
   - **Estimated**: 2-3 hours

2. **EXECUTION_TASK_01_02**: Integrate Trace ID System

   - Generate trace_id in `graphrag.py`
   - Pass trace_id to stages
   - Update pipeline metadata
   - Write integration tests
   - **Dependencies**: EXECUTION_TASK_01_01 (logger service)
   - **Estimated**: 1 hour

3. **EXECUTION_TASK_01_03**: Add Entity Resolution Logging

   - Integrate logger into entity_resolution.py
   - Add logging at merge, create, skip points
   - Extract transformation data
   - Write tests
   - **Dependencies**: EXECUTION_TASK_01_01, EXECUTION_TASK_01_02
   - **Estimated**: 1.5-2 hours

4. **EXECUTION_TASK_01_04**: Add Graph Construction Logging

   - Integrate logger into graph_construction.py
   - Add logging at relationship create, filter, augment points
   - Extract transformation data
   - Write tests
   - **Dependencies**: EXECUTION_TASK_01_01, EXECUTION_TASK_01_02
   - **Estimated**: 1.5-2 hours

5. **EXECUTION_TASK_01_05**: Add Community Detection Logging

   - Integrate logger into community_detection.py
   - Add logging at community form, cluster assignment points
   - Extract transformation data
   - Write tests
   - **Dependencies**: EXECUTION_TASK_01_01, EXECUTION_TASK_01_02
   - **Estimated**: 1-1.5 hours

6. **EXECUTION_TASK_01_06**: Documentation and Examples
   - Create logging format documentation
   - Create log query examples
   - Create usage guide
   - **Dependencies**: All previous executions
   - **Estimated**: 0.5-1 hour

**Total Estimated Time**: 7.5-11.5 hours (slightly over 6-8h estimate, but allows for learning curve)

**Parallelization**: No - sequential execution required due to dependencies

---

## 🔄 Active EXECUTION_TASKs

| Execution | Status      | File                                                      | Dependencies |
| --------- | ----------- | --------------------------------------------------------- | ------------ |
| 01_01     | ✅ Complete | EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-EXCELLENCE_01_01.md | None         |
| 01_02     | ⏳ Next     | EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-EXCELLENCE_01_02.md | 01_01        |
| 01_03     | Planning    | EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-EXCELLENCE_01_03.md | 01_01, 01_02 |
| 01_04     | Planning    | EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-EXCELLENCE_01_04.md | 01_01, 01_02 |
| 01_05     | Planning    | EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-EXCELLENCE_01_05.md | 01_01, 01_02 |
| 01_06     | Planning    | EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-EXCELLENCE_01_06.md | All previous |

---

## 🧪 Tests

### Test Strategy

**Unit Tests**: Test TransformationLogger class in isolation
**Integration Tests**: Test logging integration in each stage
**Performance Tests**: Measure logging overhead

### Test Cases

#### TransformationLogger Tests

1. **Test log_transformation()**:

   - Verify JSON log format
   - Verify human-readable format
   - Verify all fields present

2. **Test entity logging methods**:

   - `log_entity_merge()` - Verify merge log format
   - `log_entity_create()` - Verify create log format
   - `log_entity_skip()` - Verify skip log format

3. **Test relationship logging methods**:

   - `log_relationship_create()` - Verify relationship log format
   - `log_relationship_filter()` - Verify filter log format
   - `log_relationship_augment()` - Verify augment log format

4. **Test community logging methods**:

   - `log_community_form()` - Verify community log format
   - `log_entity_cluster()` - Verify cluster log format

5. **Test query methods**:
   - `get_transformations_by_trace_id()` - Verify trace_id query
   - `get_transformations_by_entity_id()` - Verify entity_id query

#### Entity Resolution Logging Tests

1. **Test MERGE logging**:

   - Verify merge logged with correct reason, similarity, confidence
   - Verify trace_id linked
   - Test with fuzzy_match, embedding_match, context_match reasons

2. **Test CREATE logging**:

   - Verify entity creation logged with type, sources, confidence
   - Verify trace_id linked

3. **Test SKIP logging** (if applicable):
   - Verify entity skip logged with reason
   - Verify trace_id linked

#### Graph Construction Logging Tests

1. **Test RELATIONSHIP logging**:

   - Verify relationship creation logged with type, confidence
   - Verify trace_id linked

2. **Test FILTER logging**:

   - Verify relationship filter logged with reason, threshold
   - Verify trace_id linked

3. **Test AUGMENT logging**:
   - Verify each augmentation method logged (co-occurrence, semantic, cross-chunk, bidirectional)
   - Verify trace_id linked

#### Community Detection Logging Tests

1. **Test COMMUNITY logging**:

   - Verify community formation logged with modularity, coherence, entity count
   - Verify trace_id linked

2. **Test CLUSTER logging**:

   - Verify entity assignment logged with reason, neighbors
   - Verify trace_id linked

3. **Test algorithm decision logging**:
   - Verify algorithm choice logged (Leiden vs. Louvain)
   - Verify resolution parameter logged

#### Performance Tests

1. **Test logging overhead**:

   - Measure pipeline execution time without logging
   - Measure pipeline execution time with logging
   - Verify overhead <10%

2. **Test log volume**:
   - Run pipeline on sample dataset
   - Measure log count and size
   - Verify storage efficiency

---

## ✅ Expected Results

### Deliverables

1. ✅ **TransformationLogger service** (`business/services/graphrag/transformation_logger.py`)

   - All log methods implemented
   - JSON and human-readable formats
   - Query methods functional

2. ✅ **Trace ID system integrated** (`business/pipelines/graphrag.py`)

   - Trace ID generated per pipeline run
   - Trace ID passed to all stages
   - Trace ID stored in metadata

3. ✅ **Entity resolution logging** (`business/stages/graphrag/entity_resolution.py`)

   - MERGE operations logged
   - CREATE operations logged
   - SKIP operations logged (if applicable)
   - All logs include trace_id

4. ✅ **Graph construction logging** (`business/stages/graphrag/graph_construction.py`)

   - RELATIONSHIP operations logged
   - FILTER operations logged
   - AUGMENT operations logged (all methods)
   - All logs include trace_id

5. ✅ **Community detection logging** (`business/stages/graphrag/community_detection.py`)

   - COMMUNITY operations logged
   - CLUSTER operations logged
   - Algorithm decisions logged
   - All logs include trace_id

6. ✅ **Documentation** (`documentation/guides/GRAPHRAG-TRANSFORMATION-LOGGING.md`)

   - Log format specifications
   - Log query examples
   - Usage guide

7. ✅ **Tests** (all test files listed above)
   - Unit tests for TransformationLogger
   - Integration tests for each stage
   - Performance tests

### Success Criteria

- [ ] Every transformation logged with reason
- [ ] All logs structured (JSON format)
- [ ] All logs queryable (by trace_id, entity_id, stage, operation)
- [ ] Trace ID links transformations across stages
- [ ] Performance impact <10%
- [ ] All tests passing (>90% coverage)
- [ ] Documentation complete

### Quality Metrics

- **Code Coverage**: >90% for new code
- **Performance Overhead**: <10% pipeline slowdown
- **Log Completeness**: 100% of transformations logged
- **Query Functionality**: Can query logs by trace_id, entity_id, stage, operation

---

## 📚 References

### Code Files to Study

- `business/stages/graphrag/entity_resolution.py` - Entity resolution stage
- `business/stages/graphrag/graph_construction.py` - Graph construction stage
- `business/stages/graphrag/community_detection.py` - Community detection stage
- `business/agents/graphrag/entity_resolution.py` - Entity resolution agent
- `business/pipelines/graphrag.py` - Pipeline orchestration
- `core/models/graphrag.py` - Data models

### Related PLANs

- `PLAN_ENTITY-RESOLUTION-REFACTOR.md` - Entity resolution context
- `PLAN_COMMUNITY-DETECTION-REFACTOR.md` - Community detection context

### Documentation

- `EXECUTION_ANALYSIS_GRAPHRAG-OBSERVABILITY-READINESS.md` - Blind spots and monitoring framework

---

**Status**: Design Complete, Ready for Execution  
**Next**: Create EXECUTION_TASK_01_01 (Transformation Logger Service)
