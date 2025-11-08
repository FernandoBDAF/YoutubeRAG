# Analysis: Prompt Generator Misalignment with PLAN Status

**Date**: 2025-11-07  
**Issue**: Auto-generated prompts don't match PLAN's "Current Status & Handoff" section  
**Priority**: HIGH - Blocks workflow automation

---

## 🔍 Problem Statement

**Observed Behavior**:

1. **PLAN_API-REVIEW-AND-TESTING.md**:

   - PLAN says: "Next: Achievement 0.3"
   - Generator produces: Achievement 0.1 prompt
   - **Misalignment**: Generator is 2 achievements behind

2. **PLAN_METHODOLOGY-V2-ENHANCEMENTS.md**:
   - PLAN says: "Next: Achievement 5.3"
   - Generator produces: Achievement 5.2 prompt
   - **Misalignment**: Generator is 1 achievement behind

**Impact**:

- User must manually override generator output
- Workflow automation broken
- Trust in generator reduced

---

## 🔬 Root Cause Analysis

### Current Implementation (`find_next_achievement()`)

**Location**: `LLM/scripts/generation/generate_prompt.py` lines 81-88

```python
def find_next_achievement(feature_name: str, achievements: List[Achievement]) -> Optional[Achievement]:
    """Find first achievement without SUBPLAN file."""
    for ach in achievements:
        subplan_num = ach.number.replace('.', '')
        subplan_file = Path(f"SUBPLAN_{feature_name}_{subplan_num}.md")
        if not subplan_file.exists():
            return ach
    return None
```

**Logic**: Finds first achievement where SUBPLAN file doesn't exist in root directory.

### Why This Fails

**Problem 1: Immediate Archiving**

- SUBPLANs are archived immediately after completion (Achievement 2.2)
- SUBPLAN files move from root → archive directory
- Generator checks root directory only
- **Result**: Generator thinks completed achievements are "next"

**Example**:

- Achievement 5.2 SUBPLAN archived → `methodology-v2-enhancements-archive/subplans/`
- Generator checks root → `SUBPLAN_METHODOLOGY-V2-ENHANCEMENTS_52.md` not found
- Generator returns Achievement 5.2 as "next"
- But PLAN says 5.2 is complete, next is 5.3

**Problem 2: No PLAN Status Parsing**

- Generator doesn't read PLAN's "Current Status & Handoff" section
- Generator doesn't parse achievement completion markers (✅)
- Generator doesn't check archive directory for completed SUBPLANs
- **Result**: Generator uses filesystem state, not PLAN's declared state

**Example**:

- PLAN_API-REVIEW-AND-TESTING.md says "✅ Achievement 0.1 Complete" and "✅ Achievement 0.2 Complete"
- PLAN says "Next: Achievement 0.3"
- Generator ignores PLAN status, finds 0.1 (no SUBPLAN in root)
- **Result**: Generator returns 0.1, but PLAN says 0.3

---

## 📊 Detailed Analysis

### Case 1: PLAN_API-REVIEW-AND-TESTING.md

**PLAN State**:

- Achievement 0.1: ✅ Complete (SUBPLAN_01 archived)
- Achievement 0.2: ✅ Complete (SUBPLAN_02 archived)
- Achievement 0.3: ⏳ Next (no SUBPLAN yet)

**Generator Behavior**:

1. Checks root for `SUBPLAN_API-REVIEW-AND-TESTING_01.md` → Not found (archived)
2. Returns Achievement 0.1 as "next"
3. **Wrong**: Should return 0.3

**Root Cause**: Generator doesn't check archive directory or parse PLAN status.

### Case 2: PLAN_METHODOLOGY-V2-ENHANCEMENTS.md

**PLAN State**:

- Achievement 5.2: ✅ Complete (SUBPLAN_52 archived)
- Achievement 5.3: ⏳ Next (no SUBPLAN yet)

**Generator Behavior**:

1. Checks root for `SUBPLAN_METHODOLOGY-V2-ENHANCEMENTS_52.md` → Not found (archived)
2. Returns Achievement 5.2 as "next"
3. **Wrong**: Should return 5.3

**Root Cause**: Same as Case 1 - doesn't check archive or PLAN status.

---

## 🎯 Solution Options

### Option 1: Parse PLAN "Current Status & Handoff" Section (RECOMMENDED)

**Approach**: Read PLAN's explicit "What's Next" statement

**Pros**:

- ✅ Single source of truth (PLAN itself)
- ✅ No filesystem dependency
- ✅ Works even if archiving fails
- ✅ Respects user's declared state

**Cons**:

- ⚠️ Requires parsing "What's Next" section (needs regex)
- ⚠️ Must handle variations in format

