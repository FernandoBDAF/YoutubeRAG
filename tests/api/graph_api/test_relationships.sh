#!/bin/bash
# Test script for Relationships API
# Tests endpoint in relationships.py
# Usage: ./test_relationships.sh [BASE_URL]

BASE_URL="${1:-http://localhost:8000}"
PASSED=0
FAILED=0

echo "Testing Relationships API endpoints at $BASE_URL"
echo "==============================================="

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

# Test 1: GET /api/relationships/search (valid)
test_endpoint "Search Relationships" \
    "/api/relationships/search?limit=10&offset=0" "200"

# Test 2: GET /api/relationships/search (with filters)
test_endpoint "Search Relationships (with filters)" \
    "/api/relationships/search?predicate=locatedIn&min_confidence=0.5&limit=5" "200"

# Test 3: GET /api/relationships (invalid path)
test_endpoint "Get Relationships (invalid path)" \
    "/api/relationships/invalid/path" "404"

echo "==============================================="
echo "Tests complete: $PASSED passed, $FAILED failed"
exit $FAILED

