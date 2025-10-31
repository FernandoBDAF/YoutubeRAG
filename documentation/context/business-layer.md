# BUSINESS Layer - LLM Context Guide

**Layer Purpose**: Implementation - Process execution, domain logic, orchestration

---

## What Belongs in BUSINESS Layer

✅ **Agents** (LLM-powered intelligence)  
✅ **Stages** (pipeline processing units)  
✅ **Pipelines** (orchestration logic)  
✅ **Services** (domain logic, business rules)  
✅ **Queries** (query handlers and processors)

❌ **Entry points** (goes in APP)  
❌ **Base class definitions** (goes in CORE)  
❌ **Infrastructure adapters** (goes in DEPENDENCIES)

---

## Structure

```
business/
├── agents/             # LLM-powered intelligent components
│   ├── graphrag/       # GraphRAG agents (extraction, resolution, etc.)
│   ├── ingestion/      # Ingestion agents (clean, enrich, trust)
│   └── rag/            # RAG agents (planner, reference_answer, etc.)
│
├── stages/             # Pipeline processing stages
│   ├── graphrag/       # GraphRAG stages
│   └── ingestion/      # Ingestion stages
│
├── pipelines/          # Pipeline orchestration
│   ├── runner.py       # PipelineRunner + StageSpec
│   ├── ingestion.py    # IngestionPipeline
│   └── graphrag.py     # GraphRAGPipeline
│
├── services/           # Domain services
│   ├── graphrag/       # GraphRAG services (indexes, query, retrieval)
│   ├── rag/            # RAG services (generation, retrieval, indexes)
│   ├── ingestion/      # Ingestion services (transcripts, metadata)
│   └── chat/           # Chat services (future)
│
└── queries/            # Query handlers
    ├── vector_search.py
    ├── llm_question.py
    └── ...
```

---

## Import Pattern

BUSINESS layer can import from CORE and DEPENDENCIES:

```python
# business/stages/graphrag/extraction.py
from core.base.stage import BaseStage                        # CORE
from core.models.graphrag import EntityModel                 # CORE
from core.config.graphrag import GraphExtractionConfig       # CORE
from business.agents.graphrag.extraction import Agent        # BUSINESS (same layer)
from dependencies.database.mongodb import MongoDBClient      # DEPENDENCIES
```

**Cannot import from**: APP ❌

---

## Organization Strategy

**Type-First, Then Feature**:

```
business/agents/        # Type: Agents
├── graphrag/           # Feature: GraphRAG
├── ingestion/          # Feature: Ingestion
└── rag/                # Feature: RAG
```

**Why**: Easy to find "all agents" or "all GraphRAG components"

---

## Example: Stage Implementation

```python
# business/stages/graphrag/extraction.py
from core.base.stage import BaseStage
from core.config.graphrag import GraphExtractionConfig
from business.agents.graphrag.extraction import GraphExtractionAgent
from dependencies.database.mongodb import get_mongo_client

class GraphExtractionStage(BaseStage):
    name = "graph_extraction"
    ConfigCls = GraphExtractionConfig

    def setup(self):
        super().setup()
        # Use DEPENDENCIES for infrastructure
        self.llm_client = get_openai_client()

        # Use BUSINESS agents for intelligence
        self.agent = GraphExtractionAgent(self.llm_client)

    def handle_doc(self, doc):
        # Business logic here
        knowledge = self.agent.extract(doc['chunk_text'])
        # Save to database
        self.db.chunks.update_one(...)
```

---

## Files in BUSINESS Layer

### Agents (12 files):

**GraphRAG**:

- `agents/graphrag/extraction.py` - Entity/relationship extraction
- `agents/graphrag/entity_resolution.py` - Entity canonicalization
- `agents/graphrag/relationship_resolution.py` - Relationship merging
- `agents/graphrag/community_detection.py` - Community detection
- `agents/graphrag/community_summarization.py` - Community summaries
- `agents/graphrag/link_prediction.py` - Link prediction

**Ingestion**:

- `agents/ingestion/clean.py` - Transcript cleaning
- `agents/ingestion/enrich.py` - Content enrichment
- `agents/ingestion/trust.py` - Trust scoring

**RAG**:

- `agents/rag/reference_answer.py` - Reference-based answers
- `agents/rag/topic_reference.py` - Topic-based answers
- `agents/rag/planner.py` - Query planning

### Stages (13 files):

**GraphRAG**: 4 stages (extraction, entity_resolution, graph_construction, community_detection)  
**Ingestion**: 9 stages (ingest, clean, chunk, enrich, embed, redundancy, trust, backfill, compress)

### Pipelines (3 files):

- `runner.py` - Pipeline orchestration framework
- `ingestion.py` - Ingestion pipeline
- `graphrag.py` - GraphRAG pipeline

### Services (14 files):

**GraphRAG**: indexes, query, retrieval, generation  
**RAG**: core, generation, retrieval, indexes, filters, feedback, persona_utils, profiles  
**Ingestion**: transcripts, metadata

### Queries (4 files):

vector_search, llm_question, get, videos_insights

---

## When Adding New Code

**Ask**: Does this implement business logic or orchestrate processes?

- **Yes** → BUSINESS layer
- **No** → Check other layers

**Examples**:

- New extraction algorithm → `business/agents/graphrag/`
- New pipeline stage → `business/stages/`
- New service → `business/services/`
- New query type → `business/queries/`

---

**For detailed patterns, see**: `documentation/architecture/`
