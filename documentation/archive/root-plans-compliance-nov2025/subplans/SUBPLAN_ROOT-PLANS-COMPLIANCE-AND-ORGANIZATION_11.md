# SUBPLAN: Update PLAN Files with Missing Sections

**Type**: SUBPLAN  
**Mother Plan**: PLAN_ROOT-PLANS-COMPLIANCE-AND-ORGANIZATION.md  
**Plan**: ROOT-PLANS-COMPLIANCE-AND-ORGANIZATION  
**Achievement Addressed**: Achievement 1.1 (Update PLAN Files with Missing Sections)  
**Achievement**: 1.1  
**Status**: In Progress  
**Created**: 2025-11-08  
**Estimated Effort**: 3-4 hours

**Metadata Tags**: See `LLM/guides/METADATA-TAGS.md` for virtual organization system

**File Location**: `work-space/subplans/SUBPLAN_ROOT-PLANS-COMPLIANCE-AND-ORGANIZATION_11.md`

---

## 🎯 Objective

Add missing required sections to all 11 PLAN files that need updates (2 PLANs are already 100% compliant). Systematically add Project Context reference, Focus Rules, Size Limits, GrammaPlan Consideration, and Archive Location sections. Preserve all existing content and ensure template compliance.

---

## 📋 What Needs to Be Created

### Files to Modify

- **11 PLAN files** (need updates):
  - PLAN_COMMUNITY-DETECTION-REFACTOR.md
  - PLAN_ENTITY-RESOLUTION-ANALYSIS.md
  - PLAN_ENTITY-RESOLUTION-REFACTOR.md
  - PLAN_EXECUTION-ANALYSIS-INTEGRATION.md
  - PLAN_EXTRACTION-QUALITY-ENHANCEMENT.md
  - PLAN_GRAPH-CONSTRUCTION-REFACTOR.md
  - PLAN_GRAPHRAG-VALIDATION.md
  - PLAN_METHODOLOGY-V2-ENHANCEMENTS.md
  - PLAN_METHODOLOGY-VALIDATION.md
  - PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md
  - PLAN_STRUCTURED-LLM-DEVELOPMENT.md

- **2 PLAN files** (already compliant, skip):
  - PLAN_FILE-MOVING-ADVANCED-OPTIMIZATION.md (100%)
  - PLAN_TESTING-REQUIREMENTS-ENFORCEMENT.md (100%)

### Sections to Add (per PLAN based on compliance report)

1. **Project Context Reference** (9 PLANs need this)
   - Add to "Context for LLM Execution" section
   - Format: Reference to `LLM/PROJECT-CONTEXT.md`

2. **What to Read (Focus Rules)** (8 PLANs need this)
   - Add complete "What to Read (Focus Rules)" section
   - Use template from PLAN-TEMPLATE.md

3. **Size Limits** (8 PLANs need this)
   - Add "Size Limits" section
   - Document line limits (600 lines) and effort limits (32 hours)
   - Show current size vs. limits

4. **GrammaPlan Consideration** (8 PLANs need this)
   - Add "GrammaPlan Consideration" section
   - Document decision criteria check
   - Explain why single PLAN vs. GrammaPlan

5. **Archive Location** (3 PLANs need this)
   - Add "Archive Location" section
   - Document archive structure
   - Specify archive path

6. **Other Missing Sections** (varies by PLAN):
   - Scope Definition (2 PLANs)
   - Goal section (2 PLANs)
   - Problem Statement (2 PLANs)
   - Context for LLM Execution (1 PLAN)
   - Current Status & Handoff (1 PLAN)

### Files to Create

- Update log: Document which sections were added to which PLANs

---

## 📝 Approach

**Strategy**: Systematic updates following compliance report, prioritizing high-impact sections

**Method**:

1. **Read Compliance Report**:
   - Use `EXECUTION_ANALYSIS_ROOT-PLANS-COMPLIANCE.md` for exact missing sections per PLAN
   - Create update checklist per PLAN

2. **For Each PLAN (11 total)**:
   - Read PLAN file
   - Identify exact location to insert each missing section
   - Add sections using template format
   - Preserve all existing content
   - Update file location references to work-space/ (if any)

3. **Section Addition Order** (for each PLAN):
   - Project Context Reference (in Context for LLM Execution)
   - What to Read (Focus Rules) - after Context for LLM Execution
   - Size Limits - after Scope Definition (or before Desirable Achievements)
   - GrammaPlan Consideration - after Size Limits
   - Archive Location - before Current Status & Handoff
   - Other missing sections as needed

4. **Template Sources**:
   - Use PLAN-TEMPLATE.md for section formats
   - Use PLAN_FILE-MOVING-ADVANCED-OPTIMIZATION.md as reference (100% compliant)
   - Use PLAN_TESTING-REQUIREMENTS-ENFORCEMENT.md as reference (100% compliant)

5. **Create Update Log**:
   - Document which sections added to which PLANs
   - Note any special considerations

**Key Considerations**:

- Preserve all existing content (no deletions)
- Maintain PLAN structure and flow
- Use consistent formatting with template
- For meta-PLANs (METHODOLOGY-V2-ENHANCEMENTS, STRUCTURED-LLM-DEVELOPMENT), verify if missing sections are intentional
- Update file location references if they mention root directory

---

## 🧪 Tests Required

**Note**: Documentation-only work, no code tests required.

**Verification**:
- Run compliance check script after updates to verify all sections present
- Verify no content was lost (compare file sizes before/after)
- Check that all PLANs now have required sections

---

## 📊 Expected Results

**Functional Changes**:
- All 11 PLANs updated with missing sections
- All PLANs now compliant with template requirements
- File location references updated to work-space/ (if needed)

**Observable Outcomes**:
- All PLANs have Project Context reference
- All PLANs have Focus Rules section
- All PLANs have Size Limits section
- All PLANs have GrammaPlan Consideration section
- All PLANs have Archive Location section (where needed)
- Update log created documenting changes

**Compliance Improvement**:
- Average compliance should increase from 59.8% to ~95%+
- All PLANs should have at least 11/13 sections (missing sections may be intentional for meta-PLANs)

---

## 🔗 Dependencies

**Prerequisites**:
- Achievement 0.2 complete (compliance report provides exact missing sections)

**Related Work**:
- Uses `EXECUTION_ANALYSIS_ROOT-PLANS-COMPLIANCE.md` for compliance checklist
- Uses `LLM/templates/PLAN-TEMPLATE.md` for section formats
- Achievement 1.2 depends on this (needs compliant PLANs for naming check)

---

## 📝 Execution Task Reference

- `EXECUTION_TASK_ROOT-PLANS-COMPLIANCE-AND-ORGANIZATION_11_01.md` - First execution

---

**Status**: In Progress  
**Next**: Execute updates systematically for all 11 PLANs

