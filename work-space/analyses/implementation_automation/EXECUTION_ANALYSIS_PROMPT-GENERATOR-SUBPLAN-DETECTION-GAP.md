# EXECUTION_ANALYSIS: Prompt Generator SUBPLAN Detection Gap

**Purpose**: Analyze workflow gap where prompt generator suggests creating SUBPLAN for achievement that already has SUBPLAN, risking duplicate creation  
**Date**: 2025-01-28  
**Status**: Active  
**Related PLAN(s)**: PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md  
**Category**: Process & Workflow Analysis

---

## 🎯 Objective

This analysis documents a critical workflow gap: **The prompt generator suggests creating a SUBPLAN for an achievement that already has a SUBPLAN in the workspace**, creating risk of duplicate SUBPLAN creation and workflow confusion.

**Case Study**: Achievement 0.1 in `PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md`

**Outcome**: Document the gap, identify root cause, propose solution to prevent duplicate SUBPLAN creation.

---

## 📋 Problem Statement

### What's the Process Issue?

**Description**: When using `generate_prompt.py --next`, the script suggests creating a SUBPLAN for Achievement 0.1, but `SUBPLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE_01.md` already exists in `work-space/subplans/`.

**Symptoms**:

- Prompt generator suggests: "Execute Achievement 0.1" (which includes creating SUBPLAN)
- SUBPLAN_01 already exists in workspace
- User concerned about duplicate creation if following prompt
- Workflow detection not checking workspace for existing SUBPLANs

**Impact**:

- **Severity**: High (workflow integrity, duplicate prevention)
- **Who/What Affected**: Users following prompts, workflow automation
- **Work Blocked/Slowed**: Risk of creating duplicate SUBPLANs, confusion about current state
- **Consequences**: 
  - Duplicate SUBPLAN files (SUBPLAN_01, SUBPLAN_01_duplicate?)
  - Workflow confusion (which SUBPLAN is active?)
  - Methodology violation (one SUBPLAN per achievement)
  - Lost work if user overwrites existing SUBPLAN

**When Does It Occur?**:

- When using `--next` flag to auto-detect next achievement
- When achievement has SUBPLAN in workspace but not yet complete
- When `find_next_achievement_hybrid` doesn't check workspace for existing SUBPLANs
- When workflow detection happens after achievement selection (not before)

---

## 🔍 Analysis

### Investigation Process

**What Was Investigated**:

1. **Prompt Generator Code** (`LLM/scripts/generation/generate_prompt.py`):
   - `find_next_achievement_hybrid()` function (lines 392-464)
   - `find_next_achievement_from_archive()` function (lines 179-220)
   - `find_next_achievement_from_root()` function (lines 223-390)
   - `detect_workflow_state()` function (lines 829-874)
   - `find_subplan_for_achievement()` function (lines 739-769)

2. **Workflow Detection Logic**:
   - How achievement is selected (`find_next_achievement_hybrid`)
   - When workflow state is checked (`detect_workflow_state`)
   - Where SUBPLAN existence is verified (`find_subplan_for_achievement`)

3. **Actual Behavior**:
   - Ran `generate_prompt.py --next @PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md`
   - Result: Suggests "Execute Achievement 0.1" (includes SUBPLAN creation)
   - Verified: `SUBPLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE_01.md` exists in workspace
   - Verified: `find_subplan_for_achievement()` correctly finds existing SUBPLAN

**Key Findings**:

1. **Achievement Selection Doesn't Check Workspace**: `find_next_achievement_hybrid()` only checks:
   - Archive directory for SUBPLANs (`find_next_achievement_from_archive`)
   - Root directory for SUBPLANs (`find_next_achievement_from_root`)
   - **Does NOT check `work-space/subplans/`**

2. **Workflow Detection Happens Too Late**: `detect_workflow_state()` is called AFTER achievement is selected, so:
   - Achievement 0.1 is selected (because no SUBPLAN found in archive/root)
   - Then workflow detection runs and finds SUBPLAN in workspace
   - But prompt already generated suggesting SUBPLAN creation

3. **Inconsistent SUBPLAN Detection**: 
   - `find_subplan_for_achievement()` correctly checks workspace first
   - `find_next_achievement_from_archive()` only checks archive
   - `find_next_achievement_from_root()` only checks root
   - **No unified check across all locations**

