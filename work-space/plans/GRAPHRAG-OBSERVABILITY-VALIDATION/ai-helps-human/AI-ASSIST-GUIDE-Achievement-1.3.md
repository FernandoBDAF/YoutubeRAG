# AI-Assist Guide: Achievement 1.3 - Grafana Dashboards Configured

**Achievement**: 1.3 - Grafana Dashboards Configured  
**Status**: AI-Assisted Execution Guide  
**Created**: November 12, 2025  
**Purpose**: Step-by-step guide with copy-paste commands and expected outcomes

---

## 📋 Overview

This guide provides copy-paste ready commands and detailed steps for configuring Grafana dashboards. Execute each phase sequentially, copy output when requested, and share results for AI analysis.

---

## Phase 1: Dashboard Import & Inspection (25-35 min)

### Step 1.1: Check Dashboard Files

**Command to run:**

```bash
ls -lh ~/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG/observability/grafana/dashboards/
```

**Expected output:**

- Should list JSON files (e.g., graphrag-pipeline.json)
- Look for: `.json` files in the directory
- Note the file names and sizes

**Share with AI**: The complete output of this command

---

### Step 1.2: Verify Grafana is Running

**Command to run:**

```bash
docker ps | grep grafana
```

**Expected output:**

- Should show: `youtuberag-grafana` container with status `Up`
- Example: `e1f2c3d4e5f6  grafana/grafana:latest  ...  youtuberag-grafana  Up 2 hours`

**If NOT running:**

```bash
docker-compose -f ~/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG/docker-compose.observability.yml up -d grafana
```

**Share with AI**: Output showing Grafana running or error if not starting

---

### Step 1.3: Access Grafana and Check Dashboards

**In your browser, navigate to:**

```
http://localhost:3000
```

**Login:**

- Username: `admin`
- Password: `admin`

**Steps:**

1. Click "Home" (top left)
2. Look for "Dashboards" in the left menu
3. Click "Dashboards" → "Browse"
4. Note: Are there any dashboards already listed?

**What to look for:**

- Current dashboard count (e.g., "1 dashboard", "0 dashboards")
- Any dashboard names visible

**Share with AI**:

- Screenshot of the dashboards browse page
- List any dashboards already present

---

### Step 1.4: Import GraphRAG Pipeline Dashboard

**Steps:**

1. In Grafana, click the "+" icon (top left)
2. Select "Import dashboard"
3. Click "Upload JSON file" OR "Paste JSON"
4. If pasting JSON:
   - Open file: `~/Local Repo/YoutubeRAG-mongohack/YoutubeRAG/observability/grafana/dashboards/graphrag-pipeline.json` in text editor
   - Copy entire contents
   - Paste into Grafana import dialog
5. Click "Load"
6. Review the dashboard name and settings
7. Click "Import"

**Expected outcome:**

- Dashboard should import successfully
- You should be redirected to the new dashboard
- Dashboard title should appear at top

**Possible issues & fixes:**

- "Data source not found" error → That's OK, we'll configure data sources next
- Import fails → Share the error message with AI

**Share with AI**:

- Screenshot after successful import (or error message if it fails)
- Dashboard name shown in the browser tab/header

---

### Step 1.5: Check for Other Dashboards to Import

**List all JSON files:**

```bash
find ~/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG/observability/grafana/dashboards/ -name "*.json" -type f
```

**For each JSON file found** (besides graphrag-pipeline.json):

1. Repeat Step 1.4 for each file
2. Note which ones import successfully

**Share with AI**:

- List of all JSON files found
- Which ones imported successfully
- Any import errors encountered

---

## Phase 2: Data Source Configuration (25-35 min)

### Step 2.1: Access Data Sources Configuration

**Steps:**

1. In Grafana, click the gear icon (⚙️) in the left sidebar
2. Select "Data sources"
3. Note: What data sources are currently listed?

**Share with AI**:

- Screenshot of the Data sources page
- List of existing data sources (if any)

---

### Step 2.2: Test Prometheus Connectivity First

**Command to verify Prometheus is running:**

```bash
docker ps | grep prometheus
```

**Expected:** Should show `youtuberag-prometheus` running

**Test Prometheus endpoint:**

```bash
curl -s http://localhost:9090/-/healthy
```

**Expected output:**

```
Prometheus is Healthy.
```

**Share with AI**: The output of the curl command

---

### Step 2.3: Add Prometheus Data Source

