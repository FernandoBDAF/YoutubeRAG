#!/bin/bash
###############################################################################
# Achievement 5.3 Validation Script
# 
# Validates that observability overhead assessment is complete with:
# 1. Cost-benefit analysis completeness
# 2. Production recommendations verification
# 3. Feature toggle strategy validation
# 4. Deliverables existence
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
echo "  Achievement 5.3 Validation: Observability Overhead Assessment"
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
# Test 1: Cost-Benefit Analysis Completeness
###############################################################################

section_header "Test 1: Cost-Benefit Analysis Completeness"

ANALYSIS_FILE="$PROJECT_ROOT/work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/EXECUTION_ANALYSIS_OBSERVABILITY-COST-BENEFIT.md"

if [ -f "$ANALYSIS_FILE" ]; then
    check_pass "EXECUTION_ANALYSIS file exists"
    
    # Check file size
    FILE_SIZE=$(wc -l < "$ANALYSIS_FILE")
    if [ "$FILE_SIZE" -ge 400 ]; then
        check_pass "Analysis is comprehensive ($FILE_SIZE lines, expected ≥400)"
    else
        check_fail "Analysis seems incomplete ($FILE_SIZE lines, expected ≥400)"
    fi
    
    # Check for all 4 cost categories
    if grep -q "Performance Overhead" "$ANALYSIS_FILE" && \
       grep -q "Storage Overhead" "$ANALYSIS_FILE" && \
       grep -q "Code Complexity" "$ANALYSIS_FILE" && \
       grep -q "Maintenance Overhead" "$ANALYSIS_FILE"; then
        check_pass "All 4 cost categories analyzed"
    else
        check_fail "Missing cost categories"
    fi
    
    # Check for all 4 benefit categories
    if grep -q "Debugging Capability" "$ANALYSIS_FILE" && \
       grep -q "Quality Visibility" "$ANALYSIS_FILE" && \
       grep -q "Learning Enablement" "$ANALYSIS_FILE" && \
       grep -q "Experimentation Support" "$ANALYSIS_FILE"; then
        check_pass "All 4 benefit categories analyzed"
    else
        check_fail "Missing benefit categories"
    fi
    
    # Check for cost-benefit matrix
    if grep -q "Cost Summary Matrix" "$ANALYSIS_FILE" || grep -q "Cost-Benefit Matrix" "$ANALYSIS_FILE"; then
        check_pass "Cost-benefit matrix present"
    else
        check_fail "Cost-benefit matrix missing"
    fi
    
    # Check for trade-off analysis
    if grep -q "Trade-Off Analysis" "$ANALYSIS_FILE"; then
        check_pass "Trade-off analysis present"
    else
        check_fail "Trade-off analysis missing"
    fi
    
    # Check for production verdict
    if grep -q "Production Verdict" "$ANALYSIS_FILE"; then
        check_pass "Production verdict present"
    else
        check_fail "Production verdict missing"
    fi
else
    check_fail "EXECUTION_ANALYSIS file NOT found"
fi

###############################################################################
# Test 2: Production Recommendations Verification
###############################################################################

section_header "Test 2: Production Recommendations Verification"

RECOMMENDATIONS_FILE="$PROJECT_ROOT/documentation/Production-Recommendations.md"

if [ -f "$RECOMMENDATIONS_FILE" ]; then
    check_pass "Production-Recommendations.md exists"
    
    # Check file size
    FILE_SIZE=$(wc -l < "$RECOMMENDATIONS_FILE")
    if [ "$FILE_SIZE" -ge 300 ]; then
        check_pass "Recommendations comprehensive ($FILE_SIZE lines, expected ≥300)"
    else
        check_fail "Recommendations incomplete ($FILE_SIZE lines, expected ≥300)"
    fi
    
    # Check for feature categorization
    if grep -q "Always-On Features" "$RECOMMENDATIONS_FILE" || grep -q "Feature Categorization" "$RECOMMENDATIONS_FILE"; then
        check_pass "Feature categorization present"
    else
        check_fail "Feature categorization missing"
    fi
    
    # Check for environment-specific recommendations
    if grep -q "Development Environment" "$RECOMMENDATIONS_FILE" && \
       grep -q "Staging Environment" "$RECOMMENDATIONS_FILE" && \
       grep -q "Production Environment" "$RECOMMENDATIONS_FILE"; then
        check_pass "Environment-specific recommendations present"
    else
        check_fail "Environment-specific recommendations missing"
    fi
    
    # Check for configuration design
    if grep -q "Configuration Guide" "$RECOMMENDATIONS_FILE" || grep -q "Environment Variables" "$RECOMMENDATIONS_FILE"; then
        check_pass "Configuration design present"
    else
        check_fail "Configuration design missing"
    fi
    
    # Check for monitoring strategy
    if grep -q "Monitoring Strategy" "$RECOMMENDATIONS_FILE"; then
        check_pass "Monitoring strategy present"
    else
        check_fail "Monitoring strategy missing"
    fi
    
    # Check for troubleshooting guidelines
    if grep -q "Troubleshooting Guidelines" "$RECOMMENDATIONS_FILE" || grep -q "Troubleshooting" "$RECOMMENDATIONS_FILE"; then
        check_pass "Troubleshooting guidelines present"
    else
        check_fail "Troubleshooting guidelines missing"
    fi
