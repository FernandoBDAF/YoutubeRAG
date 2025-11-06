# CI/CD Integration

**Last Updated**: 2025-11-06 19:25 UTC  
**Purpose**: Guide for integrating the test runner into CI/CD pipelines

---

## 🚀 Quick Start

### GitHub Actions

The project includes an example GitHub Actions workflow at `.github/workflows/tests.yml`.

**Basic Usage**:

```yaml
- name: Run tests
  run: python scripts/run_tests.py
```

**With Coverage**:

```yaml
- name: Run tests with coverage
  run: python scripts/run_tests.py --coverage
```

---

## 📋 GitHub Actions Example

### Basic Workflow

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python scripts/run_tests.py
```

### Advanced Workflow

```yaml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install coverage

      - name: Run all tests
        run: python scripts/run_tests.py

      - name: Run tests with coverage
        run: python scripts/run_tests.py --coverage --coverage-threshold 70
```

---

## 🔧 Other CI Systems

### GitLab CI

```yaml
test:
  image: python:3.12
  script:
    - pip install -r requirements.txt
    - python scripts/run_tests.py
```

### CircleCI

```yaml
jobs:
  test:
    docker:
      - image: python:3.12
    steps:
      - checkout
      - run: pip install -r requirements.txt
      - run: python scripts/run_tests.py
```

### Jenkins

```groovy
pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'python scripts/run_tests.py'
            }
        }
    }
}
```

---

## 📊 Test Categories in CI

### Run Fast Tests First

```yaml
- name: Run fast tests (unit tests)
  run: python scripts/run_tests.py --category fast

- name: Run full test suite
  run: python scripts/run_tests.py
```

### Parallel Test Execution

```yaml
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: python scripts/run_tests.py --category unit

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: python scripts/run_tests.py --category integration
```

---

## ✅ Best Practices

1. **Exit Codes**: Test runner returns proper exit codes (0 for success, 1 for failure)

   - CI systems automatically detect failures
   - No need for manual exit code checking

2. **Coverage Reporting**: Use `--coverage` for coverage metrics

   - Set threshold with `--coverage-threshold`
   - Useful for quality gates

3. **Fast Feedback**: Run fast tests first for quick feedback

   - Use `--category fast` for unit tests
   - Fail fast on critical issues

4. **Verbose Output**: Use `-v` for detailed output in CI logs
   - Helps debug failures
   - Shows which tests are running

---

**Last Updated**: 2025-11-06 19:25 UTC
