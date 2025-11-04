# Folder Structure Refactor - Brainstorming & Research

**Date**: October 31, 2025  
**Goal**: Refactor project to follow clean layered architecture with clear separation of concerns

---

## Core Vision: 4-Layer Architecture

```
APP          → External interface, executables (entry points)
BUSINESS     → Implementation, process execution
CORE         → Fundamental definitions (models, classes, utilities)
DEPENDENCIES → Custom libraries extending third-party libs
```

**Dependency Rule**: Layers only depend downward (APP → BUSINESS → CORE → DEPENDENCIES)

**Alphabetical Benefit**: Easy visual identification of layer hierarchy

---

## Current Project Structure Analysis

### Current Root-Level Folders:

```
agents/           # LLM-powered intelligent components
app/              # Pipelines, stages, queries, services
config/           # Configuration management
core/             # Base classes, models, utilities
documentation/    # All documentation
scripts/          # Utility scripts, testing, diagnostics
```

### Current Files by Category:

**Entry Points (Executables)**:

- `main.py` - Main CLI entry point (ingestion pipeline)
- `run_graphrag_pipeline.py` - GraphRAG pipeline CLI
- `streamlit_app.py` - Streamlit UI
- `chat.py` - Chat interface

**Implementation**:

- `agents/` - GraphExtractionAgent, EntityResolutionAgent, etc.
- `app/stages/` - Pipeline stages (graph_extraction, entity_resolution, etc.)
- `app/pipelines/` - Pipeline orchestration
- `app/services/` - Business logic services
- `app/queries/` - Query implementations

**Core Definitions**:

- `core/` - BaseStage, BaseAgent, graphrag_models
- `config/` - Configuration classes

**Infrastructure**:

- `scripts/` - Testing and diagnostic utilities

---

## Research: Layered Architecture Best Practices

### 1. Clean Architecture (Uncle Bob)

**Layers** (outer to inner):

- **Frameworks & Drivers** (UI, DB, External interfaces)
- **Interface Adapters** (Controllers, Presenters, Gateways)
- **Application Business Rules** (Use cases, interactors)
- **Enterprise Business Rules** (Entities, domain models)

**Dependency Rule**: Source code dependencies point inward only

**Our Mapping**:

- APP = Frameworks & Drivers
- BUSINESS = Application Business Rules + Interface Adapters
- CORE = Enterprise Business Rules
- DEPENDENCIES = Infrastructure (but inverted!)

### 2. Hexagonal Architecture (Ports & Adapters)

**Layers**:

- **Application Core** (domain logic, ports)
- **Adapters** (primary: UI/API, secondary: DB/external services)

**Key Insight**: Core should not know about external details

**Our Mapping**:

- APP = Primary Adapters
- BUSINESS = Application Core
- CORE = Domain Models
- DEPENDENCIES = Secondary Adapters (infrastructure)

### 3. Domain-Driven Design (DDD)

**Layers**:

- **User Interface** (presentation)
- **Application Layer** (orchestration)
- **Domain Layer** (business logic)
- **Infrastructure Layer** (persistence, external services)

**Our Mapping**:

- APP = User Interface
- BUSINESS = Application Layer + Domain Layer
- CORE = Shared Kernel (cross-cutting concerns)
- DEPENDENCIES = Infrastructure

---

## Option 1: Pure Layered Architecture

