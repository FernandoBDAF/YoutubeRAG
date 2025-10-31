# Folder Structure Refactor - Final Implementation Plan

**Date**: October 31, 2025  
**Architecture**: Custom Pragmatic Layered (Type-First, Feature-Aware)  
**Based on**: User preferences combining Hybrid and Pragmatic approaches

---

## Core Principles

### 1. Layer Naming (User Preference)

✅ **APP** - External interface, executables, anything that runs or talks to external world  
✅ **BUSINESS** - Implementation, process execution, domain logic  
✅ **CORE** - Fundamental definitions (models, base classes, utilities)  
✅ **DEPENDENCIES** - Custom libraries extending third-party dependencies

### 2. Organization Strategy (User Preference)

✅ **Type-First**: Organize by component type (agents/, stages/, services/)  
✅ **Feature-Aware**: Within types, group by feature (graphrag/, ingestion/) where beneficial  
✅ **GraphRAG-Centric**: Everything evolves toward GraphRAG knowledge management

### 3. Dependency Rule (Strict)

```
APP → BUSINESS → CORE → DEPENDENCIES
(Each layer only depends on layers below)
```

### 4. Runnable Code Location (User Preference)

✅ **Anything runnable or that talks to external world → APP layer**

- CLIs → `app/cli/`
- UIs → `app/ui/`
- Scripts → `app/scripts/`
- APIs → `app/api/` (future)

---

## Final Folder Structure

```
YoutubeRAG/
│
├── app/                                    # APP LAYER - External Interface
│   ├── __init__.py
│   │
│   ├── cli/                                # Command-line interfaces
│   │   ├── __init__.py
│   │   ├── main.py                         # Ingestion pipeline CLI
│   │   └── graphrag.py                     # GraphRAG pipeline CLI
│   │
│   ├── ui/                                 # User interfaces
│   │   ├── __init__.py
│   │   ├── streamlit_app.py                # Streamlit dashboard
│   │   └── chat.py                         # Chat interface
│   │
│   ├── api/                                # REST API (future MCP server)
│   │   ├── __init__.py
│   │   ├── server.py                       # FastAPI server
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── knowledge.py                # Knowledge graph endpoints
│   │   │   ├── query.py                    # Query endpoints
│   │   │   └── health.py                   # Health check
│   │   └── middleware/
│   │       ├── __init__.py
│   │       └── auth.py
│   │
│   └── scripts/                            # Runnable utility scripts
│       ├── __init__.py
│       ├── graphrag/                       # GraphRAG testing/diagnostics
│       │   ├── __init__.py
│       │   ├── test_random_chunks.py
│       │   ├── analyze_graph_structure.py
│       │   ├── diagnose_communities.py
│       │   ├── monitor_density.py
│       │   └── sample_graph_data.py
│       │
│       └── utilities/                      # General utilities
│           ├── __init__.py
│           ├── full_cleanup.py
│           └── check_data.py
│
├── business/                               # BUSINESS LAYER - Implementation
│   ├── __init__.py
│   │
│   ├── agents/                             # Intelligent agents (LLM-powered)
│   │   ├── __init__.py
│   │   │
│   │   ├── graphrag/                       # GraphRAG agents
│   │   │   ├── __init__.py
│   │   │   ├── extraction.py               # GraphExtractionAgent
│   │   │   ├── entity_resolution.py        # EntityResolutionAgent
│   │   │   ├── relationship_resolution.py  # RelationshipResolutionAgent
│   │   │   ├── community_detection.py      # CommunityDetectionAgent
│   │   │   ├── community_summarization.py  # CommunitySummarizationAgent
│   │   │   └── link_prediction.py          # GraphLinkPredictionAgent
│   │   │
│   │   └── ingestion/                      # Ingestion agents
│   │       ├── __init__.py
│   │       ├── clean.py                    # CleanAgent
│   │       ├── enrich.py                   # EnrichAgent
│   │       └── trust.py                    # TrustAgent
│   │
│   ├── stages/                             # Pipeline stages
│   │   ├── __init__.py
│   │   │
│   │   ├── graphrag/                       # GraphRAG stages
│   │   │   ├── __init__.py
│   │   │   ├── extraction.py               # GraphExtractionStage
│   │   │   ├── entity_resolution.py        # EntityResolutionStage
│   │   │   ├── graph_construction.py       # GraphConstructionStage
│   │   │   └── community_detection.py      # CommunityDetectionStage
│   │   │
│   │   └── ingestion/                      # Ingestion stages
│   │       ├── __init__.py
│   │       ├── ingest.py                   # IngestStage
│   │       ├── clean.py                    # CleanStage
│   │       ├── chunk.py                    # ChunkStage
│   │       ├── enrich.py                   # EnrichStage
│   │       ├── embed.py                    # EmbedStage
│   │       ├── redundancy.py               # RedundancyStage
│   │       └── trust.py                    # TrustStage
│   │
│   ├── pipelines/                          # Pipeline orchestration
│   │   ├── __init__.py
│   │   ├── runner.py                       # PipelineRunner (orchestrator)
│   │   ├── ingestion.py                    # IngestionPipeline
│   │   └── graphrag.py                     # GraphRAGPipeline
│   │
│   ├── services/                           # Domain services
│   │   ├── __init__.py
│   │   │
│   │   ├── graphrag/                       # GraphRAG services
│   │   │   ├── __init__.py
│   │   │   ├── indexes.py                  # GraphRAG index management
│   │   │   ├── query.py                    # GraphRAG query processing
│   │   │   ├── retrieval.py                # GraphRAG retrieval
│   │   │   └── generation.py               # GraphRAG generation
│   │   │
│   │   ├── rag/                            # Traditional RAG services
│   │   │   ├── __init__.py
│   │   │   ├── generation.py               # Answer generation
│   │   │   ├── retrieval.py                # Vector retrieval
│   │   │   └── indexes.py                  # Vector index management
│   │   │
│   │   └── ingestion/                      # Ingestion services
│   │       ├── __init__.py
│   │       ├── transcripts.py              # Transcript fetching
│   │       └── metadata.py                 # Metadata extraction
│   │
│   └── queries/                            # Query handlers
│       ├── __init__.py
│       ├── vector_search.py                # Vector search queries
│       ├── graph_search.py                 # Graph-based queries
│       └── hybrid_search.py                # Hybrid queries
│
├── core/                                   # CORE LAYER - Definitions
│   ├── __init__.py
│   │
│   ├── models/                             # Data models (Pydantic)
│   │   ├── __init__.py
│   │   ├── graphrag.py                     # GraphRAG models (Entity, Relationship, etc.)
│   │   ├── config.py                       # Configuration models
│   │   └── stage_config.py                 # Stage configuration base
│   │
│   ├── base/                               # Base classes
│   │   ├── __init__.py
│   │   ├── stage.py                        # BaseStage
│   │   ├── agent.py                        # BaseAgent
│   │   └── pipeline.py                     # BasePipeline (if needed)
│   │
│   ├── domain/                             # Domain utilities (pure functions)
│   │   ├── __init__.py
│   │   ├── text.py                         # Text processing utilities
│   │   ├── enrichment.py                   # Enrichment utilities
│   │   ├── compression.py                  # Compression utilities
│   │   └── concurrency.py                  # Concurrency helpers
│   │
│   └── config/                             # Configuration management
│       ├── __init__.py
│       ├── paths.py                        # Path constants
│       ├── runtime.py                      # Runtime configuration
│       └── graphrag.py                     # GraphRAG configuration classes
│
├── dependencies/                           # DEPENDENCIES LAYER - Infrastructure
│   ├── __init__.py
│   │
│   ├── database/                           # Database adapters
│   │   ├── __init__.py
│   │   ├── mongodb.py                      # MongoDB client wrapper
│   │   └── collections.py                  # Collection utilities
│   │
│   ├── llm/                                # LLM provider adapters
│   │   ├── __init__.py
│   │   ├── openai.py                       # OpenAI client wrapper
│   │   ├── rate_limit.py                   # Rate limiting
│   │   └── retry.py                        # Retry logic
│   │
│   ├── external/                           # External API clients
│   │   ├── __init__.py
│   │   ├── youtube.py                      # YouTube API client
│   │   └── embedding.py                    # Embedding service client
│   │
│   └── observability/                      # Logging, monitoring, tracing
│       ├── __init__.py
│       ├── logging.py                      # Logging setup
│       ├── metrics.py                      # Metrics collection
│       └── tracing.py                      # Distributed tracing (future)
│
├── documentation/                          # Documentation (at root)
│   ├── README.md                           # Main documentation index
│   ├── GRAPH-RAG-CONSOLIDATED.md           # GraphRAG technical guide
│   ├── GRAPHRAG-ARTICLE-GUIDE.md           # GraphRAG articles
│   ├── GRAPHRAG-CONFIG-REFERENCE.md        # Configuration reference
│   │
│   ├── architecture/                       # Architecture docs
│   │   ├── PIPELINE.md
│   │   ├── STAGE.md
│   │   ├── AGENT.md
│   │   ├── SERVICE.md
│   │   └── CORE.md
│   │
│   ├── guides/                             # User guides
│   │   ├── DEPLOYMENT.md
│   │   ├── TESTING.md
│   │   ├── EXECUTION.md
│   │   └── MCP-SERVER.md
│   │
│   ├── context/                            # LLM context files (inline docs)
│   │   ├── app-layer.md                    # APP layer overview
│   │   ├── business-layer.md               # BUSINESS layer overview
│   │   ├── core-layer.md                   # CORE layer overview
│   │   └── dependencies-layer.md           # DEPENDENCIES layer overview
│   │
│   └── archive/                            # Historical documentation
│       └── graphrag-implementation/
│
├── tests/                                  # Tests (mirror structure)
│   ├── __init__.py
│   ├── app/
│   │   ├── cli/
│   │   ├── ui/
│   │   └── scripts/
│   ├── business/
│   │   ├── agents/
│   │   ├── stages/
│   │   ├── pipelines/
│   │   └── services/
│   ├── core/
│   │   ├── models/
│   │   ├── base/
│   │   └── domain/
│   └── dependencies/
│       ├── database/
│       ├── llm/
│       └── external/
│
├── .env.example                            # Environment variables template
├── .gitignore
├── requirements.txt                        # Python dependencies
├── README.md                               # Project README
└── mongodb_schema.json                     # MongoDB schema definitions
```

