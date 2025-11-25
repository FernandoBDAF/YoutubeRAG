# Workspace Organization Pattern

**Purpose**: Describe the organized workspace folder structure for execution-level work  
**Status**: Active  
**Created**: 2025-11-09 15:00 UTC  
**Related**: EXECUTION-TAXONOMY.md, LLM-METHODOLOGY.md

---

## 🎯 Overview

The workspace is organized to provide dedicated folders for each execution work type, enabling better discovery, organization, and maintainability of execution-level work while supporting both SUBPLAN-connected implementation (EXECUTION_TASK) and orphaned knowledge work (EXECUTION_WORK).

---

## 📁 Workspace Structure

```
work-space/
├── execution/              # EXECUTION_TASK (SUBPLAN-connected, implementation)
├── analyses/               # EXECUTION_ANALYSIS (orphaned knowledge)
├── case-studies/           # EXECUTION_CASE-STUDY (pattern documentation)
├── observations/           # EXECUTION_OBSERVATION (real-time feedback)
├── debug-logs/             # EXECUTION_DEBUG (issue investigation)
├── reviews/                # EXECUTION_REVIEW (implementation assessment)
├── plans/                  # PLAN files (nested structure below)
│   └── [FEATURE]/
│       ├── PLAN_[FEATURE].md
│       ├── subplans/
│       ├── execution/
│       │   ├── EXECUTION_TASK_*.md
│       │   └── feedbacks/     # ← Filesystem-first state tracking
│       │       ├── APPROVED_01.md
│       │       ├── APPROVED_02.md
│       │       └── FIX_03.md
│       └── documentation/
├── subplans/               # SUBPLAN files (legacy flat structure)
├── grammaplans/            # GRAMMAPLAN files
├── north-stars/            # NORTH_STAR files
└── archive/                # Legacy archive
```

**Note**: The `execution/feedbacks/` folder within each PLAN directory is critical for filesystem-first architecture. It contains `APPROVED_XX.md` and `FIX_XX.md` files that track achievement completion status.

---

## 📋 Folder Purposes

### EXECUTION_TASK (`execution/`)

**Purpose**: Track implementation journey of a SUBPLAN

**File Type**: EXECUTION_TASK (SUBPLAN-connected)

**Characteristics**:

- Connected to specific SUBPLAN
- <200 lines (hard limit)
- Iteration tracking with TDD workflow
- Deleted when SUBPLAN archived

**Example**: `EXECUTION_TASK_FEATURE_01_01.md`

**Location**: `work-space/execution/` (flat) OR nested in PLAN folder

---

### EXECUTION_ANALYSIS (`analyses/`)

**Purpose**: Capture structured investigation and analysis work

**File Type**: EXECUTION_ANALYSIS (orphaned knowledge)

**Characteristics**:

- Standalone (not SUBPLAN-connected)
- 200-1,000+ lines
- Evidence-based findings
- Archived by type/topic for future reference

**5 Subcategories**:

1. Bug-Analysis: Root cause investigation
2. Methodology-Review: Process assessment
3. Implementation-Review: Code/feature quality
4. Process-Analysis: Workflow analysis
5. Planning-Strategy: Strategic planning

**Example**: `EXECUTION_ANALYSIS_DATABASE-SELECTION-STRATEGY.md`

---

### EXECUTION_CASE-STUDY (`case-studies/`)

**Purpose**: Document patterns and learnings from real examples

**File Type**: EXECUTION_CASE-STUDY (orphaned knowledge)

**Characteristics**:

- Deep dive with pattern extraction
- Real example from codebase
- Lessons extracted
- Generalizable insights

**Example**: `EXECUTION_CASE-STUDY_ENTITY-RESOLUTION-LEARNINGS.md`

---

### EXECUTION_OBSERVATION (`observations/`)

**Purpose**: Capture real-time feedback during work

**File Type**: EXECUTION_OBSERVATION (orphaned knowledge)

**Characteristics**:

- Informal findings
- Real-time discoveries
- Quick feedback
- May evolve into ANALYSIS later
- Living document

**Naming**: Include date for temporal tracking

**Example**: `EXECUTION_OBSERVATION_PERFORMANCE-ISSUE_2025-11-09.md`

---

### EXECUTION_DEBUG (`debug-logs/`)

**Purpose**: Document systematic debugging investigations

**File Type**: EXECUTION_DEBUG (orphaned knowledge)

**Characteristics**:

- Complex issue investigation
- Reproduction steps documented
- Root cause found
- Solution documented

**Example**: `EXECUTION_DEBUG_CIRCULAR-REFERENCE-BUG.md`

---

### EXECUTION_REVIEW (`reviews/`)

**Purpose**: Post-completion assessment of implementation

**File Type**: EXECUTION_REVIEW (orphaned knowledge)

**Characteristics**:

- Evaluates quality
- Verifies requirements
- Identifies gaps
- Suggests improvements

**Example**: `EXECUTION_REVIEW_API-IMPLEMENTATION.md`

---

## 🔄 File Organization Pattern

### For Flat EXECUTION_WORK Folders

Each folder (analyses/, case-studies/, observations/, debug-logs/, reviews/) follows this pattern:

**Folder Contents**:

```
work-space/analyses/
├── EXECUTION_ANALYSIS_TOPIC_1.md
├── EXECUTION_ANALYSIS_TOPIC_2.md
├── INDEX.md                           # Navigation & discovery
├── README.md                           # Folder purpose
└── [more EXECUTION_ANALYSIS files]
```

**INDEX.md Template**:

```markdown
# analyses/ Archive Index

**Total Files**: [COUNT]
**Last Updated**: [DATE]

## Recent Files

| File   | Topics   | Size   | Date   |
| ------ | -------- | ------ | ------ |
| [Name] | [Topics] | [Size] | [Date] |

## Search by Topic

[Topics extracted from all files]

## Archive Batches

[Links to archived batches in LLM/archiving/analyses/]
```

**README.md Template**:

```markdown
# EXECUTION_ANALYSIS Files

**Purpose**: Structured investigation of specific problems/situations

**File Naming**: `EXECUTION_ANALYSIS_<TOPIC>.md`

**When to Create**:

- Need to investigate strategy options
- Analyze methodology or process
- Review implementation quality
- Break down complex problem

**Examples**:

- `EXECUTION_ANALYSIS_DATABASE-SELECTION.md`
- `EXECUTION_ANALYSIS_METHODOLOGY-REVIEW.md`
- `EXECUTION_ANALYSIS_IMPLEMENTATION-REVIEW.md`

**Organization**:

- Files indexed in INDEX.md
- Topics listed for discoverability
- Archived by date in LLM/archiving/

**Size**: 200-1,000+ lines (variable)
```

---

### For EXECUTION_TASK in Plans

```
work-space/plans/PLAN_NAME/execution/
├── EXECUTION_TASK_FEATURE_01_01.md
├── EXECUTION_TASK_FEATURE_01_02.md
├── EXECUTION_TASK_FEATURE_02_01.md
└── [more EXECUTION_TASK files]
```

---

## 🔍 Discovery & Navigation

### INDEX.md Files

Each folder maintains an INDEX.md for navigation:

- Lists all files with metadata
- Organizes by topic/category
- Provides search guidance
- Links to archives

### README.md Files

Each folder has a README.md explaining:

- Folder purpose
- File naming conventions
- When to create files
- Examples and patterns

### Archive References

Workspace INDEX.md links to `LLM/archiving/{FOLDER}/{BATCH}/` for historical files

---

## 📚 Best Practices

### When Creating New Work

1. **Determine Type**: Is this SUBPLAN-connected (EXECUTION_TASK) or standalone (EXECUTION_WORK)?
2. **Choose Folder**: Use decision tree from EXECUTION-TAXONOMY.md
3. **Follow Naming**: Use standard `EXECUTION_<TYPE>_<TOPIC>.md`
4. **Update INDEX.md**: Add entry to folder's INDEX.md
5. **Archive Periodically**: Move completed work to `LLM/archiving/`

### Folder Maintenance

1. **Regular Cleanup**: Archive old/complete files (on-demand)
2. **Index Updates**: Keep INDEX.md current
3. **Link Verification**: Check archive links monthly
4. **Metrics**: Track folder sizes and growth

---

## 🎯 Scalability Considerations

### Current Capacity

- **Per Folder**: ~100 files before slowdown
- **Per Index**: ~50 files before unwieldy
- **Archive Trigger**: 200+ files in workspace

### Growth Strategy

**Phase 1 (Now)**: Flat folders with INDEX.md (current)

**Phase 2 (50+ PLANs)**: Consider internal grouping:

```
work-space/analyses/
├── graphrag/           # By domain
├── entity-resolution/
├── api-layer/
└── [other domains]
```

**Phase 3 (100+ PLANs)**: Add database for queryable metadata

---

## 🔗 Integration with Archive System

This workspace organization integrates with the archiving system:

**Archive Structure** (mirrors workspace):

```
LLM/archiving/
├── analyses/
│   ├── _01/  (First batch)
│   ├── _02/  (Second batch)
│   └── ...
├── case-studies/
├── observations/
└── ...
```

**Archive Workflow**:

1. User selects files from workspace folder
2. System creates numbered batch (\_01/, \_02/, etc.)
3. System generates ARCHIVE*SUMMARY*{BATCH}.md
4. Workspace INDEX.md updated with archive link

---

## ✅ Validation Checklist

- [ ] All EXECUTION_WORK folders created (analyses, case-studies, observations, debug-logs, reviews)
- [ ] Each folder has README.md explaining its purpose
- [ ] Each folder has INDEX.md for navigation
- [ ] Naming conventions consistent with EXECUTION-TAXONOMY.md
- [ ] Archive structure mirrors workspace organization
- [ ] EXECUTION_TASK files nested in PLAN folders
- [ ] Workspace structure documented and communicated

---

## 📖 Related Documentation

- **EXECUTION-TAXONOMY.md** - Detailed type definitions and decision tree
- **LLM-METHODOLOGY.md** - Overall methodology and file organization
- **WORKSPACE-ORGANIZATION-PATTERN.md** (this file) - Folder structure and navigation

---

**Status**: Active  
**Last Updated**: 2025-11-09 15:00 UTC  
**Owner**: PLAN_EXECUTION-TAXONOMY-AND-WORKSPACE.md (Achievement 1.1)
