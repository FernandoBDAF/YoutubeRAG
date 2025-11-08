# PLAN: New Session Context Enhancement

**Status**: Planning  
**Created**: 2025-11-08 00:30 UTC  
**Goal**: Implement Option 4: Hybrid Approach to address context gap in new LLM sessions, fix archive location issues, and enhance methodology with project context  
**Priority**: HIGH - Critical for preventing procedural errors in new sessions

---

## 📖 Context for LLM Execution

**If you're an LLM reading this to execute work**:

1. **What This Plan Is**: Implementation of context enhancement system to prevent procedural errors (like archive location mismatches) in new LLM sessions. This addresses the context gap identified in analysis where LLMs know WHAT to do but lack procedural context (HOW to do it correctly).

2. **Your Task**:

   - Fix immediate archive location issues from previous work
   - Enhance PLAN "Context for LLM Execution" sections with project context
   - Create PROJECT-CONTEXT.md for general project knowledge
   - Update prompt generator to include project context
   - Update PLAN template with project context section
   - Update achievement sections with archive instructions

3. **Project Context**:

   - **Project**: YoutubeRAG - GraphRAG pipeline for YouTube video analysis
   - **Methodology Location**: All LLM methodology files in `LLM/` directory
   - **Key Directories**:
     - `LLM/protocols/`: Entry/exit protocols (START_POINT, END_POINT, etc.)
     - `LLM/templates/`: Document templates (PLAN, SUBPLAN, EXECUTION_TASK)
     - `LLM/guides/`: Methodology guides (FOCUS-RULES, GRAMMAPLAN-GUIDE, etc.)
     - `LLM/scripts/`: Automation scripts (validation/, generation/, archiving/)
     - `documentation/archive/`: Completed work archives
   - **Archiving System**:
     - Each PLAN specifies archive location in "Archive Location" section
     - Archive structure: `documentation/archive/<feature>-<date>/subplans/` and `execution/`
     - Deferred archiving policy: Archive at achievement/plan completion (not immediately)
   - **Conventions**:
     - Files use kebab-case naming
     - Templates follow specific structure
     - Scripts organized by domain (validation/, generation/, archiving/)
     - Archive location must match PLAN specification exactly
   - **Related Work**:
     - `PLAN_FILE-MOVING-OPTIMIZATION.md` (in progress) - has archive location issues to fix
     - `EXECUTION_ANALYSIS_NEW-SESSION-CONTEXT-GAP.md` - context gap analysis
     - `EXECUTION_ANALYSIS_NEW-SESSION-WORK-REVIEW.md` - work review with issues

4. **How to Proceed**:

   - Read the achievements below (Priority 0-2)
   - Start with Priority 0 (Immediate Fixes)
   - Create SUBPLANs for complex achievements
   - Create EXECUTION_TASKs to log your work
   - Follow TDD workflow: test → implement → verify
   - Update methodology documentation

5. **What You'll Create**:

   - Fixed archive locations (files moved to correct locations)
   - Enhanced PLAN "Context for LLM Execution" sections
   - PROJECT-CONTEXT.md (general project knowledge)
   - Updated prompt generator (includes project context)
   - Updated PLAN template (project context section)
   - Updated achievement sections (archive instructions)
   - Validation scripts (archive location/structure checks)

6. **Where to Get Help**:
   - `LLM/protocols/IMPLEMENTATION_START_POINT.md` - Methodology
   - `EXECUTION_ANALYSIS_NEW-SESSION-CONTEXT-GAP.md` - Context gap analysis
   - `EXECUTION_ANALYSIS_NEW-SESSION-WORK-REVIEW.md` - Work review with issues
   - `LLM-METHODOLOGY.md` - Methodology reference

**Self-Contained**: This PLAN contains everything you need to execute it.

**Archive Location**: `documentation/archive/new-session-context-enhancement-nov2025/`

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

Implement Option 4: Hybrid Approach to address the context gap in new LLM sessions by:

1. Fixing immediate archive location issues from previous work
2. Enhancing PLAN "Context for LLM Execution" sections with project context
3. Creating PROJECT-CONTEXT.md for general project knowledge
4. Updating prompt generator to automatically include project context
5. Updating PLAN template with project context section
6. Creating validation scripts for archive location/structure

**Impact**: Prevents procedural errors (like archive location mismatches), ensures LLMs have sufficient context for both functional and procedural correctness, reduces clarification questions, improves methodology compliance.

---

## 📖 Problem Statement

