# Library Integration Guide

**Created**: 2025-11-13  
**Achievement**: 3.3 - Comprehensive User Documentation + Library Patterns  
**Purpose**: Document library integration patterns for prompt generation scripts and future CLI platform

---

## Overview

This guide documents the integration of 5 production-grade libraries into the prompt generation system:

1. **error_handling** - Structured exceptions with actionable suggestions
2. **logging** - Structured logging with context propagation
3. **validation** - Input validation patterns
4. **caching** - Performance optimization through intelligent caching
5. **metrics** - Observable performance with Prometheus-compatible metrics

These patterns were established in Achievements 3.1 (Error Handling + Logging + Validation) and 3.2 (Caching + Metrics), achieving:

- **582x performance improvement** for cached operations
- **91% cache hit rate** (target: 80%)
- **Structured error messages** with color-coded output
- **Production-ready observability** with Prometheus metrics

---

## Error Handling Patterns

### Custom Exceptions (Achievement 3.1)

**Location**: `LLM/scripts/generation/exceptions.py`

**Pattern**: Create domain-specific exceptions that inherit from `ApplicationError` and provide context + actionable suggestions.

**Before** (print + sys.exit):

```python
def resolve_plan_path(folder_name):
    plan_path = Path(f"work-space/plans/{folder_name}")
    if not plan_path.exists():
        print(f"ERROR: PLAN not found at {plan_path}")
        sys.exit(1)
    return plan_path
```

**After** (structured exceptions):

```python
from LLM.scripts.generation.exceptions import PlanNotFoundError

def resolve_plan_path(folder_name):
    plan_path = Path(f"work-space/plans/{folder_name}")
    if not plan_path.exists():
        raise PlanNotFoundError(
            message=f"PLAN not found: {folder_name}",
            context={
                "folder_name": folder_name,
                "expected_path": str(plan_path),
                "suggestions": [
                    f"Check if folder '{folder_name}' exists in work-space/plans/",
                    "Use @folder shortcut to search by name",
                    "List available plans: ls work-space/plans/",
                ]
            }
        )
    return plan_path
```

**Benefits**:

- Clear error types (PlanNotFoundError vs generic Exception)
- Context dictionary preserves debugging information
- Actionable suggestions guide users to solutions
- Color-coded output (red for errors, yellow for suggestions)

### Available Exception Types

**Defined in** `LLM/scripts/generation/exceptions.py`:

```python
from core.libraries.error_handling import ApplicationError

class PlanNotFoundError(ApplicationError):
    """Raised when PLAN file cannot be found."""
    pass

class AchievementNotFoundError(ApplicationError):
    """Raised when achievement doesn't exist in PLAN."""
    pass

class SubplanNotFoundError(ApplicationError):
    """Raised when SUBPLAN file cannot be found."""
    pass

class InvalidAchievementFormatError(ApplicationError):
    """Raised when achievement number format is invalid."""
    pass

class ExecutionTaskNotFoundError(ApplicationError):
    """Raised when EXECUTION_TASK file cannot be found."""
    pass

class InvalidPathError(ApplicationError):
    """Raised when path resolution fails."""
    pass
```

**Usage Pattern**:

```python
# Raise with context and suggestions
raise AchievementNotFoundError(
    message=f"Achievement {achievement_num} not found in PLAN",
    context={
        "achievement_num": achievement_num,
        "plan_path": str(plan_path),
        "available_achievements": [a.number for a in achievements],
        "suggestions": [
            f"Check Achievement Index in PLAN file",
            f"Valid format: 'X.Y' (e.g., '2.1', '3.10')",
            f"Available: {', '.join([a.number for a in achievements[:5]])}...",
        ]
    }
)
```

### Formatting Errors with Suggestions

**Function**: `format_error_with_suggestions(error, use_colors=True)`

**Features**:

- Color-coded output (red errors, yellow suggestions, blue details)
- Structured display of error message + context + suggestions
- Auto-copy to clipboard (main script integration)

**Example Output**:

```
❌ ERROR: PLAN not found: NONEXISTENT-PLAN

Details:
  folder_name: NONEXISTENT-PLAN
  expected_path: work-space/plans/NONEXISTENT-PLAN

HOW TO FIX:
1. Check if folder 'NONEXISTENT-PLAN' exists in work-space/plans/
2. Use @folder shortcut to search by name
3. List available plans: ls work-space/plans/
```

