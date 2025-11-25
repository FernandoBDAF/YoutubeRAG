# Operations Runbook

**Achievement**: 7.3 - Production Readiness Package  
**Purpose**: Day-to-day operational procedures for GraphRAG observability infrastructure  
**Last Updated**: 2025-11-15

---

## Overview

This runbook provides operational procedures for managing the GraphRAG observability infrastructure in production. Use this as your primary reference for routine operations, troubleshooting, and incident response.

**Target Audience**: Operations team, on-call engineers, support staff

**Prerequisites**: Familiarity with GraphRAG architecture and deployment (see Production-Deployment-Guide.md)

---

## Section 1: Quick Reference

### 1.1 Emergency Contacts

| Role | Name | Contact | Escalation Time |
|------|------|---------|-----------------|
| On-Call Engineer | [Name] | [Phone/Slack] | Immediate |
| Engineering Lead | [Name] | [Phone/Email] | 15 minutes |
| Database Admin | [Name] | [Phone/Email] | 30 minutes |
| DevOps Lead | [Name] | [Phone/Email] | 30 minutes |

### 1.2 Critical Systems

| System | URL/Endpoint | Health Check | SLA |
|--------|--------------|--------------|-----|
| GraphRAG Application | http://graphrag.prod:8080 | `/health` | 99.9% |
| MongoDB | mongodb://mongo.prod:27017 | `db.runCommand({ ping: 1 })` | 99.95% |
| Prometheus | http://prometheus.prod:9090 | `/-/healthy` | 99.5% |
| Grafana | http://grafana.prod:3000 | `/api/health` | 99.5% |

### 1.3 Common Commands

```bash
# Check application status
systemctl status graphrag

# View recent logs
journalctl -u graphrag -n 100 -f

# Check MongoDB connection
mongosh "$GRAPHRAG_DB_URI" --eval "db.runCommand({ ping: 1 })"

# View Grafana dashboards
open http://grafana.prod:3000/d/graphrag-overview

# Restart observability stack
docker-compose -f /opt/graphrag/observability/docker-compose.yml restart
```

### 1.4 Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| Environment | `/opt/graphrag/.env` | Application config |
| Docker Compose | `/opt/graphrag/observability/docker-compose.yml` | Observability stack |
| Logs | `/var/log/graphrag/` | Application logs |
| Backups | `/backups/graphrag/` | MongoDB backups |

---

## Section 2: Daily Operations

### 2.1 Daily Health Check

**Frequency**: Every morning (or start of shift)

**Checklist**:
- [ ] Review Grafana "GraphRAG Overview" dashboard
- [ ] Check for active alerts in Alertmanager
- [ ] Review error logs for patterns
- [ ] Verify storage usage < 70%
- [ ] Check backup status (last 24 hours)

**Commands**:

```bash
# Quick health check script
#!/bin/bash
echo "=== GraphRAG Health Check ==="

# Application health
curl -f http://localhost:8080/health && echo "✓ Application healthy" || echo "✗ Application unhealthy"

# MongoDB health
mongosh "$GRAPHRAG_DB_URI" --eval "db.runCommand({ ping: 1 })" && echo "✓ MongoDB healthy" || echo "✗ MongoDB unhealthy"

# Storage check
df -h /opt/graphrag | tail -1 | awk '{print "Storage usage: "$5}'

# Recent errors
echo "Recent errors (last hour):"
journalctl -u graphrag --since "1 hour ago" --priority=err | wc -l
```

### 2.2 Weekly Operations

**Every Monday**:
- [ ] Review weekly metrics summary
- [ ] Check storage growth trends
- [ ] Review capacity planning dashboard
- [ ] Update operational documentation if needed

**Every Friday**:
- [ ] Review week's incidents and resolutions
- [ ] Update runbook with new learnings
- [ ] Check backup rotation policy
- [ ] Plan next week's maintenance (if any)

### 2.3 Monthly Operations

- [ ] Review monthly performance trends
- [ ] Analyze storage growth and project capacity needs
- [ ] Review and rotate access credentials (if policy requires)
- [ ] Conduct disaster recovery drill
- [ ] Review and update monitoring thresholds
- [ ] Generate monthly operational report

