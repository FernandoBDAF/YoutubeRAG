# EXECUTION_ANALYSIS: PLAN, SUBPLAN, and EXECUTION_TASK Control Flow Guide

**Purpose**: Comprehensive guide for controlling PLANs, SUBPLANs, and EXECUTION_TASKs in the LLM development methodology  
**Date**: 2025-01-28  
**Status**: Active  
**Related PLAN(s)**: PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md (case study)  
**Category**: Methodology Guide

---

## 🎯 Objective

This guide provides comprehensive instructions for controlling PLANs, SUBPLANs, and EXECUTION_TASKs throughout their lifecycle. It covers states, workflows, commands, troubleshooting, and best practices.

**Use Case**: When you need to understand how to start, track, resume, or complete work in the methodology.

**Related Analysis**: See `EXECUTION_ANALYSIS_SUBPLAN-TRACKING-GAP.md` for tracking gap analysis and registration requirements.

---

## 📋 Executive Summary

**Purpose**: Enable clear understanding and control of PLANs, SUBPLANs, and EXECUTION_TASKs

**Key Topics Covered**:

- ✅ PLAN control (states, commands, updates)
- ✅ SUBPLAN control (lifecycle, registration, tracking)
- ✅ EXECUTION_TASK control (states, execution, completion)
- ✅ Complete workflow examples
- ✅ Common issues and solutions
- ✅ Quick reference commands
- ✅ Tracking checklist

**Target Audience**: LLM developers using the methodology, methodology maintainers

---

## 🎮 Control Flow Guide: How to Control PLANs, SUBPLANs, and EXECUTION_TASKs

### Overview: The Hierarchy

```
PLAN (What to achieve)
  └─ SUBPLAN (How to achieve - one per achievement)
      └─ EXECUTION_TASK (Journey log - one or more per SUBPLAN)
```

**Key Principle**: Each level has a specific role and lifecycle.

---

### 📋 PLAN Control

#### PLAN States

1. **🚀 Ready to Execute**: PLAN created, no work started
2. **🚧 In Progress**: At least one SUBPLAN created
3. **⏸️ Paused**: Work stopped temporarily
4. **✅ Complete**: All achievements complete

#### How to Control PLAN

**Start Execution**:
```bash
# Generate prompt for next achievement
python LLM/scripts/generation/generate_prompt.py --next @PLAN_FEATURE.md

# Or specific achievement
python LLM/scripts/generation/generate_prompt.py --achievement 0.1 @PLAN_FEATURE.md
```

**Check PLAN Status**:
- Read PLAN's "Current Status & Handoff" section
- Check "🔄 Active Components" for active work
- Check "🔄 Subplan Tracking" for completed work

**Update PLAN** (MANDATORY after each action):
1. **After creating SUBPLAN**: Add to "Active Components" → "Active SUBPLANs"
2. **After creating EXECUTION_TASK**: Add to "Active Components" → "Active EXECUTION_TASKs"
3. **After completing EXECUTION_TASK**: Move to "Subplan Tracking", update statistics
4. **After completing SUBPLAN**: Update status to "Complete" in "Subplan Tracking"

**Resume PLAN**:
```bash
# Generate resume prompt
python LLM/scripts/generation/generate_resume_prompt.py @PLAN_FEATURE.md
```

**Complete PLAN**:
- All achievements marked complete in "Current Status & Handoff"
- Follow `IMPLEMENTATION_END_POINT.md` protocol

---

### 📝 SUBPLAN Control

#### SUBPLAN States

1. **Not Started**: SUBPLAN file created but not registered in PLAN
2. **In Progress**: Registered in PLAN, has active EXECUTION_TASKs
3. **Complete**: All EXECUTION_TASKs complete

#### How to Control SUBPLAN

**Create SUBPLAN**:
```bash
# Generate SUBPLAN creation prompt
python LLM/scripts/generation/generate_prompt.py --achievement 0.1 --subplan-only @PLAN_FEATURE.md
```

**SUBPLAN Lifecycle**:
1. **Design Phase**: Create SUBPLAN file (200-600 lines)
   - Define objective, deliverables, approach
   - Plan execution strategy (single or multiple EXECUTIONs)
   - **MANDATORY**: Register in PLAN's "Active Components"

