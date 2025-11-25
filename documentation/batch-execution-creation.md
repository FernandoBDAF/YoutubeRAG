# Batch EXECUTION Creation

**Achievement**: 2.3 - Batch EXECUTION Creation Implemented  
**Created**: 2025-11-14  
**Status**: ✅ Complete

---

## 📋 Overview

Batch EXECUTION creation enables you to create multiple EXECUTION_TASK files at once for achievements at the same dependency level. This feature includes **prerequisite validation** to ensure all SUBPLANs exist before creating EXECUTION_TASKs, preventing invalid workflow states.

### Key Features

- **Batch Creation**: Create multiple EXECUTION_TASKs at once using `--batch` flag
- **Prerequisite Validation**: Validates all SUBPLANs exist before creating EXECUTIONs (blocks creation if missing)
- **Smart Detection**: Only creates EXECUTION_TASKs that don't already exist (no overwrites)
- **Dry-Run Mode**: Preview what would be created without creating files
- **Safety Features**: Confirmation prompts, rollback strategy, partial success handling
- **Menu Integration**: Access from parallel execution menu (option 2)

---

## 🚀 Usage

### CLI Usage

#### Basic Batch Creation

```bash
# Batch create EXECUTION_TASKs for a plan
python LLM/scripts/generation/generate_execution_prompt.py --batch @PLAN_MY-PLAN.md

# This will:
# 1. Load parallel.json from plan directory
# 2. Filter level 0 achievements (no dependencies)
# 3. Validate all SUBPLANs exist (CRITICAL PREREQUISITE)
# 4. Detect missing EXECUTION_TASKs
# 5. Show preview
# 6. Ask for confirmation
# 7. Create EXECUTION_TASKs
```

#### Dry-Run Mode (Preview Only)

```bash
# Preview what would be created without creating files
python LLM/scripts/generation/generate_execution_prompt.py --batch --dry-run @PLAN_MY-PLAN.md
```

### Menu Usage

Access batch EXECUTION creation from the parallel execution menu:

```bash
# Run generate_prompt.py in interactive mode
python LLM/scripts/generation/generate_prompt.py @PLAN_MY-PLAN.md --interactive

# When prompted, access the Parallel Execution Menu
# Select option 2: Batch Create EXECUTIONs
```

---

## 🔒 Prerequisite Validation

**CRITICAL**: EXECUTION_TASKs require SUBPLANs to exist because they reference SUBPLAN context (objective, approach, etc.).

### How It Works

1. **Check**: For each achievement, check if SUBPLAN file exists
2. **Block**: If any SUBPLANs missing, block EXECUTION creation entirely
3. **Guide**: Show clear error message with list of missing SUBPLANs
4. **Suggest**: Recommend using option 1 to create SUBPLANs first

### Example Output

```
⚠️  Missing 2 SUBPLANs (create these first):
  - Achievement 1.1
  - Achievement 1.2

💡 Tip: Use option 1 to batch create SUBPLANs first
```

---

## 📝 Examples

### Example 1: Basic Batch Creation

```bash
$ python LLM/scripts/generation/generate_execution_prompt.py --batch @PLAN_MY-PLAN.md

================================================================================
📋 Batch EXECUTION Creation Preview
================================================================================
Plan: MY-PLAN
Achievements to create: 3

EXECUTION_TASKs that will be created:
  1. Achievement 1.1 - EXECUTION_TASK_MY-PLAN_11_01.md
  2. Achievement 1.2 - EXECUTION_TASK_MY-PLAN_12_01.md
  3. Achievement 1.3 - EXECUTION_TASK_MY-PLAN_13_01.md
================================================================================

Proceed with batch creation of 3 EXECUTION_TASKs? (y/N): y

🔨 Creating EXECUTION_TASKs...
  ✅ Created: EXECUTION_TASK_MY-PLAN_11_01.md
  ✅ Created: EXECUTION_TASK_MY-PLAN_12_01.md
  ✅ Created: EXECUTION_TASK_MY-PLAN_13_01.md

================================================================================
✅ Created 3 EXECUTION_TASKs:
  - EXECUTION_TASK_MY-PLAN_11_01.md
  - EXECUTION_TASK_MY-PLAN_12_01.md
  - EXECUTION_TASK_MY-PLAN_13_01.md
================================================================================
```

### Example 2: Missing SUBPLANs (Blocked)

