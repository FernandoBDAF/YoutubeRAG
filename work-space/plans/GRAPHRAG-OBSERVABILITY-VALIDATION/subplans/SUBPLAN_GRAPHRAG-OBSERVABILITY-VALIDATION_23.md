# SUBPLAN: Data Quality Validation

**Type**: SUBPLAN  
**Mother Plan**: PLAN_GRAPHRAG-OBSERVABILITY-VALIDATION.md  
**Plan**: GRAPHRAG-OBSERVABILITY-VALIDATION  
**Achievement Addressed**: Achievement 2.3 (Data Quality Validation)  
**Achievement**: 2.3  
**Status**: Not Started  
**Created**: 2025-11-12  
**Estimated Effort**: 2-3 hours (validation + analysis + documentation)

---

## 🎯 Objective

Verify that all observability collections created in Achievement 2.2 contain correct, complete, and high-quality data. This validation ensures the observability infrastructure is not only functional but also producing reliable data for analysis and debugging.

**Primary Goal**: Validate data quality and schema correctness across all 8 observability collections

**Success Criteria**:

1. All 8 observability collections exist and are populated
2. Document counts are reasonable and consistent
3. Trace IDs are consistent across all collections
4. Schemas match expected structure (fields, types, formats)
5. Data quality is high (no critical missing fields, valid ranges)
6. Indexes are created correctly
7. All findings documented comprehensively

---

## 📦 Deliverables

### Required Deliverables (4)

1. **`Data-Quality-Validation-Report.md`**

   - Location: `documentation/`
   - Content: Comprehensive validation results for all 8 collections
   - Includes: Document counts, schema validation, data quality checks, findings

2. **`Schema-Verification-Results.md`**

   - Location: `documentation/`
   - Content: Detailed schema validation for each collection
   - Includes: Expected vs actual schemas, field types, indexes, sample documents

3. **`Trace-ID-Consistency-Report.md`**

   - Location: `documentation/`
   - Content: Trace ID validation across all collections
   - Includes: Trace ID distribution, consistency checks, query examples

4. **`Data-Quality-Issues-Log.md`**
   - Location: `documentation/`
   - Content: Log of any data quality issues found (or "No issues found")
   - Includes: Issue descriptions, severity, recommendations

---

## 🔄 Approach

### Phase 1: Collection Verification (30-45 min)

**Objective**: Verify all observability collections exist and are populated

**Tasks**:

1. **List All Collections**:

   ```bash
   mongosh "mongodb+srv://..." --eval "
     db.getCollectionNames().filter(c =>
       ['transformation_logs', 'entities_raw', 'entities_resolved',
        'relations_raw', 'relations_final', 'graph_pre_detection',
        'quality_metrics', 'graphrag_runs'].includes(c)
     ).forEach(c => print(c));
   "
   ```

2. **Count Documents in Each Collection**:

   ```bash
   mongosh "mongodb+srv://..." --eval "
     const collections = [
       'transformation_logs',
       'entities_raw',
       'entities_resolved',
       'relations_raw',
       'relations_final',
       'graph_pre_detection',
       'quality_metrics',
       'graphrag_runs'
     ];
     collections.forEach(coll => {
       const count = db[coll].countDocuments({});
       print(coll + ': ' + count + ' documents');
     });
   "
   ```

3. **Verify Reasonable Counts**:

   - Compare counts with expected ranges (from Achievement 2.2)
   - Flag any collections with 0 documents (critical issue)
   - Flag any collections with unexpectedly high/low counts

4. **Document Findings**:
   - Create summary table of collections and counts
   - Note any missing collections
   - Note any count anomalies

**Expected Outcome**: All 8 collections exist with reasonable document counts

---

### Phase 2: Schema Validation (45-60 min)

**Objective**: Verify data schemas match expected structure

**Tasks**:

1. **Sample Documents from Each Collection**:

   ```bash
   mongosh "mongodb+srv://..." --eval "
     const collections = ['transformation_logs', 'entities_raw', ...];
     collections.forEach(coll => {
       print('\\n=== ' + coll + ' ===');
       printjson(db[coll].findOne());
     });
   "
   ```

2. **Verify Field Presence**:

   - Check all expected fields are present
   - Note any missing required fields
   - Note any unexpected extra fields

