# Documentation Principles and Process

**Last Updated**: November 5, 2025  
**Purpose**: Ultimate reference for documentation standards and structured development methodology  
**Status**: Living document - update as we learn

**Related Entry/Exit Points**:

- **Start Work**: `IMPLEMENTATION_START_POINT.md` (how to begin)
- **Complete Work**: `IMPLEMENTATION_END_POINT.md` (how to finish)
- **This Document**: Ultimate reference for standards and methodology

---

## 🎯 Core Principles

### 1. Design for LLM Understanding First

**Why**: LLMs are primary consumers of documentation. If an LLM can understand it in 5 minutes, humans can understand it in 10 minutes.

**How**:

- Clear hierarchical structure (folders mirror concepts)
- Consistent naming conventions
- Explicit relationships (cross-references)
- Code examples with context
- No implicit knowledge required

**Test**: Can an LLM find what it needs in one directory traversal?

---

### 2. Separate By Purpose, Not By Time

**Why**: Organizing by "what it's for" beats organizing by "when created"

**Bad**: `docs-2024-10/`, `docs-2024-11/`  
**Good**: `technical/`, `guides/`, `posts/`

**Exception**: Archives organized by time + topic

---

### 3. Three-Tier Information Architecture

**Tier 1: Context** (5 minutes for LLMs)

- Layer context files (app-layer.md, business-layer.md, etc.)
- Quick orientation
- "Where does X go?" answered immediately

**Tier 2: Guides** (30 minutes for humans)

- How to do specific tasks
- Step-by-step instructions
- Troubleshooting

**Tier 3: Deep Dives** (hours for mastery)

- Complete technical documentation
- Design decisions and evolution
- Implementation details

---

### 4. Archive Aggressively, Reference Clearly

**Why**: Old docs clutter but contain valuable context

**Strategy**:

- Archive implementation docs after feature complete
- Create INDEX.md in each archive
- Reference archives from current docs
- Never delete - always archive

---

### 5. Posts Tell Stories, Docs Explain Systems

**Why**: Different audiences, different formats

**Posts**: Hook → Story → Insight → Takeaway  
**Docs**: Purpose → Structure → Usage → Examples → API

**Don't Mix**: Keep shareable content in posts/, technical content in docs

---

## 🏗️ Structured Development Methodology

**Added**: November 5, 2025  
**Purpose**: Hierarchical methodology for LLM-assisted development  
**Reference**: `IMPLEMENTATION_START_POINT.md` (complete guide)

### The Three-Tier Hierarchy

**Development documents organized in three tiers**:

```
PLAN (defines WHAT - achievements)
  ↓
SUBPLAN (defines HOW - approach for one achievement)
  ↓
EXECUTION_TASK (logs execution - all attempts and learnings)
```

### Document Types & Naming

**PLAN**: `PLAN_<FEATURE>.md`

- Lists priority-ordered achievements (WHAT needs to exist)
- Self-contained (LLM can execute from PLAN alone)
- Dynamic (can add achievements during execution)
- Tracks subplans as they're created
- Example: `PLAN_OPTIMIZE-EXTRACTION.md`

**SUBPLAN**: `SUBPLAN_<FEATURE>_<NUMBER>.md`

- Defines specific approach (HOW) for one achievement
- Created on-demand when tackling an achievement
- Static once created (the "assignment")
- Can have multiple EXECUTION_TASKs (different attempts)
- Example: `SUBPLAN_OPTIMIZE-EXTRACTION_01.md`

**EXECUTION_TASK**: `EXECUTION_TASK_<FEATURE>_<SUBPLAN>_<EXECUTION>.md`

- Dynamic log of all implementation attempts
- Updated after every iteration
- Captures learnings, tracks circular debugging
- Multiple per SUBPLAN if first attempt fails
- Example: `EXECUTION_TASK_OPTIMIZE-EXTRACTION_01_01.md`

### When to Use Each

**Create a PLAN when**:

- Starting significant work (>10 hours)
- Work has multiple parts (achievements)
- Coordination needed across subplans

