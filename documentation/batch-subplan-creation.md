# Batch SUBPLAN Creation

**Achievement**: 2.2 - Batch SUBPLAN Creation Implemented  
**Created**: 2025-11-14  
**Status**: ✅ Complete

---

## 📋 Overview

Batch SUBPLAN creation enables you to create multiple SUBPLAN files at once for achievements at the same dependency level. This feature significantly speeds up the workflow when working with parallel execution plans, allowing you to prepare multiple achievements for simultaneous execution.

### Key Features

- **Batch Creation**: Create multiple SUBPLANs at once using `--batch` flag
- **Dependency Level Filtering**: Automatically groups achievements by dependency level (0, 1, 2, etc.)
- **Smart Detection**: Only creates SUBPLANs that don't already exist (no overwrites)
- **Dry-Run Mode**: Preview what would be created without creating files
- **Safety Features**: Confirmation prompts, rollback strategy, partial success handling
- **Menu Integration**: Access from parallel execution menu (option 1)

---

## 🚀 Usage

### CLI Usage

#### Basic Batch Creation

```bash
# Batch create SUBPLANs for a plan
python LLM/scripts/generation/generate_subplan_prompt.py --batch @PLAN_MY-PLAN.md

# This will:
# 1. Load parallel.json from plan directory
# 2. Filter level 0 achievements (no dependencies)
# 3. Detect missing SUBPLANs
# 4. Show preview
# 5. Ask for confirmation
# 6. Create SUBPLANs
```

#### Dry-Run Mode (Preview Only)

```bash
# Preview what would be created without creating files
python LLM/scripts/generation/generate_subplan_prompt.py --batch --dry-run @PLAN_MY-PLAN.md

# This will:
# 1. Show preview of what would be created
# 2. Exit without creating files
```

### Menu Usage

Access batch SUBPLAN creation from the parallel execution menu:

```bash
# Run generate_prompt.py in interactive mode
python LLM/scripts/generation/generate_prompt.py @PLAN_MY-PLAN.md --interactive

# When prompted, access the Parallel Execution Menu
# Select option 1: Batch Create SUBPLANs
```

---

## 📊 How It Works

### Dependency Level Algorithm

Achievements are grouped by dependency level:

- **Level 0**: No dependencies (can run immediately)
- **Level 1**: Depends only on level 0 achievements
- **Level 2**: Depends on level 1 achievements
- **Level N**: Depends on level N-1 achievements

**Algorithm**:

```
level(achievement) =
    if no dependencies: 0
    else: max(level(dependency) for each dependency) + 1
```

**Example**:

```json
{
  "achievements": [
    { "achievement_id": "1.1", "dependencies": [] }, // Level 0
    { "achievement_id": "1.2", "dependencies": [] }, // Level 0
    { "achievement_id": "1.3", "dependencies": ["1.1"] }, // Level 1
    { "achievement_id": "2.1", "dependencies": ["1.1", "1.2"] }, // Level 1
    { "achievement_id": "2.2", "dependencies": ["1.3", "2.1"] } // Level 2
  ]
}
```

### Workflow

1. **Load parallel.json**

   - Reads `parallel.json` from plan directory
   - Validates JSON structure
   - Extracts achievements list

2. **Filter by Dependency Level**

   - Calculates dependency level for each achievement
   - Filters achievements at level 0 (default)
   - Uses memoization for efficiency

3. **Detect Missing SUBPLANs**

   - Checks for existing SUBPLAN files
   - Uses naming convention: `SUBPLAN_{PLAN_NAME}_{ACHIEVEMENT_ID}.md`
   - Returns list of missing SUBPLANs

4. **Show Preview**

   - Displays plan name
   - Lists achievements to be created
   - Shows SUBPLAN filenames

5. **Confirm Creation**

   - Asks user: "Proceed with batch creation? (y/N)"
   - Defaults to "No" for safety
   - Can be skipped in dry-run mode

6. **Create SUBPLANs**
   - Creates placeholder SUBPLAN files
   - Tracks created, skipped, and errors
   - Shows summary result

### SUBPLAN File Naming

```
SUBPLAN_{PLAN_NAME}_{ACHIEVEMENT_ID}.md

Examples:
- Achievement 1.1 → SUBPLAN_MY-PLAN_11.md
- Achievement 1.2 → SUBPLAN_MY-PLAN_12.md
- Achievement 2.1 → SUBPLAN_MY-PLAN_21.md
```

---

## 🔒 Safety Features

### 1. Dry-Run Mode

Preview what would be created without creating files:

```bash
python LLM/scripts/generation/generate_subplan_prompt.py --batch --dry-run @PLAN_MY-PLAN.md
```

