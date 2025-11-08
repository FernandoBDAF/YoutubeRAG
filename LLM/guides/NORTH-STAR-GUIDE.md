# NORTH_STAR Guide: Strategic Vision Documents

**Purpose**: Guide for when and how to create NORTH_STAR documents  
**Audience**: LLM developers, project strategists, methodology users  
**Version**: 1.0  
**Created**: 2025-11-08

---

## 🌟 What is a NORTH_STAR?

**Definition**: A NORTH_STAR document provides strategic vision and guiding principles for a domain, system, or initiative. It "floats above the funnel, illuminating it."

**Metaphor**: Like a north star in the night sky:

- Provides direction (strategic vision)
- Doesn't move (stable principles)
- Illuminates path (guides decisions)
- Visible from anywhere (accessible to all)
- Above the terrain (strategic, not tactical)

**Key Characteristics**:

- **Strategic** (not tactical)
- **Vision-driven** (desired future state)
- **Principle-based** (guides decisions)
- **Living** (evolves with understanding)
- **Inspiring** (energizes work)

**Size**: 800-2,000 lines (needs space for comprehensive vision and principles)

---

## 🤔 When to Create a NORTH_STAR

### Decision Tree

```
Question 1: Do you need to document strategic vision and principles?
├─ No  → You probably don't need a NORTH_STAR
└─ Yes → Question 2

Question 2: Is this vision large enough for 5+ core principles?
├─ No  → Consider adding to existing NORTH_STAR or using PLAN intro
└─ Yes → Question 3

Question 3: Will this vision guide multiple GrammaPlans or PLANs?
├─ No  → Question 4
└─ Yes → NORTH_STAR (coordination type)

Question 4: Does this vision transcend specific projects?
├─ No  → Probably PLAN with strong vision section
└─ Yes → NORTH_STAR (vision type)
```

### Use NORTH_STAR When:

✅ **Strategic Vision Needed**:

- Defining philosophy for a domain
- Articulating principles for a system
- Providing long-term direction
- Inspiring and aligning work

✅ **Multiple Principles to Document**:

- 5-10+ core principles
- Each principle needs explanation
- Principles guide tactical decisions
- Anti-patterns worth documenting

✅ **Coordination Across Initiatives**:

- Multiple GrammaPlans serving one vision
- Multiple PLANs implementing principles
- Need to align disparate work
- Strategic coherence required

✅ **Living Strategic Document**:

- Vision will evolve with learning
- Understanding deepening over time
- Want to track evolution history
- Strategic context changes

### Don't Use NORTH_STAR When:

❌ **Tactical Work**:

- Defining specific achievements → Use PLAN
- Coordinating specific PLANs only → Use GrammaPlan
- Describing implementation approach → Use SUBPLAN

❌ **Too Small**:

- Only 1-2 principles → Add to PLAN or GrammaPlan
- <800 lines naturally → Probably not strategic enough
- Just coordination → GrammaPlan is better fit

❌ **Too Specific**:

- Focused on single project → Use PLAN with vision
- Near-term only (< 6 months) → Too tactical for NORTH_STAR
- Specific deliverables → Definitely PLAN

---

## 📊 NORTH_STAR vs. GrammaPlan vs. PLAN

### Quick Comparison

| Aspect        | NORTH_STAR          | GrammaPlan             | PLAN                        |
| ------------- | ------------------- | ---------------------- | --------------------------- |
| **Purpose**   | Strategic vision    | Coordinate work        | Define achievements         |
| **Focus**     | WHY                 | WHAT + Orchestration   | HOW + WHEN                  |
| **Size**      | 800-2,000 lines     | 600-1,500 lines        | 300-900 lines               |
| **Content**   | Vision + Principles | Child PLANs + Strategy | Achievements + Deliverables |
| **Lifespan**  | Years               | Months                 | Weeks/Months                |
| **Evolution** | Evolves slowly      | Evolves with PLANs     | Static after planning       |
| **Audience**  | All stakeholders    | Project team           | Execution team              |

### Detailed Differences

**NORTH_STAR**:

- **Essence**: "Here's where we're going and why"
- **Contains**: Vision (2-4 paragraphs), Principles (5-10+), Philosophy
- **Example**: NORTH_STAR_LLM-DEVELOPMENT-PHILOSOPHY (development principles)
- **Coordinates**: May coordinate GrammaPlans (optional), provides vision for PLANs
- **Updates**: Evolves as understanding deepens (quarterly reviews)

