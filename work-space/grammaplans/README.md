# GrammaPlans Directory

**Purpose**: Strategic coordination documents that orchestrate multiple child PLANs

**Document Type**: GRAMMAPLAN documents (600-1,500 lines)

**Location**: `work-space/grammaplans/`

---

## 📋 What Are GrammaPlans?

GrammaPlans coordinate 3-8 child PLANs working toward a unified strategic goal. They provide strategic orchestration, dependency management, and timeline coordination.

**Characteristics**:
- **Strategic coordination**: Orchestrates multiple PLANs
- **Dependency management**: Defines execution order
- **Timeline coordination**: Manages parallel/sequential work
- **Size**: 600-1,500 lines (strategic coordination needs space)

**vs. NORTH_STAR**: 
- GrammaPlan = Strategic coordination (WHAT + orchestration)
- NORTH_STAR = Strategic vision (WHY + principles)

**vs. PLAN**:
- GrammaPlan = Coordinates 3-8 PLANs
- PLAN = Defines 5-20 achievements

---

## 📋 Naming Convention

**Format**: `GRAMMAPLAN_[FEATURE].md`

**Examples**:
- `GRAMMAPLAN_GRAPHRAG-PIPELINE-EXCELLENCE.md`
- `GRAMMAPLAN_YOUTUBE-RAG-SYSTEM-INTEGRATION.md`
- `GRAMMAPLAN_LLM-METHODOLOGY-V2.md`

**Rules**:
- Prefix: `GRAMMAPLAN_` (required)
- Name: ALL-CAPS-WITH-HYPHENS
- Suffix: `.md`
- Keep name descriptive but concise (3-5 words)

---

## 🎯 When to Create a GrammaPlan

**Create GRAMMAPLAN when**:
- Coordinating 3-8 related PLANs
- Work spans 4+ domains
- Natural parallelism exists
- Strategic coordination needed
- Timeline is months to a year

**Don't create GRAMMAPLAN when**:
- Single PLAN sufficient → Use PLAN
- Strategic vision needed → Use NORTH_STAR
- Only 1-2 PLANs → Use PLAN with dependencies
- Tactical work → Use PLAN

**Decision Guide**: See `LLM/guides/GRAMMAPLAN-GUIDE.md`

**Criteria**: >900 lines OR >40 hours OR 4+ domains

---

## 📊 Size Guidelines

**Size Range**: 600-1,500 lines

**Target Sizes**:
- **600-999 lines**: Typical GrammaPlan (coordinates 3-5 PLANs)
- **1,000-1,499 lines**: Large GrammaPlan (coordinates 6-8 PLANs) - **Warning**: Consider splitting
- **1,500+ lines**: **Error** - Must split into multiple GrammaPlans or convert to NORTH_STAR

**Why Size Matters**:
- Too small (<600): Might be single PLAN instead
- Too large (>1,500): Loses focus, should split or become NORTH_STAR
- Sweet spot (600-1,000): Clear coordination, manageable scope

**Validation**: Use `LLM/scripts/validation/check_grammaplan_size.py`

---

## 🏗️ Creating a GrammaPlan

**1. Use Template**:
```bash
cp LLM/templates/GRAMMAPLAN-TEMPLATE.md work-space/grammaplans/GRAMMAPLAN_[NAME].md
```

**2. Fill Sections**:
- Strategic goal and coordination strategy
- Child PLANs (3-8 PLANs with dependencies)
- Timeline and execution order
- Cross-cutting concerns
- Success criteria

**3. Review**:
- Does it coordinate 3-8 PLANs?
- Are dependencies clear?
- Is timeline realistic?
- Does size fit (600-1,500 lines)?

**Full Guide**: `LLM/guides/GRAMMAPLAN-GUIDE.md`

---

## 📊 Hierarchy Position

```
       ⭐ NORTH_STAR (800-2,000 lines)
      "Strategic vision + principles"
          /         |         \
     GRAMMAPLAN  GRAMMAPLAN   PLAN
     (coordinate) (coordinate) (execute)
       600-1,500    600-1,500   300-900
          |            |          |
        PLAN          PLAN      SUBPLAN
        300-900       300-900   200-600
```

