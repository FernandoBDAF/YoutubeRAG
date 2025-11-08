# SUBPLAN: Per-Stage Quality Metrics Implementation

**Type**: SUBPLAN  
**Mother Plan**: PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md  
**Plan**: GRAPHRAG-OBSERVABILITY-EXCELLENCE  
**Achievement Addressed**: Achievement 0.4 (Per-Stage Quality Metrics Implemented)  
**Achievement**: 0.4  
**Status**: ✅ Complete  
**Created**: 2025-11-09 23:45 UTC  
**Completed**: 2025-11-10 00:45 UTC  
**Estimated Effort**: 8-10 hours  
**Actual Effort**: 4 hours

**File Location**: `work-space/plans/GRAPHRAG-OBSERVABILITY-EXCELLENCE/subplans/SUBPLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE_04.md`

**Size**: 200-600 lines

**Note**: This SUBPLAN builds on Achievements 0.1 (Transformation Logging), 0.2 (Intermediate Data Collections), and 0.3 (Query Scripts). It implements comprehensive quality metrics at each pipeline stage to enable data-driven improvement decisions.

---

## 🎯 Objective

Implement comprehensive quality metrics collection at each GraphRAG pipeline stage (extraction, resolution, construction, detection), storing metrics in MongoDB collections and exposing them via existing APIs and dashboards. This completes Priority 0 (CRITICAL - Transformation Visibility Foundation) by providing quantitative measures of pipeline quality at each stage, enabling data-driven improvement decisions and regression detection.

---

## 📋 What Needs to Be Created

### Metrics Collection Module

**`business/services/graphrag/quality_metrics.py`** - New service for metrics calculation

- Extract metrics from transformation logs and intermediate data
- Calculate per-stage quality metrics
- Store metrics in MongoDB collections
- Provide query interface for metrics retrieval

### Stage Integration (4 stages)

1. **`business/stages/graphrag/extraction.py`** - Add extraction metrics

   - Entity count per chunk (avg, distribution)
   - Relationship count per chunk (avg, distribution)
   - Predicate diversity
   - Type coverage
   - Confidence distribution
   - Canonical predicate coverage

2. **`business/stages/graphrag/entity_resolution.py`** - Add resolution metrics

   - Merge rate
   - Duplicate reduction
   - Confidence preservation
   - Cross-video linking rate
   - False positive estimate
   - False negative estimate

3. **`business/stages/graphrag/graph_construction.py`** - Add construction metrics

   - Graph density
   - Average degree
   - Degree distribution
   - Relationship type balance
   - Post-processing contribution
   - Density safeguard triggers

4. **`business/stages/graphrag/community_detection.py`** - Add detection metrics
   - Modularity score
   - Community count and size distribution
   - Coherence scores per community
   - Singleton rate
   - Coverage

### API Enhancement

**`app/api/quality_metrics.py`** - Enhance existing API

- Add endpoints for new per-stage metrics
- Add time-series queries
- Add comparison endpoints (run vs. run)
- Add healthy range checks

### Dashboard Enhancement

**`app/ui/quality_metrics_dashboard.html`** - Update existing dashboard

- Add per-stage metrics visualization
- Add trend charts
- Add healthy range indicators
- Add alerts for out-of-range metrics

### Documentation

**`documentation/guides/QUALITY-METRICS.md`** - Metrics documentation

- Metric definitions
- Healthy ranges
- Interpretation guidelines
- Troubleshooting

### Configuration

**Healthy range definitions** - Define acceptable ranges for each metric

- Document in configuration or constants file
- Used for alerting and dashboard indicators

---

## 🎨 Approach

**Strategy**: Create a centralized quality metrics service that calculates metrics from transformation logs and intermediate data, then integrate metric collection into each pipeline stage. Expose metrics through existing API and dashboard infrastructure.

**Method**:

1. **Phase 1: Metrics Service Foundation** (2h)

   - Create `QualityMetricsService` class
   - Implement metric calculation methods
   - Implement MongoDB storage (graphrag_runs, quality_metrics collections)
   - Test with sample data

2. **Phase 2: Extraction Metrics** (1.5h)

   - Integrate metrics collection into extraction stage
   - Calculate 6 extraction metrics
   - Store in graphrag_runs collection
   - Verify metrics accuracy

3. **Phase 3: Resolution Metrics** (1.5h)

   - Integrate metrics collection into resolution stage
   - Calculate 6 resolution metrics
   - Use transformation logs for false positive/negative estimates
   - Verify metrics accuracy

