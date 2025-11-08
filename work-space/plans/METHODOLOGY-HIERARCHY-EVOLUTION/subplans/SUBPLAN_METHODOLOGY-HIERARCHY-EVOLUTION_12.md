# SUBPLAN: SUBPLAN Template Enhanced for Multi-Execution

**Parent PLAN**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md  
**Achievement**: 1.2  
**Created**: 2025-11-08 13:45 UTC  
**Estimated Effort**: 3-4 hours  
**Status**: 🎯 Executing

---

## 🎯 Objective

Update SUBPLAN template to support independent operation and multi-execution coordination, enabling Designer agents to plan multiple EXECUTIONs (parallel or sequential).

**Context**: New workflow separates SUBPLAN (Designer) from EXECUTION (Executor). Template must support Designer planning multiple EXECUTIONs, tracking their progress, and synthesizing results.

**Why This Matters**:

- Enables multi-EXECUTION planning in SUBPLAN
- Supports parallel execution coordination
- Enables sequential execution dependencies
- Provides synthesis framework for results

---

## 📦 Deliverables

### Primary Deliverables

1. **Updated `LLM/templates/SUBPLAN-TEMPLATE.md`**
   - Size limit: 200-600 lines (was 200-400)
   - New section: "## 🔄 Execution Strategy"
     - Execution count (Single / Multiple)
     - Parallelization (Yes / No)
     - Rationale for multiple executions
     - Planned executions list
   - New section: "## 🔀 Planned Executions (If Multiple)"
     - List each EXECUTION_TASK with purpose, type, estimated time
     - Coordination strategy
   - New section: "## 🔄 Active EXECUTION_TASKs"
     - Real-time tracking of all EXECUTIONs
     - Status updates as EXECUTIONs progress
   - New section: "## 📊 Execution Results Synthesis"
     - Framework for synthesizing learnings
     - Compare results (if parallel experiments)
     - Recommend best approach
     - Document collective learnings
   - Updated "What to Read" for independent operation
   - Guidance on when to create multiple EXECUTIONs

---

## 🎨 Approach

### Phase 1: Template Structure Updates (1h)

**Update `LLM/templates/SUBPLAN-TEMPLATE.md`**:

**Changes**:

1. **Size Limit Update**:

   - Change: "Size: 200-400 lines" → "Size: 200-600 lines"
   - Rationale: Multi-execution planning needs more space

2. **Add "Execution Strategy" Section** (after Approach):

   ```markdown
   ## 🔄 Execution Strategy

   **Execution Count**: [Single / Multiple]

   **If Multiple**:

   - **Parallelization**: [Yes / No]
   - **Rationale**: [Why multiple executions?]
   - **Planned Executions**: [List]

   **If Single**:

   - **Rationale**: [Why single execution?]
   ```

3. **Add "Planned Executions" Section** (if multiple):

   ```markdown
   ## 🔀 Planned Executions (If Multiple)

   | EXECUTION            | Purpose   | Type                  | Estimated | Dependencies    |
   | -------------------- | --------- | --------------------- | --------- | --------------- |
   | EXECUTION_TASK_XX_01 | [Purpose] | [Sequential/Parallel] | [Time]    | [None/Previous] |
   | EXECUTION_TASK_XX_02 | [Purpose] | [Sequential/Parallel] | [Time]    | [None/Previous] |

   **Coordination Strategy**: [How executions coordinate]
   ```

4. **Add "Active EXECUTION_TASKs" Section**:

   ```markdown
   ## 🔄 Active EXECUTION_TASKs

   | EXECUTION            | Status   | Progress   | Notes   |
   | -------------------- | -------- | ---------- | ------- |
   | EXECUTION_TASK_XX_01 | [Status] | [Progress] | [Notes] |
   ```

5. **Add "Execution Results Synthesis" Section**:

   ```markdown
   ## 📊 Execution Results Synthesis

   **Review All Results**: [Summary of all EXECUTIONs]

   **Collective Learnings**: [What worked across all?]

   **Best Approach**: [If multiple, which worked best?]

   **Recommendations**: [What to adopt?]
   ```

**Implementation**:

- Read current SUBPLAN-TEMPLATE.md
- Add new sections in logical order
- Update size limit
- Add guidance and examples

### Phase 2: Content Development (1.5h)

**Develop Section Content**:

**Execution Strategy Section**:

- Clear decision criteria
- Examples for single vs. multiple
- Examples for parallel vs. sequential
- Rationale guidance

**Planned Executions Section**:

- Table format for clarity
- Purpose, type, time, dependencies
- Coordination strategy guidance

