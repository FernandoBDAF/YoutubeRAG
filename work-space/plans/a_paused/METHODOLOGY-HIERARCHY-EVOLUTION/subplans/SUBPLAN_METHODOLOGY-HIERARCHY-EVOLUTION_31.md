# SUBPLAN: Size Validation Scripts Created/Updated

**Parent PLAN**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md  
**Achievement**: 3.1  
**Created**: 2025-11-08 18:10 UTC  
**Estimated Effort**: 3-4 hours  
**Status**: 🎯 Executing

---

## 🎯 Objective

Create validation scripts for new document types (NORTH_STAR) and update existing scripts to enforce new size limits for all document types.

**Context**: New methodology includes NORTH_STAR document type and updated size limits for PLAN and GrammaPlan. Need validation scripts to enforce these limits and provide actionable feedback.

**Why This Matters**: 
- Enforces size limits automatically
- Prevents documents from growing too large
- Provides actionable feedback for violations
- Supports methodology compliance

---

## 📦 Deliverables

### Primary Deliverables

1. **`LLM/scripts/validation/check_north_star_size.py`**
   - Minimum: 800 lines
   - Warning at 1,500 lines: "Consider splitting into multiple north stars"
   - Error at 2,000 lines: "Must split"
   - Exit code 1 if over limit
   - Accept file path as argument
   - Provide actionable feedback

2. **`LLM/scripts/validation/check_grammaplan_size.py`** (verify/update)
   - Warning at 1,000 lines
   - Error at 1,500 lines
   - Exit code 1 if over limit
   - Accept file path as argument
   - Provide actionable feedback

3. **Updated `LLM/scripts/validation/check_plan_size.py`** (verify/update)
   - Warning at 700 lines (was 400)
   - Error at 900 lines (was 600)
   - Update messaging for new context
   - Accept file path as argument
   - Provide actionable feedback

---

## 🎨 Approach

### Phase 1: Create check_north_star_size.py (1.5h)

**Create Script**:
- Follow pattern from check_plan_size.py and check_grammaplan_size.py
- Implement line count checking
- Add minimum check (800 lines)
- Add warning at 1,500 lines
- Add error at 2,000 lines
- Provide actionable feedback
- Exit code 1 if over limit

**Implementation**:
- Create script structure
- Implement count_lines() function
- Implement check_limits() function
- Add argparse for file path
- Add helpful error messages

### Phase 2: Verify/Update check_grammaplan_size.py (0.5h)

**Verify Script**:
- Check if limits are correct (1,000 warning, 1,500 error)
- Verify exit codes
- Verify actionable feedback
- Update if needed

**Implementation**:
- Read existing script
- Verify limits match requirements
- Update if discrepancies found

### Phase 3: Verify/Update check_plan_size.py (1h)

**Verify/Update Script**:
- Check if limits are correct (700 warning, 900 error)
- Verify messaging reflects new context
- Update if needed

**Implementation**:
- Read existing script
- Verify limits match requirements
- Update messaging if needed
- Ensure actionable feedback

### Phase 4: Testing (0.5h)

**Test All Scripts**:
- Test with files at various sizes
- Test error cases
- Test warning cases
- Verify exit codes
- Verify actionable feedback

---

## 🧪 Tests Required

### Validation Tests

**1. Script Functionality Test**:
- [ ] check_north_star_size.py works with NORTH_STAR file
- [ ] check_grammaplan_size.py works with GrammaPlan file
- [ ] check_plan_size.py works with PLAN file
- [ ] All scripts accept file path argument
- [ ] All scripts provide actionable feedback

**2. Limit Enforcement Test**:
- [ ] NORTH_STAR: Minimum 800 lines enforced
- [ ] NORTH_STAR: Warning at 1,500 lines
- [ ] NORTH_STAR: Error at 2,000 lines
- [ ] GrammaPlan: Warning at 1,000 lines
- [ ] GrammaPlan: Error at 1,500 lines
- [ ] PLAN: Warning at 700 lines
- [ ] PLAN: Error at 900 lines

**3. Exit Code Test**:
- [ ] All scripts exit 0 when within limits
- [ ] All scripts exit 1 when over error limit
- [ ] Scripts provide appropriate warnings

### Manual Validation

**Test Script Usability**:
1. Run each script with valid file
2. Run each script with file over limit
3. Verify error messages are helpful
4. Verify exit codes are correct

---

## 🎯 Expected Results

### Immediate Outcomes

**Scripts Created/Updated**:
- check_north_star_size.py created
- check_grammaplan_size.py verified/updated
- check_plan_size.py verified/updated
- All scripts enforce limits correctly
- All scripts provide actionable feedback

**Quality Metrics**:
- Scripts follow consistent pattern
- Error messages are helpful
- Exit codes are correct
- Actionable feedback provided

---

## 📋 Definition of Done

**All deliverables exist**:
- [ ] `LLM/scripts/validation/check_north_star_size.py` created
- [ ] `LLM/scripts/validation/check_grammaplan_size.py` verified/updated
- [ ] `LLM/scripts/validation/check_plan_size.py` verified/updated

**Quality standards met**:
- [ ] All scripts enforce correct limits
- [ ] All scripts provide actionable feedback
- [ ] All scripts accept file path argument
- [ ] Exit codes are correct

**Validation passed**:
- [ ] Manual test: All scripts work
- [ ] Manual test: Limits enforced correctly
- [ ] File checks: Scripts exist (`ls -1`)

**Documentation complete**:
- [ ] Scripts enforce size limits
- [ ] Actionable feedback provided
- [ ] Ready for use in validation pipeline

---

## 🎓 Success Criteria

**Functional Success**:
- All scripts enforce correct limits
- All scripts provide actionable feedback
- Exit codes are correct

**Quality Success**:
- Scripts follow consistent pattern
- Error messages are helpful
- Actionable feedback provided

**Adoption Success**:
- Scripts used in validation pipeline
- Limits enforced automatically
- Methodology compliance improved

---

## 📚 References

**Parent PLAN**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md (Achievement 3.1)

**Related Documents**:
- `LLM/scripts/validation/check_plan_size.py` (reference for pattern)
- `LLM/scripts/validation/check_grammaplan_size.py` (reference for pattern)
- `LLM/templates/NORTH_STAR-TEMPLATE.md` (reference for NORTH_STAR structure)
- `LLM/guides/NORTH-STAR-GUIDE.md` (reference for NORTH_STAR size limits)

**Size Limits**:
- NORTH_STAR: 800-2,000 lines (warning at 1,500, error at 2,000)
- GrammaPlan: 600-1,500 lines (warning at 1,000, error at 1,500)
- PLAN: 300-900 lines (warning at 700, error at 900)

---

## 🔄 Execution Plan

**Single EXECUTION_TASK** (recommended):
- All work is cohesive (creating/updating validation scripts)
- Sequential phases (create → verify → test)
- Estimated 3-4 hours (fits in single execution)

**Recommended**: Single execution for cohesion

---

**Status**: Ready for execution  
**Next**: Create EXECUTION_TASK_METHODOLOGY-HIERARCHY-EVOLUTION_31_01.md and execute

