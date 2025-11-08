# LLM Development Methodology: Core Documentation & Tools

**Version**: 2.0  
**Status**: Production Ready  
**Last Updated**: November 9, 2025

---

## 🎯 What This Folder Contains

The `LLM/` directory contains all methodology documentation, templates, protocols, guides, scripts, and tools for structured LLM-assisted development.

---

## 📚 Core Documentation

### Entry Points
- **`LLM-METHODOLOGY.md`** - Complete methodology reference (418 lines)
  - Five-tier hierarchy (NORTH_STAR → GRAMMAPLAN → PLAN → SUBPLAN → EXECUTION)
  - Document size limits and naming conventions
  - Quick start guide for different workflows
  - EXECUTION_ANALYSIS documents for strategic analysis

- **`METHODOLOGY-EVOLUTION-v2.0.md`** - What changed and why (comprehensive overview)
  - Evolution from v1.0 (4-tier) to v2.0 (5-tier)
  - Size limit changes and rationale
  - Workflow improvements for multi-agent coordination
  - Migration guide for existing documents

---

## 📋 Guides (Read Next)

Start here to understand how to work with each document type:

### Strategic Documents
- **`guides/NORTH-STAR-GUIDE.md`** - Creating strategic vision documents
  - When to create NORTH_STAR
  - How to write strategic vision and principles
  - Maintaining north stars long-term
  - Decision tree for NORTH_STAR vs GrammaPlan vs PLAN

### Coordination Documents  
- **`guides/GRAMMAPLAN-GUIDE.md`** - Orchestrating multiple PLANs
  - When to use GrammaPlan
  - Decomposition patterns
  - Progress tracking
  - Integration strategies

### Execution Documents
- **`guides/SUBPLAN-WORKFLOW-GUIDE.md`** - The 4-phase independent SUBPLAN workflow
  - Phase 1: Design (Designer)
  - Phase 2: Execution Planning (Designer)
  - Phase 3: Execution (Executor)
  - Phase 4: Synthesis (Designer)
  - Decision trees and 3 comprehensive examples

- **`guides/FOCUS-RULES.md`** - Context budget guidelines for LLMs
  - Agent context budgets and what each agent reads
  - Context separation benefits
  - How to write focus-aware documents

### Other Guides
- **`guides/MULTIPLE-PLANS-PROTOCOL.md`** - Managing multiple active PLANs
- **`guides/IMPLEMENTATION_MID_PLAN_REVIEW.md`** - Quality checkpoints for long PLANs

---

## 📄 Templates (Copy-Paste Ready)

Use these templates when creating new documents:

### Strategic
- **`templates/NORTH_STAR-TEMPLATE.md`** - Strategic vision template (800-2,000 lines)

### Coordination
- **`templates/GRAMMAPLAN-TEMPLATE.md`** - GrammaPlan template (600-1,500 lines)

### Execution
- **`templates/PLAN-TEMPLATE.md`** - PLAN template (300-900 lines)
- **`templates/SUBPLAN-TEMPLATE.md`** - SUBPLAN template (200-600 lines)
- **`templates/EXECUTION_TASK-TEMPLATE.md`** - EXECUTION_TASK template (<200 lines)

### Predefined Prompts
- **`templates/PROMPTS.md`** - Copy-paste ready prompts (v1.1)
  - Includes new Designer/Executor phase prompts
  - NORTH_STAR creation prompt
  - SUBPLAN and EXECUTION creation prompts
  - Synthesis prompts

---

## 🔄 Protocols (Workflow Process)

Follow these protocols for different scenarios:

### Starting Work
- **`protocols/IMPLEMENTATION_START_POINT.md`** - Entry point for all new work
  - When to create PLAN vs SUBPLAN
  - GrammaPlan decision tree
  - Naming conventions
  - Archive location setup

### Starting SUBPLAN Work (Designer Phase)
- **`protocols/CREATE_SUBPLAN.md`** - Mini-protocol for SUBPLAN creation (Designer)
  - SUBPLAN creation workflow
  - Execution strategy decision tree
  - Multi-execution planning guidance
  - Design phase checklist

### Starting EXECUTION Work (Executor Phase)
- **`protocols/CREATE_EXECUTION.md`** - Mini-protocol for EXECUTION creation (Executor)
  - Minimal context reading strategy
  - Parallelization context handling
  - Test-first development guidance
  - Circular debugging detection

### Resuming Work
- **`protocols/IMPLEMENTATION_RESUME.md`** - Resume paused work
  - Context restoration checklist
  - Dependency verification
  - Next achievement identification

### Completing Work
- **`protocols/IMPLEMENTATION_END_POINT.md`** - Complete work and archive
  - Completion checklist
  - Archive procedures
  - Backlog creation
  - ACTIVE_PLANS.md updates

---

## 🔧 Scripts (Automation)

Automated tools for document generation, validation, and management:

### Generation Scripts
- **`scripts/generation/generate_prompt.py`** - Orchestrator (detects workflow state)
- **`scripts/generation/generate_subplan_prompt.py`** - Designer phase prompts
- **`scripts/generation/generate_execution_prompt.py`** - Executor phase prompts (minimal context)

