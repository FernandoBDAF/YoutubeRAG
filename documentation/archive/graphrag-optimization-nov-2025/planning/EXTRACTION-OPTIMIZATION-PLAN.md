# Extraction Stage Optimization Plan

**Date**: November 3, 2025  
**Problem**: Extraction took ~60 hours for 13k chunks  
**Goal**: Reduce to <10 hours with concurrency + rate limiting

---

## 📊 Current Performance Analysis

### Baseline Performance

- **Chunks**: 13,031
- **Time**: ~60 hours
- **Per chunk**: ~16.6 seconds average
- **Throughput**: ~3.6 chunks/minute
- **Bottleneck**: Sequential processing (one chunk at a time)

### Why So Slow?

1. **Sequential processing**: BaseStage.run() processes one chunk at a time
2. **LLM latency**: Each OpenAI call takes 2-5 seconds
3. **No parallelization**: Can't process multiple chunks simultaneously
4. **Rate limit buffer**: Conservative delays to avoid rate limits

---

## 🎯 Optimization Options

### Option 1: Concurrent Processing with run_llm_concurrent (RECOMMENDED) ⭐

**Approach**: Use existing concurrency library pattern from enrich/clean stages

**Implementation**:

```python
# In extraction stage setup()
from core.libraries.concurrency import run_llm_concurrent

# Change from sequential to concurrent
def process_all_chunks(self, chunks):
    # Agent factory for thread safety
    def create_agent():
        return GraphExtractionAgent(
            llm_client=self.llm_client,
            model_name=self.config.model_name,
            temperature=self.config.temperature
        )

    # Run concurrently with rate limiting
    results = run_llm_concurrent(
        chunks=chunks,
        agent_factory=create_agent,
        method_name='extract_from_chunk',
        max_workers=5,  # Process 5 chunks in parallel
        retries=1,  # Already has @retry_llm_call in agent
        qps=10,  # OpenAI rate limit (queries per second)
        on_error=lambda e, chunk: None  # Continue on errors
    )

    return results
```

**Performance Estimate**:

- **Workers**: 5 concurrent
- **Time**: 60 hours / 5 = **~12 hours** ✅
- **With 10 workers**: ~6 hours ✅
- **With 15 workers**: ~4 hours ✅

**Pros**:

- ✅ Massive speedup (5-15x)
- ✅ Library already exists and tested
- ✅ Pattern already used in enrich/clean stages
- ✅ Built-in rate limiting (qps parameter)
- ✅ Built-in retry logic
- ✅ Thread-safe (agent factory pattern)

**Cons**:

- ⚠️ Need to modify BaseStage.run() or override in extraction stage
- ⚠️ More complex error handling
- ⚠️ Needs testing with rate limits

**Implementation Time**: 1-2 hours

---

### Option 2: Batch Processing with Lower QPS (Conservative)

**Approach**: Process in batches with delays

**Implementation**:

```python
# In extraction stage
def handle_batch(self, docs, batch_size=10):
    results = []
    for i, doc in enumerate(docs):
        result = self.handle_doc(doc)
        results.append(result)

        # Rate limit: ~10 requests per minute
        if (i + 1) % 10 == 0:
            time.sleep(6)  # 6 seconds per 10 = 10/min

    return results
```

**Performance Estimate**:

- **Batch size**: 10
- **Delay**: 6 seconds per batch
- **Time**: Still ~60 hours (minimal improvement)

**Pros**:

- ✅ Simple implementation
- ✅ No concurrency complexity
- ✅ Safe rate limiting

**Cons**:

- ❌ No real speedup
- ❌ Still sequential
- ❌ Doesn't solve the problem

**Verdict**: ❌ Not recommended

---

### Option 3: Concurrent with OpenAI Rate Limiting Library (Advanced)

**Approach**: Combine concurrency + rate_limiting library + token tracking

**Implementation**:

```python
from core.libraries.concurrency import run_concurrent_with_limit
from core.libraries.rate_limiting import RateLimiter

# OpenAI rate limits (Tier 1 as example):
# - 500 requests per minute
# - 150,000 tokens per minute

# Create rate limiter
limiter = RateLimiter(rpm=450, name="openai_extraction")  # Conservative

# Process chunks concurrently
def process_chunk_with_limit(chunk):
    limiter.wait()  # Wait for rate limit
    return self.extraction_agent.extract_from_chunk(chunk)

results = run_concurrent_with_limit(
    func=process_chunk_with_limit,
    items=chunks,
    max_workers=10
)
```

**Performance Estimate**:

- **Workers**: 10 concurrent
- **Rate limit**: 450 RPM = 7.5 RPS
- **Time**: 13,031 chunks / 450 per min = **~29 minutes** ✅✅✅

**Pros**:

- ✅ Maximum possible speedup
- ✅ Respects OpenAI rate limits
- ✅ Uses our libraries (concurrency + rate_limiting)
- ✅ Can add token tracking
- ✅ Thread-safe

**Cons**:

- ⚠️ More complex
- ⚠️ Need to track token usage (prevent TPM limit)
- ⚠️ Need careful testing

**Implementation Time**: 2-3 hours

