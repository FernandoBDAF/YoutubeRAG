# Observability Library Application Opportunities

**Date**: November 3, 2025  
**Scope**: Scan of business/ layer for library application  
**Goal**: Identify where to apply error_handling, metrics, retry libraries

---

## 📊 Codebase Scan Results

### Manual Retry Loops Found: 20 files

- 6 GraphRAG agents (extraction, entity_resolution, relationship_resolution, community_detection, community_summarization, link_prediction)
- 4 GraphRAG stages (extraction, entity_resolution, graph_construction, community_detection)
- 3 Ingestion stages (embed, enrich)
- 2 Services (rag/core, graphrag/generation, transcripts)
- 2 Pipelines (graphrag, ingestion)
- 1 Chat module (query_rewriter)
- 2 Config files

**Pattern Found**:

```python
for attempt in range(max_retries):
    try:
        result = llm_call()
        break
    except Exception as e:
        if attempt == max_retries - 1:
            raise
        time.sleep(backoff)
```

**Should Use**: `@retry_llm_call` or `@with_retry`

---

### Exception Handlers Found: 83 in 30 files

**Categories**:

**1. Agent Exception Handlers** (6 agents, ~15 handlers):

- GraphRAG agents all have try-except around LLM calls
- Most log errors manually
- **Should use**: `log_exception()` helper

**2. Stage Exception Handlers** (13 stages, ~35 handlers):

- Document processing errors
- Database operation errors
- **Already handled** in BaseStage (but stages have additional try-except)
- **Should review**: Some may be unnecessary with base class error handling

**3. Service Exception Handlers** (~20 handlers):

- Database operations (indexes, retrieval)
- External API calls (transcripts)
- **Should use**: `@handle_errors` decorator or `log_exception()`

**4. Pipeline Exception Handlers** (~5 handlers):

- Stage execution errors
- **Already enhanced** with error_handling library
- May have nested handlers to clean up

---

### Manual logger.error Calls: 58 in 20 files

**Pattern Found**:

```python
logger.error(f"Operation failed: {e}")  # ❌ No exception type, no traceback
```

**Should Use**: `log_exception(logger, "Operation failed", e)`

**Files with Most**:

- graph_construction.py: 14 logger.error calls
- graphrag/generation.py: 4
- rag/retrieval.py: 4
- rag/core.py: 3
- entity_resolution.py: 3
- community_detection.py: 3

---

## 🎯 Priority Application Opportunities

### HIGH PRIORITY: Agent LLM Calls

**Location**: All 6 GraphRAG agents

**Current** (Manual retry in each agent):

```python
# In extraction agent, entity_resolution, etc.
for attempt in range(max_retries):
    try:
        response = self.llm_client.beta.chat.completions.parse(...)
        break
    except Exception as e:
        if attempt == max_retries - 1:
            logger.error(f"Failed: {e}")
            raise
        time.sleep(backoff)
```

**Should Be** (Using libraries):

```python
@retry_llm_call(max_attempts=3)
def extract_from_chunk(self, chunk):
    # Libraries handle retry automatically
    response = self.llm_client.beta.chat.completions.parse(...)
    return response
```

**Impact**:

- Remove ~50 lines of manual retry code per agent
- Automatic retry metrics
- Consistent retry behavior
- Better error logging

**Files**:

1. `business/agents/graphrag/extraction.py`
2. `business/agents/graphrag/entity_resolution.py`
3. `business/agents/graphrag/relationship_resolution.py`
4. `business/agents/graphrag/community_detection.py`
5. `business/agents/graphrag/community_summarization.py`
6. `business/agents/graphrag/link_prediction.py`

**Effort**: ~2-3 hours to refactor all 6 agents

---

### HIGH PRIORITY: Database Operations

**Location**: Services (graphrag/indexes, rag/indexes, etc.)

**Current**:

```python
try:
    db.collection.insert_one(doc)
except Exception as e:
    logger.error(f"Insert failed: {e}")
```

**Should Be**:

```python
@handle_errors(log_traceback=True, reraise=False, fallback=None)
@with_retry(max_attempts=3, retry_on=(ConnectionError, ServerSelectionTimeoutError))
def insert_document(doc):
    db.collection.insert_one(doc)
```

