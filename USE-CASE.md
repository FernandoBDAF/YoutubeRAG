## “CourseCopilot”: Summarizing & Filtering Educational YouTube Dev Videos

### 0) Goal (hackathon-ready)

Build a small but convincing system that ingests dev-education YouTube videos (e.g., Python/React tutorials), cleans & enriches transcripts, embeds chunks with Voyage AI, stores in MongoDB Atlas Vector Search, and lets users ask:

- “Summarize this 12-part series into a cheat-sheet.”
- “Compare how 3 channels teach React state.”
- “Show only unique tips not repeated across channels.”

The demo should prove context engineering: capture → structure → embed → retrieve → compose → reuse memory.

### 1) Architecture (minimal, modular)

Services/Agents

- IngestAgent → YouTube API: metadata + transcript → raw_videos
- CleanAgent → punctuation, disfluency removal → cleaned_transcripts
- EnrichAgent → topic tags, keyphrases, code-block detection, simple speaker turns → enriched_transcripts
- ChunkEmbedAgent → semantic chunking + Voyage embeddings → video_chunks (with Atlas vector index)
- SummarizerAgent → hierarchical summaries (per-video → per-playlist/channel → cross-channel)
- DeduplicateAgent → near-duplicate chunk detection (cosine sim threshold) → mark is_redundant
- TrustRankAgent → basic trust signals (cross-source consensus, recency, engagement, code-lint pass) → trust_score
- RAGAgent → retrieval + answer/synopsis/cheat-sheet generation
- UI → Streamlit app

### 2) Data model (MongoDB)

raw_videos

```jsonc
{
  "video_id": "yt123",
  "channel_id": "chanA",
  "title": "React State in Depth",
  "description": "...",
  "published_at": "2024-05-01T12:00:00Z",
  "duration_sec": 1830,
  "stats": { "views": 120345, "likes": 5200, "comments": 340 },
  "playlist_id": "PL_react_course_2024",
  "transcript_raw": "... full text or array of (start, text) ...",
  "language": "en",
  "topics_hint": ["react", "state", "hooks"],
  "fetched_at": "2025-10-04T22:00:00Z"
}
```

cleaned_transcripts

```json
{
  "video_id": "yt123",
  "paragraphs": [
    { "start": 12.4, "end": 28.7, "text": "Let's define state..." }
  ],
  "quality": { "auto_punctuated": true, "disfluencies_removed": true }
}
```

enriched_transcripts

```json
{
  "video_id": "yt123",
  "segments": [
    {
      "start": 82.1,
      "end": 145.0,
      "text": "Use useState for local state...",
      "tags": ["react", "useState", "beginner"],
      "code_blocks": [
        { "lang": "jsx", "code": "const [count, setCount] = useState(0)" }
      ],
      "speaker": "Speaker A"
    }
  ],
  "entities": ["React", "useState"],
  "keyphrases": ["local component state", "hooks vs classes"]
}
```

video_chunks (vectorized)

```jsonc
{
  "video_id": "yt123",
  "chunk_id": "yt123:0007",
  "text": "When to use useReducer vs useState...",
  "meta": {
    "channel_id": "chanA",
    "title": "React State in Depth",
    "published_at": "2024-05-01T12:00:00Z",
    "playlist_id": "PL_react_course_2024",
    "tags": ["react", "useReducer"],
    "code_present": true
  },
  "embedding": [
    /* voyage vector */
  ],
  "is_redundant": false,
  "trust_score": 0.67
}
```

Atlas Vector Index (example)

```json
{
  "mappings": {
    "dynamic": true,
    "fields": {
      "embedding": {
        "type": "knnVector",
        "dimensions": 1024,
        "similarity": "cosine"
      },
      "meta.tags": { "type": "string" },
      "meta.channel_id": { "type": "string" },
      "meta.published_at": { "type": "date" }
    }
  }
}
```

### 3) Pipelines (agent steps)

#### A) Ingestion

- Input: channel/playlist IDs
- Actions: call YouTube API → store metadata + raw transcript
- Output: raw_videos

#### B) Clean

- Prompt LLM: “Fix punctuation/casing, remove disfluencies, keep code intact, preserve timestamps boundaries.”
- Output: cleaned_transcripts

#### C) Enrich

Heuristics + LLM:

- Topic tagging (regex + LLM confirm)
- Keyphrase extraction (YAKE/KeyBERT + LLM refine)
- Code block detection (triple-backticks; fenced code; simple lexers)
- Speaker turns (optional): LLM infers turn boundaries for interviews
- Output: enriched_transcripts

