# GraphRAG Pipeline Visualization User Guide

**Achievement 8.3: User Guide**

Complete guide for setting up and using the GraphRAG Pipeline Visualization system.

---

## Table of Contents

1. [Overview](#overview)
2. [Setup & Installation](#setup--installation)
3. [Dashboard Setup](#dashboard-setup)
4. [Using the Web UI](#using-the-web-ui)
5. [Pipeline Control](#pipeline-control)
6. [Graph Exploration](#graph-exploration)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Overview

The GraphRAG Pipeline Visualization system provides:

- **Real-time Pipeline Monitoring**: Track pipeline execution progress and status
- **Interactive Graph Exploration**: Browse entities, relationships, and communities
- **Quality Metrics Dashboards**: Monitor per-stage quality metrics
- **Performance Analytics**: Analyze pipeline performance and identify bottlenecks
- **Export Capabilities**: Export graphs in multiple formats for external tools

---

## Setup & Installation

### Prerequisites

- Python 3.8+
- MongoDB instance running
- GraphRAG pipeline data in MongoDB
- Web browser (Chrome, Firefox, Safari, or Edge)

### Installation Steps

1. **Ensure Dependencies are Installed**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**

   ```bash
   export MONGODB_URI="mongodb://localhost:27017"
   export DB_NAME="mongo_hack"
   export OPENAI_API_KEY="your-api-key"
   ```

3. **Start API Servers**

   The visualization system uses multiple API endpoints. You can start them individually or use a process manager:

   ```bash
   # Start pipeline control API (port 8000)
   python app/api/pipeline_control.py 8000

   # Start entity API (port 8001)
   python app/api/entities.py 8001

   # Start communities API (port 8002)
   python app/api/communities.py 8002

   # Start export API (port 8003)
   python app/api/export.py 8003
   ```

   Or use a process manager like `supervisord` or `pm2` to manage all services.

---

## Dashboard Setup

### Accessing the Dashboards

All dashboards are HTML files that can be opened directly in your browser or served via a web server.

**Option 1: Direct File Access**

Simply open the HTML files in your browser:
- `app/ui/pipeline_control.html`
- `app/ui/pipeline_monitor.html`
- `app/ui/entity_browser.html`
- `app/ui/graph_viewer.html`
- `app/ui/quality_metrics_dashboard.html`
- `app/ui/performance_dashboard.html`

**Option 2: Web Server (Recommended)**

Use a simple HTTP server:

```bash
# Python 3
cd app/ui
python -m http.server 8080

# Then access: http://localhost:8080/pipeline_control.html
```

### Grafana Dashboard Setup

1. **Start Observability Stack**

   ```bash
   docker-compose -f docker-compose.observability.yml up -d
   ```

2. **Import Dashboard**

   - Open Grafana: http://localhost:3000
   - Login (default: admin/admin)
   - Go to Dashboards → Import
   - Upload `observability/grafana/dashboards/graphrag-pipeline.json`

3. **Configure Prometheus Data Source**

   - Go to Configuration → Data Sources
   - Add Prometheus
   - URL: http://prometheus:9090
   - Save & Test

---

## Using the Web UI

### Pipeline Control Dashboard

**Location:** `app/ui/pipeline_control.html`

**Features:**
- Start new pipeline runs
- Monitor current pipeline status
- Cancel or resume pipelines
- View pipeline logs

**Usage:**
1. Enter database name
2. Optionally enter experiment ID
3. Select stages to run (or leave empty for all)
4. Configure JSON settings if needed
5. Click "Start Pipeline"
6. Monitor progress in real-time

### Pipeline Monitor

**Location:** `app/ui/pipeline_monitor.html`

**Features:**
- Real-time progress bars for each stage
- Status indicators
- Live log streaming
- Error notifications

**Usage:**
1. Open the page
2. The page automatically connects to the pipeline progress stream
3. Watch real-time updates as the pipeline executes

### Entity Browser

**Location:** `app/ui/entity_browser.html`

**Features:**
- Search entities by name
- Filter by type, confidence, source_count
- Paginated results
- Detailed entity view

**Usage:**
1. Enter database name
2. Use search box to find entities
3. Apply filters as needed
4. Click on an entity to view details
5. Click "View Relationships" to see connected entities

### Graph Viewer

**Location:** `app/ui/graph_viewer.html`

**Features:**
- Interactive force-directed graph visualization
- Ego network exploration (N-hop neighborhoods)
- Community visualization
- Predicate filtering
- Export capabilities

**Usage:**

**View Sample Graph:**
1. Enter database name
2. Set max nodes (default: 100)
3. Click "Load Graph"

**View Ego Network:**
1. Enter entity ID
2. Set max hops (1-5)
3. Set max nodes
4. Click "Load Graph"

**View Community:**
1. Enter community ID
2. Click "Load Graph"

**Filter by Predicate:**
1. Load a graph first
2. Select predicate from dropdown
3. Graph automatically filters

**Export Graph:**
1. Load a graph
2. Click "Export Graph"
3. Choose format (JSON, CSV, GraphML, GEXF)
4. File downloads automatically

### Community Explorer

**Location:** `app/ui/community_explorer.html`

**Features:**
- Browse communities by level
- Filter by size and coherence
- View community details
- Navigate to graph visualization

**Usage:**
1. Enter database name
2. Select community level (if multi-resolution)
3. Browse communities
4. Click on a community to view details
5. Click "View Graph" to visualize in graph viewer

### Quality Metrics Dashboard

**Location:** `app/ui/quality_metrics_dashboard.html`

**Features:**
- Per-stage quality metrics
- Completion and failure rates
- Quality trends over time

**Usage:**
1. Enter database name
2. Optionally filter by stage
3. View metrics for each stage
4. Enable auto-refresh for real-time updates

### Performance Dashboard

**Location:** `app/ui/performance_dashboard.html`

**Features:**
- Pipeline duration tracking
- Throughput metrics (chunks/sec)
- Performance trends over time

**Usage:**
1. Enter database name
2. Optionally filter by pipeline ID
3. View current performance metrics
4. Analyze trends in charts

---

## Pipeline Control

### Starting a Pipeline

**Via Web UI:**
1. Open Pipeline Control dashboard
2. Enter configuration
3. Click "Start Pipeline"

**Via API:**
```bash
curl -X POST "http://localhost:8000/api/pipeline/start?db_name=mongo_hack" \
  -H "Content-Type: application/json" \
  -d '{"config": {"extraction": {"read_db_name": "mongo_hack"}}}'
```

### Resuming from Failure

If a pipeline fails, you can resume from the last checkpoint:

1. Open Pipeline Control dashboard
2. Check "Resume from failure"
3. Click "Start Pipeline"

The system will automatically detect completed stages and skip them.

### Stage Selection

You can run specific stages:

- **All stages:** Leave "Stages" field empty
- **Specific stages:** Enter comma-separated list: `extraction,resolution`
- **Stage range:** Enter range: `1-3` (runs stages 1, 2, 3)

### Monitoring Progress

**Real-time Monitoring:**
- Use Pipeline Monitor dashboard for live updates
- Or use Pipeline Control dashboard status section

**API Monitoring:**
```bash
# Get current status
curl "http://localhost:8000/api/pipeline/status?pipeline_id=pipeline_123&db_name=mongo_hack"
```

---

## Graph Exploration

### Exploring Entities

1. **Search Entities:**
   - Use Entity Browser
   - Enter search query
   - Apply filters (type, confidence, etc.)

2. **View Entity Details:**
   - Click on entity in browser
   - View aliases, relationships, source chunks

3. **Explore Ego Network:**
   - Copy entity ID
   - Open Graph Viewer
   - Enter entity ID
   - Set max hops (1-5)
   - Load graph

### Exploring Relationships

1. **Browse Relationships:**
   - Use Relationship Viewer
   - Filter by predicate, type, confidence
   - View subject → predicate → object triples

2. **Filter Graph by Predicate:**
   - Load graph in Graph Viewer
   - Select predicate from dropdown
   - Graph filters automatically

### Exploring Communities

1. **Browse Communities:**
   - Use Community Explorer
   - Navigate by level (if multi-resolution)
   - Filter by size and coherence

2. **Visualize Community:**
   - Click "View Graph" on a community
   - Graph Viewer opens with community subgraph
   - Explore entities and relationships within community

3. **Multi-Resolution Navigation:**
   - Use level navigation buttons
   - Drill down from macro (level 1) to micro (level 3+)
   - View level statistics

---

## Troubleshooting

### Pipeline Not Starting

**Symptoms:** Pipeline status remains "starting" or shows error

**Solutions:**
1. Check MongoDB connection
2. Verify database name is correct
3. Check API server logs
4. Ensure OpenAI API key is set
5. Verify stage dependencies are met

### Graph Not Loading

**Symptoms:** Graph viewer shows "No graph data" or empty graph

**Solutions:**
1. Verify database name is correct
2. Check that entities/relationships exist in database
3. Try reducing max_nodes
4. Check browser console for errors
5. Verify API endpoints are accessible

### API Endpoints Not Responding

**Symptoms:** 404 errors or connection refused

**Solutions:**
1. Verify API servers are running
2. Check port numbers match
3. Verify CORS headers are set (should be automatic)
4. Check firewall settings
5. Try accessing API directly: `curl http://localhost:8000/api/pipeline/status`

### Performance Issues

**Symptoms:** Slow loading, timeouts

**Solutions:**
1. Reduce max_nodes in graph viewer
2. Use filters to limit data
3. Check MongoDB indexes are created
4. Consider pagination for large datasets
5. Monitor MongoDB performance

### Export Not Working

**Symptoms:** Export button does nothing or file is empty

**Solutions:**
1. Ensure graph is loaded first
2. Check browser allows downloads
3. Try different export format
4. Check browser console for errors
5. Verify graph data is not empty

---

## Best Practices

### Pipeline Execution

1. **Use Experiment IDs:**
   - Always set experiment_id for tracking
   - Use descriptive names: `extraction_v2_resolution_1.0`

2. **Stage Selection:**
   - Run only needed stages to save time
   - Use resume feature for failed pipelines

3. **Monitor Progress:**
   - Keep Pipeline Monitor open during execution
   - Check logs for warnings

### Graph Exploration

1. **Start Small:**
   - Begin with sample graphs (top 50-100 entities)
   - Gradually increase size as needed

2. **Use Filters:**
   - Filter by predicate to focus on specific relationships
   - Use entity type filters to narrow scope

3. **Ego Networks:**
   - Start with 1-hop, then expand to 2-3 hops
   - Use max_nodes to limit size

4. **Community Exploration:**
   - Start at level 1 (macro topics)
   - Drill down to specific communities
   - Use coherence scores to find high-quality communities

### Performance Optimization

1. **Database Indexing:**
   - Ensure indexes are created on entity_id, relationship_id
   - Index community_id for fast lookups

2. **Caching:**
   - API responses can be cached for frequently accessed data
   - Consider caching community details

3. **Pagination:**
   - Always use pagination for large result sets
   - Default limit of 50 is usually sufficient

### Export & Integration

1. **Export Formats:**
   - Use JSON for programmatic access
   - Use GraphML/GEXF for visualization tools (Gephi, yEd)
   - Use CSV for spreadsheet analysis

2. **Subgraph Export:**
   - Export communities for focused analysis
   - Export ego networks for entity-centric studies

3. **External Tools:**
   - Gephi: Import GraphML or GEXF
   - Neo4j: Convert JSON to Cypher import format
   - NetworkX: Load JSON directly

---

## Advanced Features

### Multi-Resolution Communities

If your pipeline uses multi-resolution community detection:

1. **Navigate Levels:**
   - Level 1: Macro themes (broad topics)
   - Level 2-3: Mid-level topics
   - Level 4+: Micro topics (specific subjects)

2. **Compare Levels:**
   - View statistics for each level
   - Compare community sizes across levels
   - Identify best level for your use case

### Experiment Comparison

1. **Run Multiple Experiments:**
   - Use different experiment_ids
   - Vary parameters (resolution, algorithms)

2. **Compare Results:**
   - Use Experiment Comparison UI
   - Compare quality metrics
   - Analyze cost and performance

3. **Track Changes:**
   - Use Pipeline History to review past runs
   - Export comparison reports

---

## Support & Resources

### Documentation

- API Documentation: `documentation/api/GRAPHRAG-PIPELINE-API.md`
- Plan Document: `PLAN_GRAPHRAG-PIPELINE-VISUALIZATION.md`

### Logs

- API logs: Check console output of API servers
- Pipeline logs: View in Pipeline Monitor or Pipeline Control dashboard
- MongoDB logs: Check MongoDB server logs

### Common Issues

See [Troubleshooting](#troubleshooting) section above for common issues and solutions.

---

## Version

**Guide Version:** 1.0  
**Last Updated:** 2025-11-07

