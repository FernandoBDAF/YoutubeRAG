# Architecture Guide - 4-Layer + Domains + Libraries

**Last Updated**: November 3, 2025  
**Status**: Production (implemented and validated)

---

## Overview

**What It Is**: Clean 4-layer architecture with vertical domain separation and cross-cutting libraries

**Problem It Solves**:

- 76 files scattered across 6 folders with no clear structure
- Circular dependencies
- "Where does this go?" daily question
- Difficult for LLMs to navigate

**Solution**:

- Horizontal: 4 layers (APP → BUSINESS → CORE → DEPENDENCIES)
- Vertical: 8 domains (GraphRAG, RAG, Chat, Ingestion, etc.)
- Cross-cutting: 18 libraries (error_handling, metrics, retry, etc.)

---

## The 4-Layer Architecture

### Layer 1: APP (External Interface)

**Purpose**: Anything that runs or talks to the external world

**Contains**:

- CLIs (app/cli/)
- UIs (app/ui/)
- APIs (app/api/)
- Scripts (app/scripts/)

**Import Rule**: Can import from BUSINESS, CORE, DEPENDENCIES

**Example**:

```python
# app/cli/graphrag.py
from business.pipelines.graphrag import GraphRAGPipeline  # BUSINESS
from core.config.graphrag import GraphRAGPipelineConfig  # CORE
from core.libraries.logging import setup_logging          # CORE (library)
```

**For LLMs**: See context/app-layer.md

---

### Layer 2: BUSINESS (Implementation)

**Purpose**: Process execution, domain logic, orchestration

**Contains**:

- Agents (business/agents/)
- Stages (business/stages/)
- Pipelines (business/pipelines/)
- Services (business/services/)
- Queries (business/queries/)
- Chat (business/chat/)

**Import Rule**: Can import from CORE, DEPENDENCIES (NOT from APP)

**Organization**: Type-first, then feature

```
business/agents/          # Type: Agents
├── graphrag/             # Feature: GraphRAG
├── ingestion/            # Feature: Ingestion
└── rag/                  # Feature: RAG
```

**For LLMs**: See context/business-layer.md

---

### Layer 3: CORE (Definitions)

**Purpose**: Fundamental contracts, models, base classes, libraries

**Contains**:

- Models (core/models/)
- Base classes (core/base/)
- Domain utilities (core/domain/)
- Configuration (core/config/)
- **Libraries** (core/libraries/) ⭐

**Import Rule**: Can import from DEPENDENCIES only (NOT from APP or BUSINESS)

**Libraries** (18 total):

```
core/libraries/
├── logging/              ✅ Complete
├── error_handling/       ✅ Complete
├── metrics/              ✅ Complete
├── retry/                ✅ Complete
└── [14 others]           📝 Stubs
```

**For LLMs**: See context/core-layer.md

---

### Layer 4: DEPENDENCIES (Infrastructure)

**Purpose**: Abstract external systems (databases, APIs, LLMs)

**Contains**:

- Database adapters (dependencies/database/)
- LLM providers (dependencies/llm/)
- External APIs (dependencies/external/)
- Observability (dependencies/observability/)

**Import Rule**: Only imports from external libraries (NO project code)

**For LLMs**: See context/dependencies-layer.md

---

## Vertical Domains

**8 Identified Domains**:

**Deep Domains** (use-case specific):

1. **GraphRAG** - Knowledge graph extraction (6 agents, 4 stages, 4 services)
2. **Ingestion** - Content processing (3 agents, 9 stages, 2 services)

**Medium Domains** (business + technical): 3. **RAG** - Traditional retrieval (3 agents, 8 services, 4 queries) 4. **Chat** - Conversational interface (4 modules, 3 services) 5. **Query** - Search orchestration (4 handlers)

**Shallow Domains** (technical orchestration): 6. **Pipeline** - Stage orchestration (1 runner, 2 implementations) 7. **Stage** - Processing pattern (13 implementations) 8. **Agent** - LLM interaction (12 implementations)

**Organization**: Domain code grouped by feature within type-first structure

---

## Cross-Cutting Libraries

**Purpose**: Reusable technical patterns supporting all domains

**Categories**:

**Observability** (Tier 1 - Complete):

- logging (6 files) - Setup, formatters, operations, exceptions
- error_handling (4 files) - Exceptions, decorators, context
- metrics (5 files) - Collectors, registry, exporters, cost models
- retry (3 files) - Policies, decorators

**Support** (Tier 2 - Stubs with TODO):

- validation, configuration, caching
- database, llm, concurrency, rate_limiting
- serialization, data_transform

