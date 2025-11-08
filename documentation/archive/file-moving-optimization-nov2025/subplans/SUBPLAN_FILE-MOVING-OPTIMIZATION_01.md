# SUBPLAN: Deferred Archiving Policy Implementation

**Mother Plan**: PLAN_FILE-MOVING-OPTIMIZATION.md  
**Achievement Addressed**: Achievement 0.1 (Deferred Archiving Policy Implementation)  
**Status**: In Progress  
**Created**: 2025-01-27 12:00 UTC  
**Estimated Effort**: 2-3 hours

---

## 🎯 Objective

Implement deferred archiving policy by updating all methodology templates, protocols, and scripts to change from immediate archiving (archive files as soon as they're complete) to deferred archiving (archive files at achievement completion or plan completion). This addresses the 95% time waste from immediate archiving operations and eliminates the overhead of moving files individually during execution.

**Contribution to PLAN**: This is the foundation achievement (Priority 0) that enables the other optimizations. By removing immediate archiving requirements, we eliminate the primary source of file moving overhead.

---

## 📋 What Needs to Be Created

### Files to Modify

1. **LLM/protocols/IMPLEMENTATION_END_POINT.md**
   - Remove "immediate archiving" requirement from "Immediate Archiving" section
   - Add "deferred archiving" process documentation
   - Document batch archiving at achievement/plan completion
   - Update archive workflow to reflect deferred approach

2. **LLM/templates/PLAN-TEMPLATE.md**
   - Update "Archive Location" section to clarify deferred archiving
   - Remove immediate archiving references
   - Add guidance on when to archive (achievement completion vs plan completion)

3. **LLM/templates/SUBPLAN-TEMPLATE.md**
   - Remove immediate archiving references
   - Update completion criteria to reflect deferred archiving

4. **LLM/templates/EXECUTION_TASK-TEMPLATE.md**
   - Remove immediate archiving references
   - Update completion status to reflect deferred archiving

5. **LLM/templates/PROMPTS.md**
   - Remove "Archive immediately" from all prompts
   - Add "Archive at achievement completion" guidance
   - Update completion prompts to reflect deferred archiving

6. **LLM/scripts/archiving/archive_completed.py**
   - Add `--batch` flag for batch operations
   - Document deferred usage in script comments
   - Update help text to explain deferred vs immediate usage

### Documentation Updates

- All changes must maintain consistency across documents
- Terminology must be consistent: "deferred archiving" vs "immediate archiving"
- Examples must reflect new policy

---

## 📝 Approach

**Strategy**: Systematic update of all methodology documents to replace immediate archiving with deferred archiving policy. Focus on consistency and clarity.

**Method**:

1. **Read Current State**: Review all target files to understand current immediate archiving references
2. **Update Protocols**: Start with IMPLEMENTATION_END_POINT.md (foundation document)
3. **Update Templates**: Update all templates in sequence (PLAN, SUBPLAN, EXECUTION_TASK)
4. **Update Prompts**: Update PROMPTS.md to reflect new policy
5. **Update Scripts**: Add batch flag to archive_completed.py
6. **Verify Consistency**: Ensure all documents use consistent terminology

**Key Considerations**:

- **Backward Compatibility**: Documents should still work for existing plans that may have used immediate archiving
- **Clarity**: New policy must be clearly explained - when to archive (achievement completion vs plan completion)
- **Consistency**: All documents must use same terminology and process
- **Completeness**: All references to immediate archiving must be found and updated

**Risks to Watch For**:

- Missing references in less obvious places (comments, examples)
- Inconsistent terminology across documents
- Breaking existing workflows that depend on immediate archiving

---

## 🧪 Tests Required

### Validation Approach (Documentation Work)

**Completeness Check**:
- [ ] All 6 target files updated
- [ ] No remaining references to "immediate archiving" (except in historical context)
- [ ] "Deferred archiving" documented in all relevant places

**Structure Validation**:
- [ ] IMPLEMENTATION_END_POINT.md has clear deferred archiving section
- [ ] All templates have consistent archiving guidance
- [ ] PROMPTS.md updated with deferred archiving examples

**Review Against Requirements**:
- [ ] Achievement 0.1 requirements met
- [ ] Success criteria from PLAN met
- [ ] All deliverables present

**Verification Commands**:
```bash
# Check for remaining immediate archiving references
grep -r "immediate archiving" LLM/protocols/ LLM/templates/ --exclude-dir=__pycache__

# Check for deferred archiving documentation
grep -r "deferred archiving" LLM/protocols/ LLM/templates/ --exclude-dir=__pycache__

# Verify archive_completed.py has --batch flag
grep -A 5 "--batch" LLM/scripts/archiving/archive_completed.py
```

---

## ✅ Expected Results

### Functional Changes

- **Archiving Policy**: Changed from immediate (archive as soon as file complete) to deferred (archive at achievement/plan completion)
- **Workflow**: LLM no longer required to archive files immediately upon completion
- **Batch Operations**: Script supports batch archiving for multiple files at once
- **Documentation**: All methodology documents reflect deferred archiving policy

### Observable Outcomes

- **Reduced File Moving**: No more individual file moves during execution
- **Cleaner Workflow**: Files stay in root until achievement/plan completion
- **Batch Efficiency**: Multiple files archived together at completion
- **Clear Guidance**: All templates and prompts guide toward deferred archiving

### Success Indicators

- ✅ All 6 files updated with deferred archiving policy
- ✅ No remaining "immediate archiving" requirements (except historical references)
- ✅ archive_completed.py supports batch operations
- ✅ All documents use consistent terminology
- ✅ Verification commands pass

---

## 🔍 Conflict Analysis with Other Subplans

**Review Existing Subplans**:
- None yet (this is the first SUBPLAN for this PLAN)

**Check for**:
- **Overlap**: No other subplans exist
- **Conflicts**: None
- **Dependencies**: None
- **Integration**: This is foundation work - other achievements may depend on this

**Analysis**:
- No conflicts detected
- This is the first achievement (Priority 0), so no dependencies
- Safe to proceed

**Result**: Safe to proceed

---

## 🔗 Dependencies

### Other Subplans
- None (this is the first SUBPLAN)

### External Dependencies
- None (documentation work only)

### Prerequisite Knowledge
- Understanding of current immediate archiving policy
- Understanding of methodology document structure
- Python script modification (for archive_completed.py)

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

_None yet - will be created when execution starts_

**First Execution**: `EXECUTION_TASK_FILE-MOVING-OPTIMIZATION_01_01.md`

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] IMPLEMENTATION_END_POINT.md updated with deferred archiving
- [ ] PLAN-TEMPLATE.md updated (removed immediate archiving)
- [ ] SUBPLAN-TEMPLATE.md updated (removed immediate archiving)
- [ ] EXECUTION_TASK-TEMPLATE.md updated (removed immediate archiving)
- [ ] PROMPTS.md updated (deferred archiving guidance)
- [ ] archive_completed.py updated (--batch flag added)
- [ ] All verification commands pass
- [ ] EXECUTION_TASK complete
- [ ] Ready for archive