```bash
$ python LLM/scripts/generation/generate_execution_prompt.py --batch @PLAN_MY-PLAN.md

⚠️  Missing 2 SUBPLANs (create these first):
  - Achievement 1.1
  - Achievement 1.2

💡 Tip: Use option 1 to batch create SUBPLANs first

================================================================================
⚠️  Missing 2 SUBPLANs (create these first):
  - Achievement 1.1
  - Achievement 1.2
================================================================================
```

---

## 🐛 Troubleshooting

### Error: Missing SUBPLANs

**Problem**: EXECUTION creation blocked due to missing SUBPLANs

**Solution**:

```bash
# Create SUBPLANs first using option 1 or --batch flag
python LLM/scripts/generation/generate_subplan_prompt.py --batch @PLAN_MY-PLAN.md

# Then create EXECUTIONs
python LLM/scripts/generation/generate_execution_prompt.py --batch @PLAN_MY-PLAN.md
```

### Error: parallel.json not found

**Problem**: No `parallel.json` file in plan directory

**Solution**:

```bash
# Generate parallel.json first
python LLM/scripts/generation/generate_prompt.py @PLAN_MY-PLAN.md --parallel-upgrade
```

### All EXECUTION_TASKs already exist

**Problem**: All level 0 EXECUTION_TASKs have already been created

**Solution**:

- This is expected behavior (batch creation is idempotent)
- To create level 1 EXECUTION_TASKs, modify the code to filter by `level=1`
- Or use single EXECUTION creation: `generate_execution_prompt.py create @SUBPLAN_MY-PLAN_21.md --execution 01`

---

## 🔗 Related Documentation

- **Batch SUBPLAN Creation**: `documentation/batch-subplan-creation.md`
- **Parallel Execution Schema**: `documentation/parallel-schema-documentation.md`
- **Parallel Status Transitions**: `documentation/parallel-status-transitions.md`
- **Parallel Validation Errors**: `documentation/parallel-validation-errors.md`

---

## 📚 API Reference

### `batch_create_executions()`

```python
def batch_create_executions(
    plan_path: Path,
    dry_run: bool = False,
    parallel_json_path: Optional[Path] = None
) -> BatchResult:
    """
    Batch create EXECUTION_TASKs for achievements in parallel.json.

    Args:
        plan_path: Path to PLAN directory or file
        dry_run: If True, preview without creating files
        parallel_json_path: Optional path to parallel.json (auto-detect if None)

    Returns:
        BatchResult with created EXECUTIONs, skipped, errors, and missing SUBPLANs
    """
```

### `validate_subplan_prerequisites()`

```python
def validate_subplan_prerequisites(
    plan_path: Path,
    achievements: List[Dict]
) -> Tuple[List[Dict], List[str]]:
    """
    Validate that all SUBPLANs exist for achievements.

    Args:
        plan_path: Path to PLAN directory
        achievements: List of achievement dicts

    Returns:
        Tuple of (valid_achievements, missing_subplan_ids)
    """
```

### `BatchResult`

```python
@dataclass
class BatchResult:
    """Result of batch EXECUTION creation."""
    created: List[Path]  # Successfully created EXECUTION_TASKs
    skipped: List[str]   # Achievements skipped (already exist)
    errors: List[Tuple[str, str]]  # (achievement_id, error_msg)
    missing_subplans: List[str]  # SUBPLANs that must be created first (NEW)
```

---

## 🎯 Best Practices

1. **Always Create SUBPLANs First**

   ```bash
   # Step 1: Create SUBPLANs
   python LLM/scripts/generation/generate_subplan_prompt.py --batch @PLAN_MY-PLAN.md

   # Step 2: Create EXECUTION_TASKs
   python LLM/scripts/generation/generate_execution_prompt.py --batch @PLAN_MY-PLAN.md
   ```

2. **Use Dry-Run First**

   ```bash
   # Preview before creating
   python LLM/scripts/generation/generate_execution_prompt.py --batch --dry-run @PLAN_MY-PLAN.md
   ```

3. **Create Level by Level**

   - Start with level 0 (no dependencies)
   - Complete level 0 before moving to level 1
   - This ensures dependencies are satisfied

4. **Review parallel.json Before Batch Creation**

   - Verify dependency structure is correct
   - Check for circular dependencies
   - Validate with: `python LLM/scripts/validation/validate_parallel_json.py parallel.json`

5. **Use Confirmation Prompts**
   - Don't skip confirmation (it's there for safety)
   - Review the preview before confirming
   - Cancel if something looks wrong

---

**Achievement 2.3**: ✅ Complete  
**Next**: Achievement 3.1 - Parallel Execution Coordination
