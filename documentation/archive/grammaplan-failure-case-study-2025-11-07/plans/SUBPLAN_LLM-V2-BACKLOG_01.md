# SUBPLAN: Meta-PLAN Reference Verification

**Mother Plan**: PLAN_LLM-V2-BACKLOG.md  
**Parent GrammaPlan**: GRAMMAPLAN_LLM-METHODOLOGY-V2.md  
**Achievement Addressed**: Achievement 0.1 (Meta-PLAN Reference Verification)  
**Backlog Item**: IMPL-METHOD-004  
**Status**: Ready  
**Created**: 2025-11-07  
**Estimated Effort**: 3-4 hours

---

## 🎯 Objective

Audit all documentation referencing PLAN_STRUCTURED-LLM-DEVELOPMENT.md (the meta-PLAN) to find and fix broken, outdated, or missing references. Create an automated verification script to prevent future reference issues. This ensures the methodology is discoverable and all cross-references work correctly after recent methodology changes (GrammaPlan, Mid-Plan Review, Pre-Completion Review, etc.).

---

## 📋 What Needs to Be Created

### Files to Create

1. **scripts/validate_references.py**: Automated reference verification script

   - Scan all markdown files for references to methodology docs
   - Check if referenced files exist
   - Check if referenced sections exist
   - Report broken/outdated references
   - Exit with error code if issues found (for CI/CD integration)

2. **EXECUTION_ANALYSIS_REFERENCE-AUDIT.md**: Findings document
   - List all files referencing meta-PLAN
   - Categorize issues (broken links, outdated sections, missing refs)
   - Document fixes applied
   - Statistics (total refs, broken refs, fixed refs)

### Files to Modify

Based on audit findings - TBD (will discover during execution):

- Any files with broken references to PLAN_STRUCTURED-LLM-DEVELOPMENT.md
- Any files with outdated section references (e.g., old achievement numbers)
- Any files that should reference new features (GrammaPlan, Mid-Plan Review) but don't

### Functions/Classes to Add

**scripts/validate_references.py**:

- `find_markdown_files(root_dir)`: Recursively find all .md files
- `extract_references(file_path)`: Extract all markdown link references
- `validate_file_reference(ref_path)`: Check if file exists
- `validate_section_reference(file_path, section)`: Check if section exists
- `scan_for_patterns(content, patterns)`: Find methodology-related patterns
- `generate_report(findings)`: Create formatted report
- `main()`: Orchestrate the validation

### Tests Required

- Test with known broken reference (should detect)
- Test with valid reference (should pass)
- Test with missing section (should detect)
- Test with non-existent file (should detect)
- Test report generation (should format correctly)

---

## 📝 Approach

**Strategy**: Systematic audit → Fix issues → Create automation

**Method**:

### Phase 1: Manual Audit (1-1.5h)

1. **Identify Scope**:

   - Find all files that reference PLAN_STRUCTURED-LLM-DEVELOPMENT.md
   - Use grep to search: `grep -r "PLAN_STRUCTURED-LLM-DEVELOPMENT" --include="*.md"`
   - Document all findings in EXECUTION_ANALYSIS

2. **Categorize References**:

   - **Direct links**: `[text](PLAN_STRUCTURED-LLM-DEVELOPMENT.md)`
   - **Section links**: `[text](PLAN_STRUCTURED-LLM-DEVELOPMENT.md#section)`
   - **Inline mentions**: References without links
   - **Related docs**: IMPLEMENTATION\_\*, MULTIPLE-PLANS-PROTOCOL, etc.

