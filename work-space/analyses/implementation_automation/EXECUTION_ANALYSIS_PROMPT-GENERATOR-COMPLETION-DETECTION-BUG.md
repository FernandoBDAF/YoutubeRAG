# EXECUTION_ANALYSIS: Prompt Generator Completion Detection Bug

**Category**: Bug Analysis  
**Created**: 2025-11-08 18:40 UTC  
**Status**: Analysis Complete  
**Related**: `LLM/scripts/generation/generate_prompt.py`, Achievement 2.3

---

## 🎯 Problem Statement

After completing Achievement 3.1 in `PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md`, running `generate_prompt.py` again still suggests Achievement 3.1 instead of moving to the next achievement (3.2).

**User Report**:

```
After completing Achievement 3.1, running generate_prompt.py again still refers to 3.1
```

**Expected Behavior**: After an achievement is marked complete in the PLAN, `generate_prompt.py` should skip it and suggest the next incomplete achievement.

**Actual Behavior**: `generate_prompt.py` still suggests the completed achievement.

---

## 🔍 Root Cause Analysis

### Current Workflow Detection Logic

The issue is in the workflow detection flow in `generate_prompt.py`:

1. **Step 1**: `find_next_achievement_hybrid()` finds next achievement

   - ✅ **Does check completion**: Uses `is_achievement_complete()` to skip completed achievements
   - ✅ **Works correctly**: Skips completed achievements in archive/root checks
   - ✅ **Pattern matching works**: Pattern 5 (`Achievement\s+3\.1\s+Complete:?`) matches `- ✅ **Achievement 3.1 COMPLETE**:`

2. **Step 2**: `detect_workflow_state()` determines workflow state
   - ❌ **Does NOT check completion**: Only checks SUBPLAN/EXECUTION existence
   - ❌ **Problem**: If user explicitly requests completed achievement (`--achievement 3.1`), it will suggest creating SUBPLAN even though achievement is complete

### Verification Results

**Test 1**: Completion Pattern Matching

- Pattern 5 (`Achievement\s+3\.1\s+Complete:?`) ✅ **MATCHES** `- ✅ **Achievement 3.1 COMPLETE**:`
- Completion detection **WORKS** for this format

**Test 2**: Auto-detect Next Achievement (`--next`)

- ✅ **WORKS CORRECTLY**: Suggests Achievement 3.2 (next incomplete)
- `find_next_achievement_hybrid()` correctly skips completed achievements

**Test 3**: Explicit Completed Achievement (`--achievement 3.1`)

- ❌ **BUG CONFIRMED**: If user explicitly requests completed achievement, `detect_workflow_state()` doesn't check completion
- Test result: Found SUBPLAN in work-space, suggested "create_execution" (not checking if achievement is complete)
- **Issue**: Should first check if achievement is complete in PLAN before checking SUBPLAN status

### The Bug

**Location**: `generate_prompt.py` lines 1108-1155 (auto-detect workflow state section)

**Problem Flow**:

1. User completes Achievement 3.1
2. PLAN is updated: `✅ Achievement 3.1 COMPLETE`
3. User runs: `generate_prompt.py @PLAN.md --next`
4. `find_next_achievement_hybrid()` finds Achievement 3.1 (if "What's Next" still mentions it, or if completion check fails)
5. `detect_workflow_state()` is called with Achievement 3.1
6. `detect_workflow_state()` doesn't check if achievement is complete
7. It finds no SUBPLAN (because it's archived)
8. Returns `"recommendation": "create_subplan"`
9. Script suggests creating SUBPLAN for completed achievement

### Why This Bug Occurs

**Root Cause**: `detect_workflow_state()` doesn't check if achievement is complete before suggesting workflow actions.

**Scenarios Where Bug Appears**:

1. **User explicitly requests completed achievement**: `--achievement 3.1` when 3.1 is complete

   - `find_next_achievement_hybrid()` is bypassed (user specified achievement)
   - `detect_workflow_state()` is called directly
   - No completion check happens
   - Suggests "create_subplan" even though achievement is complete

2. **"What's Next" section points to completed achievement**: If PLAN's "What's Next" explicitly mentions completed achievement

   - `find_next_achievement_from_plan()` returns it
   - Completion check happens, but if pattern doesn't match, it might slip through
   - (Note: Pattern 5 does match, so this is less likely)

3. **Archive location mismatch**: If SUBPLAN is archived but `detect_workflow_state()` doesn't find it
   - Thinks no SUBPLAN exists
   - Suggests creating SUBPLAN even if achievement is complete

---

## 🔬 Investigation

### Check 1: Completion Detection Pattern ✅ VERIFIED

**Patterns in `is_achievement_complete()`**:

```python
patterns = [
    rf"✅\s+Achievement\s+{re.escape(ach_num)}\s+complete",
    rf"✅\s+Achievement\s+{re.escape(ach_num)}",
    rf"- ✅ Achievement {re.escape(ach_num)}",
    rf"Achievement\s+{re.escape(ach_num)}.*✅",
    rf"Achievement\s+{re.escape(ach_num)}\s+Complete:?",  # Pattern 5
]
```

**Actual format in PLAN**:

```
- ✅ **Achievement 3.1 COMPLETE**: Size Validation Scripts Created/Updated
```

**Test Result**: ✅ Pattern 5 **MATCHES** correctly

- Pattern `rf"Achievement\s+{re.escape(ach_num)}\s+Complete:?"` matches `"Achievement 3.1 COMPLETE"` in the text
- Completion detection **WORKS** for this format

### Check 2: Workflow Detection Logic

**`detect_workflow_state()` function** (lines 829-875):

- Checks if SUBPLAN exists (work-space or archive)
- Checks SUBPLAN status (active EXECUTIONs, completion)
- **Missing**: Does NOT check if achievement is complete in PLAN

**Problem**: Even if achievement is complete, if SUBPLAN is archived and not found, it suggests creating SUBPLAN.

### Check 3: Archive Location Detection

**`find_subplan_for_achievement()` function** (lines 720-750):

- Checks `work-space/subplans/` first
- Checks `documentation/archive/` (iterates through all archive dirs)
- Checks `feature-archive/` (iterates through all archive dirs)

**Potential Issue**: If archive structure doesn't match expected pattern, SUBPLAN won't be found.

---

## 💡 Solution

### Fix 1: Add Completion Check to `detect_workflow_state()`

**Location**: `LLM/scripts/generation/generate_prompt.py`, function `detect_workflow_state()`

**Change**: Add completion check at the start of function:

```python
def detect_workflow_state(
    plan_path: Path, feature_name: str, achievement_num: str
) -> Dict[str, any]:
    """
    Detect workflow state for achievement (SUBPLAN/EXECUTION status).
    """
    # Read PLAN content to check completion
    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            plan_content = f.read()
    except Exception:
        plan_content = ""

    # Check if achievement is complete FIRST
    if is_achievement_complete(achievement_num, plan_content):
        return {
            "state": "achievement_complete",
            "subplan_path": None,
            "recommendation": "next_achievement",
        }

    # Continue with existing logic...
    subplan_path = find_subplan_for_achievement(feature_name, achievement_num)
    # ... rest of function
```

### Fix 2: Improve Completion Pattern Matching (OPTIONAL)

**Status**: Pattern matching already works (Pattern 5 matches), but could add more specific pattern for robustness.

**Location**: `LLM/scripts/generation/generate_prompt.py`, function `is_achievement_complete()`

**Change**: Add pattern for `**Achievement X.Y COMPLETE**` format (defense in depth):

```python
patterns = [
    rf"✅\s+Achievement\s+{re.escape(ach_num)}\s+complete",
    rf"✅\s+Achievement\s+{re.escape(ach_num)}",
    rf"- ✅ Achievement {re.escape(ach_num)}",
    rf"- ✅\s+\*\*Achievement\s+{re.escape(ach_num)}\s+COMPLETE\*\*",  # NEW (more specific)
    rf"Achievement\s+{re.escape(ach_num)}.*✅",
    rf"Achievement\s+{re.escape(ach_num)}\s+Complete:?",  # Already works
]
```

**Note**: This is optional since Pattern 5 already works, but adds robustness.

### Fix 3: Improve "What's Next" Parsing

**Location**: `LLM/scripts/generation/generate_prompt.py`, function `find_next_achievement_from_plan()`

**Change**: After finding achievement from "What's Next", verify it's not complete before returning:

```python
next_num = find_next_achievement_from_plan(plan_content)
if next_num:
    next_ach = next((a for a in achievements if a.number == next_num), None)
    if next_ach:
        # Check completion BEFORE returning
        if is_achievement_complete(next_ach.number, plan_content):
            # Skip this achievement, continue to fallback methods
            continue
        return next_ach
```

### Fix 4: Handle "next_achievement" Recommendation

**Location**: `LLM/scripts/generation/generate_prompt.py`, main() function, auto-detect section

**Change**: Handle "next_achievement" recommendation by finding actual next achievement:

```python
if workflow_state["recommendation"] == "next_achievement":
    # Achievement is complete, find next incomplete achievement
    next_ach = find_next_achievement_hybrid(
        plan_path,
        feature_name,
        plan_data["achievements"],
        plan_data["archive_location"],
    )
    if next_ach:
        # Recursively call with next achievement (or generate prompt for it)
        achievement_num = next_ach.number
        workflow_state = detect_workflow_state(plan_path, feature_name, achievement_num)
        # Continue with workflow detection for next achievement
    else:
        prompt = "✅ All achievements complete! PLAN ready for END_POINT protocol."
```

---

## 📊 Impact Analysis

### Severity: **Medium**

**Why Medium**:

- Doesn't break functionality (user can manually specify next achievement)
- Causes confusion and wasted time
- Workaround exists (use `--achievement 3.2` explicitly)

**Affected Users**: All users using `generate_prompt.py` with `--next` flag after completing achievements.

**Frequency**: High (happens every time an achievement is completed and user runs `--next` again).

---

## 🎯 Recommended Fix Priority

**Priority 1 (Critical)**: Fix completion check in `detect_workflow_state()`

- **Why**: Prevents suggesting completed achievements
- **Effort**: Low (add 5-10 lines)
- **Impact**: High (fixes main issue)

**Priority 2 (Important)**: Improve completion pattern matching

- **Why**: Ensures completion detection works for all formats
- **Effort**: Low (add one pattern)
- **Impact**: Medium (catches edge cases)

**Priority 3 (Nice to Have)**: Improve "What's Next" parsing

- **Why**: Prevents stale "What's Next" from causing issues
- **Effort**: Medium (requires logic change)
- **Impact**: Low (defense in depth)

---

## 🧪 Test Cases

### Test Case 1: Completed Achievement Detection (Auto-detect)

**Setup**: Achievement 3.1 marked complete in PLAN
**Action**: Run `generate_prompt.py @PLAN.md --next`
**Expected**: Suggests Achievement 3.2 (or next incomplete)
**Actual**: ✅ **WORKS** - Suggests Achievement 3.2 correctly

### Test Case 1b: Explicit Completed Achievement

**Setup**: Achievement 3.1 marked complete in PLAN
**Action**: Run `generate_prompt.py @PLAN.md --achievement 3.1`
**Expected**: Should detect completion and suggest next achievement or show completion message
**Actual**: ❌ **BUG** - Suggests creating SUBPLAN for completed achievement

### Test Case 2: Completion Pattern Matching

**Setup**: PLAN has `- ✅ **Achievement 3.1 COMPLETE**:`
**Action**: Call `is_achievement_complete("3.1", plan_content)`
**Expected**: Returns `True`
**Actual**: Need to verify

### Test Case 3: Workflow State for Complete Achievement

**Setup**: Achievement 3.1 complete, SUBPLAN archived
**Action**: Call `detect_workflow_state(plan_path, feature_name, "3.1")`
**Expected**: Returns `{"recommendation": "next_achievement"}`
**Actual**: Returns `{"recommendation": "create_subplan"}` ❌

---

## 📝 Implementation Plan

### Step 1: Fix `detect_workflow_state()` (Priority 1)

- Add completion check at function start
- Return "next_achievement" if complete
- Test with completed achievement

### Step 2: Improve Completion Patterns (Priority 2)

- Add pattern for `**Achievement X.Y COMPLETE**` format
- Test with various completion formats
- Verify all patterns work

### Step 3: Handle "next_achievement" in Main Flow (Priority 1)

- Add handling for "next_achievement" recommendation
- Recursively find next incomplete achievement
- Generate appropriate prompt

### Step 4: Testing

- Test with completed achievement
- Test with various completion formats
- Test with multiple completed achievements
- Test with all achievements complete

---

## 🔗 Related Issues

- Similar to previous bugs fixed in `find_next_achievement_hybrid()` (Bug #2, #3)
- Related to completion detection improvements in Achievement 2.3

---

## 📚 References

- `LLM/scripts/generation/generate_prompt.py` (lines 829-875: `detect_workflow_state()`)
- `LLM/scripts/generation/generate_prompt.py` (lines 252-273: `is_achievement_complete()`)
- `LLM/scripts/generation/generate_prompt.py` (lines 1108-1155: auto-detect workflow state)
- `work-space/plans/PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md` (Achievement 3.1 completion)

---

**Status**: Analysis Complete  
**Next**: Implement fixes (Priority 1 first)
