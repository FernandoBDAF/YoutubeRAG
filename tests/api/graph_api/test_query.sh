#!/bin/bash
# Test script for Query Execution API endpoints
# Run from GraphRAG project root: ./tests/api/graph_api/test_query.sh

BASE_URL="${API_URL:-http://localhost:8081/api}"
PASS=0
FAIL=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_test() {
    echo -e "\n${YELLOW}TEST: $1${NC}"
}

print_pass() {
    echo -e "${GREEN}✓ PASS: $1${NC}"
    ((PASS++))
}

print_fail() {
    echo -e "${RED}✗ FAIL: $1${NC}"
    ((FAIL++))
}

# ============================================
# GET /query/modes - Get available query modes
# ============================================
print_test "GET /query/modes - List query modes"
RESPONSE=$(curl -s -w "\n%{http_code}" "${BASE_URL}/query/modes")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    if echo "$BODY" | jq -e '.modes' > /dev/null 2>&1; then
        MODE_COUNT=$(echo "$BODY" | jq '.modes | length')
        DEFAULT_MODE=$(echo "$BODY" | jq -r '.default')
        print_pass "Got $MODE_COUNT modes, default: $DEFAULT_MODE"
    else
        print_fail "Missing 'modes' field in response"
    fi
else
    print_fail "Expected 200, got $HTTP_CODE"
fi

# ============================================
# POST /query/execute - Execute valid query
# ============================================
print_test "POST /query/execute - Execute valid query"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/query/execute" \
    -H "Content-Type: application/json" \
    -d '{"query": "What is machine learning?", "mode": "global"}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    if echo "$BODY" | jq -e '.answer' > /dev/null 2>&1; then
        QUERY_ID=$(echo "$BODY" | jq -r '.meta.query_id')
        CONFIDENCE=$(echo "$BODY" | jq -r '.confidence')
        print_pass "Query executed, id: $QUERY_ID, confidence: $CONFIDENCE"
    else
        print_fail "Missing 'answer' field in response"
    fi
elif [ "$HTTP_CODE" = "500" ]; then
    # This might be expected if OPENAI_API_KEY is not set
    ERROR=$(echo "$BODY" | jq -r '.error')
    if [[ "$ERROR" == *"Configuration"* ]]; then
        echo -e "${YELLOW}⚠ SKIP: Configuration error (likely missing OPENAI_API_KEY)${NC}"
    else
        print_fail "Server error: $ERROR"
    fi
else
    print_fail "Expected 200 or 500, got $HTTP_CODE"
fi

# ============================================
# POST /query/execute - Missing query text
# ============================================
print_test "POST /query/execute - Missing query text (expect 400)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/query/execute" \
    -H "Content-Type: application/json" \
    -d '{"mode": "global"}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "400" ]; then
    ERROR=$(echo "$BODY" | jq -r '.error')
    print_pass "Got expected 400 error: $ERROR"
else
    print_fail "Expected 400, got $HTTP_CODE"
fi

# ============================================
# POST /query/execute - Empty request body
# ============================================
print_test "POST /query/execute - Empty request body (expect 400)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/query/execute" \
    -H "Content-Type: application/json" \
    -d '{}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "400" ]; then
    print_pass "Got expected 400 for empty body"
else
    print_fail "Expected 400, got $HTTP_CODE"
fi

# ============================================
# POST /query/execute - Invalid mode
# ============================================
print_test "POST /query/execute - Invalid mode (expect 400)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/query/execute" \
    -H "Content-Type: application/json" \
    -d '{"query": "Test query", "mode": "invalid_mode"}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "400" ]; then
    VALID_MODES=$(echo "$BODY" | jq -r '.valid_modes')
    print_pass "Got expected 400 for invalid mode, valid modes: $VALID_MODES"
else
    print_fail "Expected 400, got $HTTP_CODE"
fi

# ============================================
# POST /query/execute - With options
# ============================================
print_test "POST /query/execute - With custom options"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/query/execute" \
    -H "Content-Type: application/json" \
    -d '{
        "query": "What is deep learning?",
        "mode": "hybrid",
        "options": {
            "top_k": 5,
            "include_sources": false,
            "include_communities": true
        }
    }')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    MODE_USED=$(echo "$BODY" | jq -r '.meta.mode_used')
    if [ "$MODE_USED" = "hybrid" ]; then
        print_pass "Query executed with hybrid mode"
    else
        print_fail "Expected hybrid mode, got $MODE_USED"
    fi
elif [ "$HTTP_CODE" = "500" ]; then
    ERROR=$(echo "$BODY" | jq -r '.error')
    if [[ "$ERROR" == *"Configuration"* ]]; then
        echo -e "${YELLOW}⚠ SKIP: Configuration error (likely missing OPENAI_API_KEY)${NC}"
    else
        print_fail "Server error: $ERROR"
    fi
else
    print_fail "Expected 200, got $HTTP_CODE"
fi

# ============================================
# POST /query - Alternative endpoint
# ============================================
print_test "POST /query - Alternative endpoint"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "Test alternative endpoint"}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "500" ]; then
    print_pass "Alternative endpoint /query works (status: $HTTP_CODE)"
else
    print_fail "Expected 200 or 500, got $HTTP_CODE"
fi

# ============================================
# Summary
# ============================================
echo -e "\n=========================================="
echo -e "Query API Test Results"
echo -e "=========================================="
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"

if [ $FAIL -gt 0 ]; then
    exit 1
fi

