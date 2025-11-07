# SUBPLAN: Stage Dependency Validation (Achievement 0.3)

**Parent PLAN**: PLAN_GRAPHRAG-PIPELINE-VISUALIZATION.md  
**Achievement**: 0.3 - Stage Dependency Validation Implemented  
**Status**: ✅ Complete  
**Created**: 2025-11-06 23:56 UTC  
**Completed**: 2025-11-06 23:58 UTC

---

## 🎯 Objective

Enhance existing dependency validation to add warnings for out-of-order stage selection and ensure comprehensive validation coverage.

**Note**: Core dependency validation is already implemented in Achievement 0.1. This achievement adds:

- Warnings when stages are selected out of order
- Enhanced logging for dependency resolution
- Additional test coverage

---

## 📋 Files to Modify/Create

### Files to Modify

1. **`business/pipelines/graphrag.py`**:
   - Enhance `_resolve_stage_selection()` to warn about out-of-order selection
   - Add `_warn_out_of_order()` method
   - Improve logging for dependency resolution

### Files to Create/Enhance

1. **`tests/business/pipelines/test_graphrag_dependency_validation.py`**:
   - Test out-of-order warnings
   - Test dependency validation edge cases
   - Test error handling when dependencies missing

---

## 🔧 Approach

### 1. Out-of-Order Detection

- Compare selected stage order with STAGE_ORDER
- Warn if stages are selected in non-sequential order
- Example: Selecting "detection,extraction" should warn

### 2. Enhanced Logging

- Log when dependencies are auto-included
- Log when stages are out of order
- Log dependency resolution process

---

## ✅ Tests Required

1. **Test out-of-order warning**:
   - Select stages out of order (e.g., "detection,extraction")
   - Verify warning is logged
2. **Test dependency auto-include logging**:
   - Select stage without dependencies
   - Verify logging shows auto-included dependencies
3. **Test error on missing dependencies**:
   - Select stage with missing dependencies and auto_include_deps=False
   - Verify ValueError is raised

---

## 🚀 Implementation Steps

1. Add `_warn_out_of_order()` method
2. Enhance `_resolve_stage_selection()` with warnings
3. Add comprehensive logging
4. Write tests for new functionality
5. Run tests and verify
6. Update documentation

---

## 📝 Success Criteria

- ✅ Warnings logged for out-of-order stage selection
- ✅ Enhanced logging for dependency resolution
- ✅ All tests passing
- ✅ Backward compatible (existing functionality preserved)

---

## 🔗 Related

- **Parent PLAN**: PLAN_GRAPHRAG-PIPELINE-VISUALIZATION.md
- **Previous Achievement**: 0.2 - Resume from Failure
- **Base Implementation**: 0.1 - Stage Selection (dependency validation foundation)

---

**Status**: ✅ Complete

## ✅ Implementation Summary

- Implemented `_warn_out_of_order()` to detect and warn about out-of-order stage selection
- Enhanced `_resolve_stage_selection()` with out-of-order warnings
- Added logging for dependency auto-inclusion
- Created comprehensive test suite (10 tests, all passing)

**Tests**: All 10 tests passing

- Out-of-order detection (single, sequential, reversed, mixed)
- Dependency validation (auto-include, error on missing)
- Order maintenance
- Logging verification
