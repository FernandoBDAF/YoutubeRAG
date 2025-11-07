# Codebase Inventory

**Created**: November 6, 2025  
**Purpose**: Complete inventory of all files in `app/` and `business/` directories  
**Status**: Baseline for PLAN_CODE-QUALITY-REFACTOR.md

---

## Executive Summary

**Total Files**: 94 Python files

- **app/**: 24 files (~5,690 lines)
- **business/**: 70 files (~19,533 lines)

**Total Lines of Code**: ~25,223 lines (app + business)

**Domains**:

- GraphRAG: 20 files (agents, stages, services)
- Ingestion: 15 files (agents, stages, services)
- RAG: 11 files (agents, services, queries)
- Chat: 7 files (modules, services)
- Pipelines: 3 files
- Core Infrastructure: 14 files (app layer)

---

## APP Layer Inventory

### Structure

```
app/
├── cli/          # Command-line interfaces (3 files)
├── ui/           # User interfaces (1 file)
├── api/          # API endpoints (1 file)
└── scripts/      # Utility scripts (19 files)
```

### File Breakdown

#### CLI (3 files)

- `app/cli/main.py` - Ingestion pipeline CLI
- `app/cli/graphrag.py` - GraphRAG pipeline CLI
- `app/cli/chat.py` - Chat interface CLI

#### UI (1 file)

- `app/ui/streamlit_app.py` - Streamlit dashboard

#### API (1 file)

- `app/api/metrics.py` - Metrics API endpoint

#### Scripts (19 files)

**GraphRAG Scripts** (8 files):

- `app/scripts/graphrag/analyze_graph_structure.py`
- `app/scripts/graphrag/diagnose_communities.py`
- `app/scripts/graphrag/inspect_community_detection.py`
- `app/scripts/graphrag/monitor_density.py`
- `app/scripts/graphrag/run_random_chunk_test.py`
- `app/scripts/graphrag/sample_graph_data.py`
- `app/scripts/graphrag/test_community_detection.py`
- `app/scripts/graphrag/test_random_chunks.py`

**Utilities** (3 files):

- `app/scripts/utilities/check_data.py`
- `app/scripts/utilities/full_cleanup.py`
- `app/scripts/utilities/seed/seed_indexes.py`

**Total**: 24 Python files in app/  
**Estimated Lines**: ~5,690 lines

---

## BUSINESS Layer Inventory

### Structure

```
business/
├── agents/       # LLM-powered agents (13 files)
├── stages/       # Pipeline stages (13 files)
├── services/     # Domain services (23 files)
├── queries/      # Query handlers (4 files)
├── chat/         # Chat modules (4 files)
└── pipelines/    # Pipeline orchestration (3 files)
```

### Domain Breakdown

#### GraphRAG Domain (20 files)

**Agents** (6 files):

- `business/agents/graphrag/extraction.py`
- `business/agents/graphrag/entity_resolution.py`
- `business/agents/graphrag/relationship_resolution.py`
- `business/agents/graphrag/community_detection.py`
- `business/agents/graphrag/community_summarization.py`
- `business/agents/graphrag/link_prediction.py`

**Stages** (4 files):

- `business/stages/graphrag/extraction.py`
- `business/stages/graphrag/entity_resolution.py`
- `business/stages/graphrag/graph_construction.py`
- `business/stages/graphrag/community_detection.py`

**Services** (5 files):

- `business/services/graphrag/indexes.py`
- `business/services/graphrag/query.py`
- `business/services/graphrag/retrieval.py`
- `business/services/graphrag/generation.py`
- `business/services/graphrag/run_metadata.py`

**Queries**: None (queries are in RAG domain)

---

#### Ingestion Domain (15 files)

**Agents** (3 files):

- `business/agents/ingestion/clean.py`
- `business/agents/ingestion/enrich.py`
- `business/agents/ingestion/trust.py`

**Stages** (9 files):

- `business/stages/ingestion/ingest.py`
- `business/stages/ingestion/clean.py`
- `business/stages/ingestion/chunk.py`
- `business/stages/ingestion/enrich.py`
- `business/stages/ingestion/embed.py`
- `business/stages/ingestion/redundancy.py`
- `business/stages/ingestion/trust.py`
- `business/stages/ingestion/backfill_transcript.py`
- `business/stages/ingestion/compress.py`

**Services** (2 files):

- `business/services/ingestion/transcripts.py`
- `business/services/ingestion/metadata.py`

**Queries**: None

---

#### RAG Domain (11 files)

**Agents** (3 files):

- `business/agents/rag/reference_answer.py`
- `business/agents/rag/topic_reference.py`
- `business/agents/rag/planner.py`

**Stages**: None (RAG uses services/queries, not stages)

**Services** (8 files):

- `business/services/rag/core.py`
- `business/services/rag/generation.py`
- `business/services/rag/retrieval.py`
- `business/services/rag/indexes.py`
- `business/services/rag/filters.py`
- `business/services/rag/feedback.py`
- `business/services/rag/persona_utils.py`
- `business/services/rag/profiles.py`

**Queries** (4 files):

- `business/queries/rag/vector_search.py`
- `business/queries/rag/llm_question.py`
- `business/queries/rag/get.py`
- `business/queries/rag/videos_insights.py`

---

#### Chat Domain (7 files)

**Modules** (4 files):

- `business/chat/memory.py`
- `business/chat/query_rewriter.py`
- `business/chat/retrieval.py`
- `business/chat/answering.py`

**Services** (3 files):

- `business/services/chat/filters.py`
- `business/services/chat/citations.py`
- `business/services/chat/export.py`

**Agents**: None  
**Stages**: None  
**Queries**: None

---

#### Pipelines (3 files)

**Core Pipeline Infrastructure**:

- `business/pipelines/runner.py` - Pipeline runner/orchestrator
- `business/pipelines/ingestion.py` - Ingestion pipeline
- `business/pipelines/graphrag.py` - GraphRAG pipeline

---

### Total BUSINESS Layer

**Files by Type**:

- Agents: 13 files
- Stages: 13 files
- Services: 23 files
- Queries: 4 files
- Chat: 4 files
- Pipelines: 3 files
- **Total**: 60 files (excluding **init**.py)

**Files by Domain**:

- GraphRAG: 20 files
- Ingestion: 15 files
- RAG: 11 files
- Chat: 7 files
- Pipelines: 3 files
- **Total**: 56 files (excluding **init**.py)

**Estimated Lines**: ~19,533 lines

---

## File Count Summary

| Layer         | Files  | Estimated Lines |
| ------------- | ------ | --------------- |
| **app/**      | 24     | ~5,690          |
| **business/** | 70     | ~19,533         |
| **Total**     | **94** | **~25,223**     |

---

## Domain Distribution

| Domain        | Agents | Stages | Services | Queries | Chat  | Pipelines | **Total** |
| ------------- | ------ | ------ | -------- | ------- | ----- | --------- | --------- |
| **GraphRAG**  | 6      | 4      | 5        | 0       | 0     | 0         | **15**    |
| **Ingestion** | 3      | 9      | 2        | 0       | 0     | 0         | **14**    |
| **RAG**       | 3      | 0      | 8        | 4       | 0     | 0         | **15**    |
| **Chat**      | 0      | 0      | 3        | 0       | 4     | 0         | **7**     |
| **Pipelines** | 0      | 0      | 0        | 0       | 0     | 3         | **3**     |
| **App Layer** | -      | -      | -        | -       | -     | -         | **24**    |
| **Total**     | **12** | **13** | **18**   | **4**   | **4** | **3**     | **78**    |

_Note: App layer files are not domain-specific_

---

## Recent Changes Context

**From ACTIVE_PLANS.md** (November 6, 2025):

**Paused Plans** (affecting GraphRAG domain):

- PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md (paused, 4/13 achievements)
- PLAN_ENTITY-RESOLUTION-REFACTOR.md (paused, 17/31 achievements)
- PLAN_GRAPH-CONSTRUCTION-REFACTOR.md (paused, 11/17 achievements)
- PLAN_COMMUNITY-DETECTION-REFACTOR.md (paused, 14/23 achievements)

**Impact**: GraphRAG domain has received significant recent work and refactoring. These changes should be considered when reviewing for library extraction opportunities.

---

## Notes for Review

1. **GraphRAG Domain** is the largest and most complex (20 files)

   - Recent refactoring work (entity resolution, graph construction, community detection)
   - Likely has patterns ready for library extraction

2. **Ingestion Domain** has the most stages (9 stages)

   - Pipeline-heavy domain
   - Likely has stage execution patterns

3. **RAG Domain** is service-heavy (8 services)

   - Query-focused domain
   - Likely has retrieval patterns

4. **Chat Domain** is smallest (7 files)

   - Recently extracted
   - May have minimal duplication

5. **Pipelines** are cross-cutting (3 files)
   - Orchestration patterns
   - Stage execution patterns

---

**Last Updated**: November 6, 2025
