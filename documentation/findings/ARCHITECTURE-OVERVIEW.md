# Architecture Overview - Current State

**Created**: November 6, 2025  
**Purpose**: Document current architecture understanding for code review context  
**Status**: Baseline for PLAN_CODE-QUALITY-REFACTOR.md

---

## Architecture Summary

**Architecture Type**: 4-Layer Clean Architecture with Domain Organization

**Layers** (top to bottom):

1. **APP** - External interface (CLIs, UIs, APIs, Scripts)
2. **BUSINESS** - Implementation (Agents, Stages, Services, Queries, Chat, Pipelines)
3. **CORE** - Definitions (Models, Base Classes, Libraries, Config)
4. **DEPENDENCIES** - Infrastructure (Database, LLM, External APIs, Observability)

**Dependency Rule**: Each layer only depends on layers below (APP → BUSINESS → CORE → DEPENDENCIES)

---

## Layer Details

### Layer 1: APP (External Interface)

**Purpose**: Anything that runs or talks to the external world

**Contains**:

- **CLIs** (`app/cli/`): Command-line interfaces
  - `main.py` - Ingestion pipeline CLI
  - `graphrag.py` - GraphRAG pipeline CLI
  - `chat.py` - Chat interface CLI
- **UIs** (`app/ui/`): User interfaces
  - `streamlit_app.py` - Streamlit dashboard
- **APIs** (`app/api/`): API endpoints
  - `metrics.py` - Metrics API endpoint
- **Scripts** (`app/scripts/`): Utility scripts
  - GraphRAG diagnostics and testing
  - Utilities and seeding

**Import Rule**: Can import from BUSINESS, CORE, DEPENDENCIES

**Files**: 24 files, ~5,690 lines

---

### Layer 2: BUSINESS (Implementation)

**Purpose**: Process execution, domain logic, orchestration

**Organization**: Type-first, then feature

**Contains**:

#### Agents (`business/agents/`)

- **GraphRAG** (6 files): extraction, entity_resolution, relationship_resolution, community_detection, community_summarization, link_prediction
- **Ingestion** (3 files): clean, enrich, trust
- **RAG** (3 files): reference_answer, topic_reference, planner

#### Stages (`business/stages/`)

- **GraphRAG** (4 files): extraction, entity_resolution, graph_construction, community_detection
- **Ingestion** (9 files): ingest, clean, chunk, enrich, embed, redundancy, trust, backfill, compress

#### Services (`business/services/`)

- **GraphRAG** (5 files): indexes, query, retrieval, generation, run_metadata
- **Ingestion** (2 files): transcripts, metadata
- **RAG** (8 files): core, generation, retrieval, indexes, filters, feedback, persona_utils, profiles
- **Chat** (3 files): filters, citations, export

#### Queries (`business/queries/`)

- **RAG** (4 files): vector_search, llm_question, get, videos_insights

#### Chat (`business/chat/`)

- **Modules** (4 files): memory, query_rewriter, retrieval, answering

#### Pipelines (`business/pipelines/`)

- **Core** (3 files): runner, ingestion, graphrag

**Import Rule**: Can import from CORE, DEPENDENCIES (NOT from APP)

**Files**: 70 files, ~19,533 lines

---

### Layer 3: CORE (Definitions)

**Purpose**: Fundamental contracts, models, base classes, libraries

**Contains**:

#### Models (`core/models/`)

- Pydantic models for data structures

#### Base Classes (`core/base/`)

- `BaseAgent` - Base class for all agents
- `BaseStage` - Base class for all stages

#### Domain Utilities (`core/domain/`)

- Domain-specific utilities

#### Configuration (`core/config/`)

- Configuration classes and loaders

#### Libraries (`core/libraries/`)

- **18 libraries** for cross-cutting concerns:
  - Tier 1: logging, error_handling, retry, metrics, tracing
  - Tier 2: validation, configuration, caching, database, llm, concurrency, rate_limiting, serialization, data_transform
  - Tier 3: health, context, di, feature_flags
  - Domain-specific: ontology

**Import Rule**: Can import from DEPENDENCIES (NOT from APP or BUSINESS)

**Files**: ~50+ files (models, base, domain, config, libraries)

---

### Layer 4: DEPENDENCIES (Infrastructure)

**Purpose**: Custom libraries extending third-party dependencies

**Contains**:

#### Database (`dependencies/database/`)

- MongoDB adapters and connection management

#### LLM (`dependencies/llm/`)

- LLM provider integrations (OpenAI, etc.)

#### External APIs (`dependencies/external/`)

- External API integrations

#### Observability (`dependencies/observability/`)

- Logging, monitoring, metrics infrastructure

**Import Rule**: Can only import third-party libraries (NOT from APP, BUSINESS, or CORE)

**Files**: ~10+ files

---

## Domain Organization

### GraphRAG Domain

**Purpose**: Knowledge graph extraction, entity resolution, relationship resolution, community detection

**Components**:

- **6 Agents**: extraction, entity_resolution, relationship_resolution, community_detection, community_summarization, link_prediction
- **4 Stages**: extraction, entity_resolution, graph_construction, community_detection
- **5 Services**: indexes, query, retrieval, generation, run_metadata

**Recent Changes** (from ACTIVE_PLANS.md):

- Entity resolution refactored (17/31 achievements)
- Graph construction refactored (11/17 achievements)
- Community detection refactored (14/23 achievements)
- Extraction quality enhanced (4/13 achievements)

