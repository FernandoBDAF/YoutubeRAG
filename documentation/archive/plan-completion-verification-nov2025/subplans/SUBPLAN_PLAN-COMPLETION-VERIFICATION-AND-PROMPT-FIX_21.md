# SUBPLAN: Add Completion Detection to Prompt Generator

**Mother Plan**: PLAN_PLAN-COMPLETION-VERIFICATION-AND-PROMPT-FIX.md  
**Achievement Addressed**: Achievement 2.1 (Add Completion Detection to Prompt Generator)  
**Status**: In Progress  
**Created**: 2025-11-08  
**Estimated Effort**: 1-2 hours

---

## 🎯 Objective

Add completion detection function to prompt generator and integrate it with the prompt generation workflow. This will enable the prompt generator to detect when a PLAN is complete and return an appropriate completion message instead of trying to generate a prompt for a non-existent next achievement. This addresses Bug #2 from the analysis documents.

**Contribution to PLAN**: This is Priority 2 (Prompt Generator Completion Detection) that creates the foundation for proper completion handling. By detecting completion before generating prompts, we prevent the prompt generator from returning wrong achievements (like 0.1) when a PLAN is actually complete.

---

## 📋 What Needs to Be Created

### Files to Update

1. **LLM/scripts/generation/generate_prompt.py**
   - Add `is_plan_complete(plan_content: str, achievements: List[Achievement]) -> bool` function
   - Update `find_next_achievement_hybrid()` to check completion first
   - Update `generate_prompt()` to handle completion and return completion message

### Content to Include

**is_plan_complete() function**:
- Extract handoff section using `extract_handoff_section()` helper
- Check for explicit completion indicators:
  - "All.*achievements.*complete"
  - "All Priority.*complete"
  - "PLAN.*complete"
  - "Status.*Complete"
- Check completion percentage (e.g., "7/7 complete", "X/Y achievements")
- Count completed achievements in handoff (✅ Achievement X.Y)
- Return True if all achievements complete

**find_next_achievement_hybrid() updates**:
- Check if PLAN is complete FIRST (before finding next achievement)
- If complete: Return None (indicates completion)
- If incomplete: Continue with normal flow

**generate_prompt() updates**:
- Check if PLAN is complete before generating prompt
- If complete: Return completion message (guide to END_POINT protocol)
- If incomplete: Generate achievement prompt as usual

---

## 📝 Approach

**Strategy**: Add completion detection function following patterns from `validate_plan_completion.py` and integrate it into the prompt generation workflow.

**Method**:

1. **Create Completion Detection Function**: Implement `is_plan_complete()` to check handoff section for completion indicators
2. **Integrate with Hybrid Function**: Update `find_next_achievement_hybrid()` to check completion first
3. **Update Prompt Generation**: Modify `generate_prompt()` to handle completion and return appropriate message
4. **Test**: Test with complete PLAN (`PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md`) and incomplete PLAN (`PLAN_METHODOLOGY-V2-ENHANCEMENTS.md`)

**Key Considerations**:

- **Consistency**: Use existing `extract_handoff_section()` helper function
- **Pattern Matching**: Use regex patterns to detect various completion formats
- **Completion Message**: Provide clear guidance to END_POINT protocol
- **Backward Compatibility**: Don't break existing functionality for incomplete PLANs

**Risks to Watch For**:

- False positives (detecting completion when PLAN is incomplete)
- False negatives (not detecting completion when PLAN is complete)
- Breaking existing prompt generation for incomplete PLANs

---

## 🧪 Tests Required (Validation Approach)

**Validation Method** (code work):

**Functionality Check**:
- [ ] `is_plan_complete()` function created
- [ ] Function correctly detects complete PLANs
- [ ] Function correctly detects incomplete PLANs
- [ ] `find_next_achievement_hybrid()` checks completion first
- [ ] `generate_prompt()` returns completion message for complete PLANs
- [ ] `generate_prompt()` generates achievement prompt for incomplete PLANs

**Integration Validation**:
- [ ] Completion detection doesn't break existing functionality
- [ ] Completion message is clear and actionable
- [ ] Tests pass with complete and incomplete PLANs

**Review Against Requirements**:
- [ ] Achievement 2.1 requirements met
- [ ] Success criteria from PLAN met
- [ ] All deliverables present

**Verification Commands**:
```bash
# Verify script exists and works
ls -1 LLM/scripts/generation/generate_prompt.py

# Test with complete PLAN (should return completion message)
python LLM/scripts/generation/generate_prompt.py PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md --next
# Expected: Completion message, not achievement prompt

# Test with incomplete PLAN (should generate achievement prompt)
python LLM/scripts/generation/generate_prompt.py PLAN_METHODOLOGY-V2-ENHANCEMENTS.md --next
# Expected: Achievement prompt, not completion message
```

---

## ✅ Expected Results

### Functional Changes

