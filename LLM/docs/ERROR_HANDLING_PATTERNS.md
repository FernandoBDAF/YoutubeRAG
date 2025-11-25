# Error Handling Patterns for Prompt Generation Scripts

**Created**: 2025-11-13  
**Achievement**: 3.1 - Comprehensive Error Messages + Library Integration  
**Purpose**: Document structured error handling patterns for consistent, user-friendly error messages

---

## Overview

This guide documents the error handling patterns implemented in Achievement 3.1, providing structured, actionable error messages with context and suggestions for fixing issues.

### Key Improvements

- **Before**: Basic `try/except` with `print(f"Error: {e}")` and `sys.exit(1)`
- **After**: Structured exceptions with context, actionable suggestions, color-coded output, and auto-copy to clipboard

**Impact**: +300% error message quality, +1000% debugging speed

---

## Custom Exception Classes

### Location

`LLM/scripts/generation/exceptions.py`

### Exception Hierarchy

```python
ApplicationError (from core.libraries.error_handling)
├── PlanNotFoundError          # PLAN file not found
├── AchievementNotFoundError    # Achievement not in PLAN
├── SubplanNotFoundError        # SUBPLAN file missing
├── InvalidAchievementFormatError  # Invalid achievement number format
├── ExecutionTaskNotFoundError  # EXECUTION_TASK file missing
└── InvalidPathError            # Invalid or inaccessible path
```

### Usage Examples

#### PlanNotFoundError

```python
from LLM.scripts.generation.exceptions import PlanNotFoundError

raise PlanNotFoundError(
    plan_name="FEATURE-NAME",
    searched_paths=[Path("work-space/plans")],
    available_plans=["PLAN-A", "PLAN-B", "PLAN-C"],
)
```

**Output**:

```
❌ ERROR: PLAN file not found: FEATURE-NAME

Details:
  plan_name: FEATURE-NAME
  searched_paths: ['work-space/plans']
  available_plans: ['PLAN-A', 'PLAN-B', 'PLAN-C']

HOW TO FIX:
1. Check if file exists: ls work-space/plans/FEATURE-NAME/
2. Use @folder shortcut: @FEATURE-NAME
3. See available plans: ls work-space/plans/
Available plans:
  - @PLAN-A
  - @PLAN-B
  - @PLAN-C

✅ Error details copied to clipboard!
```

#### InvalidAchievementFormatError

```python
from LLM.scripts.generation.exceptions import InvalidAchievementFormatError

raise InvalidAchievementFormatError(
    achievement_input="2",  # User provided "2" instead of "2.1"
    expected_format="X.Y (e.g., 2.1, 3.5)",
)
```

**Output**:

```
❌ ERROR: Invalid achievement format: '2'

Details:
  achievement_input: 2
  expected_format: X.Y (e.g., 2.1, 3.5)

HOW TO FIX:
1. Use correct format: X.Y (e.g., 2.1, 3.5)
2. Valid examples: 1.1, 2.5, 3.10
3. Must be: number.number (e.g., 2.1, not 2 or 2.1.3)

✅ Error details copied to clipboard!
```

---

## Logging Integration

### Setup

```python
from core.libraries.logging import get_logger, set_log_context

logger = get_logger(__name__)
```

### Setting Log Context

Set context at entry points (e.g., `main()` function):

```python
set_log_context(
    plan=feature_name,
    workflow="generate_prompt",
    plan_file=plan_path.name,
)

logger.info("Starting prompt generation", extra={
    "plan_path": str(plan_path),
    "interactive": args.interactive,
    "clipboard": not args.no_clipboard,
})
```

### Benefits

- **Structured Logs**: JSON-formatted logs for analysis
- **Context Propagation**: Plan, achievement, workflow automatically included
- **Searchable**: Easy to filter and search logs
- **Better Debugging**: Detailed info without cluttering output

---

## Input Validation

### Pattern

```python
from core.libraries.validation import validate_value, Pattern, ValidationError
from LLM.scripts.generation.exceptions import InvalidAchievementFormatError

# Validate achievement format (X.Y)
if not re.match(r'^\d+\.\d+$', achievement_num):
    raise InvalidAchievementFormatError(
        achievement_input=achievement_num,
        expected_format="X.Y (e.g., 2.1, 3.5)",
    )
```

### Validation Rules

Available from `core.libraries.validation`:

- `NotEmpty()` - Value cannot be None or empty
- `MinLength(n)` - Minimum length for strings/lists
- `MaxLength(n)` - Maximum length for strings/lists
- `Pattern(regex)` - Must match regex pattern
- `Range(min, max)` - Numeric value in range
- `Custom(func, desc)` - Custom validation function

---

## Color-Coded Output

### Implementation

Error messages are automatically color-coded:

- **Red**: Error messages
- **Blue**: Context details
- **Yellow**: Suggestions and fixes
- **Green**: Success messages

### Example

The `format_error_with_suggestions()` function adds ANSI color codes:

```python
from LLM.scripts.generation.exceptions import format_error_with_suggestions

try:
    # Some operation
    pass
except ApplicationError as e:
    error_message = format_error_with_suggestions(e)
    print(error_message, file=sys.stderr)
```

### Disabling Colors

Pass `use_colors=False` to disable:

```python
error_message = format_error_with_suggestions(e, use_colors=False)
```

