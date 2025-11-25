# Prompt Generation System

**Purpose**: Automated prompt generation for PLAN-driven development workflow  
**Status**: Production-Ready (v3.3+)  
**Performance**: <3s prompt generation, 582x faster with caching

---

## Quick Start (5 Minutes)

### 1. Generate Your First Prompt

```bash
# Navigate to project root
cd /path/to/YoutubeRAG

# Generate prompt for next achievement
python LLM/scripts/generation/generate_prompt.py @FEATURE-NAME --next
```

**Example**:
```bash
python LLM/scripts/generation/generate_prompt.py @PROMPT-GENERATOR-UX-AND-FOUNDATION --next
```

**Output**: Structured prompt for the next incomplete achievement, ready to paste into your LLM.

### 2. What Just Happened?

The script:
1. ✅ Found your PLAN file using `@FEATURE-NAME` shortcut
2. ✅ Parsed the PLAN (cached for future runs - 582x faster!)
3. ✅ Detected workflow state (which achievements are complete)
4. ✅ Generated a structured prompt for the next achievement
5. ✅ Copied prompt to clipboard automatically

### 3. Next Steps

Try these commands:
```bash
# Generate prompt for specific achievement
python LLM/scripts/generation/generate_prompt.py @FEATURE-NAME 2.1

# Use interactive mode (guided workflow)
python LLM/scripts/generation/generate_prompt.py @FEATURE-NAME --interactive

# Get help
python LLM/scripts/generation/generate_prompt.py --help
```

---

## Commands Reference

### Basic Syntax

```bash
python LLM/scripts/generation/generate_prompt.py <plan> [achievement] [flags]
```

**Arguments**:
- `<plan>` - PLAN identifier (`@folder-name` or full path)
- `[achievement]` - Optional achievement number (e.g., `2.1`)
- `[flags]` - Optional flags (see below)

### Command Patterns

#### 1. Generate Next Achievement (Auto-Detect)

```bash
python LLM/scripts/generation/generate_prompt.py @FEATURE --next
```

**What it does**:
- Scans PLAN for achievements
- Checks which achievements are complete (looks for `APPROVED_XX.md`)
- Finds the next incomplete achievement
- Generates structured prompt

**Use when**: You want to continue work on a PLAN sequentially.

**Example**:
```bash
$ python LLM/scripts/generation/generate_prompt.py @PROMPT-GENERATOR-UX-AND-FOUNDATION --next

Analyzing PLAN: PROMPT-GENERATOR-UX-AND-FOUNDATION
Found 18 achievements total
Completed: 1.1, 1.2, 1.3, 2.1, 2.2 (5 complete)
Next: Achievement 2.3

Generating prompt for Achievement 2.3: Extract Parsing & Utilities Module
Prompt generated (450 lines)
📋 Copied to clipboard
```

#### 2. Generate Specific Achievement

```bash
python LLM/scripts/generation/generate_prompt.py @FEATURE 2.1
```

**What it does**:
- Generates prompt for the specified achievement
- Validates achievement exists in PLAN
- Includes context from PLAN

**Use when**: You want to work on a specific achievement out of order.

**Example**:
```bash
$ python LLM/scripts/generation/generate_prompt.py @PROMPT-GENERATOR-UX-AND-FOUNDATION 3.2

Generating prompt for Achievement 3.2: Performance Optimization + Library Integration
Prompt generated (380 lines)
📋 Copied to clipboard
```

#### 3. Interactive Mode

```bash
python LLM/scripts/generation/generate_prompt.py @FEATURE --interactive
```

**What it does**:
- Presents menu of available workflows
- Guides you through options
- Handles edge cases interactively

**Use when**: You're unsure which workflow to use or want guided experience.

**Example**:
```bash
$ python LLM/scripts/generation/generate_prompt.py @PROMPT-GENERATOR-UX-AND-FOUNDATION --interactive

═══════════════════════════════════════════════════════════════════════
🎯 PROMPT GENERATOR - Interactive Mode
═══════════════════════════════════════════════════════════════════════

PLAN: PROMPT-GENERATOR-UX-AND-FOUNDATION
Achievements: 18 total, 5 complete

WORKFLOW CONTEXT:
- Last completed: Achievement 2.2 (Extract Workflow State Detection)
- Next achievement: Achievement 2.3 (Extract Parsing & Utilities Module)
- No active execution found
- No pending fixes

Available Options:
1. Generate prompt for next achievement (auto-detect)
2. Generate prompt for specific achievement
3. Generate feedback prompt (FIX detected)
4. Show PLAN summary
5. Exit

Your choice [1-5]:
```

