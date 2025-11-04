# Test Coverage Review & Future Opportunities

**Date**: November 3, 2025  
**Current**: 5 test files in tests/ folder  
**Purpose**: Review existing tests, identify gaps

---

## ✅ Tests Created & Kept (In tests/ Folder)

### 1. `tests/core/libraries/error_handling/test_exceptions.py` ✅

**Coverage**:

- ApplicationError basic, with context, with cause
- All specialized exceptions (StageError, AgentError, etc.)
- wrap_exception() helper
- add_context() method
- Empty cause message handling

**Lines**: 192  
**Tests**: 9 test functions  
**Status**: Comprehensive ✅  
**Keep**: YES

---

### 2. `tests/core/libraries/metrics/test_collectors.py` ✅

**Coverage**:

- Counter (increment, labels, reset)
- Gauge (set, inc, dec)
- Histogram (observe, summary, percentiles)
- Timer (context manager, elapsed)
- Label handling across all types

**Lines**: 124  
**Tests**: 5 test functions  
**Status**: Good coverage ✅  
**Keep**: YES

---

### 3. `tests/core/libraries/metrics/test_cost_models.py` ✅

**Coverage**:

- Known model cost estimation
- Partial model name matching
- Unknown model fallback
- Custom pricing addition
- Realistic 13k run cost calculation

**Lines**: 91  
**Tests**: 5 test functions  
**Status**: Comprehensive ✅  
**Keep**: YES

---

### 4. `tests/core/libraries/metrics/test_integration.py` ✅

**Coverage**:

- log_exception() auto-tracks metrics
- Prometheus export includes errors

**Lines**: ~80  
**Tests**: 2 test functions  
**Status**: Good for integration ✅  
**Keep**: YES

---

### 5. `tests/core/libraries/retry/test_retry.py` ✅

**Coverage**:

- Successful on first try
- Retry until success
- Max retries exceeded
- Exponential backoff timing
- Fixed delay
- Retry on specific exceptions only
- LLM retry decorator

**Lines**: 162  
**Tests**: 7 test functions  
**Status**: Comprehensive ✅  
**Keep**: YES

---

## ❌ Tests NOT Created (Ad-Hoc Validation Only)

**During implementation, I did quick validation with**:

```python
python -c "from X import Y; test(); print('works')"
```

**These were throwaway validation, NOT kept as tests**:

- Import verification tests
- Quick smoke tests
- One-off functionality checks

**This was appropriate for quick iteration!**

---

## 📋 Test Gaps Identified

### Gap 1: Error Handling Decorators ⚠️

**Missing Tests**:

- `@handle_errors` decorator behavior
- `@handle_stage_errors` decorator
- Fallback value handling
- reraise vs. suppress behavior

**Should Add**: `tests/core/libraries/error_handling/test_decorators.py`

**Effort**: 1 hour  
**Priority**: Medium (decorators are used, but not explicitly tested)

---

### Gap 2: Error Handling Context Managers ⚠️

**Missing Tests**:

- `error_context` manager
- `stage_context` manager
- `agent_context` manager
- Exception enrichment behavior

**Should Add**: `tests/core/libraries/error_handling/test_context.py`

**Effort**: 1 hour  
**Priority**: Medium

---

### Gap 3: Logging Library ⚠️

**Missing Tests**:

- setup_logging() behavior
- log_context propagation
- Formatters (JSON, Colored)
- log*operation*\*() functions
- log_exception() (tested in metrics/test_integration, but should have dedicated tests)

**Should Add**: `tests/core/libraries/logging/test_logging.py`

**Effort**: 1-2 hours  
**Priority**: Medium-High

---

### Gap 4: Registry & Exporters ⚠️

**Missing Tests**:

- MetricRegistry singleton behavior
- Registry.register/get/collect_all
- export_prometheus_text() output format
- Prometheus text format validation

**Should Add**: `tests/core/libraries/metrics/test_registry.py`  
**Should Add**: `tests/core/libraries/metrics/test_exporters.py`

**Effort**: 1 hour  
**Priority**: Medium

---

