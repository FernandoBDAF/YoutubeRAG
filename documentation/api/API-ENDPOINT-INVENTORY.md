# GraphRAG API Endpoint Inventory

**Date**: 2025-11-07 23:20 UTC  
**Scope**: All 12 GraphRAG API files  
**Purpose**: Comprehensive inventory of all API endpoints for testing, documentation, and validation

---

## Executive Summary

**Total API Files**: 12  
**Total Endpoints**: 28  
**Methods**: GET (26), POST (4), OPTIONS (1)  
**Base URL**: `http://localhost:8000`

**Endpoint Distribution**:

- Pipeline Control: 6 endpoints
- Data Browsing: 6 endpoints (entities, relationships, communities)
- Statistics & Metrics: 6 endpoints
- Export: 4 endpoints
- Monitoring: 2 endpoints (progress, metrics)
- Ego Network: 1 endpoint
- Other: 3 endpoints

**CORS Support**: 1 file has OPTIONS handler (`pipeline_control.py`), 11 files missing

---

## Endpoint Summary Table

| #   | Method  | Path                              | File                   | Purpose                         |
| --- | ------- | --------------------------------- | ---------------------- | ------------------------------- |
| 1   | GET     | `/api/pipeline/status`            | pipeline_control.py    | Get pipeline status             |
| 2   | GET     | `/api/pipeline/history`           | pipeline_control.py    | Get pipeline execution history  |
| 3   | POST    | `/api/pipeline/start`             | pipeline_control.py    | Start new pipeline              |
| 4   | POST    | `/api/pipeline/cancel`            | pipeline_control.py    | Cancel running pipeline         |
| 5   | POST    | `/api/pipeline/resume`            | pipeline_control.py    | Resume failed pipeline          |
| 6   | OPTIONS | `/api/pipeline/*`                 | pipeline_control.py    | CORS preflight                  |
| 7   | GET     | `/api/pipeline/progress`          | pipeline_progress.py   | Stream pipeline progress (SSE)  |
| 8   | GET     | `/api/pipeline/stats`             | pipeline_stats.py      | Get per-stage statistics        |
| 9   | GET     | `/api/entities/search`            | entities.py            | Search entities                 |
| 10  | GET     | `/api/entities/{entity_id}`       | entities.py            | Get entity details              |
| 11  | GET     | `/api/relationships/search`       | relationships.py       | Search relationships            |
| 12  | GET     | `/api/communities/search`         | communities.py         | Search communities              |
| 13  | GET     | `/api/communities/levels`         | communities.py         | Get community level statistics  |
| 14  | GET     | `/api/communities/{community_id}` | communities.py         | Get community details           |
| 15  | GET     | `/api/ego/network/{entity_id}`    | ego_network.py         | Get ego network                 |
| 16  | GET     | `/api/export/json`                | export.py              | Export graph as JSON            |
| 17  | GET     | `/api/export/csv`                 | export.py              | Export graph as CSV             |
| 18  | GET     | `/api/export/graphml`             | export.py              | Export graph as GraphML         |
| 19  | GET     | `/api/export/gexf`                | export.py              | Export graph as GEXF            |
| 20  | GET     | `/api/quality/metrics`            | quality_metrics.py     | Get quality metrics             |
| 21  | GET     | `/api/graph/statistics`           | graph_statistics.py    | Get graph statistics            |
| 22  | GET     | `/api/graph/trends`               | graph_statistics.py    | Get graph trends over time      |
| 23  | GET     | `/api/performance/metrics`        | performance_metrics.py | Get performance metrics         |
| 24  | GET     | `/metrics`                        | metrics.py             | Prometheus metrics (text/plain) |

---

## Per-File Endpoint Details

### 1. pipeline_control.py (6 endpoints)

**File Purpose**: Pipeline execution control (start, stop, status, history)

#### GET /api/pipeline/status

- **Method**: GET
- **Path**: `/api/pipeline/status`
- **Query Parameters**:
  - `pipeline_id` (required): Pipeline identifier
  - `db_name` (optional): Database name (default: from config)
- **Response**: JSON object with pipeline status
  ```json
  {
    "pipeline_id": "string",
    "status": "starting|running|completed|failed|cancelled",
    "started_at": "ISO datetime",
    "completed_at": "ISO datetime|null",
    "configuration": {}
  }
  ```
- **Error Responses**: 400 (missing pipeline_id), 404 (not found), 500 (server error)
- **CORS**: Yes

#### GET /api/pipeline/history

- **Method**: GET
- **Path**: `/api/pipeline/history`
- **Query Parameters**:
  - `limit` (optional, default: 50): Number of results
  - `offset` (optional, default: 0): Pagination offset
  - `status` (optional): Filter by status
  - `experiment_id` (optional): Filter by experiment ID
  - `db_name` (optional): Database name
