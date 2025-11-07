# Code Review Methodology for Library Extraction and Quality Improvement

**Purpose**: Systematic approach for reviewing code domains to identify library extraction opportunities and code quality improvements  
**Created**: November 6, 2025  
**Status**: Active - Use for all domain reviews in PLAN_CODE-QUALITY-REFACTOR.md  
**Version**: 1.0

---

## 🎯 Overview

This methodology provides a structured, repeatable process for:
1. **Identifying common patterns** that can be extracted into libraries
2. **Finding code quality issues** that need improvement
3. **Prioritizing improvements** based on impact and effort
4. **Documenting findings** consistently across all domains

**When to Use**: For every domain review in PLAN_CODE-QUALITY-REFACTOR.md (GraphRAG, Ingestion, RAG, Chat, Core Infrastructure)

---

## 📋 Review Process

### Step 1: Preparation (15-30 minutes)

**Before starting a domain review**:

1. **Understand the Domain**
   - Read domain documentation (if exists)
   - Review recent changes (check ACTIVE_PLANS.md for paused plans)
   - Understand domain's purpose and responsibilities

2. **Inventory Files**
   - List all files in the domain (agents, stages, services, queries)
   - Note file sizes and complexity
   - Identify dependencies

3. **Set Up Tracking**
   - Create findings document using template (below)
   - Prepare to track patterns, issues, and opportunities

---

### Step 2: File-by-File Review (2-4 hours per domain)

**For each file in the domain**:

#### 2.1 Initial Scan (5-10 minutes per file)

**Read the file completely** and note:
- **Purpose**: What does this file do?
- **Size**: Lines of code, number of functions/classes
- **Complexity**: Deeply nested? Many responsibilities?
- **Dependencies**: What does it import? What does it depend on?

#### 2.2 Pattern Identification (10-15 minutes per file)

**Look for these common patterns** (use checklist below):

**A. Error Handling Patterns**
- [ ] Try-except blocks (how are errors handled?)
- [ ] Custom exceptions (are they used consistently?)
- [ ] Error logging (is it informative?)
- [ ] Error context (is context captured?)

**B. LLM Call Patterns**
- [ ] LLM client initialization
- [ ] Prompt construction
- [ ] Response parsing
- [ ] Retry logic
- [ ] Structured output handling

**C. Database Operation Patterns**
- [ ] MongoDB connection/access
- [ ] Query construction
- [ ] Batch operations
- [ ] Transaction handling
- [ ] Error handling for DB operations

**D. Validation Patterns**
- [ ] Input validation
- [ ] Output validation
- [ ] Schema validation
- [ ] Type checking

**E. Configuration Patterns**
- [ ] Config loading
- [ ] Config access
- [ ] Default values
- [ ] Environment variables

**F. Logging Patterns**
- [ ] Logger initialization
- [ ] Log levels used
- [ ] Structured logging
- [ ] Context logging

**G. Retry Patterns**
- [ ] Retry logic implementation
- [ ] Backoff strategies
- [ ] Failure handling

**H. Data Transformation Patterns**
- [ ] Data cleaning
- [ ] Data normalization
- [ ] Format conversion
- [ ] Type conversion

**I. Concurrency Patterns**
- [ ] Async operations
- [ ] Threading/processing
- [ ] Rate limiting
- [ ] Resource pooling

**J. Caching Patterns**
- [ ] Result caching
- [ ] Cache invalidation
- [ ] Cache keys

#### 2.3 Code Quality Assessment (10-15 minutes per file)

**Check for clean code principles**:

**A. Type Hints**
- [ ] All public functions have type hints
- [ ] All class methods have type hints
- [ ] Complex types properly annotated (Union, Optional, etc.)

**B. Documentation**
- [ ] All public functions have docstrings
- [ ] All classes have docstrings
- [ ] Complex logic has explanatory comments
- [ ] Docstring format is consistent (Google/NumPy style)

**C. Function Design**
- [ ] Functions are focused (single responsibility)
- [ ] Function length is reasonable (max 50 lines as guideline)
- [ ] Cyclomatic complexity is low (max 10 as guideline)
- [ ] Function names are clear and descriptive

**D. Naming Conventions**
- [ ] Variable names are descriptive
- [ ] Function names follow conventions
- [ ] Class names follow conventions
- [ ] Constants are clearly identified

**E. Code Organization**
- [ ] Related code is grouped together
- [ ] Imports are organized
- [ ] No circular dependencies
- [ ] Clear separation of concerns

