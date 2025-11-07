# GraphRAG Pipeline Visualization API Documentation

**Achievement 8.2: API Documentation**

Complete REST API documentation for the GraphRAG Pipeline Visualization system.

## Base URL

All API endpoints are served from:
```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. All endpoints are publicly accessible.

---

## Pipeline Control API

### Start Pipeline

Start a new GraphRAG pipeline execution.

**Endpoint:** `POST /api/pipeline/start`

**Query Parameters:**
- `db_name` (optional): Database name (default: from config)

**Request Body:**
```json
{
  "config": {
    "extraction": {
      "read_db_name": "mongo_hack",
      "write_db_name": "mongo_hack",
      "model_name": "gpt-4o-mini"
    },
    "selected_stages": "extraction,resolution,construction,detection",
    "resume_from_failure": false
  },
  "pipeline_id": "optional_pipeline_id"
}
```

**Response:**
```json
{
  "pipeline_id": "pipeline_1234567890_abc123",
  "status": "starting",
  "message": "Pipeline started"
}
```

**Error Response:**
```json
{
  "error": "Pipeline already running",
  "pipeline_id": "pipeline_123",
  "status": "running"
}
```

### Get Pipeline Status

Get the current status of a pipeline.

**Endpoint:** `GET /api/pipeline/status`

**Query Parameters:**
- `pipeline_id` (required): Pipeline ID
- `db_name` (optional): Database name

**Response:**
```json
{
  "pipeline_id": "pipeline_123",
  "status": "running",
  "started_at": "2025-11-07T10:00:00",
  "completed_at": null,
  "configuration": {}
}
```

**Status Values:**
- `starting`: Pipeline is initializing
- `running`: Pipeline is executing
- `completed`: Pipeline finished successfully
- `failed`: Pipeline encountered an error
- `cancelled`: Pipeline was cancelled

### Cancel Pipeline

Cancel a running pipeline.

**Endpoint:** `POST /api/pipeline/cancel`

**Request Body:**
```json
{
  "pipeline_id": "pipeline_123"
}
```

**Response:**
```json
{
  "pipeline_id": "pipeline_123",
  "status": "cancelled",
  "message": "Pipeline cancellation requested"
}
```

### Resume Pipeline

Resume a pipeline from the last checkpoint.

**Endpoint:** `POST /api/pipeline/resume`

**Query Parameters:**
- `db_name` (optional): Database name

**Request Body:**
```json
{
  "config": {
    "extraction": {
      "read_db_name": "mongo_hack",
      "write_db_name": "mongo_hack"
    },
    "resume_from_failure": true
  },
  "pipeline_id": "pipeline_123"
}
```

### Get Pipeline History

Get execution history of past pipeline runs.

**Endpoint:** `GET /api/pipeline/history`

**Query Parameters:**
- `db_name` (optional): Database name
- `limit` (optional): Maximum results (default: 50)
- `offset` (optional): Pagination offset (default: 0)
- `status` (optional): Filter by status (completed, failed, running, cancelled)
- `experiment_id` (optional): Filter by experiment ID

**Response:**
```json
{
  "pipelines": [
    {
      "pipeline_id": "pipeline_123",
      "status": "completed",
      "started_at": "2025-11-07T10:00:00",
      "completed_at": "2025-11-07T10:30:00",
      "exit_code": 0
    }
  ],
  "total": 10,
  "limit": 50,
  "offset": 0,
  "has_more": false
}
```

---

## Entity API

### Search Entities

Search and filter entities in the knowledge graph.

**Endpoint:** `GET /api/entities/search`

**Query Parameters:**
- `db_name` (optional): Database name
- `query` (optional): Search query (searches name, canonical_name, aliases)
- `entity_type` (optional): Filter by entity type (PERSON, ORGANIZATION, etc.)
- `min_confidence` (optional): Minimum confidence threshold
- `min_source_count` (optional): Minimum source_count threshold
- `limit` (optional): Maximum results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "entities": [
    {
      "entity_id": "entity_123",
      "name": "John Doe",
      "canonical_name": "John Doe",
      "type": "PERSON",
      "description": "Software engineer",
      "confidence": 0.95,
      "source_count": 10
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

### Get Entity Details

Get detailed information about a specific entity.

**Endpoint:** `GET /api/entities/{entity_id}`

**Query Parameters:**
- `db_name` (optional): Database name

**Response:**
```json
{
  "entity_id": "entity_123",
  "name": "John Doe",
  "canonical_name": "John Doe",
  "type": "PERSON",
  "description": "Software engineer",
  "confidence": 0.95,
  "source_count": 10,
  "aliases": ["JD", "John"],
  "relationships": [
    {
      "relationship_id": "rel_123",
      "subject_id": "entity_123",
      "object_id": "entity_456",
      "predicate": "works_for",
      "direction": "outgoing"
    }
  ]
}
```

---

## Relationship API

### Search Relationships

Search and filter relationships in the knowledge graph.

**Endpoint:** `GET /api/relationships/search`

**Query Parameters:**
- `db_name` (optional): Database name
- `predicate` (optional): Filter by predicate
- `entity_type` (optional): Filter by entity type (subject or object)
- `min_confidence` (optional): Minimum confidence threshold
- `limit` (optional): Maximum results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "relationships": [
    {
      "relationship_id": "rel_123",
      "subject_id": "entity_123",
      "object_id": "entity_456",
      "predicate": "works_for",
      "description": "Employment relationship",
      "confidence": 0.9,
      "source_count": 5
    }
  ],
  "total": 50,
  "limit": 50,
  "offset": 0
}
```

