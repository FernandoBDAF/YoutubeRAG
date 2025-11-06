# SUBPLAN: Entity Type Distribution Analyzer

**Mother Plan**: PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md  
**Achievement Addressed**: Achievement 1.3 (Entity Type Distribution Analyzer Exists)  
**Status**: ✅ COMPLETE  
**Created**: 2025-11-06 01:00 UTC  
**Completed**: 2025-11-06 01:10 UTC  
**Actual Effort**: ~2 hours

---

## 🎯 Objective

Create an entity type distribution analyzer that identifies entity type gaps, analyzes OTHER category usage, and provides quality indicators (confidence by type, consistency) to improve entity type classification. This tool will help identify which entity types are missing or underused, and suggest improvements to entity type classification.

---

## 📋 What Needs to Be Created

### Files to Create

1. **`scripts/analyze_entity_types.py`**

   - Main script for analyzing entity type distribution
   - Analyzes type frequency, OTHER category usage, confidence by type
   - Identifies missing or underused entity types
   - Generates reports with recommendations

2. **`tests/scripts/test_analyze_entity_types.py`**
   - Test suite for the analyzer
   - Tests frequency counting, OTHER ratio calculation
   - Tests confidence analysis by type
   - Tests report generation

### Functions/Classes to Add

**In `scripts/analyze_entity_types.py`**:

- `EntityTypeDistributionAnalyzer` class:
  - `__init__(db_name, coll_name)` - Initialize with database/collection
  - `load_extraction_data()` - Load all completed extraction data
  - `analyze_type_distribution()` - Count entity type frequencies
  - `calculate_other_ratio()` - Calculate OTHER category usage ratio
  - `analyze_confidence_by_type()` - Calculate confidence scores by entity type
  - `identify_missing_types()` - Identify entity types that are rarely used
  - `analyze_type_consistency()` - Analyze consistency of entity type usage
  - `generate_report()` - Create markdown report with analysis and recommendations
  - `export_stats()` - Export JSON statistics

---

## 📝 Approach

**Strategy**: Implement using a Test-Driven Development (TDD) approach. Start by writing comprehensive tests for the `EntityTypeDistributionAnalyzer` class, then implement the class and its methods to make the tests pass.

**Method**:

1. **Test Setup**: Create `tests/scripts/test_analyze_entity_types.py` and define test cases for each functionality.
2. **Class Structure**: Create the `EntityTypeDistributionAnalyzer` class with `__init__` and placeholder methods.
3. **Data Loading**: Implement `load_extraction_data` method and corresponding tests (reuse pattern from predicate analyzer).
4. **Type Distribution**: Implement `analyze_type_distribution` and tests.
5. **OTHER Ratio**: Implement `calculate_other_ratio` and tests.
6. **Confidence Analysis**: Implement `analyze_confidence_by_type` and tests.
7. **Gap Identification**: Implement `identify_missing_types` and tests.
8. **Reporting**: Implement `generate_report` and `export_stats` with tests.

**Key Considerations**:

- **Entity Types**: Use `EntityType` enum from `core/models/graphrag.py` for reference types.
- **OTHER Category**: Focus on reducing OTHER usage by identifying patterns that could be classified better.
- **Confidence Analysis**: Analyze confidence scores by type to identify quality issues.
- **Consistency**: Check for entities that might be inconsistently typed across chunks.
- **Robustness**: Handle empty data, missing fields gracefully.

---

## 🧪 Tests Required (if applicable)

### Test File

- `tests/scripts/test_analyze_entity_types.py`

### Test Cases to Cover

1. `test_analyzer_initialization`: Verify correct setup with database and collection names.
2. `test_load_extraction_data_empty`: Test loading with no data in collection.
3. `test_load_extraction_data_success`: Test loading with mock data.
4. `test_analyze_type_distribution`: Test entity type frequency counting.
5. `test_calculate_other_ratio`: Test OTHER category ratio calculation.
6. `test_analyze_confidence_by_type`: Test confidence analysis by entity type.
7. `test_identify_missing_types`: Test identification of rarely used entity types.
8. `test_analyze_type_consistency`: Test consistency analysis (optional, more advanced).
9. `test_generate_report`: Test markdown report generation.
10. `test_export_stats`: Test JSON statistics export.
11. `test_end_to_end_analysis`: Integration test using mock data for full flow.
12. `test_edge_cases`: Test empty entities, missing types, missing confidence.

