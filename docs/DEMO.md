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

If Voyage returns 429 (rate limit), set RPM:

```bash
export VOYAGE_RPM=5
python Mongo_Hack/app/stages/chunk_embed.py
python Mongo_Hack/app/stages/redundancy.py
python Mongo_Hack/app/stages/trust.py
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

- Q&A: enter a topic (e.g., "react"), set Top-k (8), try Popular Topics, Exclude redundant, download answer & context
- Compare: enter two channel IDs from the seeded set; inspect consensus/unique, tables, and exports
- Unique: list filtered non-redundant chunks; download CSV/Markdown; inspect Top Tags & Trust histogram
- Summaries: build context for a topic; (optionally) generate LLM Markdown summary; save & view saved summaries
- Memory: view recent queries & citations

Controller tab (optional): run individual stages or full pipeline with LLM toggles; pass IDs inline.

### 5) Orchestrator CLI (optional)

```bash
python Mongo_Hack/main.py pipeline --playlist_id PLdlA6gN07G8dyQs86ebumuNiiqcyfXb8f --max 5 --llm
```

### 6) Troubleshooting

- Health check fails on vector index: create via README Atlas CLI snippet or `scripts/atlas_index_create.sh <PROJECT_ID> <CLUSTER_NAME>`
- No embeddings: verify `VOYAGE_API_KEY`
- 429 Too Many Requests: set `VOYAGE_RPM=5` (or lower), retry chunk step
- Empty UI results: confirm `video_chunks` populated; try higher Top-k; remove filters
- LLM disabled: summaries/answers will show context-only fallbacks

### 7) Next steps for the demo

- Capture screenshots of each UI tab with citations visible
- Rehearse a question → answer → references flow
- Optional: run with LLM toggles to compare outputs
