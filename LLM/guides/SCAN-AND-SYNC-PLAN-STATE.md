# How to Scan and Sync PLAN State with File System

**Purpose**: Guide for scanning actual file system state and comparing with PLAN to identify what needs updating  
**Status**: Reference Document  
**Created**: 2025-01-28  
**Related**: `LLM/scripts/validation/validate_registration.py`, `LLM/guides/SCRIPT-BASED-WORKFLOW-EXECUTION.md`

---

## 🎯 What This Guide Is

**Step-by-step process for**:

1. **Scanning** file system to discover actual SUBPLANs and EXECUTION_TASKs
2. **Comparing** with what's registered in PLAN "Subplan Tracking" section
3. **Identifying** gaps (unregistered files, orphaned registrations)
4. **Understanding** what needs to be updated in PLAN tracking

**When to Use**:

- After manual execution (PLAN tracking is outdated)
- Before resuming work (verify SUBPLAN tracking)
- When workflow automation is broken (bootstrap scenarios)
- To audit PLAN tracking vs. actual files

**Important Distinction** (Filesystem-First Architecture):

- **This guide**: Validates PLAN "Subplan Tracking" section (SUBPLAN/EXECUTION registration)
- **NOT for**: Achievement completion status (tracked by `execution/feedbacks/APPROVED_XX.md` files)
- **State Tracking**: Achievement completion tracked via filesystem (`APPROVED_XX.md`), not PLAN markdown
- **This is**: Validation tool for SUBPLAN registration, not state tracking for achievements

**Note**: This guide shows you **how to scan and identify tracking issues**. You'll still need to manually update the PLAN "Subplan Tracking" section based on scan results.

**Reference**: See `LLM/docs/FEEDBACK_SYSTEM_GUIDE.md` for achievement completion tracking

---

## 📋 Step 1: Scan and Compare State

### Primary Tool: `validate_registration.py`

**This script does exactly what you need**:

- Scans file system for SUBPLANs and EXECUTION_TASKs
- Extracts what's registered in PLAN
- Compares them and reports gaps

**Usage**:

```bash
# Scan PLAN and compare with file system
python LLM/scripts/validation/validate_registration.py @PLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING.md
```

**What It Does**:

1. **Finds Actual Files**:

   - Scans for `SUBPLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_*.md` in:
     - Current directory (root)
     - `work-space/subplans/` (workspace)
     - Archive location (if exists)
   - Scans for `EXECUTION_TASK_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_*.md` in:
     - Current directory (root)
     - `work-space/execution/` (workspace)
     - Archive location (if exists)

2. **Extracts Registered Components**:

   - Parses PLAN's "Active Components" section
   - Parses PLAN's "Subplan Tracking" section
   - Extracts SUBPLAN and EXECUTION_TASK references

3. **Compares and Reports**:
   - **Unregistered SUBPLANs**: Files exist but not in PLAN
   - **Unregistered EXECUTION_TASKs**: Files exist but not in PLAN
   - **Orphaned Registrations**: In PLAN but file doesn't exist

**Output Example**:

```
❌ REGISTRATION ISSUES FOUND - BLOCKING CONTINUATION

Issues Found:
❌ Unregistered SUBPLANs: SUBPLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_01.md, SUBPLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_02.md
❌ Unregistered EXECUTION_TASKs: EXECUTION_TASK_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_01_01.md

📋 Fix Prompt:

To fix these issues:
1. Register unregistered SUBPLANs in PLAN 'Active Components' section:
   - SUBPLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_01.md
   - SUBPLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_02.md
2. Register unregistered EXECUTION_TASKs in PLAN 'Active Components' section:
   - EXECUTION_TASK_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_01_01.md
```

**Or if everything is registered**:

```
✅ Component registration validated

Checks passed:
✓ All SUBPLANs registered (2 total)
✓ All EXECUTION_TASKs registered (1 total)

Safe to continue!
```

---

## 📋 Step 2: Get Detailed File Information

### Option A: Manual File System Scan

**List all SUBPLANs**:

