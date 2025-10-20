## Mongo Hack — Persistent Context RAG on YouTube

An independent, self-contained prototype that ingests YouTube videos and builds persistent, layered context in MongoDB. Agents clean and enrich transcripts, add visual context, chunk content, and embed it into Atlas Vector Search. A simple UI and retriever generate context-aware answers while logging interactions for long-term memory.

### Architecture Diagram

```mermaid
flowchart TD
  Y[YouTube API] --> I[Ingestion Agent]
  I --> RV[(raw_videos)]
  I -->|transcript| TC[TranscriptCleaner]
  TC --> CT[(cleaned_transcripts)]
  TC --> ST[SpeakerTagger]
  ST --> ET[(enriched_transcripts)]
  I --> VA[VisualAnnotator]
  VA --> MS[(multimodal_segments)]
  TC --> C[Chunk]
  C --> E1[Enrich (per-chunk)]
  E1 --> EB[Embed]
  EB --> VC[(video_chunks + embeddings)]

  Q[User Query] --> RET[Retriever + Generator]
  RET <--> VS[(Atlas Vector Search)]
  VS --> VC
  RET --> ML[(memory_logs)]
  UI[Streamlit UI] --> RET
  UI --> VS
```

### Collections Overview

- raw_videos: raw metadata, transcript, thumbnails, derived stats.
- cleaned_transcripts: LLM-cleaned transcript text + paragraphs.
- enriched_transcripts: diarization and speaker role inference.
- multimodal_segments: vision-derived context for key frames.
- video_chunks: per-chunk schema (chunk_text, summary, annotations, embedding).
- memory_logs: query, retrieved context, and generated answer.

### Getting Started

### Documentation Map (who should read what)

| Audience        | Start Here            | Deep Dive                          | Operations                  |
| --------------- | --------------------- | ---------------------------------- | --------------------------- |
| Reviewer / Demo | DEMO.md               | HYBRID-RETRIEVAL.md                | EXECUTION.md                |
| Developer       | TECHNICAL-CONCEPTS.md | HYBRID-RETRIEVAL.md, REDUNDANCY.md | EXECUTION.md                |
| Prompt/Agents   | PROMPTS.md            | —                                  | ORCHESTRACTION-INTERFACE.md |

### Run the Demo

1. Ensure Atlas index is READY: `python Mongo_Hack/main.py wait_index`
2. Run the UI: `streamlit run Mongo_Hack/streamlit_app.py`
3. Follow `documentation/DEMO.md` for a 7–8 minute walkthrough (Q&A streaming, Hybrid Search with per-operator scores & CSV, feedback loop, personalization, and optional offline mode).

4. Create MongoDB Atlas project and a database user.
5. Apply `mongodb_schema.json` (collections, indexes, vector index):
   - Atlas UI → Database → Collections → Create collections and indexes.
   - Or use Atlas CLI/API for index creation (see inline index JSON in schema file).
6. Configure environment variables (example):
   - MONGODB_URI
   - MONGODB_DB=mongo_hack
   - VOYAGE_API_KEY (for embeddings)
   - OPENAI_API_KEY (optional, for LLM)
   - YOUTUBE_API_KEY (optional, for metadata)

### Folder Layout (self-contained)

```
Mongo_Hack/
  README.md
  mongodb_schema.json
  docs/
    PROJECT.md
    USE-CASE.md
    PROMPTS.md
    EXECUTION.md
    DEMO.md
    ORCHESTRACTION-INTERFACE.md
  agents/
  app/
    stages/
    services/
      filters.py          # shared filter builder for Mongo/Atlas
      ui_utils.py         # shared table/CSV helpers
      persona_utils.py    # infer top tags from feedback
      generation.py       # LLM answer helpers (non-UI)
      retrieval.py        # vector/hybrid/keyword/structured + rerank
    ui/
      tabs/               # split Streamlit tabs (in progress)
  core/
    enrich_utils.py       # enrich text packing/normalization helpers
  pipelines/
  config/
  scripts/
  main.py
  streamlit_app.py
```

### Notes

- This folder is standalone and does not depend on code outside `Mongo_Hack/`.
- The schema targets Atlas Vector Search with cosine similarity and 1024-dim embeddings.
- Replace API keys and dimensions if you use a different embedding model.
- See `ORCHESTRACTION-INTERFACE.md` for the Streamlit-controlled orchestration design.

### What's New (Oct 2025)

