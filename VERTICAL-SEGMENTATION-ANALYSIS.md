# Vertical Segmentation Analysis: Domains vs. Libraries

**Date**: October 31, 2025  
**Vision**: Separate business domains from cross-cutting technical libraries  
**Goal**: Extract repetition, patternize behaviors, create reusable libraries

---

## 🎯 Conceptual Framework

### Horizontal Segmentation (DONE ✅)

```
APP          → I/O interface (closest to external world)
BUSINESS     → Business logic
CORE         → Definitions
DEPENDENCIES → Infrastructure
```

**Rule**: Each layer depends only on layers below

---

### Vertical Segmentation (NEW - TO IMPLEMENT)

**Two Types of Verticals**:

**1. DOMAINS** (Business-specific):

- Features related to use cases
- Business functionality
- Examples: graphrag, rag, chat, ingestion, query

**2. LIBRARIES** (Technical support):

- Cross-cutting concerns
- Technical patterns
- Support all domains
- Examples: logging, tracing, error_handling, retry, validation, caching

---

## Conceptual Model

```
         DOMAINS (Vertical Slices)
         ↓        ↓       ↓       ↓
    graphrag   rag    chat  ingestion
       ↓        ↓       ↓       ↓
    ┌──────────────────────────────┐
    │  LIBRARIES (Cross-cutting)   │  ← Support all domains
    │  - logging                   │
    │  - tracing                   │
    │  - error_handling            │
    │  - retry                     │
    │  - validation                │
    │  - caching                   │
    └──────────────────────────────┘
              ↓
         DEPENDENCIES
    (External adapters)
```

---

## 📊 Current Domains Identified

### 1. GraphRAG Domain ✅

**Location**: Currently in `business/agents/graphrag/`, `business/stages/graphrag/`, etc.

**Components**:

- **Agents**: extraction, entity_resolution, relationship_resolution, community_detection, community_summarization, link_prediction
- **Stages**: extraction, entity_resolution, graph_construction, community_detection
- **Services**: indexes, query, retrieval, generation
- **Models**: EntityModel, RelationshipModel, KnowledgeModel, CommunitySummary

**Functionality**: Knowledge graph extraction and management

**Depth**: Deep business domain (use-case specific)

---

### 2. RAG Domain ✅

**Location**: Currently in `business/agents/rag/`, `business/services/rag/`

**Components**:

- **Agents**: reference_answer, topic_reference, planner
- **Services**: core, generation, retrieval, indexes, filters, feedback, persona_utils, profiles
- **Queries**: vector_search, llm_question, get, videos_insights

**Functionality**: Retrieval-augmented generation (traditional vector-based)

**Depth**: Medium business domain

---

### 3. Chat Domain ✅

**Location**: Currently in `business/chat/`, `business/services/chat/`

**Components**:

- **Chat Logic**: memory, query_rewriter, retrieval, answering
- **Services**: filters, citations, export

**Functionality**: Conversational interface with memory

**Depth**: Medium business domain (orchestrates RAG)

---

### 4. Ingestion Domain ✅

**Location**: Currently in `business/agents/ingestion/`, `business/stages/ingestion/`, `business/services/ingestion/`

**Components**:

- **Agents**: clean, enrich, trust
- **Stages**: ingest, clean, chunk, enrich, embed, redundancy, trust, backfill, compress
- **Services**: transcripts, metadata

**Functionality**: Content ingestion and preparation

**Depth**: Deep business domain (YouTube-specific)

---

### 5. Pipeline Domain ✅

**Location**: Currently in `business/pipelines/`

**Components**:

- **Orchestration**: runner (PipelineRunner, StageSpec)
- **Implementations**: ingestion, graphrag

**Functionality**: Pipeline orchestration and stage execution

**Depth**: Shallow (technical orchestration)

---

### 6. Query Domain ✅

**Location**: Currently in `business/queries/`

**Components**:

- vector_search, llm_question, get, videos_insights

**Functionality**: Query processing and execution

