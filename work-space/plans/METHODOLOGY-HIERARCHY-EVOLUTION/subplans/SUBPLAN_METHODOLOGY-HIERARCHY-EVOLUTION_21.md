# SUBPLAN: SUBPLAN Prompt Generator Created

**Parent PLAN**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md  
**Achievement**: 2.1  
**Created**: 2025-11-08 15:15 UTC  
**Estimated Effort**: 4-5 hours  
**Status**: 🎯 Executing

---

## 🎯 Objective

Create prompt generator script for SUBPLAN lifecycle (create, continue, synthesize) that supports the new independent SUBPLAN workflow where Designer operates separately from Executor.

**Context**: New workflow separates SUBPLAN (Designer) from EXECUTION (Executor). Need prompt generator that supports SUBPLAN lifecycle independently, not tied to EXECUTION. Script must generate context-aware prompts for 3 modes: create SUBPLAN, continue SUBPLAN work, synthesize results.

**Why This Matters**: 
- Enables automation for SUBPLAN workflow
- Supports Designer agent independently
- Context-aware prompts reduce manual work
- Foundation for multi-agent coordination

---

## 📦 Deliverables

### Primary Deliverables

1. **`LLM/scripts/generation/generate_subplan_prompt.py`**
   - **Mode 1: Create SUBPLAN**
     - Input: PLAN file, achievement number
     - Output: Prompt to create SUBPLAN for specific achievement
     - Context: PLAN achievement section + current status (not full PLAN)
     - Instructions: Create SUBPLAN, design approach, plan executions
   - **Mode 2: Continue SUBPLAN**
     - Input: SUBPLAN file
     - Output: Prompt to continue SUBPLAN work
     - Context: SUBPLAN + active EXECUTIONs status
     - Instructions: Review design, plan next execution, or synthesize results
   - **Mode 3: Synthesize SUBPLAN**
     - Input: SUBPLAN file + completed EXECUTIONs
     - Output: Prompt to synthesize results from all EXECUTIONs
     - Context: SUBPLAN + all EXECUTION summaries
     - Instructions: Compare results, identify best approach, document learnings
   - Support `--clipboard` flag
   - Support `--next` flag (determine next step automatically)
   - Generate context-aware prompts based on SUBPLAN status

---

## 🎨 Approach

### Phase 1: Script Structure (1.5h)

**Create `LLM/scripts/generation/generate_subplan_prompt.py`**:

**Structure**:
- Command-line interface (argparse)
- Three modes: create, continue, synthesize
- Context extraction functions
- Prompt generation functions
- Clipboard support
- Auto-detect next step (`--next` flag)

**Implementation**:
- Study existing prompt generators for pattern
- Create script structure
- Implement argument parsing
- Add mode selection logic

### Phase 2: Mode 1 - Create SUBPLAN (1h)

**Implement Create Mode**:
- Parse PLAN file
- Extract achievement section (not full PLAN)
- Extract current status section
- Generate prompt with:
  - Context: Achievement section + current status
  - Instructions: Create SUBPLAN, design approach, plan executions
  - Reference to SUBPLAN template
  - Reference to SUBPLAN workflow guide

**Implementation**:
- Parse PLAN markdown
- Extract achievement section by number
- Extract current status
- Generate prompt template

### Phase 3: Mode 2 - Continue SUBPLAN (1h)

**Implement Continue Mode**:
- Parse SUBPLAN file
- Check SUBPLAN status
- Check active EXECUTIONs
- Determine next step:
  - If no EXECUTIONs: Plan first execution
  - If EXECUTIONs active: Monitor progress
  - If EXECUTIONs complete: Ready for synthesis
- Generate context-aware prompt

**Implementation**:
- Parse SUBPLAN markdown
- Check "Active EXECUTION_TASKs" section
- Determine SUBPLAN phase (Design, Execution Planning, Synthesis)
- Generate appropriate prompt

### Phase 4: Mode 3 - Synthesize SUBPLAN (1h)