**Current State**:

- New LLM sessions lack project context (structure, conventions, archive locations)
- Context gap causes procedural errors (archive location mismatches, wrong file locations)
- Work review showed: functionally correct but procedurally incorrect
- Archive location issues: files in wrong location, duplicates, missing structure
- Prompt generator doesn't include project context or archive location

**What's Wrong/Missing**:

1. **No Project Context in PLANs**: "Context for LLM Execution" doesn't include project structure, conventions, archive locations
2. **No PROJECT-CONTEXT.md**: No central source of project knowledge
3. **Prompt Generator Missing Context**: Generated prompts don't include project context or archive location
4. **Archive Location Not Prominent**: Archive location in PLAN but not in achievement sections or prompts
5. **No Validation**: No scripts to verify archive location matches PLAN
6. **Immediate Issues**: Archive location mismatch in PLAN_FILE-MOVING-OPTIMIZATION.md needs fixing

**Impact**:

- Procedural errors in new sessions (archive location mismatches, wrong file locations)
- LLMs make assumptions instead of following PLAN specifications
- Methodology compliance issues
- Time wasted fixing procedural errors
- Inconsistent work quality

**Why This Matters**:

- Context gap is confirmed by work review analysis
- Procedural errors are more common than functional errors
- Archive location is critical but not prominent enough
- Need systematic solution (Option 4: Hybrid Approach)

---

## 🎯 Success Criteria

### Must Have

- [ ] Archive location issues fixed (files in correct location, duplicates removed)
- [ ] PLAN_FILE-MOVING-OPTIMIZATION.md "Context for LLM Execution" enhanced with project context
- [ ] PROJECT-CONTEXT.md created with general project knowledge
- [ ] Prompt generator updated to include project context
- [ ] PLAN template updated with project context section
- [ ] Achievement sections include archive location instructions
- [ ] All 6 achievements complete

### Should Have

- [ ] Validation scripts created (archive location, structure, duplicates)
- [ ] Archive location included in generated prompts
- [ ] Archive structure creation steps in prompts
- [ ] Examples in templates showing project context format

### Nice to Have

- [ ] Search tool for project context
- [ ] Context validation script
- [ ] Automated context injection testing

---

## 📋 Scope Definition

### In Scope

1. **Immediate Fixes**:

   - Fix archive location for PLAN_FILE-MOVING-OPTIMIZATION.md
   - Remove duplicate files
   - Create correct archive structure

2. **Context Enhancement (Option 4: Hybrid)**:

   - Enhance PLAN "Context for LLM Execution" sections
   - Create PROJECT-CONTEXT.md
   - Update prompt generator to include project context
   - Update PLAN template with project context section

3. **Archive Location Improvements**:

   - Add archive location to achievement sections
   - Include archive location in generated prompts
   - Add archive structure creation steps

4. **Validation**:
   - Create scripts to verify archive location matches PLAN
   - Create scripts to verify archive structure exists
   - Create scripts to check for duplicate files

### Out of Scope

- Updating all existing PLANs (defer to long-term, as needed)
- Full metadata system (defer to other plans)
- Search tool implementation (defer to future)
- Context injection testing automation (defer to future)

---

## 📏 Size Limits

**⚠️ HARD LIMITS** (Must not exceed):

- **PLAN size**: <600 lines (this document)
- **Achievements per priority**: <8
- **Total priorities**: <3
- **Time estimate**: <32 hours total

**Current**: ~250 lines, 3 priorities, 6 achievements - ✅ Within limits

---

## 🌳 GrammaPlan Consideration

**Was GrammaPlan considered?**: Yes

**Decision Criteria Checked**:

- [ ] Plan would exceed 600 lines? **No** (estimated ~400 lines with 6 achievements)
- [ ] Estimated effort > 32 hours? **No** (6-8 hours estimated)
- [ ] Work spans 3+ domains? **No** (single domain: methodology enhancement)
- [ ] Natural parallelism opportunities? **No** (sequential work)

**Decision**: **Single PLAN**

**Rationale**:

- Focused scope (context enhancement + immediate fixes)
- Small effort (6-8 hours, well under 32h limit)
- Single domain (methodology documentation + scripts)
- Sequential work (fixes → context → validation)

---

## 🎯 Desirable Achievements (Priority Order)

### Priority 0: CRITICAL - Immediate Fixes

**Achievement 0.1**: Fix Archive Location Issues

