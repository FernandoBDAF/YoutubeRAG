#!/bin/bash

################################################################################
# Validation Script: Achievement 3.2 - Explanation Tools Validated
################################################################################
#
# Purpose: Validate all 5 explanation tools work correctly with real pipeline data
# Achievement: 3.2 - Explanation Tools Validated
# Date: 2025-11-13
#
# Tests:
#   1. explain_entity_merge.py
#   2. explain_relationship_filter.py
#   3. explain_community_formation.py
#   4. trace_entity_journey.py
#   5. visualize_graph_evolution.py
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

# Configuration
TRACE_ID="6088e6bd-e305-42d8-9210-e2d3f1dda035"
SCRIPTS_DIR="scripts/repositories/graphrag/explain"
OUTPUT_DIR="work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/observability/explanation-outputs"

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

test_tool() {
    local tool_name=$1
    local test_name=$2
    local command=$3
    
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -e "${YELLOW}[TEST $TESTS_RUN]${NC} $test_name"
    echo "Command: $command"
    
    if eval "$command" > "$OUTPUT_DIR/${tool_name}_output.txt" 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo ""
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo "Error output saved to: $OUTPUT_DIR/${tool_name}_output.txt"
        echo ""
        return 1
    fi
}

################################################################################
# Main Test Execution
################################################################################

print_header "ACHIEVEMENT 3.2: EXPLANATION TOOLS VALIDATION"

echo "Configuration:"
echo "  Trace ID: $TRACE_ID"
echo "  Database: $DB_NAME"
echo "  Scripts Directory: $SCRIPTS_DIR"
echo "  Output Directory: $OUTPUT_DIR"
echo "  Project Root: $(pwd)"
echo ""

################################################################################
# Phase 1: Tool Discovery & Preparation
################################################################################

print_header "PHASE 1: TOOL DISCOVERY & PREPARATION"

# Verify tools exist
echo -e "${YELLOW}Checking for explanation tools...${NC}"
if [ -d "$SCRIPTS_DIR" ]; then
    TOOL_COUNT=$(find "$SCRIPTS_DIR" -name "explain_*.py" -o -name "trace_*.py" -o -name "visualize_*.py" 2>/dev/null | wc -l)
    echo "Found $TOOL_COUNT tools in $SCRIPTS_DIR (expected 5)"
else
    echo -e "${RED}❌ Scripts directory not found: $SCRIPTS_DIR${NC}"
    exit 1
fi
echo ""

# Get sample entity IDs from database
echo -e "${YELLOW}Getting sample entity IDs from database...${NC}"

# Use mongosh to get entity IDs
ENTITY_ID_A=$(mongosh "$MONGODB_URI/$DB_NAME" --quiet --eval "db.entities_resolved.findOne({trace_id: '$TRACE_ID'})?.entity_id" 2>/dev/null | grep -v "^$" | tail -1 || echo "")
ENTITY_ID_B=$(mongosh "$MONGODB_URI/$DB_NAME" --quiet --eval "db.entities_resolved.find({trace_id: '$TRACE_ID'}).limit(2).toArray()[1]?.entity_id" 2>/dev/null | grep -v "^$" | tail -1 || echo "")

if [ -z "$ENTITY_ID_A" ]; then
    echo -e "${RED}❌ Could not retrieve entity IDs from database${NC}"
    echo "Error: Cannot proceed without entity IDs"
    echo "Please ensure:"
    echo "  1. MongoDB is accessible"
    echo "  2. Database '$DB_NAME' exists"
    echo "  3. Collection 'entities_resolved' has data for trace_id '$TRACE_ID'"
    exit 1
fi

echo "Entity A: $ENTITY_ID_A"
echo "Entity B: $ENTITY_ID_B"
echo ""

################################################################################
# Phase 2: Entity Merge & Relationship Explainers
################################################################################

print_header "PHASE 2: ENTITY MERGE & RELATIONSHIP EXPLAINERS (2 tests)"

# Test 1: explain_entity_merge.py
test_tool "explain_entity_merge" \
    "explain_entity_merge.py with valid entities" \
    "python $SCRIPTS_DIR/explain_entity_merge.py --entity-id-a '$ENTITY_ID_A' --entity-id-b '$ENTITY_ID_B' --trace-id $TRACE_ID"