**GrammaPlan**:

- **Essence**: "Here's how we coordinate 3-8 PLANs to achieve this"
- **Contains**: Child PLANs, Dependencies, Timeline, Coordination strategy
- **Example**: GRAMMAPLAN_GRAPHRAG-PIPELINE-EXCELLENCE (coordinates 6 PLANs)
- **Coordinates**: 3-8 child PLANs with dependencies and timeline
- **Updates**: Updates as child PLANs progress

**PLAN**:

- **Essence**: "Here are 5-20 achievements to accomplish this feature"
- **Contains**: Priority-ordered achievements, deliverables, subplan tracking
- **Example**: PLAN_ENTITY-RESOLUTION-REFACTOR (refactor one stage)
- **Coordinates**: Nothing (executed directly)
- **Updates**: Achievements added/reordered during execution

### Hierarchy Visualization

```
      ⭐ NORTH_STAR (Vision + Principles)
     "Where we're going and why"
      |
      |  [Inspires and guides]
      ↓
     📋 GRAMMAPLAN (Coordination)
    "What we're building and when"
    /    |    \
   /     |     \
  PLAN  PLAN  PLAN (Achievements)
  "How we'll build it"
   |
   ↓
  SUBPLAN (Approach for one achievement)
   |
   ↓
  EXECUTION_TASK (Journey log)
```

### When Each is the Right Choice

**Choose NORTH_STAR if**:

- You're defining strategic vision for a domain
- You have 5-10+ principles to document
- Vision transcends specific projects
- Need to inspire and align across initiatives
- Will guide work for years

**Choose GrammaPlan if**:

- Coordinating 3-8 related PLANs
- Work spans 4+ domains
- Natural parallelism exists
- Strategic coordination needed
- Timeline is months to a year

**Choose PLAN if**:

- Defining specific feature or refactor
- 5-20 achievements to accomplish
- Single domain focus
- Tactical execution needed
- Timeline is weeks to months

---

## ✍️ How to Write a NORTH_STAR

### Step 1: Start with Vision (Most Important)

**The Vision Section Makes or Breaks a North Star**

**Good Vision Characteristics**:

- **Aspirational**: Paints picture of desired future
- **Specific Enough**: Not "we'll be better" but "we'll have X characteristic"
- **Grounded**: Achievable, not fantasy
- **Inspiring**: Makes you want to work toward it
- **Strategic**: Transcends tactical details

**Writing Process**:

1. **Free Write** (30 minutes):

   - Where do we want to be in 2-3 years?
   - What does excellence look like in this domain?
   - Why does this matter?
   - What would success feel like?

2. **Distill to Core** (30 minutes):

   - Pick 3-4 most important ideas
   - Expand each to paragraph
   - Connect to broader context
   - Make it inspiring but honest

3. **Test with Questions**:
   - Does this inspire me?
   - Is it clear where we're going?
   - Is it achievable?
   - Does it transcend current projects?
   - Would this guide decisions?

**Example Vision** (from GRAMMAPLAN_GRAPHRAG-PIPELINE-EXCELLENCE):

> "Transform the GraphRAG pipeline from 'working' to 'excellent' through a learning-first approach where every experiment, every data transformation, and every quality metric is visible, queryable, and drives continuous improvement."

**Why This Works**:

- Aspirational: "working" → "excellent"
- Specific: "visible, queryable, drives improvement"
- Grounded: Builds on existing pipeline
- Inspiring: "learning-first approach"
- Strategic: Not about specific features

### Step 2: Extract Core Principles

**Principles Guide Tactical Decisions**

**Good Principle Characteristics**:

- **Actionable**: Can guide real decisions
- **Memorable**: Stick in your mind
- **Testable**: Can recognize violations
- **Principled**: Not just pragmatic rules

**How to Find Principles**:

1. **Review Decisions**:

   - What decisions did we make?
   - Why did we make them?
   - What patterns emerge?
   - What do we believe deeply?

2. **Look for Patterns**:

   - What do successful projects have in common?
   - What mistakes do we keep avoiding?
   - What trade-offs do we consistently make?
   - What do we value most?

