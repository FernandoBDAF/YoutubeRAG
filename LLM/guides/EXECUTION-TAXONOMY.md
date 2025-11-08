# Execution Work Taxonomy Guide

**Purpose**: Establish clear conceptual model for execution-level work, distinguishing EXECUTION_TASK (implementation-focused, SUBPLAN-connected) from EXECUTION_WORK (knowledge-focused, standalone).

**Status**: ✅ Complete  
**Created**: 2025-11-09 09:05 UTC  
**Version**: 1.0

---

## 🎯 Overview

The execution layer of the LLM-METHODOLOGY has two distinct work types:

1. **EXECUTION_TASK**: Implementation work directly connected to SUBPLANs
2. **EXECUTION_WORK**: Knowledge work (analyses, case studies, observations) not directly connected to SUBPLANs

This taxonomy clarifies when to create each type and how to organize them.

---

## 📋 EXECUTION_TASK Definition

**Category**: Implementation-focused execution work

**Purpose**: Track the iterative implementation journey of a SUBPLAN, from design to completion, including experiments, debugging, learnings, and delivery of deliverables.

### Key Characteristics

- **SUBPLAN-Connected**: Always created FROM and FOR a specific SUBPLAN
- **Small & Focused**: <200 lines hard limit (keeps work focused)
- **Iteration Tracking**: Logs each iteration with approach, results, learnings
- **Test-First Driven**: TDD workflow with test creation phase
- **Achievement-Oriented**: Goal is completing the SUBPLAN's specific objective
- **Transient**: Deleted when SUBPLAN archived (TASK is not archived separately)

### Structure

```
Header (metadata, status)
├── SUBPLAN Context (objective + approach summary)
├── Objective (what this execution achieves)
├── Approach (how to do it)
├── Test Creation Phase (TDD: tests before code)
├── Iteration Log (what was tried, results, learnings)
├── Learning Summary (key insights)
└── Completion Status (final status, archive readiness)
```

### Lifecycle

1. **Created**: When SUBPLAN is ready to execute
2. **Executing**: Runs iterations, logs progress
3. **Complete**: All deliverables done, tests passing
4. **Archived**: Deleted/removed when SUBPLAN archived

### File Organization

**Location**: `work-space/execution/`

**Naming Convention**: `EXECUTION_TASK_<FEATURE>_<SUBPLAN_NUM>_<EXECUTION_NUM>.md`

**Examples**:

- `EXECUTION_TASK_ENTITY-RESOLUTION_01_01.md` (first execution of SUBPLAN_01)
- `EXECUTION_TASK_ENTITY-RESOLUTION_01_02.md` (second execution/iteration of SUBPLAN_01)

### Template

Reference: `LLM/templates/EXECUTION_TASK-TEMPLATE.md`

### Size Constraints

| Component        | Lines       | Purpose              |
| ---------------- | ----------- | -------------------- |
| Header           | ~20         | Metadata             |
| Iteration Log    | ~50-80      | Progress tracking    |
| Learning Summary | ~30-50      | Key insights         |
| Completion       | ~20         | Final status         |
| **Total Target** | **120-170** | Well under 200 limit |

---

## 📋 EXECUTION_WORK Definition

**Category**: Knowledge-focused execution work

**Purpose**: Capture standalone knowledge creation (analysis, research, case studies, observations) that informs strategy but doesn't directly implement a SUBPLAN.

### Key Characteristics

- **Standalone**: Not connected to any SUBPLAN (orphaned work)
- **Variable Size**: 200-1000+ lines (knowledge, not just tracking)
- **Analysis-Focused**: Goal is understanding, not delivery
- **Type-Specific**: ANALYSIS, CASE_STUDY, OBSERVATION, REVIEW, DEBUG
- **Persistent**: Archived by type and date for future reference
- **Strategic**: Informs future PLANs and architecture

### Work Type Categories

#### 1. EXECUTION_ANALYSIS

- **Purpose**: Structured investigation of specific problems/situations
- **5 Subcategories**:

  1. **Bug-Analysis**: Root cause of specific issues
  2. **Methodology-Review**: Process and workflow assessment
  3. **Implementation-Review**: Code/feature quality check
  4. **Process-Analysis**: Workflow and system analysis
  5. **Planning-Strategy**: Strategic planning and roadmaps

