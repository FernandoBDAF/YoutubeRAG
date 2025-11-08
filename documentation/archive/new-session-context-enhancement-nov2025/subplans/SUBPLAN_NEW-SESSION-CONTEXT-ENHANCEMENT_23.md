# SUBPLAN: Update Achievement Sections with Archive Instructions

**Mother Plan**: PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md  
**Achievement Addressed**: Achievement 2.3 (Update Achievement Sections with Archive Instructions)  
**Status**: In Progress  
**Created**: 2025-11-08 01:52 UTC  
**Estimated Effort**: 30 minutes

---

## 🎯 Objective

Update achievement sections in `LLM/templates/PLAN-TEMPLATE.md` to include explicit archive location instructions. This ensures that LLMs creating new PLANs will include archive location guidance in achievement sections, preventing archive location mismatches like those identified in the work review analysis.

**Contribution to PLAN**: This is part of Phase 2 (Context Enhancement Phase 2) that updates templates with archive instructions. By updating achievement sections, we ensure that all new PLANs include explicit archive location guidance, addressing the procedural error where LLMs used wrong archive locations.

---

## 📋 What Needs to Be Created

### Files to Modify

1. **LLM/templates/PLAN-TEMPLATE.md**
   - Update achievement section template/example
   - Add archive location instructions to achievement format
   - Include guidance on archive structure creation
   - Reference archive location from PLAN's "Archive Location" section

### Content to Add

**Archive Instructions in Achievement Sections**:
- Reference to PLAN's "Archive Location" section
- Instructions to create archive structure if needed
- Guidance on archive location format (documentation/archive/FEATURE-NAME/)
- Note about deferred archiving policy

---

## 📝 Approach

**Strategy**: Update achievement section example/format in PLAN template to include archive location instructions.

**Method**:

1. **Read Current Template**: Review achievement section format in PLAN template
2. **Identify Update Points**: Find achievement examples/sections
3. **Add Archive Instructions**: Insert archive location guidance in achievement format
4. **Verify Integration**: Ensure new content integrates well with existing template
5. **Verify Completeness**: Check all required elements are included

**Key Considerations**:

- **Integration**: New content must integrate seamlessly with existing template
- **Clarity**: Instructions must be clear and actionable
- **Consistency**: Format must match existing template structure
- **Completeness**: All required elements must be included

**Risks to Watch For**:

- Breaking existing template structure
- Missing required elements
- Unclear instructions
- Inconsistent formatting

---

## 🧪 Tests Required (Validation Approach)

**Validation Method** (documentation work):

**Completeness Check**:
- [ ] Archive instructions added to achievement section format
- [ ] Reference to PLAN's "Archive Location" section included
- [ ] Guidance on archive structure creation included
- [ ] Note about deferred archiving policy included

**Structure Validation**:
- [ ] Content integrates well with existing template
- [ ] Formatting consistent with template structure
- [ ] Clear and actionable instructions

**Review Against Requirements**:
- [ ] Achievement 2.3 requirements met
- [ ] Success criteria from PLAN met
- [ ] All deliverables present

**Verification Commands**:
```bash
# Verify template file exists and updated
ls LLM/templates/PLAN-TEMPLATE.md

# Check for archive instructions in achievement sections
grep -A 5 -i "archive" LLM/templates/PLAN-TEMPLATE.md | grep -i "achievement" | head -10

# Check for archive location reference
grep -i "archive location\|Archive Location" LLM/templates/PLAN-TEMPLATE.md
```

---

## ✅ Expected Results

### Functional Changes

- **Template Updated**: Achievement sections include archive location instructions
- **Guidance Added**: Clear instructions on archive location and structure
- **Integration**: Content integrates seamlessly with existing template

### Observable Outcomes

- Achievement section format includes archive instructions
- Reference to PLAN's "Archive Location" section present
- Guidance on archive structure creation included
- Template structure maintained

### Success Indicators