**In Grafana:**

1. Click "Data sources" (if not already there)
2. Click "+ Add new data source"
3. Select "Prometheus"
4. Fill in:
   - **Name**: `Prometheus`
   - **URL**: `http://localhost:9090`
   - **Access**: Select "Browser" (or "Server" - try Browser first)
   - **Scrape interval**: Leave default
5. Click "Save & test" button

**Expected:**

- Green checkmark with message "Datasource is working"
- If red error appears, share it with AI

**Share with AI**:

- Screenshot showing the data source test result (green checkmark or error)

---

### Step 2.4: Test Loki Connectivity

**Command to verify Loki is running:**

```bash
docker ps | grep loki
```

**Expected:** Should show `youtuberag-loki` running

**Test Loki endpoint:**

```bash
curl -s http://localhost:3100/ready
```

**Expected output:**

```
ready
```

**Share with AI**: The output of the curl command

---

### Step 2.5: Add Loki Data Source

**In Grafana:**

1. Click "+ Add new data source" (if still on data sources page)
2. Select "Loki"
3. Fill in:
   - **Name**: `Loki`
   - **URL**: `http://localhost:3100`
   - **Access**: Select "Browser" (same as Prometheus)
4. Click "Save & test" button

**Expected:**

- Green checkmark with message "Data source is working"

**Share with AI**:

- Screenshot showing the Loki data source test result (green checkmark or error)

---

### Step 2.6: Verify Both Data Sources Listed

**Steps:**

1. From Data sources page, you should see both listed:
   - Prometheus
   - Loki
2. Click on each to verify they're saved correctly

**Share with AI**:

- Screenshot of both data sources listed

---

## Phase 3: Dashboard Functionality Verification (30-40 min)

### Step 3.1: Open the GraphRAG Pipeline Dashboard

**Steps:**

1. Click "Home" (or Grafana icon in top left)
2. Click "Dashboards" → "Browse"
3. Find "GraphRAG Pipeline" dashboard
4. Click to open it

**Expected:**

- Dashboard should load
- Various panels should be visible
- May show "No data" - this is OK and expected

**Share with AI**:

- Screenshot of the dashboard overview

---

### Step 3.2: Verify All Panels Load

**For each panel on the dashboard:**

1. Look for red error indicators or timeouts
2. Record panel names
3. Note if they show:
   - ✅ Data (numbers, graphs, tables)
   - ⚠️ "No data" message (expected before pipeline runs)
   - ❌ Error message (note what it says)

**Share with AI**:

- Count of panels: How many panels total?
- Count of panels with errors: How many show errors?
- Screenshots of any error messages

---

### Step 3.3: Test Dashboard Variables (if present)

**Steps:**

1. Look at the top of the dashboard for variable selectors (dropdowns with names)
2. If variables exist:
   - Click each dropdown
   - Select a different value
   - Observe if panels update
3. If no variables visible, that's fine - note "No variables"

**Share with AI**:

- Are variables present? (Yes/No)
- If yes, which variable names?
- Do panels update when you change variables? (Yes/No)
- Screenshot showing variables area

---

### Step 3.4: Test Time Range Selection

**Steps:**

1. Look at top right of dashboard for time range selector
2. Click on it (usually shows "Last 24h" or similar)
3. Try these:
   - Select "Last 1h"
   - Select "Last 7d"
   - Select "Custom" and pick dates
4. Observe if panels update/change

**Expected:**

- Time range selector should be responsive
- Panels should update (even if still showing "No data")

**Share with AI**:

- Does time range selector work? (Yes/No)
- Screenshot of time range selector
- Do panels update when you change time range? (Yes/No)

---

## Phase 4: Issue Debugging & Resolution (40-50 min)

**Only complete this phase if you found errors in Phase 3**

### Step 4.1: Check Panel Error Details

**If any panels show errors:**

1. Click on the panel
2. Click the "i" (info) icon or right-click → Edit
3. Look at the query/error message
4. Take screenshot of the error

**Share with AI**:

- Screenshots of each error panel
- Full error messages (copy-paste if possible)

---

### Step 4.2: Verify Docker Services Health

