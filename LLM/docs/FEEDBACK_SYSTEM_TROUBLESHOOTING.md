# Feedback System Troubleshooting Guide

**Purpose**: Solutions for common feedback system issues  
**Audience**: LLM executors, reviewers encountering problems  
**Created**: 2025-11-12  
**Achievement**: 2.5 - Codify Feedback System Patterns

---

## 🚨 Common Issues & Solutions

### Issue 1: Achievement Marked Complete But No APPROVED File

**Symptoms**:

- Achievement shows ✅ in PLAN markdown
- `is_achievement_complete()` returns False
- Scripts don't detect achievement as complete

**Root Cause**: PLAN markdown updated but APPROVED file not created

**Solution**:

```bash
# Create the missing APPROVED file
mkdir -p work-space/plans/FEATURE/execution/feedbacks/
# For Achievement X.Y, create APPROVED_XY.md
echo "# APPROVED: Achievement X.Y" > work-space/plans/FEATURE/execution/feedbacks/APPROVED_XY.md
```

**Prevention**: Always create APPROVED file when completing achievements

---

### Issue 2: APPROVED File Exists But Achievement Not in Index

**Symptoms**:

- Validation script reports "orphan" file
- APPROVED file exists in feedbacks/
- Achievement not listed in Achievement Index

**Root Cause**: Achievement was completed but not added to Index, or Index is outdated

**Solution**:

1. Verify achievement should exist
2. Add to Achievement Index in PLAN:

```markdown
## 📋 Achievement Index

- Achievement X.Y: Description
```

3. Run validation to confirm

**Prevention**: Maintain Achievement Index as achievements are added

---

### Issue 3: Wrong Naming Convention

**Symptoms**:

- Validation script reports naming error
- File named `approved_11.md` or `APPROVED_1.1.md` or `APPROVED-11.md`

**Root Cause**: Incorrect naming format used

**Solution**:

```bash
# Rename to correct format
cd work-space/plans/FEATURE/execution/feedbacks/
mv approved_11.md APPROVED_11.md       # Fix lowercase
mv APPROVED_1.1.md APPROVED_11.md      # Fix dot in number
mv APPROVED-11.md APPROVED_11.md       # Fix hyphen
```

**Correct Format**: `APPROVED_XX.md` (uppercase, underscore, no dot)

**Prevention**: Use script or template to create APPROVED files

---

### Issue 4: APPROVED File in Wrong Location

**Symptoms**:

- Validation script reports location error
- File exists but not detected by scripts
- File in PLAN root or execution/ (not execution/feedbacks/)

**Root Cause**: File created in wrong directory

**Solution**:

```bash
# Move to correct location
mkdir -p work-space/plans/FEATURE/execution/feedbacks/
mv work-space/plans/FEATURE/APPROVED_11.md \
   work-space/plans/FEATURE/execution/feedbacks/APPROVED_11.md
```

**Correct Location**: `work-space/plans/FEATURE/execution/feedbacks/APPROVED_XX.md`

**Prevention**: Always create in `execution/feedbacks/` directory

---

### Issue 5: Orphaned SUBPLAN or EXECUTION (Not in Index)

**Symptoms**:

- Validation detects SUBPLAN/EXECUTION files
- Corresponding achievement not in Index
- Unclear which achievement they belong to

**Root Cause**: Files created but achievement not added to Index

**Solution**:

1. Find corresponding achievement in SUBPLAN/EXECUTION filename
2. Add to Achievement Index:

```markdown
## 📋 Achievement Index

- Achievement X.Y: [Description from SUBPLAN]
```

**Prevention**: Add achievement to Index before creating SUBPLAN/EXECUTION

---

### Issue 6: Index Out of Sync with Filesystem

**Symptoms**:

- Multiple info messages from validation
- Achievements in Index but no APPROVED files
- Or APPROVED files but not in Index

**Root Cause**: Index and filesystem diverged over time

**Solution**:

```bash
# Step 1: Run validation to see discrepancies
python3 LLM/scripts/validation/validate_feedback_system.py work-space/plans/FEATURE/

# Step 2: For each mismatch, decide:
# - Is achievement actually complete? Create APPROVED file
# - Is achievement not started yet? Leave as-is (info only)
# - Is APPROVED file orphaned? Add to Index or remove file
```

**Prevention**: Keep Index and filesystem in sync as work progresses

---

## 🔧 Quick Fixes

### Create Missing Feedback Structure

```bash
# If execution/feedbacks/ doesn't exist:
mkdir -p work-space/plans/FEATURE/execution/feedbacks/
```

### Validate After Changes

```bash
# Always validate after fixing issues:
python3 LLM/scripts/validation/validate_feedback_system.py work-space/plans/FEATURE/
```

### Migrate Legacy Plan

```bash
# For old plans without feedback system:
python3 LLM/scripts/migration/migrate_legacy_completions.py work-space/plans/FEATURE/
# Review dry-run output, then:
python3 LLM/scripts/migration/migrate_legacy_completions.py work-space/plans/FEATURE/ --apply
```

---

## 📚 Related Documentation

- **Main Guide**: See `FEEDBACK_SYSTEM_GUIDE.md` for full conventions
- **Validation**: See `LLM/scripts/validation/validate_feedback_system.py`
- **Migration**: See `LLM/scripts/migration/migrate_legacy_completions.py`

---

## 💡 Best Practices

1. **Always validate** before and after making changes
2. **Use scripts** to create APPROVED files (less error-prone)
3. **Keep Index updated** as achievements are added
4. **Never manually edit** achievement numbers in filenames
5. **Use dry-run** mode for migration before applying

---

**Last Updated**: 2025-11-12  
**Maintained by**: Achievement 2.5 - Codify Feedback System Patterns
