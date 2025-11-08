# Script-Based Workflow Execution Guide

**Purpose**: Comprehensive guide for executing PLAN implementation workflow using automation scripts  
**Status**: Reference Document  
**Created**: 2025-01-28  
**Related**: `LLM/protocols/IMPLEMENTATION_START_POINT.md`, `LLM/scripts/README.md`, `EXECUTION_ANALYSIS_BOOTSTRAP-PROBLEM-WORKFLOW-AUTOMATION.md`

---

## 🎯 What This Guide Is

**Complete workflow for executing PLANs using automation scripts**, covering:

- Step-by-step script-based execution
- Script commands for each workflow phase
- Manual fallback when scripts fail (bootstrap scenarios)
- Validation and verification steps
- Troubleshooting common issues

**When to Use**:

- Executing PLANs with automation support
- Bootstrap scenarios (when workflow automation is broken)
- Understanding script-based workflow
- Troubleshooting execution issues

**Related**: See `EXECUTION_ANALYSIS_BOOTSTRAP-PROBLEM-WORKFLOW-AUTOMATION.md` for bootstrap problem solutions

---

## 📋 Complete Workflow: Script-Based Execution

### Phase 1: Start Achievement Execution

**Goal**: Generate prompt for next achievement and begin work

**Step 1.1: Find Next Achievement**

```bash
# Auto-detect next achievement (recommended)
python LLM/scripts/generation/generate_prompt.py --next @PLAN_FEATURE.md

# Specific achievement
python LLM/scripts/generation/generate_prompt.py --achievement 0.1 @PLAN_FEATURE.md

# Copy to clipboard
python LLM/scripts/generation/generate_prompt.py --next @PLAN_FEATURE.md --clipboard
```

**What It Does**:

- Detects next incomplete achievement
- Checks for existing SUBPLANs/EXECUTION_TASKs
- Generates context-bounded prompt
- Includes required steps and validation

**Output**: Prompt with:

- Context boundaries (what to read)
- Required steps (SUBPLAN, EXECUTION_TASK creation)
- Validation scripts that will run
- DO NOT reminders

**Step 1.2: Verify Achievement Selection**

```bash
# Check if achievement is correct
python LLM/scripts/validation/validate_plan_compliance.py @PLAN_FEATURE.md

# Check completion status
python LLM/scripts/generation/generate_completion_status.py @PLAN_FEATURE.md
```

**If Scripts Fail (Bootstrap Scenario)**:

1. **Manual Check**: Read PLAN's "Current Status & Handoff" section
2. **Manual Selection**: Find first incomplete achievement
3. **Manual Prompt**: Use template from `LLM/templates/PROMPTS.md`

---

### Phase 2: Create SUBPLAN (Designer Phase)

**Goal**: Create comprehensive SUBPLAN for achievement

**Step 2.1: Generate SUBPLAN Creation Prompt**

```bash
# Generate SUBPLAN prompt
python LLM/scripts/generation/generate_subplan_prompt.py create @PLAN_FEATURE.md --achievement 0.1

# Copy to clipboard
python LLM/scripts/generation/generate_subplan_prompt.py create @PLAN_FEATURE.md --achievement 0.1 --clipboard
```

**What It Does**:

- Extracts achievement section from PLAN
- Generates SUBPLAN creation prompt
- Includes template reference
- Includes workflow guide reference

**Step 2.2: Create SUBPLAN File**

**Using Script (if available)**:

```bash
# Script would create file (if implemented)
# For now, create manually using template
```

**Manual Creation**:

1. Copy `LLM/templates/SUBPLAN-TEMPLATE.md`
2. Save as `work-space/subplans/SUBPLAN_FEATURE_01.md`
3. Fill in achievement details
4. Follow `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` Phase 1

**Step 2.3: Register SUBPLAN in PLAN**

**Using Auto-Registration (if available)**:

```bash
# Auto-register SUBPLAN (if implemented)
python LLM/scripts/workflow/auto_register_components.py --subplan @SUBPLAN_FEATURE_01.md
```

**Manual Registration** (Bootstrap Scenario):

