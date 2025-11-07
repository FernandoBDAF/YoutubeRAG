# Next Achievement - Session Entry Point

**Purpose**: Start next achievement in an active PLAN  
**Status**: Active Protocol  
**Created**: 2025-11-07  
**Related**: IMPLEMENTATION_START_POINT.md, FOCUS-RULES.md

---

## 🎯 When to Use This

**Use this when**:

- You have an active PLAN (work in progress)
- Previous achievement is complete
- Starting a new session
- Need to begin next achievement

**Don't use this when**:

- Starting a new PLAN (use IMPLEMENTATION_START_POINT.md)
- Resuming a paused PLAN (use IMPLEMENTATION_RESUME.md)
- Continuing existing SUBPLAN (use CONTINUE_SUBPLAN.md)

---

## 📋 Pre-Start Checklist

**Before starting, verify**:

- [ ] PLAN file exists
- [ ] Previous achievement is complete (has SUBPLAN + EXECUTION_TASK)
- [ ] Archive location exists
- [ ] Run validation: `python LLM/scripts/validation/validate_achievement_completion.py @PLAN_FILE.md --achievement X.Y` (for previous achievement)

---

## 📖 Context Loading (What to Read)

**✅ READ ONLY**:

- PLAN file - Next achievement section only (50-100 lines)
- PLAN file - "Current Status & Handoff" section (30-50 lines)
- PLAN file - "Subplan Tracking" summary (20-30 lines)

**❌ DO NOT READ**:

- Full PLAN file
- Other achievements
- Completed SUBPLANs
- Completed EXECUTION_TASKs
- Full methodology guides (unless specifically referenced)

**Context Budget**: ~150 lines maximum

**Reference**: See LLM/guides/FOCUS-RULES.md for detailed focus rules

---

## 🔄 Start Workflow

### Step 1: Load Context

1. Read PLAN "Current Status & Handoff" section
2. Identify next achievement
3. Read next achievement section only
4. Review "Subplan Tracking" summary

**Time**: 1-2 minutes

### Step 2: Verify Prerequisites

1. Check previous achievement is complete
2. Verify archive location exists
3. Run validation (if previous achievement):
   ```bash
   python LLM/scripts/validation/validate_achievement_completion.py @PLAN_FILE.md --achievement X.Y
   ```

### Step 3: Create SUBPLAN

1. Use SUBPLAN-TEMPLATE.md
2. Reference parent PLAN achievement
3. Document approach for this achievement
4. Set status: In Progress

### Step 4: Create EXECUTION_TASK

1. Use EXECUTION_TASK-TEMPLATE.md
2. Reference parent SUBPLAN
3. Start Iteration 1
4. Begin work

### Step 5: Validate

Run validation:

```bash
python LLM/scripts/validate_execution_start.py @EXECUTION_TASK_FILE.md
```

If issues found: Fix before continuing

---

## 📝 Prompt Template

**Copy-paste ready prompt**:

```
Start next achievement in @PLAN_FEATURE.md following methodology.

═══════════════════════════════════════════════════════════════════════

CONTEXT BOUNDARIES (Read ONLY These):
✅ @PLAN_FEATURE.md - Next achievement section only (50-100 lines)
✅ @PLAN_FEATURE.md - "Current Status & Handoff" section (30-50 lines)
✅ @PLAN_FEATURE.md - "Subplan Tracking" summary (20-30 lines)

❌ DO NOT READ: Full PLAN, other achievements, completed work

CONTEXT BUDGET: ~150 lines maximum

═══════════════════════════════════════════════════════════════════════

NEXT ACHIEVEMENT: [Achievement Number] - [Title]

Goal: [From achievement section]
Estimated: [From achievement section]

═══════════════════════════════════════════════════════════════════════

REQUIRED STEPS:

Step 1: Create SUBPLAN (MANDATORY)
- File: SUBPLAN_FEATURE_XX.md
- Template: LLM/templates/SUBPLAN-TEMPLATE.md

Step 2: Create EXECUTION_TASK (MANDATORY)
- File: EXECUTION_TASK_FEATURE_XX_01.md
- Template: LLM/templates/EXECUTION_TASK-TEMPLATE.md

Step 3: Execute Work
[Implement achievement deliverables]

VALIDATION:
Run: python LLM/scripts/validation/validate_execution_start.py @EXECUTION_TASK_FILE.md

═══════════════════════════════════════════════════════════════════════

Now beginning next achievement...
```

---

## ✅ Success Criteria

**Start is successful when**:

- Context loaded in <3 minutes
- SUBPLAN created
- EXECUTION_TASK created
- Validation passes
- Work begins smoothly

---

## 📚 Related Documents

- LLM/protocols/IMPLEMENTATION_START_POINT.md (for creating new PLANs)
- LLM/protocols/IMPLEMENTATION_RESUME.md (for resuming paused PLANs)
- LLM/protocols/CONTINUE_SUBPLAN.md (for continuing SUBPLANs)
- LLM/protocols/CONTINUE_EXECUTION.md (for continuing EXECUTION_TASKs)
- LLM/guides/FOCUS-RULES.md (for context boundaries)

---

**Last Updated**: 2025-11-07
