#!/bin/bash
# Test script for Communities API
# Tests endpoints in communities.py
# Usage: ./test_communities.sh [BASE_URL]

BASE_URL="${1:-http://localhost:8000}"
PASSED=0
FAILED=0

echo "Testing Communities API endpoints at $BASE_URL"
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

# Test 1: GET /api/communities/search (valid)
test_endpoint "Search Communities" \
    "/api/communities/search?limit=10&offset=0" "200"

# Test 2: GET /api/communities/search (with filters)
test_endpoint "Search Communities (with filters)" \
    "/api/communities/search?level=0&min_size=5&max_size=100&limit=5" "200"

# Test 3: GET /api/communities/levels
test_endpoint "Get Community Levels" \
    "/api/communities/levels" "200"

# Test 4: GET /api/communities/{community_id} (may return 404 if community doesn't exist)
test_endpoint "Get Community Details" \
    "/api/communities/test_community_123" "404"  # 404 expected if community doesn't exist

# Test 5: GET /api/communities (invalid path)
test_endpoint "Get Communities (invalid path)" \
    "/api/communities/invalid/path" "404"

echo "=============================================="
echo "Tests complete: $PASSED passed, $FAILED failed"
exit $FAILED

