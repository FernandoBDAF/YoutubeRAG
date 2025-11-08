# Mini-Protocol: CREATE_EXECUTION

**Purpose**: Focused guide for EXECUTION_TASK creation during the Executor phase  
**Status**: Active  
**Created**: November 9, 2025

---

## 🎯 What This Is

This mini-protocol guides the **Executor Agent** through EXECUTION_TASK creation and execution - implementing the work according to the Designer's plan in the SUBPLAN.

**Key Principle**: Executor receives MINIMAL context (SUBPLAN objective + approach only) to maintain focus.

**Not for**: Design/Planning (use CREATE_SUBPLAN.md for that)

---

## 📋 When to Use This

**Use this protocol when**:

- Designer has completed SUBPLAN (Phase 1)
- You're ready to execute the SUBPLAN
- You need to create EXECUTION_TASK(s) and start work
- You're working on one of potentially multiple parallel executions

**Before using this**:

1. Read SUBPLAN objective (1-2 sentences)
2. Read SUBPLAN approach summary (3-5 sentences)
3. **Don't read the full SUBPLAN** (Designer already decided approach)
4. If parallel execution: Read parallelization context section

---

## 🔄 SUBPLAN Workflow Context (Phase 3 of 4)

**The 4-Phase SUBPLAN Independent Workflow**:

```
Phase 1: DESIGN (Designer Agent)
  └─ Create SUBPLAN
  └─ Plan approach and executions
  └─ Done before you start

Phase 2: EXECUTION PLANNING (Designer Agent)
  └─ Create EXECUTION_TASK files
  └─ Plan parallelization
  └─ Done before you start

Phase 3: EXECUTION (Executor Agents) ← You are here
  └─ Execute according to SUBPLAN plan
  └─ Create and update EXECUTION_TASK(s)
  └─ Multiple Executors may work in parallel

Phase 4: SYNTHESIS (Designer Agent)
  └─ Review all EXECUTION results
  └─ Synthesize learnings
  └─ Mark SUBPLAN complete
```

**This protocol covers Phase 3 only.**

---

## ✅ EXECUTION_TASK Creation Checklist

### Step 1: Prepare

**Read (and ONLY read)**:

- [ ] SUBPLAN objective (1-2 sentences max)
- [ ] SUBPLAN approach summary (3-5 sentences max)
- [ ] SUBPLAN "Execution Strategy" section (what execution count/parallelization)
- [ ] If parallel: SUBPLAN "Parallelization Context" section
- [ ] EXECUTION_TASK template

**Don't read**:

- ❌ Full SUBPLAN content (Designer decided)
- ❌ Other sections beyond objective + approach
- ❌ Mother PLAN (Designer already synthesized it)

**Remember**: You are the Executor. Designer made the strategic decisions. Your job is to execute the plan.

### Step 2: Create EXECUTION_TASK File

**File naming**:

```
EXECUTION_TASK_<FEATURE>_<SUBPLAN>_<EXECUTION>.md

Example: EXECUTION_TASK_METHODOLOGY-HIERARCHY_42_01.md
  - FEATURE: METHODOLOGY-HIERARCHY
  - SUBPLAN: 42
  - EXECUTION: 01 (first execution of this subplan)
```

**Location**: `work-space/execution/EXECUTION_TASK_<FEATURE>_<SUBPLAN>_<EXECUTION>.md`

### Step 3: Set Up Header

```markdown
# EXECUTION_TASK: [Brief Title]

**Type**: EXECUTION*TASK
**Subplan**: SUBPLAN*<FEATURE>_<SUBPLAN>.md
**Mother Plan**: PLAN_<FEATURE>.md
**Achievement**: [Which achievement]
**Execution Number**: [01, 02, etc.]
**Status**: 🎯 In Progress
**Started**: [ISO timestamp]
**Last Updated**: [ISO timestamp]

**Note**: This execution is part of [SUBPLAN objective]
```

### Step 4: Add SUBPLAN Context (Minimal Reading!)

```markdown
## 📖 SUBPLAN Context (What Designer Planned)

**Objective** (read this):
[1-2 sentence summary of what we're achieving]

**Approach** (read this):
[3-5 sentence summary of how to do it]

---
```

**Critical**: Designer planned the work. You follow the plan. This section is your reference.

### Step 5: Add Parallelization Context (If Applicable)

**If this is part of multiple parallel EXECUTIONs**:

```markdown
## 🔀 Parallel Execution Context (If Applicable)

**Parallel Group**: [Which other executions run simultaneously]

**Your Role**: [Your specific part]

**Independence**: [How this is independent from parallel siblings]

**Results Comparison**: [How Designer will compare results with others]

---
```

**If single execution**: Skip this section.

### Step 6: Create Test Phase (If Code Work)

```markdown
## 🧪 Test Creation Phase

**Tests Written**:

- [ ] Test 1: [description]
- [ ] Test 2: [description]

**Test File**: [path/to/test_file.py]

**Initial Test Run**: [results - should fail]

---
```