---

## File Naming Conventions

### Current → New Mapping:

**Agents**:

- `graph_extraction_agent.py` → `business/agents/graphrag/extraction.py`
- `entity_resolution_agent.py` → `business/agents/graphrag/entity_resolution.py`
- `clean_agent.py` → `business/agents/ingestion/clean.py`

**Stages**:

- `graph_extraction.py` → `business/stages/graphrag/extraction.py`
- `clean.py` → `business/stages/ingestion/clean.py`

**Rationale**: Drop redundant suffixes (`_agent`, `_stage`) since folder already indicates type

---

## Layer Responsibilities

### APP Layer - External Interface

**Purpose**: Connect to external world, provide entry points

**Contains**:

- ✅ CLI applications (argparse, commands)
- ✅ UI applications (Streamlit, Flask, etc.)
- ✅ API servers (FastAPI, MCP server)
- ✅ Executable scripts (testing, diagnostics)

**Does NOT Contain**:

- ❌ Business logic
- ❌ Domain models
- ❌ Database logic

**Example**:

```python
# app/cli/graphrag.py
from business.pipelines.graphrag import GraphRAGPipeline
from core.config.graphrag import GraphRAGPipelineConfig

def main():
    config = GraphRAGPipelineConfig.from_args_env(args, env, db)
    pipeline = GraphRAGPipeline(config)
    pipeline.run_full_pipeline()
```

---

### BUSINESS Layer - Implementation

**Purpose**: Execute processes, orchestrate domain logic

**Contains**:

- ✅ Agents (LLM-powered intelligence)
- ✅ Stages (pipeline processing units)
- ✅ Pipelines (orchestration)
- ✅ Services (domain logic)
- ✅ Queries (query handlers)

**Does NOT Contain**:

- ❌ Entry points (CLIs, UIs)
- ❌ Infrastructure code (DB clients, LLM clients)
- ❌ Base class definitions

**Example**:

```python
# business/stages/graphrag/extraction.py
from core.base.stage import BaseStage
from core.models.graphrag import EntityModel
from business.agents.graphrag.extraction import GraphExtractionAgent
from dependencies.database.mongodb import get_client

class GraphExtractionStage(BaseStage):
    def setup(self):
        self.agent = GraphExtractionAgent(...)
```

---

### CORE Layer - Definitions

**Purpose**: Define fundamental contracts, models, utilities

**Contains**:

- ✅ Pydantic models (data structures)
- ✅ Base classes (BaseStage, BaseAgent)
- ✅ Pure utility functions
- ✅ Configuration classes

**Does NOT Contain**:

- ❌ Implementation logic
- ❌ External dependencies
- ❌ Infrastructure code

**Example**:

```python
# core/models/graphrag.py
from pydantic import BaseModel, Field

class EntityModel(BaseModel):
    name: str = Field(...)
    type: EntityType = Field(...)
    description: str = Field(...)
    confidence: float = Field(ge=0.0, le=1.0)
```

---

### DEPENDENCIES Layer - Infrastructure

**Purpose**: Abstract external dependencies, provide adapters

**Contains**:

- ✅ Database clients/adapters
- ✅ LLM provider wrappers
- ✅ External API clients
- ✅ Logging/monitoring setup

**Does NOT Contain**:

- ❌ Business logic
- ❌ Domain models
- ❌ Pipeline orchestration

**Example**:

```python
# dependencies/database/mongodb.py
from pymongo import MongoClient

class MongoDBClient:
    """Wrapper around PyMongo with app-specific logic."""

    def __init__(self, uri: str):
        self._client = MongoClient(uri)

    def get_collection(self, db_name: str, coll_name: str):
        return self._client[db_name][coll_name]
```

---

## Import Patterns

### Allowed Import Directions:

```
APP
  ↓ can import
BUSINESS
  ↓ can import
CORE
  ↓ can import
DEPENDENCIES
```

### Example Import Chains:

**1. CLI → Pipeline → Stage → Agent → Base → Model → DB Client**

```python
# app/cli/graphrag.py
from business.pipelines.graphrag import GraphRAGPipeline  # ✅

# business/pipelines/graphrag.py
from business.stages.graphrag.extraction import GraphExtractionStage  # ✅
from core.config.graphrag import GraphRAGPipelineConfig  # ✅

# business/stages/graphrag/extraction.py
from business.agents.graphrag.extraction import GraphExtractionAgent  # ✅
from core.base.stage import BaseStage  # ✅
from dependencies.database.mongodb import MongoDBClient  # ✅

# business/agents/graphrag/extraction.py
from core.models.graphrag import EntityModel  # ✅
from dependencies.llm.openai import OpenAIClient  # ✅

# core/base/stage.py
from core.models.config import BaseStageConfig  # ✅

# dependencies/database/mongodb.py
from pymongo import MongoClient  # ✅ (external library)
```

**2. Forbidden Imports** ❌:

```python
# core/models/graphrag.py
from business.agents.graphrag.extraction import GraphExtractionAgent  # ❌ Core → Business

# dependencies/database/mongodb.py
from business.services.graphrag.indexes import ensure_indexes  # ❌ Dependencies → Business

# business/stages/graphrag/extraction.py
from app.cli.graphrag import parse_args  # ❌ Business → App
```

---

## GraphRAG Component Mapping

### Current Location → New Location:

| Current                                   | New                                                   | Layer    |
| ----------------------------------------- | ----------------------------------------------------- | -------- |
| `agents/graph_extraction_agent.py`        | `business/agents/graphrag/extraction.py`              | BUSINESS |
| `agents/entity_resolution_agent.py`       | `business/agents/graphrag/entity_resolution.py`       | BUSINESS |
| `agents/relationship_resolution_agent.py` | `business/agents/graphrag/relationship_resolution.py` | BUSINESS |
| `agents/community_detection_agent.py`     | `business/agents/graphrag/community_detection.py`     | BUSINESS |
| `agents/community_summarization_agent.py` | `business/agents/graphrag/community_summarization.py` | BUSINESS |
| `agents/graph_link_prediction_agent.py`   | `business/agents/graphrag/link_prediction.py`         | BUSINESS |
| `app/stages/graph_extraction.py`          | `business/stages/graphrag/extraction.py`              | BUSINESS |
| `app/stages/entity_resolution.py`         | `business/stages/graphrag/entity_resolution.py`       | BUSINESS |
| `app/stages/graph_construction.py`        | `business/stages/graphrag/graph_construction.py`      | BUSINESS |
| `app/stages/community_detection.py`       | `business/stages/graphrag/community_detection.py`     | BUSINESS |
| `app/pipelines/graphrag_pipeline.py`      | `business/pipelines/graphrag.py`                      | BUSINESS |
| `app/services/graphrag_indexes.py`        | `business/services/graphrag/indexes.py`               | BUSINESS |
| `app/services/graphrag_query.py`          | `business/services/graphrag/query.py`                 | BUSINESS |
| `app/services/graphrag_retrieval.py`      | `business/services/graphrag/retrieval.py`             | BUSINESS |
| `core/graphrag_models.py`                 | `core/models/graphrag.py`                             | CORE     |
| `config/graphrag_config.py`               | `core/config/graphrag.py`                             | CORE     |
| `config/stage_config.py`                  | `core/models/config.py`                               | CORE     |
| `core/base_stage.py`                      | `core/base/stage.py`                                  | CORE     |
| `core/base_agent.py`                      | `core/base/agent.py`                                  | CORE     |
| `run_graphrag_pipeline.py`                | `app/cli/graphrag.py`                                 | APP      |
| `scripts/analyze_graph_structure.py`      | `app/scripts/graphrag/analyze_graph_structure.py`     | APP      |
| `scripts/test_random_chunks.py`           | `app/scripts/graphrag/test_random_chunks.py`          | APP      |

---

## Migration Strategy (Detailed 10-Phase Plan)

### Phase 0: Preparation (1 hour)

**Goal**: Prepare for migration without breaking anything

1. **Create Migration Branch**:

   ```bash
   git checkout -b refactor/folder-structure
   ```

2. **Backup Current State**:

   ```bash
   git tag pre-refactor-backup
   ```

3. **Document Current Imports**:

   - Run grep to find all import statements
   - Create import dependency graph
   - Identify circular dependencies (if any)