1. Open PLAN file
2. Add to "Active Components" section:
   ```markdown
   - SUBPLAN_01: Achievement 0.1 - Status: In Progress
   ```
3. Add to "Subplan Tracking" section
4. Update "Current Status & Handoff"

**Step 2.4: Validate SUBPLAN**

```bash
# Validate SUBPLAN compliance
python LLM/scripts/validation/validate_execution_start.py @SUBPLAN_FEATURE_01.md

# Check SUBPLAN size (should be 200-600 lines)
wc -l work-space/subplans/SUBPLAN_FEATURE_01.md
```

---

### Phase 3: Plan Execution(s) (Designer Phase)

**Goal**: Plan EXECUTION_TASK(s) for SUBPLAN

**Step 3.1: Decide Execution Strategy**

**Decision Tree** (from `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md`):

- Single EXECUTION: Simple, straightforward work
- Multiple EXECUTIONs: Complex work, A/B testing, parallel work

**Step 3.2: Document Execution Strategy in SUBPLAN**

Add to SUBPLAN:

```markdown
## 🔄 Execution Plan

**Execution Count**: 1 EXECUTION (single)

**Rationale**: [Why single or multiple]

**EXECUTION 01**: [What this execution will do]
```

**For Multiple EXECUTIONs**:

```markdown
**Execution Count**: 3 EXECUTIONs (parallel)

**EXECUTION 01**: Algorithm A (baseline)
**EXECUTION 02**: Algorithm B (optimized)
**EXECUTION 03**: Algorithm C (alternative)
```

---

### Phase 4: Create EXECUTION_TASK (Executor Phase)

**Goal**: Create EXECUTION_TASK file(s) for execution

**Step 4.1: Generate EXECUTION Creation Prompt**

```bash
# Generate EXECUTION prompt from SUBPLAN
python LLM/scripts/generation/generate_execution_prompt.py create @SUBPLAN_FEATURE_01.md --execution 01

# Copy to clipboard
python LLM/scripts/generation/generate_execution_prompt.py create @SUBPLAN_FEATURE_01.md --execution 01 --clipboard
```

**What It Does**:

- Extracts SUBPLAN objective (minimal context)
- Generates EXECUTION creation prompt
- Includes deliverables and success criteria
- Focuses executor on specific work

**Step 4.2: Create EXECUTION_TASK File**

**Manual Creation**:

1. Copy `LLM/templates/EXECUTION_TASK-TEMPLATE.md`
2. Save as `work-space/execution/EXECUTION_TASK_FEATURE_01_01.md`
3. Fill in SUBPLAN objective and deliverables
4. Start with "Iteration 1" in iteration log

**Step 4.3: Register EXECUTION_TASK in PLAN**

**Using Auto-Registration (if available)**:

```bash
# Auto-register EXECUTION_TASK (if implemented)
python LLM/scripts/workflow/auto_register_components.py --execution @EXECUTION_TASK_FEATURE_01_01.md
```

**Manual Registration** (Bootstrap Scenario):

1. Open PLAN file
2. Add to "Active Components" section:
   ```markdown
   - EXECUTION_TASK_01_01: Achievement 0.1 - Status: In Progress
   ```
3. Update "Current Status & Handoff"

**Step 4.4: Validate EXECUTION_TASK**

```bash
# Check EXECUTION_TASK size (must be <200 lines)
python LLM/scripts/validation/check_execution_task_size.py @EXECUTION_TASK_FEATURE_01_01.md

# Validate execution start
python LLM/scripts/validation/validate_execution_start.py @EXECUTION_TASK_FEATURE_01_01.md
```

---

### Phase 5: Execute Work (Executor Phase)

**Goal**: Implement achievement deliverables

**Step 5.1: Execute According to SUBPLAN**

- Follow SUBPLAN approach
- Implement deliverables listed in SUBPLAN
- Follow TDD workflow if code work
- Document progress in EXECUTION_TASK iteration log

**Step 5.2: Document Iterations**

Update EXECUTION_TASK after each iteration:

```markdown
## 🔄 Iteration Log

### Iteration 1: [Date] - [Status: Planning / Executing / Complete]

**What I Did**:

- [Action 1]
- [Action 2]

**What Worked**:

- [Success 1]

**What Didn't Work**:

- [Issue 1]

**Next Steps**:

- [Next action]
```

**Step 5.3: Verify Deliverables**

```bash
# Verify each deliverable exists
ls -1 [deliverable_path_1]
ls -1 [deliverable_path_2]

# Run validation
python LLM/scripts/validation/validate_achievement_completion.py @PLAN_FEATURE.md --achievement 0.1
```

**Validation Scripts Run Automatically**:

- `validate_achievement_completion.py` - Checks deliverables exist
- `validate_execution_start.py` - Validates execution compliance
- `check_plan_size.py` - Validates PLAN size
- `check_execution_task_size.py` - Validates EXECUTION_TASK size

---

### Phase 6: Complete EXECUTION_TASK

**Goal**: Mark EXECUTION_TASK complete and capture learnings

**Step 6.1: Update EXECUTION_TASK**

1. **Mark Iteration Complete**:

   ```markdown
   ### Iteration N: [Date] - Status: Complete ✅
   ```

2. **Add Learning Summary**:

   ```markdown
   ## 📚 Learning Summary

   **Key Learnings**:

   - [Learning 1]
   - [Learning 2]

   **What Worked Well**:

   - [Success 1]

   **What Could Be Improved**:

   - [Improvement 1]

   **Time Spent**: [X hours]
   ```

3. **Verify Size** (<200 lines):
   ```bash
   wc -l work-space/execution/EXECUTION_TASK_FEATURE_01_01.md
   ```

**Step 6.2: Update PLAN Statistics**

**Manual Update** (Bootstrap Scenario):

1. Open PLAN file
2. Update "Subplan Tracking" section:
   ```markdown
   - SUBPLAN_01: Achievement 0.1 - Status: Complete ✅
     └─ EXECUTION_TASK_01_01: Complete (1 iteration, 2.5h)
   ```
3. Update summary statistics:
   ```markdown
   - **EXECUTION_TASKs**: 1 created (1 complete)
   - **Total Iterations**: 1
   - **Time Spent**: 2.5h
   ```

**Step 6.3: Validate Completion**

```bash
# Validate EXECUTION_TASK completion
python LLM/scripts/validation/validate_achievement_completion.py @PLAN_FEATURE.md --achievement 0.1

# Check registration
python LLM/scripts/validation/validate_registration.py @PLAN_FEATURE.md
```

---

### Phase 7: Archive (Deferred or Manual)

**Goal**: Archive completed SUBPLAN and EXECUTION_TASK

**Step 7.1: Archive Files**

**Using Manual Archive Script**:

```bash
# Dry-run first
python LLM/scripts/archiving/manual_archive.py --dry-run @SUBPLAN_FEATURE_01.md @EXECUTION_TASK_FEATURE_01_01.md

# Archive files
python LLM/scripts/archiving/manual_archive.py @SUBPLAN_FEATURE_01.md @EXECUTION_TASK_FEATURE_01_01.md
```

**Using Archive Completed Script**:

```bash
# Archive completed files
python LLM/scripts/archiving/archive_completed.py @SUBPLAN_FEATURE_01.md @EXECUTION_TASK_FEATURE_01_01.md

# Batch mode
python LLM/scripts/archiving/archive_completed.py --batch @SUBPLAN_FEATURE_01.md @EXECUTION_TASK_FEATURE_01_01.md
```

**Manual Archive** (Bootstrap Scenario):

1. Create archive structure:
   ```bash
   mkdir -p documentation/archive/feature-name/subplans
   mkdir -p documentation/archive/feature-name/execution
   ```
2. Move files:
   ```bash
   mv work-space/subplans/SUBPLAN_FEATURE_01.md documentation/archive/feature-name/subplans/
   mv work-space/execution/EXECUTION_TASK_FEATURE_01_01.md documentation/archive/feature-name/execution/
   ```

**Step 7.2: Update PLAN**

Remove from "Active Components", keep in "Subplan Tracking"

**Step 7.3: Validate Archive**

