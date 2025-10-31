# Known Bugs & Issues

## Critical Bugs

### 1. `--upsert-existing` Flag Not Working

**Status**: 🔴 Active  
**Priority**: Medium  
**First Identified**: 2025-10-30

**Description**:  
The `--upsert-existing` flag is not being passed correctly from `main.py` to `IngestionPipeline.from_cli_args()`. When the flag is provided on the command line, it's not recognized in the pipeline configuration.

**Evidence from Logs**:

```
2025-10-30 15:37:17,304 - app.pipelines.ingestion_pipeline - INFO - Checking upsert_existing: args.upsert_existing=False, redundancy_config.upsert_existing=False
```

Even when `--upsert-existing` is passed, `args.upsert_existing` shows as `False`.

**Root Cause**:  
In `main.py`, the `run_stage("pipeline", ...)` function creates a new `argparse.Namespace()` object (`args_obj`) and only copies specific attributes from the parsed arguments (`args`). The `upsert_existing` attribute is never copied from `args` to `args_obj` before passing it to `IngestionPipeline.from_cli_args()`.

**Location**:

- `main.py` lines ~198-238 in `run_stage("pipeline", ...)`
- The `args_obj` namespace doesn't include `upsert_existing` from `args`

**Fix Required**:  
Pass `upsert_existing` from the parsed `args` to `run_stage()` as a kwarg, and then copy it to `args_obj` before calling `IngestionPipeline.from_cli_args()`.

**Proposed Fix**:

1. In `main()` when calling `run_stage("pipeline", ...)` (around line 368):

```python
elif args.cmd == "pipeline":
    cli_args = []
    # ... existing cli_args setup ...
    pipeline_verbose = getattr(args, "verbose", False)
    pipeline_upsert_existing = getattr(args, "upsert_existing", False)  # ADD THIS
    run_stage("pipeline", args=cli_args, verbose=pipeline_verbose, upsert_existing=pipeline_upsert_existing)  # ADD upsert_existing
```

2. In `run_stage("pipeline", ...)` when creating `args_obj` (around line 207):

```python
args_obj.verbose = kwargs.get("verbose", False)
args_obj.upsert_existing = kwargs.get("upsert_existing", False)  # ADD THIS
args_obj.dry_run = kwargs.get("dry_run", False)
```

**Impact**:

- Cannot force re-processing of existing documents via CLI flag
- Users must manually modify configuration or use environment variables
- Workaround: Set `UPSERT_EXISTING=true` environment variable (if supported)

**Related Files**:

- `main.py`: Argument parsing and passing
- `app/pipelines/ingestion_pipeline.py`: Configuration reading
- `config/stage_config.py`: BaseStageConfig.from_args_env()

---

## Minor Issues

### 2. Hardcoded `upsert_existing=False` in Chunk Stage Log

**Status**: ✅ Fixed  
**Priority**: Low  
**Fixed**: 2025-10-30

**Description**:  
The chunk stage had a hardcoded log message showing `upsert_existing=False` even when the config value was different. Fixed by using the actual config value.

**Fix Applied**:  
Changed from `f"[chunk] Skip existing chunks {video_id} (upsert_existing=False)"` to `f"[chunk] Skip existing chunks {video_id} (upsert_existing={self.config.upsert_existing})"` in `app/stages/chunk.py` line 126.

---

### 3. No Progress Logging During Long-Running LLM Operations

**Status**: ✅ Fixed  
**Priority**: High  
**Fixed**: 2025-10-30

**Description**:  
When processing large batches (e.g., `max=500`), stages with LLM calls (especially `clean`) would run for minutes without any log output, leaving users "totally blind" about what was happening.

**Evidence**:  
User reported: "I am running with max 500 and it got stuck for more than 1 minute and I was totally blind without any logs information"

**Root Cause**:

- `clean` stage had no logging between starting to process a video and finishing (which could take 10-30+ seconds per video with LLM)
- `BaseStage.run()` didn't show progress during batch processing
- Long-running LLM operations in `_llm_clean_text()` had no intermediate status updates

**Fix Applied**:

1. **`app/stages/clean.py`**:

   - Added start log: `"[clean] Starting LLM cleaning for {video_id} (text_len=..., est_chunks=..., workers=...)"`
   - Added progress log in `_llm_clean_text()` for operations with >5 chunks
   - Added completion log with timing: `"[clean] Completed {video_id} → ... (time={elapsed:.1f}s)"`
   - Added LLM completion summary for large operations: `"[clean] Completed LLM calls for {video_id}: {num_chunks} chunks in {elapsed:.1f}s"`

2. **`core/base_stage.py`**:
   - Added initial log showing total documents to process
   - Added periodic progress logs (every 10% of documents or every 10 items)
   - Progress logs show: `"{stage} Progress: X/Y (Z%) processed=A updated=B skipped=C failed=D"`

**Impact**:

- Users can now see:
  - Which video is being processed
  - How many chunks/items are being processed
  - Progress percentage during large batches
  - Completion times for operations
- Reduces anxiety during long-running operations
- Enables better debugging and performance monitoring

**Related Files**:

- `app/stages/clean.py`: Added LLM operation progress logging
- `core/base_stage.py`: Added batch progress logging

---

## Notes

- All bugs should be prioritized and tracked here before implementation
- Include log snippets, code locations, and proposed fixes for reproducibility
- Mark bugs as "Fixed" with date when resolved
