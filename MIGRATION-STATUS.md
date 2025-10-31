# Folder Structure Migration - Status

**Started**: October 31, 2025  
**Branch**: refactor/folder-structure (to be created manually)  
**Current Phase**: Phase 2 Complete ✅ → Moving to Phase 3

---

## Phase 0: Preparation ✅ COMPLETE

### Completed:

- ✅ Created empty folder structure for all 4 layers
- ✅ Added `__init__.py` to all new directories
- ✅ Created `REFACTOR-TODO.md` template
- ✅ Created this migration status tracker

### Git Operations (Manual):

```bash
# To be done manually:
git checkout -b refactor/folder-structure
git tag pre-refactor-backup
```

### Folder Structure Created:

```
app/
├── cli/              # NEW - CLIs will go here
├── ui/               # NEW - UIs will go here
├── api/              # NEW - Future MCP server
└── scripts/          # NEW - Runnable scripts
    ├── graphrag/
    └── utilities/

business/
├── agents/           # NEW - Agent implementations
│   ├── graphrag/
│   └── ingestion/
├── stages/           # NEW - Stage implementations
│   ├── graphrag/
│   └── ingestion/
├── pipelines/        # NEW - Pipeline orchestration
├── services/         # NEW - Domain services
│   ├── graphrag/
│   ├── rag/
│   ├── ingestion/
│   └── chat/
├── queries/          # NEW - Query handlers
└── chat/             # NEW - Chat feature logic

core/
├── models/           # NEW - Pydantic models
├── base/             # NEW - Base classes
├── domain/           # NEW - Domain utilities
└── config/           # NEW - Configuration

dependencies/
├── database/         # NEW - Database adapters
├── llm/              # NEW - LLM providers
├── external/         # NEW - External APIs
└── observability/    # NEW - Logging, monitoring

tests/
├── app/              # NEW - APP layer tests
├── business/         # NEW - BUSINESS layer tests
├── core/             # NEW - CORE layer tests
└── dependencies/     # NEW - DEPENDENCIES layer tests
```

---

## Phase 1: Move CORE Layer ✅ COMPLETE

### Completed:

- ✅ Moved 11 files to new locations
- ✅ Updated 100+ import statements across 50+ files
- ✅ All CORE imports verified working
- ✅ Zero breaking changes

### Files Moved:

**Models** → `core/models/`:

- `core/graphrag_models.py` → `core/models/graphrag.py` ✅
- `config/stage_config.py` → `core/models/config.py` ✅

**Base Classes** → `core/base/`:

- `core/base_stage.py` → `core/base/stage.py` ✅
- `core/base_agent.py` → `core/base/agent.py` ✅

**Domain Utilities** → `core/domain/`:

- `core/text_utils.py` → `core/domain/text.py` ✅
- `core/enrich_utils.py` → `core/domain/enrichment.py` ✅
- `core/compression.py` → `core/domain/compression.py` ✅
- `core/concurrency.py` → `core/domain/concurrency.py` ✅

**Configuration** → `core/config/`:

- `config/paths.py` → `core/config/paths.py` ✅
- `config/runtime.py` → `core/config.runtime.py` ✅
- `config/graphrag_config.py` → `core/config/graphrag.py` ✅

### Files Updated (Imports):