---

## Section 3: Monitoring and Alerting

### 3.1 Grafana Dashboards

**Primary Dashboards**:

1. **GraphRAG Overview** (`/d/graphrag-overview`)
   - Pipeline execution summary
   - Error rates
   - Performance metrics
   - Storage usage

2. **Pipeline Performance** (`/d/pipeline-performance`)
   - Execution time trends
   - Stage-by-stage performance
   - Bottleneck identification

3. **Quality Metrics** (`/d/quality-metrics`)
   - Entity extraction quality
   - Relation extraction quality
   - Community detection metrics
   - Overall quality score trends

4. **Storage Usage** (`/d/storage-usage`)
   - Collection sizes
   - Growth rates
   - TTL effectiveness
   - Capacity projections

**Daily Review Focus**:
- Error rate < 1%
- Average execution time within baseline ±10%
- Storage growth rate consistent with projections
- No sustained spikes in any metric

### 3.2 Alert Response

**Alert Priority Levels**:
- **P1 (Critical)**: Immediate response, page on-call
- **P2 (High)**: Response within 15 minutes
- **P3 (Medium)**: Response within 1 hour
- **P4 (Low)**: Handle during business hours

**Alert Runbooks**:

#### P1: Pipeline Failure Rate > 5%

```
SEVERITY: Critical
SYMPTOM: High failure rate across pipelines
IMPACT: Multiple customers affected

INVESTIGATION:
1. Check Grafana "GraphRAG Overview" dashboard
2. Review recent error logs: journalctl -u graphrag --priority=err -n 100
3. Check MongoDB connectivity
4. Verify service health: systemctl status graphrag

RESOLUTION:
- If MongoDB issue: Escalate to DBA team
- If application crash: Restart service: systemctl restart graphrag
- If resource exhaustion: Scale up resources
- If data corruption: See Section 9 (Disaster Recovery)

ESCALATION:
If not resolved in 15 minutes, escalate to Engineering Lead
```

#### P1: MongoDB Connection Lost

```
SEVERITY: Critical
SYMPTOM: Cannot connect to MongoDB
IMPACT: All pipelines blocked

INVESTIGATION:
1. Test connection: mongosh "$GRAPHRAG_DB_URI" --eval "db.runCommand({ ping: 1 })"
2. Check MongoDB service status
3. Verify network connectivity
4. Check authentication

RESOLUTION:
- If MongoDB down: Escalate immediately to DBA team
- If network issue: Contact infrastructure team
- If auth failure: Verify credentials in .env file
- Check firewall rules if network issue

ESCALATION:
Immediate escalation to DBA team + DevOps
```

#### P1: Storage > 80% Full

```
SEVERITY: Critical (approaching failure)
SYMPTOM: Disk space critically low
IMPACT: Pipeline failures imminent

INVESTIGATION:
1. Check disk usage: df -h /opt/graphrag
2. Identify large collections: du -sh /opt/graphrag/*
3. Review storage growth dashboard

IMMEDIATE ACTIONS:
1. Enable intermediate data TTL if not enabled
2. Manually clean old logs if safe: find /var/log/graphrag -mtime +7 -delete
3. Request storage expansion immediately

ESCALATION:
Immediate escalation to Infrastructure team for storage expansion
```

#### P2: Performance Overhead > 10%

```
SEVERITY: High
SYMPTOM: Pipeline execution slower than baseline
IMPACT: Reduced throughput

INVESTIGATION:
1. Check Performance dashboard
2. Review recent configuration changes
3. Check batch size: echo $GRAPHRAG_LOGGING_BATCH_SIZE
4. Review MongoDB slow query logs

RESOLUTION:
- Increase batch size: export GRAPHRAG_LOGGING_BATCH_SIZE=200
- Disable intermediate data if enabled
- Check for missing indexes
- Review and optimize slow queries

ESCALATION:
If not resolved in 1 hour, escalate to Engineering team
```

