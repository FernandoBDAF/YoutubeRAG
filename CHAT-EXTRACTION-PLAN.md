# Chat Feature Extraction Plan (Phase 5.5)

**Current**: `app/cli/chat.py` (1,375 lines - monolithic)  
**Target**: Clean business logic + slim CLI (~200 lines)  
**Time Estimate**: 2-3 hours

---

## Current File Analysis

### Function Breakdown (19 functions):

**Session & Memory** (5 functions):

- `generate_session_id()` - UUID generation
- `load_long_term_memory()` - DB query for memory logs
- `setup_logger()` - Session-specific logging
- `persist_turn()` - Save conversation turn to DB
- `cprint()` - CLI color printing

**Query Processing** (2 functions):

- `_openai_available()` - Check if OpenAI configured
- `rewrite_query()` - LLM-powered query rewriting with memory context

**Retrieval** (3 functions):

- `run_retrieval()` - Orchestrates vector/hybrid/keyword search
- `normalize_context_blocks()` - Normalize hit structure
- `sanitize_filters()` - Clean and validate filters

**Answering** (3 functions):

- `answer_with_context()` - Generate answer using agents
- `build_reference_bundles()` - Group hits by video for reference mode
- `_merge_hits_by_doc()` - Merge chunks from same video
- `_anchor_from_chunk()` - Create anchor metadata

**Utilities** (3 functions):

- `format_citations()` - Format search results for display
- `export_last_turn()` - Export conversation to JSON/TXT/MD
- `upsert_vector_index()` - Ensure vector index exists

**CLI** (3 functions):

- `parse_args()` - Argparse setup
- `run_cli()` - Main CLI loop

---

## Extraction Strategy

### Target Structure:

```
business/chat/
├── __init__.py
├── memory.py              # Session & memory management
├── query_rewriter.py      # Query rewriting with LLM
├── planner.py             # Planning integration (uses PlannerAgent)
├── retrieval.py           # Retrieval orchestration
└── answering.py           # Answer generation

business/services/chat/
├── __init__.py
├── filters.py             # Filter sanitization & expansion
├── citations.py           # Citation formatting
└── export.py              # Export helpers

app/cli/
└── chat.py                # Slim CLI (~200 lines)
```

---

## Detailed Extraction Map

### 1. business/chat/memory.py

**Functions to Extract**:

- `generate_session_id()` - Lines 58-59
- `load_long_term_memory()` - Lines 62-71
- `setup_logger()` - Lines 81-100
- `persist_turn()` - Lines 488-524

**New Imports**:

```python
import uuid
import logging
from pathlib import Path
from typing import Any, Dict, List
from dependencies.database.mongodb import get_mongo_client
from core.config.paths import DB_NAME, COLL_MEMORY_LOGS
```

**Total**: ~60 lines

---

### 2. business/chat/query_rewriter.py

**Functions to Extract**:

- `_openai_available()` - Lines 112-113
- `rewrite_query()` - Lines 116-269

**New Imports**:

```python
import os
import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from openai import OpenAI
```

**Total**: ~160 lines

---

### 3. business/chat/retrieval.py

**Functions to Extract**:

- `run_retrieval()` - Lines 271-309
- `normalize_context_blocks()` - Lines 311-326

**New Imports**:

```python
from typing import Any, Dict, List, Optional
from business.services.rag.retrieval import vector_search, hybrid_search, keyword_search
from dependencies.observability.log_utils import Timer
```

**Total**: ~50 lines

---

### 4. business/chat/answering.py

**Functions to Extract**:

- `answer_with_context()` - Lines 475-486
- `build_reference_bundles()` - Lines 438-473
- `_merge_hits_by_doc()` - Lines 380-406
- `_anchor_from_chunk()` - Lines 408-436

**New Imports**:

```python
from typing import Any, Dict, List
from business.agents.rag.reference_answer import ReferenceAnswerAgent
from business.agents.rag.topic_reference import TopicReferenceAgent
```

**Total**: ~110 lines

---

### 5. business/chat/planner.py

**Purpose**: Wrapper around PlannerAgent for chat context

**Content**: Integration with existing PlannerAgent

**New File** (not direct extraction, integration):

```python
from typing import Any, Dict, List, Optional
from business.agents.rag.planner import PlannerAgent

class ChatPlanner:
    def __init__(self):
        self.planner_agent = PlannerAgent()

    def plan(self, query: str, catalog: Dict, filters: Optional[Dict] = None):
        # Uses existing PlannerAgent
        return self.planner_agent.plan(query, catalog, filters)
```

