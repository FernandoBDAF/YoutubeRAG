# Library Implementation Priority - Post 13k Failure

**Date**: November 2, 2025  
**Context**: 61-hour GraphRAG run failed silently at entity_resolution  
**Learning**: Blindness to errors is the #1 problem to solve  
**Decision**: Implement observability libraries BEFORE attempting recovery

---

## 🎯 The Case Study: Why We Were Blind

### What Happened:

- Graph extraction: 61 hours, 13,051 chunks processed ✅
- Entity resolution: Started, crashed immediately ❌
- Error message logged: **EMPTY** ❌
- No traceback, no context, no clue ❌

### The Log:

```
2025-11-02 11:56:15,588 - INFO - Summary: processed=13069 updated=13051...
2025-11-02 11:56:15,596 - ERROR - Error running GraphRAG pipeline:
```

**Error message is blank!**

### Why This Happened:

**1. No Exception Type Logging**:

```python
# Current:
except Exception as e:
    logger.error(f"Error: {e}")  # Empty if e.__str__() returns ""

# Needed:
except Exception as e:
    logger.error(f"Error: {type(e).__name__}: {e}", exc_info=True)
```

**2. No Traceback Capture**:

```python
# Missing: exc_info=True parameter
# Result: No stack trace in logs
```

**3. No Stage Lifecycle Logging**:

```python
# Should have:
logger.info("Starting entity_resolution...")
# ... stage runs ...
logger.info("entity_resolution completed")
# OR
logger.error("entity_resolution failed at line X")
```

**4. No Data Verification**:

```python
# Should verify writes:
result = collection.update_one(...)
if result.modified_count == 0:
    logger.warning("Write matched but didn't modify!")
```

---

## 🔧 Critical Libraries (Solve Blindness)

### Library 1: Error Handling ⭐⭐⭐ TOP PRIORITY

**Implementation**: 10-15 hours  
**Impact**: Eliminates 90% of blindness

**What to Build**:

**1. Exception with Context** (3 hours):

```python
# core/libraries/error_handling/exceptions.py
class ApplicationError(Exception):
    def __init__(self, message, context=None, original_exception=None):
        self.message = message
        self.context = context or {}
        self.original_exception = original_exception
        super().__init__(self.format_message())

    def format_message(self):
        msg = f"{self.message}"
        if self.context:
            ctx_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            msg += f" [Context: {ctx_str}]"
        if self.original_exception:
            msg += f" [Caused by: {type(self.original_exception).__name__}: {self.original_exception}]"
        return msg

# Usage:
raise ApplicationError(
    "Entity resolution failed",
    context={'stage': 'entity_resolution', 'chunks_processed': 13051},
    original_exception=original_error
)
```

**2. Error Handler Decorator** (4 hours):

```python
# core/libraries/error_handling/decorators.py
def handle_errors(
    log_level='ERROR',
    capture_traceback=True,
    capture_context=True,
    fallback=None,
    reraise=True
):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Build comprehensive error message
                error_msg = f"{type(e).__name__}: {str(e) or '(no message)'}"

                # Add context
                if capture_context:
                    error_msg += f" [Function: {func.__name__}]"

                # Log with traceback
                logger = logging.getLogger(func.__module__)
                if capture_traceback:
                    logger.log(log_level, error_msg, exc_info=True)
                else:
                    logger.log(log_level, error_msg)

                if fallback is not None:
                    return fallback
                if reraise:
                    raise
        return wrapper
    return decorator

# Usage:
@handle_errors(capture_traceback=True, reraise=True)
def run_full_pipeline(self):
    ...
```

**3. Error Context Manager** (3 hours):

```python
# core/libraries/error_handling/context.py
class error_context:
    def __init__(self, operation, **context):
        self.operation = operation
        self.context = context

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Enhance exception with context
            enhanced_msg = f"{exc_type.__name__} in {self.operation}: {exc_val}"
            for k, v in self.context.items():
                enhanced_msg += f"\n  {k}: {v}"
            logger.error(enhanced_msg, exc_info=True)
        return False  # Re-raise

# Usage:
with error_context("entity_resolution", chunks_processed=13051, stage="entity_resolution"):
    process_entities()
# If fails: Full context logged!
```

**Total**: 10 hours  
**Critical Features**: Exception types, tracebacks, context

---

### Library 2: Tracing ⭐⭐⭐ TOP PRIORITY

**Implementation**: 10-15 hours  
**Impact**: Shows execution flow

**What to Build**:

**1. Simple Span System** (5 hours):

```python
# core/libraries/tracing/spans.py
import time
import uuid
from contextvars import ContextVar

current_trace = ContextVar('trace', default=None)

class Span:
    def __init__(self, operation, parent=None):
        self.id = str(uuid.uuid4())
        self.operation = operation
        self.parent = parent
        self.start_time = time.time()
        self.end_time = None
        self.status = 'started'
        self.error = None

    def __enter__(self):
        current_trace.set(self)
        logger.debug(f"[TRACE] Starting {self.operation} (span_id={self.id})")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time

        if exc_type is None:
            self.status = 'completed'
            logger.info(f"[TRACE] ✓ {self.operation} completed in {duration:.2f}s")
        else:
            self.status = 'failed'
            self.error = str(exc_val)
            logger.error(f"[TRACE] ✗ {self.operation} failed after {duration:.2f}s: {exc_type.__name__}")

        return False

# Usage:
with Span('graph_extraction'):
    process_chunks()
    # Logs: "[TRACE] Starting graph_extraction..."
    # Logs: "[TRACE] ✓ graph_extraction completed in 218404s"
```

