#!/bin/bash
################################################################################
# Master Deployment Script for Achievement 1.1
# 
# Purpose: Run complete deployment sequence for observability stack
# Usage: bash observability/RUN-DEPLOYMENT.sh
#
################################################################################

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                           ║"
echo "║          Achievement 1.1: Observability Stack Deployment                 ║"
echo "║                                                                           ║"
echo "║              Master Deployment Script for Human Executor                  ║"
echo "║                                                                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

# Run deployment phases in sequence
echo "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
echo "${BLUE}PHASE 0: Pre-Flight Checks${NC}"
echo "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
echo ""

bash observability/00-preflight-checks.sh
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Pre-flight checks failed. Fix issues above and try again."
    exit 1
fi

echo ""
echo ""
echo "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
echo "${BLUE}PHASE 1: Stack Startup${NC}"
echo "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
echo ""

bash observability/01-start-stack.sh
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Stack startup failed. Check logs:"
    echo "   docker-compose -f docker-compose.observability.yml logs"
    exit 1
fi

echo ""
echo ""
echo "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
echo "${BLUE}PHASE 2: Comprehensive Debug${NC}"
echo "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
echo ""

bash observability/02-debug-all.sh

echo ""
echo ""
echo "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
echo "${BLUE}PHASE 3: Integration Verification${NC}"
echo "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
echo ""

bash observability/03-verify-integration.sh

echo ""
echo ""
echo "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
echo "${BLUE}PHASE 4: End-to-End Testing${NC}"
echo "${BLUE}═══════════════════════════════════════════════════════════════════════════${NC}"
echo ""

bash observability/04-e2e-test.sh
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ E2E tests failed."
    exit 1
fi

echo ""
echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                           ║"
echo "║          ${GREEN}✅ DEPLOYMENT COMPLETE${NC}                                       ║"
echo "║                                                                           ║"
echo "║              All 4 Phases Successfully Completed                          ║"
echo "║                                                                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Services Running:"
echo "  ${BLUE}Prometheus${NC}: http://localhost:9090"
echo "  ${BLUE}Grafana${NC}:    http://localhost:3000 (admin/admin)"
echo "  ${BLUE}Loki${NC}:       http://localhost:3100"
echo "  ${BLUE}Promtail${NC}:   (log shipper, no UI)"
echo ""
echo "Next Steps:"
echo "  1. Open Grafana: http://localhost:3000"
echo "  2. Verify datasources (Configuration → Data Sources)"
echo "  3. Create dashboards"
echo "  4. Run test metrics: python3 observability/04-generate-test-metrics.py"
echo ""
echo "Documentation: observability/01_DEPLOYMENT_GUIDE.md"
echo ""


