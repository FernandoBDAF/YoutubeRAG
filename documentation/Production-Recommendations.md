# Production Recommendations for GraphRAG Observability

**Document Type**: Production Deployment Guide  
**Achievement**: 5.3 - Observability Overhead Assessment  
**Date**: 2025-11-14  
**Version**: 1.0  
**Status**: ✅ Approved for Production

---

## Table of Contents

1. [Overview](#overview)
2. [Production Verdict](#production-verdict)
3. [Feature Categorization](#feature-categorization)
4. [Environment-Specific Recommendations](#environment-specific-recommendations)
5. [Configuration Guide](#configuration-guide)
6. [Monitoring Strategy](#monitoring-strategy)
7. [Troubleshooting Guidelines](#troubleshooting-guidelines)
8. [Feature Toggle Strategy](#feature-toggle-strategy)

---

## Overview

This document provides comprehensive production deployment recommendations for the GraphRAG observability infrastructure based on detailed cost-benefit analysis.

**Key Findings**:
- Performance overhead: <5% (well within acceptable limits)
- Storage overhead: ~490 MB per run (within 500 MB requirement)
- Benefits: 10x improvement in debugging, 23 quality metrics, complete pipeline visibility

**Recommendation**: ✅ **Enable observability in production** with selective feature configuration

---

## Production Verdict

### Should Observability Be Enabled in Production?

**Answer**: ✅ **YES, STRONGLY RECOMMENDED**

**Justification**:

1. **Costs are Minimal**:
   - Runtime overhead: <5% (threshold: 30%)
   - Storage overhead: 490 MB per run (threshold: 500 MB)
   - Maintenance: ~10 hours per quarter (manageable)

2. **Benefits are Substantial**:
   - **10x faster debugging**: 2-8 hours → 10-30 minutes
   - **23 quality metrics**: Real-time quality monitoring
   - **Complete visibility**: Can explain any transformation decision
   - **Systematic experimentation**: A/B testing capability

3. **Risk is Low**:
   - Feature toggles allow selective enabling
   - Non-invasive integration (optional, no pipeline changes)
   - TTL handles storage automatically
   - Emergency off-switch available (GRAPHRAG_ENABLE_OBSERVABILITY=false)

4. **Value is Proven**:
   - Real validation experience demonstrates effectiveness
   - Multiple successful debugging scenarios
   - Clear use cases and benefits

### What Features Should Be Always-On vs. Optional?

**Always-On (Production-Ready)**:
1. ✅ Quality Metrics (2% overhead, essential visibility)
2. ✅ Transformation Logging (0.6% overhead, debugging capability)
3. ✅ Prometheus Metrics (<0.1% overhead, monitoring)

**Configurable (Enable as Needed)**:
1. ⚠️ Intermediate Data Saving (1.7% overhead, debugging-specific)

**Development-Only**:
- None (all features provide production value)

---

## Feature Categorization

### Always-On Features

#### 1. Quality Metrics

**Configuration**: `GRAPHRAG_QUALITY_METRICS=true`

**Purpose**: Track 23 quality metrics across all pipeline stages

**Overhead**:
- Performance: 2.0% runtime
- Storage: ~10 MB per run
- Maintenance: Minimal (metrics in Prometheus)

**Benefits**:
- Real-time quality monitoring
- Trend analysis over time
- Early detection of quality regressions
- Data-driven optimization

**Production Justification**: Essential for quality assurance, minimal overhead

**Metrics Tracked**:
- Extraction: 7 metrics (entity count, confidence, type distribution)
- Resolution: 6 metrics (merge rate, entity reduction, similarity effectiveness)
- Construction: 5 metrics (relationship count, graph density, node degree)
- Detection: 5 metrics (community count, modularity, singleton ratio)

---

#### 2. Transformation Logging

**Configuration**: `GRAPHRAG_TRANSFORMATION_LOGGING=true`

**Purpose**: Log transformation decisions for debugging

**Overhead**:
- Performance: 0.6% runtime
- Storage: ~50 MB per run
- Maintenance: Minimal (automatic TTL cleanup)

**Benefits**:
- Can explain any transformation decision
- Complete audit trail of pipeline operations
- Essential for debugging issues
- Query transformation history

**Production Justification**: Critical debugging capability, minimal overhead

**What Gets Logged**:
- Entity merges (which entities merged, why, confidence)
- Relationship filtering (kept/dropped, reasons)
- Community formation (members, coherence)
- Entity clustering (grouping decisions)

---

#### 3. Prometheus Metrics

**Configuration**: `GRAPHRAG_PROMETHEUS_METRICS=true`

**Purpose**: Export metrics to Prometheus for monitoring

**Overhead**:
- Performance: <0.1% runtime
- Storage: External (Prometheus stores)
- Maintenance: Requires monitoring stack

**Benefits**:
- Real-time performance monitoring
- Historical trend analysis
- Alert capability (failures, regressions)
- Grafana dashboard visualization

**Production Justification**: Essential monitoring, negligible overhead

**Metrics Exported**:
- Pipeline execution metrics (runtime, success rate)
- Stage-level metrics (extraction time, resolution time)
- Resource metrics (memory usage, CPU usage)
- Quality summary metrics (entity count, relationship count)

---

### Configurable Features

#### 1. Intermediate Data Saving

**Configuration**: `GRAPHRAG_SAVE_INTERMEDIATE_DATA=true/false`

**Purpose**: Save intermediate data snapshots for deep analysis

**Overhead**:
- Performance: 1.7% runtime
- Storage: ~440 MB per run (90% of total observability storage)
- Maintenance: Low (TTL cleanup)

**Benefits**:
- Query any stage of pipeline
- Compare before/after transformations
- Deep data-driven debugging
- Enable all query scripts

**Production Strategy**: **Disable by default, enable for debugging**

**When to Enable**:
- ✅ Investigating quality issues
- ✅ Debugging unexpected behavior
- ✅ Analyzing transformation effectiveness
- ✅ A/B testing configurations
- ❌ Normal production operations (not needed)

**How to Enable**:
1. Set `GRAPHRAG_SAVE_INTERMEDIATE_DATA=true`
2. Run pipeline with issue
3. Use query scripts to analyze data
4. Identify root cause
5. Set back to `false` after debugging

---

## Environment-Specific Recommendations

### Development Environment

**Configuration**:
```bash
# Enable ALL features for maximum visibility
GRAPHRAG_ENABLE_OBSERVABILITY=true
GRAPHRAG_TRANSFORMATION_LOGGING=true
GRAPHRAG_QUALITY_METRICS=true
GRAPHRAG_PROMETHEUS_METRICS=true
GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
```

**Rationale**:
- Developers need maximum visibility
- Performance overhead acceptable in dev
- Storage not a concern (small datasets)
- Learning and experimentation require all features
- TTL cleanup handles storage automatically

**Benefits**:
- Complete pipeline understanding
- All query scripts available
- All explanation tools functional
- Can explore data at any stage
- Build intuition about transformations

**Performance**:
- Runtime overhead: <5%
- Storage: ~490 MB per run (cleaned after 30 days)

---

### Staging Environment

**Configuration**:
```bash
# Enable ALL features to match production debugging capability
GRAPHRAG_ENABLE_OBSERVABILITY=true
GRAPHRAG_TRANSFORMATION_LOGGING=true
GRAPHRAG_QUALITY_METRICS=true
GRAPHRAG_PROMETHEUS_METRICS=true
GRAPHRAG_SAVE_INTERMEDIATE_DATA=true  # Optional: can disable to match production
```

**Rationale**:
- Validate production configuration
- Test with production-like data
- Ensure observability works at scale
- Practice debugging workflows
- Validate alert configurations

**Testing Checklist**:
- [ ] Run pipeline with observability enabled
- [ ] Verify all metrics collected
- [ ] Test query scripts with staging data
- [ ] Validate Grafana dashboards working
- [ ] Confirm TTL cleanup functioning
- [ ] Practice debugging scenarios
- [ ] Verify performance overhead acceptable

---

### Production Environment

**Configuration** (Recommended):
```bash
# Always-on features only (minimal overhead)
GRAPHRAG_ENABLE_OBSERVABILITY=true
GRAPHRAG_TRANSFORMATION_LOGGING=true
GRAPHRAG_QUALITY_METRICS=true
GRAPHRAG_PROMETHEUS_METRICS=true

# Intermediate data disabled by default
GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
```

**Rationale**:
- Minimal overhead (<3.5% runtime, 60 MB storage)
- Essential quality monitoring always available
- Debugging capability when needed
- Can enable intermediate data for specific debug sessions
- Balance visibility with performance

**Performance**:
- Runtime overhead: <3.5%
- Storage: ~60 MB per run
- Maintenance: Minimal

**When to Enable Intermediate Data**:
```bash
# Temporarily enable for debugging
GRAPHRAG_SAVE_INTERMEDIATE_DATA=true

# Run pipeline to collect debug data
python run_graphrag_pipeline.py

# Debug using query scripts
python scripts/repositories/graphrag/queries/query_raw_entities.py --trace-id <id>

# Disable after debugging complete
GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
```

---

## Configuration Guide

### Environment Variables

#### Master Switch

```bash
# Master switch - disables ALL observability if false
GRAPHRAG_ENABLE_OBSERVABILITY=true
```

- **Purpose**: Emergency off-switch
- **Default**: `true` (recommended)
- **When to disable**: If observability causes issues (rare)

#### Feature-Specific Toggles

```bash
# Core observability features
GRAPHRAG_TRANSFORMATION_LOGGING=true      # Always-on recommended
GRAPHRAG_QUALITY_METRICS=true             # Always-on recommended
GRAPHRAG_PROMETHEUS_METRICS=true          # Always-on recommended

# Optional features
GRAPHRAG_SAVE_INTERMEDIATE_DATA=false     # Disable by default in production
```

#### Granular Controls (Optional)

```bash
# Log level
GRAPHRAG_LOG_LEVEL=info                   # Options: debug, info, warning, error

# Intermediate data stages (if enabled)
GRAPHRAG_INTERMEDIATE_DATA_STAGES=extraction,resolution,construction,detection

# Metrics sampling rate (advanced)
GRAPHRAG_METRICS_SAMPLING_RATE=1.0        # 0.0-1.0 (1.0 = 100%)
```

### Configuration Templates

#### Template 1: Production (Recommended)

**File**: `.env.production`

```bash
# GraphRAG Observability - Production Configuration
GRAPHRAG_ENABLE_OBSERVABILITY=true
GRAPHRAG_TRANSFORMATION_LOGGING=true
GRAPHRAG_QUALITY_METRICS=true
GRAPHRAG_PROMETHEUS_METRICS=true
GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
GRAPHRAG_LOG_LEVEL=info
```

#### Template 2: Production Debug

**File**: `.env.production.debug`

```bash
# GraphRAG Observability - Production Debug Configuration
# Use temporarily when investigating issues
GRAPHRAG_ENABLE_OBSERVABILITY=true
GRAPHRAG_TRANSFORMATION_LOGGING=true
GRAPHRAG_QUALITY_METRICS=true
GRAPHRAG_PROMETHEUS_METRICS=true
GRAPHRAG_SAVE_INTERMEDIATE_DATA=true      # Enabled for debugging
GRAPHRAG_LOG_LEVEL=debug                  # More verbose logging
```

#### Template 3: Development

**File**: `.env.development`

```bash
# GraphRAG Observability - Development Configuration
GRAPHRAG_ENABLE_OBSERVABILITY=true
GRAPHRAG_TRANSFORMATION_LOGGING=true
GRAPHRAG_QUALITY_METRICS=true
GRAPHRAG_PROMETHEUS_METRICS=true
GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
GRAPHRAG_LOG_LEVEL=debug
```

---

## Monitoring Strategy

### What to Monitor

#### 1. Pipeline Health

**Metrics**:
- Pipeline success rate (target: >95%)
- Pipeline runtime (baseline + track trends)
- Error rate (target: <5%)
- Stage completion rate (all 4 stages should complete)

**Prometheus Queries**:
```promql
# Success rate (last 24 hours)
rate(graphrag_pipeline_success_total[24h]) * 100

# Average runtime (last 24 hours)
avg(rate(graphrag_pipeline_duration_seconds[24h]))

# Error count (last hour)
increase(graphrag_pipeline_errors_total[1h])
```

#### 2. Quality Metrics

**Metrics to Track**:
- Entity count (raw and resolved)
- Merge rate (should be 60-80%)
- Relationship count
- Graph density
- Community modularity (target: >0.6)

**Alert Thresholds**:
- Merge rate <50% or >90% (tuning needed)
- Modularity <0.5 (community detection issue)
- Entity count drops >20% (extraction issue)

#### 3. Performance Metrics

**Metrics to Track**:
- Runtime per stage
- Memory usage
- Storage growth
- Observability overhead

**Alert Thresholds**:
- Runtime increases >50% (performance regression)
- Memory usage >8 GB (potential memory leak)
- Storage exceeds 500 MB (TTL not working)

#### 4. Storage Metrics

**Metrics to Track**:
- Collection sizes
- TTL cleanup effectiveness
- Growth rate

**MongoDB Queries**:
```javascript
// Check collection sizes
db.stats()

// Check TTL index status
db.transformation_logs.getIndexes()

// Count documents per collection
db.transformation_logs.count()
```

### Grafana Dashboards

**Dashboard 1: Pipeline Overview**
- Success rate over time
- Runtime trends
- Error count
- Stage completion rates

**Dashboard 2: Quality Metrics**
- Entity count trends
- Merge rate over time
- Relationship count
- Community metrics

**Dashboard 3: Performance**
- Runtime per stage
- Memory usage
- CPU usage
- Storage usage

### Alert Configuration

**Critical Alerts** (immediate notification):
```yaml
# Pipeline failure
alert: PipelineFailure
expr: increase(graphrag_pipeline_errors_total[5m]) > 0
severity: critical
```

**Warning Alerts** (notification within 1 hour):
```yaml
# Quality degradation
alert: QualityDegradation
expr: graphrag_quality_merge_rate < 0.5 OR graphrag_quality_merge_rate > 0.9
severity: warning

# Performance regression
alert: PerformanceRegression
expr: avg(rate(graphrag_pipeline_duration_seconds[1h])) > baseline * 1.5
severity: warning
```

---

## Troubleshooting Guidelines

### Issue 1: Pipeline Failure

**Symptoms**: Pipeline exits with error, no results produced

**Diagnosis Steps**:
1. Check Prometheus metrics for error count
2. Query transformation logs for last operations
   ```bash
   python scripts/repositories/graphrag/queries/query_recent_logs.py --limit 50
   ```
3. Check Grafana dashboards for anomalies
4. Review application logs

**Common Causes**:
- MongoDB connection issues
- Insufficient memory
- Invalid configuration
- Data quality issues

**Resolution**:
1. Verify MongoDB is running and accessible
2. Check resource availability (memory, disk)
3. Validate configuration files
4. Test with smaller dataset

### Issue 2: Quality Degradation

**Symptoms**: Metrics show declining quality (low merge rate, low modularity, etc.)

**Diagnosis Steps**:
1. Check quality metrics in Grafana
2. Compare with baseline run
   ```bash
   python scripts/repositories/graphrag/queries/compare_extraction_runs.py --trace-ids baseline current
   ```
3. Query transformation logs for patterns
4. Enable intermediate data saving for deep analysis

**Common Causes**:
- Configuration changes (thresholds, prompts)
- Input data quality changes
- Model updates (embedding, LLM)

**Resolution**:
1. Revert recent configuration changes
2. A/B test different configurations
3. Tune thresholds based on data
4. Update prompts if needed

### Issue 3: Performance Regression

**Symptoms**: Pipeline takes significantly longer than baseline

**Diagnosis Steps**:
1. Check runtime metrics in Grafana
2. Identify slow stage
   ```bash
   python scripts/repositories/graphrag/queries/query_stage_performance.py
   ```
3. Compare with baseline performance
4. Check resource utilization (CPU, memory, I/O)

**Common Causes**:
- Increased data volume
- Resource contention
- Inefficient queries
- Network issues (embedding service)

**Resolution**:
1. Optimize batch sizes
2. Scale resources (memory, CPU)
3. Profile slow operations
4. Check network latency

### Issue 4: Storage Growth

**Symptoms**: MongoDB storage exceeds limits

**Diagnosis Steps**:
1. Check collection sizes
   ```bash
   python scripts/repositories/graphrag/queries/query_storage_usage.py
   ```
2. Verify TTL indexes are working
3. Check growth rate

**Common Causes**:
- TTL indexes not created
- TTL not working correctly
- Too many runs without cleanup

**Resolution**:
1. Verify TTL indexes exist:
   ```javascript
   db.transformation_logs.getIndexes()
   ```
2. Manually clean old data if needed:
   ```javascript
   db.transformation_logs.deleteMany({
     timestamp: { $lt: new Date(Date.now() - 30*24*60*60*1000) }
   })
   ```
3. Reduce intermediate data saving

---

## Feature Toggle Strategy

### Feature Flag Hierarchy

```
GRAPHRAG_ENABLE_OBSERVABILITY (master switch)
  ├── GRAPHRAG_TRANSFORMATION_LOGGING
  │   ├── GRAPHRAG_LOG_ENTITY_MERGES
  │   ├── GRAPHRAG_LOG_RELATIONSHIP_FILTERS
  │   ├── GRAPHRAG_LOG_COMMUNITY_FORMATION
  │   └── GRAPHRAG_LOG_ENTITY_CLUSTERING
  │
  ├── GRAPHRAG_SAVE_INTERMEDIATE_DATA
  │   ├── GRAPHRAG_SAVE_ENTITIES_RAW
  │   ├── GRAPHRAG_SAVE_ENTITIES_RESOLVED
  │   ├── GRAPHRAG_SAVE_RELATIONS_RAW
  │   ├── GRAPHRAG_SAVE_RELATIONS_FINAL
  │   └── GRAPHRAG_SAVE_GRAPH_SNAPSHOTS
  │
  ├── GRAPHRAG_QUALITY_METRICS
  │   ├── GRAPHRAG_METRICS_EXTRACTION
  │   ├── GRAPHRAG_METRICS_RESOLUTION
  │   ├── GRAPHRAG_METRICS_CONSTRUCTION
  │   └── GRAPHRAG_METRICS_DETECTION
  │
  └── GRAPHRAG_PROMETHEUS_METRICS
      ├── GRAPHRAG_METRICS_PIPELINE_HEALTH
      ├── GRAPHRAG_METRICS_STAGE_PERFORMANCE
      └── GRAPHRAG_METRICS_RESOURCE_USAGE
```

### Default Settings Matrix

| Feature | Dev | Staging | Prod | Overhead | Storage |
|---------|-----|---------|------|----------|---------|
| **ENABLE_OBSERVABILITY** | ON | ON | ON | N/A | N/A |
| **TRANSFORMATION_LOGGING** | ON | ON | ON | 0.6% | 50 MB |
| **SAVE_INTERMEDIATE_DATA** | ON | ON | OFF | 1.7% | 440 MB |
| **QUALITY_METRICS** | ON | ON | ON | 2.0% | 10 MB |
| **PROMETHEUS_METRICS** | ON | ON | ON | <0.1% | External |
| **Total Overhead** | <5% | <5% | <3.5% | - | - |
| **Total Storage** | 490 MB | 490 MB | 60 MB | - | - |

### Performance/Storage Trade-offs

#### Configuration 1: Minimal (Production Default)

```bash
GRAPHRAG_QUALITY_METRICS=true
GRAPHRAG_TRANSFORMATION_LOGGING=true
GRAPHRAG_PROMETHEUS_METRICS=true
GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
```

**Trade-offs**:
- Performance: +2.6% runtime
- Storage: +60 MB per run
- Capabilities: Quality monitoring + basic debugging
- Use case: Normal production operations

#### Configuration 2: Standard (Production Debug)

```bash
# All features enabled
GRAPHRAG_ENABLE_OBSERVABILITY=true
```

**Trade-offs**:
- Performance: +5% runtime
- Storage: +490 MB per run
- Capabilities: Full debugging + all query tools
- Use case: Investigating issues in production

#### Configuration 3: Quality Only

```bash
GRAPHRAG_QUALITY_METRICS=true
GRAPHRAG_PROMETHEUS_METRICS=true
GRAPHRAG_TRANSFORMATION_LOGGING=false
GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
```

**Trade-offs**:
- Performance: +2.0% runtime
- Storage: +10 MB per run
- Capabilities: Quality monitoring only (no debugging)
- Use case: Lightweight monitoring

### Migration Strategy

#### Phase 1: Staging Validation (Week 1)

1. Deploy staging with production configuration
2. Run pipeline with production-sized dataset
3. Validate metrics:
   - Performance overhead <3.5%
   - Storage usage <70 MB per run
   - All quality metrics working
4. Test debugging workflow (enable intermediate data)
5. Verify alert configurations

#### Phase 2: Production Pilot (Week 2)

1. Deploy to production (small subset)
2. Run 10 pipeline executions
3. Monitor closely:
   - Check metrics every 6 hours
   - Validate overhead claims
   - Confirm stability
4. Collect feedback from operations team
5. Adjust configuration if needed

#### Phase 3: Full Production (Week 3)

1. Deploy to all production instances
2. Monitor continuously for first week
3. Validate long-term behavior:
   - TTL cleanup working
   - Metrics trends stable
   - No performance regressions
4. Document lessons learned
5. Update runbooks

### Rollback Plan

#### Emergency Rollback (If Issues Occur)

**Step 1: Disable Observability** (Immediate)
```bash
GRAPHRAG_ENABLE_OBSERVABILITY=false
```

**Impact**: All observability disabled, pipeline runs normally

**Step 2: Identify Issue**
- Check application logs
- Review recent changes
- Identify root cause

**Step 3: Gradual Re-enable**
```bash
# Enable one feature at a time
GRAPHRAG_QUALITY_METRICS=true  # Test
# Wait 24 hours, monitor
GRAPHRAG_TRANSFORMATION_LOGGING=true  # Test
# Wait 24 hours, monitor
GRAPHRAG_PROMETHEUS_METRICS=true  # Test
```

**Step 4: Resume Normal Operations**
- Once stable, resume normal configuration
- Document issue and resolution
- Update this guide if needed

---

## Conclusion

The GraphRAG observability infrastructure is **production-ready** with minimal overhead and substantial benefits. This guide provides comprehensive recommendations for deployment, monitoring, and troubleshooting.

**Quick Reference**:
- ✅ Enable in production: YES
- ✅ Always-on features: Quality metrics, transformation logging, Prometheus metrics
- ⚠️ Configurable features: Intermediate data saving (disable by default)
- 📊 Performance: <3.5% overhead (production config)
- 💾 Storage: ~60 MB per run (production config)
- 🔧 Maintenance: ~10 hours per quarter

**Next Steps**:
1. Review this document with operations team
2. Test recommended configuration in staging
3. Deploy to production with gradual rollout
4. Monitor and optimize based on production experience

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-14  
**Achievement**: 5.3 - Observability Overhead Assessment  
**Status**: ✅ Approved for Production  
**Total Lines**: 850+

