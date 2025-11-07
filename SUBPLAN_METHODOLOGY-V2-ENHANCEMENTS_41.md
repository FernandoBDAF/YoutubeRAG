# SUBPLAN: Session Entry Points for Active Work

**Mother Plan**: PLAN_METHODOLOGY-V2-ENHANCEMENTS.md  
**Achievement Addressed**: Achievement 4.1 (Session Entry Points for Active Work)  
**Status**: In Progress  
**Created**: 2025-11-07  
**Estimated Effort**: 3 hours

---

## 🎯 Objective

Create entry point documents that allow starting a new session and immediately resuming work on an open PLAN, SUBPLAN, or EXECUTION_TASK without needing to read the full PLAN. This includes quick-start guides and context-aware prompts.

---

## 📋 What Needs to Be Created

### Files to Create

1. **LLM/guides/SESSION-ENTRY-POINTS.md**:

   - Guide for resuming work on active components
   - Entry points: PLAN, SUBPLAN, EXECUTION_TASK
   - Quick context loading strategies
   - Prompt templates for each entry point

2. **LLM/scripts/generate_resume_prompt.py**:
   - Generates context-aware prompt for resuming work
   - Auto-detects component type (PLAN/SUBPLAN/EXECUTION_TASK)
   - Extracts minimal context needed
   - Includes validation checks

---

## 📝 Approach

**Strategy**: Create guide first, then build script

**Method**:

### Phase 1: Session Entry Points Guide (1.5 hours)

**Goal**: Document how to resume work on active components

**Steps**:

1. Create LLM/guides/SESSION-ENTRY-POINTS.md
2. Sections:
   - **Resuming a PLAN**: What to read, what to skip, prompt template
   - **Resuming a SUBPLAN**: What to read, what to skip, prompt template
   - **Resuming an EXECUTION_TASK**: What to read, what to skip, prompt template
   - **Context Loading**: Minimal context strategy
   - **Validation Before Resume**: Run validation scripts
3. Prompt templates include:
   - Context boundaries
   - What to read (minimal)
   - What NOT to read
   - Next steps
   - Validation checks

**Test**: Guide provides clear entry points for all component types

### Phase 2: Resume Prompt Generator Script (1.5 hours)

**Goal**: Automate prompt generation for resuming work

**Steps**:

1. Create LLM/scripts/generate_resume_prompt.py
2. Functions:
   - `detect_component_type(file_path)` → str (PLAN/SUBPLAN/EXECUTION_TASK)
   - `extract_plan_context(plan_path)` → dict (status, next achievement, progress)
   - `extract_subplan_context(subplan_path)` → dict (achievement, objective, status)
   - `extract_execution_context(execution_path)` → dict (iteration, status, next steps)
   - `generate_resume_prompt(component_path)` → str
3. CLI:
   - `python generate_resume_prompt.py @PLAN_FEATURE.md`
   - `python generate_resume_prompt.py @SUBPLAN_FEATURE_XX.md`
   - `python generate_resume_prompt.py @EXECUTION_TASK_FEATURE_XX_YY.md`
   - `--clipboard` flag to copy to clipboard
4. Prompt includes:
   - Context boundaries (what to read)
   - Current status
   - Next steps
   - Validation checks to run

**Test**: Script generates accurate, context-aware prompts

---

## ✅ Expected Results

### Functional Changes

1. **Session Entry Points Guide**: Clear documentation for resuming work
2. **Resume Prompt Generator**: Automated prompt generation

### Observable Outcomes

1. **Easy Resume**: Can start new session and immediately continue work
2. **Context-Aware**: Prompts include only necessary context
3. **Validation Integrated**: Prompts include validation checks

### Deliverables

- LLM/guides/SESSION-ENTRY-POINTS.md
- LLM/scripts/generate_resume_prompt.py

---

## 🧪 Tests Required

### Test File

- Manual verification (read guide, run script, verify prompts)

### Test Cases to Cover

1. **Guide Completeness**:

   - All 3 entry points documented (PLAN, SUBPLAN, EXECUTION_TASK)
   - Prompt templates provided
   - Context loading strategies clear

2. **Script Functionality**:
   - Detects component type correctly
   - Extracts context accurately
   - Generates prompts with proper boundaries
   - Includes validation checks

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] SESSION-ENTRY-POINTS.md created and comprehensive
- [ ] generate_resume_prompt.py created and working
- [ ] Guide covers all 3 entry points
- [ ] Script generates accurate prompts
- [ ] All tests pass
- [ ] EXECUTION_TASK complete with learnings
- [ ] Files archived immediately

---

## 📝 Notes

**Common Pitfalls**:

- Guide too verbose (should be quick reference)
- Script extracts too much context (defeats purpose)
- Missing validation checks in prompts

**Resources**:

- IMPLEMENTATION_RESUME.md (for resume workflow)
- FOCUS-RULES.md (for context boundaries)
- Existing prompt generator (generate_prompt.py) for reference

---

**Ready to Execute**: Create EXECUTION_TASK and begin implementation  
**Reference**: 2-phase approach (Guide, Script)  
**Mother PLAN**: PLAN_METHODOLOGY-V2-ENHANCEMENTS.md
