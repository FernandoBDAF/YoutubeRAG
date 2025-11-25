# Production Deployment Guide

**Achievement**: 7.3 - Production Readiness Package  
**Purpose**: Step-by-step guide for deploying GraphRAG observability infrastructure to production  
**Last Updated**: 2025-11-15

---

## Overview

This guide provides detailed procedures for deploying the GraphRAG observability infrastructure to production. Follow all steps in order to ensure a successful deployment.

**Deployment Strategy**: Phased rollout (Staging → Pilot → Full Production)

**Estimated Timeline**:
- Pre-deployment preparation: 1-2 days
- Staging deployment: 1 day
- Pilot deployment: 3-5 days
- Full production rollout: 1 week

---

## Prerequisites

### Required Access

- [ ] MongoDB production cluster access (admin rights for setup, read/write for application)
- [ ] Production server/container access (SSH or kubectl)
- [ ] Docker Hub or container registry access
- [ ] Cloud provider access (AWS, GCP, Azure as applicable)
- [ ] Monitoring system access (Prometheus, Grafana)

### Required Knowledge

- [ ] Familiarity with GraphRAG pipeline architecture
- [ ] MongoDB administration basics
- [ ] Docker and Docker Compose
- [ ] Environment-specific deployment procedures (Kubernetes, EC2, etc.)
- [ ] Basic troubleshooting skills

### Pre-Deployment Checklist

- [ ] Production-Readiness-Checklist.md completed (90%+ on critical items)
- [ ] All validation scripts passing in staging environment
- [ ] Stakeholders informed of deployment schedule
- [ ] Rollback plan reviewed and understood
- [ ] On-call team briefed and available

---

## Section 1: Pre-Deployment Preparation

### 1.1 Environment Configuration

**Step 1: Create Environment File**

Create `/opt/graphrag/.env` (or appropriate location):

```bash
# Core Configuration
GRAPHRAG_DB_URI=mongodb://graphrag_user:PASSWORD@mongodb.production.internal:27017/graphrag_production?authSource=admin
GRAPHRAG_DB_NAME=graphrag_production
OPENAI_API_KEY=sk-prod-xxxxxxxxxxxxxx

# Observability Configuration (Production Recommended)
GRAPHRAG_ENABLE_OBSERVABILITY=true
GRAPHRAG_TRANSFORMATION_LOGGING=true
GRAPHRAG_QUALITY_METRICS=true
GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
GRAPHRAG_PROMETHEUS_METRICS=true

# Performance Settings (Achievement 7.2)
GRAPHRAG_LOGGING_BATCH_SIZE=100
GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=7

# Application Settings
PYTHON_ENV=production
LOG_LEVEL=INFO
```

**Step 2: Secure Environment File**

```bash
chmod 600 /opt/graphrag/.env
chown graphrag:graphrag /opt/graphrag/.env
```

### 1.2 Database Setup

**Step 1: Create Database and User**

Connect to MongoDB as admin:

```javascript
use admin

// Create application user
db.createUser({
  user: "graphrag_user",
  pwd: "STRONG_PASSWORD_HERE",
  roles: [
    { role: "readWrite", db: "graphrag_production" }
  ]
})

// Create database
use graphrag_production

// Verify access
db.runCommand({ connectionStatus: 1 })
```

**Step 2: Create Indexes**

Run index creation script:

```bash
# From GraphRAG repository root
python scripts/setup/create_indexes.py --env production
```

Or manually create indexes (see Production-Readiness-Checklist.md Section 3.2).

**Step 3: Verify Database Setup**

```bash
# Test connection
mongosh "mongodb://graphrag_user:PASSWORD@mongodb.production.internal:27017/graphrag_production?authSource=admin" --eval "db.runCommand({ ping: 1 })"

# Verify indexes
mongosh "mongodb://graphrag_user:PASSWORD@mongodb.production.internal:27017/graphrag_production?authSource=admin" --eval "db.transformation_logs.getIndexes()"
```

### 1.3 Observability Stack Deployment

**Step 1: Deploy Docker Compose Stack**

```bash
# Navigate to observability directory
cd /opt/graphrag/observability

# Review docker-compose.yml
cat docker-compose.yml

# Deploy stack
docker-compose up -d

# Verify all containers running
docker-compose ps
```

