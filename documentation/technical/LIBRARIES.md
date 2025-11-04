# Libraries - Cross-Cutting Technical Concerns

**Last Updated**: November 3, 2025  
**Total Libraries**: 18 (4 complete, 14 planned)  
**Location**: `core/libraries/`

---

## Overview

**What They Are**: Reusable technical patterns that support all business domains

**Why They Exist**: Eliminate code repetition, provide consistent patterns, enable observability

**Key Principle**: Libraries are pure - no dependencies on APP or BUSINESS layers

---

## Tier 1: Critical (Full Implementation)

### 1. logging/ ✅ COMPLETE

**Purpose**: Centralized logging with multiple formatters

**Files**: 6 files (setup.py, formatters.py, context.py, operations.py, exceptions.py, loki_formatter.py)

**Features**:

- Setup and configuration
- 4 formatters (JSON, Colored, Compact, Loki)
- Log context propagation
- Operation lifecycle logging
- Exception logging (integrates with metrics)
- Log rotation

**API** (20 exports):

- setup_logging(), get_logger()
- set_log_context(), get_log_context()
- log_operation_context(), log_operation_complete()
- log_exception() ⭐ (auto-tracks metrics)
- JSONFormatter, LokiFormatter, etc.

**Usage**:

```python
from core.libraries.logging import setup_logging, get_logger, log_exception

setup_logging(verbose=True, log_file='app.log', rotate_logs=True)
logger = get_logger(__name__)
log_exception(logger, "Failed", e)  # Logs + tracks metric!
```

---

### 2. error_handling/ ✅ COMPLETE

**Purpose**: Never have empty error messages again

**Files**: 3 files (exceptions.py, decorators.py, context.py)

**Features**:

- Exception hierarchy (7 exception classes)
- Context + cause chaining
- Error decorators
- Context managers

**API** (17 exports):

- ApplicationError, StageError, AgentError, etc.
- @handle_errors, @handle_stage_errors
- error_context, stage_context
- format_exception_message()

**Usage**:

```python
from core.libraries.error_handling import ApplicationError, handle_errors

@handle_errors(log_traceback=True)
def risky():
    ...

raise ApplicationError("Failed", context={'x': 1}, cause=e)
```

**Impact**: Solved 61-hour blind debugging session

---

### 3. metrics/ ✅ COMPLETE

**Purpose**: Track everything - stages, agents, tokens, costs

**Files**: 5 files (collectors.py, registry.py, exporters.py, cost_models.py, tests)

**Features**:

- 4 collector types (Counter, Gauge, Histogram, Timer)
- Singleton registry
- Prometheus text export
- LLM cost tracking (6 models + extensible)

**API** (9 exports):

- Counter, Gauge, Histogram, Timer
- MetricRegistry
- export_prometheus_text()
- estimate_llm_cost(), LLM_PRICING

**Usage**:

```python
from core.libraries.metrics import Counter, export_prometheus_text

processed = Counter('items_processed', labels=['type'])
processed.inc(labels={'type': 'entity'})

metrics = export_prometheus_text()  # For Prometheus
```

**Tracked Automatically**:

- Stage metrics (6 per stage)
- Agent metrics (5 per agent including tokens + cost)
- Global metrics (errors, retries)

---

### 4. retry/ ✅ COMPLETE

**Purpose**: Automatic retries with configurable backoff

**Files**: 3 files (policies.py, decorators.py, tests)

**Features**:

- 4 retry policies (Exponential, Fixed, NoRetry, Default)
- Integration with logging + metrics
- Specialized decorators

**API** (7 exports):

- RetryPolicy, ExponentialBackoff, FixedDelay, NoRetry
- @with_retry, @retry_llm_call

**Usage**:

```python
from core.libraries.retry import retry_llm_call

@retry_llm_call(max_attempts=3)
def call_openai():
    # Automatic retry with exponential backoff
    ...
```

**Logs Automatically**: Retry attempts, delays, final result

---

## Tier 2: Important (Simple Implementation + TODOs)

### 5-14. Support Libraries (9 libraries)

**validation/** - Business rule validation  
**configuration/** - Centralized config loading  
**caching/** - LRU/TTL cache  
**database/** - Transactions, batch operations  
**llm/** - Provider abstraction  
**concurrency/** - Parallel execution  
**rate_limiting/** - Rate limiting for any operation  
**serialization/** - MongoDB ↔ Pydantic conversion  
**data_transform/** - Common transformations

**Status**: Stubs created, implement on demand

**When to Implement**: During code review when patterns emerge

---

## Tier 3: Future (Stubs Only)

### 15-18. Nice-to-Have Libraries (4 libraries)

**health/** - Component health checking  
**context/** - Request context propagation  
**di/** - Dependency injection  
**feature_flags/** - Runtime feature toggles

**Status**: Stubs only, implement when complexity justifies

---

## Library Integration

**How They Work Together**:

```python
# Libraries are composable
@handle_errors(log_traceback=True)      # error_handling
@with_retry(max_attempts=3)             # retry
def process():
    log_operation_context("processing")  # logging
    work()
    log_operation_complete("processing") # logging
    # metrics tracked automatically
```

**Integration Points**:

1. **log_exception() → metrics**: Auto-tracks errors_total
2. **@with_retry → logging + metrics**: Logs retries, tracks retry count
3. **BaseStage/BaseAgent → all libraries**: Complete observability

**Dependency**: error_handling → logging → metrics (one-way, clean)

---

## Applied To

**Base Classes** (automatic inheritance):

- BaseStage: Uses error_handling, logging, metrics
- BaseAgent: Uses retry, error_handling, logging, metrics

**Components Enhanced** (via inheritance):

- 13 stages get error handling + metrics
- 12 agents get retry + cost tracking + metrics

**Total**: 30 components with complete observability

---

## Code Impact

**Lines Removed**: ~50 lines of boilerplate per component using libraries

**Example** - Agent before/after:

```python
# BEFORE (manual retry in each agent):
for attempt in range(max_retries):
    try:
        result = llm_call()
        break
    except Exception as e:
        if attempt == max_retries - 1:
            logger.error(f"Failed: {e}")  # ❌ No type, no traceback
            raise
        time.sleep(backoff)

# AFTER (using libraries):
@retry_llm_call(max_attempts=3)  # Automatic retry
def extract():
    result = llm_call()
    return result  # Libraries handle everything!
```

**Benefit**: ~300 lines removed from 6 agents alone

---

## Testing

**Library Tests**: tests/core/libraries/[library]/

- 7 test files
- 39 tests total
- All passing ✅

**Integration Tests**: tests/core/base/

- BaseStage integration
- BaseAgent integration

---

## Future Libraries

**When to Create**:

- Pattern repeated 3+ times
- Affects multiple domains
- Clear separation of concerns
- Reusable across project

**Process**:

1. Identify pattern
2. Create stub in core/libraries/
3. Document API in stub
4. Implement when needed
5. Test thoroughly
6. Apply to codebase

---

## Related Documentation

**Implementation Details**: technical/OBSERVABILITY.md  
**API Reference**: reference/API-REFERENCE.md  
**Usage in Components**: architecture/STAGE.md, architecture/AGENT.md

---

**Libraries enable DRY, observable, maintainable code across all domains.**
