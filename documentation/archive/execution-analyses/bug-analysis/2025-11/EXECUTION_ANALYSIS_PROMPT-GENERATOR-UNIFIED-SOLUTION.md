# Unified Solution: Prompt Generator Regression Bugs #1 & #2

**Date**: 2025-01-27  
**Context**: Two regression bugs with common root cause  
**Status**: Comprehensive analysis complete, unified solution ready

---

## 🔍 Big Picture Analysis

### Bug #1: Missing Achievement in Handoff
- **Symptom**: Handoff references "Achievement 3.4" but it doesn't exist in PLAN
- **Root Cause**: `find_next_achievement_hybrid()` doesn't validate achievement exists
- **Fallback Behavior**: Returns Achievement 0.1 (wrong)
- **Example**: `PLAN_API-REVIEW-AND-TESTING.md`

### Bug #2: Incomplete Handoff Section
- **Symptom**: Handoff section exists but doesn't specify "Next: Achievement X"
- **Root Cause**: `find_next_achievement_from_plan()` returns None, falls back incorrectly
- **Fallback Behavior**: Returns Achievement 0.1 (wrong, even for "Planning" status)
- **Example**: `PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md`

### Common Root Cause

**Both bugs share the same fundamental issue**:
1. Primary method (`find_next_achievement_from_plan()`) fails or returns invalid result
2. Falls back to `find_next_achievement_from_archive()` or `find_next_achievement_from_root()`
3. Fallback methods return **first unarchived achievement** without validation
4. No check for:
   - Achievement completion status
   - PLAN status (Planning vs In Progress)
   - Whether achievement actually exists
   - Whether achievement is the intended next one

---

## 🎯 Unified Solution Strategy

### Solution Components