**Create a SUBPLAN when**:

- Tackling a specific achievement from a PLAN
- Have a specific approach to define
- Want to outline before executing

**Create an EXECUTION_TASK when**:

- Starting work on a SUBPLAN
- Starting a new attempt (after circular debugging)
- Any iterative LLM work (even plan creation if complex)

### Development Workflow

**Entry → Work → Exit → Reference**:

```
IMPLEMENTATION_START_POINT.md (entry)
  ↓
Create PLAN (achievements list)
  ↓
Create SUBPLAN (approach)
  ↓
Create EXECUTION_TASK (log iterations)
  ↓
Work iteratively (test-first, learn, capture)
  ↓
Complete all subplans
  ↓
IMPLEMENTATION_END_POINT.md (exit)
  ├─ Update IMPLEMENTATION_BACKLOG.md
  ├─ Process improvement analysis
  └─ Archive systematically
  ↓
DOCUMENTATION-PRINCIPLES-AND-PROCESS.md (this document - ultimate reference)
```

### Key Principles

1. **Test-First Always**: Write tests before implementation
2. **Never Cheat Tests**: Fix code, not tests
3. **Document Every Iteration**: No iteration untracked
4. **Prevent Circular Debugging**: Check every 3 iterations
5. **Capture Learnings**: Add to code as comments
6. **Dynamic Plans**: Add achievements if gaps discovered
7. **Multiple Attempts OK**: One SUBPLAN → multiple EXECUTION_TASKs normal

### Integration with Documentation

**PLANs, SUBPLANs, EXECUTION_TASKs are temporary**:

- Live in root during execution
- Archived when PLAN complete
- Follow archiving principles below

**Permanent methodology documents**:

- `IMPLEMENTATION_START_POINT.md` - Entry point guide
- `IMPLEMENTATION_END_POINT.md` - Completion guide
- `IMPLEMENTATION_BACKLOG.md` - Future work tracking
- This document - Ultimate reference

**Templates**:

- `documentation/templates/PLAN-TEMPLATE.md`
- `documentation/templates/SUBPLAN-TEMPLATE.md`
- `documentation/templates/EXECUTION_TASK-TEMPLATE.md`

For complete methodology details, see `IMPLEMENTATION_START_POINT.md`.

---

## 📂 Folder Structure (Standard)

### Root Directory

**Keep Only**:

- Essential files (README.md, requirements.txt, .env.example)
- Project files (TODO.md, CHANGELOG.md, BUGS.md)
- Methodology docs (IMPLEMENTATION_START_POINT.md, IMPLEMENTATION_END_POINT.md, IMPLEMENTATION_BACKLOG.md)
- Infrastructure (docker-compose.\*.yml)
- Active work docs (PLAN_X.md, SUBPLAN_X_Y.md, EXECUTION_TASK_X_Y_Z.md - temporary, archive when complete)

**Never Keep Long-Term**:

- Completed PLANs/SUBPLANs/EXECUTION_TASKs (archive immediately after PLAN complete)
- Implementation phase docs (archive immediately after completion)
- Session summaries (archive)
- Planning docs older than current sprint (archive)
- Analysis docs (move to documentation/planning/ or archive)

---

### documentation/

#### technical/ (Consolidated Technical Guides)

**Purpose**: Complete technical documentation of systems

**Contents**:

- GRAPH-RAG.md (knowledge graph system)
- OBSERVABILITY.md (error handling, metrics, retry, logging)
- ARCHITECTURE.md (4-layer + domains + libraries)
- LIBRARIES.md (all 18 cross-cutting libraries)
- TESTING.md (testing strategy)

**When to Create**: When you have a complete system to document

**When to Update**: After significant changes or new learnings

**Structure**:

```markdown
# System Name

## Overview (2-3 paragraphs)

## Architecture (high-level design)

## Components (detailed breakdown)

## Usage Examples (code samples)

## Integration (how it connects)

## API Reference (or link to reference/)

## Known Issues

## Future Enhancements
```