- **Goal**: Fix archive location mismatch and duplicate files from PLAN_FILE-MOVING-OPTIMIZATION.md work
- **What**:
  - Create correct archive structure: `documentation/archive/file-moving-optimization-nov2025/{subplans,execution}`
  - Move files from `feature-archive/` to correct location
  - Remove duplicate files from root directory
  - Verify archive location matches PLAN specification
  - Update PLAN_FILE-MOVING-OPTIMIZATION.md if needed
- **Success**: Files in correct location, no duplicates, archive structure exists, PLAN verified
- **Effort**: 15 minutes
- **Deliverables**:
  - Correct archive structure created
  - Files moved to correct location
  - Duplicates removed
  - Verification complete

---

### Priority 1: HIGH - Context Enhancement (Phase 1)

**Achievement 1.1**: Enhance PLAN_FILE-MOVING-OPTIMIZATION.md Context

- **Goal**: Add project context to PLAN_FILE-MOVING-OPTIMIZATION.md "Context for LLM Execution" section
- **What**:
  - Add "Project Context" subsection to "Context for LLM Execution"
  - Include: project structure, domain knowledge, key conventions, related work
  - Add archive location explicitly
  - Add "How to Archive" instructions
  - Add "Archive Structure" requirements
- **Success**: PLAN has comprehensive project context, archive location prominent, instructions clear
- **Effort**: 15 minutes
- **Deliverables**:
  - Updated PLAN_FILE-MOVING-OPTIMIZATION.md with project context

**Achievement 1.2**: Create PROJECT-CONTEXT.md

- **Goal**: Create central source of general project knowledge for all PLANs
- **What**:
  - Create `PROJECT-CONTEXT.md` in root or `LLM/` directory
  - Include: project overview, structure, domain knowledge, architecture patterns, conventions
  - Document: archive conventions, file organization, naming conventions
  - Include: active work tracking, related PLANs reference
  - Format: Easy to read, well-organized, comprehensive
- **Success**: PROJECT-CONTEXT.md created, comprehensive, well-organized, referenced in methodology
- **Effort**: 1-2 hours
- **Deliverables**:
  - PROJECT-CONTEXT.md
  - Reference in LLM-METHODOLOGY.md

---

### Priority 2: HIGH - Context Enhancement (Phase 2)

**Achievement 2.1**: Update Prompt Generator with Project Context

- **Goal**: Enhance prompt generator to automatically include project context in generated prompts
- **What**:
  - Update `LLM/scripts/generation/generate_prompt.py`:
    - Add function to read PROJECT-CONTEXT.md
    - Add function to extract archive location from PLAN
    - Include project context section in generated prompt
    - Include archive location in generated prompt
    - Include archive structure creation steps
    - Add "verify archive location" to checklist
    - Graceful fallback if PROJECT-CONTEXT.md doesn't exist
  - Test with PLAN_FILE-MOVING-OPTIMIZATION.md
  - Verify prompt includes context and archive location
- **Success**: Prompt generator includes project context, archive location, archive steps, verification passes
- **Effort**: 1-2 hours
- **Deliverables**:
  - Updated generate_prompt.py
  - Test results showing context included

**Achievement 2.2**: Update PLAN Template with Project Context Section

- **Goal**: Add project context section to PLAN template for future PLANs
- **What**:
  - Update `LLM/templates/PLAN-TEMPLATE.md`:
    - Add "Project Context" subsection to "Context for LLM Execution"
    - Include placeholders for: project structure, domain, architecture, conventions, related work
    - Add archive location section
    - Add archive structure requirements
    - Add examples showing format
  - Update template documentation
- **Success**: Template includes project context section, archive location section, examples, documentation updated
- **Effort**: 30 minutes
- **Deliverables**:
  - Updated PLAN-TEMPLATE.md

**Achievement 2.3**: Update Achievement Sections with Archive Instructions

- **Goal**: Add archive location and archive instructions to achievement sections in PLAN template
- **What**:
  - Update `LLM/templates/PLAN-TEMPLATE.md`:
    - Add archive location to achievement deliverables
    - Add archive steps to achievement instructions
    - Include "verify archive location" in achievement checklist
    - Add archive structure creation steps
  - Update template examples
- **Success**: Achievement sections include archive location, archive steps, verification, examples updated
- **Effort**: 30 minutes
- **Deliverables**:
  - Updated PLAN-TEMPLATE.md (achievement sections)

---

### Priority 3: MEDIUM - Validation Scripts

**Achievement 3.1**: Create Archive Validation Scripts

