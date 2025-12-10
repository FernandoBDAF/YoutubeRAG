#!/bin/bash
# Test script for Performance Metrics API
# Tests endpoint in performance_metrics.py
# Usage: ./test_performance_metrics.sh [BASE_URL]

BASE_URL="${1:-http://localhost:8000}"
PASSED=0
FAILED=0

echo "Testing Performance Metrics API endpoints at $BASE_URL"
echo "====================================================="

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

# Test 1: GET /api/performance/metrics
test_endpoint "Get Performance Metrics" \
    "/api/performance/metrics" "200"

# Test 2: GET /api/performance/metrics (invalid path)
test_endpoint "Get Performance Metrics (invalid path)" \
    "/api/performance/metrics/invalid" "404"

echo "====================================================="
echo "Tests complete: $PASSED passed, $FAILED failed"
exit $FAILED