#### D) Chunk + Embed

- Chunking: semantic (heading/segment/timestamp aware), target ~500 tokens, 50-token overlap
- Embeddings: Voyage AI; store vector + rich metadata in video_chunks, build Atlas vector index

#### E) Redundancy detector

- For each new chunk: search top-k similar existing chunks (same topic/channel/time window)
- If max cosine ≥ 0.92 → mark is_redundant=true (keep pointer to canonical)

#### F) TrustRank (lightweight, hackathon-friendly)

- trust_score = w1*consensus + w2*recency + w3*engagement_norm + w4*code_validity
- Consensus: proportion of distinct channels with semantically similar chunks (≥0.85) on same claim
- Recency: sigmoid on age days
- Engagement_norm: likes/views z-score within channel
- Code_validity: quick lint/compile pass success (when code_present), e.g., node --check or python -m pyflakes

#### G) Summarization (hierarchical)

- Per-video: map-reduce summarization over chunks → “key takeaways” + “code snippets” + “pitfalls”
- Per-playlist/course: summarize per-video summaries → “module overview”
- Cross-channel: RAG over all relevant chunks → fused summary with “consensus vs unique insights”

#### H) RAG Answering

- Query → embed → Atlas search (filters: topic/channel/date, exclude redundant)
- Re-rank by trust_score & recency
- Compose prompt (instructions + citations + contrastive ask)
- Generate: Cheat-sheet, Compare channels, Step-by-step plan, Reading list

### 4) Retrieval prompt shapes (ready to use)

Cheat-sheet (course series)

```text
System: You are CourseCopilot. Produce concise, accurate cheat-sheets from transcripts. Preserve code; include citations (video_id:chunk_id). Avoid speculation.

User:
Topic: React state management
Scope filter: playlist_id=PL_react_course_2024

Deliverables:
- Core concepts (bulleted)
- Decision guide (useState vs useReducer vs context)
- Common pitfalls
- Code snippets (minimal)
- References (video:timestamp)
```

Cross-channel comparison

```text
User: Compare how ChanA, ChanB, ChanC teach React forms. Summarize consensus; list unique tips per channel; flag contradictions; include citations.
```

Unique insights only

```text
User: From all React Router videos in 2024, list non-redundant tips (exclude concepts that appear in ≥2 channels).
```

### 5) Streamlit UI (MVP)

Left sidebar

- Filters: Topic (multiselect), Channels, Playlist, Date range, TrustScore min, Include code only ✔️
- Mode tabs: Cheat-Sheet, Compare, Unique Insights, Explorer

Main

- Cheat-Sheet: generated sections + collapsible code blocks + citations (click → show chunk text)
- Compare: 3-column cards per channel (consensus ribbon at top; unique tips section)
- Unique Insights: table with tip, channel, timestamp, trust_score
- Explorer:
  - UMAP scatter (chunks) with color=channel, shape=topic (hover shows snippet)
  - Topic timeline (stacked area per week)
  - Redundancy heatmap (channel × channel)

### 6) Embedding & vector search (Python sketches)

```python
# Embeddings (Voyage)
import requests, os
def embed_texts(texts):
    r = requests.post(
        "https://api.voyageai.com/embeddings",
        headers={"Authorization": f"Bearer {os.getenv('VOYAGE_API_KEY')}"},
        json={"model": "voyage-2", "input": texts}
    )
    return [v["embedding"] for v in r.json()["data"]]
```

```python
# Atlas Vector Search query (PyMongo example)
from pymongo import MongoClient
import os
client = MongoClient(os.getenv("MONGODB_URI"))
col = client.db.video_chunks

def search_chunks(query_vec, k=8, filters=None):
    pipeline = [
      {"$vectorSearch": {
         "index": "video_chunks_vec",
         "path": "embedding",
         "queryVector": query_vec,
         "numCandidates": 200,
         "limit": k,
         "filter": filters or {}
      }},
      {"$project": {"text":1, "meta":1, "score": {"$meta": "vectorSearchScore"}, "trust_score":1}}
    ]
    return list(col.aggregate(pipeline))
```

### 7) Context-engineering choices (why they matter)

- Hierarchical memory: raw → cleaned → enriched → chunked → summarized (agents can choose the right layer)
- Rich metadata: channel, playlist, topic, code_present → powerful retrieval filters
- Redundancy flag: prevents flooding the LLM with the “same” lesson across channels
- TrustScore: pragmatic, explainable ranking (consensus + recency + engagement + code validity)
- Chunk design: semantic, overlap, code-aware → better recall and fewer cut-off snippets
- Composed prompts: different templates per task (cheat-sheet vs compare vs unique)

