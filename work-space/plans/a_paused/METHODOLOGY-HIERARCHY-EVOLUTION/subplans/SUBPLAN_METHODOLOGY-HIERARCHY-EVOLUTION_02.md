# SUBPLAN: GrammaPlan Enhancements Implementation

**Parent PLAN**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md  
**Achievement**: 0.2  
**Created**: 2025-11-08 09:00 UTC  
**Estimated Effort**: 3-4 hours  
**Status**: 🎯 Executing

---

## 🎯 Objective

Enhance GrammaPlan support with dedicated folder structure and realistic size limits (600-1,500 lines), updating guides, templates, and creating validation script.

**Context**: GrammaPlans currently have implicit 800-line limit and no dedicated folder. This achievement formalizes size limits (600-1,500 lines) and creates infrastructure for GrammaPlan organization.

**Why This Matters**: 
- GrammaPlans naturally grow to 800-1,000+ lines
- Need explicit size guidance (600-1,500 lines)
- Dedicated folder improves organization
- Validation script enforces limits

---

## 📦 Deliverables

### Primary Deliverables

1. **`work-space/grammaplans/` folder**
   - Physical folder for GrammaPlan documents
   - `README.md` explaining purpose

2. **Updated `LLM/guides/GRAMMAPLAN-GUIDE.md`**
   - Size limit: 600-1,500 lines (explicit)
   - Warning at 1,000 lines
   - Error at 1,500 lines
   - Updated criteria: >900 lines OR >40 hours OR 4+ domains
   - Document folder structure

3. **Updated `LLM/templates/GRAMMAPLAN-TEMPLATE.md`**
   - Add size guidance (600-1,500 lines)
   - Add folder location guidance
   - Warning/error thresholds

4. **`LLM/scripts/validation/check_grammaplan_size.py`**
   - Warning at 1,000 lines
   - Error at 1,500 lines
   - Exit code 1 if over limit
   - Clear error messages

---

## 🎨 Approach

### Phase 1: Folder Infrastructure (0.5h)

**Create `work-space/grammaplans/` folder**:
- Create directory
- Create README.md with:
  - Purpose of folder
  - Naming convention: `GRAMMAPLAN_<FEATURE>.md`
  - Size guidance: 600-1,500 lines
  - When documents belong here
  - Current GrammaPlans (if any)

**Implementation**:
- `mkdir -p work-space/grammaplans`
- Create comprehensive README

### Phase 2: Guide Update (1h)

**Update `LLM/guides/GRAMMAPLAN-GUIDE.md`**:

**Changes**:
1. **Size Limits Section**:
   - Update: "600-1,500 lines" (explicit, was implicit 800)
   - Add warning: "At 1,000 lines, consider splitting or simplifying"
   - Add error: "At 1,500 lines, must split into multiple GrammaPlans or convert to NORTH_STAR"
   - Rationale: GrammaPlans coordinate work, need space but not unlimited

2. **Criteria Section**:
   - Update: ">900 lines OR >40 hours OR 4+ domains" (was >600/32h/3+)
   - Rationale: With workflow separation, PLANs can be larger, so GrammaPlan threshold increases

3. **Folder Structure Section**:
   - Add: "GrammaPlans live in `work-space/grammaplans/`"
   - Document naming convention
   - Link to README

**Implementation**:
- Read current GRAMMAPLAN-GUIDE.md
- Update size limits section
- Update criteria section
- Add folder structure section
- Ensure consistency with NORTH_STAR guide

### Phase 3: Template Update (0.5h)

**Update `LLM/templates/GRAMMAPLAN-TEMPLATE.md`**:

**Changes**:
1. **Size Guidance Section**:
   - Add: "Size: 600-1,500 lines"
   - Add: "Warning at 1,000 lines: Consider splitting or simplifying"
   - Add: "Error at 1,500 lines: Must split or convert to NORTH_STAR"

2. **File Location Section**:
   - Add: "File Location: Save this file in `work-space/grammaplans/GRAMMAPLAN_[NAME].md`"
   - Document naming convention

3. **Size Management Section**:
   - Add guidance on when to split
   - Add guidance on when to convert to NORTH_STAR
   - Examples of appropriate sizes

**Implementation**:
- Read current GRAMMAPLAN-TEMPLATE.md
- Add size guidance section
- Add file location section
- Update header with size limits

### Phase 4: Validation Script (1h)

**Create `LLM/scripts/validation/check_grammaplan_size.py`**:

**Functionality**:
- Read GrammaPlan file
- Count lines
- Warning if 1,000-1,499 lines: Print warning message
- Error if >= 1,500 lines: Print error message, exit code 1
- Success if 600-999 lines: Print OK message
- Too small if <600 lines: Print note (might be PLAN instead)

**Features**:
- Command-line interface: `python check_grammaplan_size.py <file>`
- Clear error messages
- Exit codes: 0 (OK), 1 (error), 2 (warning)
- Help text

**Implementation**:
- Use existing `check_plan_size.py` as reference
- Adapt for GrammaPlan limits (600-1,500)
- Test with sample files
- Add to validation suite