### Step 7: Set Up Iteration Log Section

```markdown
## 📋 Iteration Log

[Will be filled during execution]

### Iteration 1

[To be filled]

---
```

### Step 8: Ready to Execute

**Your EXECUTION_TASK is ready when**:

- [ ] File created with correct naming
- [ ] Header complete
- [ ] SUBPLAN context section added (minimal reading)
- [ ] Parallelization context (if applicable)
- [ ] Test creation phase (if applicable)
- [ ] Iteration log section prepared

**Next**: Start executing according to SUBPLAN plan. After EVERY iteration, update EXECUTION_TASK.

---

## ⚙️ Execution Process (After EXECUTION_TASK Created)

### For Each Iteration

1. **Make Implementation Change** (according to SUBPLAN plan)
2. **Run Tests** (if applicable)
3. **Update EXECUTION_TASK**:

```markdown
### Iteration N

**Date**: [timestamp]

**Change Made**: [file:line - what changed]

**Test Result**: [Passed / Failed / Error]

**Error Message**: [If failed - exact error]

**Root Cause**: [Why did it fail/pass?]

**Learning**: [Generalizable insight]

**Progress**: [New Error / Same Error / Improved / Passed]
```

4. **Capture Learning** in code as comment (if applicable)

### Circular Debugging Check (Every 3 Iterations)

**Check**: Is current error == error from 3 iterations ago?

**If YES** → Stop this EXECUTION_TASK

- Mark as "Abandoned - Circular Debug after iteration X"
- Designer will create new EXECUTION_TASK with different strategy

**If NO** → Continue normal iterations

### Completion

**Mark EXECUTION_TASK complete when**:

- [ ] All tests passing (if code work)
- [ ] All SUBPLAN deliverables completed
- [ ] Learning captured in code
- [ ] Iteration log complete

**Status**: Change to "✅ Complete"

---

## 🎓 Special Cases

### Case 1: Single Simple EXECUTION

**Most common**: One EXECUTION_TASK, straightforward work

```markdown
## 📖 SUBPLAN Context

**Objective**: Add cache invalidation to GraphRAG query pipeline

**Approach**: Implement TTL-based cache invalidation for queries older than 1 hour

---
```

### Case 2: Parallel Independent EXECUTION

**Multiple parallel executions**: Your execution is one of several

```markdown
## 📖 SUBPLAN Context

**Objective**: Test query performance optimization approaches

**Approach**: Test 3 independent optimization strategies (Approach A, B, C)

---

## 🔀 Parallel Execution Context

**Parallel Group**: [PARALLEL with EXECUTION_02 and EXECUTION_03]

**Your Role**: Implement Approach A (indexing optimization)

**Independence**: Approach A is independent from B (caching) and C (batching)

**Results Comparison**: All three compare final query latency. Best one selected.

---
```

### Case 3: Sequential Iterative EXECUTION

**Sequential executions**: Your execution depends on previous one

```markdown
## 🔀 Sequential Context

**Sequential Chain**: EXECUTION_01 (planning) → EXECUTION_02 (first impl) → EXECUTION_03 (optimization)

**Your Role**: This is EXECUTION_02 - implement based on EXECUTION_01's plan

**Results Used By**: EXECUTION_03 will optimize based on your results

---
```

---

## 🚫 Common Mistakes to Avoid

**❌ Don't**:

- Read the full SUBPLAN (trust Designer's planning)
- Skip test creation (if code work)
- Update EXECUTION_TASK only at the end (update every iteration!)
- Stop at circular debug iteration without marking as abandoned
- Modify tests to make them pass (fix implementation instead)
- Assume the plan is complete (designer is flexible if discovering issues)

**✅ Do**:

- Read SUBPLAN objective + approach (that's all you need)
- Write tests first (if code work)
- Update EXECUTION_TASK after every single iteration
- Mark as abandoned when circular debugging detected
- Fix implementation to match tests
- Alert Designer if you discover issues with the plan

---

## 🔗 Related Documents

**Before Creating EXECUTION_TASK**:

- `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` - Full workflow guide
- `LLM/templates/EXECUTION_TASK-TEMPLATE.md` - Full template reference

**For SUBPLAN Design Phase**:

- `LLM/protocols/CREATE_SUBPLAN.md` - Designer's planning protocol

**For Completion**:

- `LLM/protocols/IMPLEMENTATION_END_POINT.md` - Archive and complete

---

## ⏱️ Timing

**Executor Phase (EXECUTION_TASK work)**: Varies wildly

- Light work (1-2 hours): 1-2 hours execution
- Medium work (3-5 hours): 3-5 hours execution
- Heavy work (8+ hours): 8+ hours execution

**Not included in this time**: Designer's synthesis phase (after you complete)

---

**After EXECUTION_TASK Complete**:

1. Update SUBPLAN with your results
2. Designer runs Phase 4 (Synthesis) to synthesize all EXECUTIONs
3. Use `LLM/protocols/IMPLEMENTATION_END_POINT.md` for archival