3. **Verify Data Types**:

   - Check field types match expected (string, number, object, array)
   - Verify date fields are proper ISODate
   - Verify numeric fields are numbers (not strings)

4. **Verify Field Formats**:

   - Check trace_id format (UUID)
   - Check confidence scores (0.0-1.0 range)
   - Check entity_id format (32-char hash)
   - Check timestamps are valid

5. **Verify Indexes**:

   ```bash
   mongosh "mongodb+srv://..." --eval "
     const collections = ['transformation_logs', 'entities_raw', ...];
     collections.forEach(coll => {
       print('\\n=== ' + coll + ' indexes ===');
       db[coll].getIndexes().forEach(idx => print(idx.name));
     });
   "
   ```

6. **Document Schemas**:
   - Create schema documentation for each collection
   - Include sample documents
   - Note any schema issues

**Expected Outcome**: All schemas validated, documented, issues identified

---

### Phase 3: Trace ID Consistency Validation (30-45 min)

**Objective**: Verify trace_id consistency across all collections

**Tasks**:

1. **Extract Trace IDs from Achievement 2.2**:

   - Get trace_id from EXECUTION_OBSERVATION document
   - Get trace_id from logs
   - Expected: Single trace_id for entire run

2. **Verify Trace ID in Each Collection**:

   ```bash
   mongosh "mongodb+srv://..." --eval "
     const expected_trace_id = '...';  // From Achievement 2.2
     const collections = ['transformation_logs', 'entities_raw', ...];
     collections.forEach(coll => {
       const count = db[coll].countDocuments({trace_id: expected_trace_id});
       const total = db[coll].countDocuments({});
       print(coll + ': ' + count + '/' + total + ' docs with correct trace_id');
     });
   "
   ```

3. **Check for Multiple Trace IDs**:

   ```bash
   mongosh "mongodb+srv://..." --eval "
     const collections = ['transformation_logs', 'entities_raw', ...];
     collections.forEach(coll => {
       const trace_ids = db[coll].distinct('trace_id');
       print(coll + ': ' + trace_ids.length + ' unique trace_ids');
       if (trace_ids.length > 1) {
         print('  Trace IDs: ' + trace_ids.join(', '));
       }
     });
   "
   ```

4. **Test Trace ID Queries**:

   - Query each collection by trace_id
   - Verify results are consistent
   - Test cross-collection trace_id queries

5. **Document Trace ID Findings**:
   - Document trace_id distribution
   - Note any inconsistencies
   - Provide query examples

**Expected Outcome**: Single trace_id used consistently across all collections

---

### Phase 4: Data Quality Validation (45-60 min)

**Objective**: Verify data quality is high across all collections

**Tasks**:

1. **Check for Null/Missing Fields**:

   ```bash
   mongosh "mongodb+srv://..." --eval "
     // Check transformation_logs
     print('transformation_logs missing trace_id: ' +
       db.transformation_logs.countDocuments({trace_id: {$exists: false}}));
     print('transformation_logs missing operation: ' +
       db.transformation_logs.countDocuments({operation: {$exists: false}}));

     // Check entities_raw
     print('entities_raw missing entity_id: ' +
       db.entities_raw.countDocuments({entity_id: {$exists: false}}));
     print('entities_raw missing name: ' +
       db.entities_raw.countDocuments({name: {$exists: false}}));

     // ... repeat for all collections
   "
   ```

2. **Verify Confidence Scores**:

   ```bash
   mongosh "mongodb+srv://..." --eval "
     // Check confidence scores in valid range (0.0-1.0)
     print('entities_raw invalid confidence: ' +
       db.entities_raw.countDocuments({
         $or: [
           {confidence: {$lt: 0.0}},
           {confidence: {$gt: 1.0}}
         ]
       }));

     // ... repeat for relations_raw, relations_final
   "
   ```

3. **Verify Entity/Relationship Counts**:

   - Compare `entities_raw` count with `entities_resolved` count
   - Compare `relations_raw` count with `relations_final` count
   - Verify counts are reasonable (not 0, not unexpectedly high)
   - Compare with baseline counts from Achievement 2.1

4. **Verify Transformation Log Completeness**:

   ```bash
   mongosh "mongodb+srv://..." --eval "
     // Count transformation operations by type
     db.transformation_logs.aggregate([
       {$group: {_id: '$operation', count: {$sum: 1}}},
       {$sort: {count: -1}}
     ]).forEach(printjson);
   "
   ```

