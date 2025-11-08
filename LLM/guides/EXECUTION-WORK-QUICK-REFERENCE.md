# Execution Work Quick Reference

**Purpose**: Instant type selection for execution-level work  
**Format**: One-page printable reference  
**Status**: Active

---

## 🎯 QUICK DECISION TREE

```
IS THIS WORK SUBPLAN-CONNECTED?
(Are you implementing a specific SUBPLAN achievement?)

                YES ──→ EXECUTION_TASK ✅
               /       • Implementation-focused
              /        • Iteration tracking (TDD)
             /         • <200 lines
            /          • Filename: EXECUTION_TASK_<FEATURE>_<SUBPLAN>_<EXEC>.md
           /           • Location: work-space/execution/ (or PLAN folder)
          /
    IS IT
   SUBPLAN-
  CONNECTED?
          \
           \         NO ──→ What kind of knowledge work?
            \       /
             \     /
              \   /
               \ /
                ├─ Structured investigation?    ──→ EXECUTION_ANALYSIS ✅
                │  (root cause, review, strategy)   Filename: EXECUTION_ANALYSIS_<TOPIC>.md
                │                                     Location: work-space/analyses/
                │
                ├─ Deep dive + patterns?        ──→ EXECUTION_CASE-STUDY ✅
                │  (lessons, learnings)              Filename: EXECUTION_CASE-STUDY_<FEATURE>.md
                │                                     Location: work-space/case-studies/
                │
                ├─ Real-time feedback?          ──→ EXECUTION_OBSERVATION ✅
                │  (live discovery)                   Filename: EXECUTION_OBSERVATION_<TOPIC>_<DATE>.md
                │                                     Location: work-space/observations/
                │
                ├─ Complex debugging?           ──→ EXECUTION_DEBUG ✅
                │  (investigation steps)              Filename: EXECUTION_DEBUG_<ISSUE>.md
                │                                     Location: work-space/debug-logs/
                │
                └─ Post-review?                 ──→ EXECUTION_REVIEW ✅
                   (quality assessment)              Filename: EXECUTION_REVIEW_<FEATURE>.md
                                                      Location: work-space/reviews/
```

---

## 📊 TYPE COMPARISON TABLE

| **Aspect**             | **EXECUTION_TASK**      | **ANALYSIS**           | **CASE-STUDY**             | **OBSERVATION**            | **DEBUG**                | **REVIEW**            |
| ---------------------- | ----------------------- | ---------------------- | -------------------------- | -------------------------- | ------------------------ | --------------------- |
| **SUBPLAN-Connected?** | ✅ YES                  | ❌ NO                  | ❌ NO                      | ❌ NO                      | ❌ NO                    | ❌ NO                 |
| **Size**               | <200 lines              | 200-1000               | 200-1000                   | 100-500                    | 200-800                  | 200-600               |
| **Workflow**           | Iterations              | Investigation          | Deep dive                  | Real-time                  | Debugging                | Assessment            |
| **Purpose**            | Implement               | Understand             | Learn                      | Capture                    | Fix                      | Evaluate              |
| **Test-Driven?**       | ✅ YES (TDD)            | ❌ Verification        | ❌ Review                  | ❌ Informal                | ✅ Reproduce             | ❌ Checklist          |
| **Location**           | `work-space/execution/` | `work-space/analyses/` | `work-space/case-studies/` | `work-space/observations/` | `work-space/debug-logs/` | `work-space/reviews/` |

---

## 🎯 WHEN-TO-USE QUICK GUIDE

### ✅ Use EXECUTION_TASK When:

- "I'm implementing Achievement 2.3 from SUBPLAN_05"
- You have a specific SUBPLAN to execute
- Goal is delivering implementation/deliverables
- Work will have multiple iterations

### ✅ Use EXECUTION_ANALYSIS When:

- "I need to analyze the database strategy before designing SUBPLAN"
- Structured investigation of problem or decision needed
- Evidence-based findings and recommendations
- Examples: root cause analysis, methodology review, planning strategy

### ✅ Use EXECUTION_CASE-STUDY When:

- "I want to document entity resolution refactor learnings"
- Deep dive into a feature with pattern extraction
- Goal is capturing lessons for future reference
- Real example from codebase with generalizable insights

### ✅ Use EXECUTION_OBSERVATION When:

- "Let's watch GraphRAG execution live and capture feedback"
- Real-time discovery and immediate insights
- Informal, might evolve into ANALYSIS later
- Living document capturing things as discovered

### ✅ Use EXECUTION_DEBUG When:

- "Users report intermittent caching failures - need investigation"
- Complex issue requiring systematic debugging
- Reproduction steps, root cause, solution
- May become BUG-ANALYSIS later

