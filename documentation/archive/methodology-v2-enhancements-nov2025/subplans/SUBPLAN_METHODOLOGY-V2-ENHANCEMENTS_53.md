# SUBPLAN: Validation Visibility in Prompts

**Mother Plan**: PLAN_METHODOLOGY-V2-ENHANCEMENTS.md  
**Achievement Addressed**: Achievement 5.3 (Validation Visibility in Prompts)  
**Status**: In Progress  
**Created**: 2025-11-07  
**Estimated Effort**: 2 hours

---

## 🎯 Objective

Update all prompts in PROMPTS.md to explicitly mention validation scripts that will run, creating a deterrent effect and ensuring LLMs know validation is enforced.

---

## 📋 What Needs to Be Created

### Files to Update

1. **LLM/templates/PROMPTS.md**:
   - Update all 9 existing prompts (1-5, 8-11)
   - Update 3 new prompts from Achievement 4.1 (6-8)
   - Add "VALIDATION ENFORCEMENT" section to each prompt
   - List which validation scripts will run
   - Add clear "DO NOT skip" messaging

### Deliverables

- Updated LLM/templates/PROMPTS.md (12 prompts with validation sections)

---

## 📝 Approach

**Strategy**: Add validation enforcement sections to all prompts systematically

**Method**:

### Phase 1: Identify All Prompts (15 min)

**Goal**: List all prompts that need validation sections

**Steps**:
1. Read PROMPTS.md completely
2. Identify all prompt templates (numbered prompts)
3. Check which already have validation sections
4. Create checklist of prompts to update

**Test**: Complete list of 12 prompts identified

### Phase 2: Design Validation Section Template (15 min)

**Goal**: Create consistent validation section format

**Steps**:
1. Review validation scripts available (8 scripts)
2. Design section format:
   - "VALIDATION ENFORCEMENT:" header
   - List of scripts that will run
   - "If issues found: BLOCKS with error + fix prompt"
3. Determine which scripts apply to which prompts

**Test**: Template format defined

### Phase 3: Update All Prompts (60 min)

**Goal**: Add validation sections to all 12 prompts

**Steps**:
1. Update Prompt 1 (Create New PLAN)
2. Update Prompt 2 (Resume Paused PLAN)
3. Update Prompt 3 (Complete and Archive PLAN)
4. Update Prompt 4 (Create GrammaPlan)
5. Update Prompt 5 (Analyze Code/Plan)
6. Update Prompt 6 (Continue SUBPLAN) - from Achievement 4.1
7. Update Prompt 7 (Next Achievement) - from Achievement 4.1
8. Update Prompt 8 (Continue EXECUTION_TASK) - from Achievement 4.1
9. Update Prompt 9 (Create SUBPLAN)
10. Update Prompt 10 (Resume SUBPLAN)
11. Update Prompt 11 (Complete SUBPLAN)
12. Update Prompt 12 (Create EXECUTION_TASK)

**Test**: All prompts have validation sections

### Phase 4: Verify and Test (30 min)

**Goal**: Ensure all prompts are complete and correct

**Steps**:
1. Verify all 12 prompts have validation sections
2. Check script paths are correct (validation/ directory)
3. Verify format consistency
4. Test prompt readability

**Test**: All prompts verified

---

## ✅ Expected Results

### Functional Changes

1. **All Prompts Updated**: 12 prompts have validation sections
2. **Consistent Format**: All use same validation section structure
3. **Clear Messaging**: "DO NOT skip" messaging added

### Observable Outcomes

1. **Deterrent Effect**: LLMs know validation will run
2. **Clear Expectations**: LLMs know which scripts will check their work
3. **Better Compliance**: Prompts explicitly mention validation enforcement

### Deliverables

- LLM/templates/PROMPTS.md (12 prompts with validation sections)

---

## 🧪 Tests Required

### Test File
- Manual verification (check all prompts, verify format)

### Test Cases to Cover

1. **Completeness**:
   - All 12 prompts have validation sections
   - No prompts missing validation

2. **Format Consistency**:
   - All validation sections use same format
   - Script paths are correct (validation/ directory)

3. **Content Accuracy**:
   - Scripts listed are appropriate for each prompt
   - "DO NOT skip" messaging is clear

4. **Readability**:
   - Prompts are still readable with validation sections
   - Validation sections don't overwhelm prompts

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] All 12 prompts identified
- [ ] Validation section template designed
- [ ] All 12 prompts updated with validation sections
- [ ] All prompts verified and tested
- [ ] EXECUTION_TASK complete with learnings
- [ ] Files archived immediately

---

## 📝 Notes

**Common Pitfalls**:
- Forgetting to update some prompts
- Inconsistent format across prompts
- Wrong script paths (old vs new structure)

**Resources**:
- LLM/templates/PROMPTS.md
- LLM/scripts/validation/ directory (8 scripts)
- Achievement 4.1 prompts (6-8)

---

**Ready to Execute**: Create EXECUTION_TASK and begin implementation  
**Reference**: 4-phase approach (Identify, Design, Update, Verify)  
**Mother PLAN**: PLAN_METHODOLOGY-V2-ENHANCEMENTS.md

