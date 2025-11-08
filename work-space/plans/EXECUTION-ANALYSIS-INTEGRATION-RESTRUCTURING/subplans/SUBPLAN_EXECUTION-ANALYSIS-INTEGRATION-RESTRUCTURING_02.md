# SUBPLAN: Resolve Duplicate Files

**Achievement**: 0.2 of PLAN_EXECUTION-ANALYSIS-INTEGRATION-RESTRUCTURING  
**Status**: 📋 Design Phase Complete  
**Created**: 2025-11-09 04:30 UTC  
**Purpose**: Remove files that exist in both workspace and archive locations to establish clear single source of truth

---

## 🎯 Objective

Identify and resolve all duplicate files from EXECUTION-ANALYSIS-INTEGRATION that exist in both workspace and archive locations, establishing a single authoritative location for each file and eliminating confusion.

---

## 📦 Deliverables

1. **Duplicate Analysis Document**
   - List all duplicate files (count: 4 confirmed)
   - Show both locations for each file
   - Document file sizes and modification dates
   - Identify which are "active" (in progress) vs "completed"

2. **Authoritative Location Decision**
   - Decide for each file: keep in workspace or archive
   - Rationale: Based on completion status
   - Decision matrix documenting each choice
   - Clear policy for future duplicate prevention

3. **Duplicates Removed**
   - Remove all 4 duplicate files (keeping authoritative copy)
   - Verify removal in secondary location
   - Update git tracking if needed

4. **Git Cleanup** (if needed)
   - Remove duplicate files from git history if tracked
   - Document any cleanup performed
   - Verify clean repository state

---

## 🔍 Approach

**Phase 1: Duplicate Inventory & Analysis**
- Use `find` to locate all duplicates
- For each duplicate, determine:
  - File size in both locations
  - Last modification date in both locations
  - Status markers in file content (Complete, In Progress, etc.)
  - Archive location structure (organized by date/feature?)
- Create detailed inventory matrix

**Phase 2: Decision Criteria & Policy**
- **For "Completed" files**: Archive location is authoritative
  - Reasoning: Work is done, archive is permanent storage
  - Keep in: `documentation/archive/`
  - Remove from: `work-space/`
  
- **For "In Progress" files**: Workspace location is authoritative
  - Reasoning: Active work should be in workspace
  - Keep in: `work-space/`
  - Remove from: `documentation/archive/`
  
- **Decision Matrix**: Document each file's choice with rationale

**Phase 3: Removal & Verification**
- For each file to remove:
  - Verify content matches keeping location (checksum/spot-check)
  - Remove from secondary location
  - Verify removal with `ls` (should fail)
- Count total files removed
- Verify no remaining duplicates

**Phase 4: Git Cleanup (if applicable)**
- Check if duplicate files are tracked in git
- If yes: Document the files tracked
- Evaluate cleanup need (small files = low priority)
- Document any cleanup performed

---

## ⚙️ Execution Strategy

**Single Sequential EXECUTION**: One EXECUTION_TASK covering all duplicate resolution

**Why Sequential**:
- Removals are interdependent (must maintain logical consistency)
- Each removal can be verified before next
- Decision process informs removal order
- 2-3 hour effort fits single execution

**Workflow**:
1. EXECUTION_TASK_02_01: Analyze duplicates → Decide authoritative locations → Remove all → Verify

**Files Involved**:
- SUBPLAN_EXECUTION-ANALYSIS-INTEGRATION_11.md
- SUBPLAN_EXECUTION-ANALYSIS-INTEGRATION_12.md
- EXECUTION_TASK_EXECUTION-ANALYSIS-INTEGRATION_11_01.md
- EXECUTION_TASK_EXECUTION-ANALYSIS-INTEGRATION_12_01.md

---

## 🧪 Tests

**Test 1: Duplicate Identification**
```bash
# Count duplicates before removal (should be 4)
find work-space -name "SUBPLAN_EXECUTION-ANALYSIS-INTEGRATION_11.md" -o \
  -name "SUBPLAN_EXECUTION-ANALYSIS-INTEGRATION_12.md" -o \
  -name "EXECUTION_TASK_EXECUTION-ANALYSIS-INTEGRATION_11_01.md" -o \
  -name "EXECUTION_TASK_EXECUTION-ANALYSIS-INTEGRATION_12_01.md" | wc -l
find documentation/archive -name "SUBPLAN_EXECUTION-ANALYSIS-INTEGRATION_11.md" -o \
  -name "SUBPLAN_EXECUTION-ANALYSIS-INTEGRATION_12.md" -o \
  -name "EXECUTION_TASK_EXECUTION-ANALYSIS-INTEGRATION_11_01.md" -o \
  -name "EXECUTION_TASK_EXECUTION-ANALYSIS-INTEGRATION_12_01.md" | wc -l
# Expected: 4 in workspace, 4 in archive
```

**Test 2: Content Verification (Before Removal)**
```bash
# Verify workspace and archive versions match (spot-check hashes)
md5 work-space/subplans/SUBPLAN_EXECUTION-ANALYSIS-INTEGRATION_11.md
md5 documentation/archive/.../SUBPLAN_EXECUTION-ANALYSIS-INTEGRATION_11.md
# Expected: Hashes should match (identical files)
```

**Test 3: Post-Removal State**
```bash
# Verify only one copy remains for each file
ls -1 work-space/subplans/SUBPLAN_EXECUTION-ANALYSIS-INTEGRATION_11.md
# Should succeed (only in workspace OR only in archive, depending on decision)

ls -1 documentation/archive/.../SUBPLAN_EXECUTION-ANALYSIS-INTEGRATION_11.md
# Should fail (file removed from archive)
```

**Test 4: No Remaining Duplicates**
```bash
# Verify no files in both locations
for file in SUBPLAN_11 SUBPLAN_12 EXECUTION_TASK_11_01 EXECUTION_TASK_12_01; do
  ws_count=$(find work-space -name "*$file*" | wc -l)
  arch_count=$(find documentation/archive -name "*$file*" | wc -l)
  if [ $ws_count -gt 0 ] && [ $arch_count -gt 0 ]; then
    echo "DUPLICATE STILL EXISTS: $file"
  fi
done
# Expected: No output (no duplicates)
```

---

## 📋 Expected Results

**Success Criteria**:
- ✅ All 4 duplicate files identified with locations documented
- ✅ Authoritative location decision made for each file (with rationale)
- ✅ 4 duplicate files removed from secondary locations
- ✅ Post-removal verification: only one copy of each file remains
- ✅ No files in both workspace AND archive simultaneously
- ✅ Content integrity verified (copies matched before removal)
- ✅ Git state clean (no untracked duplicates)

**Effort**: 2-3 hours (mostly analysis and decision-making)

**Next Achievement**: 1.1 (Correct EXECUTION_TASK Status Fields)

---

## 📚 References

- **Methodology**: LLM-METHODOLOGY.md (file organization)
- **Prior Audit**: EXECUTION_ANALYSIS_PLAN-EXECUTION-ANALYSIS-INTEGRATION-AUDIT.md (Issue #2)
- **Archive Structure**: Check existing archive patterns in `documentation/archive/`
- **PLAN**: work-space/plans/PLAN_EXECUTION-ANALYSIS-INTEGRATION-RESTRUCTURING.md

---

**Status**: ✅ Complete  
**Execution**: EXECUTION_TASK_EXECUTION-ANALYSIS-INTEGRATION-RESTRUCTURING_02_01.md (Complete)  
**Result**: All 4 duplicate files removed from archive, workspace copies kept as authoritative