- ✅ Archive instructions added to achievement section format
- ✅ Reference to PLAN's "Archive Location" section included
- ✅ Guidance on archive structure creation included
- ✅ All verification commands pass
- ✅ Content integrates well with existing template

---

## 🔍 Conflict Analysis with Other Subplans

**Review Existing Subplans**:
- SUBPLAN_01: Achievement 0.1 (Fix Archive Location Issues) - Complete
- SUBPLAN_11: Achievement 1.1 (Enhance PLAN_FILE-MOVING-OPTIMIZATION.md Context) - Complete
- SUBPLAN_12: Achievement 1.2 (Create PROJECT-CONTEXT.md) - Complete
- SUBPLAN_21: Achievement 2.1 (Update Prompt Generator with Project Context) - Complete
- SUBPLAN_22: Achievement 2.2 (Update PLAN Template with Project Context Section) - Complete

**Check for**:
- **Overlap**: No overlap (different achievements)
- **Conflicts**: None
- **Dependencies**: None (can work independently)
- **Integration**: This updates achievement sections, complements template updates in Achievement 2.2

**Analysis**:
- No conflicts detected
- Independent work (updating achievement format)
- Safe to proceed

**Result**: Safe to proceed

---

## 🔗 Dependencies

### Other Subplans
- None (independent work)

### External Dependencies
- None (documentation work only)

### Prerequisite Knowledge
- Understanding of PLAN template structure
- Understanding of archive location format
- Understanding of deferred archiving policy

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

_None yet - will be created when execution starts_

**First Execution**: `EXECUTION_TASK_NEW-SESSION-CONTEXT-ENHANCEMENT_23_01.md`

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] Archive instructions added to achievement section format
- [ ] Reference to PLAN's "Archive Location" section included
- [ ] Guidance on archive structure creation included
- [ ] All verification commands pass
- [ ] EXECUTION_TASK complete
- [ ] Ready for archive

---

## 📝 Notes

**Common Pitfalls**:
- Missing required elements
- Unclear instructions
- Breaking existing template structure
- Inconsistent formatting

**Resources**:
- PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md (Achievement 2.3 section)
- EXECUTION_ANALYSIS_NEW-SESSION-WORK-REVIEW.md (archive location issues analysis)
- LLM/templates/PLAN-TEMPLATE.md (target file to modify)

---

## 📖 What to Read (Focus Rules)

**When working on this SUBPLAN**, follow these focus rules to minimize context:

**✅ READ ONLY**:
- This SUBPLAN file (complete file)
- Parent PLAN Achievement 2.3 section (19 lines)
- Active EXECUTION_TASKs (if any exist)
- Parent PLAN "Current Status & Handoff" section (18 lines)
- LLM/templates/PLAN-TEMPLATE.md (for modification - achievement sections only)

**❌ DO NOT READ**:
- Parent PLAN full content
- Other achievements in PLAN
- Other SUBPLANs
- Completed EXECUTION_TASKs (unless needed for context)
- Full template (only achievement sections)

**Context Budget**: ~400 lines

**Why**: SUBPLAN defines HOW to achieve one achievement. Reading other achievements or full PLAN adds scope and confusion.

**📖 See**: `LLM/guides/FOCUS-RULES.md` for complete focus rules and examples.

---

## 🔄 Active EXECUTION_TASKs (Updated When Created)

**Current Active Work** (register EXECUTION_TASKs immediately when created):

- [ ] **EXECUTION_TASK_NEW-SESSION-CONTEXT-ENHANCEMENT_23_01**: Status: In Progress

**Registration Workflow**:

1. When creating EXECUTION_TASK: Add to this list immediately
2. When archiving: Remove from this list

**Why**: Immediate parent awareness ensures SUBPLAN knows about its active EXECUTION_TASKs.

---

**Ready to Execute**: Create EXECUTION_TASK and begin work  
**Reference**: IMPLEMENTATION_START_POINT.md for workflows

