# SUBPLAN: Update Prompt Generator with Project Context

**Mother Plan**: PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md  
**Achievement Addressed**: Achievement 2.1 (Update Prompt Generator with Project Context)  
**Status**: In Progress  
**Created**: 2025-11-08 01:30 UTC  
**Estimated Effort**: 1-2 hours

---

## 🎯 Objective

Update `LLM/scripts/generation/generate_prompt.py` to automatically inject project context from `LLM/PROJECT-CONTEXT.md` into generated prompts. This ensures that LLMs starting new sessions have access to essential project knowledge (structure, domain, conventions, architecture) without requiring manual context addition to each PLAN.

**Contribution to PLAN**: This is part of Phase 2 (Context Enhancement Phase 2) that automates context injection. By updating the prompt generator, we ensure that all generated prompts include project context automatically, addressing the context gap identified in analysis where LLMs lack procedural knowledge when starting fresh.

---

## 📋 What Needs to Be Created

### Files to Modify

1. **LLM/scripts/generation/generate_prompt.py**
   - Add function to read and inject PROJECT-CONTEXT.md
   - Add project context section to prompt template
   - Ensure context is included in all generated prompts
   - Make context injection optional/configurable

### Content to Add

**New Function**:
- `inject_project_context() -> str`: Reads `LLM/PROJECT-CONTEXT.md` and returns formatted context section
- Handles file not found gracefully
- Formats context for prompt inclusion

**Prompt Template Update**:
- Add "Project Context" section after "Context Boundaries" section
- Include key sections from PROJECT-CONTEXT.md (Overview, Structure, Conventions)
- Keep context concise but comprehensive

**Configuration**:
- Add `--no-project-context` flag to disable context injection (for testing)
- Default: context injection enabled

---

## 📝 Approach

**Strategy**: Enhance existing prompt generator to automatically inject project context from PROJECT-CONTEXT.md.

**Method**:

1. **Read Current Prompt Generator**: Review `generate_prompt.py` structure and template
2. **Add Context Injection Function**: Create function to read and format PROJECT-CONTEXT.md
3. **Update Prompt Template**: Add project context section to generated prompts
4. **Add Configuration**: Add flag to enable/disable context injection
5. **Test Context Injection**: Verify context is included in generated prompts
6. **Handle Edge Cases**: Gracefully handle missing PROJECT-CONTEXT.md file

**Key Considerations**:

- **Integration**: Context injection must integrate seamlessly with existing prompt structure
- **Performance**: Reading PROJECT-CONTEXT.md should not significantly slow down prompt generation
- **Flexibility**: Should be configurable (can disable for testing)
- **Graceful Degradation**: Should work even if PROJECT-CONTEXT.md is missing

**Risks to Watch For**:

- Breaking existing prompt generation
- Making prompts too long (context budget concerns)
- Performance degradation
- Missing edge cases (file not found, etc.)

---

## 🧪 Tests Required (Validation Approach)

**Validation Method** (code work):

**Functionality Check**:
- [ ] Context injection function works
- [ ] Context included in generated prompts
- [ ] Context section properly formatted
- [ ] Graceful handling of missing PROJECT-CONTEXT.md

**Integration Validation**:
- [ ] Existing prompt generation still works
- [ ] Context integrates well with existing prompt structure
- [ ] No breaking changes to prompt format

**Configuration Validation**:
- [ ] `--no-project-context` flag disables context injection
- [ ] Default behavior includes context

**Review Against Requirements**:
- [ ] Achievement 2.1 requirements met
- [ ] Success criteria from PLAN met
- [ ] All deliverables present

**Verification Commands**:
```bash
# Verify prompt generator works
python LLM/scripts/generation/generate_prompt.py @PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md --next

# Check for project context in generated prompt
python LLM/scripts/generation/generate_prompt.py @PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md --next | grep -i "project context"

# Test with --no-project-context flag
python LLM/scripts/generation/generate_prompt.py @PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md --next --no-project-context | grep -i "project context" || echo "Context disabled correctly"

# Verify graceful degradation (temporarily rename PROJECT-CONTEXT.md)
mv LLM/PROJECT-CONTEXT.md LLM/PROJECT-CONTEXT.md.bak
python LLM/scripts/generation/generate_prompt.py @PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md --next
mv LLM/PROJECT-CONTEXT.md.bak LLM/PROJECT-CONTEXT.md
```

---

## ✅ Expected Results

### Functional Changes

