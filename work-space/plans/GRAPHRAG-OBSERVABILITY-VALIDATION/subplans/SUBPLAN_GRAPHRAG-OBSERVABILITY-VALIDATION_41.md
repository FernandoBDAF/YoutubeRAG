# SUBPLAN: Stage Compatibility Verified

**Type**: SUBPLAN  
**Mother Plan**: PLAN_GRAPHRAG-OBSERVABILITY-VALIDATION.md  
**Plan**: GRAPHRAG-OBSERVABILITY-VALIDATION  
**Achievement**: 4.1  
**Created**: 2025-11-13  
**Status**: 📋 Design Phase

---

## 🎯 Objective

Verify that all 4 GraphRAG pipeline stages (Extraction, Resolution, Construction, Detection) work correctly with the observability infrastructure, ensuring no breaking changes were introduced and that all integration points (TransformationLogger, IntermediateDataService, QualityMetricsService, trace_id propagation) function properly across each stage.

---

## 📦 Deliverables

### Required Deliverables

1. **Stage Compatibility Report** (`documentation/Stage-Compatibility-Report.md`)

   - Compatibility matrix for all 4 stages
   - Integration point verification results
   - Issues found and resolutions
   - Performance impact per stage
   - Test results summary

2. **Stage-Specific Test Results** (`documentation/Stage-Test-Results.md`)

   - Extraction stage test results
   - Resolution stage test results
   - Construction stage test results
   - Detection stage test results
   - Command outputs and logs

3. **Issue Fixes** (if needed)

   - Code fixes for any compatibility issues
   - Configuration adjustments
   - Documentation of changes

4. **Performance Impact Analysis** (`documentation/Stage-Performance-Impact.md`)
   - Baseline performance (without observability)
   - Performance with observability enabled
   - Memory usage comparison
   - Overhead percentage per stage
   - Recommendations for optimization

---

## 🎯 Approach

### 4-Phase Sequential Execution

**Phase 1: Baseline Establishment** (30-45 min)

- Run each stage individually WITHOUT observability
- Capture baseline performance metrics
- Document baseline memory usage
- Establish success criteria for each stage

**Phase 2: Stage-by-Stage Testing** (90-120 min)

- Test Extraction stage with observability
- Test Resolution stage with observability
- Test Construction stage with observability
- Test Detection stage with observability
- Verify integration points for each stage
- Document any issues encountered

**Phase 3: Integration Point Verification** (45-60 min)

- Verify TransformationLogger initialization in each stage
- Verify IntermediateDataService initialization in each stage
- Verify QualityMetricsService usage in each stage
- Verify trace_id propagation across all stages
- Check error handling and edge cases

**Phase 4: Performance Analysis & Documentation** (45-60 min)

- Compare baseline vs observability-enabled performance
- Calculate overhead percentage per stage
- Identify performance bottlenecks
- Document findings and recommendations
- Create all 4 deliverables

---

## 🔄 Execution Strategy

### Single Sequential Execution

**Why Single Execution**: All phases build on each other - baseline is needed before testing, testing is needed before analysis, and all results feed into the final documentation.

**Execution Flow**:

1. Phase 1: Establish baseline (required for comparison)
2. Phase 2: Test each stage (requires baseline data)
3. Phase 3: Verify integration points (requires stage tests)
4. Phase 4: Analyze and document (requires all previous data)

**Prerequisites**:

- Priority 3 complete (observability infrastructure validated)
- MongoDB accessible
- Test data available (from Achievement 2.1)
- GraphRAG pipeline executable

**Test Data**:

- Use same test data from Achievement 2.1 (50 chunks)
- Database: `validation_01` (or new `stage_test_01`)
- Experiment IDs: `test-extraction`, `test-resolution`, `test-construction`, `test-detection`

---

## 🧪 Tests

### Test 1: Extraction Stage Compatibility

**What**: Run extraction stage with observability enabled
**How**:

```bash
python business/pipelines/graphrag.py --stages extraction \
  --experiment-id test-extraction \
  --db-name stage_test_01
```

**Expected**:

- Stage completes successfully
- TransformationLogger captures extraction decisions
- IntermediateDataService saves entity_mentions
- No errors or exceptions
  **Pass Criteria**: Exit code 0, all integration points working

### Test 2: Resolution Stage Compatibility

**What**: Run resolution stage with observability enabled
**How**:

```bash
python business/pipelines/graphrag.py --stages resolution \
  --experiment-id test-resolution \
  --db-name stage_test_01 \
  --read-db-name stage_test_01
```