2. **Execution Phase**: Create EXECUTION_TASKs based on SUBPLAN
   - **MANDATORY**: Register each EXECUTION_TASK in PLAN

3. **Completion Phase**: All EXECUTION_TASKs complete
   - Move SUBPLAN to "Subplan Tracking" in PLAN
   - Update SUBPLAN status to "Complete"

**SUBPLAN Location**:
- Active: `work-space/subplans/SUBPLAN_FEATURE_NN.md`
- Archived: `documentation/archive/FEATURE/subplans/SUBPLAN_FEATURE_NN.md`

**Check SUBPLAN Status**:
- Read SUBPLAN's "🔄 Active EXECUTION_TASKs" section
- Check PLAN's "Active Components" for registration

---

### ✅ EXECUTION_TASK Control

#### EXECUTION_TASK States

1. **Planning**: EXECUTION_TASK created, not yet executing
2. **Executing**: Work in progress
3. **Complete**: Execution finished, deliverables verified
4. **Failed**: Execution encountered issues
5. **Abandoned**: Execution stopped, not resuming

#### How to Control EXECUTION_TASK

**Create EXECUTION_TASK**:
- Based on SUBPLAN's execution strategy
- File: `work-space/execution/EXECUTION_TASK_FEATURE_SUBPLAN_EXECUTION.md`
- **MANDATORY**: Register in PLAN's "Active Components"

**Execute EXECUTION_TASK**:
1. Read EXECUTION_TASK file (objective, approach)
2. Read SUBPLAN (objective only, 1-2 sentences)
3. Execute work according to SUBPLAN plan
4. Document iterations in EXECUTION_TASK

**Complete EXECUTION_TASK**:
1. Verify all deliverables exist (`ls -1` each file)
2. Update EXECUTION_TASK:
   - Mark iteration as "Complete"
   - Add Learning Summary
   - Verify <200 lines
3. **MANDATORY**: Update PLAN:
   - Move from "Active" to "Subplan Tracking"
   - Update statistics (iterations, time)

**EXECUTION_TASK Location**:
- Active: `work-space/execution/EXECUTION_TASK_FEATURE_NN_MM.md`
- Archived: `documentation/archive/FEATURE/execution/EXECUTION_TASK_FEATURE_NN_MM.md`

**Resume EXECUTION_TASK**:
- Read EXECUTION_TASK file (last iteration)
- Continue from where you left off

---

### 🔄 Complete Workflow Example

**Scenario**: Starting Achievement 0.1

**Step 1: Generate Prompt**
```bash
python LLM/scripts/generation/generate_prompt.py --next @PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md
```

**Step 2: Create SUBPLAN**
- Create `work-space/subplans/SUBPLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE_01.md`
- **MANDATORY**: Update PLAN's "Active Components" → "Active SUBPLANs"
  ```
  - SUBPLAN_01: Achievement 0.1 - Status: In Progress
  ```

**Step 3: Create EXECUTION_TASK**
- Create `work-space/execution/EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-EXCELLENCE_01_01.md`
- **MANDATORY**: Update PLAN's "Active Components" → "Active EXECUTION_TASKs"
  ```
  - SUBPLAN_01: Achievement 0.1 - Status: In Progress
    └─ EXECUTION_TASK_01_01: [Description] - Status: Planning
  ```

**Step 4: Execute Work**
- Update EXECUTION_TASK status: "Executing"
- Do the work
- Document iterations

**Step 5: Complete EXECUTION_TASK**
- Verify deliverables: `ls -1 [each file]`
- Update EXECUTION_TASK: Mark complete, add learning summary
- **MANDATORY**: Update PLAN:
  - Move to "Subplan Tracking"
  - Update statistics:
    ```
    - **EXECUTION_TASKs**: 1 created (1 complete, 0 abandoned)
    - **Total Iterations**: 1
    - **Time Spent**: 2.5h
    ```

**Step 6: Continue or Complete SUBPLAN**
- If more EXECUTIONs needed: Create next EXECUTION_TASK
- If all EXECUTIONs complete: Mark SUBPLAN "Complete" in PLAN

**Step 7: Continue or Complete PLAN**
- If more achievements: Generate next prompt
- If all achievements complete: Follow END_POINT protocol

---

