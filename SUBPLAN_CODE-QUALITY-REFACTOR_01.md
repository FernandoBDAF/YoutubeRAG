# SUBPLAN: Review Methodology Defined

**Mother Plan**: PLAN_CODE-QUALITY-REFACTOR.md  
**Achievement Addressed**: Achievement 0.1  
**Status**: Complete  
**Created**: November 6, 2025  
**Estimated Effort**: 2-4 hours

---

## Objective

Establish a systematic, repeatable methodology for reviewing code across all domains to identify:
1. Common patterns that can be extracted into libraries
2. Code quality improvements (clean code principles)
3. Opportunities for refactoring and consolidation
4. Anti-patterns and technical debt

This methodology will be used for all subsequent domain reviews (GraphRAG, Ingestion, RAG, Chat, Core Infrastructure).

---

## What Needs to Be Created

1. **Review Methodology Document** (`documentation/guides/CODE-REVIEW-METHODOLOGY.md`)
   - Step-by-step process for reviewing a domain
   - Checklist for pattern identification
   - Template for documenting findings
   - Decision framework for library extraction

2. **Findings Template** (section in methodology or separate template)
   - Standardized format for documenting review findings
   - Sections for patterns, opportunities, priorities

3. **Decision Framework** (section in methodology)
   - When to extract code into a library
   - When to refactor in-place
   - Priority assessment criteria
   - Impact vs. effort matrix

---

## Approach

### Step 1: Research Existing Patterns
- Review MASTER-PLAN.md for library vision
- Review existing libraries in `core/libraries/` to understand current structure
- Review recent structured plans (ACTIVE_PLANS.md) to understand recent patterns
- Review clean code principles and best practices

### Step 2: Define Review Process
- Create systematic checklist for reviewing files
- Define what to look for (patterns, anti-patterns, quality issues)
- Create workflow: file → analysis → documentation → prioritization

### Step 3: Create Templates
- Findings template with standard sections
- Pattern documentation format
- Library extraction decision criteria

### Step 4: Define Decision Framework
- Criteria for library extraction (frequency, complexity, reusability)
- Priority framework (impact vs. effort)
- Quick wins identification process

### Step 5: Document Everything
- Create comprehensive methodology guide
- Include examples and use cases
- Make it actionable and self-contained

---

## Tests Required

**No code tests needed** - This is documentation/process work.

**Validation**:
- Methodology is clear and actionable
- Templates are complete and usable
- Decision framework is practical
- Can be used immediately for Achievement 0.2 (Current State Analyzed)

---

## Expected Results

1. **Review Methodology Document** exists and is comprehensive
2. **Findings Template** ready for use in domain reviews
3. **Decision Framework** provides clear guidance
4. **Ready to apply** to Achievement 0.2 (Current State Analyzed) and all domain reviews

---

## Dependencies

- None - This is the foundation achievement

---

## Execution Task Reference

- EXECUTION_TASK_CODE-QUALITY-REFACTOR_01_01.md (to be created)

