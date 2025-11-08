# Mini-Protocol: CREATE_SUBPLAN

**Purpose**: Focused guide for SUBPLAN creation during the Designer phase  
**Status**: Active  
**Created**: November 9, 2025

---

## 🎯 What This Is

This mini-protocol guides the **Designer Agent** through SUBPLAN creation - the design and coordination phase where you plan HOW to execute an achievement and WHO will execute it (single Executor or multiple parallel Executors).

**Not for**: Execution (use CREATE_EXECUTION.md for that)

---

## 📋 When to Use This

**Use this protocol when**:

- You have a PLAN and selected an achievement to work on
- You're ready to design your approach (Designer phase)
- You need to plan if work will be single execution or multiple (potentially parallel)
- You want to coordinate multiple Executor agents

**Before using this**:

1. Read the PLAN achievement section
2. Understand the requirements
3. Read `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` for the 4-phase workflow

---

## 🔄 SUBPLAN Creation Workflow (Phase 1 of 4)

**The 4-Phase SUBPLAN Independent Workflow**:

```
Phase 1: DESIGN (Designer Agent) ← You are here
  └─ Create SUBPLAN
  └─ Plan approach and executions
  └─ Design execution strategy
  └─ Plan multiple EXECUTIONs if needed

Phase 2: EXECUTION PLANNING (Designer Agent)
  └─ Decide execution count
  └─ Plan parallelization
  └─ Create EXECUTION_TASK file(s)

Phase 3: EXECUTION (Executor Agents)
  └─ Execute according to SUBPLAN plan
  └─ Multiple Executors if parallel work

Phase 4: SYNTHESIS (Designer Agent)
  └─ Review all EXECUTION results
  └─ Synthesize learnings
  └─ Mark SUBPLAN complete
```

**This protocol covers Phase 1 only.**

---

## ✅ SUBPLAN Creation Checklist

### Step 1: Prepare

