# GrammaPlan Guide

**Purpose**: Define GrammaPlan (GrandMotherPlan) concept for orchestrating large initiatives  
**Status**: Permanent Reference  
**Last Updated**: 2025-11-07  
**Related**: IMPLEMENTATION_START_POINT.md, MULTIPLE-PLANS-PROTOCOL.md, PLAN-TEMPLATE.md

---

## 🎯 What is a GrammaPlan?

**Definition**: A GrammaPlan is a meta-orchestration document that coordinates multiple related PLANs working toward a unified strategic goal.

**Hierarchy**:

```
GrammaPlan (orchestration level)
└── PLAN (feature/domain level)
    └── SUBPLAN (implementation approach)
        └── EXECUTION_TASK (execution log)
```

**Key Characteristics**:

1. **Minimal Content**: GrammaPlan does NOT replicate child PLAN content
2. **Coordination Focus**: Tracks child PLAN completion, manages dependencies
3. **Strategic Level**: Defines overall goal, success criteria, child relationships
4. **Ascend Pattern**: All child PLANs work toward GrammaPlan goal (dominant context)
5. **Descend Pattern**: Actual work happens in child PLANs (distributed execution)

**Size**: 600-1,500 lines (strategic coordination needs space)

**Location**: `work-space/grammaplans/GRAMMAPLAN_[NAME].md`

**Size Guidelines**:

- **600-999 lines**: Typical GrammaPlan (coordinates 3-5 PLANs)
- **1,000-1,499 lines**: Large GrammaPlan (coordinates 6-8 PLANs) - **Warning**: Consider splitting or simplifying
- **1,500+ lines**: **Error** - Must split into multiple GrammaPlans or convert to NORTH_STAR

**Validation**: Use `LLM/scripts/validation/check_grammaplan_size.py` to validate size

---

## 🤔 When to Use GrammaPlan

### Decision Criteria

Use GrammaPlan when **ANY** of these **HARD LIMITS** apply, OR **TWO OR MORE** of the other indicators:

**HARD LIMITS** (GrammaPlan REQUIRED if exceeded):

1. **Size**: PLAN would exceed **900 lines** ⚠️ **MANDATORY**
2. **Duration**: Estimated effort > **40 hours** ⚠️ **MANDATORY**

**Other Indicators** (GrammaPlan recommended if 2+ apply):

3. **Domains**: Work spans 4+ distinct domains/areas
4. **Achievements**: > 20 achievements in single PLAN
5. **Parallelism**: Natural opportunities for parallel work
6. **Context**: Medium-context model deployment
7. **Duration**: Multi-month timeline

### Rule of Thumb

**Strong GrammaPlan Indicators**:

- PLAN draft is 900+ lines ⚠️ **MANDATORY**
- Estimated effort > 40 hours ⚠️ **MANDATORY**
- PLAN draft is 1,000+ lines (strongly recommended)
- Work naturally divides into 3+ independent areas
- Team wants to work in parallel
- High risk of context loss

**Weak GrammaPlan Indicators**:

- Single focused domain
- Clear linear progression
- < 32 hours estimated
- Tight integration required
- Small team (1-2 people)

### Quick Test

**Ask yourself**:

1. "Could this be 3+ separate PLANs?" → Yes = GrammaPlan candidate
2. "Would a medium-context model struggle with this?" → Yes = GrammaPlan recommended
3. "Do we have natural parallelism?" → Yes = GrammaPlan beneficial
4. "Is this >2 months of work?" → Yes = GrammaPlan recommended

**If 2+ answers are "Yes"**: Use GrammaPlan

---

## 📐 GrammaPlan Structure

### Required Sections

1. **Header**:

   - Status (Planning / In Progress / Complete)
   - Created date
   - Goal (strategic, one sentence)
   - Priority (Critical / High / Medium / Low)
   - Total estimated effort (aggregate of children)

2. **Strategic Goal** (2-3 paragraphs):

   - What we're achieving at high level
   - Why it matters strategically
   - How child PLANs contribute