### Gap 5: BaseStage & BaseAgent Integration ⚠️

**Missing Tests**:

- BaseStage with libraries (error handling, metrics, retry)
- BaseAgent with libraries
- Metrics actually collected during stage.run()
- Error handling actually works in stage.run()

**Should Add**:

- `tests/core/base/test_stage.py`
- `tests/core/base/test_agent.py`

**Effort**: 2-3 hours  
**Priority**: HIGH (these are critical integration points)

---

### Gap 6: Pipeline Integration

**Missing Tests**:

- Pipeline runner with enhanced error handling
- GraphRAG pipeline end-to-end
- Metrics collected during full pipeline

**Should Add**:

- `tests/business/pipelines/test_runner.py`
- `tests/business/pipelines/test_graphrag_pipeline.py`

**Effort**: 2-3 hours  
**Priority**: HIGH

---

## 🎯 Test Strategy Going Forward

### Immediate (This Week):

**Add Critical Integration Tests** (5-6 hours):

1. BaseStage integration tests (2 hrs)
2. BaseAgent integration tests (2 hrs)
3. Pipeline integration tests (1-2 hrs)

**These validate that libraries actually work in real code!**

---

### Short-Term (Next Week):

**Fill Library Test Gaps** (4-5 hours):

1. Error handling decorators (1 hr)
2. Error handling context (1 hr)
3. Logging library (1-2 hrs)
4. Registry & exporters (1 hr)

---

### Medium-Term (Month 1):

**Component Tests** (during code review):

- Test each agent after refactoring
- Test each service after refactoring
- Test each stage after refactoring

**Approach**: Add tests as we refactor each file

---

## 📊 Current Test Coverage

**Libraries**:

- error_handling/exceptions: ✅ Excellent
- error_handling/decorators: ⚠️ Missing
- error_handling/context: ⚠️ Missing
- logging/\*: ⚠️ Missing
- metrics/collectors: ✅ Good
- metrics/cost_models: ✅ Excellent
- metrics/integration: ✅ Good
- metrics/registry: ⚠️ Missing
- metrics/exporters: ⚠️ Missing
- retry/\*: ✅ Excellent

**Integration**:

- Base classes: ⚠️ Missing
- Pipelines: ⚠️ Missing

**Components**:

- Agents: ❌ None
- Stages: ❌ None
- Services: ❌ None

---

## 🎯 Testing Principles Established

### ✅ Good Practices (Continue):

1. **Tests in tests/ folder** - Mirror source structure
2. **Comprehensive test functions** - Cover edge cases
3. **Clear assertions** - Verify behavior
4. **Good naming** - test_feature_does_what()
5. **Runnable** - python -m tests.path.to.test

### ❌ Avoid (Was doing during dev):

1. Ad-hoc python -c tests - Use proper test files
2. Tests in library folders - Use tests/ folder
3. One-off validation - Write reusable tests

---

## 📋 Test Creation Workflow

**When Building a Library**:

1. Create library code
2. **Create test file in tests/** (not ad-hoc!)
3. Write comprehensive tests
4. Run tests: `python -m tests.core.libraries.X.test_Y`
5. Verify all pass
6. Document in this file

**When Refactoring Code**:

1. Review existing code
2. Identify patterns
3. Apply library
4. **Add integration test**
5. Verify behavior unchanged

---

## 🎊 Next Testing Priorities

**Critical** (Add This Week):

1. BaseStage integration tests (2 hrs)
2. BaseAgent integration tests (2 hrs)
3. Pipeline integration tests (1-2 hrs)

**Important** (Add Next Week): 4. Error handling decorator tests (1 hr) 5. Logging library tests (1-2 hrs) 6. Registry/exporter tests (1 hr)

**Ongoing** (During Refactor): 7. Component tests as we refactor each file

---

**Summary**:

- ✅ 5 solid test files created (keep all!)
- ⚠️ 6 test gaps identified (add soon)
- 📋 Clear testing strategy going forward
- 🎯 Priority: Integration tests for base classes

**Should we add the critical integration tests now (4-5 hours) or continue with agent refactoring?**
