# Service Architecture and Implementation Guide

**Purpose**: Document all service modules, focusing on GraphRAG services and their integration with the pipeline.

---

## Service Overview

### What is a Service?

A **service** is a utility module that provides:

- Database operations (indexes, collections, queries)
- Cross-cutting functionality (rate limiting, utilities)
- Reusable components for stages and agents

Services are imported and used by stages/agents, not run standalone.

---

## GraphRAG Services

### GraphRAG Indexes Service

**File**: `business/services/graphrag/indexes.py`

**Purpose**: Manage GraphRAG collections, schemas, and indexes.

**Key Functions**:

**1. Collection Management**:

```python
def get_graphrag_collections(db):
    """Get all GraphRAG collections."""
    return {
        "entities": db.entities,
        "relations": db.relations,
        "communities": db.communities,
        "entity_mentions": db.entity_mentions
    }
```

**2. Collection Creation**:

```python
def ensure_graphrag_collections(db):
    """Create GraphRAG collections with JSON schema validation."""
    # Creates all 4 collections with validation rules
    # Handles "already exists" errors gracefully
```

**Why Schema Validation**: Ensures data integrity, catches errors early.

**3. Index Creation**:

```python
def create_graphrag_indexes(db):
    """Create all GraphRAG indexes."""

    # Entities - compound index for search
    db.entities.create_index([
        ("name", 1),
        ("type", 1),
        ("trust_score", -1)
    ])

    # Entities - text index for name search
    db.entities.create_index([
        ("name", "text"),
        ("canonical_name", "text")
    ])

    # Relations - bidirectional traversal
    db.relations.create_index([
        ("subject_id", 1),
        ("object_id", 1),
        ("confidence", -1)
    ])
    db.relations.create_index([
        ("object_id", 1),
        ("subject_id", 1),
        ("confidence", -1)
    ])

    # Communities - entity lookup
    db.communities.create_index([
        ("entities", 1),
        ("level", 1),
        ("coherence_score", -1)
    ])

    # Entity mentions - chunk and entity lookup
    db.entity_mentions.create_index([
        ("entity_id", 1),
        ("chunk_id", 1),
        ("confidence", -1)
    ])
```

**Why These Indexes**: Optimized for GraphRAG query patterns (entity search, graph traversal, community lookup).

**Cross-Reference**: See `GRAPH-RAG-CONSOLIDATED.md` Section 3

---

### GraphRAG Query Service (Future)

**File**: `business/services/graphrag/query.py` (partially implemented)

**Purpose**: Process queries using graph-aware techniques.

**Planned Functions**:

- `extract_query_entities()`: Extract entities from user query
- `expand_entity_graph()`: Find related entities
- `get_community_summaries()`: Retrieve community context
- `rank_by_centrality()`: Graph-based ranking

**Status**: Blocked on community detection fix. Will be implemented after communities are working.

**Cross-Reference**: See `GRAPH-RAG-CONSOLIDATED.md` Section 12

---

## Non-GraphRAG Services

### Indexes Service

**File**: `business/services/rag/indexes.py`

**Purpose**: Manage Atlas Search indexes for vector search.

**Key Functions**:

- `ensure_vector_search_index()`: Create/verify vector search index
- `ensure_hybrid_search_index()`: Create/verify hybrid search index

**GraphRAG Integration**: Complementary to GraphRAG (vector search + graph search).

---

### RAG Service

**File**: `business/services/rag/core.py`

**Purpose**: Core RAG functionality (vector search, generation).

**Key Functions**:

- `embed_query()`: Generate query embeddings
- `rag_answer()`: Traditional RAG query
- `rag_graphrag_answer()`: GraphRAG-enhanced query (future)

**GraphRAG Integration**: Will be enhanced to use graph context.

---

### Retrieval Service

**File**: `app/services/retrieval.py`

**Purpose**: Search and retrieval functions.

**Key Functions**:

- `vector_search()`: Atlas Vector Search
- `hybrid_search()`: Keyword + vector search
- `keyword_search()`: Text-based search
- `rerank_hits()`: Rerank results

**GraphRAG Integration** (future):

- Entity-aware filtering
- Graph-based ranking
- Community context retrieval

---

### Utilities Service

**File**: `app/services/utils.py`

**Purpose**: Database connection and common utilities.

**Key Functions**:

- `get_mongo_client()`: MongoDB client singleton
- Database connection management

**Used By**: All stages and services.

---

## Service Usage Pattern

### In Stages

```python
class MyStage(BaseStage):
    def setup(self):
        super().setup()

        # Use service functions
        from app.services.graphrag_indexes import get_graphrag_collections
        self.graphrag_collections = get_graphrag_collections(self.db)
```

### In Agents

```python
class MyAgent:
    def process(self, data):
        # Agents typically don't use services directly
        # They receive processed data from stages
        pass
```

### Direct Usage

```python
# For scripts and utilities
from app.services.graphrag_indexes import ensure_graphrag_collections

db = client[db_name]
ensure_graphrag_collections(db)
```

---

## GraphRAG Service Design Principles

### 1. Separation of Concerns

- **Services**: Database operations, indexing, utilities
- **Agents**: LLM operations, intelligent processing
- **Stages**: Orchestration, data flow

### 2. Idempotency

Collections and indexes can be created multiple times safely:

```python
try:
    db.create_collection("entities", validator=schema)
except:
    if "already exists" in error:
        pass  # OK, collection exists
    else:
        raise
```

### 3. Centralization

GraphRAG collections accessed via `get_graphrag_collections()` not direct DB access.

**Why**: Single point for collection names, validation, future enhancements.

---

## Cross-Reference

**Main Documentation**: `documentation/GRAPH-RAG-CONSOLIDATED.md`  
**Stage Integration**: `documentation/STAGE.md`  
**Agent Usage**: `documentation/AGENT.md`  
**Core Models**: `documentation/CORE.md`

---

**This document focuses on service architecture. For GraphRAG query services (future), see GRAPH-RAG-CONSOLIDATED.md Section 12.**
