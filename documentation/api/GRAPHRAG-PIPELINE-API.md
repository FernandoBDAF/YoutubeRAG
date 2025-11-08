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
- `501`: Method Not Allowed (e.g., OPTIONS not supported)

### Error Response Examples

**400 Bad Request (Missing Required Parameter):**
```json
{
  "error": "Missing required parameter: pipeline_id"
}
```

**400 Bad Request (Invalid Parameter):**
```json
{
  "error": "Invalid parameter: limit must be a positive integer"
}
```

**404 Not Found (Resource Doesn't Exist):**
```json
{
  "error": "Pipeline not found: pipeline_123"
}
```

**404 Not Found (Invalid Endpoint):**
```json
{
  "error": "Endpoint not found: /api/invalid/path"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error occurred"
}
```

**Note**: As of the latest review, some endpoints may return HTML error pages or empty bodies for 404 errors instead of JSON. This is a known issue (see Known Issues section below).

### CORS Headers in Error Responses

All error responses should include CORS headers for cross-origin requests:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

**Note**: Some endpoints may be missing CORS headers on error responses. This is a known issue (see Known Issues section below).

---

## Test Results Summary

**Last Updated**: 2025-11-08  
**Test Coverage**: 28 endpoints across 12 API files

### Test Execution Status

| Test Type | Status | Coverage | Notes |
|-----------|--------|----------|-------|
| Existing Unit Tests | ✅ Passing | 13 tests | 12 passed, 1 skipped |
| Curl Integration Tests | ⚠️ Not Executed | 45+ test cases | Server required |
| CORS & OPTIONS Tests | ⚠️ Not Executed | 11 test cases | Server required |
| Error Handling Tests | ⚠️ Not Executed | 14 test cases | Server required |
| Input Validation Review | ✅ Complete | 28 endpoints | 45+ gaps identified |

### Overall Assessment

**Status**: ⚠️ **APIs need improvements before production deployment**

**Key Findings**:
- ✅ All files have Python path handling (fixed)
- ✅ Existing tests passing (12/13 passed, 1 skipped)
- ❌ Only 1/12 files has OPTIONS handler (CORS preflight support)
- ❌ 11/12 files have incomplete 404 error handling (missing JSON/CORS)
- ❌ 45+ input validation gaps identified
- ⚠️ Security concerns: MongoDB query injection, XSS, type confusion

**Total Issues Identified**: 80+ (2 Critical, 37 High, 30+ Medium, 10+ Low)

**Recommendation**: Address Critical and High priority issues before production deployment.

**Reference**: See `documentation/api/API-TEST-RESULTS-COMPREHENSIVE.md` for detailed test results.

---

## Known Issues

**Last Updated**: 2025-11-08

### Critical Issues (2)

#### 1. Missing OPTIONS Handlers

**Impact**: CORS preflight requests fail with HTTP 501  
**Affected**: 11/12 API files (all POST endpoints except `pipeline_control.py`)  
**Status**: ⚠️ **Partially Fixed** (Achievement 3.2 added OPTIONS handlers to 11 files)

**Description**: 
- Browser CORS preflight requests send OPTIONS requests before POST requests
- Most API handlers don't have `do_OPTIONS` method, causing HTTP 501 errors
- Only `pipeline_control.py` had OPTIONS handler initially

**Workaround**: 
- Use server-side requests (no CORS preflight)
- Or use a proxy server to handle OPTIONS requests

**Fix Status**: OPTIONS handlers were added in Achievement 3.2, but verification requires server testing.

#### 2. Incomplete 404 Error Handling

**Impact**: 404 responses return empty body or HTML instead of JSON  
**Affected**: 11/12 API files (all except `pipeline_control.py`)  
**Status**: ⚠️ **Partially Fixed** (Achievement 3.2 improved error handling)

**Description**:
- Some endpoints return empty bodies or HTML error pages for 404 errors
- Error responses should be JSON with CORS headers
- Only `pipeline_control.py` had complete error handling initially

**Example of Issue**:
```bash
# May return empty body or HTML instead of:
{
  "error": "Resource not found"
}
```

**Fix Status**: Error handling was improved in Achievement 3.2, but verification requires server testing.

### High Priority Issues (37)

#### Missing CORS Headers on Error Responses

**Impact**: Cross-origin requests fail when errors occur  
**Affected**: 11/12 API files  
**Status**: ⚠️ **Partially Fixed** (Achievement 3.2 added CORS headers)

**Description**: Error responses (404, 500) may be missing CORS headers, causing browser CORS errors.

#### Type Conversion Errors Not Caught

**Impact**: Invalid parameters cause 500 errors instead of 400  
**Affected**: 12+ endpoints  
**Status**: ⚠️ **Not Fixed**

**Description**: 
- Type conversion errors (e.g., `int("abc")`) raise exceptions
- These propagate as 500 errors instead of being caught and returned as 400 errors
- Should validate types before conversion

**Example**:
```bash
# Request: GET /api/pipeline/status?pipeline_id=test&limit=abc
# Current: Returns 500 Internal Server Error
# Expected: Returns 400 Bad Request with error message
```

#### No Range Validation for Numeric Parameters

**Impact**: Invalid values accepted (negative numbers, very large values)  
**Affected**: 15+ endpoints  
**Status**: ⚠️ **Not Fixed**

**Description**: 
- Parameters like `limit`, `offset`, `max_hops`, `max_nodes` accept any integer
- No validation for negative values or unreasonably large values
- Should validate ranges (e.g., `limit` between 1-1000)

#### No Format Validation for IDs and Enums

**Impact**: Invalid IDs/enums accepted, causing downstream errors  
**Affected**: 10+ endpoints  
**Status**: ⚠️ **Not Fixed**

**Description**:
- Entity IDs, pipeline IDs, community IDs not validated for format
- Enum values (status, entity_type) not validated
- Should validate format before querying database

### Medium Priority Issues (11)

- Weak error messages (not descriptive enough)
- No length validation for string parameters
- No structure validation for request bodies
- Edge case handling incomplete (empty strings, null values)

### Security Concerns

#### MongoDB Query Injection

**Risk**: Medium  
**Status**: ⚠️ **Not Fixed**

**Description**: 
- User input directly used in MongoDB queries without sanitization
- Potential for NoSQL injection attacks
- Should use parameterized queries or input sanitization

#### XSS (Cross-Site Scripting)

**Risk**: Low (API-only, no HTML rendering)  
**Status**: ⚠️ **Not Fixed**

**Description**: 
- String parameters not escaped in responses
- Low risk since API returns JSON (not HTML)
- Should escape user input if used in future HTML responses

#### Type Confusion

**Risk**: Medium  
**Status**: ⚠️ **Not Fixed**

**Description**:
- Type conversion errors not caught
- Could lead to unexpected behavior or errors
- Should validate types before conversion

---

## Input Validation

**Last Updated**: 2025-11-08

### Validation Status

**Endpoints Reviewed**: 28/28 (100%)  
**Validation Gaps Identified**: 45+  
**High Priority Gaps**: 15  
**Medium Priority Gaps**: 20  
**Low Priority Gaps**: 10+

### Current Validation

✅ **What's Working**:
- Basic type conversion present (`int()`, `float()`)
- Some required parameter checks (`pipeline_id`, `entity_id`)
- Basic error handling for missing parameters

❌ **What's Missing**:
- Range validation (negative numbers, very large values)
- Format validation (IDs, strings, enums)
- Length validation (string parameters)
- Type conversion error handling (ValueError exceptions)

### Validation Rules by Endpoint Type

#### Pipeline Control Endpoints

**Required Parameters**:
- `pipeline_id`: Required for status, cancel, resume
- `config`: Required for start, resume (must be valid JSON object)

**Optional Parameters**:
- `db_name`: String, no format validation
- `limit`: Integer, no range validation (should be 1-1000)
- `offset`: Integer, no range validation (should be >= 0)
- `status`: String enum, no validation (should be: completed, failed, running, cancelled)
- `experiment_id`: String, no format validation

#### Entity/Relationship/Community Endpoints

**Required Parameters**:
- `entity_id`: Required for detail endpoints (no format validation)
- `community_id`: Required for detail endpoints (no format validation)

**Optional Parameters**:
- `db_name`: String, no format validation
- `query`: String, no length validation
- `entity_type`: String enum, no validation (should match ontology types)
- `min_confidence`: Float, no range validation (should be 0.0-1.0)
- `min_source_count`: Integer, no range validation (should be >= 0)
- `limit`: Integer, no range validation (should be 1-1000)
- `offset`: Integer, no range validation (should be >= 0)
- `max_hops`: Integer, no range validation (should be 1-10)
- `max_nodes`: Integer, no range validation (should be 1-10000)

#### Export Endpoints

**Optional Parameters**:
- `db_name`: String, no format validation
- `entity_ids`: Comma-separated string, no format validation
- `community_id`: String, no format validation

### Validation Error Responses

When validation fails, endpoints should return:

```json
{
  "error": "Validation error: [specific message]",
  "field": "parameter_name",
  "value": "invalid_value",
  "expected": "description of expected format/range"
}
```

**Example**:
```json
{
  "error": "Validation error: limit must be between 1 and 1000",
  "field": "limit",
  "value": "-5",
  "expected": "Integer between 1 and 1000"
}
```

**Note**: Currently, most validation errors result in 500 errors instead of 400 errors with descriptive messages.

**Reference**: See `documentation/api/INPUT-VALIDATION-REVIEW.md` for detailed validation gaps.

---

## Security Considerations

**Last Updated**: 2025-11-08

### Current Security Posture

**Authentication**: ❌ None (all endpoints publicly accessible)  
**Authorization**: ❌ None (no access control)  
**Rate Limiting**: ❌ None (no protection against abuse)  
**Input Validation**: ⚠️ Basic (45+ gaps identified)  
**Error Information Disclosure**: ⚠️ Medium (detailed error messages may leak information)

### Security Recommendations

#### Before Production Deployment

1. **Implement Authentication**:
   - Add API key or OAuth2 authentication
   - Protect sensitive endpoints (pipeline control, export)

2. **Implement Rate Limiting**:
   - Prevent abuse and DoS attacks
   - Recommended: 100 requests/minute per IP

3. **Fix Input Validation**:
   - Address 15 High priority validation gaps
   - Prevent injection attacks
   - Validate all user input

4. **Sanitize MongoDB Queries**:
   - Use parameterized queries
   - Prevent NoSQL injection

5. **Implement CORS Properly**:
   - Restrict `Access-Control-Allow-Origin` to specific domains
   - Don't use `*` in production

6. **Error Message Sanitization**:
   - Don't expose internal errors to clients
   - Return generic error messages in production

### Security Best Practices

- **Never trust user input**: Always validate and sanitize
- **Use parameterized queries**: Prevent injection attacks
- **Limit error information**: Don't expose internal details
- **Implement proper CORS**: Restrict origins in production
- **Monitor API usage**: Detect and prevent abuse
- **Keep dependencies updated**: Patch security vulnerabilities

**Reference**: See `documentation/api/INPUT-VALIDATION-REVIEW.md` for detailed security concerns.

---

## Rate Limiting

Currently, no rate limiting is enforced. In production, consider implementing rate limiting to prevent abuse.

**Recommended Limits**:
- **Read endpoints**: 100 requests/minute per IP
- **Write endpoints**: 20 requests/minute per IP
- **Export endpoints**: 10 requests/minute per IP

---

## Usage Examples

### Example: Start a Pipeline

```bash
curl -X POST "http://localhost:8000/api/pipeline/start?db_name=mongo_hack" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "extraction": {
        "read_db_name": "mongo_hack",
        "write_db_name": "mongo_hack",
        "model_name": "gpt-4o-mini"
      },
      "selected_stages": "extraction,resolution,construction,detection",
      "resume_from_failure": false
    }
  }'
```

**Response**:
```json
{
  "pipeline_id": "pipeline_1234567890_abc123",
  "status": "starting",
  "message": "Pipeline started"
}
```

### Example: Get Pipeline Status

```bash
curl "http://localhost:8000/api/pipeline/status?pipeline_id=pipeline_123&db_name=mongo_hack"
```

**Response**:
```json
{
  "pipeline_id": "pipeline_123",
  "status": "running",
  "started_at": "2025-11-07T10:00:00",
  "completed_at": null,
  "configuration": {}
}
```

### Example: Get Pipeline History

```bash
curl "http://localhost:8000/api/pipeline/history?db_name=mongo_hack&limit=10&offset=0&status=completed"
```

### Example: Cancel Pipeline

```bash
curl -X POST "http://localhost:8000/api/pipeline/cancel" \
  -H "Content-Type: application/json" \
  -d '{"pipeline_id": "pipeline_123"}'
```

### Example: Search Entities

```bash
curl "http://localhost:8000/api/entities/search?db_name=mongo_hack&query=John&entity_type=PERSON&min_confidence=0.8&limit=50"
```

### Example: Get Entity Details

```bash
curl "http://localhost:8000/api/entities/entity_123?db_name=mongo_hack"
```

### Example: Search Relationships

```bash
curl "http://localhost:8000/api/relationships/search?db_name=mongo_hack&predicate=works_for&limit=50"
```

### Example: Search Communities

```bash
curl "http://localhost:8000/api/communities/search?db_name=mongo_hack&level=1&min_size=10&sort_by=entity_count&limit=50"
```

### Example: Get Community Details

```bash
curl "http://localhost:8000/api/communities/community_123?db_name=mongo_hack"
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

### Example: Get Quality Metrics

```bash
curl "http://localhost:8000/api/quality/metrics?db_name=mongo_hack&stage=detection"
```

### Example: Get Graph Statistics

```bash
curl "http://localhost:8000/api/graph/statistics?db_name=mongo_hack"
```

### Example: CORS Preflight Request

```bash
curl -X OPTIONS "http://localhost:8000/api/pipeline/start" \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type"
```

**Expected Response Headers**:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
Access-Control-Max-Age: 3600
```

**Note**: CORS preflight support may vary by endpoint (see Known Issues section).

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

### JavaScript/TypeScript Example

```javascript
const BASE_URL = "http://localhost:8000";

// Start pipeline
const response = await fetch(`${BASE_URL}/api/pipeline/start?db_name=mongo_hack`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    config: {
      extraction: {
        read_db_name: "mongo_hack",
        write_db_name: "mongo_hack",
      },
    },
  }),
});

const data = await response.json();
const pipelineId = data.pipeline_id;

// Check status
const statusResponse = await fetch(
  `${BASE_URL}/api/pipeline/status?pipeline_id=${pipelineId}&db_name=mongo_hack`
);
const status = await statusResponse.json();
```

---

## Version

**API Version:** 1.0  
**Last Updated:** 2025-01-27  
**Documentation Updated:** 2025-01-27 (Achievement 3.3: API Documentation Updated)

