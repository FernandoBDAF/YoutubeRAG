# Methodology Evolution v2.0: Five-Tier Hierarchy & Independent SUBPLAN Workflow

**Date**: November 9, 2025  
**Status**: 🚀 Production Release  
**Version**: 2.0  
**Evolution From**: v1.0 (Four-Tier with Monolithic Automation)

---

## 🎯 What Changed: The Big Picture

The LLM development methodology evolved from a four-tier hierarchy with monolithic automation to a **five-tier hierarchy with independent SUBPLAN workflow and modular automation**. This evolution enables true multi-agent coordination, strategic documentation, and context-appropriate information flow.

---

## 📊 Hierarchy Evolution

### v1.0 Hierarchy (Previous)
```
GRAMMAPLAN (strategic coordination)
  ↓
PLAN (tactical execution)
  ↓
SUBPLAN (approach)
  ↓
EXECUTION_TASK (journey)
```

**Problem**: No formal strategic layer, PLANs conflated with SUBPLAN execution context

### v2.0 Hierarchy (Current)
```
⭐ NORTH_STAR (strategic vision - illuminates all work)
       ├─→ 📋 GRAMMAPLAN (strategic coordination)
       │       └─→ 📄 PLAN (tactical execution)
       │
       └─→ 📄 PLAN (independent tactical execution)
               └─→ 📝 SUBPLAN (design + execution coordination)
                       └─→ ✅ EXECUTION_TASK (implementation)
```

**Improvement**: Dedicated strategic layer, independent workflow phases, clearer role separation

---

## 📈 Key Size Limit Changes

