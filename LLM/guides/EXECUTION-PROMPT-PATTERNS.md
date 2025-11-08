# Execution Prompt Patterns Guide

**Purpose**: Standardized natural language patterns for initiating execution work  
**Status**: ✅ Complete  
**Created**: 2025-11-09 19:00 UTC  
**Version**: 1.0

---

## 🎯 Overview

This guide defines 5 core prompt patterns for initiating execution work using natural language. Each pattern routes to a specific document type and template, enabling intuitive creation of execution work without memorizing file names or structures.

**Key Principle**: Natural language first - prompts should feel conversational, not command-like.

---

## 📋 The 5 Core Patterns

### Pattern 1: Analysis

**Purpose**: Initiate structured investigation or strategic planning

**Syntax**:
```
Execution: make an analysis on <TARGET> [for <PURPOSE>]
```

**Routes To**:
- **Document Type**: EXECUTION_ANALYSIS
- **Category**: Category 5 (Planning & Strategy) - default
- **Template**: `LLM/templates/EXECUTION_ANALYSIS-PLANNING-STRATEGY-TEMPLATE.md`
- **Location**: `work-space/analyses/EXECUTION_ANALYSIS_<TOPIC>.md`

**Required Elements**:
- `<TARGET>`: What you're analyzing (feature, system, process, strategy)

**Optional Elements**:
- `[for <PURPOSE>]`: Why you're analyzing it (improvement, decision-making, understanding)

**Examples**:

1. **Strategic Analysis**
   ```
   Execution: make an analysis on the GraphRAG pipeline execution strategy
   ```
   - **Context**: Need to understand how to optimize GraphRAG execution
   - **Routes To**: EXECUTION_ANALYSIS (Planning & Strategy)
   - **Result**: Strategic analysis document with recommendations

2. **Methodology Analysis**
   ```
   Execution: make an analysis on our methodology hierarchy for improvement opportunities
   ```
   - **Context**: Reviewing methodology structure for enhancements
   - **Routes To**: EXECUTION_ANALYSIS (Planning & Strategy)
   - **Result**: Analysis of methodology with improvement suggestions

3. **Product Design Analysis**
   ```
   Execution: make an analysis on terminal CLI tool integrations for product design
   ```
   - **Context**: Designing CLI tool integration strategy
   - **Routes To**: EXECUTION_ANALYSIS (Planning & Strategy)
   - **Result**: Design analysis with integration recommendations

**Variations**:
- "Execution: analyze <TARGET> [for <PURPOSE>]"
- "Execution: investigate <TARGET> [for <PURPOSE>]"
- "Execution: study <TARGET> [for <PURPOSE>]"

**Use Cases**:
- Strategic planning
- Process analysis
- Architecture decisions
- Methodology review
- System design

---

### Pattern 2: Case Study

**Purpose**: Document deep dive with pattern extraction and lessons learned

**Syntax**:
```
Execution: make a case study on <TARGET> [for <PURPOSE>]
```

**Routes To**:
- **Document Type**: EXECUTION_CASE-STUDY
- **Template**: `LLM/templates/EXECUTION_CASE-STUDY-TEMPLATE.md`
- **Location**: `work-space/case-studies/EXECUTION_CASE-STUDY_<FEATURE>.md`

**Required Elements**:
- `<TARGET>`: What you're documenting (feature, refactor, project, pattern)

**Optional Elements**:
- `[for <PURPOSE>]`: Why you're documenting it (pattern extraction, learning, reference)

**Examples**:

1. **Refactor Case Study**
   ```
   Execution: make a case study on the entity resolution refactor
   ```
   - **Context**: Documenting major refactor for future reference
   - **Routes To**: EXECUTION_CASE-STUDY
   - **Result**: Comprehensive case study with patterns and lessons

2. **Coordination Case Study**
   ```
   Execution: make a case study on successful GrammaPlan coordination
   ```
   - **Context**: Extracting patterns from multi-PLAN coordination
   - **Routes To**: EXECUTION_CASE-STUDY
   - **Result**: Case study on coordination strategies