3. **Articulate as Principles**:
   - Turn patterns into statements
   - Explain WHY not just WHAT
   - Document anti-patterns
   - Provide examples

**Principle Structure**:

```markdown
### Principle N: [Catchy Name]

**Statement**: [One-sentence principle]

**Explanation**:
[Why this matters - 2-3 paragraphs]
[How it guides decisions]
[What it looks like in practice]

**Anti-Pattern**: [What violating this looks like]

**Example**: [Real example from work]
```

**Example Principle**:

### Principle 1: Observability Before Optimization

**Statement**: Always build observability infrastructure before attempting optimization.

**Explanation**:
You can't optimize what you can't measure. Without observability, optimization is guesswork - you might make things worse while thinking you're improving.

This principle guides us to invest in logging, metrics, and analysis tools before tuning performance. It prevents premature optimization and ensures improvements are data-driven.

In practice, this means when facing performance issues, the first step is always "can we see what's happening?" If not, build observability first.

**Anti-Pattern**: Tuning parameters blindly, making changes without measurements, claiming improvements without data.

**Example**: Before optimizing entity resolution, we built transformation logging and quality metrics. This let us see that fuzzy matching had 15% false positives, guiding us to adjust similarity thresholds data-driven rather than guessing.

### Step 3: Document Current State (Honest Assessment)

**Current State Grounds the Vision**

**What to Include**:

**Current Reality**:

- Where are we today?
- What's working well?
- What gaps exist between current and vision?

**Progress Toward Vision**:

- How far have we come?
- What milestones have we hit?
- What momentum exists?

**Challenges**:

- What obstacles remain?
- What tensions need resolution?
- What decisions are pending?

**Tone**: Honest but not defeatist, realistic but not pessimistic

**Why This Matters**: Grounds the vision in reality, shows progress is possible, identifies work needed

### Step 4: Track Evolution (Learning History)

**Evolution History Shows Learning**

**What to Document**:

- Initial vision (where we started)
- Major shifts (how vision evolved)
- Key learnings (what prompted changes)
- Current version (where we are now)

**Format**:

```markdown
### Version 1.0 - [Date]

**Vision**: [Initial vision]
**Context**: [Why this vision]
**Status**: Superseded

### Version 2.0 - [Date]

**Evolution**: [What changed]
**Learnings**: [Why it changed]
**Status**: Current
```

**Why This Matters**:

- Shows vision is living (not static)
- Captures learning journey
- Provides historical context
- Demonstrates growth

### Step 5: Add Coordination (If Applicable)

**Only if Coordinating GrammaPlans/PLANs**

**What to Document**:

- Which initiatives this north star guides
- How they serve the vision
- How they embody principles
- How they coordinate

**Table Format**:

| Initiative   | Status | Purpose   | Alignment              |
| ------------ | ------ | --------- | ---------------------- |
| GRAMMAPLAN_X | Active | [Purpose] | [How it serves vision] |
| PLAN_Y       | Paused | [Purpose] | [Which principles]     |

**If Not Coordinating**: Remove section or state "Vision only, not coordinating specific work."

---

## 🎯 Common Pitfalls and How to Avoid Them

### Pitfall 1: Too Tactical

**Problem**: Document reads like detailed plan, not strategic vision

**Symptoms**:

- Specific deliverables listed
- Timeline with dates
- Implementation details
- "How-to" instructions

**Fix**:

- Move deliverables to PLAN
- Remove timelines (strategic vision transcends dates)
- Replace "how" with "why"
- Elevate to principles

### Pitfall 2: Too Abstract

**Problem**: Document is philosophical but not actionable

**Symptoms**:

- No principles
- Vague vision
- Can't guide decisions
- Not inspiring

**Fix**:

- Add concrete principles
- Make vision more specific
- Add examples from real work
- Test: "Would this guide a decision?"

### Pitfall 3: Too Static

**Problem**: Document written once, never updated

**Symptoms**:

- Vision outdated
- Principles no longer relevant
- Current state not current
- No evolution history

**Fix**:

- Schedule quarterly reviews
- Add evolution history section
- Update as you learn
- Make it living

### Pitfall 4: Too Small

**Problem**: Document doesn't justify NORTH_STAR (should be GrammaPlan or PLAN)

