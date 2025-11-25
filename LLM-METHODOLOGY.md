# LLM Development Methodology

**Version**: v1.4  
**Status**: Production-Ready  
**Created**: November 2025  
**Purpose**: Structured methodology for LLM-assisted software development

---

## 🎯 What This Is

A **5-tier hierarchical methodology** for managing LLM-assisted development work:

```
⭐ NORTH_STAR ────────────────────── (Strategic Vision - "Floats above funnel, illuminating it")
       ├─→ GRAMMAPLAN → PLAN        (Strategic Coordination → Tactical Execution)
       │       └─→ SUBPLAN          (Approach + Execution Coordination)
       │           └─→ EXECUTION_TASK (Implementation Journey)
       │
       └─→ PLAN                      (Tactical Execution - Independent)
           └─→ SUBPLAN
               └─→ EXECUTION_TASK
```

**Hierarchy**: NORTH_STAR (Vision) → GrammaPlan (Orchestrate) → PLAN (Objectives) → SUBPLAN (Design) → EXECUTION_TASK (Journey)

**Key Principles**:

- ✅ Achievement-based progress (clear milestones)
- ✅ Test-driven development (quality first)
- ✅ Iterative execution (learning captured)
- ✅ Complete documentation (knowledge preserved)

**Proven**: 10+ plans, 200+ achievements, 200+ hours of real usage

---

## 🧪 Testing Requirements

**Mandatory for Code Work**: All code implementations must include comprehensive test coverage.

### Testing Policy

**Required Test Types**:

- **Unit Tests**: For all new functions and classes
- **Integration Tests**: For workflows and component interactions
- **Edge Case Tests**: For error handling and boundary conditions

**Coverage Requirement**: >90% for all new code

**Test File Naming**: `test_<script_name>.py` in `tests/LLM/scripts/<domain>/`

**Test Infrastructure**: Use existing fixtures from `tests/LLM/scripts/conftest.py`

### TDD Workflow

**Preferred Approach**: Write tests first, then implement (Test-Driven Development)

**When to Write Tests**:

- Before implementation (TDD - preferred)
- During implementation (acceptable)
- After implementation (minimum - must be before marking achievement complete)

**Test File in Deliverables**: Test file must be explicitly listed in achievement deliverables

### Validation

**Automated Validation**: Use `LLM/scripts/validation/validate_test_coverage.py` to check test file existence and coverage

**Templates**: See `LLM/templates/PLAN-TEMPLATE.md` and `LLM/templates/SUBPLAN-TEMPLATE.md` for testing requirements in achievement definitions

**Example**: See `PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md` for good testing practice

**Note**: Testing is mandatory for code work, optional for documentation-only work

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

| Protocol             | Purpose             | When to Use                   | Location                                |
| -------------------- | ------------------- | ----------------------------- | --------------------------------------- |
| **NORTH-STAR-GUIDE** | Strategic vision    | Vision & principles documents | `LLM/guides/NORTH-STAR-GUIDE.md`        |
| **GRAMMAPLAN-GUIDE** | Large initiatives   | Plans >80h or >800 lines      | `LLM/guides/GRAMMAPLAN-GUIDE.md`        |
| **MULTIPLE-PLANS**   | Manage dependencies | 2+ active/paused PLANs        | `LLM/guides/MULTIPLE-PLANS-PROTOCOL.md` |
| **MULTI-LLM**        | Team collaboration  | Multiple LLM instances        | `LLM/guides/MULTI-LLM-PROTOCOL.md`      |

---

## 📝 Templates (Copy-Paste Ready)

| Template                    | Purpose             | Use For                          | Location                                   |
| --------------------------- | ------------------- | -------------------------------- | ------------------------------------------ |
| **NORTH_STAR-TEMPLATE**     | Strategic vision    | Vision & principles (>800 lines) | `LLM/templates/NORTH_STAR-TEMPLATE.md`     |
| **GRAMMAPLAN-TEMPLATE**     | Orchestrate PLANs   | Large initiatives (>80h)         | `LLM/templates/GRAMMAPLAN-TEMPLATE.md`     |
| **PLAN-TEMPLATE**           | Define achievements | Significant features (>10h)      | `LLM/templates/PLAN-TEMPLATE.md`           |
| **SUBPLAN-TEMPLATE**        | Define approach     | One achievement strategy         | `LLM/templates/SUBPLAN-TEMPLATE.md`        |
| **EXECUTION_TASK-TEMPLATE** | Log iterations      | Track execution journey          | `LLM/templates/EXECUTION_TASK-TEMPLATE.md` |
| **PROMPTS**                 | Standard prompts    | Common workflows                 | `LLM/templates/PROMPTS.md` ⭐              |

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

### Five-Tier Hierarchy