- [ ] Read PLAN achievement section (that's all you need from the PLAN)
- [ ] Understand what needs to be achieved
- [ ] Identify key deliverables
- [ ] Note any constraints or dependencies

### Step 2: Design Your Approach

**Ask yourself**:

- How will I tackle this achievement?
- What's my strategy?
- What are the key steps?
- What will be created/modified?
- Are there multiple independent paths I could take?

**Document**:

- Create file: `SUBPLAN_<FEATURE>_<NEXT-NUMBER>.md`
- Location: `work-space/subplans/`
- Write approach section with clear strategy
- List exact deliverables

### Step 3: Decide Execution Strategy

**Single or Multiple EXECUTIONs?**

```
Decision Tree:

Is this straightforward, linear work?
  YES → Single EXECUTION
  NO ↓

Could parts be independent?
  No → Single EXECUTION
  Yes ↓

Should we run them in parallel or sequential?
  Parallel (independent) → Multiple EXECUTIONs [PARALLEL]
  Sequential (dependent) → Multiple EXECUTIONs [SEQUENTIAL]
  A/B testing → Multiple EXECUTIONs [EXPERIMENTAL]
```

**Document in SUBPLAN**:

```markdown
## 🔄 Execution Strategy

- Execution Count: Single / Multiple
- Parallelization: Yes / No
- Rationale: [Why this approach]

## 🔀 Planned Executions (If Multiple)

- EXECUTION_TASK_XX_01: [Purpose] [PARALLEL/SEQUENTIAL] [time]
- EXECUTION_TASK_XX_02: [Purpose] [PARALLEL/SEQUENTIAL] [time]
- Coordination: [How results compare]
```

### Step 4: Plan Multiple EXECUTIONs (If Applicable)

**When you have multiple executions**:

1. **Define each execution's focus**:

   - What specific aspect does this EXECUTION handle?
   - How is it independent from others (if parallel)?
   - What does success look like for this EXECUTION?

2. **Define coordination**:

   - If parallel: How will you compare results?
   - If sequential: How does one feed into the next?
   - Synthesis strategy: How to combine learnings?

3. **Plan parallelization**:
   - If parallel: Can Executors work simultaneously?
   - If sequential: Any blocked dependencies?
   - Total time: single execution time × count (if sequential) or max (if parallel)?

### Step 5: Complete SUBPLAN Template

**Use**: `LLM/templates/SUBPLAN-TEMPLATE.md`

**Required Sections**:

- [ ] **Header**: SUBPLAN metadata (mother plan, achievement, status)
- [ ] **Objective** (1 paragraph): What this SUBPLAN achieves
- [ ] **Deliverables**: Exact files/functions to create/modify
- [ ] **Approach**: Your strategy and key steps
- [ ] **Execution Strategy**: Single/Multiple with rationale
- [ ] **Planned Executions** (if multiple): Table with all executions
- [ ] **Expected Results**: Outcomes, success indicators
- [ ] **Test Requirements** (if code work)

**Size**: 200-600 lines

### Step 6: Verify SUBPLAN Quality

**Checklist**:

- [ ] Could an Executor read just the objective and approach and execute well?
- [ ] Is execution strategy clear?
- [ ] Are deliverables specific and verifiable?
- [ ] Are multiple EXECUTIONs (if applicable) well-defined?
- [ ] Is size 200-600 lines?

### Step 7: Don't Execute Yet

**Critical**: SUBPLAN is complete when:

- [ ] Design is thorough
- [ ] Execution strategy is clear
- [ ] Deliverables are specified
- [ ] Multiple EXECUTIONs (if any) are planned

**Next**: Create EXECUTION_TASK(s) for Phase 2 (Execution Planning) → Use `LLM/protocols/CREATE_EXECUTION.md`

---

## 🎓 Special Cases

### Case 1: Single Sequential EXECUTION

**Simplest case**: Most achievements have one EXECUTION

```markdown
## 🔄 Execution Strategy

- Execution Count: Single
- Parallelization: No
- Rationale: Linear work with clear dependencies
```

### Case 2: Parallel Experimentation

**Multiple parallel approaches**: A/B testing, comparison

```markdown
## 🔄 Execution Strategy

- Execution Count: Multiple (3)
- Parallelization: Yes (independent approaches)
- Rationale: Testing 3 different strategies to see which works best

## 🔀 Planned Executions

| Execution | Purpose                           | Type     | Time | Depends On |
| --------- | --------------------------------- | -------- | ---- | ---------- |
| 01        | Approach A: Current best practice | PARALLEL | 2h   | -          |
| 02        | Approach B: New experimental      | PARALLEL | 2h   | -          |
| 03        | Approach C: Optimized hybrid      | PARALLEL | 2h   | -          |

Coordination Strategy:

- All run in parallel (independent)
- Results compared in SUBPLAN synthesis
- Best approach selected for production
```

### Case 3: Sequential Iterations

**Multiple sequential executions**: Iterative refinement

```markdown
## 🔄 Execution Strategy

- Execution Count: Multiple (3+, possibly more)
- Parallelization: No (sequential refinement)
- Rationale: Iterative approach - each execution learns from previous

## 🔀 Planned Executions

| Execution | Purpose                                 | Type       | Time | Depends On  |
| --------- | --------------------------------------- | ---------- | ---- | ----------- |
| 01        | Initial implementation                  | SEQUENTIAL | 3h   | -           |
| 02        | First refinement based on iteration 01  | SEQUENTIAL | 2h   | 01 complete |
| 03        | Second refinement based on iteration 02 | SEQUENTIAL | 1.5h | 02 complete |

Coordination Strategy:

- Sequential: Each execution learns from previous
- Designer synthesizes learnings after each EXECUTION
- Stop when success criteria met
```

---

## 🚫 Common Mistakes to Avoid

**❌ Don't**:

- Start execution before SUBPLAN is complete ("Let me start coding while thinking")
- Plan single EXECUTION when multiple would be beneficial
- Make SUBPLAN too prescriptive (Executor needs room to figure out details)
- Forget to specify deliverables clearly
- Make SUBPLAN too vague (Executor won't know what success looks like)

**✅ Do**:

- Complete design phase before execution
- Think critically about parallelization opportunities
- Provide clear but not overly prescriptive approach
- Specify exact deliverables and success criteria
- Plan for multiple EXECUTIONs when work is naturally parallel

---

## 🔗 Related Documents

**Before Creating SUBPLAN**:

- `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` - Complete workflow guide with examples
- `LLM-METHODOLOGY.md` - Full methodology reference

**For SUBPLAN Template**:

- `LLM/templates/SUBPLAN-TEMPLATE.md` - Use this template

**For EXECUTION Phase**:

- `LLM/protocols/CREATE_EXECUTION.md` - Phase 2: Create EXECUTION_TASK
- `LLM/protocols/IMPLEMENTATION_START_POINT.md` - Full start point guide

**For Completion**:

- `LLM/protocols/IMPLEMENTATION_END_POINT.md` - Archive and complete

---

## ⏱️ Timing

**Designer Phase (SUBPLAN Creation)**: 30 minutes to 2 hours

- Light SUBPLANs (straightforward work): 30m-1h
- Medium SUBPLANs (some complexity): 1-1.5h
- Heavy SUBPLANs (multiple parallel executions): 1.5-2h

**Not included in this time**: The actual execution (that's EXECUTION phase)

---

**Next Step**: After SUBPLAN is complete, use `LLM/protocols/CREATE_EXECUTION.md` for Phase 2 (Execution Planning) to create EXECUTION_TASK file(s).
