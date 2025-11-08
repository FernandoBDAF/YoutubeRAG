# SUBPLAN: Enhance Prompt Generator with Interactive Menu

**Type**: SUBPLAN  
**Mother Plan**: PLAN_RESTORE-EXECUTION-WORKFLOW-AUTOMATION.md  
**Achievement**: 1.7  
**Status**: ✅ Complete  
**Created**: 2025-11-09 07:00 UTC  
**Estimated Effort**: 2-3 hours

---

## 🎯 Objective

Add lightweight interactive menu to `generate_prompt.py` that improves user experience by asking "What do you want to do?" instead of telling users what to do. Result: 30-50% faster daily workflow with better UX.

**Key Value**: Immediate user experience improvement while comprehensive GRAMMAPLAN CLI is being built separately.

**Strategic Context**: User feedback during Achievement 1.6 work revealed daily workflow friction. This addresses it with simple, low-risk enhancement.

---

## 📋 Deliverables

### Files to Modify

1. **`LLM/scripts/generation/generate_prompt.py`**
   - Add `prompt_interactive_menu()` function (~60-80 lines)
   - Refactor main logic to call interactive menu
   - Add CLI flags: `--auto`, `--show`, `--save-file`
   - Update docstrings with examples
   - Preserve backward compatibility

### Files to Create

None (keep lightweight - single script enhancement)

### Documentation Updates

1. **In-code docstrings** for new functions
2. **Updated help text** for new CLI flags
3. **Example output** in docstring showing all menu options

---

## 🎨 Design: Interactive Menu Flow

### Menu Design by Workflow State

#### When SUBPLAN exists, ready for EXECUTION:

```
🎯 What would you like to do?

1. Copy prompt & show next command (default)
2. View prompt first, then copy
3. View execution plan details
4. Save prompt to file
5. Exit
```

#### When PLAN ready, need SUBPLAN:

```
🎯 What would you like to do?

1. Copy SUBPLAN prompt & show next step (default)
2. View prompt details first
3. Save prompt to file
4. Go back to PLAN view
5. Exit
```

#### When all achievements complete:

```
🎯 What would you like to do?

1. Ready to end PLAN (completion protocol)
2. View remaining work
3. Archive and finalize
4. Exit
```

### Menu Behavior

**User Input**:
- Numbers 1-5 (keyboard)
- Default: Press Enter for option 1
- Invalid: Show error, re-prompt

**Option Handling**:
1. **Copy & show next** (default)
   - Silent clipboard copy
   - Show confirmation: "✅ Copied to clipboard!"
   - Show next step guidance
   
2. **View first, then copy**
   - Display full prompt text
   - Ask "Copy to clipboard? [Y/n]: "
   - Show confirmation if yes
   
3. **View details**
   - Show SUBPLAN summary
   - Show execution strategy
   - Show success criteria (hidden from default output)
   
4. **Save to file**
   - Ask for filename: "Save to file [/tmp/prompt.md]: "
   - Write prompt to file
   - Show confirmation: "✅ Saved to /tmp/prompt.md"
   
5. **Exit**
   - Clean exit with "Goodbye!"

---

## 🔌 Implementation Strategy

### Phase 1: Analyze Current Code (30 min)

**Tasks**:
1. Read current `generate_prompt.py` (lines 1-50, 1200+, main areas)
2. Map workflow states and output points
3. Identify where menu should be inserted
4. Document current function signatures

**Success**: Clear understanding of code structure and output flow

### Phase 2: Design Menu Logic (30 min)

**Tasks**:
1. Define `prompt_interactive_menu()` function
2. Map workflow states to menu options
3. Design user interaction flow (input validation, error handling)
4. Plan CLI flag integration

**Success**: Function design document (in code comments), clear logic flow

### Phase 3: Implement Menu (1 hour)

**Tasks**:
1. Create `prompt_interactive_menu()` function with:
   - Menu display logic
   - User input handling
   - Option execution (copy, view, save, etc.)
   - Error handling (clipboard fail, file write fail, etc.)

2. Add helper functions:
   - `copy_to_clipboard(text)` - silent copy with fallback
   - `save_prompt_to_file(text, filename)` - file saving
   - `get_user_choice(menu_options)` - input validation

