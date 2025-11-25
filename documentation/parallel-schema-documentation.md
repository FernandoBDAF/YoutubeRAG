# parallel.json Schema Documentation

**Version**: 1.0  
**Created**: 2025-11-13  
**Schema File**: `parallel-schema.json`  
**Achievement**: 1.2 - parallel.json Schema Implemented

---

## 📋 Overview

### Purpose

The `parallel.json` file is a structured dependency tree that enables **automated parallel execution** of achievements and execution tasks within a PLAN. It defines which work items can run simultaneously and which must wait for dependencies to complete.

**Key Benefits**:
- **Time Savings**: Reduce PLAN completion time by 30-65%
- **Resource Optimization**: Maximize executor utilization
- **Dependency Clarity**: Explicit dependency documentation
- **Automated Orchestration**: Enable automated parallel workflow management

### When to Create parallel.json

Create a `parallel.json` file when:

1. **Multiple Independent Achievements**: PLAN has 3+ achievements that can run in parallel
2. **Multi-Execution Achievements**: Single achievement can be split into parallel executions
3. **Cross-Priority Opportunities**: Achievements across priorities can run in parallel
4. **Significant Time Savings**: Parallelization saves 4+ hours

**Do NOT create** when:
- PLAN has < 3 achievements
- All achievements are tightly coupled (sequential dependencies)
- Total PLAN time is < 10 hours (overhead not worth it)
- Coordination costs exceed time savings

### How It's Used in Workflow

```
1. PLAN Analysis (Achievement 1.1)
   ↓
   Use parallel_prompt_builder.py to analyze PLAN
   ↓
2. Generate parallel.json (Manual or LLM-assisted)
   ↓
   Create parallel.json with dependency tree
   ↓
3. Validation (Achievement 1.3)
   ↓
   Validate parallel.json against schema
   ↓
4. Workflow Integration (Achievement 2.1)
   ↓
   generate_prompt.py reads parallel.json
   ↓
5. Parallel Execution
   ↓
   Multiple executors work simultaneously
   ↓
6. Status Tracking
   ↓
   Filesystem-first status updates
```

### Relationship to Filesystem-First Philosophy

**Critical Principle**: Status is **derived from filesystem**, not persisted in `parallel.json`.

**How It Works**:
1. `parallel.json` defines the dependency structure (static)
2. Status is computed at runtime by checking filesystem:
   - `SUBPLAN_*.md` exists → `subplan_created`
   - `EXECUTION_TASK_*.md` exists → `execution_created`
   - `APPROVED_*.md` exists → `complete`
   - `FIX_*.md` exists → `failed`
3. Workflow scripts read `parallel.json` for dependencies, compute status from filesystem

**Why This Matters**:
- Single source of truth: filesystem
- No status synchronization issues
- Status always accurate
- Supports multi-executor scenarios

---

## 📖 Field Reference

### Root Level Fields

#### `plan_name` (string, required)

**Description**: Name of the PLAN being analyzed.

**Format**: Uppercase with hyphens (e.g., `GRAPHRAG-OBSERVABILITY-VALIDATION`)

**Example**:
```json
{
  "plan_name": "PARALLEL-EXECUTION-AUTOMATION"
}
```

**Validation**:
- Must match PLAN file name (without `PLAN_` prefix and `.md` suffix)
- Used to locate PLAN directory and files

---

#### `parallelization_level` (string, required)

**Description**: Level of parallelization being applied.

**Allowed Values**:
- `"level_1"`: Same achievement multi-execution (split single achievement into parallel executions)
- `"level_2"`: Same priority intra-plan (parallel achievements within same priority)
- `"level_3"`: Cross-priority (parallel achievements across different priorities)

**Example**:
```json
{
  "parallelization_level": "level_2"
}
```

**Usage**:
- Determines which prompt template to use (`parallel_prompt_builder.py`)
- Affects validation rules (Level 1 requires `sub_executions`, Level 2/3 use `priority_groups`)

---

#### `created_date` (string, required)

**Description**: Date when `parallel.json` was created.

**Format**: ISO 8601 date format (`YYYY-MM-DD`)

**Example**:
```json
{
  "created_date": "2025-11-13"
}
```

**Usage**:
- Tracking and auditing
- Helps identify stale parallel.json files

---

#### `achievements` (array, required)

**Description**: Array of achievement objects with dependency information.

**Structure**: Array of achievement objects (see Achievement Object section)

