# Graph API Tests

Bash scripts for testing the Graph Data API endpoints.

## Overview

These scripts test the Graph API (port 8081) endpoints using curl commands.
Each script tests a specific endpoint or category of functionality.

## Prerequisites

1. Graph API server running on `http://localhost:8081`
2. `curl` and `jq` installed
3. Test data in MongoDB

## Running Tests

### Run All Tests

```bash
# From GraphRAG root
for f in tests/api/graph_api/*.sh; do bash "$f"; done
```

### Run Individual Tests

```bash
# Test entities endpoint
bash tests/api/graph_api/test_entities.sh

# Test communities endpoint
bash tests/api/graph_api/test_communities.sh
```

## Test Files

| File | Endpoint | Description |
|------|----------|-------------|
| `test_entities.sh` | `/api/entities/*` | Entity search and details |
| `test_communities.sh` | `/api/communities/*` | Community operations |
| `test_relationships.sh` | `/api/relationships/*` | Relationship queries |
| `test_ego_network.sh` | `/api/ego/network/*` | Ego network retrieval |
| `test_export.sh` | `/api/export/*` | Graph export formats |
| `test_graph_statistics.sh` | `/api/statistics/*` | Graph statistics |
| `test_quality_metrics.sh` | `/api/metrics/quality/*` | Quality metrics |
| `test_performance_metrics.sh` | `/api/metrics/performance/*` | Performance metrics |
| `test_metrics.sh` | `/api/metrics/*` | General metrics |
| `test_pipeline_control.sh` | `/api/pipelines/*/control` | Pipeline control |
| `test_pipeline_progress.sh` | `/api/pipelines/*/progress` | Pipeline progress |
| `test_pipeline_stats.sh` | `/api/pipelines/stats` | Pipeline statistics |
| `test_cors.sh` | All endpoints | CORS header validation |
| `test_edge_cases.sh` | Various | Edge cases and error handling |
| `test_error_handling.sh` | Various | Error response validation |

## Test Output

Each test script outputs:
- Test name and description
- HTTP response code
- Response body (formatted with `jq` if available)
- Pass/fail status

Example output:
```
=== Testing Entity Search ===
POST /api/entities/search
Request: {"query": "machine learning", "limit": 10}
Response: 200 OK
{
  "entities": [...],
  "total": 42
}
✓ PASS
```

## Environment Variables

Override default settings:

```bash
# Custom API host
export GRAPH_API_HOST="http://localhost:8081"

# Custom database
export MONGODB_DB="test_db"

# Run tests
bash tests/api/graph_api/test_entities.sh
```

## Adding New Tests

1. Create a new `.sh` file in this directory
2. Follow the existing pattern:
   ```bash
   #!/bin/bash
   HOST="${GRAPH_API_HOST:-http://localhost:8081}"
   
   echo "=== Test Name ==="
   response=$(curl -s -X GET "$HOST/api/endpoint")
   # Assertions...
   ```
3. Make executable: `chmod +x test_new.sh`

## Troubleshooting

- **Connection refused**: Ensure Graph API server is running
- **Empty responses**: Check MongoDB has test data
- **404 errors**: Verify API routes in `app/graph_api/router.py`

