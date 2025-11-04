# Metrics Reference - Complete Catalog

**Last Updated**: November 3, 2025  
**Total Metrics**: 12 distinct metrics (~100 combinations with labels)

---

## Stage Metrics (Automatic from BaseStage)

### stage_started
**Type**: Counter  
**Labels**: stage  
**Description**: Number of stage executions started  
**Example**: `stage_started{stage="graph_extraction"} 1`

### stage_completed
**Type**: Counter  
**Labels**: stage  
**Description**: Number of stage executions completed successfully  
**Example**: `stage_completed{stage="entity_resolution"} 1`

### stage_failed
**Type**: Counter  
**Labels**: stage  
**Description**: Number of stage executions that failed fatally  
**Example**: `stage_failed{stage="community_detection"} 0`

### stage_duration_seconds
**Type**: Histogram (exported as summary)  
**Labels**: stage  
**Description**: Stage execution duration in seconds  
**Exported**:
- `stage_duration_seconds_count{stage="graph_extraction"}`
- `stage_duration_seconds_sum{stage="graph_extraction"}`  
- `stage_duration_seconds_min{stage="graph_extraction"}`
- `stage_duration_seconds_max{stage="graph_extraction"}`
- `stage_duration_seconds_avg{stage="graph_extraction"}`

**Example Prometheus Query**:
```promql
# Average stage duration
rate(stage_duration_seconds_sum[5m]) / rate(stage_duration_seconds_count[5m])
```

### documents_processed
**Type**: Counter  
**Labels**: stage  
**Description**: Total documents processed by stage  
**Example**: `documents_processed{stage="graph_extraction"} 13051`

**Prometheus Query**:
```promql
# Documents per second
rate(documents_processed[1m])
```

### documents_failed
**Type**: Counter  
**Labels**: stage  
**Description**: Total documents that failed processing in stage  
**Example**: `documents_failed{stage="graph_extraction"} 18`

**Prometheus Query**:
```promql
# Failure rate
rate(documents_failed[5m]) / rate(documents_processed[5m])
```

---

## Agent Metrics (Automatic from BaseAgent)

### agent_llm_calls
**Type**: Counter  
**Labels**: agent, model  
**Description**: Total LLM calls made by agent  
**Example**: `agent_llm_calls{agent="GraphExtractionAgent",model="gpt-4o-mini"} 13051`

**Prometheus Query**:
```promql
# Calls per minute by agent
rate(agent_llm_calls[1m])

# Total calls by model
sum by (model) (agent_llm_calls)
```

### agent_llm_errors
**Type**: Counter  
**Labels**: agent, model  
**Description**: Total LLM call errors  
**Example**: `agent_llm_errors{agent="GraphExtractionAgent",model="gpt-4o-mini"} 18`

**Prometheus Query**:
```promql
# Error rate
rate(agent_llm_errors[5m]) / rate(agent_llm_calls[5m])
```

### agent_llm_duration_seconds
**Type**: Histogram  
**Labels**: agent, model  
**Description**: LLM call duration in seconds  
**Example**: `agent_llm_duration_seconds_avg{agent="GraphExtractionAgent",model="gpt-4o-mini"} 15.2`

**Prometheus Query**:
```promql
# 95th percentile latency (requires buckets - we export summary)
agent_llm_duration_seconds_max{agent="GraphExtractionAgent"}
```

### agent_tokens_used
**Type**: Counter  
**Labels**: agent, model, token_type  
**Description**: Total tokens used (prompt/completion/total)  
**Example**: 
```
agent_tokens_used{agent="GraphExtractionAgent",model="gpt-4o-mini",token_type="prompt"} 13051000
agent_tokens_used{agent="GraphExtractionAgent",model="gpt-4o-mini",token_type="completion"} 6525500
agent_tokens_used{agent="GraphExtractionAgent",model="gpt-4o-mini",token_type="total"} 19576500
```

**Prometheus Query**:
```promql
# Tokens per minute
rate(agent_tokens_used{token_type="total"}[1m])

# Tokens by agent
sum by (agent) (agent_tokens_used{token_type="total"})

# Input vs output ratio
sum(agent_tokens_used{token_type="completion"}) / sum(agent_tokens_used{token_type="prompt"})
```

### agent_llm_cost_usd
**Type**: Counter  
**Labels**: agent, model  
**Description**: Estimated LLM cost in USD (running total)  
**Example**: `agent_llm_cost_usd{agent="GraphExtractionAgent",model="gpt-4o-mini"} 5.87`

