# GraphRAG Pipeline Pre-Test Review

**Date**: 2025-10-30  
**Purpose**: Review `graphrag_pipeline.py` and related files to prevent issues encountered during `ingestion_pipeline.py` testing.

---

## Issues Fixed in Ingestion Pipeline (Reference)

1. ✅ **Progress visibility** - Added periodic progress logs in `BaseStage` (every 10%)
2. ✅ **LLM operation logging** - Added start/completion logs in `CleanStage`
3. ✅ **Logging setup** - Enhanced `main.py` with dual output, third-party silencing, error handling
4. ✅ **Skip/update logging** - Changed from DEBUG to INFO level in `RedundancyStage`/`TrustStage`
5. ✅ **Statistics tracking** - Fixed `skipped`/`updated` counter increments
6. ✅ **Log file handling** - Timestamped files, robust path resolution, graceful fallback

---

## Issues Found in GraphRAG Pipeline

### 🔴 CRITICAL: Logging Setup Issues

#### 1. `run_graphrag_pipeline.py` - Basic Logging Setup

**Location**: Lines 29-45

**Current Code**:

```python
def setup_logging(verbose: bool = False) -> None:
    log_level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("graphrag_pipeline.log"),
        ],
    )
```

**Problems**:

- ❌ **No third-party logger silencing** (numba, graspologic, pymongo, urllib3, etc.)
- ❌ **Fixed filename** - not timestamped (will overwrite on each run)
- ❌ **No error handling** - file creation may fail silently
- ❌ **No log directory creation** - will fail if directory doesn't exist
- ❌ **No `--log-file` argument** - can't specify custom log file location
- ❌ **httpx not set to INFO** - LLM API calls won't be visible

**Recommended Fix**: Use the same `setup_logging()` pattern from `main.py`

#### 2. `graphrag_pipeline.py` **main** Block - Minimal Logging

**Location**: Lines 302-304

**Current Code**:

```python
# Configure logging
log_level = logging.DEBUG if args.verbose else logging.INFO
logging.basicConfig(level=log_level)
```

**Problems**:

- ❌ **No file handler** - logs only to console
- ❌ **No third-party silencing** - will be noisy with numba/graspologic
- ❌ **No formatting** - minimal log format

**Note**: This is less critical if users always use `run_graphrag_pipeline.py`, but should still be fixed.

---

### 🟡 MEDIUM: Progress Visibility

#### 3. GraphRAG Stages May Have Long LLM Operations

**Stages Affected**:

- `graph_extraction.py` - LLM-based entity/relationship extraction
- `entity_resolution.py` - LLM-based entity resolution
- `graph_construction.py` - Relationship resolution
- `community_detection.py` - Community summarization (LLM)

**Current State**:

- ✅ **BaseStage progress logging** - Inherited automatically (periodic updates every 10%)
- ⚠️ **LLM operation logging** - May need similar improvements as `CleanStage`

**Check Needed**: Do GraphRAG stages have long-running LLM operations that need start/completion logging?

**Example from CleanStage** (for reference):

```python
# Start log
self.logger.info(
    f"[clean] Starting LLM cleaning for {video_id} "
    f"(text_len={text_len}, est_chunks={estimated_chunks}, "
    f"workers={self.config.concurrency or 10})"
)

# Processing log (for >5 chunks)
logger.info(
    f"[clean] Processing {video_id}: {num_chunks} chunks "
    f"with {max_workers} workers (this may take a while)..."
)

# Completion log
logger.info(
    f"[clean] Completed LLM calls for {video_id}: "
    f"{num_chunks} chunks in {llm_elapsed:.1f}s "
    f"(avg {llm_elapsed/num_chunks:.2f}s/chunk)"
)
```

---

### 🟡 MEDIUM: Skip/Update Logging Visibility

#### 4. GraphRAG Stages Skip Logging

**Stages Affected**:

- `graph_extraction.py` - May skip already-extracted chunks
- `entity_resolution.py` - May skip already-resolved entities
- `graph_construction.py` - May skip already-constructed relationships
- `community_detection.py` - May skip already-detected communities

**Check Needed**:

- Are skip logs at DEBUG level (invisible by default)?
- Are update logs detailed enough (include chunk_id, video_id, scores)?

**Example from RedundancyStage** (for reference):

```python
# Skip logging (INFO level, not DEBUG)
logger.info(
    f"[redundancy] Skipping {chunk_id} (video={video_id}): "
    f"already has is_redundant={existing.get('is_redundant')}, "
    f"score={existing.get('redundancy_score', 0):.3f}"
)

# Update logging (detailed)
logger.info(
    f"[redundancy] Updating {chunk_id} (video={video_id}): "
    f"is_redundant={is_dup}, score={best_score:.3f}, method={method}"
)
```

---

### 🟢 LOW: Statistics Tracking

#### 5. Statistics Counter Increments

**Check Needed**: Do GraphRAG stages correctly increment `skipped` and `updated` counters?

**Example from TrustStage** (for reference):

```python
# When skipping
self.stats["skipped"] += 1

# When updating
self.stats["updated"] += 1
```