**Status**: Most complex domain, significant recent work

---

### Ingestion Domain

**Purpose**: Video transcript ingestion, cleaning, chunking, enrichment, embedding

**Components**:

- **3 Agents**: clean, enrich, trust
- **9 Stages**: ingest, clean, chunk, enrich, embed, redundancy, trust, backfill, compress
- **2 Services**: transcripts, metadata

**Status**: Pipeline-heavy domain, many stages

---

### RAG Domain

**Purpose**: Retrieval-augmented generation, query handling, answer generation

**Components**:

- **3 Agents**: reference_answer, topic_reference, planner
- **8 Services**: core, generation, retrieval, indexes, filters, feedback, persona_utils, profiles
- **4 Queries**: vector_search, llm_question, get, videos_insights

**Status**: Service-heavy domain, query-focused

---

### Chat Domain

**Purpose**: Conversational interface, memory, query rewriting, answer generation

**Components**:

- **4 Modules**: memory, query_rewriter, retrieval, answering
- **3 Services**: filters, citations, export

**Status**: Smallest domain, recently extracted

---

## Dependency Flow

```
APP Layer
  ↓ imports
BUSINESS Layer
  ↓ imports
CORE Layer
  ↓ imports
DEPENDENCIES Layer
  ↓ imports
Third-party libraries
```

**Key Rules**:

- APP can import from BUSINESS, CORE, DEPENDENCIES
- BUSINESS can import from CORE, DEPENDENCIES (NOT APP)
- CORE can import from DEPENDENCIES (NOT APP or BUSINESS)
- DEPENDENCIES can only import third-party libraries

---

## Base Classes

### BaseAgent

**Location**: `core/base/base_agent.py` (assumed, needs verification)

**Purpose**: Base class for all LLM-powered agents

**Expected Features**:

- LLM client initialization
- Common agent methods
- Error handling
- Logging

**Usage**: All 12 agents should inherit from this

---

### BaseStage

**Location**: `core/base/base_stage.py` (assumed, needs verification)

**Purpose**: Base class for all pipeline stages

**Expected Features**:

- Stage execution framework
- Progress tracking
- Error handling
- Logging
- Metrics

**Usage**: All 13 stages should inherit from this

---

## Library Integration Points

### Current Integration

**Libraries Used**:

- `logging` - Used in 13 files
- `retry` - Used in 4 files
- `concurrency` - Used in 3 files
- `database` - Used in 2 files
- `rate_limiting` - Used in 2 files
- `ontology` - Used in 4 files

**Libraries Not Used**:

- `error_handling` - Complete but not applied
- `metrics` - Complete but not applied
- `validation` - Partial, not used
- `configuration` - Partial, not used
- `caching` - Partial, not used
- `llm` - Stub only
- Others (stubs)

### Integration Opportunities

**BaseAgent Should Use**:

- `error_handling` - Standardize error handling
- `retry` - Already used, but could be enhanced
- `logging` - Already used, but could be enhanced
- `llm` - When implemented, standardize LLM calls

**BaseStage Should Use**:

- `error_handling` - Standardize error handling
- `logging` - Already used, but could be enhanced
- `metrics` - Track stage execution
- `validation` - Validate stage inputs/outputs

---

## Recent Architecture Changes

### From ACTIVE_PLANS.md (November 6, 2025)

**Completed Refactoring**:

- Folder structure refactor (October 2025) - 4-layer architecture established
- GraphRAG domain refactoring (entity resolution, graph construction, community detection)
- Structured LLM development methodology established

**Paused Plans** (affecting architecture):

- PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md - GraphRAG extraction
- PLAN_ENTITY-RESOLUTION-REFACTOR.md - GraphRAG entity resolution
- PLAN_GRAPH-CONSTRUCTION-REFACTOR.md - GraphRAG graph construction
- PLAN_COMMUNITY-DETECTION-REFACTOR.md - GraphRAG community detection

**Impact**: GraphRAG domain has received significant refactoring. These changes should be considered when reviewing for library extraction opportunities.

---

## Architecture Principles

1. **Layer Separation**: Clear boundaries between layers
2. **Dependency Direction**: Dependencies flow downward only
3. **Domain Organization**: Type-first, then feature
4. **Library Reuse**: Cross-cutting concerns in libraries
5. **Base Classes**: Common functionality in base classes

---

## Architecture Strengths

✅ **Clear Layer Separation**: 4-layer architecture is well-defined  
✅ **Domain Organization**: Type-first organization is clear  
✅ **Library Structure**: 18 libraries identified and organized  
✅ **Base Classes**: BaseAgent and BaseStage provide common functionality

---

## Architecture Improvement Opportunities

⚠️ **Library Usage**: Many libraries exist but aren't used  
⚠️ **Base Class Integration**: Base classes could use more libraries  
⚠️ **Consistency**: Different domains solve similar problems differently  
⚠️ **Documentation**: Architecture documentation could be more comprehensive

---

## Notes for Code Review

1. **Check Layer Compliance**: Verify imports follow layer rules
2. **Check Base Class Usage**: Verify agents/stages use base classes properly
3. **Check Library Usage**: Identify opportunities to use existing libraries
4. **Check Domain Patterns**: Identify patterns that could be extracted to libraries
5. **Check Consistency**: Ensure similar problems are solved consistently

---

**Last Updated**: November 6, 2025
