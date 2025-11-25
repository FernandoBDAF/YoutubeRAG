#!/bin/bash
# Master Validation Script for All Achievements
# Runs all validation tests for GRAPHRAG-OBSERVABILITY-VALIDATION plan

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                           ║${NC}"
echo -e "${CYAN}║    GRAPHRAG OBSERVABILITY VALIDATION - MASTER TEST       ║${NC}"
echo -e "${CYAN}║              All Achievements Validation                  ║${NC}"
echo -e "${CYAN}║                                                           ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# From observability/ go up 4 levels: observability -> GRAPHRAG-OBSERVABILITY-VALIDATION -> plans -> work-space -> YoutubeRAG
PROJECT_ROOT="$SCRIPT_DIR/../../../.."
cd "$PROJECT_ROOT"

echo "Working Directory: $(pwd)"
echo "Script Directory: $SCRIPT_DIR"
echo ""

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo -e "${CYAN}Loading environment variables from .env...${NC}"
    # Use set -a to automatically export variables, then source the file
    set -a
    source <(grep -v '^#' .env | grep -v '^$' | grep '=' | sed 's/\r$//')
    set +a
    echo -e "${GREEN}✅ Environment variables loaded${NC}"
    echo ""
elif [ -f ".env.local" ]; then
    echo -e "${CYAN}Loading environment variables from .env.local...${NC}"
    set -a
    source <(grep -v '^#' .env.local | grep -v '^$' | grep '=' | sed 's/\r$//')
    set +a
    echo -e "${GREEN}✅ Environment variables loaded${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠️  No .env file found - using existing environment variables${NC}"
    echo ""
fi

# Track results
TOTAL_ACHIEVEMENTS=0
PASSED_ACHIEVEMENTS=0
FAILED_ACHIEVEMENTS=0
SKIPPED_ACHIEVEMENTS=0

# Achievement tracking arrays
declare -a ACHIEVEMENT_NAMES
declare -a ACHIEVEMENT_STATUS

