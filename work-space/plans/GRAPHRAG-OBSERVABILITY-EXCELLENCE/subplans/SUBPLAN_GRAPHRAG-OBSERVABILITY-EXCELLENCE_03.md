# SUBPLAN: Stage Boundary Query Scripts

**Type**: SUBPLAN  
**Mother Plan**: PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md  
**Plan**: GRAPHRAG-OBSERVABILITY-EXCELLENCE  
**Achievement Addressed**: Achievement 0.3 (Stage Boundary Query Scripts Created)  
**Achievement**: 0.3  
**Status**: Design Complete, Ready for Execution  
**Created**: 2025-11-09 22:00 UTC  
**Estimated Effort**: 8-10 hours

**File Location**: `work-space/plans/GRAPHRAG-OBSERVABILITY-EXCELLENCE/subplans/SUBPLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE_03.md`

**Size**: 200-600 lines

**Note**: This SUBPLAN builds on Achievements 0.1 (Transformation Logging) and 0.2 (Intermediate Data Collections). It creates query scripts to analyze the logged transformations and intermediate data, enabling actual use of the observability infrastructure.

---

## 🎯 Objective

Create a comprehensive suite of query scripts that enable analysis of GraphRAG data at every stage boundary. These scripts will query the transformation logs (Achievement 0.1) and intermediate data collections (Achievement 0.2) to answer "why" questions about entity resolution, relationship construction, and community detection. This implements Achievement 0.3 and provides the analytical tools needed to understand pipeline behavior and identify quality improvement opportunities.

---

## 📋 What Needs to Be Created

### Directory Structure

- `scripts/repositories/graphrag/queries/` - New folder for all query scripts

### Extraction Query Scripts (2 scripts)

1. **`query_raw_entities.py`** - Query entities as extracted (before resolution)
   - Query `entities_raw` collection from IntermediateDataService
   - Filter by: trace_id, entity_type, confidence, chunk_id
   - Show: entity details, source chunks, extraction metadata
   - Export: JSON, CSV, table formats
   - Use case: "What entities were extracted from chunk X?"

2. **`compare_extraction_runs.py`** - Compare extraction from different runs
   - Compare entity counts across trace_ids
   - Compare type distributions
   - Identify extraction quality differences
   - Use case: "Did the new prompt extract more entities?"

### Resolution Query Scripts (3 scripts)

3. **`query_resolution_decisions.py`** - Query merge decisions from transformation logs
   - Query `transformation_logs` collection (type: entity_merge)
   - Filter by: trace_id, merge_reason (fuzzy/embedding/context), confidence
   - Show: before/after names, similarity scores, reasons
   - Use case: "Why did entity A merge with entity B?"

4. **`compare_before_after_resolution.py`** - Compare raw vs. resolved entities
   - Query `entities_raw` vs `entities_resolved` collections
   - Calculate: merge rate (entity count reduction %)
   - Compare: type distributions, confidence changes
   - Use case: "How effective is entity resolution?"

5. **`find_resolution_errors.py`** - Identify potential false positives/negatives
   - Find: high-confidence merges with low similarity (suspicious)
   - Find: high similarity entities that didn't merge (missed)
   - Export: candidates for manual review
   - Use case: "What resolution errors should I investigate?"

### Construction Query Scripts (3 scripts)

6. **`query_raw_relationships.py`** - Query relationships before post-processing
   - Query `relations_raw` collection
   - Filter by: trace_id, relationship_type, entities
   - Show: relationship details, source chunks
   - Use case: "What relationships were extracted?"

7. **`compare_before_after_construction.py`** - Compare raw vs. final relationships
   - Query `relations_raw` vs `relations_final` collections
   - Calculate: count increase from post-processing
   - Show: which methods added how many (co-occurrence, semantic, etc.)
   - Use case: "How much did post-processing add?"

8. **`query_graph_evolution.py`** - Track graph metrics through construction
   - Query transformation logs for relationship_create/augment
   - Calculate: density evolution, degree distribution changes
   - Show: how graph structure evolved
   - Use case: "How did the graph grow during construction?"

### Detection Query Scripts (2 scripts)

9. **`query_pre_detection_graph.py`** - Analyze graph before community detection
   - Query `graph_pre_detection` collection
   - Show: graph structure, connectivity, degree distribution
   - Use case: "What did the graph look like before communities?"

10. **`compare_detection_algorithms.py`** - Compare Leiden vs. Louvain vs. Infomap
    - Query transformation logs (type: community_form)
    - Compare: community count, sizes, modularity scores
    - Identify: which algorithm works best for your data
    - Use case: "Should I use Leiden or Louvain?"