- **Characteristics**:

  - Evidence-based findings
  - Clear problem definition
  - Root cause analysis
  - Recommendations and action items
  - Structured investigation

- **Template**: `LLM/templates/EXECUTION_ANALYSIS-<TYPE>-TEMPLATE.md`
- **Naming**: `EXECUTION_ANALYSIS_<TOPIC>.md`
- **Examples**:
  - `EXECUTION_ANALYSIS_PROMPT-GENERATOR-0.1-BUG.md`
  - `EXECUTION_ANALYSIS_METHODOLOGY-REVIEW.md`
  - `EXECUTION_ANALYSIS_ENTITY-RESOLUTION-DESIGN.md`

#### 2. EXECUTION_CASE-STUDY

- **Purpose**: Deep dive into specific feature/pattern with lessons
- **Characteristics**:

  - Real example from codebase
  - Pattern identification
  - Lessons extracted
  - Generalizable insights
  - Practical guidance

- **Template**: `LLM/templates/EXECUTION_CASE-STUDY-TEMPLATE.md`
- **Naming**: `EXECUTION_CASE-STUDY_<FEATURE>.md`
- **Example**: `EXECUTION_CASE-STUDY_ENTITY-RESOLUTION-WORKFLOW.md`

#### 3. EXECUTION_OBSERVATION

- **Purpose**: Real-time feedback and discoveries during work
- **Characteristics**:

  - Informal findings
  - Immediate insights
  - Quick feedback
  - May evolve into ANALYSIS later
  - Living document

- **Template**: Simple structure (no formal template yet)
- **Naming**: `EXECUTION_OBSERVATION_<TOPIC>_<DATE>.md`
- **Example**: `EXECUTION_OBSERVATION_PERFORMANCE-BOTTLENECK_2025-11-09.md`

#### 4. EXECUTION_REVIEW

- **Purpose**: Post-completion assessment of implementation
- **Characteristics**:

  - Evaluates quality
  - Verifies requirements
  - Identifies gaps
  - Suggests improvements
  - May lead to new SUBPLANs

- **Template**: May use EXECUTION_ANALYSIS-IMPLEMENTATION-REVIEW
- **Naming**: `EXECUTION_REVIEW_<FEATURE>.md`
- **Example**: `EXECUTION_REVIEW_API-IMPLEMENTATION.md`

#### 5. EXECUTION_DEBUG

- **Purpose**: Debugging work for complex issues
- **Characteristics**:

  - Deep investigation
  - Reproduction steps
  - Root cause found
  - Solution documented
  - May become BUG-ANALYSIS

- **Template**: May use EXECUTION_ANALYSIS-BUG or custom
- **Naming**: `EXECUTION_DEBUG_<ISSUE>.md`
- **Example**: `EXECUTION_DEBUG_CIRCULAR-REFERENCE-BUG.md`

### Lifecycle

1. **Created**: Ad-hoc when knowledge work needed
2. **Active**: In `work-space/analyses/` or similar while being worked on
3. **Archived**: Moved to `documentation/archive/` by type/category
4. **Referenced**: Used to inform future PLANs and decisions

### File Organization

**Active Location**:

- `work-space/analyses/` (for EXECUTION_ANALYSIS)
- `work-space/case-studies/` (for EXECUTION_CASE_STUDY)
- `work-space/observations/` (for EXECUTION_OBSERVATION)

**Archive Location**:

- `documentation/archive/execution-analyses/` (by category)
- `documentation/archive/case-studies/` (by topic)
- `documentation/archive/observations/` (by date)

### Naming Convention

**Pattern**: `EXECUTION_<TYPE>_<TOPIC>.md`

**Examples**:

- ANALYSIS: `EXECUTION_ANALYSIS_<TOPIC>.md`
- CASE*STUDY: `EXECUTION_CASE-STUDY*<FEATURE>.md`
- OBSERVATION: `EXECUTION_OBSERVATION_<TOPIC>_<DATE>.md`
- REVIEW: `EXECUTION_REVIEW_<FEATURE>.md`
- DEBUG: `EXECUTION_DEBUG_<ISSUE>.md`

---

## 🔄 Side-by-Side Comparison