**Future** (Tier 3 - Stubs):

- health, context, di, feature_flags

**Key Principle**: Libraries are pure (no imports from APP or BUSINESS)

---

## Dependency Flow

```
APP (external interface)
  ↓ uses
BUSINESS (domain logic)
  ↓ uses
CORE (definitions + libraries)
  ↓ uses
DEPENDENCIES (infrastructure)
  ↓ uses
External Systems (MongoDB, OpenAI, etc.)
```

**Rule**: Dependencies flow downward only

**Libraries sit in CORE**: Available to all layers below

---

## Design Evolution

### Iteration 1: Organic Growth

- Agents, stages, services added organically
- 6 root folders, no clear pattern
- "Where does this go?" confusion

### Iteration 2: Horizontal Layers (Oct 31)

- 4-layer architecture established
- 76 files migrated in 5 hours
- 0 breaking changes
- Type-first organization

### Iteration 3: Libraries + Domains (Nov 3)

- 18 cross-cutting libraries identified
- 4 observability libraries implemented
- Vertical domain analysis
- Complete observability achieved

**Lesson**: Architecture evolves through refactoring, not upfront design

---

## Integration Patterns

### Libraries + Base Classes:

```python
# core/base/stage.py
from core.libraries.error_handling import handle_errors
from core.libraries.logging import log_operation_context
from core.libraries.metrics import Counter, Histogram

# BaseStage uses all libraries
@handle_errors(log_traceback=True)
def run(self, config):
    log_operation_context(f"stage_{self.name}")
    # ... metrics tracked automatically
```

**Result**: All 13 stages inherit complete observability

---

### Libraries + Agents:

```python
# core/base/agent.py
from core.libraries.retry import retry_llm_call
from core.libraries.metrics import Counter

@retry_llm_call(max_attempts=3)
def call_model(self, ...):
    # Automatic retry + metrics tracking
```

**Result**: All 12 agents get retry + cost tracking

---

## File Organization

**Total Files**: ~100 Python files

**Breakdown**:

- APP: 14 files
- BUSINESS: 60+ files (agents, stages, services, etc.)
- CORE: 20+ files (models, base, libraries)
- DEPENDENCIES: 8 files

**Tests**: Mirror structure in tests/ folder

---

## Key Decisions

**1. Type-First vs Feature-First**

Chose: **Type-first** (business/agents/graphrag/)  
Alternative: Feature-first (business/graphrag/agents/)

**Reason**: Easier to find "all agents" than "all GraphRAG code"  
**For LLMs**: Type-first maps to "what kind of thing is this?"

**2. Libraries in CORE vs DEPENDENCIES**

Chose: **CORE** (pure, reusable patterns)  
Alternative: DEPENDENCIES (infrastructure concern)

**Reason**: Libraries are fundamental definitions, not external adapters  
**For LLMs**: CORE = "always available", DEPENDENCIES = "external world"

**3. Alphabetical Layer Naming**

**APP → BUSINESS → CORE → DEPENDENCIES**

**Benefit**: Visual hierarchy (A before B before C before D)  
**For LLMs**: Instant understanding of layer order

---

## Testing Strategy

**Mirror Structure**: tests/ mirrors source structure

```
tests/
├── core/libraries/       # Library tests
├── core/base/            # Base class integration tests
├── business/agents/      # Agent tests
└── app/cli/              # CLI tests
```

**Pattern**: One test file per source file

---

## Migration Path

**From**: Scattered 6-folder structure  
**To**: Clean 4-layer architecture  
**Time**: 5 hours  
**Files**: 76 migrated  
**Breaks**: 0

**Process**: Copy → Test → Verify → Delete old

---

## For Developers

**Adding New Code**:

**Question 1**: Does it run or talk to users?  
→ YES: **APP layer**

**Question 2**: Does it implement business logic?  
→ YES: **BUSINESS layer** (which domain?)

**Question 3**: Does it define structure or provide reusable patterns?  
→ YES: **CORE layer** (model or library?)

**Question 4**: Does it adapt an external system?  
→ YES: **DEPENDENCIES layer**

**For LLMs**: Context files have complete decision trees

---

## Related Documentation

**Deep Dives**:

- Component patterns: architecture/PIPELINE.md, STAGE.md, AGENT.md
- Library details: technical/OBSERVABILITY.md, technical/LIBRARIES.md

**Quick Reference**:

- Layer context: context/[layer]-layer.md
- Planning: planning/ROADMAP.md

---

**This architecture enables LLM-assisted development and clean agent systems.**
