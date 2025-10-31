# Tracing & Logging Architecture

## Overview

This document describes the current logging state of the YouTubeRAG system and outlines a comprehensive plan for integrating distributed tracing and enhanced logging infrastructure.

**Status**:

- ✅ **Phase 0 Complete**: Critical progress visibility improvements implemented (2025-10-30)
- ⏳ **Phase 1-5**: Comprehensive enhancements planned

**Last Updated**: 2025-10-30

---

## Quick Reference: Implemented Improvements (2025-10-30)

| Component                      | File                       | What Was Added                                                    | Status         | Code Location |
| ------------------------------ | -------------------------- | ----------------------------------------------------------------- | -------------- | ------------- |
| **BaseStage Progress Logging** | `core/base_stage.py`       | Initial progress log + periodic updates every 10%                 | ✅ Implemented | Lines 121-140 |
| **Clean Stage LLM Logging**    | `app/stages/clean.py`      | Start/completion logs with timing for LLM operations              | ✅ Implemented | Lines 258-296 |
| **Redundancy Stage**           | `app/stages/redundancy.py` | Detailed INFO-level logging for skipped/updated chunks            | ✅ Implemented | Lines 281-321 |
| **Trust Stage**                | `app/stages/trust.py`      | Detailed INFO-level logging for skipped/updated chunks            | ✅ Implemented | Lines 211-227 |
| **Main.py Logging Setup**      | `main.py`                  | Dual output (console+file), third-party silencing, error handling | ✅ Implemented | Lines 40-121  |

### Actual Code Changes

#### 1. `core/base_stage.py` (Lines 121-140)

**Added**:

```python
if total_docs > 0:
    self.logger.info(
        f"[{self.name}] Processing {total_docs} document(s) "
        f"(max={self.config.max if self.config.max else 'unlimited'})"
    )

for i, d in enumerate(docs):
    if self.config.max and i >= int(self.config.max):
        break
    try:
        # Log progress for batches (every 10% or every 10 items)
        if total_docs > 10 and (i + 1) % max(1, total_docs // 10) == 0:
            progress_pct = int((i + 1) / total_docs * 100)
            self.logger.info(
                f"[{self.name}] Progress: {i + 1}/{total_docs} ({progress_pct}%) "
                f"processed={self.stats['processed']} "
                f"updated={self.stats['updated']} "
                f"skipped={self.stats['skipped']} "
                f"failed={self.stats['failed']}"
            )
        self.handle_doc(d)
        self.stats["processed"] += 1
```

#### 2. `app/stages/clean.py` (Lines 258-296)

**Added**:

```python
# Log start of cleaning operation with LLM
self.logger.info(
    f"[clean] Starting LLM cleaning for {video_id} "
    f"(text_len={text_len}, est_chunks={estimated_chunks}, "
    f"workers={self.config.concurrency or 10})"
)

# Inside _llm_clean_text function (for operations with >5 chunks):
logger.info(
    f"[clean] Processing {video_id}: {num_chunks} chunks "
    f"with {max_workers} workers (this may take a while)..."
)

# After LLM calls complete:
logger.info(
    f"[clean] Completed LLM calls for {video_id}: "
    f"{num_chunks} chunks in {llm_elapsed:.1f}s "
    f"(avg {llm_elapsed/num_chunks:.2f}s/chunk)"
)

# Final completion log:
self.logger.info(
    f"[clean] Completed {video_id} → {dst_coll_name} "
    f"(llm={self.config.use_llm}, time={elapsed:.1f}s)"
)
```

#### 3. `app/stages/redundancy.py` (Lines 281-321)

**Changed** (from DEBUG to INFO):

```python
# Skip logging (changed from DEBUG to INFO):
logger.info(
    f"[redundancy] Skipping {chunk_id} (video={video_id}): "
    f"already has is_redundant={existing.get('is_redundant')}, "
    f"score={existing.get('redundancy_score', 0):.3f}"
)
self.stats["skipped"] += 1

# Update logging (enhanced with details):
logger.info(
    f"[redundancy] Updating {chunk_id} (video={video_id}): "
    f"is_redundant={is_dup}, score={best_score:.3f}, method={method}"
    + (f", duplicate_of={primary_chunk_id}" if duplicate_info else "")
)
self.stats["updated"] += 1
```

#### 4. `app/stages/trust.py` (Lines 211-227)

**Changed** (from DEBUG to INFO):