| Aspect           | EXECUTION_TASK                                 | EXECUTION_WORK                        |
| ---------------- | ---------------------------------------------- | ------------------------------------- |
| **Purpose**      | Implement a SUBPLAN                            | Generate knowledge                    |
| **Connection**   | SUBPLAN-connected                              | Standalone (orphaned)                 |
| **Focus**        | Implementation                                 | Analysis/Understanding                |
| **Size**         | <200 lines (hard limit)                        | 200-1000+ lines                       |
| **Lifecycle**    | SUBPLAN → Execute → Archive with SUBPLAN       | Create → Active → Archive by type     |
| **Types**        | Single type (EXECUTION_TASK)                   | 5+ types (ANALYSIS, CASE_STUDY, etc.) |
| **Tracking**     | Iteration-based                                | Topic/analysis-based                  |
| **Deliverables** | Feature/fix implementation                     | Knowledge/insights                    |
| **Tests**        | TDD workflow (required)                        | Verification-based                    |
| **Ownership**    | Executor (from SUBPLAN designer)               | Researcher/Analyst                    |
| **Archival**     | Not archived separately (removed with SUBPLAN) | Archived by type/topic for reference  |
| **Reuse**        | Informs next SUBPLAN cycle                     | Informs future PLANs and architecture |

---

## 🎯 Categorization Guidelines

### Decision Tree: TASK vs WORK?

```
Start: I need to do execution-level work

1. Is this work connected to a SUBPLAN?
   ├─ YES → Is it implementation of that SUBPLAN?
   │  ├─ YES → EXECUTION_TASK ✅
   │  └─ NO → EXECUTION_WORK (analysis/review) ✅
   └─ NO → EXECUTION_WORK ✅

2. Size constraints:
   ├─ Will it exceed 200 lines?
   │  ├─ YES → EXECUTION_WORK (probably) ✅
   │  └─ NO → Could be EXECUTION_TASK ✅

3. Purpose check:
   ├─ Implementing/delivering deliverables?
   │  ├─ YES → EXECUTION_TASK ✅
   │  └─ NO → EXECUTION_WORK ✅
```

### Ambiguous Cases

| Scenario                              | Categorization                                                      | Reasoning                                      |
| ------------------------------------- | ------------------------------------------------------------------- | ---------------------------------------------- |
| Pre-SUBPLAN analysis to inform design | EXECUTION_WORK (Planning-Strategy ANALYSIS)                         | Informs SUBPLAN design, not implementing it    |
| Review of completed SUBPLAN work      | EXECUTION_WORK (EXECUTION_REVIEW or Implementation-Review ANALYSIS) | Post-completion assessment, not implementation |
| Complex debugging during SUBPLAN      | EXECUTION_TASK (multiple iterations)                                | Directly solving SUBPLAN delivery issue        |
| Post-project lessons learned          | EXECUTION_WORK (CASE_STUDY)                                         | Knowledge capture for future reference         |
| Experimental approach within SUBPLAN  | EXECUTION_TASK (multiple iterations)                                | Part of iterative implementation process       |

---

## 📚 Practical Examples

### Example 1: Entity Resolution Feature

**Scenario**: Implementing entity resolution matching algorithm

**EXECUTION_TASK**:

```
EXECUTION_TASK_ENTITY-RESOLUTION_01_01.md
├── Iteration 1: Baseline algorithm, accuracy 75%
├── Iteration 2: Added fuzzy matching, accuracy 82%
├── Iteration 3: Added embeddings, accuracy 90%
└── Complete: Algorithm meets spec
```

**Related EXECUTION_WORK**:

```
EXECUTION_ANALYSIS_ENTITY-RESOLUTION-PERFORMANCE-REVIEW.md
├── Tests on production data
├── Comparison with alternatives
├── Recommendations for optimization
└── Archived for future reference
```

### Example 2: Performance Investigation

**Scenario**: IDE is slow, need to understand why

**Option A (Analysis-First)**:

```
EXECUTION_ANALYSIS_IDE-PERFORMANCE-DEGRADATION.md
├── Root cause: system memory pressure
├── Not code issue, environmental
├── Recommendations: restart IDE, close apps
└── Archived for troubleshooting reference
```

**Option B (If fix needed)**:

```
SUBPLAN: Fix IDE Performance
└── EXECUTION_TASK_IDE-PERFORMANCE-FIX_01_01.md
    └── Implements optimization (if code change)
```

### Example 3: Protocol Integration

**Scenario**: Adding EXECUTION_ANALYSIS guidance to protocols

**EXECUTION_TASK**:

```
EXECUTION_TASK_PROTOCOL-ENHANCEMENT_01_01.md
├── Iteration 1: Added EXECUTION_ANALYSIS section
├── Iteration 2: Added examples and templates
└── Complete: Protocol updated
```

**Related EXECUTION_WORK**:

```
EXECUTION_ANALYSIS_PROTOCOL-EFFECTIVENESS-REVIEW.md
├── Are users following the guidance?
├── Is it clear and actionable?
├── Suggestions for improvement
```

---

## 🗂️ File Organization Summary

### Active Workspace

```
work-space/
├── execution/
│   ├── EXECUTION_TASK_*.md (active implementations)
│   └── (deleted when SUBPLAN archived)
├── analyses/
│   ├── EXECUTION_ANALYSIS_*.md (active analyses)
│   ├── EXECUTION_CASE-STUDY_*.md
│   └── EXECUTION_OBSERVATION_*.md
├── case-studies/
│   └── EXECUTION_CASE-STUDY_*.md (alt organization)
└── observations/
    └── EXECUTION_OBSERVATION_*.md (alt organization)
```

### Archive

```
documentation/archive/
├── execution-analyses/
│   ├── bug-analysis/
│   │   └── EXECUTION_ANALYSIS_*-BUG.md
│   ├── methodology-review/
│   │   └── EXECUTION_ANALYSIS_*-REVIEW.md
│   ├── implementation-review/
│   ├── process-analysis/
│   └── planning-strategy/
├── case-studies/
│   └── EXECUTION_CASE-STUDY_*.md
└── observations/
    └── EXECUTION_OBSERVATION_*.md
```

---

## 📝 Naming Convention Quick Reference

| Type           | Pattern                                        | Example                                          |
| -------------- | ---------------------------------------------- | ------------------------------------------------ |
| EXECUTION_TASK | `EXECUTION_TASK_<FEATURE>_<SUBPLAN>_<EXEC>.md` | `EXECUTION_TASK_ENTITY-RESOLUTION_01_01.md`      |
| ANALYSIS       | `EXECUTION_ANALYSIS_<TOPIC>.md`                | `EXECUTION_ANALYSIS_METHODOLOGY-REVIEW.md`       |
| CASE_STUDY     | `EXECUTION_CASE-STUDY_<FEATURE>.md`            | `EXECUTION_CASE-STUDY_API-DESIGN.md`             |
| OBSERVATION    | `EXECUTION_OBSERVATION_<TOPIC>_<DATE>.md`      | `EXECUTION_OBSERVATION_PERF-ISSUE_2025-11-09.md` |
| REVIEW         | `EXECUTION_REVIEW_<FEATURE>.md`                | `EXECUTION_REVIEW_IMPLEMENTATION.md`             |
| DEBUG          | `EXECUTION_DEBUG_<ISSUE>.md`                   | `EXECUTION_DEBUG_CIRCULAR-BUG.md`                |

---

## ✅ Checklist for Categorizing Work

- [ ] Is this work connected to a SUBPLAN?
- [ ] Is it implementing/delivering SUBPLAN objectives?
- [ ] Will it exceed 200 lines?
- [ ] Is the goal implementation or knowledge creation?
- [ ] Which type best matches the work?
- [ ] Is the file in the correct location?
- [ ] Does the name follow conventions?
- [ ] Is it templated properly?

---

## 🔗 Related Documentation

- `LLM/templates/EXECUTION_TASK-TEMPLATE.md` - EXECUTION_TASK structure
- `LLM/templates/EXECUTION_ANALYSIS-*-TEMPLATE.md` - ANALYSIS templates (5 types)
- `LLM-METHODOLOGY.md` - Overall execution methodology
- `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` - SUBPLAN workflow (creates EXECUTIONs)

---

## 🎯 QUICK DECISION TREE

**Am I implementing a SUBPLAN achievement?**