**Impact**:

- Automatic retry on transient DB errors
- Better error logging
- Metrics on DB failures

**Files**:

- `business/services/graphrag/indexes.py` (6 handlers)
- `business/services/rag/indexes.py` (2 handlers)

**Effort**: ~1-2 hours

---

### MEDIUM PRIORITY: Service Error Handling

**Location**: Services (rag/retrieval, rag/generation, graphrag/query, etc.)

**Current**:

```python
try:
    result = complex_operation()
except Exception as e:
    logger.error(f"Failed: {e}")
    return default_value
```

**Should Be**:

```python
@log_and_suppress(fallback=default_value)
def complex_operation():
    # Library handles error logging and fallback
    ...
```

**Impact**:

- Cleaner code
- Consistent error handling
- Automatic error metrics

**Files** (~10 service files with handlers)

**Effort**: ~2-3 hours

---

### MEDIUM PRIORITY: Stage-Specific Error Handling

**Location**: Individual stages beyond BaseStage

**Current**: Some stages have additional try-except beyond base class

**Review Needed**:

- Are these necessary with enhanced BaseStage?
- Should they use library functions?
- Can some be removed?

**Files**: All 13 stages

**Effort**: ~2-3 hours (part of code review)

---

### LOW PRIORITY: Chat Module

**Location**: `business/chat/query_rewriter.py`

**Current**:

```python
try:
    response = client.chat.completions.create(...)
except Exception:
    return user_query, default_mode, default_k, None
```

**Should Be**:

```python
@log_and_suppress(fallback=(user_query, default_mode, default_k, None))
@retry_llm_call(max_attempts=3)
def rewrite_query_with_llm():
    response = client.chat.completions.create(...)
    # Parse and return
```

**Effort**: 30 minutes

---

## 📋 Application Roadmap

### Phase 1: Agent Refactor (2-3 hours) ⭐ HIGH IMPACT

**Apply to 6 GraphRAG agents**:

- Remove manual retry loops
- Use `@retry_llm_call`
- Use `log_exception()` for errors
- Clean up ~300 lines of boilerplate

**Impact**: Consistent retry + better error visibility across all agents

---

### Phase 2: Database Operations (1-2 hours) ⭐ HIGH VALUE

**Apply to services with DB operations**:

- Add `@with_retry` for transient errors
- Use `@handle_errors` for comprehensive logging
- Track DB operation metrics

**Impact**: Resilient DB operations

---

### Phase 3: Service Error Handling (2-3 hours)

**Apply to ~10 service files**:

- Replace manual try-except with `@handle_errors`
- Use `@log_and_suppress` where appropriate
- Ensure all errors tracked in metrics

**Impact**: Consistent error handling, complete metrics

---

### Phase 4: Code Review Cleanup (During comprehensive review)

**Review each file for**:

- Unnecessary try-except (now handled by base class)
- Manual error logging (should use log_exception)
- Missing metrics (should track operations)
- Missing retry (should handle transient failures)

---

## 🎯 Quick Wins (Next 2 Hours)

**1. BaseAgent.call_model()** ✅ DONE

- Applied `@retry_llm_call`
- All 12 agents inherit automatic retry

**2. Apply to 6 GraphRAG Agents** (2 hours)

- Remove manual retry loops
- Clean up error handling
- **Result**: ~300 lines eliminated, consistent behavior

**3. Database Services** (1 hour)

- Add retry to insert/update operations
- Use handle_errors for logging

**Total**: 3 hours for massive improvement

---

## 📊 Estimated Impact

**Lines Removed**: ~400-500 (manual retry + error handling)  
**Consistency**: All errors logged same way  
**Metrics**: All retries and errors tracked  
**Maintainability**: Much easier to modify retry behavior

---

## 🚀 Recommendation

**Start with**: GraphRAG Agents (6 files, 2-3 hours)

- Highest code repetition
- Clearest library application
- Immediate impact

**Then**: Database services (2 files, 1 hour)

- High value (resilience)
- Simple application

**Total**: 3-4 hours for 8 files cleaned up

**Ready to proceed?**