4. **Phase 4: Construction Metrics** (1.5h)

   - Integrate metrics collection into construction stage
   - Calculate 6 construction metrics
   - Use transformation logs for post-processing contribution
   - Verify metrics accuracy

5. **Phase 5: Detection Metrics** (1h)

   - Integrate metrics collection into detection stage
   - Calculate 5 detection metrics
   - Use transformation logs for modularity and coherence
   - Verify metrics accuracy

6. **Phase 6: API & Dashboard Integration** (1.5h)

   - Enhance quality_metrics.py API with new endpoints
   - Update quality_metrics_dashboard.html with visualizations
   - Add healthy range indicators
   - Test end-to-end

7. **Phase 7: Documentation & Healthy Ranges** (1h)
   - Create QUALITY-METRICS.md guide
   - Define healthy ranges for all metrics
   - Document interpretation guidelines
   - Add troubleshooting section

**Key Design Decisions**:

- **Centralized Service**: Single `QualityMetricsService` for all metric calculations (consistency)
- **Lazy Calculation**: Metrics calculated from logs/data (not stored redundantly during pipeline)
- **Two Collections**: `graphrag_runs` (per-run snapshot), `quality_metrics` (time-series)
- **Existing Infrastructure**: Leverage existing API and dashboard (no new UI framework)
- **Healthy Ranges**: Configurable ranges for alerting and visualization

**Key Considerations**:

- **Performance**: Metric calculation should not slow down pipeline execution
- **Accuracy**: Metrics must accurately reflect pipeline quality
- **Usability**: Dashboard must make metrics easy to understand
- **Actionability**: Metrics must guide specific improvements

---

## 🔄 Execution Strategy

**Execution Count**: Single

**Rationale**:

- Clear, sequential implementation across 4 stages
- All metrics follow same pattern (calculate, store, expose)
- No A/B testing or comparison needed
- Single execution with comprehensive verification

**EXECUTION_TASK**: `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-EXCELLENCE_04_01.md`

---

## 🧪 Tests Required

### Unit Tests

**Test File**: `tests/business/services/graphrag/test_quality_metrics.py`

**Test Cases**:

- Test metric calculation methods (each metric independently)
- Test MongoDB storage and retrieval
- Test healthy range checks
- Test edge cases (empty data, single entity, etc.)

### Integration Tests

**Test File**: `tests/business/stages/graphrag/test_metrics_integration.py`

**Test Cases**:

- Test metrics collection in each stage
- Test end-to-end pipeline with metrics
- Test API endpoints for metrics retrieval
- Test dashboard data loading

### Manual Testing

**Approach**: Run full pipeline and verify metrics

- Use real pipeline run data
- Verify metrics appear in dashboard
- Verify metrics are within expected ranges
- Test time-series queries

---

## 📊 Expected Results

### Deliverables Checklist

- [ ] `business/services/graphrag/quality_metrics.py` created (400-500 lines)
- [ ] Extraction metrics integrated into `extraction.py`
- [ ] Resolution metrics integrated into `entity_resolution.py`
- [ ] Construction metrics integrated into `graph_construction.py`
- [ ] Detection metrics integrated into `community_detection.py`
- [ ] API enhanced in `app/api/quality_metrics.py`
- [ ] Dashboard updated in `app/ui/quality_metrics_dashboard.html`
- [ ] Documentation created: `documentation/guides/QUALITY-METRICS.md`
- [ ] Healthy ranges defined
- [ ] Unit tests passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Manual testing complete with real data

### Success Metrics

**Functionality**:

- All 23 metrics (6+6+6+5) calculated correctly
- Metrics stored in MongoDB collections
- API returns metrics for any trace_id
- Dashboard displays metrics with visualizations

**Usability**:

- Metrics easy to understand (clear names, units)
- Healthy ranges clearly indicated
- Trends visible over time
- Alerts work for out-of-range metrics

**Performance**:

- Metric calculation adds <5% overhead to pipeline
- API responses <1 second
- Dashboard loads <2 seconds

**Value**:

- Metrics enable identification of quality issues
- Metrics guide specific improvements
- Metrics detect regressions

### Example Metrics Output

