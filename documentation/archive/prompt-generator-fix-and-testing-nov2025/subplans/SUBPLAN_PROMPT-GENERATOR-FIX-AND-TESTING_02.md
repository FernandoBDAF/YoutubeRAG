# SUBPLAN: Update Achievement Detection Logic

**Mother Plan**: PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md  
**Achievement Addressed**: Achievement 0.2 (Update Achievement Detection Logic)  
**Status**: In Progress  
**Created**: 2025-11-08 00:40 UTC  
**Estimated Effort**: 45 minutes

---

## 🎯 Objective

Update `find_next_achievement_from_plan()` to prioritize the "Current Status & Handoff" section using the `extract_handoff_section()` function from Achievement 0.1. Reorder regex patterns to check specific formats first, and implement a fallback chain. This fixes the bug where the function returns Achievement 0.1 instead of 3.3.

**Goal**: Fix achievement detection to return the correct next achievement (e.g., 3.3 for PLAN_API-REVIEW-AND-TESTING.md) by prioritizing the authoritative handoff section.

---

## 📋 What Needs to Be Modified

### Files to Modify

- `LLM/scripts/generation/generate_prompt.py`
  - Update `find_next_achievement_from_plan()` function
  - Use `extract_handoff_section()` to get handoff section first
  - Reorder regex patterns (Pattern 4 first, then 2, 5, 1, 3)
  - Implement fallback chain: handoff section → full file → archive → root

### Files to Update

- `tests/LLM/scripts/generation/test_generate_prompt.py`
  - Add tests for updated `find_next_achievement_from_plan()` function
  - Test handoff section prioritization
  - Test fallback behavior
  - Test with real PLAN file (should return 3.3)

---

## 📝 Approach

**Strategy**: Implement hybrid approach - prioritize handoff section, then fallback to full file with reordered patterns.

**Method**:
1. **Primary**: Extract handoff section using `extract_handoff_section()`
   - If handoff section found, search patterns in that section only
   - Use reordered patterns (Pattern 4 first: `⏳\s*Next[:\s]+Achievement`)
   - Return first match found

2. **Fallback 1**: If handoff section not found or no match, search full file
   - Use reordered patterns (Pattern 4, 2, 5, 1, 3)
   - Pattern 4 first (most specific: `⏳\s*Next[:\s]+Achievement`)
   - Pattern 1 last (most greedy: `(?:Next|What\'s Next)\*\*[:\s]+.*?Achievement`)

3. **Pattern Order** (for both primary and fallback):
   - Pattern 4: `r'⏳\s*Next[:\s]+Achievement\s+(\d+\.\d+)'` (first - most specific)
   - Pattern 2: `r'(?:Next|What\'s Next)[:\s]+Achievement\s+(\d+\.\d+)'`
   - Pattern 5: `r'Next[:\s]+Achievement\s+(\d+\.\d+)'`
   - Pattern 1: `r'(?:Next|What\'s Next)\*\*[:\s]+.*?Achievement\s+(\d+\.\d+)'` (last - most greedy)
   - Pattern 3: `r'⏳\s*Achievement\s+(\d+\.\d+)'` (last - least specific)

**Key Considerations**:
- Use `extract_handoff_section()` from Achievement 0.1
- Search handoff section first (authoritative source)
- Reorder patterns to check specific formats before generic ones
- Maintain backward compatibility (fallback to full file search)
- Pattern 1 should be last (most greedy, matches across sections)

---

## 🧪 Tests Required

### Unit Tests

**Test Cases**:
1. **Handoff Section Priority**: PLAN with handoff section containing "Next: Achievement 3.3" → returns 3.3
2. **Handoff Section Format Variations**: Test with `⏳ Next:`, `**What's Next**:`, `Next:` formats
3. **Fallback to Full File**: PLAN without handoff section → searches full file
4. **Pattern Order**: Verify Pattern 4 checked before Pattern 1
5. **Real PLAN Test**: Test with `PLAN_API-REVIEW-AND-TESTING.md` → should return 3.3 (not 0.1)
6. **No Match**: PLAN without any "Next" mentions → returns None

**Test File**: `tests/LLM/scripts/generation/test_generate_prompt.py`

**Validation**:
- [ ] All test cases pass
- [ ] Function returns 3.3 for PLAN_API-REVIEW-AND-TESTING.md
- [ ] Handoff section prioritized correctly
- [ ] Fallback works when handoff section missing

---

## ✅ Expected Results

### Functional Changes

- **Updated Function**: `find_next_achievement_from_plan()` prioritizes handoff section
- **Pattern Reordering**: Patterns checked in optimal order (specific → generic)
- **Fallback Chain**: Handoff section → full file → archive → root

### Observable Outcomes

- **Correct Achievement**: Returns 3.3 for PLAN_API-REVIEW-AND-TESTING.md (not 0.1)
- **Handoff Priority**: Handoff section checked first
- **Backward Compatible**: Still works for PLANs without handoff section

### Success Criteria

- ✅ Function prioritizes handoff section
- ✅ Returns 3.3 for PLAN_API-REVIEW-AND-TESTING.md
- ✅ All test cases pass
- ✅ Pattern order correct (Pattern 4 first, Pattern 1 last)
- ✅ Fallback works correctly

---

## 📊 Deliverables Checklist

- [ ] `find_next_achievement_from_plan()` updated to use handoff section
- [ ] Patterns reordered (Pattern 4 first, Pattern 1 last)
- [ ] Fallback chain implemented
- [ ] Unit tests added/updated
- [ ] Function returns 3.3 for PLAN_API-REVIEW-AND-TESTING.md

---

## 🔗 Related Context

**Dependencies**: 
- Achievement 0.1 (Extract Handoff Section Function) - Uses `extract_handoff_section()` function
- `EXECUTION_ANALYSIS_PROMPT-GENERATOR-0.1-BUG.md` - Implementation approach (lines 194-207)

**Feeds Into**: 
- Achievement 0.3 (Test Bug Fix) - Will validate the complete fix

**Reference Documents**:
- `EXECUTION_ANALYSIS_PROMPT-GENERATOR-0.1-BUG.md` - Pattern reordering details (lines 209-214)
- `LLM/scripts/generation/generate_prompt.py` - Existing function to update

---

**Status**: Ready for Execution  
**Next**: Create EXECUTION_TASK and update function

