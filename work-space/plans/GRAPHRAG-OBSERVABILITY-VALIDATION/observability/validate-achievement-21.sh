#!/bin/bash
# Test Script for Achievement 2.1: Baseline Pipeline Run
# Validates baseline pipeline execution and metrics

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Achievement 2.1: Baseline Pipeline Validation Test     ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Configuration
DB_NAME="${DB_NAME:-validation_01}"
MONGODB_URI="${MONGODB_URI}"

if [ -z "$MONGODB_URI" ]; then
    echo -e "${RED}ERROR: MONGODB_URI environment variable not set${NC}"
    echo "Please export MONGODB_URI before running this script"
    exit 1
fi

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Helper function to run test
run_test() {
    local test_name="$1"
    local test_command="$2"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -e "${YELLOW}[TEST $TOTAL_TESTS]${NC} $test_name"
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 1: Database Connectivity${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Test 1: MongoDB connection
run_test "MongoDB connection successful" \
    "mongosh \"$MONGODB_URI\" --quiet --eval 'db.runCommand({ping: 1})' | grep -q 'ok: 1'"

# Test 2: Database exists
run_test "Database '$DB_NAME' exists" \
    "mongosh \"$MONGODB_URI\" --quiet --eval 'db.getName()' | grep -q '$DB_NAME'"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 2: Legacy Collections Verification${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Test 3: Entities collection exists
run_test "Legacy 'entities' collection exists" \
    "mongosh \"$MONGODB_URI\" --quiet --eval 'db.getCollectionNames()' | grep -q 'entities'"

# Test 4: Relations collection exists
run_test "Legacy 'relations' collection exists" \
    "mongosh \"$MONGODB_URI\" --quiet --eval 'db.getCollectionNames()' | grep -q 'relations'"

# Test 5: Communities collection exists
run_test "Legacy 'communities' collection exists" \
    "mongosh \"$MONGODB_URI\" --quiet --eval 'db.getCollectionNames()' | grep -q 'communities'"

# Test 6: Video chunks collection exists
run_test "Legacy 'video_chunks' collection exists" \
    "mongosh \"$MONGODB_URI\" --quiet --eval 'db.getCollectionNames()' | grep -q 'video_chunks'"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 3: Data Presence Validation${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Get counts
ENTITIES_COUNT=$(mongosh "$MONGODB_URI" --quiet --eval "db.entities.countDocuments({})" 2>/dev/null || echo "0")
RELATIONS_COUNT=$(mongosh "$MONGODB_URI" --quiet --eval "db.relations.countDocuments({})" 2>/dev/null || echo "0")
COMMUNITIES_COUNT=$(mongosh "$MONGODB_URI" --quiet --eval "db.communities.countDocuments({})" 2>/dev/null || echo "0")

echo "Entities: $ENTITIES_COUNT"
echo "Relations: $RELATIONS_COUNT"
echo "Communities: $COMMUNITIES_COUNT"
echo ""

# Test 7: Entities populated
run_test "Entities collection populated (> 0 documents)" \
    "[ $ENTITIES_COUNT -gt 0 ]"

# Test 8: Relations populated
run_test "Relations collection populated (> 0 documents)" \
    "[ $RELATIONS_COUNT -gt 0 ]"

# Test 9: Communities populated
run_test "Communities collection populated (> 0 documents)" \
    "[ $COMMUNITIES_COUNT -gt 0 ]"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 4: Data Quality Checks${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Test 10: Entities have required fields
run_test "Entities have 'entity_id' field" \
    "mongosh \"$MONGODB_URI\" --quiet --eval 'db.entities.findOne({}, {entity_id: 1})' | grep -q 'entity_id'"

# Test 11: Relations have required fields
run_test "Relations have 'source' field" \
    "mongosh \"$MONGODB_URI\" --quiet --eval 'db.relations.findOne({}, {source: 1})' | grep -q 'source'"

# Test 12: Communities have required fields
run_test "Communities have 'community_id' field" \
    "mongosh \"$MONGODB_URI\" --quiet --eval 'db.communities.findOne({}, {community_id: 1})' | grep -q 'community_id'"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 5: Observability Disabled Verification${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Test 13: No transformation_logs collection (observability disabled)
if mongosh "$MONGODB_URI" --quiet --eval 'db.getCollectionNames()' 2>/dev/null | grep -q 'transformation_logs'; then
    echo -e "${YELLOW}⚠️  WARNING${NC}: transformation_logs collection exists (observability may have been enabled)"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    FAILED_TESTS=$((FAILED_TESTS + 1))
else
    echo -e "${GREEN}✅ PASS${NC}: No transformation_logs collection (observability correctly disabled)"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

# Test 14: No entities_raw collection (observability disabled)
if mongosh "$MONGODB_URI" --quiet --eval 'db.getCollectionNames()' 2>/dev/null | grep -q 'entities_raw'; then
    echo -e "${YELLOW}⚠️  WARNING${NC}: entities_raw collection exists (observability may have been enabled)"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    FAILED_TESTS=$((FAILED_TESTS + 1))
else
    echo -e "${GREEN}✅ PASS${NC}: No entities_raw collection (observability correctly disabled)"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 6: Performance Metrics${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Calculate metrics
ENTITIES_PER_RELATION=$(echo "scale=2; $ENTITIES_COUNT / $RELATIONS_COUNT" | bc 2>/dev/null || echo "N/A")
ENTITIES_PER_COMMUNITY=$(echo "scale=2; $ENTITIES_COUNT / $COMMUNITIES_COUNT" | bc 2>/dev/null || echo "N/A")

echo "📊 Baseline Metrics:"
echo "  - Entities: $ENTITIES_COUNT"
echo "  - Relations: $RELATIONS_COUNT"
echo "  - Communities: $COMMUNITIES_COUNT"
echo "  - Entities per Relation: $ENTITIES_PER_RELATION"
echo "  - Entities per Community: $ENTITIES_PER_COMMUNITY"
echo ""

# Test 15: Reasonable entity count (> 100 for meaningful baseline)
run_test "Entity count reasonable (> 100)" \
    "[ $ENTITIES_COUNT -gt 100 ]"

# Test 16: Reasonable relation count (> 50 for meaningful baseline)
run_test "Relation count reasonable (> 50)" \
    "[ $RELATIONS_COUNT -gt 50 ]"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}╔═════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ ALL TESTS PASSED                      ║${NC}"
    echo -e "${GREEN}╚═════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Achievement 2.1 baseline is validated."
    echo "Baseline metrics recorded for comparison with Achievement 2.2."
    exit 0
else
    echo -e "${RED}╔═════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ SOME TESTS FAILED                     ║${NC}"
    echo -e "${RED}╚═════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Please review the failed tests above."
    exit 1
fi