**Implementation**:

```python
def find_next_achievement_from_plan(plan_content: str) -> Optional[str]:
    """Find next achievement from PLAN's 'What's Next' section."""
    # Look for patterns like:
    # - "Next: Achievement X.Y"
    # - "⏳ Next: Achievement X.Y"
    # - "What's Next: Achievement X.Y"
    pattern = r'(?:Next|What\'s Next)[:\s]+Achievement\s+(\d+\.\d+)'
    match = re.search(pattern, plan_content, re.IGNORECASE)
    return match.group(1) if match else None
```

**Priority**: HIGH - Most reliable, respects PLAN as source of truth

---

### Option 2: Check Archive Directory for Completed SUBPLANs

**Approach**: Check archive location for existing SUBPLANs

**Pros**:

- ✅ Works with immediate archiving
- ✅ No PLAN parsing needed
- ✅ Filesystem-based (simple)

**Cons**:

- ⚠️ Requires archive location from PLAN
- ⚠️ Fails if archiving didn't happen
- ⚠️ Doesn't handle partial completion

**Implementation**:

```python
def find_next_achievement_from_archive(feature_name: str, achievements: List[Achievement], archive_location: Path) -> Optional[Achievement]:
    """Find first achievement without archived SUBPLAN."""
    archive_subplans = archive_location / "subplans"
    for ach in achievements:
        subplan_num = ach.number.replace('.', '')
        subplan_file = archive_subplans / f"SUBPLAN_{feature_name}_{subplan_num}.md"
        if not subplan_file.exists():
            return ach
    return None
```

**Priority**: MEDIUM - Good fallback, but not primary

---

### Option 3: Parse Achievement Completion Markers

**Approach**: Look for ✅ markers in PLAN achievements

**Pros**:

- ✅ Works with PLAN structure
- ✅ No external dependencies

**Cons**:

- ⚠️ Requires consistent marking format
- ⚠️ May miss achievements marked complete elsewhere

**Implementation**:

```python
def find_next_achievement_from_markers(plan_content: str, achievements: List[Achievement]) -> Optional[Achievement]:
    """Find first achievement without ✅ marker."""
    for ach in achievements:
        pattern = rf'\*\*Achievement {ach.number}\*\*.*?(?:\n|$)'
        match = re.search(pattern, plan_content, re.MULTILINE)
        if match and '✅' not in match.group(0):
            return ach
    return None
```

**Priority**: LOW - Fragile, format-dependent

---

### Option 4: Hybrid Approach (BEST)

**Approach**: Try multiple methods in order of reliability

**Strategy**:

1. **First**: Parse "What's Next" from PLAN (Option 1) - Most reliable
2. **Fallback**: Check archive directory (Option 2) - Filesystem truth
3. **Last Resort**: Check root directory (current method) - For non-archived plans

**Implementation**:

```python
def find_next_achievement_hybrid(plan_path: Path, feature_name: str, achievements: List[Achievement], archive_location: Path) -> Optional[Achievement]:
    """Find next achievement using multiple methods."""

    # Method 1: Parse PLAN "What's Next"
    with open(plan_path, 'r') as f:
        plan_content = f.read()

    next_num = find_next_achievement_from_plan(plan_content)
    if next_num:
        return next((a for a in achievements if a.number == next_num), None)

    # Method 2: Check archive directory
    next_ach = find_next_achievement_from_archive(feature_name, achievements, archive_location)
    if next_ach:
        return next_ach

    # Method 3: Check root directory (current method)
    return find_next_achievement(feature_name, achievements)
```

**Priority**: HIGHEST - Combines reliability with fallbacks

---

## 📋 Recommended Solution

**Choose**: **Option 4 (Hybrid Approach)**

**Rationale**:

1. **Respects PLAN as source of truth** (Option 1)
2. **Handles immediate archiving** (Option 2)
3. **Backward compatible** (Option 3 fallback)
4. **Robust** (multiple methods)

**Implementation Steps**:

1. Add `find_next_achievement_from_plan()` function
2. Add `find_next_achievement_from_archive()` function
3. Update `find_next_achievement()` to use hybrid approach
4. Test with both PLAN files
5. Update validation scripts path (already done in Achievement 5.2)

**Estimated Effort**: 1-2 hours

---

## 🧪 Test Cases

### Test 1: PLAN with "What's Next" Statement

- **Input**: PLAN_API-REVIEW-AND-TESTING.md (says "Next: Achievement 0.3")
- **Expected**: Generator returns Achievement 0.3
- **Current**: Returns 0.1 ❌
- **After Fix**: Returns 0.3 ✅

### Test 2: PLAN with Archived SUBPLANs

