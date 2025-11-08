#!/bin/bash
# Test script for Entities API
# Tests endpoints in entities.py
# Usage: ./test_entities.sh [BASE_URL]

BASE_URL="${1:-http://localhost:8000}"
PASSED=0
FAILED=0

echo "Testing Entities API endpoints at $BASE_URL"
echo "==========================================="

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

# Test 1: GET /api/entities/search (valid)
test_endpoint "Search Entities" \
    "/api/entities/search?limit=10&offset=0" "200"

# Test 2: GET /api/entities/search (with filters)
test_endpoint "Search Entities (with filters)" \
    "/api/entities/search?q=test&type=Person&min_confidence=0.5&limit=5" "200"

# Test 3: GET /api/entities/{entity_id} (valid - may return 404 if entity doesn't exist)
test_endpoint "Get Entity Details" \
    "/api/entities/test_entity_123" "404"  # 404 expected if entity doesn't exist

# Test 4: GET /api/entities (invalid path)
test_endpoint "Get Entities (invalid path)" \
    "/api/entities/invalid/path" "404"

echo "==========================================="
echo "Tests complete: $PASSED passed, $FAILED failed"
exit $FAILED

