# SUBPLAN Workflow Guide: Independent Designer/Executor Separation

**Purpose**: Guide for the new SUBPLAN independent workflow enabling true multi-agent coordination  
**Status**: Permanent Reference  
**Created**: 2025-11-08  
**Related**: SUBPLAN-TEMPLATE.md, EXECUTION_TASK-TEMPLATE.md, IMPLEMENTATION_START_POINT.md

---

## 🎯 Overview

### What is the New Workflow?

**Old Workflow** (Conflated):

```
PLAN Achievement → SUBPLAN → Immediate EXECUTION
                    (Designer + Executor merged)
```

**New Workflow** (Separated):

```
PLAN Achievement → SUBPLAN (Designer) → EXECUTION_TASK(s) (Executor)
                    Design Phase          Execution Phase
                    (Can plan multiple)   (Can run parallel)
```

**Key Change**: SUBPLAN and EXECUTION are now **independent phases**:

- **Designer Agent** (SUBPLAN): Creates design, plans execution(s)
- **Executor Agent** (EXECUTION_TASK): Executes according to plan
- **Separation**: Designer completes design BEFORE execution starts
- **Multi-Execution**: Designer can plan multiple EXECUTIONs (parallel or sequential)

### Why Separate Designer and Executor?

**Benefits**:

1. **True Multi-Agent Coordination**: Designer coordinates multiple Executors
2. **Parallel Execution**: Independent EXECUTIONs can run simultaneously
3. **Better Design**: Designer can iterate on design without execution pressure
4. **Clear Roles**: Designer thinks, Executor acts
5. **Foundation for Concurrency**: Enables concurrent multi-agent systems

**Context Budget Impact**:

- **Before**: SUBPLAN + EXECUTION in same context = 600+ lines
- **After**: EXECUTION reads SUBPLAN objective only = 200 lines total!

---

## 🔄 Four-Phase Workflow

### Phase 1: Design (Designer Agent)

**Goal**: Create comprehensive SUBPLAN with deep analysis and design

**Steps**:

1. **Read PLAN Achievement** (~100 lines):

   - Understand what needs to be achieved
   - Identify requirements and constraints
   - Note dependencies and context

2. **Create SUBPLAN**:

   - Use `LLM/templates/SUBPLAN-TEMPLATE.md`
   - File: `work-space/subplans/SUBPLAN_[PLAN]_[ACHIEVEMENT].md`
   - Size: 200-600 lines

3. **Analyze Requirements Deeply**:

   - Break down achievement into components
   - Identify technical challenges
   - Consider multiple approaches
   - Research existing solutions

4. **Design Approach**:

   - Choose best approach (or multiple for comparison)
   - Define deliverables clearly
   - Plan implementation steps
   - Identify risks and mitigations

5. **Identify Execution Strategies**:

   - Single approach? → Single EXECUTION
   - Multiple approaches? → Multiple EXECUTIONs (A/B test)
   - Iterative refinement? → Sequential EXECUTIONs
   - Independent components? → Parallel EXECUTIONs

6. **Plan Multiple EXECUTIONs (if needed)**:

   - Decide execution count
   - Determine parallel vs. sequential
   - Define success criteria per execution
   - Document execution strategy in SUBPLAN

7. **Define Success Criteria**:
   - What does "done" look like?
   - How to verify deliverables?
   - What quality standards apply?

**⚠️ CRITICAL**: **Do NOT execute yet** - complete design first!

**Design Iteration**: Designer can iterate on SUBPLAN design, refine approach, update strategy - all before execution starts.

**Example SUBPLAN Sections**:

- Objective (what we're achieving)
- Deliverables (what we're creating)
- Approach (how we'll do it)
- Execution Strategy (single or multiple? parallel or sequential?)
- Tests Required (how we'll verify)
- Expected Results (what success looks like)

---

### Phase 2: Execution Planning (Designer Agent)

**Goal**: Plan how execution will proceed (single or multiple EXECUTIONs)

**Decision: Single or Multiple EXECUTIONs?**

**Use Single EXECUTION when**:

- Single clear approach
- Straightforward implementation
- No need for comparison
- No iterative refinement needed

**Use Multiple EXECUTIONs when**:

- A/B testing approaches
- Iterative refinement (each builds on previous)
- Parallel independent work
- Comparison needed

**Decision: Parallel or Sequential?**

**Use Parallel when**:

- EXECUTIONs are independent
- No dependencies between them
- Can run simultaneously
- Example: Test 3 different algorithms in parallel

**Use Sequential when**:

- Later EXECUTIONs depend on earlier results
- Iterative refinement (each improves on previous)
- Need results from one before starting next
- Example: Implement, test, refine, test again

**Execution Planning Steps**:

1. **Decide Execution Count**:

   - Review design from Phase 1
   - Apply decision tree above
   - Document decision in SUBPLAN

2. **Create EXECUTION_TASK File(s)**:

   - Single: `EXECUTION_TASK_[PLAN]_[ACHIEVEMENT]_01.md`
   - Multiple: `EXECUTION_TASK_[PLAN]_[ACHIEVEMENT]_01.md`, `_02.md`, `_03.md`
   - Location: `work-space/execution/`
   - Size: <200 lines each

3. **Document Execution Strategy in SUBPLAN**:

   - Add "Execution Plan" section
   - Document: "Single EXECUTION" or "Multiple EXECUTIONs (parallel/sequential)"
   - Explain rationale
   - Define success criteria per execution

4. **For Multiple EXECUTIONs**:
   - Define what each EXECUTION will do
   - Specify dependencies (if sequential)
   - Define how results will be synthesized
   - Document parallel coordination (if parallel)

**Example Execution Plan in SUBPLAN**:

```markdown
## 🔄 Execution Plan

**Execution Count**: 3 EXECUTIONs (parallel)

**Rationale**: Testing 3 different algorithms to compare performance

**EXECUTION 01**: Algorithm A (baseline)
**EXECUTION 02**: Algorithm B (optimized)
**EXECUTION 03**: Algorithm C (alternative approach)

**Coordination**: All 3 run in parallel, results compared in Phase 4
```

---

### Phase 3: Execution (Executor Agent)

**Goal**: Execute EXECUTION_TASK(s) according to SUBPLAN plan

**How Executor Reads SUBPLAN**:

**Executor Context** (minimal):

- SUBPLAN objective (2 sentences)
- SUBPLAN approach (relevant section)
- Deliverables for this EXECUTION
- Success criteria

**Executor Does NOT Read**:

- Full SUBPLAN (200-600 lines)
- Other EXECUTION plans (if multiple)
- Design iterations
- Full PLAN achievement

**Execution Steps**:

1. **Read SUBPLAN Objective**:

   - Understand what this EXECUTION achieves
   - Note approach and deliverables
   - Understand success criteria

2. **Execute Work**:

   - Implement according to SUBPLAN approach
   - Create deliverables
   - Follow TDD workflow if code
   - Document journey in EXECUTION_TASK

3. **For Parallel EXECUTIONs**:

   - Execute independently
   - No coordination needed during execution
   - Document results in own EXECUTION_TASK
   - Results synthesized in Phase 4

4. **For Sequential EXECUTIONs**:

   - Wait for previous EXECUTION to complete
   - Read previous EXECUTION results
   - Build on previous results
   - Document journey

5. **Document Journey**:
   - Log iterations in EXECUTION_TASK
   - Capture learnings
   - Note what worked/didn't
   - Document completion status

**Executor Independence**:

- Each Executor works independently
- No need to coordinate during execution
- Designer reviews results in Phase 4
- Parallel execution is natural (no blocking)

---

### Phase 4: Synthesis (Designer Agent)

**Goal**: Review all EXECUTION results, synthesize learnings, complete SUBPLAN

**Synthesis Steps**:

1. **Review All EXECUTION Results**:

   - Read all EXECUTION_TASK files
   - Understand what each achieved
   - Note learnings from each
   - Identify patterns

2. **Synthesize Collective Learnings**:

   - What worked across all EXECUTIONs?
   - What didn't work?
   - What patterns emerged?
   - What should be adopted?

3. **For Multiple EXECUTIONs**:

   - Compare results
   - Identify best approach
   - Document why one succeeded
   - Capture insights

4. **Update SUBPLAN**:

   - Add "Synthesis" section
   - Document collective learnings
   - Note which approach worked best (if multiple)
   - Capture insights

5. **Request Achievement Feedback** (Filesystem-First):

   - Request reviewer to create `execution/feedbacks/APPROVED_XX.md` (if approved)
   - Or create `execution/feedbacks/FIX_XX.md` (if fixes needed)
   - Achievement completion tracked via filesystem, not PLAN markdown
   - Do NOT manually update PLAN with "✅ Achievement complete"

6. **Archive Together**:
   - Move SUBPLAN to archive
   - Move all EXECUTION_TASKs to archive
   - Keep APPROVED_XX.md in execution/feedbacks/ (not archived)
   - Create completion summary

**Reference**: See `LLM/templates/SUBPLAN-TEMPLATE.md` "Completion Workflow" section for details

**Synthesis Example**:

```markdown
## 📊 Synthesis

**EXECUTION 01 Results**: Algorithm A - Baseline performance: 50ms
**EXECUTION 02 Results**: Algorithm B - Optimized: 30ms ✅ Best
**EXECUTION 03 Results**: Algorithm C - Alternative: 45ms

**Learnings**:

- Algorithm B 40% faster than baseline
- Optimization technique X was key
- Algorithm C not worth pursuing

**Decision**: Adopt Algorithm B for production
```

---

## 🤔 Decision Trees

### When to Use Single vs. Multiple EXECUTIONs?

```
Question 1: Is there a single clear approach?
├─ Yes → Single EXECUTION
└─ No  → Question 2

Question 2: Do we need to compare approaches?
├─ Yes → Multiple EXECUTIONs (A/B test)
└─ No  → Question 3

Question 3: Is iterative refinement needed?
├─ Yes → Multiple EXECUTIONs (sequential)
└─ No  → Question 4

Question 4: Are there independent components?
├─ Yes → Multiple EXECUTIONs (parallel)
└─ No  → Single EXECUTION
```

### When to Use Parallel vs. Sequential?

```
Question 1: Are EXECUTIONs independent?
├─ Yes → Parallel
└─ No  → Question 2

Question 2: Does later EXECUTION depend on earlier results?
├─ Yes → Sequential
└─ No  → Question 3

Question 3: Is this iterative refinement?
├─ Yes → Sequential (each improves on previous)
└─ No  → Parallel (if truly independent)
```

### Decision Criteria Summary

**Single EXECUTION**:

- ✅ Single clear approach
- ✅ Straightforward implementation
- ✅ No comparison needed
- ✅ No iteration needed

**Multiple EXECUTIONs - Parallel**:

- ✅ A/B testing approaches
- ✅ Independent components
- ✅ No dependencies
- ✅ Comparison needed

**Multiple EXECUTIONs - Sequential**:

- ✅ Iterative refinement
- ✅ Later depends on earlier
- ✅ Building on results
- ✅ Progressive improvement

---

## 📊 Workflow Diagrams

### Complete Workflow

```
┌─────────────────────────────────────────────────────────┐
│ PHASE 1: DESIGN (Designer Agent)                        │
│                                                          │
│  PLAN Achievement                                        │
│      ↓                                                   │
│  Create SUBPLAN                                          │
│  • Analyze requirements                                  │
│  • Design approach                                       │
│  • Plan execution(s)                                     │
│  • Define success criteria                               │
│                                                          │
│  ⚠️ Do NOT execute yet                                   │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ PHASE 2: EXECUTION PLANNING (Designer Agent)            │
│                                                          │
│  Decide: Single or Multiple?                            │
│  Decide: Parallel or Sequential?                        │
│                                                          │
│  Create EXECUTION_TASK file(s)                          │
│  Document strategy in SUBPLAN                           │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ PHASE 3: EXECUTION (Executor Agent(s))                  │
│                                                          │
│  Single:                                                 │
│    EXECUTION_TASK_01 → Execute → Document               │
│                                                          │
│  Multiple (Parallel):                                    │
│    EXECUTION_TASK_01 ─┐                                 │
│    EXECUTION_TASK_02 ─┼→ Execute in parallel            │
│    EXECUTION_TASK_03 ─┘                                 │
│                                                          │
│  Multiple (Sequential):                                  │
│    EXECUTION_TASK_01 → Execute → Results                 │
│         ↓                                                │
│    EXECUTION_TASK_02 → Execute (uses results)            │
│         ↓                                                │
│    EXECUTION_TASK_03 → Execute (uses results)            │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ PHASE 4: SYNTHESIS (Designer Agent)                     │
│                                                          │
│  Review all EXECUTION results                            │
│  Synthesize learnings                                   │
│  Update SUBPLAN with synthesis                          │
│  Mark SUBPLAN complete                                  │
│  Archive together                                       │
└─────────────────────────────────────────────────────────┘
```

### Parallel Execution Pattern

```
Designer creates SUBPLAN with 3 parallel EXECUTIONs:

SUBPLAN
  ├─ EXECUTION_TASK_01 (Executor A) ─┐
  ├─ EXECUTION_TASK_02 (Executor B) ─┼→ Execute simultaneously
  └─ EXECUTION_TASK_03 (Executor C) ─┘
                                      ↓
                              All complete
                                      ↓
                              Designer synthesizes
```

### Sequential Execution Pattern

```
Designer creates SUBPLAN with 3 sequential EXECUTIONs:

SUBPLAN
  ├─ EXECUTION_TASK_01 (Executor A)
  │     ↓ (results)
  ├─ EXECUTION_TASK_02 (Executor B) - uses results from 01
  │     ↓ (results)
  └─ EXECUTION_TASK_03 (Executor C) - uses results from 02
                                      ↓
                              All complete
                                      ↓
                              Designer synthesizes
```

---

## 💡 Examples

### Example 1: A/B Testing (Parallel Multiple EXECUTIONs)

**Scenario**: Testing two different API implementations

**SUBPLAN Design**:

- Objective: Implement API endpoint with best performance
- Approach: Test two implementations (REST vs. GraphQL)
- Execution Strategy: 2 parallel EXECUTIONs

**Phase 2: Execution Planning**:

- EXECUTION 01: Implement REST API
- EXECUTION 02: Implement GraphQL API
- Parallel: Both independent, can run simultaneously

**Phase 3: Execution**:

- Executor A: Implements REST API, documents performance
- Executor B: Implements GraphQL API, documents performance
- Both execute in parallel

**Phase 4: Synthesis**:

- Designer reviews both results
- REST: 50ms average, simpler implementation
- GraphQL: 30ms average, more complex
- Decision: Adopt GraphQL for performance (30% faster)

### Example 2: Iterative Refinement (Sequential Multiple EXECUTIONs)

**Scenario**: Refining entity resolution algorithm

**SUBPLAN Design**:

- Objective: Improve entity resolution accuracy
- Approach: Iterative refinement (each version improves on previous)
- Execution Strategy: 3 sequential EXECUTIONs

**Phase 2: Execution Planning**:

- EXECUTION 01: Baseline implementation
- EXECUTION 02: Add fuzzy matching (uses baseline results)
- EXECUTION 03: Add embedding similarity (uses EXECUTION 02 results)
- Sequential: Each builds on previous

**Phase 3: Execution**:

- Executor A: Implements baseline, measures accuracy: 75%
- Executor B: Adds fuzzy matching, measures: 82% (uses baseline for comparison)
- Executor C: Adds embedding, measures: 90% (uses EXECUTION 02 for comparison)

**Phase 4: Synthesis**:

- Baseline: 75% accuracy
- - Fuzzy matching: +7% (82%)
- - Embedding: +8% (90%)
- Learnings: Embedding similarity provides biggest improvement
- Decision: Use all three techniques for production

### Example 3: Single EXECUTION (Simple Work)

**Scenario**: Create validation script

**SUBPLAN Design**:

- Objective: Create script to validate PLAN size
- Approach: Single clear implementation
- Execution Strategy: Single EXECUTION

**Phase 2: Execution Planning**:

- Single EXECUTION: Implement validation script

**Phase 3: Execution**:

- Executor: Implements script, tests, documents

**Phase 4: Synthesis**:

- Script created and tested
- Meets requirements
- Complete

---

## 🔗 Integration Points

### With Templates

**SUBPLAN Template** (`LLM/templates/SUBPLAN-TEMPLATE.md`):

- Add "Execution Plan" section
- Document execution strategy
- Define success criteria per execution

**EXECUTION_TASK Template** (`LLM/templates/EXECUTION_TASK-TEMPLATE.md`):

- Reference parent SUBPLAN
- Document which execution this is (if multiple)
- Note dependencies (if sequential)

### With Protocols

**IMPLEMENTATION_START_POINT.md**:

- Updated to reflect new workflow
- Designer creates SUBPLAN first
- Execution starts after SUBPLAN complete

**IMPLEMENTATION_RESUME.md**:

- Resume SUBPLAN design (Phase 1)
- Resume execution planning (Phase 2)
- Resume execution (Phase 3)
- Resume synthesis (Phase 4)

### With Automation

**Prompt Generators** (future):

- `generate_subplan_prompt.py`: For Designer creating SUBPLAN
- `generate_execution_prompt.py`: For Executor executing EXECUTION_TASK
- Separate prompts for separate phases

---

## 🎓 Best Practices

### For Designers (SUBPLAN Creation)

1. **Complete Design First**:

   - Don't rush to execution
   - Iterate on design if needed
   - Plan thoroughly

2. **Consider Multiple Approaches**:

   - When uncertain, plan multiple EXECUTIONs
   - A/B testing is valuable
   - Comparison provides confidence

3. **Document Execution Strategy**:

   - Clear rationale for single vs. multiple
   - Clear rationale for parallel vs. sequential
   - Success criteria per execution

4. **Think Multi-Agent**:
   - Can multiple Executors work in parallel?
   - What coordination is needed?
   - How will results be synthesized?

### For Executors (EXECUTION_TASK Execution)

1. **Read SUBPLAN Objective Only**:

   - Don't read full SUBPLAN
   - Focus on this EXECUTION's goal
   - Understand approach and deliverables

2. **Execute Independently**:

   - Don't coordinate with other Executors (if parallel)
   - Focus on this EXECUTION's work
   - Document journey thoroughly

3. **Document Learnings**:

   - What worked?
   - What didn't?
   - What would you do differently?

4. **Complete Thoroughly**:
   - Verify deliverables exist
   - Meet quality standards
   - Document completion status

### For Synthesis

1. **Review All Results**:

   - Read all EXECUTION_TASK files
   - Understand what each achieved
   - Identify patterns

2. **Synthesize Thoughtfully**:

   - What worked across all?
   - What didn't?
   - What should be adopted?

3. **Document Learnings**:
   - Capture insights
   - Note best approaches
   - Document decisions

---

## 🆘 Common Questions

**Q: Can I execute immediately after creating SUBPLAN?**

A: Yes, but recommended to complete design first. Designer can iterate on design without execution pressure.

**Q: How many EXECUTIONs can I plan?**

A: As many as needed, but typically 1-5. More than 5 suggests achievement might be too large.

**Q: Can EXECUTIONs run in parallel?**

A: Yes! If independent, they can run simultaneously. This is a key benefit of the new workflow.

**Q: What if an EXECUTION fails?**

A: Designer reviews in Phase 4, decides whether to retry, try different approach, or accept partial success.

**Q: How do Executors coordinate if parallel?**

A: They don't need to! Each works independently. Designer synthesizes results in Phase 4.

**Q: What if I need to change approach mid-execution?**

A: Executor documents in EXECUTION_TASK. Designer reviews in Phase 4, can plan new EXECUTION if needed.

---

## 📚 Related Documentation

**Templates**:

- `LLM/templates/SUBPLAN-TEMPLATE.md` - Create SUBPLANs
- `LLM/templates/EXECUTION_TASK-TEMPLATE.md` - Create EXECUTION_TASKs

**Protocols**:

- `LLM/protocols/IMPLEMENTATION_START_POINT.md` - Start workflow
- `LLM/protocols/IMPLEMENTATION_RESUME.md` - Resume workflow
- `LLM/protocols/IMPLEMENTATION_END_POINT.md` - Complete workflow

**Guides**:

- `LLM-METHODOLOGY.md` - Full methodology overview
- `LLM/guides/FOCUS-RULES.md` - Context management

**Analysis**:

- `EXECUTION_ANALYSIS_METHODOLOGY-HIERARCHY-AND-WORKFLOW-EVOLUTION.md` - Rationale for workflow separation

---

**Ready to Use**: Follow this workflow for all new SUBPLANs!  
**Status**: Complete  
**Version**: 1.0