**F. Error Handling**
- [ ] Errors are handled appropriately
- [ ] Error messages are informative
- [ ] Exceptions are specific (not generic Exception)
- [ ] Error context is captured

#### 2.4 Anti-Pattern Detection (5-10 minutes per file)

**Look for these anti-patterns**:

- [ ] **Code Duplication**: Same logic in multiple places
- [ ] **God Objects**: Classes with too many responsibilities
- [ ] **Long Methods**: Functions over 50 lines
- [ ] **Deep Nesting**: More than 3-4 levels of indentation
- [ ] **Magic Numbers**: Hard-coded values without constants
- [ ] **Dead Code**: Unused functions, variables, imports
- [ ] **Tight Coupling**: High dependency on specific implementations
- [ ] **Inconsistent Patterns**: Same problem solved differently
- [ ] **Missing Abstractions**: Repeated code that should be extracted
- [ ] **Poor Error Handling**: Generic exceptions, empty except blocks

#### 2.5 Library Opportunities (10-15 minutes per file)

**Identify opportunities for library extraction**:

For each pattern found:
1. **Frequency**: How many times does this pattern appear? (in this file, in domain, across codebase)
2. **Complexity**: How complex is the pattern? (simple, moderate, complex)
3. **Reusability**: Would other domains benefit? (yes/no, which domains)
4. **Library Match**: Does an existing library cover this? (check `core/libraries/`)
5. **Extraction Effort**: How hard to extract? (low, medium, high)

**Document each opportunity**:
```markdown
**Pattern**: [Name of pattern]
**Location**: [File:line or function name]
**Frequency**: [X occurrences in domain, Y across codebase]
**Complexity**: [Simple/Moderate/Complex]
**Reusability**: [Which domains would benefit]
**Existing Library**: [Library name or "None"]
**Extraction Effort**: [Low/Medium/High]
**Priority**: [High/Medium/Low - based on impact/effort]
```

---

### Step 3: Cross-File Analysis (1-2 hours per domain)

**After reviewing all files**:

1. **Consolidate Patterns**
   - Group similar patterns found across files
   - Count occurrences
   - Identify most common patterns

2. **Find Duplications**
   - Look for identical or very similar code blocks
   - Measure duplication (lines, functions, classes)
   - Identify extraction candidates

3. **Identify Inconsistencies**
   - Same problem solved differently in different files
   - Inconsistent error handling
   - Inconsistent logging
   - Inconsistent naming

4. **Map to Libraries**
   - Which patterns map to existing libraries?
   - Which patterns need new libraries?
   - Which patterns should be refactored in-place?

---

### Step 4: Prioritization (30-60 minutes per domain)

**For each finding, assess**:

#### Impact Assessment

**High Impact**:
- Affects multiple files/domains
- Reduces significant duplication
- Improves maintainability substantially
- Prevents bugs or errors

**Medium Impact**:
- Affects several files in domain
- Reduces moderate duplication
- Improves readability
- Standardizes patterns

**Low Impact**:
- Affects single file or few files
- Minor improvements
- Nice-to-have enhancements

#### Effort Assessment

**Low Effort** (< 2 hours):
- Simple extraction
- Clear library exists
- Straightforward refactoring

**Medium Effort** (2-8 hours):
- Moderate complexity
- Some design decisions needed
- Multiple files affected

**High Effort** (> 8 hours):
- Complex extraction
- New library needed
- Significant refactoring
- Risk of breaking changes

#### Priority Matrix

| Impact \ Effort | Low | Medium | High |
|----------------|-----|--------|------|
| **High**       | **P0** (Quick Win) | **P1** (High Value) | **P2** (Strategic) |
| **Medium**     | **P1** (Easy Win) | **P2** (Worth It) | **P3** (Consider) |
| **Low**        | **P2** (If Time) | **P3** (Backlog) | **P4** (Skip) |

**Priority Levels**:
- **P0**: Do immediately (quick wins, high impact)
- **P1**: Do soon (high value, reasonable effort)
- **P2**: Plan for (strategic, significant effort)
- **P3**: Backlog (consider if time permits)
- **P4**: Skip (low value, high effort)

---

### Step 5: Documentation (30-60 minutes per domain)

**Create consolidated findings document**:

Use the **Findings Template** (below) to document:
1. Domain overview
2. Files reviewed
3. Patterns identified (with examples)
4. Code quality issues
5. Library opportunities (prioritized)
6. Recommendations

---

## 📝 Findings Template

**File**: `documentation/findings/CODE-REVIEW-<DOMAIN>-<DATE>.md`

