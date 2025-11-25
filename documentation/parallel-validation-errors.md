# Parallel.json Validation Errors

**Purpose**: Common validation errors, their meanings, and how to fix them.

**Created**: 2025-11-13  
**Achievement**: 1.3 - Validation Script Created

---

## Overview

The `validate_parallel_json.py` script performs three types of validation:

1. **Schema Validation**: Checks required fields, types, and formats
2. **Circular Dependency Detection**: Detects cycles in dependency graph
3. **Dependency Existence**: Ensures all dependencies exist in achievements list

This document describes common errors and how to fix them.

---

## Schema Validation Errors

### Missing Required Field

**Error Message**:

```
Missing required field: 'plan_name'. Add this field to your parallel.json.
```

**Cause**: A required field is missing from the parallel.json file.

**Required Fields**:

- `plan_name` (string)
- `parallelization_level` (string enum)
- `achievements` (array)

**Fix**:

```json
{
  "plan_name": "YOUR-PLAN-NAME",
  "parallelization_level": "level_1",
  "achievements": []
}
```

---

### Invalid Parallelization Level

**Error Message**:

```
Invalid parallelization_level: 'invalid'. Must be one of: level_1, level_2, level_3.
Fix: Change to 'level_1', 'level_2', or 'level_3'.
```

**Cause**: The `parallelization_level` field has an invalid value.

**Valid Values**:

- `"level_1"` - Same achievement, multi-execution
- `"level_2"` - Same priority, intra-plan
- `"level_3"` - Cross-priority

**Fix**:

```json
{
  "parallelization_level": "level_1"
}
```

---

### Invalid Achievement ID Format

**Error Message**:

```
Achievement 0: Invalid achievement_id format: 'invalid'. Must match pattern X.Y (e.g., '1.1', '2.3').
Fix: Change to format like '1.1' or '2.3'.
```

**Cause**: Achievement ID doesn't match the required pattern `X.Y` (e.g., `1.1`, `2.3`).

**Valid Formats**:

- `"1.1"`, `"1.2"`, `"1.3"` (Priority 1 achievements)
- `"2.1"`, `"2.2"`, `"2.3"` (Priority 2 achievements)
- `"3.1"`, `"3.2"`, `"3.3"` (Priority 3 achievements)

**Invalid Formats**:

- `"1"` (missing decimal)
- `"1.1.1"` (too many parts)
- `"A.1"` (non-numeric)
- `"invalid"` (wrong format)

**Fix**:

```json
{
  "achievement_id": "1.1"
}
```

---

### Missing Dependencies Field

**Error Message**:

```
Achievement 1.1: Missing required field 'dependencies'.
Add: "dependencies": [] (or list of dependency IDs)
```

**Cause**: Achievement object is missing the `dependencies` field.

**Fix**:

```json
{
  "achievement_id": "1.1",
  "dependencies": []
}
```

Or with dependencies:

```json
{
  "achievement_id": "1.2",
  "dependencies": ["1.1"]
}
```

---

### Dependencies Not an Array

**Error Message**:

```
Achievement 1.1: Field 'dependencies' must be an array. Fix: Change to JSON array: []
```

**Cause**: The `dependencies` field is not a JSON array.

**Invalid**:

```json
{
  "dependencies": "1.1"
}
```

**Fix**:

```json
{
  "dependencies": ["1.1"]
}
```

---

### Invalid Status Value

**Error Message**:

```
Achievement 1.1: Invalid status: 'invalid_status'. Must be one of: not_started, subplan_created, execution_created, in_progress, complete, failed, skipped
```

**Cause**: The `status` field has an invalid value.

**Valid Status Values**:

- `"not_started"` - No files created yet
- `"subplan_created"` - SUBPLAN file exists
- `"execution_created"` - EXECUTION_TASK file exists
- `"in_progress"` - Work in progress
- `"complete"` - APPROVED file exists
- `"failed"` - FIX file exists
- `"skipped"` - SKIPPED file exists

**Note**: Status is typically **derived from filesystem** at runtime, not manually set.

**Fix**:

```json
{
  "status": "not_started"
}
```

---

## Circular Dependency Errors

### Simple Cycle

**Error Message**:

```
Circular dependency detected: 1.1 → 1.2 → 1.1.
Fix: Remove one of the dependencies to break the cycle.
```

**Cause**: Two achievements depend on each other (A→B→A).

**Example**:

```json
{
  "achievements": [
    {
      "achievement_id": "1.1",
      "dependencies": ["1.2"]
    },
    {
      "achievement_id": "1.2",
      "dependencies": ["1.1"]
    }
  ]
}
```

**Fix**: Remove one dependency to break the cycle:

```json
{
  "achievements": [
    {
      "achievement_id": "1.1",
      "dependencies": []
    },
    {
      "achievement_id": "1.2",
      "dependencies": ["1.1"]
    }
  ]
}
```

---

### Complex Cycle

**Error Message**:

```
Circular dependency detected: 1.1 → 1.2 → 1.3 → 1.1.
Fix: Remove one of the dependencies to break the cycle.
```

**Cause**: Three or more achievements form a cycle (A→B→C→A).

**Example**:

```json
{
  "achievements": [
    { "achievement_id": "1.1", "dependencies": ["1.2"] },
    { "achievement_id": "1.2", "dependencies": ["1.3"] },
    { "achievement_id": "1.3", "dependencies": ["1.1"] }
  ]
}
```

**Fix**: Remove one dependency to break the cycle:

```json
{
  "achievements": [
    { "achievement_id": "1.1", "dependencies": [] },
    { "achievement_id": "1.2", "dependencies": ["1.1"] },
    { "achievement_id": "1.3", "dependencies": ["1.2"] }
  ]
}
```

---

### Self-Dependency

**Error Message**:

```
Circular dependency detected: 1.1 → 1.1.
Fix: Remove one of the dependencies to break the cycle.
```

**Cause**: Achievement depends on itself.

**Example**:

```json
{
  "achievement_id": "1.1",
  "dependencies": ["1.1"]
}
```

**Fix**: Remove self-dependency:

```json
{
  "achievement_id": "1.1",
  "dependencies": []
}
```

---

## Dependency Existence Errors

### Missing Dependency

**Error Message**:

```
Achievement 1.2: Dependency '1.1' not found in achievements list.
Fix: Add achievement 1.1 or remove this dependency.
```

**Cause**: Achievement depends on another achievement that's not in the `achievements` array.

**Example**:

```json
{
  "achievements": [
    {
      "achievement_id": "1.2",
      "dependencies": ["1.1"]
    }
  ]
}
```

**Fix Option 1**: Add the missing achievement:

```json
{
  "achievements": [
    {
      "achievement_id": "1.1",
      "dependencies": []
    },
    {
      "achievement_id": "1.2",
      "dependencies": ["1.1"]
    }
  ]
}
```

**Fix Option 2**: Remove the dependency:

```json
{
  "achievements": [
    {
      "achievement_id": "1.2",
      "dependencies": []
    }
  ]
}
```

---

## JSON Syntax Errors

### Malformed JSON

**Error Message**:

```
Invalid JSON: Expecting ',' delimiter at line 5, column 3.
Fix: Check JSON syntax (missing comma, bracket, quote, etc.)
```

**Cause**: JSON syntax error (missing comma, bracket, quote, etc.).

**Common Issues**:

1. Missing comma between array elements
2. Missing closing bracket/brace
3. Trailing comma (not allowed in JSON)
4. Unquoted keys or values
5. Single quotes instead of double quotes

**Example (Invalid)**:

```json
{
  "plan_name": "TEST-PLAN"
  "parallelization_level": "level_1"
}
```

**Fix**:

```json
{
  "plan_name": "TEST-PLAN",
  "parallelization_level": "level_1"
}
```

---

## File Not Found

**Error Message**:

```
File not found: /path/to/parallel.json
```

**Cause**: The specified file doesn't exist.

**Fix**:

1. Check the file path is correct
2. Ensure the file exists
3. Use absolute or relative path correctly

---

## Examples

### Valid parallel.json (Level 1)

```json
{
  "plan_name": "PARALLEL-EXECUTION-AUTOMATION",
  "parallelization_level": "level_1",
  "achievements": [
    {
      "achievement_id": "2.1",
      "dependencies": ["1.3"],
      "estimated_hours": 6,
      "description": "generate_prompt.py Enhanced with Parallel Support"
    }
  ]
}
```

### Valid parallel.json (Level 2)

```json
{
  "plan_name": "GRAPHRAG-OBSERVABILITY-VALIDATION",
  "parallelization_level": "level_2",
  "achievements": [
    {
      "achievement_id": "3.1",
      "dependencies": ["2.2"],
      "estimated_hours": 4
    },
    {
      "achievement_id": "3.2",
      "dependencies": ["2.2"],
      "estimated_hours": 4
    },
    {
      "achievement_id": "3.3",
      "dependencies": ["2.2"],
      "estimated_hours": 4
    }
  ]
}
```

### Valid parallel.json (Level 3)

```json
{
  "plan_name": "PROMPT-GENERATOR-UX-AND-FOUNDATION",
  "parallelization_level": "level_3",
  "achievements": [
    {
      "achievement_id": "1.1",
      "dependencies": [],
      "estimated_hours": 3
    },
    {
      "achievement_id": "1.2",
      "dependencies": ["1.1"],
      "estimated_hours": 3
    },
    {
      "achievement_id": "2.1",
      "dependencies": ["1.2"],
      "estimated_hours": 5
    }
  ]
}
```

---

## Usage

### Validate a File

```bash
python LLM/scripts/validation/validate_parallel_json.py parallel.json
```

### Validate with Verbose Output

```bash
python LLM/scripts/validation/validate_parallel_json.py parallel.json --verbose
```

### Check Status

```bash
python LLM/scripts/validation/get_parallel_status.py parallel.json
```

---

## Related Documentation

- **Schema Documentation**: `documentation/parallel-schema-documentation.md`
- **Status Transitions**: `documentation/parallel-status-transitions.md`
- **Example Files**: `examples/parallel_level*_example.json`
- **Example Explanations**: `examples/parallel_level*_example_explained.md`

---

## Troubleshooting

### Validation Passes But Status Shows Errors

**Issue**: Validation passes, but status detection shows unexpected results.

**Cause**: Status is derived from filesystem, not from parallel.json.

**Solution**: Check filesystem for SUBPLAN, EXECUTION_TASK, APPROVED, FIX files.

### Cross-Priority Dependencies Fail Validation

**Issue**: Level 2 or Level 3 parallel.json fails validation due to missing dependencies.

**Cause**: Dependencies on achievements in different priorities aren't in the same parallel.json.

**Solution**: This is expected for cross-priority dependencies. Either:

1. Use Level 3 parallelization and include all achievements
2. Accept the validation error (dependencies will be resolved at runtime)
3. Create separate parallel.json files for each priority

---

**Last Updated**: 2025-11-13  
**Maintainer**: Achievement 1.3 - Validation Script Created
