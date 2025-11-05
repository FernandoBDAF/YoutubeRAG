# Plan: Concurrency & TPM Optimization

**Status**: Centralized - Planning Expansion  
**Last Updated**: November 5, 2025  
**Archive Reference**: `documentation/archive/concurrency-optimization-nov-2025/` (to be created)

---

## 📍 Current State

### What We Built

**Centralized Concurrency** (Production Ready):

- ✅ Generic TPM processor (`core/libraries/concurrency/tpm_processor.py`)
- ✅ Template methods in `BaseStage` for concurrent processing
- ✅ Auto-detection of concurrency mode
- ✅ Eliminated ~500 lines of duplicate code across stages
- ✅ Standardized TPM/RPM tracking
- ✅ Dynamic batch sizing

**Integrated Stages**:

- ✅ Extraction stage
- ✅ Entity resolution stage
- ✅ Graph construction stage
- ✅ Community summarization agent

### Current Capabilities

**Run Concurrent Processing**:

```python
# Automatic - just set concurrency flag
python app/cli/graphrag.py extraction --concurrency 300
```

**TPM Tracking**:

- Automatic token estimation
- Rate limiting (TPM + RPM)
- Progress tracking
- Throughput optimization

### Gaps Identified

1. **Limited Concurrency Library Coverage**

   - Only extraction-related logic centralized
   - No support for database operations concurrency
   - No support for file I/O concurrency
   - No support for external API calls (beyond OpenAI)

2. **Potential Concurrency Opportunities Not Exploited**

   - MongoDB batch operations could be parallelized
   - File processing in ingestion could be concurrent
   - Embedding generation (if we add it) needs concurrency
   - Vector similarity searches could be batched

3. **Missing Integration with Other Libraries**

   - No integration with retry library (should retry concurrent calls)
   - No integration with metrics library (concurrent operation metrics)
   - No integration with caching library (concurrent cache access)
   - No integration with error handling (concurrent error aggregation)

4. **Limited Configuration & Tuning**

   - No auto-tuning of concurrency based on system resources
   - No adaptive batch sizing based on success rates
   - No circuit breaker for overload
   - No backpressure mechanism

5. **Missing Documentation**
   - No comprehensive guide on when/how to use concurrency
   - No performance tuning guide
   - No troubleshooting guide for concurrent issues
   - No best practices documented

---

## 🎯 Goals & Scope

### Primary Goals

1. **Expand Concurrency Library** - Support more use cases beyond LLM calls
2. **Identify Concurrency Opportunities** - Scan entire codebase
3. **Integrate with Other Libraries** - Retry, metrics, caching, error handling
4. **Create Tuning Tools** - Auto-tuning, monitoring, optimization
5. **Document Best Practices** - Comprehensive concurrency guide

### Out of Scope

- Distributed processing (multi-machine)
- Message queue integration (Celery, RabbitMQ)
- Async/await refactoring (stick with threads for now)

---

## 📋 Implementation Plan

### Phase 1: Codebase Scan for Concurrency Opportunities

**Goal**: Identify all places that could benefit from concurrency

#### 1.1 Systematic Codebase Scan

**Scan Strategy**:

1. Search for loops processing independent items
2. Search for sequential API calls
3. Search for batch database operations
4. Search for file I/O operations
5. Search for CPU-intensive operations

**Script**: `scripts/scan_concurrency_opportunities.py`

```python
"""
Scan codebase for concurrency opportunities.

Looks for:
- Loops with independent iterations
- Sequential API calls
- Batch operations
- I/O operations

Usage:
    python scripts/scan_concurrency_opportunities.py \
        --output concurrency_opportunities.md
"""
```

**Implementation**:

- [ ] Create scan script
- [ ] Search patterns:
  - `for ... in ...` loops with API calls
  - `for ... in ...` loops with database operations
  - Sequential `.find()` or `.insert()` calls
  - File reading/writing in loops
- [ ] Generate report with line numbers and descriptions
- [ ] Categorize by potential impact (high/medium/low)
- [ ] Prioritize top 10 opportunities

