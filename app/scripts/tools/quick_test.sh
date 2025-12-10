#!/bin/bash
#
# Quick Test Runner - Fast feedback for specific modules
#
# Usage:
#   ./app/scripts/tools/quick_test.sh <module>
#   ./app/scripts/tools/quick_test.sh core
#   ./app/scripts/tools/quick_test.sh business
#   ./app/scripts/tools/quick_test.sh scripts
#
# This script provides a convenient shortcut to run tests for specific modules
# using the main test runner (tests/run_tests.py).

set -e  # Exit on error

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Navigate up from app/scripts/tools to project root
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

# Check if module argument provided
if [ $# -eq 0 ]; then
    echo "❌ Error: Module name required"
    echo ""
    echo "Usage: $0 <module>"
    echo ""
    echo "Examples:"
    echo "  $0 core        # Run core module tests"
    echo "  $0 business    # Run business module tests"
    echo "  $0 scripts     # Run scripts module tests"
    echo ""
    echo "Available modules:"
    ls -d tests/*/ 2>/dev/null | sed 's|tests/||' | sed 's|/$||' | sed 's/^/  - /' || echo "  (check tests/ directory)"
    exit 1
fi

MODULE="$1"

# Run tests using main test runner
python "$PROJECT_ROOT/tests/run_tests.py" --module "$MODULE"

# Exit with same code as test runner
exit $?

