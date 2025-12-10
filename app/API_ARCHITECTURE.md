# GraphRAG API Architecture

## Executive Summary

This document defines the standardized architecture for all APIs in the GraphRAG `app/` folder. It establishes patterns based on the well-structured `stages_api/` module and proposes refactoring the `api/` folder (graph data APIs) to follow the same conventions.

---

## Current State Analysis

### ✅ `stages_api/` (Well-Organized)

```
app/stages_api/
├── __init__.py          # Package exports
├── api.py               # Central router with handle_request()
├── server.py            # Single HTTP server entry point
├── constants.py         # Shared constants
├── metadata.py          # Stage metadata logic
├── validation.py        # Config validation logic
├── execution.py         # Pipeline execution logic
├── repository.py        # Database persistence
├── field_metadata.py    # Field introspection
└── docs/                # Documentation folder
    ├── README.md
    ├── API_DESIGN_SPECIFICATION.md
    ├── postman_collection.json
    └── ...
```

**Strengths:**
- Central routing in `api.py` → Single place to see all endpoints
- Clean separation: routing vs business logic
- Single `server.py` entry point
- Comprehensive documentation

---

### ⚠️ `api/` (Needs Refactoring)

```
app/graph_api/
├── __init__.py          # Empty
├── entities.py          # Handler + Logic + Standalone server
├── communities.py       # Handler + Logic + Standalone server
├── relationships.py     # Handler + Logic + Standalone server
├── ego_network.py       # Handler + Logic + Standalone server
├── export.py            # Handler + Logic + Standalone server
├── graph_statistics.py  # Handler + Logic + Standalone server
├── metrics.py           # Handler + Logic + Standalone server
├── quality_metrics.py   # Handler + Logic + Standalone server
├── performance_metrics.py # Handler + Logic + Standalone server
├── pipeline_control.py  # Handler + Logic + Standalone server
├── pipeline_progress.py # Handler + Logic + Standalone server
└── pipeline_stats.py    # Handler + Logic + Standalone server
```

**Issues:**
- No central routing → Hard to see all endpoints
- Duplicated boilerplate (CORS, JSON handling, error handling)
- Each file is a standalone server → Can't run unified API
- No documentation folder
- Mixed responsibilities (routing + logic in same file)

---

## Proposed Architecture

### Target Structure for `api/` (Graph Data API)

```
app/graph_api/
├── __init__.py              # Package exports
├── router.py                # Central router (like stages_api/api.py)
├── server.py                # Single HTTP server entry point
├── constants.py             # Shared constants (DB names, collection names)
│
├── handlers/                # Business logic modules (no HTTP code)
│   ├── __init__.py
│   ├── entities.py          # search_entities(), get_entity_details()
│   ├── communities.py       # search_communities(), get_community_details()
│   ├── relationships.py     # search_relationships()
│   ├── ego_network.py       # get_ego_network()
│   ├── export.py            # export_graph_json(), export_graph_csv()
│   ├── statistics.py        # get_graph_statistics()
│   └── query.py             # unified_query() (RAG/GraphRAG)
│
├── pipeline/                # Pipeline monitoring (keep separate from stages_api)
│   ├── __init__.py
│   ├── control.py           # pause, resume (if different from stages_api)
│   ├── progress.py          # real-time progress
│   └── stats.py             # historical stats
│
└── docs/                    # Documentation
    ├── README.md
    ├── API_SPECIFICATION.md
    ├── ENDPOINTS_REFERENCE.md
    └── postman_collection.json
```

---

## Design Patterns

### Pattern 1: Central Router

All HTTP routing logic in one file (`router.py`):

```python
# app/graph_api/router.py

"""
Graph Data API - Central Router

Routes requests to appropriate handlers.
"""

from typing import Dict, Any, Optional
from .handlers import entities, communities, relationships, ego_network, export, statistics

def handle_request(method: str, path: str, params: Dict[str, Any], body: Optional[Dict] = None) -> tuple:
    """
    Route HTTP requests to handlers.
    
    Args:
        method: HTTP method (GET, POST)
        path: URL path without /api/ prefix
        params: Query parameters
        body: Request body for POST
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    path = path.lstrip("/")
    parts = path.split("/")
    db_name = params.get("db_name", "2025-12")
    
    # Route: GET /entities/search
    if method == "GET" and path.startswith("entities"):
        if len(parts) == 1 or parts[1] == "search":
            return entities.search(
                db_name=db_name,
                query=params.get("q"),
                entity_type=params.get("type"),
                limit=int(params.get("limit", 50)),
                offset=int(params.get("offset", 0)),
            ), 200
        elif len(parts) == 2:
            # GET /entities/{entity_id}
            return entities.get_details(db_name, parts[1]), 200
    
    # Route: GET /communities/search
    if method == "GET" and path.startswith("communities"):
        if len(parts) == 1 or parts[1] == "search":
            return communities.search(
                db_name=db_name,
                level=params.get("level"),
                limit=int(params.get("limit", 50)),
            ), 200
        elif parts[1] == "levels":
            return communities.get_levels(db_name), 200
        elif len(parts) == 2:
            return communities.get_details(db_name, parts[1]), 200
    
    # ... more routes
    
    return {"error": f"Not found: {method} /{path}"}, 404
```