```
                    YES → EXECUTION_TASK ✅
                   /     - Follow SUBPLAN approach
                  /      - Track iterations
                 /       - TDD workflow
                /        - <200 lines
               /
Is it SUBPLAN-
connected?
               \
                \      NO → EXECUTION_WORK (standalone knowledge)
                 \    /
                  \  /
                   \/
                   Analysis/Strategy needed?
                   ├─ YES → EXECUTION_ANALYSIS ✅
                   │        - Structured investigation
                   │        - Evidence-based findings
                   │        - 5 subcategories
                   │
                   └─ NO → Type depends on focus
                         ├─ Deep dive + lessons? → EXECUTION_CASE-STUDY ✅
                         ├─ Real-time feedback? → EXECUTION_OBSERVATION ✅
                         ├─ Debugging complex? → EXECUTION_DEBUG ✅
                         └─ Post-completion review? → EXECUTION_REVIEW ✅
```

---

## 📚 WHEN-TO-USE QUICK REFERENCE

### EXECUTION_TASK

- **Use when**: "I'm implementing Achievement 2.3 from SUBPLAN_XX"
- **Indicator**: Work connected to specific SUBPLAN
- **Key traits**: Iteration-based, <200 lines, TDD workflow
- **How to start**: "Create EXECUTION_TASK to log implementation journey"

### EXECUTION_ANALYSIS (EXECUTION_WORK)

- **Use when**: "I need to analyze the GraphRAG pipeline strategy"
- **Indicator**: Standalone analysis/investigation work
- **Key traits**: Evidence-based, structured, 5 subcategories
- **How to start**: "Create EXECUTION*ANALYSIS*<TOPIC>.md"

### EXECUTION_CASE-STUDY (EXECUTION_WORK)

- **Use when**: "I want to document entity resolution refactor learnings"
- **Indicator**: Deep dive with pattern extraction
- **Key traits**: Real example, lessons learned, generalizable insights
- **How to start**: "Create EXECUTION*CASE-STUDY*<FEATURE>.md"

### EXECUTION_OBSERVATION (EXECUTION_WORK)

- **Use when**: "Let's watch GraphRAG execution to get real-time feedback"
- **Indicator**: Real-time discovery during implementation
- **Key traits**: Informal, immediate insights, living document
- **How to start**: "Create EXECUTION*OBSERVATION*<TOPIC>\_<DATE>.md"

### EXECUTION_DEBUG (EXECUTION_WORK)

- **Use when**: "Complex issue - need to investigate systematically"
- **Indicator**: Debugging work that may become ANALYSIS
- **Key traits**: Investigation steps, reproduction, root cause
- **How to start**: "Create EXECUTION*DEBUG*<ISSUE>.md"

---

## 🎯 SCENARIO EXAMPLES (10+ Decision Paths)

### Scenario 1: Implementing New Feature

**Situation**: "I'm building the caching layer described in SUBPLAN_03"

**Decision Path**:

1. Is it SUBPLAN-connected? **YES** ✅
2. Conclusion: **EXECUTION_TASK** ✅

**File**: `EXECUTION_TASK_FEATURE_03_01.md`

---

### Scenario 2: Post-Implementation Analysis

**Situation**: "The caching layer is done. I want to analyze its performance vs alternatives"

**Decision Path**:

1. Is it SUBPLAN-connected? **NO** (post-completion work)
2. Analysis/Strategy? **YES** ✅
3. Conclusion: **EXECUTION_ANALYSIS** (Performance comparison) ✅

**File**: `EXECUTION_ANALYSIS_CACHING-PERFORMANCE-REVIEW.md`

---

### Scenario 3: Documenting Patterns

**Situation**: "Entity resolution refactor is complete. Let me extract learnings and patterns"

**Decision Path**:

1. Is it SUBPLAN-connected? **NO** (documentation after)
2. Type? Deep dive with patterns **YES** ✅
3. Conclusion: **EXECUTION_CASE-STUDY** ✅

**File**: `EXECUTION_CASE-STUDY_ENTITY-RESOLUTION-LEARNINGS.md`

---

### Scenario 4: Real-Time Discovery

**Situation**: "While testing GraphRAG, I'm seeing interesting behaviors - let me capture them"

**Decision Path**:

1. Is it SUBPLAN-connected? **NO** (discovery, not implementation)
2. Type? Real-time observations **YES** ✅
3. Conclusion: **EXECUTION_OBSERVATION** ✅

