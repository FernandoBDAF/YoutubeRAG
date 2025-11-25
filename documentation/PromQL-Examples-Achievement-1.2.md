# PromQL Query Examples - Achievement 1.2

**Achievement**: 1.2 - Metrics Endpoint Validated  
**Date**: November 12, 2025  
**Validated In**: Prometheus UI at http://localhost:9090/query  
**Status**: ✅ TESTED & WORKING  
**Location**: documentation/

---

## Overview

This document contains **5 tested PromQL queries** executed and validated in the Prometheus Query interface. All queries return successful results and demonstrate the operational metrics endpoint.

---

## Tested Queries

### Query 1: Basic System Health Check

**Query**:

```promql
up
```

**Description**: Check the health status of all targets (Prometheus + Metrics Server). Returns 1 if UP, 0 if DOWN.

**Expected Result**: 2 series (one for Prometheus itself, one for your metrics server)

**Actual Result**: ✅ SUCCESS

```
up{environment="development", instance="host.docker.internal:9091", job="youtuberag", service="youtuberag"} = 1
up{instance="localhost:9090", job="prometheus"} = 1
```

**Load Time**: 9ms  
**Performance**: Excellent ✅

**Interpretation**:

- Your metrics server (youtuberag) is UP and healthy
- Prometheus is UP and monitoring itself
- Both targets responding correctly

**Use Case**: Quick health check of all monitoring targets

---

### Query 2: Error Count by Service

**Query**:

```promql
errors_total
```

**Description**: Total cumulative error count for the youtuberag service. Tracks all errors across the system.

**Expected Result**: 1 series with current error count

**Actual Result**: ✅ SUCCESS

```
errors_total{environment="development", instance="host.docker.internal:9091", job="youtuberag", service="youtuberag"} = 0
```

**Load Time**: 122ms  
**Performance**: Good ✅

**Value**: 0 (no errors in current session)

**Interpretation**:

- No errors have been encountered
- System is operating cleanly
- Normal for initial state before pipeline execution

**Use Case**: Monitor system error rates and error trends

---

### Query 3: Retry Attempts Tracking

**Query**:

```promql
retries_attempted
```

**Description**: Total number of retry attempts made by the system. Tracks resilience and fault recovery.

**Expected Result**: 1 series with retry count

**Actual Result**: ✅ SUCCESS

```
retries_attempted{environment="development", instance="host.docker.internal:9091", job="youtuberag", service="youtuberag"} = 0
```

**Load Time**: 31ms  
**Performance**: Excellent ✅

**Value**: 0 (no retries needed)

**Interpretation**:

- No retry events have occurred
- System has not needed to recover from failures
- All operations succeeded on first attempt

**Use Case**: Monitor system reliability and resilience patterns

---

### Query 4: Pipeline Operational State

**Query**:

```promql
graphrag_pipeline_status
```

**Description**: Current pipeline operational state. Values: 0=idle, 1=running, 2=completed, 3=failed

**Expected Result**: 1 series showing current state

**Actual Result**: ✅ SUCCESS

```
graphrag_pipeline_status{environment="development", instance="host.docker.internal:9091", job="youtuberag", service="youtuberag"} = 0
```

**Load Time**: 66ms  
**Performance**: Good ✅

**Value**: 0 (IDLE state)

**Interpretation**:

- Pipeline is currently idle (not running)
- No pipeline execution in progress
- System ready for next pipeline run

**Pipeline State Values**:

- 0 = Idle (waiting for input)
- 1 = Running (processing data)
- 2 = Completed (successfully finished)
- 3 = Failed (encountered errors)

**Use Case**: Monitor pipeline execution state and lifecycle

---

### Query 5: Metrics Server Health with Label Filter

**Query**:

```promql
up{job="youtuberag"}
```

**Description**: Check health status of specifically the youtuberag metrics server. Uses label filtering for precision.

**Expected Result**: 1 series showing only youtuberag target status

**Actual Result**: ✅ SUCCESS

```
up{environment="development", instance="host.docker.internal:9091", job="youtuberag", service="youtuberag"} = 1
```