**Depth**: Medium (business + technical)

---

## 🔧 Current Libraries Identified (Cross-Cutting Concerns)

### 1. Logging Library (Partial ✅)

**Current Location**: `dependencies/observability/logging.py`, `dependencies/observability/log_utils.py`

**What Exists**:

- `setup_logging()` - Central logging configuration
- `get_logger()` - Logger factory
- Timer class - Performance timing

**What's Missing**:

- Structured logging (JSON logs)
- Context propagation (request ID, session ID)
- Log aggregation helpers
- Async logging support

**Used By**: ALL domains (agents, stages, pipelines, services)

---

### 2. Error Handling Library (MISSING ❌)

**Current State**: Scattered try/except blocks

**Code Repetition Found**:

```python
# Pattern repeated ~50 times:
try:
    result = some_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    # Sometimes returns None, sometimes raises, inconsistent
```

**Needed**:

- Custom exception hierarchy
- Error context preservation
- Graceful degradation patterns
- Error reporting/aggregation

**Should Provide**:

```python
from core.libraries.error_handling import handle_errors, ApplicationError

@handle_errors(fallback=None, log=True)
def my_function():
    # Automatic error handling, logging, context
    ...
```

---

### 3. Retry Library (Partial ✅)

**Current Location**: Scattered across agents and stages

**Code Repetition Found**:

```python
# BaseAgent has execute_with_retries
# But agents manually implement retry loops

# Pattern repeated ~8 times:
for attempt in range(max_retries):
    try:
        result = llm_call()
        return result
    except Exception as e:
        if attempt < max_retries - 1:
            time.sleep(backoff)
        else:
            raise
```

**Needed**:

- Unified retry decorator
- Exponential backoff
- Retry policies (configurable)
- Circuit breaker pattern

**Should Provide**:

```python
from core.libraries.retry import with_retry, RetryPolicy

@with_retry(max_attempts=3, backoff='exponential')
def call_llm():
    ...
```

---

### 4. Validation Library (Partial ✅)

**Current Location**: Pydantic models in `core/models/`

**What Exists**:

- Pydantic models with field validation
- Custom validators (@field_validator)

**What's Missing**:

- Business rule validation (separate from data validation)
- Validation error aggregation
- Validation context
- Reusable validation rules

**Should Provide**:

```python
from core.libraries.validation import validate, ValidationRule

@validate(rules=[MinLength(10), MaxLength(1000)])
def process_text(text: str):
    ...
```

---

### 5. Configuration Library (Partial ✅)

**Current Location**: `core/config/`

**What Exists**:

- Configuration classes
- `from_args_env()` pattern

**Code Repetition Found**:

```python
# Pattern repeated ~13 times in different configs:
@classmethod
def from_args_env(cls, args, env, default_db):
    # ~20 lines of boilerplate per file
    ...
```

**Needed**:

- Centralized config loader
- Environment variable parsing
- Config validation
- Config merging (defaults → env → args)

**Should Provide**:

```python
from core.libraries.configuration import ConfigLoader

config = ConfigLoader.load(MyConfig, args, env, defaults)
```

---

### 6. Caching Library (MISSING ❌)

**Current State**: No caching

**Use Cases**:

- LLM response caching (same query → same answer)
- Entity lookup caching (frequently accessed entities)
- Embedding caching (avoid recomputing)
- Configuration caching

**Should Provide**:

```python
from core.libraries.caching import cached, CachePolicy

@cached(ttl=3600, key='entity:{entity_id}')
def get_entity(entity_id: str):
    ...
```

---

### 7. Tracing Library (MISSING ❌)

**Current State**: Basic logging, no distributed tracing

**Needed**:

- Request/operation tracing
- Span creation and propagation
- Performance profiling
- Trace context propagation

**Should Provide**:

```python
from core.libraries.tracing import trace, current_trace

@trace(operation='graph_extraction')
def extract_from_chunk(chunk):
    trace_id = current_trace().id
    ...
```

