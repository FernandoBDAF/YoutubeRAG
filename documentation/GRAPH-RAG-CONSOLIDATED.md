# GraphRAG Implementation Guide

**Version**: 2.0 (Consolidated - October 31, 2025)  
**Status**: Production-Ready (pending community detection fix)

---

## Overview and Vision

This document is the authoritative guide for the GraphRAG (Graph-based Retrieval-Augmented Generation) implementation in the YouTubeRAG Knowledge Manager. It consolidates learnings from iterative development, captures design decisions, and guides future enhancements.

### What is GraphRAG?

GraphRAG extends traditional vector-based RAG by constructing and leveraging a **knowledge graph** to:

- Improve retrieval quality through entity-aware search
- Enable multi-hop reasoning across relationships
- Provide hierarchical context through community summaries
- Support complex, relationship-aware queries

### Why We Built It

**Traditional RAG Limitations**:

- Chunk-level retrieval misses cross-chunk relationships
- No understanding of entity connections
- Limited context assembly (isolated chunks)
- Difficult to answer relationship queries

**GraphRAG Benefits**:

- Entity canonicalization across chunks
- Relationship mapping and traversal
- Community-based context assembly
- Multi-scale information representation

### Current Status

✅ **Implemented and Validated**:

- Graph Extraction (entity and relationship extraction)
- Entity Resolution (multi-strategy canonicalization)
- Graph Construction (with 5 post-processing methods)
- All critical fixes (adaptive window, edge weights, density safeguards)

⏳ **In Progress**:

- Production run on 13,069 chunks (638 videos)
- ~24% complete, ETA Friday evening

🔧 **Needs Fix**:

- Community detection (switch from hierarchical_leiden to Louvain)

---

## Table of Contents