---

### Pattern 2: Pure Handler Functions

Handler modules contain only business logic, no HTTP code:

```python
# app/graph_api/handlers/entities.py

"""
Entity Handler - Business Logic

Pure functions for entity operations.
No HTTP handling - that's in router.py
"""

from typing import Dict, Any, Optional, List
from dependencies.database.mongodb import get_mongo_client
from business.services.graphrag.indexes import get_graphrag_collections


def search(
    db_name: str,
    query: Optional[str] = None,
    entity_type: Optional[str] = None,
    min_confidence: Optional[float] = None,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """Search entities with filters."""
    client = get_mongo_client()
    db = client[db_name]
    # ... implementation
    return {"entities": [...], "total": n, "has_more": bool}


def get_details(db_name: str, entity_id: str) -> Optional[Dict[str, Any]]:
    """Get entity with relationships."""
    # ... implementation
    return {"entity_id": ..., "relationships": [...]}
```

---

### Pattern 3: Single Server Entry Point

One server file that starts the unified API:

```python
# app/graph_api/server.py

"""
Graph Data API Server

Single entry point for all graph data endpoints.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
from .router import handle_request


class GraphAPIHandler(BaseHTTPRequestHandler):
    """HTTP handler for Graph Data API"""
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.replace("/api/", "")
        params = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        
        result, status = handle_request("GET", path, params)
        self._send_json(result, status)
    
    def do_POST(self):
        # ... similar pattern
        pass
    
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())


def run_server(port: int = 8081):
    server = HTTPServer(("0.0.0.0", port), GraphAPIHandler)
    print(f"Graph API running on http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
```

---

### Pattern 4: Shared Constants

Centralized constants for consistency:

```python
# app/graph_api/constants.py

"""
Graph Data API Constants
"""

# Default database (can be overridden by query param)
DEFAULT_DB_NAME = "2025-12"

# Collection names (from business/services/graphrag/indexes.py)
COLL_ENTITIES = "entities"
COLL_RELATIONS = "relations"
COLL_COMMUNITIES = "communities"
COLL_CHUNKS = "video_chunks"

# Pagination defaults
DEFAULT_LIMIT = 50
MAX_LIMIT = 500

# API version
API_VERSION = "1.0.0"
```

---

## API Naming Conventions

### URL Structure

```
/api/{resource}                   # List/Search
/api/{resource}/{id}              # Get by ID
/api/{resource}/{id}/{sub}        # Sub-resource
/api/{action}                     # Action endpoints
```

### Examples

| Pattern | Example | Description |
|---------|---------|-------------|
| List/Search | `GET /api/entities?q=...` | Search entities |
| Get by ID | `GET /api/entities/{id}` | Get entity details |
| Sub-resource | `GET /api/entities/{id}/relationships` | Entity's relationships |
| Action | `POST /api/query` | Execute unified query |
| Levels | `GET /api/communities/levels` | Get hierarchy info |

### Query Parameters

| Parameter | Type | Used For |
|-----------|------|----------|
| `db_name` | string | Database override |
| `q` | string | Search query |
| `type` | string | Filter by type |
| `limit` | int | Pagination limit |
| `offset` | int | Pagination offset |
| `sort_by` | string | Sort field |

---

## Full Endpoint Reference

### Graph Data API (`/api/` on port 8081)

| Method | Endpoint | Handler | Description |
|--------|----------|---------|-------------|
| GET | `/entities/search` | `entities.search()` | Search entities |
| GET | `/entities/{id}` | `entities.get_details()` | Entity + relationships |
| GET | `/communities/search` | `communities.search()` | Search communities |
| GET | `/communities/{id}` | `communities.get_details()` | Community + members |
| GET | `/communities/levels` | `communities.get_levels()` | Hierarchy stats |
| GET | `/relationships/search` | `relationships.search()` | Search relationships |
| GET | `/ego/network/{entity_id}` | `ego_network.get()` | Ego network |
| GET | `/export/{format}` | `export.by_format()` | Export graph |
| GET | `/statistics` | `statistics.get()` | Graph stats |
| POST | `/query` | `query.execute()` | Unified RAG query |
| GET | `/health` | `health.check()` | Health check |

