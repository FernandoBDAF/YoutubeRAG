# NORTH_STAR: [NAME]

**Status**: 🌟 Strategic Vision  
**Created**: [DATE]  
**Strategic Purpose**: [One-line statement of what this north star illuminates]  
**Scope**: [What systems/domains/initiatives this provides vision for]

**File Location**: Save this file in `work-space/north-stars/NORTH_STAR_[NAME].md`

---

## 🌟 What is a NORTH_STAR?

**For LLMs/Developers**: A NORTH_STAR document provides strategic vision and guiding principles for a domain, system, or initiative. It "floats above the funnel, illuminating it" - providing high-level direction without prescribing tactical execution.

**When to Use**: See `LLM/guides/NORTH-STAR-GUIDE.md`

**Key Characteristics**:

- **Strategic** (not tactical): Focuses on WHY and WHAT, not HOW
- **Vision-driven**: Paints picture of desired future state
- **Principle-based**: Provides principles that guide decisions
- **Coordinating** (optional): May coordinate multiple GrammaPlans/PLANs
- **Living**: Evolves as understanding deepens

**Size**: 800-2,000 lines (larger than GrammaPlan to allow for comprehensive vision and principles)

**Hierarchy Position**: Top tier, above GrammaPlans and PLANs

```
       ⭐ NORTH_STAR (800-2,000 lines)
      "Floats above, illuminates"
          /         |         \
     GRAMMAPLAN  GRAMMAPLAN   PLAN
     (coordinate) (coordinate) (execute)
```

**vs. GrammaPlan**:

- NORTH_STAR = Strategic vision + principles (WHY)
- GrammaPlan = Strategic coordination (WHAT + orchestration)
- GrammaPlan focuses on coordinating work; NORTH_STAR focuses on inspiring vision

**vs. PLAN**:

- NORTH_STAR = Long-term vision, principles
- PLAN = Short-term achievements, deliverables
- PLAN executes; NORTH_STAR guides

---

## 🎯 Strategic Vision

**[Write 2-4 paragraphs of strategic vision]**

**What to Include**:

- Where we're going (desired future state)
- Why it matters (value proposition)
- What success looks like (vision of excellence)
- How this fits into larger context

**What NOT to Include**:

