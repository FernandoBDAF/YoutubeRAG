## Delivery Roadmap and Execution Plan

This is the single source of truth for scope, order of work, and status. Keep it updated as we implement.

### North Star

- Deliver a convincing hackathon demo: ingest → enrich → embed → retrieve → answer with citations, fully inside `Mongo_Hack/`.

### Scope (MVP cut)

- In-scope: ingestion, basic clean, basic enrich, chunk+embed, simple RAG, Streamlit UI, logs.
- Out-of-scope (MVP): heavy diarization, production auth, advanced analytics, autoscaling.

### Prioritized Order (milestones)

1. Schema ready in Atlas
   - Create collections per `mongodb_schema.json` (Atlas UI/CLI)
   - Create Vector Search index `embedding_index` on `video_chunks.embedding`
   - File present: `Mongo_Hack/mongodb_schema.json`
2. Ingestion working with transcripts
   - Fetch playlist/channel or explicit IDs
   - Store raw metadata + transcript in `raw_videos`
   - Derive `duration_seconds`, `keywords`, `engagement_score`
3. Clean (LLM-lite acceptable)
   - MVP: copy `transcript_raw` → `cleaned_transcripts`
   - Optional: `python Mongo_Hack/app/stages/clean.py --llm` to produce `cleaned_text` + `paragraphs`
   - Post-processing: strips stage cues like `[APPLAUSE]`, `[SQUEAKING]`, `[RUSTLING]`, `[MUSIC]`, `[LAUGHTER]`, `[NOISE]`, `[CLICKING]`; collapses multi-dashes; standardizes whitespace/newlines
4. Enrich (tags/entities/code)
   - Heuristics for `tags`, `entities`, `keyphrases`, `code_blocks`
   - Persist segments to `enriched_transcripts`
5. Per-chunk pipeline (chunk → enrich → embed)
   - Chunk cleaned text (~500 tokens, small overlap); write base chunk docs to `video_chunks`
   - Enrich each chunk via LLM to add `summary`, entities/concepts/relations, context, etc.
   - Embed chosen `embedding_text` (default `chunk_text`) with Voyage and persist vector
   - Verify vector index returns results in Atlas
6. RAG retrieval + generation + logging
   - Embed query; run `$vectorSearch` with filters
   - Re-rank by vector score, `trust_score`, recency (`age_days`)
   - Generate answer (optional LLM); log to `memory_logs`
7. Streamlit UI (filters + views)
   - Q&A: topic/channel/age filters + Markdown export
   - Compare: consensus/unique tag metrics + CSV/Markdown export
   - Unique: non-redundant chunks list
   - Summaries: build context and save summary
   - Memory: recent logs with citations
   - Adjustable RAG weights (vector/trust/recency)
   - Q&A: Popular Topics quick-select; Exclude redundant toggle; Full Retrieval Context
   - Controller tab to launch stages/pipeline with IDs and LLM toggle
8. Redundancy + TrustScore
   - Compute `is_redundant`, `duplicate_of`, `redundancy_score`
   - Redundancy LLM: auto-trigger only for borderline cosine matches around threshold (see DEDUP_LLM_MARGIN)
   - See `documentation/REDUNDANCY.md` for concepts, canonicalization, adjacency guard, and non-adjacent fallback/override flags
   - Compute `trust_score` (consensus/recency/engagement/code)
   - Trust LLM: auto-trigger in ambiguous band or when code_present/very recent (configurable)
9. QA + Demo polish
   - Run health check; seed or `main.py pipeline` end-to-end
   - Tune RAG weights via env (`RAG_WEIGHT_*`)
   - Finalize DEMO walkthrough and screenshots

### Status Board

- Env/scaffold: DONE
- Schema: PLANNED
- Ingestion: DONE (app/stages/ingest.py)
- Clean: DONE (MVP + optional LLM path)
- Enrich: DONE (heuristics)
- Chunk+Embed: DONE (app/stages/chunk_embed.py)
- Redundancy: DONE (app/stages/redundancy.py)
- Trust: DONE (app/stages/trust.py)
- RAG: DONE (retrieval, re-ranking, logging)
- UI: MVP READY (tabs, citations, filters, summaries, memory)
  - Added adjustable RAG weights in Q&A (vector/trust/recency)
  - Added Controller tab to trigger stages and full pipeline
  - Controller includes playlist/channel/video IDs and global LLM toggle
  - Summaries tab can generate Markdown via SummarizerAgent (optional LLM)
  - Compare tab shows trusted chunks tables and exports (CSV/MD)
  - Unique tab shows table and exports (CSV/MD)
  - Unique tab mini-dashboards: Top Tags and Trust histogram
  - Saved Summaries viewer (list, view, download, delete)
  - Compare tab: Top Channels summary (avg trust)
  - Q&A: Popular Topics quick-select augments tag regex filter
  - Q&A: Exclude redundant toggle filters out `is_redundant=true`
  - Q&A: Full Retrieval Context view and download