5. **Check Data Consistency**:

   - Verify entity IDs in `entities_resolved` exist in `entities_raw`
   - Verify relation IDs in `relations_final` exist in `relations_raw`
   - Check for orphaned records

6. **Document Quality Findings**:
   - Summarize data quality metrics
   - Note any quality issues
   - Provide recommendations

**Expected Outcome**: High data quality confirmed, issues documented

---

### Phase 5: Documentation (30-45 min)

**Objective**: Create all required deliverables

**Tasks**:

1. **Create `Data-Quality-Validation-Report.md`**:

   - Executive summary
   - Collection verification results (Phase 1)
   - Schema validation results (Phase 2)
   - Trace ID consistency results (Phase 3)
   - Data quality results (Phase 4)
   - Overall assessment
   - Recommendations

2. **Create `Schema-Verification-Results.md`**:

   - Schema for each collection
   - Expected vs actual comparison
   - Sample documents
   - Index verification
   - Schema issues (if any)

3. **Create `Trace-ID-Consistency-Report.md`**:

   - Trace ID from Achievement 2.2
   - Trace ID distribution across collections
   - Consistency validation results
   - Query examples

4. **Create `Data-Quality-Issues-Log.md`**:
   - List of all issues found (or "No issues found")
   - Issue severity (critical, high, medium, low)
   - Recommendations for each issue
   - Action items (if needed)

**Expected Outcome**: All 4 deliverables created and comprehensive

---

## 🎯 Execution Strategy

### Single Sequential Execution

**Rationale**: All phases build on each other and require access to the same MongoDB database. A single executor can complete all validation tasks efficiently.

**Execution Plan**:

- **EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_23_01.md**
  - Covers all 5 phases sequentially
  - Single executor performs entire workflow
  - Requires MongoDB access and Achievement 2.2 completion

**Why Single Execution**:

1. **Sequential Dependencies**: Each phase builds on previous phase findings
2. **Database Access**: All phases query the same database
3. **Context Continuity**: Executor maintains context across all validations
4. **Efficiency**: No need to coordinate between multiple executors

---

## 🧪 Tests

### Test 1: All Collections Exist

**Objective**: Verify all 8 observability collections were created

**Steps**:

```bash
mongosh "mongodb+srv://..." --eval "
  const required = [
    'transformation_logs',
    'entities_raw',
    'entities_resolved',
    'relations_raw',
    'relations_final',
    'graph_pre_detection',
    'quality_metrics',
    'graphrag_runs'
  ];
  const existing = db.getCollectionNames();
  const missing = required.filter(c => !existing.includes(c));
  if (missing.length > 0) {
    print('FAIL: Missing collections: ' + missing.join(', '));
  } else {
    print('PASS: All 8 collections exist');
  }
"
```

**Expected**: PASS - All 8 collections exist

---

### Test 2: All Collections Populated

**Objective**: Verify all collections have > 0 documents

**Steps**:

```bash
mongosh "mongodb+srv://..." --eval "
  const collections = [
    'transformation_logs',
    'entities_raw',
    'entities_resolved',
    'relations_raw',
    'relations_final',
    'graph_pre_detection',
    'quality_metrics',
    'graphrag_runs'
  ];
  let empty = [];
  collections.forEach(coll => {
    const count = db[coll].countDocuments({});
    if (count === 0) empty.push(coll);
  });
  if (empty.length > 0) {
    print('FAIL: Empty collections: ' + empty.join(', '));
  } else {
    print('PASS: All collections populated');
  }
"
```

**Expected**: PASS - All collections have > 0 documents

---

### Test 3: Trace ID Consistency

**Objective**: Verify single trace_id used across all collections

**Steps**:

```bash
mongosh "mongodb+srv://..." --eval "
  const collections = ['transformation_logs', 'entities_raw', 'entities_resolved',
                       'relations_raw', 'relations_final', 'graph_pre_detection',
                       'quality_metrics', 'graphrag_runs'];
  let trace_ids = new Set();
  collections.forEach(coll => {
    db[coll].distinct('trace_id').forEach(id => trace_ids.add(id));
  });
  if (trace_ids.size === 1) {
    print('PASS: Single trace_id across all collections: ' + Array.from(trace_ids)[0]);
  } else {
    print('FAIL: Multiple trace_ids found: ' + Array.from(trace_ids).join(', '));
  }
"
```

