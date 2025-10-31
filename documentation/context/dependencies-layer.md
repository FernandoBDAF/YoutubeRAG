# DEPENDENCIES Layer - LLM Context Guide

**Layer Purpose**: Infrastructure - Adapters for external systems (databases, APIs, LLMs)

---

## What Belongs in DEPENDENCIES Layer

✅ **Database clients** (MongoDB, Redis, etc.)  
✅ **LLM provider wrappers** (OpenAI, Anthropic, etc.)  
✅ **External API clients** (YouTube, embedding services, etc.)  
✅ **Observability** (logging, monitoring, tracing)

❌ **Business logic** (goes in BUSINESS)  
❌ **Data models** (goes in CORE)  
❌ **CLIs or UIs** (goes in APP)

---

## Structure

```
dependencies/
├── database/           # Database adapters
│   └── mongodb.py      # MongoDBClient
│
├── llm/                # LLM provider adapters
│   ├── openai.py       # OpenAIClient
│   └── rate_limit.py   # Rate limiting
│
├── external/           # External API clients
│   └── youtube.py      # YouTube API (future)
│
└── observability/      # Logging, monitoring
    ├── logging.py      # Logging setup
    └── log_utils.py    # Log utilities (Timer, etc.)
```

---

## Import Pattern

DEPENDENCIES layer can import from CORE and external libraries:

```python
# dependencies/database/mongodb.py
from pymongo import MongoClient           # External library ✅
from core.config.paths import DB_NAME     # CORE ✅
# NO imports from APP or BUSINESS ❌
```

**Cannot import from**: APP ❌, BUSINESS ❌

---

## Example: Database Adapter

```python
# dependencies/database/mongodb.py
import os
from typing import Optional
from pymongo import MongoClient

class MongoDBClient:
    """Singleton MongoDB client wrapper."""

    _instance: Optional[MongoClient] = None

    @classmethod
    def get_instance(cls, uri: Optional[str] = None) -> MongoClient:
        """Get MongoDB client (singleton)."""
        if cls._instance is None:
            connection_uri = uri or os.getenv("MONGODB_URI")
            cls._instance = MongoClient(connection_uri)
        return cls._instance

    @classmethod
    def get_collection(cls, db_name: str, coll_name: str):
        """Get collection handle."""
        client = cls.get_instance()
        return client[db_name][coll_name]
```

**Key**: Abstracts PyMongo, provides clean interface

---

## Example: LLM Adapter

```python
# dependencies/llm/openai.py
import os
from typing import Optional
from openai import OpenAI

class OpenAIClient:
    """Singleton OpenAI client wrapper."""

    _instance: Optional[OpenAI] = None

    @classmethod
    def get_instance(cls, api_key: Optional[str] = None) -> OpenAI:
        """Get OpenAI client (singleton)."""
        if cls._instance is None:
            key = api_key or os.getenv("OPENAI_API_KEY")
            if not key:
                raise RuntimeError("OPENAI_API_KEY required")
            cls._instance = OpenAI(api_key=key, timeout=60)
        return cls._instance
```

**Key**: Centralized client creation, configuration

---

## Files in DEPENDENCIES Layer

### Database (1 file):

- `database/mongodb.py` - MongoDBClient class, get_mongo_client function, read_collection function

### LLM (2 files):

- `llm/openai.py` - OpenAIClient class, get_openai_client function
- `llm/rate_limit.py` - Rate limiting utilities

### Observability (2 files):

- `observability/logging.py` - setup_logging, get_logger, create_timestamped_log_path
- `observability/log_utils.py` - Timer class, logging utilities

---

## Key Design Patterns

### 1. Singleton Pattern

**Why**: One client instance per application  
**Benefit**: Connection pooling, resource management

### 2. Backward Compatibility

**Why**: Gradual migration from old imports  
**Benefit**: Zero breaking changes

```python
# New way (recommended)
from dependencies.database.mongodb import MongoDBClient
client = MongoDBClient.get_instance()

# Old way (still works)
from dependencies.database.mongodb import get_mongo_client
client = get_mongo_client()
```

### 3. Environment-Based Configuration

**Why**: Different configs for dev/staging/production  
**Benefit**: No hardcoded credentials

```python
# All config from environment
uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
api_key = os.getenv("OPENAI_API_KEY")
```

---

## When Adding New Code

**Ask**: Does this adapt an external system?

- **Yes** → DEPENDENCIES layer
- **No** → Check other layers

**Examples**:

- New database (Redis) → `dependencies/database/redis.py`
- New LLM provider (Anthropic) → `dependencies/llm/anthropic.py`
- New external API (GitHub) → `dependencies/external/github.py`
- New monitoring (Sentry) → `dependencies/observability/sentry.py`

**Don't Add**:

- Query logic → BUSINESS (services or queries)
- Data models → CORE
- CLI tools → APP

---

## Testing Benefits

**Easy to Mock**:

```python
# In tests, mock entire DEPENDENCIES layer
from unittest.mock import Mock

mock_db = Mock(spec=MongoDBClient)
mock_llm = Mock(spec=OpenAIClient)

# Business logic runs with mocks
stage = MyStage()
stage.db_client = mock_db
stage.llm_client = mock_llm
stage.run()  # No real DB or LLM calls!
```

---

**For implementation details, see**: `documentation/architecture/`