4. **Create Empty Structure**:

   ```bash
   mkdir -p app/{cli,ui,api,scripts/{graphrag,utilities}}
   mkdir -p business/{agents/{graphrag,ingestion},stages/{graphrag,ingestion},pipelines,services/{graphrag,rag,ingestion},queries}
   mkdir -p core/{models,base,domain,config}
   mkdir -p dependencies/{database,llm,external,observability}
   mkdir -p tests/{app,business,core,dependencies}
   ```

5. **Add All `__init__.py` Files**:
   ```bash
   find app business core dependencies tests -type d -exec touch {}/__init__.py \;
   ```

**Verification**: Structure created, no code moved yet

---

### Phase 1: Move CORE Layer (2-3 hours)

**Goal**: Move foundation without breaking business logic

**1.1. Move Models**:

```bash
# Current → New
core/graphrag_models.py → core/models/graphrag.py
config/stage_config.py → core/models/config.py
```

**1.2. Move Base Classes**:

```bash
core/base_stage.py → core/base/stage.py
core/base_agent.py → core/base/agent.py
core/base_pipeline.py → core/base/pipeline.py  # If exists
```

**1.3. Move Domain Utilities**:

```bash
core/text_utils.py → core/domain/text.py
core/enrich_utils.py → core/domain/enrichment.py
core/compression.py → core/domain/compression.py
core/concurrency.py → core/domain/concurrency.py
```

**1.4. Move Configuration**:

```bash
config/paths.py → core/config/paths.py
config/runtime.py → core/config/runtime.py
config/graphrag_config.py → core/config/graphrag.py
```

**1.5. Update Imports in Moved Files**:

```python
# Before
from core.graphrag_models import EntityModel

# After
from core.models.graphrag import EntityModel
```

**Verification**:

```bash
python -c "from core.models.graphrag import EntityModel; print('OK')"
python -c "from core.base.stage import BaseStage; print('OK')"
```

---

### Phase 2: Extract DEPENDENCIES Layer (2-3 hours)

**Goal**: Abstract infrastructure before moving business logic

**2.1. Create Database Adapter**:

```python
# dependencies/database/mongodb.py
from pymongo import MongoClient
from core.config.paths import MONGODB_URI

class MongoDBClient:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = MongoClient(MONGODB_URI)
        return cls._instance
```

**2.2. Create LLM Adapter**:

```python
# dependencies/llm/openai.py
from openai import OpenAI
import os

class OpenAIClient:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        return cls._instance
```

**2.3. Move Existing Infrastructure Code**:

```bash
app/services/utils.py → dependencies/database/mongodb.py  # get_mongo_client
app/services/rate_limit.py → dependencies/llm/rate_limit.py
```

**2.4. Create Logging Setup**:

```python
# dependencies/observability/logging.py
import logging
import sys

def setup_logging(level=logging.INFO):
    # Current logging setup from main.py
    ...
```

**Verification**:

```bash
python -c "from dependencies.database.mongodb import MongoDBClient; print('OK')"
python -c "from dependencies.llm.openai import OpenAIClient; print('OK')"
```

---

### Phase 3: Move BUSINESS Layer - Agents (1-2 hours)

**Goal**: Move agent implementations

**3.1. Move GraphRAG Agents**:

```bash
agents/graph_extraction_agent.py → business/agents/graphrag/extraction.py
agents/entity_resolution_agent.py → business/agents/graphrag/entity_resolution.py
agents/relationship_resolution_agent.py → business/agents/graphrag/relationship_resolution.py
agents/community_detection_agent.py → business/agents/graphrag/community_detection.py
agents/community_summarization_agent.py → business/agents/graphrag/community_summarization.py
agents/graph_link_prediction_agent.py → business/agents/graphrag/link_prediction.py
```

**3.2. Move Ingestion Agents**:

```bash
agents/clean_agent.py → business/agents/ingestion/clean.py
agents/enrich_agent.py → business/agents/ingestion/enrich.py
agents/trust_agent.py → business/agents/ingestion/trust.py
```

**3.3. Update Imports in Agents**:

```python
# Before
from core.base_agent import BaseAgent
from core.graphrag_models import EntityModel

# After
from core.base.agent import BaseAgent
from core.models.graphrag import EntityModel
from dependencies.llm.openai import OpenAIClient
```

**Verification**:

```bash
python -c "from business.agents.graphrag.extraction import GraphExtractionAgent; print('OK')"
```

---

### Phase 4: Move BUSINESS Layer - Stages (2-3 hours)

**Goal**: Move stage implementations

**4.1. Move GraphRAG Stages**:

```bash
app/stages/graph_extraction.py → business/stages/graphrag/extraction.py
app/stages/entity_resolution.py → business/stages/graphrag/entity_resolution.py
app/stages/graph_construction.py → business/stages/graphrag/graph_construction.py
app/stages/community_detection.py → business/stages/graphrag/community_detection.py
```

**4.2. Move Ingestion Stages**:

```bash
app/stages/ingest.py → business/stages/ingestion/ingest.py
app/stages/clean.py → business/stages/ingestion/clean.py
app/stages/chunk.py → business/stages/ingestion/chunk.py
app/stages/enrich.py → business/stages/ingestion/enrich.py
app/stages/embed.py → business/stages/ingestion/embed.py
app/stages/redundancy.py → business/stages/ingestion/redundancy.py
app/stages/trust.py → business/stages/ingestion/trust.py
```

**4.3. Update Imports in Stages**:

```python
# Before
from core.base_stage import BaseStage
from agents.graph_extraction_agent import GraphExtractionAgent
from config.graphrag_config import GraphExtractionConfig

# After
from core.base.stage import BaseStage
from business.agents.graphrag.extraction import GraphExtractionAgent
from core.config.graphrag import GraphExtractionConfig
from dependencies.database.mongodb import MongoDBClient
```

**Verification**:

```bash
python -c "from business.stages.graphrag.extraction import GraphExtractionStage; print('OK')"
```

---

### Phase 5: Move BUSINESS Layer - Pipelines & Services (2-3 hours)

**Goal**: Move orchestration and domain services

**5.1. Move Pipelines**:

```bash
app/pipelines/base_pipeline.py → business/pipelines/runner.py
app/pipelines/ingestion_pipeline.py → business/pipelines/ingestion.py
app/pipelines/graphrag_pipeline.py → business/pipelines/graphrag.py
```