**Load Time**: 48ms  
**Performance**: Excellent ✅

**Value**: 1 (UP and healthy)

**Interpretation**:

- Metrics server is UP
- Responding to scrape requests
- Successfully integrated with Prometheus

**Label Details**:

- `environment="development"` - Deployment environment
- `instance="host.docker.internal:9091"` - Docker internal address and port
- `job="youtuberag"` - Job identifier (matches Prometheus config)
- `service="youtuberag"` - Service name

**Use Case**: Verify specific service health with label-based filtering

---

## Additional PromQL Queries (Ready to Test)

These queries are ready to use once pipeline data is available:

### Rate Queries (Time-Based Changes)

```promql
# Error rate over 5 minutes
rate(errors_total[5m])

# Retry rate per minute
rate(retries_attempted[1m])
```

### Aggregation Queries

```promql
# Sum of all errors
sum(errors_total)

# Count distinct jobs
count(distinct(job))
```

### Histogram Queries (When Available)

```promql
# Stage duration quantiles
histogram_quantile(0.95, stage_duration_seconds)

# 99th percentile pipeline duration
histogram_quantile(0.99, graphrag_pipeline_stage_duration_seconds)
```

---

## Query Performance Summary

| Query                    | Load Time | Status | Category   |
| ------------------------ | --------- | ------ | ---------- |
| up                       | 9ms       | ✅     | Health     |
| errors_total             | 122ms     | ✅     | Errors     |
| retries_attempted        | 31ms      | ✅     | Resilience |
| graphrag_pipeline_status | 66ms      | ✅     | Pipeline   |
| up{job="youtuberag"}     | 48ms      | ✅     | Filtering  |

**Metrics**:

- Average Load Time: 55.2ms
- Fastest Query: 9ms
- Slowest Query: 122ms
- All Queries: <200ms (excellent performance)

---

## Label Reference Guide

**Available Labels** (from executed queries):

| Label         | Value                     | Meaning                  |
| ------------- | ------------------------- | ------------------------ |
| `job`         | youtuberag, prometheus    | Job identifier           |
| `environment` | development               | Deployment environment   |
| `instance`    | host.docker.internal:9091 | Service instance address |
| `service`     | youtuberag                | Service name             |

---

## Testing Methodology

**Environment**: Prometheus UI Query Interface  
**URL**: http://localhost:9090/query  
**Method**: Manual query execution with result validation  
**Date**: November 12, 2025  
**Executor**: Human with AI validation

**Process**:

1. Navigate to Prometheus query page
2. Enter query in expression editor
3. Click Execute button
4. Verify results returned
5. Check load time and performance
6. Document findings

---

## Next Steps

### When Pipeline Runs

Once the GraphRAG pipeline executes:

1. Additional metrics will populate (chunk counts, stage durations)
2. Rate queries will show meaningful trends
3. Error metrics will track failures (if any)
4. Can create Grafana dashboards with these queries

### Recommended Additional Queries

After pipeline execution, test:

- `rate(stage_completed[5m])` - Stage completion rate
- `histogram_quantile(0.95, stage_duration_seconds)` - Performance SLA
- `errors_total / stage_started` - Error ratio

---

## Validation Status

✅ **All 5 Queries**: TESTED & WORKING  
✅ **All Results**: RETURNED SUCCESSFULLY  
✅ **Performance**: EXCELLENT (<200ms all queries)  
✅ **Labels**: PROPERLY PROPAGATED  
✅ **Network**: VERIFIED & FUNCTIONAL

---

## Conclusion

The metrics endpoint is fully operational and PromQL queries are working correctly. All tested queries execute successfully with excellent performance. The Prometheus integration with the metrics server is complete and ready for:

- Dashboard creation in Grafana
- Alert configuration
- Performance monitoring during pipeline execution
- Long-term observability tracking

---

**Document Metadata**:

- Type: PromQL Query Examples
- Achievement: 1.2
- Queries Tested: 5/5 successful
- Status: Complete and validated
- Performance: Excellent
- Ready for: Grafana dashboards, alerting, production monitoring
- Date: November 12, 2025
