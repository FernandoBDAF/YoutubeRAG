# Dashboard Queries Reference - Achievement 1.3

**Achievement**: 1.3 - Grafana Dashboards Configured  
**Date**: 2025-11-12  
**Dashboard**: GraphRAG Pipeline Dashboard

---

## 📋 Overview

This document provides a complete reference of all PromQL queries used in the GraphRAG Pipeline Dashboard. Each panel's query is documented with explanation, expected metrics, and usage context.

**Total Panels**: 12  
**Total Queries**: 15 (some panels have multiple queries)  
**Data Source**: Prometheus

---

## 📊 Panel Queries

### Panel 1: Pipeline Status

**Panel Type**: Stat  
**Panel ID**: 1  
**Position**: Top-left (h: 4, w: 6, x: 0, y: 0)

**Query A**:

```promql
graphrag_pipeline_status
```

**Legend Format**: `Status`

**Description**: Returns the current pipeline status as an integer:

- `0` = Idle (gray)
- `1` = Running (blue)
- `2` = Completed (green)
- `3` = Failed (red)

**Expected Metric**: `graphrag_pipeline_status` (gauge)

**Visualization**: Stat panel with value mappings and color thresholds

---

### Panel 2: Pipeline Runs

**Panel Type**: Stat  
**Panel ID**: 2  
**Position**: Top-center (h: 4, w: 3, x: 6, y: 0)

**Query A**:

```promql
sum(increase(pipeline_runs{pipeline_type="graphrag"}[1h]))
```

**Legend Format**: `Runs (1h)`

**Description**: Calculates the total number of pipeline runs in the last hour by:

1. Filtering for `pipeline_type="graphrag"`
2. Calculating the increase over 1 hour
3. Summing across all instances

**Expected Metric**: `pipeline_runs` (counter with label `pipeline_type`)

**Visualization**: Stat panel showing total count

---

### Panel 3: Pipeline Duration

**Panel Type**: Stat  
**Panel ID**: 3  
**Position**: Top-right (h: 4, w: 3, x: 9, y: 0)

**Query A**:

```promql
avg(pipeline_duration_seconds_sum{pipeline_type="graphrag"} / pipeline_duration_seconds_count{pipeline_type="graphrag"})
```

**Legend Format**: `Avg Duration`

**Description**: Calculates average pipeline duration by:

1. Dividing sum by count for each pipeline instance
2. Averaging across all instances

**Expected Metrics**:

- `pipeline_duration_seconds_sum` (summary)
- `pipeline_duration_seconds_count` (summary)

**Unit**: Seconds (s)  
**Decimals**: 1

**Visualization**: Stat panel showing average duration

---

### Panel 4: Stage Progress

**Panel Type**: Bar Gauge  
**Panel ID**: 4  
**Position**: Second row, left (h: 8, w: 12, x: 0, y: 4)

**Query A**:

```promql
graphrag_pipeline_stage_progress
```

**Legend Format**: `{{stage}}`

**Description**: Returns progress percentage (0-1) for each pipeline stage

**Expected Metric**: `graphrag_pipeline_stage_progress` (gauge with label `stage`)

**Unit**: Percent (0-1)  
**Thresholds**:

- 0 = Red
- 0.5 = Yellow
- 0.9 = Green

**Visualization**: Horizontal bar gauge with gradient display

---

### Panel 5: Chunks Processed by Stage

**Panel Type**: Time Series  
**Panel ID**: 5  
**Position**: Second row, right (h: 8, w: 12, x: 12, y: 4)

**Query A** (Processed):

```promql
rate(graphrag_pipeline_stage_chunks_processed[5m])
```

**Legend Format**: `{{stage}} - Processed`

**Query B** (Failed):

```promql
rate(graphrag_pipeline_stage_chunks_failed[5m])
```

**Legend Format**: `{{stage}} - Failed`

**Description**:

- **Query A**: Rate of chunks successfully processed per second (5-minute window)
- **Query B**: Rate of chunks that failed per second (5-minute window)

**Expected Metrics**:

- `graphrag_pipeline_stage_chunks_processed` (counter with label `stage`)
- `graphrag_pipeline_stage_chunks_failed` (counter with label `stage`)

**Unit**: Operations per second (ops)

**Visualization**: Time series graph with two series (processed vs failed)

---

### Panel 6: Throughput - Entities/sec

**Panel Type**: Time Series  
**Panel ID**: 6  
**Position**: Third row, left (h: 8, w: 6, x: 0, y: 12)

**Query A**:

```promql
graphrag_pipeline_throughput_entities_per_sec
```

**Legend Format**: `{{stage}}`

**Description**: Entities processed per second by stage

**Expected Metric**: `graphrag_pipeline_throughput_entities_per_sec` (gauge with label `stage`)

**Unit**: Operations per second (ops)

**Visualization**: Time series graph showing entity throughput over time

---

### Panel 7: Throughput - Relationships/sec

**Panel Type**: Time Series  
**Panel ID**: 7  
**Position**: Third row, center (h: 8, w: 6, x: 6, y: 12)