**Example**:
```json
{
  "achievements": [
    {
      "achievement_id": "1.1",
      "title": "Backend API Implementation",
      "status": "not_started",
      "dependencies": [],
      "estimated_hours": 8
    }
  ]
}
```

**Validation**:
- Must contain at least 1 achievement
- Each achievement must have unique `achievement_id`

---

#### `priority_groups` (array, optional)

**Description**: Groups of achievements by priority for Level 2/3 parallelization.

**Structure**: Array of priority group objects

**Example**:
```json
{
  "priority_groups": [
    {
      "priority": 1,
      "achievements": ["1.1", "1.2"]
    },
    {
      "priority": 2,
      "achievements": ["2.1", "2.2"]
    }
  ]
}
```

**Usage**:
- Level 2: Identifies achievements within same priority that can run in parallel
- Level 3: Shows priority structure for cross-priority analysis
- Empty array for Level 1 (not applicable)

---

#### `cross_priority_dependencies` (array, optional)

**Description**: Dependencies between achievements across different priorities.

**Structure**: Array of dependency objects with `from_achievement` and `to_achievement`

**Example**:
```json
{
  "cross_priority_dependencies": [
    {
      "from_achievement": "2.1",
      "to_achievement": "1.1"
    },
    {
      "from_achievement": "3.1",
      "to_achievement": "2.1"
    }
  ]
}
```

**Interpretation**:
- `"from_achievement": "2.1", "to_achievement": "1.1"` means "2.1 depends on 1.1"
- Achievement 2.1 cannot start until 1.1 is complete

**Usage**:
- Level 3: Critical for cross-priority parallelization
- Level 2: Documents dependencies on prior priorities
- Empty array for Level 1 (not applicable)

---

#### `analysis_notes` (string, optional)

**Description**: Summary of parallel opportunities and rationale.

**Example**:
```json
{
  "analysis_notes": "Priority 3 achievements are read-only validation tasks that can run in parallel after Priority 2.2 completes. Expected time savings: 6 hours (63% reduction)."
}
```

**Usage**:
- Provides context for parallelization decisions
- Documents expected time savings
- Explains independence rationale

---

### Achievement Object Fields

#### `achievement_id` (string, required)

**Description**: Unique identifier for the achievement.

**Format**: `X.Y` where X is priority and Y is achievement number (e.g., `"1.1"`, `"2.3"`)

**Pattern**: Must match regex `^\d+\.\d+$`

**Example**:
```json
{
  "achievement_id": "2.1"
}
```

**Validation**:
- Must be unique within `achievements` array
- Must match achievement numbering in PLAN

---

#### `title` (string, optional)

**Description**: Human-readable title of the achievement.

**Example**:
```json
{
  "title": "Backend API Implementation"
}
```

**Usage**:
- Improves readability
- Helps identify achievements without reading PLAN
- Not required for validation

---

#### `status` (string, required)

**Description**: Current status of the achievement.

**⚠️ IMPORTANT**: Status is **derived from filesystem at runtime**, not persisted in `parallel.json`. The value in the file is a snapshot or placeholder.

**Allowed Values**:
- `"not_started"`: No work begun (no SUBPLAN file)
- `"subplan_created"`: SUBPLAN file exists
- `"execution_created"`: EXECUTION_TASK file exists
- `"in_progress"`: Work in progress (inferred from activity)
- `"complete"`: APPROVED file exists
- `"failed"`: FIX file exists
- `"skipped"`: Achievement skipped

**Example**:
```json
{
  "status": "not_started"
}
```

**Filesystem Mapping**:
```python
def get_achievement_status(achievement_id):
    if approved_file_exists(achievement_id):
        return "complete"
    elif fix_file_exists(achievement_id):
        return "failed"
    elif execution_task_exists(achievement_id):
        return "execution_created"
    elif subplan_exists(achievement_id):
        return "subplan_created"
    else:
        return "not_started"
```

---

#### `dependencies` (array, required)

**Description**: Array of achievement IDs that this achievement depends on.

**Format**: Array of strings matching `achievement_id` pattern (`^\d+\.\d+$`)

**Example**:
```json
{
  "dependencies": ["1.1", "1.2"]
}
```

**Interpretation**:
- Empty array `[]`: No dependencies, can start immediately
- `["1.1"]`: Depends on achievement 1.1, must wait for 1.1 to complete
- `["1.1", "1.2"]`: Depends on both 1.1 and 1.2, must wait for both

**Validation**:
- Dependency IDs must exist in `achievements` array
- No circular dependencies allowed
- Dependencies should be in earlier priorities (best practice)

