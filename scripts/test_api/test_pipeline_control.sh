#!/bin/bash
# Test script for Pipeline Control API
# Tests all endpoints in pipeline_control.py
# Usage: ./test_pipeline_control.sh [BASE_URL]

BASE_URL="${1:-http://localhost:8000}"
PASSED=0
FAILED=0

echo "Testing Pipeline Control API endpoints at $BASE_URL"
echo "=================================================="

test_endpoint() {
    local name="$1"
    local method="$2"
    local path="$3"
    local data="$4"
    local expected_status="${5:-200}"
    
    echo -n "Testing $name ($method $path)... "
    
    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$BASE_URL$path")
    elif [ "$method" = "OPTIONS" ]; then
        response=$(curl -s -w "\n%{http_code}" -X OPTIONS \
            -H "Origin: http://localhost:3000" \
            "$BASE_URL$path")
    else
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$path")
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" = "$expected_status" ]; then
        echo "✓ (HTTP $status_code)"
        ((PASSED++))
        return 0
    else
        echo "✗ (Expected HTTP $expected_status, got HTTP $status_code)"
        echo "  Response: $body"
        ((FAILED++))
        return 1
    fi
}

# Test 1: GET /api/pipeline/status (missing pipeline_id - should fail)
test_endpoint "Get Pipeline Status (missing param)" "GET" \
    "/api/pipeline/status" "" "400"

# Test 2: GET /api/pipeline/status (with pipeline_id)
test_endpoint "Get Pipeline Status" "GET" \
    "/api/pipeline/status?pipeline_id=test_123" "" "404"  # 404 expected if pipeline doesn't exist

# Test 3: GET /api/pipeline/history
test_endpoint "Get Pipeline History" "GET" \
    "/api/pipeline/history?limit=10&offset=0" "" "200"

# Test 4: POST /api/pipeline/start (invalid config - should fail)
test_endpoint "Start Pipeline (invalid config)" "POST" \
    "/api/pipeline/start" '{"config": {}}' "400"

# Test 5: POST /api/pipeline/start (valid config)
test_endpoint "Start Pipeline" "POST" \
    "/api/pipeline/start" '{"config": {"extraction": {"read_db_name": "test", "write_db_name": "test", "model_name": "gpt-4o-mini"}, "selected_stages": "extraction"}}' "200"

# Test 6: POST /api/pipeline/cancel (missing pipeline_id - should fail)
test_endpoint "Cancel Pipeline (missing param)" "POST" \
    "/api/pipeline/cancel" '{}' "400"

# Test 7: POST /api/pipeline/cancel (with pipeline_id)
test_endpoint "Cancel Pipeline" "POST" \
    "/api/pipeline/cancel" '{"pipeline_id": "test_123"}' "200"

# Test 8: POST /api/pipeline/resume
test_endpoint "Resume Pipeline" "POST" \
    "/api/pipeline/resume" '{"config": {"extraction": {"read_db_name": "test", "write_db_name": "test", "model_name": "gpt-4o-mini"}, "selected_stages": "extraction", "resume_from_failure": true}}' "200"

# Test 9: OPTIONS /api/pipeline/start (CORS preflight)
test_endpoint "CORS Preflight" "OPTIONS" \
    "/api/pipeline/start" "" "200"

echo "=================================================="
echo "Tests complete: $PASSED passed, $FAILED failed"
exit $FAILED

