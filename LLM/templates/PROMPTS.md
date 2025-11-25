# Predefined Prompts for LLM Development Methodology

**Purpose**: Standard, reusable prompts for common methodology workflows  
**Status**: Foundation Document  
**Created**: 2025-11-07  
**Last Updated**: 2025-11-09 (Designer/Executor phase separation added)  
**Version**: 1.1

---

## 🎯 What This Document Is

**Collection of copy-paste ready prompts** for:

- Creating new PLANs
- Resuming paused work
- Completing and archiving work
- Creating GrammaPlans
- Analyzing code/plans
- Creating SUBPLANs

**Why Use These Prompts**:

- ✅ **Consistency**: Same process every time
- ✅ **Completeness**: All protocol steps included
- ✅ **Fewer Errors**: Reduces human error in complex workflows
- ✅ **Faster**: Copy/paste instead of manual construction
- ✅ **Better Quality**: Enforces best practices automatically

**When to Use**:

- New LLM sessions (fresh context)
- Complex workflows (many steps to remember)
- Team collaboration (consistent process)
- Onboarding (learn by using prompts)

---

## 📋 Prompt Library

### 1. Create New PLAN

**When to Use**:

- Starting significant new work (>10 hours)
- Work with multiple achievements
- Need coordination or phasing

**Template**:

```
Create a new PLAN for [FEATURE_NAME] following @LLM/protocols/IMPLEMENTATION_START_POINT.md

Context:
- Goal: [ONE SENTENCE DESCRIBING WHAT TO ACHIEVE]
- Priority: [Critical / High / Medium / Low]
- Estimated Effort: [X-Y hours]

GrammaPlan Decision:
- Will PLAN exceed 800 lines? [Yes / No]
- Effort > 80 hours? [Yes / No]
- Spans 3+ domains? [Yes / No]
→ Decision: [Single PLAN / GrammaPlan]

If Single PLAN:
- Create work-space/plans/PLAN_[FEATURE_NAME].md using @LLM/templates/PLAN-TEMPLATE.md
- Follow all template sections
- List priority-ordered achievements (WHAT, not HOW)
- Include GrammaPlan Consideration section with rationale

If GrammaPlan:
- Create GRAMMAPLAN_[FEATURE_NAME].md using @LLM/templates/GRAMMAPLAN-TEMPLATE.md
- Plan child PLANs (6-8 children typical)
- See @LLM/guides/GRAMMAPLAN-GUIDE.md for guidance

After Creation:
- Update @ACTIVE_PLANS.md with new PLAN
- Mark as "📋 Ready"
- Document in "Ready Plans" section

═══════════════════════════════════════════════════════════════════════

VALIDATION ENFORCEMENT:

After PLAN creation, these scripts will run:
✓ check_plan_size.py (validates 900 lines / 40 hours limit)
✓ validate_plan_compliance.py (checks template compliance)

If issues found: BLOCKS with error + fix prompt

DO NOT:
❌ Skip template sections ("it's simple" - NO)
❌ Exceed size limits (must convert to GrammaPlan if >900 lines)
❌ Create PLAN without following template
```

**Placeholders to Replace**:

- `[FEATURE_NAME]`: Short kebab-case name (e.g., `OPTIMIZE-EXTRACTION`)
- `[ONE SENTENCE...]`: Clear goal statement
- `[Priority]`: Critical/High/Medium/Low
- `[X-Y hours]`: Time estimate

**Example**:

```
Create a new PLAN for GRAPHRAG-VALIDATION following @LLM/protocols/IMPLEMENTATION_START_POINT.md

Context:
- Goal: Validate GraphRAG pipeline end-to-end with production-scale data and metrics
- Priority: High
- Estimated Effort: 15-20 hours

GrammaPlan Decision:
- Will PLAN exceed 800 lines? No (estimated ~300 lines)
- Effort > 80 hours? No (15-20 hours)
- Spans 3+ domains? No (single domain: validation)
→ Decision: Single PLAN

Create work-space/plans/PLAN_GRAPHRAG-VALIDATION.md using @LLM/templates/PLAN-TEMPLATE.md
[... LLM proceeds to create the PLAN ...]
```

---

### 2. Resume Paused PLAN

**When to Use**:

- PLAN has status "⏸️ Paused" in ACTIVE_PLANS.md
- Picking up work after break
- Context switching between plans

**Template**:

```
Resume @PLAN_[FEATURE_NAME].md following @LLM/protocols/IMPLEMENTATION_RESUME.md protocol

✅ Pre-Resume Checklist:

Step 1: Context Gathering (10-15 min)
- [ ] Read @ACTIVE_PLANS.md (verify this is the PLAN to resume)
- [ ] Read @PLAN_[FEATURE_NAME].md completely
- [ ] Read "Current Status & Handoff" section
- [ ] Review "Subplan Tracking" section
- [ ] Review "Achievement Addition Log" (if exists)
- [ ] Identify next achievement to tackle

Step 2: Naming Convention (5 min)
- [ ] Review @LLM/protocols/IMPLEMENTATION_START_POINT.md naming rules
- [ ] Check existing SUBPLAN/EXECUTION_TASK numbering
- [ ] Determine next SUBPLAN/EXECUTION_TASK numbers

Step 2.5: Dependencies (5 min)
- [ ] Read "Related Plans" section
- [ ] Verify dependencies are Ready (not Blocked)
- [ ] Review @LLM/guides/MULTIPLE-PLANS-PROTOCOL.md if needed

Step 2.6: Format Compliance (2 min)
- [ ] Verify "Related Plans" uses 6-type format
- [ ] Update format if outdated

Step 3: Technical Pre-Flight (5 min)
- [ ] Git status clean
- [ ] Tests passing
- [ ] Virtual environment active
- [ ] Configuration correct

Step 4: Context Understanding (variable)
- [ ] Read last EXECUTION_TASK
- [ ] Check for blockers
- [ ] Review learnings

Step 5: ACTIVE_PLANS.md Update (REQUIRED)
- [ ] Pause any other "🚀 In Progress" PLAN
- [ ] Mark this PLAN as "🚀 In Progress"
- [ ] Update "Last Updated" timestamp
- [ ] Verify only ONE PLAN "In Progress"

✅ Next Achievement: [ACHIEVEMENT_NUMBER] ([Title])

═══════════════════════════════════════════════════════════════════════

VALIDATION ENFORCEMENT:

Before resuming, these scripts will run:
✓ validate_execution_start.py (checks prerequisites)
✓ check_plan_size.py (validates PLAN still within limits)

If issues found: BLOCKS with error + fix prompt

DO NOT:
❌ Resume without checking prerequisites
❌ Skip validation steps
❌ Resume if PLAN exceeds size limits

Now creating SUBPLAN for this achievement...
```