**Active EXECUTION_TASKs Section**:

- Real-time tracking format
- Status options (Planning, Executing, Complete, Failed)
- Progress indicators
- Notes for coordination

**Execution Results Synthesis Section**:

- Framework for reviewing results
- Comparison methodology (if parallel)
- Learning synthesis approach
- Decision documentation

**Implementation**:

- Write detailed content for each section
- Add examples throughout
- Ensure consistency with SUBPLAN-WORKFLOW-GUIDE.md

### Phase 3: Integration and Guidance (0.5h)

**Add Integration Points**:

- Reference SUBPLAN-WORKFLOW-GUIDE.md
- Link to EXECUTION_TASK template
- Reference decision trees from guide

**Add Guidance**:

- When to use single EXECUTION
- When to use multiple EXECUTIONs
- When parallel vs. sequential
- How to coordinate

**Update "What to Read"**:

- Document independent operation
- Note that SUBPLAN runs independently
- Execution reads SUBPLAN objective only

**Implementation**:

- Add cross-references
- Add guidance sections
- Update "What to Read" section
- Ensure consistency

---

## 🧪 Tests Required

### Validation Tests

**1. Template Completeness Test**:

- [ ] Size limit updated (200-600 lines)
- [ ] Execution Strategy section present
- [ ] Planned Executions section present (if multiple)
- [ ] Active EXECUTION_TASKs section present
- [ ] Execution Results Synthesis section present
- [ ] Guidance on multiple EXECUTIONs included

**2. Clarity Test**:

- [ ] Sections clear and actionable
- [ ] Examples helpful
- [ ] Decision criteria clear
- [ ] Coordination guidance useful

### Manual Validation

**Test Template Usability**:

1. Use template to create SUBPLAN with single EXECUTION
2. Use template to create SUBPLAN with multiple EXECUTIONs
3. Verify sections guide planning
4. Verify examples illuminate concepts

---

## 🎯 Expected Results

### Immediate Outcomes

**Template Updated**:

- Size limit: 200-600 lines
- Execution Strategy section added
- Multi-execution support sections added
- Synthesis framework provided
- Guidance on when to use multiple EXECUTIONs

**Quality Metrics**:

- Clear sections for multi-execution planning
- Actionable decision criteria
- Helpful examples
- Consistent with workflow guide

---

## 📋 Definition of Done

**All deliverables exist**:

- [ ] `LLM/templates/SUBPLAN-TEMPLATE.md` updated

**Quality standards met**:

- [ ] Size limit updated (200-600 lines)
- [ ] Execution Strategy section comprehensive
- [ ] Planned Executions section clear
- [ ] Active EXECUTION_TASKs section functional
- [ ] Execution Results Synthesis section helpful
- [ ] Guidance on multiple EXECUTIONs included

**Validation passed**:

- [ ] Manual test: Template supports single EXECUTION
- [ ] Manual test: Template supports multiple EXECUTIONs
- [ ] Manual test: Sections guide planning
- [ ] File checks: Template exists (`ls -1`)

**Documentation complete**:

- [ ] Multi-execution planning supported
- [ ] Coordination strategies documented
- [ ] Synthesis framework provided

---

## 🎓 Success Criteria

**Functional Success**:

- Template supports single EXECUTION
- Template supports multiple EXECUTIONs (parallel/sequential)
- Coordination strategies documented
- Synthesis framework provided

**Quality Success**:

- Sections comprehensive and clear
- Examples helpful
- Decision criteria actionable
- Consistent with workflow guide

**Adoption Success**:

- Future SUBPLANs use new sections
- Designers plan multiple EXECUTIONs when appropriate
- Coordination strategies followed
- Synthesis framework used

---

## 📚 References

**Parent PLAN**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md (Achievement 1.2)

**Related Documents**:

- `LLM/templates/SUBPLAN-TEMPLATE.md` (to update)
- `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` (reference for workflow)
- `LLM/templates/EXECUTION_TASK-TEMPLATE.md` (reference for execution structure)

**Workflow Context**:

- Designer creates SUBPLAN with execution plan
- Multiple EXECUTIONs can be planned (parallel/sequential)
- Executor executes according to plan
- Designer synthesizes results

---

## 🔄 Execution Plan

**Single EXECUTION_TASK** (recommended):

- All work is cohesive (updating template)
- Sequential phases (structure → content → integration)
- Estimated 3-4 hours (fits in single execution)

**Recommended**: Single execution for cohesion

---

**Status**: Ready for execution  
**Next**: Create EXECUTION_TASK_METHODOLOGY-HIERARCHY-EVOLUTION_12_01.md and execute
