# Refactoring TODO List

**Created**: October 31, 2025  
**Purpose**: Track code improvements identified during folder structure migration  
**Status**: Documentation only - **NO CHANGES IMPLEMENTED YET** ⚠️

---

## ⚠️ HARD RESTRICTION

**DO NOT CHANGE WORKING CODE DURING MIGRATION!**

This file tracks improvements to implement **AFTER** folder structure migration is complete.

**Migration First, Refactor Second**

---

## How to Use This File

### During Migration:

1. When you spot repetitive code → **Document it here**
2. When you see improvement opportunities → **Add to TODO**
3. When you want to refactor → **DON'T!** → Add to this list instead
4. **Continue migration** without breaking working code

### After Migration:

1. Review all TODOs
2. Prioritize by effort/impact
3. Plan refactor sprints
4. Execute improvements safely with tests

---

## Categories

- [x] **Code Repetition** - Patterns repeated across files
- [x] **Architecture Improvements** - Design patterns, abstractions
- [x] **Performance Optimizations** - Speed, memory, efficiency
- [x] **Code Quality** - Types, docs, error handling

---

## Code Repetition Issues 🔁

### 1. Agent Initialization Pattern

**Discovered During**: Phase 3 (Move Agents)  
**Location**: All agent files (`agents/*.py`)  
**Files Affected**: 12 agent files

**Current Problem**:

```python
# Repeated in every agent __init__:
self.llm_client = llm_client
self.model_name = model_name
self.temperature = temperature
self.max_retries = max_retries
```

**Proposed Solution**:

```python
# Extend BaseAgent with common initialization
class BaseAgent:
    def __init__(self, llm_client, model_name="gpt-4o-mini",
                 temperature=0.1, max_retries=3, **kwargs):
        self.llm_client = llm_client
        self.model_name = model_name
        self.temperature = temperature
        self.max_retries = max_retries
        self._setup(**kwargs)

    def _setup(self, **kwargs):
        """Override in subclasses for specific setup"""
        pass
```

**Estimated Effort**: 2-3 hours  
**Priority**: Medium  
**Breaking Changes**: None (backward compatible)  
**Benefits**: Reduce ~50 lines across 12 files

---

### 2. Stage Collection Access Pattern

**Discovered During**: Phase 4 (Move Stages)  
**Location**: All stage files  
**Files Affected**: 11 stage files

**Current Problem**:

```python
# Repeated in every stage:
src_db = self.config.read_db_name or self.config.db_name
src_coll_name = self.config.read_coll or COLL_CHUNKS
collection = self.get_collection(src_coll_name, io="read", db_name=src_db)
```

**Proposed Solution**:

```python
# Add helper to BaseStage:
def get_read_collection(self, default_coll=None):
    """Get read collection with config fallbacks"""
    src_db = self.config.read_db_name or self.config.db_name
    src_coll = self.config.read_coll or default_coll
    return self.get_collection(src_coll, io="read", db_name=src_db)

# Usage in stages:
collection = self.get_read_collection(COLL_CHUNKS)
```

**Estimated Effort**: 1-2 hours  
**Priority**: Medium  
**Breaking Changes**: None (additive)  
**Benefits**: Reduce ~30 lines across 11 files

---

### 3. LLM Client Initialization

**Discovered During**: Phase 3 (Move Agents)  
**Location**: All stages and agents using LLM  
**Files Affected**: 8 files

**Current Problem**:

```python
# Repeated everywhere:
from openai import OpenAI
self.llm_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

**Proposed Solution**:

```python
# Use dependency injection from DEPENDENCIES layer:
from dependencies.llm.openai import get_openai_client

# In setup():
self.llm_client = get_openai_client()  # Singleton, configured
```

**Estimated Effort**: 2 hours  
**Priority**: High (aligns with layer architecture)  
**Breaking Changes**: None (internal change)  
**Benefits**: Centralize client config, easier testing

---

### 4. MongoDB Collection Management

**Discovered During**: Phase 2 (Extract Dependencies)  
**Location**: All stages, services  
**Files Affected**: 15+ files

**Current Problem**:

```python
# Two patterns coexist:
# Pattern 1: Direct access
client = get_mongo_client()
db = client[DB_NAME]
coll = db[COLL_CHUNKS]

# Pattern 2: Via stage helper
coll = self.get_collection(COLL_CHUNKS, io="read")
```

**Proposed Solution**:

```python
# Standardize on MongoDBClient from dependencies:
from dependencies.database.mongodb import MongoDBClient

