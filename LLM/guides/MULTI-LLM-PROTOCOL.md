# Multi-LLM Communication Protocol

**Purpose**: Guide for collaboration when multiple LLM instances work on same project  
**Status**: Active Protocol  
**Created**: 2025-11-07  
**Version**: 1.0  
**Related**: IMPLEMENTATION_RESUME.md, ACTIVE_PLANS.md, MULTIPLE-PLANS-PROTOCOL.md

---

## 🎯 When This Applies

Use this protocol when:

- **Multiple developers** each using LLM assistants on same project
- **Same developer** using LLM across different sessions (hours/days/weeks apart)
- **Context switching** between achievements within same PLAN
- **Collaboration needed** on same achievement (rare but possible)

**Don't use for**:

- Single LLM continuous session (no handoff needed)
- Completed work (no ongoing coordination)

---

## 📋 Key Principle

**Existing Protocols Already Handle Most Cases!**

The structured LLM development methodology already handles multi-LLM scenarios through:

- ✅ **IMPLEMENTATION_RESUME.md**: Full protocol for resuming paused work
- ✅ **ACTIVE_PLANS.md**: "ONE In Progress" rule prevents conflicts
- ✅ **PLAN "Current Status & Handoff"**: Natural handoff point
- ✅ **Git commits**: Enable conflict resolution and history tracking

**This protocol adds**: Explicit multi-LLM framing + handoff formats for edge cases

---

## 🔄 Common Scenarios

### Scenario 1: Resume After Break (Most Common)

**Situation**: LLM_A paused work, LLM_B resuming hours/days/weeks later

**Solution**: ✅ Already handled by IMPLEMENTATION_RESUME.md

**Process**:
1. LLM_B follows RESUME protocol (5-step checklist)
2. Reads PLAN "Current Status & Handoff"
3. Reviews last EXECUTION_TASK
4. Updates ACTIVE_PLANS.md to "In Progress"
5. Continues work

**Handoff Mechanism**: PLAN "Current Status & Handoff" section

**No Special Action Needed** - Standard RESUME workflow works!

---

### Scenario 2: Mid-Achievement Handoff (Less Common)

**Situation**: LLM_A created SUBPLAN, started EXECUTION_TASK (in progress), LLM_B continuing

**Solution**: Add handoff notes to EXECUTION_TASK

**Process**:

1. **LLM_A** (before stopping):
   ```markdown
   Add to EXECUTION_TASK:
   
   ## 🔄 Handoff Notes (LLM_A → LLM_B)
   
   **Date**: 2025-11-07  
   **Context**: Pausing mid-iteration, handing to LLM_B
   
   **What's Done**:
   - Steps 1-3 of Phase 2 complete
   - Files changed: [list]
   
   **What's Blocked**:
   - Waiting for dependency X
   - Issue Y needs investigation
   
   **What's Next**:
   - Continue Phase 2, step 4
   - OR: Pivot to approach B (see notes below)
   
   **Important Context**:
   - Assumption: X is true (verify!)
   - Tried Y, failed because Z
   ```

2. **LLM_B** (when resuming):
   - Read handoff notes
   - Verify assumptions
   - Continue EXECUTION_TASK (same iteration OR new strategy = new EXECUTION_TASK)

**When to Use**:
- Rare (usually pause at achievement boundaries)
- Useful for complex, multi-day achievements
- Enables smooth mid-work transitions

---

### Scenario 3: Parallel Achievements (Rare)

**Situation**: LLM_A working on Achievement 1.1, LLM_B working on Achievement 1.2 (same PLAN, different achievements)

**Solution**: Coordinate in PLAN, use separate SUBPLANs

**Process**:

1. **Check Conflicts**:
   ```markdown
   Do achievements touch same code?
   ├─ Yes: Coordinate (sequential work OR careful merge)
   └─ No: Can work in parallel
   ```

