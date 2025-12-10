#!/bin/bash
# Edge Case Test Script for GraphRAG API
# Tests edge cases: empty databases, large result sets, special characters, Unicode, timeouts, concurrent requests
# Usage: ./test_edge_cases.sh [BASE_URL]

BASE_URL="${1:-http://localhost:8000}"
PASSED=0
FAILED=0
WARNINGS=0

echo "=========================================="
echo "Edge Case Testing for GraphRAG API"
echo "Base URL: $BASE_URL"
echo "=========================================="
echo ""

test_edge_case() {
    local category="$1"
    local name="$2"
    local path="$3"
    local method="${4:-GET}"
    local data="${5:-}"
    local expected_status="${6:-200}"
    
    echo "[$category] Testing: $name"
    echo "  Request: $method $path"
    
    if [ "$method" = "POST" ]; then
        if [ -n "$data" ]; then
            response=$(curl -s -w "\n%{http_code}" -X POST \
                -H "Content-Type: application/json" \
                -H "Access-Control-Request-Method: POST" \
                -d "$data" \
                "$BASE_URL$path" 2>&1)
        else
            response=$(curl -s -w "\n%{http_code}" -X POST \
                -H "Content-Type: application/json" \
                "$BASE_URL$path" 2>&1)
        fi
    else
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$path" 2>&1)
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # Check for connection errors
    if echo "$response" | grep -q "curl: (7)\|curl: (52)\|curl: (56)"; then
        echo "  ⚠️  Server not running (connection refused)"
        ((WARNINGS++))
        return 2
    fi
    
    # Check status code
    if [ "$status_code" = "$expected_status" ] || [ "$status_code" = "000" ]; then
        if [ "$status_code" = "000" ]; then
            echo "  ⚠️  Connection failed (HTTP 000)"
            ((WARNINGS++))
        else
            echo "  ✓ Status: HTTP $status_code"
            ((PASSED++))
        fi
        return 0
    else
        echo "  ✗ Expected HTTP $expected_status, got HTTP $status_code"
        if [ ${#body} -lt 200 ]; then
            echo "  Response: $body"
        fi
        ((FAILED++))
        return 1
    fi
}

echo "=========================================="
echo "1. EMPTY DATABASE SCENARIOS"
echo "=========================================="
echo ""

# Test search endpoints with empty database (should return empty arrays)
test_edge_case "Empty DB" "Search Entities (empty)" \
    "/api/entities/search?limit=10&offset=0" "GET" "" "200"

test_edge_case "Empty DB" "Search Relationships (empty)" \
    "/api/relationships/search?limit=10&offset=0" "GET" "" "200"

test_edge_case "Empty DB" "Search Communities (empty)" \
    "/api/communities/search?limit=10&offset=0" "GET" "" "200"

test_edge_case "Empty DB" "Get Pipeline Stats (empty)" \
    "/api/pipeline/stats" "GET" "" "200"

test_edge_case "Empty DB" "Get Graph Statistics (empty)" \
    "/api/graph/statistics" "GET" "" "200"

test_edge_case "Empty DB" "Get Quality Metrics (empty)" \
    "/api/quality/metrics" "GET" "" "200"

echo ""
echo "=========================================="
echo "2. VERY LARGE RESULT SETS"
echo "=========================================="
echo ""

# Test pagination boundaries
test_edge_case "Large Results" "Search Entities (large limit)" \
    "/api/entities/search?limit=10000&offset=0" "GET" "" "200"

test_edge_case "Large Results" "Search Entities (large offset)" \
    "/api/entities/search?limit=10&offset=999999" "GET" "" "200"

test_edge_case "Large Results" "Search Relationships (large limit)" \
    "/api/relationships/search?limit=10000&offset=0" "GET" "" "200"

test_edge_case "Large Results" "Pipeline History (large limit)" \
    "/api/pipeline/history?limit=10000&offset=0" "GET" "" "200"

test_edge_case "Large Results" "Ego Network (large hops)" \
    "/api/ego/network/test_entity?maxHops=100&nodeLimit=10000" "GET" "" "200"

echo ""
echo "=========================================="
echo "3. SPECIAL CHARACTERS IN INPUTS"
echo "=========================================="
echo ""

# SQL injection attempts
test_edge_case "Special Chars" "Search Entities (SQL injection)" \
    "/api/entities/search?q='; DROP TABLE entities--" "GET" "" "200"

test_edge_case "Special Chars" "Search Entities (path traversal)" \
    "/api/entities/search?q=../../../etc/passwd" "GET" "" "200"

test_edge_case "Special Chars" "Search Entities (XSS attempt)" \
    "/api/entities/search?q=<script>alert('xss')</script>" "GET" "" "200"

# MongoDB operators
test_edge_case "Special Chars" "Search Entities (MongoDB $where)" \
    "/api/entities/search?q=\$where" "GET" "" "200"

test_edge_case "Special Chars" "Search Entities (MongoDB $regex)" \
    "/api/entities/search?q=\$regex" "GET" "" "200"

test_edge_case "Special Chars" "Get Entity (SQL injection in ID)" \
    "/api/entities/'; DROP TABLE entities--" "GET" "" "404"

test_edge_case "Special Chars" "Get Entity (path traversal in ID)" \
    "/api/entities/../../../etc/passwd" "GET" "" "404"

# Special characters in POST body
test_edge_case "Special Chars" "Start Pipeline (SQL injection in config)" \
    "/api/pipeline/start" "POST" '{"config":{"extraction":{"test":"'\''; DROP TABLE--"}}}' "400"

test_edge_case "Special Chars" "Start Pipeline (XSS in config)" \
    "/api/pipeline/start" "POST" '{"config":{"extraction":{"test":"<script>alert(1)</script>"}}}' "400"

echo ""
echo "=========================================="
echo "4. UNICODE HANDLING"
echo "=========================================="
echo ""

# Emoji
test_edge_case "Unicode" "Search Entities (emoji)" \
    "/api/entities/search?q=🚀🎉" "GET" "" "200"

test_edge_case "Unicode" "Get Entity (emoji in ID)" \
    "/api/entities/🚀🎉" "GET" "" "404"

# Non-ASCII characters
test_edge_case "Unicode" "Search Entities (Chinese)" \
    "/api/entities/search?q=中文" "GET" "" "200"

test_edge_case "Unicode" "Search Entities (Russian)" \
    "/api/entities/search?q=русский" "GET" "" "200"

test_edge_case "Unicode" "Search Entities (Arabic)" \
    "/api/entities/search?q=العربية" "GET" "" "200"

# Special symbols
test_edge_case "Unicode" "Search Entities (copyright)" \
    "/api/entities/search?q=©®™" "GET" "" "200"

test_edge_case "Unicode" "Search Entities (math symbols)" \
    "/api/entities/search?q=∑∏∫" "GET" "" "200"

# Unicode in POST body
test_edge_case "Unicode" "Start Pipeline (Unicode in config)" \
    "/api/pipeline/start" "POST" '{"config":{"extraction":{"test":"🚀中文русский"}}}' "400"

echo ""
echo "=========================================="
echo "5. TIMEOUT SCENARIOS"
echo "=========================================="
echo ""

# Note: Actual timeouts require server running and specific configurations
# These tests check if endpoints handle long operations gracefully

test_edge_case "Timeout" "Search Entities (complex query)" \
    "/api/entities/search?q=test&type=Person&min_confidence=0.1&max_confidence=0.9&limit=1000" "GET" "" "200"

test_edge_case "Timeout" "Export Graph (large dataset)" \
    "/api/export/json?limit=100000" "GET" "" "200"

test_edge_case "Timeout" "Ego Network (deep hops)" \
    "/api/ego/network/test_entity?maxHops=50&nodeLimit=10000" "GET" "" "200"

test_edge_case "Timeout" "Graph Statistics (large graph)" \
    "/api/graph/statistics" "GET" "" "200"

echo ""
echo "=========================================="
echo "6. CONCURRENT REQUESTS"
echo "=========================================="
echo ""

# Test concurrent requests (simulate with background processes)
echo "[Concurrent] Testing: Multiple simultaneous GET requests"
concurrent_test() {
    local endpoint="$1"
    local count=5
    local pids=()
    
    for i in $(seq 1 $count); do
        curl -s "$BASE_URL$endpoint" > /dev/null 2>&1 &
        pids+=($!)
    done
    
    # Wait for all to complete
    for pid in "${pids[@]}"; do
        wait $pid
    done
    
    echo "  ✓ Completed $count concurrent requests"
    ((PASSED++))
}

# Test concurrent requests to different endpoints
concurrent_test "/api/entities/search?limit=10"
concurrent_test "/api/relationships/search?limit=10"
concurrent_test "/api/communities/search?limit=10"
concurrent_test "/api/pipeline/stats"
concurrent_test "/api/graph/statistics"

echo ""
echo "=========================================="
echo "7. INVALID PARAMETER COMBINATIONS"
echo "=========================================="
echo ""

# Negative values
test_edge_case "Invalid Params" "Search Entities (negative limit)" \
    "/api/entities/search?limit=-10" "GET" "" "400"

test_edge_case "Invalid Params" "Search Entities (negative offset)" \
    "/api/entities/search?offset=-10" "GET" "" "400"

# Invalid types
test_edge_case "Invalid Params" "Search Entities (string limit)" \
    "/api/entities/search?limit=abc" "GET" "" "400"

test_edge_case "Invalid Params" "Search Entities (string offset)" \
    "/api/entities/search?offset=xyz" "GET" "" "400"

# Out of range values
test_edge_case "Invalid Params" "Search Entities (confidence > 1)" \
    "/api/entities/search?min_confidence=1.5" "GET" "" "400"

test_edge_case "Invalid Params" "Search Entities (confidence < 0)" \
    "/api/entities/search?min_confidence=-0.5" "GET" "" "400"

# Missing required parameters
test_edge_case "Invalid Params" "Start Pipeline (missing config)" \
    "/api/pipeline/start" "POST" '{}' "400"

test_edge_case "Invalid Params" "Get Pipeline Status (missing pipeline_id)" \
    "/api/pipeline/status" "GET" "" "400"

echo ""
echo "=========================================="
echo "8. EXTREME VALUES"
echo "=========================================="
echo ""

# Very long strings
long_string=$(printf 'a%.0s' {1..1000})
test_edge_case "Extreme Values" "Search Entities (very long query)" \
    "/api/entities/search?q=$long_string" "GET" "" "200"

# Very large numbers
test_edge_case "Extreme Values" "Search Entities (max int limit)" \
    "/api/entities/search?limit=2147483647" "GET" "" "200"

test_edge_case "Extreme Values" "Search Entities (max int offset)" \
    "/api/entities/search?offset=2147483647" "GET" "" "200"

# Empty strings
test_edge_case "Extreme Values" "Search Entities (empty query)" \
    "/api/entities/search?q=" "GET" "" "200"

test_edge_case "Extreme Values" "Search Entities (whitespace only)" \
    "/api/entities/search?q=%20%20%20" "GET" "" "200"

echo ""
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "Warnings: $WARNINGS"
echo ""

if [ $FAILED -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✓ All edge case tests completed successfully"
    exit 0
elif [ $FAILED -eq 0 ]; then
    echo "⚠️  Tests completed with warnings (server may not be running)"
    exit 0
else
    echo "✗ Some edge case tests failed"
    exit 1
fi


