# LLM Scripts Documentation

**Purpose**: Documentation for all automation scripts in the LLM methodology  
**Last Updated**: 2025-01-28

---

## 📁 Script Organization

Scripts are organized by domain:

- **archiving/**: File archiving scripts
- **generation/**: Prompt and document generation scripts
- **validation/**: Validation and compliance checking scripts

---

## 📦 Archiving Scripts

### manual_archive.py

**Purpose**: User-controlled archiving of files from workspace (on-demand, not automatic)

**Location**: `LLM/scripts/archiving/manual_archive.py`

**Usage**:

```bash
# Dry-run: See what would be archived
python LLM/scripts/archiving/manual_archive.py --dry-run --workspace work-space/

# Archive files with status: archived metadata tag
python LLM/scripts/archiving/manual_archive.py --workspace work-space/

# Archive specific files
python LLM/scripts/archiving/manual_archive.py work-space/plans/PLAN_TEST.md

# Archive files matching pattern
python LLM/scripts/archiving/manual_archive.py --pattern "EXECUTION_TASK_*_*_01.md" --workspace work-space/
```

**Detection Methods**:

1. **Metadata Tag**: Files with `status: archived` in metadata section
2. **Explicit List**: Files provided as command-line arguments
3. **Pattern Matching**: Files matching specified pattern (e.g., `EXECUTION_TASK_*_*_01.md`)

**Features**:

- Dry-run mode (`--dry-run`) to preview what would be archived
- Multiple detection methods for flexibility
- Validates files before archiving
- Handles duplicates gracefully
- Verbose output option (`--verbose`)
- Works with workspace folder structure

**When to Use**:

- Archive files when convenient (not during execution)
- Batch archive multiple files at once
- Preview what would be archived before actually archiving

**Related**: See `archive_completed.py` for deferred archiving during execution

---

### archive_completed.py

**Purpose**: Archive completed SUBPLANs and EXECUTION_TASKs (supports deferred archiving)

**Location**: `LLM/scripts/archiving/archive_completed.py`

**Usage**:

```bash
# Single file
python LLM/scripts/archiving/archive_completed.py @SUBPLAN_FEATURE_01.md

# Batch mode (recommended for deferred archiving)
python LLM/scripts/archiving/archive_completed.py --batch @SUBPLAN_FEATURE_01.md @EXECUTION_TASK_FEATURE_01_01.md
```

**Features**:

- Auto-detects archive location from PLAN file
- Creates archive structure if needed
- Supports batch operations for deferred archiving
- Works with root directory files

**When to Use**:

- Archive files at achievement completion (deferred archiving policy)
- Archive files during execution workflow

**Related**: See `manual_archive.py` for user-controlled on-demand archiving

---

## 🔧 Generation Scripts

Scripts for generating prompts and documents. See individual script files for documentation.

---

## ✅ Validation Scripts

Scripts for validating PLAN compliance, achievement completion, etc. See individual script files for documentation.

---

**Note**: This README is a work in progress. Individual scripts contain detailed documentation in their docstrings.