```bash
# Check workspace
ls -1 work-space/subplans/SUBPLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_*.md

# Check root (if any)
ls -1 SUBPLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_*.md

# Check archive (if exists)
ls -1 documentation/archive/*/subplans/SUBPLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_*.md
```

**List all EXECUTION_TASKs**:

```bash
# Check workspace
ls -1 work-space/execution/EXECUTION_TASK_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_*.md

# Check root (if any)
ls -1 EXECUTION_TASK_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_*.md

# Check archive (if exists)
ls -1 documentation/archive/*/execution/EXECUTION_TASK_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_*.md
```

### Option B: Use Discovery Functions (Python)

**You can use the discovery functions from the scripts**:

```python
from pathlib import Path
from LLM.scripts.validation.validate_registration import (
    find_subplans_for_plan,
    find_execution_tasks_for_plan
)

plan_path = Path("work-space/plans/PLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING.md")

# Find all SUBPLANs
subplans = find_subplans_for_plan(plan_path)
print("SUBPLANs found:")
for subplan in subplans:
    print(f"  - {subplan}")

# Find all EXECUTION_TASKs
executions = find_execution_tasks_for_plan(plan_path)
print("EXECUTION_TASKs found:")
for execution in executions:
    print(f"  - {execution}")
```

---

## 📋 Step 3: Check SUBPLAN and EXECUTION_TASK Status

### Check SUBPLAN Status

**For each SUBPLAN found**, check its status:

```bash
# Read SUBPLAN to check status
grep -i "Status" work-space/subplans/SUBPLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_01.md

# Check if it has EXECUTION_TASKs
grep -i "EXECUTION_TASK" work-space/subplans/SUBPLAN_WORKFLAN-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_01.md
```

**Or use Python**:

```python
from LLM.scripts.generation.generate_subplan_prompt import get_subplan_status

with open("work-space/subplans/SUBPLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_01.md") as f:
    content = f.read()

status = get_subplan_status(content)
print(f"Phase: {status['phase']}")
print(f"Has executions: {status['has_executions']}")
print(f"Active: {status['active_count']}")
print(f"Completed: {status['completed_count']}")
```

### Check EXECUTION_TASK Status

**For each EXECUTION_TASK found**, check completion:

```bash
# Check if complete
grep -i "Complete\|Status.*Complete" work-space/execution/EXECUTION_TASK_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_01_01.md

# Check iteration count
grep -c "### Iteration" work-space/execution/EXECUTION_TASK_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_01_01.md

# Check time spent (if documented)
grep -i "Time Spent\|hours" work-space/execution/EXECUTION_TASK_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_01_01.md
```

---

## 📋 Step 4: Extract Information for PLAN Update

### Information Needed for PLAN Update

For each **unregistered SUBPLAN**, you need:

1. **SUBPLAN number** (from filename: `SUBPLAN_FEATURE_XX.md`)
2. **Achievement it addresses** (read SUBPLAN header)
3. **Status** (In Progress / Complete)
4. **Location** (workspace / archive)

For each **unregistered EXECUTION_TASK**, you need:

1. **EXECUTION_TASK number** (from filename: `EXECUTION_TASK_FEATURE_XX_YY.md`)
2. **Parent SUBPLAN** (from filename or SUBPLAN content)
3. **Status** (In Progress / Complete)
4. **Iteration count** (from EXECUTION_TASK)
5. **Time spent** (from EXECUTION_TASK, if documented)
6. **Location** (workspace / archive)

### Extract from Files

**Quick extraction script** (you can run this):

