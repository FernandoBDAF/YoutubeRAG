# SUBPLAN: PLAN Size and Criteria Enhancements

**Parent PLAN**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md  
**Achievement**: 0.3  
**Created**: 2025-11-08 11:00 UTC  
**Estimated Effort**: 2-3 hours  
**Status**: 🎯 Executing

---

## 🎯 Objective

Increase PLAN size limit from 600 to 900 lines and adjust GrammaPlan criteria, based on workflow separation insight that PLANs now provide context for SUBPLAN creation only (not execution).

**Context**: With workflow separation, PLANs are only read by Planner agent when creating SUBPLANs, not by Executor agents. This means larger PLANs don't bloat execution context, allowing realistic size limits.

**Why This Matters**: 
- Many PLANs naturally grow to 700-900 lines
- Current 600-line limit forces premature GrammaPlan conversion
- Workflow separation enables larger PLANs without context bloat
- GrammaPlan criteria should reflect PLAN size increase

---

## 📦 Deliverables

### Primary Deliverables

1. **Updated `LLM/templates/PLAN-TEMPLATE.md`**
   - Size limit: 300-900 lines (was 300-600)
   - Document: "PLANs now provide context for SUBPLAN creation only, not execution"
   - Document: "With workflow separation, larger PLANs don't bloat execution context"
   - Warning at 700 lines: "Approaching limit, ensure focus maintained"
   - Error at 900 lines: "Must convert to GrammaPlan or split"

2. **Updated `LLM/guides/GRAMMAPLAN-GUIDE.md`**
   - GrammaPlan criteria: >900 lines OR >40 hours OR 4+ domains (verify already updated in 0.2)
   - Rationale: PLANs can be larger since they don't bloat execution context
   - Ensure consistency with new PLAN limits

3. **Updated `LLM/scripts/validation/check_plan_size.py`**
   - Warning at 700 lines (was 400)
   - Error at 900 lines (was 600)
   - Update messaging to reflect new limits
   - Update help text and examples

---

## 🎨 Approach

### Phase 1: Template Update (0.5h)

**Update `LLM/templates/PLAN-TEMPLATE.md`**:

**Changes**:
1. **Size Limit Section**:
   - Update: "Size: 300-900 lines" (was 300-600)
   - Add: "Warning at 700 lines: Approaching limit, ensure focus maintained"
   - Add: "Error at 900 lines: Must convert to GrammaPlan or split"

2. **Workflow Context Section** (new or update):
   - Add: "PLANs now provide context for SUBPLAN creation only, not execution"
   - Add: "With workflow separation, larger PLANs don't bloat execution context"
   - Explain: Executor reads SUBPLAN, not PLAN
   - Explain: Planner reads PLAN achievement (100 lines), not full PLAN

3. **Size Management Section**:
   - Update guidance for 700-900 line range
   - Document when to split vs. continue
   - Reference GrammaPlan criteria (>900 lines)

**Implementation**:
- Read current PLAN-TEMPLATE.md
- Update size limits section
- Add workflow context explanation
- Update size management guidance

### Phase 2: Guide Verification (0.5h)

**Verify `LLM/guides/GRAMMAPLAN-GUIDE.md`**:

**Check**:
- Criteria already updated in Achievement 0.2: >900 lines OR >40 hours OR 4+ domains
- Rationale mentions workflow separation
- Consistency with new PLAN limits

**If Needed**:
- Add rationale about workflow separation
- Ensure criteria clearly state >900 (not >=900)
- Verify messaging consistent

**Implementation**:
- Read current GRAMMAPLAN-GUIDE.md
- Verify criteria section
- Add rationale if missing
- Ensure consistency

### Phase 3: Validation Script Update (1h)

**Update `LLM/scripts/validation/check_plan_size.py`**:

**Changes**:
1. **Line Count Checks**:
   - Warning at 700 lines (was 400): "Consider GrammaPlan"
   - Error at 900 lines (was 600): "MUST convert to GrammaPlan"
   - Update success message: "Lines: {count} / 900 ✅"

2. **Effort Checks** (if applicable):
   - Warning at 30 hours (was 24): "Consider GrammaPlan"
   - Error at 40 hours (was 32): "MUST convert to GrammaPlan"
   - Update success message: "Estimated: {hours}h / 40h ✅"

3. **Messaging Updates**:
   - Update all error/warning messages
   - Update help text: "Limits: 900 lines / 40 hours"
   - Update examples in help text
   - Add rationale: "With workflow separation, PLANs can be larger"