### 8) Demo script (7–8 minutes)

1. Problem: info overload; repetitive tutorials; hard to compare teachings.
2. Ingest: pick a 5–12 video playlist; show raw_videos doc.
3. Pipeline: quick animation of agents; show video_chunks with embeddings.
4. Atlas: show vector index + a sample vector search from MongoDB UI.
5. Cheat-sheet: run query → live summary with citations & code.
6. Compare: pick 3 channels → consensus vs unique tips table.
7. Unique insights: show results excluding redundant chunks.
8. Memory: re-ask a follow-up; show retrieval logs; emphasize persistent adaptive memory.

### 9) Milestones (hackathon cadence)

- Day 1 (AM): Repo scaffolding, Atlas cluster + index, Voyage key; IngestAgent done
- Day 1 (PM): CleanAgent, EnrichAgent (tags, code detect), ChunkEmbedAgent, first embeddings
- Day 2 (AM): Redundancy + TrustRank; SummarizerAgent (per-video, per-playlist)
- Day 2 (PM): Streamlit MVP (Cheat-sheet & Compare), polish prompts, demo script, 2–3 curated datasets

### 10) Quality checks / evaluation (fast, practical)

- Groundedness: all answers include citations (video_id:chunk_id + timestamp)
- Coverage: % playlist videos referenced in cheat-sheet
- Redundancy reduction: unique-insight view excludes ≥80% of dup chunks
- Trust sanity: higher trust_score correlates with multi-channel consensus
- Latency: end-to-end query < 3s on small dataset (tune k, caching)

### 11) Stretch features (time-permitting)

- Code verifiers: run snippets in sandbox; auto-fix minimal errors for display
- “Compare pedagogy”: readability level, pace, exercises presence
- Learner mode: export cheat-sheet to Markdown/PDF; spaced-repetition Q&A from chunks
- Instructor mode: “what have I already taught?” planner for next videos

### 12) README skeleton (for the repo)

- What & Why (problem, hackathon theme alignment)
- Stack (MongoDB Atlas Vector Search, Voyage embeddings, Streamlit, Python)
- Setup: env vars, Atlas index JSON, seed script for 1–2 playlists
- Run: python ingest.py, python pipeline.py, streamlit run app.py
- Demo commands: preset queries for cheat-sheet / compare / unique
- Notes: limits, future work, safety & licensing of transcripts

“CourseCopilot”: Summarizing & Filtering Educational YouTube Dev Videos 0) Goal (hackathon-ready)

Build a small but convincing system that ingests dev-education YouTube videos (e.g., Python/React tutorials), cleans & enriches transcripts, embeds chunks with Voyage AI, stores in MongoDB Atlas Vector Search, and lets users ask:

“Summarize this 12-part series into a cheat-sheet.”

“Compare how 3 channels teach React state.”

“Show only unique tips not repeated across channels.”

The demo should prove context engineering: capture → structure → embed → retrieve → compose → reuse memory.

1. Architecture (minimal, modular)

Services/Agents

IngestAgent → YouTube API: metadata + transcript → raw_videos

CleanAgent → punctuation, disfluency removal → cleaned_transcripts

EnrichAgent → topic tags, keyphrases, code-block detection, simple speaker turns → enriched_transcripts

ChunkEmbedAgent → semantic chunking + Voyage embeddings → video_chunks (with Atlas vector index)

SummarizerAgent → hierarchical summaries (per-video → per-playlist/channel → cross-channel)

DeduplicateAgent → near-duplicate chunk detection (cosine sim threshold) → mark is_redundant

TrustRankAgent → basic trust signals (cross-source consensus, recency, engagement, code-lint pass) → trust_score

RAGAgent → retrieval + answer/synopsis/cheat-sheet generation

UI → Streamlit app

2. Data model (MongoDB)
   raw_videos
   {
   "video_id": "yt123",
   "channel_id": "chanA",
   "title": "React State in Depth",
   "description": "...",
   "published_at": "2024-05-01T12:00:00Z",
   "duration_sec": 1830,
   "stats": { "views": 120345, "likes": 5200, "comments": 340 },
   "playlist_id": "PL_react_course_2024",
   "transcript_raw": "... full text or array of (start, text) ...",
   "language": "en",
   "topics_hint": ["react", "state", "hooks"],
   "fetched_at": "2025-10-04T22:00:00Z"
   }

