# Dashboard Setup Guide - Achievement 1.3

**Achievement**: 1.3 - Grafana Dashboards Configured  
**Date**: 2025-11-12  
**Status**: ✅ Complete

---

## 📋 Overview

This guide provides step-by-step instructions for setting up and configuring the GraphRAG Pipeline Dashboard in Grafana. The dashboard monitors real-time pipeline execution, stage progress, throughput, and errors.

---

## 🎯 Prerequisites

Before setting up the dashboard, ensure:

1. **Observability Stack Running** (Achievement 1.1 complete):

   - ✅ Grafana running on http://localhost:3000
   - ✅ Prometheus running on http://localhost:9090
   - ✅ Loki running on http://localhost:3100

2. **Data Sources Configured** (Achievement 1.2 complete):

   - ✅ Prometheus data source configured
   - ✅ Loki data source configured

3. **Dashboard JSON File**:
   - ✅ `observability/grafana/dashboards/graphrag-pipeline.json` exists

---

## 📦 Dashboard Structure

The GraphRAG Pipeline Dashboard contains **12 panels** organized in a grid layout:

### Panel Overview

1. **Pipeline Status** (Stat) - Current pipeline state (Idle/Running/Completed/Failed)
2. **Pipeline Runs** (Stat) - Total runs in last hour
3. **Pipeline Duration** (Stat) - Average pipeline duration
4. **Stage Progress** (Bar Gauge) - Progress percentage by stage
5. **Chunks Processed by Stage** (Time Series) - Processing rate and failures
6. **Throughput - Entities/sec** (Time Series) - Entity processing rate
7. **Throughput - Relationships/sec** (Time Series) - Relationship processing rate
8. **Throughput - Communities/sec** (Time Series) - Community processing rate
9. **Stage Duration** (Time Series) - Average and max duration by stage
10. **Error Rate by Stage** (Time Series) - Error rates by stage and type
11. **Chunk Processing Time** (Histogram) - Processing time distribution
12. **Stage Failures** (Stat) - Total failures in last hour

---

## 🚀 Setup Instructions

### Step 1: Verify Dashboard File

The dashboard JSON file should be located at:

```
observability/grafana/dashboards/graphrag-pipeline.json
```

**Important**: The JSON structure must have dashboard properties at the **root level**, not nested under a `"dashboard"` key.

**Correct Structure**:

```json
{
  "title": "GraphRAG Pipeline Dashboard",
  "panels": [...],
  ...
}
```

**Incorrect Structure** (will cause provisioning failure):

```json
{
  "dashboard": {
    "title": "GraphRAG Pipeline Dashboard",
    "panels": [...],
    ...
  }
}
```

### Step 2: Verify Provisioning Configuration

Check that dashboard provisioning is configured in:

```
observability/grafana/dashboards/dashboard-provisioning.yml
```

**Expected Configuration**:

```yaml
apiVersion: 1

providers:
  - name: "YoutubeRAG Dashboards"
    orgId: 1
    folder: ""
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
      foldersFromFilesStructure: true
```

### Step 3: Verify Data Sources

The dashboard requires **Prometheus** as the data source. Verify it's configured:

1. Open Grafana: http://localhost:3000
2. Go to **Connections → Data sources**
3. Verify **Prometheus** exists with:
   - URL: `http://prometheus:9090`
   - Status: ✅ Working (green checkmark)

**Note**: Data sources are auto-provisioned via `observability/grafana/datasources/datasources.yml`

### Step 4: Restart Grafana (if needed)

If the dashboard doesn't appear automatically:

```bash
cd /path/to/YoutubeRAG
docker-compose -f docker-compose.observability.yml restart grafana
```

Wait 30 seconds for Grafana to restart and reload provisioning.

### Step 5: Verify Dashboard Import

1. Open Grafana: http://localhost:3000
2. Go to **Dashboards**
3. Look for **"GraphRAG Pipeline Dashboard"** in the list
4. Click to open