### Shared Infrastructure

- **`query_utils.py`** - Shared utilities for all query scripts
  - MongoDB connection handling
  - Output formatting (table, JSON, CSV)
  - Common filters (trace_id, date range)
  - Aggregation helpers

### Documentation

- **`README.md`** - Query scripts documentation
  - Overview of all scripts
  - Common use cases
  - Query examples
  - Output format reference

---

## 🎨 Approach

**Strategy**: Create a standardized suite of query scripts that leverage the observability infrastructure (transformation logs + intermediate data collections) to enable deep analysis of GraphRAG pipeline behavior at each stage boundary.

**Method**:

1. **Phase 1: Shared Infrastructure** (1h)
   - Create `query_utils.py` with common functions
   - Standardize argparse interface (all scripts use same pattern)
   - Implement output formatters (table, JSON, CSV)
   - Test MongoDB connection handling

2. **Phase 2: Extraction Queries** (1.5h)
   - Implement `query_raw_entities.py`
   - Implement `compare_extraction_runs.py`
   - Test with actual intermediate data
   - Document use cases

3. **Phase 3: Resolution Queries** (2h)
   - Implement `query_resolution_decisions.py`
   - Implement `compare_before_after_resolution.py`
   - Implement `find_resolution_errors.py`
   - Test with transformation logs and intermediate data
   - Document use cases

4. **Phase 4: Construction Queries** (2h)
   - Implement `query_raw_relationships.py`
   - Implement `compare_before_after_construction.py`
   - Implement `query_graph_evolution.py`
   - Test with intermediate data
   - Document use cases

5. **Phase 5: Detection Queries** (1.5h)
   - Implement `query_pre_detection_graph.py`
   - Implement `compare_detection_algorithms.py`
   - Test with transformation logs
   - Document use cases

6. **Phase 6: Documentation & Integration** (1h)
   - Create comprehensive README.md
   - Add examples to all script --help
   - Integration test: run all scripts on real pipeline run
   - Document common query patterns

**Key Design Decisions**:

- **Standardized Interface**: All scripts use argparse with consistent flags (--trace-id, --format, --output)
- **Multiple Output Formats**: Table (human-readable), JSON (programmatic), CSV (spreadsheet)
- **Filter Support**: All scripts support filtering by trace_id, date range, and domain-specific fields
- **Real Data Focus**: Test with actual pipeline runs, not synthetic data
- **Use Case Driven**: Each script solves a specific "why" question

**Key Considerations**:

- **Performance**: Queries should complete in <10 seconds for typical datasets
- **Usability**: Scripts should be self-documenting (good --help text)
- **Integration**: Scripts should work with existing MongoDB setup (no new dependencies)
- **Extensibility**: Easy to add new queries as needs emerge

---

## 🔄 Execution Strategy

**Execution Count**: Single

**Rationale**: 
- Clear, straightforward implementation of 10+ query scripts
- All scripts follow same pattern (shared infrastructure)
- Sequential implementation by stage (extraction → resolution → construction → detection)
- No need for A/B testing or comparison
- Single execution with comprehensive verification

**EXECUTION_TASK**: `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-EXCELLENCE_03_01.md`

---

## 🧪 Tests Required

### Unit Tests

**Test File**: `tests/scripts/repositories/graphrag/queries/test_query_utils.py`

**Test Cases**:
- Test MongoDB connection handling
- Test output formatters (table, JSON, CSV)
- Test common filters (trace_id, date range)
- Test aggregation helpers

### Integration Tests

**Test File**: `tests/scripts/repositories/graphrag/queries/test_query_scripts.py`

**Test Cases**:
- Test each query script with sample data
- Test output format consistency
- Test filter functionality
- Test error handling (missing trace_id, no data, etc.)

### Manual Testing

**Approach**: Run all scripts on actual pipeline run data
- Use a real trace_id from recent pipeline run
- Verify each script produces expected output
- Test all output formats (table, JSON, CSV)
- Verify filters work correctly

**Test Data**: Use existing pipeline runs in MongoDB (from validation work)

---

## 📊 Expected Results

### Deliverables Checklist

