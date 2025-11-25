# SUBPLAN: Update PROMPTS.md with New Workflow

**Type**: SUBPLAN  
**Mother Plan**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md  
**Plan**: METHODOLOGY-HIERARCHY-EVOLUTION  
**Achievement Addressed**: Achievement 4.3 (PROMPTS.md Updated)  
**Achievement Number**: 4.3  
**Status**: 🎯 Ready to Execute  
**Created**: 2025-11-09 03:20 UTC  
**Estimated Effort**: 3-4 hours

**File Location**: `work-space/subplans/SUBPLAN_METHODOLOGY-HIERARCHY-EVOLUTION_43.md`

**Size**: ~320 lines

---

## 🎯 Objective

Update LLM/templates/PROMPTS.md to include new workflow prompts for the five-tier hierarchy and Designer/Executor phase separation, providing copy-paste-ready prompts for all common workflows.

---

## 📋 Deliverables

**Primary Deliverable**: Updated `LLM/templates/PROMPTS.md` with:
- New "Create NORTH_STAR" prompt
- Updated "Create New PLAN" prompt (900-line reference)
- New "Create SUBPLAN (Designer Phase)" prompt
- New "Create EXECUTION from SUBPLAN" prompt
- New "Synthesize SUBPLAN Results" prompt
- Updated existing prompts for new workflow
- Automation script examples

---

## 📝 Approach

**Strategy**: Systematic prompt addition and update

**Method**:

1. Read current PROMPTS.md structure (copy-paste format)
2. Identify all required new prompts from Achievement 4.3
3. Create NORTH_STAR creation prompt
4. Update PLAN creation prompt with new size limits
5. Create SUBPLAN Designer phase prompt
6. Create EXECUTION Executor phase prompt
7. Create SUBPLAN synthesis prompt
8. Update any existing prompts that reference old workflow
9. Verify all prompts are copy-paste ready and complete
10. Ensure consistency with new guides and protocols

**Key Considerations**:

- Prompts must be copy-paste ready (self-contained)
- Clear instructions for when to use each prompt
- Reference to guides/protocols where appropriate
- Minimal but complete context
- Examples where helpful

---

## 🔄 Execution Strategy

**Single Execution**: One EXECUTION_TASK

**Rationale**: Prompt work is linear and best done in single focused session. All prompts update consistently.

---

## ✅ Expected Results

**Success Criteria**:

- ✅ NORTH_STAR prompt present and complete
- ✅ PLAN prompt updated with 900-line reference
- ✅ SUBPLAN Designer phase prompt created
- ✅ EXECUTION Executor phase prompt created
- ✅ SUBPLAN synthesis prompt created
- ✅ All prompts are copy-paste ready
- ✅ Consistency with CREATE_SUBPLAN.md and CREATE_EXECUTION.md
- ✅ Automation script examples included

---

## 🧪 Test Plan

**Test 1**: Completeness
- Verify all 5 new/updated prompts present
- Check no prompts are incomplete

**Test 2**: Copy-Paste Readiness
- Verify each prompt stands alone
- Confirm context is complete
- Check formatting

**Test 3**: Consistency
- Verify prompts align with protocols
- Confirm references to guides are accurate
- Check Designer/Executor terminology

**Test 4**: Usage Clarity
- Verify "when to use" is clear
- Confirm instructions are actionable

---

**Status**: ✅ SUBPLAN Ready to Execute  
**Next**: EXECUTION_TASK_METHODOLOGY-HIERARCHY-EVOLUTION_43_01.md

