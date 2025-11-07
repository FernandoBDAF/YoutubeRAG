# SUBPLAN: Meta-PLAN Predefined Prompts

**Mother Plan**: PLAN_LLM-V2-BACKLOG.md  
**Parent GrammaPlan**: GRAMMAPLAN_LLM-METHODOLOGY-V2.md  
**Achievement Addressed**: Achievement 1.1 (Meta-PLAN Predefined Prompts)  
**Backlog Item**: IMPL-METHOD-003  
**Status**: Ready  
**Created**: 2025-11-07  
**Estimated Effort**: 8-12 hours

---

## 🎯 Objective

Create standard, reusable prompt templates for common LLM development methodology workflows. These prompts will guide LLMs through complex processes (creating plans, resuming work, completing work, creating GrammaPlans, analyzing code) with consistent quality and fewer errors. Integration into methodology documents ensures prompts are discoverable and easy to use.

---

## 📋 What Needs to Be Created

### Files to Create

1. **LLM/templates/PROMPTS.md**: Central prompt library
   - 5+ prompt categories (Create, Resume, Complete, GrammaPlan, Analyze)
   - Each prompt includes: purpose, when to use, template with placeholders, example usage
   - Copy-paste ready format
   - Integration guidance

### Prompt Categories to Create

**1. Create New PLAN**

```
Prompt: "Create a new PLAN for [FEATURE] following @LLM/protocols/IMPLEMENTATION_START_POINT.md"
- Guides through: GrammaPlan decision, PLAN creation, achievement listing
- Output: PLAN_[FEATURE].md file
```

**2. Resume Paused PLAN**

```
Prompt: "Resume @PLAN_[FEATURE].md following @LLM/protocols/IMPLEMENTATION_RESUME.md protocol"
- Guides through: Pre-resume checklist, dependency check, context gathering
- Output: Resumed work with proper protocol adherence
```

**3. Complete PLAN**

```
Prompt: "Complete @PLAN_[FEATURE].md following @LLM/protocols/IMPLEMENTATION_END_POINT.md"
- Guides through: Pre-completion review, quality analysis, archiving
- Output: Archived plan with complete wrapup
```

**4. Create GrammaPlan**

```
Prompt: "Create a GrammaPlan for [INITIATIVE] using @GRAMMAPLAN-TEMPLATE.md"
- Guides through: Decision criteria, child PLAN planning, coordination
- Output: GRAMMAPLAN_[INITIATIVE].md file
```

**5. Analyze Code/Plan**

```
Prompt: "Analyze @[FILE/PLAN] for [PURPOSE] and create EXECUTION_ANALYSIS"
- Guides through: Analysis structure, findings documentation, recommendations
- Output: EXECUTION_ANALYSIS_[TOPIC].md file
```

**6. Create SUBPLAN** (bonus)

```
Prompt: "Create SUBPLAN for Achievement X.Y in @PLAN_[FEATURE].md"
- Guides through: Approach definition, test requirements, deliverables
- Output: SUBPLAN_[FEATURE]_XX.md file
```

### Files to Modify

1. **IMPLEMENTATION_START_POINT.md**: Add "Predefined Prompts" section

   - Reference PROMPTS.md
   - Explain when to use predefined vs custom prompts
   - Include 1-2 examples

2. **IMPLEMENTATION_RESUME.md**: Add prompt example

   - Show "Resume PLAN_X" prompt usage
   - Demonstrate checklist automation

3. **IMPLEMENTATION_END_POINT.md**: Add prompt example

   - Show "Complete PLAN_X" prompt usage
   - Demonstrate wrapup automation

4. **LLM/guides/GRAMMAPLAN-GUIDE.md**: Add prompt reference
   - Link to "Create GrammaPlan" prompt
   - Show usage example

---

## 📝 Approach

**Strategy**: Research current workflows → Design prompts → Test prompts → Integrate → Document

**Method**:

### Phase 1: Research Current Workflows (1-2h)

1. **Analyze Methodology Documents**:

   - Read IMPLEMENTATION_START_POINT.md completely (understand PLAN creation flow)
   - Read IMPLEMENTATION_RESUME.md completely (understand resume flow)
   - Read IMPLEMENTATION_END_POINT.md completely (understand completion flow)
   - Read GRAMMAPLAN-GUIDE.md (understand GrammaPlan creation)

2. **Identify Common Steps**:

   - Extract step-by-step processes from each protocol
   - Identify decision points (if/then logic)
   - Note required actions vs optional
   - Find common patterns across workflows

3. **Define Prompt Structure**:
   - Purpose statement
   - When to use
   - Prerequisites
   - Step-by-step guidance
   - Expected outputs
   - Verification steps

### Phase 2: Design Prompts (3-4h)