- Redundancy/Trust: DONE
- Agents: IN PROGRESS (Clean + Enrich wired; LLM flags + heuristic fallbacks)
- Pipelines: DONE (unified on PipelineRunner pattern; GraphRAG pipeline integrated and fixed)
- Ingestion Pipeline: DONE (complete pipeline with all stages including redundancy and trust)
- GraphRAG Pipeline: DONE (critical bugs fixed: setup(), get_pipeline_status(), cleanup_failed_stages())
- Testing Strategy: DONE (comprehensive TESTING.md documentation created)
- Documentation: DONE (updated for MCP server vision; PIPELINE.md created)

### Definitions of Done (per stage)

- Ingestion: ≥10 docs in `raw_videos` with transcripts or placeholders.
- Clean: `cleaned_transcripts` exists for all ingested videos.
- Enrich: segments with tags/entities/code for all cleaned videos.
- Chunk+Embed: `video_chunks` populated, vector index returns results for a probe.
- RAG: Answers include citations; `memory_logs` entries stored.
- UI: End-to-end demo flows run from sidebar filters.

Notes: For small datasets, answers may look similar across queries; increase Top‑K, tweak weights, or expand the seed set.

### Commands (quick reference)

- Unified Stage CLI flags (all stages):

  - `--db_name` override database name (defaults to `config.paths.DB_NAME` or `$DB_NAME`)
  - `--llm` enable LLM-assisted path when stage supports it
  - `--max` limit processing count when stage supports it
  - `--verbose` extra logs
  - `--dry_run` compute but do not write to DB
  - `--upsert_existing` overwrite/replace existing records when applicable
  - `--video_id` process a single video when supported
  - `--concurrency` control worker/concurrency when supported

- Programmatic invocation (all stages follow this pattern):

  - Example (Clean):
    ```python
    from app.stages.clean import CleanStage, CleanConfig
    CleanStage().run(CleanConfig(db_name="mongo_hack", use_llm=True, max=10))
    ```
  - Example (Enrich):
    ```python
    from app.stages.enrich import EnrichStage, EnrichConfig
    EnrichStage().run(EnrichConfig(db_name="mongo_hack", use_llm=False, max=20))
    ```
  - Example (Chunk):
    ```python
    from app.stages.chunk import ChunkStage, ChunkConfig
    ChunkStage().run(ChunkConfig(db_name="mongo_hack", chunk_strategy="fixed"))
    ```

- Install deps: `pip install -r Mongo_Hack/requirements.txt`
- Ingest playlist: `python Mongo_Hack/app/stages/ingest.py --playlist_id <ID> --max 10`
- Ingest channel: `python Mongo_Hack/app/stages/ingest.py --channel_id <ID> --max 10`
- Ingest IDs: `python Mongo_Hack/app/stages/ingest.py --video_ids <id1> <id2>`
- Clean (MVP): `python Mongo_Hack/app/stages/clean.py [--db_name mongo_hack]`
- Clean (LLM): `python Mongo_Hack/app/stages/clean.py --llm [--db_name mongo_hack]` (or set `CLEAN_WITH_LLM=1`)
- Enrich: `python Mongo_Hack/app/stages/enrich.py [--db_name mongo_hack]`
  - Optional LLM: `python Mongo_Hack/app/stages/enrich.py --llm [--db_name mongo_hack]` (or set `ENRICH_WITH_LLM=1`)
  - Orchestrator: `python Mongo_Hack/main.py enrich --llm [--db_name mongo_hack]`
- Chunk: `python Mongo_Hack/app/stages/chunk.py [--db_name mongo_hack]`
  - Strategies:
    - Fixed: `--chunk_strategy fixed --token_size 500 --overlap_pct 0.15`
    - Recursive: `--chunk_strategy recursive --token_size 400 --overlap_pct 0.10 --split_chars ".,;"`
    - Semantic: `--chunk_strategy semantic --token_size 500 --overlap_pct 0.15 --split_chars "." --semantic_model text-embedding-3-small`