**Placeholders to Replace**:

- `[FEATURE_NAME]`: The PLAN's feature name
- `[ACHIEVEMENT_NUMBER]`: Next achievement to tackle (e.g., 2.1)
- `[Title]`: Achievement title

**Example**:

```
Resume @PLAN_ENTITY-RESOLUTION-REFACTOR.md following @LLM/protocols/IMPLEMENTATION_RESUME.md protocol

✅ Pre-Resume Checklist:
[... complete all steps ...]

✅ Next Achievement: 4.1 (Batch Processing Optimization)

Now creating SUBPLAN_ENTITY-RESOLUTION-REFACTOR_21.md for this achievement...
```

---

### 3. Complete PLAN

**When to Use**:

- All achievements complete
- Ready to archive and wrap up
- Moving PLAN to "Recently Completed"

**Template**:

```
Complete @PLAN_[FEATURE_NAME].md following @LLM/protocols/IMPLEMENTATION_END_POINT.md

Pre-Completion Steps:

Step 0: Pre-Completion Review (if section exists in PLAN)
- [ ] Complete "Pre-Completion Review" checklist in PLAN
- [ ] Verify all items checked
- [ ] Get sign-off (if applicable)

Pre-Archiving Checklist (CRITICAL):
- [ ] Accept all pending changes in editor
- [ ] Run test suite (if code changes)
- [ ] Run linters
- [ ] Commit all changes: git commit -m "Pre-archive checkpoint - [FEATURE] complete"
- [ ] Verify clean state: git status clean

Completion Checklist:

1. Verify PLAN Completion (Filesystem-First)
   - [ ] All achievements met (verified by `APPROVED_XX.md` files in `execution/feedbacks/`)
   - [ ] All SUBPLANs complete
   - [ ] All EXECUTION_TASKs complete
   - [ ] Success criteria met
   - **Note**: Achievement completion tracked via filesystem (`APPROVED_XX.md` files), not PLAN markdown checkmarks

2. Quality Analysis
   - [ ] Tests passing
   - [ ] Use PLAN "Summary Statistics" section for metrics
   - [ ] Calculate: avg iterations, circular debugging rate, time accuracy

3. Extract Future Work
   - [ ] Review all EXECUTION_TASKs for "Future Work" sections
   - [ ] Add 3-5+ items to @LLM/protocols/IMPLEMENTATION_BACKLOG.md
   - [ ] Tag with: Theme, Effort, Priority, Discovered In

4. Process Improvement Analysis
   - [ ] Document "What Worked"
   - [ ] Document "What Didn't Work"
   - [ ] Identify methodology improvements
   - [ ] Update meta-PLAN if improvements found

5. Learning Extraction
   - [ ] Aggregate learnings from EXECUTION_TASKs
   - [ ] Update technical guides with new patterns
   - [ ] Document key decisions and rationale

6. Archive Creation (Deferred Archiving)
   - [ ] Create: documentation/archive/[feature]-[date]/
   - [ ] Move: SUBPLANs, EXECUTION_TASKs, EXECUTION_ANALYSIS (batch archive at plan completion)
   - [ ] Create: INDEX.md
   - [ ] Create: summary/[FEATURE]-COMPLETE.md
   - [ ] Keep PLAN in root or move based on importance
   - Note: Files archived at plan completion per deferred archiving policy (see IMPLEMENTATION_END_POINT.md)

7. Final Updates
   - [ ] Update @ACTIVE_PLANS.md (move to "Recently Completed")
   - [ ] Update @CHANGELOG.md with completion entry
   - [ ] Commit: git commit -m "Complete [FEATURE] - archive created"

═══════════════════════════════════════════════════════════════════════

VALIDATION ENFORCEMENT:

Before completion, these scripts will run:
✓ validate_achievement_completion.py (verifies all achievements complete)
✓ validate_mid_plan.py (checks statistics accuracy)
✓ check_plan_size.py (validates final PLAN size)

If issues found: BLOCKS with error + fix prompt

DO NOT:
❌ Mark complete without verifying all achievements done (check for `APPROVED_XX.md` files in `execution/feedbacks/`)
❌ Manually update PLAN markdown with "✅ Achievement complete" (use filesystem-first: APPROVED files)
❌ Skip archive creation
❌ Complete with incomplete statistics

Now executing completion workflow...
```

**Placeholders to Replace**:

- `[FEATURE_NAME]`: The PLAN's feature name
- `[FEATURE]`: Feature name for commit messages
- `[feature]-[date]`: Archive folder name (lowercase, with date)

