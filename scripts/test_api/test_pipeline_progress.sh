#!/bin/bash
# Test script for Pipeline Progress API
# Tests SSE endpoint in pipeline_progress.py
# Usage: ./test_pipeline_progress.sh [BASE_URL]

BASE_URL="${1:-http://localhost:8000}"
PASSED=0
FAILED=0

echo "Testing Pipeline Progress API endpoints at $BASE_URL"
echo "==================================================="

test_endpoint() {
    local name="$1"
    local path="$2"
    local expected_status="${3:-200}"
    
    echo -n "Testing $name (GET $path)... "
    
    # Test SSE endpoint (timeout after 2 seconds)
    response=$(curl -s -w "\n%{http_code}" --max-time 2 \
        -H "Accept: text/event-stream" \
        "$BASE_URL$path?pipeline_id=test_123")
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" = "$expected_status" ]; then
        echo "✓ (HTTP $status_code)"
        ((PASSED++))
        return 0
    else
        echo "✗ (Expected HTTP $expected_status, got HTTP $status_code)"
        ((FAILED++))
        return 1
    fi
}

# Test 1: GET /api/pipeline/progress (valid)
test_endpoint "Get Pipeline Progress (SSE)" \
    "/api/pipeline/progress" "200"

# Test 2: GET /api/pipeline/progress (invalid path)
test_endpoint "Get Pipeline Progress (invalid path)" \
    "/api/pipeline/progress/invalid" "404"

echo "==================================================="
echo "Tests complete: $PASSED passed, $FAILED failed"
exit $FAILED

