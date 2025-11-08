#!/bin/bash
# Test script for Export API
# Tests endpoints in export.py
# Usage: ./test_export.sh [BASE_URL]

BASE_URL="${1:-http://localhost:8000}"
PASSED=0
FAILED=0

echo "Testing Export API endpoints at $BASE_URL"
echo "========================================"

test_endpoint() {
    local name="$1"
    local path="$2"
    local expected_status="${3:-200}"
    
    echo -n "Testing $name (GET $path)... "
    
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL$path")
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

# Test 1: GET /api/export/json
test_endpoint "Export Graph (JSON)" \
    "/api/export/json" "200"

# Test 2: GET /api/export/json (with filters)
test_endpoint "Export Graph (JSON with filters)" \
    "/api/export/json?entity_ids=test1,test2&community_id=test_comm" "200"

# Test 3: GET /api/export/csv
test_endpoint "Export Graph (CSV)" \
    "/api/export/csv" "200"

# Test 4: GET /api/export/graphml
test_endpoint "Export Graph (GraphML)" \
    "/api/export/graphml" "200"

# Test 5: GET /api/export/gexf
test_endpoint "Export Graph (GEXF)" \
    "/api/export/gexf" "200"

# Test 6: GET /api/export/invalid (invalid format)
test_endpoint "Export Graph (invalid format)" \
    "/api/export/invalid" "404"

echo "========================================"
echo "Tests complete: $PASSED passed, $FAILED failed"
exit $FAILED

