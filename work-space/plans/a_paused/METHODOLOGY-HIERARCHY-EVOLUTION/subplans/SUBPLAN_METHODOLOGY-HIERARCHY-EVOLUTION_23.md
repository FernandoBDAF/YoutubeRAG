# SUBPLAN: Existing Prompt Generator Enhanced

**Parent PLAN**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md  
**Achievement**: 2.3  
**Created**: 2025-11-08 17:15 UTC  
**Estimated Effort**: 3-4 hours  
**Status**: 🎯 Executing

---

## 🎯 Objective

Update existing `generate_prompt.py` to understand new workflow separation where SUBPLAN (Designer) and EXECUTION (Executor) operate independently.

**Context**: New workflow separates SUBPLAN from EXECUTION. Main prompt generator must detect workflow state and suggest appropriate next step (create SUBPLAN, create EXECUTION, continue EXECUTION, or move to next achievement).

**Why This Matters**: 
- Main prompt generator is entry point for most users
- Must understand new workflow to guide correctly
- Enables seamless transition to new workflow
- Supports both Designer and Executor agents

---

## 📦 Deliverables

### Primary Deliverables

1. **Updated `LLM/scripts/generation/generate_prompt.py`**
   - Detect if achievement has SUBPLAN
     - If no SUBPLAN: Suggest creating SUBPLAN first
     - If SUBPLAN exists, no active EXECUTION: Suggest creating EXECUTION from SUBPLAN
     - If active EXECUTION: Suggest continuing EXECUTION
     - If SUBPLAN complete: Move to next achievement
   - Add `--subplan-only` flag: Generate prompt for SUBPLAN work only
   - Add `--execution-only` flag: Generate prompt for EXECUTION work only
   - Update context generation (PLAN for SUBPLAN, SUBPLAN for EXECUTION)
   - Support multi-execution detection
   - Update documentation in script

---

## 🎨 Approach

### Phase 1: Workflow Detection Logic (1.5h)

**Add Workflow Detection**:
- Check if SUBPLAN exists for achievement
- Check if SUBPLAN has active EXECUTIONs
- Check if SUBPLAN is complete
- Determine next step based on state

**Implementation**:
- Add function to detect SUBPLAN for achievement
- Add function to check SUBPLAN status
- Add function to check active EXECUTIONs
- Add function to determine next step

### Phase 2: Flag Implementation (1h)

**Add Flags**:
- `--subplan-only`: Generate prompt for SUBPLAN work (use generate_subplan_prompt.py)
- `--execution-only`: Generate prompt for EXECUTION work (use generate_execution_prompt.py)

**Implementation**:
- Add argparse flags
- Integrate with generate_subplan_prompt.py
- Integrate with generate_execution_prompt.py
- Handle flag combinations

### Phase 3: Context Generation Updates (0.5h)

**Update Context Generation**:
- For SUBPLAN: Use PLAN context (achievement section)
- For EXECUTION: Use SUBPLAN context (objective + approach only)
- Support multi-execution detection

**Implementation**:
- Update context extraction logic
- Add SUBPLAN context extraction
- Add multi-execution detection
- Update prompt generation

### Phase 4: Documentation and Testing (0.5h)

**Update Documentation**:
- Update script docstring
- Update help text
- Add examples for new flags

**Testing**:
- Test workflow detection
- Test flag combinations
- Test context generation

---

## 🧪 Tests Required

### Validation Tests

**1. Workflow Detection Test**:
- [ ] Detects missing SUBPLAN correctly
- [ ] Detects SUBPLAN without EXECUTION correctly
- [ ] Detects active EXECUTION correctly
- [ ] Detects complete SUBPLAN correctly

**2. Flag Functionality Test**:
- [ ] `--subplan-only` flag works
- [ ] `--execution-only` flag works
- [ ] Flags integrate with prompt generators correctly

**3. Context Generation Test**:
- [ ] PLAN context for SUBPLAN correct
- [ ] SUBPLAN context for EXECUTION correct (minimal)
- [ ] Multi-execution detection works

### Manual Validation

**Test Script Usability**:
1. Run with achievement without SUBPLAN
2. Run with SUBPLAN without EXECUTION
3. Run with active EXECUTION
4. Run with --subplan-only flag
5. Run with --execution-only flag
6. Verify prompts are appropriate

---

## 🎯 Expected Results

### Immediate Outcomes

**Script Updated**:
- Workflow detection implemented
- Flags added and integrated
- Context generation updated
- Documentation updated

**Quality Metrics**:
- Correctly detects workflow state
- Generates appropriate prompts
- Flags work as expected
- Documentation clear

---

## 📋 Definition of Done

**All deliverables exist**:
- [ ] `LLM/scripts/generation/generate_prompt.py` updated

**Quality standards met**:
- [ ] Workflow detection implemented
- [ ] `--subplan-only` flag works
- [ ] `--execution-only` flag works
- [ ] Context generation updated
- [ ] Documentation updated

**Validation passed**:
- [ ] Manual test: Workflow detection works
- [ ] Manual test: Flags work correctly
- [ ] File checks: Script exists (`ls -1`)

**Documentation complete**:
- [ ] Script understands workflow separation
- [ ] Flags documented
- [ ] Examples provided

---

## 🎓 Success Criteria

**Functional Success**:
- Script detects workflow state correctly
- Flags generate appropriate prompts
- Context generation supports new workflow

**Quality Success**:
- Detection logic accurate
- Flags integrate seamlessly
- Documentation clear

**Adoption Success**:
- Script used as entry point
- Workflow separation understood
- Both Designer and Executor supported

---

## 📚 References

**Parent PLAN**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md (Achievement 2.3)

**Related Documents**:
- `LLM/scripts/generation/generate_prompt.py` (to update)
- `LLM/scripts/generation/generate_subplan_prompt.py` (to integrate)
- `LLM/scripts/generation/generate_execution_prompt.py` (to integrate)
- `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` (reference for workflow)

**Workflow Context**:
- Designer creates SUBPLAN (from PLAN)
- Executor creates EXECUTION (from SUBPLAN)
- Workflow separation enables independent operation

---

## 🔄 Execution Plan

**Single EXECUTION_TASK** (recommended):
- All work is cohesive (updating script)
- Sequential phases (detection → flags → context → docs)
- Estimated 3-4 hours (fits in single execution)

**Recommended**: Single execution for cohesion

---

**Status**: Ready for execution  
**Next**: Create EXECUTION_TASK_METHODOLOGY-HIERARCHY-EVOLUTION_23_01.md and execute

