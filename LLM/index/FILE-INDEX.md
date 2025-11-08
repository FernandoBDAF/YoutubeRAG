# File Index: LLM Methodology Files

**Purpose**: Central catalog of all methodology files for fast discovery  
**Last Updated**: 2025-01-27  
**Total Files**: 78+

---

## 📊 Summary Statistics

| Type | Count | Location |
|------|-------|----------|
| PLANs (active) | 17 | Root directory |
| SUBPLANs (active) | 30 | Root directory |
| EXECUTION_TASKs (active) | 31 | Root directory |
| Scripts | 16 | LLM/scripts/ |
| Templates | 5 | LLM/templates/ |
| Protocols | 5 | LLM/protocols/ |
| Guides | 6 | LLM/guides/ |
| Documentation | 4 | LLM/ |
| Archived Plans | Many | documentation/archive/ |

---

## 🗂️ Active Plans (Root Directory)

### File Moving Optimization Plans
- `PLAN_FILE-MOVING-OPTIMIZATION.md` - Quick wins for file moving (deferred archiving, file index, metadata)
- `PLAN_FILE-MOVING-ADVANCED-OPTIMIZATION.md` - Advanced optimization (batch archiving, search tool, virtual organization)

### Methodology Plans
- `PLAN_EXECUTION-ANALYSIS-INTEGRATION.md` - Integration of EXECUTION_ANALYSIS documents into methodology
- `PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md` - Bug fixes for prompt generator
- `PLAN_PLAN-COMPLETION-VERIFICATION-AND-PROMPT-FIX.md` - PLAN completion verification improvements

### Other Active Plans
- Additional PLANs (17 total) - See root directory for complete list

---

## 📄 Active SUBPLANs (Root Directory)

SUBPLANs are created for each achievement and follow naming convention:
- `SUBPLAN_<FEATURE>_<NUMBER>.md`

**Current Active**: 30 SUBPLANs  
**Location**: Root directory  
**Related to**: Active PLANs

---

## 📋 Active EXECUTION_TASKs (Root Directory)

EXECUTION_TASKs log execution attempts and follow naming convention:
- `EXECUTION_TASK_<FEATURE>_<SUBPLAN>_<EXECUTION>.md`

**Current Active**: 31 EXECUTION_TASKs  
**Location**: Root directory  
**Related to**: Active SUBPLANs

---

## 🔧 Scripts (LLM/scripts/)

### Archiving Scripts (LLM/scripts/archiving/)
- `archive_completed.py` - Archive completed SUBPLANs and EXECUTION_TASKs

### Generation Scripts (LLM/scripts/generation/)
- `generate_prompt.py` - Generate prompts for next achievement
- `generate_pause_prompt.py` - Generate prompts for pausing work
- `generate_resume_prompt.py` - Generate prompts for resuming work
- `generate_verify_prompt.py` - Generate verification prompts

### Validation Scripts (LLM/scripts/validation/)
- `check_execution_task_size.py` - Validate EXECUTION_TASK size (<200 lines)
- `check_plan_size.py` - Validate PLAN size (<600 lines)
- `validate_achievement_completion.py` - Validate achievement deliverables exist
- `validate_archive_location.py` - Validate archive location matches PLAN
- `validate_archive_structure.py` - Validate archive structure (subplans/, execution/)
- `validate_execution_start.py` - Validate execution start compliance
- `validate_mid_plan.py` - Validate mid-plan review compliance
- `validate_plan_completion.py` - Validate PLAN completion requirements
- `validate_plan_compliance.py` - Validate PLAN structure compliance
- `validate_references.py` - Validate file references are correct
- `validate_registration.py` - Validate components registered in PLAN

---

## 📝 Templates (LLM/templates/)

- `PLAN-TEMPLATE.md` - Template for creating new PLANs
- `SUBPLAN-TEMPLATE.md` - Template for creating SUBPLANs
- `EXECUTION_TASK-TEMPLATE.md` - Template for creating EXECUTION_TASKs
- `GRAMMAPLAN-TEMPLATE.md` - Template for creating GRAMMAPLANs
- `PROMPTS.md` - Pre-defined prompts for common workflows ⭐ **Start here!**

---

## 📖 Protocols (LLM/protocols/)