---

#### `estimated_hours` (number, optional)

**Description**: Estimated time in hours to complete the achievement.

**Example**:
```json
{
  "estimated_hours": 8
}
```

**Usage**:
- Critical path calculation
- Resource allocation
- Time savings estimation

---

#### `actual_hours` (number, optional)

**Description**: Actual time spent on the achievement (for tracking).

**Example**:
```json
{
  "actual_hours": 7.5
}
```

**Usage**:
- Post-execution tracking
- Estimation improvement
- Not used during planning

---

#### `started_at` (string, optional)

**Description**: ISO 8601 timestamp when execution started.

**Format**: `YYYY-MM-DDTHH:MM:SSZ`

**Example**:
```json
{
  "started_at": "2025-11-13T14:30:00Z"
}
```

**Usage**:
- Execution tracking
- Timeline visualization
- Not required for planning

---

#### `completed_at` (string, optional)

**Description**: ISO 8601 timestamp when execution completed.

**Format**: `YYYY-MM-DDTHH:MM:SSZ`

**Example**:
```json
{
  "completed_at": "2025-11-13T22:30:00Z"
}
```

**Usage**:
- Execution tracking
- Actual time calculation (`completed_at - started_at`)

---

#### `executor` (string, optional)

**Description**: Name or ID of the executor assigned to this achievement.

**Example**:
```json
{
  "executor": "executor_1"
}
```

**Usage**:
- Multi-executor scenarios
- Resource allocation
- Workload balancing

---

#### `sub_executions` (array, optional)

**Description**: Array of sub-execution objects for Level 1 parallelization.

**Structure**: Similar to achievement objects but with `execution_id` (e.g., `"1.1.1"`)

**Example**:
```json
{
  "sub_executions": [
    {
      "execution_id": "2.1.1",
      "title": "Unit Tests Execution",
      "status": "not_started",
      "dependencies": [],
      "estimated_hours": 2,
      "executor": "executor_1"
    }
  ]
}
```

**Usage**:
- Level 1 parallelization only
- Empty array for Level 2/3
- Each sub-execution is an EXECUTION_TASK file

---

## 📊 Status Reference

### Status Enum Values

| Status | Description | Filesystem Indicator | Terminal? |
|--------|-------------|---------------------|-----------|
| `not_started` | No work begun | No SUBPLAN file | No |
| `subplan_created` | SUBPLAN exists | `SUBPLAN_*.md` exists | No |
| `execution_created` | EXECUTION_TASK exists | `EXECUTION_TASK_*.md` exists | No |
| `in_progress` | Work in progress | Inferred from activity | No |
| `complete` | Achievement approved | `APPROVED_*.md` exists | Yes |
| `failed` | Fixes required | `FIX_*.md` exists | No |
| `skipped` | Achievement skipped | Documented in PLAN | Yes |

### Status Transitions

See `parallel-status-transitions.md` for detailed state diagram.

**Key Transitions**:
- `not_started` → `subplan_created`: SUBPLAN file created
- `subplan_created` → `execution_created`: EXECUTION_TASK file created
- `execution_created` → `in_progress`: Work begins
- `in_progress` → `complete`: APPROVED file created
- `in_progress` → `failed`: FIX file created
- `failed` → `in_progress`: Fixes applied, work continues

### Filesystem-First Philosophy

**Why Filesystem-First?**:
1. **Single Source of Truth**: Filesystem is authoritative
2. **No Synchronization**: No need to update parallel.json status
3. **Multi-Executor Safe**: Multiple executors can work without conflicts
4. **Always Accurate**: Status computed on-demand from filesystem

**Implementation**:
```python
def can_start_achievement(achievement_id, parallel_json):
    # Check dependencies
    deps = parallel_json['achievements'][achievement_id]['dependencies']
    for dep in deps:
        if get_achievement_status(dep) != 'complete':
            return False  # Dependency not complete
    return True  # All dependencies complete
```

---

## 💡 Usage Examples

### Example 1: Level 1 Parallelization

**Scenario**: Split testing achievement into 3 parallel executions

