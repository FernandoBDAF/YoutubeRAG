# EXECUTION_ANALYSIS Guide

**Purpose**: Comprehensive guide to EXECUTION_ANALYSIS documents - taxonomy, usage, structure, and lifecycle  
**Status**: Reference Document  
**Last Updated**: 2025-11-08  
**Related**: `LLM-METHODOLOGY.md` → "EXECUTION_ANALYSIS Documents" section

---

## 🎯 What Are EXECUTION_ANALYSIS Documents?

**EXECUTION_ANALYSIS documents** are structured analysis documents used for:

- Investigating bugs, issues, or regressions
- Reviewing methodology compliance and effectiveness
- Evaluating implementation quality
- Analyzing processes and workflows
- Making strategic planning decisions

**Key Characteristics**:
- **Not execution tracking** (use EXECUTION_TASK for that)
- **Analysis-focused** (problem → analysis → recommendations)
- **Structured** (follow category-specific templates)
- **Archived** (moved to archive after completion)

**Naming Convention**: `EXECUTION_ANALYSIS_<TOPIC>.md`

---

## 📊 Taxonomy: 5 Categories

### Category 1: Bug/Issue Analysis

**Purpose**: Analyze bugs, regressions, or issues to identify root causes and propose fixes

**When to Create**:
- Bug discovered during execution or testing
- Regression detected (something that worked before now broken)
- Issue needs deep root cause analysis
- Multiple related bugs need unified analysis

**Structure Requirements**:
1. **Header Metadata**: Purpose, Date, Status, Related PLAN/Achievement, Category
2. **Problem Description**: What's broken, symptoms, impact
3. **Root Cause Analysis**: Investigation, evidence, root cause identification
4. **Solution Options**: Multiple approaches considered
5. **Recommendation**: Preferred solution with rationale
6. **Implementation Plan**: Steps to fix (if applicable)
7. **Success Criteria**: How to verify fix

**Examples**:
- `EXECUTION_ANALYSIS_PROMPT-GENERATOR-0.1-BUG.md` - Initial bug analysis
- `EXECUTION_ANALYSIS_PROMPT-GENERATOR-REGRESSION-BUG.md` - Regression analysis
- `EXECUTION_ANALYSIS_COMPLETION-DETECTION-FALSE-POSITIVE.md` - False positive bug

**Archive Location**: `documentation/archive/execution-analyses/bug-analysis/YYYY-MM/`

**Template**: `LLM/templates/EXECUTION_ANALYSIS-BUG-TEMPLATE.md` (when created)

---

### Category 2: Methodology Review & Compliance

**Purpose**: Review methodology compliance, identify gaps, extract insights from real usage

**When to Create**:
- PLAN completion (at END_POINT protocol)
- Periodic methodology review
- Methodology gap discovered
- Compliance audit needed
- Extracting learnings from completed work

**Structure Requirements**:
1. **Header Metadata**: Purpose, Date, Status, Related PLAN(s), Category
2. **Executive Summary**: High-level findings and recommendations
3. **Findings by Category**: Organized findings (compliance, gaps, patterns)
4. **Recommendations**: Methodology improvements, template updates, protocol enhancements
5. **Action Items**: Specific improvements to implement
6. **Conclusion**: Summary and next steps

**Examples**:
- `EXECUTION_ANALYSIS_METHODOLOGY-REVIEW.md` - General methodology review
- `EXECUTION_ANALYSIS_METHODOLOGY-GAP-ANALYSIS.md` - Gap analysis
- `EXECUTION_ANALYSIS_CODE-QUALITY-COMPLETION-REVIEW.md` - PLAN completion review

**Archive Location**: `documentation/archive/execution-analyses/methodology-review/YYYY-MM/`

**Template**: `LLM/templates/EXECUTION_ANALYSIS-METHODOLOGY-REVIEW-TEMPLATE.md` (when created)

---

### Category 3: Implementation Review

**Purpose**: Review implementation status, validate against requirements, identify gaps

