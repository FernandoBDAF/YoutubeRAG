# SUBPLAN: Add Mandatory Testing Section to Templates

**Type**: SUBPLAN  
**Mother Plan**: PLAN_TESTING-REQUIREMENTS-ENFORCEMENT.md  
**Plan**: TESTING-REQUIREMENTS-ENFORCEMENT  
**Achievement Addressed**: Achievement 1.1 (Add Mandatory Testing Section to Templates)  
**Achievement**: 1.1  
**Status**: In Progress  
**Created**: 2025-01-28 02:45 UTC  
**Estimated Effort**: 45 minutes (30 min PLAN + 15 min SUBPLAN)

**Metadata Tags**: See `LLM/guides/METADATA-TAGS.md` for virtual organization system

**File Location**: `work-space/subplans/SUBPLAN_TESTING-REQUIREMENTS-ENFORCEMENT_11.md`

---

## 🎯 Objective

Update both PLAN and SUBPLAN templates to require testing section for code work, making testing a mandatory part of the methodology rather than optional. This implements Achievement 1.1 and ensures all future achievements will include test requirements, preventing gaps like the `is_plan_complete()` false positive bug.

---

## 📋 What Needs to Be Created

### Files to Modify

- `LLM/templates/PLAN-TEMPLATE.md` - Add mandatory testing section to achievement format
- `LLM/templates/SUBPLAN-TEMPLATE.md` - Update "Tests Required" section to be mandatory for code work

### Files to Create

- Sample achievement showing testing section (for PLAN template)
- Sample subplan showing testing section (for SUBPLAN template)

---

## 📝 Approach

**Strategy**: Add comprehensive testing requirements section to both templates, making it mandatory for code work while keeping it optional for documentation-only work.

**Method**:

1. **Update PLAN Template**:
   - Locate achievement format section in `PLAN-TEMPLATE.md`
   - Add "Testing Requirements" subsection after "Deliverables"
   - Include all required elements:
     - Test file naming convention
     - Coverage requirement (>90%)
     - Test case examples
     - Integration test guidance
     - Edge case test guidance
     - Reference to test infrastructure
   - Update "Deliverables" section to explicitly include test file
   - Add TDD workflow note
   - Reference good example PLAN

2. **Update SUBPLAN Template**:
   - Locate "Tests Required (if applicable)" section
   - Change from optional to mandatory for code work
   - Add note: "Required for all code implementations, optional for documentation-only work"
   - Ensure test file is in deliverables
   - Reference PLAN template for consistency

3. **Create Sample Achievement**:
   - Create example achievement showing testing section
   - Verify template is clear and actionable

4. **Verify Templates**:
   - Check both templates are updated correctly
   - Ensure consistency between templates
   - Verify all required elements are included

**Key Considerations**:

- Make testing mandatory for code work, optional for documentation
- Provide clear guidance and examples
- Reference existing test infrastructure
- Ensure consistency between PLAN and SUBPLAN templates
- Keep templates actionable and not overwhelming

---

## 🧪 Tests Required

### Validation Approach

- Review updated templates for completeness
- Verify testing section is mandatory for code work
- Check all required elements are included
- Ensure examples are clear and actionable
- Verify consistency between templates

### Test Cases to Verify

1. Testing section appears in achievement format
2. Testing section is mandatory for code work
3. All required elements are included (naming, coverage, examples, guidance)
4. Test file is in deliverables
5. TDD workflow note is present
6. SUBPLAN template updated consistently
7. Examples are clear and actionable

---

## ✅ Expected Results

### Functional Changes

- PLAN template requires testing section for code work
- SUBPLAN template requires testing section for code work
- Both templates provide clear guidance and examples
- Test file explicitly included in deliverables

### Observable Outcomes

- Future PLANs will include testing requirements
- Future SUBPLANs will include testing requirements
- Methodology enforces testing for code work
- Clear guidance prevents testing gaps

### Success Indicators

- Testing section added to PLAN template achievement format
- Testing section mandatory in SUBPLAN template for code work
- All required elements included (naming, coverage, examples, guidance)
- Test file in deliverables
- TDD workflow note present
- Examples clear and actionable
- Templates consistent with each other

---

## 🔍 Conflict Analysis with Other Subplans

**Review Existing Subplans**:

- SUBPLAN_01: Achievement 0.1 (Complete) - No conflicts

**Check for**:

- **Overlap**: No overlap (different achievements)
- **Conflicts**: No conflicts (template updates, no code changes)
- **Dependencies**: None (independent work)
- **Integration**: Results will be used in future achievements (validation script, documentation)

**Analysis**:

- No conflicts detected
- Safe to proceed independently
- Results will inform subsequent achievements

**Result**: Safe to proceed

---

## 🔗 Dependencies

### Other Subplans

- None (independent template updates)

### External Dependencies

- `LLM/templates/PLAN-TEMPLATE.md` (must exist)
- `LLM/templates/SUBPLAN-TEMPLATE.md` (must exist)
- `PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md` (for example reference)

### Prerequisite Knowledge

- Understanding of template structure
- Knowledge of testing requirements from analysis
- Understanding of TDD workflow

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

- [ ] **EXECUTION_TASK_TESTING-REQUIREMENTS-ENFORCEMENT_11_01**: Status: In Progress

**First Execution**: `EXECUTION_TASK_TESTING-REQUIREMENTS-ENFORCEMENT_11_01.md`

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] PLAN template updated with mandatory testing section
- [ ] SUBPLAN template updated with mandatory testing section
- [ ] All required elements included (naming, coverage, examples, guidance)
- [ ] Test file in deliverables
- [ ] TDD workflow note present
- [ ] Examples clear and actionable
- [ ] Templates consistent with each other
- [ ] EXECUTION_TASK complete
- [ ] Ready for archive

---

## 📝 Notes

**Key Context**:

- This is template documentation work, not code changes
- Focus on making testing mandatory for code work
- Provide clear guidance to prevent future gaps
- Reference existing good examples

**Common Pitfalls**:

- Don't make testing mandatory for documentation work (only code)
- Don't forget to update both templates consistently
- Don't make templates too verbose (keep actionable)
- Don't forget to include test file in deliverables

**Resources**:

- `LLM/templates/PLAN-TEMPLATE.md` - Template to update
- `LLM/templates/SUBPLAN-TEMPLATE.md` - Template to update
- `PLAN_PROMPT-GENERATOR-FIX-AND-TESTING.md` - Good example of testing requirements
- `tests/LLM/scripts/conftest.py` - Test infrastructure to reference

---

## 📖 What to Read (Focus Rules)

**When working on this SUBPLAN**, follow these focus rules to minimize context:

**✅ READ ONLY**:

- This SUBPLAN file (complete file)
- Parent PLAN Achievement 1.1 section (36 lines)
- Active EXECUTION_TASKs (if any exist)
- Template files being modified (specific sections only)

**❌ DO NOT READ**:

- Parent PLAN full content
- Other achievements in PLAN
- Other SUBPLANs
- Completed EXECUTION_TASKs
- Full template files (only relevant sections)

**Context Budget**: ~400 lines

---

## 🔄 Active EXECUTION_TASKs (Updated When Created)

**Current Active Work** (register EXECUTION_TASKs immediately when created):

- [ ] **EXECUTION_TASK_TESTING-REQUIREMENTS-ENFORCEMENT_11_01**: Status: In Progress

**Registration Workflow**:

1. When creating EXECUTION_TASK: Add to this list immediately
2. When archiving: Remove from this list

---

**Ready to Execute**: Create EXECUTION_TASK and begin work  
**Reference**: IMPLEMENTATION_START_POINT.md for workflows

