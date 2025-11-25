# Migration Considerations

**Achievement**: 4.2 - Legacy Collection Coexistence Verified  
**Date**: 2025-11-13  
**Purpose**: Guide for migrating from legacy to observability collections  
**Audience**: DevOps, Data Engineers, Technical Leads

---

## 📋 Executive Summary

This document outlines the strategy, procedures, and considerations for migrating from legacy collections (`entities`, `relations`, `communities`) to new observability collections (`entities_resolved`, `relations_final`, etc.).

**Key Decision**: Migration is **OPTIONAL** - both collection types can coexist indefinitely.

**Recommendation**: 
- **New Projects**: Use observability collections from the start
- **Existing Projects**: Evaluate migration based on needs (debugging, quality monitoring)
- **Production Systems**: Consider keeping legacy collections for performance

---

## 🎯 Migration Strategy Overview

### Option 1: Gradual Migration (Recommended)

**Approach**: Run both pipelines in parallel, gradually shift to observability

**Timeline**: 2-4 weeks

**Steps**:
1. Week 1: Enable observability, run in parallel with legacy
2. Week 2: Test observability collections, verify data quality
3. Week 3: Update queries to use observability collections
4. Week 4: Deprecate legacy pipeline, keep collections for backup

**Pros**:
- Low risk (can rollback easily)
- Time to validate observability data
- Smooth transition

**Cons**:
- Higher storage usage during transition
- Maintenance of two pipelines

---

### Option 2: Clean Cut Migration

**Approach**: Switch entirely to observability collections

**Timeline**: 1 week

**Steps**:
1. Day 1-2: Enable observability, test thoroughly
2. Day 3-4: Update all queries to use new collections
3. Day 5: Deploy changes, monitor closely
4. Day 6-7: Verify everything works, fix issues

**Pros**:
- Fast transition
- Lower storage usage
- Clean break from legacy

**Cons**:
- Higher risk (harder to rollback)
- Requires thorough testing upfront
- Potential downtime if issues arise

---

### Option 3: No Migration (Coexistence)

**Approach**: Keep using legacy collections, enable observability selectively

**Timeline**: N/A (ongoing)

**Steps**:
1. Keep legacy pipeline for production
2. Use observability pipeline for debugging/development
3. Maintain both collection types indefinitely

**Pros**:
- Zero migration risk
- Best of both worlds
- Flexibility to choose per use case

**Cons**:
- Higher storage usage
- Maintenance of two pipelines
- Potential confusion about which to use

---

## 🔄 When to Migrate

### Migrate If:

✅ **You need debugging capabilities**
- Want to understand pipeline decisions
- Need to trace entity resolution
- Want to see before/after states

✅ **You need quality monitoring**
- Want to track metrics over time
- Need to detect quality degradation
- Want to compare pipeline versions

✅ **You're doing experimentation**
- A/B testing pipeline changes
- Comparing different configurations
- Need systematic experiment tracking

✅ **You're starting a new project**
- No legacy data to migrate
- Can benefit from observability from day one
- Want full visibility into pipeline

---

### Don't Migrate If:

❌ **Performance is critical**
- Production system with tight latency requirements
- Storage is limited
- Observability overhead is unacceptable

❌ **You have stable production system**
- Pipeline works well
- No debugging needed
- No quality issues

❌ **You lack resources**
- No time for migration
- No staff to maintain observability
- No storage for additional collections

---

## 📦 Data Migration Procedures

### Scenario 1: Fresh Start (No Existing Data)

**Situation**: No data in legacy collections

**Procedure**:
1. Enable observability features
2. Run pipeline
3. New collections will be created automatically
4. No migration needed!

**Commands**:
```bash
# Enable observability
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
export GRAPHRAG_QUALITY_METRICS=true

# Run pipeline
python business/pipelines/graphrag.py --video-id <video-id>
```

**Status**: ✅ **CURRENT STATE** - No legacy data exists

---

### Scenario 2: Existing Data in Legacy Collections

**Situation**: Legacy collections have data that needs to be preserved

**Procedure**:

**Step 1: Backup Legacy Data**
```bash
# Export legacy collections
mongodump --db mongo_hack --collection entities --out backup/
mongodump --db mongo_hack --collection relations --out backup/
mongodump --db mongo_hack --collection communities --out backup/
```

**Step 2: Enable Observability**
```bash
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
export GRAPHRAG_QUALITY_METRICS=true
```

**Step 3: Run Pipeline (Creates New Collections)**
```bash
python business/pipelines/graphrag.py --video-id <video-id>
```

**Step 4: Verify New Collections**
```bash
mongosh mongo_hack --eval "db.entities_resolved.countDocuments()"
mongosh mongo_hack --eval "db.relations_final.countDocuments()"
```

**Step 5: Update Queries**
- Change `db.entities` → `db.entities_resolved`
- Change `db.relations` → `db.relations_final`
- Add `trace_id` filtering where needed

