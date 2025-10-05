## Demo Script (7–8 minutes)

1. Problem & North Star (30s)

- Info overload in dev-education videos; need persistent, adaptive context.
- Goal: ingest → enrich → embed → retrieve → answer with citations.

2. Architecture (45s)

- Show README diagram: agents and memory layers in MongoDB.
- Atlas Vector Search + Voyage embeddings; Streamlit UI for demo.

3. Seed (60s)

```bash
python Mongo_Hack/seed_demo.py  # edit playlist ID first
```

- Briefly mention collections created and vector index.

4. Ingestion & Clean (LLM optional) (60s)

```bash
python Mongo_Hack/ingest.py --playlist_id <ID> --max 5
python Mongo_Hack/clean.py --llm  # or without --llm
```

- Show a `raw_videos` doc and a `cleaned_transcripts` doc.

5. Enrich → Chunk+Embed (60s)

```bash
python Mongo_Hack/enrich.py
python Mongo_Hack/chunk_embed.py
```

- Show `enriched_transcripts` (tags/code) and `video_chunks` with embeddings.

6. Redundancy + Trust (45s)

```bash
python Mongo_Hack/redundancy.py
python Mongo_Hack/trust.py
```

- Explain redundancy flags and trust scoring.

7. RAG + UI (3–4 min)

```bash
streamlit run Mongo_Hack/streamlit_app.py
```

- Q&A tab: ask “React state best practices”, show answer + citations.
- Compare tab: two channels; show consensus/unique tags, export metrics.
- Unique tab: non-redundant snippets for a topic.
- Summaries tab: build topic context preview.
- Memory tab: show recent queries and citations.

8. Close (30s)

- Persistent memory, explainable retrieval, modular agents.
- Next steps: better diarization, richer trust, dataset expansion.
