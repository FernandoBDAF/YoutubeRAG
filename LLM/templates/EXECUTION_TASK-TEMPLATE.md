# EXECUTION_TASK: [Brief Title]

**Type**: EXECUTION_TASK  
**Subplan**: SUBPLAN*[FEATURE]*[NUMBER].md  
**Mother Plan**: PLAN\_[FEATURE].md  
**Plan**: [FEATURE-NAME]  
**Achievement**: [Which achievement from PLAN]  
**Iteration**: [1/2/3]  
**Execution Number**: XX (first attempt, second attempt, etc.)  
**Previous Execution**: [Link if 2nd+ attempt, N/A if first]  
**Circular Debug Flag**: Yes / No [Yes if this is recovery from circular debugging]  
**Started**: [YYYY-MM-DD HH:MM UTC]  
**Status**: In Progress / Complete / Abandoned / Blocked

**Metadata Tags**: See `LLM/guides/METADATA-TAGS.md` for virtual organization system

**File Location**: Create this EXECUTION*TASK in `work-space/execution/EXECUTION_TASK*[FEATURE]_[SUBPLAN]_[EXECUTION].md`

[FILL: Use UTC timestamps for precise tracking. Example: 2025-11-05 14:30 UTC]

[FILL: Brief title describes what you're doing. Execution number shows if this is 1st, 2nd, 3rd attempt at the subplan.]

[FILL: If this is 2nd+ execution (circular debug recovery), add this note:]
**NOTE**: This is a CIRCULAR DEBUG execution - new strategy after iterations X-Y in EXECUTION*TASK*[FEATURE]_[SUBPLAN]_[PREV] encountered circular debugging.

---

## 📏 Size Limits

**⚠️ HARD LIMIT**: 200 lines maximum

**Why**: EXECUTION_TASK is the smallest unit of focus during implementation. Keeping it small ensures:

- Focused work (one achievement at a time)
- Optimized session context (minimal reading)
- Easy to resume (small file to review)

**If approaching limit**:

- Condense iteration log (focus on key decisions, not every detail)
- Focus learning summary on most important insights
- Remove redundant details
- If >200 lines: Create new EXECUTION_TASK for next phase

**Validation**: Run `python LLM/scripts/validation/check_execution_task_size.py @EXECUTION_TASK_FILE.md` before marking complete.

**Line Budget Guidance**:

- Header + Objective: ~20 lines
- Iteration Log: ~50-80 lines (keep concise!)
- Learning Summary: ~30-50 lines (key points only)
- Completion Status: ~20 lines
- **Total Target**: 120-170 lines (well under 200)

---

## 📖 What to Read (Focus Rules)

**When working on this EXECUTION_TASK**, follow these focus rules to minimize context:

**✅ READ ONLY**:

- This EXECUTION_TASK file (complete file)
- Parent SUBPLAN objective (1-2 sentences only) - see "SUBPLAN Context" section above
- Parent SUBPLAN approach summary (3-5 sentences only) - see "SUBPLAN Context" section above
- Code files being modified (if code work)

**❌ DO NOT READ**:

- Parent SUBPLAN full content (Designer already decided approach)
- Parent PLAN (except current achievement section)
- Other EXECUTION_TASKs (unless part of parallel group)
- Completed work
- Other achievements

**Context Budget**: ~200 lines (EXECUTION_TASK size limit)

**SUBPLAN-Based Execution**:
- **Executor reads**: SUBPLAN objective (~2 sentences) + approach summary (~3-5 sentences)
- **Executor does NOT read**: Full SUBPLAN (400-600 lines)
- **Why**: Designer already analyzed requirements and designed approach
- **Executor role**: Follow Designer's plan, execute according to approach

**Minimal Reading Pattern**:
1. Read SUBPLAN objective (what we're achieving)
2. Read SUBPLAN approach summary (how we'll do it)
3. Execute according to plan
4. Document journey in EXECUTION_TASK

**Parallel Execution** (if applicable):
- Read "Parallelization Context" section above
- Work independently (no coordination during execution)
- Results synthesized in SUBPLAN (Phase 4)

**Why**: EXECUTION_TASK is the smallest unit of focus. Minimal SUBPLAN reading reduces context budget and speeds execution. Executor follows Designer's plan.

**📖 See**: `LLM/guides/FOCUS-RULES.md` for complete focus rules and `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` (Phase 3: Execution) for workflow.

---

## 📖 What We're Building

[FILL: Brief description of what this execution is creating/implementing]

**Success**: [FILL: How we know we're done]

---

## 📖 SUBPLAN Context

**Parent SUBPLAN**: [SUBPLAN file path, e.g., `work-space/subplans/SUBPLAN_[FEATURE]_[NUMBER].md`]

**SUBPLAN Objective** (read only this, 1-2 sentences):
- [FILL: Copy SUBPLAN objective here - this is what we're achieving]

**SUBPLAN Approach Summary** (read only this, 3-5 sentences):
- [FILL: Copy SUBPLAN approach summary here - this is how we'll do it]

**⚠️ DO NOT READ**: Full SUBPLAN (Designer already decided approach)

**Why Minimal Reading**: 
- Designer already analyzed requirements and designed approach
- Executor follows Designer's plan (no re-design during execution)
- Minimal reading reduces context budget (~10 lines vs. 400+ lines)
- Focus on execution, not design

**See**: `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` (Phase 3: Execution) for complete workflow

---

## 🔀 Parallelization Context (If Applicable)

**If this EXECUTION is part of a parallel group, document here:**

**Parallel Group**: [Which other EXECUTIONs run simultaneously?]
- EXECUTION_TASK_[FEATURE]_[SUBPLAN]_01: [Purpose]
- EXECUTION_TASK_[FEATURE]_[SUBPLAN]_02: [Purpose] (this one)
- EXECUTION_TASK_[FEATURE]_[SUBPLAN]_03: [Purpose]

**Independence Rationale**: [Why this EXECUTION is independent?]
- Example: "No dependencies on other EXECUTIONs, can run simultaneously"
- Example: "Testing different approach, results compared in SUBPLAN synthesis"

**Results Comparison**: [How results will be compared in SUBPLAN synthesis?]
- Example: "Performance metrics compared side-by-side"
- Example: "Accuracy scores compared, best approach adopted"

**Coordination**: [How to coordinate with other parallel EXECUTIONs?]
- Example: "No coordination needed - work independently"
- Example: "Share intermediate results via SUBPLAN Active EXECUTION_TASKs section"

**If Not Parallel**: Remove this section or state "Single execution - no parallelization"

**See**: `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` (Parallel Execution Pattern) for examples

---

## 🧪 Test Creation Phase (if code work)

**Tests Written**:

- [FILL: List all test names]
- [FILL: Test file: path]

**Initial Test Run**:

- Date: [FILL: timestamp]
- Result: [FILL: All failing (expected) or partial]
- Coverage: [FILL: What the tests cover]

**For Documentation Work**:
[FILL: Describe validation approach instead of tests]

- Completeness check
- Structure validation
- Review against requirements

---

## 🔄 Iteration Log

[FILL: Update this section after EVERY iteration. No exceptions.]

### Iteration 1

**Date**: [YYYY-MM-DD HH:MM UTC]  
**Test Run**: [Which tests ran] / [What was tested]  
**Result**: Pass / Fail / Partial ([X] passed, [Y] failed)  
**Failed Test**: [Test name if failed]  
**Error**: [Exact error message if failed]  
**Root Cause Analysis**: [FILL: WHY it failed - deep analysis, not surface reason]

[FILL: Use UTC timestamps. Update iteration number and timestamp for each iteration.]  
**Fix Applied**:

- File: [FILL: file path]
- Lines: [FILL: line numbers]
- Change: [FILL: what was changed]
- Rationale: [FILL: why this should fix it]

**Learning**: [FILL: What we learned - generalizable insight, not just "fixed the bug"]  
**Code Comments Added**: Yes / No

- [FILL: If Yes: file:line - summary of comment]

**Progress Check**:

- New error: Yes / No
- Making progress: Yes / No
- Strategy effective: Yes / No

**Next Step**: [FILL: What to try next]

[FILL: Copy this iteration template for each iteration. Update iteration number.]

---

### Iteration 2

[FILL: Same structure as Iteration 1]

---

### Circular Debug Check - After Iteration 3

[FILL: Perform this check after every 3 iterations]

**Pattern Detected**: Yes / No  
**Same Error Count**: [How many times same error appeared]  
**Error**: [The repeating error if applicable]  
**Analysis**:

- [FILL: Why are we stuck?]
- [FILL: What's the common pattern?]
- [FILL: What are we missing?]

**Decision**: Continue / Change Strategy

**If Change Strategy**:

- Mark this EXECUTION_TASK as "Abandoned - Circular Debug"
- Create: `EXECUTION_TASK_[FEATURE]_[SUBPLAN]_[NEXT].md`
- New strategy: [FILL: Fundamentally different approach]
- Rationale: [FILL: Why this should work]

[FILL: Repeat this check every 3 iterations]

---

## 📚 Learning Summary

[FILL: Aggregate learnings as you go]

**Technical Learnings**:

- [FILL: Technical insights]
- [FILL: Code patterns discovered]
- [FILL: System behavior learned]

**Process Learnings**:

- [FILL: What worked in approach]
- [FILL: What didn't work]
- [FILL: Strategy changes and why]

**Mistakes Made & Recovered**:

- [FILL: Mistake 1] → [How we recovered]
- [FILL: Mistake 2] → [How we fixed it]

---

## 💬 Code Comment Map

[FILL: Track where learnings were added to code]

**Comments Added**:

- `path/to/file.py:123` (Iteration 2): [Summary of comment - what was learned]
- `path/to/file.py:456` (Iteration 5): [Summary of comment]

[FILL: For documentation work, note "Not applicable"]

---

## 🔮 Future Work Discovered

[FILL: Note ideas that are out of scope but valuable]

**During Iteration [N]**:

- [Future idea 1] - [Why valuable, why not in scope now]
- [Future idea 2] - [Rationale for deferring]

**Add to Backlog**: Yes (during IMPLEMENTATION_END_POINT process)

---

## ✅ Completion Status

- [ ] All tests passing (if code work)
- [ ] All code commented with learnings (if code work)
- [ ] Subplan objectives met
- [ ] Execution result: Success / Abandoned / Blocked
- [ ] If Abandoned: [Link to next EXECUTION_TASK with new strategy]
- [ ] Future work extracted
- [ ] Ready for archive

**Total Iterations**: [N]  
**Total Time**: [hours]  
**Final Status**: Success / Abandoned / Blocked

---

**Status**: [Update as you progress]  
**Next**: [What happens next]
