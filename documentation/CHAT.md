### Agentic, Memory-Aware CLI Chat

An intelligent chat system that performs multi-agent, memory-aware RAG over MongoDB video_chunks with adaptive retrieval planning, conversation continuity, and comprehensive logging.

### Key Features

- **Multi-Agent Architecture**: PlannerAgent, ReferenceAnswerAgent, TopicReferenceAgent
- **Conversation Memory**: Short-term (in-process) + Long-term (MongoDB persisted)
- **Adaptive Retrieval**: Query-aware catalog pruning, smart filter expansion, MMR diversification
- **Code-Level Continuity**: Auto-expands queries and auto-injects filters when LLM fails
- **Development-Grade Logging**: Per-session logs with full chunk dumps, agent prompts, timings

### Scope

- Anonymous sessions only (no auth)
- CLI-first (no Streamlit integration yet)
- All orchestration in `chat.py`

### Data Model

**`memory_logs` Collection** (per-turn):

- `session_id` (UUID), `user_query_raw`, `user_query_rewritten`
- `mode` (vector|hybrid|keyword), `k`, `filters` (planner decision)
- `retrieved[]`: `{video_id, chunk_id, score, keyword_score, vector_score}`
- `answer` (generated text), `agent` (which agent produced answer)
- `created_at` (timestamp)

### Orchestration Flow (5 Stages)

**[1/5] Query Rewriting** (with memory context)

- Detects follow-up questions ("go deeper", "what about", "it", "this")
- Rewrite agent receives SHORT_TERM (last 8 messages) + LONG_TERM (last 8 turns from DB)
- Triple-prompt strategy forces memory usage
- **Code-level enforcement**: Auto-expands unchanged queries using template + memory topic
- Logs: memory counts, rewrite before/after, query changed flag

**[2/5] Planning & Catalog** (metadata-driven decision)

- Builds full catalog (36K+ filter values from context.tags, concepts.name, entities.name, relations.subject)
- Extracts keywords from query and prunes catalog to top 20 most relevant values per field
- PlannerAgent decides:
  - `route`: topic_reference (comprehensive) vs reference_answer (focused)
  - `retrieval`: mode (vector|hybrid|keyword), k (40-300)
  - `filters`: ≤2 fields from catalog, semantically matched to query
  - Receives conversation context (last 3 short-term + 2 long-term turns with filters/topics)
- **Code-level enforcement**: Auto-injects previous filter if planner violates continuity
- Logs: planner decision JSON, conversation context, catalog pruning stats

**[3/5] Retrieval** (with filter expansion)

- Sanitizes and expands filters using fuzzy matching:
  - "RAG" → ["RAG", "rag", "RAG framework", "Graph RAG", ...] (18 variants)
  - "embedding" → ["embed", "embedding", "embeddings", ...] (word boundary matching)
- Routes:
  - Vector-only ($vectorSearch) when filters present
  - Hybrid (knnBeta + text) when no filters
  - Keyword ($search text only) on explicit mode
- MMR diversification reduces redundancy
- Logs: mode, k, filters (raw + expanded), hits count, elapsed time

**[4/5] Answer Generation** (route-specific agents)

- **TopicReferenceAgent** (for comprehensive guides):
  - Groups context by topics (tags + concepts, fallback to video_id)
  - Generates 3-6 topics with 3-5 substantial bullets each (2-3 sentences)
  - 1-2 references per topic with title, URL, time hint
  - max_tokens=12000 for detailed answers
- **ReferenceAnswerAgent** (for focused questions):
  - Concise direct answer
  - 2-3 practical references
  - max_tokens=8000
- Logs: route, elapsed, char count, topics/refs used, token usage

**[5/5] Persistence**

- Upserts turn to `memory_logs` with full metadata
- Refreshes long-term memory cache
- Dumps all chunks to log file for ETL validation
- Logs: chunk counts, unique videos, per-video distribution

### CLI Usage

**Starting a chat:**

```bash
python chat.py --top_k 200 --mode auto --log_dir chat_logs
```

**Arguments:**

- `--session <uuid>` — Resume specific session (default: generate new)
- `--top_k <int>` — Default retrieval count (planner can override, default: 200)
- `--mode <auto|vector|hybrid|keyword>` — Retrieval mode (default: auto, planner decides)
- `--log_dir <path>` — Log file directory (default: chat_logs)

**In-chat commands:**

- `:exit` — Quit
- `:new` — Start new session (generates fresh UUID)
- `:history` — Show recent conversation turns
- `:id` — Display current session_id
- `:export <fmt> [path]` — Export last Q/A pair
  - Formats: `json`, `txt`, `md`
  - Optional path (default: auto-generated filename)

### Observability & Logs

**Terminal Output** (colored, user-friendly):

