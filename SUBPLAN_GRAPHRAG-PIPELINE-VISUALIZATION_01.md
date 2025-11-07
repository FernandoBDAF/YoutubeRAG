# SUBPLAN: Stage Selection & Partial Runs (Achievement 0.1)

**Parent PLAN**: PLAN_GRAPHRAG-PIPELINE-VISUALIZATION.md  
**Achievement**: 0.1 - Stage Selection & Partial Runs Implemented  
**Status**: ✅ Complete  
**Created**: 2025-11-06 23:30 UTC

---

## 🎯 Objective

Implement flexible stage selection for the GraphRAG pipeline, allowing users to:

- Run specific stages by name (e.g., `--stages extraction,resolution`)
- Run stage ranges (e.g., `--stages 1-3`)
- Validate stage dependencies automatically
- Support partial pipeline runs efficiently

---

## 📋 Files to Modify/Create

### Files to Modify

1. **`business/pipelines/graphrag.py`**:

   - Add `run_stages()` method to accept list of stage names/indices
   - Add `_parse_stage_selection()` to parse stage list/ranges
   - Add `_get_stage_dependencies()` to define dependencies
   - Modify `_create_stage_specs()` to accept optional stage filter

2. **`app/cli/graphrag.py`**:

   - Add `--stages` argument (comma-separated list or range)
   - Update argument parsing to handle stage selection
   - Pass stage selection to pipeline config

3. **`core/config/graphrag.py`** (if needed):
   - Add `stages` field to `GraphRAGPipelineConfig` (optional list)

### Files to Create

1. **`tests/business/pipelines/test_graphrag_stage_selection.py`**:
   - Test stage selection by name
   - Test stage selection by range
   - Test dependency validation
   - Test partial pipeline execution

---

## 🔧 Approach

### 1. Define Stage Dependencies

```python
STAGE_DEPENDENCIES = {
    "graph_extraction": [],  # No dependencies
    "entity_resolution": ["graph_extraction"],
    "graph_construction": ["entity_resolution"],
    "community_detection": ["graph_construction"],
}
```

### 2. Parse Stage Selection

Support formats:

- `--stages extraction,resolution` (names)
- `--stages 1-3` (range)
- `--stages 1,2,4` (indices)
- `--stages graph_extraction,entity_resolution` (full names)

### 3. Validate Dependencies

- Check if selected stages have dependencies met
- Auto-include dependencies if needed (or error)
- Warn if running out of order

### 4. Filter Stage Specs

- Filter `self.specs` based on selection
- Maintain order
- Pass filtered specs to `PipelineRunner`

---

## ✅ Tests Required

1. **Test stage selection by name**:
   - `--stages extraction,resolution` → runs only those 2 stages
2. **Test stage selection by range**:
   - `--stages 1-3` → runs stages 1, 2, 3
3. **Test dependency auto-inclusion**:
   - `--stages resolution` → auto-includes extraction
4. **Test dependency validation**:
   - `--stages construction` without resolution → error or auto-include
5. **Test invalid stage names**:
   - `--stages invalid_stage` → clear error message
6. **Test empty selection**:
   - `--stages ""` → runs full pipeline (backward compatible)

---

## 🚀 Implementation Steps

1. Write tests first (TDD)
2. Add stage dependencies constant
3. Implement `_parse_stage_selection()` method
4. Implement `_get_stage_dependencies()` method
5. Implement `_validate_stage_dependencies()` method
6. Modify `_create_stage_specs()` to filter stages
7. Add `run_stages()` method
8. Update CLI to accept `--stages` argument
9. Run tests and verify
10. Update documentation

---

## 📝 Success Criteria

- ✅ Can run partial pipeline: `--stages extraction,resolution`
- ✅ Can run stage range: `--stages 1-3`
- ✅ Dependencies automatically included or validated
- ✅ Clear error messages for invalid selections
- ✅ Backward compatible (no `--stages` = full pipeline)
- ✅ All tests passing

---

## 🔗 Related

- **Parent PLAN**: PLAN_GRAPHRAG-PIPELINE-VISUALIZATION.md
- **Next Achievement**: 0.2 - Resume from Failure
- **Dependencies**: None (foundation feature)

---

**Status**: Ready for execution  
**Next**: Create EXECUTION_TASK and start implementation
