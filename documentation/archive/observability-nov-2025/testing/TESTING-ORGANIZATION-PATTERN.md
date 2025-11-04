# Testing Organization Pattern

**Date**: November 2, 2025  
**Issue**: Created test inside library folder, but we have a `tests/` folder  
**Goal**: Establish clear, consistent testing pattern

---

## 🤔 Current Situation

### What We Have:

```
tests/                                   # Created during refactor
├── app/
├── business/
├── core/
└── dependencies/

core/libraries/error_handling/
├── exceptions.py
└── test_exceptions.py                   # ❌ Test inside library!
```

**Inconsistency**: Test is in library folder, not in `tests/` folder

---

## 📋 Options Analysis

### Option 1: Tests in `tests/` Folder (Mirror Structure) ⭐ RECOMMENDED

**Structure**:

```
tests/
├── core/
│   ├── libraries/
│   │   ├── error_handling/
│   │   │   └── test_exceptions.py
│   │   ├── logging/
│   │   │   └── test_logging.py
│   │   └── metrics/
│   │       └── test_metrics.py
│   ├── models/
│   │   └── test_graphrag_models.py
│   └── base/
│       ├── test_stage.py
│       └── test_agent.py
├── business/
│   ├── agents/
│   │   └── graphrag/
│   │       └── test_extraction_agent.py
│   └── stages/
│       └── graphrag/
│           └── test_extraction_stage.py
└── ...

core/libraries/error_handling/
├── exceptions.py                        # Production code only
├── decorators.py
└── __init__.py
```

**Pros**:

- ✅ Standard Python/pytest convention
- ✅ Clean separation (production vs. test)
- ✅ Easy to exclude from production builds
- ✅ Clear test discovery (pytest auto-finds tests/)
- ✅ Mirrors source structure (easy to find tests)

**Cons**:

- ⚠️ Tests physically separate from code (slightly less convenient)

**This is the standard industry practice** ✅

---

### Option 2: Tests Inside Modules

**Structure**:

```
core/libraries/error_handling/
├── exceptions.py
├── test_exceptions.py                   # Test next to code
├── decorators.py
└── test_decorators.py
```

**Pros**:

- ✅ Tests close to code
- ✅ Easy to find related test

**Cons**:

- ❌ Mixes production and test code
- ❌ Need to exclude from production
- ❌ Not standard convention
- ❌ Harder pytest configuration

**Not recommended**

---

### Option 3: Hybrid Approach

**Structure**:

```
tests/                                   # Unit tests
├── core/
└── business/

core/libraries/error_handling/
└── integration_tests.py                 # Integration tests only
```

**Pros**:

- ✅ Unit tests separate
- ✅ Integration tests near code

**Cons**:

- ⚠️ Inconsistent (two test locations)
- ⚠️ Confusing pattern

**Not recommended**

---

## 🎯 Recommended Pattern: Option 1

### Structure:

```
tests/                                   # ALL tests go here
├── __init__.py
├── conftest.py                          # Shared fixtures
│
├── core/                                # Core layer tests
│   ├── __init__.py
│   ├── libraries/                       # Library tests
│   │   ├── __init__.py
│   │   ├── error_handling/
│   │   │   ├── __init__.py
│   │   │   ├── test_exceptions.py
│   │   │   ├── test_decorators.py
│   │   │   └── test_context.py
│   │   ├── logging/
│   │   │   └── test_logging.py
│   │   └── metrics/
│   │       └── test_metrics.py
│   ├── models/
│   │   ├── test_graphrag_models.py
│   │   └── test_config.py
│   ├── base/
│   │   ├── test_stage.py
│   │   └── test_agent.py
│   └── domain/
│       ├── test_text.py
│       └── test_enrichment.py
│
├── business/                            # Business layer tests
│   ├── agents/
│   │   ├── graphrag/
│   │   │   ├── test_extraction_agent.py
│   │   │   └── ...
│   │   └── ingestion/
│   │       └── test_clean_agent.py
│   ├── stages/
│   │   ├── graphrag/
│   │   │   └── test_extraction_stage.py
│   │   └── ingestion/
│   │       └── test_clean_stage.py
│   ├── pipelines/
│   │   ├── test_runner.py
│   │   └── test_graphrag_pipeline.py
│   └── services/
│       └── ...
│
├── dependencies/                        # Dependencies layer tests
│   ├── database/
│   │   └── test_mongodb.py
│   ├── llm/
│   │   └── test_openai.py
│   └── observability/
│       └── test_logging.py
│
└── app/                                 # App layer tests
    ├── cli/
    │   ├── test_main.py
    │   └── test_graphrag.py
    └── scripts/
        └── test_scripts.py
```

---

## 🔧 Test Organization Principles

### 1. Mirror Source Structure

```
Source: core/libraries/error_handling/exceptions.py
Test:   tests/core/libraries/error_handling/test_exceptions.py
```

### 2. Test File Naming

- Prefix with `test_` (pytest convention)
- Name matches source file: `exceptions.py` → `test_exceptions.py`

### 3. Test Discovery

```bash
# Run all tests
pytest tests/

# Run specific layer
pytest tests/core/

# Run specific library
pytest tests/core/libraries/error_handling/

# Run specific file
pytest tests/core/libraries/error_handling/test_exceptions.py
```

### 4. Shared Fixtures

```python
# tests/conftest.py
# Shared fixtures for all tests
@pytest.fixture
def mock_mongodb():
    ...

@pytest.fixture
def mock_llm_client():
    ...
```

---

## ✅ Correction Needed

### Move Test File:

```bash
# From:
core/libraries/error_handling/test_exceptions.py

# To:
tests/core/libraries/error_handling/test_exceptions.py
```

**This establishes the pattern for ALL future tests**

---

## 📋 Testing Strategy (For Future Reference)

### Unit Tests (tests/core/, tests/business/)

- Test individual functions/classes
- Mock all external dependencies
- Fast, isolated

### Integration Tests (tests/business/)

- Test multiple components together
- Real database (test DB)
- Real LLM calls (mocked or rate-limited)

### End-to-End Tests (tests/app/)

- Test full workflows
- Real CLI commands
- Verify complete behavior

---

## 🎯 Proposed Action

**Move the test file I created**:

```bash
mkdir -p tests/core/libraries/error_handling
mv core/libraries/error_handling/test_exceptions.py tests/core/libraries/error_handling/
touch tests/core/libraries/__init__.py
touch tests/core/libraries/error_handling/__init__.py
```

**Establish pattern**: All future tests go in `tests/` with mirrored structure

**Would you like me to:**

1. **Move the test file now** to establish the pattern?
2. **Create a pytest configuration** (pytest.ini, conftest.py)?
3. **Continue with Phase 2A** and we'll organize tests later?

**My recommendation**: Move it now (2 minutes) to establish the correct pattern from the start! 🎯
