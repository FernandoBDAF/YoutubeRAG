# Library Integration Gaps Analysis

**Date**: November 3, 2025  
**Issue**: Are libraries properly integrated or working in silos?

---

## 🔍 Current Integration Status

### ✅ What's Integrated:

**error_handling → logging**:

```python
# error_handling uses logging
from core.libraries.logging import log_exception

@handle_errors(...)  # Uses log_exception internally
```

✅ **Clean integration!**

---

### ❌ What's NOT Integrated (Gap Found!):

**Metrics ← error_handling/logging**: No automatic integration!

**Current Pattern** (Manual):

```python
# In BaseStage:
except Exception as e:
    self.stats["failed"] += 1              # Manual stat
    _documents_failed.inc(...)              # Manual metric
    log_exception(logger, "Error", e)       # Manual log
```

**Problem**: Three separate manual calls!

- Track error in stats
- Track error in metrics
- Log error
- **Not integrated!**

---

## 🎯 Integration Opportunity

### Option A: log_exception() Auto-Tracks Metrics ⭐ RECOMMENDED

**Enhance log_exception() to track error metrics**:

```python
# core/libraries/logging/exceptions.py
def log_exception(logger, message, exception, ...):
    # 1. Format and log (current)
    logger.error(f"{message}: {error_type}: {error_msg}", exc_info=True)

    # 2. Auto-track error metric (NEW!)
    from core.libraries.metrics import Counter, MetricRegistry

    error_counter = MetricRegistry.get_instance().get('errors_logged')
    if error_counter:
        error_counter.inc(labels={'type': error_type})
```

**Usage** (simplified):

```python
# One call does everything:
log_exception(logger, "Processing failed", e)

# Automatically:
# - Logs error with traceback ✅
# - Increments errors_logged counter ✅
# - No manual metric tracking needed!
```

**Benefits**:

- ✅ DRY - one call tracks everything
- ✅ Consistent - can't forget to track metrics
- ✅ Integrated - libraries work together

---

### Option B: Decorator Tracks Metrics

**@handle_errors auto-tracks**:

```python
@handle_errors(track_metrics=True)  # NEW parameter
def risky_operation():
    ...

# Decorator automatically:
# - Catches exception
# - Logs it
# - Increments error counter
```

---

### Option C: Keep Separate (Current)

**Pros**:

- Independent libraries
- Explicit control

**Cons**:

- Manual everywhere
- Easy to forget
- Repetitive

---

## 📊 Proposed Integration

### 1. Create Global Error Counter

```python
# core/libraries/metrics/collectors.py or registry.py
# Global metric for all errors
_global_errors = Counter(
    'errors_total',
    'Total errors by type and component',
    labels=['error_type', 'component']
)
```

### 2. Enhance log_exception()

```python
# core/libraries/logging/exceptions.py
def log_exception(logger, message, exception, ...):
    error_type = type(exception).__name__

    # Log (current)
    logger.error(f"{message}: {error_type}: ...", exc_info=True)

    # Auto-track metric (NEW)
    from core.libraries.metrics import MetricRegistry
    registry = MetricRegistry.get_instance()
    error_counter = registry.get('errors_total')

    if error_counter:
        # Extract component from logger name or message
        component = logger.name.split('.')[-1]
        error_counter.inc(labels={'error_type': error_type, 'component': component})
```

### 3. Simplify BaseStage/BaseAgent

**Remove manual metric tracking**:

```python
# BEFORE (manual):
except Exception as e:
    _documents_failed.inc(...)  # Manual
    log_exception(...)          # Manual

# AFTER (integrated):
except Exception as e:
    log_exception(...)  # Automatically tracks error metric!
```

---

## 🎯 My Recommendation

**Implement Option A** (5-10 minutes):

1. Create global `errors_total` counter in registry
2. Enhance `log_exception()` to auto-track
3. Remove manual error metric tracking from BaseStage/BaseAgent
4. Test that errors are automatically counted

**Benefits**:

- Libraries work together
- Less code
- Can't forget to track
- Consistent everywhere

---

## 📋 Other Integration Points to Consider

### logging → metrics?

**Should log_operation_complete() track metrics?**

Currently:

```python
log_operation_complete("stage_extraction", duration=10.5, processed=100)
# Just logs, doesn't track metrics
```

Could be:

```python
log_operation_complete("stage_extraction", duration=10.5, processed=100)
# Automatically tracks operation_duration histogram!
```

**But**: We're already tracking in BaseStage explicitly. Might be redundant.

---

### metrics → logging?

**Should metrics log when they change?**

Probably not - would be too noisy.

---

## ✅ Main Gap: log_exception() Should Auto-Track

**This is the key integration point!**

**Shall I implement it now?** (5-10 minutes to integrate)

Or document as TODO for later?
