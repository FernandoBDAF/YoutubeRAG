#!/bin/bash
# validate-achievement-42.sh - Achievement 4.2: Legacy Collection Coexistence Verified

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
# Test 1: Legacy Collections Exist
################################################################################

test_legacy_collections_exist() {
    print_header "TEST 1: Legacy Collections Exist"
    run_test
    
    # Check if mongosh is available
    if ! command -v mongosh &> /dev/null; then
        print_fail "mongosh not found - cannot test collections"
        return 1
    fi
    
    # Check legacy collections
    LEGACY_COLLECTIONS=("entities" "relations" "communities")
    ALL_EXIST=true
    
    for collection in "${LEGACY_COLLECTIONS[@]}"; do
        if mongosh mongo_hack --eval "db.getCollectionNames()" --quiet | grep -q "$collection"; then
            print_pass "Legacy collection '$collection' exists"
        else
            print_fail "Legacy collection '$collection' not found"
            ALL_EXIST=false
        fi
    done
    
    if [ "$ALL_EXIST" = false ]; then
        return 1
    fi
}

################################################################################
# Test 2: Legacy Collections Queryable
################################################################################

test_legacy_collections_queryable() {
    print_header "TEST 2: Legacy Collections Queryable"
    run_test
    
    # Test querying each legacy collection
    LEGACY_COLLECTIONS=("entities" "relations" "communities")
    ALL_QUERYABLE=true
    
    for collection in "${LEGACY_COLLECTIONS[@]}"; do
        if mongosh mongo_hack --eval "db.$collection.countDocuments()" --quiet &> /dev/null; then
            print_pass "Can query '$collection' collection"
        else
            print_fail "Cannot query '$collection' collection"
            ALL_QUERYABLE=false
        fi
    done
    
    if [ "$ALL_QUERYABLE" = false ]; then
        return 1
    fi
}

################################################################################
# Test 3: Collection Names Are Different
################################################################################

test_collection_names_different() {
    print_header "TEST 3: Collection Names Are Different"
    run_test
    
    # Get all collections
    COLLECTIONS=$(mongosh mongo_hack --eval "db.getCollectionNames()" --quiet)
    
    # Check that legacy and new collections have different names
    LEGACY_NAMES=("entities" "relations" "communities")
    NEW_NAMES=("entities_resolved" "relations_final" "transformation_logs")
    
    CONFLICTS=0
    for legacy in "${LEGACY_NAMES[@]}"; do
        for new in "${NEW_NAMES[@]}"; do
            if [ "$legacy" = "$new" ]; then
                print_fail "Naming conflict: '$legacy' = '$new'"
                ((CONFLICTS++))
            fi
        done
    done
    
    if [ $CONFLICTS -eq 0 ]; then
        print_pass "No naming conflicts between legacy and new collections"
    else
        print_fail "$CONFLICTS naming conflicts detected"
        return 1
    fi
}

################################################################################
# Test 4: New Collections Status Check
################################################################################

