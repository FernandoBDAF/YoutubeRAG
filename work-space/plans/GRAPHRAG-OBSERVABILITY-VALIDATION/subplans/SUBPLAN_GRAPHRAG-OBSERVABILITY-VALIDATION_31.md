# SUBPLAN: Query Scripts Validated

**Type**: SUBPLAN  
**Mother Plan**: PLAN_GRAPHRAG-OBSERVABILITY-VALIDATION.md  
**Plan**: GRAPHRAG-OBSERVABILITY-VALIDATION  
**Achievement**: 3.1  
**Created**: 2025-11-13  
**Status**: 📋 DESIGN PHASE

---

## 📖 Achievement Context

**From Parent PLAN** (Achievement 3.1):

**Goal**: Test all 11 query scripts with real pipeline data from Achievement 2.2

**Why Critical**: Query scripts are essential tools for debugging and analyzing GraphRAG pipeline runs. They must work correctly with real observability data to be useful in production.

**Prerequisites**:

- ✅ Achievement 2.2 complete (observability data available)
- ✅ Trace ID available: `6088e6bd-e305-42d8-9210-e2d3f1dda035`
- ✅ All observability collections populated

---

## 🎯 Objective

Validate that all 11 query scripts in `scripts/repositories/graphrag/queries/` work correctly with real pipeline data from Achievement 2.2, producing accurate results and handling errors gracefully.

---

## 📦 Deliverables

### Required Deliverables

1. **Query-Scripts-Validation-Report.md** (documentation/)

   - Test results for all 11 scripts
   - Output format validation
   - Data accuracy verification
   - Error handling assessment

2. **Query-Scripts-Example-Outputs.md** (documentation/)

   - Example output from each script
   - Sample commands with real trace IDs
   - Expected vs. actual results

3. **Query-Scripts-Bug-Log.md** (documentation/) - if bugs found

   - Bug descriptions
   - Reproduction steps
   - Fixes applied (if any)

4. **Query-Scripts-Documentation-Updates.md** (documentation/)
   - Updated usage examples with real data
   - Performance notes
   - Best practices

### Optional Deliverables

5. Bug fixes for any scripts that don't work
6. Performance improvements if needed
7. Enhanced error messages

---

## 🎯 Approach

### 4-Phase Sequential Execution

#### Phase 1: Script Discovery & Preparation (30-45 min)

**Objective**: Locate all query scripts and prepare test environment

**Tasks**:

1. List all query scripts in `scripts/repositories/graphrag/queries/`
2. Verify scripts are executable
3. Extract trace ID from Achievement 2.2
4. Prepare test database connection
5. Document script inventory

**Success Criteria**:

- All 11 scripts located
- Trace ID confirmed: `6088e6bd-e305-42d8-9210-e2d3f1dda035`
- Database connection verified

---

#### Phase 2: Extraction & Resolution Script Testing (1-1.5 hours)

**Objective**: Test scripts for Stages 1-2 (Extraction, Resolution)

**Scripts to Test** (5 scripts):

1. `query_raw_entities.py`
2. `compare_extraction_runs.py`
3. `query_resolution_decisions.py`
4. `compare_before_after_resolution.py`
5. `find_resolution_errors.py`

**Test Procedure** (per script):

1. Run script with real trace ID
2. Verify output format (table/JSON/CSV)
3. Check data accuracy against MongoDB
4. Test filtering options (if any)
5. Test error handling (invalid trace ID, missing data)
6. Capture example output
7. Document findings

**Success Criteria**:

- All 5 scripts execute without errors
- Output format correct
- Data matches MongoDB
- Error handling works

---

#### Phase 3: Construction & Detection Script Testing (1-1.5 hours)

**Objective**: Test scripts for Stages 3-4 (Construction, Detection)

**Scripts to Test** (6 scripts):

1. `query_raw_relationships.py`
2. `compare_before_after_construction.py`
3. `query_graph_evolution.py`
4. `query_pre_detection_graph.py`
5. `compare_detection_algorithms.py`
6. Any additional utility scripts

**Test Procedure**: Same as Phase 2

**Success Criteria**:

- All 6 scripts execute without errors
- Output format correct
- Data matches MongoDB
- Error handling works

---

#### Phase 4: Documentation & Bug Fixes (30-45 min)

**Objective**: Document findings and fix any bugs found

**Tasks**:

1. Create validation report
2. Compile example outputs
3. Document bugs (if any)
4. Fix critical bugs (if time permits)
5. Update script documentation with real examples

**Success Criteria**:

- All 4 required deliverables created
- Bugs documented (and fixed if possible)
- Documentation updated

---

## 🧪 Tests

### Critical Tests (Must Pass)

1. **Test 1**: All 11 scripts located and executable
2. **Test 2**: Scripts accept trace ID parameter
3. **Test 3**: Scripts connect to MongoDB successfully
4. **Test 4**: Scripts return data for valid trace ID
5. **Test 5**: Scripts handle invalid trace ID gracefully
6. **Test 6**: Output format matches specification (table/JSON/CSV)
7. **Test 7**: Data accuracy verified against MongoDB
8. **Test 8**: Filtering options work (if applicable)

### Important Tests (Should Pass)

9. **Test 9**: Scripts complete in reasonable time (< 30s each)
10. **Test 10**: Error messages are helpful
11. **Test 11**: Scripts work with empty collections

---

## 📊 Expected Results

### Script Inventory (Expected 11 scripts)

**Extraction Scripts** (2):

- `query_raw_entities.py`
- `compare_extraction_runs.py`

**Resolution Scripts** (3):

- `query_resolution_decisions.py`
- `compare_before_after_resolution.py`
- `find_resolution_errors.py`

