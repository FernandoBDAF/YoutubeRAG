# Validation Scripts Master Plan

**Date**: 2025-11-13  
**Purpose**: Define validation script requirements for all achievements in PLAN_GRAPHRAG-OBSERVABILITY-VALIDATION.md  
**Status**: 🚀 Implementation Guide

---

## 📋 Overview

Every achievement in the GraphRAG Observability Validation plan requires an automated validation script that:

- Tests all success criteria
- Outputs clear terminal results
- Returns proper exit codes
- Can run independently

---

## 🧪 Validation Scripts by Achievement

### Priority 0: Critical Foundation

#### Achievement 0.1: Collection Name Compatibility Resolved

- **Script**: `observability/validate-achievement-01.sh`
- **Tests**:
  - Verify `core/config/paths.py` has correct collection constants
  - Check for naming conflicts between legacy and new collections
  - Validate collection name documentation
- **Expected Output**:

  ```
  ═══ ACHIEVEMENT 0.1 VALIDATION ═══
  ✅ PASS: Collection constants defined in paths.py
  ✅ PASS: No naming conflicts detected
  ✅ PASS: Documentation complete

  SUMMARY: 3/3 tests passed ✅
  ACHIEVEMENT 0.1: VALIDATED
  ```

#### Achievement 0.2: Configuration Compatibility Verified

- **Script**: `observability/validate-achievement-02.sh`
- **Tests**:
  - Verify config files (`graphrag.py`, `stage.py`, `agent.py`) have trace_id support
  - Check BaseStageConfig and BaseAgentConfig compatibility
  - Validate configuration flow documentation
- **Expected Output**:

  ```
  ═══ ACHIEVEMENT 0.2 VALIDATION ═══
  ✅ PASS: trace_id support in all config files
  ✅ PASS: BaseStageConfig compatible
  ✅ PASS: BaseAgentConfig compatible
  ✅ PASS: Configuration documentation complete

  SUMMARY: 4/4 tests passed ✅
  ACHIEVEMENT 0.2: VALIDATED
  ```

#### Achievement 0.3: Environment Variables Configured

- **Script**: `observability/validate-achievement-03.sh`
- **Tests**:
  - Check all required environment variables are set
  - Verify `.env.observability` template exists
  - Validate variable documentation
- **Expected Output**:

  ```
  ═══ ACHIEVEMENT 0.3 VALIDATION ═══
  ✅ PASS: GRAPHRAG_TRANSFORMATION_LOGGING set
  ✅ PASS: GRAPHRAG_SAVE_INTERMEDIATE_DATA set
  ✅ PASS: GRAPHRAG_QUALITY_METRICS set
  ✅ PASS: .env.observability template exists
  ✅ PASS: Documentation complete

  SUMMARY: 5/5 tests passed ✅
  ACHIEVEMENT 0.3: VALIDATED
  ```

---

### Priority 1: Observability Stack

#### Achievement 1.1: Observability Stack Running

- **Script**: `observability/validate-achievement-11.sh`
- **Tests**:
  - Check Docker containers running (Prometheus, Grafana, Loki, Promtail)
  - Verify service endpoints accessible
  - Test connectivity between services
- **Expected Output**:

  ```
  ═══ ACHIEVEMENT 1.1 VALIDATION ═══
  ✅ PASS: Prometheus container running
  ✅ PASS: Grafana container running
  ✅ PASS: Loki container running
  ✅ PASS: Promtail container running
  ✅ PASS: All endpoints accessible

  SUMMARY: 5/5 tests passed ✅
  ACHIEVEMENT 1.1: VALIDATED
  ```

#### Achievement 1.2: Metrics Endpoint Validated

