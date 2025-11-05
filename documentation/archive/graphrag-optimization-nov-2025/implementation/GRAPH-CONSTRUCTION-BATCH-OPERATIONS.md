# Graph Construction - 5 Batch Operations Explained

**File**: `business/stages/graphrag/graph_construction.py`  
**Date**: November 3, 2025  
**Status**: All 5 relationship types refactored to use batch_insert

---

## 🎯 The 5 Batch Insert Operations

These operations run in the `finalize()` method of graph_construction stage (after all chunks are processed):

### 1. **Co-occurrence Relationships**

**Function**: `_add_co_occurrence_relationships()` (line ~380)

**What it does**: Creates relationships between entities that appear in the same chunk

**Pattern**:

```python
# For each chunk with multiple entities:
#   For each pair of entities in that chunk:
#     Create "co_occurs_with" relationship

# BEFORE: Individual insert_one in loop
# AFTER: Collect all, then batch_insert
```

**Example**:

- Chunk has entities: ["Python", "Django", "Web Development"]
- Creates relationships:
  - Python co_occurs_with Django
  - Python co_occurs_with Web Development
  - Django co_occurs_with Web Development

**Refactored**: ✅ Lines ~452 (now uses batch_insert)

---

### 2. **Semantic Similarity Relationships**

**Function**: `_add_semantic_similarity_relationships()` (line ~481)

**What it does**: Creates relationships between entities with similar embeddings

**Pattern**:

```python
# For each pair of entities:
#   Calculate cosine similarity of embeddings
#   If similarity >= threshold (0.85):
#     Create "semantically_similar_to" relationship

# BEFORE: Individual insert_one in loop
# AFTER: Collect all, then batch_insert
```

**Example**:

- "Python" and "Programming Language" have similar embeddings
- Creates: Python semantically_similar_to Programming Language

**Refactored**: ✅ Lines ~590 (now uses batch_insert)

---

### 3. **Cross-chunk Relationships**

**Function**: `_add_cross_chunk_relationships()` (line ~617)

**What it does**: Creates relationships between entities in nearby chunks (temporal proximity)

**Pattern**:

```python
# For each video:
#   For chunks within adaptive window (1-5 chunks apart):
#     For entities in those chunks:
#       Create cross-chunk relationship based on entity types

# BEFORE: Individual insert_one in loop
# AFTER: Collect all, then batch_insert
```

**Example**:

- Chunk 1: mentions "Python"
- Chunk 2: mentions "Django" (within window)
- Creates: Python [predicate] Django (predicate based on types)

**Refactored**: ✅ Lines ~789 (now uses batch_insert)

---

### 4. **Bidirectional Relationships**

**Function**: `_add_bidirectional_relationships()` (line ~856)

**What it does**: Creates reverse relationships for directional predicates

**Pattern**:

```python
# For each existing relationship:
#   If predicate has a reverse (e.g., "uses" ↔ "used_by"):
#     Create reverse relationship

# BEFORE: Individual insert_one in loop
# AFTER: Collect all, then batch_insert
```

**Example**:

- Original: Python uses Django
- Creates reverse: Django used_by Python

**Reverse Predicates**:

- uses ↔ used_by
- contains ↔ contained_by
- manages ↔ managed_by
- teaches ↔ taught_by
- etc.

**Refactored**: ✅ Lines ~936 (now uses batch_insert)

---

### 5. **Predicted Link Relationships**

**Function**: `_add_predicted_relationships()` (line ~991)

**What it does**: Uses link prediction agent to predict missing relationships

**Pattern**:

```python
# Use link prediction algorithm:
#   Graph structure analysis (common neighbors)
#   Embedding similarity (if available)
# For predicted links above confidence threshold:
#   Create "predicted" relationship

# BEFORE: Individual insert_one in loop
# AFTER: Collect all, then batch_insert
```

**Example**:

- Entities A and B have common neighbors
- Adamic-Adar score suggests link
- Creates: A [predicted_predicate] B

**Refactored**: ✅ Lines ~1056 (now uses batch_insert)

---

## 📊 Batch Insert Details

### All 5 Operations Use Same Pattern

**Code Pattern**:

```python
# Collect relationships
relationships_to_insert = []

# ... logic to create relationship documents ...
for ...:
    relationship_doc = {...}
    relationships_to_insert.append(relationship_doc)

# Batch insert all at once
if relationships_to_insert:
    logger.info(f"Inserting {len(relationships_to_insert)} [TYPE] relationships in batch")
    result = batch_insert(
        collection=relations_collection,
        documents=relationships_to_insert,
        batch_size=500,
        ordered=False  # Continue on errors
    )
    added_count = result["inserted"]
    logger.info(
        f"[TYPE] batch insert: {result['inserted']}/{result['total']} successful, "
        f"{result['failed']} failed"
    )
```

**Benefits**:

- Single DB call instead of N calls
- Better error reporting (X/Y successful, Z failed)
- Continue on errors (ordered=False)
- Performance improvement for large graphs

---

## 🔍 What to Validate

When validating graph_construction stage, check logs for these 5 messages:

1. ✅ **Co-occurrence**: `"Co-occurrence batch insert: X/Y successful, Z failed"`
2. ✅ **Semantic similarity**: `"Semantic similarity batch insert: X/Y successful, Z failed"`
3. ✅ **Cross-chunk**: `"Cross-chunk batch insert: X/Y successful, Z failed"`
4. ✅ **Bidirectional**: `"Bidirectional batch insert: X/Y successful, Z failed"`
5. ✅ **Predicted links**: `"Link prediction batch insert: X/Y successful, Z failed"`

**Success Criteria**: All should show "Z failed = 0"

---

## 📈 Expected Impact

### For Large Graphs (13k chunks)

**Without batch_insert** (old code):

- 5 relationship types × hundreds of relationships each
- Potentially 1000s of individual `insert_one` calls
- Each call = separate DB roundtrip
- Slower, harder to track errors

**With batch_insert** (new code):

- 5 batch operations total (one per type)
- Each batch handles 500 documents at a time
- Clear statistics: "X/Y successful"
- Faster, better error handling

---

## ✅ Validation Checklist

When checking logs:

- [ ] Co-occurrence batch insert log entry
- [ ] Semantic similarity batch insert log entry
- [ ] Cross-chunk batch insert log entry
- [ ] Bidirectional batch insert log entry
- [ ] Link prediction batch insert log entry
- [ ] All show 0 failed
- [ ] All show successful counts

---

**The 5 batch operations** are the 5 types of relationship post-processing that graph_construction performs after all chunks are processed.
