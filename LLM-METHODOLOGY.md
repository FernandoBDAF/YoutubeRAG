# LLM Development Methodology

**Version**: v1.4  
**Status**: Production-Ready  
**Created**: November 2025  
**Purpose**: Structured methodology for LLM-assisted software development

---

## 🎯 What This Is

A **4-tier hierarchical methodology** for managing LLM-assisted development work:

```
GRAMMAPLAN → PLAN → SUBPLAN → EXECUTION_TASK
(Strategy)   (What)  (How)     (Journey)
```

**Key Principles**:

- ✅ Achievement-based progress (clear milestones)
- ✅ Test-driven development (quality first)
- ✅ Iterative execution (learning captured)
- ✅ Complete documentation (knowledge preserved)

**Proven**: 10+ plans, 200+ achievements, 200+ hours of real usage

---

## 🚀 Quick Start (5 Minutes)

**Create Your First PLAN**:

1. Copy prompt from `LLM/templates/PROMPTS.md` → "Create New PLAN"
2. Replace placeholders: [FEATURE_NAME], [GOAL], [PRIORITY]
3. LLM creates PLAN\_[FEATURE].md using template
4. Start executing achievements!

**Example**: [See PROMPTS.md for complete examples]

---

## 📚 Core Protocols (Essential Reading)

### Entry/Exit Workflows

| Protocol            | Purpose              | When to Use                         | Location                                       |
| ------------------- | -------------------- | ----------------------------------- | ---------------------------------------------- |
| **START_POINT**     | Begin new work       | Starting any PLAN/SUBPLAN/EXECUTION | `LLM/protocols/IMPLEMENTATION_START_POINT.md`  |
| **RESUME**          | Continue paused work | Resuming after break                | `LLM/protocols/IMPLEMENTATION_RESUME.md`       |
| **END_POINT**       | Complete and archive | Finishing PLAN                      | `LLM/protocols/IMPLEMENTATION_END_POINT.md`    |
| **MID_PLAN_REVIEW** | Quality checkpoint   | Long plans (>20h, 5+ priorities)    | `LLM/guides/IMPLEMENTATION_MID_PLAN_REVIEW.md` |

### Coordination Protocols

| Protocol             | Purpose             | When to Use              | Location                                |
| -------------------- | ------------------- | ------------------------ | --------------------------------------- |
| **MULTIPLE-PLANS**   | Manage dependencies | 2+ active/paused PLANs   | `LLM/guides/MULTIPLE-PLANS-PROTOCOL.md` |
| **MULTI-LLM**        | Team collaboration  | Multiple LLM instances   | `LLM/guides/MULTI-LLM-PROTOCOL.md`      |
| **GRAMMAPLAN-GUIDE** | Large initiatives   | Plans >80h or >800 lines | `LLM/guides/GRAMMAPLAN-GUIDE.md`        |

---

## 📝 Templates (Copy-Paste Ready)

| Template                    | Purpose             | Use For                     | Location                                   |
| --------------------------- | ------------------- | --------------------------- | ------------------------------------------ |
| **PLAN-TEMPLATE**           | Define achievements | Significant features (>10h) | `LLM/templates/PLAN-TEMPLATE.md`           |
| **SUBPLAN-TEMPLATE**        | Define approach     | One achievement strategy    | `LLM/templates/SUBPLAN-TEMPLATE.md`        |
| **EXECUTION_TASK-TEMPLATE** | Log iterations      | Track execution journey     | `LLM/templates/EXECUTION_TASK-TEMPLATE.md` |
| **GRAMMAPLAN-TEMPLATE**     | Orchestrate PLANs   | Large initiatives (>80h)    | `LLM/templates/GRAMMAPLAN-TEMPLATE.md`     |
| **PROMPTS**                 | Standard prompts    | Common workflows            | `LLM/templates/PROMPTS.md` ⭐              |

**⭐ Start Here**: `PROMPTS.md` has copy-paste prompts for all common tasks!

---

## 🎓 Learn by Example

**Recommended Reading Order**:

1. **This file** (you are here) - 5 min
2. **LLM/templates/PROMPTS.md** - 10 min (see all workflows)
3. **LLM/protocols/IMPLEMENTATION_START_POINT.md** - 20 min (understand process)
4. **Real PLAN** (e.g., PLAN_GRAPHRAG-VALIDATION.md in root) - 10 min (see it in action)

**Total**: 45 minutes to full understanding

---

## 📊 Methodology Structure

### Four-Tier Hierarchy

1. **GRAMMAPLAN** (optional - for large initiatives):

   - Coordinates 6-8 child PLANs
   - > 80 hours OR >800 lines OR 3+ domains
   - Strategic orchestration (~200-300 lines)
   - Example: GRAMMAPLAN_LLM-METHODOLOGY-V2.md

2. **PLAN** (defines WHAT to achieve):

   - Lists priority-ordered achievements
   - Self-contained (LLM can execute from PLAN alone)
   - Dynamic (add achievements during work)
   - Example: PLAN_ENTITY-RESOLUTION-REFACTOR.md

3. **SUBPLAN** (defines HOW to achieve):

   - Created on-demand for one achievement
   - Specific approach, deliverables, tests
   - Static once created
   - Example: SUBPLAN_ENTITY-RESOLUTION-REFACTOR_01.md

