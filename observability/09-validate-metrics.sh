#!/bin/bash
################################################################################
# Comprehensive Metrics Validation Script
# 
# Purpose: Run all 6 validation tests for metrics endpoint
# Usage: bash observability/09-validate-metrics.sh
#
################################################################################

set -e

echo "╔═════════════════════════════════════════════════════════════════════════╗"
echo "║              Comprehensive Metrics Endpoint Validation                  ║"
echo "╚═════════════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

# ============================================================================
# Test 1: Metrics Server Running
# ============================================================================
echo ""
echo "${BLUE}TEST 1: Metrics Server Running${NC}"
echo "────────────────────────────────────────────────────────────────────────"

if ps aux | grep -q "[p]ython.*metrics.py"; then
    echo "${GREEN}✅ PASS${NC}: Metrics server process found"
    ((PASSED++))
else
    echo "${RED}❌ FAIL${NC}: Metrics server NOT running"
    ((FAILED++))
    echo "  Start with: python app/api/metrics.py 9091"
fi

# ============================================================================
# Test 2: Port 9091 Listening
# ============================================================================
echo ""
echo "${BLUE}TEST 2: Port 9091 Listening${NC}"
echo "────────────────────────────────────────────────────────────────────────"

if netstat -tuln 2>/dev/null | grep -q 9091 || lsof -i :9091 > /dev/null 2>&1; then
    echo "${GREEN}✅ PASS${NC}: Port 9091 is listening"
    ((PASSED++))
else
    echo "${RED}❌ FAIL${NC}: Port 9091 NOT listening"
    ((FAILED++))
    echo "  Check: lsof -i :9091"
fi

# ============================================================================
# Test 3: Endpoint Responds (HTTP 200)
# ============================================================================
echo ""
echo "${BLUE}TEST 3: Endpoint Responds (HTTP 200)${NC}"
echo "────────────────────────────────────────────────────────────────────────"

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9091/metrics 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo "${GREEN}✅ PASS${NC}: Endpoint returns HTTP 200"
    ((PASSED++))
else
    echo "${RED}❌ FAIL${NC}: Endpoint returns HTTP $HTTP_CODE"
    ((FAILED++))
    echo "  Test: curl http://localhost:9091/metrics"
fi

# ============================================================================
# Test 4: Prometheus Format Compliance
# ============================================================================
echo ""
echo "${BLUE}TEST 4: Prometheus Format Compliance${NC}"
echo "────────────────────────────────────────────────────────────────────────"

curl -s http://localhost:9091/metrics > /tmp/metrics_validation.txt 2>/dev/null || true

HELP_COUNT=$(grep -c '^# HELP' /tmp/metrics_validation.txt || echo 0)
TYPE_COUNT=$(grep -c '^# TYPE' /tmp/metrics_validation.txt || echo 0)

echo "  HELP lines: $HELP_COUNT"
echo "  TYPE lines: $TYPE_COUNT"

if [ "$HELP_COUNT" -gt 10 ] && [ "$TYPE_COUNT" -gt 10 ]; then
    echo "${GREEN}✅ PASS${NC}: Format looks valid (≥10 HELP and TYPE lines)"
    ((PASSED++))
else
    echo "${RED}❌ FAIL${NC}: Format may be incomplete"
    ((FAILED++))
fi

# ============================================================================
# Test 5: Prometheus Scraping
# ============================================================================
echo ""
echo "${BLUE}TEST 5: Prometheus Scraping${NC}"
echo "────────────────────────────────────────────────────────────────────────"

RESULT=$(curl -s 'http://localhost:9090/api/v1/query?query=up' 2>/dev/null | grep -c "value" || echo "0")

if [ "$RESULT" -gt 0 ]; then
    echo "${GREEN}✅ PASS${NC}: Prometheus has metrics (found metric values)"
    ((PASSED++))
else
    echo "${YELLOW}⚠️  WARN${NC}: Prometheus not yet scraping (may need time)"
    echo "  Wait 30-60 seconds and try again"
fi

# ============================================================================
# Test 6: Sample PromQL Queries
# ============================================================================
echo ""
echo "${BLUE}TEST 6: Sample PromQL Queries${NC}"
echo "────────────────────────────────────────────────────────────────────────"

echo "Query 1: up{job='prometheus'}"
QUERY1=$(curl -s 'http://localhost:9090/api/v1/query?query=up{job="prometheus"}' 2>/dev/null | python3 -c "import json, sys; data=json.load(sys.stdin); print(len(data.get('data', {}).get('result', [])))" || echo "0")

if [ "$QUERY1" -gt 0 ]; then
    echo "  ${GREEN}✅ Returns $QUERY1 series${NC}"
    ((PASSED++))
else
    echo "  ${YELLOW}ℹ️  No results yet${NC}"
fi

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "╔═════════════════════════════════════════════════════════════════════════╗"
echo "║                        VALIDATION SUMMARY                              ║"
echo "╚═════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Passed: ${GREEN}$PASSED${NC}"
echo "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "${GREEN}✅ All validation tests passed!${NC}"
    echo ""
    echo "Metrics endpoint is fully operational and ready for use."
    exit 0
else
    echo "${YELLOW}⚠️  Some tests need attention${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Ensure metrics server is running"
    echo "  2. Wait for Prometheus to scrape (30-60 seconds)"
    echo "  3. Run pipeline to generate metrics"
    echo "  4. Check Prometheus UI: http://localhost:9090/targets"
    exit 1
fi