- [ ] `scripts/repositories/graphrag/queries/` folder created
- [ ] `query_utils.py` - Shared utilities (200-300 lines)
- [ ] `query_raw_entities.py` - Extraction query (150-200 lines)
- [ ] `compare_extraction_runs.py` - Extraction comparison (150-200 lines)
- [ ] `query_resolution_decisions.py` - Resolution query (200-250 lines)
- [ ] `compare_before_after_resolution.py` - Resolution comparison (200-250 lines)
- [ ] `find_resolution_errors.py` - Error detection (200-250 lines)
- [ ] `query_raw_relationships.py` - Construction query (150-200 lines)
- [ ] `compare_before_after_construction.py` - Construction comparison (200-250 lines)
- [ ] `query_graph_evolution.py` - Graph evolution (200-250 lines)
- [ ] `query_pre_detection_graph.py` - Detection query (150-200 lines)
- [ ] `compare_detection_algorithms.py` - Algorithm comparison (200-250 lines)
- [ ] `README.md` - Documentation (300-400 lines)
- [ ] Unit tests passing (>90% coverage)
- [ ] Integration tests passing
- [ ] All scripts tested with real data

### Success Metrics

**Functionality**:
- All 10+ scripts execute without errors
- All output formats work correctly (table, JSON, CSV)
- All filters work as expected
- Scripts complete in <10 seconds for typical datasets

**Usability**:
- --help text is clear and helpful
- Examples provided for each script
- Error messages are informative
- Documentation is comprehensive

**Integration**:
- Scripts work with existing MongoDB setup
- Scripts work with transformation logs from Achievement 0.1
- Scripts work with intermediate data from Achievement 0.2
- No new dependencies required

**Value**:
- Can answer "why" questions about transformations
- Can identify quality improvement opportunities
- Can compare pipeline runs
- Can detect potential errors

### Example Usage

```bash
# Query raw entities from a specific run
python scripts/repositories/graphrag/queries/query_raw_entities.py \
  --trace-id abc123 \
  --type PERSON \
  --format table

# Compare entity counts before/after resolution
python scripts/repositories/graphrag/queries/compare_before_after_resolution.py \
  --trace-id abc123 \
  --format json

# Find potential resolution errors
python scripts/repositories/graphrag/queries/find_resolution_errors.py \
  --trace-id abc123 \
  --confidence-threshold 0.9 \
  --format csv \
  --output resolution_errors.csv

# Compare detection algorithms
python scripts/repositories/graphrag/queries/compare_detection_algorithms.py \
  --trace-id-1 abc123 \
  --trace-id-2 def456 \
  --format table
```

---

## 🔗 Dependencies

**Required Before Starting**:
- ✅ Achievement 0.1: Transformation Logging (provides transformation_logs collection)
- ✅ Achievement 0.2: Intermediate Data Collections (provides 5 intermediate collections)
- ✅ MongoDB accessible with existing collections
- ✅ Python environment with pymongo installed

**Blocks**:
- Achievement 1.1: Quality Metrics (will use these queries)
- Achievement 1.2: Explanation Tools (will use these queries)
- All analysis work (depends on query capabilities)

---

## 📝 Implementation Notes

### MongoDB Collections Used

**From Achievement 0.1 (Transformation Logging)**:
- `transformation_logs` - All transformation events
  - Filter by: type (entity_merge, relationship_create, etc.)
  - Fields: trace_id, timestamp, transformation_type, details, reason

**From Achievement 0.2 (Intermediate Data)**:
- `entities_raw` - Entities before resolution
- `entities_resolved` - Entities after resolution
- `relations_raw` - Relationships before post-processing
- `relations_final` - Relationships after post-processing
- `graph_pre_detection` - Graph before community detection

### Query Patterns

**Common Pattern**:
```python
# 1. Parse arguments (trace_id, filters, format)
# 2. Connect to MongoDB
# 3. Build query (filters, aggregations)
# 4. Execute query
# 5. Format output (table/JSON/CSV)
# 6. Display or export
```

**Aggregation Example**:
```python
# Count entities by type
pipeline = [
    {"$match": {"trace_id": trace_id}},
    {"$group": {"_id": "$entity_type", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]
```

### Output Format Standards

**Table Format**:
- Use `tabulate` library
- Max width 120 characters
- Truncate long fields with "..."

**JSON Format**:
- Pretty-printed (indent=2)
- ISO 8601 timestamps
- Include metadata (query, timestamp, count)

**CSV Format**:
- Standard CSV (comma-separated)
- Headers in first row
- Escape special characters

---

## 🔄 Active EXECUTION_TASKs

| Execution | Status      | File                                                      | Dependencies |
| --------- | ----------- | --------------------------------------------------------- | ------------ |
| 03_01     | ⏳ Pending  | EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-EXCELLENCE_03_01.md | None         |

---

**Status**: ✅ Design Complete, Ready for Execution  
**Next Step**: Create EXECUTION_TASK_03_01 and begin implementation  
**Estimated Duration**: 8-10 hours (single execution)  
**Critical Success Factor**: All scripts must work with real pipeline data, not just synthetic examples