**Query A**:

```promql
graphrag_pipeline_throughput_relationships_per_sec
```

**Legend Format**: `{{stage}}`

**Description**: Relationships processed per second by stage

**Expected Metric**: `graphrag_pipeline_throughput_relationships_per_sec` (gauge with label `stage`)

**Unit**: Operations per second (ops)

**Visualization**: Time series graph showing relationship throughput over time

---

### Panel 8: Throughput - Communities/sec

**Panel Type**: Time Series  
**Panel ID**: 8  
**Position**: Third row, right (h: 8, w: 6, x: 12, y: 12)

**Query A**:

```promql
graphrag_pipeline_throughput_communities_per_sec
```

**Legend Format**: `{{stage}}`

**Description**: Communities processed per second by stage

**Expected Metric**: `graphrag_pipeline_throughput_communities_per_sec` (gauge with label `stage`)

**Unit**: Operations per second (ops)

**Visualization**: Time series graph showing community throughput over time

---

### Panel 9: Stage Duration

**Panel Type**: Time Series  
**Panel ID**: 9  
**Position**: Fourth row, left (h: 8, w: 12, x: 0, y: 20)

**Query A** (Average):

```promql
rate(graphrag_pipeline_stage_duration_seconds_sum[5m]) / rate(graphrag_pipeline_stage_duration_seconds_count[5m])
```

**Legend Format**: `{{stage}} - Avg`

**Query B** (Maximum):

```promql
graphrag_pipeline_stage_duration_seconds_max
```

**Legend Format**: `{{stage}} - Max`

**Description**:

- **Query A**: Average stage duration calculated from summary metrics (5-minute rate)
- **Query B**: Maximum stage duration observed

**Expected Metrics**:

- `graphrag_pipeline_stage_duration_seconds_sum` (summary with label `stage`)
- `graphrag_pipeline_stage_duration_seconds_count` (summary with label `stage`)
- `graphrag_pipeline_stage_duration_seconds_max` (gauge with label `stage`)

**Unit**: Seconds (s)

**Visualization**: Time series graph with two series (average and maximum)

---

### Panel 10: Error Rate by Stage

**Panel Type**: Time Series  
**Panel ID**: 10  
**Position**: Fourth row, right (h: 8, w: 12, x: 12, y: 20)

**Query A**:

```promql
rate(graphrag_pipeline_stage_errors_total[5m])
```

**Legend Format**: `{{stage}} - {{error_type}}`

**Description**: Error rate per second by stage and error type (5-minute window)

**Expected Metric**: `graphrag_pipeline_stage_errors_total` (counter with labels `stage` and `error_type`)

**Unit**: Operations per second (ops)

**Visualization**: Time series graph showing error rates over time, grouped by stage and error type

---

### Panel 11: Chunk Processing Time

**Panel Type**: Histogram  
**Panel ID**: 11  
**Position**: Fifth row, left (h: 8, w: 12, x: 0, y: 28)

**Query A**:

```promql
rate(graphrag_pipeline_chunk_processing_time_seconds_sum[5m]) / rate(graphrag_pipeline_chunk_processing_time_seconds_count[5m])
```

**Legend Format**: `{{stage}}`

**Description**: Average chunk processing time calculated from summary metrics (5-minute rate)

**Expected Metrics**:

- `graphrag_pipeline_chunk_processing_time_seconds_sum` (summary with label `stage`)
- `graphrag_pipeline_chunk_processing_time_seconds_count` (summary with label `stage`)

**Unit**: Seconds (s)

**Visualization**: Histogram showing distribution of chunk processing times by stage

---

### Panel 12: Stage Failures

**Panel Type**: Stat  
**Panel ID**: 12  
**Position**: Fifth row, right (h: 4, w: 6, x: 12, y: 28)

**Query A**:

```promql
sum(increase(pipeline_stage_failures{pipeline_type="graphrag"}[1h]))
```

**Legend Format**: `Failures (1h)`

**Description**: Total number of stage failures in the last hour

**Expected Metric**: `pipeline_stage_failures` (counter with label `pipeline_type`)

**Thresholds**:

- 0 = Green
- 1 = Yellow
- 5 = Red

**Visualization**: Stat panel with color-coded thresholds

---

## 📈 Metric Inventory

### Gauge Metrics

| Metric Name                                          | Labels  | Description                   |
| ---------------------------------------------------- | ------- | ----------------------------- |
| `graphrag_pipeline_status`                           | -       | Current pipeline status (0-3) |
| `graphrag_pipeline_stage_progress`                   | `stage` | Stage progress (0-1)          |
| `graphrag_pipeline_throughput_entities_per_sec`      | `stage` | Entity throughput rate        |
| `graphrag_pipeline_throughput_relationships_per_sec` | `stage` | Relationship throughput rate  |
| `graphrag_pipeline_throughput_communities_per_sec`   | `stage` | Community throughput rate     |
| `graphrag_pipeline_stage_duration_seconds_max`       | `stage` | Maximum stage duration        |

