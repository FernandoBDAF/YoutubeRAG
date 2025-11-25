#!/bin/bash
# validate-achievement-02.sh - Achievement 0.2: Configuration Compatibility Verified

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

# Get project root (4 levels up from observability/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../../../.."

################################################################################
# Test 1: trace_id Support in Config Files
################################################################################

test_trace_id_support() {
    print_header "TEST 1: trace_id Support in Config Files"
    run_test
    
    CONFIG_FILES=(
        "$PROJECT_ROOT/core/config/graphrag.py"
        "$PROJECT_ROOT/core/base/stage.py"
        "$PROJECT_ROOT/core/base/agent.py"
    )
    
    ALL_FOUND=true
    for config_file in "${CONFIG_FILES[@]}"; do
        if [ ! -f "$config_file" ]; then
            print_fail "Config file not found: $(basename $config_file)"
            ALL_FOUND=false
            continue
        fi
        
        if grep -q "trace_id" "$config_file"; then
            print_pass "$(basename $config_file) has trace_id support"
        else
            print_fail "$(basename $config_file) missing trace_id support"
            ALL_FOUND=false
        fi
    done
    
    if [ "$ALL_FOUND" = false ]; then
        return 1
    fi
}

################################################################################
# Test 2: BaseStageConfig Compatibility
################################################################################

test_base_stage_config() {
    print_header "TEST 2: BaseStageConfig Compatibility"
    run_test
    
    STAGE_FILE="$PROJECT_ROOT/core/base/stage.py"
    
    if [ ! -f "$STAGE_FILE" ]; then
        print_fail "stage.py not found"
        return 1
    fi
    
    # Check for BaseStageConfig class
    if grep -q "class BaseStageConfig" "$STAGE_FILE" || \
       grep -q "class.*StageConfig" "$STAGE_FILE"; then
        print_pass "BaseStageConfig class found"
    else
        print_fail "BaseStageConfig class not found"
        return 1
    fi
    
    # Check for trace_id in config
    if grep -q "trace_id" "$STAGE_FILE"; then
        print_pass "trace_id support in BaseStageConfig"
    else
        print_fail "trace_id not found in BaseStageConfig"
        return 1
    fi
}

################################################################################
# Test 3: BaseAgentConfig Compatibility
################################################################################

test_base_agent_config() {
    print_header "TEST 3: BaseAgentConfig Compatibility"
    run_test
    
    AGENT_FILE="$PROJECT_ROOT/core/base/agent.py"
    
    if [ ! -f "$AGENT_FILE" ]; then
        print_fail "agent.py not found"
        return 1
    fi
    
    # Check for BaseAgentConfig class
    if grep -q "class BaseAgentConfig" "$AGENT_FILE" || \
       grep -q "class.*AgentConfig" "$AGENT_FILE"; then
        print_pass "BaseAgentConfig class found"
    else
        print_fail "BaseAgentConfig class not found"
        return 1
    fi
    
    # Check for trace_id in config
    if grep -q "trace_id" "$AGENT_FILE"; then
        print_pass "trace_id support in BaseAgentConfig"
    else
        print_fail "trace_id not found in BaseAgentConfig"
        return 1
    fi
}

################################################################################
# Test 4: Configuration Documentation
################################################################################

test_documentation() {
    print_header "TEST 4: Configuration Documentation"
    run_test
    
    DOC_FILES=(
        "$PROJECT_ROOT/documentation/Configuration-Compatibility-Report.md"
        "$PROJECT_ROOT/work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/documentation/Configuration-Compatibility-Report.md"
    )
    
    FOUND=false
    for doc_file in "${DOC_FILES[@]}"; do
        if [ -f "$doc_file" ]; then
            print_pass "Configuration documentation found: $(basename $doc_file)"
            FOUND=true
            break
        fi
    done
    
    if [ "$FOUND" = false ]; then
        print_fail "Configuration documentation not found"
        return 1
    fi
}

################################################################################
# Main
################################################################################

main() {
    print_header "ACHIEVEMENT 0.2 VALIDATION"
    echo ""
    echo "Testing: Configuration Compatibility Verified"
    echo ""
    
    test_trace_id_support
    echo ""
    test_base_stage_config
    echo ""
    test_base_agent_config
    echo ""
    test_documentation
    echo ""
    
    # Summary
    print_header "SUMMARY"
    echo "Tests Run: $TESTS_RUN"
    echo "Passed: $TESTS_PASSED ✅"
    echo "Failed: $TESTS_FAILED ❌"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✅ ACHIEVEMENT 0.2: VALIDATED${NC}"
        exit 0
    else
        echo -e "${RED}❌ ACHIEVEMENT 0.2: NEEDS FIXES${NC}"
        exit 1
    fi
}

main "$@"