---

#### guides/ (User Guides - How To)

**Purpose**: Task-oriented documentation

**Contents**:

- EXECUTION.md (how to run pipelines)
- DEPLOYMENT.md (how to deploy)
- MCP-SERVER.md (how to integrate)
- OBSERVABILITY-STACK.md (how to use Grafana) ← TODO

**When to Create**: When users need to perform a specific task

**Structure**:

```markdown
# How to [Task]

## Prerequisites

## Step-by-Step Instructions

## Examples

## Troubleshooting

## Advanced Usage
```

---

#### architecture/ (Component Patterns)

**Purpose**: Design patterns for specific component types

**Contents**:

- PIPELINE.md
- STAGE.md
- AGENT.md
- SERVICE.md
- CORE.md

**When to Update**: When base class or pattern changes

**Structure**:

```markdown
# [Component] Pattern

## What is a [Component]

## Base Class (if applicable)

## Common Patterns

## Integration with Libraries

## Examples

## Testing Strategy
```

---

#### context/ (LLM Onboarding - Critical!)

**Purpose**: 5-minute LLM orientation

**Contents**:

- app-layer.md
- business-layer.md
- core-layer.md
- dependencies-layer.md

**Format** (strict):

```markdown
# [LAYER] Layer - LLM Context Guide

**Layer Purpose**: One sentence

## What Belongs in [LAYER] Layer

✅ List of what goes here
❌ List of what doesn't go here

## Structure

[Folder tree]

## Import Pattern

[Code example showing allowed imports]

## Example

[Real code example]

## When Adding New Code

[Decision tree: where does X go?]
```

**Update When**: Layer responsibilities change (rare)

**Critical**: Keep these files short (<300 lines), focused, LLM-parseable

---

#### posts/ (LinkedIn Articles - Shareable Content)

**Purpose**: Transform implementation learnings into engaging stories

**Structure**:

```
posts/
├── README.md (index + narrative arc)
├── series-1-llm-assisted-development/
├── series-2-building-agentic-systems/
├── series-3-architecture-for-agents/
└── templates/
    ├── linkedin-post-template.md
    └── narrative-framework.md
```

**Post Format** (consistent):

```markdown
# [Title]

**Hook**: One compelling sentence or statistic

## The Problem

[What we faced]

## The Journey

[How we approached it]

## The Insight

[What we learned]

**Agent Angle**: [Impact on agent performance]
**LLM Angle**: [Impact on LLM-assisted development]

## The Code

[Real examples with line numbers]

## The Results

[Metrics, before/after]

## Key Takeaway

[Actionable advice]

**Tags**: #AI #Agents #LLM #SoftwareEngineering
```

**When to Create**: After completing significant feature or learning

**Series Strategy**:

- Series 1: LLM development practices
- Series 2: Agent system design
- Series 3: Architecture for agents

---

#### planning/ (Active Planning - Living Docs)

**Purpose**: Current objectives, strategies, roadmaps

**Contents**:

- MASTER-PLAN.md (current sprint/objectives)
- REFACTOR-GUIDE.md (systematic refactor guide)
- ROADMAP.md (3-6 month strategy)

**Update Frequency**: Weekly or after major milestones

**When Completed**: Archive to appropriate archive folder

---

#### reference/ (Quick Lookup)

**Purpose**: API references, configuration options, metrics catalog

**Contents**:

- GRAPHRAG-CONFIG-REFERENCE.md
- API-REFERENCE.md (all library functions)
- METRICS-REFERENCE.md (all 100+ metrics)

**Format**: Tables, lists, searchable

**When to Create**: When you have a stable API to document

---

#### project/ (Project Meta)

**Purpose**: Project vision, roadmap, concepts

**Contents**:

- PROJECT.md (vision, goals)
- BACKLOG.md (feature backlog)
- TECHNICAL-CONCEPTS.md (core concepts)
- USE-CASE.md (use cases)
- MIGRATION.md (migration guides)

**Update**: As project evolves

