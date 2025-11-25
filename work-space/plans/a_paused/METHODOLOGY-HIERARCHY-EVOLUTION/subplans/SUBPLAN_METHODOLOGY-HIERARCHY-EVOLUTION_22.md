# SUBPLAN: EXECUTION Prompt Generator Created

**Parent PLAN**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md  
**Achievement**: 2.2  
**Created**: 2025-11-08 16:20 UTC  
**Estimated Effort**: 4-5 hours  
**Status**: 🎯 Executing

---

## 🎯 Objective

Create prompt generator script for EXECUTION lifecycle (create, continue, next) that supports Executor agents working independently with minimal SUBPLAN context.

**Context**: New workflow separates SUBPLAN (Designer) from EXECUTION (Executor). Executor reads minimal SUBPLAN context (objective + approach only, not full SUBPLAN). Script must generate prompts that enforce minimal reading and support parallel execution.

**Why This Matters**: 
- Enables automation for EXECUTION workflow
- Supports Executor agent independently
- Enforces minimal context reading (reduces context budget)
- Supports parallel execution coordination

---

## 📦 Deliverables

### Primary Deliverables

1. **`LLM/scripts/generation/generate_execution_prompt.py`**
   - **Mode 1: Create EXECUTION from SUBPLAN**
     - Input: SUBPLAN file, execution number
     - Output: Prompt to create and start EXECUTION_TASK
     - Context: SUBPLAN objective + approach (not full SUBPLAN)
     - Instructions: Execute according to SUBPLAN plan
     - Support parallel execution context
   - **Mode 2: Continue EXECUTION**
     - Input: EXECUTION_TASK file
     - Output: Prompt to continue EXECUTION work
     - Context: EXECUTION_TASK only (Executor stays focused)
     - Instructions: Continue iteration, document progress
   - **Mode 3: Next EXECUTION**
     - Input: SUBPLAN file
     - Output: Prompt to start next EXECUTION in sequence
     - Context: SUBPLAN + previous EXECUTION learnings
     - Instructions: Apply learnings from previous execution
   - Support `--clipboard` flag
   - Support `--parallel` flag (generate prompts for parallel executions)
   - Generate minimal context (Executor agent focus)

---

## 🎨 Approach

### Phase 1: Script Structure (1.5h)

**Create `LLM/scripts/generation/generate_execution_prompt.py`**:

**Structure**:
- Command-line interface (argparse)
- Three modes: create, continue, next
- Context extraction functions (minimal SUBPLAN reading)
- Prompt generation functions
- Clipboard support
- Parallel execution support

**Implementation**:
- Study generate_subplan_prompt.py for pattern
- Create script structure
- Implement argument parsing
- Add mode selection logic

### Phase 2: Mode 1 - Create EXECUTION (1h)

**Implement Create Mode**:
- Parse SUBPLAN file
- Extract objective (1-2 sentences only)
- Extract approach summary (3-5 sentences only)
- Extract parallelization context (if applicable)
- Generate prompt with:
  - Context: SUBPLAN objective + approach (minimal)
  - Instructions: Execute according to SUBPLAN plan
  - Reference to EXECUTION_TASK template
  - Parallel execution guidance (if applicable)

**Implementation**:
- Parse SUBPLAN markdown
- Extract "Objective" section (first 1-2 sentences)
- Extract "Approach" section summary (3-5 sentences)
- Extract "Parallelization Context" (if exists)
- Generate prompt template

### Phase 3: Mode 2 - Continue EXECUTION (1h)

**Implement Continue Mode**:
- Parse EXECUTION_TASK file
- Check execution status
- Determine next iteration
- Generate continue prompt:
  - Context: EXECUTION_TASK only
  - Instructions: Continue iteration, document progress
  - Reference to last iteration

**Implementation**:
- Parse EXECUTION_TASK markdown
- Find last iteration in log
- Determine next step
- Generate continue prompt

### Phase 4: Mode 3 - Next EXECUTION (1h)

**Implement Next Mode**:
- Parse SUBPLAN file
- Find previous EXECUTION(s)
- Extract learnings from previous EXECUTION(s)
- Generate next EXECUTION prompt:
  - Context: SUBPLAN objective + approach + previous learnings
  - Instructions: Apply learnings from previous execution
  - Reference to previous EXECUTION

