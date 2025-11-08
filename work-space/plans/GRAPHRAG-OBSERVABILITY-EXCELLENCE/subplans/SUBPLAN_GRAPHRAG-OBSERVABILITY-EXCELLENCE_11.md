# SUBPLAN: Transformation Explanation Tools

**Type**: SUBPLAN  
**Mother Plan**: PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md  
**Plan**: GRAPHRAG-OBSERVABILITY-EXCELLENCE  
**Achievement Addressed**: Achievement 1.1 (Transformation Explanation Tools Created)  
**Achievement**: 1.1  
**Status**: Design Complete, Ready for Execution  
**Created**: 2025-11-10 01:00 UTC  
**Estimated Effort**: 8-10 hours

**File Location**: `work-space/plans/GRAPHRAG-OBSERVABILITY-EXCELLENCE/subplans/SUBPLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE_11.md`

**Size**: 200-600 lines

**Note**: This SUBPLAN builds on Priority 0 achievements (Transformation Logging, Intermediate Data, Query Scripts, Quality Metrics). It creates interactive tools to answer "why" questions about transformations, enabling deep understanding of pipeline decisions.

---

## 🎯 Objective

Create 5 interactive CLI tools that explain GraphRAG pipeline transformations by querying transformation logs and intermediate data. These tools answer "why" questions about entity merges, relationship filtering, community formation, entity journeys, and graph evolution, making the pipeline transparent and debuggable.

---

## 📋 What Needs to Be Created

### Explanation Tools (5 scripts)

**`scripts/repositories/graphrag/explain/` folder structure**:

```
explain/
├── __init__.py
├── explain_utils.py (shared utilities)
├── explain_entity_merge.py
├── explain_relationship_filter.py
├── explain_community_formation.py
├── trace_entity_journey.py
├── visualize_graph_evolution.py
└── README.md
```

### 1. Entity Merge Explainer

**`explain_entity_merge.py`** - Explain why two entities merged

**Functionality**:

- Input: Two entity IDs (or names)
- Query transformation_logs for entity_merge operations
- Show similarity score, merge method, confidence
- Display original entity names, descriptions, chunks
- Show merge decision reasoning

**Example Usage**:

```bash
python explain_entity_merge.py --entity-a "Barack Obama" --entity-b "President Obama"
python explain_entity_merge.py --entity-id-a abc123 --entity-id-b def456 --trace-id xyz
```

**Output**:

- Merge decision (merged/not merged)
- Similarity score
- Merge method (fuzzy match, exact match, semantic)
- Confidence score
- Original entity details (names, types, chunks)
- Merge reasoning from transformation logs

### 2. Relationship Filter Explainer

**`explain_relationship_filter.py`** - Explain why relationship kept or dropped

**Functionality**:

- Input: Entity pair (source, target)
- Query transformation_logs for relationship_filter operations
- Show all extraction attempts for this pair
- Display filtering decisions (kept/dropped, why)
- Show confidence, threshold, predicate canonicalization

**Example Usage**:

```bash
python explain_relationship_filter.py --source "Apple" --target "iPhone"
python explain_relationship_filter.py --source-id abc --target-id def --trace-id xyz
```

**Output**:

- All extraction attempts (chunk IDs, predicates, confidences)
- Filtering decisions (kept/dropped)
- Reasons (low confidence, duplicate, density safeguard)
- Final relationship (if kept)

### 3. Community Formation Explainer

**`explain_community_formation.py`** - Explain why entities clustered

**Functionality**:

- Input: Community ID
- Query communities collection
- Show community members (entities)
- Display relationships within community
- Calculate and show coherence factors
- Show algorithm parameters (Leiden, resolution, etc.)

**Example Usage**:

```bash
python explain_community_formation.py --community-id comm_123
python explain_community_formation.py --community-id comm_123 --trace-id xyz
```

**Output**:

- Community members (entity IDs, names, types)
- Relationships within community (count, types)
- Coherence score and factors
- Algorithm used and parameters
- Modularity contribution

