# Implementation Resume Point

**Purpose**: Protocol for resuming paused work  
**Status**: Permanent Reference  
**Last Updated**: November 6, 2025

---

## 🎯 When to Use This Document

Use this when:

- Resuming a paused PLAN (partial completion)
- Picking up work after a break (hours, days, weeks)
- Context switching between multiple PLANs
- Another person/LLM is continuing your work
- You see a PLAN with status "⏸️ Paused" in ACTIVE_PLANS.md

**Don't use this for**:

- Starting NEW work (use IMPLEMENTATION_START_POINT.md)
- Completing work (use IMPLEMENTATION_END_POINT.md)

---

## ✅ Pre-Resume Checklist (MANDATORY)

**CRITICAL**: Do this BEFORE touching ANY code or creating ANY files!

### 1. Context Gathering (10-15 minutes)

- [ ] **Open ACTIVE_PLANS.md**: Verify which PLAN you're resuming
- [ ] **Read the PLAN**: Open `PLAN_<FEATURE>.md`
- [ ] **Find "Current Status & Handoff"**: Read this section (handoff info, not completion status)
- [ ] **Check execution/feedbacks/ folder**: See which achievements have `APPROVED_XX.md` files (filesystem-first)
- [ ] **Check "Subplan Tracking"**: See what SUBPLANs exist
- [ ] **Review "Achievement Addition Log"**: Check for dynamic changes
- [ ] **Identify next achievement**: What should you work on next? (First without APPROVED_XX.md file)

### 2. Review Naming Convention (5 minutes)

- [ ] **Re-read IMPLEMENTATION_START_POINT.md**: Refresh naming rules
- [ ] **Check existing files**: See the pattern of SUBPLAN/EXECUTION_TASK numbering
- [ ] **Note next numbers**: What's the next SUBPLAN number? Next EXECUTION number?

### 2.5. Check Dependencies (5 minutes)

- [ ] **Read PLAN "Related Plans" section**: Identify dependencies
- [ ] **Verify prerequisites**: Are all dependencies complete?
- [ ] **Check if blocked**: Is this PLAN blocked by another?
- [ ] **Review MULTIPLE-PLANS-PROTOCOL.md**: Understand dependency types if needed

### 2.6. Check Related Plans Format Compliance (2 minutes)

- [ ] **Verify "Related Plans" section exists**: Should be in "References & Context"
- [ ] **Check format**: Should use new 6-type format (Type, Relationship, Dependency, Status, Timing)
- [ ] **If outdated**: Update format to match MULTIPLE-PLANS-PROTOCOL.md
- [ ] **If missing**: Add section with current PLAN dependencies

**New Format** (from MULTIPLE-PLANS-PROTOCOL.md):

```markdown
**PLAN_NAME.md**:

- **Type**: [Hard / Soft / Data / Code / Sequential / Decision Context]
- **Relationship**: [Description]
- **Dependency**: [What this PLAN needs]
- **Status**: [Blocked / Ready / Can proceed]
- **Timing**: [When to work on this]
```

### 3. Technical Pre-Flight (5 minutes)

- [ ] **Git status clean**: No uncommitted changes
- [ ] **All tests passing**: Run `python scripts/run_tests.py` (if applicable)
- [ ] **Virtual environment active**: Correct Python version
- [ ] **Dependencies updated**: `pip install -r requirements.txt` (if needed)
- [ ] **Configuration correct**: Check environment variables, config files

### 4. Understand Context (Read Last Work)

- [ ] **Read last EXECUTION_TASK**: See where you left off
- [ ] **Check for blockers**: Any dependencies or issues noted?
- [ ] **Review learnings**: What was discovered in last execution?
- [ ] **Review relevant EXECUTION_ANALYSIS documents**: Check archive for analyses related to current PLAN/feature
  - Look in `documentation/archive/execution-analyses/` by feature name or category
  - Check INDEX.md catalog for quick reference
  - Useful for: Understanding past decisions, avoiding repeated issues, learning from similar work

### 5. Update ACTIVE_PLANS.md (REQUIRED)

