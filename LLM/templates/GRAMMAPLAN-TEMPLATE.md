# GRAMMAPLAN: [Initiative Name]

**Status**: Planning / In Progress / Complete  
**Created**: [YYYY-MM-DD HH:MM UTC]  
**Strategic Goal**: [One sentence describing what this initiative achieves]  
**Priority**: Critical / High / Medium / Low  
**Total Estimated Effort**: [Sum of all child PLAN estimates] hours

[FILL: Use UTC timestamps. Example: 2025-11-07 14:30 UTC]

[FILL: Replace [Initiative Name] with short, descriptive name using kebab-case (e.g., CODE-QUALITY, GRAPHRAG-PIPELINE)]

---

## 📖 What is a GrammaPlan?

**For LLMs/Developers**: A GrammaPlan orchestrates multiple related PLANs working toward a unified strategic goal. This is a meta-document - the actual work happens in child PLANs.

**When to Use**: See `LLM/guides/GRAMMAPLAN-GUIDE.md`

**File Location**: Save this file in `work-space/grammaplans/GRAMMAPLAN_[NAME].md`

**Size**: 600-1,500 lines (strategic coordination needs space)

- **600-999 lines**: Typical GrammaPlan (coordinates 3-5 PLANs)
- **1,000-1,499 lines**: Large GrammaPlan (coordinates 6-8 PLANs) - **Warning**: Consider splitting or simplifying
- **1,500+ lines**: **Error** - Must split into multiple GrammaPlans or convert to NORTH_STAR

**Key Principle**: Focus on coordination and orchestration. Do NOT replicate child PLAN content here.

**Validation**: Use `LLM/scripts/validation/check_grammaplan_size.py` to validate size

---

## 🎯 Strategic Goal

[FILL: 2-3 paragraphs describing:

- What we're achieving at the highest level
- Why this matters strategically to the project/organization
- How child PLANs contribute to this goal]

**Example**:

> Transform code quality across the entire codebase by systematically reviewing all domains (GraphRAG, Ingestion, RAG, Chat, Core), extracting common patterns into reusable libraries, and applying clean code principles. This establishes a solid foundation for future development by reducing duplication by 30%, improving maintainability, and creating consistent code structure.

---

## 📋 Child PLANs

### Overview

This GrammaPlan coordinates [N] child PLANs organized by [domain/phase/component]:

| Child PLAN                           | Status   | Priority | Estimated Effort | Progress | Dependencies |
| ------------------------------------ | -------- | -------- | ---------------- | -------- | ------------ |
| PLAN\_[GRAMMAPLAN-NAME]-[CHILD-1].md | Planning | High     | Xh               | 0%       | None         |
| PLAN\_[GRAMMAPLAN-NAME]-[CHILD-2].md | Planning | High     | Yh               | 0%       | Child-1      |
| PLAN\_[GRAMMAPLAN-NAME]-[CHILD-3].md | Planning | Medium   | Zh               | 0%       | None         |

[FILL: List all child PLANs with key info. Update as children progress.]

---

### PLAN\_[GRAMMAPLAN-NAME]-[CHILD-1].md

**Status**: Planning / In Progress / Complete  
**Estimated Effort**: [Hours]  
**Progress**: [Percentage]% complete  
**Priority**: Critical / High / Medium / Low

**Purpose**: [One sentence - what this child delivers]

**Scope**: [Brief description of what this child covers]

**Dependencies**:

- [List other children this depends on, if any]
- [Or "None" if independent]

**Contributes To**: [Which strategic goal this child addresses]

**Related Sections**: [References to related work in other children]

[FILL: Repeat this section for each child PLAN. Keep each description to 5-10 lines max.]

---

### PLAN\_[GRAMMAPLAN-NAME]-[CHILD-2].md

**Status**: Planning / In Progress / Complete  
**Estimated Effort**: [Hours]  
**Progress**: [Percentage]% complete  
**Priority**: Critical / High / Medium / Low

**Purpose**: [One sentence]

**Scope**: [Brief description]

**Dependencies**:

- PLAN\_[GRAMMAPLAN-NAME]-[CHILD-1].md (must complete first)

**Contributes To**: [Strategic goal]

**Related Sections**: [Cross-references]

---

[FILL: Continue for all child PLANs - recommend 3-8 children total]

---

## 🔗 Dependencies Between Children

### Sequencing

[FILL: Document which children must complete before others can start]

**Sequential Dependencies**:

- CHILD-1 must complete → before CHILD-2 starts
- CHILD-3 must complete → before CHILD-4 starts

**Parallel Opportunities**:

- CHILD-1 and CHILD-3 can run simultaneously (independent domains)
- CHILD-5 and CHILD-6 can run simultaneously

