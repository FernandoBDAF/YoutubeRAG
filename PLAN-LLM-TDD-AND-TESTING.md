# Plan: LLM-Driven Test-Driven Development & Testing Strategy

**Status**: Foundation Established - Planning Systematic Expansion  
**Last Updated**: November 5, 2025  
**Archive Reference**: `documentation/archive/testing-validation-nov-2025/` (to be created)

---

## 📍 Current State

### What We Built

**Ontology Testing** (Complete):
- ✅ 9 comprehensive tests for ontology features
- ✅ Direct execution pattern (no pytest dependency)
- ✅ Mock LLM client for fast execution
- ✅ All tests passing

**Testing Patterns**:
- ✅ Direct execution: `python tests/test_file.py`
- ✅ Standard assertions with clear messages
- ✅ Real data where needed, mocks where appropriate

### Current Test Coverage

**What's Tested**:
- Ontology loader
- Predicate normalization (prevents bad stems)
- Canonicalization (mapping, dropping, preserving)
- Soft-keep mechanism
- Type-pair constraints
- Symmetric relation handling

**What's NOT Tested**:
- Most business logic (agents, stages, services)
- Core libraries (retry, metrics, logging, etc.)
- Pipelines end-to-end
- Integration between components
- Error handling edge cases
- Performance characteristics

### Gaps Identified

1. **No LLM TDD Documentation**
   - No guidance on test-first development with LLMs
   - No process for preventing "running in circles"
   - No documentation pattern for iterative debugging
   - No learning capture in code comments

2. **Minimal Test Coverage**
   - Only 1 test file (ontology)
   - No tests for stages
   - No tests for agents (beyond ontology)
   - No tests for services
   - No tests for pipelines

3. **No Test Organization**
   - All tests in flat `tests/` directory
   - No clear test categories
   - No test discovery pattern
   - No test suite runner

4. **No Testing Documentation**
   - Limited testing principles
   - No test writing guide
   - No mocking guide
   - No debugging guide

---

## 🎯 Goals & Scope

### Primary Goals

1. **Establish LLM TDD Process** - Fundamental documentation and workflow
2. **Expand Test Coverage** - All agents, stages, services, libraries
3. **Create Testing Tools** - Test runners, mocking utilities, assertion helpers
4. **Document Best Practices** - Comprehensive testing guide
5. **Prevent Circular Debugging** - Structured iteration and learning capture

### Out of Scope

- 100% code coverage (target: 70-80% for critical paths)
- Integration testing with external services (mock them)
- Load testing (separate performance testing plan)

---

## 📋 Implementation Plan

### Phase 1: LLM TDD Foundation Documentation

**Goal**: Create fundamental documentation to guide all future development

#### 1.1 LLM Test-Driven Development Guide

**Document**: `documentation/guides/LLM-TDD-WORKFLOW.md` (NEW)

**Contents**:

```markdown
# LLM-Driven Test-Driven Development Workflow

## Core Principles

1. **Test First** - Always write tests before implementation
2. **Never Cheat Tests** - Modify tests only if they're wrong, not to pass
3. **Document Iterations** - Track each attempt and what was learned
4. **Learn from Failures** - Each failure should teach something new
5. **Comment Learnings** - Add lessons to code as comments
6. **Prevent Circles** - Check if you're making progress or repeating

---

## The LLM TDD Cycle

### Step 1: Define Goal (5-10 minutes)

**Create**: `[FEATURE]-PLAN.md` in root

**Contents**:
- What we're building (one paragraph)
- Why we're building it (problem statement)
- Success criteria (declarative, testable)
- Implementation approach (high-level)
- Risks and unknowns

**Template**:
```markdown
# Plan: [Feature Name]

