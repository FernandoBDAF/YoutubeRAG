#!/bin/bash
# Test script for Graph Statistics API
# Tests endpoints in graph_statistics.py
# Usage: ./test_graph_statistics.sh [BASE_URL]

BASE_URL="${1:-http://localhost:8000}"
PASSED=0
FAILED=0

echo "Testing Graph Statistics API endpoints at $BASE_URL"
echo "=================================================="

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

# Test 1: GET /api/graph/statistics
test_endpoint "Get Graph Statistics" \
    "/api/graph/statistics" "200"

# Test 2: GET /api/graph/trends
test_endpoint "Get Graph Trends" \
    "/api/graph/trends?limit=50" "200"

# Test 3: GET /api/graph/trends (with default limit)
test_endpoint "Get Graph Trends (default limit)" \
    "/api/graph/trends" "200"

# Test 4: GET /api/graph (invalid path)
test_endpoint "Get Graph (invalid path)" \
    "/api/graph/invalid" "404"

echo "=================================================="
echo "Tests complete: $PASSED passed, $FAILED failed"
exit $FAILED