### Stages API (`/api/v1/` on port 8080)

Already well-organized. See `app/stages_api/docs/API_DESIGN_SPECIFICATION.md`.

---

## Implementation Plan

### Phase 1: Create Structure (No Breaking Changes)

1. Create new directory structure:
   ```bash
   mkdir -p app/graph_api/handlers
   mkdir -p app/graph_api/docs
   ```

2. Create new files:
   - `app/graph_api/router.py` - Central routing
   - `app/graph_api/server.py` - HTTP server
   - `app/graph_api/constants.py` - Shared constants

3. Keep existing files working (legacy support)

### Phase 2: Migrate Handlers

For each existing file (e.g., `entities.py`):

1. Extract pure functions to `handlers/entities.py`
2. Add routes to `router.py`
3. Mark old handler class as deprecated

```python
# entities.py (after migration)
"""
DEPRECATED: Use app.graph_api.handlers.entities instead.
This file kept for backward compatibility.
"""
from .handlers.entities import search_entities, get_entity_details

# Legacy handler (will be removed in v2)
class EntityAPIHandler(BaseHTTPRequestHandler):
    # ... keep for now
```

### Phase 3: Documentation

1. Create `docs/README.md` - Overview
2. Create `docs/API_SPECIFICATION.md` - Full spec
3. Create `docs/postman_collection.json` - Test collection
4. Update `GRAPHRAG_UI_IMPLEMENTATION_GUIDE.md` with new endpoints

### Phase 4: Unified Server

1. Test new `server.py` with all routes
2. Update deployment scripts
3. Deprecate standalone servers

---

## Server Configuration Summary

| API | Port | Entry Point | Purpose |
|-----|------|-------------|---------|
| Stages API | 8080 | `python -m app.stages_api.server` | Pipeline execution |
| Graph API | 8081 | `python -m app.graph_api.server` | Graph data queries |

### Future: Combined Gateway

```python
# app/gateway.py (future)
"""
Unified API Gateway

Routes to appropriate sub-API based on path prefix.
"""

def route(path):
    if path.startswith("/api/v1/stages") or path.startswith("/api/v1/pipelines"):
        return stages_api.handle_request(...)
    else:
        return graph_api.handle_request(...)
```

---

## Checklist

### Immediate Actions

- [ ] Create `app/graph_api/handlers/` directory
- [ ] Create `app/graph_api/router.py`
- [ ] Create `app/graph_api/server.py`
- [ ] Create `app/graph_api/constants.py`
- [ ] Create `app/graph_api/docs/README.md`
- [ ] Migrate `entities.py` functions to `handlers/entities.py`
- [ ] Migrate `communities.py` functions to `handlers/communities.py`
- [ ] Migrate `relationships.py` functions to `handlers/relationships.py`
- [ ] Migrate `ego_network.py` functions to `handlers/ego_network.py`
- [ ] Migrate `export.py` functions to `handlers/export.py`
- [ ] Migrate `graph_statistics.py` functions to `handlers/statistics.py`
- [ ] Add routes to `router.py` for all endpoints
- [ ] Test unified server on port 8081

### Documentation

- [ ] Create `API_SPECIFICATION.md`
- [ ] Create Postman collection
- [ ] Update `GRAPHRAG_UI_IMPLEMENTATION_GUIDE.md`

### Cleanup (After Validation)

- [ ] Mark legacy handlers as deprecated
- [ ] Remove standalone `if __name__ == "__main__"` blocks
- [ ] Remove duplicated CORS/JSON code

---

## Summary

| Aspect | `stages_api/` | `api/` (current) | `api/` (target) |
|--------|---------------|------------------|-----------------|
| Central Router | ✅ `api.py` | ❌ | ✅ `router.py` |
| Pure Handlers | ✅ Separate files | ❌ Mixed | ✅ `handlers/` |
| Single Server | ✅ `server.py` | ❌ 12 servers | ✅ `server.py` |
| Constants | ✅ `constants.py` | ❌ | ✅ `constants.py` |
| Documentation | ✅ `docs/` | ❌ | ✅ `docs/` |

---

*Document Version: 1.0*
*Last Updated: December 9, 2025*