- **Goal**: Create validation scripts to verify archive location matches PLAN and archive structure exists
- **What**:
  - Create `LLM/scripts/validation/validate_archive_location.py`:
    - Check archive location in PLAN matches actual archive location
    - Verify archive structure exists (subplans/, execution/)
    - Check for duplicate files (root vs archive)
    - Report mismatches and issues
    - Provide fix suggestions
  - Create `LLM/scripts/validation/validate_archive_structure.py`:
    - Verify archive directory exists
    - Verify subdirectories exist (subplans/, execution/)
    - Check archive location matches PLAN specification
  - Test with PLAN_FILE-MOVING-OPTIMIZATION.md
- **Success**: Validation scripts created, test, provide actionable feedback, catch archive issues
- **Effort**: 1-2 hours
- **Deliverables**:
  - validate_archive_location.py
  - validate_archive_structure.py
  - Test results

---

## 🔄 Subplan Tracking (Updated During Execution)

**Summary Statistics**:

- **SUBPLANs**: 7 created (7 complete, 0 in progress, 0 pending)
- **EXECUTION_TASKs**: 7 created (7 complete, 0 abandoned)
- **Total Iterations**: 31 (across all EXECUTION_TASKs: 4 + 4 + 8 + 5 + 3 + 3 + 4)
- **Time Spent**: ~48 minutes (from EXECUTION_TASK completion times: 3m + 5m + 17m + 10m + 3m + 3m + 7m)

**Subplans Created for This PLAN**:

- **SUBPLAN_01**: Achievement 0.1 (Fix Archive Location Issues) - Status: ✅ Complete
  └─ EXECUTION_TASK_01_01: Fix archive location and remove duplicates - Status: ✅ Complete (4 iterations, ~3 minutes)

  - Created correct archive structure: `documentation/archive/file-moving-optimization-nov2025/{subplans,execution}`
  - Moved files from wrong location (`feature-archive/`) to correct location
  - Removed duplicates from root directory
  - Verified archive location matches PLAN specification
  - All verification commands passed

- **SUBPLAN_11**: Achievement 1.1 (Enhance PLAN_FILE-MOVING-OPTIMIZATION.md Context) - Status: ✅ Complete
  └─ EXECUTION_TASK_11_01: Add project context and archive instructions - Status: ✅ Complete (4 iterations, ~5 minutes)

  - Added Project Context subsection to "Context for LLM Execution" section
  - Included: project structure, domain knowledge, key directories, conventions, related work
  - Added archive location explicitly in context section
  - Added archive structure requirements and "How to Archive" instructions
  - All verification commands passed

- **SUBPLAN_12**: Achievement 1.2 (Create PROJECT-CONTEXT.md) - Status: ✅ Complete
  └─ EXECUTION_TASK_12_01: Create comprehensive project context document - Status: ✅ Complete (8 iterations, ~17 minutes)

  - Created LLM/PROJECT-CONTEXT.md with all required sections
  - Included: Project Overview, Structure, Domain Knowledge, Conventions, Architecture, Related Work
  - Content is clear, actionable, and well-organized
  - File size: 387 lines (within 300-500 range)
  - All verification commands passed

- **SUBPLAN_21**: Achievement 2.1 (Update Prompt Generator with Project Context) - Status: ✅ Complete
  └─ EXECUTION_TASK_21_01: Add context injection to prompt generator - Status: ✅ Complete (5 iterations, ~10 minutes)

  - Added `inject_project_context()` function to read and format PROJECT-CONTEXT.md
  - Updated prompt template to include project context section
  - Added `--no-project-context` flag to disable context injection
  - Graceful handling of missing PROJECT-CONTEXT.md file
  - All verification commands passed

- **SUBPLAN_22**: Achievement 2.2 (Update PLAN Template with Project Context Section) - Status: ✅ Complete
  └─ EXECUTION_TASK_22_01: Add project context reference to PLAN template - Status: ✅ Complete (3 iterations, ~3 minutes)

  - Added Project Context section to "Context for LLM Execution" section
  - Included reference to `LLM/PROJECT-CONTEXT.md`
  - Added guidance on when to reference context (new sessions, unfamiliar domains)
  - Added note about prompt generator automatic context injection
  - All verification commands passed

