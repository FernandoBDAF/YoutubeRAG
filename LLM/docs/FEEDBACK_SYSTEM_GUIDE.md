# Feedback System Guide

**Purpose**: Comprehensive guide to the feedback system conventions used across all PLANs  
**Audience**: LLM executors, human reviewers, new contributors  
**Created**: 2025-11-12  
**Achievement**: 2.5 - Codify Feedback System Patterns

---

## 📖 Overview

The **feedback system** is how we track achievement completion in a filesystem-first way. Instead of marking achievements complete in the PLAN markdown (which gets out of sync), we use dedicated `APPROVED_XX.md` files that serve as the single source of truth for completion status.

**Core Philosophy**:

- **PLAN** defines what achievements exist (Achievement Index)
- **Filesystem** tracks which achievements are complete (APPROVED files)
- **No fallback** to PLAN markdown for completion status

---

## 🎯 Core Concepts

### 1. Achievement Index

The **Achievement Index** is a special section in every PLAN that lists all achievements in the plan:

```markdown
## 📋 Achievement Index

**All Achievements in This Plan**:

**Priority 0: IMMEDIATE IMPACT (COMPLETE ✅)**

- ✅ Achievement 0.1: First Achievement
- ✅ Achievement 0.2: Second Achievement
- ✅ Achievement 0.3: Third Achievement

**Priority 1: FOUNDATION**

- Achievement 1.1: Fourth Achievement
- Achievement 1.2: Fifth Achievement
```

**Purpose**:

- Quick reference for all achievements in the plan
- Enables scripts to detect all achievements without parsing full PLAN
- Shows progress at a glance
- Helps detect completion via feedback files

**Location**: Near the top of PLAN file (after header, before detailed sections)

### 2. APPROVED Files

**APPROVED files** are the single source of truth for achievement completion. They live in `execution/feedbacks/` and follow a strict naming convention:

**Format**: `APPROVED_XX.md` where XX is the achievement number without the dot

**Examples**:

- Achievement 0.1 → `APPROVED_01.md`
- Achievement 1.1 → `APPROVED_11.md`
- Achievement 2.4 → `APPROVED_24.md`

**Location**: `work-space/plans/FEATURE-NAME/execution/feedbacks/APPROVED_XX.md`

**Content** (standard template):

```markdown
# APPROVED: Achievement X.X

**Achievement**: X.X  
**Date**: YYYY-MM-DD  
**Status**: ✅ Approved

---

## ✅ Approval

[Reviewer notes and approval details]

---

**Reviewer**: [Name]  
**Approved**: YYYY-MM-DD
```

### 3. FIX Files & Tri-State Model

**NEW in Achievement 2.9**: The feedback system now supports a **tri-state model** to handle achievements that need fixes before approval.

**Three States**:

1. **"approved"** - `APPROVED_XX.md` exists → Achievement complete, move to next
2. **"needs_fix"** - `FIX_XX.md` exists (no APPROVED) → Fixes required, generate FIX prompt
3. **"incomplete"** - Neither exists → Work in progress, generate standard prompt

**FIX Files** track reviewer feedback requiring fixes before approval:

**Format**: `FIX_XX.md` where XX is the achievement number without the dot

**Examples**:

- Achievement 2.1 → `FIX_21.md`
- Achievement 1.5 → `FIX_15.md`

**Location**: `work-space/plans/FEATURE-NAME/execution/feedbacks/FIX_XX.md`

**Content** (standard template):

```markdown
# FIX REQUIRED: Achievement X.X

**Reviewer**: [Name]
**Review Date**: YYYY-MM-DD
**Status**: ⚠️ NEEDS FIXES

---

## Summary

[Brief summary of what needs to be fixed]

---

## Issues Found

### Critical Issues (must fix)

#### 1. **ISSUE TITLE** ⚠️ BLOCKER

**Issue**: [Description]

**Evidence**:

- [Point 1]
- [Point 2]

**Impact**: [Why this matters]

**Fix Required**:

1. [Action 1]
2. [Action 2]

---

#### 2. **ANOTHER ISSUE**

[... more issues ...]

---

### Minor Issues (nice to fix)

- [Issue 1]
- [Issue 2]

---

## What Worked Well

- [Positive feedback 1]
- [Positive feedback 2]
```

**Workflow**:

1. **Reviewer creates FIX_XX.md** with detailed issues
2. **System detects FIX file** (via `get_achievement_status()`)
3. **FIX-specific prompt generated** with issues, code references, and action plan
4. **Executor addresses fixes** and creates `FIX_XX_RESOLUTION.md`
5. **Reviewer reviews resolution**, creates `APPROVED_XX.md` if satisfied

**Priority**: If both `APPROVED_XX.md` and `FIX_XX.md` exist, APPROVED takes priority (status = "approved").

**Code References in FIX Files**:

FIX files can include code references using the `@FileType (start-end)` pattern:

```markdown
See @Python (779-1075) for the bug.
Also review @TypeScript (45-120) for similar pattern.
```

The FIX prompt generator extracts these references automatically.

### 4. Filesystem-First Detection

The system uses **filesystem-first** detection for achievement status:

**Tri-State Detection** (NEW in Achievement 2.9):

```python
def get_achievement_status(ach_num: str, plan_path: Path) -> str:
    """
    Get achievement status from filesystem (tri-state model).

    Returns:
        "approved"    - APPROVED_XX.md exists
        "needs_fix"   - FIX_XX.md exists (no APPROVED)
        "incomplete"  - Neither exists
    """
    feedbacks_dir = plan_path.parent / "execution" / "feedbacks"
    approved_file = feedbacks_dir / f"APPROVED_{ach_num.replace('.', '')}.md"
    fix_file = feedbacks_dir / f"FIX_{ach_num.replace('.', '')}.md"

    if approved_file.exists():
        return "approved"
    elif fix_file.exists():
        return "needs_fix"
    else:
        return "incomplete"
```

**Backward Compatibility**:

```python
def is_achievement_complete(ach_num: str, plan_content: str, plan_path: Path) -> bool:
    """Legacy binary check - wraps get_achievement_status()."""
    status = get_achievement_status(ach_num, plan_path)
    return status == "approved"  # True only if approved
```

**No fallback** to PLAN markdown! If the feedback files don't exist, status is determined purely by filesystem state.

---

## 📁 Directory Structure

```
work-space/plans/FEATURE-NAME/
├── PLAN_FEATURE-NAME.md              # Defines achievements (Index)
├── execution/
│   ├── feedbacks/                     # ← Feedback files live here
│   │   ├── APPROVED_01.md            # Achievement 0.1 complete ✅
│   │   ├── FIX_21.md                 # Achievement 2.1 needs fixes ⚠️
│   │   ├── FIX_21_RESOLUTION.md      # Resolution for review
│   │   └── APPROVED_24.md            # Achievement 2.4 complete ✅
│   ├── EXECUTION_TASK_*.md           # Execution tasks
│   └── ...
├── subplans/
│   └── SUBPLAN_*.md                  # Subplans
└── documentation/
    └── ...                            # Migration notes, etc.
```

---

## ✅ Conventions

### Naming Conventions

**MUST**:

- ✅ Use `APPROVED_XX.md` format (uppercase APPROVED, underscore, no dot in number)
- ✅ Use two digits for achievement number (01, 11, 24, not 1, 1.1, 2.4)

**MUST NOT**:

- ❌ Use lowercase (`approved_11.md`)
- ❌ Use dots (`APPROVED_1.1.md`)
- ❌ Use wrong separators (`APPROVED-11.md`)
- ❌ Use different extensions (`APPROVED_11.txt`)

### Location Conventions

**MUST**:

- ✅ Files in `execution/feedbacks/` directory
- ✅ One file per completed achievement

**MUST NOT**:

- ❌ Files in PLAN root directory
- ❌ Files in `execution/` (without feedbacks/ subdirectory)
- ❌ Files anywhere else

### Content Conventions

**MUST**:

- ✅ Include achievement number in title
- ✅ Include approval date
- ✅ Include reviewer name (can be "LLM Executor" or human name)

**RECOMMENDED**:

- ✅ Include approval reasoning or notes
- ✅ Link to related EXECUTION_TASK or SUBPLAN
- ✅ Note any caveats or follow-up items

---

## 🔍 Validation

Use the validation script to check feedback system conventions:

```bash
# Validate a single plan
python3 LLM/scripts/validation/validate_feedback_system.py work-space/plans/FEATURE/

# Validate all plans
for plan in work-space/plans/*/; do
    python3 LLM/scripts/validation/validate_feedback_system.py "$plan"
done
```

