## “CourseCopilot”: Summarizing & Filtering Educational YouTube Dev Videos

### Goal

Help developers cut through long courses/playlists by extracting the best parts, ranking trustworthy content, and answering questions with citations.

### Users

- Learner skimming a topic (React, Python, Algorithms)
- Instructor curating reference material

### Architecture (high level)

- Ingest: YouTube API + transcript loader → `raw_videos`
- Clean: readability improvements → `cleaned_transcripts`
- Enrich: tags/entities/keyphrases/code → `enriched_transcripts`
- Chunk+Embed: semantic chunks + Voyage embeddings → `video_chunks` (Atlas Vector Search)
- RAG: query → retrieve → generate answer with citations; store to `memory_logs`
- Feedback: anonymous per-session rating/tags/note on videos/chunks → re-rank and guide answers

### Data model (key fields)

- raw_videos: video_id, title, description, channel_id, published_at, duration_seconds, stats, keywords, transcript_raw, thumbnail_url
- cleaned_transcripts: video_id, cleaned_text, paragraphs?
- enriched_transcripts: video_id, segments[{text, tags[], entities[], keyphrases[], code_blocks[], difficulty?}]
- video_chunks: video_id, chunk_id, text, metadata{tags[], channel_id, age_days}, embedding[], trust_score, is_redundant
- feedback: video_feedback | chunk_feedback: session_id, (video_id|chunk_id), rating 1–5, tags[], note, created_at, updated_at

### Retrieval prompt shape

- System: prefer higher-rated, commonly tagged chunks; avoid low trust and redundant ones
- User: natural question
- Context: top‑k chunks with `feedback_context` (avg_rating, count, top_tags) and trust

### Streamlit UI

- Q&A: query, filters (topic/channel/age/trust), weight sliders (vector/trust/recency), citations, full context download
- Compare: consensus vs unique tags across channels, exports
- Unique: non‑redundant chunks list + dashboards (top tags, trust histogram)
- Summaries: topic context build + optional LLM Markdown summary; save/view
- Memory: recent Q&A logs
- Controller: run stages/pipeline; `SESSION_ID` override for feedback persistence

### Demo script (condensed)

1. Ingest small playlist; show `raw_videos` fields.
2. Run full pipeline; verify `video_chunks` has vectors.
3. Ask a question; show answer + citations.
4. Give feedback on a video and a chunk (rate 5 + tags).
5. Re‑ask; show re‑ranking and note guidance in answer.

### Quality checks

- Citations align with answer content
- Sensitive to tags and ratings
- Stable under small dataset changes

### Stretch ideas

- Instructor packs: auto‑generated lesson outlines with timecodes
- Personalization: per‑session tag preferences
- Multi‑source: blogs/papers mixed with videos
