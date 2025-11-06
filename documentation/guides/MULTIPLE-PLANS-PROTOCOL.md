# Multiple PLANS Protocol

**Purpose**: Guide for managing multiple active/paused PLANs simultaneously  
**Status**: Permanent Reference  
**Last Updated**: 2025-11-06 23:00 UTC  
**Related**: IMPLEMENTATION_START_POINT.md, IMPLEMENTATION_RESUME.md, ACTIVE_PLANS.md

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

**Status**: Permanent Reference  
**Created**: 2025-11-06 23:00 UTC  
**Purpose**: Systematic management of multiple PLANs with dependencies and intersections