---

#### archive/ (Historical Preservation)

**Purpose**: Preserve implementation journey without cluttering current docs

**Structure**:

```
archive/
├── [topic]-[date]/
│   ├── INDEX.md (guide to archive)
│   ├── planning/ (design docs, plans)
│   ├── implementation/ (completion docs, phase summaries)
│   ├── testing/ (test strategies, coverage)
│   ├── analysis/ (problem analysis, scans)
│   └── summaries/ (session summaries, retrospectives)
```

**When to Archive**: After feature/refactor/implementation complete

**INDEX.md Required**: Every archive needs comprehensive INDEX.md

---

## 📋 Documentation Lifecycle

### Creating New Documentation

**Step 1: Identify Type**

- **Feature/System**: technical/ (e.g., OBSERVABILITY.md)
- **How-To**: guides/ (e.g., HOW-TO-USE-GRAFANA.md)
- **Pattern**: architecture/ (e.g., LIBRARY.md)
- **API**: reference/ (e.g., API-REFERENCE.md)
- **Planning**: planning/ (e.g., Q1-2025-OBJECTIVES.md)
- **Story**: posts/ (e.g., series-X/post-Y.md)

**Step 2: Check for Existing**

- Would this enhance an existing doc? → Update instead of creating
- Is this temporary (implementation phase)? → Plan to archive from day 1
- Is this historical? → Goes directly to archive/

**Step 3: Follow Template**

- Use appropriate template for doc type
- Include all required sections
- Add cross-references
- Code examples must be tested

**Step 4: Update Navigation**

- Add to documentation/README.md
- Add to parent folder README if applicable
- Update cross-references in related docs

---

### During Implementation/Feature Work

**Real-Time Documentation**:

**Phase Docs** (will be archived):

- Micro-plans (e.g., ERROR-HANDLING-LIBRARY-MICRO-PLAN.md)
- Phase completions (e.g., PHASE-1A-COMPLETE.md)
- Keep in root during active work
- Archive when feature complete

**Analysis Docs** (will be archived):

- Problem analysis (e.g., GRAPHRAG-13K-FAILURE-ANALYSIS.md)
- Gap analysis (e.g., LIBRARY-INTEGRATION-GAPS.md)
- Keep in root during investigation
- Archive when resolved

**Session Summaries** (will be archived):

- Daily progress (e.g., SESSION-SUMMARY-DATE.md)
- Milestone summaries
- Archive after feature complete

**Rule**: If it's about the "journey", it will be archived. If it's about the "result", it stays in documentation/.

---

### After Feature/Implementation Complete

**Step 1: Follow IMPLEMENTATION_END_POINT.md**

Complete the exit process:

- Update IMPLEMENTATION_BACKLOG.md (extract future work from EXECUTION_TASKs)
- Process improvement analysis (improve methodology)
- Extract learnings to permanent docs
- Create archive with INDEX.md

**Step 2: Consolidate Learnings** (within 24 hours)

Extract learnings from EXECUTION_TASKs and update:

- Technical guide (documentation/technical/)
- User guide (documentation/guides/)
- Reference doc (documentation/reference/)
- Post outline (documentation/posts/)

**Step 3: Archive** (per IMPLEMENTATION_END_POINT.md)

```bash
# For PLAN-based work (using structured methodology)
mkdir -p documentation/archive/[feature]-[date]/{planning,subplans,execution,summary}

# Move PLAN documents
mv PLAN_[FEATURE].md documentation/archive/[feature]-[date]/planning/
mv SUBPLAN_[FEATURE]_*.md documentation/archive/[feature]-[date]/subplans/
mv EXECUTION_TASK_[FEATURE]_*.md documentation/archive/[feature]-[date]/execution/
# Create and move completion summary

# For other work (legacy pattern)
mkdir -p documentation/archive/[topic]-[date]/{planning,implementation,testing,analysis,summaries}
mv *-COMPLETE.md documentation/archive/[topic]/implementation/
# ... etc

# Always create INDEX.md
# Document what's in archive, why, and how to use it
```

