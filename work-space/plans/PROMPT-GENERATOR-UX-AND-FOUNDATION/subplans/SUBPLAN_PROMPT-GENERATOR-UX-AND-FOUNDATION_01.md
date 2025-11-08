# SUBPLAN: Clipboard by Default & Short Commands

**Type**: SUBPLAN  
**Mother Plan**: PLAN_PROMPT-GENERATOR-UX-AND-FOUNDATION.md  
**Plan**: PROMPT-GENERATOR-UX-AND-FOUNDATION  
**Achievement Addressed**: Achievement 0.1 (Clipboard by Default & Short Commands)  
**Achievement**: 0.1  
**Status**: ✅ Complete  
**Created**: 2025-11-09 18:30 UTC  
**Completed**: 2025-11-09 21:00 UTC  
**Actual Effort**: 2.5 hours

---

## 🎯 Objective

Transform generate_prompt.py UX by making clipboard the default behavior and supporting short folder-based commands, eliminating daily friction and delivering 80% faster workflow.

**Key Goal**: `python generate_prompt @RESTORE` should work and auto-copy to clipboard (vs current 120-character command with manual flag)

---

## 📋 Deliverables

### Files to Modify

1. **`LLM/scripts/generation/generate_prompt.py`**
   - Change clipboard default (lines ~1776-1790)
   - Add `--no-clipboard` flag
   - Enhance @folder resolution (lines ~1400-1430)
   - Update all output points to copy to clipboard
   - Update help text and docstring

### Files to Create

2. **`tests/LLM/scripts/generation/test_clipboard_and_shortcuts.py`**
   - Test clipboard default behavior
   - Test --no-clipboard flag
   - Test @folder resolution
   - Test all output types copied

### Documentation Updates

3. **In-code docstrings** for modified functions
4. **Help text** for new flags

---

## 🎨 Design: Implementation Strategy

### Part 1: Clipboard Default (45 minutes)

**Current Behavior**:

```python
# Line ~1776
if args.clipboard:
    try:
        import pyperclip
        pyperclip.copy(prompt)
        print("\n✅ Prompt copied to clipboard!")
    except:
        print("\n⚠️ Could not copy to clipboard")
```

**New Behavior**:

```python
# Clipboard is default, --no-clipboard disables
clipboard_enabled = not args.no_clipboard  # Default True

if clipboard_enabled:
    try:
        import pyperclip
        pyperclip.copy(prompt)
        print("\n✅ Copied to clipboard!")
    except Exception as e:
        print(f"\n⚠️ Could not copy to clipboard: {e}")
        print("(Output still shown below)")
```

**Changes**:

- Add `--no-clipboard` argument to argparse
- Change default from False to True
- Update all output points (prompts, errors, conflicts)
- Copy conflict messages to clipboard too

**Files**: `generate_prompt.py` lines ~1317, ~1776-1790

---

### Part 2: Folder Path Resolution (45 minutes)

**Current Behavior**:

```python
# @PLAN_NAME.md searches work-space/plans/ recursively
# But requires full filename
```

**New Behavior**:

```python
# @folder_name searches for PLAN file in that folder
# Examples:
#   @RESTORE → work-space/plans/RESTORE-EXECUTION-WORKFLOW-AUTOMATION/PLAN_*.md
#   @GRAPHRAG → work-space/plans/GRAPHRAG-OBSERVABILITY-EXCELLENCE/PLAN_*.md

def resolve_folder_shortcut(folder_name):
    """
    Resolve @folder_name to PLAN file.

    Args:
        folder_name: Folder name (e.g., "RESTORE", "GRAPHRAG")

    Returns:
        Path to PLAN file in that folder

    Logic:
        1. Search work-space/plans/ for folders matching pattern
        2. Look for PLAN_*.md in matching folder
        3. Return first match
        4. Error if not found or multiple matches
    """
    plans_dir = Path("work-space/plans")

    # Find folders containing the name (case-insensitive partial match)
    matching_folders = []
    for folder in plans_dir.iterdir():
        if folder.is_dir() and folder_name.upper() in folder.name.upper():
            matching_folders.append(folder)

    if not matching_folders:
        print(f"❌ No folder found matching '@{folder_name}'")
        print(f"   Searched in: {plans_dir}")
        sys.exit(1)

    if len(matching_folders) > 1:
        print(f"⚠️ Multiple folders match '@{folder_name}':")
        for f in matching_folders:
            print(f"   - {f.name}")
        print("   Use more specific name or full path")
        sys.exit(1)

    # Find PLAN file in folder
    folder = matching_folders[0]
    plan_files = list(folder.glob("PLAN_*.md"))

    if not plan_files:
        print(f"❌ No PLAN file found in {folder.name}")
        sys.exit(1)

    if len(plan_files) > 1:
        print(f"⚠️ Multiple PLAN files in {folder.name}")
        sys.exit(1)

    return plan_files[0]
```

**Integration**:

```python
# In main(), after argument parsing
if plan_path.startswith('@'):
    if '/' in plan_path or plan_path.endswith('.md'):
        # @PLAN_NAME.md format (existing behavior)
        plan_path = resolve_plan_shorthand(plan_path)
    else:
        # @folder_name format (new behavior)
        folder_name = plan_path[1:]  # Remove @
        plan_path = resolve_folder_shortcut(folder_name)
```

**Files**: `generate_prompt.py` new function + lines ~1400-1430

---

### Part 3: Copy All Output (30 minutes)

**Current Behavior**:

- Only prompts copied
- Conflict messages NOT copied
- Error messages NOT copied

**New Behavior**:

- ALL output copied to clipboard
- Prompts → copied
- Conflict messages → copied
- Error messages → copied
- Completion messages → copied

**Implementation**:

```python
def copy_to_clipboard_safe(text, clipboard_enabled=True):
    """
    Safely copy text to clipboard with error handling.

    Args:
        text: Text to copy
        clipboard_enabled: Whether clipboard is enabled

    Returns:
        bool: True if copied successfully
    """
    if not clipboard_enabled:
        return False

    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception as e:
        print(f"\n⚠️ Could not copy to clipboard: {e}")
        return False

# Use throughout:
output = generate_conflict_message(...)
print(output)
if copy_to_clipboard_safe(output, clipboard_enabled):
    print("\n✅ Copied to clipboard!")
```

**Files**: `generate_prompt.py` new function + all output points

---

## 🔌 Execution Strategy

**Single Execution**: One EXECUTION_TASK (straightforward implementation)

**Phases**:

1. **Implement clipboard default** (45 min)
2. **Implement folder resolution** (45 min)
3. **Copy all output** (30 min)
4. **Create tests** (45 min)
5. **Verify and document** (15 min)

**Total**: 3 hours

**Dependencies**: None (self-contained)

---

## 🧪 Test Strategy

### Test File

**Location**: `tests/LLM/scripts/generation/test_clipboard_and_shortcuts.py`

**Test Cases**:

1. **test_clipboard_default_enabled**

   - Run without --no-clipboard
   - Verify clipboard contains output
   - Verify confirmation message shown

2. **test_no_clipboard_flag_disables**

   - Run with --no-clipboard
   - Verify clipboard NOT modified
   - Verify no confirmation message

3. **test_folder_shortcut_resolution**

   - Test @RESTORE → finds PLAN file
   - Test @GRAPHRAG → finds PLAN file
   - Test @PROMPT → finds PLAN file

4. **test_folder_shortcut_not_found**

   - Test @NONEXISTENT
   - Verify helpful error message
   - Verify suggestions

5. **test_folder_shortcut_multiple_matches**

   - Test ambiguous name
   - Verify lists matches
   - Verify asks for specificity

6. **test_folder_shortcut_no_plan_file**

   - Folder exists but no PLAN file
   - Verify helpful error

7. **test_conflict_message_copied**

   - Trigger conflict detection
   - Verify conflict message in clipboard
   - Verify confirmation shown