```json
{
  "trace_id": "abc123",
  "timestamp": "2025-11-09T23:00:00Z",
  "extraction": {
    "entity_count_avg": 12.5,
    "relationship_count_avg": 8.3,
    "predicate_diversity": 0.75,
    "type_coverage": 0.85,
    "confidence_avg": 0.82,
    "canonical_predicate_coverage": 0.9
  },
  "resolution": {
    "merge_rate": 0.25,
    "duplicate_reduction": 150,
    "confidence_preservation": 0.98,
    "cross_video_linking_rate": 0.15,
    "false_positive_estimate": 0.02,
    "false_negative_estimate": 0.05
  },
  "construction": {
    "graph_density": 0.18,
    "average_degree": 5.2,
    "degree_distribution_type": "power_law",
    "relationship_type_balance": {
      "llm": 0.6,
      "co_occurrence": 0.25,
      "semantic": 0.15
    },
    "post_processing_contribution": { "co_occurrence": 120, "semantic": 45 },
    "density_safeguard_triggers": 0
  },
  "detection": {
    "modularity": 0.42,
    "community_count": 25,
    "community_size_avg": 15.6,
    "coherence_avg": 0.75,
    "singleton_rate": 0.08,
    "coverage": 0.92
  }
}
```

---

## 🔗 Dependencies

**Required Before Starting**:

- ✅ Achievement 0.1: Transformation Logging (provides transformation_logs collection)
- ✅ Achievement 0.2: Intermediate Data Collections (provides intermediate data)
- ✅ Achievement 0.3: Query Scripts (provides query patterns)
- ✅ MongoDB accessible with existing collections
- ✅ Existing API and dashboard infrastructure

**Blocks**:

- Achievement 1.1: Explanation Tools (will use metrics to identify issues)
- Achievement 1.2: Visual Comparison Tools (will visualize metrics)
- All Priority 1+ work (depends on quality metrics)

---

## 📝 Implementation Notes

### Metric Calculation Patterns

**From Transformation Logs**:

```python
# Example: Calculate merge rate
raw_count = db["entities_raw"].count_documents({"trace_id": trace_id})
resolved_count = db["entities_resolved"].count_documents({"trace_id": trace_id})
merge_rate = (raw_count - resolved_count) / raw_count if raw_count > 0 else 0
```

**From Intermediate Data**:

```python
# Example: Calculate predicate diversity
relationships = db["relations_raw"].find({"trace_id": trace_id})
predicates = set(r["predicate"] for r in relationships)
total_rels = db["relations_raw"].count_documents({"trace_id": trace_id})
diversity = len(predicates) / total_rels if total_rels > 0 else 0
```

**From Graph Structure**:

```python
# Example: Calculate graph density
node_count = db["entities_resolved"].count_documents({"trace_id": trace_id})
edge_count = db["relations_final"].count_documents({"trace_id": trace_id})
max_edges = node_count * (node_count - 1)
density = edge_count / max_edges if max_edges > 0 else 0
```

### Healthy Ranges (Initial Estimates)

**Extraction**:

- Entity count per chunk: 8-15 (avg)
- Relationship count per chunk: 5-12 (avg)
- Predicate diversity: 0.6-0.9
- Type coverage: 0.7-1.0
- Confidence avg: 0.75-0.95
- Canonical predicate coverage: 0.8-1.0

**Resolution**:

- Merge rate: 0.15-0.35 (15-35% reduction)
- Confidence preservation: 0.95-1.0
- Cross-video linking rate: 0.10-0.30
- False positive estimate: 0.0-0.05
- False negative estimate: 0.0-0.10

**Construction**:

- Graph density: 0.15-0.25
- Average degree: 3-8
- Singleton rate (detection): 0.0-0.10
- Coverage: 0.85-1.0

**Detection**:

- Modularity: 0.3-0.7
- Coherence avg: 0.65-0.95

### MongoDB Collections

**`graphrag_runs` collection** (per-run metrics):

```python
{
  "_id": ObjectId,
  "trace_id": str,
  "timestamp": datetime,
  "metrics": {
    "extraction": {...},
    "resolution": {...},
    "construction": {...},
    "detection": {...}
  }
}
```

**`quality_metrics` collection** (time-series):

```python
{
  "_id": ObjectId,
  "trace_id": str,
  "timestamp": datetime,
  "stage": str,  # "extraction", "resolution", etc.
  "metric_name": str,
  "metric_value": float,
  "healthy_range": {"min": float, "max": float},
  "in_range": bool
}
```

---

## 🔄 Active EXECUTION_TASKs

| Execution | Status      | File                                                      | Time | Dependencies |
| --------- | ----------- | --------------------------------------------------------- | ---- | ------------ |
| 04_01     | ✅ Complete | EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-EXCELLENCE_04_01.md | 4h   | None         |

---

**Status**: ✅ Complete  
**Completion Date**: 2025-11-10 00:45 UTC  
**Actual Duration**: 4 hours (50% under estimate)  
**Success**: All 23 metrics implemented, documented, and integrated. Priority 0 (CRITICAL - Transformation Visibility Foundation) now complete.