2. **Document in PLAN**:
   ```markdown
   ## Current Work (Multiple LLMs)
   
   - Achievement 1.1: LLM_A (started 2025-11-07)
     - SUBPLAN_XX created
     - Files: business/agents/*.py
   
   - Achievement 1.2: LLM_B (started 2025-11-07)
     - SUBPLAN_YY created
     - Files: business/stages/*.py
   ```

3. **Coordination**:
   - Git commits frequently
   - Pull before starting each session
   - Resolve merge conflicts if code overlaps
   - Update PLAN with both LLMs' progress

**When to Use**:
- Large PLANs with independent achievements
- Team wants parallel velocity
- Achievements don't overlap in code

**Risks**:
- Merge conflicts if code overlap
- Integration challenges if assumptions differ
- Recommend: Avoid unless necessary

---

## 📝 Handoff Formats

### Three-Tier Handoff System

**Tier 1: Inline Handoff** (for small updates)

**When**: Minor progress update, achievement boundary, clean pause

**Where**: Update PLAN "Current Status & Handoff" section directly

**Format**:
```markdown
**Last Updated**: 2025-11-07 15:30 UTC (LLM_A → LLM_B)

**What's Done**:
- Achievement 1.1 complete
- Achievement 1.2 in progress (SUBPLAN created)

**What's Next**:
- Complete Achievement 1.2 (continue EXECUTION_TASK_XX_02_01)

**Handoff Note**: Tests are failing on step 3, need to debug database connection
```

**Tier 2: EXECUTION_TASK Handoff** (for mid-work transitions)

**When**: Pausing mid-achievement, complex work in progress

**Where**: Add "Handoff Notes" section to current EXECUTION_TASK

**Format**: (See Scenario 2 above)

**Tier 3: EXECUTION_ANALYSIS Handoff** (for major transitions)

**When**: Large context needed, major changes, requires analysis

**Where**: Create EXECUTION_ANALYSIS_HANDOFF_[PLAN-NAME].md

**Format**:
```markdown
# EXECUTION_ANALYSIS: Handoff - [PLAN_NAME]

**From**: LLM_A / [Developer Name]  
**To**: LLM_B / [Developer Name]  
**Date**: 2025-11-07  
**Reason**: [Why handing off]  
**Related**: PLAN_[FEATURE].md

---

## Context Summary

**PLAN Status**:
- Progress: X/Y achievements
- Current: Achievement Z.W in progress
- Next: Achievement Z.X

**Recent Work** (last 5-10 hours):
- [Summary of recent achievements]
- [Key decisions made]
- [Blockers encountered]

**Code Changes**:
- Files modified: [list with brief description]
- New files: [list]
- Deleted files: [list]
- Tests: [status]

---

## Active Work Detail

**Current SUBPLAN**: SUBPLAN_XX  
**Current EXECUTION**: EXECUTION_TASK_XX_YY (Iteration N)

**Progress**:
- Phase 1: Complete ✅
- Phase 2: In progress (steps 1-3 done, 4-6 remaining)
- Phase 3: Not started

**Blockers**:
1. [Blocker description]
2. [Investigation needed]

---

## Important Context

**Assumptions Made**:
1. [Assumption 1] - Verified: [Yes/No]
2. [Assumption 2] - Needs verification

**Decisions Made**:
1. [Decision 1] - Rationale: [Why]
2. [Decision 2] - Alternatives considered: [What]

**Things That Didn't Work**:
1. [Approach X failed because Y]
2. [Tried Z, discovered W]

---

## Next Steps for Receiving LLM

1. [First action]
2. [Second action]
3. [Verify assumption X before proceeding]

**Recommended Strategy**: [Continue current OR pivot to alternative]

---

**Handoff Complete** - Safe to proceed
```

---

## 🤝 Coordination Patterns

### Pattern 1: Claim Before Start

**Process**:
1. Before starting achievement: Update PLAN "Current Status & Handoff"
2. Document: "LLM_X starting Achievement Y.Z on [date]"
3. Update ACTIVE_PLANS.md (mark "In Progress")
4. Commit: `git commit -m "Starting Achievement Y.Z"`

**Prevents**: Two LLMs starting same work

---