3. **Child PLANs** (central section):

   ```markdown
   ## Child PLANs

   ### PLAN\_<GRAMMAPLAN-NAME>-<DOMAIN-1>.md

   - **Status**: Planning / In Progress / Complete
   - **Estimated Effort**: X hours
   - **Progress**: Y% complete
   - **Purpose**: [One sentence - what this child delivers]
   - **Dependencies**: [Which other children this depends on]
   - **Related Sections**: [Which achieve the GrammaPlan goal]

   [Repeat for each child PLAN]
   ```

4. **Dependencies Between Children**:

   - Sequential dependencies (A must complete before B)
   - Soft dependencies (A benefits B but not blocking)
   - Parallel opportunities (A and B can run simultaneously)
   - Integration requirements (how children combine)

5. **Cross-Cutting Concerns** (optional but recommended):

   - Concerns spanning multiple children
   - Shared libraries, patterns, or infrastructure
   - Integration strategy
   - Coordination approach

6. **Success Criteria**:

   - All children complete (or specific subset)
   - Integration validated
   - Strategic goal achieved
   - Observable outcomes

7. **Current Status & Handoff**:
   - Which children are complete / in progress / pending
   - Overall progress percentage
   - Next recommended child to work on
   - Blockers or coordination needs

---

## 🌳 GrammaPlan Decomposition Patterns

### Pattern 1: Domain Decomposition

**When**: Large codebase work touching multiple distinct domains

**Structure**:

```
GRAMMAPLAN_<FEATURE>.md
├── PLAN_<FEATURE>-<DOMAIN-1>.md
├── PLAN_<FEATURE>-<DOMAIN-2>.md
├── PLAN_<FEATURE>-<DOMAIN-3>.md
└── PLAN_<FEATURE>-<DOMAIN-N>.md
```

**Example**: Code Quality Refactor

- GRAMMAPLAN_CODE-QUALITY.md
  - PLAN_CODE-QUALITY-GRAPHRAG.md
  - PLAN_CODE-QUALITY-INGESTION.md
  - PLAN_CODE-QUALITY-RAG.md
  - PLAN_CODE-QUALITY-CHAT.md
  - PLAN_CODE-QUALITY-CORE.md

**Benefits**:

- Clear domain boundaries
- High parallelism potential
- Easy to pause/resume specific domains
- Natural ownership assignment

**When to Use**:

- Multi-domain refactors
- System-wide improvements
- Cross-cutting feature additions

---

### Pattern 2: Phase Decomposition

**When**: Work has clear sequential phases with handoff points

**Structure**:

```
GRAMMAPLAN_<FEATURE>.md
├── PLAN_<FEATURE>-PHASE-1-<NAME>.md
├── PLAN_<FEATURE>-PHASE-2-<NAME>.md
└── PLAN_<FEATURE>-PHASE-3-<NAME>.md
```

**Example**: Data Migration

- GRAMMAPLAN_DB-MIGRATION.md
  - PLAN_DB-MIGRATION-PHASE-1-EXTRACT.md
  - PLAN_DB-MIGRATION-PHASE-2-TRANSFORM.md
  - PLAN_DB-MIGRATION-PHASE-3-LOAD.md

**Benefits**:

- Logical sequential flow
- Clear phase gates
- Easy to validate between phases
- Natural rollback points

**When to Use**:

- Pipeline implementations
- Migration projects
- Stepwise rollouts

---

### Pattern 3: Hybrid Decomposition

**When**: Work has both domain and phase dimensions

**Structure**:

```
GRAMMAPLAN_<FEATURE>.md
├── PLAN_<FEATURE>-FOUNDATION.md (all domains)
├── PLAN_<FEATURE>-<DOMAIN-1>.md
├── PLAN_<FEATURE>-<DOMAIN-2>.md
└── PLAN_<FEATURE>-INTEGRATION.md (all domains)
```

**Example**: Testing Infrastructure

- GRAMMAPLAN_TESTING.md
  - PLAN_TESTING-FOUNDATION.md (framework setup)
  - PLAN_TESTING-GRAPHRAG.md (GraphRAG tests)
  - PLAN_TESTING-INGESTION.md (Ingestion tests)
  - PLAN_TESTING-INTEGRATION.md (E2E tests)

**Benefits**:

- Combines phase + domain benefits
- Clear foundation and integration bookends
- Parallelism in middle layers

**When to Use**:

- Complex system changes
- Feature rollouts needing preparation
- Infrastructure improvements

---

## 📋 Child PLAN Naming Convention

### Standard Format

**Child PLANs**:

```
PLAN_<GRAMMAPLAN-NAME>-<IDENTIFIER>.md
```

**Examples**:

- `GRAMMAPLAN_CODE-QUALITY.md` → `PLAN_CODE-QUALITY-GRAPHRAG.md`
- `GRAMMAPLAN_DB-MIGRATION.md` → `PLAN_DB-MIGRATION-PHASE-1-EXTRACT.md`
- `GRAMMAPLAN_TESTING.md` → `PLAN_TESTING-FOUNDATION.md`

**Rationale**:

- Clear parent-child relationship
- Easy to identify related PLANs
- Searchable by GrammaPlan name
- Consistent with existing PLAN naming

---

## 🔗 Relationship to MULTIPLE-PLANS-PROTOCOL

### GrammaPlan Uses Multiple Plans Protocol

**Key Point**: GrammaPlan **enhances**, not **replaces**, Multiple Plans Protocol.

**How They Work Together**:

1. **GrammaPlan Level**: Coordinates child PLANs
2. **Child PLAN Level**: Use Multiple Plans Protocol for dependencies
3. **Integration**: GrammaPlan documents cross-child dependencies

**Example**:

```markdown
## Child PLAN Dependencies

**PLAN_CODE-QUALITY-LIBRARIES.md**:

- **Type**: Hard dependency (provides libraries to all domains)
- **Must complete**: Priority 7 (Library Implementation)
- **Blocks**: All domain PLANs need libraries

**PLAN_CODE-QUALITY-GRAPHRAG.md**:

- **Type**: Soft dependency on Libraries
- **Can proceed**: Using existing libraries
- **Improves**: When new libraries complete

[Use full Multiple Plans Protocol format from that guide]
```

---

## 🎯 GrammaPlan vs Single PLAN

### Comparison Matrix

| Aspect           | Single PLAN       | GrammaPlan                         |
| ---------------- | ----------------- | ---------------------------------- |
| **Size**         | < 900 lines       | 900+ lines (split across children) |
| **Effort**       | < 40 hours        | 40+ hours                          |
| **Domains**      | 1-3               | 4+                                 |
| **Parallelism**  | Sequential        | Parallel opportunities             |
| **Context**      | Single context    | Distributed context                |
| **Coordination** | Internal          | Cross-PLAN                         |
| **Resume**       | Resume whole PLAN | Resume specific child              |
| **Model Fit**    | Any model         | Better for medium models           |

### When NOT to Use GrammaPlan

**Don't create GrammaPlan for**:

- Focused, single-domain work
- Short duration (< 40 hours)
- Tight integration requirements
- Very small teams (1 person)
- Urgent bug fixes
- Exploratory work

**Rationale**: Overhead of GrammaPlan (coordination, multiple documents) isn't worth it for small work.

---

## 🚀 Creating a GrammaPlan

**💡 Quick Creation with Predefined Prompt**: See `LLM/templates/PROMPTS.md` → "Create GrammaPlan" for copy-paste ready prompt with decision criteria and structure.

**Example**:

```
Create a GrammaPlan for LLM-METHODOLOGY-V2 following @LLM/guides/GRAMMAPLAN-GUIDE.md
[... decision criteria and child PLAN breakdown auto-generated ...]
```

### Step-by-Step Process

1. **Identify Need**:

   - PLAN draft exceeds **900 lines** ⚠️ **MANDATORY** OR
   - Estimated effort > **40 hours** ⚠️ **MANDATORY** OR
   - Work spans 4+ domains OR
   - Natural parallelism exists

2. **Analyze Natural Divisions**:

   - Identify domains/phases/components
   - Map dependencies between divisions
   - Estimate effort per division
   - Confirm each division is substantial (30+ hours)

3. **Create GrammaPlan** (use template):

   - Strategic goal and rationale
   - List child PLANs (3-8 recommended)
   - Document dependencies
   - Define success criteria