#### 4. Parallel Workflow Support (Achievement 2.1)

```bash
python LLM/scripts/generation/generate_prompt.py @FEATURE --parallel-upgrade
```

**What it does**:
- Generates a parallel discovery prompt for analyzing the PLAN
- Helps identify achievements that can be executed in parallel
- Outputs a structured prompt with independence criteria and schema template

**Use when**: You want to identify parallelization opportunities in your PLAN.

**Example**:
```bash
$ python LLM/scripts/generation/generate_prompt.py @PARALLEL-EXECUTION-AUTOMATION --parallel-upgrade

Analyze @PLAN_PARALLEL-EXECUTION-AUTOMATION.md for cross-priority parallel execution opportunities.

═══════════════════════════════════════════════════════════════════════

CONTEXT:
- PLAN: PLAN_PARALLEL-EXECUTION-AUTOMATION
- Total Achievements: 11
- Level: 3 (Cross-Priority)

INDEPENDENCE CRITERIA:
- Technical Independence (no shared state, files, resources)
- Testing Independence (parallel test execution)
- Mergeability (no merge conflicts)
- Dependency Clarity (no circular dependencies)

OUTPUT FORMAT:
{
  "plan_name": "PLAN-NAME",
  "parallelization_level": "level_2",
  "achievements": [...]
}
```

**Parallel Workflow Features**:

1. **Automatic Detection**: If a `parallel.json` file exists in your plan directory, the script automatically detects it and shows a parallel workflow indicator.

2. **Validation**: The script validates `parallel.json` before use, showing clear error messages for:
   - Invalid JSON syntax
   - Circular dependencies
   - Missing dependencies
   - Schema violations

3. **Interactive Menu**: In interactive mode, you can access the Parallel Execution Menu with options for:
   - Batch Create SUBPLANs (for same level)
   - Batch Create EXECUTIONs (for same level)
   - Run Parallel Executions (multi-executor)
   - View Dependency Graph
   - Back to Main Menu

**Example with parallel.json**:
```bash
$ python LLM/scripts/generation/generate_prompt.py @MY-PLAN --next

🔀 Parallel workflow detected for MY-PLAN
  - Parallelization level: level_2
  - Achievements: 5

💡 TIP: You can access the Parallel Execution Menu
Access Parallel Menu now? (y/N): y

================================================================================
🔀 Parallel Execution Menu
================================================================================
Plan: MY-PLAN
Parallelization Level: level_2
Achievements: 5

Options:
  1. Batch Create SUBPLANs (for same level)
  2. Batch Create EXECUTIONs (for same level)
  3. Run Parallel Executions (multi-executor)
  4. View Dependency Graph
  5. Back to Main Menu

Select option (1-5): 4

📊 Dependency Graph:
================================================================================
  1.1 → no dependencies
  1.2 → depends on: 1.1
  2.1 → no dependencies
  2.2 → depends on: 2.1
  2.3 → depends on: 2.1, 2.2
================================================================================
```

**Backward Compatibility**: All parallel workflow features are opt-in. The script works normally without `parallel.json`, maintaining full backward compatibility.

### Folder Shortcuts

Use `@folder-name` shortcut instead of full path:

```bash
# Short form (recommended)
python LLM/scripts/generation/generate_prompt.py @FEATURE

# Expands to
python LLM/scripts/generation/generate_prompt.py work-space/plans/FEATURE/PLAN_FEATURE.md
```

**Benefits**:
- Faster to type
- Auto-completion friendly
- Works with partial names (fuzzy matching)

**Examples**:
```bash
@PROMPT-GENERATOR-UX-AND-FOUNDATION
@GRAPHRAG-OBSERVABILITY-VALIDATION
@STAGE-DOMAIN-REFACTOR
```

### Flags and Options

```bash
--next                    # Generate prompt for next achievement (auto-detect)
--parallel-upgrade        # Generate parallel discovery prompt (Achievement 2.1)
--interactive, -i         # Interactive mode with guided workflow
--help, -h                # Show help message
```

---

## Common Workflows

### Workflow 1: Continue Sequential Work

**Scenario**: You're working through achievements 1.1 → 1.2 → 1.3... sequentially.

