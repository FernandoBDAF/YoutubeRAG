# SUBPLAN: Predicate Distribution Analyzer

**Mother Plan**: PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md  
**Achievement Addressed**: Achievement 1.2 (Predicate Distribution Analyzer Exists)  
**Status**: ✅ COMPLETE  
**Created**: 2025-11-06 00:40 UTC  
**Completed**: 2025-11-06 00:30 UTC  
**Actual Effort**: ~2 hours

---

## 🎯 Objective

Create a predicate distribution analyzer that identifies ontology gaps by analyzing predicate frequency, canonical vs non-canonical ratios, and suggesting new canonical predicates and mappings. This tool will help identify which predicates are missing from the ontology and should be added to improve coverage.

---

## 📋 What Needs to Be Created

### Files to Create

1. **`scripts/analyze_predicate_distribution.py`**

   - Main script for analyzing predicate distribution
   - Analyzes frequency, canonical ratio, identifies gaps
   - Suggests new canonical predicates and mappings
   - Generates reports with recommendations

2. **`tests/scripts/test_analyze_predicate_distribution.py`**
   - Test suite for the analyzer
   - Tests frequency counting, canonical ratio calculation
   - Tests suggestion generation
   - Tests report generation

### Functions/Classes to Add

**In `scripts/analyze_predicate_distribution.py`**:

- `PredicateDistributionAnalyzer` class:
  - `__init__(db_name, coll_name)` - Initialize with database/collection
  - `load_extraction_data()` - Load all completed extraction data
  - `analyze_frequencies()` - Count predicate frequencies
  - `calculate_canonical_ratio()` - Calculate canonical vs non-canonical ratio
  - `identify_non_canonical_predicates()` - Find high-frequency non-canonical predicates
  - `suggest_canonical_predicates()` - Suggest new canonical predicates based on frequency
  - `suggest_mappings()` - Suggest mappings for non-canonical predicates
  - `generate_report()` - Create markdown report with analysis and recommendations
  - `export_stats()` - Export JSON statistics

---

## 📝 Approach

**Strategy**: Implement using a Test-Driven Development (TDD) approach. Start by writing comprehensive tests for the `PredicateDistributionAnalyzer` class, then implement the class and its methods to make the tests pass.

**Method**:

1. **Test Setup**: Create `tests/scripts/test_analyze_predicate_distribution.py` and define test cases for each functionality.
2. **Class Structure**: Create the `PredicateDistributionAnalyzer` class with `__init__` and placeholder methods.
3. **Data Loading**: Implement `load_extraction_data` method and corresponding tests.
4. **Frequency Analysis**: Implement `analyze_frequencies` and tests.
5. **Canonical Ratio**: Implement `calculate_canonical_ratio` and tests.
6. **Gap Identification**: Implement `identify_non_canonical_predicates` and tests.
7. **Suggestions**: Implement `suggest_canonical_predicates` and `suggest_mappings` with tests.
8. **Reporting**: Implement `generate_report` and `export_stats` with tests.

**Key Considerations**:

- **Ontology Integration**: Use `load_ontology()` to get canonical predicates and mappings.
- **Frequency Thresholds**: Define minimum frequency thresholds for suggestions (e.g., must appear in at least X chunks or Y% of chunks).
- **Similarity Matching**: Use Jaro-Winkler similarity (like `compare_extraction_quality.py`) to suggest mappings.
- **Robustness**: Handle empty data, missing fields gracefully.

---

## 🧪 Tests Required (if applicable)

### Test File

- `tests/scripts/test_analyze_predicate_distribution.py`

### Test Cases to Cover

1. `test_analyzer_initialization`: Verify correct setup with database and collection names.
2. `test_load_extraction_data_empty`: Test loading with no data in collection.
3. `test_load_extraction_data_success`: Test loading with mock data.
4. `test_analyze_frequencies`: Test predicate frequency counting.
5. `test_calculate_canonical_ratio`: Test canonical ratio calculation.
6. `test_identify_non_canonical_predicates`: Test identification of high-frequency non-canonical predicates.
7. `test_suggest_canonical_predicates`: Test suggestion logic based on frequency thresholds.
8. `test_suggest_mappings`: Test mapping suggestions using similarity matching.
9. `test_generate_report`: Test markdown report generation.
10. `test_export_stats`: Test JSON statistics export.
11. `test_end_to_end_analysis`: Integration test using mock data for full flow.
12. `test_missing_ontology_data`: Test graceful handling if ontology files are missing.