3. **Quality Improvement Case Study**
   ```
   Execution: make a case study on code quality improvements for pattern extraction
   ```
   - **Context**: Documenting quality improvement journey
   - **Routes To**: EXECUTION_CASE-STUDY
   - **Result**: Case study with reusable quality patterns

**Variations**:
- "Execution: document <TARGET> as a case study [for <PURPOSE>]"
- "Execution: create case study on <TARGET> [for <PURPOSE>]"
- "Execution: study <TARGET> in depth [for <PURPOSE>]"

**Use Cases**:
- Documenting major refactors
- Extracting patterns from successful work
- Creating reference material
- Sharing lessons learned
- Building knowledge base

---

### Pattern 3: Review

**Purpose**: Assess implementation quality and identify improvements

**Syntax**:
```
Execution: review the implementation of <TARGET> [for <PURPOSE>]
```

**Routes To**:
- **Document Type**: EXECUTION_ANALYSIS
- **Category**: Category 3 (Implementation Review)
- **Template**: `LLM/templates/EXECUTION_ANALYSIS-IMPLEMENTATION-REVIEW-TEMPLATE.md`
- **Location**: `work-space/analyses/EXECUTION_ANALYSIS_<TARGET>-REVIEW.md`

**Required Elements**:
- `<TARGET>`: What you're reviewing (feature, module, system, implementation)

**Optional Elements**:
- `[for <PURPOSE>]`: Why you're reviewing it (quality, correctness, optimization)

**Examples**:

1. **Feature Review**
   ```
   Execution: review the implementation of entity resolution
   ```
   - **Context**: Post-implementation quality assessment
   - **Routes To**: EXECUTION_ANALYSIS (Implementation Review)
   - **Result**: Review document with quality findings

2. **Verification Review**
   ```
   Execution: review the implementation of PLAN completion verification for quality
   ```
   - **Context**: Ensuring verification logic is correct
   - **Routes To**: EXECUTION_ANALYSIS (Implementation Review)
   - **Result**: Review with quality recommendations

3. **Correctness Review**
   ```
   Execution: review the implementation of graph construction for correctness
   ```
   - **Context**: Verifying graph construction logic
   - **Routes To**: EXECUTION_ANALYSIS (Implementation Review)
   - **Result**: Review with correctness assessment

**Variations**:
- "Execution: assess the implementation of <TARGET> [for <PURPOSE>]"
- "Execution: evaluate <TARGET> implementation [for <PURPOSE>]"
- "Execution: check <TARGET> implementation [for <PURPOSE>]"

**Use Cases**:
- Post-implementation quality checks
- Code review documentation
- Correctness verification
- Performance assessment
- Identifying improvements

---

### Pattern 4: Debug

**Purpose**: Investigate and document bug resolution

**Syntax**:
```
Execution: debug <ISSUE> [in <CONTEXT>]
```

**Routes To**:
- **Document Type**: EXECUTION_ANALYSIS
- **Category**: Category 1 (Bug/Issue Analysis)
- **Template**: `LLM/templates/EXECUTION_ANALYSIS-BUG-TEMPLATE.md`
- **Location**: `work-space/analyses/EXECUTION_ANALYSIS_<ISSUE>-BUG.md`

**Required Elements**:
- `<ISSUE>`: What's broken or failing (bug, error, failure)

**Optional Elements**:
- `[in <CONTEXT>]`: Where the issue occurs (module, feature, system)

**Examples**:

1. **Regression Debug**
   ```
   Execution: debug the prompt generator regression
   ```
   - **Context**: Prompt generator stopped working after changes
   - **Routes To**: EXECUTION_ANALYSIS (Bug Analysis)
   - **Result**: Debug analysis with root cause and fix

2. **Feature Failure Debug**
   ```
   Execution: debug why entity resolution is failing in cross-video linking
   ```
   - **Context**: Entity resolution not working for cross-video scenarios
   - **Routes To**: EXECUTION_ANALYSIS (Bug Analysis)
   - **Result**: Debug analysis with failure explanation and solution

