# LLM Methodology Examples: Reference Implementations

**Purpose**: Real-world examples demonstrating v2.0 five-tier hierarchy and workflows  
**Status**: Active Examples  
**Last Updated**: November 9, 2025

---

## 📚 What's Here

Examples of all major document types and workflows, ready to use as templates or reference for your own work.

---

## ⭐ Strategic Documents: NORTH_STAR

### NORTH_STAR_EXAMPLE_LEARNING-SYSTEMS.md

**What**: Strategic vision for building adaptive learning systems  
**Size**: ~900 lines  
**Purpose**: Demonstrates NORTH_STAR structure, strategic principles, coordination framework

**Key Sections**:

- Strategic vision statement
- 4 core principles with rationale and applications
- Current state assessment
- Evolution roadmap (3 phases)
- Coordination framework showing related PLANs
- Decision framework for alignment checks
- Metrics & health indicators

**Learn From This**:

- How to structure strategic vision
- How to connect principles to PLANs
- How to create decision frameworks
- How to track strategic health

**Use This When**:

- Creating your first NORTH_STAR
- Unsure what scope/detail level NORTH_STAR should have
- Need example of principle-based organization

**Reference**: See `LLM/guides/NORTH-STAR-GUIDE.md`

---

## 📝 Execution Documents: Multi-EXECUTION SUBPLAN + Parallel EXECUTIONs

### SUBPLAN_EXAMPLE_MULTI-EXECUTION.md

**What**: SUBPLAN demonstrating parallel execution exploration  
**Size**: ~480 lines  
**Purpose**: Shows how to use multiple parallel EXECUTIONs to explore options

**Key Sections**:

- Clear objective for parallel work
- Execution strategy (multiple parallel)
- Planned Executions table (3 independent approaches)
- Active EXECUTION_TASKs table
- Execution Results Synthesis section
- Comparative analysis table
- Key learnings extracted
- Recommendations based on synthesis

**Learn From This**:

- How to structure multi-execution workflow
- How to coordinate parallel work
- How to synthesize results
- How to make recommendations from evidence

**Use This When**:

- Need to explore multiple approaches
- Want to make data-driven decisions
- Have independent work that can run in parallel
- Need to compare trade-offs

**Reference**: See `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` (Phase 2: Execution Planning)

---

### EXECUTION_TASK_EXAMPLE_PARALLEL_01.md

### EXECUTION_TASK_EXAMPLE_PARALLEL_02.md

### EXECUTION_TASK_EXAMPLE_PARALLEL_03.md

**What**: Three parallel EXECUTIONs demonstrating independent work  
**Size**: <200 lines each  
**Purpose**: Shows how Executors read SUBPLAN minimally and work independently

**Key Sections** (each):

- SUBPLAN Context (objective + approach only - minimal reading)
- Parallelization Context (coordination without dependencies)
- Iteration log showing work done
- Results & learnings
- Quality checks
- Status and next steps

**Learn From These**:

- How much context Executor needs (minimal)
- How to document independent work
- How parallelization context works
- How to report learnings concisely

**Use These When**:

- Need to understand Executor role
- Want to see minimal context in action
- Exploring multiple approaches in parallel
- Learning from independent experiments

**Reference**: See `LLM/protocols/CREATE_EXECUTION.md`

---

## 🎯 How to Use These Examples

### Scenario 1: Learning v2.0 Workflow

1. Read `SUBPLAN_EXAMPLE_MULTI-EXECUTION.md` completely
2. Read EXECUTION_TASK examples in order (01 → 02 → 03)
3. Notice how synthesis brings results together
4. See how recommendations emerge from evidence

### Scenario 2: Creating Your First Multi-Execution SUBPLAN

1. Copy `SUBPLAN_EXAMPLE_MULTI-EXECUTION.md` as template
2. Replace content with your objective and approaches
3. Update Planned Executions table (your 2-3 approaches)
4. Copy EXECUTION_TASK examples and customize
5. Run your EXECUTIONs in parallel
6. Update Execution Results Synthesis with real results

### Scenario 3: Understanding Executor Role

1. Read EXECUTION_TASK_EXAMPLE_PARALLEL_01.md
2. Notice "SUBPLAN Context" (what Executor reads)
3. Notice what's NOT there (full SUBPLAN isn't included)
4. See "Parallelization Context" (coordination info only)
5. Notice results are concise and learnings are clear

### Scenario 4: Creating Your First NORTH_STAR

1. Read `NORTH_STAR_EXAMPLE_LEARNING-SYSTEMS.md` completely
2. Notice structure: vision → principles → roadmap → coordination
3. Notice decision framework connects strategy to tactics
4. Use as template for your own NORTH_STAR
5. Adapt principles to your domain

---

## 📊 Example Statistics

| Document                               | Type                  | Size       | Status      |
| -------------------------------------- | --------------------- | ---------- | ----------- |
| NORTH_STAR_EXAMPLE_LEARNING-SYSTEMS.md | NORTH_STAR            | ~900 lines | ✅ Complete |
| SUBPLAN_EXAMPLE_MULTI-EXECUTION.md     | SUBPLAN               | ~480 lines | ✅ Complete |
| EXECUTION_TASK_EXAMPLE_PARALLEL_01.md  | EXECUTION (Schema)    | ~150 lines | ✅ Complete |
| EXECUTION_TASK_EXAMPLE_PARALLEL_02.md  | EXECUTION (Heuristic) | ~150 lines | ✅ Complete |
| EXECUTION_TASK_EXAMPLE_PARALLEL_03.md  | EXECUTION (Hybrid)    | ~160 lines | ✅ Complete |

---

## 🔗 Related Documentation

- `LLM/guides/NORTH-STAR-GUIDE.md` - How to create NORTH_STARs
- `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` - 4-phase workflow guide
- `LLM/protocols/CREATE_SUBPLAN.md` - Designer phase protocol
- `LLM/protocols/CREATE_EXECUTION.md` - Executor phase protocol
- `METHODOLOGY-EVOLUTION-v2.0.md` - Complete v2.0 overview
- `LLM-METHODOLOGY.md` - Full methodology reference

---

## 💡 Key Takeaways

1. **NORTH_STARs** float above work, providing strategic light
2. **SUBPLANs** coordinate execution, support multiple parallel executions
3. **EXECUTIONs** read minimal context, work independently
4. **Synthesis** brings parallel results together into recommendations
5. **Parallelization** enables true multi-agent work

---

## ✨ Why These Examples Matter

These examples show v2.0 in action:

- ✅ Strategic documents (NORTH_STAR) exist independently
- ✅ Multi-execution workflows (3 parallel EXECUTIONs)
- ✅ Minimal context reading (Executor sees objective only)
- ✅ Synthesis pattern (bringing results together)
- ✅ Role separation (Designer plans, Executor executes)
- ✅ Parallelization (3 independent approaches)

Use them as reference, template, or learning material for your own methodology implementation.

---

**Status**: ✅ Active Examples  
**Version**: 2.0  
**Last Updated**: November 9, 2025
