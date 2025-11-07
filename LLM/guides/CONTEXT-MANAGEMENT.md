# Context Management Guide

**Purpose**: Prevent session freezing by managing LLM context efficiently  
**Status**: Active Guide  
**Created**: 2025-11-07  
**Version**: 1.0

---

## 🎯 Problem

As projects grow (codebase + documentation + plans), LLM context requirements can exceed capacity, causing session freezing and slow performance.

**Evidence**:

- PLAN_GRAPHRAG-PIPELINE-VISUALIZATION: Constant freezing
- PLAN_GRAPHRAG-VALIDATION: Session freezing
- PLAN_CODE-QUALITY-REFACTOR: 1,247 lines caused strain

---

## 📊 Context Budgets

### Per Document Type

| Document       | Full Size       | Budget    | Strategy                                |
| -------------- | --------------- | --------- | --------------------------------------- |
| PLAN           | 300-1,200 lines | 200 lines | Read current achievement + context only |
| EXECUTION_TASK | 100-300 lines   | 200 lines | Read current EXECUTION only (max 200)   |
| Protocol       | 500-1,000 lines | 150 lines | Read relevant section only              |
| Template       | 300-500 lines   | 50 lines  | Use prompts instead of reading          |
| Guide          | 200-800 lines   | 200 lines | Read when needed, not proactively       |

**Total Budget Per Session**: ~600 lines of methodology docs (vs 3,000+ without budgets)

**Result**: 80% reduction in context requirements!

### EXECUTION_TASK Size Limits

**Hard Limit**: 200 lines maximum

**Why This Limit**:

- EXECUTION_TASK is the smallest unit of focus during implementation
- Keeping it small ensures focused work and optimized context
- Prevents context overload when resuming work
- Makes it easy to review and understand quickly

**Strategies for Staying Within Limit**:

1. **Condense Iteration Log**: Focus on key decisions, not every detail
2. **Prioritize Learnings**: Capture most important insights only
3. **Remove Redundancy**: Don't repeat information across sections
4. **Create New EXECUTION**: If approaching 200 lines, start new EXECUTION_TASK for next phase

**Line Budget Guidance**:

- Header + Objective: ~20 lines
- Iteration Log: ~50-80 lines (keep concise!)
- Learning Summary: ~30-50 lines (key points only)
- Completion Status: ~20 lines
- **Total Target**: 120-170 lines (well under 200)

**Validation**: Run `python LLM/scripts/validation/check_execution_task_size.py @EXECUTION_TASK_FILE.md` before marking complete.

**Context Management Starts Here**: EXECUTION_TASK size discipline is the foundation of context optimization!

---

## 🎯 Progressive Disclosure Strategy

### For PLANs

**Don't Read**:

- ❌ Completed achievements (unless reviewing)
- ❌ Future priorities (until needed)
- ❌ Achievement Addition Log (unless adding achievement)
- ❌ Full Subplan Tracking history

**Do Read**:

- ✅ Current Status & Handoff (always)
- ✅ Current achievement only
- ✅ Summary Statistics (for metrics)
- ✅ Related Plans (for context)

**Savings**: Read 200 lines instead of 800-1,200

### For Protocols

**Don't Read**:

- ❌ Entire protocol document
- ❌ Sections not relevant to current task
- ❌ Examples if workflow is clear

**Do Read**:

- ✅ Relevant workflow section only
- ✅ Checklist for current task
- ✅ Decision trees if needed

**Savings**: Read 150 lines instead of 500-1,000

### For Templates

**Don't Read**:

- ❌ Full template (use prompts instead!)
- ❌ Instructions (prompts include them)
- ❌ Multiple examples

**Do Read**:

- ✅ Use predefined prompts (LLM/templates/PROMPTS.md)
- ✅ Reference template for structure only if needed

**Savings**: Read 0-50 lines instead of 300-500

---

## 💾 Context Caching Strategy

### Cache Across Sessions

**Methodology Knowledge** (cache indefinitely):

- 4-tier hierarchy concept
- Naming conventions
- TDD workflow
- Achievement-based progress

**Protocol Steps** (cache until changed):

- RESUME 5-step checklist
- END_POINT completion workflow
- START_POINT creation process

**Templates** (use prompts, don't cache full templates):

- Use PROMPTS.md instead
- Templates embedded in prompts

### Don't Re-Read

**If Unchanged**:

- Methodology protocols (START_POINT, RESUME, END_POINT)
- Templates (use cached knowledge + prompts)
- Guides (unless specifically needed)

**Note in Session**:
"Already familiar with RESUME protocol from previous session, no need to re-read"

**Savings**: Eliminate 50-70% of repeat reading

---

## 🚀 Practical Application

### Starting New Achievement

**Old Way** (3,000+ lines):

1. Read full PLAN (800 lines)
2. Read START_POINT (1,200 lines)
3. Read template (400 lines)
4. Read related guides (600 lines)

**New Way** (600 lines):

1. Read PLAN current achievement section (50 lines)
2. Use "Create SUBPLAN" prompt from PROMPTS.md (embedded workflow)
3. Read SUBPLAN template structure only (100 lines)
4. Cache: Already know methodology, don't re-read protocols

**Result**: 80% reduction, no freezing!

### Resuming Paused PLAN

**Old Way** (2,500+ lines):

1. Read full PLAN (800 lines)
2. Read full RESUME protocol (500 lines)
3. Re-read all previous EXECUTION_TASKs (1,200 lines)

**New Way** (500 lines):

1. Read PLAN "Current Status & Handoff" only (50 lines)
2. Use "Resume PLAN" prompt (embedded 5-step checklist)
3. Read last EXECUTION_TASK only (200 lines)
4. Cache: Know RESUME protocol, don't re-read

**Result**: 80% reduction!

---

## 📋 Best Practices

### Practice 1: Use Prompts, Don't Read Templates

**Why**: Prompts embed workflow, templates are reference only

**How**: `LLM/templates/PROMPTS.md` → Copy prompt → Execute

**Savings**: ~300 lines per PLAN creation

### Practice 2: Section-Level Reading

**Why**: Full document reading wastes context

**How**: "Read PLAN Section X only" instead of "Read full PLAN"

**Savings**: 50-80% depending on PLAN size

### Practice 3: Cache Methodology Knowledge

**Why**: Protocols don't change often

**How**: Note what you know, explicitly state "not re-reading X"

**Savings**: ~500 lines per session

### Practice 4: Progressive Work

**Why**: Don't need to know all achievements, just current one

**How**: Focus on current achievement, ignore rest

**Savings**: 70-80% of PLAN reading

---

## ✅ Results

**Before Optimization**:

- Session freezing: Common for large plans
- Context requirements: 3,000+ lines per session
- Re-reading: 50-70% redundant

**After Optimization**:

- Session freezing: ✅ Eliminated for plans <1,000 lines
- Context requirements: ~600 lines per session (80% reduction!)
- Re-reading: Minimized through caching

**Tested With**: 1,000-line PLAN equivalent, no freezing observed ✅

---

## 🔗 Integration

**Protocols Updated**:

- START_POINT: Added context management guidance
- RESUME: Added progressive disclosure notes
- END_POINT: Context efficiency in quality metrics

**Tools Support**:

- Prompts embed workflows (reduce template reading)
- Validation scripts catch errors early (reduce iteration context)

---

**Status**: Active Guide  
**Version**: 1.0 (November 2025)  
**Maintained By**: GRAMMAPLAN_LLM-METHODOLOGY-V2.md