3. **Detection Issue Debug**
   ```
   Execution: debug completion detection false positive
   ```
   - **Context**: Completion detection incorrectly reporting complete
   - **Routes To**: EXECUTION_ANALYSIS (Bug Analysis)
   - **Result**: Debug analysis with false positive root cause

**Variations**:
- "Execution: investigate <ISSUE> [in <CONTEXT>]"
- "Execution: troubleshoot <ISSUE> [in <CONTEXT>]"
- "Execution: fix <ISSUE> [in <CONTEXT>]"

**Use Cases**:
- Bug investigation
- Error root cause analysis
- Failure diagnosis
- Regression debugging
- Issue documentation

---

### Pattern 5: Observation

**Purpose**: Capture real-time feedback during execution or implementation

**Syntax**:
```
Execution: watch <TARGET> to get <FEEDBACK_TYPE>
Execution: observe <TARGET> for <INSIGHTS>
```

**Routes To**:
- **Document Type**: EXECUTION_OBSERVATION
- **Template**: `LLM/templates/EXECUTION_OBSERVATION-TEMPLATE.md`
- **Location**: `work-space/observations/EXECUTION_OBSERVATION_<TOPIC>_<DATE>.md`

**Required Elements**:
- `<TARGET>`: What you're watching (implementation, execution, process)
- `<FEEDBACK_TYPE>` or `<INSIGHTS>`: What you're looking for (performance, quality, behavior)

**Examples**:

1. **Performance Observation**
   ```
   Execution: watch the entity resolution implementation to get feedback on performance
   ```
   - **Context**: Monitoring entity resolution during execution
   - **Routes To**: EXECUTION_OBSERVATION
   - **Result**: Real-time observation document with performance notes

2. **Quality Observation**
   ```
   Execution: observe the GraphRAG pipeline execution for quality insights
   ```
   - **Context**: Capturing quality observations during pipeline run
   - **Routes To**: EXECUTION_OBSERVATION
   - **Result**: Observation document with quality findings

3. **Iterative Feedback Observation**
   ```
   Execution: watch code quality refactor to provide iterative feedback
   ```
   - **Context**: Providing real-time feedback during refactor
   - **Routes To**: EXECUTION_OBSERVATION
   - **Result**: Observation with iterative feedback notes

**Variations**:
- "Execution: monitor <TARGET> for <INSIGHTS>"
- "Execution: track <TARGET> to get <FEEDBACK_TYPE>"
- "Execution: capture <TARGET> observations for <INSIGHTS>"

**Use Cases**:
- Real-time execution monitoring
- Live implementation feedback
- Performance observation
- Quality tracking
- Behavior discovery

---

## 🔄 Extended Pattern Support

### "for <PURPOSE>" Clause

**Purpose**: Specify why you're doing the work

**Syntax**: Add "for <PURPOSE>" to any pattern

**Examples**:
- "Execution: make an analysis on database selection **for architecture decision**"
- "Execution: make a case study on refactor **for pattern extraction**"
- "Execution: review the implementation of API **for quality assurance**"

**Benefits**:
- Clarifies intent
- Provides context
- Guides analysis focus
- Improves documentation

---

### "using <METHOD>" Clause

**Purpose**: Specify how you'll approach the work

**Syntax**: Add "using <METHOD>" to any pattern

**Examples**:
- "Execution: make an analysis on performance **using profiling data**"
- "Execution: debug the issue **using reproduction steps**"
- "Execution: review the implementation **using code quality metrics**"

**Benefits**:
- Specifies methodology
- Sets expectations
- Guides approach
- Documents method

---

## 📊 Quick Reference Table