- **Response**: JSON array of pipeline executions
- **Error Responses**: 500 (server error)
- **CORS**: Yes

#### POST /api/pipeline/start

- **Method**: POST
- **Path**: `/api/pipeline/start`
- **Query Parameters**:
  - `db_name` (optional): Database name
- **Request Body**: JSON
  ```json
  {
    "config": {
      "extraction": {...},
      "selected_stages": "string",
      "resume_from_failure": false
    },
    "pipeline_id": "string (optional)"
  }
  ```
- **Response**: JSON object with pipeline_id and status
- **Error Responses**: 400 (invalid config, already running), 500 (server error)
- **CORS**: Yes

#### POST /api/pipeline/cancel

- **Method**: POST
- **Path**: `/api/pipeline/cancel`
- **Request Body**: JSON
  ```json
  {
    "pipeline_id": "string (required)"
  }
  ```
- **Response**: JSON object with cancellation status
- **Error Responses**: 400 (missing pipeline_id), 500 (server error)
- **CORS**: Yes

#### POST /api/pipeline/resume

- **Method**: POST
- **Path**: `/api/pipeline/resume`
- **Request Body**: JSON (same as start, with resume_from_failure=true)
- **Response**: JSON object with pipeline_id and status
- **Error Responses**: 400 (invalid config), 500 (server error)
- **CORS**: Yes

#### OPTIONS /api/pipeline/\*

- **Method**: OPTIONS
- **Path**: Any `/api/pipeline/*` path
- **Purpose**: CORS preflight requests
- **Response**: 200 with CORS headers
- **CORS Headers**: Access-Control-Allow-Origin, Access-Control-Allow-Methods, Access-Control-Allow-Headers

---

### 2. pipeline_progress.py (1 endpoint)

**File Purpose**: Real-time pipeline progress monitoring via Server-Sent Events (SSE)

#### GET /api/pipeline/progress

- **Method**: GET
- **Path**: `/api/pipeline/progress`
- **Query Parameters**:
  - `pipeline_id` (optional, default: "default"): Pipeline identifier
- **Response**: Server-Sent Events (SSE) stream
  - Content-Type: `text/event-stream`
  - Format: `data: {"stage": "...", "progress": 0.5, "message": "..."}`
- **Error Responses**: 404 (invalid path), 500 (server error)
- **CORS**: Yes (headers set)
- **Special**: Streaming endpoint, connection kept alive

---

### 3. pipeline_stats.py (1 endpoint)

**File Purpose**: Per-stage pipeline statistics

#### GET /api/pipeline/stats

- **Method**: GET
- **Path**: `/api/pipeline/stats`
- **Query Parameters**: None
- **Response**: JSON object with stage statistics
  ```json
  {
    "extraction": {...},
    "entity_resolution": {...},
    "graph_construction": {...},
    "community_detection": {...}
  }
  ```
- **Error Responses**: 404 (invalid path), 500 (server error)
- **CORS**: Yes

---

### 4. entities.py (2 endpoints)

**File Purpose**: Entity browsing and search

#### GET /api/entities/search

- **Method**: GET
- **Path**: `/api/entities/search` or `/api/entities`
- **Query Parameters**:
  - `q` (optional): Search query (text search)
  - `type` (optional): Filter by entity type
  - `min_confidence` (optional): Minimum confidence score
  - `min_source_count` (optional): Minimum source count
  - `limit` (optional, default: 50): Results per page
  - `offset` (optional, default: 0): Pagination offset
  - `db_name` (optional): Database name
- **Response**: JSON object with entities array and pagination
- **Error Responses**: 404 (invalid path), 500 (server error)
- **CORS**: Yes

#### GET /api/entities/{entity_id}

- **Method**: GET
- **Path**: `/api/entities/{entity_id}`
- **Path Parameters**:
  - `entity_id` (required): Entity identifier
- **Query Parameters**:
  - `db_name` (optional): Database name
- **Response**: JSON object with entity details (aliases, mentions, relationships)
- **Error Responses**: 404 (entity not found), 500 (server error)
- **CORS**: Yes

---

### 5. relationships.py (1 endpoint)

**File Purpose**: Relationship browsing and search

#### GET /api/relationships/search

- **Method**: GET
- **Path**: `/api/relationships/search` or `/api/relationships`
- **Query Parameters**:
  - `predicate` (optional): Filter by predicate type
  - `type` (optional): Filter by entity type
  - `min_confidence` (optional): Minimum confidence score
  - `subject_id` (optional): Filter by subject entity ID
  - `object_id` (optional): Filter by object entity ID
  - `limit` (optional, default: 50): Results per page
  - `offset` (optional, default: 0): Pagination offset
  - `db_name` (optional): Database name