**Prometheus Query**:
```promql
# Cost per hour
rate(agent_llm_cost_usd[1h])

# Total cost
sum(agent_llm_cost_usd)

# Cost by agent
topk(5, sum by (agent) (agent_llm_cost_usd))

# Cost projection (next 24h based on last hour)
predict_linear(agent_llm_cost_usd[1h], 24*3600)
```

---

## Global Metrics

### errors_total
**Type**: Counter  
**Labels**: error_type, component  
**Description**: Total errors logged (auto-populated by log_exception)  
**Example**: `errors_total{error_type="ValueError",component="extraction"} 18`

**Prometheus Query**:
```promql
# Error rate
rate(errors_total[5m])

# Errors by type
sum by (error_type) (errors_total)

# Top error components
topk(5, sum by (component) (errors_total))
```

**Alert Example**:
```yaml
- alert: HighErrorRate
  expr: rate(errors_total[5m]) > 1
  annotations:
    summary: "Error rate above 1/second"
```

### retries_attempted
**Type**: Counter  
**Labels**: function, error_type  
**Description**: Total retry attempts (auto-populated by @with_retry)  
**Example**: `retries_attempted{function="call_model",error_type="APIError"} 15`

**Prometheus Query**:
```promql
# Retry rate
rate(retries_attempted[5m])

# Most retried functions
topk(5, sum by (function) (retries_attempted))

# Retries by error type
sum by (error_type) (retries_attempted)
```

---

## Dashboard Queries

### Pipeline Execution Dashboard

**Stage Progress**:
```promql
# Stages started vs completed (detect stuck stages)
stage_started - stage_completed

# Average stage duration
avg by (stage) (stage_duration_seconds_avg)

# Document throughput
rate(documents_processed[5m])
```

### LLM Cost Dashboard

**Cost Tracking**:
```promql
# Cost per hour (last hour rate)
rate(agent_llm_cost_usd[1h])

# Cost by agent
sum by (agent) (agent_llm_cost_usd)

# Tokens per dollar
sum(agent_tokens_used{token_type="total"}) / sum(agent_llm_cost_usd)
```

### Error Monitoring Dashboard

**Error Tracking**:
```promql
# Error rate (errors/sec)
rate(errors_total[5m])

# Error distribution
sum by (error_type) (errors_total)

# Failed vs processed documents
rate(documents_failed[5m]) / rate(documents_processed[5m])
```

---

## Alert Recommendations

### Critical Alerts

**Stage Stuck**:
```yaml
- alert: StageStuck
  expr: (stage_started - stage_completed) > 0
  for: 1h
  annotations:
    summary: "Stage started but not completed for 1 hour"
```

**High Error Rate**:
```yaml
- alert: HighErrorRate
  expr: rate(errors_total[5m]) > 10
  annotations:
    summary: "More than 10 errors/second"
```

**High LLM Cost**:
```yaml
- alert: HighLLMCost
  expr: rate(agent_llm_cost_usd[1h]) > 10
  annotations:
    summary: "LLM cost exceeding $10/hour"
```

### Warning Alerts

**High Retry Rate**:
```yaml
- alert: HighRetryRate
  expr: rate(retries_attempted[5m]) > 1
  for: 10m
  annotations:
    summary: "Retry rate above 1/second for 10 minutes"
```

**Slow Stage**:
```yaml
- alert: SlowStage
  expr: stage_duration_seconds_avg > 3600
  annotations:
    summary: "Stage taking longer than 1 hour on average"
```

---

## Adding Custom Metrics

### In Your Code:

```python
from core.libraries.metrics import Counter, Histogram, MetricRegistry

# Create metric
my_metric = Counter('my_custom_metric', 'Description', labels=['type'])

# Register
registry = MetricRegistry.get_instance()
registry.register(my_metric)

# Use
my_metric.inc(labels={'type': 'success'})

# Automatically exported to Prometheus!
```

---

## Accessing Metrics

### Prometheus Endpoint:
http://localhost:9091/metrics

### Programmatically:
```python
from core.libraries.metrics import MetricRegistry, export_prometheus_text

# Get specific metric
registry = MetricRegistry.get_instance()
stage_counter = registry.get('stage_started')
count = stage_counter.get(labels={'stage': 'extraction'})

# Export all
metrics_text = export_prometheus_text()
```

---

**For observability stack setup**: See observability/README.md  
**For library details**: See technical/OBSERVABILITY.md

