## 🎛️ Streamlit-Controlled Agentic Flow System

This document describes how the Mongo_Hack project orchestrates the end‑to‑end pipeline via CLI and Streamlit, which env vars control behavior, and how state is persisted and reused.

### Components

- `main.py` Orchestrator: runs individual stages or the full pipeline as subprocesses.
- `app/stages/*.py`: concrete stage scripts for ingest, clean, enrich, chunk+embed, redundancy, trust.
- `streamlit_app.py` UI: tabs for Q&A, Compare, Unique, Summaries, Memory, and a Controller tab to launch stages.

### Pipeline order

1. Ingest → 2) Clean → 3) Enrich → 4) Chunk+Embed → 5) Redundancy → 6) Trust

### CLI usage

```bash
# Full pipeline (example with playlist, 5 items, LLM on)
python Mongo_Hack/main.py pipeline --playlist_id <PLAYLIST_ID> --max 5 --llm

# Individual stages
python Mongo_Hack/main.py ingest --playlist_id <PLAYLIST_ID> --max 10
python Mongo_Hack/main.py clean --llm
python Mongo_Hack/main.py enrich --llm
python Mongo_Hack/main.py chunk --llm
python Mongo_Hack/main.py redundancy --llm
python Mongo_Hack/main.py trust --llm

# Launch UI
streamlit run Mongo_Hack/streamlit_app.py
```

### Controller tab (Streamlit)

- Inputs: playlist/channel/video IDs, LLM toggle, max items.
- Buttons: run any stage or the full pipeline (calls `main.py`).
- Feedback UI: rate videos/chunks 1–5, add tags and notes; stored to `video_feedback`/`chunk_feedback`.

### Collections (state)

- `raw_videos`: metadata + transcript_raw.
- `cleaned_transcripts`: cleaned_text, optional paragraphs.
- `enriched_transcripts`: segments with tags/entities/code.
- `video_chunks`: chunk text, metadata, embedding, trust/redundancy flags.
- `memory_logs`: query, retrieved citations, answer for auditability.
- `video_feedback`, `chunk_feedback`: per-session feedback (rating/tags/note).

### Environment variables

- Core:
  - `MONGODB_URI`, `MONGODB_DB` (default `mongo_hack`)
  - `VOYAGE_API_KEY` (embeddings)
  - `OPENAI_API_KEY` (LLM optional)
  - `YOUTUBE_API_KEY` (ingest metadata)
- Orchestration:
  - `INGEST_UPSERT_EXISTING` (false by default; when true, re‑upserts existing `raw_videos`)
  - `SESSION_ID` (optional; overrides anonymous UI session ID for feedback persistence)
  - `VOYAGE_RPM` (rate limit for embeddings; default 20; e.g., `5` for demos)
  - `RAG_WEIGHT_VECTOR`, `RAG_WEIGHT_TRUST`, `RAG_WEIGHT_RECENCY` (optional tuning)
  - `FEEDBACK_ALPHA` (optional; weight to re-rank by user feedback)
- Atlas CLI seeding (optional):
  - `PROJECT_ID`, `CLUSTER_NAME` (auto‑create vector index via Atlas CLI if available)

### Idempotency & skipping

- Ingest: by default, skips videos already present in `raw_videos`. Set `INGEST_UPSERT_EXISTING=true` to force re‑upsert.
- Downstream stages are naturally idempotent if they overwrite documents by `video_id`/`chunk_id`.

### Error handling & resilience

- Subprocesses use `subprocess.run(..., check=True)` with `PYTHONPATH` set to project root to avoid path issues.
- Clean/Enrich/Chunk can run with or without `--llm`. Heuristic fallbacks ensure progress when LLMs are unavailable.
- Transcript retrieval uses LangChain `YoutubeLoader` with language fallback; ingest falls back to description text in Clean if transcript missing.
- Embedding step includes simple rate limiting via `VOYAGE_RPM`.

### Health & readiness

- `health_check.py` validates env, DB connectivity, required collections, and vector index presence/dimension.
- On `main.py` startup, `ensure_collections_and_indexes` creates base collections and tries to create the Atlas vector index when CLI/envs are available.

### Demo recipe (condensed)

1. Seed 3–5 videos (playlist or channel), run full pipeline with `--llm` if keys set.
2. Open Streamlit → Q&A tab → ask topical question → inspect citations and full retrieval context.
3. Provide feedback on one video + a few chunks; re‑run the same question to see re‑ranking effects (if enabled).
4. Explore Compare/Unique/Summaries tabs and download artifacts (CSV/MD).