- [ ] **Check current active PLAN**: Is another PLAN marked "🚀 In Progress"?
- [ ] **If yes**: Pause it first:
  - Update that PLAN's "Current Status & Handoff"
  - Commit changes: `git commit -m "Pausing PLAN_X at Achievement Y"`
  - Mark as "⏸️ Paused" in ACTIVE_PLANS.md
- [ ] **Mark this PLAN as "🚀 In Progress"** in ACTIVE_PLANS.md
- [ ] **Update "Last Updated"** timestamp
- [ ] **Verify**: Only ONE PLAN is "🚀 In Progress"

**⚠️ CRITICAL**: Skipping this step violates the "ONE In Progress" rule and can cause context confusion.

---

## 📢 Resume Announcement (Best Practice)

**When resuming, announce your intent explicitly**:

```
Following IMPLEMENTATION_RESUME.md to resume PLAN_<FEATURE>.md for Achievement X.Y

✅ Pre-Resume Checklist:
  ✅ Step 1: Context Gathering - Complete
  ✅ Step 2: Naming Convention - Reviewed
  ✅ Step 2.5: Dependencies - [Status]
  ✅ Step 3: Technical Pre-Flight - Complete
  ✅ Step 4: Context Understanding - Complete
  ✅ Step 5: ACTIVE_PLANS.md - Updated to "In Progress"

✅ Next Achievement Identified: X.Y ([Title])

Creating SUBPLAN_<NUMBER>...
```

**💡 Quick Resume with Predefined Prompt**:

See `LLM/templates/PROMPTS.md` → "Resume Paused PLAN" for copy-paste ready prompt that includes this entire checklist.

**Example**:

```
Resume @PLAN_ENTITY-RESOLUTION-REFACTOR.md following @LLM/protocols/IMPLEMENTATION_RESUME.md protocol
[... full checklist auto-generated ...]
```

**Why this matters**:

- Makes resume explicit and traceable
- Shows checklist compliance
- Prevents assumption of context
- Demonstrates process adherence

---

## 📋 Resume Workflow

### Step 1: Select Next Achievement (from PLAN)

**In PLAN\_<FEATURE>.md**:

1. Find "Desirable Achievements" section
2. Look for next uncompleted achievement (usually in priority order)
3. Check "Subplan Tracking" to see if SUBPLAN already exists for this achievement
4. If SUBPLAN exists: Check if EXECUTION_TASK exists
5. If both exist but incomplete: Continue existing EXECUTION_TASK or create new one (new strategy)

**💡 Finding Relevant EXECUTION_ANALYSIS Documents**:

Before starting work, check for relevant analyses that might inform your approach:

1. **By Feature Name**: Look in `documentation/archive/execution-analyses/` for analyses matching your feature
2. **By Category**: Check category subdirectories (methodology-review, planning-strategy, bug-analysis, etc.)
3. **By INDEX.md**: Review `documentation/archive/execution-analyses/INDEX.md` for catalog of all analyses
4. **Search by Topic**: Look for analyses covering similar problems, blockers, or decisions

**Why This Matters**:

- Learn from past decisions and avoid repeating mistakes
- Understand context from previous work on same feature
- Find solutions to similar problems
- Discover methodology improvements or patterns

**Example**: If resuming `PLAN_ENTITY-RESOLUTION-REFACTOR.md`, check for:

- `EXECUTION_ANALYSIS_ENTITY-RESOLUTION-*.md` files
- Analyses in `bug-analysis/` category related to entity resolution
- Methodology reviews that mention entity resolution work

**Decision Tree**:

```
Achievement to tackle?
  ├─ SUBPLAN exists?
  │   ├─ Yes: EXECUTION_TASK exists?
  │   │   ├─ Yes: Is it complete?
  │   │   │   ├─ Yes: Create next achievement's SUBPLAN
  │   │   │   └─ No: Continue EXECUTION_TASK OR create new one (different strategy)
  │   │   └─ No: Create EXECUTION_TASK_<FEATURE>_<SUBPLAN>_01.md
  │   └─ No: Create SUBPLAN_<FEATURE>_<NEXT_NUMBER>.md
  └─ Continue
```

