#!/bin/bash
###############################################################################
# Achievement 7.1 Validation Script
# 
# Validates that all tool enhancements from Achievement 7.1 are implemented
# and working correctly.
#
# Tests:
# 1. Code enhancements exist (grep for class/function definitions)
# 2. Test suite exists and passes
# 3. Tool-Enhancement-Report.md exists
# 4. Documentation updated (README files)
#
# Exit Codes:
#   0 - All checks passed
#   1 - One or more checks failed
###############################################################################

# Don't exit on error - we want to run all checks
set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "═══════════════════════════════════════════════════════════════════════"
echo "  Achievement 7.1 Validation: Tool Enhancements"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED_CHECKS++))
    ((TOTAL_CHECKS++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED_CHECKS++))
    ((TOTAL_CHECKS++))
}

section_header() {
    echo ""
    echo -e "${BLUE}━━━ $1 ━━━${NC}"
}

###############################################################################
# Test 1: Code Enhancements Exist
###############################################################################

section_header "Test 1: Code Enhancements Verification"

QUERY_UTILS="$PROJECT_ROOT/scripts/repositories/graphrag/queries/query_utils.py"

# Check Colors class
if grep -q "class Colors:" "$QUERY_UTILS"; then
    check_pass "Colors class defined in query_utils.py"
else
    check_fail "Colors class NOT found in query_utils.py"
fi

# Check QueryCache class
if grep -q "class QueryCache:" "$QUERY_UTILS"; then
    check_pass "QueryCache class defined in query_utils.py"
else
    check_fail "QueryCache class NOT found in query_utils.py"
fi

# Check paginate_results function
if grep -q "def paginate_results(" "$QUERY_UTILS"; then
    check_pass "paginate_results() function defined"
else
    check_fail "paginate_results() function NOT found"
fi

# Check format_color_value function
if grep -q "def format_color_value(" "$QUERY_UTILS"; then
    check_pass "format_color_value() function defined"
else
    check_fail "format_color_value() function NOT found"
fi

# Check print_progress function
if grep -q "def print_progress(" "$QUERY_UTILS"; then
    check_pass "print_progress() function defined"
else
    check_fail "print_progress() function NOT found"
fi

# Check bug fix in compare_before_after_resolution.py
COMPARE_SCRIPT="$PROJECT_ROOT/scripts/repositories/graphrag/queries/compare_before_after_resolution.py"
if grep -q "all_types_filtered" "$COMPARE_SCRIPT"; then
    check_pass "Bug fix applied (None filtering in compare_before_after_resolution.py)"
else
    check_fail "Bug fix NOT found in compare_before_after_resolution.py"
fi

###############################################################################
# Test 2: Test Suite
###############################################################################

section_header "Test 2: Test Suite Verification"

TEST_FILE="$PROJECT_ROOT/tests/scripts/repositories/graphrag/queries/test_query_utils_enhancements.py"

# Check test file exists
if [ -f "$TEST_FILE" ]; then
    check_pass "Test suite file exists"
    
    # Count test functions
    TEST_COUNT=$(grep -c "def test_" "$TEST_FILE" || true)
    if [ "$TEST_COUNT" -ge 20 ]; then
        check_pass "Test suite has $TEST_COUNT tests (expected ≥20)"
    else
        check_fail "Test suite has only $TEST_COUNT tests (expected ≥20)"
    fi
    
    # Run tests
    echo ""
    echo "Running test suite..."
    cd "$PROJECT_ROOT"
    if python3 -m pytest "$TEST_FILE" -q --tb=no 2>/dev/null; then
        check_pass "All tests pass"
    else
        check_fail "Some tests failed"
    fi
else
    check_fail "Test suite file NOT found"
    check_fail "Cannot run tests (file missing)"
fi

###############################################################################
# Test 3: Tool-Enhancement-Report
###############################################################################

section_header "Test 3: Tool-Enhancement-Report Verification"

REPORT_FILE="$PROJECT_ROOT/documentation/Tool-Enhancement-Report.md"

