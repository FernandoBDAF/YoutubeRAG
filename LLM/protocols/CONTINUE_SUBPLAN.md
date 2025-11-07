# Continue SUBPLAN - Session Entry Point

**Purpose**: Resume work on an active SUBPLAN in a new session  
**Status**: Active Protocol  
**Created**: 2025-11-07  
**Related**: IMPLEMENTATION_RESUME.md, FOCUS-RULES.md

---

## 🎯 When to Use This

**Use this when**:

- You have an active SUBPLAN (work in progress)
- Starting a new session
- Need to continue work on a specific achievement
- SUBPLAN exists but EXECUTION_TASK may or may not exist

**Don't use this when**:

- Starting a new PLAN (use IMPLEMENTATION_START_POINT.md)
- Resuming a paused PLAN (use IMPLEMENTATION_RESUME.md)
- Continuing an EXECUTION_TASK (use CONTINUE_EXECUTION.md)

---

## 📋 Pre-Resume Checklist

**Before resuming, verify**:

- [ ] SUBPLAN file exists
- [ ] Parent PLAN exists
- [ ] Archive location exists (from PLAN)
- [ ] Run validation: `python LLM/scripts/validation/validate_execution_start.py @SUBPLAN_FILE.md` (if EXECUTION_TASK exists)

---

## 📖 Context Loading (What to Read)

**✅ READ ONLY**:

- This SUBPLAN file (complete file, max 400 lines)
- Parent PLAN current achievement section (50-100 lines)
- Active EXECUTION_TASK (if exists, max 200 lines)
- Parent PLAN "Current Status & Handoff" section (30-50 lines)

**❌ DO NOT READ**:

- Full parent PLAN
- Other achievements in PLAN
- Other SUBPLANs
- Completed EXECUTION_TASKs (unless needed for specific context)
- Full methodology guides (unless specifically referenced)

**Context Budget**: ~400 lines (SUBPLAN size limit)

**Reference**: See LLM/guides/FOCUS-RULES.md for detailed focus rules

---

## 🔄 Resume Workflow

### Step 1: Load Context

1. Read SUBPLAN file completely
2. Read parent PLAN current achievement section
3. Read active EXECUTION_TASK (if exists)
4. Read parent PLAN "Current Status & Handoff" section

**Time**: 2-3 minutes

### Step 2: Verify Status

1. Check SUBPLAN status (In Progress / Complete)
2. Check if EXECUTION_TASK exists
3. Check if deliverables are complete
4. Review "Success Criteria" in SUBPLAN

### Step 3: Continue Work

**If EXECUTION_TASK exists**:

- Continue current iteration
- Update iteration log
- Work on deliverables

**If EXECUTION_TASK doesn't exist**:

- Create EXECUTION_TASK (see EXECUTION_TASK-TEMPLATE.md)
- Start Iteration 1
- Begin work

### Step 4: Validate Before Continuing

Run validation:

```bash
python LLM/scripts/validate_execution_start.py @EXECUTION_TASK_FILE.md
```

If issues found: Fix before continuing

### Step 5: Update Progress

- Update EXECUTION_TASK iteration log
- Update SUBPLAN status if complete
- Update parent PLAN statistics

---

## 📝 Prompt Template

**Copy-paste ready prompt**:

```
Continue work on @SUBPLAN_FEATURE_XX.md following methodology.

═══════════════════════════════════════════════════════════════════════

CONTEXT BOUNDARIES (Read ONLY These):
✅ @SUBPLAN_FEATURE_XX.md (complete file)
✅ @PLAN_FEATURE.md - Current achievement section only
✅ @EXECUTION_TASK_FEATURE_XX_YY.md (if exists, max 200 lines)
✅ @PLAN_FEATURE.md - "Current Status & Handoff" section

❌ DO NOT READ: Full PLAN, other achievements, other SUBPLANs

CONTEXT BUDGET: ~400 lines maximum

═══════════════════════════════════════════════════════════════════════

CURRENT STATUS:
[Read from SUBPLAN and EXECUTION_TASK]

NEXT STEPS:
[Read from SUBPLAN "Approach" section]

VALIDATION:
Run: python LLM/scripts/validation/validate_execution_start.py @EXECUTION_TASK_FILE.md

═══════════════════════════════════════════════════════════════════════

Continue work on SUBPLAN...
```

---

## ✅ Success Criteria

**Resume is successful when**:

- Context loaded in <5 minutes
- Work continues smoothly
- No need to read full PLAN
- Validation passes

---

## 📚 Related Documents

- LLM/protocols/IMPLEMENTATION_RESUME.md (for resuming paused PLANs)
- LLM/protocols/CONTINUE_EXECUTION.md (for continuing EXECUTION_TASKs)
- LLM/protocols/NEXT_ACHIEVEMENT.md (for starting next achievement)
- LLM/guides/FOCUS-RULES.md (for context boundaries)

---

**Last Updated**: 2025-11-07
