# EXECUTION_TASK: Update Achievement Sections with Archive Instructions

**Subplan**: SUBPLAN_NEW-SESSION-CONTEXT-ENHANCEMENT_23.md  
**Mother Plan**: PLAN_NEW-SESSION-CONTEXT-ENHANCEMENT.md  
**Achievement**: 2.3 (Update Achievement Sections with Archive Instructions)  
**Execution Number**: 01 (first attempt)  
**Previous Execution**: N/A  
**Circular Debug Flag**: No  
**Started**: 2025-11-08 01:52 UTC  
**Status**: In Progress

---

## 📏 Size Limits

**⚠️ HARD LIMIT**: 200 lines maximum

**Line Budget Guidance**:
- Header + Objective: ~20 lines
- Iteration Log: ~50-80 lines (keep concise!)
- Learning Summary: ~30-50 lines (key points only)
- Completion Status: ~20 lines
- **Total Target**: 120-170 lines (well under 200)

---

## 📖 What We're Building

Updating achievement sections in `LLM/templates/PLAN-TEMPLATE.md` to include explicit archive location instructions. This ensures LLMs creating new PLANs will include archive location guidance in achievement sections.

**Success**: Archive instructions added to achievement section format, reference to PLAN's "Archive Location" section included, guidance on archive structure creation included, all verification passes.

---

## 🧪 Validation Approach (Documentation Work)

**Validation Method**:
- Completeness check (all required elements added)
- Structure validation (content integrates well)
- Review against requirements (Achievement 2.3 met)

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

## 🔄 Iteration Log

### Iteration 1: Read Current Achievement Format
**Date**: 2025-11-08 01:52 UTC  
**Result**: Pass  
**Action**: Reviewed achievement section format in PLAN template  
**Learning**: Achievement sections have basic format (Title, Description, Success, Effort), need to add archive instructions  
**Next Step**: Add archive instructions to achievement format

---

### Iteration 2: Add Archive Instructions to Achievement Format
**Date**: 2025-11-08 01:54 UTC  
**Result**: Pass  
**Action**: Added archive location instructions to achievement section example  
**Fix Applied**:
- File: LLM/templates/PLAN-TEMPLATE.md
- Added: Archive location instructions to achievement format
- Added: Reference to PLAN's "Archive Location" section
- Added: Guidance on archive structure creation (subplans/, execution/)
- Added: Note about deferred archiving policy
- Rationale: Ensures LLMs know where to archive work and how to create archive structure

**Learning**: Instructions should be concise but clear, reference PLAN's archive location section  
**Next Step**: Verify integration and completeness

---

### Iteration 3: Verification
**Date**: 2025-11-08 01:55 UTC  
**Result**: Pass  
**Action**: Verified all required elements are present and integrated well  
**Verification Results**:
- ✅ Archive instructions added to achievement section format
- ✅ Reference to PLAN's "Archive Location" section included
- ✅ Guidance on archive structure creation included
- ✅ Note about deferred archiving policy included
- ✅ Content integrates well with existing template

**Learning**: Verification essential to ensure completeness  
**Next Step**: Complete EXECUTION_TASK

---

## 📚 Learning Summary

**Technical Learnings**:
- Archive instructions must be explicit and actionable
- Reference to PLAN's archive location section helps prevent mismatches
- Guidance on archive structure creation prevents missing directories

**Process Learnings**:
- Systematic approach (read → add → verify) works well
- Verification commands essential to catch missing elements
- Integration is key - new content must fit existing structure

**Mistakes Made & Recovered**:
- None - work was straightforward template update

---

## 💬 Code Comment Map

**Comments Added**:
- Not applicable (documentation work, no code)

---

## 🔮 Future Work Discovered

**During Execution**:
- None (focused on immediate template update)

**Add to Backlog**: N/A

---

## ✅ Completion Status

- [x] Archive instructions added to achievement section format
- [x] Reference to PLAN's "Archive Location" section included
- [x] Guidance on archive structure creation included
- [x] All verification commands pass
- [x] Subplan objectives met
- [x] Execution result: Success
- [x] Ready for archive

**Total Iterations**: 3  
**Total Time**: ~3 minutes  
**Final Status**: Success

---

**Status**: Complete  
**Next**: Archive this EXECUTION_TASK and SUBPLAN, update PLAN statistics