### ✅ Use EXECUTION_REVIEW When:

- "SUBPLAN work complete - now reviewing quality"
- Post-completion assessment of implementation
- Verify requirements, identify gaps
- May trigger new SUBPLANs for improvements

---

## 📋 QUICK EXAMPLES (8 Common Scenarios)

### Example 1: Feature Implementation

**Scenario**: "Building the caching layer described in SUBPLAN_03"  
**Decision**: **EXECUTION_TASK** ✅  
**Why**: SUBPLAN-connected implementation

### Example 2: Strategy Analysis

**Scenario**: "Need to decide between 3 database solutions before planning SUBPLAN"  
**Decision**: **EXECUTION_ANALYSIS** ✅  
**Why**: Pre-SUBPLAN investigation (Planning-Strategy type)

### Example 3: Post-Implementation Learning

**Scenario**: "Entity resolution refactor is done. Extract learnings and patterns"  
**Decision**: **EXECUTION_CASE-STUDY** ✅  
**Why**: Deep dive after completion with pattern extraction

### Example 4: Real-Time Discovery

**Scenario**: "While testing GraphRAG, seeing interesting behaviors - capture them"  
**Decision**: **EXECUTION_OBSERVATION** ✅  
**Why**: Real-time feedback during work (not SUBPLAN-connected)

### Example 5: Bug Investigation

**Scenario**: "Why did the prompt generator fail this morning?"  
**Decision**: **EXECUTION_DEBUG** ✅  
**Why**: Reactive investigation into complex issue

### Example 6: Multi-Iteration SUBPLAN Work

**Scenario**: "SUBPLAN_05 has 3 approaches to test"  
**Decision**: **EXECUTION_TASK** (track all iterations) ✅  
**Why**: All iterations go in one EXECUTION_TASK file

### Example 7: Code Quality Review

**Scenario**: "Reviewed new code. Found 5 issues and suggestions"  
**Decision**: **EXECUTION_ANALYSIS** (Implementation-Review) ✅  
**Why**: Post-completion assessment (if SUBPLAN done) or EXECUTION_TASK iteration (if still implementing)

### Example 8: Architecture Decision

**Scenario**: "Comparing 3 LLM prompt engineering approaches"  
**Decision**: **EXECUTION_ANALYSIS** ✅  
**Why**: Standalone investigation informing future decisions

---

## 🗂️ FILE LOCATION QUICK MAP

**Active Work** (current workspace):

- `work-space/execution/` → EXECUTION_TASK files
- `work-space/analyses/` → EXECUTION_ANALYSIS files
- `work-space/case-studies/` → EXECUTION_CASE-STUDY files
- `work-space/observations/` → EXECUTION_OBSERVATION files
- `work-space/debug-logs/` → EXECUTION_DEBUG files
- `work-space/reviews/` → EXECUTION_REVIEW files

**Archived** (for reference):

- `documentation/archive/execution-analyses/` → Archived ANALYSIS files
- `documentation/archive/case-studies/` → Archived CASE-STUDY files
- `documentation/archive/observations/` → Archived OBSERVATION files

---

## ✅ DECISION CHECKLIST

Before creating a new execution file, confirm:

- [ ] Is this SUBPLAN-connected? → YES = EXECUTION_TASK | NO = EXECUTION_WORK
- [ ] Am I investigating/analyzing? → YES = EXECUTION_ANALYSIS
- [ ] Am I documenting patterns? → YES = EXECUTION_CASE-STUDY
- [ ] Am I capturing real-time? → YES = EXECUTION_OBSERVATION
- [ ] Am I debugging complex issue? → YES = EXECUTION_DEBUG
- [ ] Am I reviewing post-completion? → YES = EXECUTION_REVIEW
- [ ] Do I have the correct file name? → Check naming convention above
- [ ] Is it in the right location? → Check location map above
- [ ] Does it follow the template? → Use LLM/templates/EXECUTION\_\*-TEMPLATE.md

---

## 🔗 RELATED RESOURCES

**For More Details**:

- 📖 Full Taxonomy: `LLM/guides/EXECUTION-TAXONOMY.md` (comprehensive, 779 lines)
- 📋 Methodology: `LLM-METHODOLOGY.md` (overall execution framework)
- 📝 Templates: `LLM/templates/EXECUTION_*-TEMPLATE.md` (specific file templates)

**Quick Decision Flowchart**: Use the QUICK DECISION TREE at top of this page

---

**Print This**: This guide is designed to fit one page when printed - keep as reference card at your desk!

**Last Updated**: 2025-11-09  
**Status**: Active & Ready for Use
