# SUBPLAN: Metrics Endpoint Validated - Achievement 1.2

**PLAN**: PLAN_GRAPHRAG-OBSERVABILITY-VALIDATION.md  
**Achievement**: 1.2 - Metrics Endpoint Validated  
**Created**: 2025-11-11  
**Status**: 🎨 Design Phase Complete - Ready for Execution

---

## 🎯 Objective

Verify that the Prometheus metrics endpoint is fully functional and properly integrated with the running Prometheus server. Validate that:

- Metrics server starts correctly on port 9091
- Metrics are exported in correct Prometheus format
- Stage metrics (extraction, resolution, construction, detection) are present
- Agent metrics (LLM calls, errors, tokens, costs) are present
- Prometheus successfully scrapes metrics from the endpoint
- PromQL queries work correctly

---

## 📋 Deliverables

1. **Metrics Endpoint Validation Report** (Markdown)

   - Current endpoint implementation status
   - Prometheus format compliance verification
   - All metrics identified and categorized
   - Any issues found and workarounds

2. **Prometheus Configuration Validation** (YAML)

   - Updated prometheus.yml if changes needed
   - Scrape target configuration
   - Any new configurations added

3. **Debug Log** (Text/Markdown)

   - Step-by-step execution log
   - Issues encountered and how resolved
   - Network connectivity verification
   - Performance observations

4. **PromQL Query Examples** (Markdown)
   - 10-15 working PromQL queries
   - Examples for each metric category
   - Query descriptions and expected results

---

## 🔍 Detailed Approach

### Phase 1: Endpoint Review & Setup (25-30 minutes)

**Step 1.1**: Review existing metrics endpoint

- Examine `app/api/metrics.py`
- Check `business/services/observability/prometheus_metrics.py`
- Verify port configuration (should be 9091)
- Check if endpoint is exposed correctly
- Note any dependencies or initialization steps

**Step 1.2**: Verify Prometheus configuration

- Review `observability/prometheus/prometheus.yml`
- Check scrape targets section
- Verify target URL: `http://localhost:9091/metrics`
- Check scrape interval and timeout settings
- Note any authentication or TLS configurations

**Step 1.3**: Start metrics server

```bash
python app/api/metrics.py 9091
```

- Verify server starts without errors
- Check console output for initialization messages
- Confirm port 9091 is listening
- Note any warnings or issues

### Phase 2: Metrics Format Validation (30-35 minutes)

**Step 2.1**: Access metrics endpoint

```bash
curl http://localhost:9091/metrics
```

- Verify endpoint responds (HTTP 200)
- Check response format (should be Prometheus text format)
- Save full metrics output for analysis

**Step 2.2**: Verify Prometheus format compliance

- Check HELP lines present for each metric
- Check TYPE lines present for each metric
- Verify metric naming convention (snake_case)
- Verify labels format `{label="value"}`
- Check numerical values are valid floats/ints

**Step 2.3**: Identify and categorize metrics
Count and list all metrics by type:

- **Stage Metrics**: stage_started, stage_completed, stage_failed, stage_duration_seconds, documents_processed, documents_failed
- **Agent Metrics**: agent_llm_calls, agent_llm_errors, agent_llm_duration_seconds, agent_tokens_used, agent_llm_cost_usd
- **Global Metrics**: errors_total, retries_attempted
- **Custom Metrics**: Any project-specific metrics
- **System Metrics**: process*\*, go*_, node\__ (if enabled)

**Step 2.4**: Verify stage metrics present
For each stage (extraction, resolution, construction, detection):

- stage_started metric exists and has stage label
- stage_completed metric exists
- stage_failed metric exists
- stage_duration_seconds metric exists
- documents_processed metric has stage label
- Log findings in debug log

**Step 2.5**: Verify agent metrics present
For each agent (if applicable):

- agent_llm_calls metric with agent label
- agent_llm_errors metric with agent label
- agent_llm_duration_seconds metric with agent label
- agent_tokens_used metric with token_type label
- agent_llm_cost_usd metric present
- Log findings in debug log

