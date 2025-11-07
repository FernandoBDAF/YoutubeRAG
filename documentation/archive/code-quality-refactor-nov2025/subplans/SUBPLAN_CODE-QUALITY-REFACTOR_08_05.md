# SUBPLAN: Achievement 8.5 - Automated Code Formatting and Validation Tools

**Parent Plan**: PLAN_CODE-QUALITY-REFACTOR.md  
**Achievement**: 8.5 - Automated Code Formatting and Validation Tools  
**Priority**: 8 (Code Quality Improvements)  
**Status**: ⏳ Not Started  
**Estimated Effort**: 3-5 hours

---

## 🎯 Goal

Set up automatic code formatting (similar to Prettier for JavaScript) and validation tools with git hooks to enforce code standards automatically on commit/push.

---

## 📋 Objectives

1. Configure Black (Python code formatter) for automatic formatting
2. Configure isort (import sorter) for consistent import organization
3. Set up pre-commit hooks to run checks automatically
4. Configure git hooks to validate code standards before push
5. Document setup and usage for developers

---

## 🛠️ Tools to Configure

### 1. Black (Code Formatter)

**Purpose**: Automatic code formatting (like Prettier for Python)

**Configuration**: `pyproject.toml`

```toml
[tool.black]
line-length = 100
target-version = ['py39']
include = '\.pyi?$'
extend-exclude = '''
/(
  \.git
  | __pycache__
  | \.venv
  | \.eggs
  | \.mypy_cache
)/
'''
```

**Usage**:

- Format all code: `black .`
- Check formatting: `black --check .`
- Format specific file: `black path/to/file.py`

---

### 2. isort (Import Sorter)

**Purpose**: Organize and sort imports consistently

**Configuration**: `pyproject.toml`

```toml
[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
skip_glob = ["*/migrations/*", "*/__pycache__/*"]
```

**Usage**:

- Sort imports: `isort .`
- Check imports: `isort --check-only .`

---

### 3. Pre-Commit Hooks

**Purpose**: Run checks automatically before git commit

**Configuration**: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.10.0
    hooks:
      - id: black
        language_version: python3.9
        args: [--line-length=100]

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black, --line-length=100]

  - repo: https://github.com/pycqa/pylint
    rev: v3.0.0
    hooks:
      - id: pylint
        args: [--fail-under=8.0]
        additional_dependencies: [pylint]

  - repo: local
    hooks:
      - id: validate-imports
        name: Validate Python Imports
        entry: python scripts/validate_imports.py
        language: system
        pass_filenames: false
        always_run: true

      - id: validate-metrics
        name: Validate Metrics Registration
        entry: python scripts/validate_metrics.py
        language: system
        pass_filenames: false
        always_run: false

      - id: run-tests
        name: Run Test Suite
        entry: python scripts/run_tests.py
        language: system
        pass_filenames: false
        always_run: false # Too slow for every commit
```

**Setup**:

```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type pre-push  # Also run on push
```

---

### 4. Git Hooks (Pre-Push Validation)

**Purpose**: Enforce code standards before push to remote

**Create**: `.githooks/pre-push`

```bash
#!/bin/bash
# Git pre-push hook to validate code standards

set -e

echo "🔍 Running pre-push validation..."

# Run Black check
echo "📝 Checking code formatting..."
black --check . || {
    echo "❌ Code formatting check failed. Run 'black .' to fix."
    exit 1
}

# Run isort check
echo "📦 Checking import organization..."
isort --check-only . || {
    echo "❌ Import organization check failed. Run 'isort .' to fix."
    exit 1
}

# Run pylint (if configured)
if command -v pylint &> /dev/null; then
    echo "🔍 Running linter..."
    pylint business app core --fail-under=8.0 || {
        echo "⚠️  Linter warnings found (not blocking)"
    }
fi

# Run import validation
echo "✅ Validating imports..."
python scripts/validate_imports.py business app core || {
    echo "❌ Import validation failed."
    exit 1
}

echo "✅ All pre-push checks passed!"
exit 0
```

**Setup**:

```bash
chmod +x .githooks/pre-push
git config core.hooksPath .githooks
```

---

## 📝 Implementation Steps

### Step 1: Create Configuration Files (30 min)

1. Create/update `pyproject.toml` with Black and isort config
2. Create `.pre-commit-config.yaml` with hooks
3. Create `.githooks/pre-push` script

### Step 2: Install Tools (15 min)

```bash
pip install black isort pre-commit
```

### Step 3: Format Existing Code (30-60 min)

```bash
# Format all code
black .
isort .

# Verify no changes needed
black --check .
isort --check-only .
```

### Step 4: Set Up Git Hooks (15 min)

```bash
# Install pre-commit hooks
pre-commit install
pre-commit install --hook-type pre-push

# Set up custom git hooks directory
git config core.hooksPath .githooks
chmod +x .githooks/pre-push
```

### Step 5: Test Hooks (15 min)

```bash
# Test pre-commit
pre-commit run --all-files

# Test pre-push (manually)
.git/hooks/pre-push  # or .githooks/pre-push
```

### Step 6: Update Documentation (30 min)

1. Update `QUALITY-GATES.md` with new tools
2. Create `CONTRIBUTING.md` or update existing docs
3. Document developer workflow

---

## ✅ Success Criteria

- [ ] Black configured and formatting code consistently
- [ ] isort configured and organizing imports
- [ ] Pre-commit hooks installed and working
- [ ] Pre-push hooks validate code standards
- [ ] All existing code formatted (no diff after running formatters)
- [ ] Documentation updated with setup instructions
- [ ] Developers can run `black .` and `isort .` successfully

---

## 📊 Expected Impact

**Before**:

- Manual code formatting
- Inconsistent import organization
- Code standards enforced only in PR reviews
- Easy to push code that doesn't meet standards

**After**:

- Automatic formatting on save/commit
- Consistent code style across codebase
- Standards enforced automatically
- Faster code reviews (less style discussion)

---

## 🚀 Next Steps

1. Create `pyproject.toml` with Black/isort config
2. Create `.pre-commit-config.yaml`
3. Create `.githooks/pre-push` script
4. Install and test tools
5. Format existing codebase
6. Update documentation

---

**Status**: Ready for implementation