3. Refactor main workflow:
   - Call `prompt_interactive_menu()` instead of print/copy
   - Pass workflow state to menu function
   - Preserve existing output logic (use internally)

4. Add CLI flags:
   - `--auto` - Skip menu (use option 1 by default)
   - `--show` - View prompt before menu (use option 2)
   - `--save-file <path>` - Save instead of copy (use option 4)
   - Can be combined: `--show --save-file /tmp/prompt.md`

**Success**: Menu functional, all options working, backward compatible

### Phase 4: Test & Refine (30 min)

**Test Cases**:
1. Manual test - Interactive menu with different workflow states
2. Test each menu option (copy, view, save, details, exit)
3. Test edge cases:
   - Invalid input (non-numeric, out of range)
   - Clipboard unavailable (fallback to manual copy)
   - File save failure (permission denied, invalid path)
   - Terminal without TTY (auto-enable --auto mode)
4. Test CLI flags:
   - `--auto` skips menu
   - `--show` displays prompt before menu
   - `--save-file` saves to file
   - Combined flags work correctly
5. Backward compatibility: Existing scripts still work

**Success**: All tests passing, no regressions

### Phase 5: Documentation (15 min)

**Tasks**:
1. Update function docstrings:
   - `prompt_interactive_menu()` - purpose, params, returns
   - Helper functions - clear purpose and behavior
2. Add code comments for complex logic
3. Update script-level docstring with CLI flags
4. Add example output showing menu in action

**Success**: Code is self-documenting, no external docs needed

---

## 🧪 Test Strategy

### Manual Testing Scenarios

**Scenario 1: SUBPLAN exists, no EXECUTION_TASK**
```bash
python generate_prompt.py --next work-space/plans/PLAN_NAME.md
# Should show: Menu with 5 options (copy & show, view first, etc.)
# User selects "1"
# Should: Copy to clipboard, show next command
```

**Scenario 2: All achievements complete**
```bash
python generate_prompt.py --next PLAN_NAME.md
# Should show: Menu with completion options
# User selects "1" (Ready to end PLAN)
# Should: Show plan completion protocol
```

**Scenario 3: Edge case - clipboard unavailable**
```bash
# Uninstall pyperclip to simulate unavailable clipboard
python generate_prompt.py --next PLAN_NAME.md
# User selects "1" (copy option)
# Should: Fall back gracefully
# Output: "⚠️ Clipboard not available, please copy manually from output above"
```

**Scenario 4: Power user - skip menu**
```bash
python generate_prompt.py --next PLAN_NAME.md --auto
# Should: Skip menu, auto-copy (option 1 behavior)
# No prompt shown
```

**Scenario 5: View first, then save**
```bash
python generate_prompt.py --next PLAN_NAME.md --show --save-file /tmp/prompt.txt
# Should: Display prompt, skip menu, save to file
# Output: "✅ Saved to /tmp/prompt.txt"
```

### Edge Cases

1. **Invalid menu selection** (user types "6" or "abc")
   - Show error message
   - Re-prompt with menu
   - No crash or exception

2. **Clipboard library missing**
   - Gracefully handle import error
   - Show message: "Clipboard unavailable, copy manually"
   - Option 1 becomes "Show prompt (copy manually)"

3. **File save permission denied**
   - Catch exception
   - Show helpful error: "Cannot write to file (permission denied), try different path"
   - Offer to save to /tmp instead

4. **TTY detection (non-interactive terminal)**
   - Auto-detect if not interactive
   - Auto-enable `--auto` mode
   - Skip menu display

5. **Multiple selections (e.g., user accidentally selects twice)**
   - Process once, exit cleanly
   - No loop (one choice per run)

---

## ✅ Expected Results

### Immediate Outcomes

**Code Changes**:
- `generate_prompt.py`: +60-80 lines (menu + helpers)
- No new files
- No dependency changes (use what we have)

**User Impact**:
- Interactive menu for every prompt generation
- Clear options presented
- Better UX with guidance

**Compatibility**:
- Backward compatible (--auto for scripts)
- No breaking changes
- Existing workflows still work

### Workflow Improvement

