# Configuration Matrix

**Achievement**: 4.3 - Configuration Integration Validated  
**Date**: 2025-11-14  
**Purpose**: Quick reference for all observability configuration options

---

## Configuration Variables Overview

| Variable | Default | Type | Valid Values | Location |
|----------|---------|------|--------------|----------|
| GRAPHRAG_TRANSFORMATION_LOGGING | `"true"` | Boolean | "true", "false" (case-insensitive) | transformation_logger.py:588 |
| GRAPHRAG_SAVE_INTERMEDIATE_DATA | `"false"` | Boolean | "true", "false" (case-insensitive) | entity_resolution.py:73 |
| GRAPHRAG_QUALITY_METRICS | `"true"` | Boolean | "true", "false" (case-insensitive) | graphrag.py:137 |
| GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS | `"7"` | Integer | Any positive integer | entity_resolution.py:78 |

---

## Variable Details

### GRAPHRAG_TRANSFORMATION_LOGGING

**What It Affects**:
- Transformation logging for all pipeline stages
- Logs saved to `transformation_logs` collection
- Captures input/output data, transformations, metadata

**Valid Values**:
- `"true"` (case-insensitive): Enable logging
- `"false"` (case-insensitive): Disable logging
- Any other value: Treated as `"false"`

**Default**: `"true"` (enabled by default)

**Dependencies**: None (independent variable)

**Impact on Pipeline**:
- **Enabled**: ~2-3% performance overhead, detailed debugging capability
- **Disabled**: No overhead, no transformation logs

**Storage Impact**:
- **Enabled**: ~10-50 MB per pipeline run (depends on data size)
- **Disabled**: 0 MB

**When to Use**:
- ✅ Development: Always enable for debugging
- ✅ Staging: Enable for validation
- ⚠️ Production: Enable if debugging needed, disable for performance

---

### GRAPHRAG_SAVE_INTERMEDIATE_DATA

**What It Affects**:
- Intermediate data storage during entity resolution and graph construction
- Data saved to stage-specific collections (e.g., `entity_resolution_intermediate`)
- Enables inspection of data between transformation steps

**Valid Values**:
- `"true"` (case-insensitive): Enable intermediate data saving
- `"false"` (case-insensitive): Disable intermediate data saving
- Any other value: Treated as `"false"`

**Default**: `"false"` (disabled by default)

**Dependencies**: 
- `GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS`: Controls TTL for intermediate data (default: 7 days)

**Impact on Pipeline**:
- **Enabled**: ~5-10% performance overhead, detailed data inspection capability
- **Disabled**: No overhead, no intermediate data

**Storage Impact**:
- **Enabled**: ~50-200 MB per pipeline run (depends on data size)
- **Disabled**: 0 MB

**When to Use**:
- ✅ Development: Enable for debugging transformation issues
- ⚠️ Staging: Enable if needed for validation
- ❌ Production: Disable to save storage (enable only for debugging)

---

### GRAPHRAG_QUALITY_METRICS

**What It Affects**:
- Quality metrics calculation and storage
- Metrics saved to `quality_metrics` collection
- Tracks 23 quality metrics across all pipeline stages

**Valid Values**:
- `"true"` (case-insensitive): Enable quality metrics
- `"false"` (case-insensitive): Disable quality metrics
- Any other value: Treated as `"false"`

**Default**: `"true"` (enabled by default)

**Dependencies**: None (independent variable)

**Impact on Pipeline**:
- **Enabled**: ~3-5% performance overhead, comprehensive quality monitoring
- **Disabled**: No overhead, no quality metrics

**Storage Impact**:
- **Enabled**: ~1-5 MB per pipeline run (lightweight)
- **Disabled**: 0 MB

**When to Use**:
- ✅ Development: Always enable for quality monitoring
- ✅ Staging: Always enable for validation
- ✅ Production: Enable for monitoring (minimal overhead)

---

### GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS

**What It Affects**:
- Time-to-live (TTL) for intermediate data collections
- Automatic cleanup of old intermediate data
- Only applies when `GRAPHRAG_SAVE_INTERMEDIATE_DATA=true`

**Valid Values**:
- Any positive integer (days)
- Examples: `"1"`, `"7"`, `"30"`

**Default**: `"7"` (7 days)

**Dependencies**: 
- Only used when `GRAPHRAG_SAVE_INTERMEDIATE_DATA=true`

**Impact on Pipeline**:
- No performance impact (TTL is database-level)
- Controls storage retention

**Storage Impact**:
- Lower values: Less storage used (faster cleanup)
- Higher values: More storage used (longer retention)

**When to Use**:
- Development: 1-3 days (frequent cleanup)
- Staging: 7-14 days (validation period)
- Production: 1-7 days (if intermediate data enabled)

---

## CLI Arguments

### Experiment Mode Arguments

| Argument | Purpose | Type | Example |
|----------|---------|------|---------|
| --experiment-id | Track experiment runs | String | `--experiment-id test-001` |
| --read-db-name | Source database | String | `--read-db-name mongo_hack` |
| --write-db-name | Target database | String | `--write-db-name mongo_hack_test` |
| --db-name | General database name | String | `--db-name mongo_hack` |

**Usage**:
```bash
python business/pipelines/graphrag.py \
  --experiment-id my-test \
  --read-db-name production_db \
  --write-db-name test_db
```

**Impact**: Enables safe testing without affecting production data

---

## Configuration Dependencies

### Dependency Graph

```
GRAPHRAG_TRANSFORMATION_LOGGING (independent)
GRAPHRAG_QUALITY_METRICS (independent)
GRAPHRAG_SAVE_INTERMEDIATE_DATA (independent)
  └── GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS (dependent on SAVE_INTERMEDIATE_DATA)
```

**Key Points**:
- All 3 main variables are **independent** (no conflicts)
- `TTL_DAYS` only matters when `SAVE_INTERMEDIATE_DATA=true`
- Can enable/disable any combination without issues

---

## Performance Impact Matrix

| Configuration | Logging | Intermediate | Metrics | Total Overhead | Storage/Run |
|---------------|---------|--------------|---------|----------------|-------------|
| All Enabled | ✅ | ✅ | ✅ | ~10-15% | ~60-255 MB |
| Logging + Metrics | ✅ | ❌ | ✅ | ~5-8% | ~11-55 MB |
| Metrics Only | ❌ | ✅ | ✅ | ~8-15% | ~51-205 MB |
| Logging Only | ✅ | ❌ | ❌ | ~2-3% | ~10-50 MB |
| Metrics Only | ❌ | ❌ | ✅ | ~3-5% | ~1-5 MB |
| All Disabled | ❌ | ❌ | ❌ | ~0% | 0 MB |
| Default | ✅ | ❌ | ✅ | ~5-8% | ~11-55 MB |

**Notes**:
- Overhead percentages are estimates based on code analysis
- Storage sizes depend on data volume
- Default configuration balances observability and performance

---

## Configuration Validation Logic

### Boolean Validation Pattern

All boolean environment variables use the same validation pattern:

```python
env_value = os.getenv("VARIABLE_NAME", "default_value")
enabled = env_value.lower() == "true"
```

**Behavior**:
- Case-insensitive: "TRUE", "True", "true" all work
- Only "true" enables the feature
- Any other value (including invalid) disables the feature
- No crashes or errors for invalid values
- Silent fallback to disabled state

**Examples**:
- `"true"` → Enabled ✅
- `"TRUE"` → Enabled ✅
- `"True"` → Enabled ✅
- `"false"` → Disabled ❌
- `"FALSE"` → Disabled ❌
- `"invalid"` → Disabled ❌ (silent fallback)
- `"yes"` → Disabled ❌ (silent fallback)
- `"1"` → Disabled ❌ (silent fallback)
- `""` (empty) → Disabled ❌ (silent fallback)

