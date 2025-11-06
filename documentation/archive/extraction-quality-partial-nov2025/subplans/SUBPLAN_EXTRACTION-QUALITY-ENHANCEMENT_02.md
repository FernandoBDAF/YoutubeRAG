# SUBPLAN: Quality Comparison Tools

**Mother Plan**: PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md  
**Achievement Addressed**: Achievement 1.1 (Quality Comparison Tools Exist)  
**Status**: ✅ COMPLETE  
**Created**: 2025-11-06 00:00 UTC  
**Completed**: 2025-11-06 00:30 UTC  
**Actual Effort**: ~4 hours

---

## 🎯 Objective

Create comprehensive quality comparison tools that enable quantitative analysis of extraction quality improvements. These tools will compare old (pre-ontology) extraction data from `validation_db` with new (ontology-based) extraction data from `mongo_hack`, generating metrics, reports, and recommendations that prove the value of the ontology integration. This implements Achievement 1.1 and provides the foundation for all subsequent quality validation work.

---

## 📋 What Needs to Be Created

### Files to Create

1. **`scripts/compare_extraction_quality.py`**

   - Main comparison script comparing two databases
   - Calculates quality metrics (predicate quality, entity quality, relationship quality, coverage)
   - Generates markdown reports and JSON metrics
   - Command-line interface for database selection

2. **`scripts/compare_old_vs_new_extraction.py`**
   - Convenience wrapper for comparing `validation_db` (old) vs `mongo_hack` (new)
   - Side-by-side comparison with visual diffs
   - Highlights improvements and regressions
   - Generates executive summary report

### Functions/Classes to Add

**In `scripts/compare_extraction_quality.py`**:

- `ExtractionQualityComparator` class:
  - `__init__(old_db, new_db, old_coll, new_coll)`
  - `load_extraction_data()` - Query and load extraction data from both databases
  - `calculate_predicate_quality()` - Compare predicate canonicalization rates
  - `calculate_entity_quality()` - Compare entity extraction quality
  - `calculate_relationship_quality()` - Compare relationship extraction quality
  - `calculate_coverage_metrics()` - Compare coverage metrics
  - `generate_report()` - Create markdown report
  - `export_metrics()` - Export JSON metrics

**In `scripts/compare_old_vs_new_extraction.py`**:

- `main()` - Entry point that calls comparator with defaults
- Side-by-side comparison logic
- Visual diff generation

### Tests Required

- **Test File**: `tests/scripts/test_compare_extraction_quality.py`
- **Test Cases**:
  1. Test data loading from both databases
  2. Test predicate quality calculation (canonical ratio comparison)
  3. Test entity quality calculation (type distribution, confidence)
  4. Test relationship quality calculation (constraint validation, confidence)
  5. Test coverage metrics (predicate coverage, entity coverage)
  6. Test report generation (markdown format, completeness)
  7. Test JSON metrics export (valid JSON, all metrics present)
  8. Test edge cases (empty databases, missing fields, no common chunks)

---

## 📝 Approach

**Strategy**: Build a reusable comparison framework that can compare any two extraction databases, with specific convenience wrapper for the old vs new comparison.

**Method**:

1. **Design Phase**: Define metric calculations based on PLAN requirements

   - Predicate quality: Canonical ratio, mapping effectiveness, coverage
   - Entity quality: Type distribution, confidence scores, OTHER category usage
   - Relationship quality: Constraint validation, confidence scores, predicate diversity
   - Coverage: Semantic coverage, ontology usage, missing elements

2. **Implementation Phase**:

   - Create `ExtractionQualityComparator` class with database connection
   - Implement data loading with MongoDB queries
   - Implement metric calculations for each quality dimension
   - Implement report generation (markdown + JSON)
   - Create convenience wrapper script

3. **Testing Phase**:
   - Write tests before implementation (TDD)
   - Test with mock data
   - Validate against real databases
   - Verify report quality

**Key Considerations**:

- Must handle chunks that exist in one database but not the other
- Must normalize metrics for fair comparison (e.g., per-chunk averages)
- Must provide actionable recommendations, not just metrics
- Must handle missing fields gracefully (old data may lack ontology fields)
- Should be efficient for large databases (use aggregation pipelines where possible)

---

## 🧪 Tests Required

### Test File

