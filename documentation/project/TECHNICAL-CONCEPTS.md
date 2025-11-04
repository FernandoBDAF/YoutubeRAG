## Technical Concepts Behind The Improvements

This guide explains, from first principles, the core techniques we use and the options we exposed for the demo. Each section ends with practical use cases so you can choose the right configuration quickly.

### 1) Vector Embeddings and Atlas Vector Search

Embeddings map text to vectors so we can measure semantic similarity by cosine distance. MongoDB Atlas Vector Search stores the vectors and lets us query by a vector using `$search` with `knnBeta`.

Key ideas:

- Vector dimensionality must match the embedding model (e.g., Voyage “voyage-2” at 1024 dims). The Atlas index definition must use that same dimension.
- Index status can be IN_PROGRESS before it becomes READY; retrieval quality and speed stabilize once READY. We add an index waiter in tooling to avoid races.

Use cases:

- High‑quality semantic search: use a modern hosted model (Voyage). Best for accuracy.
- Offline/deterministic: use a local hashing embedder (HashingVectorizer) to avoid external API calls. Best for offline demos and predictability.

### 2) Embedding Choices: Voyage vs HashingVectorizer

Voyage (API)

- Pros: high semantic fidelity, compact vectors, robust to noise.
- Cons: external API dependency, rate limits, cost.

HashingVectorizer (local)

- Pros: no network, deterministic, very fast to compute, simple to ship.
- Cons: bag‑of‑words style; lower semantic fidelity than neural embeddings; dimensionality must be selected and configured.

Use cases:

- Internet available, best quality demo: Voyage.
- Offline venue or cost‑sensitive: HashingVectorizer fallback.

### 3) Chunking and Normalization

Why chunk?

- Embedding long transcripts as a single vector makes retrieval fuzzy. Chunking yields multiple focused vectors so retrieval pulls the most relevant segments.

Techniques:

- Word/token windows with a small overlap keep context continuity.
- Normalize text before embedding (collapse whitespace, strip stage cues like `[APPLAUSE]`) to reduce noise.
- Persist `display_text` (cleaned) alongside original text for a consistent UI.

Use cases:

- Classroom lectures/transcripts: moderate chunks (~400–600 words) with 10% overlap.
- Code‑heavy segments: smaller chunks to keep examples intact.

### 4) Hybrid Retrieval (Keyword + Vector)

Atlas Search supports compound queries that combine keyword and vector:

- `text` operator captures exact keywords and field boosts.
- `knnBeta` returns top‑K nearest neighbors by cosine similarity.
- We can return both `search_score` (hybrid), and per‑operator scores (e.g., `vector_score`, `keyword_score`) via `searchScoreDetails`.
  - Retrieval code separation: `app/services/retrieval.py` hosts hybrid/keyword/vector/structured + rerank.

Benefits:

- Handles exact terms (identifiers, acronyms) and semantics together.
- Improves robustness for short queries and domain jargon.

Use cases:

- Technical queries mixing jargon and prose: “AVL rotations in balanced BSTs”.
- Entity‑centric questions where names/titles matter.

### 5) Redundancy Detection (De‑dup)

Goal: reduce repeated content caused by chunk overlap and repeated phrases.

Core signals:

- Cosine similarity between chunk vectors within a video.
- If `best_score ≥ DEDUP_THRESHOLD`, candidate is redundant.

Enhancements (env‑controlled):

- Borderline LLM trigger: only call LLM when `abs(best_score − DEDUP_THRESHOLD) ≤ DEDUP_LLM_MARGIN`.
- Canonicalization: symmetric pairs (A↔B) collapse to a single primary (smallest chunk_id); others point to `duplicate_of`.
- Adjacency guard: skip marking duplicates if the best match is the immediate neighbor (overlap noise). `DEDUP_SKIP_ADJACENT`.
- Non‑adjacent fallback: if best is adjacent, use the best non‑adjacent above threshold. `DEDUP_NONADJ_FALLBACK`.
- High‑confidence override: still mark adjacent duplicates if `best_score ≥ DEDUP_ADJ_OVERRIDE`.