**Component 1: Validate Achievement Existence** (Addresses Bug #1)
- Check if achievement from handoff exists in parsed achievements
- If missing, generate Plan Review Prompt (from Final Recommendation)
- Prevents returning wrong achievement when handoff references non-existent achievement

**Component 2: Check PLAN Status** (Addresses Bug #2)
- Detect if PLAN is in "Planning" vs "In Progress" status
- For "Planning" status: Return first achievement (correct behavior)
- For "In Progress" status: Use fallback methods with validation

**Component 3: Check Completion Status in Fallback** (Addresses Both Bugs)
- Make fallback methods skip achievements marked complete in PLAN
- Parse completion status from handoff section or achievement list
- Prevents returning completed achievements

**Component 4: Validate Handoff Completeness** (Addresses Bug #2)
- Detect when handoff section exists but doesn't specify next achievement
- Log warning for PLAN maintainers
- Provide guidance on fixing incomplete handoff

---

## 📋 Unified Implementation Plan

### Achievement 0.4: Handle Missing Achievements & Incomplete Handoff

**Objective**: Fix both regression bugs with comprehensive validation

**Deliverables**:
1. Add achievement existence validation in `find_next_achievement_hybrid()`
2. Add PLAN status detection (Planning vs In Progress)
3. Add completion status checking in fallback methods
4. Add handoff completeness validation
5. Generate Plan Review Prompt when achievement doesn't exist
6. Add comprehensive tests for both bug scenarios

**Implementation Steps**:

1. **Add PLAN Status Detection**:
   ```python
   def get_plan_status(plan_content: str) -> str:
       """Extract PLAN status (Planning, In Progress, Complete, etc.)."""
       status_match = re.search(r"\*\*Status\*\*[:\s]+(\w+)", plan_content, re.IGNORECASE)
       if status_match:
           return status_match.group(1).lower()
       return "unknown"
   ```

2. **Add Completion Status Check**:
   ```python
   def is_achievement_complete(ach_num: str, plan_content: str) -> bool:
       """Check if achievement is marked complete in PLAN."""
       patterns = [
           rf"✅\s+Achievement\s+{re.escape(ach_num)}\s+complete",
           rf"✅\s+Achievement\s+{re.escape(ach_num)}",
           rf"- ✅ Achievement {re.escape(ach_num)}",
       ]
       for pattern in patterns:
           if re.search(pattern, plan_content, re.IGNORECASE):
               return True
       return False
   ```

3. **Update find_next_achievement_hybrid()**:
   ```python
   def find_next_achievement_hybrid(
       plan_path: Path, feature_name: str, achievements: List[Achievement], archive_location: str
   ) -> Optional[Achievement]:
       """Find next achievement using multiple methods (hybrid approach)."""
       
       with open(plan_path, "r", encoding="utf-8") as f:
           plan_content = f.read()
       
       # Check PLAN status first
       status = get_plan_status(plan_content)
       if status == "planning":
           # Return first achievement if PLAN not started
           if achievements:
               return achievements[0]
           return None
       
       # Method 1: Parse PLAN "What's Next" (most reliable)
       handoff_section = extract_handoff_section(plan_content)
       next_num = find_next_achievement_from_plan(plan_content)
       
       if next_num:
           next_ach = next((a for a in achievements if a.number == next_num), None)
           if next_ach:
               return next_ach
           
           # Achievement doesn't exist - return special marker for Plan Review Prompt
           return Achievement(
               number=next_num,
               title="PLAN_REVIEW_REQUIRED",
               goal="",
               effort="",
               priority="",
               section_lines=0,
           )
       
       # Validate handoff completeness
       if handoff_section and not next_num:
           import warnings
           warnings.warn(
               "Handoff section exists but doesn't specify 'Next: Achievement X'. "
               "Using fallback methods.",
               UserWarning
           )
       
       # Method 2: Check archive directory (with completion check)
       next_ach = find_next_achievement_from_archive(
           feature_name, achievements, archive_location, plan_content
       )
       if next_ach:
           return next_ach
       
       # Method 3: Check root directory (with completion check)
       return find_next_achievement_from_root(feature_name, achievements, plan_content)
   ```

4. **Update Fallback Methods**:
   ```python
   def find_next_achievement_from_archive(
       feature_name: str, achievements: List[Achievement], 
       archive_location: str, plan_content: str
   ) -> Optional[Achievement]:
       """Find first achievement without archived SUBPLAN (skip completed)."""
       archive_path = Path(archive_location)
       if not archive_path.exists():
           return None
       
       archive_subplans = archive_path / "subplans"
       if not archive_subplans.exists():
           return None
       
       for ach in achievements:
           # Skip if marked complete
           if is_achievement_complete(ach.number, plan_content):
               continue
           
           subplan_num = ach.number.replace(".", "")
           subplan_file = archive_subplans / f"SUBPLAN_{feature_name}_{subplan_num}.md"
           if not subplan_file.exists():
               return ach
       
       return None
   
   def find_next_achievement_from_root(
       feature_name: str, achievements: List[Achievement], plan_content: str
   ) -> Optional[Achievement]:
       """Find first achievement without SUBPLAN (skip completed)."""
       for ach in achievements:
           # Skip if marked complete
           if is_achievement_complete(ach.number, plan_content):
               continue
           
           subplan_num = ach.number.replace(".", "")
           subplan_file = Path(f"SUBPLAN_{feature_name}_{subplan_num}.md")
           if not subplan_file.exists():
               return ach
       return None
   ```

5. **Add Plan Review Prompt Generation**:
   ```python
   PLAN_REVIEW_TEMPLATE = """
   ⚠️ PLAN TRACKING INCONSISTENCY DETECTED
   
   The handoff section references Achievement {achievement_num}, but this achievement is not defined in the PLAN.
   
   **Issue**:
   - Handoff section says: "Next: Achievement {achievement_num}"
   - But Achievement {achievement_num} is not found in the PLAN achievements list
   - Available achievements: {available_achievements}
   
   **Action Required**:
   Please review the PLAN and:
   1. Check if the plan is actually complete (all achievements done)
   2. If complete: Update handoff section to mark plan as complete
   3. If incomplete: Add missing achievement definition or fix handoff reference
   4. Update Subplan Tracking section if needed
   5. Verify completion criteria checklist
   
   **Files to Review**:
   - {plan_path}
   """
   ```

6. **Update generate_prompt()**:
   ```python
   def generate_prompt(...):
       # ... existing code ...
       
       next_ach = find_next_achievement_hybrid(...)
       
       if not next_ach:
           return "❌ No achievements found or all complete!"
       
       # Check for Plan Review requirement
       if next_ach.title == "PLAN_REVIEW_REQUIRED":
           available = [a.number for a in plan_data["achievements"]]
           return PLAN_REVIEW_TEMPLATE.format(
               achievement_num=next_ach.number,
               available_achievements=", ".join(available),
               plan_path=plan_path,
           )
       
       # ... continue with normal prompt generation ...
   ```

---

## 🧪 Test Cases

### Bug #1 Tests (Missing Achievement)
1. **Handoff references non-existent achievement**:
   - Input: `PLAN_API-REVIEW-AND-TESTING.md` (references 3.4, doesn't exist)
   - Expected: Plan Review Prompt generated
   - Verify: Prompt includes available achievements, clear instructions

2. **Handoff references valid achievement**:
   - Input: PLAN with valid achievement in handoff
   - Expected: Normal achievement prompt generated
   - Verify: No regression

### Bug #2 Tests (Incomplete Handoff)
3. **Planning status with no "Next"**:
   - Input: `PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md` (Planning status)
   - Expected: Returns first achievement (0.1)
   - Verify: No warning (correct behavior for Planning status)

4. **In Progress with incomplete handoff**:
   - Input: PLAN with "In Progress" but no "Next" in handoff
   - Expected: Warning logged, fallback returns next incomplete achievement
   - Verify: Doesn't return completed achievements

5. **No handoff section**:
   - Input: PLAN without handoff section
   - Expected: Uses fallback methods with completion check
   - Verify: No regression

### General Tests
6. **All achievements complete**:
   - Input: PLAN with all achievements marked complete
   - Expected: Returns None or appropriate message
   - Verify: Clear guidance provided

7. **Fallback skips completed achievements**:
   - Input: PLAN with some achievements complete, some not
   - Expected: Returns first incomplete achievement
   - Verify: Doesn't return completed ones

---

## 📊 Impact Assessment

**Current Impact**:
- **High**: Users get wrong prompts, waste time on completed/wrong work
- **Frequency**: Affects any PLAN with:
  - Handoff referencing non-existent achievement
  - Incomplete handoff section
  - "Planning" status plans

**After Fix**:
- **Low**: Graceful handling of all edge cases
- **Confidence**: High (validates status, checks completion, warns on issues)
- **Self-Healing**: Plan Review Prompt helps fix PLAN inconsistencies

---

## 📋 PLAN Update Recommendation

### Add to PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md

**Achievement 0.4**: Handle Missing Achievements & Incomplete Handoff

- Add PLAN status detection (Planning vs In Progress)
- Add achievement existence validation in `find_next_achievement_hybrid()`
- Add completion status checking in fallback methods
- Add handoff completeness validation with warnings
- Generate Plan Review Prompt when achievement doesn't exist
- Update fallback methods to skip completed achievements
- Add comprehensive tests for both bug scenarios (Bug #1 and Bug #2)
- Success: Both regression bugs fixed, graceful handling of edge cases
- Effort: 1.5 hours
- Files: `LLM/scripts/generation/generate_prompt.py`, `tests/LLM/scripts/generation/test_generate_prompt.py`

**Priority**: HIGH (blocks workflow, affects multiple PLANs, regression from previous fix)

**Dependencies**: 
- Achievement 0.1 ✅ (extract_handoff_section)
- Achievement 0.2 ✅ (find_next_achievement_from_plan)
- Achievement 0.3 ✅ (test coverage)

**Test Coverage**:
- 7 test cases covering both bugs
- Tests for Planning status, In Progress status, missing achievements, incomplete handoff
- Tests for completion status checking in fallback methods

---

## ✅ Success Criteria

**Fix is Complete When**:
- [ ] `find_next_achievement_hybrid()` validates achievement existence
- [ ] PLAN status detection works (Planning vs In Progress)
- [ ] Completion status checking works in fallback methods
- [ ] Handoff completeness validation with warnings
- [ ] Plan Review Prompt generated when achievement doesn't exist
- [ ] Fallback methods skip completed achievements
- [ ] All 7 test cases pass
- [ ] Both `PLAN_API-REVIEW-AND-TESTING.md` and `PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md` work correctly
- [ ] No regressions in other PLANs

---

## 🎯 Final Recommendation

**Implement Unified Solution (Achievement 0.4)**

**Rationale**:
1. Fixes both regression bugs completely
2. Handles all edge cases (Planning status, incomplete handoff, missing achievements)
3. Provides self-healing capability (Plan Review Prompt)
4. Prevents returning wrong/completed achievements
5. Better user experience (clear errors vs silent wrong behavior)
6. Reasonable effort (1.5 hours)

**Next Steps**:
1. Add Achievement 0.4 to `PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md`
2. Implement unified solution (all 4 components)
3. Add comprehensive tests (7 test cases)
4. Test with both problematic PLANs
5. Verify no regressions

**Status**: Ready for implementation  
**Priority**: HIGH (blocks workflow, affects multiple PLANs)  
**Effort**: 1.5 hours