```json
{
  "plan_name": "TESTING-FRAMEWORK",
  "parallelization_level": "level_1",
  "created_date": "2025-11-13",
  "achievements": [
    {
      "achievement_id": "2.1",
      "title": "Testing Framework Implementation",
      "status": "subplan_created",
      "dependencies": [],
      "estimated_hours": 7,
      "sub_executions": [
        {
          "execution_id": "2.1.1",
          "title": "Unit Tests",
          "status": "not_started",
          "dependencies": [],
          "estimated_hours": 2,
          "executor": "executor_1"
        },
        {
          "execution_id": "2.1.2",
          "title": "Integration Tests",
          "status": "not_started",
          "dependencies": [],
          "estimated_hours": 2,
          "executor": "executor_2"
        },
        {
          "execution_id": "2.1.3",
          "title": "E2E Tests",
          "status": "not_started",
          "dependencies": [],
          "estimated_hours": 3,
          "executor": "executor_3"
        }
      ]
    }
  ],
  "priority_groups": [],
  "cross_priority_dependencies": [],
  "analysis_notes": "Testing split into 3 parallel executions. Time savings: 4 hours (57% reduction)."
}
```

**Key Points**:
- Single achievement with `sub_executions`
- All sub-executions have empty dependencies (can run in parallel)
- `priority_groups` is empty (not applicable for Level 1)

---

### Example 2: Level 2 Parallelization

**Scenario**: 3 validation achievements in same priority run in parallel

```json
{
  "plan_name": "GRAPHRAG-OBSERVABILITY-VALIDATION",
  "parallelization_level": "level_2",
  "created_date": "2025-11-13",
  "achievements": [
    {
      "achievement_id": "3.1",
      "title": "Query Scripts Validated",
      "status": "not_started",
      "dependencies": ["2.2"],
      "estimated_hours": 3.5
    },
    {
      "achievement_id": "3.2",
      "title": "Explanation Tools Validated",
      "status": "not_started",
      "dependencies": ["2.2"],
      "estimated_hours": 2.5
    },
    {
      "achievement_id": "3.3",
      "title": "Quality Metrics Validated",
      "status": "not_started",
      "dependencies": ["2.2"],
      "estimated_hours": 3.5
    }
  ],
  "priority_groups": [
    {
      "priority": 3,
      "achievements": ["3.1", "3.2", "3.3"]
    }
  ],
  "cross_priority_dependencies": [
    {
      "from_achievement": "3.1",
      "to_achievement": "2.2"
    },
    {
      "from_achievement": "3.2",
      "to_achievement": "2.2"
    },
    {
      "from_achievement": "3.3",
      "to_achievement": "2.2"
    }
  ],
  "analysis_notes": "Priority 3 achievements are read-only validations. Time savings: 6 hours (63% reduction)."
}
```

**Key Points**:
- Multiple achievements, all depend on 2.2
- `priority_groups` shows they're in same priority
- `cross_priority_dependencies` documents dependency on prior priority
- Once 2.2 completes, all three can start in parallel

---

### Example 3: Level 3 Parallelization

**Scenario**: Backend and frontend run in parallel across priorities

```json
{
  "plan_name": "FEATURE-IMPLEMENTATION",
  "parallelization_level": "level_3",
  "created_date": "2025-11-13",
  "achievements": [
    {
      "achievement_id": "1.1",
      "title": "Backend API",
      "status": "not_started",
      "dependencies": [],
      "estimated_hours": 8
    },
    {
      "achievement_id": "1.2",
      "title": "Frontend UI",
      "status": "not_started",
      "dependencies": [],
      "estimated_hours": 8
    },
    {
      "achievement_id": "2.1",
      "title": "Integration",
      "status": "not_started",
      "dependencies": ["1.1", "1.2"],
      "estimated_hours": 6
    }
  ],
  "priority_groups": [
    {
      "priority": 1,
      "achievements": ["1.1", "1.2"]
    },
    {
      "priority": 2,
      "achievements": ["2.1"]
    }
  ],
  "cross_priority_dependencies": [
    {
      "from_achievement": "2.1",
      "to_achievement": "1.1"
    },
    {
      "from_achievement": "2.1",
      "to_achievement": "1.2"
    }
  ],
  "analysis_notes": "Backend and frontend run in parallel. Time savings: 8 hours."
}
```

**Key Points**:
- Achievements across priorities (1.1, 1.2 in P1; 2.1 in P2)
- 1.1 and 1.2 have no dependencies (can start immediately)
- 2.1 depends on both 1.1 and 1.2 (must wait for Priority 1)
- `cross_priority_dependencies` explicitly documents this

---

## 🎯 Best Practices

### Dependency Management

1. **Explicit is Better**: Always document dependencies explicitly, even if "obvious"
2. **No Circular Dependencies**: Validate dependency graph is acyclic
3. **Minimal Dependencies**: Only add dependencies that are truly blocking
4. **Cross-Priority Clarity**: Use `cross_priority_dependencies` for Level 3

