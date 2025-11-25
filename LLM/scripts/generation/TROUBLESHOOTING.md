# Troubleshooting Guide

**Created**: 2025-11-13  
**Achievement**: 3.3 - Comprehensive User Documentation + Library Patterns  
**Purpose**: Comprehensive troubleshooting guide for common issues and debugging techniques

---

## Quick Issue Index

**Common Errors**:

1. [PLAN not found](#issue-1-plan-not-found) - File doesn't exist or wrong path
2. [Achievement not found](#issue-2-achievement-not-found) - Invalid achievement number
3. [Invalid achievement format](#issue-3-invalid-achievement-format) - Wrong number format
4. [Cache issues](#issue-4-cache-issues-stale-data) - Stale or corrupted cache
5. [Performance issues](#issue-5-slow-performance) - Generation takes >3s

**Debugging**: 6. [Reading structured logs](#debugging-with-structured-logs) - Parse JSON logs 7. [Tracing workflow execution](#tracing-workflow-execution) - Follow execution path 8. [Identifying bottlenecks](#identifying-bottlenecks) - Find slow operations 9. [Cache statistics](#checking-cache-statistics) - Monitor cache performance 10. [Viewing metrics](#viewing-metrics) - Prometheus metrics export

---

## Common Issues

### Issue 1: PLAN Not Found

**Error Message**:

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

**Causes**:

1. **Typo in folder name** - Most common cause
2. **PLAN doesn't exist** - Folder not created yet
3. **Wrong workspace** - Running from wrong directory

**Solutions**:

**1. Check spelling**:

```bash
# List all plans
ls work-space/plans/

# Search for partial match
ls work-space/plans/ | grep -i KEYWORD
```

**2. Verify folder structure**:

```bash
# Check if PLAN file exists
cat work-space/plans/FEATURE/PLAN_FEATURE.md | head -10
```

**3. Use correct @shortcut**:

```bash
# Correct
python generate_prompt.py @PROMPT-GENERATOR-UX-AND-FOUNDATION --next

# Incorrect (typo)
python generate_prompt.py @PROMPT-GENERATER-UX-AND-FOUNDATION --next
```

**4. Check working directory**:

```bash
# Must run from project root
pwd
# Should show: /path/to/YoutubeRAG

# If not, cd to correct directory
cd /path/to/YoutubeRAG
```

---

### Issue 2: Achievement Not Found

**Error Message**:

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

**Causes**:

1. **Achievement doesn't exist** - Number not in PLAN
2. **Typo in number** - e.g., `9.9` instead of `2.9`
3. **Using wrong PLAN** - Achievement exists in different PLAN

**Solutions**:

**1. Check Achievement Index**:

```bash
# View all achievements in PLAN
grep "^\*\*Achievement" work-space/plans/FEATURE/PLAN_FEATURE.md

# Output:
# **Achievement 1.1**: First Achievement
# **Achievement 1.2**: Second Achievement
# ...
```

**2. Use interactive mode to see available**:

```bash
python generate_prompt.py @FEATURE --interactive

# Shows:
# - All achievements
# - Which are complete
# - Which is next
```

**3. Verify PLAN is correct**:

```bash
# Check PLAN header
head -20 work-space/plans/FEATURE/PLAN_FEATURE.md

# Should show:
# # PLAN: Feature Name
# ...
```

---

### Issue 3: Invalid Achievement Format

**Error Message**:

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

**Causes**:

1. **Wrong separator** - Using `-` or `_` instead of `.`
2. **Missing minor** - Using `2` instead of `2.1`
3. **Non-numeric** - Using `2.a` instead of `2.1`

**Solutions**:

**1. Use dot separator**:

```bash
# Correct
python generate_prompt.py @FEATURE 2.1

# Incorrect
python generate_prompt.py @FEATURE 2-1  # BAD: dash
python generate_prompt.py @FEATURE 2_1  # BAD: underscore
```

**2. Include both parts**:

```bash
# Correct
python generate_prompt.py @FEATURE 2.1

# Incorrect
python generate_prompt.py @FEATURE 2  # BAD: missing minor version
```

**3. Use only numbers**:

```bash
# Correct
python generate_prompt.py @FEATURE 2.10  # OK: 2.10
python generate_prompt.py @FEATURE 3.5   # OK: 3.5

# Incorrect
python generate_prompt.py @FEATURE 2.a   # BAD: letter
```

---

### Issue 4: Cache Issues (Stale Data)

**Symptoms**:

- PLAN changes not reflected in prompts
- Old achievement descriptions shown
- Outdated validation scripts referenced

**Causes**:

1. **TTL not expired** - Cache still valid (5 minute TTL)
2. **Mtime not updated** - File touched but not modified
3. **Cache corruption** - Rare, but possible

**Solutions**:

**1. Check cache statistics**:

```python
from LLM.scripts.generation.plan_parser import PlanParser
from pathlib import Path

parser = PlanParser()
plan_path = Path("work-space/plans/FEATURE/PLAN_FEATURE.md")

# Parse (will use cache if available)
parser.parse_plan_file(plan_path)

# Check stats
stats = parser.parse_plan_file.cache.stats()
print(f"Cache size: {stats['size']}")
print(f"Hit rate: {stats['hit_rate']}%")
print(f"Hits: {stats['hits']}, Misses: {stats['misses']}")
```

**2. Clear cache manually**:

```python
# Clear entire cache
parser.parse_plan_file.cache.clear()

# Or clear specific entry
cache_key = f"{plan_path}:{os.path.getmtime(plan_path)}"
# Cache will auto-invalidate on next access
```

**3. Force cache miss** (edit file):

```bash
# Touch file to update mtime
touch work-space/plans/FEATURE/PLAN_FEATURE.md

# Next parse will be cache miss (new mtime)
python generate_prompt.py @FEATURE --next
```

**4. Wait for TTL expiration**:

- Default TTL: 5 minutes
- Cache automatically expires after TTL
- No action needed, just wait

---

### Issue 5: Slow Performance

**Symptoms**:

- Prompt generation takes >3s consistently
- No apparent caching benefit
- First-time performance similar to repeated calls

**Causes**:

1. **Large PLAN files** - >5000 lines
2. **Low cache hit rate** - <50% hits
3. **Disk I/O issues** - Slow filesystem
4. **Many glob operations** - Expensive directory scans

**Solutions**:

**1. Check cache hit rate**:

```python
from LLM.scripts.generation.plan_parser import PlanParser

parser = PlanParser()
stats = parser.parse_plan_file.cache.stats()

if stats['hit_rate'] < 80:
    print(f"⚠️  Low hit rate: {stats['hit_rate']}%")
    print(f"Expected: >80%")
    # Investigation needed
```

**2. Profile execution time**:

```python
import time

start = time.perf_counter()
# ... generate prompt ...
duration = time.perf_counter() - start

print(f"Duration: {duration*1000:.2f}ms")

if duration > 3.0:
    print("⚠️  Slow execution (>3s)")
    # Check:
    # - PLAN file size
    # - Cache statistics
    # - Disk I/O speed
```

**3. Check PLAN file size**:

```bash
# Count lines in PLAN
wc -l work-space/plans/FEATURE/PLAN_FEATURE.md

# If >5000 lines, consider splitting
# Target: <3000 lines per PLAN
```

**4. Use profiling decorator** (see `PERFORMANCE_OPTIMIZATION_GUIDE.md`):

```python
from LLM.scripts.generation.plan_parser import PlanParser
import time

# Add @profile_function decorator to functions
# See PERFORMANCE_OPTIMIZATION_GUIDE.md for details
```

**Expected Performance**:

- **First call** (cache miss): ~15ms
- **Cached calls** (cache hit): ~7ms
- **Cache hit rate**: >80%

If not meeting these targets, investigate further.

---

## Debugging with Structured Logs

### Understanding Log Format

**Structured logs** (JSON format):

```json
{
  "timestamp": "2025-11-13T12:34:56.789Z",
  "level": "INFO",
  "message": "Prompt generated",
  "plan": "FEATURE",
  "workflow": "next_achievement",
  "achievement": "2.3",
  "lines": 450
}
```

**Benefits**:

- **Searchable**: Filter by field (plan, workflow, achievement)
- **Machine-readable**: Parse with `jq` or Python
- **Context**: Includes execution context automatically

### Viewing Logs

**1. View all logs**:

```bash
python generate_prompt.py @FEATURE --next 2>&1 | tee output.log
```

**2. Filter by level**:

```bash
# Show only errors
python generate_prompt.py @FEATURE --next 2>&1 | grep '"level":"ERROR"'

# Show warnings and errors
python generate_prompt.py @FEATURE --next 2>&1 | grep -E '"level":"(ERROR|WARNING)"'
```

**3. Parse JSON logs**:

```bash
# Extract message field
python generate_prompt.py @FEATURE --next 2>&1 | jq '.message'

# Filter by plan
python generate_prompt.py @FEATURE --next 2>&1 | jq 'select(.plan=="FEATURE")'

# Extract duration
python generate_prompt.py @FEATURE --next 2>&1 | jq '.duration'
```

### Common Log Patterns

**Successful execution**:

```
INFO: Starting workflow (plan=FEATURE, workflow=next_achievement)
DEBUG: Parsing PLAN (path=work-space/plans/FEATURE/PLAN_FEATURE.md)
DEBUG: Cache hit (key=..., hit_rate=91.5%)
INFO: Detected next achievement (achievement=2.3)
INFO: Prompt generated (achievement=2.3, lines=450)
INFO: Workflow complete (duration=0.007s)
```

**Error execution**:

```
INFO: Starting workflow (plan=FEATURE, workflow=next_achievement)
DEBUG: Parsing PLAN (path=work-space/plans/FEATURE/PLAN_FEATURE.md)
ERROR: Achievement not found (achievement=9.9, available=[1.1, 1.2, ...])
```

---

## Tracing Workflow Execution

### Execution Flow

1. **main()** - Entry point, argument parsing
2. **set_log_context()** - Set context for all logs
3. **resolve_plan_path()** - Resolve @folder shortcut
4. **parse_plan_file()** - Parse PLAN (cached)
5. **detect_workflow_state()** - Check completion status
6. **generate_prompt()** - Build prompt
7. **format output** - Display result

### Tracing with Logs

**Enable DEBUG logging**:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Follow execution**:

```bash
python generate_prompt.py @FEATURE --next 2>&1 | grep -E '(Starting|Parsing|Detected|Generated|Complete)'
```

**Output**:

```
Starting workflow (plan=FEATURE)
Parsing PLAN (path=...)
Detected next achievement (achievement=2.3)
Generated prompt (lines=450)
Workflow complete (duration=0.007s)
```

---

## Identifying Bottlenecks

### Performance Profiling

**1. Add profiling decorator** (from `PERFORMANCE_OPTIMIZATION_GUIDE.md`):

```python
def profile_function(func):
    """Decorator to profile function execution time."""
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        logger.debug(f"{func.__name__} took {duration:.3f}s")
        return result
    return wrapper

@profile_function
def slow_function():
    # ... code ...
    pass
```

**2. Check logs for timing**:

```bash
python generate_prompt.py @FEATURE --next 2>&1 | grep "took"
```

**Output**:

```
parse_plan_file took 0.008s
detect_workflow_state took 0.005s
generate_prompt took 0.002s
```

**3. Identify slowest operations**:

- **PLAN parsing**: Should be <10ms (cached: <0.01ms)
- **Workflow detection**: Should be <10ms
- **Prompt generation**: Should be <5ms
- **Total**: Should be <20ms

---

## Checking Cache Statistics

### View Cache Stats

```python
from LLM.scripts/generation.plan_parser import PlanParser

parser = PlanParser()
stats = parser.parse_plan_file.cache.stats()

print(f"Cache: {stats['name']}")
print(f"Size: {stats['size']}/{stats['max_size']}")
print(f"Hits: {stats['hits']}")
print(f"Misses: {stats['misses']}")
print(f"Hit Rate: {stats['hit_rate']:.1f}%")
print(f"TTL: {stats['ttl']}s")
```

**Expected Output**:

```
Cache: plan_cache
Size: 5/50
Hits: 45
Misses: 5
Hit Rate: 90.0%
TTL: 300s
```

### Interpreting Results

**Good Cache Performance**:

- Hit rate: >80%
- Size: Growing gradually
- Misses: Few, mostly first calls

**Poor Cache Performance**:

- Hit rate: <50%
- Size: Always 0 or 1
- Misses: Most calls

**Investigate if**:

- Hit rate <80%
- Cache size always 0
- Many cache misses

---

## Viewing Metrics

### Export Prometheus Metrics

```python
from core.libraries.metrics import export_prometheus_text

metrics_text = export_prometheus_text()
print(metrics_text)
```

**Output**:

```
# HELP prompt_generation_total Total prompts generated
# TYPE prompt_generation_total counter
prompt_generation_total{workflow="next_achievement",status="success"} 50
prompt_generation_total{workflow="next_achievement",status="error"} 2

# HELP prompt_generation_duration_seconds Prompt generation duration
# TYPE prompt_generation_duration_seconds histogram
prompt_generation_duration_seconds_sum{workflow="next_achievement"} 0.750
prompt_generation_duration_seconds_count{workflow="next_achievement"} 52

# HELP plan_cache_hits_total PLAN cache hits
# TYPE plan_cache_hits_total counter
plan_cache_hits_total{cache_name="plan_cache",hit_type="hit"} 47
plan_cache_hits_total{cache_name="plan_cache",hit_type="miss"} 5
```

### Analyzing Metrics

**Success Rate**:

```
success = 50
error = 2
total = 52
success_rate = 50/52 = 96.2%  # Good!
```

**Average Duration**:

```
sum = 0.750s
count = 52
avg = 0.750/52 = 0.014s = 14ms  # Excellent!
```

**Cache Hit Rate**:

```
hits = 47
misses = 5
total = 52
hit_rate = 47/52 = 90.4%  # Excellent! (target: >80%)
```

---

## Resolution Flowcharts

### Error Resolution Process

```
┌─────────────────────┐
│   Error Occurred    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Check Error Message │ ← Color-coded, structured
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Read Suggestions   │ ← "HOW TO FIX" section
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Apply Solution    │
└──────────┬──────────┘
           │
           ├─ Yes ─→ ✅ Resolved
           │
           └─ No ──→ Check Logs / File Issue
```

### Performance Debugging Process

```
┌─────────────────────┐
│  Slow Performance   │ (>3s)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Check Cache Stats   │
└──────────┬──────────┘
           │
           ├─ Hit Rate <80% ──→ Investigate Cache
           │                    (Clear, check mtime)
           │
           ├─ Large PLAN ──────→ Split PLAN
           │                    (target: <3000 lines)
           │
           └─ Disk I/O ────────→ Check Filesystem
                                 (SSD recommended)
```

---

## Getting Additional Help

### Documentation Resources

**Guides**:

- `README.md` - Quick start and commands
- `LIBRARY_INTEGRATION_GUIDE.md` - Library patterns
- `ERROR_HANDLING_PATTERNS.md` - Error handling details
- `PERFORMANCE_OPTIMIZATION_GUIDE.md` - Performance details

**References**:

- `core/libraries/error_handling/` - Error handling library
- `core/libraries/logging/` - Logging library
- `core/libraries/caching/` - Caching library
- `core/libraries/metrics/` - Metrics library

### Reporting Issues

**Include in Report**:

1. **Command**: Exact command you ran
2. **Error**: Full error message (auto-copied to clipboard)
3. **Context**:
   - PLAN name
   - Achievement number
   - Working directory
4. **Logs**: Relevant log output
5. **Environment**:
   - Python version
   - OS
   - Disk type (HDD/SSD)

**Example Report**:

```
Command: python generate_prompt.py @FEATURE 2.1
Error: Achievement not found (see attached)
Context:
  - PLAN: PROMPT-GENERATOR-UX-AND-FOUNDATION
  - Achievement: 2.1
  - Working dir: /path/to/YoutubeRAG
Logs: (see attached output.log)
Environment:
  - Python 3.10
  - macOS 12.0
  - SSD
```

---

**Last Updated**: 2025-11-13  
**Status**: Production-Ready  
**Achievement**: 3.3 - Comprehensive User Documentation