4. **Prompt Template Issue**: The generated prompt says "Execute Achievement 0.1" which includes "Step 1: Create SUBPLAN", but SUBPLAN already exists.

---

### Root Cause Analysis

**Primary Cause**: **Achievement selection logic doesn't check workspace for existing SUBPLANs**

**Why It Exists**:

1. **Separation of Concerns**: Achievement selection (`find_next_achievement_hybrid`) and workflow detection (`detect_workflow_state`) are separate functions:
   - Achievement selection: "What achievement should we work on?"
   - Workflow detection: "What's the state of that achievement?"
   - **Gap**: Achievement selection doesn't know about workspace SUBPLANs

2. **Historical Evolution**: The code evolved to check archive and root, but workspace structure (`work-space/subplans/`) was added later:
   - `find_next_achievement_from_archive()` checks archive
   - `find_next_achievement_from_root()` checks root
   - **Missing**: Check workspace (newer structure)

3. **Incomplete Integration**: `find_subplan_for_achievement()` correctly checks workspace, but it's only used in `detect_workflow_state()`, not in achievement selection:
   - Achievement selection uses different functions (archive/root only)
   - Workflow detection uses `find_subplan_for_achievement()` (workspace + archive)
   - **Inconsistency**: Two different code paths

**Contributing Factors**:

1. **No Unified SUBPLAN Discovery**: Each function checks different locations:
   - Archive check: `archive/subplans/`
   - Root check: `SUBPLAN_*.md` in root
   - Workspace check: `work-space/subplans/` (only in `find_subplan_for_achievement`)
   - **No single function that checks all locations**

2. **Prompt Generation Order**: Prompt is generated before workflow detection:
   - Achievement selected → Prompt generated → Workflow detected
   - **Should be**: Achievement selected → Workflow detected → Prompt generated based on state

3. **Template Assumes No SUBPLAN**: The prompt template always includes "Step 1: Create SUBPLAN", even when SUBPLAN exists:
   - Template doesn't check workflow state
   - Always assumes SUBPLAN doesn't exist
   - **Missing**: Conditional prompt based on workflow state

---

### Evidence

**Code Evidence**:

```python
# find_next_achievement_hybrid() - Lines 392-464
# Only checks archive and root, NOT workspace
def find_next_achievement_hybrid(...):
    # STEP 4: Check archive (no workspace check)
    next_ach = find_next_achievement_from_archive(...)
    if next_ach:
        return next_ach
    
    # STEP 5: Check root (no workspace check)
    return find_next_achievement_from_root(...)

# find_subplan_for_achievement() - Lines 739-769
# CORRECTLY checks workspace first
def find_subplan_for_achievement(feature_name, achievement_num):
    # Check work-space/subplans first ✅
    workspace_subplan = Path(f"work-space/subplans/SUBPLAN_{feature_name}_{subplan_num}.md")
    if workspace_subplan.exists():
        return workspace_subplan
    # Then check archive...
```

**Behavioral Evidence**:

1. **Terminal Output** (user provided):
   ```
   Execute Achievement 0.1 in @PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md following strict methodology.
   ...
   Step 1: Create SUBPLAN (MANDATORY)
   - File: SUBPLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE_01.md
   ```

2. **File System Check**:
   ```bash
   $ ls -1 work-space/subplans/SUBPLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE_01.md
   work-space/subplans/SUBPLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE_01.md  # EXISTS
   ```

3. **Path Detection Test**:
   ```python
   Feature name: GRAPHRAG-OBSERVABILITY-EXCELLENCE
   Looking for: work-space/subplans/SUBPLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE_01.md
   Exists: True  # CORRECTLY DETECTED by find_subplan_for_achievement()
   ```

**Impact Evidence**:

- User concern: "I am wondering if I prompt a duplicated subplan 01 for that plan will be created"
- Risk: Following prompt would create duplicate or overwrite existing SUBPLAN
- Workflow confusion: Which SUBPLAN is the active one?

---

## 💡 Recommendations

### Process Improvements

**Recommendation 1**: Unify SUBPLAN Discovery Across All Locations