if [ -f "$REPORT_FILE" ]; then
    check_pass "Tool-Enhancement-Report.md exists"
    
    # Check file size (should be substantial)
    FILE_SIZE=$(wc -l < "$REPORT_FILE")
    if [ "$FILE_SIZE" -ge 400 ]; then
        check_pass "Report is comprehensive ($FILE_SIZE lines)"
    else
        check_fail "Report seems incomplete ($FILE_SIZE lines, expected ≥400)"
    fi
    
    # Check for key sections
    if grep -q "## 1. Bug Fixes" "$REPORT_FILE"; then
        check_pass "Bug Fixes section present"
    else
        check_fail "Bug Fixes section missing"
    fi
    
    if grep -q "## 2. Output Formatting Improvements" "$REPORT_FILE"; then
        check_pass "Output Formatting section present"
    else
        check_fail "Output Formatting section missing"
    fi
    
    if grep -q "## 3. Pagination Support" "$REPORT_FILE"; then
        check_pass "Pagination Support section present"
    else
        check_fail "Pagination Support section missing"
    fi
    
    if grep -q "## 4. Query Caching" "$REPORT_FILE"; then
        check_pass "Query Caching section present"
    else
        check_fail "Query Caching section missing"
    fi
    
    if grep -q "## 5. Progress Indicators" "$REPORT_FILE"; then
        check_pass "Progress Indicators section present"
    else
        check_fail "Progress Indicators section missing"
    fi
else
    check_fail "Tool-Enhancement-Report.md NOT found"
fi

###############################################################################
# Test 4: Documentation Updates
###############################################################################

section_header "Test 4: Documentation Updates Verification"

QUERIES_README="$PROJECT_ROOT/scripts/repositories/graphrag/queries/README.md"
EXPLAIN_README="$PROJECT_ROOT/scripts/repositories/graphrag/explain/README.md"

# Check queries README updated
if [ -f "$QUERIES_README" ]; then
    check_pass "Query scripts README exists"
    
    if grep -q "New Utility Functions" "$QUERIES_README"; then
        check_pass "Query README includes new utility functions section"
    else
        check_fail "Query README missing utility functions documentation"
    fi
    
    if grep -q "Color Formatting" "$QUERIES_README"; then
        check_pass "Query README documents color formatting"
    else
        check_fail "Query README missing color formatting docs"
    fi
    
    if grep -q "Pagination Support" "$QUERIES_README"; then
        check_pass "Query README documents pagination"
    else
        check_fail "Query README missing pagination docs"
    fi
    
    if grep -q "Query Caching" "$QUERIES_README"; then
        check_pass "Query README documents caching"
    else
        check_fail "Query README missing caching docs"
    fi
else
    check_fail "Query scripts README NOT found"
fi

# Check explain README updated
if [ -f "$EXPLAIN_README" ]; then
    check_pass "Explain tools README exists"
    
    if grep -q "Using Color Formatting" "$EXPLAIN_README"; then
        check_pass "Explain README includes color formatting guide"
    else
        check_fail "Explain README missing color formatting section"
    fi
else
    check_fail "Explain tools README NOT found"
fi

###############################################################################
# Results Summary
###############################################################################

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "  Validation Results"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "Total Checks:  $TOTAL_CHECKS"
echo -e "${GREEN}Passed:        $PASSED_CHECKS${NC}"
if [ "$FAILED_CHECKS" -gt 0 ]; then
    echo -e "${RED}Failed:        $FAILED_CHECKS${NC}"
else
    echo -e "${GREEN}Failed:        $FAILED_CHECKS${NC}"
fi
echo ""

if [ "$FAILED_CHECKS" -eq 0 ]; then
    echo -e "${GREEN}✓ All validation checks passed!${NC}"
    echo ""
    echo "Achievement 7.1 is complete and verified."
    exit 0
else
    echo -e "${RED}✗ Some validation checks failed.${NC}"
    echo ""
    echo "Please review the failures above and address them."
    exit 1
fi