### 🚨 Common Issues and Solutions

#### Issue 1: "No achievements found or all complete!"

**Cause**: Prompt generator thinks PLAN is complete

**Check**:
```bash
# Check if PLAN is marked complete
grep -i "complete\|✅.*plan\|all.*complete" work-space/plans/PLAN_FEATURE.md | head -5

# Check achievement status
python LLM/scripts/validation/validate_plan_completion.py @PLAN_FEATURE.md

# Check what prompt generator sees
python LLM/scripts/generation/generate_prompt.py --achievement 0.1 @PLAN_FEATURE.md
```

**Fix**:
- Ensure "Current Status & Handoff" shows "In Progress" or "Ready to Execute"
- Remove any "✅ PLAN Complete" or "All achievements complete" text
- Ensure at least one achievement is NOT marked complete
- Check that SUBPLAN exists in correct location: `work-space/subplans/SUBPLAN_FEATURE_NN.md`
- **Common False Positive**: Text like "validation PLAN complete" matches "PLAN complete" pattern - change to "validation work complete"

#### Issue 2: Prompt Generator Can't Find SUBPLAN

**Cause**: SUBPLAN in wrong location or wrong naming

**Check**:
```bash
# Check SUBPLAN location
ls -1 work-space/subplans/SUBPLAN_FEATURE_*.md

# Check naming (should be SUBPLAN_FEATURE_NN.md where NN = achievement number without dot)
# Example: Achievement 0.1 → SUBPLAN_FEATURE_01.md
```

**Fix**:
- Ensure SUBPLAN in `work-space/subplans/`
- Ensure naming: `SUBPLAN_FEATURE_NN.md` (NN = achievement number, dot removed)

#### Issue 3: PLAN Not Tracking Active Work

**Cause**: SUBPLAN/EXECUTION_TASK not registered in PLAN

**Check**:
```bash
# Check if registered
grep -A 5 "Active Components" work-space/plans/PLAN_FEATURE.md
```

**Fix**:
- Manually add to PLAN's "Active Components" section
- Follow registration workflow (see "Registration Workflow" below)

#### Issue 4: Can't Resume Work

**Cause**: Don't know what's active

**Check**:
1. Read PLAN's "Active Components" section
2. Read SUBPLAN's "Active EXECUTION_TASKs" section
3. Read EXECUTION_TASK file (last iteration)

**Fix**:
- Use resume prompt: `generate_resume_prompt.py`
- Or manually read active components

---

### 📊 Tracking Checklist

**After Creating SUBPLAN**:
- [ ] SUBPLAN file created in `work-space/subplans/`
- [ ] SUBPLAN registered in PLAN's "Active Components"
- [ ] SUBPLAN status set to "In Progress"

**After Creating EXECUTION_TASK**:
- [ ] EXECUTION_TASK file created in `work-space/execution/`
- [ ] EXECUTION_TASK registered in PLAN's "Active Components"
- [ ] EXECUTION_TASK status set to "Planning" or "Executing"

**After Completing EXECUTION_TASK**:
- [ ] All deliverables verified (`ls -1` each file)
- [ ] EXECUTION_TASK marked complete with learning summary
- [ ] EXECUTION_TASK <200 lines
- [ ] Moved to PLAN's "Subplan Tracking"
- [ ] PLAN statistics updated (iterations, time)

**After Completing SUBPLAN**:
- [ ] All EXECUTION_TASKs complete
- [ ] SUBPLAN status set to "Complete" in PLAN
- [ ] Ready to archive (when achievement complete)

---

### 🎯 Quick Reference Commands

```bash
# Generate next achievement prompt
python LLM/scripts/generation/generate_prompt.py --next @PLAN_FEATURE.md

# Generate specific achievement prompt
python LLM/scripts/generation/generate_prompt.py --achievement 0.1 @PLAN_FEATURE.md

# Generate SUBPLAN-only prompt
python LLM/scripts/generation/generate_prompt.py --achievement 0.1 --subplan-only @PLAN_FEATURE.md

# Generate resume prompt
python LLM/scripts/generation/generate_resume_prompt.py @PLAN_FEATURE.md

# Validate PLAN completion
python LLM/scripts/validation/validate_plan_completion.py @PLAN_FEATURE.md

# Check EXECUTION_TASK size
python LLM/scripts/validation/check_execution_task_size.py @EXECUTION_TASK_FILE.md
```