```python
#!/usr/bin/env python3
"""Quick scan to extract information for PLAN update"""

from pathlib import Path
import re

plan_path = Path("work-space/plans/PLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING.md")
feature = "WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING"

# Find SUBPLANs
subplans = list(Path("work-space/subplans").glob(f"SUBPLAN_{feature}_*.md"))
print("SUBPLANs found:")
for subplan in subplans:
    with open(subplan) as f:
        content = f.read()
    # Extract achievement
    ach_match = re.search(r"Achievement.*?(\d+\.\d+)", content)
    achievement = ach_match.group(1) if ach_match else "Unknown"
    # Extract status
    status_match = re.search(r"Status.*?(\w+)", content)
    status = status_match.group(1) if status_match else "Unknown"
    print(f"  {subplan.name}: Achievement {achievement}, Status: {status}")

# Find EXECUTION_TASKs
executions = list(Path("work-space/execution").glob(f"EXECUTION_TASK_{feature}_*.md"))
print("\nEXECUTION_TASKs found:")
for execution in executions:
    with open(execution) as f:
        content = f.read()
    # Extract status
    status_match = re.search(r"Status.*?(\w+)|Complete", content, re.IGNORECASE)
    status = status_match.group(1) if status_match else "Unknown"
    # Count iterations
    iterations = len(re.findall(r"### Iteration", content))
    print(f"  {execution.name}: Status: {status}, Iterations: {iterations}")
```

---

## 📋 Step 5: Understand What Needs Updating

### Based on `validate_registration.py` Output

**If you see "Unregistered SUBPLANs"**:

- These SUBPLANs exist in file system but aren't in PLAN
- **Action**: Add them to PLAN's "Active Components" section
- **Format**: `- SUBPLAN_XX: Achievement X.Y - Status: [status]`

**If you see "Unregistered EXECUTION_TASKs"**:

- These EXECUTION_TASKs exist but aren't in PLAN
- **Action**: Add them to PLAN's "Active Components" section
- **Format**: `- EXECUTION_TASK_XX_YY: Achievement X.Y - Status: [status]`

**If you see "Orphaned Registrations"**:

- These are registered in PLAN but file doesn't exist
- **Action**: Remove from PLAN (or check if archived)

### Update PLAN Sections

**1. "Active Components" Section**:

Add unregistered components here:

```markdown
## 🔄 Active Components (Updated When Created)

**Active SUBPLANs**:

- SUBPLAN_01: Achievement 0.1 - Status: In Progress
- SUBPLAN_02: Achievement 0.2 - Status: In Progress

**Active EXECUTION_TASKs**:

- EXECUTION_TASK_01_01: Achievement 0.1 - Status: In Progress
```

**2. "Subplan Tracking" Section**:

Add completed components here:

```markdown
## 🔄 Subplan Tracking

- SUBPLAN_01: Achievement 0.1 - Status: Complete ✅
  └─ EXECUTION_TASK_01_01: Complete (1 iteration, 2.5h)
```

**3. "Current Status & Handoff" Section**:

Update to reflect current state:

```markdown
## 📝 Current Status & Handoff

**What's Done**:

- ✅ SUBPLAN_01 created for Achievement 0.1
- ✅ EXECUTION_TASK_01_01 complete

**Active Work**:

- SUBPLAN_01: Achievement 0.1 - 1/6 EXECUTIONs complete
  - ✅ EXECUTION_TASK_01_01: Complete
  - ⏳ EXECUTION_TASK_01_02: Next

**What's Next**:

- Continue Achievement 0.1 (EXECUTION_TASK_01_02)
```

**4. Summary Statistics**:

Update based on actual counts:

```markdown
## 📊 Summary Statistics

**SUBPLANs**: 2 created (1 complete, 1 in progress)
**EXECUTION_TASKs**: 1 created (1 complete)
**Total Iterations**: 1
**Time Spent**: 2.5h
```

---

## 📋 Step 6: Verify After Update

**After updating PLAN**, verify again:

```bash
# Re-run validation
python LLM/scripts/validation/validate_registration.py @PLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING.md
```

**Should show**:

```
✅ Component registration validated

Checks passed:
✓ All SUBPLANs registered (2 total)
✓ All EXECUTION_TASKs registered (1 total)

Safe to continue!
```

---

## 🔧 Complete Workflow Example

### Scenario: PLAN is Outdated After Manual Execution

**Step 1: Scan State**

```bash
python LLM/scripts/validation/validate_registration.py @PLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING.md
```

**Output**:

```
❌ Unregistered SUBPLANs: SUBPLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_01.md, SUBPLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_02.md
❌ Unregistered EXECUTION_TASKs: EXECUTION_TASK_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_01_01.md
```