**When to Create**:
- Achievement completion review
- PLAN pause or milestone review
- External feedback received (e.g., code review)
- Quality validation needed
- Implementation status check

**Structure Requirements**:
1. **Header Metadata**: Purpose, Date, Status, Related PLAN/Achievement, Category
2. **Status Review**: Current state, what's implemented, what's missing
3. **Findings**: Issues found, gaps identified, quality assessment
4. **Recommendations**: What to fix, what to improve
5. **Action Items**: Specific tasks to address findings

**Examples**:
- `EXECUTION_ANALYSIS_API-REVIEW.md` - API code review
- `EXECUTION_ANALYSIS_ENTITY-RESOLUTION-BUGS.md` - Implementation bugs found
- `EXECUTION_ANALYSIS_GRAPH-CONSTRUCTION-REVIEW.md` - Feature review

**Archive Location**: `documentation/archive/execution-analyses/implementation-review/YYYY-MM/`

**Template**: `LLM/templates/EXECUTION_ANALYSIS-IMPLEMENTATION-REVIEW-TEMPLATE.md` (when created)

---

### Category 4: Process & Workflow Analysis

**Purpose**: Analyze processes, workflows, or methodology aspects to identify improvements

**When to Create**:
- Process issues identified (workflow friction)
- Performance problems found
- Methodology gap discovered
- Workflow optimization needed
- Process bottleneck analysis

**Structure Requirements**:
1. **Header Metadata**: Purpose, Date, Status, Related, Category
2. **Problem Statement**: What's the process issue, impact, symptoms
3. **Analysis**: Investigation, root cause, contributing factors
4. **Recommendations**: Process improvements, workflow changes
5. **Implementation Plan**: Steps to improve process

**Examples**:
- `EXECUTION_ANALYSIS_FILE-MOVING-PERFORMANCE.md` - Performance analysis
- `EXECUTION_ANALYSIS_NEW-SESSION-CONTEXT-GAP.md` - Process gap analysis
- `EXECUTION_ANALYSIS_RESUME-PROTOCOL-GAPS.md` - Protocol gap analysis

**Archive Location**: `documentation/archive/execution-analyses/process-analysis/YYYY-MM/`

**Template**: `LLM/templates/EXECUTION_ANALYSIS-PROCESS-ANALYSIS-TEMPLATE.md` (when created)

---

### Category 5: Planning & Strategy

**Purpose**: Strategic analysis, planning decisions, or design recommendations

**When to Create**:
- Before creating new PLAN (strategic decision needed)
- Design choice requires analysis
- Multiple approaches to evaluate
- Planning question arises
- Strategy decision needed

**Structure Requirements**:
1. **Header Metadata**: Purpose, Date, Status, Related, Category
2. **Current State**: What exists now, context
3. **Analysis**: Options considered, trade-offs, evaluation
4. **Recommendation**: Preferred approach with rationale
5. **Next Steps**: How to proceed (often leads to PLAN creation)

**Examples**:
- `EXECUTION_ANALYSIS_PROMPT-AUTOMATION-STRATEGY.md` - Automation strategy
- `EXECUTION_ANALYSIS_PLAN-COMPLETION-VERIFICATION-GAP.md` - Planning gap analysis
- `EXECUTION_ANALYSIS_TESTING-REQUIREMENTS-GAP.md` - Requirements gap

**Archive Location**: `documentation/archive/execution-analyses/planning-strategy/YYYY-MM/`

**Template**: `LLM/templates/EXECUTION_ANALYSIS-PLANNING-STRATEGY-TEMPLATE.md` (when created)

---

## 🔄 Lifecycle Stages

### Stage 1: Active (In Root Directory)

**Characteristics**:
- Recently created
- Being worked on or referenced
- Referenced in active PLANs
- May be updated

**Location**: Root directory (`/`)

**Duration**: Until analysis complete + actively referenced

---

### Stage 2: Archived (In Archive)

**Characteristics**:
- Analysis complete
- No longer actively referenced
- Historical record
- May be referenced by other documents