### 4. Entity Journey Tracer

**`trace_entity_journey.py`** - Trace complete entity transformation journey

**Functionality**:

- Input: Entity name or ID
- Query all collections and logs for this entity
- Show complete lifecycle:
  - **Extraction**: Which chunks, confidence, type
  - **Resolution**: Merge decisions, method, final ID
  - **Graph**: Relationships, types, sources
  - **Detection**: Community assignment, role
- Timeline visualization

**Example Usage**:

```bash
python trace_entity_journey.py --entity "Barack Obama"
python trace_entity_journey.py --entity-id abc123 --trace-id xyz
```

**Output**:

- **Stage 1: Extraction**
  - Chunks where entity appeared
  - Extraction confidence
  - Entity type
- **Stage 2: Resolution**
  - Merge decisions (if any)
  - Merge method and confidence
  - Final resolved entity ID
- **Stage 3: Graph Construction**
  - Relationships (count, types)
  - Relationship sources (LLM, co-occurrence, semantic)
  - Node degree
- **Stage 4: Community Detection**
  - Community ID
  - Community size
  - Entity role (hub, peripheral, etc.)

### 5. Graph Evolution Visualizer

**`visualize_graph_evolution.py`** - Show graph structure evolution

**Functionality**:

- Input: Trace ID
- Query transformation_logs for relationship_create and relationship_augment
- Show graph evolution through construction steps:
  - Step 1: LLM relationships only
  - Step 2: + Co-occurrence relationships
  - Step 3: + Semantic similarity relationships
  - Step 4: + Cross-chunk relationships
- Track density and degree at each step

**Example Usage**:

```bash
python visualize_graph_evolution.py --trace-id xyz
python visualize_graph_evolution.py --trace-id xyz --output graph_evolution.json
```

**Output**:

- **Step-by-step metrics**:
  - Node count
  - Edge count (cumulative)
  - Graph density
  - Average degree
  - Edges added in this step
- **Breakdown by source**:
  - LLM: X relationships
  - Co-occurrence: Y relationships
  - Semantic similarity: Z relationships
- **Visualization** (text-based or JSON for external tools)

### Shared Utilities

**`explain_utils.py`** - Common functions for all tools

**Functionality**:

- MongoDB connection helper
- Transformation log queries
- Intermediate data queries
- Output formatting (table, JSON, text)
- Entity lookup (by name or ID)
- Trace ID validation

### Documentation

**`README.md`** - Usage guide for all explanation tools

**Content**:

- Overview of explanation tools
- Installation and setup
- Usage examples for each tool
- Common use cases
- Troubleshooting

---

## 🎨 Approach

**Strategy**: Create modular CLI tools that leverage existing transformation logs and intermediate data to provide interactive explanations. Each tool focuses on a specific "why" question, with shared utilities for common operations.

**Method**:

1. **Phase 1: Shared Infrastructure** (1.5h)

   - Create `explain/` folder structure
   - Implement `explain_utils.py` with common functions
   - MongoDB connection, query helpers, output formatting
   - Test with sample queries

2. **Phase 2: Entity Merge Explainer** (1.5h)

   - Implement `explain_entity_merge.py`
   - Query transformation_logs for entity_merge operations
   - Display merge decision, similarity, reasoning
   - Test with real merge examples

3. **Phase 3: Relationship Filter Explainer** (1.5h)

   - Implement `explain_relationship_filter.py`
   - Query transformation_logs for relationship_filter operations
   - Show all extraction attempts and filtering decisions
   - Test with filtered relationships

4. **Phase 4: Community Formation Explainer** (1.5h)

   - Implement `explain_community_formation.py`
   - Query communities collection
   - Calculate coherence factors
   - Test with real communities

5. **Phase 5: Entity Journey Tracer** (2h)

   - Implement `trace_entity_journey.py`
   - Query all collections for entity lifecycle
   - Build timeline visualization
   - Test with entities across all stages