Use cases:

- Clean demo tables (no chains): enable adjacency guard + non‑adjacent fallback.
- Strict compression: increase `DEDUP_THRESHOLD` and keep override high.
- Cost‑sensitive: keep LLM only for borderlines.

### 6) Trust Scoring

Goal: estimate reliability of a chunk. We combine:

- Consensus: similarity to peers (`redundancy_score` and neighbor context).
- Recency: `age_days` from published date.
- Engagement: channel/video metrics when available.
- Code presence: code blocks can increase confidence for how‑to queries.

LLM assist (optional):

- Auto trigger when: redundancy score in band, `code_present`, or recent (<30 days). `TRUST_LLM_AUTO` with `TRUST_LLM_BAND_LOW/HIGH`.
- Forced trigger: `TRUST_WITH_LLM=1`.

Use cases:

- Fresh tutorials/code reviews: LLM auto‑trust for recent/code‑present.
- Survey/meta questions: heuristic trust suffices (stable, cheap).

### 7) Upserts, Idempotency, and Batch Writes

Upsert flags (`*_UPSERT_EXISTING`) help skip recompute during iteration. For write throughput, use `bulk_write` to upsert multiple chunks per batch.

Use cases:

- Rapid re‑runs during dev: skip existing stages to save time.
- Big imports: batch upserts to reduce round‑trips.

### 8) Rate Limits and Concurrency

External calls (embeddings/LLM) can rate‑limit. We include:

- Central rate limiter with max RPM and jitter.
- Concurrency helpers with ordering and retries.

Use cases:

- Demos with strict API quotas: reduce QPS, increase batch sizes.
- Longer videos: parallelize LLM requests while preserving order.

### 9) Transcript Robustness and Proxies (YouTube)

Fetching transcripts can fail due to IP throttling. We support proxy rotation (via env), retries, and fallbacks. Clean stage post‑process strips stage cues and normalizes whitespace.

Use cases:

- Aggressive content fetching before a demo: rotate proxies, then cache.

### 10) Streaming LLM Answers

Interactive demos benefit from token streaming. We expose a streaming toggle so the answer appears progressively, and we preserve a non‑streaming path for reproducible capture/logging.

Use cases:

- Live demo: enable streaming.
- QA screenshots/regression tests: disable streaming for deterministic output.
  - LLM helper separation: `app/services/generation.py` hosts answering/streaming helpers used by RAG orchestrators.

### 13) Memory & Personalization (Agentic UX)

- Memory logs capture `query`, retrieved citations, and `answer`. We also record retrieval `mode` (vector/hybrid), retrieval `weights`, and `session_id`.
- The UI remembers session defaults (topic/channel); recent queries are listed for quick recall; a feedback summary shows the session’s average ratings and top tags.
  - Persona helpers: `app/services/persona_utils.py` (top tag inference); filter helpers: `app/services/filters.py`.

### 11) Environment Flags Cheat‑Sheet (selected)

- Redundancy: `DEDUP_THRESHOLD`, `DEDUP_LLM_MARGIN`, `DEDUP_SKIP_ADJACENT`, `DEDUP_NONADJ_FALLBACK`, `DEDUP_ADJ_OVERRIDE`, `DEDUP_WITH_LLM`.
- Trust: `TRUST_WITH_LLM`, `TRUST_LLM_AUTO`, `TRUST_LLM_BAND_LOW/HIGH`, `TRUST_LLM_NEIGHBORS`, `TRUST_UPSERT_EXISTING`.
- Chunk/Embed: `CHUNK_UPSERT_EXISTING`, `EMBEDDER=voyage|hashing`, `VECTOR_DIM`, `VOYAGE_*`.
- Concurrency/Rate: `VOYAGE_RPM`, backoff bases, retries.

### 12) GraphRAG Pipeline Architecture

