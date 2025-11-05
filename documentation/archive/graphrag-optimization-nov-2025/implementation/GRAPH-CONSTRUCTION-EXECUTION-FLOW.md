# Graph Construction Execution Flow

**Date**: November 3, 2025  
**Clarification**: When the 5 batch operations execute

---

## 🔄 Execution Flow

### Phase 1: Per-Chunk Processing (iter_docs → handle_doc)

**For each chunk** that completed entity resolution:

```python
def handle_doc(self, doc):
    # 1. Get extraction data
    # 2. Resolve relationships for THIS chunk (using relationship_resolution agent)
    # 3. Store resolved relationships for THIS chunk
    # 4. Mark chunk as completed
```

**This phase**: Stores LLM-extracted relationships only

---

### Phase 2: Post-Processing (finalize)

**After ALL chunks are processed**, the `finalize()` method runs **ONCE**:

```python
def finalize(self):
    # Called by BaseStage after all documents processed

    # Add 5 types of auto-generated relationships:
    self._add_co_occurrence_relationships()      # Batch op #1
    self._add_semantic_similarity_relationships()  # Batch op #2
    self._add_cross_chunk_relationships()        # Batch op #3
    self._add_bidirectional_relationships()      # Batch op #4
    self._add_predicted_relationships()          # Batch op #5

    # Then call parent finalize for stats
    super().finalize()
```

**This phase**: Adds auto-generated relationships using batch_insert

---

## ✅ Your Observation is Correct

> "The 5 batch operations are not currently being called in the iter_docs function"

**Correct!** They're called in `finalize()` which runs:

1. **After** all chunks processed
2. **Once** for the entire graph
3. **Not** per-chunk

---

## 🎯 What to Expect When Running

### Step 1: Per-Chunk Relationship Resolution

```
Processing chunk 1/N
Resolving relationships...
Stored X relationships

Processing chunk 2/N
...
(repeat for all chunks)
```

### Step 2: Graph Post-Processing (finalize)

```
Starting co-occurrence relationship post-processing
Inserting X co-occurrence relationships in batch
Co-occurrence batch insert: X/Y successful, 0 failed

Starting semantic similarity relationship post-processing
Inserting X semantic similarity relationships in batch
Semantic similarity batch insert: X/Y successful, 0 failed

Starting cross-chunk relationship post-processing
...
(all 5 batch operations)

Summary: processed=N updated=N skipped=0 failed=0
```

---

## 📋 Validation Checklist

When you run graph_construction:

**During Processing**:

- [ ] Processes all chunks with completed resolution
- [ ] Resolves relationships per chunk
- [ ] Stores relationships to DB

**During Finalize** (after all chunks):

- [ ] Co-occurrence batch insert runs
- [ ] Semantic similarity batch insert runs
- [ ] Cross-chunk batch insert runs
- [ ] Bidirectional batch insert runs
- [ ] Link prediction batch insert runs
- [ ] All show "0 failed"

---

**Ready to run**: The 5 batch operations will execute in `finalize()` after all chunks are processed! ✅
