#!/bin/bash
# Error Handling Testing Script
# Tests error responses (404, 400, 500) and verifies JSON format
# Usage: ./test_error_handling.sh [BASE_URL]

BASE_URL="${1:-http://localhost:8000}"
PASSED=0
FAILED=0
WARNINGS=0

echo "Testing Error Handling"
echo "====================="
echo "Base URL: $BASE_URL"
echo ""

test_error_response() {
    local name="$1"
    local method="$2"
    local path="$3"
    local expected_status="$4"
    local expected_json="$5"
    
    echo -n "Testing $name ($method $path)... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$path")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$6" \
            "$BASE_URL$path")
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" = "000" ]; then
        echo "✗ (Connection failed - server not running)"
        ((FAILED++))
        return 1
    fi
    
    if [ "$status_code" != "$expected_status" ]; then
        echo "✗ (Expected HTTP $expected_status, got HTTP $status_code)"
        ((FAILED++))
        return 1
    fi
    
    if [ "$expected_json" = "true" ]; then
        if echo "$body" | grep -q "^{.*}$" || echo "$body" | grep -q "^<"; then
            if echo "$body" | grep -q "^<"; then
                echo "✗ (HTTP $status_code, but response is HTML, not JSON)"
                ((FAILED++))
                return 1
            else
                if echo "$body" | python3 -m json.tool >/dev/null 2>&1; then
                    echo "✓ (HTTP $status_code, valid JSON response)"
                    ((PASSED++))
                    return 0
                else
                    echo "⚠ (HTTP $status_code, looks like JSON but invalid)"
                    ((WARNINGS++))
                    return 1
                fi
            fi
        else
            if [ -z "$body" ]; then
                echo "⚠ (HTTP $status_code, but empty response body)"
                ((WARNINGS++))
                return 1
            else
                echo "✗ (HTTP $status_code, but response is not JSON)"
                ((FAILED++))
                return 1
            fi
        fi
    else
        echo "✓ (HTTP $status_code)"
        ((PASSED++))
        return 0
    fi
}

echo "=== 404 Error Testing (Invalid Paths) ==="
echo ""

# Test 404 errors - invalid paths
test_error_response "404 - Invalid Pipeline Path" "GET" "/api/pipeline/invalid" "404" "true"
test_error_response "404 - Invalid Entities Path" "GET" "/api/entities/invalid/path" "404" "true"
test_error_response "404 - Invalid Relationships Path" "GET" "/api/relationships/invalid" "404" "true"
test_error_response "404 - Invalid Communities Path" "GET" "/api/communities/invalid/path" "404" "true"

echo ""
echo "=== 404 Error Testing (Non-existent Resources) ==="
echo ""

# Test 404 errors - non-existent resources
test_error_response "404 - Non-existent Entity" "GET" "/api/entities/nonexistent_entity_12345" "404" "true"
test_error_response "404 - Non-existent Community" "GET" "/api/communities/nonexistent_community_12345" "404" "true"
test_error_response "404 - Non-existent Pipeline" "GET" "/api/pipeline/status?pipeline_id=nonexistent_123" "404" "true"

echo ""
echo "=== 400 Error Testing (Missing Parameters) ==="
echo ""

# Test 400 errors - missing required parameters
test_error_response "400 - Missing Pipeline ID (Cancel)" "POST" "/api/pipeline/cancel" "400" "true" "{}"
test_error_response "400 - Missing Pipeline ID (Status)" "GET" "/api/pipeline/status" "400" "true"

echo ""
echo "=== 400 Error Testing (Invalid JSON) ==="
echo ""

# Test 400 errors - invalid JSON
test_error_response "400 - Invalid JSON (Start)" "POST" "/api/pipeline/start" "400" "true" "{invalid json}"

echo ""
echo "=== 400 Error Testing (Invalid Parameters) ==="
echo ""

# Test 400 errors - invalid parameter values
test_error_response "400 - Invalid Limit (Negative)" "GET" "/api/entities/search?limit=-1" "400" "true"
test_error_response "400 - Invalid Offset (Negative)" "GET" "/api/entities/search?offset=-1" "400" "true"

echo ""
echo "=== Edge Case Testing ==="
echo ""

# Test edge cases
test_error_response "Edge - Empty Request Body" "POST" "/api/pipeline/start" "400" "true" ""
test_error_response "Edge - Missing Content-Type" "POST" "/api/pipeline/start" "400" "true" "{\"test\":\"data\"}"

echo ""
echo "====================="
echo "Tests complete: $PASSED passed, $FAILED failed, $WARNINGS warnings"
exit $FAILED