cleaned_transcripts
{
"video_id": "yt123",
"paragraphs": [
{ "start": 12.4, "end": 28.7, "text": "Let's define state..." }
],
"quality": { "auto_punctuated": true, "disfluencies_removed": true }
}

enriched_transcripts
{
"video_id": "yt123",
"segments": [
{
"start": 82.1,
"end": 145.0,
"text": "Use useState for local state...",
"tags": ["react", "useState", "beginner"],
"code_blocks": [
{ "lang": "jsx", "code": "const [count, setCount] = useState(0)" }
],
"speaker": "Speaker A"
}
],
"entities": ["React", "useState"],
"keyphrases": ["local component state", "hooks vs classes"]
}

video_chunks (vectorized)
{
"video_id": "yt123",
"chunk_id": "yt123:0007",
"text": "When to use useReducer vs useState...",
"meta": {
"channel_id": "chanA",
"title": "React State in Depth",
"published_at": "2024-05-01T12:00:00Z",
"playlist_id": "PL_react_course_2024",
"tags": ["react", "useReducer"],
"code_present": true
},
"embedding": [/* voyage vector */],
"is_redundant": false,
"trust_score": 0.67
}

Atlas Vector Index (example)

{
"mappings": {
"dynamic": true,
"fields": {
"embedding": { "type": "knnVector", "dimensions": 1024, "similarity": "cosine" },
"meta.tags": { "type": "string" },
"meta.channel_id": { "type": "string" },
"meta.published_at": { "type": "date" }
}
}
}

3. Pipelines (agent steps)
   A) Ingestion

Input: channel/playlist IDs

Actions: call YouTube API → store metadata + raw transcript

Output: raw_videos

B) Clean

Prompt LLM: “Fix punctuation/casing, remove disfluencies, keep code intact, preserve timestamps boundaries.”

Output: cleaned_transcripts

C) Enrich

Heuristics + LLM:

Topic tagging (regex + LLM confirm)

Keyphrase extraction (YAKE/KeyBERT + LLM refine)

Code block detection (triple-backticks; fenced code; simple lexers)

Speaker turns (optional): LLM infers turn boundaries for interviews

Output: enriched_transcripts

D) Chunk + Embed

Chunking: semantic (heading/segment/timestamp aware), target ~500 tokens, 50-token overlap

Embeddings: Voyage AI; store vector + rich metadata in video_chunks, build Atlas vector index

E) Redundancy detector

For each new chunk: search top-k similar existing chunks (same topic/channel/time window)

If max cosine ≥ 0.92 → mark is_redundant=true (keep pointer to canonical)

F) TrustRank (lightweight, hackathon-friendly)

trust_score = w1*consensus + w2*recency + w3*engagement_norm + w4*code_validity

Consensus: proportion of distinct channels with semantically similar chunks (≥0.85) on same claim

Recency: sigmoid on age days

Engagement_norm: likes/views z-score within channel

Code_validity: quick lint/compile pass success (when code_present), e.g., node --check or python -m pyflakes

G) Summarization (hierarchical)

Per-video: map-reduce summarization over chunks → “key takeaways” + “code snippets” + “pitfalls”

Per-playlist/course: summarize per-video summaries → “module overview”

Cross-channel: RAG over all relevant chunks → fused summary with “consensus vs unique insights”

H) RAG Answering

Query → embed → Atlas search (filters: topic/channel/date, exclude redundant)

Re-rank by trust_score & recency

Compose prompt (instructions + citations + contrastive ask)

Generate: Cheat-sheet, Compare channels, Step-by-step plan, Reading list

4. Retrieval prompt shapes (ready to use)
   Cheat-sheet (course series)

System: “You are CourseCopilot. Produce concise, accurate cheat-sheets from transcripts. Preserve code; include citations (video_id:chunk_id). Avoid speculation.”
User:

Topic: React state management

Scope filter: playlist_id=PL_react_course_2024

Deliverables:

Core concepts (bulleted)

Decision guide (useState vs useReducer vs context)

Common pitfalls

Code snippets (minimal)

References (video:timestamp)

Cross-channel comparison

User: “Compare how ChanA, ChanB, ChanC teach React forms. Summarize consensus; list unique tips per channel; flag contradictions; include citations.”

Unique insights only

User: “From all React Router videos in 2024, list non-redundant tips (exclude concepts that appear in ≥2 channels).”