**Overview**:

```
⭐ NORTH_STAR → 📋 GRAMMAPLAN → 📄 PLAN → 📝 SUBPLAN → ✅ EXECUTION_TASK
(Vision)       (Orchestrate)   (What)   (Design)   (Journey)
```

**The Funnel Metaphor**: NORTH_STAR floats above the funnel, illuminating all work below with strategic principles and vision.

---

**0. NORTH_STAR** (optional - strategic vision):

- Strategic vision and guiding principles
- "Floats above funnel, illuminating it"
- 800-2,000 lines
- May coordinate GrammaPlans/PLANs
- Living document (evolves with understanding)
- Example: NORTH_STAR_LLM-DEVELOPMENT-PHILOSOPHY.md
- Location: `work-space/north-stars/`

1. **GRAMMAPLAN** (optional - for large initiatives):

   - Coordinates 6-8 child PLANs
   - > 80 hours OR >800 lines OR 3+ domains
   - Strategic orchestration (600-1,500 lines)
   - Example: GRAMMAPLAN_GRAPHRAG-PIPELINE-EXCELLENCE.md
   - Location: `work-space/grammaplans/`

2. **PLAN** (defines WHAT to achieve):

   - Lists priority-ordered achievements
   - Self-contained (LLM can execute from PLAN alone)
   - Dynamic (add achievements during work)
   - 300-900 lines
   - Example: PLAN_ENTITY-RESOLUTION-REFACTOR.md
   - Location: `work-space/plans/`

3. **SUBPLAN** (defines HOW to achieve):

   - Created on-demand for one achievement
   - Specific approach, deliverables, tests
   - Static once created
   - 200-600 lines
   - Example: SUBPLAN_ENTITY-RESOLUTION-REFACTOR_01.md
   - Location: `work-space/subplans/`

4. **EXECUTION_TASK** (logs the journey):
   - Dynamic log of all iterations
   - Captures learnings, what worked/didn't
   - Multiple per SUBPLAN possible (different attempts)
   - <200 lines
   - Example: EXECUTION_TASK_ENTITY-RESOLUTION-REFACTOR_01_01.md
   - Location: `work-space/plans/<PLAN>/execution/` (nested with PLAN)

### Document Size Table

| Document Type         | Size Range | Purpose                  | Location                           |
| --------------------- | ---------- | ------------------------ | ---------------------------------- |
| NORTH_STAR            | 800-2,000  | Strategic vision         | work-space/north-stars/            |
| GRAMMAPLAN            | 600-1,500  | Coordinate PLANs         | work-space/grammaplans/            |
| PLAN                  | 300-900    | Define achievements      | work-space/plans/                  |
| SUBPLAN               | 200-600    | Define approach          | work-space/subplans/               |
| EXECUTION_TASK        | <200       | Log execution journey    | work-space/plans/<PLAN>/execution/ |
| EXECUTION_ANALYSIS    | 200-1,000  | Investigation & analysis | work-space/analyses/               |
| EXECUTION_CASE-STUDY  | 200-1,000  | Pattern documentation    | work-space/case-studies/           |
| EXECUTION_OBSERVATION | 100-500    | Real-time feedback       | work-space/observations/           |
| EXECUTION_DEBUG       | 200-1,000  | Issue investigation      | work-space/debug-logs/             |
| EXECUTION_REVIEW      | 200-1,000  | Implementation review    | work-space/reviews/                |

### Naming Convention

- NORTH*STAR: `NORTH_STAR*<NAME>.md`
- GRAMMAPLAN: `GRAMMAPLAN_<FEATURE>.md`
- PLAN: `PLAN_<FEATURE>.md` or `PLAN_<GRAMMAPLAN>-<DOMAIN>.md` (child)
- SUBPLAN: `SUBPLAN_<FEATURE>_<NUMBER>.md` (nested: `work-space/plans/<PLAN>/subplans/`)
- EXECUTION*TASK: `EXECUTION_TASK*<FEATURE>_<SUBPLAN>_<EXECUTION>.md`(nested:`work-space/plans/<PLAN>/execution/`)
- EXECUTION*ANALYSIS: `EXECUTION_ANALYSIS*<TOPIC>.md`(flat:`work-space/analyses/`)
- EXECUTION\*CASE-STUDY: `EXECUTION_CASE-STUDY_<FEATURE>.md` (flat: `work-space/case-studies/`)
- EXECUTION\*OBSERVATION: `EXECUTION_OBSERVATION_<TOPIC>_<DATE>.md` (flat: `work-space/observations/`)
- EXECUTION\*DEBUG: `EXECUTION_DEBUG_<ISSUE>.md` (flat: `work-space/debug-logs/`)
- EXECUTION\*REVIEW: `EXECUTION_REVIEW_<FEATURE>.md` (flat: `work-space/reviews/`)