### Independence Validation

Before marking achievements as parallel, validate:

1. **Technical Independence**:
   - No shared code files (except common libraries)
   - No shared state (global variables, singletons)
   - No shared resources (databases, files)

2. **Testing Independence**:
   - Independent test suites
   - Independent test data
   - Independent test environments

3. **Mergeability**:
   - Minimal overlapping file changes
   - Clear merge strategy documented

4. **Dependency Clarity**:
   - No implicit dependencies
   - No hidden ordering requirements

### Common Patterns

**Pattern 1: Fan-Out (Level 1)**
```
SUBPLAN → [Exec 1, Exec 2, Exec 3] → Achievement Complete
```
- Single achievement, multiple executions
- All executions independent
- Merge at end

**Pattern 2: Parallel Priority (Level 2)**
```
Priority N-1 Complete → [Ach N.1, Ach N.2, Ach N.3] → Priority N Complete
```
- Multiple achievements, same priority
- All depend on prior priority
- No inter-achievement dependencies

**Pattern 3: Split Priorities (Level 3)**
```
[Ach 1.1, Ach 1.2] → Ach 2.1 → Ach 3.1
```
- Achievements across priorities
- Some parallel, some sequential
- Complex dependency graph

### Anti-Patterns to Avoid

❌ **Anti-Pattern 1: Fake Parallelization**
```json
{
  "achievements": [
    {"achievement_id": "1.1", "dependencies": []},
    {"achievement_id": "1.2", "dependencies": ["1.1"]}
  ]
}
```
**Problem**: 1.2 depends on 1.1, so they can't run in parallel. Don't create parallel.json if everything is sequential.

❌ **Anti-Pattern 2: Over-Parallelization**
```json
{
  "achievements": [
    {"achievement_id": "1.1", "estimated_hours": 0.5},
    {"achievement_id": "1.2", "estimated_hours": 0.5}
  ]
}
```
**Problem**: Achievements are too small (< 1 hour). Coordination overhead exceeds time savings.

❌ **Anti-Pattern 3: Missing Dependencies**
```json
{
  "achievements": [
    {"achievement_id": "2.1", "dependencies": []},
    {"achievement_id": "2.2", "dependencies": []}
  ]
}
```
**Problem**: If 2.2 actually depends on 2.1 but it's not documented, parallel execution will fail.

❌ **Anti-Pattern 4: Circular Dependencies**
```json
{
  "achievements": [
    {"achievement_id": "1.1", "dependencies": ["1.2"]},
    {"achievement_id": "1.2", "dependencies": ["1.1"]}
  ]
}
```
**Problem**: Circular dependency - neither can start. Validation should catch this.

---

## 🔧 Integration with Workflow

### How generate_prompt.py Uses parallel.json

```python
# 1. Read parallel.json
parallel_data = json.load(open('parallel.json'))

# 2. Get current achievement
current_achievement = get_next_achievement()

# 3. Check dependencies
deps = parallel_data['achievements'][current_achievement]['dependencies']
for dep in deps:
    if get_achievement_status(dep) != 'complete':
        print(f"Waiting for {dep} to complete...")
        return

# 4. Check for parallel opportunities
parallel_achievements = find_parallel_achievements(current_achievement)
if parallel_achievements:
    print(f"Can run in parallel with: {parallel_achievements}")

# 5. Generate prompt
generate_prompt(current_achievement)
```

### Validation Script (Achievement 1.3)

The validation script will:
1. Validate JSON against schema
2. Check for circular dependencies
3. Verify all dependency IDs exist
4. Validate achievement numbering
5. Check parallelization level consistency

---

## 📚 Related Documentation

- **Schema File**: `parallel-schema.json`
- **Status Transitions**: `documentation/parallel-status-transitions.md`
- **Examples**:
  - Level 1: `examples/parallel_level1_example.json` + `_explained.md`
  - Level 2: `examples/parallel_level2_example.json` + `_explained.md`
  - Level 3: `examples/parallel_level3_example.json` + `_explained.md`
- **Prompt Builder**: `LLM/scripts/generation/parallel_prompt_builder.py`
- **Analysis Examples**:
  - `examples/parallel_analysis_graphrag_observability.md`
  - `examples/parallel_analysis_prompt_generator.md`

---

**Last Updated**: 2025-11-13  
**Version**: 1.0  
**Maintainer**: PARALLEL-EXECUTION-AUTOMATION team