**Integration in Main Script**:

```python
from LLM.scripts.generation.exceptions import (
    ApplicationError,
    format_error_with_suggestions
)
import pyperclip

try:
    # ... main logic ...
except ApplicationError as e:
    # Format error with suggestions
    error_output = format_error_with_suggestions(e, use_colors=True)
    print(error_output)

    # Auto-copy to clipboard for easy sharing
    try:
        pyperclip.copy(error_output)
        print("\n📋 Error copied to clipboard")
    except Exception:
        pass  # Clipboard not available

    sys.exit(1)
```

### Input Validation Patterns

**Pattern**: Validate inputs early with clear error messages.

**Example**: Achievement number format validation

```python
import re
from LLM.scripts.generation.exceptions import InvalidAchievementFormatError

def validate_achievement_number(achievement_num: str):
    """Validate achievement number format (X.Y)."""
    if not re.match(r'^\d+\.\d+$', achievement_num):
        raise InvalidAchievementFormatError(
            message=f"Invalid achievement number format: {achievement_num}",
            context={
                "provided": achievement_num,
                "expected_format": "X.Y (e.g., '2.1', '3.10')",
                "suggestions": [
                    "Use format: <major>.<minor> (e.g., '2.1')",
                    "Both parts must be numbers",
                    "Examples: '1.1', '2.5', '3.10'",
                ]
            }
        )
```

### Anti-Patterns to Avoid

❌ **Don't** use generic exceptions:

```python
raise Exception("PLAN not found")  # BAD: No context, no suggestions
```

❌ **Don't** use print + sys.exit:

```python
print("ERROR: Invalid input")
sys.exit(1)  # BAD: Not catchable, no structured data
```

❌ **Don't** swallow exceptions silently:

```python
try:
    parse_plan()
except Exception:
    pass  # BAD: Silent failure
```

✅ **Do** use domain-specific exceptions with context:

```python
raise PlanNotFoundError(
    message="PLAN not found",
    context={"folder": name, "suggestions": [...]}"
)
```

---

## Performance Patterns

### Caching with @cached Decorator (Achievement 3.2)

**Location**: `core/libraries/caching`

**Pattern**: Cache expensive operations (PLAN parsing, file I/O) with automatic invalidation.

**Before** (no caching):

```python
def parse_plan_file(self, plan_path: Path) -> Dict[str, any]:
    """Parse PLAN file - always reads from disk (1-2s)."""
    with open(plan_path, "r") as f:
        content = f.read()
    # ... expensive parsing ...
    return result
```

**After** (with caching):

```python
import os
from core.libraries.caching import cached

@cached(
    max_size=50,  # Cache up to 50 PLANs
    ttl=300,  # 5 minutes TTL
    key_func=lambda self, plan_path: f"{plan_path}:{os.path.getmtime(plan_path)}",
    name="plan_cache"
)
def parse_plan_file(self, plan_path: Path) -> Dict[str, any]:
    """Parse PLAN file - cached with mtime-based invalidation.

    Performance:
    - First call: ~8ms (cache miss)
    - Cached calls: ~0.01ms (cache hit)
    - Speed improvement: 582x faster
    """
    with open(plan_path, "r") as f:
        content = f.read()
    # ... expensive parsing ...
    return result
```

**Performance Results** (Real-World Test):

```
PLAN: PLAN_PROMPT-GENERATOR-UX-AND-FOUNDATION.md (18 achievements)
First call (cache miss):  7.98ms
Second call (cache hit):  0.01ms
Speed improvement:        582x faster
Time saved:               99.8%
```

**Key Features**:

- **Automatic Invalidation**: mtime in cache key invalidates on file changes
- **TTL**: Time-to-live prevents stale data (5 minutes default)
- **LRU Eviction**: Least recently used items evicted when cache full
- **Thread-Safe**: Built-in locking for concurrent access

### Cache Statistics

**Access cache stats**:

```python
parser = PlanParser()
parser.parse_plan_file(plan_path)  # Populate cache

stats = parser.parse_plan_file.cache.stats()
print(stats)

# Output:
# {
#     'name': 'plan_cache',
#     'hits': 10,
#     'misses': 1,
#     'size': 1,
#     'max_size': 50,
#     'hit_rate': 90.9,  # %
#     'ttl': 300
# }
```

### Compiled Regex Patterns (Achievement 3.2)

**Pattern**: Compile regex patterns once at module level, not on each call.

**Before** (slow - compiled each time):

```python
def parse_achievements(lines):
    for line in lines:
        if match := re.match(r"\*\*Achievement (\d+\.\d+)\*\*:(.+)", line):
            # Pattern compiled on every iteration
            process_match(match)
```

**After** (fast - compiled once):

```python
# Module level - compiled once
ACHIEVEMENT_PATTERN = re.compile(r"\*\*Achievement (\d+\.\d+)\*\*:(.+)")
HANDOFF_PATTERN = re.compile(r"##\s*.*Current Status.*Handoff", re.IGNORECASE)
TIME_PATTERN = re.compile(r"\*\*(?:Time|Actual)\*\*:\s*([\d.]+)\s*hours?")

def parse_achievements(lines):
    for line in lines:
        if match := ACHIEVEMENT_PATTERN.match(line):
            # Pattern already compiled, ~10-20% faster
            process_match(match)
```

**Performance Gain**: ~10-20% faster for regex-heavy operations.

**Patterns Compiled** (from `plan_parser.py`):

- `ACHIEVEMENT_PATTERN` - Parse achievement headers
- `HANDOFF_PATTERN` - Find handoff section
- `ACHIEVEMENT_COUNT_PATTERN` - Count achievements
- `TIME_PATTERN` - Extract execution times
- `ARCHIVE_PATTERN` - Extract archive locations

### Metrics Collection (Achievement 3.2)

**Location**: `core/libraries/metrics`

**Pattern**: Collect performance metrics with Prometheus-compatible Counter/Histogram/Timer.

**Defining Metrics**:

```python
from core.libraries.metrics import Counter, Histogram, Timer, MetricRegistry

# Define metrics
prompt_generation_counter = Counter(
    'prompt_generation_total',
    description='Total prompts generated',
    labels=['workflow', 'status']
)

prompt_generation_duration = Histogram(
    'prompt_generation_duration_seconds',
    description='Prompt generation duration',
    labels=['workflow']
)

plan_cache_hits = Counter(
    'plan_cache_hits_total',
    description='PLAN cache hits',
    labels=['cache_name', 'hit_type']
)

# Register with global registry
registry = MetricRegistry.get_instance()
registry.register(prompt_generation_counter)
registry.register(prompt_generation_duration)
registry.register(plan_cache_hits)
```

**Using Metrics**:

```python
# Counter - increment on events
prompt_generation_counter.inc(labels={'workflow': 'next_achievement', 'status': 'success'})
prompt_generation_counter.inc(labels={'workflow': 'next_achievement', 'status': 'error'})

# Histogram - record durations
prompt_generation_duration.observe(1.5, labels={'workflow': 'next_achievement'})

# Timer - context manager for timing
with Timer() as timer:
    result = generate_prompt()

prompt_generation_duration.observe(timer.elapsed(), labels={'workflow': 'next_achievement'})
```

**Exporting Metrics** (Prometheus format):

```python
from core.libraries.metrics import export_prometheus_text

metrics_text = export_prometheus_text()
print(metrics_text)

# Output:
# # HELP prompt_generation_total Total prompts generated
# # TYPE prompt_generation_total counter
# prompt_generation_total{workflow="next_achievement",status="success"} 50
#
# # HELP prompt_generation_duration_seconds Prompt generation duration
# # TYPE prompt_generation_duration_seconds histogram
# prompt_generation_duration_seconds_sum{workflow="next_achievement"} 75.0
# prompt_generation_duration_seconds_count{workflow="next_achievement"} 50
```

### Profiling Functions

**Pattern**: Measure execution time of critical functions.

**Implementation**:

```python
import time
from core.libraries.logging import get_logger

logger = get_logger(__name__)

def profile_function(func):
    """Decorator to profile function execution time."""
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            logger.debug(
                f"Function {func.__name__} took {duration:.3f}s",
                extra={'function': func.__name__, 'duration': duration}
            )
            return result
        except Exception as e:
            duration = time.perf_counter() - start
            logger.error(
                f"Function {func.__name__} failed after {duration:.3f}s",
                extra={'function': func.__name__}, 'duration': duration, 'error': str(e)}
            )
            raise
    return wrapper

# Usage
@profile_function
def parse_plan(plan_path):
    # ... expensive operation ...
    pass

# Logs: DEBUG: Function parse_plan took 1.234s
```

### Anti-Patterns to Avoid

❌ **Don't** cache without considering invalidation:

```python
@cached()  # BAD: No TTL, no mtime, stale data
def parse_plan(path):
    pass
```

❌ **Don't** compile regex in loops:

```python
for line in lines:
    if re.match(r"pattern", line):  # BAD: Compiled each iteration
        pass
```

❌ **Don't** forget to register metrics:

```python
my_counter = Counter('my_metric')
# BAD: Not registered, won't appear in export
```

✅ **Do** use mtime-based cache keys:

```python
@cached(key_func=lambda self, path: f"{path}:{os.path.getmtime(path)}")
def parse_plan(self, path):
    pass
```

✅ **Do** compile patterns at module level:

```python
PATTERN = re.compile(r"pattern")  # Module level
def process():
    if PATTERN.match(line):  # Fast
        pass
```

✅ **Do** register all metrics:

```python
registry = MetricRegistry.get_instance()
registry.register(my_counter)
```

---

## Logging Patterns

### Structured Logging (Achievement 3.1)

**Location**: `core/libraries/logging`

**Pattern**: Use structured logging with context instead of print statements.

**Before** (print statements):

```python
def generate_prompt(plan_path, achievement_num):
    print(f"Generating prompt for achievement {achievement_num}")
    # ... logic ...
    print("Prompt generated successfully")
```

**After** (structured logging):

```python
from core.libraries.logging import get_logger, set_log_context

logger = get_logger(__name__)

def generate_prompt(plan_path, achievement_num):
    # Set context for all logs in this execution
    set_log_context(
        plan=plan_path.stem,
        achievement=achievement_num,
        workflow='generate_prompt'
    )

    logger.info(
        "Generating prompt",
        extra={'achievement': achievement_num, 'plan': plan_path.stem}
    )

    # ... logic ...

    logger.info(
        "Prompt generated successfully",
        extra={'achievement': achievement_num, 'lines': len(prompt)}
    )
```

**Benefits**:

- **Searchable**: JSON logs enable searching by field
- **Context**: Logs include execution context automatically
- **Levels**: DEBUG, INFO, WARNING, ERROR for filtering
- **Structured**: Machine-readable for log aggregation

### Context Propagation

**Pattern**: Set log context once, it propagates to all subsequent logs.

```python
from core.libraries.logging import get_logger, set_log_context

logger = get_logger(__name__)

def main():
    # Set context once
    set_log_context(
        plan='FEATURE',
        workflow='next_achievement',
        execution_id=str(uuid.uuid4())
    )

    logger.info("Starting workflow")  # Includes context
    detect_state()  # All logs include context
    generate_prompt()  # All logs include context
    logger.info("Workflow complete")  # Includes context
```

**Log Output** (JSON):

```json
{
  "timestamp": "2025-11-13T12:34:56.789Z",
  "level": "INFO",
  "message": "Starting workflow",
  "plan": "FEATURE",
  "workflow": "next_achievement",
  "execution_id": "abc-123-def-456"
}
```

### Logging Levels

**Usage Guide**:

```python
# DEBUG - Detailed information for debugging
logger.debug("Cache hit", extra={'key': cache_key, 'hit_rate': 91.5})

# INFO - General information about execution
logger.info("Prompt generated", extra={'achievement': '3.2', 'lines': 500})

# WARNING - Something unexpected but recoverable
logger.warning("Slow PLAN parse", extra={'duration': 5.2, 'threshold': 3.0})

# ERROR - Operation failed, but application continues
logger.error("Achievement not found", extra={'achievement': '9.9'})

# CRITICAL - Severe error, application may exit
logger.critical("PLAN corrupted", extra={'plan': 'FEATURE'})
```

### Anti-Patterns to Avoid

❌ **Don't** use print statements:

```python
print("Processing...")  # BAD: Not structured, not searchable
```

❌ **Don't** log sensitive data:

```python
logger.info("User password", extra={'password': pwd})  # BAD: Security risk
```

❌ **Don't** log in hot loops without throttling:

```python
for i in range(10000):
    logger.debug(f"Processing {i}")  # BAD: Performance impact
```

✅ **Do** use structured logging:

```python
logger.info("Processing", extra={'count': 10000})
```

✅ **Do** set context early:

```python
set_log_context(plan='FEATURE', workflow='next')
```

✅ **Do** use appropriate levels:

```python
logger.debug("Cache hit")  # Debug details
logger.info("Workflow complete")  # Important events
logger.error("Operation failed", exc_info=True)  # Errors with traceback
```

---

## Best Practices

### When to Use Each Library

**Error Handling** (`exceptions.py`):

- ✅ Use for all user-facing errors
- ✅ Use for validation errors
- ✅ Use for file not found, invalid input
- ❌ Don't use for internal assertions (use standard assert)
- ❌ Don't use for expected flow control (use if/else)

**Logging** (`get_logger()`):

- ✅ Use for all output (replace print statements)
- ✅ Use for debugging information
- ✅ Use for workflow tracing
- ❌ Don't log sensitive data
- ❌ Don't log in performance-critical loops

**Validation** (pattern in exceptions):

- ✅ Validate inputs early (achievement numbers, paths)
- ✅ Provide clear error messages
- ✅ Suggest correct format
- ❌ Don't validate output (trust your logic)
- ❌ Don't over-validate (balance safety vs complexity)

**Caching** (`@cached`):

- ✅ Cache expensive operations (PLAN parsing, file I/O)
- ✅ Use mtime-based keys for file data
- ✅ Set reasonable TTL (5-10 minutes)
- ❌ Don't cache non-deterministic functions
- ❌ Don't cache without invalidation strategy

**Metrics** (`Counter`, `Histogram`):

- ✅ Track user-facing operations
- ✅ Track performance-critical paths
- ✅ Register all metrics
- ❌ Don't collect metrics without a use case
- ❌ Don't create unbounded label cardinality

### Integration Checklist

When adding a new feature to the prompt generation system:

**1. Error Handling**:

- [ ] Define domain-specific exceptions if needed
- [ ] Raise exceptions with context and suggestions
- [ ] Catch and format exceptions in main()

**2. Logging**:

- [ ] Replace print statements with logger calls
- [ ] Set log context at entry points
- [ ] Use appropriate log levels

**3. Performance**:

- [ ] Identify expensive operations
- [ ] Add caching with mtime invalidation
- [ ] Compile regex patterns at module level
- [ ] Add metrics for user-facing operations

**4. Validation**:

- [ ] Validate inputs early
- [ ] Provide clear error messages
- [ ] Suggest correct format

**5. Testing**:

- [ ] Test error handling (expect specific exceptions)
- [ ] Test cache hit/miss behavior
- [ ] Test cache invalidation
- [ ] Test metrics collection

### Common Pitfalls

1. **Cache Invalidation**: Always include mtime in cache key for file-based data
2. **Metric Registration**: Register all metrics with MetricRegistry
3. **Log Levels**: Use DEBUG for details, INFO for events, ERROR for failures
4. **Exception Context**: Always provide context dict with suggestions
5. **Regex Compilation**: Compile patterns at module level, not in functions

---

## Real-World Examples

### Example 1: Complete Function with All Libraries