- Redundancy improvements: fixed `duplicate_of`, canonical primary selection, adjacency guard with non-adjacent fallback and high-confidence override, `redundancy_method`/`redundancy_reason` fields. See `documentation/REDUNDANCY.md`.
- Trust docs: added trust overview and linkage to redundancy; clarified auto-LLM triggers. See `documentation/REDUNDANCY.md`.
- Chunk hygiene: strip stage cues prior to embedding; persist `display_text` for UI clarity.
- Env updates: new `DEDUP_*` and `TRUST_*` flags in `env.example`.
- Concepts guide: `documentation/TECHNICAL-CONCEPTS.md` explains embeddings, hybrid retrieval, chunking, concurrency, and recommended presets.
- Deep dive: `documentation/HYBRID-RETRIEVAL.md` covers Hybrid Search, hashing fallback, bulk upserts, and `wait_index` for Atlas readiness.

### Pipeline runner (typed configs)

The new pipeline supports sequential execution of stages with explicit, typed configuration objects. Each stage has a Config dataclass with defaults. The runner orchestrates them and supports per-stage IO overrides (separate read/write DBs and collections) and a simple policy to stop or continue on errors.

Example (clean → chunk → enrich) with cross‑DB IO:

```python
from app.pipelines.base_pipeline import StageSpec, PipelineRunner
from app.stages.clean import CleanConfig
from app.stages.chunk import ChunkConfig
from app.stages.enrich import EnrichConfig

specs = [
    StageSpec(stage="clean", config=CleanConfig(
        concurrency=8,
        read_db_name="source_db", read_coll="raw_videos",
        write_db_name="work_db", write_coll="cleaned_transcripts",
    )),
    StageSpec(stage="chunk", config=ChunkConfig(
        chunk_strategy="recursive", token_size=800, overlap_pct=0.15,
        read_db_name="work_db", read_coll="cleaned_transcripts",
        write_db_name="work_db", write_coll="video_chunks",
    )),
    StageSpec(stage="enrich", config=EnrichConfig(
        concurrency=8,
        read_db_name="work_db", read_coll="video_chunks",
        write_db_name="work_db", write_coll="video_chunks",
    )),
]

PipelineRunner(specs, stop_on_error=True).run()
```

CLI example: `python Mongo_Hack/app/pipelines/examples/yt_clean_enrich.py`.

Notes:

- Stages still run standalone with CLI/args for backward compatibility.
- Config dataclasses are the source of truth (env/args optional).

### Atlas Vector Index (CLI or auto-seed)

- Auto-seed (recommended): on first run, the app will attempt to create required collections and the vector index from `config/seed/vector_index.json` if Atlas CLI is installed and envs are set.
- Manual CLI:

```bash
# After atlas auth login
atlas clusters search indexes create \
  --projectId <PROJECT_ID> \
  --clusterName <CLUSTER_NAME> \
  --db mongo_hack \
  --collection video_chunks \
  --file Mongo_Hack/config/seed/vector_index.json

# Check status
atlas clusters search indexes list \
  --projectId <PROJECT_ID> \
  --clusterName <CLUSTER_NAME> \
  --db mongo_hack \
  --collection video_chunks
```

### Quickstart

1. Install prerequisites

```
# (Optional) macOS: Atlas CLI for vector index via CLI
brew tap mongodb/brew && brew install mongodb-atlas-cli

# (Optional) create and activate a virtualenv
python3 -m venv .venv
source .venv/bin/activate

# Python dependencies
python3 -m pip install --upgrade pip
pip install -r Mongo_Hack/requirements.txt
```

2. Set environment (create `.env` or export in shell)

```
export MONGODB_URI="<your-atlas-uri>"
export MONGODB_DB="mongo_hack"
export VOYAGE_API_KEY="<voyage-key>"
export OPENAI_API_KEY="<openai-key-optional>"
export YOUTUBE_API_KEY="<youtube-key-optional>"
export VOYAGE_RPM=5  # recommended for demos to avoid 429s
export PROJECT_ID="<your-atlas-project-id>"
export CLUSTER_NAME="<your-atlas-cluster-name>"
```

3. Collections and vector index

- Auto: run any `python Mongo_Hack/main.py ...` command; on first run, it ensures base collections and attempts to create `embedding_index` using Atlas CLI and envs above.
- Manual UI: create DB `mongo_hack`, collections, and a Vector Search index on `video_chunks.embedding` (dims: 1024, similarity: cosine).
- Manual CLI: see section “Atlas Vector Index (CLI or auto-seed)”.

4. Seed a small dataset (edit playlist ID in file)

```
python Mongo_Hack/seed_demo.py
```

5. Run the UI

```
streamlit run Mongo_Hack/streamlit_app.py
```

6. RAG CLI smoke-test (optional)

