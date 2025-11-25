# Implementation Start Point

**Purpose**: Entry point for all new work using structured LLM development methodology  
**Status**: Foundation Document - Permanent Reference  
**Last Updated**: November 9, 2025 (Designer/Executor phase separation added)

---

## 🎯 What This Document Is

**You're here because**:

- You want to start new work in this project
- You need to create a PLAN, SUBPLAN, or EXECUTION_TASK
- You want to understand the structured development methodology

**What you'll get**:

- Complete guide to the three-tier hierarchy (PLAN → SUBPLAN → EXECUTION_TASK)
- How to create each document type
- Test-driven development workflow
- Circular debugging prevention
- Everything you need to start and execute work

**This document is self-contained**: You shouldn't need anything else to get started.

---

## 📐 The Structured Methodology - Overview

### Four-Tier Hierarchy (with GrammaPlan)

```
GRAMMAPLAN (orchestrates large initiatives - optional)
  ├─ Coordinates multiple related PLANs
  ├─ Strategic-level goals (>80 hours, 3+ domains)
  ├─ Tracks child PLAN completion
  ├─ Minimal content (~200-300 lines)
  └─ See "When to Use GrammaPlan" section below
      ↓
PLAN (defines WHAT - the achievements)
  ├─ Lists priority-ordered achievements
  ├─ Self-contained (LLM can execute from PLAN alone)
  ├─ Dynamic (can add achievements during execution)
  ├─ May reference parent GrammaPlan
  └─ Tracks subplans created
      ↓
SUBPLAN (defines HOW - the approach)
  ├─ Created on-demand when tackling an achievement
  ├─ Specific approach for one achievement
  ├─ Static once created (doesn't change)
  ├─ Can have multiple EXECUTION_TASKs
  └─ References mother PLAN
      ↓
EXECUTION_TASK (logs execution - the journey)
  ├─ Dynamic log of all attempts
  ├─ Updated after every iteration
  ├─ Tracks what worked, what didn't
  ├─ Captures learnings
  ├─ Multiple per SUBPLAN possible (different attempts)
  └─ References SUBPLAN and PLAN
```

### Document Types

1. **GRAMMAPLAN**: Orchestrates multiple PLANs (optional - for large initiatives)
2. **PLAN**: What needs to be achieved (achievements list)
3. **SUBPLAN**: How you'll tackle one achievement (your approach)
4. **EXECUTION_TASK**: Log of execution (iteration diary)

**Not separate types**:

- CIRCULAR_DEBUG is an EXECUTION_TASK variant
- Plan updates/refinements are also execution work (can be tracked)

### Naming Convention

**Pattern**: `TYPE_FEATURE_NUMBER.md`

#### Core Document Types

- **GRAMMAPLAN**: `GRAMMAPLAN_<FEATURE>.md` (e.g., `GRAMMAPLAN_CODE-QUALITY.md`)
  - For large initiatives (>80 hours, 3+ domains)
  - Orchestrates multiple child PLANs
  - See "When to Use GrammaPlan" section below
- **PLAN**: `PLAN_<FEATURE>.md` (e.g., `PLAN_OPTIMIZE-EXTRACTION.md`)
  - **Location**: `work-space/plans/PLAN_<FEATURE>.md`
  - Child PLANs under GrammaPlan: `PLAN_<GRAMMAPLAN-NAME>-<DOMAIN>.md`
  - Example: `work-space/plans/PLAN_CODE-QUALITY-GRAPHRAG.md` (child of GRAMMAPLAN_CODE-QUALITY)
- **SUBPLAN**: `SUBPLAN_<FEATURE>_<NUMBER>.md` (e.g., `SUBPLAN_OPTIMIZE-EXTRACTION_01.md`)
  - **Location**: `work-space/subplans/SUBPLAN_<FEATURE>_<NUMBER>.md`
- **EXECUTION_TASK**: `EXECUTION_TASK_<FEATURE>_<SUBPLAN>_<EXECUTION>.md`
  - **Location**: `work-space/execution/EXECUTION_TASK_<FEATURE>_<SUBPLAN>_<EXECUTION>.md`
  - Example: `work-space/execution/EXECUTION_TASK_OPTIMIZE-EXTRACTION_01_01.md` (first execution of subplan 01)
  - Example: `work-space/execution/EXECUTION_TASK_OPTIMIZE-EXTRACTION_01_02.md` (second execution - new strategy)