**Steps**:
1. Complete current achievement
2. Create `APPROVED_XX.md` in `execution/feedbacks/`
3. Run: `python generate_prompt.py @FEATURE --next`
4. Paste prompt into LLM
5. Repeat

**Example**:
```bash
# Just completed Achievement 2.2
echo "# APPROVED" > work-space/plans/FEATURE/execution/feedbacks/APPROVED_22.md

# Generate next prompt
python LLM/scripts/generation/generate_prompt.py @FEATURE --next
# Output: Prompt for Achievement 2.3
```

### Workflow 2: Work on Specific Achievement

**Scenario**: You need to work on Achievement 3.5 specifically (not sequential).

**Steps**:
1. Run: `python generate_prompt.py @FEATURE 3.5`
2. Paste prompt into LLM
3. Complete work
4. Create `APPROVED_35.md`

**Example**:
```bash
python LLM/scripts/generation/generate_prompt.py @PROMPT-GENERATOR-UX-AND-FOUNDATION 3.2
```

### Workflow 3: Address Fix Feedback

**Scenario**: Reviewer created `FIX_XX.md` file, you need to address issues.

**Steps**:
1. Reviewer creates `FIX_XX.md` in `execution/feedbacks/`
2. Run: `python generate_prompt.py @FEATURE --next`
3. Script auto-detects FIX file
4. Generates FIX-specific prompt with issues
5. Address issues, create `APPROVED_XX.md`

**Example**:
```bash
# Reviewer created FIX_21.md
$ python LLM/scripts/generation/generate_prompt.py @FEATURE --next

Detected FIX file: FIX_21.md
Generating FIX prompt for Achievement 2.1

Issues to address:
  🔴 CRITICAL: Test coverage below 80%
  🟡 MINOR: Docstrings incomplete

Prompt generated (320 lines)
📋 Copied to clipboard
```

**Auto-Detection**: The script automatically detects `FIX_XX.md` files and generates appropriate prompts.

### Workflow 4: Handle Conflicts

**Scenario**: Multiple developers working on same PLAN, conflicting state.

**Steps**:
1. Use `--interactive` mode to review state
2. Script shows:
   - Completed achievements
   - Active executions
   - Pending fixes
3. Choose appropriate workflow
4. Script guides you through resolution

**Example**:
```bash
python LLM/scripts/generation/generate_prompt.py @FEATURE --interactive
# Shows full state, helps choose correct action
```

### Workflow 5: Resume After Interruption

**Scenario**: You were working on Achievement 2.5, got interrupted, forgot where you were.

**Steps**:
1. Run: `python generate_prompt.py @FEATURE --interactive`
2. Review "WORKFLOW CONTEXT" section
3. See last completed achievement
4. Choose option 1 (next achievement) to resume

**Example**:
```bash
$ python LLM/scripts/generation/generate_prompt.py @FEATURE --interactive

WORKFLOW CONTEXT:
- Last completed: Achievement 2.4 (Extract Parsing Module)
- Next achievement: Achievement 2.5 (Feedback System Patterns)
- No active execution found
- No pending fixes

# Choose option 1 to resume with Achievement 2.5
```

---

## Library Integration

### Libraries Used

This system integrates 5 production-grade libraries:

1. **error_handling** - Structured exceptions with actionable suggestions
2. **logging** - Structured logging with JSON output
3. **validation** - Input validation with clear errors
4. **caching** - Performance optimization (582x speedup)
5. **metrics** - Prometheus-compatible observability

**Why These Libraries?**
- Proven patterns from production systems
- Observable performance (metrics + logs)
- Production-ready error handling
- Reusable for future CLI platform

**Benefits**:
- 🚀 **582x faster** for cached operations (7.98ms → 0.01ms)
- 📊 **91% cache hit rate** (target: 80%)
- 🎨 **Color-coded errors** with actionable suggestions
- 📈 **Prometheus metrics** for observability
- 🔍 **Structured logs** for debugging

**Learn More**: See `LIBRARY_INTEGRATION_GUIDE.md` for patterns and examples.

### Performance Characteristics

**First Run** (cache miss):
```
PLAN parsing:        ~8ms
Workflow detection:  ~5ms
Prompt generation:   ~2ms
Total:               ~15ms
```

**Cached Run** (cache hit):
```
PLAN parsing:        ~0.01ms  (582x faster!)
Workflow detection:  ~5ms
Prompt generation:   ~2ms
Total:               ~7ms
```

