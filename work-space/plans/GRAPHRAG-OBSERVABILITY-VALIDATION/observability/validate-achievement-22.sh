#!/bin/bash
# Test Script for Achievement 2.2: Observability Pipeline Run
# Validates observability collections and data quality

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Achievement 2.2: Observability Pipeline Validation     ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Configuration
DB_NAME="${DB_NAME:-validation_01}"
MONGODB_URI="${MONGODB_URI}"
TRACE_ID="${TRACE_ID:-6088e6bd-e305-42d8-9210-e2d3f1dda035}"

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

echo "Configuration:"
echo "  Database: $DB_NAME"
echo "  Trace ID: $TRACE_ID"
echo ""

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 1: Database Connectivity${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Test 1: MongoDB connection
run_test "MongoDB connection successful" \
    "mongosh \"$MONGODB_URI\" --quiet --eval 'db.runCommand({ping: 1})' | grep -q 'ok: 1'"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 2: Observability Collections Verification${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Test 2-9: Check all observability collections exist
OBSERVABILITY_COLLECTIONS=(
    "transformation_logs"
    "entities_raw"
    "entities_resolved"
    "relations_raw"
    "quality_metrics"
    "graphrag_runs"
)

for collection in "${OBSERVABILITY_COLLECTIONS[@]}"; do
    run_test "Observability collection '$collection' exists" \
        "mongosh \"$MONGODB_URI\" --quiet --eval 'db.getCollectionNames()' | grep -q '$collection'"
done

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 3: Collection Population Verification${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Get counts
TRANSFORMATION_LOGS=$(mongosh "$MONGODB_URI" --quiet --eval "db.transformation_logs.countDocuments({trace_id: '$TRACE_ID'})" 2>/dev/null || echo "0")
ENTITIES_RAW=$(mongosh "$MONGODB_URI" --quiet --eval "db.entities_raw.countDocuments({trace_id: '$TRACE_ID'})" 2>/dev/null || echo "0")
ENTITIES_RESOLVED=$(mongosh "$MONGODB_URI" --quiet --eval "db.entities_resolved.countDocuments({trace_id: '$TRACE_ID'})" 2>/dev/null || echo "0")
RELATIONS_RAW=$(mongosh "$MONGODB_URI" --quiet --eval "db.relations_raw.countDocuments({trace_id: '$TRACE_ID'})" 2>/dev/null || echo "0")
QUALITY_METRICS=$(mongosh "$MONGODB_URI" --quiet --eval "db.quality_metrics.countDocuments({trace_id: '$TRACE_ID'})" 2>/dev/null || echo "0")
GRAPHRAG_RUNS=$(mongosh "$MONGODB_URI" --quiet --eval "db.graphrag_runs.countDocuments({trace_id: '$TRACE_ID'})" 2>/dev/null || echo "0")

echo "📊 Document Counts (trace_id: $TRACE_ID):"
echo "  - transformation_logs: $TRANSFORMATION_LOGS"
echo "  - entities_raw: $ENTITIES_RAW"
echo "  - entities_resolved: $ENTITIES_RESOLVED"
echo "  - relations_raw: $RELATIONS_RAW"
echo "  - quality_metrics: $QUALITY_METRICS"
echo "  - graphrag_runs: $GRAPHRAG_RUNS"
echo ""

# Test 10-15: Verify collections are populated
run_test "transformation_logs populated (> 100 events)" \
    "[ $TRANSFORMATION_LOGS -gt 100 ]"

run_test "entities_raw populated (> 0 entities)" \
    "[ $ENTITIES_RAW -gt 0 ]"

run_test "entities_resolved populated (> 0 entities)" \
    "[ $ENTITIES_RESOLVED -gt 0 ]"

run_test "relations_raw populated (> 0 relationships)" \
    "[ $RELATIONS_RAW -gt 0 ]"

run_test "quality_metrics populated (> 10 metrics)" \
    "[ $QUALITY_METRICS -gt 10 ]"

run_test "graphrag_runs populated (= 1 run)" \
    "[ $GRAPHRAG_RUNS -eq 1 ]"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 4: Trace ID Consistency Validation${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Test 16: Single trace_id across all collections
UNIQUE_TRACE_IDS=$(mongosh "$MONGODB_URI" --quiet --eval "
    const collections = ['transformation_logs', 'entities_raw', 'entities_resolved', 'relations_raw', 'quality_metrics', 'graphrag_runs'];
    const trace_ids = new Set();
    collections.forEach(coll => {
        if (db.getCollectionNames().includes(coll)) {
            db[coll].distinct('trace_id').forEach(id => trace_ids.add(id));
        }
    });
    print(trace_ids.size);
" 2>/dev/null || echo "0")

run_test "Single trace_id across all collections" \
    "[ $UNIQUE_TRACE_IDS -eq 1 ]"

# Test 17: Trace ID matches expected
ACTUAL_TRACE_ID=$(mongosh "$MONGODB_URI" --quiet --eval "db.transformation_logs.findOne({}, {trace_id: 1})?.trace_id" 2>/dev/null || echo "")

run_test "Trace ID matches expected ($TRACE_ID)" \
    "[ \"$ACTUAL_TRACE_ID\" = \"$TRACE_ID\" ]"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 5: Schema Validation${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Test 18: transformation_logs has required fields
run_test "transformation_logs has 'event_type' field" \
    "mongosh \"$MONGODB_URI\" --quiet --eval 'db.transformation_logs.findOne({trace_id: \"$TRACE_ID\"}, {event_type: 1})' | grep -q 'event_type'"

# Test 19: entities_raw has required fields
run_test "entities_raw has 'entity_id' field" \
    "mongosh \"$MONGODB_URI\" --quiet --eval 'db.entities_raw.findOne({trace_id: \"$TRACE_ID\"}, {entity_id: 1})' | grep -q 'entity_id'"

# Test 20: entities_resolved has required fields
run_test "entities_resolved has 'entity_id' field" \
    "mongosh \"$MONGODB_URI\" --quiet --eval 'db.entities_resolved.findOne({trace_id: \"$TRACE_ID\"}, {entity_id: 1})' | grep -q 'entity_id'"

# Test 21: quality_metrics has required fields
run_test "quality_metrics has 'metric_name' field" \
    "mongosh \"$MONGODB_URI\" --quiet --eval 'db.quality_metrics.findOne({trace_id: \"$TRACE_ID\"}, {metric_name: 1})' | grep -q 'metric_name'"

# Test 22: graphrag_runs has required fields
run_test "graphrag_runs has 'status' field" \
    "mongosh \"$MONGODB_URI\" --quiet --eval 'db.graphrag_runs.findOne({trace_id: \"$TRACE_ID\"}, {status: 1})' | grep -q 'status'"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 6: Data Quality Checks${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Test 23: Confidence scores in valid range (entities_raw)
INVALID_ENTITIES=$(mongosh "$MONGODB_URI" --quiet --eval "
    db.entities_raw.countDocuments({
        trace_id: '$TRACE_ID',
        \$or: [{confidence: {\$lt: 0.0}}, {confidence: {\$gt: 1.0}}]
    })
" 2>/dev/null || echo "0")

run_test "All entity confidence scores valid (0.0-1.0)" \
    "[ $INVALID_ENTITIES -eq 0 ]"

# Test 24: Timestamps present
run_test "transformation_logs has timestamps" \
    "mongosh \"$MONGODB_URI\" --quiet --eval 'db.transformation_logs.findOne({trace_id: \"$TRACE_ID\"}, {timestamp: 1})' | grep -q 'timestamp'"

# Test 25: Entity linkage (chunk_id present)
run_test "entities_raw has chunk_id linkage" \
    "mongosh \"$MONGODB_URI\" --quiet --eval 'db.entities_raw.findOne({trace_id: \"$TRACE_ID\"}, {chunk_id: 1})' | grep -q 'chunk_id'"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Phase 7: Legacy Collections Verification${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Test 26-28: Legacy collections still exist
run_test "Legacy 'entities' collection still exists" \
    "mongosh \"$MONGODB_URI\" --quiet --eval 'db.getCollectionNames()' | grep -q 'entities'"

run_test "Legacy 'relations' collection still exists" \
    "mongosh \"$MONGODB_URI\" --quiet --eval 'db.getCollectionNames()' | grep -q 'relations'"

run_test "Legacy 'communities' collection still exists" \
    "mongosh \"$MONGODB_URI\" --quiet --eval 'db.getCollectionNames()' | grep -q 'communities'"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

echo "📊 Final Observability Metrics:"
echo "  - Total observability documents: $((TRANSFORMATION_LOGS + ENTITIES_RAW + ENTITIES_RESOLVED + RELATIONS_RAW + QUALITY_METRICS + GRAPHRAG_RUNS))"
echo "  - Transformation events logged: $TRANSFORMATION_LOGS"
echo "  - Entities tracked: $ENTITIES_RAW (raw) / $ENTITIES_RESOLVED (resolved)"
echo "  - Relationships tracked: $RELATIONS_RAW"
echo "  - Quality metrics calculated: $QUALITY_METRICS"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}╔═════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ ALL TESTS PASSED                      ║${NC}"
    echo -e "${GREEN}╚═════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Achievement 2.2 observability pipeline is validated."
    echo "All observability features are working correctly."
    exit 0
else
    echo -e "${RED}╔═════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ SOME TESTS FAILED                     ║${NC}"
    echo -e "${RED}╚═════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Please review the failed tests above."
    exit 1
fi

