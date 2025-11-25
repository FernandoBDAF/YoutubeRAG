# Recommended Configurations

**Achievement**: 4.3 - Configuration Integration Validated  
**Date**: 2025-11-14  
**Purpose**: Environment-specific configuration recommendations for GraphRAG observability

---

## Overview

This guide provides recommended configurations for different environments and use cases. Each configuration is optimized for specific goals: development velocity, production performance, debugging capability, or cost optimization.

---

## Configuration by Environment

### 1. Development Environment

**Goal**: Maximum observability for debugging and development

**Configuration**:
```bash
# .env
GRAPHRAG_TRANSFORMATION_LOGGING=true
GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
GRAPHRAG_QUALITY_METRICS=true
GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=3
```

**Characteristics**:
- ✅ All observability features enabled
- ✅ Short TTL (3 days) for frequent cleanup
- ✅ Maximum debugging capability
- ⚠️ Higher storage usage (~60-255 MB per run)
- ⚠️ ~10-15% performance overhead

**When to Use**:
- Local development
- Feature development
- Bug investigation
- Data quality analysis

**Storage Management**:
- 3-day TTL keeps storage manageable
- Manual cleanup if needed: `db.dropDatabase("mongo_hack_dev")`

---

### 2. Staging Environment

**Goal**: Validation and testing with balanced observability

**Configuration**:
```bash
# .env
GRAPHRAG_TRANSFORMATION_LOGGING=true
GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
GRAPHRAG_QUALITY_METRICS=true
GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=7
```

**Characteristics**:
- ✅ Logging enabled for debugging
- ✅ Metrics enabled for validation
- ❌ Intermediate data disabled (save storage)
- ✅ Moderate storage usage (~11-55 MB per run)
- ⚠️ ~5-8% performance overhead

**When to Use**:
- Pre-production testing
- Integration testing
- Performance validation
- User acceptance testing

**Why This Configuration**:
- Logs provide debugging capability
- Metrics validate quality
- No intermediate data saves storage
- Close to production performance

---

### 3. Production Environment

**Goal**: Lightweight monitoring with minimal overhead

**Configuration**:
```bash
# .env
GRAPHRAG_TRANSFORMATION_LOGGING=false
GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
GRAPHRAG_QUALITY_METRICS=true
```

**Characteristics**:
- ❌ Logging disabled (reduce overhead)
- ❌ Intermediate data disabled (save storage)
- ✅ Metrics enabled (quality monitoring)
- ✅ Minimal storage usage (~1-5 MB per run)
- ✅ Low performance overhead (~3-5%)

**When to Use**:
- Production workloads
- Cost-sensitive environments
- High-volume processing
- Performance-critical applications

**Why This Configuration**:
- Metrics provide quality visibility
- Minimal overhead maintains performance
- Low storage costs
- Can enable logging temporarily if issues arise

**Temporary Debugging**:
```bash
# Enable logging temporarily for debugging
export GRAPHRAG_TRANSFORMATION_LOGGING=true
python business/pipelines/graphrag.py

# Disable after debugging
unset GRAPHRAG_TRANSFORMATION_LOGGING
```

---

### 4. Debugging Configuration

**Goal**: Maximum observability for troubleshooting issues

**Configuration**:
```bash
# .env
GRAPHRAG_TRANSFORMATION_LOGGING=true
GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
GRAPHRAG_QUALITY_METRICS=true
GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=1

# Experiment mode for isolation
--experiment-id debug-session-001
--read-db-name mongo_hack
--write-db-name mongo_hack_debug
```

**Characteristics**:
- ✅ All observability features enabled
- ✅ Database isolation (safe testing)
- ✅ Short TTL (1 day) for quick cleanup
- ✅ Maximum debugging capability
- ⚠️ Highest storage usage
- ⚠️ ~10-15% performance overhead

**When to Use**:
- Investigating production issues
- Reproducing bugs
- Data quality problems
- Performance analysis

**Complete Example**:
```bash
# Set environment variables
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
export GRAPHRAG_QUALITY_METRICS=true
export GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=1

# Run with experiment mode
python business/pipelines/graphrag.py \
  --experiment-id debug-$(date +%Y%m%d-%H%M%S) \
  --read-db-name mongo_hack \
  --write-db-name mongo_hack_debug \
  --video-id problematic-video-id

# After debugging, cleanup
mongo mongo_hack_debug --eval "db.dropDatabase()"
```

