# PLAN: [Feature Name]

**Type**: PLAN  
**Status**: Planning / In Progress / Complete  
**Priority**: Critical / High / Medium / Low  
**Created**: [YYYY-MM-DD HH:MM UTC]  
**Goal**: [One sentence describing what this plan achieves]

**Metadata Tags**: See `LLM/guides/METADATA-TAGS.md` for virtual organization system

[FILL: Use UTC timestamps for precise tracking. Example: 2025-11-05 14:30 UTC]

[FILL: Replace [Feature Name] with short, descriptive name using kebab-case (e.g., OPTIMIZE-EXTRACTION)]

---

## 📖 Context for LLM Execution

**If you're an LLM reading this to execute work**:

1. **What This Plan Is**: [Brief description]
2. **Your Task**: [What you need to implement]
3. **How to Proceed**:
   - Read the achievements below
   - Select one to work on
   - Create a SUBPLAN with your approach
   - Create an EXECUTION_TASK to log your work
   - Follow the TDD workflow in IMPLEMENTATION_START_POINT.md
4. **What You'll Create**: [List of deliverables]
5. **Where to Get Help**: IMPLEMENTATION_START_POINT.md, templates, related docs
6. **Project Context**: For essential project knowledge (structure, domain, conventions, architecture), see `LLM/PROJECT-CONTEXT.md`
   - **When to Reference**: New sessions, unfamiliar domains, architecture questions, convention questions
   - **Automatic Injection**: The prompt generator (`generate_prompt.py`) automatically includes project context in generated prompts
   - **Manual Reference**: If you need more detail, read `LLM/PROJECT-CONTEXT.md` directly

**Self-Contained**: This PLAN contains everything you need to execute it.

**File Location**: Create this PLAN in `work-space/plans/PLAN_[FEATURE].md`

[FILL: Make this section specific to your plan. Provide enough context that an LLM can understand and execute without external information.]

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
- Achievement Addition Log (unless adding achievement)

**Context Budget**: ~200 lines per achievement

**Why**: PLAN defines WHAT to achieve. Reading all achievements at once causes context overload. Focus on current achievement only.

**📖 See**: `LLM/guides/FOCUS-RULES.md` for complete focus rules and examples.

---

## 📋 Achievement Index

**All Achievements in This Plan** (for sequence reference):

**Priority 0: IMMEDIATE (COMPLETE ✅)**

- ✅ Achievement 0.1: [Title]
- ✅ Achievement 0.2: [Title]
- ✅ Achievement 0.3: [Title]

**Priority 1: FOUNDATION**

- ✅ Achievement 1.1: [Title]
- ✅ Achievement 1.2: [Title]
- Achievement 1.3: [Title] (in progress)

**Priority 2: HIGH**

- Achievement 2.1: [Title]
- Achievement 2.2: [Title]

**Priority 3: MEDIUM**

- Achievement 3.1: [Title]

[FILL: List ALL achievements from this PLAN in sequence. Mark completed achievements with ✅. This provides a quick reference and helps scripts detect the full achievement sequence.]

**Purpose**:

- Quick reference for achievement sequence
- Enables scripts to detect all achievements without parsing full PLAN
- Shows progress at a glance (✅ = completed via APPROVED feedback)
- Helps detect completion via feedback files (APPROVED_XX.md)

**Completion Tracking** (Filesystem-First):

- Achievement completion is determined by presence of `execution/feedbacks/APPROVED_XX.md` file
- Scripts check for APPROVED feedback file to mark achievement as complete
- Update this index with ✅ when APPROVED feedback exists
- See `LLM/docs/FEEDBACK_SYSTEM_GUIDE.md` for complete conventions

---

## 📋 Current Status & Handoff

**Last Updated**: [YYYY-MM-DD HH:MM UTC]  
**Status**: 🎯 [Planning / 🚀 In Progress / ✅ Complete]

[FILL: Update this section as work progresses to provide context for next executor]

**Context**:

- [What's the current situation?]
- [Any recent changes or decisions?]
- [What context does next executor need?]

**What's Done**:

- ✅ [Completed achievement or milestone]
- ✅ [Another completed item]

**What's Next**:

- ⏳ [Next achievement or task]
- [Any blockers or issues?]

**Archive Location** (when complete): `documentation/archive/[feature-name]-YYYY-MM/`

[FILL: Keep this section updated as the plan progresses. This helps with handoffs between sessions and provides quick status updates.]

---

## 🎯 Goal

[FILL: 1-2 paragraphs describing what we're building and why it matters]

**Example**:

> Implement a caching layer for frequently accessed data to improve query performance by 10x and reduce database load by 80%.

---

## 📖 Problem Statement

**Current State**:
[FILL: Describe the current situation]

**What's Wrong/Missing**:
[FILL: Explain the problem or gap]

**Impact**:
[FILL: Why this matters, what's the cost of not fixing it]

---

## 🎯 Success Criteria

### Must Have

- [ ] [Required outcome 1 - must be testable/measurable]
- [ ] [Required outcome 2]
- [ ] [Required outcome 3]

### Should Have

- [ ] [Important outcome 1]
- [ ] [Important outcome 2]

### Nice to Have

- [ ] [Bonus outcome 1]
- [ ] [Bonus outcome 2]

[FILL: Make criteria specific and measurable. Each should answer "how do we know we're done?"]

---

## 📋 Scope Definition

### In Scope

- [FILL: What we will do]
- [FILL: What's included]
- [FILL: Boundaries of this work]

### Out of Scope

- [FILL: What we won't do]
- [FILL: What's explicitly excluded]
- [FILL: Rationale for exclusions]

[FILL: Be explicit about boundaries to prevent scope creep]

---

## 📏 Size Limits

**⚠️ HARD LIMITS** (Must not exceed):

- **Lines**: 900 lines maximum
- **Estimated Effort**: 40 hours maximum

**Size Guidelines**:

- **300-699 lines**: Typical PLAN (comfortable size)
- **700-899 lines**: Large PLAN - **Warning**: Approaching limit, ensure focus maintained
- **900+ lines**: **Error** - Must convert to GrammaPlan or split

**Workflow Context**:

- **PLANs now provide context for SUBPLAN creation only, not execution**
- With workflow separation, larger PLANs don't bloat execution context
- Planner agent reads PLAN achievement (~100 lines) when creating SUBPLAN
- Executor agent reads SUBPLAN objective (~2 sentences), not full PLAN
- This enables realistic size limits without context bloat

**If your PLAN exceeds these limits**:

- **MUST** convert to GrammaPlan (not optional)
- See `LLM/guides/GRAMMAPLAN-GUIDE.md` for guidance
- Run `python LLM/scripts/validation/check_plan_size.py @PLAN_FILE.md` to validate

**Validation**:

- Script will **BLOCK** (exit code 1) if limits exceeded
- Warning at 700 lines: "Approaching limit, ensure focus maintained"
- Error at 900 lines: "MUST convert to GrammaPlan or split"

---

## 🌳 GrammaPlan Consideration

**Was GrammaPlan considered?**: [Yes / No]

**Decision Criteria Checked**:

- [ ] Plan would exceed 900 lines? [Yes/No] ⚠️ **HARD LIMIT**
- [ ] Estimated effort > 40 hours? [Yes/No] ⚠️ **HARD LIMIT**
- [ ] Work spans 4+ domains? [Yes/No]
- [ ] Natural parallelism opportunities? [Yes/No]

**Decision**: [Single PLAN / GrammaPlan]

**⚠️ IMPORTANT**: If ANY of the first two criteria are "Yes", GrammaPlan is **REQUIRED** (not optional).

**Rationale**:

[FILL: If Single PLAN chosen, explain why:]

- [Reason 1]
- [Reason 2]

[FILL: If GrammaPlan chosen, see GRAMMAPLAN-TEMPLATE.md]

**See**: `LLM/guides/GRAMMAPLAN-GUIDE.md` for complete criteria and guidance

**Case Study**: EXECUTION_ANALYSIS_CODE-QUALITY-COMPLETION-REVIEW.md analyzes a 1,247-line plan that should have been a GrammaPlan

---

## 🎯 Desirable Achievements (Priority Order)

[FILL: List WHAT needs to be achieved, not HOW to achieve it. Subplans (HOW) are created on-demand.]

### Priority 1: CRITICAL

**Achievement 1.1**: [Title]

- [What needs to exist]
- [Why it's valuable]
- Success: [How we know it's done]
- Effort: [Hours estimate]
- **Deliverables**:
  - [List of files, functions, features to create]
  - **Test file** (required for code work): `tests/LLM/scripts/<domain>/test_<script_name>.py`
- **Testing Requirements** (required for code work, optional for documentation):
  - **Test File Naming**: `test_<script_name>.py` in `tests/LLM/scripts/<domain>/`
  - **Coverage Requirement**: >90% for new code
  - **Test Cases Required**:
    - Unit tests for all new functions/classes
    - Integration tests for workflows
    - Edge case tests for error handling
  - **Test Infrastructure**: Use existing fixtures from `tests/LLM/scripts/conftest.py`
  - **TDD Workflow**: Write tests first (preferred), then implement
  - **Example**: See `PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md` for good testing practice
- **Archive Location**: Use archive location from PLAN's "Archive Location" section (typically `documentation/archive/FEATURE-NAME/`)
  - Create archive structure if needed: `mkdir -p documentation/archive/FEATURE-NAME/{subplans,execution}`
  - Archive SUBPLANs to `subplans/` subdirectory
  - Archive EXECUTION_TASKs to `execution/` subdirectory
  - **Deferred Archiving**: Archive at achievement completion (not immediately upon file completion)

**Sub-Achievements** (may be discovered during execution):

- 1.1.1: [If main achievement has logical sub-parts]
- (More may be added as gaps discovered)

**Achievement 1.2**: [Title]

- [Description]
- Success: [Criteria]
- Effort: [Estimate]
- **Archive Location**: Use archive location from PLAN's "Archive Location" section (typically `documentation/archive/FEATURE-NAME/`)
  - Create archive structure if needed: `mkdir -p documentation/archive/FEATURE-NAME/{subplans,execution}`
  - Archive SUBPLANs to `subplans/` subdirectory
  - Archive EXECUTION_TASKs to `execution/` subdirectory
  - **Deferred Archiving**: Archive at achievement completion (not immediately upon file completion)

### Priority 2: HIGH

**Achievement 2.1**: [Title]

- [Description]
- **Archive Location**: Use archive location from PLAN's "Archive Location" section (typically `documentation/archive/FEATURE-NAME/`)
  - Create archive structure if needed: `mkdir -p documentation/archive/FEATURE-NAME/{subplans,execution}`
  - Archive SUBPLANs to `subplans/` subdirectory
  - Archive EXECUTION_TASKs to `execution/` subdirectory
  - **Deferred Archiving**: Archive at achievement completion (not immediately upon file completion)

### Priority 3: MEDIUM

**Achievement 3.1**: [Title]

- [Description]

### Priority 4: LOW

**Achievement 4.1**: [Title]

- [Description]

[FILL: Organize by priority. Achievements guide subplan creation.]

---

## 🎯 Achievement Addition Log

**Dynamically Added Achievements**:

_None yet - will be added if gaps discovered during execution_

**Format When Adding**:

```
**Achievement X.Y**: [Title]
- Added: [date]
- Why: [Gap discovered during execution]
- Discovered In: [EXECUTION_TASK that revealed this]
- Priority: [Critical/High/Medium/Low]
- Parent Achievement: [If this is a sub-achievement]
```

[FILL: Update this section if you discover new achievements during execution]

---

## 🔄 Active Components (Updated When Created)

**Current Active Work** (register components immediately when created):

**Active SUBPLANs**:

- [ ] **SUBPLAN_FEATURE_XX**: [Achievement] - Status: In Progress
      └─ [ ] EXECUTION_TASK_FEATURE_XX_YY: Status: In Progress

**Active EXECUTION_TASKs** (without parent SUBPLAN):

- [ ] **EXECUTION_TASK_FEATURE_XX_YY**: Status: In Progress

**Registration Workflow**:

1. When creating SUBPLAN: Add to "Active SUBPLANs" above
2. When creating EXECUTION_TASK: Add under parent SUBPLAN or to "Active EXECUTION_TASKs"
3. When archiving: Move from "Active" to "Subplan Tracking" below

**Why**: Immediate parent awareness ensures focus enforcement and prevents orphaned components.

---

## 🔄 Subplan Tracking (Updated During Execution)

**Summary Statistics** (update after each EXECUTION_TASK completion):

- **SUBPLANs**: [0] created ([0] complete, [0] in progress, [0] pending)
- **EXECUTION_TASKs**: [0] created ([0] complete, [0] abandoned)
- **Total Iterations**: [0] (across all EXECUTION_TASKs)
- **Average Iterations**: [0.0] per task
- **Circular Debugging**: [0] incidents (EXECUTION_TASK_XX_YY_02 or higher)
- **Time Spent**: [0h] (from EXECUTION_TASK completion times)

**Subplans Created for This PLAN**:

_None yet - will be added as subplans are created_

**Format**:

```
- SUBPLAN_XX: [Achievement addressed] - [Brief description] - Status: [Not Started/In Progress/Complete]
  └─ EXECUTION_TASK_XX_YY: [Brief description] - Status: [In Progress/Complete/Abandoned] (N iterations, Xh)
```

**Example**:

```
- SUBPLAN_01: Achievement 1.1 - Status: Complete ✅
  └─ EXECUTION_TASK_01_01: First attempt - Status: Complete ✅ (3 iterations, 2h)
  └─ EXECUTION_TASK_01_02: Second attempt (circular debug recovery) - Status: Complete ✅ (5 iterations, 3h)
```

**Instructions**:

- Add each subplan when created
- Update status as work progresses
- **Update summary statistics after each EXECUTION_TASK completion**
- Track iterations and time from EXECUTION_TASK documents

[FILL: Update this section as subplans are created. Shows progress at a glance. Statistics enable END_POINT quality analysis.]

---

## 🔗 Constraints

### Technical Constraints

- [FILL: Technical limitations]
- [FILL: System requirements]
- [FILL: Integration requirements]

### Process Constraints

- [FILL: Methodology requirements]
- [FILL: Testing requirements]
- [FILL: Documentation requirements]

### Resource Constraints

- [FILL: Time limits]
- [FILL: Dependencies on other work]
- [FILL: Available resources]

---

## 📚 References & Context

### Related Plans

[FILL: Document dependencies on other PLANs using MULTIPLE-PLANS-PROTOCOL.md format]

**Format**:

```markdown
**PLAN_DEPENDENCY_NAME.md**:

- **Type**: [Hard / Soft / Data / Code / Sequential]
- **Relationship**: [Description of relationship]
- **Dependency**: [What this PLAN needs from dependency]
- **Status**: [Blocked / Ready / Can proceed]
- **Timing**: [When to work on this relative to dependency]
```

**Example**:

```markdown
**PLAN_ENTITY-RESOLUTION-REFACTOR.md**:

- **Type**: Hard dependency
- **Relationship**: Sequential (entity resolution → graph construction)
- **Dependency**: Graph construction depends on stable entity_ids
- **Status**: Ready (Priorities 0-3 and 3.5 complete)
- **Timing**: After entity resolution (Priorities 0-3 and 3.5 complete)
```

**Before creating PLAN**: Check ACTIVE_PLANS.md for related PLANs and dependencies. See `LLM/guides/MULTIPLE-PLANS-PROTOCOL.md` for complete guidance.

### Related Documentation

- [FILL: Link to related guides]
- [FILL: Link to reference docs]
- [FILL: Link to related archives]

### Related Code

- [FILL: Files that will be modified]
- [FILL: Modules affected]
- [FILL: Tests to update]

### Related Archives

- [FILL: Previous work this builds on]
- [FILL: Similar implementations]

### Dependencies

- [FILL: What must exist before starting]
- [FILL: External dependencies]

---

## ⏱️ Time Estimates

**Total Estimated Effort**: [X-Y hours across all achievements]

**By Priority**:

- Priority 1 (Critical): [hours]
- Priority 2 (High): [hours]
- Priority 3 (Medium): [hours]
- Priority 4 (Low): [hours]

[FILL: Provide realistic estimates based on achievement complexity]

---

## 📝 Meta-Learning Space

[FILL: As you execute this PLAN, document insights here]

**What Worked**:

- [Learning 1]

**What Didn't Work**:

- [Challenge 1]

**Methodology Improvements**:

- [Improvement suggested]

[FILL: This section grows during execution. Captures process insights.]

---

## 🎓 Key Learnings (Updated During Execution)

**Technical Learnings**:

1. [Learning 1] - Discovered in: [EXECUTION_TASK_XX_YY] - [Date]
2. [Learning 2] - Discovered in: [EXECUTION_TASK_XX_YY] - [Date]

**Process Learnings**:

1. [Learning 1] - Discovered in: [EXECUTION_TASK_XX_YY] - [Date]
2. [Learning 2] - Discovered in: [EXECUTION_TASK_XX_YY] - [Date]

**Code Patterns Discovered**:

1. [Pattern 1] - Applied in: [Files/modules] - [EXECUTION_TASK reference]
2. [Pattern 2] - Applied in: [Files/modules] - [EXECUTION_TASK reference]

**Instructions**:

- Update this section as you work (don't wait until the end)
- Extract key learnings from EXECUTION_TASK "Learning Summary" sections
- Reference the EXECUTION_TASK where each learning was discovered
- Makes learning extraction easier at IMPLEMENTATION_END_POINT

[FILL: Add learnings incrementally during execution. This makes END_POINT learning extraction much faster and prevents loss of insights.]

---

## ✅ Pre-Completion Review (MANDATORY Before Marking Complete)

**⚠️ DO NOT mark status as "Complete" until this review is done!**

**Review Date**: [YYYY-MM-DD HH:MM UTC]  
**Reviewer**: [Name/Role]

### END_POINT Compliance Checklist

- [ ] **All achievements met** (verify in "Desirable Achievements" section above)
- [ ] **Execution statistics complete** (verify in "Subplan Tracking" section)
  - [ ] All SUBPLAN/EXECUTION_TASK counts accurate
  - [ ] Total iterations calculated
  - [ ] Circular debugging incidents counted
  - [ ] Time spent totaled
- [ ] **Pre-archiving checklist complete** (from IMPLEMENTATION_END_POINT.md)
  - [ ] All pending changes accepted in editor
  - [ ] Test suite passing (if code changes)
  - [ ] Linters passing (if code changes)
  - [ ] All changes committed (git status clean)
- [ ] **Backlog updated** (IMPLEMENTATION_BACKLOG.md has new items extracted)
  - [ ] All EXECUTION_TASKs reviewed for future work
  - [ ] At least [3-5] items added to backlog (for plans >20 hours)
- [ ] **Process improvement analysis done**
  - [ ] "What worked" documented (in Meta-Learning Space)
  - [ ] "What didn't work" documented (in Meta-Learning Space)
  - [ ] Methodology improvements identified
- [ ] **Learning extraction complete**
  - [ ] Technical learnings aggregated (in Key Learnings section)
  - [ ] Process learnings aggregated (in Key Learnings section)
  - [ ] Relevant documentation updated
- [ ] **Ready for archiving**
  - [ ] Archive structure planned (see Archive Plan section below)
  - [ ] INDEX.md content prepared
  - [ ] Completion summary drafted

### Sign-Off

**Reviewer**: [Name] - [Date]  
**Status**: [ ] Pending / [✅] Approved for Completion

**If NOT Approved**: [List missing items that must be completed first]

**Once Approved**: Update PLAN status to "Complete" and proceed with archiving per IMPLEMENTATION_END_POINT.md

[FILL: This review is MANDATORY. Do not skip. Prevents incomplete completions like CODE-QUALITY case study showed.]

---

## 📦 Archive Location

**⚠️ CRITICAL**: Create archive folder at PLAN start (see IMPLEMENTATION_START_POINT.md).

**Default Location**: `documentation/archive/<feature>-<date>/` (replace `feature` with your feature name)

**Example**: `documentation/archive/methodology-v2-enhancements-nov2025/`

**Note**: PLAN files are created in `work-space/plans/` directory. Archive location is separate from workspace.

**Structure**:

```
./feature-archive/
├── subplans/
│   └── SUBPLAN_FEATURE_*.md (archived at achievement/plan completion)
└── execution/
    └── EXECUTION_TASK_FEATURE_*_*.md (archived at achievement/plan completion)
```

**Creation**:

- Create at PLAN start: `mkdir -p ./feature-archive/{subplans,execution}`
- Document location here
- Reference: IMPLEMENTATION_START_POINT.md "Create Archive Folder at Plan Start"

**Deferred Archiving**: SUBPLANs and EXECUTION_TASKs are archived at achievement completion or plan completion (not immediately upon individual file completion). See IMPLEMENTATION_END_POINT.md "Deferred Archiving" section.

---

## 📦 Final Archive Plan (When PLAN Complete)

**Final Archive Location**: `documentation/archive/<feature>-<date>/`

**Structure**:

```
planning/
  └── PLAN_<FEATURE>.md

subplans/
  └── SUBPLAN_<FEATURE>_*.md

execution/
  └── EXECUTION_TASK_<FEATURE>_*_*.md

summary/
  └── <FEATURE>-COMPLETE.md
```

**Permanent Docs** (keep in current locations):

- [FILL: List any documents that stay permanent]
- [FILL: Update locations if creating new permanent docs]

---

## ✅ Completion Criteria

**This PLAN is Complete When**:

1. ✅ All Priority 1 (Critical) achievements met
2. ✅ All Priority 2 (High) achievements met
3. ✅ Tests passing (if code work)
4. ✅ Code commented with learnings (if code work)
5. ✅ Documentation updated with learnings
6. ✅ IMPLEMENTATION_BACKLOG.md updated with future work
7. ✅ Process improvement analysis complete
8. ✅ All documents archived per IMPLEMENTATION_END_POINT.md

**Optional** (for comprehensive completion):

- ✅ Priority 3 (Medium) achievements met
- ✅ Priority 4 (Low) achievements met

[FILL: Customize based on your PLAN's requirements]

---

## 🚀 Ready to Execute

**Next Action**: Create first SUBPLAN for chosen achievement

**Remember**:

- Subplans are created on-demand (select achievement, create SUBPLAN)
- One SUBPLAN can have multiple EXECUTION_TASKs (different attempts)
- Update "Subplan Tracking" section as you create subplans
- Add achievements if gaps discovered

---

**Status**: Ready for execution  
**Start Work**: Create SUBPLAN for your chosen achievement