### 3.3 Monitoring Best Practices

**Thresholds**:
- Set alert thresholds at 80% of capacity (warning)
- Set critical thresholds at 90% of capacity
- Review thresholds monthly
- Adjust based on observed patterns

**Noise Reduction**:
- Use alert grouping for related alerts
- Implement alert suppression during maintenance
- Set minimum duration for transient issues (e.g., 5 minutes)

---

## Section 4: Performance Tuning

### 4.1 Batch Size Optimization

**Current Setting**: `GRAPHRAG_LOGGING_BATCH_SIZE=100`

**When to Increase** (to 200-500):
- High throughput environment
- Low latency requirements less critical
- Stable network with good bandwidth

**When to Decrease** (to 50):
- Need faster feedback in logs
- Debugging issues
- Unstable network conditions

**How to Change**:

```bash
# Edit .env
nano /opt/graphrag/.env

# Update value
GRAPHRAG_LOGGING_BATCH_SIZE=200

# Reload application
systemctl reload graphrag

# Monitor impact
watch -n 5 'journalctl -u graphrag -n 20 | grep "flush"'
```

### 4.2 MongoDB Performance Tuning

**Check Query Performance**:

```javascript
// In mongosh
use graphrag_production

// Enable profiling
db.setProfilingLevel(1, { slowms: 100 })

// Check slow queries
db.system.profile.find({ millis: { $gt: 100 } }).sort({ ts: -1 }).limit(10).pretty()

// Analyze query plans
db.transformation_logs.find({ trace_id: "xxx" }).explain("executionStats")
```

**Index Optimization**:

```javascript
// Check index usage
db.transformation_logs.aggregate([
  { $indexStats: {} }
])

// Drop unused indexes (if any)
// db.collection.dropIndex("index_name")

// Rebuild indexes if needed
db.transformation_logs.reIndex()
```

### 4.3 Feature Toggle Optimization

**Scenario 1: Reduce Overhead for High-Volume Period**

```bash
# Temporarily disable intermediate data
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=false

# Reload
systemctl reload graphrag
```

**Scenario 2: Enhanced Debugging**

```bash
# Enable all features for debugging
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
export GRAPHRAG_LOGGING_BATCH_SIZE=10  # Faster feedback

# Reload
systemctl reload graphrag
```

**Scenario 3: Production Optimization**

```bash
# Optimal production settings (from Achievement 5.3)
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_QUALITY_METRICS=true
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
export GRAPHRAG_PROMETHEUS_METRICS=true
export GRAPHRAG_LOGGING_BATCH_SIZE=100
```

---

## Section 5: Data Management

### 5.1 TTL Management

**Verify TTL Indexes**:

```javascript
use graphrag_production

// Check TTL index on intermediate data
db.entities_raw.getIndexes().filter(idx => idx.expireAfterSeconds !== undefined)

// Expected: expireAfterSeconds: 604800 (7 days)
```

**Manually Clean Old Data** (if TTL not working):

```javascript
// Calculate cutoff date (7 days ago)
var cutoffDate = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)

// Delete old documents
db.entities_raw.deleteMany({ timestamp: { $lt: cutoffDate.getTime() / 1000 } })
db.entities_resolved.deleteMany({ timestamp: { $lt: cutoffDate.getTime() / 1000 } })
// Repeat for other intermediate collections
```

### 5.2 Storage Cleanup

**Weekly Cleanup Tasks**:

```bash
# Clean old application logs (> 30 days)
find /var/log/graphrag -name "*.log" -mtime +30 -delete

# Clean old Docker logs
docker system prune -a --filter "until=168h" -f

# Verify storage freed
df -h /opt/graphrag
```

### 5.3 Data Archival

**Archive Old Transformation Logs** (optional, for compliance):

```javascript
// Export logs older than 90 days
mongoexport --uri="$GRAPHRAG_DB_URI" \
  --collection=transformation_logs \
  --query='{ "timestamp": { "$lt": <90_days_ago_timestamp> } }' \
  --out=/backups/graphrag/transformation_logs_archive_$(date +%Y%m%d).json

// After verification, delete archived data
db.transformation_logs.deleteMany({ timestamp: { $lt: <90_days_ago_timestamp> } })
```