3. **Check for Issues**:
   - Broken links (file doesn't exist - unlikely for meta-PLAN)
   - Outdated section references (sections renamed/removed)
   - Missing references (new features not mentioned where relevant)
   - Inconsistent naming (different ways to reference same doc)

### Phase 2: Fix Issues (0.5-1h)

1. **Fix Broken Links**:

   - Update paths if files moved
   - Fix typos in filenames
   - Update section anchors if changed

2. **Add Missing References**:

   - Add GrammaPlan references where relevant
   - Add Mid-Plan Review references where relevant
   - Add Pre-Completion Review references where relevant

3. **Standardize Naming**:
   - Consistent capitalization
   - Consistent link format
   - Consistent section references

### Phase 3: Create Automation (1-1.5h)

1. **Script Design**:

   ```python
   # Pseudocode
   for markdown_file in find_all_markdown():
       references = extract_references(markdown_file)
       for ref in references:
           if is_file_reference(ref):
               if not file_exists(ref):
                   report_broken_link(ref)
           if is_section_reference(ref):
               if not section_exists(ref):
                   report_broken_section(ref)
   generate_report(all_issues)
   ```

2. **Features**:

   - Configurable ignore patterns (e.g., external URLs, archive/)
   - Exit code 0 if all valid, 1 if issues found
   - Colorized output for terminal
   - JSON output option for CI/CD
   - Verbose mode for debugging

3. **Testing**:
   - Create test fixtures (valid/broken references)
   - Run script on fixtures
   - Verify detection accuracy
   - Test in dry-run mode

### Phase 4: Documentation & Integration (0.5h)

1. **Usage Documentation**:

   - Add to README or create scripts/README.md
   - Examples of running the script
   - Integration with CI/CD (future)

2. **Integration Points**:
   - Mention in IMPLEMENTATION_MID_PLAN_REVIEW.md (compliance check)
   - Add to backlog: CI/CD integration (IMPL-TOOLING-004 or similar)

**Key Considerations**:

- **Backward Compatibility**: Don't break existing valid references
- **Archive Handling**: Archived docs may reference old versions (acceptable)
- **External Links**: Don't validate external URLs (out of scope)
- **Performance**: Script should run in <10 seconds for entire project

---

## 🧪 Tests Required

### Test File

`scripts/test_validate_references.py` (if time permits, otherwise manual testing)

### Test Cases to Cover

1. **Valid Reference Detection**:

   - Valid file reference → PASS
   - Valid section reference → PASS
   - Multiple valid refs in one file → PASS

2. **Broken Reference Detection**:

   - Non-existent file → FAIL (detected)
   - Non-existent section → FAIL (detected)
   - Malformed reference → FAIL (detected)

3. **Edge Cases**:

   - Archived files (should ignore or warn)
   - Case sensitivity in file paths
   - Spaces in section anchors
   - Special characters in URLs

4. **Report Generation**:
   - Formats correctly
   - Includes all required information
   - Exit codes correct

### Test-First Requirement

- [ ] Tests written before implementation (if scripting, may be manual testing)
- [ ] Initial test run shows expected behavior
- [ ] Tests define success criteria

**For this SUBPLAN**: Manual testing is acceptable given the 3-4h timeline and documentation focus. Automated tests are "nice to have."

---

## ✅ Expected Results

### Functional Changes

1. **All References Fixed**: No broken links to PLAN_STRUCTURED-LLM-DEVELOPMENT.md
2. **Automation Created**: `scripts/validate_references.py` works and catches issues
3. **Documentation Complete**: EXECUTION_ANALYSIS documents findings and fixes

### Observable Outcomes

1. **Audit Complete**: Know exactly which files reference meta-PLAN
2. **Issues Resolved**: All broken/outdated references fixed
3. **Prevention**: Script prevents future broken references
4. **Faster Discovery**: Developers can find methodology docs easier

### Deliverables

- `scripts/validate_references.py` (100-200 lines)
- `EXECUTION_ANALYSIS_REFERENCE-AUDIT.md` (findings and statistics)
- Fixed references across all affected files
- Updated PLAN_LLM-V2-BACKLOG.md (achievement complete, statistics updated)

---

## 🔍 Conflict Analysis with Other Subplans

**Review Existing Subplans**:

This is the first SUBPLAN for PLAN_LLM-V2-BACKLOG.md.

**Check for**:

- **Overlap**: None (first achievement)
- **Conflicts**: None (reference verification doesn't conflict with future work)
- **Dependencies**: None (this is P0, foundation for everything)
- **Integration**: Output (audit script) used by future compliance work

**Analysis**: No conflicts detected. Safe to proceed.

---

## 🔗 Dependencies

### Other Subplans

None (this is the first)

### External Dependencies

- Python 3.8+ (for script)
- Access to all project markdown files
- Git repository (to find all files)

### Prerequisite Knowledge

- Markdown link syntax
- File path resolution
- Regular expressions (for pattern matching)
- Python scripting

---

## 🔄 Execution Task Reference

**Execution Tasks** (created during execution):

- **EXECUTION_TASK_LLM-V2-BACKLOG_01_01**: First execution attempt - Status: [Pending]

---

## 📊 Success Criteria

**This Subplan is Complete When**:

- [ ] Audit complete (all files referencing meta-PLAN identified)
- [ ] All broken references fixed
- [ ] All outdated section references updated
- [ ] Missing references added (GrammaPlan, Mid-Plan Review where relevant)
- [ ] `scripts/validate_references.py` created and tested
- [ ] `EXECUTION_ANALYSIS_REFERENCE-AUDIT.md` created with findings
- [ ] Script runs successfully on entire project (exit code 0)
- [ ] All expected results achieved
- [ ] EXECUTION_TASK complete
- [ ] PLAN updated (achievement 0.1 marked complete, statistics updated)
- [ ] Ready for next achievement

---

## 📝 Notes

**Common Pitfalls**:

- Don't break archived documentation (old references are okay in archives)
- Don't over-engineer the script (simple is better for 3-4h timeline)
- Focus on methodology docs, not code documentation

**Resources**:

- `grep -r` for finding references
- Python `pathlib` for file operations
- Python `re` for regex pattern matching
- Markdown parsers (optional, regex may suffice)

**Time Management**:

- Phase 1 (Audit): 1-1.5h → Don't spend more than 1.5h
- Phase 2 (Fixes): 0.5-1h → Batch fixes, don't perfect
- Phase 3 (Script): 1-1.5h → Simple script, not production-grade yet
- Phase 4 (Docs): 0.5h → Brief documentation

**If Running Over Time**:

- Prioritize: Manual audit + fixes > Script creation
- Script can be basic (just file existence check)
- Defer advanced features (section validation) to future
- Document what's left for backlog

---

**Ready to Execute**: Create EXECUTION_TASK and begin work  
**Reference**: IMPLEMENTATION_START_POINT.md for workflows  
**Mother PLAN**: PLAN_LLM-V2-BACKLOG.md (update after completion)  
**Parent GrammaPlan**: GRAMMAPLAN_LLM-METHODOLOGY-V2.md (update after all achievements)