6. **Phase 6: Graph Evolution Visualizer** (1.5h)

   - Implement `visualize_graph_evolution.py`
   - Query transformation_logs for relationship operations
   - Track graph metrics at each step
   - Test with full pipeline run

7. **Phase 7: Documentation** (0.5h)
   - Create README.md with usage examples
   - Document common use cases
   - Add troubleshooting section

**Key Design Decisions**:

- **CLI Tools**: Interactive command-line tools (not library functions) for ease of use
- **Leverage Existing Data**: Use transformation logs and intermediate data (no new data collection)
- **JSON Output**: All tools support JSON output for programmatic use
- **Shared Utilities**: Common functions in `explain_utils.py` to avoid duplication
- **Argparse Interface**: Consistent argument parsing across all tools

**Key Considerations**:

- **Performance**: Queries should be fast (use indexed fields)
- **Usability**: Clear, human-readable output
- **Flexibility**: Support both entity names and IDs
- **Trace ID Support**: All tools support filtering by trace_id

---

## 🔄 Execution Strategy

**Execution Count**: Single

**Rationale**:

- All 5 tools follow same pattern (query logs/data, format output)
- Shared infrastructure enables rapid development
- Sequential implementation with testing at each step
- Single execution with comprehensive verification

**EXECUTION_TASK**: `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-EXCELLENCE_11_01.md`

---

## 🧪 Tests Required

### Unit Tests

**Test File**: `tests/scripts/repositories/graphrag/explain/test_explain_utils.py`

**Test Cases**:

- Test MongoDB connection
- Test entity lookup (by name, by ID)
- Test transformation log queries
- Test output formatting (table, JSON)

### Integration Tests

**Test File**: `tests/scripts/repositories/graphrag/explain/test_explain_tools.py`

**Test Cases**:

- Test each tool with sample data
- Test JSON output parsing
- Test error handling (entity not found, no data)
- Test trace_id filtering

### Manual Testing

**Approach**: Run each tool with real pipeline data

- Use actual trace_id from completed pipeline run
- Verify explanations match expected behavior
- Test edge cases (no merges, no relationships, etc.)

---

## 📊 Expected Results

### Deliverables Checklist

- [ ] `scripts/repositories/graphrag/explain/` folder created
- [ ] `explain_utils.py` created (200-300 lines)
- [ ] `explain_entity_merge.py` created (150-200 lines)
- [ ] `explain_relationship_filter.py` created (150-200 lines)
- [ ] `explain_community_formation.py` created (150-200 lines)
- [ ] `trace_entity_journey.py` created (200-250 lines)
- [ ] `visualize_graph_evolution.py` created (200-250 lines)
- [ ] `README.md` created (200-300 lines)
- [ ] All tools functional and tested
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Manual testing complete

### Success Metrics

**Functionality**:

- All 5 tools run without errors
- Tools answer "why" questions accurately
- JSON output is valid and complete
- Tools work with any trace_id

**Usability**:

- Clear, human-readable output
- Helpful error messages
- Consistent interface across tools
- Examples in --help text

**Performance**:

- Queries complete in <2 seconds
- Efficient use of indexes
- No unnecessary data loading

**Value**:

- Enables understanding of pipeline decisions
- Helps debug quality issues
- Supports iterative improvement

### Example Output

**Entity Merge Explainer**:

```
═══════════════════════════════════════════════════════════
   ENTITY MERGE EXPLANATION
═══════════════════════════════════════════════════════════

Trace ID: abc-123-def
Merge Decision: ✅ MERGED

Entity A:
  Name: Barack Obama
  Type: person
  Confidence: 0.92
  Chunks: [chunk_1, chunk_3, chunk_5]

Entity B:
  Name: President Obama
  Type: person
  Confidence: 0.88
  Chunks: [chunk_7, chunk_9]

Merge Details:
  Method: fuzzy_match
  Similarity Score: 0.87
  Confidence: 0.90
  Reason: High name similarity, same type, overlapping context

Merged Entity:
  Final ID: entity_abc123
  Final Name: Barack Obama
  Total Chunks: 5
  Combined Confidence: 0.90
```