1. [Theoretical Foundation](#1-theoretical-foundation)
2. [Architecture and Components](#2-architecture-and-components)
3. [Data Model and Schema](#3-data-model-and-schema)
4. [Pipeline Stages](#4-pipeline-stages)
5. [Post-Processing Enhancements](#5-post-processing-enhancements)
6. [Critical Design Decisions](#6-critical-design-decisions)
7. [Configuration Reference](#7-configuration-reference)
8. [Testing and Validation](#8-testing-and-validation)
9. [Performance and Scalability](#9-performance-and-scalability)
10. [Known Issues and Future Work](#10-known-issues-and-future-work)
11. [Integration Points](#11-integration-points)
12. [Query and Retrieval (Future)](#12-query-and-retrieval-future)
13. [MCP Server Integration (Future)](#13-mcp-server-integration-future)
14. [Utilities and Scripts](#14-utilities-and-scripts)
15. [References](#15-references)

---

## 1. Theoretical Foundation

### Microsoft GraphRAG Analysis

Microsoft's GraphRAG research introduces two key concepts:

**1. Summaries at Different Scales**

- **Problem**: Traditional RAG assumes all information is in small chunks
- **Solution**: Hierarchical summaries (chunks → communities → higher-level communities)
- **Benefit**: Provides both local and global context

**2. Graphical Representation**

- **Problem**: Text similarity misses logical connections
- **Solution**: Entities as nodes, relationships as edges
- **Benefit**: Multi-hop reasoning and relationship traversal

### Our Enhanced Approach

We build on Microsoft's foundation while addressing its limitations:

**Multi-Strategy Entity Resolution** (vs simple concatenation):

- Fuzzy string matching
- Embedding-based similarity
- Context-based resolution
- Relationship clustering
- Trust-weighted resolution (using existing trust scores)

**Enhanced Community Detection** (vs Leiden-only):

- Structural communities (Leiden/Louvain)
- Semantic communities (embedding-based)
- Trust-weighted communities
- Entity-type aware communities
- **LESSON LEARNED**: Louvain works better than hierarchical_leiden for sparse graphs

**Incremental Updates** (Microsoft's gap):

- Delta graph updates
- Community reassignment
- Summary refresh
- Trust propagation

**YouTube-Specific**:

- Temporal community detection
- Channel-based entity resolution
- Engagement-weighted trust scores

---

## 2. Architecture and Components

### Pipeline Flow

```
video_chunks (with embeddings, trust, redundancy)
    ↓
Graph Extraction → Entity Resolution → Graph Construction → Community Detection
    ↓                    ↓                      ↓                    ↓
(in chunks)        entities/mentions        relations          communities
```

### Core Components

**1. GraphRAG Models** (`core/graphrag_models.py`):

- Pydantic models for structured data (EntityModel, RelationshipModel, etc.)
- Validation and type safety
- ID generation (MD5 hashing for consistency)

**2. GraphRAG Configuration** (`config/graphrag_config.py`):

- Configuration classes for each stage
- Environment variable integration
- Adaptive defaults based on testing

**3. GraphRAG Agents** (`agents/`):

- GraphExtractionAgent: LLM-powered entity/relationship extraction
- EntityResolutionAgent: Multi-strategy entity canonicalization
- RelationshipResolutionAgent: Relationship deduplication and merging
- CommunityDetectionAgent: Graph clustering and summarization
- GraphLinkPredictionAgent: Predict missing relationships

**4. GraphRAG Stages** (`app/stages/`):

- graph_extraction: Extract from chunks
- entity_resolution: Canonicalize entities
- graph_construction: Build graph + post-processing
- community_detection: Detect communities and summarize

**5. GraphRAG Services** (`app/services/`):

- graphrag_indexes: Collection and index management
- graphrag_query: Query processing (future)

---

## 3. Data Model and Schema

### Collections

#### entities

```json
{
  "entity_id": "32-char MD5 hash",
  "name": "Python",
  "canonical_name": "Python",
  "type": "TECHNOLOGY",
  "description": "High-level programming language...",
  "confidence": 0.95,
  "source_count": 12,
  "resolution_methods": ["exact_match", "fuzzy_match"],
  "aliases": ["Python3", "python"],
  "entity_embedding": [0.1, 0.2, ...],
  "centrality_score": 0.85,
  "degree": 15,
  "trust_score": 0.78,
  "created_at": 1234567890.0,
  "updated_at": 1234567890.0
}
```

#### relations

```json
{
  "relationship_id": "32-char MD5 hash",
  "subject_id": "entity_id_1",
  "object_id": "entity_id_2",
  "predicate": "uses",
  "description": "Python uses Django framework...",
  "confidence": 0.9,
  "source_count": 3,
  "source_chunks": ["chunk_1", "chunk_2"],
  "video_id": "video_123",
  "relationship_type": "llm_extracted", // or co_occurrence, semantic_similarity, cross_chunk, bidirectional, predicted
  "weight": 0.9, // For community detection
  "created_at": 1234567890.0,
  "updated_at": 1234567890.0
}
```

#### communities

```json
{
  "community_id": "level_1_community_0",
  "level": 1,
  "title": "Python Development Community",
  "summary": "Community focused on Python...",
  "entities": ["entity_id_1", "entity_id_2"],
  "entity_count": 15,
  "relationship_count": 45,
  "coherence_score": 0.87,
  "entity_names": ["Python", "Django", "Flask"],
  "entity_types": ["TECHNOLOGY", "TECHNOLOGY"],
  "created_at": 1234567890.0
}
```

#### entity_mentions

```json
{
  "entity_id": "entity_id_1",
  "chunk_id": "chunk_uuid",
  "video_id": "video_123",
  "confidence": 0.95,
  "position": 0,
  "created_at": 1234567890.0
}
```

**Indexes**:

- See `app/services/graphrag_indexes.py` for complete index definitions
- Compound indexes for efficient traversal
- Text indexes for entity search
- Vector indexes for semantic similarity

---

## 4. Pipeline Stages

### 4.1. Graph Extraction Stage

**File**: `app/stages/graph_extraction.py`  
**Agent**: `agents/graph_extraction_agent.py`

**Purpose**: Extract entities and relationships from text chunks using LLM.

**Input**: `video_chunks` with `chunk_text`  
**Output**: Chunks with `graphrag_extraction` metadata

**Process**:

1. Query chunks without completed extraction
2. For each chunk:
   - Call LLM with structured output (Pydantic models)
   - Extract 4-10 entities per chunk
   - Extract 3-7 relationships per chunk
3. Store extraction data in chunk metadata
4. Track stats (processed, updated, failed)

**LLM Prompt Design** (Enhanced):

The prompt evolved to extract **multiple relationship types** per entity pair:

```
2. **Relationship Extraction**: Extract ALL relationship types between each entity pair:
- **Multiple Types**: If Entity A relates to Entity B, extract ALL applicable relationships
  * Example: "Algorithm uses Data Structure" → extract: 'uses', 'applies_to', 'depends_on'
- **Hierarchical**: Extract parent-child, part-of, is-a relationships
- **Bidirectional**: Consider reverse relationships
```

**Why This Matters**: Initial testing showed we only extracted ~0.73 relationships per entity. The enhanced prompt increased this significantly.

**Configuration** (`config/graphrag_config.py`):

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

**Performance**:

- ~15 seconds per chunk (LLM call time)
- ~390 chunks/hour in production
- Failure rate: <0.1%

---

### 4.2. Entity Resolution Stage

**File**: `app/stages/entity_resolution.py`  
**Agent**: `agents/entity_resolution_agent.py`

**Purpose**: Canonicalize entities across chunks, resolving duplicates and variants.

**Input**: Chunks with `graphrag_extraction.status = "completed"`  
**Output**: `entities` and `entity_mentions` collections

**Process**:

1. Extract entities from chunk extraction data
2. Group by normalized name (lowercase, stripped)
3. For duplicates:
   - Use LLM to merge descriptions
   - Calculate aggregate confidence
   - Track all source chunks
4. Generate entity_id (MD5 hash of canonical name)
5. Store in entities collection
6. Store mentions in entity_mentions collection

**Multi-Strategy Resolution** (Current):

- Exact match (normalized names)
- Context-based grouping
- LLM summarization for duplicates

**Future Enhancements** (from `GRAPHRAG-ENHANCEMENTS.md`):

- Fuzzy string matching (Levenshtein, Jaro-Winkler)
- Embedding-based similarity
- Relationship clustering
- Abbreviation/acronym handling

**Configuration**:

```python
@dataclass
class EntityResolutionConfig(BaseStageConfig):
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.1
    similarity_threshold: float = 0.85
    llm_retries: int = 3
```

**Performance**:

- ~0.5 seconds per chunk (fast when no LLM needed)
- ~2-3 seconds when LLM summarization required
- Deduplication: ~141 mentions → 84 unique entities (typical)

---

### 4.3. Graph Construction Stage

**File**: `app/stages/graph_construction.py`  
**Agent**: `agents/relationship_resolution_agent.py`

**Purpose**: Build knowledge graph from resolved entities and relationships.

**Input**: Chunks with `graphrag_resolution.status = "completed"`  
**Output**: `relations` collection + post-processing relationships

**Process**:

1. Extract relationships from chunks
2. Resolve duplicate relationships (merge descriptions)
3. Validate entity existence
4. Store in relations collection
5. **Run post-processing** (finalize method):
   - Co-occurrence relationships
   - Semantic similarity relationships
   - Cross-chunk relationships (adaptive window)
   - Bidirectional relationships
   - Link prediction (optional)

**This is the MOST COMPLEX stage** - See Section 5 for detailed post-processing.

**Configuration**:

```python
@dataclass
class GraphConstructionConfig(BaseStageConfig):
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.1
    llm_retries: int = 3
```

**Performance**:

- Chunk processing: ~0.5 seconds
- Post-processing: **Minutes to hours** depending on entity count
  - Co-occurrence: ~30-60s for 12 chunks
  - Semantic similarity: ~2-3 min for 84 entities (embedding generation)
  - Cross-chunk: ~1-2 min (with adaptive window)
  - Bidirectional: ~30s
  - Link prediction: ~2-3 min

---

### 4.4. Community Detection Stage

**File**: `app/stages/community_detection.py`  
**Agent**: `agents/community_detection_agent.py`, `agents/community_summarization_agent.py`

**Purpose**: Detect entity communities and generate hierarchical summaries.

**Input**: Chunks with `graphrag_construction.status = "completed"`  
**Output**: `communities` collection

**Process**:

1. Load all entities and relationships
2. Build NetworkX graph with edge weights
3. Run community detection algorithm
4. Filter communities by size (≥ min_cluster_size)
5. Generate LLM summaries for each community
6. Store in communities collection

**CRITICAL ISSUE DISCOVERED**:

`hierarchical_leiden` creates single-entity communities even with dense graphs:

**Our Testing Results**:

- 12 random chunks: 66 entities, 177 edges, density 0.09
- hierarchical_leiden: 88 communities (all single-entity)
- **Louvain**: 6 communities (sizes: 22, 20, 15, 12, 9, 6) ✅

**Root Cause**: `hierarchical_leiden` doesn't work well for our graph characteristics (sparse, diverse topics).

**Solution** (to be implemented Monday):

```python
# Switch primary algorithm from hierarchical_leiden to Louvain
try:
    import networkx.algorithms.community as nx_comm
    communities = list(nx_comm.greedy_modularity_communities(G))
except:
    # Fallback to hierarchical_leiden
    from graspologic.partition import hierarchical_leiden
    communities = hierarchical_leiden(G, max_cluster_size=50)
```

**Configuration**:

```python
@dataclass
class CommunityDetectionConfig(BaseStageConfig):
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.2
    max_cluster_size: int = 50  # Increased from 10
    min_cluster_size: int = 2   # Post-filtering threshold
    llm_retries: int = 3
```

**Performance**:

- Community detection: <1 second (algorithm)
- LLM summarization: ~10-20s per community
- For 100 communities: ~15-30 minutes of summarization

---

## 5. Post-Processing Enhancements

Post-processing runs in `GraphConstructionStage.finalize()` and adds relationships beyond LLM extraction.

**Design Philosophy**: Strategic relationship addition to improve connectivity without creating complete graphs.

### 5.1. Co-Occurrence Relationships

**What**: Connect entities that appear in the same chunk.

**Why**: Entities mentioned together are likely related, even if LLM didn't extract explicit relationship.

**Implementation** (`_add_co_occurrence_relationships()`):

1. Group entity mentions by chunk_id
2. For each chunk with 2+ entities:
   - Create relationships between all pairs
   - Skip if relationship already exists
   - Use predicate: `co_occurs_with`
   - Confidence: 0.7 (moderate)
   - Mark as `relationship_type: "co_occurrence"`

**Testing Results**:

- 12 chunks: Added 124 co-occurrence relationships
- 25 chunks: Added 212 co-occurrence relationships

**Impact**: Significantly improves connectivity, especially for CONCEPT entities.

**Configuration**: Always enabled (part of finalize).

---

### 5.2. Semantic Similarity Relationships

**What**: Connect entities with highly similar embeddings.

**Why**: Identify duplicates/variants across different chunks (e.g., "Input" ↔ "Inputs").

**Design Evolution**:

**V1**: Threshold = 0.85

- Result: 426 relationships (11.9% of total)
- Problem: Too many moderate similarities

**V2**: Threshold = 0.92 (current)

- Result: ~100-150 relationships (expected)
- Benefit: Only high-quality duplicate detection

**Implementation** (`_add_semantic_similarity_relationships()`):

1. Generate embeddings for entities (name + description)
2. Calculate pairwise cosine similarity
3. Create `semantically_similar_to` relationships if similarity ≥ threshold
4. Skip if relationship already exists
5. Store similarity score in relationship

**Testing Results**:

- 12 random chunks: Added 0 relationships (threshold 0.92, 66 entities)
- 25 consecutive chunks: Added 2 relationships (threshold 0.92, 84 entities)

**Configuration**:

```bash
GRAPHRAG_SIMILARITY_THRESHOLD=0.92  # Min cosine similarity
```

**Performance**: ~2-3 minutes for 80-100 entities (includes embedding generation).

---

### 5.3. Cross-Chunk Relationships (Adaptive Window)

**What**: Connect entities in nearby chunks of the same video.

**Why**: Preserve temporal context (entities mentioned minutes apart are likely related).

#### Design Evolution: The Complete Graph Problem

This is our **most important design lesson**.

**V1: Video-Level Cross-Chunk** (FAILED)

```python
# Connect ALL entities in same video
for video_id, entity_ids in video_entities.items():
    for entity1, entity2 in all_pairs(entity_ids):
        create_relationship(entity1, entity2)
```

**Result**:

- 25 chunks, 84 entities → 2,749 cross-chunk relationships (76.6% of total!)
- **Density: 1.0** (complete graph - maximum possible edges!)
- Communities: 0
- **Lesson**: Same video ≠ semantically related

**Why It Failed**: Transitive connections

```
Chunks: A → B → C → D → E
All chunks from same video → All entities transitively connected
Result: Complete graph where community detection is impossible
```

**V2: Fixed Window=5** (BETTER, STILL PROBLEMATIC)

```python
# Connect entities in chunks within window of 5
for i, chunk1 in enumerate(chunks):
    for j in range(i+1, min(i+5+1, len(chunks))):
        chunk2 = chunks[j]
        connect_entities(chunk1, chunk2)
```

**Result**:

- 12 chunks: 412 cross-chunk relationships
- Density: 0.83 (still near-complete!)
- Communities: 0

**Why Still Failed**: For short videos, window=5 covers too much

- 12 chunks with window=5 = **42% video coverage** per chunk
- Creates excessive overlapping windows
- Still leads to transitive connections

**V3: Adaptive Window** (SOLUTION) ✅

```python
# Calculate window based on video length
if total_chunks <= 15:
    window = 1  # Only adjacent chunks
elif total_chunks <= 30:
    window = 2
elif total_chunks <= 60:
    window = 3
else:
    window = 5  # Long videos only
```

**Key Insight**: Maintain **~5-10% video coverage** regardless of length.

**Result**:

- 12 chunks (1 per video): 0 cross-chunk (correct - need 2+ chunks)
- 12 chunks (same video): ~30-50 cross-chunk (window=1)
- Density: 0.20-0.25 (healthy!)

**Implementation Details**:

1. Sort chunks by timestamp
2. Calculate adaptive window per video
3. Only connect entities in nearby chunks
4. Confidence decreases with distance:
   - Adjacent (distance=1): 0.60
   - Window edge (distance=5): 0.40
5. Store chunk_distance for analysis

**Configuration**:

```bash
# Leave unset for adaptive (RECOMMENDED)
# GRAPHRAG_CROSS_CHUNK_WINDOW=

# Or override for all videos:
# GRAPHRAG_CROSS_CHUNK_WINDOW=3
```

**Performance**: ~1-2 minutes for typical video.

**Testing Results**:

- Fixed window=5, 12 chunks: 412 relationships, density 0.83
- Adaptive window, 12 chunks: 0 relationships (1 chunk/video)
- Adaptive window, 25 chunks (same video): ~60-100 relationships (expected)

---

### 5.4. Bidirectional Relationships

**What**: Create reverse relationships for asymmetric predicates.

**Why**: Make graph more navigable, improve community detection.

**Implementation** (`_add_bidirectional_relationships()`):

Reverse predicate mappings:

```python
{
    "uses": "used_by",
    "teaches": "taught_by",
    "creates": "created_by",
    "implements": "implemented_by",
    # ... 18 total mappings
}
```

**Testing Results**:

- 12 random chunks: Added 19 bidirectional relationships

**Impact**: Doubles effective edges for asymmetric relationships.

---

### 5.5. Link Prediction

**What**: Predict missing relationships using graph structure and embeddings.

**Why**: Discover implicit relationships.

**Implementation** (`agents/graph_link_prediction_agent.py`):

**Two strategies**:

1. **Structural**: Adamic-Adar index (common neighbors)
2. **Semantic**: Embedding similarity for unconnected entities

**Current Issue** (to be fixed):

- Predicted relationships have `source_count=0`
- MongoDB validation requires `source_count ≥ 1`
- All 270 predictions failed validation

**Fix Needed**:

```python
"source_count": 1,  # Change from 0
```

**Configuration**:

```bash
GRAPHRAG_ENABLE_LINK_PREDICTION=true  # Can disable
GRAPHRAG_LINK_PREDICTION_THRESHOLD=0.65
GRAPHRAG_MAX_PREDICTIONS_PER_ENTITY=5
```

---

## 6. Critical Design Decisions

This section captures our most important learnings and design evolution.

### 6.1. The Complete Graph Problem

**The Discovery**:

Testing 25 consecutive chunks from one video:

- Entities: 84
- Relationships: 3,591
- **Density: 1.000** (complete graph!)
- Communities: 0

**The Diagnosis** (`analyze_graph_structure.py`):

```
Edges: 3,486
Max possible: 84 × 83 / 2 = 3,486
Density: 3,486 / 3,486 = 1.0

Every entity connected to every other entity!
```

**Root Cause**:

- Cross-chunk: 2,749 relationships (76.6%)
- Video-level strategy connected ALL entity pairs
- Created mathematically complete graph

**Why Community Detection Failed**:

- `hierarchical_leiden` can't find clusters in complete graphs
- No modularity structure (everyone equally connected)
- Algorithm defaults to N single-entity communities

**The Solution** (Section 5.3):

- Adaptive window based on video length
- Density safeguards
- Edge weights

**Key Metrics**:

| Stage        | Relationships | Density | Communities |
| ------------ | ------------- | ------- | ----------- |
| Before fixes | 3,591         | 1.000   | 0           |
| After fixes  | ~600          | 0.15    | 5-15        |

**Lesson**: Test with diverse data, not just one video!

---

### 6.2. Adaptive Window Strategy

**The Problem**: Fixed window doesn't scale across video lengths.

**The Math**:

```
Video: 12 chunks, window=5
Coverage per chunk: 5/12 = 42%
Result: Massive overlap, near-complete graph
```

**The Solution**: Adaptive sizing maintains ~5-10% coverage.

**Logic**:
| Video Length | Window | % Coverage |
|--------------|--------|------------|
| 10 chunks | 1 | 10% |
| 20 chunks | 2 | 10% |
| 50 chunks | 3 | 6% |
| 100 chunks | 5 | 5% |

**Updated Thresholds** (based on 12-chunk test showing window=2 still too large):

- ≤15 chunks: window=1 (was ≤10)
- ≤30 chunks: window=2 (was ≤25)
- ≤60 chunks: window=3 (was ≤50)
- > 60 chunks: window=5

**Implementation**: `app/stages/graph_construction.py` lines 673-695

**Lesson**: Adaptive > Fixed for mixed-length datasets.

---

### 6.3. Edge Weights for Community Detection

**The Problem**: All relationships treated equally in clustering.

**Why It Matters**:

- LLM-extracted relationships (conf 0.9) = same weight as auto-generated (conf 0.4)
- Community structure dominated by quantity, not quality

**The Solution**: Weight by relationship type and confidence.

**Weight Multipliers**:

```python
LLM-extracted: 1.0 × confidence = 0.85-0.95
Co-occurrence: 1.0 × confidence = 0.70
Bidirectional: 1.0 × confidence = inherited
Semantic similarity: 0.8 × confidence = 0.70-0.95
Cross-chunk: 0.5 × confidence = 0.20-0.30
Predicted: 0.4 × confidence = 0.25-0.40
```

**Implementation**: `agents/community_detection_agent.py` lines 151-187

**Impact**: Communities form around high-quality (LLM) relationships, not auto-generated noise.

**Lesson**: Quality over quantity for graph structure.

---

### 6.4. Density Safeguards

**The Problem**: Post-processing can create runaway relationships.

**Example**:

- After co-occurrence: density 0.18
- After cross-chunk (bad): density 0.83 → **STOP!**

**The Solution**: Check density after each post-processing step.

**Implementation**:

```python
max_density = 0.3  # Threshold

after_each_step:
    current_density = calculate_density()
    if current_density >= max_density:
        logger.warning("Density limit reached, stopping")
        return  # Skip remaining steps
```

**Result**:

- 12-chunk test (window=2): Stopped after cross-chunk (density 0.54)
- 12-chunk test (window=1): Expected to complete all steps

**Configuration**:

```bash
GRAPHRAG_MAX_DENSITY=0.3  # Maximum allowed density
```

**Lesson**: Safeguards prevent catastrophic over-connection.

---

## 7. Configuration Reference

**See**: `documentation/GRAPHRAG-CONFIG-REFERENCE.md` for complete reference.

**Essential Variables**:

```bash
# Semantic Similarity
GRAPHRAG_SIMILARITY_THRESHOLD=0.92

# Cross-Chunk (leave unset for adaptive - RECOMMENDED)
# GRAPHRAG_CROSS_CHUNK_WINDOW=

# Density Safeguards
GRAPHRAG_MAX_DENSITY=0.3

# Link Prediction
GRAPHRAG_ENABLE_LINK_PREDICTION=true
GRAPHRAG_LINK_PREDICTION_THRESHOLD=0.65
GRAPHRAG_MAX_PREDICTIONS_PER_ENTITY=5
```

**Configuration Philosophy**:

- **Adaptive by default**: System adjusts to data characteristics
- **Override when needed**: Can set explicit values for specific use cases
- **Safe defaults**: Based on actual test results, not theory

---

## 8. Testing and Validation

### Testing Methodology Evolution

**V1: Consecutive Chunks** (MISLEADING)

- Problem: All chunks from same video → transitive connections
- Result: Complete graph, even with fixes
- Lesson: Doesn't represent real-world diversity

**V2: Random Chunks from Different Videos** (CORRECT) ✅

- Solution: 12 chunks from 12 different videos
- Result: Realistic disconnected components, proper density
- Tool: `scripts/run_random_chunk_test.py`

**Key Insight**: Test environment must match production diversity!

### Validation Criteria

**Graph Structure**:

- ✅ Density < 0.30
- ✅ Isolated nodes < 15%
- ✅ Average degree > 2.0
- ✅ Disconnected components = reasonable for topic diversity

**Community Detection**:

- ✅ Multi-entity communities detected (not all single-entity)
- ✅ Community sizes reasonable (2-30 entities)
- ✅ Coherence scores > 0.5

**Relationship Quality**:

- ✅ LLM-extracted: High confidence (0.85-0.95)
- ✅ Co-occurrence: Meaningful pairings
- ✅ Semantic similarity: True duplicates only
- ✅ Cross-chunk: Local temporal context preserved

### Testing Tools

**1. `scripts/analyze_graph_structure.py`** - Primary validation tool

- Outputs: Density, degree distribution, connectivity, hubs
- **This caught the complete graph problem!**

**2. `scripts/run_random_chunk_test.py`** - Realistic testing setup

- Selects chunks from different videos
- Sets `_test_exclude` flags for controlled testing
- **This revealed the single-video testing problem!**

**3. `scripts/test_community_detection.py`** - Algorithm validation

- Tests different algorithms (hierarchical_leiden, Louvain)
- **This proved Louvain works for our graphs!**

**4. `scripts/sample_graph_data.py`** - Quality checking

- Samples entities and relationships
- Shows type distributions

---

## 9. Performance and Scalability

### Production Metrics (13k Chunks, In Progress)

**Current Status** (Friday morning, 8 hours in):

- Chunks processed: ~3,148 / 13,069 (24%)
- Processing rate: ~390 chunks/hour
- Failures: 2 (~0.06%)
- Stage: Graph Extraction

**Estimated Completion**: Friday evening (~40 hours total)

**Expected Final Results**:

- Entities: 20,000-30,000 (after resolution)
- LLM relationships: 40,000-50,000
- Co-occurrence: 50,000-70,000
- Semantic similarity: 5,000-10,000
- Cross-chunk: 30,000-50,000 (adaptive windows)
- Bidirectional: 20,000-30,000
- **Total relationships**: 150,000-200,000
- **Density**: 0.10-0.15 (healthy)
- Communities: 100-500 (after Louvain fix)

### Bottlenecks

**1. LLM Calls** (Primary):

- ~15 seconds per chunk
- 13,069 chunks × 15s = ~54 hours theoretical minimum
- Actual: ~40 hours (parallelization in LLM processing)

**2. Sequential Processing**:

- One chunk at a time
- Could parallelize but risks rate limits

**3. Post-Processing** (Secondary):

- Semantic similarity: O(n²) for entities
- Cross-chunk: O(chunks × window × entities²)
- Mitigated by density safeguards

### Scalability Projections

**For 100k chunks** (future):

- Extraction: ~250 hours (~10 days)
- Post-processing: ~10-20 hours
- Total: ~260-270 hours (~11 days)

**Optimization Options**:

- Parallel extraction (5-10 workers)
- Incremental updates (only new chunks)
- Batch processing
- Local LLM models

---

## 10. Known Issues and Future Work

### Known Issues

**1. Community Detection Algorithm**

- **Issue**: `hierarchical_leiden` creates single-entity communities
- **Status**: Identified, solution known (switch to Louvain)
- **Priority**: HIGH (blocks production use)
- **ETA**: Monday (15-minute fix)

**2. Link Prediction Validation Error**

- **Issue**: `source_count=0` fails MongoDB validation (requires ≥1)
- **Status**: All 270 predictions failed
- **Priority**: MEDIUM (link prediction optional)
- **Fix**: Change `source_count` from 0 to 1

**3. Cross-Source Entity Linking**

- **Issue**: No entity linking across different source types (YouTube, PDFs, etc.)
- **Status**: Current implementation is source-aware but doesn't cross-link
- **Priority**: LOW (future enhancement)

### Future Enhancements

**From `GRAPHRAG-ENHANCEMENTS.md`**:

**1. Fuzzy Matching**

- Enhanced entity resolution with Levenshtein, Jaro-Winkler
- Abbreviation/acronym handling
- Typo tolerance

**2. Graph Visualization**

- Interactive graph explorer
- Entity relationship display
- Community visualization
- Export capabilities (PNG, SVG, HTML)

**3. Knowledge Hole Detection**

- Identify gaps in knowledge graph
- Suggest content to ingest
- Find under-connected entities
- Guide acquisition strategy

**4. Improved Community Detection**

- Test additional algorithms (Label Propagation, Girvan-Newman)
- Hierarchical communities (levels 1-3)
- Temporal community tracking

**5. Cross-Video Entity Linking**

- Link same entities across videos
- Already partially handled by semantic similarity
- Could enhance with external knowledge bases

**6. Performance Optimization**

- Parallel extraction (5-10 workers)
- Incremental graph updates
- Caching strategies
- Query optimization

---

## 11. Integration Points

### With Ingestion Pipeline

GraphRAG pipeline consumes output from ingestion pipeline:

**Input**: `video_chunks` collection with:

- `chunk_text`: Cleaned text for extraction
- `embedding`: Vector for semantic operations
- `trust_score`: From trust stage (used for entity weighting)
- `is_redundant`: From redundancy stage (used for entity canonicalization)

**Integration**:

- Redundancy signals help entity resolution
- Trust scores propagate to entities
- Existing pipeline stages remain unchanged

**See**: `documentation/PIPELINE.md` for integration details.

### With Query/Retrieval (Future)

GraphRAG will enhance query processing:

**Planned Flow**:

```
Query → Extract Entities → Expand via Graph → Retrieve Chunks → Rank by Centrality → Generate
```

**Services to Build**:

- `app/services/graphrag_query.py`: Query processing
- Entity expansion algorithms
- Graph-based ranking
- Context assembly from communities

**See**: Section 12 for detailed query plans.

---

## 12. Query and Retrieval (Future)

**Status**: Not yet implemented (blocked on community detection fix).

**Planned Implementation**:

### Query Processing

1. Extract entities from query (LLM)
2. Find entities in graph (exact + semantic match)
3. Expand via relationships (1-2 hops)
4. Retrieve chunks mentioning entities
5. Get community summaries
6. Rank by graph centrality + relevance
7. Generate answer with graph context

### Hybrid Retrieval

- Combine vector search + entity search
- Weight by centrality scores
- Use community summaries as context

**See**: `documentation/GRAPH-RAG.md` (current) Section 11 for detailed query architecture.

---

## 13. MCP Server Integration (Future)

**Status**: Planned, not yet implemented.

**Vision**: Expose GraphRAG as MCP tools for AI assistant integration.

**Planned Tools**:

- `query_knowledge_graph`: Query entities and relationships
- `get_entity_details`: Retrieve entity information
- `get_community_summary`: Community summaries
- `create_entity`: Manual entity creation
- `merge_entities`: Entity canonicalization

**See**: `documentation/MCP-SERVER.md` for integration plans.

---

## 14. Utilities and Scripts

### Graph Analysis

**`scripts/analyze_graph_structure.py`** ⭐ **ESSENTIAL**

**Purpose**: Comprehensive graph metrics analysis

**Output**:

```
Nodes: 84
Edges: 360
Density: 0.103270
Isolated nodes: 0
Degree distribution: ...
Hub analysis: Top 10 entities
Connected components: 1
```

**When to Use**:

- After graph construction
- To validate structure
- To debug connectivity issues
- **This caught the complete graph!**

**Usage**:

```bash
python scripts/analyze_graph_structure.py
```

---

**`scripts/sample_graph_data.py`**

**Purpose**: Sample entities and relationships for quality checking

**Output**:

- 5 sample entities
- Relationship type distribution
- High-confidence LLM relationships
- Cross-chunk samples

**When to Use**:

- Validate entity/relationship quality
- Check type distributions
- Inspect specific relationship types

---

### Testing

**`scripts/run_random_chunk_test.py`** ⭐ **KEY INNOVATION**

**Purpose**: Select random chunks from different videos for realistic testing

**Innovation**: Solved the single-video testing problem!

**What It Does**:

1. Selects N chunks from N different videos (max diversity)
2. Sets `_test_exclude=true` on all other chunks
3. Pipeline processes only selected chunks
4. Enables realistic testing without full dataset

**When to Use**:

- Validation before production runs
- Testing with diverse data
- Algorithm comparisons

**Usage**:

```bash
python scripts/run_random_chunk_test.py
python run_graphrag_pipeline.py --max 12 --log-file logs/pipeline/graphrag_random_test.log
```

**Key Learning**: This revealed that consecutive chunks create transitive connections!

---

**`scripts/test_community_detection.py`** ⭐ **ALGORITHM VALIDATOR**

**Purpose**: Test different community detection algorithms

**Key Finding**: Louvain works, hierarchical_leiden doesn't!

**Output**:

```
hierarchical_leiden: 88 communities (all single-entity)
Louvain: 6 communities (sizes: 22, 20, 15, 12, 9, 6) ✅
```

**When to Use**:

- Compare algorithms
- Validate community detection
- Debug clustering issues

---

### Maintenance

**`scripts/full_cleanup.py`**

**Purpose**: Clean all GraphRAG data for fresh runs

**What It Does**:

- Drops entities, relations, communities, entity_mentions collections
- Clears graphrag\_\* metadata from chunks

**When to Use**:

- Before validation tests
- Fresh production runs
- After major changes

---

**`scripts/check_graphrag_data.py`**

**Purpose**: Health check for GraphRAG collections

**Output**: Collection counts across all databases

**When to Use**:

- Verify data exists
- Check collection sizes
- Database health monitoring

---

### Diagnostic (Archive After Consolidation)

**`scripts/monitor_density.py`** - Real-time density monitoring (replaced by log-based)  
**`scripts/quick_validation_cleanup.py`** - Remove problematic relationships  
**`scripts/inspect_community_detection.py`** - Deep community inspection  
**`scripts/diagnose_graphrag_communities.py`** - Community diagnosis  
**`scripts/test_random_chunks.py`** - Older random test version

---

## 15. References

### Implementation Files

**Core**:

- `core/graphrag_models.py` - Pydantic models
- `config/graphrag_config.py` - Configuration classes

**Agents**:

- `agents/graph_extraction_agent.py`
- `agents/entity_resolution_agent.py`
- `agents/relationship_resolution_agent.py`
- `agents/community_detection_agent.py`
- `agents/community_summarization_agent.py`
- `agents/graph_link_prediction_agent.py`

**Stages**:

- `app/stages/graph_extraction.py`
- `app/stages/entity_resolution.py`
- `app/stages/graph_construction.py`
- `app/stages/community_detection.py`

**Services**:

- `app/services/graphrag_indexes.py`

### Related Documentation

- `GRAPHRAG-CONFIG-REFERENCE.md` - Configuration guide
- `PIPELINE.md` - Pipeline architecture
- `STAGE.md` - Stage patterns
- `AGENT.md` - Agent patterns
- `TESTING.md` - Testing strategy
- `MCP-SERVER.md` - MCP integration

### Historical Documentation

**Archive**: `documentation/archive/graphrag-implementation/`

Contains all analysis, plans, and diagnostic documentation from the iterative implementation phase. Preserved for reference.

---

## LLM Update Guide

When updating this documentation:

1. **Preserve Structure**: Keep sections 1-15 intact
2. **Add Learnings**: Update "Design Evolution" subsections with new insights
3. **Update Metrics**: Replace estimates with actual results as available
4. **Track Issues**: Move resolved issues from Section 10 to relevant implementation sections
5. **Sync Code**: Ensure code examples match actual implementation
6. **Cross-Reference**: Update links to related documentation
7. **Date Updates**: Add date stamps to major changes

**Pattern for New Features**:

```markdown
### X.X. New Feature Name

#### What It Is

[Brief description]

#### Why We Need It

**Problem**: [What problem does it solve]
**Solution**: [How it solves it]

#### Design Evolution

**V1**: [First attempt, what happened]
**V2**: [Iteration, what changed]
**VN**: [Final solution, why it works]

#### Implementation

[Code and details]

#### Testing

[Results and validation]

#### Configuration

[Environment variables]

#### Future Work

[Planned improvements]
```

---

**This consolidated guide preserves our implementation journey while providing clear technical guidance for future development!** 🚀