**Step 3: Update Current Docs**

- Update technical/ guide with new insights
- Update planning/ docs with next steps
- Update README.md navigation if needed

---

## 🔍 Documentation Quality Standards

### For LLM Optimization:

**1. Clear Hierarchy** ✅

```markdown
# Top Level (H1)

## Second Level (H2)

### Third Level (H3)

❌ Don't skip levels
❌ Don't use H4+ (too deep for quick scanning)
```

**2. Explicit Structure** ✅

```markdown
## Section Name

**Purpose**: One sentence
**Contents**: List
**When to Use**: Clear criteria

❌ Don't use implicit structure
✅ Do use bold labels for scanability
```

**3. Code Examples** ✅

```python
# Always include:
# 1. Import statements (show full path)
from core.libraries.error_handling import ApplicationError

# 2. Complete example (runnable if possible)
def example():
    ...

# 3. Expected output or behavior
# Result: ApplicationError with context shown in logs
```

**4. Cross-References** ✅

```markdown
See also: [Related Doc](path/to/doc.md)
Implementation: `path/to/code.py` (line 123-145)
Tests: `tests/path/to/test.py`

✅ Always provide context for references
```

---

### For Human Readability:

**1. Start with "Why"**

```markdown
## Overview

**Problem This Solves**: [Specific problem]
**How It Solves It**: [Approach]
**Why This Approach**: [Rationale]
```

**2. Progressive Disclosure**

```markdown
# Quick overview at top

## Common use cases next

### Advanced features later

#### Edge cases at end
```

**3. Real Examples Over Abstract**

```markdown
❌ "You can configure X to do Y"
✅ "To track LLM costs: Counter('llm_cost_usd', labels=['agent'])"
```

---

## 📝 Document Templates

### Technical Guide Template:

````markdown
# [System/Feature Name]

**Last Updated**: [Date]  
**Status**: [Production/Beta/Planning]

## Overview

**What It Is**: [1-2 sentences]
**What Problem It Solves**: [Specific problem]
**Key Benefits**: [3-5 bullet points]

## Architecture

[High-level design, diagrams if helpful]

## Components

### Component 1

**Purpose**: [What it does]
**Location**: `path/to/code`
**API**: [Key functions/classes]
**Example**:

```python
[code example]
```
````

[Repeat for each component]

## Integration

**Works With**: [Related systems]
**Depends On**: [Dependencies]
**Used By**: [Consumers]

## Usage

### Basic Usage

[Simple example]

### Advanced Usage

[Complex example]

## Configuration

[All configuration options]

## Testing