## Goal
[One paragraph - what we're building]

## Problem
[What problem this solves]

## Success Criteria
- [ ] Criterion 1 (testable)
- [ ] Criterion 2 (testable)
- [ ] Criterion 3 (testable)

## Implementation Approach
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Risks
- [Risk 1] → [Mitigation]
- [Risk 2] → [Mitigation]
```

---

### Step 2: Write Tests (20-30 minutes)

**Create**: `tests/test_[feature].py`

**Test Structure**:
```python
\"\"\"
Tests for [Feature].

Tests cover:
- [Aspect 1]
- [Aspect 2]
- [Aspect 3]

Run with: python tests/test_[feature].py
\"\"\"

def test_basic_functionality():
    \"\"\"Test that [feature] works for simple case.\"\"\"
    # Setup
    # Execute
    # Assert
    print("✓ Basic functionality works")

def test_edge_case_1():
    \"\"\"Test that [feature] handles [edge case].\"\"\"
    # ...
    print("✓ Edge case 1 handled")

# ... more tests ...

def run_all_tests():
    \"\"\"Run all tests and report results.\"\"\"
    print(f"Testing [Feature]")
    print("=" * 60)
    
    try:
        test_basic_functionality()
        test_edge_case_1()
        # ... call all tests ...
        print("\\n" + "=" * 60)
        print("✓ All tests passed!")
    except AssertionError as e:
        print(f"\\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()
```

**Key Principles**:
- Tests are declarative (define expected behavior)
- Tests are independent (can run in any order)
- Tests have clear assertions with failure messages
- Tests print progress (✓ for pass, ❌ for fail)

---

### Step 3: Implement to Pass Tests (iterative)

**Process**:

1. **Run tests** → See failures
2. **Analyze failure** → Understand what's wrong
3. **Implement fix** → Make minimal change
4. **Run tests** → See if fixed or new error
5. **Document iteration** → Update iteration log

**Iteration Documentation** (keep in root during development):

`[FEATURE]-ITERATION-LOG.md`:
```markdown
# [Feature] Implementation Iterations

## Iteration 1
**Date**: [timestamp]
**Test Run**: Failed on test_basic_functionality
**Error**: AssertionError: Expected X, got Y
**Analysis**: [Why it failed]
**Fix Applied**: [What we changed]
**Learning**: [What we learned]
**Code Comments Added**: Yes/No

## Iteration 2
**Test Run**: Failed on test_edge_case_1
**Error**: [New error]
**Analysis**: [Why it failed]
**Fix Applied**: [What we changed]
**Learning**: [What we learned]
**Progress Check**: ✓ Moving forward (new error, not repeating)

## Iteration 3
**Test Run**: All tests passed
**Final Changes**: [Summary]
**Total Iterations**: 3
**Lessons Learned**:
1. [Lesson 1]
2. [Lesson 2]
**Archive**: Yes (feature complete)
```

**Critical Check**: After each iteration, verify:
- ✅ **New Error** - Making progress (different error than before)
- ❌ **Same Error** - Running in circles (stop, analyze, change strategy)

---

### Step 4: Document Learnings in Code

**Pattern**:
```python
def complex_function(data):
    \"\"\"
    Process data with special handling for edge cases.
    
    IMPLEMENTATION NOTE (from testing):
    - Initially tried approach X, but failed because Y
    - Switched to approach Z which handles edge case A
    - Special case B requires explicit check at line X
    
    Args:
        data: Input data
        
    Returns:
        Processed result
        
    Raises:
        ValueError: If data invalid (learned from iteration 2)
    \"\"\"
    
    # LEARNED: Must validate before processing (test_edge_case_1)
    if not data or not data.get("required_field"):
        raise ValueError("Data must have required_field")
    
    # LEARNED: Special handling for case B (test_edge_case_2)
    if data.get("type") == "special":
        return handle_special_case(data)
    
    # Normal processing
    return process_normal(data)
```

**Key**: Capture WHY decisions were made, what was learned through iteration

---

### Step 5: Complete and Archive

**When feature complete**:
1. All tests passing
2. Code commented with learnings
3. Iteration log complete
4. Create completion document

**Create**: `[FEATURE]-COMPLETE.md`

```markdown
# [Feature] Implementation Complete

**Date**: [date]
**Duration**: [X hours]
**Iterations**: [X]
**Status**: ✅ Complete

## Summary
[What was built, why, how]

## Key Learnings
1. [Learning 1]
2. [Learning 2]
3. [Learning 3]

## Test Coverage
- [X] tests created
- All passing
- Coverage: [aspects covered]

## Code Changes
**Files Modified**: [list]
**Files Created**: [list]
**Lines Changed**: ~[X]

## Archive
- Move `[FEATURE]-PLAN.md` → `archive/[theme]/planning/`
- Move `[FEATURE]-ITERATION-LOG.md` → `archive/[theme]/implementation/`
- Move `[FEATURE]-COMPLETE.md` → `archive/[theme]/summaries/`
- Tests remain in `tests/` (permanent)

## References
- Tests: `tests/test_[feature].py`
- Code: [file paths]
- Docs: [documentation paths]
```

---

## Preventing "Running in Circles"

### The Problem

**Symptoms**:
- Same error appears 3+ times in iteration log
- No new learnings in recent iterations
- Trying random changes without understanding
- Test modifications to make them pass (cheating)

### The Solution

#### 1. Error Tracking

**After each iteration**, check:
```
Current error == Previous error?
  ✅ NO  → Making progress, continue
  ❌ YES → Check previous iteration
    Current error == Previous-2 error?
      ✅ NO  → Might be oscillating, review approach
      ❌ YES → STOP! Running in circles
```

**If running in circles**:
1. STOP implementing
2. Create `[FEATURE]-CIRCULAR-DEBUG.md`
3. Document:
   - All errors encountered
   - All fixes attempted
   - Why each fix failed
   - What's the common pattern?
4. Change strategy fundamentally
5. Request human guidance if needed

#### 2. Learning Capture

**After each iteration**, document:
- What was the error?
- Why did it happen? (root cause)
- What did we learn? (generalizable insight)
- How does this inform next iteration?

**Red flag**: If "learning" section is empty or generic, you're not learning

#### 3. Strategy Review

**Every 3 iterations**, review:
- Are we making progress toward goal?
- Are errors getting simpler or more complex?
- Do we understand the system better?
- Should we change approach?

#### 4. Test Integrity

**NEVER**:
- Modify test to make it pass (unless test is genuinely wrong)
- Remove assertions that fail
- Add mocks that bypass the actual logic
- Change test expectations without understanding why

**ALWAYS**:
- Understand why test fails
- Fix the implementation, not the test
- If test is wrong, document WHY it's wrong before changing
- Keep test expectations strict

---

## LLM TDD Best Practices

### 1. Start Simple

**Bad**: Write 20 tests for all edge cases
**Good**: Write 1-2 tests for happy path, iterate

### 2. One Change at a Time

**Bad**: Modify 5 files in one iteration
**Good**: Change one thing, run tests, see result

### 3. Understand Before Fixing

**Bad**: "Let's try changing this line"
**Good**: "The error happens because X, so we need to Y"

### 4. Comment Learnings

**Bad**: Fix silently, move on
**Good**: Add comment explaining what you learned and why this fix works

### 5. Check for Patterns

**Bad**: Treat each error as unique
**Good**: Look for patterns across errors, fix root cause

---

## Testing Patterns

### Pattern 1: Direct Execution Tests

**When**: Testing pure functions, classes, agents

**Structure**:
```python
def test_function():
    # Clear test name and description
    result = function(input)
    assert result == expected, f"Clear message with values: {result} != {expected}"
    print("✓ Test name")

if __name__ == "__main__":
    run_all_tests()
```

### Pattern 2: Mock External Dependencies

**When**: Testing code that calls LLMs, databases, APIs

**Pattern**:
```python
from unittest.mock import MagicMock

def test_with_mock_llm():
    # Create mock
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    
    # Use mock
    agent = Agent(llm_client=mock_client)
    result = agent.process(data)
    
    # Assert
    assert result is not None
    print("✓ Test with mock")
```

### Pattern 3: Integration Tests

**When**: Testing interactions between components

**Pattern**:
```python
def test_integration():
    # Setup real dependencies
    db = get_test_database()
    
    # Execute workflow
    stage1.process(data)
    stage2.process(data)
    
    # Assert final state
    result = db.find_one({"id": test_id})
    assert result["status"] == "complete"
    
    # Cleanup
    db.drop()
    print("✓ Integration test")
```

---

## Implementation Plan

### Phase 1: LLM TDD Documentation

**Goal**: Create comprehensive guide for LLM-assisted test-driven development

#### 1.1 Create LLM TDD Guide

**Document**: `documentation/guides/LLM-TDD-WORKFLOW.md` (NEW)

**Sections**:
1. Core Principles
2. The LLM TDD Cycle (detailed)
3. Preventing Running in Circles
4. Learning Capture Patterns
5. Test Integrity Rules
6. Best Practices
7. Common Pitfalls
8. Real Examples

**Implementation**:
- [ ] Create comprehensive guide (based on template above)
- [ ] Include real examples from ontology testing
- [ ] Add troubleshooting section
- [ ] Include iteration log templates
- [ ] Test with new feature development

#### 1.2 Create Iteration Log Template

**Document**: `documentation/templates/ITERATION-LOG-TEMPLATE.md` (NEW)

**Template**:
```markdown
# [Feature] Implementation Iterations

**Start Date**: [date]
**Status**: In Progress / Complete
**Total Iterations**: [X]

---

## Iteration 1
**Date**: [timestamp]
**Test Run**: [which tests ran]
**Result**: Pass/Fail
**Error**: [error message if failed]
**Analysis**: [why it failed - root cause]
**Fix Applied**: [what changed - file and line numbers]
**Learning**: [generalizable insight]
**Code Comments**: [Yes/No - learnings added to code]
**Progress**: [New error / Same error / Tests passed]

---

[Repeat for each iteration]

---

## Final Summary

**Total Iterations**: [X]
**Time Spent**: [hours]
**Key Learnings**:
1. [Learning 1]
2. [Learning 2]
3. [Learning 3]

**Mistakes Made**:
1. [Mistake 1] → [How we recovered]
2. [Mistake 2] → [How we recovered]

**Best Practices Discovered**:
1. [Practice 1]
2. [Practice 2]

---

**Archive**: `documentation/archive/[theme]-[date]/implementation/`
```

**Implementation**:
- [ ] Create template
- [ ] Add to `documentation/templates/`
- [ ] Document usage in LLM TDD guide
- [ ] Use for next feature

#### 1.3 Create Circular Debug Template

**Document**: `documentation/templates/CIRCULAR-DEBUG-TEMPLATE.md` (NEW)

**Template**:
```markdown
# [Feature] Circular Debugging Analysis

**Date**: [date]
**Symptom**: Same error after [X] iterations
**Status**: Analyzing / Resolved

---

## Error Pattern

**Error Message**: [exact error]

**Iterations Where This Error Appeared**:
- Iteration [X]: [what we tried]
- Iteration [Y]: [what we tried]
- Iteration [Z]: [what we tried]

---

## Attempted Fixes

### Fix 1 (Iteration [X])
**Approach**: [what we tried]
**Rationale**: [why we thought it would work]
**Result**: [why it didn't work]

### Fix 2 (Iteration [Y])
**Approach**: [what we tried]
**Rationale**: [why we thought it would work]
**Result**: [why it didn't work]

---

## Pattern Analysis

**Common Factor**: [what's common across all attempts]
**What We're Missing**: [what we don't understand]
**Why We're Stuck**: [diagnosis]

---

## Strategy Change

**Old Strategy**: [what we were doing]
**New Strategy**: [fundamentally different approach]
**Rationale**: [why this should work]

---

## Resolution

**Iteration [X]**: [how it was finally resolved]
**Key Insight**: [what we learned]
**Why Previous Attempts Failed**: [retrospective analysis]

---

## Lessons for Future

1. [How to recognize this pattern earlier]
2. [How to avoid this trap]
3. [Better approaches for similar problems]

---

**Archive**: After resolution
```

**Implementation**:
- [ ] Create template
- [ ] Add to templates directory
- [ ] Document when to use
- [ ] Test with next circular debugging scenario

#### 1.4 Update Testing Principles Documentation

**Document**: `documentation/technical/TESTING.md` (UPDATE)

**Add Sections**:
- LLM TDD workflow overview
- Test-first philosophy
- Preventing circular debugging
- Learning capture in code
- When to modify tests vs implementation
- Real examples from ontology testing

**Implementation**:
- [ ] Review existing TESTING.md
- [ ] Add LLM TDD section
- [ ] Include ontology testing as case study
- [ ] Add troubleshooting section
- [ ] Cross-reference LLM-TDD-WORKFLOW.md

---

### Phase 2: Test Coverage Expansion

**Goal**: Expand test coverage to all critical components

#### 2.1 Agent Tests

**Priority**: High (agents contain core business logic)

**Tests to Create**:

1. **`tests/test_entity_resolution_agent.py`**:
   - Test entity grouping logic
   - Test canonical name selection
   - Test type resolution
   - Test edge cases (empty groups, all same confidence)
   - Est: 8-10 tests

2. **`tests/test_graph_construction_agent.py`**:
   - Test relationship type generation
   - Test similarity calculations
   - Test cross-chunk links
   - Test bidirectional relationships
   - Est: 10-12 tests

3. **`tests/test_community_detection_agent.py`**:
   - Test Louvain algorithm execution
   - Test resolution parameter effects
   - Test cluster size constraints
   - Test empty graph handling
   - Est: 8-10 tests

4. **`tests/test_community_summarization_agent.py`**:
   - Test summary generation
   - Test token estimation
   - Test truncation logic
   - Test model switching (if applicable)
   - Est: 6-8 tests

**Implementation** (per agent):
- [ ] Create plan document
- [ ] Write tests (test-first)
- [ ] Run tests (expect failures)
- [ ] Implement fixes iteratively
- [ ] Document iterations
- [ ] Capture learnings in code comments
- [ ] Archive plan and iteration log

#### 2.2 Stage Tests

**Priority**: Medium (stages orchestrate agents, less logic)

**Tests to Create**:

1. **`tests/test_extraction_stage.py`**:
   - Test batch processing
   - Test concurrent execution
   - Test statistics tracking
   - Test error handling

2. **`tests/test_entity_resolution_stage.py`**:
   - Test stage orchestration
   - Test statistics aggregation
   - Test error handling

3. **`tests/test_graph_construction_stage.py`**:
   - Test batch insert operations
   - Test statistics tracking
   - Test error handling

4. **`tests/test_community_detection_stage.py`**:
   - Test single execution guarantee
   - Test batch update logic
   - Test statistics tracking

**Implementation**: Follow same LLM TDD cycle for each

#### 2.3 Library Tests

**Priority**: High (libraries are foundational)

**Tests to Create**:

1. **`tests/core/test_concurrency_library.py`**:
   - Test TPM processor
   - Test rate limiter
   - Test concurrent executor
   - Test thread safety
   - Est: 15-20 tests

2. **`tests/core/test_retry_library.py`**:
   - Test retry decorators
   - Test backoff strategies
   - Test quota error detection
   - Test max attempts
   - Est: 10-12 tests

3. **`tests/core/test_metrics_library.py`**:
   - Test counter, gauge, histogram
   - Test metric registration
   - Test metric export
   - Est: 8-10 tests

4. **`tests/core/test_error_handling_library.py`**:
   - Test error classes
   - Test error context
   - Test error logging
   - Est: 8-10 tests

**Implementation**: Follow LLM TDD cycle for each library

#### 2.4 Service Tests

**Priority**: Medium (services orchestrate stages)

**Tests to Create**:

1. **`tests/business/test_graphrag_services.py`**:
   - Test query processing
   - Test index creation
   - Test collections management

2. **`tests/business/test_rag_services.py`**:
   - Test retrieval logic
   - Test ranking
   - Test hybrid retrieval (if applicable)

**Implementation**: Follow LLM TDD cycle

---

### Phase 3: Test Infrastructure & Tools

**Goal**: Create tools to make testing easier and more effective

#### 3.1 Test Utilities Library

**Module**: `tests/utils/` (NEW)

**Components**:

1. **`mock_factories.py`**:
   - Factory functions for mock LLM clients
   - Factory functions for mock databases
   - Factory functions for test data
   
```python
# tests/utils/mock_factories.py

def create_mock_llm_client(responses=None):
    \"\"\"Create mock OpenAI client with predefined responses.\"\"\"
    mock = MagicMock(spec=OpenAI)
    # Setup nested structure
    # ...
    return mock

def create_test_chunk(chunk_id="test_1", text="Test text"):
    \"\"\"Create test chunk with standard structure.\"\"\"
    return {
        "chunk_id": chunk_id,
        "chunk_text": text,
        # ... standard fields
    }

def create_test_entity(name="Test", entity_type=EntityType.CONCEPT):
    \"\"\"Create test entity.\"\"\"
    return EntityModel(name=name, type=entity_type, ...)
```

2. **`assertions.py`**:
   - Custom assertion helpers
   - Better error messages

```python
# tests/utils/assertions.py

def assert_dict_contains(actual, expected_subset):
    \"\"\"Assert dict contains expected keys with values.\"\"\"
    for key, value in expected_subset.items():
        assert key in actual, f"Missing key: {key}"
        assert actual[key] == value, f"Key {key}: expected {value}, got {actual[key]}"

def assert_entity_equal(entity1, entity2, ignore_confidence=False):
    \"\"\"Assert two entities are equal (with optional field ignoring).\"\"\"
    # Custom comparison logic
```

3. **`test_database.py`**:
   - Test database creation and cleanup
   - Fixture-like behavior

```python
# tests/utils/test_database.py

class TestDatabase:
    \"\"\"Context manager for test databases.\"\"\"
    
    def __enter__(self):
        self.db = create_test_db()
        return self.db
    
    def __exit__(self, *args):
        cleanup_test_db(self.db)
```

**Implementation**:
- [ ] Create `tests/utils/` directory
- [ ] Implement mock factories
- [ ] Implement assertion helpers
- [ ] Implement test database utilities
- [ ] Document usage
- [ ] Use in all new tests

#### 3.2 Test Runner

**Goal**: Run all tests with single command

**Script**: `scripts/run_all_tests.py`

```python
\"\"\"
Run all tests in the project.

Usage:
    python scripts/run_all_tests.py
    python scripts/run_all_tests.py --pattern "test_ontology*"
    python scripts/run_all_tests.py --verbose
\"\"\"
```

**Features**:
- Discover all test files
- Run in order or parallel
- Aggregate results
- Generate report
- Exit code for CI/CD

**Implementation**:
- [ ] Create test runner script
- [ ] Implement test discovery
- [ ] Add parallel execution option
- [ ] Generate summary report
- [ ] Test with current tests
- [ ] Document usage

#### 3.3 Test Coverage Analyzer

**Goal**: Measure test coverage

**Script**: `scripts/analyze_test_coverage.py`

```python
\"\"\"
Analyze test coverage across the codebase.

Usage:
    python scripts/analyze_test_coverage.py --output coverage_report.md
\"\"\"
```

**Metrics**:
- Files with tests vs without
- Functions/classes with tests
- Critical paths tested
- Edge cases covered

**Implementation**:
- [ ] Create coverage analyzer
- [ ] Scan codebase for testable units
- [ ] Match with existing tests
- [ ] Generate coverage report
- [ ] Identify gaps
- [ ] Prioritize untested critical code

---

### Phase 4: Testing Documentation

**Goal**: Comprehensive testing documentation

#### 4.1 Testing Guide

**Document**: `documentation/guides/TESTING-GUIDE.md` (NEW)

**Contents**:
- How to write tests
- How to run tests
- How to debug test failures
- Mocking strategies
- Assertion patterns
- When to test what
- Performance testing
- Integration testing

**Implementation**:
- [ ] Create guide
- [ ] Include examples from ontology tests
- [ ] Add mocking examples
- [ ] Add troubleshooting section
- [ ] Cross-reference LLM TDD guide

#### 4.2 Testing Reference

**Document**: `documentation/reference/TESTING-REFERENCE.md` (NEW)

**Contents**:
- All test utilities API
- Mock factories API
- Assertion helpers API
- Test database API
- Environment setup
- CI/CD integration

**Implementation**:
- [ ] Create reference document
- [ ] Document all test utilities
- [ ] Include code examples
- [ ] Keep updated as utilities expand

---

## 🔍 Identified Gaps & Solutions

### Gap 1: No CI/CD Integration

**Problem**: Tests run manually, not automatically on commits

**Solution**:
- [ ] Create GitHub Actions workflow
- [ ] Run all tests on PR
- [ ] Run all tests on push to main
- [ ] Fail build if tests fail
- [ ] Document CI setup

### Gap 2: No Test Data Management

**Problem**: No standard test datasets, each test creates own data

**Solution**:
- [ ] Create `tests/fixtures/` directory
- [ ] Standard test chunks
- [ ] Standard test entities
- [ ] Standard test relationships
- [ ] Load fixtures in tests
- [ ] Document fixture usage

### Gap 3: No Performance Testing

**Problem**: Don't test performance characteristics

**Solution**:
- [ ] Create `tests/performance/` directory
- [ ] Performance benchmarks for critical paths
- [ ] Measure throughput, latency
- [ ] Track over time
- [ ] Alert on regressions

### Gap 4: No Test for Production Issues

**Problem**: Production bugs not captured as tests

**Solution**:
- [ ] When bug found in production → create test first
- [ ] Test reproduces bug
- [ ] Fix bug
- [ ] Test passes
- [ ] Document in BUGS.md with test reference

---

## 📊 Success Criteria

### Phase 1 Complete When:
- ✅ LLM TDD guide created and comprehensive
- ✅ Iteration log template created
- ✅ Circular debug template created
- ✅ Team trained on LLM TDD workflow

### Phase 2 Complete When:
- ✅ 50+ tests created (from current ~9)
- ✅ All agents tested
- ✅ All critical libraries tested
- ✅ Coverage > 70% for critical paths

### Phase 3 Complete When:
- ✅ Test utilities library created
- ✅ Test runner working
- ✅ Coverage analyzer created
- ✅ All tools documented

### Phase 4 Complete When:
- ✅ Testing guide complete
- ✅ Testing reference complete
- ✅ All patterns documented
- ✅ Examples provided

---

## ⏱️ Time Estimates

**Phase 1** (Documentation): 4-6 hours  
**Phase 2** (Test Expansion): 20-30 hours (depends on number of tests)  
**Phase 3** (Tools): 6-8 hours  
**Phase 4** (Documentation): 4-6 hours

**Total**: 34-50 hours

---

## 🚀 Immediate Next Steps

1. **Archive old documentation** - Execute archiving plan
2. **Create LLM TDD guide** - Foundation for all future work
3. **Create templates** - Iteration log, circular debug
4. **Start test expansion** - Pick first agent, follow LLM TDD
5. **Document learnings** - Update guide as we learn

---

## 📚 References

**Archive** (post-archiving):
- `documentation/archive/testing-validation-nov-2025/`

**Current Docs**:
- `documentation/technical/TESTING.md` (to be updated)
- `documentation/guides/TESTING-GUIDE.md` (to be created)
- `documentation/guides/LLM-TDD-WORKFLOW.md` (to be created)

**Code**:
- `tests/test_ontology_extraction.py` - Example of good testing
- `tests/utils/` (to be created) - Test utilities

**Templates**:
- `documentation/templates/ITERATION-LOG-TEMPLATE.md` (to be created)
- `documentation/templates/CIRCULAR-DEBUG-TEMPLATE.md` (to be created)

---

**Status**: Ready for execution after archiving  
**Priority**: CRITICAL - Foundation for all future development with LLMs