**Implementation**:
- Read current check_plan_size.py
- Update line count thresholds (700/900)
- Update effort thresholds (30/40 if applicable)
- Update all messaging
- Update help text
- Test with sample files

---

## 🧪 Tests Required

### Validation Tests

**1. Template Completeness Test**:
- [ ] Size limit clearly stated (300-900 lines)
- [ ] Warning/error thresholds documented (700/900)
- [ ] Workflow context explained
- [ ] Size management guidance updated

**2. Guide Consistency Test**:
- [ ] GrammaPlan criteria updated (>900/40h/4+)
- [ ] Rationale mentions workflow separation
- [ ] Consistent with PLAN limits

**3. Script Functionality Test**:
- [ ] Warning at 700 lines
- [ ] Error at 900 lines
- [ ] Exit codes correct
- [ ] Messaging clear and helpful
- [ ] Help text updated

### Manual Validation

**Test Template Updates**:
1. Use template to create test PLAN
2. Verify size guidance helpful
3. Verify workflow context clear
4. Verify warning/error thresholds appropriate

**Test Script Updates**:
1. Run script on existing PLANs
2. Verify warnings/errors appropriate
3. Verify exit codes correct
4. Verify messaging helpful

---

## 🎯 Expected Results

### Immediate Outcomes

**Template Updated**:
- Size limits explicit (300-900 lines)
- Warning/error thresholds clear (700/900)
- Workflow context explained
- Size management guidance helpful

**Guide Verified**:
- Criteria consistent (>900/40h/4+)
- Rationale complete
- Messaging consistent

**Script Updated**:
- Thresholds updated (700/900)
- Messaging clear
- Help text accurate
- Functional and tested

### Quality Metrics

**Template Quality**:
- Clear size guidance
- Workflow context explained
- Warning/error thresholds helpful
- Size management guidance actionable

**Guide Quality**:
- Criteria consistent
- Rationale complete
- Messaging aligned

**Script Quality**:
- Functional and tested
- Clear error messages
- Proper exit codes
- Helpful guidance

---

## 📋 Definition of Done

**All deliverables exist**:
- [ ] `LLM/templates/PLAN-TEMPLATE.md` updated
- [ ] `LLM/guides/GRAMMAPLAN-GUIDE.md` verified/updated
- [ ] `LLM/scripts/validation/check_plan_size.py` updated

**Quality standards met**:
- [ ] Size limits explicit (300-900 lines)
- [ ] Warning/error thresholds clear (700/900)
- [ ] Workflow context explained
- [ ] Criteria consistent (>900/40h/4+)
- [ ] Script functional and tested

**Validation passed**:
- [ ] Manual test: Template updates clear
- [ ] Manual test: Guide consistency verified
- [ ] Manual test: Script validates correctly
- [ ] File checks: All files exist (`ls -1` each path)

**Documentation complete**:
- [ ] Workflow separation rationale documented
- [ ] Size limits consistent across documents
- [ ] Messaging aligned

---

## 🎓 Success Criteria

**Functional Success**:
- PLANs can be 900 lines
- GrammaPlan criteria adjusted (>900/40h/4+)
- Validation script enforces new limits
- Workflow separation rationale clear

**Quality Success**:
- Template comprehensive and clear
- Guide consistent
- Script reliable and tested
- Messaging helpful

**Adoption Success**:
- Future PLANs use new limits
- Validation prevents oversized PLANs
- Workflow separation understood

---

## 📚 References

**Parent PLAN**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md (Achievement 0.3)

**Related Documents**:
- `LLM/templates/PLAN-TEMPLATE.md` (to update)
- `LLM/guides/GRAMMAPLAN-GUIDE.md` (to verify/update)
- `LLM/scripts/validation/check_plan_size.py` (to update)
- `LLM/scripts/validation/check_grammaplan_size.py` (reference for consistency)

**Workflow Context**:
- SUBPLAN workflow separation (PLAN → SUBPLAN → EXECUTION)
- Context budgets: Planner reads PLAN achievement, Executor reads SUBPLAN objective
- Rationale: Larger PLANs don't bloat execution context

---

## 🔄 Execution Plan

**Single EXECUTION_TASK** (recommended):
- All work is cohesive (updating PLAN size limits)
- Sequential phases (template → guide → script)
- Estimated 2-3 hours (fits in single execution)

**Recommended**: Single execution for cohesion

---

**Status**: Ready for execution  
**Next**: Create EXECUTION_TASK_METHODOLOGY-HIERARCHY-EVOLUTION_03_01.md and execute

