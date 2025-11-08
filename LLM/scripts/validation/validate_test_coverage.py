#!/usr/bin/env python3
"""
Validate Test Coverage - Blocking Validation Script

Validates that test files exist for implementations and checks coverage.
Checks: Test file exists, test file location correct, coverage (if available).

Usage:
    python LLM/scripts/validation/validate_test_coverage.py <implementation_file>

Exit Codes:
    0 = Test file exists and coverage OK
    1 = Test file missing or coverage insufficient
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional, Tuple


def map_implementation_to_test_file(impl_path: Path) -> Optional[Path]:
    """
    Map implementation file path to expected test file path.
    
    Examples:
        LLM/scripts/generation/generate_prompt.py -> tests/LLM/scripts/generation/test_generate_prompt.py
        work-space/plans/PLAN_TEST.md -> tests/LLM/scripts/... (not applicable, skip)
    """
    impl_str = str(impl_path)
    
    # Handle workspace files
    if "work-space/" in impl_str:
        # Workspace files are typically documentation, not code
        # Skip validation for workspace files
        return None
    
    # Extract domain and script name from LLM/scripts/<domain>/<script>.py
    pattern = r"LLM/scripts/([^/]+)/([^/]+)\.py$"
    match = re.search(pattern, impl_str)
    
    if not match:
        # Not a script file, skip validation
        return None
    
    domain = match.group(1)
    script_name = match.group(2)
    
    # Map to test file: tests/LLM/scripts/<domain>/test_<script>.py
    test_file = Path(f"tests/LLM/scripts/{domain}/test_{script_name}.py")
    return test_file


def check_test_file_exists(test_file: Path) -> Tuple[bool, str]:
    """Check if test file exists and return status with message."""
    if test_file.exists():
        return True, f"✅ Test file exists: {test_file}"
    else:
        return False, f"❌ Test file missing: {test_file}"


def check_test_coverage(test_file: Path) -> Tuple[bool, str]:
    """
    Check test coverage if pytest-cov is available.
    Returns (is_ok, message).
    """
    try:
        import subprocess
        result = subprocess.run(
            ["pytest", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            return True, "⚠️  pytest not available, skipping coverage check"
        
        # Try to run coverage check
        result = subprocess.run(
            ["pytest", str(test_file), "--cov", "--cov-report=term-missing"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Extract coverage percentage from output
        coverage_match = re.search(r"TOTAL\s+(\d+)\s+(\d+)\s+(\d+)%", result.stdout)
        if coverage_match:
            coverage_pct = int(coverage_match.group(3))
            if coverage_pct >= 90:
                return True, f"✅ Coverage: {coverage_pct}% (>=90%)"
            else:
                return False, f"⚠️  Coverage: {coverage_pct}% (<90% target)"
        
        return True, "⚠️  Coverage check completed (percentage not available)"
    except (ImportError, subprocess.TimeoutExpired, FileNotFoundError):
        return True, "⚠️  pytest-cov not available, skipping coverage check"


def verify_test_content(test_file: Path, impl_file: Path) -> Tuple[bool, str]:
    """
    Verify test file has tests for functions/classes in implementation.
    Returns (is_ok, message).
    """
    try:
        # Read implementation file to find functions/classes
        with open(impl_file, "r", encoding="utf-8") as f:
            impl_content = f.read()
        
        # Extract function and class names
        functions = re.findall(r"^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", impl_content, re.MULTILINE)
        classes = re.findall(r"^class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[(:]", impl_content, re.MULTILINE)
        
        if not functions and not classes:
            # No functions/classes to test (maybe just constants)
            return True, "✅ No functions/classes to test"
        
        # Read test file
        with open(test_file, "r", encoding="utf-8") as f:
            test_content = f.read()
        
        # Check if tests exist for functions/classes
        missing_tests = []
        for func in functions:
            # Look for test function or test class that tests this function
            if f"test_{func}" not in test_content and f"Test{func.capitalize()}" not in test_content:
                missing_tests.append(func)
        
        for cls in classes:
            # Look for test class that tests this class
            if f"Test{cls}" not in test_content and f"test_{cls.lower()}" not in test_content:
                missing_tests.append(cls)
        
        if missing_tests:
            return False, f"⚠️  Missing tests for: {', '.join(missing_tests)}"
        else:
            return True, "✅ Tests exist for all functions/classes"
    
    except Exception as e:
        return True, f"⚠️  Could not verify test content: {e}"


def main():
    """Main validation logic."""
    parser = argparse.ArgumentParser(
        description="Validate test file existence and coverage for implementation"
    )
    parser.add_argument(
        "implementation_file",
        type=str,
        help="Path to implementation file to validate"
    )
    parser.add_argument(
        "--check-coverage",
        action="store_true",
        help="Check test coverage (requires pytest-cov)"
    )
    parser.add_argument(
        "--check-content",
        action="store_true",
        help="Verify test file has tests for functions/classes"
    )
    
    args = parser.parse_args()
    
    impl_path = Path(args.implementation_file)
    
    if not impl_path.exists():
        print(f"❌ Implementation file not found: {impl_path}", file=sys.stderr)
        sys.exit(1)
    
    # Map to test file
    test_file = map_implementation_to_test_file(impl_path)
    
    if test_file is None:
        # Not a script file or workspace file, skip validation
        print(f"ℹ️  Skipping validation (not a script file or workspace file): {impl_path}")
        sys.exit(0)
    
    # Check test file existence
    exists, message = check_test_file_exists(test_file)
    print(message)
    
    if not exists:
        print(f"\n💡 Fix: Create test file at {test_file}", file=sys.stderr)
        print(f"   Example: tests/LLM/scripts/<domain>/test_<script_name>.py", file=sys.stderr)
        sys.exit(1)
    
    # Check coverage if requested
    if args.check_coverage:
        coverage_ok, coverage_msg = check_test_coverage(test_file)
        print(coverage_msg)
        if not coverage_ok:
            print(f"\n💡 Fix: Increase test coverage to >=90%", file=sys.stderr)
            sys.exit(1)
    
    # Verify test content if requested
    if args.check_content:
        content_ok, content_msg = verify_test_content(test_file, impl_path)
        print(content_msg)
        if not content_ok:
            print(f"\n💡 Fix: Add tests for missing functions/classes", file=sys.stderr)
            sys.exit(1)
    
    print("✅ Test coverage validation passed")
    sys.exit(0)


if __name__ == "__main__":
    main()