---

## 🧪 Tests Required

### Validation Tests

**1. Folder Structure Test**:
- [ ] `work-space/grammaplans/` exists
- [ ] README.md exists and complete
- [ ] Naming convention documented

**2. Guide Completeness Test**:
- [ ] Size limits clearly stated (600-1,500 lines)
- [ ] Warning/error thresholds documented
- [ ] Criteria updated (>900 lines OR >40 hours OR 4+ domains)
- [ ] Folder structure documented

**3. Template Completeness Test**:
- [ ] Size guidance included
- [ ] File location guidance included
- [ ] Warning/error thresholds included

**4. Script Functionality Test**:
- [ ] Script runs without errors
- [ ] Warning at 1,000 lines
- [ ] Error at 1,500 lines
- [ ] Exit codes correct
- [ ] Help text clear

### Manual Validation

**Test Guide Updates**:
1. Read updated GRAMMAPLAN-GUIDE.md
2. Verify size limits clear
3. Verify criteria updated
4. Verify folder structure documented

**Test Template Updates**:
1. Use template to create test GrammaPlan
2. Verify size guidance helpful
3. Verify file location clear

**Test Validation Script**:
1. Run script on existing GrammaPlans
2. Verify warnings/errors appropriate
3. Verify exit codes correct

---

## 🎯 Expected Results

### Immediate Outcomes

**Folder Created**:
- `work-space/grammaplans/` exists
- README.md explains purpose
- Ready for GrammaPlan documents

**Guide Updated**:
- Size limits explicit (600-1,500 lines)
- Warning/error thresholds clear
- Criteria updated (>900/40h/4+ domains)
- Folder structure documented

**Template Updated**:
- Size guidance included
- File location guidance included
- Warning/error thresholds included

**Script Created**:
- `check_grammaplan_size.py` functional
- Validates size limits
- Clear error messages
- Proper exit codes

### Quality Metrics

**Guide Quality**:
- Clear size guidance
- Updated criteria
- Consistent with NORTH_STAR guide
- Helpful examples

**Template Quality**:
- Size guidance clear
- File location explicit
- Warning/error thresholds documented

**Script Quality**:
- Functional and tested
- Clear error messages
- Proper exit codes
- Integrates with validation suite

---

## 📋 Definition of Done

**All deliverables exist**:
- [ ] `work-space/grammaplans/` folder created
- [ ] `work-space/grammaplans/README.md` created
- [ ] `LLM/guides/GRAMMAPLAN-GUIDE.md` updated
- [ ] `LLM/templates/GRAMMAPLAN-TEMPLATE.md` updated
- [ ] `LLM/scripts/validation/check_grammaplan_size.py` created

**Quality standards met**:
- [ ] Size limits explicit (600-1,500 lines)
- [ ] Warning/error thresholds clear
- [ ] Criteria updated (>900/40h/4+ domains)
- [ ] Folder structure documented
- [ ] Script functional and tested

**Validation passed**:
- [ ] Manual test: Guide updates clear
- [ ] Manual test: Template updates helpful
- [ ] Manual test: Script validates correctly
- [ ] File checks: All files exist (`ls -1` each path)

**Documentation complete**:
- [ ] Size guidance consistent across all documents
- [ ] Folder structure clear
- [ ] Validation script documented

---

## 🎓 Success Criteria

**Functional Success**:
- GrammaPlans have dedicated folder
- Size limits explicit and enforced
- Criteria updated for new workflow
- Validation script operational

**Quality Success**:
- Guide comprehensive and clear
- Template helpful and complete
- Script reliable and tested
- Consistency across documents

**Adoption Success**:
- Future GrammaPlans use folder
- Size limits guide document creation
- Validation prevents oversized documents

---

## 📚 References

**Parent PLAN**: PLAN_METHODOLOGY-HIERARCHY-EVOLUTION.md (Achievement 0.2)

**Related Documents**:
- `LLM/guides/GRAMMAPLAN-GUIDE.md` (to update)
- `LLM/templates/GRAMMAPLAN-TEMPLATE.md` (to update)
- `LLM/scripts/validation/check_plan_size.py` (reference for script)
- `LLM/guides/NORTH-STAR-GUIDE.md` (for consistency)

**Existing GrammaPlans** (to reference):
- `work-space/plans/GRAMMAPLAN_GRAPHRAG-PIPELINE-EXCELLENCE.md`
- `work-space/plans/GRAMMAPLAN_YOUTUBE-RAG-SYSTEM-INTEGRATION.md`

---

## 🔄 Execution Plan

**Single EXECUTION_TASK** (recommended):
- All work is cohesive (enhancing GrammaPlan support)
- Sequential phases (folder → guide → template → script)
- Estimated 3-4 hours (fits in single execution)

**Recommended**: Single execution for cohesion

---

**Status**: Ready for execution  
**Next**: Create EXECUTION_TASK_METHODOLOGY-HIERARCHY-EVOLUTION_02_01.md and execute