**Step 6: Test Thoroughly**
- Run all queries against new collections
- Verify results match expectations
- Check for missing data

**Step 7: Deprecate Legacy (Optional)**
- Rename legacy collections (e.g., `entities_legacy`)
- Keep as backup for 30 days
- Delete after verification period

---

### Scenario 3: Partial Migration (Selective Collections)

**Situation**: Want to migrate some collections but not others

**Procedure**:

**Example: Migrate entities only, keep relations legacy**

```bash
# Enable selective observability
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
export GRAPHRAG_QUALITY_METRICS=false  # Disable metrics

# Run pipeline
python business/pipelines/graphrag.py --video-id <video-id>

# Update entity queries only
# db.entities → db.entities_resolved
# Keep db.relations as is
```

---

## 🔀 Query Migration Examples

### Example 1: Simple Entity Query

**Legacy Query**:
```javascript
db.entities.find({ type: "PERSON" }).limit(10)
```

**Migrated Query**:
```javascript
db.entities_resolved.find({ type: "PERSON" }).limit(10)
```

**Changes**: Collection name only

---

### Example 2: Entity Query with Filtering

**Legacy Query**:
```javascript
db.entities.find({ 
  type: "PERSON",
  "metadata.confidence": { $gt: 0.8 }
})
```

**Migrated Query**:
```javascript
db.entities_resolved.find({ 
  type: "PERSON",
  "metadata.confidence": { $gt: 0.8 }
})
```

**Changes**: Collection name only (fields are compatible)

---

### Example 3: Relationship Query

**Legacy Query**:
```javascript
db.relations.find({ 
  source: "entity_123",
  type: "KNOWS"
})
```

**Migrated Query**:
```javascript
db.relations_final.find({ 
  source: "entity_123",
  type: "KNOWS"
})
```

**Changes**: Collection name only

---

### Example 4: Query with trace_id (New Feature)