---

### 5. Performance Testing Configuration

**Goal**: Measure baseline performance without observability overhead

**Configuration**:
```bash
# .env
GRAPHRAG_TRANSFORMATION_LOGGING=false
GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
GRAPHRAG_QUALITY_METRICS=false
```

**Characteristics**:
- ❌ All observability disabled
- ✅ Zero observability overhead
- ✅ Zero storage usage
- ✅ Legacy behavior (pre-observability)

**When to Use**:
- Performance benchmarking
- Baseline measurements
- Comparing with/without observability
- Maximum performance requirements

**Comparison Testing**:
```bash
# Test 1: No observability (baseline)
export GRAPHRAG_TRANSFORMATION_LOGGING=false
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
export GRAPHRAG_QUALITY_METRICS=false
time python business/pipelines/graphrag.py

# Test 2: With observability
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
export GRAPHRAG_QUALITY_METRICS=true
time python business/pipelines/graphrag.py

# Compare execution times
```

---

## Configuration by Use Case

### Use Case 1: Data Quality Investigation

**Scenario**: Entity resolution producing unexpected results

**Configuration**:
```bash
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
export GRAPHRAG_QUALITY_METRICS=true
export GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=7
```

**Why**:
- Logs show transformation steps
- Intermediate data reveals entity states
- Metrics quantify quality issues

**Investigation Steps**:
1. Run pipeline with full observability
2. Query intermediate data: `python scripts/repositories/graphrag/queries/compare_before_after_resolution.py`
3. Check quality metrics: `python scripts/repositories/graphrag/queries/quality_metrics_by_stage.py`
4. Review transformation logs for errors

---

### Use Case 2: Production Monitoring

**Scenario**: Monitor pipeline quality in production

**Configuration**:
```bash
export GRAPHRAG_TRANSFORMATION_LOGGING=false
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
export GRAPHRAG_QUALITY_METRICS=true
```

**Why**:
- Metrics provide quality visibility
- Minimal overhead (~3-5%)
- Low storage costs
- Can alert on quality degradation

**Monitoring Approach**:
1. Run pipeline with metrics enabled
2. Query metrics regularly: `python scripts/repositories/graphrag/queries/quality_metrics_summary.py`
3. Set up alerts for quality thresholds
4. Enable logging if issues detected

---

### Use Case 3: Cost Optimization

**Scenario**: Reduce storage and compute costs

**Configuration**:
```bash
export GRAPHRAG_TRANSFORMATION_LOGGING=false
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
export GRAPHRAG_QUALITY_METRICS=true
GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=1  # If ever enabled
```

**Why**:
- Minimal storage usage
- Low compute overhead
- Basic quality monitoring maintained

**Cost Savings**:
- Storage: ~60-250 MB saved per run
- Compute: ~7-12% performance improvement
- Still maintains quality visibility

---

### Use Case 4: Experiment Testing

**Scenario**: Test changes without affecting production

**Configuration**:
```bash
# Full observability + database isolation
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
export GRAPHRAG_QUALITY_METRICS=true

python business/pipelines/graphrag.py \
  --experiment-id experiment-name \
  --read-db-name mongo_hack \
  --write-db-name mongo_hack_experiment
```

**Why**:
- Database isolation protects production
- Full observability for comparison
- Experiment ID tracks test runs

**Comparison Workflow**:
```bash
# Run baseline (production config)
python business/pipelines/graphrag.py \
  --experiment-id baseline \
  --read-db-name mongo_hack \
  --write-db-name mongo_hack_baseline

# Run experiment (modified config)
python business/pipelines/graphrag.py \
  --experiment-id modified \
  --read-db-name mongo_hack \
  --write-db-name mongo_hack_modified

# Compare results
python scripts/repositories/graphrag/queries/compare_experiments.py \
  --experiment-1 baseline \
  --experiment-2 modified
```

---

## Configuration Migration Guide

### From No Observability to Full Observability

