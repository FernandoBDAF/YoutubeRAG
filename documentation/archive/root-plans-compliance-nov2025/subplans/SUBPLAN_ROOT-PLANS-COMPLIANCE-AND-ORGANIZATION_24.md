# SUBPLAN: Move Archive Folders to Documentation Archive

**Type**: SUBPLAN  
**Mother Plan**: PLAN_ROOT-PLANS-COMPLIANCE-AND-ORGANIZATION.md  
**Plan**: ROOT-PLANS-COMPLIANCE-AND-ORGANIZATION  
**Achievement Addressed**: Achievement 2.4 (Move Archive Folders to Documentation Archive)  
**Achievement**: 2.4  
**Status**: In Progress  
**Created**: 2025-11-08  
**Estimated Effort**: 1-2 hours

**Metadata Tags**: See `LLM/guides/METADATA-TAGS.md` for virtual organization system

**File Location**: `work-space/subplans/SUBPLAN_ROOT-PLANS-COMPLIANCE-AND-ORGANIZATION_24.md`

---

## 🎯 Objective

Move all incorrectly placed archive folders from root directory to `documentation/archive/` according to LLM-METHODOLOGY.md folder rules. Identify all archive folders, determine correct archive locations, move folders, verify structure, check for duplicates, and update any references.

---

## 📋 What Needs to Be Created

### Archive Folders to Move

**4 archive folders in root directory**:

1. `api-review-and-testing-archive/`
   - Target: `documentation/archive/api-review-and-testing-nov2025/` (or appropriate date)
   - Contains: subplans/, execution/ subdirectories

2. `methodology-v2-enhancements-archive/`
   - Target: `documentation/archive/methodology-v2-enhancements-nov2025/` (or appropriate date)
   - Contains: subplans/, execution/, analysis/ subdirectories

3. `methodology-validation-archive/`
   - Target: `documentation/archive/methodology-validation-nov2025/` (or appropriate date)
   - Contains: subplans/, execution/ subdirectories

4. `prompt-generator-fix-and-testing-archive/`
   - Target: `documentation/archive/prompt-generator-fix-and-testing-nov2025/` (or appropriate date)
   - Contains: subplans/, execution/ subdirectories

### Files to Create

- Migration report: `EXECUTION_ANALYSIS_ARCHIVE-FOLDERS-MIGRATION.md`

---

## 📝 Approach

**Strategy**: Systematic folder migration with duplicate checking and structure verification

**Method**:

1. **Identify Archive Folders**:
   - List all folders in root ending with `-archive`
   - Verify they are archive folders (contain subplans/, execution/, etc.)
   - Document folder structure for each

2. **Determine Target Locations**:
   - Extract feature name from folder name (remove `-archive` suffix)
   - Determine date from folder contents or use default (nov2025)
   - Format: `documentation/archive/<feature-name>-<date>/`
   - Check if target location already exists (duplicate check)

3. **Check for Duplicates**:
   - Search `documentation/archive/` for existing folders with same feature name
   - If duplicate found, merge strategy or rename
   - Document any duplicates found

4. **Verify Folder Structure**:
   - Check each folder contains expected subdirectories (subplans/, execution/, etc.)
   - Document structure for each folder
   - Note any anomalies

5. **Move Folders**:
   - Use Python `shutil.move()` to preserve permissions/timestamps
   - Move each folder to target location
   - Verify move was successful

6. **Update References**:
   - Search for references to old folder paths
   - Update any documentation or scripts that reference these folders
   - Verify all references updated

7. **Create Migration Report**:
   - Document all folders moved
   - List source and target paths
   - Note any duplicates or special handling
   - Verify root directory clean

**Key Considerations**:

- Some folders may already exist in documentation/archive/ (duplicates)
- Folder structure may vary (some have analysis/ subdirectory)
- Date determination from folder contents or default to nov2025
- Preserve all folder contents (no modifications, just moves)
- Update references if any exist

---

## 🧪 Tests Required

**Note**: File organization work, no code tests required.

**Verification**:
- Verify all 4 folders moved successfully
- Verify folder structure preserved
- Verify no duplicates in documentation/archive/
- Verify root directory has 0 archive folders remaining
- Verify references updated (if any)

---

## 📊 Expected Results

**Functional Changes**:
- All 4 archive folders moved to documentation/archive/
- Folder structure preserved
- Root directory clean of archive folders

**Observable Outcomes**:
- Root directory: 0 archive folders
- documentation/archive/: 4 folders added (or merged if duplicates)
- Folder structure matches expected format
- References updated (if any existed)

**Organization Compliance**:
- 100% of archive folders organized
- All folders in correct archive locations
- Archive structure matches LLM-METHODOLOGY.md requirements
- Root directory clean

---

## 🔗 Dependencies

**Prerequisites**:
- Achievement 2.3 complete (EXECUTION_ANALYSIS files organized)

**Related Work**:
- Part of Priority 2 (Organization and Migration)
- Follows archive structure from LLM-METHODOLOGY.md

---

## 📝 Execution Task Reference

- `EXECUTION_TASK_ROOT-PLANS-COMPLIANCE-AND-ORGANIZATION_24_01.md` - First execution

---

**Status**: In Progress  
**Next**: Execute folder migration systematically