### 5.4 Backup and Restore

**Daily Backup**:

```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups/graphrag/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup MongoDB
mongodump --uri="$GRAPHRAG_DB_URI" --out="$BACKUP_DIR/mongodb"

# Backup configuration
cp /opt/graphrag/.env $BACKUP_DIR/config.env

# Compress
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# Rotate old backups (keep 30 days)
find /backups/graphrag -name "*.tar.gz" -mtime +30 -delete
```

**Restore from Backup**:

```bash
# Extract backup
tar -xzf /backups/graphrag/20251115.tar.gz

# Restore MongoDB
mongorestore --uri="$GRAPHRAG_DB_URI" --dir=/backups/graphrag/20251115/mongodb
```

---

## Section 6: Troubleshooting Guide

### 6.1 Common Issues and Solutions

#### Issue 1: Pipeline Stuck or Hanging

**Symptoms**:
- Pipeline execution not progressing
- No new logs appearing
- Health check failing

**Diagnosis**:

```bash
# Check if process is running
ps aux | grep graphrag

# Check for deadlocks in logs
journalctl -u graphrag --since "10 minutes ago" | grep -i "deadlock\|timeout\|hang"

# Check MongoDB connections
mongosh "$GRAPHRAG_DB_URI" --eval "db.serverStatus().connections"
```

**Resolution**:

```bash
# Option 1: Restart application
systemctl restart graphrag

# Option 2: Kill stuck process
pkill -9 -f graphrag
systemctl start graphrag

# Option 3: Check MongoDB (if persistent)
mongosh "$GRAPHRAG_DB_URI" --eval "db.currentOp()"
# Kill long-running operations if found
```

#### Issue 2: High Memory Usage

**Symptoms**:
- OOM killer logs
- Application crashes
- Slow performance

**Diagnosis**:

```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head -10

# Check for memory leaks
journalctl -u graphrag | grep -i "memory\|oom"
```

**Resolution**:

```bash
# Immediate: Restart to free memory
systemctl restart graphrag

# Long-term: Adjust batch sizes
export GRAPHRAG_LOGGING_BATCH_SIZE=50  # Reduce buffer size

# Consider: Scale up instance
```

#### Issue 3: Metrics Not Appearing in Grafana

**Symptoms**:
- Dashboards show "No data"
- Metrics stopped updating

**Diagnosis**:

```bash
# Check Prometheus scraping
curl http://localhost:8080/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets'

# Check Grafana data source
curl http://localhost:3000/api/datasources
```

**Resolution**:

```bash
# Restart Prometheus
docker-compose -f /opt/graphrag/observability/docker-compose.yml restart prometheus

# Verify scrape config
cat /opt/graphrag/observability/prometheus/prometheus.yml

# Check firewall rules
iptables -L -n | grep 8080
```

#### Issue 4: Transformation Logs Missing

**Symptoms**:
- No logs in transformation_logs collection
- Query scripts return empty results

**Diagnosis**:

```bash
# Check if logging is enabled
echo $GRAPHRAG_TRANSFORMATION_LOGGING

# Check for errors
journalctl -u graphrag | grep -i "transformation.*error\|buffer.*error"

# Check MongoDB write permissions
mongosh "$GRAPHRAG_DB_URI" --eval "db.transformation_logs.insertOne({ test: true })"
```

**Resolution**:

```bash
# Enable logging if disabled
export GRAPHRAG_TRANSFORMATION_LOGGING=true
systemctl reload graphrag

# Check buffer size
export GRAPHRAG_LOGGING_BATCH_SIZE=100

# Manually flush buffer (if application has API)
curl -X POST http://localhost:8080/api/flush-logs
```

### 6.2 Debugging Tools

**MongoDB Debugging**:

```javascript
// Check collection stats
db.transformation_logs.stats()

// Check recent documents
db.transformation_logs.find().sort({ timestamp: -1 }).limit(10).pretty()

// Check for errors
db.transformation_logs.find({ error: { $exists: true } }).count()
```

