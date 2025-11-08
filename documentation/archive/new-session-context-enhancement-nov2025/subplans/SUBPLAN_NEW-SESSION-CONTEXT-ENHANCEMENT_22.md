# SUBPLAN: Update PLAN Template with Project Context Section

**Mother Plan**: PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md  
**Achievement Addressed**: Achievement 2.2 (Update PLAN Template with Project Context Section)  
**Status**: In Progress  
**Created**: 2025-11-08 01:45 UTC  
**Estimated Effort**: 30 minutes

---

## 🎯 Objective

Update `LLM/templates/PLAN-TEMPLATE.md` to include a "Project Context" section that references `LLM/PROJECT-CONTEXT.md`. This ensures that all new PLANs created from the template will include guidance on where to find project context, addressing the context gap for LLMs starting new sessions.

**Contribution to PLAN**: This is part of Phase 2 (Context Enhancement Phase 2) that updates templates to reference project context. By updating the PLAN template, we ensure that all new PLANs include project context guidance, making it easier for LLMs to find essential project knowledge.

---

## 📋 What Needs to Be Created

### Files to Modify

1. **LLM/templates/PLAN-TEMPLATE.md**
   - Add "Project Context" section to template
   - Reference `LLM/PROJECT-CONTEXT.md` as source of project knowledge
   - Include guidance on when to reference project context
   - Place section appropriately (likely in "Context for LLM Execution" section)

### Content to Add

**Project Context Section**:
- Reference to `LLM/PROJECT-CONTEXT.md` as comprehensive project knowledge source
- Guidance on when to reference it (new sessions, unfamiliar domains, etc.)
- Note that prompt generator automatically injects context
- Optional: Brief summary of what's in PROJECT-CONTEXT.md

---

## 📝 Approach

**Strategy**: Add project context reference to PLAN template in the "Context for LLM Execution" section.

**Method**:

1. **Read Current Template**: Review `LLM/templates/PLAN-TEMPLATE.md` structure
2. **Identify Insertion Point**: Find "Context for LLM Execution" section
3. **Add Project Context Section**: Insert new section with reference to PROJECT-CONTEXT.md
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
- [ ] Project Context section added to template
- [ ] Reference to PROJECT-CONTEXT.md included
- [ ] Guidance on when to reference context included
- [ ] Note about prompt generator automatic injection included

**Structure Validation**:
- [ ] Content integrates well with existing template
- [ ] Formatting consistent with template structure
- [ ] Clear and actionable instructions

**Review Against Requirements**:
- [ ] Achievement 2.2 requirements met
- [ ] Success criteria from PLAN met
- [ ] All deliverables present

**Verification Commands**:
```bash
# Verify template file exists and updated
ls LLM/templates/PLAN-TEMPLATE.md

# Check for Project Context section
grep -A 10 "Project Context" LLM/templates/PLAN-TEMPLATE.md

# Check for reference to PROJECT-CONTEXT.md
grep -i "PROJECT-CONTEXT.md\|project context" LLM/templates/PLAN-TEMPLATE.md
```

---

## ✅ Expected Results

### Functional Changes

- **Template Updated**: PLAN template includes project context reference
- **Guidance Added**: Clear instructions on when and how to use project context
- **Integration**: Content integrates seamlessly with existing template

### Observable Outcomes

- PLAN template includes "Project Context" section
- Reference to `LLM/PROJECT-CONTEXT.md` present
- Guidance on context usage included
- Template structure maintained

### Success Indicators

- ✅ Project Context section added to template
- ✅ Reference to PROJECT-CONTEXT.md included
- ✅ Guidance on context usage included
- ✅ All verification commands pass
- ✅ Content integrates well with existing template

---

## 🔍 Conflict Analysis with Other Subplans

**Review Existing Subplans**:
- SUBPLAN_01: Achievement 0.1 (Fix Archive Location Issues) - Complete
- SUBPLAN_11: Achievement 1.1 (Enhance PLAN_FILE-MOVING-OPTIMIZATION.md Context) - Complete
- SUBPLAN_12: Achievement 1.2 (Create PROJECT-CONTEXT.md) - Complete
- SUBPLAN_21: Achievement 2.1 (Update Prompt Generator with Project Context) - Complete

**Check for**:
- **Overlap**: No overlap (different achievements)
- **Conflicts**: None
- **Dependencies**: Depends on Achievement 1.2 (PROJECT-CONTEXT.md must exist) and Achievement 2.1 (prompt generator context injection)
- **Integration**: This updates template to reference context created in Achievement 1.2 and injected in Achievement 2.1

**Analysis**:
- No conflicts detected
- Safe dependencies (both prerequisites complete)
- Safe to proceed

**Result**: Safe to proceed

---

## 🔗 Dependencies

### Other Subplans
- **SUBPLAN_12**: Achievement 1.2 (Create PROJECT-CONTEXT.md) - Required (PROJECT-CONTEXT.md must exist)
- **SUBPLAN_21**: Achievement 2.1 (Update Prompt Generator with Project Context) - Required (context injection must exist)

### External Dependencies
- None (documentation work only)

### Prerequisite Knowledge
- Understanding of PLAN template structure
- Understanding of PROJECT-CONTEXT.md location
- Understanding of prompt generator context injection

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

_None yet - will be created when execution starts_

**First Execution**: `EXECUTION_TASK_NEW-SESSION-CONTEXT-ENHANCEMENT_22_01.md`

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] Project Context section added to PLAN template
- [ ] Reference to PROJECT-CONTEXT.md included
- [ ] Guidance on context usage included
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
- PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md (Achievement 2.2 section)
- LLM/templates/PLAN-TEMPLATE.md (target file to modify)
- LLM/PROJECT-CONTEXT.md (context source to reference)

---

## 📖 What to Read (Focus Rules)

**When working on this SUBPLAN**, follow these focus rules to minimize context:

**✅ READ ONLY**:
- This SUBPLAN file (complete file)
- Parent PLAN Achievement 2.2 section (16 lines)
- Active EXECUTION_TASKs (if any exist)
- Parent PLAN "Current Status & Handoff" section (18 lines)
- LLM/templates/PLAN-TEMPLATE.md (for modification)

**❌ DO NOT READ**:
- Parent PLAN full content
- Other achievements in PLAN
- Other SUBPLANs
- Completed EXECUTION_TASKs (unless needed for context)
- Full PROJECT-CONTEXT.md (only need to know it exists)

**Context Budget**: ~400 lines

**Why**: SUBPLAN defines HOW to achieve one achievement. Reading other achievements or full PLAN adds scope and confusion.

**📖 See**: `LLM/guides/FOCUS-RULES.md` for complete focus rules and examples.

---

## 🔄 Active EXECUTION_TASKs (Updated When Created)

**Current Active Work** (register EXECUTION_TASKs immediately when created):

- [ ] **EXECUTION_TASK_NEW-SESSION-CONTEXT-ENHANCEMENT_22_01**: Status: In Progress

**Registration Workflow**:

1. When creating EXECUTION_TASK: Add to this list immediately
2. When archiving: Remove from this list

**Why**: Immediate parent awareness ensures SUBPLAN knows about its active EXECUTION_TASKs.

---

**Ready to Execute**: Create EXECUTION_TASK and begin work  
**Reference**: IMPLEMENTATION_START_POINT.md for workflows


