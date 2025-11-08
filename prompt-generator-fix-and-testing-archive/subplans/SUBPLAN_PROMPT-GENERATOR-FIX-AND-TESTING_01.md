# SUBPLAN: Extract Handoff Section Function

**Mother Plan**: PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md  
**Achievement Addressed**: Achievement 0.1 (Extract Handoff Section Function)  
**Status**: In Progress  
**Created**: 2025-11-08 00:30 UTC  
**Estimated Effort**: 30 minutes

---

## 🎯 Objective

Implement `extract_handoff_section()` function that extracts the "Current Status & Handoff" section from PLAN content. This function is the foundation for fixing the prompt generator bug by prioritizing the authoritative handoff section over other "Next" mentions in the file.

**Goal**: Create a robust function that reliably extracts the handoff section, handles edge cases (missing section, malformed section), and returns the section content for pattern matching.

---

## 📋 What Needs to Be Created

### Files to Modify

- `LLM/scripts/generation/generate_prompt.py`
  - Add `extract_handoff_section(plan_content: str) -> Optional[str]` function
  - Function should extract content between "## 📝 Current Status & Handoff" and next `##` section
  - Handle edge cases gracefully

### Files to Create

- `tests/LLM/scripts/generation/test_generate_prompt.py` (if doesn't exist)
  - Unit tests for `extract_handoff_section()`
  - Test cases: normal extraction, missing section, malformed section, empty section

---

## 📝 Approach

**Strategy**: Implement section extraction using regex or line-by-line parsing, prioritizing reliability and edge case handling.

**Method**:
1. **Find Section Start**: Search for "## 📝 Current Status & Handoff" or variations
2. **Extract Content**: Collect lines until next `##` section header
3. **Handle Edge Cases**: 
   - Missing section → return None
   - Malformed section → return None or partial content
   - Empty section → return empty string or None
4. **Return Content**: Return extracted section as string

**Key Considerations**:
- Section header may have variations (emoji, spacing)
- Section ends at next `##` header (any level)
- Should handle markdown formatting within section
- Return None if section not found (for fallback logic)

**Implementation Pattern**:
```python
def extract_handoff_section(plan_content: str) -> Optional[str]:
    """Extract 'Current Status & Handoff' section content."""
    lines = plan_content.split('\n')
    # Find section start
    # Extract until next ## section
    # Return section content or None
```

---

## 🧪 Tests Required

### Unit Tests

**Test Cases**:
1. **Normal Extraction**: PLAN with handoff section → returns section content
2. **Missing Section**: PLAN without handoff section → returns None
3. **Malformed Section**: PLAN with incomplete section → handles gracefully
4. **Empty Section**: PLAN with empty handoff section → returns empty string or None
5. **Section Variations**: Test with different header formats (emoji, spacing)
6. **Multiple Sections**: Verify it stops at next `##` header

**Test File**: `tests/LLM/scripts/generation/test_generate_prompt.py`

**Validation**:
- [ ] All test cases pass
- [ ] Edge cases handled correctly
- [ ] Function returns expected types (Optional[str])

---

## ✅ Expected Results

### Functional Changes

- **New Function**: `extract_handoff_section()` added to `generate_prompt.py`
- **Edge Case Handling**: Function handles missing/malformed sections gracefully
- **Test Coverage**: Unit tests validate function behavior

### Observable Outcomes

- **Function Available**: `extract_handoff_section()` can be imported and called
- **Tests Pass**: All unit tests pass
- **Edge Cases Covered**: Missing, malformed, empty sections handled

### Success Criteria

- ✅ Function implemented and working
- ✅ All test cases pass
- ✅ Edge cases handled (missing, malformed, empty)
- ✅ Function returns Optional[str] as expected
- ✅ Code follows existing style in file

---

## 📊 Deliverables Checklist

- [ ] `extract_handoff_section()` function implemented in `generate_prompt.py`
- [ ] Unit tests created in `tests/LLM/scripts/generation/test_generate_prompt.py`
- [ ] All test cases pass
- [ ] Edge cases handled
- [ ] Code follows existing style

---

## 🔗 Related Context

**Dependencies**: 
- Achievement 0.2 (Update Achievement Detection Logic) - Will use this function
- `EXECUTION_ANALYSIS_PROMPT-GENERATOR-0.1-BUG.md` - Bug analysis and solution approach

**Feeds Into**: 
- Achievement 0.2: This function will be used in `find_next_achievement_from_plan()`
- Achievement 0.3: Tests will validate the fix

**Reference Documents**:
- `EXECUTION_ANALYSIS_PROMPT-GENERATOR-0.1-BUG.md` - Implementation approach (lines 183-192)
- `LLM/scripts/generation/generate_prompt.py` - Existing code structure

---

**Status**: Ready for Execution  
**Next**: Create EXECUTION_TASK and implement function