| Pattern | Syntax | Routes To | Template | Use When |
|---------|--------|-----------|----------|----------|
| **Analysis** | `make an analysis on <TARGET>` | EXECUTION_ANALYSIS (Planning & Strategy) | PLANNING-STRATEGY | Strategic planning, process analysis, architecture decisions |
| **Case Study** | `make a case study on <TARGET>` | EXECUTION_CASE-STUDY | CASE-STUDY | Documenting refactors, extracting patterns, creating reference material |
| **Review** | `review the implementation of <TARGET>` | EXECUTION_ANALYSIS (Implementation Review) | IMPLEMENTATION-REVIEW | Post-implementation quality checks, code review, correctness verification |
| **Debug** | `debug <ISSUE>` | EXECUTION_ANALYSIS (Bug Analysis) | BUG | Bug investigation, error analysis, failure diagnosis, regression debugging |
| **Observation** | `watch <TARGET> to get <FEEDBACK>` | EXECUTION_OBSERVATION | OBSERVATION | Real-time monitoring, live feedback, performance observation, behavior discovery |

---

## 🎯 Pattern Selection Guide

### Decision Tree

```
What do you need to do?

├─ Investigate strategy/process/architecture?
│  └─ Use: Analysis Pattern
│     "Execution: make an analysis on <TARGET>"
│
├─ Document deep dive with lessons?
│  └─ Use: Case Study Pattern
│     "Execution: make a case study on <TARGET>"
│
├─ Assess implementation quality?
│  └─ Use: Review Pattern
│     "Execution: review the implementation of <TARGET>"
│
├─ Fix a bug or investigate failure?
│  └─ Use: Debug Pattern
│     "Execution: debug <ISSUE>"
│
└─ Monitor execution in real-time?
   └─ Use: Observation Pattern
      "Execution: watch <TARGET> to get <FEEDBACK>"
```

---

## 💡 Usage Examples by Domain

### GraphRAG Domain

**Analysis**:
```
Execution: make an analysis on the GraphRAG pipeline execution strategy
```

**Case Study**:
```
Execution: make a case study on GraphRAG observability implementation
```

**Review**:
```
Execution: review the implementation of graph construction
```

**Debug**:
```
Execution: debug entity resolution failures in cross-video linking
```

**Observation**:
```
Execution: observe the GraphRAG pipeline execution for quality insights
```

---

### Methodology Domain

**Analysis**:
```
Execution: make an analysis on our methodology hierarchy for improvement opportunities
```

**Case Study**:
```
Execution: make a case study on successful GrammaPlan coordination
```

**Review**:
```
Execution: review the implementation of PLAN completion verification for quality
```

**Debug**:
```
Execution: debug completion detection false positive
```

**Observation**:
```
Execution: watch methodology evolution to get feedback on effectiveness
```

---

### Code Quality Domain

**Analysis**:
```
Execution: make an analysis on code quality metrics for improvement strategy
```

**Case Study**:
```
Execution: make a case study on code quality improvements for pattern extraction
```

**Review**:
```
Execution: review the implementation of linting integration
```

**Debug**:
```
Execution: debug why code quality checks are failing
```

**Observation**:
```
Execution: watch code quality refactor to provide iterative feedback
```

---

## 🔧 Pattern Variations

### Analysis Pattern Variations

- "Execution: analyze <TARGET> [for <PURPOSE>]"
- "Execution: investigate <TARGET> [for <PURPOSE>]"
- "Execution: study <TARGET> [for <PURPOSE>]"
- "Execution: research <TARGET> [for <PURPOSE>]"

**All route to**: EXECUTION_ANALYSIS (Planning & Strategy)

---

### Case Study Pattern Variations

- "Execution: document <TARGET> as a case study [for <PURPOSE>]"
- "Execution: create case study on <TARGET> [for <PURPOSE>]"
- "Execution: study <TARGET> in depth [for <PURPOSE>]"

**All route to**: EXECUTION_CASE-STUDY

---

### Review Pattern Variations

- "Execution: assess the implementation of <TARGET> [for <PURPOSE>]"
- "Execution: evaluate <TARGET> implementation [for <PURPOSE>]"
- "Execution: check <TARGET> implementation [for <PURPOSE>]"
- "Execution: audit <TARGET> implementation [for <PURPOSE>]"

**All route to**: EXECUTION_ANALYSIS (Implementation Review)