```
YoutubeRAG/
├── app/                          # APP LAYER - Entry Points
│   ├── __init__.py
│   ├── main.py                   # Main CLI
│   ├── graphrag_pipeline_cli.py  # GraphRAG CLI
│   ├── streamlit_app.py          # Streamlit UI
│   ├── chat_cli.py               # Chat CLI
│   └── api/                      # Future: FastAPI endpoints
│       ├── __init__.py
│       ├── routes/
│       └── middleware/
│
├── business/                     # BUSINESS LAYER - Implementation
│   ├── __init__.py
│   ├── agents/                   # LLM-powered intelligent components
│   │   ├── __init__.py
│   │   ├── graph/                # GraphRAG agents
│   │   │   ├── extraction_agent.py
│   │   │   ├── entity_resolution_agent.py
│   │   │   ├── relationship_resolution_agent.py
│   │   │   ├── community_detection_agent.py
│   │   │   └── community_summarization_agent.py
│   │   └── ingestion/            # Ingestion agents
│   │       ├── clean_agent.py
│   │       ├── enrich_agent.py
│   │       └── trust_agent.py
│   │
│   ├── stages/                   # Pipeline stages
│   │   ├── __init__.py
│   │   ├── graph/                # GraphRAG stages
│   │   │   ├── graph_extraction.py
│   │   │   ├── entity_resolution.py
│   │   │   ├── graph_construction.py
│   │   │   └── community_detection.py
│   │   └── ingestion/            # Ingestion stages
│   │       ├── ingest.py
│   │       ├── clean.py
│   │       ├── chunk.py
│   │       ├── enrich.py
│   │       ├── embed.py
│   │       ├── redundancy.py
│   │       └── trust.py
│   │
│   ├── pipelines/                # Pipeline orchestration
│   │   ├── __init__.py
│   │   ├── base_pipeline.py
│   │   ├── ingestion_pipeline.py
│   │   └── graphrag_pipeline.py
│   │
│   ├── services/                 # Business logic services
│   │   ├── __init__.py
│   │   ├── graph/                # GraphRAG services
│   │   │   ├── graphrag_indexes.py
│   │   │   ├── graphrag_query.py
│   │   │   └── graphrag_retrieval.py
│   │   ├── ingestion/            # Ingestion services
│   │   │   ├── transcripts.py
│   │   │   └── metadata.py
│   │   └── rag/                  # RAG services
│   │       ├── generation.py
│   │       ├── retrieval.py
│   │       └── indexes.py
│   │
│   └── queries/                  # Query implementations
│       ├── __init__.py
│       ├── vector_search.py
│       └── llm_question.py
│
├── core/                         # CORE LAYER - Definitions
│   ├── __init__.py
│   ├── models/                   # Domain models
│   │   ├── __init__.py
│   │   ├── graphrag_models.py    # GraphRAG Pydantic models
│   │   └── stage_config.py       # Configuration models
│   │
│   ├── base/                     # Base classes
│   │   ├── __init__.py
│   │   ├── base_stage.py
│   │   ├── base_agent.py
│   │   └── base_pipeline.py
│   │
│   ├── domain/                   # Domain logic (pure functions)
│   │   ├── __init__.py
│   │   ├── text_utils.py
│   │   ├── enrich_utils.py
│   │   └── compression.py
│   │
│   └── config/                   # Configuration
│       ├── __init__.py
│       ├── paths.py
│       ├── runtime.py
│       └── graphrag_config.py
│
├── dependencies/                 # DEPENDENCIES LAYER - Infrastructure
│   ├── __init__.py
│   ├── database/                 # Database adapters
│   │   ├── __init__.py
│   │   ├── mongodb_client.py
│   │   └── collection_manager.py
│   │
│   ├── llm/                      # LLM provider adapters
│   │   ├── __init__.py
│   │   ├── openai_client.py
│   │   └── rate_limiter.py
│   │
│   ├── external/                 # External API clients
│   │   ├── __init__.py
│   │   └── youtube_client.py
│   │
│   └── monitoring/               # Logging, tracing
│       ├── __init__.py
│       ├── logger.py
│       └── metrics.py
│
├── documentation/                # Documentation (unchanged)
├── scripts/                      # Utility scripts (unchanged)
├── tests/                        # Tests (mirror structure)
├── requirements.txt
├── README.md
└── .env.example
```

**Pros**:

- ✅ Pure layered architecture
- ✅ Clear separation of concerns
- ✅ Easy to understand dependencies
- ✅ Alphabetical ordering works perfectly

**Cons**:

- ⚠️ `business/` becomes very large
- ⚠️ Deep nesting (e.g., `business/agents/graph/extraction_agent.py`)

---

## Option 2: Hybrid (Layers + Feature Modules)

```
YoutubeRAG/
├── app/                          # APP LAYER
│   ├── cli/
│   │   ├── main.py
│   │   └── graphrag.py
│   ├── ui/
│   │   ├── streamlit_app.py
│   │   └── chat.py
│   └── api/                      # Future
│
├── business/                     # BUSINESS LAYER
│   ├── graphrag/                 # Feature: GraphRAG
│   │   ├── __init__.py
│   │   ├── agents/
│   │   ├── stages/
│   │   ├── pipeline.py
│   │   └── services/
│   │
│   ├── ingestion/                # Feature: Ingestion
│   │   ├── __init__.py
│   │   ├── agents/
│   │   ├── stages/
│   │   ├── pipeline.py
│   │   └── services/
│   │
│   └── rag/                      # Feature: RAG Query/Generation
│       ├── __init__.py
│       ├── queries/
│       ├── generation/
│       └── retrieval/
│
├── core/                         # CORE LAYER
│   ├── models/
│   ├── base/
│   ├── domain/
│   └── config/
│
└── dependencies/                 # DEPENDENCIES LAYER
    ├── database/
    ├── llm/
    ├── external/
    └── monitoring/
```