- `tests/scripts/test_compare_extraction_quality.py`

### Test Cases to Cover

1. **Data Loading**: Test loading from both databases, handling missing chunks
2. **Predicate Quality**: Test canonical ratio calculation, mapping effectiveness
3. **Entity Quality**: Test type distribution, confidence analysis, OTHER usage
4. **Relationship Quality**: Test constraint validation rate, confidence scores
5. **Coverage Metrics**: Test predicate coverage, entity type coverage
6. **Report Generation**: Test markdown format, completeness, recommendations
7. **JSON Export**: Test valid JSON structure, all metrics present
8. **Edge Cases**: Empty databases, missing fields, no common chunks, malformed data

### Test-First Requirement

- [ ] Tests written before implementation
- [ ] Initial test run shows all failing
- [ ] Tests define success criteria

---

## ✅ Expected Results

### Functional Changes

- New scripts in `scripts/` directory for quality comparison
- Ability to compare extraction quality between any two databases
- Quantitative metrics proving ontology impact
- Actionable recommendations for improvement

### Observable Outcomes

- Can run: `python scripts/compare_old_vs_new_extraction.py`
- Generates: `reports/extraction_quality_comparison_YYYYMMDD_HHMMSS.md`
- Generates: `reports/extraction_quality_metrics_YYYYMMDD_HHMMSS.json`
- Shows: Canonical predicate ratio improvement (e.g., 70% → 85%)
- Shows: Entity type distribution improvements
- Shows: Relationship quality improvements
- Shows: Coverage gaps and recommendations

---

## 🔍 Conflict Analysis with Other Subplans

**Review Existing Subplans**:

- SUBPLAN_01: Achievement 0.1 (Extraction Stage Validation) - ✅ COMPLETE

**Check for**:

- **Overlap**: No - SUBPLAN_01 was validation, this is quality analysis
- **Conflicts**: No conflicts detected
- **Dependencies**: Depends on SUBPLAN_01 being complete (✅ done) - need working extraction to compare
- **Integration**: This provides data for SUBPLAN_03 (Predicate Distribution) and SUBPLAN_04 (Entity Type Distribution)

**Analysis**:

- No conflicts detected
- Safe to proceed independently
- Results will inform SUBPLAN_03 and SUBPLAN_04

**Result**: Safe to proceed

---

## 🔗 Dependencies

### Other Subplans

- SUBPLAN_01 (Achievement 0.1) - ✅ COMPLETE - Need working extraction to compare

### External Dependencies

- `pymongo` - MongoDB connection (already in project)
- `pandas` - Data analysis (may need to add if not present)
- `json` - JSON export (standard library)
- `datetime` - Timestamp generation (standard library)

### Prerequisite Knowledge

- MongoDB query syntax for extraction data
- GraphRAG extraction data structure (`graphrag_extraction` field)
- Ontology structure (canonical predicates, mappings, type constraints)
- Quality metrics definitions from PLAN

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

_None yet - will be created when execution starts_

**First Execution**: `EXECUTION_TASK_EXTRACTION-QUALITY-ENHANCEMENT_02_01.md`

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [x] `scripts/compare_extraction_quality.py` created and functional
- [x] `scripts/compare_old_vs_new_extraction.py` created and functional
- [x] All tests passing
- [x] Can successfully compare `validation_db` vs `mongo_hack`
- [x] Reports generated with actionable metrics and recommendations
- [x] Code commented with learnings
- [x] EXECUTION_TASK complete
- [x] Real database testing completed and validated
- [ ] Ready for archive (pending PLAN update - now complete)

---

## 📝 Notes

**Common Pitfalls**:

- Don't assume all chunks exist in both databases
- Don't assume old data has same structure as new data
- Handle missing ontology fields in old data gracefully
- Use efficient MongoDB aggregation pipelines for large datasets

**Resources**:

- `PLAN-ONTOLOGY-AND-EXTRACTION.md` - Context on ontology integration
- `scripts/compare_graphrag_experiments.py` - Reference for comparison script pattern
- `business/stages/graphrag/extraction.py` - Understanding extraction data structure
- `core/models/graphrag.py` - KnowledgeModel structure

---

**Ready to Execute**: Create EXECUTION_TASK and begin work  
**Reference**: IMPLEMENTATION_START_POINT.md for workflows
