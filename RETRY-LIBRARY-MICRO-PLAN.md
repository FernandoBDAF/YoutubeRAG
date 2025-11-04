# Retry Library - Micro Implementation Plan

**Date**: November 3, 2025  
**Total Time**: 5-7 hours  
**Approach**: Small steps with review points  
**Goal**: Automatic retries for transient failures

---

## 🎯 Micro-Phase Breakdown

### Phase 1A: Retry Policies (1 hour) ✋ REVIEW POINT

**What to Build**:

```python
# core/libraries/retry/policies.py
# - RetryPolicy base class
# - ExponentialBackoff
# - FixedDelay
# - NoRetry
```

**Deliverable**:

- 1 file (~100 lines)
- 4 policy classes
- Simple, configurable

**Review**: Policy design sufficient?

---

### Phase 1B: Retry Decorator (1.5 hours) ✋ REVIEW POINT

**What to Build**:

```python
# core/libraries/retry/decorators.py
# - @with_retry decorator
# - Integrates with logging (log retry attempts)
# - Integrates with metrics (track retry counts)
```

**Deliverable**:

- 1 file (~150 lines)
- Working decorator
- Library integration

**Review**: Decorator API clear?

---

### Phase 2A: Tests (30 min) ✋ REVIEW POINT

**What to Build**:

```python
# tests/core/libraries/retry/test_retry.py
# Test policies, decorator, integration
```

**Deliverable**:

- Tests passing
- Coverage verified

**Review**: Tests sufficient?

---

### Phase 2B: Package & Export (15 min) ✋ REVIEW POINT

**What to Build**:

```python
# core/libraries/retry/__init__.py
# Clean API exports
```

**Deliverable**:

- Public API defined

**Review**: API clear?

---

### Phase 3: Apply to BaseAgent (1 hour) ✋ REVIEW POINT

**What to Change**:

```python
# Remove manual retry loops from BaseAgent
# Use @with_retry on call_model()
```

**Deliverable**:

- BaseAgent simplified
- All 12 agents get automatic retries

**Review**: Verify no breaking changes

---

### Phase 4: Integration Test (30 min) ✋ REVIEW POINT

**What to Test**:

```bash
# Simulate LLM failure, verify retry
# Check retry metrics
# Verify backoff timing
```

**Deliverable**:

- Retry working in real code

**Review**: Retries working correctly?

---

## ⏸️ Total: 6 Review Points

**Estimated**: 4.5 hours total

**Starting with Phase 1A now (Retry Policies, 1 hour)**