### Entry/Exit Workflows
- `IMPLEMENTATION_START_POINT.md` - How to start new work
- `IMPLEMENTATION_RESUME.md` - How to resume paused work
- `IMPLEMENTATION_END_POINT.md` - How to complete and archive work
- `CONTINUE_EXECUTION.md` - How to continue mid-execution
- `NEXT_ACHIEVEMENT.md` - How to move to next achievement

### Backlog Management
- `IMPLEMENTATION_BACKLOG.md` - Backlog of future work items

---

## 📚 Guides (LLM/guides/)

### Core Guides
- `FOCUS-RULES.md` - Context management and focus rules
- `CONTEXT-MANAGEMENT.md` - Advanced context management techniques
- `MULTIPLE-PLANS-PROTOCOL.md` - Managing multiple active PLANs
- `MULTI-LLM-PROTOCOL.md` - Multi-LLM team collaboration
- `GRAMMAPLAN-GUIDE.md` - When and how to use GRAMMAPLANs
- `IMPLEMENTATION_MID_PLAN_REVIEW.md` - Mid-plan review process

---

## 📑 Documentation (LLM/)

- `README.md` - LLM folder overview and navigation
- `QUICK-START.md` - 5-minute getting started guide
- `PROJECT-CONTEXT.md` - Project context for LLM execution
- `EXPORT.md` - Export and sharing guidelines

---

## 📦 Archived Work (documentation/archive/)

Completed PLANs, SUBPLANs, and EXECUTION_TASKs are archived to:
- `documentation/archive/<feature>-<date>/`

Structure:
- `planning/` - PLAN files
- `subplans/` - SUBPLAN files
- `execution/` - EXECUTION_TASK files
- `summary/` - Completion summaries

**See**: Each archive folder contains an `INDEX.md` with complete file listing.

---

## 🔍 How to Use This Index

### Finding Files by Type

**Need a template?**
→ Look in "Templates" section above
→ Location: `LLM/templates/`

**Need a protocol?**
→ Look in "Protocols" section above
→ Location: `LLM/protocols/`

**Looking for a script?**
→ Look in "Scripts" section above
→ Location: `LLM/scripts/<domain>/`

**Need a guide?**
→ Look in "Guides" section above
→ Location: `LLM/guides/`

### Finding Files by Purpose

**Starting new work?**
→ `LLM/protocols/IMPLEMENTATION_START_POINT.md`
→ `LLM/templates/PROMPTS.md` (predefined prompts)

**Resuming paused work?**
→ `LLM/protocols/IMPLEMENTATION_RESUME.md`
→ `LLM/templates/PROMPTS.md` (resume prompts)

**Completing work?**
→ `LLM/protocols/IMPLEMENTATION_END_POINT.md`

**Managing context?**
→ `LLM/guides/FOCUS-RULES.md`
→ `LLM/guides/CONTEXT-MANAGEMENT.md`

**Working with multiple PLANs?**
→ `LLM/guides/MULTIPLE-PLANS-PROTOCOL.md`

**Creating large initiatives?**
→ `LLM/guides/GRAMMAPLAN-GUIDE.md`

### Quick Search

Use Cmd+F (Mac) or Ctrl+F (Windows/Linux) to search this document for:
- File names
- Keywords (e.g., "validation", "archiving", "template")
- Purposes (e.g., "start", "resume", "complete")

---

## 🔄 Update Process

**When to Update**:
- New files added to LLM/ directory
- Files moved or renamed
- New scripts created
- New templates or protocols added

**How to Update** (Manual for Quick Wins):
1. Add new files to appropriate section
2. Update summary statistics
3. Update "Last Updated" date at top
4. Keep sections organized alphabetically or by purpose

**Future**: Search tool (see `PLAN_FILE-MOVING-ADVANCED-OPTIMIZATION.md`) will automate file discovery and eliminate need for manual index updates.

---

## 📖 Related Documentation

- `LLM-METHODOLOGY.md` - Main methodology document
- `LLM/README.md` - LLM folder navigation
- `LLM/templates/PROMPTS.md` - Predefined prompts ⭐
- `LLM/QUICK-START.md` - Getting started guide

---

**Index Version**: 1.0  
**Created**: 2025-01-27  
**Maintained By**: Manual updates (until search tool implemented)