**5.2. Move Services**:

```bash
app/services/graphrag_indexes.py → business/services/graphrag/indexes.py
app/services/graphrag_query.py → business/services/graphrag/query.py
app/services/graphrag_retrieval.py → business/services/graphrag/retrieval.py
app/services/generation.py → business/services/rag/generation.py
app/services/retrieval.py → business/services/rag/retrieval.py
app/services/indexes.py → business/services/rag/indexes.py
app/services/transcripts.py → business/services/ingestion/transcripts.py
app/services/metadata.py → business/services/ingestion/metadata.py
```

**5.3. Move Queries**:

```bash
app/queries/vector_search.py → business/queries/vector_search.py
app/queries/llm_question.py → business/queries/llm_question.py
```

**5.4. Update Imports**:

```python
# Pipelines
from business.stages.graphrag.extraction import GraphExtractionStage
from business.stages.graphrag.entity_resolution import EntityResolutionStage
from core.config.graphrag import GraphRAGPipelineConfig

# Services
from dependencies.database.mongodb import MongoDBClient
from core.models.graphrag import EntityModel
```

**Verification**:

```bash
python -c "from business.pipelines.graphrag import GraphRAGPipeline; print('OK')"
python -c "from business.services.graphrag.indexes import ensure_graphrag_indexes; print('OK')"
```

---

### Phase 6: Move APP Layer - CLIs (1 hour)

**Goal**: Move entry points

**6.1. Move CLI Files**:

```bash
main.py → app/cli/main.py
run_graphrag_pipeline.py → app/cli/graphrag.py
```

**6.2. Update Imports in CLIs**:

```python
# app/cli/graphrag.py
from business.pipelines.graphrag import GraphRAGPipeline
from core.config.graphrag import GraphRAGPipelineConfig
from dependencies.observability.logging import setup_logging
```

**6.3. Update Entry Points**:

- Update `setup.py` or package config if exists
- Update run commands in README

**Verification**:

```bash
python app/cli/main.py --help
python app/cli/graphrag.py --help
```

---

### Phase 7: Move APP Layer - UI & Scripts (1-2 hours)

**Goal**: Move remaining APP layer components

**7.1. Move UI Files**:

```bash
streamlit_app.py → app/ui/streamlit_app.py
chat.py → app/ui/chat.py
```

**7.2. Move Scripts**:

```bash
scripts/analyze_graph_structure.py → app/scripts/graphrag/analyze_graph_structure.py
scripts/test_random_chunks.py → app/scripts/graphrag/test_random_chunks.py
scripts/diagnose_graphrag_communities.py → app/scripts/graphrag/diagnose_communities.py
scripts/monitor_density.py → app/scripts/graphrag/monitor_density.py
scripts/sample_graph_data.py → app/scripts/graphrag/sample_graph_data.py
scripts/full_cleanup.py → app/scripts/utilities/full_cleanup.py
scripts/check_graphrag_data.py → app/scripts/utilities/check_data.py
```

**7.3. Update Imports**:

```python
# app/ui/streamlit_app.py
from business.services.rag.generation import generate_answer
from business.queries.vector_search import search_chunks

# app/scripts/graphrag/analyze_graph_structure.py
from business.services.graphrag.indexes import get_graphrag_collections
```

**Verification**:

```bash
streamlit run app/ui/streamlit_app.py  # Should work
python app/scripts/graphrag/analyze_graph_structure.py  # Should work
```

---

### Phase 8: Reorganize Documentation (1-2 hours)

**Goal**: Update documentation structure

**8.1. Create LLM Context Files**:

```bash
# documentation/context/app-layer.md
# documentation/context/business-layer.md
# documentation/context/core-layer.md
# documentation/context/dependencies-layer.md
```

**8.2. Reorganize Existing Docs**:

```bash
mkdir documentation/architecture
mkdir documentation/guides

mv documentation/PIPELINE.md documentation/architecture/
mv documentation/STAGE.md documentation/architecture/
mv documentation/AGENT.md documentation/architecture/
mv documentation/SERVICE.md documentation/architecture/
mv documentation/CORE.md documentation/architecture/

mv documentation/DEPLOYMENT.md documentation/guides/
mv documentation/TESTING.md documentation/guides/
mv documentation/EXECUTION.md documentation/guides/
mv documentation/MCP-SERVER.md documentation/guides/
```

**8.3. Create Documentation Index**:

```markdown
# documentation/README.md

## Quick Navigation

### For LLM Context

- [APP Layer Overview](context/app-layer.md)
- [BUSINESS Layer Overview](context/business-layer.md)
- [CORE Layer Overview](context/core-layer.md)
- [DEPENDENCIES Layer Overview](context/dependencies-layer.md)

### For Developers

- [Architecture Docs](architecture/)
- [User Guides](guides/)
- [GraphRAG Technical Guide](GRAPH-RAG-CONSOLIDATED.md)
```

---

### Phase 9: Update All Documentation (2-3 hours)

**Goal**: Update code references in all docs

**9.1. Update Architecture Docs**:

- Update all file paths in STAGE.md, AGENT.md, SERVICE.md, CORE.md
- Update import examples

**9.2. Update GraphRAG Docs**:

- Update GRAPH-RAG-CONSOLIDATED.md with new paths
- Update GRAPHRAG-ARTICLE-GUIDE.md with new code references

**9.3. Update README**:

- Update quickstart examples
- Update folder structure overview
- Add layer diagram

**9.4. Create Layer Context Files**:

```markdown
# documentation/context/business-layer.md

## BUSINESS Layer Overview

**Purpose**: Implementation and process execution

**Structure**:

- `agents/` - LLM-powered intelligent components
- `stages/` - Pipeline processing units
- `pipelines/` - Orchestration
- `services/` - Domain logic
- `queries/` - Query handlers

**Key Files**:

- GraphRAG Pipeline: `business/pipelines/graphrag.py`
- Entity Resolution: `business/stages/graphrag/entity_resolution.py`
- ...
```

---

### Phase 10: Final Cleanup & Testing (2-3 hours)

**Goal**: Remove old structure, comprehensive testing

**10.1. Remove Old Empty Directories**:

```bash
rm -rf agents/
rm -rf app/stages/
rm -rf app/pipelines/
rm -rf app/services/
rm -rf app/queries/
rm -rf config/
rm -rf scripts/
```

**10.2. Update .gitignore**:

```gitignore
# Keep
__pycache__/
*.pyc
.env
logs/

# Add if needed
app/__pycache__/
business/__pycache__/
core/__pycache__/
dependencies/__pycache__/
```

**10.3. Comprehensive Testing**:

```bash
# Test imports
python -c "from business.pipelines.graphrag import GraphRAGPipeline; print('✓ GraphRAG Pipeline')"
python -c "from business.pipelines.ingestion import IngestionPipeline; print('✓ Ingestion Pipeline')"

# Test CLIs
python app/cli/main.py --help
python app/cli/graphrag.py --help

# Test UI
streamlit run app/ui/streamlit_app.py

# Run actual pipeline on small dataset
python app/cli/main.py pipeline --playlist_id TEST --max 1
python app/cli/graphrag.py --max 1
```

**10.4. Linting**:

```bash
# Check for import errors
pylint business/ core/ dependencies/ app/ || true

# Check for unused imports
autoflake --check --remove-all-unused-imports -r business/ core/ dependencies/ app/
```

**10.5. Git Commit**:

```bash
git add .
git commit -m "refactor: migrate to 4-layer architecture (APP/BUSINESS/CORE/DEPENDENCIES)

- Organized by type-first, feature-aware structure
- Clear separation of concerns across layers
- All runnable code in APP layer (cli, ui, scripts)
- Business logic in BUSINESS layer (agents, stages, services)
- Definitions in CORE layer (models, base classes, utilities)
- Infrastructure in DEPENDENCIES layer (database, llm, external)

Fixes: dependency flow, import patterns, layer isolation"
```

---

## Post-Migration Checklist

### Functionality ✅

- [ ] Ingestion pipeline runs successfully
- [ ] GraphRAG pipeline runs successfully
- [ ] Streamlit UI loads and functions
- [ ] Chat interface works
- [ ] All scripts in `app/scripts/` execute

### Code Quality ✅

- [ ] No circular dependencies
- [ ] All imports follow layer rules (downward only)
- [ ] No orphaned files
- [ ] All `__init__.py` files present
- [ ] Linter passes (or acceptable warnings)

### Documentation ✅

- [ ] All architecture docs updated
- [ ] GRAPH-RAG-CONSOLIDATED.md updated
- [ ] README.md updated
- [ ] LLM context files created
- [ ] Code examples in docs use new paths

### Testing ✅

- [ ] Unit tests updated (if any exist)
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] No regressions identified

---

## Rollback Plan

If migration fails:

```bash
# Rollback to backup
git reset --hard pre-refactor-backup

# Or revert specific commits
git revert <commit-hash>
```

---

## Benefits After Migration

### For Development:

✅ Clear separation of concerns  
✅ Easy to find files (type-first organization)  
✅ Dependency flow is obvious  
✅ New developers can navigate easily  
✅ Reduced cognitive load

### For Testing:

✅ Easy to mock layers  
✅ Clear test organization  
✅ Can test layers independently

### For Future Features:

✅ MCP server goes in `app/api/`  
✅ New agents go in `business/agents/`  
✅ Infrastructure changes isolated in `dependencies/`  
✅ Room to grow without confusion

### For Documentation:

✅ LLM context files per layer  
✅ Clear architecture diagrams  
✅ Code examples always use correct paths

---

---

## Chat Feature Extraction Plan

### Current State Analysis

**File**: `chat.py` (1,370 lines)

**What it does**:

- Memory-aware CLI chat interface
- Query rewriting with conversation context
- Multi-modal retrieval (vector, hybrid, keyword)
- Reference and topic answer agents
- Session management and export

**Current location**: Root (entry point)

### Target Structure

**Entry Point** → `app/cli/chat.py`

- CLI orchestration only
- Command parsing
- Session management

**Business Logic** → `business/chat/`

```
business/chat/
├── __init__.py
├── memory.py              # Session & memory management
├── query_rewriter.py      # Query rewriting agent
├── planner.py             # Route/mode/filter planning (uses PlannerAgent)
├── retrieval.py           # Retrieval orchestration
└── answering.py           # Answer generation (uses ReferenceAnswerAgent, TopicReferenceAgent)
```

**Services** → `business/services/chat/`

```
business/services/chat/
├── __init__.py
├── filters.py             # Filter sanitization & expansion
├── citations.py           # Citation formatting
└── export.py              # Export helpers (JSON, TXT, MD)
```

### Migration Strategy

**Phase 5.5: Extract Chat Feature** (2-3 hours)

**5.5.1. Extract Business Logic**:

```bash
# New files to create:
business/chat/memory.py              # load_long_term_memory, session management
business/chat/query_rewriter.py      # rewrite_query function
business/chat/planner.py             # Planning orchestration
business/chat/retrieval.py           # run_retrieval, normalize_context_blocks
business/chat/answering.py           # answer_with_context, build_reference_bundles

business/services/chat/filters.py   # sanitize_filters, expand_filter_values
business/services/chat/citations.py # format_citations
business/services/chat/export.py    # export_last_turn
```

**5.5.2. Slim Down CLI**:

```python
# app/cli/chat.py (new, ~200 lines)
from business.chat.memory import SessionManager
from business.chat.planner import ChatPlanner
from business.chat.retrieval import ChatRetrieval
from business.chat.answering import ChatAnswering

def run_cli():
    session = SessionManager(session_id)
    planner = ChatPlanner(session)
    retrieval = ChatRetrieval()
    answering = ChatAnswering()

    while True:
        user_input = input("> ")

        # Orchestrate
        plan = planner.plan(user_input)
        hits = retrieval.retrieve(plan)
        answer = answering.answer(plan, hits)

        # Display and persist
        session.add_turn(user_input, answer, hits)
```

**Key Benefit**: Clean separation of CLI (APP) from chat logic (BUSINESS)

---

## Improvement TODO Tracking

### HARD RESTRICTION ⚠️

**Do NOT change working code during migration!**

Instead, create `REFACTOR-TODO.md` to track improvements identified during migration.

### Categories of TODOs

**1. Code Repetition** 🔁