### Phase 3: Prometheus Scraping Validation (30-35 minutes)

**Step 3.1**: Check Prometheus targets

- Open Prometheus UI: http://localhost:9090/targets
- Look for scrape target with URL http://localhost:9091/metrics
- Check target health (should be "UP")
- Check last scrape time (should be recent)
- Note any errors or warnings
- Take screenshot or log state

**Step 3.2**: Check scrape history

- In Prometheus UI, check "Up" metric
- Look for metrics with job label matching metrics endpoint
- Verify metrics have been scraped (non-empty results)
- Check timestamp of metrics (should be recent)
- Log any timing issues

**Step 3.3**: Test basic PromQL queries

```promql
# Test 1: Check if any metrics available
up{job="prometheus"}

# Test 2: Check specific metric
stage_started{stage="extraction"}

# Test 3: Check agent metrics
agent_llm_calls{agent="GraphExtractionAgent"}
```

- Run each query in Prometheus UI
- Verify results are returned (not empty)
- Check metric values are reasonable
- Note any query errors in debug log

**Step 3.4**: Test rate queries (if time-series data available)

```promql
# Rate of stage completions per minute
rate(stage_completed[1m])

# Rate of LLM calls per minute
rate(agent_llm_calls[1m])
```

- Log results (may be empty if insufficient time-series data)
- Note if data needs to accumulate over time

### Phase 4: Debugging & Resolution (40-50 minutes)

**Step 4.1**: If endpoint not responding

- Verify metrics server is running: `ps aux | grep metrics.py`
- Check for port conflicts: `lsof -i :9091`
- Check server logs for errors
- Try restarting metrics server with verbose logging
- Check Python dependencies are installed

**Step 4.2**: If metrics format incorrect

- Review prometheus_metrics.py implementation
- Check metric registration (Counter, Gauge, Histogram types)
- Verify HELP and TYPE decorators present
- Check metric names don't violate Prometheus conventions
- Log issues found in debug log

**Step 4.3**: If Prometheus not scraping

- Verify metrics server port accessible from Prometheus container: `docker exec youtuberag-prometheus curl http://localhost:9091/metrics`
- Check Prometheus config has correct target URL
- Verify scrape interval setting (default 15s)
- Check Prometheus logs for scrape errors
- May need to update prometheus.yml if target changed

**Step 4.4**: Network connectivity issues

- Test ping from Prometheus container to metrics server
- Test curl from Prometheus container
- Check firewall rules if running on different machines
- Verify Docker network connectivity if containerized

### Phase 5: Documentation & Query Examples (30-40 minutes)

**Step 5.1**: Create validation report

- Document current implementation status
- List all metrics found (with sample values)
- Note any Prometheus format issues
- Document issues found and how resolved
- Include screenshots of Prometheus UI if helpful

**Step 5.2**: Create PromQL query examples

- Write 10-15 example queries covering:
  - Per-stage metrics (extraction, resolution, construction, detection)
  - Agent metrics for each agent type
  - Rate of metric changes over time
  - Aggregation queries (sum, avg, etc.)
  - Alerting-ready queries (thresholds)
- Include query description and expected results for each
- Document successful queries vs. failed queries

**Step 5.3**: Test all queries

- Run each PromQL query in Prometheus UI
- Verify results are returned
- Note any queries that don't work (may need pipeline data)
- Document which queries require active pipeline

---

## ⏱️ Time Breakdown

- Phase 1 (Endpoint Review): 25-30 min
- Phase 2 (Metrics Format): 30-35 min
- Phase 3 (Prometheus Validation): 30-35 min
- Phase 4 (Debugging): 40-50 min (if issues found)
- Phase 5 (Documentation): 30-40 min
- **Total**: 2-3 hours

---

## 🧪 Testing Plan

### Test 1: Endpoint Responsiveness (5 min)