**Cache Behavior**:
- **Automatic invalidation**: File modification time (mtime) in cache key
- **TTL**: 5 minutes (configurable)
- **Size**: Max 50 PLANs cached
- **Hit rate**: 91% in production (target: 80%)

**Check Cache Stats**:
```python
from LLM.scripts.generation.plan_parser import PlanParser
parser = PlanParser()
stats = parser.parse_plan_file.cache.stats()
print(stats)
# {'hits': 50, 'misses': 5, 'hit_rate': 90.9%, 'size': 10, 'max_size': 50}
```

### Metrics Collection

**Metrics Collected**:
- `prompt_generation_total` (Counter) - Prompts generated (success/error)
- `prompt_generation_duration_seconds` (Histogram) - Generation time
- `plan_cache_hits_total` (Counter) - Cache hits/misses

**Export Metrics** (Prometheus format):
```python
from core.libraries.metrics import export_prometheus_text
print(export_prometheus_text())
```

**Learn More**: See `PERFORMANCE_OPTIMIZATION_GUIDE.md` for details.

---

## Troubleshooting

### Common Issues

#### Issue 1: "PLAN not found"

**Error**:
```
❌ ERROR: PLAN not found: NONEXISTENT-PLAN

Details:
  folder_name: NONEXISTENT-PLAN
  expected_path: work-space/plans/NONEXISTENT-PLAN

HOW TO FIX:
1. Check if folder 'NONEXISTENT-PLAN' exists in work-space/plans/
2. Use @folder shortcut to search by name
3. List available plans: ls work-space/plans/
```

**Solutions**:
1. Check spelling: `ls work-space/plans/ | grep -i FEATURE`
2. Use correct folder name: `@CORRECT-FEATURE-NAME`
3. Check if PLAN exists: `cat work-space/plans/FEATURE/PLAN_FEATURE.md`

#### Issue 2: "Achievement not found"

**Error**:
```
❌ ERROR: Achievement 9.9 not found in PLAN

Details:
  achievement_num: 9.9
  plan_path: work-space/plans/FEATURE/PLAN_FEATURE.md
  available_achievements: 1.1, 1.2, 1.3, 2.1, 2.2...

HOW TO FIX:
1. Check Achievement Index in PLAN file
2. Valid format: 'X.Y' (e.g., '2.1', '3.10')
3. Available: 1.1, 1.2, 1.3, 2.1, 2.2...
```

**Solutions**:
1. Check PLAN file: `grep "Achievement" work-space/plans/FEATURE/PLAN_FEATURE.md | head -20`
2. Use correct achievement number (must exist in PLAN)
3. Use `--interactive` to see available achievements

#### Issue 3: Invalid Achievement Format

**Error**:
```
❌ ERROR: Invalid achievement number format: 2-1

Details:
  provided: 2-1
  expected_format: X.Y (e.g., '2.1', '3.10')

HOW TO FIX:
1. Use format: <major>.<minor> (e.g., '2.1')
2. Both parts must be numbers
3. Examples: '1.1', '2.5', '3.10'
```

**Solutions**:
1. Use dot separator: `2.1` not `2-1`
2. Both parts must be numbers: `2.1` not `2.a`

#### Issue 4: Slow Performance

**Symptoms**: Generation takes >3s consistently.

**Solutions**:
1. Check cache hit rate:
   ```python
   from LLM.scripts.generation.plan_parser import PlanParser
   parser = PlanParser()
   stats = parser.parse_plan_file.cache.stats()
   print(f"Hit rate: {stats['hit_rate']}")
   # Should be >80%
   ```

2. Clear cache if stale:
   ```python
   parser.parse_plan_file.cache.clear()
   ```

3. Check PLAN file size:
   ```bash
   wc -l work-space/plans/FEATURE/PLAN_FEATURE.md
   # Should be <5000 lines
   ```

### Getting Help

**See Full Troubleshooting Guide**: `TROUBLESHOOTING.md`

**Check Logs**:
```bash
# Logs are written to stdout with structured format
python generate_prompt.py @FEATURE --next 2>&1 | grep ERROR
```

**Report Issues**:
1. Copy error message (auto-copied to clipboard)
2. Include command you ran
3. Include PLAN name and achievement number
4. Include relevant log output

---

## File Structure