### Step 2: Create Work Documents (If Needed)

**If creating NEW SUBPLAN**:

```bash
# Check next number from "Subplan Tracking" section
# Example: Last SUBPLAN was 08, so create 09

File: SUBPLAN_<FEATURE>_09.md
```

**Follow IMPLEMENTATION_START_POINT.md** for SUBPLAN structure.

**If creating NEW EXECUTION_TASK**:

```bash
# Format: EXECUTION_TASK_<FEATURE>_<SUBPLAN_NUMBER>_<EXECUTION_NUMBER>.md
# Example: First execution of SUBPLAN 09

File: EXECUTION_TASK_<FEATURE>_09_01.md
```

**If CONTINUING existing EXECUTION_TASK**:

- Just open it and continue logging iterations
- Update iteration count
- Document new attempts

### Step 3: Execute Work (Follow TDD Workflow)

**Standard Execution** (from IMPLEMENTATION_START_POINT.md):

1. **Write tests first** (if applicable)
2. **Implement iteratively**
3. **Document each iteration** in EXECUTION_TASK
4. **Check for circular debugging** (every 3 iterations)
5. **Add learnings to code** as comments
6. **Update PLAN**: Add completed SUBPLAN to "Subplan Tracking"

**Track Progress**:

- Update EXECUTION_TASK after each iteration
- Update PLAN "Subplan Tracking" when SUBPLAN complete
- Commit at logical checkpoints (see commit discipline below)

### Commit Discipline

**When to commit**:

- After completing each SUBPLAN
- Before pausing a PLAN
- At logical checkpoints (every 2-3 hours of work)
- After significant milestones

**Commit message format**:

```bash
Complete Achievement X.Y: [Title]

- [Deliverable 1]
- [Deliverable 2]
- [Deliverable 3]
```

**Examples**:

```bash
git commit -m "Complete Achievement 0.1: Relationship Existence Checks

- Fixed co-occurrence checks to include predicate
- Fixed semantic similarity checks to include predicate
- Added 12 tests (all passing)
"

git commit -m "Pausing PLAN_GRAPH-CONSTRUCTION at Priority 3

- Priorities 0-3 complete (11/17 achievements)
- Remaining: Priority 4-5 + Achievement 2.1
- Foundation production-ready
"
```

### Step 4: Pause Again (If Needed)

**Follow IMPLEMENTATION_END_POINT.md** (for partial completion):

1. **Update PLAN "Current Status & Handoff" section**:

   - Note where you stopped
   - Note what should be done next
   - Document what's complete
   - Document what remains

2. **Commit all changes**:

   ```bash
   git add -A
   git commit -m "Pausing PLAN_<FEATURE> at Achievement X.Y

   - Achievements complete: [list]
   - Remaining: [list]
   - Status: [status]
   "
   ```

3. **Update ACTIVE_PLANS.md**:

   - Mark as "⏸️ Paused"
   - Update completion percentage
   - Update "Last Updated" timestamp
   - Update "Next Achievement" column

4. **Archive completed work** (if significant milestone):
   - Follow IMPLEMENTATION_END_POINT.md partial completion process
   - Move completed SUBPLANs and EXECUTION_TASKs to archive
   - Keep PLAN in root

---

## 🚫 Common Resume Mistakes (DO NOT DO THIS)

### ❌ Creating Non-Conforming Files

**DON'T create these** (they violate naming convention):

- ❌ `PLAN_UPDATE_<FEATURE>.md` → Update the PLAN itself (section)
- ❌ `<FEATURE>-STATUS.md` → Section in PLAN "Current Status & Handoff"
- ❌ `<FEATURE>-SUMMARY.md` → Section in parent document
- ❌ `<FEATURE>-COMPLIANCE.md` → Section in PLAN or use EXECUTION*ANALYSIS*
- ❌ `<FEATURE>-INSIGHTS.md` → Section in EXECUTION*ANALYSIS*
- ❌ `MILESTONE_<FEATURE>.md` → Section in PLAN
- ❌ `RESUME_<FEATURE>.md` → Just resume, don't create resume file