---

## Quick Reference Table

### By Environment

| Environment | Logging | Intermediate | Metrics | Rationale |
|-------------|---------|--------------|---------|-----------|
| **Development** | ✅ true | ✅ true | ✅ true | Maximum observability for debugging |
| **Staging** | ✅ true | ❌ false | ✅ true | Logging + metrics, no heavy storage |
| **Production** | ❌ false | ❌ false | ✅ true | Lightweight monitoring only |
| **Debugging** | ✅ true | ✅ true | ✅ true | All features for troubleshooting |
| **Performance** | ❌ false | ❌ false | ❌ false | No overhead (legacy behavior) |

### By Use Case

| Use Case | Logging | Intermediate | Metrics | Why |
|----------|---------|--------------|---------|-----|
| **Data Quality Issues** | ✅ | ✅ | ✅ | Need all data for debugging |
| **Performance Testing** | ❌ | ❌ | ❌ | Measure baseline performance |
| **Production Monitoring** | ❌ | ❌ | ✅ | Lightweight quality tracking |
| **Development** | ✅ | ✅ | ✅ | Maximum visibility |
| **Cost Optimization** | ❌ | ❌ | ✅ | Minimal storage, basic monitoring |

---

## Configuration Examples

### Example 1: Development Environment

```bash
# .env
GRAPHRAG_TRANSFORMATION_LOGGING=true
GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
GRAPHRAG_QUALITY_METRICS=true
GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=3
```

**Result**: Maximum observability, 3-day TTL for cleanup

---

### Example 2: Production Environment

```bash
# .env
GRAPHRAG_TRANSFORMATION_LOGGING=false
GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
GRAPHRAG_QUALITY_METRICS=true
```

**Result**: Lightweight monitoring, minimal overhead

---

### Example 3: Debugging Session

```bash
# Temporary override
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
export GRAPHRAG_QUALITY_METRICS=true

# Run pipeline
python business/pipelines/graphrag.py

# Cleanup
unset GRAPHRAG_TRANSFORMATION_LOGGING
unset GRAPHRAG_SAVE_INTERMEDIATE_DATA
unset GRAPHRAG_QUALITY_METRICS
```

**Result**: Full observability for debugging, then back to defaults

---

## How to Check Current Configuration

### Method 1: Check Environment Variables

```bash
echo "Logging: $GRAPHRAG_TRANSFORMATION_LOGGING"
echo "Intermediate: $GRAPHRAG_SAVE_INTERMEDIATE_DATA"
echo "Metrics: $GRAPHRAG_QUALITY_METRICS"
echo "TTL: $GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS"
```

### Method 2: Check Pipeline Logs

```bash
# Look for these log messages at pipeline start:
# "Quality metrics collection: enabled" or "disabled"
# "Transformation logging: enabled" or "disabled"
```

### Method 3: Check MongoDB Collections

```bash
# If collections exist, features are enabled:
mongo mongo_hack --eval "db.getCollectionNames()" | grep -E "transformation_logs|quality_metrics|intermediate"
```

---

## Summary

**Total Configuration Variables**: 4
- 3 boolean toggles (independent)
- 1 integer parameter (dependent on intermediate data)

**Total CLI Arguments**: 4
- All for experiment mode and database isolation

**Key Characteristics**:
- ✅ Independent variables (no conflicts)
- ✅ Graceful invalid value handling
- ✅ Sensible defaults
- ✅ Flexible configuration per environment
- ✅ Clear performance/storage tradeoffs

**Recommended Approach**:
1. Start with defaults (logging + metrics enabled)
2. Adjust based on environment needs
3. Enable intermediate data only for debugging
4. Monitor storage and performance impact
5. Optimize configuration over time

---

**Last Updated**: 2025-11-14  
**Related Documents**: 
- Configuration-Validation-Report.md
- Recommended-Configurations.md
- Configuration-Troubleshooting-Guide.md