- **EXECUTION_ANALYSIS**: `EXECUTION_ANALYSIS_<TOPIC>.md` (for analysis work that isn't execution tracking)
  - Example: `EXECUTION_ANALYSIS_METHODOLOGY-REVIEW.md` (performance review/post-mortem)
  - Example: `EXECUTION_ANALYSIS_ENTITY-RESOLUTION-BUGS.md` (critical analysis)
  - Use for: post-mortems, reviews, investigations, cross-cutting analysis
  - Does NOT track iterations (use EXECUTION_TASK for that)

#### ❌ NEVER Create These (Common Mistakes)

These should be **sections**, not files:

- ❌ `PLAN_UPDATE_<FEATURE>.md` → Update the PLAN itself (add section)
- ❌ `<FEATURE>-STATUS.md` → Section in PLAN "Current Status & Handoff"
- ❌ `<FEATURE>-SUMMARY.md` → Section in parent document or EXECUTION*ANALYSIS*
- ❌ `<FEATURE>-COMPLIANCE.md` → Section in PLAN or EXECUTION*ANALYSIS*
- ❌ `<FEATURE>-INSIGHTS.md` → Section in EXECUTION*ANALYSIS*
- ❌ `<FEATURE>-REVIEW.md` → Section or use EXECUTION*ANALYSIS*
- ❌ `MILESTONE_*.md` → Section in PLAN
- ❌ `FEEDBACK_*.md` → Section in PLAN or EXECUTION_TASK
- ❌ `RESUME_*.md` → Just resume, don't create file (use IMPLEMENTATION_RESUME.md)

**Golden Rule**: If it's about ONE specific PLAN/SUBPLAN/EXECUTION, put it IN that document as a section, not a separate file.

**Feature Name Rules**:

- Use kebab-case (hyphens)
- Keep short (2-4 words)
- Be specific and actionable
- Same across all documents for one feature

---

## 🌳 When to Use GrammaPlan

**GrammaPlan** = GrandMotherPlan = Orchestration document for large initiatives

### Decision Criteria

Use GrammaPlan when **TWO OR MORE** of these apply:

1. **Size**: PLAN would exceed 800 lines
2. **Duration**: Estimated effort > 80 hours
3. **Domains**: Work spans 3+ distinct domains/areas
4. **Achievements**: > 20 achievements in single PLAN
5. **Parallelism**: Natural opportunities for parallel work
6. **Context**: Medium-context model deployment
7. **Long timeline**: Multi-month project

### Quick Decision Tree

```
Is your planned work large/complex?
├─ No (< 500 lines, < 40 hours, < 15 achievements)
│   └─ Use: Single PLAN
│
└─ Yes → Check indicators:
    ├─ PLAN draft is >800 lines? → GrammaPlan RECOMMENDED
    ├─ Estimated >80 hours? → GrammaPlan RECOMMENDED
    ├─ Spans 3+ distinct domains? → GrammaPlan RECOMMENDED
    ├─ Natural parallelism? → GrammaPlan BENEFICIAL
    └─ Medium-model context strain? → GrammaPlan RECOMMENDED
```

### When to Use Single PLAN (Not GrammaPlan)

- Focused, single-domain work
- < 40 hours estimated
- Clear linear progression
- Tight integration required
- Small team (1-2 people)
- Urgent work

### GrammaPlan Benefits

**For Large Work**:
- Reduces per-document size by 75% (1200 lines → 200-300 per child)
- Better for medium-context models
- Enables parallel work streams
- Clearer progress tracking

**Example**: PLAN_CODE-QUALITY-REFACTOR at 1,247 lines could split into:
- GRAMMAPLAN_CODE-QUALITY (~200 lines)
- 6 child PLANs (~200-300 lines each)
- Result: 75% reduction in context per session

### How to Create GrammaPlan

1. **Identify need** (use decision criteria above)
2. **Analyze natural divisions** (domains? phases? components?)
3. **Create GrammaPlan** (use `LLM/templates/GRAMMAPLAN-TEMPLATE.md`)
4. **Create child PLANs** (use `LLM/templates/PLAN-TEMPLATE.md`)
5. **Update ACTIVE_PLANS.md** (add GrammaPlan + children)
6. **Execute** (work on one child at a time, unless coordinating parallel)

### Key Principle

**GrammaPlan is LEAN**: Keep it ~200-300 lines max. Do NOT replicate child PLAN content. Focus on:
- Strategic goal
- Child PLAN tracking
- Dependencies between children
- Success criteria (typically "all children complete")

### Full Guide

See `LLM/guides/GRAMMAPLAN-GUIDE.md` for comprehensive guide including:
- Decomposition patterns (Domain, Phase, Hybrid)
- Progress tracking formulas
- Integration strategies
- Best practices and examples

---

## 📝 How to Create a PLAN

### When to Create a PLAN

Create a PLAN when:

- Starting significant new work (>10 hours estimated)
- Work has multiple distinct parts (achievements)
- Work needs coordination or phasing
- Work affects multiple areas of codebase

**Don't create a PLAN for**:

- Small fixes (<4 hours)
- Single-file changes
- Well-defined small features
  → Instead: Create SUBPLAN directly or just do the work

### PLAN Structure

**Required Sections** (in order):

1. **Header**:

   ```markdown
   # PLAN: [Feature Name]

   **Status**: Planning / In Progress / Complete
   **Created**: [date]
   **Goal**: [One sentence]
   **Priority**: Critical / High / Medium / Low
   ```

2. **Context for LLM Execution**:

   - What this plan is
   - Your task
   - How to proceed
   - What you'll create
   - Self-contained instructions

3. **Goal** (1 paragraph): What we're building and why

4. **Problem Statement** (2-3 paragraphs): Current state, what's wrong, impact

5. **Success Criteria**:

   - Must have (required)
   - Should have (important)
   - Nice to have (bonus)

6. **Scope Definition**:

   - In scope (what we'll do)
   - Out of scope (what we won't)

7. **Desirable Achievements** (priority-ordered):

   - **Achievement X.Y**: [Title]
   - Description
   - Success criteria
   - Effort estimate
   - **Can include sub-achievements** (hierarchical)

8. **Achievement Addition Log** (if achievements added during execution):

   ```markdown
   **Achievement X.Y** (Added: [date])

   - Why: [Gap discovered]
   - Discovered In: [EXECUTION_TASK]
   ```

9. **Subplan Tracking** (updated during execution):

   ```markdown
   - SUBPLAN_XX: [Achievement] - Status
     └─ EXECUTION_TASK_XX_YY: Status
   ```

10. **Constraints**: Technical, time, resource

11. **References**: Related docs, code, archives

**Template**: `LLM/templates/PLAN-TEMPLATE.md` (when created)

**Before Creating PLAN**: Check `ACTIVE_PLANS.md` for related PLANs and dependencies. See `LLM/guides/MULTIPLE-PLANS-PROTOCOL.md` for managing multiple PLANs.

### Strategic Decision Support with EXECUTION_ANALYSIS

**When facing complex decisions during planning**, consider creating an EXECUTION_ANALYSIS document to:

- Analyze blockers or methodology gaps
- Investigate quality issues or bugs
- Review process effectiveness
- Evaluate multiple solution options
- Document root cause analysis

**When to Create EXECUTION_ANALYSIS**:

- **Blockers**: Work is blocked and root cause needs investigation
- **Methodology Gaps**: Process or workflow issues discovered
- **Quality Issues**: Performance, correctness, or reliability problems
- **Strategic Decisions**: Multiple approaches to evaluate
- **Post-Mortems**: Understanding what went wrong/right

**Quick Decision Tree**:

```
Facing complex decision or issue?
├─ Is it blocking work? → Create EXECUTION_ANALYSIS
├─ Multiple solutions to evaluate? → Create EXECUTION_ANALYSIS
├─ Need root cause analysis? → Create EXECUTION_ANALYSIS
├─ Process/methodology issue? → Create EXECUTION_ANALYSIS
└─ Simple, clear path forward? → Proceed with PLAN
```

**Templates Available**:

- `LLM/templates/EXECUTION_ANALYSIS-METHODOLOGY-REVIEW-TEMPLATE.md` - For methodology reviews
- `LLM/templates/EXECUTION_ANALYSIS-PLANNING-STRATEGY-TEMPLATE.md` - For strategic planning decisions
- See `LLM-METHODOLOGY.md` → "EXECUTION_ANALYSIS Documents" section for all categories

**Archive Location**: `documentation/archive/execution-analyses/` (organized by category and date)

**Reference**: See `LLM-METHODOLOGY.md` for complete EXECUTION_ANALYSIS workflow and categorization.

### Create Archive Folder & Feedback System at Plan Start

**⚠️ CRITICAL**: Create archive folder AND feedback system structure immediately when creating PLAN.

**Steps**:

1. **Determine Archive Location**:
   - Default: `./feature-archive/` (replace `feature` with your feature name)
   - Example: `./methodology-v2-enhancements-archive/`
   - Document in PLAN "Archive Location" section

2. **Create Archive Structure**:
   ```bash
   mkdir -p ./feature-archive/subplans
   mkdir -p ./feature-archive/execution
   mkdir -p ./feature-archive/documentation
   ```

3. **Create Feedback System Structure** (**NEW - Filesystem-First Architecture**):
   ```bash
   mkdir -p work-space/plans/[FEATURE]/execution/feedbacks
   ```
   - This is where `APPROVED_XX.md` and `FIX_XX.md` files will be created
   - Achievement completion tracked via files in this folder (not PLAN markdown)

4. **Document in PLAN**:
   - Add "Archive Location" section to PLAN
   - Reference: `LLM/templates/PLAN-TEMPLATE.md` "Archive Location" section

**Why Archive Folder**: Archive folder must exist before work starts so completed SUBPLANs and EXECUTION_TASKs can be immediately archived.

**Why Feedback System Folder**: Filesystem-first architecture requires `execution/feedbacks/` folder for APPROVED/FIX files that track achievement completion status (replaces markdown-based completion tracking).

**Folder Structure** (Complete):
```
work-space/plans/[FEATURE]/
├── PLAN_[FEATURE].md
├── subplans/
│   └── SUBPLAN_[FEATURE]_XX.md
├── execution/
│   ├── EXECUTION_TASK_[FEATURE]_XX_YY.md
│   └── feedbacks/              ← NEW! Filesystem-first state tracking
│       ├── APPROVED_01.md       (Achievement 0.1 complete)
│       ├── APPROVED_02.md       (Achievement 0.2 complete)
│       └── FIX_03.md           (Achievement 0.3 needs fixes)
└── documentation/
    └── (supporting docs)
```

**Result**: Clean root directory, active work in workspace (`work-space/`), completed work archived to `documentation/archive/`, achievement completion tracked via filesystem (`execution/feedbacks/`).

**Reference**: See `LLM/docs/FEEDBACK_SYSTEM_GUIDE.md` for complete feedback system guidance.

---

## 🔄 Working with Multiple PLANs

**When This Applies**:

- 2+ PLANs active/paused simultaneously
- Dependencies exist between PLANs
- Context switching between features
- Overlapping code concerns

**Before Creating a New PLAN**:

1. **Check ACTIVE_PLANS.md**:

   - Are there related PLANs?
   - Do any PLANs touch same code?
   - Are there existing dependencies?

2. **Review Existing PLANs**:

   - Read "Related Plans" sections
   - Check for code overlaps
   - Identify dependencies

3. **Document Dependencies**:
   - Add "Related Plans" section to new PLAN
   - Use format from `LLM/guides/MULTIPLE-PLANS-PROTOCOL.md`
   - Document dependency type (Hard/Soft/Data/Code/Sequential)

**Key Rules**:

- Only **ONE PLAN** should be "🚀 In Progress" at a time
- Check dependencies before starting work
- Update dependent PLANs when prerequisites complete
- Coordinate if code conflicts exist

**Complete Guide**: See `LLM/guides/MULTIPLE-PLANS-PROTOCOL.md` for:

- Dependency types and tracking
- Context switching workflow
- Decision trees
- Coordination strategies
- Real-world examples

---

### Common Mistakes to Avoid

**❌ Don't**:

- List prescriptive subplans (SUBPLAN_01, SUBPLAN_02...) ← Common mistake!
- Describe HOW to implement (that's for SUBPLANs)
- Pre-populate everything (plans are dynamic)
- Create separate update/status files (edit PLAN directly)

**✅ Do**:

- List achievements (WHAT needs to exist)
- Make it self-contained (LLM can execute from PLAN alone)
- Update PLAN directly as you learn
- Add achievements if gaps discovered
- Track subplans as they're created

### Meta-Insight: Plan Creation is Iterative

**Learned from creating PLAN_STRUCTURED-LLM-DEVELOPMENT.md**:

- Creating a PLAN involves iterations and feedback
- Complex PLANs may need EXECUTION tracking
- Example: `EXECUTION_PLAN-CREATION_<FEATURE>_01.md`
- Captures: feedback received, changes made, learnings

---

## 📝 How to Create a SUBPLAN

### When to Create a SUBPLAN

Create a SUBPLAN when:

- You've selected an achievement from a PLAN to work on
- You have a specific approach in mind
- You want to define what you'll do before doing it

**Process**:

1. Read PLAN and review achievements
2. Select achievement to tackle
3. Decide your approach
4. Create SUBPLAN with your approach
5. Create EXECUTION_TASK and start work

### SUBPLAN Structure

**Required Sections**:

1. **Header**:

   ```markdown
   # SUBPLAN: [Brief Title]

   **Mother Plan**: PLAN\_<FEATURE>.md
   **Achievement Addressed**: Achievement X.Y
   **Status**: Not Started / In Progress / Complete
   **Created**: [date]
   **Estimated Effort**: [hours]
   ```

2. **Objective** (1 paragraph):

   - What this subplan achieves
   - How it contributes to mother plan

3. **What Needs to Be Created**:

   - Files to create/modify
   - Functions/classes to add/modify
   - Specific deliverables

4. **Approach**:

   - Your strategy
   - Key steps
   - Method/technique

5. **Tests Required** (if applicable):

   - Test file to create
   - Test cases to cover
   - Test-first requirement

6. **Expected Results**:

   - Functional changes
   - Observable outcomes
   - Success indicators

7. **Dependencies**:

   - Other subplans needed first
   - External dependencies
   - Prerequisites

8. **Execution Task Reference**:
   - Link to EXECUTION_TASK (when created)
   - Can have multiple EXECUTIONs

**Template**: `LLM/templates/SUBPLAN-TEMPLATE.md` (when created)

### Key Concepts

**Static Document**: SUBPLAN doesn't change once created

- Defines the approach
- The "assignment"
- The "what to do"

**Multiple Executions**: One SUBPLAN can have multiple EXECUTION_TASKs

- First attempt: EXECUTION*TASK*<FEATURE>\_01_01.md
- If circular debug: EXECUTION*TASK*<FEATURE>\_01_02.md (new strategy)
- All tracked and archived

**Creation Can Be Iterative**: If SUBPLAN is complex:

- You can track its creation with an EXECUTION_TASK
- Capture feedback and iterations
- Refine the approach before executing

---

## 🔄 How to Create an EXECUTION_TASK

### When to Create an EXECUTION_TASK

Create EXECUTION_TASK when:

- Starting work on a SUBPLAN
- Starting a new attempt (after circular debugging)
- Any iterative LLM work (even plan/subplan creation if complex)

**One SUBPLAN → One or More EXECUTION_TASKs**

### Two EXECUTION Patterns

**Pattern 1: EXECUTION_TASK** (subplan work):

- Name: `EXECUTION_TASK_<FEATURE>_<SUBPLAN>_<EXECUTION>.md`
- Used when: Executing a specific SUBPLAN
- Tied to: A SUBPLAN
- Example: `EXECUTION_TASK_OPTIMIZE-EXTRACTION_01_01.md`

**Pattern 2: EXECUTION** (plan-level work):

- Name: `EXECUTION_<TYPE>_<FEATURE>_<NUMBER>.md`
- Used when: Work at plan level, not subplan-specific
- Types: PLAN-CREATION, FEEDBACK-INTEGRATION, ANALYSIS, REVIEW
- Examples:
  - `EXECUTION_PLAN-CREATION_STRUCTURED-LLM-DEVELOPMENT_01.md`
  - `EXECUTION_FEEDBACK-INTEGRATION_OPTIMIZE-EXTRACTION_01.md`

**Both are valid!** Use appropriate pattern for your work type.

### EXECUTION_TASK Structure

**Required Sections**:

1. **Header**:

   ```markdown
   # EXECUTION_TASK: [Brief Title]

   **Subplan**: SUBPLAN*<FEATURE>\_XX.md
   **Mother Plan**: PLAN*<FEATURE>.md
   **Achievement**: [Which achievement]
   **Execution Number**: XX (first attempt, second attempt, etc.)
   **Previous Execution**: [Link if 2nd+ attempt]
   **Circular Debug Flag**: Yes/No
   **Started**: [date]
   **Status**: In Progress / Complete / Abandoned / Blocked
   **Total Iterations**: [updated after each]
   ```

2. **Test Creation Phase** (if applicable):

   - Tests written (list)
   - Test file created
   - Initial test run (should fail)

3. **Iteration Log** (updated after EVERY iteration):

   ```markdown
   ### Iteration N

   **Date**: [timestamp]
   **Test Run**: [results]
   **Error**: [exact error if failed]
   **Root Cause**: [deep analysis]
   **Fix Applied**: [file:line - what changed]
   **Learning**: [generalizable insight]
   **Code Comments**: [Yes/No - where]
   **Progress**: [New error / Same error / Passed]
   ```

4. **Circular Debugging Check** (every 3 iterations):

   - Pattern detected: Yes/No
   - Same error count
   - Decision: Continue / Change Strategy

5. **Learning Summary**:

   - Technical learnings
   - Process learnings
   - Mistakes and recoveries

6. **Code Comment Map**:

   - file.py:123 (Iteration 2): [comment summary]

7. **Future Work Discovered**:

   - Ideas out of scope
   - Add to backlog during completion

8. **Completion Status**:
   - Tests passing: Yes/No
   - Code commented: Yes/No
   - Objectives met: Yes/No
   - Result: Success / Abandoned / Blocked
   - Ready for archive: Yes/No

**Template**: `LLM/templates/EXECUTION_TASK-TEMPLATE.md` (when created)

### Key Concepts

**Dynamic Document**: Grows with every iteration
**Iteration Discipline**: Update after EVERY iteration, no exceptions
**Circular Debug Detection**: Check every 3 iterations for same error
**Multiple per SUBPLAN**: Normal if first approach doesn't work

### When Circular Debugging Detected

**Process**:

1. After iteration N, same error as iteration N-3
2. STOP implementing
3. Mark current EXECUTION_TASK as "Abandoned - Circular Debug"
4. Create new EXECUTION*TASK*<FEATURE>_<SUBPLAN>_<NEXT>.md
5. In new header, note: "Strategy change after circular debug"
6. Analyze pattern: why stuck?
7. Define fundamentally different approach
8. Start fresh iterations in new EXECUTION_TASK
9. Archive both (shows the journey)

---

## 🌳 Dynamic Achievement Management

### Adding Achievements During Execution

**When**:

- Gap discovered during EXECUTION_TASK
- New requirement emerges
- Dependency identified

**Process**:

1. Note in EXECUTION_TASK: "Gap discovered - need Achievement X.Y"
2. Update PLAN's "Achievement Addition Log"
3. Add new achievement with priority
4. Continue or create new SUBPLAN for new achievement

### Sub-Achievements

**Hierarchical Structure**:

```
Achievement 1: Foundation Documents
  ├─ Achievement 1.1: Entry Point Exists
  │   ├─ Achievement 1.1.1: PLAN creation process defined
  │   └─ Achievement 1.1.2: SUBPLAN creation process defined
  └─ Achievement 1.2: Exit Point Exists
```

**When to Use**:

- Main achievement breaks down into logical parts
- Sub-achievements discovered during execution
- Helps organize complex achievements

---

## 🧪 Test-Driven Development Workflow

### Core Principles

1. **Test First** - Always write tests before implementation
2. **Never Cheat** - Fix implementation, not tests
3. **Document Every Iteration** - No iteration goes untracked
4. **Learn from Failures** - Each failure teaches something
5. **Comment Learnings** - Add to code as comments

### The TDD Cycle

```
1. Create SUBPLAN (define what to do)
   ↓
2. Create EXECUTION_TASK (start logging)
   ↓
3. Write Tests (define success)
   ↓
4. Run Tests (should fail)
   ↓
5. Implement (make minimal change)
   ↓
6. Run Tests (pass or new error)
   ↓
7. Document Iteration (in EXECUTION_TASK)
   ↓
8. Check Progress (new error or same?)
   ↓
9. Repeat 5-8 until tests pass
   ↓
10. Add Learnings to Code (as comments)
   ↓
11. Complete SUBPLAN
```

### Iteration Documentation

**After EVERY iteration**:

```markdown
### Iteration N

**Date**: [timestamp]
**Error**: [exact message]
**Why**: [root cause - not surface reason]
**Fix**: [what changed - file:line]
**Learning**: [generalizable insight]
**Progress**: New Error / Same Error / Passed
```

**Critical**: If "Learning" is empty or generic, you didn't learn enough. Dig deeper.

---

## 🚫 Preventing Circular Debugging

### What Is Circular Debugging?

**Symptoms**:

- Same error 3+ times
- No new learnings
- Random changes without understanding
- Temptation to modify tests

### Detection

**Every 3 Iterations**:

```
Check: Is current error == error from 3 iterations ago?

YES → Circular debugging detected
  ├─ STOP implementing
  ├─ Analyze pattern
  ├─ Change strategy
  └─ Create new EXECUTION_TASK

NO → Making progress, continue
```

### Recovery Process

**When Circular Debugging Detected**:

1. **STOP** - Don't make more changes
2. **Mark Current EXECUTION_TASK**: "Abandoned - Circular Debug after iteration X"
3. **Analyze**:
   - What have we tried?
   - Why did each attempt fail?
   - What's the common pattern?
   - What are we missing/misunderstanding?
4. **Change Strategy**:
   - New approach (fundamentally different)
   - Different angle
   - Request human guidance
5. **Create New EXECUTION_TASK**:
   - Name: `EXECUTION_TASK_<FEATURE>_<SUBPLAN>_<NEXT>.md`
   - Header notes: "Strategy change after circular debug"
   - References previous EXECUTION_TASK
   - Explains what changed
6. **Start Fresh**: New iterations in new EXECUTION_TASK

**Both EXECUTION_TASKs archived**: Shows the learning journey

---

## 🎓 Learning Capture

### In Code Comments

**Pattern**:

```python
def function():
    \"\"\"
    IMPLEMENTATION NOTE (from testing):
    - Initially tried X (iteration 1), failed because Y
    - Switched to Z which handles edge case A

    LEARNED (iteration 3): Must validate before processing
    \"\"\"

    # LEARNED: Special case requires explicit check (iteration 5)
    if special_case:
        return handle_special()

    return process_normal()
```

**When to Add**:

- After discovering something non-obvious
- After fixing a tricky bug
- After changing approach
- After every significant learning

**What to Capture**:

- What we learned
- Why it matters
- Which iteration taught us
- Reference to test if applicable

### In Documentation

**In EXECUTION_TASK**:

- Every iteration has "Learning" section
- Aggregated in "Learning Summary"

**In PLAN/SUBPLAN**:

- Meta-learning sections
- Common mistakes
- Insights from execution

---

## 🛠️ Templates and Tools

### Templates

**Location**: `LLM/templates/` (when created)

**Available Templates**:

- `PLAN-TEMPLATE.md` - How to create a PLAN
- `SUBPLAN-TEMPLATE.md` - How to create a SUBPLAN
- `EXECUTION_TASK-TEMPLATE.md` - How to create an EXECUTION_TASK

**Usage**: Copy template, fill in sections, reference examples

### Validation Tools

**Location**: `scripts/` (when created)

**Tools**:

- `validate_documents.py` - Check naming, structure
- `generate_from_template.py` - Interactive document creation
- `aggregate_learnings.py` - Extract insights from EXECUTION_TASKs

---

## 📚 Examples

### Example PLAN

**See**: `PLAN_STRUCTURED-LLM-DEVELOPMENT.md` (this methodology itself!)

**What it shows**:

- Achievement-based structure (not prescriptive subplans)
- Self-contained LLM execution context
- Dynamic achievement additions
- Subplan tracking
- Meta-learning from creating itself

### Example SUBPLAN

**See**: `SUBPLAN_STRUCTURED-LLM-DEVELOPMENT_01.md` (creating this document!)

**What it shows**:

- References mother PLAN
- Specific approach defined
- Expected results listed
- Will have EXECUTION_TASK

### Example EXECUTION_TASK

**See**: `EXECUTION_TASK_STRUCTURED-LLM-DEVELOPMENT_01_01.md`

**What it shows**:

- Iteration logging
- Learning capture
- Progress tracking

---

## 🎯 Quick Decision Trees

### Should I Create a PLAN or SUBPLAN?

```
Is the work significant (>10 hours) with multiple parts?
  YES → Create PLAN
  NO ↓

Is there an existing PLAN this fits into?
  YES → Create SUBPLAN for that PLAN
  NO → Create SUBPLAN directly (small, standalone work)
```

### Should I Create New SUBPLAN or New EXECUTION_TASK?

```
Am I starting work on a new achievement?
  YES → Create new SUBPLAN
  NO ↓

Am I continuing work on existing SUBPLAN?
  Is first attempt still viable?
    YES → Continue current EXECUTION_TASK
    NO (circular debug) → Create new EXECUTION_TASK (new strategy)
```

### Should I Add Achievement or Create New PLAN?

```
Is this related to current PLAN's goal?
  YES → Add achievement to current PLAN
  NO → Create new PLAN

Is this high priority?
  YES → Add as high-priority achievement
  NO → Add to IMPLEMENTATION_BACKLOG.md for future
```

---

## 🔄 Workflow Summary

### Starting New Work

```
1. Read IMPLEMENTATION_START_POINT.md (you are here!)
   ↓
2. Decide: PLAN or SUBPLAN?
   ├─ Significant work → Create PLAN
   └─ Part of existing PLAN → Create SUBPLAN
   ↓
3. Create SUBPLAN (your approach)
   ↓
4. Create EXECUTION_TASK (start logging)
   ↓
5. Write tests (if code work)
   ↓
6. Implement iteratively
   ├─ Update EXECUTION_TASK after each iteration
   ├─ Check circular debug every 3 iterations
   └─ Add learnings to code as comments
   ↓
7. Tests pass → SUBPLAN complete
   ↓
8. All subplans done → PLAN complete
   ↓
9. Go to IMPLEMENTATION_END_POINT.md (completion process)
```

### During Execution

**Every Iteration**:

1. Make change
2. Run tests
3. Document in EXECUTION_TASK
4. Capture learning

**Every 3 Iterations**:

1. Check for circular debugging
2. Review progress
3. Validate learning
4. Decide: continue or change

**When Stuck**:

1. Create new EXECUTION_TASK
2. Change strategy fundamentally
3. Start fresh

---

## 📖 Detailed Workflows

### Creating a PLAN

**Step-by-Step**:

1. **Name It**: `PLAN_<YOUR-FEATURE>.md`

   - Feature name: short, descriptive, kebab-case
   - Example: `PLAN_OPTIMIZE-EXTRACTION.md`

2. **Start with Header**:

   - Status: Planning
   - Goal: One sentence
   - Priority: Based on impact

3. **Add LLM Context Section**:

   - What is this plan
   - What should LLM do
   - How to proceed
   - Make it self-contained

4. **Define the Problem**:

   - What's current state
   - What's wrong
   - Why it matters

5. **List Achievements** (not subplans!):

   - What needs to exist
   - Priority order
   - Success criteria
   - **Don't prescribe HOW** (that's for subplans)

6. **Add Tracking Sections**:

   - Achievement Addition Log (empty initially)
   - Subplan Tracking (empty initially)
   - Update as work progresses

7. **Review**: Is it self-contained? Can LLM execute from this alone?

### Creating a SUBPLAN

**Step-by-Step**:

1. **Select Achievement**: From a PLAN

2. **Name It**: `SUBPLAN_<FEATURE>_<NEXT-NUMBER>.md`

   - Feature: Matches PLAN
   - Number: Sequential (01, 02, 03...)

3. **Define Your Approach**:

   - How will you tackle this achievement?
   - What's your strategy?
   - What will you create/modify?

4. **List Specifics**:

   - Exact files to change
   - Tests to write
   - Expected outcomes

5. **Note Dependencies**: What must exist first?

6. **Link to PLAN**: Update PLAN's subplan tracking

### Creating an EXECUTION_TASK

**Step-by-Step**:

1. **Name It**: `EXECUTION_TASK_<FEATURE>_<SUBPLAN>_<EXECUTION>.md`

   - Feature: Matches PLAN
   - Subplan: Which subplan (01, 02...)
   - Execution: Which attempt (01, 02...)
   - Example: `EXECUTION_TASK_OPTIMIZE-EXTRACTION_01_01.md`

2. **Set Up Header**:

   - Link to SUBPLAN and PLAN
   - Execution number
   - If 2nd+ attempt, link previous and explain why

3. **Write Tests First** (if code work):

   - Create test file
   - Write all test cases
   - Run (should fail)
   - Document in "Test Creation Phase"

4. **Start Iterations**:

   - Make change
   - Run tests
   - Document iteration
   - Repeat

5. **Update After EVERY Iteration**:

   - No exceptions
   - Capture learning
   - Check progress

6. **Check Circular Debug** (every 3 iterations):
   - Same error?
   - If yes: abandon this EXECUTION, create new one

---

## ⚠️ Common Mistakes & How to Avoid

### Mistake 1: Listing Subplans in PLAN

**Wrong**:

```markdown
## Sub-Plans

- SUBPLAN_01: Create feature X
- SUBPLAN_02: Create feature Y
```

**Right**:

```markdown
## Desirable Achievements

**Achievement 1.1**: Feature X Exists

- Description, success criteria
- **Not**: How to do it (that's for SUBPLAN)
```

**Why**: PLAN lists WHAT, SUBPLAN defines HOW

### Mistake 2: Populating Backlog at Creation

**Wrong**: Create IMPLEMENTATION_BACKLOG.md with items

**Right**: Create empty with instructions, fill during IMPLEMENTATION_END_POINT

**Why**: Backlog fills from execution discoveries, not upfront

### Mistake 3: Creating Update/Status Files

**Wrong**: Create separate PLAN_UPDATES.md, PLAN_STATUS.md

**Right**: Edit PLAN directly or track in EXECUTION_TASK

**Why**: Plans are dynamic, edit in place

### Mistake 4: Not Tracking Plan Creation

**Missed Opportunity**: Complex plan creation without EXECUTION tracking

**Better**: Create EXECUTION*PLAN-CREATION*<FEATURE>\_01.md

**Why**: Plan creation is iterative work that benefits from tracking

### Mistake 5: Cheating on Tests

**Wrong**: Modify test expectations to make them pass

**Right**: Understand why test fails, fix implementation

**Why**: Tests define correctness, implementation must match

---

## 🔗 Next Steps

### After Reading This

1. **If starting new work**: Create a PLAN or SUBPLAN (decision tree above)
2. **If executing existing PLAN**: Review achievements, select one, create SUBPLAN
3. **If executing existing SUBPLAN**: Create EXECUTION_TASK, start iterations

### Related Documents

- **Predefined prompts**: `LLM/templates/PROMPTS.md` (copy-paste ready prompts for common workflows)
- **When work complete**: `IMPLEMENTATION_END_POINT.md` (completion guide)
- **For long-running plans**: `LLM/guides/IMPLEMENTATION_MID_PLAN_REVIEW.md` (quality checkpoints)
- **Future work ideas**: `IMPLEMENTATION_BACKLOG.md` (backlog)
- **Documentation standards**: `documentation/DOCUMENTATION-PRINCIPLES-AND-PROCESS.md` (ultimate reference)

### For Long-Running Plans (>20 hours, 5+ priorities)

**Use Mid-Plan Reviews** to maintain quality and prevent drift:

**When to Review**:
- After 20 hours of work
- After completing Priority 3
- After 1 month of calendar time
- Before creating 10th SUBPLAN

**Why Important**:
- Prevents methodology drift
- Catches technical debt early
- Validates execution health (avg iterations, circular debugging)
- Ensures learning capture happens incrementally

**See**: `LLM/guides/IMPLEMENTATION_MID_PLAN_REVIEW.md` for complete protocol

**Learnings**: CODE-QUALITY refactor (70h, 8 priorities) showed mid-plan reviews prevent issues like statistics gaps, learning loss, scope creep

---

## 🎯 Using Predefined Prompts

**NEW**: We now have standard prompts for common workflows!

**See**: `LLM/templates/PROMPTS.md` for complete prompt library

**Available Prompts**:
- ✅ Create New PLAN
- ✅ Resume Paused PLAN
- ✅ Complete PLAN
- ✅ Create GrammaPlan
- ✅ Analyze Code/Plan
- ✅ Create SUBPLAN
- ✅ Pause PLAN
- ✅ Add Achievement
- ✅ Create Mid-Plan Review

**Example Usage**:

Instead of manually constructing a prompt, copy from PROMPTS.md:

```
Create a new PLAN for GRAPHRAG-VALIDATION following @LLM/protocols/IMPLEMENTATION_START_POINT.md

Context:
- Goal: Validate GraphRAG pipeline end-to-end
- Priority: High
- Estimated Effort: 15-20 hours
...
```

**Benefits**:
- Consistent process execution
- All protocol steps included
- Fewer errors
- Faster workflow

**When to Use**:
- New LLM sessions (fresh context)
- Complex workflows (many steps)
- Want to enforce best practices

---

## 📊 Summary

**Remember**:

1. **PLAN** = Achievements (WHAT)
2. **SUBPLAN** = Approach (HOW)
3. **EXECUTION_TASK** = Journey (iterations, learnings)
4. **Test First** = Always
5. **Document Everything** = Every iteration
6. **Learn Continuously** = Capture in code and docs
7. **Check Circular** = Every 3 iterations
8. **Be Dynamic** = Plans evolve, add achievements
9. **Self-Contained** = PLANs work standalone

**Start Here, End at IMPLEMENTATION_END_POINT.md, Reference DOCUMENTATION-PRINCIPLES-AND-PROCESS.md**

---

**You're ready to start! Create your PLAN or SUBPLAN and begin.**