**Rule**: Updates/status/summaries go IN existing documents as sections, not as new files.

### ❌ Skipping the PLAN

**DON'T**:

- Assume you remember context
- Start coding without reading "Current Status"
- Create SUBPLAN without checking existing ones

**DO**:

- Read PLAN "Current Status & Handoff" every time
- Check "Subplan Tracking" for what's done
- Review "Achievement Addition Log" for changes

### ❌ Duplicate SUBPLANs/EXECUTION_TASKs

**DON'T**:

- Create SUBPLAN\_<FEATURE>\_05.md if 05 already exists
- Reuse EXECUTION_TASK numbers

**DO**:

- Check "Subplan Tracking" section in PLAN
- Use sequential numbers (if last is 08, create 09)
- Each SUBPLAN can have multiple EXECUTION_TASKs (01, 02, 03...)

### ❌ Wrong Feature Name

**DON'T**:

- Use different feature name than PLAN
- Example: PLAN is `PLAN_OPTIMIZE-EXTRACTION.md`, don't create `SUBPLAN_EXTRACTION-OPTIMIZATION_01.md`

**DO**:

- Copy feature name EXACTLY from PLAN filename
- Example: `SUBPLAN_OPTIMIZE-EXTRACTION_09.md`

---

## 🔄 Context Switching Between Plans

**If working on multiple PLANs** (shown in ACTIVE_PLANS.md):

### Before Pausing Current PLAN

1. **Commit all changes**: `git add -A && git commit -m "Pausing PLAN_X at Achievement Y"`
2. **Update PLAN**: "Current Status & Handoff" section
3. **Update ACTIVE_PLANS.md**: Mark as "⏸️ Paused"
4. **Note blocker/reason**: Why pausing (if relevant)

### Before Resuming Other PLAN

1. **Follow this document**: Complete Pre-Resume Checklist
2. **Check dependencies**:
   - Read PLAN "Related Plans" section
   - Verify prerequisites are complete
   - Check if blocked by another PLAN
   - See `LLM/guides/MULTIPLE-PLANS-PROTOCOL.md` for dependency types
3. **Update ACTIVE_PLANS.md**: Mark as "🚀 In Progress"

### Tracking Active Plan

**Only ONE plan should be "🚀 In Progress" at a time.**

Update ACTIVE_PLANS.md when switching:

```markdown
| Plan   | Status         | Priority | Completion | Last Updated | Next Achievement |
| ------ | -------------- | -------- | ---------- | ------------ | ---------------- |
| PLAN_A | ⏸️ Paused      | HIGH     | 60%        | 2025-11-06   | Achievement 3.1  |
| PLAN_B | 🚀 In Progress | CRITICAL | 45%        | 2025-11-06   | Achievement 2.2  |
```

---

## ✅ Resume Verification (After 1 Hour)

**Self-check after resuming work for 1 hour**:

- [ ] **ACTIVE_PLANS.md updated**: This PLAN marked "🚀 In Progress" ⚠️ CRITICAL
- [ ] **Only ONE PLAN "In Progress"**: Verify no other PLANs active ⚠️ CRITICAL
- [ ] **All files follow naming**: `TYPE_FEATURE_NUMBER.md` pattern
- [ ] **PLAN updated**: "Subplan Tracking" section (if completed any)
- [ ] **EXECUTION_TASK updated**: Logging iterations properly
- [ ] **Tests running**: If applicable
- [ ] **No non-conforming files**: No status/summary/update files created
- [ ] **Correct feature name**: Matches PLAN exactly
- [ ] **Sequential numbering**: Correct (checked "Subplan Tracking")
- [ ] **Git commits**: Good messages, logical checkpoints

**If ANY item is ❌**: Stop, fix it now before continuing.

**Focus on CRITICAL items first** (ACTIVE_PLANS.md updates are most commonly missed).

---

## 📚 Quick Reference

### Document Types (Complete List)

**Use these** (create during work):