**Output**:

```
📋 Batch SUBPLAN Creation Preview
================================================================================
Plan: MY-PLAN
Achievements to create: 3

SUBPLANs that will be created:
  1. Achievement 1.1 - SUBPLAN_MY-PLAN_11.md
  2. Achievement 1.2 - SUBPLAN_MY-PLAN_12.md
  3. Achievement 1.3 - SUBPLAN_MY-PLAN_13.md
================================================================================

🔍 DRY-RUN MODE: No files created
```

### 2. Confirmation Prompt

User must explicitly confirm before files are created:

```
Proceed with batch creation of 3 SUBPLANs? (y/N):
```

- Defaults to "No" for safety
- Type "y" or "yes" to proceed
- Any other input cancels

### 3. Skip Existing SUBPLANs

Batch creation never overwrites existing SUBPLANs:

```
✅ Created 2 SUBPLANs:
  - SUBPLAN_MY-PLAN_12.md
  - SUBPLAN_MY-PLAN_13.md

⏭️  Skipped 1 (already exist):
  - Achievement 1.1
```

### 4. Rollback Strategy

For git-based rollback (if needed):

```python
from LLM.scripts.generation.batch_rollback import (
    create_rollback_point,
    rollback_to_point
)

# Create rollback point before batch operation
commit_sha = create_rollback_point(plan_path)

try:
    # Perform batch operation
    result = batch_create_subplans(plan_path)
except Exception as e:
    # Rollback on error
    if commit_sha:
        rollback_to_point(commit_sha, plan_path)
```

### 5. Partial Success Handling

If some SUBPLANs fail to create, successful ones are kept:

```
✅ Created 2 SUBPLANs:
  - SUBPLAN_MY-PLAN_11.md
  - SUBPLAN_MY-PLAN_12.md

❌ Errors (1):
  - Achievement 1.3: Invalid achievement format
```

---

## 📝 Examples

### Example 1: Basic Batch Creation

```bash
$ python LLM/scripts/generation/generate_subplan_prompt.py --batch @PLAN_PARALLEL-EXECUTION-AUTOMATION.md

================================================================================
📋 Batch SUBPLAN Creation Preview
================================================================================
Plan: PARALLEL-EXECUTION-AUTOMATION
Achievements to create: 3

SUBPLANs that will be created:
  1. Achievement 1.1 - SUBPLAN_PARALLEL-EXECUTION-AUTOMATION_11.md
  2. Achievement 1.2 - SUBPLAN_PARALLEL-EXECUTION-AUTOMATION_12.md
  3. Achievement 1.3 - SUBPLAN_PARALLEL-EXECUTION-AUTOMATION_13.md
================================================================================

Proceed with batch creation of 3 SUBPLANs? (y/N): y

🔨 Creating SUBPLANs...
  ✅ Created: SUBPLAN_PARALLEL-EXECUTION-AUTOMATION_11.md
  ✅ Created: SUBPLAN_PARALLEL-EXECUTION-AUTOMATION_12.md
  ✅ Created: SUBPLAN_PARALLEL-EXECUTION-AUTOMATION_13.md

================================================================================
✅ Created 3 SUBPLANs:
  - SUBPLAN_PARALLEL-EXECUTION-AUTOMATION_11.md
  - SUBPLAN_PARALLEL-EXECUTION-AUTOMATION_12.md
  - SUBPLAN_PARALLEL-EXECUTION-AUTOMATION_13.md
================================================================================
```

### Example 2: Dry-Run Mode

```bash
$ python LLM/scripts/generation/generate_subplan_prompt.py --batch --dry-run @PLAN_MY-PLAN.md

================================================================================
📋 Batch SUBPLAN Creation Preview
================================================================================
Plan: MY-PLAN
Achievements to create: 2

SUBPLANs that will be created:
  1. Achievement 1.1 - SUBPLAN_MY-PLAN_11.md
  2. Achievement 1.2 - SUBPLAN_MY-PLAN_12.md
================================================================================

🔍 DRY-RUN MODE: No files created
```

### Example 3: Skip Existing SUBPLANs

```bash
$ python LLM/scripts/generation/generate_subplan_prompt.py --batch @PLAN_MY-PLAN.md

# SUBPLAN_MY-PLAN_11.md already exists

================================================================================
📋 Batch SUBPLAN Creation Preview
================================================================================
Plan: MY-PLAN
Achievements to create: 1

SUBPLANs that will be created:
  1. Achievement 1.2 - SUBPLAN_MY-PLAN_12.md
================================================================================

Proceed with batch creation of 1 SUBPLANs? (y/N): y

🔨 Creating SUBPLANs...
  ✅ Created: SUBPLAN_MY-PLAN_12.md

================================================================================
✅ Created 1 SUBPLANs:
  - SUBPLAN_MY-PLAN_12.md

⏭️  Skipped 1 (already exist):
  - Achievement 1.1
================================================================================
```