---

## 📝 Registration Workflow (MANDATORY)

### When Creating SUBPLAN

1. Create SUBPLAN file
2. **Immediately** open PLAN file
3. Find "🔄 Active Components" section
4. Add to "Active SUBPLANs":
   ```
   - SUBPLAN_01: Achievement 0.1 - Transformation Logging Infrastructure - Status: In Progress
   ```
5. Save PLAN
6. Verify: `grep "SUBPLAN_01" PLAN_FILE.md`

### When Creating EXECUTION_TASK

1. Create EXECUTION_TASK file
2. **Immediately** open PLAN file
3. Find "🔄 Active Components" section
4. Add to "Active EXECUTION_TASKs" under parent SUBPLAN:
   ```
   - SUBPLAN_01: Achievement 0.1 - Status: In Progress
     └─ EXECUTION_TASK_01_01: Transformation Logger Service - Status: In Progress
   ```
5. Save PLAN
6. Verify: `grep "EXECUTION_TASK_01_01" PLAN_FILE.md`

### When Completing EXECUTION_TASK

1. Mark EXECUTION_TASK complete in file
2. **Immediately** open PLAN file
3. Read EXECUTION_TASK to get:
   - Iterations count
   - Time spent
   - Status
4. Move from "Active EXECUTION_TASKs" to "Subplan Tracking"
5. Update statistics:
   - Increment EXECUTION_TASK count
   - Add iterations to total
   - Add time to total
6. Update SUBPLAN status if all EXECUTIONs complete
7. Save PLAN

---

## 📊 Status Updates

### Status Values

- **SUBPLAN**: Not Started / In Progress / Complete
- **EXECUTION_TASK**: Planning / Executing / Complete / Failed / Abandoned

### When to Update

- **SUBPLAN**: When first EXECUTION starts → "In Progress", when all EXECUTIONs complete → "Complete"
- **EXECUTION_TASK**: When created → "Planning", when work starts → "Executing", when done → "Complete"

---

## 📊 Statistics Tracking

### Required Statistics (from PLAN template)

- **SUBPLANs**: Count created, complete, in progress, pending
- **EXECUTION_TASKs**: Count created, complete, abandoned
- **Total Iterations**: Sum across all EXECUTION_TASKs
- **Average Iterations**: Total iterations / EXECUTION_TASK count
- **Circular Debugging**: Count of EXECUTION_TASKs with execution number > 1
- **Time Spent**: Sum of time from all completed EXECUTION_TASKs

### Source

Read from EXECUTION_TASK files, not estimated

---

## 📚 References

### Methodology Documents

- `LLM-METHODOLOGY.md` - Core methodology
- `LLM/templates/PLAN-TEMPLATE.md` - PLAN structure
- `LLM/templates/SUBPLAN-TEMPLATE.md` - SUBPLAN structure
- `LLM/templates/EXECUTION_TASK-TEMPLATE.md` - EXECUTION_TASK structure
- `LLM/templates/PROMPTS.md` - Standard prompts

### Related Analysis

- `EXECUTION_ANALYSIS_SUBPLAN-TRACKING-GAP.md` - Tracking gap analysis and registration requirements

### Case Study Files

- `work-space/subplans/SUBPLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE_01.md` - Example SUBPLAN
- `work-space/execution/EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-EXCELLENCE_01_01.md` - Example EXECUTION_TASK
- `work-space/plans/PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md` - Example PLAN

---

## ✅ Success Criteria

**This guide is successful if**:

1. ✅ Clear understanding of PLAN, SUBPLAN, EXECUTION_TASK hierarchy
2. ✅ Complete workflow examples provided
3. ✅ Common issues documented with solutions
4. ✅ Quick reference commands available
5. ✅ Registration workflow clearly explained
6. ✅ Status and statistics tracking understood

**Status**: ✅ Complete  
**Next**: Use as reference when working with PLANs, SUBPLANs, and EXECUTION_TASKs

---

**Status**: Complete  
**Archive Location**: Will be archived with PLAN_GRAPHRAG-OBSERVABILITY-EXCELLENCE.md when PLAN completes