---

## 🎯 Execution Work System

The methodology distinguishes two types of execution-level work:

### EXECUTION_TASK (Tier 4 - SUBPLAN-Connected)

**Purpose**: Track the iterative implementation journey of a SUBPLAN achievement, from design to completion.

**Characteristics**:

- Connected to specific SUBPLAN
- <200 lines (hard limit)
- Iteration tracking with test-first workflow
- Location: `work-space/execution/`
- Deleted when SUBPLAN archived (not archived separately)

**Example**: Implementing Authentication in SUBPLAN_04 → Create `EXECUTION_TASK_FEATURE_04_01.md` in `work-space/plans/FEATURE/execution/` to log iterations, tests, and learnings.

### EXECUTION_WORK (Standalone Knowledge Work - Outside Hierarchy)

**Purpose**: Capture standalone knowledge creation (analysis, case studies, observations, reviews, debugging) that informs strategy but isn't directly implementing a SUBPLAN.

**Types** (5 categories):

1. **EXECUTION_ANALYSIS**: Structured investigation (5 subcategories: bug-analysis, methodology-review, implementation-review, process-analysis, planning-strategy)
2. **EXECUTION_CASE-STUDY**: Deep dive with pattern extraction
3. **EXECUTION_OBSERVATION**: Real-time feedback during work
4. **EXECUTION_DEBUG**: Complex issue investigation
5. **EXECUTION_REVIEW**: Post-completion assessment

**Characteristics**:

- Standalone, not SUBPLAN-connected
- 200-1000+ lines (variable)
- Archived by type/topic for future reference
- Ad-hoc creation as knowledge work emerges

**Locations** (Flat folders by type):

- EXECUTION_ANALYSIS: `work-space/analyses/`
- EXECUTION_CASE-STUDY: `work-space/case-studies/`
- EXECUTION_OBSERVATION: `work-space/observations/`
- EXECUTION_DEBUG: `work-space/debug-logs/`
- EXECUTION_REVIEW: `work-space/reviews/`

**Example**: After implementing Authentication, create `EXECUTION_ANALYSIS_AUTHENTICATION-PERFORMANCE-REVIEW.md` in `work-space/analyses/` to analyze performance vs alternatives.

### Decision Framework

**When EXECUTION_TASK?** "I'm implementing Achievement 2.3 from SUBPLAN_XX" → YES, use EXECUTION_TASK

**When EXECUTION_WORK?** "I need to analyze the codebase strategy" OR "I found a pattern worth documenting" → YES, use EXECUTION_WORK

**See**: `LLM/guides/EXECUTION-TAXONOMY.md` for detailed decision tree, 12+ scenario examples, and quick reference card.

---

---

## 📁 Feedback System (Achievement Completion Tracking)

The **feedback system** is how we track achievement completion using a filesystem-first approach.

### Core Concept

Instead of marking achievements complete in PLAN markdown (which gets out of sync), we use dedicated `APPROVED_XX.md` files as the single source of truth:

- **PLAN** defines what achievements exist (Achievement Index)
- **Filesystem** tracks which achievements are complete (APPROVED files)
- **No fallback** to PLAN markdown for completion status

### Achievement Index

Every PLAN must have an **Achievement Index** section near the top that lists all achievements:

```markdown
## 📋 Achievement Index

**All Achievements in This Plan**:

- ✅ Achievement 0.1: First Achievement
- ✅ Achievement 0.2: Second Achievement
- Achievement 1.1: Third Achievement (in progress)
```

**Purpose**: Quick reference, enables scripts to detect all achievements, shows progress.

### APPROVED Files

Completed achievements have an `APPROVED_XX.md` file in `execution/feedbacks/`:

**Naming**: `APPROVED_XX.md` where XX is achievement number without dot

- Achievement 0.1 → `APPROVED_01.md`
- Achievement 1.1 → `APPROVED_11.md`
- Achievement 2.4 → `APPROVED_24.md`

**Location**: `work-space/plans/FEATURE/execution/feedbacks/APPROVED_XX.md`

**Detection**:

```python
def is_achievement_complete(ach_num: str, plan_path: Path) -> bool:
    feedbacks_dir = plan_path.parent / "execution" / "feedbacks"
    approved_file = feedbacks_dir / f"APPROVED_{ach_num.replace('.', '')}.md"
    return approved_file.exists()
```

### Tools

**Validate feedback system**:

```bash
python3 LLM/scripts/validation/validate_feedback_system.py work-space/plans/FEATURE/
```

**Migrate legacy plan**:

```bash
python3 LLM/scripts/migration/migrate_legacy_completions.py work-space/plans/FEATURE/ --apply
```