```
python Mongo_Hack/rag.py
```

7. Health check

```
python Mongo_Hack/health_check.py
```

8. Orchestrator (one entrypoint)

```
python Mongo_Hack/main.py ingest --playlist_id <ID> --max 5 --db_name mongo_hack
python Mongo_Hack/main.py clean --llm --db_name mongo_hack
python Mongo_Hack/main.py enrich --llm --db_name mongo_hack      # or set ENRICH_WITH_LLM=1
python Mongo_Hack/app/stages/chunk.py --db_name mongo_hack
python Mongo_Hack/app/stages/enrich.py --db_name mongo_hack
python Mongo_Hack/app/stages/embed.py --db_name mongo_hack --embed_source chunk
export VOYAGE_RPM=5                         # rate limit embeddings
python Mongo_Hack/main.py redundancy --llm --db_name mongo_hack  # or set REDUNDANCY_WITH_LLM=1
python Mongo_Hack/main.py trust --llm --db_name mongo_hack       # or set TRUST_WITH_LLM=1
python Mongo_Hack/main.py ui
python Mongo_Hack/main.py health
python Mongo_Hack/main.py pipeline --playlist_id <ID> --max 5 --llm
```

### Pipeline runner (typed configs)

See `app/pipelines/examples/yt_clean_enrich.py` for a full example (clean → compress → chunk → enrich → embed) with explicit read/write DBs and typed config objects per stage.

Notes:

- Stages still run standalone with CLI/args for backward compatibility.
- Config dataclasses are the source of truth (env/args optional).

New options overview:

- Clean: filler removal, paragraphization; LLM flags `--llm_retries`, `--llm_backoff_s`, `--llm_qps`, `--model_name`.
- Chunk: `metadata.chunk_index` and `metadata.chunk_count` for ordering.
- Enrich: conceptual relations prompt, confidence levels, `quality_score`, always sets `embedding_text`.
- Embed: hybrid `embedding_text` by default, `vector_norm`, optional multi-vector outputs; flags `--use_hybrid_embedding_text/--no_use_hybrid_embedding_text`, `--unit_normalize_embeddings/--no_unit_normalize_embeddings`, `--emit_multi_vectors`.

Utilities:

```
# Indexes
python Mongo_Hack/scripts/create_indexes.py "$MONGODB_URI"

# Schema validator
python Mongo_Hack/scripts/validate_chunks.py "$MONGODB_URI" mongo_hack video_chunks
```

### Chunking strategies

The chunk stage supports three strategies selectable via `--chunk_strategy` (default: `fixed`).

- Fixed token size with overlap:

  - Uses TokenTextSplitter (tiktoken).
  - Example: `python Mongo_Hack/app/stages/chunk_embed.py --chunk_strategy fixed --token_size 500 --overlap_pct 0.15 --db_name mongo_hack`

- Recursive with overlap:

  - Uses RecursiveCharacterTextSplitter and packs to tokens.
  - Example: `python Mongo_Hack/app/stages/chunk_embed.py --chunk_strategy recursive --token_size 400 --overlap_pct 0.1 --split_chars ".,;"`

- Semantic:
  - Uses SemanticChunker to merge semantically similar sentence groups.
  - Requires embeddings provider (defaults to OpenAI embeddings); set `OPENAI_API_KEY` and optionally `--semantic_model`.
  - Example: `python Mongo_Hack/app/stages/chunk_embed.py --chunk_strategy semantic --token_size 500 --overlap_pct 0.15 --split_chars "." --semantic_model text-embedding-3-small`

Note: All chunk configuration used is stored per chunk under `metadata.chunking` for auditability.

### UI Features

- KPIs metrics bar (counts for raw_videos, video_chunks, feedback)
- Explore tab for Mongo searches (raw_videos, video_chunks) with CSV export
- Vector Search tab (semantic-only) with filters and scores
- Q&A with adjustable retrieval weights and Markdown export; preview feedback alpha
- Compare with consensus/unique metrics, trusted chunk tables, Top Channels summary
- Unique insights table with CSV/Markdown export and mini-dashboards (Top Tags, Trust histogram)
- Summaries with optional LLM Markdown and Saved Summaries viewer
- Controller tab to trigger stages/full pipeline with IDs and LLM toggle

### Demo Flow (suggested)

1. Show KPIs on preloaded DB; Explore Mongo queries.
2. Run a Vector Search (semantic-only) and then Q&A.
3. Provide feedback (video + chunks), re-run query.
4. Ingest from Controller; Run Full Pipeline for last args; refresh KPIs.
5. Click New session in Q&A Session expander to demonstrate no prior feedback.
