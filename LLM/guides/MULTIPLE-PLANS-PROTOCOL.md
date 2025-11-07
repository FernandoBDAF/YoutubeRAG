# Multiple PLANS Protocol

**Purpose**: Guide for managing multiple active/paused PLANs simultaneously (including GrammaPlan orchestration)  
**Status**: Permanent Reference  
**Last Updated**: 2025-11-07 (GrammaPlan support added)  
**Related**: IMPLEMENTATION_START_POINT.md, IMPLEMENTATION_RESUME.md, ACTIVE_PLANS.md, GRAMMAPLAN-GUIDE.md

---

## 🎯 When This Applies

Use this protocol when:

- **2+ PLANs active/paused simultaneously** (shown in ACTIVE_PLANS.md)
- **Context switching** between different features
- **Dependencies exist** between PLANs (code, data, decisions, or sequencing)
- **Overlapping concerns** (same code area, different aspects)
- **Collaborative work** (different people on different PLANs)
- **Code evolution** where implementation decisions in one PLAN affect another
- **Integration needs** where understanding WHY decisions were made provides context

**Don't use this for**:

- Single PLAN work (follow standard methodology)
- Starting new work (use IMPLEMENTATION_START_POINT.md)
- Completing work (use IMPLEMENTATION_END_POINT.md)

---

## 📋 Dependency Types

**Key Insight**: Dependencies are not just about "active/paused" status. They're about:

- **Code Evolution**: Implementations in PLAN_A change assumptions for PLAN_B
- **Decision Context**: Understanding WHY decisions were made in PLAN_A helps integrate PLAN_B
- **Planned Impact**: Planned implementations in PLAN_A may impact PLAN_B even before execution
- **Integration Knowledge**: Reading PLAN_A's SUBPLANs and EXECUTION_TASKs provides critical context for PLAN_B

**Therefore**: PLANs are **valuable context sources** for each other, not just blockers or prerequisites.

---

### Hard Dependency

**Definition**: PLAN_A **cannot proceed** without PLAN_B completion.

**Characteristics**:

- Blocks progress on dependent PLAN
- Must wait for dependency to complete
- Clear prerequisite relationship

**Example**:

```
PLAN_GRAPH-CONSTRUCTION-REFACTOR.md depends on PLAN_ENTITY-RESOLUTION-REFACTOR.md
- Graph construction needs stable entity_ids (Achievement 0.3)
- Cannot build relationships without resolved entities
- Must wait for entity resolution Priorities 0-3 complete
```

**Tracking Format**:

```markdown
**PLAN_DEPENDENCY_NAME.md**:

- **Type**: Hard dependency
- **Blocks**: Achievement X.Y (specific achievement blocked)
- **Requires**: Achievement A.B from dependency (what must be complete)
- **Status**: Blocked / Ready (when dependency complete)
```

### Soft Dependency

**Definition**: PLAN_A **benefits from** PLAN_B but can proceed independently.

**Characteristics**:

- Can work in parallel
- Quality/performance improves with dependency
- Not blocking, but recommended

**Example**:

```
PLAN_COMMUNITY-DETECTION-REFACTOR.md benefits from PLAN_GRAPH-CONSTRUCTION-REFACTOR.md
- Community detection can work with current graph
- Better graph quality → better communities
- Can start in parallel, but validates together
```

**Tracking Format**:

```markdown
**PLAN_DEPENDENCY_NAME.md**:

- **Type**: Soft dependency
- **Benefits**: Achievement X.Y (what improves)
- **Requires**: Achievement A.B from dependency (recommended)
- **Status**: Can proceed / Recommended to wait
```

### Data Dependency

**Definition**: PLAN_A uses **data produced** by PLAN_B.

**Characteristics**:

- Output of PLAN_B feeds into PLAN_A
- May need data export/import
- Analysis PLANs often have this

**Example**:

```
PLAN_ENTITY-RESOLUTION-ANALYSIS.md uses data from PLAN_ENTITY-RESOLUTION-REFACTOR.md
- Analysis needs production data from refactor
- Uses MongoDB collections created by refactor
- Can run after refactor completes
```

**Tracking Format**:

```markdown
**PLAN_DEPENDENCY_NAME.md**:

- **Type**: Data dependency
- **Uses**: [Data type/collection] from dependency
- **Requires**: Achievement A.B from dependency (data producer)
- **Status**: Waiting for data / Ready
```

### Code Dependency

**Definition**: PLAN_A and PLAN_B **modify the same code**.

**Characteristics**:

- Both touch same files/functions
- Risk of merge conflicts
- Need coordination

**Example**:

```
PLAN_ENTITY-RESOLUTION-REFACTOR.md and PLAN_GRAPH-CONSTRUCTION-REFACTOR.md
- Both modify business/stages/graphrag/*.py
- Entity resolution creates entities, graph construction uses them
- Sequential work recommended (entity resolution first)
```

**Tracking Format**:

```markdown
**PLAN_DEPENDENCY_NAME.md**:

- **Type**: Code dependency
- **Overlaps**: [Files/functions] modified by both
- **Risk**: Merge conflicts / Coordination needed
- **Strategy**: Sequential / Parallel with coordination
```

### Sequential Dependency

**Definition**: PLAN_A → PLAN_B → PLAN_C (pipeline).

