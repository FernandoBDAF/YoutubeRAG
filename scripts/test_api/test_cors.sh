#!/bin/bash
# CORS & OPTIONS Testing Script
# Tests OPTIONS requests and CORS headers for all API endpoints
# Usage: ./test_cors.sh [BASE_URL]

BASE_URL="${1:-http://localhost:8000}"
PASSED=0
FAILED=0
WARNINGS=0

echo "Testing CORS & OPTIONS Support"
echo "=============================="
echo "Base URL: $BASE_URL"
echo ""

test_options() {
    local name="$1"
    local path="$2"
    
    echo -n "Testing OPTIONS $name ($path)... "
    
    response=$(curl -s -w "\n%{http_code}" -X OPTIONS \
        -H "Origin: http://localhost:3000" \
        -H "Access-Control-Request-Method: POST" \
        -H "Access-Control-Request-Headers: Content-Type" \
        "$BASE_URL$path")
    
    status_code=$(echo "$response" | tail -n1)
    headers=$(curl -s -I -X OPTIONS \
        -H "Origin: http://localhost:3000" \
        "$BASE_URL$path" | grep -i "access-control")
    
    if [ "$status_code" = "200" ]; then
        if echo "$headers" | grep -qi "access-control-allow-origin"; then
            echo "✓ (HTTP 200, CORS headers present)"
            ((PASSED++))
            return 0
        else
            echo "⚠ (HTTP 200, but missing CORS headers)"
            ((WARNINGS++))
            return 1
        fi
    elif [ "$status_code" = "501" ]; then
        echo "✗ (HTTP 501 - OPTIONS handler missing)"
        ((FAILED++))
        return 1
    elif [ "$status_code" = "000" ]; then
        echo "✗ (Connection failed - server not running)"
        ((FAILED++))
        return 1
    else
        echo "✗ (HTTP $status_code - unexpected)"
        ((FAILED++))
        return 1
    fi
}

test_cors_headers() {
    local name="$1"
    local method="$2"
    local path="$3"
    
    echo -n "Testing CORS headers $name ($method $path)... "
    
    if [ "$method" = "GET" ]; then
        headers=$(curl -s -I -H "Origin: http://localhost:3000" "$BASE_URL$path" | grep -i "access-control")
    else
        headers=$(curl -s -I -X "$method" \
            -H "Origin: http://localhost:3000" \
            -H "Content-Type: application/json" \
            -d '{}' \
            "$BASE_URL$path" | grep -i "access-control")
    fi
    
    if echo "$headers" | grep -qi "access-control-allow-origin"; then
        echo "✓ (CORS headers present)"
        ((PASSED++))
        return 0
    else
        echo "✗ (Missing CORS headers)"
        ((FAILED++))
        return 1
    fi
}

echo "=== OPTIONS Request Testing (POST Endpoints) ==="
echo ""

# Test OPTIONS for POST endpoints
test_options "Pipeline Start" "/api/pipeline/start"
test_options "Pipeline Cancel" "/api/pipeline/cancel"
test_options "Pipeline Resume" "/api/pipeline/resume"

echo ""
echo "=== CORS Headers Testing (GET Endpoints) ==="
echo ""

# Test CORS headers in GET responses
test_cors_headers "Pipeline Status" "GET" "/api/pipeline/status?pipeline_id=test"
test_cors_headers "Pipeline History" "GET" "/api/pipeline/history"
test_cors_headers "Entities Search" "GET" "/api/entities/search"
test_cors_headers "Relationships Search" "GET" "/api/relationships/search"
test_cors_headers "Communities Search" "GET" "/api/communities/search"

echo ""
echo "=== CORS Headers Testing (Error Responses) ==="
echo ""

# Test CORS headers in error responses (404s)
test_cors_headers "404 Response (invalid path)" "GET" "/api/pipeline/invalid"
test_cors_headers "404 Response (entity not found)" "GET" "/api/entities/nonexistent_123"

echo ""
echo "=============================="
echo "Tests complete: $PASSED passed, $FAILED failed, $WARNINGS warnings"
exit $FAILED