```markdown
# Code Review Findings: [Domain Name]

**Review Date**: [Date]  
**Reviewer**: [Name/LLM]  
**Domain**: [GraphRAG/Ingestion/RAG/Chat/Core]  
**Files Reviewed**: [Number] files, [Number] lines of code  
**Review Duration**: [Hours]

---

## Executive Summary

**Key Findings**:
- [X] patterns identified
- [X] code quality issues found
- [X] library opportunities identified
- Top priority: [Description]

**Quick Stats**:
- Average function length: [X] lines
- Files with type hints: [X]%
- Files with docstrings: [X]%
- Code duplication: [X]% (estimated)

---

## Files Reviewed

| File | Lines | Functions | Classes | Complexity | Notes |
|------|-------|-----------|---------|------------|-------|
| `path/to/file.py` | 150 | 5 | 2 | Medium | [Notes] |

---

## Patterns Identified

### Pattern 1: [Pattern Name]

**Description**: [What the pattern does]

**Locations**:
- `file1.py:123` - Function `function_name()`
- `file2.py:45` - Function `another_function()`
- [X] total occurrences

**Example Code**:
```python
# Example of the pattern
```

**Library Opportunity**:
- **Existing Library**: [Library name or "None"]
- **Extraction Effort**: [Low/Medium/High]
- **Reusability**: [Which domains]
- **Priority**: [P0-P4]

---

## Code Quality Issues

### Issue 1: [Issue Name]

**Description**: [What's wrong]

**Locations**: [Files affected]

**Impact**: [High/Medium/Low]

**Fix Effort**: [Low/Medium/High]

**Recommendation**: [How to fix]

---

## Library Opportunities (Prioritized)

### Opportunity 1: [Library/Extraction Name] - Priority P0

**Pattern**: [Pattern name]

**Impact**: [High/Medium/Low] - [Why]

**Effort**: [Low/Medium/High] - [Why]

**Files Affected**: [List]

**Recommendation**: [What to do]

---

## Recommendations

### Immediate Actions (P0)
1. [Action 1]
2. [Action 2]

### Short-term (P1)
1. [Action 1]
2. [Action 2]

### Strategic (P2)
1. [Action 1]
2. [Action 2]

### Backlog (P3-P4)
1. [Action 1]
2. [Action 2]

---

## Metrics

**Before Review**:
- Total lines: [X]
- Average function length: [X]
- Files with type hints: [X]%
- Files with docstrings: [X]%

**Targets** (after improvements):
- Code duplication: < 30%
- Average function length: < 50 lines
- Type hints: 100% (public APIs)
- Docstrings: 100% (public APIs)

---

## Next Steps

1. [Next step 1]
2. [Next step 2]
3. [Next step 3]
```

---

## 🎯 Decision Framework: Library Extraction

### When to Extract into a Library

**Extract if ALL of these are true**:
1. ✅ **Pattern appears 3+ times** (in domain or across codebase)
2. ✅ **Pattern is reusable** (other domains would benefit)
3. ✅ **Pattern has clear boundaries** (can be extracted cleanly)
4. ✅ **Extraction effort is reasonable** (< 8 hours for high-impact patterns)

**Extract if ANY of these are true**:
- Pattern is complex and error-prone (extraction reduces bugs)
- Pattern is performance-critical (centralized optimization)
- Pattern needs testing (library enables better testing)
- Pattern is changing frequently (centralized updates)

### When to Refactor In-Place

**Refactor in-place if**:
- Pattern appears only 1-2 times
- Pattern is domain-specific (not reusable)
- Extraction would be complex (> 8 hours)
- Pattern is tightly coupled to domain logic

### When to Use Existing Library

**Use existing library if**:
- Library exists in `core/libraries/`
- Library covers the pattern (even if not perfect)
- Library can be enhanced to cover the pattern
- **Action**: Apply library first, enhance if needed

### When to Create New Library

**Create new library if**:
- No existing library covers the pattern
- Pattern is high-frequency (3+ occurrences)
- Pattern is reusable across domains
- Pattern is complex enough to warrant abstraction

---

## 📊 Priority Framework

### Quick Wins (P0) - Do First

**Criteria**:
- High impact, low effort
- Clear library exists
- Simple extraction
- Immediate value

**Examples**:
- Apply existing library to domain
- Extract simple utility function
- Fix obvious code quality issues

### High Value (P1) - Do Soon

**Criteria**:
- High impact, medium effort
- Medium impact, low effort
- Clear path forward
- Significant improvement