```bash
# Validate archive structure
python LLM/scripts/validation/validate_archive_structure.py documentation/archive/feature-name/

# Validate archive location matches PLAN
python LLM/scripts/validation/validate_archive_location.py @PLAN_FEATURE.md
```

---

### Phase 8: Continue to Next Achievement

**Goal**: Move to next achievement or complete PLAN

**Step 8.1: Generate Next Prompt**

```bash
# Auto-detect next achievement
python LLM/scripts/generation/generate_prompt.py --next @PLAN_FEATURE.md

# Check if PLAN complete
python LLM/scripts/validation/validate_plan_completion.py @PLAN_FEATURE.md
```

**Step 8.2: If PLAN Complete**

Follow `LLM/protocols/IMPLEMENTATION_END_POINT.md`:

1. Final validation
2. Archive PLAN
3. Update ACTIVE_PLANS.md
4. Create completion summary

---

## 🔧 Script Reference

### Generation Scripts

| Script                          | Purpose                     | Usage                               |
| ------------------------------- | --------------------------- | ----------------------------------- |
| `generate_prompt.py`            | Generate achievement prompt | `--next` or `--achievement N.N`     |
| `generate_subplan_prompt.py`    | Generate SUBPLAN prompt     | `create @PLAN.md --achievement N.N` |
| `generate_execution_prompt.py`  | Generate EXECUTION prompt   | `create @SUBPLAN.md --execution NN` |
| `generate_resume_prompt.py`     | Generate resume prompt      | `@PLAN.md` or `@EXECUTION_TASK.md`  |
| `generate_completion_status.py` | Check completion status     | `@PLAN.md`                          |

### Validation Scripts

| Script                               | Purpose                         | Usage                        |
| ------------------------------------ | ------------------------------- | ---------------------------- |
| `validate_plan_compliance.py`        | Validate PLAN structure         | `@PLAN.md`                   |
| `validate_achievement_completion.py` | Validate deliverables           | `@PLAN.md --achievement N.N` |
| `validate_execution_start.py`        | Validate execution start        | `@EXECUTION_TASK.md`         |
| `check_plan_size.py`                 | Check PLAN size limit           | `@PLAN.md`                   |
| `check_execution_task_size.py`       | Check EXECUTION_TASK size       | `@EXECUTION_TASK.md`         |
| `validate_registration.py`           | Validate component registration | `@PLAN.md`                   |
| `validate_plan_completion.py`        | Validate PLAN completion        | `@PLAN.md`                   |

### Archiving Scripts

| Script                 | Purpose                 | Usage                       |
| ---------------------- | ----------------------- | --------------------------- |
| `manual_archive.py`    | Manual archiving        | `@FILE.md` or `--workspace` |
| `archive_completed.py` | Archive completed files | `@FILE.md` or `--batch`     |

---

## 🚨 Bootstrap Scenarios: Manual Fallback

**When Scripts Fail or Don't Exist**:

### Manual Achievement Selection

1. Read PLAN's "Current Status & Handoff" section
2. Find first incomplete achievement
3. Read achievement section only (~100 lines)
4. Proceed with manual SUBPLAN creation

### Manual SUBPLAN Creation

1. Copy `LLM/templates/SUBPLAN-TEMPLATE.md`
2. Fill in achievement details
3. Save to `work-space/subplans/`
4. **Manually register in PLAN** (critical step)

### Manual EXECUTION_TASK Creation

1. Copy `LLM/templates/EXECUTION_TASK-TEMPLATE.md`
2. Fill in SUBPLAN objective (minimal)
3. Save to `work-space/execution/`
4. **Manually register in PLAN** (critical step)

### Manual Registration

**After Creating SUBPLAN**:

1. Open PLAN file
2. Add to "Active Components":
   ```markdown
   - SUBPLAN_01: Achievement 0.1 - Status: In Progress
   ```
3. Add to "Subplan Tracking"
4. Update "Current Status & Handoff"

**After Creating EXECUTION_TASK**:

1. Open PLAN file
2. Add to "Active Components":
   ```markdown
   - EXECUTION_TASK_01_01: Achievement 0.1 - Status: In Progress
   ```
3. Update "Current Status & Handoff"

