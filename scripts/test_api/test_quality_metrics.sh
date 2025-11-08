#!/bin/bash
# Test script for Quality Metrics API
# Tests endpoint in quality_metrics.py
# Usage: ./test_quality_metrics.sh [BASE_URL]

BASE_URL="${1:-http://localhost:8000}"
PASSED=0
FAILED=0

echo "Testing Quality Metrics API endpoints at $BASE_URL"
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

# Test 1: GET /api/quality/metrics (all stages)
test_endpoint "Get Quality Metrics" \
    "/api/quality/metrics" "200"

# Test 2: GET /api/quality/metrics (specific stage)
test_endpoint "Get Quality Metrics (specific stage)" \
    "/api/quality/metrics?stage=extraction" "200"

# Test 3: GET /api/quality/metrics (invalid path)
test_endpoint "Get Quality Metrics (invalid path)" \
    "/api/quality/metrics/invalid" "404"

echo "=================================================="
echo "Tests complete: $PASSED passed, $FAILED failed"
exit $FAILED