client = MongoDBClient.get_instance()
coll = client.get_collection(DB_NAME, COLL_CHUNKS)
```

**Estimated Effort**: 3-4 hours  
**Priority**: High (architectural consistency)  
**Breaking Changes**: Internal only  
**Benefits**: Single pattern, easier to mock for testing

---

### 5. Configuration Loading Pattern

**Discovered During**: Phase 1 (Move Core)  
**Location**: All stage and pipeline files  
**Files Affected**: 13 files

**Current Problem**:

```python
# Repeated in every stage/pipeline:
@classmethod
def from_args_env(cls, args, env, default_db):
    # Parse args, load from env, create config
    # ~20 lines of boilerplate per file
```

**Proposed Solution**:

```python
# Create ConfigLoader in CORE:
class ConfigLoader:
    @staticmethod
    def load_stage_config(ConfigClass, args, env, defaults):
        # Centralized parsing logic
        pass

# Usage:
config = ConfigLoader.load_stage_config(MyStageConfig, args, env, defaults)
```

**Estimated Effort**: 4-5 hours  
**Priority**: Low (works fine as-is)  
**Breaking Changes**: Could break existing code  
**Benefits**: DRY, consistent config handling

---

## Architecture Improvements 🏗️

### 6. Dependency Injection for Agents

**Discovered During**: Phase 3-4 (Agents/Stages)  
**Location**: Stage setup methods  
**Files Affected**: All stages

**Current Problem**:

```python
# Stages directly instantiate agents:
self.agent = GraphExtractionAgent(
    llm_client=self.llm_client,
    model_name=self.config.model_name,
    temperature=self.config.temperature
)
```

**Proposed Solution**:

```python
# Agent factory in BUSINESS layer:
class AgentFactory:
    @staticmethod
    def create_extraction_agent(config):
        llm_client = get_openai_client()
        return GraphExtractionAgent(llm_client, config.model_name, config.temperature)

# Usage:
self.agent = AgentFactory.create_extraction_agent(self.config)
```

**Estimated Effort**: 3-4 hours  
**Priority**: Medium  
**Breaking Changes**: None (encapsulates creation)  
**Benefits**: Easier testing, centralized creation logic

---

### 7. Pipeline Stage Registry Pattern

**Discovered During**: Phase 5 (Pipelines)  
**Location**: Pipeline files  
**Files Affected**: 2 pipeline files

**Current Problem**:

```python
# Stages hardcoded in pipeline:
from business.stages.graphrag.extraction import GraphExtractionStage
from business.stages.graphrag.entity_resolution import EntityResolutionStage
# ... 4 more imports

stages = [
    GraphExtractionStage(),
    EntityResolutionStage(),
    # ... hardcoded list
]
```

**Proposed Solution**:

```python
# Stage registry pattern (already partially implemented):
STAGE_REGISTRY = {
    "graph_extraction": GraphExtractionStage,
    "entity_resolution": EntityResolutionStage,
    # ...
}

# Pipeline uses registry:
stage_names = ["graph_extraction", "entity_resolution", ...]
stages = [STAGE_REGISTRY[name]() for name in stage_names]
```

**Estimated Effort**: 2 hours  
**Priority**: Low (nice-to-have)  
**Breaking Changes**: None (internal)  
**Benefits**: Dynamic stage composition

---

### 8. Chat Feature as Reusable Business Logic

**Discovered During**: Chat.py review  
**Location**: `chat.py` (1,370 lines)  
**Files Affected**: 1 monolithic file

**Current Problem**:

- All chat logic in single entry point file
- Hard to reuse chat components elsewhere
- UI can't easily use same logic

**Proposed Solution**:
See "Chat Feature Extraction Plan" in main refactor plan

**Estimated Effort**: 2-3 hours  
**Priority**: High (already planned in Phase 5.5)  
**Breaking Changes**: None (extract, don't modify)  
**Benefits**: Reusable chat logic, cleaner CLI

---

## Performance Optimizations ⚡

### 9. Lazy Loading for LLM Clients

**Discovered During**: Phase 2 (Dependencies)  
**Location**: Stages and agents  
**Files Affected**: 8 files

**Current Problem**:

```python
# LLM client created in setup() even if not used:
def setup(self):
    self.llm_client = OpenAI(...)  # Always created
    # But only used in handle_doc() for some docs
```

**Proposed Solution**:

```python
# Lazy property:
@property
def llm_client(self):
    if not hasattr(self, '_llm_client'):
        self._llm_client = get_openai_client()
    return self._llm_client
