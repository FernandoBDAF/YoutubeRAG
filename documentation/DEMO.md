## Demo & Testing Guide (7–8 minutes)

This walks you through a clean run on a small playlist, validating each stage and the UI.

### 0) Prereqs

- Atlas Cluster + Vector Search enabled; user with read/write
- Env vars set (can use `.env`): `MONGODB_URI`, `MONGODB_DB=mongo_hack`, `VOYAGE_API_KEY`, optional `OPENAI_API_KEY`, optional `YOUTUBE_API_KEY`
- Python deps installed: `pip install -r Mongo_Hack/requirements.txt`

### 1) Health check (1 min)

```bash
python Mongo_Hack/health_check.py
```

Confirms env, DB connectivity, base collections, a sample embedding dimension, and probes the Atlas vector index `embedding_index`.

### 2) Seed a tiny dataset (2–3 min)

Default playlist baked in: `PLdlA6gN07G8dyQs86ebumuNiiqcyfXb8f` (max 5 videos). Adjust if needed.

```bash
python Mongo_Hack/app/stages/seed_demo.py
```

What runs:

- Ingest (playlist) → `raw_videos`
- Clean → `cleaned_transcripts`
- Enrich → `enriched_transcripts`
- Chunk+Embed → `video_chunks`
- Redundancy → flags
- Trust → scores

### 3) Validate data quickly (30s)

Open MongoDB Atlas or CLI and spot-check:

- `raw_videos` count > 0
- `video_chunks` contains vectors and metadata (tags, channel_id, age_days)

### 4) UI run (3–4 min)

```bash
streamlit run Mongo_Hack/streamlit_app.py
```

Try the tabs:

- KPIs: verify counts for raw_videos, video_chunks, feedback; click Refresh after pipeline.
- Explore: run Mongo searches on raw_videos (title/desc/channel/transcript) and chunks (tags/trust/redundancy), export CSV.
- Vector Search: run semantic-only search (no LLM) to show scores and filters.
- Q&A: enter a topic (e.g., "react"), set Top-k (8), try Popular Topics, Exclude redundant, download answer & context. Adjust Vector/Trust/Recency weights. Enable streaming. Use “Use Hybrid Retrieval for Q&A” to compare answers.
  - (Optional) Toggle “Reweight by persona/feedback” to bias results toward your persona interests and top feedback tags; adjust Reweight alpha.
- Compare: enter two channel IDs from the seeded set; inspect consensus/unique, tables, and exports
- Unique: list filtered non-redundant chunks; download CSV/Markdown; inspect Top Tags & Trust histogram
- Summaries: build context for a topic; (optionally) generate LLM Markdown summary; save & view saved summaries
- Memory: view recent queries & citations; logs now include retrieval mode, weights, and session_id.
- Retrieval Lab: run the same query side-by-side across Keyword, Vector, Hybrid, and Structured; inspect per-mode scores and export CSV.

Controller tab: run individual stages or full pipeline with LLM toggles; pass IDs inline. After Ingest, click "Run Full Pipeline for Last Ingest Args".

### 5) Personalization & Feedback (1 min)

- In Q&A → Session: Load a recent query; defaults for topic/channel carry between runs in this session.
- Provide feedback on the first cited video/chunk. The “Your feedback so far” panel shows counts/averages and top tags.
- Controller → Persona & Session: Save preset (persona + interests + preferred channels); Apply from interactions to infer interests from recent queries + feedback.
  - Switch persona (Academic ↔ Job Seeker) or session id and re-run Q&A to demonstrate different rankings for the same query.

### 6) Ingest from UI and run pipeline

- Controller: run Ingest with playlist/channel/ids.
- Then click "Run Full Pipeline for Last Ingest Args".

### 7) Orchestrator CLI (optional)

```bash
python Mongo_Hack/main.py pipeline --playlist_id PLdlA6gN07G8dyQs86ebumuNiiqcyfXb8f --max 5 --llm
```

### 8) Troubleshooting

- Health check fails on vector index: create via README Atlas CLI snippet or `scripts/atlas_index_create.sh <PROJECT_ID> <CLUSTER_NAME>`
- No embeddings: verify `VOYAGE_API_KEY`
- 429 Too Many Requests: set `VOYAGE_RPM=5` (or lower), retry chunk step
- Empty UI results: confirm `video_chunks` populated; try higher Top-k; remove filters
- LLM disabled: summaries/answers will show context-only fallbacks

### 9) Next steps for the demo

- Capture screenshots of each UI tab with citations visible
- Rehearse a question → answer → references flow
- Optional: run with LLM toggles to compare outputs

### Per‑tab Quick Guide

- KPIs: quick counts (raw_videos, video_chunks, feedback); use to confirm data after runs.
- Explore: query raw_videos/video_chunks by regex filters; export CSV for inspection.
- Vector Search: semantic search via `$vectorSearch`; shows scores and supports filters.
- Q&A: ask with streaming, adjust weights; optionally Hybrid + Reweight (persona/feedback). Save/Load queries.
- Hybrid Search: keyword + vector in one; shows `search_score` and per-operator scores; CSV export.
- Retrieval Lab: compare Keyword/Vector/Hybrid/Structured side-by-side for the same query.
- Compare: show channel comparisons (consensus/unique tags), tables, and exports.
- Unique: list non-redundant chunks; Top Tags and Trust histogram; CSV/Markdown export.
- Summaries: build context and optionally LLM Markdown summary; save/view saved summaries.
- Memory: recent queries, answers, and citations; includes retrieval mode/weights/session_id.
- Controller: run stages/pipeline, set args, toggle LLM; includes persona & session tools.
- Persona & Session: choose persona, switch session id, save preset, apply from interactions.

### Managing Profiles (user_profiles)

- Use Controller → Persona & Session to select a persona, switch sessions, and manage presets.
- Save preset persists persona, interests, channels, and defaults tied to the current session_id.
- Apply from interactions infers interests from recent queries and feedback tags.
