# Stage Architecture and Implementation Guide

**Purpose**: Document all pipeline stages, focusing on GraphRAG stages and their integration with the ingestion pipeline.

---

## Stage Overview

### What is a Stage?

A **stage** is a self-contained processing unit that:

- Reads from one or more MongoDB collections
- Processes documents through transformation logic
- Writes results to MongoDB collections
- Tracks statistics (processed, updated, skipped, failed)
- Implements error handling and retry logic

### BaseStage Pattern

All stages extend `BaseStage` (`core/base_stage.py`):

```python
class MyStage(BaseStage):
    name = "my_stage"              # Registry key for pipeline lookup
    description = "Stage purpose"   # Human-readable description
    ConfigCls = MyStageConfig       # Configuration class

    def __init__(self):
        """Initialize stage (no arguments)."""
        super().__init__()

    def setup(self):
        """Initialize stage-specific resources after config is set."""
        super().setup()
        # Initialize agents, connections, etc.

    def iter_docs(self):
        """Return iterable of documents to process."""
        # Query source collection
        # Return cursor or generator

    def handle_doc(self, doc):
        """Process a single document."""
        # Transform document
        # Write to destination collection
        # Return None (writes directly to DB)

    def finalize(self):
        """Clean up after processing all documents."""
        super().finalize()  # Logs statistics
```

### Key Methods

**`setup()`**: Initialize resources

- Called after config is set
- Initialize LLM clients, agents, database connections
- One-time setup before processing

**`iter_docs()`**: Provide documents

- Query source collection(s)
- Filter for documents needing processing
- Return cursor or generator

**`handle_doc(doc)`**: Process document

- Core transformation logic
- Write results to destination
- Update statistics
- Return None (DB writes happen inside)

**`finalize()`**: Post-processing

- Runs after all documents processed
- Perfect for graph post-processing
- Log final statistics

---

## GraphRAG Stages

### Graph Extraction Stage

**File**: `app/stages/graph_extraction.py`  
**Agent**: `agents/graph_extraction_agent.py`  
**Config**: `config/graphrag_config.py` → `GraphExtractionConfig`

**Purpose**: Extract entities and relationships from text chunks using LLM with structured output.

**Pattern**: Read chunks → Extract with LLM → Write back to chunks

```python
class GraphExtractionStage(BaseStage):
    name = "graph_extraction"
    description = "Extract entities and relationships from text chunks"
    ConfigCls = GraphExtractionConfig

    def setup(self):
        super().setup()
        # Initialize OpenAI client
        self.llm_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Initialize extraction agent
        self.extraction_agent = GraphExtractionAgent(
            llm_client=self.llm_client,
            model_name=self.config.model_name,
            temperature=self.config.temperature
        )

    def iter_docs(self):
        # Read chunks without extraction
        query = {
            "chunk_text": {"$exists": True, "$ne": ""},
            "$or": [
                {"graphrag_extraction": {"$exists": False}},
                {"graphrag_extraction.status": {"$ne": "completed"}}
            ],
            "_test_exclude": {"$exists": False}  # Skip test-excluded chunks
        }

        collection = self.get_collection(COLL_CHUNKS, io="read")
        return collection.find(query).limit(self.config.max or float("inf"))

    def handle_doc(self, doc):
        # Extract entities and relationships
        knowledge = self.extraction_agent.extract_from_chunk(doc)

        # Write extraction results back to chunk
        collection = self.get_collection(COLL_CHUNKS, io="write")
        collection.update_one(
            {"chunk_id": doc["chunk_id"]},
            {"$set": {"graphrag_extraction": {
                "status": "completed",
                "data": knowledge_to_dict(knowledge)
            }}}
        )

        self.stats["updated"] += 1
        return None  # Writes directly to DB
```

**Key Decisions**:

- Uses `chunk_text` field (not summary) for extraction
- Stores extraction in chunk metadata (not separate collection)
- Enhanced prompt extracts **multiple relationship types** per entity pair

**Configuration**:

```python
@dataclass
class GraphExtractionConfig(BaseStageConfig):
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.1
    max_entities_per_chunk: int = 10
    max_relationships_per_chunk: int = 15
    llm_retries: int = 3
    llm_backoff_s: float = 1.0
```

**Cross-Reference**: See `documentation/GRAPH-RAG-CONSOLIDATED.md` Section 4.1

---

### Entity Resolution Stage

**File**: `app/stages/entity_resolution.py`  
**Agent**: `agents/entity_resolution_agent.py`  
**Config**: `EntityResolutionConfig`

**Purpose**: Canonicalize entities across chunks, resolving duplicates and variants.

**Pattern**: Read chunks with extractions → Resolve entities → Write to entities + entity_mentions collections

