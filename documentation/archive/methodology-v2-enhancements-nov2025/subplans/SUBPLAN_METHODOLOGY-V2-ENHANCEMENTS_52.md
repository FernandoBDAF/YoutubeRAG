# SUBPLAN: Script Organization by Domain

**Mother Plan**: PLAN_METHODOLOGY-V2-ENHANCEMENTS.md  
**Achievement Addressed**: Achievement 5.2 (Script Organization by Domain)  
**Status**: In Progress  
**Created**: 2025-11-07  
**Estimated Effort**: 1-2 hours

---

## 🎯 Objective

Organize LLM methodology scripts into domain-based subdirectories within LLM/scripts/ to improve discoverability and maintainability. Scripts should live in the folder they belong to instead of having an exclusive folder.

---

## 📋 What Needs to Be Created

### Files to Move

1. **Validation Scripts** → `LLM/scripts/validation/`:
   - validate_achievement_completion.py
   - validate_execution_start.py
   - validate_mid_plan.py
   - validate_registration.py
   - check_plan_size.py
   - check_execution_task_size.py

2. **Generation Scripts** → `LLM/scripts/generation/`:
   - generate_prompt.py

3. **Archiving Scripts** → `LLM/scripts/archiving/`:
   - archive_completed.py

### Files to Create

1. **LLM/scripts/README.md**:
   - Overview of script organization
   - Directory structure
   - Usage examples for each domain

---

## 📝 Approach

**Strategy**: Organize by domain, create README, update references

**Method**:

### Phase 1: Create Domain Directories (15 min)

**Goal**: Create subdirectories for each script domain

**Steps**:
1. Create LLM/scripts/validation/ directory
2. Create LLM/scripts/generation/ directory
3. Create LLM/scripts/archiving/ directory

**Test**: Directories exist

### Phase 2: Move Scripts (30 min)

**Goal**: Move scripts to appropriate domain directories

**Steps**:
1. Move validation scripts to validation/
2. Move generation scripts to generation/
3. Move archiving scripts to archiving/
4. Verify all scripts still work after move

**Test**: Scripts run from new locations

### Phase 3: Create README (30 min)

**Goal**: Document script organization

**Steps**:
1. Create LLM/scripts/README.md
2. Document directory structure
3. List scripts per domain
4. Provide usage examples
5. Document how to add new scripts

**Test**: README is comprehensive

### Phase 4: Update References (15 min)

**Goal**: Update any hardcoded script paths in documentation

**Steps**:
1. Search for references to old script paths
2. Update to new paths
3. Verify all references updated

**Test**: No broken references

---

## ✅ Expected Results

### Functional Changes

1. **Organized Structure**: Scripts organized by domain
2. **README Documentation**: Clear organization documented
3. **Updated References**: All paths updated

### Observable Outcomes

1. **Better Discoverability**: Scripts easier to find by domain
2. **Clear Organization**: Domain-based structure is intuitive
3. **Maintainability**: Easier to add new scripts

### Deliverables

- LLM/scripts/validation/ directory with validation scripts
- LLM/scripts/generation/ directory with generation scripts
- LLM/scripts/archiving/ directory with archiving scripts
- LLM/scripts/README.md (documentation)

---

## 🧪 Tests Required

### Test File
- Manual verification (check directories, run scripts, verify README)

### Test Cases to Cover

1. **Directory Structure**:
   - All domain directories exist
   - Scripts in correct directories

2. **Script Functionality**:
   - All scripts run from new locations
   - No broken imports

3. **Documentation**:
   - README is comprehensive
   - Usage examples work

4. **References**:
   - All documentation references updated

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] Domain directories created
- [ ] Scripts moved to correct directories
- [ ] README created and comprehensive
- [ ] All references updated
- [ ] All scripts still work
- [ ] All tests pass
- [ ] EXECUTION_TASK complete with learnings
- [ ] Files archived immediately

---

## 📝 Notes

**Common Pitfalls**:
- Forgetting to update references
- Breaking script imports
- Missing scripts in move

**Resources**:
- Current LLM/scripts/ directory
- Documentation files that reference scripts

---

**Ready to Execute**: Create EXECUTION_TASK and begin implementation  
**Reference**: 4-phase approach (Directories, Move, README, References)  
**Mother PLAN**: PLAN_METHODOLOGY-V2-ENHANCEMENTS.md

