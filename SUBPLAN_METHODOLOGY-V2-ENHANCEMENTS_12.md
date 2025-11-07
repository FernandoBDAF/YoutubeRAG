# SUBPLAN: EXECUTION_TASK Size Limits (200 lines)

**Mother Plan**: PLAN_METHODOLOGY-V2-ENHANCEMENTS.md  
**Achievement Addressed**: Achievement 1.2 (EXECUTION_TASK Size Limits)  
**Status**: In Progress  
**Created**: 2025-11-07  
**Estimated Effort**: 2 hours

---

## 🎯 Objective

Implement hard size limits for EXECUTION_TASKs (200 lines maximum) to ensure focused work and optimize session context. This includes updating the EXECUTION_TASK template, creating a blocking validation script, and updating the context management guide.

---

## 📋 What Needs to Be Created

### Files to Create

1. **LLM/scripts/check_execution_task_size.py**:
   - Blocking validation script
   - Checks EXECUTION_TASK file size (lines)
   - Exits with error if >200 lines
   - Provides feedback prompt for fixing

### Files to Modify

1. **LLM/templates/EXECUTION_TASK-TEMPLATE.md**:
   - Add size limit warning (200 lines maximum)
   - Add guidance on keeping focused
   - Update with size limit enforcement

2. **LLM/guides/CONTEXT-MANAGEMENT.md**:
   - Add EXECUTION_TASK size limits section
   - Explain why 200-line limit exists
   - Provide strategies for staying within limit

---

## 📝 Approach

**Strategy**: Update documentation first, then build blocking validation

**Method**:

### Phase 1: Update EXECUTION_TASK Template (30 min)

**Goal**: Document 200-line limit in template

**Steps**:
1. Read current EXECUTION_TASK-TEMPLATE.md
2. Add "Size Limits" section:
   - Hard limit: 200 lines maximum
   - If exceeded: Must refactor (condense iteration log, focus on key learnings)
3. Add guidance on keeping focused:
   - Iteration log should be concise
   - Learning summary should capture key points only
   - Remove redundant details

**Test**: Template includes size limits and guidance

### Phase 2: Update Context Management Guide (30 min)

**Goal**: Document EXECUTION_TASK limits in context guide

**Steps**:
1. Read current CONTEXT-MANAGEMENT.md (or create if doesn't exist)
2. Add "EXECUTION_TASK Size Limits" section:
   - Why 200 lines (focused work, context optimization)
   - Strategies for staying within limit
   - What to do if approaching limit
3. Link to EXECUTION_TASK template

**Test**: Guide explains EXECUTION_TASK size limits

### Phase 3: Build Validation Script (1 hour)

**Goal**: Create blocking script that enforces 200-line limit

**Steps**:
1. Create LLM/scripts/check_execution_task_size.py
2. Functions:
   - `count_lines(file_path)` → int
   - `check_limit(file_path)` → (bool, str) (pass/fail, message)
3. CLI:
   - `python check_execution_task_size.py @EXECUTION_TASK_FILE.md`
   - Exit code 0 if within limit
   - Exit code 1 if exceeded (with error message)
4. Error message includes:
   - Current size vs limit
   - Recommendation: Condense iteration log, focus on key learnings
   - Link to template for guidance

**Test**: Script correctly identifies oversized EXECUTION_TASKs

---

## ✅ Expected Results

### Functional Changes

1. **EXECUTION_TASK Template Updated**: Size limit documented (200 lines)
2. **Context Guide Updated**: EXECUTION_TASK limits explained
3. **Validation Script**: Blocks oversized EXECUTION_TASKs automatically

### Observable Outcomes

1. **Template Clarity**: New EXECUTION_TASKs include size limit warnings
2. **Guide Accuracy**: Context management explains EXECUTION_TASK limits
3. **Automated Enforcement**: Script prevents oversized EXECUTION_TASKs

### Deliverables

- LLM/templates/EXECUTION_TASK-TEMPLATE.md (updated with 200-line limit)
- LLM/guides/CONTEXT-MANAGEMENT.md (updated with EXECUTION_TASK limits)
- LLM/scripts/check_execution_task_size.py (blocking validation script)

---

## 🧪 Tests Required

### Test File
- Manual verification (read files, run script)

### Test Cases to Cover

1. **Template Updated**:
   - Size limits section exists
   - Guidance on staying focused exists
   - Limit is 200 lines

2. **Guide Updated**:
   - EXECUTION_TASK size limits section exists
   - Strategies for staying within limit documented

3. **Script Works**:
   - Detects EXECUTION_TASKs within limit (exit 0)
   - Detects EXECUTION_TASKs exceeding limit (exit 1)
   - Error message helpful

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] EXECUTION_TASK-TEMPLATE.md updated with 200-line limit
- [ ] CONTEXT-MANAGEMENT.md updated with EXECUTION_TASK limits
- [ ] check_execution_task_size.py created and working
- [ ] Script blocks oversized EXECUTION_TASKs
- [ ] All tests pass
- [ ] EXECUTION_TASK complete with learnings
- [ ] Files archived immediately

---

## 📝 Notes

**Common Pitfalls**:
- Forgetting to update both template and guide
- Script not actually blocking (just warning)
- Error message not helpful

**Resources**:
- Current EXECUTION_TASK-TEMPLATE.md
- Current CONTEXT-MANAGEMENT.md (if exists)
- EXECUTION_ANALYSIS_METHODOLOGY-V2-ENHANCED-STRATEGY.md (Tier 1 insights)

---

**Ready to Execute**: Create EXECUTION_TASK and begin implementation  
**Reference**: 3-phase approach (Template, Guide, Script)  
**Mother PLAN**: PLAN_METHODOLOGY-V2-ENHANCEMENTS.md

