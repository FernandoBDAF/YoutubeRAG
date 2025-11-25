#!/bin/bash
set -e

echo "═══════════════════════════════════════════════════════════════════════════"
echo "  Fixing and Restarting Observability Stack"
echo "═══════════════════════════════════════════════════════════════════════════"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "${BLUE}Step 1: Stopping containers...${NC}"
docker-compose -f docker-compose.observability.yml down
echo "${GREEN}✅ Stopped${NC}"

echo ""
echo "${BLUE}Step 2: Removing Loki volume...${NC}"
docker volume rm youtuberag_loki-data 2>/dev/null || echo "   (Volume not found)"
echo "${GREEN}✅ Cleaned${NC}"

echo ""
echo "${BLUE}Step 3: Starting stack with fixed config...${NC}"
docker-compose -f docker-compose.observability.yml up -d
echo "${GREEN}✅ Starting${NC}"

echo ""
echo "${BLUE}Step 4: Waiting 60 seconds for initialization...${NC}"
sleep 60

echo ""
echo "${BLUE}Step 5: Checking status...${NC}"
docker-compose -f docker-compose.observability.yml ps

echo ""
echo "${GREEN}✅ Fix and restart complete${NC}"
echo ""
echo "Services:"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana: http://localhost:3000"
echo "  Loki: http://localhost:3100"
echo ""
echo "Next: bash observability/04-e2e-test.sh"
