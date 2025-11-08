# SUBPLAN: Plan Size Limits (600 lines / 32 hours)

**Mother Plan**: PLAN_METHODOLOGY-V2-ENHANCEMENTS.md  
**Achievement Addressed**: Achievement 1.1 (Plan Size Limits)  
**Status**: In Progress  
**Created**: 2025-11-07  
**Estimated Effort**: 2 hours

---

## 🎯 Objective

Implement stricter size limits for PLANs (600 lines / 32 hours) to prevent context overload and enforce GrammaPlan consideration. This includes updating templates, guides, and creating a blocking validation script.

---

## 📋 What Needs to Be Created

### Files to Create

1. **LLM/scripts/check_plan_size.py**:
   - Blocking validation script
   - Checks PLAN file size (lines)
   - Checks estimated effort (hours)
   - Exits with error if limits exceeded
   - Provides feedback prompt for fixing

### Files to Modify

1. **LLM/templates/PLAN-TEMPLATE.md**:
   - Add size limit warnings
   - Add GrammaPlan consideration section
   - Update with 600-line / 32-hour limits

2. **LLM/guides/GRAMMAPLAN-GUIDE.md**:
   - Update decision criteria with new limits
   - Clarify when GrammaPlan is required (not optional)

---

## 📝 Approach

**Strategy**: Update documentation first, then build blocking validation

**Method**:

### Phase 1: Update Templates (30 min)

**Goal**: Document new size limits in PLAN template

**Steps**:
1. Read current PLAN-TEMPLATE.md
2. Add "Size Limits" section:
   - Hard limit: 600 lines
   - Hard limit: 32 hours estimated effort
   - If exceeded: Must use GrammaPlan
3. Add "GrammaPlan Consideration" section:
   - Decision criteria checklist
   - Link to GRAMMAPLAN-GUIDE.md

**Test**: Template includes size limits and GrammaPlan guidance

### Phase 2: Update GrammaPlan Guide (30 min)

**Goal**: Update decision criteria with new limits

**Steps**:
1. Read current GRAMMAPLAN-GUIDE.md
2. Update "Decision Criteria" section:
   - Replace 800 lines → 600 lines
   - Replace 80 hours → 32 hours
   - Clarify: Exceeding limits = GrammaPlan REQUIRED (not optional)
3. Update examples to reflect new limits

**Test**: Guide reflects 600/32 limits and mandatory nature

### Phase 3: Build Validation Script (1 hour)

**Goal**: Create blocking script that enforces limits

**Steps**:
1. Create LLM/scripts/check_plan_size.py
2. Functions:
   - `count_lines(file_path)` → int
   - `extract_estimated_effort(content)` → int (hours)
   - `check_limits(file_path)` → (bool, str) (pass/fail, message)
3. CLI:
   - `python check_plan_size.py @PLAN_FILE.md`
   - Exit code 0 if within limits
   - Exit code 1 if exceeded (with error message)
4. Error message includes:
   - Current size vs limit
   - Recommendation: Use GrammaPlan
   - Link to GRAMMAPLAN-GUIDE.md

**Test**: Script correctly identifies oversized PLANs

---

## ✅ Expected Results

### Functional Changes

1. **PLAN Template Updated**: Size limits documented (600 lines / 32 hours)
2. **GrammaPlan Guide Updated**: Decision criteria reflect new limits
3. **Validation Script**: Blocks oversized PLANs automatically

### Observable Outcomes

1. **Template Clarity**: New PLANs include size limit warnings
2. **Guide Accuracy**: Decision criteria match new limits
3. **Automated Enforcement**: Script prevents oversized PLANs

### Deliverables

- LLM/templates/PLAN-TEMPLATE.md (updated with size limits)
- LLM/guides/GRAMMAPLAN-GUIDE.md (updated with 600/32 limits)
- LLM/scripts/check_plan_size.py (blocking validation script)

---

## 🧪 Tests Required

### Test File
- Manual verification (read files, run script)

### Test Cases to Cover

1. **Template Updated**:
   - Size limits section exists
   - GrammaPlan consideration section exists
   - Limits are 600 lines / 32 hours

2. **Guide Updated**:
   - Decision criteria use 600/32 limits
   - GrammaPlan is REQUIRED (not optional) when limits exceeded

3. **Script Works**:
   - Detects PLANs within limits (exit 0)
   - Detects PLANs exceeding limits (exit 1)
   - Error message helpful

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] PLAN-TEMPLATE.md updated with 600/32 limits
- [ ] GRAMMAPLAN-GUIDE.md updated with 600/32 limits
- [ ] check_plan_size.py created and working
- [ ] Script blocks oversized PLANs
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
- Current PLAN-TEMPLATE.md
- Current GRAMMAPLAN-GUIDE.md
- EXECUTION_ANALYSIS_METHODOLOGY-V2-ENHANCED-STRATEGY.md (Tier 1 insights)

---

**Ready to Execute**: Create EXECUTION_TASK and begin implementation  
**Reference**: 3-phase approach (Template, Guide, Script)  
**Mother PLAN**: PLAN_METHODOLOGY-V2-ENHANCEMENTS.md

