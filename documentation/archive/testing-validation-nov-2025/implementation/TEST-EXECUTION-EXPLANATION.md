# Test Execution Explanation

**Question**: "If pytest is not installed, how did we previously run those tests?"

---

## Answer: Tests Support Both pytest and Direct Execution

### Previous Test Execution Pattern

Based on codebase analysis, tests in this project follow a **dual-mode pattern**:

1. **Primary**: Use `pytest` if available (standard testing framework)
2. **Fallback**: Direct execution via `if __name__ == "__main__"` blocks

### Evidence from Codebase

#### Example 1: `tests/core/libraries/metrics/test_cost_models.py`
```python
def run_all_tests():
    """Run all cost model tests."""
    test_estimate_cost_known_model()
    test_estimate_cost_partial_match()
    # ... etc

if __name__ == "__main__":
    run_all_tests()  # Direct execution
```

#### Example 2: `tests/core/base/test_stage.py`
```python
def run_all_tests():
    """Run all BaseStage integration tests."""
    test_stage_successful_execution()
    test_stage_handles_document_errors()
    # ... etc

if __name__ == "__main__":
    run_all_tests()  # Direct execution
```

#### Example 3: `tests/core/libraries/serialization/test_converters.py`
```python
if __name__ == "__main__":
    run_all_tests()  # Direct execution pattern
```

### Documentation Evidence

From `documentation/archive/observability-nov-2025/summaries/TIER2-TESTING-PROGRESS.md`:

> **"All tests use direct execution (no pytest dependency)"**
> 
> **"Simple Test Pattern - Direct execution works great, no pytest needed"**

---

## How Tests Were Run Previously

### Method 1: Direct Execution (No pytest required)
```bash
# Run individual test files
python tests/core/libraries/metrics/test_cost_models.py
python tests/core/base/test_stage.py
python tests/test_ontology_extraction.py
```

### Method 2: As Python Modules
```bash
# Run as module (if __main__ block exists)
python -m tests.core.libraries.metrics.test_cost_models
python -m tests.core.base.test_stage
```

### Method 3: With pytest (if installed)
```bash
# If pytest is available
python -m pytest tests/test_ontology_extraction.py -v
```

---

## Why This Pattern?

### Benefits:

1. **No External Dependencies**: Tests work without installing pytest
2. **Simple Execution**: Just run the Python file directly
3. **Flexible**: Can use pytest if available, but not required
4. **Quick Feedback**: Fast iteration without setup overhead

### Project Philosophy:

From the documentation:
- Tests should be **simple and accessible**
- **No complex setup required**
- **Direct execution works great**

---

## Current Test File Status

### `tests/test_ontology_extraction.py`

**Original**: Required pytest
```python
import pytest
# ...
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Updated**: Now supports both modes
```python
# Try to import pytest, but allow tests to run without it
try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False
    # Create mock pytest.skip for compatibility

# ...
if __name__ == "__main__":
    if HAS_PYTEST:
        pytest.main([__file__, "-v"])
    else:
        # Direct execution fallback
        run_all_tests()
```

---

## How to Run Tests Now

### Option 1: Direct Execution (No pytest needed)
```bash
python tests/test_ontology_extraction.py
```

### Option 2: With pytest (if installed)
```bash
pip install pytest  # Install if needed
python -m pytest tests/test_ontology_extraction.py -v
```

### Option 3: As Module (if supported)
```bash
python -m tests.test_ontology_extraction
```

---

## Test Coverage Verification

All 11 tests in `tests/test_ontology_extraction.py` cover:

1. ✅ **Predicate Normalization** (2 tests)
   - Prevents bad stems
   - Handles short words

2. ✅ **Canonicalization** (4 tests)
   - Mapping from predicate_map
   - __DROP__ predicates
   - Canonical predicates kept
   - Soft-keep mechanism

3. ✅ **Type Pair Constraints** (2 tests)
   - Allowed pairs pass
   - Violations rejected

4. ✅ **Symmetric Predicates** (2 tests)
   - Endpoint sorting
   - Non-symmetric unchanged

5. ✅ **Ontology Loader** (1 test)
   - Structure validation

---

## Summary

**Answer**: Tests were run using **direct execution** pattern (`python tests/file.py`), not pytest. The project follows a pattern where tests can run directly without pytest, but pytest is optional if available.

**Current Status**: `tests/test_ontology_extraction.py` has been updated to support both:
- ✅ Direct execution (no pytest needed)
- ✅ pytest execution (if installed)

**Verification**: Run `python tests/test_ontology_extraction.py` to verify all tests pass.

---

**Pattern**: This matches the project's testing philosophy - simple, accessible tests that work without complex setup.

