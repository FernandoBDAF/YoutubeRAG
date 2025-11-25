#!/bin/bash
################################################################################
# Pre-Flight Checks for Observability Stack Deployment
# 
# Purpose: Verify all prerequisites before attempting deployment
# Usage: bash observability/00-preflight-checks.sh
#
################################################################################

set -e

echo "═══════════════════════════════════════════════════════════════════════════"
echo "  Pre-Flight Checks for Observability Stack Deployment"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

CHECKS_PASSED=0
CHECKS_FAILED=0

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: Docker installed
echo "Checking: Docker installation..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo "  ${GREEN}✅${NC} Docker installed: $DOCKER_VERSION"
    ((CHECKS_PASSED++))
else
    echo "  ${RED}❌${NC} Docker not found. Install Docker Desktop or Docker Engine."
    ((CHECKS_FAILED++))
fi

# Check 2: Docker daemon running
echo ""
echo "Checking: Docker daemon..."
if docker ps &> /dev/null; then
    echo "  ${GREEN}✅${NC} Docker daemon running"
    ((CHECKS_PASSED++))
else
    echo "  ${RED}❌${NC} Docker daemon not running. Start Docker Desktop or Docker service."
    ((CHECKS_FAILED++))
fi

# Check 3: docker-compose installed
echo ""
echo "Checking: docker-compose installation..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo "  ${GREEN}✅${NC} docker-compose installed: $COMPOSE_VERSION"
    ((CHECKS_PASSED++))
else
    echo "  ${RED}❌${NC} docker-compose not found. Install docker-compose."
    ((CHECKS_FAILED++))
fi

# Check 4: Configuration files
echo ""
echo "Checking: Configuration files..."
CONFIG_FILES=(
    "docker-compose.observability.yml"
    "observability/prometheus/prometheus.yml"
    "observability/loki/loki-config.yml"
    "observability/promtail/promtail-config.yml"
)

CONFIG_OK=true
for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ${GREEN}✅${NC} Found: $file"
    else
        echo "  ${RED}❌${NC} Missing: $file"
        CONFIG_OK=false
    fi
done

if [ "$CONFIG_OK" = true ]; then
    ((CHECKS_PASSED++))
else
    ((CHECKS_FAILED++))
fi

# Check 5: Required ports available
echo ""
echo "Checking: Required ports..."
PORTS=(9090 3100 3000)
PORTS_OK=true

for port in "${PORTS[@]}"; do
    if nc -z localhost $port 2>/dev/null; then
        echo "  ${YELLOW}⚠️${NC}  Port $port already in use"
        PORTS_OK=false
    else
        echo "  ${GREEN}✅${NC} Port $port available"
    fi
done

if [ "$PORTS_OK" = true ]; then
    ((CHECKS_PASSED++))
else
    echo "  ${YELLOW}ℹ️  Port conflicts detected - services may fail to start"
    ((CHECKS_FAILED++))
fi

# Check 6: logs directory
echo ""
echo "Checking: Logs directory..."
if [ -d "logs" ]; then
    echo "  ${GREEN}✅${NC} logs/ directory exists"
    ((CHECKS_PASSED++))
else
    echo "  ${YELLOW}ℹ️${NC}  logs/ directory not found - will be created during startup"
    mkdir -p logs
    echo "  ${GREEN}✅${NC} Created logs/ directory"
    ((CHECKS_PASSED++))
fi

# Summary
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "Pre-Flight Check Results:"
echo "  ${GREEN}Passed: $CHECKS_PASSED${NC}"
echo "  ${RED}Failed: $CHECKS_FAILED${NC}"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo "${GREEN}✅ All pre-flight checks passed!${NC}"
    echo ""
    echo "Ready to deploy observability stack."
    echo ""
    echo "Next step: bash observability/01-start-stack.sh"
    exit 0
else
    echo "${RED}❌ Some checks failed. Please fix issues above before proceeding.${NC}"
    exit 1
fi