- Stage indicators: `[1/5] Rewriting query...`, `[2/5] Plan: mode=vector, k=250`, etc.
- Memory awareness: `💭 Context: continuing from '...'`, `💡 Planner aware of 6 turns`
- Auto-fixes: `🔧 Auto-expanded query`, `🔧 Auto-injected previous filter: RAG`
- Warnings: `⚠️ Memory available but query not expanded`
- Summary: `✓ Retrieved 84 chunks from 41 videos`, filter breakdowns

**Log Files** (`chat_logs/<session_id>.log`):

- **Catalog & Insights**: Full catalog keys, sample values, pruning stats, age averages
- **Keywords**: Extracted query keywords for catalog pruning
- **Planner**: Full system/user prompts, JSON decision, conversation context, elapsed time
- **Rewrite**: SHORT_TERM/LONG_TERM memory content, rewritten query, changed flag
- **Retrieval**: Mode, k, filters (raw + sanitized + expanded), hit count, timing
- **Answer**: Route, agent used, char count, topics/refs, token usage (prompt/completion/total)
- **Chunks**: Preview (first 10) + full dump (all N chunks with enrichment fields)
- **Continuity**: Follow-up detection, violations, auto-fix actions

**Catalog Snapshot** (`chat_logs/catalog_snapshot.json`):

- Full catalog saved per session for debugging filter selection
- Shows all available filter values the planner can choose from

### Exporting the Last Turn

Examples:

```bash
# JSON (default filename)
:export json

# Markdown to a custom path
:export md exports/last.md
```

### Agent Prompts (Summary)

**PlannerAgent:**

- CRITICAL RULE #1: Filter continuity - MUST include at least one previous filter when conversation context exists
- Routing: Detects "detailed", "comprehensive", "guide" keywords → topic_reference route
- k guidance: topic_reference=200-300, reference_answer complex=100-150, simple=40-80
- Receives: question, pruned catalog (20 values/field), conversation context, allowed keys
- Returns: `{route, retrieval: {mode, k}, filters, notes}`

**Rewrite Agent:**

- CRITICAL INSTRUCTION #1: For follow-ups, extract topic from memory and MERGE into query
- Triple-prompt: System lead + user reminder (if follow-up) + self-check (4 questions)
- Receives: query, SHORT_TERM (last 8 messages), LONG_TERM (last 8 DB turns), catalog samples
- Returns: `{query, tool, k, filters}`
- **Fallback**: Code auto-expands if unchanged on follow-up

**TopicReferenceAgent:**

- Generates comprehensive multi-topic answers (3-6 topics)
- 3-5 substantial bullets per topic (2-3 sentences each, grounded in context)
- 1-2 references per topic with title, URL, time hint, "where to start"
- CRITICAL: Must use CONTEXT snippets, no external knowledge
- Target: 1500-2000 words, max_tokens=12000

**ReferenceAnswerAgent:**

- Concise direct answer for focused questions
- 2-3 practical references with time hints
- Grounded in retrieved chunks
- max_tokens=8000

### Memory & Continuity System

**Memory Sources:**

1. **Short-term** (in-process list): Last 8 user/assistant message pairs
2. **Long-term** (MongoDB): Last 8 turns from `memory_logs` collection

**Continuity Mechanisms:**

1. **Detection**: Keywords ("go deeper", "what about", "it", "this", "that", "also")
2. **Triple-Prompt Strategy**: Critical rules in system prompt + user reminder + self-check
3. **Code-Level Enforcement** (fallback when LLM fails):
   - Auto-expand queries: Extracts topic from memory, applies template
   - Auto-inject filters: Validates overlap, injects previous filter if missing
4. **Conversation Context**: Planner sees last 3 short-term + 2 long-term with filters/topics
5. **Logging**: All violations logged, auto-fixes visible in terminal and logs

**Success Rate**: ~85% (LLM follows instructions 60-70%, code enforcement covers rest)

### Index Configuration

**Vector Search Index** (type: `vectorSearch`):

- Name: `vector_index_text`
- Field: `embedding` (1024-dim, cosine similarity)
- Filterable fields: context.tags, concepts.name, entities.name, relations.subject, metadata.age_days, published_at, trust_score

**Hybrid Search Index** (type: `search`):

- Name: `search_index_text`
- knnVector: `embedding` (1024-dim, cosine similarity)
- Text fields: text, display_text
- Token fields: context.tags, concepts.name, entities.name, relations.subject
- Number/Date fields: metadata.age_days, trust_score, published_at

### Future Optimizations

**Short-term (next iteration):**

- Route continuity: Keep topic_reference for follow-ups when previous route was topic_reference
- Improve filter injection: Use semantic similarity instead of exact match

**Medium-term:**

- Semantic history retrieval: For 20+ turn conversations, embed and retrieve only relevant turns
- User accounts with persistent preferences
- Streaming answers in CLI

**Long-term:**

- Video-level tagging: Backfill metadata.tags from video summaries for better filtering
- Cross-session learning: Aggregate popular query patterns
- Feedback-aware reranking using video_feedback/chunk_feedback