#### 1.2 Manual Code Review

**Areas to Review**:

1. **Ingestion Pipeline** (`business/stages/ingestion/`):

   - File processing (transcripts, chunks)
   - API calls to YouTube/OpenAI
   - Database batch operations
   - Potential: Concurrent file processing, concurrent API calls

2. **RAG Services** (`business/services/rag/`):

   - Embedding generation (if we add it)
   - Vector similarity searches
   - Hybrid retrieval operations
   - Potential: Concurrent embedding, parallel searches

3. **Chat System** (`business/chat/`):

   - Memory loading
   - Query rewriting
   - Multi-retrieval strategies
   - Potential: Parallel retrieval, concurrent rewriting

4. **Scripts** (`scripts/`):
   - Data migration scripts
   - Comparison scripts
   - Analysis scripts
   - Potential: Concurrent database queries, parallel processing

**Implementation**:

- [ ] Review each area systematically
- [ ] Document opportunities in scan report
- [ ] Estimate effort and impact
- [ ] Create prioritized list

---

### Phase 2: Concurrency Library Expansion

**Goal**: Extend concurrency library to support more use cases

#### 2.1 Generic Concurrent Processor (Beyond LLM)

**New Module**: `core/libraries/concurrency/generic_processor.py`

**Features**:

- Process any iterable concurrently
- Configurable worker count
- Progress tracking
- Error handling and retry
- Result aggregation
- Support for both CPU-bound and I/O-bound tasks

**API**:

```python
from core.libraries.concurrency import run_concurrent

results = run_concurrent(
    items=items,
    processor_fn=lambda item: process(item),
    max_workers=10,
    progress_name="items",
    retry_on_error=True,
    error_handler=lambda item, error: log_error(item, error),
)
```

**Implementation**:

- [ ] Create `generic_processor.py`
- [ ] Implement with ThreadPoolExecutor
- [ ] Add progress bars
- [ ] Add error handling
- [ ] Add retry logic integration
- [ ] Test with various use cases
- [ ] Document API

#### 2.2 Database Batch Processor

**New Module**: `core/libraries/concurrency/db_processor.py`

**Features**:

- Concurrent MongoDB queries
- Batch insert/update operations
- Connection pool management
- Error handling per operation
- Transaction support (if needed)

**API**:

```python
from core/libraries/concurrency import batch_db_operation

# Concurrent batch inserts
batch_db_operation(
    collection=collection,
    operation="insert_many",
    items=documents,
    batch_size=1000,
    max_workers=5,
)

# Concurrent queries
results = concurrent_find(
    collection=collection,
    queries=[{"id": id} for id in ids],
    max_workers=10,
)
```

**Implementation**:

- [ ] Create `db_processor.py`
- [ ] Implement concurrent insert/update/delete
- [ ] Implement concurrent queries
- [ ] Add connection pooling
- [ ] Test with MongoDB
- [ ] Document API

#### 2.3 Rate Limiter Enhancements

**Current**: Basic TPM/RPM rate limiting

**Add**:

- Support for multiple limiters (different APIs)
- Adaptive rate limiting (slow down on errors)
- Circuit breaker (stop on repeated failures)
- Backpressure (slow producers when consumers overloaded)

**API Enhancements**:

```python
from core.libraries.rate_limiting import AdaptiveRateLimiter, CircuitBreaker

limiter = AdaptiveRateLimiter(
    initial_rpm=1000,
    max_rpm=5000,
    adapt_on_error=True,
)

breaker = CircuitBreaker(
    failure_threshold=10,
    timeout=60,
    half_open_retries=3,
)
```

**Implementation**:

- [ ] Extend `RateLimiter` class
- [ ] Add adaptive rate adjustment
- [ ] Implement circuit breaker
- [ ] Add backpressure mechanism
- [ ] Test with various scenarios
- [ ] Document patterns

---

### Phase 3: Integration with Other Libraries

**Goal**: Concurrency + Retry + Metrics + Error Handling + Caching

#### 3.1 Concurrency + Retry Integration

**Current**: Retry is per-call, concurrency is batch-level

