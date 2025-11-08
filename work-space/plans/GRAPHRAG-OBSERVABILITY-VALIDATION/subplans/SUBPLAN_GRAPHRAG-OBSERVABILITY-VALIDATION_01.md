# SUBPLAN: Collection Name Compatibility Resolved

**Parent PLAN**: PLAN_GRAPHRAG-OBSERVABILITY-VALIDATION.md  
**Achievement**: 0.1  
**Status**: 🚀 Ready to Execute  
**Created**: 2025-11-10  
**Estimated Effort**: 3-4 hours  

---

## 🎯 Objective

Resolve collection name mismatch between legacy infrastructure (entities, relations, communities) and new observability infrastructure (entities_resolved, relations_final, transformation_logs, intermediate collections) by implementing Option C (coexistence approach) that allows both schemas to function without conflicts.

---

## 📋 Deliverables (Required)

**Primary Deliverables**:

1. **Updated `core/config/paths.py`**
   - Add new collection constants
   - Document legacy vs new collection names
   - Include migration documentation
   - Add enum or constants for collection grouping

2. **Collection Compatibility Documentation**
   - Mapping matrix (legacy ↔ new collections)
   - Usage patterns by domain (GraphRAG stages, services, tools)
   - Coexistence strategy explanation
   - Backward compatibility notes

3. **Migration Guide (if needed)**
   - How to support both legacy and new collections
   - Transition strategy for existing pipelines
   - Data consistency considerations

4. **Verification Test Results**
   - Imports verification (all files importing from paths.py still work)
   - Stage compatibility check (all stages use correct collections)
   - Legacy query verification (old queries still function)
   - New service verification (new services use new collections)

---

## 🎯 Context & Prerequisites

**What Exists**:
- Legacy collections in MongoDB: `entities`, `relations`, `communities` 
- New infrastructure code expects: `entities_resolved`, `relations_final`, `transformation_logs`, intermediate collections
- Current `core/config/paths.py` defines only legacy collection names
- New services (TransformationLogger, IntermediateDataService, QualityMetricsService) need new collection names

**Why This Matters**:
- Query scripts cannot access data without correct collection names
- Pipeline stages may fail if collection names don't match
- Observability tools cannot function without proper collection configuration
- Backward compatibility needed for existing data

---

## 📊 Execution Strategy

### Phase 1: Analysis (30-45 minutes)

**Step 1.1**: Audit current state
- Read `core/config/paths.py` fully (document all constants)
- Search for all imports of `core.config.paths` in codebase
- Identify all references to legacy collection names
- Create usage map (which files use which collections)

**Step 1.2**: Identify new collection needs
- Scan new observability services for collection references
- List all new collection names expected
- Identify collection usage in stages
- Document schema differences (legacy vs new)

**Step 1.3**: Document compatibility matrix
- Create matrix: Collection Name → Legacy/New/Both → Used By → Purpose
- Identify conflicts or overlaps
- Note any special handling needed

### Phase 2: Implementation (1.5-2 hours)

**Step 2.1**: Update `core/config/paths.py`
- Add new collection constants (COLL_ENTITIES_RESOLVED, COLL_RELATIONS_FINAL, etc.)
- Organize constants by category (legacy, new, intermediate)
- Add clear comments distinguishing purpose
- Include migration documentation as docstring

**Step 2.2**: Create compatibility documentation
- Write markdown document with collection matrix
- Explain coexistence strategy (Option C rationale)
- Document usage patterns by domain
- Add examples of correct collection usage

**Step 2.3**: Verify imports and usage
- Check that new services have access to new collection constants
- Ensure stages import correctly
- Update any hardcoded collection names to use constants

### Phase 3: Verification (45-60 minutes)

**Step 3.1**: Test imports
- Verify all Python files importing from paths.py still import successfully
- Check that new constants are accessible
- Ensure no import errors

**Step 3.2**: Stage compatibility test
- Check that extraction, entity_resolution, graph_construction stages still work
- Verify they use correct collection names (legacy for existing, new for new features)
- Test that both legacy and new collections can be queried

**Step 3.3**: Query verification
- Test that legacy queries still work (read from old collections)
- Test that new query scripts can find new collections
- Verify no collection conflicts

---

## 📋 Approach

### Strategy: Option C - Coexistence

Why this approach:
- **Least disruptive**: Existing data and code remain unchanged
- **Backward compatible**: Legacy pipelines continue working
- **Forward compatible**: New infrastructure can grow independently
- **Flexible**: Can migrate gradually as needed

