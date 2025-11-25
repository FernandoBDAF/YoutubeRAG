# SUBPLAN: [Brief Title]

**Type**: SUBPLAN  
**Mother Plan**: PLAN\_[FEATURE].md  
**Plan**: [FEATURE-NAME]  
**Achievement Addressed**: Achievement X.Y ([Achievement title])  
**Achievement**: [X.Y]  
**Status**: Not Started / In Progress / Complete  
**Created**: [YYYY-MM-DD HH:MM UTC]  
**Estimated Effort**: [X-Y hours]

**Metadata Tags**: See `LLM/guides/METADATA-TAGS.md` for virtual organization system

**File Location**: Create this SUBPLAN in `work-space/subplans/SUBPLAN_[FEATURE]_[NUMBER].md`

**Size**: 200-600 lines (increased to support multi-execution planning)

[FILL: Use UTC timestamps. Example: 2025-11-05 14:30 UTC]

[FILL: Brief title should describe what you're creating/doing. Achievement reference shows which goal this addresses.]

**Note**: This SUBPLAN operates independently - Designer creates design, plans execution(s), then Executor(s) execute. See `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` for complete workflow.

---

## 🎯 Objective

[FILL: 1 paragraph - what this subplan achieves and how it contributes to the mother PLAN]

**Example**:

> Create the user authentication service with JWT tokens, enabling secure API access. This implements Achievement 2.3 (Security Layer) and provides the foundation for user-specific features in the PLAN.

---

## 📋 What Needs to Be Created

[FILL: List specific deliverables - files, functions, features]

### Files to Create

- [FILL: New files]
- [FILL: Path and purpose for each]

### Files to Modify

- [FILL: Existing files to change]
- [FILL: What changes in each]

### Functions/Classes to Add

- [FILL: New functions/classes]
- [FILL: Signatures and purposes]

### Tests Required

- [FILL: Test files to create]
- [FILL: Test cases to cover]

[FILL: Be specific - this guides the EXECUTION_TASK]

---

## 📝 Approach

**Strategy**: [FILL: High-level approach - how you'll tackle this]

**Method**:

1. [FILL: Step 1]
2. [FILL: Step 2]
3. [FILL: Step 3]

**Key Considerations**:

- [FILL: Important factors]
- [FILL: Trade-offs]
- [FILL: Risks to watch for]

[FILL: Your specific approach to achieving the goal. Someone else might have a different approach for the same achievement.]

---

## 🔄 Execution Strategy

**Execution Count**: [Single / Multiple]

**If Single**:

- **Rationale**: [Why single execution?]
  - Example: "Single clear approach, straightforward implementation"
- **EXECUTION_TASK**: `EXECUTION_TASK_[FEATURE]_[SUBPLAN_NUMBER]_01.md`

**If Multiple**:

- **Parallelization**: [Yes / No]
- **Rationale**: [Why multiple executions?]
  - Example: "A/B testing two approaches", "Iterative refinement", "Parallel independent components"
- **Execution Type**: [Parallel / Sequential]
  - **Parallel**: Independent work, can run simultaneously
  - **Sequential**: Later executions depend on earlier results
- **Planned Executions**: See "Planned Executions" section below

**Decision Guidance**:

- **Single**: Clear approach, straightforward work, no comparison needed
- **Multiple - Parallel**: A/B testing, independent components, comparison needed
- **Multiple - Sequential**: Iterative refinement, later builds on earlier, progressive improvement

**See**: `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` for complete decision trees

---

## 🔀 Planned Executions (If Multiple)

**If execution count is "Multiple", document planned executions here:**

| EXECUTION                               | Purpose   | Type                  | Estimated | Dependencies                |
| --------------------------------------- | --------- | --------------------- | --------- | --------------------------- |
| EXECUTION*TASK*[FEATURE]\_[SUBPLAN]\_01 | [Purpose] | [Sequential/Parallel] | [X hours] | [None / Previous execution] |
| EXECUTION*TASK*[FEATURE]\_[SUBPLAN]\_02 | [Purpose] | [Sequential/Parallel] | [X hours] | [None / EXECUTION_01]       |
| EXECUTION*TASK*[FEATURE]\_[SUBPLAN]\_03 | [Purpose] | [Sequential/Parallel] | [X hours] | [None / EXECUTION_02]       |

**Coordination Strategy**:

- [How executions coordinate]
- [If parallel: How results will be compared]
- [If sequential: How later executions use earlier results]
- [How synthesis will proceed]

**Example (Parallel)**:

- EXECUTION_01: Test Algorithm A (baseline)
- EXECUTION_02: Test Algorithm B (optimized)
- EXECUTION_03: Test Algorithm C (alternative)
- Coordination: All run in parallel, results compared in synthesis

**Example (Sequential)**:

- EXECUTION_01: Implement baseline (accuracy: 75%)
- EXECUTION_02: Add fuzzy matching (uses baseline, accuracy: 82%)
- EXECUTION_03: Add embedding similarity (uses EXECUTION_02, accuracy: 90%)
- Coordination: Each builds on previous, progressive improvement

**If Single**: Remove this section or state "Single execution - see Execution Strategy above"

---

## 🧪 Tests Required

**Note**: Required for all code implementations, optional for documentation-only work.

### Test File

- [FILL: Path to test file to create]
- **Naming Convention**: `test_<script_name>.py` in `tests/LLM/scripts/<domain>/`
- **Test Infrastructure**: Use existing fixtures from `tests/LLM/scripts/conftest.py`

### Test Cases to Cover

1. [FILL: Test case 1 - what it tests]
2. [FILL: Test case 2]
3. [FILL: Edge case 1]
4. [FILL: Edge case 2]

### Coverage Requirements

- **Target Coverage**: >90% for new code
- **Required Test Types**:
  - Unit tests for all new functions/classes
  - Integration tests for workflows
  - Edge case tests for error handling

### Test-First Requirement

- [ ] Tests written before implementation (TDD workflow preferred)
- [ ] Initial test run shows all failing
- [ ] Tests define success criteria

[FILL: For code work, define comprehensive test coverage. For documentation work, define validation approach. See PLAN template "Testing Requirements" section for complete guidance.]

---

## ✅ Expected Results

### Functional Changes

- [FILL: What will work differently]
- [FILL: New capabilities]
- [FILL: Behavior changes]

### Performance Changes (if applicable)

- [FILL: Speed improvements]
- [FILL: Resource usage changes]
- [FILL: Scalability improvements]

### Observable Outcomes

- [FILL: How to verify this worked]
- [FILL: What users/systems will see]
- [FILL: Success indicators]

[FILL: Be specific about what success looks like]

---

## 🔍 Conflict Analysis with Other Subplans

[FILL: Before creating this subplan, check for conflicts with existing subplans]

**Review Existing Subplans**:

- [FILL: List other subplans for this PLAN from PLAN's "Subplan Tracking" section]

**Check for**:

- **Overlap**: Does this duplicate work from another subplan?
- **Conflicts**: Will this interfere with another subplan's approach?
- **Dependencies**: Must another subplan complete first?
- **Integration**: How does this connect with other subplans?

**Analysis**:

- [FILL: "No conflicts detected" or list specific conflicts/dependencies]
- [FILL: If conflicts exist, how will you resolve them?]
- [FILL: If dependencies exist, have they been completed?]

**Result**: Safe to proceed / Needs coordination / Blocked by SUBPLAN_XX

---

## 🔗 Dependencies

### Other Subplans

- [FILL: Must complete SUBPLAN_XX before this]
- [FILL: Depends on SUBPLAN_YY for Z]
- None (if independent)

### External Dependencies

- [FILL: Libraries needed]
- [FILL: Services required]
- [FILL: Data dependencies]

### Prerequisite Knowledge

- [FILL: What you need to understand first]
- [FILL: Documentation to read]

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

_None yet - will be created when execution starts_

**First Execution**: `EXECUTION_TASK_[FEATURE]_[SUBPLAN_NUMBER]_01.md`

**If Circular Debug**: `EXECUTION_TASK_[FEATURE]_[SUBPLAN_NUMBER]_02.md` (or next number)

[FILL: Update this as EXECUTION_TASKs are created. Shows all attempts.]

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] All deliverables created
- [ ] All tests passing (if code work)
- [ ] All expected results achieved
- [ ] Code commented with learnings (if code work)
- [ ] EXECUTION_TASK complete
- [ ] **Achievement feedback received** (see Completion Workflow below)
- [ ] Ready for archive

[FILL: Specific criteria for this subplan's completion]

---

## ✅ Completion Workflow (Filesystem-First)

**After All Work Complete**:

1. **Request Review**: Ask reviewer to assess achievement completion
2. **Reviewer Creates Feedback File**:
   - **If Approved**: Create `execution/feedbacks/APPROVED_[XX].md` (XX = achievement number without dot)
   - **If Fixes Needed**: Create `execution/feedbacks/FIX_[XX].md` with detailed issues
3. **Filesystem = Source of Truth**: Achievement completion tracked by APPROVED file existence, not PLAN markdown

**Achievement Index in PLAN**:
- Defines structure (list of all achievements)
- NOT updated with checkmarks or status manually
- Filesystem (`APPROVED_XX.md` files) indicates completion status

**Do NOT**:
- ❌ Manually update PLAN markdown with "✅ Achievement complete"
- ❌ Add checkmarks to Achievement Index
- ❌ Update "Current Status & Handoff" to mark achievement done

**DO**:
- ✅ Request reviewer feedback after work complete
- ✅ Wait for `APPROVED_XX.md` or `FIX_XX.md` file creation
- ✅ If FIX required: Address issues, request re-review

**Why Filesystem-First**:
- Single source of truth (files, not markdown parsing)
- Automated detection by scripts (`generate_prompt.py`)
- Clear audit trail (feedback files are timestamped, contain rationale)
- Prevents markdown parsing issues

**Reference**: See `LLM/docs/FEEDBACK_SYSTEM_GUIDE.md` for complete guidance

---

## 📝 Notes

[FILL: Any additional context, warnings, or important information]

**Common Pitfalls**:

- [FILL: What to watch out for]

**Resources**:

- [FILL: Helpful links, docs, examples]

---

---

## 📖 What to Read (Focus Rules)

**When working on this SUBPLAN**, follow these focus rules to minimize context:

**✅ READ ONLY**:

- This SUBPLAN file (complete file)
- Parent PLAN current achievement section (50-100 lines)
- Active EXECUTION_TASKs (if any exist)
- Parent PLAN "Current Status & Handoff" section (30-50 lines)

**❌ DO NOT READ**:

- Parent PLAN full content
- Other achievements in PLAN
- Other SUBPLANs
- Completed EXECUTION_TASKs (unless needed for context)
- Completed work

**Context Budget**: ~400 lines

**Why**: SUBPLAN defines HOW to achieve one achievement. Reading other achievements or full PLAN adds scope and confusion.

**📖 See**: `LLM/guides/FOCUS-RULES.md` for complete focus rules and examples.

---

## 🔄 Active EXECUTION_TASKs

**Real-Time Tracking** (update as EXECUTIONs progress):

| EXECUTION                               | Status                                     | Progress | Notes   |
| --------------------------------------- | ------------------------------------------ | -------- | ------- |
| EXECUTION*TASK*[FEATURE]\_[SUBPLAN]\_01 | [Planning / Executing / Complete / Failed] | [0-100%] | [Notes] |
| EXECUTION*TASK*[FEATURE]\_[SUBPLAN]\_02 | [Planning / Executing / Complete / Failed] | [0-100%] | [Notes] |

**Status Options**:

- **Planning**: EXECUTION_TASK created, not yet executing
- **Executing**: Work in progress
- **Complete**: Execution finished, deliverables verified
- **Failed**: Execution encountered issues (document in notes)

**Update Frequency**: Update this table as EXECUTIONs progress

**For Single Execution**: Single row in table

**For Multiple Executions**: One row per planned execution

**Why**: Real-time tracking enables Designer to monitor progress, coordinate parallel executions, and plan synthesis.

---

## 📊 Execution Results Synthesis

**Review All Results** (complete after all EXECUTIONs finish):

**EXECUTION Summary**:

- **EXECUTION_01 Results**: [Summary of what was achieved, learnings, outcomes]
- **EXECUTION_02 Results**: [Summary of what was achieved, learnings, outcomes]
- **EXECUTION_03 Results**: [Summary of what was achieved, learnings, outcomes]

**Collective Learnings**:

- [What worked across all EXECUTIONs?]
- [What didn't work?]
- [What patterns emerged?]
- [What should be adopted?]

**Comparison** (if parallel experiments):

- [Compare results side-by-side]
- [Which approach performed best?]
- [Why did one succeed over others?]
- [What factors made the difference?]

**Best Approach** (if multiple):

- [Which execution achieved best results?]
- [Why this approach?]
- [What should be adopted for production?]

**Recommendations**:

- [What to adopt from successful EXECUTIONs?]
- [What to avoid from failed EXECUTIONs?]
- [What to try next (if iterative)?]

**Example Synthesis**:

- EXECUTION_01 (Algorithm A): 50ms average, simple implementation
- EXECUTION_02 (Algorithm B): 30ms average, optimized ✅ Best
- EXECUTION_03 (Algorithm C): 45ms average, alternative approach
- **Learnings**: Algorithm B 40% faster, optimization technique X was key
- **Decision**: Adopt Algorithm B for production

**For Single Execution**: Document learnings from that execution

**When to Complete**: After all EXECUTIONs finish, before marking SUBPLAN complete

---

## 📖 What to Read (Focus Rules)

**When working on this SUBPLAN**, follow these focus rules to minimize context:

**✅ READ ONLY**:

- This SUBPLAN file (complete file)
- Parent PLAN current achievement section (50-100 lines)
- Active EXECUTION_TASKs (if any exist)
- Parent PLAN "Current Status & Handoff" section (30-50 lines)

**❌ DO NOT READ**:

- Parent PLAN full content
- Other achievements in PLAN
- Other SUBPLANs
- Completed EXECUTION_TASKs (unless needed for context)
- Completed work

**Context Budget**: ~400-600 lines (increased for multi-execution planning)

**Independent Operation**: This SUBPLAN operates independently:

- **Designer Phase**: Create SUBPLAN, design approach, plan execution(s)
- **Executor Phase**: Execute EXECUTION_TASK(s) according to plan
- **Synthesis Phase**: Review results, synthesize learnings, complete SUBPLAN

**Executor Context**: Executor reads SUBPLAN objective (~2 sentences) and approach section only, not full SUBPLAN.

**Why**: SUBPLAN defines HOW to achieve one achievement. Reading other achievements or full PLAN adds scope and confusion.

**📖 See**: `LLM/guides/FOCUS-RULES.md` for complete focus rules and `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` for workflow.

---

**Ready to Execute**:

- **Designer**: Complete SUBPLAN design, plan execution(s), then create EXECUTION_TASK(s)
- **Executor**: Read SUBPLAN objective, execute according to plan
- **Reference**: `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` for complete workflow, `LLM/protocols/IMPLEMENTATION_START_POINT.md` for execution workflows
