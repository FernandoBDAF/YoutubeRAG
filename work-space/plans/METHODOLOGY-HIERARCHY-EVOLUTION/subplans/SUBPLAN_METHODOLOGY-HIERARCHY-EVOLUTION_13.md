# SUBPLAN: EXECUTION_TASK Template Enhanced for Independence

**Parent PLAN**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md  
**Achievement**: 1.3  
**Created**: 2025-11-08 14:30 UTC  
**Estimated Effort**: 2-3 hours  
**Status**: 🎯 Executing

---

## 🎯 Objective

Update EXECUTION_TASK template to support independent operation where Executor reads minimal SUBPLAN context (objective and approach only) and can coordinate parallel execution.

**Context**: New workflow separates SUBPLAN (Designer) from EXECUTION (Executor). Executor must read minimal SUBPLAN context (objective + approach summary), not full SUBPLAN. Template must support this minimal reading pattern and parallel execution coordination.

**Why This Matters**: 
- Enables Executor to work independently with minimal context
- Supports parallel execution (multiple Executors work simultaneously)
- Executor follows Designer's plan (no re-design during execution)
- Reduces context budget (Executor reads ~10 lines, not 400+)

---

## 📦 Deliverables

### Primary Deliverables

1. **Updated `LLM/templates/EXECUTION_TASK-TEMPLATE.md`**
   - New section: "## 📖 SUBPLAN Context"
     - Read SUBPLAN objective (1-2 sentences)
     - Read SUBPLAN approach summary (3-5 sentences)
     - Don't read full SUBPLAN (Designer already decided approach)
     - Guidance on minimal reading
   - New section: "## 🔀 Parallelization Context (If Applicable)"
     - Parallel group (which other EXECUTIONs run simultaneously)
     - Independence rationale (why this is independent)
     - Results comparison (how results will be compared in SUBPLAN)
   - Updated "What to Read" section:
     - Document SUBPLAN-based execution
     - Emphasize minimal reading (objective + approach only)
     - Note: Executor follows Designer's plan
   - Add guidance: "Read parent SUBPLAN objective and approach only, not full content"
   - Emphasize: Executor follows Designer's plan

---

## 🎨 Approach

### Phase 1: Template Structure Updates (1h)

**Update `LLM/templates/EXECUTION_TASK-TEMPLATE.md`**:

**Changes**:
1. **Add "SUBPLAN Context" Section** (after Objective):
   ```markdown
   ## 📖 SUBPLAN Context
   
   **Parent SUBPLAN**: [SUBPLAN file path]
   
   **SUBPLAN Objective** (read only this, 1-2 sentences):
   - [Copy SUBPLAN objective here]
   
   **SUBPLAN Approach Summary** (read only this, 3-5 sentences):
   - [Copy SUBPLAN approach summary here]
   
   **⚠️ DO NOT READ**: Full SUBPLAN (Designer already decided approach)
   ```

2. **Add "Parallelization Context" Section** (if applicable):
   ```markdown
   ## 🔀 Parallelization Context (If Applicable)
   
   **Parallel Group**: [Which other EXECUTIONs run simultaneously?]
   - EXECUTION_TASK_XX_01: [Purpose]
   - EXECUTION_TASK_XX_02: [Purpose] (this one)
   - EXECUTION_TASK_XX_03: [Purpose]
   
   **Independence Rationale**: [Why this EXECUTION is independent?]
   
   **Results Comparison**: [How results will be compared in SUBPLAN synthesis?]
   
   **If Not Parallel**: Remove this section or state "Single execution - no parallelization"
   ```

3. **Update "What to Read" Section**:
   - Document SUBPLAN-based execution
   - Emphasize minimal reading (objective + approach only)
   - Note: Executor follows Designer's plan
   - Update context budget (reduced from full SUBPLAN)

**Implementation**:
- Read current EXECUTION_TASK-TEMPLATE.md
- Add new sections in logical order
- Update "What to Read" section
- Add guidance and examples

### Phase 2: Content Development (1h)

**Develop Section Content**:

**SUBPLAN Context Section**:
- Clear guidance on what to read (objective + approach summary)
- Clear guidance on what NOT to read (full SUBPLAN)
- Rationale: Designer already decided approach
- Examples of minimal reading

**Parallelization Context Section**:
- How to identify parallel group
- How to document independence rationale
- How to document results comparison
- Examples for parallel vs. single execution

**Updated "What to Read" Section**:
- Document SUBPLAN-based execution pattern
- Emphasize minimal reading
- Note Executor follows Designer's plan
- Update context budget

