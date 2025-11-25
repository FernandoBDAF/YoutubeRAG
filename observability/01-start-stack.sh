#!/bin/bash
################################################################################
# Phase 1: Start Observability Stack
# 
# Purpose: Start all Docker containers for the observability stack
# Usage: bash observability/01-start-stack.sh
#
################################################################################

set -e

echo "═══════════════════════════════════════════════════════════════════════════"
echo "  Phase 1: Starting Observability Stack"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT" || exit 1

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Step 1: Verify configuration files
echo "${BLUE}Step 1: Verifying configuration files...${NC}"
if [ ! -f "docker-compose.observability.yml" ]; then
    echo "${RED}❌ docker-compose.observability.yml not found${NC}"
    exit 1
fi
echo "${GREEN}✅ docker-compose.observability.yml found${NC}"

# Step 2: Create logs directory
echo ""
echo "${BLUE}Step 2: Creating logs directory...${NC}"
mkdir -p logs
echo "${GREEN}✅ Logs directory ready${NC}"

# Step 3: Remove old containers (if any)
echo ""
echo "${BLUE}Step 3: Cleaning up old containers...${NC}"
docker-compose -f docker-compose.observability.yml down 2>/dev/null || true
echo "${GREEN}✅ Old containers cleaned${NC}"

# Step 4: Start stack
echo ""
echo "${BLUE}Step 4: Starting observability stack...${NC}"
echo "  (This may take 1-2 minutes on first run)"
echo ""

if docker-compose -f docker-compose.observability.yml up -d; then
    echo ""
    echo "${GREEN}✅ Docker-compose up successful${NC}"
else
    echo ""
    echo "${RED}❌ Docker-compose up failed${NC}"
    exit 1
fi

# Step 5: Wait for services to start
echo ""
echo "${BLUE}Step 5: Waiting for services to initialize...${NC}"
echo "  ⏳ Waiting 30 seconds..."
sleep 30

# Step 6: Verify container status
echo ""
echo "${BLUE}Step 6: Verifying container status...${NC}"
echo ""

docker-compose -f docker-compose.observability.yml ps

# Step 7: Check if containers are actually running
echo ""
CONTAINERS_RUNNING=true

if ! docker-compose -f docker-compose.observability.yml ps | grep -q "youtuberag-prometheus.*running"; then
    echo "${RED}❌ Prometheus not running${NC}"
    CONTAINERS_RUNNING=false
fi

if ! docker-compose -f docker-compose.observability.yml ps | grep -q "youtuberag-grafana.*running"; then
    echo "${RED}❌ Grafana not running${NC}"
    CONTAINERS_RUNNING=false
fi

if ! docker-compose -f docker-compose.observability.yml ps | grep -q "youtuberag-loki.*running"; then
    echo "${RED}❌ Loki not running${NC}"
    CONTAINERS_RUNNING=false
fi

if ! docker-compose -f docker-compose.observability.yml ps | grep -q "youtuberag-promtail.*running"; then
    echo "${RED}❌ Promtail not running${NC}"
    CONTAINERS_RUNNING=false
fi

echo ""
if [ "$CONTAINERS_RUNNING" = true ]; then
    echo "${GREEN}✅ All containers running${NC}"
else
    echo "${RED}⚠️  Some containers not running. Check logs:${NC}"
    echo "  docker-compose -f docker-compose.observability.yml logs"
    exit 1
fi

# Step 8: Summary
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "${GREEN}✅ Phase 1 Complete: Stack Started${NC}"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "Services now running:"
echo "  ${BLUE}Prometheus${NC}: http://localhost:9090"
echo "  ${BLUE}Grafana${NC}:    http://localhost:3000 (admin/admin)"
echo "  ${BLUE}Loki${NC}:       http://localhost:3100"
echo ""
echo "Next step: bash observability/02-debug-all.sh"
echo ""