- **Input**: PLAN_METHODOLOGY-V2-ENHANCEMENTS.md (5.2 archived, 5.3 next)
- **Expected**: Generator returns Achievement 5.3
- **Current**: Returns 5.2 ❌
- **After Fix**: Returns 5.3 ✅

### Test 3: PLAN without "What's Next" (New Plan)

- **Input**: New PLAN with no "What's Next" section
- **Expected**: Generator falls back to archive check, then root check
- **After Fix**: Works correctly ✅

### Test 4: PLAN with Non-Sequential Achievements

- **Input**: PLAN with completed 0.1, 0.2, but next is 1.1
- **Expected**: Generator returns 1.1 (respects PLAN)
- **After Fix**: Works correctly ✅

---

## 🚨 Edge Cases

1. **PLAN says "Next: Achievement X.Y" but X.Y doesn't exist**

   - **Solution**: Validate achievement exists, fallback to archive check

2. **Archive location not found in PLAN**

   - **Solution**: Use default archive location, continue with other methods

3. **Multiple "What's Next" statements in PLAN**

   - **Solution**: Use first occurrence, or most recent in "Current Status" section

4. **Achievement marked complete but SUBPLAN not archived**
   - **Solution**: Hybrid approach handles this (checks archive, then root)

---

## 📝 Implementation Notes

**Files to Modify**:

- `LLM/scripts/generation/generate_prompt.py`

**New Functions**:

- `find_next_achievement_from_plan(plan_content: str) -> Optional[str]`
- `find_next_achievement_from_archive(feature_name: str, achievements: List[Achievement], archive_location: Path) -> Optional[Achievement]`
- `find_next_achievement_hybrid(...)` (replaces current `find_next_achievement()`)

**Validation Script Paths**:

- Already fixed in Achievement 5.2 (scripts moved to `validation/`, `generation/`, `archiving/`)
- Need to update `detect_validation_scripts()` to check new paths

---

## ✅ Success Criteria

**This analysis is complete when**:

- [x] Root cause identified (immediate archiving + no PLAN parsing)
- [x] Solution options evaluated (4 options, hybrid recommended)
- [x] Test cases defined (4 cases)
- [x] Edge cases documented (4 cases)
- [x] Implementation approach specified

**Next Step**: Implement Option 4 (Hybrid Approach) in `generate_prompt.py`

---

**Status**: ✅ Analysis Complete → ✅ Implementation Complete  
**Implementation**: Option 4 (Hybrid Approach) - COMPLETED 2025-11-07

---

## ✅ Implementation Summary

**Date Implemented**: 2025-11-07  
**Duration**: ~30 minutes  
**Status**: ✅ Complete and Tested

### Changes Made

1. **Added `find_next_achievement_from_plan()`**:

   - Parses "What's Next" section from PLAN content
   - Supports multiple patterns: "Next:", "⏳ Next:", "What's Next:"
   - Returns achievement number as string

2. **Added `find_next_achievement_from_archive()`**:

   - Checks archive directory for archived SUBPLANs
   - Handles immediate archiving (Achievement 2.2)
   - Returns first achievement without archived SUBPLAN

3. **Added `find_next_achievement_from_root()`**:

   - Renamed from original `find_next_achievement()`
   - Checks root directory for SUBPLAN files
   - Backward compatible for non-archived plans

4. **Added `find_next_achievement_hybrid()`**:

   - Orchestrates all 3 methods in priority order
   - Graceful error handling with fallbacks
   - Primary method: Parse PLAN "What's Next"

5. **Updated `detect_validation_scripts()`**:

   - Now checks `LLM/scripts/validation/` directory
   - Falls back to old structure for backward compatibility
   - Found 8 validation scripts correctly

6. **Updated `generate_prompt()`**:
   - Uses `find_next_achievement_hybrid()` for `--next` flag
   - Passes plan_path, feature_name, achievements, archive_location

### Test Results

✅ **Test 1**: PLAN_API-REVIEW-AND-TESTING.md

- Before: Returned Achievement 0.1 ❌
- After: Returns Achievement 0.3 ✅
- **Status**: FIXED

✅ **Test 2**: PLAN_METHODOLOGY-V2-ENHANCEMENTS.md

- Before: Returned Achievement 5.2 ❌
- After: Returns Achievement 5.3 ✅
- **Status**: FIXED

✅ **Validation Script Detection**: 8 scripts found correctly

✅ **Linting**: No errors

### Impact

- **Workflow Automation**: ✅ RESTORED
- **Trust in Generator**: ✅ RESTORED
- **User Experience**: ✅ IMPROVED
- **Alignment**: Generator now perfectly aligned with PLAN status

**Ready for Production**: ✅ YES