**Expected**: PASS - Single trace_id

---

### Test 4: Required Fields Present

**Objective**: Verify critical fields are present in all documents

**Steps**:

```bash
mongosh "mongodb+srv://..." --eval "
  // Check transformation_logs
  const missing_trace = db.transformation_logs.countDocuments({trace_id: {$exists: false}});
  const missing_op = db.transformation_logs.countDocuments({operation: {$exists: false}});

  // Check entities_raw
  const missing_entity_id = db.entities_raw.countDocuments({entity_id: {$exists: false}});
  const missing_name = db.entities_raw.countDocuments({name: {$exists: false}});

  if (missing_trace + missing_op + missing_entity_id + missing_name === 0) {
    print('PASS: All required fields present');
  } else {
    print('FAIL: Missing fields found');
    print('  transformation_logs missing trace_id: ' + missing_trace);
    print('  transformation_logs missing operation: ' + missing_op);
    print('  entities_raw missing entity_id: ' + missing_entity_id);
    print('  entities_raw missing name: ' + missing_name);
  }
"
```

**Expected**: PASS - All required fields present

---

### Test 5: Confidence Scores Valid

**Objective**: Verify confidence scores are in valid range (0.0-1.0)

**Steps**:

```bash
mongosh "mongodb+srv://..." --eval "
  const invalid_entities = db.entities_raw.countDocuments({
    $or: [{confidence: {$lt: 0.0}}, {confidence: {$gt: 1.0}}]
  });
  const invalid_relations = db.relations_raw.countDocuments({
    $or: [{confidence: {$lt: 0.0}}, {confidence: {$gt: 1.0}}]
  });

  if (invalid_entities + invalid_relations === 0) {
    print('PASS: All confidence scores in valid range');
  } else {
    print('FAIL: Invalid confidence scores found');
    print('  entities_raw: ' + invalid_entities);
    print('  relations_raw: ' + invalid_relations);
  }
"
```

**Expected**: PASS - All confidence scores valid

---

### Test 6: Entity Count Consistency

**Objective**: Verify entity counts are consistent across collections

**Steps**:

```bash
mongosh "mongodb+srv://..." --eval "
  const raw_count = db.entities_raw.countDocuments({});
  const resolved_count = db.entities_resolved.countDocuments({});
  const baseline_count = 220;  // From Achievement 2.1

  print('entities_raw: ' + raw_count);
  print('entities_resolved: ' + resolved_count);
  print('baseline (entities): ' + baseline_count);

  if (raw_count === resolved_count && resolved_count === baseline_count) {
    print('PASS: Entity counts consistent');
  } else {
    print('WARN: Entity counts differ (may be expected)');
  }
"
```

**Expected**: PASS or WARN (counts may differ slightly)

---

### Test 7: Indexes Created

**Objective**: Verify indexes are created on key fields

**Steps**:

```bash
mongosh "mongodb+srv://..." --eval "
  const collections = ['transformation_logs', 'entities_raw', 'entities_resolved'];
  let missing_indexes = [];

  collections.forEach(coll => {
    const indexes = db[coll].getIndexes();
    const has_trace_id = indexes.some(idx => idx.key.trace_id);
    if (!has_trace_id) {
      missing_indexes.push(coll + ' (trace_id)');
    }
  });

  if (missing_indexes.length === 0) {
    print('PASS: Key indexes present');
  } else {
    print('WARN: Missing indexes: ' + missing_indexes.join(', '));
  }
"
```

**Expected**: PASS - Key indexes present

---

### Test 8: GraphRAG Run Metadata

**Objective**: Verify graphrag_runs collection has run metadata

**Steps**:

```bash
mongosh "mongodb+srv://..." --eval "
  const run = db.graphrag_runs.findOne({});
  if (run && run.trace_id && run.start_time && run.end_time) {
    print('PASS: GraphRAG run metadata complete');
    print('  trace_id: ' + run.trace_id);
    print('  runtime: ' + (new Date(run.end_time) - new Date(run.start_time)) / 1000 + 's');
  } else {
    print('FAIL: GraphRAG run metadata incomplete');
  }
"
```

**Expected**: PASS - Run metadata complete

---

## 📊 Expected Results

### Collection Document Counts (Expected Ranges)