```
LLM/scripts/generation/
├── generate_prompt.py           # Main script (entry point)
├── generate_subplan_prompt.py   # SUBPLAN prompt generation
├── generate_execution_prompt.py # EXECUTION prompt generation
├── generate_fix_prompt.py       # FIX prompt generation
├── plan_parser.py               # PLAN parsing (cached)
├── workflow_detector.py         # State detection
├── prompt_builder.py            # Prompt formatting
├── interactive_menu.py          # Interactive mode UI
├── exceptions.py                # Custom exceptions
├── utils.py                     # Shared utilities
├── path_resolution.py           # Path/folder resolution
├── README.md                    # This file
├── LIBRARY_INTEGRATION_GUIDE.md # Library patterns
├── TROUBLESHOOTING.md           # Detailed troubleshooting
└── tests/                       # Test suite

work-space/plans/
├── FEATURE/
│   ├── PLAN_FEATURE.md          # Main PLAN file
│   ├── subplans/                # SUBPLANs for achievements
│   │   ├── SUBPLAN_FEATURE_11.md
│   │   └── SUBPLAN_FEATURE_12.md
│   └── execution/               # Execution tracking
│       ├── EXECUTION_TASK_FEATURE_11_01.md
│       └── feedbacks/           # Completion/feedback
│           ├── APPROVED_11.md   # Approved achievements
│           └── FIX_12.md        # Fix feedback
```

---

## Examples

### Example 1: Complete Workflow from Start

```bash
# 1. Start new PLAN work
python LLM/scripts/generation/generate_prompt.py @NEW-FEATURE --next
# Output: Prompt for Achievement 1.1

# 2. Complete Achievement 1.1
# ... do the work ...

# 3. Mark complete
echo "# APPROVED" > work-space/plans/NEW-FEATURE/execution/feedbacks/APPROVED_11.md

# 4. Generate next prompt
python LLM/scripts/generation/generate_prompt.py @NEW-FEATURE --next
# Output: Prompt for Achievement 1.2

# 5. Repeat for each achievement
```

### Example 2: Fix Workflow

```bash
# 1. Reviewer creates FIX file
cat > work-space/plans/FEATURE/execution/feedbacks/FIX_25.md << EOF
# FIX: Achievement 2.5

## Critical Issues
- Test coverage: 65% (target: 80%)
- Missing docstrings

## Minor Issues
- Code style inconsistencies
EOF

# 2. Generate FIX prompt
python LLM/scripts/generation/generate_prompt.py @FEATURE --next
# Auto-detects FIX, generates FIX-specific prompt

# 3. Address issues
# ... fix the code ...

# 4. Mark complete
echo "# APPROVED" > work-space/plans/FEATURE/execution/feedbacks/APPROVED_25.md

# 5. Continue
python LLM/scripts/generation/generate_prompt.py @FEATURE --next
# Output: Prompt for Achievement 2.6
```

### Example 3: Check Status

```bash
# Use interactive mode to see current state
python LLM/scripts/generation/generate_prompt.py @FEATURE --interactive

# Shows:
# - Completed achievements
# - Next achievement
# - Active executions
# - Pending fixes
# - Available options
```

---

## Dependencies

**Required**:
- Python 3.8+
- Core libraries (included in repo):
  - `core/libraries/error_handling`
  - `core/libraries/logging`
  - `core/libraries/caching`
  - `core/libraries/metrics`

**Optional**:
- `pyperclip` - Clipboard support (auto-copy prompts)
  - Install: `pip install pyperclip`
  - Fallback: Manual copy if not available

**Development**:
- `pytest` - Run tests
- `pytest-cov` - Coverage reports

---

## Further Reading

**Guides**:
- `LIBRARY_INTEGRATION_GUIDE.md` - Library patterns and examples
- `TROUBLESHOOTING.md` - Detailed troubleshooting guide
- `ERROR_HANDLING_PATTERNS.md` - Error handling details
- `PERFORMANCE_OPTIMIZATION_GUIDE.md` - Caching and metrics

**Templates**:
- `LLM/templates/SUBPLAN-TEMPLATE.md` - SUBPLAN structure
- `LLM/templates/EXECUTION_TASK-TEMPLATE.md` - EXECUTION structure

**Workflow Guides**:
- `LLM/guides/SUBPLAN-WORKFLOW-GUIDE.md` - Design workflow
- `LLM/guides/EXECUTION-TAXONOMY.md` - Execution types

---

**Last Updated**: 2025-11-13  
**Version**: 3.3  
**Status**: Production-Ready