**Location**: `documentation/archive/execution-analyses/<category>/YYYY-MM/`

**Archival Triggers**:
- Analysis complete + 30 days
- Related PLAN archived
- No active references for 30 days
- Manual archival (when ready)

---

### Stage 3: Superseded (In Archive, Marked)

**Characteristics**:
- Replaced by newer analysis
- Historical reference only
- Marked as superseded in metadata

**Location**: Same as archived, with status marked "Superseded"

**Example**: Bug #1 analysis superseded by unified solution analysis

---

## 🔗 Cross-Reference System

### Linking Related Analyses

**In Analysis Document**:
```markdown
## Related Analyses

- **EXECUTION_ANALYSIS_BUG-1.md** - Initial bug analysis (superseded)
- **EXECUTION_ANALYSIS_BUG-2.md** - Related regression
- **EXECUTION_ANALYSIS_UNIFIED-SOLUTION.md** - Comprehensive solution (current)
```

**Tracking Analysis Lineage**:
- Bug #1 → Bug #2 → Bug #3 → Unified Solution
- Each analysis references previous ones
- Final analysis links to all related analyses

### INDEX.md Catalog

**Location**: `documentation/archive/execution-analyses/INDEX.md`

**Contents**:
- Catalog of all analyses
- Grouped by category
- Grouped by related PLAN
- Metadata (date, status, related)
- Quick reference

**Usage**: Use INDEX.md to find relevant analyses by category, PLAN, or topic

---

## 🎯 Quick Reference Decision Tree

**Should I create an EXECUTION_ANALYSIS?**

```
Facing issue or decision?
├─ Bug/Regression? → Category 1: Bug/Issue Analysis
├─ Methodology question? → Category 2: Methodology Review
├─ Implementation review needed? → Category 3: Implementation Review
├─ Process/workflow issue? → Category 4: Process Analysis
└─ Strategic decision? → Category 5: Planning & Strategy
```

**When NOT to Create**:
- Simple, clear path forward (just proceed)
- Well-understood issue (fix directly)
- Routine work (use EXECUTION_TASK for tracking)

---

## 📋 Category Summary Table

| Category | Purpose | When to Create | Archive Location | Template |
|----------|---------|----------------|------------------|----------|
| **Bug/Issue Analysis** | Analyze bugs, root causes, fixes | Bug discovered, regression | `bug-analysis/YYYY-MM/` | BUG-TEMPLATE |
| **Methodology Review** | Review compliance, extract learnings | PLAN completion, periodic review | `methodology-review/YYYY-MM/` | METHODOLOGY-REVIEW-TEMPLATE |
| **Implementation Review** | Review implementation quality | Achievement review, external feedback | `implementation-review/YYYY-MM/` | IMPLEMENTATION-REVIEW-TEMPLATE |
| **Process Analysis** | Analyze workflows, processes | Process issues, performance problems | `process-analysis/YYYY-MM/` | PROCESS-ANALYSIS-TEMPLATE |
| **Planning & Strategy** | Strategic decisions, design choices | Before PLAN creation, design decisions | `planning-strategy/YYYY-MM/` | PLANNING-STRATEGY-TEMPLATE |

---

## 🔗 Integration with Methodology

### START_POINT Protocol

**When Planning**: Consider creating EXECUTION_ANALYSIS for strategic decisions
- See `LLM/protocols/IMPLEMENTATION_START_POINT.md` → "Strategic Decision Support"

### RESUME Protocol

**When Resuming**: Review relevant EXECUTION_ANALYSIS documents
- See `LLM/protocols/IMPLEMENTATION_RESUME.md` → "Understand Context" checklist

### END_POINT Protocol

**When Completing**: Create completion review (Category 2)
- See `LLM/protocols/IMPLEMENTATION_END_POINT.md` → "EXECUTION_ANALYSIS Completion Review"

### LLM-METHODOLOGY.md

**Reference**: See `LLM-METHODOLOGY.md` → "EXECUTION_ANALYSIS Documents" section for methodology integration