**Application Debugging**:

```bash
# Enable debug logging temporarily
export LOG_LEVEL=DEBUG
systemctl reload graphrag

# Tail debug logs
journalctl -u graphrag -f | grep DEBUG

# Revert after debugging
export LOG_LEVEL=INFO
systemctl reload graphrag
```

---

## Section 7: Disaster Recovery

### 7.1 Service Failure Recovery

**Scenario 1: Application Crash**

```bash
# Check crash logs
journalctl -u graphrag --since "1 hour ago" | grep -i "crash\|fatal\|segfault"

# Restart service
systemctl restart graphrag

# Verify recovery
systemctl status graphrag
curl http://localhost:8080/health
```

**Scenario 2: MongoDB Failure**

```bash
# Contact DBA team immediately
# Document failure time and symptoms

# Check backup availability
ls -lh /backups/graphrag/*.tar.gz | tail -5

# While waiting for recovery, disable observability
export GRAPHRAG_ENABLE_OBSERVABILITY=false
systemctl reload graphrag
```

**Scenario 3: Observability Stack Failure**

```bash
# Stop and restart stack
cd /opt/graphrag/observability
docker-compose down
docker-compose up -d

# Verify all services
docker-compose ps

# Re-import Grafana dashboards if needed
curl -X POST http://admin:admin@localhost:3000/api/dashboards/import \
  -H "Content-Type: application/json" \
  -d @grafana/dashboards/graphrag-overview.json
```

### 7.2 Data Corruption Recovery

**Symptoms**:
- Query results look wrong
- Inconsistent data
- Index errors

**Recovery Steps**:

```javascript
// 1. Identify corrupted collection
use graphrag_production
db.transformation_logs.validate({ full: true })

// 2. If validation fails, rebuild indexes
db.transformation_logs.reIndex()

// 3. If still corrupted, restore from backup
// (see Section 5.4)
```

### 7.3 Complete System Recovery

**Worst Case Scenario**: Complete system failure

**Recovery Procedure**:

1. **Assess Damage**:
   ```bash
   # Check what's working
   systemctl status graphrag
   docker ps
   mongosh "$GRAPHRAG_DB_URI" --eval "db.runCommand({ ping: 1 })"
   ```

2. **Restore from Backup**:
   ```bash
   # Get latest backup
   LATEST_BACKUP=$(ls -t /backups/graphrag/*.tar.gz | head -1)
   tar -xzf $LATEST_BACKUP -C /tmp/restore
   
   # Restore MongoDB
   mongorestore --uri="$GRAPHRAG_DB_URI" --drop --dir=/tmp/restore/mongodb
   ```

3. **Rebuild Infrastructure**:
   ```bash
   # Redeploy observability stack
   cd /opt/graphrag/observability
   docker-compose down
   docker-compose up -d
   
   # Restart application
   systemctl restart graphrag
   ```

4. **Verify Recovery**:
   ```bash
   # Run validation scripts
   cd /opt/graphrag/observability
   ./validate-achievement-73.sh
   ```

5. **Document Incident**:
   - Timeline of events
   - Root cause
   - Actions taken
   - Lessons learned
   - Preventive measures

---

## Section 8: Performance Monitoring

### 8.1 Key Metrics to Monitor

**Application Metrics**:
- Pipeline execution time (target: < baseline + 5%)
- Error rate (target: < 1%)
- Throughput (pipelines/hour)
- Memory usage (target: < 80%)
- CPU usage (target: < 70%)

**Database Metrics**:
- Query execution time (target: < 100ms)
- Connection pool usage (target: < 80%)
- Storage growth rate (track trend)
- Index efficiency (> 95% index hits)

**Observability Metrics**:
- Logging overhead (target: 0.3-0.4%)
- Buffer flush rate
- Metrics collection overhead (target: 0.8-1.5%)
- Total overhead (target: < 5%)

### 8.2 Performance Baselines

From Achievement 5.1:

| Metric | Baseline | With Observability | Target Overhead |
|--------|----------|-------------------|-----------------|
| Pipeline Time | 100% | 104-105% | < 105% |
| Memory | 100% | 102-103% | < 105% |
| CPU | 100% | 103-105% | < 110% |
| Storage | N/A | 490 MB/run | < 500 MB/run |

### 8.3 Trend Analysis

**Weekly Review**:
```bash
# Generate weekly performance report
python scripts/reporting/weekly_performance.py --week=$(date +%V)

# Review trends
# - Execution time trend
# - Error rate trend
# - Storage growth trend
# - Resource utilization trend
```

**Monthly Review**:
- Compare month-to-month trends
- Identify seasonal patterns
- Plan capacity adjustments
- Update baselines if needed

---

## Section 9: Capacity Planning

### 9.1 Storage Projections

**Current Growth**: ~3 GB/month (without TTL)

**Projection Model**:
```
Monthly Growth = (Pipelines/day × Storage/pipeline × 30)
Annual Projection = Monthly Growth × 12

With TTL (7 days): ~500 MB steady state
Without TTL: ~3 GB/month, ~36 GB/year
```

**Action Thresholds**:
- 60% full: Start planning expansion
- 70% full: Initiate expansion request
- 80% full: Emergency expansion needed

### 9.2 Scaling Recommendations

**Vertical Scaling** (Increase resources):

| Load Level | CPU | Memory | Storage |
|------------|-----|--------|---------|
| Low (< 100 pipelines/day) | 4 cores | 8 GB | 50 GB |
| Medium (100-500 pipelines/day) | 8 cores | 16 GB | 100 GB |
| High (> 500 pipelines/day) | 16 cores | 32 GB | 200 GB |

**Horizontal Scaling** (Multiple instances):
- Use load balancer for application instances
- MongoDB replica set for database
- Prometheus federation for metrics aggregation

### 9.3 Cost Optimization

**Storage Cost Reduction**:
- Enable TTL on all intermediate collections
- Reduce TTL period if possible (3-5 days)
- Archive old logs to cheaper storage
- Compress backups

**Compute Cost Reduction**:
- Optimize batch sizes for efficiency
- Disable intermediate data in production
- Use spot instances for non-critical environments
- Right-size instances based on utilization

---

## Section 10: Escalation Procedures

### 10.1 Escalation Matrix

**Level 1: On-Call Engineer** (You)
- Initial triage and diagnosis
- Attempt standard remediation
- Document findings
- **Escalate if**: Not resolved in 30 minutes

**Level 2: Engineering Lead**
- Complex technical issues
- Code-related problems
- Performance tuning needs
- **Escalate if**: Requires code changes or deep expertise

**Level 3: Database Admin**
- MongoDB issues
- Data corruption
- Performance problems
- **Escalate if**: Database-level issue identified

**Level 4: Management**
- Major outage (> 4 hours)
- Data loss incident
- Security breach
- **Escalate if**: Business impact is high

### 10.2 Escalation Criteria

**Immediate Escalation** (Level 2+):
- Complete service outage
- Data loss or corruption
- Security incident
- Performance degradation > 50%

**15-Minute Escalation** (Level 2):
- Partial service degradation
- Recurring errors
- Performance degradation 10-50%
- Unable to resolve with standard procedures

**30-Minute Escalation** (Level 2):
- Persistent issues
- Unusual behavior
- Need expert consultation

### 10.3 Incident Communication

**Internal Communication Template**:

```
INCIDENT: [Brief title]
SEVERITY: [P1/P2/P3/P4]
STATUS: [Investigating/Identified/Resolving/Resolved]

IMPACT:
- [What is affected]
- [How many users/pipelines]
- [Business impact]

TIMELINE:
- [Time] Incident detected
- [Time] Investigation started
- [Time] Root cause identified (if known)
- [Time] Resolution applied (if applicable)

NEXT STEPS:
- [What we're doing next]
- [ETA for resolution]

UPDATES:
Regular updates every 30 minutes until resolved.
```

