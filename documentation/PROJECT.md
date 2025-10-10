## 🧱 Technical Architecture (Hackathon-scale)

### 1. Data Ingestion Agent

- Uses YouTube API to fetch:
  - metadata (title, channel, publish date, stats, category)
  - transcript (via youtube-transcript-api)
  - thumbnail URL
- Adds derived fields: duration, keywords, engagement score.
- Inserts raw → `mongodb.collection("raw_videos")`.

### 2. Processing / Enrichment Agents

Each step writes to a new collection (demonstrating “context engineering via structured memory”).

| Agent              | Function                                                                                                                              | MongoDB Collection   |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| TranscriptCleaner  | Fix punctuation, remove disfluencies, paragraphize using an LLM (Voyage AI embeddings optional for semantic segmentation).            | cleaned_transcripts  |
| SpeakerTagger      | Basic diarization heuristic + LLM inference for speaker roles.                                                                        | enriched_transcripts |
| VisualAnnotator    | Uses Voyage AI Vision or GPT-4 Vision on key frames → adds [visual_context] text snippets.                                            | multimodal_segments  |
| Chunker + Embedder | Splits into semantic chunks (~500 tokens) → creates embeddings with Voyage AI API → stores vectors + metadata in Atlas Vector Search. | video_chunks         |

### 3. Retrieval + Generation Agent (RAG Core)

- Query embedding → Atlas Vector Search → retrieve top-k chunks.
- Compose contextual prompt (system + retrieved content).
- Generate response with LLM (GPT-4 / Voyage LLM).
- Optionally: store query + retrieved chunks + answer back to `memory_logs` for the agent’s long-term memory.

### 4. Interface Layer

Streamlit dashboard showing:

- Filters: channel / topic / date
- Context map: embedding clusters (UMAP)
- Interactive Q&A panel
- “Memory growth” timeline (how context expands as new videos are added)

### ☁️ Hackathon-Relevant Stack

| Component         | Tech                        | Why it fits “Context Engineering”               |
| ----------------- | --------------------------- | ----------------------------------------------- |
| Persistent memory | MongoDB Atlas Vector Search | Stores long-term semantic memory for agents.    |
| Embeddings        | Voyage AI Embeddings API    | High-quality, compact context representation.   |
| LLM reasoning     | OpenAI / Voyage LLM         | Adaptive agent that learns from stored context. |
| Data ingestion    | YouTube API + Python agents | Demonstrates real-world dynamic data sources.   |
| Visualization     | Streamlit + Plotly          | Shows how context evolves and is retrieved.     |

### 🧠 Why It’s a Strong Hackathon Fit

- Directly addresses “persistent, adaptive agents.”
- Shows how to capture, store, and recall large external knowledge (YouTube videos).
- Demonstrates context engineering.
- Multiple structured memory layers inside MongoDB: raw → cleaned → enriched → embedded.
- Uses official hackathon partners (Atlas Vector Search + Voyage AI embeddings).
- Visually engaging: Streamlit UI shows context recall and memory expansion.
- Expandable: Same architecture can index podcasts, meetings, or enterprise knowledge.

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

### 📄 Deliverables

- `main.py` – orchestrator (agent pipeline)
- `agents/` – each stage class (cleaner, diarizer, chunker, retriever)
- `streamlit_app.py` – interactive demo
- `mongodb_schema.json` – collections + vector index config
- `README.md` – problem → solution → tech → demo steps
