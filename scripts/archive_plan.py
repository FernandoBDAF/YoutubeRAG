#!/usr/bin/env python3
"""
Archive PLAN and related documents.

This is a template script - edit the configuration section for each PLAN,
then run to archive all documents.

Usage:
    python scripts/archive_plan.py
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# ============================================================================
# EDIT THIS SECTION FOR EACH PLAN
# ============================================================================

# Feature name (must match PLAN filename)
FEATURE = "STRUCTURED-LLM-DEVELOPMENT"  # Configured by IMPLEMENTATION_END_POINT

# Archive date (month-year format)
ARCHIVE_DATE = "partial-nov-2025"  # PARTIAL completion

# Archive description (one sentence)
ARCHIVE_DESCRIPTION = (
    "Structured LLM development methodology foundation (partial completion)"
)

# Implementation period
START_DATE = "2025-11-05"
END_DATE = "2025-11-05"

# Total duration in hours
DURATION_HOURS = 2.85  # Total across 8 subplans

# Completion type
COMPLETION_TYPE = "partial"  # "partial" or "full"

# ============================================================================
# DO NOT EDIT BELOW (unless customizing archive structure)
# ============================================================================


def main():
    """Archive PLAN and all related documents."""

    root = Path(".")
    archive_name = f"{FEATURE.lower()}-{ARCHIVE_DATE}"
    archive_base = Path(f"documentation/archive/{archive_name}")

    print(f"Archiving {FEATURE} to {archive_base}")
    print("=" * 60)

    # Create archive structure
    folders = {
        "planning": archive_base / "planning",
        "subplans": archive_base / "subplans",
        "execution": archive_base / "execution",
        "summary": archive_base / "summary",
    }

    for name, path in folders.items():
        path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {path}")

    # Find and move files
    files_to_move = {
        "planning": [f"PLAN_{FEATURE}.md"],
        "subplans": list(root.glob(f"SUBPLAN_{FEATURE}_*.md")),
        "execution": list(root.glob(f"EXECUTION_*_{FEATURE}_*.md"))
        + list(root.glob(f"EXECUTION_{FEATURE}_*.md")),
    }

    moved_count = 0

    # Move PLAN (only if full completion)
    if COMPLETION_TYPE == "full":
        for filename in files_to_move["planning"]:
            src = root / filename
            if src.exists():
                dest = folders["planning"] / filename
                shutil.move(str(src), str(dest))
                print(f"✓ Moved: {filename} → planning/")
                moved_count += 1
            else:
                print(f"⚠ Not found: {filename}")
    else:
        print(
            f"ℹ Partial completion - PLAN stays in root: {files_to_move['planning'][0]}"
        )

    # Move SUBPLANs
    for src in files_to_move["subplans"]:
        if src.exists():
            dest = folders["subplans"] / src.name
            shutil.move(str(src), str(dest))
            print(f"✓ Moved: {src.name} → subplans/")
            moved_count += 1

    # Move EXECUTION_TASKs
    for src in files_to_move["execution"]:
        if src.exists():
            dest = folders["execution"] / src.name
            shutil.move(str(src), str(dest))
            print(f"✓ Moved: {src.name} → execution/")
            moved_count += 1

    # Create INDEX.md
    index_content = generate_index()
    index_path = archive_base / "INDEX.md"
    index_path.write_text(index_content)
    print(f"✓ Created: INDEX.md")

    print("=" * 60)
    print(f"Archive complete: {moved_count} files moved")
    print(f"Location: {archive_base}")
    print(f"\nNext: Create completion summary in {folders['summary']}")


def generate_index():
    """Generate INDEX.md template for archive."""

    status = (
        "Partial Completion (In Progress)"
        if COMPLETION_TYPE == "partial"
        else "Complete"
    )
    active_plan_note = (
        f"\n**Active PLAN**: `PLAN_{FEATURE}.md` (still in root)\n"
        if COMPLETION_TYPE == "partial"
        else ""
    )

    return f"""# {FEATURE.replace('-', ' ').title()} Archive - {ARCHIVE_DATE.replace('partial-', '').split('-')[0].title()} {ARCHIVE_DATE.replace('partial-', '').split('-')[1]}

**Implementation Period**: {START_DATE} - {END_DATE}  
**Duration**: {DURATION_HOURS} hours  
**Result**: {ARCHIVE_DESCRIPTION}  
**Status**: {status}{active_plan_note}

---

## Purpose

This archive contains all documentation for {FEATURE.replace('-', ' ')} implementation.

**Use for**: [EDIT: When to reference this archive]

**Current Documentation**:
- [EDIT: Links to current docs]
- [EDIT: Links to permanent docs created]

---

## What Was Built

[EDIT: 2-3 paragraph summary of achievements]

**Key Achievements**:
- [EDIT: Achievement 1]
- [EDIT: Achievement 2]

**Metrics/Impact**:
- [EDIT: Metric 1]
- [EDIT: Metric 2]

---

## Archive Contents

### planning/ (1 file)
- `PLAN_{FEATURE}.md` - Mother plan with all achievements

### subplans/ ([X] files)
[EDIT: List subplans]

### execution/ ([X] files)
[EDIT: List execution tasks]

### summary/ ([X] files)
[EDIT: Completion summary when created]

---

## Key Documents

**Start Here**:
1. INDEX.md (this file) - Overview
2. `planning/PLAN_{FEATURE}.md` - What we aimed to achieve

**Deep Dive**:
1. `subplans/` - Specific approaches taken
2. `execution/` - Implementation journeys and learnings

---

## Implementation Timeline

**{START_DATE}**: Started  
[EDIT: Add key milestones]  
**{END_DATE}**: Completed

---

## Code Changes

[EDIT: List files modified/created, or "No code changes - documentation work"]

---

## Testing

[EDIT: Test files created, coverage, or "Not applicable"]

---

## Related Archives

[EDIT: Links to related archives]

---

**Archive Complete**: [X] files preserved  
**Reference from**: [EDIT: Current docs that link here]
"""


if __name__ == "__main__":
    main()