**Implementation**:
- Parse SUBPLAN markdown
- Find EXECUTION_TASK files referenced
- Extract learnings from previous EXECUTION(s)
- Generate next EXECUTION prompt

### Phase 5: Flags and Integration (0.5h)

**Add Flags**:
- `--clipboard`: Copy prompt to clipboard
- `--parallel`: Generate prompts for parallel executions

**Integration**:
- Test with real SUBPLAN/EXECUTION files
- Verify minimal context extraction
- Verify prompt quality

---

## 🧪 Tests Required

### Validation Tests

**1. Script Functionality Test**:
- [ ] Mode 1 (create) works with SUBPLAN file
- [ ] Mode 2 (continue) works with EXECUTION_TASK file
- [ ] Mode 3 (next) works with SUBPLAN file
- [ ] `--clipboard` flag works
- [ ] `--parallel` flag works

**2. Context Extraction Test**:
- [ ] SUBPLAN objective extracted correctly (1-2 sentences)
- [ ] SUBPLAN approach extracted correctly (3-5 sentences)
- [ ] Parallelization context detected correctly
- [ ] Previous EXECUTION learnings extracted correctly

**3. Prompt Quality Test**:
- [ ] Prompts enforce minimal reading
- [ ] Prompts reference correct templates/guides
- [ ] Prompts provide clear instructions
- [ ] Parallel execution guidance included (if applicable)

### Manual Validation

**Test Script Usability**:
1. Run Mode 1 with real SUBPLAN
2. Run Mode 2 with real EXECUTION_TASK
3. Run Mode 3 with real SUBPLAN + previous EXECUTION
4. Verify prompts enforce minimal reading

---

## 🎯 Expected Results

### Immediate Outcomes

**Script Created**:
- `generate_execution_prompt.py` with 3 modes
- Minimal context prompt generation
- Clipboard and parallel support

**Quality Metrics**:
- Prompts enforce minimal reading (objective + approach only)
- Clear instructions for each mode
- References to templates/guides
- Usable for automation

---

## 📋 Definition of Done

**All deliverables exist**:
- [ ] `LLM/scripts/generation/generate_execution_prompt.py` created

**Quality standards met**:
- [ ] Mode 1 (create) implemented
- [ ] Mode 2 (continue) implemented
- [ ] Mode 3 (next) implemented
- [ ] `--clipboard` flag works
- [ ] `--parallel` flag works
- [ ] Minimal context extraction accurate

**Validation passed**:
- [ ] Manual test: All modes work
- [ ] Manual test: Prompts enforce minimal reading
- [ ] File checks: Script exists (`ls -1`)

**Documentation complete**:
- [ ] Script supports EXECUTION lifecycle
- [ ] Minimal context prompts generated
- [ ] Ready for automation use

---

## 🎓 Success Criteria

**Functional Success**:
- Script generates prompts for all 3 modes
- Minimal context extraction works correctly
- Flags work as expected

**Quality Success**:
- Prompts enforce minimal reading
- Instructions are clear
- References are correct

**Adoption Success**:
- Script used for EXECUTION automation
- Prompts help Executor agents
- Foundation for parallel execution

---

## 📚 References

**Parent PLAN**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md (Achievement 2.2)

**Related Documents**:
- `LLM/scripts/generation/generate_subplan_prompt.py` (reference for pattern)
- `LLM/templates/EXECUTION_TASK-TEMPLATE.md` (reference for structure)
- `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` (reference for workflow, Phase 3)

**Workflow Context**:
- Executor reads SUBPLAN objective (~2 sentences) + approach (~3-5 sentences) only
- Executor does NOT read full SUBPLAN (400-600 lines)
- Executor follows Designer's plan
- Parallel execution: Multiple Executors work simultaneously

---

## 🔄 Execution Plan

**Single EXECUTION_TASK** (recommended):
- All work is cohesive (creating script)
- Sequential phases (structure → modes → flags)
- Estimated 4-5 hours (fits in single execution)

**Recommended**: Single execution for cohesion

---

**Status**: Ready for execution  
**Next**: Create EXECUTION_TASK_METHODOLOGY-HIERARCHY-EVOLUTION_22_01.md and execute