**Construction Scripts** (3):

- `query_raw_relationships.py`
- `compare_before_after_construction.py`
- `query_graph_evolution.py`

**Detection Scripts** (2):

- `query_pre_detection_graph.py`
- `compare_detection_algorithms.py`

**Utility Scripts** (1+):

- Any additional helper scripts

### Expected Data Availability

Based on Achievement 2.2 results:

| Collection            | Documents | Available for Queries   |
| --------------------- | --------- | ----------------------- |
| `transformation_logs` | 573       | ✅ Yes                  |
| `entities_raw`        | 373       | ✅ Yes                  |
| `entities_resolved`   | 373       | ✅ Yes                  |
| `relations_raw`       | 68        | ✅ Yes                  |
| `relations_final`     | 0         | ⚠️ Empty                |
| `graph_pre_detection` | Unknown   | ✅ Likely               |
| `quality_metrics`     | 24        | ✅ Yes                  |
| `graphrag_runs`       | 1         | ⚠️ Incomplete (Bug #10) |

**Note**: Scripts querying `relations_final` may return empty results (expected).

---

## 🎯 Success Criteria

### Must Have (All Required)

1. ✅ All 11 query scripts tested
2. ✅ All scripts execute without crashes
3. ✅ Output format validated for each script
4. ✅ Data accuracy verified for each script
5. ✅ Error handling tested for each script
6. ✅ All 4 required deliverables created

### Should Have

7. ✅ All bugs documented
8. ✅ Critical bugs fixed
9. ✅ Performance acceptable (< 30s per script)
10. ✅ Documentation updated with real examples

### Nice to Have

11. ✅ Performance improvements implemented
12. ✅ Enhanced error messages
13. ✅ Additional test cases

---

## ⚠️ Risks & Mitigation

### Risk 1: Scripts Don't Exist

**Likelihood**: Medium  
**Impact**: High  
**Mitigation**:

- Check if scripts are in different location
- Check if scripts were renamed
- Document missing scripts
- Create placeholder scripts if needed

### Risk 2: Scripts Use Old Collection Names

**Likelihood**: Medium  
**Impact**: Medium  
**Mitigation**:

- Update scripts to use new collection names
- Test with both old and new names
- Document required changes

### Risk 3: Scripts Fail with Empty Collections

**Likelihood**: High (for `relations_final`)  
**Impact**: Low  
**Mitigation**:

- Test with empty collections
- Verify graceful handling
- Document expected behavior

### Risk 4: Scripts Have Dependencies

**Likelihood**: Medium  
**Impact**: Medium  
**Mitigation**:

- Check for missing dependencies
- Install required packages
- Document dependencies

---

## 📋 Execution Strategy

### Single Sequential Execution

**Rationale**: All phases build on each other and require the same environment

**Execution Plan**:

1. Create single EXECUTION_TASK file
2. Executor runs all 4 phases sequentially
3. Document progress in iteration log
4. Create all deliverables at end

**Estimated Timeline**: 3-4 hours total

---

## 🔗 Dependencies

### Prerequisites (Must Be Complete)

- ✅ Achievement 2.2: Observability Pipeline Run Executed
  - Provides real data for testing
  - Provides trace ID: `6088e6bd-e305-42d8-9210-e2d3f1dda035`

### Blocks (What This Unblocks)

- Achievement 3.2: Explanation Tools Validated
- Achievement 3.3: Quality Metrics Validated
- Achievement 6.1: Real-World Examples Documented

---

## 📊 Effort Estimate

**Total Estimated Time**: 3-4 hours

**Breakdown**:

- Phase 1 (Discovery): 0.5-0.75 hours
- Phase 2 (Extraction/Resolution): 1-1.5 hours
- Phase 3 (Construction/Detection): 1-1.5 hours
- Phase 4 (Documentation): 0.5-0.75 hours

**Complexity**: Medium

- Scripts should be straightforward to test
- Real data available from Achievement 2.2
- May need bug fixes if scripts don't work

---

## 📝 Notes

### Important Considerations

1. **Trace ID**: Use `6088e6bd-e305-42d8-9210-e2d3f1dda035` from Achievement 2.2
2. **Database**: Use `validation_01` database
3. **Empty Collections**: `relations_final` is empty (all relationships filtered)
4. **Bug #10**: `graphrag_runs` metadata incomplete (may affect some scripts)

### Testing Strategy

1. **Happy Path**: Test with valid trace ID and populated collections
2. **Error Path**: Test with invalid trace ID, empty collections
3. **Edge Cases**: Test with missing data, malformed data

### Documentation Strategy

1. **Capture Everything**: Screenshot/copy all outputs
2. **Real Examples**: Use actual data from Achievement 2.2
3. **Be Specific**: Include exact commands, trace IDs, results

---

## ✅ Definition of Done

This SUBPLAN is complete when:

1. ✅ All 4 phases defined with clear objectives
2. ✅ All 11 tests specified
3. ✅ Expected results documented
4. ✅ Success criteria defined (6 must-have, 4 should-have, 3 nice-to-have)
5. ✅ Risks identified and mitigated
6. ✅ Execution strategy documented
7. ✅ EXECUTION_TASK created

This achievement is complete when:

1. ✅ All 11 query scripts tested
2. ✅ All 4 required deliverables created
3. ✅ All must-have success criteria met
4. ✅ EXECUTION_TASK marked complete
5. ✅ APPROVED_31.md created (after review)

---

**SUBPLAN Status**: ✅ DESIGN COMPLETE  
**Next Step**: Create EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_31_01.md  
**Then**: Executor runs EXECUTION_TASK to perform actual validation work