**Legacy Query**: N/A (trace_id doesn't exist)

**Migrated Query**:
```javascript
db.entities_resolved.find({ 
  trace_id: "abc123",
  type: "PERSON"
})
```

**Changes**: Can now filter by trace_id for debugging

---

### Example 5: Aggregation Pipeline

**Legacy Query**:
```javascript
db.entities.aggregate([
  { $match: { type: "PERSON" } },
  { $group: { _id: "$type", count: { $sum: 1 } } }
])
```

**Migrated Query**:
```javascript
db.entities_resolved.aggregate([
  { $match: { type: "PERSON" } },
  { $group: { _id: "$type", count: { $sum: 1 } } }
])
```

**Changes**: Collection name only (aggregation logic unchanged)

---

## ⏱️ Timeline Recommendations

### Gradual Migration Timeline

**Week 1: Preparation**
- Day 1-2: Review migration plan
- Day 3-4: Set up observability environment
- Day 5: Enable observability, run test pipeline
- Day 6-7: Verify new collections created correctly

**Week 2: Parallel Operation**
- Day 1-3: Run both pipelines in parallel
- Day 4-5: Compare data between legacy and observability collections
- Day 6-7: Identify and fix any discrepancies

**Week 3: Query Migration**
- Day 1-2: Update queries to use new collections
- Day 3-4: Test updated queries thoroughly
- Day 5: Deploy query changes to staging
- Day 6-7: Monitor staging, fix issues

**Week 4: Production Cutover**
- Day 1-2: Deploy to production
- Day 3-4: Monitor closely, verify everything works
- Day 5: Deprecate legacy pipeline
- Day 6-7: Keep legacy collections as backup

**Total**: 4 weeks

---

### Clean Cut Migration Timeline

**Week 1: Rapid Migration**
- Day 1: Enable observability, test thoroughly
- Day 2: Update all queries
- Day 3: Test updated queries
- Day 4: Deploy to staging
- Day 5: Deploy to production
- Day 6-7: Monitor, fix issues, verify

**Total**: 1 week

---

## ⚠️ Risk Assessment

### High Risk Scenarios

🔴 **Risk 1: Data Loss**
- **Scenario**: Migration fails, legacy data deleted
- **Mitigation**: Always backup before migration
- **Rollback**: Restore from backup

🔴 **Risk 2: Query Breakage**
- **Scenario**: Updated queries don't work with new collections
- **Mitigation**: Test all queries before deployment
- **Rollback**: Revert query changes

🔴 **Risk 3: Performance Degradation**
- **Scenario**: Observability overhead impacts production
- **Mitigation**: Test performance in staging first
- **Rollback**: Disable observability features

---

### Medium Risk Scenarios

🟡 **Risk 4: Storage Overflow**
- **Scenario**: New collections use too much storage
- **Mitigation**: Monitor storage, set TTL indexes
- **Rollback**: Delete observability collections

🟡 **Risk 5: Schema Incompatibility**
- **Scenario**: New schema breaks existing code
- **Mitigation**: Test schema compatibility thoroughly
- **Rollback**: Use legacy collections

---

### Low Risk Scenarios

🟢 **Risk 6: User Confusion**
- **Scenario**: Users don't know which collection to use
- **Mitigation**: Document clearly, provide training
- **Rollback**: N/A (documentation issue)

🟢 **Risk 7: Maintenance Overhead**
- **Scenario**: Maintaining two pipelines is burdensome
- **Mitigation**: Automate where possible
- **Rollback**: Choose one pipeline to maintain

---

## 🔙 Rollback Procedures

### Rollback Scenario 1: Observability Pipeline Fails

**Symptoms**: New collections not created, pipeline errors

**Procedure**:
1. Disable observability features
2. Revert to legacy pipeline
3. Investigate errors
4. Fix issues before retrying

**Commands**:
```bash
# Disable observability
export GRAPHRAG_TRANSFORMATION_LOGGING=false
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
export GRAPHRAG_QUALITY_METRICS=false

# Run legacy pipeline
python business/pipelines/graphrag.py --video-id <video-id>
```

---

### Rollback Scenario 2: Query Migration Fails

**Symptoms**: Queries don't work with new collections

**Procedure**:
1. Revert query changes
2. Use legacy collections
3. Investigate query issues
4. Fix queries before retrying

**Commands**:
```bash
# Revert code changes
git revert <commit-hash>

# Queries will use legacy collections again
```

---

### Rollback Scenario 3: Performance Issues

**Symptoms**: Pipeline too slow with observability

**Procedure**:
1. Disable expensive observability features
2. Keep essential features only
3. Monitor performance
4. Optimize if needed

**Commands**:
```bash
# Disable expensive features
export GRAPHRAG_TRANSFORMATION_LOGGING=false  # Disable logging
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=false  # Disable intermediate data
export GRAPHRAG_QUALITY_METRICS=true          # Keep metrics only
```

---

## 🧪 Testing Recommendations

### Pre-Migration Testing

1. **Test Observability Pipeline**
   - Run with sample data
   - Verify collections created
   - Check data quality

2. **Test Query Compatibility**
   - Run all queries against new collections
   - Verify results match legacy
   - Check performance

3. **Test Rollback Procedures**
   - Practice rollback
   - Verify backup restore works
   - Document rollback steps

---

### Post-Migration Testing

1. **Verify Data Integrity**
   - Compare document counts
   - Sample and compare documents
   - Check for missing data

2. **Verify Query Functionality**
   - Run all queries
   - Check results
   - Monitor performance

3. **Monitor System Health**
   - Watch database metrics
   - Monitor pipeline performance
   - Check for errors

---

## ✅ Success Criteria

Migration is successful when:

- [x] New collections created successfully
- [x] All queries work with new collections
- [x] Data quality matches or exceeds legacy
- [x] Performance is acceptable
- [x] No data loss
- [x] Rollback procedures tested
- [x] Team trained on new collections

---

## 📝 Decision Matrix

| Factor | Use Legacy | Use Observability | Coexist |
|--------|-----------|------------------|---------|
| **New Project** | ❌ | ✅ Recommended | ⚠️ Optional |
| **Existing Project** | ✅ If stable | ⚠️ If needed | ✅ Recommended |
| **Need Debugging** | ❌ | ✅ Required | ✅ Recommended |
| **Need Monitoring** | ❌ | ✅ Required | ✅ Recommended |
| **Performance Critical** | ✅ Recommended | ❌ | ⚠️ Optional |
| **Limited Storage** | ✅ Recommended | ❌ | ❌ |
| **Experimentation** | ❌ | ✅ Required | ✅ Recommended |

---

## 🎯 Recommendations

### For New Projects

**Recommendation**: ✅ **Use observability collections from the start**

**Why**:
- No migration needed
- Full visibility from day one
- Better debugging and monitoring

---

### For Existing Projects (Stable)

**Recommendation**: ⚠️ **Coexist - Use both as needed**

**Why**:
- Keep stable production pipeline
- Use observability for debugging
- No migration risk

---

### For Existing Projects (Issues)

**Recommendation**: ✅ **Migrate to observability collections**

**Why**:
- Need debugging capabilities
- Want quality monitoring
- Issues require investigation

---

## 📚 Summary

**Key Takeaways**:
- Migration is **optional** - collections can coexist
- Choose migration strategy based on needs and risk tolerance
- Always backup before migration
- Test thoroughly before production deployment
- Have rollback procedures ready
- Monitor closely after migration

**Next Steps**:
1. Evaluate your situation (new project vs. existing)
2. Choose migration strategy (gradual, clean cut, or coexist)
3. Plan timeline and resources
4. Execute migration with testing and monitoring
5. Document lessons learned

---

**Document Status**: ✅ COMPLETE  
**Last Updated**: 2025-11-13  
**Next Review**: After first migration attempt


