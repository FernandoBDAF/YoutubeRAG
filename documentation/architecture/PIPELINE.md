# Pipeline Architecture and Implementation Guide

This document provides comprehensive documentation for the pipeline system in the GraphRAG Knowledge Manager MCP Server. It covers pipeline architecture, implemented pipelines, stage details, and guidelines for creating new pipelines.

## Table of Contents

1. [Pipeline Architecture Overview](#pipeline-architecture-overview)
2. [Implemented Pipelines](#implemented-pipelines)
3. [Stage Details](#stage-details)
4. [Creating New Pipelines](#creating-new-pipelines)
5. [Pipeline Orchestration](#pipeline-orchestration)
6. [Document Type Extensibility](#document-type-extensibility)

## Pipeline Architecture Overview

### Core Concepts

**Pipeline**: A sequence of stages that processes documents through multiple transformations. Pipelines orchestrate stages and handle error recovery, logging, and status monitoring.

**Stage**: An individual processing step that reads from one collection and writes to another. Each stage implements `BaseStage` and has a corresponding configuration class.

**Agent**: LLM-powered components that perform intelligent operations within stages (e.g., entity extraction, content enrichment).

### Architecture Pattern

All pipelines follow a consistent pattern:

```python
class MyPipeline:
    def __init__(self, config: MyPipelineConfig):
        self.config = config
        self.specs = self._create_stage_specs()
        self.runner = PipelineRunner(self.specs, stop_on_error=not config.continue_on_error)

    def _create_stage_specs(self) -> List[StageSpec]:
        return [
            StageSpec(stage="stage_name", config=self.config.stage_config),
            # ... more stages
        ]

    def setup(self) -> None:
        # Create collections, indexes, etc.
        pass

    def run_full_pipeline(self) -> int:
        self.setup()
        return self.runner.run()
```

### Pipeline Services

**PipelineRunner**: Orchestrates stage execution, handles errors, and provides progress tracking.

**StageSpec**: Declaratively defines a stage within a pipeline with its configuration.

**STAGE_REGISTRY**: Central registry mapping stage names to stage classes for dynamic lookup.

### Data Flow

```
Raw Documents → Ingestion Pipeline → Processed Chunks
                                    ↓
                           GraphRAG Pipeline → Knowledge Graph
```

Data flows unidirectionally through stages, with each stage reading from collections written by previous stages.

## Implemented Pipelines

### Ingestion Pipeline

**Purpose**: Process raw documents into enriched, embedded chunks with quality scores.

**Pipeline Flow**: `ingest → clean → enrich → chunk → embed → redundancy → trust`

**Input**: Raw documents from source-specific collections (e.g., `raw_videos`)

**Output**: `video_chunks` collection with:

- Embedded vectors for semantic search
- Quality scores (redundancy, trust)
- Source type identification
- Rich metadata (tags, entities, concepts)

**Configuration**: `IngestionPipelineConfig`

**Usage**:

```python
from app.pipelines.ingestion_pipeline import IngestionPipeline, IngestionPipelineConfig

# Create pipeline with configuration
config = IngestionPipelineConfig.from_args_env(args, env, default_db)
pipeline = IngestionPipeline(config)

# Run full pipeline
exit_code = pipeline.run_full_pipeline()

# Run single stage
exit_code = pipeline.run_stage("clean")
```

**CLI Usage**:

```bash
# Run full ingestion pipeline
python main.py pipeline --playlist_id <ID> --max 10 --llm

# Run via pipeline module directly
python app/pipelines/ingestion_pipeline.py --playlist_id <ID> --max 10 --llm

# Run specific stage
python app/pipelines/ingestion_pipeline.py --stage clean --llm
```

**Stage Details**:

1. **ingest**: Fetch raw documents from external sources (YouTube, PDFs, etc.)

   - Input: External sources (YouTube API, file system, etc.)
   - Output: `raw_videos` (or source-specific raw collection)
   - Key Features: Metadata extraction, transcript fetching

2. **clean**: Normalize and clean document text

   - Input: `raw_videos`
   - Output: `cleaned_transcripts`
     -project Root/Users/fernandobarroso/Local Repo/YoutubeRAG-mongohack/YoutubeRAG
   - Key Features: LLM-powered cleaning, paragraph detection, normalization

3. **enrich**: Extract entities, tags, concepts, and code blocks

   - Input: `cleaned_transcripts`
   - Output: `enriched_transcripts`
   - Key Features: Entity extraction, concept identification, code block detection

4. **chunk**: Split documents into semantic chunks

   - Input: `cleaned_transcripts` or `enriched_transcripts`
   - Output: `video_chunks`
   - Key Features: Multiple chunking strategies (fixed, recursive, semantic), overlap handling

5. **embed**: Generate vector embeddings for chunks

   - Input: `video_chunks` (without embeddings)
   - Output: `video_chunks` (with embeddings)
   - Key Features: Voyage AI embeddings, rate limiting, batch processing

6. **redundancy**: Detect and mark duplicate/redundant chunks

   - Input: `video_chunks` (with embeddings)
   - Output: `video_chunks` (with redundancy scores)
   - Key Features: Cosine similarity, adjacency guard, LLM validation for borderline cases
   - GraphRAG Integration: Exports `get_entity_canonicalization_signals()` for entity resolution

7. **trust**: Compute trust scores for chunks
   - Input: `video_chunks` (with redundancy scores)
   - Output: `video_chunks` (with trust scores)
   - Key Features: Multi-factor scoring (consensus, recency, engagement, code presence), LLM validation
   - GraphRAG Integration: Exports `get_entity_trust_scores()` and `propagate_trust_to_entities()` for graph weighting

### GraphRAG Pipeline

**Purpose**: Build knowledge graph from processed chunks using multi-stage extraction, resolution, and post-processing.

**Pipeline Flow**: `graph_extraction → entity_resolution → graph_construction → community_detection`

**Input**: `video_chunks` collection with:

- `chunk_text`: Cleaned text for extraction
- `embedding`: Vector embeddings
- `trust_score`: Quality scoring (from trust stage)
- `is_redundant`: Duplicate detection (from redundancy stage)

**Output**: GraphRAG collections:

- `entities`: Canonicalized entities with descriptions, centrality scores, trust scores
- `relations`: Entity relationships with confidence scores, edge weights, relationship types
- `communities`: Entity communities with hierarchical summaries (pending Louvain fix)
- `entity_mentions`: All entity occurrences across chunks

**Configuration**: `GraphRAGPipelineConfig`

**Usage**:

```python
from app.pipelines.graphrag_pipeline import GraphRAGPipeline, GraphRAGPipelineConfig

config = GraphRAGPipelineConfig.from_args_env(args, env, default_db)
pipeline = GraphRAGPipeline(config)
exit_code = pipeline.run_full_pipeline()
```

**CLI Usage**:

```bash
# Run full GraphRAG pipeline
python run_graphrag_pipeline.py

# Run with logging
python run_graphrag_pipeline.py --log-file logs/pipeline/graphrag.log --verbose

# Run specific stage
python run_graphrag_pipeline.py --stage entity_resolution

# Check pipeline status
python run_graphrag_pipeline.py --status

# Cleanup failed stages
python run_graphrag_pipeline.py --cleanup
```

**Stage Details**:

1. **graph_extraction**: Extract entities and relationships from chunks

   - Input: `video_chunks` with `chunk_text`
   - Output: Chunks with `graphrag_extraction` metadata
   - Key Features:
     - LLM-powered extraction with structured output (Pydantic)
     - Enhanced prompt for multiple relationship types
     - ~15s per chunk, ~390 chunks/hour
   - Agent: `GraphExtractionAgent`
   - **See**: `STAGE.md`, `GRAPH-RAG-CONSOLIDATED.md` Section 4.1

2. **entity_resolution**: Canonicalize entities across chunks

   - Input: Chunks with `graphrag_extraction.status = "completed"`
   - Output: `entities`, `entity_mentions` collections
   - Key Features:
     - Multi-strategy resolution (exact match, LLM summarization)
     - MD5-based entity IDs for consistency
     - Source tracking across chunks
   - Agent: `EntityResolutionAgent`
   - **See**: `STAGE.md`, `GRAPH-RAG-CONSOLIDATED.md` Section 4.2

3. **graph_construction**: Build knowledge graph with comprehensive post-processing

   - Input: Chunks with `graphrag_resolution.status = "completed"`
   - Output: `relations` collection
   - Key Features:
     - Relationship resolution and merging
     - **5 post-processing methods** (in finalize):
       1. Co-occurrence relationships (same-chunk entities)
       2. Semantic similarity (embedding-based, threshold 0.92)
       3. **Cross-chunk relationships (adaptive window)** ⭐
       4. Bidirectional relationships (reverse edges)
       5. Link prediction (graph structure + embeddings)
     - **Density safeguards** (stops if density > 0.30)
     - Edge weight calculation for community detection
   - Agents: `RelationshipResolutionAgent`, `GraphLinkPredictionAgent`
   - **See**: `STAGE.md`, `GRAPH-RAG-CONSOLIDATED.md` Sections 4.3, 5, 6

4. **community_detection**: Detect entity communities and generate summaries

   - Input: Chunks with `graphrag_construction.status = "completed"`
   - Output: `communities` collection
   - Key Features:
     - Community detection algorithms (hierarchical_leiden, Louvain)
     - Post-filtering by `min_cluster_size` (≥2 entities)
     - LLM-generated community summaries
     - Coherence scoring
   - Agents: `CommunityDetectionAgent`, `CommunitySummarizationAgent`
   - **Known Issue**: hierarchical_leiden creates single-entity communities
   - **Fix Needed**: Switch to Louvain (Monday)
   - **See**: `STAGE.md`, `GRAPH-RAG-CONSOLIDATED.md` Sections 4.4, 6, 10

---

### GraphRAG Pipeline Integration with Ingestion

**Data Flow**:

```
Ingestion Pipeline                    GraphRAG Pipeline
├─ ingest                             ├─ graph_extraction
├─ clean                              ├─ entity_resolution
├─ enrich                             ├─ graph_construction
├─ chunk                              └─ community_detection
├─ embed
├─ redundancy  ──────────────┐
└─ trust       ──────────────┤
                              │
                              ├──> Signals for entity resolution
                              └──> Scores for entity weighting
```

**Integration Points**:

1. **Redundancy → Entity Resolution**:

   - `get_entity_canonicalization_signals()`: Similarity clusters
   - Helps group entity variations

2. **Trust → Graph Construction**:

   - `get_entity_trust_scores()`: Quality scores
   - `propagate_trust_to_entities()`: Update graph entities
   - Weights entities in graph operations

3. **Both Pipelines Share**:
   - Same `video_chunks` collection
   - Same MongoDB database
   - Can run independently or together

**Running Both**:

```bash
# Option 1: Run ingestion, then GraphRAG
python main.py pipeline --playlist_id <ID> --max 100
python run_graphrag_pipeline.py

# Option 2: GraphRAG on existing chunks
python run_graphrag_pipeline.py  # Processes all chunks without ingestion
```

---

### GraphRAG Pipeline Critical Features

#### 1. Adaptive Window Cross-Chunk

**File**: `app/stages/graph_construction.py`

**Innovation**: Window size adapts to video length

**Logic**:

- ≤15 chunks: window=1 (adjacent only)
- ≤30 chunks: window=2
- ≤60 chunks: window=3
- > 60 chunks: window=5

**Why**: Fixed window=5 created complete graphs for short videos.

**Result**: Maintains ~5-10% coverage regardless of video length.

**See**: `GRAPH-RAG-CONSOLIDATED.md` Section 6.2

---

#### 2. Density Safeguards

**File**: `app/stages/graph_construction.py`

**Innovation**: Checks density after each post-processing step

**Logic**:

```python
max_density = 0.3

after_each_post_processing_step:
    if current_density >= max_density:
        log_warning("Density limit reached")
        stop_post_processing()
```

**Why**: Prevents runaway relationship creation (complete graph problem).

**Result**: Stopped at density 0.54 in problematic test, preventing complete graph.

**See**: `GRAPH-RAG-CONSOLIDATED.md` Section 6.4

---

#### 3. Edge Weights

**File**: `agents/community_detection_agent.py`

**Innovation**: Weight edges by relationship type and confidence

**Logic**:

- LLM-extracted: 1.0 × confidence (highest weight)
- Co-occurrence: 1.0 × confidence
- Cross-chunk: 0.5 × confidence (penalized)
- Semantic similarity: 0.8 × confidence
- Predicted: 0.4 × confidence (most penalized)

**Why**: Prioritize high-quality relationships for community structure.

**See**: `GRAPH-RAG-CONSOLIDATED.md` Section 6.3

---

### GraphRAG Pipeline Performance

**Current Production Run** (13,069 chunks, 638 videos):

| Stage               | Status             | Time           | Rate                  |
| ------------------- | ------------------ | -------------- | --------------------- |
| Graph Extraction    | 24% (3,148 chunks) | 8 hours        | ~390 chunks/hour      |
| Entity Resolution   | Pending            | Est. 2-3 hours | Fast (no LLM)         |
| Graph Construction  | Pending            | Est. 3-4 hours | Post-processing heavy |
| Community Detection | Pending            | Est. 1 hour    | One-time for all      |

**Total Estimated**: ~40 hours

**Bottleneck**: LLM calls in extraction (~15s each × 13k = ~54 hours theoretical minimum)

**See**: `OVERNIGHT-RUN-ANALYSIS.md` for detailed production metrics.

---

### GraphRAG Testing Strategy

**Critical Lesson**: Test with diverse data, not consecutive chunks!

**Methodology**:

- **Wrong**: First 12 chunks (all from same video) → Transitive connections
- **Right**: 12 random chunks from 12 different videos → True diversity

**Tool**: `scripts/run_random_chunk_test.py`

**Impact**: Revealed the transitive connection problem that caused complete graphs.

**See**: `GRAPH-RAG-CONSOLIDATED.md` Section 8, `RANDOM-CHUNK-TEST-GUIDE.md`

## Stage Details

### Common Stage Interface

All stages implement `BaseStage`:

```python
class MyStage(BaseStage):
    name = "my_stage"  # Registry key
    description = "Stage description"
    ConfigCls = MyStageConfig  # Configuration class

    def iter_docs(self):
        # Return iterable of documents to process
        pass

    def handle_doc(self, doc):
        # Process single document
        pass

    def setup(self):
        # Optional: Initialize stage-specific resources
        super().setup()
```

### Stage Configuration Pattern

All stage configs extend `BaseStageConfig`:

```python
@dataclass
class MyStageConfig(BaseStageConfig):
    # Stage-specific fields
    my_param: str = "default"

    @classmethod
    def from_args_env(cls, args, env, default_db):
        base = BaseStageConfig.from_args_env(args, env, default_db)
        my_param = getattr(args, "my_param", None) or env.get("MY_PARAM", "default")
        return cls(**vars(base), my_param=my_param)
```

### Individual Stage Documentation

#### Ingest Stage

**Purpose**: Fetch raw documents from external sources.

**Input**: External sources (YouTube API, file system, web URLs, etc.)

**Output**: `raw_videos` collection (or source-specific raw collection)

**Key Features**:

- YouTube video metadata and transcript fetching
- Extensible architecture for other sources (PDFs, HTML, etc.)
- Idempotent processing (skips existing documents)

**Configuration**:

- Pulitzer filtering
- Video/channel/playlist selection
- Max document limits

#### Clean Stage

**Purpose**: Normalize and clean document text.

**Input**: `raw_videos` (or source-specific raw collection)

**Output**: `cleaned_transcripts`

**Key Features**:

- Text normalization (whitespace, line endings)
- LLM-powered cleaning for disfluencies
- Paragraph detection
- Stage cue removal

**Configuration**:

- LLM enable/disable
- Retry logic
- Concurrency control

**GraphRAG Integration**: Provides clean text for entity extraction.

#### Enrich Stage

**Purpose**: Extract semantic metadata from cleaned text.

**Input**: `cleaned_transcripts`

**Output**: `enriched_transcripts`

**Key Features**:

- Entity extraction
- Concept identification
- Code block detection
- Tag/keyword extraction
- Difficulty scoring

**Configuration**:

- LLM model selection
- Extraction coroutines
- Retry and backoff settings

**GraphRAG Integration**: Provides initial entity candidates for graph construction.

#### Chunk Stage

**Purpose**: Split documents into semantic chunks for embedding.

**Input**: `cleaned_transcripts` or `enriched_transcripts`

**Output**: `video_chunks`

**Key Features**:

- Multiple chunking strategies:
  - **Fixed**: Token-based windows with overlap
  - **Recursive**: Character-delimited with size limits
  - **Semantic**: Embedding-based boundary detection
- Overlap handling
- Source type tracking

**Configuration**:

- Chunk strategy selection
- Token size and overlap percentage
- Split characters for recursive strategy
- Semantic model for semantic strategy

**Document Type Note**: Different document types may require different chunk sizes. PDFs might use smaller chunks than video transcripts.

#### Embed Stage

**Purpose**: Generate vector embeddings for chunks.

**Input**: `video_chunks` (without embeddings)

**Output**: `video_chunks` (with embeddings)

**Key Features**:

- Voyage AI embeddings (default)
- Rate limiting and retry logic
- Batch processing
- Unit normalization

**Configuration**:

- Embedding source (chunk text vs summary)
- Model selection
- Rate limits

#### Redundancy Stage

**Purpose**: Detect and mark duplicate/redundant chunks.

**Input**: `video_chunks` (with embeddings)

**Output**: `video_chunks` (with redundancy scores and flags)

**Key Features**:

- Cosine similarity-based detection
- Adjacency guard (prevents false positives from overlapping chunks)
- Non-adjacent fallback
- LLM validation for borderline cases
- Canonicalization (marks primary chunk)

**Configuration**:

- Similarity threshold
- LLM margin for borderline cases
- Adjacency guard enable/disable
- Adjacent override threshold

**GraphRAG Integration**:

- `get_entity_canonicalization_signals()`: Provides similarity clusters and grouping hints
- `get_chunk_similarity_matrix()`: Provides similarity scores for entity resolution

#### Trust Stage

**Purpose**: Compute trust scores for chunks.

**Input**: `video_chunks` (with redundancy scores)

**Output**: `video_chunks` (with trust scores)

**Key Features**:

- Multi-factor scoring:
  - Consensus (redundancy-based)
  - Recency (publication date)
  - Engagement (views, likes, comments)
  - Code presence
- LLM validation for borderline cases
- Auto-trigger LLM for specific conditions

**Configuration**:

- LLM enable/disable
- Auto-LLM trigger bands
- Neighbor count for context

**GraphRAG Integration**:

- `get_entity_trust_scores()`: Aggregates trust scores for entities
- `propagate_trust_to_entities()`: Updates GraphRAG entities with trust scores
- `get_trust_statistics()`: Provides trust distribution statistics

## Creating New Pipelines

### Pipeline Template

```python
"""
My Custom Pipeline

Description of what this pipeline does.
"""

import logging
from typing import List
from dataclasses import dataclass
from app.pipelines.base_pipeline import StageSpec, PipelineRunner
from config.stage_config import BaseStageConfig

logger = logging.getLogger(__name__)


@dataclass
class MyPipelineConfig:
    """Configuration for My Pipeline."""
    db_name: Optional[str] = None
    continue_on_error: bool = True
    # Stage-specific configs
    stage1_config: Optional[Stage1Config] = None
    stage2_config: Optional[Stage2Config] = None

    @classmethod
    def from_args_env(cls, args, env, default_db):
        # Create configuration from args and environment
        pass


class MyPipeline:
    """My custom pipeline."""

    def __init__(self, config: MyPipelineConfig):
        self.config = config
        self.specs = self._create_stage_specs()
        self.runner = PipelineRunner(
            self.specs,
            stop_on_error=not config.continue_on_error
        )
        # Initialize database connection if needed
        from app.services.utils import get_mongo_client
        from config.paths import DB_NAME
        self.client = get_mongo_client()
        self.db = self.client[config.db_name or DB_NAME]

    def _create_stage_specs(self) -> List[StageSpec]:
        return [
            StageSpec(stage="stage1", config=self.config.stage1_config),
            StageSpec(stage="stage2", config=self.config.stage2_config),
        ]

    def setup(self) -> None:
        """Set up pipeline (create collections, indexes, etc.)."""
        logger.info("Setting up My Pipeline...")
        # Setup logic here
        logger.info("My Pipeline setup completed")

    def run_stage(self, stage_name: str) -> int:
        """Run a specific stage."""
        for spec in self.specs:
            if spec.stage == stage_name:
                return PipelineRunner([spec]).run()
        raise ValueError(f"Unknown stage: {stage_name}")

    def run_full_pipeline(self) -> int:
        """Run the complete pipeline."""
        logger.info("Starting My Pipeline execution")
        self.setup()
        exit_code = self.runner.run()
        if exit_code == 0:
            logger.info("My Pipeline completed successfully")
        else:
            logger.error("My Pipeline failed")
        return exit_code
```

### Best Practices

1. **Use Stage Registry Keys**: Always use string keys (e.g., `"clean"`) in `StageSpec`, not class references
2. **Configuration Pattern**: Use `from_args_env()` for configuration anagement
3. **Error Handling**: Set `continue_on_error` based on pipeline requirements
4. **Database Connection**: Initialize in `__init__` if `setup()` needs it
5. **Logging**: Use module-level logger for all pipeline operations
6. **Documentation**: Include docstrings explaining pipeline purpose and flow

### Testing New Pipelines

1. Test individual stages first
2. Test pipeline with minimal data
3. Verify data flow between stages
4. Test error handling and recovery
5. Validate output collections

## Pipeline Orchestration

### Running Pipelines via CLI

**Ingestion Pipeline**:

```bash
# Via main.py orchestrator
python main.py pipeline --playlist_id <ID> --max 10 --llm

# Direct pipeline execution
python app/pipelines/ingestion_pipeline.py --playlist_id <ID> --max 10 --llm

# Single stage execution
python app/pipelines/ingestion_pipeline.py --stage clean --llm
```

**GraphRAG Pipeline**:

```bash
# Full pipeline
python run_graphrag_pipeline.py

# Single stage
python run_graphrag_pipeline.py --stage entity_resolution

# Status and cleanup
python run_graphrag_pipeline.py --status
python run_graphrag_pipeline.py --cleanup
```

### Running Pipelines Programmatically

```python
from app.pipelines.ingestion_pipeline import IngestionPipeline, IngestionPipelineConfig
import os

# Create configuration
env = dict(os.environ)
args = argparse.Namespace(
    playlist_id="PLxxx",
    max=10,
    llm=True,
    verbose=False
)
config = IngestionPipelineConfig.from_args_env(args, env, "mongo_hack")

# Create and run pipeline
pipeline = IngestionPipeline(config)
exit_code = pipeline.run_full_pipeline()
```

### Pipeline Status Monitoring

**GraphRAG Pipeline** provides status monitoring:

```python
pipeline = GraphRAGPipeline(config)
status = pipeline.get_pipeline_status()
# Returns: {"pipeline_status": "active", "stage_statuses": {...}, "timestamp": ...}
```

**Cleanup Failed Stages**:

```python
cleanup_results = pipeline.cleanup_failed_stages()
# Returns: {"stage_name": count_of_cleaned_records, ...}
```

### Error Handling and Recovery

- **stop_on_error**: If `True`, pipeline stops on first stage failure
- **continue_on_error**: If `True`, pipeline continues after stage failures
- **Cleanup Methods**: Stages can implement cleanup methods to reset failed records
- **Retry Logic**: Individual stages handle retries via configuration

## Document Type Extensibility

### Current Architecture

**Source-Specific Raw Collections**: Each document type has its own raw collection:

- `raw_videos` - YouTube videos
- `raw_pdfs` - PDF documents (future)
- `raw_html` - HTML/web pages (future)

**Unified Chunks Collection**: All chunks stored in `video_chunks` with:

- `source_type`: Document source ("youtube", "pdf", "html", etc.) -支持的 Source-specific identifiers: `video_id` (YouTube), `document_id` (PDFs), etc.

### Adding New Document Types

**Step 1: Create Source-Specific Raw Collection**

```python
# In config/paths.py
COLL_RAW_PDFS: Final[str] = "raw_pdfs"
```

**Step 2: Implement Ingestor Stage**

```python
class PDFIngestStage(BaseStage):
    name = "pdf_ingest"
    # Read PDFs, extract text, store in raw_pdfs collection
    # Include source_type="pdf" in all documents
```

**Step 3: Update Chunk Stage**

```python
# Ensure chunks include source_type field
chunk_doc = {
    "chunk_id": "...",
    "source_type": "pdf",  # Critical field
    "document_id": "...",  # Source-specific ID
    "text": "...",
    # ... other fields
}
```

**Step 4: Configure Stage-Specific Settings**

Different document types may need different configurations:

- **Chunk size**: PDFs might use 300 tokens vs 500 for videos
- **Chunking strategy**: PDFs might prefer recursive, videos prefer fixed
- **Embedding source**: PDFs might use full text, videos might use summaries

**Step 5: Create Type-Specific Pipeline (Optional)**

```python
class PDFIngestionPipeline(IngestionPipeline):
    """PDF-specific ingestion pipeline with optimized settings."""

    def _create_stage_specs(self):
        # Override with PDF-optimized configurations
        return [
            StageSpec(stage="pdf_ingest", config=...),
            StageSpec(stage="clean", config=clean_config_with_pdf_settings),
            # ... etc
        ]
```

### Configuration per Document Type

Use environment variables or configuration files to manage type-specific settings:

```bash
# PDF-specific chunking
PDF_CHUNK_SIZE=300
PDF_CHUNK_STRATEGY=recursive

# HTML-specific chunking
HTML_CHUNK_SIZE=400
HTML_CHUNK_STRATEGY=semantic
```

### Best Practices

1. **Always include `source_type`**: Every chunk must identify its source
2. **Preserve source identifiers**: Keep `video_id`, `document_id`, etc. for traceability
3. **Type-specific configurations**: Different types may need different processing
4. **Consistent metadata**: Use common fields across types (title, author, published_at)
5. **Document type registry**: Consider creating a registry for type-specific configurations

## Conclusion

The pipeline system provides a flexible, extensible architecture for processing documents and building knowledge graphs. By following the established patterns, you can create new pipelines and stages that integrate seamlessly with the existing system.

For more information, see:

- `documentation/EXECUTION.md` - Execution patterns and quick reference
- `documentation/GRAPH-RAG.md` - GraphRAG implementation details
- `documentation/ORCHESTRATION-INTERFACE.md` - Orchestration patterns