---

### Debug Pattern Variations

- "Execution: investigate <ISSUE> [in <CONTEXT>]"
- "Execution: troubleshoot <ISSUE> [in <CONTEXT>]"
- "Execution: fix <ISSUE> [in <CONTEXT>]"
- "Execution: diagnose <ISSUE> [in <CONTEXT>]"

**All route to**: EXECUTION_ANALYSIS (Bug Analysis)

---

### Observation Pattern Variations

- "Execution: monitor <TARGET> for <INSIGHTS>"
- "Execution: track <TARGET> to get <FEEDBACK_TYPE>"
- "Execution: capture <TARGET> observations for <INSIGHTS>"
- "Execution: follow <TARGET> for <INSIGHTS>"

**All route to**: EXECUTION_OBSERVATION

---

## ⚠️ Anti-Patterns (What NOT to Do)

### ❌ Ambiguous Prompts

**Bad**: "Execution: look at entity resolution"
- **Problem**: Unclear action (analyze? review? debug? observe?)
- **Fix**: Use specific pattern - "Execution: review the implementation of entity resolution"

**Bad**: "Execution: do something with GraphRAG"
- **Problem**: No clear target or action
- **Fix**: Be specific - "Execution: make an analysis on GraphRAG pipeline strategy"

---

### ❌ Mixed Patterns

**Bad**: "Execution: make an analysis and review entity resolution"
- **Problem**: Mixing two patterns in one prompt
- **Fix**: Choose one - "Execution: make an analysis on entity resolution" OR "Execution: review the implementation of entity resolution"

---

### ❌ Missing Target

**Bad**: "Execution: make an analysis"
- **Problem**: No target specified
- **Fix**: Add target - "Execution: make an analysis on database selection strategy"

---

## 🎓 Best Practices

### 1. Be Specific with Targets

**Good**: "Execution: make an analysis on GraphRAG pipeline execution strategy"  
**Better**: "Execution: make an analysis on GraphRAG pipeline execution strategy for performance optimization"

---

### 2. Use Optional Clauses for Clarity

**Good**: "Execution: debug entity resolution failures"  
**Better**: "Execution: debug entity resolution failures in cross-video linking"

---

### 3. Choose the Right Pattern

**Scenario**: Need to understand how to improve GraphRAG performance

**Wrong Pattern**: "Execution: debug GraphRAG performance" (it's not broken)  
**Right Pattern**: "Execution: make an analysis on GraphRAG performance for optimization strategy"

---

### 4. Use Variations Naturally

All these are valid and route to the same place:
- "Execution: make an analysis on database selection"
- "Execution: analyze database selection"
- "Execution: investigate database selection"

Choose the one that feels most natural for your context.

---

## 🔗 Related Documentation

- `LLM/guides/EXECUTION-TAXONOMY.md` - Document type definitions
- `LLM/guides/EXECUTION-WORK-QUICK-REFERENCE.md` - Quick type reference
- `LLM/templates/EXECUTION_ANALYSIS-*-TEMPLATE.md` - Analysis templates
- `LLM/templates/EXECUTION_CASE-STUDY-TEMPLATE.md` - Case study template
- `LLM/templates/EXECUTION_OBSERVATION-TEMPLATE.md` - Observation template

---

## 📋 Summary

**5 Core Patterns**:
1. **Analysis**: Strategic investigation and planning
2. **Case Study**: Deep dive with pattern extraction
3. **Review**: Implementation quality assessment
4. **Debug**: Bug investigation and resolution
5. **Observation**: Real-time execution monitoring

**Key Principles**:
- Natural language first
- Unambiguous routing
- Consistent structure
- Extensible design
- Example-driven

**Next Steps**:
- Use patterns to initiate execution work
- Refer to quick reference table for syntax
- See comprehensive guide for detailed examples
- Consult taxonomy for document type details

---

**Version**: 1.0  
**Status**: ✅ Complete  
**Last Updated**: 2025-11-09  
**Next**: Achievement 0.2 (Design Prompt Routing Logic)




