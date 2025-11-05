# EXECUTION_TASK: [Brief Title]

**Subplan**: SUBPLAN*[FEATURE]*[NUMBER].md  
**Mother Plan**: PLAN\_[FEATURE].md  
**Achievement**: [Which achievement from PLAN]  
**Execution Number**: XX (first attempt, second attempt, etc.)  
**Previous Execution**: [Link if 2nd+ attempt, N/A if first]  
**Circular Debug Flag**: Yes / No [Yes if this is recovery from circular debugging]  
**Started**: [YYYY-MM-DD HH:MM UTC]  
**Status**: In Progress / Complete / Abandoned / Blocked

[FILL: Use UTC timestamps for precise tracking. Example: 2025-11-05 14:30 UTC]

[FILL: Brief title describes what you're doing. Execution number shows if this is 1st, 2nd, 3rd attempt at the subplan.]

[FILL: If this is 2nd+ execution (circular debug recovery), add this note:]
**NOTE**: This is a CIRCULAR DEBUG execution - new strategy after iterations X-Y in EXECUTION*TASK*[FEATURE]_[SUBPLAN]_[PREV] encountered circular debugging.

---

## 📖 What We're Building

[FILL: Brief description of what this execution is creating/implementing]

**Success**: [FILL: How we know we're done]

---

## 🧪 Test Creation Phase (if code work)

**Tests Written**:

- [FILL: List all test names]
- [FILL: Test file: path]

**Initial Test Run**:

- Date: [FILL: timestamp]
- Result: [FILL: All failing (expected) or partial]
- Coverage: [FILL: What the tests cover]

**For Documentation Work**:
[FILL: Describe validation approach instead of tests]

- Completeness check
- Structure validation
- Review against requirements

---

## 🔄 Iteration Log

[FILL: Update this section after EVERY iteration. No exceptions.]

### Iteration 1

**Date**: [YYYY-MM-DD HH:MM UTC]  
**Test Run**: [Which tests ran] / [What was tested]  
**Result**: Pass / Fail / Partial ([X] passed, [Y] failed)  
**Failed Test**: [Test name if failed]  
**Error**: [Exact error message if failed]  
**Root Cause Analysis**: [FILL: WHY it failed - deep analysis, not surface reason]

[FILL: Use UTC timestamps. Update iteration number and timestamp for each iteration.]  
**Fix Applied**:

- File: [FILL: file path]
- Lines: [FILL: line numbers]
- Change: [FILL: what was changed]
- Rationale: [FILL: why this should fix it]

**Learning**: [FILL: What we learned - generalizable insight, not just "fixed the bug"]  
**Code Comments Added**: Yes / No

- [FILL: If Yes: file:line - summary of comment]

**Progress Check**:

- New error: Yes / No
- Making progress: Yes / No
- Strategy effective: Yes / No

**Next Step**: [FILL: What to try next]

[FILL: Copy this iteration template for each iteration. Update iteration number.]

---

### Iteration 2

[FILL: Same structure as Iteration 1]

---

### Circular Debug Check - After Iteration 3

[FILL: Perform this check after every 3 iterations]

**Pattern Detected**: Yes / No  
**Same Error Count**: [How many times same error appeared]  
**Error**: [The repeating error if applicable]  
**Analysis**:

- [FILL: Why are we stuck?]
- [FILL: What's the common pattern?]
- [FILL: What are we missing?]

**Decision**: Continue / Change Strategy

**If Change Strategy**:

- Mark this EXECUTION_TASK as "Abandoned - Circular Debug"
- Create: `EXECUTION_TASK_[FEATURE]_[SUBPLAN]_[NEXT].md`
- New strategy: [FILL: Fundamentally different approach]
- Rationale: [FILL: Why this should work]

[FILL: Repeat this check every 3 iterations]

---

## 📚 Learning Summary

[FILL: Aggregate learnings as you go]

**Technical Learnings**:

- [FILL: Technical insights]
- [FILL: Code patterns discovered]
- [FILL: System behavior learned]

**Process Learnings**:

- [FILL: What worked in approach]
- [FILL: What didn't work]
- [FILL: Strategy changes and why]

**Mistakes Made & Recovered**:

- [FILL: Mistake 1] → [How we recovered]
- [FILL: Mistake 2] → [How we fixed it]

---

## 💬 Code Comment Map

[FILL: Track where learnings were added to code]

**Comments Added**:

- `path/to/file.py:123` (Iteration 2): [Summary of comment - what was learned]
- `path/to/file.py:456` (Iteration 5): [Summary of comment]

[FILL: For documentation work, note "Not applicable"]

---

## 🔮 Future Work Discovered

[FILL: Note ideas that are out of scope but valuable]

**During Iteration [N]**:

- [Future idea 1] - [Why valuable, why not in scope now]
- [Future idea 2] - [Rationale for deferring]

**Add to Backlog**: Yes (during IMPLEMENTATION_END_POINT process)

---

## ✅ Completion Status

- [ ] All tests passing (if code work)
- [ ] All code commented with learnings (if code work)
- [ ] Subplan objectives met
- [ ] Execution result: Success / Abandoned / Blocked
- [ ] If Abandoned: [Link to next EXECUTION_TASK with new strategy]
- [ ] Future work extracted
- [ ] Ready for archive

**Total Iterations**: [N]  
**Total Time**: [hours]  
**Final Status**: Success / Abandoned / Blocked

---

**Status**: [Update as you progress]  
**Next**: [What happens next]
