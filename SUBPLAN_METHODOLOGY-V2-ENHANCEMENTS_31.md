# SUBPLAN: Blocking Validation Scripts

**Mother Plan**: PLAN_METHODOLOGY-V2-ENHANCEMENTS.md  
**Achievement Addressed**: Achievement 3.1 (Blocking Validation Scripts)  
**Status**: In Progress  
**Created**: 2025-11-07  
**Estimated Effort**: 5-6 hours

---

## 🎯 Objective

Create automated validation scripts that block continuation if methodology rules are violated and provide actionable feedback prompts. This includes scripts for achievement completion, execution start, and mid-plan review.

---

## 📋 What Needs to Be Created

### Files to Create

1. **LLM/scripts/validate_achievement_completion.py**:

   - Validates achievement completion before marking complete
   - Checks: SUBPLAN exists? EXECUTION_TASK exists? Deliverables exist?
   - Blocks with error + fix prompt if issues found

2. **LLM/scripts/validate_execution_start.py**:

   - Validates before starting EXECUTION_TASK
   - Checks: SUBPLAN exists? Parent PLAN exists? Archive location exists?
   - Blocks with error + fix prompt if issues found

3. **LLM/scripts/validate_mid_plan.py**:
   - Auto-triggers at 20h intervals (or manual)
   - Checks: Methodology compliance, statistics accuracy, deliverable existence
   - Blocks with error + fix prompt if issues found

---

## 📝 Approach

**Strategy**: Build each script incrementally, test thoroughly

**Method**:

### Phase 1: Achievement Completion Validator (2 hours)

**Goal**: Block completion if achievement not properly executed

**Steps**:

1. Create validate_achievement_completion.py
2. Functions:
   - `find_achievement_in_plan(plan_path, achievement_num)` → dict
   - `check_subplan_exists(feature, achievement_num)` → bool
   - `check_execution_task_exists(feature, achievement_num)` → bool
   - `check_deliverables_exist(achievement)` → (bool, list) (pass/fail, missing)
   - `validate_achievement(plan_path, achievement_num)` → (bool, str)
3. CLI:
   - `python validate_achievement_completion.py @PLAN_FILE.md --achievement 1.1`
   - Exit code 0 if valid
   - Exit code 1 if invalid (with detailed error + fix prompt)
4. Error message includes:
   - What's missing
   - How to fix
   - Prompt to run after fixing

**Test**: Script correctly identifies missing SUBPLANs, EXECUTION_TASKs, deliverables

### Phase 2: Execution Start Validator (1.5 hours)

**Goal**: Block starting EXECUTION_TASK if prerequisites missing

**Steps**:

1. Create validate_execution_start.py
2. Functions:
   - `check_subplan_exists(file_path)` → bool
   - `check_parent_plan_exists(file_path)` → bool
   - `check_archive_location_exists(plan_path)` → bool
   - `validate_execution_start(file_path)` → (bool, str)
3. CLI:
   - `python validate_execution_start.py @EXECUTION_TASK_FILE.md`
   - Exit code 0 if valid
   - Exit code 1 if invalid (with fix prompt)
4. Error message includes:
   - Missing prerequisites
   - How to create them
   - Prompt to run after fixing

**Test**: Script correctly identifies missing prerequisites

### Phase 3: Mid-Plan Validator (1.5 hours)

**Goal**: Auto-validate PLAN compliance at intervals

**Steps**:

1. Create validate_mid_plan.py
2. Functions:
   - `check_statistics_accuracy(plan_path)` → (bool, str)
   - `check_subplan_registration(plan_path)` → (bool, list) (missing registrations)
   - `check_archive_compliance(plan_path)` → (bool, str)
   - `validate_mid_plan(plan_path)` → (bool, str)
3. CLI:
   - `python validate_mid_plan.py @PLAN_FILE.md`
   - Exit code 0 if valid
   - Exit code 1 if invalid (with fix prompt)
4. Auto-trigger: Can be run manually or scheduled

**Test**: Script correctly identifies compliance issues

---

## ✅ Expected Results

### Functional Changes

1. **Achievement Completion Validator**: Blocks incomplete achievements
2. **Execution Start Validator**: Blocks starting without prerequisites
3. **Mid-Plan Validator**: Catches compliance issues early

### Observable Outcomes

1. **Methodology Enforcement**: Violations caught automatically
2. **Actionable Feedback**: Error messages include fix prompts
3. **Early Detection**: Mid-plan validator catches issues before completion

### Deliverables

- LLM/scripts/validate_achievement_completion.py
- LLM/scripts/validate_execution_start.py
- LLM/scripts/validate_mid_plan.py

---

## 🧪 Tests Required

### Test File

- Manual verification (run scripts, verify output)

### Test Cases to Cover

1. **Achievement Validator**:

   - Detects missing SUBPLAN
   - Detects missing EXECUTION_TASK
   - Detects missing deliverables
   - Provides actionable error message

2. **Execution Validator**:

   - Detects missing SUBPLAN
   - Detects missing parent PLAN
   - Detects missing archive location
   - Provides actionable error message

3. **Mid-Plan Validator**:
   - Detects inaccurate statistics
   - Detects unregistered SUBPLANs
   - Detects archive compliance issues
   - Provides actionable error message

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] validate_achievement_completion.py created and working
- [ ] validate_execution_start.py created and working
- [ ] validate_mid_plan.py created and working
- [ ] All scripts block on violations
- [ ] All scripts provide actionable feedback
- [ ] All tests pass
- [ ] EXECUTION_TASK complete with learnings
- [ ] Files archived immediately

---

## 📝 Notes

**Common Pitfalls**:

- Scripts not actually blocking (just warning)
- Error messages not actionable
- Missing edge cases in validation

**Resources**:

- Existing validation scripts (check_plan_size.py, check_execution_task_size.py)
- PLAN template for structure reference

---

**Ready to Execute**: Create EXECUTION_TASK and begin implementation  
**Reference**: 3-phase approach (Achievement, Execution, Mid-Plan)  
**Mother PLAN**: PLAN_METHODOLOGY-V2-ENHANCEMENTS.md
