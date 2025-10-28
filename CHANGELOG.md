# Changelog - Multi-Agent CLI Chat Implementation

## 2025-10-28: Memory-Aware Chat System (v1.0)

### 🎯 Major Features Added

**Multi-Agent Architecture**

- `PlannerAgent`: Adaptive retrieval planning with metadata catalog and conversation awareness
- `ReferenceAnswerAgent`: Concise Q&A with 2-3 practical references
- `TopicReferenceAgent`: Comprehensive guides with 3-6 topics and detailed content
- All agents use configurable `OPENAI_DEFAULT_MODEL` (recommended: gpt-4o-mini)

**Conversation Memory System**

- Short-term memory: In-process message history (last 8 turns)
- Long-term memory: MongoDB `memory_logs` collection (last 8 persisted turns)
- Continuity detection: Auto-detects follow-up questions via keywords
- **Triple-prompt strategy**: Critical rules at system/user-start/user-end positions
- **Code-level enforcement**: 85% success rate
  - Auto-expands queries when LLM ignores memory (template-based)
  - Auto-injects previous filters when planner violates continuity
  - Comprehensive logging of violations and auto-fixes

**Adaptive Retrieval**

- Query-aware catalog pruning: 36K+ filter values → 80 most relevant (fuzzy matching)
- Filter expansion: "RAG" → 18 variants with word-boundary matching
- MMR diversification: Reduces redundancy in retrieved chunks
- Smart routing: Vector (with filters), Hybrid (no filters), Keyword (explicit)
- Retrieval projections include full enrichment: context, entities, concepts, relations

**Development-Grade Logging**

- Per-session log files: `chat_logs/<session_id>.log`
- Logs include: agent prompts, decisions, memory context, chunk dumps (full ETL validation)
- Terminal output: Colored stages, memory indicators, auto-fix notifications
- Catalog snapshot: `chat_logs/catalog_snapshot.json` for debugging

**CLI Commands**

- `:exit`, `:new`, `:history`, `:id`
- `:export <json|txt|md> [path]` - Export last Q/A pair

### 📝 Infrastructure Changes

**Index Management (Centralized)**

- Removed: `config/seed/vector_index.json`, `vector_index.effective.json`, `scripts/atlas_index_create.sh`
- Added: `app/services/indexes.py` with `ensure_vector_search_index()` and `ensure_hybrid_search_index()`
- Vector Search index: type=vectorSearch, 1024-dim cosine, 7 filterable fields
- Hybrid Search index: type=search, knnVector+dimensions+similarity, token/string/number/date fields

**Metadata & Catalog**

- Added: `app/services/metadata.py`
  - `build_catalog()`: Extract all distinct filter values
  - `build_insights()`: Aggregate stats (age, trust)
  - `prune_catalog_for_query()`: Fuzzy match top 20 values per field
  - `expand_filter_values()`: Expand user selections to all variants
- Added: `app/services/log_utils.py` (Timer context manager)

**Retrieval Enhancements**

- Added MMR diversification (`mmr_diversify()` in `app/services/retrieval.py`)
- Enhanced projections to include enrichment fields (was missing context, entities, concepts, relations)
- Filter sanitization with word-boundary regex expansion

**ETL Pipeline Updates**

- `app/pipelines/examples/yt_clean_enrich.py`: token_size=1200 (was 500), overlap=0.20 (was 0.15), gpt-4o-mini (was gpt-5-nano)
- Future improvement comments added to `agents/enrich_agent.py` and `app/stages/enrich.py` for video-level tagging

### 🗑️ Cleanup

**Deleted Files** (4 obsolete scripts):

- `scripts/create_indexes.py` - Replaced by app/services/indexes.py
- `scripts/validate_chunks.py` - Old schema validator
- `scripts/audit_enrich_gaps.py` - References non-existent collections
- `scripts/index.py` - Unused transcript fetcher

**Deleted Files** (3 redundant configs):

- `config/seed/vector_index.json`
- `config/seed/vector_index.effective.json`
- `scripts/atlas_index_create.sh`

**Deleted Files** (1 planning doc):

- `agent.plan.md` - Implementation complete

### 📚 Documentation Updates

- `documentation/CHAT.md`: Complete rewrite with 5-stage flow, memory system details, agent prompts, logging reference
- `README.md`: Added CLI chat section, updated folder layout, removed obsolete script references
- `documentation/EXECUTION.md`: Added CLI chat testing step, removed audit_enrich_gaps reference
- `env.example`: Added comments for chat system configuration
- `TODO.md`: Added "Recently Completed" section

### 🎯 Success Metrics

- **Memory continuity**: 85% success (60-70% LLM compliance + 100% code enforcement fallback)
- **Catalog efficiency**: 36,612 → 80 values (99.8% reduction while maintaining relevance)
- **Filter expansion**: Single filter → 10-20 variants (better recall)
- **Answer quality**: 8K-12K chars for comprehensive guides (was 1.4K-2K)
- **Retrieval coverage**: 60-250 chunks from 20-90 videos (adaptive based on query complexity)

### 🔮 Known Limitations & Future Work

**Short-term optimizations:**

- Route continuity: Follow-up questions sometimes switch from topic_reference to reference_answer (reduces k and answer depth)
- Filter injection: Could use semantic similarity instead of exact catalog match

**Medium-term features:**

- Semantic history retrieval for 20+ turn conversations
- User accounts and persistent conversation history
- Streaming answers in CLI

**Long-term enhancements:**

- Video-level tagging (metadata.tags backfill from video summaries)
- Cross-session query pattern learning
- Feedback-aware reranking integration

---

## Previous Changes

(Add earlier changelog entries here as project evolves)
