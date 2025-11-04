# Designing Documentation for LLM Understanding

**Series**: 1 - LLM-Assisted Development  
**Status**: Outline (to be expanded)

---

## Hook

"Our LLM onboarding went from 30 minutes to 5 minutes with one change. We created 4 files that teach architecture faster than any tutorial."

---

## The Problem

Building with LLM assistance means the LLM needs to understand your codebase.

**Our Challenge**:

- 76 files across 6 folders
- No clear "where does X go?" answer
- LLM spent 30 minutes reading scattered docs
- Still asked: "Where should agents go?"
- Slowed down every development session

**Scale**: Every code addition = 5 minutes of LLM confusion

---

## The Journey

**Attempt 1**: Traditional documentation

- README with architecture overview
- Component docs spread across folders
- **Result**: LLM couldn't form mental model

**Attempt 2**: Single architecture doc

- 2000-line ARCHITECTURE.md
- Everything in one place
- **Result**: Better, but still slow (15 min to digest)

**Breakthrough**: Layer context files

- 4 files: app-layer.md, business-layer.md, core-layer.md, dependencies-layer.md
- Each <300 lines
- Strict template: "What belongs here" + "What doesn't" + "Examples"
- **Result**: 5-minute LLM onboarding

---

## The Solution

**The 4-Layer Context System**:

Each context file answers:

1. What is this layer?
2. What code belongs here?
3. What code does NOT belong here?
4. Import rules (what can this layer import?)
5. Real example from codebase
6. Decision tree: "Where does new code X go?"

**Code Example** - app-layer.md:

```markdown
## What Belongs in APP Layer

✅ Command-line interfaces
✅ User interfaces  
✅ API servers
✅ Runnable scripts

❌ Business logic → BUSINESS
❌ Data models → CORE
❌ Database clients → DEPENDENCIES

## When Adding New Code

**Question**: Does it run or talk to users?

- YES → APP layer
- NO → Check other layers
```

**Agent Angle**: Clear layer separation means agents (GraphRAG, extraction, etc.) have obvious homes. Agent code = business logic = BUSINESS layer. LLM never has to guess.

**LLM Angle**: LLMs pattern-match. Give them explicit patterns ("✅ goes here, ❌ doesn't") and they replicate perfectly. Our LLM now suggests correct layer 100% of the time.

---

## The Results

**Before/After**:
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| LLM onboarding | 30 min | 5 min | 83% faster |
| "Where does X go?" questions | Daily | Never | 100% reduction |
| Incorrect suggestions | ~30% | ~0% | Near perfect |

**Real Metrics**:

- 4 context files
- ~800 total lines
- 5-minute complete understanding
- Works for any LLM (Claude, GPT, etc.)

---

## Key Takeaways

**1. Layer Separation is LLM-Friendly**
Design your architecture so layers have clear, non-overlapping responsibilities. LLMs understand boundaries better than gradients.

**2. Explicit > Implicit for LLMs**
Don't make LLMs infer. Tell them: "This goes here, that doesn't." Use ✅ and ❌ symbols - LLMs parse them instantly.

**3. Short, Focused Files > Long, Comprehensive**
4 files of 200 lines each beats 1 file of 800 lines. LLMs can load and parse faster.

---

## For LLM Developers

**Pattern to Adopt**:

```
documentation/context/
├── [layer1]-layer.md  # What belongs, what doesn't, examples
├── [layer2]-layer.md
└── ...
```

**Common Pitfalls**:

- Making LLM read entire codebase to understand structure
- Implicit rules ("developers just know...")
- No decision trees for common questions

---

## For Agent Builders

**Design Principle**: Agents are business logic. If your architecture doesn't make this obvious, LLMs will put them in wrong places.

**Our Solution**:

```
business/agents/     # All agents here
  ├── graphrag/      # GraphRAG agents
  ├── ingestion/     # Ingestion agents
  └── rag/           # RAG agents
```

Clear. Unambiguous. LLM-navigable.

---

## CTA

**Question**: How do you structure documentation for LLM tools? Share your strategies!

**Repository**: [Link to context files]

---

**Tags**: #LLM #AI #Documentation #DeveloperTools #SoftwareArchitecture
