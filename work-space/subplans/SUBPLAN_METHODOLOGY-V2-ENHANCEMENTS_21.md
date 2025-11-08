# SUBPLAN: Tree Hierarchy Focus Rules

**Mother Plan**: PLAN_METHODOLOGY-V2-ENHANCEMENTS.md  
**Achievement Addressed**: Achievement 2.1 (Tree Hierarchy Focus Rules)  
**Status**: In Progress  
**Created**: 2025-11-07  
**Estimated Effort**: 3 hours

---

## 🎯 Objective

Document and integrate explicit rules for LLM context focus based on the current hierarchy level (GrammaPlan, PLAN, SUBPLAN, EXECUTION_TASK). This ensures LLMs focus exclusively on the lowest open component and don't look up the tree until work is complete.

---

## 📋 What Needs to Be Created

### Files to Create

1. **LLM/guides/FOCUS-RULES.md**:
   - New guide document
   - Defines focus rules for each hierarchy level
   - Explains why focus is critical
   - Provides examples and anti-patterns

### Files to Modify

1. **LLM/templates/PLAN-TEMPLATE.md**:
   - Add "What to Read" section
   - Document focus rules for PLAN level

2. **LLM/templates/SUBPLAN-TEMPLATE.md**:
   - Add "What to Read" section
   - Document focus rules for SUBPLAN level

3. **LLM/templates/EXECUTION_TASK-TEMPLATE.md**:
   - Add "What to Read" section
   - Document focus rules for EXECUTION_TASK level

---

## 📝 Approach

**Strategy**: Create comprehensive guide first, then integrate into templates

**Method**:

### Phase 1: Create Focus Rules Guide (1.5 hours)

**Goal**: Document complete focus rules for all hierarchy levels

**Steps**:
1. Create LLM/guides/FOCUS-RULES.md
2. Define rules for each level:
   - **EXECUTION_TASK Level**: Focus ONLY on this EXECUTION_TASK
     - Read: This EXECUTION_TASK file only
     - Don't read: Parent SUBPLAN, parent PLAN, other EXECUTION_TASKs
     - Why: Smallest unit of focus, prevents context overload
   - **SUBPLAN Level**: Focus ONLY on this SUBPLAN
     - Read: This SUBPLAN, active EXECUTION_TASKs only
     - Don't read: Parent PLAN (except current achievement), other SUBPLANs
     - Why: Focused approach, prevents scope creep
   - **PLAN Level**: Focus on current achievement only
     - Read: Current achievement, current status, active SUBPLANs
     - Don't read: Other achievements, completed work, full plan
     - Why: Progressive disclosure, prevents context overload
   - **GrammaPlan Level**: Focus on child PLAN coordination
     - Read: GrammaPlan, active child PLAN status
     - Don't read: Child PLAN details, child SUBPLANs/EXECUTION_TASKs
     - Why: Strategic coordination, not implementation details
3. Add examples and anti-patterns
4. Add decision trees for "What should I read?"

**Test**: Guide is comprehensive and clear

### Phase 2: Integrate into Templates (1.5 hours)

**Goal**: Add "What to Read" sections to all templates

**Steps**:
1. Update PLAN-TEMPLATE.md:
   - Add "What to Read" section after "Context for LLM Execution"
   - List: Current achievement, current status, active SUBPLANs
   - Don't read: Other achievements, completed work
2. Update SUBPLAN-TEMPLATE.md:
   - Add "What to Read" section
   - List: This SUBPLAN, active EXECUTION_TASKs
   - Don't read: Parent PLAN (except achievement), other SUBPLANs
3. Update EXECUTION_TASK-TEMPLATE.md:
   - Add "What to Read" section
   - List: This EXECUTION_TASK only
   - Don't read: Parent SUBPLAN, parent PLAN, other EXECUTION_TASKs
4. Link to FOCUS-RULES.md guide in each template

**Test**: All templates have clear "What to Read" guidance

---

## ✅ Expected Results

### Functional Changes

1. **Focus Rules Guide**: Comprehensive guide exists
2. **Templates Updated**: All templates have "What to Read" sections
3. **Clear Guidance**: LLMs know exactly what to read at each level

### Observable Outcomes

1. **Reduced Context**: LLMs read only what's needed
2. **Better Focus**: No looking up tree until work complete
3. **Faster Execution**: Less reading = faster work

### Deliverables

- LLM/guides/FOCUS-RULES.md (new guide)
- LLM/templates/PLAN-TEMPLATE.md (updated with "What to Read")
- LLM/templates/SUBPLAN-TEMPLATE.md (updated with "What to Read")
- LLM/templates/EXECUTION_TASK-TEMPLATE.md (updated with "What to Read")

---

## 🧪 Tests Required

### Test File
- Manual verification (read files, check completeness)

### Test Cases to Cover

1. **Guide Complete**:
   - All 4 hierarchy levels documented
   - Examples and anti-patterns included
   - Decision trees clear

2. **Templates Updated**:
   - All 3 templates have "What to Read" sections
   - Sections are clear and actionable
   - Links to guide exist

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] FOCUS-RULES.md created and comprehensive
- [ ] PLAN-TEMPLATE.md updated with "What to Read"
- [ ] SUBPLAN-TEMPLATE.md updated with "What to Read"
- [ ] EXECUTION_TASK-TEMPLATE.md updated with "What to Read"
- [ ] All templates link to guide
- [ ] All tests pass
- [ ] EXECUTION_TASK complete with learnings
- [ ] Files archived immediately

---

## 📝 Notes

**Common Pitfalls**:
- Making rules too complex (keep simple and clear)
- Forgetting to update all templates
- Not providing examples

**Resources**:
- Current templates
- EXECUTION_ANALYSIS_METHODOLOGY-V2-ENHANCED-STRATEGY.md (Tier 1 insights)

---

**Ready to Execute**: Create EXECUTION_TASK and begin implementation  
**Reference**: 2-phase approach (Guide, Templates)  
**Mother PLAN**: PLAN_METHODOLOGY-V2-ENHANCEMENTS.md

