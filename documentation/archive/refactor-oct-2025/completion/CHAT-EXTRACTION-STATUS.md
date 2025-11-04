# Chat Extraction Status (Phase 5.5)

**Started**: October 31, 2025  
**Current Status**: In Progress (1 of 8 modules complete)  
**Estimated Remaining**: 2 hours

---

## ✅ Completed Modules

### 1. business/chat/memory.py ✅ (Created)

**Functions Extracted**:

- `generate_session_id()` - UUID generation
- `load_long_term_memory()` - Load conversation history from DB
- `setup_chat_logger()` - Session-specific logging
- `persist_turn()` - Save conversation turn to DB

**Lines**: ~140 lines  
**Status**: Complete and ready to use

---

## ⏳ Remaining Modules (7 modules)

### 2. business/chat/query_rewriter.py (Not Started)

**Source**: Lines 112-269 from `app/cli/chat.py`

**Functions to Extract**:

- `_openai_available()` - Check OpenAI configuration
- `rewrite_query()` - LLM-powered query rewriting with memory context

**Key Features**:

- Memory-aware query rewriting
- Follow-up query detection
- Catalog-aware filter generation
- Self-check prompt for LLM

**Complexity**: High (160 lines, complex prompt)  
**Time**: 20 minutes

---

### 3. business/chat/retrieval.py (Not Started)

**Source**: Lines 271-326 from `app/cli/chat.py`

**Functions to Extract**:

- `run_retrieval()` - Orchestrate vector/hybrid/keyword search
- `normalize_context_blocks()` - Normalize hit structure

**Dependencies**:

- `business.services.rag.retrieval` (vector_search, hybrid_search, keyword_search)
- `dependencies.observability.log_utils` (Timer)

**Complexity**: Medium (60 lines)  
**Time**: 15 minutes

---

### 4. business/chat/answering.py (Not Started)

**Source**: Lines 380-486 from `app/cli/chat.py`

**Functions to Extract**:

- `answer_with_context()` - Generate answer using agents
- `build_reference_bundles()` - Group hits by video
- `_merge_hits_by_doc()` - Merge chunks from same video
- `_anchor_from_chunk()` - Create anchor metadata

**Dependencies**:

- `business.agents.rag.reference_answer` (ReferenceAnswerAgent)
- `business.agents.rag.topic_reference` (TopicReferenceAgent)

**Complexity**: High (110 lines, multiple functions)  
**Time**: 20 minutes

---

### 5. business/services/chat/filters.py (Not Started)

**Source**: Lines 328-378 from `app/cli/chat.py`

**Functions to Extract**:

- `sanitize_filters()` - Clean and validate filters

**Also Consider**:

- `expand_filter_values()` from `business.services.ingestion.metadata`

**Complexity**: Medium (80 lines)  
**Time**: 15 minutes

---

### 6. business/services/chat/citations.py (Not Started)

**Source**: Lines 526-550 from `app/cli/chat.py`

**Functions to Extract**:

- `format_citations()` - Format search results for display

**Complexity**: Low (30 lines)  
**Time**: 10 minutes

---

### 7. business/services/chat/export.py (Not Started)

**Source**: Lines 552-632 from `app/cli/chat.py`

**Functions to Extract**:

- `export_last_turn()` - Export conversation to JSON/TXT/MD

**Complexity**: Medium (90 lines)  
**Time**: 15 minutes

---

### 8. app/cli/chat.py Refactored (Not Started)

**Current**: 1,375 lines (monolithic)  
**Target**: ~200 lines (orchestration only)

**Keep in CLI**:

- `parse_args()` - CLI argument parsing
- `run_cli()` - Main loop (refactored to use extracted modules)
- `cprint()` - Color printing helper
- `upsert_vector_index()` - Initialization helper
- ANSI color constants

**Refactored Structure**:

```python
def run_cli():
    # Parse args
    args = parse_args()

    # Initialize business components
    from business.chat.memory import (
        generate_session_id,
        load_long_term_memory,
        setup_chat_logger,
        persist_turn
    )
    from business.chat.query_rewriter import rewrite_query
    from business.chat.retrieval import run_retrieval, normalize_context_blocks
    from business.chat.answering import answer_with_context
    from business.services.chat.citations import format_citations
    from business.services.chat.export import export_last_turn

    # Setup session
    session_id = args.session_id or generate_session_id()
    logger = setup_chat_logger(session_id)
    long_term_memory = load_long_term_memory(session_id)
    short_term_msgs = []

    # Main loop
    while True:
        try:
            user_query = input("> ").strip()

            # Handle commands
            if user_query in ["exit", "quit", "/exit", "/quit"]:
                break
            if user_query.startswith("/export"):
                export_last_turn(session_id, args.export_format)
                continue

            # Rewrite query with memory context
            rewritten, mode, k, filters = rewrite_query(
                user_query, short_term_msgs, long_term_memory,
                args.mode, args.k, catalog, logger
            )

            # Retrieve context
            hits = run_retrieval(rewritten, mode, k, filters, logger)
            hits = normalize_context_blocks(hits)

            # Generate answer
            answer = answer_with_context(mode, hits, rewritten, logger)

            # Display
            cprint(f"\n{answer}\n", GREEN)
            citations = format_citations(hits)
            cprint(citations, DIM)

            # Persist
            persist_turn(session_id, user_query, rewritten, mode, k, filters, hits, answer)

            # Update short-term memory
            short_term_msgs.append({"role": "user", "content": user_query})
            short_term_msgs.append({"role": "assistant", "content": answer})

        except KeyboardInterrupt:
            break
        except Exception as e:
            cprint(f"Error: {e}", RED)
```

**Complexity**: Medium (refactor existing loop)  
**Time**: 30 minutes

---

## Extraction Sequence

**Recommended Order**:

1. ✅ memory.py (DONE)
2. → query_rewriter.py (next)
3. → retrieval.py
4. → answering.py
5. → filters.py
6. → citations.py
7. → export.py
8. → Refactor CLI

**Total Time Remaining**: ~2 hours

---

## Next Session Resume Point

**To Continue**:

1. Read lines 112-269 from `app/cli/chat.py` (query rewriting)
2. Create `business/chat/query_rewriter.py`
3. Continue with remaining modules in order
4. Test each module as created
5. Final refactor of CLI to use all modules

**Files Ready**:

- ✅ `business/chat/memory.py` - Complete
- ✅ `business/chat/__init__.py` - Empty, ready
- ✅ `business/services/chat/__init__.py` - Empty, ready

**Verification After Completion**:

```python
from business.chat.memory import generate_session_id, persist_turn
from business.chat.query_rewriter import rewrite_query
from business.chat.retrieval import run_retrieval
from business.chat.answering import answer_with_context
print("✓ All chat modules working!")
```

---

## Benefits When Complete

### Reusability:

**For Streamlit**:

```python
from business.chat.answering import answer_with_context
# Use same logic as CLI!
```

**For MCP Server**:

```python
from business.chat.retrieval import run_retrieval
from business.chat.answering import answer_with_context
# Expose as API endpoints
```

**For Testing**:

```python
# Test business logic without CLI
from business.chat.query_rewriter import rewrite_query
result = rewrite_query(query, memory, ...)
assert result[0] != query  # Verify rewriting works
```

### Code Quality:

- 1,375 lines → ~200 line CLI + ~620 lines business logic
- Clear separation of concerns
- Each module independently testable
- Follows 4-layer architecture

---

**Status**: 1 of 8 modules complete. Ready to resume extraction.