- Tactical plans (that's for PLANs)
- Specific timelines (strategic vision transcends near-term)
- Detailed implementations (that's for SUBPLANs)

**Example Topics**:

- "Transform our development process to be learning-first..."
- "Build a knowledge graph that deeply understands..."
- "Create a methodology that scales with system complexity..."

**Tone**: Aspirational but grounded, inspiring but realistic

---

## 💎 Core Principles

**[List 5-10 core principles that guide decisions and actions]**

**Format** (for each principle):

### Principle N: [Principle Name]

**Statement**: [One-sentence principle]

**Explanation**: [2-3 paragraphs explaining the principle]

- Why this principle matters
- How it guides decisions
- What it looks like in practice

**Anti-Pattern**: [What violating this principle looks like]

**Example** (from real work):

### Principle 1: Learning-First Development

**Statement**: Optimize for learning and understanding, not just features and timelines.

**Explanation**:
When building complex systems (like GraphRAG), deep understanding is more valuable than quick features. A developer who understands WHY entities merge will make better architectural decisions than one who just follows recipes.

This principle guides us to invest in observability, documentation, and experimentation infrastructure. When choosing between "ship feature X" and "understand system behavior Y", we often choose understanding - because understanding compounds.

**Anti-Pattern**: Rushing to ship features without understanding, accumulating technical debt and mysteries that slow future work.

---

## 🔗 Coordination (Optional - if coordinating GrammaPlans/PLANs)

**[Describe how this north star coordinates multiple initiatives]**

**If Coordinating GrammaPlans**:

### Child GrammaPlans

| GrammaPlan         | Status   | Purpose   | Alignment with Vision  |
| ------------------ | -------- | --------- | ---------------------- |
| GRAMMAPLAN\_[NAME] | [Status] | [Purpose] | [How it serves vision] |

**If Coordinating PLANs**:

### Child PLANs

| PLAN         | Status   | Purpose   | Alignment with Principles |
| ------------ | -------- | --------- | ------------------------- |
| PLAN\_[NAME] | [Status] | [Purpose] | [Which principles]        |

**Coordination Strategy**:

- [How work is coordinated]
- [How decisions are made]
- [How principles are applied]

**If Not Coordinating**: Remove this section or state "This north star provides vision only, not work coordination."

---

## 📊 Current State

**[Describe where we are today relative to the vision]**

**What to Include**:

### Current Reality

- [What we have today]
- [What's working well]
- [What gaps exist]

### Progress Toward Vision

- [How far we've come]
- [What we've learned]
- [What remains]

### Challenges

- [Obstacles to vision]
- [Tensions to resolve]
- [Decisions to make]

**Tone**: Honest assessment, neither overly optimistic nor pessimistic

---

## 🔄 Evolution History

**[Track how this vision has evolved over time]**

**Format**:

### Version 1.0 - [Date]

**Vision at This Time**: [What the vision was]

**Context**: [What prompted this vision]

**Status**: [Initial/Superseded/Current]

### Version 2.0 - [Date]

**How Vision Evolved**: [What changed and why]

**Key Learnings**: [What we learned that prompted evolution]

**Status**: [Current/Superseded]

**Purpose**:

- Track how understanding deepens
- Show that vision is living (not static)
- Preserve historical context
- Demonstrate learning journey

---

## 🎓 Philosophy and Mental Models (Optional)

**[Deeper philosophical foundations, if helpful]**

**Mental Models**:

- [Key mental models that shape thinking]
- [Analogies that illuminate concepts]
- [Frameworks that guide decisions]

**Philosophical Foundations**:

- [Deeper "why" behind principles]
- [Values that underpin vision]
- [Beliefs about the domain]

**Example Topics**:

- "The Funnel Metaphor: Strategist → Planner → Designer → Executor"
- "Test-Driven Development as Learning Tool"
- "Observability as Foundation for Understanding"

---

## 🌐 Cross-Cutting Themes (Optional)

**[Themes that appear across multiple areas]**

**Example Themes**:

- Quality over speed
- Understanding over automation
- Principles over rules
- Iteration over perfection

**For Each Theme**:

- Why it matters
- How it manifests
- How to recognize it
- How to apply it

---

## 📚 References & Context

**Related North Stars**:

- [Other NORTH_STAR documents]

**Key Documents**:

- [GrammaPlans aligned with this vision]
- [PLANs that implement principles]
- [Analyses that informed vision]

**External References**:

- [Books, papers, philosophies that influenced thinking]
- [Other methodologies studied]
- [Experts consulted]

---

## 🎯 How to Use This North Star

**For Developers**:

- Read when starting work in this domain
- Consult when making architectural decisions
- Reference when principles conflict
- Contribute to evolution as you learn

**For LLMs**:

- Read to understand strategic context
- Use principles to guide implementation decisions
- Align tactical work with strategic vision
- Propose principle-driven solutions

**For Planners**:

- Ensure PLANs align with vision
- Check GrammaPlans serve strategic goals
- Validate achievements embody principles
- Propose evolution when vision shifts

**For Strategists**:

- Review quarterly for relevance
- Update as understanding deepens
- Ensure coordination serves vision
- Communicate vision broadly

---

## 🔄 Maintenance

**Review Frequency**: Quarterly (every 3 months)

**Review Questions**:

- [ ] Does vision still inspire?
- [ ] Are principles still relevant?
- [ ] Has understanding shifted?
- [ ] Do current initiatives align?
- [ ] Should vision evolve?

**Update Triggers**:

- Major learnings from work
- Shift in strategic context
- New principles discovered
- Vision no longer inspiring
- Misalignment with reality

**Evolution Process**:

1. Identify need for evolution
2. Draft updated vision
3. Review with stakeholders
4. Update north star
5. Add to Evolution History
6. Communicate changes

---

## 📝 Template Usage Notes

**Creating Your North Star**:

1. **Start with Vision** (most important):

   - What are we trying to achieve?
   - Why does it matter?
   - What does success look like?

2. **Extract Principles**:

   - What guides our decisions?
   - What patterns have we learned?
   - What do we believe deeply?

3. **Document Current State** (honest assessment):

   - Where are we today?
   - What's working?
   - What gaps exist?

4. **Track Evolution** (capture learning):

   - How has thinking evolved?
   - What prompted changes?
   - What did we learn?

5. **Add Coordination** (if applicable):
   - What initiatives does this guide?
   - How are they coordinated?
   - How do they serve vision?

**Size Guidance**:

- Minimum: 800 lines (need space for comprehensive vision)
- Target: 1,000-1,500 lines (typical for mature north star)
- Maximum: 2,000 lines (beyond this, consider splitting)
- If <800 lines: Might be GrammaPlan (coordination) rather than NORTH_STAR (vision)
- If >2,000 lines: Consider splitting into multiple north stars or creating hierarchy

**Tone**:

- Strategic (not tactical)
- Aspirational (but grounded)
- Principled (not prescriptive)
- Inspiring (but honest)

**What Makes a Good North Star**:

- ✅ Provides clear vision of desired future
- ✅ Articulates principles that guide decisions
- ✅ Inspires and energizes work
- ✅ Honest about current state and challenges
- ✅ Evolves as understanding deepens
- ❌ Prescribes specific implementations
- ❌ Focuses on near-term tactics
- ❌ Becomes outdated and static
- ❌ Too abstract to be actionable

---

## 📊 Size and Scope Guidelines

**When to Use NORTH_STAR** (vs. other document types):

```
Is this strategic vision/principles?
  Yes → NORTH_STAR
  No  → Is it coordinating multiple PLANs?
         Yes → GrammaPlan
         No  → Is it defining achievements?
                Yes → PLAN
                No  → Is it defining approach?
                       Yes → SUBPLAN
```

**NORTH_STAR Characteristics**:

- Strategic vision (2-4 paragraphs minimum)
- 5-10+ core principles with explanations
- Evolution history (living document)
- May coordinate GrammaPlans/PLANs (optional)
- 800-2,000 lines typical

**Red Flags** (might not be NORTH_STAR):

- Focused on specific deliverables → Probably PLAN
- Coordinating work without vision → Probably GrammaPlan
- Tactical "how-to" content → Probably SUBPLAN or Guide
- <800 lines and mostly coordination → Probably GrammaPlan

---

**Ready to Create**: Replace [PLACEHOLDERS], fill sections, align with vision, inspire with principles!

**For Help**: See `LLM/guides/NORTH-STAR-GUIDE.md`

**Archive Location** (when superseded): `documentation/archive/north-stars/[NAME]-[DATE]/`
