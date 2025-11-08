# PLAN: File Moving Workspace and Manual Archive

**Type**: PLAN  
**Status**: Planning  
**Priority**: HIGH  
**Created**: 2025-01-27 23:30 UTC  
**Goal**: Create workspace folder for generated files and manual archive script to prevent root pollution and give user control over archiving timing

**Metadata Tags**: See `LLM/guides/METADATA-TAGS.md` for virtual organization system

---

## 📖 Context for LLM Execution

**If you're an LLM reading this to execute work**:

1. **What This Plan Is**: Additive plan to extend file moving optimizations by creating a dedicated workspace folder and manual archive script. This prevents root directory pollution and gives the user full control over when archiving happens.

2. **Your Task**:

   - Create `work-space/` folder structure for all generated files (PLANs, SUBPLANs, EXECUTION_TASKs)
   - Create manual archive script that archives files marked for archiving only when user runs it
   - Update methodology to use workspace folder
   - Update templates and protocols to reference workspace

3. **Project Context**:

   - **Project**: YoutubeRAG - GraphRAG pipeline for YouTube video analysis
   - **Methodology Location**: All LLM methodology files in `LLM/` directory
   - **Current State**: Files are created in root directory, causing pollution
   - **Related Work**:
     - `PLAN_FILE-MOVING-OPTIMIZATION.md` (completed) - established deferred archiving policy
     - `PLAN_FILE-MOVING-ADVANCED-OPTIMIZATION.md` (planned) - search tool and virtual organization

4. **How to Proceed**:

   - Read the achievements below (Priority 0-1)
   - Start with Priority 0 (Workspace Structure)
   - Create SUBPLANs for complex achievements
   - Create EXECUTION_TASKs to log your work
   - Follow TDD workflow: test → implement → verify
   - Update methodology documentation

5. **What You'll Create**:

   - `work-space/` directory structure
   - Manual archive script (`LLM/scripts/archiving/manual_archive.py`)
   - Updated templates (reference workspace)
   - Updated protocols (use workspace)
   - Updated documentation

6. **Where to Get Help**:
   - `LLM/protocols/IMPLEMENTATION_START_POINT.md` - Methodology
   - `LLM/protocols/IMPLEMENTATION_END_POINT.md` - Completion workflow
   - `LLM-METHODOLOGY.md` - Methodology reference
   - `documentation/archive/file-moving-optimization-nov2025/` - Previous file moving work

**Self-Contained**: This PLAN contains everything you need to execute it.

**Archive Location**: `documentation/archive/file-moving-workspace-and-manual-archive-jan2025/`

---

## 📖 What to Read (Focus Rules)

**When working on this PLAN**, follow these focus rules to minimize context:

**✅ READ ONLY**:

- Current achievement section (50-100 lines)
- "Current Status & Handoff" section (30-50 lines)
- Active SUBPLANs (if any exist)
- Summary statistics (for metrics)

**❌ DO NOT READ**:

- Other achievements (unless reviewing)
- Completed achievements
- Full SUBPLAN content (unless creating one)
- Full EXECUTION_TASK content (unless creating one)

**Context Budget**: ~200 lines per achievement

**Why**: PLAN defines WHAT to achieve. Reading all achievements at once causes context overload. Focus on current achievement only.

**📖 See**: `LLM/guides/FOCUS-RULES.md` for complete focus rules and examples.

---

## 🎯 Goal

Create a dedicated workspace folder for all generated methodology files (PLANs, SUBPLANs, EXECUTION_TASKs) and implement a manual archive script that allows the user to archive files on-demand rather than automatically. This prevents root directory pollution and gives the user full control over archiving timing, avoiding any slowdown during LLM execution.

**Key Benefits**:

- Clean root directory (no methodology files cluttering it)
- User-controlled archiving (archive when convenient, not during execution)
- Better organization (all active work in one place)
- No execution slowdown (archiving happens separately)

---

## 📖 Problem Statement

**Current State**:

- All PLANs, SUBPLANs, and EXECUTION_TASKs are created in the root directory
- Root directory has 17+ PLANs, 30+ SUBPLANs, 31+ EXECUTION_TASKs
- Files accumulate in root, making it hard to find project files
- Archiving happens at achievement completion (deferred policy from previous PLAN)

**What's Wrong/Missing**:

- Root directory is polluted with methodology files
- No dedicated workspace for active work
- Archiving still happens during execution (even if deferred)
- User has no control over when archiving happens (must happen at achievement completion)

