# CORE Layer - LLM Context Guide

**Layer Purpose**: Definitions - Fundamental contracts, models, base classes, configuration

---

## What Belongs in CORE Layer

✅ **Pydantic models** (data structures, validation)  
✅ **Base classes** (BaseStage, BaseAgent, BasePipeline)  
✅ **Pure utility functions** (text processing, domain helpers)  
✅ **Configuration classes** (env-based configs)

❌ **Implementation logic** (goes in BUSINESS)  
❌ **External dependencies** (goes in DEPENDENCIES)  
❌ **Entry points** (goes in APP)

---

## Structure

```
core/
├── models/             # Data models (Pydantic)
│   ├── graphrag.py     # EntityModel, RelationshipModel, etc.
│   └── config.py       # BaseStageConfig
│
├── base/               # Base classes
│   ├── stage.py        # BaseStage
│   └── agent.py        # BaseAgent
│
├── domain/             # Domain utilities (pure functions)
│   ├── text.py         # Text processing
│   ├── enrichment.py   # Enrichment utilities
│   ├── compression.py  # Compression utilities
│   └── concurrency.py  # Concurrency helpers
│
└── config/             # Configuration management
    ├── paths.py        # Constants (DB_NAME, COLL_*)
    ├── runtime.py      # Runtime configuration
    └── graphrag.py     # GraphRAG configs
```

---

## Import Pattern

CORE layer can only import from DEPENDENCIES and external libraries:

```python
# core/models/graphrag.py
from pydantic import BaseModel, Field    # External library ✅
from typing import List, Optional        # Standard library ✅
# NO imports from APP or BUSINESS ❌
```

**Cannot import from**: APP ❌, BUSINESS ❌

---

## Example: Pydantic Model

```python
# core/models/graphrag.py
from pydantic import BaseModel, Field
from typing import List
import hashlib

class EntityModel(BaseModel):
    """Entity extracted from text."""
    name: str = Field(min_length=1, max_length=200)
    type: EntityType
    description: str = Field(min_length=10, max_length=2000)
    confidence: float = Field(ge=0.0, le=1.0)

    @classmethod
    def generate_id(cls, name: str) -> str:
        """Generate deterministic ID."""
        return hashlib.md5(name.lower().encode()).hexdigest()
```

**Key**: No business logic, just structure and validation

---

## Example: Base Class

```python
# core/base/stage.py
from typing import Any, Dict, Iterable
from core.models.config import BaseStageConfig

class BaseStage:
    """Abstract base for all pipeline stages."""

    name = "base"
    ConfigCls = BaseStageConfig

    def setup(self):
        """Initialize stage resources."""
        pass

    def iter_docs(self) -> Iterable[Dict[str, Any]]:
        """Return documents to process."""
        raise NotImplementedError

    def handle_doc(self, doc: Dict[str, Any]):
        """Process a single document."""
        raise NotImplementedError
```

**Key**: Defines contract, no implementation details

---

## Files in CORE Layer

### Models (2 files):

- `models/graphrag.py` - All GraphRAG Pydantic models (EntityModel, RelationshipModel, KnowledgeModel, ResolvedEntity, ResolvedRelationship, CommunitySummary)
- `models/config.py` - Base configuration classes (BaseStageConfig)

### Base Classes (2 files):

- `base/stage.py` - BaseStage abstract class
- `base/agent.py` - BaseAgent abstract class

### Domain Utilities (4 files):

- `domain/text.py` - Text normalization, cleaning (pure functions)
- `domain/enrichment.py` - Enrichment helpers (pure functions)
- `domain/compression.py` - Compression utilities
- `domain/concurrency.py` - Concurrency helpers

### Configuration (3 files):

- `config/paths.py` - Database and collection name constants
- `config/runtime.py` - Runtime configuration defaults
- `config/graphrag.py` - All GraphRAG configuration classes

---

## When Adding New Code

**Ask**: Does this define structure or contracts?

- **Yes** → CORE layer
- **No** → Check other layers

**Examples**:

- New Pydantic model → `core/models/`
- New base class → `core/base/`
- New pure utility function → `core/domain/`
- New configuration class → `core/config/`

**Don't Add**:

- Database queries → BUSINESS (services) or DEPENDENCIES (adapters)
- LLM calls → BUSINESS (agents)
- CLI parsing → APP

---

**For detailed information, see**: `documentation/architecture/CORE.md`