### Validation Scripts
- **`scripts/validation/check_north_star_size.py`** - NORTH_STAR size validation
- **`scripts/validation/check_grammaplan_size.py`** - GrammaPlan size validation
- **`scripts/validation/check_plan_size.py`** - PLAN size validation
- **`scripts/validation/check_execution_task_size.py`** - EXECUTION_TASK size validation
- **`scripts/validation/validate_subplan_executions.py`** - Multi-execution validation
- **`scripts/validation/validate_achievement_completion.py`** - Achievement completion validation

### Archive & Organization Scripts
- **`scripts/archiving/manual_archive.py`** - User-controlled on-demand archiving
- **`scripts/archiving/archive_completed.py`** - Archive completed work (called by END_POINT)

---

## 📇 Index & Discovery

- **`index/FILE-INDEX.md`** - Central catalog of all methodology files
  - Organized by type and location
  - Quick links to frequently accessed documents
  - Statistics on active work

---

## 🚀 Quick Start by Scenario

### Scenario 1: Starting New Feature Work
1. Check `ACTIVE_PLANS.md` for related work
2. Use `protocols/IMPLEMENTATION_START_POINT.md` to create PLAN
3. Use `templates/PLAN-TEMPLATE.md` (copy-paste)
4. For each achievement, use `protocols/CREATE_SUBPLAN.md`
5. Reference `guides/SUBPLAN-WORKFLOW-GUIDE.md` for 4-phase workflow

### Scenario 2: Strategic Work
1. Review `guides/NORTH-STAR-GUIDE.md`
2. Use `templates/NORTH_STAR-TEMPLATE.md` (copy-paste)
3. Create in `work-space/north-stars/`
4. Reference from child GrammaPlans/PLANs

### Scenario 3: Large Coordination
1. Review `guides/GRAMMAPLAN-GUIDE.md`
2. Use `templates/GRAMMAPLAN-TEMPLATE.md` (copy-paste)
3. Create in `work-space/grammaplans/`
4. Track 4-6 child PLANs

### Scenario 4: Context for New LLM Session
1. Read `LLM-METHODOLOGY.md` (highlights only)
2. Read `METHODOLOGY-EVOLUTION-v2.0.md` if new to v2.0
3. Read relevant guide (NORTH-STAR, GRAMMAPLAN, SUBPLAN, etc.)
4. Refer to appropriate template and protocol

---

## 📊 Key Statistics

- **Active GrammaPlans**: 6
- **Active PLANs**: 17+
- **Active SUBPLANs**: 30+
- **Active EXECUTION_TASKs**: 31+
- **Archived Work**: documentation/archive/

---

## 🔍 File Organization

```
LLM/
├── README.md                  # This file
├── LLM-METHODOLOGY.md        # Core methodology
├── protocols/                # Workflow protocols
│   ├── IMPLEMENTATION_START_POINT.md
│   ├── IMPLEMENTATION_RESUME.md
│   ├── IMPLEMENTATION_END_POINT.md
│   ├── CREATE_SUBPLAN.md     # Designer phase
│   └── CREATE_EXECUTION.md   # Executor phase
├── guides/                   # How-to guides
│   ├── NORTH-STAR-GUIDE.md
│   ├── GRAMMAPLAN-GUIDE.md
│   ├── SUBPLAN-WORKFLOW-GUIDE.md
│   └── FOCUS-RULES.md
├── templates/                # Copy-paste templates
│   ├── NORTH_STAR-TEMPLATE.md
│   ├── GRAMMAPLAN-TEMPLATE.md
│   ├── PLAN-TEMPLATE.md
│   ├── SUBPLAN-TEMPLATE.md
│   ├── EXECUTION_TASK-TEMPLATE.md
│   └── PROMPTS.md
├── scripts/                  # Automation tools
│   ├── generation/
│   ├── validation/
│   └── archiving/
└── index/                    # Discovery & indexing
    └── FILE-INDEX.md
```

---

## 🎓 What to Read First

**New to the methodology?**
1. Start: `LLM-METHODOLOGY.md` (overview)
2. Read: `guides/SUBPLAN-WORKFLOW-GUIDE.md` (core workflow)
3. Refer: Relevant template (PLAN, SUBPLAN, EXECUTION)
4. Use: Relevant protocol (START_POINT, CREATE_SUBPLAN, etc.)

**Upgrading from v1.0 to v2.0?**
1. Read: `METHODOLOGY-EVOLUTION-v2.0.md` (what changed)
2. Read: `guides/NORTH-STAR-GUIDE.md` (new document type)
3. Review: `guides/SUBPLAN-WORKFLOW-GUIDE.md` (workflow changes)
4. Check: Updated templates and protocols

**Specific Task?**
- Check `index/FILE-INDEX.md` for relevant documents
- Use `templates/PROMPTS.md` for copy-paste ready prompts
- Reference appropriate guide and protocol

---

## 📞 Need Help?

- **Understanding methodology**: See `LLM-METHODOLOGY.md`
- **Creating specific document**: See relevant template + guide
- **Following workflow**: See relevant protocol
- **Discovering files**: See `index/FILE-INDEX.md`
- **What changed in v2.0**: See `METHODOLOGY-EVOLUTION-v2.0.md`

---

**Last Updated**: November 9, 2025  
**Version**: 2.0  
**Status**: 🚀 Production Ready
