# SUBPLAN: Manual Archive Script Creation

**Type**: SUBPLAN  
**Mother Plan**: PLAN_FILE-MOVING-WORKSPACE-AND-MANUAL-ARCHIVE.md  
**Plan**: FILE-MOVING-WORKSPACE-AND-MANUAL-ARCHIVE  
**Achievement Addressed**: Achievement 0.2 (Manual Archive Script Creation)  
**Achievement**: 0.2  
**Status**: In Progress  
**Created**: 2025-01-28 00:05 UTC  
**Estimated Effort**: 2-3 hours

**Metadata Tags**: See `LLM/guides/METADATA-TAGS.md` for virtual organization system

---

## 🎯 Objective

Create a manual archive script (`LLM/scripts/archiving/manual_archive.py`) that allows the user to archive files on-demand rather than automatically. The script will scan the workspace for files marked for archiving using multiple detection methods, validate files, provide dry-run mode, and archive files to appropriate locations. This implements Achievement 0.2 and gives the user full control over when archiving happens, avoiding any slowdown during LLM execution.

---

## 📋 What Needs to Be Created

### Files to Create

- `LLM/scripts/archiving/manual_archive.py` - Main archive script
- Script documentation (inline docstring and usage examples)

### Files to Modify

- `LLM/scripts/README.md` (if exists) - Add manual_archive.py documentation
- Or create `LLM/scripts/README.md` if it doesn't exist

---

## 🎯 Approach

### Step 1: Design Script Architecture

**Core Functionality**:
1. **File Detection**: Multiple methods to find files to archive
   - Metadata tag detection (`status: archived`)
   - Explicit file list (command-line arguments)
   - Pattern matching (e.g., completed EXECUTION_TASKs)
2. **Validation**: Check files exist, are readable, not already archived
3. **Dry-Run Mode**: Show what would be archived without actually archiving
4. **Archive Execution**: Move files to appropriate archive locations
5. **Error Handling**: Handle duplicates, missing files, permission errors

**Command-Line Interface**:
- `--dry-run`: Show what would be archived without archiving
- `--verbose`: Detailed output
- `--workspace`: Specify workspace directory (default: `work-space/`)
- `--pattern`: Archive files matching pattern
- Positional arguments: Explicit file list

### Step 2: Implement Script

**Key Functions**:
- `detect_files_to_archive()`: Scan workspace using detection methods
- `validate_files()`: Check files exist and are readable
- `determine_archive_location()`: Find archive location from PLAN or metadata
- `archive_files()`: Move files to archive
- `main()`: CLI interface

**Detection Methods**:
1. **Metadata Tag**: Scan files for `status: archived` in metadata
2. **Explicit List**: Files provided as command-line arguments
3. **Pattern Matching**: Files matching patterns (e.g., `EXECUTION_TASK_*_*_01.md` for completed tasks)

**Archive Location Detection**:
- Read PLAN file to find archive location
- Use metadata tag `archived:` if present
- Default to `documentation/archive/` structure

### Step 3: Create Documentation

**Inline Documentation**:
- Module docstring with usage examples
- Function docstrings
- Command-line help text

**External Documentation**:
- Add to `LLM/scripts/README.md` (or create it)
- Usage examples
- Detection method explanations
- Common use cases

### Step 4: Test Script

**Test Cases**:
- Dry-run mode works
- Detects files with metadata tags
- Handles explicit file list
- Validates files before archiving
- Handles duplicates gracefully
- Provides clear output

---

## ✅ Expected Results

### Deliverables

1. **LLM/scripts/archiving/manual_archive.py**:
   - Scans workspace for files to archive
   - Multiple detection methods (metadata, explicit, pattern)
   - Dry-run mode
   - Validation
   - Archive execution
   - Error handling

2. **Script Documentation**:
   - Inline docstrings
   - Usage examples
   - Command-line help

3. **LLM/scripts/README.md** (created or updated):
   - Manual archive script documentation
   - Usage examples
   - Detection methods explained

### Success Criteria

- [ ] Script created and functional
- [ ] Detects files using metadata tags
- [ ] Detects files from explicit list
- [ ] Dry-run mode works
- [ ] Validates files before archiving
- [ ] Archives files to correct locations
- [ ] Handles duplicates gracefully
- [ ] Documentation complete
- [ ] Script tested with examples

---

## 🧪 Tests

### Test 1: Script Exists

```bash
# Verify script exists
ls -1 LLM/scripts/archiving/manual_archive.py

# Check script is executable
python LLM/scripts/archiving/manual_archive.py --help
```

**Expected**: Script exists, help text displays

### Test 2: Dry-Run Mode

```bash
# Test dry-run mode
python LLM/scripts/archiving/manual_archive.py --dry-run --workspace work-space/
```

**Expected**: Shows files that would be archived without archiving

### Test 3: Metadata Detection

```bash
# Create test file with status: archived
# Test detection
python LLM/scripts/archiving/manual_archive.py --dry-run --workspace work-space/
```

**Expected**: Detects files with `status: archived` metadata

### Test 4: Explicit File List

```bash
# Test explicit file list
python LLM/scripts/archiving/manual_archive.py --dry-run work-space/plans/PLAN_TEST.md
```

**Expected**: Archives specified file

---

## 📝 Notes

- **User Control**: Script only archives when user runs it (no automatic archiving)
- **Workspace Focus**: Script works with workspace folder (not root directory)
- **Flexible Detection**: Multiple detection methods for different use cases
- **Safe by Default**: Dry-run mode and validation prevent accidental archiving
- **Error Handling**: Graceful handling of duplicates, missing files, errors

---

**Status**: Ready to Execute  
**Next**: Create EXECUTION_TASK and begin implementation

