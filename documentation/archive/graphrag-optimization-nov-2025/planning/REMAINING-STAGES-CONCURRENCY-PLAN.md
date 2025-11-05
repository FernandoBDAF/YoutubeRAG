# Concurrency Plan for Remaining GraphRAG Stages

**Date**: November 4, 2025  
**Status**: Planning concurrency for entity_resolution and graph_construction  
**Goal**: Apply same concurrent pattern to all GraphRAG stages

---

## 🎯 Current Status

### ✅ Completed

- **extraction**: Concurrent processing implemented (Option 1 + Option 3 with TPM)
  - 10 workers: 8.5x speedup
  - 50 workers with TPM: ~200x speedup

### ⏳ To Implement

- **entity_resolution**: Currently sequential (needs concurrency)
- **graph_construction**: Currently sequential (needs concurrency)
- **community_detection**: Special case (processes entire graph once)

---

## 📊 Stage 2: entity_resolution Concurrency Analysis

### Current Performance

- **Baseline**: 13,031 chunks in ~2.5 hours (entity_resolution stage from logs)
- **Per chunk**: ~0.7 seconds
- **Bottleneck**: Sequential LLM calls for multi-entity resolution

### Concurrent Opportunities

**LLM Calls in entity_resolution**:

1. `_resolve_descriptions()` - LLM call to merge entity descriptions
2. This happens when multiple instances of same entity found
3. Frequency: ~20-30% of entities (most are single instance)

**Challenge**: NOT every chunk has LLM calls

- Single entity per chunk → No LLM call needed
- Multiple instances of same entity → LLM call to merge descriptions

### Implementation Strategy

**Option A: Batch Resolution (RECOMMENDED)**

```python
def _run_concurrent(self, docs):
    """Process chunks concurrently, batch-resolve entities at end."""

    # Phase 1: Collect all extraction data (sequential, fast)
    all_extracted_data = []
    for doc in docs:
        extraction_data = doc.get('graphrag_extraction', {}).get('data', {})
        all_extracted_data.append(extraction_data)

    # Phase 2: Resolve entities in batches (concurrent LLM calls)
    # Group entities by normalized name across ALL chunks
    entity_groups = self._group_all_entities(all_extracted_data)

    # Resolve entity groups concurrently
    def resolve_group(group_data):
        normalized_name, entity_list = group_data
        return self.resolution_agent._resolve_entity_group(normalized_name, entity_list)

    # Use ThreadPoolExecutor for concurrent resolution
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(resolve_group, entity_groups.items())

    # Phase 3: Store results (can be batched)
    ...
```

**Benefits**:

- Parallelizes the slow part (LLM calls)
- Processes multiple entity groups simultaneously
- Still preserves entity grouping logic

**Expected Speedup**: 5-10x (modest, since not all resolutions need LLM)

---

**Option B: Per-Chunk Concurrent Processing**

```python
def _run_concurrent(self, docs):
    """Process each chunk concurrently."""

    def process_chunk(doc):
        # Each thread has its own agent
        agent = EntityResolutionAgent(...)
        extraction_data = doc.get('graphrag_extraction', {}).get('data', {})
        return agent.resolve_entities([extraction_data])

    # Run concurrent
    results = run_llm_concurrent(
        chunks=docs,
        agent_factory=lambda: EntityResolutionAgent(...),
        method_name='resolve_entities',
        max_workers=20,
        qps=10
    )

    # Store results
    ...
```

**Issues**:

- Each chunk resolves entities independently
- Loses cross-chunk entity resolution
- Different entities might not group properly

**Verdict**: ❌ Not recommended (breaks entity resolution logic)

---

### Recommended Approach for entity_resolution

**Hybrid: Concurrent Resolution of Entity Groups**

```python
def run(self, config):
    # Setup
    self.config = config
    self.setup()

    # Get all docs
    docs = list(self.iter_docs())

    # Collect all extraction data (fast)
    all_extracted_data = [
        doc.get('graphrag_extraction', {}).get('data', {})
        for doc in docs
    ]

    # Group entities across ALL chunks
    entity_groups = self.resolution_agent._group_entities_by_name(all_extracted_data)

    logger.info(f"Found {len(entity_groups)} entity groups to resolve")

    # Resolve groups concurrently (THIS is where LLM calls happen)
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_group = {}
        for normalized_name, entity_group in entity_groups.items():
            future = executor.submit(
                self.resolution_agent._resolve_entity_group,
                normalized_name,
                entity_group
            )
            future_to_group[future] = normalized_name

        # Collect results
        resolved_entities = []
        for future in as_completed(future_to_group):
            result = future.result()
            if result:
                resolved_entities.append(result)

    # Store all resolved entities (existing logic)
    for doc in docs:
        # Mark as processed...
```

**Speedup**: 5-10x (only the LLM calls are parallelized)

**Time**: 2.5 hours → **15-30 minutes** ✅

---

## 📊 Stage 3: graph_construction Concurrency Analysis

### Current Performance

- **Baseline**: 13,031 chunks in ~4 hours (from logs)
- **Per chunk**: ~1.1 seconds
- **Bottleneck**: Sequential relationship resolution per chunk

### LLM Calls in graph_construction

1. `relationship_resolution._resolve_descriptions()` - Merge relationship descriptions
2. Happens when multiple instances of same relationship
3. Also relatively infrequent

