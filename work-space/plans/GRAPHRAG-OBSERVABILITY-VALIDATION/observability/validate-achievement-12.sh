#!/bin/bash
# validate-achievement-12.sh - Achievement 1.2: Metrics Endpoint Validated

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
# Test 1: Metrics Endpoint Accessible
################################################################################

test_metrics_endpoint() {
    print_header "TEST 1: Metrics Endpoint Accessible"
    run_test
    
    # Check if metrics endpoint is accessible
    METRICS_URL="http://localhost:9091/metrics"
    
    if command -v curl &> /dev/null; then
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$METRICS_URL" 2>/dev/null)
        
        if [ "$RESPONSE" = "200" ]; then
            print_pass "Metrics endpoint accessible at $METRICS_URL"
        else
            print_fail "Metrics endpoint not accessible (HTTP $RESPONSE)"
            echo "  Note: Ensure metrics server is running:"
            echo "  python app/api/metrics.py 9091"
            return 1
        fi
    else
        print_fail "curl not available for endpoint tests"
        return 1
    fi
}

################################################################################
# Test 2: Prometheus Format Validation
################################################################################

test_prometheus_format() {
    print_header "TEST 2: Prometheus Format Validation"
    run_test
    
    METRICS_URL="http://localhost:9091/metrics"
    
    if command -v curl &> /dev/null; then
        METRICS_OUTPUT=$(curl -s "$METRICS_URL" 2>/dev/null)
        
        if [ -n "$METRICS_OUTPUT" ]; then
            print_pass "Metrics endpoint returns data"
            
            # Check for Prometheus format indicators
            if echo "$METRICS_OUTPUT" | grep -q "^# HELP\|^# TYPE"; then
                print_pass "Prometheus format detected (HELP/TYPE comments)"
            else
                print_fail "Prometheus format not detected"
                return 1
            fi
            
            # Check for actual metrics
            if echo "$METRICS_OUTPUT" | grep -qE "^[a-zA-Z_][a-zA-Z0-9_]*"; then
                print_pass "Metrics data present"
            else
                print_fail "No metrics data found"
                return 1
            fi
        else
            print_fail "No data returned from metrics endpoint"
            return 1
        fi
    else
        print_fail "curl not available"
        return 1
    fi
}

################################################################################
# Test 3: Prometheus Scraping
################################################################################

test_prometheus_scraping() {
    print_header "TEST 3: Prometheus Scraping"
    run_test
    
    # Check if Prometheus is scraping the metrics endpoint
    PROMETHEUS_URL="http://localhost:9090"
    
    if command -v curl &> /dev/null; then
        # Check Prometheus targets
        TARGETS=$(curl -s "$PROMETHEUS_URL/api/v1/targets" 2>/dev/null)
        
        if [ -n "$TARGETS" ]; then
            print_pass "Prometheus targets API accessible"
            
            # Check if metrics endpoint (port 9091) is in targets
            if echo "$TARGETS" | grep -q "9091"; then
                print_pass "Metrics endpoint (9091) is a Prometheus target"
                
                # Check if target is up
                if echo "$TARGETS" | grep -q '"health":"up"'; then
                    print_pass "At least one target is up and being scraped"
                else
                    print_fail "No targets are up"
                fi
            else
                print_fail "Metrics endpoint not configured as Prometheus target"
                echo "  Note: Add metrics endpoint to prometheus.yml"
            fi
        else
            print_fail "Cannot reach Prometheus API"
            echo "  Note: Ensure Prometheus is running (http://localhost:9090)"
        fi
    else
        print_fail "curl not available"
        return 1
    fi
}

################################################################################
# Test 4: Metrics Service Files
################################################################################

test_metrics_service_files() {
    print_header "TEST 4: Metrics Service Files"
    run_test
    
    SERVICE_FILES=(
        "$PROJECT_ROOT/app/api/metrics.py"
        "$PROJECT_ROOT/business/services/observability/prometheus_metrics.py"
    )
    
    ALL_FOUND=true
    for service_file in "${SERVICE_FILES[@]}"; do
        if [ -f "$service_file" ]; then
            print_pass "$(basename $service_file) exists"
        else
            print_fail "Missing: $service_file"
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
    print_header "ACHIEVEMENT 1.2 VALIDATION"
    echo ""
    echo "Testing: Metrics Endpoint Validated"
    echo ""
    
    test_metrics_endpoint
    echo ""
    test_prometheus_format
    echo ""
    test_prometheus_scraping
    echo ""
    test_metrics_service_files
    echo ""
    
    # Summary
    print_header "SUMMARY"
    echo "Tests Run: $TESTS_RUN"
    echo "Passed: $TESTS_PASSED ✅"
    echo "Failed: $TESTS_FAILED ❌"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✅ ACHIEVEMENT 1.2: VALIDATED${NC}"
        echo ""
        echo "Metrics endpoint is working and Prometheus is scraping!"
        exit 0
    else
        echo -e "${RED}❌ ACHIEVEMENT 1.2: NEEDS FIXES${NC}"
        exit 1
    fi
}

main "$@"

