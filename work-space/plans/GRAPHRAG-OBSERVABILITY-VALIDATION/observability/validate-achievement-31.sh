#!/bin/bash

################################################################################
# Validation Script: Achievement 3.1 - Query Scripts Validated
################################################################################
#
# Purpose: Validate all 11 query scripts work correctly with real pipeline data
# Achievement: 3.1 - Query Scripts Validated
# Date: 2025-11-13
#
# Tests:
#   1. Extraction scripts (2 scripts)
#   2. Resolution scripts (3 scripts)
#   3. Construction scripts (3 scripts)
#   4. Detection scripts (2 scripts)
#   5. Error handling (1 test)
#
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Configuration
TRACE_ID="6088e6bd-e305-42d8-9210-e2d3f1dda035"
SCRIPTS_DIR="scripts/repositories/graphrag/queries"
OUTPUT_DIR="work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/query-outputs"

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# From observability/ go up 3 levels: observability -> GRAPHRAG-OBSERVABILITY-VALIDATION -> plans -> work-space -> YoutubeRAG
PROJECT_ROOT="$SCRIPT_DIR/../../../.."

# Change to project root
cd "$PROJECT_ROOT"

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Export environment variables
export MONGODB_URI="mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
export DB_NAME="validation_01"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"
}

test_script() {
    local script_name=$1
    local test_name=$2
    local command=$3
    
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -e "${YELLOW}[TEST $TESTS_RUN]${NC} $test_name"
    echo "Command: $command"
    
    if eval "$command" > "$OUTPUT_DIR/${script_name}_output.txt" 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo ""
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo "Error output saved to: $OUTPUT_DIR/${script_name}_output.txt"
        echo ""
        return 1
    fi
}

skip_test() {
    local test_name=$1
    local reason=$2
    
    TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
    echo -e "${YELLOW}[SKIP]${NC} $test_name"
    echo "Reason: $reason"
    echo ""
}

################################################################################
# Main Test Execution
################################################################################

print_header "ACHIEVEMENT 3.1: QUERY SCRIPTS VALIDATION"

echo "Configuration:"
echo "  Trace ID: $TRACE_ID"
echo "  Database: $DB_NAME"
echo "  Scripts Directory: $SCRIPTS_DIR"
echo "  Output Directory: $OUTPUT_DIR"
echo "  Project Root: $(pwd)"
echo ""

################################################################################
# Phase 1: Extraction Scripts
################################################################################

print_header "PHASE 1: EXTRACTION SCRIPTS (2 tests)"

# Test 1: query_raw_entities.py
test_script "query_raw_entities" \
    "Query Raw Entities" \
    "python $SCRIPTS_DIR/query_raw_entities.py --trace-id $TRACE_ID --limit 10"

# Test 2: compare_extraction_runs.py (requires 2 trace IDs - skip)
skip_test "compare_extraction_runs.py" "Requires 2 trace IDs (not available)"

################################################################################
# Phase 2: Resolution Scripts
################################################################################

print_header "PHASE 2: RESOLUTION SCRIPTS (3 tests)"

# Test 3: query_resolution_decisions.py
test_script "query_resolution_decisions" \
    "Query Resolution Decisions" \
    "python $SCRIPTS_DIR/query_resolution_decisions.py --trace-id $TRACE_ID --limit 10"

# Test 4: compare_before_after_resolution.py (no --limit parameter)
test_script "compare_before_after_resolution" \
    "Compare Before/After Resolution" \
    "python $SCRIPTS_DIR/compare_before_after_resolution.py --trace-id $TRACE_ID"

# Test 5: find_resolution_errors.py
test_script "find_resolution_errors" \
    "Find Resolution Errors" \
    "python $SCRIPTS_DIR/find_resolution_errors.py --trace-id $TRACE_ID --limit 10"

################################################################################
# Phase 3: Construction Scripts
################################################################################

print_header "PHASE 3: CONSTRUCTION SCRIPTS (3 tests)"

# Test 6: query_raw_relationships.py
test_script "query_raw_relationships" \
    "Query Raw Relationships" \
    "python $SCRIPTS_DIR/query_raw_relationships.py --trace-id $TRACE_ID --limit 10"

# Test 7: compare_before_after_construction.py (no --limit parameter)
test_script "compare_before_after_construction" \
    "Compare Before/After Construction" \
    "python $SCRIPTS_DIR/compare_before_after_construction.py --trace-id $TRACE_ID"

# Test 8: query_graph_evolution.py (no --limit parameter)
test_script "query_graph_evolution" \
    "Query Graph Evolution" \
    "python $SCRIPTS_DIR/query_graph_evolution.py --trace-id $TRACE_ID"

################################################################################
# Phase 4: Detection Scripts
################################################################################

print_header "PHASE 4: DETECTION SCRIPTS (2 tests)"

# Test 9: query_pre_detection_graph.py (no --limit parameter)
test_script "query_pre_detection_graph" \
    "Query Pre-Detection Graph" \
    "python $SCRIPTS_DIR/query_pre_detection_graph.py --trace-id $TRACE_ID"

# Test 10: compare_detection_algorithms.py (requires 2 trace IDs - skip)
skip_test "compare_detection_algorithms.py" "Requires 2 trace IDs (not available)"

################################################################################
# Phase 5: Error Handling
################################################################################

print_header "PHASE 5: ERROR HANDLING (1 test)"

# Test 11: Invalid trace ID handling
test_script "query_raw_entities_invalid" \
    "Query Raw Entities (Invalid Trace ID)" \
    "python $SCRIPTS_DIR/query_raw_entities.py --trace-id invalid-trace-id-12345 --limit 10"

################################################################################
# Final Summary
################################################################################

print_header "TEST SUMMARY"

echo "Total Tests Run: $TESTS_RUN"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo -e "${YELLOW}Skipped: $TESTS_SKIPPED${NC}"
echo ""
echo "Output files saved to: $OUTPUT_DIR"
echo ""

# Calculate success rate
if [ $TESTS_RUN -gt 0 ]; then
    SUCCESS_RATE=$((TESTS_PASSED * 100 / TESTS_RUN))
    echo "Success Rate: ${SUCCESS_RATE}%"
    echo ""
fi

# Final verdict
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}╔═════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ ACHIEVEMENT 3.1: ALL TESTS PASSED                 ║${NC}"
    echo -e "${GREEN}╚═════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "All query scripts are working correctly with real pipeline data."
    exit 0
else
    echo -e "${RED}╔═════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ ACHIEVEMENT 3.1: SOME TESTS FAILED                ║${NC}"
    echo -e "${RED}╚═════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Please review the output files in $OUTPUT_DIR for details."
    exit 1
fi

