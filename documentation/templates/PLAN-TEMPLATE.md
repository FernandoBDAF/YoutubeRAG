# PLAN: [Feature Name]

**Status**: Planning / In Progress / Complete  
**Created**: [YYYY-MM-DD HH:MM UTC]  
**Goal**: [One sentence describing what this plan achieves]  
**Priority**: Critical / High / Medium / Low

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

**Self-Contained**: This PLAN contains everything you need to execute it.

[FILL: Make this section specific to your plan. Provide enough context that an LLM can understand and execute without external information.]

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

## 🎯 Desirable Achievements (Priority Order)

[FILL: List WHAT needs to be achieved, not HOW to achieve it. Subplans (HOW) are created on-demand.]

### Priority 1: CRITICAL

**Achievement 1.1**: [Title]

- [What needs to exist]
- [Why it's valuable]
- Success: [How we know it's done]
- Effort: [Hours estimate]

**Sub-Achievements** (may be discovered during execution):

- 1.1.1: [If main achievement has logical sub-parts]
- (More may be added as gaps discovered)

**Achievement 1.2**: [Title]

- [Description]
- Success: [Criteria]
- Effort: [Estimate]

### Priority 2: HIGH

**Achievement 2.1**: [Title]

- [Description]

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

## 🔄 Subplan Tracking (Updated During Execution)

**Subplans Created for This PLAN**:

_None yet - will be added as subplans are created_

**Format**:

```
- SUBPLAN_XX: [Achievement addressed] - [Brief description] - Status: [Not Started/In Progress/Complete]
  └─ EXECUTION_TASK_XX_YY: [Brief description] - Status: [In Progress/Complete/Abandoned]
```

**Example**:

```
- SUBPLAN_01: Achievement 1.1 - Status: Complete ✅
  └─ EXECUTION_TASK_01_01: First attempt - Status: Complete ✅
  └─ EXECUTION_TASK_01_02: Second attempt (circular debug recovery) - Status: Complete ✅
```

[FILL: Update this section as subplans are created. Shows progress at a glance.]

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

## 📦 Archive Plan (When Complete)

**Archive Location**: `documentation/archive/<feature>-<date>/`

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