- `PLAN_<FEATURE>.md` - One per feature
- `SUBPLAN_<FEATURE>_<NUMBER>.md` - One per approach
- `EXECUTION_TASK_<FEATURE>_<SUBPLAN>_<EXECUTION>.md` - Execution logs
- `EXECUTION_ANALYSIS_<TOPIC>.md` - Analysis work (post-mortems, reviews)

**Never create these** (should be sections):

- ❌ `PLAN_UPDATE_*`, `*-STATUS`, `*-SUMMARY`, `*-COMPLIANCE`, `*-INSIGHTS`

### Naming Rules Refresher

**Pattern**: `TYPE_FEATURE_NUMBER.md`

- Type: PLAN, SUBPLAN, EXECUTION_TASK, EXECUTION_ANALYSIS
- Feature: Kebab-case (hyphens), 2-4 words, matches PLAN exactly
- Number: Zero-padded (01, 02, 03... not 1, 2, 3)

**Examples**:

- ✅ `PLAN_OPTIMIZE-EXTRACTION.md`
- ✅ `SUBPLAN_OPTIMIZE-EXTRACTION_01.md`
- ✅ `EXECUTION_TASK_OPTIMIZE-EXTRACTION_01_01.md`
- ✅ `EXECUTION_ANALYSIS_METHODOLOGY-REVIEW.md`

### Where to Find Information

**Before resuming**:

- PLAN "Current Status & Handoff" → Where you left off
- PLAN "Subplan Tracking" → What's complete
- PLAN "Achievement Addition Log" → Dynamic changes
- Last EXECUTION_TASK → Detailed progress

**During work**:

- IMPLEMENTATION_START_POINT.md → How to create documents
- ACTIVE_PLANS.md → All active/paused work

**When pausing**:

- IMPLEMENTATION_END_POINT.md → Completion/pause workflow

---

## 🎯 Example Resume Scenario

**Situation**: You paused PLAN_ENTITY-RESOLUTION-REFACTOR.md after Priority 3, now resuming for Priority 3.5.

### Steps

1. **Open ACTIVE_PLANS.md**: See entity-resolution is "⏸️ Paused"
2. **Open PLAN_ENTITY-RESOLUTION-REFACTOR.md**
3. **Read "Current Status & Handoff"**:
   - "Priorities 0-3 complete"
   - "Priority 3.5 added (critical bugs)"
   - "Next: Achievement 3.5.1"
4. **Check "Subplan Tracking"**: Last SUBPLAN was 33
5. **Check "Achievement Addition Log"**: Priority 3.5 was added dynamically
6. **Refresh naming rules**: Read START_POINT naming section
7. **Create SUBPLAN_ENTITY-RESOLUTION-REFACTOR_34.md** (for Achievement 3.5.1)
8. **Create EXECUTION_TASK_ENTITY-RESOLUTION-REFACTOR_34_01.md**
9. **Update ACTIVE_PLANS.md**: Mark entity-resolution as "🚀 In Progress"
10. **Start working**: Follow TDD workflow

---

## ⚠️ CRITICAL: Before Creating ANY File

**STOP and ask these questions**:

1. Does it match `PLAN_*`, `SUBPLAN_*`, `EXECUTION_TASK_*`, or `EXECUTION_ANALYSIS_*`?
2. If it's about ONE specific PLAN/SUBPLAN, should it be a section IN that document?
3. Is it a status/summary/update/compliance file? → Should be section, not file
4. Does feature name match parent PLAN EXACTLY?
5. Did I check next sequential number from "Subplan Tracking"?
6. Are numbers zero-padded (01 not 1)?

**If you answered "not sure" to ANY question**: Re-read IMPLEMENTATION_START_POINT.md before proceeding.

---

**Status**: Permanent Reference  
**Created**: 2025-11-06  
**Purpose**: Prevent naming violations and context loss when resuming paused work

**Integration**:

- From START_POINT: "Resuming work? See IMPLEMENTATION_RESUME.md"
- From END_POINT: "To resume later, follow IMPLEMENTATION_RESUME.md"
- From ACTIVE_PLANS: Link to this document for each paused plan