# Helper function to run achievement test
run_achievement_test() {
    local achievement_id="$1"
    local achievement_name="$2"
    local test_script="$3"
    local skip_reason="$4"
    
    TOTAL_ACHIEVEMENTS=$((TOTAL_ACHIEVEMENTS + 1))
    ACHIEVEMENT_NAMES+=("$achievement_name")
    
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Achievement $achievement_id: $achievement_name${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    if [ -n "$skip_reason" ]; then
        echo -e "${YELLOW}⏭️  SKIPPED${NC}: $skip_reason"
        ACHIEVEMENT_STATUS+=("SKIPPED")
        SKIPPED_ACHIEVEMENTS=$((SKIPPED_ACHIEVEMENTS + 1))
        echo ""
        return 0
    fi
    
    if [ ! -f "$test_script" ]; then
        echo -e "${YELLOW}⏭️  SKIPPED${NC}: No test script found ($test_script)"
        ACHIEVEMENT_STATUS+=("SKIPPED")
        SKIPPED_ACHIEVEMENTS=$((SKIPPED_ACHIEVEMENTS + 1))
        echo ""
        return 0
    fi
    
    echo "Running: $test_script"
    echo ""
    
    if bash "$test_script"; then
        echo -e "${GREEN}✅ PASSED${NC}: Achievement $achievement_id"
        ACHIEVEMENT_STATUS+=("PASSED")
        PASSED_ACHIEVEMENTS=$((PASSED_ACHIEVEMENTS + 1))
    else
        echo -e "${RED}❌ FAILED${NC}: Achievement $achievement_id"
        ACHIEVEMENT_STATUS+=("FAILED")
        FAILED_ACHIEVEMENTS=$((FAILED_ACHIEVEMENTS + 1))
    fi
    
    echo ""
}

# Phase 0: Foundation (Achievements 0.1-0.3)
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  PHASE 0: FOUNDATION                                      ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

run_achievement_test "0.1" "Collection Name Compatibility" "$SCRIPT_DIR/validate-achievement-01.sh" ""
run_achievement_test "0.2" "Configuration Compatibility" "$SCRIPT_DIR/validate-achievement-02.sh" ""
run_achievement_test "0.3" "Environment Variables" "$SCRIPT_DIR/validate-achievement-03.sh" ""

# Phase 1: Infrastructure (Achievements 1.1-1.3)
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  PHASE 1: INFRASTRUCTURE                                  ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

run_achievement_test "1.1" "Observability Stack Running" "$SCRIPT_DIR/validate-achievement-11.sh" ""
run_achievement_test "1.2" "Metrics Endpoint Validated" "$SCRIPT_DIR/validate-achievement-12.sh" ""
run_achievement_test "1.3" "Grafana Dashboards Configured" "$SCRIPT_DIR/validate-achievement-13.sh" ""

# Phase 2: Pipeline Execution (Achievements 2.1-2.3)
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  PHASE 2: PIPELINE EXECUTION                              ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

run_achievement_test "2.1" "Baseline Pipeline Run" "$SCRIPT_DIR/validate-achievement-21.sh" ""
run_achievement_test "2.2" "Observability Pipeline Run" "$SCRIPT_DIR/validate-achievement-22.sh" ""
run_achievement_test "2.3" "Data Quality Validation" "$SCRIPT_DIR/validate-achievement-23.sh" ""

# Phase 3: Validation (Achievements 3.1-3.3)
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  PHASE 3: VALIDATION                                      ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

run_achievement_test "3.1" "Query Scripts Validated" "$SCRIPT_DIR/validate-achievement-31.sh" ""
run_achievement_test "3.2" "Explanation Tools Validated" "$SCRIPT_DIR/validate-achievement-32.sh" ""
run_achievement_test "3.3" "Quality Metrics Validated" "$SCRIPT_DIR/validate-achievement-33.sh" ""

# Phase 4: Stage Compatibility (Achievement 4.1)
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  PHASE 4: STAGE COMPATIBILITY                             ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

run_achievement_test "4.1" "Stage Compatibility Verified" "$SCRIPT_DIR/validate-achievement-41.sh" ""

# Final Summary
echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  OVERALL VALIDATION SUMMARY                               ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "Total Achievements: $TOTAL_ACHIEVEMENTS"
echo -e "${GREEN}Passed: $PASSED_ACHIEVEMENTS${NC}"
echo -e "${RED}Failed: $FAILED_ACHIEVEMENTS${NC}"
echo -e "${YELLOW}Skipped: $SKIPPED_ACHIEVEMENTS${NC}"
echo ""

# Detailed results
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Detailed Results by Achievement${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

for i in "${!ACHIEVEMENT_NAMES[@]}"; do
    achievement_name="${ACHIEVEMENT_NAMES[$i]}"
    status="${ACHIEVEMENT_STATUS[$i]}"
    
    case "$status" in
        "PASSED")
            echo -e "${GREEN}✅ PASSED${NC}: $achievement_name"
            ;;
        "FAILED")
            echo -e "${RED}❌ FAILED${NC}: $achievement_name"
            ;;
        "SKIPPED")
            echo -e "${YELLOW}⏭️  SKIPPED${NC}: $achievement_name"
            ;;
    esac
done

echo ""

# Calculate success rate
if [ $TOTAL_ACHIEVEMENTS -gt 0 ]; then
    TESTABLE_ACHIEVEMENTS=$((TOTAL_ACHIEVEMENTS - SKIPPED_ACHIEVEMENTS))
    if [ $TESTABLE_ACHIEVEMENTS -gt 0 ]; then
        SUCCESS_RATE=$(echo "scale=1; $PASSED_ACHIEVEMENTS * 100 / $TESTABLE_ACHIEVEMENTS" | bc)
        echo "Success Rate: ${SUCCESS_RATE}% ($PASSED_ACHIEVEMENTS/$TESTABLE_ACHIEVEMENTS testable achievements)"
    fi
fi

echo ""

# Final verdict
if [ $FAILED_ACHIEVEMENTS -eq 0 ]; then
    echo -e "${GREEN}╔═════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ ALL TESTABLE ACHIEVEMENTS PASSED      ║${NC}"
    echo -e "${GREEN}╚═════════════════════════════════════════════╝${NC}"
    echo ""
    echo "🎉 GRAPHRAG Observability Validation: COMPLETE"
    echo ""
    echo "All testable achievements have passed validation."
    echo "The observability infrastructure is production-ready."
    exit 0
else
    echo -e "${RED}╔═════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ SOME ACHIEVEMENTS FAILED              ║${NC}"
    echo -e "${RED}╚═════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Please review the failed achievements above."
    echo "Check individual test outputs for detailed error information."
    exit 1
fi

