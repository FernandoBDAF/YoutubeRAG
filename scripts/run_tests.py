#!/usr/bin/env python3
"""
Test Runner - Run all tests in the project.

This script discovers and runs all tests in the tests/ directory using Python's
unittest framework.

Usage:
    python scripts/run_tests.py              # Run all tests
    python scripts/run_tests.py -v           # Verbose output
    python scripts/run_tests.py --module core  # Run tests for specific module
    python scripts/run_tests.py --help      # Show help

Exit Codes:
    0 - All tests passed
    1 - Some tests failed or errors occurred
"""

import sys
import os
import argparse
import unittest
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Color support
class Colors:
    """ANSI color codes for terminal output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    @staticmethod
    def is_supported() -> bool:
        """Check if terminal supports colors."""
        # Check if output is a terminal
        if not sys.stdout.isatty():
            return False
        # Check environment variables
        if os.environ.get("NO_COLOR") or os.environ.get("TERM") == "dumb":
            return False
        return True

    @staticmethod
    def colorize(text: str, color: str, use_colors: bool = None) -> str:
        """Apply color to text if colors are supported."""
        if use_colors is None:
            use_colors = Colors.is_supported()
        if use_colors:
            return f"{color}{text}{Colors.RESET}"
        return text


def _get_test_category(test_path: Path) -> str:
    """
    Determine the category of a test based on its path.

    Args:
        test_path: Path to the test file

    Returns:
        Category: 'unit', 'integration', 'scripts', or 'other'
    """
    # Convert to string and normalize
    path_str = str(test_path).replace("\\", "/")

    # Check for category patterns
    if "/tests/core/" in path_str:
        return "unit"
    elif "/tests/business/" in path_str:
        return "integration"
    elif "/tests/scripts/" in path_str:
        return "scripts"
    else:
        return "other"


def _discover_function_based_tests(
    start_dir: str, pattern: str, module: str = None, category: str = None
) -> list:
    """
    Discover function-based test files (those with if __name__ == "__main__" blocks).

    Args:
        start_dir: Directory to start discovery from
        pattern: Pattern to match test files
        module: Optional module name to filter

    Returns:
        List of test file paths (as module paths)
    """
    test_files = []
    start_path = Path(project_root) / start_dir

    if module:
        start_path = Path(project_root) / "tests" / module

    if not start_path.exists():
        return []

    # Find all test files
    for test_file in start_path.rglob(pattern):
        if not test_file.is_file():
            continue

        # Check if file has if __name__ == "__main__" pattern
        try:
            content = test_file.read_text(encoding="utf-8")
            if "__name__" in content and "__main__" in content:
                # Filter by category if specified
                if category and category != "all":
                    test_category = _get_test_category(test_file)
                    # Map category to filter
                    if category == "unit":
                        if test_category != "unit":
                            continue
                    elif category == "integration":
                        if test_category != "integration":
                            continue
                    elif category == "fast":
                        # Fast = unit tests (core library tests)
                        if test_category != "unit":
                            continue
                    # Other categories can be added here

                # Convert to module path
                rel_path = test_file.relative_to(project_root)
                module_path = (
                    str(rel_path)
                    .replace("/", ".")
                    .replace("\\", ".")
                    .replace(".py", "")
                )
                test_files.append((test_file, module_path))
        except Exception:
            # Skip files that can't be read
            continue

    return test_files


def _create_function_based_suite(test_files: list) -> unittest.TestSuite:
    """
    Create a test suite that runs function-based tests.

    Args:
        test_files: List of (file_path, module_path) tuples

    Returns:
        TestSuite with function-based test runners
    """
    suite = unittest.TestSuite()

    for test_file, module_path in test_files:
        # Create a test case that runs the test file
        test_case = _FunctionBasedTestRunner(
            module_path=module_path, test_file=test_file
        )
        suite.addTest(test_case)

    return suite


class _FunctionBasedTestRunner(unittest.TestCase):
    """Test case that runs a function-based test file."""

    def __init__(
        self, methodName="runTest", module_path: str = None, test_file: Path = None
    ):
        super().__init__(methodName)
        self.module_path = module_path
        self.test_file = test_file

    def runTest(self):
        """Run the function-based test file."""
        import subprocess
        import sys

        if not self.module_path:
            self.skipTest("No module path provided")
            return

        # Run the test file as a module
        try:
            result = subprocess.run(
                [sys.executable, "-m", self.module_path],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per test file
            )

            # Check if test passed (exit code 0)
            if result.returncode != 0:
                # Extract the actual error message from stderr or stdout
                error_output = result.stderr if result.stderr else result.stdout

                # Extract the actual test error, filtering out subprocess wrapper noise
                error_lines = error_output.split("\n")
                actual_error = []
                in_test_traceback = False

                # Find where the actual test traceback starts (after runpy wrapper)
                for i, line in enumerate(error_lines):
                    # Look for Traceback line
                    if "Traceback" in line:
                        # Start capturing from Traceback
                        actual_error.append(line)
                        in_test_traceback = True
                        continue

                    if in_test_traceback:
                        # Skip runpy/frozen lines but keep everything else
                        if '"<frozen runpy>' in line or (
                            "File" in line and "runpy" in line
                        ):
                            continue
                        # Skip lines from run_tests.py
                        if "run_tests.py" in line:
                            continue
                        # Skip "During handling" messages
                        if "During handling of the above exception" in line:
                            continue

                        # Capture all lines until AssertionError
                        actual_error.append(line)

                        # Stop after AssertionError (capture it and maybe a bit more)
                        if "AssertionError" in line:
                            # Capture next few lines if they exist (like ^ pointer)
                            for j in range(i + 1, min(len(error_lines), i + 4)):
                                next_line = error_lines[j]
                                if (
                                    next_line.strip()
                                    and "run_tests.py" not in next_line
                                ):
                                    actual_error.append(next_line)
                            break

                # If we didn't capture a good traceback, try fallback
                if (
                    not actual_error
                    or len(
                        [l for l in actual_error if l.strip() and "Traceback" not in l]
                    )
                    < 2
                ):
                    # Find AssertionError and get context around it
                    for i in range(len(error_lines) - 1, -1, -1):
                        if "AssertionError" in error_lines[i]:
                            # Get context before and after
                            start = max(0, i - 12)
                            end = min(len(error_lines), i + 4)
                            for j in range(start, end):
                                line = error_lines[j]
                                # Skip wrapper lines
                                if (
                                    "run_tests.py" not in line
                                    and "runpy" not in line
                                    and '"<frozen runpy>' not in line
                                ):
                                    if not actual_error or line not in actual_error:
                                        actual_error.append(line)
                            break

                # Clean up: remove duplicates while preserving order
                seen = set()
                cleaned = []
                for line in actual_error:
                    if line not in seen:
                        cleaned.append(line)
                        seen.add(line)
                actual_error = cleaned

                # Format the error message
                error_msg = "\n".join(actual_error).strip()
                if not error_msg:
                    # Last resort: show first meaningful lines
                    meaningful = [
                        l
                        for l in error_lines[:25]
                        if l.strip()
                        and "run_tests.py" not in l
                        and "runpy" not in l
                        and '"<frozen runpy>' not in l
                    ]
                    error_msg = "\n".join(meaningful[:15]).strip()
                if not error_msg:
                    error_msg = f"Test failed with exit code {result.returncode}"

                # Fail with the clean error message
                self.fail(error_msg)

        except subprocess.TimeoutExpired:
            # Fail the test for timeout
            self.fail(f"Test file {self.module_path} timed out after 5 minutes")
        except AssertionError:
            # Re-raise AssertionError (from self.fail()) without wrapping
            raise
        except Exception as e:
            # Other exceptions (not from self.fail())
            self.fail(f"Test file {self.module_path} raised exception: {e}")

    def __str__(self):
        return f"{self.module_path}" if self.module_path else "FunctionBasedTest"

    def shortDescription(self):
        return f"Run {self.module_path}"


def discover_test_files(start_dir: str = "tests") -> list:
    """
    Discover all test files in the tests directory.

    Args:
        start_dir: Directory to start discovery from (default: tests)

    Returns:
        List of test file paths
    """
    test_files = []
    start_path = Path(project_root) / start_dir

    if not start_path.exists():
        print(f"❌ Error: Test directory '{start_dir}' not found")
        return []

    # Find all test_*.py files
    for test_file in start_path.rglob("test_*.py"):
        if test_file.is_file():
            test_files.append(test_file)

    return sorted(test_files)


def run_tests(
    project_root: Path = None,
    start_dir: str = "tests",
    pattern: str = "test_*.py",
    verbosity: int = 1,
    module: Optional[str] = None,
    category: Optional[str] = None,
) -> Tuple[int, bool, unittest.TestResult]:
    """
    Discover and run tests.

    Args:
        project_root: The root directory of the project (defaults to script's parent).
        start_dir: The directory to start discovering tests from.
        pattern: Pattern to match test files.
        verbosity: Verbosity level for test runner.
        module: Optional module name to run tests for (e.g., 'core', 'business')
        category: Optional category to filter tests ('unit', 'integration', 'fast', 'all')

    Returns:
        Tuple of (test_count, success, result)
    """
    # Use module-level project_root if not provided
    if project_root is None:
        project_root = Path(__file__).parent.parent

    # Build test directory path
    if module:
        # Module can be like "core", "business", "scripts", or "core.base"
        test_dir = Path(project_root) / "tests" / module
        if not test_dir.exists():
            print(f"❌ Error: Test module '{module}' not found in tests/")
            result = unittest.TestResult()
            return (0, False, result)
        # Use the module path as-is for discovery (unittest expects relative to tests/)
        start_dir = f"tests/{module}"
        print(f"📁 Running tests for module: {module}")
    else:
        test_dir = Path(project_root) / start_dir
        if not test_dir.exists():
            print(f"❌ Error: Test directory '{start_dir}' not found")
            result = unittest.TestResult()
            return (0, False, result)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    try:
        # Discover and load tests using unittest discovery
        # This will find TestCase classes automatically
        # Change to project root for discovery to work correctly
        original_cwd = os.getcwd()
        os.chdir(project_root)
        try:
            discovered_suite = loader.discover(
                start_dir=start_dir,
                pattern=pattern,
                top_level_dir=str(project_root),
            )
            suite.addTest(discovered_suite)
        finally:
            os.chdir(original_cwd)

        # Filter unittest-discovered tests by category if specified
        if category and category != "all":
            # Filter the discovered suite
            filtered_suite = unittest.TestSuite()
            for test in suite:
                # Get test file path from test
                if hasattr(test, "_testMethodName"):
                    # For TestCase-based tests, get the module path
                    test_module = test.__class__.__module__
                    if test_module.startswith("tests."):
                        # Reconstruct path
                        test_path = project_root / test_module.replace(".", "/") + ".py"
                        test_category = _get_test_category(test_path)
                        # Check if category matches
                        if category == "unit" and test_category == "unit":
                            filtered_suite.addTest(test)
                        elif (
                            category == "integration" and test_category == "integration"
                        ):
                            filtered_suite.addTest(test)
                        elif category == "fast" and test_category == "unit":
                            filtered_suite.addTest(test)
                        elif category == "all":
                            filtered_suite.addTest(test)
                    else:
                        # Unknown test, include if no category filter
                        if category == "all":
                            filtered_suite.addTest(test)
                else:
                    # For test suites, recursively filter
                    if category == "all":
                        filtered_suite.addTest(test)
                    else:
                        # Try to filter sub-tests
                        for sub_test in test:
                            test_module = (
                                sub_test.__class__.__module__
                                if hasattr(sub_test, "__class__")
                                else None
                            )
                            if test_module and test_module.startswith("tests."):
                                test_path = (
                                    project_root / test_module.replace(".", "/") + ".py"
                                )
                                test_category = _get_test_category(test_path)
                                if (
                                    (category == "unit" and test_category == "unit")
                                    or (
                                        category == "integration"
                                        and test_category == "integration"
                                    )
                                    or (category == "fast" and test_category == "unit")
                                ):
                                    filtered_suite.addTest(sub_test)
                            elif category == "all":
                                filtered_suite.addTest(sub_test)
            suite = filtered_suite if (category and category != "all") else suite

        # Also discover function-based tests (tests with if __name__ == "__main__")
        # These tests can be run using python -m
        function_based_tests = _discover_function_based_tests(
            start_dir, pattern, module, category
        )
        if function_based_tests:
            # Create a custom test suite for function-based tests
            function_suite = _create_function_based_suite(function_based_tests)
            suite.addTest(function_suite)
    except Exception as e:
        print(f"❌ Error discovering tests: {e}")
        import traceback

        traceback.print_exc()
        result = unittest.TestResult()
        return (0, False, result)

    # Count tests before running
    test_count = suite.countTestCases()

    if test_count == 0:
        warning_text = Colors.colorize(
            "⚠️  Warning: No tests found", Colors.YELLOW, Colors.is_supported()
        )
        print(warning_text)
        # Create empty result object
        result = unittest.TestResult()
        return (0, True, result)

    test_count_text = Colors.colorize(
        f"🧪 Found {test_count} test(s)",
        Colors.BOLD + Colors.CYAN,
        Colors.is_supported(),
    )
    print(test_count_text)
    print("=" * 80)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity, stream=sys.stdout)
    result = runner.run(suite)

    # Return results (test_count, success, result)
    return (test_count, result.wasSuccessful(), result)


def format_summary(result, test_count: int, duration: float = None):
    """
    Format test summary output with colored formatting.

    Args:
        result: unittest.TestResult object
        test_count: Total number of tests
        duration: Optional test duration in seconds
    """
    use_colors = Colors.is_supported()

    print()
    print("=" * 80)
    summary_header = Colors.colorize(
        "📊 Test Summary", Colors.BOLD + Colors.CYAN, use_colors
    )
    print(summary_header)
    print("=" * 80)

    passed = result.testsRun - len(result.failures) - len(result.errors)
    failed = len(result.failures) + len(result.errors)
    skipped = len(result.skipped) if hasattr(result, "skipped") else 0

    # Color-coded status
    if result.wasSuccessful():
        status_icon = Colors.colorize("✅", Colors.GREEN, use_colors)
        status_text = Colors.colorize(
            "All tests passed!", Colors.GREEN + Colors.BOLD, use_colors
        )
    else:
        status_icon = Colors.colorize("❌", Colors.RED, use_colors)
        status_text = Colors.colorize(
            "Some tests failed", Colors.RED + Colors.BOLD, use_colors
        )

    print(f"{status_icon} {status_text}")
    print()

    # Test counts with colors
    tests_run_text = Colors.colorize(
        f"Tests Run: {result.testsRun}", Colors.BOLD, use_colors
    )
    print(f"   {tests_run_text}")

    passed_text = Colors.colorize(f"Passed: {passed}", Colors.GREEN, use_colors)
    print(f"   {passed_text}")

    if failed > 0:
        failed_text = Colors.colorize(f"Failed: {failed}", Colors.RED, use_colors)
        print(f"   {failed_text}")

    if skipped > 0:
        skipped_text = Colors.colorize(f"Skipped: {skipped}", Colors.YELLOW, use_colors)
        print(f"   {skipped_text}")

    if duration:
        duration_text = Colors.colorize(
            f"Duration: {duration:.2f}s", Colors.CYAN, use_colors
        )
        print(f"   {duration_text}")

    # Show failures if any (with color)
    if result.failures:
        failures_header = Colors.colorize(
            "\n❌ Failures:", Colors.RED + Colors.BOLD, use_colors
        )
        print(failures_header)
        for i, (test, traceback) in enumerate(result.failures[:5], 1):
            test_name = Colors.colorize(f"   {i}. {test}", Colors.RED, use_colors)
            print(test_name)
            # Show first few lines of error
            lines = traceback.split("\n")[:4]
            for line in lines:
                if line.strip():
                    # Highlight AssertionError lines
                    if "AssertionError" in line:
                        error_line = Colors.colorize(
                            f"     {line}", Colors.RED, use_colors
                        )
                        print(error_line)
                    else:
                        print(
                            f"     {Colors.colorize(line, Colors.YELLOW, use_colors)}"
                        )
            if i < len(result.failures[:5]):
                print()

    if result.errors:
        errors_header = Colors.colorize(
            "\n❌ Errors:", Colors.RED + Colors.BOLD, use_colors
        )
        print(errors_header)
        for i, (test, traceback) in enumerate(result.errors[:5], 1):
            test_name = Colors.colorize(f"   {i}. {test}", Colors.RED, use_colors)
            print(test_name)
            # Show first few lines of error
            lines = traceback.split("\n")[:4]
            for line in lines:
                if line.strip():
                    if "Error" in line or "Exception" in line:
                        error_line = Colors.colorize(
                            f"     {line}", Colors.RED, use_colors
                        )
                        print(error_line)
                    else:
                        print(
                            f"     {Colors.colorize(line, Colors.YELLOW, use_colors)}"
                        )
            if i < len(result.errors[:5]):
                print()

    if len(result.failures) + len(result.errors) > 5:
        remaining = len(result.failures) + len(result.errors) - 5
        remaining_text = Colors.colorize(
            f"\n   ... and {remaining} more failure(s)", Colors.YELLOW, use_colors
        )
        print(remaining_text)

    print("=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run all tests in the project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_tests.py                      # Run all tests
  python scripts/run_tests.py -v                   # Verbose output
  python scripts/run_tests.py --module core         # Run core tests only
  python scripts/run_tests.py --category unit       # Run unit tests only (core/)
  python scripts/run_tests.py --category integration # Run integration tests only (business/)
  python scripts/run_tests.py --category fast       # Run fast tests (unit tests)
        """,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output (show all test names)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Quiet output (minimal output)",
    )
    parser.add_argument(
        "--module",
        type=str,
        help="Run tests for specific module only (e.g., 'core', 'business', 'scripts')",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="test_*.py",
        help="Pattern to match test files (default: test_*.py)",
    )
    parser.add_argument(
        "--category",
        type=str,
        choices=["unit", "integration", "fast", "all"],
        default="all",
        help="Run tests by category (unit=core tests, integration=business tests, fast=unit tests, all=all tests)",
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate test coverage report (requires 'coverage' package: pip install coverage)",
    )
    parser.add_argument(
        "--coverage-threshold",
        type=float,
        default=None,
        metavar="PERCENT",
        help="Minimum coverage percentage required (0-100). Only used with --coverage",
    )

    args = parser.parse_args()

    # Set verbosity
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 2
    else:
        verbosity = 1

    # Print header
    print("=" * 80)
    print("🧪 Test Runner")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project Root: {project_root}")
    print()

    # Discover test files (for info)
    test_files = discover_test_files()
    if test_files:
        print(f"📁 Discovered {len(test_files)} test file(s)")
        if args.verbose:
            for test_file in test_files[:10]:  # Show first 10
                rel_path = test_file.relative_to(project_root)
                print(f"   - {rel_path}")
            if len(test_files) > 10:
                print(f"   ... and {len(test_files) - 10} more")
        print()

    # Check for coverage support
    coverage_available = False
    cov = None
    if args.coverage:
        try:
            import coverage

            coverage_available = True
            cov = coverage.Coverage()
            cov.start()
        except ImportError:
            use_colors = Colors.is_supported()
            warning_text = Colors.colorize(
                "⚠️  Warning: 'coverage' package not installed. Install with: pip install coverage",
                Colors.YELLOW,
                use_colors,
            )
            print(f"\n{warning_text}")
            print("   Running tests without coverage...\n")

    # Run tests
    start_time = datetime.now()
    test_count, success, result = run_tests(
        project_root,
        start_dir="tests",
        pattern=args.pattern,
        verbosity=verbosity,
        module=args.module,
        category=args.category,
    )
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Stop coverage and get report if enabled
    coverage_percentage = None
    if args.coverage and coverage_available and cov:
        cov.stop()
        cov.save()

        # Get coverage percentage
        try:
            # Use coverage's report method to get percentage
            import io
            import sys

            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            total_coverage = cov.report(
                show_missing=False, skip_covered=False, skip_empty=False
            )
            sys.stdout = old_stdout
            coverage_percentage = total_coverage

            # Display coverage summary
            use_colors = Colors.is_supported()
            print()
            coverage_header = Colors.colorize(
                "📊 Coverage Report", Colors.BOLD + Colors.CYAN, use_colors
            )
            print("=" * 80)
            print(coverage_header)
            print("=" * 80)

            if coverage_percentage is not None:
                if coverage_percentage >= 80:
                    coverage_color = Colors.GREEN
                elif coverage_percentage >= 60:
                    coverage_color = Colors.YELLOW
                else:
                    coverage_color = Colors.RED

                coverage_text = Colors.colorize(
                    f"Total Coverage: {coverage_percentage:.1f}%",
                    coverage_color + Colors.BOLD,
                    use_colors,
                )
                print(f"   {coverage_text}")

            # Check threshold if specified
            if args.coverage_threshold is not None:
                if coverage_percentage < args.coverage_threshold:
                    threshold_msg = Colors.colorize(
                        f"⚠️  Coverage {coverage_percentage:.1f}% is below threshold {args.coverage_threshold}%",
                        Colors.RED,
                        use_colors,
                    )
                    print(f"\n   {threshold_msg}")
                    success = False
                else:
                    threshold_msg = Colors.colorize(
                        f"✅ Coverage {coverage_percentage:.1f}% meets threshold {args.coverage_threshold}%",
                        Colors.GREEN,
                        use_colors,
                    )
                    print(f"\n   {threshold_msg}")

            print("=" * 80)
            print()
        except Exception as e:
            use_colors = Colors.is_supported()
            error_text = Colors.colorize(
                f"⚠️  Error generating coverage report: {e}",
                Colors.YELLOW,
                use_colors,
            )
            print(f"\n{error_text}")

    # Print duration if we have results (format_summary handles this now)
    if test_count > 0 and result:
        format_summary(result, test_count, duration)
        # Return exit code based on success
        return 0 if success else 1
    else:
        warning_text = Colors.colorize(
            "⚠️  No tests were run", Colors.YELLOW, Colors.is_supported()
        )
        print(warning_text)
        return 0


if __name__ == "__main__":
    sys.exit(main())
