#!/bin/bash

# Validation Script for Achievement 4.3: Configuration Integration Validated
# Tests all configuration options and CLI arguments

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Project root (4 levels up from observability/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$PROJECT_ROOT"

echo "=================================================="
echo "Achievement 4.3 Validation"
echo "Configuration Integration Validated"
echo "=================================================="
echo ""

# Helper function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Environment Variables Exist in Code"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "GRAPHRAG_TRANSFORMATION_LOGGING exists" \
    "grep -q -- 'GRAPHRAG_TRANSFORMATION_LOGGING' business/services/graphrag/transformation_logger.py"

run_test "GRAPHRAG_SAVE_INTERMEDIATE_DATA exists" \
    "grep -q -- 'GRAPHRAG_SAVE_INTERMEDIATE_DATA' business/stages/graphrag/entity_resolution.py"

run_test "GRAPHRAG_QUALITY_METRICS exists" \
    "grep -q -- 'GRAPHRAG_QUALITY_METRICS' business/pipelines/graphrag.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. Default Values Defined"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "GRAPHRAG_TRANSFORMATION_LOGGING has default 'true'" \
    "grep -q 'GRAPHRAG_TRANSFORMATION_LOGGING.*\"true\"' business/services/graphrag/transformation_logger.py"

run_test "GRAPHRAG_SAVE_INTERMEDIATE_DATA has default 'false'" \
    "grep -q 'GRAPHRAG_SAVE_INTERMEDIATE_DATA.*\"false\"' business/stages/graphrag/entity_resolution.py"

run_test "GRAPHRAG_QUALITY_METRICS has default 'true'" \
    "grep -q 'GRAPHRAG_QUALITY_METRICS.*\"true\"' business/pipelines/graphrag.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. Validation Logic Present"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "GRAPHRAG_TRANSFORMATION_LOGGING uses .lower() validation" \
    "grep -q '.lower().*==.*\"true\"' business/services/graphrag/transformation_logger.py"

run_test "GRAPHRAG_SAVE_INTERMEDIATE_DATA uses .lower() validation" \
    "grep -q '.lower().*==.*\"true\"' business/stages/graphrag/entity_resolution.py"

run_test "GRAPHRAG_QUALITY_METRICS uses .lower() validation" \
    "grep -q '.lower().*==.*\"true\"' business/pipelines/graphrag.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. CLI Arguments Accepted"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

PIPELINE_FILE="business/pipelines/graphrag.py"

run_test "CLI accepts --experiment-id" \
    "grep -q -- '--experiment-id' $PIPELINE_FILE"

run_test "CLI accepts --read-db-name" \
    "grep -q -- '--read-db-name' $PIPELINE_FILE"

run_test "CLI accepts --write-db-name" \
    "grep -q -- '--write-db-name' $PIPELINE_FILE"

run_test "CLI accepts --db-name" \
    "grep -q -- '--db-name' $PIPELINE_FILE"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. CLI Help Works"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Pipeline --help works" \
    "PYTHONPATH=$PROJECT_ROOT python business/pipelines/graphrag.py --help"

run_test "Pipeline accepts experiment arguments" \
    "PYTHONPATH=$PROJECT_ROOT python business/pipelines/graphrag.py --experiment-id test-001 --read-db-name test_db --write-db-name test_db_out --help"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. Deliverables Exist"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Configuration Validation Report exists" \
    "test -f documentation/Configuration-Validation-Report.md"

run_test "Configuration Matrix exists" \
    "test -f documentation/Configuration-Matrix.md"

run_test "Recommended Configurations exists" \
    "test -f documentation/Recommended-Configurations.md"

run_test "Troubleshooting Guide exists" \
    "test -f documentation/Configuration-Troubleshooting-Guide.md"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7. Deliverables Have Content"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Configuration Validation Report has content" \
    "test -s documentation/Configuration-Validation-Report.md"

run_test "Configuration Matrix has content" \
    "test -s documentation/Configuration-Matrix.md"

run_test "Recommended Configurations has content" \
    "test -s documentation/Recommended-Configurations.md"

run_test "Troubleshooting Guide has content" \
    "test -s documentation/Configuration-Troubleshooting-Guide.md"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8. Deliverables Mention Key Variables"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Validation Report mentions GRAPHRAG_TRANSFORMATION_LOGGING" \
    "grep -q 'GRAPHRAG_TRANSFORMATION_LOGGING' documentation/Configuration-Validation-Report.md"

run_test "Configuration Matrix mentions all 3 variables" \
    "grep -q 'GRAPHRAG_TRANSFORMATION_LOGGING' documentation/Configuration-Matrix.md && \
     grep -q 'GRAPHRAG_SAVE_INTERMEDIATE_DATA' documentation/Configuration-Matrix.md && \
     grep -q 'GRAPHRAG_QUALITY_METRICS' documentation/Configuration-Matrix.md"

run_test "Recommended Configurations has environment examples" \
    "grep -q -i 'export\|environment' documentation/Recommended-Configurations.md"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "9. EXECUTION_TASK Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

EXEC_FILE="work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/execution/EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_43_01.md"

run_test "EXECUTION_TASK exists" \
    "test -f $EXEC_FILE"

run_test "EXECUTION_TASK mentions all deliverables" \
    "grep -q 'Configuration-Validation-Report.md' $EXEC_FILE && \
     grep -q 'Configuration-Matrix.md' $EXEC_FILE && \
     grep -q 'Recommended-Configurations.md' $EXEC_FILE && \
     grep -q 'Configuration-Troubleshooting-Guide.md' $EXEC_FILE"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "10. Configuration Scenarios Documented"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Validation Report documents 'All Enabled' scenario" \
    "grep -q -i 'all.*enabled\|all observability enabled' documentation/Configuration-Validation-Report.md"

run_test "Validation Report documents 'All Disabled' scenario" \
    "grep -q -i 'all.*disabled\|all observability disabled' documentation/Configuration-Validation-Report.md"

run_test "Validation Report documents selective features" \
    "grep -q -i 'selective\|logging only\|metrics only' documentation/Configuration-Validation-Report.md"

run_test "Validation Report documents default configuration" \
    "grep -q -i 'default' documentation/Configuration-Validation-Report.md"

echo ""
echo "=================================================="
echo "Validation Summary"
echo "=================================================="
echo ""
echo "Total tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
if [ $FAILED_TESTS -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED_TESTS${NC}"
else
    echo "Failed: $FAILED_TESTS"
fi
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Achievement 4.3 validation: SUCCESS ✅"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Achievement 4.3 validation: FAILED ❌"
    exit 1
fi