- **Completion Detection Function**: `is_plan_complete()` function added
- **Completion Check in Hybrid**: `find_next_achievement_hybrid()` checks completion first
- **Completion Message**: `generate_prompt()` returns completion message for complete PLANs
- **Backward Compatibility**: Incomplete PLANs still generate achievement prompts

### Observable Outcomes

- `is_plan_complete()` function exists in `generate_prompt.py`
- Complete PLANs return completion message (not achievement prompt)
- Incomplete PLANs still generate achievement prompts (no regression)
- Completion message guides to END_POINT protocol

### Success Indicators

- ✅ `is_plan_complete()` function created
- ✅ Function detects complete PLANs correctly
- ✅ Function detects incomplete PLANs correctly
- ✅ `find_next_achievement_hybrid()` checks completion first
- ✅ `generate_prompt()` handles completion correctly
- ✅ All verification commands pass

---

## 🔍 Conflict Analysis with Other Subplans

**Review Existing Subplans**:
- SUBPLAN_11: Achievement 1.1 (Create validate_plan_completion.py) - ✅ Complete

**Check for**:
- **Overlap**: No overlap (different focus: validation script vs prompt generator)
- **Conflicts**: None
- **Dependencies**: Uses `extract_handoff_section()` helper (already exists)
- **Integration**: Can work independently

**Analysis**:
- No conflicts detected
- Independent work (updating prompt generator)
- Safe to proceed

**Result**: Safe to proceed

---

## 🔗 Dependencies

### Other Subplans
- None (independent work)

### External Dependencies
- Python standard library (re, pathlib)
- Existing `extract_handoff_section()` helper function
- Existing `find_next_achievement_hybrid()` function

### Prerequisite Knowledge
- Understanding of prompt generator structure
- Understanding of completion detection patterns
- Understanding of handoff section format

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

_None yet - will be created when execution starts_

**First Execution**: `EXECUTION_TASK_PLAN-COMPLETION-VERIFICATION-AND-PROMPT-FIX_21_01.md`

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] `is_plan_complete()` function created
- [ ] Function correctly detects complete PLANs
- [ ] Function correctly detects incomplete PLANs
- [ ] `find_next_achievement_hybrid()` checks completion first
- [ ] `generate_prompt()` returns completion message for complete PLANs
- [ ] `generate_prompt()` generates achievement prompt for incomplete PLANs
- [ ] All verification commands pass
- [ ] EXECUTION_TASK complete
- [ ] Ready for archive

---

## 📝 Notes

**Common Pitfalls**:
- False positives (detecting completion when incomplete)
- False negatives (not detecting completion when complete)
- Breaking existing functionality
- Not handling edge cases (missing handoff section, etc.)

**Resources**:
- PLAN_PLAN-COMPLETION-VERIFICATION-AND-PROMPT-FIX.md (Achievement 2.1 section)
- LLM/scripts/generation/generate_prompt.py (existing code)
- LLM/scripts/validation/validate_plan_completion.py (pattern reference)
- PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md (test case: complete PLAN)
- PLAN_METHODOLOGY-V2-ENHANCEMENTS.md (test case: incomplete PLAN)
- EXECUTION_ANALYSIS_PROMPT-GENERATOR-REGRESSION-BUG-2.md (Bug #2 analysis)

---

## 📖 What to Read (Focus Rules)

**When working on this SUBPLAN**, follow these focus rules to minimize context:

**✅ READ ONLY**:
- This SUBPLAN file (complete file)
- Parent PLAN Achievement 2.1 section (36 lines)
- Active EXECUTION_TASKs (if any exist)
- Parent PLAN "Current Status & Handoff" section (18 lines)
- LLM/scripts/generation/generate_prompt.py (relevant sections only)
- LLM/scripts/validation/validate_plan_completion.py (for pattern reference - minimal reading)

**❌ DO NOT READ**:
- Parent PLAN full content
- Other achievements in PLAN
- Other SUBPLANs
- Completed EXECUTION_TASKs (unless needed for context)
- Full validation directory (only pattern reference)

**Context Budget**: ~400 lines

**Why**: SUBPLAN defines HOW to achieve one achievement. Reading other achievements or full PLAN adds scope and confusion.

**📖 See**: `LLM/guides/FOCUS-RULES.md` for complete focus rules and examples.

---

## 🔄 Active EXECUTION_TASKs (Updated When Created)

**Current Active Work** (register EXECUTION_TASKs immediately when created):

- [ ] **EXECUTION_TASK_PLAN-COMPLETION-VERIFICATION-AND-PROMPT-FIX_21_01**: Status: In Progress

**Registration Workflow**:

1. When creating EXECUTION_TASK: Add to this list immediately
2. When archiving: Remove from this list

**Why**: Immediate parent awareness ensures SUBPLAN knows about its active EXECUTION_TASKs.

---

**Ready to Execute**: Create EXECUTION_TASK and begin work  
**Reference**: IMPLEMENTATION_START_POINT.md for workflows