- **Context Injection**: Prompt generator automatically includes project context
- **Configurable**: Can disable context injection with flag
- **Graceful Degradation**: Works even if PROJECT-CONTEXT.md is missing

### Observable Outcomes

- Generated prompts include "Project Context" section
- Context section contains key information from PROJECT-CONTEXT.md
- Prompt generation still works as before
- No breaking changes to prompt format

### Success Indicators

- ✅ Context injection function implemented
- ✅ Context included in generated prompts
- ✅ Configuration flag works
- ✅ Graceful handling of missing file
- ✅ All verification commands pass

---

## 🔍 Conflict Analysis with Other Subplans

**Review Existing Subplans**:
- SUBPLAN_01: Achievement 0.1 (Fix Archive Location Issues) - Complete
- SUBPLAN_11: Achievement 1.1 (Enhance PLAN_FILE-MOVING-OPTIMIZATION.md Context) - Complete
- SUBPLAN_12: Achievement 1.2 (Create PROJECT-CONTEXT.md) - Complete

**Check for**:
- **Overlap**: No overlap (different achievements)
- **Conflicts**: None
- **Dependencies**: Depends on Achievement 1.2 (PROJECT-CONTEXT.md must exist)
- **Integration**: This uses PROJECT-CONTEXT.md created in Achievement 1.2

**Analysis**:
- No conflicts detected
- Safe dependency (PROJECT-CONTEXT.md already created)
- Safe to proceed

**Result**: Safe to proceed

---

## 🔗 Dependencies

### Other Subplans
- **SUBPLAN_12**: Achievement 1.2 (Create PROJECT-CONTEXT.md) - Required (PROJECT-CONTEXT.md must exist)

### External Dependencies
- None (code work only)

### Prerequisite Knowledge
- Understanding of prompt generator structure
- Understanding of PROJECT-CONTEXT.md format
- Python file I/O

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

_None yet - will be created when execution starts_

**First Execution**: `EXECUTION_TASK_NEW-SESSION-CONTEXT-ENHANCEMENT_21_01.md`

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] Context injection function implemented
- [ ] Context included in generated prompts
- [ ] Configuration flag works
- [ ] Graceful handling of missing file
- [ ] All verification commands pass
- [ ] EXECUTION_TASK complete
- [ ] Ready for archive

---

## 📝 Notes

**Common Pitfalls**:
- Breaking existing prompt generation
- Making prompts too long
- Not handling missing file gracefully
- Performance degradation

**Resources**:
- PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md (Achievement 2.1 section)
- EXECUTION_ANALYSIS_NEW-SESSION-CONTEXT-GAP.md (context gap analysis)
- LLM/scripts/generation/generate_prompt.py (target file to modify)
- LLM/PROJECT-CONTEXT.md (context source)

---

## 📖 What to Read (Focus Rules)

**When working on this SUBPLAN**, follow these focus rules to minimize context:

**✅ READ ONLY**:
- This SUBPLAN file (complete file)
- Parent PLAN Achievement 2.1 section (20 lines)
- Active EXECUTION_TASKs (if any exist)
- Parent PLAN "Current Status & Handoff" section (18 lines)
- LLM/scripts/generation/generate_prompt.py (for modification)
- LLM/PROJECT-CONTEXT.md (for context source - minimal reading)

**❌ DO NOT READ**:
- Parent PLAN full content
- Other achievements in PLAN
- Other SUBPLANs
- Completed EXECUTION_TASKs (unless needed for context)
- Full codebase (only prompt generator file)

**Context Budget**: ~400 lines

**Why**: SUBPLAN defines HOW to achieve one achievement. Reading other achievements or full PLAN adds scope and confusion.

**📖 See**: `LLM/guides/FOCUS-RULES.md` for complete focus rules and examples.

---

## 🔄 Active EXECUTION_TASKs (Updated When Created)

**Current Active Work** (register EXECUTION_TASKs immediately when created):

- [ ] **EXECUTION_TASK_NEW-SESSION-CONTEXT-ENHANCEMENT_21_01**: Status: In Progress

**Registration Workflow**:

1. When creating EXECUTION_TASK: Add to this list immediately
2. When archiving: Remove from this list

**Why**: Immediate parent awareness ensures SUBPLAN knows about its active EXECUTION_TASKs.

---

**Ready to Execute**: Create EXECUTION_TASK and begin work  
**Reference**: IMPLEMENTATION_START_POINT.md for workflows