**Step 1: Start with Metrics Only**
```bash
# Minimal impact, maximum value
export GRAPHRAG_QUALITY_METRICS=true
```

**Step 2: Add Logging (if needed)**
```bash
# For debugging capability
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_QUALITY_METRICS=true
```

**Step 3: Add Intermediate Data (if needed)**
```bash
# For deep debugging
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
export GRAPHRAG_QUALITY_METRICS=true
export GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=7
```

---

### From Full Observability to Production

**Step 1: Disable Intermediate Data**
```bash
# Save storage
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
export GRAPHRAG_QUALITY_METRICS=true
```

**Step 2: Disable Logging**
```bash
# Reduce overhead
export GRAPHRAG_TRANSFORMATION_LOGGING=false
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
export GRAPHRAG_QUALITY_METRICS=true
```

**Step 3: Monitor and Adjust**
- Monitor quality metrics
- Enable logging if issues arise
- Optimize based on needs

---

## Environment Variable Templates

### Template 1: .env.development
```bash
# Development Environment
# Maximum observability for debugging

GRAPHRAG_TRANSFORMATION_LOGGING=true
GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
GRAPHRAG_QUALITY_METRICS=true
GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=3

# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=mongo_hack_dev
```

---

### Template 2: .env.staging
```bash
# Staging Environment
# Balanced observability for validation

GRAPHRAG_TRANSFORMATION_LOGGING=true
GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
GRAPHRAG_QUALITY_METRICS=true
GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=7

# MongoDB
MONGO_URI=mongodb://staging-server:27017
MONGO_DB_NAME=mongo_hack_staging
```

---

### Template 3: .env.production
```bash
# Production Environment
# Lightweight monitoring with minimal overhead

GRAPHRAG_TRANSFORMATION_LOGGING=false
GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
GRAPHRAG_QUALITY_METRICS=true

# MongoDB
MONGO_URI=mongodb://production-server:27017
MONGO_DB_NAME=mongo_hack
```

---

### Template 4: .env.debug
```bash
# Debugging Configuration
# Maximum observability for troubleshooting

GRAPHRAG_TRANSFORMATION_LOGGING=true
GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
GRAPHRAG_QUALITY_METRICS=true
GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=1

# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=mongo_hack_debug
```

---

## Quick Decision Matrix

### Choose Configuration Based On:

| Priority | Configuration | Logging | Intermediate | Metrics |
|----------|---------------|---------|--------------|---------|
| **Debugging** | Development | ✅ | ✅ | ✅ |
| **Validation** | Staging | ✅ | ❌ | ✅ |
| **Performance** | Production | ❌ | ❌ | ✅ |
| **Cost** | Minimal | ❌ | ❌ | ✅ |
| **Baseline** | None | ❌ | ❌ | ❌ |

### Decision Tree

```
Need debugging capability?
├─ Yes → Enable TRANSFORMATION_LOGGING
└─ No → Disable TRANSFORMATION_LOGGING

Need to inspect intermediate data?
├─ Yes → Enable SAVE_INTERMEDIATE_DATA (set short TTL)
└─ No → Disable SAVE_INTERMEDIATE_DATA

Need quality monitoring?
├─ Yes → Enable QUALITY_METRICS (recommended)
└─ No → Disable QUALITY_METRICS

Cost sensitive?
├─ Yes → Disable TRANSFORMATION_LOGGING and SAVE_INTERMEDIATE_DATA
└─ No → Enable based on needs
```

---

## Summary

**Key Recommendations**:

1. **Start Simple**: Begin with metrics only (`QUALITY_METRICS=true`)
2. **Add as Needed**: Enable logging/intermediate data when debugging
3. **Environment-Specific**: Use different configs for dev/staging/prod
4. **Monitor Impact**: Track storage and performance overhead
5. **Optimize Over Time**: Adjust based on actual usage patterns

**Default Recommendation**: Staging configuration (logging + metrics, no intermediate data)
- Good balance of observability and performance
- Suitable for most use cases
- Easy to adjust up or down

---

**Last Updated**: 2025-11-14  
**Related Documents**:
- Configuration-Matrix.md
- Configuration-Validation-Report.md
- Configuration-Troubleshooting-Guide.md


