# North Stars Directory

**Purpose**: Strategic vision documents that "float above the funnel, illuminating it"

**Document Type**: NORTH_STAR documents (800-2,000 lines)

**Location**: `work-space/north-stars/`

---

## 🌟 What Are North Stars?

NORTH_STAR documents provide strategic vision and guiding principles for domains, systems, or initiatives. They sit at the top of the methodology hierarchy, above GrammaPlans and PLANs.

**Characteristics**:
- **Strategic vision**: Desired future state
- **Core principles**: 5-10+ principles that guide decisions
- **Living documents**: Evolve as understanding deepens
- **Coordinating** (optional): May coordinate GrammaPlans/PLANs
- **Inspiring**: Energize and align work

**Size**: 800-2,000 lines (larger than GrammaPlan to allow comprehensive vision)

---

## 📋 Naming Convention

**Format**: `NORTH_STAR_[NAME].md`

**Examples**:
- `NORTH_STAR_LLM-DEVELOPMENT-PHILOSOPHY.md`
- `NORTH_STAR_GRAPHRAG-EXCELLENCE-VISION.md`
- `NORTH_STAR_YOUTUBE-RAG-STRATEGIC-VISION.md`

**Rules**:
- Prefix: `NORTH_STAR_` (required)
- Name: ALL-CAPS-WITH-HYPHENS
- Suffix: `.md`
- Keep name descriptive but concise (3-5 words)

---

## 🎯 When to Create a North Star

**Create NORTH_STAR when**:
- Documenting strategic vision for domain
- Articulating 5-10+ core principles
- Providing long-term direction (years)
- Coordinating multiple GrammaPlans (optional)
- Need to inspire and align work

**Don't create NORTH_STAR when**:
- Coordinating specific PLANs only → Use GrammaPlan
- Defining specific achievements → Use PLAN
- Only 1-2 principles → Add to PLAN or GrammaPlan
- Tactical work → Use PLAN or SUBPLAN

**Decision Guide**: See `LLM/guides/NORTH-STAR-GUIDE.md`

---

## 🏗️ Creating a North Star

**1. Use Template**:
```bash
cp LLM/templates/NORTH_STAR-TEMPLATE.md work-space/north-stars/NORTH_STAR_[NAME].md
```

**2. Fill Sections**:
- Strategic Vision (2-4 paragraphs)
- Core Principles (5-10+, with explanations)
- Current State (honest assessment)
- Evolution History (track learning)
- Coordination (if coordinating GrammaPlans)

**3. Review**:
- Does vision inspire?
- Are principles actionable?
- Is current state honest?
- Would this guide decisions?

**4. Reference**:
- Link from GrammaPlans/PLANs
- Reference in related documents
- Communicate to stakeholders

**Full Guide**: `LLM/guides/NORTH-STAR-GUIDE.md`

---

## 📊 Hierarchy Position

```
       ⭐ NORTH_STAR (800-2,000 lines)
      "Floats above, illuminates"
      Strategic vision + principles
          /         |         \
     GRAMMAPLAN  GRAMMAPLAN   PLAN
     (coordinate) (coordinate) (execute)
       600-1,500    600-1,500   300-900
          |            |          |
        PLAN          PLAN      SUBPLAN
        300-900       300-900   200-600
          |             |          |
       SUBPLAN       SUBPLAN    EXECUTION
       200-600       200-600     <200
```

**NORTH_STAR is Top Tier**:
- Provides vision for GrammaPlans
- Guides PLANs with principles
- Inspires all work in domain
- Transcends specific projects

---

## 🔄 Maintaining North Stars

**Review Frequency**: Quarterly (every 3 months)

**Review Questions**:
- Does vision still inspire?
- Are principles still relevant?
- Has understanding shifted?
- Do current initiatives align?
- Should vision evolve?

**Update Process**:
1. Identify need for evolution
2. Draft updated vision/principles
3. Review with stakeholders
4. Update north star document
5. Add version to Evolution History
6. Communicate changes
7. Update aligned documents

**Evolution**: Track in "Evolution History" section (don't delete old versions)

---

## 📁 Current North Stars

**Active**:
- (None yet - this is the first achievement creating the infrastructure!)

**Potential Candidates** (to be migrated):
- `PLAN_STRUCTURED-LLM-DEVELOPMENT.md` (2,099 lines, extensive principles)
  - Could become NORTH_STAR_LLM-DEVELOPMENT-METHODOLOGY
  - Has strategic vision and 10+ principles
  - Referenced by many PLANs

**Future North Stars**:
- NORTH_STAR_GRAPHRAG-EXCELLENCE (from GRAMMAPLAN)
- NORTH_STAR_YOUTUBE-RAG-VISION (system-wide vision)

---

## 🗄️ Archiving

**When to Archive**:
- Vision fully achieved (rare)
- Domain no longer relevant
- Superseded by new north star
- Merged into larger vision

**Archive Location**: `documentation/archive/north-stars/[NAME]-[DATE]/`

**Archive Structure**:
```
documentation/archive/north-stars/[NAME]-[DATE]/
├── NORTH_STAR_[NAME].md
├── INDEX.md (references to aligned GrammaPlans/PLANs)
└── MIGRATION-NOTES.md (if superseded)
```

**Process**:
1. Move north star to archive location
2. Update references in other documents
3. Create INDEX.md linking related work
4. Create MIGRATION-NOTES.md if superseded
5. Update this README (move from Active to Archived)

---

## 📚 Documentation

**Templates**:
- `LLM/templates/NORTH_STAR-TEMPLATE.md` - Create new north stars

**Guides**:
- `LLM/guides/NORTH-STAR-GUIDE.md` - When and how to create
- `LLM-METHODOLOGY.md` - Full methodology overview

**Related Folders**:
- `work-space/grammaplans/` - Strategic coordination documents
- `work-space/plans/` - Tactical execution documents
- `work-space/subplans/` - Approach documents
- `work-space/execution/` - Journey logs

---

## 🎯 Best Practices

**Writing**:
- Start with vision (most important)
- Explain principles (don't just list)
- Be honest about current state
- Track evolution (living document)
- Make it inspiring

**Size**:
- Target: 1,000-1,500 lines (typical)
- Minimum: 800 lines (need space for vision)
- Maximum: 2,000 lines (beyond this, consider splitting)
- If <800: Might be GrammaPlan instead
- If >2,000: Consider hierarchy of north stars

**Audience**:
- Write for intelligent newcomer
- Provide context, don't assume knowledge
- Be inspiring but practical
- Guide decisions, don't prescribe

**Maintenance**:
- Review quarterly
- Update proactively
- Track evolution history
- Communicate changes

---

## 🆘 Questions?

**"Should I create a NORTH_STAR?"**
→ See decision tree in `LLM/guides/NORTH-STAR-GUIDE.md`

**"How do I start?"**
→ Use `LLM/templates/NORTH_STAR-TEMPLATE.md`

**"NORTH_STAR vs. GrammaPlan?"**
→ NORTH_STAR = vision + principles; GrammaPlan = coordination

**"How big should it be?"**
→ 800-2,000 lines; typically 1,000-1,500 for mature vision

**"How often to update?"**
→ Quarterly reviews + trigger-based updates

---

**Status**: Infrastructure complete, ready for first north stars!  
**Created**: 2025-11-08  
**Maintained By**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md