**Symptoms**:

- <800 lines
- Only 1-2 principles
- Mostly coordination
- Could fit in PLAN

**Fix**:

- Expand principles (explain more)
- Add philosophy section
- Or convert to GrammaPlan
- Or add as PLAN vision section

### Pitfall 5: Wrong Audience

**Problem**: Written for experts only or too basic

**Symptoms**:

- Jargon without explanation
- Assumes deep context
- Or: Explains obvious things

**Fix**:

- Write for intelligent newcomer
- Explain domain concepts
- Provide context
- But don't over-explain

---

## 📚 Examples and Case Studies

### Example 1: LLM Development Methodology (If It Were NORTH_STAR)

**What It Would Contain**:

**Vision**:

- Future where LLM-assisted development is structured, traceable, and high-quality
- Developers and LLMs collaborate seamlessly
- Work is documented, learnings captured, quality assured

**Core Principles**:

- Achievement-based progress (clear milestones)
- Test-driven development (quality first)
- Iterative execution (learning captured)
- Complete documentation (knowledge preserved)
- Multi-agent coordination (specialized roles)

**Current State**:

- Methodology working well (10+ PLANs, 200+ achievements)
- Some pain points (size limits, workflow confusion)
- Evolution in progress (new hierarchy, workflows)

**Why This Would Be NORTH_STAR**: Provides vision and principles for entire development methodology, transcends specific projects, guides all work

### Example 2: GraphRAG Pipeline Excellence

**Actual** (GrammaPlan):

- GRAMMAPLAN_GRAPHRAG-PIPELINE-EXCELLENCE
- Coordinates 6 child PLANs
- Timeline and dependencies
- Strategic coordination

**Could Be NORTH_STAR If**:

- Focused more on "what is GraphRAG excellence?"
- Articulated 10+ principles of excellent knowledge graphs
- Provided vision transcending current pipeline
- Less coordination, more philosophy

**Why It's GrammaPlan Not NORTH_STAR**: Primarily coordinates specific work, has timelines, focuses on WHAT not WHY

### Example 3: When PLAN Should Be NORTH_STAR

**Red Flags a PLAN Should Be NORTH_STAR**:

- PLAN has 3+ pages of "Philosophy" section
- PLAN articulates 5-10 principles
- PLAN vision transcends the specific achievements
- PLAN is referenced by many other PLANs
- PLAN exceeds 1,500 lines mostly from principles

**Example**: PLAN_STRUCTURED-LLM-DEVELOPMENT (2,099 lines)

- Could be NORTH_STAR_LLM-DEVELOPMENT-PHILOSOPHY
- Has extensive principles and vision
- Transcends specific work
- Referenced by many PLANs

---

## 🔄 Maintaining North Stars

### Review Frequency

**Quarterly Reviews** (every 3 months):

- Read entire north star
- Ask: Does vision still inspire?
- Ask: Are principles still relevant?
- Ask: Has understanding shifted?
- Ask: Do current initiatives align?

**Trigger-Based Updates**:

- Major learnings from work
- Strategic context shift
- New principles discovered
- Vision no longer inspiring
- Misalignment detected

### Evolution Process

**When to Evolve**:

- Understanding has deepened
- Context has changed
- Principles refined
- Vision expanded/focused

**How to Evolve**:

1. Identify what needs updating
2. Draft changes (new vision/principles)
3. Review with stakeholders
4. Update north star document
5. Add version to Evolution History
6. Communicate changes to users
7. Update aligned GrammaPlans/PLANs

### Archiving

**When to Archive**:

- Vision fully achieved (rare)
- Domain no longer relevant
- Superseded by new north star
- Merged into larger vision

**How to Archive**:

- Move to `documentation/archive/north-stars/[NAME]-[DATE]/`
- Update references in other documents
- Create migration guide if needed
- Preserve for historical context

---

## 🎓 Best Practices

### Writing Best Practices

1. **Start with Vision**: Most important section, spend most time here
2. **Explain Principles**: Don't just list, explain WHY
3. **Use Examples**: Ground principles in real work
4. **Be Honest**: Current state should be realistic
5. **Make it Living**: Plan for evolution from start

### Size Best Practices