1. **Create PLAN Prompt**:

   - Template: "Create a new PLAN for [FEATURE] following @LLM/protocols/IMPLEMENTATION_START_POINT.md"
   - Includes: GrammaPlan decision tree, PLAN structure, achievement listing
   - Placeholders: [FEATURE], [GOAL], [PRIORITY]
   - Example: Real PLAN creation (e.g., TEST-RUNNER)

2. **Resume PLAN Prompt**:

   - Template: "Resume @PLAN\_[FEATURE].md following @LLM/protocols/IMPLEMENTATION_RESUME.md protocol"
   - Includes: Pre-resume checklist (5 steps), context gathering, ACTIVE_PLANS update
   - Placeholders: [PLAN_FILE]
   - Example: Resuming entity resolution

3. **Complete PLAN Prompt**:

   - Template: "Complete @PLAN\_[FEATURE].md following @LLM/protocols/IMPLEMENTATION_END_POINT.md"
   - Includes: Pre-completion review, quality analysis, backlog extraction, archiving
   - Placeholders: [PLAN_FILE]
   - Example: CODE-QUALITY completion

4. **Create GrammaPlan Prompt**:

   - Template: "Create a GrammaPlan for [INITIATIVE] using @GRAMMAPLAN-TEMPLATE.md and @GRAMMAPLAN-GUIDE.md"
   - Includes: Decision criteria (>800 lines, >80h, 3+ domains), child PLAN breakdown
   - Placeholders: [INITIATIVE], [ESTIMATED_EFFORT]
   - Example: LLM-METHODOLOGY-V2 GrammaPlan

5. **Analyze Code/Plan Prompt**:

   - Template: "Analyze @[TARGET] for [PURPOSE] and create EXECUTION*ANALYSIS*[TOPIC].md"
   - Includes: Analysis structure, findings format, recommendations
   - Placeholders: [TARGET], [PURPOSE], [TOPIC]
   - Example: CODE-QUALITY completion review

6. **Create SUBPLAN Prompt** (bonus):
   - Template: "Create SUBPLAN for Achievement X.Y in @PLAN\_[FEATURE].md"
   - Includes: Objective, deliverables, approach, tests, conflict analysis
   - Placeholders: [ACHIEVEMENT], [PLAN_FILE]
   - Example: Entity resolution SUBPLAN

### Phase 3: Test Prompts (2-3h)

1. **Dry Run Testing**:

   - Mentally walk through each prompt
   - Verify all steps covered
   - Check placeholders clear
   - Ensure examples realistic

2. **LLM Testing** (if time permits):

   - Use prompts to create test artifacts
   - Verify output quality
   - Refine based on results

3. **Peer Review**:
   - Check prompts are self-explanatory
   - Verify no ambiguity
   - Ensure consistent format

### Phase 4: Integration (1-2h)

1. **Add to START_POINT.md**:

   - Section: "Using Predefined Prompts"
   - When to use (new users, consistency needed, complex workflows)
   - Link to PROMPTS.md
   - Example: "Create new PLAN" prompt

2. **Add to RESUME.md**:

   - Section: "Quick Resume with Prompt"
   - Show "Resume PLAN_X" prompt
   - Note: Prompt enforces checklist

3. **Add to END_POINT.md**:

   - Section: "Quick Completion with Prompt"
   - Show "Complete PLAN_X" prompt
   - Note: Prompt enforces wrapup

4. **Add to GRAMMAPLAN-GUIDE.md**:
   - Section: "Quick GrammaPlan Creation"
   - Link to "Create GrammaPlan" prompt

### Phase 5: Documentation (1h)

1. **Usage Guide in PROMPTS.md**:

   - How to use prompts effectively
   - When to customize vs use as-is
   - Troubleshooting common issues

2. **Examples Section**:
   - Real usage examples
   - Before/after comparisons
   - Common variations

**Key Considerations**:

- **Self-Contained**: Prompts should work without external context (reference @files clearly)
- **Placeholder Clarity**: Obvious what to replace ([FEATURE], [GOAL], etc.)
- **Example Quality**: Use real examples from our project
- **Consistency**: All prompts follow same format
- **Maintenance**: Note where prompts need updates when methodology changes

---

## 🧪 Tests Required

### Test Cases to Cover

1. **Create PLAN Prompt**:

   - Prompt correctly walks through START_POINT workflow
   - GrammaPlan decision included
   - Output matches PLAN template

2. **Resume PLAN Prompt**:

   - Prompt includes all 5 RESUME checklist steps
   - ACTIVE_PLANS update enforced
   - Dependencies checked

3. **Complete PLAN Prompt**:

   - Pre-Completion Review included
   - Quality analysis guided
   - Archiving process covered

4. **GrammaPlan Prompt**:

   - Decision criteria checked
   - Child PLAN breakdown guided
   - GRAMMAPLAN template followed