**Goal**: Retry individual failures in concurrent batches

**Pattern**:

```python
from core.libraries.concurrency import run_concurrent_with_retry
from core.libraries.retry import RetryPolicy

results = run_concurrent_with_retry(
    items=items,
    processor_fn=api_call,
    retry_policy=RetryPolicy(max_attempts=3, backoff="exponential"),
    max_workers=10,
)
```

**Implementation**:

- [ ] Create `run_concurrent_with_retry` function
- [ ] Integrate retry logic per item
- [ ] Track retry statistics
- [ ] Add to concurrency library
- [ ] Test and document

#### 3.2 Concurrency + Metrics Integration

**Goal**: Automatic metrics for all concurrent operations

**Metrics to Track**:

- Worker utilization (active/total)
- Queue depth (items waiting)
- Throughput (items/sec)
- Error rate (failures/total)
- Latency (avg/p50/p95/p99)

**Pattern**:

```python
from core.libraries.concurrency import run_concurrent_with_metrics
from core.libraries.metrics import Counter, Histogram

results = run_concurrent_with_metrics(
    items=items,
    processor_fn=process,
    max_workers=10,
    metric_prefix="extraction",  # Auto-creates metrics
)
# Creates:
# - extraction_items_total
# - extraction_items_success
# - extraction_items_failed
# - extraction_duration_seconds
# - extraction_worker_utilization
```

**Implementation**:

- [ ] Extend `run_concurrent_with_tpm` to include metrics
- [ ] Auto-create standard metrics
- [ ] Track worker utilization
- [ ] Add latency histograms
- [ ] Test and document

#### 3.3 Concurrency + Caching Integration

**Goal**: Thread-safe caching for concurrent operations

**Use Cases**:

- LLM normalization results (already has basic cache)
- Embedding lookups
- Similarity calculations
- API response caching

**Pattern**:

```python
from core.libraries.concurrency import run_concurrent_with_cache
from core.libraries.caching import ThreadSafeCache

cache = ThreadSafeCache(max_size=10000)

results = run_concurrent_with_cache(
    items=items,
    processor_fn=expensive_operation,
    cache_key_fn=lambda item: item["id"],
    cache=cache,
    max_workers=10,
)
```

**Implementation**:

- [ ] Create thread-safe cache wrapper
- [ ] Integrate with concurrent processor
- [ ] Add cache hit/miss metrics
- [ ] Test for race conditions
- [ ] Document patterns

#### 3.4 Concurrency + Error Handling Integration

**Goal**: Aggregate errors from concurrent operations

**Pattern**:

```python
from core.libraries.concurrency import run_concurrent_with_error_handling
from core.libraries.error_handling import ErrorAggregator

error_aggregator = ErrorAggregator()

results = run_concurrent_with_error_handling(
    items=items,
    processor_fn=process,
    error_aggregator=error_aggregator,
    max_workers=10,
    continue_on_error=True,
)

# After processing
error_aggregator.log_summary()
error_aggregator.raise_if_critical()
```

**Implementation**:

- [ ] Create error aggregation for concurrent ops
- [ ] Categorize errors (retryable, fatal, transient)
- [ ] Implement continue-on-error logic
- [ ] Add error summary reporting
- [ ] Test and document

---

### Phase 4: Auto-Tuning & Optimization

**Goal**: Automatically optimize concurrency parameters

#### 4.1 Worker Count Auto-Tuning

**Goal**: Find optimal worker count for each operation

**Approach**:

- Start with small worker count (e.g., 10)
- Monitor throughput and error rate
- Gradually increase if throughput improves and errors low
- Decrease if errors increase or no throughput gain
- Settle on optimal count

**Implementation**:

- [ ] Create `AutoTuner` class
- [ ] Implement worker count tuning algorithm
- [ ] Add to concurrent processor as optional feature
- [ ] Test with various operations
- [ ] Document tuning process

#### 4.2 Batch Size Optimization

**Current**: Fixed batch size = `min(workers * 2, 1000)`

**Goal**: Adaptive batch sizing based on success rate and throughput