**Before**:
- Run command
- Read output
- Manually decide what to do
- Type next command
- ~2-3 minutes per cycle

**After**:
- Run command
- See interactive menu
- Select option (1 keystroke)
- Copy + guidance shown
- Type next command
- ~1-2 minutes per cycle

**Gain**: 30-50% faster workflow

---

## 🎓 Designer Notes

### Key Design Decisions

1. **Interactive vs Auto-Execution**
   - Chosen: Interactive (ask user)
   - Rationale: User has control, safer, more transparent

2. **Menu Style**
   - Chosen: Simple numbered options (no dependencies)
   - Rationale: Terminal-first, works everywhere, simple to maintain

3. **Clipboard Behavior**
   - Chosen: Always copy silently with confirmation
   - Rationale: Most common action, user expects this

4. **Backward Compatibility**
   - Chosen: Preserve all existing behavior, add `--auto` flag
   - Rationale: Existing scripts and workflows must not break

5. **Menu Placement**
   - Chosen: After workflow detection, before main output
   - Rationale: User sees menu first, then decides action

### Implementation Tips

1. **Use existing patterns**: Match current code style
2. **Test early**: Manual test menu before full implementation
3. **Error handling**: Graceful fallbacks (clipboard, file, input)
4. **TTY detection**: Use `sys.stdin.isatty()` to detect interactive mode
5. **Keep it simple**: Don't over-engineer - simple is better

### Potential Enhancements (Future)

- Remember last choice (use as default)
- Config file to set default behavior
- Rich menu styling (with next phase)
- Keyboard shortcuts (advanced)
- Menu history (what user selected)

---

## 📊 Success Criteria

**Functional Success**:
- [ ] Interactive menu displays for all workflow states
- [ ] All menu options functional (copy, view, save, details, exit)
- [ ] Clipboard integration working (with fallback)
- [ ] File saving working for option 4
- [ ] CLI flags working (--auto, --show, --save-file)
- [ ] Edge cases handled gracefully

**Quality Success**:
- [ ] Code is clean and maintainable
- [ ] Docstrings clear and complete
- [ ] Comments for complex logic
- [ ] No new dependencies
- [ ] ~60-80 lines of code (lightweight)

**Compatibility Success**:
- [ ] Backward compatible (--auto for scripts)
- [ ] No breaking changes
- [ ] Works with existing workflows
- [ ] Tested with real PLAN files

**User Experience Success**:
- [ ] Menu is clear and easy to use
- [ ] Next steps are obvious
- [ ] Faster workflow (perceived or measured)
- [ ] Better guidance for new users

---

## 🔗 References

### Analysis Document
- `EXECUTION_ANALYSIS_INTERACTIVE-CLI-ENHANCEMENT-STRATEGY.md` (comprehensive strategy analysis with 4 options evaluated, rationale, and design decisions)

### Related Code
- `LLM/scripts/generation/generate_prompt.py` (main file to modify)
- `LLM/scripts/generation/generate_execution_prompt.py` (similar script, may benefit from same approach later)

### Dependencies
- `pyperclip` library (if available, for clipboard)
- Python stdlib: `sys`, `os`, `pathlib` (already used)

### Methodology
- LLM-METHODOLOGY.md
- EXECUTION_ANALYSIS documents (Category 5)

---

## 💡 Rationale

**Why This Achievement**:
- User feedback revealed daily workflow friction
- Analysis showed interactive menu could reduce friction by 30-50%
- Lightweight implementation (2-3 hours)
- Independent from GRAMMAPLAN work
- Immediate value while comprehensive CLI is built

**Why Now**:
- Achievement 1.6 bug fix is prerequisite (fixing detection logic)
- After 1.6, prompt generation will work correctly for all states
- Interactive menu adds finishing touch
- Quick win to show progress and value

**Why This Approach**:
- Simple interactive menu (not full platform)
- Validates UX patterns for GRAMMAPLAN
- Low risk (changes only one script)
- Backward compatible
- Foundation for future enhancements

---

**SUBPLAN Status**: Ready for Execution

**Next**: Create EXECUTION_TASK_RESTORE-EXECUTION-WORKFLOW-AUTOMATION_17_01.md and execute implementation