1. **Don't Artificially Expand**: If naturally <800 lines, might not be NORTH_STAR
2. **Don't Artificially Constrain**: If needs >2,000 lines, might need split
3. **Typical Size**: 1,000-1,500 lines for mature north star
4. **Quality over Quantity**: Better short and inspiring than long and boring

### Audience Best Practices

1. **Write for Intelligent Newcomer**: Assume smart but unfamiliar
2. **Provide Context**: Don't assume deep domain knowledge
3. **Be Inspiring**: Vision should energize, not just inform
4. **Be Practical**: Principles should guide real decisions

### Maintenance Best Practices

1. **Schedule Reviews**: Don't wait for vision to become outdated
2. **Track Evolution**: Capture learning journey
3. **Update Proactively**: Evolve as understanding deepens
4. **Communicate Changes**: Make sure stakeholders know of updates

---

## 📝 Checklist for Good North Star

**Vision Section**:

- [ ] 2-4 paragraphs of strategic vision
- [ ] Aspirational but grounded
- [ ] Specific enough to guide decisions
- [ ] Inspiring and energizing
- [ ] Clear desired future state

**Core Principles**:

- [ ] 5-10+ principles articulated
- [ ] Each principle explained (not just listed)
- [ ] Anti-patterns documented
- [ ] Examples from real work
- [ ] Guides tactical decisions

**Current State**:

- [ ] Honest assessment of reality
- [ ] Progress toward vision documented
- [ ] Challenges identified
- [ ] Not overly pessimistic

**Evolution History**:

- [ ] Initial vision documented
- [ ] Major shifts tracked
- [ ] Key learnings captured
- [ ] Current version clear

**Size and Scope**:

- [ ] 800-2,000 lines
- [ ] Strategic (not tactical)
- [ ] Comprehensive principles
- [ ] Living document

**Quality**:

- [ ] Inspiring to read
- [ ] Guides real decisions
- [ ] Clear and accessible
- [ ] Grounded in reality
- [ ] Worth revisiting

---

## 🆘 FAQ

**Q: How is NORTH_STAR different from GrammaPlan?**

A: NORTH_STAR is strategic vision + principles (WHY). GrammaPlan is strategic coordination (WHAT + orchestration). NORTH_STAR inspires; GrammaPlan coordinates.

**Q: Can a NORTH_STAR coordinate GrammaPlans?**

A: Yes, optionally. A NORTH_STAR can provide vision for multiple GrammaPlans, but coordination is not its primary purpose.

**Q: How often should I update a NORTH_STAR?**

A: Quarterly reviews minimum, plus trigger-based updates when understanding shifts significantly.

**Q: What if my north star is <800 lines?**

A: It might be a GrammaPlan (if coordinating) or strong PLAN vision (if tactical). Consider if you've fully articulated principles and vision.

**Q: What if my north star exceeds 2,000 lines?**

A: Consider splitting into multiple north stars (by domain) or creating hierarchy (parent NORTH_STAR coordinating child NORTH_STARs).

**Q: Should every project have a NORTH_STAR?**

A: No. Only create when you need strategic vision document. Most projects are fine with PLANs and GrammaPlans.

**Q: Can I convert an existing PLAN to NORTH_STAR?**

A: Yes, if the PLAN is primarily vision/principles and exceeds 1,000 lines. Extract achievements to separate PLANs.

---

## 📚 Related Documentation

**Templates**:

- `LLM/templates/NORTH_STAR-TEMPLATE.md` - Template to create north stars
- `LLM/templates/GRAMMAPLAN-TEMPLATE.md` - For comparison
- `LLM/templates/PLAN-TEMPLATE.md` - For comparison

**Guides**:

- `LLM/guides/GRAMMAPLAN-GUIDE.md` - When to use GrammaPlan
- `LLM-METHODOLOGY.md` - Full methodology overview

**Examples**:

- `work-space/plans/PLAN_STRUCTURED-LLM-DEVELOPMENT.md` - Could be NORTH_STAR
- `work-space/plans/GRAMMAPLAN_GRAPHRAG-PIPELINE-EXCELLENCE.md` - GrammaPlan for comparison

---

**Ready to Create**: Use `LLM/templates/NORTH_STAR-TEMPLATE.md` to start!

**Questions**: Revisit decision tree in this guide or ask in project context.