---

## 📊 Performance Comparison

| Option                    | Workers | Rate Limit | Time  | Speedup | Complexity |
| ------------------------- | ------- | ---------- | ----- | ------- | ---------- |
| **Current** (sequential)  | 1       | None       | 60h   | 1x      | Simple     |
| **Option 1** (concurrent) | 5       | QPS=10     | 12h   | 5x      | Medium     |
| **Option 1** (concurrent) | 10      | QPS=10     | 6h    | 10x     | Medium     |
| **Option 1** (concurrent) | 15      | QPS=10     | 4h    | 15x     | Medium     |
| **Option 3** (advanced)   | 10      | RPM=450    | 30min | 120x    | High       |

---

## 🎯 Recommended Approach

### **Recommended: Option 1 with 10-15 Workers** ⭐

**Why**:

- Proven pattern (already used in enrich/clean)
- Manageable complexity
- 6-12 hour runtime (vs 60 hours)
- Built-in rate limiting
- Library already exists

**Implementation**:

1. Override BaseStage processing in extraction stage
2. Use run_llm_concurrent (like enrich stage does)
3. Set max_workers=10-15
4. Set qps=10 (conservative)
5. Test with --max 100 first

**Steps**:

```python
# 1. Import in extraction stage
from core.libraries.concurrency import run_llm_concurrent

# 2. Override run() or add concurrent_run() method
def run_with_concurrency(self, config):
    # Setup as normal
    self.config = config
    self.setup()

    # Get all docs
    docs = list(self.iter_docs())

    # Agent factory
    def create_agent():
        return GraphExtractionAgent(
            llm_client=self.llm_client,
            model_name=self.config.model_name,
            temperature=self.config.temperature
        )

    # Run concurrently
    results = run_llm_concurrent(
        chunks=docs,
        agent_factory=create_agent,
        method_name='extract_from_chunk',
        max_workers=self.config.concurrency or 10,
        qps=10,
        retries=1
    )

    # Store results (batch)
    self._store_results(results, docs)

    self.finalize()
    return 0
```

---

## 🔍 Rate Limiting Considerations

### OpenAI Rate Limits (Tier Dependent)

**Tier 1** (example):

- 500 requests per minute (RPM)
- 150,000 tokens per minute (TPM)

**Tier 2** (example):

- 5,000 RPM
- 2,000,000 TPM

### Token Tracking (Optional Enhancement)

**Current**: Only request-based rate limiting  
**Enhanced**: Track both requests AND tokens

```python
# Advanced rate limiting with token tracking
from core.libraries.rate_limiting import RateLimiter

request_limiter = RateLimiter(rpm=450, name="openai_requests")
token_limiter = RateLimiter(rpm=140000, name="openai_tokens")  # Tokens per minute

def process_with_token_tracking(chunk):
    request_limiter.wait()

    # Estimate tokens (rough: ~4 chars per token)
    estimated_tokens = len(chunk['chunk_text']) / 4 + 1000  # Input + output

    # Wait for token capacity
    for _ in range(int(estimated_tokens / 1000)):
        token_limiter.wait()

    return agent.extract_from_chunk(chunk)
```

**Benefit**: Prevents hitting TPM limit  
**Complexity**: Higher  
**Need**: Only if hitting TPM limits

---

## 📋 Implementation Plan

### Phase 1: Quick Win - Moderate Concurrency (2 hours)

**Target**: 10x speedup (60h → 6h)

**Steps**:

1. Add concurrent processing to extraction stage (1 hour)
2. Use run_llm_concurrent with max_workers=10
3. Set conservative qps=10
4. Test with --max 100 (15 min)
5. Test with --max 1000 (2 hours)
6. Validate results match sequential

**Result**: Proven 10x speedup

---

### Phase 2: Advanced - Maximum Speed (optional, 3 hours)

**Target**: 120x speedup (60h → 30min)

**Steps**:

1. Implement token tracking
2. Use RateLimiter for both RPM and TPM
3. Increase workers to match rate limits
4. Test carefully with small batches
5. Monitor for rate limit errors

**Result**: Maximum possible speed

---

## ⚠️ Risks & Mitigations

### Risk 1: Hit Rate Limits

**Mitigation**: Start with qps=5, gradually increase

### Risk 2: Inconsistent Results

**Mitigation**: Test with --max 100, compare to sequential

### Risk 3: Memory Issues

**Mitigation**: Process in batches of 1000

### Risk 4: Database Overload

**Mitigation**: Use batch_insert for results (already have it)

---

## 🎯 My Recommendation

### Start with Option 1: 10 Workers, QPS=10

**Why**:

- Proven pattern (enrich/clean use this)
- 10x speedup (60h → 6h)
- Low risk
- Can increase workers if successful

**Implementation**:

1. Look at how enrich.py stage uses run_llm_concurrent
2. Copy that pattern to extraction stage
3. Test with --max 100 first
4. Scale up to full dataset

**Time**: 2 hours implementation + 6 hours runtime = **8 hours total** vs 60 hours

**Speedup**: **52 hours saved** ✅

---

**Next**: Should I create detailed implementation code for Option 1?
