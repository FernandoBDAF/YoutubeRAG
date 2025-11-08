# SUBPLAN: Comprehensive Interactive Mode

**Type**: SUBPLAN  
**Mother Plan**: PLAN_PROMPT-GENERATOR-UX-AND-FOUNDATION.md  
**Plan**: PROMPT-GENERATOR-UX-AND-FOUNDATION  
**Achievement Addressed**: Achievement 0.3 (Comprehensive Interactive Mode)  
**Achievement**: 0.3  
**Status**: ✅ Complete  
**Created**: 2025-11-09 23:50 UTC  
**Estimated Effort**: 3-4 hours

**File Location**: `work-space/plans/PROMPT-GENERATOR-UX-AND-FOUNDATION/subplans/SUBPLAN_PROMPT-GENERATOR-UX-AND-FOUNDATION_03.md`

**Size**: 200-600 lines

---

## 🎯 Objective

Integrate the `--interactive` flag with ALL workflow states in `generate_prompt.py`, providing a consistent interactive menu experience across all recommendation types (create SUBPLAN, create EXECUTION, continue EXECUTION, create next EXECUTION, synthesize results, PLAN complete, conflict detected). This ensures users can navigate the entire workflow interactively with smart defaults and zero friction.

---

## 📋 Deliverables

### Core Implementation

1. **Enhanced `prompt_interactive_menu()` function**

   - Support for all 7 workflow states
   - Consistent menu structure
   - Smart defaults (copy on Enter)
   - State-specific options

2. **Integration with all recommendation paths**

   - `create_subplan` → Interactive menu
   - `create_execution` → Interactive menu
   - `continue_execution` → Interactive menu
   - `create_next_execution` → Interactive menu (multi-execution)
   - `synthesize_results` → Interactive menu
   - `plan_complete` → Interactive menu
   - `conflict_detected` → Interactive menu

3. **Menu options for each state**
   - Copy to clipboard (default)
   - View full prompt
   - Save to file
   - Execute command (if applicable)
   - Get help
   - Exit

### Testing

1. **Unit tests** for `prompt_interactive_menu()`

   - Test each workflow state
   - Test menu options
   - Test smart defaults
   - Test error handling

2. **Integration tests** for interactive workflow
   - Test full workflow interactively
   - Test state transitions
   - Test clipboard integration

### Documentation

1. **Help text updates**

   - Document `--interactive` flag
   - Show examples for each state
   - Explain menu options

2. **Code documentation**
   - Inline comments for menu logic
   - Docstrings for new functions

---

## 🎨 Approach

**Strategy**: Extend existing interactive menu implementation to cover all workflow states, ensuring consistent UX and smart defaults across the entire prompt generation workflow.

**Design Principles**:

1. **Consistency**: Same menu structure for all states
2. **Smart Defaults**: Copy to clipboard on Enter (most common action)
3. **Context-Aware**: Menu options adapt to workflow state
4. **Zero Friction**: Minimal keystrokes for common actions
5. **Helpful**: Clear instructions and feedback

---

## 🔄 Execution Strategy

**Execution Count**: Single

**Rationale**: This is a cohesive enhancement to a single function (`prompt_interactive_menu()`) with integration across multiple call sites. A single execution can handle the analysis, implementation, and testing systematically.

**Execution Plan**:

**EXECUTION_TASK_03_01**: Comprehensive Interactive Mode Implementation

- Analyze current interactive menu implementation
- Design menu structure for all 7 workflow states
- Implement enhanced `prompt_interactive_menu()` function
- Integrate with all recommendation paths
- Create comprehensive tests
- Update documentation
- Estimated: 3-4 hours

**Dependencies**: None (builds on existing interactive menu from Achievement 1.7 in PLAN_RESTORE-EXECUTION-WORKFLOW-AUTOMATION)

---

## 🎯 Implementation Phases

### Phase 1: Analysis & Design (30 minutes)

**Tasks**:

1. Review current `prompt_interactive_menu()` implementation
2. Identify all 7 workflow states in `generate_prompt.py`
3. Design menu structure for each state
4. Define state-specific menu options
5. Plan integration points

**Deliverables**:

- Menu structure design
- State-to-options mapping
- Integration plan

### Phase 2: Core Implementation (90 minutes)

**Tasks**:

1. Enhance `prompt_interactive_menu()` function

   - Add support for all workflow states
   - Implement state-specific menu options
   - Add smart defaults (Enter = copy)
   - Add error handling

2. Integrate with all recommendation paths

   - Line ~1877: `create_subplan` state
   - Line ~1892: `create_execution` state
   - Line ~1906: `continue_execution` state
   - Line ~2002: `create_next_execution` state
   - Line ~2014: `next_achievement` state
   - Completion message path
   - Conflict detection path

3. Add menu option handlers
   - Copy to clipboard
   - View full prompt
   - Save to file
   - Execute command (if applicable)
   - Get help
   - Exit

**Deliverables**:

- Enhanced `prompt_interactive_menu()` function
- Integration with all 7 workflow states
- Menu option handlers

### Phase 3: Testing (60 minutes)

**Tasks**:

1. Create unit tests

   - Test menu for each workflow state
   - Test menu options
   - Test smart defaults
   - Test error handling
   - Test clipboard integration

2. Create integration tests

   - Test full interactive workflow
   - Test state transitions
   - Test with real PLAN files

3. Manual testing
   - Test each workflow state manually
   - Verify UX is smooth
   - Check error messages

**Deliverables**:

- `tests/LLM/scripts/generation/test_interactive_menu.py` (15+ tests)
- Integration test suite
- Manual test results

### Phase 4: Documentation & Verification (30 minutes)

**Tasks**:

1. Update help text

   - Document `--interactive` flag
   - Add examples for each state
   - Explain menu options

2. Add code documentation

   - Inline comments for menu logic
   - Docstrings for functions

3. Verify all deliverables
   - Run: `ls -1 [each deliverable]`
   - Confirm tests pass
   - Check documentation complete

**Deliverables**:

- Updated help text
- Code documentation
- Verification results

---

## 🧪 Testing Strategy

### Unit Tests (10+ tests)

**Test Coverage**:

1. `test_interactive_menu_create_subplan()` - Menu for create SUBPLAN state
2. `test_interactive_menu_create_execution()` - Menu for create EXECUTION state
3. `test_interactive_menu_continue_execution()` - Menu for continue EXECUTION state
4. `test_interactive_menu_create_next_execution()` - Menu for multi-execution state
5. `test_interactive_menu_next_achievement()` - Menu for next achievement state
6. `test_interactive_menu_plan_complete()` - Menu for completion state
7. `test_interactive_menu_conflict()` - Menu for conflict state
8. `test_menu_option_copy()` - Test copy to clipboard option
9. `test_menu_option_view()` - Test view full prompt option
10. `test_menu_option_save()` - Test save to file option
11. `test_menu_option_execute()` - Test execute command option
12. `test_menu_smart_defaults()` - Test Enter key = copy
13. `test_menu_error_handling()` - Test invalid input handling

**Test File**: `tests/LLM/scripts/generation/test_interactive_menu.py`

### Integration Tests (3+ tests)

**Test Scenarios**:

1. Full interactive workflow (create SUBPLAN → create EXECUTION → complete)
2. Multi-execution workflow (create → continue → create next)
3. Conflict detection workflow (conflict → resolve → continue)

**Test File**: `tests/LLM/scripts/generation/test_interactive_workflow.py`

### Manual Testing

**Test Cases**:

1. Run `--interactive` with each workflow state
2. Verify menu appears correctly
3. Test each menu option
4. Verify clipboard works
5. Check error messages

---

## ✅ Success Criteria

**Functional**:

- ✅ Interactive mode works for all 7 workflow states
- ✅ Menu structure is consistent across states
- ✅ Smart defaults work (Enter = copy)
- ✅ All menu options functional
- ✅ Clipboard integration works

**Quality**:

- ✅ 13+ unit tests passing
- ✅ 3+ integration tests passing
- ✅ Code documented with inline comments
- ✅ Help text updated
- ✅ No regressions (existing tests pass)

**UX**:

- ✅ Zero friction (minimal keystrokes)
- ✅ Clear instructions
- ✅ Helpful feedback
- ✅ Consistent experience
- ✅ 50% faster for interactive users

---

## 🚨 Risks & Mitigations

### Risk 1: Breaking Existing Interactive Menu

**Mitigation**:

- Review existing implementation first
- Extend, don't replace
- Test existing functionality
- Keep backward compatibility

### Risk 2: Menu Complexity

**Mitigation**:

- Keep menu simple (5-6 options max)
- Use smart defaults
- Clear option descriptions
- Consistent across states

### Risk 3: Integration Points

**Mitigation**:

- Map all 7 integration points first
- Test each integration individually
- Integration tests for full workflow

---

## 📚 Context & References

**Related Work**:

- Achievement 1.7 in `PLAN_RESTORE-EXECUTION-WORKFLOW-AUTOMATION.md` (initial interactive menu)
- `EXECUTION_ANALYSIS_INTERACTIVE-CLI-ENHANCEMENT-STRATEGY.md` (design analysis)

**Code Locations**:

- `LLM/scripts/generation/generate_prompt.py` (lines 1877-2016, recommendation paths)
- Existing `prompt_interactive_menu()` function (if exists)

**Templates**:

- `LLM/templates/SUBPLAN-TEMPLATE.md`
- `LLM/templates/EXECUTION_TASK-TEMPLATE.md`

---

## 🎯 Expected Results

**After Completion**:

1. **Users can run**:

   ```bash
   python generate_prompt.py @RESTORE --next --interactive
   ```

   And get interactive menu for ANY workflow state:

   - Creating SUBPLAN
   - Creating EXECUTION
   - Continuing EXECUTION
   - Creating next EXECUTION
   - Synthesizing results
   - Completing PLAN
   - Resolving conflicts

2. **Menu Experience**:

   ```
   🎯 What would you like to do?

   1. Copy to clipboard (default)
   2. View full prompt
   3. Save to file
   4. Execute command
   5. Get help
   6. Exit

   Choose [1-6] or press Enter for default:
   ```

3. **Smart Defaults**:

   - Enter key = Copy to clipboard (most common)
   - Clear feedback: "✅ Copied to clipboard!"
   - Consistent across all states

4. **50% Faster Workflow**:
   - No need to add `--clipboard` flag
   - No need to manually copy text
   - Interactive navigation through workflow

**Quality Metrics**:

- 13+ tests passing
- 0 regressions
- Code documented
- Help text updated

---

**Status**: ✅ Design Complete, Ready for Execution  
**Next Step**: Create EXECUTION_TASK_PROMPT-GENERATOR-UX-AND-FOUNDATION_03_01.md  
**Estimated Time**: 3-4 hours  
**Confidence**: High (building on existing implementation)