**After Completing EXECUTION_TASK**:

1. Update "Subplan Tracking":
   ```markdown
   - SUBPLAN_01: Achievement 0.1 - Status: Complete ✅
     └─ EXECUTION_TASK_01_01: Complete (1 iteration, 2.5h)
   ```
2. Update summary statistics
3. Update "Current Status & Handoff"

### Manual Validation

**Check Deliverables**:

```bash
ls -1 [each_deliverable_path]
```

**Check File Sizes**:

```bash
wc -l work-space/subplans/SUBPLAN_FEATURE_01.md  # Should be 200-600 lines
wc -l work-space/execution/EXECUTION_TASK_FEATURE_01_01.md  # Should be <200 lines
```

**Check Registration**:

- Open PLAN file
- Verify SUBPLAN/EXECUTION_TASK listed in "Active Components"
- Verify in "Subplan Tracking"

---

## 📋 Quick Reference: Complete Workflow Commands

### Start Achievement

```bash
# Generate prompt for next achievement
python LLM/scripts/generation/generate_prompt.py --next @PLAN_FEATURE.md --clipboard
```

### Create SUBPLAN

```bash
# Generate SUBPLAN prompt
python LLM/scripts/generation/generate_subplan_prompt.py create @PLAN_FEATURE.md --achievement 0.1 --clipboard

# Validate SUBPLAN (after creation)
python LLM/scripts/validation/validate_execution_start.py @SUBPLAN_FEATURE_01.md
```

### Create EXECUTION_TASK

```bash
# Generate EXECUTION prompt
python LLM/scripts/generation/generate_execution_prompt.py create @SUBPLAN_FEATURE_01.md --execution 01 --clipboard

# Validate EXECUTION_TASK size
python LLM/scripts/validation/check_execution_task_size.py @EXECUTION_TASK_FEATURE_01_01.md
```

### Verify Deliverables

```bash
# Validate achievement completion
python LLM/scripts/validation/validate_achievement_completion.py @PLAN_FEATURE.md --achievement 0.1
```

### Archive

```bash
# Archive completed files
python LLM/scripts/archiving/manual_archive.py @SUBPLAN_FEATURE_01.md @EXECUTION_TASK_FEATURE_01_01.md
```

### Continue

```bash
# Generate next achievement prompt
python LLM/scripts/generation/generate_prompt.py --next @PLAN_FEATURE.md --clipboard
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: "No achievements found or all complete!"

**Cause**: Completion detection bug or PLAN not updated

**Solution**:

1. Check PLAN's "Current Status & Handoff" section manually
2. Verify achievement status in PLAN
3. Use `--achievement N.N` to specify achievement explicitly

### Issue 2: "SUBPLAN already exists" warning

**Cause**: SUBPLAN detection gap (not checking workspace)

**Solution**:

1. Check if SUBPLAN exists: `ls -1 work-space/subplans/SUBPLAN_FEATURE_*.md`
2. If exists, continue with EXECUTION_TASK creation
3. Use `generate_execution_prompt.py` instead

### Issue 3: Script fails with import error

**Cause**: Missing dependencies or structure detection not available

**Solution**:

1. Check Python environment: `python --version`
2. Install dependencies if needed
3. Use manual fallback (see Bootstrap Scenarios)

### Issue 4: Validation fails

**Cause**: Missing deliverables or registration

**Solution**:

1. Check deliverables exist: `ls -1 [deliverable_path]`
2. Check registration in PLAN
3. Fix issues and re-run validation

---

## 📚 Related Documentation

- `LLM/protocols/IMPLEMENTATION_START_POINT.md` - Complete methodology guide
- `LLM/scripts/README.md` - Individual script documentation
- `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` - SUBPLAN workflow details
- `EXECUTION_ANALYSIS_BOOTSTRAP-PROBLEM-WORKFLOW-AUTOMATION.md` - Bootstrap solutions
- `EXECUTION_ANALYSIS_PLAN-SUBPLAN-EXECUTION-CONTROL-FLOW.md` - Control flow guide

---

**Status**: Complete  
**Last Updated**: 2025-01-28  
**Maintained By**: Methodology documentation