- Agent initialization patterns (LLM client, retries)
- Stage setup patterns (collection access, DB connections)
- Pipeline orchestration patterns (stage registry, error handling)

**2. Architecture Improvements** 🏗️

- Dependency injection opportunities
- Factory patterns for agents/stages
- Configuration management consolidation

**3. Performance Optimizations** ⚡

- Lazy loading opportunities
- Caching strategies
- Batch processing patterns

**4. Code Quality** ✨

- Type hints completion
- Docstring standardization
- Error message improvements

### Example TODO Format

````markdown
# REFACTOR-TODO.md

## Code Repetition Issues

### Agent Initialization Pattern

**Location**: All agents (graph_extraction_agent.py, entity_resolution_agent.py, etc.)

**Current Problem**:

```python
# Repeated in every agent
def __init__(self, llm_client, model_name="gpt-4o-mini", temperature=0.1):
    self.llm_client = llm_client
    self.model_name = model_name
    self.temperature = temperature
```
````

**Proposed Solution**:

```python
# Create BaseAgent with common initialization
class BaseAgent:
    def __init__(self, llm_client, model_name="gpt-4o-mini", temperature=0.1, **kwargs):
        self.llm_client = llm_client
        self.model_name = model_name
        self.temperature = temperature
        self._setup(**kwargs)

    def _setup(self, **kwargs):
        """Override in subclasses for specific setup"""
        pass
```

**Files Affected**: 10+ agent files
**Estimated Effort**: 2-3 hours
**Priority**: Medium
**Breaking Changes**: None (backward compatible)

````

### Phase 0.5: Create TODO Tracking (30 min)

**0.5.1. Create REFACTOR-TODO.md**:
```markdown
# Refactoring TODO List

**Purpose**: Track code improvements identified during folder structure migration

**Status**: Documentation only - no changes implemented yet

**Categories**:
- [ ] Code Repetition
- [ ] Architecture Improvements
- [ ] Performance Optimizations
- [ ] Code Quality

## Instructions
During migration, when you identify repetitive code or improvement opportunities:
1. Document it here
2. Categorize it
3. Estimate effort
4. Note priority
5. Continue migration (don't fix now!)
````

**0.5.2. During Each Phase**:

- Add identified improvements to TODO
- Include file locations
- Include code snippets
- Estimate refactor effort

**0.5.3. Post-Migration**:

- Review TODO list
- Prioritize items
- Plan refactor sprints
- Execute improvements safely

---

## LinkedIn Article: "Refactoring to Clean Architecture"

### Article Plan

**Target**: LinkedIn audience (developers, architects, technical leads)

**Hook**: "We rewrote 18,000 lines across 100+ files without breaking a single test. Here's how."

### Article Outline

#### Article: "Refactoring 18k Lines Without Breaking Production: A Clean Architecture Journey"

**Part 1: The Problem** (Hook)

_The Setup_:

- Project grew organically (agents → stages → pipelines → GraphRAG)
- Files scattered across folders
- Import chains becoming tangled
- New developers confused about where code belongs
- "Where does this go?" became daily question

_The Symptoms_:

```
agents/graph_extraction_agent.py
app/stages/graph_extraction.py
app/services/graphrag_indexes.py
config/graphrag_config.py
core/graphrag_models.py
# All GraphRAG, but 5 different folders!
```

_The Metrics_:

- 100+ Python files
- 18,000+ lines of code
- 6 root-level folders
- No clear architecture pattern
- 30-second "where is this file?" searches

**Part 2: The Vision** (Journey Begins)

_The Realization_:
"We need layers, not chaos."

_The Principles_:

```
APP          → External interface (CLIs, UIs, Scripts)
BUSINESS     → Implementation (Agents, Stages, Services)
CORE         → Definitions (Models, Base classes, Config)
DEPENDENCIES → Infrastructure (DB, LLM, External APIs)
```

_The Rule_:
**Dependency flows downward only**

- APP can import BUSINESS, CORE, DEPENDENCIES
- BUSINESS can import CORE, DEPENDENCIES
- CORE can import DEPENDENCIES
- DEPENDENCIES imports nothing (except external libs)

_The Constraint_:
**Zero breakage allowed** - Production system keeps running

**Part 3: The Strategy** (Breakthrough)

_Type-First Organization_:

```
business/
├── agents/           # What they are
│   ├── graphrag/     # What they do
│   └── ingestion/
├── stages/
│   ├── graphrag/
│   └── ingestion/
└── services/
    ├── graphrag/
    ├── rag/
    └── ingestion/
```

_Migration Order_ (Critical Decision):

```
1. CORE first       # Foundation
2. DEPENDENCIES     # Infrastructure
3. BUSINESS         # Logic
4. APP last         # Entry points
```

**Why this order**:

- Core has no dependencies → safe to move first
- Business depends on Core → move after Core stable
- APP depends on everything → move last

_The Safety Net_:

```bash
git tag pre-refactor-backup
# Every phase: Test imports before proceeding
python -c "from core.models.graphrag import EntityModel; print('OK')"
```

**Part 4: The Execution** (Action)

_Phase-by-Phase Breakdown_:

**Phase 1: Core Layer** (3 hours)

- Moved 15 files
- Updated 200+ import statements
- Zero runtime errors

**Discovery #1**: Import cycles hidden by deep nesting

```python
# Before (hidden cycle)
config/graphrag_config.py → core/graphrag_models.py → config/paths.py

# After (cycle broken)
core/config/graphrag.py → core/models/graphrag.py → core/config/paths.py
```

**Phase 2: Dependencies Layer** (3 hours)

- Extracted infrastructure code
- Created adapters for MongoDB, LLM clients
- Centralized all external dependencies

**Discovery #2**: Same DB connection logic copy-pasted 8 times

```python
# Before: Repeated everywhere
client = MongoClient(os.getenv("MONGODB_URI"))