### Pattern 2: Frequent Commits

**Process**:
1. Commit after each logical checkpoint (every 3-5 files, after each test passing)
2. Clear commit messages: "Achievement X.Y: Step completed"
3. Push regularly (if shared repository)

**Prevents**: Large merge conflicts, work loss

---

### Pattern 3: Pull Before Resume

**Process**:
1. Before resuming work: `git pull`
2. Review commits since last session
3. Check for conflicts with your planned work
4. Adjust strategy if conflicts exist

**Prevents**: Duplicate work, conflicts

---

## 🚨 Conflict Resolution

### Code Conflicts

**If both LLMs edited same file**:

1. **Git merge conflict**:
   - Review both changes
   - Keep better implementation OR combine if complementary
   - Test after merge
   - Document resolution in EXECUTION_TASK

2. **Divergent approaches**:
   - Compare approaches in EXECUTION_ANALYSIS
   - Choose based on: quality, test coverage, simplicity
   - Document decision rationale

---

### Achievement Conflicts

**If both LLMs worked on same achievement**:

1. **Check ACTIVE_PLANS.md**: Who marked PLAN "In Progress" first?
2. **Priority**: First LLM has priority
3. **Second LLM**: Either:
   - Wait for first to complete
   - Switch to different achievement
   - Collaborate (only if achievements truly independent)

---

### Document Conflicts

**If both LLMs created same document**:

1. **Check timestamps**: Who created first?
2. **Compare quality**: Which is more complete?
3. **Merge or choose**: Combine best parts OR keep better one
4. **Document**: Note in EXECUTION_TASK which was kept and why

---

## 📚 Best Practices

### Best Practice 1: Update PLAN Frequently

**Why**: PLAN "Current Status & Handoff" is primary communication mechanism

**How**:
- After each achievement completion
- When pausing work
- When making significant decisions
- Before long breaks

---

### Best Practice 2: Use Git Effectively

**Why**: Git provides natural multi-LLM coordination

**How**:
- Commit often (every checkpoint)
- Clear commit messages (reference achievements)
- Pull before starting sessions
- Push after completing work units

---

### Best Practice 3: Leverage Existing Protocols

**Why**: Don't create new handoff mechanisms, use existing PLAN sections

**How**:
- Small handoffs: PLAN "Current Status"
- Medium: EXECUTION_TASK notes
- Large: EXECUTION_ANALYSIS (rare)

---

### Best Practice 4: ONE In Progress Rule

**Why**: Prevents most multi-LLM conflicts

**How**:
- Enforced by ACTIVE_PLANS.md
- Only ONE PLAN marked "In Progress"
- Others must be "Paused" or "Ready"
- Checked in RESUME Step 5

---

## 🔗 Integration with Existing Protocols

### IMPLEMENTATION_RESUME.md

**Already handles**: Multi-LLM resume scenario  
**Integration**: Reference this protocol in RESUME for explicit multi-LLM cases

### ACTIVE_PLANS.md

**Already handles**: "ONE In Progress" rule  
**Integration**: Core conflict prevention mechanism

### MULTIPLE-PLANS-PROTOCOL.md

**Related**: This protocol is about multiple LLMs, that's about multiple PLANs  
**Integration**: Complementary - can have multiple LLMs AND multiple PLANs

---

## 🎯 Quick Reference

**Scenario**: [Your situation]

| Scenario | Handoff Format | Coordination | Reference |
|----------|----------------|--------------|-----------|
| Resume after break | PLAN "Current Status" | IMPLEMENTATION_RESUME | Scenario 1 |
| Mid-achievement pause | EXECUTION_TASK notes | Update + commit | Scenario 2 |
| Parallel achievements | PLAN coordination | Separate SUBPLANs | Scenario 3 |
| Major transition | EXECUTION_ANALYSIS | Full handoff doc | Tier 3 format |

---

**Status**: Active Protocol  
**Version**: 1.0 (November 2025)  
**Maintained By**: Meta-PLAN (PLAN_STRUCTURED-LLM-DEVELOPMENT.md)