---

## 🐛 Troubleshooting

### Error: parallel.json not found

**Problem**: No `parallel.json` file in plan directory

**Solution**:

```bash
# Generate parallel.json first
python LLM/scripts/generation/generate_prompt.py @PLAN_MY-PLAN.md --parallel-upgrade
```

### Error: Invalid JSON in parallel.json

**Problem**: `parallel.json` has syntax errors

**Solution**:

1. Validate JSON: `cat parallel.json | python -m json.tool`
2. Fix syntax errors
3. Or regenerate: `python LLM/scripts/generation/generate_prompt.py @PLAN_MY-PLAN.md --parallel-upgrade`

### Error: No achievements at level 0

**Problem**: All achievements have dependencies (none at level 0)

**Solution**:

- This is expected if you've already created level 0 SUBPLANs
- Check `parallel.json` to verify dependency structure
- Level 0 achievements are those with `"dependencies": []`

### All SUBPLANs already exist

**Problem**: All level 0 SUBPLANs have already been created

**Solution**:

- This is expected behavior (batch creation is idempotent)
- To create level 1 SUBPLANs, modify the code to filter by `level=1`
- Or use single SUBPLAN creation: `generate_subplan_prompt.py create @PLAN_MY-PLAN.md --achievement 2.1`

---

## 🔗 Related Documentation

- **Parallel Execution Schema**: `documentation/parallel-schema-documentation.md`
- **Parallel Status Transitions**: `documentation/parallel-status-transitions.md`
- **Parallel Validation Errors**: `documentation/parallel-validation-errors.md`
- **SUBPLAN Workflow Guide**: `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md`
- **SUBPLAN Template**: `LLM/templates/SUBPLAN-TEMPLATE.md`

---

## 📚 API Reference

### `batch_create_subplans()`

```python
def batch_create_subplans(
    plan_path: Path,
    dry_run: bool = False,
    parallel_json_path: Optional[Path] = None
) -> BatchResult:
    """
    Batch create SUBPLANs for achievements in parallel.json.

    Args:
        plan_path: Path to PLAN directory or file
        dry_run: If True, preview without creating files
        parallel_json_path: Optional path to parallel.json (auto-detect if None)

    Returns:
        BatchResult with created SUBPLANs, skipped, and errors
    """
```

### `filter_by_dependency_level()`

```python
def filter_by_dependency_level(
    achievements: List[Dict],
    level: int = 0
) -> List[Dict]:
    """
    Filter achievements by dependency level.

    Args:
        achievements: List of achievement dicts from parallel.json
        level: Dependency level to filter (default: 0)

    Returns:
        List of achievements at specified level
    """
```

### `detect_missing_subplans()`

```python
def detect_missing_subplans(
    plan_path: Path,
    achievements: List[Dict]
) -> List[Dict]:
    """
    Detect which achievements are missing SUBPLANs.

    Args:
        plan_path: Path to PLAN directory or file
        achievements: List of achievement dicts

    Returns:
        List of achievements without SUBPLANs
    """
```

### `BatchResult`

```python
@dataclass
class BatchResult:
    """Result of batch SUBPLAN creation."""
    created: List[Path]  # Successfully created SUBPLANs
    skipped: List[str]   # Achievements skipped (already exist)
    errors: List[Tuple[str, str]]  # (achievement_id, error_msg)
```

---

## 🎯 Best Practices

1. **Always Use Dry-Run First**

   ```bash
   # Preview before creating
   python LLM/scripts/generation/generate_subplan_prompt.py --batch --dry-run @PLAN_MY-PLAN.md
   ```

2. **Create Level by Level**

   - Start with level 0 (no dependencies)
   - Complete level 0 before moving to level 1
   - This ensures dependencies are satisfied

3. **Review parallel.json Before Batch Creation**

   - Verify dependency structure is correct
   - Check for circular dependencies
   - Validate with: `python LLM/scripts/validation/validate_parallel_json.py parallel.json`

4. **Use Confirmation Prompts**

   - Don't skip confirmation (it's there for safety)
   - Review the preview before confirming
   - Cancel if something looks wrong

5. **Check for Existing SUBPLANs**
   - Batch creation skips existing SUBPLANs
   - This is idempotent (safe to run multiple times)
   - Check `subplans/` directory before running

---

**Achievement 2.2**: ✅ Complete  
**Next**: Achievement 2.3 - Batch EXECUTION Creation Implemented