**Algorithm**:

- If success rate > 95% and throughput high → increase batch size
- If success rate < 80% → decrease batch size
- If throughput plateaus → adjust batch size
- Monitor and adapt every N batches

**Implementation**:

- [ ] Implement adaptive batch sizing
- [ ] Add to generic processor
- [ ] Test with extraction stage
- [ ] Measure improvement
- [ ] Document algorithm

#### 4.3 Resource Monitoring

**Goal**: Monitor system resources and throttle if needed

**Metrics**:

- CPU usage
- Memory usage
- Network bandwidth
- MongoDB connection count
- Thread count

**Throttling**:

- If CPU > 90% → reduce workers
- If memory > 80% → reduce batch size
- If connections > 80% of pool → queue operations

**Implementation**:

- [ ] Add resource monitoring to concurrent processor
- [ ] Implement throttling logic
- [ ] Add configuration for thresholds
- [ ] Test on resource-constrained systems
- [ ] Document behavior

---

### Phase 5: New Concurrent Operations

**Goal**: Apply concurrency to identified opportunities

#### 5.1 Concurrent File Processing (Ingestion)

**Current**: Sequential file processing

**Target**: `business/stages/ingestion/transcript_processor.py`

**Implementation**:

```python
from core.libraries.concurrency import run_concurrent

# Process multiple transcript files concurrently
results = run_concurrent(
    items=file_paths,
    processor_fn=process_transcript_file,
    max_workers=10,
    progress_name="transcripts",
)
```

**Steps**:

- [ ] Identify file processing loops
- [ ] Extract processor function
- [ ] Add concurrent processing
- [ ] Test for thread safety (file handles)
- [ ] Measure performance improvement
- [ ] Document change

#### 5.2 Concurrent Database Migrations

**Current**: Sequential chunk copying/updating

**Target**: `scripts/copy_chunks_to_validation_db.py`, `scripts/clean_graphrag_fields.py`

**Implementation**:

```python
from core.libraries.concurrency import batch_db_operation

# Concurrent chunk copying
batch_db_operation(
    source_collection=src_coll,
    target_collection=dst_coll,
    operation="copy",
    batch_size=1000,
    max_workers=5,
)
```

**Steps**:

- [ ] Review migration scripts
- [ ] Add concurrent processing
- [ ] Test for data consistency
- [ ] Measure speedup
- [ ] Document pattern

#### 5.3 Concurrent Embedding Generation (Future)

**Use Case**: If we add embedding-based features

**Pattern**:

```python
from core.libraries.concurrency import run_concurrent_with_tpm

embeddings = run_concurrent_with_tpm(
    items=texts,
    processor_fn=generate_embedding,
    estimate_tokens_fn=lambda text: len(text.split()),
    max_workers=50,
    target_tpm=1_000_000,
    target_rpm=50_000,
)
```

**Implementation**:

- [ ] Design embedding concurrency pattern
- [ ] Test with OpenAI embeddings API
- [ ] Measure throughput vs sequential
- [ ] Document pattern
- [ ] Add to library

#### 5.4 Concurrent Similarity Calculations

**Use Case**: Graph construction similarity calculations

**Current**: Sequential cosine similarity calculations

**Target**: Large-scale pairwise similarity

**Implementation**:

```python
from core.libraries.concurrency import run_concurrent

# Concurrent similarity matrix calculation
similarities = run_concurrent(
    items=entity_pairs,
    processor_fn=calculate_similarity,
    max_workers=20,
    progress_name="similarity_pairs",
)
```

**Steps**:

- [ ] Identify similarity calculation loops
- [ ] Parallelize pairwise calculations
- [ ] Test for correctness
- [ ] Measure speedup
- [ ] Document pattern

---

### Phase 6: Advanced Concurrency Patterns

**Goal**: Implement advanced patterns for complex scenarios

#### 6.1 Pipeline Parallelism

**Pattern**: Process items through multiple stages concurrently

**Use Case**: Chunk → Extract → Resolve → Construct (pipeline stages)

**Implementation**:

