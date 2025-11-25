# EXECUTION SUPPORT: Metrics Endpoint Validation Scripts

**For**: EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_12_01  
**Achievement**: 1.2 - Metrics Endpoint Validated  
**Purpose**: Provide ready-to-run validation scripts for human executor

---

## 🚀 Quick Start Commands

### Phase 1: Review & Start Metrics Server

```bash
# Step 1: Examine metrics implementation
echo "=== Checking app/api/metrics.py ==="
head -50 app/api/metrics.py
echo ""
echo "=== Checking prometheus_metrics.py ==="
head -50 business/services/observability/prometheus_metrics.py

# Step 2: Start metrics server on port 9091
echo "=== Starting metrics server ==="
python app/api/metrics.py 9091

# In another terminal, verify it's running:
ps aux | grep metrics.py
```

### Phase 2: Validate Metrics Format

```bash
# Step 1: Access metrics endpoint
echo "=== Fetching metrics from endpoint ==="
curl -s http://localhost:9091/metrics > /tmp/metrics.txt
echo "Metrics saved to /tmp/metrics.txt"

# Step 2: Verify Prometheus format
echo "=== Verifying Prometheus format ==="
echo "Total lines: $(wc -l < /tmp/metrics.txt)"
echo "HELP lines: $(grep -c '^# HELP' /tmp/metrics.txt)"
echo "TYPE lines: $(grep -c '^# TYPE' /tmp/metrics.txt)"
echo ""
echo "=== Sample metrics (first 20 lines) ==="
head -20 /tmp/metrics.txt

# Step 3: Count metrics by category
echo ""
echo "=== Metrics by category ==="
echo "Stage metrics: $(grep -c 'stage_' /tmp/metrics.txt)"
echo "Agent metrics: $(grep -c 'agent_' /tmp/metrics.txt)"
echo "Error metrics: $(grep -c 'errors_' /tmp/metrics.txt)"
echo "Other metrics: $(grep -v '^#' /tmp/metrics.txt | grep -v '^$' | wc -l)"
```

### Phase 3: Test Prometheus Scraping

```bash
# Test if Prometheus is scraping the metrics
echo "=== Testing Prometheus scraping ==="

# Test 1: Check if Prometheus can reach the endpoint
docker exec youtuberag-prometheus curl -s http://localhost:9091/metrics | head -5

# Test 2: Query Prometheus directly
echo ""
echo "=== Querying Prometheus ==="
curl -s 'http://localhost:9090/api/v1/query?query=up' | python3 -m json.tool | head -20

# Test 3: Check specific metrics
echo ""
echo "=== Checking specific metrics in Prometheus ==="
curl -s 'http://localhost:9090/api/v1/query?query=stage_started' | python3 -m json.tool

# Test 4: Check targets
echo ""
echo "=== Prometheus Targets ==="
curl -s 'http://localhost:9090/api/v1/targets' | python3 -c "import json, sys; data=json.load(sys.stdin); print(f\"Active targets: {len(data.get('data', {}).get('activeTargets', []))}\")"
```

### Phase 4: Comprehensive Validation Script

Save as `validate-metrics.sh` and run:

```bash
#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                   Metrics Endpoint Validation Script                     ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"

# Test 1: Server running
echo ""
echo "TEST 1: Metrics Server Running"
if ps aux | grep -q "python.*metrics.py"; then
    echo "✅ Metrics server process found"
else
    echo "❌ Metrics server NOT running"
    exit 1
fi

# Test 2: Port listening
echo ""
echo "TEST 2: Port 9091 Listening"
if netstat -tuln | grep -q 9091 || lsof -i :9091 > /dev/null 2>&1; then
    echo "✅ Port 9091 is listening"
else
    echo "❌ Port 9091 NOT listening"
fi

# Test 3: Endpoint responds
echo ""
echo "TEST 3: Endpoint Responds (HTTP 200)"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9091/metrics)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Endpoint returns HTTP 200"
else
    echo "❌ Endpoint returns HTTP $HTTP_CODE"
fi

# Test 4: Prometheus format
echo ""
echo "TEST 4: Prometheus Format Compliance"
curl -s http://localhost:9091/metrics > /tmp/metrics_test.txt
HELP_COUNT=$(grep -c '^# HELP' /tmp/metrics_test.txt)
TYPE_COUNT=$(grep -c '^# TYPE' /tmp/metrics_test.txt)
echo "HELP lines: $HELP_COUNT"
echo "TYPE lines: $TYPE_COUNT"
if [ "$HELP_COUNT" -gt 10 ] && [ "$TYPE_COUNT" -gt 10 ]; then
    echo "✅ Format looks valid"
else
    echo "❌ Format may be incorrect"
fi

# Test 5: Prometheus scraping
echo ""
echo "TEST 5: Prometheus Scraping"
RESULT=$(curl -s 'http://localhost:9090/api/v1/query?query=up' 2>/dev/null | grep -c "value")
if [ "$RESULT" -gt 0 ]; then
    echo "✅ Prometheus has metrics"
else
    echo "❌ Prometheus not scraping"
fi

# Test 6: Sample PromQL queries
echo ""
echo "TEST 6: PromQL Query Examples"
echo "Query 1: up{job='prometheus'}"
curl -s 'http://localhost:9090/api/v1/query?query=up{job="prometheus"}' 2>/dev/null | python3 -c "import json, sys; data=json.load(sys.stdin); print(f\"  Result: {len(data.get('data', {}).get('result', []))} series\")"

echo ""
echo "✅ Validation complete"
```