---

## 📝 Notes

**Common Pitfalls**:
- Missing references in comments or examples
- Inconsistent terminology (immediate vs deferred)
- Breaking existing workflows unintentionally

**Resources**:
- PLAN_FILE-MOVING-OPTIMIZATION.md (Achievement 0.1 section)
- Current methodology documents (for reference)
- EXECUTION_ANALYSIS_FILE-MOVING-PERFORMANCE.md (problem analysis)

---

## 📖 What to Read (Focus Rules)

**When working on this SUBPLAN**, follow these focus rules to minimize context:

**✅ READ ONLY**:
- This SUBPLAN file (complete file)
- Parent PLAN Achievement 0.1 section (35 lines)
- Active EXECUTION_TASKs (if any exist)
- Parent PLAN "Current Status & Handoff" section (17 lines)

**❌ DO NOT READ**:
- Parent PLAN full content
- Other achievements in PLAN
- Other SUBPLANs
- Completed EXECUTION_TASKs (unless needed for context)
- Completed work

**Context Budget**: ~400 lines

**Why**: SUBPLAN defines HOW to achieve one achievement. Reading other achievements or full PLAN adds scope and confusion.

**📖 See**: `LLM/guides/FOCUS-RULES.md` for complete focus rules and examples.

---

## 🔄 Active EXECUTION_TASKs (Updated When Created)

**Current Active Work** (register EXECUTION_TASKs immediately when created):

- [ ] **EXECUTION_TASK_FILE-MOVING-OPTIMIZATION_01_01**: Status: In Progress

**Registration Workflow**:

1. When creating EXECUTION_TASK: Add to this list immediately
2. When archiving: Remove from this list

**Why**: Immediate parent awareness ensures SUBPLAN knows about its active EXECUTION_TASKs.

---

**Ready to Execute**: Create EXECUTION_TASK and begin work  
**Reference**: IMPLEMENTATION_START_POINT.md for workflows