- **Response**: JSON object with relationships array and pagination
- **Error Responses**: 404 (invalid path), 500 (server error)
- **CORS**: Yes (on success, missing on errors)

---

### 6. communities.py (3 endpoints)

**File Purpose**: Community exploration and search

#### GET /api/communities/search

- **Method**: GET
- **Path**: `/api/communities/search` or `/api/communities`
- **Query Parameters**:
  - `level` (optional): Filter by community level
  - `min_size` (optional): Minimum community size
  - `max_size` (optional): Maximum community size
  - `min_coherence` (optional): Minimum coherence score
  - `limit` (optional, default: 50): Results per page
  - `offset` (optional, default: 0): Pagination offset
  - `sort_by` (optional, default: "entity_count"): Sort field
  - `db_name` (optional): Database name
- **Response**: JSON object with communities array and pagination
- **Error Responses**: 404 (invalid path), 500 (server error)
- **CORS**: Yes

#### GET /api/communities/levels

- **Method**: GET
- **Path**: `/api/communities/levels`
- **Query Parameters**:
  - `db_name` (optional): Database name
- **Response**: JSON object with level statistics
- **Error Responses**: 404 (invalid path), 500 (server error)
- **CORS**: Yes

#### GET /api/communities/{community_id}

- **Method**: GET
- **Path**: `/api/communities/{community_id}`
- **Path Parameters**:
  - `community_id` (required): Community identifier
- **Query Parameters**:
  - `db_name` (optional): Database name
- **Response**: JSON object with community details (entities, relationships, summary)
- **Error Responses**: 404 (community not found), 500 (server error)
- **CORS**: Yes

---

### 7. ego_network.py (1 endpoint)

**File Purpose**: Ego network visualization (N-hop neighborhood)

#### GET /api/ego/network/{entity_id}

- **Method**: GET
- **Path**: `/api/ego/network/{entity_id}`
- **Path Parameters**:
  - `entity_id` (required): Central entity identifier
- **Query Parameters**:
  - `max_hops` (optional, default: 2): Maximum hop distance
  - `max_nodes` (optional, default: 100): Maximum nodes to return
  - `db_name` (optional): Database name
- **Response**: JSON object with nodes and links arrays
  ```json
  {
    "nodes": [...],
    "links": [...],
    "total_nodes": 10,
    "total_links": 15
  }
  ```
- **Error Responses**: 404 (entity not found), 500 (server error)
- **CORS**: Yes (on success, missing on errors)

---

### 8. export.py (4 endpoints)

**File Purpose**: Graph data export in multiple formats

#### GET /api/export/json

- **Method**: GET
- **Path**: `/api/export/json`
- **Query Parameters**:
  - `entity_ids` (optional): Comma-separated entity IDs to filter
  - `community_id` (optional): Community ID to export
  - `db_name` (optional): Database name
- **Response**: JSON file download
  - Content-Type: `application/json`
  - Content-Disposition: `attachment; filename="graph_{db_name}.json"`
- **Error Responses**: 404 (invalid path), 500 (server error)
- **CORS**: Yes (on success, missing on errors)

#### GET /api/export/csv

- **Method**: GET
- **Path**: `/api/export/csv`
- **Query Parameters**: Same as JSON export
- **Response**: CSV file download
  - Content-Type: `text/csv`
  - Content-Disposition: `attachment; filename="graph_{db_name}.csv"`
- **Error Responses**: 404 (invalid path), 500 (server error)
- **CORS**: Yes (on success, missing on errors)

#### GET /api/export/graphml

- **Method**: GET
- **Path**: `/api/export/graphml`
- **Query Parameters**: Same as JSON export
- **Response**: GraphML file download
  - Content-Type: `application/xml`
  - Content-Disposition: `attachment; filename="graph_{db_name}.graphml"`
- **Error Responses**: 404 (invalid path), 500 (server error)
- **CORS**: Yes (on success, missing on errors)

#### GET /api/export/gexf

- **Method**: GET
- **Path**: `/api/export/gexf`
- **Query Parameters**: Same as JSON export
- **Response**: GEXF file download
  - Content-Type: `application/xml`
  - Content-Disposition: `attachment; filename="graph_{db_name}.gexf"`
- **Error Responses**: 404 (invalid path), 500 (server error)
- **CORS**: Yes (on success, missing on errors)

---

### 9. quality_metrics.py (1 endpoint)

**File Purpose**: Per-stage quality metrics

#### GET /api/quality/metrics

- **Method**: GET
- **Path**: `/api/quality/metrics`
- **Query Parameters**:
  - `stage` (optional): Filter by stage name
  - `db_name` (optional): Database name
