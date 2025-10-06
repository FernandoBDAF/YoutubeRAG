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
4. Enrich (tags/entities/code)
   - Heuristics for `tags`, `entities`, `keyphrases`, `code_blocks`
   - Persist segments to `enriched_transcripts`
5. Chunk + Embeddings + Vector index
   - Chunk enriched text (~500 tokens, small overlap)
   - Embed with Voyage; upsert chunks + `metadata` to `video_chunks`
   - Verify vector index returns results in Atlas
   - Optional: `--llm` chunking via ChunkEmbedAgent (heuristic fallback)
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
   - Compute `trust_score` (consensus/recency/engagement/code)
   - Optional: LLM-assisted redundancy/trust scoring (`--llm`)
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
- Pipelines: IN PROGRESS (pipelines/video_pipeline.py; optional UI orchestrator per ORCHESTRACTION-INTERFACE.md)

### Definitions of Done (per stage)

- Ingestion: ≥10 docs in `raw_videos` with transcripts or placeholders.
- Clean: `cleaned_transcripts` exists for all ingested videos.
- Enrich: segments with tags/entities/code for all cleaned videos.
- Chunk+Embed: `video_chunks` populated, vector index returns results for a probe.
- RAG: Answers include citations; `memory_logs` entries stored.
- UI: End-to-end demo flows run from sidebar filters.

Notes: For small datasets, answers may look similar across queries; increase Top‑K, tweak weights, or expand the seed set.

### Commands (quick reference)

- Install deps: `pip install -r Mongo_Hack/requirements.txt`
- Ingest playlist: `python Mongo_Hack/app/stages/ingest.py --playlist_id <ID> --max 10`
- Ingest channel: `python Mongo_Hack/app/stages/ingest.py --channel_id <ID> --max 10`
- Ingest IDs: `python Mongo_Hack/app/stages/ingest.py --video_ids <id1> <id2>`
- Clean (MVP): `python Mongo_Hack/app/stages/clean.py`
- Clean (LLM): `python Mongo_Hack/app/stages/clean.py --llm` (or set `CLEAN_WITH_LLM=1`)
- Enrich: `python Mongo_Hack/app/stages/enrich.py`
  - Optional LLM: `python Mongo_Hack/app/stages/enrich.py --llm` (or set `ENRICH_WITH_LLM=1`)
  - Orchestrator: `python Mongo_Hack/main.py enrich --llm`
- Chunk+Embed: `python Mongo_Hack/app/stages/chunk_embed.py`
  - Optional LLM: `python Mongo_Hack/app/stages/chunk_embed.py --llm` (or set `CHUNK_WITH_LLM=1`)
  - Orchestrator: `python Mongo_Hack/main.py chunk --llm`
  - Rate limit (recommended for demos): `export VOYAGE_RPM=5` (defaults to 20)
- Redundancy: `python Mongo_Hack/app/stages/redundancy.py`
  - Optional LLM: `python Mongo_Hack/app/stages/redundancy.py --llm` (or set `DEDUP_WITH_LLM=1`)
  - Orchestrator: `python Mongo_Hack/main.py redundancy --llm`
- Trust: `python Mongo_Hack/app/stages/trust.py`
  - Optional LLM: `python Mongo_Hack/app/stages/trust.py --llm` (or set `TRUST_WITH_LLM=1`)
  - Orchestrator: `python Mongo_Hack/main.py trust --llm`
- Seed demo (playlist): `python Mongo_Hack/app/stages/seed_demo.py` (edit playlist ID first)
- Run UI: `streamlit run Mongo_Hack/streamlit_app.py`
- Orchestrator: `python Mongo_Hack/main.py <stage>` (see README)
  - Full pipeline example: `python Mongo_Hack/main.py pipeline --playlist_id <ID> --max 5 --llm`
  - Atlas index helper: `Mongo_Hack/scripts/atlas_index_create.sh <PROJECT_ID> <CLUSTER_NAME>`

### Data Contracts (key fields)

- `raw_videos`: video_id, title, channel_id, published_at, duration_seconds, stats{viewCount,likeCount,commentCount}, keywords[], transcript_raw?, transcript_language?, thumbnail_url
- `cleaned_transcripts`: video_id, language?, cleaned_text, paragraphs[{start,end,text}]
- `enriched_transcripts`: video_id, segments[{start,end,text,tags[],entities[],keyphrases[],code_blocks[],difficulty?}]
- `video_chunks`: video_id, chunk_id, text, metadata{start_ms?,end_ms?,tags[],speakers?,visuals?,keywords[]}, embedding[], embedding_model, embedding_dim
- `memory_logs`: query, retrieved[{video_id,chunk_id,score}], answer, created_at

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

### Next Up (active)

- Schema: validate Atlas Vector index is READY for current cluster.
- QA & Demo Checklist:
  - Run `python Mongo_Hack/health_check.py` (env/DB/collections/embedding).
  - Run `python Mongo_Hack/main.py pipeline --playlist_id <ID> --max 5 --llm`.
  - Open UI and test Q&A (topic/channel/age/trust filters), Compare, Unique, Summaries, Memory.
  - Review `docs/ORCHESTRACTION-INTERFACE.md` for orchestrator-driven demo flow.
  - Assess answer quality; tune `RAG_WEIGHT_*` via env; consider expanding the seed set for more diverse answers.
  - Capture screenshots and rehearse `docs/DEMO.md` sequence.