**2. Trace Decorator** (3 hours):

```python
# core/libraries/tracing/decorators.py
def trace(operation=None):
    def decorator(func):
        op_name = operation or func.__name__
        def wrapper(*args, **kwargs):
            with Span(op_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage:
@trace('entity_resolution_stage')
def run_entity_resolution():
    ...
```

**3. Trace Export** (2 hours - simple JSON):

```python
# Save trace to file for analysis
traces = []
# At end: save_traces('traces.json')
```

**Total**: 10 hours  
**Critical Features**: Span timing, status tracking, hierarchical traces

---

### Library 3: Enhanced Logging ⭐⭐ HIGH

**Implementation**: 3-4 hours  
**Impact**: Better error messages immediately

**What to Add to Current Logging**:

**1. Force Tracebacks** (1 hour):

```python
# core/libraries/logging/helpers.py
def log_exception(logger, message, exception):
    """Log exception with guaranteed traceback."""
    exc_type = type(exception).__name__
    exc_msg = str(exception) or "(no message)"
    full_msg = f"{message}: {exc_type}: {exc_msg}"
    logger.error(full_msg, exc_info=True)

# Usage everywhere:
except Exception as e:
    log_exception(logger, "Entity resolution failed", e)
```

**2. Stage Lifecycle Logger** (2 hours):

```python
# core/libraries/logging/stage_logging.py
def log_stage_start(stage_name, context=None):
    logger.info(f"[STAGE] Starting {stage_name}")
    if context:
        for k, v in context.items():
            logger.info(f"  {k}: {v}")

def log_stage_complete(stage_name, stats, duration):
    logger.info(f"[STAGE] ✓ {stage_name} completed in {duration:.2f}s")
    for k, v in stats.items():
        logger.info(f"  {k}: {v}")

def log_stage_failed(stage_name, error, duration):
    logger.error(f"[STAGE] ✗ {stage_name} failed after {duration:.2f}s", exc_info=True)
```

**Total**: 3 hours

---

## 🎯 Implementation Plan (Starting Monday)

### Monday (Error Handling - Day 1)

**Time**: 6-8 hours

**Build**:

1. Exception hierarchy (ApplicationError, StageError, etc.)
2. @handle_errors decorator
3. error_context manager
4. Apply to pipeline runner
5. Test on 1 chunk

**Outcome**: See actual error messages

---

### Tuesday (Error Handling - Day 2 + Tracing Start)

**Time**: 6-8 hours

**Complete**:

1. Finish error_handling library
2. Apply to all stages
3. Start tracing library (Span class)

**Outcome**: Error handling complete

---

### Wednesday (Tracing)

**Time**: 6-8 hours

**Build**:

1. Complete Span system
2. @trace decorator
3. Apply to pipeline and stages
4. Test on 1 chunk

**Outcome**: See execution flow

---

### Thursday (Enhanced Logging + Integration)

**Time**: 4-6 hours

**Build**:

1. log_exception helper
2. Stage lifecycle logging
3. Apply everywhere
4. Test on 10 chunks

**Outcome**: Full observability

---

### Friday (Validation Test)

**Time**: 4-6 hours

**Test**:

1. Run 100-chunk test with all libraries
2. Verify error visibility
3. Verify tracing works
4. Check all logs comprehensive

**Outcome**: Confidence in observability

**Then**: Decide on 13k recovery or full re-run

---

## 📈 Before/After Comparison

### Before (Current - Blind):

```
ERROR - Error running GraphRAG pipeline:
```

**Information**: None  
**Action**: Guess and debug for hours

---

### After (With Libraries - Visible):

```
ERROR - Error running GraphRAG pipeline: ModuleNotFoundError: No module named 'graspologic'
  File: business/pipelines/runner.py, line 25, in <module>
  Trace: graphrag_pipeline > run_stages > entity_resolution (failed after 0.01s)
  Context: stage=entity_resolution, extraction_completed=13051, entities_created=0
  Stack trace:
    [full traceback showing exact line that failed]

Metrics:
  stage_completed{stage="graph_extraction"} = 1 ✅
  stage_started{stage="entity_resolution"} = 1
  stage_completed{stage="entity_resolution"} = 0 ❌
```

**Information**: Complete picture  
**Action**: Install graspologic, re-run

---

## 🎊 Conclusion

**The 61-hour failure taught us**:

1. Observability is NOT optional
2. Error handling library is CRITICAL
3. Tracing library is CRITICAL
4. Enhanced logging is CRITICAL

**Investment**: 23-34 hours  
**Benefit**: Never be blind again  
**ROI**: Infinite (prevents future 61-hour losses)

---

**My recommendation: Implement error_handling + tracing + logging enhancements (23-34 hours) BEFORE attempting any GraphRAG recovery or re-run. The extraction data is safe. Visibility is more important than rushing to process it.**

**Do you agree?**
