# Complete Observability Guide

**Last Updated**: November 3, 2025  
**Status**: Production-ready observability stack with 4 libraries

---

## Overview

Complete observability system with error handling, metrics, retry, and logging libraries integrated with Prometheus + Grafana + Loki stack.

**What This Solves**: 61-hour blind debugging session where error message was empty.

---

## Libraries

### 1. Error Handling Library ✅

**Location**: `core/libraries/error_handling/`

**Purpose**: Never have empty error messages again

**Components**:

- 7 exception classes (ApplicationError, StageError, AgentError, etc.)
- 5 decorators (@handle_errors, @handle_stage_errors, etc.)
- 4 context managers (error_context, stage_context, etc.)

**Usage**:

```python
from core.libraries.error_handling import ApplicationError, handle_errors, error_context

# Raise informative exceptions
raise ApplicationError(
    "Entity resolution failed",
    context={'chunks_processed': 1000, 'stage': 'resolution'},
    cause=original_error
)

# Auto-handle errors
@handle_errors(log_traceback=True)
def risky_operation():
    ...

# Add context to operations
with error_context("data_processing", chunk_id='123'):
    process_data()
```

**API**: See documentation/reference/API-REFERENCE.md

---

### 2. Metrics Library ✅

**Location**: `core/libraries/metrics/`

**Purpose**: Track everything - stages, agents, tokens, costs

**Components**:

- 4 collectors (Counter, Gauge, Histogram, Timer)
- Singleton registry
- Prometheus exporter
- LLM cost models (6 models + extensible)

**Usage**:

```python
from core.libraries.metrics import Counter, Histogram, export_prometheus_text

# Create metrics
processed = Counter('items_processed', labels=['type'])
duration = Histogram('operation_duration')

# Use metrics
processed.inc(labels={'type': 'entity'})
duration.observe(10.5)

# Export for Prometheus
metrics_text = export_prometheus_text()
```

**Tracked Automatically** (via BaseStage + BaseAgent):

- Stage execution (started, completed, failed, duration, documents)
- Agent LLM calls (calls, errors, duration, tokens, cost)
- Errors (by type and component)
- Retries (by function and error type)

**API**: See documentation/reference/METRICS-REFERENCE.md

---

### 3. Retry Library ✅

**Location**: `core/libraries/retry/`

**Purpose**: Automatic retries with configurable backoff

**Components**:

- 4 policies (Exponential, Fixed, NoRetry, Default)
- 2 decorators (@with_retry, @retry_llm_call)

**Usage**:

```python
from core.libraries.retry import with_retry, retry_llm_call

# General retry
@with_retry(max_attempts=3, backoff="exponential")
def call_api():
    ...

# Specialized for LLM
@retry_llm_call(max_attempts=5)
def call_openai():
    ...
```

**Integrated**: Logs retries, tracks retry metrics automatically

---

### 4. Logging Library ✅

**Location**: `core/libraries/logging/`

**Purpose**: Comprehensive logging with multiple formatters

**Components**:

- Setup and configuration
- 4 formatters (JSON, Colored, Compact, Loki)
- Context propagation
- Operation lifecycle logging
- Exception logging (integrates with metrics)
- Log rotation

**Usage**:

```python
from core.libraries.logging import setup_logging, get_logger, log_exception

# Setup once
setup_logging(verbose=True, log_file='app.log', rotate_logs=True)

# Use anywhere
logger = get_logger(__name__)
log_exception(logger, "Operation failed", e)  # Auto-tracks metric!
```

---

## Integration

**Libraries Work Together**:

```python
@handle_errors(log_traceback=True)      # error_handling
@with_retry(max_attempts=3)             # retry (logs attempts)
def process_data():
    log_operation_context("processing")  # logging
    # Work...
    log_operation_complete("processing", duration=5.0)  # logging
    # Metrics tracked automatically
```

**Dependency Flow**: error_handling → logging → metrics → Python logging

---

## Observability Stack

**Location**: `observability/` + `docker-compose.observability.yml`

**Components**:

- Prometheus (metrics collection)
- Grafana (visualization)
- Loki (log aggregation)
- Promtail (log shipping)

**Start**:

```bash
docker-compose -f docker-compose.observability.yml up -d
python app/api/metrics.py  # Metrics endpoint
```

**Access**:

- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- Metrics: http://localhost:9091/metrics

---

## Complete Guide

See observability/README.md for detailed usage, queries, and troubleshooting.

**Tests**: 7 test files, 39 tests, all passing ✅  
**Status**: Production-ready ✅
