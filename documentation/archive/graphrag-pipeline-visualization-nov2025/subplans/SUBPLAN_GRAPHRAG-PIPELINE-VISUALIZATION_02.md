# SUBPLAN: Resume from Failure (Achievement 0.2)

**Parent PLAN**: PLAN_GRAPHRAG-PIPELINE-VISUALIZATION.md  
**Achievement**: 0.2 - Resume from Failure Implemented  
**Status**: ✅ Complete  
**Created**: 2025-11-06 23:50 UTC  
**Completed**: 2025-11-06 23:55 UTC

---

## 🎯 Objective

Implement resume capability for the GraphRAG pipeline, allowing users to:

- Detect which stages have already completed (by checking chunk status in DB)
- Skip completed stages automatically
- Resume from the first incomplete stage
- Support `--resume` flag in CLI

---

## 📋 Files to Modify/Create

### Files to Modify

1. **`business/pipelines/graphrag.py`**:

   - Add `_detect_completed_stages()` method to check DB for completion status
   - Add `_get_last_completed_stage()` method
   - Modify `run_full_pipeline()` to support resume mode
   - Add `run_with_resume()` method

2. **`app/cli/graphrag.py`**:

   - Add `--resume` argument
   - Pass resume flag to pipeline config
   - Handle resume logic in main()

3. **`core/config/graphrag.py`**:
   - Add `resume_from_failure: bool = False` field

### Files to Create

1. **`tests/business/pipelines/test_graphrag_resume.py`**:
   - Test detecting completed stages
   - Test resume skips completed stages
   - Test resume from middle stage
   - Test resume when all stages complete

---

## 🔧 Approach

### 1. Detect Completed Stages

Each stage marks completion in chunk documents:

- `graphrag_extraction.status: "completed"`
- `graphrag_resolution.status: "completed"`
- `graphrag_construction.status: "completed"`
- `graphrag_communities.status: "completed"`

Strategy:

- Query chunks collection for completion status
- Check percentage of chunks with each stage completed
- Consider stage complete if >95% of chunks have status="completed"

### 2. Determine Last Completed Stage

- Check stages in order (extraction → resolution → construction → detection)
- Find first stage that is NOT complete
- Resume from that stage

### 3. Resume Logic

- If `--resume` flag is set:
  - Detect completed stages
  - Filter stage specs to only include incomplete stages
  - Run filtered pipeline

---

## ✅ Tests Required

1. **Test detecting completed stages**:
   - Mock DB with chunks having extraction completed
   - Verify detection returns extraction as complete
2. **Test resume skips completed stages**:
   - Mock DB with extraction and resolution completed
   - Resume should skip those, start from construction
3. **Test resume from middle stage**:
   - Mock DB with only extraction completed
   - Resume should start from resolution
4. **Test resume when all complete**:
   - Mock DB with all stages completed
   - Resume should detect and skip all (or warn)
5. **Test resume with no completed stages**:
   - Mock DB with no stages completed
   - Resume should run all stages (same as normal run)

---

## 🚀 Implementation Steps

1. Write tests first (TDD)
2. Implement `_detect_stage_completion()` method
3. Implement `_get_last_completed_stage()` method
4. Implement `_should_skip_stage()` method
5. Modify `run_full_pipeline()` to support resume
6. Add `--resume` CLI argument
7. Update config with resume flag
8. Run tests and verify
9. Update documentation

---

## 📝 Success Criteria

- ✅ Can detect which stages have completed from DB
- ✅ Resume automatically skips completed stages
- ✅ Resume starts from first incomplete stage
- ✅ Clear logging of which stages are skipped
- ✅ Backward compatible (no `--resume` = normal behavior)
- ✅ All tests passing

---

## 🔗 Related

- **Parent PLAN**: PLAN_GRAPHRAG-PIPELINE-VISUALIZATION.md
- **Previous Achievement**: 0.1 - Stage Selection (leverages stage filtering)
- **Next Achievement**: 0.3 - Stage Dependency Validation (already implemented in 0.1)

---

**Status**: ✅ Complete

## ✅ Implementation Summary

- Implemented `_detect_stage_completion()` to check DB for completion status
- Implemented `_get_last_completed_stage()` to find last completed stage
- Implemented `_get_stages_to_run()` to filter incomplete stages
- Implemented `run_with_resume()` to orchestrate resume logic
- Modified `run_full_pipeline()` to support resume parameter
- Added `--resume` CLI argument
- Added `resume_from_failure` config field
- Created comprehensive test suite (11 tests, all passing)

**Tests**: All 11 tests passing

- Stage completion detection (all, partial, none)
- Last completed stage detection
- Stages to run filtering
- Resume logic (skips completed, handles all complete)