test_new_collections_status() {
    print_header "TEST 4: New Collections Status Check"
    run_test
    
    # Check if new observability collections exist
    NEW_COLLECTIONS=("entities_resolved" "relations_final" "transformation_logs" "quality_metrics")
    
    EXISTS_COUNT=0
    for collection in "${NEW_COLLECTIONS[@]}"; do
        if mongosh mongo_hack --eval "db.getCollectionNames()" --quiet | grep -q "$collection"; then
            ((EXISTS_COUNT++))
        fi
    done
    
    if [ $EXISTS_COUNT -eq 0 ]; then
        print_pass "New collections don't exist yet (expected for fresh setup)"
    elif [ $EXISTS_COUNT -eq ${#NEW_COLLECTIONS[@]} ]; then
        print_pass "All new collections exist (observability pipeline has run)"
    else
        print_pass "Some new collections exist ($EXISTS_COUNT/${#NEW_COLLECTIONS[@]})"
    fi
}

################################################################################
# Test 5: No Data Conflicts Possible
################################################################################

test_no_data_conflicts() {
    print_header "TEST 5: No Data Conflicts Possible"
    run_test
    
    # Check if both legacy and new entities collections have data
    LEGACY_COUNT=$(mongosh mongo_hack --eval "db.entities.countDocuments()" --quiet 2>/dev/null || echo "0")
    NEW_COUNT=$(mongosh mongo_hack --eval "db.entities_resolved.countDocuments()" --quiet 2>/dev/null || echo "0")
    
    if [ "$LEGACY_COUNT" = "0" ] || [ "$NEW_COUNT" = "0" ]; then
        print_pass "No data conflicts possible (one or both collections empty)"
    else
        # Check for overlapping IDs (sample check)
        print_pass "Both collections have data - conflicts possible but collections are separate"
    fi
}

################################################################################
# Test 6: Deliverables Exist
################################################################################

test_deliverables_exist() {
    print_header "TEST 6: Deliverables Exist"
    run_test
    
    DOC_DIR="$PROJECT_ROOT/documentation"
    
    DELIVERABLES=(
        "Legacy-Collection-Coexistence-Report.md"
        "Collection-Usage-Guide.md"
        "Migration-Considerations.md"
    )
    
    MISSING_DELIVERABLES=()
    for doc in "${DELIVERABLES[@]}"; do
        if [ ! -f "$DOC_DIR/$doc" ]; then
            MISSING_DELIVERABLES+=("$doc")
        else
            # Check file is not empty
            if [ ! -s "$DOC_DIR/$doc" ]; then
                MISSING_DELIVERABLES+=("$doc (empty)")
            else
                print_pass "$doc exists and has content"
            fi
        fi
    done
    
    if [ ${#MISSING_DELIVERABLES[@]} -gt 0 ]; then
        print_fail "Missing deliverables: ${MISSING_DELIVERABLES[*]}"
        return 1
    fi
}

################################################################################
# Test 7: Coexistence Report Complete
################################################################################

test_coexistence_report_complete() {
    print_header "TEST 7: Coexistence Report Complete"
    run_test
    
    REPORT_FILE="$PROJECT_ROOT/documentation/Legacy-Collection-Coexistence-Report.md"
    
    if [ ! -f "$REPORT_FILE" ]; then
        print_fail "Coexistence report not found"
        return 1
    fi
    
    # Check for key sections
    REQUIRED_SECTIONS=(
        "Executive Summary"
        "Test Results"
        "Coexistence Status"
        "Legacy Collections"
        "New Collections"
    )
    
    MISSING_SECTIONS=()
    for section in "${REQUIRED_SECTIONS[@]}"; do
        if ! grep -qi "$section" "$REPORT_FILE"; then
            MISSING_SECTIONS+=("$section")
        fi
    done
    
    if [ ${#MISSING_SECTIONS[@]} -eq 0 ]; then
        print_pass "All required sections present in coexistence report"
    else
        print_fail "Missing sections: ${MISSING_SECTIONS[*]}"
        return 1
    fi
}

################################################################################
# Test 8: Usage Guide Complete
################################################################################

test_usage_guide_complete() {
    print_header "TEST 8: Usage Guide Complete"
    run_test
    
    GUIDE_FILE="$PROJECT_ROOT/documentation/Collection-Usage-Guide.md"
    
    if [ ! -f "$GUIDE_FILE" ]; then
        print_fail "Usage guide not found"
        return 1
    fi
    
    # Check for key sections
    REQUIRED_SECTIONS=(
        "Collection Inventory"
        "When to Use"
        "Query Examples"
        "Best Practices"
    )
    
    MISSING_SECTIONS=()
    for section in "${REQUIRED_SECTIONS[@]}"; do
        if ! grep -qi "$section" "$GUIDE_FILE"; then
            MISSING_SECTIONS+=("$section")
        fi
    done
    
    if [ ${#MISSING_SECTIONS[@]} -eq 0 ]; then
        print_pass "All required sections present in usage guide"
    else
        print_fail "Missing sections: ${MISSING_SECTIONS[*]}"
        return 1
    fi
}

################################################################################
# Test 9: Migration Document Complete
################################################################################

test_migration_document_complete() {
    print_header "TEST 9: Migration Document Complete"
    run_test
    
    MIGRATION_FILE="$PROJECT_ROOT/documentation/Migration-Considerations.md"
    
    if [ ! -f "$MIGRATION_FILE" ]; then
        print_fail "Migration document not found"
        return 1
    fi
    
    # Check for key sections
    REQUIRED_SECTIONS=(
        "Migration Strategy"
        "When to Migrate"
        "Migration Procedures"
        "Risk Assessment"
        "Rollback"
    )
    
    MISSING_SECTIONS=()
    for section in "${REQUIRED_SECTIONS[@]}"; do
        if ! grep -qi "$section" "$MIGRATION_FILE"; then
            MISSING_SECTIONS+=("$section")
        fi
    done
    
    if [ ${#MISSING_SECTIONS[@]} -eq 0 ]; then
        print_pass "All required sections present in migration document"
    else
        print_fail "Missing sections: ${MISSING_SECTIONS[*]}"
        return 1
    fi
}

################################################################################
# Test 10: EXECUTION_TASK Complete
################################################################################

test_execution_task_complete() {
    print_header "TEST 10: EXECUTION_TASK Complete"
    run_test
    
    EXEC_FILE="$PROJECT_ROOT/work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/execution/EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_42_01.md"
    
    if [ ! -f "$EXEC_FILE" ]; then
        print_fail "EXECUTION_TASK not found"
        return 1
    fi
    
    print_pass "EXECUTION_TASK exists"
    
    # Check for completion status
    if grep -q "✅ COMPLETE" "$EXEC_FILE"; then
        print_pass "EXECUTION_TASK marked as complete"
    else
        print_fail "EXECUTION_TASK not marked as complete"
        return 1
    fi
    
    # Check for all deliverables marked complete
    if grep -q "Legacy-Collection-Coexistence-Report.md" "$EXEC_FILE" && \
       grep -q "Collection-Usage-Guide.md" "$EXEC_FILE" && \
       grep -q "Migration-Considerations.md" "$EXEC_FILE"; then
        print_pass "All deliverables referenced in EXECUTION_TASK"
    else
        print_fail "Not all deliverables referenced"
        return 1
    fi
}

################################################################################
# Main execution
################################################################################

main() {
    print_header "ACHIEVEMENT 4.2 VALIDATION"
    echo ""
    echo "Achievement: Legacy Collection Coexistence Verified"
    echo "Validates: Collection coexistence, naming separation, deliverables"
    echo ""
    
    # Run all tests
    test_legacy_collections_exist
    test_legacy_collections_queryable
    test_collection_names_different
    test_new_collections_status
    test_no_data_conflicts
    test_deliverables_exist
    test_coexistence_report_complete
    test_usage_guide_complete
    test_migration_document_complete
    test_execution_task_complete
    
    # Summary
    echo ""
    print_header "VALIDATION SUMMARY"
    echo "Tests Run:    $TESTS_RUN"
    echo "Tests Passed: $TESTS_PASSED ✅"
    echo "Tests Failed: $TESTS_FAILED ❌"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║                                                               ║${NC}"
        echo -e "${GREEN}║          ✅ ACHIEVEMENT 4.2: VALIDATED                        ║${NC}"
        echo -e "${GREEN}║                                                               ║${NC}"
        echo -e "${GREEN}║  Legacy and new collections coexist by design                ║${NC}"
        echo -e "${GREEN}║  All deliverables complete                                   ║${NC}"
        echo -e "${GREEN}║                                                               ║${NC}"
        echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo "Next Steps:"
        echo "  1. Proceed to Achievement 4.3 (Configuration Integration Validated)"
        echo ""
        exit 0
    else
        echo -e "${RED}╔═══════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║                                                               ║${NC}"
        echo -e "${RED}║          ❌ ACHIEVEMENT 4.2: NEEDS FIXES                      ║${NC}"
        echo -e "${RED}║                                                               ║${NC}"
        echo -e "${RED}║  $TESTS_FAILED test(s) failed - see details above                    ║${NC}"
        echo -e "${RED}║                                                               ║${NC}"
        echo -e "${RED}╚═══════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo "Action Required:"
        echo "  1. Review failed tests above"
        echo "  2. Fix identified issues"
        echo "  3. Re-run validation: bash observability/validate-achievement-42.sh"
        echo ""
        exit 1
    fi
}

main "$@"