### Test-First Requirement

- [x] Tests written before implementation
- [ ] Initial test run shows all failing
- [x] Tests define success criteria

---

## ✅ Expected Results

### Functional Changes

- New Python script (`analyze_entity_types.py`) will be available in the `scripts/` directory.
- New test file (`test_analyze_entity_types.py`) will be in `tests/scripts/`.
- The script will generate markdown reports and JSON statistics in a specified output directory.

### Observable Outcomes

- Running `analyze_entity_types.py` will:
  - Analyze entity type distribution in the specified database
  - Identify OTHER category usage and patterns
  - Calculate confidence scores by entity type
  - Identify missing or underused entity types
  - Generate reports with distribution tables and recommendations
- Reports will show:
  - Total entities found by type
  - OTHER category ratio and patterns
  - Average confidence by entity type
  - Type diversity metrics
  - Recommendations for improving type classification
- All tests in `test_analyze_entity_types.py` will pass.

---

## 🔍 Conflict Analysis with Other Subplans

**Review Existing Subplans**:

- `SUBPLAN_01`: Achievement 0.1 (Extraction Stage Validation) - COMPLETE
- `SUBPLAN_02`: Achievement 1.1 (Quality Comparison Tools) - COMPLETE
- `SUBPLAN_03`: Achievement 1.2 (Predicate Distribution Analyzer) - COMPLETE

**Analysis**:

- Builds on `SUBPLAN_02` which already has entity quality analysis in `compare_extraction_quality.py`
- Can reuse similar patterns for data loading and MongoDB integration
- Complements `SUBPLAN_03` (predicate analyzer) by focusing on entity types
- No conflicts detected - this is a complementary analysis tool

**Result**: Safe to proceed

---

## 🔗 Dependencies

### Other Subplans

- None (depends on `SUBPLAN_01` and `SUBPLAN_02` being complete, which they are)

### External Dependencies

- `pymongo`
- `python-dotenv`
- `collections.Counter` for frequency counting
- `core/models/graphrag.py` for EntityType enum reference

### Prerequisite Knowledge

- Understanding of MongoDB data structure for GraphRAG extraction.
- Familiarity with entity types defined in `EntityType` enum.
- Understanding of entity extraction data structure.

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

- `EXECUTION_TASK_EXTRACTION-QUALITY-ENHANCEMENT_04_01.md`: Initial implementation and testing.

**First Execution**: `EXECUTION_TASK_EXTRACTION-QUALITY-ENHANCEMENT_04_01.md`

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [x] All deliverables created
- [x] All tests passing (if code work)
- [x] All expected results achieved
- [x] Code commented with learnings (if code work)
- [x] `EXECUTION_TASK_EXTRACTION-QUALITY-ENHANCEMENT_04_01.md` complete
- [x] Tested with real database data (13,048 chunks, 99,332 entities analyzed)
- [x] Real database validation: 6.17% OTHER ratio, 7/7 types used, excellent coverage
- [ ] Ready for archive (pending PLAN update)

---

## 📝 Notes

**Common Pitfalls**:

- Ensuring correct MongoDB connection and data loading.
- Handling edge cases for type frequency calculation (e.g., empty lists, missing types).
- Distinguishing between "OTHER" as a valid type vs missing type classification.
- Confidence analysis should account for missing confidence scores.

**Resources**:

- `scripts/compare_extraction_quality.py` (for entity quality analysis patterns)
- `scripts/analyze_predicate_distribution.py` (for data loading and report generation patterns)
- `core/models/graphrag.py` (for EntityType enum definition)
- `business/agents/graphrag/extraction.py` (for understanding entity extraction)

---

**Ready to Execute**: Create EXECUTION_TASK and begin work  
**Reference**: IMPLEMENTATION_START_POINT.md for workflows