```python
# Skip logging (changed from DEBUG to INFO):
logger.info(
    f"[trust] Skipping {chunk_id} (video={video_id}): "
    f"already has trust_score={existing.get('trust_score'):.3f}"
)
self.stats["skipped"] += 1

# Update logging (enhanced with details):
logger.info(
    f"[trust] Updating {chunk_id} (video={video_id}): "
    f"trust_score={score:.3f}, method={method}"
)
self.stats["updated"] += 1
```

#### 5. `main.py` (Lines 40-121)

**Added** `setup_logging()` function:

```python
def setup_logging(verbose: bool = False, log_file: str = None) -> None:
    log_level = logging.DEBUG if verbose else logging.INFO

    # Silence noisy third-party loggers
    noisy_loggers = ["numba", "graspologic", "pymongo", "urllib3",
                     "httpx", "httpcore", "openai", "numba.core", ...]
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    # httpx at INFO for LLM visibility
    logging.getLogger("httpx").setLevel(logging.INFO)

    # Dual output: console + file
    handlers = [logging.StreamHandler(sys.stdout)]

    # File handler with error handling
    log_path = Path(log_file).resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(str(log_path), encoding="utf-8")
    handlers.append(file_handler)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
        force=True,
    )
```

**Detailed documentation**: See section [Recent Implementations (2025-10-30)](#recent-implementations-2025-10-30) below.

---

## Current Logging State

### 1. Logging Infrastructure

#### Entry Points

**`main.py`** - Primary logging setup:

- **Function**: `setup_logging(verbose, log_file)`
- **Features**:
  - Dual output: Console (stdout) + File handler
  - Configurable verbosity: `--verbose` flag enables DEBUG level
  - Timestamped log files: `logs/pipeline/ingestion_YYYYMMDD_HHMMSS.log`
  - Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
  - Third-party logger silencing (numba, pymongo, urllib3, httpx, httpcore, openai, numba.core.\*)
  - **Enhanced (2025-10-30)**:
    - Robust file path resolution with error handling
    - Graceful fallback to console-only logging if file creation fails
    - Silencing applied before and after `basicConfig` to ensure persistence
    - `httpx` specifically set to INFO level (other noisy loggers to WARNING) for LLM call visibility

**`chat.py`** - Session-based logging:

- **Function**: `setup_logger(session_id, log_dir)`
- **Features**:
  - Per-session log files: `chat_logs/{session_id}.log`
  - Separate console handler (WARNING+ only)
  - Format: `%(asctime)s | %(levelname)s | %(message)s`

**`run_graphrag_pipeline.py`** - GraphRAG pipeline logging:

- **Function**: `setup_logging(verbose)`
- **Features**:
  - Dual output: Console + `graphrag_pipeline.log`
  - Basic configuration, less sophisticated than main.py

#### Logging Patterns Across Codebase

**Base Classes**:

1. **`core/base_stage.py`**:

   ```python
   self.logger = logger or logging.getLogger(self.name)
   ```

   - Each stage gets a logger named after the stage (e.g., `clean`, `chunk`, `enrich`)
   - Logs via `self.logger.info()`, `self.logger.debug()`, `self.logger.error()`
   - **Enhanced (2025-10-30)**:
     - **Initial progress logging**: Logs total documents to process when batch starts
     - **Periodic progress updates**: Logs progress every 10% of documents (or every 10 items for smaller batches)
     - **Progress format**: `[{stage}] Progress: X/Y (Z%) processed=A updated=B skipped=C failed=D`
     - **Statistics included**: All stage stats (processed, updated, skipped, failed) in progress logs

2. **`core/base_agent.py`**:
   ```python
   logger = logging.getLogger(__name__)
   ```
   - Agent events logged at DEBUG level (model calls, retries)
   - Errors logged at WARNING level
   - Explicit logging via `log()` method (called manually)

**Stage Implementations**:

- **Clean Stage** (`app/stages/clean.py`):

  - ✅ Progress logging: Start, chunk processing, completion with timing
  - ✅ LLM operation logging: Chunk count, worker count, elapsed time
  - ✅ Skip/update logging with video_id details
  - **Enhanced (2025-10-30)**:
    - **Start logging**: `[clean] Starting LLM cleaning for {video_id} (text_len={len}, est_chunks={est}, workers={workers})`
    - **LLM processing logs**: For operations with >5 chunks, logs start and completion with timing
    - **Completion logging**: `[clean] Completed {video_id} → {collection} (llm={use_llm}, time={elapsed:.1f}s)`
    - **LLM summary**: `[clean] Completed LLM calls for {video_id}: {num_chunks} chunks in {time}s (avg {time/chunk}s/chunk)`
    - **Progress visibility**: Prevents "blind" periods during long-running LLM operations

- **Chunk Stage** (`app/stages/chunk.py`):

  - ✅ INFO: Skip existing chunks, chunk creation progress
  - ✅ Logs actual config values (upsert_existing)

- **Enrich Stage** (`app/stages/enrich.py`):

  - Uses `print()` statements (inconsistent pattern - should migrate to logger)
  - Logs concurrent LLM calls, upserting progress

- **Redundancy Stage** (`app/stages/redundancy.py`):

  - ✅ INFO: Chunk updates with scores, methods, duplicate links
  - ✅ INFO: Skipped chunks with reasons
  - ✅ Summary statistics
  - **Enhanced (2025-10-30)**:
    - **Detailed skip logging**: `[redundancy] Skipping {chunk_id} (video={video_id}): already has is_redundant={value}, score={score:.3f}`
    - **Detailed update logging**: `[redundancy] Updating {chunk_id} (video={video_id}): is_redundant={bool}, score={score:.3f}, method={method}, duplicate_of={id}`
    - **Statistics tracking**: Correctly increments `skipped` and `updated` counters
    - **Visibility**: Changed skip logs from DEBUG to INFO level for default visibility

- **Trust Stage** (`app/stages/trust.py`):
  - ✅ INFO: Chunk updates with trust scores and methods
  - ✅ INFO: Skipped chunks
  - ✅ Summary statistics
  - **Enhanced (2025-10-30)**:
    - **Detailed skip logging**: `[trust] Skipping {chunk_id} (video={video_id}): already has trust_score={score:.3f}`
    - **Detailed update logging**: `[trust] Updating {chunk_id} (video={video_id}): trust_score={score:.3f}, method={method}`
    - **Statistics tracking**: Correctly increments `skipped` and `updated` counters
    - **Visibility**: Changed skip logs from DEBUG to INFO level for default visibility

**Pipeline Orchestration**:

- **`app/pipelines/base_pipeline.py`** (`PipelineRunner`):

  - Minimal logging (could be enhanced)
  - Progress indicators: `[pipeline] (N/M) Running {stage}`
  - No detailed stage-level statistics aggregation

- **`app/pipelines/ingestion_pipeline.py`**:
  - Setup logging: Collection/index creation
  - Pipeline execution start/end
  - Configuration logging: `upsert_existing` flag propagation tracking

### 2. Current Logging Levels

| Level       | Usage                        | Examples                                                                  |
| ----------- | ---------------------------- | ------------------------------------------------------------------------- |
| **DEBUG**   | Detailed diagnostic info     | Agent model calls, LLM request/response previews, similarity calculations |
| **INFO**    | General operational messages | Stage progress, chunk updates, skip notifications, summaries              |
| **WARNING** | Warning conditions           | Failed operations with fallback, missing data, configuration issues       |
| **ERROR**   | Error conditions             | Exceptions, fatal failures, missing dependencies                          |

### 3. Log Output Locations

```
logs/
├── pipeline/
│   └── ingestion_20251030_154129.log  # Timestamped ingestion logs
├── chat_logs/
│   └── {session_id}.log              # Per-session chat logs
└── graphrag_pipeline.log             # GraphRAG pipeline logs (fixed name)
```

### 4. Log Format

**Standard Format**:

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

**Example**:

```
2025-10-30 15:41:35,685 - app.pipelines.ingestion_pipeline - INFO - Initialized IngestionPipeline with PipelineRunner
2025-10-30 15:41:38,465 - clean - INFO - [clean] Skip existing cleaned IPSaG9RRc-k
2025-10-30 15:43:17,285 - clean - INFO - [clean] Starting LLM cleaning for 9iE9Mj4m8jk (text_len=45231, est_chunks=5, workers=15)
2025-10-30 15:43:17,301 - clean - INFO - [clean] Processing 9iE9Mj4m8jk: 8 chunks with 15 workers (this may take a while)...
2025-10-30 15:43:29,542 - clean - INFO - [clean] Completed LLM calls for 9iE9Mj4m8jk: 8 chunks in 12.3s (avg 1.54s/chunk)
2025-10-30 15:43:30,125 - clean - INFO - [clean] Completed 9iE9Mj4m8jk → cleaned_transcripts (llm=True, time=14.2s)
2025-10-30 15:43:30,156 - clean - INFO - [clean] Progress: 50/500 (10%) processed=50 updated=2 skipped=48 failed=0
2025-10-30 15:45:42,891 - redundancy - INFO - [redundancy] Updating 629529fb-... (video=ZA-tUyM_y7s): is_redundant=False, score=0.897, method=cosine
2025-10-30 15:45:42,892 - trust - INFO - [trust] Updating 629529fb-... (video=ZA-tUyM_y7s): trust_score=0.061, method=heuristic
```

### 5. Recent Improvements (Implemented 2025-10-30)

#### Progress Visibility Enhancements

**Problem Solved**: During long-running operations (especially with `max=500`), users were "totally blind" with no log output for minutes at a time.

**Solutions Implemented**:

1. **BaseStage Progress Logging** (`core/base_stage.py`):

   - ✅ Initial log: `[{stage}] Processing {total} document(s) (max={max})`
   - ✅ Periodic updates: Every 10% of documents or every 10 items (whichever is more frequent)
   - ✅ Progress format includes: `processed`, `updated`, `skipped`, `failed` statistics
   - ✅ Provides visibility into batch processing progress

2. **Clean Stage LLM Operation Logging** (`app/stages/clean.py`):

   - ✅ Start log: `[clean] Starting LLM cleaning for {video_id} (text_len={len}, est_chunks={est}, workers={workers})`
   - ✅ Processing log: `[clean] Processing {video_id}: {num_chunks} chunks with {workers} workers (this may take a while)...`
   - ✅ Completion log: `[clean] Completed LLM calls for {video_id}: {num_chunks} chunks in {time}s (avg {time/chunk}s/chunk)`
   - ✅ Final log: `[clean] Completed {video_id} → {collection} (llm={use_llm}, time={elapsed:.1f}s)`
   - ✅ Prevents "blind periods" during long LLM operations

3. **Redundancy/Trust Detailed Logging**:

   - ✅ **Before**: Skip logs at DEBUG level (invisible by default)
   - ✅ **After**: Skip logs at INFO level with full context (chunk_id, video_id, scores)
   - ✅ **Before**: Update logs lacked detail
   - ✅ **After**: Update logs include chunk_id, video_id, scores, methods, duplicate_of links
   - ✅ Statistics counters correctly incremented (`skipped`, `updated`)

4. **Main.py Logging Setup** (`main.py`):
   - ✅ Comprehensive `setup_logging()` function with error handling
   - ✅ Third-party logger silencing (numba, graspologic, pymongo, etc.)
   - ✅ `httpx` set to INFO level (allows LLM API call visibility)
   - ✅ Robust file path resolution and error handling
   - ✅ Graceful fallback if file creation fails

**Impact**:

- Users can now see progress during large batch operations
- No more "blind periods" during long-running LLM calls
- Detailed chunk-level logging for debugging and verification
- Statistics accurately tracked and reported

### 6. Current Limitations

#### Remaining Issues

1. **Inconsistent Logging Patterns**:

   - Some stages use `print()` (enrich.py) instead of logger
   - Different log formats across entry points
   - No standardized context (e.g., pipeline_id, run_id, stage_id)

2. **Limited Correlation**:

   - No request/pipeline IDs to trace operations across stages
   - Difficult to correlate logs from same pipeline run
   - No parent-child relationship tracking

3. **No Structured Logging**:

   - All logs are plain text strings
   - No JSON/structured format for parsing/analysis
   - Difficult to extract metrics programmatically

4. **No Distributed Tracing**:

   - No trace IDs for LLM calls
   - Cannot track request flow through pipeline stages
   - No performance tracing across async operations

5. **Limited Context**:

   - Logs lack pipeline execution context (pipeline_id, run_id)
   - No correlation between related operations
   - Some logs missing metadata (video_id, chunk_id added recently but not standardized)

6. **No Log Aggregation**:
   - Logs scattered across multiple files
   - No centralized collection/analysis
   - No log rotation/retention policies

---

## Recent Implementations (2025-10-30) {#recent-implementations-2025-10-30}

### Progress Visibility Improvements

During testing of the ingestion pipeline with large batches (`max=500`), several critical improvements were implemented to eliminate "blind periods" during long-running operations:

#### 1. BaseStage Progress Logging

**File**: `core/base_stage.py`

**Implementation**:

- Added initial progress log when batch starts: `[{stage}] Processing {total} document(s) (max={max})`
- Periodic progress updates every 10% of documents (or every 10 items for smaller batches)
- Progress format includes all statistics: `processed={X} updated={Y} skipped={Z} failed={W}`
- Provides real-time visibility into batch processing

**Example Output**:

```
[clean] Processing 500 document(s) (max=500)
[clean] Progress: 50/500 (10%) processed=50 updated=2 skipped=48 failed=0
[clean] Progress: 100/500 (20%) processed=100 updated=5 skipped=95 failed=0
```

#### 2. Clean Stage LLM Operation Logging

**File**: `app/stages/clean.py`

**Implementation**:

- **Start log**: When LLM cleaning begins for a video
  ```python
  self.logger.info(
      f"[clean] Starting LLM cleaning for {video_id} "
      f"(text_len={text_len}, est_chunks={estimated_chunks}, "
      f"workers={self.config.concurrency or 10})"
  )
  ```
- **Processing log**: For operations with >5 chunks, logs chunk count and worker info
  ```python
  logger.info(
      f"[clean] Processing {video_id}: {num_chunks} chunks "
      f"with {max_workers} workers (this may take a while)..."
  )
  ```
- **Completion log**: After LLM calls complete, logs summary with timing
  ```python
  logger.info(
      f"[clean] Completed LLM calls for {video_id}: "
      f"{num_chunks} chunks in {llm_elapsed:.1f}s "
      f"(avg {llm_elapsed/num_chunks:.2f}s/chunk)"
  )
  ```
- **Final log**: Complete operation timing
  ```python
  self.logger.info(
      f"[clean] Completed {video_id} → {dst_coll_name} "
      f"(llm={self.config.use_llm}, time={elapsed:.1f}s)"
  )
  ```

**Impact**: Users can now see exactly which video is being processed and progress through LLM operations.

#### 3. Redundancy & Trust Stage Detailed Logging

**Files**: `app/stages/redundancy.py`, `app/stages/trust.py`

**Implementation**:

- **Skip logging** (changed from DEBUG to INFO):
  ```python
  logger.info(
      f"[redundancy] Skipping {chunk_id} (video={video_id}): "
      f"already has is_redundant={existing.get('is_redundant')}, "
      f"score={existing.get('redundancy_score', 0):.3f}"
  )
  ```
- **Update logging** (enhanced with full context):
  ```python
  logger.info(
      f"[redundancy] Updating {chunk_id} (video={video_id}): "
      f"is_redundant={is_dup}, score={best_score:.3f}, method={method}"
      + (f", duplicate_of={primary_chunk_id}" if duplicate_info else "")
  )
  ```
- **Statistics fixes**: Correctly increments `skipped` and `updated` counters

**Impact**: Users can verify in database which chunks were processed and their scores.

#### 4. Main.py Logging Infrastructure

**File**: `main.py`

**Implementation**:

- Comprehensive `setup_logging()` function with:
  - Dual output (console + file) with error handling
  - Third-party logger silencing (numba, graspologic, pymongo, urllib3, httpcore, openai)
  - `httpx` set to INFO level (allows LLM API call visibility)
  - Robust file path resolution with Path.resolve()
  - Graceful fallback to console-only if file creation fails
  - Silencing applied before and after `basicConfig` for persistence

**Key Features**:

```python
# Third-party silencing
noisy_loggers = ["numba", "graspologic", "pymongo", "urllib3", ...]
for logger_name in noisy_loggers:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

# httpx at INFO for LLM visibility
logging.getLogger("httpx").setLevel(logging.INFO)
```

**Impact**: Clean, focused logs without third-party noise, but with LLM API call visibility.

---

## Comprehensive Tracing & Logging Plan

### Phase 1: Standardize Logging Infrastructure

#### 1.1 Centralized Logging Configuration

**Create `core/logging_config.py`**:

```python
"""
Centralized logging configuration for the entire system.
Provides consistent setup across all entry points.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

class LoggingConfig:
    """Centralized logging configuration."""

    # Standard format
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Structured format (for JSON logs)
    JSON_FORMAT = {
        "timestamp": "%(asctime)s",
        "logger": "%(name)s",
        "level": "%(levelname)s",
        "message": "%(message)s",
        "module": "%(module)s",
        "function": "%(funcName)s",
        "line": "%(lineno)d",
    }

    # Noisy loggers to silence
    NOISY_LOGGERS = [
        "numba", "graspologic", "pymongo", "urllib3",
        "httpcore", "openai", "numba.core.*"
    ]

    @staticmethod
    def setup_logging(
        verbose: bool = False,
        log_file: Optional[str] = None,
        log_dir: str = "logs",
        structured: bool = False,
        json_logs: bool = False
    ) -> logging.Logger:
        """Configure logging for the application."""
        # ... implementation
        pass
```

#### 1.2 Context-Aware Logging

**Add execution context to all logs**:

```python
import contextvars
from typing import Optional

# Context variables for pipeline execution
pipeline_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('pipeline_id', default=None)
run_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('run_id', default=None)
stage_name: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('stage_name', default=None)
video_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('video_id', default=None)
chunk_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('chunk_id', default=None)

class ContextualFormatter(logging.Formatter):
    """Log formatter that includes execution context."""

    def format(self, record):
        # Add context to log record
        record.pipeline_id = pipeline_id.get()
        record.run_id = run_id.get()
        record.stage_name = stage_name.get()
        record.video_id = video_id.get()
        record.chunk_id = chunk_id.get()
        return super().format(record)
```

#### 1.3 Structured Logging

**Add JSON logging option**:

```python
import json
from typing import Dict, Any

class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add context
        if hasattr(record, 'pipeline_id'):
            log_entry["pipeline_id"] = record.pipeline_id
        if hasattr(record, 'run_id'):
            log_entry["run_id"] = record.run_id
        if hasattr(record, 'stage_name'):
            log_entry["stage_name"] = record.stage_name
        if hasattr(record, 'video_id'):
            log_entry["video_id"] = record.video_id
        if hasattr(record, 'chunk_id'):
            log_entry["chunk_id"] = record.chunk_id

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)
```

---

### Phase 2: Distributed Tracing Integration

#### 2.1 OpenTelemetry Setup

**Install dependencies**:

```bash
pip install opentelemetry-api opentelemetry-sdk
pip install opentelemetry-instrumentation-pymongo
pip install opentelemetry-instrumentation-openai
```

**Create `core/tracing.py`**:

```python
"""
Distributed tracing setup using OpenTelemetry.
"""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Status, StatusCode

# Initialize tracer provider
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({
            "service.name": "youtuberag",
            "service.version": "1.0.0",
        })
    )
)

tracer = trace.get_tracer(__name__)

# Add console exporter (for development)
# In production, use OTLP exporter to send to tracing backend
console_exporter = ConsoleSpanExporter()
span_processor = BatchSpanProcessor(console_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

def create_span(name: str, attributes: Dict[str, Any] = None):
    """Create a new tracing span."""
    return tracer.start_as_current_span(name, attributes=attributes or {})
```

#### 2.2 Instrument Pipeline Stages

**Add tracing to `BaseStage`**:

```python
from core.tracing import create_span

class BaseStage:
    def run(self, config: Optional[BaseStageConfig] = None) -> int:
        # Create span for stage execution
        with create_span(f"stage.{self.name}", attributes={
            "stage.name": self.name,
            "stage.description": self.description,
            "config.max": self.config.max,
            "config.concurrency": self.config.concurrency,
        }) as span:
            try:
                # ... existing run logic ...
                span.set_status(Status(StatusCode.OK))
                span.set_attribute("stats.processed", self.stats["processed"])
                span.set_attribute("stats.updated", self.stats["updated"])
                span.set_attribute("stats.skipped", self.stats["skipped"])
                span.set_attribute("stats.failed", self.stats["failed"])
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
```

#### 2.3 Instrument LLM Calls

**Add tracing to `BaseAgent`**:

```python
class BaseAgent:
    def call_model(self, system_prompt: str, prompt: str, **kwargs) -> str:
        with create_span("llm.call", attributes={
            "agent.name": self.name,
            "model.name": self.config.model_name,
            "prompt.length": len(prompt),
            "system_prompt.length": len(system_prompt),
        }) as span:
            try:
                # ... existing LLM call logic ...
                span.set_attribute("response.length", len(response))
                span.set_attribute("tokens.estimated", len(prompt.split()) // 4)
                return response
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
```

---

### Phase 3: Enhanced Logging Features

#### 3.1 Performance Metrics Logging

**Add performance instrumentation**:

```python
import time
from functools import wraps

def log_performance(operation_name: str):
    """Decorator to log operation performance."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.info(
                    f"[performance] {operation_name} completed in {elapsed:.3f}s",
                    extra={
                        "operation": operation_name,
                        "duration_seconds": elapsed,
                        "status": "success",
                    }
                )
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"[performance] {operation_name} failed after {elapsed:.3f}s: {e}",
                    extra={
                        "operation": operation_name,
                        "duration_seconds": elapsed,
                        "status": "error",
                        "error": str(e),
                    }
                )
                raise
        return wrapper
    return decorator
```

#### 3.2 Batch Progress Logging

**✅ IMPLEMENTED (2025-10-30)** - Enhanced progress logging in BaseStage:

**Current Implementation** (`core/base_stage.py`):

```python
class BaseStage:
    def run(self, config: Optional[BaseStageConfig] = None) -> int:
        # ... existing setup ...

        docs = list(self.iter_docs())
        total_docs = len(docs)
        if self.config.max:
            total_docs = min(total_docs, int(self.config.max))

        # ✅ IMPLEMENTED: Initial progress log
        if total_docs > 0:
            self.logger.info(
                f"[{self.name}] Processing {total_docs} document(s) "
                f"(max={self.config.max if self.config.max else 'unlimited'})"
            )

        # ✅ IMPLEMENTED: Periodic progress updates
        for i, d in enumerate(docs):
            if self.config.max and i >= int(self.config.max):
                break
            try:
                # Log progress for batches (every 10% or every 10 items)
                if total_docs > 10 and (i + 1) % max(1, total_docs // 10) == 0:
                    progress_pct = int((i + 1) / total_docs * 100)
                    self.logger.info(
                        f"[{self.name}] Progress: {i + 1}/{total_docs} ({progress_pct}%) "
                        f"processed={self.stats['processed']} "
                        f"updated={self.stats['updated']} "
                        f"skipped={self.stats['skipped']} "
                        f"failed={self.stats['failed']}"
                    )
                self.handle_doc(d)
                self.stats["processed"] += 1
            except Exception as e:
                # ... error handling ...
```

**Status**: ✅ Fully implemented and working

**Future Enhancement** (Phase 3):

- Add structured `extra` dictionary for JSON logging support
- Include pipeline_id, run_id in progress logs

#### 3.3 Error Tracking & Reporting

**Enhanced error logging**:

```python
class BaseStage:
    def handle_doc(self, doc):
        try:
            # ... document processing ...
        except Exception as e:
            self.stats["failed"] += 1
            self.logger.error(
                f"[{self.name}] Error processing document",
                exc_info=True,
                extra={
                    "stage": self.name,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "document_id": doc.get("_id"),
                    "video_id": doc.get("video_id"),
                    "chunk_id": doc.get("chunk_id"),
                    "stats": self.stats.copy(),
                }
            )
            raise
```

---

### Phase 4: Log Aggregation & Analysis

#### 4.1 Log Rotation & Retention

**Add log rotation**:

```python
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

def setup_file_handler(log_file: str, max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5):
    """Create rotating file handler."""
    handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,  # 10 MB
        backupCount=backup_count,  # Keep 5 backups
        encoding="utf-8"
    )
    return handler

# Or time-based rotation
def setup_timed_file_handler(log_file: str, when: str = "midnight", interval: int = 1, backup_count: int = 30):
    """Create time-based rotating file handler."""
    handler = TimedRotatingFileHandler(
        log_file,
        when=when,  # Rotate at midnight
        interval=interval,  # Every day
        backupCount=backup_count,  # Keep 30 days
        encoding="utf-8"
    )
    return handler
```

#### 4.2 Log Analysis Tools

**Create `scripts/analyze_logs.py`**:

```python
"""
Analyze log files to extract metrics and insights.
"""

import json
import re
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

def parse_log_file(log_path: Path) -> List[Dict]:
    """Parse log file and extract structured information."""
    logs = []
    with open(log_path) as f:
        for line in f:
            # Parse structured JSON logs or text logs
            if line.strip().startswith("{"):
                try:
                    logs.append(json.loads(line))
                except:
                    pass
            else:
                # Parse text logs with regex
                # ... implementation ...
                pass
    return logs

def extract_metrics(logs: List[Dict]) -> Dict:
    """Extract metrics from logs."""
    metrics = {
        "total_logs": len(logs),
        "by_level": defaultdict(int),
        "by_stage": defaultdict(int),
        "errors": [],
        "performance": [],
    }

    for log in logs:
        metrics["by_level"][log.get("level", "UNKNOWN")] += 1
        metrics["by_stage"][log.get("stage_name", "unknown")] += 1

        if log.get("level") == "ERROR":
            metrics["errors"].append(log)

        if "duration_seconds" in log:
            metrics["performance"].append({
                "operation": log.get("operation"),
                "duration": log.get("duration_seconds"),
            })

    return metrics
```

#### 4.3 Integration with Monitoring Tools

**Options**:

1. **Loki (Log Aggregation)**:

   - Collect logs via Promtail
   - Query with LogQL
   - Integrate with Grafana

2. **Elasticsearch + Kibana**:

   - Ship JSON logs to Elasticsearch
   - Visualize in Kibana
   - Create dashboards for pipeline metrics

3. **CloudWatch / Azure Monitor**:
   - Ship logs to cloud provider
   - Use built-in analysis tools
   - Set up alarms and dashboards

---

## Implementation Roadmap

### Phase 0: Critical Improvements (Completed 2025-10-30) ✅

**Problem**: Users were "totally blind" during long-running operations (especially with `max=500`).

**Completed**:

- ✅ Enhanced progress logging in `BaseStage.run()` - periodic updates every 10%
- ✅ LLM operation progress logging in `CleanStage` - start/completion with timing
- ✅ Detailed chunk-level logging in `RedundancyStage` and `TrustStage` - INFO level with full context
- ✅ Comprehensive logging setup in `main.py` - dual output, error handling, third-party silencing
- ✅ Statistics tracking fixes - correct increment of `skipped` and `updated` counters
- ✅ Visibility improvements - changed skip logs from DEBUG to INFO level

**Impact**: Users now have full visibility into pipeline progress, eliminating "blind periods" during long operations.

### Phase 1: Foundation (Week 1-2)

- ⏳ Create `core/logging_config.py` (centralized config)
- ⏳ Standardize logging across all entry points
- ⏳ Remove `print()` statements (enrich.py), replace with logger
- ⏳ Add context variables for execution tracking (pipeline_id, run_id)

### Phase 2: Structured Logging (Week 2-3)

- ⏳ Add JSON logging option
- ⏳ Implement contextual formatter
- ⏳ Add structured logging to all stages
- ⏳ Create log parsing utilities

### Phase 3: Distributed Tracing (Week 3-4)

- ⏳ Install OpenTelemetry dependencies
- ⏳ Create `core/tracing.py`
- ⏳ Instrument pipeline stages
- ⏳ Instrument LLM calls and MongoDB operations

### Phase 4: Enhanced Features (Week 4-5)

- ✅ **Partial**: Performance metrics logging (timing in clean stage)
- ⏳ Enhance error tracking (structured error logs)
- ⏳ Implement log rotation
- ⏳ Create log analysis scripts

### Phase 5: Integration & Monitoring (Week 5-6)

- ⏳ Choose and integrate log aggregation backend
- ⏳ Set up monitoring dashboards
- ⏳ Create alerts for critical errors
- ⏳ Document logging best practices

**Legend**: ✅ = Completed, ⏳ = Planned

---

## Configuration

### Environment Variables

```bash
# Logging configuration
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=text                   # text or json
LOG_FILE=logs/pipeline/ingestion.log
LOG_ROTATION_MAX_BYTES=10485760   # 10 MB
LOG_ROTATION_BACKUP_COUNT=5

# Structured logging
LOG_STRUCTURED=true               # Enable JSON logs
LOG_INCLUDE_CONTEXT=true          # Include execution context

# Distributed tracing
TRACING_ENABLED=true
TRACING_EXPORTER=console           # console, otlp, jaeger
TRACING_ENDPOINT=http://localhost:4317

# Log aggregation (optional)
LOG_SHIP_TO_LOKI=true
LOKI_ENDPOINT=http://localhost:3100
```

---

## Best Practices

### 1. Log Levels

- **DEBUG**: Detailed diagnostic information (LLM prompts, intermediate calculations)
- **INFO**: General operational messages (stage progress, successful operations)
- **WARNING**: Warning conditions (fallbacks, missing optional data)
- **ERROR**: Error conditions (exceptions, failures)

### 2. Log Messages

- Include relevant context (video_id, chunk_id, stage_name)
- Use structured format when possible
- Avoid logging sensitive data (API keys, tokens)
- Keep messages concise but informative

### 3. Performance

- Use appropriate log levels to avoid overhead
- Consider async logging for high-throughput scenarios
- Rotate logs regularly to manage disk space

### 4. Correlation

- Always include execution context (pipeline_id, run_id)
- Use consistent identifiers across related logs
- Link stages with parent-child relationships

---

## References

- Current Implementation: `main.py` (setup_logging), `core/base_stage.py`, `core/base_agent.py`
- Logging Documentation: Python `logging` module
- OpenTelemetry: https://opentelemetry.io/
- Structured Logging: https://www.structlog.org/

---

**Last Updated**: 2025-10-30  
**Status**: Enhancement plan, ready for implementation
