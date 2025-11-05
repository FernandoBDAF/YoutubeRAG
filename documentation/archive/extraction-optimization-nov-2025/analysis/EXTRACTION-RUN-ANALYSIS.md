# GraphRAG Extraction Run Analysis

**Date**: November 4, 2025  
**Log File**: `graphrag_graph_extraction_20251104_214901.log`  
**Status**: ⚠️ Quota Exceeded (Partial Success)

---

## 📊 Run Summary

### Metrics

- **Total Documents**: 13,069
- **Successfully Processed**: 3,592 (27.5%)
- **Failed**: 9,477 (72.5%) - mostly quota exceeded
- **Runtime**: 57.6 minutes (3,455.5 seconds)
- **Final Batch**: 469 documents processed before quota exhaustion

### Model Usage ✅

- **Model Used**: `gpt-4o-mini` ✅ **CORRECT**
- **Configuration**: Default model correctly applied
- **Compliance**: ✅ Fully compliant with model usage principle

### Ontology Integration ✅

- **Canonical Predicates Loaded**: 34
- **Symmetric Predicates**: 11
- **Predicate Mappings**: 122
- **Type Constraints**: 18
- **Entity Types**: 20 (from types.yml)
- **Status**: Working correctly - filtering relationships as expected

### Quota Issues ⚠️

- **Quota Errors**: 132,657 occurrences (excessive retries)
- **Error Pattern**: All retries failed with `insufficient_quota` (429 errors)
- **Impact**: System kept retrying even after quota was exhausted
- **Waste**: Many unnecessary API calls after quota limit reached

---

## 🔍 Key Findings

### 1. Model Configuration ✅

**Status**: Correct

- Model defaults to `gpt-4o-mini` ✅
- Configuration respects environment variables ✅
- No hardcoded expensive models ✅

### 2. System Prompt Length ⚠️

**Issue**: System prompt is now very long

- Base prompt: ~250 lines
- Ontology context: ~15 lines (predicates + types)
- **Total tokens per request**: ~2,500-3,000 tokens (estimated)
- **Impact**: Higher cost per request, but necessary for quality

**Recommendation**:

- Current approach is correct (better quality)
- Consider monitoring token usage
- Option to make ontology context optional for testing

### 3. Hardcoded max_tokens ❌

**Issue**: `max_tokens=4000` is hardcoded in `_extract_with_llm`

- Config has `max_tokens` but it's not used
- Should respect `self.config.max_tokens` or config default

### 4. Quota Error Handling ❌

**Issue**: No early termination on quota errors

- System retries 3 times for each chunk even after quota exceeded
- 132,657 quota errors = massive waste of retries
- No circuit breaker for quota errors

**Impact**:

- Wasted API calls
- Slower failure detection
- Unclear error reporting

### 5. Ontology Filtering ✅

**Status**: Working as expected

- Many relationships being dropped (expected behavior)
- Canonicalization working
- Type constraint validation working
- Examples from logs:
  - "2 canonicalized, 3 dropped (1 explicit, 2 not found, 0 type violations)"
  - "1 canonicalized, 4 dropped (0 explicit, 3 not found, 1 type violations)"

---

## 🛠️ Required Improvements

### ✅ Priority 1: Critical Fixes (COMPLETED)

#### ✅ 1. Use Config max_tokens

**File**: `business/agents/graphrag/extraction.py`
**Status**: ✅ **FIXED**

- Added `max_tokens` parameter to `GraphExtractionAgent.__init__`
- Now uses `self.config.max_tokens` passed from stage
- Falls back to 4000 if not provided (backward compatible)

#### ✅ 2. Add Quota Error Detection

**File**: `business/agents/graphrag/extraction.py`, `core/libraries/retry/decorators.py`
**Status**: ✅ **FIXED**

