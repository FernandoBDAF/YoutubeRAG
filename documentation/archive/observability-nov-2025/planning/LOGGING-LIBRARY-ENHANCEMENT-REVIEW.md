# Logging Library Enhancement Review

**Date**: November 3, 2025  
**Goal**: Review logging library for gaps and enhancement opportunities

---

## ✅ What Logging Library Currently Has

### Files:
```
core/libraries/logging/
├── __init__.py          # 20 exports
├── setup.py             # setup_logging, get_logger, etc.
├── formatters.py        # JSON, Colored, Compact formatters
├── context.py           # Log context propagation
├── operations.py        # log_operation_context/complete ✅ ADDED
└── exceptions.py        # log_exception ✅ ADDED
```

**Exports**: 20 functions

---

## 🔍 Gap Analysis

### Gap 1: No File Rotation

**Current**: Logs to single file, grows indefinitely

**Issue**: Long-running processes → huge log files

**Solution**:
```python
# Add to setup.py
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

def setup_logging(..., rotate_logs=True, max_bytes=10_000_000, backup_count=5):
    if rotate_logs:
        handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,  # 10MB default
            backupCount=backup_count
        )
    else:
        handler = logging.FileHandler(log_file)
```

**Priority**: Medium (good for production)  
**Effort**: 30 minutes

---

### Gap 2: No Structured Logging to Loki

**Current**: Plain text logs

**Needed for Loki**: JSON formatted logs with labels

**Solution**:
```python
# Enhance JSONFormatter in formatters.py
class LokiFormatter(JSONFormatter):
    """JSON formatter optimized for Grafana Loki."""
    def format(self, record):
        log_data = super().format(record)
        # Add Loki-specific fields
        log_data['stream'] = {
            'service': 'youtuberag',
            'environment': os.getenv('ENV', 'development'),
            'component': record.name.split('.')[0]
        }
        return json.dumps(log_data)
```

**Priority**: HIGH (needed for observability stack)  
**Effort**: 1 hour

---

### Gap 3: No Request/Trace ID Propagation

**Current**: Log context exists but not automatically propagated

**Issue**: Hard to trace requests across components

**Solution**:
```python
# Enhance context.py
import uuid

def generate_request_id() -> str:
    return str(uuid.uuid4())

def with_request_tracking(func):
    """Decorator to auto-generate and propagate request ID."""
    def wrapper(*args, **kwargs):
        request_id = generate_request_id()
        set_log_context(request_id=request_id)
        try:
            return func(*args, **kwargs)
        finally:
            clear_log_context()
    return wrapper

# Usage:
@with_request_tracking
def handle_request():
    # All logs automatically include request_id
    ...
```

**Priority**: MEDIUM (nice for debugging)  
**Effort**: 30 minutes

---

### Gap 4: No Performance Markers

**Current**: log_operation_context/complete exist but basic

**Enhancement**: Add performance markers
```python
# Add to operations.py
def log_performance_marker(operation, metric_name, value, **labels):
    """Log performance marker for analysis."""
    logger.info(f"[PERF] {operation}.{metric_name}={value} {labels}")

# Usage:
log_performance_marker("entity_resolution", "entities_per_second", 150, stage="resolution")
# Useful for performance analysis in logs
```

**Priority**: LOW  
**Effort**: 15 minutes

---

### Gap 5: No Log Level Helpers

**Current**: Have to use logging.DEBUG, logging.INFO constants

**Enhancement**: Convenience functions
```python
# Add to setup.py
def set_debug_mode():
    """Quick switch to DEBUG level."""
    logging.getLogger().setLevel(logging.DEBUG)

def set_quiet_mode():
    """Quick switch to WARNING+ only."""
    logging.getLogger().setLevel(logging.WARNING)

def set_component_level(component, level):
    """Set level for specific component."""
    logging.getLogger(component).setLevel(level)
```

**Priority**: LOW  
**Effort**: 15 minutes

---

## 🎯 Recommended Enhancements

### HIGH PRIORITY (For Observability Stack):

**1. Loki-Compatible Formatting** (1 hour):
- Add LokiFormatter
- Ensure JSON logs work with Loki
- Add stream labels

**2. Log Rotation** (30 min):
- Prevent huge log files
- Production-ready logging

**Total**: 1.5 hours

---

### MEDIUM PRIORITY (Nice to Have):

**3. Request ID Propagation** (30 min):
- Auto-generate request IDs
- Propagate through call stack
- Easier debugging

**Total**: 30 minutes

---

### LOW PRIORITY (Future):

**4. Performance Markers** (15 min)
**5. Level Helpers** (15 min)

**Total**: 30 minutes

---

## 📋 Implementation Plan

### Phase 1: Loki Formatter (1 hour)

**Create**: `core/libraries/logging/loki_formatter.py`
```python
class LokiFormatter(logging.Formatter):
    """JSON formatter for Grafana Loki with labels."""
    ...
```

**Update**: `formatters.py` or keep separate

**Test**: Verify JSON output format

---

### Phase 2: Log Rotation (30 min)

**Update**: `setup.py`
```python
def setup_logging(..., rotate_logs=True, max_mb=10, backup_count=5):
    if rotate_logs:
        from logging.handlers import RotatingFileHandler
        handler = RotatingFileHandler(...)
```

**Test**: Verify rotation works

---

### Phase 3: Request ID (30 min)

**Update**: `context.py`
```python
def with_request_tracking(func):
    ...

def generate_request_id():
    ...
```

**Test**: Verify IDs propagate

---

## ✅ Current Logging Library Status

**What's Already Enhanced**:
- ✅ log_exception() with metric tracking
- ✅ log_operation_context/complete()
- ✅ Context propagation
- ✅ Multiple formatters
- ✅ Integration with metrics

**What Needs Enhancement**:
- ⏳ Loki formatter (for observability stack)
- ⏳ Log rotation (for production)
- ⏳ Request ID helpers (for debugging)

**Total Effort**: 2 hours for HIGH + MEDIUM priority

---

**Should I implement HIGH priority enhancements now (1.5 hours)?**