**What it checks**:

1. Naming conventions (APPROVED_XX.md format)
2. File locations (execution/feedbacks/)
3. Achievement Index alignment (Index matches filesystem)
4. No orphaned files (APPROVED for non-existent achievement)
5. No gaps (SUBPLANs/EXECUTIONs match Index)

**Example output**:

```
✅ VALIDATION PASSED

📊 SUMMARY:
   Total Issues: 10
   Errors:       0
   Warnings:     0
   Info:         10

ℹ️ INFOS (10):
  • Achievement 2.5 in Index but not complete (no APPROVED file)
    Resolution: This is OK if achievement is still in progress
```

---

## 🔄 Migration

Use the migration script to migrate legacy plans to feedback system:

```bash
# Dry-run (safe, shows what would be done)
python3 LLM/scripts/migration/migrate_legacy_completions.py work-space/plans/LEGACY-PLAN/

# Actually apply migration
python3 LLM/scripts/migration/migrate_legacy_completions.py work-space/plans/LEGACY-PLAN/ --apply
```

**What it does**:

1. Detects completed achievements from PLAN markdown (✅ markers)
2. Creates `execution/feedbacks/` structure if missing
3. Generates `APPROVED_XX.md` files for completed achievements
4. Validates result

**Safe by default**: Always runs in dry-run mode unless `--apply` flag is used.

---

## 💡 Examples

### Example 1: Complete Achievement

**Before** (achievement just completed):

```
work-space/plans/FEATURE/
└── execution/
    └── feedbacks/
        └── (empty)
```

**After** (achievement approved):

```
work-space/plans/FEATURE/
└── execution/
    └── feedbacks/
        └── APPROVED_11.md    # ← New file created
```

**APPROVED_11.md content**:

```markdown
# APPROVED: Achievement 1.1

**Achievement**: 1.1  
**Date**: 2025-11-12  
**Status**: ✅ Approved

---

## ✅ Approval

Achievement 1.1 has been completed successfully:

- All deliverables created
- Tests passing
- Documentation complete

Quality is high, ready for production.

---

**Reviewer**: LLM Executor  
**Approved**: 2025-11-12
```

### Example 2: Check Achievement Status

**In code**:

```python
from pathlib import Path

def is_achievement_complete(ach_num: str, plan_path: Path) -> bool:
    feedbacks_dir = plan_path.parent / "execution" / "feedbacks"
    approved_file = feedbacks_dir / f"APPROVED_{ach_num.replace('.', '')}.md"
    return approved_file.exists()

# Check if Achievement 1.1 is complete
plan_path = Path("work-space/plans/FEATURE/PLAN_FEATURE.md")
if is_achievement_complete("1.1", plan_path):
    print("✅ Achievement 1.1 is complete")
else:
    print("⏳ Achievement 1.1 is in progress")
```

---

## 🔗 Related Documentation

- **Troubleshooting**: See `FEEDBACK_SYSTEM_TROUBLESHOOTING.md` for common issues
- **Methodology**: See `LLM-METHODOLOGY.md` for integration with LLM workflow
- **Templates**: See `LLM/templates/PLAN-TEMPLATE.md` for Achievement Index examples
- **Philosophy**: See `LLM/docs/STATE_TRACKING_PHILOSOPHY.md` for filesystem-first rationale

---

## ❓ FAQ

**Q: Why not mark achievements complete in the PLAN markdown?**  
A: PLAN markdown gets out of sync easily. Filesystem is the single source of truth.

**Q: Can I have multiple APPROVED files for the same achievement?**  
A: No. One achievement = one APPROVED file.

**Q: What if I delete an APPROVED file by accident?**  
A: The system will consider that achievement incomplete. Recreate the file or restore from git.

**Q: Can I use a different naming format?**  
A: No. The format is part of the convention. Scripts depend on it.

**Q: Do I need an Achievement Index?**  
A: Yes. The Index is how scripts know what achievements exist in a PLAN.

**Q: Can I put APPROVED files in a different location?**  
A: No. The location is part of the convention: `execution/feedbacks/`

---

**Last Updated**: 2025-11-12  
**Maintained by**: Achievement 2.5 - Codify Feedback System Patterns