- Enrich (per-chunk LLM): `python Mongo_Hack/app/stages/enrich.py [--db_name mongo_hack]`
- Embed: `python Mongo_Hack/app/stages/embed.py [--db_name mongo_hack] [--embed_source chunk|summary]`
  - Rate limit (recommended for demos): `export VOYAGE_RPM=5` (defaults to 20)
  - Concurrency: embed batching uses Voyage client with backoff
- Redundancy: `python Mongo_Hack/app/stages/redundancy.py [--db_name mongo_hack]`
  - Optional LLM: `python Mongo_Hack/app/stages/redundancy.py --llm [--db_name mongo_hack]` (or set `REDUNDANCY_WITH_LLM=1`)
  - Orchestrator: `python Mongo_Hack/main.py redundancy --llm [--db_name mongo_hack]`
- Trust: `python Mongo_Hack/app/stages/trust.py [--db_name mongo_hack]`
  - Optional LLM: `python Mongo_Hack/app/stages/trust.py --llm [--db_name mongo_hack]` (or set `TRUST_WITH_LLM=1`)
  - Orchestrator: `python Mongo_Hack/main.py trust --llm [--db_name mongo_hack]`
- Compress (optional): `python Mongo_Hack/app/stages/compress.py [--db_name mongo_hack]`
  - Example: `python Mongo_Hack/app/stages/compress.py --video_id ZA-tUyM_y7s --target_tokens 1200 --ratio 0.4`
  - Source: `--source cleaned` (default) or `--source enriched`
  - Fields written: `compressed_text`, `compression_meta`
- Seed demo (playlist): `python Mongo_Hack/app/stages/seed_demo.py` (edit playlist ID first)
- Run UI: `streamlit run Mongo_Hack/streamlit_app.py`
- Orchestrator: `python Mongo_Hack/main.py <stage>` (see README)
  - **Ingestion pipeline**: `python main.py pipeline --playlist_id <ID> --max 10 --llm` (uses `app/pipelines/ingestion_pipeline.py`)
  - **GraphRAG pipeline**: `python run_graphrag_pipeline.py [--stage <stage_name>] [--status] [--cleanup]`
  - **Legacy example**: `python Mongo_Hack/app/pipelines/examples/yt_clean_enrich.py` (for reference, will be removed)
  - **Pipeline documentation**: See `documentation/PIPELINE.md` for comprehensive pipeline usage
  - Atlas index helper: `Mongo_Hack/scripts/atlas_index_create.sh <PROJECT_ID> <CLUSTER_NAME>`

### Data Contracts (key fields)

- `raw_videos`: video_id, title, channel_id, published_at, duration_seconds, stats{viewCount,likeCount,commentCount}, keywords[], transcript_raw?, transcript_language?, thumbnail_url
- `cleaned_transcripts`: video_id, language?, cleaned_text, paragraphs[{start,end,text}]
- `enriched_transcripts`: video_id, segments[{start,end,text,tags[],entities[],keyphrases[],code_blocks[],difficulty?}]
- `video_chunks`: video_id, chunk_id, text, source_type (e.g., "youtube", "pdf", "html"), metadata{start_ms?,end_ms?,tags[],speakers?,visuals?,keywords[]}, embedding[], embedding_model, embedding_dim, redundancy_score, trust_score, is_redundant, duplicate_of
- `memory_logs`: query, retrieved[{video_id,chunk_id,score}], answer, created_at
- **GraphRAG Collections:**
  - `entities`: name, type, description, confidence, canonical_name, trust_score, centrality_score
  - `relations`: subject_id, object_id, relation_type, description, confidence, weight
  - `communities`: entities[], level, coherence_score, summary, keywords[]
  - `entity_mentions`: entity_id, chunk_id, video_id, mention_text, context, confidence

### Risks and Mitigations

- Transcript gaps: improved transcript fallback (English manual → generated → any); if still missing, Clean stage falls back to `description`.
- Rate limits: batch queries, small datasets (≤10 videos), cache partial results.
- Vector index readiness delays: build early; gate chunk step on index.
- Environment drift: central Mongo client auto-loads `.env`; DB name configurable via `MONGODB_DB`.

### Decision Log (append entries below)