**Pros**:

- ✅ Grouped by feature (GraphRAG, Ingestion, RAG)
- ✅ Less nesting
- ✅ Easier to navigate within features

**Cons**:

- ⚠️ Breaks pure layering slightly (features span multiple concerns)
- ⚠️ May create circular dependencies if not careful

---

## Option 3: Vertical Slices (DDD-inspired)

```
YoutubeRAG/
├── app/                          # APP LAYER
│   ├── cli/
│   ├── ui/
│   └── api/
│
├── business/                     # BUSINESS LAYER
│   ├── contexts/                 # Bounded contexts (DDD)
│   │   ├── graph_knowledge/      # GraphRAG bounded context
│   │   │   ├── domain/
│   │   │   │   ├── models.py
│   │   │   │   └── services.py
│   │   │   ├── application/
│   │   │   │   ├── agents/
│   │   │   │   ├── stages/
│   │   │   │   └── pipeline.py
│   │   │   └── infrastructure/
│   │   │       └── indexes.py
│   │   │
│   │   ├── content_ingestion/    # Ingestion bounded context
│   │   │   ├── domain/
│   │   │   ├── application/
│   │   │   └── infrastructure/
│   │   │
│   │   └── intelligent_retrieval/ # RAG bounded context
│   │       ├── domain/
│   │       ├── application/
│   │       └── infrastructure/
│   │
│   └── shared/                   # Shared across contexts
│       └── pipeline_orchestration/
│
├── core/                         # CORE LAYER
│   └── shared_kernel/            # Shared across all contexts
│       ├── models/
│       ├── base/
│       └── utilities/
│
└── dependencies/                 # DEPENDENCIES LAYER
```

**Pros**:

- ✅ Aligns with DDD bounded contexts
- ✅ Each context is self-contained
- ✅ Clear domain boundaries

**Cons**:

- ⚠️ Most complex option
- ⚠️ May be over-engineered for current project size
- ⚠️ Shared concerns (pipelines) span contexts

---

## Option 4: Pragmatic Layered (Recommended Starting Point)

```
YoutubeRAG/
├── app/                          # APP LAYER - Entry Points
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py               # Ingestion pipeline CLI
│   │   └── graphrag.py           # GraphRAG pipeline CLI
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── streamlit_app.py
│   │   └── chat.py
│   │
│   └── api/                      # Future: REST API
│       └── __init__.py
│
├── business/                     # BUSINESS LAYER
│   ├── __init__.py
│   │
│   ├── agents/                   # Intelligent agents (all)
│   │   ├── __init__.py
│   │   ├── graphrag/
│   │   │   ├── graph_extraction_agent.py
│   │   │   ├── entity_resolution_agent.py
│   │   │   ├── relationship_resolution_agent.py
│   │   │   ├── community_detection_agent.py
│   │   │   └── community_summarization_agent.py
│   │   │
│   │   └── ingestion/
│   │       ├── clean_agent.py
│   │       ├── enrich_agent.py
│   │       └── trust_agent.py
│   │
│   ├── stages/                   # Pipeline stages (all)
│   │   ├── __init__.py
│   │   ├── graphrag/
│   │   │   ├── graph_extraction.py
│   │   │   ├── entity_resolution.py
│   │   │   ├── graph_construction.py
│   │   │   └── community_detection.py
│   │   │
│   │   └── ingestion/
│   │       ├── ingest.py
│   │       ├── clean.py
│   │       ├── chunk.py
│   │       ├── enrich.py
│   │       ├── embed.py
│   │       ├── redundancy.py
│   │       └── trust.py
│   │
│   ├── pipelines/                # Pipeline orchestration
│   │   ├── __init__.py
│   │   ├── runner.py             # PipelineRunner
│   │   ├── ingestion.py          # Ingestion pipeline
│   │   └── graphrag.py           # GraphRAG pipeline
│   │
│   ├── services/                 # Domain services
│   │   ├── __init__.py
│   │   ├── graphrag/
│   │   │   ├── indexes.py
│   │   │   ├── query.py
│   │   │   └── retrieval.py
│   │   │
│   │   ├── rag/
│   │   │   ├── generation.py
│   │   │   ├── retrieval.py
│   │   │   └── indexes.py
│   │   │
│   │   └── ingestion/
│   │       ├── transcripts.py
│   │       └── metadata.py
│   │
│   └── queries/                  # Query handlers
│       ├── __init__.py
│       ├── vector_search.py
│       └── llm_question.py
│
├── core/                         # CORE LAYER - Definitions
│   ├── __init__.py
│   │
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   ├── graphrag.py           # GraphRAG Pydantic models
│   │   └── config.py             # Configuration models
│   │
│   ├── base/                     # Base classes
│   │   ├── __init__.py
│   │   ├── stage.py              # BaseStage
│   │   ├── agent.py              # BaseAgent
│   │   └── pipeline.py           # BasePipeline
│   │
│   ├── domain/                   # Domain utilities
│   │   ├── __init__.py
│   │   ├── text.py
│   │   ├── enrichment.py
│   │   └── compression.py
│   │
│   └── config/                   # Configuration
│       ├── __init__.py
│       ├── paths.py
│       ├── runtime.py
│       └── graphrag.py
│
├── dependencies/                 # DEPENDENCIES LAYER - Infrastructure
│   ├── __init__.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── mongodb.py            # MongoDB client
│   │   └── collections.py        # Collection utilities
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── client.py             # OpenAI client
│   │   └── rate_limit.py
│   │
│   ├── external/
│   │   ├── __init__.py
│   │   └── youtube.py
│   │
│   └── observability/
│       ├── __init__.py
│       ├── logging.py
│       └── metrics.py
│
├── documentation/                # All documentation (unchanged)
│
├── scripts/                      # Utility scripts (unchanged)
│   ├── graphrag/                 # GraphRAG testing/diagnostics
│   └── general/                  # General utilities
│
├── tests/                        # Tests (mirror structure)
│   ├── app/
│   ├── business/
│   ├── core/
│   └── dependencies/
│
├── requirements.txt
├── README.md
└── .env.example
```

