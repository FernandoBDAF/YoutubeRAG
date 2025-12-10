# Development Tools

Convenience scripts for development workflow.

## Scripts

### `quick_test.sh`

Quick test runner for rapid feedback during development.

**Usage:**
```bash
./tools/quick_test.sh
```

**What it does:**
1. Runs linting checks
2. Executes unit tests for recently changed files
3. Validates imports

## Git Hooks

Git hooks are located in `.git-hooks/` directory.

### Setup

Configure git to use custom hooks:
```bash
git config core.hooksPath .git-hooks
```

### `pre-commit`

Runs before each commit to ensure code quality.

**Checks performed:**
1. Python import validation
2. Error handling audit
3. Metrics validation
4. Basic linting

**Skip hook (not recommended):**
```bash
git commit --no-verify
```

## Adding New Tools

1. Add script to `tools/` directory
2. Make executable: `chmod +x tools/script.sh`
3. Document in this README