---

### 8. Metrics Library (MISSING ❌)

**Current State**: Statistics in stages (self.stats), no centralized metrics

**Code Repetition Found**:

```python
# Pattern repeated in every stage:
self.stats = {"processed": 0, "skipped": 0, "failed": 0, "updated": 0}
# Manual increment throughout
self.stats["processed"] += 1
```

**Needed**:

- Centralized metrics collection
- Counter, Gauge, Histogram types
- Metrics export (Prometheus, etc.)
- Performance metrics

**Should Provide**:

```python
from core.libraries.metrics import Counter, track_performance

processed = Counter('stage_processed', labels=['stage_name'])

@track_performance('extraction_time')
def extract():
    ...
```

---

### 9. Database Library (Partial ✅)

**Current Location**: `dependencies/database/mongodb.py`

**What Exists**:

- MongoDBClient singleton
- get_mongo_client() wrapper

**What's Missing**:

- Transaction support
- Batch operations helpers
- Query builders
- Connection pool configuration
- Migration helpers

**Should Provide**:

```python
from core.libraries.database import with_transaction, batch_insert

@with_transaction
def update_entities(entities):
    ...

batch_insert(collection, documents, batch_size=1000)
```

---

### 10. LLM Library (Partial ✅)

**Current Location**: `dependencies/llm/openai.py`

**What Exists**:

- OpenAIClient singleton
- get_openai_client() wrapper

**What's Missing**:

- Unified LLM interface (provider-agnostic)
- Response streaming
- Token counting
- Cost tracking
- Prompt templates management

**Should Provide**:

```python
from core.libraries.llm import LLMClient, with_llm_retry

client = LLMClient.get_instance()  # Works with OpenAI, Anthropic, etc.

@with_llm_retry(max_attempts=3)
def call_llm(prompt):
    ...
```

---

## 🗺️ Proposed New Structure

### Horizontal + Vertical Integration

```
app/
  ├── cli/
  ├── ui/
  ├── api/
  └── scripts/

business/
  ├── domains/                    # Business domains (vertical slices)
  │   ├── graphrag/              # GraphRAG domain
  │   │   ├── agents/
  │   │   ├── stages/
  │   │   ├── services/
  │   │   └── pipeline.py
  │   │
  │   ├── ingestion/             # Ingestion domain
  │   │   ├── agents/
  │   │   ├── stages/
  │   │   ├── services/
  │   │   └── pipeline.py
  │   │
  │   ├── rag/                   # RAG domain
  │   │   ├── agents/
  │   │   ├── services/
  │   │   └── queries/
  │   │
  │   └── chat/                  # Chat domain
  │       ├── logic/
  │       └── services/
  │
  └── shared/                    # Shared business logic (orchestration)
      └── pipelines/
          └── runner.py          # PipelineRunner (orchestrates domains)

core/
  ├── models/                    # Data models (domain-specific)
  │   ├── graphrag.py
  │   └── config.py
  │
  ├── libraries/                 # Cross-cutting technical libraries ⭐ NEW
  │   ├── logging/
  │   │   ├── __init__.py
  │   │   ├── setup.py
  │   │   ├── structured.py
  │   │   └── context.py
  │   │
  │   ├── error_handling/
  │   │   ├── __init__.py
  │   │   ├── exceptions.py
  │   │   ├── handlers.py
  │   │   └── decorators.py
  │   │
  │   ├── retry/
  │   │   ├── __init__.py
  │   │   ├── policies.py
  │   │   └── decorators.py
  │   │
  │   ├── validation/
  │   │   ├── __init__.py
  │   │   ├── rules.py
  │   │   └── validators.py
  │   │
  │   ├── caching/
  │   │   ├── __init__.py
  │   │   ├── cache.py
  │   │   └── decorators.py
  │   │
  │   ├── tracing/
  │   │   ├── __init__.py
  │   │   ├── spans.py
  │   │   └── context.py
  │   │
  │   ├── metrics/
  │   │   ├── __init__.py
  │   │   ├── collectors.py
  │   │   └── exporters.py
  │   │
  │   ├── configuration/
  │   │   ├── __init__.py
  │   │   ├── loader.py
  │   │   └── merger.py
  │   │
  │   └── database/
  │       ├── __init__.py
  │       ├── transactions.py
  │       └── batch.py
  │
  ├── base/                      # Base classes (use libraries)
  │   ├── stage.py
  │   └── agent.py
  │
  └── config/                    # Configuration definitions
      ├── paths.py
      ├── runtime.py
      └── graphrag.py

dependencies/
  ├── database/
  │   └── mongodb.py            # Uses core.libraries.database
  ├── llm/
  │   ├── openai.py             # Uses core.libraries.llm (future)
  │   └── rate_limit.py
  └── observability/
      └── [moved to core.libraries.*]
```