**Pros**:

- ✅ Balanced complexity
- ✅ Clear layering with practical organization
- ✅ Grouped by type (agents, stages, services) then by feature
- ✅ Easy to navigate and understand
- ✅ Room for growth

**Cons**:

- ⚠️ Still some nesting (but manageable)

---

## Dependency Flow Analysis

### Current Import Patterns:

**Example 1: GraphRAG Stage**

```python
# Current (app/stages/graph_extraction.py)
from core.base_stage import BaseStage
from core.graphrag_models import EntityModel
from agents.graph_extraction_agent import GraphExtractionAgent
from config.graphrag_config import GraphExtractionConfig
```

**Example 2: Main CLI**

```python
# Current (main.py)
from app.pipelines.ingestion_pipeline import IngestionPipeline
from app.services.utils import get_mongo_client
```

### After Refactor (Option 4):

**Example 1: GraphRAG Stage**

```python
# business/stages/graphrag/graph_extraction.py
from core.base.stage import BaseStage
from core.models.graphrag import EntityModel
from business.agents.graphrag.graph_extraction_agent import GraphExtractionAgent
from core.config.graphrag import GraphExtractionConfig
```

**Example 2: Main CLI**

```python
# app/cli/main.py
from business.pipelines.ingestion import IngestionPipeline
from dependencies.database.mongodb import get_client
```

**Dependency Direction**: ✅ All pointing downward!

```
app/cli/main.py
    ↓
business/pipelines/ingestion.py
    ↓
business/stages/ingestion/clean.py
    ↓
business/agents/ingestion/clean_agent.py
    ↓
core/base/stage.py
    ↓
core/models/config.py
    ↓
dependencies/database/mongodb.py
```

---

## Key Design Decisions

### 1. Where do Agents belong?

**Option A**: `business/agents/` (Recommended)

- Agents are implementation (use LLM, have business logic)
- They're invoked by stages (same layer)

**Option B**: `core/agents/`

- Agents could be seen as "core business logic"
- But they have external dependencies (LLM client)

**Decision**: `business/agents/` ✅

---

### 2. Where do Stages belong?

**Option A**: `business/stages/` (Recommended)

- Stages orchestrate agents and services
- They're part of pipeline execution

**Option B**: Split between `business/` and `core/`

- Base classes in `core/base/`
- Implementations in `business/stages/`

**Decision**: Implementations in `business/stages/`, bases in `core/base/` ✅

---

### 3. Where do Services belong?

**Option A**: `business/services/` (Recommended)

- Services contain domain logic
- They're invoked by stages and queries

**Option B**: Split services by infrastructure concern

- Database services → `dependencies/database/services/`
- LLM services → `dependencies/llm/services/`

**Decision**: `business/services/` for domain logic, `dependencies/` for infrastructure ✅

---

### 4. Where does Configuration belong?

**Option A**: `core/config/` (Recommended)

- Configuration is fundamental to all layers
- Config classes define structure

**Option B**: `dependencies/config/`

- Configuration loads from environment (infrastructure concern)

**Decision**: `core/config/` for models, `dependencies/` for loaders if needed ✅

