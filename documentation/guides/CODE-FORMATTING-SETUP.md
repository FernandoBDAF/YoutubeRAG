# Code Formatting and Validation Setup

**Created**: November 6, 2025  
**Achievement**: 8.5 - Automated Code Formatting and Validation Tools  
**Purpose**: Guide for developers on using automated code formatting tools

---

## 📋 Overview

This project uses automated code formatting and validation tools to maintain consistent code quality:

- **Black**: Automatic code formatter (like Prettier for Python)
- **isort**: Import statement organizer
- **Pre-commit hooks**: Automatic checks before git commit
- **Git hooks**: Validation before push

---

## 🚀 Quick Start

### 1. Install Tools

```bash
pip install black isort pre-commit
```

Or add to `requirements.txt`:
```
black>=24.1.1
isort>=5.13.2
pre-commit>=3.5.0
```

### 2. Install Pre-Commit Hooks

```bash
pre-commit install
pre-commit install --hook-type pre-push
```

### 3. Set Up Git Hooks

```bash
git config core.hooksPath .githooks
```

---

## 📝 Usage

### Format Code Automatically

**Format all code:**
```bash
black .
```

**Format specific file:**
```bash
black path/to/file.py
```

**Check formatting (don't modify):**
```bash
black --check .
```

### Organize Imports

**Sort imports:**
```bash
isort .
```

**Sort specific file:**
```bash
isort path/to/file.py
```

**Check imports (don't modify):**
```bash
isort --check-only .
```

### Run All Checks

**Before committing:**
```bash
pre-commit run --all-files
```

---

## ⚙️ Configuration

### Black Configuration

Located in `pyproject.toml`:
- Line length: 100 characters
- Target Python version: 3.9+
- Excludes: `__pycache__`, `.venv`, `.git`, etc.

### isort Configuration

Located in `pyproject.toml`:
- Profile: `black` (compatible with Black)
- Line length: 100 characters
- Known first-party: `core`, `business`, `app`, `dependencies`

### Pre-Commit Hooks

Located in `.pre-commit-config.yaml`:
- Black formatting check
- isort import organization
- Import validation (via `scripts/validate_imports.py`)
- Pylint (on push only, not every commit)

### Git Hooks

Located in `.githooks/pre-push`:
- Black formatting check
- isort import organization
- Import validation

---

## 🔄 Workflow

### Recommended Workflow

1. **Make changes** to code
2. **Format code** before committing:
   ```bash
   black .
   isort .
   ```
3. **Commit** (pre-commit hooks will run automatically)
4. **Push** (pre-push hooks will validate)

### If Hooks Fail

If pre-commit or pre-push hooks fail:

1. **Fix formatting:**
   ```bash
   black .
   isort .
   ```

2. **Fix import errors:**
   ```bash
   python scripts/validate_imports.py
   ```

3. **Re-commit/push**

### Bypassing Hooks (Not Recommended)

**Skip pre-commit:**
```bash
git commit --no-verify
```

**Skip pre-push:**
```bash
git push --no-verify
```

⚠️ **Warning**: Only bypass hooks in emergencies. Code quality standards should be maintained.

---

## 🛠️ Troubleshooting

### Black Not Found

```bash
pip install black
```

### isort Not Found

```bash
pip install isort
```

### Pre-Commit Not Working

```bash
pre-commit install --overwrite
```

### Git Hooks Not Running

```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-push
```

### Import Validation Fails

Check that `scripts/validate_imports.py` exists and is executable:
```bash
python scripts/validate_imports.py --help
```

---

## 📚 Additional Resources

- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Pre-commit Documentation](https://pre-commit.com/)

---

## ✅ Success Criteria

After setup, you should be able to:

- ✅ Run `black .` without errors
- ✅ Run `isort .` without errors
- ✅ Commit code (pre-commit hooks run automatically)
- ✅ Push code (pre-push hooks validate automatically)
- ✅ All code formatted consistently

---

**Status**: ✅ Complete - Ready for use


