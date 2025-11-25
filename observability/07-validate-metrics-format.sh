#!/bin/bash
################################################################################
# Phase 2: Validate Metrics Format
# 
# Purpose: Access metrics endpoint and validate Prometheus format
# Usage: bash observability/07-validate-metrics-format.sh
#
################################################################################

set -e

echo "═══════════════════════════════════════════════════════════════════════════"
echo "  Phase 2: Validate Metrics Format"
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
# Step 1: Access metrics endpoint
# ============================================================================
echo "${BLUE}Step 1: Accessing metrics endpoint${NC}"
echo ""

echo "Fetching metrics from http://localhost:9091/metrics..."
curl -s http://localhost:9091/metrics > /tmp/metrics.txt
echo "${GREEN}✅ Metrics saved to /tmp/metrics.txt${NC}"
echo ""

# ============================================================================
# Step 2: Verify Prometheus format
# ============================================================================
echo "${BLUE}Step 2: Verifying Prometheus format compliance${NC}"
echo ""

TOTAL_LINES=$(wc -l < /tmp/metrics.txt)
HELP_COUNT=$(grep -c '^# HELP' /tmp/metrics.txt || echo 0)
TYPE_COUNT=$(grep -c '^# TYPE' /tmp/metrics.txt || echo 0)
METRIC_COUNT=$(grep -v '^#' /tmp/metrics.txt | grep -v '^$' | wc -l || echo 0)

echo "Format Verification:"
echo "  Total lines: $TOTAL_LINES"
echo "  HELP lines: $HELP_COUNT"
echo "  TYPE lines: $TYPE_COUNT"
echo "  Metric lines: $METRIC_COUNT"
echo ""

if [ "$HELP_COUNT" -gt 10 ] && [ "$TYPE_COUNT" -gt 10 ]; then
    echo "${GREEN}✅ Format looks valid (≥10 HELP and TYPE lines)${NC}"
else
    echo "${RED}⚠️  Format may be incomplete${NC}"
fi

# ============================================================================
# Step 3: Show sample metrics
# ============================================================================
echo ""
echo "${BLUE}Step 3: Sample metrics (first 20 lines)${NC}"
echo ""
head -20 /tmp/metrics.txt

# ============================================================================
# Step 4: Count metrics by category
# ============================================================================
echo ""
echo "${BLUE}Step 4: Metrics by category${NC}"
echo ""

STAGE_METRICS=$(grep -c 'stage_' /tmp/metrics.txt || echo 0)
AGENT_METRICS=$(grep -c 'agent_' /tmp/metrics.txt || echo 0)
ERROR_METRICS=$(grep -c 'errors_' /tmp/metrics.txt || echo 0)
OTHER_METRICS=$(grep -v '^#' /tmp/metrics.txt | grep -v '^$' | grep -v 'stage_' | grep -v 'agent_' | grep -v 'errors_' | wc -l || echo 0)

echo "Stage metrics: $STAGE_METRICS"
echo "Agent metrics: $AGENT_METRICS"
echo "Error metrics: $ERROR_METRICS"
echo "Other metrics: $OTHER_METRICS"
echo ""

# ============================================================================
# Step 5: Verify naming convention
# ============================================================================
echo "${BLUE}Step 5: Verifying naming conventions${NC}"
echo ""

# Check for snake_case
SNAKE_CASE=$(grep -v '^#' /tmp/metrics.txt | grep -v '^$' | grep -E '[a-z]+_[a-z]+' | wc -l || echo 0)
echo "Snake_case metrics: $SNAKE_CASE / $METRIC_COUNT"

# Check for label format
LABEL_FORMAT=$(grep -E '\{[a-z_]+="[^"]*"' /tmp/metrics.txt | wc -l || echo 0)
echo "Metrics with labels: $LABEL_FORMAT"

echo ""

# ============================================================================
# Step 6: Detailed metric breakdown
# ============================================================================
echo "${BLUE}Step 6: Detailed metric breakdown${NC}"
echo ""

echo "Stage metrics found:"
grep 'stage_' /tmp/metrics.txt | grep -v '^#' | sort -u | head -10 || echo "  (none)"
echo ""

echo "Agent metrics found:"
grep 'agent_' /tmp/metrics.txt | grep -v '^#' | sort -u | head -10 || echo "  (none)"
echo ""

# ============================================================================
# Step 7: Summary
# ============================================================================
echo "${BLUE}Step 7: Validation Summary${NC}"
echo ""

if [ "$HELP_COUNT" -gt 0 ] && [ "$TYPE_COUNT" -gt 0 ] && [ "$METRIC_COUNT" -gt 0 ]; then
    echo "${GREEN}✅ Metrics endpoint is responding with valid Prometheus format${NC}"
    echo ""
    echo "Summary:"
    echo "  • Total Prometheus metrics: $METRIC_COUNT"
    echo "  • HELP descriptions: $HELP_COUNT"
    echo "  • TYPE declarations: $TYPE_COUNT"
    echo "  • Stage metrics found: $STAGE_METRICS"
    echo "  • Agent metrics found: $AGENT_METRICS"
else
    echo "${RED}❌ Metrics endpoint may not be responding correctly${NC}"
fi

echo ""
echo "Metrics output saved to: /tmp/metrics.txt"
echo ""
