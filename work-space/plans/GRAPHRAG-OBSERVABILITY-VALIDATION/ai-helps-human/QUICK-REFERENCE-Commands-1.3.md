# Quick Reference: Copy-Paste Commands for Achievement 1.3

**Achievement**: 1.3 - Grafana Dashboards Configured  
**Purpose**: Quick command reference (copy-paste ready)

---

## Health Checks

### Check if all services are running:

```bash
docker ps | grep -E "grafana|prometheus|loki"
```

### Check Prometheus health:

```bash
curl -s http://localhost:9090/-/healthy
```

### Check Loki health:

```bash
curl -s http://localhost:3100/ready
```

### View all dashboard files:

```bash
ls -lh ~/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG/observability/grafana/dashboards/
```

---

## Restart Commands

### Restart just Grafana:

```bash
docker-compose -f ~/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG/docker-compose.observability.yml restart grafana
```

### Restart just Prometheus:

```bash
docker-compose -f ~/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG/docker-compose.observability.yml restart prometheus
```

### Restart just Loki:

```bash
docker-compose -f ~/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG/docker-compose.observability.yml restart loki
```

### Restart entire observability stack:

```bash
cd ~/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG && \
docker-compose -f docker-compose.observability.yml restart
```

### Start observability stack (if stopped):

```bash
cd ~/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG && \
docker-compose -f docker-compose.observability.yml up -d
```

---

## Debugging Commands

### Check Grafana logs:

```bash
docker logs youtuberag-grafana --tail 50
```

### Check Prometheus logs:

```bash
docker logs youtuberag-prometheus --tail 50
```

### Check Loki logs:

```bash
docker logs youtuberag-loki --tail 50
```

### Check Prometheus targets:

```bash
curl -s http://localhost:9090/api/v1/targets | python3 -m json.tool
```

### Check if Prometheus is scraping metrics:

```bash
curl -s http://localhost:9090/api/v1/query?query=up | python3 -m json.tool
```

### Check available metrics on Prometheus:

```bash
curl -s http://localhost:9090/api/v1/label/__name__/values | python3 -m json.tool
```

---

## Browser URLs

### Grafana Dashboard:

```
http://localhost:3000
```

- Username: `admin`
- Password: `admin`

### Prometheus Query Interface:

```
http://localhost:9090
```

### Prometheus Targets Page:

```
http://localhost:9090/targets
```

### Loki API (for testing):

```
http://localhost:3100/ready
```

---

## Data Source URLs (for Grafana)

**Prometheus**:

```
http://localhost:9090
```

**Loki**:

```
http://localhost:3100
```

---

## File Locations

**Dashboard JSON files**:

```
~/Local Repo/YoutubeRAG-mongohack/YoutubeRAG/observability/grafana/dashboards/
```

**Grafana config**:

```
~/Local Repo/YoutubeRAG-mongohack/YoutubeRAG/observability/grafana/
```

**Docker compose**:

```
~/Local Repo/YoutubeRAG-mongohack/YoutubeRAG/docker-compose.observability.yml
```

---

## Expected Outputs

### Grafana running (docker ps):

```
youtuberag-grafana   grafana/grafana:latest   ...   youtuberag-grafana   Up 2 hours   0.0.0.0:3000->3000/tcp
```

### Prometheus running (docker ps):

```
youtuberag-prometheus   prom/prometheus:latest   ...   youtuberag-prometheus   Up 2 hours   0.0.0.0:9090->9090/tcp
```

### Loki running (docker ps):

```
youtuberag-loki   grafana/loki:latest   ...   youtuberag-loki   Up 2 hours   0.0.0.0:3100->3100/tcp
```

### Prometheus healthy:

```
Prometheus is Healthy.
```

### Loki ready:

```
ready
```

---

## If Services Won't Start

### Check Docker daemon:

```bash
docker ps
```

### View full Docker logs:

```bash
docker-compose -f ~/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG/docker-compose.observability.yml logs
```

### Force restart (stop + start):

```bash
cd ~/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG && \
docker-compose -f docker-compose.observability.yml down && \
docker-compose -f docker-compose.observability.yml up -d
```

### Clean restart (remove volumes):

```bash
cd ~/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG && \
docker-compose -f docker-compose.observability.yml down -v && \
docker-compose -f docker-compose.observability.yml up -d
```

---

## Useful Tips

### Change directory to project root:

```bash
cd ~/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG
```

### Copy a dashboard JSON to view:

```bash
cat ~/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG/observability/grafana/dashboards/graphrag-pipeline.json
```

### Count dashboard files:

```bash
ls ~/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG/observability/grafana/dashboards/*.json | wc -l
```

### List all JSON files with details:

```bash
find ~/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG/observability/grafana/dashboards -name "*.json" -exec ls -lh {} \;
```

---

## Share These Commands' Output with AI

When you share results, include output from:

1. `docker ps | grep -E "grafana|prometheus|loki"`
2. `curl -s http://localhost:9090/-/healthy`
3. `curl -s http://localhost:3100/ready`
4. `curl -s http://localhost:9090/api/v1/targets | python3 -m json.tool` (or first 50 lines)
5. Any error messages or screenshots

---

**Status**: ✅ **READY TO USE**

Copy commands directly to your terminal. All paths are absolute and should work as-is.