```python
class EntityResolutionStage(BaseStage):
    name = "entity_resolution"
    description = "Resolve and canonicalize entities across chunks"
    ConfigCls = EntityResolutionConfig

    def setup(self):
        super().setup()
        self.llm_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.resolution_agent = EntityResolutionAgent(
            llm_client=self.llm_client,
            model_name=self.config.model_name
        )
        self.graphrag_collections = get_graphrag_collections(self.db)

    def iter_docs(self):
        # Read chunks with completed extraction
        query = {
            "graphrag_extraction.status": "completed",
            "$or": [
                {"graphrag_resolution": {"$exists": False}},
                {"graphrag_resolution.status": {"$ne": "completed"}}
            ],
            "_test_exclude": {"$exists": False}
        }

        collection = self.get_collection(COLL_CHUNKS, io="read")
        return collection.find(query).limit(self.config.max or float("inf"))

    def handle_doc(self, doc):
        # Extract entity data
        extraction_data = doc["graphrag_extraction"]["data"]

        # Resolve entities
        resolved_entities = self.resolution_agent.resolve_entities([extraction_data])

        # Store in entities collection
        for entity in resolved_entities:
            entity_id = ResolvedEntity.generate_entity_id(entity.canonical_name)

            self.graphrag_collections["entities"].update_one(
                {"entity_id": entity_id},
                {"$set": entity.dict(), "$inc": {"source_count": 1}},
                upsert=True
            )

            # Store entity mention
            self.graphrag_collections["entity_mentions"].insert_one({
                "entity_id": entity_id,
                "chunk_id": doc["chunk_id"],
                "video_id": doc["video_id"],
                "confidence": entity.confidence
            })

        # Mark chunk as resolved
        collection = self.get_collection(COLL_CHUNKS, io="write")
        collection.update_one(
            {"chunk_id": doc["chunk_id"]},
            {"$set": {"graphrag_resolution": {"status": "completed"}}}
        )

        self.stats["updated"] += 1
        return None
```

**Key Decisions**:

- Entity ID generation uses MD5(canonical_name) for consistency
- Stores both entities (deduplicated) and mentions (all occurrences)
- LLM summarization for entities with multiple descriptions

**Cross-Reference**: See `GRAPH-RAG-CONSOLIDATED.md` Section 4.2

---

### Graph Construction Stage

**File**: `app/stages/graph_construction.py`  
**Agent**: `agents/relationship_resolution_agent.py`  
**Config**: `GraphConstructionConfig`

**Purpose**: Build knowledge graph from resolved entities and relationships, including comprehensive post-processing.

**Pattern**: Read chunks with resolutions → Resolve relationships → Write to relations → **Run post-processing**

**This is the MOST COMPLEX stage** due to 5 post-processing methods in `finalize()`.

```python
class GraphConstructionStage(BaseStage):
    name = "graph_construction"
    description = "Build knowledge graph with post-processing"
    ConfigCls = GraphConstructionConfig

    def setup(self):
        super().setup()
        self.llm_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.relationship_agent = RelationshipResolutionAgent(
            llm_client=self.llm_client
        )
        self.graphrag_collections = get_graphrag_collections(self.db)

    def iter_docs(self):
        # Read chunks with completed resolution
        query = {
            "graphrag_resolution.status": "completed",
            "$or": [
                {"graphrag_construction": {"$exists": False}},
                {"graphrag_construction.status": {"$ne": "completed"}}
            ],
            "_test_exclude": {"$exists": False}
        }

        collection = self.get_collection(COLL_CHUNKS, io="read")
        return collection.find(query).limit(self.config.max or float("inf"))

    def handle_doc(self, doc):
        # Process relationships from extraction data
        # Resolve and store in relations collection
        # (Implementation details in GRAPH-RAG-CONSOLIDATED.md)

        # Mark chunk as constructed
        collection = self.get_collection(COLL_CHUNKS, io="write")
        collection.update_one(
            {"chunk_id": doc["chunk_id"]},
            {"$set": {"graphrag_construction": {"status": "completed"}}}
        )

        self.stats["updated"] += 1
        return None

    def finalize(self):
        """Run comprehensive post-processing."""
        # 1. Co-occurrence relationships
        # 2. Semantic similarity relationships
        # 3. Cross-chunk relationships (adaptive window)
        # 4. Bidirectional relationships
        # 5. Link prediction (optional)

        # Each with density checking!
        super().finalize()
```

**Key Decisions**:

- Post-processing runs in `finalize()` after all chunks processed
- Density safeguards prevent over-connection
- Adaptive window adjusts per video length
- Edge weights assigned for community detection

**Post-Processing Methods**:

1. **Co-occurrence**: Same-chunk entities
2. **Semantic similarity**: Embedding-based (threshold 0.92)
3. **Cross-chunk**: Nearby chunks (adaptive window)
4. **Bidirectional**: Reverse asymmetric relationships
5. **Link prediction**: Graph structure + embeddings

**Cross-Reference**: See `GRAPH-RAG-CONSOLIDATED.md` Sections 4.3, 5

---

### Community Detection Stage

**File**: `app/stages/community_detection.py`  
**Agents**: `agents/community_detection_agent.py`, `agents/community_summarization_agent.py`  
**Config**: `CommunityDetectionConfig`

**Purpose**: Detect entity communities and generate hierarchical summaries.

**Pattern**: Read chunks (once) → Load all entities/relations → Detect communities → Generate summaries → Store communities