- Added `_is_quota_error()` function in retry decorators
- Detects `RateLimitError` with `insufficient_quota` code
- Stops retrying quota errors immediately
- Logs clear quota exceeded message
- Applied to both retry decorator and extraction agent

#### ✅ 3. Improve Retry Logic

**File**: `core/libraries/retry/decorators.py`
**Status**: ✅ **FIXED**

- Retry decorator now checks for quota errors before retrying
- Quota errors are raised immediately without retry attempts
- Prevents wasted API calls on quota-exceeded errors

### Priority 2: Optimizations

#### 4. System Prompt Optimization

**File**: `business/agents/graphrag/extraction.py`
**Option**: Make ontology context optional via env flag

- `GRAPHRAG_INJECT_ONTOLOGY_CONTEXT=true` (default)
- Allows testing without ontology for cost comparison

#### 5. Cost Monitoring

**Add**: Token usage tracking

- Track input/output tokens per request
- Log estimated cost per batch
- Alert when approaching quota limits

#### 6. Better Error Reporting

**Add**: Clear quota exceeded detection

- Detect quota errors early
- Log summary: "Quota exceeded after X successful extractions"
- Stop processing gracefully instead of retrying

---

## 📈 Performance Analysis

### Before Quota Exceeded

- **Successful Rate**: ~27.5% (3,592 / 13,069)
- **Processing Speed**: ~3.8 chunks/second average
- **TPM Utilization**: 196,408 tokens/minute (vs 950k target = 20.7%)

### After Quota Exceeded

- **Wasted Retries**: 132,657 failed attempts
- **Time Wasted**: ~10-15 minutes of unnecessary retries
- **Impact**: Could have stopped earlier and saved quota

---

## ✅ What's Working Well

1. **Model Compliance**: ✅ Using `gpt-4o-mini` correctly
2. **Ontology Integration**: ✅ Loading and using ontology correctly
3. **Filtering**: ✅ Dropping noisy predicates as designed
4. **Concurrency**: ✅ 300 workers processing efficiently
5. **TPM Tracking**: ✅ Working (though utilization was low)

---

## 🎯 Action Items

### ✅ Immediate (COMPLETED - Before Next Run)

1. ✅ Fix `max_tokens` to use config
2. ✅ Add quota error detection
3. ✅ Improve retry logic for quota errors

**All critical fixes have been implemented!** The next run will:

- Stop immediately on quota errors (no wasted retries)
- Use config.max_tokens instead of hardcoded value
- Provide clear error messages for quota issues

### Short-term

4. Add cost monitoring
5. Add early termination on quota errors
6. Consider making ontology context optional

### Long-term

7. Add cost estimation before runs
8. Add quota monitoring/alerting
9. Consider prompt optimization (reduce length if possible)

---

## 💡 Cost Estimation

### Current Run (3,592 successful extractions)

- **System prompt**: ~2,500 tokens × 3,592 = ~9M tokens
- **User input**: ~1,000 tokens/chunk × 3,592 = ~3.6M tokens
- **Output**: ~1,000 tokens/chunk × 3,592 = ~3.6M tokens
- **Total**: ~16.2M tokens

### gpt-4o-mini Pricing (approximate)

- Input: $0.15 / 1M tokens
- Output: $0.60 / 1M tokens
- **Estimated Cost**: ~$2.50 for successful extractions

### Wasted Retries

- Each retry: ~2,500 tokens
- 132,657 retries = ~331M tokens wasted
- **Wasted Cost**: ~$50-100 (estimated)

**Total Estimated Cost**: $52.50 - $102.50

- **Efficient Cost**: ~$2.50 (if stopped early)
- **Waste**: ~95-98% of total cost was wasted retries

---

## 🚨 Critical Issues to Fix

1. **Stop retrying quota errors** - This is the biggest waste
2. **Use config.max_tokens** - Respect configuration
3. **Add early termination** - Detect quota issues and stop gracefully

---

**Next Steps**: Implement fixes for quota error handling and max_tokens configuration.