### Counter Metrics

| Metric Name                                | Labels                | Description                   |
| ------------------------------------------ | --------------------- | ----------------------------- |
| `pipeline_runs`                            | `pipeline_type`       | Total pipeline runs           |
| `graphrag_pipeline_stage_chunks_processed` | `stage`               | Chunks processed successfully |
| `graphrag_pipeline_stage_chunks_failed`    | `stage`               | Chunks that failed            |
| `graphrag_pipeline_stage_errors_total`     | `stage`, `error_type` | Total errors by type          |
| `pipeline_stage_failures`                  | `pipeline_type`       | Total stage failures          |

### Summary Metrics

| Metric Name                                       | Labels          | Description                       |
| ------------------------------------------------- | --------------- | --------------------------------- |
| `pipeline_duration_seconds`                       | `pipeline_type` | Pipeline duration (sum/count)     |
| `graphrag_pipeline_stage_duration_seconds`        | `stage`         | Stage duration (sum/count)        |
| `graphrag_pipeline_chunk_processing_time_seconds` | `stage`         | Chunk processing time (sum/count) |

---

## 🔍 Query Patterns

### Rate Calculation

**Pattern**: `rate(metric[5m])`

**Usage**: Convert counter metrics to per-second rates

**Examples**:

- `rate(graphrag_pipeline_stage_chunks_processed[5m])`
- `rate(graphrag_pipeline_stage_errors_total[5m])`

### Average from Summary

**Pattern**: `rate(sum[5m]) / rate(count[5m])`

**Usage**: Calculate average from summary metrics

**Example**:

```promql
rate(graphrag_pipeline_stage_duration_seconds_sum[5m]) /
rate(graphrag_pipeline_stage_duration_seconds_count[5m])
```

### Increase Over Time

**Pattern**: `increase(metric[1h])`

**Usage**: Calculate total increase over time window

**Examples**:

- `increase(pipeline_runs{pipeline_type="graphrag"}[1h])`
- `increase(pipeline_stage_failures{pipeline_type="graphrag"}[1h])`

### Label Filtering

**Pattern**: `metric{label="value"}`

**Usage**: Filter metrics by label values

**Examples**:

- `pipeline_runs{pipeline_type="graphrag"}`
- `pipeline_stage_failures{pipeline_type="graphrag"}`

### Aggregation

**Pattern**: `sum(...)` or `avg(...)`

**Usage**: Aggregate across multiple instances or labels

**Examples**:

- `sum(increase(pipeline_runs{pipeline_type="graphrag"}[1h]))`
- `avg(pipeline_duration_seconds_sum{...} / pipeline_duration_seconds_count{...})`

---

## 🧪 Testing Queries

### Test in Prometheus UI

1. Open Prometheus: http://localhost:9090
2. Go to **Graph** tab
3. Paste query
4. Click **Execute**
5. Verify results

### Test in Grafana Explore

1. Open Grafana: http://localhost:3000
2. Go to **Explore**
3. Select **Prometheus** datasource
4. Paste query
5. Click **Run query**

### Example Test Queries

**Test Pipeline Status**:

```promql
graphrag_pipeline_status
```

**Test Pipeline Runs**:

```promql
pipeline_runs{pipeline_type="graphrag"}
```

**Test Stage Progress**:

```promql
graphrag_pipeline_stage_progress
```

---

## 📝 Query Modifications

### Change Time Window

**Original** (1 hour):

```promql
sum(increase(pipeline_runs{pipeline_type="graphrag"}[1h]))
```

**Modified** (6 hours):

```promql
sum(increase(pipeline_runs{pipeline_type="graphrag"}[6h]))
```

### Add Label Filters

**Original**:

```promql
graphrag_pipeline_stage_progress
```

**Modified** (filter by stage):

```promql
graphrag_pipeline_stage_progress{stage="extraction"}
```

### Change Rate Window

**Original** (5 minutes):

```promql
rate(graphrag_pipeline_stage_chunks_processed[5m])
```

**Modified** (1 minute):

```promql
rate(graphrag_pipeline_stage_chunks_processed[1m])
```

---

## 🔗 Related Documentation

- **Setup Guide**: `documentation/Dashboard-Setup-Guide-1.3.md`
- **Debug Log**: `documentation/Grafana-Dashboards-Debug-Log-1.3.md`
- **Metrics Endpoint**: `documentation/Metrics-Endpoint-Validation-Report-1.2.md`
- **PromQL Examples**: `documentation/PromQL-Examples-Achievement-1.2.md`

---

## ✅ Query Verification Checklist

Before using the dashboard, verify:

- [ ] All metrics exist in Prometheus
- [ ] Queries return data (or "No data" if pipeline hasn't run)
- [ ] Label values match expected stages
- [ ] Time windows are appropriate for use case
- [ ] Aggregations work correctly
- [ ] Rate calculations are accurate

---

**Last Updated**: 2025-11-12  
**Version**: 1.0