else
    check_fail "Production-Recommendations.md NOT found"
fi

###############################################################################
# Test 3: Feature Toggle Strategy Validation
###############################################################################

section_header "Test 3: Feature Toggle Strategy Validation"

# Feature toggle strategy should be in Production-Recommendations.md
if [ -f "$RECOMMENDATIONS_FILE" ]; then
    # Check for feature flag hierarchy
    if grep -q "Feature Flag Hierarchy" "$RECOMMENDATIONS_FILE" || grep -q "Feature Toggle Strategy" "$RECOMMENDATIONS_FILE"; then
        check_pass "Feature flag hierarchy documented"
    else
        check_fail "Feature flag hierarchy missing"
    fi
    
    # Check for default settings matrix
    if grep -q "Default Settings Matrix" "$RECOMMENDATIONS_FILE" || grep -q "Default Settings" "$RECOMMENDATIONS_FILE"; then
        check_pass "Default settings matrix present"
    else
        check_fail "Default settings matrix missing"
    fi
    
    # Check for performance/storage trade-offs
    if grep -q "Trade-offs" "$RECOMMENDATIONS_FILE" || grep -q "Performance/Storage" "$RECOMMENDATIONS_FILE"; then
        check_pass "Performance/storage trade-offs documented"
    else
        check_fail "Performance/storage trade-offs missing"
    fi
    
    # Check for migration strategy
    if grep -q "Migration Strategy" "$RECOMMENDATIONS_FILE"; then
        check_pass "Migration strategy present"
    else
        check_fail "Migration strategy missing"
    fi
    
    # Check for rollback plan
    if grep -q "Rollback Plan" "$RECOMMENDATIONS_FILE" || grep -q "Rollback" "$RECOMMENDATIONS_FILE"; then
        check_pass "Rollback plan present"
    else
        check_fail "Rollback plan missing"
    fi
else
    check_fail "Cannot verify feature toggle strategy (recommendations file missing)"
fi

###############################################################################
# Test 4: Deliverables Existence
###############################################################################

section_header "Test 4: Deliverables Existence"

# Check EXECUTION_ANALYSIS exists and has content
if [ -f "$ANALYSIS_FILE" ]; then
    FILE_SIZE=$(wc -l < "$ANALYSIS_FILE")
    if [ "$FILE_SIZE" -ge 400 ]; then
        check_pass "EXECUTION_ANALYSIS exists and comprehensive ($FILE_SIZE lines)"
    else
        check_fail "EXECUTION_ANALYSIS incomplete ($FILE_SIZE lines)"
    fi
    
    # Check for all required sections in ANALYSIS
    REQUIRED_SECTIONS=(
        "Executive Summary"
        "Cost Analysis"
        "Benefit Analysis"
        "Cost-Benefit Matrix"
        "Production Verdict"
        "Recommendations"
    )
    
    ALL_SECTIONS=true
    for section in "${REQUIRED_SECTIONS[@]}"; do
        if ! grep -q "$section" "$ANALYSIS_FILE"; then
            ALL_SECTIONS=false
            break
        fi
    done
    
    if $ALL_SECTIONS; then
        check_pass "All sections present in ANALYSIS"
    else
        check_fail "Some sections missing in ANALYSIS"
    fi
else
    check_fail "EXECUTION_ANALYSIS file missing"
fi

# Check Production-Recommendations exists and has content
if [ -f "$RECOMMENDATIONS_FILE" ]; then
    FILE_SIZE=$(wc -l < "$RECOMMENDATIONS_FILE")
    if [ "$FILE_SIZE" -ge 300 ]; then
        check_pass "Production-Recommendations exists and comprehensive ($FILE_SIZE lines)"
    else
        check_fail "Production-Recommendations incomplete ($FILE_SIZE lines)"
    fi
    
    # Check for all required sections in Recommendations
    REQUIRED_SECTIONS=(
        "Overview"
        "Production Verdict"
        "Feature Categorization"
        "Environment-Specific Recommendations"
        "Configuration Guide"
        "Monitoring Strategy"
        "Troubleshooting Guidelines"
        "Feature Toggle Strategy"
    )
    
    ALL_SECTIONS=true
    for section in "${REQUIRED_SECTIONS[@]}"; do
        if ! grep -q "$section" "$RECOMMENDATIONS_FILE"; then
            ALL_SECTIONS=false
            break
        fi
    done
    
    if $ALL_SECTIONS; then
        check_pass "All sections present in Recommendations"
    else
        check_fail "Some sections missing in Recommendations"
    fi
else
    check_fail "Production-Recommendations file missing"
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
    echo "Achievement 5.3 is complete and verified."
    echo ""
    echo "Deliverables:"
    echo "  - EXECUTION_ANALYSIS_OBSERVABILITY-COST-BENEFIT.md"
    echo "  - documentation/Production-Recommendations.md"
    echo ""
    echo "Cost-Benefit Summary:"
    echo "  Performance: <5% overhead"
    echo "  Storage: ~490 MB per run"
    echo "  Benefits: 10x debugging improvement, 23 quality metrics"
    echo "  Verdict: ✅ Strongly recommended for production"
    exit 0
else
    echo -e "${RED}✗ Some validation checks failed.${NC}"
    echo ""
    echo "Please review the failures above and address them."
    exit 1
fi