**Implement Synthesize Mode**:
- Parse SUBPLAN file
- Find all completed EXECUTIONs
- Extract EXECUTION summaries
- Generate synthesis prompt:
  - Context: SUBPLAN + all EXECUTION summaries
  - Instructions: Compare results, identify best approach, document learnings
  - Reference to synthesis section in SUBPLAN template

**Implementation**:
- Parse SUBPLAN markdown
- Find EXECUTION_TASK files referenced
- Extract summaries from EXECUTIONs
- Generate synthesis prompt

### Phase 5: Flags and Integration (0.5h)

**Add Flags**:
- `--clipboard`: Copy prompt to clipboard
- `--next`: Auto-detect next step (use Mode 2 logic)

**Integration**:
- Test with real PLAN/SUBPLAN files
- Verify context extraction
- Verify prompt quality

---

## 🧪 Tests Required

### Validation Tests

**1. Script Functionality Test**:
- [ ] Mode 1 (create) works with PLAN file
- [ ] Mode 2 (continue) works with SUBPLAN file
- [ ] Mode 3 (synthesize) works with SUBPLAN + EXECUTIONs
- [ ] `--clipboard` flag works
- [ ] `--next` flag works

**2. Context Extraction Test**:
- [ ] Achievement section extracted correctly
- [ ] Current status extracted correctly
- [ ] Active EXECUTIONs detected correctly
- [ ] Completed EXECUTIONs found correctly

**3. Prompt Quality Test**:
- [ ] Prompts are context-aware
- [ ] Prompts reference correct templates/guides
- [ ] Prompts provide clear instructions

### Manual Validation

**Test Script Usability**:
1. Run Mode 1 with real PLAN
2. Run Mode 2 with real SUBPLAN
3. Run Mode 3 with real SUBPLAN + EXECUTIONs
4. Verify prompts are helpful

---

## 🎯 Expected Results

### Immediate Outcomes

**Script Created**:
- `generate_subplan_prompt.py` with 3 modes
- Context-aware prompt generation
- Clipboard and auto-detect support

**Quality Metrics**:
- Prompts are context-aware
- Clear instructions for each mode
- References to templates/guides
- Usable for automation

---

## 📋 Definition of Done

**All deliverables exist**:
- [ ] `LLM/scripts/generation/generate_subplan_prompt.py` created

**Quality standards met**:
- [ ] Mode 1 (create) implemented
- [ ] Mode 2 (continue) implemented
- [ ] Mode 3 (synthesize) implemented
- [ ] `--clipboard` flag works
- [ ] `--next` flag works
- [ ] Context extraction accurate

**Validation passed**:
- [ ] Manual test: All modes work
- [ ] Manual test: Prompts are helpful
- [ ] File checks: Script exists (`ls -1`)

**Documentation complete**:
- [ ] Script supports SUBPLAN lifecycle
- [ ] Context-aware prompts generated
- [ ] Ready for automation use

---

## 🎓 Success Criteria

**Functional Success**:
- Script generates prompts for all 3 modes
- Context extraction works correctly
- Flags work as expected

**Quality Success**:
- Prompts are context-aware
- Instructions are clear
- References are correct

**Adoption Success**:
- Script used for SUBPLAN automation
- Prompts help Designer agents
- Foundation for multi-agent coordination

---

## 📚 References

**Parent PLAN**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md (Achievement 2.1)

**Related Documents**:
- `LLM/scripts/generation/generate_prompt.py` (reference for pattern)
- `LLM/templates/SUBPLAN-TEMPLATE.md` (reference for structure)
- `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` (reference for workflow)

**Workflow Context**:
- Designer creates SUBPLAN (Mode 1)
- Designer continues SUBPLAN work (Mode 2)
- Designer synthesizes results (Mode 3)
- Executor works independently (not in this script)

---

## 🔄 Execution Plan

**Single EXECUTION_TASK** (recommended):
- All work is cohesive (creating script)
- Sequential phases (structure → modes → flags)
- Estimated 4-5 hours (fits in single execution)

**Recommended**: Single execution for cohesion

---

**Status**: Ready for execution  
**Next**: Create EXECUTION_TASK_METHODOLOGY-HIERARCHY-EVOLUTION_21_01.md and execute