**Expected Result**: Dashboard opens with all 12 panels visible (may show "No data" if pipeline hasn't run yet)

---

## 🔧 Data Source Configuration Details

### Prometheus Data Source

**Configuration**:

- **Name**: Prometheus
- **Type**: Prometheus
- **URL**: `http://prometheus:9090`
- **Access**: Server (proxy)
- **Default**: Yes

**Auto-Provisioned Via**:

```
observability/grafana/datasources/datasources.yml
```

**Manual Configuration** (if needed):

1. Go to **Connections → Data sources**
2. Click **"+ Add new data source"**
3. Select **Prometheus**
4. Set URL: `http://prometheus:9090`
5. Click **"Save & Test"**
6. Verify green checkmark ✅

### Loki Data Source

**Configuration**:

- **Name**: Loki
- **Type**: Loki
- **URL**: `http://loki:3100`
- **Access**: Server (proxy)

**Note**: Currently not used by the GraphRAG Pipeline Dashboard, but configured for future log visualization.

---

## 📊 Dashboard Variables

**Status**: This dashboard has **no variables** configured.

All panels use static PromQL queries. If you need to add variables (e.g., for stage filtering), you can add them in the dashboard JSON under the `"templating"` section.

---

## 🎨 Expected Initial State

### Before Pipeline Execution

When you first open the dashboard **before running any pipeline**:

- ✅ All 12 panels should be visible
- ✅ Panels show **"No data"** (this is **expected and correct**)
- ✅ No error indicators (red X marks)
- ✅ Dashboard layout matches the grid structure
- ✅ Time range selector shows "Last 1 hour"

**This is normal!** The dashboard is correctly configured and waiting for metrics from pipeline execution.

### After Pipeline Execution

Once you run a GraphRAG pipeline:

- ✅ Panels will populate with actual metrics
- ✅ Pipeline Status will show current state
- ✅ Throughput panels will show processing rates
- ✅ Error panels will show any failures
- ✅ Time series panels will display graphs

---

## 🔍 Troubleshooting

### Issue 1: Dashboard Not Appearing

**Symptoms**: Dashboard not in dashboard list

**Solutions**:

1. Check Grafana logs:
   ```bash
   docker logs youtuberag-grafana | grep -i dashboard
   ```
2. Verify JSON structure (must be at root level, not nested)
3. Check provisioning config path is correct
4. Restart Grafana:
   ```bash
   docker-compose -f docker-compose.observability.yml restart grafana
   ```

### Issue 2: "Dashboard title cannot be empty" Error

**Symptoms**: Error in Grafana logs, dashboard not loading

**Root Cause**: JSON has nested `"dashboard"` wrapper

**Solution**: Flatten JSON structure - move all properties to root level

**Before (Wrong)**:

```json
{
  "dashboard": {
    "title": "GraphRAG Pipeline Dashboard",
    ...
  }
}
```

**After (Correct)**:

```json
{
  "title": "GraphRAG Pipeline Dashboard",
  ...
}
```

### Issue 3: Panels Show "No data" After Pipeline Run

**Symptoms**: Panels still empty after running pipeline

**Solutions**:

1. Verify metrics server is running:
   ```bash
   curl http://localhost:9091/metrics
   ```
2. Check Prometheus is scraping metrics:
   - Go to http://localhost:9090/targets
   - Verify `youtuberag` target is **UP**
3. Verify time range in dashboard matches pipeline execution time
4. Check Prometheus has metrics:
   ```bash
   curl 'http://localhost:9090/api/v1/query?query=graphrag_pipeline_status'
   ```

### Issue 4: Panels Show "Error" Indicators

**Symptoms**: Red X marks or error messages in panels

**Solutions**:

1. Check data source connectivity:
   - Go to **Connections → Data sources**
   - Click **Prometheus**
   - Click **"Save & Test"**
   - Verify green checkmark ✅
2. Verify Prometheus is accessible:
   ```bash
   curl http://localhost:9090/-/healthy
   ```
3. Check panel queries are valid PromQL:
   - Click panel → Edit
   - Verify query syntax
   - Test query in Prometheus UI

### Issue 5: Duplicate Dashboards

**Symptoms**: Multiple dashboards with similar names

**Solution**: Delete the old/broken dashboard:

1. Go to **Dashboards**
2. Find duplicate (usually the one without tags)
3. Right-click → **Delete**
4. Keep only **"GraphRAG Pipeline Dashboard"** (with tags: graphrag, pipeline, monitoring)

### Issue 6: Data Source Not Found

**Symptoms**: Panels show "Data source not found"

**Solutions**:

1. Verify Prometheus datasource exists:
   - Go to **Connections → Data sources**
   - Check **Prometheus** is listed
2. Check dashboard JSON has datasource references:
   ```json
   "datasource": {"type": "prometheus", "name": "Prometheus"}
   ```
3. Re-import dashboard if datasource was added after import

---

## 📸 Verification Checklist

After setup, verify:

- [ ] Dashboard appears in dashboard list
- [ ] Dashboard opens without errors
- [ ] All 12 panels are visible
- [ ] Panels show "No data" (expected before pipeline run)
- [ ] No red error indicators
- [ ] Time range selector works
- [ ] Refresh interval is 10s
- [ ] Data source is Prometheus (check panel edit mode)

---

## 🔄 Maintenance

### Updating Dashboard

To update the dashboard:

1. Edit `observability/grafana/dashboards/graphrag-pipeline.json`
2. Save changes
3. Grafana will auto-reload within 10 seconds (updateIntervalSeconds: 10)
4. Refresh browser to see changes

### Adding New Panels

1. Edit dashboard JSON
2. Add new panel object to `"panels"` array
3. Ensure `"datasource"` is set correctly
4. Set `"gridPos"` for layout
5. Save and wait for auto-reload

### Backup Dashboard

To backup dashboard configuration:

1. In Grafana, open dashboard
2. Click **"Export"** (top right)
3. Save JSON file
4. Store in version control or backup location

---

## 📚 Related Documentation

- **Debug Log**: `documentation/Grafana-Dashboards-Debug-Log-1.3.md`
- **Query Reference**: `documentation/Dashboard-Queries-1.3.md`
- **Metrics Endpoint**: `documentation/Metrics-Endpoint-Validation-Report-1.2.md`
- **Observability Stack**: `observability/01_DEPLOYMENT_GUIDE.md`

---

## ✅ Success Criteria

Dashboard setup is successful when:

- ✅ Dashboard auto-provisions on Grafana startup
- ✅ All 12 panels display correctly
- ✅ No errors in Grafana logs
- ✅ Data source connectivity verified
- ✅ Dashboard ready to display metrics after pipeline execution

---

**Last Updated**: 2025-11-12  
**Version**: 1.0