**Expected**:

- Stage completes successfully
- TransformationLogger captures resolution decisions
- IntermediateDataService saves entities_before_resolution, entities_after_resolution
- trace_id propagates from extraction
  **Pass Criteria**: Exit code 0, all integration points working, trace_id consistent

### Test 3: Construction Stage Compatibility

**What**: Run construction stage with observability enabled
**How**:

```bash
python business/pipelines/graphrag.py --stages construction \
  --experiment-id test-construction \
  --db-name stage_test_01 \
  --read-db-name stage_test_01
```

**Expected**:

- Stage completes successfully
- TransformationLogger captures construction decisions
- IntermediateDataService saves relations_before_filter, relations_final
- trace_id propagates from previous stages
  **Pass Criteria**: Exit code 0, all integration points working, trace_id consistent

### Test 4: Detection Stage Compatibility

**What**: Run detection stage with observability enabled
**How**:

```bash
python business/pipelines/graphrag.py --stages detection \
  --experiment-id test-detection \
  --db-name stage_test_01 \
  --read-db-name stage_test_01
```

**Expected**:

- Stage completes successfully
- TransformationLogger captures detection decisions
- trace_id propagates from previous stages
- Communities collection populated
  **Pass Criteria**: Exit code 0, all integration points working, trace_id consistent

### Test 5: TransformationLogger Integration

**What**: Verify TransformationLogger works in all stages
**How**: Query `transformation_logs` collection for each stage
**Expected**: Logs exist for all 4 stages with correct trace_id
**Pass Criteria**: transformation_logs count > 0 for each stage

### Test 6: IntermediateDataService Integration

**What**: Verify IntermediateDataService works in applicable stages
**How**: Query intermediate data collections
**Expected**:

- entity_mentions (extraction)
- entities_before_resolution, entities_after_resolution (resolution)
- relations_before_filter, relations_final (construction)
  **Pass Criteria**: All expected collections populated

### Test 7: QualityMetricsService Integration

**What**: Verify QualityMetricsService calculates metrics (if enabled)
**How**: Query `quality_metrics` collection
**Expected**: Metrics calculated for each stage (if GRAPHRAG_QUALITY_METRICS=true)
**Pass Criteria**: quality_metrics documents exist for each stage OR feature disabled

### Test 8: trace_id Propagation

**What**: Verify trace_id propagates correctly across all stages
**How**: Query all observability collections, check trace_id consistency
**Expected**: Same trace_id in all collections for a given pipeline run
**Pass Criteria**: 100% trace_id consistency across all collections

### Test 9: Memory Usage

**What**: Verify no memory leaks with observability enabled
**How**: Monitor memory usage during each stage execution
**Expected**: Memory usage remains stable, no unbounded growth
**Pass Criteria**: Memory usage < 2x baseline, no leaks detected

### Test 10: Performance Overhead

**What**: Measure performance impact of observability
**How**: Compare execution time with/without observability
**Expected**: Overhead < 20% per stage
**Pass Criteria**: Performance degradation acceptable (< 20%)

---

## 📊 Expected Results

### Stage Compatibility Matrix

| Stage        | TransformationLogger | IntermediateDataService             | QualityMetricsService | trace_id      | Status        |
| ------------ | -------------------- | ----------------------------------- | --------------------- | ------------- | ------------- |
| Extraction   | ✅ Working           | ✅ Working (entity_mentions)        | ✅ Working            | ✅ Propagates | ✅ Compatible |
| Resolution   | ✅ Working           | ✅ Working (entities before/after)  | ✅ Working            | ✅ Propagates | ✅ Compatible |
| Construction | ✅ Working           | ✅ Working (relations before/after) | ✅ Working            | ✅ Propagates | ✅ Compatible |
| Detection    | ✅ Working           | N/A (no intermediate data)          | ✅ Working            | ✅ Propagates | ✅ Compatible |

### Integration Points

**TransformationLogger**:

- Initialized in all 4 stages ✅
- Captures decisions correctly ✅
- Logs stored in `transformation_logs` collection ✅

**IntermediateDataService**:

- Initialized in Extraction, Resolution, Construction ✅
- Saves intermediate data to correct collections ✅
- Not used in Detection (expected) ✅

**QualityMetricsService**:

- Calculates metrics for all stages (if enabled) ✅
- Stores metrics in `quality_metrics` collection ✅
- Gracefully disabled if GRAPHRAG_QUALITY_METRICS=false ✅

