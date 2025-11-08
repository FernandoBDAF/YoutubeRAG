# EXECUTION_ANALYSIS: [Bug/Issue Title]

**Purpose**: [Brief description of the bug or issue being analyzed]  
**Date**: [YYYY-MM-DD]  
**Status**: [Active / Complete / Superseded]  
**Related**: [PLAN_NAME.md, Achievement X.Y, or other related work]  
**Category**: Bug/Issue Analysis

---

## 🔍 Problem Description

**Symptom**:
- [What is broken or not working as expected?]
- [What behavior is observed?]
- [When does it occur?]

**Expected Behavior**:
- [What should happen instead?]
- [What is the correct behavior?]

**Impact**:
- [Who/what is affected?]
- [What is the severity? (Critical / High / Medium / Low)]
- [What work is blocked?]

**Reproduction Steps**:
1. [Step 1]
2. [Step 2]
3. [Step 3]
4. [Observed result]

---

## 🔬 Root Cause Analysis

### Investigation Process

**What Was Tested**:
- [Tests performed, code reviewed, data analyzed]

**Evidence Collected**:
- [Test results, logs, data samples, code analysis]

**Key Findings**:
- [What was discovered during investigation]

### Root Cause

**Primary Cause**:
- [The main reason for the bug]

**Contributing Factors**:
- [Additional factors that enabled or worsened the bug]

**Why It Wasn't Caught Earlier**:
- [Gaps in testing, assumptions, edge cases]

---

## 📊 Evidence

### Test Results

[Include relevant test output, code snippets, or data]

```python
# Example test or code snippet
```

### Data/Logs

[Include relevant logs, data samples, or screenshots]

### File State

[Describe relevant file states, configurations, or environment]

---

## 🎯 Solution Options

### Option 1: [Solution Name]

**Approach**: [How this solution works]

**Pros**:
- [Advantage 1]
- [Advantage 2]

**Cons**:
- [Disadvantage 1]
- [Disadvantage 2]

**Effort**: [Estimated time/effort]

**Risk**: [Low / Medium / High]

### Option 2: [Solution Name]

**Approach**: [How this solution works]

**Pros**:
- [Advantage 1]
- [Advantage 2]

**Cons**:
- [Disadvantage 1]
- [Disadvantage 2]

**Effort**: [Estimated time/effort]

**Risk**: [Low / Medium / High]

### Option 3: [Solution Name] (if applicable)

[Repeat structure for additional options]

---

## ✅ Recommendation

**Preferred Solution**: [Option X]

**Rationale**:
- [Why this solution is best]
- [How it addresses root cause]
- [Why other options are less suitable]

**Implementation Priority**: [Critical / High / Medium / Low]

**Dependencies**: [What must exist or be done first]

---

## 📋 Implementation Plan (Optional)

**If recommendation requires implementation, outline steps**:

1. **Step 1**: [Action]
   - [Sub-step or detail]

2. **Step 2**: [Action]
   - [Sub-step or detail]

3. **Step 3**: [Action]
   - [Sub-step or detail]

**Estimated Effort**: [Time estimate]

**Related Work**:
- [Link to PLAN, Achievement, or other work]

---

## ✅ Success Criteria

**How to Verify Fix**:
- [ ] [Criterion 1: Specific test or check]
- [ ] [Criterion 2: Expected behavior verified]
- [ ] [Criterion 3: No regressions introduced]

**Testing Approach**:
- [How to test the fix]
- [What tests to run]
- [What to verify]

---

## 🔗 Related Analyses

**Related EXECUTION_ANALYSIS Documents**:
- [Link to related bug analyses, if any]
- [Link to unified solution, if this is part of a series]

**Analysis Lineage** (if part of series):
- Bug #1 → Bug #2 → Bug #3 → Unified Solution

---

## 📝 Notes

[Additional context, observations, or considerations]

---

## 📚 Usage Guidelines

**When to Use This Template**:
- Bug discovered during execution or testing
- Regression detected (something that worked before now broken)
- Issue needs deep root cause analysis
- Multiple related bugs need unified analysis

**How to Fill This Template**:
1. **Header**: Fill in Purpose, Date, Status, Related work, Category
2. **Problem Description**: Be specific about symptoms and impact
3. **Root Cause Analysis**: Investigate thoroughly, collect evidence
4. **Solution Options**: Consider multiple approaches, evaluate trade-offs
5. **Recommendation**: Choose best solution with clear rationale
6. **Implementation Plan**: Only if fix needs implementation steps
7. **Success Criteria**: Define how to verify the fix works

**Best Practices**:
- Be specific and evidence-based
- Include test results and data
- Consider multiple solution options
- Link to related analyses if part of series
- Update status as analysis progresses

**Reference**:
- See `LLM/guides/EXECUTION-ANALYSIS-GUIDE.md` for complete taxonomy and usage
- See `documentation/archive/execution-analyses/bug-analysis/` for examples
- Archive location: `documentation/archive/execution-analyses/bug-analysis/YYYY-MM/`

---

**Example**: See `EXECUTION_ANALYSIS_PROMPT-GENERATOR-0.1-BUG.md` in archive for completed example.