- **SUBPLAN_23**: Achievement 2.3 (Update Achievement Sections with Archive Instructions) - Status: ✅ Complete
  └─ EXECUTION_TASK_23_01: Add archive instructions to achievement sections - Status: ✅ Complete (3 iterations, ~3 minutes)

  - Added archive location instructions to achievement section format
  - Included reference to PLAN's "Archive Location" section
  - Added guidance on archive structure creation (subplans/, execution/)
  - Added note about deferred archiving policy
  - All verification commands passed

- **SUBPLAN_31**: Achievement 3.1 (Create Archive Validation Scripts) - Status: ✅ Complete
  └─ EXECUTION_TASK_31_01: Create archive validation scripts - Status: ✅ Complete (4 iterations, ~7 minutes)

  - Created validate_archive_location.py to check archive location matches PLAN specification
  - Created validate_archive_structure.py to verify archive structure exists
  - Scripts catch archive location mismatches and missing archive structures
  - Scripts provide actionable fix suggestions
  - All verification commands passed

**Archive Location**: `documentation/archive/new-session-context-enhancement-nov2025/`

---

## ⏱️ Time Estimates

**Priority 0** (Immediate Fixes): 15 minutes  
**Priority 1** (Context Enhancement Phase 1): 1.25-2.25 hours  
**Priority 2** (Context Enhancement Phase 2): 2-4 hours  
**Priority 3** (Validation Scripts): 1-2 hours

**Total**: 4.5-8.5 hours

---

## 📝 Current Status & Handoff (For Pause/Resume)

**Last Updated**: 2025-11-08 02:06 UTC  
**Status**: In Progress

**What's Done**:

- PLAN created
- Achievement 0.1 Complete: Fix Archive Location Issues
  - Archive structure created correctly
  - Files moved from `feature-archive/` to `documentation/archive/file-moving-optimization-nov2025/`
  - Duplicates removed from root
  - Archive location verified (matches PLAN specification)
  - SUBPLAN and EXECUTION_TASK archived
- Achievement 1.1 Complete: Enhance PLAN_FILE-MOVING-OPTIMIZATION.md Context
  - Project Context subsection added to "Context for LLM Execution" section
  - Archive location explicitly stated in context section
  - Archive structure requirements and "How to Archive" instructions added
  - All verification commands passed
  - SUBPLAN and EXECUTION_TASK archived
- Achievement 1.2 Complete: Create PROJECT-CONTEXT.md
  - Created LLM/PROJECT-CONTEXT.md with all required sections
  - Included: Project Overview, Structure, Domain Knowledge, Conventions, Architecture, Related Work
  - Content is clear, actionable, and well-organized (387 lines)
  - All verification commands passed
  - SUBPLAN and EXECUTION_TASK archived
- Achievement 2.1 Complete: Update Prompt Generator with Project Context
  - Added context injection function to prompt generator
  - Updated prompt template to include project context section
  - Added `--no-project-context` flag for configuration
  - Graceful handling of missing PROJECT-CONTEXT.md file
  - All verification commands passed
  - SUBPLAN and EXECUTION_TASK archived
- Achievement 2.2 Complete: Update PLAN Template with Project Context Section
  - Added Project Context section to PLAN template
  - Included reference to `LLM/PROJECT-CONTEXT.md`
  - Added guidance on when to reference context
  - Added note about prompt generator automatic injection
  - All verification commands passed
  - SUBPLAN and EXECUTION_TASK archived
- Achievement 2.3 Complete: Update Achievement Sections with Archive Instructions
  - Added archive location instructions to achievement section format
  - Included reference to PLAN's "Archive Location" section
  - Added guidance on archive structure creation
  - Added note about deferred archiving policy
  - All verification commands passed
  - SUBPLAN and EXECUTION_TASK archived
- Achievement 3.1 Complete: Create Archive Validation Scripts
  - Created validate_archive_location.py to check archive location compliance
  - Created validate_archive_structure.py to verify archive structure exists
  - Scripts catch archive location mismatches and missing archive structures
  - Scripts provide actionable fix suggestions
  - All verification commands passed
  - SUBPLAN and EXECUTION_TASK archived

**What's Next**:

- All Priority 0-3 achievements complete! ✅
- PLAN ready for completion review or can continue with additional priorities if needed

**Status**: Priority 0-3 Complete (All immediate and short-term fixes done)

**When Resuming**:

1. Read this section
2. Review "Subplan Tracking" above
3. All Priority 0-3 achievements complete! ✅
4. Create SUBPLAN and continue

---

**Status**: Achievement 3.1 Complete (Priority 0-3 Complete)  
**Next**: PLAN ready for completion review or continue with additional priorities if needed