**Impact**:

- Hard to navigate root directory
- Methodology files mixed with project files
- Archiving during execution can still cause slowdowns
- User wants to batch archive when convenient, not during work

---

## 🎯 Success Criteria

### Must Have

- [ ] `work-space/` folder created with proper structure
- [ ] All new PLANs, SUBPLANs, EXECUTION_TASKs created in workspace
- [ ] Manual archive script created (`LLM/scripts/archiving/manual_archive.py`)
- [ ] Script archives files marked for archiving (metadata tag or explicit marking)
- [ ] Templates updated to reference workspace folder
- [ ] Protocols updated to use workspace folder
- [ ] Documentation updated (LLM-METHODOLOGY.md, guides)

### Should Have

- [ ] Migration guide for moving existing files to workspace
- [ ] Script validates files before archiving
- [ ] Script provides dry-run mode
- [ ] Workspace structure documented

### Nice to Have

- [ ] Script provides summary of what will be archived
- [ ] Script handles edge cases (duplicates, missing files)
- [ ] Workspace cleanup utilities

---

## 📋 Scope Definition

### In Scope

- Create `work-space/` directory structure
- Create manual archive script with metadata-based file detection
- Update templates to generate files in workspace
- Update protocols to reference workspace
- Update documentation
- Migration of existing files (optional, can be manual)

### Out of Scope

- Automatic archiving (user wants manual control)
- Search tool implementation (see PLAN_FILE-MOVING-ADVANCED-OPTIMIZATION.md)
- Virtual organization (see PLAN_FILE-MOVING-ADVANCED-OPTIMIZATION.md)
- Moving existing files automatically (user can do manually)

**Rationale**: Focus on workspace creation and manual archive script. Advanced features deferred to other plans.

---

## 📏 Size Limits

**⚠️ HARD LIMITS** (Must not exceed):

- **PLAN size**: <600 lines (this document)
- **Achievements per priority**: <8
- **Total priorities**: <2
- **Time estimate**: <32 hours total

**Current**: ~250 lines estimated, 2 priorities, 4 achievements - ✅ Within limits

---

## 🌳 GrammaPlan Consideration

**Was GrammaPlan considered?**: Yes

**Decision Criteria Checked**:

- [ ] Plan would exceed 600 lines? **No** (estimated ~250 lines with 4 achievements)
- [ ] Estimated effort > 32 hours? **No** (4-6 hours estimated)
- [ ] Work spans 3+ domains? **No** (single domain: file organization)
- [ ] Natural parallelism opportunities? **No** (sequential work)

**Decision**: **Single PLAN**

**Rationale**:

- Focused scope (workspace + manual archive)
- Small effort (4-6 hours, well under 32h limit)
- Single domain (file organization)
- Sequential work (workspace → script → integration)

---

## 🎯 Desirable Achievements (Priority Order)

### Priority 0: HIGH - Workspace Structure

**Achievement 0.1**: Workspace Folder Creation

- **Goal**: Create `work-space/` directory structure for all generated methodology files
- **What**:
  - Create `work-space/` directory in project root
  - Create subdirectories:
    - `work-space/plans/` - For PLAN files
    - `work-space/subplans/` - For SUBPLAN files
    - `work-space/execution/` - For EXECUTION_TASK files
  - Create `work-space/README.md`:
    - Explain workspace purpose
    - Document structure
    - Usage instructions
    - Migration notes
  - Update `.gitignore` (if needed) to exclude workspace from version control (optional)
- **Success**: Workspace folder created with proper structure, documented
- **Effort**: 30 minutes
- **Deliverables**:
  - `work-space/` directory with subdirectories
  - `work-space/README.md`

**Achievement 0.2**: Manual Archive Script Creation

- **Goal**: Create script that archives files marked for archiving, only when user runs it
- **What**:
  - Create `LLM/scripts/archiving/manual_archive.py`:
    - Scans workspace for files marked for archiving
    - Detection methods:
      - Files with `status: archived` metadata tag
      - Files in explicit archive list (config file or command-line)
      - Files matching archive patterns (e.g., completed EXECUTION_TASKs)
    - Validates files exist and are readable
    - Provides dry-run mode (`--dry-run` flag)
    - Shows summary of what will be archived
    - Archives files to appropriate archive location
    - Handles duplicates (skip or error)
    - Provides verbose output
  - Create script documentation:
    - Usage examples
    - Command-line options
    - Archive detection methods
  - Add to `LLM/scripts/README.md` (if exists) or create it