5. Streamlit UI (MVP)

Left sidebar

Filters: Topic (multiselect), Channels, Playlist, Date range, TrustScore min, Include code only ✔️

Mode tabs: Cheat-Sheet, Compare, Unique Insights, Explorer

Main

Cheat-Sheet: generated sections + collapsible code blocks + citations (click → show chunk text)

Compare: 3-column cards per channel (consensus ribbon at top; unique tips section)

Unique Insights: table with tip, channel, timestamp, trust_score

Explorer:

UMAP scatter (chunks) with color=channel, shape=topic (hover shows snippet)

Topic timeline (stacked area per week)

Redundancy heatmap (channel × channel)

6. Embedding & vector search (Python sketches)

# Embeddings (Voyage)

import requests, os
def embed_texts(texts):
r = requests.post(
"https://api.voyageai.com/embeddings",
headers={"Authorization": f"Bearer {os.getenv('VOYAGE_API_KEY')}"},
json={"model": "voyage-2", "input": texts}
)
return [v["embedding"] for v in r.json()["data"]]

# Atlas Vector Search query (PyMongo example)

from pymongo import MongoClient
client = MongoClient(os.getenv("MONGODB_URI"))
col = client.db.video_chunks

def search_chunks(query_vec, k=8, filters=None):
pipeline = [
{"$vectorSearch": {
"index": "video_chunks_vec",
"path": "embedding",
"queryVector": query_vec,
"numCandidates": 200,
"limit": k,
"filter": filters or {}
}},
{"$project": {"text":1, "meta":1, "score": {"$meta": "vectorSearchScore"}, "trust_score":1}}
]
return list(col.aggregate(pipeline))

7. Context-engineering choices (why they matter)

Hierarchical memory: raw → cleaned → enriched → chunked → summarized (agents can choose the right layer)

Rich metadata: channel, playlist, topic, code_present → powerful retrieval filters

Redundancy flag: prevents flooding the LLM with the “same” lesson across channels

TrustScore: pragmatic, explainable ranking (consensus + recency + engagement + code validity)

Chunk design: semantic, overlap, code-aware → better recall and fewer cut-off snippets

Composed prompts: different templates per task (cheat-sheet vs compare vs unique)

8. Demo script (7–8 minutes)

Problem: info overload; repetitive tutorials; hard to compare teachings.

Ingest: pick a 5–12 video playlist; show raw_videos doc.

Pipeline: quick animation of agents; show video_chunks with embeddings.

Atlas: show vector index + a sample vector search from MongoDB UI.

Cheat-sheet: run query → live summary with citations & code.

Compare: pick 3 channels → consensus vs unique tips table.

Unique insights: show results excluding redundant chunks.

Memory: re-ask a follow-up; show retrieval logs; emphasize persistent adaptive memory.

9. Milestones (hackathon cadence)

Day 1 (AM): Repo scaffolding, Atlas cluster + index, Voyage key; IngestAgent done

Day 1 (PM): CleanAgent, EnrichAgent (tags, code detect), ChunkEmbedAgent, first embeddings

Day 2 (AM): Redundancy + TrustRank; SummarizerAgent (per-video, per-playlist)

Day 2 (PM): Streamlit MVP (Cheat-sheet & Compare), polish prompts, demo script, 2–3 curated datasets

10. Quality checks / evaluation (fast, practical)

Groundedness: all answers include citations (video_id:chunk_id + timestamp)

Coverage: % playlist videos referenced in cheat-sheet

Redundancy reduction: unique-insight view excludes ≥80% of dup chunks

Trust sanity: higher trust_score correlates with multi-channel consensus

Latency: end-to-end query < 3s on small dataset (tune k, caching)

11. Stretch features (time-permitting)

Code verifiers: run snippets in sandbox; auto-fix minimal errors for display

“Compare pedagogy”: readability level, pace, exercises presence

Learner mode: export cheat-sheet to Markdown/PDF; spaced-repetition Q&A from chunks

Instructor mode: “what have I already taught?” planner for next videos

12. README skeleton (for the repo)

What & Why (problem, hackathon theme alignment)

Stack (MongoDB Atlas Vector Search, Voyage embeddings, Streamlit, Python)

Setup: env vars, Atlas index JSON, seed script for 1–2 playlists

Run: python ingest.py, python pipeline.py, streamlit run app.py

Demo commands: preset queries for cheat-sheet / compare / unique

Notes: limits, future work, safety & licensing of transcripts