---

## 🔍 Domain Mapping (Complete List)

### Deep Domains (Use-Case Specific):

**1. GraphRAG** (Deepest - core business value)

- Entities, relationships, communities
- Knowledge graph construction
- Graph-aware queries
- 6 agents, 4 stages, 4 services

**2. Ingestion** (Deep - YouTube-specific)

- Video fetching, cleaning, chunking
- Transcript processing
- Quality scoring
- 3 agents, 9 stages, 2 services

---

### Medium Domains (Mixed Business + Technical):

**3. RAG** (Traditional retrieval)

- Vector search
- Hybrid search
- Answer generation
- 3 agents, 8 services, 4 queries

**4. Chat** (Conversational interface)

- Memory management
- Query rewriting
- Multi-turn conversations
- 4 modules, 3 services

**5. Query** (Search orchestration)

- Query processing
- Result ranking
- Filter handling
- 4 query handlers

---

### Shallow Domains (Technical Orchestration):

**6. Pipeline** (Orchestration)

- Stage execution
- Error handling
- Progress tracking
- 1 runner, 2 implementations

**7. Stage** (Processing unit pattern)

- Document iteration
- Transformation
- Statistics
- 13 implementations

**8. Agent** (LLM interaction pattern)

- Prompt management
- Response parsing
- Retry logic
- 12 implementations

---

## 🔧 Library Mapping (Cross-Cutting Concerns)

### Core Technical Libraries (Support ALL Domains):

**1. Logging** (Priority: Critical)

- **Current**: Partial (`dependencies/observability/`)
- **Needed**: Structured logging, context propagation
- **Used By**: ALL domains
- **Effort**: 8-12 hours

**2. Error Handling** (Priority: Critical)

- **Current**: Scattered try/except
- **Needed**: Exception hierarchy, handlers, decorators
- **Used By**: ALL domains
- **Effort**: 10-15 hours

**3. Retry** (Priority: High)

- **Current**: Manual loops in agents
- **Needed**: Unified decorator, policies
- **Used By**: Agents, services (LLM calls, DB operations)
- **Effort**: 5-8 hours

**4. Tracing** (Priority: High)

- **Current**: None
- **Needed**: Distributed tracing, spans
- **Used By**: ALL domains (debugging, performance)
- **Effort**: 10-15 hours

**5. Metrics** (Priority: High)

- **Current**: Manual stats in stages
- **Needed**: Centralized collectors, exporters
- **Used By**: Stages, pipelines, services
- **Effort**: 8-12 hours

**6. Validation** (Priority: Medium)

- **Current**: Pydantic models only
- **Needed**: Business rule validation, aggregation
- **Used By**: ALL domains (input validation)
- **Effort**: 8-12 hours

**7. Configuration** (Priority: Medium)

- **Current**: `from_args_env()` repeated 13 times
- **Needed**: Central loader, merging
- **Used By**: Stages, pipelines, services
- **Effort**: 5-8 hours

**8. Caching** (Priority: Low)

- **Current**: None
- **Needed**: LRU cache, TTL cache, decorators
- **Used By**: Services (entity lookup, LLM responses)
- **Effort**: 5-8 hours