**Total**: ~40 lines

---

### 6. business/services/chat/filters.py

**Functions to Extract**:

- `sanitize_filters()` - Lines 328-378

**Also Move From** `app/services/metadata.py`:

- `expand_filter_values()` - Currently in metadata service

**New Imports**:

```python
from typing import Any, Dict, List, Optional
from business.services.ingestion.metadata import extract_query_keywords
```

**Total**: ~80 lines

---

### 7. business/services/chat/citations.py

**Functions to Extract**:

- `format_citations()` - Lines 526-550

**New Imports**:

```python
from typing import Any, Dict, List
```

**Total**: ~30 lines

---

### 8. business/services/chat/export.py

**Functions to Extract**:

- `export_last_turn()` - Lines 552-632

**New Imports**:

```python
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
```

**Total**: ~90 lines

---

### 9. app/cli/chat.py (Slim CLI)

**Keep in CLI**:

- `parse_args()` - Lines 634-651
- `run_cli()` - Lines 653-1375 (but refactored to use extracted modules)
- `cprint()` - Lines 103-104 (CLI display)
- `upsert_vector_index()` - Lines 74-78 (CLI initialization)
- ANSI color constants - Lines 46-55

**Refactored run_cli()** (~150 lines):

```python
def run_cli():
    args = parse_args()

    # Initialize components (BUSINESS layer)
    from business.chat.memory import SessionManager
    from business.chat.query_rewriter import QueryRewriter
    from business.chat.retrieval import ChatRetrieval
    from business.chat.answering import ChatAnswering
    from business.services.chat.citations import format_citations
    from business.services.chat.export import export_conversation

    session = SessionManager(args.session_id)
    rewriter = QueryRewriter()
    retrieval = ChatRetrieval()
    answering = ChatAnswering()

    # Main loop
    while True:
        user_input = input("> ")

        # Process
        rewritten, mode, k, filters = rewriter.rewrite(user_input, session.memory)
        hits = retrieval.retrieve(rewritten, mode, k, filters)
        answer = answering.answer(mode, hits)

        # Display
        print_answer(answer, hits)

        # Persist
        session.save_turn(user_input, answer, hits)
```

**Total**: ~200 lines

---

## Execution Plan

### Step 1: Create Memory Module (15 min)

Extract session and memory functions to `business/chat/memory.py`

### Step 2: Create Query Rewriter (20 min)

Extract query rewriting logic to `business/chat/query_rewriter.py`

### Step 3: Create Retrieval Module (15 min)

Extract retrieval orchestration to `business/chat/retrieval.py`

### Step 4: Create Answering Module (20 min)

Extract answering logic to `business/chat/answering.py`

### Step 5: Create Filter Service (15 min)

Extract filter utilities to `business/services/chat/filters.py`

### Step 6: Create Citation Service (10 min)

Extract citation formatting to `business/services/chat/citations.py`

### Step 7: Create Export Service (15 min)

Extract export helpers to `business/services/chat/export.py`

### Step 8: Create Slim CLI (30 min)

Refactor `app/cli/chat.py` to orchestrate extracted modules

### Step 9: Test & Verify (20 min)

Test chat CLI end-to-end

**Total**: ~2.5 hours

---

## Benefits

### Before:

- 1,375 lines in one file
- Hard to test (CLI mixed with logic)
- Can't reuse for UI or API

### After:

- ~200 lines CLI (orchestration only)
- ~530 lines business logic (testable)
- Reusable for:
  - Chat CLI
  - Streamlit chat UI
  - Future MCP server chat endpoints

### Reusability Example:

**For Streamlit UI**:

```python
# app/ui/chat_widget.py
from business.chat.memory import SessionManager
from business.chat.answering import ChatAnswering

def chat_widget():
    session = st.session_state.get('chat_session')
    if not session:
        session = SessionManager()
        st.session_state['chat_session'] = session

    # Use same business logic as CLI!
    answering = ChatAnswering()
    answer = answering.answer(mode, hits)
    st.write(answer)
```

**For MCP Server**:

```python
# app/api/routes/chat.py
from business.chat.answering import ChatAnswering

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    answering = ChatAnswering()
    answer = answering.answer(request.mode, request.context)
    return {"answer": answer}
```

---

**Ready to execute extraction!**