```python
class CommunityDetectionStage(BaseStage):
    name = "community_detection"
    description = "Detect communities and generate summaries"
    ConfigCls = CommunityDetectionConfig

    def setup(self):
        super().setup()
        self.llm_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.detection_agent = CommunityDetectionAgent(
            max_cluster_size=self.config.max_cluster_size,
            min_cluster_size=self.config.min_cluster_size
        )
        self.summarization_agent = CommunitySummarizationAgent(
            llm_client=self.llm_client
        )

    def handle_doc(self, doc):
        # Special: Only runs ONCE for entire graph
        # Detects communities from ALL entities
        # Generates summaries for each community
        # Stores in communities collection

        # Mark all chunks as processed
        # (Implementation runs once, marks all chunks)
```

**Key Decisions**:

- Runs once for entire graph (not per chunk)
- Uses first chunk as trigger
- Post-filters communities by `min_cluster_size`
- **KNOWN ISSUE**: hierarchical_leiden creates single-entity communities
- **FIX NEEDED**: Switch to Louvain (Monday)

**Cross-Reference**: See `GRAPH-RAG-CONSOLIDATED.md` Section 4.4

---

## Collection Access Pattern (Critical for GraphRAG)

### The Correct Pattern

**Reading**:

```python
src_db = self.config.read_db_name or self.config.db_name
src_coll_name = self.config.read_coll or COLL_CHUNKS
collection = self.get_collection(src_coll_name, io="read", db_name=src_db)
```

**Writing**:

```python
dst_db = self.config.write_db_name or self.config.db_name
dst_coll_name = self.config.write_coll or COLL_CHUNKS
collection = self.get_collection(dst_coll_name, io="write", db_name=dst_db)
```

### What NOT to Do

❌ **Don't use** `self.get_read_collection()` (doesn't exist!)  
❌ **Don't use** `self.db.collection_name` directly (bypasses config)  
✅ **Do use** `self.get_collection()` with io parameter

**Why This Matters**: GraphRAG stages initially had this bug, causing runtime errors. Fixed by following the existing stage patterns.

**Historical Note**: See archived `GRAPHRAG-STAGE-PATTERNS-EXPLAINED.md` for the discovery and fix of this issue.

---

## GraphRAG Collections

GraphRAG stages use helper to get collections:

```python
from app.services.graphrag_indexes import get_graphrag_collections

self.graphrag_collections = get_graphrag_collections(self.db)

# Access collections:
entities = self.graphrag_collections["entities"]
relations = self.graphrag_collections["relations"]
communities = self.graphrag_collections["communities"]
entity_mentions = self.graphrag_collections["entity_mentions"]
```

**Why**: Centralized collection management, validation, and indexing.

---

## Test Exclusion Pattern (For Random Chunk Testing)

All GraphRAG stages respect the `_test_exclude` flag:

```python
query = {
    # ... normal query conditions ...
    "_test_exclude": {"$exists": False}  # Skip excluded chunks
}
```

**Purpose**: Enable controlled testing with random chunk selection.

**Implementation**: `scripts/run_random_chunk_test.py` sets this flag.

**Cross-Reference**: See `GRAPH-RAG-CONSOLIDATED.md` Section 8.

---

## Ingestion Pipeline Stages (with GraphRAG Notes)

For complete ingestion pipeline documentation, see `documentation/PIPELINE.md`.

### Clean Stage

**GraphRAG Integration**: Provides clean text for entity extraction.

### Enrich Stage

**GraphRAG Integration**: Provides initial entity candidates (redundant with graph extraction, but useful for comparison).

### Chunk Stage

**GraphRAG Integration**: Creates the chunks that GraphRAG processes.

### Redundancy Stage

**GraphRAG Integration**:

- Exports `get_entity_canonicalization_signals()` for entity resolution hints
- Provides similarity scores for entity grouping

### Trust Stage

**GraphRAG Integration**:

- Exports `get_entity_trust_scores()` for entity quality weighting
- Can propagate scores to graph entities via `propagate_trust_to_entities()`

---

## Stage Lifecycle

```
1. __init__()         # Create stage instance
2. parse_args()       # Parse command-line arguments (if running standalone)
3. setup()            # Initialize resources (agents, DB connections)
4. iter_docs()        # Get documents to process
5. handle_doc(doc)    # Process each document (called in loop)
6. finalize()         # Post-processing and statistics
```

**For GraphRAG stages**:

- Steps 1-5: Same as other stages
- Step 6 (`finalize()`): **Critical for graph post-processing**
  - Co-occurrence relationships
  - Semantic similarity
  - Cross-chunk (adaptive window)
  - Bidirectional
  - Link prediction
  - Density safeguards throughout

---

## Cross-Reference

**Main Documentation**: `documentation/GRAPH-RAG-CONSOLIDATED.md`  
**Pipeline Integration**: `documentation/PIPELINE.md`  
**Agent Details**: `documentation/AGENT.md`  
**Configuration**: `config/graphrag_config.py`, `documentation/GRAPHRAG-CONFIG-REFERENCE.md`

---

**This document focuses on stage architecture. For GraphRAG implementation details, see GRAPH-RAG-CONSOLIDATED.md.**