# Test 2: explain_relationship_filter.py
test_tool "explain_relationship_filter" \
    "explain_relationship_filter.py with sample IDs" \
    "python $SCRIPTS_DIR/explain_relationship_filter.py --source-id '$ENTITY_ID_A' --target-id '$ENTITY_ID_B' --trace-id $TRACE_ID"

################################################################################
# Phase 3: Community & Entity Journey Tools
################################################################################

print_header "PHASE 3: COMMUNITY & ENTITY JOURNEY TOOLS (2 tests)"

# Test 3: explain_community_formation.py (expect to fail gracefully - no communities)
TESTS_RUN=$((TESTS_RUN + 1))
echo -e "${YELLOW}[TEST $TESTS_RUN]${NC} explain_community_formation.py with missing community"
echo "Command: python $SCRIPTS_DIR/explain_community_formation.py --community-id 'test_community_123' --trace-id $TRACE_ID"

if python "$SCRIPTS_DIR/explain_community_formation.py" --community-id "test_community_123" --trace-id "$TRACE_ID" > "$OUTPUT_DIR/explain_community_formation_output.txt" 2>&1; then
    echo -e "${GREEN}✅ PASS${NC}: Tool executed (found community)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    # Check if error is expected (community not found)
    if grep -q "Community not found\|No community found\|not found" "$OUTPUT_DIR/explain_community_formation_output.txt" 2>/dev/null; then
        echo -e "${GREEN}✅ PASS${NC}: Tool executed with expected error (community not found)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ FAIL${NC}: Unexpected error"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
fi
echo ""

# Test 4: trace_entity_journey.py
test_tool "trace_entity_journey" \
    "trace_entity_journey.py with entity tracking" \
    "python $SCRIPTS_DIR/trace_entity_journey.py --entity-id '$ENTITY_ID_A' --trace-id $TRACE_ID"

################################################################################
# Phase 4: Graph Evolution Visualizer
################################################################################

print_header "PHASE 4: GRAPH EVOLUTION VISUALIZER (1 test)"

# Test 5: visualize_graph_evolution.py
test_tool "visualize_graph_evolution" \
    "visualize_graph_evolution.py with graph evolution" \
    "python $SCRIPTS_DIR/visualize_graph_evolution.py --trace-id $TRACE_ID"

################################################################################
# Phase 5: Sample Outputs Display
################################################################################

print_header "PHASE 5: SAMPLE OUTPUTS"

echo -e "${YELLOW}--- explain_entity_merge.py output (first 30 lines) ---${NC}"
if [ -f "$OUTPUT_DIR/explain_entity_merge_output.txt" ]; then
    head -30 "$OUTPUT_DIR/explain_entity_merge_output.txt"
else
    echo "(No output file found)"
fi
echo ""

echo -e "${YELLOW}--- trace_entity_journey.py output (first 30 lines) ---${NC}"
if [ -f "$OUTPUT_DIR/trace_entity_journey_output.txt" ]; then
    head -30 "$OUTPUT_DIR/trace_entity_journey_output.txt"
else
    echo "(No output file found)"
fi
echo ""

echo -e "${YELLOW}--- visualize_graph_evolution.py output (first 30 lines) ---${NC}"
if [ -f "$OUTPUT_DIR/visualize_graph_evolution_output.txt" ]; then
    head -30 "$OUTPUT_DIR/visualize_graph_evolution_output.txt"
else
    echo "(No output file found)"
fi
echo ""

################################################################################
# Final Summary
################################################################################

print_header "TEST SUMMARY"

echo "Total Tests Run: $TESTS_RUN"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
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
    echo -e "${GREEN}║  ✅ ACHIEVEMENT 3.2: ALL TESTS PASSED                 ║${NC}"
    echo -e "${GREEN}╚═════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "All 5 explanation tools are working correctly with real pipeline data."
    exit 0
else
    echo -e "${RED}╔═════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ ACHIEVEMENT 3.2: SOME TESTS FAILED                ║${NC}"
    echo -e "${RED}╚═════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Please review the output files in $OUTPUT_DIR for details."
    exit 1
fi

