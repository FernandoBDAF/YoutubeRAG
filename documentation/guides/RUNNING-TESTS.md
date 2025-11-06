# Running Tests

**Last Updated**: 2025-11-06 18:50 UTC  
**Purpose**: Guide for running tests in the project

---

## Quick Start

### Run All Tests

```bash
python scripts/run_tests.py
```

### Run Tests for Specific Module

```bash
# Using quick test runner (recommended)
./scripts/quick_test.sh core
./scripts/quick_test.sh business
./scripts/quick_test.sh scripts

# Or using main test runner
python scripts/run_tests.py --module core
python scripts/run_tests.py --module business
python scripts/run_tests.py --module scripts
```

---

## Pre-commit Hook (Optional)

You can optionally set up a pre-commit hook to run fast tests automatically before each commit.

### Installation

```bash
# Copy the hook script to .git/hooks/
cp scripts/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Usage

Once installed, the hook will automatically run fast tests before each commit:

```bash
git commit -m "Your commit message"
# Hook runs: python scripts/run_tests.py --category fast
```

### Skipping the Hook

To skip the hook (not recommended):

```bash
git commit --no-verify -m "Your commit message"
```

### What It Does

- Runs fast tests (`--category fast`) before commit
- Blocks commit if tests fail
- Provides clear feedback on test status

**Note**: This is optional. The hook runs fast tests only for quick feedback. Always run the full test suite before pushing.

---

## Test Runner Scripts

### Main Test Runner: `scripts/run_tests.py`

The main test runner script discovers and runs all tests in the project.

**Usage**:

```bash
# Run all tests
python scripts/run_tests.py

# Run with verbose output
python scripts/run_tests.py -v

# Run with quiet output
python scripts/run_tests.py -q

# Run tests for specific module
python scripts/run_tests.py --module <module>

# Show help
python scripts/run_tests.py --help
```

**Options**:

- `-v, --verbose`: Verbose output (show all test names)
- `-q, --quiet`: Quiet output (minimal output)
- `--module MODULE`: Run tests for specific module only (e.g., 'core', 'business', 'scripts')
- `--pattern PATTERN`: Pattern to match test files (default: test\_\*.py)

**Exit Codes**:

- `0`: All tests passed
- `1`: Some tests failed or errors occurred

### Quick Test Runner: `scripts/quick_test.sh`

A convenient shortcut for running tests for specific modules during development.

**Usage**:

```bash
# Run tests for core module
./scripts/quick_test.sh core

# Run tests for business module
./scripts/quick_test.sh business

# Run tests for scripts module
./scripts/quick_test.sh scripts

# Show available modules (if no argument provided)
./scripts/quick_test.sh
```

**Benefits**:

- Fast execution for quick feedback
- Simple command to remember
- Lists available modules when help is needed

---

## Test Organization

Tests are organized in the `tests/` directory by domain:

```
tests/
├── core/          # Core functionality tests
├── business/      # Business logic tests
├── scripts/       # Script tests
└── ...            # Other test directories
```

### Available Modules

- `core`: Core functionality and libraries
- `business`: Business logic and agents
- `scripts`: Test scripts and utilities
- (Check `tests/` directory for other modules)

---

## Test Types

The project uses a mix of test types:

### TestCase-Based Tests

These are discovered automatically by `unittest.discover()`:

- Tests using `unittest.TestCase` classes
- Discovered by test runner automatically
- Run with `python scripts/run_tests.py`

### Function-Based Tests

Some tests use function-based style (not TestCase classes):

- **Automatically discovered** by test runner (tests with `if __name__ == "__main__"` blocks)
- Can also be run directly: `python -m tests.module.path`
- Example: `python -m tests.core.libraries.metrics.test_cost_models`
- Test runner executes them via subprocess and reports results

---

## Output Format

### Normal Output

```
================================================================================
🧪 Test Runner
================================================================================
Started: 2025-11-06 01:30:00
Project Root: /path/to/project

📁 Discovered 27 test file(s)

🧪 Found 150 test(s)
================================================================================
[Test execution output]
================================================================================
📊 Test Summary
================================================================================
✅ Tests Run: 150
   Passed: 150
   Duration: 12.34s
================================================================================

✅ All tests passed!
```

### Verbose Output (`-v`)

Shows individual test names as they run:

```
test_estimate_cost_known_model ... ok
test_estimate_cost_partial_match ... ok
...
```

### Quiet Output (`-q`)

Minimal output, only summary:

```
📊 Test Summary
✅ Tests Run: 150
   Passed: 150
```

---

## Common Patterns

### During Development

For fast feedback during development:

```bash
# Run tests for module you're working on
./scripts/quick_test.sh core

# Or run specific test file directly
python -m tests.core.libraries.metrics.test_cost_models
```

### Before Committing

Run all tests to ensure nothing broke:

```bash
python scripts/run_tests.py
```

### CI/CD Integration

The test runner exits with appropriate codes for CI/CD:

```bash
# In CI/CD pipeline
python scripts/run_tests.py
if [ $? -ne 0 ]; then
    echo "Tests failed!"
    exit 1
fi
```

---

## Troubleshooting

### No Tests Found

If you see "⚠️ Warning: No tests found":

1. Check that test files follow naming convention: `test_*.py`
2. Ensure test files contain `unittest.TestCase` classes (for automatic discovery)
3. For function-based tests, run directly: `python -m tests.module.path`

### Import Errors

If tests fail with import errors:

1. Ensure you're running from project root
2. Check that all dependencies are installed
3. Verify Python path includes project root

### Module Not Found

If you see "❌ Error: Test module 'X' not found":

1. Check that module exists in `tests/` directory
2. List available modules: `./scripts/quick_test.sh` (no arguments)
3. Verify module name spelling

---

## Best Practices

1. **Run Tests Frequently**: Use quick test runner during development
2. **Run All Tests Before Committing**: Ensure no regressions
3. **Use Verbose Mode for Debugging**: `-v` flag shows individual test names
4. **Check Exit Codes**: Important for CI/CD integration
5. **Run Function-Based Tests Manually**: If needed, use `python -m` directly

---

## Future Enhancements

Potential improvements for the test runner:

- Support for function-based test discovery
- Parallel test execution for speed
- Test coverage reporting
- Watch mode for continuous testing
- Test result caching

---

## Related Documentation

- Test organization: See `tests/` directory structure
- Test writing: See existing test files for examples
- CI/CD: Exit codes suitable for pipeline integration

---

**Quick Reference**:

```bash
# All tests
python scripts/run_tests.py

# Quick module test
./scripts/quick_test.sh <module>

# Verbose
python scripts/run_tests.py -v

# Help
python scripts/run_tests.py --help
```