**File**: `EXECUTION_OBSERVATION_GRAPHRAG-BEHAVIOR_2025-11-09.md`

---

### Scenario 5: Bug Investigation

**Situation**: "Users report intermittent caching failures. Need to investigate"

**Decision Path**:

1. Is it SUBPLAN-connected? **NO** (reactive investigation)
2. Type? Debugging complex issue **YES** ✅
3. Conclusion: **EXECUTION_DEBUG** ✅

**File**: `EXECUTION_DEBUG_CACHING-INTERMITTENT-FAILURES.md`

---

### Scenario 6: Multi-Iteration Implementation

**Situation**: "SUBPLAN_05 has 3 iterations: baseline, optimized, alternative. Should I use one EXECUTION_TASK?"

**Decision Path**:

1. Is it SUBPLAN-connected? **YES** ✅
2. Multiple attempts? **YES** (multiple iterations)
3. Conclusion: **EXECUTION_TASK** (single file, track all iterations) ✅

**File**: `EXECUTION_TASK_OPTIMIZATION_05_01.md` (logs all iterations 1-3)

---

### Scenario 7: Architecture Decision

**Situation**: "Need to decide between 3 database solutions before planning SUBPLAN"

**Decision Path**:

1. Is it SUBPLAN-connected? **NO** (pre-SUBPLAN planning)
2. Analysis/Strategy? **YES** ✅
3. Conclusion: **EXECUTION_ANALYSIS** (Planning-Strategy type) ✅

**File**: `EXECUTION_ANALYSIS_DATABASE-SELECTION-STRATEGY.md`

---

### Scenario 8: Code Review Analysis

**Situation**: "Reviewed new code. Found 5 issues and 3 improvements"

**Decision Path**:

1. Is it SUBPLAN-connected? **Depends**:
   - If SUBPLAN-connected → **EXECUTION_TASK** (issues during implementation)
   - If post-completion → **EXECUTION_ANALYSIS** (Implementation-Review) ✅

**Files**:

- During: `EXECUTION_TASK_FEATURE_01_01.md` (track issues as iterations)
- After: `EXECUTION_ANALYSIS_CODE-REVIEW-FINDINGS.md`

---

### Scenario 9: Quick Investigation

**Situation**: "Why did the prompt generator fail this morning?"

**Decision Path**:

1. Is it SUBPLAN-connected? **NO** (reactive)
2. Type? Debugging investigation **YES** ✅
3. Conclusion: **EXECUTION_DEBUG** (or EXECUTION_ANALYSIS if quick) ✅

**File**: `EXECUTION_DEBUG_PROMPT-GENERATOR-FAILURE_2025-11-09.md`

---

### Scenario 10: Comparative Study

**Situation**: "Compare 3 LLM prompt engineering approaches"

**Decision Path**:

1. Is it SUBPLAN-connected? **NO** (standalone study)
2. Type? Analysis with comparison **YES** ✅
3. Conclusion: **EXECUTION_ANALYSIS** (or CASE-STUDY if extracting patterns) ✅

**File**: `EXECUTION_ANALYSIS_PROMPT-ENGINEERING-COMPARISON.md`

---

### Scenario 11: Live Execution Observation

**Situation**: "Running Entity Resolution in production, want to capture real-time issues"

**Decision Path**:

1. Is it SUBPLAN-connected? **NO** (observation, not implementation)
2. Type? Real-time feedback **YES** ✅
3. Conclusion: **EXECUTION_OBSERVATION** ✅

**File**: `EXECUTION_OBSERVATION_ER-PRODUCTION-BEHAVIOR_2025-11-09.md`

---

### Scenario 12: Refactoring Work (Edge Case)

**Situation**: "SUBPLAN_08 is 'Refactor API responses'. Should I use EXECUTION_TASK?"

**Decision Path**:

1. Is it SUBPLAN-connected? **YES** ✅
2. Implementing refactoring? **YES** ✅
3. Conclusion: **EXECUTION_TASK** ✅
4. Note: Even refactoring is implementation of SUBPLAN

**File**: `EXECUTION_TASK_API-REFACTOR_08_01.md`

---

## 🎓 EDGE CASES & AMBIGUITY RESOLUTION