---

### 🟢 LOW: Configuration Consistency

#### 6. GraphRAG Pipeline Configuration

**Location**: `config/graphrag_config.py` - `GraphRAGPipelineConfig.from_args_env()`

**Check Needed**:

- Does `upsert_existing` flag propagate correctly to all stage configs?
- Are there any missing configuration overrides similar to `ingestion_pipeline.py`?

**Reference from IngestionPipeline**:

```python
# Apply upsert_existing flag to all stages if provided
upsert_existing = getattr(args, "upsert_existing", False)
if upsert_existing:
    clean_config.upsert_existing = True
    enrich_config.upsert_existing = True
    # ... etc
```

---

## Recommended Fixes

### Priority 1: Fix Logging Setup (Before Testing)

**File**: `run_graphrag_pipeline.py`

**Action**: Replace `setup_logging()` function with enhanced version from `main.py`:

```python
def setup_logging(verbose: bool = False, log_file: str = None) -> None:
    """
    Set up logging configuration for GraphRAG pipeline.

    Args:
        verbose: Enable verbose (DEBUG) logging
        log_file: Optional path to log file (default: logs/pipeline/graphrag_TIMESTAMP.log)
    """
    from pathlib import Path
    import sys
    from datetime import datetime

    log_level = logging.DEBUG if verbose else logging.INFO

    # Silence noisy third-party loggers FIRST
    noisy_loggers = [
        "numba",
        "graspologic",
        "pymongo",
        "urllib3",
        "httpx",
        "httpcore",
        "openai",
        "numba.core",
        "numba.core.ssa",
        "numba.core.byteflow",
        "numba.core.interpreter",
    ]
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    # Create log directory if needed
    if log_file is None:
        log_dir = Path("logs/pipeline")
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = str(log_dir / f"graphrag_{timestamp}.log")

    # Configure logging with both console and file handlers
    handlers = [logging.StreamHandler(sys.stdout)]

    # Add file handler with error handling
    log_file_path = None
    log_file_error = None
    try:
        log_path = Path(log_file).resolve()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(log_path), encoding="utf-8")
        handlers.append(file_handler)
        log_file_path = str(log_path)
    except Exception as e:
        log_file_error = str(e)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
        force=True,
    )

    # Re-apply silencing after basicConfig
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    # httpx at INFO for LLM visibility
    logging.getLogger("httpx").setLevel(logging.INFO)

    logger = logging.getLogger(__name__)
    if log_file_path:
        logger.info(
            f"Logging configured: level={logging.getLevelName(log_level)}, file={log_file_path}"
        )
    else:
        if log_file and log_file_error:
            logger.warning(
                f"Failed to create log file '{log_file}': {log_file_error}. "
                f"Continuing with console logging only."
            )
        logger.info(
            f"Logging configured: level={logging.getLevelName(log_level)}, file=console only"
        )
```

**Also**: Add `--log-file` argument to parser:

```python
parser.add_argument(
    "--log-file",
    help="Path to log file (default: logs/pipeline/graphrag_TIMESTAMP.log)",
)
```

**Update**: Call `setup_logging()` with log_file:

```python
setup_logging(args.verbose, getattr(args, "log_file", None))
```

### Priority 2: Review GraphRAG Stage Logging

**Action**: Review each GraphRAG stage for:

1. LLM operation logging (start/completion)
2. Skip logging level (should be INFO, not DEBUG)
3. Update logging detail (include chunk_id, video_id)
4. Statistics counter increments

**Files to Review**:

- `app/stages/graph_extraction.py`
- `app/stages/entity_resolution.py`
- `app/stages/graph_construction.py`
- `app/stages/community_detection.py`

### Priority 3: Fix graphrag_pipeline.py **main** Block

**Action**: Remove or enhance the `__main__` block logging, or add a comment that users should use `run_graphrag_pipeline.py` instead.

---

## Testing Checklist

Before running tests, verify:

- [ ] `run_graphrag_pipeline.py` uses enhanced logging setup
- [ ] Third-party loggers are silenced
- [ ] Log files are timestamped
- [ ] `--log-file` argument works
- [ ] GraphRAG stages show progress (BaseStage inherited)
- [ ] Skip/update logs are visible (INFO level)
- [ ] Statistics counters increment correctly
- [ ] Long LLM operations have start/completion logs

---

## Summary

**Critical Issues** (Fix Before Testing):

1. 🔴 Logging setup in `run_graphrag_pipeline.py` - Missing third-party silencing, error handling, timestamped files
2. 🔴 No `--log-file` argument support

**Medium Priority** (Fix Soon): 3. 🟡 Review GraphRAG stage logging (skip/update visibility) 4. 🟡 LLM operation logging in GraphRAG stages

**Low Priority** (Verify During Testing): 5. 🟢 Statistics tracking verification 6. 🟢 Configuration consistency check

---

**Recommendation**: Fix Priority 1 issues before starting tests to avoid the same "blind periods" and logging visibility issues encountered during ingestion pipeline testing.