### Documentation

- **Full Guide**: `LLM/docs/FEEDBACK_SYSTEM_GUIDE.md`
- **Troubleshooting**: `LLM/docs/FEEDBACK_SYSTEM_TROUBLESHOOTING.md`
- **Philosophy**: `LLM/docs/STATE_TRACKING_PHILOSOPHY.md`

---

## 🎓 Multi-Agent Workflow Evolution

The methodology now explicitly separates agent roles in the SUBPLAN independent workflow:

**Designer Agent** (SUBPLAN work):

- Analyzes requirements deeply
- Designs approach and coordination strategy
- Plans multiple EXECUTIONs (if needed)
- Coordinates parallel work
- Synthesizes collective learnings from EXECUTIONs

**Executor Agents** (EXECUTION_TASK work):

- Receive minimal context (SUBPLAN objective + approach only)
- Execute according to Designer's plan
- Document journey and learnings
- May work in parallel on independent tasks
- Report results for Designer synthesis

**Designer/Executor Separation Benefits**:

- ✅ Each agent can focus on their role deeply
- ✅ Reduces context pollution (Executor gets 200 lines, not 1,000+)
- ✅ Enables true parallelization (multiple Executors under one Designer)
- ✅ Foundation for concurrent multi-agent systems
- ✅ Clearer accountability and specialization

**Parallel Execution Patterns**:

- **Sequential**: Step 1 → Step 2 → Step 3 (default)
- **Parallel Independent**: Multiple EXECUTIONs run simultaneously, coordinated by Designer
- **Parallel Iterative**: Run, learn, improve, repeat (A/B testing, refinement)

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
├── index/               # 🔍 File index for fast discovery
│   ├── FILE-INDEX.md    # Central catalog of all methodology files ⭐
│   └── README.md        # How to use the index
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
├── scripts/             # Automation scripts
│   ├── archiving/       # Archiving scripts
│   │   ├── archive_completed.py  # Deferred archiving during execution
│   │   └── manual_archive.py    # User-controlled on-demand archiving ⭐
│   ├── generation/      # Prompt generation
│   └── validation/      # Validation scripts
├── examples/            # Example PLANs and workflows
│   └── (to be populated)
├── QUICK-START.md       # 5-minute getting started
└── README.md            # Navigation and structure
```

**Active Work**: Lives in `work-space/` directory:

- `work-space/plans/` - PLAN files
- `work-space/subplans/` - SUBPLAN files
- `work-space/execution/` - EXECUTION_TASK files
- See `work-space/README.md` for workspace documentation

**Completed Work**: Lives in `documentation/archive/`

**Archiving**: Use `LLM/scripts/archiving/manual_archive.py` for user-controlled on-demand archiving from workspace.

**🔍 Quick File Discovery**: See `LLM/index/FILE-INDEX.md` for complete catalog of all methodology files

---

## 🏷️ Metadata Tags and Virtual Organization

**Purpose**: Organize files by metadata rather than physical directory structure.

**Key Concept**: **Virtual Organization**

- Files stay in root directory (no physical moves needed)
- Organized by metadata tags (type, status, plan, achievement, priority)
- Search tool queries by tags (see `PLAN_FILE-MOVING-ADVANCED-OPTIMIZATION.md`)
- No reference updates when organizing (tags change, not file locations)

**Standard Tags**:

- **type**: PLAN, SUBPLAN, EXECUTION_TASK, EXECUTION_ANALYSIS, GRAMMAPLAN
- **status**: active, complete, paused, archived, abandoned
- **plan**: Parent PLAN name (for SUBPLANs and EXECUTION_TASKs)
- **achievement**: Achievement number (e.g., 1.1, 2.3)
- **priority**: Priority level (0-4, for PLANs)
- **created**: Creation date
- **completed**: Completion date (for completed work)

**Benefits**:

- No file moving needed (eliminates all moving overhead)
- No reference updates (files don't move)
- Flexible organization (query by any tag combination)
- Fast discovery with search tool (future)

**Current Status**: Metadata tags documented, templates updated. Full value realized when search tool implemented (see `PLAN_FILE-MOVING-ADVANCED-OPTIMIZATION.md`).

**Documentation**: See `LLM/guides/METADATA-TAGS.md` for complete tag system documentation, usage examples, and conventions.

---

## 🎯 Success Metrics

**Methodology Health** (from Nov 2025 review of 10 PLANs):

| Metric                | Score        | Evidence                 |
| --------------------- | ------------ | ------------------------ |
| Achievement Structure | ✅ Excellent | 100% adoption            |
| TDD Adherence         | ✅ Excellent | 0% circular debug        |
| Test Coverage         | ✅ Excellent | >90% for new code        |
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