```

**Estimated Effort**: 1 hour  
**Priority**: Low (minor gain)  
**Breaking Changes**: None  
**Benefits**: Faster stage initialization, lower memory

---

### 10. MongoDB Connection Pooling

**Discovered During**: Phase 2 (Dependencies)  
**Location**: `dependencies/database/mongodb.py`  
**Files Affected**: 1 file

**Current Problem**:

```python
# Simple singleton, no explicit pooling config:
_instance = MongoClient(uri)
```

**Proposed Solution**:

```python
# Explicit connection pool configuration:
_instance = MongoClient(
    uri,
    maxPoolSize=50,
    minPoolSize=10,
    maxIdleTimeMS=30000
)
```

**Estimated Effort**: 30 min  
**Priority**: Low (PyMongo pools by default)  
**Breaking Changes**: None  
**Benefits**: Explicit control, better for high concurrency

---

## Code Quality Improvements ✨

### 11. Type Hints Coverage

**Discovered During**: All phases  
**Location**: Everywhere  
**Files Affected**: 100+ files

**Current Problem**:

```python
# Many functions lack type hints:
def extract_from_chunk(self, chunk):  # What's the type of chunk?
    ...
```

**Proposed Solution**:

```python
# Add comprehensive type hints:
from typing import Dict, Any
def extract_from_chunk(self, chunk: Dict[str, Any]) -> KnowledgeModel:
    ...
```

**Estimated Effort**: 10-15 hours (across all files)  
**Priority**: Medium  
**Breaking Changes**: None (additive)  
**Benefits**: Better IDE support, catch type errors early

---

### 12. Docstring Standardization

**Discovered During**: All phases  
**Location**: Everywhere  
**Files Affected**: 100+ files

**Current Problem**:

- Mix of Google, NumPy, and no docstrings
- Inconsistent documentation

**Proposed Solution**:

```python
# Standardize on Google style:
def extract_from_chunk(self, chunk: Dict[str, Any]) -> KnowledgeModel:
    """Extract entities and relationships from a text chunk.

    Args:
        chunk: Dictionary containing chunk_text and metadata

    Returns:
        KnowledgeModel with extracted entities and relationships

    Raises:
        ValueError: If chunk_text is missing or empty
    """
```

**Estimated Effort**: 8-10 hours  
**Priority**: Low  
**Breaking Changes**: None  
**Benefits**: Better documentation, easier onboarding

---

### 13. Error Message Improvements

**Discovered During**: All phases  
**Location**: Exception handling across files  
**Files Affected**: 50+ files

**Current Problem**:

```python
# Generic error messages:
raise ValueError("Invalid data")
logger.error("Failed")
```

**Proposed Solution**:

```python
# Actionable error messages:
raise ValueError(
    f"Invalid chunk data: missing 'chunk_text' field. "
    f"Chunk ID: {chunk.get('chunk_id', 'unknown')}"
)
logger.error(
    "Graph extraction failed for chunk %s: %s",
    chunk_id, str(e), exc_info=True
)
```

**Estimated Effort**: 3-4 hours  
**Priority**: Medium  
**Breaking Changes**: None  
**Benefits**: Faster debugging, better logs

---

### 14. Logging Level Consistency

**Discovered During**: All phases  
**Location**: Logger calls across files  
**Files Affected**: 80+ files

**Current Problem**:

```python
# Inconsistent logging levels:
logger.info("Processing chunk...")  # Should be DEBUG
logger.debug("Stage failed!")       # Should be ERROR
```

**Proposed Solution**:

- **DEBUG**: Detailed flow, variable values
- **INFO**: Stage start/complete, counts
- **WARNING**: Skipped items, fallbacks
- **ERROR**: Failures, exceptions

**Estimated Effort**: 2-3 hours  
**Priority**: Low  
**Breaking Changes**: None  
**Benefits**: Cleaner logs, better signal/noise ratio

---

## Summary Statistics

**Total TODOs**: 14  
**Estimated Total Effort**: 45-65 hours  
**High Priority**: 3 items (LLM client, MongoDB patterns, Chat extraction)  
**Medium Priority**: 6 items  
**Low Priority**: 5 items

**Most Impactful**:

1. Chat Feature Extraction (Phase 5.5) - Already planned
2. LLM Client Dependency Injection - Architectural consistency
3. MongoDB Pattern Standardization - Testing & consistency
4. Agent Initialization Pattern - Reduce 50+ lines

**Quick Wins** (<2 hours each):

- MongoDB Connection Pooling (30 min)
- Lazy Loading for LLM Clients (1 hour)
- Stage Collection Access Helper (1-2 hours)
- Pipeline Stage Registry (2 hours)

---

## Notes

- This list will grow during migration
- Prioritize after migration complete
- Group related TODOs into refactor sprints
- Always test after each refactor
- Document breaking changes clearly

---

**Last Updated**: October 31, 2025  
**Status**: Active - growing during migration