| Document Type | v1.0 Limit | v2.0 Limit | Reason |
|---------------|-----------|-----------|--------|
| NORTH_STAR | N/A (didn't exist) | 800-2,000 | Strategic docs need space for comprehensive vision |
| GRAMMAPLAN | 800 lines | 600-1,500 | Increased capacity for larger coordination scopes |
| PLAN | 600 lines | 300-900 | Increased because PLAN no longer in execution context |
| SUBPLAN | 200-400 | 200-600 | Increased for better execution coordination |
| EXECUTION_TASK | <200 lines | <200 lines | Unchanged (maintains Executor focus) |

---

## 🔄 Workflow Evolution: SUBPLAN Independence

### v1.0 Workflow (Linear)
```
1. Create SUBPLAN
2. Immediately create EXECUTION_TASK
3. Execute work
4. Archive both together
```

**Problem**: Designer and Executor roles merged; no support for parallel execution; limited exploration

### v2.0 Workflow (4-Phase with Independence)
```
Phase 1: DESIGN (Designer)
  → Analyze requirements → Design approach → Plan executions

Phase 2: EXECUTION PLANNING (Designer)
  → Create EXECUTION_TASK file(s) → Plan parallelization

Phase 3: EXECUTION (Executor Agent)
  → Execute according to Designer's plan (minimal context reading)
  → May run in parallel with other Executors

Phase 4: SYNTHESIS (Designer)
  → Review all EXECUTION results → Synthesize learnings
```

**Improvement**: Separate roles, parallel execution capability, better context management

---

## 🤖 Automation Modernization

### v1.0 Automation
- Single `generate_prompt.py` for all workflows
- Monolithic: Did everything

### v2.0 Automation
- **`generate_prompt.py`** (orchestrator) - Detects workflow state, recommends next step
- **`generate_subplan_prompt.py`** (new) - Creates Designer-phase prompts
- **`generate_execution_prompt.py`** (new) - Creates Executor-phase prompts with minimal context
- **Validation scripts** (updated):
  - `check_north_star_size.py` (new)
  - `check_grammaplan_size.py` (updated)
  - `check_plan_size.py` (updated)
  - `validate_subplan_executions.py` (new)

**Improvement**: Modular, role-aware, context-appropriate prompt generation

---

## 💾 Folder Structure v2.0

```
work-space/
├── north-stars/           # ⭐ NORTH_STAR documents (800-2,000 lines)
├── grammaplans/          # 📋 GRAMMAPLAN documents (600-1,500 lines)
├── plans/                # 📄 PLAN documents (300-900 lines)
├── subplans/             # 📝 SUBPLAN documents (200-600 lines)
└── execution/            # ✅ EXECUTION_TASK documents (<200 lines)

LLM/
├── protocols/            # Updated with CREATE_SUBPLAN.md, CREATE_EXECUTION.md
├── templates/            # NORTH_STAR-TEMPLATE, updated others
├── guides/               # New: NORTH-STAR-GUIDE, SUBPLAN-WORKFLOW-GUIDE
├── scripts/              # New modular prompt generators
└── index/                # Enhanced FILE-INDEX.md
```

---

## 📚 Why These Changes?

### Strategic Document Layer (NORTH_STAR)
**Need**: Methodology was growing complex, needed guidance without cluttering tactical layer

**Evidence**: 
- Multiple documents >1,000 lines with strategic intent
- PLANs needed more space for tactical detail
- No formal way to capture strategic vision

**Solution**: NORTH_STAR documents (800-2,000 lines) provide strategic light that "floats above funnel, illuminating it"

### Larger PLANs (900 lines vs. 600)
**Need**: Medium projects naturally grew to 700-900 lines; artificial limit forced premature GrammaPlan conversion

**Evidence**:
- PLANs for 15-20 achievements frequently exceeded 600 lines
- Most exceeding documents didn't need GrammaPlan coordination
- GrammaPlan threshold (>600 lines) was too low

**Solution**: Increase PLAN limit to 900 lines; raise GrammaPlan criteria to >900 lines

**Why it works**: With SUBPLAN independent workflow, PLAN only provides context for SUBPLAN creation (Planner reads), not execution (Executor reads SUBPLAN objective only). This context separation allows larger PLANs without bloating execution context.

### Independent SUBPLAN Workflow
**Need**: Designer and Executor conflated; parallel execution impossible; limited exploration

**Evidence**:
- Many achievements benefit from parallel approaches (A/B testing, parallel refinement)
- Designer needs thinking time without rushing to execution
- Executor needs minimal context to stay focused

**Solution**: 4-phase workflow with explicit role separation

**Why it works**: Allows Designer to explore multiple strategies, Executor to focus intently, and parallel execution when work is independent

---

## 🔄 Migration Guide for Old Documents

### For Existing PLAN Documents

**Option 1: Keep as PLAN** (if <900 lines and not strategic)
- No changes needed
- Works with new workflow immediately
- SUBPLAN creation now supports multiple executions

**Option 2: Convert to NORTH_STAR** (if >900 lines with strategic intent)
- Rename: `PLAN_XXX.md` → `NORTH_STAR_XXX.md`
- Move to: `work-space/north-stars/`
- Update references in `ACTIVE_PLANS.md`
- Now illuminates related PLANs/GrammaPlans

**Option 3: Expand PLAN** (if 700-900 lines, strategic focus)
- Keep as PLAN (now allowed with 900-line limit)
- Focus on achievement definition, not execution details
- Add cross-references to supporting guides

### For Existing SUBPLAN Documents

**Workflow Update Only**
- No name/structure changes needed
- New features available:
  - Execution Strategy section
  - Multiple EXECUTIONs support
  - Planned Executions table
  - Execution Results Synthesis section
- Old single-execution SUBPLANs continue to work

### For Existing EXECUTION_TASK Documents

**Minimal Changes**
- Continue using as-is (no structural changes)
- New features available:
  - Read SUBPLAN objective + approach only (minimal context)
  - Can be part of parallel execution group
  - Parallelization context section available
- Size limit unchanged (<200 lines)

---

## 📖 How to Use v2.0 Effectively

### For Strategic Work (NORTH_STAR)
1. Create NORTH_STAR (800-2,000 lines) for strategic vision
2. Reference from related GrammaPlans/PLANs
3. Update periodically as strategy evolves
4. Use as guiding light for tactical work

### For Coordination Work (GRAMMAPLAN)
1. GRAMMAPLAN coordinates 4-6 related PLANs
2. Size: 600-1,500 lines (room for complex coordination)
3. Reference parent NORTH_STAR if applicable
4. Track child PLAN status

### For Execution Work (PLAN → SUBPLAN → EXECUTION)
1. **Create PLAN** (300-900 lines) defining achievements
2. **Create SUBPLAN** for each achievement (200-600 lines):
   - Design approach thoroughly
   - Decide execution strategy (single or multiple)
   - Plan parallelization if applicable
3. **Create EXECUTION_TASK(s)** (Designer + Executor roles):
   - Designer: Creates EXECUTION_TASK file
   - Executor: Reads SUBPLAN objective + approach only
   - May run in parallel with other Executors
4. **Synthesis** (Designer):
   - Review results from all EXECUTIONs
   - Compare and synthesize learnings
   - Mark SUBPLAN complete

---

## 🎯 Benefits of v2.0

### For Strategy
- ✅ Dedicated layer for strategic vision
- ✅ Room for comprehensive principles and guidance
- ✅ Clear separation from tactical execution

### For Scaling
- ✅ Larger PLANs accommodate complex projects
- ✅ Support for 15-20+ achievement PLANs
- ✅ Natural organization at appropriate scale

### For Multi-Agent Coordination
- ✅ Designer and Executor roles clearly separated
- ✅ Minimal context for Executor (200-300 lines vs. 1,000+)
- ✅ Foundation for parallel agent execution
- ✅ Support for experimentation and exploration

### For Documentation
- ✅ Modular prompt generation
- ✅ Role-appropriate context budgets
- ✅ Clear guidance for Designer/Executor phases
- ✅ Comprehensive workflow documentation

---

## 📊 Adoption Timeline

- **Immediate**: All new documents use v2.0 structure
- **Gradual**: Existing documents migrate as needed
- **Optional**: Legacy v1.0 workflows still supported
- **Future**: Full migration to v2.0 recommended for new projects

---

## 🔗 Key Resources

**Guides**:
- `LLM/guides/NORTH-STAR-GUIDE.md` - Creating NORTH_STAR documents
- `LLM/guides/GRAMMAPLAN-GUIDE.md` - Updated with new size limits
- `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` - 4-phase workflow details
- `LLM-METHODOLOGY.md` - Complete methodology reference

**Templates**:
- `LLM/templates/NORTH_STAR-TEMPLATE.md` - Strategic vision template
- `LLM/templates/GRAMMAPLAN-TEMPLATE.md` - Coordination template (updated)
- `LLM/templates/PLAN-TEMPLATE.md` - Execution template (updated)
- `LLM/templates/SUBPLAN-TEMPLATE.md` - Design + execution template (updated)
- `LLM/templates/EXECUTION_TASK-TEMPLATE.md` - Journey template (updated)

**Prompts**:
- `LLM/templates/PROMPTS.md` (v1.1) - Copy-paste ready prompts (updated with v2.0 workflows)

---

## 🎓 Learning Points

1. **Strategic layers matter**: Decoupling strategy from tactics improves clarity
2. **Context budgets drive design**: Role-aware context enables better scaling
3. **Workflow phases enable parallelization**: Separating design from execution opens opportunities
4. **Size limits should fit reality**: Artificial constraints cause workarounds; increase limits appropriately
5. **Modularity improves automation**: Separate tools for separate roles enable better specialization

---

**Version**: 2.0  
**Status**: 🚀 Production Release  
**Date**: November 9, 2025  
**Created By**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md (Achievement 6.1)