- **What**: Create single function that checks workspace, archive, and root for SUBPLANs
- **Why**: Ensures consistent SUBPLAN detection across all code paths
- **How**: 
  1. Refactor `find_subplan_for_achievement()` to be the single source of truth
  2. Update `find_next_achievement_from_archive()` to use unified function
  3. Update `find_next_achievement_from_root()` to use unified function
  4. Update `find_next_achievement_hybrid()` to check workspace via unified function
- **Priority**: Critical
- **Effort**: 2-3 hours

**Recommendation 2**: Check Workspace in Achievement Selection

- **What**: Update `find_next_achievement_hybrid()` to check workspace for existing SUBPLANs
- **Why**: Prevents suggesting achievements that already have SUBPLANs
- **How**:
  1. Add workspace check in `find_next_achievement_hybrid()` before returning achievement
  2. Skip achievements that have SUBPLANs in workspace (unless complete)
  3. Use `find_subplan_for_achievement()` for consistency
- **Priority**: Critical
- **Effort**: 1-2 hours

**Recommendation 3**: Generate Prompt Based on Workflow State

- **What**: Check workflow state BEFORE generating prompt, adjust template accordingly
- **Why**: Prevents suggesting SUBPLAN creation when SUBPLAN exists
- **How**:
  1. Call `detect_workflow_state()` before generating prompt
  2. Use workflow state to select appropriate prompt template:
     - `no_subplan` → "Create SUBPLAN" prompt
     - `subplan_no_execution` → "Create EXECUTION" prompt
     - `active_execution` → "Continue EXECUTION" prompt
     - `subplan_complete` → "Next achievement" prompt
  3. Remove "Step 1: Create SUBPLAN" from prompt if SUBPLAN exists
- **Priority**: High
- **Effort**: 2-3 hours

**Recommendation 4**: Add Validation

- **What**: Add validation to prevent duplicate SUBPLAN creation
- **Why**: Safety net to catch duplicates even if detection fails
- **How**:
  1. Add check in SUBPLAN creation prompt/template
  2. Warn user if SUBPLAN already exists
  3. Suggest continuing existing SUBPLAN instead
  4. Add validation script: `validate_no_duplicate_subplans.py`
- **Priority**: Medium
- **Effort**: 1-2 hours

---

### Workflow Changes

**Change 1**: Achievement Selection Workflow

- **Current**: Select achievement → Generate prompt → Detect workflow
- **Proposed**: Select achievement → Detect workflow → Generate prompt based on state
- **Why**: Ensures prompt matches actual workflow state
- **How**: Reorder function calls in `main()` function

**Change 2**: SUBPLAN Discovery Workflow

- **Current**: Different functions check different locations (inconsistent)
- **Proposed**: Single unified function checks all locations (consistent)
- **Why**: Prevents gaps in detection
- **How**: Refactor to use `find_subplan_for_achievement()` everywhere

---

## 📋 Implementation Plan

### Step 1: Unify SUBPLAN Discovery

**What**: Refactor to use `find_subplan_for_achievement()` as single source of truth

**How**:
1. Review `find_subplan_for_achievement()` - ensure it checks all locations correctly
2. Update `find_next_achievement_from_archive()` to use unified function
3. Update `find_next_achievement_from_root()` to use unified function
4. Remove duplicate SUBPLAN discovery logic

**Dependencies**: None

**Estimated Effort**: 2-3 hours

---

### Step 2: Add Workspace Check to Achievement Selection

**What**: Update `find_next_achievement_hybrid()` to check workspace for SUBPLANs

**How**:
1. After selecting achievement candidate, check if SUBPLAN exists in workspace
2. If SUBPLAN exists and not complete, skip to next achievement
3. Use `find_subplan_for_achievement()` for consistency
4. Add test cases for workspace SUBPLAN detection

**Dependencies**: Step 1 (unified discovery)

**Estimated Effort**: 1-2 hours

---

### Step 3: Generate Prompt Based on Workflow State

**What**: Check workflow state before generating prompt, adjust template

**How**:
1. Call `detect_workflow_state()` in `main()` before generating prompt
2. Pass workflow state to prompt generation function
3. Select appropriate prompt template based on state:
   - `no_subplan` → Full prompt with SUBPLAN creation
   - `subplan_no_execution` → EXECUTION creation prompt
   - `active_execution` → Continue EXECUTION prompt
   - `subplan_complete` → Next achievement prompt