**Step 2: Verify Services**

```bash
# Check Prometheus
curl http://localhost:9090/-/healthy

# Check Grafana
curl http://localhost:3000/api/health

# Check Loki
curl http://localhost:3100/ready
```

**Step 3: Import Grafana Dashboards**

```bash
# Import dashboards
curl -X POST http://admin:admin@localhost:3000/api/dashboards/import \
  -H "Content-Type: application/json" \
  -d @grafana/dashboards/graphrag-overview.json

curl -X POST http://admin:admin@localhost:3000/api/dashboards/import \
  -H "Content-Type: application/json" \
  -d @grafana/dashboards/pipeline-performance.json
```

---

## Section 2: Staging Deployment

### 2.1 Deploy to Staging

**Purpose**: Validate deployment procedures and configuration in staging environment before production.

**Step 1: Deploy Application**

```bash
# Pull latest code
cd /opt/graphrag
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Run database migrations (if any)
python scripts/setup/migrate.py --env staging
```

**Step 2: Start Application**

```bash
# Start GraphRAG application
systemctl start graphrag

# Or if using Docker
docker-compose -f docker-compose.staging.yml up -d
```

**Step 3: Verify Deployment**

```bash
# Check application logs
tail -f /var/log/graphrag/application.log

# Verify observability
curl http://localhost:8080/health
curl http://localhost:8080/metrics
```

### 2.2 Run Validation Tests

**Step 1: Execute Sample Pipeline**

```bash
# Run test pipeline with observability enabled
python -m business.pipelines.graphrag.main \
  --video-id test-video-001 \
  --chunk-count 10

# Monitor execution
tail -f /var/log/graphrag/application.log | grep "test-video-001"
```

**Step 2: Verify Data in MongoDB**

```bash
mongosh "mongodb://graphrag_user:PASSWORD@mongodb.staging.internal:27017/graphrag_staging?authSource=admin"

// Check transformation logs
db.transformation_logs.countDocuments({ video_id: "test-video-001" })

// Check quality metrics
db.graphrag_runs.find({ video_id: "test-video-001" }).pretty()
```

**Step 3: Verify Metrics in Grafana**

