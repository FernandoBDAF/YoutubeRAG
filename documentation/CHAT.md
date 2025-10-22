### Agentic, Memory-Aware CLI Chat

This document describes the CLI chat added in `chat.py` that performs memory-aware, tool-augmented RAG over the project’s MongoDB collections.

### Scope

- Anonymous sessions only (no auth)
- CLI-first; streamlit integration can come later
- All orchestration implemented in `chat.py`

### Data Model

- `memory_logs` (per-turn):
  - `session_id`, `user_query_raw`, `user_query_rewritten`
  - `mode` (vector|hybrid|keyword|auto), `k`, `filters`
  - `retrieved[]` with `{video_id, chunk_id, score|search_score, keyword_score, vector_score}`
  - `answer`, `created_at`

### Orchestration Steps

1. Session bootstrap
   - Generate or accept `--session` id (UUID)
   - Load last N logs for long‑term context
2. Short/long‑term memory
   - Short-term: in-process recent messages list
   - Long-term: last N session logs from `memory_logs`
3. Query rewrite agent
   - If `OPENAI_API_KEY` available, LLM rewrites: returns `{query, tool, k, filters}`
   - Otherwise identity rewrite
4. Retrieval tools
   - `vector_search`, `hybrid_search`, `keyword_search` (wrappers in `chat.py`)
   - `--mode` overrides tool; otherwise planner suggestion; default is vector
5. Answer agent
   - Compose answer with `app/services/generation.py` using retrieved context
   - Adds a tiny recent-history hint to the question
6. Persistence
   - Insert a document into `memory_logs` with full metadata

### CLI Usage

Run:

```bash
python chat.py --session <optional-id> --top_k 8 --mode auto --log_dir chat_logs
```

In-chat commands:

- `:exit` — quit
- `:new` — start a new session (new UUID)
- `:history` — show recent turns
- `:id` — show current `session_id`
- `:export <fmt> [path]` — export last Q/A to json|txt|md (optional path)

### Observability & Logs

- Colored stage prints in CLI for pipeline visibility:
  - `[1/5] Rewriting query…`
  - `[2/5] Retrieval plan …`
  - `[3/5] Retrieving context…`
  - `[4/5] Generating answer…`
  - `[5/5] Answer:`
- Per-session logs are written to `chat_logs/<session_id>.log` (override with `--log_dir`).
  - Includes rewrite/retrieve/answer/persist events, counts, and sizes for debugging and optimization.

### Exporting the Last Turn

Examples:

```bash
# JSON (default filename)
:export json

# Markdown to a custom path
:export md exports/last.md
```

### Prompts (outline)

- QueryRewriteAgent (system):
  "You improve user queries for retrieval using conversation memory. Return strict JSON with keys: query, tool, k, filters. tool in {auto, vector, hybrid, keyword}."

- AnswerAgent: uses `answer_with_openai` with the rewritten question and context blocks.

### Notes & Fallbacks

- If no `OPENAI_API_KEY`, rewrite becomes identity and answers show a context dump format.
- Vector index is ensured via `setup_vector_search_index` before retrieval.
- Short/long-term caps are applied to keep prompts small.

### Future Work

- User accounts and profile/persona preferences
- Tool autonomy expansions (e.g., structured filters, rerank controls)
- Streaming in CLI, richer citations/metadata
- Feedback-aware reranking using `video_feedback`/`chunk_feedback`