**9. Database Operations** (Priority: Medium)

- **Current**: Basic client
- **Needed**: Transactions, batch ops, query builders
- **Used By**: Stages, services
- **Effort**: 8-12 hours

**10. LLM Operations** (Priority: Medium)

- **Current**: Basic client
- **Needed**: Provider abstraction, streaming, token counting
- **Used By**: Agents
- **Effort**: 10-15 hours

---

## 📋 Code Repetition Analysis

### 1. Agent Initialization (12 occurrences)

**Current Pattern**:

```python
# Repeated in every agent:
def __init__(self, llm_client, model_name="gpt-4o-mini", temperature=0.1):
    self.llm_client = llm_client
    self.model_name = model_name
    self.temperature = temperature
```

**Root Cause**: BaseAgent doesn't provide this

**Solution**: Extract to BaseAgent + use libraries

```python
# core/base/agent.py
from core.libraries.llm import LLMClient
from core.libraries.logging import get_logger
from core.libraries.retry import with_retry

class BaseAgent:
    def __init__(self, model_name="gpt-4o-mini", temperature=0.1, **kwargs):
        self.llm_client = LLMClient.get_instance()
        self.model_name = model_name
        self.temperature = temperature
        self.logger = get_logger(self.__class__.__name__)
        self._setup(**kwargs)

    @with_retry(max_attempts=3)
    def call_llm(self, prompt):
        # Uses libraries: retry, logging, llm
        ...
```

**Effort**: 3-4 hours (after libraries exist)

---

### 2. Stage Setup Pattern (13 occurrences)

**Current Pattern**:

```python
# Repeated in every stage:
def setup(self):
    super().setup()
    self.llm_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    self.agent = MyAgent(self.llm_client, ...)
```

**Root Cause**: No dependency injection, manual instantiation

**Solution**: Use libraries + DI

```python
# core/base/stage.py
from core.libraries.llm import LLMClient
from core.libraries.database import DatabaseClient
from core.libraries.logging import get_logger

class BaseStage:
    def __init__(self):
        self.db_client = None
        self.llm_client = None
        self.logger = None

    def setup(self):
        self.db_client = DatabaseClient.get_instance()
        self.llm_client = LLMClient.get_instance()
        self.logger = get_logger(self.__class__.__name__)
        self._setup_resources()  # Subclass hook

    def _setup_resources(self):
        """Override in subclasses."""
        pass
```

**Effort**: 4-5 hours (after libraries exist)

---

### 3. Collection Access Pattern (11 occurrences)

**Current Pattern**:

```python
# Repeated in every stage:
src_db = self.config.read_db_name or self.config.db_name
src_coll_name = self.config.read_coll or COLL_CHUNKS
collection = self.get_collection(src_coll_name, io="read", db_name=src_db)
```

**Root Cause**: No helper method in BaseStage

**Solution**: Add to BaseStage (already proposed in REFACTOR-TODO)

```python
# core/base/stage.py
def get_read_collection(self, default_coll=None):
    """Get read collection with config fallbacks."""
    src_db = self.config.read_db_name or self.config.db_name
    src_coll = self.config.read_coll or default_coll
    return self.get_collection(src_coll, io="read", db_name=src_db)

# Usage:
collection = self.get_read_collection(COLL_CHUNKS)
```

**Effort**: 1-2 hours

---

### 4. Error Logging Pattern (50+ occurrences)

**Current Pattern**:

```python
# Repeated everywhere:
try:
    result = operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    # Inconsistent: sometimes return None, sometimes raise
```

**Root Cause**: No centralized error handling

**Solution**: Use error_handling library

```python
from core.libraries.error_handling import handle_errors

@handle_errors(fallback=None, log_level='ERROR')
def operation():
    ...
```

**Effort**: 3-4 hours to implement library + 8-12 hours to apply everywhere

---

### 5. LLM Call Pattern (10+ occurrences)