**Example**:

```
Complete @PLAN_CODE-QUALITY-REFACTOR.md following @LLM/protocols/IMPLEMENTATION_END_POINT.md

[... complete all steps ...]

Creating archive at: documentation/archive/code-quality-refactor-nov2025/
```

---

### 4. Create GrammaPlan

**When to Use**:

- Planning initiative >80 hours OR >800 lines OR 3+ domains
- Need to coordinate multiple related PLANs
- Want parallel work streams

**Template**:

```
Create a GrammaPlan for [INITIATIVE_NAME] following @LLM/guides/GRAMMAPLAN-GUIDE.md

Decision Validation:
Check TWO OR MORE of these apply:
- [ ] Would exceed 800 lines as single PLAN
- [ ] Estimated effort > 80 hours
- [ ] Spans 3+ distinct domains
- [ ] >20 achievements
- [ ] Natural parallelism opportunities
- [ ] Medium-context model deployment

If YES to 2+: GrammaPlan is appropriate ✅

GrammaPlan Structure:

1. Create GRAMMAPLAN_[INITIATIVE_NAME].md using @LLM/templates/GRAMMAPLAN-TEMPLATE.md

2. Define Strategic Goals:
   - Primary goal (1 sentence)
   - Success criteria (must/should/nice to have)
   - Problem statement (pain points)

3. Plan Child PLANs (6-8 typical):
   - Domain decomposition OR
   - Sequential phases OR
   - Component-based split
   - Name: PLAN_[INITIATIVE_NAME]-[DOMAIN].md

4. Define Dependencies:
   - Which children depend on which?
   - What can run in parallel?
   - Coordination points?

5. Progress Tracking:
   - Child PLAN table
   - Overall progress formula
   - Learning cache for insights

6. Update @ACTIVE_PLANS.md:
   - Add to "GrammaPlans" section
   - Add child PLAN table
   - Mark as "📋 Ready"

═══════════════════════════════════════════════════════════════════════

VALIDATION ENFORCEMENT:

After GrammaPlan creation, these scripts will run:
✓ check_plan_size.py (validates child PLANs within limits)
✓ validate_plan_compliance.py (checks GrammaPlan template compliance)
✓ validate_references.py (verifies child PLAN references)

If issues found: BLOCKS with error + fix prompt

DO NOT:
❌ Create GrammaPlan without meeting criteria (2+ of: >800 lines, >80 hours, 3+ domains)
❌ Skip child PLAN validation
❌ Create GrammaPlan with invalid structure

Now creating GrammaPlan...
```

**Placeholders to Replace**:

- `[INITIATIVE_NAME]`: Short name for initiative (e.g., `LLM-METHODOLOGY-V2`)
- `[DOMAIN]`: Domain for each child PLAN (e.g., `GRAPHRAG`, `INGESTION`)

**Example**:

```
Create a GrammaPlan for LLM-METHODOLOGY-V2 following @LLM/guides/GRAMMAPLAN-GUIDE.md

Decision Validation:
- [x] Would exceed 800 lines as single PLAN (yes - 1000+ lines estimated)
- [x] Estimated effort > 80 hours (yes - 100 hours)
- [x] Spans 3+ distinct domains (yes - 6 domains: backlog, compliance, organization, automation, optimization, export)
→ GrammaPlan is appropriate ✅

Child PLANs:
1. PLAN_LLM-V2-BACKLOG (Meta-Plan Items, 20-30h, P0)
2. PLAN_LLM-V2-COMPLIANCE (Plan Compliance, 15-20h, P1)
3. PLAN_LLM-V2-ORGANIZATION (Doc Organization, 8-12h, P1)
4. PLAN_LLM-V2-AUTOMATION (Tooling, 20-25h, P2)
5. PLAN_LLM-V2-OPTIMIZATION (Context Reduction, 12-18h, P2)
6. PLAN_LLM-V2-EXPORT (External Export, 8-12h, P3)

[... proceed with GrammaPlan creation ...]
```

---

### 5. Analyze Code or Plan

**When to Use**:

- Need systematic analysis (not execution tracking)
- Post-mortem or review needed
- Cross-cutting investigation
- Methodology improvement analysis

**Template**:

```
Analyze @[TARGET_FILE/PLAN] for [ANALYSIS_PURPOSE] and create EXECUTION_ANALYSIS_[TOPIC].md

Analysis Structure:

1. Purpose & Context:
   - What are we analyzing?
   - Why is this analysis needed?
   - What questions to answer?

2. Methodology:
   - How will we analyze?
   - What data sources?
   - What criteria/metrics?

3. Findings:
   - Key discoveries (organized by theme)
   - Evidence for each finding
   - Severity/impact assessment

4. Recommendations:
   - Actionable improvements
   - Priority (High/Medium/Low)
   - Effort estimates
   - Dependencies

5. Learnings:
   - What did we learn?
   - How to apply insights?
   - What to do differently next time?

Output: EXECUTION_ANALYSIS_[TOPIC].md

═══════════════════════════════════════════════════════════════════════

VALIDATION ENFORCEMENT:

After analysis creation, these scripts will run:
✓ validate_references.py (checks file references in analysis)
✓ validate_plan_compliance.py (if analyzing PLAN structure)

If issues found: BLOCKS with error + fix prompt

DO NOT:
❌ Create analysis without structured sections
❌ Skip evidence for findings
❌ Create analysis without actionable recommendations

Now creating analysis document...
```

**Placeholders to Replace**:

- `[TARGET_FILE/PLAN]`: File or PLAN to analyze
- `[ANALYSIS_PURPOSE]`: Why analyzing (e.g., "completion review", "bug investigation")
- `[TOPIC]`: Short topic name for filename (e.g., `METHODOLOGY-REVIEW`, `ENTITY-BUGS`)

**Example**:

```
Analyze @PLAN_CODE-QUALITY-REFACTOR.md for completion review and methodology improvements, creating EXECUTION_ANALYSIS_CODE-QUALITY-COMPLETION-REVIEW.md

Purpose: Extract insights from 70-hour, 36-achievement plan to improve meta-PLAN

[... proceed with structured analysis ...]
```

---

### 6. Continue SUBPLAN

**When to Use**:

- Resuming work on an active SUBPLAN
- Starting a new session
- Need to continue mid-achievement work

**Template**:

```
Continue work on @SUBPLAN_[FEATURE]_[XX].md following @LLM/protocols/CONTINUE_SUBPLAN.md

═══════════════════════════════════════════════════════════════════════

CONTEXT BOUNDARIES (Read ONLY These):
✅ @SUBPLAN_[FEATURE]_[XX].md (complete file, max 400 lines)
✅ @PLAN_[FEATURE].md - Current achievement section only
✅ @EXECUTION_TASK_[FEATURE]_[XX]_[YY].md (if exists, max 200 lines)
✅ @PLAN_[FEATURE].md - "Current Status & Handoff" section

❌ DO NOT READ: Full PLAN, other achievements, other SUBPLANs

CONTEXT BUDGET: ~400 lines maximum

═══════════════════════════════════════════════════════════════════════

CURRENT STATUS:
[Read from SUBPLAN and EXECUTION_TASK]

NEXT STEPS:
[Read from SUBPLAN "Approach" section]

═══════════════════════════════════════════════════════════════════════

VALIDATION ENFORCEMENT:

After Step 4, these scripts will run:
✓ validate_execution_start.py (checks SUBPLAN exists, prerequisites met)
✓ check_plan_size.py (validates parent PLAN still within limits)

If issues found: BLOCKS with error + fix prompt

DO NOT:
❌ Skip SUBPLAN creation
❌ Continue without validating prerequisites
❌ Skip validation steps

═══════════════════════════════════════════════════════════════════════

Continue work on SUBPLAN...
```

**Placeholders to Replace**:

- `[FEATURE]`: Feature name
- `[XX]`: SUBPLAN number
- `[YY]`: EXECUTION_TASK number

---

### 7. Next Achievement

**When to Use**:

- Starting next achievement in active PLAN
- Previous achievement complete
- New session, need to begin next work

**Template**:

```
Start next achievement in @PLAN_[FEATURE].md following @LLM/protocols/NEXT_ACHIEVEMENT.md

═══════════════════════════════════════════════════════════════════════

CONTEXT BOUNDARIES (Read ONLY These):
✅ @PLAN_[FEATURE].md - Next achievement section only (50-100 lines)
✅ @PLAN_[FEATURE].md - "Current Status & Handoff" section (30-50 lines)
✅ @PLAN_[FEATURE].md - "Subplan Tracking" summary (20-30 lines)

❌ DO NOT READ: Full PLAN, other achievements, completed work

CONTEXT BUDGET: ~150 lines maximum

═══════════════════════════════════════════════════════════════════════

NEXT ACHIEVEMENT: [X.Y] - [Title]

Goal: [From achievement section]
Estimated: [From achievement section]

═══════════════════════════════════════════════════════════════════════

REQUIRED STEPS:

Step 1: Create SUBPLAN (MANDATORY)
- File: SUBPLAN_[FEATURE]_[XX].md
- Template: LLM/templates/SUBPLAN-TEMPLATE.md

Step 2: Create EXECUTION_TASK (MANDATORY)
- File: EXECUTION_TASK_[FEATURE]_[XX]_01.md
- Template: LLM/templates/EXECUTION_TASK-TEMPLATE.md

Step 3: Execute Work
[Implement achievement deliverables]

═══════════════════════════════════════════════════════════════════════

VALIDATION ENFORCEMENT:

After Step 4, these scripts will run:
✓ validate_achievement_completion.py (verifies previous achievement complete)
✓ validate_execution_start.py (checks prerequisites before starting)
✓ check_plan_size.py (validates PLAN still within limits)
✓ validate_registration.py (verifies SUBPLAN registered in PLAN)

If issues found: BLOCKS with error + fix prompt

DO NOT:
❌ Skip SUBPLAN creation ("it's simple" - NO)
❌ Skip EXECUTION_TASK creation ("just document in PLAN" - NO)
❌ Start achievement without verifying previous complete
❌ Skip validation steps

═══════════════════════════════════════════════════════════════════════

Now beginning next achievement...
```

**Placeholders to Replace**:

- `[FEATURE]`: Feature name
- `[X.Y]`: Achievement number
- `[Title]`: Achievement title
- `[XX]`: Next SUBPLAN number

---

### 8. Continue EXECUTION_TASK

**When to Use**:

- Resuming work on an active EXECUTION_TASK
- Starting a new session
- Need to continue current iteration

**Template**:

```
Continue work on @EXECUTION_TASK_[FEATURE]_[XX]_[YY].md following @LLM/protocols/CONTINUE_EXECUTION.md

═══════════════════════════════════════════════════════════════════════

CONTEXT BOUNDARIES (Read ONLY These):
✅ @EXECUTION_TASK_[FEATURE]_[XX]_[YY].md (complete file, max 200 lines)
✅ @SUBPLAN_[FEATURE]_[XX].md - Objective only (1-2 sentences)
✅ Code files being modified (if code work)

❌ DO NOT READ: Full SUBPLAN, full PLAN, other EXECUTION_TASKs

CONTEXT BUDGET: ~200 lines maximum

═══════════════════════════════════════════════════════════════════════

CURRENT STATUS:
[Read from EXECUTION_TASK iteration log]

NEXT STEPS:
[Read from EXECUTION_TASK "Next" section]

═══════════════════════════════════════════════════════════════════════

VALIDATION ENFORCEMENT:

After Step 4, these scripts will run:
✓ check_execution_task_size.py (validates <200 lines limit)
✓ validate_execution_start.py (checks prerequisites still met)

If issues found: BLOCKS with error + fix prompt

DO NOT:
❌ Exceed 200-line limit (create new EXECUTION_TASK if needed)
❌ Continue without validating size
❌ Skip validation steps

═══════════════════════════════════════════════════════════════════════

Continue work on EXECUTION_TASK...
```

**Placeholders to Replace**:

- `[FEATURE]`: Feature name
- `[XX]`: SUBPLAN number
- `[YY]`: EXECUTION_TASK number

---

### 9. Create SUBPLAN (Bonus)

**When to Use**:

- Tackling an achievement from a PLAN
- Need to define approach before execution
- Achievement is complex (>2 hours)

**Template**:

```
Create SUBPLAN for Achievement [X.Y] in @PLAN_[FEATURE].md

Achievement Details:
- Number: [X.Y]
- Title: [ACHIEVEMENT_TITLE]
- Effort: [X-Y hours]

SUBPLAN Structure (use @LLM/templates/SUBPLAN-TEMPLATE.md):

1. Objective:
   - What needs to be achieved?
   - Why this achievement matters?

2. Deliverables:
   - Files to create
   - Files to modify
   - Functions/classes to add
   - Tests required

3. Approach:
   - Strategy (high-level plan)
   - Method (step-by-step)
   - Key considerations

4. Tests Required:
   - Test file name
   - Test cases to cover
   - Test-first requirement

5. Expected Results:
   - Functional changes
   - Observable outcomes

6. Conflict Analysis:
   - Review existing SUBPLANs
   - Check for overlap/conflicts

7. Dependencies:
   - Other subplans
   - External dependencies
   - Prerequisite knowledge

Create: SUBPLAN_[FEATURE]_[NUMBER].md

Then create: EXECUTION_TASK_[FEATURE]_[NUMBER]_01.md to begin execution

═══════════════════════════════════════════════════════════════════════

VALIDATION ENFORCEMENT:

After SUBPLAN creation, these scripts will run:
✓ validate_execution_start.py (checks SUBPLAN prerequisites)
✓ check_plan_size.py (validates parent PLAN still within limits)
✓ validate_registration.py (verifies SUBPLAN registered in PLAN)

If issues found: BLOCKS with error + fix prompt

DO NOT:
❌ Create SUBPLAN without following template
❌ Skip EXECUTION_TASK creation
❌ Create SUBPLAN without registering in PLAN
```

**Placeholders to Replace**:

- `[X.Y]`: Achievement number
- `[ACHIEVEMENT_TITLE]`: Achievement title from PLAN
- `[X-Y hours]`: Effort estimate
- `[FEATURE]`: Feature name
- `[NUMBER]`: Next SUBPLAN number (01, 02, 03, ...)

**Example**:

```
Create SUBPLAN for Achievement 1.1 in @PLAN_LLM-V2-BACKLOG.md

Achievement Details:
- Number: 1.1
- Title: Meta-PLAN Predefined Prompts
- Effort: 8-12 hours

Create: SUBPLAN_LLM-V2-BACKLOG_02.md
[... proceed with SUBPLAN creation ...]
```

---

## 🎯 Advanced Prompts

### 7. Pause PLAN (Context Switching)

**Template**:

```
Pause @PLAN_[FEATURE].md at Achievement [X.Y] to switch context

Before Pausing:
- [ ] Update PLAN "Current Status & Handoff" section
- [ ] Document: What's done, what's next, blockers
- [ ] Commit all changes: git commit -m "Pausing PLAN_[FEATURE] at Achievement [X.Y]"
- [ ] Update @ACTIVE_PLANS.md status to "⏸️ Paused"
- [ ] Update "Last Updated" timestamp

Now ready to switch to different PLAN using Resume protocol
```

---

### 8. Add Achievement to PLAN (Dynamic)

**Template**:

```
Add new Achievement [X.Y] to @PLAN_[FEATURE].md (gap discovered during execution)

Achievement Details:
- Number: [X.Y] (next available in this priority)
- Title: [ACHIEVEMENT_TITLE]
- Why: [GAP_DISCOVERED]
- Discovered In: [EXECUTION_TASK_XX_YY]
- Priority: [Critical/High/Medium/Low]
- Effort: [X-Y hours]

Add to "Achievement Addition Log" section:
- Use format from PLAN template
- Include discovery context
- Note parent achievement if sub-achievement

Then update "Subplan Tracking" section when creating SUBPLAN for new achievement
```

---

### 9. Create Mid-Plan Review Checkpoint

**When to Use**:

- After 20 hours of work
- After completing Priority 3
- After 1 month calendar time
- Before creating 10th SUBPLAN

**Template**:

```
Create Mid-Plan Review for @PLAN_[FEATURE].md following @LLM/guides/IMPLEMENTATION_MID_PLAN_REVIEW.md

Review Trigger: [20 hours / Priority 3 / 1 month / 10 SUBPLANs]

Checklist:

1. Execution Health (5 min)
   - Review PLAN "Summary Statistics"
   - Check avg iterations (<4 target)
   - Check circular debugging (<2 target)
   - Check time vs estimate

2. Methodology Compliance (10 min)
   - Naming compliance
   - EXECUTION_TASKs complete
   - Subplan tracking updated
   - Statistics current

3. Technical Debt Check (15 min)
   - Test coverage maintained
   - Linters passing
   - TODO comments extracted
   - Code quality consistent

4. Learning Extraction (10 min)
   - Key learnings extracted to PLAN
   - Patterns documented
   - Methodology improvements noted

5. Scope & Priority Review (10 min)
   - Original scope maintained
   - Priorities still valid
   - Achievements complete meet criteria

6. GrammaPlan Consideration (5 min)
   - Re-check criteria if PLAN growing
   - Decide: continue or convert

7. Process Efficiency Review (10 min)
   - Reflect on recent work
   - Identify patterns in blockers
   - Document insights

Add Mid-Plan Review summary to PLAN "Current Status & Handoff"
```

---

## 💡 Usage Tips

### When to Use Predefined vs Custom Prompts

**Use Predefined Prompts When**:

- Following standard workflows (Create, Resume, Complete)
- Want consistency and completeness
- New to methodology (learning by using)
- Working in team (shared process)

**Customize or Skip When**:

- Unique workflow not covered by prompts
- Very simple task (prompts may be overkill)
- Experienced with methodology (internalized process)
- Special circumstances require deviation

### How to Customize Prompts

1. **Copy the template** from this file
2. **Replace placeholders** with your specific values
3. **Add/remove steps** based on your needs
4. **Keep the structure** (checklists, references to @files)
5. **Test your prompt** before using in production

### Troubleshooting

**Prompt Too Long?**
→ Remove optional steps, keep only critical path

**LLM Confused?**
→ Add more context, clarify placeholders

**Missing Steps?**
→ Compare to protocol document (@LLM/protocols/IMPLEMENTATION_START_POINT.md, etc.)

**Prompt Out of Date?**
→ Check protocol documents for updates, revise prompt

---

### 10. Create NORTH_STAR (New)

**When to Use**:

- Creating strategic vision document for methodology, learning frameworks, or cross-domain principles
- Document spans 800-2,000 lines of strategic guidance
- Need to illuminate/coordinate multiple GrammaPlans or PLANs

**Template**:

```
Create a new NORTH_STAR for [TOPIC] following @LLM/guides/NORTH-STAR-GUIDE.md

Context:
- Topic: [STRATEGIC TOPIC - e.g., METHODOLOGY-EVOLUTION, MULTI-AGENT-COORDINATION]
- Strategic Vision: [2-3 sentences of strategic intent]
- Scope: [What domains/areas does this illuminate?]

Deliverables:
- Location: work-space/north-stars/NORTH_STAR_[TOPIC].md
- Use: @LLM/templates/NORTH_STAR-TEMPLATE.md
- Size: 800-2,000 lines (strategic vision expected to be comprehensive)

Key Sections (from template):
- Strategic Vision (2-4 paragraphs explaining long-term direction)
- Core Principles (5-7 guiding principles)
- Coordination (which PLANs/GrammaPlans does this illuminate?)
- Current State (where are we now?)
- Evolution History (how have we gotten here?)

After Creation:
- Verify size 800-2,000 lines (informational warning if <800, must split if >2,000)
- Update @ACTIVE_PLANS.md if tracking methodology work
- Reference from related GrammaPlans or PLANs

═══════════════════════════════════════════════════════════════════════

VALIDATION ENFORCEMENT:

After NORTH_STAR creation, these scripts will run:
✓ check_north_star_size.py (validates 800-2,000 line limits)

If issues found: BLOCKS with error + fix prompt

DO NOT:
❌ Create NORTH_STAR for tactical work (use PLAN instead)
❌ Exceed 2,000 lines (must split into multiple NORTH_STARs)
❌ Make NORTH_STAR too vague (must be specific principles/vision)
```

**Placeholders to Replace**:

- `[TOPIC]`: Strategic topic in kebab-case (e.g., `LLM-METHODOLOGY`, `MULTI-AGENT-LEARNING`)
- `[2-3 sentences...]`: Clear strategic intent

**Example**:

```
Create a new NORTH_STAR for MULTI-AGENT-COORDINATION following @LLM/guides/NORTH-STAR-GUIDE.md

Context:
- Topic: MULTI-AGENT-COORDINATION
- Strategic Vision: Enable parallel concurrent execution of multiple LLM agents with coordination, learning, and shared context
- Scope: Agent design patterns, execution coordination, learning synthesis, context management

[... LLM proceeds to create NORTH_STAR ...]
```

---

### 11. Create SUBPLAN (Designer Phase) (New)

**When to Use**:

- You have selected an achievement from a PLAN
- You're ready to design the approach (Designer phase)
- You need to plan execution strategy (single or multiple EXECUTIONs)

**Template**:

```
Create SUBPLAN for @PLAN_[FEATURE_NAME].md Achievement [X.Y] following @LLM/protocols/CREATE_SUBPLAN.md

Achievement Context:
- Achievement: [X.Y: Title]
- Mother PLAN: PLAN_[FEATURE_NAME].md
- Strategic Goal: [One sentence from PLAN achievement]

Design Phase (READ ONLY these from PLAN):
- Read PLAN achievement section [X.Y] (50-100 lines)
- Read any achievement prerequisites
- Understand required deliverables
- **Do NOT read full PLAN** (Designer focuses on one achievement)

Designer Responsibilities:
1. Create SUBPLAN_[FEATURE]_[NEXT_NUMBER].md in work-space/subplans/
2. Design approach (strategy, key steps, HOW to do it)
3. Decide execution strategy:
   - Single EXECUTION? (linear work)
   - Multiple EXECUTIONs? (parallel or sequential)
4. If multiple: plan each EXECUTION's purpose and coordination
5. Specify exact deliverables and success criteria
6. Document in SUBPLAN following @LLM/templates/SUBPLAN-TEMPLATE.md

Location: work-space/subplans/SUBPLAN_[FEATURE]_[NUMBER].md
Size: 200-600 lines
Template: @LLM/templates/SUBPLAN-TEMPLATE.md
Guide: @LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md

Key Sections:
- Objective: What we're achieving
- Deliverables: Exact files/functions to create/modify
- Approach: Strategy and key steps (how, not what)
- Execution Strategy: Single or Multiple EXECUTIONs?
- Planned Executions (if multiple): Purpose, parallelization, coordination
- Expected Results: Observable outcomes, success criteria

After SUBPLAN Complete:
- Size validation will run automatically
- Next step: Create EXECUTION_TASK(s) for Phase 2 (Execution Planning)

═══════════════════════════════════════════════════════════════════════

DO NOT:
❌ Execute while designing (design first, execute later)
❌ Make SUBPLAN too prescriptive (Executor needs some autonomy)
❌ Skip execution strategy decision
❌ Forget to specify deliverables
```

**Placeholders to Replace**:

- `[FEATURE_NAME]`: Feature name from PLAN
- `[X.Y]`: Achievement number (e.g., 2.1)
- `[NEXT_NUMBER]`: Sequential number for this SUBPLAN (01, 02, etc.)

**Example**:

```
Create SUBPLAN for @PLAN_GRAPHRAG-VALIDATION.md Achievement 1.1 following @LLM/protocols/CREATE_SUBPLAN.md

Achievement Context:
- Achievement: 1.1: End-to-End Pipeline Validation
- Mother PLAN: PLAN_GRAPHRAG-VALIDATION.md
- Strategic Goal: Validate GraphRAG pipeline with production data

[... LLM creates SUBPLAN_GRAPHRAG-VALIDATION_01.md ...]
```

---

### 12. Create EXECUTION from SUBPLAN (Executor Phase) (New)

**When to Use**:

- Designer has completed SUBPLAN (Phase 1)
- You're ready to execute the SUBPLAN (Executor phase)
- You need to create EXECUTION_TASK and start work

**Template**:

```
Create and start EXECUTION_TASK for @SUBPLAN_[FEATURE]_[NUMBER].md following @LLM/protocols/CREATE_EXECUTION.md

SUBPLAN Context (READ ONLY):
- Read SUBPLAN objective (1-2 sentences) ← That's all you need
- Read SUBPLAN approach summary (3-5 sentences) ← Designer's plan
- **Do NOT read full SUBPLAN** (Designer already decided approach)
- If parallel: Read parallelization context section

Executor Responsibilities:
1. Create EXECUTION_TASK_[FEATURE]_[SUBPLAN]_[EXEC].md in work-space/execution/
2. Set up header with SUBPLAN/PLAN references
3. Add SUBPLAN context section (minimal reading!)
4. Create tests (if code work) and run initially (should fail)
5. Iterate: make changes → run tests → document
6. After every iteration: update EXECUTION_TASK with learnings
7. Check for circular debugging every 3 iterations
8. When complete: mark EXECUTION_TASK complete and update SUBPLAN

Location: work-space/execution/EXECUTION_TASK_[FEATURE]_[SUBPLAN]_[EXEC].md
Size: <200 lines
Template: @LLM/templates/EXECUTION_TASK-TEMPLATE.md
Guide: @LLM/protocols/CREATE_EXECUTION.md

Key Sections:
- Header: SUBPLAN/PLAN references, execution number
- SUBPLAN Context: Read objective + approach only!
- Test Creation Phase (if applicable)
- Iteration Log: Updated after EVERY iteration
- Circular Debug Check: Every 3 iterations
- Learning Summary: Captured learnings

During Execution:
- Follow Designer's plan (that's what SUBPLAN is for)
- Test-driven development (write tests first)
- Document every iteration
- Capture learnings in code comments
- If circular debugging: abandon EXECUTION, create new one

═══════════════════════════════════════════════════════════════════════

DO NOT:
❌ Read full SUBPLAN (it's too much context, Designer already decided)
❌ Skip test creation (tests define what success means)
❌ Skip iteration documentation (every iteration matters)
❌ Modify tests to make them pass (fix implementation instead)
❌ Continue past circular debugging (change strategy, create new EXECUTION)
```

**Placeholders to Replace**:

- `[FEATURE]`: Feature name from PLAN
- `[SUBPLAN]`: SUBPLAN number (01, 02, etc.)
- `[EXEC]`: Execution number (01, 02, etc.)

**Example**:

```
Create and start EXECUTION_TASK for @SUBPLAN_GRAPHRAG-VALIDATION_01.md following @LLM/protocols/CREATE_EXECUTION.md

SUBPLAN Context:
- Objective: Validate GraphRAG query pipeline end-to-end
- Approach: Test with production-scale data, capture metrics, verify correctness

[... LLM creates EXECUTION_TASK_GRAPHRAG-VALIDATION_01_01.md and begins execution ...]
```

---

### 13. Synthesize SUBPLAN Results (New)

**When to Use**:

- Multiple EXECUTION_TASKs (parallel or sequential) have completed
- Designer phase: need to synthesize collective learnings
- SUBPLAN needs synthesis section populated
- Ready to mark SUBPLAN complete

**Template**:

```
Synthesize results from completed EXECUTION_TASKs for @SUBPLAN_[FEATURE]_[NUMBER].md

SUBPLAN Context:
- Read full SUBPLAN including all EXECUTION results
- Review each completed EXECUTION_TASK:
  - EXECUTION_TASK_[FEATURE]_[NUMBER]_01.md
  - EXECUTION_TASK_[FEATURE]_[NUMBER]_02.md
  - [etc.]

Synthesis Responsibilities:
1. Review all EXECUTION_TASK learnings and results
2. In SUBPLAN "Execution Results Synthesis" section:
   a) Compare results (if parallel executions)
   b) Evaluate success of each execution
   c) Document collective learnings
   d) Recommend best approach (if A/B testing)
   e) Identify patterns across executions
   f) Extract insights for future work

3. If multiple EXECUTIONs:
   - Create comparison table or analysis
   - Evaluate which approach was most effective
   - Document why (what made it better?)
   - Recommend for production/future work

4. Update SUBPLAN:
   - Mark "Execution Results Synthesis" section complete
   - Mark SUBPLAN status as "Complete"
   - Archive entire SUBPLAN + all EXECUTION_TASKs

Follow: @LLM/protocols/IMPLEMENTATION_END_POINT.md for archival

═══════════════════════════════════════════════════════════════════════

DO NOT:
❌ Mark SUBPLAN complete until ALL EXECUTIONs complete
❌ Skip synthesis section
❌ Leave execution results undocumented
❌ Fail to recommend best approach (if applicable)
```

**Placeholders to Replace**:

- `[FEATURE]`: Feature name from PLAN
- `[NUMBER]`: SUBPLAN number
- List all EXECUTION_TASK files by number

**Example**:

```
Synthesize results from completed EXECUTION_TASKs for @SUBPLAN_GRAPHRAG-VALIDATION_01.md

EXECUTIONs to synthesize:
- EXECUTION_TASK_GRAPHRAG-VALIDATION_01_01.md ✅ Complete
- EXECUTION_TASK_GRAPHRAG-VALIDATION_01_02.md ✅ Complete

[... LLM synthesizes learnings and completes SUBPLAN ...]
```

---

## 🔄 Maintenance

### When to Update Prompts

**Update prompts if**:

- Methodology protocols change (START_POINT, END_POINT, RESUME updated)
- New templates added (new document types)
- Process improvements discovered
- User feedback indicates confusion

### Prompt Versioning

**Current Version**: 1.1 (November 2025)

**Version History**:

- 1.1 (2025-11-09): Added Designer/Executor phase separation prompts (NORTH_STAR, Create SUBPLAN, Create EXECUTION, Synthesize)
- 1.0 (2025-11-07): Initial prompt library created

**To Update**:

1. Edit this file (PROMPTS.md)
2. Update version number
3. Add to version history
4. Notify users of changes (in CHANGELOG.md if significant)

---

## 📚 Examples from Real Usage

### Example 1: Creating PLAN_GRAPHRAG-VALIDATION

**Prompt Used**:

```
Create a new PLAN for GRAPHRAG-VALIDATION following @LLM/protocols/IMPLEMENTATION_START_POINT.md
...
```

**Result**: Clean PLAN created in ~10 minutes, all sections present, GrammaPlan consideration documented

---

### Example 2: Resuming PLAN_ENTITY-RESOLUTION-REFACTOR

**Prompt Used**:

```
Resume @PLAN_ENTITY-RESOLUTION-REFACTOR.md following @LLM/protocols/IMPLEMENTATION_RESUME.md protocol
...
```

**Result**: Resume checklist completed, context restored, work continued smoothly

---

### Example 3: Completing PLAN_CODE-QUALITY-REFACTOR

**Prompt Used**:

```
Complete @PLAN_CODE-QUALITY-REFACTOR.md following @LLM/protocols/IMPLEMENTATION_END_POINT.md
...
```

**Result**: Complete wrapup, archive created, learnings extracted, backlog updated

---

## 🎓 Learnings & Best Practices

### Best Practice 1: Always Reference @Files

**Why**: Prompts should guide LLM to read authoritative sources, not replicate content

**Example**: `following @LLM/protocols/IMPLEMENTATION_START_POINT.md` instead of listing all START_POINT steps

### Best Practice 2: Include Verification Steps

**Why**: Prompts should enforce quality gates

**Example**: "Verify only ONE PLAN 'In Progress'" in Resume prompt

### Best Practice 3: Use Real Examples

**Why**: Concrete examples clarify abstract instructions

**Example**: Show actual PLAN names, real achievement numbers

### Best Practice 4: Make Placeholders Obvious

**Why**: Users should instantly know what to replace

**Example**: `[FEATURE_NAME]` in brackets vs ambiguous "feature name"

---

## 🔗 Related Documents

- **Entry Point**: IMPLEMENTATION_START_POINT.md
- **Resume Point**: IMPLEMENTATION_RESUME.md
- **Exit Point**: IMPLEMENTATION_END_POINT.md
- **GrammaPlan Guide**: LLM/guides/GRAMMAPLAN-GUIDE.md
- **Mid-Plan Reviews**: LLM/guides/IMPLEMENTATION_MID_PLAN_REVIEW.md
- **Templates**: LLM/templates/ (PLAN, SUBPLAN, EXECUTION_TASK, GRAMMAPLAN)

---

**Status**: Active and ready for use  
**Created**: PLAN_LLM-V2-BACKLOG Achievement 1.1  
**Maintained By**: Meta-PLAN (PLAN_STRUCTURED-LLM-DEVELOPMENT.md)  
**Version**: 1.0 (November 2025)