- Navigate to Grafana (http://grafana.staging.internal:3000)
- Open "GraphRAG Overview" dashboard
- Verify metrics appear for test run
- Check for any errors or anomalies

### 2.3 Performance Validation

**Step 1: Measure Baseline Performance**

```bash
# Run pipeline without observability
GRAPHRAG_ENABLE_OBSERVABILITY=false python -m business.pipelines.graphrag.main \
  --video-id baseline-test \
  --chunk-count 50

# Record execution time
```

**Step 2: Measure Observability Performance**

```bash
# Run pipeline with observability
GRAPHRAG_ENABLE_OBSERVABILITY=true python -m business.pipelines.graphrag.main \
  --video-id observability-test \
  --chunk-count 50

# Record execution time
```

**Step 3: Calculate Overhead**

```
Overhead % = ((Observability Time - Baseline Time) / Baseline Time) × 100

Target: < 5% overhead
Acceptable: < 10% overhead
Investigate if: > 10% overhead
```

### 2.4 Staging Sign-Off

- [ ] All validation tests pass
- [ ] Performance overhead within acceptable limits
- [ ] No critical errors in logs
- [ ] Metrics appear correctly in Grafana
- [ ] Team confident in deployment procedures

**Decision Point**: Go/No-Go for Pilot Deployment

---

## Section 3: Pilot Deployment (Production Subset)

### 3.1 Pilot Strategy

**Scope**: 10-20% of production traffic for 3-5 days

**Selection Criteria**:
- Non-critical pipelines or videos
- Representative workload
- Easy to monitor and rollback

**Pilot Configuration**:

```bash
# Enable observability for pilot subset only
GRAPHRAG_ENABLE_OBSERVABILITY=true
GRAPHRAG_PILOT_MODE=true
GRAPHRAG_PILOT_SAMPLE_RATE=0.15  # 15% of traffic
```

### 3.2 Deploy Pilot

**Step 1: Update Production Configuration**

```bash
# Edit production .env file
nano /opt/graphrag/.env

# Add pilot settings
GRAPHRAG_PILOT_MODE=true
GRAPHRAG_PILOT_SAMPLE_RATE=0.15
```

**Step 2: Deploy Updated Configuration**

```bash
# Reload configuration (method depends on deployment)
systemctl reload graphrag

# Or restart containers
docker-compose restart graphrag
```

**Step 3: Verify Pilot Active**

```bash
# Check logs for pilot mode confirmation
grep "Pilot mode enabled" /var/log/graphrag/application.log

# Verify sample rate
curl http://localhost:8080/config | jq '.pilot'
```

### 3.3 Monitor Pilot

**Day 1-2: Intensive Monitoring**

Every 2-4 hours:
- [ ] Check Grafana dashboards for anomalies
- [ ] Review error logs
- [ ] Monitor performance metrics
- [ ] Check storage growth rate
- [ ] Verify data quality

**Day 3-5: Standard Monitoring**

Daily:
- [ ] Review daily metrics summary
- [ ] Check for any alerts
- [ ] Analyze pilot data vs baseline
- [ ] Gather stakeholder feedback

### 3.4 Pilot Evaluation

**Success Criteria**:
- [ ] No critical production incidents
- [ ] Performance overhead < 5%
- [ ] Storage growth within projections
- [ ] Quality metrics show expected values
- [ ] No data loss or corruption
- [ ] Team confidence high

**Decision Point**: Go/No-Go for Full Production Rollout

---

## Section 4: Full Production Rollout

### 4.1 Rollout Plan

**Phase 1 (Day 1)**: 25% of production traffic
**Phase 2 (Day 2-3)**: 50% of production traffic
**Phase 3 (Day 4-5)**: 75% of production traffic
**Phase 4 (Day 6-7)**: 100% of production traffic

### 4.2 Phase 1: 25% Rollout

**Step 1: Update Configuration**

```bash
# Edit .env
GRAPHRAG_PILOT_MODE=true
GRAPHRAG_PILOT_SAMPLE_RATE=0.25
```

**Step 2: Deploy and Monitor**

```bash
# Reload/restart
systemctl reload graphrag

# Monitor for 24-48 hours
```

**Step 3: Validation Checkpoint**

- [ ] Performance stable
- [ ] No error rate increase
- [ ] Metrics look healthy

### 4.3 Phase 2: 50% Rollout

Repeat Phase 1 steps with `GRAPHRAG_PILOT_SAMPLE_RATE=0.50`

### 4.4 Phase 3: 75% Rollout

Repeat Phase 1 steps with `GRAPHRAG_PILOT_SAMPLE_RATE=0.75`

### 4.5 Phase 4: 100% Rollout (Full Production)

**Step 1: Enable for All Traffic**

```bash
# Edit .env - disable pilot mode
GRAPHRAG_PILOT_MODE=false
GRAPHRAG_ENABLE_OBSERVABILITY=true
GRAPHRAG_TRANSFORMATION_LOGGING=true
GRAPHRAG_QUALITY_METRICS=true
GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
GRAPHRAG_PROMETHEUS_METRICS=true
```

**Step 2: Deploy Full Configuration**

```bash
systemctl reload graphrag
# Or restart containers
docker-compose restart graphrag
```

**Step 3: Verify Full Deployment**

```bash
# Check configuration
curl http://localhost:8080/config | jq '.observability'

# Verify all pipelines using observability
grep "Observability enabled" /var/log/graphrag/application.log | wc -l
```

### 4.6 Post-Deployment Verification

**24-Hour Intensive Monitoring**:
- [ ] All metrics stable
- [ ] No performance degradation
- [ ] Error rates normal
- [ ] Storage growing as expected
- [ ] Quality metrics consistent

**48-Hour Extended Monitoring**:
- [ ] System stability confirmed
- [ ] No anomalies detected
- [ ] Team trained and confident
- [ ] Stakeholders satisfied

---

## Section 5: Configuration Management

### 5.1 Environment-Specific Settings

**Development**:
```bash
GRAPHRAG_ENABLE_OBSERVABILITY=true
GRAPHRAG_SAVE_INTERMEDIATE_DATA=true  # For debugging
GRAPHRAG_LOGGING_BATCH_SIZE=10  # Smaller batches for faster feedback
```

**Staging**:
```bash
GRAPHRAG_ENABLE_OBSERVABILITY=true
GRAPHRAG_SAVE_INTERMEDIATE_DATA=true  # For validation
GRAPHRAG_LOGGING_BATCH_SIZE=50
```

**Production**:
```bash
GRAPHRAG_ENABLE_OBSERVABILITY=true
GRAPHRAG_SAVE_INTERMEDIATE_DATA=false  # Performance optimization
GRAPHRAG_LOGGING_BATCH_SIZE=100  # Optimal performance
```

### 5.2 Feature Toggle Reference

From Achievement 5.3 (Production-Recommendations.md):

| Feature | Dev | Staging | Production | Overhead |
|---------|-----|---------|------------|----------|
| Transformation Logging | ✓ | ✓ | ✓ | 0.6% |
| Quality Metrics | ✓ | ✓ | ✓ | 1.3-2.5% |
| Intermediate Data | ✓ | ✓ | ✗ | 1.7% |
| Prometheus Metrics | ✓ | ✓ | ✓ | <0.1% |

### 5.3 Performance Tuning

**Batch Size Tuning** (Achievement 7.2):
- High throughput: `GRAPHRAG_LOGGING_BATCH_SIZE=200-500`
- Balanced (default): `GRAPHRAG_LOGGING_BATCH_SIZE=100`
- Low latency: `GRAPHRAG_LOGGING_BATCH_SIZE=50`

**Storage Management**:
- Aggressive cleanup: `GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=3`
- Balanced (default): `GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=7`
- Extended retention: `GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=14`

---

## Section 6: Validation and Testing

### 6.1 Post-Deployment Validation

Run all validation scripts:

```bash
cd /opt/graphrag/observability

# Run each validation script
./validate-achievement-53.sh  # Cost-benefit validation
./validate-achievement-71.sh  # Tool enhancements
./validate-achievement-72.sh  # Performance optimizations
./validate-achievement-73.sh  # Production readiness

# All should pass
```

### 6.2 Smoke Tests

```bash
# Quick smoke test script
#!/bin/bash

echo "Running smoke tests..."

# Test 1: Application health
curl -f http://localhost:8080/health || exit 1

# Test 2: Metrics endpoint
curl -f http://localhost:8080/metrics || exit 1

# Test 3: MongoDB connection
mongosh "$GRAPHRAG_DB_URI" --eval "db.runCommand({ ping: 1 })" || exit 1

# Test 4: Quick pipeline run
python -m business.pipelines.graphrag.main --video-id smoke-test --chunk-count 5 || exit 1

echo "All smoke tests passed!"
```

### 6.3 Integration Tests

Run comprehensive integration test suite:

```bash
# Run integration tests
pytest tests/integration/ -v

# Expected: All tests pass
```

---

## Section 7: Troubleshooting

### 7.1 Common Deployment Issues

**Issue 1: MongoDB Connection Failed**

```bash
# Symptoms
Error: MongoServerError: Authentication failed

# Solution
1. Verify credentials in .env file
2. Check user permissions: db.getUser("graphrag_user")
3. Verify network connectivity: telnet mongodb.host 27017
4. Check firewall rules
```

**Issue 2: Indexes Not Created**

```bash
# Symptoms
Slow queries, high CPU usage

# Solution
1. Verify indexes exist: db.transformation_logs.getIndexes()
2. Recreate indexes if missing
3. Run: python scripts/setup/create_indexes.py --env production
```

**Issue 3: Observability Stack Not Running**

```bash
# Symptoms
Grafana/Prometheus inaccessible

# Solution
1. Check container status: docker-compose ps
2. View logs: docker-compose logs prometheus
3. Restart stack: docker-compose restart
4. Verify ports not in use: netstat -tulpn | grep 9090
```

**Issue 4: High Performance Overhead**

```bash
# Symptoms
Overhead > 10%

# Solution
1. Check batch size: echo $GRAPHRAG_LOGGING_BATCH_SIZE
2. Increase if low: export GRAPHRAG_LOGGING_BATCH_SIZE=200
3. Disable intermediate data if enabled
4. Review MongoDB query performance
```

### 7.2 Rollback Procedures

See Section 8 below for detailed rollback procedures.

---

## Section 8: Rollback Procedures

### 8.1 Emergency Rollback (Immediate)

**When to Use**: Critical production issue, immediate rollback needed

```bash
# Step 1: Disable observability (master switch)
export GRAPHRAG_ENABLE_OBSERVABILITY=false

# Step 2: Reload/restart application
systemctl reload graphrag

# Step 3: Verify rollback
curl http://localhost:8080/config | jq '.observability.enabled'
# Should return: false
```

**Rollback Time**: < 5 minutes

### 8.2 Graceful Rollback (Planned)

**When to Use**: Non-critical issues, planned downgrade

```bash
# Step 1: Reduce sample rate (if using pilot mode)
export GRAPHRAG_PILOT_SAMPLE_RATE=0.10  # 10%

# Step 2: Monitor for 24 hours

# Step 3: Full disable if needed
export GRAPHRAG_ENABLE_OBSERVABILITY=false

# Step 4: Reload
systemctl reload graphrag
```

### 8.3 Database Rollback

**If indexes need to be removed**:

```javascript
use graphrag_production

// Drop observability indexes (if needed)
db.transformation_logs.dropIndexes()
db.quality_metrics.dropIndexes()
db.graphrag_runs.dropIndexes()

// Drop observability collections (if needed - CAUTION!)
db.transformation_logs.drop()
db.quality_metrics.drop()
```

**⚠️ WARNING**: Dropping collections will lose all observability data. Only do this if instructed.

### 8.4 Post-Rollback Actions

- [ ] Notify stakeholders of rollback
- [ ] Document root cause
- [ ] Create action plan for re-deployment
- [ ] Update deployment procedures if needed

---

## Section 9: Post-Deployment

### 9.1 Communication

**Internal Communication**:
- [ ] Email engineering team: Deployment complete
- [ ] Update status page/dashboard
- [ ] Post in team chat channel
- [ ] Schedule post-mortem meeting

**External Communication** (if applicable):
- [ ] Customer notification (if customer-facing)
- [ ] Status page update
- [ ] Release notes published

### 9.2 Monitoring Schedule

**Week 1**: Daily monitoring and review
**Week 2-4**: Every 2-3 days
**Month 2+**: Weekly review

**Review Checklist**:
- [ ] Grafana dashboards reviewed
- [ ] Alert history reviewed
- [ ] Performance metrics analyzed
- [ ] Storage growth tracked
- [ ] Issues logged and prioritized

### 9.3 Continuous Improvement

- [ ] Collect feedback from operations team
- [ ] Document lessons learned
- [ ] Update deployment guide
- [ ] Improve monitoring/alerting
- [ ] Plan optimization opportunities

---

## Appendix A: Quick Reference

### Deployment Commands

```bash
# Check application status
systemctl status graphrag

# Reload configuration
systemctl reload graphrag

# Restart application
systemctl restart graphrag

# View logs
journalctl -u graphrag -f

# Check MongoDB
mongosh "$GRAPHRAG_DB_URI" --eval "db.serverStatus()"

# Check observability stack
docker-compose -f /opt/graphrag/observability/docker-compose.yml ps
```

### Configuration Locations

- Application config: `/opt/graphrag/.env`
- Docker Compose: `/opt/graphrag/observability/docker-compose.yml`
- Logs: `/var/log/graphrag/`
- Validation scripts: `/opt/graphrag/observability/`

### Support Contacts

- On-Call Engineer: [contact info]
- Database Team: [contact info]
- DevOps Team: [contact info]
- Engineering Manager: [contact info]

---

## Appendix B: Deployment Checklist

Quick checklist for deployment day:

- [ ] Pre-deployment checklist complete
- [ ] Stakeholders notified
- [ ] Rollback plan reviewed
- [ ] On-call team available
- [ ] Configuration files prepared
- [ ] Database setup complete
- [ ] Observability stack deployed
- [ ] Staging validation passed
- [ ] Pilot deployment successful
- [ ] Full rollout completed
- [ ] Post-deployment validation passed
- [ ] Monitoring confirmed working
- [ ] Team trained and ready
- [ ] Documentation updated
- [ ] Communication sent

---

**Guide Version**: 1.0  
**Achievement**: 7.3  
**Last Updated**: 2025-11-15

**Next Document**: Operations-Runbook.md (for ongoing operational procedures)





