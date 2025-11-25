# SUBPLAN: Legacy Collection Coexistence Verified

**Type**: SUBPLAN  
**Mother Plan**: PLAN_GRAPHRAG-OBSERVABILITY-VALIDATION.md  
**Plan**: GRAPHRAG-OBSERVABILITY-VALIDATION  
**Achievement**: 4.2  
**Created**: 2025-11-13  
**Status**: 📋 Design Phase

---

## 🎯 Objective

Verify that legacy collections (`entities`, `relations`, `communities`) and new observability collections (`entities_resolved`, `relations_final`, `transformation_logs`, etc.) can coexist in the same MongoDB database without conflicts, ensuring backward compatibility with existing queries while enabling new observability features.

**Core Validation**: Confirm that:

1. Legacy collections remain untouched by new pipeline
2. New collections are created separately
3. No data conflicts between legacy and new collections
4. No schema conflicts between legacy and new collections
5. Existing queries against legacy collections continue to work
6. New queries against observability collections return correct data

---

## 📦 Deliverables

### Required Deliverables

1. **Coexistence Verification Report** (`documentation/Legacy-Collection-Coexistence-Report.md`)

   - Test results for legacy collection queries
   - Test results for new collection queries
   - Verification that collections are separate
   - Data conflict analysis
   - Schema conflict analysis
   - Summary of coexistence status

2. **Collection Usage Guide** (`documentation/Collection-Usage-Guide.md`)

   - When to use legacy collections
   - When to use new observability collections
   - Collection naming conventions
   - Collection purpose and contents
   - Query examples for each collection type
   - Best practices for collection selection

3. **Migration Considerations Document** (`documentation/Migration-Considerations.md`)
   - Migration strategy from legacy to new collections
   - Data migration procedures (if needed)
   - Query migration examples
   - Timeline recommendations
   - Risk assessment
   - Rollback procedures

---

## 🎯 Approach

### 3-Phase Sequential Execution

**Phase 1: Legacy Collection Testing** (30-45 min)

- Identify existing queries that use legacy collections
- Test queries against `entities` collection
- Test queries against `relations` collection
- Test queries against `communities` collection (if exists)
- Document query results
- Verify no errors or breakage

**Phase 2: New Collection Testing** (30-45 min)

- Identify new queries for observability collections
- Test queries against `entities_resolved` collection
- Test queries against `relations_final` collection
- Test queries against `transformation_logs` collection
- Test queries against observability collections
- Document query results
- Verify correct data returned

**Phase 3: Coexistence Verification & Documentation** (60-90 min)

- Verify legacy collections untouched by new pipeline
- Verify new collections created separately
- Check for data conflicts (same IDs, overlapping data)
- Check for schema conflicts (incompatible structures)
- Create coexistence verification report
- Create collection usage guide
- Create migration considerations document

---

## 🔄 Execution Strategy

### Single Sequential Execution

**Why Single Execution**: All phases build on each other - legacy testing establishes baseline, new collection testing validates observability, and coexistence verification requires results from both.

**Execution Flow**:

1. Phase 1: Test legacy collections (baseline)
2. Phase 2: Test new collections (observability)
3. Phase 3: Verify coexistence and document (synthesis)

**Total Estimated Time**: 2-3 hours

**EXECUTION_TASK**: `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_42_01.md`

---

## 🧪 Critical Tests

### Test 1: Legacy Entities Collection

**What**: Verify existing queries against `entities` collection work

**How**:

```bash
# Query legacy entities collection
mongosh mongo_hack --eval "db.entities.find().limit(5).pretty()"
mongosh mongo_hack --eval "db.entities.countDocuments()"
```

**Expected Result**:

- Query executes successfully
- Returns entity documents (if data exists)
- No errors or schema issues

---

### Test 2: Legacy Relations Collection

**What**: Verify existing queries against `relations` collection work

**How**:

```bash
# Query legacy relations collection
mongosh mongo_hack --eval "db.relations.find().limit(5).pretty()"
mongosh mongo_hack --eval "db.relations.countDocuments()"
```

**Expected Result**:

- Query executes successfully
- Returns relationship documents (if data exists)
- No errors or schema issues

---

### Test 3: New Entities Resolved Collection

**What**: Verify new queries against `entities_resolved` collection work

**How**:

```bash
# Query new entities_resolved collection
mongosh mongo_hack --eval "db.entities_resolved.find().limit(5).pretty()"
mongosh mongo_hack --eval "db.entities_resolved.countDocuments()"
```

**Expected Result**:

- Query executes successfully
- Returns resolved entity documents
- Includes trace_id and observability metadata

---

### Test 4: New Relations Final Collection

**What**: Verify new queries against `relations_final` collection work

**How**:

```bash
# Query new relations_final collection
mongosh mongo_hack --eval "db.relations_final.find().limit(5).pretty()"
mongosh mongo_hack --eval "db.relations_final.countDocuments()"
```

**Expected Result**:

- Query executes successfully
- Returns final relationship documents
- Includes trace_id and observability metadata

---

### Test 5: Collection Separation

**What**: Verify legacy and new collections are separate

**How**:

```bash
# List all collections
mongosh mongo_hack --eval "db.getCollectionNames()"

# Check if legacy collections exist
mongosh mongo_hack --eval "db.entities.countDocuments()"
mongosh mongo_hack --eval "db.relations.countDocuments()"

# Check if new collections exist
mongosh mongo_hack --eval "db.entities_resolved.countDocuments()"
mongosh mongo_hack --eval "db.relations_final.countDocuments()"
```

**Expected Result**:

- Both legacy and new collections exist
- Collections have different names
- No overlap in collection names

---

### Test 6: Data Conflict Check

**What**: Verify no data conflicts between legacy and new collections

**How**:

```bash
# Check for overlapping entity IDs
mongosh mongo_hack --eval "
  const legacyIds = db.entities.distinct('_id');
  const newIds = db.entities_resolved.distinct('_id');
  const overlap = legacyIds.filter(id => newIds.includes(id));
  print('Overlapping IDs: ' + overlap.length);
"
```

**Expected Result**:

- No overlapping IDs (or expected overlap if migration in progress)
- Legacy data untouched
- New data separate

---

### Test 7: Schema Conflict Check

**What**: Verify no schema conflicts between legacy and new collections

**How**:

```bash
# Compare schemas
mongosh mongo_hack --eval "
  const legacySchema = Object.keys(db.entities.findOne() || {});
  const newSchema = Object.keys(db.entities_resolved.findOne() || {});
  print('Legacy fields: ' + legacySchema);
  print('New fields: ' + newSchema);
"
```

**Expected Result**:

- New collections have additional observability fields (trace_id, etc.)
- Legacy collections unchanged
- No incompatible field types

---

### Test 8: Transformation Logs Collection

**What**: Verify transformation_logs collection exists and is separate

**How**:

```bash
# Query transformation logs
mongosh mongo_hack --eval "db.transformation_logs.find().limit(5).pretty()"
mongosh mongo_hack --eval "db.transformation_logs.countDocuments()"
```

**Expected Result**:

- Collection exists
- Contains transformation log documents
- Separate from legacy collections

---

### Test 9: Intermediate Data Collections

**What**: Verify intermediate data collections exist and are separate

**How**:

```bash
# Query intermediate data collections
mongosh mongo_hack --eval "db.entity_mentions.find().limit(5).pretty()"
mongosh mongo_hack --eval "db.entities_before_resolution.find().limit(5).pretty()"
mongosh mongo_hack --eval "db.entities_after_resolution.find().limit(5).pretty()"
```

**Expected Result**:

- Collections exist
- Contain intermediate data
- Separate from legacy collections

---

### Test 10: Quality Metrics Collection

**What**: Verify quality_metrics collection exists and is separate

**How**:

```bash
# Query quality metrics
mongosh mongo_hack --eval "db.quality_metrics.find().limit(5).pretty()"
mongosh mongo_hack --eval "db.quality_metrics.countDocuments()"
```

**Expected Result**:

- Collection exists
- Contains quality metric documents
- Separate from legacy collections

---

## 📊 Expected Results

### Collection Inventory

**Legacy Collections** (may or may not exist):

- `entities` - Original entity collection
- `relations` - Original relationship collection
- `communities` - Original community collection
- `chunks` - Original chunk collection

**New Observability Collections** (should exist after Achievement 2.2):

