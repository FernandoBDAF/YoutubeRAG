# Achievement 1.1: Observability Stack Deployment - Quick Start Guide

**For**: Human Executor  
**Goal**: Deploy and verify complete observability stack (Prometheus, Grafana, Loki, Promtail)  
**Time**: 3-4 hours total  
**Difficulty**: Medium (automated scripts provided)

---

## 🎯 What You'll Accomplish

By following this guide, you'll:

1. ✅ Deploy 4 Docker services (Prometheus, Grafana, Loki, Promtail)
2. ✅ Verify all services are operational and connected
3. ✅ Configure data sources in Grafana
4. ✅ Test end-to-end metrics and logs flow
5. ✅ Pass all 6 verification tests

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Docker Desktop OR Docker Engine + docker-compose installed
- [ ] Docker running (test: `docker ps`)
- [ ] Ports 9090, 3000, 3100 available (not in use)
- [ ] Network connectivity (to pull Docker images)
- [ ] ~5 GB disk space
- [ ] This project directory

---

## 🚀 Quick Start (3 Steps)

### Step 1: Run Pre-Flight Checks (2 min)

```bash
cd /path/to/YoutubeRAG
bash observability/00-preflight-checks.sh
```

**Expected Output**: All checks pass ✅

If any checks fail, fix the issues before proceeding.

### Step 2: Run Complete Deployment (20-30 min)

```bash
bash observability/RUN-DEPLOYMENT.sh
```

This runs all 4 phases automatically:

1. Pre-flight checks
2. Stack startup
3. Comprehensive debug
4. Integration verification
5. End-to-end testing

**Expected Output**: All phases complete ✅

### Step 3: Access the Stack (1 min)

Open in your browser:

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Loki**: http://localhost:3100 (API only, no UI)

---

## 📊 Detailed Execution Guide

If you prefer step-by-step control, run phases individually:

### Phase 1: Stack Startup (30-40 min)

```bash
bash observability/01-start-stack.sh
```

What happens:

- Validates configuration files
- Starts 4 Docker containers
- Waits 30 seconds for services to initialize
- Verifies containers are running

**Check**: `docker-compose -f docker-compose.observability.yml ps`

### Phase 2: Comprehensive Debug (30-45 min)

```bash
bash observability/02-debug-all.sh
```

What happens:

- Checks Docker status
- Tests service endpoints
- Reviews Prometheus configuration
- Verifies Grafana environment
- Shows Loki and Promtail status
- Displays container logs

**Check**: Services should be responding on ports 9090, 3000, 3100

### Phase 3: Integration Verification (30-40 min)

```bash
bash observability/03-verify-integration.sh
```

What happens:

- Verifies Grafana is accessible
- Creates datasource provisioning files (if not present)
- Tests Prometheus query API
- Tests Loki query API
- Restarts Grafana to load datasources

**Check**: Visit http://localhost:3000 and confirm datasources exist

### Phase 4: End-to-End Testing (30-45 min)

```bash
bash observability/04-e2e-test.sh
```

Runs 6 verification tests:

1. ✅ Container Health - All 4 containers running
2. ✅ Service Accessibility - HTTP endpoints respond
3. ✅ Prometheus Health - Configuration and queries working
4. ✅ Grafana Connectivity - API and provisioning ready
5. ✅ Dashboard Provisioning - Ready for use
6. ✅ End-to-End Flow - Complete data flow verified

**Expected**: All 6 tests pass ✅

---

## 🧪 Testing with Real Data (Optional)

After deployment, test with real metrics:

```bash
# Terminal 1: Start generating test metrics
python3 observability/04-generate-test-metrics.py

# Terminal 2: Query Prometheus (after 30 seconds)
curl http://localhost:9090/api/v1/query?query=test_metric_total
```

Then in Grafana:

1. Create new dashboard
2. Add panel with query: `rate(test_metric_total[1m])`
3. See metrics flowing!

---

## 📍 Service Locations

| Service    | URL                   | Port | Credentials |
| ---------- | --------------------- | ---- | ----------- |
| Prometheus | http://localhost:9090 | 9090 | (none)      |
| Grafana    | http://localhost:3000 | 3000 | admin/admin |
| Loki       | http://localhost:3100 | 3100 | API only    |
| Promtail   | (no UI)               | -    | -           |

---

## 🆘 Troubleshooting

### Port Already in Use

```bash
# Find what's using port 9090 (example)
lsof -i :9090

# Kill the process (if safe)
kill -9 <PID>

# Or try a different port in docker-compose.observability.yml
```

### Containers Won't Start

```bash
# Check detailed logs
docker-compose -f docker-compose.observability.yml logs -f

# Force cleanup and restart
docker-compose -f docker-compose.observability.yml down -v
docker-compose -f docker-compose.observability.yml up -d
```

### Prometheus Not Scraping

1. Check targets: http://localhost:9090/targets
2. Verify config: `docker exec youtuberag-prometheus cat /etc/prometheus/prometheus.yml`
3. Wait 30 seconds for first scrape

### Grafana Datasources Not Connected

1. Check provisioning: `ls -la observability/grafana/datasources/`
2. Restart Grafana: `docker-compose -f docker-compose.observability.yml restart grafana`
3. Verify in UI: Configuration → Data Sources

### Loki Not Receiving Logs

1. Verify logs directory: `ls -la logs/`
2. Check Promtail: `docker logs youtuberag-promtail`
3. Generate test logs: `echo "test" >> logs/test.log`

---

## ✅ Success Criteria

Achievement 1.1 is complete when:

- ✅ All 4 services running: `docker-compose -f docker-compose.observability.yml ps`
- ✅ Prometheus accessible: http://localhost:9090/targets
- ✅ Grafana accessible: http://localhost:3000 (login successful)
- ✅ Loki ready: `curl http://localhost:3100/ready`
- ✅ Datasources configured in Grafana
- ✅ All 6 tests passing
- ✅ Can query metrics and logs

---

## 📚 Documentation

For detailed information, see:

- **`01_DEPLOYMENT_GUIDE.md`** - Complete deployment walkthrough
- **`README.md`** - Service overview and examples
- **`docker-compose.observability.yml`** - Container configuration

---

## 🎯 Next Steps After Deployment

1. **Create Dashboards**: Design visualizations for your metrics
2. **Connect Application**: Start collecting metrics from your app
3. **Monitor Pipeline**: Watch GraphRAG transformations in real-time
4. **Set Alerts**: Configure alerting rules for important metrics
5. **Analyze Logs**: Query logs from Loki for debugging

---

## 💬 Support

If you encounter issues:

1. Run debug script: `bash observability/02-debug-all.sh`
2. Check logs: `docker-compose -f docker-compose.observability.yml logs`
3. Review `01_DEPLOYMENT_GUIDE.md` troubleshooting section

---

## 🎉 You're Ready!

```bash
# Quick start (all-in-one)
bash observability/RUN-DEPLOYMENT.sh

# Or run step-by-step
bash observability/00-preflight-checks.sh
bash observability/01-start-stack.sh
bash observability/02-debug-all.sh
bash observability/03-verify-integration.sh
bash observability/04-e2e-test.sh
```

Good luck! 🚀