| Collection              | Expected Range | Notes                            |
| ----------------------- | -------------- | -------------------------------- |
| **transformation_logs** | 200-500        | Transformation operations logged |
| **entities_raw**        | ~220           | Raw entities before resolution   |
| **entities_resolved**   | ~220           | Resolved entities                |
| **relations_raw**       | ~71            | Raw relations before validation  |
| **relations_final**     | ~71            | Final validated relations        |
| **graph_pre_detection** | 1-5            | Graph snapshots                  |
| **quality_metrics**     | 50-200         | Quality metrics per stage        |
| **graphrag_runs**       | 1              | Single pipeline run              |

### Schema Validation Expected

✅ **All Fields Present**: No missing required fields  
✅ **Correct Data Types**: All fields have expected types  
✅ **Valid Formats**: UUIDs, hashes, dates formatted correctly  
✅ **Indexes Created**: Key indexes (trace_id, entity_id) present

### Trace ID Validation Expected

✅ **Single Trace ID**: One trace_id across all collections  
✅ **Consistent**: All documents have same trace_id  
✅ **Valid Format**: UUID format (e.g., `45c1256d-5d7d-46a3-900f-3b6b139a289a`)

### Data Quality Expected

✅ **No Missing Fields**: All required fields present  
✅ **Valid Confidence Scores**: All scores in 0.0-1.0 range  
✅ **Reasonable Counts**: Entity/relation counts match baseline  
✅ **Complete Logs**: Transformation logs cover all operations

---

## ⚠️ Risk Assessment

### Risk 1: Missing Collections

**Probability**: Low  
**Impact**: Critical  
**Mitigation**:

- Achievement 2.2 should have created all collections
- If missing, indicates Achievement 2.2 failure
- Document issue and recommend re-running Achievement 2.2

### Risk 2: Empty Collections

**Probability**: Low  
**Impact**: High  
**Mitigation**:

- Check if observability was actually enabled in Achievement 2.2
- Verify environment variables were set correctly
- Document issue and recommend re-running Achievement 2.2

### Risk 3: Multiple Trace IDs

**Probability**: Low  
**Impact**: Medium  
**Mitigation**:

- May indicate multiple pipeline runs in same database
- Check timestamps to identify which run to validate
- Document finding and recommend database cleanup

### Risk 4: Schema Mismatches

**Probability**: Medium  
**Impact**: Medium  
**Mitigation**:

- Document actual vs expected schemas
- Determine if mismatch is critical or acceptable
- Recommend schema updates if needed

---

## 📋 Prerequisites

### From Achievement 2.2

- [x] Pipeline executed with observability enabled
- [x] All 8 observability collections created
- [x] Trace ID documented in EXECUTION_OBSERVATION
- [x] Pipeline completed successfully

### Environment

- [x] MongoDB accessible
- [x] `mongosh` installed and configured
- [x] Access to Achievement 2.2 deliverables

---

## 🎓 Success Criteria

### Must Have (Critical)

1. ✅ All 8 collections exist
2. ✅ All collections have > 0 documents
3. ✅ Single trace_id across all collections
4. ✅ All required fields present
5. ✅ All 4 deliverables created

### Should Have (Important)

6. ✅ Confidence scores in valid range
7. ✅ Entity/relation counts match baseline
8. ✅ Indexes created correctly
9. ✅ No critical data quality issues

### Nice to Have (Optional)

10. ⭐ Sample documents included in deliverables
11. ⭐ Query examples provided
12. ⭐ Detailed schema documentation

---

## 📝 Notes

### Key Decisions

1. **Validation Scope**: Validate all 8 collections comprehensively
2. **Comparison Baseline**: Use Achievement 2.1 baseline for count comparisons
3. **Issue Severity**: Classify issues as critical, high, medium, low
4. **Documentation**: Create separate documents for different aspects (quality, schema, trace_id)

### References

- **Achievement 2.2 Deliverables**: For trace_id and expected counts
- **Achievement 2.1 Baseline**: For entity/relation/community count comparison
- **Collection Schemas**: Expected schemas defined in observability infrastructure code

---

**SUBPLAN Status**: ✅ COMPLETE (Ready for Executor)  
**Next Step**: Executor creates and runs EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_23_01.md  
**Estimated Total Time**: 2-3 hours (validation + analysis + documentation)
