# EXECUTION_DEBUG: Entity Resolution Decorator Bug

**Type**: EXECUTION_DEBUG (Complex Issue Investigation)  
**Date**: 2025-11-12  
**Status**: ✅ ROOT CAUSE IDENTIFIED & FIX PROPOSED  
**Severity**: 🔴 CRITICAL - Blocks Achievement 2.1 baseline run  
**Impact**: All 400 chunks failed in Stage 2 (Entity Resolution)

---

## 📋 Issue Summary

**Error Message**:

```
ERROR | business.stages.graphrag.entity_resolution | handle_doc:250 |
Error processing chunk for entity resolution:
handle_errors.<locals>.decorator() got an unexpected keyword argument 'entities'
```

**Occurrence**: All 400 chunks in Stage 2 (Entity Resolution) failed with this error

**Impact**:

- ❌ Stage 2 (Resolution): 100% failure rate (400/400 chunks)
- ⚠️ Stage 3 (Construction): Skipped (no resolved entities)
- ⚠️ Stage 4 (Detection): Skipped (no graph to analyze)
- 🚫 **BLOCKS** Achievement 2.1 baseline establishment
- 🚫 **BLOCKS** Achievement 2.2 observability comparison

---

## 🔍 Investigation Process

### Step 1: Error Location

**Log Evidence** (line 8001):

```
2025-11-12 13:53:03 | ERROR | business.stages.graphrag.entity_resolution | handle_doc:250 |
Error processing chunk e09a7481-d6cb-493f-973d-a03beccbdacb for entity resolution:
handle_errors.<locals>.decorator() got an unexpected keyword argument 'entities'
```

**File**: `business/stages/graphrag/entity_resolution.py`  
**Line**: 250 (error handler in `handle_doc` method)

### Step 2: Call Site Analysis

**Found calls in `entity_resolution.py`**:

**Line 144-150** (save_entities_raw):

```python
self.intermediate_data.save_entities_raw(
    entities=raw_entities,          # ← 'entities' keyword argument
    chunk_id=chunk_id,
    video_id=video_id,
    trace_id=trace_id,
    extraction_method="llm"
)
```

**Line 194-200** (save_entities_resolved):

```python
self.intermediate_data.save_entities_resolved(
    entities=resolved_entities_data,  # ← 'entities' keyword argument
    chunk_id=chunk_id,
    video_id=video_id,
    trace_id=trace_id,
    resolution_method="fuzzy_match"
)
```

**Observation**: Both calls use `entities=...` as a keyword argument ✅ (This is correct)

### Step 3: Method Definition Analysis

**File**: `business/services/graphrag/intermediate_data.py`

**Line 102-110** (save_entities_raw):

```python
@handle_errors                    # ← NO PARENTHESES! 🔴
def save_entities_raw(
    self,
    entities: List[Dict[str, Any]],
    chunk_id: str,
    video_id: str,
    trace_id: str,
    extraction_method: str = "llm",
) -> int:
```

**Line 156-164** (save_entities_resolved):

```python
@handle_errors                    # ← NO PARENTHESES! 🔴
def save_entities_resolved(
    self,
    entities: List[Dict[str, Any]],
    chunk_id: str,
    video_id: str,
    trace_id: str,
    resolution_method: str = "fuzzy_match",
) -> int:
```

**🚨 ROOT CAUSE IDENTIFIED**: `@handle_errors` used **WITHOUT parentheses**

### Step 4: Decorator Definition Analysis

**File**: `core/libraries/error_handling/decorators.py`

**Lines 13-19** (decorator signature):

```python
def handle_errors(
    fallback: Optional[Any] = None,
    log_traceback: bool = True,
    capture_context: bool = True,
    reraise: bool = True,
    log_level: int = logging.ERROR,
) -> Callable:
```

**Lines 47-80** (decorator implementation):

```python
def decorator(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)  # ← Should pass through all args
        except Exception as e:
            # ... error handling ...
```

**Observation**: Decorator expects to be called WITH parentheses: `@handle_errors()`

---

## 🐛 Root Cause Analysis

### The Bug

**Incorrect Usage**:

```python
@handle_errors                    # ← NO PARENTHESES
def save_entities_raw(self, entities, ...):
    pass
```

**What Python Does**:

1. Python calls: `handle_errors(save_entities_raw)`
2. `save_entities_raw` function is passed as the `fallback` parameter (first positional arg)
3. `handle_errors` returns a `decorator` function
4. This `decorator` function becomes the new `save_entities_raw`

**When Method is Called**:

```python
self.intermediate_data.save_entities_raw(
    entities=raw_entities,  # ← Python thinks this is for the decorator!
    chunk_id=chunk_id,
    ...
)
```

Python tries to call: `decorator(entities=raw_entities, chunk_id=..., ...)`

But `decorator` function signature is: `decorator(func: Callable) -> Callable`

**Result**: `TypeError: decorator() got an unexpected keyword argument 'entities'`

### Why This Happens

**Decorator Design**:

- `@handle_errors()` ← WITH parentheses: Returns a decorator that wraps the function
- `@handle_errors` ← WITHOUT parentheses: Passes the function as `fallback` parameter

**Correct Pattern**:

```python
# Pattern 1: With parameters (most common)
@handle_errors(fallback=None, reraise=False)
def my_function():
    pass

# Pattern 2: Without parameters (MUST use parentheses)
@handle_errors()
def my_function():
    pass
```

**Incorrect Pattern** (current bug):

```python
# Pattern 3: Without parentheses (WRONG for this decorator)
@handle_errors
def my_function():
    pass
```

---

## ✅ The Fix

### Solution: Add Parentheses to Decorator

**File**: `business/services/graphrag/intermediate_data.py`

**Change 1** (Line 102):

```python
# BEFORE (WRONG):
@handle_errors
def save_entities_raw(

# AFTER (CORRECT):
@handle_errors()
def save_entities_raw(
```

**Change 2** (Line 156):

```python
# BEFORE (WRONG):
@handle_errors
def save_entities_resolved(

# AFTER (CORRECT):
@handle_errors()
def save_entities_resolved(
```

### Why This Works

With `@handle_errors()`:

1. Python calls: `handle_errors()` with default parameters
2. Returns a `decorator` function
3. `decorator(save_entities_raw)` wraps the function
4. Returns `wrapper` function that accepts `*args, **kwargs`
5. When called with `entities=...`, `wrapper` passes it through to the original function ✅

---

## 🧪 Testing Strategy

### Test 1: Quick Validation (50 chunks)

```bash
# After applying fix
python -m app.cli.graphrag --max 50 --db-name validation_01 --verbose
```

**Expected**:

- ✅ Stage 1 (Extraction): 50 chunks processed
- ✅ Stage 2 (Resolution): 50 chunks resolved (0 failed)
- ✅ Stage 3 (Construction): Graph built
- ✅ Stage 4 (Detection): Communities detected

### Test 2: Full Baseline (400 chunks)

```bash
# After Test 1 passes
python -m app.cli.graphrag --max 400 --db-name validation_01 --verbose
```

**Expected**:

- ✅ All 4 stages complete successfully
- ✅ Entities resolved and stored
- ✅ Relations created
- ✅ Communities detected

### Test 3: Verify Observability Disabled

```bash
# Check logs for confirmation
grep "QualityMetricsService (enabled=" logs/pipeline/graphrag_*.log
```

**Expected**: `QualityMetricsService (enabled=False)`

---

## 📊 Impact Assessment

### Before Fix

| Stage               | Status     | Chunks | Result                          |
| ------------------- | ---------- | ------ | ------------------------------- |
| **1. Extraction**   | ✅ Success | 400    | Entities extracted              |
| **2. Resolution**   | ❌ Failed  | 400    | All failed with decorator error |
| **3. Construction** | ⚠️ Skipped | 0      | No data to process              |
| **4. Detection**    | ⚠️ Skipped | 0      | No data to process              |

**Baseline Status**: ❌ INVALID (only 1 of 4 stages successful)

### After Fix (Expected)

| Stage               | Status     | Chunks | Result               |
| ------------------- | ---------- | ------ | -------------------- |
| **1. Extraction**   | ✅ Success | 400    | Entities extracted   |
| **2. Resolution**   | ✅ Success | 400    | Entities resolved    |
| **3. Construction** | ✅ Success | 400    | Graph built          |
| **4. Detection**    | ✅ Success | 400    | Communities detected |

**Baseline Status**: ✅ VALID (all 4 stages successful)

---

## 🔍 Related Issues

### Other Instances of Same Pattern

**Search for similar bugs**:

```bash
grep -rn "@handle_errors$" business/services/graphrag/
```

