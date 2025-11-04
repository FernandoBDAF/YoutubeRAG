# YoutubeRAG Observability Stack

**Components**: Prometheus + Grafana + Loki + Promtail  
**Purpose**: Complete observability for metrics and logs

---

## 🚀 Quick Start

### 1. Start Observability Stack

```bash
# From project root
docker-compose -f docker-compose.observability.yml up -d

# Verify all services running
docker-compose -f docker-compose.observability.yml ps
```

**Services**:

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- Loki: http://localhost:3100

---

### 2. Start Metrics Endpoint

```bash
# In separate terminal, start metrics server
python app/api/metrics.py

# Or in background thread within your app:
import threading
from app.api.metrics import start_metrics_server

thread = threading.Thread(target=start_metrics_server, daemon=True)
thread.start()
```

**Endpoint**: http://localhost:9091/metrics

---

### 3. Access Grafana

1. Open http://localhost:3000
2. Login: admin/admin
3. Datasources auto-configured (Prometheus + Loki)
4. Ready to create dashboards!

---

## 📊 Available Metrics

### Stage Metrics:

```
stage_started{stage="graph_extraction"}
stage_completed{stage="graph_extraction"}
stage_failed{stage="graph_extraction"}
stage_duration_seconds{stage="graph_extraction"}
documents_processed{stage="graph_extraction"}
documents_failed{stage="graph_extraction"}
```

### Agent Metrics:

```
agent_llm_calls{agent="GraphExtractionAgent",model="gpt-4o-mini"}
agent_llm_errors{agent="GraphExtractionAgent",model="gpt-4o-mini"}
agent_llm_duration_seconds{agent="GraphExtractionAgent",model="gpt-4o-mini"}
agent_tokens_used{agent="GraphExtractionAgent",model="gpt-4o-mini",token_type="prompt"}
agent_llm_cost_usd{agent="GraphExtractionAgent",model="gpt-4o-mini"}
```

### Global Metrics:

```
errors_total{error_type="ValueError",component="extraction"}
retries_attempted{function="call_model",error_type="APIError"}
```

---

## 📈 Example Grafana Queries

### Stage Performance:

```promql
# Average stage duration
rate(stage_duration_seconds_sum[5m]) / rate(stage_duration_seconds_count[5m])

# Documents processed per second
rate(documents_processed[1m])

# Stage failure rate
rate(stage_failed[5m])
```

### LLM Cost Tracking:

```promql
# Total cost per hour
rate(agent_llm_cost_usd[1h])

# Tokens per minute
rate(agent_tokens_used{token_type="total"}[1m])

# Cost by agent
sum by (agent) (agent_llm_cost_usd)
```

### Error Monitoring:

```promql
# Error rate
rate(errors_total[5m])

# Errors by type
sum by (error_type) (errors_total)

# Top error components
topk(5, sum by (component) (errors_total))
```

---

## 🔍 Logs in Loki

### Example Queries:

```logql
# All logs from graph_extraction
{component="stages"} |= "graph_extraction"

# Errors only
{level="ERROR"}

# Specific stage errors
{component="stages", stage="entity_resolution", level="ERROR"}

# Retry attempts
{} |= "[RETRY]"

# Operation lifecycle
{} |= "[OPERATION]"
```

---

## 🛠️ Troubleshooting

### Metrics Not Showing:

1. **Check metrics endpoint**: `curl http://localhost:9091/metrics`
2. **Check Prometheus targets**: http://localhost:9090/targets
3. **Verify service running**: `docker-compose -f docker-compose.observability.yml ps`

### Logs Not Showing:

1. **Check Loki**: `curl http://localhost:3100/ready`
2. **Check Promtail**: `docker logs youtuberag-promtail`
3. **Verify logs exist**: `ls -la logs/`

### Grafana Connection Issues:

1. **Check datasources**: Grafana → Configuration → Data Sources
2. **Test connection**: Click "Test" on each datasource
3. **Check network**: `docker network ls`

---

## 🎯 Dashboard Ideas

### Pipeline Execution Dashboard:

- Stage duration chart (line graph)
- Documents processed (counter)
- Success vs failure rates (pie chart)
- Active stages (gauge)

### LLM Cost Dashboard:

- Cost per hour (line graph)
- Cost by agent (bar chart)
- Tokens used (counter)
- Cost projection

### Error Monitoring Dashboard:

- Error rate (line graph)
- Error distribution by type (pie chart)
- Top failing components (table)
- Recent errors (log panel)

---

## 📋 Maintenance

### Stop Stack:

```bash
docker-compose -f docker-compose.observability.yml down
```

### Stop and Remove Data:

```bash
docker-compose -f docker-compose.observability.yml down -v
```

### View Logs:

```bash
docker-compose -f docker-compose.observability.yml logs -f
```

### Restart Service:

```bash
docker-compose -f docker-compose.observability.yml restart prometheus
```

---

## 🎊 Stack Ready!

**Start observability**: `docker-compose -f docker-compose.observability.yml up -d`  
**Start metrics endpoint**: `python app/api/metrics.py`  
**Access Grafana**: http://localhost:3000  
**Build dashboards**: Use metrics + logs!

**Complete observability achieved!** 🚀
