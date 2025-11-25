#!/bin/bash
# Test Script for Achievement 1.3: Grafana Dashboards Configured
# Validates that Grafana dashboards are properly configured and functional

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Achievement 1.3: Grafana Dashboards Validation Test    ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Helper function to run test
run_test() {
    local test_name="$1"
    local test_command="$2"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -e "${YELLOW}[TEST $TOTAL_TESTS]${NC} $test_name"
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 1: Grafana Service Health${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Test 1: Grafana container running
run_test "Grafana container is running" \
    "docker ps | grep -q grafana"

# Test 2: Grafana HTTP endpoint accessible
run_test "Grafana HTTP endpoint accessible (port 3000)" \
    "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 | grep -q 200"

# Test 3: Grafana API health check
run_test "Grafana API health check" \
    "curl -s http://localhost:3000/api/health | grep -q '\"database\":\"ok\"'"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 2: Data Source Configuration${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Test 4: Prometheus data source exists
run_test "Prometheus data source configured" \
    "curl -s -u admin:admin http://localhost:3000/api/datasources | grep -q '\"type\":\"prometheus\"'"

# Test 5: Loki data source exists
run_test "Loki data source configured" \
    "curl -s -u admin:admin http://localhost:3000/api/datasources | grep -q '\"type\":\"loki\"'"

# Test 6: Prometheus data source healthy
run_test "Prometheus data source health check" \
    "curl -s http://localhost:9090/-/healthy | grep -q 'Prometheus'"

# Test 7: Loki data source healthy
run_test "Loki data source health check" \
    "curl -s http://localhost:3100/ready | grep -q 'ready'"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 3: Dashboard Provisioning${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Test 8: Dashboard JSON file exists
run_test "Dashboard JSON file exists" \
    "test -f observability/grafana/dashboards/graphrag-pipeline.json"

# Test 9: Dashboard provisioning config exists
run_test "Dashboard provisioning config exists" \
    "test -f observability/grafana/dashboards/dashboard-provisioning.yml"

# Test 10: Dashboard accessible via API
run_test "GraphRAG dashboard accessible via API" \
    "curl -s -u admin:admin http://localhost:3000/api/search | grep -q 'GraphRAG Pipeline'"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 4: Dashboard Structure Validation${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Test 11: Dashboard has title
run_test "Dashboard JSON has title field" \
    "grep -q '\"title\"' observability/grafana/dashboards/graphrag-pipeline.json"

# Test 12: Dashboard has panels
run_test "Dashboard JSON has panels" \
    "grep -q '\"panels\"' observability/grafana/dashboards/graphrag-pipeline.json"

# Test 13: Dashboard has datasource references
run_test "Dashboard panels reference Prometheus datasource" \
    "grep -q '\"datasource\"' observability/grafana/dashboards/graphrag-pipeline.json"

# Test 14: Dashboard JSON is valid
run_test "Dashboard JSON syntax is valid" \
    "python3 -m json.tool observability/grafana/dashboards/graphrag-pipeline.json"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 5: Panel Functionality (Sample Queries)${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Test 15: Prometheus accepts sample query
run_test "Prometheus accepts 'up' query" \
    "curl -s 'http://localhost:9090/api/v1/query?query=up' | grep -q '\"status\":\"success\"'"

# Test 16: Prometheus accepts GraphRAG metrics query
run_test "Prometheus accepts 'graphrag_pipeline_status' query" \
    "curl -s 'http://localhost:9090/api/v1/query?query=graphrag_pipeline_status' | grep -q '\"status\":\"success\"'"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}╔═════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ ALL TESTS PASSED                      ║${NC}"
    echo -e "${GREEN}╚═════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Achievement 1.3 is validated and operational."
    exit 0
else
    echo -e "${RED}╔═════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ SOME TESTS FAILED                     ║${NC}"
    echo -e "${RED}╚═════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Please review the failed tests above."
    exit 1
fi

