# API Reference - All Libraries

**Last Updated**: November 3, 2025  
**Coverage**: 4 complete libraries (70+ functions)

---

## logging Library

**Location**: `core/libraries/logging/`  
**Exports**: 21 functions

### Setup

- `setup_logging(level, log_file, verbose, silence_third_party, json_format, rotate_logs, max_bytes, backup_count)` - Configure logging
- `get_logger(name, context)` - Get logger instance
- `create_timestamped_log_path(base_dir, prefix, extension)` - Generate log filename
- `configure_logger_for_component(component_name, level, propagate)` - Per-component config

### Context

- `set_log_context(**kwargs)` - Set context for all logs
- `get_log_context()` - Retrieve current context
- `clear_log_context()` - Clear context
- `get_context_logger(name)` - Logger with auto-context
- `with_session_context(session_id)` - Set session context
- `with_request_context(request_id, user_id)` - Set request context

### Operations

- `log_operation_start(operation, **context)` - Log operation start
- `log_operation_complete(operation, duration, **results)` - Log operation end
- `log_operation_progress(operation, current, total, **metrics)` - Log progress

### Exceptions

- `log_exception(logger, message, exception, include_traceback, context, track_metric)` - Log exception (auto-tracks metric!)

### Formatters

- `JSONFormatter(include_extra)` - JSON formatter
- `ColoredFormatter()` - Colored console
- `CompactFormatter()` - Minimal format
- `LokiFormatter(service_name, environment, include_extra)` - Grafana Loki

---

## error_handling Library

**Location**: `core/libraries/error_handling/`  
**Exports**: 17 functions/classes

### Exceptions

- `ApplicationError(message, context, cause)` - Base exception with context
- `StageError(...)` - Stage execution errors
- `AgentError(...)` - Agent execution errors
- `PipelineError(...)` - Pipeline errors
- `ConfigurationError(...)` - Config errors
- `DatabaseError(...)` - DB errors
- `LLMError(...)` - LLM errors
- `wrap_exception(message, original, error_class, **context)` - Wrap with context

### Decorators

- `@handle_errors(fallback, log_traceback, capture_context, reraise, log_level)` - Auto error handling
- `@handle_stage_errors(stage_name)` - Stage-specific
- `@handle_agent_errors(agent_name)` - Agent-specific
- `@log_and_suppress(fallback, log_level)` - Log but continue
- `@require_success(error_class)` - Ensure specific error type

### Context Managers

- `error_context(operation, **context)` - Enrich exceptions
- `stage_context(stage_name, **context)` - Stage-specific
- `agent_context(agent_name, **context)` - Agent-specific
- `db_operation_context(operation, **context)` - DB-specific

### Helpers

- `format_exception_message(exception)` - Format as "Type: message"

---

## metrics Library

**Location**: `core/libraries/metrics/`  
**Exports**: 9 functions/classes

### Collectors

- `Counter(name, description, labels)` - Cumulative counts
  - `.inc(amount, labels)` - Increment
  - `.get(labels)` - Get value
  - `.reset(labels)` - Reset to zero
- `Gauge(name, description, labels)` - Current value
  - `.set(value, labels)` - Set value
  - `.inc(amount, labels)` - Increment
  - `.dec(amount, labels)` - Decrement
  - `.get(labels)` - Get value
- `Histogram(name, description, labels)` - Value distribution
  - `.observe(value, labels)` - Record observation
  - `.summary(labels)` - Get stats (count, sum, min, max, avg)
  - `.percentile(p, labels)` - Calculate percentile
- `Timer()` - Context manager for timing
  - `.elapsed()` - Get duration

### Registry

- `MetricRegistry.get_instance()` - Get singleton
  - `.register(metric)` - Register metric
  - `.get(name)` - Retrieve metric
  - `.collect_all()` - Get all metrics

### Export

- `export_prometheus_text()` - Export in Prometheus format

### Cost Models

- `estimate_llm_cost(model_name, prompt_tokens, completion_tokens)` - Calculate cost
- `add_model_pricing(model_name, input_price, output_price)` - Add custom model
- `LLM_PRICING` - Dict of model prices

---

## retry Library

**Location**: `core/libraries/retry/`  
**Exports**: 7 functions/classes

### Policies

- `RetryPolicy(max_attempts)` - Base policy
  - `.should_retry(attempt, exception)` - Check if should retry
  - `.get_delay(attempt)` - Get delay duration
- `ExponentialBackoff(max_attempts, base_delay, max_delay, multiplier)` - Exponential backoff
- `FixedDelay(max_attempts, delay)` - Fixed delay
- `NoRetry()` - Disable retry
- `DEFAULT_POLICY` - ExponentialBackoff(3, 1.0, 60.0)

### Decorators

- `@with_retry(max_attempts, backoff, base_delay, max_delay, retry_on, policy)` - General retry
- `@retry_llm_call(max_attempts)` - Specialized for LLM (exponential backoff)

---

## Usage Examples

### Complete Integration:

```python
from core.libraries.error_handling import handle_errors, error_context
from core.libraries.retry import with_retry
from core.libraries.logging import log_operation_context, log_exception
from core.libraries.metrics import Counter

processed = Counter('items_processed')

@handle_errors(log_traceback=True)
@with_retry(max_attempts=3)
def process_item(item):
    log_operation_context("item_processing", item_id=item['id'])

    with error_context("processing", item_type=item['type']):
        result = complex_operation(item)

    processed.inc()
    return result
```

**Result**: Error handling + retry + logging + metrics - all automatic!

---

**For detailed library guides**: See technical/OBSERVABILITY.md  
**For metrics catalog**: See reference/METRICS-REFERENCE.md
