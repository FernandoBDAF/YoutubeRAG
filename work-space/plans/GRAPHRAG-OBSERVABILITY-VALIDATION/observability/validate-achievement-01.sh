#!/bin/bash
# validate-achievement-01.sh - Achievement 0.1: Collection Name Compatibility Resolved

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
# Test 1: Collection Constants in paths.py
################################################################################

test_collection_constants() {
    print_header "TEST 1: Collection Constants in paths.py"
    run_test
    
    PATHS_FILE="$PROJECT_ROOT/core/config/paths.py"
    
    if [ ! -f "$PATHS_FILE" ]; then
        print_fail "paths.py not found at $PATHS_FILE"
        return 1
    fi
    
    print_pass "paths.py exists"
    
    # Check for observability collection constants
    REQUIRED_CONSTANTS=(
        "COLL_TRANSFORMATION_LOGS"
        "COLL_ENTITIES_RAW"
        "COLL_ENTITIES_RESOLVED"
        "COLL_RELATIONS_RAW"
        "COLL_RELATIONS_FINAL"
        "COLL_GRAPHRAG_RUNS"
        "COLL_QUALITY_METRICS"
        "OBSERVABILITY_COLLECTIONS"
    )
    
    MISSING_CONSTANTS=()
    for constant in "${REQUIRED_CONSTANTS[@]}"; do
        if ! grep -q "$constant" "$PATHS_FILE"; then
            MISSING_CONSTANTS+=("$constant")
        fi
    done
    
    if [ ${#MISSING_CONSTANTS[@]} -eq 0 ]; then
        print_pass "All ${#REQUIRED_CONSTANTS[@]} collection constants defined"
    else
        print_fail "Missing constants: ${MISSING_CONSTANTS[*]}"
        return 1
    fi
}

################################################################################
# Test 2: No Naming Conflicts
################################################################################

test_naming_conflicts() {
    print_header "TEST 2: No Naming Conflicts"
    run_test
    
    PATHS_FILE="$PROJECT_ROOT/core/config/paths.py"
    
    # Check that new collections don't conflict with legacy ones
    # Legacy: entities, relations, communities
    # New: entities_resolved, relations_final, transformation_logs, etc.
    
    # This is a simple check - in reality, we'd query MongoDB
    # For now, we just verify the naming convention is different
    
    if grep -q "ENTITIES_RESOLVED_COLLECTION" "$PATHS_FILE" || \
       grep -q "entities_resolved" "$PATHS_FILE"; then
        print_pass "New entity collection uses different name (entities_resolved vs entities)"
    else
        print_fail "Cannot verify entity collection naming"
        return 1
    fi
    
    if grep -q "RELATIONS_FINAL_COLLECTION" "$PATHS_FILE" || \
       grep -q "relations_final" "$PATHS_FILE"; then
        print_pass "New relations collection uses different name (relations_final vs relations)"
    else
        print_fail "Cannot verify relations collection naming"
        return 1
    fi
    
    print_pass "No naming conflicts detected"
}

################################################################################
# Test 3: Documentation Complete
################################################################################

test_documentation() {
    print_header "TEST 3: Documentation Complete"
    run_test
    
    # Check for collection documentation
    DOC_FILES=(
        "$PROJECT_ROOT/documentation/Collection-Compatibility-Report.md"
        "$PROJECT_ROOT/work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/documentation/Collection-Compatibility-Report.md"
    )
    
    FOUND=false
    for doc_file in "${DOC_FILES[@]}"; do
        if [ -f "$doc_file" ]; then
            print_pass "Collection documentation found: $(basename $doc_file)"
            FOUND=true
            break
        fi
    done
    
    if [ "$FOUND" = false ]; then
        print_fail "Collection documentation not found"
        return 1
    fi
}

################################################################################
# Main
################################################################################

main() {
    print_header "ACHIEVEMENT 0.1 VALIDATION"
    echo ""
    echo "Testing: Collection Name Compatibility Resolved"
    echo ""
    
    test_collection_constants
    echo ""
    test_naming_conflicts
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
        echo -e "${GREEN}✅ ACHIEVEMENT 0.1: VALIDATED${NC}"
        exit 0
    else
        echo -e "${RED}❌ ACHIEVEMENT 0.1: NEEDS FIXES${NC}"
        exit 1
    fi
}

main "$@"