- 2025-10-05: MVP clean uses non-LLM stub; upgrade later to LLM per PROMPTS.md.
- 2025-10-05: Added optional LLM clean path via `--llm`.
- 2025-10-05: Wired EnrichmentAgent behind `--llm` with safe heuristic fallback.
- 2025-10-05: Orchestrator supports `main.py enrich --llm` and passes flag in full pipeline.
- 2025-10-05: Added ChunkEmbedAgent `--llm` option and wired redundancy/trust `--llm` flags.
- 2025-10-05: Streamlit UI exposes RAG weight sliders and passes weights to `rag_answer`.
- 2025-10-05: Refactored stages into `app/stages/` and services into `app/services/`.
- 2025-10-05: Health check now validates Atlas vector index presence and dims.
- 2025-10-06: Unified env loading in `get_mongo_client()`; DB name from `MONGODB_DB` (default `mongo_hack`).
- 2025-10-06: Ingest handles private/404 playlists and improved transcript fallbacks (manual → generated → any language).
- 2025-10-06: Clean stage falls back to `description` when transcript is absent to keep pipeline moving.
- 2025-10-06: Switched to official Voyage AI Python client; added HTTP fallback, exponential backoff, and a `RateLimiter` with `VOYAGE_RPM` and jitter.
- 2025-10-06: Baked default playlist ID `PLdlA6gN07G8dyQs86ebumuNiiqcyfXb8f` in seed; health check verified all four stage counts and vector dim.
- 2025-10-10: Redundancy refined: fixed `duplicate_of` formatting, added canonicalization (primary chunk), adjacency guard with non-adjacent fallback and high-confidence override; added `redundancy_method` and `redundancy_reason` fields.
- 2025-10-10: New envs for redundancy/trust documented in `env.example` (`DEDUP_THRESHOLD`, `DEDUP_LLM_MARGIN`, `DEDUP_SKIP_ADJACENT`, `DEDUP_NONADJ_FALLBACK`, `DEDUP_ADJ_OVERRIDE`, `TRUST_LLM_AUTO`, `TRUST_LLM_BAND_LOW/HIGH`, `TRUST_LLM_NEIGHBORS`, `TRUST_UPSERT_EXISTING`).
- 2025-10-10: Chunking/embedding hygiene: strip stage cues before embedding and persist `display_text` for UI.
- 2025-10-10: Documentation added: `documentation/REDUNDANCY.md` (redundancy + trust linkage) and `documentation/TECHNICAL-CONCEPTS.md` (embeddings, hybrid search, chunking, concurrency, env presets).
- 2025-01-27: GraphRAG Pipeline fixes: Fixed critical bugs in `setup()`, `get_pipeline_status()`, and `cleanup_failed_stages()` methods. Removed unused functions and added comprehensive TODO comments for future enhancements.
- 2025-01-27: Testing Strategy: Created comprehensive `documentation/TESTING.md` with detailed testing plans for all project components, including unit tests, integration tests, and end-to-end testing strategies.
- 2025-01-27: Ingestion Pipeline: Created `app/pipelines/ingestion_pipeline.py` with all stages (ingest → clean → enrich → chunk → embed → redundancy → trust). Updated `main.py` to use implemented pipelines instead of artificial stage calling.
- 2025-01-27: Documentation Update: Updated all documentation to reflect "GraphRAG Knowledge Manager MCP Server" vision. Created `documentation/PIPELINE.md` for comprehensive pipeline documentation.

### Next Up (active)

- Schema: validate Atlas Vector index is READY for current cluster (see `main.py wait_index`). Index filters added for Vector Search (metadata.age_days, metadata.channel_id, metadata.tags, trust_score).
- QA & Demo Checklist:
  - Run `python Mongo_Hack/health_check.py` (env/DB/collections/embedding).
  - (Optional) Run `python Mongo_Hack/main.py wait_index` to ensure Atlas Search index is READY before retrieval tests.
  - Run `python Mongo_Hack/main.py pipeline --playlist_id <ID> --max 5 --llm`.
  - Open UI and test Q&A (topic/channel/age/trust filters), Compare, Unique, Summaries, Memory.
  - Test the new Hybrid Search tab and CSV export; compare with Vector Search; verify per-operator scores appear.
  - Q&A: enable streaming; try the "Use Hybrid Retrieval for Q&A" toggle; confirm memory_logs include `mode`, `weights`, and `session_id`.
  - **CLI Chat**: Run `python chat.py --top_k 200` and test multi-turn conversations with memory continuity.
  - Note: code refactor split retrieval/generation/helpers and enrich utils; see README Folder Layout.
  - Review `docs/CHAT.md` for CLI chat architecture and `docs/ORCHESTRACTION-INTERFACE.md` for orchestrator patterns.
  - Assess answer quality; tune `RAG_WEIGHT_*` via env; consider expanding the seed set for more diverse answers.
  - Capture screenshots and rehearse `docs/DEMO.md` sequence.