**External Communication** (if customer-facing):
- Use status page for updates
- Keep messages brief and non-technical
- Provide realistic ETAs
- Follow up post-resolution

---

## Appendix A: Useful Scripts

### Health Check Script

```bash
#!/bin/bash
# /opt/graphrag/scripts/health_check.sh

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "=== GraphRAG Health Check ==="
echo ""

# Application
if curl -sf http://localhost:8080/health > /dev/null; then
    echo -e "${GREEN}✓${NC} Application healthy"
else
    echo -e "${RED}✗${NC} Application unhealthy"
fi

# MongoDB
if mongosh "$GRAPHRAG_DB_URI" --quiet --eval "db.runCommand({ ping: 1 })" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} MongoDB healthy"
else
    echo -e "${RED}✗${NC} MongoDB unhealthy"
fi

# Prometheus
if curl -sf http://localhost:9090/-/healthy > /dev/null; then
    echo -e "${GREEN}✓${NC} Prometheus healthy"
else
    echo -e "${RED}✗${NC} Prometheus unhealthy"
fi

# Grafana
if curl -sf http://localhost:3000/api/health > /dev/null; then
    echo -e "${GREEN}✓${NC} Grafana healthy"
else
    echo -e "${RED}✗${NC} Grafana unhealthy"
fi

# Storage
STORAGE_USAGE=$(df -h /opt/graphrag | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $STORAGE_USAGE -lt 70 ]; then
    echo -e "${GREEN}✓${NC} Storage at ${STORAGE_USAGE}%"
elif [ $STORAGE_USAGE -lt 80 ]; then
    echo -e "\033[1;33m⚠${NC} Storage at ${STORAGE_USAGE}% (warning)"
else
    echo -e "${RED}✗${NC} Storage at ${STORAGE_USAGE}% (critical)"
fi
```

### Performance Monitor Script

```bash
#!/bin/bash
# /opt/graphrag/scripts/performance_monitor.sh

# Collect performance metrics
TIMESTAMP=$(date +%Y-%m-%d_%H:%M:%S)
echo "[$TIMESTAMP] Performance Snapshot"

# CPU and Memory
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')%"
echo "Memory: $(free -h | grep Mem | awk '{print $3 "/" $2}')"

# MongoDB connections
MONGO_CONNECTIONS=$(mongosh "$GRAPHRAG_DB_URI" --quiet --eval "db.serverStatus().connections.current")
echo "MongoDB Connections: $MONGO_CONNECTIONS"

# Recent pipeline count
RECENT_PIPELINES=$(mongosh "$GRAPHRAG_DB_URI" --quiet --eval "db.graphrag_runs.countDocuments({ timestamp: { \$gt: $(date -d '1 hour ago' +%s) } })")
echo "Pipelines (last hour): $RECENT_PIPELINES"

# Error count
ERROR_COUNT=$(journalctl -u graphrag --since "1 hour ago" --priority=err | wc -l)
echo "Errors (last hour): $ERROR_COUNT"
```

---

## Appendix B: Maintenance Windows

### Planned Maintenance Procedures

**Monthly Maintenance** (First Sunday, 2 AM - 4 AM):

1. **Database Maintenance**:
   ```bash
   # Compact collections (if needed)
   mongosh "$GRAPHRAG_DB_URI" --eval "db.runCommand({ compact: 'transformation_logs' })"
   
   # Rebuild indexes
   mongosh "$GRAPHRAG_DB_URI" --eval "db.transformation_logs.reIndex()"
   ```

2. **Application Updates**:
   ```bash
   # Stop application
   systemctl stop graphrag
   
   # Update code
   cd /opt/graphrag
   git pull origin main
   pip install -r requirements.txt
   
   # Restart
   systemctl start graphrag
   ```

3. **Backup Verification**:
   ```bash
   # Test restore from latest backup
   # (in test environment)
   ```

---

**Runbook Version**: 1.0  
**Achievement**: 7.3  
**Last Updated**: 2025-11-15  
**Review Schedule**: Quarterly

**Related Documents**:
- Production-Readiness-Checklist.md
- Production-Deployment-Guide.md