**Agents** (12 files): All GraphRAG and ingestion agents  
**Stages** (13 files): All GraphRAG and ingestion stages  
**Pipelines** (3 files): base_pipeline, ingestion_pipeline, graphrag_pipeline  
**Services** (20 files): All services  
**Queries** (4 files): All query handlers  
**Entry Points** (4 files): main.py, run_graphrag_pipeline.py, streamlit_app.py, chat.py  
**Scripts** (10 files): All scripts  
**Config** (1 file): config/**init**.py

### Verification Results:

```python
✓ EntityModel, RelationshipModel, KnowledgeModel
✓ BaseStage, BaseAgent
✓ DB_NAME, GraphExtractionConfig
✓ text utils, enrichment utils
✓ GraphExtractionStage imports working
✓ GraphExtractionAgent imports working
```

### Time Taken: ~1 hour

---

## Phase 2: Extract DEPENDENCIES Layer ✅ COMPLETE

### Completed:

- ✅ Created MongoDB client adapter
- ✅ Created OpenAI client adapter
- ✅ Created logging setup module
- ✅ Moved rate limiting to dependencies
- ✅ All backward compatibility wrappers added
- ✅ Zero breaking changes

### Files Created:

**Database** → `dependencies/database/`:

- `mongodb.py` ✅ (MongoDBClient class + get_mongo_client wrapper)

**LLM** → `dependencies/llm/`:

- `openai.py` ✅ (OpenAIClient class + get_openai_client wrapper)
- `rate_limit.py` ✅ (Moved from app/services/)

**Observability** → `dependencies/observability/`:

- `logging.py` ✅ (setup_logging, get_logger, create_timestamped_log_path)

### Verification Results:

```python
✓ MongoDBClient ready
✓ OpenAIClient ready
✓ Logging setup ready
✓ DEPENDENCIES layer verified!
```

### Key Features:

- **Singleton pattern** for MongoDB and OpenAI clients
- **Backward compatibility** wrappers (get_mongo_client, get_openai_client)
- **Centralized logging** configuration
- **Third-party logger silencing** built-in

### Time Taken: ~30 minutes

---

## Current Structure (To Be Migrated):

### ROOT FILES:

- `main.py` → `app/cli/main.py`
- `run_graphrag_pipeline.py` → `app/cli/graphrag.py`
- `streamlit_app.py` → `app/ui/streamlit_app.py`
- `chat.py` → Extract to `app/cli/chat.py` + `business/chat/`

### agents/ (11 files):

- `graph_extraction_agent.py` → `business/agents/graphrag/extraction.py`
- `entity_resolution_agent.py` → `business/agents/graphrag/entity_resolution.py`
- `relationship_resolution_agent.py` → `business/agents/graphrag/relationship_resolution.py`
- `community_detection_agent.py` → `business/agents/graphrag/community_detection.py`
- `community_summarization_agent.py` → `business/agents/graphrag/community_summarization.py`
- `graph_link_prediction_agent.py` → `business/agents/graphrag/link_prediction.py`
- `clean_agent.py` → `business/agents/ingestion/clean.py`
- `enrich_agent.py` → `business/agents/ingestion/enrich.py`
- `trust_agent.py` → `business/agents/ingestion/trust.py`
- `reference_answer_agent.py` → `business/agents/rag/reference_answer.py` (new location)
- `topic_reference_agent.py` → `business/agents/rag/topic_reference.py` (new location)
- `planner_agent.py` → `business/agents/rag/planner.py` (new location)

### app/stages/ (13 files):

- `graph_extraction.py` → `business/stages/graphrag/extraction.py`
- `entity_resolution.py` → `business/stages/graphrag/entity_resolution.py`
- `graph_construction.py` → `business/stages/graphrag/graph_construction.py`
- `community_detection.py` → `business/stages/graphrag/community_detection.py`
- `ingest.py` → `business/stages/ingestion/ingest.py`
- `clean.py` → `business/stages/ingestion/clean.py`
- `chunk.py` → `business/stages/ingestion/chunk.py`
- `enrich.py` → `business/stages/ingestion/enrich.py`
- `embed.py` → `business/stages/ingestion/embed.py`
- `redundancy.py` → `business/stages/ingestion/redundancy.py`
- `trust.py` → `business/stages/ingestion/trust.py`
- `backfill_transcript.py` → `business/stages/ingestion/backfill_transcript.py`
- `compress.py` → `business/stages/ingestion/compress.py`

### app/pipelines/ (3 files):

- `base_pipeline.py` → `business/pipelines/runner.py`
- `ingestion_pipeline.py` → `business/pipelines/ingestion.py`
- `graphrag_pipeline.py` → `business/pipelines/graphrag.py`

### app/services/ (20 files):

GraphRAG:

- `graphrag_indexes.py` → `business/services/graphrag/indexes.py`
- `graphrag_query.py` → `business/services/graphrag/query.py`
- `graphrag_retrieval.py` → `business/services/graphrag/retrieval.py`
- `graphrag_generation.py` → `business/services/graphrag/generation.py`

RAG:

- `generation.py` → `business/services/rag/generation.py`
- `retrieval.py` → `business/services/rag/retrieval.py`
- `indexes.py` → `business/services/rag/indexes.py`
- `rag.py` → `business/services/rag/core.py` (renamed)

Ingestion:

- `transcripts.py` → `business/services/ingestion/transcripts.py`
- `metadata.py` → `business/services/ingestion/metadata.py`

Infrastructure (→ DEPENDENCIES):

- `utils.py` → `dependencies/database/mongodb.py` (extract get_mongo_client)
- `rate_limit.py` → `dependencies/llm/rate_limit.py`
- `log_utils.py` → `dependencies/observability/logging.py`

Utilities (→ APP/BUSINESS):

- `filters.py` → `business/services/rag/filters.py`
- `feedback.py` → `business/services/rag/feedback.py`
- `persona_utils.py` → `business/services/rag/persona_utils.py`
- `profiles.py` → `business/services/rag/profiles.py`
- `ui_utils.py` → `app/ui/utils.py` (stays in APP)

To Review:

- `enhanced_graphrag_pipeline.py` → May archive to `documentation/examples/`
- `graphrag_mongodb_query.py` → Extract useful parts or archive

### app/queries/ (4 files):

- `vector_search.py` → `business/queries/vector_search.py`
- `llm_question.py` → `business/queries/llm_question.py`
- `get.py` → `business/queries/get.py`
- `videos_insights.py` → `business/queries/videos_insights.py`

### core/ (9 files):

Models:

- `graphrag_models.py` → `core/models/graphrag.py`

Base:

- `base_stage.py` → `core/base/stage.py`
- `base_agent.py` → `core/base/agent.py`

Domain:

- `text_utils.py` → `core/domain/text.py`
- `enrich_utils.py` → `core/domain/enrichment.py`
- `compression.py` → `core/domain/compression.py`
- `concurrency.py` → `core/domain/concurrency.py`

### config/ (4 files):

- `paths.py` → `core/config/paths.py`
- `runtime.py` → `core/config/runtime.py`
- `graphrag_config.py` → `core/config/graphrag.py`
- `stage_config.py` → `core/models/config.py`

### scripts/ (10 files):

GraphRAG:

- `analyze_graph_structure.py` → `app/scripts/graphrag/analyze_graph_structure.py`
- `test_random_chunks.py` → `app/scripts/graphrag/test_random_chunks.py`
- `run_random_chunk_test.py` → `app/scripts/graphrag/run_random_chunk_test.py`
- `diagnose_graphrag_communities.py` → `app/scripts/graphrag/diagnose_communities.py`
- `monitor_density.py` → `app/scripts/graphrag/monitor_density.py`
- `sample_graph_data.py` → `app/scripts/graphrag/sample_graph_data.py`
- `inspect_community_detection.py` → `app/scripts/graphrag/inspect_community_detection.py`
- `test_community_detection.py` → `app/scripts/graphrag/test_community_detection.py`

Utilities:

- `full_cleanup.py` → `app/scripts/utilities/full_cleanup.py`
- `check_graphrag_data.py` → `app/scripts/utilities/check_data.py`
- `create_indexes.py` → `app/scripts/utilities/create_indexes.py` (if exists)
- `validate_chunks.py` → `app/scripts/utilities/validate_chunks.py` (if exists)

---

## Next Steps:

### Phase 1: Move CORE Layer (2-3 hours)

**Status**: Ready to start

**Files to Move** (9 files):

1. Models:

   - `core/graphrag_models.py` → `core/models/graphrag.py`
   - `config/stage_config.py` → `core/models/config.py`

2. Base Classes:

   - `core/base_stage.py` → `core/base/stage.py`
   - `core/base_agent.py` → `core/base/agent.py`

3. Domain Utilities:

   - `core/text_utils.py` → `core/domain/text.py`
   - `core/enrich_utils.py` → `core/domain/enrichment.py`
   - `core/compression.py` → `core/domain/compression.py`
   - `core/concurrency.py` → `core/domain/concurrency.py`

4. Configuration:
   - `config/paths.py` → `core/config/paths.py`
   - `config/runtime.py` → `core/config/runtime.py`
   - `config/graphrag_config.py` → `core/config/graphrag.py`

**Verification Commands**:

```bash
python -c "from core.models.graphrag import EntityModel; print('OK')"
python -c "from core.base.stage import BaseStage; print('OK')"
python -c "from core.config.paths import DB_NAME; print('OK')"
```

---

## Migration Statistics:

**Total Files to Migrate**: ~100 files

- Agents: 12 files
- Stages: 13 files
- Pipelines: 3 files
- Services: 20 files
- Queries: 4 files
- Core: 9 files
- Config: 4 files
- Scripts: 10+ files
- Entry points: 4 files

**Total Import Statements to Update**: Estimated 500-1000

**Estimated Total Time**: 22-32 hours

---

**Status**: ✅ Phase 0 Complete - Ready for Phase 1
