## 🧱 Technical Architecture - GraphRAG Knowledge Manager MCP Server

### Architecture Layers

The system is organized into four main layers:

1. **MCP Server Layer**: Exposes tools, resources, and prompts via Model Context Protocol
2. **Knowledge Graph Layer**: GraphRAG for entity-relationship knowledge representation
3. **Document Processing Layer**: Multi-stage pipelines for ingestion and enrichment
4. **Storage Layer**: MongoDB collections and indexes for persistence

### 1. MCP Server Layer

**Purpose**: Expose knowledge graph operations via Model Context Protocol for integration with AI assistants.

**Components**:

- **MCP Tools**: Knowledge graph queries, document ingestion, entity management
- **MCP Resources**: Schema definitions, entity templates, community summaries
- **MCP Prompts**: Query expansion, entity extraction, relationship inference

**See**: `documentation/MCP-SERVER.md` for detailed MCP server documentation.

### 2. Document Ingestion

**Purpose**: Fetch raw documents from various sources with extensible architecture.

**YouTube Ingestion**:

- Uses YouTube API to fetch:
  - metadata (title, channel, publish date, stats, category)
  - transcript (via youtube-transcript-api)
  - thumbnail URL
- Adds derived fields: duration, keywords, engagement score
- Inserts raw → `mongodb.collection("raw_videos")`

**Future Document Types**:

- PDF documents → `raw_pdfs` collection
- HTML/web pages → `raw_html` collection
- Each type maintains source-specific fields and configurations

**Key Design**: Source-specific raw collections with unified processing pipeline.

### 3. Document Processing Layer (Ingestion Pipeline)

**Purpose**: Process raw documents through multi-stage pipeline into enriched, embedded chunks.

**Pipeline Flow**: `ingest → clean → enrich → chunk → embed → redundancy → trust`

Each stage writes to a collection (demonstrating "context engineering via structured memory"):

| Stage      | Function                                                                                                                   | MongoDB Collection   |
| ---------- | -------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| Clean      | Fix punctuation, remove disfluencies, paragraphize using an LLM (Voyage AI embeddings optional for semantic segmentation). | cleaned_transcripts  |
| Enrich     | Extract entities, concepts, tags, code blocks using LLM inference.                                                         | enriched_transcripts |
| Chunk      | Splits documents into semantic chunks (configurable size per document type).                                               | video_chunks         |
| Embed      | Creates embeddings with Voyage AI API → stores vectors + metadata in Atlas Vector Search.                                  | video_chunks         |
| Redundancy | Detects duplicate/redundant chunks using cosine similarity and LLM validation.                                             | video_chunks         |
| Trust      | Computes trust scores based on consensus, recency, engagement, and code presence.                                          | video_chunks         |

**See**: `documentation/PIPELINE.md` for comprehensive pipeline documentation.

### 4. Knowledge Graph Layer (GraphRAG Pipeline)

**Purpose**: Build knowledge graph from processed chunks for enhanced query understanding.

**Pipeline Flow**: `graph_extraction → entity_resolution → graph_construction → community_detection`

| Stage                       | Function                                                                                             | MongoDB Collection  |
| --------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------- |
| GraphExtractionAgent        | Extract entities and relationships from chunks using LLM with structured output.                     | entities, relations |
| EntityResolutionAgent       | Canonicalize and resolve entity references across chunks with fuzzy matching and confidence scoring. | entities            |
| RelationshipResolutionAgent | Resolve and merge relationship references between entities with confidence scoring.                  | relations           |
| CommunityDetectionAgent     | Detect entity communities using hierarchical Leiden algorithm and generate community summaries.      | communities         |

**Key Features**:

- Multi-strategy entity resolution (exact match, fuzzy match, LLM)
- Hierarchical community detection with Leiden algorithm
- Trust score propagation from chunks to entities
- Canonicalization signals from redundancy stage

**See**: `documentation/GRAPH-RAG.md` for detailed GraphRAG implementation.

### 5. Retrieval + Generation Agent (RAG Core)

- Query embedding → Atlas Vector Search → retrieve top-k chunks.
- Compose contextual prompt (system + retrieved content).
- Generate response with LLM (GPT-4 / Voyage LLM).
- Optionally: store query + retrieved chunks + answer back to `memory_logs` for the agent's long-term memory.

### 5.1. GraphRAG Enhanced Retrieval

- Entity extraction from user queries → knowledge graph traversal.
- Community-based context assembly for comprehensive answers.
- Hybrid retrieval combining traditional vector search with graph-based reasoning.
- Enhanced answer generation with entity relationships and community summaries.

### 6. Storage Layer

**MongoDB Collections**:

**Raw Document Collections** (source-specific):

- `raw_videos`: YouTube videos
- Future: `raw_pdfs`, `raw_html` for other document types

**Processing Collections**:

- `cleaned_transcripts`: Cleaned text
- `enriched_transcripts`: Entities, concepts, tags
- `video_chunks`: Chunks with embeddings, quality scores, and `source_type` field

**GraphRAG Collections**:

- `entities`: Canonicalized entities
- `relations`: Entity relationships
- `communities`: Entity communities
- `entity_mentions`: Entity mentions in chunks

**Application Collections**:

- `memory_logs`: Query/answer history

**Key Design**: Unified chunks collection with `source_type` field supports multiple document types.

### 7. Interface Layer

Streamlit dashboard showing:

- Filters: channel / topic / date
- Context map: embedding clusters (UMAP)
- Interactive Q&A panel
- "Memory growth" timeline (how context expands as new videos are added)
- GraphRAG pipeline status and monitoring
- Knowledge graph visualization and exploration

### ☁️ Technology Stack

| Component         | Tech                        | Purpose                                               |
| ----------------- | --------------------------- | ----------------------------------------------------- |
| Persistent memory | MongoDB Atlas Vector Search | Stores long-term semantic memory and knowledge graphs |
| Knowledge Graphs  | NetworkX + Graspologic      | Entity-relationship graphs and community detection    |
| Embeddings        | Voyage AI Embeddings API    | High-quality, compact context representation          |
| LLM reasoning     | OpenAI / Voyage LLM         | Adaptive agents for extraction, enrichment, and query |
| Data ingestion    | YouTube API + extensible    | Multi-source document ingestion                       |
| MCP Protocol      | Model Context Protocol      | Standard interface for AI assistant integration       |
| Visualization     | Streamlit + Plotly          | Shows knowledge graphs and context evolution          |

### 🧠 Why This Architecture

- **MCP Server**: Standard protocol for AI assistant integration
- **GraphRAG**: Knowledge graph-based retrieval for better context understanding
- **Multi-Source**: Extensible architecture supports multiple document types
- **Pipeline Architecture**: Modular, testable, and maintainable processing
- **Document Type Awareness**: Source-specific configurations and unified processing
- **Multiple Memory Layers**: Raw → cleaned → enriched → embedded → knowledge graph

### 🚀 Demo Narrative (7-minute flow)

1. Ingest new YouTube video – show raw JSON entry.
2. Agents run – transcript cleaned, speakers inferred, visuals summarized.
3. MongoDB Atlas UI – display embedded chunks in vector search index.
4. User query: “How has this creator’s strategy changed over time?”
5. Live RAG answer: agent retrieves relevant clips + summarizes evolution.
6. Show “memory log” – the agent stores this Q&A for reuse later.
7. Dashboard: updated vector map proving persistent, adaptive memory.

### 🗓️ Week-of-Hackathon Plan

| Day               | Milestone                                                                                                 |
| ----------------- | --------------------------------------------------------------------------------------------------------- |
| D-6 → D-4         | Finalize schema (video_id, chunks, embedding, metadata). Test Atlas Vector Search + Voyage embedding API. |
| D-3 → D-2         | Build Python agents for ingest → clean → embed. Use sample 10 videos.                                     |
| D-1               | Create minimal Streamlit UI + retrieval endpoint.                                                         |
| Hackathon Day 1–2 | Integrate Atlas + Voyage credentials; polish demo; prep slides.                                           |
| Final Pitch       | Present live ingestion → question → context-aware answer.                                                 |

### 📄 Key Deliverables

**Core Components**:

- `app/pipelines/ingestion_pipeline.py` – Complete ingestion pipeline with all stages
- `app/pipelines/graphrag_pipeline.py` – GraphRAG knowledge graph pipeline
- `main.py` – Orchestrator using implemented pipelines
- `agents/` – LLM-powered agents for extraction, enrichment, and processing
- `app/stages/` – Pipeline stages following BaseStage pattern

**Documentation**:

- `documentation/PIPELINE.md` – Comprehensive pipeline architecture and usage
- `documentation/MCP-SERVER.md` – MCP server implementation and integration
- `documentation/GRAPH-RAG.md` – GraphRAG implementation details
- `documentation/EXECUTION.md` – Execution patterns and quick reference
- `README.md` – Project overview and getting started

**Application**:

- `streamlit_app.py` – Interactive demo and monitoring dashboard
- `chat.py` – Multi-agent CLI chat system
- `run_graphrag_pipeline.py` – GraphRAG pipeline runner with status/cleanup

**Configuration**:

- `mongodb_schema.json` – Collections + vector index config
- `config/` – Centralized configuration management