# After: One place
from dependencies.database.mongodb import MongoDBClient
client = MongoDBClient.get_instance()
```

**Phase 3-5: Business Layer** (8 hours)

- Moved 60+ files
- Organized by type (agents/, stages/, services/)
- Then by feature (graphrag/, ingestion/)

**Discovery #3**: Agent initialization pattern repeated 12 times
→ Added to REFACTOR-TODO.md (not fixed yet!)

**Phase 6-7: APP Layer** (2 hours)

- Moved CLIs, UIs, Scripts
- All entry points in one place
- Clear "this is runnable" signal

**Part 5: The Results** (Victory)

_Metrics_:

- **100% success rate** - Zero broken imports
- **18 hours total** - Spread over 4 days
- **0 regressions** - All pipelines run
- **30 → 5 seconds** - File finding time

_Structure Now_:

```
app/cli/graphrag.py                          # "I want to run this"
  ↓
business/pipelines/graphrag.py               # "I orchestrate"
  ↓
business/stages/graphrag/extraction.py       # "I process"
  ↓
business/agents/graphrag/extraction.py       # "I'm intelligent"
  ↓
core/models/graphrag.py                      # "I define structure"
  ↓
dependencies/database/mongodb.py             # "I talk to MongoDB"
```

_Developer Experience_:

- **Before**: "Where does this go?" → 30 seconds searching
- **After**: "Is it runnable? → APP. Business logic? → BUSINESS."

_New Feature Time_:

- **Before**: "Let me check 5 different folders..."
- **After**: "MCP server? `app/api/`. Done."

**Part 6: The Lessons** (Key Learnings)

**Lesson 1: Don't mix layers**

```python
# BAD: CLI has business logic
# app/cli/main.py
answer = llm_client.chat.completions.create(...)  # ❌

# GOOD: CLI calls business
# app/cli/chat.py
answer = answering.answer(plan, hits)  # ✅
```

**Lesson 2: Move bottom-up, test top-down**

- Move: Core → Dependencies → Business → APP
- Test: APP → Business → Dependencies → Core

**Lesson 3: Document, don't fix (yet)**

- Found 20+ refactor opportunities
- Tracked in REFACTOR-TODO.md
- Addressed later, safely

**Lesson 4: Alphabetical ordering is underrated**

```
app/
business/
core/
dependencies/
# Immediate visual hierarchy!
```

**Part 7: The Bonus** (Future)

_What We Unlocked_:

**LLM Context Files**:

```
documentation/context/
├── app-layer.md          # "I'm APP layer, I handle entry points"
├── business-layer.md     # "I'm BUSINESS, I execute logic"
├── core-layer.md         # "I'm CORE, I define contracts"
└── dependencies-layer.md # "I'm DEPENDENCIES, I adapt external world"
```

**Easy Testing**:

```python
# Mock entire dependency layer
mock_db = MockMongoDBClient()
# Business logic runs unchanged
```

**Clear Growth Path**:

- New pipeline? → `business/pipelines/`
- New agent? → `business/agents/`
- New external API? → `dependencies/external/`

**Part 8: The Code** (Technical Deep-Dive)

**Example: GraphRAG Stage Before/After**

_Before_:

```python
# app/stages/graph_extraction.py
from core.base_stage import BaseStage
from agents.graph_extraction_agent import GraphExtractionAgent
from config.graphrag_config import GraphExtractionConfig
from app.services.utils import get_mongo_client  # ⚠️ Cross-cutting

class GraphExtractionStage(BaseStage):
    def setup(self):
        self.client = get_mongo_client()  # Infrastructure in business logic
        self.agent = GraphExtractionAgent(...)
```

_After_:

```python
# business/stages/graphrag/extraction.py
from core.base.stage import BaseStage
from business.agents.graphrag.extraction import GraphExtractionAgent
from core.config.graphrag import GraphExtractionConfig
from dependencies.database.mongodb import MongoDBClient  # ✅ Clear layer

class GraphExtractionStage(BaseStage):
    def setup(self):
        self.client = MongoDBClient.get_instance()  # Infrastructure abstracted
        self.agent = GraphExtractionAgent(...)
```

**What Changed**:

- Imports from correct layers
- Infrastructure in DEPENDENCIES
- Clear file location
- Feature grouping (`graphrag/`)

**Part 9: Call to Action**

"Refactoring tip: If you're struggling to explain where code should go, you need better layers.

Start with 4 questions:

1. Does it run or talk to users? → APP
2. Does it implement logic? → BUSINESS
3. Does it define structure? → CORE
4. Does it adapt external systems? → DEPENDENCIES

Your imports will tell you if you got it right."

---

### Article Metadata

**Title**: "Refactoring 18k Lines Without Breaking Production: A Clean Architecture Journey"

**Subtitle**: "How we reorganized 100+ files into a 4-layer architecture in 18 hours with zero regressions"

**Tags**: #SoftwareArchitecture #CleanArchitecture #Refactoring #Python #BestPractices

**Estimated Reading Time**: 12 minutes

**Code Examples**: 8 (Before/After comparisons)

**Diagrams**: 2 (Layer dependency, File organization)

**Target Audience**: Mid to Senior developers, Technical leads, Architects

**Key Takeaways**:

1. Layer your codebase by dependency direction
2. Move bottom-up (Core first), test top-down (APP first)
3. Document improvements, don't fix during migration
4. Type-first organization beats feature-first for discoverability
5. Alphabetical layer names create visual hierarchy

---

## Timeline Estimate (Updated)

| Phase     | Description                        | Time             |
| --------- | ---------------------------------- | ---------------- |
| 0         | Preparation                        | 1 hour           |
| 0.5       | Create TODO Tracking               | 30 min           |
| 1         | Move CORE                          | 2-3 hours        |
| 2         | Extract DEPENDENCIES               | 2-3 hours        |
| 3         | Move BUSINESS - Agents             | 1-2 hours        |
| 4         | Move BUSINESS - Stages             | 2-3 hours        |
| 5         | Move BUSINESS - Pipelines/Services | 2-3 hours        |
| 5.5       | Extract Chat Feature               | 2-3 hours        |
| 6         | Move APP - CLIs                    | 1 hour           |
| 7         | Move APP - UI/Scripts              | 1-2 hours        |
| 8         | Reorganize Documentation           | 1-2 hours        |
| 9         | Update All Documentation           | 2-3 hours        |
| 10        | Final Cleanup & Testing            | 2-3 hours        |
| 11        | Write LinkedIn Article             | 2-3 hours        |
| **Total** | **Complete Migration**             | **~22-32 hours** |

**Recommended**: Spread over 4-5 days, 4-8 hours per day

---

**Ready to execute this plan!** 🚀