- **Success**: Script created, tested, documented, can archive files on-demand
- **Effort**: 2-3 hours
- **Deliverables**:
  - `LLM/scripts/archiving/manual_archive.py`
  - Script documentation
  - Usage examples

---

### Priority 1: HIGH - Methodology Integration

**Achievement 1.1**: Template Updates for Workspace

- **Goal**: Update all templates to generate files in workspace folder
- **What**:
  - Update `LLM/templates/PLAN-TEMPLATE.md`:
    - Change file location from root to `work-space/plans/`
    - Update archive location references
    - Add workspace guidance
  - Update `LLM/templates/SUBPLAN-TEMPLATE.md`:
    - Change file location from root to `work-space/subplans/`
    - Update references
  - Update `LLM/templates/EXECUTION_TASK-TEMPLATE.md`:
    - Change file location from root to `work-space/execution/`
    - Update references
  - Update `LLM/templates/PROMPTS.md`:
    - Update "Create New PLAN" prompt to reference workspace
    - Update file paths in examples
- **Success**: All templates updated, files will be created in workspace
- **Effort**: 1 hour
- **Deliverables**:
  - Updated PLAN-TEMPLATE.md
  - Updated SUBPLAN-TEMPLATE.md
  - Updated EXECUTION_TASK-TEMPLATE.md
  - Updated PROMPTS.md

**Achievement 1.2**: Protocol and Documentation Updates

- **Goal**: Update protocols and documentation to use workspace folder
- **What**:
  - Update `LLM/protocols/IMPLEMENTATION_START_POINT.md`:
    - Reference workspace folder for file creation
    - Update file location examples
  - Update `LLM/protocols/IMPLEMENTATION_END_POINT.md`:
    - Reference manual archive script
    - Update archiving workflow (use manual script)
    - Remove automatic archiving references
  - Update `LLM-METHODOLOGY.md`:
    - Add workspace folder to directory structure
    - Document workspace purpose
    - Reference manual archive script
  - Update `LLM/index/FILE-INDEX.md`:
    - Update file locations (workspace instead of root)
    - Update statistics
- **Success**: All protocols and documentation updated, workspace integrated
- **Effort**: 1-2 hours
- **Deliverables**:
  - Updated IMPLEMENTATION_START_POINT.md
  - Updated IMPLEMENTATION_END_POINT.md
  - Updated LLM-METHODOLOGY.md
  - Updated FILE-INDEX.md

---

## ⏱️ Time Estimates

**Priority 0** (Workspace Structure): 2.5-3.5 hours (0.1: 0.5h, 0.2: 2-3h)  
**Priority 1** (Methodology Integration): 2-3 hours

**Total**: 4.5-6.5 hours

---

## 🔄 Subplan Tracking (Updated During Execution)

**Summary Statistics**:

- **SUBPLANs**: 1 created, 1 complete
- **EXECUTION_TASKs**: 1 created, 1 complete
- **Total Iterations**: 1
- **Time Spent**: 0.33 hours

**Subplans Created for This PLAN**:

1. **SUBPLAN_FILE-MOVING-WORKSPACE-AND-MANUAL-ARCHIVE_01.md** (Achievement 0.1)
   - Status: Complete
   - EXECUTION_TASKs: 1 (EXECUTION_TASK_FILE-MOVING-WORKSPACE-AND-MANUAL-ARCHIVE_01_01.md)
   - Iterations: 1
   - Time: 0.33 hours
   - Archived: `documentation/archive/file-moving-workspace-and-manual-archive-jan2025/subplans/`

**Archive Location**: `documentation/archive/file-moving-workspace-and-manual-archive-jan2025/`

---

## 📝 Current Status & Handoff (For Pause/Resume)

**Last Updated**: 2025-01-27 23:55 UTC  
**Status**: In Progress

**What's Done**:

- PLAN created
- Achievement 0.1 complete (Workspace Folder Creation)
  - Created work-space/ directory with subdirectories (plans/, subplans/, execution/)
  - Created work-space/README.md with comprehensive documentation
  - SUBPLAN and EXECUTION_TASK archived

**What's Next**:

- Achievement 0.2 (Manual Archive Script Creation)

**When Resuming**:

1. Read this section
2. Review "Subplan Tracking" above
3. Select next achievement (0.2)
4. Create SUBPLAN and continue

---

**Status**: Achievement 0.1 Complete  
**Next**: Achievement 0.2 (Manual Archive Script Creation)