**Examples**:
- Extract common pattern into library
- Standardize error handling
- Add type hints comprehensively

### Strategic (P2) - Plan For

**Criteria**:
- High impact, high effort
- Medium impact, medium effort
- Requires design decisions
- Long-term value

**Examples**:
- Create new library
- Major refactoring
- Architecture improvements

### Backlog (P3-P4) - Consider Later

**Criteria**:
- Low impact
- High effort
- Nice-to-have
- Can wait

**Examples**:
- Minor improvements
- Code style fixes
- Documentation enhancements

---

## 🔍 Pattern Identification Checklist

### Common Patterns to Look For

**Error Handling**:
- [ ] Try-except blocks
- [ ] Custom exception classes
- [ ] Error logging patterns
- [ ] Error context capture
- [ ] Error recovery strategies

**LLM Operations**:
- [ ] LLM client initialization
- [ ] Prompt construction
- [ ] Response parsing
- [ ] Structured output handling
- [ ] Retry logic for LLM calls
- [ ] Cost tracking

**Database Operations**:
- [ ] MongoDB connection patterns
- [ ] Query construction
- [ ] Batch operations
- [ ] Transaction handling
- [ ] Error handling for DB ops
- [ ] Connection pooling

**Validation**:
- [ ] Input validation
- [ ] Output validation
- [ ] Schema validation
- [ ] Type checking
- [ ] Data sanitization

**Configuration**:
- [ ] Config loading
- [ ] Config access patterns
- [ ] Default value handling
- [ ] Environment variable access

**Logging**:
- [ ] Logger initialization
- [ ] Log level usage
- [ ] Structured logging
- [ ] Context logging
- [ ] Log formatting

**Retry Logic**:
- [ ] Retry decorators
- [ ] Backoff strategies
- [ ] Failure handling
- [ ] Circuit breaker patterns

**Data Transformation**:
- [ ] Data cleaning
- [ ] Data normalization
- [ ] Format conversion
- [ ] Type conversion
- [ ] Data validation

**Concurrency**:
- [ ] Async operations
- [ ] Threading patterns
- [ ] Rate limiting
- [ ] Resource pooling
- [ ] Parallel processing

**Caching**:
- [ ] Result caching
- [ ] Cache invalidation
- [ ] Cache key generation
- [ ] Cache strategies

---

## 📈 Quality Metrics

### Metrics to Track

**Code Duplication**:
- Percentage of duplicated code
- Number of duplicate blocks
- Average duplication size

**Function Complexity**:
- Average function length
- Max function length
- Cyclomatic complexity average
- Functions over complexity threshold

**Documentation**:
- Percentage of functions with docstrings
- Percentage of classes with docstrings
- Docstring quality (subjective)

**Type Safety**:
- Percentage of functions with type hints
- Type checking errors (mypy)
- Type coverage

**Code Organization**:
- Average file size
- Number of responsibilities per class
- Coupling metrics (if available)

### Target Metrics

**After Refactoring**:
- Code duplication: < 30%
- Average function length: < 50 lines
- Max function length: < 100 lines
- Cyclomatic complexity: < 10 (average)
- Type hints: 100% (public APIs)
- Docstrings: 100% (public APIs)
- Files with > 1 responsibility: 0

---

## ✅ Review Completion Checklist

**Before marking a domain review complete**:

- [ ] All files in domain reviewed
- [ ] Patterns identified and documented
- [ ] Code quality issues documented
- [ ] Library opportunities prioritized
- [ ] Findings document created
- [ ] Recommendations provided
- [ ] Metrics captured (before state)
- [ ] Next steps defined

---

## 📚 Related Documents

- **PLAN_CODE-QUALITY-REFACTOR.md**: Master plan for all reviews
- **MASTER-PLAN.md**: Library vision and observability plan
- **ACTIVE_PLANS.md**: Current plan status and coordination
- **documentation/technical/ARCHITECTURE.md**: Architecture overview
- **core/libraries/**: Existing library implementations

---

## 🎓 Best Practices

1. **Be Systematic**: Follow the process, don't skip steps
2. **Document Everything**: Capture findings immediately
3. **Prioritize Wisely**: Focus on high-impact, reasonable-effort improvements
4. **Think Reusability**: Consider if other domains would benefit
5. **Check Existing Libraries**: Always check `core/libraries/` first
6. **Measure Impact**: Track metrics before and after
7. **Test Continuously**: Ensure tests pass after changes
8. **Incremental Progress**: Don't try to fix everything at once

---

**Last Updated**: November 6, 2025  
**Version**: 1.0

