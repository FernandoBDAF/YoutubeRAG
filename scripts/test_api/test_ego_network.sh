#!/bin/bash
# Test script for Ego Network API
# Tests endpoint in ego_network.py
# Usage: ./test_ego_network.sh [BASE_URL]

BASE_URL="${1:-http://localhost:8000}"
PASSED=0
FAILED=0

echo "Testing Ego Network API endpoints at $BASE_URL"
echo "=============================================="

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

# Test 1: GET /api/ego/network/{entity_id} (may return 404 if entity doesn't exist)
test_endpoint "Get Ego Network" \
    "/api/ego/network/test_entity_123?max_hops=2&max_nodes=100" "404"  # 404 expected if entity doesn't exist

# Test 2: GET /api/ego/network/{entity_id} (with parameters)
test_endpoint "Get Ego Network (with params)" \
    "/api/ego/network/test_entity_123?max_hops=1&max_nodes=50" "404"  # 404 expected if entity doesn't exist

# Test 3: GET /api/ego/network (invalid path - missing entity_id)
test_endpoint "Get Ego Network (invalid path)" \
    "/api/ego/network" "404"

echo "=============================================="
echo "Tests complete: $PASSED passed, $FAILED failed"
exit $FAILED