5. **Analyze Prompt**:
   - Analysis structure clear
   - Findings format consistent
   - Recommendations actionable

### Test-First Requirement

- [ ] Tests written before implementation (manual testing acceptable for prompts)
- [ ] Initial test run (dry run through each prompt)
- [ ] Tests define success criteria (does prompt produce expected output?)

**For this SUBPLAN**: Manual testing and dry runs are appropriate given the documentation nature of the work.

---

## ✅ Expected Results

### Functional Changes

1. **Prompt Library Exists**: LLM/templates/PROMPTS.md with 5-6 prompt categories
2. **Prompts Integrated**: START_POINT, RESUME, END_POINT reference PROMPTS.md
3. **Prompts Tested**: Each prompt dry-run tested for completeness

### Observable Outcomes

1. **Faster PLAN Creation**: Users can copy/paste prompt instead of manually constructing
2. **Consistent Execution**: Prompts enforce protocol adherence automatically
3. **Lower Error Rate**: Predefined prompts reduce human error in complex workflows
4. **Better Onboarding**: New users/LLMs can follow prompts without deep methodology knowledge

### Deliverables

- `LLM/templates/PROMPTS.md` (300-400 lines with all prompts + examples)
- Updated `IMPLEMENTATION_START_POINT.md` (~20 lines added)
- Updated `IMPLEMENTATION_RESUME.md` (~15 lines added)
- Updated `IMPLEMENTATION_END_POINT.md` (~15 lines added)
- Updated `LLM/guides/GRAMMAPLAN-GUIDE.md` (~10 lines added)

---

## 🔍 Conflict Analysis with Other Subplans

**Review Existing Subplans**:

- SUBPLAN_LLM-V2-BACKLOG_01 (Reference Verification) - ✅ Complete

**Check for**:

- **Overlap**: None (reference verification vs prompt creation)
- **Conflicts**: None (different deliverables)
- **Dependencies**: None (prompts are independent of reference audit)
- **Integration**: Prompts will reference verified documentation (all refs now valid ✅)

**Analysis**: No conflicts detected. Safe to proceed.

---

## 🔗 Dependencies

### Other Subplans

- SUBPLAN_LLM-V2-BACKLOG_01 (Reference Verification) - ✅ Complete (ensures all methodology doc refs are valid)

### External Dependencies

- All methodology documents exist (START_POINT, END_POINT, RESUME, templates)
- GrammaPlan methodology defined (GRAMMAPLAN-GUIDE, template)

### Prerequisite Knowledge

- Structured LLM development methodology concepts
- Workflow steps in each protocol document
- Real-world examples from executed PLANs

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

- **EXECUTION_TASK_LLM-V2-BACKLOG_02_01**: First execution attempt - Status: [Pending]

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] PROMPTS.md created with 5-6 prompt categories
- [ ] Each prompt includes: purpose, when to use, template, placeholders, example
- [ ] Prompts tested (dry run or real usage)
- [ ] Integration complete (START_POINT, RESUME, END_POINT, GRAMMAPLAN-GUIDE updated)
- [ ] All expected results achieved
- [ ] EXECUTION_TASK complete
- [ ] PLAN updated (achievement 1.1 marked complete, statistics updated)
- [ ] Ready for next achievement

---

## 📝 Notes

**Common Pitfalls**:

- Making prompts too verbose (keep concise, reference @files for details)
- Not enough placeholders (users shouldn't guess what to fill in)
- Examples too complex (use simple, clear examples)
- Forgetting integration (prompts must be discoverable in workflows)

**Resources**:

- Real PLANs in root (examples of PLAN creation)
- Archived PLANs (examples of completion)
- EXECUTION_ANALYSIS documents (examples of analysis)
- Recent work: CODE-QUALITY, PIPELINE-VISUALIZATION completions

**Time Management**:

- Phase 1 (Research): 1-2h → Read protocols, identify patterns
- Phase 2 (Design): 3-4h → Create 5-6 prompts with examples
- Phase 3 (Test): 2-3h → Dry run, refine
- Phase 4 (Integration): 1-2h → Update methodology docs
- Phase 5 (Documentation): 1h → Usage guide

**If Running Over Time**:

- Prioritize: Create, Resume, Complete prompts (core workflows)
- Defer: Analyze, SUBPLAN prompts (nice-to-have)
- Focus: Quality over quantity (3 excellent prompts > 6 mediocre)

---

**Ready to Execute**: Create EXECUTION_TASK and begin research phase  
**Reference**: IMPLEMENTATION_START_POINT.md, IMPLEMENTATION_RESUME.md, IMPLEMENTATION_END_POINT.md  
**Mother PLAN**: PLAN_LLM-V2-BACKLOG.md (update after completion)  
**Parent GrammaPlan**: GRAMMAPLAN_LLM-METHODOLOGY-V2.md (feeds into AUTOMATION plan)