### Test-First Requirement

- [x] Tests written before implementation
- [ ] Initial test run shows all failing
- [x] Tests define success criteria

---

## ✅ Expected Results

### Functional Changes

- New Python script (`analyze_predicate_distribution.py`) will be available in the `scripts/` directory.
- New test file (`test_analyze_predicate_distribution.py`) will be in `tests/scripts/`.
- The script will generate markdown reports and JSON statistics in a specified output directory.

### Observable Outcomes

- Running `analyze_predicate_distribution.py` will:
  - Analyze predicate distribution in the specified database
  - Identify high-frequency non-canonical predicates
  - Suggest new canonical predicates and mappings
  - Generate reports with frequency tables and recommendations
- Reports will show:
  - Total predicates found
  - Canonical vs non-canonical ratio
  - Top non-canonical predicates by frequency
  - Suggested new canonical predicates
  - Suggested mappings for non-canonical predicates
- All tests in `test_analyze_predicate_distribution.py` will pass.

---

## 🔍 Conflict Analysis with Other Subplans

**Review Existing Subplans**:

- `SUBPLAN_01`: Achievement 0.1 (Extraction Stage Validation) - COMPLETE
- `SUBPLAN_02`: Achievement 1.1 (Quality Comparison Tools) - COMPLETE

**Analysis**:

- Builds on `SUBPLAN_02` which already has predicate analysis logic in `compare_extraction_quality.py`
- Can reuse similar patterns for data loading and ontology integration
- No conflicts detected - this is a complementary analysis tool

**Result**: Safe to proceed

---

## 🔗 Dependencies

### Other Subplans

- None (depends on `SUBPLAN_01` and `SUBPLAN_02` being complete, which they are)

### External Dependencies

- `pymongo`
- `python-dotenv`
- `pyyaml`
- `jellyfish` (for Jaro-Winkler similarity in mapping suggestions)
- `collections.Counter` for frequency counting

### Prerequisite Knowledge

- Understanding of MongoDB data structure for GraphRAG extraction.
- Familiarity with the ontology definition in `ontology/` directory.
- Understanding of predicate canonicalization process.

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

- `EXECUTION_TASK_EXTRACTION-QUALITY-ENHANCEMENT_03_01.md`: Initial implementation and testing.

**First Execution**: `EXECUTION_TASK_EXTRACTION-QUALITY-ENHANCEMENT_03_01.md`

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [x] All deliverables created
- [x] All tests passing (if code work)
- [x] All expected results achieved
- [x] Code commented with learnings (if code work)
- [x] `EXECUTION_TASK_EXTRACTION-QUALITY-ENHANCEMENT_03_01.md` complete
- [x] Tested with real database data (13,048 chunks analyzed)
- [x] Real database validation: 100% canonical ratio, no gaps found
- [ ] Ready for archive (pending PLAN update)

---

## 📝 Notes

**Common Pitfalls**:

- Ensuring correct MongoDB connection and data loading.
- Handling edge cases for frequency calculation (e.g., empty lists, zero divisions).
- Aligning frequency thresholds with meaningful gaps (not too low, not too high).
- Similarity matching should use same approach as `compare_extraction_quality.py` for consistency.

**Resources**:

- `scripts/compare_extraction_quality.py` (for data loading and ontology integration patterns)
- `scripts/derive_ontology.py` (for predicate frequency analysis patterns)
- `scripts/build_predicate_map.py` (for mapping suggestion patterns)
- `core/libraries/ontology/loader.py` (for loading ontology data)

---

**Ready to Execute**: Create EXECUTION_TASK and begin work  
**Reference**: IMPLEMENTATION_START_POINT.md for workflows
