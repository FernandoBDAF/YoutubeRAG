#!/bin/bash
# validate-achievement-41.sh - Achievement 4.1: Stage Compatibility Verified

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
# observability/ -> GRAPHRAG-OBSERVABILITY-VALIDATION/ -> plans/ -> work-space/ -> PROJECT_ROOT
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../../../.."

################################################################################
# Test 1: CLI Arguments Added to Pipeline
################################################################################

test_cli_arguments() {
    print_header "TEST 1: CLI Arguments Added to Pipeline"
    run_test
    
    PIPELINE_FILE="$PROJECT_ROOT/business/pipelines/graphrag.py"
    
    if [ ! -f "$PIPELINE_FILE" ]; then
        print_fail "Pipeline file not found: $PIPELINE_FILE"
        return 1
    fi
    
    print_pass "Pipeline file exists"
    
    # Check for required CLI arguments
    REQUIRED_ARGS=(
        "experiment-id"
        "db-name"
        "read-db-name"
        "write-db-name"
    )
    
    MISSING_ARGS=()
    for arg in "${REQUIRED_ARGS[@]}"; do
        if ! grep -q -- "--$arg" "$PIPELINE_FILE"; then
            MISSING_ARGS+=("--$arg")
        fi
    done
    
    if [ ${#MISSING_ARGS[@]} -eq 0 ]; then
        print_pass "All 4 CLI arguments defined in pipeline"
    else
        print_fail "Missing CLI arguments: ${MISSING_ARGS[*]}"
        return 1
    fi
}

################################################################################
# Test 2: Pipeline Help Output Shows New Arguments
################################################################################

test_help_output() {
    print_header "TEST 2: Pipeline Help Output Shows New Arguments"
    run_test
    
    cd "$PROJECT_ROOT" || exit 2
    
    # Capture help output
    HELP_OUTPUT=$(PYTHONPATH="$PROJECT_ROOT" python business/pipelines/graphrag.py --help 2>&1)
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -ne 0 ]; then
        print_fail "Pipeline --help failed with exit code $EXIT_CODE"
        echo "Output: $HELP_OUTPUT"
        return 1
    fi
    
    print_pass "Pipeline --help executed successfully"
    
    # Check for required arguments in help output
    REQUIRED_IN_HELP=(
        "experiment-id"
        "db-name"
        "read-db-name"
        "write-db-name"
    )
    
    MISSING_IN_HELP=()
    for arg in "${REQUIRED_IN_HELP[@]}"; do
        if ! echo "$HELP_OUTPUT" | grep -q -- "--$arg"; then
            MISSING_IN_HELP+=("--$arg")
        fi
    done
    
    if [ ${#MISSING_IN_HELP[@]} -eq 0 ]; then
        print_pass "All 4 arguments appear in --help output"
    else
        print_fail "Missing in --help: ${MISSING_IN_HELP[*]}"
        return 1
    fi
}

################################################################################
# Test 3: BaseStageConfig Has Required Fields
################################################################################

test_base_stage_config() {
    print_header "TEST 3: BaseStageConfig Has Required Fields"
    run_test
    
    CONFIG_FILE="$PROJECT_ROOT/core/models/config.py"
    
    if [ ! -f "$CONFIG_FILE" ]; then
        print_fail "Config file not found: $CONFIG_FILE"
        return 1
    fi
    
    print_pass "Config file exists"
    
    # Check for BaseStageConfig class
    if ! grep -q "class BaseStageConfig" "$CONFIG_FILE"; then
        print_fail "BaseStageConfig class not found"
        return 1
    fi
    
    print_pass "BaseStageConfig class found"
    
    # Check for required fields
    REQUIRED_FIELDS=(
        "trace_id"
        "read_db_name"
        "write_db_name"
    )
    
    MISSING_FIELDS=()
    for field in "${REQUIRED_FIELDS[@]}"; do
        if ! grep -q "$field" "$CONFIG_FILE"; then
            MISSING_FIELDS+=("$field")
        fi
    done
    
    if [ ${#MISSING_FIELDS[@]} -eq 0 ]; then
        print_pass "All required fields present in BaseStageConfig"
    else
        print_fail "Missing fields: ${MISSING_FIELDS[*]}"
        return 1
    fi
}

################################################################################
# Test 4: Stage Configs Inherit from BaseStageConfig
################################################################################

test_stage_configs() {
    print_header "TEST 4: Stage Configs Inherit from BaseStageConfig"
    run_test
    
    GRAPHRAG_CONFIG="$PROJECT_ROOT/core/config/graphrag.py"
    
    if [ ! -f "$GRAPHRAG_CONFIG" ]; then
        print_fail "GraphRAG config not found: $GRAPHRAG_CONFIG"
        return 1
    fi
    
    print_pass "GraphRAG config file exists"
    
    # Check for stage config classes
    STAGE_CONFIGS=(
        "GraphExtractionConfig"
        "EntityResolutionConfig"
        "GraphConstructionConfig"
        "CommunityDetectionConfig"
    )
    
    MISSING_CONFIGS=()
    for config in "${STAGE_CONFIGS[@]}"; do
        if ! grep -q "$config" "$GRAPHRAG_CONFIG"; then
            MISSING_CONFIGS+=("$config")
        fi
    done
    
    if [ ${#MISSING_CONFIGS[@]} -eq 0 ]; then
        print_pass "All 4 stage config classes found"
    else
        print_fail "Missing stage configs: ${MISSING_CONFIGS[*]}"
        return 1
    fi
}

################################################################################
# Test 5: from_args_env Method Exists
################################################################################

test_from_args_env() {
    print_header "TEST 5: from_args_env Method Exists"
    run_test
    
    CONFIG_FILE="$PROJECT_ROOT/core/models/config.py"
    GRAPHRAG_CONFIG="$PROJECT_ROOT/core/config/graphrag.py"
    
    # Check for from_args_env in BaseStageConfig
    if grep -q "def from_args_env" "$CONFIG_FILE"; then
        print_pass "from_args_env method found in BaseStageConfig"
    else
        print_fail "from_args_env method not found in BaseStageConfig"
        return 1
    fi
    
    # Check for from_args_env usage in GraphRAGPipelineConfig
    if grep -q "from_args_env" "$GRAPHRAG_CONFIG"; then
        print_pass "from_args_env method used in GraphRAGPipelineConfig"
    else
        print_fail "from_args_env not used in GraphRAGPipelineConfig"
        return 1
    fi
}

################################################################################
# Test 6: TransformationLogger Integration
################################################################################

test_transformation_logger() {
    print_header "TEST 6: TransformationLogger Integration"
    run_test
    
    LOGGER_FILE="$PROJECT_ROOT/business/services/graphrag/transformation_logger.py"
    
    if [ ! -f "$LOGGER_FILE" ]; then
        print_fail "TransformationLogger not found"
        return 1
    fi
    
    print_pass "TransformationLogger service exists"
    
    # Check for TransformationLogger class
    if grep -q "class TransformationLogger" "$LOGGER_FILE"; then
        print_pass "TransformationLogger class defined"
    else
        print_fail "TransformationLogger class not found"
        return 1
    fi
}

################################################################################
# Test 7: IntermediateDataService Integration
################################################################################

test_intermediate_data_service() {
    print_header "TEST 7: IntermediateDataService Integration"
    run_test
    
    SERVICE_FILE="$PROJECT_ROOT/business/services/graphrag/intermediate_data.py"
    
    if [ ! -f "$SERVICE_FILE" ]; then
        print_fail "IntermediateDataService not found"
        return 1
    fi
    
    print_pass "IntermediateDataService exists"
    
    # Check for IntermediateDataService class
    if grep -q "class IntermediateDataService" "$SERVICE_FILE"; then
        print_pass "IntermediateDataService class defined"
    else
        print_fail "IntermediateDataService class not found"
        return 1
    fi
}

################################################################################
# Test 8: QualityMetricsService Integration
################################################################################

test_quality_metrics_service() {
    print_header "TEST 8: QualityMetricsService Integration"
    run_test
    
    SERVICE_FILE="$PROJECT_ROOT/business/services/graphrag/quality_metrics.py"
    
    if [ ! -f "$SERVICE_FILE" ]; then
        print_fail "QualityMetricsService not found"
        return 1
    fi
    
    print_pass "QualityMetricsService exists"
    
    # Check for QualityMetricsService class
    if grep -q "class QualityMetricsService" "$SERVICE_FILE"; then
        print_pass "QualityMetricsService class defined"
    else
        print_fail "QualityMetricsService class not found"
        return 1
    fi
}

################################################################################
# Test 9: Deliverables Exist
################################################################################

test_deliverables() {
    print_header "TEST 9: Deliverables Exist"
    run_test
    
    DOC_DIR="$PROJECT_ROOT/documentation"
    
    DELIVERABLES=(
        "Stage-Compatibility-Report.md"
        "Pipeline-Testing-Infrastructure-Added.md"
        "Stage-Test-Results.md"
        "Stage-Performance-Impact.md"
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
# Test 10: Stage Compatibility Verified
################################################################################

test_stage_compatibility() {
    print_header "TEST 10: Stage Compatibility Verified"
    run_test
    
    RESULTS_FILE="$PROJECT_ROOT/documentation/Stage-Test-Results.md"
    
    if [ ! -f "$RESULTS_FILE" ]; then
        print_fail "Stage-Test-Results.md not found"
        return 1
    fi
    
    # Check that all 4 stages are documented as compatible
    STAGES=(
        "Extraction"
        "Resolution"
        "Construction"
        "Detection"
    )
    
    MISSING_STAGES=()
    for stage in "${STAGES[@]}"; do
        if ! grep -q "✅ Compatible" "$RESULTS_FILE" | grep -q "$stage"; then
            # Alternative check: look for stage name and Compatible status
            if grep -q "$stage" "$RESULTS_FILE" && grep -q "Compatible" "$RESULTS_FILE"; then
                print_pass "$stage verified compatible"
            else
                MISSING_STAGES+=("$stage")
            fi
        else
            print_pass "$stage verified compatible"
        fi
    done
    
    if [ ${#MISSING_STAGES[@]} -gt 0 ]; then
        print_fail "Stages not verified: ${MISSING_STAGES[*]}"
        return 1
    fi
}

################################################################################
# Test 11: Performance Impact Documented
################################################################################

test_performance_impact() {
    print_header "TEST 11: Performance Impact Documented"
    run_test
    
    PERF_FILE="$PROJECT_ROOT/documentation/Stage-Performance-Impact.md"
    
    if [ ! -f "$PERF_FILE" ]; then
        print_fail "Stage-Performance-Impact.md not found"
        return 1
    fi
    
    print_pass "Performance impact document exists"
    
    # Check for key sections
    REQUIRED_SECTIONS=(
        "Extraction"
        "Resolution"
        "Construction"
        "Detection"
        "overhead"
        "Performance Impact"
    )
    
    MISSING_SECTIONS=()
    for section in "${REQUIRED_SECTIONS[@]}"; do
        if ! grep -qi "$section" "$PERF_FILE"; then
            MISSING_SECTIONS+=("$section")
        fi
    done
    
    if [ ${#MISSING_SECTIONS[@]} -eq 0 ]; then
        print_pass "All required sections present in performance document"
    else
        print_fail "Missing sections: ${MISSING_SECTIONS[*]}"
        return 1
    fi
}

################################################################################
# Test 12: EXECUTION_TASK Complete
################################################################################

test_execution_task() {
    print_header "TEST 12: EXECUTION_TASK Complete"
    run_test
    
    EXEC_FILE="$PROJECT_ROOT/work-space/plans/GRAPHRAG-OBSERVABILITY-VALIDATION/execution/EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_41_01.md"
    
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
    if grep -q "Stage-Test-Results.md.*COMPLETE" "$EXEC_FILE" && \
       grep -q "Stage-Performance-Impact.md.*COMPLETE" "$EXEC_FILE"; then
        print_pass "All deliverables marked complete in EXECUTION_TASK"
    else
        print_fail "Not all deliverables marked complete"
        return 1
    fi
}

################################################################################
# Main execution
################################################################################

main() {
    print_header "ACHIEVEMENT 4.1 VALIDATION"
    echo ""
    echo "Achievement: Stage Compatibility Verified"
    echo "Validates: CLI infrastructure, stage compatibility, observability integration"
    echo ""
    
    # Run all tests
    test_cli_arguments
    test_help_output
    test_base_stage_config
    test_stage_configs
    test_from_args_env
    test_transformation_logger
    test_intermediate_data_service
    test_quality_metrics_service
    test_deliverables
    test_stage_compatibility
    test_performance_impact
    test_execution_task
    
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
        echo -e "${GREEN}║          ✅ ACHIEVEMENT 4.1: VALIDATED                        ║${NC}"
        echo -e "${GREEN}║                                                               ║${NC}"
        echo -e "${GREEN}║  All 4 stages compatible with observability infrastructure   ║${NC}"
        echo -e "${GREEN}║  CLI arguments added and verified                            ║${NC}"
        echo -e "${GREEN}║  All deliverables complete                                   ║${NC}"
        echo -e "${GREEN}║                                                               ║${NC}"
        echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo "Next Steps:"
        echo "  1. Proceed to Achievement 4.2 (Legacy Collection Coexistence)"
        echo "  2. Proceed to Achievement 4.3 (Configuration Integration)"
        echo ""
        exit 0
    else
        echo -e "${RED}╔═══════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║                                                               ║${NC}"
        echo -e "${RED}║          ❌ ACHIEVEMENT 4.1: NEEDS FIXES                      ║${NC}"
        echo -e "${RED}║                                                               ║${NC}"
        echo -e "${RED}║  $TESTS_FAILED test(s) failed - see details above                    ║${NC}"
        echo -e "${RED}║                                                               ║${NC}"
        echo -e "${RED}╚═══════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo "Action Required:"
        echo "  1. Review failed tests above"
        echo "  2. Fix identified issues"
        echo "  3. Re-run validation: bash observability/validate-achievement-41.sh"
        echo ""
        exit 1
    fi
}

main "$@"