**trace_id Propagation**:

- Generated in first stage (Extraction) ✅
- Propagates through all subsequent stages ✅
- Consistent across all observability collections ✅

### Performance Impact

**Expected Overhead** (based on observability features):

- Extraction: 10-15% (logging + intermediate data + metrics)
- Resolution: 10-15% (logging + intermediate data + metrics)
- Construction: 10-15% (logging + intermediate data + metrics)
- Detection: 5-10% (logging + metrics only)

**Memory Impact**:

- Baseline: ~500MB per stage
- With Observability: ~600-700MB per stage
- Increase: ~20-40% (acceptable for observability benefits)

### Known Issues from Previous Achievements

From Achievement 2.1, we know:

- **0% merge rate** in Resolution (no entities merged)
- **0 relationships** in Construction (all filtered out)
- **0 communities** in Detection (no graph structure)

These are **data quality issues**, not observability compatibility issues. The stages should still complete successfully with observability enabled.

---

## 🎓 Success Criteria

1. ✅ All 4 stages execute successfully with observability enabled
2. ✅ TransformationLogger works in all 4 stages
3. ✅ IntermediateDataService works in applicable stages (Extraction, Resolution, Construction)
4. ✅ QualityMetricsService works in all 4 stages (if enabled)
5. ✅ trace_id propagates correctly across all stages
6. ✅ No breaking changes or errors introduced
7. ✅ Performance overhead < 20% per stage
8. ✅ Memory usage acceptable (< 2x baseline)
9. ✅ All 10 tests passed
10. ✅ All 4 deliverables created

---

## ⏱️ Estimated Effort

**Total**: 3-4 hours

**Breakdown**:

- Phase 1: 30-45 min (baseline establishment)
- Phase 2: 90-120 min (stage-by-stage testing)
- Phase 3: 45-60 min (integration point verification)
- Phase 4: 45-60 min (performance analysis & documentation)

---

## 🔗 Dependencies

**Depends On**:

- Achievement 3.3 (Quality Metrics Validated) - **COMPLETE** ✅
- Priority 3 complete (observability infrastructure validated)
- Achievement 2.1 (Baseline Pipeline Run) - **COMPLETE** ✅
- Test data available (50 chunks from Achievement 2.1)

**Blocks**:

- Achievement 4.2 (Legacy Collection Coexistence Verified)
- Achievement 4.3 (Configuration Integration Validated)

---

## 📋 Notes

### Stage Execution Commands

**Extraction Only**:

```bash
python business/pipelines/graphrag.py \
  --stages extraction \
  --experiment-id test-extraction \
  --db-name stage_test_01
```

**Resolution Only** (requires extraction data):

```bash
python business/pipelines/graphrag.py \
  --stages resolution \
  --experiment-id test-resolution \
  --db-name stage_test_01 \
  --read-db-name stage_test_01
```

**Construction Only** (requires resolution data):

```bash
python business/pipelines/graphrag.py \
  --stages construction \
  --experiment-id test-construction \
  --db-name stage_test_01 \
  --read-db-name stage_test_01
```

**Detection Only** (requires construction data):

```bash
python business/pipelines/graphrag.py \
  --stages detection \
  --experiment-id test-detection \
  --db-name stage_test_01 \
  --read-db-name stage_test_01
```

### Database Strategy

**Option 1: Use validation_01** (existing data from Achievement 2.1)

- Pros: Data already exists, faster testing
- Cons: May have legacy data, harder to isolate stage-specific issues

**Option 2: Use new stage_test_01** (fresh database)

- Pros: Clean slate, easier to isolate issues
- Cons: Need to run extraction first to populate data

**Recommendation**: Use **stage_test_01** (new database) for clean testing.

### Observability Configuration

Ensure these environment variables are set:

```bash
GRAPHRAG_TRANSFORMATION_LOGGING=true
GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
GRAPHRAG_QUALITY_METRICS=true  # Optional, but recommended for full testing
```

### Integration Point Verification

For each stage, verify:

1. **Logger Initialization**: Check logs for "TransformationLogger initialized"
2. **Service Initialization**: Check logs for "IntermediateDataService initialized"
3. **Data Saved**: Query collections to verify data exists
4. **trace_id Present**: Check all documents have trace_id field
5. **No Errors**: Check logs for exceptions or warnings

### Performance Measurement

**Baseline (without observability)**:

```bash
# Disable observability
export GRAPHRAG_TRANSFORMATION_LOGGING=false
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
export GRAPHRAG_QUALITY_METRICS=false

# Run and time each stage
time python business/pipelines/graphrag.py --stages extraction ...
```

**With Observability**:

```bash
# Enable observability
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
export GRAPHRAG_QUALITY_METRICS=true

# Run and time each stage
time python business/pipelines/graphrag.py --stages extraction ...
```

**Calculate Overhead**:

```
Overhead % = ((Time_With_Obs - Time_Baseline) / Time_Baseline) * 100
```

### Memory Monitoring

Use `psutil` or system monitoring tools:

```bash
# Monitor memory during execution
watch -n 1 'ps aux | grep graphrag.py'
```

Or add memory profiling to the pipeline code temporarily.

---

## 🚨 Potential Issues

### Issue 1: Stage Dependencies

**Problem**: Later stages (Resolution, Construction, Detection) require data from earlier stages.
**Solution**: Run stages sequentially, ensuring each stage has required input data.

### Issue 2: Database Configuration

**Problem**: `--read-db-name` vs `--db-name` confusion.
**Solution**:

- `--db-name`: Where to WRITE output
- `--read-db-name`: Where to READ input (for stages after Extraction)

### Issue 3: trace_id Generation

**Problem**: trace_id might not propagate if stages run separately.
**Solution**: Check if trace_id is read from input data or generated fresh. May need to pass trace_id explicitly.

### Issue 4: Collection Name Conflicts

**Problem**: Observability collections might conflict with stage collections.
**Solution**: Already resolved in Achievement 0.1, but verify no regressions.

### Issue 5: Performance Overhead

**Problem**: Observability might slow down stages significantly.
**Solution**: Measure and document. If > 20%, identify bottlenecks and optimize.

---

## 🧪 Validation

### Automated Validation Script

**Script**: `observability/validate-achievement-41.sh`

**Tests** (30 total):

1. ✅ CLI Arguments Added to Pipeline (2 tests)
2. ✅ Pipeline Help Output Shows New Arguments (2 tests)
3. ✅ BaseStageConfig Has Required Fields (3 tests)
4. ✅ Stage Configs Inherit from BaseStageConfig (2 tests)
5. ✅ from_args_env Method Exists (2 tests)
6. ✅ TransformationLogger Integration (2 tests)
7. ✅ IntermediateDataService Integration (2 tests)
8. ✅ QualityMetricsService Integration (2 tests)
9. ✅ Deliverables Exist (4 tests)
10. ✅ Stage Compatibility Verified (4 tests)
11. ✅ Performance Impact Documented (2 tests)
12. ✅ EXECUTION_TASK Complete (3 tests)

**How to Run**:

```bash
# From project root
bash work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/validate-achievement-41.sh

# Expected output: 30/30 tests passed ✅
# Exit code: 0 (success)
```

**Validation Criteria**:

- All 4 CLI arguments present in pipeline code
- All 4 arguments appear in `--help` output
- BaseStageConfig has required fields (trace_id, read_db_name, write_db_name)
- All 4 stage configs exist and inherit from BaseStageConfig
- from_args_env method exists and is used
- All 3 observability services exist and are properly defined
- All 4 deliverables exist and have content
- All 4 stages documented as compatible
- Performance impact documented for all stages
- EXECUTION_TASK marked as complete with all deliverables

---

## 📚 Reference Documents

**From Parent PLAN** (PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md):

- Achievement 0.1: TransformationLogger implementation
- Achievement 0.2: IntermediateDataService implementation
- Achievement 0.3: QualityMetricsService implementation
- Achievement 0.4: Query scripts and tools

**From This PLAN**:

- Achievement 2.1: Baseline Pipeline Run (test data source)
- Achievement 3.1: Query Scripts Validated
- Achievement 3.2: Explanation Tools Validated
- Achievement 3.3: Quality Metrics Validated

**Configuration Files**:

- `core/config/paths.py`: Collection name definitions
- `core/config/graphrag.py`: Pipeline configuration
- `core/base/stage.py`: Stage base class
- `core/base/agent.py`: Agent base class

**Observability Services**:

- `business/services/graphrag/transformation_logger.py`
- `business/services/graphrag/intermediate_data_service.py`
- `business/services/graphrag/quality_metrics.py`

---

**SUBPLAN Status**: 📋 Ready for EXECUTION_TASK Creation  
**Next Step**: Create EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_41_01.md