4. **EXECUTION_TASK** (logs the journey):
   - Dynamic log of all iterations
   - Captures learnings, what worked/didn't
   - Multiple per SUBPLAN possible (different attempts)
   - Example: EXECUTION_TASK_ENTITY-RESOLUTION-REFACTOR_01_01.md

### Naming Convention

- GRAMMAPLAN: `GRAMMAPLAN_<FEATURE>.md`
- PLAN: `PLAN_<FEATURE>.md` or `PLAN_<GRAMMAPLAN>-<DOMAIN>.md` (child)
- SUBPLAN: `SUBPLAN_<FEATURE>_<NUMBER>.md`
- EXECUTION*TASK: `EXECUTION_TASK*<FEATURE>_<SUBPLAN>_<EXECUTION>.md`
- EXECUTION*ANALYSIS: `EXECUTION_ANALYSIS*<TOPIC>.md` (for analyses, not execution tracking)

---

## 🌐 For External Projects

**To Use This Methodology in Your Project**:

1. **Copy Files**:

   ```bash
   # Copy entire LLM folder
   cp -r /path/to/this/project/LLM /path/to/your/project/

   # Copy entry point
   cp /path/to/this/project/LLM-METHODOLOGY.md /path/to/your/project/
   ```

2. **Customize**:

   - Review LLM/ docs (no changes needed for methodology)
   - Create your first PLAN using PROMPTS.md
   - Adapt examples to your domain

3. **Start Working**:
   - Follow prompts from PROMPTS.md
   - Use templates from LLM/templates/
   - Follow protocols from LLM/protocols/

**Time to Adopt**: ~30 minutes (copy files, read quick-start, create first PLAN)

---

## 📖 Full Documentation Index

**All methodology documentation lives in `LLM/` folder**:

```
LLM/
├── protocols/           # How to start, resume, complete work
│   ├── IMPLEMENTATION_START_POINT.md
│   ├── IMPLEMENTATION_RESUME.md
│   ├── IMPLEMENTATION_END_POINT.md
│   └── IMPLEMENTATION_BACKLOG.md
├── templates/           # Document templates
│   ├── PLAN-TEMPLATE.md
│   ├── SUBPLAN-TEMPLATE.md
│   ├── EXECUTION_TASK-TEMPLATE.md
│   ├── GRAMMAPLAN-TEMPLATE.md
│   └── PROMPTS.md ⭐ (start here!)
├── guides/              # Specialized guides
│   ├── MULTIPLE-PLANS-PROTOCOL.md
│   ├── MULTI-LLM-PROTOCOL.md
│   ├── GRAMMAPLAN-GUIDE.md
│   └── IMPLEMENTATION_MID_PLAN_REVIEW.md
├── examples/            # Example PLANs and workflows
│   └── (to be populated)
├── QUICK-START.md       # 5-minute getting started
└── README.md            # Navigation and structure
```

**Active Work**: Lives in project root (PLAN*\*.md, SUBPLAN*_.md, EXECUTION\__.md)

**Completed Work**: Lives in `documentation/archive/`

---

## 🎯 Success Metrics

**Methodology Health** (from Nov 2025 review of 10 PLANs):

| Metric                | Score        | Evidence                 |
| --------------------- | ------------ | ------------------------ |
| Achievement Structure | ✅ Excellent | 100% adoption            |
| TDD Adherence         | ✅ Excellent | 0% circular debug        |
| Partial Completion    | ✅ Excellent | 100% success rate        |
| Archive Quality       | ✅ Excellent | All resumable            |
| Context Management    | 🟡 Improving | Optimization in progress |
| Automation            | 🟡 Improving | Tools being built        |

**Overall**: ✅ Fundamentally sound, continuous improvement

---

## 🔄 Version History

- **v1.0** (Nov 2025): Foundation (START_POINT, END_POINT, templates)
- **v1.1** (Nov 2025): RESUME protocol
- **v1.2** (Nov 2025): BACKLOG process
- **v1.3** (Nov 2025): MULTIPLE-PLANS-PROTOCOL
- **v1.4** (Nov 2025): GrammaPlan, Mid-Plan Review, Pre-Completion Review, Execution Statistics, Predefined Prompts

**Current**: v1.4 (Production-Ready)

---

## 🆘 Need Help?

**Common Questions**:

- **"How do I start?"** → Read `LLM/templates/PROMPTS.md`, use "Create New PLAN" prompt
- **"How do I resume paused work?"** → Use "Resume Paused PLAN" prompt from PROMPTS.md
- **"My plan is getting large"** → Check `LLM/guides/GRAMMAPLAN-GUIDE.md` for GrammaPlan option
- **"Working with team?"** → Read `LLM/guides/MULTI-LLM-PROTOCOL.md`

**Read Next**: `LLM/templates/PROMPTS.md` (most useful starting point)

---

**Maintained By**: PLAN_STRUCTURED-LLM-DEVELOPMENT.md (meta-PLAN in root)  
**Latest Updates**: GRAMMAPLAN_LLM-METHODOLOGY-V2.md (methodology v2 in progress)  
**Status**: ✅ Production-Ready, continuously improving
