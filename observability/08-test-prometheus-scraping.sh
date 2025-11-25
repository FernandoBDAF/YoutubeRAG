#!/bin/bash
################################################################################
# Phase 3: Test Prometheus Scraping
# 
# Purpose: Test if Prometheus is successfully scraping metrics
# Usage: bash observability/08-test-prometheus-scraping.sh
#
################################################################################

set -e

echo "═══════════════════════════════════════════════════════════════════════════"
echo "  Phase 3: Test Prometheus Scraping"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

# ============================================================================
# Test 1: Check if Prometheus can reach the endpoint from container
# ============================================================================
echo "${BLUE}Test 1: Prometheus Container Access to Metrics Endpoint${NC}"
echo ""

echo "Running: docker exec youtuberag-prometheus curl -s http://localhost:9091/metrics | head -5"
echo ""

if docker exec youtuberag-prometheus curl -s http://localhost:9091/metrics 2>/dev/null | head -5; then
    echo ""
    echo "${GREEN}✅ Prometheus container can reach metrics endpoint${NC}"
else
    echo ""
    echo "${RED}❌ Prometheus container cannot reach metrics endpoint${NC}"
    echo "This may indicate a network connectivity issue"
fi

# ============================================================================
# Test 2: Query Prometheus directly for targets
# ============================================================================
echo ""
echo "${BLUE}Test 2: Checking Prometheus Targets${NC}"
echo ""

echo "Active targets in Prometheus:"
curl -s 'http://localhost:9090/api/v1/targets' 2>/dev/null | python3 << 'PYTHON'
import json, sys
try:
    data = json.load(sys.stdin)
    targets = data.get('data', {}).get('activeTargets', [])
    print(f"  Total active targets: {len(targets)}")
    for target in targets[:5]:
        labels = target.get('labels', {})
        health = target.get('health', 'unknown')
        print(f"    • {labels.get('job', 'unknown')}: {health}")
except Exception as e:
    print(f"Error: {e}")
PYTHON

# ============================================================================
# Test 3: Query Prometheus for "up" metric
# ============================================================================
echo ""
echo "${BLUE}Test 3: Querying Prometheus - up metric${NC}"
echo ""

echo "Query: up{job='prometheus'}"
echo "Response:"
curl -s 'http://localhost:9090/api/v1/query?query=up{job="prometheus"}' 2>/dev/null | python3 << 'PYTHON'
import json, sys
try:
    data = json.load(sys.stdin)
    status = data.get('status')
    result = data.get('data', {}).get('result', [])
    if status == 'success':
        if result:
            print(f"  ✅ Found {len(result)} series")
            for series in result[:3]:
                print(f"    • {series.get('metric', {})}: {series.get('value', [None, 'N/A'])[1]}")
        else:
            print("  ⚠️  Query executed but no results returned")
    else:
        print(f"  ❌ Query error: {data.get('error', 'unknown')}")
except Exception as e:
    print(f"  Error: {e}")
PYTHON

# ============================================================================
# Test 4: Check specific metrics - stage_started
# ============================================================================
echo ""
echo "${BLUE}Test 4: Querying Prometheus - stage_started metric${NC}"
echo ""

echo "Query: stage_started"
echo "Response:"
curl -s 'http://localhost:9090/api/v1/query?query=stage_started' 2>/dev/null | python3 << 'PYTHON'
import json, sys
try:
    data = json.load(sys.stdin)
    status = data.get('status')
    result = data.get('data', {}).get('result', [])
    if status == 'success':
        if result:
            print(f"  ✅ Found {len(result)} series")
            for series in result[:3]:
                metric = series.get('metric', {})
                value = series.get('value', [None, 'N/A'])[1]
                stage = metric.get('stage', 'unknown')
                print(f"    • {stage}: {value}")
        else:
            print("  ⚠️  stage_started metric not found (may need pipeline data)")
    else:
        print(f"  ❌ Query error: {data.get('error', 'unknown')}")
except Exception as e:
    print(f"  Error: {e}")
PYTHON

# ============================================================================
# Test 5: Check metrics count
# ============================================================================
echo ""
echo "${BLUE}Test 5: Checking metrics in Prometheus database${NC}"
echo ""

echo "Attempting to query for any metrics..."
RESULT=$(curl -s 'http://localhost:9090/api/v1/query?query={__name__=~".+"}' 2>/dev/null | python3 -c "import json, sys; data=json.load(sys.stdin); print(len(data.get('data', {}).get('result', [])))" || echo "0")

if [ "$RESULT" -gt 0 ]; then
    echo "  ${GREEN}✅ Prometheus has $RESULT metric series${NC}"
else
    echo "  ${YELLOW}⚠️  No metrics found (may need time for scraping)${NC}"
fi

# ============================================================================
# Test 6: Rate queries (if time-series data available)
# ============================================================================
echo ""
echo "${BLUE}Test 6: Testing rate queries (requires time-series data)${NC}"
echo ""

echo "Query: rate(stage_completed[1m])"
echo "Response:"
curl -s 'http://localhost:9090/api/v1/query?query=rate(stage_completed[1m])' 2>/dev/null | python3 << 'PYTHON'
import json, sys
try:
    data = json.load(sys.stdin)
    status = data.get('status')
    result = data.get('data', {}).get('result', [])
    if status == 'success':
        if result:
            print(f"  ✅ Found {len(result)} series")
        else:
            print("  ℹ️  No rate data yet (needs multiple scrapes)")
    else:
        print(f"  ℹ️  Not yet available: {data.get('error', 'unknown')}")
except Exception as e:
    print(f"  Error: {e}")
PYTHON

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "${BLUE}Summary${NC}"
echo ""
echo "Prometheus Scraping Tests Complete"
echo ""
echo "If tests show no metrics, this could mean:"
echo "  1. Metrics server is not yet registered as a target"
echo "  2. Prometheus hasn't scraped yet (wait 30 seconds)"
echo "  3. Pipeline hasn't run to generate metrics"
echo "  4. Network connectivity issue between Prometheus and metrics server"
echo ""
echo "Next steps:"
echo "  1. Check http://localhost:9090/targets in browser"
echo "  2. Wait 30-60 seconds for Prometheus to scrape"
echo "  3. Run pipeline to generate metrics"
echo ""

