#!/bin/bash
# validate-achievement-11.sh - Achievement 1.1: Observability Stack Running

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
print_header() { echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"; echo -e "${BLUE}$1${NC}"; echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"; }
print_test() { echo -e "${YELLOW}TEST $1:${NC} $2"; }
print_pass() { echo -e "${GREEN}✅ PASS:${NC} $1"; ((TESTS_PASSED++)); }
print_fail() { echo -e "${RED}❌ FAIL:${NC} $1"; ((TESTS_FAILED++)); }
run_test() { ((TESTS_RUN++)); }

# Get project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../../../.."

################################################################################
# Test 1: Docker Containers Running
################################################################################

test_docker_containers() {
    print_header "TEST 1: Docker Containers Running"
    run_test
    
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        print_fail "Docker command not found"
        return 1
    fi
    
    # Check for observability containers
    CONTAINERS=(
        "prometheus"
        "grafana"
        "loki"
        "promtail"
    )
    
    ALL_RUNNING=true
    for container in "${CONTAINERS[@]}"; do
        if docker ps --format '{{.Names}}' | grep -q "$container"; then
            print_pass "$container container is running"
        else
            print_fail "$container container not running"
            ALL_RUNNING=false
        fi
    done
    
    if [ "$ALL_RUNNING" = false ]; then
        echo ""
        echo "  To start observability stack:"
        echo "  docker-compose -f docker-compose.observability.yml up -d"
        return 1
    fi
}

################################################################################
# Test 2: Service Endpoints Accessible
################################################################################

test_service_endpoints() {
    print_header "TEST 2: Service Endpoints Accessible"
    run_test
    
    # Test Prometheus endpoint
    if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
        print_pass "Prometheus endpoint accessible (http://localhost:9090)"
    else
        print_fail "Prometheus endpoint not accessible"
    fi
    
    # Test Grafana endpoint
    if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
        print_pass "Grafana endpoint accessible (http://localhost:3000)"
    else
        print_fail "Grafana endpoint not accessible"
    fi
    
    # Test Loki endpoint
    if curl -s http://localhost:3100/ready > /dev/null 2>&1; then
        print_pass "Loki endpoint accessible (http://localhost:3100)"
    else
        print_fail "Loki endpoint not accessible"
    fi
}

################################################################################
# Test 3: Service Connectivity
################################################################################

test_service_connectivity() {
    print_header "TEST 3: Service Connectivity"
    run_test
    
    # Check if Prometheus can reach its targets
    if command -v curl &> /dev/null; then
        TARGETS=$(curl -s http://localhost:9090/api/v1/targets 2>/dev/null)
        if [ -n "$TARGETS" ]; then
            print_pass "Prometheus targets API responding"
            
            # Check if any targets are up
            if echo "$TARGETS" | grep -q '"health":"up"'; then
                print_pass "At least one Prometheus target is up"
            else
                print_fail "No Prometheus targets are up"
            fi
        else
            print_fail "Cannot reach Prometheus targets API"
        fi
    else
        print_fail "curl not available for connectivity tests"
        return 1
    fi
}

################################################################################
# Test 4: Configuration Files
################################################################################

test_configuration_files() {
    print_header "TEST 4: Configuration Files"
    run_test
    
    CONFIG_FILES=(
        "$PROJECT_ROOT/docker-compose.observability.yml"
        "$PROJECT_ROOT/observability/prometheus/prometheus.yml"
        "$PROJECT_ROOT/observability/grafana/provisioning/datasources/datasources.yml"
    )
    
    ALL_FOUND=true
    for config_file in "${CONFIG_FILES[@]}"; do
        if [ -f "$config_file" ]; then
            print_pass "$(basename $(dirname $config_file))/$(basename $config_file) exists"
        else
            print_fail "Missing: $config_file"
            ALL_FOUND=false
        fi
    done
    
    if [ "$ALL_FOUND" = false ]; then
        return 1
    fi
}

################################################################################
# Main
################################################################################

main() {
    print_header "ACHIEVEMENT 1.1 VALIDATION"
    echo ""
    echo "Testing: Observability Stack Running"
    echo ""
    
    test_docker_containers
    echo ""
    test_service_endpoints
    echo ""
    test_service_connectivity
    echo ""
    test_configuration_files
    echo ""
    
    # Summary
    print_header "SUMMARY"
    echo "Tests Run: $TESTS_RUN"
    echo "Passed: $TESTS_PASSED ✅"
    echo "Failed: $TESTS_FAILED ❌"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✅ ACHIEVEMENT 1.1: VALIDATED${NC}"
        echo ""
        echo "All observability services are running and accessible!"
        exit 0
    else
        echo -e "${RED}❌ ACHIEVEMENT 1.1: NEEDS FIXES${NC}"
        exit 1
    fi
}

main "$@"