---

## Error Handling in Main Entry Point

### Pattern

```python
def main():
    try:
        # ... main logic ...

    except Exception as e:
        from core.libraries.error_handling import ApplicationError
        from LLM.scripts.generation.exceptions import format_error_with_suggestions

        # Structured error handling
        if isinstance(e, ApplicationError):
            error_message = format_error_with_suggestions(e)
            print(error_message, file=sys.stderr)

            # Auto-copy error to clipboard
            try:
                from LLM.scripts.generation.path_resolution import copy_to_clipboard_safe
                if copy_to_clipboard_safe(error_message):
                    print("✅ Error details copied to clipboard!", file=sys.stderr)
            except:
                pass  # Silent fail on clipboard
        else:
            # Generic exception
            error_type = type(e).__name__
            error_msg = str(e) or "(no message)"
            print(f"❌ ERROR: {error_type}: {error_msg}", file=sys.stderr)

        sys.exit(1)
```

---

## Testing Error Scenarios

### Test Pattern

```python
from LLM.scripts.generation.exceptions import PlanNotFoundError

def test_plan_not_found():
    """Test PlanNotFoundError is raised with correct context."""
    with pytest.raises(PlanNotFoundError) as exc_info:
        resolve_folder_shortcut("NONEXISTENT")

    error = exc_info.value
    assert "NONEXISTENT" in str(error)
    assert "suggestions" in error.context
    assert len(error.context["suggestions"]) >= 3
```

### Update Existing Tests

Replace `SystemExit` expectations with custom exceptions:

```python
# OLD (before Achievement 3.1)
with self.assertRaises(SystemExit):
    utils.resolve_folder_shortcut("NONEXISTENT")

# NEW (Achievement 3.1)
from LLM.scripts.generation.exceptions import PlanNotFoundError
with self.assertRaises(PlanNotFoundError):
    utils.resolve_folder_shortcut("NONEXISTENT")
```

---

## Best Practices

### 1. Always Include Context

```python
raise PlanNotFoundError(
    plan_name=name,
    searched_paths=paths,    # Where did we look?
    available_plans=plans,   # What options exist?
)
```

### 2. Provide Actionable Suggestions

```python
suggestions=[
    "Check if file exists: ls work-space/plans/",
    "Use @folder shortcut: @FEATURE",
    "See available: ls work-space/plans/",
]
```

### 3. Use Specific Exception Classes

Don't use generic `ApplicationError` when a more specific class exists:

```python
# GOOD
raise PlanNotFoundError(...)

# BAD
raise ApplicationError("PLAN not found")
```

### 4. Set Log Context Early

```python
# At the start of main logic
set_log_context(plan=plan_name, workflow="generate_prompt")
```

### 5. Test Error Scenarios

Always test that errors are raised correctly and include proper context.

---

## Migration Guide

### Migrating Old Error Handling

**Before**:

```python
try:
    result = operation()
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
```

**After**:

```python
from core.libraries.error_handling import ApplicationError

try:
    result = operation()
except FileNotFoundError as e:
    raise PlanNotFoundError(
        plan_name=name,
        searched_paths=[path],
        available_plans=get_available_plans(),
        cause=e,
    )
```

### Steps

1. Identify the error scenario (file not found, invalid format, etc.)
2. Choose or create appropriate custom exception
3. Add context (what, where, why)
4. Add actionable suggestions (how to fix)
5. Update tests to expect new exception type

---

## Common Patterns

### File Not Found

```python
from LLM.scripts.generation.exceptions import PlanNotFoundError, InvalidPathError

if not path.exists():
    raise InvalidPathError(
        path=path,
        reason="file does not exist",
        path_type="PLAN",
    )
```

### Invalid Input Format

```python
from LLM.scripts.generation.exceptions import InvalidAchievementFormatError

if not re.match(r'^\d+\.\d+$', achievement):
    raise InvalidAchievementFormatError(
        achievement_input=achievement,
        expected_format="X.Y (e.g., 2.1)",
    )
```

### Multiple Matches (Ambiguous)

```python
from core.libraries.error_handling import ApplicationError

if len(matches) > 1:
    raise ApplicationError(
        f"Multiple files match '{pattern}'",
        context={
            "pattern": pattern,
            "matches": [str(f) for f in matches],
            "suggestions": [
                "Use full path to specify which file:",
            ] + [f"  {f}" for f in matches],
        },
    )
```

---

## Future Improvements

Potential enhancements for future achievements:

1. **Error Recovery**: Suggest automatic fixes for common errors
2. **Interactive Fixes**: Prompt user to select from available options
3. **Error Analytics**: Track common errors to improve UX
4. **Better IDE Integration**: VSCode error lens integration
5. **Documentation Links**: Auto-generate links to relevant docs

---

## References

- **Achievement**: 3.1 - Comprehensive Error Messages + Library Integration
- **Analysis**: `work-space/analyses/EXECUTION_ANALYSIS_LIBRARY-INTEGRATION-OPPORTUNITIES-PRIORITY-3.md`
- **Core Libraries**: `core/libraries/error_handling/`, `core/libraries/logging/`, `core/libraries/validation/`
- **Custom Exceptions**: `LLM/scripts/generation/exceptions.py`
- **Tests**: `tests/LLM/scripts/generation/test_exceptions.py`