```python
from core.libraries.concurrency import PipelineProcessor

pipeline = PipelineProcessor(
    stages=[
        ("extract", extract_fn, 10),    # 10 workers
        ("resolve", resolve_fn, 5),     # 5 workers
        ("construct", construct_fn, 5), # 5 workers
    ],
    queue_size=100,
)

pipeline.process(chunks)
```

**Steps**:

- [ ] Design pipeline processor
- [ ] Implement with queues between stages
- [ ] Add backpressure handling
- [ ] Test with GraphRAG pipeline
- [ ] Measure end-to-end throughput
- [ ] Document pattern

#### 6.2 Fan-Out/Fan-In Pattern

**Pattern**: Distribute work, aggregate results

**Use Case**: Chunk → Extract N relationships → Aggregate to graph

**Implementation**:

```python
from core.libraries.concurrency import fan_out_fan_in

results = fan_out_fan_in(
    items=chunks,
    fan_out_fn=extract_relationships,  # Returns list of relationships
    fan_in_fn=aggregate_to_graph,      # Aggregates all relationships
    max_workers=20,
)
```

**Steps**:

- [ ] Implement fan-out/fan-in processor
- [ ] Handle result aggregation
- [ ] Test with extraction→aggregation
- [ ] Document pattern

#### 6.3 Priority Queue Processing

**Pattern**: Process high-priority items first

**Use Case**: Urgent chunks (user-requested) vs background processing

**Implementation**:

```python
from core.libraries.concurrency import PriorityProcessor

processor = PriorityProcessor(max_workers=10)

# Add high-priority items
processor.add(urgent_items, priority=1)

# Add low-priority items
processor.add(background_items, priority=10)

# Process (high-priority first)
processor.process()
```

**Steps**:

- [ ] Implement priority queue processor
- [ ] Test priority ordering
- [ ] Add to concurrency library
- [ ] Document use cases

---

### Phase 7: Integration Projects

#### 7.1 Concurrency + Retry Integration

**Goal**: Automatic retry for failed concurrent operations

**Pattern**:

```python
from core.libraries.concurrency import run_concurrent
from core.libraries.retry import retry_config

results = run_concurrent(
    items=items,
    processor_fn=api_call,
    max_workers=10,
    retry_config=retry_config(max_attempts=3, backoff="exponential"),
)
```

**Features**:

- Retry individual failed items
- Don't block other workers during retry
- Track retry statistics
- Exponential backoff per item

**Implementation**:

- [ ] Add retry parameter to concurrent processor
- [ ] Integrate with retry library
- [ ] Test retry behavior
- [ ] Measure success rate improvement
- [ ] Document pattern

#### 7.2 Concurrency + Metrics Integration

**Goal**: Automatic metrics for all concurrent operations

**Metrics**:

- `{operation}_concurrent_workers_active` (gauge)
- `{operation}_concurrent_items_queued` (gauge)
- `{operation}_concurrent_throughput` (counter)
- `{operation}_concurrent_duration_seconds` (histogram)
- `{operation}_concurrent_errors` (counter)

**Implementation**:

- [ ] Add metrics to concurrent processor
- [ ] Auto-create standard metrics
- [ ] Track in real-time
- [ ] Export to Prometheus
- [ ] Create Grafana dashboard
- [ ] Document metrics

#### 7.3 Concurrency + Caching Integration

**Goal**: Thread-safe caching for concurrent operations

**Pattern**:

```python
from core.libraries.concurrency import run_concurrent
from core.libraries.caching import thread_safe_cache

@thread_safe_cache(max_size=10000)
def expensive_operation(item):
    return compute(item)

results = run_concurrent(
    items=items,
    processor_fn=expensive_operation,  # Automatically cached
    max_workers=20,
)
```

**Implementation**:

- [ ] Create thread-safe cache decorator
- [ ] Integrate with concurrent processor
- [ ] Add cache metrics
- [ ] Test for race conditions
- [ ] Document patterns

#### 7.4 Concurrency + Error Handling Integration

**Goal**: Comprehensive error handling in concurrent operations

**Pattern**:

```python
from core.libraries.concurrency import run_concurrent
from core.libraries.error_handling import ErrorAggregator

aggregator = ErrorAggregator()

results = run_concurrent(
    items=items,
    processor_fn=process,
    max_workers=10,
    error_aggregator=aggregator,
    continue_on_error=True,
)

# After processing
if aggregator.has_errors():
    aggregator.log_summary()
    aggregator.raise_if_critical()
```

**Implementation**:

- [ ] Integrate error aggregator with concurrent processor
- [ ] Categorize errors (retryable, fatal, transient)
- [ ] Add error summaries
- [ ] Test error handling
- [ ] Document patterns

---

## 🔍 Identified Gaps & Solutions

### Gap 1: No Concurrency Profiling Tools

**Problem**: Can't easily profile concurrent operations to find bottlenecks

**Solution**:

- [ ] Create `scripts/profile_concurrency.py`
- [ ] Measure: worker utilization, queue depth, wait times
- [ ] Identify bottlenecks
- [ ] Generate profiling report
- [ ] Use for optimization

### Gap 2: No Concurrency Testing Framework

**Problem**: Hard to test concurrent code for race conditions

**Solution**:

- [ ] Create `tests/test_concurrency_library.py`
- [ ] Test for race conditions
- [ ] Test for deadlocks
- [ ] Test for resource leaks
- [ ] Stress testing with high concurrency

### Gap 3: No Concurrency Documentation

**Problem**: No comprehensive guide on when/how to use concurrency

**Solution**:

- [ ] Create `documentation/technical/CONCURRENCY.md`
- [ ] Document all patterns
- [ ] Include when to use each
- [ ] Add performance tuning guide
- [ ] Include troubleshooting

### Gap 4: No Concurrency Limits Configuration

**Problem**: Hard-coded limits, no global configuration

**Solution**:

- [ ] Create concurrency configuration system
- [ ] Central limits file or environment variables
- [ ] Per-operation override
- [ ] Document configuration

---

## 📊 Success Criteria

### Phase 1 Complete When:

- ✅ Codebase scan complete
- ✅ Top 10 opportunities identified and prioritized
- ✅ Effort estimates documented

### Phase 2 Complete When:

- ✅ Generic concurrent processor created
- ✅ Database batch processor created
- ✅ Rate limiter enhanced
- ✅ All tested and documented

### Phase 3 Complete When:

- ✅ Retry integration working
- ✅ Metrics integration working
- ✅ Caching integration working
- ✅ Error handling integration working

### Phase 4 Complete When:

- ✅ 5+ new concurrent operations implemented
- ✅ Performance improvements measured
- ✅ Patterns documented

---

## ⏱️ Time Estimates

**Phase 1** (Scan): 4-6 hours  
**Phase 2** (Library Expansion): 10-12 hours  
**Phase 3** (Integration): 8-10 hours  
**Phase 4** (New Operations): 6-8 hours  
**Phase 5** (Advanced Patterns): 8-10 hours

**Total**: 36-46 hours

---

## 🚀 Immediate Next Steps

1. **Archive old documentation** - Execute archiving plan
2. **Run codebase scan** - Identify all concurrency opportunities
3. **Prioritize opportunities** - Focus on high-impact, low-effort
4. **Start Phase 2** - Extend concurrency library
5. **Document patterns** - As we implement

---

## 📚 References

**Archive** (post-archiving):

- `documentation/archive/concurrency-optimization-nov-2025/`

**Current Docs**:

- `documentation/technical/GRAPHRAG-OPTIMIZATION.md`
- `documentation/technical/CONCURRENCY.md` (to be created)

**Code**:

- `core/libraries/concurrency/tpm_processor.py` - Current TPM processor
- `core/libraries/concurrency/__init__.py` - Library exports
- `core/base/stage.py` - Template methods for concurrency
- `core/libraries/rate_limiting/limiter.py` - Rate limiter

**Tests**:

- `tests/test_concurrency_library.py` (to be created)

---

**Status**: Ready for execution after archiving  
**Priority**: Medium - Foundation for performance improvements
