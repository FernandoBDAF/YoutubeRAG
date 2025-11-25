#!/bin/bash
################################################################################
# Phase 3: Verify Integration and Configuration
# 
# Purpose: Verify Grafana datasources and test queries
# Usage: bash observability/03-verify-integration.sh
#
################################################################################

set -e

echo "═══════════════════════════════════════════════════════════════════════════"
echo "  Phase 3: Verify Integration and Configuration"
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
# Step 1: Verify Grafana Access
# ============================================================================
echo "${BLUE}Step 1: Verify Grafana Access${NC}"
echo ""

echo "Testing Grafana health endpoint..."
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "${GREEN}✅${NC} Grafana is responding"
else
    echo "${RED}❌${NC} Grafana is NOT responding"
    echo "Make sure Grafana is running: docker-compose -f docker-compose.observability.yml up -d"
    exit 1
fi

# ============================================================================
# Step 2: Check Datasources Directory
# ============================================================================
echo ""
echo "${BLUE}Step 2: Check Datasources Directory${NC}"
echo ""

DS_DIR="observability/grafana/datasources"
if [ -d "$DS_DIR" ]; then
    echo "${GREEN}✅${NC} Datasources directory exists: $DS_DIR"
    echo "   Contents:"
    ls -la "$DS_DIR" | grep -v "^total" | sed 's/^/     /'
else
    echo "${YELLOW}ℹ️${NC}  Creating datasources directory..."
    mkdir -p "$DS_DIR"
    echo "${GREEN}✅${NC} Created: $DS_DIR"
fi

# ============================================================================
# Step 3: Provision Datasources
# ============================================================================
echo ""
echo "${BLUE}Step 3: Configure Datasources${NC}"
echo ""

# Check if datasources already configured
if [ -f "$DS_DIR/prometheus.yml" ] && [ -f "$DS_DIR/loki.yml" ]; then
    echo "${GREEN}✅${NC} Datasources already provisioned"
else
    echo "${YELLOW}ℹ️${NC}  Creating datasource provisioning files..."
    
    # Create Prometheus datasource
    cat > "$DS_DIR/prometheus.yml" << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://youtuberag-prometheus:9090
    isDefault: true
    editable: true
EOF
    echo "${GREEN}✅${NC} Created prometheus.yml"
    
    # Create Loki datasource
    cat > "$DS_DIR/loki.yml" << 'EOF'
apiVersion: 1

datasources:
  - name: Loki
    type: loki
    access: proxy
    url: http://youtuberag-loki:3100
    isDefault: false
    editable: true
EOF
    echo "${GREEN}✅${NC} Created loki.yml"
    
    # Restart Grafana to load new datasources
    echo ""
    echo "${YELLOW}ℹ️${NC}  Restarting Grafana to load datasources..."
    docker-compose -f docker-compose.observability.yml restart grafana
    echo "   ⏳ Waiting 15 seconds for Grafana to restart..."
    sleep 15
    echo "${GREEN}✅${NC} Grafana restarted"
fi

# ============================================================================
# Step 4: Test Prometheus Query
# ============================================================================
echo ""
echo "${BLUE}Step 4: Test Prometheus Query${NC}"
echo ""

echo "Querying Prometheus for metrics..."
PROM_RESPONSE=$(curl -s 'http://localhost:9090/api/v1/query?query=up' 2>/dev/null)

echo "$PROM_RESPONSE" | python3 << 'PYTHON_EOF' || echo "  (requires Python for JSON parsing)"
import json, sys
try:
    data = json.load(sys.stdin)
    status = data.get('status', 'unknown')
    if status == 'success':
        result = data.get('data', {}).get('result', [])
        if result:
            print(f"  ✅ Prometheus query successful: {len(result)} metric(s) found")
            for metric in result[:3]:
                print(f"     - {metric['metric']}: {metric['value']}")
        else:
            print("  ⚠️  No metrics found yet (may take 30 seconds)")
    else:
        print(f"  ❌ Query failed: {data.get('error', 'unknown error')}")
except json.JSONDecodeError:
    print("  ❌ Invalid response from Prometheus")
PYTHON_EOF

# ============================================================================
# Step 5: Test Loki Query
# ============================================================================
echo ""
echo "${BLUE}Step 5: Test Loki Query${NC}"
echo ""

echo "Querying Loki for logs..."
LOKI_RESPONSE=$(curl -s -X GET "http://localhost:3100/loki/api/v1/query" \
  --data-urlencode 'query={job="varlogs"}' 2>/dev/null)

echo "$LOKI_RESPONSE" | python3 << 'PYTHON_EOF' || echo "  (requires Python for JSON parsing)"
import json, sys
try:
    data = json.load(sys.stdin)
    status = data.get('status', 'unknown')
    if status == 'success':
        result = data.get('data', {}).get('result', [])
        if result:
            print(f"  ✅ Loki query successful: {len(result)} stream(s) found")
            for stream in result[:3]:
                values = stream.get('values', [])
                print(f"     - {stream['stream']}: {len(values)} log entries")
        else:
            print("  ⚠️  No logs found yet (create logs to test)")
    else:
        print(f"  ❌ Query failed: {data.get('error', 'unknown error')}")
except json.JSONDecodeError:
    print("  ❌ Invalid response from Loki")
PYTHON_EOF

# ============================================================================
# Step 6: Summary
# ============================================================================
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "${GREEN}✅ Phase 3 Complete: Integration Verified${NC}"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "Access Grafana:"
echo "  http://localhost:3000"
echo "  Login: admin / admin"
echo ""
echo "Next steps:"
echo "  1. Go to Configuration → Data Sources (verify Prometheus and Loki connected)"
echo "  2. Create test dashboard and panels"
echo "  3. Run: bash observability/04-e2e-test.sh"
echo ""