**Critical Path**: [Identify longest dependency chain]

- CHILD-1 → CHILD-2 → CHILD-4 (estimated Xh total)

---

### Cross-PLAN Coordination

[FILL: Use MULTIPLE-PLANS-PROTOCOL.md format for child relationships]

**Between PLAN*[CHILD-1] and PLAN*[CHILD-2]**:

- **Type**: Hard / Soft / Data / Code / Sequential / Decision Context
- **Relationship**: [Description]
- **Dependency**: [What CHILD-2 needs from CHILD-1]
- **Status**: Blocked / Ready / Can proceed
- **Timing**: [When to work on this]

[FILL: Document all significant cross-child dependencies]

---

## 🔄 Cross-Cutting Concerns

[FILL: Optional but recommended - concerns spanning multiple children]

### Libraries / Infrastructure

[FILL: If some children provide libraries/infrastructure to others]

**PLAN\_[GRAMMAPLAN-NAME]-LIBRARIES**:

- Provides: [What it creates]
- Used By: [Which other children use it]
- Integration: [How others integrate]

### Shared Patterns

[FILL: Patterns that all or most children should follow]

- Pattern 1: [Description]
- Pattern 2: [Description]

### Integration Strategy

[FILL: How children combine at the end]

- Integration approach: [How to bring children together]
- Validation: [How to verify combined system]
- Testing: [Cross-child testing approach]

---

## ✅ Success Criteria

### Must Have (Required for Completion)

- [ ] All child PLANs complete (or specific subset listed below)
- [ ] Integration validated [if applicable]
- [ ] Strategic goal achieved
- [ ] [Other specific outcomes]

### Should Have

- [ ] [Important outcomes]

### Nice to Have

- [ ] [Bonus outcomes]

[FILL: Make criteria measurable. Typically "all children complete" is the main criterion.]

---

## 📊 Progress Tracking

### Overall Progress

**Formula**:

```
GrammaPlan Progress =
    (Child_1_Progress * Child_1_Effort +
     Child_2_Progress * Child_2_Effort +
     ... +
     Child_N_Progress * Child_N_Effort)
    /
    Total_Effort
```

**Current Progress**: [Calculate based on child progress]

**Example**:

```
CHILD-1: 100% * 30h = 30h
CHILD-2:  80% * 25h = 20h
CHILD-3:  50% * 20h = 10h
CHILD-4:   0% * 25h =  0h
                      ---
Total: 60h / 100h = 60% complete
```

---

### Child PLAN Status Summary

| Child   | Status      | Progress | Hours  | Next Milestone |
| ------- | ----------- | -------- | ------ | -------------- |
| CHILD-1 | ✅ Complete | 100%     | 30/30h | -              |
| CHILD-2 | 🔨 Active   | 80%      | 20/25h | Priority 3     |
| CHILD-3 | ⏸️ Paused   | 50%      | 10/20h | Priority 2     |
| CHILD-4 | ⏳ Pending  | 0%       | 0/25h  | Not started    |

**Recommended Next**: [Which child to work on next based on dependencies and priorities]

---

## 📝 Current Status & Handoff (For Pause/Resume)

**Last Updated**: [YYYY-MM-DD HH:MM UTC]  
**Status**: [Planning / In Progress / Complete]

**Completed Children**: [List children that are 100% done]

**In Progress Children**: [List children currently being worked on]

**Pending Children**: [List children not yet started]

**Next Steps**:

1. [What should be done next]
2. [Which child to focus on]
3. [Any blockers or coordination needs]

**When Resuming**:

1. Read this section for current state
2. Review child PLAN status (table above)
3. Check dependencies (are prerequisites complete?)
4. Follow IMPLEMENTATION_RESUME.md for chosen child PLAN

**Context Preserved**: This section + Child Status Summary + Dependency section = full context

---

## 🔗 Decomposition Pattern Used

[FILL: Which pattern from GRAMMAPLAN-GUIDE.md]

**Pattern**: Domain / Phase / Hybrid Decomposition

**Rationale**: [Why this pattern was chosen]

**Example**:

> This initiative uses Domain Decomposition because work naturally divides by technical domain (GraphRAG, Ingestion, RAG, Chat, Core). Each domain has clear boundaries, minimal coupling, and can progress independently after foundation work completes.

---

## ⚠️ Constraints

### Technical Constraints

- [FILL: Technical limitations that affect all or most children]
- [FILL: Shared technical requirements]

### Process Constraints

- [FILL: Process requirements (e.g., "Only one child 'In Progress' at a time")]
- [FILL: Coordination requirements]

### Resource Constraints

- [FILL: Resource limitations (e.g., "One developer, sequential execution")]
- [FILL: Time constraints]