**Run this health check command:**

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "prometheus|loki|grafana"
```

**Expected output:**

- All three services should show "Up" status
- Should see port mappings

**Share with AI**: The output of this command

---

### Step 4.3: Check Prometheus Scrape Targets

**Command:**

```bash
curl -s http://localhost:9090/api/v1/targets | python3 -m json.tool | head -50
```

**Expected:**

- Should show targets in JSON format
- Look for "youtuberag" and "prometheus" targets
- Should show "state": "up"

**Share with AI**: Output showing target status

---

### Step 4.4: Restart Services if Needed

**If services not running or unresponsive:**

```bash
cd ~/Local\ Repo/YoutubeRAG-mongohack/YoutubeRAG && \
docker-compose -f docker-compose.observability.yml restart
```

**Wait 30 seconds, then:**

```bash
docker ps | grep -E "prometheus|loki|grafana"
```

**Share with AI**: Status of restarted services

---

## Phase 5: Documentation & Screenshots (25-35 min)

### Step 5.1: Collect Screenshots

**Capture and save these screenshots:**

1. **Dashboard Overview** - Full dashboard view

   - File: `dashboard-overview.png`

2. **Data Sources Configuration** - List of both Prometheus and Loki

   - File: `datasources-configured.png`

3. **Sample Panels** - 2-3 representative panels (with or without data)

   - Files: `panel-1.png`, `panel-2.png`

4. **Time Range Selector** - Top right showing time control

   - File: `time-range-selector.png`

5. **Variables (if present)** - Variable selectors area
   - File: `variables.png`

**Share with AI**: All screenshot files

---

### Step 5.2: Create Timeline of Execution

**Record this information for each phase:**

**Phase 1: Dashboard Import**

- Dashboards found: [List the JSON files]
- Dashboards imported: [List imported dashboards]
- Any errors: [Yes/No, describe if yes]
- Time taken: [e.g., "10 minutes"]

**Phase 2: Data Source Configuration**

- Prometheus connectivity: [Success/Fail]
- Loki connectivity: [Success/Fail]
- Data sources saved: [Prometheus: OK, Loki: OK]
- Time taken: [e.g., "8 minutes"]

**Phase 3: Dashboard Verification**

- Panels loaded: [e.g., "15 panels total"]
- Panels with errors: [e.g., "0 errors"]
- Variables present: [Yes/No]
- Variables working: [Yes/No/N/A]
- Time range working: [Yes/No]
- Time taken: [e.g., "12 minutes"]

**Phase 4: Debugging (if needed)**

- Issues found: [List any]
- Resolutions applied: [List actions]
- Remaining issues: [None/List if any]

**Phase 5: Documentation**

- Screenshots captured: [Count and list]
- Setup guide created: [Yes/No]
- Time taken: [e.g., "5 minutes"]

**Share with AI**: This timeline information

---

## Summary for AI Analysis

**After completing all phases, share with AI:**

1. ✅ All command outputs
2. ✅ All screenshots (5-8 images)
3. ✅ Timeline of execution (from Step 5.2)
4. ✅ Any error messages or unusual findings
5. ✅ Current status:
   - Are dashboards displaying? (Yes/No/Partially)
   - Are data sources connected? (Both/Prometheus only/Loki only/Neither)
   - Are panels functional? (Yes/No/Some with issues)

---

## Troubleshooting Quick Reference

| Problem                                    | Quick Fix                                                        |
| ------------------------------------------ | ---------------------------------------------------------------- |
| Grafana won't load (http://localhost:3000) | Check: `docker ps \| grep grafana` - may need restart            |
| Data source test fails                     | Verify service running: `docker ps \| grep prometheus` or `loki` |
| Dashboard won't import                     | Try importing with data sources first configured                 |
| Panels show "No data"                      | Normal! Means dashboard is working but no pipeline data yet      |
| Variables not showing                      | Dashboard may not have variables - check with AI                 |
| Time range not changing                    | Refresh browser (F5), or restart Grafana                         |
| Error: "datasource not found"              | Configure data source, then re-import dashboard                  |

---

## Next Steps

1. Execute Phase 1 (Dashboard Import) - 25-35 minutes
2. Execute Phase 2 (Data Sources) - 25-35 minutes
3. Execute Phase 3 (Verification) - 30-40 minutes
4. Execute Phase 4 (Debugging, if needed) - 40-50 minutes
5. Execute Phase 5 (Documentation) - 25-35 minutes
6. Share all results and screenshots with AI for analysis

**Total estimated time**: 2-3 hours

---

**Status**: ✅ **READY FOR EXECUTION**

Proceed with Phase 1. After each phase, share the requested outputs. AI will analyze results and guide next steps.
