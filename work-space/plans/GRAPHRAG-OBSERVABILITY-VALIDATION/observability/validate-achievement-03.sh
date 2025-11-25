#!/bin/bash
# validate-achievement-03.sh - Achievement 0.3: Environment Variables Configured

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
# Test 1: Required Environment Variables
################################################################################

test_required_env_vars() {
    print_header "TEST 1: Required Environment Variables"
    run_test
    
    # Check for observability environment variables
    REQUIRED_VARS=(
        "GRAPHRAG_TRANSFORMATION_LOGGING"
        "GRAPHRAG_SAVE_INTERMEDIATE_DATA"
        "GRAPHRAG_QUALITY_METRICS"
    )
    
    MISSING_VARS=()
    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var}" ]; then
            # Variable not set, check if it's in .env file
            if [ -f "$PROJECT_ROOT/.env" ] && grep -q "^$var=" "$PROJECT_ROOT/.env"; then
                print_pass "$var defined in .env"
            else
                MISSING_VARS+=("$var")
            fi
        else
            print_pass "$var is set: ${!var}"
        fi
    done
    
    if [ ${#MISSING_VARS[@]} -gt 0 ]; then
        print_fail "Missing variables: ${MISSING_VARS[*]}"
        echo "  Note: Variables can be in .env file or exported"
        return 1
    fi
}

################################################################################
# Test 2: .env.observability Template
################################################################################

test_env_template() {
    print_header "TEST 2: .env.observability Template"
    run_test
    
    TEMPLATE_LOCATIONS=(
        "$PROJECT_ROOT/.env.observability"
        "$PROJECT_ROOT/.env.observability.template"
        "$PROJECT_ROOT/work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/.env.observability"
    )
    
    FOUND=false
    for template in "${TEMPLATE_LOCATIONS[@]}"; do
        if [ -f "$template" ]; then
            print_pass ".env.observability template found: $(basename $template)"
            FOUND=true
            
            # Check if template has required variables
            REQUIRED_IN_TEMPLATE=(
                "GRAPHRAG_TRANSFORMATION_LOGGING"
                "GRAPHRAG_SAVE_INTERMEDIATE_DATA"
                "GRAPHRAG_QUALITY_METRICS"
            )
            
            ALL_IN_TEMPLATE=true
            for var in "${REQUIRED_IN_TEMPLATE[@]}"; do
                if ! grep -q "$var" "$template"; then
                    print_fail "$var not in template"
                    ALL_IN_TEMPLATE=false
                fi
            done
            
            if [ "$ALL_IN_TEMPLATE" = true ]; then
                print_pass "All required variables in template"
            fi
            break
        fi
    done
    
    if [ "$FOUND" = false ]; then
        print_fail ".env.observability template not found"
        return 1
    fi
}

################################################################################
# Test 3: Variable Documentation
################################################################################

test_documentation() {
    print_header "TEST 3: Variable Documentation"
    run_test
    
    DOC_FILES=(
        "$PROJECT_ROOT/documentation/Environment-Variables-Guide.md"
        "$PROJECT_ROOT/work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/documentation/Environment-Variables-Guide.md"
        "$PROJECT_ROOT/README.md"
    )
    
    FOUND=false
    for doc_file in "${DOC_FILES[@]}"; do
        if [ -f "$doc_file" ]; then
            # Check if documentation mentions observability variables
            if grep -q "GRAPHRAG_TRANSFORMATION_LOGGING\|GRAPHRAG_SAVE_INTERMEDIATE_DATA\|GRAPHRAG_QUALITY_METRICS" "$doc_file"; then
                print_pass "Variable documentation found in $(basename $doc_file)"
                FOUND=true
                break
            fi
        fi
    done
    
    if [ "$FOUND" = false ]; then
        print_fail "Variable documentation not found or incomplete"
        echo "  Note: Documentation should explain observability environment variables"
        return 1
    fi
}

################################################################################
# Test 4: Variable Values Validation
################################################################################

test_variable_values() {
    print_header "TEST 4: Variable Values Validation"
    run_test
    
    # Check if variables have valid values (true/false)
    BOOLEAN_VARS=(
        "GRAPHRAG_TRANSFORMATION_LOGGING"
        "GRAPHRAG_SAVE_INTERMEDIATE_DATA"
        "GRAPHRAG_QUALITY_METRICS"
    )
    
    ALL_VALID=true
    for var in "${BOOLEAN_VARS[@]}"; do
        value="${!var}"
        if [ -z "$value" ]; then
            # Check .env file
            if [ -f "$PROJECT_ROOT/.env" ]; then
                value=$(grep "^$var=" "$PROJECT_ROOT/.env" | cut -d'=' -f2)
            fi
        fi
        
        if [ -n "$value" ]; then
            if [[ "$value" =~ ^(true|false|True|False|TRUE|FALSE|1|0)$ ]]; then
                print_pass "$var has valid boolean value: $value"
            else
                print_fail "$var has invalid value: $value (should be true/false)"
                ALL_VALID=false
            fi
        fi
    done
    
    if [ "$ALL_VALID" = false ]; then
        return 1
    fi
}

################################################################################
# Main
################################################################################

main() {
    print_header "ACHIEVEMENT 0.3 VALIDATION"
    echo ""
    echo "Testing: Environment Variables Configured"
    echo ""
    
    test_required_env_vars
    echo ""
    test_env_template
    echo ""
    test_documentation
    echo ""
    test_variable_values
    echo ""
    
    # Summary
    print_header "SUMMARY"
    echo "Tests Run: $TESTS_RUN"
    echo "Passed: $TESTS_PASSED ✅"
    echo "Failed: $TESTS_FAILED ❌"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✅ ACHIEVEMENT 0.3: VALIDATED${NC}"
        exit 0
    else
        echo -e "${RED}❌ ACHIEVEMENT 0.3: NEEDS FIXES${NC}"
        exit 1
    fi
}

main "$@"