**Tests**: `path/to/tests`
**Coverage**: [What's tested]
**Run**: `python -m tests.path.to.test`

## Troubleshooting

**Common Issues**:

1. [Issue] → [Solution]
2. [Issue] → [Solution]

## API Reference

[Link to reference/API-REFERENCE.md or inline]

## Future Enhancements

**Planned**:

- [Enhancement 1]
- [Enhancement 2]

**Deferred**:

- [Enhancement with TODO]

## References

**Code**: `path/to/implementation`
**Tests**: `path/to/tests`
**Related Docs**: [Links]

````

---

### Context File Template (LLM Onboarding):

```markdown
# [LAYER] Layer - LLM Context Guide

**Layer Purpose**: [One sentence - what this layer does]

---

## What Belongs in [LAYER] Layer

✅ **Does belong**:
- [Type 1] (description)
- [Type 2] (description)
- [Type 3] (description)

❌ **Does NOT belong**:
- [Type 1] (goes in [OTHER LAYER])
- [Type 2] (goes in [OTHER LAYER])

---

## Structure

````

[layer]/
├── [folder1]/
│ └── [description]
└── [folder2]/
└── [description]

````

---

## Import Pattern

[LAYER] can import from [which layers]:

```python
# ✅ Allowed imports:
from [lower_layer].module import Class

# ❌ Forbidden imports:
from [higher_layer].module import Class
````

---

## Example: [Real Component]

```python
# [layer]/[path]/[file].py
[complete real example from codebase]
```

**Key**: [What this example demonstrates]

---

## When Adding New Code

**Ask**: [Decision question]

- **Yes** → [LAYER] layer
- **No** → Check other layers

**Examples**:

- [Case 1] → [LAYER]
- [Case 2] → [OTHER LAYER]

---

**For detailed patterns, see**: `documentation/architecture/`

````

---

### LinkedIn Post Template:

```markdown
# [Title - Action-Oriented]

**Series**: [1/2/3]
**Theme**: [LLM Development / Agentic Systems / Architecture]
**Date**: [Publication date]

---

## Hook (The Surprise)

[One compelling sentence or statistic]

---

## The Problem

[What we faced - relatable, specific]

**Context**:
- [Detail 1]
- [Detail 2]
- [Metric showing scale]

---

## The Journey

[How we approached it - chronological]

**Attempt 1**: [What we tried]
**Result**: [What happened]

**Attempt 2**: [What we tried]
**Result**: [What happened]

**Breakthrough**: [What worked]

---

## The Insight

[What we learned - generalizable]

**Agent Angle**: [Impact on agent performance/design]
**LLM Angle**: [Impact on LLM-assisted development]

---

## The Code

[Real, tested examples]

**Before** (what we had):
```python
[old code]
````

**After** (what we built):

```python
[new code]
```

**What Changed**: [Explanation]

---

## The Results

**Metrics**:

- [Quantifiable result 1]
- [Quantifiable result 2]
- [Improvement percentage]

**Before/After Comparison**:
| Aspect | Before | After | Improvement |
|--------|--------|-------|-------------|
| [Metric 1] | [Value] | [Value] | [%] |

---

## Key Takeaways

**1. [Primary Lesson]**
[Explanation - actionable]

**2. [Secondary Lesson]**
[Explanation - actionable]

**3. [Tertiary Lesson]**
[Explanation - actionable]

---

## For LLM Developers

[Specific advice for those building with LLMs]

## For Agent Builders

[Specific advice for those building agent systems]

---

## Call to Action

[Question or engagement prompt]

**Tags**: #AI #Agents #LLM #Development #SoftwareEngineering

---

**Code Examples**: [Link to repo]  
**Full Documentation**: [Link to docs]

````

---

### Archive INDEX Template:

```markdown
# [Topic] Archive - [Month Year]

**Implementation Period**: [Dates]
**Duration**: [Hours]
**Result**: [What was built]

---

## Purpose

[Why this archive exists, what it contains]

**Use for**: [When to reference this archive]
**Current Documentation**: [Link to current docs]

---

## What Was Built

[Summary of achievements]

---

## Archive Contents

### planning/ (X files)
[List with brief descriptions]

### implementation/ (X files)
[List with brief descriptions]

### testing/ (X files)
### analysis/ (X files)
### summaries/ (X files)

---

## Key Documents

**Most Important**:
1. [Doc name] - [Why important]
2. [Doc name] - [Why important]

---

## Timeline

[Chronological summary]

---

**Archive Complete**: [X] files preserved
````

---

## 🔄 Maintenance Process

### Weekly Review (15 minutes)

**Check**:

- Are there >5 .md files in root? → Archive old ones
- Are planning/ docs current? → Update or archive
- Have we completed features? → Consolidate to technical/
- New learnings to document? → Update guides

---

### After Feature/Implementation (1 hour)

**1. Extract Learnings** (30 min):

- Review all phase docs
- Identify key insights
- Note code examples
- Gather metrics

**2. Consolidate** (20 min):

- Update relevant technical/ guide
- Add to guides/ if new capability
- Update reference/ if API changed
- Outline post in posts/

**3. Archive** (10 min):

- Create archive folder structure
- Move all phase docs
- Create INDEX.md
- Update main README

---

### Monthly Review (1 hour)

**Content Audit**:

- Outdated information? → Update
- Missing documentation? → Create
- Redundant docs? → Consolidate
- Archive INDEX files → Ensure complete

**Navigation Audit**:

- All links work?
- Cross-references current?
- README.md updated?
- Easy to find info?

---

## ✅ Quality Checklist

### Before Creating New Doc:

- [ ] Does this belong in existing doc? (update vs create)
- [ ] Is this temporary? (will it be archived?)
- [ ] What type is it? (technical/guide/post/reference)
- [ ] Have I checked the template?
- [ ] Will LLM understand the structure?

### Before Publishing/Committing:

- [ ] All code examples tested?
- [ ] All links work?
- [ ] Follows template for its type?
- [ ] Cross-references added?
- [ ] Navigation updated?
- [ ] No orphaned docs? (referenced from somewhere)

### Before Archiving:

- [ ] Learnings extracted to current docs?
- [ ] Archive folder structure created?
- [ ] INDEX.md written?
- [ ] Files moved to correct subfolders?
- [ ] Navigation updated to point to current docs?

---

## 🎯 LLM-Specific Optimizations

### 1. Consistent File Naming

**Pattern**: `NOUN-VERB.md` or `SYSTEM-NAME.md`

✅ Good:

- `ERROR-HANDLING.md`
- `OBSERVABILITY-STACK.md`
- `HOW-TO-DEPLOY.md`

❌ Bad:

- `errors.md` (too vague)
- `stuff-about-deployment.md` (unclear)
- `notes-2024.md` (what notes?)

---

### 2. Frontmatter for Context

```markdown
# Document Title

**Last Updated**: [Date]
**Purpose**: [One sentence]
**Audience**: [LLMs/Developers/Users]
**Status**: [Complete/WIP/Planning]
**Related**: [Links to related docs]

---

[Content starts here]
```

**Why**: LLM knows immediately what the doc is for

---

### 3. Hierarchical Information

```markdown
# Top Level (What it is)

## Architecture (How it works)

### Component 1 (What it does)

#### Method 1 (How to use it)

✅ Each level adds detail
❌ Don't put API details at top level
```

---

### 4. Explicit Relationships

```markdown
## Integration

**Depends On**:

- logging library → [Link]
- metrics library → [Link]

**Used By**:

- BaseStage → `core/base/stage.py`
- BaseAgent → `core/base/agent.py`

**Related Concepts**:

- Error handling patterns → [Link]
```

**Why**: LLM can traverse relationships

---

## 📊 Metrics for Documentation Quality

### Track These:

**Structure Metrics**:

- Root .md files (target: <10)
- Archive completeness (all have INDEX.md?)
- Orphaned docs (referenced from nowhere)

**Content Metrics**:

- Code examples tested? (target: 100%)
- Broken links (target: 0)
- Outdated information (check monthly)

**LLM Metrics**:

- Can LLM find info in <5 min? (test quarterly)
- Context files up to date? (update on layer changes)
- Navigation clear? (one path to any doc)

---

## 🎊 Success Criteria

**Documentation is Good When**:

- ✅ LLM can onboard in 5 minutes (context/ files)
- ✅ Developer can find any info in <2 minutes
- ✅ Root directory has <10 .md files
- ✅ Every archive has INDEX.md
- ✅ All code examples tested
- ✅ No broken links
- ✅ Clear path: context → guides → technical → reference

**Documentation Needs Work When**:

- ❌ Root has >15 .md files
- ❌ LLM asks "where is X?" repeatedly
- ❌ Code examples don't run
- ❌ Links broken
- ❌ No INDEX.md in archives

---

## 🚀 This Document

**Status**: Living document  
**Update**: When documentation practices evolve  
**Location**: `documentation/DOCUMENTATION-PRINCIPLES-AND-PROCESS.md`  
**Purpose**: Single source of truth for documentation standards

**When to Reference**:

- Before creating any new documentation
- During documentation reviews
- When onboarding new contributors
- When LLM struggles to navigate

---

**Follow these principles = LLM-optimized, maintainable, professional documentation**