- **Script**: `observability/validate-achievement-12.sh`
- **Tests**:
  - Verify metrics endpoint (http://localhost:9091/metrics) accessible
  - Check Prometheus format compliance
  - Verify Prometheus scraping working
- **Expected Output**:

  ```
  ═══ ACHIEVEMENT 1.2 VALIDATION ═══
  ✅ PASS: Metrics endpoint accessible
  ✅ PASS: Prometheus format valid
  ✅ PASS: Prometheus scraping metrics

  SUMMARY: 3/3 tests passed ✅
  ACHIEVEMENT 1.2: VALIDATED
  ```

#### Achievement 1.3: Grafana Dashboards Configured

- **Script**: `observability/test-achievement-1.3-dashboards.sh` ✅ **EXISTS**
- **Tests**: 16 automated tests (already implemented)
- **Status**: ✅ Complete

---

### Priority 2: Pipeline Validation

#### Achievement 2.1: Baseline Pipeline Run Executed

- **Script**: `observability/test-achievement-2.1-baseline.sh` ✅ **EXISTS**
- **Tests**: 16 automated tests (already implemented)
- **Status**: ✅ Complete

#### Achievement 2.2: Observability Pipeline Run Executed

- **Script**: `observability/test-achievement-2.2-observability.sh` ✅ **EXISTS**
- **Tests**: 28 automated tests (already implemented)
- **Status**: ✅ Complete

#### Achievement 2.3: Data Quality Validation

- **Script**: `observability/validate-achievement-23.sh`
- **Tests**:
  - Verify all observability collections exist
  - Check document counts are reasonable
  - Validate trace_id consistency
  - Verify schema correctness
- **Expected Output**:

  ```
  ═══ ACHIEVEMENT 2.3 VALIDATION ═══
  ✅ PASS: All 6 observability collections exist
  ✅ PASS: Document counts > 0
  ✅ PASS: Single trace_id across collections
  ✅ PASS: Schema validation passed

  SUMMARY: 4/4 tests passed ✅
  ACHIEVEMENT 2.3: VALIDATED
  ```

---

### Priority 3: Tool Validation

#### Achievement 3.1: Query Scripts Validated

- **Script**: `observability/test-all-query-scripts.sh` ✅ **EXISTS**
- **Tests**: 11 query scripts (already implemented)
- **Status**: ✅ Complete

#### Achievement 3.2: Explanation Tools Validated

- **Script**: `observability/test-all-explanation-tools.sh` ✅ **EXISTS**
- **Tests**: 5 explanation tools (already implemented)
- **Status**: ✅ Complete

#### Achievement 3.3: Quality Metrics Validated

- **Script**: `observability/test-achievement-3.3-quality-metrics.sh` ✅ **EXISTS**
- **Tests**: 23 automated tests (already implemented)
- **Status**: ✅ Complete

---

### Priority 4: Compatibility Verification

#### Achievement 4.1: Stage Compatibility Verified

- **Script**: `observability/validate-achievement-41.sh`
- **Tests**:
  - Run each stage (Extraction, Resolution, Construction, Detection) with observability
  - Verify TransformationLogger works in all stages
  - Verify IntermediateDataService works in applicable stages
  - Verify trace_id propagation
  - Measure performance overhead
- **Expected Output**:

  ```
  ═══ ACHIEVEMENT 4.1 VALIDATION ═══
  ✅ PASS: Extraction stage compatible
  ✅ PASS: Resolution stage compatible
  ✅ PASS: Construction stage compatible
  ✅ PASS: Detection stage compatible
  ✅ PASS: TransformationLogger works (4/4 stages)
  ✅ PASS: IntermediateDataService works (3/3 stages)
  ✅ PASS: trace_id propagates correctly
  ✅ PASS: Performance overhead < 20%

  SUMMARY: 8/8 tests passed ✅
  ACHIEVEMENT 4.1: VALIDATED
  ```

#### Achievement 4.2: Legacy Collection Coexistence Verified

- **Script**: `observability/validate-achievement-42.sh`
- **Tests**:
  - Verify legacy collections still exist and accessible
  - Test legacy queries still work
  - Verify new collections don't conflict with legacy
  - Check data separation
- **Expected Output**:

  ```
  ═══ ACHIEVEMENT 4.2 VALIDATION ═══
  ✅ PASS: Legacy collections exist
  ✅ PASS: Legacy queries work
  ✅ PASS: No naming conflicts
  ✅ PASS: Data properly separated

  SUMMARY: 4/4 tests passed ✅
  ACHIEVEMENT 4.2: VALIDATED
  ```

#### Achievement 4.3: Configuration Integration Validated

- **Script**: `observability/validate-achievement-43.sh`
- **Tests**:
  - Test all observability enabled
  - Test selective features (logging only, metrics only)
  - Test all observability disabled
  - Verify no breaking changes
- **Expected Output**:

  ```
  ═══ ACHIEVEMENT 4.3 VALIDATION ═══
  ✅ PASS: All features enabled works
  ✅ PASS: Logging only works
  ✅ PASS: Metrics only works
  ✅ PASS: All disabled works
  ✅ PASS: No breaking changes

  SUMMARY: 5/5 tests passed ✅
  ACHIEVEMENT 4.3: VALIDATED
  ```

---

### Priority 5: Performance Analysis

#### Achievement 5.1: Performance Impact Measured

- **Script**: `observability/validate-achievement-51.sh`
- **Tests**:
  - Compare baseline vs observability runtime
  - Calculate overhead percentage
  - Verify overhead < 30%
  - Check performance documentation
- **Expected Output**:

  ```
  ═══ ACHIEVEMENT 5.1 VALIDATION ═══
  ✅ PASS: Baseline metrics captured
  ✅ PASS: Observability metrics captured
  ✅ PASS: Overhead calculated: 15%
  ✅ PASS: Overhead < 30% threshold
  ✅ PASS: Documentation complete

  SUMMARY: 5/5 tests passed ✅
  ACHIEVEMENT 5.1: VALIDATED
  ```

#### Achievement 5.2: Storage Growth Analyzed

- **Script**: `observability/validate-achievement-52.sh`
- **Tests**:
  - Measure storage used by observability collections
  - Verify TTL mechanism working
  - Check storage < 500 MB threshold
  - Validate storage documentation
- **Expected Output**:

  ```
  ═══ ACHIEVEMENT 5.2 VALIDATION ═══
  ✅ PASS: Storage measured: 350 MB
  ✅ PASS: TTL indexes created
  ✅ PASS: TTL mechanism working
  ✅ PASS: Storage < 500 MB threshold
  ✅ PASS: Documentation complete

  SUMMARY: 5/5 tests passed ✅
  ACHIEVEMENT 5.2: VALIDATED
  ```

#### Achievement 5.3: Observability Overhead Assessment

- **Script**: `observability/validate-achievement-53.sh`
- **Tests**:
  - Verify cost-benefit analysis document exists
  - Check production recommendations documented
  - Validate overhead assessment complete
- **Expected Output**:

  ```
  ═══ ACHIEVEMENT 5.3 VALIDATION ═══
  ✅ PASS: Cost-benefit analysis exists
  ✅ PASS: Production recommendations documented
  ✅ PASS: Overhead assessment complete

  SUMMARY: 3/3 tests passed ✅
  ACHIEVEMENT 5.3: VALIDATED
  ```

---

### Priority 6: Documentation

#### Achievement 6.1: Real-World Examples Documented

- **Script**: `observability/validate-achievement-61.sh`
- **Tests**:
  - Verify all 5 guides have real examples
  - Check example outputs exist
  - Validate documentation completeness
- **Expected Output**:

  ```
  ═══ ACHIEVEMENT 6.1 VALIDATION ═══
  ✅ PASS: All guides updated with real examples
  ✅ PASS: Example outputs captured
  ✅ PASS: Documentation complete

  SUMMARY: 3/3 tests passed ✅
  ACHIEVEMENT 6.1: VALIDATED
  ```

#### Achievement 6.2: Validation Case Study Created

- **Script**: `observability/validate-achievement-62.sh`
- **Tests**:
  - Verify case study document exists
  - Check validation workflow documented
  - Validate completeness
- **Expected Output**:

  ```
  ═══ ACHIEVEMENT 6.2 VALIDATION ═══
  ✅ PASS: Case study document exists
  ✅ PASS: Validation workflow documented
  ✅ PASS: Document complete

  SUMMARY: 3/3 tests passed ✅
  ACHIEVEMENT 6.2: VALIDATED
  ```

#### Achievement 6.3: Lessons Learned Documented

- **Script**: `observability/validate-achievement-63.sh`
- **Tests**:
  - Verify lessons learned document exists
  - Check best practices guide exists
  - Validate completeness
- **Expected Output**:

  ```
  ═══ ACHIEVEMENT 6.3 VALIDATION ═══
  ✅ PASS: Lessons learned document exists
  ✅ PASS: Best practices guide exists
  ✅ PASS: Document complete

  SUMMARY: 3/3 tests passed ✅
  ACHIEVEMENT 6.3: VALIDATED
  ```

---

### Priority 7: Production Readiness

#### Achievement 7.1: Tool Enhancements Implemented

- **Script**: `observability/validate-achievement-71.sh`
- **Tests**:
  - Verify tool enhancements implemented
  - Check updated documentation
  - Test enhanced tools work
- **Expected Output**:

  ```
  ═══ ACHIEVEMENT 7.1 VALIDATION ═══
  ✅ PASS: Tool enhancements implemented
  ✅ PASS: Documentation updated
  ✅ PASS: Enhanced tools tested

  SUMMARY: 3/3 tests passed ✅
  ACHIEVEMENT 7.1: VALIDATED
  ```

#### Achievement 7.2: Performance Optimizations Applied

- **Script**: `observability/validate-achievement-72.sh`
- **Tests**:
  - Verify optimizations implemented
  - Compare performance before/after
  - Check optimization documentation
- **Expected Output**:

  ```
  ═══ ACHIEVEMENT 7.2 VALIDATION ═══
  ✅ PASS: Optimizations implemented
  ✅ PASS: Performance improved
  ✅ PASS: Documentation complete

  SUMMARY: 3/3 tests passed ✅
  ACHIEVEMENT 7.2: VALIDATED
  ```

#### Achievement 7.3: Production Readiness Checklist

- **Script**: `observability/validate-achievement-73.sh`
- **Tests**:
  - Verify production readiness checklist exists
  - Check deployment guide exists
  - Validate rollback procedures documented
- **Expected Output**:

  ```
  ═══ ACHIEVEMENT 7.3 VALIDATION ═══
  ✅ PASS: Production readiness checklist exists
  ✅ PASS: Deployment guide exists
  ✅ PASS: Rollback procedures documented

  SUMMARY: 3/3 tests passed ✅
  ACHIEVEMENT 7.3: VALIDATED
  ```

---

## 📊 Implementation Status

| Priority  | Achievements | Scripts Needed | Scripts Exist     | Status           |
| --------- | ------------ | -------------- | ----------------- | ---------------- |
| 0         | 3            | 3              | 0                 | 🔴 Pending       |
| 1         | 3            | 3              | 1 (1.3)           | 🟡 Partial       |
| 2         | 3            | 3              | 2 (2.1, 2.2)      | 🟡 Partial       |
| 3         | 3            | 3              | 3 (3.1, 3.2, 3.3) | 🟢 Complete      |
| 4         | 3            | 3              | 0                 | 🔴 Pending       |
| 5         | 3            | 3              | 0                 | 🔴 Pending       |
| 6         | 3            | 3              | 0                 | 🔴 Pending       |
| 7         | 3            | 3              | 0                 | 🔴 Pending       |
| **Total** | **24**       | **24**         | **7**             | **29% Complete** |

---

## 🚀 Next Steps

### Immediate (Create Missing Scripts)

1. **Priority 0** (Foundation):

   - `validate-achievement-01.sh`
   - `validate-achievement-02.sh`
   - `validate-achievement-03.sh`

2. **Priority 1** (Observability Stack):

   - `validate-achievement-11.sh`
   - `validate-achievement-12.sh`
   - ✅ `test-achievement-1.3-dashboards.sh` (exists)

3. **Priority 2** (Pipeline):

   - ✅ `test-achievement-2.1-baseline.sh` (exists)
   - ✅ `test-achievement-2.2-observability.sh` (exists)
   - `validate-achievement-23.sh`

4. **Priority 3** (Tools):

   - ✅ All scripts exist

5. **Priority 4-7** (Compatibility, Performance, Documentation, Production):
   - Create 12 remaining validation scripts

### Long-term (Master Script)

- Update `validate-all-achievements.sh` to run all 24 scripts
- Create CI/CD integration guide
- Document validation workflow

---

## 📝 Notes

- **Existing Scripts**: 7 scripts already created during Achievements 1.3, 2.1, 2.2, 3.1, 3.2, 3.3
- **Naming Convention**: New scripts use `validate-achievement-XX.sh`, existing use `test-achievement-XX.sh`
- **Location**: All scripts in `observability/` directory
- **Exit Codes**: 0 = success, 1 = failure, 2 = setup error

---

**Status**: 🚀 Ready for Implementation  
**Completion**: 29% (7/24 scripts exist)  
**Next Action**: Create remaining 17 validation scripts
