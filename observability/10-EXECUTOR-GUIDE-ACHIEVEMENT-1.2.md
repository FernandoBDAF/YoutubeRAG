# 🚀 Executor Guide: Achievement 1.2 - Metrics Endpoint Validated

**Achievement**: 1.2 - Metrics Endpoint Validated  
**Duration**: 2-3 hours  
**Difficulty**: Medium  
**Status**: Ready to Execute

---

## 📋 Table of Contents

1. [Quick Overview](#quick-overview)
2. [Prerequisites Check](#prerequisites-check)
3. [Phase 1: Review & Start Server](#phase-1-review--start-server)
4. [Phase 2: Validate Format](#phase-2-validate-format)
5. [Phase 3: Test Prometheus Scraping](#phase-3-test-prometheus-scraping)
6. [Phase 4: Comprehensive Validation](#phase-4-comprehensive-validation)
7. [Phase 5: Documentation](#phase-5-documentation)
8. [Troubleshooting](#troubleshooting)
9. [Completion Checklist](#completion-checklist)

---

## Quick Overview

**Goal**: Verify that the Prometheus metrics endpoint is working correctly and Prometheus is successfully scraping metrics.

**What You'll Do**:

1. Review metrics implementation
2. Start metrics server
3. Validate metrics format
4. Test Prometheus scraping
5. Document findings with PromQL examples

**Expected Results**:

- ✅ Metrics server running on port 9091
- ✅ Metrics in Prometheus format
- ✅ All metrics categories present
- ✅ Prometheus successfully scraping
- ✅ 10-15 PromQL queries working
- ✅ Complete validation report

---

## Prerequisites Check

Before starting, verify you have everything:

### System Requirements

```bash
# Check if you're in the right directory
pwd
# Should show: .../YoutubeRAG

# Check Docker is running
docker ps
# Should show: youtuberag-prometheus, youtuberag-loki, youtuberag-grafana, youtuberag-promtail

# Check if metrics server code exists
ls -l app/api/metrics.py
# Should show the file exists

# Check if observability scripts exist
ls -l observability/0[6-9]-*.sh
# Should show 4 scripts
```

### Prerequisites Checklist

#### Infrastructure & Tools

```
□ Docker containers running (Prometheus, Grafana, Loki, Promtail)
□ Port 9090 accessible (Prometheus UI: http://localhost:9090)
□ Port 3000 accessible (Grafana: http://localhost:3000)
□ Port 9091 available (for metrics server)
□ Project directory: .../YoutubeRAG
□ Scripts ready: observability/06-09-*.sh
□ Python environment available
□ curl installed
□ python3 for JSON parsing
```

#### Environment Variables

**For Achievement 1.2**, you need these environment variables set:

**REQUIRED (for metrics server)**:

```bash
# At minimum, these 2 are usually sufficient for just starting the metrics server:
MONGODB_URI=mongodb://localhost:27017      # (or your MongoDB connection)
DB_NAME=mongo_hack                          # (or your database name)
```

**Optional (but recommended for full pipeline integration)**:

```bash
OPENAI_API_KEY=sk-your-key-here            # (only needed if running full pipeline)
GRAPHRAG_MODEL=gpt-4o-mini
GRAPHRAG_LOG_LEVEL=INFO
```

**Check if environment variables are set**:

```bash
# Verify key variables
echo "MongoDB URI: $MONGODB_URI"
echo "DB Name: $DB_NAME"

# If empty, set them:
export MONGODB_URI=mongodb://localhost:27017
export DB_NAME=mongo_hack
```

**Full environment template** (if you need all variables):

- Location: `documentation/ENV-OBSERVABILITY-TEMPLATE.md`
- Variables documented: `documentation/Environment-Variables-Guide.md`

**⚠️ NOTE**: Achievement 1.2 focuses on **metrics validation**, not pipeline execution:

- ✅ Metrics server will start with minimal env vars
- ✅ Prometheus scraping works with just Docker running
- ❌ Full pipeline requires OPENAI_API_KEY (not needed for 1.2)

**Verification**:

```bash
# Quick check
docker ps | grep youtuberag-prometheus    # Should show Prometheus running
curl http://localhost:9090                 # Should respond
echo $MONGODB_URI                           # Should show your MongoDB URI
```

**If anything is missing**, stop and set it up before continuing.

---

## Phase 1: Review & Start Server

**Objective**: Understand the metrics implementation and start the metrics server  
**Time**: 25-30 minutes  
**Terminal**: Terminal 1 (will run continuously)

### Step 1.1: Review Metrics Implementation

```bash
# Go to project root
cd /Users/fernandobarroso/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG

# Run the review script
bash observability/06-review-metrics-code.sh
```

**What to Look For**:

- ✅ File paths shown and readable
- ✅ Metrics implementation code displayed
- ✅ Port 9091 mentioned in config
- ✅ Prometheus config file found

**Expected Output Example**:

```
=== Reviewing app/api/metrics.py ===
✅ File found
First 50 lines of app/api/metrics.py:
[code shown here]

=== Reviewing prometheus_metrics.py ===
✅ File found
First 50 lines:
[code shown here]
```

### Step 1.2: Start the Metrics Server

**⚠️ IMPORTANT**: Keep this terminal running in the background!

The script will start the metrics server. Once you see this message:

```
Starting metrics server on port 9091
[Server running message]
```

**Keep this terminal open and minimized** - it needs to keep running.

**Document this**:

- [ ] Note the start time: **\*\***\_\_\_**\*\***
- [ ] Server started successfully: Yes / No
- [ ] Any error messages? Write them down: **\*\***\_\_\_**\*\***

---

## Phase 2: Validate Format

**Objective**: Verify metrics are being exported in correct Prometheus format  
**Time**: 30-35 minutes  
**Terminal**: Terminal 2 (new terminal)

### Step 2.1: Open New Terminal

Open a NEW terminal window/tab. **Do not stop Terminal 1!**

```bash
# In new terminal, go to project root
cd /Users/fernandobarroso/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG
```

### Step 2.2: Run Format Validation

```bash
bash observability/07-validate-metrics-format.sh
```

**What to Look For**:

- ✅ HTTP 200 response from endpoint
- ✅ HELP lines count: should be > 10
- ✅ TYPE lines count: should be > 10
- ✅ Metrics found in categories

**Expected Output Example**:

```
═══════════════════════════════════════════════════════════════════════════
  Phase 2: Validate Metrics Format
═══════════════════════════════════════════════════════════════════════════

Step 1: Accessing metrics endpoint

Fetching metrics from http://localhost:9091/metrics...
✅ Metrics saved to /tmp/metrics.txt

Step 2: Verifying Prometheus format compliance

Format Verification:
  Total lines: 1248
  HELP lines: 32
  TYPE lines: 32
  Metric lines: 1184

✅ Format looks valid (≥10 HELP and TYPE lines)

Step 3: Sample metrics (first 20 lines)
[metrics shown]

Step 4: Metrics by category
Stage metrics: 45
Agent metrics: 32
Error metrics: 8
Other metrics: 1099

✅ Metrics endpoint is responding with valid Prometheus format
```

### Step 2.3: Document Findings

**Record these findings**:

- [ ] Total metrics lines: **\*\***\_\_\_**\*\***
- [ ] HELP lines count: **\*\***\_\_\_**\*\***
- [ ] TYPE lines count: **\*\***\_\_\_**\*\***
- [ ] Stage metrics found: ✅ / ❌
- [ ] Agent metrics found: ✅ / ❌
- [ ] Any issues?: **\*\***\_\_\_**\*\***

**Save the full output**:

```bash
# Metrics are already saved to /tmp/metrics.txt
# View the full output:
cat /tmp/metrics.txt

# Copy a few lines for your report:
head -50 /tmp/metrics.txt > ~/metrics_sample.txt
```

---

## Phase 3: Test Prometheus Scraping

**Objective**: Verify Prometheus is successfully scraping metrics  
**Time**: 30-35 minutes  
**Terminal**: Terminal 3 (another new terminal) or Terminal 2 if Phase 2 completed

### Step 3.1: Run Prometheus Scraping Tests

```bash
bash observability/08-test-prometheus-scraping.sh
```

**What to Look For**:

- ✅ Container can reach metrics endpoint
- ✅ Prometheus targets show as "UP"
- ✅ Query results returned (not empty)
- ✅ Rate queries working

**Expected Output Example**:

```
═══════════════════════════════════════════════════════════════════════════
  Phase 3: Test Prometheus Scraping
═══════════════════════════════════════════════════════════════════════════

Test 1: Prometheus Container Access to Metrics Endpoint
Running: docker exec youtuberag-prometheus curl -s http://localhost:9091/metrics | head -5
# HELP metrics_processed Total metrics processed
# TYPE metrics_processed counter
metrics_processed{stage="extraction"} 124

✅ Prometheus container can reach metrics endpoint

Test 2: Checking Prometheus Targets
Active targets in Prometheus:
  Total active targets: 3
    • prometheus: UP
    • node_exporter: UP
    • custom-metrics: UP

Test 3: Querying Prometheus - up metric
Query: up{job='prometheus'}
Response:
  ✅ Found 1 series
    • {job="prometheus"}: 1

Test 4: Querying Prometheus - stage_started metric
Query: stage_started
Response:
  ✅ Found 4 series
    • extraction: 2
    • resolution: 1
    • construction: 1
```

### Step 3.2: Document Findings

**Record these findings**:

- [ ] Container can reach endpoint: ✅ / ❌
- [ ] Prometheus targets health: UP / DOWN / UNKNOWN
- [ ] up{job="prometheus"} returns results: ✅ / ❌
- [ ] stage_started queries return results: ✅ / ❌
- [ ] Any connection issues?: **\*\***\_\_\_**\*\***

### Step 3.3: Open Prometheus UI (Optional)

For visual verification:

```bash
# Open in browser:
# http://localhost:9090

# Check these pages:
# 1. Targets page: http://localhost:9090/targets
#    Look for your metrics endpoint target
#    Should show "UP" status
# 2. Graph page: http://localhost:9090/graph
#    Try querying: up
#    Should show results
```

---

## Phase 4: Comprehensive Validation

**Objective**: Run all 6 tests and get final pass/fail report  
**Time**: 10-15 minutes  
**Terminal**: Any terminal

### Step 4.1: Run Comprehensive Test

```bash
bash observability/09-validate-metrics.sh
```

**Expected Output Example**:

```
╔═════════════════════════════════════════════════════════════════════════╗
║              Comprehensive Metrics Endpoint Validation                  ║
╚═════════════════════════════════════════════════════════════════════════╝

TEST 1: Metrics Server Running
────────────────────────────────────────────────────────────────────────
✅ PASS: Metrics server process found

TEST 2: Port 9091 Listening
────────────────────────────────────────────────────────────────────────
✅ PASS: Port 9091 is listening

TEST 3: Endpoint Responds (HTTP 200)
────────────────────────────────────────────────────────────────────────
✅ PASS: Endpoint returns HTTP 200

TEST 4: Prometheus Format Compliance
────────────────────────────────────────────────────────────────────────
  HELP lines: 32
  TYPE lines: 32
✅ PASS: Format looks valid (≥10 HELP and TYPE lines)

TEST 5: Prometheus Scraping
────────────────────────────────────────────────────────────────────────
✅ PASS: Prometheus has 1248 metric series

TEST 6: Sample PromQL Queries
────────────────────────────────────────────────────────────────────────
Query 1: up{job='prometheus'}
  ✅ Returns 1 series

╔═════════════════════════════════════════════════════════════════════════╗
║                        VALIDATION SUMMARY                              ║
╚═════════════════════════════════════════════════════════════════════════╝

Passed: 6
Failed: 0

✅ All validation tests passed!

Metrics endpoint is fully operational and ready for use.
```

### Step 4.2: Document Results

**Record all 6 test results**:

- [ ] Test 1 - Server Running: PASS / FAIL
- [ ] Test 2 - Port Listening: PASS / FAIL
- [ ] Test 3 - HTTP 200: PASS / FAIL
- [ ] Test 4 - Format: PASS / FAIL
- [ ] Test 5 - Scraping: PASS / FAIL
- [ ] Test 6 - Queries: PASS / FAIL

**If any FAIL**:

- [ ] Document which test failed: **\*\***\_\_\_**\*\***
- [ ] Error message: **\*\***\_\_\_**\*\***
- [ ] See [Troubleshooting](#troubleshooting) section

---

## Phase 5: Documentation

**Objective**: Create validation reports and PromQL examples  
**Time**: 30-40 minutes  
**Output**: 3 documents for EXECUTION_TASK

### Step 5.1: Create Validation Report

Create file: `documentation/Metrics-Endpoint-Validation-Report-1.2.md`

```markdown
# Metrics Endpoint Validation Report - Achievement 1.2

**Date**: [TODAY'S DATE]
**Executor**: [YOUR NAME]
**Status**: ✅ COMPLETE

## Executive Summary

[Brief description of what was validated]

## Test Results Summary

### Format Verification

- Total metrics: [NUMBER]
- HELP lines: [NUMBER]
- TYPE lines: [NUMBER]
- Metrics format: ✅ Valid

### Categories Found

- Stage metrics: [NUMBER]
- Agent metrics: [NUMBER]
- Error metrics: [NUMBER]
- Total unique metrics: [NUMBER]

### Prometheus Integration

- Target health: UP
- Last scrape time: [TIME]
- Query execution: ✅ Success

## Metrics Categories Verified

### Stage Metrics

- stage_started
- stage_completed
- stage_failed
- stage_duration_seconds
- documents_processed

### Agent Metrics

- agent_llm_calls
- agent_llm_errors
- agent_llm_duration_seconds
- agent_tokens_used
- agent_llm_cost_usd

## Issues Encountered

[List any issues found, or write "None" if all clear]

## Resolutions Applied

[List resolutions applied]

## Recommendations

1. Metrics endpoint is stable
2. Prometheus scraping is working
3. Ready for production use

## Conclusion

✅ All validation tests passed. Metrics endpoint is fully operational.
```

### Step 5.2: Create PromQL Examples Document

Create file: `documentation/PromQL-Examples-Achievement-1.2.md`

Test these PromQL queries in Prometheus UI and document results:

```bash
# Test each query in http://localhost:9090/graph

# 1. Basic up check
up{job="prometheus"}

# 2. Stage metrics
stage_started{stage="extraction"}
stage_completed{stage="extraction"}
stage_failed{stage="extraction"}

# 3. Rate queries (if data available)
rate(stage_completed[1m])
rate(agent_llm_calls[1m])

# 4. Sum queries
sum(documents_processed)
sum by (stage) (documents_processed)

# 5. Duration queries
avg(stage_duration_seconds)
max(stage_duration_seconds)

# 6. Error rates
rate(stage_failed[1m])
rate(agent_llm_errors[1m])

# 7. Agent metrics
agent_llm_calls{agent="gpt-4"}
sum by (agent) (agent_llm_calls)

# 8. Token usage
sum(agent_tokens_used)
sum by (token_type) (agent_tokens_used)

# 9. Cost tracking
sum(agent_llm_cost_usd)
sum by (agent) (agent_llm_cost_usd)

# 10. Custom calculations
rate(stage_completed[5m]) * 60  # per minute
sum(documents_processed) / sum(stage_started)  # success rate
```

**For each query you test successfully, document**:

````markdown
# PromQL Query Examples - Achievement 1.2

**Date**: [TODAY]
**Tested In**: Prometheus UI (http://localhost:9090/graph)

## Query 1: Basic System Health

```promql
up{job="prometheus"}
```
````

**Description**: Check if Prometheus itself is up  
**Expected Result**: Returns 1 (up and healthy)  
**Actual Result**: ✅ Returns 1

## Query 2: Stage Started Count

```promql
stage_started{stage="extraction"}
```

**Description**: Count of extraction stage starts  
**Expected Result**: Positive number  
**Actual Result**: ✅ [NUMBER]

[Continue for each query...]

````

### Step 5.3: Create Debug Log

Create file: `documentation/Metrics-Validation-Debug-Log-1.2.md`

```markdown
# Debug Log - Achievement 1.2 Execution

**Start Time**: [TIME]
**End Time**: [TIME]
**Executor**: [YOUR NAME]

## Phase 1: Code Review & Server Start
- Started: [TIME]
- Completed: [TIME]
- Issues: None / [describe]
- Output: [Any notable output]

## Phase 2: Format Validation
- Started: [TIME]
- Completed: [TIME]
- Metrics lines: [NUMBER]
- HELP lines: [NUMBER]
- TYPE lines: [NUMBER]
- Issues: None / [describe]

## Phase 3: Prometheus Scraping
- Started: [TIME]
- Completed: [TIME]
- Container access: ✅ / ❌
- Target health: UP / DOWN
- Query success: ✅ / ❌
- Issues: None / [describe]

## Phase 4: Comprehensive Validation
- Tests passed: [6/6 or other]
- Failed tests: None / [list]
- Issues: None / [describe]

## Troubleshooting Notes

[Any troubleshooting you had to do]

## Learnings

[What you learned about metrics and observability]

## Network Notes

- Prometheus container can reach metrics: ✅ / ❌
- Metrics server responding: ✅ / ❌
- Port 9091 accessible: ✅ / ❌
- Docker network working: ✅ / ❌
````

---

## Troubleshooting

### Issue: Metrics server won't start

**Symptoms**: Script 06 fails or server crashes immediately

**Solutions**:

```bash
# Check if port 9091 is already in use
lsof -i :9091

# Kill any existing process on port 9091
kill -9 [PID]

# Try starting with verbose output
python -u app/api/metrics.py 9091 2>&1 | tee /tmp/metrics-startup.log

# Check the error log
cat /tmp/metrics-startup.log
```

**Common Causes**:

- Port already in use (check `lsof -i :9091`)
- Python environment issue (check `python --version`)
- Missing dependencies (check imports in `app/api/metrics.py`)

---

### Issue: Metrics endpoint not responding

**Symptoms**: Script 07 fails with connection error

**Solutions**:

```bash
# Verify server is running
ps aux | grep metrics.py

# Test endpoint manually
curl http://localhost:9091/metrics

# Check if port is listening
netstat -tuln | grep 9091
```

**Common Causes**:

- Server crashed (check logs)
- Server not started yet
- Port not listening (firewall issue)

---

### Issue: Prometheus not scraping metrics

**Symptoms**: Script 08 shows "Prometheus not yet scraping"

**Solutions**:

```bash
# Wait for next scrape interval (default 15 seconds)
sleep 30

# Check Prometheus logs
docker logs youtuberag-prometheus | tail -20

# Test from container
docker exec youtuberag-prometheus curl http://localhost:9091/metrics

# Verify config has the target
cat observability/prometheus/prometheus.yml | grep -A5 "9091"
```

**Common Causes**:

- Prometheus hasn't scraped yet (wait a minute)
- Container network issue
- Prometheus config missing target
- Prometheus not running

---

### Issue: PromQL queries return empty results

**Symptoms**: Queries execute but return no data

**Solutions**:

```bash
# May need pipeline to run to generate data
# Try basic query first:
up{job="prometheus"}

# Wait for metrics to accumulate
sleep 60

# Check if Prometheus has any metrics
curl 'http://localhost:9090/api/v1/query?query=up'
```

**Common Causes**:

- No data yet (need to run pipeline)
- Metrics not scraped yet
- Time range issue in Prometheus UI

---

## Completion Checklist

**Final verification before marking complete**:

### Prerequisites Met

- [ ] Docker containers running
- [ ] Prometheus accessible
- [ ] Scripts created and executable
- [ ] Project root verified

### Phases Executed

- [ ] Phase 1: Code review completed
- [ ] Phase 1: Metrics server started successfully
- [ ] Phase 2: Format validation passed
- [ ] Phase 3: Prometheus scraping verified
- [ ] Phase 4: Comprehensive validation completed
- [ ] All 6 tests passed (or documented failures)

### Documentation Created

- [ ] Validation Report created
- [ ] PromQL Examples (10+ queries) tested and documented
- [ ] Debug Log created

### Deliverables Complete

- [ ] All 3 documentation files in `documentation/` folder
- [ ] All findings recorded in files
- [ ] No outstanding issues

### Final Status

- [ ] Mark EXECUTION_TASK as complete
- [ ] Add Learning Summary to EXECUTION_TASK
- [ ] Update project plan with completion time
- [ ] All deliverables verified

---

## Next Steps After Completion

1. **Review deliverables** in `documentation/` folder
2. **Update EXECUTION_TASK**:
   - Add Learning Summary
   - Mark as ✅ COMPLETE
   - Record actual time spent
3. **Update main PLAN**:

   - Mark Achievement 1.2 as complete
   - Update completion statistics

4. **Optional**: Create Grafana dashboard using the validated metrics

---

## Quick Reference

### Command Summary

```bash
# Phase 1: Review & Start
bash observability/06-review-metrics-code.sh

# Phase 2: Validate Format
bash observability/07-validate-metrics-format.sh

# Phase 3: Test Scraping
bash observability/08-test-prometheus-scraping.sh

# Phase 4: Comprehensive
bash observability/09-validate-metrics.sh

# View saved metrics
cat /tmp/metrics.txt | head -50

# View Prometheus UI
# http://localhost:9090

# View Grafana UI
# http://localhost:3000
```

### Key Ports

- Metrics server: `http://localhost:9091/metrics`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`
- Loki: `http://localhost:3100`

### Key Files

- Metrics implementation: `app/api/metrics.py`
- Prometheus metrics: `business/services/observability/prometheus_metrics.py`
- Prometheus config: `observability/prometheus/prometheus.yml`
- Scripts: `observability/0[6-9]-*.sh`

---

## Support

If you encounter issues not covered in [Troubleshooting](#troubleshooting):

1. **Check error messages carefully**
2. **Review logs**:
   ```bash
   docker logs youtuberag-prometheus
   docker logs youtuberag-loki
   cat /tmp/metrics-startup.log
   ```
3. **Run comprehensive validation**:
   ```bash
   bash observability/09-validate-metrics.sh
   ```
4. **Document your findings** for later analysis

---

**Ready to begin? Start with Phase 1:**

```bash
cd /Users/fernandobarroso/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG
bash observability/06-review-metrics-code.sh
```

Good luck! 🚀