**Entity Journey Tracer**:

```
═══════════════════════════════════════════════════════════
   ENTITY JOURNEY: Barack Obama
═══════════════════════════════════════════════════════════

Trace ID: abc-123-def

Stage 1: EXTRACTION
  ✅ Extracted from 5 chunks
  - chunk_1: confidence=0.92, type=person
  - chunk_3: confidence=0.90, type=person
  - chunk_5: confidence=0.88, type=person
  - chunk_7: confidence=0.85, type=person (as "President Obama")
  - chunk_9: confidence=0.87, type=person (as "President Obama")

Stage 2: RESOLUTION
  ✅ Merged 2 mentions → 1 entity
  - Merge: "Barack Obama" + "President Obama"
  - Method: fuzzy_match, similarity=0.87
  - Final ID: entity_abc123

Stage 3: GRAPH CONSTRUCTION
  ✅ Connected to 12 entities
  - 8 LLM relationships (works_for, located_in, etc.)
  - 3 co-occurrence relationships
  - 1 semantic similarity relationship
  - Node degree: 12

Stage 4: COMMUNITY DETECTION
  ✅ Assigned to community comm_5
  - Community size: 25 entities
  - Role: hub (high degree)
  - Coherence: 0.78
```

---

## 🔗 Dependencies

**Required Before Starting**:

- ✅ Achievement 0.1: Transformation Logging (provides transformation_logs)
- ✅ Achievement 0.2: Intermediate Data Collections (provides intermediate data)
- ✅ Achievement 0.3: Query Scripts (provides query patterns)
- ✅ MongoDB accessible with transformation logs and intermediate data

**Blocks**:

- Achievement 1.2: Visual Comparison Tools (will use explanation tools)
- Future debugging and optimization work

---

## 📝 Implementation Notes

### Query Patterns

**Entity Merge Query**:

```python
# Find merge operations for specific entities
transformation_logs.find({
    "trace_id": trace_id,
    "operation": "entity_merge",
    "$or": [
        {"before.entity_id": entity_id_a},
        {"before.entity_id": entity_id_b},
        {"after.entity_id": entity_id_a},
        {"after.entity_id": entity_id_b}
    ]
})
```

**Relationship Filter Query**:

```python
# Find filter operations for entity pair
transformation_logs.find({
    "trace_id": trace_id,
    "operation": "relationship_filter",
    "entity_ids": {"$all": [source_id, target_id]}
})
```

**Entity Journey Query**:

```python
# Find all operations involving entity
transformation_logs.find({
    "trace_id": trace_id,
    "$or": [
        {"entity_id": entity_id},
        {"before.entity_id": entity_id},
        {"after.entity_id": entity_id}
    ]
}).sort("timestamp", 1)
```

### Output Formatting

**Table Format** (default):

- Human-readable tables using tabulate or similar
- Color coding for important information
- Clear section headers

**JSON Format** (--format json):

- Valid JSON for programmatic use
- Complete data (no truncation)
- Consistent structure across tools

**Text Format** (--format text):

- Plain text (no colors)
- Suitable for logging or piping

---

## 🔄 Active EXECUTION_TASKs

| Execution | Status     | File                                                      | Dependencies |
| --------- | ---------- | --------------------------------------------------------- | ------------ |
| 11_01     | ⏳ Pending | EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-EXCELLENCE_11_01.md | None         |

---

**Status**: ✅ Design Complete, Ready for Execution  
**Next Step**: Create EXECUTION_TASK_11_01 and begin implementation  
**Estimated Duration**: 8-10 hours (single execution)  
**Critical Success Factor**: Tools must provide clear, actionable explanations that enable understanding and debugging of pipeline decisions