**Implementation**:
- Write detailed content for each section
- Add examples throughout
- Ensure consistency with SUBPLAN-WORKFLOW-GUIDE.md

### Phase 3: Integration and Guidance (0.5h)

**Add Integration Points**:
- Reference SUBPLAN-WORKFLOW-GUIDE.md
- Link to SUBPLAN template
- Reference Phase 3 (Execution) from workflow guide

**Add Guidance**:
- How to read SUBPLAN objective
- How to read SUBPLAN approach summary
- How to identify parallel group
- How to document independence

**Emphasize Key Points**:
- Executor follows Designer's plan
- Minimal reading reduces context budget
- Parallel execution coordination

**Implementation**:
- Add cross-references
- Add guidance sections
- Emphasize key points
- Ensure consistency

---

## 🧪 Tests Required

### Validation Tests

**1. Template Completeness Test**:
- [ ] SUBPLAN Context section present
- [ ] Parallelization Context section present (if applicable)
- [ ] "What to Read" updated for SUBPLAN-based execution
- [ ] Guidance on minimal reading included
- [ ] Emphasis on following Designer's plan

**2. Clarity Test**:
- [ ] Sections clear and actionable
- [ ] Examples helpful
- [ ] Minimal reading guidance clear
- [ ] Parallel coordination guidance useful

### Manual Validation

**Test Template Usability**:
1. Use template to create EXECUTION_TASK with single execution
2. Use template to create EXECUTION_TASK with parallel execution
3. Verify sections guide minimal reading
4. Verify examples illuminate concepts

---

## 🎯 Expected Results

### Immediate Outcomes

**Template Updated**:
- SUBPLAN Context section added
- Parallelization Context section added
- "What to Read" updated for SUBPLAN-based execution
- Guidance on minimal reading included
- Emphasis on following Designer's plan

**Quality Metrics**:
- Clear sections for SUBPLAN-based execution
- Actionable minimal reading guidance
- Helpful examples
- Consistent with workflow guide

---

## 📋 Definition of Done

**All deliverables exist**:
- [ ] `LLM/templates/EXECUTION_TASK-TEMPLATE.md` updated

**Quality standards met**:
- [ ] SUBPLAN Context section comprehensive
- [ ] Parallelization Context section clear
- [ ] "What to Read" updated for SUBPLAN-based execution
- [ ] Guidance on minimal reading included
- [ ] Emphasis on following Designer's plan

**Validation passed**:
- [ ] Manual test: Template supports single execution
- [ ] Manual test: Template supports parallel execution
- [ ] Manual test: Sections guide minimal reading
- [ ] File checks: Template exists (`ls -1`)

**Documentation complete**:
- [ ] SUBPLAN-based execution supported
- [ ] Minimal reading pattern documented
- [ ] Parallel coordination supported

---

## 🎓 Success Criteria

**Functional Success**:
- Template supports SUBPLAN-based execution
- Template supports minimal reading (objective + approach only)
- Template supports parallel execution coordination
- Executor follows Designer's plan emphasized

**Quality Success**:
- Sections comprehensive and clear
- Examples helpful
- Minimal reading guidance actionable
- Consistent with workflow guide

**Adoption Success**:
- Future EXECUTION_TASKs use minimal SUBPLAN reading
- Executors follow Designer's plan
- Parallel execution coordination documented
- Context budget reduced

---

## 📚 References

**Parent PLAN**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md (Achievement 1.3)

**Related Documents**:
- `LLM/templates/EXECUTION_TASK-TEMPLATE.md` (to update)
- `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` (reference for workflow, Phase 3)
- `LLM/templates/SUBPLAN-TEMPLATE.md` (reference for SUBPLAN structure)

**Workflow Context**:
- Executor reads SUBPLAN objective (~2 sentences) and approach summary (~3-5 sentences)
- Executor does NOT read full SUBPLAN (Designer already decided approach)
- Executor follows Designer's plan
- Parallel execution: Multiple Executors work simultaneously

---

## 🔄 Execution Plan

**Single EXECUTION_TASK** (recommended):
- All work is cohesive (updating template)
- Sequential phases (structure → content → integration)
- Estimated 2-3 hours (fits in single execution)

**Recommended**: Single execution for cohesion

---

**Status**: Ready for execution  
**Next**: Create EXECUTION_TASK_METHODOLOGY-HIERARCHY-EVOLUTION_13_01.md and execute