---

## Community API

### Search Communities

Search and filter communities in the knowledge graph.

**Endpoint:** `GET /api/communities/search`

**Query Parameters:**
- `db_name` (optional): Database name
- `level` (optional): Filter by community level
- `min_size` (optional): Minimum community size (entity_count)
- `max_size` (optional): Maximum community size
- `min_coherence` (optional): Minimum coherence score
- `sort_by` (optional): Sort field (entity_count, coherence_score, level)
- `limit` (optional): Maximum results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "communities": [
    {
      "community_id": "community_123",
      "title": "Software Engineering Community",
      "level": 1,
      "entity_count": 50,
      "relationship_count": 100,
      "coherence_score": 0.85
    }
  ],
  "total": 20,
  "limit": 50,
  "offset": 0
}
```

### Get Community Details

Get detailed information about a specific community.

**Endpoint:** `GET /api/communities/{community_id}`

**Query Parameters:**
- `db_name` (optional): Database name

**Response:**
```json
{
  "community_id": "community_123",
  "title": "Software Engineering Community",
  "summary": "A community focused on software engineering practices...",
  "level": 1,
  "entity_count": 50,
  "relationship_count": 100,
  "coherence_score": 0.85,
  "entities": [...],
  "relationships": [...]
}
```

### Get Community Levels

Get statistics about community levels.

**Endpoint:** `GET /api/communities/levels`

**Query Parameters:**
- `db_name` (optional): Database name

**Response:**
```json
{
  "levels": [
    {
      "level": 1,
      "count": 10,
      "avg_size": 50.5,
      "avg_coherence": 0.85
    }
  ]
}
```

---

## Ego Network API

### Get Ego Network

Get N-hop ego network around an entity.

**Endpoint:** `GET /api/ego/network/{entity_id}`

**Query Parameters:**
- `db_name` (optional): Database name
- `max_hops` (optional): Maximum number of hops (default: 2)
- `max_nodes` (optional): Maximum number of nodes (default: 100)

**Response:**
```json
{
  "center_entity": {
    "entity_id": "entity_123",
    "name": "John Doe",
    "type": "PERSON"
  },
  "nodes": [
    {
      "entity_id": "entity_123",
      "name": "John Doe",
      "type": "PERSON",
      "hop_level": 0,
      "is_center": true
    }
  ],
  "links": [
    {
      "source": "entity_123",
      "target": "entity_456",
      "predicate": "works_for",
      "confidence": 0.9,
      "hop": 1
    }
  ],
  "max_hops": 2,
  "total_nodes": 10,
  "total_links": 15
}
```

---

## Export API

### Export Graph as JSON

Export graph data as JSON.

**Endpoint:** `GET /api/export/json`

**Query Parameters:**
- `db_name` (optional): Database name
- `entity_ids` (optional): Comma-separated list of entity IDs (subgraph)
- `community_id` (optional): Community ID to export

**Response:** JSON file download

### Export Graph as CSV

Export graph data as CSV.

**Endpoint:** `GET /api/export/csv`

**Query Parameters:**
- `db_name` (optional): Database name
- `entity_ids` (optional): Comma-separated list of entity IDs
- `community_id` (optional): Community ID to export

**Response:** CSV file download

### Export Graph as GraphML

Export graph data as GraphML format (for Gephi, yEd, etc.).

**Endpoint:** `GET /api/export/graphml`

**Query Parameters:**
- `db_name` (optional): Database name
- `entity_ids` (optional): Comma-separated list of entity IDs
- `community_id` (optional): Community ID to export

**Response:** GraphML XML file download

### Export Graph as GEXF

Export graph data as GEXF format (for Gephi).

**Endpoint:** `GET /api/export/gexf`

**Query Parameters:**
- `db_name` (optional): Database name
- `entity_ids` (optional): Comma-separated list of entity IDs
- `community_id` (optional): Community ID to export

**Response:** GEXF XML file download

---

## Quality Metrics API

### Get Quality Metrics

Get per-stage quality metrics.

**Endpoint:** `GET /api/quality/metrics`

**Query Parameters:**
- `db_name` (optional): Database name
- `stage` (optional): Stage name (extraction, resolution, construction, detection)

**Response:**
```json
{
  "extraction": {
    "completion_rate": 0.95,
    "failure_rate": 0.05,
    "total_chunks": 1000,
    "canonical_ratio": 0.95
  },
  "detection": {
    "modularity": 0.75,
    "coverage": 0.90,
    "total_communities": 50
  }
}
```

### Get Quality Trends

Get quality metrics trends over time.

**Endpoint:** `GET /api/quality/trends`

**Query Parameters:**
- `db_name` (optional): Database name
- `stage` (optional): Stage name (default: detection)
- `limit` (optional): Maximum data points (default: 50)

---

## Graph Statistics API

### Get Graph Statistics

Get comprehensive graph-level statistics.

**Endpoint:** `GET /api/graph/statistics`

**Query Parameters:**
- `db_name` (optional): Database name

**Response:**
```json
{
  "total_entities": 1000,
  "total_relationships": 5000,
  "graph_density": 0.01,
  "avg_degree": 5.0,
  "max_degree": 50,
  "type_distribution": [...],
  "predicate_distribution": [...],
  "degree_distribution": [...]
}
```

---

## Performance Metrics API

### Get Performance Metrics

Get pipeline performance metrics.

**Endpoint:** `GET /api/performance/metrics`

**Query Parameters:**
- `db_name` (optional): Database name
- `pipeline_id` (optional): Pipeline ID to filter by

**Response:**
```json
{
  "pipeline_id": "pipeline_123",
  "status": "completed",
  "duration_seconds": 1800,
  "total_chunks": 1000,
  "throughput": {
    "chunks_per_sec": 0.56,
    "chunks_per_min": 33.33
  }
}
```

### Get Performance Trends

Get performance trends over time.

**Endpoint:** `GET /api/performance/trends`

**Query Parameters:**
- `db_name` (optional): Database name
- `limit` (optional): Maximum data points (default: 50)

---

## Pipeline Stats API

### Get Stage Statistics

Get per-stage statistics for the pipeline.

**Endpoint:** `GET /api/pipeline/stats`

**Query Parameters:**
- `db_name` (optional): Database name

**Response:**
```json
{
  "stages": {
    "graph_extraction": {
      "input_count": 1000,
      "output_count": 950,
      "status": "completed"
    }
  }
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error message description"
}
```

**HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request (missing or invalid parameters)
- `404`: Not Found (resource doesn't exist)
- `500`: Internal Server Error

---

## Rate Limiting

Currently, no rate limiting is enforced. In production, consider implementing rate limiting to prevent abuse.

---

## Examples

### Example: Start a Pipeline

```bash
curl -X POST "http://localhost:8000/api/pipeline/start?db_name=mongo_hack" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "extraction": {
        "read_db_name": "mongo_hack",
        "write_db_name": "mongo_hack"
      },
      "selected_stages": "extraction,resolution"
    }
  }'
```

### Example: Get Entity Ego Network

```bash
curl "http://localhost:8000/api/ego/network/entity_123?db_name=mongo_hack&max_hops=2&max_nodes=50"
```

### Example: Export Community as GraphML

```bash
curl "http://localhost:8000/api/export/graphml?db_name=mongo_hack&community_id=community_123" \
  -o community_123.graphml
```

---

## Client Libraries

### Python Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Start pipeline
response = requests.post(
    f"{BASE_URL}/api/pipeline/start",
    params={"db_name": "mongo_hack"},
    json={
        "config": {
            "extraction": {"read_db_name": "mongo_hack", "write_db_name": "mongo_hack"}
        }
    }
)
pipeline_id = response.json()["pipeline_id"]

# Check status
status = requests.get(
    f"{BASE_URL}/api/pipeline/status",
    params={"pipeline_id": pipeline_id, "db_name": "mongo_hack"}
).json()
```

---

## Version

**API Version:** 1.0  
**Last Updated:** 2025-11-07

