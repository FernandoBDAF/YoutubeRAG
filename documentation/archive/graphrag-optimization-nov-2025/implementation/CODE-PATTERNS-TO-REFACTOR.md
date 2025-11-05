# Code Patterns to Refactor - Tracking Document

**Date**: November 3, 2025  
**Purpose**: Track code patterns identified during library implementation  
**Action**: Fix during comprehensive code review (Week 2-3)

---

## 🔍 Pattern #1: Duplicate Error Logging in BaseAgent

**Location**: `core/base/agent.py` (lines 129-138)

**Current Code**:

```python
except Exception as e:
    # 1. Log to _log_event (DEBUG, structured)
    error_formatted = format_exception_message(e)
    self._log_event({
        "type": "model_call:error",
        "model": self.config.model_name,
        "error": error_formatted,
    })

    # 2. Log with log_exception (ERROR, with traceback)
    log_exception(logger, f"[{self.name}] LLM call failed", e)
    return ""
```

**Problem**: Same error logged TWICE

- Once at DEBUG level (structured)
- Once at ERROR level (with traceback)

**Solution Options**:

**A. Remove \_log_event for errors** (Recommended):

```python
except Exception as e:
    # Single log using library
    log_exception(
        logger,
        f"[{self.name}] LLM call failed",
        e,
        context={'model': self.config.model_name}
    )
    return ""
```

**B. Keep \_log_event, remove log_exception**:

```python
except Exception as e:
    error_formatted = format_exception_message(e)
    self._log_event({
        "type": "model_call:error",
        "model": self.config.model_name,
        "error": error_formatted,
    })
    # Log only once, at WARNING level with traceback
    logger.warning(f"[{self.name}] LLM failed: {error_formatted}", exc_info=True)
    return ""
```

**C. Enhance \_log_event to use log_exception internally**:

```python
def _log_event(self, event):
    if event.get("type") == "model_call:error":
        # Use library for error events
        log_exception(logger, f"[{self.name}] Model call error", ...)
    else:
        # Keep DEBUG logging for non-errors
        logger.debug(...)
```

**Recommendation**: Option A (simplest, uses library)

**Priority**: Medium (fix during code review)  
**Effort**: 10 minutes  
**Impact**: Cleaner logs, no redundancy

---

## 🔍 Pattern #2: Manual Exception Type Extraction (ALREADY FIXED)

**Was in 5 places, now uses `log_exception()`**:

- ✅ app/cli/graphrag.py (2 places) → Fixed
- ✅ core/base/stage.py (2 places) → Fixed
- ✅ core/base/agent.py (1 place) → Fixed (but still has pattern #1)

**Status**: Resolved by creating log_exception() helper

---

## 🔍 Pattern #3: [TO BE DISCOVERED]

**During comprehensive code review, we'll find more patterns like**:

- Collection access repetition
- Configuration loading repetition
- Agent initialization repetition
- LLM call patterns
- Database operation patterns
- Etc.

**Will document here as we find them**

---

## 📋 Review Strategy

**During comprehensive code review** (Week 2-3):

1. Review each file systematically
2. Identify repeated patterns
3. Document here
4. Extract to libraries or helpers
5. Apply across codebase

**For each pattern**:

- Document location (file + lines)
- Show current code
- Propose solution
- Estimate effort
- Prioritize (High/Medium/Low)

---

## 🎯 Next Steps

**Now**: Document patterns as we see them  
**Week 2-3**: Systematic code review  
**Fix**: Apply library patterns consistently

---

**This document tracks patterns to fix during code review phase. Pattern #1 documented, more to come!**