```python
import os
import re
from pathlib import Path
from core.libraries.caching import cached
from core.libraries.logging import get_logger
from LLM.scripts.generation.exceptions import PlanNotFoundError

logger = get_logger(__name__)

# Compile regex at module level
ACHIEVEMENT_PATTERN = re.compile(r"\*\*Achievement (\d+\.\d+)\*\*:(.+)")

class PlanParser:
    @cached(
        max_size=50,
        ttl=300,
        key_func=lambda self, path: f"{path}:{os.path.getmtime(path)}",
        name="plan_cache"
    )
    def parse_plan_file(self, plan_path: Path):
        """Parse PLAN file with caching, logging, and error handling.

        Libraries used:
        - caching: @cached decorator (582x speedup for cached calls)
        - logging: Structured logs with context
        - exceptions: Domain-specific errors with suggestions

        Performance:
        - First call: ~8ms (cache miss)
        - Cached calls: ~0.01ms (cache hit, 582x faster)

        Raises:
            PlanNotFoundError: If PLAN file doesn't exist
        """
        logger.debug("Parsing PLAN", extra={'path': str(plan_path)})

        # Error handling with structured exception
        if not plan_path.exists():
            raise PlanNotFoundError(
                message=f"PLAN not found: {plan_path.name}",
                context={
                    "path": str(plan_path),
                    "suggestions": [
                        "Check if file exists",
                        "Use @folder shortcut",
                        "List plans: ls work-space/plans/",
                    ]
                }
            )

        with open(plan_path, "r") as f:
            content = f.read()

        achievements = []
        for line in content.split("\n"):
            # Use compiled pattern for performance
            if match := ACHIEVEMENT_PATTERN.match(line):
                achievements.append({
                    'number': match.group(1),
                    'title': match.group(2).strip()
                })

        logger.info(
            "PLAN parsed successfully",
            extra={'achievements': len(achievements), 'path': plan_path.stem}
        )

        return {'achievements': achievements}
```

### Example 2: Main Script Integration

```python
from LLM.scripts.generation.exceptions import (
    ApplicationError,
    format_error_with_suggestions,
    InvalidAchievementFormatError
)
from core.libraries.logging import get_logger, set_log_context
from core.libraries.metrics import Counter, Histogram, Timer, MetricRegistry
import pyperclip

# Setup logging
logger = get_logger(__name__)

# Setup metrics
prompt_counter = Counter('prompt_generation_total', labels=['workflow', 'status'])
prompt_duration = Histogram('prompt_generation_duration_seconds', labels=['workflow'])

registry = MetricRegistry.get_instance()
registry.register(prompt_counter)
registry.register(prompt_duration)

def main():
    try:
        # Set log context
        set_log_context(plan='FEATURE', workflow='next_achievement')

        # Measure duration
        with Timer() as timer:
            # Validate input
            if not re.match(r'^\d+\.\d+$', achievement_num):
                raise InvalidAchievementFormatError(
                    message=f"Invalid format: {achievement_num}",
                    context={"suggestions": ["Use format: X.Y (e.g., '2.1')"]}
                )

            # Generate prompt (uses caching, logging internally)
            prompt = generate_prompt(plan_path, achievement_num)

        # Record metrics
        prompt_duration.observe(timer.elapsed(), labels={'workflow': 'next_achievement'})
        prompt_counter.inc(labels={'workflow': 'next_achievement', 'status': 'success'})

        logger.info("Prompt generated", extra={'duration': timer.elapsed()})
        print(prompt)

    except ApplicationError as e:
        # Format and display error
        error_output = format_error_with_suggestions(e, use_colors=True)
        print(error_output)

        # Copy to clipboard
        try:
            pyperclip.copy(error_output)
            print("\n📋 Error copied to clipboard")
        except Exception:
            pass

        # Record error metric
        prompt_counter.inc(labels={'workflow': 'next_achievement', 'status': 'error'})
        sys.exit(1)
```

---

## References

**Library Documentation**:

- `core/libraries/error_handling/` - Error handling library
- `core/libraries/logging/` - Logging library
- `core/libraries/caching/` - Caching library
- `core/libraries/metrics/` - Metrics library

**Implementation Examples**:

- `LLM/scripts/generation/exceptions.py` - Custom exceptions
- `LLM/scripts/generation/plan_parser.py` - Caching implementation
- `LLM/scripts/generation/generate_prompt.py` - Metrics integration

**Pattern Documentation**:

- `LLM/docs/ERROR_HANDLING_PATTERNS.md` - Error handling details
- `LLM/docs/PERFORMANCE_OPTIMIZATION_GUIDE.md` - Caching/metrics details

**Test Examples**:

- `tests/LLM/scripts/generation/test_exceptions.py` - Error handling tests
- `tests/LLM/scripts/generation/test_performance.py` - Performance tests

---

**Last Updated**: 2025-11-13  
**Status**: Production-Ready  
**Achievements**: 3.1 (Error Handling), 3.2 (Performance), 3.3 (Documentation)
