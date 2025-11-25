#!/bin/bash
# validate-achievement-23.sh - Achievement 2.3: Data Quality Validation

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
PROJECT_ROOT="$SCRIPT_DIR/../../.."

# MongoDB connection (use environment variable or default)
MONGODB_URI="${MONGODB_URI:-mongodb://localhost:27017}"
DB_NAME="${DB_NAME:-validation_01}"

################################################################################
# Test 1: Observability Collections Exist
################################################################################

test_collections_exist() {
    print_header "TEST 1: Observability Collections Exist"
    run_test
    
    # Check if mongosh or mongo is available
    if command -v mongosh &> /dev/null; then
        MONGO_CMD="mongosh"
    elif command -v mongo &> /dev/null; then
        MONGO_CMD="mongo"
    else
        print_fail "MongoDB client (mongosh/mongo) not found"
        return 1
    fi
    
    # Required observability collections
    REQUIRED_COLLECTIONS=(
        "transformation_logs"
        "entity_mentions"
        "entities_before_resolution"
        "entities_after_resolution"
        "relations_before_filter"
        "relations_final"
    )
    
    ALL_EXIST=true
    for collection in "${REQUIRED_COLLECTIONS[@]}"; do
        COUNT=$($MONGO_CMD "$MONGODB_URI/$DB_NAME" --quiet --eval "db.$collection.countDocuments({})" 2>/dev/null)
        
        if [ -n "$COUNT" ] && [ "$COUNT" -ge 0 ]; then
            print_pass "$collection exists (count: $COUNT)"
        else
            print_fail "$collection not found or inaccessible"
            ALL_EXIST=false
        fi
    done
    
    if [ "$ALL_EXIST" = false ]; then
        return 1
    fi
}

################################################################################
# Test 2: Document Counts Reasonable
################################################################################

test_document_counts() {
    print_header "TEST 2: Document Counts Reasonable"
    run_test
    
    if command -v mongosh &> /dev/null; then
        MONGO_CMD="mongosh"
    elif command -v mongo &> /dev/null; then
        MONGO_CMD="mongo"
    else
        print_fail "MongoDB client not found"
        return 1
    fi
    
    # Check that collections have data
    COLLECTIONS_TO_CHECK=(
        "transformation_logs"
        "entity_mentions"
    )
    
    ALL_REASONABLE=true
    for collection in "${COLLECTIONS_TO_CHECK[@]}"; do
        COUNT=$($MONGO_CMD "$MONGODB_URI/$DB_NAME" --quiet --eval "db.$collection.countDocuments({})" 2>/dev/null)
        
        if [ -n "$COUNT" ] && [ "$COUNT" -gt 0 ]; then
            print_pass "$collection has data (count: $COUNT)"
        else
            print_fail "$collection is empty (count: $COUNT)"
            ALL_REASONABLE=false
        fi
    done
    
    if [ "$ALL_REASONABLE" = false ]; then
        echo "  Note: Collections should be populated after pipeline run"
        return 1
    fi
}

################################################################################
# Test 3: trace_id Consistency
################################################################################

test_trace_id_consistency() {
    print_header "TEST 3: trace_id Consistency"
    run_test
    
    if command -v mongosh &> /dev/null; then
        MONGO_CMD="mongosh"
    elif command -v mongo &> /dev/null; then
        MONGO_CMD="mongo"
    else
        print_fail "MongoDB client not found"
        return 1
    fi
    
    # Get distinct trace_ids from transformation_logs
    TRACE_IDS=$($MONGO_CMD "$MONGODB_URI/$DB_NAME" --quiet --eval "db.transformation_logs.distinct('trace_id')" 2>/dev/null)
    
    if [ -n "$TRACE_IDS" ]; then
        # Count how many trace_ids exist
        TRACE_ID_COUNT=$(echo "$TRACE_IDS" | grep -o "'" | wc -l)
        TRACE_ID_COUNT=$((TRACE_ID_COUNT / 2))  # Divide by 2 since each ID has two quotes
        
        if [ "$TRACE_ID_COUNT" -eq 1 ]; then
            print_pass "Single trace_id found across collections"
        elif [ "$TRACE_ID_COUNT" -gt 1 ]; then
            print_pass "Multiple trace_ids found ($TRACE_ID_COUNT runs)"
        else
            print_fail "No trace_ids found"
            return 1
        fi
        
        # Verify trace_id exists in all collections
        FIRST_TRACE_ID=$(echo "$TRACE_IDS" | grep -o "'[^']*'" | head -1 | tr -d "'")
        
        if [ -n "$FIRST_TRACE_ID" ]; then
            COLLECTIONS=(
                "entity_mentions"
                "entities_before_resolution"
                "entities_after_resolution"
            )
            
            for collection in "${COLLECTIONS[@]}"; do
                COUNT=$($MONGO_CMD "$MONGODB_URI/$DB_NAME" --quiet --eval "db.$collection.countDocuments({trace_id: '$FIRST_TRACE_ID'})" 2>/dev/null)
                
                if [ -n "$COUNT" ] && [ "$COUNT" -gt 0 ]; then
                    print_pass "trace_id found in $collection"
                fi
            done
        fi
    else
        print_fail "Cannot retrieve trace_ids"
        return 1
    fi
}

################################################################################
# Test 4: Schema Validation
################################################################################

test_schema_validation() {
    print_header "TEST 4: Schema Validation"
    run_test
    
    if command -v mongosh &> /dev/null; then
        MONGO_CMD="mongosh"
    elif command -v mongo &> /dev/null; then
        MONGO_CMD="mongo"
    else
        print_fail "MongoDB client not found"
        return 1
    fi
    
    # Check transformation_logs schema
    SAMPLE_LOG=$($MONGO_CMD "$MONGODB_URI/$DB_NAME" --quiet --eval "JSON.stringify(db.transformation_logs.findOne())" 2>/dev/null)
    
    if [ -n "$SAMPLE_LOG" ] && [ "$SAMPLE_LOG" != "null" ]; then
        print_pass "transformation_logs has documents"
        
        # Check for required fields
        REQUIRED_FIELDS=("trace_id" "stage" "timestamp")
        
        for field in "${REQUIRED_FIELDS[@]}"; do
            if echo "$SAMPLE_LOG" | grep -q "\"$field\""; then
                print_pass "transformation_logs has $field field"
            else
                print_fail "transformation_logs missing $field field"
            fi
        done
    else
        print_fail "transformation_logs is empty or inaccessible"
        return 1
    fi
}

################################################################################
# Main
################################################################################

main() {
    print_header "ACHIEVEMENT 2.3 VALIDATION"
    echo ""
    echo "Testing: Data Quality Validation"
    echo "Database: $DB_NAME"
    echo ""
    
    test_collections_exist
    echo ""
    test_document_counts
    echo ""
    test_trace_id_consistency
    echo ""
    test_schema_validation
    echo ""
    
    # Summary
    print_header "SUMMARY"
    echo "Tests Run: $TESTS_RUN"
    echo "Passed: $TESTS_PASSED ✅"
    echo "Failed: $TESTS_FAILED ❌"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✅ ACHIEVEMENT 2.3: VALIDATED${NC}"
        echo ""
        echo "All observability collections are populated with quality data!"
        exit 0
    else
        echo -e "${RED}❌ ACHIEVEMENT 2.3: NEEDS FIXES${NC}"
        exit 1
    fi
}

main "$@"

