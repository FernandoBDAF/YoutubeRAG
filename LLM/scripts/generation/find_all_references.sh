#!/bin/bash
# Comprehensive reference finder for function extraction
# Created: 2025-11-12
# Achievement: 2.4 - Lesson learned from incomplete import updates
#
# PURPOSE: Find ALL references to a function being extracted to ensure
#          complete import chain updates (not just top-level imports)
#
# USAGE: ./find_all_references.sh <function_name>
#
# WHAT IT FINDS:
# 1. Import statements (from X import Y)
# 2. Direct function calls (function_name())
# 3. Test mocks (@patch decorators)

if [ -z "$1" ]; then
    echo "❌ Error: Missing function name"
    echo ""
    echo "Usage: $0 <function_name>"
    echo ""
    echo "Example:"
    echo "  $0 parse_plan_file"
    echo "  $0 copy_to_clipboard_safe"
    exit 1
fi

FUNCTION_NAME="$1"

echo "🔍 Finding ALL references to: ${FUNCTION_NAME}"
echo ""
echo "============================================================"

# 1. Find import statements
echo "1️⃣  IMPORT STATEMENTS:"
echo "------------------------------------------------------------"
IMPORTS=$(grep -rn "from .* import.*${FUNCTION_NAME}" --include="*.py" . \
    2>/dev/null | grep -v ".pyc" | grep -v "__pycache__" | grep -v ".venv")

if [ -z "$IMPORTS" ]; then
    echo "   (none found)"
else
    echo "$IMPORTS"
fi

echo ""

# 2. Find direct function calls (the ones often missed!)
echo "2️⃣  DIRECT FUNCTION CALLS:"
echo "------------------------------------------------------------"
CALLS=$(grep -rn "${FUNCTION_NAME}\(" --include="*.py" . \
    2>/dev/null | grep -v ".pyc" | grep -v "__pycache__" | grep -v ".venv" \
    | grep -v "def ${FUNCTION_NAME}" | grep -v "# .*${FUNCTION_NAME}")

if [ -z "$CALLS" ]; then
    echo "   (none found)"
else
    echo "$CALLS"
fi

echo ""

# 3. Find test mocks (also often missed!)
echo "3️⃣  TEST MOCKS (@patch decorators):"
echo "------------------------------------------------------------"
MOCKS=$(grep -rn "patch.*${FUNCTION_NAME}" --include="*.py" . \
    2>/dev/null | grep -v ".pyc" | grep -v "__pycache__" | grep -v ".venv")

if [ -z "$MOCKS" ]; then
    echo "   (none found)"
else
    echo "$MOCKS"
fi

echo ""
echo "============================================================"

# Count total references
if [ -z "$IMPORTS" ]; then
    IMPORT_COUNT=0
else
    IMPORT_COUNT=$(echo "$IMPORTS" | grep -c ":")
fi

if [ -z "$CALLS" ]; then
    CALL_COUNT=0
else
    CALL_COUNT=$(echo "$CALLS" | grep -c ":")
fi

if [ -z "$MOCKS" ]; then
    MOCK_COUNT=0
else
    MOCK_COUNT=$(echo "$MOCKS" | grep -c ":")
fi

TOTAL=$((IMPORT_COUNT + CALL_COUNT + MOCK_COUNT))

echo ""
echo "📊 SUMMARY:"
echo "   Import statements: ${IMPORT_COUNT}"
echo "   Direct calls:      ${CALL_COUNT}"
echo "   Test mocks:        ${MOCK_COUNT}"
echo "   ─────────────────"
echo "   TOTAL REFERENCES:  ${TOTAL}"
echo ""

if [ $TOTAL -eq 0 ]; then
    echo "✅ No references found - function may not exist or already moved"
else
    echo "⚠️  Found ${TOTAL} references that need updating!"
    echo ""
    echo "📋 CHECKLIST:"
    echo "   [ ] Review each reference above"
    echo "   [ ] Update all imports to new module"
    echo "   [ ] Update all direct calls (use instance if now a method)"
    echo "   [ ] Update all test mocks to new module path"
    echo "   [ ] Run tests after updates"
    echo "   [ ] Test end-to-end (interactive mode, CLI)"
    echo ""
    echo "💡 TIP: Save this output for systematic updates"
fi

echo ""

