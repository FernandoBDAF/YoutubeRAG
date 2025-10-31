# GraphRAG Stage Patterns Explanation

## Issue Identified

The GraphRAG stages I implemented (`graph_extraction.py`, `entity_resolution.py`, `graph_construction.py`, `community_detection.py`) used a method `self.get_read_collection()` that **does not exist** in the `BaseStage` class.

## Correct Pattern (from Existing Stages)

Looking at existing stages like `clean.py` and `chunk.py`, the correct pattern is:

### 1. **Source Collection Pattern**

```python
# Get source database and collection name
src_db = self.config.read_db_name or self.config.db_name
src_coll_name = self.config.read_coll or COLL_CONSTANT

# Get the collection using get_collection()
coll = self.get_collection(src_coll_name, io="read", db_name=src_db)
```

### 2. **Destination Collection Pattern**

```python
# Get destination database and collection name
dst_db = self.config.write_db_name or self.config.db_name
dst_coll_name = self.config.write_coll or COLL_CONSTANT

# Get the collection using get_collection()
coll = self.get_collection(dst_coll_name, io="write", db_name=dst_db)
```

### 3. **BaseStage Methods Available**

- `self.get_collection(name, io="read", db_name=None)` - Get a collection handle
- `self.db_read` - Read database handle
- `self.db_write` - Write database handle
- `self.db` - Default database handle

### 4. **Configuration Pattern**

Stages should use:

- `self.config.read_coll` or a constant like `COLL_CHUNKS` for source collection
- `self.config.write_coll` or a constant for destination collection
- `self.config.read_db_name` or `self.config.db_name` for source database
- `self.config.write_db_name` or `self.config.db_name` for destination database

## What Was Wrong in GraphRAG Stages

I incorrectly used:

```python
collection = self.get_read_collection()  # ❌ This method doesn't exist!
```

## Correct Implementation for GraphRAG Stages

For GraphRAG stages, since they all work with the `chunks` collection, it should be:

```python
def iter_docs(self):
    """Iterate over chunks that need processing."""
    src_db = self.config.read_db_name or self.config.db_name
    src_coll_name = self.config.read_coll or COLL_CHUNKS
    coll = self.get_collection(src_coll_name, io="read", db_name=src_db)

    # Query logic here
    query = {...}
    cursor = coll.find(query).limit(self.config.max or float("inf"))

    for doc in cursor:
        yield doc
```

## Fix Needed

All GraphRAG stages need to be updated to follow the existing pattern:

1. **graph_extraction.py** - Read from chunks, write back to chunks (with extraction metadata)
2. **entity_resolution.py** - Read from chunks (with extraction), write to `entities` and `entity_mentions` collections
3. **graph_construction.py** - Read from chunks (with resolution), write to `relations` collection
4. **community_detection.py** - Read from chunks (with construction), write to `communities` collection

## Collection Constants Needed

We need to add constants (if not already defined) for GraphRAG collections:

- `COLL_CHUNKS` - Already exists, used as source
- `COLL_ENTITIES` - For entities collection (or use GraphRAG collections helper)
- `COLL_RELATIONS` - For relations collection
- `COLL_COMMUNITIES` - For communities collection
- `COLL_ENTITY_MENTIONS` - For entity mentions collection

Or, since we have `get_graphrag_collections()` helper, we can use:

```python
from app.services.graphrag_indexes import get_graphrag_collections
graphrag_collections = get_graphrag_collections(self.db)
entities_collection = graphrag_collections["entities"]
```

## Summary

The error was using a non-existent `get_read_collection()` method instead of following the existing pattern:

1. Get source/destination DB from config
2. Get collection name from config or constant
3. Use `self.get_collection(collection_name, io="read"/"write", db_name=...)`

I'll fix all GraphRAG stages to follow this pattern correctly.