### Phase 5: Create Validation Report

```bash
# Generate comprehensive validation report

cat > validation-report.md << 'REPORT'
# Metrics Endpoint Validation Report

**Date**: $(date)
**Executor**: (Your name)

## Test Results

### Endpoint Accessibility
- [ ] Server running on port 9091
- [ ] HTTP 200 response
- [ ] Response time < 100ms

### Prometheus Format
- [ ] HELP lines present: _____ count
- [ ] TYPE lines present: _____ count
- [ ] Metric naming (snake_case): ✅/❌
- [ ] Labels format correct: ✅/❌

### Metrics Categories
- [ ] Stage metrics found: ✅/❌
  - stage_started
  - stage_completed
  - stage_failed
  - stage_duration_seconds
  - documents_processed

- [ ] Agent metrics found: ✅/❌
  - agent_llm_calls
  - agent_llm_errors
  - agent_llm_duration_seconds
  - agent_tokens_used
  - agent_llm_cost_usd

### Prometheus Scraping
- [ ] Target health: UP/DOWN
- [ ] Last scrape: _____ (should be recent)
- [ ] Query execution: ✅/❌

### PromQL Query Examples

#### Working Queries:
1. Query: `up{job="prometheus"}`
   Result: ✅ Returns results

2. Query: `stage_started`
   Result: ✅/❌

3. Query: `rate(stage_completed[1m])`
   Result: ✅/❌

## Issues Encountered

(Document any issues found)

## Resolutions Applied

(Document how issues were resolved)

## Recommendations

(Any recommendations for improvements)
REPORT

echo "Report template created: validation-report.md"
```

---

## 📋 Manual Testing Checklist

### Phase 1: Code Review

```
□ Read app/api/metrics.py
  - Verify metrics server implementation
  - Check port configuration
  - Understand metrics registration

□ Read business/services/observability/prometheus_metrics.py
  - Verify metrics definitions
  - Check Counter, Gauge, Histogram usage
  - Note all available metrics
```

### Phase 2: Endpoint Testing

```
□ Start metrics server
  python app/api/metrics.py 9091

□ Test endpoint
  curl http://localhost:9091/metrics

□ Verify format
  - Check for # HELP lines
  - Check for # TYPE lines
  - Verify metric naming

□ Save metrics output
  curl http://localhost:9091/metrics > metrics-output.txt
```

### Phase 3: Prometheus Integration

```
□ Open Prometheus UI
  http://localhost:9090

□ Check Targets page
  - Look for metrics endpoint target
  - Check health (UP/DOWN)
  - Check last scrape time

□ Test queries
  - Query 1: up{job="prometheus"}
  - Query 2: stage_started
  - Query 3: agent_llm_calls
```

### Phase 4: Documentation

```
□ Create Validation Report
  - Document findings
  - List all metrics found
  - Note any issues

□ Create PromQL Examples
  - 10-15 working queries
  - Descriptions for each
  - Expected results

□ Create Debug Log
  - Step-by-step execution
  - Issues and resolutions
  - Performance notes
```

---

## 📊 Expected Metrics

### Stage Metrics (should find)

- `stage_started{stage="extraction"}`
- `stage_started{stage="resolution"}`
- `stage_started{stage="construction"}`
- `stage_started{stage="detection"}`
- `stage_completed{stage=...}`
- `stage_failed{stage=...}`
- `stage_duration_seconds{stage=...}`
- `documents_processed{stage=...}`

### Agent Metrics (if agents present)

- `agent_llm_calls{agent=...}`
- `agent_llm_errors{agent=...}`
- `agent_llm_duration_seconds{agent=...}`
- `agent_tokens_used{agent=..., token_type=...}`
- `agent_llm_cost_usd{agent=...}`

---

## 🆘 Troubleshooting

### If Metrics Server Won't Start

```bash
# Check port conflicts
lsof -i :9091
ps aux | grep metrics.py

# Try verbose startup
python -u app/api/metrics.py 9091 2>&1 | tee metrics-startup.log
```

### If Prometheus Not Scraping

```bash
# Test from Prometheus container
docker exec youtuberag-prometheus curl http://localhost:9091/metrics

# Check Prometheus config
cat observability/prometheus/prometheus.yml | grep -A5 "9091"

# Check Prometheus logs
docker logs youtuberag-prometheus 2>&1 | grep -i "9091\|scrape"
```

### If Queries Return Empty

```bash
# Wait for metrics to accumulate (minimum 30 seconds)
sleep 30

# Check if Prometheus has any data
curl -s 'http://localhost:9090/api/v1/query?query=up' | python3 -m json.tool

# May need to run pipeline to generate metrics
```

---

**Status**: Ready for human executor to follow these scripts and procedures.
