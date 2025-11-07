# Continue EXECUTION_TASK - Session Entry Point

**Purpose**: Resume work on an active EXECUTION_TASK in a new session  
**Status**: Active Protocol  
**Created**: 2025-11-07  
**Related**: CONTINUE_SUBPLAN.md, FOCUS-RULES.md

---

## 🎯 When to Use This

**Use this when**:

- You have an active EXECUTION_TASK (work in progress)
- Starting a new session
- Need to continue current iteration
- EXECUTION_TASK exists and is In Progress

**Don't use this when**:

- Starting a new PLAN (use IMPLEMENTATION_START_POINT.md)
- Resuming a paused PLAN (use IMPLEMENTATION_RESUME.md)
- Continuing a SUBPLAN (use CONTINUE_SUBPLAN.md)
- Starting new achievement (use NEXT_ACHIEVEMENT.md)

---

## 📋 Pre-Resume Checklist

**Before resuming, verify**:

- [ ] EXECUTION_TASK file exists
- [ ] Parent SUBPLAN exists
- [ ] Parent PLAN exists
- [ ] Archive location exists
- [ ] Run validation: `python LLM/scripts/validation/validate_execution_start.py @EXECUTION_TASK_FILE.md`

---

## 📖 Context Loading (What to Read)

**✅ READ ONLY**:

- This EXECUTION_TASK file (complete file, max 200 lines)
- Parent SUBPLAN objective (1-2 sentences only)
- Code files being modified (if code work)
- Relevant test files (if TDD)

**❌ DO NOT READ**:

- Full parent SUBPLAN
- Full parent PLAN
- Other EXECUTION_TASKs
- Completed work
- Other achievements
- Full methodology guides (unless specifically referenced)

**Context Budget**: ~200 lines (EXECUTION_TASK size limit)

**Reference**: See LLM/guides/FOCUS-RULES.md for detailed focus rules

---

## 🔄 Resume Workflow

### Step 1: Load Context

1. Read EXECUTION_TASK file completely
2. Read parent SUBPLAN objective (1-2 sentences)
3. Review current iteration status
4. Check code files (if code work)

**Time**: 1-2 minutes

### Step 2: Verify Status

1. Check EXECUTION_TASK status (In Progress / Complete)
2. Review current iteration
3. Check what's been completed
4. Identify next steps

### Step 3: Continue Work

**If continuing current iteration**:

- Update iteration log
- Continue work on deliverables
- Document progress

**If starting new iteration**:

- Add new iteration entry
- Document approach changes
- Begin work

### Step 4: Validate

Run validation:

```bash
python LLM/scripts/check_execution_task_size.py @EXECUTION_TASK_FILE.md
```

If issues found: Fix before continuing

### Step 5: Update Progress

- Update EXECUTION_TASK iteration log
- Update completion status if done
- Archive immediately if complete

---

## 📝 Prompt Template

**Copy-paste ready prompt**:

```
Continue work on @EXECUTION_TASK_FEATURE_XX_YY.md following methodology.

═══════════════════════════════════════════════════════════════════════

CONTEXT BOUNDARIES (Read ONLY These):
✅ @EXECUTION_TASK_FEATURE_XX_YY.md (complete file, max 200 lines)
✅ @SUBPLAN_FEATURE_XX.md - Objective only (1-2 sentences)
✅ Code files being modified (if code work)

❌ DO NOT READ: Full SUBPLAN, full PLAN, other EXECUTION_TASKs

CONTEXT BUDGET: ~200 lines maximum

═══════════════════════════════════════════════════════════════════════

CURRENT STATUS:
[Read from EXECUTION_TASK iteration log]

NEXT STEPS:
[Read from EXECUTION_TASK "Next" section]

VALIDATION:
Run: python LLM/scripts/validation/check_execution_task_size.py @EXECUTION_TASK_FILE.md

═══════════════════════════════════════════════════════════════════════

Continue work on EXECUTION_TASK...
```

---

## ✅ Success Criteria

**Resume is successful when**:

- Context loaded in <3 minutes
- Work continues smoothly
- No need to read parent SUBPLAN/PLAN
- Validation passes
- EXECUTION_TASK stays under 200 lines

---

## 📚 Related Documents

- LLM/protocols/CONTINUE_SUBPLAN.md (for continuing SUBPLANs)
- LLM/protocols/NEXT_ACHIEVEMENT.md (for starting next achievement)
- LLM/protocols/IMPLEMENTATION_RESUME.md (for resuming paused PLANs)
- LLM/guides/FOCUS-RULES.md (for context boundaries)

---

**Last Updated**: 2025-11-07