The GraphRAG pipeline extends traditional RAG with knowledge graph construction:

- **Graph Extraction**: Extract entities and relationships from video chunks using LLM
- **Entity Resolution**: Canonicalize and resolve entity references across chunks
- **Graph Construction**: Build knowledge graph from resolved entities and relationships
- **Community Detection**: Identify entity communities and generate summaries

Key improvements:

- **Fixed Critical Bugs**: `setup()`, `get_pipeline_status()`, and `cleanup_failed_stages()` methods now work correctly
- **Stage Registry Integration**: Uses unified `PipelineRunner` pattern for consistency
- **Error Handling**: Robust error handling and recovery mechanisms
- **Status Monitoring**: Real-time pipeline status and cleanup capabilities

### 13) MCP Server Architecture

**Model Context Protocol (MCP)** is a standard protocol for AI assistants to interact with external systems. This project implements an MCP server that exposes knowledge graph operations.

**Key Concepts**:

- **MCP Tools**: Functions that AI assistants can call (e.g., query knowledge graph, ingest documents)
- **MCP Resources**: Data that AI assistants can read (e.g., entity schemas, community summaries)
- **MCP Prompts**: Pre-defined prompt templates for common operations

**Architecture**:

- MCP server layer sits above GraphRAG and ingestion pipelines
- Exposes GraphRAG operations as MCP tools
- Provides knowledge graph schemas as MCP resources
- Enables AI assistants to interact with the knowledge graph seamlessly

**See**: `documentation/MCP-SERVER.md` for detailed MCP server implementation.

### 14) Document Type Extensibility

**Current Architecture**:

- Source-specific raw collections: `raw_videos`, future `raw_pdfs`, `raw_html`
- Unified chunks collection: `video_chunks` with `source_type` field
- Configurable processing: Different chunk sizes, strategies per document type

**Adding New Document Types**:

1. Create source-specific raw collection (e.g., `raw_pdfs`)
2. Implement ingestor stage (e.g., `PDFIngestStage`)
3. Ensure chunks include `source_type="pdf"` field
4. Configure type-specific settings (chunk size, strategy)
5. Optionally create type-specific pipeline

**Benefits**:

- Clear separation of document sources in database
- Type-specific optimizations possible
- Unified processing pipeline for all types
- Easy to extend without breaking existing functionality

### 15) Testing Strategy

Comprehensive testing approach covering all project components:

- **Unit Tests (70%)**: Individual functions and classes with 80%+ coverage
- **Integration Tests (20%)**: Component interactions and database operations
- **End-to-End Tests (10%)**: Complete pipeline workflows and user scenarios
- **Performance Testing**: Load, stress, and benchmark testing
- **Mock Services**: OpenAI, MongoDB, and YouTube API mocking for isolated testing

Testing infrastructure:

- **Framework**: pytest with comprehensive dependencies and utilities
- **Test Data**: Synthetic, sample, and mock data management
- **CI/CD**: Automated testing pipeline with quality gates
- **Monitoring**: Test performance and reliability tracking

### 16) Recommended Presets

Demo (internet available, best quality)

- `EMBEDDER=voyage`, `DEDUP_SKIP_ADJACENT=true`, `DEDUP_NONADJ_FALLBACK=true`, `TRUST_LLM_AUTO=true`, set trust band to focus where needed, enable Hybrid Search tab.

Offline/low‑cost

- `EMBEDDER=hashing`, pre‑create index with matching dims, keep LLM off or only for borderlines, rely more on hybrid keyword+vector.

Fast iteration

- Disable expensive stages via upsert flags; run redundancy/trust with narrow scopes; enable batch upserts.

GraphRAG development

- Use `python run_graphrag_pipeline.py --status` to monitor pipeline health, `--cleanup` to recover from failures.

Pipeline development

- Use `app/pipelines/ingestion_pipeline.py` for complete ingestion with redundancy and trust stages.
- See `documentation/PIPELINE.md` for comprehensive pipeline documentation and patterns.
