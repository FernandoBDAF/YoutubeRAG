# Validation Workflow Guide

**Date**: 2025-11-14  
**Based On**: EXECUTION_CASE-STUDY_OBSERVABILITY-INFRASTRUCTURE-VALIDATION.md  
**Purpose**: Step-by-step guide for validating infrastructure components like observability stack

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Pre-Validation Setup](#pre-validation-setup)
3. [Step-by-Step Validation Process](#step-by-step-validation-process)
4. [Issue Debugging Strategies](#issue-debugging-strategies)
5. [Success Measurement](#success-measurement)
6. [Common Issues & Solutions](#common-issues--solutions)
7. [Validation Checklist](#validation-checklist)

---

## 🎯 Overview

### When to Use This Guide

Use this guide when validating:
- Infrastructure deployments (Docker services, databases)
- Integration points (between components, with existing code)
- Configuration changes (new settings, feature flags)
- Performance impacts (before/after comparisons)
- Data quality (transformations, calculations)

### Key Principles

1. **Automated First**: Use scripts for objective, repeatable tests
2. **Real Data**: Always validate with production-like data
3. **Systematic**: Follow structured process, not ad-hoc testing
4. **Documented**: Record all findings immediately
5. **Actionable**: Each finding should lead to clear action

---

## 🔧 Pre-Validation Setup

### Step 1: Environment Preparation

```bash
# 1. Create validation workspace
mkdir -p validation-work/{scripts,reports,data}
cd validation-work

# 2. Check prerequisites
- Docker installed and running (docker --version)
- Docker Compose installed (docker-compose --version)
- Database access (MongoDB, etc.)
- Required ports available (9090, 3000, 3100, etc.)
- Adequate disk space (50+ GB recommended)

# 3. Backup production data
- Create database snapshot before testing
- Document baseline metrics
- Save original configurations

# 4. Prepare test data
- Identify representative test dataset (100-1000 records)
- Production-like volume and complexity
- Document test data characteristics
```

### Step 2: Create Validation Plan

```markdown
# Validation Plan: [Component]

## What We're Validating
- [Feature 1]
- [Feature 2]
- [Feature 3]

## Success Criteria
- Criterion 1
- Criterion 2
- Criterion 3

## Test Strategy
- Automated tests: [script names]
- Manual verification: [steps]
- Performance tests: [benchmarks]

## Timeline
- Phase 1: [duration]
- Phase 2: [duration]
- Phase 3: [duration]

## Team & Approval
- Executor: [name]
- Reviewer: [name]
```

### Step 3: Document Baseline

```bash
# Before making any changes, capture current state
docker ps -a  # Service status
docker stats  # Resource usage
db_stats.sh   # Database statistics
network_health.sh  # Network connectivity
config_audit.sh    # Configuration audit
```

---

## 📍 Step-by-Step Validation Process

### Phase 1: Setup & Pre-Flight Checks (30-45 min)

**Objective**: Ensure environment is ready for validation

**Step 1.1: Verify Prerequisites**
```bash
# Create pre-flight check script
cat > preflight-checks.sh << 'EOF'
#!/bin/bash
echo "🔍 Pre-Flight Validation Checks"
echo "================================"

# Check Docker
echo -n "Docker installed: "
if command -v docker &> /dev/null; then echo "✅"; else echo "❌"; fi

# Check Docker running
echo -n "Docker daemon running: "
if docker ps &> /dev/null; then echo "✅"; else echo "❌"; fi

# Check ports
for port in 9090 3000 3100; do
  echo -n "Port $port available: "
  if ! nc -z localhost $port 2>/dev/null; then echo "✅"; else echo "❌"; fi
done

# Check disk space
echo -n "Disk space (50GB+): "
available=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$available" -ge 50 ]; then echo "✅"; else echo "❌"; fi

echo "================================"
echo "Pre-flight checks complete"
EOF

chmod +x preflight-checks.sh
./preflight-checks.sh
```

**Step 1.2: Document Current State**
- Take snapshots of all systems
- Record current metrics
- Save configuration copies
- Document any known issues

**Step 1.3: Prepare Test Environment**
```bash
# Set up isolated environment
export VALIDATION_ENV=true
export VALIDATION_PREFIX="test_"
export LOG_LEVEL=DEBUG

# Create isolated data copies
cp production_config.json validation_config.json
# Modify for validation (different database, prefixed collections)
```

---

### Phase 2: Deploy & Configure (30-45 min)

**Objective**: Stand up infrastructure with comprehensive automation

**Step 2.1: Create Deployment Scripts**
```bash
# Standard deployment script structure
cat > deploy.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting Deployment"

# Step 1: Pull latest images
echo "📦 Pulling images..."
docker-compose pull

# Step 2: Start services
echo "🔧 Starting services..."
docker-compose up -d

# Step 3: Wait for health
echo "⏳ Waiting for services to be healthy..."
for i in {1..30}; do
  if docker-compose ps | grep -q "healthy\|running"; then
    echo "✅ Services healthy"
    break
  fi
  sleep 2
  echo -n "."
done

echo "🎉 Deployment complete"
EOF

chmod +x deploy.sh
./deploy.sh
```

**Step 2.2: Verify Service Status**
```bash
# Check all services operational
docker-compose ps
# Expected: All services "Up" or "healthy"

# Test each service
curl http://localhost:9090  # Prometheus
curl http://localhost:3000  # Grafana
curl http://localhost:3100  # Loki
```

**Step 2.3: Configure Integrations**
```bash
# Add data sources to Grafana
curl -X POST http://localhost:3000/api/datasources \
  -H "Content-Type: application/json" \
  -d '{"name":"Prometheus","type":"prometheus","url":"http://prometheus:9090"}'

# Verify configuration
curl http://localhost:3000/api/datasources
```

---

### Phase 3: Functional Testing (45-60 min)

**Objective**: Verify all components work correctly

**Step 3.1: Create Test Suite**
```bash
# Example: Metrics validation tests
cat > test-metrics.sh << 'EOF'
#!/bin/bash

test_count=0
pass_count=0
fail_count=0

# Test 1: Prometheus metrics endpoint
test_count=$((test_count + 1))
echo -n "Test 1: Prometheus metrics endpoint... "
if curl -s http://localhost:9090/metrics | grep -q "prometheus_http_requests_total"; then
  echo "✅ PASS"
  pass_count=$((pass_count + 1))
else
  echo "❌ FAIL"
  fail_count=$((fail_count + 1))
fi

# Test 2: Grafana dashboards
test_count=$((test_count + 1))
echo -n "Test 2: Grafana dashboards loaded... "
if curl -s http://localhost:3000/api/dashboards/db/observability | grep -q '"title"'; then
  echo "✅ PASS"
  pass_count=$((pass_count + 1))
else
  echo "❌ FAIL"
  fail_count=$((fail_count + 1))
fi

# Test 3: Loki log ingestion
test_count=$((test_count + 1))
echo -n "Test 3: Loki log ingestion... "
if curl -s http://localhost:3100/ready | grep -q "ready"; then
  echo "✅ PASS"
  pass_count=$((pass_count + 1))
else
  echo "❌ FAIL"
  fail_count=$((fail_count + 1))
fi

echo ""
echo "Results: $pass_count/$test_count tests passed"
[ $fail_count -eq 0 ] && exit 0 || exit 1
EOF

chmod +x test-metrics.sh
./test-metrics.sh
```

**Step 3.2: Test Data Collection**
```bash
# Generate test load
python generate_metrics.py --duration 5 --frequency 1000

# Verify metrics collected
curl -s http://localhost:9090/api/v1/query?query=test_metric_total | python -m json.tool
```

**Step 3.3: Verify Integration**
```bash
# Check end-to-end flow
echo "Testing: Metrics → Prometheus → Grafana"

# 1. Generate metric
python -c "from prometheus_client import Counter; c = Counter('test_e2e', 'E2E test'); c.inc()"

# 2. Verify in Prometheus
curl -s "http://localhost:9090/api/v1/query?query=test_e2e" | grep "value"

# 3. Query in Grafana
curl -s http://localhost:3000/api/datasources/1/query --data '{"targets":[{"expr":"test_e2e"}]}'
```

---

### Phase 4: Issue Investigation & Resolution (60-90 min)

**Objective**: Debug and fix any issues discovered

**Step 4.1: Systematic Debugging**
```bash
# When a test fails, follow this process:

# 1. Reproduce the issue
echo "Reproducing issue..."
[run failing test]

# 2. Check logs for errors
echo "Checking logs..."
docker-compose logs --tail=100 [service]

# 3. Verify configuration
echo "Verifying configuration..."
docker inspect [service]

# 4. Test dependencies
echo "Testing dependencies..."
curl -v http://service-name:port/health

# 5. Check resource usage
echo "Checking resources..."
docker stats [service]
```

**Step 4.2: Common Issues & Solutions**

*See "Common Issues & Solutions" section below*

**Step 4.3: Document Findings**
```bash
# Create issue report
cat > issue-report.md << 'EOF'
## Issue Report

**Issue**: [Description]
**Severity**: [Critical/High/Medium/Low]
**Found During**: [Test phase/Step]
**Root Cause**: [Analysis]
**Resolution**: [Fix applied]
**Time to Resolve**: [Duration]
**Lessons Learned**: [What we learned]

### Evidence
- Logs: [attached]
- Configuration: [attached]
- Reproduction steps: [listed]
EOF
```

---

### Phase 5: Performance Testing (30-45 min)

**Objective**: Verify performance meets requirements

**Step 5.1: Baseline Testing**
```bash
# Measure baseline performance
time python run-pipeline.py --size small
time python run-pipeline.py --size medium
time python run-pipeline.py --size large

# Capture metrics
- Duration per stage
- Throughput (items/sec)
- Resource utilization
- Error rates
```

**Step 5.2: Comparison Testing**
```bash
# Compare with previous version
before=$(time python run-pipeline.py --old-version)
after=$(time python run-pipeline.py --new-version)

# Calculate impact
impact=$(bc <<< "scale=2; ($after - $before) / $before * 100")
echo "Performance impact: ${impact}%"
```

**Step 5.3: Scalability Testing**
```bash
# Test with increasing load
for size in 100 1000 10000; do
  echo "Testing with $size items..."
  time python run-pipeline.py --size $size --observations results-$size.json
done

# Create performance report
python analyze_performance.py results-*.json
```

---

## 🔍 Issue Debugging Strategies

### Strategy 1: Layered Debugging

```
Level 1: Container Level
  - Is service running? (docker ps)
  - Check logs (docker logs)
  - Check health (docker inspect)

Level 2: Process Level
  - Is process running? (ps aux | grep)
  - CPU/Memory usage? (top, htop)
  - File handles? (lsof)

Level 3: Network Level
  - Port listening? (netstat -tlnp)
  - DNS resolving? (nslookup)
  - Connectivity? (nc, curl)

Level 4: Data Level
  - Database accessible? (mongo shell)
  - Tables exist? (show tables)
  - Data present? (count documents)

Level 5: Application Level
  - Configuration loaded? (echo config)
  - Logs show what? (tail -f)
  - Metrics exposed? (curl /metrics)
```

### Strategy 2: Isolation Testing

```bash
# Test each component independently
# Component 1: Database
mongo --host localhost --port 27017 --eval "db.adminCommand('ping')"

# Component 2: Message Queue (if used)
rabbitmq-diagnostics -q ping

# Component 3: API Service
curl -v http://localhost:8000/health

# Component 4: Web Dashboard
curl -v http://localhost:3000/

# Only when all pass, test integration
```

### Strategy 3: Hypothesis-Driven Investigation

```
1. Observe the problem
   "Service X is failing"

2. Form hypothesis
   "Hypothesis: Database connection timeout"

3. Design test
   "Test: Query database directly with explicit timeout"

4. Run test
   "mongo --connect-timeout 5000 ..."

5. Evaluate result
   - Hypothesis confirmed → Apply fix
   - Hypothesis rejected → Form new hypothesis

6. Repeat until resolved
```

---

## 📊 Success Measurement

### Success Criteria Template

```markdown
# Success Criteria: [Component]

## Functional Success
- [ ] All services deployed and running
- [ ] All services respond to health checks
- [ ] All integrations operational
- [ ] All features tested and working

## Performance Success
- [ ] Latency < [target] ms (p99)
- [ ] Throughput > [target] items/sec
- [ ] Error rate < [target] %
- [ ] Resource utilization acceptable

## Data Quality Success
- [ ] No data corruption
- [ ] Data consistency verified
- [ ] Calculations accurate
- [ ] Query results correct

## Documentation Success
- [ ] All findings documented
- [ ] All issues tracked
- [ ] All resolutions verified
- [ ] Case study completed
```

### Validation Report Template

```markdown
# Validation Report: [Component]

## Executive Summary
- Status: [PASS/FAIL/PARTIAL]
- Tests Run: X
- Tests Passed: Y
- Tests Failed: Z
- Issues Found: N
- Issues Resolved: M

## Test Results
- [Category 1]: X/Y passed
- [Category 2]: X/Y passed
- [Category 3]: X/Y passed

## Issues & Resolutions
1. [Issue 1] → [Resolution]
2. [Issue 2] → [Resolution]

## Performance Metrics
- Metric 1: [Value]
- Metric 2: [Value]

## Recommendations
- [Recommendation 1]
- [Recommendation 2]

## Sign-Off
- Validated By: [Name]
- Date: [Date]
- Status: [APPROVED/APPROVED_WITH_RESERVATIONS/REJECTED]
```

---

## 🚨 Common Issues & Solutions

### Issue 1: Port Already in Use

**Symptom**: `Error: Address already in use`

**Debug Process**:
```bash
# Find what's using the port
sudo lsof -i :9090

# Stop the conflicting service
sudo kill -9 [PID]

# Or use different port
sed -i 's/9090/9091/g' docker-compose.yml
```

**Prevention**: Pre-flight check script to verify ports

---

### Issue 2: Docker Image Pull Fails

**Symptom**: `Error pulling image: net/http: TLS handshake timeout`

**Debug Process**:
```bash
# Check internet connectivity
ping 8.8.8.8

# Check Docker registry connectivity
curl -I https://registry-1.docker.io

# Check Docker configuration
docker info | grep -A 5 "Registry"
```

**Prevention**: Pull images during setup phase with retry logic

---

### Issue 3: Service Won't Start

**Symptom**: `Container exits immediately with code 1`

**Debug Process**:
```bash
# Check logs for error message
docker logs [container_name] --tail=50

# Check configuration mounting
docker inspect [container_name] | grep -A 5 "Mounts"

# Verify config file format
cat config.yml | yamllint -

# Test service startup in foreground
docker-compose run --rm [service] /bin/bash
```

**Prevention**: Validate configuration before deployment

---

### Issue 4: Metrics Not Appearing

**Symptom**: `Dashboard shows no data`

**Debug Process**:
```bash
# Check if metrics are being generated
curl http://localhost:9090/metrics | head -20

# Check if Prometheus is scraping
curl http://localhost:9090/api/v1/targets

# Check query in Prometheus UI
# Navigate to: http://localhost:9090/graph
# Query: up (should show all targets)

# Check metric name
curl 'http://localhost:9090/api/v1/query?query=metric_name'
```

**Prevention**: Generate test metrics during setup

---

### Issue 5: High Latency

**Symptom**: `Queries taking >10 seconds`

**Debug Process**:
```bash
# Check database indexes
db.collection.getIndexes()

# Check query execution plan
db.collection.find({}).explain("executionStats")

# Check resource usage
docker stats [container]

# Check for locks
db.currentOp()
```

**Prevention**: Create required indexes during setup

---

## ✅ Validation Checklist

### Pre-Validation Phase
- [ ] Environment documented
- [ ] Baseline metrics captured
- [ ] Test data prepared
- [ ] Validation plan reviewed
- [ ] Team notified
- [ ] Approval obtained

### Deployment Phase
- [ ] Pre-flight checks passed (6/6)
- [ ] Services deployed
- [ ] Service health verified
- [ ] Integrations configured
- [ ] Deployment logs captured

### Testing Phase
- [ ] Functional tests defined
- [ ] Test scripts created
- [ ] Functional tests run (100% pass)
- [ ] Integration tests run (100% pass)
- [ ] Performance tests run (targets met)

### Issue Resolution Phase
- [ ] All issues documented
- [ ] All issues investigated
- [ ] All critical issues resolved
- [ ] All non-critical issues logged

### Performance Phase
- [ ] Baseline measured
- [ ] Performance tests run
- [ ] Bottlenecks identified
- [ ] Optimization applied

### Documentation Phase
- [ ] Findings documented
- [ ] Case study created
- [ ] Troubleshooting guide updated
- [ ] Best practices extracted

### Sign-Off Phase
- [ ] Validation report reviewed
- [ ] Quality criteria met
- [ ] Stakeholder approval obtained
- [ ] Results communicated
- [ ] Lessons learned captured

---

## 📖 Quick Reference

### Essential Commands

```bash
# Health checks
docker-compose ps                    # Service status
docker-compose logs [service]        # Service logs
docker-compose exec [service] bash   # Service shell

# Data inspection
mongo shell                          # MongoDB CLI
curl http://localhost:PORT/metrics   # Metrics endpoint

# Performance testing
time python script.py                # Duration
docker stats                         # Resource usage

# Network debugging
netstat -tlnp                        # Open ports
curl -v http://service:port          # HTTP debugging
nslookup service                     # DNS resolution
```

### Key Files

- `docker-compose.yml` - Service definitions
- `config.yml` - Application configuration
- `tests/*.sh` - Test scripts
- `results/` - Test results directory
- `reports/` - Generated reports

---

**Guide Created**: 2025-11-14  
**Based On**: Actual observability validation experience  
**Status**: Ready for Reference & Future Validation Work