**GrammaPlan Position**:
- Below NORTH_STAR (if exists)
- Coordinates multiple PLANs
- Provides strategic orchestration
- Manages dependencies and timeline

---

## 🔄 Maintaining GrammaPlans

**Review Frequency**: As child PLANs progress

**Review Questions**:
- Are child PLANs on track?
- Do dependencies need adjustment?
- Is timeline realistic?
- Should GrammaPlan split or evolve?

**Update Process**:
1. Monitor child PLAN progress
2. Update dependencies as needed
3. Adjust timeline if necessary
4. Document learnings

**Evolution**: GrammaPlans evolve as child PLANs progress and dependencies clarify

---

## 📁 Current GrammaPlans

**Active**:
- `GRAMMAPLAN_GRAPHRAG-PIPELINE-EXCELLENCE.md` (coordinates 6 PLANs)
- `GRAMMAPLAN_YOUTUBE-RAG-SYSTEM-INTEGRATION.md` (coordinates multiple PLANs)

**Note**: Existing GrammaPlans in `work-space/plans/` should be moved here when convenient (not blocking).

---

## 🗄️ Archiving

**When to Archive**:
- All child PLANs complete
- Strategic goal achieved
- Superseded by new GrammaPlan
- No longer coordinating work

**Archive Location**: `documentation/archive/[FEATURE-NAME]/planning/]`

**Archive Structure**:
```
documentation/archive/[FEATURE-NAME]/
├── planning/
│   └── GRAMMAPLAN_[NAME].md
├── child-plans/ (links to child PLAN archives)
└── summary/
    └── [FEATURE]-COMPLETE.md
```

**Process**:
1. Move GrammaPlan to archive location
2. Update references in other documents
3. Create INDEX.md linking child PLANs
4. Create completion summary
5. Update this README (move from Active to Archived)

---

## 📚 Documentation

**Templates**:
- `LLM/templates/GRAMMAPLAN-TEMPLATE.md` - Create new GrammaPlans

**Guides**:
- `LLM/guides/GRAMMAPLAN-GUIDE.md` - When and how to create
- `LLM-METHODOLOGY.md` - Full methodology overview

**Validation**:
- `LLM/scripts/validation/check_grammaplan_size.py` - Size validation

**Related Folders**:
- `work-space/north-stars/` - Strategic vision documents
- `work-space/plans/` - Tactical execution documents
- `work-space/subplans/` - Approach documents
- `work-space/execution/` - Journey logs

---

## 🎯 Best Practices

**Coordination**:
- Keep child PLAN count manageable (3-8)
- Clear dependencies and timeline
- Regular progress reviews
- Adjust as needed

**Size Management**:
- Target 600-1,000 lines (sweet spot)
- Warning at 1,000 lines (consider splitting)
- Error at 1,500 lines (must split or convert)
- Use validation script

**Content**:
- Focus on coordination (not execution details)
- Strategic orchestration (not tactical plans)
- Dependency management (not implementation)
- Timeline and milestones (not day-to-day)

**Maintenance**:
- Update as child PLANs progress
- Adjust dependencies when needed
- Document learnings
- Keep current

---

## 🆘 Questions?

**"Should I create a GRAMMAPLAN?"**
→ See decision criteria in `LLM/guides/GRAMMAPLAN-GUIDE.md`

**"How do I start?"**
→ Use `LLM/templates/GRAMMAPLAN-TEMPLATE.md`

**"GRAMMAPLAN vs. NORTH_STAR?"**
→ GRAMMAPLAN = coordination; NORTH_STAR = vision

**"How big should it be?"**
→ 600-1,500 lines; typically 600-1,000 for good coordination

**"When to split?"**
→ At 1,000 lines consider, at 1,500 lines must split

---

**Status**: Infrastructure complete, ready for GrammaPlans!  
**Created**: 2025-11-08  
**Maintained By**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md

