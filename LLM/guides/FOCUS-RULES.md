# Focus Rules Guide

**Purpose**: Define explicit rules for LLM context focus based on hierarchy level  
**Status**: Active Guide  
**Created**: 2025-11-07  
**Version**: 1.0

---

## 🎯 Problem

LLMs can easily read too much context, looking up the tree (PLAN → SUBPLAN → EXECUTION_TASK) or reading unrelated sections. This causes:

- Context overload and session freezing
- Slower execution (reading unnecessary information)
- Scope creep (working on wrong level)
- Confusion about what to focus on

**Solution**: Explicit focus rules for each hierarchy level.

---

## 📐 The Four-Tier Hierarchy

```
GRAMMAPLAN (orchestration)
  └── PLAN (what to achieve)
      └── SUBPLAN (how to achieve)
          └── EXECUTION_TASK (execution log)
```

**Key Principle**: Focus **exclusively** on the **lowest open component**. Don't look up the tree until work is complete.

---

## 🔍 Focus Rules by Level

### Level 1: EXECUTION_TASK (Smallest Unit)

**When**: Working on an active EXECUTION_TASK

**✅ READ ONLY**:

- This EXECUTION_TASK file (complete file)
- Immediate parent SUBPLAN objective (1-2 sentences only)
- Code files being modified (if code work)

**❌ DO NOT READ**:

- Parent SUBPLAN full content
- Parent PLAN (except current achievement section)
- Other EXECUTION_TASKs
- Completed work
- Other achievements

**Context Budget**: ~200 lines (EXECUTION_TASK size limit)

**Why**: EXECUTION_TASK is the smallest unit of focus. Reading parent documents adds unnecessary context and slows execution.

**Example**:

```
✅ CORRECT:
- Read: EXECUTION_TASK_METHODOLOGY-V2-ENHANCEMENTS_21_01.md (76 lines)
- Read: SUBPLAN objective: "Document focus rules" (2 lines)
- Total: 78 lines

❌ WRONG:
- Read: Full SUBPLAN (200 lines)
- Read: Full PLAN (773 lines)
- Read: Other EXECUTION_TASKs (300 lines)
- Total: 1,273 lines (16x more!)
```

---

### Level 2: SUBPLAN (Implementation Approach)

**When**: Creating or working on a SUBPLAN

**✅ READ ONLY**:

- This SUBPLAN file (complete file)
- Parent PLAN current achievement section (50-100 lines)
- Active EXECUTION_TASKs (if any exist)
- Parent PLAN "Current Status & Handoff" section (30-50 lines)

**❌ DO NOT READ**:

- Parent PLAN full content
- Other achievements in PLAN
- Other SUBPLANs
- Completed EXECUTION_TASKs (unless needed for context)
- Completed work

**Context Budget**: ~400 lines

**Why**: SUBPLAN defines HOW to achieve one achievement. Reading other achievements or full PLAN adds scope and confusion.

**Example**:

```
✅ CORRECT:
- Read: SUBPLAN_METHODOLOGY-V2-ENHANCEMENTS_21.md (200 lines)
- Read: PLAN Achievement 2.1 section (19 lines)
- Read: PLAN Current Status (47 lines)
- Total: 266 lines

❌ WRONG:
- Read: Full PLAN (773 lines)
- Read: All SUBPLANs (800 lines)
- Total: 1,573 lines (6x more!)
```

---

### Level 3: PLAN (What to Achieve)

**When**: Creating PLAN or working on next achievement

**✅ READ ONLY**:

- Current achievement section (50-100 lines)
- "Current Status & Handoff" section (30-50 lines)
- Active SUBPLANs (if any exist)
- Summary statistics (for metrics)

**❌ DO NOT READ**:

- Other achievements (unless reviewing)
- Completed achievements
- Full SUBPLAN content (unless creating one)
- Full EXECUTION_TASK content (unless creating one)
- Achievement Addition Log (unless adding achievement)

**Context Budget**: ~200 lines (per achievement)

**Why**: PLAN defines WHAT to achieve. Reading all achievements at once causes context overload. Focus on current achievement only.

**Example**:

```
✅ CORRECT:
- Read: PLAN Achievement 2.1 section (19 lines)
- Read: PLAN Current Status (47 lines)
- Total: 66 lines

❌ WRONG:
- Read: Full PLAN (773 lines)
- Read: All achievements (500 lines)
- Total: 1,273 lines (19x more!)
```

---

### Level 4: GrammaPlan (Orchestration)

**When**: Working on GrammaPlan or coordinating child PLANs

**✅ READ ONLY**:

- GrammaPlan file (200-300 lines)
- Active child PLAN status (from ACTIVE_PLANS.md)
- Child PLAN "Current Status" sections (if coordinating)

**❌ DO NOT READ**:

- Child PLAN full content
- Child SUBPLANs
- Child EXECUTION_TASKs
- Implementation details

**Context Budget**: ~500 lines

**Why**: GrammaPlan coordinates strategy, not implementation. Reading child PLAN details adds unnecessary context.

**Example**:

```
✅ CORRECT:
- Read: GRAMMAPLAN_LLM-METHODOLOGY-V2.md (200 lines)
- Read: ACTIVE_PLANS.md child status (50 lines)
- Total: 250 lines

❌ WRONG:
- Read: All 6 child PLANs (4,500 lines)
- Read: All child SUBPLANs (2,000 lines)
- Total: 6,750 lines (27x more!)
```

---

## 🎯 Decision Trees

### "What Should I Read?" - Quick Decision

**Question 1**: What am I working on?

- **EXECUTION_TASK** → Read EXECUTION_TASK only (Level 1 rules)
- **SUBPLAN** → Read SUBPLAN + current achievement (Level 2 rules)
- **PLAN achievement** → Read achievement + status (Level 3 rules)
- **GrammaPlan** → Read GrammaPlan + child status (Level 4 rules)

**Question 2**: Do I need parent context?

- **Yes** → Read parent objective only (1-2 sentences)
- **No** → Don't read parent

**Question 3**: Do I need sibling context?

- **Yes** → Read only if blocking (dependency)
- **No** → Don't read siblings

**Result**: Follow rules for your level, read minimum needed.

---

## ⚠️ Anti-Patterns

### Anti-Pattern 1: Reading Up the Tree

**Wrong**:

```
Working on EXECUTION_TASK
→ Read full SUBPLAN (200 lines)
→ Read full PLAN (773 lines)
→ Read related PLANs (1,000 lines)
Total: 1,973 lines
```

**Right**:

```
Working on EXECUTION_TASK
→ Read EXECUTION_TASK only (76 lines)
→ Read SUBPLAN objective (2 lines)
Total: 78 lines
```

### Anti-Pattern 2: Reading Completed Work

**Wrong**:

```
Working on Achievement 2.1
→ Read Achievement 0.1 (completed)
→ Read Achievement 0.2 (completed)
→ Read Achievement 1.1 (completed)
→ Read Achievement 1.2 (completed)
Total: 200+ lines of completed work
```

**Right**:

```
Working on Achievement 2.1
→ Read Achievement 2.1 only (19 lines)
→ Read Current Status (47 lines)
Total: 66 lines
```

### Anti-Pattern 3: Reading Siblings

**Wrong**:

```
Working on SUBPLAN_21
→ Read SUBPLAN_01 (completed)
→ Read SUBPLAN_02 (completed)
→ Read SUBPLAN_11 (completed)
→ Read SUBPLAN_12 (completed)
Total: 800 lines of other SUBPLANs
```

**Right**:

```
Working on SUBPLAN_21
→ Read SUBPLAN_21 only (200 lines)
→ Read PLAN Achievement 2.1 (19 lines)
Total: 219 lines
```

---

## 📊 Context Savings

**Without Focus Rules**:

- EXECUTION_TASK work: 1,273 lines
- SUBPLAN work: 1,573 lines
- PLAN work: 1,273 lines
- **Average**: 1,373 lines per session

**With Focus Rules**:

- EXECUTION_TASK work: 78 lines
- SUBPLAN work: 266 lines
- PLAN work: 66 lines
- **Average**: 137 lines per session

**Savings**: **90% reduction in context requirements!**

---

## ✅ Best Practices

### Practice 1: Start at Lowest Level

**Always start** by identifying the lowest open component:

1. Is there an active EXECUTION_TASK? → Focus on it
2. Is there an active SUBPLAN? → Focus on it
3. Is there a current achievement? → Focus on it

### Practice 2: Read Parent Objective Only

**When you need parent context**:

- Read parent objective (1-2 sentences)
- Don't read full parent document
- Example: "SUBPLAN objective: Document focus rules" (2 lines)

### Practice 3: Don't Read Completed Work

**Completed work is archived**:

- Don't read completed EXECUTION_TASKs
- Don't read completed SUBPLANs
- Don't read completed achievements
- If needed: Read archive INDEX.md (summary)

### Practice 4: Use "What to Read" Sections

**Templates have "What to Read" sections**:

- Check template for your level
- Follow the guidance
- Don't read beyond what's listed

---

## 🔗 Integration

**Templates Updated**:

- PLAN-TEMPLATE.md: "What to Read" section
- SUBPLAN-TEMPLATE.md: "What to Read" section
- EXECUTION_TASK-TEMPLATE.md: "What to Read" section

**Protocols Updated**:

- IMPLEMENTATION_START_POINT.md: References focus rules
- IMPLEMENTATION_RESUME.md: References focus rules

**Validation**:

- Size limit scripts enforce document sizes
- Focus rules prevent reading beyond limits

---

## 📝 Summary

**Key Principle**: Focus exclusively on the lowest open component.

**Rules**:

- **EXECUTION_TASK**: Read EXECUTION_TASK only (~200 lines)
- **SUBPLAN**: Read SUBPLAN + current achievement (~400 lines)
- **PLAN**: Read current achievement + status (~200 lines)
- **GrammaPlan**: Read GrammaPlan + child status (~500 lines)

**Result**: 90% reduction in context requirements, no session freezing!

---

**Status**: Active Guide  
**Version**: 1.0 (November 2025)  
**Maintained By**: PLAN_METHODOLOGY-V2-ENHANCEMENTS.md
