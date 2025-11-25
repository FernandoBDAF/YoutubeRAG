# SUBPLAN: Create Execution Work Quick Reference

**Type**: SUBPLAN  
**Mother Plan**: PLAN_EXECUTION-TAXONOMY-AND-WORKSPACE.md  
**Plan**: EXECUTION-TAXONOMY-AND-WORKSPACE  
**Achievement Addressed**: Achievement 2.1 (Create Execution Work Quick Reference)  
**Achievement**: 2.1  
**Status**: In Progress  
**Created**: 2025-11-09 16:30 UTC  
**Estimated Effort**: 1-2 hours

---

## 🎯 Objective

Create a concise, one-page quick reference guide for execution work types that enables practitioners to instantly select the correct type (EXECUTION_TASK vs EXECUTION_WORK and specific subtypes) when beginning work. This complements the comprehensive EXECUTION-TAXONOMY.md and provides a printable, accessible decision tool.

---

## 📋 What Needs to Be Created

### Primary Deliverable

**EXECUTION-WORK-QUICK-REFERENCE.md** (1 page, ~150-200 lines)

**Sections**:
1. Taxonomy overview (1 paragraph summarizing 2 types)
2. Visual decision tree (ASCII diagram showing TASK vs WORK branching)
3. Type comparison table (quick side-by-side: TASK vs 5 WORK types)
4. Quick examples (5-10 scenarios with instant answers)
5. When-to-use guidance (clear indicators for each type)
6. Location guide (where files live for each type)
7. Quick reference card (printable format)

### Secondary Deliverables

- Update LLM-METHODOLOGY.md: Add link to quick reference
- Update PROMPTS.md: Add link to quick reference

---

## 📝 Approach

**Strategy**: Extract and condense the most useful parts of EXECUTION-TAXONOMY.md into a single-page reference that enables instant decision-making

**Method**:

1. **Phase 1: Design**
   - Review EXECUTION-TAXONOMY.md sections (decision tree, comparison table, scenarios)
   - Identify most critical decision indicators
   - Plan single-page layout with visual emphasis

2. **Phase 2: Extract & Condense**
   - Create visual decision tree (ASCII diagram)
   - Build type comparison table (condensed vs full)
   - Select 5-10 most representative examples
   - Write concise "when-to-use" guidance

3. **Phase 3: Format for Reference**
   - Ensure printable (fits one page when printed)
   - Use visual hierarchy (headers, emphasis, spacing)
   - Make decision path obvious and fast
   - Include file locations for quick navigation

4. **Phase 4: Integration**
   - Add links from LLM-METHODOLOGY.md and PROMPTS.md
   - Ensure discoverability (users can find it easily)
   - Position as "go here first when unsure about type"

**Key Considerations**:
- Balance between completeness and brevity (must fit one page)
- Visual clarity (decision tree should be scannable)
- Real examples (use scenarios from EXECUTION-TAXONOMY.md)
- Printability (proper formatting for physical reference card)

---

## 🔄 Execution Strategy

**Execution Count**: Single

**Rationale**:
- Straightforward design work (condensing existing taxonomy)
- Single clear approach (extract + format)
- All deliverables created together
- No dependencies on execution order

**EXECUTION_TASK**: `EXECUTION_TASK_EXECUTION-TAXONOMY-AND-WORKSPACE_21_01.md`

---

## 📊 Expected Results

**Deliverables** (to be created by EXECUTION_TASK):

1. ✅ EXECUTION-WORK-QUICK-REFERENCE.md (150-200 lines)
   - Visual decision tree
   - Type comparison table
   - Quick examples
   - When-to-use guidance
   - Location guide
   - Printable format

2. ✅ Updated LLM-METHODOLOGY.md
   - Link to quick reference in appropriate section

3. ✅ Updated PROMPTS.md
   - Link to quick reference for type selection

**Success Criteria**:
- Reference fits one page (visually balanced)
- Decision tree is clear and fast to follow
- Examples cover common scenarios
- Links integrated into methodology docs
- Printable and usable as reference card

**Ready For**: Distribution and use by practitioners working on execution-level tasks

---

## 🧪 Tests Required

N/A - Reference guide (no code testing)

**Validation Instead**:
- Completeness: All work types covered
- Usability: Decision path clear and fast
- Accuracy: Examples match EXECUTION-TAXONOMY.md
- Format: Fits one page, printable
- Integration: Links present in methodology docs

---

## 📚 Related Documents

- **EXECUTION-TAXONOMY.md**: Full taxonomy (this condenses it)
- **LLM-METHODOLOGY.md**: Will be updated with link
- **PROMPTS.md**: Will be updated with link
- **SUBPLAN-WORKFLOW-GUIDE.md**: Reference for workflow

---

## 🎯 Success Metrics

**Usability Metrics**:
- Decision time: <30 seconds to select correct type
- Printability: Fits on one standard page
- Completeness: All 6 types (TASK + 5 WORK) covered

**Integration Metrics**:
- Links present in LLM-METHODOLOGY.md
- Links present in PROMPTS.md
- File discoverable from main guides

---

**Status**: In Progress  
**Next**: Create EXECUTION_TASK to implement this reference guide