---

## 📚 Examples by Category

### Category 1: Bug Analysis
- `EXECUTION_ANALYSIS_PROMPT-GENERATOR-0.1-BUG.md`
- `EXECUTION_ANALYSIS_PROMPT-GENERATOR-REGRESSION-BUG.md`
- `EXECUTION_ANALYSIS_COMPLETION-DETECTION-FALSE-POSITIVE.md`

### Category 2: Methodology Review
- `EXECUTION_ANALYSIS_METHODOLOGY-REVIEW.md`
- `EXECUTION_ANALYSIS_METHODOLOGY-GAP-ANALYSIS.md`
- `EXECUTION_ANALYSIS_CODE-QUALITY-COMPLETION-REVIEW.md`

### Category 3: Implementation Review
- `EXECUTION_ANALYSIS_API-REVIEW.md`
- `EXECUTION_ANALYSIS_ENTITY-RESOLUTION-BUGS.md`
- `EXECUTION_ANALYSIS_GRAPH-CONSTRUCTION-REVIEW.md`

### Category 4: Process Analysis
- `EXECUTION_ANALYSIS_FILE-MOVING-PERFORMANCE.md`
- `EXECUTION_ANALYSIS_NEW-SESSION-CONTEXT-GAP.md`
- `EXECUTION_ANALYSIS_RESUME-PROTOCOL-GAPS.md`

### Category 5: Planning & Strategy
- `EXECUTION_ANALYSIS_PROMPT-AUTOMATION-STRATEGY.md`
- `EXECUTION_ANALYSIS_PLAN-COMPLETION-VERIFICATION-GAP.md`
- `EXECUTION_ANALYSIS_TESTING-REQUIREMENTS-GAP.md`

**Note**: All examples are archived in `documentation/archive/execution-analyses/` by category and date.

---

## 🛠️ Automation & Tools

### Scripts (When Created)

**Location**: `LLM/scripts/analysis/`

1. **`generate_execution_analysis.py`**: Interactive template selection and file creation
2. **`categorize_execution_analysis.py`**: Auto-detect or suggest category
3. **`archive_execution_analysis.py`**: Move to archive and update INDEX.md
4. **`list_execution_analyses.py`**: List by category, date, PLAN, or keyword

**Status**: Planned (see `PLAN_EXECUTION-ANALYSIS-INTEGRATION.md` Priority 3)

---

## 📝 Best Practices

### When Creating

1. **Choose correct category** (use decision tree above)
2. **Use template** (when available) for structure
3. **Include metadata** (Purpose, Date, Status, Related, Category)
4. **Link related analyses** (if building on previous work)
5. **Be specific** (clear problem statement, actionable recommendations)

### When Archiving

1. **Wait 30 days** after completion (unless related PLAN archived)
2. **Update INDEX.md** when archiving
3. **Check references** (ensure no broken links)
4. **Mark superseded** if replaced by newer analysis

### When Referencing

1. **Use INDEX.md** to find relevant analyses
2. **Check archive** by category or date
3. **Link to analyses** when referencing in PLANs or other documents
4. **Track lineage** (link related analyses together)

---

## 🔗 Related Documentation

- **`LLM-METHODOLOGY.md`**: Methodology overview with EXECUTION_ANALYSIS section
- **`LLM/protocols/IMPLEMENTATION_START_POINT.md`**: Strategic decision guidance
- **`LLM/protocols/IMPLEMENTATION_RESUME.md`**: Analysis review step
- **`LLM/protocols/IMPLEMENTATION_END_POINT.md`**: Completion review protocol
- **Templates**: `LLM/templates/EXECUTION_ANALYSIS-*-TEMPLATE.md` (when created)
- **Archive**: `documentation/archive/execution-analyses/` with INDEX.md catalog

---

**Status**: Complete  
**Maintained By**: `PLAN_EXECUTION-ANALYSIS-INTEGRATION.md`  
**Last Updated**: 2025-11-08