**Characteristics**:

- Natural pipeline order
- Each feeds into next
- Complete in order

**Example**:

```
PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md → PLAN_ENTITY-RESOLUTION-REFACTOR.md → PLAN_GRAPH-CONSTRUCTION-REFACTOR.md
- Extraction produces entities
- Entity resolution canonicalizes entities
- Graph construction builds relationships
- Natural pipeline: extraction → resolution → construction
```

**Tracking Format**:

```markdown
**Pipeline Order**: PLAN_A → PLAN_B → PLAN_C

- **Stage 1**: PLAN_A (must complete first)
- **Stage 2**: PLAN_B (depends on PLAN_A)
- **Stage 3**: PLAN_C (depends on PLAN_B)
```

---

## 🔄 Context Switching Workflow

### Before Pausing Current PLAN

1. **Commit all changes**:

   ```bash
   git add -A
   git commit -m "Pausing PLAN_X at Achievement Y.Z"
   ```

2. **Update PLAN**:

   - Update "Current Status & Handoff" section
   - Note where you stopped
   - Note what should be done next
   - Document any blockers

3. **Update ACTIVE_PLANS.md**:

   - Mark current PLAN as "⏸️ Paused"
   - Update "Last Updated" timestamp
   - Note reason for pause (if relevant)

4. **Check dependencies**:
   - Are other PLANs waiting on this?
   - Update dependent PLANs if needed

### Before Resuming Other PLAN

1. **Follow IMPLEMENTATION_RESUME.md**:

   - Complete Pre-Resume Checklist
   - Read PLAN "Current Status & Handoff"
   - Check "Subplan Tracking"
   - Review "Achievement Addition Log"

2. **Check dependencies**:

   - Are all prerequisites complete?
   - Is this PLAN blocked by another?
   - Can this PLAN proceed?

3. **Update ACTIVE_PLANS.md**:

   - Mark this PLAN as "🚀 In Progress"
   - Update "Last Updated" timestamp

4. **Verify context**:
   - Understand where you left off
   - Know what to work on next
   - Have all required context

### Active PLAN Management

**Rule**: Only **ONE PLAN** should be "🚀 In Progress" at a time.

**Rationale**:

- Prevents context confusion
- Ensures focused work
- Reduces merge conflicts
- Clear progress tracking

**Exception**: Parallel work on independent PLANs (no dependencies, no code overlap) can both be "In Progress" if explicitly coordinated.

---

## 🔍 Dependency Detection

### When Creating a New PLAN

**Before starting work**:

1. **Check ACTIVE_PLANS.md**:

   - Are there related PLANs?
   - Do any PLANs touch same code?
   - Are there existing dependencies?

2. **Review existing PLANs**:

   - Read "Related Plans" sections
   - Check "Constraints" sections
   - Look for dependency mentions

3. **Document dependencies**:
   - Add "Related Plans" section to new PLAN
   - Document dependency type
   - Note blocking/beneficial relationships

### When Resuming a PLAN

**Before resuming**:

1. **Check dependencies**:

   - Read PLAN "Related Plans" section
   - Verify prerequisites are complete
   - Check if blocked by another PLAN

2. **Check for conflicts**:

   - Are other PLANs modifying same code?
   - Is coordination needed?
   - Should work be sequential?

3. **Update if needed**:
   - If dependency status changed, update PLAN
   - If unblocked, note in "Current Status"

---

## 🎯 Decision Trees

### Should I Start PLAN_B While PLAN_A is Active?

```
Is PLAN_B blocked by PLAN_A?
├─ Yes (Hard dependency)
│   └─ Wait for PLAN_A to complete required achievement
│
└─ No
    ├─ Does PLAN_B modify same code as PLAN_A?
    │   ├─ Yes
    │   │   ├─ Can work be sequential? → Wait for PLAN_A
    │   │   └─ Must be parallel? → Coordinate, mark both "In Progress"
    │   │
    │   └─ No
    │       └─ Can proceed in parallel (independent)
    │
    └─ Does PLAN_B benefit from PLAN_A?
        ├─ Yes (Soft dependency)
        │   └─ Can proceed, but quality improves if wait
        │
        └─ No
            └─ Fully independent, can proceed
```

### Which PLAN Should I Work On?

```
Are there hard dependencies?
├─ Yes
│   └─ Work on prerequisite PLAN first
│
└─ No
    ├─ Are there critical bugs?
    │   └─ Work on critical PLAN first
    │
    ├─ Are there soft dependencies?
    │   └─ Consider working on dependency first (better quality)
    │
    └─ All independent?
        └─ Work on highest priority PLAN
```

### How Do I Handle Code Conflicts?

```
Do PLANs modify same files?
├─ Yes
    ├─ Can work be sequential?
    │   ├─ Yes → Complete PLAN_A first, then PLAN_B
    │   └─ No → Coordinate:
    │       ├─ Split work (different functions)
    │       ├─ Communicate changes
    │       └─ Test integration frequently
    │
    └─ No
        └─ No conflict, proceed independently
```

---

## 📝 Documenting Dependencies in PLANs

### PLAN Template Section

Add to PLAN "References & Context" section:

```markdown
### Related Plans

**PLAN_DEPENDENCY_NAME.md**:

- **Type**: [Hard / Soft / Data / Code / Sequential]
- **Relationship**: [Description]
- **Dependency**: [What this PLAN needs from dependency]
- **Status**: [Blocked / Ready / Can proceed]
- **Timing**: [When to work on this relative to dependency]
```

### Example from Real PLAN

From `PLAN_GRAPH-CONSTRUCTION-REFACTOR.md`:

```markdown
**PLAN_ENTITY-RESOLUTION-REFACTOR.md**:

- **Type**: Hard dependency
- **Relationship**: Sequential (entity resolution → graph construction)
- **Dependency**: Graph construction depends on stable entity_ids
- **Status**: Ready (Priorities 0-3 and 3.5 complete)
- **Timing**: After entity resolution (Priorities 0-3 and 3.5 complete)
```

---

## 🔄 Coordination Strategies

### Sequential Work

**When to use**:

- Hard dependencies exist
- Code conflicts would occur
- Natural pipeline order

**Process**:

1. Complete PLAN_A fully
2. Archive PLAN_A
3. Start PLAN_B (dependency satisfied)
4. Reference PLAN_A in PLAN_B "Related Plans"

### Parallel Work (Independent)

**When to use**:

- No dependencies
- No code overlap
- Different code areas

**Process**:

1. Both PLANs can be "In Progress"
2. Work on one at a time (context switching)
3. Update ACTIVE_PLANS when switching
4. No coordination needed

### Parallel Work (Coordinated)

**When to use**:

- Soft dependencies
- Code overlap but different functions
- Can work together

**Process**:

1. Communicate changes frequently
2. Split work clearly (different functions/files)
3. Test integration regularly
4. Document coordination in PLANs

---

## 📊 ACTIVE_PLANS.md Integration

### Dependency Visualization

**Current Format** (enhanced):

```markdown
| Plan   | Status         | Priority | Completion | Dependencies  | Next Achievement |
| ------ | -------------- | -------- | ---------- | ------------- | ---------------- |
| PLAN_A | ⏸️ Paused      | HIGH     | 60%        | None          | Achievement 3.1  |
| PLAN_B | 🚀 In Progress | HIGH     | 45%        | PLAN_A (hard) | Achievement 2.2  |
```

**Dependency Column**:

- `None` - No dependencies
- `PLAN_A (hard)` - Hard dependency on PLAN_A
- `PLAN_A (soft)` - Soft dependency on PLAN_A
- `PLAN_A → PLAN_B` - Sequential pipeline

### Intersection Detection

**Add section to ACTIVE_PLANS.md**:

```markdown
## 🔗 Plan Intersections

**Code Overlaps**:

- PLAN_A + PLAN_B: `business/stages/graphrag/*.py` (coordinate)

**Data Dependencies**:

- PLAN_C uses data from PLAN_A (wait for PLAN_A)

**Sequential Pipelines**:

- PLAN_A → PLAN_B → PLAN_C (complete in order)
```

---

## ✅ Best Practices

### 1. Document Early

- Add "Related Plans" section when creating PLAN
- Update as dependencies discovered
- Keep ACTIVE_PLANS.md current

### 2. Check Before Starting

- Always check ACTIVE_PLANS.md before new PLAN
- Review existing PLANs for conflicts
- Document dependencies immediately

### 3. Update When Status Changes

- When dependency completes, update dependent PLANs
- When pausing, note blockers
- When resuming, verify prerequisites

### 4. Communicate Conflicts

- If code conflicts detected, document in both PLANs
- Coordinate work clearly
- Test integration frequently

### 5. Prioritize Correctly

- Hard dependencies first
- Critical bugs first
- Then soft dependencies
- Finally independent work

---

## 🎯 Real-World Examples

### Example 1: Sequential Pipeline

**Scenario**: Extraction → Entity Resolution → Graph Construction

**PLANs**:

- `PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md` (Priority 0-1 complete)
- `PLAN_ENTITY-RESOLUTION-REFACTOR.md` (Priorities 0-3 and 3.5 complete)
- `PLAN_GRAPH-CONSTRUCTION-REFACTOR.md` (Priorities 0-3 complete)

**Dependencies**:

- Graph construction **hard depends** on entity resolution (stable IDs)
- Entity resolution **soft depends** on extraction (better extraction → better resolution)

**Strategy**: Complete in order, but can start graph construction after entity resolution foundation (Priorities 0-3)

### Example 2: Soft Dependency

**Scenario**: Community Detection benefits from Graph Construction

**PLANs**:

- `PLAN_GRAPH-CONSTRUCTION-REFACTOR.md` (Priorities 0-3 complete)
- `PLAN_COMMUNITY-DETECTION-REFACTOR.md` (Ready to start)

**Dependencies**:

- Community detection **soft depends** on graph construction (better graph → better communities)

**Strategy**: Can start community detection now, but quality improves if wait for graph construction Priority 4-5

### Example 3: Meta Dependency

**Scenario**: All PLANs use methodology

**PLANs**:

- `PLAN_STRUCTURED-LLM-DEVELOPMENT.md` (foundation complete)
- All other PLANs

**Dependencies**:

- All PLANs **meta depend** on methodology (use START_POINT, END_POINT, RESUME)

**Strategy**: Methodology foundation complete, all PLANs can use it

### Example 4: Decision Context Dependency

**Scenario**: Community detection needs to understand graph construction decisions

**PLANs**:

- `PLAN_GRAPH-CONSTRUCTION-REFACTOR.md` (Priorities 0-3 complete)
- `PLAN_COMMUNITY-DETECTION-REFACTOR.md` (Ready to start)

**Decision Context Needed**:

- Why density formula counts unique pairs (affects community algorithms)
- Why source_count is conditional (affects edge weighting)
- Why bidirectional relationships use ontology (affects community boundaries)
- Edge cases discovered and solutions (from EXECUTION_TASKs)

**Strategy**: Read PLAN_GRAPH-CONSTRUCTION-REFACTOR.md SUBPLANs and EXECUTION_TASKs for integration context. Archive also contains valuable insights.

**Value**: Understanding implementation decisions prevents conflicts, improves integration quality, and avoids re-solving already-solved problems.

---

## 🎯 Complex Multi-PLAN Scenarios

### Scenario: 4+ Paused PLANs + Feature PLAN

**Example Situation**:

```
You have:
- PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md (Paused at Priority 2)
- PLAN_ENTITY-RESOLUTION-REFACTOR.md (Paused at Priority 4)
- PLAN_GRAPH-CONSTRUCTION-REFACTOR.md (Paused at Priority 4)
- PLAN_COMMUNITY-DETECTION-REFACTOR.md (Paused at Priority 3)

And you want to:
- PLAN_KNOWLEDGE-GRAPH-FEATURE.md (New - depends on ALL of the above)
```

**Decision Tree**:

```
Do all 4 PLANs need to complete fully?
├─ Yes
│   ├─ Option 1: Grand-Mother Plan (Orchestration)
│   │   └─ Create PLAN_GRAPHRAG-PIPELINE-REFACTOR.md
│   │       - Achievement 1: Complete extraction (resume PLAN_EXTRACTION)
│   │       - Achievement 2: Complete entity resolution (resume PLAN_ENTITY-RESOLUTION)
│   │       - Achievement 3: Complete graph construction (resume PLAN_GRAPH-CONSTRUCTION)
│   │       - Achievement 4: Complete community detection (resume PLAN_COMMUNITY-DETECTION)
│   │       - Achievement 5: Integrate into feature (PLAN_KNOWLEDGE-GRAPH-FEATURE)
│   │
│   └─ Option 2: Sequential Completion
│       └─ Complete each PLAN in pipeline order, then start feature PLAN
│
└─ No (Only certain achievements needed)
    ├─ Option 3: Cherry-Pick Achievements
    │   └─ Identify minimum achievements needed from each PLAN
    │       - PLAN_A: Achievement 2.1 only
    │       - PLAN_B: Priorities 4-5 only
    │       - Resume PLANs for those specific achievements
    │       - Then start feature PLAN
    │
    └─ Option 4: Foundation is Sufficient
        └─ Current state of all 4 PLANs is good enough
            - Start feature PLAN now
            - Note soft dependencies
            - Improve PLANs later if needed
```

### Option 1: Grand-Mother PLAN (Orchestration)

**When to use**:

- 4+ PLANs need orchestrated completion
- Complex dependencies between PLANs
- Feature depends on complete pipeline
- Want systematic, organized approach

**How it works**:

```markdown
# PLAN: GraphRAG Pipeline Refactor (Grand-Mother Plan)

**Type**: Orchestration PLAN  
**Orchestrates**: 4 child PLANs  
**Goal**: Complete GraphRAG pipeline refactor to enable feature X

## Achievements

**Achievement 1**: Complete Extraction Quality Enhancement

- Resume PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md
- Complete Priorities 2-6
- Deliverable: High-quality extraction

**Achievement 2**: Complete Entity Resolution Refactor

- Resume PLAN_ENTITY-RESOLUTION-REFACTOR.md
- Complete Priorities 4-7
- Deliverable: Accurate entity resolution

**Achievement 3**: Complete Graph Construction Refactor

- Resume PLAN_GRAPH-CONSTRUCTION-REFACTOR.md
- Complete Priorities 4-5 + Achievement 2.1
- Deliverable: Scalable graph construction

**Achievement 4**: Complete Community Detection Refactor

- Resume PLAN_COMMUNITY-DETECTION-REFACTOR.md
- Complete all priorities
- Deliverable: High-quality communities

**Achievement 5**: Integrate into Knowledge Graph Feature

- Create feature implementation
- Use outputs from Achievements 1-4
- Deliverable: Feature X complete

## Related Plans

- Child PLANs: PLAN_EXTRACTION-QUALITY-ENHANCEMENT, etc. (orchestrated)
- Dependent PLAN: PLAN_KNOWLEDGE-GRAPH-FEATURE (uses output)
```

**Advantages**:

- Clear orchestration and sequencing
- Single PLAN to track overall progress
- Child PLANs can still be worked on independently
- Feature PLAN comes after grand-mother

**Disadvantages**:

- Extra layer of planning
- May be overkill for simple cases

### Option 2: Sequential Completion

**When to use**:

- Natural pipeline order
- Each PLAN feeds into next
- No parallel work possible

**How it works**:

1. Complete PLAN_A fully (all priorities)
2. Archive PLAN_A
3. Complete PLAN_B fully
4. Archive PLAN_B
5. Continue through PLAN_C, PLAN_D
6. Start feature PLAN with all foundations complete

**Advantages**:

- Simple and systematic
- No coordination complexity
- Each PLAN gets full attention

**Disadvantages**:

- Longer time to feature
- May complete work not needed for feature

### Option 3: Cherry-Pick Achievements

**When to use**:

- Only certain achievements needed for feature
- Want to minimize work
- Can identify minimum viable foundation

**How it works**:

1. Analyze feature requirements
2. Identify minimum achievements from each PLAN:
   - PLAN_A: Achievements 1.1, 2.3 only
   - PLAN_B: Priority 4 only
   - PLAN_C: Already sufficient (paused state OK)
   - PLAN_D: Achievement 0.1 only
3. Resume each PLAN for specific achievements
4. Start feature PLAN when minimums complete

**Advantages**:

- Fastest path to feature
- Only necessary work
- Can complete PLANs later

**Disadvantages**:

- Requires careful dependency analysis
- May need to revisit PLANs later
- Risk of missing necessary work

### Option 4: Foundation is Sufficient

**When to use**:

- Current paused state is good enough
- Feature can work with foundation
- Can improve PLANs later if needed

**How it works**:

1. Review each paused PLAN:
   - PLAN_A: Priority 0-1 complete → Foundation OK
   - PLAN_B: Priority 0-3 complete → Foundation OK
   - etc.
2. Start feature PLAN now
3. Note soft dependencies in feature PLAN
4. Resume underlying PLANs later if issues found

**Advantages**:

- Fastest time to feature
- Test assumptions early
- Iterate based on real needs

**Disadvantages**:

- May need to revisit PLANs
- Quality may be lower initially
- Risk of rework

### Recommendation: Decision Matrix

| Scenario                            | Recommended Option      | Rationale                      |
| ----------------------------------- | ----------------------- | ------------------------------ |
| All PLANs must be 100% complete     | Option 1 or 2           | Systematic completion          |
| Feature needs specific achievements | Option 3                | Minimum viable approach        |
| Foundations are sufficient          | Option 4                | Fast iteration, validate early |
| Complex orchestration needed        | Option 1 (Grand-Mother) | Clear sequencing               |

---

## 📚 Integration Points

### IMPLEMENTATION_START_POINT.md

**Add section**: "Working with Multiple PLANs"

```markdown
## 🔄 Working with Multiple PLANs

Before creating a new PLAN:

1. Check ACTIVE_PLANS.md for related PLANs
2. Review existing PLANs for dependencies
3. Document dependencies in new PLAN
4. See MULTIPLE-PLANS-PROTOCOL.md for details
```

### IMPLEMENTATION_RESUME.md

**Enhance**: "Pre-Resume Checklist" with dependency checking

```markdown
### 2. Check Dependencies

- [ ] Read PLAN "Related Plans" section
- [ ] Verify prerequisites are complete
- [ ] Check if blocked by another PLAN
- [ ] See MULTIPLE-PLANS-PROTOCOL.md for dependency types
```

### PLAN Template

**Add**: "Related Plans" section to template

```markdown
### Related Plans

[Document dependencies using MULTIPLE-PLANS-PROTOCOL.md format]
```

---

## ⚠️ Common Mistakes

### ❌ Ignoring Dependencies

**Wrong**: Start PLAN_B without checking if PLAN_A blocks it

**Right**: Always check dependencies before starting

### ❌ Working on Multiple PLANs Simultaneously

**Wrong**: Mark 3 PLANs as "In Progress" at once

**Right**: Only ONE "In Progress" at a time (unless explicitly coordinated)

### ❌ Not Updating When Status Changes

**Wrong**: Dependency completes but dependent PLAN not updated

**Right**: Update dependent PLANs when prerequisites complete

### ❌ Not Documenting Conflicts

**Wrong**: Both PLANs modify same code, no coordination

**Right**: Document code overlaps, coordinate work

---

## 🔗 Quick Reference

**Dependency Types**:

- **Hard**: Cannot proceed without dependency (blocking)
- **Soft**: Benefits from dependency, can proceed (quality improvement)
- **Data**: Uses data from dependency (data flow)
- **Code**: Modifies same code (coordination needed)
- **Sequential**: Natural pipeline order (staged work)
- **Decision Context**: Needs to understand WHY decisions were made (knowledge transfer)

**Workflow**:

1. Check dependencies before starting
2. Document in PLAN "Related Plans"
3. Update ACTIVE_PLANS.md
4. Coordinate if conflicts exist
5. Update when status changes

**Decision**:

- Hard dependency? → Wait
- Code conflict? → Sequential or coordinate
- Soft dependency? → Can proceed, but consider waiting
- Independent? → Proceed freely

---

## 🌳 GrammaPlan Coordination

### What is GrammaPlan?

**GrammaPlan** (GrandMotherPlan) = Orchestration document for large initiatives that coordinates multiple child PLANs.

**When to Use**: See `LLM/guides/GRAMMAPLAN-GUIDE.md` for full criteria. Use when PLAN would exceed 800 lines OR >80 hours OR spans 3+ domains.

### GrammaPlan vs Multiple Plans Protocol

**Key Relationship**: GrammaPlan **uses** Multiple Plans Protocol for child coordination.

**Differences**:

| Aspect          | Multiple Plans Protocol                    | GrammaPlan                          |
| --------------- | ------------------------------------------ | ----------------------------------- |
| **Purpose**     | Manage independent PLANs with dependencies | Orchestrate unified initiative      |
| **Structure**   | Flat (all PLANs are peers)                 | Hierarchical (parent-child)         |
| **Goal**        | Coordinate parallel work                   | Achieve strategic goal via children |
| **Typical Use** | 2-5 independent PLANs                      | 1 GrammaPlan + 3-8 child PLANs      |

**When to Use Each**:

- **Multiple Plans Protocol**: Independent PLANs that may have dependencies (e.g., 4 GraphRAG stage refactors)
- **GrammaPlan**: Large work naturally divided into child PLANs (e.g., Code Quality across 6 domains)

### Child PLAN Coordination

**Use Standard Protocol for Children**:

When coordinating child PLANs within a GrammaPlan, use the dependency tracking format from this protocol:

```markdown
## Child PLAN Dependencies (in GrammaPlan)

**PLAN_CODE-QUALITY-LIBRARIES.md**:

- **Type**: Hard dependency (provides libraries to all domains)
- **Relationship**: Sequential (must complete before domains)
- **Dependency**: Domains need libraries
- **Status**: In Progress
- **Timing**: Must complete first

**PLAN_CODE-QUALITY-GRAPHRAG.md**:

- **Type**: Soft dependency on Libraries
- **Relationship**: Parallel (can run with existing libraries)
- **Dependency**: Benefits from new libraries
- **Status**: Can proceed
- **Timing**: After foundation, parallel with other domains
```

### GrammaPlan Tracking in ACTIVE_PLANS.md

**Format**:

```markdown
### GrammaPlans

| GrammaPlan                 | Status    | Priority | Completion    | Children        | Next    |
| -------------------------- | --------- | -------- | ------------- | --------------- | ------- |
| GRAMMAPLAN_CODE-QUALITY.md | 🚀 Active | HIGH     | 40% (60/150h) | 6 (1✅ 2🔨 3⏸️) | CHILD-3 |

**Child PLANs**:

- [x] PLAN_CODE-QUALITY-FOUNDATION.md (100% - 20/20h) ✅
- [~] PLAN_CODE-QUALITY-GRAPHRAG.md (80% - 24/30h) 🔨
- [~] PLAN_CODE-QUALITY-INGESTION.md (60% - 15/25h) 🔨
- [ ] PLAN_CODE-QUALITY-RAG.md (50% - 10/20h) ⏸️
- [ ] PLAN_CODE-QUALITY-CHAT.md (0% - 0/15h) ⏸️
- [ ] PLAN_CODE-QUALITY-CORE.md (0% - 0/20h) ⏸️
```

### Context Switching with GrammaPlan

**Rule**: Only **ONE child PLAN** should be "In Progress" at a time (unless explicitly coordinating parallel work).

**Workflow**:

1. **Pause Current Child**:

   - Update child PLAN "Current Status"
   - Commit changes
   - Mark as "⏸️ Paused" in GrammaPlan

2. **Update GrammaPlan**:

   - Update child status table
   - Recalculate overall progress
   - Note which child is next

3. **Resume Next Child**:
   - Follow IMPLEMENTATION_RESUME.md for child PLAN
   - Mark as "🔨 In Progress" in GrammaPlan
   - Update ACTIVE_PLANS.md

### GrammaPlan Completion

**Complete When**:

1. All required child PLANs complete (or explicitly deprioritized)
2. Integration validated (if applicable)
3. Strategic goal achieved

**Process**:

1. Mark last child complete
2. Verify integration across children
3. Update GrammaPlan status to "Complete"
4. Follow IMPLEMENTATION_END_POINT for GrammaPlan
5. Archive GrammaPlan + all children together

### GrammaPlan Archiving

**Structure**:

```
documentation/archive/grammaplan-[name]-[date]/
├── INDEX.md
├── GRAMMAPLAN_[FEATURE].md
├── planning/
│   └── PLAN_[FEATURE]-[CHILD-*].md (all children)
├── subplans/
│   └── SUBPLAN_* (from all children)
├── execution/
│   └── EXECUTION_TASK_* (from all children)
└── summary/
    └── GRAMMAPLAN-[FEATURE]-COMPLETE.md
```

**Key**: Archive GrammaPlan and ALL children together as one cohesive unit.

---

**Status**: Permanent Reference  
## 🎯 Meta-PLAN Special Handling

**What is a Meta-PLAN?**: A PLAN that defines the methodology for all other PLANs (e.g., PLAN_STRUCTURED-LLM-DEVELOPMENT.md)

### Identifying Meta-PLANs

**Characteristics**:

1. **Process-Defining**: Defines HOW to create/execute other PLANs (not WHAT to implement)
2. **Self-Referential**: Uses the methodology it defines (creates itself following its own rules)
3. **Universal Dependency**: ALL other PLANs depend on it (explicitly or implicitly)
4. **Cascading Impact**: Changes affect all existing and future PLANs
5. **Template-Defining**: Creates/modifies templates used by other PLANs

**Examples**:

- ✅ **Meta-PLAN**: PLAN_STRUCTURED-LLM-DEVELOPMENT.md (defines PLAN/SUBPLAN/EXECUTION_TASK methodology)
- ❌ **Not Meta**: PLAN_ENTITY-RESOLUTION-REFACTOR.md (implements feature using methodology)
- ❌ **Not Meta**: GRAMMAPLAN_LLM-METHODOLOGY-V2 (uses methodology but doesn't define it)

**In Related Plans Section**:

```markdown
**PLAN_STRUCTURED-LLM-DEVELOPMENT.md**:

- **Type**: Meta (defines methodology for all PLANs)
- **Relationship**: Universal (all PLANs use this methodology)
- **Dependency**: All PLANs depend on stable methodology
- **Status**: Foundation complete (v1.4)
- **Timing**: Methodology ready for use
```

---

### Meta-PLAN Versioning

**Policy**: Semantic versioning adapted for methodology (major.minor format)

**Version Format**: `v[MAJOR].[MINOR]`

- **Major** (v1 → v2): Breaking changes
  - Format changes (PLAN template structure changed)
  - Removed features (deprecated features removed)
  - Renamed files/sections (breaks existing references)
  - **Impact**: Requires all PLANs to update
  - **Example**: v1 → v2 if we changed PLAN template structure fundamentally

- **Minor** (v1.0 → v1.1): Additive changes
  - New features (GrammaPlan, Mid-Plan Review, Pre-Completion Review)
  - Enhanced templates (added sections)
  - New protocols (MULTIPLE-PLANS-PROTOCOL, MID_PLAN_REVIEW)
  - **Impact**: Optional for existing PLANs, recommended for new PLANs
  - **Example**: v1.3 → v1.4 when we added GrammaPlan support

**Current Version**: v1.4 (as of November 2025)

**Version History** (track in meta-PLAN):
- v1.0: Foundation (START_POINT, END_POINT, templates)
- v1.1: RESUME protocol added
- v1.2: BACKLOG process added
- v1.3: MULTIPLE-PLANS-PROTOCOL added
- v1.4: GrammaPlan, Mid-Plan Review, Pre-Completion Review, Execution Statistics added

**When to Bump**:
- Always bump when merging changes to meta-PLAN
- Announce in CHANGELOG.md
- Update "Version History" section in meta-PLAN

---

### Cascading Update Process

**Decision Tree**:

```
Meta-PLAN changed?
├─ Breaking change (format change, removed feature)?
│   ├─ Action: MANDATORY UPDATE
│   ├─ When: Within 1 week OR before PLAN resume
│   ├─ How:
│   │   - Review all active/paused PLANs
│   │   - Update to new format
│   │   - Document in CHANGELOG
│   │   - Add "Methodology Updated" note to each PLAN
│   └─ Communication:
│       - CHANGELOG.md entry (major changes)
│       - Meta-PLAN update note (breaking changes section)
│       - Affected PLAN updates (compliance notes)
│
├─ Additive change (new feature like GrammaPlan)?
│   ├─ Action: OPTIONAL UPDATE (on-resume basis)
│   ├─ When: Next time PLAN is resumed
│   ├─ How:
│   │   - IMPLEMENTATION_RESUME.md Step 2.6 catches this
│   │   - Update "Related Plans" format if needed
│   │   - Add new sections if template changed
│   └─ Communication:
│       - CHANGELOG.md entry (minor changes)
│       - Meta-PLAN version bump (minor)
│       - No immediate action required
│
└─ Fix/clarification (typo, better wording)?
    ├─ Action: NO UPDATE NEEDED
    ├─ When: Never (historical PLANs stay as-is)
    └─ Communication:
        - CHANGELOG.md entry (patch notes)
        - Meta-PLAN version stays same (or patch bump)
```

**Examples from Recent Changes**:

- **GrammaPlan Addition** (v1.3 → v1.4, Additive):
  - Added to templates and guides
  - Existing PLANs NOT updated immediately
  - Will update on-resume via RESUME Step 2.6 ✅

- **Mid-Plan Review, Pre-Completion Review** (v1.4, Additive):
  - Added to PLAN template
  - Integration gaps found in Achievement 0.1 ✅
  - Fixed by adding to START_POINT/END_POINT ✅
  - Existing PLANs will adopt on next creation/resume

---

### Compliance Auditing

**Purpose**: Ensure all PLANs stay current with latest methodology

**Audit Triggers**:

1. **After Meta-PLAN Changes** (within 1 week):
   - If breaking change: Audit all PLANs immediately
   - If additive change: Schedule audit for next quarter
   - If fix: No audit needed

2. **Quarterly Review** (every 3 months):
   - Audit all active/paused PLANs
   - Check compliance with current methodology version
   - Update non-compliant PLANs or document exceptions

3. **Before PLAN Resume** (automatic):
   - IMPLEMENTATION_RESUME.md Step 2.6 checks compliance
   - Updates format if needed
   - No separate audit needed (built into resume)

**Audit Process**:

```
For each PLAN:
1. Check "Related Plans" section format (6-type format?)
2. Check template compliance (all required sections present?)
3. Check naming compliance (follows conventions?)
4. Check references valid (no broken links?)
5. Document findings in EXECUTION_ANALYSIS if large audit
6. Fix issues:
   - Immediate fix for breaking issues
   - Schedule fix for minor issues
   - Document exceptions if intentional
```

**Audit Tools**:

- `scripts/validate_references.py` (Achievement 0.1) - checks broken links
- Future: `scripts/validate_plan_structure.py` (from AUTOMATION plan) - checks format
- Manual: Review "Related Plans" format compliance

**Case Study**: 

EXECUTION_ANALYSIS_PLAN-COMPLIANCE-AUDIT.md (November 2025) audited 6 PLANs after MULTIPLE-PLANS-PROTOCOL changes, found 1 critical gap (missing "Related Plans" section), fixed immediately.

---

### Meta-PLAN Feature Integration Checklist

**Purpose**: Prevent discoverability issues when adding features to methodology

**Background**: Achievement 0.1 (Reference Verification) discovered that Mid-Plan Review, Pre-Completion Review, and Execution Statistics were added to templates but NOT integrated into entry/exit protocols. Users couldn't discover these features without reading templates directly.

**Checklist** (use when adding ANY feature to meta-PLAN):

```markdown
When adding feature to meta-PLAN templates or protocols:

Step 1: Template/Protocol Updates
- [ ] Feature added to relevant template (PLAN, SUBPLAN, EXECUTION_TASK, GRAMMAPLAN)
- [ ] Feature documented with purpose, usage, examples
- [ ] Template version updated

Step 2: Entry/Exit Protocol Integration
- [ ] Check: Is feature relevant to IMPLEMENTATION_START_POINT?
  - [ ] If yes: Add section explaining when/how to use
  - [ ] If no: Document why not applicable
- [ ] Check: Is feature relevant to IMPLEMENTATION_END_POINT?
  - [ ] If yes: Add to completion checklist or quality analysis
  - [ ] If no: Document why not applicable
- [ ] Check: Is feature relevant to IMPLEMENTATION_RESUME?
  - [ ] If yes: Add to resume checklist or compliance step
  - [ ] If no: Document why not applicable
- [ ] Check: Is feature relevant to IMPLEMENTATION_MID_PLAN_REVIEW?
  - [ ] If yes: Add to review checklist
  - [ ] If no: Document why not applicable
- [ ] Check: Is feature relevant to MULTIPLE-PLANS-PROTOCOL?
  - [ ] If yes: Add section or update existing
  - [ ] If no: Document why not applicable

Step 3: Discovery & Communication
- [ ] Feature mentioned in meta-PLAN README or overview
- [ ] Example added to documentation (real usage preferred)
- [ ] Cross-references added (bidirectional links)
- [ ] CHANGELOG.md entry created
- [ ] Meta-PLAN version bumped (minor for additive)

Step 4: Validation
- [ ] Run scripts/validate_references.py (no broken links)
- [ ] Dry-run test: Can someone use feature from entry point?
- [ ] Check: Is feature discoverable without deep doc reading?

Step 5: Learning Capture
- [ ] Document in meta-PLAN what was learned
- [ ] Update this checklist if new integration points discovered
```

**Case Study - What Happens Without This**:

Achievement 0.1 found 3 integration gaps:
1. Mid-Plan Review: Added to template but not START_POINT → Users couldn't discover
2. Pre-Completion Review: Added to template but not END_POINT → Users might skip
3. Execution Statistics: Added to template but END_POINT didn't reference → Underutilized

All fixed in Achievement 0.1, but this checklist prevents recurrence.

---

### Meta-PLAN Execution Considerations

**Self-Reference Challenge**:

When executing the meta-PLAN itself (PLAN_STRUCTURED-LLM-DEVELOPMENT.md):
- You're using a methodology that you're simultaneously changing
- Changes made during execution become the new standard
- Must be extra careful about consistency

**Best Practices**:

1. **Test Changes in Examples**: Add to template, test in example PLAN before declaring done
2. **Document Rationale**: Explain WHY each change, not just WHAT changed
3. **Compliance Check Self**: Meta-PLAN should follow its own rules
4. **Integration Verification**: Use integration checklist on self

**Current Example**:

GRAMMAPLAN_LLM-METHODOLOGY-V2 is improving PLAN_STRUCTURED-LLM-DEVELOPMENT.md using the methodology defined by that same plan. This requires careful tracking and self-awareness.

---

### Summary: Meta-PLAN Management

**Remember**:

1. **Meta-PLANs are different**: Universal dependency, cascading impact, self-referential
2. **Version everything**: Track methodology changes explicitly
3. **Communicate widely**: Breaking changes need loud announcements
4. **Audit compliance**: Ensure other PLANs stay current
5. **Use integration checklist**: Prevent discoverability issues
6. **Self-reference carefully**: Meta-PLAN execution requires extra diligence

**Tools**:

- Integration checklist (above)
- Compliance audit triggers (above)
- Version bump rules (above)
- `scripts/validate_references.py` (checks links)

---

**Created**: 2025-11-06 23:00 UTC  
**Updated**: 2025-11-07 (GrammaPlan support, Meta-PLAN special handling)  
**Purpose**: Systematic management of multiple PLANs with dependencies, GrammaPlan orchestration, Meta-PLAN special rules
