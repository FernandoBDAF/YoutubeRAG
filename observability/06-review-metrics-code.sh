#!/bin/bash
################################################################################
# Phase 1: Review & Start Metrics Server
# 
# Purpose: Review metrics implementation and start the metrics server
# Usage: bash observability/06-review-metrics-code.sh
#
################################################################################

set -e

echo "═══════════════════════════════════════════════════════════════════════════"
echo "  Phase 1: Review Metrics Code & Start Server"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

# ============================================================================
# Step 1: Review metrics implementation
# ============================================================================
echo "${BLUE}Step 1: Reviewing app/api/metrics.py${NC}"
echo ""

if [ -f "app/api/metrics.py" ]; then
    echo "${GREEN}✅ File found${NC}"
    echo ""
    echo "First 50 lines of app/api/metrics.py:"
    echo "─────────────────────────────────────"
    head -50 app/api/metrics.py
    echo ""
    echo "File info:"
    wc -l app/api/metrics.py
else
    echo "${YELLOW}⚠️  app/api/metrics.py not found${NC}"
fi

# ============================================================================
# Step 2: Review prometheus metrics definitions
# ============================================================================
echo ""
echo "${BLUE}Step 2: Reviewing business/services/observability/prometheus_metrics.py${NC}"
echo ""

if [ -f "business/services/observability/prometheus_metrics.py" ]; then
    echo "${GREEN}✅ File found${NC}"
    echo ""
    echo "First 50 lines of prometheus_metrics.py:"
    echo "────────────────────────────────────────"
    head -50 business/services/observability/prometheus_metrics.py
    echo ""
    echo "File info:"
    wc -l business/services/observability/prometheus_metrics.py
else
    echo "${YELLOW}⚠️  prometheus_metrics.py not found${NC}"
fi

# ============================================================================
# Step 3: Verify port configuration
# ============================================================================
echo ""
echo "${BLUE}Step 3: Verifying port configuration${NC}"
echo ""

echo "Searching for port 9091 references..."
grep -r "9091" app/ business/ observability/ 2>/dev/null | head -10 || echo "No explicit port 9091 found (may use default)"

# ============================================================================
# Step 4: Check Prometheus configuration
# ============================================================================
echo ""
echo "${BLUE}Step 4: Checking Prometheus configuration${NC}"
echo ""

if [ -f "observability/prometheus/prometheus.yml" ]; then
    echo "${GREEN}✅ Prometheus config found${NC}"
    echo ""
    echo "Relevant sections from prometheus.yml:"
    echo "────────────────────────────────────"
    grep -A10 "9091\|metrics\|scrape" observability/prometheus/prometheus.yml | head -20 || echo "No 9091 target found yet"
else
    echo "${YELLOW}⚠️  Prometheus config not found${NC}"
fi

# ============================================================================
# Step 5: Start metrics server
# ============================================================================
echo ""
echo "${BLUE}Step 5: Starting metrics server on port 9091${NC}"
echo ""

echo "Command: ${YELLOW}python app/api/metrics.py 9091${NC}"
echo ""
echo "Starting in 3 seconds... Press Ctrl+C to stop."
sleep 3

# Start metrics server
python app/api/metrics.py 9091

# Note: The script will block here running the server.
# In another terminal, run:
# - ps aux | grep metrics.py (to verify running)
# - curl http://localhost:9091/metrics (to test endpoint)
