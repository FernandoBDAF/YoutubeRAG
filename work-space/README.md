# Work-Space Directory: Active LLM Development Files

**Purpose**: Central workspace for active LLM methodology documents  
**Status**: Active Development Hub  
**Last Updated**: November 9, 2025

---

## 📁 Folder Structure

### `north-stars/` ⭐
**Purpose**: Strategic vision documents that illuminate and guide all work  
**Size**: 800-2,000 lines per document  
**Examples**: NORTH_STAR_LLM-METHODOLOGY.md, NORTH_STAR_MULTI-AGENT-COORDINATION.md

These documents exist "above the funnel," providing strategic principles and long-term vision that guide all tactical work below. They rarely change and serve as reference points for GrammaPlans and PLANs.

### `grammaplans/` 📋
**Purpose**: Strategic coordination documents that orchestrate multiple PLANs  
**Size**: 600-1,500 lines per document  
**Examples**: GRAMMAPLAN_GRAPHRAG-PIPELINE-EXCELLENCE.md, GRAMMAPLAN_EXECUTION-WORK-SYSTEM-ENHANCEMENT.md

GrammaPlans coordinate 4-6 related child PLANs under a strategic umbrella. They track completion of child PLANs and identify dependencies.

### `plans/` 📄
**Purpose**: Tactical execution documents defining achievements for a specific feature or domain  
**Size**: 300-900 lines per document  
**Examples**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md, PLAN_GRAPHRAG-VALIDATION.md

PLANs break down work into priority-ordered achievements. With the v2.0 workflow, PLANs provide context for SUBPLAN creation only (not execution), enabling efficient context separation.

### `subplans/` 📝
**Purpose**: Design and execution coordination documents  
**Size**: 200-600 lines per document  
**Naming**: `SUBPLAN_<FEATURE>_<NUMBER>.md`

SUBPLANs define the approach for one achievement and coordinate execution. They support:
- Single or multiple EXECUTIONs
- Parallel execution of independent work
- Synthesis of collective learnings from multiple EXECUTIONs

### `execution/` ✅
**Purpose**: Execution journey documents logging work attempts  
**Size**: <200 lines per document  
**Naming**: `EXECUTION_TASK_<FEATURE>_<SUBPLAN>_<EXECUTION>.md`

EXECUTIONs log the journey of executing according to the SUBPLAN design. Multiple EXECUTIONs can exist for:
- Different approaches (A/B testing)
- Sequential refinement (iteration)
- Parallel independent work

---

## 🔄 Workflow: From PLAN to Execution

### Phase 1: Design (Designer)
1. Create SUBPLAN (200-600 lines)
2. Design approach thoroughly
3. Plan execution strategy (single or multiple?)
4. Plan parallelization if applicable

### Phase 2: Execution Planning (Designer)
1. Create EXECUTION_TASK file(s)
2. Mark executability in SUBPLAN

### Phase 3: Execution (Executor)
1. Read SUBPLAN objective + approach only
2. Execute according to plan
3. May run in parallel with other Executors
4. Document journey and learnings

### Phase 4: Synthesis (Designer)
1. Review results from all EXECUTIONs
2. Synthesize collective learnings
3. Recommend best approach
4. Mark SUBPLAN complete

---

## 📊 Statistics

| Document Type | Active | Total Archived | Size Range |
|---------------|--------|----------------|-----------|
| NORTH_STARs | 3 | - | 800-2,000 lines |
| GrammaPlans | 6 | - | 600-1,500 lines |
| PLANs | 17+ | - | 300-900 lines |
| SUBPLANs | 30+ | - | 200-600 lines |
| EXECUTION_TASKs | 31+ | - | <200 lines |

---

## 🚀 Getting Started

### For New Work
1. Check `ACTIVE_PLANS.md` for related plans
2. Find or create a PLAN (300-900 lines)
3. For an achievement, create a SUBPLAN (200-600 lines)
4. Execute via EXECUTION_TASK(s) (<200 lines each)

### For Strategic Work
1. Check if NORTH_STAR exists for your domain
2. If not, create one (800-2,000 lines) for strategic vision
3. Reference from related GrammaPlans or PLANs

### For Large Coordination
1. Identify 4-6 related PLANs
2. Create GrammaPlan (600-1,500 lines) to coordinate
3. Track child PLAN completion

---

## 📚 Documentation

- **`LLM-METHODOLOGY.md`** - Complete methodology reference
- **`LLM/guides/NORTH-STAR-GUIDE.md`** - NORTH_STAR creation guide
- **`LLM/guides/GRAMMAPLAN-GUIDE.md`** - GrammaPlan creation guide
- **`LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md`** - 4-phase workflow guide
- **`METHODOLOGY-EVOLUTION-v2.0.md`** - What changed and why

---

## 🔗 Archive

Completed and paused work is archived in:  
`documentation/archive/`

Archive structure mirrors work-space:
- `documentation/archive/<FEATURE>/subplans/`
- `documentation/archive/<FEATURE>/execution/`

---

**This workspace represents the current state of all active LLM development work. Use the guides and templates in `LLM/` for comprehensive documentation.**