4. **Create Child PLANs**:

   - Use standard PLAN template
   - Add "Parent GrammaPlan" field
   - Reference sibling PLANs in "Related Plans"
   - Keep each child focused and manageable

5. **Update ACTIVE_PLANS.md**:

   - Add GrammaPlan entry
   - Add child PLAN entries (indented)
   - Track progress hierarchically

6. **Execute**:
   - Work on one child PLAN at a time (unless coordinating parallel work)
   - Update GrammaPlan as children complete
   - Use Multiple Plans Protocol for child coordination

---

## 📊 Progress Tracking

### GrammaPlan Progress Formula

```
GrammaPlan Progress =
    (Child_1_Progress * Child_1_Effort +
     Child_2_Progress * Child_2_Effort +
     ... +
     Child_N_Progress * Child_N_Effort)
    /
    Total_Effort
```

**Example**:

```
GRAMMAPLAN_CODE-QUALITY (150 hours total)
├── PLAN_CODE-QUALITY-GRAPHRAG (30h, 100% complete) = 30h
├── PLAN_CODE-QUALITY-INGESTION (25h, 80% complete) = 20h
├── PLAN_CODE-QUALITY-RAG (20h, 50% complete) = 10h
└── PLAN_CODE-QUALITY-CHAT (15h, 0% complete) = 0h

Progress = (30 + 20 + 10 + 0) / 150 = 40%
```

### ACTIVE_PLANS.md Format

```markdown
### GrammaPlan Section

| GrammaPlan                 | Status    | Priority | Completion    | Children        | Next                  |
| -------------------------- | --------- | -------- | ------------- | --------------- | --------------------- |
| GRAMMAPLAN_CODE-QUALITY.md | 🚀 Active | HIGH     | 40% (60/150h) | 4 (1✅ 1🔨 2⏸️) | PLAN_CODE-QUALITY-RAG |

**Child PLANs**:

- [x] PLAN_CODE-QUALITY-GRAPHRAG.md (100% - 30/30h) ✅
- [~] PLAN_CODE-QUALITY-INGESTION.md (80% - 20/25h) 🔨
- [ ] PLAN_CODE-QUALITY-RAG.md (50% - 10/20h) ⏸️
- [ ] PLAN_CODE-QUALITY-CHAT.md (0% - 0/15h) ⏸️
```

---

## ✅ Completion Criteria

### GrammaPlan is Complete When

**Required**:

1. All child PLANs complete (or explicitly deprioritized)
2. Integration validated (if applicable)
3. Strategic goal achieved
4. Success criteria met
5. All documentation archived

**Process**:

1. Mark last child PLAN complete
2. Verify integration (cross-child validation)
3. Update GrammaPlan status to "Complete"
4. Follow IMPLEMENTATION_END_POINT for GrammaPlan
5. Archive GrammaPlan + all children together

---

## 📦 Archiving GrammaPlan

### Archive Structure

```
documentation/archive/grammaplan-<name>-<date>/
├── INDEX.md (GrammaPlan archive navigation)
├── GRAMMAPLAN_<FEATURE>.md (orchestration doc)
├── planning/
│   ├── PLAN_<FEATURE>-<CHILD-1>.md
│   ├── PLAN_<FEATURE>-<CHILD-2>.md
│   └── ... (all child PLANs)
├── subplans/
│   ├── SUBPLAN_<FEATURE>-<CHILD-1>_01.md
│   ├── SUBPLAN_<FEATURE>-<CHILD-2>_01.md
│   └── ... (all SUBPLANs from all children)
├── execution/
│   ├── EXECUTION_TASK_<FEATURE>-<CHILD-1>_01_01.md
│   └── ... (all EXECUTION_TASKs from all children)
└── summary/
    └── GRAMMAPLAN-<FEATURE>-COMPLETE.md
```

**Key Points**:

- GrammaPlan and all children archived together
- Maintains hierarchy in archive structure
- Single INDEX.md covers entire GrammaPlan
- Summary documents GrammaPlan-level completion

---

## 🎓 Best Practices

### Do's