**Step 2: Get Details**

```bash
# Check SUBPLAN status
grep -i "Achievement\|Status" work-space/subplans/SUBPLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_01.md

# Check EXECUTION_TASK status
grep -i "Status\|Complete\|Iteration" work-space/execution/EXECUTION_TASK_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING_01_01.md
```

**Step 3: Update PLAN**

Manually add to PLAN:

- "Active Components" section
- "Subplan Tracking" section
- "Current Status & Handoff" section
- Summary statistics

**Step 4: Verify**

```bash
python LLM/scripts/validation/validate_registration.py @PLAN_WORKFLOW-AUTOMATION-AND-WORKSPACE-RESTRUCTURING.md
```

**Should pass** ✅

---

## 📚 Related Scripts and Functions

### Discovery Functions

**From `validate_registration.py`**:

- `find_subplans_for_plan(plan_path)` - Find all SUBPLANs for PLAN
- `find_execution_tasks_for_plan(plan_path)` - Find all EXECUTION_TASKs for PLAN
- `find_execution_tasks_for_subplan(subplan_path)` - Find EXECUTION_TASKs for SUBPLAN

**From `generate_prompt.py`**:

- `find_subplan_for_achievement(feature_name, achievement_num)` - Find SUBPLAN for specific achievement
- `check_subplan_status(subplan_path)` - Check SUBPLAN status
- `detect_workflow_state(plan_path, feature_name, achievement_num)` - Detect workflow state

**From `generate_subplan_prompt.py`**:

- `get_subplan_status(subplan_content)` - Get SUBPLAN phase and status
- `find_execution_files(subplan_path)` - Find EXECUTION_TASKs for SUBPLAN

### Validation Scripts

- `validate_registration.py` - **Primary tool** for scanning and comparing
- `validate_mid_plan.py` - Extract statistics from PLAN
- `validate_plan_completion.py` - Check if PLAN is complete

---

## ⚠️ Important Notes

### File Locations

The scripts check multiple locations:

1. **Current directory** (root) - for legacy files
2. **`work-space/subplans/`** - workspace SUBPLANs
3. **`work-space/execution/`** - workspace EXECUTION_TASKs
4. **Archive location** - from PLAN's "Archive Location" section

### Structure Detection

Scripts support both:

- **Flat structure**: Files in `work-space/subplans/` and `work-space/execution/`
- **Nested structure**: Files in `plan_folder/subplans/` and `plan_folder/execution/`

The scripts auto-detect which structure is used.

### Manual Update Required

**Important**: The scripts **scan and report**, but **do not automatically update** the PLAN. You must:

1. Read the scan results
2. Extract information from files
3. Manually update PLAN sections
4. Verify with validation script

This is by design - PLAN updates require human review to ensure accuracy.

---

## 📋 Quick Reference

### Scan State

```bash
# Primary tool
python LLM/scripts/validation/validate_registration.py @PLAN_FEATURE.md
```

### List Files Manually

```bash
# SUBPLANs
ls -1 work-space/subplans/SUBPLAN_FEATURE_*.md

# EXECUTION_TASKs
ls -1 work-space/execution/EXECUTION_TASK_FEATURE_*.md
```

### Check Status

```bash
# SUBPLAN status
grep -i "Status\|Achievement" work-space/subplans/SUBPLAN_FEATURE_01.md

# EXECUTION_TASK status
grep -i "Status\|Complete" work-space/execution/EXECUTION_TASK_FEATURE_01_01.md
```

### Verify After Update

```bash
python LLM/scripts/validation/validate_registration.py @PLAN_FEATURE.md
```

---

## 🔗 Related Documentation

- `LLM/scripts/validation/validate_registration.py` - The primary scanning tool
- `LLM/guides/SCRIPT-BASED-WORKFLOW-EXECUTION.md` - Complete workflow guide
- `EXECUTION_ANALYSIS_BOOTSTRAP-PROBLEM-WORKFLOW-AUTOMATION.md` - Bootstrap scenarios

---

**Status**: Complete  
**Last Updated**: 2025-01-28  
**Maintained By**: Methodology documentation
