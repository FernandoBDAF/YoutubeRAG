#!/bin/bash
################################################################################
# Phase 2: Comprehensive Debug Script
# 
# Purpose: Debug and verify all observability services
# Usage: bash observability/02-debug-all.sh
#
################################################################################

set -e

echo "═══════════════════════════════════════════════════════════════════════════"
echo "  Phase 2: Comprehensive Observability Stack Debug"
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
# Debug 1: Docker Status
# ============================================================================
echo "${BLUE}═══ Debug 1: Docker Status ═══${NC}"
echo ""

docker-compose -f docker-compose.observability.yml ps

echo ""

# ============================================================================
# Debug 2: Network Status
# ============================================================================
echo "${BLUE}═══ Debug 2: Network Status ═══${NC}"
echo ""

NETWORK_NAME=$(docker network ls --filter name=observability -q | head -1)
if [ -n "$NETWORK_NAME" ]; then
    echo "Network: $NETWORK_NAME"
    docker network inspect "$NETWORK_NAME" | grep -A 20 '"Containers"' | grep '"Name"' | head -5
    echo ""
fi

# ============================================================================
# Debug 3: Service Endpoints
# ============================================================================
echo "${BLUE}═══ Debug 3: Service Endpoints ═══${NC}"
echo ""

echo "Testing Prometheus (http://localhost:9090)..."
if curl -s -I http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo "${GREEN}✅${NC} Prometheus is responding"
else
    echo "${RED}❌${NC} Prometheus is NOT responding"
fi

echo ""
echo "Testing Grafana (http://localhost:3000)..."
if curl -s -I http://localhost:3000 > /dev/null 2>&1; then
    echo "${GREEN}✅${NC} Grafana is responding"
else
    echo "${RED}❌${NC} Grafana is NOT responding"
fi

echo ""
echo "Testing Loki (http://localhost:3100)..."
if curl -s -I http://localhost:3100/ready > /dev/null 2>&1; then
    echo "${GREEN}✅${NC} Loki is responding"
else
    echo "${RED}❌${NC} Loki is NOT responding"
fi

# ============================================================================
# Debug 4: Prometheus Configuration
# ============================================================================
echo ""
echo "${BLUE}═══ Debug 4: Prometheus Configuration ═══${NC}"
echo ""

echo "Prometheus config file:"
docker exec youtuberag-prometheus cat /etc/prometheus/prometheus.yml | head -20
echo "  ... (truncated)"

# ============================================================================
# Debug 5: Prometheus Targets
# ============================================================================
echo ""
echo "${BLUE}═══ Debug 5: Prometheus Targets ═══${NC}"
echo ""

curl -s http://localhost:9090/api/v1/targets 2>/dev/null | python3 << 'PYTHON_EOF' || echo "  (Python not available or Prometheus not responding)"
import json, sys
try:
    data = json.load(sys.stdin)
    targets = data.get('data', {}).get('activeTargets', [])
    print(f"Active Targets: {len(targets)}")
    for target in targets[:5]:
        labels = target.get('labels', {})
        health = target.get('health', 'unknown')
        print(f"  - {labels.get('job', 'unknown')}: {health}")
except:
    pass
PYTHON_EOF

# ============================================================================
# Debug 6: Loki Status
# ============================================================================
echo ""
echo "${BLUE}═══ Debug 6: Loki Status ═══${NC}"
echo ""

echo "Loki config file:"
docker exec youtuberag-loki cat /etc/loki/local-config.yaml | head -15
echo "  ... (truncated)"

echo ""
echo "Loki ready status:"
curl -s http://localhost:3100/ready 2>/dev/null

# ============================================================================
# Debug 7: Promtail Status
# ============================================================================
echo ""
echo "${BLUE}═══ Debug 7: Promtail Status ═══${NC}"
echo ""

echo "Promtail config file:"
docker exec youtuberag-promtail cat /etc/promtail/config.yml | head -15
echo "  ... (truncated)"

echo ""
echo "Promtail logs (last 10 lines):"
docker logs --tail=10 youtuberag-promtail 2>&1 | tail -10

# ============================================================================
# Debug 8: Grafana Status
# ============================================================================
echo ""
echo "${BLUE}═══ Debug 8: Grafana Status ═══${NC}"
echo ""

echo "Grafana environment:"
docker exec youtuberag-grafana env | grep GF_ | head -10

echo ""
echo "Grafana provisioning directories:"
docker exec youtuberag-grafana ls -la /etc/grafana/provisioning/ 2>/dev/null || echo "  (provisioning not found)"

# ============================================================================
# Debug 9: Container Logs
# ============================================================================
echo ""
echo "${BLUE}═══ Debug 9: Recent Container Logs ═══${NC}"
echo ""

for container in youtuberag-prometheus youtuberag-grafana youtuberag-loki youtuberag-promtail; do
    echo "${YELLOW}$container (last 5 lines):${NC}"
    docker logs --tail=5 "$container" 2>&1 | sed 's/^/  /'
    echo ""
done

# ============================================================================
# Debug 10: File System
# ============================================================================
echo ""
echo "${BLUE}═══ Debug 10: File System ═══${NC}"
echo ""

echo "Logs directory:"
if [ -d "logs" ]; then
    ls -lah logs/ | head -10
else
    echo "  logs/ directory not found"
fi

echo ""
echo "Observability directory:"
ls -lah observability/ | grep -E "^d|^-" | head -10

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "${GREEN}✅ Debug Complete${NC}"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "Access Services:"
echo "  ${BLUE}Prometheus${NC}: http://localhost:9090"
echo "  ${BLUE}Grafana${NC}:    http://localhost:3000 (admin/admin)"
echo "  ${BLUE}Loki${NC}:       http://localhost:3100"
echo ""
echo "Next step: bash observability/03-verify-integration.sh"
echo ""


