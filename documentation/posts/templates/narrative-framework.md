# Narrative Framework for LLM & Agent Posts

**Purpose**: Consistent storytelling structure across all posts  
**Goal**: Engage → Educate → Empower

---

## Story Structure (Universal)

### Act 1: The Hook (First 3 sentences)

**Purpose**: Stop the scroll

**Elements**:

- Surprising statistic or result
- Relatable problem
- Promise of solution

**Formula**: [RESULT] in [TIMEFRAME]. [UNEXPECTED DETAIL]. Here's how.

**Examples**:

- "61 hours of LLM processing. $5.87 in costs. Lost to an empty error message."
- "Our agents built a perfect graph. Every entity connected to every other. That was the problem."
- "5-minute LLM onboarding. Down from 30 minutes. One documentation change did it."

---

### Act 2: The Problem (Build Empathy)

**Purpose**: "I've been there too"

**Elements**:

- Specific scenario (not abstract)
- Scale (numbers, scope)
- Pain point (cost, time, frustration)
- Why it matters

**Show Don't Tell**:

```
❌ "We had documentation issues"
✅ "Our LLM spent 30 minutes reading docs, then asked: 'Where do agents go?'"
```

---

### Act 3: The Journey (Show Process)

**Purpose**: Educational - how we approached it

**Elements**:

- Attempt 1 → Result (often failure)
- Attempt 2 → Result (getting closer)
- Breakthrough → Result (success!)

**Include**:

- Code snippets showing evolution
- Metrics at each stage
- Decision points ("We chose X over Y because...")

**LLM Development Angle**: Show how LLM participated in solution

---

### Act 4: The Solution (Teach)

**Purpose**: Transfer knowledge

**Elements**:

- What we built
- How it works
- Why this approach
- **Agent Angle**: Impact on agent performance
- **LLM Angle**: Impact on LLM-assisted development

**Code-Heavy Section**:

- Before code (the problem)
- After code (the solution)
- What changed (explanation)

---

### Act 5: The Results (Prove It)

**Purpose**: Credibility through metrics

**Elements**:

- Quantifiable results
- Before/after comparison
- Real production metrics
- Cost savings or efficiency gains

**Format**: Tables, lists, or dashboards

**Example**:
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Debug time | Hours | Seconds | 99.9% |
| Error visibility | 0% | 100% | ∞ |
| Code lines | 1,375 | 200 | 85% reduction |

---

### Act 6: Takeaways (Make It Actionable)

**Purpose**: "What can I use tomorrow?"

**Elements**:

- 3 key lessons (numbered)
- Each lesson: Principle + How-to + Why
- Applicable beyond our specific case

**Formula**:

1. **[Lesson]**: [Principle]. [How to apply]. [Why it works]

---

### Act 7: CTA (Conversation)

**Purpose**: Engagement and community

**Questions**:

- Ask about their experience
- Request their approach
- Invite discussion

**Don't**: Hard sell, promote products  
**Do**: Start conversations, build community

---

## Agent-Specific Narrative Elements

### When Writing About Agents:

**Always Include**:

1. **Agent Performance Metrics**: Tokens, cost, accuracy, speed
2. **Agent Constraints**: What limits were imposed and why
3. **Agent Output Quality**: How constraints affect results
4. **Cost-Benefit**: When to use agents vs simpler approaches

**Example Integration**:

```
Our GraphRAG agents were creating complete graphs.
3,486 relationships for 84 entities.
Mathematically perfect. Practically useless.

**Agent Insight**: Unconstrained agents optimize for completeness,
not meaningfulness. The adaptive window strategy taught our agents
when to connect entities (nearby in video) and when not to
(distant chunks = different context).

Result: Density dropped from 1.0 to 0.15. Community detection
finally worked.

**Lesson**: Constrain your agents wisely. Perfect is the enemy of useful.
```

---

## LLM Development Narrative Elements

### When Writing About LLM-Assisted Development:

**Always Include**:

1. **LLM Collaboration**: How LLM helped in development
2. **Documentation Impact**: How docs enable LLM effectiveness
3. **Error Message Quality**: How it affects LLM debugging
4. **Code Organization**: How structure helps LLM navigate

**Example Integration**:

```
We created 4 context files: app-layer.md, business-layer.md, etc.
Each <300 lines. Total reading time: 5 minutes for an LLM.

**LLM Impact**: Before: "Where should I put this code?"
took 5+ minutes of back-and-forth. After: "Read app-layer.md"
→ instant correct answer.

**Why It Works**: LLMs excel at pattern matching. Give them
clear patterns (APP = external, BUSINESS = logic, etc.) and
they never ask twice.

**Lesson**: Design documentation for machine parsing first,
human reading second. You'll get both.
```

---

## Tone & Voice

**Be**: Technical but accessible, humble but confident  
**Use**: "We" not "I" (team effort)  
**Show**: Code and metrics, not just claims  
**Teach**: Share learnings, don't gatekeep

**Avoid**:

- Marketing speak
- Hype without substance
- Abstract concepts without examples
- Claims without metrics

---

## Content Checklist

Before publishing, verify:

- [ ] Hook is compelling (would I stop scrolling?)
- [ ] Problem is relatable (have others faced this?)
- [ ] Journey shows process (not just result)
- [ ] Agent angle included (impact on agent systems)
- [ ] LLM angle included (impact on LLM development)
- [ ] Code examples are real (from our codebase)
- [ ] Metrics are actual (not hypothetical)
- [ ] Takeaways are actionable (can use tomorrow)
- [ ] CTA encourages discussion (not selling)
- [ ] Length appropriate (1500-2000 words)

---

**Use this framework for every post to maintain consistency and quality.**