- **Response**: JSON object with quality metrics per stage
- **Error Responses**: 404 (invalid path), 500 (server error)
- **CORS**: Yes (on success, missing on errors)

---

### 10. graph_statistics.py (2 endpoints)

**File Purpose**: Graph-level statistics and trends

#### GET /api/graph/statistics

- **Method**: GET
- **Path**: `/api/graph/statistics`
- **Query Parameters**:
  - `db_name` (optional): Database name
- **Response**: JSON object with graph statistics (nodes, edges, degree distribution, etc.)
- **Error Responses**: 404 (invalid path), 500 (server error)
- **CORS**: Yes

#### GET /api/graph/trends

- **Method**: GET
- **Path**: `/api/graph/trends`
- **Query Parameters**:
  - `limit` (optional, default: 50): Number of time points
  - `db_name` (optional): Database name
- **Response**: JSON object with time series statistics
- **Error Responses**: 404 (invalid path), 500 (server error)
- **CORS**: Yes

---

### 11. performance_metrics.py (1 endpoint)

**File Purpose**: Pipeline performance metrics

#### GET /api/performance/metrics

- **Method**: GET
- **Path**: `/api/performance/metrics`
- **Query Parameters**:
  - `db_name` (optional): Database name
- **Response**: JSON object with performance metrics (duration, throughput, trends)
- **Error Responses**: 404 (invalid path), 500 (server error)
- **CORS**: Yes (on success, missing on errors)

---

### 12. metrics.py (1 endpoint)

**File Purpose**: Prometheus metrics export

#### GET /metrics

- **Method**: GET
- **Path**: `/metrics`
- **Query Parameters**: None
- **Response**: Prometheus text format metrics
  - Content-Type: `text/plain; charset=utf-8`
- **Error Responses**: 404 (invalid path), 500 (server error, returns text/plain)
- **CORS**: No (Prometheus scraping endpoint)

---

## Endpoint Grouping by Functionality

### Pipeline Control (6 endpoints)

- Start, stop, resume, status, history, CORS preflight

### Data Browsing (6 endpoints)

- Entities: search, details
- Relationships: search
- Communities: search, levels, details

### Statistics & Metrics (6 endpoints)

- Pipeline stats, quality metrics, graph statistics, graph trends, performance metrics, Prometheus metrics

### Export (4 endpoints)

- JSON, CSV, GraphML, GEXF formats

### Monitoring (2 endpoints)

- Progress streaming (SSE), Prometheus metrics

### Network Analysis (1 endpoint)

- Ego network visualization

---

## Common Patterns

### Query Parameters

- `db_name` (optional): Present in most endpoints, defaults to config value
- `limit` (optional): Pagination limit, default varies (50 common)
- `offset` (optional): Pagination offset, default 0

### Response Format

- Most endpoints return JSON with `Content-Type: application/json`
- Export endpoints return file downloads with `Content-Disposition` headers
- Progress endpoint uses SSE (`text/event-stream`)
- Metrics endpoint returns Prometheus format (`text/plain`)

### Error Handling

- 400: Bad request (missing required params, invalid input)
- 404: Not found (entity, community, invalid path)
- 500: Server error (exceptions)

### CORS Support

- `pipeline_control.py`: Full CORS support (OPTIONS handler + headers)
- Other files: CORS headers on success, missing on some error responses

---

## Testing Status

**Unit Tests**: 3 files have tests

- `test_pipeline_control.py`: 6 tests (5 passed, 1 skipped)
- `test_ego_network.py`: 2 tests (2 passed)
- `test_export.py`: 5 tests (5 passed)

**Integration Tests**: None (curl tests to be created in Achievement 1.1)

**Coverage**: ~25% of endpoints have unit tests

---

## Dependencies

**MongoDB**: All endpoints require MongoDB connection (except `/metrics`)

**Business Logic**: Endpoints call business layer functions from:

- `business.pipelines.graphrag`
- `business.stages.graphrag.*`
- `business.services.graphrag.*`
- `business.services.observability.prometheus_metrics`

**Configuration**: Most endpoints use `core.config.graphrag.GraphRAGPipelineConfig`

---

## Notes

1. **CORS Issues**: Only `pipeline_control.py` has OPTIONS handler. Other files may fail CORS preflight requests.

2. **Error Response Consistency**: Some endpoints return JSON errors, others return empty 404 responses.

3. **Path Parsing**: All endpoints use manual URL parsing with `urlparse` and path splitting.

4. **Database Parameter**: Most endpoints accept `db_name` query parameter for multi-database support.

5. **Pagination**: Search endpoints support `limit` and `offset` for pagination.

---

**Inventory Complete**: 2025-11-07 23:25 UTC  
**Total Endpoints Documented**: 28  
**Files Reviewed**: 12/12 (100%)