- **What**: Verify metrics endpoint responds on port 9091
- **How**: `curl http://localhost:9091/metrics`
- **Expected**: HTTP 200 response with Prometheus text format
- **Pass Criteria**: Endpoint accessible and returns data

### Test 2: Format Compliance (5 min)

- **What**: Verify Prometheus text format compliance
- **How**: Check for HELP, TYPE, and metric line format
- **Expected**: Valid Prometheus format with all required lines
- **Pass Criteria**: All metrics properly formatted

### Test 3: Metrics Presence (5 min)

- **What**: Verify all expected metrics present
- **How**: Count metrics by category (stage, agent, etc.)
- **Expected**: ≥ 20 metrics total, all categories represented
- **Pass Criteria**: All metric categories present with samples

### Test 4: Prometheus Scraping (10 min)

- **What**: Verify Prometheus successfully scrapes endpoint
- **How**: Check Prometheus targets page + run test query
- **Expected**: Target shows "UP", query returns results
- **Pass Criteria**: Prometheus scraping actively

### Test 5: Query Examples (10 min)

- **What**: Verify PromQL queries work
- **How**: Run 5-10 example queries in Prometheus UI
- **Expected**: All queries return results (or expected empty if no data)
- **Pass Criteria**: Queries formatted correctly and execute

### Test 6: Network Connectivity (5 min)

- **What**: Verify network path from Prometheus to metrics
- **How**: `docker exec youtuberag-prometheus curl http://localhost:9091/metrics`
- **Expected**: Metrics returned from within container
- **Pass Criteria**: Network connectivity verified

---

## 🚀 Execution Strategy

**Single EXECUTION_TASK with Sequential Phases**

This achievement is best executed as a single sequential task:

1. Review existing implementation (Phase 1)
2. Validate metrics format (Phase 2)
3. Test Prometheus scraping (Phase 3)
4. Debug any issues (Phase 4)
5. Document findings and queries (Phase 5)

Each phase builds on previous results, so sequential execution is optimal.

**Estimated Duration**: 2-3 hours for full execution including all testing and documentation

---

## 📊 Success Criteria

Achievement 1.2 is complete when:

✅ Metrics server running successfully on port 9091  
✅ Endpoint responds to curl with Prometheus-formatted metrics  
✅ All expected metrics present (stage + agent + custom)  
✅ Prometheus successfully scrapes metrics (target shows "UP")  
✅ At least 10 PromQL queries verified working  
✅ Validation report completed  
✅ Debug log documenting any issues and resolutions  
✅ Query examples documented with descriptions

---

## 📚 Expected Results

Upon completion:

- Metrics endpoint fully validated and operational
- Prometheus receiving live metrics data
- PromQL queries ready for dashboard creation
- Foundation established for Achievement 1.3 (Grafana dashboards)
- Clear documentation of metrics available for monitoring

---

## 🔗 Dependencies & Context

**Prerequisites**:

- Achievement 1.1 (Observability Stack Running) - COMPLETE ✅
- Prometheus running and accessible on port 9090
- Metrics server code available in `app/api/metrics.py`

**Enables Next Achievement**:

- Achievement 1.3 (Grafana Dashboards Configured)
- Metrics data needed for dashboard panels

**Related Work**:

- Achievement 0.4 (Per-Stage Quality Metrics) - Provides metrics data
- Achievement 0.3 (Query Scripts) - Uses metrics endpoints

---

## 📋 Notes

- If metrics server doesn't exist yet, will need to create basic implementation
- May need to update Prometheus config to point to correct endpoint
- Network connectivity between Prometheus and metrics server critical
- Queries may return empty results if no pipeline has run yet
- Can use `04-generate-test-metrics.py` from Achievement 1.1 to test with sample data

---

**Design Status**: ✅ COMPLETE - Ready for Execution Phase

All sections detailed, execution strategy clear, tests defined, success criteria specified.

Executor can now proceed with EXECUTION_TASK.