**Current Pattern**:

```python
# Repeated in agents:
response = self.llm_client.chat.completions.create(
    model=self.model_name,
    messages=[...],
    temperature=self.temperature
)
result = response.choices[0].message.content
```

**Root Cause**: No unified LLM call abstraction

**Solution**: Extract to BaseAgent + use libraries

```python
# core/base/agent.py
from core.libraries.llm import call_llm
from core.libraries.retry import with_retry
from core.libraries.tracing import trace

class BaseAgent:
    @with_retry(max_attempts=3)
    @trace(operation='llm_call')
    def call_llm(self, system_prompt, user_prompt):
        # Centralized, traced, retried
        return call_llm(self.llm_client, system_prompt, user_prompt,
                       model=self.model_name, temperature=self.temperature)
```

**Effort**: 2-3 hours

---

## 🎯 Proposed Refactor Strategy

### Phase 1: Build Libraries Foundation (30-40 hours)

**Order** (dependencies first):

**1.1. Logging Library** (8-12 hours)

- Structured logging (JSON)
- Context propagation
- Log aggregation
- **Benefit**: Foundation for all other libraries

**1.2. Error Handling Library** (10-15 hours)

- Exception hierarchy
- Error handlers
- Decorators (@handle_errors)
- **Benefit**: Used by retry, tracing, all domains

**1.3. Retry Library** (5-8 hours)

- Retry decorator
- Policies (exponential backoff)
- Circuit breaker
- **Benefit**: Used by agents, services

**1.4. Tracing Library** (10-15 hours)

- Span creation
- Context propagation
- Performance profiling
- **Benefit**: Debugging, monitoring

**1.5. Metrics Library** (8-12 hours)

- Collectors (Counter, Gauge, Histogram)
- Exporters
- **Benefit**: Performance visibility

---

### Phase 2: Refactor Base Classes (15-20 hours)

**Using Libraries Built in Phase 1**:

**2.1. BaseAgent Refactor** (5-8 hours)

- Use logging library
- Use retry library
- Use LLM library
- Use tracing library
- **Result**: All 12 agents inherit improved base

**2.2. BaseStage Refactor** (5-8 hours)

- Use logging library
- Use error handling library
- Use metrics library
- Use database library
- **Result**: All 13 stages inherit improved base

**2.3. Configuration Refactor** (5-8 hours)

- Centralize config loading
- Use configuration library
- **Result**: 13 stages use one pattern

---

### Phase 3: Refactor Domains (20-30 hours)

**Using Refactored Bases from Phase 2**:

**3.1. GraphRAG Domain** (8-12 hours)

- Remove agent init boilerplate (use BaseAgent)
- Remove error handling boilerplate (use library)
- Remove retry boilerplate (use library)
- Add tracing
- **Result**: ~200-300 lines removed

**3.2. Ingestion Domain** (6-10 hours)

- Same refactors as GraphRAG
- **Result**: ~150-200 lines removed

**3.3. RAG Domain** (4-6 hours)

- Refactor agents to use BaseAgent
- **Result**: ~100-150 lines removed

**3.4. Chat Domain** (2-4 hours)

- Already extracted, minimal work
- Add error handling, tracing

---

### Phase 4: Enhanced Patterns (10-15 hours)

**4.1. Validation Library** (8-12 hours)

- Business rule validation
- Validation aggregation

**4.2. Caching Library** (5-8 hours)

- LRU cache
- TTL cache
- Decorators

**4.3. Database Library Enhancement** (8-12 hours)

- Transactions
- Batch operations
- Query builders

---

## 📊 Complete Refactor Effort Estimate

| Phase     | Focus                 | Effort           | Priority |
| --------- | --------------------- | ---------------- | -------- |
| **1**     | Build Libraries       | 30-40 hours      | Critical |
| **2**     | Refactor Bases        | 15-20 hours      | Critical |
| **3**     | Refactor Domains      | 20-30 hours      | High     |
| **4**     | Enhanced Patterns     | 20-30 hours      | Medium   |
| **Total** | **Complete Refactor** | **85-120 hours** | -        |

