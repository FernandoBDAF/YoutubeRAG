# Refactor Application Guide - From Scan Results

**Date**: November 3, 2025  
**Purpose**: Guide for applying observability libraries during code review  
**Source**: Codebase scan results

---

## 📊 Scan Summary

**Scanned**: business/ layer (69 files)  
**Found**:

- 20 files with manual retry loops
- 83 exception handlers in 30 files
- 58 manual logger.error calls in 20 files

---

## 🎯 Priority 1: GraphRAG Agents (6 files) - HIGH IMPACT

### Files to Refactor:

1. `business/agents/graphrag/extraction.py`
2. `business/agents/graphrag/entity_resolution.py`
3. `business/agents/graphrag/relationship_resolution.py`
4. `business/agents/graphrag/community_detection.py`
5. `business/agents/graphrag/community_summarization.py`
6. `business/agents/graphrag/link_prediction.py`

### Pattern to Replace:

```python
# REMOVE THIS PATTERN (~50 lines per agent):
for attempt in range(max_retries):
    try:
        response = self.llm_client.beta.chat.completions.parse(...)
        return response
    except Exception as e:
        if attempt == max_retries - 1:
            logger.error(f"Extraction failed: {e}")
            raise
        logger.warning(f"Attempt {attempt + 1} failed, retrying...")
        time.sleep(backoff_delay)
```

### Replace With:

```python
# USE THIS (~5 lines, handled by BaseAgent):
# Just call the LLM - @retry_llm_call handles it
response = self.llm_client.beta.chat.completions.parse(...)
return response

# OR if not using BaseAgent's call_model:
@retry_llm_call(max_attempts=3)
def extract_with_llm(self, data):
    response = self.llm_client.beta.chat.completions.parse(...)
    return response
```

**Benefits**:

- ✅ Remove ~300 lines total
- ✅ Automatic retry logging
- ✅ Retry metrics tracked
- ✅ Consistent behavior

**Effort**: 2-3 hours (30 min per agent)

---

## 🎯 Priority 2: Database Operations (2 files) - HIGH VALUE

### Files to Refactor:

1. `business/services/graphrag/indexes.py` (6 exception handlers)
2. `business/services/rag/indexes.py` (2 exception handlers)

### Pattern to Replace:

```python
# REMOVE:
try:
    db.collection.create_index(...)
except Exception as e:
    logger.error(f"Index creation failed: {e}")
    # Sometimes passes, sometimes raises
```

### Replace With:

```python
# USE:
from core.libraries.error_handling import handle_errors
from core.libraries.retry import with_retry
from pymongo.errors import ConnectionError, ServerSelectionTimeoutError

@handle_errors(log_traceback=True, reraise=False, fallback=False)
@with_retry(max_attempts=3, retry_on=(ConnectionError, ServerSelectionTimeoutError))
def create_index_safe(collection, index_spec):
    collection.create_index(index_spec)
    return True
```

**Benefits**:

- ✅ Retry on transient DB errors
- ✅ Better error logging
- ✅ Metrics on DB failures
- ✅ More resilient

**Effort**: 1-2 hours

---

## 🎯 Priority 3: Service Error Handlers (10 files) - CONSISTENCY

### Files with Most Handlers:

1. `business/stages/graphrag/graph_construction.py` (14 handlers!)
2. `business/services/rag/retrieval.py` (4 handlers)
3. `business/services/rag/core.py` (3 handlers)
4. `business/services/graphrag/generation.py` (4 handlers)
5. `business/stages/graphrag/entity_resolution.py` (3 handlers)
6. `business/stages/graphrag/community_detection.py` (3 handlers)
7. `business/stages/ingestion/trust.py` (3 handlers)
8. `business/stages/ingestion/redundancy.py` (2 handlers)
9. `business/stages/ingestion/ingest.py` (5 handlers)
10. Others with 1-2 handlers each

### Pattern to Replace:

```python
# REMOVE:
try:
    result = operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")  # ❌ No type, no traceback
    return None
```

### Replace With:

```python
# USE:
from core.libraries.logging import log_exception

try:
    result = operation()
except Exception as e:
    log_exception(logger, "Operation failed", e)
    return None

# OR use decorator:
from core.libraries.error_handling import log_and_suppress

@log_and_suppress(fallback=None)
def operation():
    # Library handles everything
    ...
```

**Benefits**:

- ✅ Consistent error logging
- ✅ All errors tracked in metrics
- ✅ Exception types visible
- ✅ Full tracebacks

**Effort**: 2-3 hours (15-20 min per file)

---

## 📋 Refactor Checklist (Per File)

**For Each File with Exception Handlers**:

1. **Identify Pattern**:

   - [ ] Manual retry loop?
   - [ ] Database operation?
   - [ ] LLM call?
   - [ ] Generic try-except?

2. **Choose Library Approach**:

   - [ ] `@retry_llm_call` - For LLM calls
   - [ ] `@with_retry` - For DB/external ops
   - [ ] `@handle_errors` - For comprehensive error handling
   - [ ] `log_exception()` - For simple error logging
   - [ ] `@log_and_suppress` - For non-critical operations

3. **Apply**:

   - [ ] Import library functions
   - [ ] Replace pattern with library usage
   - [ ] Remove manual code
   - [ ] Test

4. **Verify**:
   - [ ] Error still logged correctly
   - [ ] Metrics tracked
   - [ ] Behavior unchanged
   - [ ] Simpler code

---

## 🗂️ Refactor Order

### Week 2 (Code Review):

**Monday** (8 hours):

- GraphRAG agents (6 files) - 2-3 hours
- Database services (2 files) - 1 hour
- Service errors (5 files) - 2 hours
- Document findings - 1 hour

**Tuesday** (8 hours):

- Service errors (5 more files) - 2 hours
- Stage-specific handlers (review) - 3 hours
- Chat module - 30 min
- Pipeline cleanup - 1 hour
- Document findings - 1 hour

**Wednesday** (8 hours):

- Remaining files - 3 hours
- Integration testing - 2 hours
- Update documentation - 2 hours
- Final review - 1 hour

---

## 📈 Expected Results

**After Complete Application**:

**Code Quality**:

- ~400-500 lines removed (manual retry + error handling)
- Consistent patterns throughout
- All errors logged same way
- All retries configured same way

**Observability**:

- 100% error visibility (all use log_exception)
- 100% retry tracking (all use @with_retry)
- 100% metrics coverage (all operations tracked)
- Complete cost tracking (all LLM calls)

**Maintainability**:

- Change library = change everywhere
- Easy to adjust retry behavior
- Easy to modify error handling
- Clear, consistent codebase

---

**This guide ensures systematic application of libraries during code review.**
