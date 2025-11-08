# SUBPLAN: Curl Test Scripts Creation

**Mother Plan**: PLAN_API-REVIEW-AND-TESTING.md  
**Achievement Addressed**: Achievement 1.1 (Curl Test Scripts Created)  
**Status**: In Progress  
**Created**: 2025-11-07 23:30 UTC  
**Estimated Effort**: 6-8 hours

---

## 🎯 Objective

Create curl test scripts for all 28 API endpoints across all 12 GraphRAG API files, covering both success and error cases. This implements Achievement 1.1 and provides the foundation for systematic integration testing in Achievement 1.2.

**Goal**: Create 12 curl test scripts (one per API file) that test all endpoints with valid inputs, invalid inputs, missing parameters, and edge cases. Each script should be executable and document expected responses.

---

## 📋 What Needs to Be Created

### Files to Create

- `scripts/test_api/test_pipeline_control.sh` - Pipeline control endpoints (6 endpoints)
- `scripts/test_api/test_pipeline_progress.sh` - Progress monitoring endpoint (1 endpoint)
- `scripts/test_api/test_pipeline_stats.sh` - Pipeline statistics endpoint (1 endpoint)
- `scripts/test_api/test_entities.sh` - Entity browsing endpoints (2 endpoints)
- `scripts/test_api/test_relationships.sh` - Relationship viewing endpoint (1 endpoint)
- `scripts/test_api/test_communities.sh` - Community exploration endpoints (3 endpoints)
- `scripts/test_api/test_ego_network.sh` - Ego network endpoint (1 endpoint)
- `scripts/test_api/test_export.sh` - Export endpoints (4 endpoints)
- `scripts/test_api/test_quality_metrics.sh` - Quality metrics endpoint (1 endpoint)
- `scripts/test_api/test_graph_statistics.sh` - Graph statistics endpoints (2 endpoints)
- `scripts/test_api/test_performance_metrics.sh` - Performance metrics endpoint (1 endpoint)
- `scripts/test_api/test_metrics.sh` - Prometheus metrics endpoint (1 endpoint)

### Directory Structure

- Create `scripts/test_api/` directory if it doesn't exist
- Each script should be executable (`chmod +x`)
- Each script should include comments explaining test cases

### Test Script Structure

Each script should:

1. **Header**: Script name, purpose, usage instructions
2. **Configuration**: Base URL, default parameters
3. **Test Functions**: Individual test functions for each endpoint
4. **Success Cases**: Valid inputs, expected 200 responses
5. **Error Cases**: Invalid inputs, missing params, expected error responses
6. **Summary**: Test results summary at the end

---

## 📝 Approach

**Strategy**: Create one script per API file, using the endpoint inventory as reference, testing both success and error cases.

**Method**:

1. **Create Directory**: Ensure `scripts/test_api/` exists
2. **Review Inventory**: Use `API-ENDPOINT-INVENTORY.md` as reference
3. **Create Scripts**: One script per API file (12 scripts)
4. **Test Cases**: Include success and error cases for each endpoint
5. **Documentation**: Add comments explaining each test
6. **Make Executable**: Ensure all scripts are executable

**Key Considerations**:

- Use `http://localhost:8000` as base URL (configurable)
- Test with valid inputs (success cases)
- Test with invalid inputs (error cases)
- Test missing required parameters
- Test edge cases (empty results, large limits, etc.)
- Include JSON response validation
- Document expected responses in comments

**Script Template**:

```bash
#!/bin/bash
# Test script for [API_NAME]
# Tests all endpoints in [api_file].py

BASE_URL="${BASE_URL:-http://localhost:8000}"
echo "Testing [API_NAME] endpoints at $BASE_URL"
echo "=========================================="

# Test function template
test_endpoint() {
    local name="$1"
    local method="$2"
    local path="$3"
    local data="$4"

    echo -n "Testing $name... "
    # curl command here
    # Check response
    echo "✓" or "✗"
}

# Test cases
test_endpoint "name" "GET" "/api/path" ""
# ... more tests

echo "=========================================="
echo "Tests complete"
```

---

## 🧪 Tests Required

### Validation Approach (Not Code Tests)

**Completeness Check**:

- [ ] All 12 scripts created
- [ ] All 28 endpoints covered
- [ ] Success cases included
- [ ] Error cases included

**Quality Check**:

- [ ] Scripts are executable
- [ ] Scripts have clear comments
- [ ] Test cases are comprehensive
- [ ] Expected responses documented

**Structure Validation**:

- [ ] Scripts follow consistent format
- [ ] Scripts include usage instructions
- [ ] Scripts output clear test results
- [ ] Scripts handle errors gracefully

---

## ✅ Expected Results

### Functional Changes

- **Test Scripts**: 12 executable curl test scripts created
- **Test Coverage**: All 28 endpoints covered with success and error cases
- **Documentation**: Each script documents test cases and expected responses

### Observable Outcomes

- **Scripts Directory**: `scripts/test_api/` contains 12 test scripts
- **Executability**: All scripts are executable (`chmod +x`)
- **Test Cases**: Each endpoint has at least 2 test cases (success + error)
- **Documentation**: Scripts include comments and usage instructions

### Success Criteria

- ✅ All 12 scripts created
- ✅ All 28 endpoints covered
- ✅ Success and error cases included
- ✅ Scripts are executable
- ✅ Scripts ready for use in Achievement 1.2

---

## 📊 Deliverables Checklist

- [ ] `scripts/test_api/` directory created
- [ ] All 12 test scripts created
- [ ] All scripts are executable
- [ ] All endpoints covered (28 total)
- [ ] Success cases included
- [ ] Error cases included
- [ ] Scripts documented with comments

---

## 🔗 Related Context

**Dependencies**:

- Achievement 0.3 (API Endpoint Inventory) - Provides endpoint reference

**Feeds Into**:

- Achievement 1.2 (All Endpoints Tested with Curl) - Execute these scripts
- Achievement 2.1 (Error Handling Validated) - Use error test cases

**Reference Documents**:

- `documentation/api/API-ENDPOINT-INVENTORY.md` - Endpoint reference
- `documentation/api/GRAPHRAG-PIPELINE-API.md` - API documentation
- `EXECUTION_ANALYSIS_API-REVIEW.md` - API review findings

---

**Status**: Ready for Execution  
**Next**: Create EXECUTION_TASK and begin script creation