**Timeline**: 8-12 weeks @ 10-15 hours/week

---

## 🎯 Recommended Execution Plan

### Sprint 1 (Week 1-2): Core Libraries - Part 1

**Build**:

1. Logging library (8-12 hours)
2. Error handling library (10-15 hours)
3. Retry library (5-8 hours)

**Total**: 23-35 hours  
**Outcome**: Foundation libraries ready

---

### Sprint 2 (Week 3-4): Core Libraries - Part 2 + Base Classes

**Build**:

1. Tracing library (10-15 hours)
2. Metrics library (8-12 hours)
3. Refactor BaseAgent (5-8 hours)
4. Refactor BaseStage (5-8 hours)

**Total**: 28-43 hours  
**Outcome**: Complete libraries + improved bases

---

### Sprint 3 (Week 5-6): Domain Refactoring

**Apply**:

1. GraphRAG domain (8-12 hours)
2. Ingestion domain (6-10 hours)
3. RAG domain (4-6 hours)
4. Chat domain (2-4 hours)

**Total**: 20-32 hours  
**Outcome**: All domains using libraries

---

### Sprint 4 (Week 7-8): Enhanced Patterns

**Build**:

1. Validation library (8-12 hours)
2. Caching library (5-8 hours)
3. Database library enhancement (8-12 hours)
4. Final cleanup and testing (5-8 hours)

**Total**: 26-40 hours  
**Outcome**: Complete refactor

---

## 💡 Key Insights

### Naming Considerations:

**Option A: "Libraries"** (Recommended)

- Clear purpose (reusable technical patterns)
- Familiar term
- Location: `core/libraries/`

**Option B: "Support"**

- Emphasizes supporting role
- Location: `core/support/`

**Option C: "Commons"**

- Common across domains
- Location: `core/commons/`

**Recommendation**: **"Libraries"** - clearest intent

---

### Domain Organization:

**Option A: Keep Current** (Type-first in business/)

```
business/agents/graphrag/
business/stages/graphrag/
business/services/graphrag/
```

**Option B: Domain-First** (Recommended for deep refactor)

```
business/domains/graphrag/agents/
business/domains/graphrag/stages/
business/domains/graphrag/services/
```

**Benefit of Domain-First**: All GraphRAG code together, easier to see full domain

---

## 🎯 Decision Points

### Decision 1: Library Scope

**Question**: Build all 10 libraries or start with critical 5?

**Option A: Critical 5 First** (Recommended)

- Logging, error_handling, retry, tracing, metrics
- ~45-60 hours
- High impact

**Option B: All 10**

- Complete but longer
- ~85-120 hours
- Comprehensive

---

### Decision 2: Domain Reorganization

**Question**: Keep type-first or switch to domain-first?

**Option A: Keep Type-First**

- Less disruption
- Already organized
- Refactor internals only

**Option B: Switch to Domain-First** (Recommended)

- Better for deep domains (graphrag, ingestion)
- All domain code together
- Clearer bounded contexts

---

### Decision 3: Timing

**Question**: When to start library refactor?

**Option A: After GraphRAG Validation** (Recommended)

- Wait for 13k run + Louvain fix
- Validate system works
- Then refactor from solid base

**Option B: Start Now**

- Parallel with GraphRAG run
- Don't wait
- Risk: changes while validating

---

## 📋 Next Steps to Start

**Immediate** (To Plan Libraries):

1. ✅ Review this analysis
2. → Decide on library scope (critical 5 vs. all 10)
3. → Decide on domain organization (keep vs. reorganize)
4. → Create detailed library implementation plans
5. → Start with logging library (foundation)

**Monday** (GraphRAG First):

1. Fix community detection
2. Validate graph
3. **Then** start library refactor

---

**This analysis provides the complete picture. Ready to create detailed implementation plans for each library when you decide on scope!** 🚀