4. Update prompt templates to be state-aware

**Dependencies**: Step 2 (workspace check)

**Estimated Effort**: 2-3 hours

---

### Step 4: Add Validation and Safety Checks

**What**: Add validation to prevent duplicate SUBPLAN creation

**How**:
1. Add check in SUBPLAN creation prompt: "Check if SUBPLAN exists first"
2. Create validation script: `validate_no_duplicate_subplans.py`
3. Add warning if SUBPLAN already exists
4. Suggest continuing existing SUBPLAN instead

**Dependencies**: Step 3 (workflow-aware prompts)

**Estimated Effort**: 1-2 hours

---

### Overall Implementation Summary

**Total Estimated Effort**: 6-10 hours

**Priority Order**:
1. Step 1: Unify SUBPLAN discovery (foundation)
2. Step 2: Add workspace check (fixes immediate issue)
3. Step 3: Generate prompt based on state (improves UX)
4. Step 4: Add validation (safety net)

**Success Criteria**:
- [ ] `find_next_achievement_hybrid()` checks workspace for SUBPLANs
- [ ] Prompt generator doesn't suggest SUBPLAN creation when SUBPLAN exists
- [ ] Prompt template adjusts based on workflow state
- [ ] Validation prevents duplicate SUBPLAN creation
- [ ] All tests pass with workspace SUBPLANs

**Related Work**:
- `PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md` - Previous prompt generator fixes
- `EXECUTION_ANALYSIS_SUBPLAN-TRACKING-GAP.md` - Related tracking gap analysis

---

## 🔗 Related Analyses

**Related EXECUTION_ANALYSIS Documents**:
- `EXECUTION_ANALYSIS_PROMPT-GENERATOR-0.1-BUG.md` - Initial prompt generator bug
- `EXECUTION_ANALYSIS_PROMPT-GENERATOR-REGRESSION-BUG.md` - Regression bug analysis
- `EXECUTION_ANALYSIS_SUBPLAN-TRACKING-GAP.md` - SUBPLAN tracking in PLAN updates
- `EXECUTION_ANALYSIS_EXECUTION-ANALYSIS-PROTOCOL-VIOLATIONS.md` - Protocol violations analysis

**Feeds Into**:
- `PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md` - If not already addressed
- Methodology improvements for workflow detection

---

## 📝 Notes

**Additional Context**:

- This issue is related to the workspace structure (`work-space/subplans/`) being newer than archive/root checks
- The `find_subplan_for_achievement()` function already correctly checks workspace, but isn't used in achievement selection
- This is a workflow detection gap, not a file system issue (files are correctly detected when checked)

**Observations**:

- The code has evolved to support multiple locations (archive, root, workspace) but not consistently
- Achievement selection and workflow detection are separate concerns but need to be coordinated
- Prompt generation should be state-aware, not template-driven only

**Future Considerations**:

- Consider metadata tags system for virtual organization (see `LLM/guides/METADATA-TAGS.md`)
- May simplify SUBPLAN discovery if all SUBPLANs are tagged with metadata
- Could enable more flexible SUBPLAN location (not just workspace/archive/root)

---

## 📚 Usage Guidelines

**When to Use This Analysis**:
- Implementing prompt generator fixes
- Reviewing workflow detection logic
- Preventing duplicate SUBPLAN creation
- Understanding achievement selection behavior

**How to Use This Analysis**:
1. Review root cause analysis to understand the gap
2. Follow implementation plan to fix the issue
3. Use recommendations to improve workflow detection
4. Reference related analyses for context

**Best Practices**:
- Always check workspace before suggesting SUBPLAN creation
- Use unified SUBPLAN discovery function across all code paths
- Generate prompts based on actual workflow state
- Add validation to prevent duplicates

**Reference**:
- See `LLM/guides/EXECUTION-ANALYSIS-GUIDE.md` for complete taxonomy and usage
- See `documentation/archive/execution-analyses/process-analysis/` for examples
- Archive location: `documentation/archive/execution-analyses/process-analysis/2025-01/`

---

**Status**: Complete  
**Archive Location**: Will be archived in `documentation/archive/execution-analyses/process-analysis/2025-01/` when complete