---

## 📚 References & Context

### Related Documentation

- **GrammaPlan Guide**: `LLM/guides/GRAMMAPLAN-GUIDE.md`
- **Multiple Plans Protocol**: `LLM/guides/MULTIPLE-PLANS-PROTOCOL.md`
- **ACTIVE_PLANS Dashboard**: `ACTIVE_PLANS.md` (for tracking)

### Parent/Sibling GrammaPlans

[FILL: If this GrammaPlan relates to others]

- **Parent**: [If this is nested under another GrammaPlan]
- **Siblings**: [If there are related GrammaPlans]

### Methodology

- **Entry Point**: `IMPLEMENTATION_START_POINT.md`
- **Exit Point**: `IMPLEMENTATION_END_POINT.md`
- **Resume Protocol**: `IMPLEMENTATION_RESUME.md`

---

## ⏱️ Time Estimates

### Per Child

- **PLAN\_[CHILD-1]**: Xh
- **PLAN\_[CHILD-2]**: Yh
- **PLAN\_[CHILD-3]**: Zh
- [List all children]

**Total Estimated**: [Sum] hours

**Breakdown**:

- Critical priority children: [Sum]h
- High priority children: [Sum]h
- Medium/Low priority children: [Sum]h

### Sequencing Impact

**If Sequential**: [Total hours, no parallelism]  
**If Parallel** (ideal): [Shortest critical path]  
**Realistic** (some parallelism): [Estimate based on resources]

---

## 📦 Archiving Plan

**When This GrammaPlan Is Complete**:

Create archive: `documentation/archive/grammaplan-[name]-[date]/`

**Structure**:

```
documentation/archive/grammaplan-[name]-[date]/
├── INDEX.md (GrammaPlan archive navigation)
├── GRAMMAPLAN_[FEATURE].md (this orchestration doc)
├── planning/
│   ├── PLAN_[FEATURE]-[CHILD-1].md
│   ├── PLAN_[FEATURE]-[CHILD-2].md
│   └── ... (all child PLANs)
├── subplans/
│   ├── SUBPLAN_[FEATURE]-[CHILD-1]_01.md
│   └── ... (all SUBPLANs from all children)
├── execution/
│   ├── EXECUTION_TASK_[FEATURE]-[CHILD-1]_01_01.md
│   └── ... (all EXECUTION_TASKs from all children)
└── summary/
    └── GRAMMAPLAN-[FEATURE]-COMPLETE.md
```

**Note**: Archive GrammaPlan and ALL children together as one archive.

---

## ✅ Completion Criteria

**This GrammaPlan is Complete When**:

1. [ ] All required child PLANs complete (or explicitly deprioritized)
2. [ ] Integration validated (if applicable)
3. [ ] Strategic goal achieved
4. [ ] Success criteria met
5. [ ] All documentation archived

**Process**:

1. Mark last required child PLAN complete
2. Verify integration (cross-child validation)
3. Update GrammaPlan status to "Complete"
4. Follow IMPLEMENTATION_END_POINT for GrammaPlan
5. Archive GrammaPlan + all children together

---

## 🎯 Expected Outcomes

### Short-term (After First N Children)

- [FILL: Early outcomes]

### Medium-term (After Most Children)

- [FILL: Mid-point outcomes]

### Long-term (Upon Completion)

- [FILL: Final outcomes]
- Strategic goal achieved
- All children integrated
- [Measurable impact]

---

## 📋 Immediate Next Steps

1. **Review This GrammaPlan** - Confirm scope, children, dependencies
2. **Create First Child PLAN** - Start with foundation or highest priority
3. **Update ACTIVE_PLANS.md** - Add GrammaPlan and children
4. **Execute** - Follow IMPLEMENTATION_START_POINT for child PLAN
5. **Track Progress** - Update this GrammaPlan as children complete

---

**Status**: GRAMMAPLAN Created and Ready  
**Next**: Create first child PLAN following PLAN-TEMPLATE.md

---

## 📝 Notes

**Common Patterns**:

- Domain Decomposition: Split by technical domain (GraphRAG, Ingestion, RAG)
- Phase Decomposition: Split by sequential phases (Extract, Transform, Load)
- Hybrid Decomposition: Foundation → Domains → Integration

**Sizing Guidelines**:

- Each child PLAN: 30-60 hours ideal
- Total children: 3-8 recommended
- GrammaPlan doc: Keep under 300 lines

**Coordination**:

- Use Multiple Plans Protocol for child dependencies
- Update child status in this doc regularly
- Coordinate integration explicitly

**For Help**: See `LLM/guides/GRAMMAPLAN-GUIDE.md`