- `entities_resolved` - Resolved entities (replaces `entities`)
- `relations_final` - Final relationships (replaces `relations`)
- `transformation_logs` - Transformation decisions
- `entity_mentions` - Raw extracted entities
- `entities_before_resolution` - Entities before resolution
- `entities_after_resolution` - Entities after resolution
- `relations_before_filter` - Relationships before filtering
- `quality_metrics` - Quality metrics
- `graphrag_runs` - Pipeline run metadata

### Coexistence Status

**Expected**: ✅ **COEXIST**

- Legacy collections (if they exist) remain untouched
- New collections created with different names
- No data conflicts
- No schema conflicts
- Both can be queried independently

**Alternative**: ⚠️ **MIGRATION IN PROGRESS**

- Legacy collections being phased out
- New collections replacing legacy
- Some overlap expected
- Document migration strategy

**Failure**: ❌ **CONFLICT**

- Collections overwrite each other
- Data corruption
- Schema incompatibilities
- Queries fail

---

## 🚨 Known Issues & Mitigations

### Issue 1: Legacy Collections Don't Exist

**Problem**: Fresh database may not have legacy collections.

**Solution**: Document that coexistence is N/A for fresh installations. Focus on verifying new collections work correctly.

**Mitigation**: Create test legacy collections if needed for verification.

---

### Issue 2: Collection Name Conflicts

**Problem**: Legacy and new collections might have conflicting names.

**Solution**: Already resolved in Achievement 0.1 (Collection Name Compatibility). Verify no regressions.

**Mitigation**: Check `core/config/paths.py` for collection name definitions.

---

### Issue 3: Data Migration Needed

**Problem**: Users with legacy data may need to migrate.

**Solution**: Document migration strategy in Migration Considerations document.

**Mitigation**: Provide migration scripts or procedures.

---

### Issue 4: Schema Evolution

**Problem**: New collections have different schemas than legacy.

**Solution**: Document schema differences in Collection Usage Guide.

**Mitigation**: Provide schema comparison and field mapping.

---

### Issue 5: Query Compatibility

**Problem**: Queries written for legacy collections may not work with new collections.

**Solution**: Provide query migration examples in Collection Usage Guide.

**Mitigation**: Document field name changes and new fields.

---

## 🧪 Validation

### Automated Validation Script

**Script**: `observability/validate-achievement-42.sh`

**Tests** (20 total):

1. ✅ Legacy Collections Queryable (3 tests)
2. ✅ New Collections Queryable (6 tests)
3. ✅ Collection Separation Verified (2 tests)
4. ✅ Data Conflicts Checked (2 tests)
5. ✅ Schema Conflicts Checked (2 tests)
6. ✅ Deliverables Exist (3 tests)
7. ✅ EXECUTION_TASK Complete (2 tests)

**How to Run**:

```bash
# From project root
bash work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/validate-achievement-42.sh

# Expected output: 20/20 tests passed ✅
# Exit code: 0 (success)
```

**Validation Criteria**:

- Legacy collections queryable (if they exist)
- All new observability collections queryable
- Collections have different names (no conflicts)
- No data conflicts detected
- No schema conflicts detected
- All 3 deliverables exist and have content
- EXECUTION_TASK marked as complete

---

## 📚 Reference Documents

**From Parent PLAN** (PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md):

- Achievement 0.1: Collection Name Compatibility Resolved
- Achievement 0.2: Configuration Compatibility Verified
- Achievement 0.3: Environment Variables Configured

**From This PLAN**:

- Achievement 2.1: Baseline Pipeline Run (test data source)
- Achievement 2.2: Observability Pipeline Run (new collections created)
- Achievement 4.1: Stage Compatibility Verified (CLI infrastructure)

**Configuration Files**:

- `core/config/paths.py`: Collection name definitions
- `core/config/graphrag.py`: Pipeline configuration
- `.env`: Environment variables

**Observability Collections**:

- `transformation_logs`: Transformation decisions
- `entity_mentions`: Raw extracted entities
- `entities_before_resolution`: Entities before resolution
- `entities_after_resolution`: Entities after resolution
- `entities_resolved`: Final resolved entities
- `relations_before_filter`: Relationships before filtering
- `relations_final`: Final relationships
- `quality_metrics`: Quality metrics
- `graphrag_runs`: Pipeline run metadata

---

**SUBPLAN Status**: 📋 Ready for EXECUTION_TASK Creation  
**Next Step**: Create EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_42_01.md