8. **test_error_message_copied**

   - Trigger error (file not found)
   - Verify error message in clipboard

9. **test_backward_compatibility**
   - Test old @PLAN_NAME.md format
   - Verify still works
   - Test full paths
   - Verify still works

**Total**: 9 test functions

**Coverage Target**: All new code paths

---

## ✅ Expected Results

### User Experience

**Before**:

```bash
python LLM/scripts/generation/generate_prompt.py \
  work-space/plans/RESTORE-EXECUTION-WORKFLOW-AUTOMATION/PLAN_RESTORE-EXECUTION-WORKFLOW-AUTOMATION.md \
  --next --clipboard
```

- 120 characters
- Must remember --clipboard flag
- 5 minutes to type/find path

**After**:

```bash
python generate_prompt @RESTORE
```

- 32 characters (73% shorter)
- Clipboard automatic
- 1 minute (80% faster)

### Functionality

**Clipboard**:

- ✅ All output auto-copied (prompts, errors, conflicts)
- ✅ Confirmation message shown
- ✅ --no-clipboard disables if needed
- ✅ Graceful fallback if clipboard unavailable

**Folder Resolution**:

- ✅ @RESTORE → finds RESTORE-EXECUTION-WORKFLOW-AUTOMATION plan
- ✅ @GRAPHRAG → finds GRAPHRAG-OBSERVABILITY-EXCELLENCE plan
- ✅ @PROMPT → finds PROMPT-GENERATOR-UX-AND-FOUNDATION plan
- ✅ Helpful errors if not found
- ✅ Backward compatible with old format

### Code Quality

- ✅ Clean implementation
- ✅ Comprehensive tests (9 test functions)
- ✅ Error handling
- ✅ Backward compatible
- ✅ Well-documented

---

## 📊 Success Criteria

### Functional

- ✅ `python generate_prompt @RESTORE` works
- ✅ Output auto-copied to clipboard
- ✅ Conflict messages auto-copied
- ✅ Error messages auto-copied
- ✅ `--no-clipboard` disables copying
- ✅ Backward compatible (old commands work)

### Technical

- ✅ 9 tests passing
- ✅ No regressions (existing tests pass)
- ✅ Code clean and documented
- ✅ Error handling comprehensive

### User Experience

- ✅ 80% faster workflow
- ✅ Zero friction (no flag needed)
- ✅ Helpful errors
- ✅ Confirmation messages

---

## 🔗 References

**Parent PLAN**: `PLAN_PROMPT-GENERATOR-UX-AND-FOUNDATION.md`

**Code to Modify**: `LLM/scripts/generation/generate_prompt.py`

**Templates**:

- `LLM/templates/SUBPLAN-TEMPLATE.md`
- `LLM/templates/EXECUTION_TASK-TEMPLATE.md`

**Guides**:

- `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md`
- `LLM-METHODOLOGY.md`

---

## 💡 Designer Notes

**Design Philosophy**:

- Smart defaults (clipboard on by default)
- Power user flexibility (--no-clipboard)
- Progressive disclosure (@folder simple, full path power)
- Backward compatibility (old commands work)

**Key Decisions**:

1. Clipboard default (serves 95% of users)
2. @folder resolution (convenience without breaking old)
3. Copy all output (errors too, not just prompts)
4. Graceful fallback (if clipboard fails, still show output)

**Implementation Approach**:

- Add resolve_folder_shortcut() function
- Add copy_to_clipboard_safe() helper
- Modify argparse (--no-clipboard instead of --clipboard)
- Update all output points
- Comprehensive tests

**Estimated Complexity**: Medium (clear requirements, straightforward implementation)

---

**Status**: ✅ Design Complete - Ready for EXECUTION_TASK creation  
**Next**: Create EXECUTION_TASK_PROMPT-GENERATOR-UX-AND-FOUNDATION_01_01.md  
**Execution**: Single execution (straightforward, no parallelization needed)