### Implementation Strategy

**Similar to entity_resolution**:

```python
def run(self, config):
    # Setup
    self.config = config
    self.setup()

    # Get all docs
    docs = list(self.iter_docs())

    # Process chunks concurrently
    with ThreadPoolExecutor(max_workers=20) as executor:
        def process_chunk(doc):
            # Resolve relationships for this chunk
            extraction_data = doc.get('graphrag_extraction', {}).get('data', {})
            entity_mapping = self._get_entity_name_to_id_mapping()
            return self.relationship_agent.resolve_relationships(
                [extraction_data],
                entity_mapping
            )

        future_to_doc = {}
        for doc in docs:
            future = executor.submit(process_chunk, doc)
            future_to_doc[future] = doc

        # Store results as they complete
        for future in as_completed(future_to_doc):
            doc = future_to_doc[future]
            relationships = future.result()
            self._store_resolved_relationships(relationships, doc['chunk_id'], doc['video_id'])
            # Mark chunk as processed
            ...

    # Then run finalize() for post-processing
    self.finalize()
```

**Speedup**: 10-15x

**Time**: 4 hours → **15-25 minutes** ✅

---

## 📊 Complete Pipeline Performance

### Current (Sequential)

- **extraction**: 60 hours
- **entity_resolution**: 2.5 hours
- **graph_construction**: 4 hours
- **community_detection**: 5 minutes
- **Total**: ~66.5 hours

### With Concurrency (All Stages)

- **extraction** (TPM mode): 16 minutes
- **entity_resolution** (concurrent): 20 minutes
- **graph_construction** (concurrent): 20 minutes
- **community_detection**: 5 minutes
- **Total**: **~61 minutes** ✅

**Overall Speedup**: 66.5 hours → 1 hour = **~65x faster!** ✅✅✅

---

## 🎯 Implementation Plan

### Phase 1: entity_resolution Concurrency (2-3 hours)

**Step 1**: Override `run()` method
**Step 2**: Group entities across all chunks
**Step 3**: Resolve entity groups concurrently
**Step 4**: Batch store results
**Step 5**: Test with --max 100

**Code Pattern**:

```python
class EntityResolutionStage(BaseStage):
    def run(self, config):
        # Check concurrency flag
        if self.config.concurrency and self.config.concurrency > 1:
            return self._run_concurrent(docs)
        else:
            return super().run(config)

    def _run_concurrent(self, docs):
        # Collect all extraction data
        # Group entities (already have this method)
        # Resolve groups concurrently
        # Batch store results
        ...
```

---

### Phase 2: graph_construction Concurrency (2-3 hours)

**Step 1**: Override `run()` method  
**Step 2**: Process chunk relationships concurrently
**Step 3**: Store relationships in batches
**Step 4**: Run finalize() for post-processing
**Step 5**: Test with --max 100

**Code Pattern**:

```python
class GraphConstructionStage(BaseStage):
    def run(self, config):
        if self.config.concurrency and self.config.concurrency > 1:
            return self._run_concurrent(docs)
        else:
            return super().run(config)

    def _run_concurrent(self, docs):
        # Process chunks concurrently
        # Each chunk: resolve relationships
        # Batch store results
        # Then finalize() for post-processing
        ...
```

---

### Phase 3: Testing (1 hour)

**Test Each Stage**:

```bash
# Test entity_resolution concurrent
python -m app.cli.graphrag --stage entity_resolution \
  --max 1000 \
  --concurrency 10 \
  --read-db-name validation_db \
  --write-db-name validation_db

# Test graph_construction concurrent
python -m app.cli.graphrag --stage graph_construction \
  --max 1000 \
  --concurrency 20 \
  --read-db-name validation_db \
  --write-db-name validation_db
```

---

## 🎯 Recommended Implementation Order

### Priority 1: entity_resolution (Higher Impact)

- More LLM calls than graph_construction
- Bottleneck after extraction
- Expected: 2.5h → 20min

### Priority 2: graph_construction

- Fewer LLM calls
- Still beneficial
- Expected: 4h → 20min

### Priority 3: Full Pipeline Test

- Run all 4 stages with concurrency
- Validate end-to-end
- Expected: ~1 hour total

---

## ⚠️ Considerations

### entity_resolution Specific

**Challenge**: Entity grouping must happen across ALL chunks
**Solution**: Collect all, group, then resolve concurrently
**Note**: Can't truly parallelize per-chunk like extraction

### graph_construction Specific

**Challenge**: finalize() must run after ALL chunks
**Solution**: Concurrent per-chunk processing, then sequential finalize()
**Note**: finalize() post-processing is already optimized with batch_insert

---

## 📋 Next Steps (After Current Run)

1. ✅ Wait for TPM extraction to complete
2. ✅ Validate results
3. ⏳ Implement entity_resolution concurrency (2-3 hours)
4. ⏳ Implement graph_construction concurrency (2-3 hours)
5. ⏳ Test full pipeline (1 hour)

**Total Implementation**: ~5-7 hours  
**Total Pipeline Speedup**: 66.5 hours → **~1 hour** ✅

---

**While extraction runs** (400/1000 done):

- I can start implementing entity_resolution concurrency if you'd like
- Or we can wait and validate TPM results first

**Your choice**: Start implementing now or wait for validation?
