# Library Interaction Design - Separation of Concerns

**Date**: November 3, 2025  
**Issue**: Overlap between error_handling and logging libraries  
**Goal**: Clear separation with well-defined interaction points

---

## 🎯 Current Problem

### Overlapping Concerns:

**error_handling library**:

- Captures exceptions
- Logs errors (using logging)
- Adds context to errors

**logging library**:

- Configures logging
- Provides loggers
- Manages log context

**Overlap**: Both log errors! Who should do what?

---

## ✅ Proposed Separation of Concerns

### 1. Logging Library (CORE concerns)

**Responsibility**: "I manage ALL logging"

**Owns**:

- ✅ Logger configuration (setup_logging)
- ✅ Logger factory (get_logger)
- ✅ Log context management (set_log_context)
- ✅ Formatters (JSON, colored, etc.)
- ✅ **Operation lifecycle logging** (log_operation_context, log_operation_complete)
- ✅ **Exception logging helper** (log_exception) ← MOVE HERE

**Exports**:

```python
from core.libraries.logging import (
    # Setup
    setup_logging, get_logger,
    # Context
    set_log_context, get_log_context,
    # Operations
    log_operation_context, log_operation_complete,
    # Exceptions
    log_exception,  # ← Logging library owns this!
)
```

**Philosophy**: "If it writes to a log, it's my concern"

---

### 2. Error Handling Library (EXCEPTION concerns)

**Responsibility**: "I manage exception types and enrichment"

**Owns**:

- ✅ Custom exception classes (ApplicationError, StageError, etc.)
- ✅ Exception enrichment (context, cause)
- ✅ Error decorators (wrap functions with try-except)
- ✅ Error context managers (enrich exceptions)
- ✅ **Exception wrapping/formatting** (format_exception_message)

**Does NOT Own**:

- ❌ Actual logging (delegates to logging library)

**Exports**:

```python
from core.libraries.error_handling import (
    # Exceptions
    ApplicationError, StageError, AgentError,
    # Decorators
    handle_errors, handle_stage_errors,
    # Context
    error_context, stage_context,
    # Formatting
    format_exception_message,  # Format, but don't log!
)
```

**Philosophy**: "I create and enrich exceptions, logging library logs them"

---

## 🔗 Library Interaction Contract

### How They Work Together:

```python
# error_handling creates/enriches exceptions
from core.libraries.error_handling import ApplicationError

# logging logs them
from core.libraries.logging import log_exception

try:
    risky_operation()
except Exception as e:
    # error_handling: wrap exception with context
    enriched = ApplicationError("Failed", context={'x': 1}, cause=e)

    # logging: log the enriched exception
    log_exception(logger, "Operation failed", enriched)
```

**Clear separation**: error_handling enriches, logging logs!

---

## 📋 Proposed Reorganization

### Step 1: Move Functions to Logging Library

**Move FROM** `core/libraries/error_handling/context.py`:

- `log_operation_context()` → `core/libraries/logging/operations.py`
- `log_operation_complete()` → `core/libraries/logging/operations.py`

**Move FROM** `core/libraries/error_handling/helpers.py`:

- `log_exception()` → `core/libraries/logging/exceptions.py`
- `format_exception_message()` → Keep in error_handling (it's formatting, not logging)

---

### Step 2: Clean Error Handling Library

**Keep ONLY exception concerns**:

```
core/libraries/error_handling/
├── __init__.py
├── exceptions.py        # Exception classes
├── decorators.py        # @handle_errors (uses logging.log_exception internally)
├── context.py           # error_context (uses logging.log_exception internally)
└── helpers.py           # format_exception_message (pure formatting)
```

**Dependencies**:

- error_handling → logging (uses log_exception)
- logging → nothing (pure logging)

---

### Step 3: Enhance Logging Library

**Add to logging library**:

```
core/libraries/logging/
├── __init__.py
├── setup.py             # ✅ Setup
├── formatters.py        # ✅ Formatters
├── context.py           # ✅ Log context
├── exceptions.py        # ← NEW: log_exception()
└── operations.py        # ← NEW: operation lifecycle logging
```

**New file: `logging/exceptions.py`**:

```python
def log_exception(logger, message, exception, include_traceback=True, context=None):
    """Log exception with full details."""
    # ... implementation ...
```

**New file: `logging/operations.py`**:

```python
def log_operation_context(operation, **context):
    """Log operation start."""
    # ... implementation ...

def log_operation_complete(operation, duration=None, **results):
    """Log operation completion."""
    # ... implementation ...
```

---

## 🎯 Updated Library Interaction

### How Libraries Interact:

```
┌─────────────────────────────────────────┐
│ error_handling Library                  │
│ - Creates exceptions                    │
│ - Enriches with context                 │
│ - Provides decorators                   │
│                                         │
│ Uses ↓                                  │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ logging Library                         │
│ - Configures logging                    │
│ - Provides loggers                      │
│ - Logs exceptions (log_exception)       │
│ - Logs operations (lifecycle)           │
│                                         │
│ Uses ↓                                  │
└─────────────────────────────────────────┘
              ↓
       Python logging
```

**Dependency Direction**: error_handling → logging → python logging

**Clear separation**:

- error_handling = exception management
- logging = log output management

---

## 📊 Example: Clean Usage

**In BaseStage**:

```python
from core.libraries.logging import get_logger, log_operation_context, log_operation_complete, log_exception
from core.libraries.error_handling import handle_errors, stage_context

class BaseStage:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    @handle_errors(log_traceback=True)
    def run(self, config):
        # logging: track operation
        log_operation_context(f"stage_{self.name}", stage=self.name)

        try:
            # error_handling: add context
            with stage_context(self.name):
                process_docs()

            # logging: log completion
            log_operation_complete(f"stage_{self.name}", duration=10.5)

        except Exception as e:
            # logging: log the exception
            log_exception(self.logger, "Stage failed", e)
```

**Clean responsibilities**:

- logging library: All log output
- error_handling library: Exception enrichment

---

## 🔧 Implementation Plan

### Phase 4D: Reorganize Library Responsibilities (30 min)

**1. Move to logging library** (15 min):

- Create `core/libraries/logging/operations.py`
- Move `log_operation_context()`, `log_operation_complete()`
- Create `core/libraries/logging/exceptions.py`
- Move `log_exception()`
- Update logging/**init**.py exports

**2. Update error_handling library** (10 min):

- Remove operation logging from context.py
- Keep only error_context (exception enrichment)
- Update imports in decorators.py to use logging.log_exception
- Update error_handling/**init**.py exports

**3. Update all code** (5 min):

- Update imports in core/base/stage.py
- Update imports in core/base/agent.py
- Update imports in app/cli/graphrag.py

**4. Test** (5 min):

- Run 1-chunk test
- Verify no duplicate logs
- Verify errors still visible

---

## 🎯 Questions for Decision:

**1. Should error_handling decorators use logging.log_exception()?**

- Yes → error_handling depends on logging
- Creates clear hierarchy

**2. Should we remove duplicate \_log_event() for errors?**

- Yes → DRY, cleaner logs
- Keep \_log_event only for start/done (metrics)

**3. Proceed with reorganization now?**

- 30 minutes to clean separation
- Then approve error_handling library

---

## 💡 My Recommendation:

**Do Phase 4D now (30 min)**:

1. Move operation logging → logging library
2. Move log_exception → logging library
3. Update error_handling to use logging.log_exception
4. Remove duplicate \_log_event for errors
5. Test everything works

**Result**:

- Clean separation of concerns
- No overlaps
- No redundant logging
- Libraries interact properly

**Shall I proceed with Phase 4D reorganization?** 🎯