### Edge Case 1: Analysis During SUBPLAN Execution

**Situation**: "During EXECUTION_TASK, I need to analyze performance impact"

**Resolution**:

- Keep analysis findings in EXECUTION_TASK iteration log
- If extensive (>100 lines), consider separate EXECUTION_ANALYSIS
- Default: Stay in EXECUTION_TASK unless clearly separable

---

### Edge Case 2: Post-SUBPLAN Review

**Situation**: "SUBPLAN complete. Now reviewing quality and learnings"

**Resolution**:

- Type: EXECUTION_ANALYSIS (Implementation-Review) or EXECUTION_CASE-STUDY
- Not EXECUTION_TASK (implementation complete)
- Create new file, don't extend EXECUTION_TASK

---

### Edge Case 3: Unclear Connection to SUBPLAN

**Situation**: "This might be SUBPLAN-connected, or might be standalone"

**Resolution**:

- When in doubt: Treat as EXECUTION_WORK (safer default)
- EXECUTION_ANALYSIS covers most investigation cases
- Can later extract into EXECUTION_TASK if connection found

---

## 📋 QUICK REFERENCE CARD (Printable/Copyable)

```
EXECUTION WORK TYPE SELECTOR

═══════════════════════════════════════════════════════════════════

STEP 1: Is this SUBPLAN-connected implementation?
  YES → EXECUTION_TASK (go to Step 2)
  NO  → EXECUTION_WORK (go to Step 3)

═══════════════════════════════════════════════════════════════════

STEP 2: EXECUTION_TASK Setup
  Type: EXECUTION_TASK_<FEATURE>_<SUBPLAN>_<EXEC>.md
  Location: work-space/execution/
  Size: <200 lines (hard limit)
  Structure: Header → SUBPLAN context → Tests → Iterations → Learnings
  Track: Iterations, learnings, TDD workflow
  ✅ Go create your EXECUTION_TASK

═══════════════════════════════════════════════════════════════════

STEP 3: EXECUTION_WORK Type Selection
  What's your work focus?

  ├─ Investigation/Analysis   → EXECUTION_ANALYSIS
  │  File: EXECUTION_ANALYSIS_<TOPIC>.md
  │  Examples: strategy, bug root cause, review, process
  │
  ├─ Deep Dive + Patterns    → EXECUTION_CASE-STUDY
  │  File: EXECUTION_CASE-STUDY_<FEATURE>.md
  │  Examples: refactor learnings, pattern extraction
  │
  ├─ Real-Time Feedback      → EXECUTION_OBSERVATION
  │  File: EXECUTION_OBSERVATION_<TOPIC>_<DATE>.md
  │  Examples: live execution, real-time discovery
  │
  ├─ Debugging               → EXECUTION_DEBUG
  │  File: EXECUTION_DEBUG_<ISSUE>.md
  │  Examples: complex issue investigation
  │
  └─ Uncertain?              → EXECUTION_ANALYSIS (default)
     File: EXECUTION_ANALYSIS_<TOPIC>.md
     ANALYSIS covers most cases

═══════════════════════════════════════════════════════════════════

QUICK TYPE COMPARISON

| Aspect | EXECUTION_TASK | EXECUTION_ANALYSIS | CASE_STUDY | OBSERVATION |
|--------|---|---|---|---|
| Connected to SUBPLAN | YES | NO | NO | NO |
| Size | <200 lines | 200-1000 | 200-1000 | 100-500 |
| Workflow | Iterations | Investigation | Deep dive | Real-time |
| Location | work-space/execution/ | work-space/analyses/ | case-studies/ | observations/ |
| When to use | Implementing | Analyzing | Learning | Capturing |

═══════════════════════════════════════════════════════════════════

STILL UNSURE? Ask:
1. Am I implementing a SUBPLAN? YES→ EXECUTION_TASK
2. Am I investigating? YES → EXECUTION_ANALYSIS
3. Am I documenting patterns? YES → EXECUTION_CASE-STUDY
4. Am I capturing real-time? YES → EXECUTION_OBSERVATION
5. None? → EXECUTION_ANALYSIS (safest default)
```

---

**Version**: 1.0 (Enhanced with Decision Framework)  
**Status**: ✅ Complete with Decision Support  
**Last Updated**: 2025-11-09