Implementation:
- Keep all legacy collection constants in `paths.py`
- Add new collection constants separately
- Services choose which collections to use
- No renaming or migration required initially
- Both schemas can coexist in same MongoDB instance

### Code Changes Scope

**File 1**: `core/config/paths.py`
- Add ~30-40 lines for new collection constants
- Add ~50-100 lines of documentation
- Add enum or grouping for organization

**Files 2**: New documentation files
- `Collection Compatibility Matrix.md` (~200 lines)
- `Collection Usage Patterns.md` (~150 lines)
- Migration guide (if needed) (~100 lines)

**Files 3**: No code changes needed in stages/services
- They already import from paths.py
- Just need new constants available

---

## ✅ Testing Plan

### Test 1: Import Verification
```bash
python -c "from core.config.paths import *; print('✓ All imports successful')"
```
Expected: No import errors, all collection constants accessible

### Test 2: Legacy Stage Compatibility
```bash
# Run extraction stage (uses legacy collections)
python app/cli/graphrag.py --stage graph_extraction --max 5 --verbose
```
Expected: Stage runs without errors, queries legacy collections successfully

### Test 3: New Service Access
```python
# Verify new services can access new collection constants
from core.config.paths import COLL_ENTITIES_RESOLVED, COLL_TRANSFORMATION_LOGS
print(f"New collections accessible: {COLL_ENTITIES_RESOLVED}, {COLL_TRANSFORMATION_LOGS}")
```
Expected: New constants available and accessible

### Test 4: Query Verification
```bash
# Test that both legacy and new collections can be queried
python scripts/repositories/graphrag/query_entities.py --limit 5
python scripts/repositories/graphrag/stats_summary.py
```
Expected: Legacy queries work with existing data

---

## 📈 Expected Results

**After Completion**:

1. ✅ `core/config/paths.py` contains both legacy and new collection constants
2. ✅ All legacy collection references continue working
3. ✅ New services have access to new collection constants
4. ✅ Collection compatibility documented clearly
5. ✅ No code breaks from this change
6. ✅ Coexistence verified working
7. ✅ Clear migration path documented

**Success Metrics**:
- 0 import errors in codebase
- All legacy code continues working
- New constants accessible to new services
- Matrix document created and verified
- Verification tests pass

---

## 🔄 Contingencies

**If legacy code breaks**:
- Revert changes to paths.py
- Add new constants without removing old ones
- Ensure no naming conflicts

**If new services can't access constants**:
- Check import paths
- Verify paths.py has new constants defined
- Update service imports if needed

**If collection conflicts found**:
- Use different collection names
- Add prefix to distinguish (e.g., `observability_entities`)
- Document strategy clearly

---

## 📝 Documentation

### Inline Code Comments
- Explain why both legacy and new collections exist
- Document collection name conventions
- Add examples of correct usage

### Markdown Deliverables
1. **Collection Compatibility Matrix**: Table showing all collections, their purpose, and usage
2. **Usage Patterns**: Examples of how different parts use different collections
3. **Coexistence Strategy**: Explanation of why Option C and how it works

---

## ⏱️ Time Breakdown (Estimated)

- Phase 1 (Analysis): 30-45 minutes
- Phase 2 (Implementation): 1.5-2 hours  
- Phase 3 (Verification): 45-60 minutes
- Phase 4 (Documentation): 30-45 minutes
- **Total**: 3-4 hours

---

## 🎓 Success Criteria

**Must Have**:
- ✅ New collection constants added to paths.py
- ✅ Legacy collection constants still work
- ✅ No import errors in codebase
- ✅ Legacy queries still function
- ✅ Compatibility matrix documented

**Should Have**:
- ✅ Migration guide created
- ✅ Best practices documented
- ✅ Verification tests all pass

**Nice to Have**:
- ✅ Automated verification script
- ✅ Examples in documentation
- ✅ Visual diagram of collection relationships

---

## 📚 References

**Files to Review**:
- `core/config/paths.py` - Current collection definitions
- `core/base/stage.py` - How stages use collections
- `business/services/graphrag/transformation_logger.py` - New service needs
- `scripts/repositories/graphrag/query_entities.py` - Query patterns

**Related Documentation**:
- Parent PLAN: PLAN_GRAPHRAG-OBSERVABILITY-VALIDATION.md
- Parent PLAN parent: PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md
- Observability Services Guide: `documentation/guides/OBSERVABILITY-SERVICES.md`

---

**Status**: 🚀 Ready to Execute  
**Next Step**: Create EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_01_01.md