1. **Keep GrammaPlan Lean**: 150-300 lines max, mostly references to children
2. **Clear Boundaries**: Each child should have clear scope
3. **Manageable Children**: 3-8 children ideal, each 30-60 hours
4. **Document Dependencies**: Use Multiple Plans Protocol format
5. **Track Progress**: Update GrammaPlan as children progress
6. **Coordinate Actively**: Check child status before starting new work
7. **Integrate Explicitly**: Plan integration phase or child

### Don'ts

1. **Don't Duplicate**: Don't replicate child PLAN content in GrammaPlan
2. **Don't Micromanage**: Trust child PLANs to manage their details
3. **Don't Over-Split**: Too many tiny children (10+) defeats purpose
4. **Don't Under-Split**: Children should be <800 lines each
5. **Don't Forget Integration**: Plan how children combine
6. **Don't Skip Dependencies**: Document child-to-child relationships

---

## 📚 Examples

### Example 1: GRAMMAPLAN_CODE-QUALITY (from case study)

**Size**: 1,247 lines → Split into 6 children (~200-300 lines each)

**Structure**:

```
GRAMMAPLAN_CODE-QUALITY.md (200 lines - orchestration)
├── PLAN_CODE-QUALITY-GRAPHRAG.md (250 lines)
├── PLAN_CODE-QUALITY-INGESTION.md (250 lines)
├── PLAN_CODE-QUALITY-RAG.md (200 lines)
├── PLAN_CODE-QUALITY-CHAT.md (200 lines)
├── PLAN_CODE-QUALITY-CORE.md (250 lines)
└── PLAN_CODE-QUALITY-LIBRARIES.md (300 lines)
```

**Dependencies**:

- LIBRARIES must complete first (provides to all)
- Domain PLANs can run in parallel after LIBRARIES
- Each domain integrates libraries independently

**Benefits**:

- 75% reduction in individual doc size
- 6x parallelism potential
- Clear domain ownership
- Easy pause/resume per domain

---

### Example 2: GRAMMAPLAN_GRAPHRAG-PIPELINE

**Scenario**: Refactor entire GraphRAG pipeline (extraction → resolution → construction → detection)

**Structure**:

```
GRAMMAPLAN_GRAPHRAG-PIPELINE.md
├── PLAN_GRAPHRAG-EXTRACTION-REFACTOR.md
├── PLAN_GRAPHRAG-ENTITY-RESOLUTION-REFACTOR.md
├── PLAN_GRAPHRAG-GRAPH-CONSTRUCTION-REFACTOR.md
└── PLAN_GRAPHRAG-COMMUNITY-DETECTION-REFACTOR.md
```

**Dependencies**:

- Sequential: Each stage depends on previous
- Extraction → Resolution → Construction → Detection

**Note**: This is actually NOT a good GrammaPlan candidate!

- Strong sequential dependencies (minimal parallelism)
- Better as 4 separate sequential PLANs
- Use Multiple Plans Protocol, not GrammaPlan

**Learning**: GrammaPlan is for parallelizable work, not purely sequential chains.

---

## 🎯 Summary

**GrammaPlan Purpose**: Orchestrate large initiatives by coordinating multiple PLANs

**Use When**:

- > **900 lines** in single PLAN ⚠️ **MANDATORY**
- > **40 hours** estimated ⚠️ **MANDATORY**
- 4+ domains (recommended)
- Natural parallelism (recommended)

**Key Benefits**:

- Reduces cognitive load per PLAN
- Enables parallel work
- Better for medium-context models
- Clearer progress tracking

**Relationship to Methodology**:

- Extends 3-tier hierarchy (PLAN/SUBPLAN/EXECUTION_TASK) to 4-tier
- Uses Multiple Plans Protocol for child coordination
- Integrates with ACTIVE_PLANS.md dashboard
- Follows same archiving process

**Next**: See GRAMMAPLAN-TEMPLATE.md for creating your first GrammaPlan

---

**Last Updated**: 2025-11-07  
**Related Documents**:

- GRAMMAPLAN-TEMPLATE.md (how to create)
- MULTIPLE-PLANS-PROTOCOL.md (child coordination)
- IMPLEMENTATION_START_POINT.md (when to create)
- ACTIVE_PLANS.md (how to track)