**Found**:

- `intermediate_data.py` line 102: `save_entities_raw` ← **FIX REQUIRED**
- `intermediate_data.py` line 156: `save_entities_resolved` ← **FIX REQUIRED**

**Check for other methods in same file**:

```bash
grep -A2 "@handle_errors" business/services/graphrag/intermediate_data.py
```

**Potential**: May be other methods with same issue in this file

---

## 📝 Prevention Strategy

### Code Review Checklist

When using `@handle_errors`:

- [ ] Always use parentheses: `@handle_errors()`
- [ ] Or specify parameters: `@handle_errors(fallback=None, reraise=False)`
- [ ] Never use without parentheses: `@handle_errors` ❌

### Linter Rule (Future)

**Suggestion**: Add a linter rule to detect `@handle_errors` without parentheses

**Pattern to detect**:

```python
@handle_errors\s*$  # Decorator without parentheses on same line
```

---

## 🎯 Resolution Steps

### Step 1: Apply Fix

```bash
# Edit file
vim business/services/graphrag/intermediate_data.py

# Change line 102:
# FROM: @handle_errors
# TO:   @handle_errors()

# Change line 156:
# FROM: @handle_errors
# TO:   @handle_errors()
```

### Step 2: Verify Fix

```bash
# Check the changes
git diff business/services/graphrag/intermediate_data.py
```

**Expected diff**:

```diff
-    @handle_errors
+    @handle_errors()
     def save_entities_raw(

-    @handle_errors
+    @handle_errors()
     def save_entities_resolved(
```

### Step 3: Test with Small Dataset

```bash
# Clean previous failed runs
mongosh "..." --eval "
  db.video_chunks.updateMany(
    {},
    {\$unset: {
      'graphrag_extraction': '',
      'graphrag_resolution': '',
      'graphrag_construction': '',
      'graphrag_detection': ''
    }}
  )
"

# Run test
python -m app.cli.graphrag --max 50 --db-name validation_01 --verbose
```

### Step 4: Verify Success

```bash
# Check logs for Stage 2 success
tail -100 logs/pipeline/graphrag_*.log | grep "entity_resolution.*complete"
```

**Expected**: `[entity_resolution] Batch 1 complete: 50 documents ... updated=50, failed=0`

### Step 5: Run Full Baseline

```bash
# Clean again
mongosh "..." --eval "db.video_chunks.updateMany({}, {\$unset: {...}})"

# Run full baseline
python -m app.cli.graphrag --max 400 --db-name validation_01 --verbose
```

---

## 📚 Documentation Updates

### Files to Update After Fix

1. **`BASELINE-RUN-RESULTS-FINAL-2025-11-12.md`**:

   - Add "BUG FIXED" section
   - Mark as superseded by new run

2. **`EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_21_01.md`**:

   - Add Phase 2.2: "Bug Fix & Re-run"
   - Document fix and new results

3. **New Baseline Report**:
   - Create `BASELINE-RUN-RESULTS-FIXED-2025-11-12.md`
   - Document successful run with all 4 stages

---

## 🎓 Lessons Learned

### Technical Lessons

1. **Decorator Syntax Matters**: `@decorator` vs `@decorator()` are fundamentally different
2. **Error Messages Can Be Misleading**: "unexpected keyword argument" pointed to wrong location
3. **Test Incrementally**: Start with small dataset (50 chunks) before full run (400 chunks)

### Process Lessons

1. **Root Cause Analysis**: Don't assume error location from error message
2. **Code Review**: Check decorator usage patterns across codebase
3. **Documentation**: EXECUTION_DEBUG format helps track complex issues

### Prevention

1. **Linting**: Add rules to catch decorator misuse
2. **Code Review**: Check all `@handle_errors` usage
3. **Testing**: Test error handling paths, not just happy paths

---

## ✅ Resolution Status

**Bug Status**: ✅ ROOT CAUSE IDENTIFIED  
**Fix Status**: ⏳ READY TO APPLY  
**Test Status**: ⏳ PENDING (after fix)  
**Documentation**: ✅ COMPLETE

**Next Action**: Apply fix to `business/services/graphrag/intermediate_data.py` (2 lines)

---

**Prepared By**: AI Debug Investigation  
**Investigation Time**: 15 minutes  
**Complexity**: Medium (misleading error message, required decorator analysis)  
**Confidence**: 100% (root cause definitively identified)