---

### 5. What goes in `dependencies/`?

**Infrastructure Concerns**:

- ✅ Database clients (MongoDB, Redis, etc.)
- ✅ LLM provider clients (OpenAI, Anthropic, etc.)
- ✅ External API clients (YouTube, etc.)
- ✅ Logging and monitoring
- ✅ Rate limiting

**NOT Infrastructure**:

- ❌ Business logic
- ❌ Domain models
- ❌ Pipeline orchestration

---

## GraphRAG-Specific Considerations

### GraphRAG Components in New Structure:

**Models** → `core/models/graphrag.py`

- EntityModel, RelationshipModel, KnowledgeModel, etc.

**Agents** → `business/agents/graphrag/`

- graph_extraction_agent.py
- entity_resolution_agent.py
- relationship_resolution_agent.py
- community_detection_agent.py
- community_summarization_agent.py

**Stages** → `business/stages/graphrag/`

- graph_extraction.py
- entity_resolution.py
- graph_construction.py
- community_detection.py

**Services** → `business/services/graphrag/`

- indexes.py
- query.py
- retrieval.py

**Configuration** → `core/config/graphrag.py`

- GraphExtractionConfig, EntityResolutionConfig, etc.

**Pipeline** → `business/pipelines/graphrag.py`

- GraphRAGPipeline class

**Entry Point** → `app/cli/graphrag.py`

- CLI interface (run_graphrag_pipeline.py content)

---

## Migration Strategy

### Phase 1: Create New Structure (Empty)

1. Create all folders
2. Add `__init__.py` files
3. No code movement yet

### Phase 2: Move Core Layer

1. Move `core/` → New structure
2. Update imports in moved files
3. Test: Ensure core still importable

### Phase 3: Move Dependencies Layer

1. Extract infrastructure code
2. Create adapters in `dependencies/`
3. Test: Database, LLM connections work

### Phase 4: Move Business Layer

1. Move agents → `business/agents/`
2. Move stages → `business/stages/`
3. Move pipelines → `business/pipelines/`
4. Move services → `business/services/`
5. Update all imports
6. Test: Pipelines run

### Phase 5: Move App Layer

1. Move entry points → `app/`
2. Update all imports
3. Test: All CLIs work

### Phase 6: Update Documentation

1. Update all code references in docs
2. Update README
3. Update GRAPH-RAG-CONSOLIDATED.md

---

## Testing Strategy

**Mirror Structure** in `tests/`:

```
tests/
├── app/
├── business/
│   ├── agents/
│   ├── stages/
│   └── services/
├── core/
└── dependencies/
```

**Test Dependency Flow**: Tests can import from any layer below

---

## Comparison Matrix

| Criteria            | Option 1   | Option 2 | Option 3   | Option 4   |
| ------------------- | ---------- | -------- | ---------- | ---------- |
| **Simplicity**      | ⭐⭐⭐     | ⭐⭐⭐⭐ | ⭐⭐       | ⭐⭐⭐⭐   |
| **Scalability**     | ⭐⭐⭐     | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐   |
| **Clarity**         | ⭐⭐⭐⭐   | ⭐⭐⭐   | ⭐⭐⭐     | ⭐⭐⭐⭐⭐ |
| **Maintainability** | ⭐⭐⭐     | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐   |
| **Learning Curve**  | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐       | ⭐⭐⭐⭐   |
| **Fits Vision**     | ⭐⭐⭐⭐   | ⭐⭐⭐   | ⭐⭐⭐     | ⭐⭐⭐⭐⭐ |

**Recommendation**: **Option 4 (Pragmatic Layered)** ✅

---

## Next Steps

1. **Review and Decide**: Choose architecture option
2. **Refine Details**: Adjust specific folder placements
3. **Create Migration Plan**: Detailed step-by-step
4. **Update Documentation**: Reflect new structure
5. **Execute Migration**: Careful, tested migration

---

## Questions for Discussion

1. **Layer Naming**: Happy with APP/BUSINESS/CORE/DEPENDENCIES? Alternatives:

   - `interface/application/domain/infrastructure` (DDD-style)
   - `presentation/logic/foundation/adapters`

2. **Feature Grouping**: Should agents/stages be grouped by feature first (graphrag/, ingestion/) or by type first (agents/, stages/)?

3. **Scripts Organization**: Keep `scripts/` at root or move to `app/scripts/`?

4. **Documentation**: Keep `documentation/` at root (current) or move docs closer to code?

5. **Tests**: Mirror structure or group by test type (unit, integration, e2e)?

---

**This brainstorm provides 4 concrete options with analysis. Ready to refine and choose!**
